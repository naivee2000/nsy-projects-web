from functools import lru_cache
from itertools import product
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.content_solutions import TreeNode
from code_practice.import_batch_014 import level_values
from code_practice.import_batch_019 import complete_bst_oracle
from code_practice.import_batch_040 import BATCH, cycle_oracle, game_oracle, repetition_oracle
from code_practice.learning import prerequisites_met, review_focus_boost
from code_practice.schemas import ProblemDefinition, TestCase as Case, analyze_integer_tree
from code_practice.validation import _serialize, _treenode, compare, run_source


def reference(pid):
    namespace = {'TreeNode':TreeNode}
    exec(BATCH[pid]['reference'],namespace)
    return namespace[BATCH[pid]['name']]


@lru_cache(None)
def shapes(size):
    if size==0:
        return (None,)
    return tuple((a,b) for left in range(size) for a in shapes(left) for b in shapes(size-left-1))


def label(shape,iterator):
    if shape is None:
        return None
    left = label(shape[0],iterator)
    value = next(iterator)
    return value,left,label(shape[1],iterator)


def fixtures(pid):
    spec = BATCH[pid]; rng = random.Random(4047+pid)
    return ([a for a,_ in spec['examples']] + spec['boundaries'] + [a for a,_ in spec['stress']]
            + [spec['generator'](rng) for _ in range(500)])


def lifted_repetition(s1,n1,s2,n2):
    """Independent binary lifting of block transitions, with no cycle detection."""
    jump,gain = [],[]
    for start in range(len(s2)):
        index,matched = start,0
        for char in s1:
            if char==s2[index]:
                index += 1
                if index==len(s2):
                    index = 0
                    matched += 1
        jump.append(index); gain.append(matched)
    offset,completed = 0,0
    while n1:
        if n1 & 1:
            completed += gain[offset]
            offset = jump[offset]
        gain = [gain[i]+gain[jump[i]] for i in range(len(s2))]
        jump = [jump[jump[i]] for i in range(len(s2))]
        n1 >>= 1
    return completed//n2


def test_batch_40_reference_and_plausible_wrong_solutions():
    catalog = get_catalog()
    for pid in BATCH:
        problem = catalog[f'leetcode-{pid}']
        assert problem.status=='approved' and len(problem.hints)==4 and problem.editorial
        assert sum(t.visible for t in problem.tests)==2 and sum(not t.visible for t in problem.tests)>=12
        assert all(run_source(problem.reference_solution,problem,test)==(True,None) for test in problem.tests)
        for wrong in problem.known_wrong_solutions:
            results = [run_source(wrong,problem,test) for test in problem.tests]
            assert (False,None) in results and all(error is None for _,error in results)
    assert review_focus_boost(catalog['leetcode-450'])>=60
    assert review_focus_boost(catalog['leetcode-464'])>=50
    assert catalog['leetcode-464'].difficulty==7
    assert prerequisites_met(catalog['leetcode-466'],{'strings':70,'dynamic-programming':70})
    assert not prerequisites_met(catalog['leetcode-466'],{'strings':70,'dynamic-programming':69})


def test_batch_40_deterministic_and_generated_inputs_respect_source_constraints():
    for pid in BATCH:
        for args in fixtures(pid):
            if pid==450:
                tree = analyze_integer_tree(args[0])
                assert tree is not None and len(tree[0])<=10000
                assert tree[0]==sorted(set(tree[0])) and all(abs(v)<=100000 for v in tree[0])
                assert type(args[1]) is int and abs(args[1])<=100000
            elif pid==457:
                assert 1<=len(args[0])<=5000 and all(0<abs(v)<=1000 for v in args[0])
            elif pid==464:
                assert 1<=args[0]<=20 and 0<=args[1]<=300
            else:
                assert all(1<=len(args[i])<=100 and set(args[i])<=set('abcdefghijklmnopqrstuvwxyz') for i in (0,2))
                assert 1<=args[1]<=10**6 and 1<=args[3]<=10**6


def test_bst_deletion_accepts_every_surviving_shape_without_requiring_balance():
    checked = 0
    for size in range(8):
        expected = list(range(size))
        # A complete BST is one expectation, but every valid shape must pass.
        goal = complete_bst_oracle([expected])
        for shape in shapes(size):
            actual = level_values(label(shape,iter(expected)))
            assert compare(actual,goal,'bst_delete')
            checked += 1
    assert checked==626
    assert compare([1,None,2,None,3,None,4],[3,2,4,1],'bst_delete')
    assert not compare([2,3,1],[2,1,3],'bst_delete')
    assert not compare([2,1,2],[2,1,3],'bst_delete')
    assert not compare([2,1],[2,1,3],'bst_delete')


def test_bst_deletion_reference_exhausts_every_small_tree_and_key():
    solve = reference(450)
    for size in range(8):
        for shape in shapes(size):
            tree = level_values(label(shape,iter(range(size))))
            for key in range(-1,size+1):
                answer = _serialize(solve(_treenode(tree),key),'treenode',True)
                assert analyze_integer_tree(answer)[0]==[n for n in range(size) if n!=key]
    for args,expected in BATCH[450]['stress']:
        answer = _serialize(solve(_treenode(args[0]),args[1]),'treenode',True)
        assert compare(answer,expected,'bst_delete')


