"""Recursive decomposition, four-way partition, two-budget selection and coverage."""
from itertools import product

from .import_batch_003 import entry


def words_oracle(args):
    """Enumerate every nonempty set of cut positions, not a segmentation DP."""
    words = args[0]
    vocabulary = set(words)
    result = []
    for word in words:
        for mask in range(1, 1 << (len(word)-1)):
            cuts = [0] + [i for i in range(1, len(word)) if mask & (1 << (i-1))] + [len(word)]
            if all(word[a:b] in vocabulary for a, b in zip(cuts, cuts[1:])):
                result.append(word)
                break
    return result


def square_oracle(args):
    """Subset states fill one side at a time, independent of four-bucket DFS."""
    sticks = args[0]
    total = sum(sticks)
    if total % 4 or max(sticks) > total // 4:
        return False
    target = total // 4
    remainder = [-1] * (1 << len(sticks))
    remainder[0] = 0
    for mask, partial in enumerate(remainder):
        if partial < 0:
            continue
        for i, stick in enumerate(sticks):
            if not mask & (1 << i) and partial + stick <= target:
                remainder[mask | (1 << i)] = (partial + stick) % target
    return remainder[-1] == 0


def budgets_oracle(args):
    words, zeros, ones = args
    costs = [(word.count('0'), word.count('1')) for word in words]
    best = 0
    for mask in range(1 << len(words)):
        selected = [cost for i, cost in enumerate(costs) if mask & (1 << i)]
        if sum(z for z, _ in selected) <= zeros and sum(o for _, o in selected) <= ones:
            best = max(best, len(selected))
    return best


def heaters_oracle(args):
    houses, heaters = args
    return max(min(abs(house-heater) for heater in heaters) for house in houses)


def random_words(rng):
    words = set()
    target = rng.randint(1, 10)
    while len(words) < target:
        words.add(''.join(rng.choice('ab') for _ in range(rng.randint(1, 8))))
    return [sorted(words)]


def random_square(rng):
    return [[rng.randint(1, 10) for _ in range(rng.randint(1, 10))]]


def random_budgets(rng):
    return [[''.join(rng.choice('01') for _ in range(rng.randint(1, 8)))
             for _ in range(rng.randint(1, 10))], rng.randint(1, 10), rng.randint(1, 10)]


def random_heaters(rng):
    return [[rng.randint(1, 50) for _ in range(rng.randint(1, 10))],
            [rng.randint(1, 50) for _ in range(rng.randint(1, 10))]]


WORDS = '''\
def concatenated_words(words):
    from functools import lru_cache
    vocabulary = set(words)
    answer = []
    for word in words:
        @lru_cache(None)
        def can_finish(start):
            if start == len(word):
                return True
            for end in range(start+1, len(word)+1):
                if start == 0 and end == len(word):
                    continue
                if word[start:end] in vocabulary and can_finish(end):
                    return True
            return False
        if can_finish(0):
            answer.append(word)
    return answer
'''
SQUARE = '''\
def make_square(matchsticks):
    from functools import lru_cache
    total = sum(matchsticks)
    if total % 4 or max(matchsticks) > total//4:
        return False
    target = total//4
    ordered = sorted(matchsticks, reverse=True)
    @lru_cache(None)
    def place(index, sides):
        if index == len(ordered):
            return True
        seen = set()
        for side, used in enumerate(sides):
            if used in seen or used+ordered[index] > target:
                continue
            seen.add(used)
            following = list(sides)
            following[side] += ordered[index]
            if place(index+1, tuple(sorted(following))):
                return True
        return False
    return place(0, (0,0,0,0))
'''
BUDGETS = '''\
def largest_binary_subset(strs, m, n):
    dp = [[0]*(n+1) for _ in range(m+1)]
    for word in strs:
        zeros = word.count('0')
        ones = len(word)-zeros
        for z in range(m, zeros-1, -1):
            row, previous = dp[z], dp[z-zeros]
            for o in range(n, ones-1, -1):
                candidate = previous[o-ones]+1
                if candidate > row[o]:
                    row[o] = candidate
    return dp[m][n]
'''
HEATERS = '''\
def minimum_heater_radius(houses, heaters):
    from bisect import bisect_left
    ordered = sorted(heaters)
    answer = 0
    for house in houses:
        index = bisect_left(ordered, house)
        distance = float('inf')
        if index:
            distance = min(distance, house-ordered[index-1])
        if index < len(ordered):
            distance = min(distance, ordered[index]-house)
        answer = max(answer, distance)
    return answer
'''


# Equal-length words cannot use shorter dictionary entries: 10,000 unique words,
# total length exactly 100,000, with many shared prefixes but no valid splits.
LARGE_WORDS = [''.join(chars) for chars in product('ab', repeat=10)]
LARGE_WORDS += [''.join(chars) for chars in product('cdefghijkl', repeat=4)][:8976]
# Pad the four-letter family to ten letters without introducing a shorter word.
LARGE_WORDS = [word if len(word) == 10 else 'zzzzzz'+word for word in LARGE_WORDS]

