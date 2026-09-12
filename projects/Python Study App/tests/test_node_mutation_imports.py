import json
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.import_batch_002 import positions
from code_practice.import_batch_016 import BATCH, RIGHT_FIRST_WRONG
from code_practice.learning import review_focus_boost
from code_practice.schemas import FunctionSignature, TestCase as Case
from code_practice.starter_code import with_support_classes
from code_practice.validation import run_source


@pytest.mark.parametrize("order", [[True], [-1], [1.0], [0, 0]])
def test_node_order_indices_are_unique_nonnegative_strict_integers(order):
    with pytest.raises(ValueError):
        Case(id="bad-order", arguments=[[1]], expected=[1], expected_node_order=order)


def test_node_reuse_schema_supports_trees_and_mutation_but_not_raw_prefix_outputs():
    for adapter in ("treenode", "listnode"):
        base = dict(name="solve", parameters=[dict(name="root", annotation="object", adapter=adapter)],
                    returns="object", node_policy="reuse_input_nodes")
        assert FunctionSignature(**base, return_adapter=adapter).node_policy == "reuse_input_nodes"
        assert FunctionSignature(**base, result_mode="mutated_argument", mutated_parameter=0).node_policy == "reuse_input_nodes"
        with pytest.raises(ValueError):
            FunctionSignature(**base)
        with pytest.raises(ValueError):
            FunctionSignature(**base, result_mode="mutated_argument", mutated_parameter=5)
    with pytest.raises(ValueError):
        FunctionSignature(name="solve", parameters=[dict(name="nums", annotation="list[int]")],
                          returns="int", result_mode="returned_prefix", mutated_parameter=0, node_policy="reuse_input_nodes")


def test_tree_reference_schema_requires_an_earlier_tree_and_identity_checked_output():
    parameters = [
        dict(name="root", annotation="TreeNode", adapter="treenode"),
        dict(name="p", annotation="TreeNode", adapter="treenode_ref", source_parameter=0),
        dict(name="q", annotation="TreeNode", adapter="treenode_ref", source_parameter=0),
    ]
    signature = FunctionSignature(name="lca", parameters=parameters, returns="TreeNode",
                                  return_adapter="treenode_value", node_policy="return_input_node")
    assert signature.parameters[1].source_parameter == 0
    assert "class TreeNode" in with_support_classes("def lca(root, p, q):\n    pass\n",
                                                     ["treenode", "treenode_ref", "treenode_value"])
    with pytest.raises(ValueError):
        FunctionSignature(name="bad", parameters=parameters, returns="TreeNode",
                          return_adapter="treenode_value")
    with pytest.raises(ValueError):
        FunctionSignature(name="bad", parameters=[parameters[1], parameters[0]], returns="int")
    with pytest.raises(ValueError):
        FunctionSignature(name="bad", parameters=[dict(name="x", annotation="int", source_parameter=0)], returns="int")


def test_list_reference_schema_requires_the_selected_deletion_contract():
    parameter = dict(name="node", annotation="ListNode", adapter="listnode_ref")
    signature = FunctionSignature(
        name="delete_node", parameters=[parameter], returns="None", return_adapter="raw",
        result_mode="mutated_argument", mutated_parameter=0,
        node_policy="delete_referenced_list_node",
    )
    assert signature.parameters[0].adapter == "listnode_ref"
    assert "class ListNode" in with_support_classes(
        "def delete_node(node):\n    pass\n", ["listnode_ref"]
    )
    with pytest.raises(ValueError):
        FunctionSignature(
            name="bad", parameters=[parameter], returns="None", return_adapter="raw",
            node_policy="delete_referenced_list_node",
        )
    with pytest.raises(ValueError):
        FunctionSignature(
            name="bad", parameters=[{**parameter, "source_parameter": 0}], returns="None",
            result_mode="mutated_argument", mutated_parameter=0,
            node_policy="delete_referenced_list_node",
        )


