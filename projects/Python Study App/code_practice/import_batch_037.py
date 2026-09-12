"""Multiset enumeration, recursive scrambling, basin flooding and capacity search."""
from collections import deque
from functools import lru_cache
from itertools import combinations, permutations
from .import_batch_003 import entry


def four_oracle(args):
    nums,target = args
    return [list(row) for row in sorted({tuple(sorted(row)) for row in combinations(nums,4) if sum(row)==target})]


def concat_oracle(args):
    s,words = args
    width,length = len(words[0]),len(words)*len(words[0])
    return [start for start in range(len(s)-length+1)
            if sorted(s[i:i+width] for i in range(start,start+length,width)) == sorted(words)]


@lru_cache(maxsize=128)
def permutation_rows(values):
    return tuple(sorted(set(permutations(values))))


def permutation_oracle(args):
    return [list(row) for row in permutation_rows(tuple(args[0]))]


@lru_cache(maxsize=256)
def scramble_language(text):
    if len(text)==1:
        return frozenset([text])
    answers = set()
    for split in range(1,len(text)):
        for left in scramble_language(text[:split]):
            for right in scramble_language(text[split:]):
                answers.update((left+right,right+left))
    return frozenset(answers)


def scramble_oracle(args):
    return args[1] in scramble_language(args[0])


def water_oracle(args):
    grid = args[0]
    rows,cols = len(grid),len(grid[0])
    total = 0
    # Flood the exterior at every integer layer; no heap or minimax recurrence.
    for level in range(1,max(map(max,grid))+1):
        low = {(r,c) for r in range(rows) for c in range(cols) if grid[r][c]<level}
        reached = {(r,c) for r,c in low if r in (0,rows-1) or c in (0,cols-1)}
        queue = deque(reached)
        while queue:
            r,c = queue.popleft()
            for neighbor in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if neighbor in low and neighbor not in reached:
                    reached.add(neighbor)
                    queue.append(neighbor)
        total += len(low-reached)
    return total


def split_oracle(args):
    nums,k = args
    return min(max(sum(nums[a:b]) for a,b in zip((0,)+cuts,cuts+(len(nums),)))
               for cuts in combinations(range(1,len(nums)),k-1))


def slices_oracle(args):
    nums = args[0]
    return sum(len({nums[i]-nums[i-1] for i in range(start+1,end)})==1
               for start in range(len(nums)) for end in range(start+3,len(nums)+1))


def third_oracle(args):
    values = sorted(set(args[0]),reverse=True)
    return values[2] if len(values)>=3 else values[0]


def random_four(rng):
    nums = [rng.randint(-10,10) for _ in range(rng.randint(1,14))]
    target = sum(rng.sample(nums,4)) if len(nums)>=4 and rng.random()<.6 else rng.randint(-40,40)
    return [nums,target]


def random_concat(rng):
    width = rng.randint(1,4)
    words = [''.join(rng.choice('ab') for _ in range(width)) for _ in range(rng.randint(1,5))]
    text = ''.join(rng.choice('ab') for _ in range(rng.randint(1,25)))
    if rng.random()<.6:
        shuffled = rng.sample(words,len(words))
        at = rng.randrange(len(text)+1)
        text = text[:at]+''.join(shuffled)+text[at:]
    return [text,words]


def random_permutation(rng):
    return [[rng.randint(-3,3) for _ in range(rng.randint(1,6))]]


def random_scramble(rng):
    text = ''.join(rng.choice('abcd') for _ in range(rng.randint(1,6)))
    def scramble(part):
        if len(part)==1:
            return part
        cut = rng.randrange(1,len(part))
        left,right = scramble(part[:cut]),scramble(part[cut:])
        return left+right if rng.random()<.5 else right+left
    kind = rng.randrange(3)
    other = scramble(text) if kind==0 else ''.join(rng.sample(text,len(text))) if kind==1 else ''.join(rng.choice('abcd') for _ in text)
    return [text,other]


def random_water(rng):
    rows,cols = rng.randint(1,6),rng.randint(1,6)
    return [[[rng.randint(0,5) for _ in range(cols)] for _ in range(rows)]]


def random_split(rng):
    nums = [rng.randint(0,20) for _ in range(rng.randint(1,10))]
    return [nums,rng.randint(1,len(nums))]


def random_slices(rng):
    return [[rng.randint(-5,5) for _ in range(rng.randint(1,20))]]


def random_third(rng):
    return [[rng.choice([-2**31,2**31-1,rng.randint(-10,10)]) for _ in range(rng.randint(1,50))]]


