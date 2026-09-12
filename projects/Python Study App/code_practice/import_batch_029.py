"""Bit sets, recursive enumeration, prefix sums, matrix DAGs and tree DP."""
from collections import deque
from itertools import combinations

from .import_batch_002 import positions, random_tree
from .import_batch_003 import entry
from .import_batch_024 import right_chain


def word_product_oracle(args):
    words = args[0]
    return max((len(a)*len(b) for a, b in combinations(words, 2) if not set(a) & set(b)), default=0)


def abbreviation_oracle(args):
    word = args[0]
    answers = []
    for mask in range(1 << len(word)):
        result, index = [], 0
        while index < len(word):
            if mask & (1 << index):
                end = index + 1
                while end < len(word) and mask & (1 << end):
                    end += 1
                result.append(str(end-index))
                index = end
            else:
                result.append(word[index])
                index += 1
        answers.append(''.join(result))
    return sorted(answers)


def power_three_oracle(args):
    return args[0] in {3**exponent for exponent in range(20)}


def range_sum_oracle(args):
    nums, lower, upper = args
    answer = 0
    for start in range(len(nums)):
        total = 0
        for end in range(start, len(nums)):
            total += nums[end]
            answer += lower <= total <= upper
    return answer


def increasing_path_oracle(args):
    """Enumerate every strictly increasing path, without memoized subproblems."""
    matrix = args[0]
    rows, columns = len(matrix), len(matrix[0])
    longest = 1
    for r in range(rows):
        for c in range(columns):
            stack = [(r, c, 1)]
            while stack:
                row, column, length = stack.pop()
                longest = max(longest, length)
                for nr, nc in ((row-1,column), (row+1,column), (row,column-1), (row,column+1)):
                    if 0 <= nr < rows and 0 <= nc < columns and matrix[nr][nc] > matrix[row][column]:
                        stack.append((nr, nc, length+1))
    return longest


def patch_oracle(args):
    """BFS over complete subset-sum sets, trying every possible added value."""
    nums, n = args
    limit = (1 << (n+1)) - 1
    sums = 1
    for value in nums:
        sums = (sums | (sums << value)) & limit
    queue, seen = deque([(sums, 0)]), {sums}
    while queue:
        state, count = queue.popleft()
        if state == limit:
            return count
        for patch in range(1, n+1):
            updated = (state | (state << patch)) & limit
            if updated not in seen:
                seen.add(updated)
                queue.append((updated, count+1))


def serialization_oracle(args):
    """Repeatedly collapse complete leaf subtrees into a null marker."""
    stack = []
    for token in args[0].split(','):
        stack.append(token)
        while len(stack) >= 3 and stack[-2:] == ['#', '#'] and stack[-3] != '#':
            stack[-3:] = ['#']
    return stack == ['#']


def largest_bst_oracle(args):
    mapping = positions(args[0])
    longest = 0
    for root in mapping:
        subtree = {path: value for path, value in mapping.items() if path[:len(root)] == root}
        valid = True
        for path, value in subtree.items():
            for depth in range(len(root), len(path)):
                ancestor = mapping[path[:depth]]
                if (path[depth] == 0 and value >= ancestor) or (path[depth] == 1 and value <= ancestor):
                    valid = False
                    break
            if not valid:
                break
        if valid:
            longest = max(longest, len(subtree))
    return longest


def tree_robber_oracle(args):
    mapping = positions(args[0])
    paths = list(mapping)
    best = 0
    for mask in range(1 << len(paths)):
        selected = {path for i, path in enumerate(paths) if mask & (1 << i)}
        if all(not path or path[:-1] not in selected for path in selected):
            best = max(best, sum(mapping[path] for path in selected))
    return best


def random_words(rng):
    return [[''.join(rng.choice('abcdef') for _ in range(rng.randint(1, 8)))
             for _ in range(rng.randint(2, 8))]]


def random_abbreviations(rng):
    return [''.join(rng.choice('abcde') for _ in range(rng.randint(1, 8)))]


def random_power_three(rng):
    return [rng.choice([3**rng.randrange(20), rng.randint(-(2**31), 2**31-1)])]


