"""Node rearrangement, exact line geometry, buckets, and original-array mutation."""
from .import_batch_002 import positions, flatten
from .import_batch_003 import entry


def sort_oracle(args):
    return sorted(args[0])


def points_oracle(args):
    # Enumerate geometric lines using cross products, not normalized slopes.
    points = args[0]
    best = 1
    for i, (x, y) in enumerate(points):
        for u, v in points[i+1:]:
            best = max(best, sum((a-x)*(v-y) == (b-y)*(u-x) for a,b in points))
    return best


def flipped_paths(values):
    source = positions(values)
    depth = max((len(p) for p in source if 1 not in p), default=0)
    mapping = {}
    for path in source:
        if 1 not in path:
            mapping[path] = (1,)*(depth-len(path))
        else:
            mapping[path] = (1,)*(depth-len(path))+(0,)
    return mapping


def upside_oracle(args):
    source = positions(args[0])
    return flatten({new:source[old] for old,new in flipped_paths(args[0]).items()})


def upside_node_order(args):
    mapping = flipped_paths(args[0])
    original = {path:index for index,path in enumerate(sorted(mapping))}
    return [original[old] for old in sorted(mapping,key=mapping.get)]


def gap_oracle(args):
    ordered = sorted(args[0])
    return max((b-a for a,b in zip(ordered,ordered[1:])),default=0)


def words_oracle(args):
    return list(' '.join(''.join(args[0]).split(' ')[::-1]))


def rotate_oracle(args):
    nums,k = args
    return [nums[(index-k)%len(nums)] for index in range(len(nums))]


def remove_oracle(args):
    return [value for value in args[0] if value != args[1]]


def random_sort(rng):
    return [[rng.randint(-20,20) for _ in range(rng.randint(0,70))]]


def random_points(rng):
    return [rng.sample([[x,y] for x in range(-5,6) for y in range(-5,6)],rng.randint(1,15))]


def random_upside(rng):
    depth = rng.randrange(10)
    nodes = {(0,)*i:rng.randint(1,10) for i in range(depth+1)}
    for i in rng.sample(range(depth),rng.randint(0,min(depth,9-depth))):
        nodes[(0,)*i+(1,)] = rng.randint(1,10)
    return [flatten(nodes)]


def random_gap(rng):
    return [[rng.randint(0,10**9) if rng.random()<.3 else rng.randint(0,30)
             for _ in range(rng.randint(1,70))]]


def random_words(rng):
    return [list(' '.join(''.join(rng.choice('abXYZ019') for _ in range(rng.randint(1,10)))
                         for _ in range(rng.randint(1,10))))]


def random_rotate(rng):
    return [[rng.randint(-20,20) for _ in range(rng.randint(1,70))],rng.randint(0,100000)]


def random_remove(rng):
    return [[rng.randint(1,8) for _ in range(rng.randint(0,70))],rng.randint(0,9)]


