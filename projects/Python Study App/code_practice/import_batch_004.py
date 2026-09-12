"""Reviewed linked-list and tree contracts; no multi-operation design interface.

Oracles operate on arrays and binary-path maps, independently of the reference
implementations' pointer manipulation and postorder state.
"""
from textwrap import dedent

from .import_batch_002 import positions, flatten, random_tree


def remove_oracle(args):
    values, n = args
    index = len(values) - n
    return values[:index] + values[index + 1:]


def swap_oracle(args):
    values, = args
    return [values[i ^ 1] if (i ^ 1) < len(values) else values[i] for i in range(len(values))]


def segment_oracle(args):
    values, left, right = args
    return values[:left - 1] + values[left - 1:right][::-1] + values[right:]


def number_oracle(args):
    mapping = positions(args[0])
    leaves = [p for p in mapping if p + (0,) not in mapping and p + (1,) not in mapping]
    return sum(int("".join(str(mapping[p[:i]]) for i in range(len(p) + 1))) for p in leaves)


def kth_oracle(args):
    return sorted(value for value in args[0] if value is not None)[args[1] - 1]


def left_oracle(args):
    mapping = positions(args[0])
    return sum(value for p, value in mapping.items() if p and p[-1] == 0
               and p + (0,) not in mapping and p + (1,) not in mapping)


def diameter_oracle(args):
    # Direct all-pairs path distance, rather than height-based tree DP.
    keys = list(positions(args[0]))
    longest = 0
    for a in keys:
        for b in keys:
            shared = 0
            while shared < min(len(a), len(b)) and a[shared] == b[shared]:
                shared += 1
            longest = max(longest, len(a) + len(b) - 2 * shared)
    return longest


def tilt_oracle(args):
    mapping = positions(args[0])
    total = 0
    for key in mapping:
        sums = [sum(v for p, v in mapping.items() if p[:len(key) + 1] == key + (side,)) for side in (0, 1)]
        total += abs(sums[0] - sums[1])
    return total


def search_oracle(args):
    mapping = positions(args[0])
    found = next((p for p, value in mapping.items() if value == args[1]), None)
    return [] if found is None else flatten({p[len(found):]: value for p, value in mapping.items() if p[:len(found)] == found})


def random_remove(rng):
    values = [rng.randrange(101) for _ in range(rng.randint(1, 30))]
    return [values, rng.randint(1, len(values))]


def random_swap(rng):
    return [[rng.randrange(101) for _ in range(rng.randrange(101))]]


def random_segment(rng):
    values = [rng.randint(-500, 500) for _ in range(rng.randint(1, 60))]
    left = rng.randint(1, len(values))
    return [values, left, rng.randint(left, len(values))]


def random_numbers(rng):
    # Depth <= 6 keeps every generated total inside signed 32-bit bounds.
    mapping = {(): rng.randrange(10)}
    for depth in range(5):
        for p in [key for key in mapping if len(key) == depth]:
            for side in (0, 1):
                if rng.random() < .7:
                    mapping[p + (side,)] = rng.randrange(10)
    return [flatten(mapping)]


def random_bst(rng):
    # Insert values using path keys only, without reference TreeNode objects.
    mapping = {}
    for value in rng.sample(range(1, 101), rng.randint(1, 30)):
        key = ()
        while key in mapping:
            key += (int(value > mapping[key]),)
        mapping[key] = value
    return flatten(mapping)


def random_kth(rng):
    tree = random_bst(rng)
    return [tree, rng.randint(1, sum(x is not None for x in tree))]


def random_search(rng):
    tree = random_bst(rng)
    return [tree, rng.choice([x for x in tree if x is not None]) if rng.random() < .6 else rng.randint(1, 150)]


def random_nonempty(rng):
    return [random_tree(rng, nonempty=True)]


def random_tilt(rng):
    return [random_tree(rng)]