def random_range_sum(rng):
    lower, upper = sorted([rng.randint(-12, 12), rng.randint(-12, 12)])
    return [[rng.randint(-7, 7) for _ in range(rng.randint(1, 15))], lower, upper]


def random_matrix_path(rng):
    rows, columns = rng.randint(1, 3), rng.randint(1, 3)
    return [[[rng.randint(0, 9) for _ in range(columns)] for _ in range(rows)]]


def random_patches(rng):
    return [sorted(rng.randint(1, 9) for _ in range(rng.randint(1, 5))), rng.randint(1, 10)]


def random_serialization(rng):
    if rng.random() < .5:
        def tree(depth):
            if depth == 0 or rng.random() < .35:
                return ['#']
            return [str(rng.randint(0, 100))] + tree(depth-1) + tree(depth-1)
        return [','.join(tree(5))]
    return [','.join(rng.choice(['#', '0', '1', '100']) for _ in range(rng.randint(1, 25)))]


def random_bst_subtree(rng):
    return [random_tree(rng)]


def random_tree_robber(rng):
    tree = random_tree(rng, nonempty=True)[:11]
    return [[None if value is None else abs(value) for value in tree]]


WORD_PRODUCT = '''\
def max_word_length_product(words):
    longest = {}
    for word in words:
        mask = 0
        for letter in set(word):
            mask |= 1 << (ord(letter)-ord('a'))
        longest[mask] = max(longest.get(mask, 0), len(word))
    items = list(longest.items())
    best = 0
    for i, (mask, length) in enumerate(items):
        for other_mask, other_length in items[i+1:]:
            if mask & other_mask == 0:
                best = max(best, length * other_length)
    return best
'''

ABBREVIATIONS = '''\
def generalized_abbreviations(word):
    result = []
    def visit(index, prefix, skipped):
        if index == len(word):
            result.append(prefix + (str(skipped) if skipped else ''))
            return
        visit(index+1, prefix, skipped+1)
        visit(index+1, prefix + (str(skipped) if skipped else '') + word[index], 0)
    visit(0, '', 0)
    return result
'''

POWER_THREE = '''\
def is_power_of_three(n):
    if n <= 0:
        return False
    while n % 3 == 0:
        n //= 3
    return n == 1
'''

RANGE_SUM = '''\
def count_range_sum(nums, lower, upper):
    prefix = [0]
    for value in nums:
        prefix.append(prefix[-1] + value)
    def count_sort(values):
        if len(values) <= 1:
            return 0, values
        middle = len(values)//2
        count_left, left = count_sort(values[:middle])
        count_right, right = count_sort(values[middle:])
        total = count_left + count_right
        low = high = 0
        for start in left:
            while low < len(right) and right[low]-start < lower:
                low += 1
            while high < len(right) and right[high]-start <= upper:
                high += 1
            total += high-low
        merged, i, j = [], 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return total, merged
    return count_sort(prefix)[0]
'''

MATRIX_PATH = '''\
def longest_increasing_matrix_path(matrix):
    from collections import deque
    rows, columns = len(matrix), len(matrix[0])
    degree = [[0]*columns for _ in range(rows)]
    for r in range(rows):
        for c in range(columns):
            for nr, nc in ((r-1,c), (r+1,c), (r,c-1), (r,c+1)):
                if 0 <= nr < rows and 0 <= nc < columns and matrix[nr][nc] < matrix[r][c]:
                    degree[r][c] += 1
    queue = deque((r,c) for r in range(rows) for c in range(columns) if degree[r][c] == 0)
    length = 0
    while queue:
        length += 1
        for _ in range(len(queue)):
            r, c = queue.popleft()
            for nr, nc in ((r-1,c), (r+1,c), (r,c-1), (r,c+1)):
                if 0 <= nr < rows and 0 <= nc < columns and matrix[nr][nc] > matrix[r][c]:
                    degree[nr][nc] -= 1
                    if degree[nr][nc] == 0:
                        queue.append((nr,nc))
    return length
'''

