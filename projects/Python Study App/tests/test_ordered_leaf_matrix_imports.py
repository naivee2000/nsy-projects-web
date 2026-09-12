import ast
from functools import lru_cache
from itertools import product
import json
from math import comb
from pathlib import Path
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_002 import positions
from code_practice.import_batch_033 import (
    BATCH, RECTANGLE, LEAVES, SQUARE, ADDITION, POWER, GUESS, WIGGLE, ORDERED_SUM,
    KTH_MATRIX, rectangle_oracle, leaves_oracle, square_oracle, power_oracle,
    guessing_oracle, wiggle_oracle, ordered_sum_oracle, kth_matrix_oracle,
)
from code_practice.schemas import ProblemDefinition
from code_practice.validation import TreeNode, _serialize, compare, run_source


def function(source, name):
    namespace = {}
    exec(compile(source,f'<{name}>','exec'),namespace)
    return namespace[name]


def test_row_comparator_preserves_group_order_and_integer_multiplicities():
    expected = [[1,2,1],[3]]
    assert compare([[2,1,1],[3]],expected,'unordered_rows')
    assert compare([],[],'unordered_rows')
    for wrong in ([[3],[1,1,2]],[[1,2],[3]],[[1,1,2,2],[3]],[[1,1,2]],
                  [[True,1,2],[3]],[[1.0,1,2],[3]],[[[1],1,2],[3]], [1,1,2,3], None):
        assert not compare(wrong,expected,'unordered_rows')
    # The pre-existing fully unordered comparator must NOT grade leaf rounds.
    assert compare([[3],[1,1,2]],expected,'unordered_nested')


@pytest.mark.parametrize('change',['flat','boolean','float','nested','mixed','return_type','adapter'])
def test_schema_rejects_inconsistent_ordered_group_contracts(change):
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root/'catalog_import/candidates/leetcode-366.json').read_text())
    if change == 'flat':
        payload['tests'][0]['expected'] = [1,2,3]
    elif change in {'boolean','float','nested'}:
        payload['tests'][0]['expected'][0][0] = {'boolean':True,'float':1.0,'nested':[1]}[change]
    elif change == 'mixed':
        payload['tests'][0]['comparator'] = 'unordered_nested'
    elif change == 'return_type':
        payload['signature']['returns'] = 'list[int]'
    else:
        payload['signature']['return_adapter'] = 'treenode'
    with pytest.raises(ValueError):
        ProblemDefinition.model_validate(payload)


def test_batch_33_published_references_and_wrong_algorithms():
    for source_id in BATCH:
        problem = get_catalog()[f'leetcode-{source_id}']
        assert problem.status == 'approved' and len(problem.hints)==4 and problem.editorial
        assert sum(t.visible for t in problem.tests)>=2 and sum(not t.visible for t in problem.tests)>=12
        assert all(run_source(problem.reference_solution,problem,t)[0] for t in problem.tests)
        for wrong in problem.known_wrong_solutions:
            assert any(run_source(wrong,problem,t)==(False,None) for t in problem.tests)
    leaf = get_catalog()['leetcode-366']
    assert 'class TreeNode:' in leaf.starter_code and 'recursion' in leaf.topics
    assert {case.comparator for case in leaf.tests} == {'unordered_rows'}
    assert 'ordered sequences' in get_catalog()['leetcode-377'].statement


def test_rectangle_fenwick_queries_match_all_two_by_three_ternary_grids():
    solve = function(RECTANGLE,'max_bounded_rectangle')
    for cells in product((-1,0,1),repeat=6):
        matrix = [list(cells[:3]),list(cells[3:])]
        for k in range(-4,5):
            try:
                expected = rectangle_oracle([matrix,k])
            except ValueError:
                continue
            assert solve(matrix,k) == expected
            assert solve(list(map(list,zip(*matrix))),k) == expected
    assert solve([[-5]],-4) == -5  # Empty rectangles are forbidden.


@lru_cache(None)
def shapes(n):
    if n == 0:
        return (None,)
    return tuple((left,right) for size in range(n)
                 for left in shapes(size) for right in shapes(n-1-size))


def test_recursive_leaf_heights_match_simultaneous_pruning_on_all_small_trees():
    solve = function(LEAVES,'leaf_removal_rounds')
    def build(shape,values):
        if shape is None:
            return None
        return TreeNode(next(values),build(shape[0],values),build(shape[1],values))
    for n in range(1,6):
        for shape in shapes(n):
            for values in product((0,1),repeat=n):
                root = build(shape,iter(values))
                expected = leaves_oracle([_serialize(root,'treenode')])
                actual = solve(root)
                assert compare(actual,expected,'unordered_rows')
                assert sum(map(len,actual)) == n


def test_square_boundaries_and_reference_source_restrictions():
    square = function(SQUARE,'is_perfect_square')
    for root in range(1,46341):
        for num in (root*root-1,root*root,root*root+1):
            if num >= 1:
                assert square(num) == square_oracle([num])
    square_ast = ast.parse(SQUARE)
    assert not any(isinstance(node,ast.Pow) for node in ast.walk(square_ast))
    assert not any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                   and node.func.id in {'sqrt','isqrt','pow'} for node in ast.walk(square_ast))
    assert not any(isinstance(node,(ast.Add,ast.Sub,ast.UAdd,ast.USub)) for node in ast.walk(ast.parse(ADDITION)))


