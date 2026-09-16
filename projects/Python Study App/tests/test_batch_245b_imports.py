import json
from itertools import product
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_245b import BATCH, attendance_oracle, palindrome_oracle


ROOT = Path(__file__).resolve().parents[1]


def test_batch_245b_verified():
    catalog = get_catalog()
    records = {record["source_id"]: record for record in json.loads(
        (ROOT / "catalog_import" / "ledger.json").read_text())["records"]}
    for source_id, spec in BATCH.items():
        if records[source_id]["status"] != "imported":
            continue
        problem = catalog[f"leetcode-{source_id}"]
        report = json.loads((ROOT / "catalog_import" / "reports" / f"leetcode-{source_id}.json").read_text())
        assert problem.signature.name == spec["name"]
        assert sum(test.visible for test in problem.tests) >= 2
        assert sum(not test.visible for test in problem.tests) >= 12
        assert len(problem.hints) == 4
        assert report["valid"]
        assert report["reference_passed"] == len(problem.tests)
        assert report["oracle_inputs"] >= 500
        assert len(report["wrong_solutions"]) >= 2
        assert all(item["failed_cases"] for item in report["wrong_solutions"])


def test_batch_245b_inputs_are_distinct():
    for spec in BATCH.values():
        encoded = [json.dumps(value, sort_keys=True) for value in (
            [args for args, _ in spec["examples"]] + spec["boundaries"])]
        assert len(encoded) == len(set(encoded))


def test_attendance_oracle_matches_literal_enumeration():
    for days in range(1, 9):
        expected = sum(record.count("A") < 2 and "LLL" not in record
                       for record in map("".join, product("ALP", repeat=days)))
        assert attendance_oracle([days]) == expected


def test_palindrome_rank_oracle_matches_literal_search():
    for value in range(1, 5001):
        for distance in range(1, value + 2):
            lower, upper = value - distance, value + distance
            if lower >= 0 and str(lower) == str(lower)[::-1]:
                expected = str(lower)
                break
            if str(upper) == str(upper)[::-1]:
                expected = str(upper)
                break
        assert palindrome_oracle([str(value)]) == expected
