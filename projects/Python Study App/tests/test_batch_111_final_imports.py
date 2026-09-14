import json
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_111d import BATCH
from code_practice.validation import run_source


ROOT = Path(__file__).resolve().parents[1]
IDS = (1930, 1931, 1932, 1933, 1935)


def test_final_batch_111_slice_is_complete_and_verified():
    catalog = get_catalog()
    for source_id in IDS:
        problem = catalog[f"leetcode-{source_id}"]
        report = json.loads((ROOT / "catalog_import/reports" / f"leetcode-{source_id}.json").read_text())
        assert problem.status == "approved"
        assert len([case for case in problem.tests if case.visible]) >= 2
        assert len([case for case in problem.tests if not case.visible]) >= 12
        assert len(problem.hints) == 4
        assert report["valid"] is True
        assert report["reference_passed"] == len(problem.tests)
        assert report["oracle_inputs"] == 500
        assert all(item["failed_cases"] for item in report["wrong_solutions"])


def test_tree_forest_adapter_builds_real_nodes_and_serializes_the_result():
    problem = get_catalog()["leetcode-1932"]
    assert problem.signature.parameters[0].adapter == "treenode_list"
    assert problem.signature.return_adapter == "treenode"
    assert "class TreeNode" in problem.starter_code
    assert run_source(problem.reference_solution, problem, problem.tests[0]) == (True, None)
    wrong_shape = '''def merge_small_bsts(trees):
    return trees[0]
'''
    assert run_source(wrong_shape, problem, problem.tests[0]) == (False, None)


def test_batch_111_final_specs_have_distinct_deterministic_inputs():
    for source_id in IDS:
        spec = BATCH[source_id]
        visible = [arguments for arguments, _ in spec["examples"]]
        all_inputs = visible + spec["boundaries"]
        serialized = [json.dumps(arguments, sort_keys=True) for arguments in all_inputs]
        assert len(serialized) == len(set(serialized))
