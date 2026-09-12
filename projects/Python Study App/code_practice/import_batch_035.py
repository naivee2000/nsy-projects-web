"""Recover a swapped BST without changing any original child links."""
from .import_batch_002 import positions, flatten, random_tree
from .import_batch_003 import entry


def inorder_paths(nodes):
    # Path digit 0 precedes the current node (1), which precedes digit 2.
    # This orders paths independently of pointer traversal or Morris threading.
    return sorted(nodes,key=lambda path:tuple(2*side for side in path)+(1,))


def recover_oracle(args):
    nodes = positions(args[0])
    return flatten(dict(zip(inorder_paths(nodes),sorted(nodes.values()))))


def swap_inorder(values, first, second):
    nodes = positions(values)
    paths = inorder_paths(nodes)
    a,b = paths[first],paths[second]
    nodes[a],nodes[b] = nodes[b],nodes[a]
    return flatten(nodes)


def random_recover(rng):
    nodes = positions(random_tree(rng,nonempty=True))
    while len(nodes)<2:
        nodes = positions(random_tree(rng,nonempty=True))
    valid = flatten(dict(zip(inorder_paths(nodes),sorted(rng.sample(range(-100000,100001),len(nodes))))))
    return [swap_inorder(valid,*rng.sample(range(len(nodes)),2))]


RECOVER = '''\
def recover_bst(root):
    previous = first = second = None
    def visit(node):
        nonlocal previous, first, second
        if previous is not None and previous.val > node.val:
            if first is None:
                first = previous
            second = node
        previous = node

    current = root
    while current:
        if current.left is None:
            visit(current)
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right
            if predecessor.right is None:
                predecessor.right = current
                current = current.left
            else:
                predecessor.right = None
                visit(current)
                current = current.right
    first.val, second.val = second.val, first.val
'''
LOCAL_WRONG = '''\
def recover_bst(root):
    stack = [root]
    while stack:
        node = stack.pop()
        if node.left:
            if node.left.val > node.val:
                node.left.val,node.val = node.val,node.left.val
            stack.append(node.left)
        if node.right:
            if node.right.val < node.val:
                node.right.val,node.val = node.val,node.right.val
            stack.append(node.right)
'''

BALANCED = [4,2,6,1,3,5,7]
LEFT_CHAIN = flatten({(0,)*i:1000-i for i in range(1000)})
RIGHT_CHAIN = flatten({(1,)*i:i-500 for i in range(1000)})
BATCH = {
99: entry('recover_bst',[('root','TreeNode | None')],'None',
    ['trees','binary-search-trees','inorder-traversal'],
    ['2 <= node count <= 1000; -2^31 <= Node.val <= 2^31−1.',
     'All node values are distinct. Exactly two values were swapped in an otherwise valid BST.',
     'Modify the original values without changing the final left/right links or replacing nodes; return None.',
     'An O(n)-space solution is allowed. Follow-up: O(1) auxiliary space; temporary traversal links must be restored.'],
    [([[1,3,None,None,2]],
      'Inorder values are [3,2,1], but must be [1,2,3]. Swap the values at the root and its left child; the node holding 2 stays in place.'),
     ([[3,1,4,None,None,2]],
      'Inorder is [1,3,2,4]. Swap 3 with the deeper 2 in its right subtree. The shape stays [root, left, right, null, null, right.left].')],
    [[[1,2]],[[2,None,1]],
     *[[swap_inorder(BALANCED,a,b)] for a,b in ((0,6),(1,5),(2,3),(3,4),(0,3),(3,6))],
     [swap_inorder([4,3,None,2,None,1],0,2)],
     [swap_inorder([1,None,2,None,3,None,4],1,3)],
     [[-2147483648,2147483647]],
     [[-1,2147483647,-2147483648]]],
    RECOVER,[RECOVER.replace('            second = node','            if second is None:\n                second = node'),LOCAL_WRONG],
    ['Fixes only the first inorder inversion, missing the second endpoint when the swapped positions are not adjacent.',
     'Repairs direct parent-child comparisons only; a node may violate an ancestor bound despite fitting its immediate parent.'],
    recover_oracle,random_recover,
    ['An inorder traversal of a valid BST yields strictly increasing values.',
     'Two swapped positions create one inversion if adjacent, or two inversions otherwise. Keep the earlier node of the first inversion and the later node of the last.',
     'Traverse inorder, retaining previous. On previous.val > current.val: set first to previous if unset, and always set second to current. Swap first.val and second.val after traversal.',
     'A stack gives a straightforward O(h)-space traversal. Morris traversal temporarily threads each left-subtree predecessor back to its parent, removes each thread on the second encounter, and uses O(1) extra space.'],
    'In sorted inorder order, swapping positions i < j makes the larger misplaced value the '
    'earlier endpoint of the first descending pair and the smaller misplaced value the later '
    'endpoint of the last descending pair. These may be the same pair when j = i+1. '
    'Track both endpoints while traversing the entire tree; do not repair values early. '
    'The reference uses Morris traversal: find the rightmost node of a left subtree, add a '
    'temporary link back to its parent on first encounter, and remove it before visiting that '
    'parent on the second encounter. Every temporary link is restored, then the two values '
    'are swapped. Each edge is examined a constant number of times. A conventional stack '
    'is also correct, with O(h) extra memory; recursive traversals may overflow on a deep chain.',
    'O(n)','O(1) auxiliary (Morris traversal)',difficulty=6,
    stress=[([swap_inorder(LEFT_CHAIN,0,999)],LEFT_CHAIN),
            ([swap_inorder(RIGHT_CHAIN,123,876)],RIGHT_CHAIN)])
}
BATCH[99].update(params=[('root','TreeNode | None','treenode')],
                 result_mode='mutated_argument',mutated_parameter=0,
                 node_policy='preserve_tree_structure')
