from itertools import combinations_with_replacement, permutations, product
import json
import math
from pathlib import Path
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_037 import (
    BATCH, four_oracle, concat_oracle, permutation_oracle, scramble_oracle,
    water_oracle, split_oracle, slices_oracle, third_oracle, bowl,
)
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.reconcile_overlaps import check_unique_permutations
from code_practice.schemas import TestCase as Case
from code_practice.validation import compare, run_source


def reference(pid):
    namespace = {}
    exec(BATCH[pid]['reference'],namespace)
    return namespace[BATCH[pid]['name']]


def test_batch_37_approved_references_reject_two_logical_errors_and_keep_study_gates():
    catalog = get_catalog()
    for pid in BATCH:
        problem = catalog[f'leetcode-{pid}']
        assert problem.status=='approved' and len(problem.hints)==4 and problem.editorial
        assert sum(t.visible for t in problem.tests)==2
        assert sum(not t.visible for t in problem.tests)>=12
        assert all(run_source(problem.reference_solution,problem,t)==(True,None) for t in problem.tests)
        for wrong in problem.known_wrong_solutions:
            results = [run_source(wrong,problem,t) for t in problem.tests]
            assert (False,None) in results
            assert all(error is None for _,error in results)
        if problem.difficulty>=8:
            assert not prerequisites_met(problem,{p:69 for p in problem.prerequisites})
            assert prerequisites_met(problem,{p:70 for p in problem.prerequisites})
    for pid in (47,87,410):
        assert review_focus_boost(catalog[f'leetcode-{pid}'])>0


def test_batch_37_every_fixture_preserves_full_source_contract():
    for pid,spec in BATCH.items():
        rng = random.Random(4047+pid)
        cases = [a for a,_ in spec['examples']] + spec['boundaries']
        cases += [a for a,_ in spec['stress']] + [spec['generator'](rng) for _ in range(500)]
        for args in cases:
            if pid==18:
                nums,target = args
                assert 1<=len(nums)<=200 and -10**9<=target<=10**9
                assert all(-10**9<=v<=10**9 for v in nums)
            elif pid==30:
                text,words = args
                assert 1<=len(text)<=10000 and 1<=len(words)<=5000
                assert 1<=len(words[0])<=30 and all(len(w)==len(words[0]) for w in words)
                assert set(text+''.join(words))<=set('abcdefghijklmnopqrstuvwxyz')
            elif pid==47:
                assert 1<=len(args[0])<=8 and all(-10<=v<=10 for v in args[0])
            elif pid==87:
                assert 1<=len(args[0])==len(args[1])<=30
                assert set(''.join(args))<=set('abcdefghijklmnopqrstuvwxyz')
            elif pid==407:
                grid = args[0]
                assert 1<=len(grid)<=200 and 1<=len(grid[0])<=200
                assert all(len(row)==len(grid[0]) and all(0<=v<=20000 for v in row) for row in grid)
            elif pid==410:
                nums,k = args
                assert 1<=len(nums)<=1000 and 1<=k<=min(50,len(nums))
                assert all(0<=v<=10**6 for v in nums)
            elif pid==413:
                assert 1<=len(args[0])<=5000 and all(-1000<=v<=1000 for v in args[0])
            else:
                assert 1<=len(args[0])<=10000 and all(-2**31<=v<=2**31-1 for v in args[0])


def test_four_sum_exhausts_short_multisets_and_preserves_multiplicity():
    solve = reference(18)
    for length in range(1,9):
        for values in combinations_with_replacement(range(-2,3),length):
            for target in range(-8,9):
                actual = solve(list(values),target)
                assert compare(actual,four_oracle([values,target]),'unordered_nested')
                assert all(len(row)==4 and sum(row)==target for row in actual)
                assert len(actual)==len({tuple(sorted(row)) for row in actual})
    for args,expected in BATCH[18]['stress']:
        assert solve(*args)==expected


def test_word_windows_exhaust_short_binary_text_and_word_multisets():
    solve = reference(30)
    for width in (1,2):
        vocabulary = [''.join(row) for row in product('ab',repeat=width)]
        for word_count in range(1,4):
            for words in combinations_with_replacement(vocabulary,word_count):
                for length in range(1,8):
                    for chars in product('ab',repeat=length):
                        text = ''.join(chars)
                        assert sorted(solve(text,list(words)))==concat_oracle([text,words])
    assert sorted(solve('aaaa',['aa']))==[0,1,2]
    for args,expected in BATCH[30]['stress']:
        assert sorted(solve(*args))==expected


def test_numeric_permutations_exhaust_multisets_and_count_all_eight_factorial_rows():
    solve = reference(47)
    for length in range(1,9):
        for nums in combinations_with_replacement((-1,0,1),length):
            actual = solve(list(nums))
            assert sorted(actual)==permutation_oracle([nums])
            assert all(sorted(row)==list(nums) for row in actual)
            assert len(actual)==len({tuple(row) for row in actual})
    actual = solve(list(range(8)))
    assert len(actual)==math.factorial(8)==40320
    assert sorted(actual)==permutation_oracle([list(range(8))])


