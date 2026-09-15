"""Second-greater stacks, message splitting, tree levels, palindromes, and BST queries."""
from collections import deque

from .import_batch_055 import entry


class Node:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None


def make_tree(values):
    if not values:
        return None
    nodes = [None if value is None else Node(value) for value in values]
    children = iter(nodes[1:])
    for node in nodes:
        if node is not None:
            node.left = next(children, None)
            node.right = next(children, None)
    return nodes[0]


def second_greater_oracle(args):
    nums = args[0]
    answer = []
    for index, value in enumerate(nums):
        greater = [candidate for candidate in nums[index + 1:] if candidate > value]
        answer.append(greater[1] if len(greater) >= 2 else -1)
    return answer


def random_second_greater(rng):
    return [[rng.randint(0, 20) for _ in range(rng.randint(1, 25))]]


def split_message_oracle(args):
    message, limit = args
    for total in range(1, len(message) + 1):
        capacities = [limit - len(f'<{index}/{total}>') for index in range(1, total + 1)]
        if min(capacities) <= 0 or sum(capacities) < len(message):
            continue
        parts = []
        offset = 0
        for index, capacity in enumerate(capacities, 1):
            chunk = message[offset:offset + capacity]
            offset += len(chunk)
            parts.append(chunk + f'<{index}/{total}>')
        if offset == len(message):
            return parts
    return []


def random_split_message(rng):
    message = ''.join(rng.choice('abc ') for _ in range(rng.randint(1, 35)))
    return [message, rng.randint(5, 18)]


def minimum_swaps_bruteforce(values):
    target = tuple(sorted(values))
    start = tuple(values)
    if start == target:
        return 0
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        state, distance = queue.popleft()
        first = next(index for index, value in enumerate(state) if value != target[index])
        for other in range(first + 1, len(state)):
            if state[other] != target[first]:
                continue
            changed = list(state); changed[first], changed[other] = changed[other], changed[first]
            following = tuple(changed)
            if following == target:
                return distance + 1
            if following not in seen:
                seen.add(following); queue.append((following, distance + 1))
    raise AssertionError('unreachable permutation')


def sort_levels_oracle(args):
    root = make_tree(args[0]); queue = deque([root]); answer = 0
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft(); level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        answer += minimum_swaps_bruteforce(level)
    return answer


def random_sort_levels(rng):
    size = rng.randint(1, 7)
    values = rng.sample(range(1, 100), size)
    serialized = [values[0]]; next_value = 1; parents = 1
    while parents and next_value < size:
        parents -= 1
        for _ in range(2):
            if next_value < size and (rng.random() < .8 or not parents):
                serialized.append(values[next_value]); next_value += 1; parents += 1
            else:
                serialized.append(None)
    while serialized and serialized[-1] is None: serialized.pop()
    return [serialized]


def palindromes_oracle(args):
    text, minimum = args
    memo = {}
    def visit(index):
        if index >= len(text): return 0
        if index in memo: return memo[index]
        best = visit(index + 1)
        for end in range(index + minimum, len(text) + 1):
            piece = text[index:end]
            if piece == piece[::-1]: best = max(best, 1 + visit(end))
        memo[index] = best
        return best
    return visit(0)


def random_palindromes(rng):
    text = ''.join(rng.choice('abc') for _ in range(rng.randint(1, 13)))
    return [text, rng.randint(1, len(text))]


def bst_queries_oracle(args):
    values = sorted(value for value in args[0] if value is not None)
    answer = []
    for query in args[1]:
        lower = max((value for value in values if value <= query), default=-1)
        upper = min((value for value in values if value >= query), default=-1)
        answer.append([lower, upper])
    return answer


def random_bst_queries(rng):
    values = rng.sample(range(1, 80), rng.randint(2, 12)); root = Node(values[0])
    for value in values[1:]:
        node = root
        while True:
            side = 'left' if value < node.val else 'right'
            child = getattr(node, side)
            if child is None:
                setattr(node, side, Node(value)); break
            node = child
    serialized = []; queue = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            serialized.append(None); continue
        serialized.append(node.val); queue.extend((node.left, node.right))
    while serialized[-1] is None: serialized.pop()
    return [serialized, [rng.randint(1, 85) for _ in range(rng.randint(1, 10))]]


SECOND_GREATER = '''def second_greater_elements(nums):
    answer=[-1]*len(nums);first=[];second=[]
    for index,value in enumerate(nums):
        while second and nums[second[-1]]<value:answer[second.pop()]=value
        moved=[]
        while first and nums[first[-1]]<value:moved.append(first.pop())
        second.extend(reversed(moved));first.append(index)
    return answer
'''


