import random
from collections import Counter
from fractions import Fraction

from code_practice.catalog import get_catalog
from code_practice.import_batch_013 import BATCH, cuts_oracle, rpn_oracle
from code_practice.learning import prerequisites_met
from code_practice.schemas import TestCase as Case
from code_practice.validation import run_source


def assert_postfix_domain(tokens):
    assert 1 <= len(tokens) <= 10000
    values = []
    for token in tokens:
        if token not in {"+", "-", "*", "/"}:
            value = int(token)
            assert -200 <= value <= 200
        else:
            assert len(values) >= 2
            right, left = values.pop(), values.pop()
            if token == "+":
                value = left + right
            elif token == "-":
                value = left - right
            elif token == "*":
                value = left * right
            else:
                assert right != 0
                value = int(Fraction(left, right))
        assert -(2**31) <= value < 2**31
        values.append(value)
    assert len(values) == 1
    return values[0]


def test_sequence_expression_inputs_and_generators_obey_source_constraints():
    for pid, spec in BATCH.items():
        rng = random.Random(4047 + pid)
        cases = [args for args, _ in spec["examples"]] + spec["boundaries"]
        cases += [args for args, _ in spec["stress"]]
        cases += [spec["generator"](rng) for _ in range(500)]
        for (value,) in cases:
            if pid == 128:
                assert len(value) <= 100000
                assert all(type(item) is int and -10**9 <= item <= 10**9 for item in value)
            elif pid == 132:
                assert 1 <= len(value) <= 2000
                assert set(value) <= set("abcdefghijklmnopqrstuvwxyz")
            elif pid == 137:
                assert 1 <= len(value) <= 30000
                assert all(type(item) is int and -(2**31) <= item < 2**31 for item in value)
                counts = Counter(value)
                assert sum(count == 1 for count in counts.values()) == 1
                assert all(count in (1, 3) for count in counts.values())
            else:
                assert_postfix_domain(value)
        if pid == 150:
            for args, expected in spec["stress"]:
                assert assert_postfix_domain(args[0]) == expected


def test_postfix_division_truncates_to_zero_and_keeps_operand_order():
    problem = get_catalog()["leetcode-150"]
    for tokens, expected in [(["7", "-3", "/"], -2), (["-7", "3", "/"], -2),
                             (["-7", "-3", "/"], 2), (["2", "5", "-"], -3)]:
        assert rpn_oracle([tokens]) == expected
        case = Case(id="operand-order", arguments=[tokens], expected=expected)
        assert run_source(problem.reference_solution, problem, case) == (True, None)


def test_palindrome_cuts_are_not_piece_counts_and_cover_even_centers():
    problem = get_catalog()["leetcode-132"]
    for text, expected in [("a", 0), ("abba", 0), ("aab", 1), ("abc", 2), ("banana", 1)]:
        assert cuts_oracle([text]) == expected
        case = Case(id="cuts", arguments=[text], expected=expected)
        assert run_source(problem.reference_solution, problem, case) == (True, None)
    assert problem.difficulty >= 8
    assert not prerequisites_met(problem, {"strings": 100, "dynamic-programming": 69})
    assert prerequisites_met(problem, {"strings": 70, "dynamic-programming": 70})


def test_signed_singleton_and_noncontiguous_consecutive_values():
    for pid, arguments, expected in [
        (137, [[-2147483648, 7, 7, 7]], -2147483648),
        (137, [[-2147483648] * 3 + [2147483647]], 2147483647),
        (128, [[100, 4, 200, 1, 3, 2]], 4),
        (128, [[1, 1, 2, 2, 3]], 3),
    ]:
        problem = get_catalog()[f"leetcode-{pid}"]
        case = Case(id="representation", arguments=arguments, expected=expected)
        assert run_source(problem.reference_solution, problem, case) == (True, None)
