"""Batched range products, graphical degrees, distinct groups, jumps, and robot shots."""
from bisect import bisect_left
from functools import lru_cache
from itertools import combinations, product
from collections import Counter
from .import_batch_055 import entry


def xor_oracle(args):
    nums,queries=args;nums=nums[:];mod=10**9+7
    for left,right,step,factor in queries:
        index=left
        while index<=right:nums[index]=nums[index]*factor%mod;index+=step
    answer=0
    for value in nums:answer^=value
    return answer

def random_xor(rng):
    n=rng.randint(1,20);nums=[rng.randint(1,10**9) for _ in range(n)];queries=[]
    for _ in range(rng.randint(1,20)):
        left=rng.randrange(n);right=rng.randrange(left,n);queries.append([left,right,rng.randint(1,n),rng.randint(1,10**5)])
    return [nums,queries]

def graph_oracle(args):
    degrees=sorted(args[0],reverse=True)
    while degrees:
        degree=degrees.pop(0)
        if degree<0 or degree>len(degrees):return False
        for i in range(degree):
            degrees[i]-=1
            if degrees[i]<0:return False
        degrees.sort(reverse=True)
    return True

def random_graph(rng):
    n=rng.randint(1,12);return [[rng.randint(0,n-1) for _ in range(n)]]

def groups_oracle(args):
    nums,k=args
    if len(nums)%k:return False
    @lru_cache(None)
    def fill(values):
        if not values:return True
        for chosen in combinations(range(1,len(values)),k-1):
            indices=(0,)+chosen;group=[values[index] for index in indices]
            if len(set(group))<k:continue
            selected=set(indices);remaining=tuple(value for index,value in enumerate(values) if index not in selected)
            if fill(remaining):return True
        return False
    return fill(tuple(sorted(nums)))

def random_groups(rng):
    n=rng.randint(1,10);return [[rng.randint(1,6) for _ in range(n)],rng.randint(1,n)]

def jump_oracle(args):
    nums=args[0];n=len(nums);answer=[]
    for start in range(n):
        seen={start};stack=[start]
        while stack:
            i=stack.pop()
            for j in range(n):
                if j not in seen and ((j>i and nums[j]<nums[i]) or (j<i and nums[j]>nums[i])):seen.add(j);stack.append(j)
        answer.append(max(nums[i] for i in seen))
    return answer

def random_jump(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,15))]]

def walls_oracle(args):
    robots,distance,walls=args;ordered=sorted(zip(robots,distance));answer=0
    for directions in product((0,1),repeat=len(ordered)):
        destroyed=set()
        for i,((position,reached),rightward) in enumerate(zip(ordered,directions)):
            if rightward:
                end=position+reached
                if i+1<len(ordered):end=min(end,ordered[i+1][0]-1)
                destroyed.update(wall for wall in walls if position<=wall<=end)
            else:
                start=position-reached
                if i:start=max(start,ordered[i-1][0]+1)
                destroyed.update(wall for wall in walls if start<=wall<=position)
        answer=max(answer,len(destroyed))
    return answer

def random_walls(rng):
    n=rng.randint(1,8);robots=rng.sample(range(1,40),n);walls=rng.sample(range(1,40),rng.randint(1,10))
    return [robots,[rng.randint(1,12) for _ in range(n)],walls]


XOR_BATCH='''def xor_after_many_range_products(nums,queries):
    import math
    mod=10**9+7;n=len(nums);threshold=math.isqrt(n)+1
    events=[[[] for _ in range(step)] for step in range(threshold+1)]
    for left,right,step,factor in queries:
        if step>threshold:
            for index in range(left,right+1,step):nums[index]=nums[index]*factor%mod
        else:
            residue=left%step;start=(left-residue)//step;end=(right-residue)//step
            events[step][residue].append((start,factor))
            if end+1<=(n-1-residue)//step:events[step][residue].append((end+1,pow(factor,mod-2,mod)))
    for step in range(1,threshold+1):
        for residue in range(step):
            changes=events[step][residue]
            if not changes:continue
            changes.sort();combined=[]
            for time,factor in changes:
                if combined and combined[-1][0]==time:combined[-1][1]=combined[-1][1]*factor%mod
                else:combined.append([time,factor])
            current=1;pointer=0;time=0
            for index in range(residue,n,step):
                while pointer<len(combined) and combined[pointer][0]==time:current=current*combined[pointer][1]%mod;pointer+=1
                nums[index]=nums[index]*current%mod;time+=1
    answer=0
    for value in nums:answer^=value
    return answer
'''

GRAPHICAL='''def simple_graph_exists(degrees):
    import bisect
    n=len(degrees);values=sorted(degrees,reverse=True)
    if any(value<0 or value>=n for value in values) or sum(values)%2:return False
    prefix=[0]
    for value in values:prefix.append(prefix[-1]+value)
    negative=[-value for value in values]
    for count in range(1,n+1):
        split=bisect.bisect_left(negative,-count,count)
        available=count*(count-1)+(split-count)*count+prefix[n]-prefix[split]
        if prefix[count]>available:return False
    return True
'''

