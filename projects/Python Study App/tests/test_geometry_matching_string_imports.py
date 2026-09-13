from copy import deepcopy
from itertools import combinations, combinations_with_replacement, product
import random
import string

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_041 import BATCH
from code_practice.validation import compare, run_source


def reference(pid):
    namespace = {}
    exec(BATCH[pid]['reference'], namespace)
    return namespace[BATCH[pid]['name']]


@pytest.mark.parametrize('pid', BATCH)
def test_batch_41_reference_hidden_tests_and_logical_counterexamples(pid):
    problem = get_catalog()[f'leetcode-{pid}']
    assert problem.status == 'approved' and len(problem.hints) == 4 and problem.editorial
    assert sum(t.visible for t in problem.tests) == 2
    assert sum(not t.visible for t in problem.tests) >= 12
    assert all(run_source(problem.reference_solution, problem, t) == (True, None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        outcomes = [run_source(wrong, problem, t) for t in problem.tests]
        assert (False, None) in outcomes and all(error is None for _, error in outcomes)


@pytest.mark.parametrize('pid', BATCH)
def test_batch_41_all_fixtures_obey_source_domains(pid):
    spec = BATCH[pid]
    rng = random.Random(4047 + pid)
    inputs = ([a for a, _ in spec['examples']] + spec['boundaries']
              + [a for a, _ in spec['stress']] + [spec['generator'](rng) for _ in range(500)])
    for args in inputs:
        if pid == 447:
            assert 1 <= len(args[0]) <= 500
            assert len(set(map(tuple, args[0]))) == len(args[0])
            assert all(len(p) == 2 and all(type(v) is int and abs(v) <= 10000 for v in p) for p in args[0])
        elif pid == 448:
            assert 1 <= len(args[0]) <= 100000 and all(1 <= v <= len(args[0]) for v in args[0])
        elif pid == 452:
            assert 1 <= len(args[0]) <= 100000
            assert all(-2**31 <= a < b <= 2**31-1 for a, b in args[0])
        elif pid in (453, 462):
            nums = args[0]
            assert 1 <= len(nums) <= 100000 and all(abs(v) <= 10**9 for v in nums)
            # Independent lower bounds are achievable: decrement to min, or pair extremes.
            ordered = sorted(nums)
            cost = sum(v-ordered[0] for v in nums) if pid == 453 else sum(
                ordered[-1-i]-ordered[i] for i in range(len(nums)//2))
            assert 0 <= cost <= 2**31-1
        elif pid == 454:
            assert len(args) == 4 and len({len(a) for a in args}) == 1
            assert 1 <= len(args[0]) <= 200 and all(abs(v) <= 2**28 for a in args for v in a)
        elif pid == 455:
            assert 1 <= len(args[0]) <= 30000 and len(args[1]) <= 30000
            assert all(1 <= v <= 2**31-1 for a in args for v in a)
        elif pid == 456:
            assert 1 <= len(args[0]) <= 200000 and all(abs(v) <= 10**9 for v in args[0])
        elif pid == 461:
            assert len(args) == 2 and all(0 <= v <= 2**31-1 for v in args)
        elif pid in (459, 467):
            assert 1 <= len(args[0]) <= (10000 if pid == 459 else 100000)
            assert set(args[0]) <= set(string.ascii_lowercase)
        else:
            assert set(args[0]) <= set(string.ascii_letters + string.digits + '.:')


@pytest.mark.parametrize('pid', BATCH)
def test_batch_41_source_scale_expected_results(pid):
    solve = reference(pid)
    for args, expected in BATCH[pid]['stress']:
        assert compare(solve(*deepcopy(args)), expected, BATCH[pid].get('comparator', 'exact'))


def test_boomerangs_exhaust_all_nonempty_subsets_of_nine_point_grid():
    solve = reference(447)
    grid = list(product(range(-1, 2), repeat=2))
    for size in range(1, 10):
        for points in combinations(grid, size):
            assert solve(points) == BATCH[447]['oracle']([points])


def test_missing_values_exhaust_duplicate_marking_and_order_flexibility():
    solve = reference(448)
    for n in range(1, 7):
        for values in product(range(1, n+1), repeat=n):
            assert sorted(solve(list(values))) == BATCH[448]['oracle']([values])
    assert compare([6, 5], [5, 6], 'unordered')
    assert not compare([5, 5, 6], [5, 6], 'unordered')
    assert not compare([5], [5, 6], 'unordered')


def test_balloon_arrows_exhaust_closed_endpoint_hitting_sets():
    solve = reference(452)
    possible = list(combinations(range(5), 2))
    for size in range(1, 6):
        for intervals in combinations_with_replacement(possible, size):
            assert solve(intervals) == BATCH[452]['oracle']([intervals])


def test_array_move_operations_have_distinct_optima():
    many, single = reference(453), reference(462)
    assert many([-1, 1, 3]) == 6 and single([-1, 1, 3]) == 4
    for size in range(1, 6):
        for values in product(range(4), repeat=size):
            assert many(values) == BATCH[453]['oracle']([values])
            assert single(values) == BATCH[462]['oracle']([values])


def test_four_array_index_tuples_exhaust_repeated_and_signed_pairs():
    solve = reference(454)
    for size in (1, 2):
        arrays = list(product(range(-1, 2), repeat=size))
        for args in product(arrays, repeat=4):
            assert solve(*args) == BATCH[454]['oracle'](args)


def test_cookie_greedy_matches_general_bipartite_matching():
    solve = reference(455)
    multisets = [v for n in range(5) for v in combinations_with_replacement(range(1, 5), n)]
    for needs in multisets[1:]:
        for cookies in multisets:
            assert solve(needs[::-1], cookies) == BATCH[455]['oracle']([needs, cookies])


def test_strict_nonadjacent_132_pattern_exhaust_ternary_arrays():
    solve = reference(456)
    for size in range(1, 9):
        for nums in product((-1, 0, 1), repeat=size):
            assert solve(nums) == BATCH[456]['oracle']([nums])


def test_string_borders_must_be_complete_repetitions():
    solve = reference(459)
    for size in range(1, 13):
        for chars in product('ab', repeat=size):
            text = ''.join(chars)
            assert solve(text) == BATCH[459]['oracle']([text])


def test_hamming_exhaust_byte_pairs_and_all_31_bit_boundaries():
    solve = reference(461)
    for x, y in product(range(256), repeat=2):
        assert solve(x, y) == BATCH[461]['oracle']([x, y])
    for bit in range(31):
        assert solve(0, 1 << bit) == 1
        assert solve((1 << bit)-1, 1 << bit) == bit+1
        assert solve(2**31-1, 1 << bit) == 30


def test_cyclic_substrings_count_values_not_occurrences():
    solve = reference(467)
    for size in range(1, 6):
        for chars in product('abcxyz', repeat=size):
            text = ''.join(chars)
            assert solve(text) == BATCH[467]['oracle']([text])
    for start in range(26):
        for size in range(1, 121):
            text = ''.join(string.ascii_lowercase[(start+i) % 26] for i in range(size))
            assert solve(text) == (size*(size+1)//2 if size <= 26 else 26*size-325)


def test_ip_grammar_exhaust_decimal_ranges_and_hex_group_boundaries():
    solve = reference(468)
    for position in range(4):
        for number in range(301):
            for width in range(1, 5):
                groups = ['1']*4
                groups[position] = str(number).zfill(width)
                text = '.'.join(groups)
                assert solve(text) == BATCH[468]['oracle']([text])
    for position in range(8):
        for char in '0123456789abcdefABCDEFgGzZ':
            for width in range(6):
                groups = ['0']*8
                groups[position] = char*width
                text = ':'.join(groups)
                assert solve(text) == BATCH[468]['oracle']([text])
    for text in ('::', '::1', '2001:db8::1', '1:2:3:4:5:6:192.168.0.1'):
        assert solve(text) == 'Neither'
