"""Lock ordering, digit paths, LCM components, rectangles, and modular prefixes."""
from itertools import combinations, permutations
from math import gcd

from .import_batch_055 import entry


def locks_oracle(args):
    strength, k = args
    return min(sum((value + 1 + index * k - 1) // (1 + index * k)
                   for index, value in enumerate(order))
               for order in permutations(strength))


def random_locks(rng):
    return [[rng.randint(1, 40) for _ in range(rng.randint(1, 7))], rng.randint(1, 8)]


def is_prime(value):
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def digit_neighbors(value, digits):
    text = list(str(value).zfill(digits))
    for index, char in enumerate(text):
        digit = ord(char) - 48
        if digit < 9:
            changed = text[:]
            changed[index] = str(digit + 1)
            yield int(''.join(changed))
        if digit > 0 and not (index == 0 and digit == 1):
            changed = text[:]
            changed[index] = str(digit - 1)
            yield int(''.join(changed))


def digit_oracle(args):
    start, target = args
    if is_prime(start) or is_prime(target):
        return -1
    digits = len(str(start))
    low = 1 if digits == 1 else 10 ** (digits - 1)
    high = 10 ** digits
    infinity = 10 ** 30
    distance = [infinity] * high
    distance[start] = start
    queue = [start]
    present = {start}
    while queue:
        current = queue.pop(0)
        present.discard(current)
        for neighbor in digit_neighbors(current, digits):
            if low <= neighbor < high and not is_prime(neighbor):
                candidate = distance[current] + neighbor
                if candidate < distance[neighbor]:
                    distance[neighbor] = candidate
                    if neighbor not in present:
                        queue.append(neighbor)
                        present.add(neighbor)
    return -1 if distance[target] == infinity else distance[target]


def random_digits(rng):
    digits = rng.randint(1, 2)
    low = 1 if digits == 1 else 10 ** (digits - 1)
    high = 10 ** digits - 1
    return [rng.randint(low, high), rng.randint(low, high)]


def lcm_components_oracle(args):
    nums, threshold = args
    parent = list(range(len(nums)))
    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    def union(left, right):
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left
    for left in range(len(nums)):
        for right in range(left):
            if nums[left] // gcd(nums[left], nums[right]) * nums[right] <= threshold:
                union(left, right)
    return len({find(index) for index in range(len(nums))})


def random_lcm(rng):
    size = rng.randint(1, 9)
    nums = rng.sample(range(1, 35), size)
    return [nums, rng.randint(1, 35)]


def rectangle_oracle(args):
    points = args[0]
    available = {tuple(point) for point in points}
    best = -1
    xs = sorted({point[0] for point in points})
    ys = sorted({point[1] for point in points})
    for x1, x2 in combinations(xs, 2):
        for y1, y2 in combinations(ys, 2):
            corners = {(x1, y1), (x1, y2), (x2, y1), (x2, y2)}
            if corners <= available and all((x, y) in corners or not (x1 <= x <= x2 and y1 <= y <= y2)
                                             for x, y in available):
                best = max(best, (x2 - x1) * (y2 - y1))
    return best


def random_rectangle(rng):
    size = rng.randint(1, 10)
    points = rng.sample([[x, y] for x in range(7) for y in range(7)], size)
    return [points]


def subarray_oracle(args):
    nums, k = args
    return max(sum(nums[left:right]) for left in range(len(nums))
               for right in range(left + k, len(nums) + 1, k))


def random_subarray(rng):
    size = rng.randint(1, 14)
    return [[rng.randint(-20, 20) for _ in range(size)], rng.randint(1, size)]


LOCKS = '''def minimum_lock_break_time(strength,k):
    size=len(strength);infinity=10**30;dp=[infinity]*(1<<size);dp[0]=0
    for mask in range(1<<size):
        factor=1+mask.bit_count()*k
        for index,value in enumerate(strength):
            if not (mask>>index&1):
                nxt=mask|1<<index
                dp[nxt]=min(dp[nxt],dp[mask]+(value+factor-1)//factor)
    return dp[-1]
'''