GROUPS='''def can_partition_distinct_groups(nums,k):
    from collections import Counter
    groups,remainder=divmod(len(nums),k)
    if remainder:return False
    return max(Counter(nums).values())<=groups
'''

JUMPS='''def maximum_reachable_jump_values(nums):
    n=len(nums);prefix=[nums[0]]*n
    for i in range(1,n):prefix[i]=max(prefix[i-1],nums[i])
    answer=[0]*n;suffix_min=10**30
    for i in range(n-1,-1,-1):
        answer[i]=answer[i+1] if prefix[i]>suffix_min else prefix[i]
        suffix_min=min(suffix_min,nums[i])
    return answer
'''

WALLS='''def maximum_destroyed_walls(robots,distance,walls):
    import bisect
    from functools import lru_cache
    ordered=sorted(zip(robots,distance));walls=sorted(walls);n=len(ordered)
    def count(left,right):return bisect.bisect_right(walls,right)-bisect.bisect_left(walls,left)
    @lru_cache(None)
    def solve(i,next_right):
        if i<0:return 0
        position,reached=ordered[i];left=position-reached
        if i:left=max(left,ordered[i-1][0]+1)
        best=solve(i-1,0)+count(left,position)
        right=position+reached
        if i+1<n:
            if next_right==0:right=min(right,ordered[i+1][0]-ordered[i+1][1]-1)
            else:right=min(right,ordered[i+1][0]-1)
        best=max(best,solve(i-1,1)+count(position,right))
        return best
    return solve(n-1,1)
'''

def lesson(a,b,c,d):return [a,b,c,d]

X_CASES=[[a,q] for a,q in (([1],[[0,0,1,2]]),([2,3],[[1,1,1,4]]),([1,2,3],[[0,2,2,5]]),([10,20,30,40],[[0,3,1,1]]),([10**9],[[0,0,1,10**5]]),([2,3,5],[[0,2,1,10**5],[1,2,1,10**5]]),([7,7,7,7],[[0,3,3,2]]),([1,2,4,8,16],[[1,4,2,3],[0,4,4,5]]),([999999999,1],[[0,1,1,100000]]),([3,6,9,12,15],[[0,4,2,7],[1,3,1,11]]),([5,10,20],[[0,0,3,4],[2,2,2,6]]),([1,3,5,7,9,11],[[0,5,5,2],[1,5,2,3],[2,4,1,4]]))]
G_CASES=[[[0]],[[1]],[[0,0]],[[1,1]],[[2,1,1]],[[1,1,1]],[[3,3,3,3]],[[3,3,1,1]],[[4,3,3,2,2]],[[5,5,2,2,2,2]],[[2,2,2,2,2]],[[6,5,4,3,2,1,1]]]
P_CASES=[[a,k] for a,k in (([1],1),([1,1],1),([1,1],2),([1,2,3],2),([1,2,1,2],2),([1,1,1,2,2,2],3),([1,2,3,4,5,6],3),([1,1,2,2,3,3],2),([1,1,1,1,2,3,4,5],4),([5,4,3,2,1],5),([1,2,2,3,3,4,4,5],4),([7,7,8,8,9,9],3))]
J_CASES=[[x] for x in ([1],[1,2],[2,1],[1,1],[1,2,1],[3,2,1],[4,3,2,1],[1,2,3,4],[5,1,4,2,3],[2,2,1,3],[10,5,6,1,9],[3,8,2,7,1,6])]
W_CASES=[[r,d,w] for r,d,w in (([5],[2],[3,5,7]),([1,4],[10,1],[2,3,4,5]),([2,10],[1,5],[2,5,7]),([1,2],[100,1],[10]),([3,8,14],[4,4,4],[1,3,5,8,10,14,18]),([10,3],[5,1],[5,3,7]),([4,9],[3,3],[1,4,6,9,12]),([5,15,25],[20,2,20],[1,6,14,16,24,30]),([6,12],[5,5],[1,6,7,11,12,17]),([2,20,30],[10,10,10],[1,5,15,20,25,35]),([7],[1],[6,7,8]),([4,8,12,16],[3,3,3,3],[1,4,7,8,11,12,15,16,19]))]

