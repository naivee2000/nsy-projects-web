import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_126d import BATCH


ROOT = Path(__file__).resolve().parents[1]
IDS = (2288, 2289, 2290, 2291, 2293)


def test_batch_126_fourth_slice_is_complete_and_verified():
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


def test_batch_126_fourth_slice_inputs_are_distinct():
    for source_id in IDS:
        spec = BATCH[source_id]
        inputs = [arguments for arguments, _ in spec["examples"]] + spec["boundaries"]
        encoded = [json.dumps(arguments, sort_keys=True) for arguments in inputs]
        assert len(encoded) == len(set(encoded))


def test_corrected_stock_contract_and_hard_grid_are_retained():
    catalog = get_catalog()
    assert 'any subset of distinct stocks' in catalog['leetcode-2291'].statement
    assert catalog['leetcode-2290'].difficulty >= 8
