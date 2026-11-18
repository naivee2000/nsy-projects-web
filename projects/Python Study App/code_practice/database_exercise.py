"""Shared definitions for executable Database exercises and their reproducible cases."""
import json
from random import Random


def table(columns, rows):
    return {"columns": list(columns), "rows": list(rows)}


def fixture(tables, columns, rows, **parameters):
    return {"tables": tables, "expected": table(columns, rows), "parameters": parameters}


def sample_set(seed, factory):
    random = Random(seed)
    cases = [factory(random, i) for i in range(16)]
    assert len({json.dumps((c["tables"], c["parameters"], c.get("schema")), sort_keys=True)
                for c in cases}) == len(cases)
    return cases


def exercise(topic, schema, cases, sql, pandas, wrong, *, runner="query", ordered=False, advice="",
             routine=None, result_table=None, scalar_column=None, mysql_starter=None, wrong_pandas=(), date_columns=()):
    return {"topic": topic, "schema": schema, "cases": cases, "sql": sql, "pandas": pandas,
            "runner": runner, "ordered": ordered, "wrong": wrong, "advice": advice,
            "routine": routine, "result_table": result_table, "scalar_column": scalar_column,
            "mysql_starter": mysql_starter or "-- Write your MySQL solution here.\n",
            "wrong_pandas": list(wrong_pandas), "date_columns": list(date_columns)}