BATCH={
3655:entry('xor_after_many_range_products',[('nums','list[int]'),('queries','list[list[int]]')],'int',['arrays','square root decomposition','modular arithmetic'],['Up to 100,000 values and queries.','Each inclusive arithmetic-progression range is multiplied modulo 1,000,000,007.','Return the XOR after all queries.'],[([[1,1,1],[[0,2,1,4]]],'Multiplying all three entries by four leaves XOR four.'),([[2,3,1,5,4],[[1,4,2,3],[0,2,1,2]]],'The final array [4,18,2,15,4] has XOR thirty-one.')],X_CASES,XOR_BATCH,[XOR_BATCH.replace('end+1','end'),XOR_BATCH.replace('range(left,right+1,step)','range(left,right,step)')],['Ends a deferred multiplier one progression position too early.','Treats the inclusive right endpoint as exclusive for large steps.'],xor_oracle,random_xor,lesson('Large steps touch few indices; small steps share residue-class progressions that support multiplicative difference events.','Apply large-step queries directly and record start/inverse-end events for each small step and residue.','Sweep every small progression, maintaining its active multiplier modulo M, then XOR the final values.','A factor enters exactly at its first progression coordinate and its inverse removes it just after the last, so every query affects precisely its requested indices.'),'O((n+q)*sqrt(n)*log M)','O(n*sqrt(n)+q)',8),
3656:entry('simple_graph_exists',[('degrees','list[int]')],'bool',['graphs','sorting','prefix sums'],['One to 100,000 requested degrees, each from zero to n-1.','The graph must be undirected and simple: no loops or parallel edges.','Return whether exactly this degree sequence is realizable.'],[([[3,1,2,2]],'Edges 0-1, 0-2, 0-3, and 2-3 realize these degrees.'),([[1,3,3,1]],'The two degree-three vertices force both degree-one vertices to have degree at least two.')],G_CASES,GRAPHICAL,[GRAPHICAL.replace(' or sum(values)%2',''),GRAPHICAL.replace('count*(count-1)+','')],['Ignores the handshake parity requirement.','Omits the possible edges among the highest-degree prefix.'],graph_oracle,random_graph,lesson('The Erdős-Gallai inequalities characterize graphical degree sequences.','Sort degrees downward and use prefix sums plus binary search to evaluate each inequality quickly.','Check even total degree, then compare every top-k demand with its maximum possible internal and suffix connections.','The handshake lemma supplies parity, and satisfying all Erdős-Gallai inequalities is necessary and sufficient for a simple graph.'),'O(n log n)','O(n)',6),
3659:entry('can_partition_distinct_groups',[('nums','list[int]'),('k','int')],'bool',['arrays','hash maps','counting'],['One to 100,000 values.','Every group has exactly k pairwise-distinct elements.','All occurrences must be used exactly once.'],[([[1,2,3,4],2],'Two groups of two distinct values use every element.'),([[3,5,2,2],2],'Place the two copies of two into separate groups with three and five.')],P_CASES,GROUPS,[GROUPS.replace('if remainder:return False',''),GROUPS.replace('<=groups','<groups')],['Allows a partial final group when the length is not divisible by k.','Rejects a value appearing exactly once per available group.'],groups_oracle,random_groups,lesson('If there are g=n/k groups, no value may appear more than g times.','Length divisibility and the maximum frequency are the only constraints.','Reject a remainder; otherwise count values and compare the largest count with n/k.','Distribute each value across distinct groups; the frequency bound prevents duplicates within a group and all groups have exactly k slots overall.'),'O(n)','O(n)',5),
3660:entry('maximum_reachable_jump_values',[('nums','list[int]')],'list[int]',['arrays','dynamic programming'],['One to 100,000 positive values.','Jump right only to a smaller value or left only to a larger value.','Return the maximum value reachable from every start.'],[([[2,1,3]],'The first two indices share maximum reachable value two; the last remains three.'),([[2,3,1]],'Every index can reach the value three through valid jumps.')],J_CASES,JUMPS,[JUMPS.replace('prefix[i]>suffix_min','prefix[i]>=suffix_min'),JUMPS.replace('else prefix[i]','else nums[i]')],['Merges regions across equal values even though jumps require strict inequality.','Returns only the current value at a region boundary instead of its prefix maximum.'],jump_oracle,random_jump,lesson('A suffix value below the current prefix maximum connects the current region to the already-solved region on its right.','Compute prefix maxima, then scan backward with the suffix minimum.','If prefix_max exceeds the later suffix minimum, copy the next answer; otherwise close a region at prefix_max.','The strict crossing supplies jumps in both directions between regions, while absence of a crossing makes the current prefix maximum the greatest reachable value.'),'O(n)','O(n)',5),
3661:entry('maximum_destroyed_walls',[('robots','list[int]'),('distance','list[int]'),('walls','list[int]')],'int',['arrays','dynamic programming','binary search'],['Up to 100,000 unique robot positions and unique wall positions.','Each robot fires once left or right within its distance; another robot blocks the shot.','Count each destroyed wall only once, including a wall at the firing robot position.'],[([[4],[3],[1,10]],'Firing left covers one through four and destroys the wall at one.'),([[10,2],[5,1],[5,2,7]],'The robots at ten and two fire left and destroy all three walls.')],W_CASES,WALLS,[WALLS.replace("if i:left=max(left,ordered[i-1][0]+1)","if i:pass"),WALLS.replace("else:right=min(right,ordered[i+1][0]-1)","else:pass")],['Lets a leftward bullet pass through the previous robot.','Lets a rightward bullet pass through the next robot.'],walls_oracle,random_walls,lesson('After sorting robots, only adjacent robots can block a shot; overlapping destruction depends on the next robot’s direction.','Use a two-state DP from right to left and count walls in each clipped interval by binary search.','State whether the next robot fired right; try the current robot left or right with the corresponding clipping bound.','The state captures the only possible overlap boundary, and every direction assignment appears in one DP path while interval counts remain unique.'),'O((n+w) log(n+w))','O(n+w)',8),
}
