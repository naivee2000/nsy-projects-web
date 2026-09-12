import random
from itertools import product

from code_practice.catalog import get_catalog
from code_practice.content_solutions import TreeNode
from code_practice.import_batch_014 import (
    BATCH, level_values, random_shape, regions_oracle, traversal_values,
)
from code_practice.learning import review_focus_boost
from code_practice.schemas import TestCase as Case
from code_practice.validation import run_source


def node_traversals(root):
    preorder, inorder, postorder, seen = [], [], [], set()
    stack = [(root, 0)]
    while stack:
        node, state = stack.pop()
        if node is None:
            continue
        if state == 0:
            assert isinstance(node, TreeNode) and id(node) not in seen
            seen.add(id(node))
            preorder.append(node.val)
            stack.extend([(node, 1), (node.left, 0)])
        elif state == 1:
            inorder.append(node.val)
            stack.extend([(node, 2), (node.right, 0)])
        else:
            postorder.append(node.val)
    return preorder, inorder, postorder


def test_tree_reconstruction_roundtrips_original_shapes_not_only_oracle_agreement():
    rng = random.Random(4047)
    for _ in range(500):
        tree = random_shape(rng)
        preorder, inorder, postorder = traversal_values(tree)
        expected = level_values(tree)
        for pid, args in ((105, [preorder, inorder]), (106, [inorder, postorder])):
            assert BATCH[pid]["oracle"](args) == expected
            problem = get_catalog()[f"leetcode-{pid}"]
            assert run_source(problem.reference_solution, problem,
                              Case(id="original-shape", arguments=args, expected=expected)) == (True, None)


def test_reconstruction_source_domains_deep_trees_and_traversal_contracts():
    for pid in (105, 106):
        spec = BATCH[pid]
        rng = random.Random(4047 + pid)
        arguments = [args for args, _ in spec["examples"]] + spec["boundaries"]
        arguments += [args for args, _ in spec["stress"]]
        arguments += [spec["generator"](rng) for _ in range(500)]
        namespace = {"TreeNode": TreeNode}
        exec(spec["reference"], namespace)
        for args in arguments:
            first, second = args
            assert 1 <= len(first) == len(second) <= 3000
            assert len(set(first)) == len(first) and set(first) == set(second)
            assert all(type(value) is int and -3000 <= value <= 3000 for value in first)
            actual = node_traversals(namespace[spec["name"]](*args))
            assert [actual[0], actual[1]] == args if pid == 105 else [actual[1], actual[2]] == args
        problem = get_catalog()[f"leetcode-{pid}"]
        assert problem.signature.return_adapter == "treenode"
        assert "class TreeNode" in problem.starter_code
        assert review_focus_boost(problem) >= 50


def reachable_boundary_oracle(board):
    """Check a separate reachability question from each O; no union-find."""
    rows, columns = len(board), len(board[0])
    answer = [row[:] for row in board]
    for row in range(rows):
        for column in range(columns):
            if board[row][column] != "O":
                continue
            pending, visited, escapes = [(row, column)], set(), False
            while pending:
                r, c = pending.pop()
                if (r, c) in visited:
                    continue
                visited.add((r, c))
                if r in (0, rows - 1) or c in (0, columns - 1):
                    escapes = True
                    break
                pending.extend((nr, nc) for nr, nc in ((r-1, c), (r+1, c), (r, c-1), (r, c+1))
                               if 0 <= nr < rows and 0 <= nc < columns and board[nr][nc] == "O")
            if not escapes:
                answer[row][column] = "X"
    return answer


def test_regions_all_512_three_by_three_boards_match_reachability():
    problem = get_catalog()["leetcode-130"]
    for cells in product("XO", repeat=9):
        board = [list(cells[index:index + 3]) for index in (0, 3, 6)]
        expected = reachable_boundary_oracle(board)
        assert regions_oracle([board]) == expected
        assert run_source(problem.reference_solution, problem,
                          Case(id="all-small-boards", arguments=[board], expected=expected)) == (True, None)


def test_regions_domain_inplace_contract_and_grid_review_priority():
    spec = BATCH[130]
    rng = random.Random(4047 + 130)
    cases = [args for args, _ in spec["examples"]] + spec["boundaries"]
    cases += [args for args, _ in spec["stress"]]
    cases += [spec["generator"](rng) for _ in range(500)]
    for (board,) in cases:
        assert 1 <= len(board) <= 200 and 1 <= len(board[0]) <= 200
        assert all(len(row) == len(board[0]) and set(row) <= set("XO") for row in board)
        if len(board) <= 9 and len(board[0]) <= 9:
            assert regions_oracle([board]) == reachable_boundary_oracle(board)
    problem = get_catalog()["leetcode-130"]
    assert problem.signature.result_mode == "mutated_argument"
    assert problem.signature.mutated_parameter == 0
    assert review_focus_boost(problem) >= 130
    case = Case(id="mutate-original", arguments=[[list("XXX"), list("XOX"), list("XXX")]],
                expected=[list("XXX") for _ in range(3)])
    returned_copy = 'def capture_regions(board):\n    return [["X"] * len(row) for row in board]\n'
    assert run_source(returned_copy, problem, case)[0] is False