DIGITS = '''def minimum_nonprime_digit_cost(n,m):
    import heapq
    digits=len(str(n));limit=10**digits
    prime=[True]*limit
    if limit>0:prime[0]=False
    if limit>1:prime[1]=False
    for value in range(2,int(limit**0.5)+1):
        if prime[value]:
            for multiple in range(value*value,limit,value):prime[multiple]=False
    if prime[n] or prime[m]:return -1
    distance={n:n};heap=[(n,n)]
    while heap:
        cost,current=heapq.heappop(heap)
        if cost!=distance[current]:continue
        if current==m:return cost
        text=list(str(current))
        for index,char in enumerate(text):
            digit=int(char)
            for change in (-1,1):
                changed=digit+change
                if not 0<=changed<=9 or (index==0 and changed==0):continue
                candidate=text[:];candidate[index]=str(changed);neighbor=int(''.join(candidate))
                new_cost=cost+neighbor
                if not prime[neighbor] and new_cost<distance.get(neighbor,float('inf')):
                    distance[neighbor]=new_cost;heapq.heappush(heap,(new_cost,neighbor))
    return -1
'''

LCM_COMPONENTS = '''def count_lcm_components(nums,threshold):
    parent=list(range(threshold+1))
    def find(node):
        while parent[node]!=node:
            parent[node]=parent[parent[node]];node=parent[node]
        return node
    def union(left,right):
        left=find(left);right=find(right)
        if left!=right:parent[right]=left
    for value in nums:
        if value<=threshold:
            for multiple in range(value,threshold+1,value):union(value,multiple)
    roots=set();outside=0
    for value in nums:
        if value>threshold:outside+=1
        else:roots.add(find(value))
    return outside+len(roots)
'''

RECTANGLE = '''def maximum_empty_rectangle_area(points):
    available={tuple(point) for point in points};answer=-1
    for first in range(len(points)):
        x1,y1=points[first]
        for second in range(first):
            x2,y2=points[second]
            if x1==x2 or y1==y2:continue
            low_x,high_x=sorted((x1,x2));low_y,high_y=sorted((y1,y2))
            corners={(low_x,low_y),(low_x,high_y),(high_x,low_y),(high_x,high_y)}
            if not corners<=available:continue
            if all((x,y) in corners or not (low_x<=x<=high_x and low_y<=y<=high_y) for x,y in available):
                answer=max(answer,(high_x-low_x)*(high_y-low_y))
    return answer
'''

SUBARRAY = '''def maximum_divisible_length_subarray_sum(nums,k):
    minimum=[float('inf')]*k;minimum[0]=0;prefix=0;answer=float('-inf')
    for end,value in enumerate(nums,1):
        prefix+=value;remainder=end%k
        answer=max(answer,prefix-minimum[remainder])
        minimum[remainder]=min(minimum[remainder],prefix)
    return answer
'''


def lesson(a, b, c, d):
    return [a, b, c, d]


LOCK_CASES = [[values, k] for values, k in [
    ([3, 4, 1], 1), ([2, 5, 4], 2), ([1], 1), ([10], 5), ([1, 1], 1),
    ([2, 3], 1), ([10, 10], 10), ([5, 9, 2], 3), ([7, 3, 12, 1], 2),
    ([100, 1, 50], 5), ([4, 8, 12, 16], 1), ([9, 2, 6], 4),
    ([20, 19, 18, 1], 3), ([6, 6, 6, 6, 6], 2)]]
DIGIT_CASES = [[left, right] for left, right in [
    (10, 12), (4, 8), (6, 2), (1, 1), (8, 8), (10, 10), (11, 12),
    (12, 14), (20, 22), (25, 27), (80, 88), (90, 99), (100, 102), (200, 202)]]
LCM_CASES = [[nums, threshold] for nums, threshold in [
    ([2, 4, 8, 3, 9], 5), ([2, 4, 8, 3, 9, 12], 10), ([1], 1),
    ([1, 2, 3], 3), ([2, 3], 6), ([2, 3], 5), ([6, 10, 15], 30),
    ([4, 6, 9], 12), ([7, 14, 21], 10), ([2, 5, 10], 10),
    ([3, 4, 12, 20], 12), ([5, 7, 11], 20), ([1, 50, 100], 20),
    ([8, 12, 18, 24], 24)]]
RECTANGLE_CASES = [[points] for points in [
    [[1, 1], [1, 3], [3, 1], [3, 3]],
    [[1, 1], [1, 3], [3, 1], [3, 3], [2, 2]],
    [[1, 1], [1, 3], [3, 1], [3, 3], [1, 2], [3, 2]], [[0, 0]],
    [[0, 0], [0, 1], [1, 0]], [[0, 0], [0, 1], [1, 0], [1, 1]],
    [[0, 0], [0, 2], [3, 0], [3, 2]], [[0, 0], [0, 2], [3, 0], [3, 2], [0, 1]],
    [[0, 0], [0, 3], [4, 0], [4, 3], [5, 5]],
    [[0, 0], [0, 1], [1, 0], [1, 1], [0, 2], [1, 2]],
    [[0, 0], [0, 2], [2, 0], [2, 2], [3, 0], [3, 2]],
    [[1, 1], [1, 4], [2, 1], [2, 4], [3, 2]],
    [[0, 0], [0, 4], [4, 0], [4, 4], [2, 0]],
    [[2, 2], [2, 5], [7, 2], [7, 5], [0, 0], [9, 9]]]]
