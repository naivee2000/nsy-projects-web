"""Interval DP, vertical trees, suffix counts, greedy subsequences and grid paths."""
from collections import deque
from functools import lru_cache
from heapq import heappop, heappush
from itertools import combinations

from .import_batch_002 import positions, random_tree
from .import_batch_003 import entry
from .import_batch_024 import right_chain


def balloons_oracle(args):
    @lru_cache(None)
    def burst(values):
        if not values:
            return 0
        return max((values[i - 1] if i else 1) * value
                   * (values[i + 1] if i + 1 < len(values) else 1)
                   + burst(values[:i] + values[i + 1:])
                   for i, value in enumerate(values))
    return burst(tuple(args[0]))


def super_ugly_oracle(args):
    n, primes = args
    heap, seen = [1], {1}
    for _ in range(n):
        value = heappop(heap)
        for prime in primes:
            candidate = value * prime
            if candidate not in seen:
                seen.add(candidate)
                heappush(heap, candidate)
    return value


def vertical_oracle(args):
    cells = [(sum(1 if side else -1 for side in path), len(path), path, value)
             for path, value in positions(args[0]).items()]
    result, previous = [], None
    for column, _, _, value in sorted(cells):
        if column != previous:
            result.append([])
            previous = column
        result[-1].append(value)
    return result


def smaller_oracle(args):
    values = args[0]
    return [sum(other < value for other in values[i + 1:])
            for i, value in enumerate(values)]


def letters_oracle(args):
    text = args[0]
    required = set(text)
    return min(candidate for indices in combinations(range(len(text)), len(required))
               if set(candidate := "".join(text[i] for i in indices)) == required)


def buildings_oracle(args):
    """Start a separate search at every candidate house, stopping at buildings."""
    grid = args[0]
    rows, columns = len(grid), len(grid[0])
    buildings = sum(row.count(1) for row in grid)
    best = float('inf')
    for r in range(rows):
        for c in range(columns):
            if grid[r][c] != 0:
                continue
            queue, seen, reached, total = deque([(r, c, 0)]), {(r, c)}, 0, 0
            while queue:
                row, column, distance = queue.popleft()
                for nr, nc in ((row-1, column), (row+1, column),
                               (row, column-1), (row, column+1)):
                    if not (0 <= nr < rows and 0 <= nc < columns) or (nr, nc) in seen:
                        continue
                    seen.add((nr, nc))
                    if grid[nr][nc] == 1:
                        reached += 1
                        total += distance + 1
                    elif grid[nr][nc] == 0:
                        queue.append((nr, nc, distance+1))
            if reached == buildings:
                best = min(best, total)
    return -1 if best == float('inf') else best


def random_balloons(rng):
    return [[rng.randint(0, 7) for _ in range(rng.randint(1, 7))]]


def random_super_ugly(rng):
    # Including 2 and keeping n small also guarantees the 32-bit result bound.
    return [rng.randint(1, 25), [2] + sorted(rng.sample([3, 5, 7, 11, 13], rng.randint(0, 5)))]


def random_vertical(rng):
    return [random_tree(rng)]


def random_smaller(rng):
    return [[rng.randint(-9, 9) for _ in range(rng.randint(1, 30))]]


def random_letters(rng):
    return ["".join(rng.choice("abcde") for _ in range(rng.randint(1, 11)))]


def random_buildings(rng):
    rows, columns = rng.randint(1, 4), rng.randint(1, 4)
    grid = [[rng.choices([0, 1, 2], [6, 2, 2])[0] for _ in range(columns)] for _ in range(rows)]
    grid[rng.randrange(rows)][rng.randrange(columns)] = 1
    return [grid]


BALLOONS = '''\
def max_burst_coins(nums):
    values = [1] + nums + [1]
    size = len(values)
    dp = [[0] * size for _ in range(size)]
    for width in range(2, size):
        for left in range(size - width):
            right = left + width
            best = 0
            boundary = values[left] * values[right]
            for last in range(left + 1, right):
                best = max(best, dp[left][last] + dp[last][right] + boundary * values[last])
            dp[left][right] = best
    return dp[0][-1]
'''

