"""MySQL client for the isolated, disposable local practice instance."""
from __future__ import annotations

from collections import Counter
from decimal import Decimal, InvalidOperation
from itertools import groupby
import os
import re
import subprocess
from tempfile import TemporaryFile
from threading import BoundedSemaphore
from uuid import uuid4
import xml.etree.ElementTree as ET

LIMIT = 1_000_000
SLOTS = BoundedSemaphore(2)
MYSQL = ["mysql", "--no-defaults", "--binary-mode", "--local-infile=0", "--default-character-set=utf8mb4",
         "--connect-timeout=3"]


class Unavailable(Exception):
    pass


def client(args, sql, timeout=5):
    container = os.environ.get("CODE_PRACTICE_MYSQL_CONTAINER")
    if not container or not re.fullmatch(r"nsy-study-mysql-[a-zA-Z0-9-]+", container):
        raise Unavailable("Start the isolated MySQL practice container to use MySQL.")
    try:
        with TemporaryFile() as stdout:
            result = subprocess.run(["docker", "exec", "-i", container, *args], input=sql.encode(),
                                    stdout=stdout, stderr=subprocess.PIPE, timeout=timeout)
            stdout.seek(0)
            data = stdout.read(LIMIT + 1)
    except OSError as error:
        raise Unavailable("The local MySQL practice container is unavailable.") from error
    message = result.stderr.decode(errors="replace").strip()
    if result.returncode in (125, 126, 127) or any(marker in message.lower() for marker in (
        "error response from daemon", "cannot connect to the docker daemon",
        "permission denied while trying to connect", "error 2002 (hy000)",
    )):
        raise Unavailable("The local MySQL practice container is unavailable.")
    if len(data) > LIMIT:
        return 1, "", "The query returned too much data."
    return result.returncode, data.decode(errors="replace"), message[:1000]


def root(sql):
    try:
        code, data, _ = client(
            ["sh", "-c", 'export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec "$@"',
             "mysql-admin", *MYSQL, "--user=root", "--batch", "--skip-column-names"], sql, timeout=15)
    except subprocess.TimeoutExpired as error:
        raise Unavailable("The MySQL practice instance timed out preparing the test.") from error
    if code != 0:
        raise Unavailable("The MySQL practice instance could not prepare the test.")
    return data


def literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    # String values are fixtures, encoded without statement delimiters.
    return "CONVERT(0x" + value.encode().hex() + " USING utf8mb4)" if value else "''"


def setup(problem, case, name, password):
    schema = case.get("schema", problem["schema"])
    rights = {"query": "SELECT", "mutation": "SELECT, DELETE, UPDATE",
              "function": "SELECT, CREATE ROUTINE, ALTER ROUTINE, EXECUTE",
              "procedure": "SELECT, CREATE ROUTINE, ALTER ROUTINE, EXECUTE"}[problem["runner"]]
    root(f"CREATE DATABASE `{name}`;\nCREATE USER '{name}'@'localhost' IDENTIFIED BY '{password}';\n"
         f"GRANT {rights} ON `{name}`.* TO '{name}'@'localhost';\n"
         f"USE `{name}`;\n" + "\n".join(
            f"CREATE TABLE `{table}` (" + ",".join(f"`{col}` {type_}" for col, type_ in columns) + ");\n"
            + (f"INSERT INTO `{table}` VALUES " + ",".join(
                "(" + ",".join(literal(x) for x in row) + ")" for row in case["tables"][table]) + ";"
               if case["tables"][table] else "")
            for table, columns in schema.items()
         ))


def read_table(data, expected):
    data = re.sub(r"<\?xml[^>]+\?>", "", data)
    # Empty results require the column-type output from a fresh fixture.
    results = ET.fromstring("<results>" + data + "</results>").findall("resultset")
    if len(results) != 1:
        return {"columns": [], "rows": []}, False
    rows = results[0].findall("row")
    if not rows:
        return {"columns": [], "rows": []}, not expected["rows"]
    names = [node.get("name") for node in rows[0]]
    values = [[None if node.get("{http://www.w3.org/2001/XMLSchema-instance}nil") else node.text or ""
               for node in row] for row in rows]
    return {"columns": names, "rows": values}, matches(expected, names, values, numeric_strings=True)


