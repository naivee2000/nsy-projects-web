"""In-place tree/list rewiring: original node identity and order are graded."""
from collections import deque

from .import_batch_002 import positions, random_tree
from .import_batch_003 import entry


def right_chain(values):
    return [item for value in values for item in (value, None)][:-1]


def flatten_oracle(args):
    mapping = positions(args[0])
    return right_chain([mapping[path] for path in sorted(mapping)])


def flatten_node_order(args):
    return list(range(sum(value is not None for value in args[0])))


def reorder_oracle(args):
    remaining, answer = deque(args[0]), []
    while remaining:
        answer.append(remaining.popleft())
        if remaining:
            answer.append(remaining.pop())
    return answer


def reorder_node_order(args):
    count = len(args[0])
    return sorted(range(count), key=lambda index: (min(index, count - index - 1), index))


def random_flatten(rng):
    return [random_tree(rng)]


def random_reorder(rng):
    return [[rng.randint(1, 12) for _ in range(rng.randint(1, 60))]]


FLATTEN = '''\
def flatten_tree(root):
    current = root
    while current:
        if current.left:
            predecessor = current.left
            while predecessor.right:
                predecessor = predecessor.right
            predecessor.right = current.right
            current.right = current.left
            current.left = None
        current = current.right
'''
RIGHT_FIRST_WRONG = '''\
def flatten_tree(root):
    if root is None:
        return
    nodes, stack = [], [root]
    while stack:
        node = stack.pop()
        nodes.append(node)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    for index, node in enumerate(nodes):
        node.left = None
        node.right = nodes[index + 1] if index + 1 < len(nodes) else None
'''
REORDER = '''\
def reorder_list(head):
    slow = fast = head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    second = slow.next
    slow.next = None
    previous = None
    while second:
        following = second.next
        second.next = previous
        previous = second
        second = following
    first, second = head, previous
    while second:
        following_first, following_second = first.next, second.next
        first.next = second
        second.next = following_first
        first, second = following_first, following_second
'''
REVERSE_TAIL_WRONG = '''\
def reorder_list(head):
    previous, current = None, head.next
    while current:
        following = current.next
        current.next = previous
        previous, current = current, following
    head.next = previous
'''
HALVES_WRONG = '''\
def reorder_list(head):
    nodes, current = [], head
    while current:
        nodes.append(current)
        current = current.next
    middle = (len(nodes) + 1) // 2
    ordered = nodes[:middle] + nodes[middle:][::-1]
    for index, node in enumerate(ordered):
        node.next = ordered[index + 1] if index + 1 < len(ordered) else None
'''

CHAIN_VALUES = [index % 101 - 50 for index in range(2000)]
LEFT_CHAIN = [CHAIN_VALUES[0]] + [item for value in CHAIN_VALUES[1:] for item in (value, None)]
LEFT_CHAIN.pop()
LONG_LIST = [index % 1000 + 1 for index in range(50000)]

