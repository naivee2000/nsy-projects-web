"""BST frequency runs, subtree sums, and level-position/value contracts."""
from collections import Counter, deque

from .import_batch_002 import positions, flatten
from .import_batch_003 import entry


def mode_oracle(args):
    counts=Counter(v for v in args[0] if v is not None)
    highest=max(counts.values())
    return sorted(v for v,count in counts.items() if count==highest)


def sums_oracle(args):
    nodes=positions(args[0])
    # Independently enumerate every subtree's descendants; no shared partial sums.
    counts=Counter(sum(v for p,v in nodes.items() if p[:len(root)]==root) for root in nodes)
    highest=max(counts.values())
    return sorted(v for v,count in counts.items() if count==highest)


def bottom_oracle(args):
    nodes=positions(args[0])
    deepest=max(map(len,nodes))
    return nodes[min(p for p in nodes if len(p)==deepest)]


def rows_oracle(args):
    nodes=positions(args[0])
    return [max(v for p,v in nodes.items() if len(p)==level)
            for level in range(1+max(map(len,nodes),default=-1))]


def chain(values,left=False):
    result=[values[0]]
    for value in values[1:]:result.extend([value,None] if left else [None,value])
    if result[-1] is None:result.pop()
    return result


def balanced(values):
    out=[];queue=deque([(0,len(values))])
    while queue:
        lo,hi=queue.popleft()
        if lo==hi:out.append(None);continue
        mid=(lo+hi)//2;out.append(values[mid])
        queue.extend(((lo,mid),(mid+1,hi)))
    while out and out[-1] is None:out.pop()
    return out


def random_bst(rng):
    values=sorted(rng.randint(-5,5) for _ in range(rng.randint(1,30)))
    if rng.random()<.3:return [chain(values)]
    if rng.random()<.3:return [chain(values[::-1],True)]
    return [balanced(values)]


def random_tree(rng,empty=False):
    n=rng.randint(0 if empty else 1,25)
    if not n:return [[]]
    nodes={():rng.randint(-5,5)};slots=[(0,),(1,)]
    for _ in range(n-1):
        path=slots.pop(rng.randrange(len(slots)))
        nodes[path]=rng.randint(-5,5);slots.extend((path+(0,),path+(1,)))
    return [flatten(nodes)]


def random_rows(rng):return random_tree(rng,True)


MODE='''\
def bst_modes(root):
    stack=[];node=root;previous=None;run=best=0;answer=[]
    while stack or node is not None:
        while node is not None:
            stack.append(node);node=node.left
        node=stack.pop()
        run=run+1 if node.val==previous else 1
        previous=node.val
        if run>best:
            best=run;answer=[node.val]
        elif run==best:answer.append(node.val)
        node=node.right
    return answer
'''
SUMS='''\
def frequent_subtree_sums(root):
    from collections import Counter
    frequencies=Counter();sums={};stack=[(root,False)]
    while stack:
        node,ready=stack.pop()
        if not ready:
            stack.append((node,True))
            if node.right is not None:stack.append((node.right,False))
            if node.left is not None:stack.append((node.left,False))
        else:
            total=node.val+sums.pop(node.left,0)+sums.pop(node.right,0)
            sums[node]=total;frequencies[total]+=1
    highest=max(frequencies.values())
    return [value for value,count in frequencies.items() if count==highest]
'''
BOTTOM='''\
def bottom_left_tree_value(root):
    stack=[(root,0)];deepest=-1;answer=root.val
    while stack:
        node,depth=stack.pop()
        if depth>deepest:
            deepest=depth;answer=node.val
        if node.right is not None:stack.append((node.right,depth+1))
        if node.left is not None:stack.append((node.left,depth+1))
    return answer
'''
ROWS='''\
def largest_tree_row_values(root):
    if root is None:return []
    answer=[];stack=[(root,0)]
    while stack:
        node,depth=stack.pop()
        if depth==len(answer):answer.append(node.val)
        else:answer[depth]=max(answer[depth],node.val)
        if node.right is not None:stack.append((node.right,depth+1))
        if node.left is not None:stack.append((node.left,depth+1))
    return answer
'''
SMALL_TREES=[[0],[-1],[1,2],[1,None,2],[1,2,3],[0,0,0],[1,-2,3],
    [-5,-4,-3],[-1,-1,-1],[1,2,3,4,None,None,5],[1,2,3,None,4,5],
    [1,None,2,3],[1,2,None,None,3],[5,2,-5],[5,2,-3],
    [1,2,3,4,None,5,6,None,None,7]]

