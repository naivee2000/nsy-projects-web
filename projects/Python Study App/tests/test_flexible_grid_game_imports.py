from itertools import product
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_026 import (
    BATCH,
    INF,
    flip_grundy_wins,
    flip_win_oracle,
    life_oracle,
    wiggle_oracle,
)
from code_practice.schemas import TestCase as Case
from code_practice.validation import compare, run_source


IDS = (280, 282, 283, 285, 286, 287, 289, 291, 292, 293, 294)


def test_batch_26_is_published_with_complete_executable_evidence():
    catalog = get_catalog()
    for problem_id in IDS:
        problem = catalog[f"leetcode-{problem_id}"]
        assert problem.status == "approved"
        assert len([case for case in problem.tests if case.visible]) >= 2
        assert len([case for case in problem.tests if not case.visible]) >= 12
        assert len(problem.hints) == 4
        assert problem.editorial and problem.reference_solution
        assert len(problem.known_wrong_solutions) >= 2
        assert all(run_source(problem.reference_solution, problem, case)[0]
                   for case in problem.tests)
        for wrong in problem.known_wrong_solutions:
            assert any(run_source(wrong, problem, case) == (False, None)
                       for case in problem.tests)


def test_wiggle_oracle_and_property_cover_every_short_array():
    for length in range(1, 7):
        for values in product((-1, 0, 1), repeat=length):
            expected = wiggle_oracle([list(values)])
            assert sorted(expected) == sorted(values)
            assert compare(expected, expected, "wiggle")
    problem = get_catalog()["leetcode-280"]
    alternate = Case(id="alternate-wiggle", arguments=[[1, 2, 3, 4, 5, 6]],
                     expected=[1, 3, 2, 5, 4, 6], comparator="wiggle")
    assert run_source(problem.reference_solution, problem, alternate) == (True, None)


def test_game_of_life_matches_immutable_oracle_on_all_three_by_three_boards():
    problem = get_catalog()["leetcode-289"]
    for cells in product((0, 1), repeat=9):
        board = [list(cells[row:row + 3]) for row in range(0, 9, 3)]
        case = Case(id="life-exhaustive", arguments=[board], expected=life_oracle([board]))
        assert run_source(problem.reference_solution, problem, case) == (True, None)


def test_flip_game_optimized_stress_logic_matches_recursive_oracle_on_short_states():
    for length in range(1, 11):
        for state in map("".join, product("+-", repeat=length)):
            assert flip_grundy_wins(state) == flip_win_oracle([state])


def test_successor_requires_an_existing_tree_node_and_allows_none():
    problem = get_catalog()["leetcode-285"]
    existing = Case(id="successor-existing", arguments=[[5, 3, 7, 2, 4, 6, 8], 4], expected=5)
    maximum = Case(id="successor-none", arguments=[[2, 1, 3], 3], expected=None)
    assert run_source(problem.reference_solution, problem, existing) == (True, None)
    assert run_source(problem.reference_solution, problem, maximum) == (True, None)
    assert run_source("def inorder_successor(root, p):\n    return TreeNode(5)",
                      problem, existing) == (False, None)
    assert run_source("def inorder_successor(root, p):\n    root.left = None\n    return None",
                      problem, maximum) == (False, None)


def test_duplicate_input_is_read_only_even_when_return_value_is_correct():
    problem = get_catalog()["leetcode-287"]
    case = Case(id="duplicate-read-only", arguments=[[1, 3, 4, 2, 2]], expected=2)
    source = "def find_duplicate(nums):\n    nums.sort()\n    return 2"
    assert run_source(source, problem, case) == (False, None)


def test_batch_26_generators_stay_inside_reviewed_contracts():
    for problem_id, spec in BATCH.items():
        rng = random.Random(4047 + problem_id)
        for _ in range(500):
            args = spec["generator"](rng)
            if problem_id == 280:
                assert 1 <= len(args[0]) <= 30
            elif problem_id == 282:
                assert 1 <= len(args[0]) <= 7 and args[0].isdigit()
            elif problem_id == 283:
                assert 1 <= len(args[0]) <= 50
            elif problem_id == 285:
                assert args[1] in args[0]
            elif problem_id == 286:
                assert args[0] and args[0][0]
                assert all(value in (INF, -1, 0) for row in args[0] for value in row)
            elif problem_id == 287:
                values = args[0]
                maximum = len(values) - 1
                repeats = [value for value in set(values) if values.count(value) > 1]
                assert len(repeats) == 1
                assert all(1 <= value <= maximum for value in values)
            elif problem_id == 289:
                assert all(value in (0, 1) for row in args[0] for value in row)
            elif problem_id == 291:
                assert len(args[0]) <= len(args[1])
            elif problem_id == 292:
                assert 1 <= args[0] <= 200
            else:
                assert set(args[0]) <= {"+", "-"}
