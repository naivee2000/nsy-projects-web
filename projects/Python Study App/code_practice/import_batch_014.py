"""Tree reconstruction and in-place surrounded regions with independent oracles."""
from collections import deque

from .import_batch_003 import entry


def level_values(tree):
    queue, result = deque([tree]), []
    while queue:
        node = queue.popleft()
        if node is None:
            result.append(None)
        else:
            result.append(node[0])
            queue.extend(node[1:])
    while result and result[-1] is None:
        result.pop()
    return result


def traversal_values(tree):
    if tree is None:
        return [], [], []
    value, left, right = tree
    lp, li, lo = traversal_values(left)
    rp, ri, ro = traversal_values(right)
    return [value] + lp + rp, li + [value] + ri, lo + ro + [value]


def cartesian_oracle(inorder, root_priority):
    # A Cartesian tree is ordered by inorder position and heap-ordered by root
    # visit rank. This deliberately does not mirror the reference's stack scan.
    priority = {value: index for index, value in enumerate(root_priority)}
    def segment(values):
        if not values:
            return None
        split = min(range(len(values)), key=lambda index: priority[values[index]])
        return values[split], segment(values[:split]), segment(values[split + 1:])
    return level_values(segment(inorder))


def preorder_build_oracle(args):
    preorder, inorder = args
    return cartesian_oracle(inorder, preorder)


def postorder_build_oracle(args):
    inorder, postorder = args
    return cartesian_oracle(inorder, postorder[::-1])


def random_shape(rng):
    values = rng.sample(range(-3000, 3001), rng.randint(1, 35))
    def grow(items):
        if not items:
            return None
        split = rng.randrange(len(items))
        return items[0], grow(items[1:split + 1]), grow(items[split + 1:])
    return grow(values)


def random_preorder_build(rng):
    preorder, inorder, _ = traversal_values(random_shape(rng))
    return [preorder, inorder]


def random_postorder_build(rng):
    _, inorder, postorder = traversal_values(random_shape(rng))
    return [inorder, postorder]