def matches(expected, columns, rows, *, ordered=False, numeric_strings=False, date_columns=()):
    if columns != expected["columns"] or len(rows) != len(expected["rows"]):
        return False
    numeric = [any(isinstance(row[i], (int, float)) for row in expected["rows"]) for i in range(len(columns))]

    def normalized(row, strings):
        values = []
        for name, cell, as_number in zip(columns, row, numeric):
            if name in date_columns and isinstance(cell, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}[ T]00:00:00(?:\.0+)?", cell):
                cell = cell[:10]
            if as_number and (type(cell) in (float, int) or (strings and isinstance(cell, str))):
                try:
                    cell = Decimal(str(cell)).quantize(Decimal("0.00000001"))
                except InvalidOperation:
                    pass
            values.append(cell)
        return tuple(values)

    if any(len(row) != len(columns) or any(isinstance(value, (dict, list)) for value in row) for row in rows):
        return False
    actual = [normalized(row, numeric_strings) for row in rows]
    target = [normalized(row, False) for row in expected["rows"]]
    if isinstance(ordered, (list, tuple)):
        positions = [columns.index(key) for key in ordered]
        def groups(data):
            return [(key, Counter(group)) for key, group in groupby(
                data, lambda row: tuple(row[position] for position in positions))]
        return groups(actual) == groups(target)
    return actual == target if ordered else Counter(actual) == Counter(target)


def result_statement(problem, case):
    runner = problem["runner"]
    if runner == "query":
        return ""
    if runner == "mutation":
        return f"SELECT * FROM `{problem['result_table']}`;"
    # Use the declared order even after a JSON client reorders parameter keys.
    names = problem["cases"][0]["parameters"]
    arguments = ", ".join(literal(case["parameters"][key]) for key in names)
    call = f"`{problem['routine']}`({arguments})"
    if runner == "procedure":
        return f"CALL {call};"
    alias = problem["scalar_column"].format(**case["parameters"]).replace("`", "``")
    return f"SELECT {call} AS `{alias}`;"


def run_mysql(problem, case, source, *, metadata=False):
    name = "study_" + uuid4().hex[:23]
    password = uuid4().hex
    with SLOTS:
        # A client that returned normally has already closed its only connection.
        # An interrupted client may still have a query running inside the container.
        client_finished = False
        try:
            setup(problem, case, name, password)
            # In batch binary mode only SQL plus the client's charset/delimiter
            # directives are available. The restricted login only sees this fixture.
            code, data, error = client(
                ["env", f"MYSQL_PWD={password}", *MYSQL,
                 *(["--column-type-info", "-vvv"] if metadata else ["--xml"]),
                 f"--user={name}", "--database=" + name],
                "SET SESSION sql_mode='';\nSET SESSION max_execution_time=1500;\n"
                + source.rstrip().rstrip(";") + ";\n" + result_statement(problem, case) + "\n")
            client_finished = True
            if code:
                return {"passed": False, "error": error.replace(name, "practice") or "MySQL rejected the statement."}
            if metadata:
                names = re.findall(r"^Field\s+\d+:  `([^\n`]*)`$", data, re.M)
                actual = {"columns": names, "rows": []}
                return {"passed": matches(case["expected"], names, []), "actual": actual}
            actual, valid = read_table(data, case["expected"])
            if valid and not actual["rows"]:
                return {"passed": False, "verify_empty": True}
            if valid and problem["ordered"]:
                valid = matches(case["expected"], actual["columns"], actual["rows"], ordered=problem["ordered"], numeric_strings=True)
            return {"passed": valid, "actual": actual}
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "The query exceeded the time limit."}
        except ET.ParseError:
            return {"passed": False, "error": "Return one result table."}
        finally:
            try:
                if not client_finished:
                    connections = root(f"SELECT ID FROM information_schema.PROCESSLIST WHERE USER='{name}';")
                    for thread in connections.splitlines():
                        if thread.isdigit():
                            root(f"KILL CONNECTION {thread};")
                root(f"DROP DATABASE IF EXISTS `{name}`; DROP USER IF EXISTS '{name}'@'localhost';")
            except (Unavailable, subprocess.TimeoutExpired):
                pass


def evaluate_mysql(problem, case, source):
    outcome = run_mysql(problem, case, source)
    if outcome.get("verify_empty"):
        return run_mysql(problem, case, source, metadata=True)
    return outcome
