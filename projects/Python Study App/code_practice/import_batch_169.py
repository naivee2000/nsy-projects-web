"""GCD propagation, uncovered ranges, greedy sums, prefix sets, and flood fill batch 169."""

from collections import deque
from math import gcd

from .import_batch_055 import entry


def ones_oracle(args):
    start=tuple(args[0])
    if all(value==1 for value in start):return 0
    queue=deque([(start,0)]);seen={start}
    while queue:
        values,distance=queue.popleft()
        for index in range(len(values)-1):
            common=gcd(values[index],values[index+1])
            for changed in (index,index+1):
                following=list(values);following[changed]=common;following=tuple(following)
                if following not in seen:
                    if all(value==1 for value in following):return distance+1
                    seen.add(following);queue.append((following,distance+1))
    return -1


def random_ones(rng):return [[rng.randint(1,12) for _ in range(rng.randint(1,6))]]


def uncovered_oracle(args):
    n,ranges=args;covered=[False]*n
    for left,right in ranges:
        for index in range(left,right+1):covered[index]=True
    answer=[];index=0
    while index<n:
        if covered[index]:index+=1;continue
        start=index
        while index+1<n and not covered[index+1]:index+=1
        answer.append([start,index]);index+=1
    return answer


def random_uncovered(rng):
    n=rng.randint(1,30);ranges=[]
    for _ in range(rng.randint(0,12)):
        left=rng.randrange(n);ranges.append([left,rng.randint(left,n-1)])
    return [n,ranges]


def maximum_oracle(args):
    nums,k=args
    if k>8:return k*max(nums)+k*(k-1)//2
    states={tuple(sorted(nums)):0}
    for _ in range(k):
        following={}
        for values,score in states.items():
            for index,value in enumerate(values):
                changed=list(values);changed[index]=value+1;changed=tuple(sorted(changed))
                following[changed]=max(following.get(changed,-1),score+value)
        states=following
    return max(states.values())


def random_maximum(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,5))],rng.randint(1,7)]


def common_oracle(args):
    first,second=args;answer=[]
    for end in range(len(first)):answer.append(len(set(first[:end+1])&set(second[:end+1])))
    return answer


def random_common(rng):
    n=rng.randint(1,30);first=list(range(1,n+1));second=first.copy();rng.shuffle(first);rng.shuffle(second)
    return [first,second]


def fish_oracle(args):
    grid=args[0];rows=len(grid);columns=len(grid[0]);seen=set();best=0
    for row in range(rows):
        for column in range(columns):
            if grid[row][column]==0 or (row,column) in seen:continue
            queue=deque([(row,column)]);seen.add((row,column));total=0
            while queue:
                r,c=queue.popleft();total+=grid[r][c]
                for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr,nc=r+dr,c+dc
                    if 0<=nr<rows and 0<=nc<columns and grid[nr][nc]>0 and (nr,nc) not in seen:
                        seen.add((nr,nc));queue.append((nr,nc))
            best=max(best,total)
    return best


def random_fish(rng):
    rows,columns=rng.randint(1,7),rng.randint(1,7)
    return [[[rng.randint(0,9) for _ in range(columns)] for _ in range(rows)]]


ONES="""\
def minimum_operations_to_all_ones(nums):
    import math
    ones=nums.count(1);n=len(nums)
    if ones:return n-ones
    shortest=n+1
    for left in range(n):
        common=0
        for right in range(left,n):
            common=math.gcd(common,nums[right])
            if common==1:shortest=min(shortest,right-left+1);break
    return -1 if shortest>n else n+shortest-2
"""

UNCOVERED="""\
def maximal_uncovered_ranges(n,ranges):
    ranges=sorted(ranges);answer=[];covered_end=-1
    for left,right in ranges:
        if covered_end+1<left:answer.append([covered_end+1,left-1])
        covered_end=max(covered_end,right)
    if covered_end+1<n:answer.append([covered_end+1,n-1])
    return answer
"""

MAXIMUM="""\
def maximum_exact_k_score(nums,k):
    largest=max(nums)
    return k*largest+k*(k-1)//2
"""

COMMON="""\
def prefix_common_counts(A,B):
    seen_a=set();seen_b=set();answer=[]
    for first,second in zip(A,B):
        seen_a.add(first);seen_b.add(second);answer.append(len(seen_a&seen_b))
    return answer
"""

