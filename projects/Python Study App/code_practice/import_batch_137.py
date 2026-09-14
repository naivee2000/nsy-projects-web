"""Hard-focused workbook batch 137."""

from functools import lru_cache
from math import gcd

from .import_batch_055 import entry


MOD=1_000_000_007


def paths_oracle(args):
    grid=args[0];rows=len(grid);columns=len(grid[0]);answer=0
    def walk(row,column):
        nonlocal answer
        answer+=1
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=row+dr,column+dc
            if 0<=nr<rows and 0<=nc<columns and grid[nr][nc]>grid[row][column]:walk(nr,nc)
    for row in range(rows):
        for column in range(columns):walk(row,column)
    return answer%MOD


def random_paths(rng):
    rows,columns=rng.randint(1,4),rng.randint(1,4)
    return [[[rng.randint(1,8) for _ in range(columns)] for _ in range(rows)]]


def squared_oracle(args):
    nums1,nums2,k1,k2=args;differences=[abs(a-b) for a,b in zip(nums1,nums2)]
    for _ in range(k1+k2):
        index=max(range(len(differences)),key=differences.__getitem__)
        if differences[index]==0:break
        differences[index]-=1
    return sum(value*value for value in differences)


def random_squared(rng):
    n=rng.randint(1,9);return [[rng.randint(0,30) for _ in range(n)],[rng.randint(0,30) for _ in range(n)],rng.randint(0,20),rng.randint(0,20)]


def deletion_oracle(args):
    nums,divide=args;common=0
    for value in divide:common=gcd(common,value)
    ordered=sorted(nums)
    for index,value in enumerate(ordered):
        if common%value==0:return index
    return -1


def random_deletion(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,12))],[rng.randint(1,60) for _ in range(rng.randint(1,10))]]


def impossible_oracle(args):
    rolls,k=args
    def occurs(sequence):
        index=0
        for value in rolls:
            if value==sequence[index]:
                index+=1
                if index==len(sequence):return True
        return False
    candidates=[()]
    length=0
    while candidates:
        length+=1;candidates=[prefix+(value,) for prefix in candidates for value in range(1,k+1)]
        if any(not occurs(sequence) for sequence in candidates):return length


def random_impossible(rng):
    k=rng.randint(1,4)
    return [[rng.randint(1,k) for _ in range(rng.randint(1,14))],k]


def excellent_oracle(args):
    nums,k=args;values=set(nums)
    return sum(left.bit_count()+right.bit_count()>=k for left in values for right in values)


def random_excellent(rng):return [[rng.randint(1,255) for _ in range(rng.randint(1,14))],rng.randint(1,16)]


PATHS='''\
def count_increasing_grid_paths(grid):
    from functools import lru_cache
    rows=len(grid);columns=len(grid[0])
    @lru_cache(None)
    def paths(row,column):
        answer=1
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=row+dr,column+dc
            if 0<=nr<rows and 0<=nc<columns and grid[nr][nc]>grid[row][column]:answer+=paths(nr,nc)
        return answer%1000000007
    return sum(paths(row,column) for row in range(rows) for column in range(columns))%1000000007
'''

SQUARED='''\
def minimum_squared_difference(nums1,nums2,k1,k2):
    differences=[abs(a-b) for a,b in zip(nums1,nums2)];operations=k1+k2
    if operations>=sum(differences):return 0
    low=0;high=max(differences)
    while low<high:
        middle=(low+high)//2
        if sum(max(0,value-middle) for value in differences)<=operations:high=middle
        else:low=middle+1
    cap=low;used=sum(max(0,value-cap) for value in differences);remaining=operations-used
    answer=sum(min(value,cap)**2 for value in differences)
    return answer-remaining*(2*cap-1)
'''

DELETIONS='''\
def minimum_deletions_for_divisibility(nums,numsDivide):
    common=0
    for value in numsDivide:common=__import__('math').gcd(common,value)
    for index,value in enumerate(sorted(nums)):
        if common%value==0:return index
    return -1
'''

IMPOSSIBLE='''\
def shortest_impossible_roll_sequence(rolls,k):
    seen=set();complete=0
    for value in rolls:
        seen.add(value)
        if len(seen)==k:complete+=1;seen.clear()
    return complete+1
'''

