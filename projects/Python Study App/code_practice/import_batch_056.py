"""First completed slice of batch 56: small ordinary function interfaces."""
from collections import Counter
from itertools import combinations

from .import_batch_003 import entry


def square_oracle(args):
    points = args
    distances = sorted((a[0]-b[0]) ** 2 + (a[1]-b[1]) ** 2 for a, b in combinations(points, 2))
    return distances[0] > 0 and distances[:4] == [distances[0]] * 4 and distances[4:] == [2 * distances[0]] * 2


def harmonious_oracle(args):
    counts = Counter(args[0])
    return max((counts[value] + counts[value + 1] for value in counts if value + 1 in counts), default=0)


def range_oracle(args):
    rows, cols, operations = args
    if not operations:
        return rows * cols
    return min(operation[0] for operation in operations) * min(operation[1] for operation in operations)


def restaurant_oracle(args):
    left, right = args
    position = {word: index for index, word in enumerate(right)}
    scores = {word: index + position[word] for index, word in enumerate(left) if word in position}
    best = min(scores.values())
    return [word for word in left if scores.get(word) == best]


def flowers_oracle(args):
    bed, needed = args
    best = 0
    for mask in range(1 << len(bed)):
        candidate = bed.copy()
        placed = 0
        valid = True
        for index in range(len(bed)):
            if mask >> index & 1:
                placed += 1
                if candidate[index] or (index and candidate[index-1]) or (index + 1 < len(bed) and candidate[index+1]):
                    valid = False
                    break
                candidate[index] = 1
        if valid:
            best = max(best, placed)
    return best >= needed


def random_square(rng):
    points = [[rng.randint(-5, 5), rng.randint(-5, 5)] for _ in range(4)]
    return points


def random_harmonious(rng): return [[rng.randint(-12, 12) for _ in range(rng.randint(1, 50))]]


def random_range(rng):
    rows, cols = rng.randint(1, 40), rng.randint(1, 40)
    return [rows, cols, [[rng.randint(1, rows), rng.randint(1, cols)] for _ in range(rng.randint(0, 12))]]


def random_restaurants(rng):
    words = [f"place{index}" for index in range(20)]
    left, right = rng.sample(words, rng.randint(1, 12)), rng.sample(words, rng.randint(1, 12))
    if not set(left) & set(right): right[0] = left[0]
    return [left, right]


def random_bed(rng):
    length = rng.randint(1, 15)
    bed = [0] * length
    for index in range(length):
        if rng.random() < .25 and (not index or not bed[index-1]): bed[index] = 1
    return [bed, rng.randint(0, 6)]


SQUARE = '''\
from itertools import combinations

def valid_square(p1, p2, p3, p4):
    points = [p1, p2, p3, p4]
    distances = sorted((left[0] - right[0]) ** 2 + (left[1] - right[1]) ** 2 for left, right in combinations(points, 2))
    return distances[0] > 0 and distances[:4] == [distances[0]] * 4 and distances[4:] == [2 * distances[0]] * 2
'''
HARMONIOUS = '''\
def longest_harmonious_subsequence(nums):
    counts = Counter(nums)
    return max((counts[value] + counts[value + 1] for value in counts if value + 1 in counts), default=0)
'''
RANGE = '''\
def maximum_count_region(m, n, ops):
    if not ops:
        return m * n
    return min(row for row, _ in ops) * min(col for _, col in ops)
'''
RESTAURANT = '''\
def minimum_index_restaurants(list1, list2):
    positions = {word: index for index, word in enumerate(list2)}
    best = float('inf')
    answer = []
    for index, word in enumerate(list1):
        if word not in positions:
            continue
        score = index + positions[word]
        if score < best:
            best, answer = score, [word]
        elif score == best:
            answer.append(word)
    return answer
'''
FLOWERS = '''\
def can_place_flowers(flowerbed, n):
    bed = [0] + flowerbed[:] + [0]
    for index in range(1, len(bed) - 1):
        if bed[index-1] == bed[index] == bed[index+1] == 0:
            bed[index] = 1
            n -= 1
    return n <= 0
'''


def lesson(concept, strategy, pseudo, editorial): return [concept, strategy, pseudo, editorial], editorial