FIRST_GREATER = '''def second_greater_elements(nums):
    answer=[-1]*len(nums);stack=[]
    for index,value in enumerate(nums):
        while stack and nums[stack[-1]]<value:answer[stack.pop()]=value
        stack.append(index)
    return answer
'''


SPLIT_MESSAGE = '''def split_message(message,limit):
    digit_sum=0
    for total in range(1,len(message)+1):
        digit_sum+=len(str(total));denominator=len(str(total))
        capacity=limit*total-digit_sum-denominator*total-3*total
        if limit<=2*denominator+3 or capacity<len(message):continue
        answer=[];offset=0
        for index in range(1,total+1):
            suffix=f'<{index}/{total}>';take=limit-len(suffix)
            answer.append(message[offset:offset+take]+suffix);offset+=take
        return answer
    return []
'''


SORT_LEVELS = '''def minimum_level_sort_operations(root):
    from collections import deque
    queue=deque([root]);answer=0
    while queue:
        values=[]
        for _ in range(len(queue)):
            node=queue.popleft();values.append(node.val)
            if node.left:queue.append(node.left)
            if node.right:queue.append(node.right)
        positions={value:index for index,value in enumerate(sorted(values))}
        permutation=[positions[value] for value in values]
        for index in range(len(permutation)):
            while permutation[index]!=index:
                other=permutation[index];permutation[index],permutation[other]=permutation[other],permutation[index];answer+=1
    return answer
'''


UNSORTED_LEVELS = '''def minimum_level_sort_operations(root):
    from collections import deque
    queue=deque([root]);answer=0
    while queue:
        values=[]
        for _ in range(len(queue)):
            node=queue.popleft();values.append(node.val)
            if node.left:queue.append(node.left)
            if node.right:queue.append(node.right)
        answer+=values!=sorted(values)
    return answer
'''


INVERSION_LEVELS = '''def minimum_level_sort_operations(root):
    from collections import deque
    queue=deque([root]);answer=0
    while queue:
        values=[]
        for _ in range(len(queue)):
            node=queue.popleft();values.append(node.val)
            if node.left:queue.append(node.left)
            if node.right:queue.append(node.right)
        answer+=sum(values[i]>values[j] for i in range(len(values)) for j in range(i+1,len(values)))
    return answer
'''


PALINDROMES = '''def maximum_nonoverlapping_palindromes(s,k):
    size=len(s);palindrome=[[False]*size for _ in range(size)]
    for left in range(size-1,-1,-1):
        for right in range(left,size):
            palindrome[left][right]=s[left]==s[right] and (right-left<2 or palindrome[left+1][right-1])
    best=[0]*(size+1)
    for end in range(1,size+1):
        best[end]=best[end-1]
        for start in range(end-k+1):
            if palindrome[start][end-1]:best[end]=max(best[end],best[start]+1)
    return best[size]
'''


COUNT_OVERLAPPING = '''def maximum_nonoverlapping_palindromes(s,k):
    return sum(s[left:right]==s[left:right][::-1] for left in range(len(s)) for right in range(left+k,len(s)+1))
'''


BST_QUERIES = '''def closest_bst_nodes(root,queries):
    import bisect
    values=[];stack=[];node=root
    while node or stack:
        while node:stack.append(node);node=node.left
        node=stack.pop();values.append(node.val);node=node.right
    answer=[]
    for query in queries:
        lower=bisect.bisect_right(values,query)-1;upper=bisect.bisect_left(values,query)
        answer.append([values[lower] if lower>=0 else -1,values[upper] if upper<len(values) else -1])
    return answer
'''


