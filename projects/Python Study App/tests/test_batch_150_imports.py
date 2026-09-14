import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_150 import BATCH

ROOT = Path(__file__).resolve().parents[1]
IDS = (2516, 2517, 2518, 2519, 2521)


def test_batch_150_is_complete_and_verified():
    catalog = get_catalog()
    for source_id in IDS:
        problem = catalog[f"leetcode-{source_id}"]
        report = json.loads(
            (ROOT / "catalog_import/reports" / f"leetcode-{source_id}.json").read_text()
        )
        assert sum(test.visible for test in problem.tests) >= 2
        assert sum(not test.visible for test in problem.tests) >= 12
        assert len(problem.hints) == 4
        assert report["valid"] and report["oracle_inputs"] == 500
        assert report["reference_passed"] == len(problem.tests)
        assert all(item["failed_cases"] for item in report["wrong_solutions"])


def test_batch_150_inputs_are_distinct():
    for source_id in IDS:
        values = [args for args, _ in BATCH[source_id]["examples"]]
        values += BATCH[source_id]["boundaries"]
        encoded = [json.dumps(args, sort_keys=True) for args in values]
        assert len(encoded) == len(set(encoded))