SUPER_UGLY = '''\
def nth_super_ugly_number(n, primes):
    values = [1]
    indices = [0] * len(primes)
    candidates = list(primes)
    for _ in range(1, n):
        smallest = min(candidates)
        values.append(smallest)
        for i, prime in enumerate(primes):
            if candidates[i] == smallest:
                indices[i] += 1
                candidates[i] = prime * values[indices[i]]
    return values[-1]
'''

VERTICAL = '''\
def vertical_order(root):
    from collections import deque
    if root is None:
        return []
    columns = {}
    queue = deque([(root, 0)])
    low = high = 0
    while queue:
        node, column = queue.popleft()
        columns.setdefault(column, []).append(node.val)
        low, high = min(low, column), max(high, column)
        if node.left:
            queue.append((node.left, column - 1))
        if node.right:
            queue.append((node.right, column + 1))
    return [columns[column] for column in range(low, high + 1)]
'''

SMALLER = '''\
def count_smaller_after_self(nums):
    ranks = {value: i + 1 for i, value in enumerate(sorted(set(nums)))}
    tree = [0] * (len(ranks) + 1)
    answer = []
    for value in reversed(nums):
        rank = ranks[value]
        index, count = rank - 1, 0
        while index:
            count += tree[index]
            index -= index & -index
        answer.append(count)
        index = rank
        while index < len(tree):
            tree[index] += 1
            index += index & -index
    return answer[::-1]
'''

LETTERS = '''\
def remove_duplicate_letters(s):
    last = {letter: index for index, letter in enumerate(s)}
    stack, used = [], set()
    for index, letter in enumerate(s):
        if letter in used:
            continue
        while stack and stack[-1] > letter and last[stack[-1]] > index:
            used.remove(stack.pop())
        stack.append(letter)
        used.add(letter)
    return "".join(stack)
'''

BUILDINGS = '''\
def shortest_distance_to_buildings(grid):
    from collections import deque
    rows, columns = len(grid), len(grid[0])
    totals = [[0] * columns for _ in range(rows)]
    reached = [[0] * columns for _ in range(rows)]
    buildings = 0
    for r in range(rows):
        for c in range(columns):
            if grid[r][c] != 1:
                continue
            buildings += 1
            queue = deque([(r, c, 0)])
            seen = {(r, c)}
            while queue:
                row, column, distance = queue.popleft()
                for nr, nc in ((row-1, column), (row+1, column),
                               (row, column-1), (row, column+1)):
                    if (0 <= nr < rows and 0 <= nc < columns
                            and grid[nr][nc] == 0 and (nr, nc) not in seen):
                        seen.add((nr, nc))
                        totals[nr][nc] += distance + 1
                        reached[nr][nc] += 1
                        queue.append((nr, nc, distance+1))
    return min((totals[r][c] for r in range(rows) for c in range(columns)
                if grid[r][c] == 0 and reached[r][c] == buildings), default=-1)
'''

GREEDY_BALLOONS = '''\
def max_burst_coins(nums):
    remaining = [1] + nums + [1]
    total = 0
    while len(remaining) > 2:
        i = max(range(1, len(remaining)-1),
                key=lambda j: remaining[j-1] * remaining[j] * remaining[j+1])
        total += remaining[i-1] * remaining[i] * remaining[i+1]
        remaining.pop(i)
    return total
'''

STATIC_BALLOONS = '''\
def max_burst_coins(nums):
    values = [1] + nums + [1]
    return sum(values[i-1] * values[i] * values[i+1] for i in range(1, len(values)-1))
'''

ONE_POINTER_UGLY = SUPER_UGLY.replace(
    '                candidates[i] = prime * values[indices[i]]',
    '                candidates[i] = prime * values[indices[i]]\n                break')
