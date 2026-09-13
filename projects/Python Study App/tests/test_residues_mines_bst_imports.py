from copy import deepcopy
from itertools import combinations,product
import json
from pathlib import Path
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_053 import BATCH,abbreviated,balanced,chain,neighbors
from code_practice.learning import review_focus_boost
from code_practice.reconcile_overlaps import check_bst_gap
from code_practice.validation import _treenode,run_source
from code_practice.schemas import TestCase as Case


def reference(pid):
    scope={};exec(BATCH[pid]['reference'],scope)
    return scope[BATCH[pid]['name']]


@pytest.mark.parametrize('pid',BATCH)
def test_batch_53_reference_tests_and_algorithmic_rejections(pid):
    p=get_catalog()[f'leetcode-{pid}']
    assert len(p.hints)==4 and p.editorial
    assert sum(t.visible for t in p.tests)==2 and sum(not t.visible for t in p.tests)>=12
    assert all(run_source(p.reference_solution,p,t)==(True,None) for t in p.tests)
    for wrong in p.known_wrong_solutions:
        results=[run_source(wrong,p,t) for t in p.tests]
        assert (False,None) in results and all(error is None for _,error in results)


@pytest.mark.parametrize('pid',BATCH)
def test_batch_53_fixture_and_generator_domains(pid):
    spec=BATCH[pid];rng=random.Random(4047+pid)
    args=[a for a,_ in spec['examples']]+spec['boundaries']+[a for a,_ in spec['stress']]
    args += [spec['generator'](rng) for _ in range(500)]
    for a in args:
        if pid==523:
            nums,k=a
            assert 1<=len(nums)<=100000 and all(type(v) is int and 0<=v<=10**9 for v in nums)
            assert sum(nums)<=2**31-1 and 1<=k<=2**31-1
        elif pid==527:
            words=a[0]
            assert 1<=len(words)<=400 and len(set(words))==len(words)
            assert all(2<=len(w)<=400 and set(w)<=set('abcdefghijklmnopqrstuvwxyz') for w in words)
        elif pid==529:
            board,(r,c)=a;rows=len(board);cols=len(board[0])
            assert 1<=rows<=50 and 1<=cols<=50 and all(len(row)==cols for row in board)
            assert all(v in 'MEB12345678' for row in board for v in row)
            assert 0<=r<rows and 0<=c<cols and board[r][c] in 'ME'
            for x,row in enumerate(board):
                for y,v in enumerate(row):
                    mines=sum(board[i][j]=='M' for i,j in neighbors(x,y,rows,cols))
                    if v=='B':assert mines==0
                    if v.isdigit():assert int(v)==mines
        else:
            values=[v for v in a[0] if v is not None]
            assert 2<=len(values)<=10000 and all(type(v) is int and 0<=v<=100000 for v in values)
            node=_treenode(a[0]);stack=[];ordered=[]
            while stack or node:
                while node:stack.append(node);node=node.left
                node=stack.pop();ordered.append(node.val);node=node.right
            assert ordered==sorted(values)


def test_remainders_exhaustive_short_arrays_and_full_value_range():
    solve=reference(523)
    for length in range(1,8):
        for values in product(range(3),repeat=length):
            for k in range(1,10):assert solve(values,k)==BATCH[523]['oracle']([values,k])
    rng=random.Random(523)
    for _ in range(500):
        remaining=2**31-1;nums=[]
        for _ in range(rng.randint(1,20)):
            value=rng.randint(0,min(remaining,10**9));nums.append(value);remaining-=value
        k=rng.randint(1,2**31-1)
        assert solve(nums,k)==BATCH[523]['oracle']([nums,k])
    assert solve([1,0,0],3) is True and solve([6,1],6) is False
    for args,expected in BATCH[523]['stress']:assert solve(*args)==expected


def pair_lcp_certificate(words):
    result=[]
    for i,word in enumerate(words):
        needed=1
        for j,other in enumerate(words):
            if i==j or len(word)!=len(other) or word[-1]!=other[-1]:continue
            same=0
            while same<len(word) and word[same]==other[same]:same+=1
            needed=max(needed,same+1)
        result.append(abbreviated(word,needed))
    return result


def test_abbreviation_collision_process_exhaustive_small_sets():
    solve=reference(527)
    pool=['aa','aaa','aaaa','aaba','abaa','abba','baaa','baab','baba','abcdef','abndef']
    for size in range(1,6):
        for words in combinations(pool,size):
            assert solve(words)==BATCH[527]['oracle']([words])==pair_lcp_certificate(words)
    for args,expected in BATCH[527]['stress']:
        assert solve(*args)==expected==pair_lcp_certificate(args[0])
        assert len(set(expected))==len(args[0]) and all(len(a)<=len(w) for a,w in zip(expected,args[0]))
    rng=random.Random(527)
    words=BATCH[527]['stress'][1][0][0][:];rng.shuffle(words)
    assert solve(words)==pair_lcp_certificate(words)