FISH="""\
def maximum_fish_component(grid):
    rows=len(grid);columns=len(grid[0]);seen=set();best=0
    for start_row in range(rows):
        for start_column in range(columns):
            if grid[start_row][start_column]==0 or (start_row,start_column) in seen:continue
            stack=[(start_row,start_column)];seen.add((start_row,start_column));total=0
            while stack:
                row,column=stack.pop();total+=grid[row][column]
                for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr,nc=row+dr,column+dc
                    if 0<=nr<rows and 0<=nc<columns and grid[nr][nc]>0 and (nr,nc) not in seen:
                        seen.add((nr,nc));stack.append((nr,nc))
            best=max(best,total)
    return best
"""


BATCH={
2654:entry('minimum_operations_to_all_ones',[('nums','list[int]')],'int',['arrays','greatest common divisor','number theory'],
 ['In one operation, choose adjacent values and replace either one with their greatest common divisor.','Return the minimum operations needed to make every value one.','Return -1 when no sequence can create a one.'],
 [([[2,6,3,4]],'The shortest gcd-one subarray has length three; creating one and spreading it takes four operations total.'),([[2,10,6,14]],'Every value shares gcd two, so no operation can create one.')],
 [[a] for a in [[1],[2],[1,1],[1,2],[2,1],[2,3],[2,4],[6,10,15],[3,6,9],[5,10,6],[2,6,3,4],[1,2,3,4],[7,11,13],[4,6,9,15],[2,4,6,8,3]]],
 ONES,[ONES.replace('n+shortest-2','n+shortest-1'),ONES.replace('ones:return n-ones','ones:return ones')],
 ['Charges one extra operation after creating the first one.','Returns the number of existing ones rather than operations needed to convert the rest.'],ones_oracle,random_ones,
 ['Existing ones convert each non-one neighbor in one operation, so handle that case directly.','Otherwise find the shortest contiguous subarray whose gcd is one.','It takes length-1 operations to create one there, then n-1 operations to spread it through the array.','Any first one must arise from a contiguous chain of gcd operations, so the shortest gcd-one subarray is necessary and sufficient.'],'O(n² log M)','O(1)',5),
2655:entry('maximal_uncovered_ranges',[('n','int'),('ranges','list[list[int]]')],'list[list[int]]',['arrays','intervals','sorting'],
 ['Array indices run from zero through n-1; each inclusive input range is covered.','Return every maximal consecutive interval containing only uncovered indices.','Sort returned intervals by their starting index.'],
 [([10,[[3,5],[7,8]]],'The uncovered runs are zero through two, index six, and index nine.'),([3,[]],'With no covered ranges, the whole array interval [0,2] is uncovered.')],
 [[n,r] for n,r in [(1,[]),(1,[[0,0]]),(5,[]),(5,[[0,4]]),(5,[[1,3]]),(6,[[0,1],[4,5]]),(6,[[1,2],[2,4]]),(10,[[3,5],[7,8]]),(8,[[5,7],[0,1]]),(7,[[1,5],[2,3]]),(9,[[0,0],[2,2],[4,4],[6,6],[8,8]]),(10,[[2,7],[0,3]]),(4,[[1,1],[1,1]]),(12,[[3,4],[6,9],[1,2]])]],
 UNCOVERED,[UNCOVERED.replace('covered_end=max(covered_end,right)','covered_end=right'),UNCOVERED.replace('left-1','left')],
 ['Lets a nested range move the covered endpoint backward.','Includes the first covered index in the preceding uncovered interval.'],uncovered_oracle,random_uncovered,
 ['Sort covered ranges by start.','Track the farthest covered endpoint seen so far.','A gap exists when the next start is more than one beyond that endpoint; add the trailing gap after the scan.','Taking the maximum endpoint merges overlaps and nesting, while each emitted gap is bounded by covered positions or array edges and is therefore maximal.'],'O(r log r)','O(r)',5),
2656:entry('maximum_exact_k_score',[('nums','list[int]'),('k','int')],'int',['arrays','greedy','math'],
 ['Repeat exactly k times: remove a chosen value m, add m+1 back, and increase the score by m.','Choose operations to maximize the total score.','Return that maximum score.'],
 [([[1,2,3,4,5],3],'Repeatedly choosing the current maximum scores five, six, and seven for total eighteen.'),([[5,5,5],2],'Choose a five and then its replacement six for total eleven.')],
 [[a,k] for a,k in [([1],1),([1],5),([1,2],1),([1,2],2),([5,5],3),([3,1,4],4),([10,2,8],2),([1,2,3,4,5],3),([100],10),([2,9,2],5),([7,6,5],1),([4,4,1],6),([20,1,2],7),([3,8,5,8],4)]],
 MAXIMUM,[MAXIMUM.replace('max(nums)','min(nums)'),MAXIMUM.replace('k*(k-1)//2','k*(k+1)//2')],
 ['Starts from the smallest array value.','Adds increments one through k instead of zero through k-1.'],maximum_oracle,random_maximum,
 ['The currently largest value yields the best immediate score.','After choosing it, its replacement increases by one and remains at least as large as every untouched value.','Thus all k choices form largest, largest+1, ..., largest+k-1.','The exchange argument makes every smaller first choice no better, and the arithmetic-series formula sums the forced optimal sequence.'],'O(n)','O(1)',3),
2657:entry('prefix_common_counts',[('A','list[int]'),('B','list[int]')],'list[int]',['arrays','hash maps','prefix sums'],
 ['A and B are permutations of the integers one through n.','For each i, count values appearing in both prefixes A[0:i+1] and B[0:i+1].','Return those n prefix counts in order.'],
 [([[1,3,2,4],[3,1,2,4]],'The common prefix-value counts are zero, two, three, and four.'),([[2,3,1],[3,1,2]],'The first prefixes do not intersect, the length-two prefixes share three, and the full prefixes share all three values.')],
 [[a,b] for a,b in [([1],[1]),([1,2],[1,2]),([1,2],[2,1]),([1,2,3],[3,2,1]),([1,2,3],[2,3,1]),([1,3,2,4],[3,1,2,4]),([4,3,2,1],[1,2,3,4]),([2,1,4,3],[1,2,3,4]),([1,4,2,5,3],[5,1,3,2,4]),([3,1,4,2],[2,4,1,3]),([5,4,3,2,1],[5,1,2,3,4]),([2,5,1,4,3],[3,4,5,1,2]),([1,2,3,4,5,6],[6,5,4,3,2,1]),([3,2,1,5,4],[1,4,2,3,5])]],
 COMMON,[COMMON.replace('seen_a&seen_b','seen_a|seen_b'),COMMON.replace('seen_b.add(second)','seen_b.add(first)')],
 ['Counts the union of prefix values instead of the intersection.','Adds A values to both seen sets and ignores B.'],common_oracle,random_common,
 ['Maintain one seen set for each prefix.','Insert the newly exposed value from A and B at every index.','Append the size of the set intersection.','The sets exactly represent the two prefixes after each insertion, and permutation uniqueness means ordinary intersection size is the required common count.'],'O(n²)','O(n)',5),
2658:entry('maximum_fish_component',[('grid','list[list[int]]')],'int',['matrices','graphs','depth-first search'],
 ['Zero cells are land; positive cells are water containing that many fish.','A fisher may start at any water cell and move four-directionally through water cells, collecting all fish visited.','Return the greatest fish total in one connected water component, or zero if none exists.'],
 [([[[0,2,1,0],[4,0,0,3],[1,0,0,4],[0,3,2,0]]],'The right-side water component contains three and four fish for total seven.'),([[[1,0,0],[0,2,2],[0,2,0]]],'The lower component totals six fish, exceeding the isolated one.')],
 [[g] for g in [[[0]],[[1]],[[1,2]],[[1,0,2]],[[1],[2]],[[1],[0],[2]],[[1,1],[1,1]],[[1,0],[0,1]],[[0,0],[0,0]],[[1,2,0],[0,3,4]],[[5,0,1],[5,0,1]],[[1,2,3],[0,0,4],[7,6,5]],[[0,9,0],[9,9,9],[0,9,0]],[[1,0,2,2],[1,0,0,2]]]],
 FISH,[FISH.replace('(0,1),(0,-1)','(0,1)'),FISH.replace('total+=grid[row][column]','total+=1')],
 ['Explores right but not left, splitting some connected components.','Counts water cells rather than their fish values.'],fish_oracle,random_fish,
 ['Each starting point can reach exactly one four-connected positive component.','Scan all cells and flood-fill every unseen water cell once.','Sum cell values during each fill and retain the largest component sum.','Components partition all water cells, so considering each component once covers every possible start and its maximum collectable total.'],'O(rows*columns)','O(rows*columns)',5),
}
