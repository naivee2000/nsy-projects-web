"""Tree references, preorder validation, triples, graphs, number sequences, and DP."""
from collections import Counter, deque
from heapq import heappop, heappush
from itertools import combinations, product
from math import comb

from .import_batch_003 import entry


def tree_positions(values):
    """Represent a compact level-order tree as binary paths, without TreeNode objects."""
    if not values:
        return {}
    mapping, queue, index = {(): values[0]}, deque([()]), 1
    while queue and index < len(values):
        parent = queue.popleft()
        for side in (0, 1):
            if index >= len(values):
                break
            value = values[index]
            index += 1
            if value is not None:
                path = parent + (side,)
                mapping[path] = value
                queue.append(path)
    return mapping


def flatten_tree(mapping):
    if not mapping:
        return []
    values, queue = [], deque([()])
    while queue:
        path = queue.popleft()
        values.append(mapping.get(path))
        if path in mapping:
            queue.extend((path + (0,), path + (1,)))
    while values and values[-1] is None:
        values.pop()
    return values


def lca_oracle(args):
    values, first, second = args
    mapping = tree_positions(values)
    paths = {value: path for path, value in mapping.items()}
    left, right = paths[first], paths[second]
    shared = 0
    while shared < min(len(left), len(right)) and left[shared] == right[shared]:
        shared += 1
    return mapping[left[:shared]]


def preorder_oracle(args):
    def valid(values):
        if len(values) < 2:
            return True
        root = values[0]
        split = next((index for index, value in enumerate(values[1:], 1) if value > root), len(values))
        return (all(value < root for value in values[1:split])
                and all(value > root for value in values[split:])
                and valid(values[1:split]) and valid(values[split:]))
    return valid(args[0])


def tree_paths_oracle(args):
    mapping = tree_positions(args[0])
    answers = []
    for path in mapping:
        if path + (0,) in mapping or path + (1,) in mapping:
            continue
        answers.append("->".join(str(mapping[path[:depth]]) for depth in range(len(path) + 1)))
    return answers


def three_sum_smaller_oracle(args):
    nums, target = args
    return sum(sum(nums[index] for index in chosen) < target
               for chosen in combinations(range(len(nums)), 3))


def two_singles_oracle(args):
    return [value for value, count in Counter(args[0]).items() if count == 1]


def valid_tree_oracle(args):
    node_count, edges = args
    if len(edges) != node_count - 1:
        return False
    reached = {0}
    while True:
        expanded = reached | {
            right if left in reached else left
            for left, right in edges
            if (left in reached) != (right in reached)
        }
        if expanded == reached:
            return len(reached) == node_count
        reached = expanded


def ugly_values(limit=2**31 - 1):
    values = set()
    power_two = 1
    while power_two <= limit:
        power_three = power_two
        while power_three <= limit:
            value = power_three
            while value <= limit:
                values.add(value)
                value *= 5
            power_three *= 3
        power_two *= 2
    return tuple(sorted(values))


UGLY_VALUES = ugly_values()
UGLY_SET = set(UGLY_VALUES)


def ugly_oracle(args):
    return args[0] in UGLY_SET


def nth_ugly_oracle(args):
    target = args[0]
    heap, seen = [1], {1}
    for _ in range(target - 1):
        value = heappop(heap)
        for factor in (2, 3, 5):
            candidate = value * factor
            if candidate not in seen:
                seen.add(candidate)
                heappush(heap, candidate)
    return heap[0]


def paint_oracle(args):
    costs = args[0]
    return min(sum(costs[house][color] for house, color in enumerate(colors))
               for colors in product(range(len(costs[0])), repeat=len(costs))
               if all(colors[index] != colors[index - 1] for index in range(1, len(colors))))


def paint_dp_oracle(costs):
    previous = costs[0][:]
    for row in costs[1:]:
        previous = [cost + min(previous[other] for other in range(len(row)) if other != color)
                    for color, cost in enumerate(row)]
    return min(previous)


def random_bst_lca(rng):
    values = rng.sample(range(-1000, 1001), rng.randint(2, 30))
    mapping = {}
    for value in values:
        path = ()
        while path in mapping:
            path += (0 if value < mapping[path] else 1,)
        mapping[path] = value
    first, second = rng.sample(values, 2)
    return [flatten_tree(mapping), first, second]


