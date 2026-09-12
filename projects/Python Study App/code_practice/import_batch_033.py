"""Ordered leaf rounds, bounded rectangles, modular arithmetic and minimax DP."""
from functools import lru_cache
from math import isqrt

from .import_batch_002 import positions, random_tree
from .import_batch_003 import entry


def rectangle_oracle(args):
    matrix, k = args
    rows, cols = len(matrix), len(matrix[0])
    candidates = []
    for top in range(rows):
        for bottom in range(top+1, rows+1):
            for left in range(cols):
                for right in range(left+1, cols+1):
                    total = sum(matrix[r][c] for r in range(top,bottom) for c in range(left,right))
                    if total <= k:
                        candidates.append(total)
    if not candidates:
        raise ValueError('Source guarantees a nonempty rectangle with sum <= k')
    return max(candidates)


def leaves_oracle(args):
    remaining = positions(args[0])
    rounds = []
    while remaining:
        leaves = [path for path in remaining if path+(0,) not in remaining and path+(1,) not in remaining]
        rounds.append([remaining[path] for path in leaves])
        for path in leaves:
            del remaining[path]
    return rounds


def square_oracle(args):
    return isqrt(args[0])**2 == args[0]


def addition_oracle(args):
    return args[0]+args[1]


def power_oracle(args):
    # The trusted offline oracle can parse all 2000 digits (under Python's
    # 4300-digit safety limit); the reference instead processes digits online.
    return pow(args[0], int(''.join(map(str,args[1]))), 1337)


@lru_cache(None)
def all_guess_trees(low, high):
    if low > high:
        return (None,)
    return tuple((root,left,right) for root in range(low,high+1)
                 for left in all_guess_trees(low,root-1)
                 for right in all_guess_trees(root+1,high))


@lru_cache(None)
def guess_cost(n):
    """Simulate every hidden number through every binary decision tree."""
    best = float('inf')
    for tree in all_guess_trees(1,n):
        worst = 0
        for hidden in range(1,n+1):
            node, paid = tree, 0
            while node[0] != hidden:
                guess,left,right = node
                paid += guess
                node = left if hidden < guess else right
            worst = max(worst,paid)
        best = min(best,worst)
    return best


def guessing_oracle(args):
    return guess_cost(args[0])


def wiggle_oracle(args):
    values = args[0]
    best = 1
    for mask in range(1,1 << len(values)):
        subsequence = [value for i,value in enumerate(values) if mask & (1 << i)]
        differences = [b-a for a,b in zip(subsequence,subsequence[1:])]
        if all(differences) and all(a*b < 0 for a,b in zip(differences,differences[1:])):
            best = max(best,len(subsequence))
    return best


def ordered_sum_oracle(args):
    nums,target = args
    def enumerate_sequences(remaining):
        if remaining == 0:
            return 1
        return sum(enumerate_sequences(remaining-value) for value in nums if value <= remaining)
    return enumerate_sequences(target)


def kth_matrix_oracle(args):
    matrix,k = args
    return sorted(value for row in matrix for value in row)[k-1]


def random_rectangle(rng):
    rows,cols = rng.randint(1,4),rng.randint(1,4)
    matrix = [[rng.randint(-8,8) for _ in range(cols)] for _ in range(rows)]
    # Ensure at least a singleton is feasible, while keeping negative targets.
    return [matrix,rng.randint(min(map(min,matrix)),20)]


def random_leaves(rng):
    return [random_tree(rng,nonempty=True)]


def random_square(rng):
    root = rng.randint(1,46340)
    return [rng.choice([root*root,root*root+1,rng.randint(1,2**31-1)])]


def random_addition(rng):
    return [rng.randint(-1000,1000),rng.randint(-1000,1000)]


def random_power(rng):
    return [rng.randint(1,2**31-1),list(map(int,str(rng.randint(1,100000))))]


def random_guess(rng):
    return [rng.randint(1,8)]


def random_wiggle(rng):
    return [[rng.randint(0,8) for _ in range(rng.randint(1,10))]]


def random_ordered_sum(rng):
    return [rng.sample(range(1,9),rng.randint(1,5)),rng.randint(1,12)]


