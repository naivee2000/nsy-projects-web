import ast
from collections import Counter
from itertools import combinations_with_replacement, permutations, product
from functools import cache
import random

from code_practice.catalog import get_catalog
from code_practice.import_batch_048 import BATCH, REFERENCE, collapse_oracle, random_zuma, zuma_oracle, relaxed_deletion_bound
from code_practice.learning import review_focus_boost
from code_practice.validation import run_source


def reference():
    namespace={}
    exec(REFERENCE,namespace)
    return namespace['zuma_min_insertions']


def stable(board):
    return all(color*3 not in board for color in 'RYBGW')


def test_zuma_reference_and_two_plausible_wrong_algorithms():
    problem=get_catalog()['leetcode-488']
    assert problem.status=='approved' and len(problem.hints)==4 and problem.editorial
    assert sum(t.visible for t in problem.tests)==2
    assert sum(not t.visible for t in problem.tests)>=12
    assert all(run_source(problem.reference_solution,problem,t)==(True,None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        outcomes=[run_source(wrong,problem,t) for t in problem.tests]
        assert (False,None) in outcomes and all(error is None for _,error in outcomes)


def test_zuma_fixture_and_generator_domains():
    spec=BATCH[488];rng=random.Random(4535)
    inputs=([a for a,_ in spec['examples']]+spec['boundaries']+[a for a,_ in spec['stress']]
            +[random_zuma(rng) for _ in range(500)])
    for board,hand in inputs:
        assert 1<=len(board)<=16 and 1<=len(hand)<=5
        assert set(board+hand)<=set('RYBGW') and stable(board)
    assert max(len(board) for board,_ in inputs)==16
    assert max(len(hand) for _,hand in inputs)==5


def test_zuma_generator_balances_possible_and_impossible_cases():
    rng=random.Random(4535)
    inputs=[random_zuma(rng) for _ in range(500)]
    results=Counter(zuma_oracle(args) for args in inputs)
    assert results[-1]>=100 and sum(count for result,count in results.items() if result>=0)>=200
    assert len(set(map(tuple,inputs)))>=150
    assert set(''.join(board+hand for board,hand in inputs))==set('RYBGW')


def test_local_chain_resolution_matches_global_run_rescanning():
    tree=ast.parse(REFERENCE)
    insertion=next(node for node in tree.body[0].body if isinstance(node,ast.FunctionDef) and node.name=='insert')
    namespace={}
    exec(compile(ast.Module(body=[insertion],type_ignores=[]),'<isolated-local-collapse>','exec'),namespace)
    insert=namespace['insert']
    for length in range(1,9):
        for chars in product('RB',repeat=length):
            board=''.join(chars)
            if not stable(board):continue
            for color in 'RYBGW':
                for position in range(len(board)+1):
                    assert insert(board,position,color)==collapse_oracle(board[:position]+color+board[position:])
    assert insert('RRBBRR',3,'B')==''  # The second removed group has four R balls.


def test_zuma_exhaustive_small_board_and_hand_states():
    solve=reference()
    hands=[''.join(chars) for length in range(1,4) for chars in combinations_with_replacement('RB',length)]
    checked=0
    for length in range(1,9):
        for chars in product('RB',repeat=length):
            board=''.join(chars)
            if not stable(board):continue
            for hand in hands:
                assert solve(board,hand)==zuma_oracle([board,hand])
                checked+=1
    assert checked>1000


def test_preparatory_insertion_and_multi_group_chain_are_required():
    board,hand='RRWWRRBBRR','WB'
    prepared=collapse_oracle(board[:1]+'B'+board[1:])
    assert prepared=='RBRWWRRBBRR' and len(prepared)==len(board)+1
    assert collapse_oracle(prepared[:3]+'W'+prepared[3:])==''
    for color in hand:
        for position in range(len(board)+1):
            assert collapse_oracle(board[:position]+color+board[position:])!=''
    assert reference()(board,hand)==zuma_oracle([board,hand])==2
    assert reference()('RRBBRR','B')==1


def test_zuma_hand_inventory_unused_balls_and_symmetries():
    solve=reference()
    assert solve('RR','R')==1 and solve('RR','B')==-1
    assert solve('G','GGGGG')==2 and solve('R','R')==-1
    rng=random.Random(488)
    translation=str.maketrans('RYBGW','YBGWR')
    for _ in range(100):
        board,hand=random_zuma(rng)
        expected=solve(board,hand)
        assert solve(board[::-1],hand)==expected
        assert solve(board.translate(translation),hand.translate(translation))==expected
        for order in set(permutations(hand)):
            assert solve(board,''.join(order))==expected


def test_zuma_full_size_stress_matches_independent_oracle_or_certificate():
    solve=reference()
    for args,expected in BATCH[488]['stress'][:4]:
        assert solve(*args)==expected==zuma_oracle(args)
    for args,expected in BATCH[488]['stress'][4:]:
        assert relaxed_deletion_bound(args[0],len(args[1]))>len(args[1])
        assert solve(*args)==expected==-1


def test_interval_lower_bound_matches_independent_relaxed_deletion_search():
    tree=ast.parse(REFERENCE)
    optimistic=next(node for node in tree.body[0].body if isinstance(node,ast.FunctionDef) and node.name=='optimistic')
    namespace={'cache':cache}
    exec(compile(ast.Module(body=[optimistic],type_ignores=[]),'<isolated-relaxation>','exec'),namespace)
    bound=namespace['optimistic']
    for length in range(1,9):
        for chars in product('RB',repeat=length):
            board=''.join(chars)
            assert bound(board)==relaxed_deletion_bound(board,2*length)
    assert bound('RRWWRRBBRR')==2  # Compressing the initial R runs breaks this bound.
    for args,expected in BATCH[488]['stress']:
        if expected>=0:assert bound(args[0])<=expected
    for args,_ in BATCH[488]['stress'][4:]:
        assert bound(args[0])>len(args[1])


def test_zuma_recursion_priority_and_advanced_prerequisites():
    catalog=get_catalog();problem=catalog['leetcode-488']
    assert problem.difficulty>=8 and review_focus_boost(problem)>=50
    assert problem.prerequisites==['recursion','backtracking','dynamic-programming']
    for topic in problem.prerequisites:
        assert any(p.difficulty<8 and topic in p.topics for p in catalog.values())
    assert any('removes nothing immediately' in constraint for constraint in problem.constraints)