BATCH = {
472: entry('concatenated_words', [('words','list[str]')], 'list[str]',
    ['strings','recursion','dynamic-programming'],
    ['1 <= words.length <= 10,000; words are unique lowercase English strings of length 1..30; total characters <= 100,000.',
     'Return all dictionary words formed from at least two strictly shorter dictionary words, in any order.',
     'A shorter word may be reused. A word cannot count itself as a one-piece decomposition.'],
    [([['cat','cats','catsdogcats','dog','dogcatsdog','hippopotamuses','rat','ratcatdogcat']],
      'The results split as cats+dog+cats, dog+cats+dog, and rat+cat+dog+cat. Reusing a shorter word is allowed.'),
     ([['a','aaa','b']], 'Only aaa qualifies: a+a+a uses three pieces. Neither single-letter word can be split.')],
    [[words] for words in (['a'], ['a','b'], ['a','aa'], ['aa','aaaa'], ['a','aaaa'],
        ['ab','abab','aba'], ['cat','dog','catdog'], ['abc','ab','c'], ['a','b','ab','ba','abba'],
        ['aaa','aa','aaaaa'], ['abc','abcd'], ['a','b','aba','bab','ababab'])],
    WORDS, [WORDS.replace('if start == 0 and end == len(word):', 'if False:'),
      "def concatenated_words(words):\n    vocabulary=set(words)\n    return [w for w in words if any(w[:i] in vocabulary and w[i:] in vocabulary for i in range(1,len(w)))]\n"],
    ['Accepts the entire word as a one-piece decomposition.', 'Requires exactly two pieces and misses three-or-more-part decompositions.'],
    words_oracle, random_words,
    ['Try decomposing each candidate using other, strictly shorter words.',
     'Recursively solve the remaining suffix and memoize its starting index. Forbid the unsplit whole candidate.',
     'For each end after start, check the dictionary slice and recurse on end; reaching the end means success.',
     'A first cut guarantees at least two pieces. Reuse dictionary entries freely; memoization avoids repeating suffix failures.'],
    'Every legal decomposition chooses a first shorter prefix and then a decomposition of the remainder. '
    'Skipping the whole-word first edge prevents self-acceptance while leaving every multi-piece path. '
    'Memoized start positions bound repeated search. The oracle enumerates cut-position subsets rather '
    'than memoized suffixes. This returns qualifying dictionary words, unlike Word Break\'s boolean or sentence list.',
    'O(sum(L_i^3)) with Python substring slicing', 'O(total input characters + max L_i)', difficulty=8,
    stress=[([LARGE_WORDS], []), ([['a','a'*30,'b'*30]], ['a'*30])]),
473: entry('make_square', [('matchsticks','list[int]')], 'bool',
    ['arrays','backtracking','recursion','memoization'],
    ['1 <= matchsticks.length <= 15; 1 <= each length <= 100,000,000.',
     'Use every stick exactly once to form four equal sides. Sticks may be joined but never broken.',
     'Return a boolean. Divisibility of the total by four is necessary, not sufficient.'],
    [([[1,1,2,2,2]], 'Each side has length 2: use 1+1 for one side and a single 2 for each of the other three.'),
     ([[3,3,3,3,4]], 'The total is 16, but the four length-3 sticks cannot form three remaining sides of length 4. Return false.')],
    [[sticks] for sticks in ([1], [1,1], [1,1,1], [1,1,1,1], [2,2,2,2], [1,1,1,2],
      [1,1,1,5], [2,2,2,2,2,2], [1,1,1,1,2,2], [3,3,3,3], [1,2,3,4,5,6,7,8],
      [2,2,2,2,3,3,3,3,4], [1,1,2,2,2,2,3,3,6,6])],
    SQUARE, ['def make_square(matchsticks):\n    return sum(matchsticks)%4==0\n',
      'def make_square(matchsticks):\n    target=sum(matchsticks)/4\n    sides=[0]*4\n    for stick in sorted(matchsticks,reverse=True):\n        for i in range(4):\n            if sides[i]+stick<=target:\n                sides[i]+=stick\n                break\n        else: return False\n    return len(set(sides))==1\n'],
    ['Checks only perimeter divisibility, ignoring impossible side assignments.', 'Commits to the first fitting side without backtracking.'],
    square_oracle, random_square,
    ['After checking divisibility, the target side length is total/4.',
     'Place longer sticks first and recursively try every side that has enough remaining capacity.',
     'After placing a stick, recurse on the next index; undo failed choices. Equal side totals are interchangeable.',
     'Memoize the next index and sorted side totals to merge symmetric states. Using every stick under four capacity limits forces equality.'],
    'Each complete assignment is a partition of sticks into four side buckets. Exhaustively trying feasible '
    'buckets preserves all solutions; sorting and symmetry reduce repeated work but do not make a greedy '
    'commitment. The independent oracle instead builds subset masks that complete one side before starting '
    'another. This is four-way partition, not the existing two-way equal-subset problem.',
    'O(4^n) worst case', 'O(4^n) memoized states plus O(n) recursion', difficulty=6,
    stress=[([[10**8]*4], True), ([[1]*15], False), ([[1]*12+[2,2,4]], True),
            ([[4]*12+[8,8,8]], False)]),
474: entry('largest_binary_subset', [('strs','list[str]'),('m','int'),('n','int')], 'int',
    ['strings','dynamic-programming','knapsack'],
    ['1 <= strs.length <= 600; each binary string has length 1..100; 1 <= m,n <= 100.',
     'Select the maximum number of array entries using at most m zeros AND at most n ones in total.',
     'Each index can be chosen once. Repeated equal strings at different indices are separate choices. Budgets need not be used exactly.'],
    [([['10','0001','111001','1','0'],5,3], 'Choose 10,0001,1,0: four entries consume five zeros and three ones. The 111001 entry alone has too many ones.'),
     ([['0','0','1'],2,1], 'All three indices fit. The two identical zero strings are distinct available entries, not one reusable item.')],
    [args for args in ([['0'],1,1], [['1'],1,1], [['01'],1,1], [['00'],1,1],
      [['0'],3,2], [['0','0'],2,1], [['10','0','1'],1,1], [['11','00'],1,1],
      [['000','1'],2,2], [['1','1','0'],1,2], [['10','10','10'],2,2], [['001','01','1'],3,2])],
    BUDGETS, [BUDGETS.replace('range(m, zeros-1, -1)', 'range(zeros, m+1)').replace('range(n, ones-1, -1)', 'range(ones, n+1)'),
              BUDGETS.replace('for word in strs:', 'for word in set(strs):')],
    ['Updates capacities upward, allowing the same array entry to be reused.', 'Deduplicates equal strings and loses distinct selectable indices.'],
    budgets_oracle, random_budgets,
    ['Each string costs two resources and contributes one selected item.',
     'Use a table indexed by available zeros and ones, storing the maximum item count.',
     'For each string cost (z,o), update both capacity loops backward with 1+dp[zeros-z][ones-o].',
     'Backward updates read the previous item layer, including strings with zero cost in one resource. Do not deduplicate entries.'],
    'For each entry the optimum either skips it or takes it from a state with both resource costs removed. '
    'Descending capacities implement this 0/1 choice without reusing the same entry. Repeated strings '
    'remain separate items. The oracle enumerates index subsets and counts their literal zeros and ones.',
    'O(total characters + len(strs)*m*n)', 'O(m*n)', difficulty=6,
    stress=[([['0']*300+['1']*300,100,100],200), ([['0'*100]*600,100,100],1),
            ([['01'*50]*600,100,100],2)]),
475: entry('minimum_heater_radius', [('houses','list[int]'),('heaters','list[int]')], 'int',
    ['arrays','sorting','binary-search'],
    ['1 <= houses.length,heaters.length <= 30,000; positions are integers in 1..1,000,000,000.',
     'All heaters use the same radius. Every house must be within that distance of at least one heater.',
     'Positions can be unsorted or repeated. Return the smallest nonnegative radius; heaters need not coincide with houses.'],
    [([[1,2,3],[2]], 'Radius 1 reaches both endpoint houses from the heater at 2. Radius 0 misses them.'),
     ([[1,5],[2]], 'Distances to the only heater are 1 and 3. The shared radius must be 3, not the smaller or average distance.')],
    [[a,b] for a,b in (([1],[1]),([1],[2]),([2],[1]),([2],[1,3]),([1,4],[1,4]),
      ([3,1,2],[3,1]),([10],[1,9]),([1],[2,8]),([1,1,5],[1,1,4]),([2,6,10],[3,7]),
      ([1,2],[10]),([10,11],[1,2]))],
    HEATERS, ['def minimum_heater_radius(houses,heaters):\n    from bisect import bisect_left\n    ordered=sorted(heaters)\n    return max(abs(h-ordered[max(0,bisect_left(ordered,h)-1)]) for h in houses)\n',
      HEATERS.replace('answer = 0', "answer = float('inf')").replace('answer = max(answer, distance)', 'answer = min(answer, distance)')],
    ['Checks only the left neighbor even when a right heater is closer.', 'Returns the best-covered house distance instead of covering every house.'],
    heaters_oracle, random_heaters,
    ['A house only needs its nearest heater, but the shared radius must work for the worst-covered house.',
     'Sort heater positions and binary-search each house insertion point.',
     'Take the smaller distance to the predecessor and successor where present; maximize that distance over all houses.',
     'No heater farther left or right can beat the nearest neighbor on that side. Handle houses outside both ends without indexing past the list.'],
    'The closest heater determines the minimum radius needed by one house. Taking the maximum of these '
    'requirements is both necessary and sufficient for all houses. Sorted predecessor/successor search '
    'avoids comparing every pair. The oracle explicitly measures every house-heater distance.',
    'O(H log H + N log H)', 'O(H)', difficulty=5,
    stress=[([list(range(1,30001)),[1,30000]],14999),
            ([[10**9]*30000,list(range(1,30001))],10**9-30000),
            ([[1]*30000,[1]*30000],0)]),
}
BATCH[472]['comparator'] = 'unordered'
BATCH[472]['prerequisites'] = ['strings', 'dynamic-programming']
