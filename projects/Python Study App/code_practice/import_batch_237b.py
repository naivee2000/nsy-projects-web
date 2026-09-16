"""Forbidden swaps, grouped tree distances, diameter endpoints, split scores, and costs."""
from collections import Counter,deque
from itertools import combinations
from .import_batch_055 import entry


def forbidden_oracle(args):
    nums,forbidden=args;start=tuple(nums)
    if all(a!=b for a,b in zip(start,forbidden)):return 0
    queue=deque([(start,0)]);seen={start}
    while queue:
        state,moves=queue.popleft()
        for i,j in combinations(range(len(state)),2):
            nxt=list(state);nxt[i],nxt[j]=nxt[j],nxt[i];key=tuple(nxt)
            if key in seen:continue
            if all(a!=b for a,b in zip(key,forbidden)):return moves+1
            seen.add(key);queue.append((key,moves+1))
    return -1

def random_forbidden(rng):
    n=rng.randint(1,7);return [[rng.randint(1,4) for _ in range(n)],[rng.randint(1,4) for _ in range(n)]]

def interaction_oracle(args):
    n,edges,groups=args;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    answer=0
    for start in range(n):
        distance=[-1]*n;distance[start]=0;queue=deque([start])
        while queue:
            node=queue.popleft()
            for nxt in graph[node]:
                if distance[nxt]<0:distance[nxt]=distance[node]+1;queue.append(nxt)
        answer+=sum(distance[end] for end in range(start+1,n) if groups[end]==groups[start])
    return answer

def random_interaction(rng):
    n=rng.randint(1,10);return [n,[[i,rng.randrange(i)] for i in range(1,n)],[rng.randint(1,4) for _ in range(n)]]

def diameter_oracle(args):
    n,edges=args;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    distances=[]
    for start in range(n):
        dist=[-1]*n;dist[start]=0;queue=deque([start])
        while queue:
            node=queue.popleft()
            for nxt in graph[node]:
                if dist[nxt]<0:dist[nxt]=dist[node]+1;queue.append(nxt)
        distances.append(dist)
    diameter=max(map(max,distances));return ''.join('1' if max(distances[i])==diameter else '0' for i in range(n))

def random_diameter(rng):
    n=rng.randint(1,20);return [n,[[i,rng.randrange(i)] for i in range(1,n)]]

def split_oracle(args):
    nums=args[0];return max(sum(nums[:i])-min(nums[i:]) for i in range(1,len(nums)))

def random_split(rng):return [[rng.randint(-50,50) for _ in range(rng.randint(2,30))]]

def acquire_oracle(args):
    c1,c2,both,n1,n2=args
    return min(k*both+max(0,n1-k)*c1+max(0,n2-k)*c2 for k in range(max(n1,n2)+1))

def random_acquire(rng):return [rng.randint(1,30),rng.randint(1,30),rng.randint(1,30),rng.randint(0,20),rng.randint(0,20)]


FORBIDDEN='''def minimum_forbidden_swaps(nums,forbidden):
    n=len(nums);all_nums=Counter(nums);all_forbidden=Counter(forbidden)
    if any(all_nums[value]+all_forbidden[value]>n for value in all_nums):return -1
    bad=Counter(nums[i] for i in range(n) if nums[i]==forbidden[i]);total=sum(bad.values())
    return max((total+1)//2,max(bad.values(),default=0))
'''

INTERACTION='''def total_group_interaction_cost(n,edges,group):
    graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    parent=[-1]*n;depth=[0]*n;order=[0]
    for node in order:
        for child in graph[node]:
            if child!=parent[node]:parent[child]=node;depth[child]=depth[node]+1;order.append(child)
    maps=[None]*n;answer=0
    for node in reversed(order):
        current={group[node]:(1,depth[node])}
        for child in graph[node]:
            if parent[child]!=node:continue
            other=maps[child]
            if len(current)<len(other):current,other=other,current
            for color,(count,total_depth) in other.items():
                old_count,old_depth=current.get(color,(0,0))
                answer+=count*old_depth+old_count*total_depth-2*depth[node]*count*old_count
                current[color]=(old_count+count,old_depth+total_depth)
        maps[node]=current
    return answer
'''

