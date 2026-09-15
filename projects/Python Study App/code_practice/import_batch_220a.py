"""OR/XOR splits, anchored 2D paths, four picks, worker timing, and consecutive subsequences."""
from itertools import combinations,product
from bisect import bisect_left
from .import_batch_055 import entry

def sequence_oracle(args):
    nums,k=args;best=0
    for indices in combinations(range(len(nums)),2*k):
        left=right=0
        for i in indices[:k]:left|=nums[i]
        for i in indices[k:]:right|=nums[i]
        best=max(best,left^right)
    return best
def random_sequence(rng):
    n=rng.randint(2,10);return [[rng.randint(1,63) for _ in range(n)],rng.randint(1,n//2)]

def path_oracle(args):
    points,k=args;n=len(points);target=points[k];before=[1]*n;after=[1]*n
    order=sorted(range(n),key=lambda i:(points[i][0],points[i][1]))
    for i in order:
        for j in order:
            if points[j][0]<points[i][0] and points[j][1]<points[i][1]:before[i]=max(before[i],before[j]+1)
    for i in reversed(order):
        for j in order:
            if points[j][0]>points[i][0] and points[j][1]>points[i][1]:after[i]=max(after[i],after[j]+1)
    return before[k]+after[k]-1
def random_path(rng):
    n=rng.randint(1,13);points=set()
    while len(points)<n:points.add((rng.randint(0,20),rng.randint(0,20)))
    values=[list(p) for p in points];return [values,rng.randrange(n)]

def score_oracle(args):
    a,b=args;return max(sum(a[j]*b[i] for j,i in enumerate(indices)) for indices in combinations(range(len(b)),4))
def random_score(rng):return [[rng.randint(-8,8) for _ in range(4)],[rng.randint(-8,8) for _ in range(rng.randint(4,10))]]

def mountain_oracle(args):
    height,times=args;best=10**30
    for allocation in product(range(height+1),repeat=len(times)):
        if sum(allocation)==height:best=min(best,max((t*x*(x+1)//2 for t,x in zip(times,allocation)),default=0))
    return best
def random_mountain(rng):return [rng.randint(1,10),[rng.randint(1,8) for _ in range(rng.randint(1,4))]]

def subsequence_oracle(args):
    nums=args[0];answer=0
    for mask in range(1,1<<len(nums)):
        values=[nums[i] for i in range(len(nums)) if mask>>i&1]
        if len(values)==1 or all(b-a==1 for a,b in zip(values,values[1:])) or all(b-a==-1 for a,b in zip(values,values[1:])):answer+=sum(values)
    return answer%(10**9+7)
def random_subsequence(rng):return [[rng.randint(1,9) for _ in range(rng.randint(1,14))]]

SEQUENCE='''def maximum_or_xor_subsequence(nums,k):
    n=len(nums)
    prefix=[[set() for _ in range(k+1)] for _ in range(n+1)];prefix[0][0].add(0)
    for i,value in enumerate(nums):
        for used in range(k+1):
            prefix[i+1][used]|=prefix[i][used]
            if used<k:prefix[i+1][used+1]|={current|value for current in prefix[i][used]}
    suffix=[[set() for _ in range(k+1)] for _ in range(n+1)];suffix[n][0].add(0)
    for i in range(n-1,-1,-1):
        for used in range(k+1):
            suffix[i][used]|=suffix[i+1][used]
            if used<k:suffix[i][used+1]|={current|nums[i] for current in suffix[i+1][used]}
    answer=0
    for split in range(k,n-k+1):
        for left in prefix[split][k]:
            for right in suffix[split][k]:answer=max(answer,left^right)
    return answer
'''
PATH='''def longest_increasing_path_through(coordinates,k):
    import bisect
    target_x,target_y=coordinates[k]
    def length(points):
        tails=[]
        for x,y in sorted(points,key=lambda point:(point[0],-point[1])):
            position=bisect.bisect_left(tails,y)
            if position==len(tails):tails.append(y)
            else:tails[position]=y
        return len(tails)
    lower=[point for point in coordinates if point[0]<target_x and point[1]<target_y]
    upper=[[-x,-y] for x,y in coordinates if x>target_x and y>target_y]
    return length(lower)+1+length(upper)
'''
SCORE='''def maximum_four_pick_score(a,b):
    negative=-10**30;dp=[0]+[negative]*4
    for value in b:
        for chosen in range(3,-1,-1):dp[chosen+1]=max(dp[chosen+1],dp[chosen]+a[chosen]*value)
    return dp[4]
'''
MOUNTAIN='''def minimum_mountain_seconds(mountain_height,worker_times):
    import math
    def enough(seconds):
        removed=0
        for worker in worker_times:
            removed+=(math.isqrt(1+8*(seconds//worker))-1)//2
            if removed>=mountain_height:return True
        return False
    low=0;high=min(worker_times)*mountain_height*(mountain_height+1)//2
    while low<high:
        middle=(low+high)//2
        if enough(middle):high=middle
        else:low=middle+1
    return low
'''
SUBSEQUENCES='''def sum_consecutive_subsequence_values(nums):
    modulo=10**9+7;inc_count={};inc_sum={};dec_count={};dec_sum={};answer=0
    for value in nums:
        up_count=1+inc_count.get(value-1,0);up_sum=value*up_count+inc_sum.get(value-1,0)
        down_count=1+dec_count.get(value+1,0);down_sum=value*down_count+dec_sum.get(value+1,0)
        answer=(answer+up_sum+down_sum-value)%modulo
        inc_count[value]=(inc_count.get(value,0)+up_count)%modulo;inc_sum[value]=(inc_sum.get(value,0)+up_sum)%modulo
        dec_count[value]=(dec_count.get(value,0)+down_count)%modulo;dec_sum[value]=(dec_sum.get(value,0)+down_sum)%modulo
    return answer
'''
def lesson(a,b,c,d):return [a,b,c,d]

BATCH={
3287:entry('maximum_or_xor_subsequence',[('nums','list[int]'),('k','int')],'int',['dynamic programming','bit manipulation','subsequences'],['2≤len(nums)≤400, values are 1..127, and 1≤k≤len(nums)//2.','Choose a length-2k subsequence; OR its first k values and OR its last k values.','Return the maximum XOR of those two OR results.'],[([[2,6,7],1],'Choosing 2 and 7 produces 2 XOR 7 = 5.'),([[4,2,5,6,7],2],'The subsequence 4,5,6,7 gives (4 OR 5) XOR (6 OR 7) = 2.')],[[a,k] for a,k in [([1,2],1),([7,7],1),([1,2,4],1),([1,2,3,4],2),([8,1,2,4],1),([3,5,6,9],2),([1,1,2,2,4,4],2),([127,1,64,2],1),([5,10,20,40,80],2),([2,3,4,5,6,7],3),([1,7,8,15,16,31],2),([12,3,9,6,5],1),([4,4,1,2,8,8],2),([63,32,16,8,4,2],2)]],SEQUENCE,[SEQUENCE.replace('left^right','left|right'),SEQUENCE.replace('suffix[split][k]','suffix[split+1][k]')],['Combines the two OR values with OR instead of XOR.','Forces an unused index between the selected halves.'],sequence_oracle,random_sequence,lesson('Only selected count and accumulated 7-bit OR matter on either side of a split.','Build reachable OR sets for choosing up to k values in every prefix and suffix.','For each valid split, XOR every reachable k-choice prefix OR with every k-choice suffix OR.','Every ordered subsequence has a unique split between its kth and k+1st selections, so the scan is complete.'),'O(nk·128+n·128²)','O(nk·128)',8),
3288:entry('longest_increasing_path_through',[('coordinates','list[list[int]]'),('k','int')],'int',['binary search','sorting','longest increasing subsequence'],['coordinates contains up to 100,000 distinct 2D points and k is a valid index.','A path strictly increases both x and y and must contain coordinates[k].','Return its maximum possible number of points.'],[([[[3,1],[2,2],[4,1],[0,0],[5,3]],1],'The path (0,0),(2,2),(5,3) contains the target and has length three.'),([[[2,1],[7,0],[5,6]],2],'Point (2,1) can precede the target (5,6), producing length two.')],[[p,k] for p,k in [([[0,0]],0),([[0,0],[1,1]],0),([[0,0],[1,1]],1),([[0,1],[1,0]],0),([[1,1],[0,0],[2,2]],0),([[1,2],[2,1],[3,3]],2),([[0,0],[1,2],[2,1],[3,3]],1),([[5,5],[1,1],[3,3],[7,7]],2),([[0,2],[1,2],[2,3]],1),([[3,0],[2,1],[1,2],[4,4]],3),([[2,2],[0,1],[1,0],[3,4]],0),([[10,10],[9,9],[8,7],[7,8]],0),([[1,5],[2,6],[3,4],[4,7]],1),([[4,4],[1,1],[2,3],[3,2],[5,5]],0)]],PATH,[PATH.replace('bisect.bisect_left','bisect.bisect_right'),PATH.replace('point[0]<target_x and point[1]<target_y','point[0]<target_x or point[1]<target_y')],['Uses nondecreasing y subsequences and therefore permits equal y coordinates.','Includes points that are lower in only one coordinate.'],path_oracle,random_path,lesson('Any valid target-containing path splits into points strictly southwest and strictly northeast of the target.','Compute a 2D strict LIS independently on each side, reversing signs for the northeast half.','Sort x ascending and y descending on x ties, then take a strict LIS of y with bisect_left.','Tie reversal prevents equal x values from chaining; the two independent paths join only through the target.'),'O(n log n)','O(n)',8),
3290:entry('maximum_four_pick_score',[('a','list[int]'),('b','list[int]')],'int',['dynamic programming','subsequences'],['a has exactly four integers and b has at least four; values may be negative.','Choose indices i0<i1<i2<i3 from b and sum a[j]*b[ij].','Return the maximum possible score.'],[([[3,2,5,6],[2,-6,4,-5,-3,2,-7]],'Indices 0,1,2,5 produce score 26.'),([[-1,4,5,-2],[-5,-1,-3,-2,-4]],'Indices 0,1,3,4 produce the maximum score -1.')],[[a,b] for a,b in [([1,1,1,1],[1,2,3,4]),([1,1,1,1],[4,3,2,1]),([-1,-1,-1,-1],[1,2,3,4]),([0,0,0,0],[9,-2,4,1]),([2,-1,3,-2],[1,2,3,4]),([5,4,3,2],[-1,-2,-3,-4]),([1,2,3,4],[4,3,2,1,5]),([-2,3,-4,5],[6,-1,2,-3,4]),([10,-10,10,-10],[1,2,3,4,5]),([1,-2,3,-4],[-5,-4,-3,-2,-1]),([7,1,-2,6],[3,8,-1,4,2]),([2,2,2,2],[1,9,1,9,1]),([-3,5,1,-2],[7,0,-4,6,3]),([4,-1,-1,4],[2,5,-3,7,1,8])]],SCORE,[SCORE.replace('range(3,-1,-1)','range(4)'),SCORE.replace('return dp[4]','return max(dp)')],['Updates selection states forward, allowing one b value to be reused.','Allows fewer than four selected indices.'],score_oracle,random_score,lesson('After scanning a prefix of b, only how many coefficients have been assigned matters.','Keep the best score for selecting exactly zero through four indices.','Process states backward so each b value is used at most once; assign it to the next coefficient.','Skip/take transitions cover every ordered four-index choice, and exact-count states preserve feasibility with negatives.'),'O(len(b))','O(1)',6),
3296:entry('minimum_mountain_seconds',[('mountain_height','int'),('worker_times','list[int]')],'int',['binary search','math','greedy'],['mountain_height is 1..100,000 and worker_times contains 1..10,000 positive values.','A worker removing x units needs worker_time·x(x+1)/2 seconds; workers act simultaneously.','Return the minimum time in which their total removable units reach the mountain height.'],[([4,[2,1,1]],'Assignments of 1,2,1 units take 2,3,1 seconds, so the optimum is three.'),([10,[3,2,2,4]],'Assignments 2,3,3,2 all finish within twelve seconds.')],[[h,w] for h,w in [(1,[1]),(5,[1]),(1,[10,20]),(2,[1,1]),(3,[2,2]),(4,[3]),(6,[1,2]),(7,[2,3,4]),(10,[1]),(8,[5,1]),(9,[2,2,2]),(12,[3,1,4]),(15,[10,5,2]),(20,[1,10,10])]],MOUNTAIN,[MOUNTAIN.replace('seconds//worker','seconds'),MOUNTAIN.replace('removed>=mountain_height','removed>mountain_height')],['Ignores differing worker speeds when computing capacity.','Requires workers to remove strictly more than the mountain height.'],mountain_oracle,random_mountain,lesson('The total units removable by a fixed time is monotone, so search the earliest feasible time.','Invert worker·x(x+1)/2≤time using an integer square root.','Sum every worker capacity and compare with the height; binary-search between zero and the one-worker bound.','The capacity inversion is exact and feasibility is monotone, so lower-bound binary search returns the optimum second.'),'O(w log answer)','O(1)',7),
3299:entry('sum_consecutive_subsequence_values',[('nums','list[int]')],'int',['dynamic programming','hash maps','subsequences'],['1≤len(nums)≤100,000 and values are positive.','A nonempty subsequence is consecutive when all adjacent differences are +1 or all are -1; singletons qualify.','Return the sum of element sums over all such index subsequences modulo 1,000,000,007.'],[([[1,2]],'The valid subsequences [1], [2], and [1,2] have values totaling six.'),([[1,4,2,3]],'The eight listed increasing, decreasing, and singleton subsequences total 31.')],[[a] for a in [[1],[2,1],[1,1],[1,2,3],[3,2,1],[1,3],[1,2,1],[2,3,2],[1,4,2,3],[5,4,3,2],[1,2,2,3],[2,1,2,3],[7,8,9,7],[3,1,2,4]]],SUBSEQUENCES,[SUBSEQUENCES.replace('up_sum+down_sum-value','up_sum+down_sum'),SUBSEQUENCES.replace('value-1','value+1')],['Counts every singleton twice.','Extends increasing sequences from the wrong previous value.'],subsequence_oracle,random_subsequence,lesson('Classify valid length≥2 subsequences by their fixed direction; the two classes overlap only on singletons.','For each ending value track count and total sum of increasing and decreasing subsequences.','Extend +1 chains from value-1 and -1 chains from value+1, add new singletons, then subtract one singleton copy.','Grouping by final index and direction counts every valid index subsequence once and accumulates its full value.'),'O(n)','O(distinct values)',8),
}

# Equal y-values cannot be chained in a path that must increase strictly.
BATCH[3288]['boundaries'].append([[[0,0],[1,0],[2,2]],2])
