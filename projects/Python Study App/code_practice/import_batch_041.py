"""Geometry, resource matching, move semantics and strict string contracts."""
from collections import deque
from itertools import combinations, permutations, product
import re
import string

from .import_batch_003 import entry


def boomerang_oracle(args):
    return sum((a[0]-b[0])**2+(a[1]-b[1])**2==(a[0]-c[0])**2+(a[1]-c[1])**2
               for a,b,c in permutations(args[0],3))


def missing_oracle(args):
    return sorted(set(range(1,len(args[0])+1))-set(args[0]))


def arrows_oracle(args):
    intervals = args[0]
    covers = {sum(1<<i for i,(a,b) in enumerate(intervals) if a<=point<=b)
              for point in {x for interval in intervals for x in interval}}
    full = (1<<len(intervals))-1
    queue,seen = deque([(0,0)]),{0}
    while queue:
        mask,distance = queue.popleft()
        if mask==full:
            return distance
        for cover in covers:
            following = mask | cover
            if following not in seen:
                seen.add(following)
                queue.append((following,distance+1))


def moves_oracle(args):
    """Literal n-1 increments on small normalized states, not the sum/min formula.

    Translation and permutation do not change future costs. An optimal path need
    not widen the initial range: omit a currently maximal entry until equal.
    """
    nums = args[0]
    initial = tuple(sorted(value-min(nums) for value in nums))
    bound = max(initial)
    queue,seen = deque([(initial,0)]),{initial}
    while queue:
        state,distance = queue.popleft()
        if state[-1]==0:
            return distance
        for omitted in range(len(nums)):
            following = [value+int(i!=omitted) for i,value in enumerate(state)]
            smallest = min(following)
            normalized = tuple(sorted(value-smallest for value in following))
            if normalized[-1]<=bound and normalized not in seen:
                seen.add(normalized)
                queue.append((normalized,distance+1))


def four_oracle(args):
    return sum(sum(values)==0 for values in product(*args))


def cookies_oracle(args):
    needs,sizes = args
    assigned = [-1]*len(sizes)
    def augment(child,seen):
        for cookie,size in enumerate(sizes):
            if cookie in seen or size<needs[child]:
                continue
            seen.add(cookie)
            if assigned[cookie]<0 or augment(assigned[cookie],seen):
                assigned[cookie] = child
                return True
        return False
    return sum(augment(child,set()) for child in range(len(needs)))


def pattern_oracle(args):
    return any(a<c<b for a,b,c in combinations(args[0],3))