SORT = '''\
def sort_linked_list(head):
    def cut(node, width):
        if node is None:
            return None
        for _ in range(width-1):
            if node.next is None:
                break
            node = node.next
        following = node.next
        node.next = None
        return following

    count, node = 0, head
    while node:
        count += 1
        node = node.next
    dummy = ListNode(0, head)
    width = 1
    while width < count:
        current, tail = dummy.next, dummy
        while current:
            left = current
            right = cut(left, width)
            current = cut(right, width)
            while left and right:
                if left.val <= right.val:
                    tail.next, left = left, left.next
                else:
                    tail.next, right = right, right.next
                tail = tail.next
            tail.next = left if left else right
            while tail.next:
                tail = tail.next
        width *= 2
    return dummy.next
'''
POINTS = '''\
def max_points_on_line(points):
    from math import gcd
    best = 1
    for i, (x, y) in enumerate(points):
        counts = {}
        for u, v in points[i+1:]:
            dx, dy = u-x, v-y
            divisor = gcd(abs(dx), abs(dy))
            dx, dy = dx//divisor, dy//divisor
            if dx < 0 or (dx == 0 and dy < 0):
                dx, dy = -dx, -dy
            key = (dx,dy)
            counts[key] = counts.get(key,0)+1
            best = max(best,counts[key]+1)
    return best
'''
UPSIDE = '''\
def upside_down_tree(root):
    if root is None or root.left is None:
        return root
    new_root = upside_down_tree(root.left)
    root.left.left = root.right
    root.left.right = root
    root.left = None
    root.right = None
    return new_root
'''
GAP = '''\
def maximum_gap(nums):
    if len(nums) < 2:
        return 0
    low, high = min(nums), max(nums)
    if low == high:
        return 0
    width = (high-low+len(nums)-2)//(len(nums)-1)
    count = (high-low)//width+1
    minima, maxima = [None]*count, [None]*count
    for value in nums:
        index = (value-low)//width
        if minima[index] is None or value < minima[index]:
            minima[index] = value
        if maxima[index] is None or value > maxima[index]:
            maxima[index] = value
    best, previous = 0, low
    for index in range(count):
        if minima[index] is not None:
            best = max(best,minima[index]-previous)
            previous = maxima[index]
    return best
'''
WORDS = '''\
def reverse_words_in_place(s):
    def reverse(left, right):
        while left < right:
            s[left],s[right] = s[right],s[left]
            left += 1
            right -= 1
    reverse(0,len(s)-1)
    start = 0
    for end in range(len(s)+1):
        if end == len(s) or s[end] == ' ':
            reverse(start,end-1)
            start = end+1
'''
ROTATE = '''\
def rotate_array(nums, k):
    def reverse(left, right):
        while left < right:
            nums[left],nums[right] = nums[right],nums[left]
            left += 1
            right -= 1
    k %= len(nums)
    reverse(0,len(nums)-1)
    reverse(0,k-1)
    reverse(k,len(nums)-1)
'''
REMOVE = '''\
def remove_list_elements(head, val):
    dummy = ListNode(0, head)
    previous = dummy
    while previous.next:
        if previous.next.val == val:
            previous.next = previous.next.next
        else:
            previous = previous.next
    return dummy.next
'''


