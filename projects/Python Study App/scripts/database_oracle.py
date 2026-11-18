"""Evaluate published read-only oracle queries against authoring fixtures on the local test MySQL only."""

import re
from uuid import uuid4
import xml.etree.ElementTree as ET

from code_practice.database_judge import MYSQL, client, literal, root


def quoted(name):
    return "`" + name.replace("`", "``") + "`"


def query_tables(schema, inputs, queries):
    # Assign each question a private database and a SELECT-only account. Only our fixture
    # writer runs as the administrator. Published SELECTs run as the disposable reader.
    name = "study_oracle_" + uuid4().hex[:16]
    password = uuid4().hex
    dbs = [name + "_" + str(i) for i in range(len(inputs))]
    try:
        ddl = [f"CREATE USER '{name}'@'localhost' IDENTIFIED BY '{password}';"]
        for db, tables in zip(dbs, inputs):
            ddl.extend(
                (
                    f"CREATE DATABASE {quoted(db)};",
                    f"GRANT SELECT ON {quoted(db)}.* TO '{name}'@'localhost';",
                    f"USE {quoted(db)};",
                )
            )
            for table, columns in schema.items():
                ddl.append(
                    f"CREATE TABLE {quoted(table)} ("
                    + ",".join(quoted(k) + " " + t for k, t in columns)
                    + ");"
                )
                if tables[table]:
                    values = ",".join(
                        "(" + ",".join(literal(v) for v in row) + ")" for row in tables[table]
                    )
                    ddl.append(f"INSERT INTO {quoted(table)} VALUES {values};")
        root("\n".join(ddl))
        results = []
        for query in queries:
            commands = ["SET SESSION sql_mode=''; SET SESSION max_execution_time=1500;"]
            for db in dbs:
                commands.extend((f"USE {quoted(db)};", query.strip().rstrip(";") + ";"))
            code, result, error = client(
                ["env", f"MYSQL_PWD={password}", *MYSQL, "--xml", "--user=" + name],
                "\n".join(commands),
                timeout=40,
            )
            if code:
                raise ValueError(error)
            sets = ET.fromstring("<sets>" + re.sub(r"<\?xml[^>]+\?>", "", result) + "</sets>").findall(
                "resultset"
            )
            if len(sets) != len(inputs):
                raise ValueError("Wrong number of result tables")
            series = []
            for each in sets:
                rows = each.findall("row")

                def cell(node):
                    return (
                        None
                        if node.get("{http://www.w3.org/2001/XMLSchema-instance}nil")
                        else node.text or ""
                    )

                series.append(
                    (
                        [field.get("name") for field in rows[0]] if rows else [],
                        [[cell(field) for field in row] for row in rows],
                    )
                )
            results.append(series)
        code, meta, error = client(
            [
                "env",
                f"MYSQL_PWD={password}",
                *MYSQL,
                "--user=" + name,
                "--database=" + dbs[0],
                "--column-type-info",
                "-vvv",
            ],
            "SET SESSION sql_mode='';\n" + queries[0].rstrip(";") + ";",
            timeout=10,
        )
        if code:
            raise ValueError(error)
        fields = re.findall(r"^Field\s+\d+:  `([^`\n]+)`(.*?)^Type:\s+(\w+)", meta, re.S | re.M)
        if not fields:
            raise ValueError("Could not read oracle output field types")
        return results, [(name, kind) for name, _, kind in fields]
    finally:
        root(
            "\n".join(f"DROP DATABASE IF EXISTS {quoted(db)};" for db in dbs)
            + f"\nDROP USER IF EXISTS '{name}'@'localhost';"
        )
