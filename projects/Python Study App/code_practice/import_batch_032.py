"""Distinct intersections, recursive locks, geometry, grids, lists and range updates."""
from collections import deque
from functools import lru_cache
from itertools import permutations
from math import gcd

from .import_batch_003 import entry


def intersection_oracle(args):
    left, right = args
    return [value for value in sorted(set(left)) if value in right]


def multiset_oracle(args):
    remaining = list(args[1])
    result = []
    for value in args[0]:
        if value in remaining:
            remaining.remove(value)
            result.append(value)
    return result


@lru_cache(None)
def pattern_counts():
    """Enumerate every ordered permutation, using geometric interior points.

    Unlike the memoized reference this neither shares prefix states nor uses
    a manually enumerated jump table. The finite board has 986409 permutations.
    """
    cells = tuple((r, c) for r in range(3) for c in range(3))
    inside = {}
    for first in cells:
        for second in cells:
            dr, dc = second[0]-first[0], second[1]-first[1]
            steps = gcd(abs(dr), abs(dc))
            inside[first, second] = {(first[0]+dr*i//steps, first[1]+dc*i//steps)
                                     for i in range(1, steps)}
    counts = [0]*10
    for length in range(1, 10):
        for path in permutations(cells, length):
            seen = {path[0]}
            for first, second in zip(path, path[1:]):
                if not inside[first, second] <= seen:
                    break
                seen.add(second)
            else:
                counts[length] += 1
    return tuple(counts)


def unlock_oracle(args):
    lower, upper = args
    return sum(pattern_counts()[lower:upper+1]) if lower <= upper else 0


def envelopes_oracle(args):
    envelopes = args[0]
    @lru_cache(None)
    def chain(index):
        w, h = envelopes[index]
        return 1+max((chain(j) for j, (x, y) in enumerate(envelopes) if x < w and y < h), default=0)
    return max(map(chain, range(len(envelopes))))


def reflection_oracle(args):
    points = {tuple(p) for p in args[0]}
    # Enumerate candidate axes from all x pairs, rather than assuming extrema.
    candidates = {a[0]+b[0] for a in points for b in points}
    return any({(axis-x, y) for x, y in points} == points for axis in candidates)


def transformed_oracle(args):
    nums, a, b, c = args
    return sorted(a*x*x+b*x+c for x in nums)


def bomb_oracle(args):
    grid = args[0]
    rows, cols = len(grid), len(grid[0])
    best = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != '0':
                continue
            killed = 0
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                y, x = r+dr, c+dc
                while 0 <= y < rows and 0 <= x < cols and grid[y][x] != 'W':
                    killed += grid[y][x] == 'E'
                    y, x = y+dr, x+dc
            best = max(best, killed)
    return best


def jug_oracle(args):
    x, y, target = args
    queue, seen = deque([(0, 0)]), {(0, 0)}
    while queue:
        a, b = queue.popleft()
        if a+b == target:
            return True
        pour_right, pour_left = min(a, y-b), min(b, x-a)
        for state in ((x, b), (a, y), (0, b), (a, 0),
                      (a-pour_right, b+pour_right), (a+pour_left, b-pour_left)):
            if state not in seen:
                seen.add(state)
                queue.append(state)
    return False


def linked_plus_oracle(args):
    return list(map(int, str(int(''.join(map(str, args[0])))+1)))


def range_oracle(args):
    length, updates = args
    return [sum(inc for start, end, inc in updates if start <= i <= end) for i in range(length)]


def random_arrays(rng):
    return [[rng.randrange(8) for _ in range(rng.randint(1, 14))] for _ in range(2)]


def random_unlock(rng):
    return [rng.randint(1, 9), rng.randint(1, 9)]


def random_envelopes(rng):
    return [[[rng.randint(1, 8), rng.randint(1, 8)] for _ in range(rng.randint(1, 12))]]


def random_reflection(rng):
    points = [[rng.randint(-5, 5), rng.randint(-3, 3)] for _ in range(rng.randint(1, 8))]
    if rng.random() < .5:
        axis = rng.randint(-3, 3)
        points += [[axis-x, y] for x, y in points]
        if rng.random() < .5:
            points.append(rng.choice(points)[:])
    return [points]


def random_transformed(rng):
    return [sorted(rng.randint(-100, 100) for _ in range(rng.randint(1, 20))),
            *[rng.randint(-100, 100) for _ in range(3)]]


def random_bomb(rng):
    rows, cols = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.choice('0EW') for _ in range(cols)] for _ in range(rows)]]


