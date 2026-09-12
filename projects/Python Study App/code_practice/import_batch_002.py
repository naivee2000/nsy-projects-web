"""Reviewed tree and ordinary Hard exercises, with independent JSON-level oracles."""
from collections import deque
from textwrap import dedent


def positions(values):
    """Map binary paths to values without constructing the reference's node objects."""
    if not values:
        return {}
    result, queue, index = {(): values[0]}, deque([()]), 1
    while queue and index < len(values):
        parent = queue.popleft()
        for side in (0, 1):
            if index >= len(values):
                break
            if values[index] is not None:
                key = parent + (side,)
                result[key] = values[index]
                queue.append(key)
            index += 1
    return result


def flatten(mapping):
    if not mapping:
        return []
    out, queue = [], deque([()])
    while queue:
        key = queue.popleft()
        out.append(mapping.get(key))
        if key in mapping:
            queue.extend((key + (0,), key + (1,)))
    while out and out[-1] is None:
        out.pop()
    return out


def invert_oracle(args):
    return flatten({tuple(1 - bit for bit in key): value for key, value in positions(args[0]).items()})


def merge_oracle(args):
    left, right = map(positions, args)
    return flatten({key: left.get(key, 0) + right.get(key, 0) for key in left.keys() | right.keys()})


def symmetric_oracle(args):
    mapping = positions(args[0])
    return mapping == {tuple(1 - bit for bit in key): value for key, value in mapping.items()}


def balanced_oracle(args):
    # Enumerate descendant paths independently for every node, intentionally
    # trading speed for a direct definition of the height-balance condition.
    mapping = positions(args[0])
    for key in mapping:
        heights = []
        for side in (0, 1):
            prefix = key + (side,)
            heights.append(max((len(p) - len(key) for p in mapping if p[:len(prefix)] == prefix), default=0))
        if abs(heights[0] - heights[1]) > 1:
            return False
    return True


def path_oracle(args):
    mapping, target = positions(args[0]), args[1]
    for key in mapping:
        if key + (0,) not in mapping and key + (1,) not in mapping:
            if sum(mapping[key[:i]] for i in range(len(key) + 1)) == target:
                return True
    return False


def reverse_oracle(args):
    values, k = args
    out = []
    for start in range(0, len(values), k):
        chunk = values[start:start + k]
        out.extend(reversed(chunk) if len(chunk) == k else chunk)
    return out


def rain_oracle(args):
    height, = args
    return sum(max(0, min(max(height[:i + 1]), max(height[i:])) - h) for i, h in enumerate(height))


def sliding_oracle(args):
    nums, k = args
    return [max(nums[start:start + k]) for start in range(len(nums) - k + 1)]


def random_tree(rng, nonempty=False):
    if not nonempty and rng.random() < .12:
        return []
    out, pending = [rng.randrange(-5, 6)], 1
    while pending and len(out) < 31:
        pending -= 1
        for _ in range(2):
            value = None if rng.random() < .4 else rng.randrange(-5, 6)
            out.append(value)
            pending += value is not None
    while out and out[-1] is None:
        out.pop()
    return out


def random_single(rng):
    return [random_tree(rng)]


def random_pair(rng):
    return [random_tree(rng), random_tree(rng)]


def random_symmetric(rng):
    if rng.random() < .5:
        return [random_tree(rng, nonempty=True)]
    branch = positions(random_tree(rng))
    mapping = {(): rng.randrange(-5, 6)}
    for key, value in branch.items():
        mapping[(0,) + key] = value
        mapping[(1,) + tuple(1 - bit for bit in key)] = value
    return [flatten(mapping)]


def random_path(rng):
    tree = random_tree(rng)
    mapping = positions(tree)
    leaves = [key for key in mapping if key + (0,) not in mapping and key + (1,) not in mapping]
    if leaves and rng.random() < .5:
        key = rng.choice(leaves)
        target = sum(mapping[key[:i]] for i in range(len(key) + 1))
    else:
        target = rng.randrange(-20, 21)
    return [tree, target]


