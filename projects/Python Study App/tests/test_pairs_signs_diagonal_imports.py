from collections import Counter
from copy import deepcopy
from itertools import combinations_with_replacement, permutations, product
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_047 import BATCH, OVERLAP_SPECS
from code_practice.learning import review_focus_boost
from code_practice.validation import run_source


def reference(pid):
    namespace = {}
    spec=(BATCH | OVERLAP_SPECS)[pid]
    exec(spec['reference'], namespace)
    return namespace[spec['name']]


@pytest.mark.parametrize('pid', BATCH)
def test_batch_47_references_and_wrong_algorithms(pid):
    problem = get_catalog()[f'leetcode-{pid}']
    assert problem.status == 'approved' and len(problem.hints) == 4 and problem.editorial
    assert sum(t.visible for t in problem.tests) == 2
    assert sum(not t.visible for t in problem.tests) >= 12
    assert all(run_source(problem.reference_solution, problem, t) == (True, None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        outcomes = [run_source(wrong, problem, t) for t in problem.tests]
        assert (False, None) in outcomes and all(error is None for _, error in outcomes)


@pytest.mark.parametrize('pid', BATCH | OVERLAP_SPECS)
def test_batch_47_source_domains(pid):
    spec = (BATCH | OVERLAP_SPECS)[pid]
    rng = random.Random(4047 + pid)
    inputs = ([a for a, _ in spec['examples']] + spec['boundaries']
              + [a for a, _ in spec['stress']] + [spec['generator'](rng) for _ in range(500)])
    for args in inputs:
        value = args[0]
        if pid == 485:
            assert 1 <= len(value) <= 100000 and all(type(x) is int and x in (0, 1) for x in value)
        elif pid == 493:
            assert 1 <= len(value) <= 50000 and all(type(x) is int and -2**31 <= x < 2**31 for x in value)
        elif pid == 494:
            assert 1 <= len(value) <= 20 and sum(value) <= 1000
            assert all(type(x) is int and 0 <= x <= 1000 for x in value)
            assert type(args[1]) is int and -1000 <= args[1] <= 1000
        elif pid == 495:
            assert 1 <= len(value) <= 10000 and value == sorted(value)
            assert all(type(x) is int and 0 <= x <= 10**7 for x in value)
            assert type(args[1]) is int and 0 <= args[1] <= 10**7
        elif pid == 496:
            queries, nums = args
            assert 1 <= len(queries) <= len(nums) <= 1000
            assert len(queries) == len(set(queries)) and len(nums) == len(set(nums))
            assert set(queries) <= set(nums)
            assert all(type(x) is int and 0 <= x <= 10000 for x in queries + nums)
        else:
            assert 1 <= len(value) <= 10000 and 1 <= len(value[0]) <= 10000
            assert len(value) * len(value[0]) <= 10000
            assert all(len(row) == len(value[0]) for row in value)
            assert all(type(x) is int and -100000 <= x <= 100000 for row in value for x in row)


@pytest.mark.parametrize('pid', BATCH)
def test_batch_47_maximum_cases_preserve_input(pid):
    solve = reference(pid)
    for args, expected in BATCH[pid]['stress']:
        copied = deepcopy(args)
        assert solve(*copied) == expected
        assert copied == args


def test_ones_exhaustive_and_distinct_from_one_flip():
    solve = reference(485)
    for length in range(1, 11):
        for values in product((0, 1), repeat=length):
            nums = list(values)
            assert solve(nums) == BATCH[485]['oracle']([nums])
    assert solve([1, 0, 1]) == 1  # The one-flip exercise returns 3.
    assert solve([1, 1, 0, 1]) == 2


def test_reverse_pairs_exhaustive_signed_strictness_and_original_order():
    solve = reference(493)
    for length in range(1, 7):
        for values in product(range(-2, 3), repeat=length):
            nums = list(values)
            assert solve(nums) == BATCH[493]['oracle']([nums])
    rng = random.Random(493)
    for _ in range(500):
        nums = [rng.randint(-2**31, 2**31 - 1) for _ in range(rng.randint(1, 25))]
        assert solve(nums) == BATCH[493]['oracle']([nums])
    assert solve([2, 1]) == 0 and solve([3, 1]) == 1
    assert solve([-1, -1]) == 1 and solve([1, 3]) == 0
    assert solve([-2**31, -2**31]) == 1


def test_reverse_pair_large_expected_values_independently():
    for args, expected in BATCH[493]['stress']:
        nums = args[0]
        if len(set(nums)) < 3:
            seen = Counter()
            total = 0
            for value in nums:
                total += sum(count for earlier, count in seen.items() if earlier > 2 * value)
                seen[value] += 1
            assert total == expected
        else:
            assert nums == list(range(len(nums), 0, -1))
            n = len(nums)
            k = (n - 1) // 2
            assert expected == k * (n - k - 1)


def expression_counts(nums):
    counts = {0: 1}
    for value in nums:
        updated = Counter()
        for total, count in counts.items():
            updated[total + value] += count
            updated[total - value] += count
        counts = updated
    return counts


def test_target_signs_exhaustive_position_counts_and_zero_choices():
    solve = reference(494)
    for length in range(1, 7):
        for values in product(range(3), repeat=length):
            nums = list(values)
            counts = Counter(sum(s * n for s, n in zip(signs, nums))
                             for signs in product((-1, 1), repeat=length))
            for target in range(-sum(nums) - 1, sum(nums) + 2):
                assert solve(nums, target) == counts[target]
    for args, expected in BATCH[494]['stress']:
        nums, target = args
        assert expression_counts(nums).get(target, 0) == expected
    assert solve([0] * 20, 0) == 1048576
    assert solve([0, 1], 1) == 2 and solve([1, 1], 0) == 2


def test_poison_exhaustive_inclusive_seconds_and_large_event_sweep():
    solve = reference(495)
    for length in range(1, 7):
        for times in combinations_with_replacement(range(5), length):
            for duration in range(7):
                args = [list(times), duration]
                assert solve(*args) == OVERLAP_SPECS[495]['oracle'](args)
    for args, expected in OVERLAP_SPECS[495]['stress']:
        times, duration = args
        events = Counter()
        for start in times:
            events[start] += 1
            events[start + duration] -= 1
        covered = active = previous = 0
        for point, change in sorted(events.items()):
            if active:
                covered += point - previous
            active += change
            previous = point
        assert covered == expected


def test_next_greater_exhaustive_first_position_and_query_order():
    solve = reference(496)
    for length in range(1, 8):
        for ordering in permutations(range(length)):
            nums = list(ordering)
            queries = list(reversed(nums))
            assert solve(queries, nums) == OVERLAP_SPECS[496]['oracle']([queries, nums])
    assert solve([1], [1, 5, 3]) == [5]
    assert solve([3], [3, 1, 4]) == [4]
    assert solve([4, 1, 2], [1, 3, 4, 2]) == [-1, 3, -1]


def test_diagonal_rectangular_coordinates_and_duplicate_values():
    solve = reference(498)
    for rows in range(1, 21):
        for cols in range(1, 21):
            matrix = [[r * cols + c for c in range(cols)] for r in range(rows)]
            actual = solve(matrix)
            assert actual == BATCH[498]['oracle']([matrix])
            assert sorted(actual) == list(range(rows * cols))
    for rows, cols in ((1, 8), (2, 4), (4, 2), (8, 1), (2, 3), (3, 2)):
        for values in product((0, 1), repeat=rows * cols):
            matrix = [list(values[r * cols:(r + 1) * cols]) for r in range(rows)]
            assert solve(matrix) == BATCH[498]['oracle']([matrix])


def test_new_recursion_priorities_and_advanced_preparation():
    catalog = get_catalog()
    for pid in (493, 494):
        assert review_focus_boost(catalog[f'leetcode-{pid}']) >= 50
    problem = catalog['leetcode-493']
    assert problem.difficulty >= 8 and problem.prerequisites
    for topic in problem.prerequisites:
        assert any(p.difficulty < 8 and topic in p.topics for p in catalog.values())