OMIT_ONE_UGLY = SUPER_UGLY.replace('range(1, n)', 'range(n)')

DFS_VERTICAL = '''\
def vertical_order(root):
    columns = {}
    def visit(node, column):
        if node:
            columns.setdefault(column, []).append(node.val)
            visit(node.left, column-1)
            visit(node.right, column+1)
    visit(root, 0)
    return [columns[column] for column in sorted(columns)]
'''
VALUE_SORT_VERTICAL = VERTICAL.replace('columns[column] for column', 'sorted(columns[column]) for column')
EQUAL_SMALLER = SMALLER.replace('rank - 1, 0', 'rank, 0')
LEFT_SMALLER = SMALLER.replace('reversed(nums)', 'nums').replace('return answer[::-1]', 'return answer')
SORT_LETTERS = '''\
def remove_duplicate_letters(s):
    return "".join(sorted(set(s)))
'''
FIRST_LETTERS = '''\
def remove_duplicate_letters(s):
    return "".join(dict.fromkeys(s))
'''
PASS_BUILDINGS = BUILDINGS.replace('and grid[nr][nc] == 0 and', 'and grid[nr][nc] != 2 and')
MANHATTAN_BUILDINGS = '''\
def shortest_distance_to_buildings(grid):
    buildings = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value == 1]
    return min((sum(abs(r-br) + abs(c-bc) for br, bc in buildings)
                for r, row in enumerate(grid) for c, value in enumerate(row) if value == 0), default=-1)
'''

PRIMES_100 = [number for number in range(2, 542)
              if all(number % divisor for divisor in range(2, int(number**.5)+1))]
large_buildings = [[0] * 50 for _ in range(50)]
for r, c in ((0, 0), (0, 49), (49, 0), (49, 49)):
    large_buildings[r][c] = 1