REMOVE = '''\
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next
    while fast.next:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next
'''
SWAP = '''\
def swap_pairs(head):
    if head is None or head.next is None:
        return head
    second = head.next
    rest = swap_pairs(second.next)
    second.next = head
    head.next = rest
    return second
'''
SEGMENT = '''\
def reverse_between(head, left, right):
    dummy = ListNode(0, head)
    before = dummy
    for _ in range(left - 1):
        before = before.next
    tail = before.next
    for _ in range(right - left):
        moving = tail.next
        tail.next = moving.next
        moving.next = before.next
        before.next = moving
    return dummy.next
'''
NUMBERS = '''\
def sum_root_numbers(root):
    def visit(node, prefix):
        if node is None:
            return 0
        value = prefix * 10 + node.val
        if node.left is None and node.right is None:
            return value
        return visit(node.left, value) + visit(node.right, value)
    return visit(root, 0)
'''
KTH = '''\
def kth_smallest_bst(root, k):
    stack = []
    while root or stack:
        while root:
            stack.append(root)
            root = root.left
        root = stack.pop()
        k -= 1
        if k == 0:
            return root.val
        root = root.right
'''
LEFT = '''\
def sum_left_leaves(root):
    total = 0
    stack = [(root, False)]
    while stack:
        node, is_left = stack.pop()
        if node is None:
            continue
        if is_left and node.left is None and node.right is None:
            total += node.val
        stack.append((node.left, True))
        stack.append((node.right, False))
    return total
'''
DIAMETER = '''\
def tree_diameter(root):
    stack, heights, best = [(root, False)], {}, 0
    while stack:
        node, visited = stack.pop()
        if node is None:
            continue
        if not visited:
            stack.extend([(node, True), (node.right, False), (node.left, False)])
        else:
            left = heights.pop(node.left, 0)
            right = heights.pop(node.right, 0)
            best = max(best, left + right)
            heights[node] = 1 + max(left, right)
    return best
'''
TILT = '''\
def tree_tilt(root):
    stack, sums, total = [(root, False)], {}, 0
    while stack:
        node, visited = stack.pop()
        if node is None:
            continue
        if not visited:
            stack.extend([(node, True), (node.right, False), (node.left, False)])
        else:
            left = sums.pop(node.left, 0)
            right = sums.pop(node.right, 0)
            total += abs(left - right)
            sums[node] = node.val + left + right
    return total
'''
SEARCH = '''\
def search_bst(root, val):
    while root and root.val != val:
        root = root.left if val < root.val else root.right
    return root
'''


def spec(name, params, returns, adapter, difficulty, topics, constraints, examples, hidden,
         reference, wrong, reasons, oracle, generator, hints, editorial, time, space,
         policy="values", stress=()):
    return dict(name=name, params=params, returns=returns, adapter=adapter,
                difficulty=difficulty, topics=topics, constraints=constraints,
                examples=examples, boundaries=hidden, reference=dedent(reference),
                wrong=[dedent(s) for s in wrong], wrong_reasons=reasons,
                oracle=oracle, generator=generator, hints=hints, editorial=editorial,
                time=time, space=space, node_policy=policy, stress=list(stress))


TREE = [("root", "TreeNode | None", "treenode")]
LIST = [("head", "ListNode | None", "listnode")]
# Structurally varied trees: left/right chains, interior gaps, negative and equal
# values, and a longest path wholly below the root. All obey the source bounds.
TREES = [[0], [-1], [1, 2], [1, None, 2], [1, 2, 3], [1, 2, None, 3],
         [1, None, 2, None, 3], [1, 2, 3, 4], [1, -2, 3], [0, 0, 0],
         [1, 2, None, 3, 4, 5, None, None, 6], [1, 2, 3, None, 4, 5]]