BATCH={
501:entry('bst_modes',[('root','TreeNode')],'list[int]',['trees','binary-search-trees','depth-first-search'],
    ['1 <= node count <= 10,000; -100,000 <= node.val <= 100,000.',
     'This BST ALLOWS duplicates: every left-subtree value is <= its root and every right-subtree value is >= it.',
     'Return ALL distinct values tied for highest occurrence count, in any order. Do not return the counts or just one tied value.'],
    [([[1,None,2,2]],'The value 2 occurs twice, while 1 occurs once. Only 2 has the maximum frequency, so return [2].'),
     ([[2,1,3,1,None,None,3]],'Values 1 and 3 each occur twice; 2 occurs once. Return [1,3] in any order, not one tied value and not the frequency list [2,2].')],
    [[a] for a in ([0],[1],[-1],[1,1],[1,None,1],[0,-1,1],[2,1,2],
        [2,2,3],[2,1,3,1,None,3],[0,0,0],[-2,-3,-1],[-1,-1,None],
        [100000,-100000,100000],[2,1,3,None,1,3,3],[2,2,2,2,None,None,2])],
    MODE,[MODE.replace('return answer','return answer[:1]'),
          MODE.replace('run=run+1 if node.val==previous else 1','run=1')],
    ['Keeps only one value when the maximum frequency is tied.', 'Treats every visit as a new run, ignoring repeated-value frequency.'],
    mode_oracle,random_bst,
    ['An inorder traversal of this duplicate-permitting BST is non-decreasing.',
     'Count consecutive equal values; compare each run length with the largest seen.',
     'Traverse left/node/right with an explicit stack. Extend or reset run; replace answers on a new record and append on a tie.',
     'A run that later exceeds the record replaces provisional tied values. Return distinct modes, not every repeated occurrence.'],
    'Sorted inorder values place equal keys consecutively, even when duplicates occur on '
    'both sides of a node. Track the previous value, current run and best run. The explicit '
    'stack supports a 10,000-node chain without a Python recursion-limit increase. Auxiliary '
    'space is O(h), excluding output, for height h. The optional constant-extra-space follow-up '
    'can use Morris traversal with every temporary thread restored; this reference uses a stack. '
    'The independent oracle counts non-null JSON values without traversing inorder.',
    'O(n)','O(h) auxiliary, excluding output',difficulty=3,
    stress=[([chain(list(range(10000)))],list(range(10000))),
            ([chain([7]*10000,True)],[7]),([balanced([-1]*5000+[2]*5000)],[-1,2]),
            ([balanced([-100000]*3333+[0]*3334+[100000]*3333)],[0])]),
508:entry('frequent_subtree_sums',[('root','TreeNode')],'list[int]',['trees','recursion','dynamic-programming','hash-maps'],
    ['1 <= node count <= 10,000; -100,000 <= node.val <= 100,000.',
     'A subtree sum includes its root and ALL descendants, not just one downward path.',
     'Count one sum for every node; return all distinct sums tied for highest frequency in any order. Negative and zero sums are valid.'],
    [([[5,2,-3]],'The three subtree sums are 2, -3 and 5+2-3=4. Each appears once, so all three are returned.'),
     ([[5,2,-5]],'The left leaf sums to 2 and the whole tree also sums to 2. Thus 2 occurs twice, more often than -5; return [2].')],
    [[a] for a in SMALL_TREES if a not in ([5,2,-3],[5,2,-5])],
    SUMS,[SUMS.replace('total=node.val+sums.pop(node.left,0)+sums.pop(node.right,0)','total=node.val'),
          SUMS.replace('return [value for value,count in frequencies.items() if count==highest]',
                       'return [next(value for value,count in frequencies.items() if count==highest)]')],
    ['Counts node values instead of complete subtree sums.', 'Drops other sums tied for the highest frequency.'],
    sums_oracle,random_tree,
    ['A parent sum needs both child sums before it can be counted.',
     'Use postorder evaluation and a frequency map of completed sums.',
     'For each node after its children, compute node.val + left_sum + right_sum and increment that sum frequency.',
     'Use explicit enter/exit frames for deep trees. Return every key whose frequency equals the maximum, without duplicate keys.'],
    'Structural recursion gives sum(node)=node.val+sum(left)+sum(right). An explicit '
    'postorder stack evaluates the recurrence safely at height 10,000, and consumed child '
    'sums can be removed. Frequencies can require O(n) space even when stack height is small. '
    'The independent oracle enumerates each node path and literally sums all descendant '
    'paths separately. Max-size chain and complete-tree expectations are derived analytically.',
    'O(n)','O(n)',difficulty=5,
    stress=[([chain([0]*10000)],[0]),([chain([1]*10000)],list(range(1,10001))),
            ([chain([1,-1]*5000)],[-1,0]),([[1]*10000],[1]),
            ([chain([100000]*10000,True)],[100000*i for i in range(1,10001)])]),
513:entry('bottom_left_tree_value',[('root','TreeNode')],'int',['trees','recursion','depth-first-search'],
    ['1 <= node count <= 10,000; -2^31 <= node.val <= 2^31-1.',
     'Return the LEFTMOST value among nodes at the maximum depth. Leftmost describes position, not numeric size.',
     'A deeper node in the right subtree beats a shallower node on the root\'s left chain.'],
    [([[2,1,3]],'Both 1 and 3 are at the deepest level. The leftmost is 1.'),
     ([[9,8,7,100,None,None,-5]],'At the deepest level, 100 is left of -5. Return 100, even though -5 is numerically smaller.')],
    [[a] for a in SMALL_TREES]+[[[-2**31]],[[2**31-1]]],
    BOTTOM,[BOTTOM.replace('depth>deepest','depth>=deepest'),
            'def bottom_left_tree_value(root):\n    while root.left is not None:root=root.left\n    return root.val\n'],
    ['Overwrites with the rightmost value on an already-seen deepest level.', 'Follows only left children and misses a deeper node elsewhere.'],
    bottom_oracle,random_tree,
    ['Compare depth first, then left-to-right position, never the node value.',
     'Visit left children before right children; the first node at a new maximum depth is the answer.',
     'On a stack, push right first, then left. Update the answer only when depth strictly exceeds the previous maximum.',
     'Do not overwrite at equal depth. An explicit stack implements preorder recursion without failing on a deep chain.'],
    'Left-first preorder encounters each depth from left to right. The first node at '
    'the eventual maximum depth must be the leftmost there. Update only on a strictly '
    'deeper level, not on a smaller value or equal depth. Explicit frames use O(h) '
    'space and support 10,000 nodes. The independent oracle orders binary paths '
    'by greatest length and then lexicographic position.',
    'O(n)','O(h)',difficulty=5,
    stress=[([chain(list(range(10000)))],9999),([chain(list(range(10000)),True)],9999),
            ([list(range(10000))],8191),([[-2**31]*10000],-2**31)]),
515:entry('largest_tree_row_values',[('root','TreeNode | None')],'list[int]',['trees','recursion','depth-first-search'],
    ['0 <= node count <= 10,000; -2^31 <= node.val <= 2^31-1.',
     'Return one maximum value per depth, ordered from root level to deepest. Empty input returns [].',
     'Levels may contain only negative values. The rightmost node is not necessarily the maximum.'],
    [([[1,3,2,5,3,None,9]],'The level maxima are 1, max(3,2)=3, and max(5,3,9)=9. Return [1,3,9].'),
     ([[-1,-5,-3]],'Return [-1,-3]. Zero is not a tree value and must not replace a negative level maximum.')],
    [[[]]]+[[a] for a in SMALL_TREES]+[[[-2**31]],[[2**31-1]]],
    ROWS,[ROWS.replace('answer.append(node.val)','answer.append(max(0,node.val))'),
          ROWS.replace('max(answer[depth],node.val)','node.val')],
    ['Initializes each row maximum with zero, corrupting all-negative rows.', 'Returns the final visited value per row rather than the largest.'],
    rows_oracle,random_rows,
    ['Group by depth, but keep only the largest value for each group.',
     'Visit each node with its depth and update that depth\'s running maximum.',
     'The first node at a new depth initializes its entry to node.val; later nodes take max(existing,node.val).',
     'Handle the empty root before creating a stack. Keep entries in depth order and never initialize maxima to zero.'],
    'Depth-indexed accumulation gives one maximum per row regardless of traversal '
    'order. Initializing from an actual node handles the full signed value range. '
    'An explicit DFS stack replaces recursive calls for chains of height 10,000; '
    'the result and traversal state use O(h) space. The independent oracle groups '
    'binary paths by length and selects each group\'s literal maximum. This is '
    'different from right-side view, which asks about position rather than value.',
    'O(n)','O(h), including result',difficulty=5,
    stress=[([chain(list(range(10000)))],list(range(10000))),
            ([list(range(10000))],[min(2**(d+1)-2,9999) for d in range(14)]),
            ([[-2**31]*10000],[-2**31]*14),
            ([chain([2**31-1]*10000,True)],[2**31-1]*10000)])
}

for pid,spec in BATCH.items():
    name,annotation,_=spec['params'][0]
    spec['params'][0]=(name,annotation,'treenode')
    spec['statement']=' '.join(spec['constraints'][1:])
for pid in (501,508):BATCH[pid]['comparator']='unordered'
