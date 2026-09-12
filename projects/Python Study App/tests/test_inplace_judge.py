import json
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.build_import_batch import workbook_sample
from code_practice.schemas import FunctionSignature, TestCase as Case
from code_practice.validation import run_source


@pytest.mark.parametrize("body,accepted", [
    ("nums[:2] = [1, 2]; return 2", True),
    ("nums[:] = [1, 2, 999, 888]; return 2", True),
    ("nums[:] = [1, 2]; return 2", True),
    ("nums = [1, 2]; return 2", False),
    ("return 2", False),
    ("nums[:2] = [1, 2]; return True", False),
    ("nums[:2] = [1, 2]; return 2.0", False),
    ("return -1", False),
    ("return 100", False),
    ("return None", False),
])
def test_prefix_judge_checks_mutation_and_strict_count_but_ignores_tail(body, accepted):
    problem = get_catalog()["leetcode-26"]
    case = problem.tests[0]
    before = json.dumps(case.arguments)
    assert run_source("def remove_duplicates(nums):\n    " + body, problem, case) == (accepted, None)
    assert json.dumps(case.arguments) == before


def test_remove_element_accepts_any_prefix_order_but_not_missing_duplicates():
    problem = get_catalog()["leetcode-27"]
    correct = "def remove_element(nums, val):\n    nums[:] = [v for v in nums if v != val][::-1]\n    return len(nums)"
    wrong = "def remove_element(nums, val):\n    nums[:] = sorted(set(v for v in nums if v != val))\n    return len(nums)"
    assert all(run_source(correct, problem, case) == (True, None) for case in problem.tests)
    assert any(run_source(wrong, problem, case) == (False, None) for case in problem.tests)


def test_mutation_observer_ignores_returned_copies_and_supports_other_parameter_positions():
    problem = get_catalog()["leetcode-48"]
    copy = "def rotate_image(matrix):\n    return [list(row) for row in zip(*matrix[::-1])]"
    rebind = "def rotate_image(matrix):\n    matrix = [list(row) for row in zip(*matrix[::-1])]"
    for source in (copy, rebind):
        assert run_source(source, problem, problem.tests[0]) == (False, None)
    signature = FunctionSignature(name="change_second", parameters=[
        {"name": "first", "annotation": "list[int]"}, {"name": "second", "annotation": "list[int]"}],
        returns="None", result_mode="mutated_argument", mutated_parameter=1)
    second = problem.model_copy(update={"signature": signature})
    case = Case(id="second-argument", arguments=[[9, 8], [2, 1]], expected=[1, 2])
    assert run_source("def change_second(first, second):\n    second.sort()", second, case) == (True, None)
    assert run_source("def change_second(first, second):\n    first.sort()", second, case) == (False, None)


def test_mutated_tree_uses_node_serializer_and_cycle_protection():
    original = get_catalog()["leetcode-226"]
    signature = original.signature.model_copy(update={"returns": "None", "result_mode": "mutated_argument", "mutated_parameter": 0})
    problem = original.model_copy(update={"signature": signature})
    for case in problem.tests:
        assert run_source(problem.reference_solution, problem, case) == (True, None)
    case = next(case for case in problem.tests if case.arguments[0])
    ok, error = run_source("def invert_tree(root):\n    root.left = root", problem, case)
    assert not ok and "cycle" in error


@pytest.mark.parametrize("updates", [
    {"result_mode": "returned_prefix"},
    {"result_mode": "returned_prefix", "mutated_parameter": 1},
    {"result_mode": "returned_prefix", "mutated_parameter": -1},
    {"result_mode": "return", "mutated_parameter": 0},
    {"result_mode": "returned_prefix", "mutated_parameter": 0, "returns": "None"},
])
def test_invalid_mutation_signatures_are_rejected(updates):
    payload = {"name": "solve", "parameters": [{"name": "nums", "annotation": "list[int]"}], "returns": "int"}
    with pytest.raises(ValueError):
        FunctionSignature.model_validate({**payload, **updates})


def test_prefix_sample_parser_preserves_count_and_ignores_only_unspecified_tail():
    parameters = [{"name": "nums", "annotation": "list[int]", "adapter": "raw"}]
    sample = "Input nums = [1,1,2] → Output 2, nums = [1,2,_]."
    assert workbook_sample(sample, parameters, "returned_prefix", 0) == ([[1, 1, 2]], {"return": 2, "prefix": [1, 2]})
    for output in ("2, nums=[1,_,2]", "4, nums=[1,2,_]", "True, nums=[1]",
                   "2, other=[1,2]", "2, nums=[1,2,__import__('os')]", "2, nums=[1,2], nums=[3,4]"):
        with pytest.raises((ValueError, SyntaxError)):
            workbook_sample("Input nums = [1,1,2] → Output " + output, parameters, "returned_prefix", 0)


def test_inplace_batch_domain_limits_and_reference_algorithm_restrictions():
    import ast
    from code_practice.import_batch_011 import BATCH, COLORS
    assert not any(isinstance(node, ast.Call) and (
        isinstance(node.func, ast.Name) and node.func.id == "sorted"
        or isinstance(node.func, ast.Attribute) and node.func.attr == "sort") for node in ast.walk(ast.parse(COLORS)))
    for pid, spec in BATCH.items():
        rng = random.Random(4047 + pid)
        cases = [args for args, _ in spec["examples"]] + spec["boundaries"]
        cases += [args for args, _ in spec["stress"]]
        cases += [spec["generator"](rng) for _ in range(500)]
        for args in cases:
            if pid in (26, 80):
                assert 1 <= len(args[0]) <= 30000 and args[0] == sorted(args[0])
                bound = 100 if pid == 26 else 10000
                assert all(-bound <= value <= bound for value in args[0])
            elif pid == 27:
                assert len(args[0]) <= 100 and 0 <= args[1] <= 100
                assert all(0 <= value <= 50 for value in args[0])
            elif pid in (31, 75):
                assert 1 <= len(args[0]) <= (100 if pid == 31 else 300)
                assert all(0 <= value <= (100 if pid == 31 else 2) for value in args[0])
            elif pid in (48, 73):
                matrix = args[0]
                maximum = 20 if pid == 48 else 200
                assert 1 <= len(matrix) <= maximum and 1 <= len(matrix[0]) <= maximum
                assert all(len(row) == len(matrix[0]) for row in matrix)
                if pid == 48:
                    assert len(matrix) == len(matrix[0])
                lo, hi = (-1000, 1000) if pid == 48 else (-(2**31), 2**31 - 1)
                assert all(lo <= value <= hi for row in matrix for value in row)
            else:
                first, m, second, n = args
                assert 0 <= m and 0 <= n and 1 <= m + n <= 200
                assert len(first) == m + n and len(second) == n
                assert first[:m] == sorted(first[:m]) and second == sorted(second)
                assert first[m:] == [0] * n
                assert all(-10**9 <= value <= 10**9 for value in first + second)