BATCH = {
    19: spec("remove_nth_from_end", LIST + [("n", "int", "raw")], "ListNode | None", "listnode", 5,
        ["linked-lists", "two-pointers"], ["1–30 nodes; each value is between 0 and 100.", "1 <= n <= number of nodes. Count positions from the tail starting at one."],
        [([[1,2,3,4,5],2], "The second node from the end holds 4. Removing it leaves 1→2→3→5."),
         ([[1],1], "The only node is removed, so return None (displayed as []).")],
        [[[1,2],1], [[1,2],2], [[1,2,3],1], [[1,2,3],2], [[1,2,3],3],
         [[0],1], [[0,0],2], [[9,9,1],2], [[3,2,1,0],4], [[1,1,1],1],
         [[100,0,100,0],3], [list(range(30)),15]], REMOVE,
        [REMOVE.replace("return dummy.next", "return head"), '''def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    before = dummy
    for _ in range(n - 1):
        before = before.next
    before.next = before.next.next
    return dummy.next
'''], ["Returns the old head even when the head was removed.", "Counts from the front rather than from the end."], remove_oracle, random_remove,
        ["A fixed gap between two pointers can locate a node relative to the tail.", "Start from a sentinel so deleting the first real node needs no special case.", "Advance fast n links, move both until fast is last, then bypass slow.next.", "Return the sentinel's current next pointer, not the original head."],
        "Advance a fast pointer n nodes ahead of a slow pointer, both initially at a sentinel before the list. Move them together until fast reaches the last node. Slow is then immediately before the node to delete. Bypass that node and return the sentinel's next pointer. The constant pointer gap proves the removed node has exactly n-1 nodes after it.", "O(n)", "O(1)"),
    24: spec("swap_pairs", LIST, "ListNode | None", "listnode", 5, ["linked-lists", "recursion"],
        ["0–100 nodes; each value is between 0 and 100.", "Reconnect the original nodes; do not alter node values. Leave an unpaired final node unchanged."],
        [([[1,2,3,4]], "Swap 1 with 2 and 3 with 4, yielding 2→1→4→3."),
         ([[1,2,3]], "The first pair swaps; the final 3 has no partner and stays last.")],
        [[v] for v in ([], [1], [0], [1,2], [2,1], [1,1], [0,1,0], [1,1,2,2], [5,4,3,2,1],
                         [0,100,0,100], list(range(8)), list(range(100)))], SWAP,
        [SWAP.replace("rest = swap_pairs(second.next)", "rest = second.next"),
         '''def swap_pairs(head):
    node = head
    while node and node.next:
        node.val, node.next.val = node.next.val, node.val
        node = node.next.next
    return head
'''], ["Swaps only the first pair, leaving the rest untouched.", "Swaps stored values rather than reconnecting nodes."], swap_oracle, random_swap,
        ["The first two nodes and the remaining list form a smaller copy of the same task.", "Recursively swap the remainder, then place the second node before the first.", "Base case: fewer than two nodes. Otherwise swap the tail after the pair, attach first to that tail, and second to first.", "Save the second node and tail before rewiring to avoid losing them or creating a cycle."],
        "With fewer than two nodes there is nothing to exchange. Otherwise retain the second node and recursively transform the list after it. Connect the first node to that transformed tail, then connect the second node to the first. The second node becomes the head of this segment. Recursion has at most 50 levels under the constraints; an iterative sentinel-based solution can reduce auxiliary space to constant.", "O(n)", "O(n) recursive stack", policy="reuse_input_nodes"),
    92: spec("reverse_between", LIST + [("left","int","raw"),("right","int","raw")], "ListNode | None", "listnode", 5,
        ["linked-lists"], ["1–500 nodes with values in [-500, 500].", "1 <= left <= right <= node count; positions are one-indexed.", "Reverse the nodes in the inclusive segment, preserving every node and its value."],
        [([[1,2,3,4,5],2,4], "Only positions 2 through 4 reverse: 1→4→3→2→5."),
         ([[5],1,1], "A one-node segment is unchanged.")],
        [[[1,2],1,1], [[1,2],2,2], [[1,2],1,2], [[1,2,3],1,3], [[1,2,3],1,2], [[1,2,3],2,3],
         [[-1,0,1,2],2,4], [[1,1,2,2],1,4], [[0],1,1], [[1,2,3,4],3,4],
         [[9,8,7,6,5],2,3], [list(range(500)),1,500]], SEGMENT,
        [SEGMENT.replace("range(right - left)", "range(max(0, right - left - 1))"),
         SEGMENT.replace("range(left - 1)", "range(0)")],
        ["Reverses one fewer node by treating the right boundary as exclusive.", "Reverses from the head instead of from the requested left boundary."], segment_oracle, random_segment,
        ["Locate the node just before the segment; a sentinel also covers left=1.", "Keep the segment's original first node as a tail and move its next node to the segment front repeatedly.", "Repeat right-left times: detach tail.next and insert it immediately after before.", "The unaffected prefix and suffix remain attached throughout."],
        "Walk left-1 links from a sentinel to the node before the segment. Its next node will become the reversed segment's tail. Repeatedly remove the node after that tail and insert it at the segment front. After right-left moves, the requested inclusive segment is reversed without losing the suffix. Return the sentinel's next node.", "O(n)", "O(1)", policy="reuse_input_nodes"),
    129: spec("sum_root_numbers", TREE, "int", "raw", 5, ["trees", "recursion"],
        ["1–1000 nodes, each holding a digit 0–9. Tree depth is at most 10.", "The total answer fits a signed 32-bit integer. Count only complete root-to-leaf paths."],
        [([[1,2,3]], "The two paths represent 12 and 13; their sum is 25."),
         ([[4,9,0,5,1]], "The complete paths represent 495, 491, and 40; their sum is 1026.")],
        [[v] for v in ([0],[1],[9],[1,2],[1,None,2],[0,1,2],[1,0,0],[1,2,None,3],
                       [1,None,2,None,3],[2,3,4,5],[0,0,0],[9,9,9])], NUMBERS,
        [NUMBERS.replace("prefix * 10 + node.val", "prefix + node.val"),
         NUMBERS.replace("return visit(node.left, value) + visit(node.right, value)", "return value + visit(node.left, value) + visit(node.right, value)")],
        ["Adds digits instead of concatenating their decimal positions.", "Includes unfinished root-to-internal-node paths in the total."], number_oracle, random_numbers,
        ["A path's numeric prefix can be carried from parent to child.", "Append a digit with prefix*10+digit, and contribute only when both children are absent.", "Return the current number at a leaf; otherwise sum the recursive results for both children.", "A missing child contributes zero, not an additional copy of the prefix."],
        "A recursive call carries the number represented by the path before the current node. Multiply by ten and add the current digit to extend it. At a leaf, return that complete number; at an internal node, add the totals from the existing branches. The depth limit keeps the call stack small. The oracle independently constructs decimal strings from root-to-leaf path keys.", "O(n)", "O(h)"),
    230: spec("kth_smallest_bst", TREE + [("k","int","raw")], "int", "raw", 5, ["trees", "binary-search"],
        ["1 <= k <= node count <= 10,000. Node values are in [0, 10,000].", "The input is a binary search tree. k is one-indexed."],
        [([[3,1,4,None,2],1], "In sorted order the values are 1,2,3,4; the first is 1."),
         ([[5,3,6,2,4,None,None,1],3], "The sorted order is 1,2,3,4,5,6; the third is 3.")],
        [[[0],1], [[1],1], [[2,1],1], [[2,1],2], [[1,None,2],1], [[1,None,2],2],
         [[2,1,3],1], [[2,1,3],2], [[2,1,3],3], [[4,2,6,1,3,5,7],4],
         [[4,2,6,1,3,5,7],7], [[10000,9999],2]], KTH,
        [KTH.replace("k -= 1", "k -= 0").replace("if k == 0:", "if k == 1:"),
         KTH.replace("root = root.left", "root = REVERSE").replace("root = root.right", "root = root.left").replace("root = REVERSE", "root = root.right")],
        ["Never advances the rank counter for k greater than one.", "Walks the wrong subtrees instead of maintaining inorder order."], kth_oracle, random_kth,
        ["Inorder traversal of a BST visits values in increasing order.", "Use a stack to reach the next smallest unvisited node without sorting all values.", "Push a left spine, pop and decrement k, return at zero, then traverse the popped node's right subtree.", "An explicit stack also handles highly skewed trees without Python recursion-depth errors."],
        "Push the root's entire left spine. The next popped node is the smallest unvisited value. Decrement the remaining rank and return its value when the rank reaches zero. Otherwise visit its right subtree by pushing that subtree's left spine. Each visited node is processed once, with O(h) stack entries and O(h+k) time before the kth result.", "O(h + k)", "O(h)"),
    404: spec("sum_left_leaves", TREE, "int", "raw", 3, ["trees", "recursion"],
        ["1–1000 nodes; node values are in [-1000, 1000].", "A left leaf has no children and is its parent's left child. The root itself is never a left leaf."],
        [([[3,9,20,None,None,15,7]], "9 and 15 are left children with no children of their own. Their sum is 24; right leaf 7 is not counted."),
         ([[1]], "The root has no parent, so it contributes zero despite being a leaf.")],
        [[v] for v in TREES], LEFT,
        [LEFT.replace("if is_left and node.left is None and node.right is None:", "if is_left:"),
         LEFT.replace("if is_left and node.left is None and node.right is None:", "if node.left is None and node.right is None:")],
        ["Counts left children that are internal nodes.", "Counts right leaves and the root leaf as well."], left_oracle, random_nonempty,
        ["Being a left child and being a leaf are separate requirements.", "Carry a flag indicating whether each visited node came from a left edge.", "Add a value only when the flag is true and both children are absent; push children with their corresponding flags.", "Start the root with a false flag. The same state can be passed through recursion."],
        "Traverse the tree with pairs of a node and a left-child flag. A node contributes precisely when its flag is true and it has no children. Each left child gets a true flag; each right child gets false. The root starts false. The explicit stack avoids recursion limits on a 1000-node chain, while expressing the same state that a recursive solution would pass.", "O(n)", "O(h)"),
    543: spec("tree_diameter", TREE, "int", "raw", 3, ["trees", "recursion"],
        ["1–10,000 nodes; node values are in [-100, 100].", "Measure path length in edges. The longest path need not pass through the root."],
        [([[1,2,3,4,5]], "The path 4→2→1→3 has three edges, which is maximal."),
         ([[1,2]], "Two connected nodes have a path of one edge.")],
        [[v] for v in TREES if v != [1,2]] + [[[7,7,7,7,7,7,7]]], DIAMETER,
        [DIAMETER.replace("best = max(best, left + right)", "best = max(best, left + right + 1)"),
         DIAMETER.replace("best = max(best, left + right)", "best = left + right")],
        ["Counts nodes instead of edges in the candidate path.", "Overwrites the best subtree path and keeps only the path through the root."], diameter_oracle, random_nonempty,
        ["The longest path through a node joins its deepest left and right descendants.", "Compute child heights before the parent and keep a separate global best path.", "For each postorder node, update best with left_height+right_height, then return height 1+max(left_height,right_height).", "The height returned to a parent and the best path anywhere in the tree are different quantities."],
        "Postorder traversal makes both child heights available before a node is processed. Their sum is the number of edges in the longest path whose highest node is this node. Maximize that candidate over every node, not just the root. Return one plus the larger child height upward. The implementation uses explicit visited-state frames and discards child heights after use, so its auxiliary storage is O(h), without relying on Python recursion depth.", "O(n)", "O(h)",
        stress=[([[0,None] * 9999 + [0]],9999)]),
    563: spec("tree_tilt", TREE, "int", "raw", 3, ["trees", "recursion"],
        ["0–10,000 nodes; values are in [-1000, 1000].", "A node's tilt is abs(sum of left subtree - sum of right subtree). Return the sum of tilts at every node."],
        [([[1,2,3]], "The root's tilt is |2−3|=1 and each leaf has tilt zero, so the total is 1."),
         ([[4,2,9,3,5,None,7]], "The nonzero tilts are 2 at node 2, 7 at node 9, and 6 at node 4, totaling 15.")],
        [[v] for v in TREES if v != [1,2,3]] + [[[]]], TILT,
        [TILT.replace("total += abs(left - right)", "total += left - right"),
         TILT.replace("sums[node] = node.val + left + right", "sums[node] = node.val")],
        ["Omits absolute value, allowing positive and negative differences to cancel.", "Uses only immediate child values instead of complete subtree sums."], tilt_oracle, random_tilt,
        ["A parent's tilt depends on subtree sums, not child tilts.", "Compute sums bottom-up and accumulate each node's absolute difference separately.", "After both children, add abs(left_sum-right_sum) to the total and pass node.val+left_sum+right_sum upward.", "Negative node values still participate in subtree sums before taking the absolute difference."],
        "Process nodes after their children. Add the absolute difference of their two subtree sums to a running total, and retain the complete sum including the current value for the parent. Do not replace a subtree sum with its tilt, height, or immediate child value. An explicit postorder stack supports deep chains; consumed child sums are removed to keep auxiliary storage proportional to tree height.", "O(n)", "O(h)",
        stress=[([[1,None] * 9999 + [1]],49995000)]),
    700: spec("search_bst", TREE + [("val","int","raw")], "TreeNode | None", "treenode", 3, ["trees", "binary-search"],
        ["The input is a BST with 1–5000 nodes. Node values and val are in [1, 10^7].", "Return the complete subtree rooted at the matching node, or None (displayed as []) if absent."],
        [([[4,2,7,1,3],2], "The matching node is 2; return it with descendants 1 and 3, displayed as [2,1,3]."),
         ([[4,2,7,1,3],5], "The search goes right to 7, then left to an empty child. No node holds 5.")],
        [[[1],1], [[1],2], [[2,1],1], [[2,1],2], [[2,1],3], [[1,None,2],2],
         [[4,2,6,1,3,5,7],4], [[4,2,6,1,3,5,7],6], [[4,2,6,1,3,5,7],7],
         [[4,2,6,1,3,5,7],8], [[10,5,None,None,7],5], [[10000000],1]], SEARCH,
        [SEARCH.replace("val < root.val", "val > root.val"),
         SEARCH.replace("return root", "return TreeNode(root.val) if root else None")],
        ["Chooses the opposite BST branch after a comparison.", "Returns just the matching value as a new leaf, discarding its subtree."], search_oracle, random_search,
        ["The BST ordering tells you which single branch can contain the target.", "Compare at each node: smaller goes left, larger goes right, equal returns that node.", "Repeat until finding val or reaching None. Return the node itself, with its children still attached.", "Do not return only its value or construct a leaf copy; the output is a subtree."],
        "At each node, BST ordering rules out the entire right subtree for a smaller target and the entire left subtree for a larger one. Follow the remaining branch until equality or a missing child. Returning the matching node preserves all of its descendants. This takes O(h) time and constant extra space iteratively; a recursive version needs O(h) call-stack space.", "O(h)", "O(1)"),
}