def test_outer_order_is_flexible_but_permutation_rows_and_counts_are_not():
    problem = get_catalog()['leetcode-47']
    case = Case(id='ordered-rows',arguments=[[0,1,2]],expected=permutation_oracle([[0,1,2]]),comparator='unordered')
    correct = f'def unique_number_permutations(nums):\n    return {case.expected[::-1]!r}\n'
    assert run_source(correct,problem,case)==(True,None)
    for output in ([[0,1,2]]*6,case.expected[:-1],case.expected+[case.expected[0]]):
        wrong = f'def unique_number_permutations(nums):\n    return {output!r}\n'
        assert run_source(wrong,problem,case)==(False,None)
    # Four-sum rows are value combinations instead, so reversing each row is valid.
    quad = get_catalog()['leetcode-18']
    case = quad.tests[0]
    reverse = [row[::-1] for row in case.expected[::-1]]
    assert run_source(f'def four_sum(nums,target):\n    return {reverse!r}',quad,case)==(True,None)


def table_scramble(first,second):
    """Bottom-up interval relation, used only for larger independent regressions."""
    n = len(first)
    matches = {(i,j,1) for i in range(n) for j in range(n) if first[i]==second[j]}
    for size in range(2,n+1):
        for i in range(n-size+1):
            for j in range(n-size+1):
                for cut in range(1,size):
                    if (((i,j,cut) in matches and (i+cut,j+cut,size-cut) in matches)
                        or ((i,j+size-cut,cut) in matches and (i+cut,j,size-cut) in matches)):
                        matches.add((i,j,size))
                        break
    return (0,0,n) in matches


def test_scramble_matches_enumerated_languages_not_arbitrary_anagrams():
    solve = reference(87)
    for length in range(1,6):
        texts = [''.join(row) for row in product('ab',repeat=length)]
        for first in texts:
            for second in texts:
                assert solve(first,second)==scramble_oracle([first,second])
    for perm in permutations('abcdef'):
        second = ''.join(perm)
        assert solve('abcdef',second)==scramble_oracle(['abcdef',second])
    assert not solve('abcde','caebd')
    # Same multiset at the full source length: an anagram-only early acceptance
    # must not bypass the interval structure even with a long repeated suffix.
    first,second = 'abcde'+'x'*25,'caebd'+'x'*25
    assert not solve(first,second) and not table_scramble(first,second)
    for args,expected in BATCH[87]['stress']:
        assert solve(*args)==table_scramble(*args)==expected
    rng = random.Random(87)
    for _ in range(25):
        first = ''.join(rng.choice('abcd') for _ in range(20))
        second = ''.join(rng.sample(first,len(first)))
        assert solve(first,second)==table_scramble(first,second)


def test_heap_water_matches_every_ternary_three_by_three_map_and_source_scale():
    solve = reference(407)
    for cells in product(range(3),repeat=9):
        grid = [list(cells[i:i+3]) for i in (0,3,6)]
        # Only the center can retain water on a 3x3 map; corner leaks are diagonal.
        expected = max(0,min(cells[i] for i in (1,3,5,7))-cells[4])
        assert solve(grid)==water_oracle([grid])==expected
    for args,expected in BATCH[407]['stress']:
        before = [row[:] for row in args[0]]
        assert solve(*args)==expected and args[0]==before
    for size in range(3,10):
        assert solve(bowl(size,7))==7*(size-2)**2
        assert solve(bowl(size,7,True))==0


def test_capacity_search_exhausts_nonnegative_arrays_and_exact_part_counts():
    solve = reference(410)
    for length in range(1,8):
        for nums in product(range(3),repeat=length):
            answers = [solve(nums,k) for k in range(1,length+1)]
            assert answers==[split_oracle([nums,k]) for k in range(1,length+1)]
            assert answers==sorted(answers,reverse=True)
            assert answers[0]==sum(nums) and answers[-1]==max(nums)
    for args,expected in BATCH[410]['stress']:
        assert solve(*args)==expected


def test_arithmetic_slices_exhaust_short_arrays_and_full_constant_run():
    solve = reference(413)
    for length in range(1,8):
        for nums in product((-1,0,1),repeat=length):
            assert solve(nums)==slices_oracle([nums])
    for args,expected in BATCH[413]['stress']:
        assert solve(*args)==expected


def test_third_distinct_maximum_exhausts_duplicates_and_integer_boundaries():
    solve = reference(414)
    for length in range(1,8):
        for nums in product((-2**31,-1,0,2**31-1),repeat=length):
            assert solve(nums)==third_oracle([nums])
    for args,expected in BATCH[414]['stress']:
        assert solve(*args)==expected


def test_unique_numeric_permutations_overlap_is_proved_without_a_duplicate_id():
    root = Path(__file__).resolve().parent.parent
    source = next(r for line in (root/'catalog_import/sources.jsonl').read_text().splitlines()
                  if (r:=json.loads(line))['source_id']==46)
    payload = get_catalog()['leetcode-47'].model_dump(mode='json')
    evidence = check_unique_permutations(payload,source)
    assert evidence['oracle_inputs']==500 and evidence['largest_output']==720
    assert 'leetcode-46' not in get_catalog()
    bad = {**payload,'reference_solution': 'def unique_number_permutations(nums):\n    return [sorted(nums)]'}
    with pytest.raises(ValueError,match='sample'):
        check_unique_permutations(bad,source)
    ledger = json.loads((root/'catalog_import/ledger.json').read_text())
    record = next(r for r in ledger['records'] if r['source_id']==46)
    assert record['status']=='overlap' and record['existing_id']=='leetcode-47'