BATCH = {
    114: entry("flatten_tree", [("root", "TreeNode | None")], "None", ["trees", "linked-lists", "recursion"],
        ["The binary tree has 0–2000 nodes, each with a value between -100 and 100. Repeated values are allowed.",
         "Modify the original TreeNode objects in place: every left pointer must become None, and right pointers must follow the original preorder (root, left, right). Do not return a ListNode chain, create replacement tree nodes, or rewrite values.",
         "Return nothing. The judge checks the original root's level-order representation and original node order, even when values are equal. The empty tree is represented by []."],
        [([[1, 2, 5, 3, 4, None, 6]], "Original preorder is 1,2,3,4,5,6. Reconnect those same TreeNodes through right pointers; null entries in [1,null,2,null,3,null,4,null,5,null,6] are their empty left children."),
         ([[1, None, 2, 3]], "Although 3 starts as the left child of 2, the final right-only chain is 1→2→3. All left pointers become None.")],
        [[tree] for tree in ([], [0], [-100], [100], [1, 2], [1, None, 2], [1, 2, 3], [1, 2, 3, 4],
                             [1, 2, 3, None, 4], [1, 2, 3, None, None, 4, 5], [1, 1, 1], [2, 1, 2, 1, None, None, 1])],
        FLATTEN, [FLATTEN.replace("predecessor.right = current.right", "predecessor.right = None"), RIGHT_FIRST_WRONG],
        ["Moves the left subtree but drops the original right subtree instead of preserving its continuation.",
         "Visits the right subtree before the left subtree, producing root-right-left rather than preorder."],
        flatten_oracle, random_flatten,
        ["The required order is the original preorder, not the tree's level-order display.",
         "The left subtree must be inserted before the current right subtree; preserve the right subtree before replacing that pointer.",
         "For each current node with a left child, find the rightmost node in the left subtree. Attach the old right subtree there, move left to right, clear left, and advance right.",
         "A recursive or explicit-stack preorder solution can also rewire nodes. The predecessor-splicing reference achieves the O(1)-extra-space follow-up without recursion depth limits."],
        "Preorder visits the current node, then every node in its left subtree, then its right subtree. Splice the left subtree in front of the right by attaching the old right subtree after the left subtree's rightmost continuation. Clear the left link, then continue along the new right link. This preserves the original nodes and their values; the repeated predecessor walks have linear total cost because original right-edge runs are scanned only a bounded number of times. The reference uses constant auxiliary storage. The independent oracle maps the input tree to binary path keys, sorts those keys into preorder, and serializes a right-only chain. Tests additionally compare original object order, not just matching values.",
        "O(n)", "O(1) auxiliary", difficulty=5,
        stress=[([LEFT_CHAIN], right_chain(CHAIN_VALUES)), ([right_chain(CHAIN_VALUES)], right_chain(CHAIN_VALUES))]),
    143: entry("reorder_list", [("head", "ListNode | None")], "None", ["linked-lists", "two-pointers"],
        ["The linked list has 1–50000 nodes, each with a value between 1 and 1000. Values may repeat.",
         "Reconnect original nodes in the order first, last, second, second-last, and so on. Do not modify node values or substitute newly allocated nodes.",
         "Modify the list reachable from the original head and return nothing. Node identity order is checked in addition to displayed values, so equal values do not make different node positions interchangeable."],
        [([[1, 2, 3, 4]], "Alternate from the front and back: the original nodes at positions 0,3,1,2 become 1→4→2→3."),
         ([[1, 2, 3, 4, 5]], "For an odd length, alternate 1,5,2,4 and leave the original middle node 3 last.")],
        [[values] for values in ([1], [1000], [1, 2], [2, 1], [1, 2, 3], [3, 2, 1],
                                 [1, 1, 1, 1], [1, 2, 1, 2, 1], [5, 4, 3, 2],
                                 [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6, 7], [1000, 1, 1000, 1, 1000, 1])],
        REORDER, [REVERSE_TAIL_WRONG, HALVES_WRONG],
        ["Reverses the entire tail without alternating nodes from the front half.",
         "Reverses the second half but appends it instead of weaving the two halves."],
        reorder_oracle, random_reorder,
        ["The final pattern alternates nodes from opposite ends, but a singly linked list cannot walk backward directly.",
         "Find the middle, split the list, reverse the second half, then weave the halves together.",
         "Use slow/fast pointers to split. Reverse the detached second chain. Repeatedly save both next pointers, link first→second→next_first, and advance both halves.",
         "Detach the halves before weaving to avoid cycles. For odd lengths, the first half owns the middle node and is one node longer."],
        "Slow and fast pointers find the first half's tail. Detach the second half before reversing its links. Its traversal order now matches the required last, second-last, and so on. Weave nodes alternately from the original first half and reversed second half, saving next pointers before rewiring. The head remains the same object; each original value remains attached to its original node. This takes three linear passes and constant pointer storage. The independent value oracle alternates deque removals from opposite ends, while a separate index-order oracle ranks positions by distance from an end. Tests include 50,000 nodes and repeated values to verify identity-sensitive order.",
        "O(n)", "O(1) auxiliary", difficulty=5,
        stress=[([LONG_LIST], reorder_oracle([LONG_LIST]))]),
}
for pid, adapter, node_order in ((114, "treenode", flatten_node_order), (143, "listnode", reorder_node_order)):
    spec = BATCH[pid]
    spec["params"] = [(name, annotation, adapter) for name, annotation, _ in spec["params"]]
    spec["result_mode"] = "mutated_argument"
    spec["mutated_parameter"] = 0
    spec["node_policy"] = "reuse_input_nodes"
    spec["node_order"] = node_order
