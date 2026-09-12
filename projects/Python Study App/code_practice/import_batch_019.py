"""Noncanonical balanced tree construction and structural subtree counting."""
from .import_batch_002 import positions, random_tree
from .import_batch_003 import entry


def complete_bst_oracle(args):
    # Fix a COMPLETE heap-indexed shape, then fill its inorder slots. This is
    # independent of both midpoint recursion and the linked cursor reference.
    values = args[0]
    result = [None] * len(values)
    stack, index, next_value = [], 0, 0
    while stack or index < len(values):
        while index < len(values):
            stack.append(index)
            index = 2 * index + 1
        index = stack.pop()
        result[index] = values[next_value]
        next_value += 1
        index = 2 * index + 2
    return result


def count_oracle(args):
    # Source inputs are complete trees, hence every level-order entry is a node.
    return len(args[0])


def unival_oracle(args):
    mapping = positions(args[0])
    return sum(all(value == other for path, other in mapping.items() if path[:len(root)] == root)
               for root, value in mapping.items())


def random_array(rng):
    return [sorted(rng.sample(range(-10000, 10001), rng.randint(1, 75)))]


def random_list(rng):
    return [sorted(rng.randint(-8, 8) for _ in range(rng.randrange(76)))]


def random_complete(rng):
    return [[rng.randrange(50001) for _ in range(rng.randrange(301))]]


def random_unival(rng):
    tree = random_tree(rng)
    if rng.random() < .5:
        value = rng.randint(-1000, 1000)
        tree = [None if item is None else value for item in tree]
    return [tree]


ARRAY = '''\
def sorted_array_bst(nums):
    def build(left, right):
        if left > right:
            return None
        middle = (left + right) // 2
        root = TreeNode(nums[middle])
        root.left = build(left, middle - 1)
        root.right = build(middle + 1, right)
        return root
    return build(0, len(nums) - 1)
'''
ARRAY_CHAIN = '''\
def sorted_array_bst(nums):
    root = tail = None
    for value in nums:
        node = TreeNode(value)
        if tail is None:
            root = node
        else:
            tail.right = node
        tail = node
    return root
'''
LIST = '''\
def sorted_list_bst(head):
    length, current = 0, head
    while current is not None:
        length += 1
        current = current.next
    current = head
    def build(count):
        nonlocal current
        if count == 0:
            return None
        left_count = count // 2
        left = build(left_count)
        root = TreeNode(current.val)
        current = current.next
        root.left = left
        root.right = build(count - left_count - 1)
        return root
    return build(length)
'''
LIST_CHAIN = '''\
def sorted_list_bst(head):
    root = tail = None
    while head is not None:
        node = TreeNode(head.val)
        if tail is None:
            root = node
        else:
            tail.right = node
        tail = node
        head = head.next
    return root
'''
LIST_DEDUP = ARRAY.replace("def sorted_array_bst(nums):", '''def sorted_list_bst(head):
    nums = []
    while head is not None:
        nums.append(head.val)
        head = head.next
    nums = sorted(set(nums))''')
COMPLETE = '''\
def count_complete_nodes(root):
    def left_height(node):
        height = 0
        while node is not None:
            height += 1
            node = node.left
        return height
    total = 0
    while root is not None:
        left, right = left_height(root.left), left_height(root.right)
        if left == right:
            total += 1 << left
            root = root.right
        else:
            total += 1 << right
            root = root.left
    return total
'''
PERFECT_ONLY = '''\
def count_complete_nodes(root):
    height = 0
    while root is not None:
        height += 1
        root = root.left
    return (1 << height) - 1
'''
UNIVAL = '''\
def count_univalue_subtrees(root):
    uniform, result = {}, 0
    stack = [(root, False)]
    while stack:
        node, visited = stack.pop()
        if node is None:
            continue
        if not visited:
            stack.extend(((node, True), (node.right, False), (node.left, False)))
            continue
        same = all(child is None or (uniform[id(child)] and child.val == node.val)
                   for child in (node.left, node.right))
        uniform[id(node)] = same
        result += same
    return result
'''
LEAVES_ONLY = '''\
def count_univalue_subtrees(root):
    stack, result = [root], 0
    while stack:
        node = stack.pop()
        if node is not None:
            result += node.left is None and node.right is None
            stack.extend((node.left, node.right))
    return result
'''