def regions_oracle(args):
    board = args[0]
    rows, columns = len(board), len(board[0])
    parent = list(range(rows * columns + 1))
    outside = rows * columns
    def root(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    def union(a, b):
        parent[root(a)] = root(b)
    for row in range(rows):
        for column in range(columns):
            if board[row][column] != "O":
                continue
            cell = row * columns + column
            if row in (0, rows - 1) or column in (0, columns - 1):
                union(cell, outside)
            for r, c in ((row + 1, column), (row, column + 1)):
                if r < rows and c < columns and board[r][c] == "O":
                    union(cell, r * columns + c)
    return [["O" if board[r][c] == "O" and root(r * columns + c) == root(outside) else "X"
             for c in range(columns)] for r in range(rows)]


def random_regions(rng):
    rows, columns = rng.randint(1, 9), rng.randint(1, 9)
    probability = rng.choice((.15, .4, .6, .85))
    return [[["O" if rng.random() < probability else "X" for _ in range(columns)] for _ in range(rows)]]


PRE_BUILD = '''\
def build_from_preorder(preorder, inorder):
    root = TreeNode(preorder[0])
    stack = [root]
    index = 0
    for value in preorder[1:]:
        node = stack[-1]
        child = TreeNode(value)
        if node.val != inorder[index]:
            node.left = child
        else:
            while stack and stack[-1].val == inorder[index]:
                node = stack.pop()
                index += 1
            node.right = child
        stack.append(child)
    return root
'''
POST_BUILD = '''\
def build_from_postorder(inorder, postorder):
    root = TreeNode(postorder[-1])
    stack = [root]
    index = len(inorder) - 1
    for value in reversed(postorder[:-1]):
        node = stack[-1]
        child = TreeNode(value)
        if node.val != inorder[index]:
            node.right = child
        else:
            while stack and stack[-1].val == inorder[index]:
                node = stack.pop()
                index -= 1
            node.left = child
        stack.append(child)
    return root
'''
BALANCED_WRONG = '''\
def NAME(PARAMS):
    def build(values):
        if not values:
            return None
        middle = len(values) // 2
        node = TreeNode(values[middle])
        node.left = build(values[:middle])
        node.right = build(values[middle + 1:])
        return node
    return build(inorder)
'''
REGIONS = '''\
def capture_regions(board):
    rows, columns = len(board), len(board[0])
    stack = []
    def protect(row, column):
        if 0 <= row < rows and 0 <= column < columns and board[row][column] == "O":
            board[row][column] = "#"
            stack.append((row, column))
    for row in range(rows):
        protect(row, 0)
        protect(row, columns - 1)
    for column in range(columns):
        protect(0, column)
        protect(rows - 1, column)
    while stack:
        row, column = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            protect(row + dr, column + dc)
    for row in range(rows):
        for column in range(columns):
            board[row][column] = "O" if board[row][column] == "#" else "X"
'''
INTERIOR_WRONG = '''\
def capture_regions(board):
    for row in range(1, len(board) - 1):
        for column in range(1, len(board[0]) - 1):
            board[row][column] = "X"
'''


def leaf(value):
    return value, None, None


SAMPLE_TREE = (3, leaf(9), (20, leaf(15), leaf(7)))
HIDDEN_TREES = [
    leaf(0), leaf(3000), leaf(-3000),
    (1, leaf(2), None), (1, None, leaf(2)), (2, leaf(1), leaf(3)),
    (1, (2, leaf(3), None), None), (1, None, (2, None, leaf(3))),
    (1, (2, None, leaf(3)), None), (1, None, (2, leaf(3), None)),
    (0, (-2, leaf(-3), leaf(-1)), (2, leaf(1), leaf(3))),
    (5, (8, None, leaf(-2)), (-7, leaf(3), None)),
]


def reconstruction_entry(pid):
    is_pre = pid == 105
    name = "build_from_preorder" if is_pre else "build_from_postorder"
    parameters = [("preorder", "list[int]"), ("inorder", "list[int]")] if is_pre else [("inorder", "list[int]"), ("postorder", "list[int]")]
    def arguments(tree):
        preorder, inorder, postorder = traversal_values(tree)
        return [preorder, inorder] if is_pre else [inorder, postorder]
    reference = PRE_BUILD if is_pre else POST_BUILD
    order = "preorder" if is_pre else "postorder"
    right_chain = [value for number in range(3000) for value in (number, None)][:-1]
    # Compact level-order for a right-only chain is value,null,value,null,...
    left_chain = [0] + [value for number in range(1, 3000) for value in (number, None)]
    left_chain.pop()
    ascending = list(range(3000))
    descending = ascending[::-1]
    spec = entry(name, parameters, "TreeNode | None", ["trees", "recursion", "stacks"],
        [f"The inorder and {order} traversals describe the same binary tree and each contains 1–3000 nodes.",
         "All node values are distinct integers between -3000 and 3000. The arrays contain the same values and form valid traversals.",
         "Return a TreeNode root, not a list. The judge displays and compares its level-order serialization, with null for missing children and trailing nulls omitted. The tree need not be balanced or a search tree."],
        [(arguments(SAMPLE_TREE), "The root is 3, its left child is 9, and its right subtree has root 20 with children 15 and 7. Missing children of 9 appear as null in the displayed result."),
         (arguments(leaf(-1)), "A single traversal value produces one TreeNode with value -1 and no children.")],
        [arguments(tree) for tree in HIDDEN_TREES], reference,
        [reference.replace(".left", ".temporary").replace(".right", ".left").replace(".temporary", ".right"),
         BALANCED_WRONG.replace("NAME", name).replace("PARAMS", ", ".join(n for n, _ in parameters))],
        ["Attaches the reconstructed subtrees to the opposite child sides.",
         "Builds a balanced tree from inorder alone, ignoring the root order in the other traversal."],
        preorder_build_oracle if is_pre else postorder_build_oracle,
        random_preorder_build if is_pre else random_postorder_build,
        [f"Inorder separates a root's left and right subtrees; {order} identifies which node is the root.",
         "Recursively split at each root in inorder. To handle a chain of 3000 nodes safely in Python, represent pending ancestors with an explicit stack.",
         ("Scan preorder forward. Attach left children until the stack top matches the next inorder value; pop completed ancestors, then attach a right child."
          if is_pre else "Scan postorder backward. Attach right children until the stack top matches the next reverse-inorder value; pop completed ancestors, then attach a left child."),
         "Unique values make each subtree split unambiguous. Every node is pushed and popped once; do not assume inorder is numerically sorted."],
        f"The recursive interpretation splits inorder around the root selected by {order}; the two sides are the left and right subproblems. The reference simulates this structure with a stack, avoiding Python call-stack overflow for skewed 3000-node trees. {'Forward preorder visits root then left then right; the inorder cursor marks completed left subtrees.' if is_pre else 'Reversed postorder visits root then right then left; a reverse-inorder cursor marks completed right subtrees.'} Once the cursor matches pending ancestors, pop them before attaching the next opposite-side child. The independent oracle instead forms a Cartesian tree: inorder positions fix the node order and root-visit ranks determine each segment minimum. Generated trees are also checked against their original shape, not only oracle agreement. O(n) time includes input scanning and node creation; O(n) auxiliary space includes the traversal slice and stack, in addition to n output nodes.",
        "O(n)", "O(n), plus the returned tree", difficulty=5,
        stress=[([ascending, ascending] if is_pre else [ascending, descending], right_chain),
                ([ascending, descending] if is_pre else [descending, descending], left_chain)])
    spec["adapter"] = "treenode"
    return spec


def grid(*rows):
    return [list(row) for row in rows]


BATCH = {105: reconstruction_entry(105), 106: reconstruction_entry(106)}
BATCH[130] = entry("capture_regions", [("board", "list[list[str]]")], "None",
    ["matrices", "graphs", "recursion"],
    ["The rectangular board has 1–200 rows and 1–200 columns and contains only 'X' and 'O'.",
     "Only horizontal and vertical neighbors connect. Any O region connected to any board edge stays O, even if some of its cells are far inside the board. Diagonal contact does not connect regions.",
     "Change surrounded O cells to X in the original board. Return nothing; the judge checks the mutated board, not a returned copy."],
    [([grid("XXXX", "XOOX", "XXOX", "XOXX")], "The three interior O cells have no route to an edge and become X. The bottom-row O touches the edge and stays O."),
     ([grid("XOXX", "XOOX", "XXOX", "XXXX")], "All O cells connect through up/down/left/right steps to the top-edge O, so the entire region stays unchanged.")],
    [[board] for board in (grid("X"), grid("O"), grid("OOO"), grid("O", "O", "O"),
                           grid("XX", "XX"), grid("OO", "OO"), grid("XXX", "XOX", "XXX"),
                           grid("OXX", "XOX", "XXX"), grid("XXX", "XOX", "XXO"),
                           grid("XXXXX", "XOOOX", "XXXXX"), grid("XXXXX", "OOOOX", "XXXXX"),
                           grid("XXXXXXX", "XOXOOOX", "XOXXXXX", "XOXXXXX"))],
    REGIONS,
    [INTERIOR_WRONG, REGIONS.replace("((1, 0), (-1, 0), (0, 1), (0, -1))",
                                    "((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))")],
    ["Captures every interior O even when its region connects to an edge.",
     "Treats diagonal O cells as connected and incorrectly preserves surrounded regions."],
    regions_oracle, random_regions,
    ["Ask which O cells cannot be captured: those connected to an edge.",
     "Flood-fill from every edge O and temporarily mark all reachable O cells as protected.",
     "Push unmarked edge O cells, repeatedly mark/push their four O neighbors, then restore marked cells to O and change remaining O cells to X.",
     "Mark before pushing so each cell is processed once. Use an explicit stack for large grids; recursive DFS expresses the same idea but can exceed Python's recursion limit."],
    "A region is captured exactly when it has no path to the boundary. Reverse the question and explore only safe regions from all edge cells. The reference uses an explicit DFS stack and a temporary marker in the original board, then performs one final in-place sweep. This handles a 200×200 connected region without Python recursion overflow. The independent oracle does no boundary flood-fill: it unions adjacent O cells in a disjoint-set structure with an outside sentinel, then queries connectivity. This differs from island counting and flood-fill recoloring: only fully enclosed regions change, no seed cell is supplied, and the input board itself is the graded output.",
    "O(rows × columns)", "O(rows × columns) for the explicit stack", difficulty=5,
    stress=[([[list("O" * 200) for _ in range(200)]], [list("O" * 200) for _ in range(200)]),
            ([[list("X" * 200)] + [list("X" + "O" * 198 + "X") for _ in range(198)] + [list("X" * 200)]],
             [list("X" * 200) for _ in range(200)])])
BATCH[130]["result_mode"] = "mutated_argument"
BATCH[130]["mutated_parameter"] = 0
