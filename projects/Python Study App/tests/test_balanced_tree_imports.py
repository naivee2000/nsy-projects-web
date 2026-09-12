from functools import lru_cache
from itertools import product
import random

import pytest

from code_practice.catalog import get_catalog
from code_practice.content_solutions import TreeNode
from code_practice.import_batch_002 import positions
from code_practice.import_batch_014 import level_values
from code_practice.import_batch_019 import BATCH, complete_bst_oracle
from code_practice.learning import review_focus_boost
from code_practice.schemas import ProblemDefinition, TestCase as Case, analyze_integer_tree
from code_practice.validation import _treenode, compare, run_source


def cases(pid):
    spec = BATCH[pid]
    rng = random.Random(4047 + pid)
    return ([args for args, _ in spec["examples"]] + spec["boundaries"]
            + [args for args, _ in spec["stress"]] + [spec["generator"](rng) for _ in range(500)])


def test_balanced_tree_imports_preserve_source_input_domains():
    for pid in BATCH:
        for (values,) in cases(pid):
            if pid == 108:
                assert 1 <= len(values) <= 10000
                assert values == sorted(set(values))
                assert all(type(v) is int and -10000 <= v <= 10000 for v in values)
            elif pid == 109:
                assert len(values) <= 20000 and values == sorted(values)
                assert all(type(v) is int and -100000 <= v <= 100000 for v in values)
            elif pid == 222:
                assert len(values) <= 50000
                assert all(type(v) is int and 0 <= v <= 50000 for v in values)
                # No gaps: the encoded tree is complete, not an arbitrary tree.
                assert len(positions(values)) == len(values)
            else:
                assert sum(v is not None for v in values) <= 1000
                assert all(v is None or (type(v) is int and -1000 <= v <= 1000) for v in values)
                assert len(positions(values)) == sum(v is not None for v in values)


@lru_cache(None)
def shapes(size):
    if size == 0:
        return (None,)
    return tuple((left, right) for split in range(size)
                 for left in shapes(split) for right in shapes(size - split - 1))


def shape_height_and_balance(shape):
    if shape is None:
        return 0, True
    a, left_ok = shape_height_and_balance(shape[0])
    b, right_ok = shape_height_and_balance(shape[1])
    return 1 + max(a, b), left_ok and right_ok and abs(a - b) <= 1


def labelled_shape(shape, iterator):
    if shape is None:
        return None
    left = labelled_shape(shape[0], iterator)
    value = next(iterator)
    return value, left, labelled_shape(shape[1], iterator)


def test_property_comparator_exhausts_all_626_shapes_up_to_seven_nodes():
    checked = accepted = 0
    for size in range(8):
        values = list(range(size))
        expected = complete_bst_oracle([values])
        for shape in shapes(size):
            actual = level_values(labelled_shape(shape, iter(values)))
            correct = shape_height_and_balance(shape)[1]
            assert compare(actual, expected, "balanced_bst") == correct
            assert analyze_integer_tree(actual) == (values, correct)
            accepted += correct
            checked += 1
    assert checked == 626 and accepted > 8  # Multiple accepted shapes, not one per size.


@pytest.mark.parametrize("bad", [None, {}, [None], [True], [1.0], ["1"], [1, None, None, 2], [1, None, None, None]])
def test_tree_property_parser_rejects_malformed_or_noninteger_encodings(bad):
    assert analyze_integer_tree(bad) is None
    assert not compare(bad, [1], "balanced_bst")


def test_property_comparator_checks_order_multiplicity_and_every_subtree():
    assert compare([1, None, 3], [3, 1], "balanced_bst")
    assert compare([3, 1], [1, None, 3], "balanced_bst")
    assert not compare([1, 3], [3, 1], "balanced_bst")  # Same multiset, not a BST.
    assert not compare([2, 1], [2, 1, 2], "balanced_bst")
    assert compare([2, 1, 2], [2, 1, 2], "balanced_bst")
    # The root has equally tall sides; both descendants are unbalanced chains.
    nested = (4, (3, (2, (1, None, None), None), None),
              (5, None, (6, None, (7, None, None))))
    assert not compare(level_values(nested), complete_bst_oracle([list(range(1, 8))]), "balanced_bst")
    assert not compare([0, None] * 19999 + [0], [0] * 20000, "balanced_bst")


