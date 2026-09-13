"""Reviewed ordinary binary-tree imports with TreeNode adapter coverage."""
from collections import deque

from .import_batch_055 import entry


def from_level(values):
    if not values: return None
    root = [values[0], None, None]
    queue, index = deque([root]), 1
    while queue and index < len(values):
        node = queue.popleft()
        for side in (1, 2):
            if index < len(values) and values[index] is not None:
                child = [values[index], None, None]
                node[side] = child
                queue.append(child)
            index += 1
    return root


def to_level(root):
    if root is None: return []
    values, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            values.append(None)
        else:
            values.append(node[0])
            queue.extend((node[1], node[2]))
    while values and values[-1] is None: values.pop()
    return values


def add_row_oracle(args):
    root, value, depth = from_level(args[0]), args[1], args[2]
    if depth == 1: return to_level([value, root, None])
    def visit(node, current):
        if node is None: return
        if current == depth - 1:
            node[1] = [value, node[1], None]
            node[2] = [value, None, node[2]]
            return
        visit(node[1], current + 1); visit(node[2], current + 1)
    visit(root, 1)
    return to_level(root)


def averages_oracle(args):
    root = from_level(args[0])
    if root is None: return []
    answer, level = [], [root]
    while level:
        answer.append(sum(node[0] for node in level) / len(level))
        level = [child for node in level for child in (node[1], node[2]) if child is not None]
    return answer


def bst_sum_oracle(args):
    values = [value for value in args[0] if value is not None]
    seen = set()
    for value in values:
        if args[1] - value in seen: return True
        seen.add(value)
    return False


def maximum_tree_oracle(args):
    def build(values):
        if not values: return None
        maximum = max(values); index = values.index(maximum)
        return [maximum, build(values[:index]), build(values[index + 1:])]
    return to_level(build(args[0]))


def print_tree_oracle(args):
    root = from_level(args[0])
    def height(node):
        return 0 if node is None else 1 + max(height(node[1]), height(node[2]))
    rows = height(root)
    output = [[''] * (2 ** rows - 1) for _ in range(rows)]
    def place(node, row, left, right):
        if node is None: return
        middle = (left + right) // 2
        output[row][middle] = str(node[0])
        place(node[1], row + 1, left, middle - 1)
        place(node[2], row + 1, middle + 1, right)
    place(root, 0, 0, len(output[0]) - 1)
    return output


def random_node(rng, depth=0, maximum=4):
    if depth >= maximum or (depth and rng.random() < .35): return None
    return [rng.randint(-20, 20), random_node(rng, depth + 1, maximum), random_node(rng, depth + 1, maximum)]


def random_tree_values(rng):
    return to_level(random_node(rng, maximum=rng.randint(1, 5)))


def random_add_row(rng):
    values = random_tree_values(rng)
    root = from_level(values)
    def height(node): return 0 if node is None else 1 + max(height(node[1]), height(node[2]))
    return [values, rng.randint(-10, 10), rng.randint(1, height(root) + 1)]


def random_averages(rng): return [random_tree_values(rng)]


def random_bst_sum(rng):
    values = rng.sample(range(-40, 41), rng.randint(1, 15))
    root = None
    for value in values:
        if root is None:
            root = [value, None, None]; continue
        node = root
        while True:
            side = 1 if value < node[0] else 2
            if node[side] is None:
                node[side] = [value, None, None]; break
            node = node[side]
    target = sum(rng.sample(values, 2)) if len(values) > 1 and rng.random() < .55 else rng.randint(-80, 80)
    return [to_level(root), target]


def random_maximum_tree(rng):
    return [rng.sample(range(-50, 51), rng.randint(1, 18))]


def random_print_tree(rng): return [random_tree_values(rng)]


ADD_ROW = '''\
def add_tree_row(root, val, depth):
    if depth == 1:
        return TreeNode(val, root, None)
    level = [root]
    for _ in range(depth - 2):
        level = [child for node in level for child in (node.left, node.right) if child]
    for node in level:
        node.left = TreeNode(val, node.left, None)
        node.right = TreeNode(val, None, node.right)
    return root
'''


AVERAGES = '''\
def average_tree_levels(root):
    if not root: return []
    answer, level = [], [root]
    while level:
        answer.append(sum(node.val for node in level) / len(level))
        level = [child for node in level for child in (node.left, node.right) if child]
    return answer
'''


BST_SUM = '''\
def bst_has_pair_sum(root, k):
    seen = set()
    stack = [root] if root else []
    while stack:
        node = stack.pop()
        if k - node.val in seen: return True
        seen.add(node.val)
        if node.left: stack.append(node.left)
        if node.right: stack.append(node.right)
    return False
'''


MAXIMUM_TREE = '''\
def construct_maximum_tree(nums):
    stack = []
    for value in nums:
        node = TreeNode(value)
        while stack and stack[-1].val < value:
            node.left = stack.pop()
        if stack:
            stack[-1].right = node
        stack.append(node)
    return stack[0]
'''