SUBARRAY_CASES = [[nums, k] for nums, k in [
    ([1, 2], 1), ([-1, -2, -3, -4, -5], 4), ([-5, 1, 2, -3, 4], 2),
    ([5], 1), ([-5], 1), ([1, -2, 3], 3), ([1, 2, 3, 4], 2),
    ([-1, -2, -3, -4], 2), ([4, -1, 2, 1], 3), ([10, -20, 30, -5, 6], 2),
    ([0, 0, 0], 2), ([8, -9, 8, -9, 8], 4), ([3, -1, 3, -1, 3, -1], 3),
    ([-10, 5, 5, -10, 20, -1], 2)]]


BATCH = {
    3376: entry('minimum_lock_break_time', [('strength', 'list[int]'), ('k', 'int')], 'int',
                ['arrays', 'bitmask dynamic programming', 'backtracking'],
                ['strength has 1–8 positive values up to one million; 1 <= k <= 10.',
                 'The sword begins with factor one, gains that much energy per minute, and resets energy after each lock.',
                 'After each broken lock the factor increases by k; choose the lock order minimizing total minutes.'],
                [([[3, 4, 1], 1], 'Break strengths one, four, then three at factors one, two, and three for four minutes total.'),
                 ([[2, 5, 4], 2], 'An optimal order spends two, two, then one minute, totaling five.')],
                LOCK_CASES, LOCKS,
                [LOCKS.replace('(value+factor-1)//factor', 'value//factor'),
                 LOCKS.replace('factor=1+mask.bit_count()*k', 'factor=1+mask.bit_count()')],
                ['Uses floor division when partial final minutes are required.', 'Increases the factor by one rather than by k.'],
                locks_oracle, random_locks,
                lesson('Only the set of broken locks determines the current energy factor.',
                       'Use subset dynamic programming and try every remaining lock as the next choice.',
                       'For each mask, compute factor 1+popcount(mask)*k and relax mask plus one lock by its ceiling time.',
                       'Every order corresponds to one path through the subset states, so taking the cheapest predecessor finds the best permutation.'),
                'O(n*2^n)', 'O(2^n)', 6),
    3377: entry('minimum_nonprime_digit_cost', [('n', 'int'), ('m', 'int')], 'int',
                ['graphs', 'shortest paths', 'number theory'],
                ['1 <= n,m < 10,000 and both have the same number of decimal digits.',
                 'Each step changes one digit by one without creating a leading zero, and every visited value must be non-prime.',
                 'The path cost includes the starting value and every value reached; return -1 when no valid path exists.'],
                [([10, 12], 'The cheapest valid route is 10, 20, 21, 22, 12, whose values total 85.'),
                 ([4, 8], 'Every route from four is blocked by primes, so eight is unreachable.')],
                DIGIT_CASES, DIGITS,
                [DIGITS.replace('if prime[n] or prime[m]:return -1', 'if False:return -1').replace('if not prime[neighbor]', 'if True'),
                 DIGITS.replace('distance={n:n};heap=[(n,n)]', 'distance={n:0};heap=[(0,n)]')],
                ['Allows prime endpoints and intermediate values.', 'Omits the starting number from the transformation cost.'],
                digit_oracle, random_digits,
                lesson('Treat each allowed non-prime integer as a graph node and a digit edit as an edge.',
                       'Use a sieve to block primes and Dijkstra because entering different numbers has different positive cost.',
                       'Start with distance n; pop the cheapest value, generate legal one-digit neighbors, and relax by adding the neighbor.',
                       'Dijkstra finalizes minimum accumulated cost because all entered-value edge weights are nonnegative.'),
                'O(10^d*d log 10^d)', 'O(10^d)', 6),
    3378: entry('count_lcm_components', [('nums', 'list[int]'), ('threshold', 'int')], 'int',
                ['arrays', 'union find', 'number theory'],
                ['nums has up to 100,000 distinct positive values; threshold is at most 200,000.',
                 'Two array positions share an undirected edge exactly when their least common multiple is at most threshold.',
                 'Return the number of connected components; every value above threshold is necessarily isolated.'],
                [([[2, 4, 8, 3, 9], 5], 'Only values two and four connect; eight, three, and nine are isolated, giving four components.'),
                 ([[2, 4, 8, 3, 9, 12], 10], 'Values two, three, four, eight, and nine connect through bounded common multiples; twelve is isolated.')],
                LCM_CASES, LCM_COMPONENTS,
                [LCM_COMPONENTS.replace('range(value,threshold+1,value)', 'range(value,threshold,value)'),
                 LCM_COMPONENTS.replace('for multiple in range(value,threshold+1,value):union(value,multiple)', 'for multiple in (value,):union(value,multiple)')],
                ['Treats the threshold boundary as strict.', 'Unions no shared-multiple intermediates, leaving connected values separate.'],
                lcm_components_oracle, random_lcm,
                lesson('Values connect through any common multiple not exceeding the threshold.',
                       'Use multiples as virtual union-find nodes; all multiples of each present value join its component.',
                       'For each value at most threshold, union it with every bounded multiple, then count distinct roots plus large isolated values.',
                       'A direct LCM edge supplies a shared multiple, and chains through virtual multiples exactly preserve graph connectivity.'),
                'O(threshold log threshold+n)', 'O(threshold)', 8),
    3380: entry('maximum_empty_rectangle_area', [('points', 'list[list[int]]')], 'int',
                ['geometry', 'arrays', 'enumeration'],
                ['points contains 1–10 unique integer coordinates in 0..100.',
                 'A valid positive-area rectangle is axis-aligned, uses four listed corners, and contains no other listed point inside or on its border.',
                 'Return the largest valid area, or -1 when no rectangle exists.'],
                [([[[1, 1], [1, 3], [3, 1], [3, 3]]], 'The four points form an empty two-by-two rectangle with area four.'),
                 ([[[1, 1], [1, 3], [3, 1], [3, 3], [2, 2]]], 'The extra center point invalidates the only possible rectangle, so return -1.')],
                RECTANGLE_CASES, RECTANGLE,
                [RECTANGLE.replace("if all((x,y) in corners or not (low_x<=x<=high_x and low_y<=y<=high_y) for x,y in available):", 'if True:'),
                 RECTANGLE.replace('low_x<=x<=high_x and low_y<=y<=high_y', 'low_x<x<high_x and low_y<y<high_y')],
                ['Checks the four corners but ignores all interior and border points.', 'Rejects interior points but incorrectly allows extra points on the border.'],
                rectangle_oracle, random_rectangle,
                lesson('Opposite corners determine one axis-aligned rectangle and its other two required corners.',
                       'Enumerate point pairs, verify all four corners, then scan every point for forbidden occupancy.',
                       'Normalize x/y bounds; require the corner set and reject any non-corner within the closed rectangle.',
                       'Every rectangle has an opposite-corner pair, and the closed-region scan enforces both the interior and border restriction.'),
                'O(p³)', 'O(p)', 5),
    3381: entry('maximum_divisible_length_subarray_sum', [('nums', 'list[int]'), ('k', 'int')], 'int',
                ['arrays', 'prefix sums', 'dynamic programming'],
                ['1 <= k <= len(nums) <= 200,000; values may be negative and have absolute value up to one billion.',
                 'Choose a nonempty contiguous subarray whose length is divisible by k.',
                 'Return the maximum possible sum.'],
                [([[1, 2], 1], 'The full length-two subarray is divisible by one and has maximum sum three.'),
                 ([[-1, -2, -3, -4, -5], 4], 'The first four values form the best valid length-four subarray, with sum negative ten.')],
                SUBARRAY_CASES, SUBARRAY,
                [SUBARRAY.replace("        answer=max(answer,prefix-minimum[remainder])\n        minimum[remainder]=min(minimum[remainder],prefix)", "        minimum[remainder]=min(minimum[remainder],prefix)\n        answer=max(answer,prefix-minimum[remainder])"),
                 SUBARRAY.replace('remainder=end%k', 'remainder=(end-1)%k')],
                ['Updates the minimum first, allowing an invalid empty subarray with sum zero.', 'Matches prefix positions from different modulo classes.'],
                subarray_oracle, random_subarray,
                lesson('A subarray length is divisible by k when its two prefix indices share the same remainder modulo k.',
                       'For each remainder, retain the smallest earlier prefix sum to maximize the current difference.',
                       'Scan prefix ends; query the matching remainder minimum before inserting the current prefix.',
                       'Every valid start is in that remainder class, and subtracting its minimum yields the best valid subarray ending here.'),
                'O(n)', 'O(k)', 5),
}