BATCH = {
148: entry('sort_linked_list',[('head','ListNode | None')],'ListNode | None',
    ['linked-lists','merge-sort','divide-and-conquer'],
    ['0 <= node count <= 50,000; -100,000 <= Node.val <= 100,000.',
     'The function receives ListNode objects, not a Python list. Return the sorted head or None.',
     'Follow-up target: O(n log n) time and O(1) auxiliary memory.'],
    [([[4,2,1,3]],'The returned chain is 1 → 2 → 3 → 4. Values, not original positions, determine order.'),
     ([[-1,5,3,4,0]],'The negative value stays first; 0 moves before 3, producing -1 → 0 → 3 → 4 → 5.')],
    [[v] for v in ([],[1],[2,1],[1,2],[2,2],[3,1,2],[1,3,2,4],[4,3,2,1],
                   [0,-1,0,-1],[5]*7,[-100000,100000,0],[9,8,7,6,5,4,3,2,1])],
    SORT,[SORT.replace('left.val <= right.val','left.val >= right.val'),
          SORT.replace('while width < count:','if width < count:')],
    ['Merges in descending rather than ascending order.',
     'Performs only the width-one pass; sorted pairs do not imply a sorted whole chain.'],
    sort_oracle,random_sort,
    ['Linked lists support merging sorted chains without random indexing.',
     'Start with one-node runs, merge neighbors, then double the run width.',
     'For widths 1, 2, 4, …: cut two runs, merge into the output tail, and continue with the saved remainder.',
     'Bottom-up merge sort scans O(n) nodes per pass for O(log n) passes. Rewire links with a constant number of pointers.'],
    'Count the nodes. On each pass, cut adjacent runs of the current width so their tails terminate. '
    'Save the unprocessed remainder before merging. Append the smaller head repeatedly, then the remaining run. '
    'A final short run is valid. Doubling the width eventually produces a single ascending chain. '
    'The iterative implementation avoids both an auxiliary array and recursion-stack space.',
    'O(n log n)','O(1)',difficulty=6,
    stress=[([list(range(50000,0,-1))],list(range(1,50001))),
            ([[100000,-100000]*25000],[-100000]*25000+[100000]*25000)]),
149: entry('max_points_on_line',[('points','list[list[int]]')],'int',
    ['geometry','hash-maps','arrays'],
    ['1 <= points.length <= 300; every point has exactly two integer coordinates.',
     '-10,000 <= x, y <= 10,000; all points are distinct.',
     'Vertical, horizontal, and negatively sloped lines all count. Return a count, not a line.'],
    [([[[1,1],[2,2],[3,3]]],'All three points lie on y = x, so the maximum count is 3.'),
     ([[[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]]],
      'The four points (4,1), (3,2), (2,3), and (1,4) share x + y = 5. No line contains more.')],
    [[v] for v in ([[0,0]],[[0,0],[1,2]],[[0,0],[0,1],[0,-1],[0,3]],
                   [[-1,2],[0,2],[4,2]],[[0,0],[1,1],[2,3]],
                   [[0,0],[1,2],[2,4],[3,6]],[[0,0],[-1,-2],[1,2],[2,4]],
                   [[0,0],[1,-1],[2,-2],[4,0]],[[0,0],[1,0],[0,1],[1,1]],
                   [[-10000,-10000],[0,0],[10000,10000],[1,0]],
                   [[10000,9999],[9999,9998],[0,0]],
                   [[2,3],[2,7],[2,-1],[0,3],[1,3]])],
    POINTS,[POINTS.replace('divisor = gcd(abs(dx), abs(dy))','divisor = 1'),
            POINTS.replace('divisor = gcd(abs(dx), abs(dy))','if dx == 0:\n                continue\n            divisor = gcd(abs(dx), abs(dy))')],
    ['Counts equal displacement vectors instead of equal directions, missing unequal point spacing.',
     'Skips vertical lines to avoid a zero denominator, although vertical lines are valid.'],
    points_oracle,random_points,
    ['Fix one point as an anchor and ask which other points share a line through it.',
     'Use an exact direction pair; reduce by the greatest common divisor and normalize its sign.',
     'For each anchor, count normalized (dx, dy) pairs to later points; the largest bucket plus one includes the anchor.',
     'The first input point on an optimal line sees all remaining points on that line. Integer direction keys avoid floating-point slope errors.'],
    'For each anchor, reduce every displacement by gcd(|dx|, |dy|). Choose a consistent sign: '
    'dx positive, or dy positive when dx is zero. Opposite directions then share one key, and vertical '
    'lines need no division by zero. Add the anchor to the most frequent key. The earliest point on '
    'any optimal line sees every later point on that line. There are O(n²) pairs; gcd adds a logarithmic '
    'coordinate factor (bounded here), and the per-anchor map stores O(n) directions.',
    'O(n² log C), C = coordinate span','O(n)',difficulty=8,
    stress=[([[[x,2*x+1] for x in range(-150,150)]],300),
            ([[[x,y] for x in range(30) for y in range(10)]],30)]),
156: entry('upside_down_tree',[('root','TreeNode | None')],'TreeNode | None',
    ['trees','recursion','pointer-manipulation'],
    ['0 <= node count <= 10; 1 <= Node.val <= 10.',
     'Every right child is a leaf and has a left sibling.',
     'Rewire the original nodes level by level; return the original leftmost node as the new root. Empty input returns None.'],
    [([[1,2,3,4,5]],'Node 4 becomes the root with children 5 and 2. Node 2 has children 3 and 1; old child links are removed.'),
     ([[1,2]],'The old left child 2 becomes the root, with no left child and old root 1 as its right child: [2, null, 1].')],
    [[v] for v in ([],[1],[2],[1,2,3],[1,2,None,3],[1,2,3,4],
                   [1,2,None,3,4],[1,2,3,4,5,None,None,6,7],[1,1,1],
                   [2,2,2,2,2],[10,1,10,2,3],[3,2,None,1,None,4])],
    UPSIDE,[UPSIDE.replace('root.left.left = root.right','root.left.left = None'),
            '''
def upside_down_tree(root):
    if root is None:
        return None
    root.left, root.right = root.right, root.left
    return root
'''],
    ['Drops each old right leaf instead of attaching it as the new left child.',
     'Confuses turning the tree upside down with a left/right mirror at the root.'],
    upside_oracle,random_upside,
    ['Follow the left-child chain: its last node becomes the new root.',
     'Recursively transform the left subtree, then attach the old parent and its right leaf beneath the old left child.',
     'new = solve(root.left); root.left.left = root.right; root.left.right = root; clear root.left and root.right; return new.',
     'The recursion returns one fixed new root while each unwinding frame reconnects three original nodes. Clearing old links prevents cycles.'],
    'An empty tree or a node without a left child is already transformed. Otherwise first transform '
    'the left subtree. The old left child is now the place to attach the old right leaf on the left '
    'and the old parent on the right. Clear both old parent links before returning the new root. '
    'The right-leaf guarantee ensures these local operations lose no descendants. The call stack '
    'uses O(h) space; at most ten nodes are present. Equal values do not make nodes interchangeable.',
    'O(n)','O(h)',difficulty=5,
    stress=[([flatten({(0,)*i:i+1 for i in range(10)})],
             flatten({(1,)*i:10-i for i in range(10)}))]),
164: entry('maximum_gap',[('nums','list[int]')],'int',
    ['arrays','bucket-sort','pigeonhole-principle'],
    ['1 <= nums.length <= 100,000; 0 <= nums[i] <= 1,000,000,000.',
     'Measure adjacent differences in sorted order, not the full range or adjacent input positions.',
     'Required algorithm target: linear time and linear extra space. A singleton or all-equal array has gap 0.'],
    [([[3,6,9,1]],'Sorted order is [1,3,6,9]. Its neighboring gaps are 2, 3, and 3, so return 3 rather than the full span 8.'),
     ([[10]],'A single value has no neighboring pair; return 0.')],
    [[v] for v in ([0],[0,0],[0,1],[1,1,1],[1,100],[9,1,5],
                   [1,2,3,4],[4,3,2,1],[0,0,100,100],[0,1000000000],
                   [1,1,2,2,3,50],[0,3,4,7,10])],
    GAP,['''
def maximum_gap(nums):
    return max(nums)-min(nums)
''','''
def maximum_gap(nums):
    return max((abs(b-a) for a,b in zip(nums,nums[1:])),default=0)
'''],
    ['Returns the whole range, ignoring the values that divide it into adjacent gaps.',
     'Measures consecutive input positions instead of sorted neighbors.'],
    gap_oracle,random_gap,
    ['The n−1 sorted gaps must cover max(nums)−min(nums). At least one gap is as large as their average.',
     'Use buckets of width ceil(range/(n−1)); retain only each nonempty bucket’s minimum and maximum.',
     'Assign each value to (value−minimum)//width. Scan nonempty buckets, comparing the next minimum with the previous maximum.',
     'The maximum gap is at least the bucket width; two integers inside one bucket differ by less than that width. Therefore only inter-bucket gaps matter.'],
    'Handle n < 2 and a zero range before dividing. Set bucket width to ceil((high−low)/(n−1)); '
    'this creates at most n buckets. Values within a bucket cannot contain the maximum gap, '
    'so only its extremes matter. Scan populated buckets in order, skipping empty buckets and '
    'measuring the distance from the preceding maximum. Each value and bucket is visited a '
    'constant number of times. Sorting is a useful correctness oracle, but misses the linear-time target.',
    'O(n)','O(n)',difficulty=6,
    stress=[([list(range(0,10**9,10000))],10000),
            ([[7]*100000],0),([[0]*99999+[10**9]],10**9)]),
186: entry('reverse_words_in_place',[('s','list[str]')],'None',
    ['strings','two-pointers','in-place'],
    ['1 <= s.length <= 100,000; each element is one English letter, digit, or ASCII space.',
     'At least one word; no leading/trailing spaces; exactly one space between words.',
     'Modify the original character array without extra array storage. The judge checks s after the call; a returned copy does not count.'],
    [([list('the sky is blue')],'The words become “blue is sky the”; letters within each word remain in their original order.'),
     ([list('Hi 2 cats')],'The same character array must become “cats 2 Hi”; uppercase H and the digit 2 are preserved.')],
    [[list(s)] for s in ('a','ab','ABC','a b','ab cd','a bc d','0 1 2','one two',
                        'a a a','a B9 c','abcd e','x yz ABC')],
    WORDS,['''
def reverse_words_in_place(s):
    s.reverse()
''','''
def reverse_words_in_place(s):
    return list(' '.join(''.join(s).split(' ')[::-1]))
'''],
    ['Reverses the letters inside every word as well as the word order.',
     'Computes the right characters but returns a copy without modifying the input.'],
    words_oracle,random_words,
    ['Reversing the entire character array also reverses each word’s letters.',
     'After one full reversal, reverse each individual word to restore its spelling.',
     'Swap s[l] with s[r] while l < r. Apply to the whole array, then to each range between spaces, including the final word.',
     'Each character participates in at most two reversals. Index swaps use O(1) auxiliary space and preserve the original array.'],
    'Reverse the whole array using two pointers. Scan for spaces and reverse every word-sized '
    'range; treat the end of the array as a final boundary. The first reversal changes word '
    'order, and the second restores letters within words. Exactly one space separates words, '
    'so no whitespace normalization is needed. Unlike the string-returning Reverse Words '
    'exercise, this callable mutates the original character array and returns None.',
    'O(n)','O(1)',difficulty=5,
    stress=[([list('a '*49999+'ab')],list('ab '+'a '*49998+'a'))]),
189: entry('rotate_array',[('nums','list[int]'),('k','int')],'None',
    ['arrays','two-pointers','in-place'],
    ['1 <= nums.length <= 100,000; -2^31 <= nums[i] <= 2^31−1; 0 <= k <= 100,000.',
     'Move every value k positions to the right with wraparound, modifying the original nums array.',
     'Return None; the judge observes nums after the call. Follow-up: achieve O(1) extra space.'],
    [([[1,2,3,4,5,6,7],3],'The last three values wrap to the front, making the original array [5,6,7,1,2,3,4].'),
     ([[-1,-100,3,99],2],'Two rightward steps produce [3,99,-1,-100]; signs do not affect rotation.')],
    [[[1],0],[[1],100000],[[1,2],1],[[1,2],2],[[1,2],3],[[1,2,3],0],
     [[1,2,3],1],[[1,2,3],2],[[1,2,3],4],[[2,2,1,2],3],
     [[-2147483648,0,2147483647],100000],[[9,8,7,6,5],5]],
    ROTATE,[ROTATE.replace('k %= len(nums)','k = (-k)%len(nums)'),
            '''
def rotate_array(nums, k):
    k %= len(nums)
    return nums[-k:]+nums[:-k]
'''],
    ['Performs a left rotation instead of a right rotation.',
     'Returns a rotated copy but leaves the input array unchanged.'],
    rotate_oracle,random_rotate,
    ['A rotation by the array length does nothing; reduce k modulo n.',
     'Write the array as A+B, where B contains its final k elements. The desired arrangement is B+A.',
     'Reverse all n elements; reverse indices 0 through k−1; reverse indices k through n−1.',
     'Reversing A+B gives reverse(B)+reverse(A); reversing each section restores B+A using only swaps.'],
    'Normalize k modulo the nonzero array length. Reverse the entire array, then its first k '
    'values and the remaining values separately. All three operations act on the original '
    'array, including when k is zero. This meets the O(1)-space follow-up. The original '
    'Rotate Values Right exercise returns a list; this source callable instead modifies nums, '
    'so a returned-copy solution is observably different and is rejected here.',
    'O(n)','O(1)',difficulty=5,
    stress=[([list(range(100000)),99999],list(range(1,100000))+[0]),
            ([list(range(100000)),100000],list(range(100000)))]),
203: entry('remove_list_elements',[('head','ListNode | None'),('val','int')],'ListNode | None',
    ['linked-lists','pointer-manipulation','recursion'],
    ['0 <= node count <= 10,000; 1 <= Node.val <= 50; 0 <= val <= 50.',
     'Remove every matching value while preserving the relative order of all survivors.',
     'Return the new ListNode head, or None if no nodes remain. The head itself may need removal.'],
    [([[1,2,6,3,4,5,6],6],'Remove both nodes holding 6, including the tail. The surviving chain is 1 → 2 → 3 → 4 → 5.'),
     ([[7,7,7,7],7],'Every node matches, including consecutive matches at the head. Return None, displayed as [].')],
    [[[],1],[[1],1],[[1],0],[[1],2],[[1,2],1],[[1,2],2],[[2,2,1],2],
     [[1,2,2],2],[[2,1,2,1,2],2],[[1,2,3],0],[[50,1,50],50],[[1,1,2,1,1],1]],
    REMOVE,['''
def remove_list_elements(head, val):
    previous = head
    while previous and previous.next:
        if previous.next.val == val:
            previous.next = previous.next.next
        else:
            previous = previous.next
    return head
''',REMOVE.replace('        else:\n            previous = previous.next',
                   '        previous = previous.next').replace('while previous.next:', 'while previous and previous.next:')],
    ['Checks only successors and never removes a matching head.',
     'Always advances after deleting, skipping adjacent matching nodes.'],
    remove_oracle,random_remove,
    ['Deleting a node is easier when you hold a pointer to its predecessor.',
     'A dummy node before the head makes deleting the first node an ordinary case.',
     'While previous.next exists: bypass it if its value matches; otherwise advance previous. Return dummy.next.',
     'After a deletion, stay at the same predecessor so consecutive matches are checked. A recursive alternative cleans the suffix then keeps or drops the current head.'],
    'Put a dummy node before the input head. Maintain the invariant that previous is the last '
    'retained node before the unprocessed suffix. Bypass a matching successor without advancing; '
    'advance only when keeping that successor. Returning dummy.next handles empty and all-deleted '
    'lists. The recursive recurrence cleans head.next, then returns that cleaned suffix when '
    'head.val matches, or head otherwise. It needs O(n) stack space; the iterative reference '
    'supports the 10,000-node boundary without changing Python’s recursion limit.',
    'O(n)','O(1)',difficulty=3,
    stress=[([[50]*10000,50],[]),([[1,2]*5000,1],[2]*5000)]),
}

for pid in (148,203):
    BATCH[pid]['params'][0] = ('head','ListNode | None','listnode')
    BATCH[pid]['adapter'] = 'listnode'
BATCH[156].update(params=[('root','TreeNode | None','treenode')],adapter='treenode',
                  node_policy='reuse_input_nodes',node_order=upside_node_order)
BATCH[149]['prerequisites'] = ['arrays','hash-maps']
for pid in (186,189):
    BATCH[pid].update(result_mode='mutated_argument',mutated_parameter=0)
BATCH[189]['statement'] = (
    'Given an integer array nums, rotate it to the right by k non-negative steps. '
    'Modify the original nums array and return None. Each value wraps from the end '
    'back to the beginning. The examples show the input array after the call, not a '
    'returned copy. Follow-up: use O(1) extra space.')