def random_reverse(rng):
    n = rng.randint(1, 30)
    return [[rng.randrange(11) for _ in range(n)], rng.randint(1, n)]


def random_rain(rng):
    return [[rng.randrange(15) for _ in range(rng.randint(1, 30))]]


def random_sliding(rng):
    n = rng.randint(1, 30)
    return [[rng.randrange(-15, 16) for _ in range(n)], rng.randint(1, n)]


INVERT = dedent('''\
def invert_tree(root):
    if root is None:
        return None
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root
''')
MERGE = dedent('''\
def merge_trees(root1, root2):
    if root1 is None:
        return root2
    if root2 is None:
        return root1
    merged = TreeNode()
    stack = [(root1, root2, merged)]
    while stack:
        left, right, output = stack.pop()
        output.val = left.val + right.val
        for side in ("left", "right"):
            a, b = getattr(left, side), getattr(right, side)
            if a is None or b is None:
                setattr(output, side, a if a is not None else b)
            else:
                child = TreeNode()
                setattr(output, side, child)
                stack.append((a, b, child))
    return merged
''')
SYMMETRIC = dedent('''\
def symmetric_tree(root):
    if root is None:
        return True
    pairs = [(root.left, root.right)]
    while pairs:
        left, right = pairs.pop()
        if left is None or right is None:
            if left is not right:
                return False
            continue
        if left.val != right.val:
            return False
        pairs.append((left.left, right.right))
        pairs.append((left.right, right.left))
    return True
''')
BALANCED = dedent('''\
def balanced_tree(root):
    heights = {None: 0}
    stack = [(root, False)] if root is not None else []
    while stack:
        node, visited = stack.pop()
        if visited:
            left, right = heights[node.left], heights[node.right]
            if abs(left - right) > 1:
                return False
            heights[node] = 1 + max(left, right)
        else:
            stack.append((node, True))
            if node.right is not None:
                stack.append((node.right, False))
            if node.left is not None:
                stack.append((node.left, False))
    return True
''')
PATH = dedent('''\
def has_path_sum(root, target_sum):
    stack = [(root, root.val)] if root is not None else []
    while stack:
        node, total = stack.pop()
        if node.left is None and node.right is None and total == target_sum:
            return True
        if node.right is not None:
            stack.append((node.right, total + node.right.val))
        if node.left is not None:
            stack.append((node.left, total + node.left.val))
    return False
''')
REVERSE = dedent('''\
def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    previous_group = dummy
    while True:
        kth = previous_group
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next
        following = kth.next
        previous, current = following, previous_group.next
        while current is not following:
            next_node = current.next
            current.next = previous
            previous, current = current, next_node
        old_head = previous_group.next
        previous_group.next = kth
        previous_group = old_head
''')
RAIN = dedent('''\
def trapped_water(height):
    left, right = 0, len(height) - 1
    left_max = right_max = water = 0
    while left <= right:
        if left_max <= right_max:
            left_max = max(left_max, height[left])
            water += left_max - height[left]
            left += 1
        else:
            right_max = max(right_max, height[right])
            water += right_max - height[right]
            right -= 1
    return water
''')
SLIDING = dedent('''\
def sliding_window_maximum(nums, k):
    from collections import deque
    candidates = deque()
    answer = []
    for index, value in enumerate(nums):
        while candidates and candidates[0] <= index - k:
            candidates.popleft()
        while candidates and nums[candidates[-1]] <= value:
            candidates.pop()
        candidates.append(index)
        if index >= k - 1:
            answer.append(nums[candidates[0]])
    return answer
''')

TREE_CASES = [[], [0], [1,2], [1,None,2], [1,2,3], [1,2,2],
              [0,-1,1], [1,2,None,3], [1,None,2,None,3], [1,2,3,4,None,None,5],
              [-100,100], [1,1,1,1,1]]