def test_selected_list_node_deletion_preserves_required_original_identities():
    original = get_catalog()["leetcode-143"]
    signature = FunctionSignature(
        name="delete_node",
        parameters=[dict(name="node", annotation="ListNode", adapter="listnode_ref")],
        returns="None", return_adapter="raw", result_mode="mutated_argument",
        mutated_parameter=0, node_policy="delete_referenced_list_node",
    )
    problem = original.model_copy(update={"signature": signature})
    case = Case(
        id="selected-delete",
        arguments=[{"values": [4, 5, 1, 9], "index": 1}],
        expected=[4, 1, 9],
    )
    correct = "def delete_node(node):\n    node.val = node.next.val\n    node.next = node.next.next"
    assert run_source(correct, problem, case) == (True, None)
    assert run_source("def delete_node(node):\n    node.next = node.next.next", problem, case) == (False, None)
    copied = '''def delete_node(node):
    value = node.next.val
    rest = node.next.next
    node.val = value
    node.next = ListNode(rest.val) if rest else None
'''
    assert run_source(copied, problem, case) == (False, None)
    rewrite = '''def delete_node(node):
    node.val = node.next.val
    node.next = node.next.next
    if node.next:
        node.next.val += 1
'''
    assert run_source(rewrite, problem, case) == (False, None)


def test_tree_references_are_real_source_nodes_and_returned_identity_preserves_tree():
    original = get_catalog()["leetcode-230"]
    signature = FunctionSignature(name="lca", parameters=[
        dict(name="root", annotation="TreeNode", adapter="treenode"),
        dict(name="p", annotation="TreeNode", adapter="treenode_ref", source_parameter=0),
        dict(name="q", annotation="TreeNode", adapter="treenode_ref", source_parameter=0),
    ], returns="TreeNode", return_adapter="treenode_value", node_policy="return_input_node")
    problem = original.model_copy(update={"signature": signature})
    root_case = Case(id="root-lca", arguments=[[6, 2, 8, 0, 4, 7, 9], 2, 8], expected=6)
    descendant_case = Case(id="node-self", arguments=[[6, 2, 8, 0, 4, 7, 9], 2, 4], expected=2)
    source = '''def lca(root, p, q):
    node = root
    low, high = sorted((p.val, q.val))
    while node:
        if node.val < low:
            node = node.right
        elif node.val > high:
            node = node.left
        else:
            return node
'''
    assert run_source(source, problem, root_case) == (True, None)
    assert run_source(source, problem, descendant_case) == (True, None)
    assert run_source("def lca(root, p, q):\n    return TreeNode(root.val)", problem, root_case) == (False, None)
    assert run_source("def lca(root, p, q):\n    root.left = None\n    return root", problem, root_case) == (False, None)
    duplicate = root_case.model_copy(update={"arguments": [[1, 1, 2], 1, 2], "expected": 1})
    passed, error = run_source(source, problem, duplicate)
    assert not passed and "exactly one" in error
    no_successor = root_case.model_copy(update={"arguments": [[2, 1, 3], 3, 1], "expected": None})
    assert run_source("def lca(root, p, q):\n    return None", problem, no_successor) == (True, None)
    assert run_source("def lca(root, p, q):\n    root.left = None\n    return None", problem, no_successor) == (False, None)


def test_equal_valued_nodes_still_require_correct_original_order():
    flatten = get_catalog()["leetcode-114"]
    case = Case(id="equal-tree", arguments=[[1, 1, 1]], expected=[1, None, 1, None, 1], expected_node_order=[0, 1, 2])
    assert run_source(flatten.reference_solution, flatten, case) == (True, None)
    assert run_source(RIGHT_FIRST_WRONG, flatten, case) == (False, None)
    # Without the position contract, the same all-one chain looks correct.
    assert run_source(RIGHT_FIRST_WRONG, flatten, case.model_copy(update={"expected_node_order": None})) == (True, None)
    reorder = get_catalog()["leetcode-143"]
    case = Case(id="equal-list", arguments=[[1, 1, 1, 1]], expected=[1, 1, 1, 1], expected_node_order=[0, 3, 1, 2])
    assert run_source(reorder.reference_solution, reorder, case) == (True, None)
    assert run_source("def reorder_list(head):\n    pass", reorder, case) == (False, None)