PATCHES = '''\
def min_patches(nums, n):
    missing, index, patches = 1, 0, 0
    while missing <= n:
        if index < len(nums) and nums[index] <= missing:
            missing += nums[index]
            index += 1
        else:
            patches += 1
            missing += missing
    return patches
'''

SERIALIZATION = '''\
def valid_preorder_serialization(preorder):
    slots = 1
    for token in preorder.split(','):
        if slots == 0:
            return False
        slots -= 1
        if token != '#':
            slots += 2
    return slots == 0
'''

LARGEST_BST = '''\
def largest_bst_subtree(root):
    if root is None:
        return 0
    summaries = {id(None): (True, 0, float('inf'), float('-inf'))}
    stack, answer = [(root, False)], 0
    while stack:
        node, visited = stack.pop()
        if not visited:
            stack.append((node, True))
            if node.right:
                stack.append((node.right, False))
            if node.left:
                stack.append((node.left, False))
            continue
        left_ok, left_size, left_min, left_max = summaries[id(node.left)]
        right_ok, right_size, right_min, right_max = summaries[id(node.right)]
        valid = left_ok and right_ok and left_max < node.val < right_min
        size = left_size + right_size + 1 if valid else 0
        summaries[id(node)] = (valid, size, min(left_min, node.val), max(right_max, node.val))
        answer = max(answer, size)
    return answer
'''

TREE_ROBBER = '''\
def rob_tree(root):
    summaries = {id(None): (0, 0)}
    stack = [(root, False)]
    while stack:
        node, visited = stack.pop()
        if not visited:
            stack.append((node, True))
            if node.right:
                stack.append((node.right, False))
            if node.left:
                stack.append((node.left, False))
            continue
        left_take, left_skip = summaries[id(node.left)]
        right_take, right_skip = summaries[id(node.right)]
        take = node.val + left_skip + right_skip
        skip = max(left_take, left_skip) + max(right_take, right_skip)
        summaries[id(node)] = (take, skip)
    return max(summaries[id(root)])
'''

WORD_DISTINCT_LENGTH = WORD_PRODUCT.replace('len(word)', 'len(set(word))')
WORD_DIFFERENT_MASK = WORD_PRODUCT.replace('mask & other_mask == 0', 'mask != other_mask')
ABBREVIATION_ONES = ABBREVIATIONS.replace("str(skipped)", "'1'*skipped")
ABBREVIATION_ONE_RUN = '''\
def generalized_abbreviations(word):
    return [word] + [word[:i]+str(j-i)+word[j:] for i in range(len(word)) for j in range(i+1,len(word)+1)]
'''
DIVISIBLE_THREE = '''\
def is_power_of_three(n):
    return n == 1 or (n > 0 and n % 3 == 0)
'''
NOT_ONE_THREE = POWER_THREE.replace('if n <= 0:', 'if n <= 1:')
EXCLUSIVE_RANGE = RANGE_SUM.replace('right[high]-start <= upper', 'right[high]-start < upper')
MISSING_ZERO_PREFIX = RANGE_SUM.replace('    return count_sort(prefix)[0]', '    return count_sort(prefix[1:])[0]')
DIAGONAL_PATH = MATRIX_PATH.replace('(r-1,c), (r+1,c), (r,c-1), (r,c+1)',
    '(r-1,c), (r+1,c), (r,c-1), (r,c+1), (r-1,c-1), (r-1,c+1), (r+1,c-1), (r+1,c+1)')
UNIT_STEP_PATH = MATRIX_PATH.replace('matrix[nr][nc] < matrix[r][c]', 'matrix[nr][nc] == matrix[r][c]-1').replace(
    'matrix[nr][nc] > matrix[r][c]', 'matrix[nr][nc] == matrix[r][c]+1')