DIAMETER='''def find_diameter_endpoints(n,edges):
    from collections import deque
    graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    def bfs(start):
        distance=[-1]*n;distance[start]=0;queue=deque([start]);far=start
        while queue:
            node=queue.popleft()
            if distance[node]>distance[far]:far=node
            for nxt in graph[node]:
                if distance[nxt]<0:distance[nxt]=distance[node]+1;queue.append(nxt)
        return far,distance
    first,_=bfs(0);second,left=bfs(first);_,right=bfs(second);diameter=left[second]
    return ''.join('1' if left[i]==diameter or right[i]==diameter else '0' for i in range(n))
'''

DIAMETER_WRONG_1=DIAMETER.replace("return ''.join('1' if left[i]==diameter or right[i]==diameter else '0' for i in range(n))","return ''.join('1' if i in (first,second) else '0' for i in range(n))")
DIAMETER_WRONG_2=DIAMETER.replace("left[i]==diameter or right[i]==diameter","len(graph[i])<=1")

SPLIT='''def maximum_split_score(nums):
    suffix=nums[-1];suffix_min=[0]*len(nums);suffix_min[-1]=suffix
    for index in range(len(nums)-2,-1,-1):suffix=min(nums[index],suffix);suffix_min[index]=suffix
    prefix=0;answer=-10**30
    for index in range(len(nums)-1):prefix+=nums[index];answer=max(answer,prefix-suffix_min[index+1])
    return answer
'''

ACQUIRE='''def minimum_acquisition_cost(cost1,cost2,cost_both,need1,need2):
    separate=need1*cost1+need2*cost2
    all_both=max(need1,need2)*cost_both
    shared=min(need1,need2);mixed=shared*cost_both+(need1-shared)*cost1+(need2-shared)*cost2
    return min(separate,all_both,mixed)
'''

def lesson(a,b,c,d):return [a,b,c,d]

F_CASES=[[a,b] for a,b in (([1],[1]),([1],[2]),([1,2],[1,2]),([1,2,3],[3,2,1]),([1,1,2],[1,2,2]),([1,1,1],[1,2,3]),([1,2,1,2],[1,2,2,1]),([1,2,3,4],[1,2,3,4]),([1,1,2,2],[2,1,2,1]),([1,1,2,2],[1,1,3,3]),([1,2,3,1,2],[1,3,2,2,1]),([4,4,3,2,1],[4,1,3,2,4]),([1,2,2,3,3,1],[1,2,3,3,1,2]),([1,1,2,3,4,4],[1,2,2,3,4,1]),([1,2,3,4,1,2,3],[1,2,4,3,2,1,3]))]
I_CASES=[[n,e,g] for n,e,g in ((1,[],[1]),(2,[[0,1]],[1,1]),(2,[[0,1]],[1,2]),(3,[[0,1],[1,2]],[1,1,1]),(3,[[0,1],[0,2]],[1,2,1]),(4,[[0,1],[1,2],[2,3]],[1,2,1,2]),(4,[[0,1],[0,2],[0,3]],[1,1,1,1]),(5,[[0,1],[1,2],[1,3],[3,4]],[1,2,1,2,1]),(5,[[0,1],[0,2],[2,3],[2,4]],[1,1,2,2,1]),(6,[[0,1],[1,2],[1,3],[3,4],[3,5]],[1,2,1,2,1,2]),(6,[[0,1],[0,2],[2,3],[3,4],[4,5]],[1,1,1,2,2,2]),(7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[1,2,3,1,2,3,1]),(8,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]],[1,2,1,2,1,2,1,2]),(9,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6],[6,7],[6,8]],[1,1,2,2,3,3,1,2,3]))]
D_CASES=[[n,e] for n,e in ((1,[]),(2,[[0,1]]),(3,[[0,1],[1,2]]),(4,[[0,1],[0,2],[0,3]]),(4,[[0,1],[1,2],[2,3]]),(5,[[0,1],[1,2],[1,3],[3,4]]),(5,[[0,1],[0,2],[2,3],[2,4]]),(6,[[0,1],[1,2],[1,3],[3,4],[3,5]]),(6,[[0,1],[0,2],[2,3],[3,4],[4,5]]),(7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]]),(8,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]]),(8,[[0,1],[0,2],[0,3],[1,4],[2,5],[3,6],[6,7]]),(9,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6],[6,7],[6,8]]),(10,[[0,1],[1,2],[2,3],[1,4],[4,5],[5,6],[4,7],[7,8],[7,9]]))]
S_CASES=[[[*v]] for v in ([1,2],[10,-1,3,-4,-5],[-1,-2],[-5,10],[3,3,3],[5,-10,4],[1,2,3,4],[-4,-3,-2,-1],[100,-100,50,-60],[2,-1,2,-1,2],[7,0,0,-8],[9,-2,-3,4,-5],[1,-10,20,-30,40],[50,40,30,20,10])]
A_CASES=[[a,b,c,x,y] for a,b,c,x,y in ((3,2,1,3,2),(1,1,5,3,4),(5,6,20,2,2),(10,10,3,0,0),(4,9,6,5,2),(9,4,6,2,5),(7,8,10,3,3),(2,100,3,10,1),(100,2,3,1,10),(5,5,5,4,7),(6,7,4,9,2),(20,30,25,6,6),(1,9,7,20,4),(12,3,8,5,11))]

