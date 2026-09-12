import json
import random
from itertools import product
from pathlib import Path

from code_practice.catalog import get_catalog
from code_practice.import_batch_025 import (
    BATCH,
    h_index_oracle,
    paint_fence_oracle,
    palindrome_permutations_oracle,
    perfect_squares_oracle,
)
from code_practice.schemas import TestCase as Case
from code_practice.validation import run_source


ROOT = Path(__file__).resolve().parents[1]
IDS = (237, 266, 267, 270, 272, 273, 274, 275, 276, 279)


def test_batch_twenty_five_is_complete_and_published():
    catalog = get_catalog()
    assert set(BATCH) == set(IDS)
    for problem_id in IDS:
        problem = catalog[f"leetcode-{problem_id}"]
        assert sum(test.visible for test in problem.tests) >= 2
        assert sum(not test.visible for test in problem.tests) >= 12
        assert all(test.explanation for test in problem.tests if test.visible)
        assert len(problem.hints) == 4
        assert len(problem.known_wrong_solutions) >= 2
        report = json.loads((ROOT / "catalog_import/reports" / f"leetcode-{problem_id}.json").read_text())
        assert report["valid"] and report["oracle_inputs"] == 500
        assert report["reference_passed"] == len(problem.tests)
        assert all(item["failed_cases"] for item in report["wrong_solutions"])


def test_delete_node_uses_source_sample_context_and_every_selected_position():
    problem = get_catalog()["leetcode-237"]
    assert problem.signature.parameters[0].adapter == "listnode_ref"
    assert problem.signature.node_policy == "delete_referenced_list_node"
    assert problem.signature.result_mode == "mutated_argument"
    report = json.loads((ROOT / "catalog_import/reports/leetcode-237.json").read_text())
    adapter = report["sample_contract_adapter"]
    assert adapter["source_sample"] == "Input head = [4,5,1,9], node = 5 → Output [4,1,9]."
    assert adapter["arguments"] == [{"values": [4, 5, 1, 9], "index": 1}]
    for length in range(2, 20):
        values = [index % 4 - 2 for index in range(length)]
        for selected in range(length - 1):
            case = Case(
                id=f"delete-{length}-{selected}",
                arguments=[{"values": values, "index": selected}],
                expected=values[:selected] + values[selected + 1:],
            )
            assert run_source(problem.reference_solution, problem, case) == (True, None)


def test_palindrome_generation_is_unique_complete_and_palindromic():
    for length in range(1, 8):
        for letters in product("abc", repeat=length):
            text = "".join(letters)
            output = palindrome_permutations_oracle([text])
            assert len(output) == len(set(output))
            assert all(value == value[::-1] and sorted(value) == sorted(text) for value in output)
            assert bool(output) == (sum(text.count(char) % 2 for char in set(text)) <= 1)


def test_h_index_oracle_matches_rank_definition_exhaustively():
    for length in range(1, 6):
        for citations in product(range(6), repeat=length):
            expected = sum(value >= rank for rank, value in enumerate(sorted(citations, reverse=True), 1))
            # Feasible ranks form a prefix, so count and maximum are equal.
            assert h_index_oracle([list(citations)]) == expected
            assert h_index_oracle([sorted(citations)]) == expected


def test_paint_fence_oracle_matches_exhaustive_color_assignments():
    for posts in range(1, 7):
        for colors in range(1, 5):
            brute = sum(
                all(not (assignment[index] == assignment[index - 1] == assignment[index - 2])
                    for index in range(2, posts))
                for assignment in product(range(colors), repeat=posts)
            )
            assert paint_fence_oracle([posts, colors]) == brute


def test_perfect_square_oracle_matches_independent_dynamic_program():
    best = list(range(501))
    for value in range(1, 501):
        best[value] = 1 + min(best[value - root * root]
                              for root in range(1, int(value ** .5) + 1))
        assert perfect_squares_oracle([value]) == best[value]


def test_batch_generators_stay_inside_reviewed_domains():
    rng = random.Random(4047)
    for problem_id, spec in BATCH.items():
        for _ in range(500):
            args = spec["generator"](rng)
            if problem_id == 237:
                payload = args[0]
                assert 2 <= len(payload["values"]) <= 25
                assert 0 <= payload["index"] < len(payload["values"]) - 1
            elif problem_id in (266, 267):
                assert args[0] and args[0].islower() and args[0].isalpha()
                assert len(args[0]) <= (8 if problem_id == 267 else 18)
            elif problem_id in (270, 272):
                assert args[0] and all(value is None or type(value) is int for value in args[0])
                if problem_id == 272:
                    assert 1 <= args[2] <= len([value for value in args[0] if value is not None])
            elif problem_id == 273:
                assert 0 <= args[0] <= 2**31 - 1
            elif problem_id in (274, 275):
                assert 1 <= len(args[0]) <= 30 and all(0 <= value <= 50 for value in args[0])
                if problem_id == 275:
                    assert args[0] == sorted(args[0])
            elif problem_id == 276:
                assert 1 <= args[0] <= 8 and 1 <= args[1] <= 5
                assert paint_fence_oracle(args) <= 2**31 - 1
            elif problem_id == 279:
                assert 1 <= args[0] <= 500
