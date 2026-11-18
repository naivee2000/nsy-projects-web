"""Package question contracts after checking published examples and an independent SQL oracle."""

import argparse
from calendar import month_abbr
from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from itertools import groupby
import json
import os
from pathlib import Path
from random import Random
import re
import sys

from code_practice.database_judge import matches
from scripts.database_oracle import query_tables
from scripts.database_source_examples import read_source
from scripts import database_batch_01, database_solutions_01
from scripts import database_batch_02, database_solutions_02
from scripts import database_batch_03, database_solutions_03
from scripts import database_batch_04, database_solutions_04
from scripts import database_batch_05, database_solutions_05
from scripts import database_batch_06, database_solutions_06
from scripts import database_batch_07, database_solutions_07
from scripts import database_batch_08, database_solutions_08
from scripts import database_batch_09, database_solutions_09
from scripts import database_solutions_recent
from scripts import database_batch_10, database_solutions_10

BATCHES = [
    (database_batch_01.inputs, database_solutions_01.SOLUTIONS),
    (database_batch_02.inputs, database_solutions_02.SOLUTIONS),
    (database_batch_03.inputs, database_solutions_03.SOLUTIONS),
    (database_batch_04.inputs, database_solutions_04.SOLUTIONS),
    (database_batch_05.inputs, database_solutions_05.SOLUTIONS),
    (database_batch_06.inputs, database_solutions_06.SOLUTIONS),
    (database_batch_07.inputs, database_solutions_07.SOLUTIONS),
    (database_batch_08.inputs, database_solutions_08.SOLUTIONS),
    (database_batch_09.inputs, database_solutions_09.SOLUTIONS),
    (database_batch_09.inputs, database_solutions_recent.SOLUTIONS),
    (database_batch_10.inputs, database_solutions_10.SOLUTIONS),
]
SETS = {k: (factory, s) for factory, defs in BATCHES for k, s in defs.items()}


def substitute(code, before, after):
    if before not in code or before == after:
        raise ValueError(f"Missing or ineffective mutation {before!r}")
    return code.replace(before, after)


def numeric_value(value, kind):
    if value is None or str(value).strip().lower() == "null":
        return None
    if kind in ("TINY", "SHORT", "LONG", "LONGLONG", "INT24", "YEAR"):
        return int(Decimal(value))
    if kind in ("NEWDECIMAL", "DECIMAL", "FLOAT", "DOUBLE"):
        return float(value)
    if kind == "DATE":
        return datetime.strptime(str(value), "%Y-%m-%d").date().isoformat()
    return str(value)


def table_case(sql, schema):
    # Preserve literals and projection aliases, which may deliberately share a
    # spelling with a table (e.g. 'failed' and NPV.npv).
    for name in schema:
        sql = re.sub(
            r"(\b(?:FROM|JOIN)\s+)" + re.escape(name) + r"\b", lambda m: m[1] + name, sql, flags=re.I
        )
        sql = re.sub(r"\b" + re.escape(name) + r"(?=\.)", name, sql, flags=re.I)
    return sql


