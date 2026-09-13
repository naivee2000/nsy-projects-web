"""Run boundaries, signed pair counts, recursive expressions and ordered traversal."""
from itertools import product
from math import comb

from .import_batch_003 import entry


def ones_oracle(args):
    return max(map(len, ''.join(map(str,args[0])).split('0')))


def pairs_oracle(args):
    nums=args[0]
    return sum(nums[i]>2*nums[j] for j in range(len(nums)) for i in range(j))


def target_oracle(args):
    nums,target=args
    return sum(sum(sign*value for sign,value in zip(signs,nums))==target
               for signs in product((-1,1),repeat=len(nums)))


def poison_oracle(args):
    times,duration=args
    return len({second for start in times for second in range(start,start+duration)})


def greater_oracle(args):
    queries,nums=args
    return [next((v for v in nums[nums.index(q)+1:] if v>q),-1) for q in queries]


def diagonal_oracle(args):
    matrix=args[0]
    cells=[(r,c) for r in range(len(matrix)) for c in range(len(matrix[0]))]
    cells.sort(key=lambda p:(sum(p), p[0] if sum(p)%2 else -p[0]))
    return [matrix[r][c] for r,c in cells]


def random_ones(rng):return [[rng.randrange(2) for _ in range(rng.randint(1,30))]]
def random_pairs(rng):return [[rng.choice([-2**31,2**31-1,-3,-2,-1,0,1,2,3]) for _ in range(rng.randint(1,16))]]
def random_target(rng):return [[rng.randrange(6) for _ in range(rng.randint(1,10))],rng.randint(-30,30)]
def random_poison(rng):return [sorted(rng.randrange(31) for _ in range(rng.randint(1,12))),rng.randrange(11)]
def random_greater(rng):
    nums=rng.sample(range(21),rng.randint(1,10))
    return [rng.sample(nums,rng.randint(1,len(nums))),nums]
def random_diagonal(rng):
    rows,cols=rng.randint(1,6),rng.randint(1,6)
    return [[[rng.randint(-5,5) for _ in range(cols)] for _ in range(rows)]]


ONES='''\
def max_consecutive_ones(nums):
    best=run=0
    for value in nums:
        run=run+1 if value==1 else 0
        best=max(best,run)
    return best
'''
PAIRS='''\
def count_reverse_pairs(nums):
    values=nums[:]
    scratch=[0]*len(values)
    def count(left,right):
        if right-left<2:
            return 0
        middle=(left+right)//2
        result=count(left,middle)+count(middle,right)
        j=middle
        for i in range(left,middle):
            while j<right and values[i]>2*values[j]:
                j+=1
            result+=j-middle
        i,j,out=left,middle,left
        while i<middle and j<right:
            if values[i]<=values[j]:
                scratch[out]=values[i]
                i+=1
            else:
                scratch[out]=values[j]
                j+=1
            out+=1
        while i<middle:
            scratch[out]=values[i]
            i+=1
            out+=1
        while j<right:
            scratch[out]=values[j]
            j+=1
            out+=1
        values[left:right]=scratch[left:right]
        return result
    return count(0,len(values))
'''
TARGET='''\
def target_sum_ways(nums,target):
    from functools import cache
    suffix=[0]*(len(nums)+1)
    for i in range(len(nums)-1,-1,-1):
        suffix[i]=suffix[i+1]+nums[i]
    @cache
    def ways(index,remaining):
        if abs(remaining)>suffix[index]:
            return 0
        if index==len(nums):
            return int(remaining==0)
        return ways(index+1,remaining-nums[index])+ways(index+1,remaining+nums[index])
    return ways(0,target)
'''
POISON='''\
def poisoned_seconds(time_series,duration):
    total=duration
    for i in range(1,len(time_series)):
        total+=min(duration,time_series[i]-time_series[i-1])
    return total
'''
GREATER='''\
def next_greater_elements(nums1,nums2):
    following={}
    pending=[]
    for value in nums2:
        while pending and pending[-1]<value:
            following[pending.pop()]=value
        pending.append(value)
    return [following.get(value,-1) for value in nums1]
'''
DIAGONAL='''\
def diagonal_traverse(mat):
    rows,cols=len(mat),len(mat[0])
    result=[]
    for diagonal in range(rows+cols-1):
        low=max(0,diagonal-cols+1)
        high=min(rows-1,diagonal)
        indices=range(low,high+1) if diagonal%2 else range(high,low-1,-1)
        for row in indices:
            result.append(mat[row][diagonal-row])
    return result
'''