PATCH_TOO_LARGE = PATCHES.replace('missing += missing', 'missing += missing + 1')
PATCH_STRICT = PATCHES.replace('nums[index] <= missing', 'nums[index] < missing')
SERIAL_COUNT_ONLY = '''\
def valid_preorder_serialization(preorder):
    tokens = preorder.split(',')
    return tokens.count('#') == len(tokens)-tokens.count('#')+1
'''
SERIAL_UNFINISHED = SERIALIZATION.replace('return slots == 0', 'return slots >= 0')
BST_ALLOW_EQUAL = LARGEST_BST.replace('left_max < node.val < right_min', 'left_max <= node.val <= right_min')
BST_LOCAL_ONLY = LARGEST_BST.replace('left_max < node.val < right_min',
    '(node.left is None or node.left.val < node.val) and (node.right is None or node.right.val > node.val)')
ROBBER_SKIP_CHILDREN = TREE_ROBBER.replace('take = node.val + left_skip + right_skip', 'take = node.val')
ROBBER_LEVELS = '''\
def rob_tree(root):
    levels = [0, 0]
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        levels[depth%2] += node.val
        if node.left:
            stack.append((node.left, depth+1))
        if node.right:
            stack.append((node.right, depth+1))
    return max(levels)
'''

snake = [list(range(row*200, (row+1)*200))[::1 if row%2 == 0 else -1] for row in range(200)]