def random_kth_matrix(rng):
    n = rng.randint(1,5)
    matrix = [[0]*n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            matrix[r][c] = max(matrix[r-1][c] if r else -20,
                               matrix[r][c-1] if c else -20)+rng.randint(0,5)
    return [matrix,rng.randint(1,n*n)]


RECTANGLE = '''\
def max_bounded_rectangle(matrix, k):
    from bisect import bisect_left
    rows, cols = len(matrix),len(matrix[0])
    transpose = rows > cols
    narrow, wide = min(rows,cols),max(rows,cols)
    best = None
    for top in range(narrow):
        sums = [0]*wide
        for bottom in range(top,narrow):
            prefixes = [0]
            for c in range(wide):
                sums[c] += matrix[c][bottom] if transpose else matrix[bottom][c]
                prefixes.append(prefixes[-1]+sums[c])
            coordinates = sorted(set(prefixes))
            size = len(coordinates)
            ranks = {value:i+1 for i,value in enumerate(coordinates)}
            counts = [0]*(size+1)
            seen = 0
            step = 1 << (size.bit_length()-1)
            for current in prefixes:
                index = bisect_left(coordinates,current-k)
                less = 0
                while index:
                    less += counts[index]
                    index -= index & -index
                if less < seen:
                    # Select the (less+1)-th previously inserted prefix.
                    rank, index, bit = less+1,0,step
                    while bit:
                        nxt = index+bit
                        if nxt <= size and counts[nxt] < rank:
                            rank -= counts[nxt]
                            index = nxt
                        bit >>= 1
                    candidate = current-coordinates[index]
                    best = candidate if best is None else max(best,candidate)
                    if best == k:
                        return best
                index = ranks[current]
                while index <= size:
                    counts[index] += 1
                    index += index & -index
                seen += 1
    return best
'''
LEAVES = '''\
def leaf_removal_rounds(root):
    rounds = []
    def height(node):
        if node is None:
            return -1
        level = 1+max(height(node.left),height(node.right))
        if level == len(rounds):
            rounds.append([])
        rounds[level].append(node.val)
        return level
    height(root)
    return rounds
'''
SQUARE = '''\
def is_perfect_square(num):
    left,right = 1,num
    while left <= right:
        middle = (left+right)//2
        value = middle*middle
        if value == num:
            return True
        if value < num:
            left = middle+1
        else:
            right = middle-1
    return False
'''
ADDITION = '''\
def sum_without_arithmetic(a, b):
    mask = 0xffffffff
    a,b = a & mask,b & mask
    while b:
        a,b = a ^ b,((a & b) << 1) & mask
    return a if a < 0x80000000 else ~(a ^ mask)
'''
POWER = '''\
def super_pow(a, b):
    result = 1
    for digit in b:
        result = pow(result,10,1337)*pow(a,digit,1337) % 1337
    return result
'''
GUESS = '''\
def minimum_guess_budget(n):
    cost = [[0]*(n+2) for _ in range(n+2)]
    for width in range(2,n+1):
        for low in range(1,n-width+2):
            high = low+width-1
            cost[low][high] = min(guess+max(cost[low][guess-1],cost[guess+1][high])
                                  for guess in range(low,high+1))
    return cost[1][n]
'''
WIGGLE = '''\
def longest_wiggle_subsequence(nums):
    up = down = 1
    for previous,current in zip(nums,nums[1:]):
        if current > previous:
            up = down+1
        elif current < previous:
            down = up+1
    return max(up,down)
'''
ORDERED_SUM = '''\
def count_ordered_sums(nums, target):
    ways = [1]+[0]*target
    for total in range(1,target+1):
        for value in nums:
            if value <= total:
                ways[total] += ways[total-value]
    return ways[target]
'''
KTH_MATRIX = '''\
def kth_smallest_matrix(matrix, k):
    n = len(matrix)
    low,high = matrix[0][0],matrix[-1][-1]
    while low < high:
        middle = (low+high)//2
        row,col,count = n-1,0,0
        while row >= 0 and col < n:
            if matrix[row][col] <= middle:
                count += row+1
                col += 1
            else:
                row -= 1
        if count >= k:
            high = middle
        else:
            low = middle+1
    return low
'''

BATCH = {
    363: entry('max_bounded_rectangle',[('matrix','list[list[int]]'),('k','int')],'int',
        ['matrices','binary-search','prefix-sums','fenwick-tree'],
        ['The matrix has 1 to 100 rows and columns; -100 <= each value <= 100; -100000 <= k <= 100000.',
         'Return the largest sum <= k over nonempty axis-aligned contiguous rectangles. At least one feasible rectangle is guaranteed.'],
        [([[[1,0,1],[0,-2,3]],2],'Rows 0..1 and columns 1..2 contain [[0,1],[-2,3]], summing to 2. No permitted answer can exceed the bound 2.'),
         ([[[2,2,-1]],3],'All three cells sum to 3. A sliding window for positive values would miss how the negative cell makes the larger rectangle feasible.')],
        [[matrix,k] for matrix,k in (([[1]],1),([[-1]],-1),([[0]],0),([[5]],6),
            ([[-5,-2]],-3),([[2,-1,2]],2),([[3,-4,5]],4),([[2],[2],[-1]],3),
            ([[1,2],[3,4]],8),([[-3,-4],[-5,-6]],-7),([[0,0],[0,0]],1),
            ([[2,-3],[4,-1]],0),([[2,-2,2],[-2,2,-2]],-1),([[100,-100],[100,-100]],-100))],RECTANGLE,
        [RECTANGLE.replace('best = None','best = 0'),
         'def max_bounded_rectangle(matrix, k):\n    return max((sum(row[left:right]) for row in matrix for left in range(len(row)) for right in range(left+1,len(row)+1) if sum(row[left:right]) <= k),default=0)'],
        ['Permits an empty zero-sum result even when every feasible rectangle has negative sum.',
         'Only considers rectangles one row tall.'],rectangle_oracle,random_rectangle,
        ['Fixing two boundaries compresses the rectangle problem into a bounded subarray-sum problem.',
         'For current prefix p, find the smallest earlier prefix >= p-k. Use ordered counts of compressed prefix values.',
         'Enumerate bands along the shorter dimension. Maintain a Fenwick tree of earlier prefix counts and select the first eligible prefix rank.',
         'Earlier prefix q gives sum p-q. Choosing the least q >= p-k maximizes the feasible sum, and every rectangle appears in one band.'],
        'Enumerate top/bottom boundaries along the shorter matrix dimension without copying a transpose. Compress each band into column sums and prefix sums. Coordinate compression plus a Fenwick count tree supplies predecessor-count and rank-selection operations, finding the smallest earlier prefix at least p-k in logarithmic time. Query before inserting p so only nonempty subarrays count. The oracle independently sums every cell of every small rectangle.',
        'O(min(rows,cols)^2 * max(rows,cols) * log max(rows,cols))','O(max(rows,cols))',difficulty=8,
        stress=[([[[1]*100 for _ in range(100)],9999],9900),
                ([[[-100]*100 for _ in range(50)],-49999],-50000)]),
    366: entry('leaf_removal_rounds',[('root','TreeNode | None')],'list[list[int]]',
        ['trees','recursion','depth-first-search','dynamic-programming'],
        ['The tree has 1 to 100 nodes; -100 <= each node value <= 100.',
         'Return one list of values per simultaneous leaf-removal round, earliest round first. Values within a round may be in any order, but repeated values from different nodes must be preserved.',
         'You need not physically modify the tree; report the rounds as if all current leaves were removed together.'],
        [([[1,2,3,4,5]],'First remove leaves 4,5,3 in any order, then 2, then 1. [[3,5,4],[2],[1]] is equally valid, but swapping the rounds is not.'),
         ([[1]],'The root is already a leaf, so its single value is collected in the first and only round: [[1]].')],
        [[values] for values in ([0],[2,1],[2,None,1],[1,2,3],[1,1,1],[0,-1,1],
            [1,2,None,3],[1,None,2,None,3],[1,2,3,4,None,None,5],[1,2,3,4,5,6,7],
            [5,5,5,5,None,5],[1,2,3,None,4],[1,2,3,4,None,None,5,6],[-100,100,0])],LEAVES,
        [LEAVES.replace('level = 1+max','level = 1+min'),
         LEAVES.replace('    return rounds','    return rounds[::-1]')],
        ['Assigns removal by the nearer child instead of waiting for the last remaining child.',
         'Reverses chronological removal rounds.'],leaves_oracle,random_leaves,
        ['A node becomes a leaf only after both of its child subtrees have disappeared.',
         'Its removal round is one plus the maximum child removal round; missing children have round -1.',
         'Recursively compute child heights, append node.val to rounds[1+max(left,right)], and return that height.',
         'Postorder groups each node by its height above the deepest descendant leaf. Equal values remain separate occurrences.'],
        'The first round contains leaves, whose height is zero. An internal node disappears one round after its last child, giving 1+max(child heights). One postorder traversal assigns each node to exactly one chronological group. The comparator ignores order only inside each group, never across rounds, and preserves duplicate counts. The independent oracle repeatedly removes actual leaf paths from a JSON-level tree map.',
        'O(n)','O(n) output and O(height) recursion',difficulty=5,
        stress=[([[value for i in range(100) for value in ((i,None) if i<99 else (i,))]],[[i] for i in reversed(range(100))])]),
    367: entry('is_perfect_square',[('num','int')],'bool',['binary-search','math'],
        ['1 <= num <= 2147483647.', 'Determine whether num equals an integer multiplied by itself. Do not use a built-in square-root function.'],
        [([16],'4*4 is exactly 16, so the answer is true.'),([14],'3*3=9 and 4*4=16 bracket 14; neither equals it, so the answer is false.')],
        [[n] for n in (1,2,3,4,5,8,9,10,15,17,25,26,2147395600,2147395599,2147483647)],SQUARE,
        [SQUARE.replace('left,right = 1,num','left,right = 1,num//2'),
         'def is_perfect_square(num):\n    return num % 4 in (0,1)'],
        ['Excludes the only valid candidate when num is 1.','Mistakes a necessary modulo-four condition for a sufficient test.'],
        square_oracle,random_square,
        ['Squaring positive integers is strictly increasing.', 'Binary-search possible integer roots and compare squared candidates directly.',
         'If mid*mid < num move left upward; if greater move right downward; equality succeeds.',
         'The search discards only roots whose squares lie entirely on the wrong side; exhaustion means no integer root exists.'],
        'Search integers from 1 through num, comparing middle*middle to num. This avoids rounding and forbidden square-root functions. Unlike floor-square-root output, this contract returns a Boolean indicating exact equality. The trusted offline oracle uses integer square root, independently of the reference binary search.',
        'O(log num)','O(1)',difficulty=3),
    371: entry('sum_without_arithmetic',[('a','int'),('b','int')],'int',['bit-manipulation','math'],
        ['-1000 <= a,b <= 1000. Return their signed integer sum.',
         'Solve using bit operations, without the + or - operators. Python negative integers require an explicitly bounded two\u2019s-complement representation during carry propagation.'],
        [([1,2],'The binary digits 01 and 10 have no carry; their sum is 11, or 3.'),
         ([-2,3],'The signed result is 1. A correct bitwise implementation must handle negative inputs, not return an unsigned 32-bit encoding.')],
        [[a,b] for a,b in ((0,0),(0,5),(5,0),(1,1),(3,3),(7,1),(-1,1),(-1,-1),
            (-1000,1000),(-1000,-1000),(1000,1000),(-5,2),(2,-5),(511,1),(999,-1000))],ADDITION,
        ['def sum_without_arithmetic(a,b):\n    return a ^ b',
         ADDITION.replace('return a if a < 0x80000000 else ~(a ^ mask)','return a')],
        ['Uses XOR without propagating carry bits.','Leaves negative sums encoded as positive unsigned values.'],
        addition_oracle,random_addition,
        ['XOR combines bits without carrying; AND identifies carry-producing positions.',
         'Shift carry bits left and repeat, masking to 32 bits so negative Python values terminate.',
         'While carry: a,b = a^b, ((a&b)<<1)&mask. Decode a as signed after the loop.',
         'Each iteration moves unresolved carry bits left. After at most 32 shifts, the masked representation is the exact signed sum.'],
        'Use a 32-bit representation, sufficient for the input and output range. XOR computes the carry-free sum, and shifted AND computes carries. Mask carries to prevent Python sign extension from propagating indefinitely. Decode a negative result using complement operations, with no addition or subtraction in the reference. The oracle uses ordinary integer addition; separate AST regression checks audit the reference restriction.',
        'O(32)','O(1)',difficulty=5),
    372: entry('super_pow',[('a','int'),('b','list[int]')],'int',['math','modular-arithmetic'],
        ['1 <= a <= 2147483647; b contains 1 to 2000 decimal digits representing a positive exponent with no leading zero.',
         'Return a raised to that exponent modulo 1337. Process decimal positions correctly, including internal or trailing zero digits.'],
        [([2,[3]],'The exponent is 3, so 2^3 mod 1337 = 8.'),
         ([2,[1,0]],'Digits [1,0] represent ten, not one or a digit sum. 2^10 = 1024, already below 1337.')],
        [[a,digits] for a,digits in ((1,[1]),(1,[9,9]),(2,[1]),(2,[2]),(2,[1,1]),(2,[2,0]),
            (3,[1,0]),(7,[1,1,4,0]),(191,[1,1,4,0]),(1337,[1]),(1337,[1,1,4,0]),
            (1338,[1,2,3]),(2147483647,[9]),(2,[1,0,1]),(10,[1,2]))],POWER,
        [POWER.replace('for digit in b:','for digit in b[::-1]:'),
         'def super_pow(a,b):\n    exponent=int("".join(map(str,b))) % 1140\n    return pow(a,exponent,1337)'],
        ['Reads exponent digits in reverse positional order.','Applies Euler exponent reduction even when the base shares a factor with 1337.'],
        power_oracle,random_power,
        ['Appending decimal digit d turns exponent e into 10*e+d.',
         'Update the running modular power using its tenth power and a^d.',
         'Start result=1; for digit d, set result=pow(result,10,1337)*pow(a,d,1337)%1337.',
         'The exponent-prefix invariant follows from a^(10e+d)=(a^e)^10*a^d. It works without any coprimality assumption.'],
        'Maintain the power for the exponent prefix. Each new digit raises the previous result to ten and multiplies by the base to that digit, always modulo 1337. The exponents in these modular-power operations are bounded by ten. Do not reduce the exponent modulo Euler\u2019s totient unless coprimality requirements are satisfied. The oracle constructs the trusted integer exponent and uses an independent full modular exponentiation.',
        'O(len(b))','O(1) auxiliary',difficulty=5,
        stress=[([1337,[9]*2000],0),([1338,[9]*2000],1),([2,[1]+[0]*1999],pow(2,10**1999,1337))]),
    375: entry('minimum_guess_budget',[('n','int')],'int',['dynamic-programming','recursion','game-theory'],
        ['1 <= n <= 200. The hidden integer is in [1,n]. A wrong guess x costs x; a correct guess costs nothing.',
         'Return the minimum budget that guarantees success in the worst case. This is an ordinary function problem; no interactive guess API is used.'],
        [([10],'A strategy starting at 7 needs at most 16: the upper branch may pay 7 then 9, while the lower branch can be solved within 8 more. No strategy guarantees a smaller budget.'),
         ([1],'There is only one possible number. Guess it correctly and pay nothing, so the answer is 0.')],
        [[n] for n in (2,3,4,5,6,7,8)],GUESS,
        [GUESS.replace('max(cost[low][guess-1],cost[guess+1][high])','min(cost[low][guess-1],cost[guess+1][high])'),
         'def minimum_guess_budget(n):\n    def cost(low,high):\n        if low>=high: return 0\n        mid=(low+high)//2\n        return mid+max(cost(low,mid-1),cost(mid+1,high))\n    return cost(1,n)'],
        ['Optimizes for the cheaper branch instead of guaranteeing the worst case.','Assumes midpoint guessing minimizes monetary cost as well as comparison count.'],
        guessing_oracle,random_guess,
        ['The cost of a strategy is its worst hidden-number outcome, not its average number of guesses.',
         'For every interval, try each first guess and combine its cost with the worse remaining interval.',
         'dp[l][r]=min(g+max(dp[l][g-1],dp[g+1][r])) over g in [l,r]. Singleton intervals cost zero.',
         'Fill shorter intervals before longer ones. Minimizing the worst branch yields a guaranteed budget.'],
        'A wrong first guess splits the remaining candidates into lower and upper intervals. The adversary may choose the more expensive branch, so use their maximum; then minimize over the first guess. A singleton requires no paid mistake. Bottom-up interval DP evaluates all choices. The independent small-input oracle enumerates every binary decision tree and simulates every hidden number. Larger deterministic cases are cross-checked separately by a top-down minimax implementation.',
        'O(n^3)','O(n^2)',difficulty=6,
        stress=[([9],14),([11],18),([12],21),([13],24),([14],27),([15],30),([20],49),([200],952)]),
    376: entry('longest_wiggle_subsequence',[('nums','list[int]')],'int',['arrays','greedy','dynamic-programming'],
        ['1 <= len(nums) <= 1000; 0 <= nums[i] <= 1000.',
         'Delete any elements without changing the order of those retained. Successive differences must alternate strictly in sign; zero differences are invalid. The first difference may have either sign.'],
        [([[1,7,4,9,2,5]],'All six values alternate up, down, up, down, up, so the entire sequence is a valid wiggle subsequence.'),
         ([[1,2,3,4]],'A strictly increasing run contributes only two values, such as [1,4]. The answer is 2, not 4.')],
        [[values] for values in ([0],[1,1],[1,2],[2,1],[1,1,1],[1,2,1],[3,2,1],
            [1,2,2,1],[1,7,4,5,5],[1,2,3,2,1,2],[0,1000,0,1000],[2,2,3,3,2,2],
            [1,3,2,4,3],[4,1,3,2,5],[0,0,1,0,0])],WIGGLE,
        ['def longest_wiggle_subsequence(nums):\n    return 1+sum(a!=b for a,b in zip(nums,nums[1:]))',
         WIGGLE.replace('return max(up,down)','return up')],
        ['Counts every nonzero difference, even successive differences with the same sign.','Only returns sequences ending in a positive difference.'],
        wiggle_oracle,random_wiggle,
        ['Within a monotonic run, keeping its extreme endpoint is at least as useful as keeping an interior value.',
         'Track the best lengths ending with an upward versus a downward difference.',
         'On a rise set up=down+1; on a fall set down=up+1; ignore equal adjacent values.',
         'Each sign change extends the opposite state, while monotonic runs only replace an endpoint. Return the larger state.'],
        'Maintain up/down lengths initialized to one. A rise can extend a downward-ending subsequence, and a fall can extend an upward-ending one. Equal values do not extend either. Replacing endpoints along a monotonic run preserves or improves future extension opportunities, yielding linear time and constant space. Unlike Wiggle Sort, elements cannot be reordered. The oracle exhausts all index-subset subsequences.',
        'O(n)','O(1)',difficulty=5,stress=[([[0,1000]*500],1000),([list(range(1000))],2)]),
    377: entry('count_ordered_sums',[('nums','list[int]'),('target','int')],'int',
        ['arrays','dynamic-programming','recursion'],
        ['1 <= len(nums) <= 200; all values are distinct positive integers <= 1000; 1 <= target <= 1000.',
         'Values may be reused. ORDER MATTERS: [1,2] and [2,1] count separately. The final count is guaranteed to fit a signed 32-bit integer.'],
        [([[1,2,3],4],'The seven sequences are [1,1,1,1], [1,1,2], [1,2,1], [2,1,1], [1,3], [3,1], and [2,2].'),
         ([[9],3],'The only allowed value exceeds the target, so no sequence exists and the answer is 0.')],
        [[nums,target] for nums,target in (([1],1),([1],5),([2],1),([2],2),([2],5),
            ([2,3],5),([3,2],5),([1,2],3),([2,4],7),([2,4],8),([4,5,6],10),([9],9),
            ([1,10],10),([3,5],12))],ORDERED_SUM,
        ['def count_ordered_sums(nums,target):\n    ways=[1]+[0]*target\n    for value in nums:\n        for total in range(value,target+1):\n            ways[total]+=ways[total-value]\n    return ways[target]',
         'def count_ordered_sums(nums,target):\n    ways=[1]+[0]*target\n    for value in nums:\n        for total in range(target,value-1,-1):\n            ways[total]+=ways[total-value]\n    return ways[target]'],
        ['Counts unordered coin combinations by iterating values first.','Allows each input value only once and ignores sequence order.'],
        ordered_sum_oracle,random_ordered_sum,
        ['Separate sequences according to their last value.', 'For each total, sum the counts for total-value over every usable last value.',
         'Set ways[0]=1; loop totals upward, then choices; add ways[total-value] when value<=total.',
         'Each ordered sequence has one final value and one shorter prefix, so the recurrence counts it exactly once.'],
        'Count by final choice, not by unordered sets of chosen values. Initializing the empty prefix count to one lets each exact first value contribute a sequence. Iterating totals before choices permits all orderings; looping choices first would instead count coin combinations. Positive values make the recurrence acyclic. The oracle explicitly enumerates all small sequences without memoization. This generalizes the original fixed one-or-two-step exercise to an input-dependent choice set.',
        'O(target * len(nums))','O(target)',difficulty=5,
        stress=[([[1],1000],1),([[1,2],45],1836311903),([list(range(801,1001)),1000],1)]),
    378: entry('kth_smallest_matrix',[('matrix','list[list[int]]'),('k','int')],'int',
        ['matrices','binary-search'],
        ['The square matrix has 1 to 300 rows. Every row and column is nondecreasing; entries lie between -1000000000 and 1000000000.',
         '1 <= k <= n*n. Count duplicate occurrences separately: this is the kth sorted value, not the kth distinct value.',
         'Aim for less than O(n^2) auxiliary memory; the reference uses constant workspace.'],
        [([[[1,5,9],[10,11,13],[12,13,15]],8],'Sorted values are [1,5,9,10,11,12,13,13,15]. Both occurrences of 13 count, and position 8 is 13.'),
         ([[[-5]],1],'The only cell is the first smallest value, so return -5.')],
        [[matrix,k] for matrix,k in (([[0]],1),([[1,2],[3,4]],1),([[1,2],[3,4]],4),
            ([[1,3],[2,4]],2),([[1,1],[1,2]],3),([[1,1],[1,2]],4),
            ([[-4,-3],[-2,-1]],2),([[0,0],[0,0]],4),([[-1000000000,0],[0,1000000000]],3),
            ([[1,2,3],[2,3,4],[3,4,5]],5),([[1,2],[100,101]],3),([[1,100],[2,101]],3),
            ([[2,2],[2,2]],1),([[1,5],[3,6]],3))],KTH_MATRIX,
        ['def kth_smallest_matrix(matrix,k):\n    n=len(matrix)\n    return matrix[(k-1)//n][(k-1)%n]',
         'def kth_smallest_matrix(matrix,k):\n    values=sorted({x for row in matrix for x in row})\n    return values[min(k-1,len(values)-1)]'],
        ['Assumes row-major flattening is globally sorted.','Discards repeated values before selecting rank.'],
        kth_matrix_oracle,random_kth_matrix,
        ['The number of cells <= a candidate value increases monotonically with that value.',
         'Binary-search the value range, counting eligible cells by walking a staircase from the bottom-left.',
         'If matrix[row][col]<=mid, add row+1 and move right; otherwise move up. Keep the smallest mid with count>=k.',
         'Every staircase step removes a row or column, so each count costs O(n), and the first feasible value is the kth occurrence.'],
        'Binary-search between the minimum and maximum cell values. A bottom-left staircase counts values <= mid in O(n) without flattening or sorting the matrix. If the count is at least k, the answer is no larger than mid; otherwise it is larger. Duplicate cells contribute individually. The oracle flattens and sorts independently; generated matrices are row/column sorted but need not be row-major sorted.',
        'O(n log(value_range + 1))','O(1)',difficulty=6,
        stress=[([[[r+c for c in range(300)] for r in range(300)],45000],299),
                ([[[-1000000000]*300 for _ in range(300)],90000],-1000000000)])
}

BATCH[363]['prerequisites'] = ['matrices','binary-search','prefix-sums']
BATCH[366]['params'] = [('root','TreeNode | None','treenode')]
BATCH[366]['comparator'] = 'unordered_rows'
BATCH[377]['statement'] = ('Given distinct positive integers nums and a positive target, count all ordered sequences '
    'of values from nums whose sum is target. Values may be reused. Two sequences with the same values in a '
    'different order count separately. The answer fits a signed 32-bit integer.')