PRINT_TREE = '''\
def print_binary_tree(root):
    def height(node):
        return 0 if not node else 1 + max(height(node.left), height(node.right))
    rows = height(root)
    answer = [[''] * (2 ** rows - 1) for _ in range(rows)]
    def place(node, row, left, right):
        if not node: return
        middle = (left + right) // 2
        answer[row][middle] = str(node.val)
        place(node.left, row + 1, left, middle - 1)
        place(node.right, row + 1, middle + 1, right)
    place(root, 0, 0, len(answer[0]) - 1)
    return answer
'''


ADD_ROW_LATE = '''\
def add_tree_row(root, val, depth):
    if depth == 1: return TreeNode(val, root, None)
    level = [root]
    for _ in range(depth - 1):
        level = [child for node in level for child in (node.left, node.right) if child]
    for node in level:
        node.left = TreeNode(val, node.left, None)
        node.right = TreeNode(val, None, node.right)
    return root
'''


ADD_ROW_SWAPPED = '''\
def add_tree_row(root, val, depth):
    if depth == 1: return TreeNode(val, root, None)
    level = [root]
    for _ in range(depth - 2):
        level = [child for node in level for child in (node.left, node.right) if child]
    for node in level:
        old_left, old_right = node.left, node.right
        node.left = TreeNode(val, old_right, None)
        node.right = TreeNode(val, None, old_left)
    return root
'''


MAXIMUM_TREE_MIN = MAXIMUM_TREE.replace("stack[-1].val < value", "stack[-1].val > value")
MAXIMUM_TREE_CHAIN = '''\
def construct_maximum_tree(nums):
    root = TreeNode(max(nums))
    current = root
    for value in sorted((v for v in nums if v != root.val), reverse=True):
        current.left = TreeNode(value)
        current = current.left
    return root
'''


PRINT_TREE_MIRROR = PRINT_TREE.replace("place(node.left, row + 1, left, middle - 1)\n        place(node.right, row + 1, middle + 1, right)", "place(node.right, row + 1, left, middle - 1)\n        place(node.left, row + 1, middle + 1, right)")
PRINT_TREE_INTS = PRINT_TREE.replace("str(node.val)", "node.val")


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial], editorial


