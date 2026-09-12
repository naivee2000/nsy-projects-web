from itertools import combinations, product
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_028 import (
    BATCH, BALLOONS, SUPER_UGLY, SMALLER, LETTERS, BUILDINGS, PRIMES_100,
    balloons_oracle, super_ugly_oracle, smaller_oracle, letters_oracle, buildings_oracle,
)
from code_practice.validation import run_source


def function(source, name):
    namespace = {}
    exec(compile(source, f'<{name}>', 'exec'), namespace)
    return namespace[name]


def test_batch_28_published_references_and_algorithmic_wrong_answers():
    for source_id in BATCH:
        problem = get_catalog()[f'leetcode-{source_id}']
        assert problem.status == 'approved'
        assert sum(case.visible for case in problem.tests) >= 2
        assert sum(not case.visible for case in problem.tests) >= 12
        assert all(case.explanation for case in problem.tests if case.visible)
        assert all(run_source(problem.reference_solution, problem, case)[0]
                   for case in problem.tests)
        for wrong in problem.known_wrong_solutions:
            assert any(run_source(wrong, problem, case) == (False, None)
                       for case in problem.tests)


def test_interval_dp_matches_every_small_balloon_array():
    solve = function(BALLOONS, 'max_burst_coins')
    for length in range(1, 6):
        for values in map(list, product(range(4), repeat=length)):
            assert solve(values) == balloons_oracle([values])


def test_super_ugly_merging_handles_prime_subsets_and_ties():
    solve = function(SUPER_UGLY, 'nth_super_ugly_number')
    for size in range(1, 6):
        for primes in combinations((2, 3, 5, 7, 11), size):
            for n in range(1, 21):
                # The source guarantees a 32-bit result. Check only that domain.
                expected = super_ugly_oracle([n, primes])
                if expected < 2**31:
                    assert solve(n, primes) == expected


def test_super_ugly_maximum_fixture_has_independent_factorization_evidence():
    assert len(PRIMES_100) == 100
    count, last = 0, None
    for value in range(1, 284446):
        remainder = value
        for prime in PRIMES_100:
            while remainder % prime == 0:
                remainder //= prime
            if remainder == 1:
                break
        if remainder == 1:
            count += 1
            last = value
    assert (count, last) == (100000, 284445)


def test_fenwick_counts_match_all_short_signed_arrays_with_duplicates():
    solve = function(SMALLER, 'count_smaller_after_self')
    for length in range(1, 8):
        for values in map(list, product((-1, 0, 1), repeat=length)):
            assert solve(values) == smaller_oracle([values])


def test_greedy_subsequence_matches_all_short_three_letter_strings():
    solve = function(LETTERS, 'remove_duplicate_letters')
    for length in range(1, 8):
        for text in map(''.join, product('abc', repeat=length)):
            assert solve(text) == letters_oracle([text])


def test_building_search_matches_every_two_by_three_grid_with_a_building():
    solve = function(BUILDINGS, 'shortest_distance_to_buildings')
    for cells in product((0, 1, 2), repeat=6):
        if 1 not in cells:
            continue
        grid = [list(cells[:3]), list(cells[3:])]
        assert solve(grid) == buildings_oracle([grid])


def test_vertical_traversal_preserves_row_before_branch_and_not_value_order():
    problem = get_catalog()['leetcode-314']
    tie_case = next(case for case in problem.tests
                    if case.arguments == [[1,2,3,4,10,9,11]])
    assert tie_case.expected == [[4],[2],[1,10,9],[3],[11]]
    deep_case = next(case for case in problem.tests
                    if case.arguments == [[1,2,3,4,10,9,11,None,5,None,None,None,None,None,None,None,6]])
    assert deep_case.expected == [[4],[2,5],[1,10,9,6],[3],[11]]
    assert run_source(problem.known_wrong_solutions[0], problem, deep_case) == (False, None)
    assert run_source(problem.known_wrong_solutions[1], problem, tie_case) == (False, None)


def test_batch_28_generated_and_deterministic_inputs_obey_source_constraints():
    for source_id, spec in BATCH.items():
        rng = random.Random(4047 + source_id)
        inputs = ([args for args, _ in spec['examples']] + spec['boundaries']
                  + [args for args, _ in spec['stress']]
                  + [spec['generator'](rng) for _ in range(500)])
        for args in inputs:
            if source_id == 312:
                assert 1 <= len(args[0]) <= 300
                assert all(type(value) is int and 0 <= value <= 100 for value in args[0])
            elif source_id == 313:
                n, primes = args
                assert 1 <= n <= 100000 and 1 <= len(primes) <= 100
                assert primes == sorted(set(primes))
                assert all(2 <= p <= 1000 and all(p % d for d in range(2, int(p**.5)+1)) for p in primes)
                if n < 1000:
                    assert super_ugly_oracle(args) < 2**31
            elif source_id == 314:
                values = [v for v in args[0] if v is not None]
                assert len(values) <= 100 and all(-100 <= v <= 100 for v in values)
            elif source_id == 315:
                assert 1 <= len(args[0]) <= 100000
                assert all(-10000 <= value <= 10000 for value in args[0])
            elif source_id == 316:
                assert 1 <= len(args[0]) <= 10000 and set(args[0]) <= set('abcdefghijklmnopqrstuvwxyz')
            elif source_id == 317:
                grid = args[0]
                assert 1 <= len(grid) <= 50 and 1 <= len(grid[0]) <= 50
                assert all(len(row) == len(grid[0]) and set(row) <= {0, 1, 2} for row in grid)
                assert any(1 in row for row in grid)
