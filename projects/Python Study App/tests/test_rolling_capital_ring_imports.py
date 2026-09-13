from copy import deepcopy
from itertools import product
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_049 import BATCH, hole_oracle, maze_oracle, ring_oracle
from code_practice.learning import review_focus_boost
from code_practice.validation import run_source


def reference(pid):
    scope={}
    exec(BATCH[pid]['reference'],scope)
    return scope[BATCH[pid]['name']]


@pytest.mark.parametrize('pid',BATCH)
def test_batch_49_references_and_two_logically_wrong_algorithms(pid):
    problem=get_catalog()[f'leetcode-{pid}']
    assert len(problem.hints)==4 and problem.editorial and problem.status=='approved'
    assert sum(t.visible for t in problem.tests)==2
    assert sum(not t.visible for t in problem.tests)>=12
    assert len({str(t.arguments) for t in problem.tests})==len(problem.tests)
    assert all(run_source(problem.reference_solution,problem,t)==(True,None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        outcomes=[run_source(wrong,problem,t) for t in problem.tests]
        assert (False,None) in outcomes and all(error is None for _,error in outcomes)


@pytest.mark.parametrize('pid',BATCH)
def test_batch_49_full_source_domains(pid):
    spec=BATCH[pid];rng=random.Random(4047+pid)
    cases=[a for a,_ in spec['examples']]+spec['boundaries']+[a for a,_ in spec['stress']]
    cases += [spec['generator'](rng) for _ in range(500)]
    for args in cases:
        if pid in (499,505):
            maze,start,target=args;rows,cols=len(maze),len(maze[0])
            assert 1<=rows<=100 and 1<=cols<=100 and start!=target
            assert all(len(row)==cols and all(type(v) is int and v in (0,1) for v in row) for row in maze)
            for r,c in (start,target):assert 0<=r<rows and 0<=c<cols and maze[r][c]==0
        elif pid==502:
            k,w,p,c=args
            assert 1<=k<=100000 and 1<=len(p)==len(c)<=100000
            assert 0<=w<=10**9 and all(0<=v<=10**9 for v in c)
            assert all(0<=v<=10000 for v in p) and w+sum(sorted(p,reverse=True)[:k])<2**31
        elif pid==503:
            assert 1<=len(args[0])<=10000 and all(type(v) is int and abs(v)<=10**9 for v in args[0])
        else:
            ring,key=args
            assert 1<=len(ring)<=100 and 1<=len(key)<=100
            assert set(key)<=set(ring)<=set('abcdefghijklmnopqrstuvwxyz')


@pytest.mark.parametrize('pid',BATCH)
def test_batch_49_stress_expected_results_and_input_preservation(pid):
    solve=reference(pid)
    for args,expected in BATCH[pid]['stress']:
        copy=deepcopy(args)
        assert solve(*copy)==expected
        assert copy==args
        if pid in (499,505,514):assert BATCH[pid]['oracle'](args)==expected


def test_all_three_by_three_mazes_and_distinct_empty_endpoints():
    hole,distance=reference(499),reference(505)
    checked=0
    for mask in range(512):
        maze=[[(mask>>(r*3+c))&1 for c in range(3)] for r in range(3)]
        cells=[[r,c] for r in range(3) for c in range(3) if not maze[r][c]]
        for start in cells:
            for target in cells:
                if start==target:continue
                args=[maze,start,target]
                assert hole(*args)==hole_oracle(args)
                assert distance(*args)==maze_oracle(args)
                checked+=1
    assert checked==9216


def test_rolling_contracts_and_lexicographic_distance_not_turn_count():
    distance,hole=reference(505),reference(499)
    args=[[[0,0,0,0,0]],[0,0],[0,2]]
    assert distance(*args)==-1 and hole(*args)=='r'
    sample=BATCH[499]['examples'][0][0]
    assert hole(*sample)=='lul'  # Same distance as ul, but more instructions.
    maze=[[0,0,0],[0,0,0],[0,0,0]]
    assert hole(maze,[0,0],[2,2])=='dr'
    assert distance(maze,[0,0],[2,2])==4
    assert hole(maze,[0,0],[1,1])=='impossible'
    assert 'heaps' in BATCH[499]['topics'] and 'matrices' in BATCH[505]['topics']


def test_ipo_exhaustive_small_project_sets_and_initial_capital():
    solve=reference(502)
    checked=0
    for n in range(1,4):
        for values in product(range(3),repeat=2*n):
            profits,capital=list(values[:n]),list(values[n:])
            for w in range(3):
                for k in range(1,n+2):
                    args=[k,w,profits,capital]
                    assert solve(*args)==BATCH[502]['oracle'](args)
                    checked+=1
    assert checked==9531


def test_capital_is_not_spent_projects_not_reused_and_stop_is_legal():
    solve=reference(502)
    assert solve(2,10,[5,9],[10,15])==24
    assert solve(100000,0,[1],[0])==1
    assert solve(3,0,[0,99],[0,1])==0
    assert solve(1,0,[1,100],[0,1])==1
    assert solve(2,0,[1,100],[0,1])==101


def test_circular_successors_exhaustive_signed_duplicates():
    solve=reference(503)
    for n in range(1,8):
        for values in product((-2,-1,0,1,2),repeat=n):
            nums=list(values)
            assert solve(nums)==BATCH[503]['oracle']([nums])
    assert solve([3,1,2])==[-1,2,3]
    assert solve([2,2])==[-1,-1]


def test_ring_exhaustive_binary_rings_and_keys():
    solve=reference(514);checked=0
    for n in range(1,7):
        for chars in product('ab',repeat=n):
            ring=''.join(chars)
            for m in range(1,5):
                for letters in product(sorted(set(ring)),repeat=m):
                    key=''.join(letters)
                    assert solve(ring,key)==ring_oracle([ring,key])
                    checked+=1
    assert checked>3000


def test_ring_future_positions_wraparound_and_press_costs():
    solve=reference(514)
    assert solve('aabac','bac')==7
    # Nearest-a greedy breaks the tie toward index 1 and costs 8. Index 3 enables c.
    assert solve('abcde','ee')==3
    assert solve('a','aaaa')==4
    catalog=get_catalog()
    assert review_focus_boost(catalog['leetcode-514'])>=50
    for pid in (499,502,514):
        problem=catalog[f'leetcode-{pid}']
        assert problem.difficulty>=8 and problem.prerequisites
        for topic in problem.prerequisites:
            assert any(p.difficulty<8 and topic in p.topics for p in catalog.values())
