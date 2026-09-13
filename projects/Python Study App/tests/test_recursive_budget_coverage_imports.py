from copy import deepcopy
from itertools import combinations, combinations_with_replacement, product
import random
import string

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_042 import BATCH, square_oracle
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.validation import compare, run_source


def reference(pid):
    namespace = {}
    exec(BATCH[pid]['reference'], namespace)
    return namespace[BATCH[pid]['name']]


@pytest.mark.parametrize('pid', BATCH)
def test_batch_42_reference_and_logical_wrong_algorithms(pid):
    problem = get_catalog()[f'leetcode-{pid}']
    assert problem.status == 'approved' and len(problem.hints) == 4 and problem.editorial
    assert sum(t.visible for t in problem.tests) == 2
    assert sum(not t.visible for t in problem.tests) >= 12
    assert all(run_source(problem.reference_solution, problem, t) == (True, None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        results = [run_source(wrong, problem, t) for t in problem.tests]
        assert (False, None) in results and all(error is None for _, error in results)


@pytest.mark.parametrize('pid', BATCH)
def test_batch_42_fixture_and_generated_source_domains(pid):
    spec = BATCH[pid]
    rng = random.Random(4047+pid)
    inputs = ([a for a, _ in spec['examples']] + spec['boundaries']
              + [a for a, _ in spec['stress']] + [spec['generator'](rng) for _ in range(500)])
    for args in inputs:
        if pid == 472:
            words = args[0]
            assert 1 <= len(words) <= 10000 and len(words) == len(set(words))
            assert sum(map(len, words)) <= 100000
            assert all(1 <= len(w) <= 30 and set(w) <= set(string.ascii_lowercase) for w in words)
        elif pid == 473:
            assert 1 <= len(args[0]) <= 15 and all(1 <= v <= 10**8 for v in args[0])
        elif pid == 474:
            words, m, n = args
            assert 1 <= len(words) <= 600 and 1 <= m <= 100 and 1 <= n <= 100
            assert all(1 <= len(w) <= 100 and set(w) <= {'0','1'} for w in words)
        else:
            assert all(1 <= len(a) <= 30000 and all(1 <= v <= 10**9 for v in a) for a in args)


@pytest.mark.parametrize('pid', BATCH)
def test_batch_42_maximum_size_cases(pid):
    solve = reference(pid)
    for args, expected in BATCH[pid]['stress']:
        assert compare(solve(*deepcopy(args)), expected, BATCH[pid].get('comparator','exact'))


def test_concatenated_dictionary_exhaust_small_vocabularies_and_piece_reuse():
    solve = reference(472)
    vocabulary = ['a','b','aa','ab','ba','bb','aaa','aba','bab','bbb']
    for count in range(1, len(vocabulary)+1):
        for words in combinations(vocabulary, count):
            assert sorted(solve(words)) == sorted(BATCH[472]['oracle']([words]))
    assert solve(['a','aaaaaaa']) == ['aaaaaaa']
    assert solve(['abc']) == []
    expected = ['catdog','dogcat']
    assert compare(expected[::-1], expected, 'unordered')
    assert not compare(expected+['catdog'], expected, 'unordered')
    assert not compare(['catdog'], expected, 'unordered')


def literal_four_bucket_partition(sticks):
    if sum(sticks) % 4:
        return False
    target = sum(sticks)//4
    # Fixing the first stick on side zero removes only a naming symmetry.
    for assignment in product(range(4), repeat=len(sticks)-1):
        sides = [sticks[0],0,0,0]
        for stick, side in zip(sticks[1:], assignment):
            sides[side] += stick
        if sides == [target]*4:
            return True
    return False


def test_square_subset_oracle_against_literal_assignments_and_reference():
    solve = reference(473)
    for size in range(1, 8):
        for sticks in combinations_with_replacement(range(1, 5), size):
            answer = literal_four_bucket_partition(sticks)
            assert square_oracle([sticks]) == answer
            assert solve(sticks) == answer
    example = [1,1,2,2,2,2,3,3,6,6]
    assert solve(example) and square_oracle([example])
    wrong = {}
    exec(BATCH[473]['wrong'][1], wrong)
    assert not wrong['make_square'](example)
    # The valid sides are 6+1, 6+1, 3+2+2, 3+2+2.
    for scale in (1, 7, 10**7):
        assert solve([scale*v for v in example])


def test_two_budgets_exhaust_duplicate_strings_and_zero_cost_resources():
    solve = reference(474)
    vocabulary = ('0','1','01','00','11')
    for size in range(1, 6):
        for words in combinations_with_replacement(vocabulary, size):
            for m, n in product(range(1, 5), repeat=2):
                assert solve(words,m,n) == BATCH[474]['oracle']([words,m,n])
    assert solve(['0'], 100, 100) == 1
    assert solve(['0','0','1'], 2, 1) == 3
    assert solve(['00','11'], 1, 1) == 0


def test_heater_radius_exhaust_unsorted_and_repeated_positions_with_minimality():
    solve = reference(475)
    arrays = [a for size in range(1, 4) for a in combinations_with_replacement(range(1, 7), size)]
    for houses, heaters in product(arrays, repeat=2):
        radius = solve(houses[::-1], heaters[::-1])
        assert radius == BATCH[475]['oracle']([houses,heaters])
        assert all(any(abs(h-t) <= radius for t in heaters) for h in houses)
        if radius:
            assert any(all(abs(h-t) > radius-1 for t in heaters) for h in houses)


def test_new_recursion_and_search_topics_keep_review_boosts_and_hard_prerequisites():
    catalog = get_catalog()
    assert review_focus_boost(catalog['leetcode-472']) >= 50
    assert review_focus_boost(catalog['leetcode-473']) >= 50
    assert review_focus_boost(catalog['leetcode-475']) >= 60
    hard = catalog['leetcode-472']
    assert hard.difficulty >= 8 and hard.prerequisites
    assert prerequisites_met(hard, {topic:70 for topic in hard.prerequisites})
    assert not prerequisites_met(hard, {topic:69 for topic in hard.prerequisites})