def test_node_mutations_reject_replacement_nodes_value_rewriting_and_returned_copies():
    reorder = get_catalog()["leetcode-143"]
    rewrite = '''def reorder_list(head):
    nodes = []
    current = head
    while current:
        nodes.append(current)
        current = current.next
    values = [node.val for node in nodes]
    values = [values[index] for index in sorted(range(len(values)), key=lambda i: (min(i, len(values)-1-i), i))]
    for node, value in zip(nodes, values):
        node.val = value
'''
    assert run_source(rewrite, reorder, reorder.tests[0]) == (False, None)
    flatten = get_catalog()["leetcode-114"]
    copied = '''def flatten_tree(root):
    if root is None:
        return
    values, stack = [], [root]
    while stack:
        node = stack.pop()
        values.append(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    root.left = None
    root.right = None
    tail = root
    for value in values[1:]:
        tail.right = TreeNode(value)
        tail = tail.right
'''
    case = flatten.tests[0]
    unchanged = json.dumps(case.arguments)
    assert run_source(copied, flatten, case) == (False, None)
    assert run_source(copied, flatten.model_copy(update={"signature": flatten.signature.model_copy(update={"node_policy": "values"})}),
                      case.model_copy(update={"expected_node_order": None})) == (True, None)
    assert run_source("def flatten_tree(root):\n    return TreeNode(1)", flatten, case) == (False, None)
    assert json.dumps(case.arguments) == unchanged
    ok, error = run_source("def flatten_tree(root):\n    root.right = root", flatten, case)
    assert not ok and "cycle" in error


def test_selected_mutation_parameter_scopes_original_node_tracking():
    original = get_catalog()["leetcode-143"]
    signature = FunctionSignature(name="change_second", parameters=[
        dict(name="first", annotation="ListNode", adapter="listnode"),
        dict(name="second", annotation="ListNode", adapter="listnode")],
        returns="None", result_mode="mutated_argument", mutated_parameter=1, node_policy="reuse_input_nodes")
    problem = original.model_copy(update={"signature": signature})
    case = Case(id="selected-nodes", arguments=[[9, 8], [1, 2, 3]], expected=[1, 3, 2], expected_node_order=[0, 2, 1])
    source = "def change_second(first, second):\n    middle = second.next\n    second.next = middle.next\n    second.next.next = middle\n    middle.next = None"
    assert run_source(source, problem, case) == (True, None)
    assert run_source(source.replace("second.next = middle.next", "second.next = first"), problem, case)[0] is False


def test_node_mutation_generators_domains_orders_and_weak_topic_priorities():
    for pid, spec in BATCH.items():
        rng = random.Random(4047 + pid)
        cases = [args for args, _ in spec["examples"]] + spec["boundaries"]
        cases += [args for args, _ in spec["stress"]]
        cases += [spec["generator"](rng) for _ in range(500)]
        for (values,) in cases:
            order = spec["node_order"]([values])
            if pid == 114:
                count = sum(value is not None for value in values)
                assert count <= 2000
                assert all(value is None or type(value) is int and -100 <= value <= 100 for value in values)
                # Count only structurally reachable values, not orphan entries.
                assert len(positions(values)) == count
                assert order == list(range(count))
            else:
                assert 1 <= len(values) <= 50000
                assert all(type(value) is int and 1 <= value <= 1000 for value in values)
                assert sorted(order) == list(range(len(values)))
                assert [values[index] for index in order] == spec["oracle"]([values])
        problem = get_catalog()[f"leetcode-{pid}"]
        assert review_focus_boost(problem) >= 60
        assert all(case.expected_node_order is not None for case in problem.tests)
        bad_order = problem.tests[0].model_copy(update={"expected_node_order": [1000000]})
        assert run_source(problem.reference_solution, problem, bad_order) == (False, None)