def random_tree_lca(rng):
    values = rng.sample(range(-1000, 1001), rng.randint(2, 30))
    mapping, slots = {(): values[0]}, [((), 0), ((), 1)]
    for value in values[1:]:
        parent, side = slots.pop(rng.randrange(len(slots)))
        path = parent + (side,)
        mapping[path] = value
        slots.extend(((path, 0), (path, 1)))
    first, second = rng.sample(values, 2)
    return [flatten_tree(mapping), first, second]


def random_preorder(rng):
    return [rng.sample(range(1, 101), rng.randint(1, 10))]


def random_path_tree(rng):
    node_count = rng.randint(1, 20)
    mapping, slots = {(): rng.randint(-5, 5)}, [((), 0), ((), 1)]
    for _ in range(node_count - 1):
        parent, side = slots.pop(rng.randrange(len(slots)))
        path = parent + (side,)
        mapping[path] = rng.randint(-5, 5)
        slots.extend(((path, 0), (path, 1)))
    return [flatten_tree(mapping)]


def random_three_sum_smaller(rng):
    return [[rng.randint(-10, 10) for _ in range(rng.randint(0, 10))], rng.randint(-12, 12)]


def random_two_singles(rng):
    pair_count = rng.randint(0, 10)
    values = rng.sample(range(-100, 101), pair_count + 2)
    nums = values[:2] + [value for value in values[2:] for _ in range(2)]
    rng.shuffle(nums)
    return [nums]


def random_graph(rng):
    node_count = rng.randint(1, 10)
    possible = [[left, right] for left in range(node_count) for right in range(left + 1, node_count)]
    edge_count = rng.randint(0, min(len(possible), 15))
    edges = rng.sample(possible, edge_count)
    edges = [[right, left] if rng.random() < .5 else [left, right] for left, right in edges]
    return [node_count, edges]


def random_ugly(rng):
    if rng.random() < .35:
        return [rng.choice(UGLY_VALUES)]
    return [rng.randint(-(2**31), 2**31 - 1)]


def random_nth_ugly(rng):
    return [rng.randint(1, 100)]


def random_paint(rng):
    colors = rng.randint(2, 4)
    return [[[rng.randint(1, 20) for _ in range(colors)] for _ in range(rng.randint(1, 5))]]


def right_chain(node_count):
    values = [0]
    for value in range(1, node_count):
        values.extend((None, value))
    return values


BST_LCA = '''\
def lowest_common_ancestor_bst(root, p, q):
    low, high = sorted((p.val, q.val))
    current = root
    while current:
        if current.val < low:
            current = current.right
        elif current.val > high:
            current = current.left
        else:
            return current
'''

TREE_LCA = '''\
def lowest_common_ancestor(root, p, q):
    parent = {root: None}
    stack = [root]
    while p not in parent or q not in parent:
        node = stack.pop()
        if node.left:
            parent[node.left] = node
            stack.append(node.left)
        if node.right:
            parent[node.right] = node
            stack.append(node.right)
    ancestors = set()
    current = p
    while current is not None:
        ancestors.add(current)
        current = parent[current]
    current = q
    while current not in ancestors:
        current = parent[current]
    return current
'''

VERIFY_PREORDER = '''\
def verify_bst_preorder(preorder):
    lower = float("-inf")
    stack = []
    for value in preorder:
        if value < lower:
            return False
        while stack and value > stack[-1]:
            lower = stack.pop()
        stack.append(value)
    return True
'''

TREE_PATHS = '''\
def binary_tree_paths(root):
    answers = []
    def visit(node, path):
        path.append(str(node.val))
        if node.left is None and node.right is None:
            answers.append("->".join(path))
        else:
            if node.left:
                visit(node.left, path)
            if node.right:
                visit(node.right, path)
        path.pop()
    visit(root, [])
    return answers
'''