BATCH = {
    108: entry("sorted_array_bst", [("nums", "list[int]")], "TreeNode | None", ["arrays", "trees", "recursion", "divide-and-conquer"],
        ["1–10000 strictly increasing integers from -10000 to 10000.", "Return a TreeNode root, not a serialized list. Its inorder traversal must equal nums exactly, and at EVERY node its left/right subtree heights must differ by at most one. Any valid balanced shape is accepted."],
        [([[-10, -3, 0, 5, 9]], "One valid output has root 5, left child -3 (children -10 and 0), and right child 9. A balanced tree rooted at 0 is also valid; the displayed shape is not mandatory."),
         ([[1, 3]], "Root 3 with left child 1 and root 1 with right child 3 are both valid. Both preserve inorder [1,3] and have height difference at most one.")],
        [[a] for a in ([0], [1], [1, 2], [-1, 1], [-2, 0, 2], list(range(4)), list(range(6)), list(range(7)), [-10000, 10000], [-3, -2, -1], list(range(0, 80, 10)), [-5, -4, -2, 0, 7, 9, 10, 11, 99])],
        ARRAY, [ARRAY_CHAIN, ARRAY.replace("len(nums) - 1", "len(nums) - 2")],
        ["Builds a sorted right-only chain, preserving inorder but violating height balance.", "Excludes the final array position and silently drops its value."], complete_bst_oracle, random_array,
        ["In a search tree, values before the root belong on the left and values after it on the right.", "Choose a middle array value as the root and recursively build from the two remaining ranges.", "For inclusive bounds, return None if left>right; create the midpoint node and recursively assign its left and right children.", "Either middle choice is valid for an even-length range. Do not impose a particular sample shape; preserve all values and balance every subtree."],
        "A middle element divides the sorted input into ranges whose lengths differ by at most one. Recursively applying that split gives a height-balanced BST and visits each array position once. Bounds avoid repeated list slicing, and the recursion depth is logarithmic. The independent oracle uses a different complete heap-indexed shape and assigns input values to its inorder positions. Property-based grading compares inorder values and checks balance at every node instead of matching either construction's serialized shape.",
        "O(n)", "O(log n) auxiliary recursion, plus O(n) returned nodes", difficulty=3,
        stress=[([list(range(-5000, 5000))], complete_bst_oracle([list(range(-5000, 5000))]))]),
    109: entry("sorted_list_bst", [("head", "ListNode | None")], "TreeNode | None", ["linked-lists", "trees", "recursion", "divide-and-conquer"],
        ["0–20000 linked-list nodes in nondecreasing order, with values from -100000 to 100000; repeated values are allowed.", "Return a TreeNode root (None for an empty list). Its inorder values must equal the complete input list, including duplicates, and every subtree must be height-balanced. Tree shape need not match the example."],
        [([[-10, -3, 0, 5, 9]], "One valid tree has root 5, left subtree containing -10,-3,0, and right child 9. Other balanced shapes with the same inorder values are equally correct."),
         ([[]], "An empty linked list becomes an empty tree: return None, displayed as [].")],
        [[a] for a in ([0], [1, 1], [1, 2], [1, 2, 3], [1, 1, 1], [-1, -1, 2, 2], [-1, 0, 0, 3, 3], list(range(4)), list(range(6)), [100000], [-100000, 100000], [5] * 12)],
        LIST, [LIST_CHAIN, LIST_DEDUP],
        ["Copies the sorted linked list into an unbalanced right-only tree.", "Removes duplicate values before construction, changing the required inorder multiset."], complete_bst_oracle, random_list,
        ["A linked list cannot access its middle by index cheaply, but its order is already the desired inorder traversal.", "Count the nodes, build a left subtree of a chosen size, consume the current list node as root, then build the right subtree.", "Keep one advancing list cursor. build(count) recursively creates count//2 left nodes, consumes one cursor value, and creates the remaining right nodes.", "The cursor advances only after the left subtree is built. Duplicate values still represent separate required tree nodes."],
        "First count the list length. Recursive subtree sizes determine a balanced shape, while a shared list cursor fills the nodes in inorder, advancing exactly once per input node. This takes O(n) time without copying the list into an auxiliary array. New TreeNode objects are required: ListNode objects are the input, not the returned tree. The independent oracle fills inorder positions of a complete heap-indexed tree from the original JSON values. Grading allows any balanced shape, checks every duplicate occurrence, and uses iterative checks so an incorrect deep chain is rejected without a checker recursion overflow.",
        "O(n)", "O(log(n+1)) auxiliary recursion, plus O(n) returned nodes", difficulty=5,
        stress=[([[0] * 20000], complete_bst_oracle([[0] * 20000]))]),
    222: entry("count_complete_nodes", [("root", "TreeNode | None")], "int", ["trees", "binary-search"],
        ["0–50000 tree nodes with integer values from 0 to 50000. The tree is guaranteed complete: all levels except possibly the last are full, and the last is filled from left to right.", "Return the number of nodes, regardless of repeated values. Use the complete-tree structure to achieve sublinear time rather than visiting every node."],
        [([[1, 2, 3, 4, 5, 6]], "There are six nodes: the last level has 4,5,6 in the leftmost positions, not all four possible nodes."),
         ([[]], "An empty tree contains zero nodes.")],
        [[a] for a in ([1], [1, 2], [1, 2, 3], [1, 2, 3, 4], [1, 2, 3, 4, 5], [0] * 6, [0] * 7, [0] * 8, [9] * 14, [9] * 15, [9] * 16, [50000] * 31)],
        COMPLETE, [PERFECT_ONLY, COMPLETE.replace("total += 1 << left", "total += (1 << left) - 1").replace("total += 1 << right", "total += (1 << right) - 1")],
        ["Assumes the final level is full and counts a perfect tree of the same height.", "Counts each skipped perfect subtree but forgets its parent root."], count_oracle, random_complete,
        ["Completeness guarantees that one of the current root's subtrees is perfect.", "Compare the left-edge heights of the left and right children to identify the perfect subtree.", "If heights match, add 2^left_height for the root plus its perfect left subtree and continue right; otherwise add 2^right_height and continue left.", "A perfect subtree of height h has 2^h-1 nodes; including the current root makes the skipped contribution 2^h."],
        "At each complete subtree, equal child left-edge heights mean the left child is perfect; otherwise the right child is perfect one level shorter. Count that perfect side in constant arithmetic and descend only into the remaining side. There are logarithmically many descents and each pair of height scans is logarithmic, giving O(log²(n+1)) time and constant extra space. The independent oracle simply counts the complete level-order input entries. Regression tests additionally count node-link reads, distinguishing the advertised sublinear reference from a full traversal; ordinary submissions still receive behavioral correctness and a time deadline, not a symbolic complexity proof.",
        "O(log²(n+1))", "O(1)", difficulty=3,
        stress=[([[7] * 50000], 50000)]),
    250: entry("count_univalue_subtrees", [("root", "TreeNode | None")], "int", ["trees", "recursion", "dynamic-programming"],
        ["0–1000 nodes; values range from -1000 to 1000. The binary tree may be sparse or skewed.", "A subtree consists of a node and ALL of its descendants. Count it if every value equals its root value. Every leaf counts; a connected same-value portion of a nonuniform subtree does not count."],
        [([[5, 1, 5, 5, 5, None, 5]], "The three leaves each count, and the right child 5 with its leaf 5 counts too. The subtree rooted at 1 and the entire tree are not uniform, so the total is 4."),
         ([[]], "There are no node-rooted subtrees in an empty tree, so the answer is 0.")],
        [[a] for a in ([1], [1, 1], [1, 2], [1, 1, 1], [1, 1, 1, 2], [5, 5, 5, 5, 5, None, 5], [0, -1, 0], [-1000], [1000, 1000, 1000], [1, None, 1, None, 2], [2, 2, None, 2], [1, 2, 3, 4, 5, 6, 7])],
        UNIVAL, [LEAVES_ONLY, UNIVAL.replace("(uniform[id(child)] and child.val == node.val)", "child.val == node.val")],
        ["Counts only leaves, missing larger uniform subtrees.", "Checks immediate child values but ignores a mismatching deeper descendant."], unival_oracle, random_unival,
        ["A parent subtree can be uniform only if each of its child subtrees is already uniform.", "Process children before their parent and retain one uniform/nonuniform result per child.", "A node qualifies when each existing child is uniform and has the node's value; add one for each qualifying node.", "Use explicit postorder frames for a 1000-node chain, preserving recursive dependencies without relying on the interpreter's recursion limit."],
        "Uniformity is a postorder property: both child subtrees must be uniform, and their root values must match the parent. Every qualifying node contributes one subtree, including internal nodes and leaves. An explicit visited-frame stack evaluates each node after its children and avoids deep-call-stack errors. The independent oracle stores binary paths and, for each possible subtree root, directly scans all descendant values. Tests distinguish an entire subtree from a partial same-value region and include both uniformly valued and nonuniform deep structures.",
        "O(n)", "O(n)", difficulty=5,
        stress=[([[1, None] * 999 + [1]], 1000), ([[0, None] * 999 + [1]], 1)]),
}
for pid in (108, 109):
    BATCH[pid]["adapter"] = "treenode"
    BATCH[pid]["comparator"] = "balanced_bst"
BATCH[109]["params"] = [("head", "ListNode | None", "listnode")]
for pid in (222, 250):
    BATCH[pid]["params"] = [("root", "TreeNode | None", "treenode")]
