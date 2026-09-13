from collections import Counter
from copy import deepcopy
from itertools import combinations_with_replacement, product
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_002 import positions,flatten
from code_practice.import_batch_050 import BATCH,balanced,chain
from code_practice.learning import review_focus_boost
from code_practice.validation import run_source, _treenode as tree_from


def reference(pid):
    namespace={};exec(BATCH[pid]['reference'],namespace)
    return namespace[BATCH[pid]['name']]


@pytest.mark.parametrize('pid',BATCH)
def test_batch_50_reference_and_logical_wrong_algorithms(pid):
    problem=get_catalog()[f'leetcode-{pid}']
    assert 'class TreeNode:' in problem.starter_code and len(problem.hints)==4
    assert sum(t.visible for t in problem.tests)==2 and sum(not t.visible for t in problem.tests)>=12
    assert all(run_source(problem.reference_solution,problem,t)==(True,None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        outcomes=[run_source(wrong,problem,t) for t in problem.tests]
        assert (False,None) in outcomes and all(error is None for _,error in outcomes)


@pytest.mark.parametrize('pid',BATCH)
def test_batch_50_source_domains_and_duplicate_bst_policy(pid):
    spec=BATCH[pid];rng=random.Random(4047+pid)
    cases=[a for a,_ in spec['examples']]+spec['boundaries']+[a for a,_ in spec['stress']]
    cases += [spec['generator'](rng) for _ in range(500)]
    for (values,) in cases:
        nums=[v for v in values if v is not None]
        assert (0 if pid==515 else 1)<=len(nums)<=10000
        lo,hi=(-100000,100000) if pid in (501,508) else (-2**31,2**31-1)
        assert all(type(v) is int and lo<=v<=hi for v in nums)
        root=tree_from(values)
        if pid==501:
            stack=[(root,lo,hi)]
            while stack:
                node,low,high=stack.pop()
                assert low<=node.val<=high
                if node.left:stack.append((node.left,low,node.val))
                if node.right:stack.append((node.right,node.val,high))


@pytest.mark.parametrize('pid',BATCH)
def test_batch_50_full_size_outputs_and_unchanged_nodes(pid):
    solve=reference(pid)
    for args,expected in BATCH[pid]['stress']:
        root=tree_from(args[0]);stack=[root];before={}
        while stack:
            node=stack.pop();before[id(node)]=(node,node.val,node.left,node.right)
            if node.left:stack.append(node.left)
            if node.right:stack.append(node.right)
        result=solve(root)
        assert (sorted(result) if pid in (501,508) else result)==expected
        assert all((n.val,n.left,n.right)==(v,l,r) for n,v,l,r in before.values())
        assert len(before)==10000


def test_bst_modes_all_small_multisets_in_three_shapes():
    solve=reference(501)
    for n in range(1,9):
        for values in combinations_with_replacement((-2,-1,0,1,2),n):
            counts=Counter(values);expected=sorted(v for v,c in counts.items() if c==max(counts.values()))
            for tree in (balanced(values),chain(values),chain(values[::-1],True)):
                assert sorted(solve(tree_from(tree)))==expected


def test_subtree_sums_exhaustive_signed_complete_trees():
    solve=reference(508)
    for n in range(1,8):
        for values in product((-1,0,1),repeat=n):
            args=[list(values)]
            assert sorted(solve(tree_from(args[0])))==BATCH[508]['oracle'](args)
    assert sorted(solve(tree_from([0,0,0])))==[0]
    assert sorted(solve(tree_from([5,2,-3])))==[-3,2,4]


def test_level_contracts_exhaust_all_depth_three_shapes():
    bottom,rows=reference(513),reference(515)
    paths=[(),(0,),(1,),(0,0),(0,1),(1,0),(1,1)]
    checked=0
    for flags in product((False,True),repeat=6):
        present={paths[0]}|{p for p,on in zip(paths[1:],flags) if on}
        if any(p[:-1] not in present for p in present if p):continue
        ordered=sorted(present)
        for values in product((-1,1),repeat=len(ordered)):
            tree=flatten(dict(zip(ordered,values)))
            assert bottom(tree_from(tree))==BATCH[513]['oracle']([tree])
            assert rows(tree_from(tree))==BATCH[515]['oracle']([tree])
            checked+=1
    assert checked==722
    assert rows(None)==[]


def test_leftmost_not_minimum_or_left_chain_and_rows_not_right_view():
    bottom,rows=reference(513),reference(515)
    assert bottom(tree_from([9,8,7,100,None,None,-5]))==100
    assert bottom(tree_from([1,2,3,None,None,4]))==4
    assert rows(tree_from([-1,-5,-3]))==[-1,-3]
    assert rows(tree_from([1,9,2]))==[1,9]


def test_recursive_tree_imports_retain_review_priority_and_distinct_contracts():
    catalog=get_catalog()
    for pid in (508,513,515):assert review_focus_boost(catalog[f'leetcode-{pid}'])>=50
    assert catalog['leetcode-501'].signature.parameters[0].adapter=='treenode'
    assert catalog['leetcode-501'].tests[1].expected==[1,3]
    assert 'not numeric size' in catalog['leetcode-513'].statement
    assert 'only negative values' in catalog['leetcode-515'].statement
