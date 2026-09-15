import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_216a import BATCH as BATCH_A
from code_practice.import_batch_216b import BATCH as BATCH_B

BATCH = {**BATCH_A, **BATCH_B}

ROOT = Path(__file__).resolve().parents[1]
IDS = tuple(BATCH)


def test_batch_216_verified():
    catalog = get_catalog()
    for source_id in IDS:
        problem = catalog[f"leetcode-{source_id}"]
        report = json.loads((ROOT / "catalog_import/reports" / f"leetcode-{source_id}.json").read_text())
        assert sum(test.visible for test in problem.tests) >= 2
        assert sum(not test.visible for test in problem.tests) >= 12
        assert len(problem.hints) == 4
        assert report["valid"] and report["oracle_inputs"] == 500
        assert len(report["wrong_solutions"]) >= 2
        assert all(item["failed_cases"] for item in report["wrong_solutions"])


def test_batch_216_inputs_are_distinct():
    for spec in BATCH.values():
        values = [args for args, _ in spec["examples"]] + spec["boundaries"]
        encoded = [json.dumps(args, sort_keys=True) for args in values]
        assert len(encoded) == len(set(encoded))
