from itertools import combinations, permutations, product
import json
from pathlib import Path

from code_practice.build_import_batch import build
from code_practice.import_batch_024 import BATCH, lca_oracle, paint_oracle, tree_paths_oracle
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.schemas import TestCase as Case
from code_practice.validation import run_source


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    row["source_id"]: row
    for line in (ROOT / "catalog_import/sources.jsonl").read_text().splitlines()
    if (row := json.loads(line))
}


def problem(problem_id):
    return build(problem_id, BATCH[problem_id], SOURCES[problem_id])


def reference(problem_id):
    namespace = {}
    exec(BATCH[problem_id]["reference"], namespace)
    return namespace[BATCH[problem_id]["name"]]


def test_batch_has_complete_content_and_preserves_every_workbook_sample():
    for problem_id in BATCH:
        candidate = problem(problem_id)
        assert sum(case.visible for case in candidate.tests) == 2
        assert sum(not case.visible for case in candidate.tests) >= 12
        assert len({json.dumps(case.arguments, sort_keys=True) for case in candidate.tests}) == len(candidate.tests)
        assert candidate.reference_solution and len(candidate.hints) == 4 and candidate.editorial
        assert len(candidate.known_wrong_solutions) >= 2
        assert any(case.arguments == BATCH[problem_id]["examples"][0][0] for case in candidate.tests if case.visible)


def test_lca_contract_passes_real_tree_references_and_rejects_copies_or_mutation():
    for problem_id in (235, 236):
        candidate = problem(problem_id)
        assert [parameter.adapter for parameter in candidate.signature.parameters] == [
            "treenode", "treenode_ref", "treenode_ref"
        ]
        assert [parameter.source_parameter for parameter in candidate.signature.parameters] == [None, 0, 0]
        assert candidate.signature.return_adapter == "treenode_value"
        assert candidate.signature.node_policy == "return_input_node"
        assert "class TreeNode" in candidate.starter_code
        assert run_source(candidate.reference_solution, candidate, candidate.tests[0]) == (True, None)

        name = candidate.signature.name
        copied = f"def {name}(root, p, q):\n    return TreeNode(root.val)\n"
        mutated = f"def {name}(root, p, q):\n    root.left = None\n    return root\n"
        assert run_source(copied, candidate, candidate.tests[0]) == (False, None)
        assert run_source(mutated, candidate, candidate.tests[0]) == (False, None)

    tree = [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]
    assert lca_oracle([tree, 5, 1]) == 3
    assert lca_oracle([tree, 5, 4]) == 5


def test_preorder_reference_matches_direct_partition_definition_for_all_short_orders():
    solve = reference(255)
    oracle = BATCH[255]["oracle"]
    for length in range(1, 7):
        for values in permutations(range(1, length + 1)):
            values = list(values)
            assert solve(values) == oracle([values])


def test_tree_paths_keep_complete_branches_and_duplicate_value_paths():
    candidate = problem(257)
    assert candidate.signature.parameters[0].adapter == "treenode"
    assert candidate.tests[0].comparator == "unordered"
    duplicate = [1, 2, 2, 3, None, None, 3]
    expected = ["1->2->3", "1->2->3"]
    assert tree_paths_oracle([duplicate]) == expected
    assert run_source(candidate.reference_solution, candidate,
                      Case(id="duplicates", arguments=[duplicate], expected=expected,
                           comparator="unordered")) == (True, None)
    assert review_focus_boost(candidate) >= 50


def test_three_sum_smaller_matches_all_short_repeated_value_arrays():
    solve = reference(259)
    oracle = BATCH[259]["oracle"]
    for length in range(7):
        for nums in product((-1, 0, 1), repeat=length):
            nums = list(nums)
            for target in (-2, 0, 2):
                assert solve(nums, target) == oracle([nums, target])


def test_two_singletons_preserve_signed_values_and_index_multiplicity():
    solve = reference(260)
    for pair_count in range(4):
        values = list(range(-pair_count - 2, pair_count + 3))
        for singles in combinations(values, 2):
            pairs = [value for value in values if value not in singles][:pair_count]
            nums = [*singles, *(value for pair in pairs for value in (pair, pair))]
            assert sorted(solve(nums)) == sorted(singles)


def test_graph_reference_matches_connectivity_definition_for_every_small_simple_graph():
    solve = reference(261)
    oracle = BATCH[261]["oracle"]
    for node_count in range(1, 6):
        possible = [[left, right] for left in range(node_count) for right in range(left + 1, node_count)]
        for mask in range(1 << len(possible)):
            edges = [edge for index, edge in enumerate(possible) if mask & (1 << index)]
            assert solve(node_count, edges) == oracle([node_count, edges])


def test_ugly_references_cover_membership_and_sequence_boundaries():
    is_ugly = reference(263)
    ugly_oracle = BATCH[263]["oracle"]
    for value in range(-50, 501):
        assert is_ugly(value) == ugly_oracle([value])

    nth = reference(264)
    nth_oracle = BATCH[264]["oracle"]
    for index in range(1, 170):
        assert nth(index) == nth_oracle([index])
    assert nth(1690) == 2123366400


def test_many_color_painting_matches_exhaustive_assignments_and_has_reachable_prerequisite():
    solve = reference(265)
    for houses, colors in ((1, 2), (2, 2), (3, 2), (1, 3), (2, 3)):
        for cells in product((1, 2, 3), repeat=houses * colors):
            costs = [list(cells[index * colors:(index + 1) * colors]) for index in range(houses)]
            assert solve(costs) == paint_oracle([costs])

    candidate = problem(265)
    assert candidate.difficulty >= 8
    assert not prerequisites_met(candidate, {"dynamic-programming": 69})
    assert prerequisites_met(candidate, {"dynamic-programming": 70})


def test_seeded_generators_stay_inside_declared_source_domains():
    import random

    rng = random.Random(4047)
    for _ in range(500):
        preorder = BATCH[255]["generator"](rng)[0]
        assert 1 <= len(preorder) <= 10 and len(preorder) == len(set(preorder))
        assert all(1 <= value <= 10000 for value in preorder)

        nums, target = BATCH[259]["generator"](rng)
        assert len(nums) <= 10 and all(-100 <= value <= 100 for value in nums)
        assert -100 <= target <= 100

        node_count, edges = BATCH[261]["generator"](rng)
        assert 1 <= node_count <= 2000 and len(edges) <= 5000
        assert len({tuple(sorted(edge)) for edge in edges}) == len(edges)
        assert all(0 <= left < node_count and 0 <= right < node_count and left != right
                   for left, right in edges)

        costs = BATCH[265]["generator"](rng)[0]
        assert 1 <= len(costs) <= 100 and 2 <= len(costs[0]) <= 20
        assert all(len(row) == len(costs[0]) and all(1 <= value <= 20 for value in row)
                   for row in costs)