BATCH={
485:entry('max_consecutive_ones',[('nums','list[int]')],'int',['arrays'],
    ['1 <= nums.length <= 100,000; every entry is 0 or 1.',
     'Return the longest contiguous run of ones. Zeros break runs; no value may be flipped or deleted.'],
    [([[1,1,0,1,1,1]],'The zero separates runs of lengths 2 and 3. Return 3, not the total of five ones.'),
     ([[1,1,0,1]],'The longest run has length 2 even though the final run has length 1. Remember the best earlier run.')],
    [[a] for a in ([0],[1],[0,0],[1,1],[0,1],[1,0],[1,0,1],[1,1,0],[0,1,1],
      [0,0,1,1,0,1],[1,1,1,0,1,1],[0,1,0,1,0],[1,1,0,0,1,1],[1,0,0,0,1])],
    ONES,['def max_consecutive_ones(nums):\n    return sum(nums)\n',ONES.replace('return best','return run')],
    ['Counts disconnected runs together.', 'Returns the final run instead of the longest run.'],
    ones_oracle,random_ones,
    ['The current run ends whenever a zero appears.', 'Keep both the current run length and the best length seen anywhere.',
     'Increment run on a one; reset it on a zero; update best after each value.',
     'The running maximum is needed because the longest run need not touch the last array position.'],
    'The current counter is exactly the length of the all-one suffix of the processed prefix. '
    'A separate maximum preserves earlier completed runs. This differs from Max Consecutive Ones II: '
    'that exercise allows a zero flip, while this one does not. The oracle splits a binary string at zeros.',
    'O(n)','O(1)',difficulty=3,
    stress=[([[1]*100000],100000),([[0]*100000],0),([[1,0]*50000],1),([[0]*49999+[1]*50001],50001)]),
493:entry('count_reverse_pairs',[('nums','list[int]')],'int',['arrays','divide-and-conquer','recursion','binary-search'],
    ['1 <= nums.length <= 50,000; -2^31 <= nums[i] <= 2^31-1.',
     'Count index pairs i < j with nums[i] > 2*nums[j]. The inequality is strict and depends on original index order.',
     'Negative numbers and repeated values are allowed. Use exact integer arithmetic for twice a signed 32-bit value.'],
    [([[1,3,2,3,1]],'Only index pairs (1,4) and (3,4) satisfy value > twice the later value. The ordinary inversion (1,2), with values 3 and 2, does not count because 3 is not greater than 4.'),
     ([[-1,-1]],'There is one pair: -1 > 2*(-1) = -2. Equal negative values can count, unlike ordinary inversions.')],
    [[a] for a in ([0],[1],[-1],[2,1],[3,1],[1,3],[0,0],[-2,-1],[-1,-2],
      [2,4,3,5,1],[2**31-1,-2**31],[-2**31,2**31-1],[-2**31,-2**31],[5,4,3,2,1],[1,2,3,4,5])],
    PAIRS,[PAIRS.replace('values[i]>2*values[j]','values[i]>values[j]'),
           PAIRS.replace('values[i]>2*values[j]','values[i]>=2*values[j]')],
    ['Counts ordinary inversions rather than the doubled-value condition.', 'Counts equality even though the doubled-value comparison must be strict.'],
    pairs_oracle,random_pairs,
    ['Split by original index so every left-half position precedes every right-half position.',
     'Once both halves are sorted, one forward pointer can count right values below half of each left value.',
     'Recursively count each half, count strict cross pairs using exact doubling, then merge the halves.',
     'Separate cross-pair counting from ordinary merge comparisons: the two predicates are different. Work on a copy to preserve the supplied input.'],
    'Merge-sort partitions preserve the i<j relation for cross pairs. Sorted halves make the '
    'counting pointer monotone even for negative values, and each merge level does linear work. '
    'Python integers preserve the doubled 32-bit boundary exactly. The independent oracle examines '
    'every original index pair literally, including equal negative values and strict-equality boundaries.',
    'O(n log n)','O(n)',difficulty=8,
    stress=[([[-1]*50000],50000*49999//2),([[0]*50000],0),
      ([[2**31-1]*25000+[-2**31]*25000],25000**2+25000*24999//2),
      ([list(range(50000,0,-1))],sum(max(50000-2*x,0) for x in range(1,50001)))]),
494:entry('target_sum_ways',[('nums','list[int]'),('target','int')],'int',['arrays','dynamic-programming','recursion'],
    ['1 <= nums.length <= 20; 0 <= nums[i] <= 1000; sum(nums) <= 1000; -1000 <= target <= 1000.',
     'Assign exactly one plus or minus sign to EACH array position. Return the number of assignments whose signed sum equals target.',
     'Equal values at different indices remain separate choices. +0 and -0 are different expressions, even though their numeric contributions agree.'],
    [([[1,1,1,1,1],3],'Exactly one of the five positions receives a minus sign, so there are five different expressions.'),
     ([[0,1],1],'Both +0+1 and -0+1 give 1. The zero doubles the number of expressions instead of disappearing.')],
    [([1],1),([1],-1),([1],0),([0],0),([0],1),([0,0],0),([1,1],0),([1,1],1),
     ([1,2,3],0),([2,2,2],2),([0,0,1],-1),([1000],1000),([1000],-1000),([1,2],1000),([1,2],-3)],
    TARGET,[TARGET.replace('from functools import cache','nums=[value for value in nums if value]\n    from functools import cache'),
      TARGET.replace('from functools import cache','nums=list(dict.fromkeys(nums))\n    from functools import cache')],
    ['Discards zeros, losing the two distinct sign choices for every zero.', 'Deduplicates equal input values even though signs are assigned to positions.'],
    target_oracle,random_target,
    ['At each index there are two sign choices, including when the value is zero.',
     'Cache the number of ways from an index to achieve a remaining signed sum.',
     'Add ways(i+1,remaining-nums[i]) and ways(i+1,remaining+nums[i]); at the end count one only for remaining zero.',
     'A suffix sum bounds the largest absolute contribution still possible. Memoization shares computation without merging distinct expression counts.'],
    'Recursive states track index and remaining target. The two outgoing branches count separate '
    'sign assignments even if they reach the same cached state. A suffix-sum bound safely prunes '
    'unreachable targets. With S=sum(nums), at most O(n*(S+1)) states are needed. '
    'The oracle independently enumerates every sign tuple and evaluates the resulting expression.',
    'O(n*(S+1)), S=sum(nums)','O(n*(S+1))',difficulty=5,
    stress=[([[0]*20,0],2**20),([[50]*20,0],comb(20,10)),([[0]*19+[1000],-1000],2**19),
            ([[1]*20,0],comb(20,10)),([[50]*20,1],0)]),
495:entry('poisoned_seconds',[('time_series','list[int]'),('duration','int')],'int',['arrays','intervals'],
    ['1 <= time_series.length <= 10,000; times are sorted in non-decreasing order and may repeat.',
     '0 <= time_series[i], duration <= 10,000,000. An attack at t covers inclusive seconds t through t+duration-1.',
     'An overlapping attack resets the timer. Count poisoned seconds once, not once for each attack; duration zero covers no seconds.'],
    [([[1,4],2],'The covered seconds are {1,2} and {4,5}. The gap at second 3 is not poisoned; total 4.'),
     ([[1,2],2],'The intervals cover {1,2} and {2,3}. Second 2 is shared, so the total is 3 rather than 4.')],
    [([0],0),([0],1),([5],3),([0,0],2),([0,1],0),([0,1],1),([0,2],2),([0,3],2),
     ([0,1,2],3),([1,1,1],4),([0,2,10],4),([0,0,3,3],2),([10,20],3),([0,100],100)],
    POISON,['def poisoned_seconds(time_series,duration):\n    return len(time_series)*duration\n',
      POISON.replace('total=duration','duration=max(0,duration-1)\n    total=duration')],
    ['Adds full durations for overlapping or repeated attacks.', 'Treats an inclusive duration as one second shorter.'],
    poison_oracle,random_poison,
    ['An attack contributes until either its timer expires or the next attack begins.',
     'Each gap contributes min(duration,gap); the final attack contributes a full duration.',
     'Start total=duration and add min(duration,time[i]-time[i-1]) for every later attack.',
     'Repeated times add zero, non-overlapping gaps add only duration, and duration zero makes every contribution zero.'],
    'Consecutive attacks divide the covered timeline into non-overlapping contributions. '
    'Capping each gap at duration avoids counting unpoisoned gaps, while using the gap avoids '
    'counting overlap twice. The small-input oracle explicitly forms the union of covered integer seconds.',
    'O(n)','O(1)',difficulty=3,
    stress=[([list(range(10000)),10**7],10009999),([[10**7]*10000,10**7],10**7),
      ([list(range(0,10**7,1000)),100],1000000),([list(range(10000)),0],0)]),
496:entry('next_greater_elements',[('nums1','list[int]'),('nums2','list[int]')],'list[int]',['arrays','stacks','hash-maps'],
    ['1 <= nums1.length <= nums2.length <= 1000; every value is in 0..10,000.',
     'Each array has unique values, and every nums1 value appears in nums2.',
     'For each nums1 value, return the FIRST strictly greater value to its right in nums2, or -1. Preserve nums1 query order; return values, not distances or indices.',
     'The follow-up target is O(len(nums1)+len(nums2)) time.'],
    [([[4,1,2],[1,3,4,2]],'4 and 2 have no greater value to their right; the first greater value after 1 is 3. Answers follow query order [4,1,2].'),
     ([[1,4],[1,4,2,5,3]],'After 1 the first greater value is 4, not the smaller-but-later 2. After 4, skip 2 and return 5.')],
    [([0],[0]),([1],[1,2]),([2],[1,2]),([1],[2,1]),([1],[1,5,3]),([3],[3,1,4]),
     ([2,0],[0,1,2,3]),([3,2,1],[3,2,1]),([1,2,3],[1,2,3]),([0,10],[10,0,5]),
     ([4,1],[1,4,3,2,5]),([2,4],[1,2,3,4]),([10000,0],[0,10000]),([0,5],[0,9,5,7])],
    GREATER,['def next_greater_elements(nums1,nums2):\n    return [min((v for v in nums2[nums2.index(q)+1:] if v>q),default=-1) for q in nums1]\n',
      'def next_greater_elements(nums1,nums2):\n    result=[]\n    for q in nums1:\n        i=nums2.index(q)\n        result.append(nums2[i+1] if i+1<len(nums2) and nums2[i+1]>q else -1)\n    return result\n'],
    ['Returns the smallest greater suffix value rather than the first one encountered.', 'Only checks the immediate neighbor and misses greater values beyond a dip.'],
    greater_oracle,random_greater,
    ['Keep values whose next greater value has not appeared yet.',
     'A decreasing stack lets a newly larger value resolve every smaller value waiting at its top.',
     'For each nums2 value, pop smaller pending values into a next-greater map, then push it. Look up nums1 in its own order.',
     'Each value is pushed and popped at most once; unresolved values map to -1. Uniqueness lets the value itself identify a position.'],
    'The decreasing stack contains unresolved earlier values. When a value is popped, the '
    'current value is the first greater one to its right because no intervening value could pop it. '
    'A map decouples scan order from query order. The oracle searches each queried suffix literally.',
    'O(len(nums1)+len(nums2))','O(len(nums2))',difficulty=3,
    stress=[([list(range(1000)),list(range(1000))],list(range(1,1000))+[-1]),
      ([list(range(1000)),list(range(999,-1,-1))],[-1]*1000),
      ([list(range(999,-1,-1)),list(range(1000))],[-1]+list(range(999,0,-1)))]),
498:entry('diagonal_traverse',[('mat','list[list[int]]')],'list[int]',['arrays','matrices'],
    ['The matrix is rectangular with 1 <= rows, columns <= 10,000 and rows*columns <= 10,000.',
     '-100,000 <= mat[r][c] <= 100,000. Return every value exactly once in alternating diagonal order.',
     'Start at the top-left cell. Traverse diagonals of equal row+column in increasing sum: even sums go upward/right, odd sums downward/left. Rectangles need not be square.'],
    [([[[1,2,3],[4,5,6],[7,8,9]]],'Diagonals are [1], [2,4], [7,5,3], [6,8], [9]. Reversing every other direction yields [1,2,4,7,5,3,6,8,9].'),
     ([[[1,2,3],[4,5,6]]],'The rectangular matrix yields [1,2,4,5,3,6]. Each diagonal stops at whichever matrix edge it reaches first.')],
    [[m] for m in ([[0]],[[1,2]],[[1],[2]],[[1,2],[3,4]],[[1,2,3,4]],[[1],[2],[3],[4]],
      [[1,2],[3,4],[5,6]],[[1,1,1],[1,1,1]],[[-1,0],[1,-2]],[[0,1,2,3],[4,5,6,7]],
      [[0,1],[2,3],[4,5],[6,7]],[[100000,-100000],[0,5]],[[1,2,3],[4,5,6],[7,8,9],[10,11,12]])],
    DIAGONAL,['def diagonal_traverse(mat):\n    return [value for row in mat for value in row]\n',
      DIAGONAL.replace('range(low,high+1) if diagonal%2 else range(high,low-1,-1)','range(low,high+1)')],
    ['Traverses rows instead of alternating diagonals.', 'Visits every diagonal in the same direction.'],
    diagonal_oracle,random_diagonal,
    ['Cells on the same diagonal have the same row+column sum.',
     'Visit sums in increasing order and reverse the row direction on alternate sums.',
     'For sum d, valid rows range from max(0,d-cols+1) to min(rows-1,d). Use descending rows for even d and ascending for odd d.',
     'These bounds handle one-row, one-column, and rectangular matrices without special square assumptions.'],
    'Enumerate diagonal sums and their valid row intervals. Their parity determines traversal '
    'direction; column is derived as sum-row. Every coordinate belongs to exactly one diagonal '
    'and is emitted once. The independent oracle sorts all coordinates by diagonal and parity-aware row keys.',
    'O(rows*columns)','O(1) auxiliary plus output',difficulty=5,
    stress=[([[[i for i in range(10000)]]],list(range(10000))),
      ([[[i] for i in range(10000)]],list(range(10000))),
      ([[[r*100+c for c in range(100)] for r in range(100)]],
       diagonal_oracle([[[r*100+c for c in range(100)] for r in range(100)]]))]),
}
BATCH[493]['prerequisites']=['arrays','binary-search','recursion']
# Kept as offline source fixtures for proved adaptations of existing originals,
# not registered or packaged as duplicate runnable exercises.
OVERLAP_SPECS={pid:BATCH.pop(pid) for pid in (495,496)}