BATCH = {
    312: entry(
        'max_burst_coins', [('nums', 'list[int]')], 'int',
        ['dynamic-programming', 'intervals', 'recursion'],
        ['1 <= len(nums) <= 300; 0 <= nums[i] <= 100.',
         'Burst every balloon. Its neighbors are the nearest balloons STILL PRESENT; a missing neighbor has value 1. Return the maximum total coins.'],
        [([[3,1,5,8]], 'Burst values 1, 5, 3, then 8: earn 15 + 120 + 24 + 8 = 167. Neighbors change after each burst.'),
         ([[1,5]], 'Burst 1 first for 5 coins, then the remaining 5 for another 5: total 10.')],
        [[values] for values in ([0], [1], [100], [0,0], [0,5], [5,0], [2,3], [3,2],
                                 [1,1,1], [2,1,2], [9,1,9], [0,5,0,2], [2,4,3,5], [1,0,1,0,1])],
        BALLOONS, [GREEDY_BALLOONS, STATIC_BALLOONS],
        ['Maximizing the immediate reward can destroy better future neighbors.',
         'Uses original neighbors for every burst, ignoring that removed balloons disappear.'],
        balloons_oracle, random_balloons,
        ['Think about which balloon is removed last within an interval.',
         'The last balloon has fixed outer neighbors, separating the remaining choices into two independent intervals.',
         'Pad with 1s. For each open interval (l,r), maximize dp[l][k]+dp[k][r]+a[l]*a[k]*a[r] over l<k<r.',
         'Fill intervals by increasing width. Empty intervals earn zero; the full padded interval gives the answer.'],
        'Choosing the first burst changes neighboring subproblems. Choosing the last burst k between fixed boundaries l and r avoids that dependency: every earlier burst lies entirely on one side. Maximize the sum of the two optimal open intervals and the last reward. Increasing interval width provides all dependencies. The oracle independently enumerates first-burst choices on shrinking tuples with memoization.',
        'O(n^3)', 'O(n^2)', difficulty=8,
        stress=[([ [100]*300 ], 298_010_100)]),
    313: entry(
        'nth_super_ugly_number', [('n', 'int'), ('primes', 'list[int]')], 'int',
        ['dynamic-programming', 'heaps', 'math'],
        ['1 <= n <= 100000. primes contains 1–100 distinct ascending primes from 2 through 1000.',
         'The nth result fits a signed 32-bit integer. The sequence starts with 1; each distinct integer is counted once.'],
        [([12,[2,7,13,19]], 'The sequence begins 1,2,4,7,8,13,14,16,19,26,28,32; the twelfth value is 32.'),
         ([1,[2,3,5]], '1 has no prime factors and is the first valid number for every allowed prime list.')],
        [[n, primes] for n, primes in ((2,[2]), (3,[3]), (4,[5]), (2,[997]), (5,[2,3]),
            (10,[2,3]), (15,[2,3,5]), (8,[3,5]), (7,[2,7]), (10,[7,11]),
            (20,[2,3,7]), (6,[13,17,19]), (3,[2,3,5,7,11]), (1,[997]))],
        SUPER_UGLY, [ONE_POINTER_UGLY, OMIT_ONE_UGLY],
        ['Advances only one prime when several generate the same number, counting duplicates.',
         'Advances the sequence n times after the initial 1, returning the next number.'],
        super_ugly_oracle, random_super_ugly,
        ['Every value after 1 is a listed prime multiplied by an earlier valid value.',
         'Merge one increasing product stream per prime and suppress equal candidates.',
         'Start values=[1]. Append the minimum p[i]*values[index[i]], then advance EVERY matching index.',
         'Keep k stream positions and k candidate values. After n-1 appends, return the last value.'],
        'For each prime p, maintain its smallest product with a generated value that has not been emitted. The minimum across these streams is the next valid integer: dividing any candidate by one allowed prime reaches a smaller generated value. Advance all streams tied at the minimum so values remain distinct. This generalizes the fixed 2/3/5 problem to an input prime set. The independent oracle explores products with a heap and a global visited set.',
        'O(nk)', 'O(n+k)', difficulty=6,
        # 284445 was independently obtained by factoring every integer from 1
        # upward until 100000 numbers contained only these 100 allowed primes.
        stress=[([31,[2]], 1 << 30), ([100000, PRIMES_100], 284445)]),
    314: entry(
        'vertical_order', [('root', 'TreeNode')], 'list[list[int]]',
        ['trees', 'breadth-first-search', 'recursion'],
        ['root has 0–100 nodes with values from -100 through 100.',
         'The root is in column 0, a left child in column-1, and a right child in column+1. Return columns left to right; within each column, order by depth, then left-to-right position, NOT node value.'],
        [([[3,9,20,None,None,15,7]], 'Columns -1,0,1,2 contain [9], [3,15], [20], [7]. Node 15 is below 3 in column 0.'),
         ([[1,2,3,4,10,9,11]], 'The middle column is [1,10,9]. Values 10 and 9 share a row and column, so their left-to-right order is retained.')],
        [[tree] for tree in ([], [0], [1,2], [1,None,2], [0,-1,1], [0,0,0],
            [3,2,1], [5,4,3,2,1,0,-1], [1,2,3,None,4,5],
            [1,2,3,4,10,9,11,None,5,None,None,None,None,None,None,None,6],
            [8,None,7,6,None,None,5], [2,1,None,None,3], [-1,-2,-3,None,-4,-5], [100,-100,0])],
        VERTICAL, [DFS_VERTICAL, VALUE_SORT_VERTICAL],
        ['Depth-first preorder can put a deeper left-branch node before a shallower right-branch node in the same column.',
         'Sorting column values loses the required row and left-to-right ordering.'],
        vertical_oracle, random_vertical,
        ['Each left edge changes column by -1 and each right edge by +1.',
         'A breadth-first queue processes nodes by row and left-to-right position, resolving ties without value sorting.',
         'Queue (root,0). Append each value to its column; enqueue its left child before its right child.',
         'Track the minimum and maximum column and emit those lists in increasing column order.'],
        'Breadth-first traversal preserves the exact within-column order: shallower nodes precede deeper ones, and children are enqueued left to right. Store each visited value under its horizontal column. Columns between the minimum and maximum all exist because edges change the column by one. Empty input returns an empty list. The independent oracle computes binary paths, then sorts by column, path length, and path rather than using the queue reference.',
        'O(n)', 'O(n)', difficulty=6,
        stress=[([right_chain(100)], [[i] for i in range(100)])]),
    315: entry(
        'count_smaller_after_self', [('nums', 'list[int]')], 'list[int]',
        ['binary-search', 'sorting', 'binary-indexed-tree', 'divide-and-conquer'],
        ['1 <= len(nums) <= 100000; -10000 <= nums[i] <= 10000.',
         'Return one count per ORIGINAL index: count elements strictly smaller to its right. Equal values do not count.'],
        [([[5,2,6,1]], '5 has 2 and 1 to its right; 2 has 1; 6 has 1; the final 1 has none. Return [2,1,1,0].'),
         ([[2,2,1]], 'Each 2 has only the final 1 as a smaller suffix value; the other 2 is equal. Return [1,1,0].')],
        [[values] for values in ([0], [-1], [-1,-1], [1,2], [2,1], [3,2,1], [1,2,3],
            [0,-1,0,-1], [-3,-2,-1], [4,1,4,1,0], [5,4,3,2,1], [1,1,1,1],
            [-10000,10000,0], [10000,0,-10000,0])],
        SMALLER, [EQUAL_SMALLER, LEFT_SMALLER],
        ['Queries through the current rank and incorrectly includes equal suffix values.',
         'Scans left to right and counts smaller values before each index rather than after it.'],
        smaller_oracle, random_smaller,
        ['Process from right to left so a frequency structure represents exactly the suffix.',
         'Compress sorted distinct values to ranks. A Fenwick tree supports counts below a rank and inserting one occurrence.',
         'For each reversed value query prefix(rank-1), then add one at rank. Reverse the collected counts.',
         'Fenwick queries remove the lowest set bit and updates add it. Strict rank-1 queries exclude duplicates.'],
        'Before processing position i, the frequency tree contains exactly values at positions greater than i. Coordinate compression preserves strict numeric order, including negative values. A prefix query ending before the current rank counts every smaller suffix occurrence, and inserting the current rank maintains the invariant. A merge-sort counting solution is also valid. The oracle directly compares each value with its full suffix.',
        'O(n log n)', 'O(n)', difficulty=8,
        stress=[([[1]*50000+[0]*50000], [50000]*50000+[0]*50000),
                ([list(range(10000,-10001,-1))], list(range(20000,-1,-1)))]),
    316: entry(
        'remove_duplicate_letters', [('s', 'str')], 'str',
        ['strings', 'stacks', 'greedy'],
        ['1 <= len(s) <= 10000; s contains lowercase English letters.',
         'Delete characters without rearranging the survivors. Include every distinct letter exactly once, and choose the lexicographically smallest valid subsequence.'],
        [(['bcabc'], 'Keep the later b and c after a, producing abc. All three letters appear once in their original relative order.'),
         (['cbacdcbc'], 'The smallest valid subsequence is acdb. Sorting to abcd is invalid because no d occurs after the final b.')],
        [[s] for s in ('a', 'aaaa', 'ab', 'ba', 'abc', 'cba', 'bbcaac', 'abacb',
                        'ecbacba', 'cdadabcc', 'bbbaa', 'abccba', 'bac', 'babab')],
        LETTERS, [SORT_LETTERS, FIRST_LETTERS],
        ['Sorts the distinct alphabet even when that ordering is not a subsequence.',
         'Keeps first occurrences, missing smaller choices made possible by later repeated letters.'],
        letters_oracle, random_letters,
        ['You can postpone a chosen letter only if it appears again later.',
         'Maintain a stack and each letter\'s last position. A smaller incoming letter may replace a larger stack top that can still be recovered.',
         'Skip used letters. While top > current and last[top] > index, pop and unmark top; then push and mark current.',
         'Every removal improves the earliest differing position while preserving the ability to include all letters. Each occurrence is pushed and popped at most once.'],
        'The stack holds the best feasible prefix. When a smaller unused letter arrives, remove larger trailing letters only if they occur later; otherwise removing them would lose a required letter. Greedy exchange at the first differing position justifies each pop. Skipping letters already retained prevents duplicates. The oracle enumerates all subsequences with exactly the required number of letters and selects the smallest containing the whole distinct alphabet.',
        'O(n)', 'O(a), a <= 26', difficulty=6,
        stress=[(['z'*9974+'abcdefghijklmnopqrstuvwxyz'], 'abcdefghijklmnopqrstuvwxyz'),
                (['zyxwvutsrqponmlkjihgfedcba'*384], 'abcdefghijklmnopqrstuvwxyz')]),
    317: entry(
        'shortest_distance_to_buildings', [('grid', 'list[list[int]]')], 'int',
        ['matrices', 'graphs', 'breadth-first-search', 'grid-traversal'],
        ['grid is a rectangular 1–50 by 1–50 matrix of 0 (empty), 1 (building), and 2 (obstacle), with at least one building.',
         'Choose an EMPTY cell. Sum its shortest four-direction distances to ALL buildings. Paths may traverse only empty cells; buildings are destinations, never corridors. Return -1 if no empty cell reaches every building.'],
        [([[[1,0,2,0,1],[0,0,0,0,0],[0,0,1,0,0]]], 'From empty cell (1,2), shortest paths to the three buildings have lengths 3,3,1. Their sum 7 is minimal.'),
         ([[[0,1,1]]], 'The only empty cell cannot reach the far building without passing through the nearer building, so return -1.')],
        [[grid] for grid in ([[1]], [[1,0]], [[1,2,0]], [[1,0,1]], [[1,1,0]],
            [[1,0],[0,1]], [[1,2],[2,0]], [[1,0,2],[2,0,1]],
            [[1,2,0],[0,0,0],[0,2,1]], [[1,0,0],[0,2,0],[0,0,1]],
            [[0,1,0],[0,1,0],[0,0,0]], [[1],[0],[0],[1]],
            [[1,2,1],[0,0,0]], [[1,0,1],[2,2,2],[0,0,0]])],
        BUILDINGS, [PASS_BUILDINGS, MANHATTAN_BUILDINGS],
        ['Allows paths through other buildings, incorrectly connecting otherwise isolated destinations.',
         'Uses Manhattan distances even when obstacles require detours or make destinations unreachable.'],
        buildings_oracle, random_buildings,
        ['Shortest paths in an unweighted four-direction grid can be found with breadth-first search.',
         'Run a search from each building and accumulate distance and reach-count at empty cells.',
         'For every building, queue it at distance 0; visit each reachable empty cell once, adding distance and one reach. Never enqueue another building.',
         'Among empty cells reached by every building, return the smallest accumulated distance. If there are none, return -1.'],
        'Run BFS from each building through empty cells only. Undirected paths have the same length in either direction, so accumulated building-to-cell distances are the desired house-to-building distances. The reach count prevents partial sums from disconnected buildings from winning. Reinitialize visited state for each building. The independent oracle reverses the search orientation: it tries every empty house and discovers buildings as terminal neighbors.',
        'O(bmn), b = building count', 'O(mn)', difficulty=8,
        stress=[([large_buildings], 196), ([[[1]*50 for _ in range(50)]], -1)]),
}

BATCH[314]['params'] = [('root', 'TreeNode', 'treenode')]
for problem_id in (312, 315, 317):
    BATCH[problem_id]['prerequisites'] = {
        312: ['dynamic-programming', 'recursion'],
        315: ['binary-search', 'sorting'],
        317: ['matrices', 'graphs'],
    }[problem_id]
