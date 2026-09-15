"""Grid-height DP, grouped one moves, signed layers, chain covers, and prime squares."""
import bisect
from itertools import product

from .import_batch_055 import entry


def grid_score(grid,heights):
    n=len(grid);score=0
    for column in range(n):
        adjacent=max(heights[column-1] if column else 0,heights[column+1] if column+1<n else 0)
        score+=sum(grid[row][column] for row in range(heights[column],adjacent))
    return score


def grid_oracle(args):
    grid=args[0];n=len(grid);return max(grid_score(grid,heights) for heights in product(range(n+1),repeat=n))


def random_grid(rng):
    n=rng.randint(1,4);return [[[rng.randint(0,12) for _ in range(n)] for _ in range(n)]]


def ones_oracle(args):
    text=args[0];ones=answer=0
    for index,char in enumerate(text):
        if char=='1':ones+=1
        elif index and text[index-1]=='1':answer+=ones
    return answer


def random_ones(rng):return [''.join(rng.choice('01') for _ in range(rng.randint(1,30)))]


def operations_oracle(args):
    nums,target=args;difference=[b-a for a,b in zip(nums,target)];answer=0
    for level in range(1,max([abs(x) for x in difference]+[0])+1):
        answer+=sum(difference[i]>=level and (i==0 or difference[i-1]<level) for i in range(len(difference)))
        answer+=sum(difference[i]<=-level and (i==0 or difference[i-1]>-level) for i in range(len(difference)))
    return answer


def random_operations(rng):
    nums=[rng.randint(1,15) for _ in range(rng.randint(1,12))];return [nums,[max(1,value+rng.randint(-5,5)) for value in nums]]


def removal_oracle(args):
    nums=args[0];dp=[1]*len(nums)
    for right in range(len(nums)):
        for left in range(right):
            if nums[left]>=nums[right]:dp[right]=max(dp[right],dp[left]+1)
    return max(dp)


def random_removal(rng):return [[rng.randint(-10,15) for _ in range(rng.randint(1,15))]]


def special_oracle(args):
    left,right=args;special=0
    for value in range(left,right+1):
        proper=sum(value%d==0 for d in range(1,value))
        special+=proper==2
    return right-left+1-special


def random_special(rng):
    left=rng.randint(1,200);return [left,rng.randint(left,min(250,left+40))]


GRID='''def maximum_grid_operation_score(grid):
    n=len(grid)
    if n==1:return 0
    prefix=[[0]*(n+1) for _ in range(n)]
    for column in range(n):
        for row in range(n):prefix[column][row+1]=prefix[column][row]+grid[row][column]
    negative=-10**30;dp=[[negative]*(n+1) for _ in range(n+1)]
    for height in range(n+1):dp[0][height]=0
    for column in range(n-1):
        nxt=[[negative]*(n+1) for _ in range(n+1)];values=prefix[column]
        for middle in range(n+1):
            base=[dp[left][middle] for left in range(n+1)];pref=[];best=negative
            for value in base:best=max(best,value);pref.append(best)
            suffix_weight=[negative]*(n+2);middle_suffix=[negative]*(n+2)
            for left in range(n,-1,-1):
                suffix_weight[left]=max(suffix_weight[left+1],base[left]+values[left])
            for left in range(middle,-1,-1):middle_suffix[left]=max(middle_suffix[left+1],base[left])
            for right in range(n+1):
                score=pref[right]+(values[right]-values[middle] if right>middle else 0)
                if right<middle:score=max(score,middle_suffix[right+1])
                threshold=max(right,middle)+1
                if threshold<=n:score=max(score,suffix_weight[threshold]-values[middle])
                nxt[middle][right]=score
        dp=nxt
    answer=0;values=prefix[-1]
    for left in range(n+1):
        for middle in range(n+1):answer=max(answer,dp[left][middle]+(values[left]-values[middle] if left>middle else 0))
    return answer
'''


ONES='''def maximum_one_block_moves(s):
    ones=answer=0
    for index,char in enumerate(s):
        if char=='1':ones+=1
        elif index and s[index-1]=='1':answer+=ones
    return answer
'''


OPERATIONS='''def minimum_subarray_adjustments(nums,target):
    difference=[wanted-current for current,wanted in zip(nums,target)];answer=abs(difference[0])
    for previous,current in zip(difference,difference[1:]):
        if previous*current>0:answer+=max(0,abs(current)-abs(previous))
        else:answer+=abs(current)
    return answer
'''