def test_schema_requires_sorted_inputs_matching_valid_noncanonical_expectations():
    problem = get_catalog()["leetcode-108"]
    for change in ("unsorted", "missing", "unbalanced", "raw-output", "mixed", "tree-input"):
        payload = problem.model_dump(mode="json")
        first = payload["tests"][0]
        if change == "unsorted":
            first["arguments"][0].reverse()
        elif change == "missing":
            first["expected"] = [0]
        elif change == "unbalanced":
            first["expected"] = [-10, None, -3, None, 0, None, 5, None, 9]
        elif change == "raw-output":
            payload["signature"]["return_adapter"] = "raw"
        elif change == "mixed":
            first["comparator"] = "exact"
        else:
            payload["signature"]["parameters"][0]["adapter"] = "treenode"
        with pytest.raises(ValueError, match="Balanced-BST"):
            ProblemDefinition.model_validate(payload)


def test_returned_trees_require_real_integer_nodes_and_allow_alternative_shapes():
    problem = get_catalog()["leetcode-108"]
    case = Case(id="alternate", arguments=[[1, 3]], expected=[3, 1], comparator="balanced_bst")
    assert run_source("def sorted_array_bst(nums):\n    return TreeNode(1, None, TreeNode(3))", problem, case) == (True, None)
    assert run_source("def sorted_array_bst(nums):\n    return TreeNode(1, TreeNode(3))", problem, case) == (False, None)
    for source, text in [
        ("def sorted_array_bst(nums):\n    return TreeNode(True)", "integer values"),
        ("def sorted_array_bst(nums):\n    root = TreeNode(1)\n    root.right = root\n    return root", "cycle"),
        ("def sorted_array_bst(nums):\n    child = TreeNode(1)\n    return TreeNode(3, child, child)", "shared child"),
        ("def sorted_array_bst(nums):\n    return [3,1]", "AttributeError"),
    ]:
        ok, error = run_source(source, problem, case)
        assert not ok and text in error
    empty = get_catalog()["leetcode-109"]
    case = Case(id="empty", arguments=[[]], expected=[], comparator="balanced_bst")
    assert run_source("def sorted_list_bst(head):\n    return None", empty, case) == (True, None)
    ok, error = run_source("def sorted_list_bst(head):\n    return TreeNode(None)", empty, case)
    assert not ok and "integer values" in error


def test_complete_tree_reference_has_log_squared_link_reads():
    class CountedNode:
        reads = 0

        def __init__(self):
            self.val = 0
            self._left = self._right = None

        @property
        def left(self):
            CountedNode.reads += 1
            return self._left

        @property
        def right(self):
            CountedNode.reads += 1
            return self._right

    namespace = {}
    exec(BATCH[222]["reference"], namespace)
    for size in list(range(1025)) + [32767, 32768, 49999, 50000]:
        nodes = [CountedNode() for _ in range(size)]
        for index, node in enumerate(nodes):
            node._left = nodes[2 * index + 1] if 2 * index + 1 < size else None
            node._right = nodes[2 * index + 2] if 2 * index + 2 < size else None
        CountedNode.reads = 0
        assert namespace["count_complete_nodes"](nodes[0] if nodes else None) == size
        assert CountedNode.reads <= 2 * (size.bit_length() + 1)**2


def test_univalue_counts_match_direct_descendant_enumeration():
    namespace = {"TreeNode": TreeNode}
    exec(BATCH[250]["reference"], namespace)
    def brute(root):
        if root is None:
            return [], 0
        left, a = brute(root.left)
        right, b = brute(root.right)
        values = left + [root.val] + right
        return values, a + b + int(all(value == root.val for value in values))
    for values in product((0, 1), repeat=7):
        root = _treenode(values)
        expected = brute(root)[1]
        assert namespace["count_univalue_subtrees"](root) == expected
        assert BATCH[250]["oracle"]([values]) == expected
    assert namespace["count_univalue_subtrees"](_treenode([1, 1, 1, 2])) == 2


def test_new_tree_and_list_exercises_keep_weak_topic_review_boosts():
    for pid, minimum in ((108, 50), (109, 60), (222, 60), (250, 50)):
        assert review_focus_boost(get_catalog()[f"leetcode-{pid}"]) >= minimum
    starter = get_catalog()["leetcode-109"].starter_code
    assert "class ListNode" in starter and "class TreeNode" in starter