BATCH = {
    318: entry('max_word_length_product', [('words','list[str]')], 'int', ['strings','bit-manipulation','hash-maps'],
        ['2–1000 words, each with 1–1000 lowercase English letters.',
         'Choose two different positions whose words share NO letter. Maximize the product of their full lengths, counting repeated letters in each length. Return 0 if no pair works.'],
        [([['abcw','baz','foo','bar','xtfn','abcdef']], 'abcw and xtfn share no letters and have lengths 4 and 4, giving 16.'),
         ([['aa','bbb','ab']], 'aa and bbb are disjoint and give 2×3=6. Repeated letters count toward length.')],
        [[words] for words in (['a','b'],['a','a'],['ab','bc'],['ab','cd'],['abc','def','ad'],
            ['a','aa','aaa'],['a','bb','ccc'],['ab','cd','abcd'],['zz','yyy','zx'],['xy','xz','yz'],
            ['aaaa','b','bb'],['ab','ba','ccc'],['az','by','cx'],['a','abcdefghijklmnopqrstuvwxy','z'])],
        WORD_PRODUCT, [WORD_DISTINCT_LENGTH,WORD_DIFFERENT_MASK],
        ['Uses the number of distinct letters instead of the word length.', 'Assumes different masks are disjoint even when they share some letters.'],
        word_product_oracle, random_words,
        ['Only letter membership determines whether a pair is compatible.',
         'Encode the 26 lowercase letters as bits; two masks are disjoint when their bitwise AND is zero.',
         'Store the greatest full word length for each mask, then compare every pair of masks with AND=0.',
         'Keeping only the longest word for a mask is safe because all words with that mask have the same compatible partners.'],
        'A 26-bit mask records membership, while length is kept separately. Any two words with a common letter have a nonzero mask intersection. Compress equal masks to their longest length and maximize products of compatible pairs. The oracle compares explicit character sets for every original pair.',
        'O(L+u^2), L = total characters, u = distinct masks', 'O(u)', difficulty=6,
        stress=[([['a'*1000]*500+['b'*1000]*500],1000000)]),
    320: entry('generalized_abbreviations', [('word','str')], 'list[str]', ['recursion','backtracking','strings'],
        ['1 <= len(word) <= 15; lowercase English letters only.',
         'Independently keep or abbreviate each character. Replace every maximal consecutive abbreviated run by its decimal length; do not write adjacent separate counts. Return every result once in any order.'],
        [(['word'], 'Each of four positions can be kept or abbreviated, giving 16 results. For example w2d replaces or, and 1o1d replaces w and r.'),
         (['a'], 'Either keep a or replace its single character by 1, so the results are [a,1].')],
        [[word] for word in ('b','ab','aa','abc','aba','abcd','aaaa','hello','abcdef','ababa','code','python')],
        ABBREVIATIONS,[ABBREVIATION_ONES,ABBREVIATION_ONE_RUN],
        ['Writes runs as repeated 1s instead of one decimal count.', 'Generates only a single removed run and misses separated abbreviated runs.'],
        abbreviation_oracle,random_abbreviations,
        ['At each position, choose whether to keep the character or add it to an abbreviated run.',
         'Carry an unfinished skip count instead of immediately writing a number for each removed character.',
         'Recurse with skip+1 for abbreviation. To keep a character, flush the skip count, append the character, and reset skip to zero.',
         'At the end flush any remaining count. Binary decisions generate 2^n unique outputs without adjacent abbreviation counts.'],
        'A pending count combines adjacent skipped characters into one legal run. Keeping a letter ends that run and separates it from any later count. Each keep/skip mask corresponds to exactly one output, including the unchanged word and the all-abbreviated length. The oracle scans bit masks and compresses consecutive set-bit positions independently.',
        'O(n*2^n)', 'O(n*2^n) including output',difficulty=6,
        stress=[(['abcdefghijklmno'],abbreviation_oracle(['abcdefghijklmno']))]),
    326: entry('is_power_of_three',[('n','int')],'bool',['math','recursion'],
        ['-(2^31) <= n <= 2^31-1. Return whether n = 3^x for a nonnegative integer x.',
         '1 is 3^0 and is valid. Zero, negatives, and multiples of 3 containing other factors are invalid.'],
        [([27],'27 = 3×3×3, so return true.'),([45],'45 is divisible by 3, but after removing its two factors of 3, a factor 5 remains. Return false.')],
        [[n] for n in (0,1,-1,2,3,6,9,12,18,81,243,244,-27,1162261467,2147483647,-2147483648)],
        POWER_THREE,[DIVISIBLE_THREE,NOT_ONE_THREE],
        ['Accepts all positive multiples of 3, including numbers with other prime factors.', 'Rejects 1 even though exponent zero is allowed.'],
        power_three_oracle,random_power_three,
        ['Repeated division by 3 removes exactly the allowed prime factors.',
         'Reject nonpositive inputs first; then keep dividing while the remainder is zero.',
         'While n%3==0, set n=n//3. The original number was a power of three exactly when the remaining n is 1.',
         'For this fixed 32-bit domain, the optional loop-free method checks whether positive n divides 3^19=1162261467.'],
        'Repeatedly remove factors of three. A positive integer is a power of three exactly when no factor remains afterward. The n=1 case succeeds without entering the loop. The independent oracle checks membership in the complete finite set of 32-bit powers. This differs from power-of-two exercises because divisibility is by three.',
        'O(log n) for positive n', 'O(1)',difficulty=3),
    327: entry('count_range_sum',[('nums','list[int]'),('lower','int'),('upper','int')],'int',
        ['prefix-sums','divide-and-conquer','recursion','binary-search'],
        ['1 <= len(nums) <= 100000; each element is a signed 32-bit integer.',
         '-100000 <= lower <= upper <= 100000. The answer fits a signed 32-bit integer.',
         'Count nonempty contiguous index ranges whose sum lies between BOTH inclusive bounds. Different index ranges count separately even if their sums are equal.'],
        [([[-2,5,-1],-2,2],'The ranges [0,0], [2,2], and [0,2] have sums -2,-1,2, giving 3.'),
         ([[0,0],0,0],'The two single-element ranges and the full two-element range all sum to zero. Return 3.')],
        [[nums,lo,hi] for nums,lo,hi in (([0],0,0),([1],1,1),([-1],-1,-1),([1],2,3),
            ([1,-1],0,0),([2,-2,2],-2,2),([1,2,3],3,3),([-3,-2,-1],-5,-2),
            ([5,-5,5,-5],0,0),([0,0,0],-1,1),([10,-10,1],-1,1),
            ([2147483647,2147483647,-2147483648,-2147483648],-2,2),([2,2,2],2,4))],
        RANGE_SUM,[EXCLUSIVE_RANGE,MISSING_ZERO_PREFIX],
        ['Treats the upper bound as exclusive and misses sums exactly equal to it.', 'Omits the initial zero prefix, losing ranges that start at index zero.'],
        range_sum_oracle,random_range_sum,
        ['A range sum is the difference of two prefix sums with the earlier index first.',
         'Divide prefix positions into halves. For each left prefix, count right prefixes between left+lower and left+upper.',
         'Recursively sort each half. Move two monotone pointers through the right half for each sorted left prefix, then merge.',
         'Add within-half and cross-half counts. Include prefix zero, and preserve duplicate prefixes because they represent distinct positions.'],
        'Each range corresponds uniquely to a pair of prefix positions i<j. Recursive splitting counts pairs within either half; a merge step counts pairs across the split, where index order is already guaranteed. Sorted values allow two linear sweeps for inclusive bounds. Merging preserves duplicates, so equal-valued prefixes retain their multiplicity. The oracle directly accumulates every nonempty subarray.',
        'O(n log n)','O(n)',difficulty=8,
        stress=[([[1]*100000,1,1000],99500500),([[0]*65535,0,0],2147450880)]),
    329: entry('longest_increasing_matrix_path',[('matrix','list[list[int]]')],'int',
        ['matrices','graphs','recursion','dynamic-programming'],
        ['matrix is rectangular with 1–200 rows and 1–200 columns; values are 0 through 2^31-1.',
         'Count cells on the longest path with strictly increasing values. You may start anywhere and move only up, down, left, or right, without wrapping. Equal values are not a legal step.'],
        [([[[9,9,4],[6,6,8],[2,1,1]]],'A path of four cells has values 1→2→6→9. No strictly increasing path is longer.'),
         ([[[1,10],[2,3]]],'The path 1→2→3→10 uses all four cells. Increases need not be exactly one.')],
        [[grid] for grid in ([[0]],[[1]],[[1,1]],[[1,2,3]],[[3,2,1]],[[1],[2],[3]],
            [[1,1],[1,1]],[[1,4],[3,2]],[[1,0],[0,2]],[[3,4,5],[3,2,6],[2,2,1]],
            [[0,2147483647]],[[5,4,3],[6,1,2]],[[1,2,1],[2,3,2]],[[9,1,8],[2,7,3]])],
        MATRIX_PATH,[DIAGONAL_PATH,UNIT_STEP_PATH],
        ['Allows diagonal movement, joining cells that are not four-direction neighbors.', 'Requires an increase of exactly one and misses valid larger increases.'],
        increasing_path_oracle,random_matrix_path,
        ['Direct edges from smaller cells to larger neighboring cells; strict increase prevents cycles.',
         'Memoized DFS can compute the longest suffix at each cell. Alternatively, process the graph in topological layers.',
         'Count incoming edges from smaller neighbors. Queue local minima; remove one queue layer at a time, decrementing larger neighbors\' incoming counts.',
         'The number of layers equals the longest increasing path. An explicit queue also handles a 40000-cell path without Python call-stack limits.'],
        'Strictly increasing edges make a directed acyclic graph. A cell can be removed only after all smaller predecessors have been removed, so its layer is one plus the greatest predecessor layer. The largest layer is the longest path length. Memoized DFS uses the equivalent recurrence; the reference uses a queue to handle deeply winding paths. The oracle enumerates all paths on small grids without caching.',
        'O(mn)','O(mn)',difficulty=8,
        stress=[([snake],40000),([[[7]*200 for _ in range(200)]],1)]),
    330: entry('min_patches',[('nums','list[int]'),('n','int')],'int',['greedy','arrays','intervals'],
        ['nums contains 1–1000 positive integers from 1 through 10000 in nondecreasing order; 1 <= n <= 2^31-1.',
         'Add as few positive integers as possible so every target from 1 through n is a subset sum. Each array occurrence or added occurrence can be used at most once in a given sum.'],
        [([[1,3],6],'Adding 2 gives [1,2,3], whose subset sums include every integer from 1 through 6. One patch suffices.'),
         ([[1,5,10],20],'Add 2 and 4. These extend coverage to 1–7, then 5 and 10 extend it beyond 20. Return 2.')],
        [[nums,n] for nums,n in (([1],1),([2],1),([1],2),([1,2,2],5),([1,1],5),
            ([3],6),([2,3],8),([1,2,3],10),([1,4],8),([1,1,1],8),
            ([4,5],10),([1,2,4,8],10),([10],10),([2,2,2],9))],
        PATCHES,[PATCH_TOO_LARGE,PATCH_STRICT],
        ['Adds missing+1, leaving the smallest uncovered value impossible to form.', 'Patches when the next existing number equals the first gap, although that number already fills it.'],
        patch_oracle,random_patches,
        ['Track a contiguous range of attainable sums, not the individual subsets.',
         'If all sums below missing are attainable, an existing value at most missing extends the covered range.',
         'Start missing=1. Consume nums[i]<=missing by adding it to missing; otherwise patch exactly missing and double missing.',
         'When missing>n all required values are covered. Patching the first gap is necessary and maximizes coverage for one added value.'],
        'Maintain that every sum in [0,missing) is attainable using processed occurrences. Consuming x<=missing extends coverage to [0,missing+x). If the next x is larger, no remaining existing value can form missing. Any useful patch must be at most missing; choosing exactly missing covers the most, doubling the range. The independent oracle performs breadth-first search over subset-sum sets and tries every candidate patch for small n.',
        'O(len(nums)+log n)','O(1)',difficulty=8,
        stress=[([[1],2147483647],30),([[10000]*1000,2147483647],22)]),
    331: entry('valid_preorder_serialization',[('preorder','str')],'bool',['trees','stacks','recursion'],
        ['1 <= len(preorder) <= 10000. Comma-separated tokens are # or integers from 0 through 100; token formatting is valid.',
         'A number consumes one child position and creates two child positions. # represents a null child. Validate the entire preorder sequence without reconstructing the tree.'],
        [(['9,3,4,#,#,1,#,#,2,#,6,#,#'],'Every numbered node has exactly two serialized child positions; after the last # the root tree is complete.'),
         (['9,#,#,1'],'9,#,# already completes a whole tree. The extra 1 has nowhere to attach, so return false.')],
        [[text] for text in ('#','1','1,#','1,#,#','#,#','#,1,#','1,2,#,#,#',
            '1,#,2,#,#','1,#,#,#','1,2,#,#','1,2,3,#,#,#,#','0,#,#','100,#,#','1,#,#,2,#,#')],
        SERIALIZATION,[SERIAL_COUNT_ONLY,SERIAL_UNFINISHED],
        ['Checks only final token counts, ignoring that all slots may be exhausted before the input ends.', 'Accepts a partial tree with unfilled child slots after the last token.'],
        serialization_oracle,random_serialization,
        ['Begin with one available position for the root.',
         'Every token fills one available position. A non-null node additionally supplies two child positions.',
         'Before each token reject if slots==0; decrement slots and add two for numbers. At the end require slots==0.',
         'A zero total alone is insufficient: no proper prefix may exhaust all positions while tokens remain.'],
        'The slot invariant represents the unfinished tree without building nodes. Null consumes one slot; a number consumes one and contributes two. Reject before consuming a token if no slot remains, and require none to remain after the final token. The independent oracle reduces completed number,#,# patterns to a single # and accepts exactly one fully reduced tree.',
        'O(n)','O(n) for split tokens',difficulty=6,
        stress=[([','.join(['0']*2499+['#']*2500)],True),([','.join(['0']*2500+['#']*2499)],False)]),
    333: entry('largest_bst_subtree',[('root','TreeNode | None')],'int',['trees','recursion','binary-search-trees'],
        ['root has 0–10000 nodes with values from -10000 through 10000.',
         'Return the largest number of nodes in a rooted subtree that is a STRICT BST. The subtree must include all descendants of its root; you cannot drop invalid branches.'],
        [([[10,5,15,1,8,None,7]],'The subtree rooted at 5 contains [5,1,8] and is a BST of size 3. The right child 7 under 15 prevents the entire tree from being a BST.'),
         ([[2,2,3]],'The duplicate 2 violates strict ordering at the root. Each leaf is a valid size-one BST, so return 1.')],
        [[tree] for tree in ([],[0],[2,1,3],[3,2,1],[1,None,2],[2,1],
            [10,5,15,None,12],[5,1,8,None,None,4,9],[2,1,2],[0,-1,1],
            [4,2,6,1,3,5,7],[4,2,7,2,3,5,None,2,None,None,None,None,None,1],
            [-10000,None,10000],[1,1,1])],
        LARGEST_BST,[BST_ALLOW_EQUAL,BST_LOCAL_ONLY],
        ['Allows equal descendant values even though BST ordering must be strict.', 'Checks direct children only, missing deeper values outside an ancestor\'s allowed range.'],
        largest_bst_oracle,random_bst_subtree,
        ['A parent needs more than each child\'s value: it needs the range and validity of the entire child subtree.',
         'Use postorder summaries: valid BST, node count, minimum value, maximum value.',
         'A subtree is valid when both children are valid and left.max < node.val < right.min. Combine counts and extrema; track the largest valid count.',
         'Use empty-subtree extrema +infinity/-infinity. An explicit visited-node stack computes the same recurrence without deep recursion.'],
        'Postorder makes both child summaries available. The extrema enforce ordering against every descendant, while child validity prevents invalid internal structures from passing. A failed subtree contributes no candidate size but does not erase the best size found below it. The reference uses iterative postorder for 10000-node chains. The oracle tries every possible subtree root and checks each descendant against every ancestor on its path.',
        'O(n)','O(n)',difficulty=6,
        stress=[([right_chain(10000)],10000)]),
    337: entry('rob_tree',[('root','TreeNode')],'int',['trees','recursion','dynamic-programming'],
        ['root contains 1–10000 nodes, each valued from 0 through 10000.',
         'Choose houses with maximum total value, never choosing both a parent and its direct child. Different branches may choose different depth parities.'],
        [([[3,2,3,None,3,None,1]],'Choose the root 3 and grandchildren 3 and 1 for total 7, skipping their direct parents.'),
         ([[3,4,5,1,3,None,1]],'Choosing children 4 and 5 gives 9, which is better than taking the root and grandchildren.')],
        [[tree] for tree in ([0],[1],[5,1,1],[1,5,5],[0,0,0],[4,1,None,2,None,3],
            [1,100,1,None,None,100,100],[10,1,1,10,10,10,10],[2,2,2,2],
            [1,None,2,None,3],[10000,0,10000],[0,1,None,0,None,1],[5,4,3,2,1],[2,1,3,None,4])],
        TREE_ROBBER,[ROBBER_SKIP_CHILDREN,ROBBER_LEVELS],
        ['When taking a node, discards all descendants instead of allowing grandchildren.', 'Chooses one global even/odd depth parity instead of optimizing each branch independently.'],
        tree_robber_oracle,random_tree_robber,
        ['For each subtree, distinguish whether its root is chosen or skipped.',
         'Taking a node forces both children to be skipped; skipping it lets each child choose its better state.',
         'take=node.val+left.skip+right.skip; skip=max(left.take,left.skip)+max(right.take,right.skip). Compute postorder.',
         'Return max(take,skip) at the root. Store the two states per node and use an explicit postorder stack for deep trees.'],
        'The only edge linking a subtree to its parent touches its root, so two states capture all constraints. The take state combines child skip states; the skip state combines independently optimized child states. This permits mixed choices across branches, unlike summing alternating levels. The oracle enumerates subsets of nodes and rejects any subset containing a parent-child pair.',
        'O(n)','O(n)',difficulty=6,
        stress=[([right_chain(10000)],25000000)]),
}
BATCH[320]['comparator'] = 'unordered'
BATCH[329]['statement'] = ('Return the number of cells on the longest strictly increasing path in matrix. '
                           'Start at any cell and move up, down, left, or right to a strictly greater value.')
for problem_id in (333,337):
    BATCH[problem_id]['params'] = [(BATCH[problem_id]['params'][0][0],BATCH[problem_id]['params'][0][1],'treenode')]
for problem_id, prerequisites in {327:['prefix-sums','binary-search'],329:['matrices','recursion'],330:['arrays','greedy']}.items():
    BATCH[problem_id]['prerequisites'] = prerequisites