BATCH = {
    623: entry('add_tree_row', [('root','TreeNode | None'),('val','int'),('depth','int')], 'TreeNode | None', ['trees','breadth-first-search'],
        ['The tree contains 1 to 10,000 nodes; 1 <= depth <= tree height + 1.', 'At depth one, the new node becomes root; otherwise preserve each original subtree under the correct new node.'],
        [([[4,2,6,3,1,5],1,2], 'Two new ones become children of four while preserving the original left and right subtrees.'), ([[1,2,3],5,1], 'A new root five is created with the original tree as its left child.')],
        [[tree,val,depth] for tree,val,depth in (([1],2,2),([1,2],3,2),([1,None,2],4,2),([1,2,3],0,3),([4,2,6,3,1,5],1,3),([1,2,3,4],9,4),([0],0,1),([-1,-2,-3],5,2),([1,2,None,3],7,3),([1,None,2,None,3],8,4),([10,5,15],6,2),([1,2,3,4,5,6,7],9,3))],
        ADD_ROW, [ADD_ROW_LATE, ADD_ROW_SWAPPED], ['Inserts the row one level too deep.', 'Swaps the original left and right subtrees when reconnecting them.'], add_row_oracle, random_add_row,
        *lesson('Only nodes immediately above the requested depth change.', 'Reach depth-1 with breadth-first traversal, then splice two new children under every node.', 'Save old children; new-left.left=old-left and new-right.right=old-right.', 'No descendants are rebuilt or lost; depth one is the single special case because no parent exists.'), 'O(n)', 'O(tree width)', 5),
    637: entry('average_tree_levels', [('root','TreeNode | None')], 'list[float]', ['trees','breadth-first-search'],
        ['The tree contains 0 to 10,000 nodes with integer values.', 'Return one average per depth from root downward, accurate within 0.00001.'],
        [([[3,9,20,None,None,15,7]], 'The level averages are 3, (9+20)/2, and (15+7)/2.'), ([[1]], 'A single-node tree has one average equal to its value.')],
        [[tree] for tree in ([],[0],[-1,1,3],[1,2,3],[1,2,None,4],[1,None,2,None,3],[5,5,5,5,5],[10,-10,20,0],[1,2,3,4,5,6,7],[-5,-4,-3,None,-2],[1000000000,-1000000000,0],[2,1,4,None,None,3,5])],
        AVERAGES, [AVERAGES.replace('/ len(level)','// len(level)'), AVERAGES.replace('sum(node.val for node in level)','max(node.val for node in level)')],
        ['Uses integer division and truncates fractional averages.', 'Uses the largest value at each level instead of its sum.'], averages_oracle, random_averages,
        *lesson('Breadth-first traversal naturally groups nodes by depth.', 'Process one complete frontier at a time and build the next frontier from its children.', 'Append sum(level)/size(level), then replace level with all non-null children.', 'Every node appears in exactly one frontier, so each level average is computed once.'), 'O(n)', 'O(tree width)', 3),
    653: entry('bst_has_pair_sum', [('root','TreeNode | None'),('k','int')], 'bool', ['trees','binary-search-trees','hash-maps'],
        ['The tree contains 1 to 10,000 nodes and is a binary search tree.', 'The two values must come from distinct nodes.'],
        [([[5,3,6,2,4,None,7],9], 'Values two and seven are distinct nodes summing to nine.'), ([[5,3,6,2,4,None,7],28], 'No two values in the tree sum to twenty-eight.')],
        [[tree,k] for tree,k in (([1],2),([2,1,3],4),([2,1,3],6),([5,3,7],10),([5,3,7],6),([0,-2,3],1),([10,5,15,3,7,12,20],22),([10,5,15,3,7,12,20],40),([1,None,2],3),([3,2,None,1],4),([-3,-5,-1],-6),([8,4,12,2,6,10,14],16))],
        BST_SUM, [BST_SUM.replace("if k - node.val in seen", "if k == 2 * node.val or k - node.val in seen"), "def bst_has_pair_sum(root, k):\n    return bool(root and ((root.left and root.val + root.left.val == k) or (root.right and root.val + root.right.val == k)))\n"],
        ['Allows one node to be paired with itself.', 'Checks only parent-child pairs at the root.'], bst_sum_oracle, random_bst_sum,
        *lesson('The problem is a two-sum search over distinct tree nodes.', 'Traverse once while storing values already visited.', 'Before inserting node.val, test whether k-node.val is in the seen set.', 'Checking before insertion prevents a single node from satisfying an even target by itself.'), 'O(n)', 'O(n)', 3),
    654: entry('construct_maximum_tree', [('nums','list[int]')], 'TreeNode | None', ['trees','monotonic-stacks'],
        ['1 <= len(nums) <= 1,000; all values are unique.', 'The maximum value is root; recursively apply the rule to the original left and right subarrays.'],
        [([[3,2,1,6,0,5]], 'Six is root; the values before and after it form the left and right subtrees.'), ([[3,2,1]], 'The decreasing input forms a left-rooted chain beginning at three.')],
        [[[v for v in nums]] for nums in ([1],[1,2],[2,1],[1,3,2],[2,1,3],[5,1,4,2,3],[0,-1,-2],[-3,-1,-2],[4,2,5,1,3],[1,5,2,4,3],[9,0,8,1,7],[3,1,4,0,2])],
        MAXIMUM_TREE, [MAXIMUM_TREE_MIN, MAXIMUM_TREE_CHAIN], ['Builds a minimum tree by reversing the monotonic comparison.', 'Sorts the remaining values and loses their required input-side structure.'], maximum_tree_oracle, random_maximum_tree,
        *lesson('A decreasing stack represents the unfinished right spine of the maximum tree.', 'Pop smaller nodes to become the new node’s left subtree; attach the new node as the remaining top’s right child.', 'For each value, pop smaller stack nodes, link the last popped as left, link from stack top as right, then push.', 'Each value is pushed and popped at most once, reproducing the same nearest-greater boundaries as recursive maximum splits.'), 'O(n)', 'O(n)', 5),
    655: entry('print_binary_tree', [('root','TreeNode')], 'list[list[str]]', ['trees','recursion','layout'],
        ['The tree contains 1 to 1,024 nodes.', 'For h levels, return h rows and 2^h-1 columns, using strings and empty strings exactly as placeholders.'],
        [([[1,2]], 'The root is centered in three columns and its left child occupies the lower-left column.'), ([[1,2,3,None,4]], 'Each child is centered in its recursively assigned half of the output matrix.')],
        [[tree] for tree in ([1],[1,None,2],[1,2,3],[1,2,None,3],[1,None,2,None,3],[-1,-2,-3],[1,2,3,4,5,6,7],[5,3,8,None,4],[0,-1,1,-2,None,None,2],[1,2,3,None,None,4],[10,5,None,2],[7,None,8,9])],
        PRINT_TREE, [PRINT_TREE_MIRROR, PRINT_TREE_INTS], ['Mirrors left and right children in the display.', 'Places integer values in a matrix that must contain strings.'], print_tree_oracle, random_print_tree,
        *lesson('Every subtree owns a horizontal interval whose midpoint holds its root.', 'Compute tree height, allocate the exact matrix, and recursively halve column intervals.', 'Place at (left+right)//2; recurse left into the left half and right into the right half.', 'The 2^h-1 width ensures every descendant midpoint is an integer and no two nodes share a cell.'), 'O(rows * columns)', 'O(tree height)', 5),
}

for pid in (623, 637, 653, 655):
    BATCH[pid]['params'][0] = ('root', 'TreeNode | None', 'treenode')
for pid in (623, 654):
    BATCH[pid]['adapter'] = 'treenode'
BATCH[637]['comparator'] = 'float_list'