REMOVAL='''def minimum_increasing_subsequence_removals(nums):
    import bisect
    tails=[]
    for number in nums:
        value=-number;position=bisect.bisect_right(tails,value)
        if position==len(tails):tails.append(value)
        else:tails[position]=value
    return len(tails)
'''


SPECIAL='''def count_non_special_numbers(l,r):
    import math
    limit=math.isqrt(r);prime=[True]*(limit+1)
    if limit>=0:prime[0]=False
    if limit>=1:prime[1]=False
    for value in range(2,math.isqrt(limit)+1):
        if prime[value]:
            for multiple in range(value*value,limit+1,value):prime[multiple]=False
    special=sum(flag and l<=value*value<=r for value,flag in enumerate(prime))
    return r-l+1-special
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
3225:entry('maximum_grid_operation_score',[('grid','list[list[int]]')],'int',['dynamic programming','matrices','prefix sums'],['grid is a nonempty square matrix of nonnegative cell values.','Choose a black prefix height independently for every column; a cell below its column’s black prefix remains white.','Score each white cell once when at least one horizontal neighbor is black, and maximize the score.'],[([[[0,0,0,0,0],[0,0,3,0,0],[0,1,0,0,0],[5,0,0,3,0],[0,0,0,0,2]]],'Choosing compatible column heights exposes white cells totaling eleven beside black neighbors.'),([[[1,2],[3,4]]],'Exhausting the three height choices per column shows the best score is six.')],[[g] for g in [[[0]],[[1,2],[3,4]],[[0,1],[2,0]],[[5,0],[0,5]],[[1,2,3],[4,5,6],[7,8,9]],[[0,0,0],[0,5,0],[0,0,0]],[[9,1,9],[1,9,1],[9,1,9]],[[1,0,0],[0,1,0],[0,0,1]],[[3,3,3],[3,3,3],[3,3,3]],[[0,2,0,2],[4,0,4,0],[0,6,0,6],[8,0,8,0]],[[1,0],[10,1]],[[7,2,5],[3,8,1],[4,6,9]],[[0,1,0],[2,0,3],[0,4,0]],[[5,1,4,2],[3,7,0,6],[8,2,9,1],[4,0,5,3]]]],GRID,[GRID.replace('threshold=max(right,middle)+1','threshold=n+1'),GRID.replace('answer=max(answer,dp[left][middle]+','answer=max(answer,dp[left][middle]-')],['Ignores transitions where the left neighboring black prefix is taller than both current and right heights.','Subtracts rather than adds the final column’s exposed white-cell contribution.'],grid_oracle,random_grid,lesson('A column’s contribution depends only on its own prefix height and the maximum of its two neighbors’ heights.','DP over the previous two heights; prefix and suffix maxima evaluate all older left heights for each new right height in constant time.','Add the completed center-column prefix-sum range, shift the two-height state, then close the final column against outside height zero.','Triple-local contributions are finalized exactly when the right height becomes known; optimized maxima partition left heights by which neighbor determines exposure.'),'O(n³)','O(n²)',8),
3228:entry('maximum_one_block_moves',[('s','str')],'int',['greedy','strings','counting'],['s is a nonempty binary string.','One operation chooses a 1 immediately followed by 0 and moves that 1 right across the entire consecutive zero block.','Return the maximum number of operations possible under an optimal order.'],[(['1001101'],'The first zero block can receive one earlier one and the later zero block can receive three, totaling four operations.'),(['00111'],'No one has a zero block to its right, so no operation is possible.')],[[s] for s in ['0','1','1001101','00111','10','01','1100','1010','111000','000111','10101','10001','1101010','0101100']],ONES,[ONES.replace("s[index-1]=='1'","True"),ONES.replace('answer+=ones','answer+=1')],['Adds all earlier ones for every zero character instead of once per zero block.','Counts each zero block once rather than once for every earlier one that can enter it.'],ones_oracle,random_ones,lesson('At the start of a zero block, every one seen earlier can eventually be moved across that block once.','Count prefix ones and add that count only on a 1-to-0 boundary.','Increment ones on 1; on 0 with previous 1 add ones.','Each operation can be charged uniquely to a one and a later zero block, and processing blocks left to right realizes every such charge.'),'O(n)','O(1)',5),
3229:entry('minimum_subarray_adjustments',[('nums','list[int]'),('target','list[int]')],'int',['greedy','arrays'],['nums and target are nonempty equal-length positive-integer arrays.','One operation selects a contiguous subarray and adds one to every element, or subtracts one from every element.','Return the minimum operations needed to transform nums into target.'],[([[3,5,1,2],[4,6,2,4]],'Increase the whole array once, then increase only the last element once, totaling two.'),([[1,3,2],[2,1,4]],'Required differences change sign, so positive and negative adjustment layers cannot share operations.')],[[a,b] for a,b in [([3,5,1,2],[4,6,2,4]),([1,3,2],[2,1,4]),([1],[1]),([1],[5]),([5],[1]),([1,1],[2,2]),([1,2],[2,1]),([5,5,5],[1,2,3]),([1,2,3],[3,2,1]),([10,1,10],[1,10,1]),([2,4,6,8],[3,5,7,9]),([4,4,1,1],[1,1,4,4]),([3,1,4,1,5],[5,1,2,3,5]),([9,8,7],[6,10,5])]],OPERATIONS,[OPERATIONS.replace('max(0,abs(current)-abs(previous))','abs(current)'),OPERATIONS.replace('max(0,abs(current)-abs(previous))','abs(current-previous)')],['Starts every same-sign layer again instead of reusing layers already active from the previous index.','Charges the full difference change even when existing same-sign layers can be reused.'],operations_oracle,random_operations,lesson('View each required signed difference as stacked positive or negative unit layers across indices.','Same-sign neighboring stacks reuse their overlapping layers; a sign change must start all layers anew.','Start abs(d[0]); add max(0,abs(cur)-abs(prev)) for same sign, else abs(cur).','Each counted layer start requires one subarray operation, and extending every layer until it ends constructs a matching optimal sequence.'),'O(n)','O(n)',8),
3231:entry('minimum_increasing_subsequence_removals',[('nums','list[int]')],'int',['binary search','subsequences'],['nums is a nonempty integer array and may contain duplicates.','Each operation removes any strictly increasing subsequence of remaining elements.','Return the minimum operations required to remove every element.'],[([[5,3,1,4,2]],'A non-increasing subsequence 5,3,1 has length three, forcing three rounds; three increasing chains achieve it.'),([[1,2,3]],'The entire array is strictly increasing and can be removed in one operation.')],[[n] for n in [[5,3,1,4,2],[1,2,3],[3,2,1],[1],[1,1],[1,2,1],[2,1,2],[3,1,2,1],[5,4,4,3],[1,3,2,4],[4,1,3,2],[0,-1,-1,-2],[2,5,1,4,3],[7,3,5,2,6,1]]],REMOVAL,[REMOVAL.replace('bisect.bisect_right','bisect.bisect_left'),REMOVAL.replace('value=-number','value=number')],['Computes a strictly decreasing obstruction and mishandles equal values, which cannot share a strict-increasing removal round.','Finds a nondecreasing subsequence in the original direction instead of a non-increasing obstruction.'],removal_oracle,random_removal,lesson('Partitioning a sequence into strict-increasing chains needs as many chains as the longest non-increasing subsequence.','Negate values and compute the longest nondecreasing subsequence with patience sorting and bisect_right.','Insert -x at upper_bound in tails; the tails length is the answer.','Dilworth’s chain-antichain theorem gives equality, while patience sorting computes the obstructing non-increasing length including duplicates.'),'O(n log n)','O(n)',8),
3233:entry('count_non_special_numbers',[('l','int'),('r','int')],'int',['number theory','sieve'],['1≤l≤r.','A special number has exactly two positive proper divisors, excluding itself.','Return how many integers in the inclusive range are not special.'],[([5,7],'None of five, six, or seven has exactly two proper divisors, so all three are non-special.'),([1,10],'Only 4 and 9 are squares of primes and therefore special; eight numbers are not.')],[[l,r] for l,r in [(5,7),(1,10),(1,1),(4,4),(8,9),(10,20),(20,30),(25,25),(49,50),(2,3),(100,130),(200,250),(999,1050),(10000,10200)]],SPECIAL,[SPECIAL.replace('value*value','value'),SPECIAL.replace('math.isqrt(r)','math.isqrt(r)-1')],['Counts prime values themselves as special instead of prime squares.','Sieves only through one below sqrt(r) and can miss the largest relevant prime square.'],special_oracle,random_special,lesson('A number has exactly two proper divisors iff it is p² for a prime p: its divisors are 1,p,p².','Sieve primes through floor(sqrt(r)) and count whose squares fall in [l,r].','Return range size minus qualifying prime-square count.','Composite bases add more divisors, and nonsquares cannot have exactly the paired divisor structure, so prime squares characterize all special numbers.'),'O(sqrt(r) log log r)','O(sqrt(r))',5),
}