BATCH={
3785:entry('minimum_forbidden_swaps',[('nums','list[int]'),('forbidden','list[int]')],'int',['arrays','hash maps','greedy'],['nums and forbidden have equal length up to 100,000.','Any two distinct nums positions may be swapped in one operation.','Make nums[i] differ from forbidden[i] everywhere, or return -1 if impossible.'],[([[1,2,3],[3,2,1]],'Only the middle position conflicts; swapping values at positions one and two resolves it in one move.'),([[1,1,1],[1,2,3]],'Three copies of one cannot avoid the sole position that also forbids one, so return -1.')],F_CASES,FORBIDDEN,[FORBIDDEN.replace('max((total+1)//2,max(bad.values(),default=0))','(total+1)//2'),FORBIDDEN.replace("if any(all_nums[value]+all_forbidden[value]>n for value in all_nums):return -1","if False:return -1")],['Ignores a dominant conflicting value that can fix only one bad position per swap.','Omits the global feasibility check for values with too few allowed positions.'],forbidden_oracle,random_forbidden,lesson('Only positions currently equal to their forbidden value must be repaired, but global value capacity determines feasibility.','A swap fixes at most two bad positions; two bad positions can pair only when their values differ.','The answer is the larger of half the bad count rounded up and the largest bad-value frequency, after checking count(nums=v)+count(forbidden=v)≤n.','The two lower bounds are achievable by pairing different bad values first and using feasible helper positions for the remaining dominant value.'),'O(n)','O(n)',8),
3786:entry('total_group_interaction_cost',[('n','int'),('edges','list[list[int]]'),('group','list[int]')],'int',['trees','small-to-large merging','depth-first search'],['n is up to 100,000; edges is a valid tree and group has length n.','Each unordered same-group pair contributes its tree distance.','Return the total contribution over all groups.'],[([3,[[0,1],[1,2]],[1,1,1]],'The three pair distances are one, one, and two, totaling four.'),([4,[[0,1],[0,2],[0,3]],[1,1,1,1]],'Six leaf/center or leaf/leaf pairs have total distance nine.')],I_CASES,INTERACTION,[INTERACTION.replace('-2*depth[node]*count*old_count','-depth[node]*count*old_count'),INTERACTION.replace('count*old_depth+old_count*total_depth-2*depth[node]*count*old_count','count*old_count')],['Subtracts the shared root depth only once instead of from both path endpoints.','Counts same-group pairs but ignores that their path lengths may exceed one.'],interaction_oracle,random_interaction,lesson('At a node, pairs whose lowest common ancestor is that node lie in different processed child maps or at the node itself.','Store per group both node count and sum of depths, merging smaller maps into the largest.','For two same-group sets, sum distance as countA·depthSumB + countB·depthSumA - 2·depthLCA·countA·countB.','Every same-group pair is counted exactly once when its two sides first meet at its lowest common ancestor.'),'O(n log n)','O(n)',8),
3787:entry('find_diameter_endpoints',[('n','int'),('edges','list[list[int]]')],'str',['trees','breadth-first search','graphs'],['1≤n≤100,000 and edges is a valid undirected tree.','Return one character per node: one iff it can end some longest path.','A one-node tree marks its only node.'],[([3,[[0,1],[1,2]]],'Nodes zero and two end the unique diameter, producing 101.'),([4,[[0,1],[0,2],[0,3]]],'Every leaf can pair with another leaf on a diameter, producing 0111.')],D_CASES,DIAMETER,[DIAMETER_WRONG_1,DIAMETER_WRONG_2],['Marks only the two endpoints selected by one diameter search and misses alternative tied endpoints.','Assumes every leaf is a diameter endpoint, including leaves on shorter branches.'],diameter_oracle,random_diameter,lesson('Find endpoints A and B of any diameter using two breadth-first searches.','A node is an endpoint of some diameter exactly when its distance from A or from B equals the diameter length.','Run BFS from both endpoints and mark that condition for every node.','Tree eccentricity satisfies max(dist(A,v),dist(B,v)); it equals the diameter precisely for possible diameter endpoints.'),'O(n)','O(n)',5),
3788:entry('maximum_split_score',[('nums','list[int]')],'int',['arrays','prefix sums'],['nums contains at least two and up to 100,000 signed integers.','Split after index i with 0≤i<n-1.','Score equals the prefix sum through i minus the minimum value strictly to its right.'],[([[10,-1,3,-4,-5]],'Splitting after 3 gives prefix twelve minus suffix minimum -5, producing the maximum score seventeen.'),([[1,2]],'The only split scores one minus two, or -1.')],S_CASES,SPLIT,[SPLIT.replace('suffix=min(nums[index],suffix)','suffix=max(nums[index],suffix)'),SPLIT.replace('prefix+=nums[index]','prefix=nums[index]')],['Uses a suffix maximum instead of the required suffix minimum.','Uses only the last prefix element rather than the complete prefix sum.'],split_oracle,random_split,lesson('Each split needs a left prefix sum and the minimum strictly to its right.','Precompute suffix minima, then scan split points while accumulating the prefix.','Evaluate prefix-suffixMin[i+1] at every legal split and keep the maximum.','The two precomputed quantities exactly match the score definition for each split, so examining all splits finds the optimum.'),'O(n)','O(n)',5),
3789:entry('minimum_acquisition_cost',[('cost1','int'),('cost2','int'),('cost_both','int'),('need1','int'),('need2','int')],'int',['math','greedy'],['Costs are positive and needs are nonnegative integers.','A both-item contributes one unit toward each requirement.','Requirements are lower bounds, so buying extra of one type is allowed.'],[([3,2,1,3,2],'Three both-items cost three and satisfy both lower bounds.'),([5,6,20,2,2],'Separate items cost twenty-two, cheaper than any both-item plan.')],A_CASES,ACQUIRE,[ACQUIRE.replace('return min(separate,all_both,mixed)','return separate'),ACQUIRE.replace('return min(separate,all_both,mixed)','return min(separate,mixed)')],['Never considers shared both-items.','Forbids buying extra coverage, missing the all-both optimum when it is cheaper.'],acquire_oracle,random_acquire,lesson('For a chosen number k of both-items, remaining needs are max(0,need1-k) and max(0,need2-k).','This piecewise-linear cost can change slope only at zero, min(need1,need2), or max(need1,need2).','Evaluate no both-items, exactly the shared minimum, and enough both-items for both requirements.','Between breakpoints the cost is linear, so an interval minimum occurs at an endpoint; these three plans cover every endpoint.'),'O(1)','O(1)',5),
}
