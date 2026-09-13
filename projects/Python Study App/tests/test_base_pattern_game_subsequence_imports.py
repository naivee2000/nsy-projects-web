from copy import deepcopy
from itertools import product
from math import isqrt
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_046 import BATCH, root_base_oracle
from code_practice.learning import review_focus_boost
from code_practice.validation import run_source


def reference(pid):
    namespace = {}
    exec(BATCH[pid]['reference'], namespace)
    return namespace[BATCH[pid]['name']]


@pytest.mark.parametrize('pid', BATCH)
def test_batch_46_reference_and_logical_wrong_solutions(pid):
    problem = get_catalog()[f'leetcode-{pid}']
    assert problem.status == 'approved' and len(problem.hints) == 4 and problem.editorial
    assert sum(t.visible for t in problem.tests) == 2
    assert sum(not t.visible for t in problem.tests) >= 12
    assert all(run_source(problem.reference_solution, problem, t) == (True, None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        outcomes = [run_source(wrong, problem, t) for t in problem.tests]
        assert (False, None) in outcomes and all(error is None for _, error in outcomes)


@pytest.mark.parametrize('pid', BATCH)
def test_batch_46_source_domains(pid):
    spec = BATCH[pid]
    rng = random.Random(4047 + pid)
    inputs = ([a for a, _ in spec['examples']] + spec['boundaries']
              + [a for a, _ in spec['stress']] + [spec['generator'](rng) for _ in range(500)])
    for args in inputs:
        value = args[0]
        if pid == 483:
            assert type(value) is str and value.isascii() and value.isdecimal()
            assert value == str(int(value)) and 3 <= int(value) <= 10**18
        elif pid == 484:
            assert 1 <= len(value) <= 100000 and set(value) <= {'I', 'D'}
        elif pid == 486:
            assert 1 <= len(value) <= 20
            assert all(type(x) is int and 0 <= x <= 10**7 for x in value)
        elif pid == 487:
            assert 1 <= len(value) <= 100000 and all(type(x) is int and x in (0, 1) for x in value)
        elif pid == 491:
            assert 1 <= len(value) <= 15 and all(type(x) is int and -100 <= x <= 100 for x in value)
        else:
            assert type(value) is int and 1 <= value <= 10**7


@pytest.mark.parametrize('pid', BATCH)
def test_batch_46_maximum_cases_preserve_input(pid):
    solve = reference(pid)
    for args, expected in BATCH[pid]['stress']:
        copied = deepcopy(args)
        actual = solve(*copied)
        assert (sorted(actual) == sorted(expected)) if pid == 491 else (actual == expected)
        assert copied == args


def test_good_base_exhaustive_small_and_exact_large_certificates():
    solve = reference(483)
    for number in range(3, 3001):
        assert solve(str(number)) == BATCH[483]['oracle']([str(number)]) == root_base_oracle(number)
    rng = random.Random(483)
    numbers = [int(args[0]) for args, _ in BATCH[483]['stress']]
    numbers += [rng.randint(3, 10**18) for _ in range(500)]
    for base in (2, 3, 7, 10, 31, 100, 999, 999999):
        number = 1 + base
        while number * base + 1 <= 10**18:
            number = number * base + 1
            numbers.append(number)
    for number in numbers:
        answer = solve(str(number))
        assert type(answer) is str and answer == root_base_oracle(number)
        base, remaining = int(answer), number
        assert 2 <= base < number
        while remaining:
            remaining, digit = divmod(remaining, base)
            assert digit == 1


def test_pattern_permutation_exhaustive_lexicographic_minimality():
    solve = reference(484)
    for length in range(1, 7):
        for chars in product('ID', repeat=length):
            pattern = ''.join(chars)
            actual = solve(pattern)
            assert actual == BATCH[484]['oracle']([pattern])
            assert sorted(actual) == list(range(1, length + 2))
    for args, expected in BATCH[484]['stress']:
        pattern = args[0]
        assert sorted(expected) == list(range(1, len(pattern) + 2))
        assert all((a < b) == (c == 'I') for a, b, c in zip(expected, expected[1:], pattern))


def test_optimal_game_exhaustive_literal_turns_and_ties():
    solve = reference(486)
    for length in range(1, 8):
        for values in product(range(3), repeat=length):
            nums = list(values)
            assert solve(nums) == BATCH[486]['oracle']([nums])
    assert solve([0]) is True and solve([1, 1]) is True
    assert solve([1, 5, 233, 7]) is True
    # Literal alternating minimax also checks every maximum-size fixture.
    for args, expected in BATCH[486]['stress']:
        assert BATCH[486]['oracle'](args) == expected
    assert review_focus_boost(get_catalog()['leetcode-486']) >= 50


def test_one_flip_exhaustive_and_single_pass_stream():
    solve = reference(487)
    for length in range(1, 11):
        for values in product((0, 1), repeat=length):
            nums = list(values)
            assert solve(nums) == BATCH[487]['oracle']([nums])
            assert solve(iter(nums)) == solve(nums)
    # A generator has no indexing, length, copying, or second iteration.
    assert solve(value for value in [1] * 49999 + [0] + [1] * 50000) == 100000
    assert solve(iter([1] * 100000)) == 100000


def test_subsequences_exhaustive_value_deduplication_and_index_order():
    solve = reference(491)
    for length in range(1, 8):
        for values in product((-1, 0, 1), repeat=length):
            nums = list(values)
            actual = solve(nums)
            assert sorted(actual) == BATCH[491]['oracle']([nums])
            assert len(actual) == len(set(map(tuple, actual)))
    assert len(solve(list(range(15)))) == 2**15 - 16
    assert solve([4, 4, 3, 2, 1]) == [[4, 4]]
    assert review_focus_boost(get_catalog()['leetcode-491']) >= 50


def test_subsequence_comparator_preserves_row_order_and_multiplicity():
    problem = get_catalog()['leetcode-491']
    assert all(t.comparator == 'unordered' for t in problem.tests)
    case = next(t for t in problem.tests if t.arguments == [[4, 6, 7, 7]])
    source = problem.reference_solution.replace('def nondecreasing_subsequences(', 'def original(')
    for expression, accepted in (
        ('list(reversed(original(nums)))', True),
        ('[list(reversed(row)) for row in original(nums)]', False),
        ('original(nums) + [original(nums)[0]]', False),
        ('original(nums)[:-1]', False),
    ):
        wrapper = source + '\ndef nondecreasing_subsequences(nums):\n    return ' + expression + '\n'
        assert run_source(wrapper, problem, case) == (accepted, None)


def test_rectangle_exhaustive_gap_optimality_and_large_boundaries():
    solve = reference(492)
    for area in range(1, 5001):
        assert solve(area) == BATCH[492]['oracle']([area])
    for args, expected in BATCH[492]['stress']:
        area = args[0]
        factors = [(area // w, w) for w in range(1, isqrt(area) + 1) if area % w == 0]
        assert list(min(factors, key=lambda pair: pair[0] - pair[1])) == expected


def test_advanced_base_prerequisites_have_existing_preparation():
    catalog = get_catalog()
    problem = catalog['leetcode-483']
    assert problem.difficulty >= 8 and problem.prerequisites == ['math', 'binary-search']
    for topic in problem.prerequisites:
        assert any(p.difficulty < 8 and topic in p.topics for p in catalog.values())