def repeat_oracle(args):
    text = args[0]
    return any(len(text)%width==0 and text[:width]*(len(text)//width)==text
               for width in range(1,len(text)//2+1))


def hamming_oracle(args):
    return sum(a!=b for a,b in zip(f'{args[0]:031b}',f'{args[1]:031b}'))


def median_oracle(args):
    nums = args[0]
    return min(sum(abs(value-target) for value in nums) for target in range(min(nums),max(nums)+1))


def wrap_oracle(args):
    text = args[0]
    base = string.ascii_lowercase*(2+len(text)//26)
    return len({text[i:j] for i in range(len(text)) for j in range(i+1,len(text)+1) if text[i:j] in base})


def ip_oracle(args):
    decimal = r'(?:0|[1-9][0-9]?|1[0-9]{2}|2[0-4][0-9]|25[0-5])'
    if re.fullmatch(decimal+r'(?:\.'+decimal+r'){3}',args[0]):
        return 'IPv4'
    if re.fullmatch(r'[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){7}',args[0]):
        return 'IPv6'
    return 'Neither'


def random_points(rng):
    return [[list(point) for point in rng.sample(list(product(range(-3,4),repeat=2)),rng.randint(1,8))]]


def random_missing(rng):
    n = rng.randint(1,30)
    return [[rng.randint(1,n) for _ in range(n)]]


def random_arrows(rng):
    intervals = []
    for _ in range(rng.randint(1,7)):
        a,b = sorted(rng.sample(range(-5,7),2))
        intervals.append([a,b])
    return [intervals]


def random_moves(rng):
    offset = rng.randint(-5,5)
    return [[offset+rng.randint(0,3) for _ in range(rng.randint(1,4))]]


def random_four(rng):
    n = rng.randint(1,5)
    return [[rng.randint(-3,3) for _ in range(n)] for _ in range(4)]


def random_cookies(rng):
    return [[rng.randint(1,6) for _ in range(rng.randint(1,6))],
            [rng.randint(1,6) for _ in range(rng.randint(0,6))]]


def random_pattern(rng):
    return [[rng.randint(-6,6) for _ in range(rng.randint(1,12))]]


def random_repeat(rng):
    text = ''.join(rng.choice('abc') for _ in range(rng.randint(1,6)))
    return [text*rng.randint(2,5) if rng.random()<.5 else ''.join(rng.choice('abc') for _ in range(rng.randint(1,20))) ]


def random_hamming(rng):
    return [rng.randint(0,2**31-1),rng.randint(0,2**31-1)]


def random_median(rng):
    return [[rng.randint(-5,5) for _ in range(rng.randint(1,12))]]


def random_wrap(rng):
    if rng.random()<.5:
        start = rng.randrange(26)
        return [''.join(string.ascii_lowercase[(start+i)%26] for i in range(rng.randint(1,30))) ]
    return [''.join(rng.choice('abcxyz') for _ in range(rng.randint(1,20)))]


def random_ip(rng):
    choice = rng.randrange(5)
    if choice==0:
        return ['.'.join(str(rng.randint(0,255)) for _ in range(4))]
    if choice==1:
        return [':'.join(''.join(rng.choice(string.hexdigits) for _ in range(rng.randint(1,4))) for _ in range(8))]
    if choice==2:
        return ['.'.join(str(rng.randint(0,999)).zfill(rng.randint(1,4)) for _ in range(rng.randint(3,5)))]
    if choice==3:
        return [':'.join(''.join(rng.choice('0123aAFg') for _ in range(rng.randint(0,5))) for _ in range(rng.randint(6,9)))]
    return [''.join(rng.choice(string.ascii_letters+string.digits+'.:') for _ in range(rng.randint(0,45)))]


BOOMERANG = '''\
def count_boomerangs(points):
    total = 0
    for x,y in points:
        counts = {}
        for a,b in points:
            distance = (x-a)**2+(y-b)**2
            previous = counts.get(distance,0)
            total += 2*previous
            counts[distance] = previous+1
    return total
'''
MISSING = '''\
def disappeared_numbers(nums):
    for value in nums:
        index = abs(value)-1
        nums[index] = -abs(nums[index])
    return [i+1 for i,value in enumerate(nums) if value>0]
'''
ARROWS = '''\
def minimum_balloon_arrows(points):
    ordered = sorted(points,key=lambda interval:interval[1])
    arrows = 0
    endpoint = None
    for start,end in ordered:
        if endpoint is None or start>endpoint:
            arrows += 1
            endpoint = end
    return arrows
'''
MOVES = '''\
def minimum_n_minus_one_moves(nums):
    return sum(nums)-len(nums)*min(nums)
'''
FOUR = '''\
def four_array_zero_sum_count(nums1, nums2, nums3, nums4):
    counts = {}
    for a in nums1:
        for b in nums2:
            counts[a+b] = counts.get(a+b,0)+1
    return sum(counts.get(-c-d,0) for c in nums3 for d in nums4)
'''
COOKIES = '''\
def assign_cookies(g, s):
    needs = sorted(g)
    child = 0
    for size in sorted(s):
        if child<len(needs) and size>=needs[child]:
            child += 1
    return child
'''
PATTERN = '''\
def has_132_pattern(nums):
    stack = []
    middle = float('-inf')
    for value in reversed(nums):
        if value<middle:
            return True
        while stack and value>stack[-1]:
            middle = stack.pop()
        stack.append(value)
    return False
'''
REPEAT = '''\
def repeated_substring_pattern(s):
    prefix = [0]*len(s)
    for i in range(1,len(s)):
        length = prefix[i-1]
        while length and s[i]!=s[length]:
            length = prefix[length-1]
        if s[i]==s[length]:
            length += 1
        prefix[i] = length
    period = len(s)-prefix[-1]
    return prefix[-1]>0 and len(s)%period==0
'''
HAMMING = '''\
def hamming_distance(x, y):
    different = x^y
    count = 0
    while different:
        different &= different-1
        count += 1
    return count
'''
MEDIAN = '''\
def minimum_single_element_moves(nums):
    ordered = sorted(nums)
    median = ordered[len(ordered)//2]
    return sum(abs(value-median) for value in nums)
'''
WRAP = '''\
def unique_wraparound_substrings(s):
    longest = [0]*26
    run = 0
    for i,char in enumerate(s):
        run = run+1 if i and (ord(char)-ord(s[i-1]))%26==1 else 1
        index = ord(char)-97
        longest[index] = max(longest[index],run)
    return sum(longest)
'''
IP = '''\
def classify_ip_address(query_ip):
    if len(query_ip)>39:
        return 'Neither'
    if '.' in query_ip:
        parts = query_ip.split('.')
        if len(parts)==4 and all(1<=len(part)<=3 and all(c in '0123456789' for c in part)
                                and (len(part)==1 or part[0]!='0') and int(part)<=255 for part in parts):
            return 'IPv4'
    else:
        parts = query_ip.split(':')
        if len(parts)==8 and all(1<=len(part)<=4 and all(c in '0123456789abcdefABCDEF' for c in part) for part in parts):
            return 'IPv6'
    return 'Neither'
'''


BATCH = {
447: entry('count_boomerangs',[('points','list[list[int]]')],'int',['arrays','hash-maps','geometry'],
    ['1 <= points.length <= 500; all coordinate pairs are distinct; coordinates are integers in -10,000..10,000.',
     'Count ordered triples of distinct points (i,j,k) whose Euclidean distances from i to j and i to k are equal.',
     'Swapping j and k creates a different triple. Use squared distances to avoid floating-point rounding.'],
    [([[[0,0],[1,0],[2,0]]],'The middle point is equally far from the endpoints. Their two possible orders give 2 triples.'),
     ([[[0,0],[1,0],[0,1],[-1,0],[0,-1]]],'The center has four equal-distance neighbors, giving 4×3=12 triples. The four outer centers contribute 2 each, for 20 total.')],
    [[p] for p in ([[0,0]],[[0,0],[1,0]],[[0,0],[1,0],[1,1]],[[0,0],[2,0],[1,1]],
      [[0,0],[1,1],[2,2]],[[0,0],[1,0],[3,0]],[[0,0],[1,0],[2,0],[3,0]],
      [[0,0],[1,1],[0,1],[1,0]],[[-1,0],[0,0],[1,0]],[[0,0],[2,2],[-2,-2]],
      [[-10000,-10000],[10000,10000],[10000,-10000]],[[-2,1],[0,1],[2,1],[0,3]])],
    BOOMERANG,[BOOMERANG.replace('total += 2*previous','total += previous'),
               BOOMERANG.replace('(x-a)**2+(y-b)**2','abs(x-a)+abs(y-b)')],
    ['Counts unordered neighbor pairs instead of ordered triples.', 'Uses Manhattan distance rather than Euclidean distance.'],
    boomerang_oracle,random_points,
    ['Fix the first point and group all other points by squared distance.',
     'A distance group of size c contributes c*(c-1) ordered choices.',
     'As each neighbor joins a group of size c, add 2*c new triples, then increment that group.',
     'Repeat for every center. Distinct points mean the center is alone at distance zero and contributes nothing.'],
    'Every triple has a unique center and distance group. A new neighbor forms two ordered pairs '
    'with each earlier neighbor in its group. Exact squared integer distances preserve Euclidean '
    'equality, including extreme and negative coordinates. The oracle enumerates all ordered triples.',
    'O(n^2)','O(n)',difficulty=5,
    stress=[([[[i,0] for i in range(500)]],2*sum(min(i,499-i) for i in range(500)))]),
448: entry('disappeared_numbers',[('nums','list[int]')],'list[int]',['arrays','index-marking'],
    ['1 <= n == nums.length <= 100,000; each value lies in 1..n.',
     'Return every missing value from 1..n exactly once, in any order. Repeated input values are allowed.',
     'Input mutation is permitted. The follow-up targets O(n) time and O(1) extra space, excluding the returned list.'],
    [([[4,3,2,7,8,2,3,1]],'Values 1,2,3,4,7,8 appear; only 5 and 6 from 1..8 are missing.'),
     ([[2,2,4,4]],'Duplicates still mark just values 2 and 4 as present. Return missing values [1,3], not their zero-based positions.')],
    [[v] for v in ([1],[1,1],[2,2],[1,2],[2,1],[3,3,3],[4,4,4,4],[2,2,2],
                   [1,2,2],[1,3,3],[2,3,4,4],[1,1,1,1,1])],
    MISSING,[MISSING.replace('-abs(nums[index])','-nums[index]'),MISSING.replace('[i+1 for','[i for')],
    ['Toggles signs so repeated values can erase a presence mark.', 'Returns zero-based positions instead of missing values.'],
    missing_oracle,random_missing,
    ['Every possible value has a corresponding slot in the input array.',
     'Use the sign at value-1 as its presence mark; read absolute values because some entries are already marked.',
     'Set nums[abs(value)-1] to its negative absolute value. Then collect positive slots, adding one to their indices.',
     'Marking must be idempotent: a repeated value must leave its slot negative. No separate set is needed.'],
    'The source range maps values to valid indices. Negative signs record presence without '
    'destroying magnitudes, so later original values remain recoverable via abs. Positive slots '
    'are exactly unvisited values. A set-difference oracle independently computes the answer.',
    'O(n)','O(1), excluding output',difficulty=3,
    stress=[([[1]*100000],list(range(2,100001))),([list(range(100000,0,-1))],[])]),
452: entry('minimum_balloon_arrows',[('points','list[list[int]]')],'int',['intervals','greedy','sorting'],
    ['1 <= points.length <= 100,000; -2^31 <= start < end <= 2^31-1.',
     'Each balloon is a closed interval. One arrow at x bursts every balloon with start <= x <= end.',
     'Return the fewest arrow positions needed; touching endpoints can share an arrow.'],
    [([[[10,16],[2,8],[1,6],[7,12]]],'Arrows at 6 and 11 cover all four balloons. One position cannot lie inside all four.'),
     ([[[1,2],[2,3],[3,4],[4,5]]],'Arrows at 2 and 4 suffice because endpoints are included. The four touching intervals do not all share one common position.')],
    [[v] for v in (
      [[0,1]],[[1,2],[2,3]],[[1,2],[3,4]],[[1,10],[2,3],[4,5]],[[1,10],[2,9],[3,8]],
      [[0,1],[0,1]],[[-3,-1],[-1,1]],[[-5,-4],[-3,-2],[-1,0]],
      [[-2**31,2**31-1]],[[5,6],[1,2],[3,4]],[[0,2],[1,3],[2,4]],[[0,2],[2,4],[4,6]])],
    ARROWS,[ARROWS.replace('start>endpoint','start>=endpoint'),ARROWS.replace('interval[1]','interval[0]')],
    ['Treats touching closed intervals as requiring separate arrows.', 'Chooses the first-starting interval endpoint instead of the earliest-ending endpoint.'],
    arrows_oracle,random_arrows,
    ['The earliest-ending uncovered balloon must receive an arrow before its right endpoint.',
     'Place that arrow at its right endpoint to cover as many later balloons as possible.',
     'Sort by end; when start exceeds the last arrow position, add an arrow at this end.',
     'An exchange argument moves an optimal arrow rightward to the earliest end without losing any balloon it needs to cover.'],
    'Any solution must cover the earliest-ending balloon. Moving its covering arrow to that '
    'endpoint preserves coverage of other intervals sharing the arrow, so the greedy choice is '
    'safe. Merely chaining overlaps is insufficient: all balloons assigned one arrow need a '
    'common intersection. The oracle searches endpoint hitting sets with a coverage-state BFS.',
    'O(n log n)','O(n)',difficulty=5,
    stress=[([[[2*i,2*i+1] for i in range(100000)]],100000),([[[i,i+1] for i in range(100000)]],50000)]),
453: entry('minimum_n_minus_one_moves',[('nums','list[int]')],'int',['arrays','math','invariants'],
    ['1 <= nums.length <= 100,000; -10^9 <= nums[i] <= 10^9; the minimum answer fits a signed 32-bit integer.',
     'One move increments exactly n-1 entries by 1, leaving one entry unchanged.',
     'Return the minimum number of moves to make every entry equal. This is not the single-element increment/decrement variant.'],
    [([[1,2,3]],'Three moves suffice: [1,2,3]→[2,3,3]→[3,4,3]→[4,4,4]. Each move changes two entries.'),
     ([[-1,1,3]],'Incrementing two entries at a time needs 6 moves. A median-based single-element solution would solve a different problem.')],
    [[v] for v in ([0],[1],[-1],[1,1],[0,1],[1,2],[1,1,2],[1,2,2],[0,0,3],[3,0,0],[-2,-1,0],[2,2,2,2])],
    MOVES,['def minimum_n_minus_one_moves(nums):\n    return max(nums)-min(nums)\n',
           'def minimum_n_minus_one_moves(nums):\n    target=sorted(nums)[len(nums)//2]\n    return sum(abs(v-target) for v in nums)\n'],
    ['Uses only the range, ignoring how many entries need relative changes.', 'Applies the median formula for a different move operation.'],
    moves_oracle,random_moves,
    ['Adding one to all entries does not affect whether they are equal.',
     'Incrementing n-1 entries is equivalent, up to a shared translation, to decrementing the omitted entry.',
     'Reduce every value to the minimum: sum the differences from min(nums).',
     'The answer is sum(nums)-n*min(nums). A one-entry or already-equal array requires zero moves.'],
    'Subtract a common increment after every move: only the omitted entry decreases relative '
    'to the rest. With decrements alone, the greatest common target is the initial minimum. '
    'Every difference must be removed, yielding the stated formula. The oracle literally '
    'explores small normalized n-1-increment states, rather than evaluating the formula.',
    'O(n)','O(1)',difficulty=5,
    stress=[([[-10**9,10**9]],2*10**9),([[0]*50000+[40000]*50000],2*10**9),([[10**9]*100000],0)]),
454: entry('four_array_zero_sum_count',[(f'nums{i}','list[int]') for i in range(1,5)],'int',['arrays','hash-maps'],
    ['All four arrays have the same length n, 1 <= n <= 200; values lie in -2^28..2^28.',
     'Choose one index independently from each array and count tuples whose four values sum to zero.',
     'Equal values at different indices count separately. Return a count, not unique quadruplet values from one array.'],
    [([[1,2],[-2,-1],[-1,2],[0,2]],'Index tuples (0,0,0,1) and (1,1,0,0) are the two zero-sum choices.'),
     ([[0,0],[0,0],[0,0],[0,0]],'Each of four arrays offers two distinct indices: 2^4=16 tuples, although all selected values are zero.')],
    [v for v in ([[0],[0],[0],[0]],[[1],[1],[-1],[-1]],[[1],[2],[3],[4]],
      [[-1],[-1],[1],[1]],[[0],[1],[0],[-1]],[[1,1],[-1,-1],[0,0],[0,0]],
      [[1,2],[3,4],[-4,-5],[0,1]],[[2,2],[2,2],[-2,-2],[-2,-2]],
      [[-2,0],[0,2],[-1,1],[-1,1]],[[2**28],[-2**28],[2**28],[-2**28]],
      [[1],[0],[0],[0]],[[0,1],[0,1],[0,-1],[0,-1]])],
    FOUR,[FOUR.replace('counts.get(a+b,0)+1','1'),FOUR.replace('counts.get(-c-d,0)','counts.get(c+d,0)')],
    ['Stores pair sums as a set, losing index multiplicities.', 'Looks up the same pair sum rather than its additive inverse.'],
    four_oracle,random_four,
    ['Split the sum into two independent pairs.',
     'Count every nums1+nums2 sum, then look up the negative of each nums3+nums4 sum.',
     'Accumulate pair frequencies, not just membership; add that frequency for every right-pair index choice.',
     'There are n^2 pairs per side instead of n^4 explicit tuples. Multiplicities are preserved by frequency addition.'],
    'Each four-index tuple has a unique left and right pair. Their sums must be opposites; '
    'frequency lookup counts all compatible left pairs, including repeated values at distinct '
    'indices. The oracle enumerates the Cartesian product of four small arrays.',
    'O(n^2) expected','O(n^2)',difficulty=5,
    stress=[([([0]*200) for _ in range(4)],200**4),([[2**28]*200]*4,0)]),
455: entry('assign_cookies',[('g','list[int]'),('s','list[int]')],'int',['arrays','greedy','sorting'],
    ['1 <= g.length <= 30,000; 0 <= s.length <= 30,000; every size and requirement is in 1..2^31-1.',
     'Each child receives at most one cookie and each cookie serves at most one child. Size >= requirement satisfies a child.',
     'Return the maximum number satisfied; cookies cannot be combined to meet a larger requirement.'],
    [([[1,2,3],[1,1]],'Only the child requiring 1 can be satisfied. The two size-1 cookies cannot be combined for another child.'),
     ([[2,1],[1]],'Give the only cookie to the second child. The input order does not force servicing the harder child first.')],
    [[g,s] for g,s in [([1],[]),([1],[1]),([2],[1]),([1],[2]),([1,1],[1]),([1,1],[1,1]),
      ([1,2],[2,1]),([3,2,1],[1,1,1]),([2,3],[3]),([3],[1,2]),([2**31-1],[2**31-1]),([1],[1,2,3])]],
    COOKIES,[COOKIES.replace('size>=needs[child]','size>needs[child]'),COOKIES.replace('needs = sorted(g)','needs = list(g)')],
    ['Rejects cookies that exactly meet a requirement.', 'Keeps children in input order, letting a demanding child block easier matches.'],
    cookies_oracle,random_cookies,
    ['Use the smallest adequate cookie for the least-demanding remaining child.',
     'Sort requirements and sizes, then advance the child pointer whenever a cookie is adequate.',
     'Skip undersized cookies; otherwise assign this cookie once and move to the next child.',
     'Exchanging a larger assigned cookie for a smaller adequate one cannot reduce the remaining matching options.'],
    'The least-demanding child can use any cookie another child could use. Assigning the '
    'smallest adequate cookie therefore leaves maximum flexibility for harder children. Each '
    'cookie is examined once after sorting. The independent oracle finds a maximum bipartite '
    'matching through augmenting paths instead of the greedy ordering.',
    'O(g log g + s log s)','O(g+s)',difficulty=3,
    stress=[([list(range(30000,0,-1)),list(range(1,30001))],30000),([[2]*30000,[1]*30000],0)]),
456: entry('has_132_pattern',[('nums','list[int]')],'bool',['arrays','stacks','monotonic-stack'],
    ['1 <= nums.length <= 200,000; -10^9 <= nums[i] <= 10^9.',
     'Find indices i<j<k with nums[i]<nums[k]<nums[j]. Both value inequalities are strict.',
     'The three entries form a subsequence and need not be adjacent. Return a boolean.'],
    [([[1,2,3,4]],'Increasing values cannot place a smaller third value after a larger second value, so no 132 pattern exists.'),
     ([[1,4,0,2]],'Indices 0,1,3 give values 1,4,2. This valid pattern skips the intervening zero.')],
    [[v] for v in ([1],[1,2],[1,3,2],[3,1,2],[1,2,1],[1,2,2],[3,1,4,2],[-1,3,2,0],
                   [4,3,2,1],[0,0,0],[3,5,0,3,4],[-10**9,10**9,0])],
    PATTERN,[PATTERN.replace('value<middle','value<=middle'),
             'def has_132_pattern(nums):\n    return any(nums[i]<nums[i+2]<nums[i+1] for i in range(len(nums)-2))\n'],
    ['Allows the low and middle values to be equal.', 'Checks only adjacent triples, missing patterns with gaps.'],
    pattern_oracle,random_pattern,
    ['Search right-to-left for a valid middle value that already has a larger value before it.',
     'A decreasing stack stores candidates for the large value; popped values become candidates for the middle.',
     'If the current value is below the saved middle, succeed. Pop smaller stack values, saving the last popped one, then push current.',
     'Every index enters and leaves the stack at most once. Strict comparisons reject equal-value false patterns.'],
    'When a value pops a smaller stack entry, their index order forms the large/middle pair. '
    'Keep the best middle threshold while moving left; a later lower value completes the pattern. '
    'The monotone stack avoids trying every triple. An independent oracle enumerates all '
    'three-index choices in small arrays, preserving order and strict inequalities.',
    'O(n)','O(n)',difficulty=6,
    stress=[([list(range(200000))],False),([list(range(200000,0,-1))],False),([[0,200000]+list(range(199998))],True)]),
459: entry('repeated_substring_pattern',[('s','str')],'bool',['strings','string-matching'],
    ['1 <= s.length <= 10,000; lowercase English letters only.',
     'The entire string must equal at least two copies of one nonempty substring. A shared prefix/suffix alone is not enough.'],
    [(['abab'],'Two copies of ab produce the whole string.'),
     (['ababa'],'Although aba is both a prefix and suffix, a length-2 period does not divide length 5; partial final copies do not count.')],
    [[s] for s in ('a','aa','aaa','ab','aba','abcabcabc','abcabcxabc','aaaaab','zzzzzz','abaaba','abcdabcd','abac')],
    REPEAT,[REPEAT.replace('prefix[-1]>0 and len(s)%period==0','prefix[-1]>0'),
            'def repeated_substring_pattern(s):\n    return len(s)%2==0 and s[:len(s)//2]==s[len(s)//2:]\n'],
    ['Accepts any nonempty border even when the implied period does not divide the length.', 'Checks only two equal halves, omitting odd repetition counts.'],
    repeat_oracle,random_repeat,
    ['A repeated string has a proper prefix that is also a suffix.',
     'Compute the longest border with a prefix-function table, then consider period n-border.',
     'Build prefix lengths with fallback links. Return true only if the final border is nonzero and n is divisible by n-border.',
     'Divisibility ensures complete copies; a single-character string has no proper border and cannot repeat twice.'],
    'The prefix function finds the longest proper border in linear time. Its complement is '
    'the smallest candidate period; it describes full repetition precisely when it divides the '
    'string length. The oracle explicitly tries every possible block length and concatenates copies.',
    'O(n)','O(n)',difficulty=3,
    stress=[(['ab'*5000],True),(['a'*9999+'b'],False),(['a'*10000],True)]),
461: entry('hamming_distance',[('x','int'),('y','int')],'int',['math','bit-manipulation'],
    ['0 <= x,y <= 2^31-1. Compare binary positions, including leading zero positions as needed.',
     'Return the number of differing bit positions, not numeric distance or the difference in counts of one-bits.'],
    [([1,4],'Binary 0001 and 0100 differ in two positions, so return 2.'),
     ([7,8],'Binary 0111 and 1000 differ in all four positions even though the integers are only one apart.')],
    [[a,b] for a,b in ((0,0),(0,1),(1,1),(3,1),(3,3),(0,2**31-1),(2**30,0),(2**30,2**30),
                       (2**31-1,2**31-2),(5,10),(15,0),(8,1))],
    HAMMING,['def hamming_distance(x,y):\n    return (x|y).bit_count()\n',
             'def hamming_distance(x,y):\n    return abs(x.bit_count()-y.bit_count())\n'],
    ['Uses OR, counting positions where both inputs already have a one.', 'Compares only one-bit totals and loses their positions.'],
    hamming_oracle,random_hamming,
    ['XOR marks exactly the bit positions that disagree.',
     'Count the one-bits of x XOR y.',
     'While different is nonzero, clear its lowest one-bit with different &= different-1 and increment a counter.',
     'Each step removes exactly one differing bit. The 31-bit nonnegative input bound keeps the loop finite.'],
    'XOR is one exactly when its operands differ at that bit. Clearing the lowest set bit '
    'counts disagreements without converting to decimal or conflating positions. The oracle '
    'compares two independently padded binary strings position by position.',
    'O(log(max(x,y)+1))','O(1)',difficulty=3,
    stress=[([1431655765,715827882],31)]),
462: entry('minimum_single_element_moves',[('nums','list[int]')],'int',['arrays','sorting','math'],
    ['1 <= nums.length <= 100,000; -10^9 <= nums[i] <= 10^9; the answer fits a signed 32-bit integer.',
     'One move increments OR decrements exactly one entry by 1. Return the fewest moves to make all entries equal.',
     'This differs from incrementing n-1 entries per move; any median is an optimal target.'],
    [([[1,2,3]],'Increment 1 to 2 and decrement 3 to 2: two single-entry moves suffice.'),
     ([[1,1,10]],'Target 1 costs 9 moves. Targeting the mean, 4, would cost 3+3+6=12.')],
    [[v] for v in ([0],[1],[-1],[1,1],[0,1],[1,2],[1,2,2],[0,0,3],[3,0,0],[-2,-1,0],
                   [2,2,2,2],[1,10,2,9])],
    MEDIAN,[MEDIAN.replace('median = ordered[len(ordered)//2]','median = sum(nums)//len(nums)'),
            MEDIAN.replace('median = ordered[len(ordered)//2]','median = min(nums)')],
    ['Targets the arithmetic mean rather than minimizing absolute deviations.', 'Uses the minimum, confusing single-entry moves with the n-1 increment operation.'],
    median_oracle,random_median,
    ['Moving every value to target t costs the sum of its absolute distances from t.',
     'Pair the smallest and largest values; any target between them has the same cost for that pair.',
     'Sort, choose a middle value, and sum absolute differences from it.',
     'The nested pair intervals meet at a median. For even lengths any point between the middle two is optimal.'],
    'Absolute-distance cost decreases toward a median and increases after passing it. Pairing '
    'extremes gives another proof: each pair pays at least its gap, and a median achieves every '
    'pair lower bound simultaneously. The oracle tries every integer target in small input ranges.',
    'O(n log n)','O(n)',difficulty=5,
    stress=[([[-10**9,10**9]],2*10**9),([[0]*50000+[40000]*50000],2*10**9),([[10**9]*100000],0)]),
467: entry('unique_wraparound_substrings',[('s','str')],'int',['strings','dynamic-programming'],
    ['1 <= s.length <= 100,000; lowercase English letters only.',
     'Count distinct nonempty substring VALUES present in the infinite cyclic alphabet ...xyzabcdefghijklmnopqrstuvwxyz...',
     'Consecutive z→a is valid. Repeated occurrences of the same substring count once.'],
    [(['a'],'The only nonempty substring is a, which occurs in the cyclic alphabet.'),
     (['zab'],'The six distinct valid substrings are z,a,b,za,ab,zab; z→a crosses the alphabet boundary.')],
    [[s] for s in ('b','aa','abc','z','za','yza','zabc','az','cac','abca','abzab',string.ascii_lowercase)],
    WRAP,[WRAP.replace('(ord(char)-ord(s[i-1]))%26==1','ord(char)-ord(s[i-1])==1'),
          WRAP.replace('longest[index] = max(longest[index],run)','longest[index] += run')],
    ['Breaks a valid run at z→a.', 'Counts occurrences rather than distinct substring values.'],
    wrap_oracle,random_wrap,
    ['Within the cyclic alphabet, a substring is determined by its final letter and length.',
     'Track the longest valid consecutive run ending at each of the 26 letters.',
     'Extend the run when character differences are 1 modulo 26; otherwise reset to 1. Maximize the record for this final letter.',
     'If the longest run ending at a letter has length L, exactly L distinct lengths are represented for that ending. Sum the 26 maxima.'],
    'All shorter suffixes of a valid run are valid. For a fixed final letter and length there '
    'is only one cyclic-alphabet string, so the maximum run length counts distinct values '
    'without storing substrings or recounting repeated occurrences. The oracle enumerates a '
    'set of substrings and checks membership in a sufficiently long literal cyclic alphabet.',
    'O(n)','O(1)',difficulty=5,
    stress=[([(string.ascii_lowercase*3847)[:100000]],26*100000-325),(['a'*100000],1)]),
468: entry('classify_ip_address',[('query_ip','str')],'str',['strings','parsing'],
    ['Inputs contain only English letters, digits, dots, and colons; malformed lengths and empty input may occur.',
     'IPv4 requires exactly four decimal groups in 0..255 with no leading zeros except the single digit 0.',
     'IPv6 requires exactly eight nonempty groups of 1–4 hexadecimal characters. Leading zeros and either letter case are allowed.',
     'For this problem, compressed :: notation and IPv4-embedded IPv6 are NOT accepted. Return IPv4, IPv6, or Neither.'],
    [(['172.16.254.1'],'Four decimal groups lie in 0..255 and have no leading zeros, so return IPv4.'),
     (['2001:db8:85a3:0:0:8A2E:0370:7334'],'Eight hexadecimal groups are present. Uppercase letters and the leading zero in 0370 are allowed for IPv6.')],
    [[s] for s in ('','0.0.0.0','255.255.255.255','256.1.2.3','01.2.3.4','1.2.3','1.2.3.4.5',
      '1..2.3','.1.2.3','1.2.3.','::1','1:2:3:4:5:6:7:8','1:2:3:4:5:6:7:8:9',
      '1:2:3:4:5:6:7:g','12345:1:2:3:4:5:6:7','0000:0000:0000:0000:0000:0000:0000:0000',
      '1:2:3:4:5:6:192.168.0.1')],
    IP,[IP.replace("and (len(part)==1 or part[0]!='0') ",''),
        "def classify_ip_address(query_ip):\n    import ipaddress\n    try: return 'IPv'+str(ipaddress.ip_address(query_ip).version)\n    except ValueError: return 'Neither'\n"],
    ['Accepts zero-padded decimal IPv4 groups.', 'Uses general IP-address parsing that permits compressed or embedded IPv6 forms forbidden by this exercise.'],
    ip_oracle,random_ip,
    ['Validate the exact group structure before accepting individual numeric groups.',
     'Use separate decimal and hexadecimal rules, especially for leading zeros and group counts.',
     'IPv4: four 1–3-digit groups, no padding, value<=255. IPv6: eight 1–4-character hex groups, none empty.',
     'Do not accept real-world IPv6 shorthand here. The exercise specifies the full eight-group notation only.'],
    'Group-count and character checks rule out empty fields, mixed notation, and invalid '
    'digits. IPv4 disallows leading zeros while IPv6 permits them. Full IPv6 notation is at '
    'most 39 characters, so longer inputs can be rejected immediately. The oracle uses two '
    'independent full-string regular expressions with explicit decimal ranges and hex grammar.',
    'O(n)','O(n)',difficulty=5,
    stress=[(['1'*100000],'Neither'),(['.'*100000],'Neither')]),
}
BATCH[448]['comparator'] = 'unordered'