def independent_sql(key, schema, oracle_dir):
    sql = (oracle_dir / f"{key}.sql").read_text().strip().rstrip(";")
    sql = table_case(sql, schema)
    if key == 569:
        sql = sql.replace("ORDER BY salary", "ORDER BY salary, id")
    if key == 615:
        sql = sql.replace("Salary.pay_date", "DATE_FORMAT(Salary.pay_date,'%Y-%m')")
    if key == 618:
        sql = sql.replace("AS Europe,\n  id", "AS Europe") + " ORDER BY id"
    if key == 1435:
        sql = sql.replace(" <= ", " < ").replace(" > ", " >= ")
    if key == 1445:
        sql = """SELECT a.sale_date,a.sold_num-o.sold_num AS diff FROM Sales a JOIN Sales o ON a.sale_date=o.sale_date
                WHERE a.fruit='apples' AND o.fruit='oranges' ORDER BY a.sale_date"""
    if key == 1459:
        sql = re.sub(r"\bp([12])\.", lambda m: "P" + m[1] + ".", sql, flags=re.I)
    if key == 1517:
        sql += " AND BINARY RIGHT(mail,13) = '@leetcode.com'"
    if key == 1892:
        sql = sql.replace("LEFT JOIN Likes AS FriendLikes", "JOIN Likes AS FriendLikes")
    if key in (2004, 2010):
        sql = sql.replace("accumulated_salary <", "accumulated_salary <=")
    if key == 2020:
        sql = """SELECT COUNT(*) AS accounts_count FROM
        (SELECT s.account_id FROM Subscriptions s LEFT JOIN Streams t USING(account_id)
          WHERE s.start_date<'2022-01-01' AND s.end_date>='2021-01-01' GROUP BY s.account_id
          HAVING COUNT(CASE WHEN t.stream_date BETWEEN '2021-01-01' AND '2021-12-31' THEN 1 END)=0) accounts"""
    if key == 2388:
        sql = """SELECT c.id,(SELECT d.drink FROM CoffeeShop d WHERE d.input_position<=c.input_position AND d.drink IS NOT NULL
                 ORDER BY d.input_position DESC LIMIT 1) drink FROM CoffeeShop c ORDER BY c.input_position"""
    if key == 2329:
        sql += ", user_id ASC"
    if key == 2668:
        sql = """SELECT s.* FROM Salary s WHERE NOT EXISTS(SELECT 1 FROM Salary n WHERE n.emp_id=s.emp_id
                 AND CAST(n.salary AS UNSIGNED)>CAST(s.salary AS UNSIGNED)) ORDER BY s.emp_id"""
    if key == 3188:
        # Independently enumerate missing mandatory courses and low grades, counting
        # distinct electives when a student retakes a course in a later semester.
        sql = """SELECT s.student_id FROM students s
          WHERE (SELECT AVG(e.GPA) FROM enrollments e WHERE e.student_id=s.student_id)>=2.5
          AND NOT EXISTS (SELECT 1 FROM courses c WHERE c.major=s.major AND LOWER(c.mandatory)='yes'
            AND NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.course_id=c.course_id AND e.student_id=s.student_id))
          AND NOT EXISTS (SELECT 1 FROM enrollments e JOIN courses c USING(course_id) WHERE e.student_id=s.student_id
            AND c.major=s.major AND (LOWER(c.mandatory)='yes' AND e.grade<>'A'
              OR LOWER(c.mandatory)='no' AND e.grade NOT IN ('A','B')))
          AND (SELECT COUNT(*) FROM courses c WHERE c.major=s.major AND LOWER(c.mandatory)='no'
            AND EXISTS (SELECT 1 FROM enrollments e WHERE e.course_id=c.course_id AND e.student_id=s.student_id))>=2
          ORDER BY s.student_id"""
    if key == 3252:
        sql = sql.replace("* 0.33", "/ 3.0").replace("* 0.67", "* 2 / 3.0")
    if key == 3293:
        sql += " ORDER BY Products.product_id"
    if key == 3328:
        sql = sql.replace("ORDER BY city SEPARATOR", "ORDER BY REPLACE(city,' ',''),city SEPARATOR")
    if key == 3415:
        sql = sql.replace("ORDER BY 1", "OR name REGEXP '^[0-9]{3}$' ORDER BY 1")
    if key == 3465:
        sql = """SELECT * FROM products WHERE REGEXP_SUBSTR(description,'SN[0-9]{4}-[0-9]{4}([^0-9]|$)',1,1,'c') IS NOT NULL ORDER BY product_id"""
    return sql