def random_jug(rng):
    return [rng.randint(1, 12), rng.randint(1, 12), rng.randint(1, 30)]


def random_linked_plus(rng):
    if rng.random() < .1:
        return [[0]]
    return [[rng.randint(1, 9)]+[rng.randrange(10) for _ in range(rng.randint(0, 25))]]


def random_range(rng):
    length = rng.randint(1, 15)
    updates = []
    for _ in range(rng.randint(0, 15)):
        start = rng.randrange(length)
        updates.append([start, rng.randrange(start, length), rng.randint(-1000, 1000)])
    return [length, updates]


INTERSECTION = '''\
def unique_intersection(nums1, nums2):
    return list(set(nums1) & set(nums2))
'''
MULTISET = '''\
def multiset_intersection(nums1, nums2):
    from collections import Counter
    available = Counter(nums1)
    result = []
    for value in nums2:
        if available[value] > 0:
            result.append(value)
            available[value] -= 1
    return result
'''
UNLOCK = '''\
def count_unlock_patterns(m, n):
    from functools import lru_cache
    if m > n:
        return 0
    jumps = {}
    for a, b, middle in ((1,3,2),(1,7,4),(1,9,5),(2,8,5),
                          (3,7,5),(3,9,6),(4,6,5),(7,9,8)):
        jumps[a,b] = jumps[b,a] = middle
    @lru_cache(None)
    def visit(last, mask):
        length = mask.bit_count()
        result = int(m <= length <= n)
        if length == n:
            return result
        for nxt in range(1,10):
            middle = jumps.get((last,nxt))
            if not mask & (1 << nxt) and (middle is None or mask & (1 << middle)):
                result += visit(nxt,mask | (1 << nxt))
        return result
    return sum(visit(start,1 << start) for start in range(1,10))
'''
ENVELOPES = '''\
def max_nested_envelopes(envelopes):
    from bisect import bisect_left
    tails = []
    for width, height in sorted(envelopes,key=lambda pair: (pair[0],-pair[1])):
        index = bisect_left(tails,height)
        if index == len(tails):
            tails.append(height)
        else:
            tails[index] = height
    return len(tails)
'''
REFLECTION = '''\
def has_vertical_reflection(points):
    present = {tuple(p) for p in points}
    axis_twice = min(x for x,y in present)+max(x for x,y in present)
    return all((axis_twice-x,y) in present for x,y in present)
'''
TRANSFORMED = '''\
def sort_transformed_array(nums, a, b, c):
    def transform(x):
        return a*x*x+b*x+c
    left, right = 0,len(nums)-1
    result = [0]*len(nums)
    for offset in range(len(nums)):
        low, high = transform(nums[left]),transform(nums[right])
        if a >= 0:
            if low > high:
                result[-1-offset] = low
                left += 1
            else:
                result[-1-offset] = high
                right -= 1
        else:
            if low < high:
                result[offset] = low
                left += 1
            else:
                result[offset] = high
                right -= 1
    return result
'''
BOMB = '''\
def max_bomb_enemies(grid):
    rows, cols = len(grid),len(grid[0])
    vertical = [0]*cols
    best = horizontal = 0
    for r in range(rows):
        for c in range(cols):
            if c == 0 or grid[r][c-1] == 'W':
                horizontal = 0
                x = c
                while x < cols and grid[r][x] != 'W':
                    horizontal += grid[r][x] == 'E'
                    x += 1
            if r == 0 or grid[r-1][c] == 'W':
                vertical[c] = 0
                y = r
                while y < rows and grid[y][c] != 'W':
                    vertical[c] += grid[y][c] == 'E'
                    y += 1
            if grid[r][c] == '0':
                best = max(best,horizontal+vertical[c])
    return best
'''
JUG = '''\
def can_measure_water(x, y, target):
    from math import gcd
    return target <= x+y and target % gcd(x,y) == 0
'''
LINKED_PLUS = '''\
def plus_one_linked_list(head):
    dummy = ListNode(0,head)
    last_non_nine = dummy
    current = head
    while current:
        if current.val != 9:
            last_non_nine = current
        current = current.next
    last_non_nine.val += 1
    current = last_non_nine.next
    while current:
        current.val = 0
        current = current.next
    return dummy if dummy.val else dummy.next
'''
RANGE = '''\
def apply_range_additions(length, updates):
    changes = [0]*(length+1)
    for start,end,increment in updates:
        changes[start] += increment
        changes[end+1] -= increment
    result = []
    running = 0
    for i in range(length):
        running += changes[i]
        result.append(running)
    return result
'''

