import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_124b import BATCH


ROOT = Path(__file__).resolve().parents[1]
IDS = (2226, 2229, 2231, 2233)


def test_batch_124_second_slice_is_complete_and_verified():
    catalog = get_catalog()
    for source_id in IDS:
        problem = catalog[f"leetcode-{source_id}"]
        report = json.loads((ROOT / "catalog_import/reports" / f"leetcode-{source_id}.json").read_text())
        assert sum(case.visible for case in problem.tests) >= 2
        assert sum(not case.visible for case in problem.tests) >= 12
        assert len(problem.hints) == 4
        assert report["valid"]
        assert report["reference_passed"] == len(problem.tests)
        assert report["oracle_inputs"] == 500
        assert all(item["failed_cases"] for item in report["wrong_solutions"])


def test_batch_124_second_slice_inputs_are_distinct():
    for source_id in IDS:
        spec = BATCH[source_id]
        inputs = [arguments for arguments, _ in spec["examples"]] + spec["boundaries"]
        encoded = [json.dumps(arguments, sort_keys=True) for arguments in inputs]
        assert len(encoded) == len(set(encoded))


def test_direct_addition_is_replaced_by_the_stronger_bitwise_sum():
    ledger = json.loads((ROOT / "catalog_import/ledger.json").read_text())
    record = next(item for item in ledger["records"] if item["source_id"] == 2235)
    assert record["status"] == "overlap"
    assert record["existing_id"] == "leetcode-371"
    assert "leetcode-2235" not in get_catalog()
    assert get_catalog()["leetcode-371"].difficulty >= 5