THREE_SUM_SMALLER = '''\
def three_sum_smaller(nums, target):
    ordered = sorted(nums)
    count = 0
    for left in range(len(ordered) - 2):
        middle, right = left + 1, len(ordered) - 1
        while middle < right:
            if ordered[left] + ordered[middle] + ordered[right] < target:
                count += right - middle
                middle += 1
            else:
                right -= 1
    return count
'''

SINGLE_NUMBER_THREE = '''\
def single_number_three(nums):
    combined = 0
    for value in nums:
        combined ^= value
    distinguishing_bit = combined & -combined
    first = second = 0
    for value in nums:
        if value & distinguishing_bit:
            first ^= value
        else:
            second ^= value
    return [first, second]
'''

GRAPH_TREE = '''\
def is_valid_tree(n, edges):
    if len(edges) != n - 1:
        return False
    parent = list(range(n))
    size = [1] * n
    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    for left, right in edges:
        first, second = find(left), find(right)
        if first == second:
            return False
        if size[first] < size[second]:
            first, second = second, first
        parent[second] = first
        size[first] += size[second]
    return True
'''

UGLY = '''\
def is_ugly_number(n):
    if n <= 0:
        return False
    for factor in (2, 3, 5):
        while n % factor == 0:
            n //= factor
    return n == 1
'''

NTH_UGLY = '''\
def nth_ugly_number(n):
    values = [1] * n
    two = three = five = 0
    for index in range(1, n):
        next_value = min(values[two] * 2, values[three] * 3, values[five] * 5)
        values[index] = next_value
        while values[two] * 2 <= next_value:
            two += 1
        while values[three] * 3 <= next_value:
            three += 1
        while values[five] * 5 <= next_value:
            five += 1
    return values[-1]
'''

PAINT_HOUSE_TWO = '''\
def minimum_paint_cost_many_colors(costs):
    previous = costs[0][:]
    for row in costs[1:]:
        least = second = float("inf")
        least_color = -1
        for color, value in enumerate(previous):
            if value < least:
                second = least
                least = value
                least_color = color
            elif value < second:
                second = value
        previous = [cost + (second if color == least_color else least)
                    for color, cost in enumerate(row)]
    return min(previous)
'''


LCA_ROOT = '''\
def {name}(root, p, q):
    return root
'''
LCA_P = '''\
def {name}(root, p, q):
    return p
'''

large_paint = [[1 + (house * 7 + color * 3) % 20 for color in range(20)] for house in range(100)]


