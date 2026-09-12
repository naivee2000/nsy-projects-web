"""Tree traversal/path contracts and triangular dynamic programming.

JSON path-map ordering and exhaustive path enumeration serve as independent
oracles, rather than repeating the references' node recursion or tree DP.
"""
from itertools import product

from .import_batch_002 import positions, random_tree
from .import_batch_003 import entry


def inorder_oracle(args):
    mapping = positions(args[0])
    # In a ternary lexicographic key, left descendants precede a node's
    # terminating 1 and right descendants follow it.
    return [mapping[key] for key in sorted(mapping, key=lambda p: tuple(2 * side for side in p) + (1,))]


def preorder_oracle(args):
    mapping = positions(args[0])
    return [mapping[key] for key in sorted(mapping)]


def postorder_oracle(args):
    mapping = positions(args[0])
    return [mapping[key] for key in sorted(mapping, key=lambda p: p + (2,))]


def levels_by_position(values):
    mapping = positions(values)
    depths = sorted({len(key) for key in mapping})
    return [[mapping[key] for key in sorted(mapping) if len(key) == depth] for depth in depths]


def zigzag_oracle(args):
    return [row[::-1] if depth % 2 else row for depth, row in enumerate(levels_by_position(args[0]))]


def bottom_up_oracle(args):
    return levels_by_position(args[0])[::-1]


def paths_oracle(args):
    mapping, target = positions(args[0]), args[1]
    paths = []
    for key in sorted(mapping):
        if key + (0,) in mapping or key + (1,) in mapping:
            continue
        values = [mapping[key[:length]] for length in range(len(key) + 1)]
        if sum(values) == target:
            paths.append(values)
    return paths


def maximum_path_oracle(args):
    mapping = positions(args[0])
    adjacency = {key: [] for key in mapping}
    for key in mapping:
        if key:
            adjacency[key].append(key[:-1])
            adjacency[key[:-1]].append(key)
    # Enumerate every start/end pair's unique simple path; no subtree gains.
    best = max(mapping.values())
    for start in mapping:
        stack = [(start, None, 0)]
        while stack:
            current, parent, subtotal = stack.pop()
            subtotal += mapping[current]
            best = max(best, subtotal)
            stack.extend((other, current, subtotal) for other in adjacency[current] if other != parent)
    return best


def triangle_oracle(args):
    triangle = args[0]
    best = float("inf")
    for choices in product((0, 1), repeat=len(triangle) - 1):
        column, total = 0, triangle[0][0]
        for row, shift in enumerate(choices, 1):
            column += shift
            total += triangle[row][column]
        best = min(best, total)
    return best


def random_traversal(rng):
    return [random_tree(rng)]


def random_nonempty(rng):
    return [random_tree(rng, nonempty=True)]


def random_paths(rng):
    tree = random_tree(rng)
    mapping = positions(tree)
    leaves = [key for key in mapping if key + (0,) not in mapping and key + (1,) not in mapping]
    if leaves and rng.random() < .6:
        key = rng.choice(leaves)
        target = sum(mapping[key[:length]] for length in range(len(key) + 1))
    else:
        target = rng.randint(-1000, 1000)
    return [tree, target]


def random_triangle(rng):
    return [[[rng.randint(-100, 100) for _ in range(row)] for row in range(1, rng.randint(1, 9) + 1)]]