BATCH = {
    226: dict(name="invert_tree", topics=["trees", "recursion"], params=[("root", "TreeNode | None", "treenode")],
        returns="TreeNode | None", adapter="treenode", difficulty=3,
        constraints=["The tree has 0–100 nodes.", "-100 <= node.val <= 100.", "Input and output are displayed in level order; null denotes a missing child."],
        time="O(n)", space="O(h) recursive stack",
        examples=[([[4,2,7,1,3,6,9]], "Swap children at every node: 7 moves left of 4, 2 moves right, and their own children are swapped as well."),
                  ([[2,1,3]], "The root remains 2; its left and right child values become 3 and 1.")],
        boundaries=[[tree] for tree in TREE_CASES], reference=INVERT, oracle=invert_oracle, generator=random_single,
        wrong=["def invert_tree(root):\n    return root\n",
               "def invert_tree(root):\n    if root is not None:\n        root.left, root.right = root.right, root.left\n    return root\n"],
        wrong_reasons=["Leaves the tree unchanged.", "Swaps only the root's children, leaving deeper subtrees uninverted."],
        hints=["The same operation is needed at every node, including descendants.", "Invert each subtree and assign it to the opposite child position.",
               "An empty node returns empty. Otherwise recursively invert right into left and left into right, then return the node.",
               "The base case ends at missing children; every real node is visited exactly once."],
        editorial="Inverting a tree means exchanging the left and right subtree at each node. Recursively invert both children, then attach the inverted former right subtree on the left and vice versa. The root's value does not change. A missing child in one tree position becomes a missing child at the mirrored position. Time is linear and recursion uses a path of height h."),
    101: dict(name="symmetric_tree", topics=["trees", "recursion", "depth-first-search"], params=[("root", "TreeNode", "treenode")],
        returns="bool", adapter="raw", difficulty=3,
        constraints=["The tree contains 1–1000 nodes.", "-100 <= node.val <= 100.", "Symmetry requires matching values and mirrored missing-child positions."],
        time="O(n)", space="O(h)",
        examples=[([[1,2,2,3,4,4,3]], "The two 2 nodes match, their outer children are both 3, and their inner children are both 4."),
                  ([[1,2,2,None,3,None,3]], "The two 3 nodes both point right from their parents. Mirror symmetry requires opposite directions.")],
        boundaries=[[[0]], [[1,2]], [[1,None,2]], [[1,2,2]], [[1,2,3]], [[1,2,2,3,None,None,3]],
                    [[1,2,2,None,3,3]], [[1,2,2,3,None,3]], [[1,-1,-1]], [[1,-1,1]],
                    [[1,2,2,3,4,4,5]], [[0]*31]],
        reference=SYMMETRIC, oracle=symmetric_oracle, generator=random_symmetric,
        wrong=[SYMMETRIC.replace("if left.val != right.val:", "if False:"),
               SYMMETRIC.replace("(left.left, right.right)", "(left.left, right.left)").replace("(left.right, right.left)", "(left.right, right.right)")],
        wrong_reasons=["Checks mirrored shape but ignores values.", "Compares the same child directions rather than mirror directions."],
        hints=["A mirror compares opposite directions, not simply equal traversal values.", "Compare pairs of nodes: outer children together, then inner children together.",
               "For a pair, reject exactly one missing node or unequal values. Then compare left.left with right.right and left.right with right.left.",
               "A recursive mirror check or a stack of mirrored pairs preserves missing-child positions."],
        editorial="Begin with the root's left and right children. Two absent nodes match; exactly one absent node fails. Present nodes must have equal values. Continue with their outer pair and inner pair. The reference uses an explicit stack to avoid Python recursion-depth limits while performing the same comparisons as the recursive definition."),
    110: dict(name="balanced_tree", topics=["trees", "recursion", "depth-first-search"], params=[("root", "TreeNode | None", "treenode")],
        returns="bool", adapter="raw", difficulty=3,
        statement="Return whether the tree is height-balanced: at every node, the heights of its left and right subtrees differ by at most one. An empty subtree has height zero, and an empty tree is balanced.",
        constraints=["The tree contains 0–5000 nodes.", "-10,000 <= node.val <= 10,000.", "Check the balance condition at every node, not only the root."],
        time="O(n)", space="O(n)",
        examples=[([[3,9,20,None,None,15,7]], "The root's subtree heights are 1 and 2; every descendant also differs by at most one."),
                  ([[1,2,2,3,3,None,None,4,4]], "The left subtree has height 3 while the right subtree has height 1, so the root is unbalanced.")],
        boundaries=[[tree] for tree in TREE_CASES],
        stress=[([[0] * 5000], True)],
        reference=BALANCED, oracle=balanced_oracle, generator=random_single,
        wrong=[BALANCED.replace("abs(left - right) > 1", "abs(left - right) > 0"),
               BALANCED.replace("abs(left - right) > 1", "abs(left - right) > 2")],
        wrong_reasons=["Requires exactly equal heights instead of allowing a difference of one.", "Incorrectly permits height differences of two."],
        hints=["A subtree's height can be reused by its parent.", "Process children before their parent and reject as soon as any local height difference exceeds one.",
               "Compute both child heights. If their difference exceeds one, fail. Otherwise store one plus the larger height for the parent.",
               "Postorder traversal avoids repeatedly recalculating every subtree's height."],
        editorial="Compute child heights before visiting a parent. At each parent, check their absolute difference and record one plus the larger height. This checks every node rather than only the root. An explicit postorder stack and a height dictionary handle very deep inputs without a recursion-limit failure. Each node is processed a constant number of times."),
    112: dict(name="has_path_sum", topics=["trees", "recursion", "depth-first-search"], params=[("root", "TreeNode | None", "treenode"), ("target_sum", "int", "raw")],
        returns="bool", adapter="raw", difficulty=3,
        constraints=["The tree contains 0–5000 nodes.", "-1000 <= node.val <= 1000 and -1000 <= target_sum <= 1000.",
                     "A leaf has neither a left nor a right child. An empty tree has no qualifying path."],
        time="O(n)", space="O(h)",
        examples=[([[5,4,8,11,None,13,4,7,2,None,None,None,1],22], "The path 5 → 4 → 11 → 2 ends at a leaf and sums to 22."),
                  ([[1,2,3],5], "The only root-to-leaf sums are 1+2=3 and 1+3=4; neither is 5.")],
        boundaries=[[[],0], [[1],1], [[1],0], [[1,2],1], [[1,2],3], [[1,None,2],3],
                    [[-2,None,-3],-5], [[0,0,0],0], [[1,-2,3,1,3,-2,None,-1],-1],
                    [[1000,-1000],0], [[1,2,3],3], [[1,2,3],4]],
        stress=[([[0] * 5000, 1], False)],
        reference=PATH, oracle=path_oracle, generator=random_path,
        wrong=[PATH.replace("node.left is None and node.right is None and total == target_sum", "total == target_sum"),
               PATH.replace("if node.right is not None:", "if False:")],
        wrong_reasons=["Accepts a matching prefix that does not end at a leaf.", "Skips every right-child path."],
        hints=["A matching sum is valid only at a leaf.", "Carry the sum from the root along each candidate path; do not stop merely because it equals the target at an internal node.",
               "Visit a node with its running total. At a leaf compare with target; otherwise continue into each existing child with its value added.",
               "Negative values rule out pruning just because a partial sum exceeds the target."],
        editorial="Use depth-first traversal while carrying each root-to-current-node sum. Compare with the target only when both child pointers are absent. An internal node with the target sum is not a root-to-leaf path. Explore both branches, including negative values, without pruning by the current total. The explicit stack keeps deep trees within the Python runtime's limits."),
    617: dict(name="merge_trees", topics=["trees", "recursion"], params=[("root1", "TreeNode | None", "treenode"), ("root2", "TreeNode | None", "treenode")],
        returns="TreeNode | None", adapter="treenode", difficulty=3,
        constraints=["Each input tree has 0–2000 nodes.", "-10,000 <= node.val <= 10,000.",
                     "Sum nodes at the same structural position; retain any position present in only one input."],
        time="O(n + m)", space="O(n + m) including output",
        examples=[([[1,3,2,5],[2,1,3,None,4,None,7]], "Overlapping roots/children sum to 3,4,5. The unmatched nodes 5,4,7 retain their positions, yielding [3,4,5,5,4,null,7]."),
                  ([[1],[1,2]], "The roots sum to 2, and the second tree's unmatched left child 2 is retained.")],
        boundaries=[[[],[]], [[1],[]], [[],[1]], [[1],[2]], [[-1],[1]], [[1,2],[3,None,4]],
                    [[1,None,2],[3,4]], [[0,0,0],[0]], [[1,2,3],[4,5,6]],
                    [[1,2,None,3],[4]], [[1],[4,None,5,None,6]], [[10000],[-10000,-10000]]],
        reference=MERGE, oracle=merge_oracle, generator=random_pair,
        wrong=[MERGE.replace("output.val = left.val + right.val", "output.val = left.val"),
               MERGE.replace("a if a is not None else b", "None")],
        wrong_reasons=["Keeps the first value instead of summing overlapping nodes.", "Drops unmatched subtrees."],
        hints=["Tree positions, rather than array indices in the display, decide which values overlap.", "For a pair of nodes, reuse the present subtree when only one exists; otherwise combine values and continue with both child pairs.",
               "If either root is absent, return the other. Otherwise create a node with their sum and merge the left pair and right pair into its children.",
               "A stack of input pairs and output nodes implements the recursive rule without a deep call stack."],
        editorial="Merge corresponding structural positions. A position occupied by both inputs gets the sum of the two values. A position occupied by one input retains that entire subtree. Do not simply add the displayed arrays by index: null placeholders and omitted trailing children make that incorrect. The iterative reference creates nodes for overlapping pairs and retains unmatched branches."),
    25: dict(name="reverse_k_group", topics=["linked-lists", "pointer-manipulation"], prerequisites=["linked-lists"],
        params=[("head", "ListNode", "listnode"), ("k", "int", "raw")], returns="ListNode", adapter="listnode", node_policy="reuse_input_nodes", difficulty=8,
        constraints=["1 <= k <= number of nodes <= 5000.", "0 <= node.val <= 1000.",
                     "Reconnect the original nodes without changing their values; leave an incomplete final group in its original order."],
        time="O(n)", space="O(1)",
        examples=[([[1,2,3,4,5],2], "Reverse the complete pairs (1,2) and (3,4). The remaining node 5 stays in place."),
                  ([[1,2,3,4,5],3], "Reverse the first three nodes. The final two nodes are not a complete group, so retain 4 → 5.")],
        boundaries=[[[1],1], [[1,2],1], [[1,2],2], [[1,2,3],2], [[1,2,3],3], [[1,2,3,4],2],
                    [[1,2,3,4,5,6],3], [[1,2,3,4,5,6,7,8],3], [[0,0,1,1,2],2], [[1000,0,1000],2],
                    [[1,2,3,4],4], [[1,2,3,4,5,6,7],4]],
        stress=[([[i % 1001 for i in range(5000)],1], [i % 1001 for i in range(5000)])],
        reference=REVERSE, oracle=reverse_oracle, generator=random_reverse,
        wrong=[REVERSE.replace("range(k)", "range(1)"),
               REVERSE.replace("previous_group = old_head", "return dummy.next")],
        wrong_reasons=["Treats every group as a singleton, so no reversal occurs.", "Reverses the first complete group but stops before later groups."],
        hints=["Before changing pointers, establish whether a full group of k nodes exists.", "Keep the node before the group and the node after it so the reversed chain can reconnect at both ends.",
               "Find the kth node. If absent, stop. Reverse until the following node; connect the previous group to the old kth node, then advance to the old group head.",
               "The former head becomes the new tail and the predecessor of the next group."],
        editorial="A dummy head gives the first group the same predecessor interface as later groups. Look ahead k nodes before mutating anything, leaving an incomplete group intact. Reverse one complete group's next pointers with the following node as the initial previous pointer, reconnect the predecessor to the old kth node, and continue from the old head. The judge checks node identity and unchanged values as well as the resulting order."),
    42: dict(name="trapped_water", topics=["arrays", "two-pointers", "stacks"], prerequisites=["two-pointers"],
        params=[("height", "list[int]", "raw")], returns="int", adapter="raw", difficulty=8,
        constraints=["1 <= len(height) <= 20,000.", "0 <= height[i] <= 100,000.", "Every bar has width one."],
        time="O(n)", space="O(1)",
        examples=[([[0,1,0,2,1,0,1,3,2,1,2,1]], "The trapped depths at indices 2,4,5,6,9 are 1,1,2,1,1, totaling 6."),
                  ([[4,2,0,3,2,5]], "The internal depths are 2,4,1,2; their sum is 9.")],
        boundaries=[[[0]], [[1]], [[1,2]], [[2,1]], [[2,0,2]], [[3,0,1]], [[1,0,3]],
                    [[3,3,3]], [[0,1,2,3]], [[3,2,1,0]], [[5,0,0,5]], [[2,0,2,0,2]]],
        stress=[([[100000] + [0] * 19998 + [100000]], 1999800000)],
        reference=RAIN, oracle=rain_oracle, generator=random_rain,
        wrong=[RAIN.replace("left_max <= right_max", "left_max >= right_max"),
               "def trapped_water(height):\n    return sum(max(0, min(height[i-1], height[i+1]) - height[i]) for i in range(1, len(height)-1))\n"],
        wrong_reasons=["Finalizes depths using the larger boundary before the smaller side is known.", "Looks only at immediate neighbors, missing wider basins."],
        hints=["Water at one index is limited by the smaller of the best walls on its two sides.", "Track maximum walls seen from both ends; the smaller wall determines which side can be finalized.",
               "Advance the side with smaller known maximum. Update that maximum and add the difference between it and the current bar.",
               "Each index contributes a nonnegative depth exactly once."],
        editorial="The depth above an index is the smaller of its highest left and right barriers minus its own height, clipped at zero. Scan inward with the highest barrier seen from each end. When one known barrier is smaller, the opposite known barrier already suffices to bound that side, so its contribution is final. Moving each pointer inward once gives linear time and constant extra space."),
    239: dict(name="sliding_window_maximum", topics=["arrays", "sliding-window", "queues", "monotonic-queue"], prerequisites=["sliding-window"],
        params=[("nums", "list[int]", "raw"), ("k", "int", "raw")], returns="list[int]", adapter="raw", difficulty=8,
        constraints=["1 <= k <= len(nums) <= 100,000.", "-10,000 <= nums[i] <= 10,000.", "Return one maximum for each consecutive length-k window, in window order."],
        time="O(n)", space="O(k) excluding output",
        examples=[([[1,3,-1,-3,5,3,6,7],3], "The six windows have maxima 3,3,5,5,6,7. A maximum stops counting when its index leaves the window."),
                  ([[1],1], "The only window contains the only value 1.")],
        boundaries=[[[0],1], [[-1],1], [[1,2],1], [[1,2],2], [[2,1],2], [[5,5,5],2],
                    [[-5,-2,-3],2], [[9,1,2,3],2], [[1,2,3,4],3], [[4,3,2,1],3],
                    [[5,1,5,1,5],2], [[-10000,10000,0],3]],
        stress=[([[7] * 100000, 99999], [7,7])],
        reference=SLIDING, oracle=sliding_oracle, generator=random_sliding,
        wrong=[SLIDING.replace("candidates[0] <= index - k", "candidates[0] < index - k"),
               SLIDING.replace("answer.append(nums[candidates[0]])", "answer.append(nums[candidates[-1]])")],
        wrong_reasons=["Keeps the previous window's expired maximum for one extra step.", "Returns the newest candidate rather than the maximum at the front."],
        hints=["A smaller earlier value cannot become a future maximum while a larger later value remains.", "Keep candidate indices in a deque with decreasing values, discarding expired indices from the front.",
               "Expire indices outside the window. Remove no-larger values from the back. Append the new index and emit the front once a full window exists.",
               "Each index enters and leaves the deque at most once, giving linear total work."],
        editorial="Store indices so expiration can be checked precisely. Values along the deque decrease: when a new value arrives, remove smaller or equal values at the back, since the new value is at least as good and expires later. Remove indices before the current window from the front. The front then holds the current maximum. Begin emitting only after k elements have arrived."),
}