BATCH = {
    235: entry("lowest_common_ancestor_bst", [("root", "TreeNode"), ("p", "TreeNode"), ("q", "TreeNode")], "TreeNode", ["trees", "binary-search", "binary-search-trees"],
        ["The input contains 2–100 TreeNode objects with unique values from -10^9 through 10^9, arranged as a binary search tree.", "p and q are different existing nodes selected by their values. Return the actual lowest common ancestor node from root; a node is its own descendant, and the input tree must remain unchanged."],
        [([[6,2,8,0,4,7,9,None,None,3,5],2,8], "Nodes 2 and 8 lie on opposite sides of 6, so the existing root node is their lowest common ancestor."), ([[6,2,8,0,4,7,9,None,None,3,5],2,4], "Node 2 is an ancestor of node 4 and counts as its own descendant, so return the existing node 2.")],
        [[tree, p, q] for tree, p, q in (([2,1],2,1),([2,1,3],1,3),([5,3,7,2,4,6,8],2,4),([5,3,7,2,4,6,8],6,8),([5,3,7,2,4,6,8],2,8),([0,-2,3,-4,-1,2,5],-4,-1),([0,-2,3,-4,-1,2,5],-1,2),([10,5,None,2,7],2,7),([1,None,2,None,3,None,4],2,4),([4,3,None,2,None,1],4,1),([8,4,12,2,6,10,14,1,3,5,7,9,11,13,15],9,11),([8,4,12,2,6,10,14,1,3,5,7,9,11,13,15],1,15))],
        BST_LCA, [LCA_ROOT.format(name="lowest_common_ancestor_bst"), LCA_P.format(name="lowest_common_ancestor_bst")],
        ["Always returns the root, even when both selected nodes lie inside a lower subtree.", "Always returns p, even when p is not an ancestor of q."], lca_oracle, random_bst_lca,
        ["BST ordering tells you which single side can still contain both selected values.", "If both values are smaller, move left; if both are larger, move right.", "Stop at the first node whose value lies between p.val and q.val, including either endpoint.", "Return that existing TreeNode, not a newly created node with the same value."],
        "Walk down from the root while both targets remain strictly on one side. The first split point, or the first selected node encountered, is the deepest node containing both targets. The judge passes p and q as actual references within root and requires the returned identity while confirming that no link or value changed. The independent oracle finds both binary paths in the compact input and takes their longest common prefix.", "O(h)", "O(1)", difficulty=5,
        stress=[([right_chain(12),4,11],4)]),
    236: entry("lowest_common_ancestor", [("root", "TreeNode"), ("p", "TreeNode"), ("q", "TreeNode")], "TreeNode", ["trees", "depth-first-search", "lowest-common-ancestor"],
        ["The input contains 2–100 TreeNode objects with unique values from -10^9 through 10^9; it is an arbitrary binary tree, not necessarily a search tree.", "p and q are different existing nodes selected by their values. Return their actual lowest common ancestor node, counting a node as its own descendant, without changing the input tree."],
        [([[3,5,1,6,2,0,8,None,None,7,4],5,1], "Nodes 5 and 1 occupy different root subtrees, so their lowest common ancestor is the existing node 3."), ([[3,5,1,6,2,0,8,None,None,7,4],5,4], "Node 5 contains node 4 in its subtree and counts as its own descendant, so the answer is node 5.")],
        [[tree,p,q] for tree,p,q in (([1,2],1,2),([1,2,3],2,3),([1,2,3,4,5],4,5),([1,2,3,4,5],4,3),([1,2,None,3,None,4],3,4),([1,None,2,None,3,None,4],2,4),([0,-1,1,-2,None,None,2],-2,2),([8,4,12,2,6,10,14],2,6),([8,4,12,2,6,10,14],6,10),([5,1,9,None,3,7,11,2,4],2,4),([5,1,9,None,3,7,11,2,4],1,4),([5,1,9,None,3,7,11,2,4],4,7))],
        TREE_LCA, [LCA_ROOT.format(name="lowest_common_ancestor"), LCA_P.format(name="lowest_common_ancestor")],
        ["Always returns the root, missing lower common ancestors within one subtree.", "Always returns p, even when p is not an ancestor of q."], lca_oracle, random_tree_lca,
        ["You need a way to move upward from both selected nodes even though TreeNode has no parent field.", "Traverse once to record each visited node's parent until both p and q have been found.", "Collect p and all of its ancestors, then move q upward until it enters that set.", "Use node identity, not only values; return the actual shared ancestor from root and do not alter the tree."],
        "An iterative traversal builds parent links only until both selected object references are discovered. Every ancestor of p is placed in a set; the first ancestor reached while climbing from q is the lowest shared one. A recursive approach also fits the stated tree size. The independent oracle compares the targets' binary paths rather than constructing parent pointers.", "O(n)", "O(n)", difficulty=5,
        stress=[([right_chain(12),4,11],4)]),
    255: entry("verify_bst_preorder", [("preorder", "list[int]")], "bool", ["arrays", "stacks", "binary-search-trees"],
        ["preorder contains 1–10000 unique integers from 1 through 10000.", "Return whether preorder could be the root-left-right traversal of a binary search tree with strict ordering. You do not need to construct the tree."],
        [([[5,2,1,3,6]], "Five is the root; [2,1,3] is a valid left-subtree preorder and [6] is its valid right subtree."), ([[5,2,6,1,3]], "After traversal enters the right subtree at 6, the later value 1 cannot return below root 5, so this order is invalid.")],
        [[values] for values in ([1],[1,2],[2,1],[8,5,1,7,10,12],[8,10,5],[5,4,3,2,1],[1,2,3,4,5],[10,5,1,7,40,50],[10,5,1,40,7,50],[5,2,1,3,7,6,8],[5,2,4,1,6],[3,1,2,5,4,6])],
        VERIFY_PREORDER, ['def verify_bst_preorder(preorder):\n    return len(preorder) == len(set(preorder))\n', VERIFY_PREORDER.replace("while stack and value > stack[-1]:", "if stack and value > stack[-1]:")],
        ["Checks only uniqueness and accepts orders that violate a previously completed ancestor's lower bound.", "Pops only one completed ancestor instead of all smaller ancestors, so it retains an obsolete lower bound."], preorder_oracle, random_preorder,
        ["Once preorder moves into a right subtree, later values cannot fall below that ancestor.", "Use a decreasing stack of open ancestors and one lower bound.", "Reject value<lower; while value exceeds the stack top, pop and replace lower; then push value.", "The stack simulates ancestor ranges without building TreeNode objects."],
        "The stack contains ancestors whose right subtree has not yet been entered. A larger value completes one or more left-subtree chains; the last popped value becomes a permanent lower bound. Any later value below it is invalid. The independent oracle recursively divides each short generated sequence at its first value greater than the root and verifies both strict partitions.", "O(n)", "O(n)", difficulty=5,
        stress=[([list(range(1,10001))],True)]),
    257: entry("binary_tree_paths", [("root", "TreeNode | None")], "list[str]", ["trees", "recursion", "depth-first-search"],
        ["root contains 1–100 TreeNode objects with values from -100 through 100.", "Return every root-to-leaf path as values joined by '->'. A leaf has neither child; output order does not matter."],
        [([[1,2,3,None,5]], "The leaves are 5 and 3, producing the complete paths 1->2->5 and 1->3."), ([[1]], "The root is also the only leaf, so the only complete path is the one-value string '1'.")],
        [[tree] for tree in ([1,2],[1,None,3],[1,2,3],[1,2,None,3],[1,None,2,None,3],[1,2,3,4,5,None,6],[-1,-2,-3],[0,0,0],[1,2,2,3,None,None,3],[5,4,8,11,None,13,4,7,2,None,None,5,1],[1,2,3,None,4,None,5],[100,-100,0])],
        TREE_PATHS, ['def binary_tree_paths(root):\n    return [str(root.val)]\n', TREE_PATHS.replace('if node.left is None and node.right is None:', 'if node.left is None or node.right is None:')],
        ["Returns only the root and omits descendants on every nontrivial path.", "Treats a node with one missing child as a leaf and truncates paths before their actual leaves."], tree_paths_oracle, random_path_tree,
        ["A result is recorded only at a node with no left child and no right child.", "Carry the current sequence of value strings through depth-first recursion.", "Append the node value, recurse into existing children, then pop it while backtracking.", "Join and save a copy only at leaves; otherwise shared mutable path state can leak between branches."],
        "Depth-first recursion mirrors the path definition. The current list contains exactly the nodes from root to the active node. A leaf records that list as one arrow-joined string; popping restores the parent's path before another branch. The independent oracle represents nodes by binary paths and constructs each leaf result from its path prefixes.", "O(n²) worst case including copied path strings", "O(h) recursion excluding output", difficulty=3,
        stress=[([right_chain(100)], ["->".join(map(str,range(100)))])]),
    259: entry("three_sum_smaller", [("nums", "list[int]"), ("target", "int")], "int", ["arrays", "sorting", "two-pointers"],
        ["nums contains 0–3500 integers from -100 through 100; target is from -100 through 100. The answer is guaranteed to fit within 10^9.", "Count triples of distinct indices i<j<k whose three values sum to strictly less than target. Equal values at different indices form distinct triples."],
        [([[-2,0,1,3],2], "The qualifying index triples have values (-2,0,1) and (-2,0,3), so the count is 2."), ([[-2,0,1,3],0], "The smallest three-value sum is -1 from (-2,0,1), and it is the only sum strictly below 0, so the count is 1.")],
        [[nums,target] for nums,target in (([],0),([1],2),([1,2],4),([0,0,0],1),([0,0,0],0),([-1,-1,-1],-2),([-1,0,1,2],3),([3,1,0,-2],4),([1,1,1,1],4),([1,1,1,1],3),([-5,-4,-3,-2,-1],-8),([-2,0,1,3],-1))],
        THREE_SUM_SMALLER, [THREE_SUM_SMALLER.replace("< target:", "<= target:"), THREE_SUM_SMALLER.replace("count += right - middle", "count += 1")],
        ["Uses a non-strict comparison and counts triples whose sum equals target.", "Counts only the current middle/right pair, missing all right-middle valid choices implied by sorted order."], three_sum_smaller_oracle, random_three_sum_smaller,
        ["Sort first so moving one pointer changes the sum predictably.", "Fix the first index. If left+middle+right is below target, every index from middle+1 through right also works with that left and middle.", "Add right-middle and advance middle on a qualifying sum; otherwise decrement right.", "The condition is strictly less than target, and duplicate values still represent separate index choices."],
        "For each fixed first value, two pointers cover the remaining pairs. When the largest current right value still makes a small enough sum, all right-middle choices from the current interval qualify, so they are counted together. Otherwise only a smaller right value can help. The independent oracle enumerates every three-index combination.", "O(n²)", "O(n) for the sorted copy", difficulty=5,
        stress=[([[0]*3500,0],0), ([[0]*1800,1],comb(1800,3))]),
    260: entry("single_number_three", [("nums", "list[int]")], "list[int]", ["arrays", "bit-manipulation"],
        ["nums contains 2–30000 signed 32-bit integers. Exactly two values occur once and every other value occurs exactly twice.", "Return the two single-occurrence values in any order using linear time and constant auxiliary space."],
        [([[1,2,1,3,2,5]], "Values 3 and 5 each occur once; 1 and 2 each occur twice and cancel."), ([[-1,0]], "Both input values occur once, so the two answers are -1 and 0.")],
        [[nums] for nums in ([1,2],[1,1,2,3],[0,1,0,2],[-1,-2,-1,-3],[4,1,2,1,2,5],[7,7,8,9],[2,2,-1,0],[100,-100],[3,4,5,3,4,6],[-2147483648,2147483647],[0,0,1,-1],[9,1,9,2,3,3])],
        SINGLE_NUMBER_THREE, ['def single_number_three(nums):\n    value = 0\n    for number in nums: value ^= number\n    return [value]\n', 'def single_number_three(nums):\n    positive = negative = 0\n    for value in nums:\n        if value >= 0: positive ^= value\n        else: negative ^= value\n    return [positive, negative]\n'],
        ["Returns only the XOR of the two answers rather than separating them.", "Partitions by sign, which does not separate two singletons having the same sign."], two_singles_oracle, random_two_singles,
        ["XOR of every input cancels paired values and leaves first_single XOR second_single.", "A set bit in that combined XOR differs between the two singletons.", "Isolate combined & -combined, then XOR numbers into two groups according to that bit.", "Every duplicate pair stays within one group and cancels; the two singletons land in different groups."],
        "All paired values vanish under XOR. Any set bit of the remaining XOR distinguishes the two answers; the lowest set bit is isolated arithmetically. Partitioning and XORing again yields one singleton per group with constant state, including for negative Python integers. The independent oracle counts occurrences directly.", "O(n)", "O(1)", difficulty=5,
        stress=[([[-1,0]+[value for value in range(1,15000) for _ in range(2)]],[-1,0])]),
    261: entry("is_valid_tree", [("n", "int"), ("edges", "list[list[int]]")], "bool", ["graphs", "union-find", "depth-first-search"],
        ["n is 1–2000. edges contains 0–5000 distinct undirected pairs [a,b] with 0≤a,b<n and a≠b; reversed duplicates and self-loops are absent.", "Return whether the graph is one tree: every node must be connected and no cycle may exist."],
        [([5,[[0,1],[0,2],[0,3],[1,4]]], "Four edges connect all five nodes without a cycle, so the graph is a tree."), ([5,[[0,1],[1,2],[2,3],[1,3],[1,4]]], "Edges 1-2, 2-3, and 1-3 form a cycle, so the graph is not a tree.")],
        [[n,edges] for n,edges in ((1,[]),(2,[]),(2,[[0,1]]),(3,[[0,1],[1,2]]),(3,[[0,1],[1,2],[0,2]]),(4,[[0,1],[2,3]]),(4,[[0,1],[1,2],[2,0]]),(4,[[0,1],[0,2],[0,3]]),(5,[[0,1],[1,2],[2,3],[3,4]]),(5,[[0,1],[1,2],[3,4]]),(6,[[0,1],[1,2],[2,0],[3,4],[4,5]]),(6,[[0,5],[1,5],[2,5],[3,5],[4,5]]))],
        GRAPH_TREE, ['def is_valid_tree(n, edges):\n    return len(edges) == n - 1\n', 'def is_valid_tree(n, edges):\n    reached = {0}\n    while True:\n        expanded = reached | {v if u in reached else u for u,v in edges if (u in reached) != (v in reached)}\n        if expanded == reached: return len(reached) == n\n        reached = expanded\n'],
        ["Checks only the edge count and accepts a disconnected component containing a cycle.", "Checks only connectivity and accepts connected graphs that contain extra cycle edges."], valid_tree_oracle, random_graph,
        ["A tree on n nodes has exactly n-1 edges, but the count alone is not enough without cycle checks.", "Use disjoint-set roots. Every edge must join two previously separate components.", "Reject if an edge's endpoints already have the same root; otherwise union by size with path compression.", "With exactly n-1 successful unions, all n nodes form one connected acyclic component."],
        "Disjoint-set union records connected components. An edge within one component creates a cycle; an edge across components safely merges them. The n-1 edge prerequisite plus successful unions proves connectivity and acyclicity. The independent oracle uses repeated edge-boundary reachability and a separate edge-count theorem.", "O((n+e) α(n))", "O(n)", difficulty=5,
        stress=[([2000,[[index,index+1] for index in range(1999)]],True)]),
    263: entry("is_ugly_number", [("n", "int")], "bool", ["math", "number-theory"],
        ["n is a signed 32-bit integer.", "An ugly number is positive and has no prime factors other than 2, 3, and 5. One is ugly because it has no prime factors; zero and negative values are not ugly."],
        [([6], "Six factors as 2×3, so every prime factor is allowed."), ([14], "Fourteen includes prime factor 7, so it is not ugly.")],
        [[n] for n in (-2147483648,-6,-1,0,1,2,3,5,8,15,25,30,1073741824,2147483647)],
        UGLY, ['def is_ugly_number(n):\n    return n > 0 and (n == 1 or n % 2 == 0 or n % 3 == 0 or n % 5 == 0)\n', 'def is_ugly_number(n):\n    if n <= 0: return False\n    for factor in (2,3,5):\n        if n % factor == 0: n //= factor\n    return n == 1\n'],
        ["Accepts any positive number divisible by one allowed prime, even when another factor such as 7 remains.", "Divides by each allowed prime only once and rejects valid higher powers such as 8."], ugly_oracle, random_ugly,
        ["Reject nonpositive inputs before trying to divide.", "Repeatedly remove every factor of 2, then 3, then 5.", "After the three loops, return whether the remaining value is exactly 1.", "One needs no division and is accepted; a remaining value above 1 supplies a forbidden prime factor."],
        "Repeated division removes the full multiplicity of every permitted prime. A positive input is ugly exactly when nothing but 1 remains. The independent oracle pre-enumerates all products 2^a·3^b·5^c within the signed 32-bit range and performs membership checks.", "O(log n)", "O(1)", difficulty=3),
    264: entry("nth_ugly_number", [("n", "int")], "int", ["dynamic-programming", "math", "number-theory"],
        ["1≤n≤1690.", "Return the nth positive integer whose prime factors are limited to 2, 3, and 5. One is the first ugly number."],
        [([10], "The first ten values are 1,2,3,4,5,6,8,9,10,12, so the tenth is 12."), ([1], "One has no prime factors and is defined as the first ugly number.")],
        [[n] for n in (2,3,4,5,6,7,8,9,11,15,25,100)],
        NTH_UGLY, [NTH_UGLY.replace("values = [1] * n", "values = [1] * (n + 1)").replace("range(1, n):", "range(1, n + 1):").replace("return values[-1]", "return values[n]"), NTH_UGLY.replace(", values[five] * 5", "").replace("        while values[five] * 5 <= next_value:\n            five += 1\n", "")],
        ["Returns the next sequence value after the requested one, an off-by-one error.", "Generates products of only 2 and 3 and omits values requiring factor 5."], nth_ugly_oracle, random_nth_ugly,
        ["Every ugly number after 1 is a previous ugly number multiplied by 2, 3, or 5.", "Keep three indices for the next unused multiple of each factor.", "Append the minimum of values[i2]*2, values[i3]*3, values[i5]*5; advance every index whose product is no larger than it.", "Advance all tied factors so values such as 6 are emitted once, not once from 2×3 and again from 3×2."],
        "The three indices partition the sorted sequence by the next unseen multiple of each allowed factor. Their minimum is the next ugly number, and advancing every matching index suppresses duplicates. The independent oracle uses a min-heap and a seen set, a different generation strategy.", "O(n)", "O(n)", difficulty=5,
        stress=[([1690],2123366400)]),
    265: entry("minimum_paint_cost_many_colors", [("costs", "list[list[int]]")], "int", ["arrays", "dynamic-programming"],
        ["costs is an n×k matrix with 1≤n≤100, 2≤k≤20, and costs[i][j] from 1 through 20.", "Choose one color column per house so adjacent houses use different colors. Return the minimum total cost in O(nk) time."],
        [([[[1,5,3],[2,9,4]]], "Choose colors 0 then 2 for 1+4=5, or colors 2 then 0 for 3+2=5."), ([[[1,3],[2,4]]], "The two valid choices cost 1+4=5 or 3+2=5, so the minimum is 5.")],
        [[costs] for costs in ([[1,1]],[[1,20],[20,1]],[[1,20],[1,20]],[[1,2,3],[3,2,1]],[[5,1,5],[5,1,5],[5,1,5]],[[1,10,10],[10,1,10],[10,10,1]],[[3,4],[5,6],[7,8]],[[1,2,3,4],[4,3,2,1]],[[20,1,20,20],[20,1,20,20],[1,20,20,20]],[[1,2],[2,1],[1,2],[2,1]],[[7,3,8],[6,7,2],[5,4,3],[9,1,6]],[[20,19,18,17],[1,2,3,4],[4,3,2,1]])],
        PAINT_HOUSE_TWO, ['def minimum_paint_cost_many_colors(costs):\n    return sum(min(row) for row in costs)\n', 'def minimum_paint_cost_many_colors(costs):\n    return min(sum(row[color] for row in costs) for color in range(len(costs[0])))\n'],
        ["Greedily chooses each row's cheapest color and can repeat that color on adjacent houses.", "Forces every house to use one fixed color, violating adjacency rather than switching among colors."], paint_oracle, random_paint,
        ["The best prefix ending in color c needs the smallest previous cost from a different color.", "For each previous row, retain its smallest value, second-smallest value, and the smallest value's color.", "For current color c, add the second minimum only when c was the previous minimum's color; otherwise add the minimum.", "Compute the new row from the complete previous row. This avoids scanning all other colors for every cell."],
        "Dynamic programming stores the cheapest valid prefix ending in each color. The transition needs the minimum previous value excluding the current color. Knowing the smallest and second-smallest values makes that exclusion O(1), so all nk cells are processed once. The independent oracle enumerates all color assignments for small generated matrices; the source-scale fixture uses a direct O(nk²) exclusion DP.", "O(nk)", "O(k)", difficulty=8,
        stress=[([large_paint],paint_dp_oracle(large_paint))]),
}

for problem_id in (235, 236):
    BATCH[problem_id]["params"] = [
        ("root", "TreeNode", "treenode"),
        ("p", "TreeNode", "treenode_ref"),
        ("q", "TreeNode", "treenode_ref"),
    ]
    BATCH[problem_id]["adapter"] = "treenode_value"
    BATCH[problem_id]["node_policy"] = "return_input_node"
    BATCH[problem_id]["parameter_sources"] = {1: 0, 2: 0}

BATCH[257]["params"] = [("root", "TreeNode | None", "treenode")]
BATCH[257]["comparator"] = "unordered"
BATCH[260]["comparator"] = "unordered"
BATCH[265]["prerequisites"] = ["dynamic-programming"]