def test_mines_exhaustive_three_by_three_boards_and_every_click():
    solve=reference(529)
    for cells in product('EM',repeat=9):
        board=[list(cells[r*3:r*3+3]) for r in range(3)]
        for r in range(3):
            for c in range(3):
                assert solve(deepcopy(board),[r,c])==BATCH[529]['oracle']([board,[r,c]])


def test_mines_prior_reveals_copy_solution_and_maximum_flood():
    solve=reference(529);rng=random.Random(529)
    for _ in range(100):
        board=[['M' if rng.random()<.2 else 'E' for _ in range(8)] for _ in range(8)]
        for _ in range(4):
            empty=[(r,c) for r in range(8) for c in range(8) if board[r][c]=='E']
            if not empty:break
            click=list(rng.choice(empty));previous=deepcopy(board)
            expected=BATCH[529]['oracle']([previous,click]);board=solve(board,click)
            assert board==expected
            assert all(board[r][c]==v for r,row in enumerate(previous) for c,v in enumerate(row) if v!='E')
    for args,expected in BATCH[529]['stress']:assert solve(*deepcopy(args))==expected==BATCH[529]['oracle'](args)
    p=get_catalog()['leetcode-529'];copy_source=p.reference_solution.replace('def reveal_minesweeper(board,click):','def reveal_minesweeper(board,click):\n    board=[row[:] for row in board]')
    assert all(run_source(copy_source,p,t)==(True,None) for t in p.tests)
    assert review_focus_boost(p)>=50


def test_bst_gap_exhaustive_multisets_three_shapes_and_maximum_chains():
    from itertools import combinations_with_replacement
    solve=reference(530)
    for n in range(2,8):
        for values in combinations_with_replacement(range(5),n):
            for tree in (balanced(values),chain(values),chain(values[::-1],True)):
                assert solve(_treenode(tree))==BATCH[530]['oracle']([tree])
    for args,expected in BATCH[530]['stress']:assert solve(_treenode(args[0]))==expected
    p=get_catalog()['leetcode-530']
    assert p.signature.immutable_parameters==[0] and review_focus_boost(p)>=50
    mutation=p.reference_solution.replace('return best','root.val+=1\n    return best')
    assert all(not run_source(mutation,p,t)[0] for t in p.tests)


def test_bst_duplicate_source_full_domain_and_wrong_reference_rejection():
    root=Path(__file__).resolve().parent.parent
    source=next(s for s in map(json.loads,(root/'catalog_import/sources.jsonl').read_text().splitlines()) if s['source_id']==783)
    payload=get_catalog()['leetcode-530'].model_dump(mode='json')
    evidence=check_bst_gap(payload,source)
    assert evidence['oracle_inputs']==500 and evidence['largest_input']==100
    for wrong in BATCH[530]['wrong']:
        with pytest.raises(ValueError,match='disagrees'):check_bst_gap({**payload,'reference_solution':wrong},source)
    assert 'leetcode-783' not in get_catalog()


@pytest.mark.parametrize('mutation',[
    'root.left=TreeNode(root.left.val,root.left.left,root.left.right)',
    'root.left,root.right=root.right,root.left',
    'root.left.val=True',
    'root.left.left=TreeNode(1)',
])
def test_readonly_tree_rejects_identical_replacements_links_and_value_types(mutation):
    p=get_catalog()['leetcode-530']
    case=Case(id='equal-node-identity',arguments=[[1,1,1]],expected=0)
    source=p.reference_solution.replace('return best',mutation+'\n    return best')
    assert run_source(source,p,case)==(False,None)


MORRIS='''\
def minimum_bst_difference(root):
    node=root;previous=None;best=100001
    while node is not None:
        if node.left is None:
            if previous is not None:best=min(best,node.val-previous)
            previous=node.val;node=node.right
        else:
            predecessor=node.left
            while predecessor.right is not None and predecessor.right is not node:
                predecessor=predecessor.right
            if predecessor.right is None:
                predecessor.right=node;node=node.left
            else:
                predecessor.right=None
                if previous is not None:best=min(best,node.val-previous)
                previous=node.val;node=node.right
    return best
'''


def test_readonly_tree_allows_falsey_original_nodes_and_restored_morris_threads():
    p=get_catalog()['leetcode-530']
    falsey='class TreeNode:\n    def __init__(self,val=0,left=None,right=None):\n        self.val=val;self.left=left;self.right=right\n    def __bool__(self):\n        return False\n'
    for solution in (p.reference_solution,MORRIS):
        for source in (solution,falsey+solution):
            assert all(run_source(source,p,t)==(True,None) for t in p.tests)