INORDER = '''\
def inorder_traversal(root):
    answer = []
    def visit(node):
        if node is None:
            return
        visit(node.left)
        answer.append(node.val)
        visit(node.right)
    visit(root)
    return answer
'''
PREORDER = '''\
def preorder_traversal(root):
    answer = []
    def visit(node):
        if node is None:
            return
        answer.append(node.val)
        visit(node.left)
        visit(node.right)
    visit(root)
    return answer
'''
POSTORDER = '''\
def postorder_traversal(root):
    answer = []
    def visit(node):
        if node is None:
            return
        visit(node.left)
        visit(node.right)
        answer.append(node.val)
    visit(root)
    return answer
'''
ZIGZAG = '''\
def zigzag_level_order(root):
    from collections import deque
    if root is None:
        return []
    queue, answer = deque([root]), []
    while queue:
        row = []
        for _ in range(len(queue)):
            node = queue.popleft()
            row.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        answer.append(row[::-1] if len(answer) % 2 else row)
    return answer
'''
BOTTOM = ZIGZAG.replace("zigzag_level_order", "bottom_up_level_order").replace(
    "answer.append(row[::-1] if len(answer) % 2 else row)", "answer.append(row)"
).replace("return answer", "return answer[::-1]")
PATHS = '''\
def path_sum_paths(root, target_sum):
    answer, path, subtotal = [], [], 0
    stack = [(root, False)]
    while stack:
        node, leaving = stack.pop()
        if node is None:
            continue
        if leaving:
            subtotal -= path.pop()
            continue
        path.append(node.val)
        subtotal += node.val
        if node.left is None and node.right is None and subtotal == target_sum:
            answer.append(path.copy())
        stack.extend([(node, True), (node.right, False), (node.left, False)])
    return answer
'''
MAXIMUM = '''\
def maximum_tree_path_sum(root):
    stack, gains, best = [(root, False)], {}, root.val
    while stack:
        node, visited = stack.pop()
        if node is None:
            continue
        if not visited:
            stack.extend([(node, True), (node.right, False), (node.left, False)])
        else:
            left = max(0, gains.pop(node.left, 0))
            right = max(0, gains.pop(node.right, 0))
            best = max(best, node.val + left + right)
            gains[node] = node.val + max(left, right)
    return best
'''
TRIANGLE = '''\
def triangle_minimum_total(triangle):
    costs = triangle[-1].copy()
    for row in range(len(triangle) - 2, -1, -1):
        for column in range(row + 1):
            costs[column] = triangle[row][column] + min(costs[column], costs[column + 1])
    return costs[0]
'''

TREE_HIDDEN = [[], [0], [-1], [1, 2], [1, None, 2], [1, 2, 3], [1, 2, None, 3],
               [1, None, 2, None, 3], [1, 2, 3, 4], [1, -2, 3], [0, 0, 0], [1, 2, 3, None, 4, 5]]


def mirror(source):
    return source.replace("node.left", "node.TEMP").replace("node.right", "node.left").replace("node.TEMP", "node.right")


def traversal(name, order, reference, wrong_order, oracle, first_explanation, second_explanation):
    return entry(name, [("root", "TreeNode | None")], "list[int]", ["trees", "recursion"],
        ["The tree has 0–100 nodes; -100 <= node.val <= 100. It is not necessarily a binary search tree.",
         f"Visit each node in {order} order. Return a flat list of values, retaining duplicates. An empty tree returns []."],
        [([[1, None, 2, 3]], first_explanation), ([[4, 2, 6, 1, 3, 5, 7]], second_explanation)],
        [[tree] for tree in TREE_HIDDEN], reference,
        [wrong_order.replace(wrong_order.split("def ", 1)[1].split("(", 1)[0], name), mirror(reference)],
        ["Places the root at the wrong point relative to its child subtrees.", "Visits the right subtree before the left subtree."],
        oracle, random_traversal,
        ["Treat a subtree as a smaller copy of the same traversal problem.",
         f"A missing node does nothing. For a present node, perform {order} in that order.",
         "Use one shared result list and a helper for a node; append its value at the required position among the two recursive calls.",
         "Values are not necessarily sorted. Structure and the visit order, not numerical magnitude, determine the result."],
        f"Apply {order} recursively at every node, doing nothing at a missing child. A shared output list avoids repeatedly copying subtree lists. Each node is appended once; recursion requires O(h) stack space, where h is height. At most 100 nodes keeps this reference within ordinary Python recursion limits. An explicit-stack implementation is also valid. The independent oracle never calls this traversal: it maps JSON nodes to binary position paths and sorts symbolic ordering keys.",
        "O(n)", "O(h) auxiliary; O(n) output", difficulty=3)