def question_inputs(key, schema, ex, make_inputs):
    inputs = [ex["tables"]]
    for index in range(1, 16):
        r = Random(key * 100 + index)
        tables = make_inputs(key, index, r, ex["tables"]) if key >= 1468 else make_inputs(key, index, r)
        if key != 2388:
            for data in tables.values():
                r.shuffle(data)
        inputs.append(tables)
    if key == 2388:
        schema["CoffeeShop"].append(("input_position", "INT"))
        for tables in inputs:
            tables["CoffeeShop"] = [[*row, pos] for pos, row in enumerate(tables["CoffeeShop"], 1)]
    signatures = [
        json.dumps({k: sorted(json.dumps(r) for r in v) for k, v in t.items()}, sort_keys=True)
        for t in inputs
    ]
    if len(set(signatures)) != 16:
        raise ValueError("Input contents repeat")
    return inputs


def build(key, source_dir, oracle_dir, destination):
    make_inputs, definition = SETS[key]
    source_file = source_dir / f"{key}.md"
    schema, examples = read_source(source_file)
    if not definition.sql:
        blocks = re.findall(r"^```sql\s*\n(.*?)^```", source_file.read_text(), re.M | re.S)
        sql = " ".join(
            line.strip() for line in blocks[0].splitlines() if not line.lstrip().startswith(("#", "--"))
        )
        sql = re.sub(r"\s+", " ", table_case(sql, schema)).strip().rstrip(";")
        if key == 1097:
            sql = re.sub(r"AS day1_retention", "AS Day1_retention", sql, flags=re.I)
        if key == 1479:
            sql = sql.replace("AS category", "AS Category")
        if key == 2994:
            sql = sql.replace(
                "SELECT '2023-11-01' AS purchase_date", "SELECT DATE('2023-11-01') AS purchase_date"
            )
        if key == 3060 and "ORDER BY user_id" not in sql:
            sql += " ORDER BY user_id"
        if key == 3308:
            sql = sql.replace("SUM(accidents) accidents", "MAX(accidents) accidents")
        if key == 3328:
            sql = sql.replace("ORDER BY city SEPARATOR", "ORDER BY REPLACE(city,' ',''),city SEPARATOR")
        if key == 3611:
            sql = (
                sql.replace("hours >= 20", "hours > 20")
                .replace(
                    "YEAR(meeting_date) AS year, WEEK(meeting_date, 1) AS week",
                    "YEARWEEK(meeting_date,3) AS week",
                )
                .replace("GROUP BY 1, 2, 3 ), intensive_weeks", "GROUP BY 1, 2 ), intensive_weeks")
            )
        definition = replace(definition, sql=sql)
    ex = examples[0]
    cols = ex["columns"]
    if key == 1484:
        # The published output lower-cases the S in T-Shirt; the input supplies the spelling.
        for row in ex["output"]:
            row[-1] = row[-1].replace("T-shirt", "T-Shirt")
    if key == 1179:
        cols = ["id", *(name + "_Revenue" for name in list(month_abbr)[1:])]
        lookup = {(dept, month): amount for dept, amount, month in ex["tables"]["Department"]}
        ex["output"] = [
            [d, *(lookup.get((d, m)) for m in list(month_abbr)[1:])]
            for d in sorted({d for d, _ in lookup})
        ]
    inputs = question_inputs(key, schema, ex, make_inputs)
    if key in (3368, 3374):
        (reference,), types = query_tables(schema, inputs, [definition.sql])

        def official_capitalization(word):
            if key == 3374 and not re.match("[a-zA-Z]", word):
                return word
            chars = list(word.lower())
            starts = [0]
            if key == 3374 and re.fullmatch(r"[a-zA-Z]+(?:-[a-zA-Z]+)+", word):
                starts += [i + 1 for i, c in enumerate(word) if c == "-"]
            for pos in starts:
                chars[pos] = chars[pos].upper()
            return "".join(chars)

        independent = [
            (
                cols,
                [
                    [n, t, re.sub(r"[^ ]+", lambda m: official_capitalization(m[0]), t)]
                    for n, t in data["user_content"]
                ],
            )
            for data in inputs
        ]
    elif (oracle_dir / f"{key}.sql").is_file():
        oracle = independent_sql(key, schema, oracle_dir)
        (reference, independent), types = query_tables(schema, inputs, [definition.sql, oracle])
    else:
        from hashlib import sha256

        cache = json.loads((oracle_dir / f"{key}-pandas.json").read_text())
        if cache["inputs"] != sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest():
            raise ValueError("Independent Pandas oracle must be rerun on this input generation")
        (reference,), types = query_tables(schema, inputs, [definition.sql])
        independent = cache["outputs"]
    if [name for name, _ in types] != cols:
        raise ValueError(("reference schema", types, cols))
    if len(reference) != len(independent) or len(reference) != len(inputs):
        raise ValueError("Incomplete reference or independent result set")
    cases = []
    for index, (actual, other) in enumerate(zip(reference, independent)):
        names, rows = other
        if names and [c.lower() for c in names] != [c.lower() for c in cols]:
            raise ValueError(("oracle schema", names, cols))
        target = {
            "columns": cols,
            "rows": [[numeric_value(v, t) for (_, t), v in zip(types, row)] for row in rows],
        }
        if not matches(
            target, actual[0] or cols, actual[1], ordered=definition.ordered, numeric_strings=True
        ):
            raise ValueError(("disagreement", index, target, actual))
        if index == 0:
            original = [[numeric_value(v, t) for (_, t), v in zip(types, row)] for row in ex["output"]]
            if not matches(target, cols, original, ordered=definition.ordered):
                raise ValueError(("published example", target, original))
            target["rows"] = original
        elif definition.ordered is not True:
            # MySQL can return equivalent rows in a different order on a clean
            # rebuild. Give those rows a stable display order without requiring
            # students to reproduce it.
            order_keys = [cols.index(name) for name in (definition.ordered or [])]
            groups = groupby(target["rows"], lambda row: tuple(row[pos] for pos in order_keys))
            target["rows"] = [
                row
                for _, group in groups
                for row in sorted(group, key=lambda r: tuple((cell is not None, cell) for cell in r))
            ]
        cases.append({"tables": inputs[index], "parameters": {}, "expected": target})
    wrong_sql, wrong_pd = [], []
    for a, b, c, d in definition.mistakes:
        wrong_sql.append(substitute(definition.sql, a, b))
        wrong_pd.append(substitute(definition.pandas, c, d))
    result = {
        "id": key,
        "topic": definition.topic,
        "sql": definition.sql,
        "pandas": definition.pandas,
        "schema": schema,
        "cases": cases,
        "wrong": wrong_sql,
        "wrong_pandas": wrong_pd,
        "ordered": definition.ordered,
        "date_columns": [name for name, kind in types if kind == "DATE"],
    }
    path = destination / f"{key}.json"
    if key == 2388:
        result["advice"] = (
            "On this site CoffeeShop.input_position numbers the input rows starting at 1. Use it to preserve their original order. Return only id and drink."
        )
    if key == 3252:
        result["advice"] = (
            "For N teams the tier cutoffs are ceil(N/3) and ceil(2N/3). Use the shared competition rank for tied teams."
        )
    if key == 3188:
        result["advice"] = (
            "Count different elective courses in the student's major. Retaking the same elective counts once. Apply the grade rule to every graded attempt in that major and average GPA across all enrollments."
        )
    if key == 3328:
        result["advice"] = (
            "Alphabetize city names ignoring spaces for comparison, as in the published New York example. Preserve the spaces in the displayed names."
        )
    path.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("database_catalog/exercises"))
    parser.add_argument("ids", type=int, nargs="*")
    args = parser.parse_args()
    container = os.environ.get("CODE_PRACTICE_MYSQL_CONTAINER", "")
    if not container.startswith("nsy-study-mysql-") or container.startswith(
        "nsy-study-mysql-production"
    ):
        parser.error("Use a dedicated local MySQL authoring container.")
    args.out.mkdir(parents=True, exist_ok=True)
    errors = 0
    for key in args.ids or sorted(SETS):
        try:
            build(key, args.source, args.oracle, args.out)
            print(f"Built #{key}", flush=True)
        except Exception as e:
            errors += 1
            print(f"#{key}: {str(e)[:1400]}", file=sys.stderr, flush=True)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