NEAREST_ONLY = '''def closest_bst_nodes(root,queries):
    values=[];stack=[root]
    while stack:
        node=stack.pop();values.append(node.val)
        if node.left:stack.append(node.left)
        if node.right:stack.append(node.right)
    return [[min(values,key=lambda value:abs(value-query))]*2 for query in queries]
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


BATCH = {
    2454: entry(
        'second_greater_elements', [('nums','list[int]')], 'list[int]', ['monotonic stacks','arrays'],
        ['nums contains 1 through 100000 nonnegative integers.', 'For each index, find the value at the second later index whose value is strictly greater than nums[i].', 'Return -1 where fewer than two later greater values exist.'],
        [([[2,4,0,9,6]], 'For two, the greater values encountered are four then nine; analogous scans produce [9,6,6,-1,-1].'), ([[3,3]], 'Equal values are not strictly greater, so neither index has a second greater value.')],
        [[[value for value in nums]] for nums in [[1],[1,2],[1,2,3],[3,2,1],[1,3,2],[2,1,3],[1,1,2,2,3],[5,1,2,3,4],[0,0,1,0,2],[4,5,1,2,6],[2,4,3,5,1,6],[9,1,8,2,7,3],[1,5,2,4,3,6],[6,2,6,3,7,4,8]]],
        SECOND_GREATER,
        [SECOND_GREATER.replace('nums[second[-1]]<value','nums[second[-1]]<=value').replace('nums[first[-1]]<value','nums[first[-1]]<=value'), FIRST_GREATER],
        ['Treats equal values as greater.', 'Returns the first greater value instead of waiting for the second.'],
        second_greater_oracle, random_second_greater,
        lesson('An index passes through two waiting stages as greater values arrive.', 'Use one decreasing stack awaiting its first greater value and another awaiting its second.', 'Resolve the second stack with the current value, move newly first-greater indices from the first stack to the second in order, then push the current index.', 'Each index changes stage exactly when a strictly greater value is encountered, so the value that removes it from the second stage is precisely its second greater value.'),
        'O(n)', 'O(n)', 8,
    ),
    2468: entry(
        'split_message', [('message','str'),('limit','int')], 'list[str]', ['strings','enumeration','counting'],
        ['message is nonempty and each part ends with <index/total>.', 'Every part except the last has exactly limit characters; the last has at most limit.', 'Return the split using the fewest parts, or an empty list if no valid split exists.'],
        [(['this is really a very awesome message',9], 'Fourteen parts are the first feasible total once every suffix is counted.'), (['short message',15], 'Two parts carry ten and three message characters before their suffixes.')],
        [[m,l] for m,l in [('a',5),('a',4),('abc',6),('abc',5),('abcdefghij',7),('abcdefghij',8),('hello world',10),('aaaaaa',6),('abcdefghijklmno',9),('one two three',8),('xyz',10),('abcdefghijklmnopqrst',10),('a b c d e f',7),('message',12)]],
        SPLIT_MESSAGE,
        [SPLIT_MESSAGE.replace('digit_sum+=len(str(total))','digit_sum+=1'), SPLIT_MESSAGE.replace("suffix=f'<{index}/{total}>'", "suffix=f'<{index}>'")],
        ['Assumes every part index has one digit and overestimates capacity after part nine.', 'Builds suffixes without the required total-part denominator.'],
        split_message_oracle, random_split_message,
        lesson('Suffix length changes when either the index or total gains a digit.', 'Enumerate candidate totals while maintaining the sum of index digit lengths and calculate usable capacity exactly.', 'Choose the first total with positive per-part capacity and enough aggregate capacity, then slice the message using each suffix’s remaining room.', 'Candidate totals are checked in increasing order, and exact suffix accounting proves feasibility; therefore the first constructed split uses the minimum number of parts.'),
        'O(message length)', 'O(message length)', 8,
    ),
    2471: entry(
        'minimum_level_sort_operations', [('root','TreeNode')], 'int', ['trees','breadth-first search','permutations'],
        ['The nonempty binary tree has unique values.', 'One operation swaps any two values on the same level.', 'Return the minimum total swaps that make every level strictly increasing.'],
        [([[1,4,3,7,6,8,5,None,None,None,None,9,None,10]], 'Level two needs one swap and level three needs two, for three operations total.'), ([[1,2,3,4,5,6]], 'Every level is already increasing, so no operation is required.')],
        [[[value for value in tree]] for tree in [[1],[2,1,3],[1,3,2],[1,4,3,2,5,7,6],[1,2,3,7,6,5,4],[5,3,8,1,4,7,9],[1,5,2,9,8,7,6],[10,20,5,30,25,8,1],[4,2,6,1,3,5,7],[1,9,8,7,6,5,4],[7,3,9,None,5,8,10],[8,4,12,6,2,14,10],[1,10,2,9,3,8,4],[50,20,80,10,30,90,70]]],
        SORT_LEVELS,
        [UNSORTED_LEVELS, INVERSION_LEVELS],
        ['Counts only whether a level is unsorted instead of its minimum swaps.', 'Counts adjacent swaps through inversions even though one operation may swap any two level values.'],
        sort_levels_oracle, random_sort_levels,
        lesson('Each level is an independent permutation-sorting problem.', 'Traverse by BFS, map each unique value to its sorted position, and count permutation-cycle swaps.', 'For each position, repeatedly swap its mapped destination into place and add one.', 'A permutation cycle of length c needs exactly c-1 arbitrary swaps; summing those minima across independent levels yields the global minimum.'),
        'O(nodes log nodes)', 'O(width)', 5,
    ),
    2472: entry(
        'maximum_nonoverlapping_palindromes', [('s','str'),('k','int')], 'int', ['dynamic programming','strings','palindromes'],
        ['s is a nonempty lowercase string and 1 <= k <= len(s).', 'Choose contiguous palindromes of length at least k whose index ranges do not overlap.', 'Return the greatest possible number of chosen substrings.'],
        [(['abaccdbbd',3], 'The non-overlapping palindromes aba and dbbd give the optimal count two.'), (['adbcda',2], 'No substring of length at least two is a palindrome, so the answer is zero.')],
        [[s,k] for s,k in [('a',1),('aa',1),('aa',2),('ab',1),('ab',2),('aba',2),('aba',3),('aaaa',2),('aaaaa',3),('abbaeae',3),('abcbaab',3),('racecarx',4),('aabbaa',2),('abacdcaba',3)]],
        PALINDROMES,
        [PALINDROMES.replace('for start in range(end-k+1):', 'for start in [end-k] if end>=k else []:'), COUNT_OVERLAPPING],
        ['Considers only palindromes of exactly k characters and misses longer valid choices.', 'Counts every qualifying palindrome even when their ranges overlap.'],
        palindromes_oracle, random_palindromes,
        lesson('A prefix optimum either skips its last character or ends with one chosen palindrome.', 'Precompute palindrome intervals, then run prefix DP over non-overlapping endings.', 'For each end, inherit the previous best and try every qualifying palindrome [start,end), adding one to best[start].', 'Every optimal selection has a final interval or omits the final character; these exhaustive disjoint cases make the prefix recurrence exact.'),
        'O(n^2)', 'O(n^2)', 8,
    ),
    2476: entry(
        'closest_bst_nodes', [('root','TreeNode'),('queries','list[int]')], 'list[list[int]]', ['binary search trees','inorder traversal','binary search'],
        ['The BST has at least two nodes with distinct positive values.', 'For each query return [largest value <= query, smallest value >= query].', 'Use -1 for a missing lower or upper bound and preserve query order.'],
        [([[6,2,13,1,4,9,15,None,None,None,None,None,None,14],[2,5,16]], 'The exact two, the neighbors four and six, and the missing upper bound give [[2,2],[4,6],[15,-1]].'), ([[4,None,9],[3]], 'No tree value is at most three, while four is the smallest value at least three.')],
        [[tree,queries] for tree,queries in [
            ([2,1,3],[2]), ([2,1,3],[0,4]), ([4,2,6,1,3,5,7],[4]),
            ([4,2,6,1,3,5,7],[0,8]), ([4,2,6,1,3,5,7],[3,4,5]),
            ([5,3,8,2,4,7,9],[1,6,10]), ([10,5,15,None,7,12,20],[6,13]),
            ([1,None,2,None,3],[1,2,4]), ([3,2,None,1],[0,2,5]),
            ([8,4,12,2,6,10,14],[5,11,13]), ([20,10,30,5,15,25,35],[14,16,20]),
            ([6,2,9,1,4,8,10],[3,7]), ([50,25,75,10,40,60,90],[26,74]),
            ([7,3,11,1,5,9,13],[7,12]),
        ]],
        BST_QUERIES,
        [BST_QUERIES.replace('lower=bisect.bisect_right(values,query)-1', 'lower=bisect.bisect_left(values,query)-1'), NEAREST_ONLY],
        ['Uses a strict lower bound, incorrectly excluding an exact query match.', 'Returns one nearest value twice rather than independent floor and ceiling bounds.'],
        bst_queries_oracle, random_bst_queries,
        lesson('Inorder traversal turns a BST into a sorted array.', 'Collect values iteratively, then answer each floor and ceiling query with upper- and lower-bound binary searches.', 'Floor is upper_bound(query)-1; ceiling is lower_bound(query); replace out-of-range indices with -1.', 'Sorted-order boundary searches directly identify the greatest allowed lower value and smallest allowed upper value for each independent query.'),
        'O(nodes+queries log nodes)', 'O(nodes)', 5,
    ),
}

BATCH[2471]['params'][0] = ('root','TreeNode','treenode')
BATCH[2476]['params'][0] = ('root','TreeNode','treenode')