BATCH = {
    593: entry('valid_square', [('p1', 'list[int]'), ('p2', 'list[int]'), ('p3', 'list[int]'), ('p4', 'list[int]')], 'bool', ['math', 'geometry'],
        ['Each point has integer coordinates in -10,000..10,000.', 'The four input points may be in any order.'],
        [([[0, 0], [1, 1], [1, 0], [0, 1]], 'Four unit sides and two diagonal lengths of two form a square.'),
         ([[0, 0], [1, 0], [2, 0], [3, 0]], 'Collinear points have a zero-area shape, not a square.')],
        [[[0, 0], [1, 0], [0, 1], [1, 1]], [[0, 0], [2, 0], [0, 2], [2, 2]], [[0, 0], [2, 0], [0, 1], [2, 1]], [[0, 0], [1, 1], [2, 0], [1, -1]], [[0, 0], [0, 0], [0, 0], [0, 0]], [[-1, -1], [0, 0], [-1, 0], [0, -1]], [[0, 0], [3, 0], [0, 3], [3, 3]], [[1, 2], [2, 3], [3, 2], [2, 1]], [[0, 0], [1, 0], [1, 1], [2, 1]], [[0, 0], [1, 2], [2, 1], [1, -1]], [[5, 5], [5, 6], [6, 5], [6, 6]], [[0, 0], [2, 1], [4, 0], [2, -1]]], SQUARE,
        [SQUARE.replace("and distances[4:] == [2 * distances[0]] * 2", "").replace("distances[:4] == [distances[0]] * 4", "distances[:2] == [distances[0]] * 2"), SQUARE.replace('distances[0] > 0', 'True')],
        ['Accepts equal-sided rectangles without checking diagonals.', 'Accepts four coincident points with zero-length sides.'], square_oracle, random_square,
        *lesson('A square has a characteristic multiset of six pair distances.', 'Ignore input order by sorting all squared distances.', 'Compute six squared distances; require four equal nonzero sides and two equal double-length diagonals.', 'Squared distance avoids roots. The square distance pattern is necessary and sufficient for four planar points.'), 'O(1)', 'O(1)', 3),
    594: entry('longest_harmonious_subsequence', [('nums', 'list[int]')], 'int', ['arrays', 'hash-maps'],
        ['1 <= len(nums) <= 20,000; values are in -10^9..10^9.', 'A valid subsequence has maximum minus minimum exactly one.'],
        [([[1, 3, 2, 2, 5, 2, 3, 7]], 'Use the three 2 values and two 3 values, for length five.'),
         ([[1, 1, 1, 1]], 'No value one greater than 1 exists, so no harmonious subsequence exists.')],
        [[[1]], [[1, 2]], [[2, 1]], [[1, 3]], [[-1, 0]], [[-2, -1, -1]], [[1, 2, 2, 3, 3, 3]], [[0, 0, 1, 1]], [[5, 5, 6]], [[-10, -9, -8]], [[1, 2, 3, 4]], [[2, 2, 2, 3]], [[100, 101, 101, 102]]], HARMONIOUS,
        [HARMONIOUS.replace('value + 1', 'value + 2'), HARMONIOUS.replace('counts[value] + counts[value + 1]', 'max(counts.values())')],
        ['Uses values two apart.', 'Returns the most frequent value even without an adjacent value.'], harmonious_oracle, random_harmonious,
        *lesson('Only two neighboring values can appear in a harmonious subsequence.', 'Count every value, then combine each count with value+1.', 'Build a frequency map and maximize count[x]+count[x+1].', 'All copies of two adjacent values help, while any farther value would violate the exact range requirement.'), 'O(n)', 'O(n)', 3),
    598: entry('maximum_count_region', [('m', 'int'), ('n', 'int'), ('ops', 'list[list[int]]')], 'int', ['matrices', 'math'],
        ['1 <= m,n <= 40,000; each operation [a,b] satisfies 1 <= a <= m and 1 <= b <= n.', 'An operation increments the top-left a by b submatrix.'],
        [([3, 3, [[2, 2], [3, 3]]], 'Only the overlapping 2 by 2 corner receives both increments, so it has the maximum count.'),
         ([3, 3, []], 'Without operations every cell remains at the same maximum value, so all nine cells count.')],
        [[1, 1, []], [1, 5, [[1, 3]]], [5, 1, [[3, 1]]], [2, 2, [[1, 1]]], [4, 5, [[4, 5]]], [4, 5, [[2, 4], [3, 2]]], [10, 10, [[10, 1], [1, 10]]], [3, 4, [[3, 4], [2, 2], [1, 3]]], [7, 8, [[5, 6], [6, 5]]], [2, 9, [[1, 9], [2, 2]]], [100, 100, [[99, 100], [100, 99]]], [3, 3, [[2, 2]]]], RANGE,
        [RANGE.replace('min(row for row, _ in ops)', 'max(row for row, _ in ops)'), RANGE.replace('return m * n', 'return 0')],
        ['Uses the union instead of the common overlap.', 'Returns no cells for an empty operation list.'], range_oracle, random_range,
        *lesson('Cells with the most increments must belong to every operated rectangle.', 'The common top-left rectangle has the smallest row and column limits.', 'If ops is empty return m*n; otherwise multiply the minimum a and minimum b.', 'All operation rectangles share exactly that minimum-size prefix, and no cell outside it receives every increment.'), 'O(number of operations)', 'O(1)', 3),
    599: entry('minimum_index_restaurants', [('list1', 'list[str]'), ('list2', 'list[str]')], 'list[str]', ['arrays', 'hash-maps'],
        ['Each list has 1..1,000 unique strings, and at least one string is common.', 'Return every common string with the smallest combined index sum in list1 order.'],
        [([['Shogun', 'Tapioca Express', 'Burger King', 'KFC'], ['Piatti', 'The Grill at Torrey Pines', 'Hungry Hunter Steakhouse', 'Shogun']], 'Shogun is the only common restaurant and has index sum three.'),
         ([['a', 'b', 'c'], ['c', 'b', 'a']], 'All three common items have index sum two, so preserve list1 order.')],
        [[['a'], ['a']], [['a'], ['b', 'a']], [['a', 'b'], ['b', 'a']], [['a', 'b', 'c'], ['x', 'b', 'c']], [['a', 'b', 'c'], ['c', 'x', 'a']], [['aa', 'bb'], ['cc', 'aa']], [['a', 'b', 'c', 'd'], ['d', 'c', 'b', 'a']], [['a', 'b', 'c'], ['a', 'c', 'b']], [['x', 'y', 'z'], ['z', 'y', 'x']], [['a', 'x', 'b'], ['b', 'x', 'a']], [['red', 'blue'], ['blue', 'red']], [['one', 'two', 'three'], ['three', 'two', 'one']]], RESTAURANT,
        [RESTAURANT.replace('elif score == best:', 'elif False:'), RESTAURANT.replace('score = index + positions[word]', 'score = positions[word]')],
        ['Drops ties for the smallest index sum.', 'Ignores the index in the first list.'], restaurant_oracle, random_restaurants,
        *lesson('A dictionary turns a matching restaurant into a constant-time lookup.', 'Scan list1 while tracking the smallest sum seen so far and all ties.', 'Map list2 strings to indices; for list1 matches replace or append to the answer by sum.', 'Every common string is examined once, and retaining ties is required because several strings can share the minimum sum.'), 'O(len(list1)+len(list2))', 'O(len(list2))', 3),
    605: entry('can_place_flowers', [('flowerbed', 'list[int]'), ('n', 'int')], 'bool', ['arrays', 'greedy'],
        ['1 <= len(flowerbed) <= 20,000; 0 <= n <= len(flowerbed).', 'Existing flowers are never adjacent.'],
        [([[1, 0, 0, 0, 1], 1], 'Plant in the middle empty plot, yielding a valid arrangement.'),
         ([[1, 0, 0, 0, 1], 2], 'After the middle placement no other plot has both neighbors empty.')],
        [[[0], 0], [[0], 1], [[1], 0], [[1], 1], [[0, 0], 1], [[0, 0], 2], [[0, 0, 0], 2], [[1, 0, 0], 1], [[0, 0, 1], 1], [[0, 1, 0], 1], [[0, 0, 0, 0, 0], 3], [[1, 0, 1, 0, 1], 1]], FLOWERS,
        [FLOWERS.replace('bed = [0] + flowerbed[:] + [0]', 'bed = flowerbed[:]'), FLOWERS.replace('bed[index] = 1', 'pass')],
        ['Misses edge plots because they lack virtual empty neighbors.', 'Counts a placement without blocking its adjacent plots.'], flowers_oracle, random_bed,
        *lesson('A flower only needs its two immediate neighbors empty.', 'Scan left to right; a greedy placement cannot block a better earlier placement.', 'Pad with zero sentinels, plant whenever three consecutive cells are zero, and decrement n.', 'Taking the earliest legal plot leaves at least as much room to its right as skipping it, so the greedy scan is optimal.'), 'O(n)', 'O(n)', 3),
}