def test_signed_carry_propagation_exhausts_small_signed_pairs():
    solve = function(ADDITION,'sum_without_arithmetic')
    for a,b in product(range(-32,33),repeat=2):
        assert solve(a,b) == a+b


def test_decimal_power_handles_non_coprime_bases_and_full_length_exponents():
    solve = function(POWER,'super_pow')
    for a in (1,2,7,191,1337,1338,2147483647):
        for exponent in range(1,100):
            digits = list(map(int,str(exponent)))
            assert solve(a,digits) == power_oracle([a,digits])
    for args,expected in BATCH[372]['stress']:
        assert power_oracle(args) == expected == solve(*args)
    assert solve(7,[1,1,4,0]) != pow(7,0,1337)


def test_guessing_budget_matches_enumerated_strategies_and_large_top_down_check():
    solve = function(GUESS,'minimum_guess_budget')
    for n in range(1,11):
        assert solve(n) == guessing_oracle([n])
    @lru_cache(None)
    def adversarial_budget(low,high):
        if low >= high:
            return 0
        best = float('inf')
        for first in range(low,high+1):
            left = adversarial_budget(low,first-1)
            right = adversarial_budget(first+1,high)
            best = min(best,first+max(left,right))
        return best
    for args,expected in BATCH[375]['stress']:
        assert adversarial_budget(1,args[0]) == expected == solve(*args)


def test_wiggle_greedy_matches_every_short_ternary_sequence():
    solve = function(WIGGLE,'longest_wiggle_subsequence')
    for length in range(1,7):
        for nums in product(range(3),repeat=length):
            assert solve(nums) == wiggle_oracle([nums])


def test_ordered_sum_counts_do_not_collapse_permutations_or_exceed_source_limit():
    solve = function(ORDERED_SUM,'count_ordered_sums')
    for mask in range(1,1 << 5):
        nums = [i+1 for i in range(5) if mask & (1 << i)]
        for target in range(1,13):
            assert solve(nums,target) == ordered_sum_oracle([nums,target])
    assert solve([1,2],3) == 3  # [1,1,1], [1,2], [2,1].
    # Count positions of twos in every possible-length sequence independently.
    assert sum(comb(45-twos,twos) for twos in range(23)) == 1836311903
    for args,expected in BATCH[377]['stress']:
        assert 0 <= expected < 2**31 and solve(*args) == expected


def test_matrix_rank_counts_duplicates_not_distinct_values_or_row_major_order():
    solve = function(KTH_MATRIX,'kth_smallest_matrix')
    for cells in product(range(-2,3),repeat=4):
        a,b,c,d = cells
        if a<=b<=d and a<=c<=d:
            matrix = [[a,b],[c,d]]
            for k in range(1,5):
                assert solve(matrix,k) == kth_matrix_oracle([matrix,k])
    for args,expected in BATCH[378]['stress']:
        assert kth_matrix_oracle(args) == expected


def test_batch_33_inputs_follow_source_contracts():
    for source_id,spec in BATCH.items():
        rng = random.Random(4047+source_id)
        inputs = ([args for args,_ in spec['examples']] + spec['boundaries']
                  + [args for args,_ in spec['stress']]
                  + [spec['generator'](rng) for _ in range(500)])
        for args in inputs:
            if source_id == 363:
                matrix,k = args
                assert 1 <= len(matrix)<=100 and 1 <= len(matrix[0])<=100 and -100000 <= k <= 100000
                assert all(len(row)==len(matrix[0]) and all(-100<=x<=100 for x in row) for row in matrix)
                if len(matrix)*len(matrix[0])<=16:
                    assert rectangle_oracle(args)<=k
            elif source_id == 366:
                values = positions(args[0]).values()
                assert 1 <= len(values)<=100 and all(-100<=x<=100 for x in values)
            elif source_id == 367:
                assert 1 <= args[0] < 2**31
            elif source_id == 371:
                assert all(-1000<=x<=1000 for x in args)
            elif source_id == 372:
                a,b = args
                assert 1<=a<2**31 and 1<=len(b)<=2000 and b[0]!=0 and all(0<=d<=9 for d in b)
            elif source_id == 375:
                assert 1<=args[0]<=200
            elif source_id == 376:
                assert 1<=len(args[0])<=1000 and all(0<=x<=1000 for x in args[0])
            elif source_id == 377:
                nums,target = args
                assert 1<=len(nums)<=200 and len(set(nums))==len(nums) and all(1<=x<=1000 for x in nums)
                assert 1<=target<=1000
            elif source_id == 378:
                matrix,k = args
                n = len(matrix)
                assert 1<=n<=300 and 1<=k<=n*n
                assert all(len(row)==n and row==sorted(row) and all(-10**9<=x<=10**9 for x in row) for row in matrix)
                assert all(list(column)==sorted(column) for column in zip(*matrix))