ARRAY_CASES = [([0],[0]),([0],[1]),([1],[1,1]),([1,1],[1]),([2,2],[2,2,2]),
               ([1,2],[2,1]),([0,1000],[1000]),([3,4],[5,6]),([1,2,3],[3,2]),
               ([5,5,6],[6,6,5]),([7,8,7,9],[7,9,9]),([1000],[0,1000,1000]),
               ([1,2,1,2],[1,2,1]),([4,4,4],[4,4,4,4])]

BATCH = {
    349: entry('unique_intersection',[('nums1','list[int]'),('nums2','list[int]')],'list[int]',
        ['arrays','hash-maps'],
        ['1 <= len(nums1), len(nums2) <= 1000; 0 <= every element <= 1000.',
         'Return each shared value exactly once, in any order. Repeated input occurrences do not repeat the output.'],
        [([[1,2,2,1],[2,2]],'Only 2 occurs in both arrays. Return [2], not [2,2].'),
         ([[4,9,5],[9,4,9,8,4]],'The shared values are 4 and 9; either [4,9] or [9,4] is valid.')],
        [list(pair) for pair in ARRAY_CASES],INTERSECTION,
        ['def unique_intersection(nums1, nums2):\n    return list(set(nums1) | set(nums2))',
         'def unique_intersection(nums1, nums2):\n    return [x for x in nums1 if x in nums2]'],
        ['Computes union instead of intersection.','Preserves repeated left-side values instead of emitting unique values.'],
        intersection_oracle,random_arrays,
        ['Membership and frequency are different contracts.', 'Use sets for both inputs and retain only common values.',
         'Build A=set(nums1), B=set(nums2); return list(A & B).', 'Set intersection discards repeated occurrences and keeps exactly shared values.'],
        'Represent each input by its distinct values. Their intersection contains a value if and only if it occurs in both inputs. Any output order is allowed, but duplicate outputs are not. The independent oracle scans sorted distinct left values using membership in the original right list.',
        'O(n + m) expected','O(n + m)',stress=[([[7]*1000,[7]*1000],[7])]),
    350: entry('multiset_intersection',[('nums1','list[int]'),('nums2','list[int]')],'list[int]',
        ['arrays','hash-maps'],
        ['1 <= len(nums1), len(nums2) <= 1000; 0 <= every element <= 1000.',
         'Include each value min(count in nums1, count in nums2) times. Output order does not matter.'],
        [([[1,2,2,1],[2,2]],'There are two occurrences of 2 in each input, so both must appear: [2,2].'),
         ([[4,9,5],[9,4,9,8,4]],'Only one 4 and one 9 are available in the first input, so [4,9] is valid despite extra right-side copies.')],
        [list(pair) for pair in ARRAY_CASES],MULTISET,
        [INTERSECTION.replace('unique_intersection','multiset_intersection'), MULTISET.replace('            available[value] -= 1','            pass')],
        ['Drops required repeated occurrences by using sets.','Never consumes matched occurrences and may overuse the first input.'],
        multiset_oracle,random_arrays,
        ['Every match consumes one occurrence from each input.', 'Count the first input, then consume available counts while scanning the second.',
         'If count[value]>0: append value and decrement its count.', 'Each append spends one remaining occurrence, yielding the minimum of the two frequencies.'],
        'Store remaining frequencies from one input. A value in the other input contributes only when its remaining count is positive; decrement immediately after appending. This differs from the unique-intersection exercise. The independent oracle removes matched values from a copied list, without a frequency map.',
        'O(n + m) expected','O(n + m)',stress=[([[7]*1000,[7]*1000],[7]*1000)]),
    351: entry('count_unlock_patterns',[('m','int'),('n','int')],'int',
        ['recursion','backtracking','dynamic-programming','bitmask'],
        ['1 <= m, n <= 9. Count ordered patterns whose length is at least m and at most n; if m > n, return 0.',
         'Number the board row by row: 1 2 3 / 4 5 6 / 7 8 9. A dot may appear only once.',
         'A move through the exact center of another dot is allowed only if that dot was selected earlier. For example 1->3 needs 2; 2->9 has no intermediate dot and is allowed.'],
        [([1,1],'Each of the nine individual dots forms one pattern, so the count is 9.'),
         ([1,2],'There are 9 one-dot patterns and 56 legal ordered two-dot patterns, totaling 65. An unvisited midpoint blocks jumps such as 1->3.')],
        [[m,n] for m in range(1,10) for n in range(1,10) if (m,n) not in {(1,1),(1,2)}],UNLOCK,
        ['def count_unlock_patterns(m, n):\n    from math import perm\n    return sum(perm(9,k) for k in range(m,n+1))',
         UNLOCK.replace('(middle is None or mask & (1 << middle))','middle is None')],
        ['Counts permutations that jump through unvisited dots.','Forbids midpoint-crossing moves even after the midpoint was visited.'],
        unlock_oracle,random_unlock,
        ['Whether a jump is legal depends on the set of previously selected dots.',
         'Recurse on the last dot and a visited bitmask. Memoize these states.',
         'Count the current state if its size is within [m,n]; extend to each unused dot when its required midpoint is already visited.',
         'Precompute the eight unordered midpoint-crossing pairs. Memoized search counts each ordered path while sharing suffix states.'],
        'A state consists of the last selected dot and the visited set. Every valid next dot is unused and either has no midpoint on its segment or crosses a previously visited midpoint. Count each state at a permitted length, then extend until n dots. Summing over all starts counts ordered patterns. The independent oracle exhausts every dot permutation and checks geometric interior points; all 81 parameter pairs are deterministic tests.',
        'O(K^2 * 2^K), K = 9','O(K * 2^K)',difficulty=6),
    354: entry('max_nested_envelopes',[('envelopes','list[list[int]]')],'int',
        ['arrays','sorting','binary-search','dynamic-programming'],
        ['1 <= len(envelopes) <= 100000; each [width,height] has dimensions from 1 to 100000.',
         'Both width and height must increase strictly. Rotation is forbidden; equal-width or equal-height envelopes cannot nest.'],
        [([[[5,4],[6,4],[6,7],[2,3]]],'The chain [2,3] -> [5,4] -> [6,7] has length 3; [6,4] cannot fit in [6,7] because their widths are equal.'),
         ([[[1,1],[1,1],[1,1]]],'Identical envelopes do not fit strictly inside each other, so the longest chain contains one envelope.')],
        [[values] for values in ([[1,1]],[[1,2],[1,3]],[[1,2],[2,2]],[[2,1],[3,2]],
            [[3,2],[2,3]],[[1,1],[2,2],[3,3]],[[3,3],[2,2],[1,1]],[[1,4],[2,3],[3,2]],
            [[2,2],[2,3],[3,4]],[[1,3],[2,1],[3,2],[4,4]],[[1,100000],[100000,1]],
            [[1,1],[1,2],[2,2],[2,3]],[[2,2],[3,3],[3,3],[4,4]])],ENVELOPES,
        [ENVELOPES.replace('(pair[0],-pair[1])','(pair[0],pair[1])'),
         ENVELOPES.replace('bisect_left','bisect_right')],
        ['Ascending equal-width heights incorrectly form a nesting chain.','Non-strict height insertion incorrectly includes equal heights.'],
        envelopes_oracle,random_envelopes,
        ['Sorting one dimension leaves a subsequence problem in the other, but ties are dangerous.',
         'Sort widths ascending and tied heights descending, then find a strictly increasing height subsequence.',
         'Maintain minimum tails. Find the first tail >= height using binary search; replace it or append.',
         'Descending ties prevent equal widths from extending the increasing height subsequence; lower-bound insertion prevents equal heights from extending it.'],
        'Sort by (width,-height). Within one width, heights descend, so a strictly increasing height subsequence takes at most one of them. Maintain the smallest possible ending height for each chain length with binary search. This preserves all extension opportunities and gives O(n log n) time. The independent oracle searches the strict two-dimensional containment DAG without reducing it to a one-dimensional subsequence.',
        'O(n log n)','O(n)',difficulty=8,
        stress=[([[[i,i] for i in range(1,100001)]],100000),
                ([[[1,i] for i in range(1,100001)]],1)]),
    356: entry('has_vertical_reflection',[('points','list[list[int]]')],'bool',
        ['arrays','hash-maps','geometry'],
        ['1 <= len(points) <= 10000; each x and y is an integer between -100000000 and 100000000.',
         'Seek a vertical line x=c. Reflections must keep the same y. Compare coordinate sets, so repeated identical points do not need equal multiplicities.'],
        [([[[1,1],[-1,1]]],'The line x=0 exchanges the two points while preserving y=1, so reflection is possible.'),
         ([[[1,1],[-1,-1]]],'The x coordinates are symmetric, but the y coordinates differ. A vertical reflection cannot exchange these points, so the answer is false.')],
        [[points] for points in ([[0,0]],[[1,2],[1,3]],[[0,1],[2,1],[2,1]],[[0,0],[1,0]],
            [[0,0],[1,0],[3,0]],[[0,0],[2,0],[1,1]],[[0,0],[2,0],[0,1]],
            [[-3,2],[3,2],[0,9]],[[1,0],[3,0],[2,1],[4,1]],[[2,5],[2,5]],
            [[-100000000,0],[100000000,0]],[[1,1],[2,1],[3,1],[4,1]],
            [[0,0],[4,0],[1,1],[3,1]],[[0,0],[4,0],[1,1],[2,1]])],REFLECTION,
        [REFLECTION.replace('min(x for x,y in present)+max(x for x,y in present)','0'),
         'def has_vertical_reflection(points):\n    from collections import Counter\n    counts=Counter(map(tuple,points))\n    axis=min(x for x,y in counts)+max(x for x,y in counts)\n    return all(counts[x,y]==counts[axis-x,y] for x,y in counts)'],
        ['Only tests the y-axis rather than an arbitrary vertical line.','Treats repeated coordinates as a multiset despite the source set contract.'],
        reflection_oracle,random_reflection,
        ['Any valid vertical axis lies halfway between the leftmost and rightmost x coordinates.',
         'Store distinct coordinate pairs and use twice the axis to avoid floating-point arithmetic.',
         'Let s=min_x+max_x. Require (s-x,y) in the set for every (x,y).',
         'Extremes fix the only possible axis; testing every reflected coordinate proves that axis works.'],
        'A reflection exchanges the minimum and maximum x coordinates, fixing twice the axis as their sum. Every distinct (x,y) must have a partner (sum-x,y). Points on the axis partner with themselves. Repeated coordinates do not change the set, and half-integer axes need no floating point. The oracle independently enumerates candidate axes from all pairs.',
        'O(n) expected','O(n)',difficulty=5,
        stress=[([[[sign*i,i%7] for i in range(1,5001) for sign in (-1,1)]],True)]),
    360: entry('sort_transformed_array',[('nums','list[int]'),('a','int'),('b','int'),('c','int')],'list[int]',
        ['arrays','two-pointers','math'],
        ['1 <= len(nums) <= 200. nums is sorted in nondecreasing order.',
         '-100 <= nums[i], a, b, c <= 100. Return sorted values of a*x*x+b*x+c, preserving all occurrences.'],
        [([[-4,-2,2,4],1,3,5],'The values transform to [9,3,15,33]; sorting gives [3,9,15,33].'),
         ([[-4,-2,2,4],-1,3,5],'The downward-opening parabola gives [-23,-5,7,1], whose sorted order is [-23,-5,1,7].')],
        [[values,a,b,c] for values,a,b,c in [([0],0,0,0),([1],1,1,1),([-1,0,1],1,0,0),
            ([-1,0,1],-1,0,0),([-2,-1,0],0,2,1),([0,1,2],0,-2,1),([1,1,2],0,0,7),
            ([-5,-4,-3],1,0,0),([1,2,3],-1,0,0),([-100,100],100,100,100),
            ([-100,-99,0,99,100],-100,-100,-100),([-3,-1,0,4],2,-3,1),
            ([-2,-2,2,2],1,0,0)]],TRANSFORMED,
        ['def sort_transformed_array(nums, a, b, c):\n    return [a*x*x+b*x+c for x in nums]',
         TRANSFORMED.replace('if a >= 0:','if True:')],
        ['Assumes the transformation preserves sorted input order.','Always fills from the largest end, including downward-opening parabolas.'],
        transformed_oracle,random_transformed,
        ['For an upward-opening parabola, the maximum over an interval is at an endpoint; for a downward-opening one, the minimum is.',
         'Compare transformed left/right endpoints. Fill the result backward if a>=0 and forward otherwise.',
         'Choose the larger endpoint for a>=0, smaller for a<0; consume that endpoint and repeat.',
         'Every chosen endpoint is the next required extreme of the remaining values. Linear functions also satisfy the endpoint rule.'],
        'The quadratic is convex when a>=0 and concave when a<0. Its corresponding extreme on the remaining sorted interval lies at an endpoint. Select that extreme with two pointers, filling from the correct end. Each input is processed once; ties preserve duplicate counts. The independent oracle evaluates all values and performs a general sort.',
        'O(n)','O(n) output; O(1) auxiliary',difficulty=5,
        stress=[([list(range(-100,100)),100,-100,100],sorted(100*x*x-100*x+100 for x in range(-100,100)))]),
    361: entry('max_bomb_enemies',[('grid','list[list[str]]')],'int',
        ['matrices','dynamic-programming'],
        ['The rectangular grid has 1 to 500 rows and 1 to 500 columns; cells are exactly "0", "E", or "W".',
         'Place one bomb only on "0". It kills enemies in four straight row/column rays, stopping at walls, not at enemies. Return 0 if there is no empty cell.'],
        [([[['0','E','0','0'],['E','0','W','E'],['0','E','0','0']]],'Bombing row 1, column 1 (zero-based) kills one enemy above, one below, and one left. The wall shields the enemy to its right; the maximum is 3.'),
         ([[['W','W','W'],['0','0','0'],['E','E','E']]],'Each empty cell sees exactly one enemy below. No bomb can kill all three because explosions do not turn corners.')],
        [[grid] for grid in ([['0']],[['E']],[['W']],[list('0EE')],[list('0EWE')],
            [['0'],['E'],['W'],['E']],[list('E0E')],[list('W0W')],[list('EE'),list('EE')],
            [list('0E'),list('E0')],[list('EWE'),list('000'),list('EWE')],
            [list('E0E'),list('WWW'),list('EEE')],[list('000'),list('000')])],BOMB,
        [BOMB.replace("grid[r][x] != 'W'","True").replace("grid[y][c] != 'W'","True"),
         BOMB.replace("if grid[r][c] == '0':","if grid[r][c] != 'W':")],
        ['Counts enemies through walls.','Allows placement on enemy cells instead of only empty cells.'],
        bomb_oracle,random_bomb,
        ['Empty cells in the same wall-delimited segment see the same enemies along that direction.',
         'Recompute a horizontal count only at a row segment start, and a vertical count only at a column segment start.',
         'At each empty cell, combine its current row-segment count with its cached column-segment count.',
         'Each segment is scanned once for its count and once during traversal, giving linear work in grid area.'],
        'Walls divide each row and column into independent segments. Keep a single horizontal count and one vertical count per column. When crossing a segment boundary, scan that segment to count enemies. At an empty cell the two counts add without double counting because the bomb cell is not an enemy. The independent oracle casts four rays separately from every empty cell.',
        'O(rows * cols)','O(cols)',difficulty=5,
        stress=[([[[('0' if r==250 and c==250 else 'E') for c in range(500)] for r in range(500)]],998),
                ([[['W']*500 for _ in range(500)]],0)]),
    365: entry('can_measure_water',[('x','int'),('y','int'),('target','int')],'bool',
        ['math','graphs','breadth-first-search'],
        ['1 <= x, y, target <= 1000. Both jugs begin empty; the supply is unlimited.',
         'Allowed actions: fill one jug completely, empty one jug, or pour until the source is empty or the destination is full.',
         'The goal is target liters TOTAL across both jugs, not necessarily in one jug.'],
        [([3,5,4],'A valid sequence is (0,0)->(0,5)->(3,2)->(0,2)->(2,0)->(2,5)->(3,4)->(0,4). The total is now 4.'),
         ([1,2,3],'Fill both jugs: their combined total is 3, even though neither jug alone holds 3.')],
        [[x,y,t] for x,y,t in ((2,6,5),(1,1,1),(1,1,2),(1,1,3),(2,4,6),(2,4,8),
            (3,6,1),(3,6,3),(3,6,9),(4,7,5),(7,4,11),(5,5,10),(5,5,1),
            (6,10,8),(6,10,7),(8,12,4))],JUG,
        [JUG.replace('target <= x+y and ','') , JUG.replace('target <= x+y','target <= max(x,y)')],
        ['Ignores the combined-capacity bound.','Incorrectly requires the target to fit in a single jug.'],
        jug_oracle,random_jug,
        ['State search can model all six operations, but reachable quantities also share a divisibility invariant.',
         'Every reachable amount is a multiple of gcd(x,y). The total cannot exceed x+y.',
         'Return target <= x+y and target % gcd(x,y) == 0.',
         'The Euclidean pouring process realizes multiples of the gcd within total capacity; the two conditions are necessary and sufficient.'],
        'Filling and pouring produce amounts in the integer lattice generated by the capacities, whose step is gcd(x,y). The Euclidean pouring process realizes the needed multiples, while x+y bounds the combined storage. Check both conditions. For independent verification, the oracle uses breadth-first search over actual (left_volume,right_volume) states and all allowed operations.',
        'O(log min(x,y))','O(1)',difficulty=5,
        stress=[([999,1000,1],True),([1000,1000,999],False),([500,500,1000],True)]),
    369: entry('plus_one_linked_list',[('head','ListNode | None')],'ListNode | None',
        ['linked-lists','math'],
        ['The linked list has 1 to 100 nodes. Node values are digits 0 through 9, most significant first.',
         'No leading zero is present unless the entire number is zero. Return a ListNode head representing the incremented number, not a Python list.',
         'Digits may be updated in place and an overflow head may be added. Reusing existing nodes is not required by this source contract.'],
        [([[1,2,3]],'123 + 1 = 124, so the returned list is 1 -> 2 -> 4.'),
         ([[9,9]],'99 + 1 = 100: the carry passes through both digits and creates a new leading 1, producing 1 -> 0 -> 0.')],
        [[digits] for digits in ([0],[1],[8],[9],[1,0],[1,9],[9,0],[9,8],[9,9,9],
            [1,9,9],[9,1,9],[1,0,9,9],[8,9,0,9],[1,2,0,0],[9,9,8,9])],LINKED_PLUS,
        [LINKED_PLUS.replace('return dummy if dummy.val else dummy.next','return dummy.next'),
         'def plus_one_linked_list(head):\n    current=head\n    while current.next:\n        current=current.next\n    current.val=(current.val+1)%10\n    return head'],
        ['Discards the new leading digit when every input digit is 9.','Wraps the last digit but never propagates carry.'],
        linked_plus_oracle,random_linked_plus,
        ['Only the trailing run of 9s needs carry propagation.',
         'Keep the last node whose value is not 9, using a zero-valued dummy before the head.',
         'Increment that node, set every following digit to zero, and return the dummy only if it became 1.',
         'All digits after the remembered node are 9s; they become zeros. If every original digit is 9, the dummy provides the new leading 1.'],
        'Track the rightmost non-9 digit in a forward traversal. Increment it and zero its suffix, which consists entirely of 9s. A leading dummy handles overflow without reversing links. The source requires a linked-node result but does not impose identity reuse. This is distinct from array Plus One because the function receives and returns actual ListNode objects. The independent oracle uses decimal arithmetic on the serialized digits.',
        'O(n)','O(1) auxiliary',difficulty=5,
        stress=[([[9]*100],[1]+[0]*100),([[1]+[9]*99],[2]+[0]*99)]),
    370: entry('apply_range_additions',[('length','int'),('updates','list[list[int]]')],'list[int]',
        ['arrays','prefix-sums'],
        ['1 <= length <= 100000; 0 <= len(updates) <= 10000.',
         'Each update is [start,end,increment], with 0 <= start <= end < length and -1000 <= increment <= 1000.',
         'Begin with all zeros. Add to every position in each inclusive interval; overlapping updates accumulate.'],
        [([5,[[1,3,2],[2,4,3],[0,2,-2]]],'The arrays after the three updates are [0,2,2,2,0], then [0,2,5,5,3], then [-2,0,3,5,3].'),
         ([4,[[0,3,2],[1,1,-5]]],'The first interval adds 2 everywhere. The single-position second update changes only index 1, giving [2,-3,2,2].')],
        [[length,updates] for length,updates in ((1,[]),(3,[]),(1,[[0,0,1]]),(1,[[0,0,-1]]),
            (2,[[0,0,2]]),(2,[[1,1,3]]),(2,[[0,1,3]]),(3,[[0,2,2],[0,2,-2]]),
            (4,[[1,2,7]]),(5,[[0,0,1],[4,4,2]]),(3,[[0,1,3],[1,2,4]]),
            (2,[[0,1,0]]),(1,[[0,0,1000],[0,0,1000]]),(4,[[0,3,-1000],[2,3,1000]]))],RANGE,
        [RANGE.replace('changes[end+1] -= increment','changes[end] -= increment'),
         RANGE.replace('changes[start] += increment','changes[start] = increment').replace('changes[end+1] -= increment','changes[end+1] = -increment')],
        ['Ends updates before the inclusive right endpoint.','Overwrites previous boundary changes instead of accumulating overlapping updates.'],
        range_oracle,random_range,
        ['Record where an increment begins and where it stops instead of visiting its entire interval.',
         'Use a difference array with a sentinel after the last valid index.',
         'For [l,r,inc], add inc at l and subtract inc at r+1. Prefix-sum the first length entries.',
         'The prefix sum includes an update exactly on its inclusive interval. All updates combine by addition.'],
        'Each inclusive range contributes two boundary events. Summing events from left to right reconstructs the total increment active at each position. The extra sentinel permits an update ending at length-1 without special indexing. Negative increments, empty updates, and overlapping ranges all follow the same rule. The oracle independently sums covering updates for each output index.',
        'O(length + updates)','O(length)',difficulty=5,
        stress=[([100000,[[0,99999,1000] for _ in range(10000)]],[10000000]*100000)])
}

for source_id in (349,350):
    BATCH[source_id]['comparator'] = 'unordered'
BATCH[354]['prerequisites'] = ['binary-search','dynamic-programming']
BATCH[369]['params'] = [('head','ListNode | None','listnode')]
BATCH[369]['adapter'] = 'listnode'