EXCELLENT='''\
def number_of_excellent_pairs(nums,k):
    counts=[0]*31
    for value in set(nums):counts[value.bit_count()]+=1
    return sum(counts[left]*counts[right] for left in range(31) for right in range(31) if left+right>=k)
'''


BATCH={
2328:entry('count_increasing_grid_paths',[('grid','list[list[int]]')],'int',['matrices','recursion','dynamic programming'],['A path is a nonempty sequence of cells connected by four-direction moves.','Every next cell value must be strictly greater than the previous value.','Count paths by their ordered cell sequence and return the result modulo 1,000,000,007.'],[([[[1,1],[3,4]]],'Four singleton paths plus four longer increasing paths give eight.'),([[[1],[2]]],'The two singleton paths and path 1-to-2 give three.')],[[g] for g in [[[1]],[[2,1]],[[1,2]],[[1,1]],[[1,2],[3,4]],[[4,3],[2,1]],[[1,1],[1,1]],[[1,3],[2,4]],[[3,1,2]],[[1],[2],[3]],[[1,2,3],[6,5,4]],[[9,1,9],[1,2,3],[9,4,9]],[[1,2],[2,3],[3,4]],[[5,4,3],[6,1,2]]]],PATHS,[PATHS.replace('((1,0),(-1,0),(0,1),(0,-1))','((1,0),(0,1))'),PATHS.replace('answer=1','answer=0')],['Explores only down and right moves, omitting valid increasing paths in the other directions.','Omits every singleton path by starting each recursive count at zero.'],paths_oracle,random_paths,['Define a recursive state as the number of increasing paths starting at one cell.','Every cell contributes its singleton path, then may extend to each strictly larger four-neighbor.','Memoize the recursive state because strictly increasing moves make the dependency graph acyclic.','Each path has a unique first step (or no step for a singleton), so the recurrence partitions paths without duplication.'],'O(rows*columns)','O(rows*columns)',8),
2333:entry('minimum_squared_difference',[('nums1','list[int]'),('nums2','list[int]'),('k1','int'),('k2','int')],'int',['arrays','binary search','greedy'],['One operation increments or decrements one value in either array by one.','Use at most k1 operations on nums1 and k2 on nums2 to minimize the sum of squared pairwise differences.','Only the total k1+k2 matters because either side can reduce an absolute difference.'],[([[1,2,3,4],[2,10,20,19],0,0],'With no operations, squared differences sum to 579.'),([[1,4,10,12],[5,8,6,9],1,1],'Spending two operations on the largest differences minimizes the squared sum to 43.')],[[a,b,k1,k2] for a,b,k1,k2 in [([1],[1],0,0),([1],[5],2,0),([1],[5],10,10),([1,2],[3,4],1,1),([0,10],[10,0],5,0),([5,5,5],[1,2,3],3,2),([1,100],[50,50],10,10),([3,8,2],[7,1,9],2,3),([10,20,30],[1,2,3],0,5),([1,1,1],[9,9,9],4,4),([2,4,6,8],[1,3,5,7],2,0),([0,0],[5,9],6,2),([100],[0],99,0),([7,3,11],[2,8,1],5,5)]],SQUARED,[SQUARED.replace('operations=k1+k2','operations=k1'),SQUARED.replace('2*cap-1','2*cap+1')],['Ignores all operations available on the second array.','Uses the square-decrease formula with the wrong sign, subtracting too much for leftover operations.'],squared_oracle,random_squared,['Convert each pair to an absolute difference and combine the two operation budgets.','Convex squares make reducing a currently larger difference never worse than reducing a smaller one.','Binary-search the smallest cap reachable within the budget, cap every difference, then distribute leftover reductions across cap-valued entries.','Leveling implements the repeated-largest greedy choice in bulk; reducing a cap to cap-1 lowers its square by 2*cap-1.'],'O(n log maxdiff)','O(n)',5),
2344:entry('minimum_deletions_for_divisibility',[('nums','list[int]'),('numsDivide','list[int]')],'int',['arrays','sorting','number theory'],['Delete any number of elements from nums.','After deletion, the smallest remaining nums value must divide every value in numsDivide.','Return the minimum deletions, or -1 if no nums value can satisfy the condition.'],[([[2,3,2,4,3],[9,6,9,3,15]],'After sorting, deleting both twos exposes three, which divides every target, so two deletions are needed.'),([[4,3,6],[8,2,6,10]],'No candidate divides the gcd two, so the result is minus one.')],[[a,b] for a,b in [([1],[1]),([2],[4,6]),([3],[4,6]),([2,4],[8,12]),([4,2],[8,12]),([5,2,10],[20,30]),([3,6,9],[18,27]),([7,14],[28,42]),([6,4,2],[8,12]),([10,5,2],[15,25]),([2,2,3],[6,12]),([8,4],[16,24,32]),([9,3,1],[12,18]),([11,22],[33,55])]],DELETIONS,[DELETIONS.replace('sorted(nums)','nums'),DELETIONS.replace('common%value==0','value%common==0')],['Scans unsorted input and returns deletions before a candidate rather than the minimum possible count.','Reverses divisibility and tests whether the candidate is divisible by the target gcd.'],deletion_oracle,random_deletion,['A value divides every numsDivide entry exactly when it divides their gcd.','Compute that gcd once and sort nums.','Return the first sorted index whose value divides the gcd; earlier values are precisely the necessary deletions.','The first qualifying sorted value minimizes removed elements, and absence of one proves impossibility.'],'O(m log values+n log n)','O(n)',8),
2350:entry('shortest_impossible_roll_sequence',[('rolls','list[int]'),('k','int')],'int',['arrays','greedy','subsequences'],['Roll values range from one through k.','Find the minimum length of a value sequence that is not a subsequence of rolls.','Return that minimum length, not the sequence itself.'],[([[4,2,1,2,3,3,2,4,1],4],'The rolls contain every one-symbol and two-symbol sequence as subsequences, but some length-three sequence is impossible.'),([[1,1,2,2],2],'Both faces occur, but sequence [2,1] is absent, so the answer is two.')],[[r,k] for r,k in [([1],1),([1,1],1),([1,2],2),([1,2,1,2],2),([1,1,2,2],2),([1,2,3],3),([3,2,1],3),([1,2,3,1,2,3],3),([1,1,1],2),([2,2,2],2),([1,2,1],2),([1,2,3,2,1,3],3),([4,1,2,3,4],4),([1,2,3,4,1,2,3,4],4)]],IMPOSSIBLE,[IMPOSSIBLE.replace('complete+1','complete'),IMPOSSIBLE.replace('seen.clear()','seen={value}')],['Returns the number of completed full-face blocks instead of one more.','Keeps the completing face in the next block even though one roll occurrence cannot serve twice.'],impossible_oracle,random_impossible,['Scan rolls while collecting distinct faces in the current block.','Whenever all k faces have appeared, increment a completed-block count and clear the set.','Return completed_blocks+1.','Each completed block can supply one chosen symbol for every sequence position; after c blocks a carefully chosen next symbol is missing, proving the shortest impossible length c+1.'],'O(n)','O(k)',8),
2354:entry('number_of_excellent_pairs',[('nums','list[int]'),('k','int')],'int',['bit manipulation','counting'],['A pair is ordered and may use the same value twice.','Duplicate occurrences in nums are discarded before forming pairs.','A pair (a,b) is excellent when popcount(a OR b)+popcount(a AND b) is at least k.'],[([[1,2,3,1],3],'After deduplication, five ordered pairs have combined bit counts at least three.'),([[5,1,1],10],'No pair has enough combined set bits, so the result is zero.')],[[a,k] for a,k in [([1],1),([1],2),([1,2],2),([1,2],3),([3,3],4),([3,5,7],4),([1,1,1],1),([7,8],3),([15,1,2],5),([31,16],6),([2,4,8],2),([5,10,5,10],4),([255,1],9),([6,9,12],4)]],EXCELLENT,[EXCELLENT.replace('for value in set(nums)','for value in nums'),EXCELLENT.replace('left+right>=k','left+right>k')],['Counts duplicate occurrences as distinct pair values despite required deduplication.','Uses a strict threshold and rejects pairs whose combined bit count equals k.'],excellent_oracle,random_excellent,['Use popcount(a OR b)+popcount(a AND b)=popcount(a)+popcount(b) bit by bit.','Deduplicate nums, then count how many unique values have each popcount.','Sum count[i]*count[j] for every ordered popcount pair with i+j>=k.','The identity reduces excellence to popcount classes, and the double loop retains ordered pairs and self-pairs exactly.'],'O(n+bits^2)','O(bits)',8),
}