@pytest.mark.parametrize('change',['duplicate-input','invalid-input','wrong-survivors','bad-key','mixed',
                                     'raw-return','wrong-input','wrong-key-adapter','node-policy','missing-key'])
def test_bst_deletion_schema_binds_expectations_to_the_actual_input(change):
    payload = get_catalog()['leetcode-450'].model_dump(mode='json')
    first = payload['tests'][0]
    if change=='duplicate-input': first['arguments'][0] = [2,1,2]
    elif change=='invalid-input': first['arguments'][0] = [2,3,1]
    elif change=='wrong-survivors': first['expected'] = [5,3,6,2,4,None,7]
    elif change=='bad-key': first['arguments'][1] = True
    elif change=='mixed': first['comparator'] = 'exact'
    elif change=='raw-return': payload['signature']['return_adapter'] = 'raw'
    elif change=='wrong-input': payload['signature']['parameters'][0]['adapter'] = 'raw'
    elif change=='wrong-key-adapter': payload['signature']['parameters'][1]['adapter'] = 'listnode'
    elif change=='node-policy': payload['signature']['node_policy'] = 'reuse_input_nodes'
    else: first['arguments'].pop()
    with pytest.raises(ValueError,match='BST-deletion'):
        ProblemDefinition.model_validate(payload)


@pytest.mark.parametrize('bad',[None,{},[None],[True],[1.0],['1'],[1,None,None,2],[1,None,None,None]])
def test_bst_deletion_rejects_malformed_or_noninteger_tree_encodings(bad):
    assert not compare(bad,[1],'bst_delete')


def test_bst_deletion_requires_real_nodes_and_allows_predecessor_successor_and_empty():
    problem = get_catalog()['leetcode-450']
    case = Case(id='root-choice',arguments=[[2,1,3],2],expected=[3,1],comparator='bst_delete')
    for body in ['return TreeNode(3,TreeNode(1))','return TreeNode(1,None,TreeNode(3))']:
        assert run_source('def delete_bst_node(root,key):\n    '+body,problem,case)==(True,None)
    for body in ['return root','return TreeNode(3)','return TreeNode(1,TreeNode(3))',
                 'return TreeNode(3,TreeNode(1.0))','return TreeNode(True)',
                 'return [3,1]','root.right=root; return root',
                 'child=TreeNode(1); return TreeNode(3,child,child)']:
        assert not run_source('def delete_bst_node(root,key):\n    '+body,problem,case)[0]
    empty = Case(id='last-node',arguments=[[2],2],expected=[],comparator='bst_delete')
    assert run_source('def delete_bst_node(root,key):\n    return None',problem,empty)==(True,None)
    assert not run_source('def delete_bst_node(root,key):\n    return TreeNode(None)',problem,empty)[0]


def test_circular_cycles_exhaust_directions_wrapping_and_self_loops():
    solve = reference(457)
    for size in range(1,7):
        for nums in product([-2,-1,1,2],repeat=size):
            assert solve(list(nums))==cycle_oracle([nums])
    for args,expected in BATCH[457]['stress']:
        assert solve(args[0][:])==expected


def test_circular_path_clearing_has_linear_array_access_on_long_failed_routes():
    class Counted(list):
        accesses = 0
        def __getitem__(self,index):
            self.accesses += 1
            return super().__getitem__(index)
        def __setitem__(self,index,value):
            self.accesses += 1
            return super().__setitem__(index,value)
    for size in [10,100,1000,5000]:
        nums = Counted([1]*(size-1)+[-1])
        assert not reference(457)(nums)
        assert nums.accesses<100*size


def test_minimax_exhausts_small_games_and_large_boundary_states():
    solve = reference(464)
    # Literal un-memoized game tree does not use either implementation's bitmasks.
    def literal(remaining,needed):
        return any(value>=needed or not literal(remaining[:i]+remaining[i+1:],needed-value)
                   for i,value in enumerate(remaining))
    for maximum in range(1,10):
        for target in range(maximum*(maximum+1)//2+3):
            expected = target==0 or maximum*(maximum+1)//2>=target and literal(tuple(range(1,maximum+1)),target)
            assert solve(maximum,target)==game_oracle([maximum,target])==expected
    for args,expected in BATCH[464]['stress']:
        assert solve(*args)==game_oracle(args)==expected


def test_repetition_cycles_match_expanded_search_and_independent_binary_lifting():
    solve = reference(466)
    strings = [''.join(chars) for length in range(1,4) for chars in product('ab',repeat=length)]
    for s1,s2 in product(strings,repeat=2):
        for n1,n2 in product(range(1,5),repeat=2):
            assert solve(s1,n1,s2,n2)==repetition_oracle([s1,n1,s2,n2])==lifted_repetition(s1,n1,s2,n2)
    rng = random.Random(466)
    for _ in range(500):
        args = [''.join(rng.choice('ab') for _ in range(rng.randint(1,100))),rng.randint(1,10**6),
                ''.join(rng.choice('ab') for _ in range(rng.randint(1,100))),rng.randint(1,10**6)]
        assert solve(*args)==lifted_repetition(*args)
    for args,expected in BATCH[466]['stress']:
        assert solve(*args)==lifted_repetition(*args)==expected