FOUR = '''\
def four_sum(nums, target):
    values = sorted(nums)
    result = []
    for first in range(len(values)-3):
        if first and values[first] == values[first-1]:
            continue
        for second in range(first+1,len(values)-2):
            if second > first+1 and values[second] == values[second-1]:
                continue
            left, right = second+1, len(values)-1
            while left < right:
                total = values[first]+values[second]+values[left]+values[right]
                if total < target:
                    left += 1
                elif total > target:
                    right -= 1
                else:
                    result.append([values[first],values[second],values[left],values[right]])
                    left, right = left+1, right-1
                    while left < right and values[left] == values[left-1]:
                        left += 1
                    while left < right and values[right] == values[right+1]:
                        right -= 1
    return result
'''

CONCAT = '''\
def concatenation_indices(s, words):
    from collections import Counter
    needed = Counter(words)
    width, count = len(words[0]), len(words)
    result = []
    for offset in range(width):
        left, used = offset, 0
        seen = Counter()
        for right in range(offset,len(s)-width+1,width):
            word = s[right:right+width]
            if word not in needed:
                seen.clear()
                left, used = right+width, 0
                continue
            seen[word] += 1
            used += 1
            while seen[word] > needed[word]:
                seen[s[left:left+width]] -= 1
                left += width
                used -= 1
            if used == count:
                result.append(left)
    return result
'''

PERMUTATION = '''\
def unique_number_permutations(nums):
    from collections import Counter
    counts = Counter(nums)
    values = sorted(counts)
    path, answers = [], []
    def visit():
        if len(path) == len(nums):
            answers.append(path.copy())
            return
        for value in values:
            if counts[value]:
                counts[value] -= 1
                path.append(value)
                visit()
                path.pop()
                counts[value] += 1
    visit()
    return answers
'''

SCRAMBLE = '''\
def is_scramble(s1, s2):
    from collections import Counter
    from functools import cache
    @cache
    def matches(first, second, width):
        left, right = s1[first:first+width], s2[second:second+width]
        if left == right:
            return True
        if Counter(left) != Counter(right):
            return False
        for split in range(1,width):
            if matches(first,second,split) and matches(first+split,second+split,width-split):
                return True
            if matches(first,second+width-split,split) and matches(first+split,second,width-split):
                return True
        return False
    return matches(0,0,len(s1))
'''

WATER = '''\
def trapped_water_grid(height_map):
    from heapq import heappop, heappush
    rows, cols = len(height_map), len(height_map[0])
    seen = set()
    boundary = []
    for row in range(rows):
        for col in range(cols):
            if row in (0,rows-1) or col in (0,cols-1):
                seen.add((row,col))
                heappush(boundary,(height_map[row][col],row,col))
    water = 0
    while boundary:
        level,row,col = heappop(boundary)
        for r,c in ((row-1,col),(row+1,col),(row,col-1),(row,col+1)):
            if 0<=r<rows and 0<=c<cols and (r,c) not in seen:
                seen.add((r,c))
                height = height_map[r][c]
                water += max(0,level-height)
                heappush(boundary,(max(level,height),r,c))
    return water
'''

SPLIT = '''\
def split_array_largest_sum(nums, k):
    low, high = max(nums), sum(nums)
    while low < high:
        capacity = (low+high)//2
        groups, subtotal = 1, 0
        for value in nums:
            if subtotal+value > capacity:
                groups += 1
                subtotal = 0
            subtotal += value
        if groups <= k:
            high = capacity
        else:
            low = capacity+1
    return low
'''

SLICES = '''\
def arithmetic_slices(nums):
    total = ending = 0
    for index in range(2,len(nums)):
        if nums[index]-nums[index-1] == nums[index-1]-nums[index-2]:
            ending += 1
        else:
            ending = 0
        total += ending
    return total
'''

THIRD = '''\
def third_maximum(nums):
    top = []
    for value in nums:
        if value not in top:
            top.append(value)
            top.sort(reverse=True)
            if len(top) > 3:
                top.pop()
    return top[2] if len(top)==3 else top[0]
'''


