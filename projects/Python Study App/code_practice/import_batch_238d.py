"""Reduction bounds, bitwise LIS, convex partition DP, alternation, and BST levels."""
from bisect import bisect_left
from itertools import combinations
from .import_batch_055 import entry


def reduce_oracle(args):
    nums=args[0]
    for k in range(1,max(nums)+2):
        if sum((value+k-1)//k for value in nums)<=k*k:return k
def random_reduce(rng):return [[rng.randint(1,100) for _ in range(rng.randint(1,25))]]

def bit_lis_oracle(args):
    nums=args[0];best=0
    for mask in range(1,1<<len(nums)):
        values=[nums[i] for i in range(len(nums)) if mask>>i&1]
        if all(values[i]<values[i+1] for i in range(len(values)-1)):
            value=values[0]
            for item in values[1:]:value&=item
            if value:best=max(best,len(values))
    return best
def random_bit_lis(rng):return [[rng.randint(0,31) for _ in range(rng.randint(1,12))]]

def score(total):return total*(total+1)//2
def partition_oracle(args):
    nums,k=args;n=len(nums);prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    dp=[[10**30]*(n+1) for _ in range(k+1)];dp[0][0]=0
    for groups in range(1,k+1):
        for end in range(groups,n+1):
            dp[groups][end]=min(dp[groups-1][cut]+score(prefix[end]-prefix[cut]) for cut in range(groups-1,end))
    return dp[k][n]
def random_partition(rng):
    n=rng.randint(1,18);return [[rng.randint(1,20) for _ in range(n)],rng.randint(1,n)]

def alternating(values):return all((values[i]-values[i-1])*(values[i+1]-values[i])<0 for i in range(1,len(values)-1)) and all(values[i]!=values[i+1] for i in range(len(values)-1))
def alternating_oracle(args):
    nums=args[0];best=1
    for removed in range(-1,len(nums)):
        values=nums[:] if removed<0 else nums[:removed]+nums[removed+1:]
        for left in range(len(values)):
            for right in range(left,len(values)):best=max(best,right-left+1 if alternating(values[left:right+1]) else 0)
    return best
def random_alternating(rng):return [[rng.randint(1,12) for _ in range(rng.randint(2,14))]]

def level_oracle(args):
    values,level=args
    if not values or values[0] is None:return -1
    current=[values[0]];cursor=1;depth=0
    while current and depth<level:
        nxt=[]
        for _ in current:
            for _ in range(2):
                if cursor<len(values):
                    value=values[cursor];cursor+=1
                    if value is not None:nxt.append(value)
        current=nxt;depth+=1
    if depth!=level or not current:return -1
    ordered=sorted(current);return ordered[len(ordered)//2]

def serialize_bst(values):
    class Node:
        def __init__(self,value):self.value=value;self.left=self.right=None
    def build(items):
        if not items:return None
        middle=len(items)//2;node=Node(items[middle]);node.left=build(items[:middle]);node.right=build(items[middle+1:]);return node
    root=build(sorted(values));answer=[];queue=[root]
    while queue:
        node=queue.pop(0)
        if node is None:answer.append(None)
        else:answer.append(node.value);queue.extend((node.left,node.right))
    while answer and answer[-1] is None:answer.pop()
    return answer
def random_level(rng):
    count=rng.randint(1,20);tree=serialize_bst(rng.sample(range(1,200),count));return [tree,rng.randint(0,8)]


REDUCE='''def minimum_reduction_k(nums):
    def feasible(k):return sum((value+k-1)//k for value in nums)<=k*k
    left=1;right=max(max(nums),len(nums))
    while left<right:
        middle=(left+right)//2
        if feasible(middle):right=middle
        else:left=middle+1
    return left
'''

LIS='''def longest_increasing_nonzero_and(nums):
    from bisect import bisect_left
    answer=0
    for bit in range(max(nums,default=0).bit_length()):
        tails=[]
        for value in nums:
            if value>>bit&1:
                index=bisect_left(tails,value)
                if index==len(tails):tails.append(value)
                else:tails[index]=value
        answer=max(answer,len(tails))
    return answer
'''

PARTITION='''def minimum_partition_score(nums,k):
    prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    previous=[10**30]*(len(nums)+1);previous[0]=0
    def line(index,dp):
        value=prefix[index];return (-value,dp[index]+value*(value-1)//2)
    def evaluate(item,x):return item[0]*x+item[1]
    for groups in range(1,k+1):
        current=[10**30]*(len(nums)+1);hull=[];head=0
        for end in range(groups,len(nums)+1):
            if head:hull=hull[head:];head=0
            candidate=line(end-1,previous)
            while len(hull)>=2:
                m1,b1=hull[-2];m2,b2=hull[-1];m3,b3=candidate
                if (b2-b1)*(m2-m3)>=(b3-b2)*(m1-m2):hull.pop()
                else:break
            hull.append(candidate);x=prefix[end]
            while head+1<len(hull) and evaluate(hull[head],x)>=evaluate(hull[head+1],x):head+=1
            current[end]=x*(x+1)//2+evaluate(hull[head],x)
        previous=current
    return previous[-1]
'''

ALTERNATING='''def longest_alternating_after_removal(nums):
    n=len(nums);up_left=[1]*n;down_left=[1]*n;up_right=[1]*n;down_right=[1]*n;answer=1
    for i in range(1,n):
        if nums[i-1]<nums[i]:up_left[i]=down_left[i-1]+1
        elif nums[i-1]>nums[i]:down_left[i]=up_left[i-1]+1
        answer=max(answer,up_left[i],down_left[i])
    for i in range(n-2,-1,-1):
        if nums[i]<nums[i+1]:up_right[i]=down_right[i+1]+1
        elif nums[i]>nums[i+1]:down_right[i]=up_right[i+1]+1
    for i in range(1,n-1):
        if nums[i-1]<nums[i+1]:answer=max(answer,down_left[i-1]+down_right[i+1])
        elif nums[i-1]>nums[i+1]:answer=max(answer,up_left[i-1]+up_right[i+1])
    return answer
'''

MEDIAN='''def bst_level_upper_median(root,level):
    values=[];stack=[(root,0)]
    while stack:
        node,depth=stack.pop()
        if node is None:continue
        if depth==level:values.append(node.val);continue
        if depth<level:stack.append((node.right,depth+1));stack.append((node.left,depth+1))
    if not values:return -1
    values.sort();return values[len(values)//2]
'''

def lesson(a,b,c,d):return [a,b,c,d]

K_CASES=[[[*v]] for v in ([1],[3,7,5],[2],[10],[1,1,1],[5,5,5],[1,10],[1,7],[100,100],[2,3,5,7],[20,1,1],[9,9,1,1],[50,40,30],[100,1,100,1],[6,12,18,24])]
L_CASES=[[[*v]] for v in ([0],[1],[5,4,7],[2,3,6],[0,1],[1,2,4,8],[7,3,5,9],[8,4,2,1],[3,3,3],[1,3,2,7,6],[5,10,12,15],[0,2,1,3],[16,17,18,19],[6,5,7,12,14])]
P_CASES=[[a,k] for a,k in (([5,1,2,1],2),([1,2,3,4],1),([1,1,1],3),([1],1),([1,2],2),([2,2,2,2],2),([1,3,1,3],2),([10,1,1],2),([1,2,3,4,5],3),([5,4,3,2,1],2),([7,1,8,2,9],3),([1,1,1,1,1,1],4),([20,5,10,5],2),([2,4,6,8,10,12],3))]
A_CASES=[[[*v]] for v in ([2,1],[2,1,3,2],[3,2,1,2,3,2,1],[100000,100000],[1,2,3],[3,2,1],[1,3,2,4,3],[5,1,4,2,3],[1,1,2,1],[4,2,5,3,6],[7,3,5,1,4,2],[2,4,1,3,2,5],[9,8,10,7,11,6],[1,5,2,6,3,7,4])]
M_CASES=[[tree,level] for tree,level in (([4,None,5,None,7],2),([6,3,8],1),([2,1],2),([5],0),([5],1),([4,2,6,1,3,5,7],2),([8,4,12,2,6,10,14],1),([10,5,15,None,7,12,20],2),([3,1,5,None,2,4,6],2),([20,10,30,5,15,25,35],2),([7,3,9,1,5,8,10],1),([50,25,75,10,30,60,90],3),([6,2,9,1,4,8,10,None,None,3,5],3),([15,7,22,3,10,18,27],2))]

BATCH={
3824:entry('minimum_reduction_k',[('nums','list[int]')],'int',['arrays','binary search'],['nums has up to 100,000 positive values no greater than 100,000.','For a chosen positive k, reducing value x to nonpositive needs ceil(x/k) operations.','Find the smallest k whose total operations are at most k².'],[([[3,7,5]],'At k=3 the operation counts are one, three, and two, totaling six≤nine.'),([[1]],'One subtraction of one reaches zero and meets the bound one.')],K_CASES,REDUCE,[REDUCE.replace('(value+k-1)//k','value//k'),REDUCE.replace('<=k*k','<k*k')],['Uses floor division and undercounts values not divisible by k.','Requires strictly fewer than k² operations instead of allowing equality.'],reduce_oracle,random_reduce,lesson('For fixed k, each value independently needs ceil(value/k) operations.','The total decreases as k grows while k² grows, so feasibility is monotone.','Binary-search the first feasible k between one and max(nums).','Monotonicity guarantees every smaller k fails and the returned boundary is minimal.'),'O(n log M)','O(1)',5),
3825:entry('longest_increasing_nonzero_and',[('nums','list[int]')],'int',['arrays','longest increasing subsequence','bit manipulation'],['nums has up to 100,000 nonnegative values.','Choose a strictly increasing subsequence whose cumulative bitwise AND is nonzero.','Return its maximum length, or zero if none exists.'],[([[5,4,7]],'Subsequence [5,7] is increasing and has AND five, so length two is attainable.'),([[2,3,6]],'All three increase and share bit one, giving length three.')],L_CASES,LIS,[LIS.replace('bisect_left(tails,value)','__import__("bisect").bisect_right(tails,value)'),LIS.replace('if value>>bit&1:','if not (value>>bit&1):')],['Computes a nondecreasing rather than strictly increasing subsequence.','Keeps values missing the shared bit instead of values containing it.'],bit_lis_oracle,random_bit_lis,lesson('A nonzero AND means at least one bit is set in every chosen value.','For each possible bit, filter values containing it and compute their strictly increasing LIS.','Take the maximum LIS length over all bit positions.','Every valid subsequence shares some set bit and appears in that bit’s filtered sequence; every filtered LIS has nonzero AND at that bit.'),'O(Bn log n)','O(n)',6),
3826:entry('minimum_partition_score',[('nums','list[int]'),('k','int')],'int',['arrays','dynamic programming','convex hull trick','prefix sums'],['nums has up to 1,000 positive values and 1≤k≤n.','Partition into exactly k nonempty contiguous subarrays.','A segment of sum s costs s(s+1)/2; minimize total cost.'],[([[5,1,2,1],2],'Splitting as [5] and [1,2,1] costs fifteen plus ten, totaling twenty-five.'),([[1,1,1],3],'Three singleton segments each cost one, totaling three.')],P_CASES,PARTITION,[PARTITION.replace('value*(value-1)//2','value*(value+1)//2'),PARTITION.replace('previous[0]=0','previous[1]=0')],['Uses the wrong expanded intercept sign for each cut prefix.','Initializes the empty partition at index one instead of index zero.'],partition_oracle,random_partition,lesson('Expand f(Pi-Pj) so each previous cut j contributes a line of slope -Pj queried at x=Pi.','Positive nums make prefix sums and query x values strictly increasing, while new line slopes strictly decrease.','Maintain the lower hull in a deque for each group count and query it monotonically.','The algebra equals the exact segment cost, and the DP considers every last cut while hull dominance removes only lines that can never be optimal.'),'O(kn)','O(n)',8),
3830:entry('longest_alternating_after_removal',[('nums','list[int]')],'int',['arrays','dynamic programming'],['nums has at least two and up to 100,000 positive values.','After deleting at most one element, select a contiguous subarray of the resulting array.','Adjacent comparisons must be strict and alternate directions.'],[([[2,1,3,2]],'The entire array already follows >,<,>, so its length is four.'),([[100000,100000]],'Equal neighbors cannot alternate; a singleton of length one is best.')],A_CASES,ALTERNATING,[ALTERNATING.replace('for i in range(1,n-1):','for i in ():'),ALTERNATING.replace('+down_right[i+1]','+down_right[i+1]+1')],['Never evaluates stitching across a deleted element.','Counts the removed element in the stitched result length.'],alternating_oracle,random_alternating,lesson('Precompute alternating run lengths ending at each position for both last comparison directions, and analogous starting lengths.','Without deletion, these arrays give every run; deleting i can stitch positions i-1 and i+1 only when their new comparison has the needed direction.','Combine the matching left and right states without adding the deleted position.','Every optimal result either uses no deletion or has one unique gap, both of which are evaluated with exact direction compatibility.'),'O(n)','O(n)',8),
3831:entry('bst_level_upper_median',[('root','TreeNode | None'),('level','int')],'int',['trees','binary search trees','depth-first search'],['The BST contains up to 200,000 nodes and level is nonnegative.','Collect values at root-distance level; return -1 if that level is empty.','For even counts, return the upper of the two middle sorted values.'],[([[4,None,5,None,7],2],'The only value at level two is seven.'),([[6,3,8],1],'Sorted values [3,8] have upper median eight.')],M_CASES,MEDIAN,[MEDIAN.replace("values.sort();return values[len(values)//2]","values.sort();return values[0]"),MEDIAN.replace('len(values)//2','(len(values)-1)//2')],['Returns the smallest value on the requested level instead of its median.','Returns the lower median when the level has even size.'],level_oracle,random_level,lesson('Only nodes at the requested depth matter.','Traverse with explicit (node,depth) states to avoid recursion depth limits, collecting exactly that level.','Sort the collected values and select index count//2, the upper middle index.','Sorting defines the median directly; count//2 is the unique middle for odd sizes and upper middle for even sizes.'),'O(n+w log w)','O(n)',6),
}

BATCH[3831]['params'][0]=('root','TreeNode | None','treenode')
