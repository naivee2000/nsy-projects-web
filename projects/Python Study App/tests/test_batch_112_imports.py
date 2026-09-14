import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_112 import BATCH


ROOT = Path(__file__).resolve().parents[1]
IDS = (1936, 1937, 1938, 1940, 1941)


def test_first_batch_112_slice_is_complete_and_verified():
    catalog = get_catalog()
    for source_id in IDS:
        problem = catalog[f"leetcode-{source_id}"]
        report = json.loads((ROOT / "catalog_import/reports" / f"leetcode-{source_id}.json").read_text())
        assert len([case for case in problem.tests if case.visible]) >= 2
        assert len([case for case in problem.tests if not case.visible]) >= 12
        assert len(problem.hints) == 4
        assert report["valid"] and report["reference_passed"] == len(problem.tests)
        assert report["oracle_inputs"] == 500
        assert all(wrong["failed_cases"] for wrong in report["wrong_solutions"])


def test_first_batch_112_deterministic_inputs_are_distinct():
    for source_id in IDS:
        spec = BATCH[source_id]
        inputs = [arguments for arguments, _ in spec["examples"]] + spec["boundaries"]
        encoded = [json.dumps(arguments, sort_keys=True) for arguments in inputs]
        assert len(encoded) == len(set(encoded))


def test_genetic_queries_keep_the_full_ancestor_path_contract():
    problem = get_catalog()["leetcode-1938"]
    assert {"trees", "tries", "bit manipulation", "depth-first search"} <= set(problem.topics)
    assert problem.tests[0].expected == [2, 3, 7]
    assert problem.target_time_complexity == "O((n+q)*log V)"