def bowl(size,height,gap=False):
    grid = [[height if r in (0,size-1) or c in (0,size-1) else 0
             for c in range(size)] for r in range(size)]
    if gap:
        grid[size//2][0] = 0
    return grid


BATCH = {
18: entry('four_sum',[('nums','list[int]'),('target','int')],'list[list[int]]',
    ['arrays','two-pointers','sorting'],
    ['1 <= nums.length <= 200; -10^9 <= nums[i], target <= 10^9.',
     'Use four distinct indices. Equal values at different indices may be used.',
     'Return each value quadruplet once; quadruplets and their values may appear in any order.'],
    [([[1,0,-1,0,-2,2],0],'Three distinct value quadruplets sum to 0. The two zeros are separate input elements.'),
     ([[2,2,2,2,2],8],'Any four of the five indices give [2,2,2,2], so return that value quadruplet only once.')],
    [[v,t] for v,t in [([1],4),([1,2,3],6),([0,0,0,0],0),([0,0,0,0],1),
      ([-2,-1,0,1,2],0),([1,2,3,4],10),([4,3,2,1],10),([-5,-4,-3,-2,-1],-14),
      ([-3,-1,0,2,4,5],2),([1,1,1,2,2,2],6),([0]*6,0),([-10**9,-10**9,10**9,10**9],0)]],
    FOUR,[FOUR.replace('values = sorted(nums)','values = sorted(set(nums))'),
          FOUR.replace('left, right = second+1, len(values)-1','left, right = second, len(values)-1')],
    ['Discards repeated input values that may be needed at separate indices.',
     'Reuses the second fixed index as a moving index.'],
    four_oracle,random_four,
    ['Distinct indices do not require distinct values.',
     'Sort, fix two indices, then search the remaining suffix from both ends.',
     'Move left or right according to the four-value sum; skip equal fixed choices and equal endpoints after a match.',
     'Two fixed loops plus a linear two-pointer scan cost O(n^3). Preserve multiplicities and emit each value quadruplet once.'],
    'Sorting makes the remaining pair sum monotone. Keep first < second < left < right. A small sum '
    'needs a larger left value; a large sum needs a smaller right value. On equality record the values '
    'and skip repeated choices. Sorting a set would destroy needed occurrences. Python integers safely '
    'handle intermediate sums beyond signed 32-bit limits.',
    'O(n^3)','O(n), excluding output',difficulty=6,
    stress=[([[10**9]*100+[-10**9]*100,0],[[-10**9,-10**9,10**9,10**9]]),([list(range(100,300)),-1],[])]),
30: entry('concatenation_indices',[('s','str'),('words','list[str]')],'list[int]',
    ['strings','hash-maps','sliding-window'],
    ['1 <= s.length <= 10,000; 1 <= words.length <= 5,000.',
     'All words have equal length w, 1 <= w <= 30; all text is lowercase English letters.',
     'Use every word exactly its given number of times, contiguously. Return all zero-based starts in any order.'],
    [(['barfoothefoobarman',['foo','bar']],'At index 0, barfoo uses bar then foo; at index 9, foobar uses foo then bar.'),
     (['wordgoodgoodgoodbestword',['word','good','best','word']],
      'No window contains two copies of word plus one good and one best. Matching only the distinct words is insufficient.')],
    [[s,w] for s,w in [('a',['a']),('a',['b']),('aaa',['a','a']),('aaaa',['aa']),
      ('ababa',['ab','ba']),('xbarfoo',['bar','foo']),('foofoo',['foo','foo']),
      ('barfoofoobarthefoobarman',['bar','foo','the']),('aaaaab',['aa','ab']),
      ('wordgoodgoodgoodbestword',['word','good','best','good']),('foobar',['foobar','foobar']),('ababab',['ab','ab'])]],
    CONCAT,[CONCAT.replace('range(width):','range(1):'),CONCAT.replace('while seen[word] > needed[word]:','while seen[word] > 1:')],
    ['Checks only offsets aligned with index zero.', 'Limits words to one copy even when repeated copies are required.'],
    concat_oracle,random_concat,
    ['Equal word lengths let you scan whole blocks.',
     'Maintain a sliding window for each offset modulo word length and track multiplicities.',
     'Reset at unknown words; shrink while the newest word is overrepresented; record left when all words are used.',
     'Each block enters and leaves once. Python slicing/hashing costs O(w), giving O((|s|+|words|)*w) time.'],
    'Each answer belongs to one alignment. Keep a contiguous window whose word counts do not exceed '
    'the requested multiset. Unknown tokens reset it; excess copies shrink it from the left. When '
    'the window contains len(words) tokens, every required count must match. Do not skip overlapping '
    'answers. At most u distinct word keys are retained, each of length w.',
    'O((|s| + |words|) * w)','O(u * w), excluding output',difficulty=8,
    stress=[(['a'*10000,['a']*5000],list(range(5001))),(['b'*10000,['a'*30]*5000],[])]),
47: entry('unique_number_permutations',[('nums','list[int]')],'list[list[int]]',
    ['arrays','backtracking','recursion'],
    ['1 <= nums.length <= 8; -10 <= nums[i] <= 10.',
     'Use every occurrence exactly once, including repeated values.',
     'Return each distinct ordered list once. Outer order is arbitrary; order inside a permutation matters.'],
    [([[1,1,2]],'Only [1,1,2], [1,2,1], and [2,1,1] are distinct: exchanging the two 1s creates no new row.'),
     ([[0,-1]],'Both [0,-1] and [-1,0] are required. Reversing a row changes its permutation.')],
    [[v] for v in ([0],[1],[-10],[2,2],[2,1],[1,2,3],[3,2,1],[0,0,0],
                   [-1,-1,0,1],[1,1,2,2],[1,2,1,2,1],[-10,0,10])],
    PERMUTATION,["def unique_number_permutations(nums):\n    from itertools import permutations\n    return [list(row) for row in permutations(nums)]\n",
                 PERMUTATION.replace('counts[value] += 1','pass  # omitted restoration')],
    ['Treats equal-valued positions as different choices and emits duplicate rows.',
     'Forgets to restore a used count, losing sibling branches.'],
    permutation_oracle,random_permutation,
    ['Track the remaining count of each integer.',
     'Choose an available value, recurse, and restore its count afterward.',
     'At length n append a path copy; otherwise decrement a positive count, append, recurse, pop, and increment.',
     'Frequency-based branches emit distinct ordered permutations once. Copy completed paths before undoing choices.'],
    'Values, rather than equal-valued positions, label branches. The remaining count vector records '
    'the unused multiset. A complete path consumes every occurrence, and different choice sequences '
    'produce different rows. Signed and multidigit integers remain indivisible values: this is not '
    'the original string-permutation contract. Unique-only source 46 is covered by this numeric contract.',
    'O(n * n!) worst case','O(n), excluding output',difficulty=6,
    stress=[([list(range(8))],permutation_oracle([list(range(8))])),([[10]*8],[[10]*8])]),
87: entry('is_scramble',[('s1','str'),('s2','str')],'bool',
    ['strings','recursion','dynamic-programming'],
    ['1 <= s1.length == s2.length <= 30; lowercase English letters only.',
     'Recursively split into two nonempty parts, optionally swap them, and transform each part.',
     'Return whether some sequence works. An arbitrary anagram need not be a scramble.'],
    [(['great','rgeat'],'Split gr | eat, swap g | r inside the first part, and leave eat unchanged.'),
     (['abcde','caebd'],'The letters match, but no recursive split-and-optional-swap tree produces this arrangement.')],
    [[a,b] for a,b in [('a','a'),('a','b'),('ab','ba'),('ab','ab'),('abc','bca'),('abc','cab'),
      ('aab','aba'),('aabb','baba'),('abcd','bdac'),('abcd','badc'),('abcde','edcba'),('aaaa','aaab')]],
    SCRAMBLE,["def is_scramble(s1,s2):\n    return sorted(s1)==sorted(s2)\n",
              SCRAMBLE.replace('range(1,width):','[width//2]:')],
    ['Accepts every anagram without checking the split-tree restriction.',
     'Tries only the midpoint, although legal splits can occur anywhere.'],
    scramble_oracle,random_scramble,
    ['Character counts are necessary but insufficient.',
     'Match two equal-length intervals; try every split with child intervals kept or swapped.',
     'Memoize (start1,start2,length). Accept equal text, reject unequal counts, otherwise test both pairings at every split.',
     'There are O(n^3) interval-pair states and O(n) split choices each: O(n^4) time, O(n^3) memo space.'],
    'The root of any scramble splits the first interval somewhere. Its children match either the '
    'corresponding second intervals or their exchanged positions. Testing all splits and both '
    'pairings is complete. Every recursive call shortens the interval; caching avoids repeated '
    'work. Text equality and multiset checks prune states but cannot replace structural checks.',
    'O(n^4)','O(n^3)',difficulty=8,
    stress=[(['abcdefghijklmnopqrstuvwxyzabcd','dcbazyxwvutsrqponmlkjihgfedcba'],True),
            (['a'*29+'b','a'*28+'bb'],False)]),
407: entry('trapped_water_grid',[('height_map','list[list[int]]')],'int',
    ['matrices','graphs','heaps','flood-fill'],
    ['1 <= rows, columns <= 200; the matrix is rectangular.',
     '0 <= height_map[r][c] <= 20,000; each cell has unit area.',
     'Water escapes through the boundary along four edge-adjacent directions, not diagonally. Return total volume.'],
    [([[[1,4,3,1,3,2],[3,2,1,3,2,4],[2,3,3,2,3,1]]],
      'Interior cells at row 1, columns 1, 2, and 4 (zero-based) hold 1, 2, and 1 units: total 4.'),
     ([bowl(4,3,True)],'The zero-height gap in the left boundary connects all interior zeros to the outside, so no water remains.')],
    [[g] for g in ([[0]],[[4]],[[3,0,3]],[[3],[0],[3]],[[3,3],[3,0]],
      bowl(3,3),bowl(4,3),bowl(5,2),bowl(3,5,True),
      [[5,5,1,5],[5,0,0,5],[5,5,5,5]],[[3,3,3],[3,5,3],[3,3,3]],[[4,4,4,4],[4,1,2,4],[4,4,4,4]])],
    WATER,[WATER.replace('max(level,height),r,c','height,r,c'),
           WATER.replace('row in (0,rows-1) or col in (0,cols-1)','row in (0,rows-1)')],
    ['Propagates raw height instead of effective water level, allowing a basin to drain through itself.',
     'Seeds only top and bottom edges, missing left/right outlets.'],
    water_oracle,random_water,
    ['An escape path can wind around obstacles; immediate walls alone do not determine water depth.',
     'Start from every boundary cell and expand from the lowest effective frontier using a min-heap.',
     'Pop level; for each unseen neighbor h add max(0,level-h), mark seen, and push max(level,h).',
     'The lowest frontier fixes the smallest escape level. Carry that effective level, not just the terrain height.'],
    'Flood inward from the exterior through the lowest frontier. Any lower escape route would '
    'already have been processed when a new cell is reached, so its surface is max(frontier,terrain). '
    'Add the difference and propagate the effective surface. Seed each boundary once. The iterative '
    'flood practices connected-region reasoning without overflowing Python recursion on 40,000 cells.',
    'O(m*n log(m*n))','O(m*n)',difficulty=8,
    stress=[([bowl(200,20000)],198*198*20000),([bowl(200,20000,True)],0)]),
410: entry('split_array_largest_sum',[('nums','list[int]'),('k','int')],'int',
    ['arrays','binary-search','greedy'],
    ['1 <= nums.length <= 1,000; 0 <= nums[i] <= 10^6.',
     '1 <= k <= min(50, nums.length). Use exactly k nonempty contiguous parts.',
     'Preserve input order. Return the smallest achievable largest part sum, not the cuts.'],
    [([[7,2,5,10,8],2],'Split [7,2,5] | [10,8]. Their sums are 14 and 18; no split has largest sum below 18.'),
     ([[1,2,3,4,5],2],'Split [1,2,3] | [4,5], with sums 6 and 9. Equal element counts need not be optimal.')],
    [[v,k] for v,k in [([0],1),([10],1),([1,2,3],1),([1,2,3],3),([0,0,0],2),
      ([1,1,1,1],3),([10,1,1,1],2),([1,1,1,10],2),([0,5,0,5,0],3),
      ([2,3,1,2,4,3],3),([1000000,0,1000000],2),([3,3,3,3,3],2)]],
    SPLIT,["def split_array_largest_sum(nums,k):\n    return max(max(nums),(sum(nums)+k-1)//k)\n",
           SPLIT.replace('if groups <= k:','if groups == k:')],
    ['Assumes maximum-item and average-load lower bounds are always achievable by contiguous cuts.',
     'Rejects capacities needing fewer than k groups even though extra splits remain possible.'],
    split_oracle,random_split,
    ['Test whether a proposed maximum sum is feasible.',
     'Greedily fill each part until the next item would exceed that capacity.',
     'Binary-search max(nums)..sum(nums); at most k greedy groups means feasible, otherwise increase capacity.',
     'Nonnegative items make feasibility monotone and let you split existing groups to reach exactly k without increasing the largest sum.'],
    'For fixed capacity, extending each part as far as possible minimizes required groups. If that '
    'minimum is at most k, subdivide groups until there are exactly k nonempty pieces: nonnegative '
    'items cannot increase any sum. Feasible capacities form an upper interval for binary search. '
    'Zeros require no exception. This is not arbitrary bin packing; parts must be contiguous.',
    'O(n log(sum(nums)+1))','O(1)',difficulty=8,
    stress=[([[1000000]*1000,50],20000000),([[0]*1000,50],0)]),
413: entry('arithmetic_slices',[('nums','list[int]')],'int',
    ['arrays','dynamic-programming'],
    ['1 <= nums.length <= 5,000; -1,000 <= nums[i] <= 1,000.',
     'Count contiguous subarrays of length at least three with equal consecutive differences.',
     'Zero/negative differences and overlapping slices count. Arbitrary subsequences do not.'],
    [([[1,2,3,4]],'The three slices are [1,2,3], [2,3,4], and [1,2,3,4].'),
     ([[1,3,5,8,11]],'Only [1,3,5] (difference 2) and [5,8,11] (difference 3) qualify: answer 2.')],
    [[v] for v in ([1],[1,2],[1,1,1],[3,2,1],[1,2,4],[0,0,0,0],
      [1,3,5,7,9],[5,1,-3,-7],[1,2,3,8,9,10],[1,2,3,4,7,10],[-1000,0,1000],[1,2,1,2,1])],
    SLICES,[SLICES.replace('total += ending','total += int(ending > 0)'),
            SLICES.replace('ending = 0\n        total','pass\n        total')],
    ['Counts only length-three windows, omitting longer slices.',
     'Carries an old run through a changed difference instead of resetting.'],
    slices_oracle,random_slices,
    ['Count slices by their ending index.',
     'An unchanged difference extends every previous slice and creates a new length-three slice.',
     'If the last two differences match, ending += 1; otherwise ending = 0. Add ending to total.',
     'Each slice has exactly one right endpoint, so summing endpoint counts avoids omissions and double counting.'],
    'Maintain how many arithmetic slices end at the previous index. An unchanged difference extends '
    'them all and creates one new three-value slice. A changed difference cannot extend any of them, '
    'so reset. Constant and decreasing runs use the same difference-equality invariant.',
    'O(n)','O(1)',difficulty=5,
    stress=[([[0]*5000],4999*4998//2),([[-1000,1000]*2500],0)]),
414: entry('third_maximum',[('nums','list[int]')],'int',
    ['arrays','hash-maps'],
    ['1 <= nums.length <= 10,000; -2^31 <= nums[i] <= 2^31-1.',
     'Rank distinct values. With fewer than three distinct values, return the maximum.',
     'Target O(n) time with only three retained candidates.'],
    [([[3,2,1]],'The distinct descending values are 3, 2, 1, so the third maximum is 1.'),
     ([[2,2,3,1]],'Repeating 2 does not change its rank; the third distinct maximum is still 1.')],
    [[v] for v in ([1],[1,2],[2,2],[1,1,2,2],[-1,-2,-3],[3,1,2,4],[5,4,3,2,1],
      [0,0,-1,-2],[-2**31],[-2**31,0,2**31-1],[2**31-1,2**31-1,0],[-5,-4,-3,-2,-1])],
    THIRD,["def third_maximum(nums):\n    values=sorted(nums,reverse=True)\n    return values[2] if len(values)>=3 else values[0]\n",
           THIRD.replace('else top[0]','else top[-1]')],
    ['Ranks occurrences rather than distinct values.', 'Returns the smaller candidate when only two distinct values exist.'],
    third_oracle,random_third,
    ['Only the three greatest distinct values can affect the answer.',
     'Ignore retained duplicates, insert a new value, and discard the fourth largest.',
     'Keep at most three descending unique candidates; return the third if present, otherwise the first.',
     'Sorting at most four values is constant work. Avoid sentinel values that collide with signed-32-bit inputs.'],
    'After each item, retain the largest min(3,distinct count) values. Repetition cannot promote a '
    'discarded smaller value. This invariant supports local deduplication and constant storage. '
    'All-negative inputs and the minimum signed integer remain ordinary values, not special markers.',
    'O(n)','O(1)',difficulty=3,
    stress=[([[2**31-1]*9998+[0,-2**31]],-2**31),([[1,2]*5000],2)]),
}

BATCH[18]['comparator'] = 'unordered_nested'
BATCH[30]['comparator'] = 'unordered'
BATCH[47]['comparator'] = 'unordered'
BATCH[30]['prerequisites'] = ['hash-maps','sliding-window']
BATCH[87]['prerequisites'] = ['recursion','dynamic-programming']
BATCH[407]['prerequisites'] = ['graphs','heaps']
BATCH[410]['prerequisites'] = ['binary-search','greedy']