BATCH = {
    94: traversal("inorder_traversal", "left subtree → root → right subtree", INORDER, PREORDER, inorder_oracle,
        "The root 1 has no left child. Its right child 2 has left child 3, so visit 1, then 3, then 2.",
        "Read the left subtree as 1,2,3, then root 4, then the right subtree as 5,6,7."),
    144: traversal("preorder_traversal", "root → left subtree → right subtree", PREORDER, INORDER, preorder_oracle,
        "Visit root 1, then its right child 2, then 2's left child 3, giving [1,2,3].",
        "Visit 4 first, then the complete left subtree [2,1,3], then the right subtree [6,5,7]."),
    145: traversal("postorder_traversal", "left subtree → right subtree → root", POSTORDER, PREORDER, postorder_oracle,
        "Visit leaf 3 before its parent 2, then visit root 1 last, giving [3,2,1].",
        "Finish the left subtree as [1,3,2], the right as [5,7,6], and append root 4 last."),
    103: entry("zigzag_level_order", [("root", "TreeNode | None")], "list[list[int]]", ["trees", "breadth-first-search"],
        ["0–2000 nodes; values between -100 and 100.", "Return one list per depth: root level left-to-right, next level right-to-left, then alternate. An empty tree returns []."],
        [([[3, 9, 20, None, None, 15, 7]], "Level 0 is [3]. Reverse level 1 to [20,9], then read level 2 normally as [15,7]."),
         ([[1, 2, 3, 4, 5, 6, 7]], "Only the middle of these three levels reverses: [[1],[3,2],[4,5,6,7]].")],
        [[tree] for tree in TREE_HIDDEN], ZIGZAG,
        [ZIGZAG.replace("row[::-1] if len(answer) % 2 else row", "row"),
         ZIGZAG.replace("len(answer) % 2", "not len(answer) % 2")],
        ["Always uses left-to-right level order.", "Reverses the wrong parity of levels."], zigzag_oracle, random_traversal,
        ["Group nodes by depth before changing their display direction.", "Use a breadth-first queue and snapshot its length for each level.",
         "Read that many nodes, enqueue left then right children, and reverse the row only when its zero-based depth is odd.",
         "Keep the queue order consistent; alternating output direction does not require changing how the next level is discovered."],
        "Run standard breadth-first traversal, collecting one row at a time. Reverse only rows at odd depths. Queueing children left-to-right independently of display direction prevents one reversed row from corrupting later levels. Every node is processed and reversed at most once. The oracle groups binary position paths by their lengths, sorts positions within each depth, then applies the required parity.",
        "O(n)", "O(w) auxiliary; O(n) output", difficulty=5,
        stress=[([[0] + [None, 0] * 1999], [[0] for _ in range(2000)])]),
    107: entry("bottom_up_level_order", [("root", "TreeNode | None")], "list[list[int]]", ["trees", "breadth-first-search"],
        ["0–2000 nodes; values between -1000 and 1000.", "Return levels from deepest to shallowest while keeping values left-to-right inside each level. An empty tree returns []."],
        [([[3, 9, 20, None, None, 15, 7]], "The deepest row is [15,7], followed by [9,20], then [3]. Only the order of levels reverses."),
         ([[1, 2, 3, 4]], "The rows from deepest upward are [4], [2,3], [1]; node 3 stays with its own depth even though it is a leaf.")],
        [[tree] for tree in TREE_HIDDEN if tree != [1, 2, 3, 4]] + [[[8, None, 9]]], BOTTOM,
        [BOTTOM.replace("return answer[::-1]", "return answer"),
         BOTTOM.replace("return answer[::-1]", "return [row[::-1] for row in answer[::-1]]")],
        ["Returns top-down levels without reversing their order.", "Reverses values inside each level as well as reversing the levels."],
        bottom_up_oracle, random_traversal,
        ["Bottom-up depth order is not the same as visiting every leaf first.", "Build ordinary left-to-right breadth-first levels, then reverse the outer list.",
         "Pop one queue-width group at a time, append its values, enqueue children, and return levels[::-1].",
         "Do not reverse the values inside a row: the left-to-right requirement is unchanged."],
        "Group nodes by depth with a queue, retaining left-to-right order. Reversing only the completed list of rows changes depth order without changing within-level order. Nodes that are leaves at different depths do not belong in the same group. The oracle independently sorts position paths by depth and horizontal position.",
        "O(n)", "O(w) auxiliary; O(n) output", difficulty=5,
        stress=[([[0] + [None, 0] * 1999], [[0] for _ in range(2000)])]),
    113: entry("path_sum_paths", [("root", "TreeNode | None"), ("target_sum", "int")], "list[list[int]]", ["trees", "recursion", "backtracking"],
        ["0–5000 nodes; -1000 <= node.val, target_sum <= 1000.", "Return every root-to-leaf path whose values sum to target_sum. Preserve value order within a path; outer path order is unrestricted.",
         "Two different leaf paths may have identical values; include both. A leaf has no left or right child."],
        [([[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22], "Both [5,4,11,2] and [5,8,4,5] end at leaves and sum to 22."),
         ([[1, 2, 3], 5], "The only root-to-leaf sums are 3 and 4, so return []; the unrelated values 2 and 3 are not a root-to-leaf path.")],
        [[[], 0], [[0], 0], [[1], 0], [[-1], -1], [[1, 2], 1], [[1, None, 2], 3],
         [[0, 0, 0], 0], [[1, -2, 3], -1], [[1, 2, 3], 3], [[1, 2, 3], 4],
         [[5, -10, None, 5], 0], [[1, 2, None, 3, 4], 7]], PATHS,
        [PATHS.replace("node.left is None and node.right is None and subtotal", "subtotal"),
         PATHS.replace("answer.append(path.copy())", "answer.append(path)")],
        ["Accepts matching prefixes ending at an internal node.", "Stores the mutable working path without copying it, so later backtracking erases saved answers."],
        paths_oracle, random_paths,
        ["Track the complete current root-to-node path and its sum.", "Only a leaf may complete a qualifying path; negative values mean partial sums cannot safely prune branches.",
         "On entering a node, append its value and add it to the sum. Copy a matching leaf path. After its children, remove the node and subtract its value.",
         "Use explicit enter/leave frames to reproduce recursion safely for a 5000-node chain."],
        "Backtracking maintains one path and running sum. Entering a node extends them; leaving restores their prior state. Copy a matching path only at a leaf. Explicit enter/leave frames express recursive depth-first traversal without depending on Python's recursion limit. Duplicate value sequences from different leaves remain separate answers. With S total values in returned paths, time is O(n+S), while working frames and path use O(h) storage. The independent oracle enumerates leaf position keys and reconstructs each ancestor sequence.",
        "O(n + total returned path lengths)", "O(h) auxiliary plus output", difficulty=5,
        stress=[([[0] + [None, 0] * 4999, 0], [[0] * 5000])]),
    120: entry("triangle_minimum_total", [("triangle", "list[list[int]]")], "int", ["arrays", "dynamic-programming"],
        ["1–200 rows. Row i has i+1 integers, each between -10000 and 10000.", "Start at row 0, column 0. From column i move to column i or i+1 in the next row; reach the final row."],
        [([[[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]], "The adjacent choices 2→3→5→1 sum to 11, the minimum."),
         ([[[-10]]], "The top is already the bottom, so the only path has sum -10.")],
        [[[[0]]], [[[7]]], [[[1], [2, 3]]], [[[1], [3, 2]]], [[[0], [-1, -2]]],
         [[[1], [1, 100], [100, 100, -1000]]], [[[0], [0, 0], [0, 0, 0]]],
         [[[-1], [-2, -3], [-4, -5, -6]]], [[[5], [10, 1], [1, 1, 10]]],
         [[[2], [3, 4], [1, 100, 1]]], [[[10000], [-10000, 10000]]],
         [[[1], [2, 2], [3, 3, 3], [4, 4, 4, 4]]]], TRIANGLE,
        [TRIANGLE.replace("min(costs[column], costs[column + 1])", "max(costs[column], costs[column + 1])"),
         "def triangle_minimum_total(triangle):\n    return sum(min(row) for row in triangle)\n"],
        ["Maximizes the remaining path instead of minimizing it.", "Chooses the smallest value in each row independently, ignoring adjacency."],
        triangle_oracle, random_triangle,
        ["The cheapest child today may lead to expensive later rows; use the best complete suffix cost.",
         "Work upward from the bottom row using one row of costs.",
         "For row r and column c, set cost[c] to triangle[r][c]+min(cost[c],cost[c+1]); update columns left-to-right.",
         "Keep a copy of the last row so the input need not be modified; the final answer is cost[0]."],
        "A cell's optimal suffix cost is its value plus the smaller suffix cost of its two reachable children. Initialize costs from the last row and apply this recurrence upward. Left-to-right updates keep cost[c+1] from the row below until it is needed. Negative values are handled naturally because the triangle has no cycles. One row of memory suffices. The independent oracle enumerates every sequence of left/right moves on small generated triangles.",
        "O(r²), where r is the row count", "O(r)", difficulty=5,
        stress=[([[[10000] * width for width in range(1, 201)]], 2000000)]),
    124: entry("maximum_tree_path_sum", [("root", "TreeNode")], "int", ["trees", "recursion", "dynamic-programming"],
        ["1–30000 nodes; each value is between -1000 and 1000.", "Choose a nonempty simple path connected by tree edges. It may start and end anywhere, need not include the root, and cannot repeat a node."],
        [([[1, 2, 3]], "The best path is 2→1→3 and sums to 6. It may use both child branches around one turning node."),
         ([[-10, 9, 20, None, None, 15, 7]], "The best path 15→20→7 sums to 42 and stays entirely below the root.")],
        [[[0]], [[-3]], [[5]], [[-1, -2, -3]], [[1, -2, 3]], [[-5, 10]],
         [[2, -1]], [[1, 2, None, 3]], [[1, None, 2, None, 3]], [[-10, 2, 3, 4, 5]],
         [[10, 2, 3, 20, 30]], [[-1000, 1000, 1000]]], MAXIMUM,
        [MAXIMUM.replace("{}, root.val", "{}, 0"),
         MAXIMUM.replace("gains[node] = node.val + max(left, right)", "gains[node] = node.val + left + right")],
        ["Allows an empty zero-sum path, giving the wrong answer for all-negative trees.",
         "Propagates both child branches to a parent, producing a branching subgraph rather than a simple path."],
        maximum_path_oracle, random_nonempty,
        ["Separate the best complete path from the one-branch gain that can extend to a parent.",
         "At a node, ignore negative child gains. A complete candidate may join both gains, but a parent can receive only the larger one.",
         "Postorder: best=max(best,node.val+left_gain+right_gain); return node.val+max(left_gain,right_gain) upward.",
         "Initialize the answer from a real node for all-negative inputs. An explicit postorder stack handles deep trees safely."],
        "Compute downward gains after both children. Negative gains are discarded because stopping at the current node is better. The best path whose highest node is current joins its two nonnegative gains with its value. Maximize this candidate across the tree. To its parent, however, a node can contribute only one child branch; propagating both creates an invalid fork. Initialize best to root.val, not zero. Explicit postorder frames and consumption of child gains keep storage proportional to height and avoid recursion-depth failure. The oracle constructs an undirected graph of binary positions and enumerates every start/end path independently.",
        "O(n)", "O(h)", difficulty=8,
        stress=[([[1] + [None, 1] * 29999], 30000)]),
}

for source_id, spec in BATCH.items():
    if source_id != 120:
        name, annotation, _ = spec["params"][0]
        spec["params"][0] = (name, annotation, "treenode")
BATCH[113]["comparator"] = "unordered"
BATCH[124]["prerequisites"] = ["trees", "recursion"]
