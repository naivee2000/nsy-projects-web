from functools import lru_cache
from itertools import combinations
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_002 import positions
from code_practice.import_batch_035 import BATCH, RECOVER, recover_oracle, swap_inorder
from code_practice.schemas import FunctionSignature, TestCase as Case
from code_practice.validation import TreeNode, _serialize, run_source


def test_recovery_reference_examples_counterexamples_and_large_chains():
    problem = get_catalog()['leetcode-99']
    assert problem.signature.node_policy == 'preserve_tree_structure'
    assert problem.signature.result_mode == 'mutated_argument'
    assert 'class TreeNode:' in problem.starter_code
    assert sum(t.visible for t in problem.tests) == 2
    assert sum(not t.visible for t in problem.tests) >= 12
    assert len(problem.hints) == 4 and problem.editorial
    assert all(run_source(RECOVER,problem,t) == (True,None) for t in problem.tests)
    for wrong in problem.known_wrong_solutions:
        assert any(run_source(wrong,problem,t) == (False,None) for t in problem.tests)


@pytest.mark.parametrize('change',[
    {'result_mode':'return','mutated_parameter':None},
    {'result_mode':'returned_prefix','returns':'int'},
    {'mutated_parameter':None}, {'mutated_parameter':1},
    {'returns':'TreeNode | None'}, {'return_adapter':'treenode'},
    {'return_adapter':'treenode_value'}, {'immutable_parameters':[0]},
    {'parameters':[{'name':'root','annotation':'list[int]','adapter':'raw'}]},
    {'parameters':[{'name':'root','annotation':'ListNode | None','adapter':'listnode'}]},
])
def test_structure_policy_rejects_incompatible_signatures(change):
    payload = get_catalog()['leetcode-99'].signature.model_dump()
    with pytest.raises(ValueError):
        FunctionSignature.model_validate({**payload,**change})


@pytest.mark.parametrize('body,accepted',[
    ('root.val,root.left.val = root.left.val,root.val',True),
    ('root.val = 2; root.left = TreeNode(1)',False),
    ('return TreeNode(2,TreeNode(1))',False),
    ('root.val = 2.0; root.left.val = 1',False),
    ('root.val = 2; root.left.val = True',False),
    ('Ghost=type("Ghost",(TreeNode,),{"__bool__":lambda self:False}); root.val=2; root.left.val=1; root.right=Ghost(None)',False),
    ('root.left.val = 1; root.val = 2; root.right = root.left; root.left = None',False),
    ('child = root.left; child.right = root; child.right = None; root.val = 2; child.val = 1',True),
])
def test_recovery_allows_restored_threads_but_not_rebuilding_or_noninteger_values(body,accepted):
    problem = get_catalog()['leetcode-99']
    case = Case(id='swapped-left-pair',arguments=[[1,2]],expected=[2,1])
    assert run_source('def recover_bst(root):\n    '+body,problem,case) == (accepted,None)


def test_correct_displayed_values_do_not_allow_swapping_node_positions():
    problem = get_catalog()['leetcode-99']
    case = Case(id='swapped-children',arguments=[[2,3,1]],expected=[2,1,3])
    wrong = 'def recover_bst(root):\n    root.left,root.right = root.right,root.left'
    assert run_source(wrong,problem,case) == (False,None)
    assert run_source(RECOVER,problem,case) == (True,None)
    incomplete = 'def recover_bst(root):\n    root.left.right = root'
    accepted,error = run_source(incomplete,problem,case)
    assert not accepted and 'cycle' in error


def test_structure_policy_observes_the_selected_tree_argument():
    problem = get_catalog()['leetcode-99']
    payload = problem.signature.model_dump()
    payload['parameters'].insert(0,{'name':'untouched','annotation':'int','adapter':'raw'})
    payload['mutated_parameter'] = 1
    signature = FunctionSignature.model_validate(payload)
    observed = problem.model_copy(update={'signature':signature})
    case = Case(id='second-argument',arguments=[7,[1,2]],expected=[2,1])
    assert run_source('def recover_bst(untouched,root):\n    root.val,root.left.val=root.left.val,root.val',observed,case) == (True,None)


def test_returned_input_node_policy_also_rejects_falsey_inserted_children():
    problem = get_catalog()['leetcode-236']
    case = Case(id='falsey-new-child',arguments=[[2,1],1,2],expected=2)
    source = 'def lowest_common_ancestor(root,p,q):\n    Ghost=type("Ghost",(TreeNode,),{"__bool__":lambda self:False}); root.right=Ghost(None); return root'
    assert run_source(source,problem,case) == (False,None)


@lru_cache(None)
def shapes(n):
    if n == 0:
        return (None,)
    return tuple((left,right) for split in range(n)
                 for left in shapes(split) for right in shapes(n-1-split))


def build_shape(shape, counter):
    if shape is None:
        return None
    left = build_shape(shape[0],counter)
    value = next(counter)
    right = build_shape(shape[1],counter)
    return TreeNode(value,left,right)


def inorder_values(values):
    # Separate conventional pointer traversal to audit the path-sorting oracle.
    from code_practice.validation import _treenode
    stack, current, ordered = [], _treenode(values), []
    while stack or current:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        ordered.append(current.val)
        current = current.right
    return ordered


def test_morris_recovery_exhausts_every_swap_on_all_tree_shapes_through_seven_nodes():
    problem = get_catalog()['leetcode-99']
    for n in range(2,8):
        for shape in shapes(n):
            valid = _serialize(build_shape(shape,iter(range(n))),'treenode')
            for first,second in combinations(range(n),2):
                corrupted = swap_inorder(valid,first,second)
                assert recover_oracle([corrupted]) == valid
                assert inorder_values(valid) == list(range(n))
                assert run_source(RECOVER,problem,Case(id='all-swaps',arguments=[corrupted],expected=valid)) == (True,None)


def test_all_recovery_inputs_have_exactly_two_swapped_values_and_valid_source_bounds():
    spec = BATCH[99]
    rng = random.Random(4146)
    inputs = [a for a,_ in spec['examples']] + spec['boundaries']
    inputs += [a for a,_ in spec['stress']] + [spec['generator'](rng) for _ in range(500)]
    for args in inputs:
        values = list(positions(args[0]).values())
        assert 2 <= len(values) <= 1000 and len(values) == len(set(values))
        assert all(type(value) is int and -2**31 <= value < 2**31 for value in values)
        ordered = inorder_values(args[0])
        expected = sorted(values)
        assert sum(a != b for a,b in zip(ordered,expected)) == 2
        assert inorder_values(recover_oracle(args)) == expected
