import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_113 import BATCH
from code_practice.import_batch_113b import BATCH as BATCH_B


ROOT = Path(__file__).resolve().parents[1]
IDS = (1959, 1960, 1961, 1962, 1963, 1964, 1966, 1967, 1969, 1970)
SPECS = {**BATCH, **BATCH_B}


def test_batch_113_slices_are_complete_and_verified():
    catalog = get_catalog()
    for source_id in IDS:
        problem = catalog[f"leetcode-{source_id}"]
        report = json.loads((ROOT / "catalog_import/reports" / f"leetcode-{source_id}.json").read_text())
        assert sum(case.visible for case in problem.tests) >= 2
        assert sum(not case.visible for case in problem.tests) >= 12
        assert len(problem.hints) == 4
        assert report["valid"] and report["reference_passed"] == len(problem.tests)
        assert report["oracle_inputs"] == 500
        assert all(wrong["failed_cases"] for wrong in report["wrong_solutions"])


def test_batch_113_inputs_are_distinct():
    for source_id in IDS:
        spec = SPECS[source_id]
        inputs = [arguments for arguments, _ in spec["examples"]] + spec["boundaries"]
        encoded = [json.dumps(arguments, sort_keys=True) for arguments in inputs]
        assert len(encoded) == len(set(encoded))


def test_long_palindrome_problem_retains_linear_target():
    problem = get_catalog()["leetcode-1960"]
    assert problem.difficulty >= 8
    assert problem.target_time_complexity == "O(n)"
    assert "Manacher algorithm" in problem.topics
