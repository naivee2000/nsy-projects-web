"""Combinatorial grids/subsequences, paired painting, bounded extrema, and locked sorting."""
from itertools import combinations
from math import comb

from .import_batch_055 import entry

MOD=1_000_000_007


def grid_distance_oracle(args):
    rows,columns,pieces=args;cells=list(range(rows*columns));answer=0
    for chosen in combinations(cells,pieces):
        for left,right in combinations(chosen,2):
            answer+=abs(left//columns-right//columns)+abs(left%columns-right%columns)
    return answer%MOD


def random_grid_distance(rng):
    while True:
        rows,columns=rng.randint(1,3),rng.randint(1,3)
        if rows*columns>=2:return [rows,columns,rng.randint(2,rows*columns)]


def subsequence_oracle(args):
    nums,k=args;answer=0
    for size in range(1,k+1):
        for indices in combinations(range(len(nums)),size):
            values=[nums[index] for index in indices];answer+=min(values)+max(values)
    return answer%MOD


def random_subsequence(rng):
    n=rng.randint(1,10)
    return [[rng.randint(0,20) for _ in range(n)],rng.randint(1,n)]


def paint_oracle(args):
    n,cost=args;answer=10**30;colors=[0]*n
    def visit(index,total):
        nonlocal answer
        if total>=answer:return
        if index==n:answer=total;return
        for color in range(3):
            if index and colors[index-1]==color:continue
            if index>=n//2 and colors[n-1-index]==color:continue
            colors[index]=color;visit(index+1,total+cost[index][color])
    visit(0,0);return answer


def random_paint(rng):
    n=2*rng.randint(1,4)
    return [n,[[rng.randint(0,15) for _ in range(3)] for _ in range(n)]]


def extrema_oracle(args):
    nums,k=args;answer=0
    for left in range(len(nums)):
        for right in range(left,min(len(nums),left+k)):
            values=nums[left:right+1];answer+=min(values)+max(values)
    return answer


def random_extrema(rng):
    n=rng.randint(1,12)
    return [[rng.randint(-15,15) for _ in range(n)],rng.randint(1,n)]


def unlock_oracle(args):
    nums,locked=args;required=set()
    for left in range(len(nums)):
        for right in range(left+1,len(nums)):
            if nums[left]==3 and nums[right]==1:return -1
            if nums[left]==nums[right]+1:required.update(range(left,right))
    return sum(locked[index] for index in required)


def random_unlock(rng):
    n=rng.randint(1,12)
    return [[rng.randint(1,3) for _ in range(n)],[rng.randint(0,1) for _ in range(n)]]


GRID='''def sum_grid_arrangement_distances(m,n,k):
    from math import comb
    modulo=1000000007;cells=m*n
    row_sum=n*n*m*(m-1)*(m+1)//6
    column_sum=m*m*n*(n-1)*(n+1)//6
    return (row_sum+column_sum)*comb(cells-2,k-2)%modulo
'''

SUBSEQUENCE='''def sum_bounded_subsequence_extrema(nums,k):
    modulo=1000000007;nums=sorted(nums);n=len(nums);answer=0
    choose=[1]*n
    for extra in range(k):
        for index,value in enumerate(nums):
            answer=(answer+value*(choose[index]+choose[n-1-index]))%modulo
        if extra+1<k:
            inverse=pow(extra+1,modulo-2,modulo)
            for index in range(n):choose[index]=choose[index]*(index-extra)*inverse%modulo if index>extra else 0
    return answer
'''

PAINT='''def minimum_beautiful_house_cost(n,cost):
    states={(left,right):cost[0][left]+cost[n-1][right] for left in range(3) for right in range(3) if left!=right}
    for layer in range(1,n//2):
        following={}
        for left in range(3):
            for right in range(3):
                if left==right:continue
                following[left,right]=min(value+cost[layer][left]+cost[n-1-layer][right] for (old_left,old_right),value in states.items() if old_left!=left and old_right!=right)
        states=following
    return min(states.values())
'''

EXTREMA='''def sum_at_most_k_subarray_extrema(nums,k):
    from collections import deque
    total=0;maximum=deque();minimum=deque();maximum_sum=minimum_sum=0
    for end,value in enumerate(nums):
        start=max(0,end-k+1)
        if start:
            maximum[0][2]-=1;maximum_sum-=maximum[0][1]
            if maximum[0][0]<start:maximum.popleft()
            minimum[0][2]-=1;minimum_sum-=minimum[0][1]
            if minimum[0][0]<start:minimum.popleft()
        shares=1;maximum_sum+=value
        while maximum and maximum[-1][1]<=value:
            _,old,count=maximum.pop();shares+=count;maximum_sum+=(value-old)*count
        maximum.append([end,value,shares])
        shares=1;minimum_sum+=value
        while minimum and minimum[-1][1]>=value:
            _,old,count=minimum.pop();shares+=count;minimum_sum+=(value-old)*count
        minimum.append([end,value,shares]);total+=maximum_sum+minimum_sum
    return total
'''

UNLOCK='''def minimum_indices_to_unlock(nums,locked):
    n=len(nums);first_two=first_three=n;last_one=last_two=-1
    for index,value in enumerate(nums):
        if value==1:last_one=index
        elif value==2:first_two=min(first_two,index);last_two=index
        else:first_three=min(first_three,index)
    if first_three<last_one:return -1
    return sum(state and (first_two<=index<last_one or first_three<=index<last_two) for index,state in enumerate(locked))
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


GRID_CASES=[[m,n,k] for m,n,k in [(2,2,2),(1,4,3),(1,2,2),(2,1,2),(1,5,2),(1,5,5),(2,3,2),(2,3,3),(2,3,6),(3,3,2),(3,3,4),(3,4,3),(4,2,5),(2,4,7)]]
SUBSEQUENCE_CASES=[[values,k] for values,k in [([1,2,3],2),([5,0,6],1),([1],1),([0,0],2),([1,1,1],2),([3,1],2),([4,2,7,1],1),([4,2,7,1],2),([4,2,7,1],4),([0,5,0,5],3),([10,1,9,2,8],2),([2,3,2,3,2],4),([100,0,50],3),([1,2,3,4,5,6],3)]]
PAINT_CASES=[[n,cost] for n,cost in [(4,[[3,5,7],[6,2,9],[4,8,1],[7,3,5]]),(6,[[2,4,6],[5,3,8],[7,1,9],[4,6,2],[3,5,7],[8,2,4]]),(2,[[1,2,3],[1,2,3]]),(2,[[0,0,0],[0,0,0]]),(4,[[1,9,9],[9,1,9],[9,1,9],[1,9,9]]),(4,[[1,2,3]]*4),(6,[[1,10,10],[10,1,10],[10,10,1],[1,10,10],[10,1,10],[10,10,1]]),(6,[[0,5,2],[3,0,4],[6,1,0],[2,7,1],[0,3,5],[4,0,6]]),(8,[[i%4+1,(i*3)%7,(i*5)%9] for i in range(8)]),(2,[[10,1,5],[3,8,2]]),(4,[[0,8,8],[8,0,8],[8,8,0],[0,8,8]]),(6,[[5,5,5]]*6),(8,[[1,2,9],[2,9,1],[9,1,2],[1,9,2],[2,1,9],[9,2,1],[1,2,9],[2,9,1]]),(4,[[100,1,100],[1,100,100],[100,100,1],[1,100,100]])]]
EXTREMA_CASES=[[values,k] for values,k in [([1,2,3],2),([1],1),([3,2,1],1),([3,2,1],2),([3,2,1],3),([-1,-2,-3],2),([2,2,2],3),([5,1,4,2],2),([5,1,4,2],4),([10,-10,10],2),([0,1,0,1,0],3),([7,3,9,2,8],1),([7,3,9,2,8],4),([-5,4,-3,2,-1,0],5)]]
UNLOCK_CASES=[[nums,locked] for nums,locked in [([1,2,1,2,3,2],[1,0,1,1,0,1]),([1,2,1,1,3,2,2],[1,0,1,1,0,1,0]),([1],[1]),([1,2,3],[1,1,1]),([3,1],[0,0]),([2,1],[1,0]),([2,1],[0,1]),([3,2],[1,0]),([1,3,2],[1,1,1]),([2,2,1,1],[1,0,1,0]),([1,2,1,2],[1,1,1,1]),([3,2,2,1],[0,0,0,0]),([2,3,2,1],[1,1,1,1]),([1,3,2,2,1],[0,1,0,1,0])]]


BATCH={
3426:entry('sum_grid_arrangement_distances',[('m','int'),('n','int'),('k','int')],'int',['math','combinatorics','grids'],['1 <= m,n and 2 <= m*n <= 100,000.','Place exactly k identical pieces in distinct cells, where 2 <= k <= m*n.','Sum every unordered pair’s Manhattan distance over every placement and return it modulo 1,000,000,007.'],[([2,2,2],'There are four adjacent pairs of distance one and two diagonal pairs of distance two, totaling eight.'),([1,4,3],'The four three-cell placements have pair-distance totals four, six, six, and four, totaling twenty.')],GRID_CASES,GRID,[GRID.replace('*comb(cells-2,k-2)',''),GRID.replace('row_sum+column_sum','row_sum')],['Counts each cell pair only once instead of once for every placement containing that pair.','Includes vertical distance but omits all horizontal distance.'],grid_distance_oracle,random_grid_distance,lesson('Every fixed pair of cells appears together in exactly C(m*n-2,k-2) placements.','Sum vertical and horizontal distances over all cell pairs, then apply the common placement multiplier.','For each row gap d, count d*(m-d)*n^2; repeat for columns and multiply by the binomial coefficient.','Linearity of summation lets us count a pair’s contribution independently, avoiding enumeration of arrangements.'),'O(1)','O(1)',8),
3428:entry('sum_bounded_subsequence_extrema',[('nums','list[int]'),('k','int')],'int',['arrays','sorting','combinatorics'],['nums has 1–100,000 nonnegative integers.','Consider every nonempty index subsequence containing at most k elements, with k <= min(70,len(nums)).','Sum the minimum and maximum of every such subsequence modulo 1,000,000,007.'],[([[1,2,3],2],'Three singleton contributions total twelve, and the three length-two contributions total twelve, giving twenty-four.'),([[5,0,6],1],'Each singleton contributes its value twice, so the result is twenty-two.')],SUBSEQUENCE_CASES,SUBSEQUENCE,[SUBSEQUENCE.replace('for extra in range(k):','for extra in range(1):'),SUBSEQUENCE.replace('choose[index]+choose[n-1-index]','choose[index]')],['Counts only singleton subsequences and ignores every larger allowed size.','Counts each value only as a maximum and omits its minimum contribution.'],subsequence_oracle,random_subsequence,lesson('After sorting, a value is an extreme according to how many elements are chosen on one side of it.','Accumulate binomial counts for choosing zero through k-1 companion indices.','At each size add value*C(index,size) as a maximum and value*C(n-1-index,size) as a minimum, updating combinations in place.','Every subsequence is counted once by its chosen minimum and once by its chosen maximum; sorting affects values, not index-choice multiplicity.'),'O(n*k+n log n)','O(n)',6),
3429:entry('minimum_beautiful_house_cost',[('n','int'),('cost','list[list[int]]')],'int',['arrays','dynamic programming'],['n is even, 2 <= n <= 100,000, and cost has n rows of three nonnegative painting costs.','Adjacent houses must use different colors.','Each mirrored pair i and n-1-i must also use different colors; return the minimum total cost.'],[([4,[[3,5,7],[6,2,9],[4,8,1],[7,3,5]]],'Colors [1,2,3,2] cost three plus two plus one plus three, totaling nine.'),([2,[[1,2,3],[1,2,3]]],'The two adjacent and mirrored houses use colors one and two for total cost three.')],PAINT_CASES,PAINT,[PAINT.replace(' if left!=right',''),PAINT.replace('if left==right:continue','if False:continue')],['Allows the outer mirrored pair to share a color.','Allows every later mirrored pair to share a color.'],paint_oracle,random_paint,lesson('Process houses as mirrored pairs so both long-range and adjacent restrictions stay local.','Keep the previous left and right colors as a nine-state dynamic program.','For each inward pair choose distinct colors that also differ from their same-side predecessor, then add both costs.','The state records exactly the colors that can constrain the next pair, so optimal substructure holds.'),'O(n)','O(1)',6),
3430:entry('sum_at_most_k_subarray_extrema',[('nums','list[int]'),('k','int')],'int',['arrays','monotonic stacks','sliding window'],['nums has 1–100,000 integers and 1 <= k <= len(nums).','Consider every nonempty contiguous subarray whose length is at most k.','Return the sum of each subarray’s minimum plus maximum.'],[([[1,2,3],2],'The singleton totals are two, four, and six; the two length-two totals are three and five, giving twenty.'),([[3,2,1],1],'Only singletons qualify, contributing six, four, and two for total twelve.')],EXTREMA_CASES,EXTREMA,[EXTREMA.replace('total+=maximum_sum+minimum_sum','total+=maximum_sum'),EXTREMA.replace('start=max(0,end-k+1)','start=max(0,end-k)')],['Adds only subarray maxima and omits minima.','Keeps windows of length k+1, so oversized subarrays enter the total.'],extrema_oracle,random_extrema,lesson('For each right endpoint, maintain the sum of maxima and minima of every allowed suffix.','Use monotonic block deques whose share counts say how many suffixes currently choose each extreme.','Merge dominated blocks when appending, remove one share when the left limit advances, and add both running sums.','Each suffix contributes to one block; block merging updates exactly the suffixes whose extreme changes.'),'O(n)','O(n)',8),
3431:entry('minimum_indices_to_unlock',[('nums','list[int]'),('locked','list[int]')],'int',['arrays','invariants','sorting'],['nums and locked have equal length up to 100,000; nums values are 1, 2, or 3 and locked values are binary.','Adjacent positions i and i+1 may swap only when their values differ by one and locked[i] is zero.','Set locked indices to zero at unit cost; return the minimum cost that makes nums sortable, or -1 if impossible.'],[([[1,2,1,2,3,2],[1,0,1,1,0,1]],'The needed 2-before-1 and 3-before-2 swaps already cross unlocked boundaries, so no operation is needed.'),([[1,2,1,1,3,2,2],[1,0,1,1,0,1,0]],'Unlocking boundaries two and five permits all required adjacent swaps, costing two.')],UNLOCK_CASES,UNLOCK,[UNLOCK.replace('return -1','return 0'),UNLOCK.replace('first_two<=index<last_one','first_two<index<last_one').replace('first_three<=index<last_two','first_three<index<last_two')],['Treats an inversion of three before one as sortable even though those values can never cross.','Fails to unlock the first boundary in each required crossing interval.'],unlock_oracle,random_unlock,lesson('A three can never cross a one, while every inverted neighboring-value pair must cross every boundary between its endpoints.','Reject any 3-before-1 inversion; otherwise identify the union of boundaries needed by 2-before-1 and 3-before-2 inversions.','Find the first larger value and last smaller value for each adjacent value pair, then count locked boundaries in those intervals.','All required crossings are possible after those boundaries are unlocked, and every counted boundary is necessary for at least one inversion.'),'O(n)','O(1)',6),
}
