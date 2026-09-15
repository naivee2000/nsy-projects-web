"""Divisible permutations, threshold-graph distances, unit ratios, special grids, and road merges."""
from fractions import Fraction
from functools import lru_cache
from itertools import permutations

from .import_batch_055 import entry


def concatenation_oracle(args):
    nums,k=args;valid=[]
    for order in set(permutations(nums)):
        value=int(''.join(map(str,order)))
        if value%k==0:valid.append(order)
    return list(min(valid)) if valid else []


def random_concatenation(rng):return [[rng.randint(1,99) for _ in range(rng.randint(1,8))],rng.randint(1,30)]


def graph_distance_oracle(args):
    n,nums,max_diff,queries=args;graph=[[] for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            if abs(nums[i]-nums[j])<=max_diff:graph[i].append(j);graph[j].append(i)
    answer=[]
    for source,target in queries:
        distance=[-1]*n;distance[source]=0;queue=[source]
        for node in queue:
            for nxt in graph[node]:
                if distance[nxt]<0:distance[nxt]=distance[node]+1;queue.append(nxt)
        answer.append(distance[target])
    return answer


def random_graph_distance(rng):
    n=rng.randint(1,12);return [n,[rng.randint(0,30) for _ in range(n)],rng.randint(0,10),[[rng.randrange(n),rng.randrange(n)] for _ in range(rng.randint(1,15))]]


def conversion_query_oracle(args):
    conversions,queries=args;n=len(conversions)+1;graph=[[] for _ in range(n)]
    for source,target,factor in conversions:graph[source].append((target,Fraction(factor)));graph[target].append((source,Fraction(1,factor)))
    answer=[];modulo=1000000007
    for source,target in queries:
        stack=[(source,Fraction(1))];seen={source};ratio=None
        while stack:
            node,value=stack.pop()
            if node==target:ratio=value;break
            for nxt,factor in graph[node]:
                if nxt not in seen:seen.add(nxt);stack.append((nxt,value*factor))
        answer.append(ratio.numerator*pow(ratio.denominator,modulo-2,modulo)%modulo)
    return answer


def random_conversion_query(rng):
    n=rng.randint(2,10);edges=[]
    for node in range(1,n):
        parent=rng.randrange(node);factor=rng.randint(1,20)
        edges.append([parent,node,factor] if rng.randrange(2) else [node,parent,factor])
    return [edges,[[rng.randrange(n),rng.randrange(n)] for _ in range(rng.randint(1,15))]]


def special_grid_oracle(args):
    n=args[0];size=1<<n;answer=[]
    for row in range(size):
        current=[]
        for column in range(size):
            value=0
            for bit in range(n-1,-1,-1):
                lower=(row>>bit)&1;right=(column>>bit)&1
                quadrant=0 if not lower and right else 1 if lower and right else 2 if lower else 3
                value=value*4+quadrant
            current.append(value)
        answer.append(current)
    return answer


def random_special_grid(rng):return [rng.randint(0,3)]


def road_oracle(args):
    _,_,merges,positions,times=args
    @lru_cache(None)
    def solve(pos,rate,left):
        pos=list(pos);rate=list(rate)
        if left==0:return sum((pos[i+1]-pos[i])*rate[i] for i in range(len(pos)-1))
        return min(solve(tuple(pos[:i]+pos[i+1:]),tuple(rate[:i]+[rate[i]+rate[i+1]]+rate[i+2:]),left-1) for i in range(1,len(pos)-1))
    return solve(tuple(positions),tuple(times),merges)


def random_road(rng):
    n=rng.randint(2,8);positions=[0]
    for _ in range(n-1):positions.append(positions[-1]+rng.randint(1,6))
    merges=rng.randint(0,min(n-2,3));return [positions[-1],n,merges,positions,[rng.randint(1,12) for _ in range(n)]]


def houses_oracle(args):
    import heapq
    forward,backward,queries=args;n=len(forward);graph=[[] for _ in range(n)]
    for node in range(n):graph[node].append(((node+1)%n,forward[node]));graph[node].append(((node-1)%n,backward[node]))
    total=0;current=0
    for target in queries:
        distance=[10**30]*n;distance[current]=0;heap=[(0,current)]
        while heap:
            cost,node=heapq.heappop(heap)
            if cost!=distance[node]:continue
            for nxt,weight in graph[node]:
                if cost+weight<distance[nxt]:distance[nxt]=cost+weight;heapq.heappush(heap,(cost+weight,nxt))
        total+=distance[target];current=target
    return total


def random_houses(rng):
    n=rng.randint(2,10);length=rng.randint(1,15);queries=[];current=0
    for _ in range(length):
        target=rng.randrange(n)
        while target==current:target=rng.randrange(n)
        queries.append(target);current=target
    return [[rng.randint(1,15) for _ in range(n)],[rng.randint(1,15) for _ in range(n)],queries]


CONCATENATION='''def smallest_divisible_concatenation(nums,k):
    values=sorted(nums);n=len(values);powers=[pow(10,len(str(value)),k) for value in values]
    from functools import lru_cache
    @lru_cache(None)
    def possible(mask,remainder):
        if mask==(1<<n)-1:return remainder==0
        for index,value in enumerate(values):
            if not mask>>index&1 and possible(mask|1<<index,(remainder*powers[index]+value)%k):return True
        return False
    if not possible(0,0):return []
    answer=[];mask=remainder=0
    while mask!=(1<<n)-1:
        for index,value in enumerate(values):
            if mask>>index&1:continue
            nxt=(remainder*powers[index]+value)%k
            if possible(mask|1<<index,nxt):answer.append(value);mask|=1<<index;remainder=nxt;break
    return answer
'''


GRAPH_DISTANCE='''def minimum_threshold_graph_distances(n,nums,max_diff,queries):
    ordered=sorted((value,index) for index,value in enumerate(nums));rank=[0]*n
    for position,(_,index) in enumerate(ordered):rank[index]=position
    next_position=[0]*n;right=0
    for left in range(n):
        right=max(right,left)
        while right+1<n and ordered[right+1][0]-ordered[left][0]<=max_diff:right+=1
        next_position[left]=right
    levels=max(1,n.bit_length());jump=[next_position]
    for _ in range(1,levels):jump.append([jump[-1][jump[-1][i]] for i in range(n)])
    answer=[]
    for source,target in queries:
        if source==target:answer.append(0);continue
        left,right=sorted((rank[source],rank[target]));steps=0;current=left
        for level in range(levels-1,-1,-1):
            nxt=jump[level][current]
            if nxt<right and nxt>current:current=nxt;steps+=1<<level
        answer.append(steps+1 if next_position[current]>=right else -1)
    return answer
'''


CONVERSION_QUERY='''def query_unit_conversions(conversions,queries):
    modulo=1000000007;n=len(conversions)+1;graph=[[] for _ in range(n)]
    for source,target,factor in conversions:
        graph[source].append((target,factor%modulo));graph[target].append((source,pow(factor,modulo-2,modulo)))
    value=[0]*n;value[0]=1;stack=[(0,-1)]
    while stack:
        node,parent=stack.pop()
        for nxt,factor in graph[node]:
            if nxt!=parent:value[nxt]=value[node]*factor%modulo;stack.append((nxt,node))
    return [value[target]*pow(value[source],modulo-2,modulo)%modulo for source,target in queries]
'''


SPECIAL_GRID='''def build_special_grid(n):
    size=1<<n;grid=[[0]*size for _ in range(size)];value=0
    def fill(top,left,width):
        nonlocal value
        if width==1:grid[top][left]=value;value+=1;return
        half=width//2
        fill(top,left+half,half);fill(top+half,left+half,half);fill(top+half,left,half);fill(top,left,half)
    fill(0,0,size)
    return grid
'''


ROAD='''def minimum_travel_time_after_merges(l,n,k,position,time):
    prefix=[0]
    for value in time:prefix.append(prefix[-1]+value)
    infinity=10**30;states={(-1,0,0):0}
    for current in range(1,n):
        updated={}
        for (previous,last,removed),cost in states.items():
            new_removed=removed+current-last-1
            if new_removed>k:continue
            rate=time[0] if last==0 else prefix[last+1]-prefix[previous+1]
            key=(last,current,new_removed);updated[key]=min(updated.get(key,infinity),cost+(position[current]-position[last])*rate)
        for key,cost in updated.items():states[key]=min(states.get(key,infinity),cost)
    return min(cost for (previous,last,removed),cost in states.items() if last==n-1 and removed==k)
'''


HOUSES='''def minimum_circular_house_visit_time(forward,backward,queries):
    n=len(forward);forward_prefix=[0];backward_prefix=[0]
    for value in forward:forward_prefix.append(forward_prefix[-1]+value)
    for value in backward:backward_prefix.append(backward_prefix[-1]+value)
    def distance(source,target):
        clockwise=forward_prefix[target]-forward_prefix[source] if source<=target else forward_prefix[n]-forward_prefix[source]+forward_prefix[target]
        counter=backward_prefix[source+1]-backward_prefix[target+1] if source>=target else backward_prefix[source+1]+backward_prefix[n]-backward_prefix[target+1]
        return min(clockwise,counter)
    total=0;current=0
    for target in queries:total+=distance(current,target);current=target
    return total
'''


def lesson(a,b,c,d):return [a,b,c,d]


CONCAT_CASES=[[nums,k] for nums,k in [([3,12,45],5),([10,5],10),([1,2,3],5),([7],7),([7],3),([1,10],2),([12,12],3),([9,91,3],7),([2,20,200],4),([11,22,33],11),([5,15,25],5),([8,81,18,1],9),([4,40,44],8),([13,7,21,2],13)]]
GRAPH_CASES=[[n,nums,diff,queries] for n,nums,diff,queries in [
(5,[1,8,3,4,2],3,[[0,3],[2,4]]),(5,[5,3,1,9,10],2,[[0,1],[0,2],[2,3],[4,3]]),(3,[3,6,1],1,[[0,0],[0,1],[1,2]]),
(1,[4],0,[[0,0]]),(3,[1,1,1],0,[[0,1],[1,2]]),(4,[0,2,4,6],2,[[0,3],[0,2]]),(4,[0,3,6,9],2,[[0,3]]),
(5,[10,0,5,3,8],3,[[1,0],[1,4],[2,3]]),(6,[1,2,3,10,11,12],2,[[0,2],[0,5],[3,5]]),(4,[7,7,10,13],3,[[0,1],[0,3]]),
(5,[100,90,80,70,60],15,[[0,4],[1,3]]),(3,[0,5,10],5,[[0,2]]),(7,[4,1,7,10,13,16,19],3,[[1,6],[0,3]]),(5,[2,9,2,9,5],3,[[0,2],[0,4],[1,3]])]]
CONVERSION_CASES=[[edges,queries] for edges,queries in [
([[0,1,2],[0,2,6]],[[1,2],[1,0]]),([[0,1,2],[0,2,6],[0,3,8],[2,4,2],[2,5,4],[3,6,3]],[[1,2],[0,4],[6,5],[4,6],[6,1]]),
([[0,1,3]],[[0,1],[1,0],[1,1]]),([[1,0,2]],[[0,1],[1,0]]),([[0,1,5],[1,2,7]],[[0,2],[2,0]]),
([[1,0,2],[1,2,3]],[[0,2],[2,0]]),([[0,2,4],[2,1,5]],[[1,0],[0,1]]),([[0,1,1000000006]],[[0,1],[1,0]]),
([[0,1,2],[0,2,3],[2,3,4]],[[1,3],[3,1]]),([[1,0,3],[2,1,5],[2,3,7]],[[0,3],[3,0]]),
([[0,1,11],[1,2,13],[2,3,17]],[[1,3],[3,1]]),([[0,4,2],[4,3,3],[3,2,5],[2,1,7]],[[0,1],[1,4]]),
([[0,1,6],[2,1,10],[2,3,14]],[[0,3],[3,0]]),([[1,0,4],[1,2,9],[3,2,5],[3,4,7]],[[0,4],[4,0]])]]
GRID_CASES=[[n] for n in [0,1,2,3,4,0,1,2,3,4,0,1,2,3]]
ROAD_CASES=[list(case) for case in [
(10,4,1,[0,3,8,10],[5,8,3,6]),(5,5,1,[0,1,2,3,5],[8,3,9,3,3]),(5,2,0,[0,5],[4,9]),
(6,3,0,[0,2,6],[3,5,7]),(6,3,1,[0,2,6],[3,5,7]),(10,5,2,[0,2,5,7,10],[2,4,3,5,1]),
(12,6,3,[0,1,3,6,8,12],[5,1,4,2,3,6]),(8,4,1,[0,1,7,8],[9,2,8,1]),(9,5,1,[0,2,4,6,9],[1,2,3,4,5]),
(15,6,2,[0,3,5,9,12,15],[6,5,4,3,2,1]),(7,4,2,[0,1,3,7],[2,2,2,2]),(20,7,3,[0,2,5,9,12,16,20],[1,3,2,5,4,2,1]),
(11,5,0,[0,2,6,8,11],[7,1,9,2,3]),(14,6,1,[0,1,4,7,10,14],[2,8,1,8,2,8])]]
HOUSE_CASES=[[forward,backward,queries] for forward,backward,queries in [
([1,4,4],[4,1,2],[1,2,0,2]),([1,1,1,1],[2,2,2,2],[1,2,3,0]),([5,5],[5,5],[1]),
([1,10],[10,1],[1,0]),([3,4,5],[6,7,8],[2]),([3,4,5],[6,7,8],[1,0]),([10,1,10],[1,10,1],[2,1]),
([2,2,2,2,2],[9,9,9,9,9],[4,3,2,1]),([9,9,9,9],[1,1,1,1],[3,2,1,0]),([1,5,1,5],[5,1,5,1],[2,0]),
([7,3,8,2,6],[4,9,1,5,3],[1,4,2]),([100,1,1],[1,1,100],[2,1,0]),([2,7,4,9,3,8],[8,3,9,4,7,2],[5,2,4,1]),
([1,2,3,4,5],[5,4,3,2,1],[3,0,2,4])]]


BATCH={
3533:entry('smallest_divisible_concatenation',[('nums','list[int]'),('k','int')],'list[int]',['arrays','bitmask dynamic programming','modular arithmetic'],['nums has at most 13 positive integers and k is at most 100.','Permute every occurrence, concatenate decimal representations, and require divisibility by k.','Return the lexicographically smallest valid integer list, or [] when none exists.'],[([[3,12,45],5],'Both [3,12,45] and [12,3,45] work; the first is lexicographically smaller.'),([[10,5],10],'Only concatenation 510 is divisible by ten, so the answer is [5,10].')],CONCAT_CASES,CONCATENATION,[CONCATENATION.replace('values=sorted(nums)','values=sorted(nums,reverse=True)'),CONCATENATION.replace('remainder*powers[index]+value','remainder+value')],['Tries values in descending order and returns the lexicographically largest feasible permutation.','Updates the remainder by addition instead of decimal concatenation.'],concatenation_oracle,random_concatenation,lesson('A partial permutation is fully described by its used-index mask and current remainder.','Memoize whether each state can reach remainder zero, then reconstruct by trying remaining values in ascending order.','Append value with (remainder*10^digits+value)%k; choose the first candidate whose next state is feasible.','The DP explores every indexed permutation, while greedy reconstruction over feasible blocks produces the smallest value sequence, including duplicates.'),'O(2^n*n*k)','O(2^n*k)',8),
3534:entry('minimum_threshold_graph_distances',[('n','int'),('nums','list[int]'),('max_diff','int'),('queries','list[list[int]]')],'list[int]',['graphs','sorting','binary lifting','two pointers'],['nums has n values with n up to 100,000; nodes are joined when their value difference is at most max_diff.','Edges are unweighted and queries ask shortest path length, with zero for the same node and -1 if disconnected.','Return one distance per query.'],[([5,[1,8,3,4,2],3,[[0,3],[2,4]]],'Each queried pair differs by at most three, so both shortest paths use one edge.'),([5,[5,3,1,9,10],2,[[0,1],[0,2],[2,3],[4,3]]],'The answers include a direct edge, a two-hop chain, a disconnected pair, and another direct edge.')],GRAPH_CASES,GRAPH_DISTANCE,[GRAPH_DISTANCE.replace('steps+1 if next_position[current]>=right else -1','steps if next_position[current]>=right else -1'),GRAPH_DISTANCE.replace('<=max_diff','<max_diff')],['Omits the final edge after binary-lifting to just before the target.','Treats value differences equal to max_diff as disconnected.'],graph_distance_oracle,random_graph_distance,lesson('After sorting nodes by value, one step from a rank can reach every rank through its furthest value within maxDiff.','Compute each furthest one-step rank with two pointers and binary-lift repeated furthest jumps.','Map query nodes to ranks, greedily take largest jumps that stay before the target, then add the final edge or report -1.','Any shortest path can replace an intermediate neighbor by the furthest reachable rank without increasing hops, validating greedy jump composition.'),'O((n+queries) log n)','O(n log n)',8),
3535:entry('query_unit_conversions',[('conversions','list[list[int]]'),('queries','list[list[int]]')],'list[int]',['graphs','modular arithmetic','depth first search'],['The n-1 conversions form one connected unit tree, with either direction usable; factors are invertible modulo 1,000,000,007.','[source,target,factor] means one source unit equals factor target units.','For [A,B], return units B per one A as a modular fraction.'],[([[[0,1,2],[0,2,6]],[[1,2],[1,0]]],'Relative root values give 6/2=3 and 1/2, whose modular value is 500000004.'),([[[0,1,2],[0,2,6],[0,3,8],[2,4,2],[2,5,4],[3,6,3]],[[1,2],[0,4],[6,5],[4,6],[6,1]]],'Root-relative products and modular division produce [3,12,1,2,83333334].')],CONVERSION_CASES,CONVERSION_QUERY,[CONVERSION_QUERY.replace('pow(factor,modulo-2,modulo)','factor%modulo'),CONVERSION_QUERY.replace('value[target]*pow(value[source],modulo-2,modulo)','value[target]*value[source]')],['Uses the forward factor on reverse edges instead of its modular inverse.','Multiplies root-relative values instead of dividing target by source.'],conversion_query_oracle,random_conversion_query,lesson('Assign each unit a root-relative value; any A-to-B ratio is then value[B]/value[A].','Traverse the conversion tree bidirectionally, labeling reverse edges with modular inverses.','Propagate root values once, then answer each query with target value times inverse(source value).','Path products are consistent in a tree, and dividing two root paths cancels their shared portion to yield the requested conversion.'),'O(n+queries log M)','O(n)',6),
3538:entry('minimum_travel_time_after_merges',[('l','int'),('n','int'),('k','int'),('position','list[int]'),('time','list[int]')],'int',['arrays','dynamic programming','prefix sums'],['Positions are strictly increasing from 0 to l; n <= 50 and exactly k <= 10 internal signs must be removed.','Removing sign i adds its per-km time to the next sign’s time; endpoints cannot be removed.','After exactly k merges, minimize sum(distance segment * current per-km time).'],[([10,4,1,[0,3,8,10],[5,8,3,6]],'Removing position three makes rates [5,11] on distances eight and two, totaling 62.'),([5,5,1,[0,1,2,3,5],[8,3,9,3,3]],'Removing position one yields segment costs 16, 12, and 6, totaling 34.')],ROAD_CASES,ROAD,[ROAD.replace('prefix[last+1]-prefix[previous+1]','time[last]'),ROAD.replace('prefix[last+1]-prefix[previous+1]','prefix[last]-prefix[previous+1]')],['Ignores times accumulated from removed signs before the retained sign.','Excludes the retained sign’s own time from its accumulated outgoing rate.'],road_oracle,random_road,lesson('A retained sign’s rate equals the sum of original rates since the preceding retained sign, so pricing its outgoing segment needs the previous two retained boundaries.','Use prefix sums and DP states (previous retained, last retained, removed count), extending to each later retained sign.','Charge distance(last,current) times the accumulated rate at last, add skipped signs to the merge count, and require the endpoint with exactly k removals.','Every final retained-sign sequence uniquely defines all merged rate groups, and every legal merge result corresponds to one such sequence.'),'O(n^3*k)','O(n^2*k)',8),
3540:entry('minimum_circular_house_visit_time',[('forward','list[int]'),('backward','list[int]'),('queries','list[int]')],'int',['arrays','prefix sums','shortest paths'],['forward and backward describe directed clockwise and counterclockwise edge costs on a circle of up to 100,000 houses.','Start at house zero and visit query houses in order; every consecutive query target differs.','Return the minimum total travel time, choosing either direction independently for each leg.'],[([[1,4,4],[4,1,2],[1,2,0,2]],'The cheapest legs cost one, four, three, and four seconds, totaling twelve.'),([[1,1,1,1],[2,2,2,2],[1,2,3,0]],'Walking one forward edge for every leg completes the tour in four seconds.')],HOUSE_CASES,HOUSES,[HOUSES.replace('return min(clockwise,counter)','return clockwise'),HOUSES.replace('backward_prefix[source+1]','backward_prefix[source]')],['Always moves clockwise even when the backward route is cheaper.','Omits the backward edge leaving the source house in counterclockwise distances.'],houses_oracle,random_houses,lesson('Between two houses on a directed circle, every simple route is either entirely clockwise or entirely counterclockwise.','Prefix-sum the two directional edge arrays and compute both wrap-aware arc costs for each requested leg.','Starting at zero, add min(clockwise(source,target), counterclockwise(source,target)) and advance source to target.','Positive edge costs make extra cycles useless, so one of the two simple directional arcs is always an optimal leg.'),'O(n+queries)','O(n)',6),
}
