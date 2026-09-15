"""Circle barriers, weighted rerooting, noncrossing roads, monotone pairs, and trie costs."""
from collections import deque
from itertools import product
from functools import lru_cache
from .import_batch_055 import entry

def geometry_parts(width,height,circles):
    def inside(px,py,c):return (px-c[0])**2+(py-c[1])**2<=c[2]**2
    def a(c):x,y,r=c;return (x<=r and 0<=y<=height) or (abs(y-height)<=r and 0<=x<=width)
    def b(c):x,y,r=c;return (abs(x-width)<=r and 0<=y<=height) or (y<=r and 0<=x<=width)
    def touch(c,d):
        x,y,r=c;u,v,q=d
        return (x-u)**2+(y-v)**2<=(r+q)**2 and x*q+u*r<(r+q)*width and y*q+v*r<(r+q)*height
    return inside,a,b,touch
def corner_oracle(args):
    width,height,circles=args;inside,a,b,touch=geometry_parts(width,height,circles)
    if any(inside(0,0,c) or inside(width,height,c) for c in circles):return False
    graph=[[] for _ in circles]
    for i in range(len(circles)):
        for j in range(i):
            if touch(circles[i],circles[j]):graph[i].append(j);graph[j].append(i)
    queue=deque(i for i,c in enumerate(circles) if a(c));seen=set(queue)
    while queue:
        i=queue.popleft()
        if b(circles[i]):return False
        for j in graph[i]:
            if j not in seen:seen.add(j);queue.append(j)
    return True
def random_corner(rng):
    w=rng.randint(3,12);h=rng.randint(3,12);n=rng.randint(1,7)
    return [w,h,[[rng.randint(1,w+3),rng.randint(1,h+3),rng.randint(1,4)] for _ in range(n)]]

def time_oracle(args):
    edges=args[0];n=len(edges)+1;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    answer=[]
    for source in range(n):
        distance=[None]*n;distance[source]=0;queue=deque([source])
        while queue:
            node=queue.popleft()
            for child in graph[node]:
                if distance[child] is None:distance[child]=distance[node]+(1 if child%2 else 2);queue.append(child)
        answer.append(max(distance))
    return answer
def random_tree(rng):
    n=rng.randint(2,18);edges=[[i,rng.randrange(i)] for i in range(1,n)];rng.shuffle(edges);return [edges]

def road_oracle(args):
    n,queries=args;graph=[[] for _ in range(n)];answer=[]
    for i in range(n-1):graph[i].append(i+1)
    for u,v in queries:
        graph[u].append(v);dist=[-1]*n;dist[0]=0;queue=deque([0])
        while queue:
            node=queue.popleft()
            for nxt in graph[node]:
                if dist[nxt]<0:dist[nxt]=dist[node]+1;queue.append(nxt)
        answer.append(dist[-1])
    return answer
def random_noncrossing(rng):
    n=rng.randint(3,25)
    if rng.randrange(2):choices=[[0,v] for v in range(2,n)]
    else:choices=[[u,n-1] for u in range(n-2)]
    rng.shuffle(choices);return [n,choices[:rng.randint(1,len(choices))]]

def monotone_oracle(args):
    nums=args[0];answer=0
    for first in product(*(range(value+1) for value in nums)):
        second=tuple(value-a for value,a in zip(nums,first))
        answer+=all(a<=b for a,b in zip(first,first[1:])) and all(a>=b for a,b in zip(second,second[1:]))
    return answer
def random_monotone(rng):return [[rng.randint(1,6) for _ in range(rng.randint(1,7))]]

def cost_oracle(args):
    target,words,costs=args
    @lru_cache(None)
    def visit(index):
        if index==len(target):return 0
        options=[cost+visit(index+len(word)) for word,cost in zip(words,costs) if target.startswith(word,index) and visit(index+len(word))>=0]
        return min(options,default=-1)
    return visit(0)
def random_cost(rng):
    alphabet='abc';target=''.join(rng.choice(alphabet) for _ in range(rng.randint(1,10)));count=rng.randint(1,10)
    words=[''.join(rng.choice(alphabet) for _ in range(rng.randint(1,len(target)))) for _ in range(count)]
    return [target,words,[rng.randint(1,20) for _ in words]]

CORNER='''def rectangle_corner_reachable(x_corner,y_corner,circles):
    n=len(circles);parent=list(range(n+2));left_top=n;right_bottom=n+1
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b):parent[find(a)]=find(b)
    for i,(x,y,r) in enumerate(circles):
        if x*x+y*y<=r*r or (x-x_corner)**2+(y-y_corner)**2<=r*r:return False
        if (x<=r and 0<=y<=y_corner) or (abs(y-y_corner)<=r and 0<=x<=x_corner):union(i,left_top)
        if (abs(x-x_corner)<=r and 0<=y<=y_corner) or (y<=r and 0<=x<=x_corner):union(i,right_bottom)
        for j in range(i):
            u,v,q=circles[j]
            if ((x-u)**2+(y-v)**2<=(r+q)**2 and x*q+u*r<(r+q)*x_corner
                    and y*q+v*r<(r+q)*y_corner):union(i,j)
    return find(left_top)!=find(right_bottom)
'''
TIMES='''def all_tree_marking_times(edges):
    n=len(edges)+1;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    parent=[-1]*n;order=[0]
    for node in order:
        for child in graph[node]:
            if child!=parent[node]:parent[child]=node;order.append(child)
    down=[0]*n
    for node in reversed(order):
        down[node]=max([0]+[(1 if child%2 else 2)+down[child] for child in graph[node] if parent[child]==node])
    up=[0]*n;answer=[0]*n
    for node in order:
        branches=[((1 if child%2 else 2)+down[child],child) for child in graph[node] if parent[child]==node]
        best=sorted(branches,reverse=True)[:2];answer[node]=max(down[node],up[node])
        for child in graph[node]:
            if parent[child]==node:
                sibling=best[0][0] if best and best[0][1]!=child else best[1][0] if len(best)>1 else 0
                up[child]=(1 if node%2 else 2)+max(up[node],sibling)
    return answer
'''
ROADS='''def shortest_noncrossing_road_distances(n,queries):
    next_city=list(range(1,n));distance=n-1;answer=[]
    for start,end in queries:
        if next_city[start] and next_city[start]<end:
            city=next_city[start]
            while city<end:
                distance-=1;following=next_city[city];next_city[city]=0;city=following
            next_city[start]=end
        answer.append(distance)
    return answer
'''
MONOTONE='''def count_monotonic_array_pairs(nums):
    modulo=10**9+7;previous=[1]*(nums[0]+1)
    for index in range(1,len(nums)):
        prefix=[];total=0
        for value in previous:total=(total+value)%modulo;prefix.append(total)
        current=[0]*(nums[index]+1)
        for first in range(nums[index]+1):
            limit=min(first,first+nums[index-1]-nums[index])
            if limit>=0:current[first]=prefix[min(limit,len(prefix)-1)]
        previous=current
    return sum(previous)%modulo
'''
COST='''def minimum_string_construction_cost(target,words,costs):
    trie={}
    for word,cost in zip(words,costs):
        node=trie
        for char in word:node=node.setdefault(char,{})
        node['$']=min(node.get('$',10**30),cost)
    dp=[10**30]*(len(target)+1);dp[0]=0
    for start in range(len(target)):
        if dp[start]==10**30:continue
        node=trie
        for end in range(start,len(target)):
            if target[end] not in node:break
            node=node[target[end]]
            if '$' in node:dp[end+1]=min(dp[end+1],dp[start]+node['$'])
    return -1 if dp[-1]==10**30 else dp[-1]
'''
def lesson(a,b,c,d):return [a,b,c,d]

BATCH={
3235:entry('rectangle_corner_reachable',[('x_corner','int'),('y_corner','int'),('circles','list[list[int]]')],'bool',['geometry','union find','graphs'],['x_corner and y_corner are at least three; circles contain positive center coordinates and radii.','A path must stay inside the rectangle from (0,0) to (x_corner,y_corner) without touching any circle.','Return false when a circle covers an endpoint or connected circle obstacles join left/top to right/bottom.'],[([3,4,[[2,1,1]]],'The circle does not form a boundary-to-boundary barrier, so a route remains.'),([3,3,[[1,1,2]]],'The starting corner lies inside the circle, so no valid path exists.')],[[w,h,c] for w,h,c in [(3,3,[[2,1,1],[1,2,1]]),(4,4,[[5,5,1]]),(5,5,[[1,4,1]]),(5,5,[[4,1,1]]),(5,5,[[1,4,1],[4,1,1]]),(6,6,[[1,3,2],[4,5,2]]),(6,4,[[2,1,1],[3,2,1],[4,3,1]]),(10,10,[[5,5,1]]),(3,5,[[1,1,1]]),(8,6,[[2,5,2],[6,1,2]]),(8,8,[[4,4,5]]),(7,7,[[1,6,1],[3,5,2],[6,2,2]]),(9,5,[[4,1,2],[5,4,2]]),(4,6,[[5,3,1]])]],CORNER,[CORNER.replace('find(left_top)!=find(right_bottom)','True'),CORNER.replace('union(i,right_bottom)','union(i,left_top)')],['Ignores connected boundary barriers.','Classifies right/bottom contacts as left/top contacts, preventing barrier detection.'],corner_oracle,random_corner,lesson('A path is blocked exactly when obstacle components connect the rectangle’s left/top boundary to its right/bottom boundary.','Union intersecting circles and two virtual boundary nodes, while ignoring circle intersections occurring wholly beyond the relevant rectangle corner.','Reject covered endpoints; connect each circle to touched boundary sides and to qualifying intersecting circles.','Planar separation makes a left/top-to-right/bottom component necessary and sufficient for blocking opposite corners.'),'O(c² α(c))','O(c)',8),
3241:entry('all_tree_marking_times',[('edges','list[list[int]]')],'list[int]',['trees','rerooting','dynamic programming'],['edges describes a tree of 2–100,000 nodes numbered from zero.','Traversing into an odd node costs one time unit; traversing into an even node costs two.','For every possible initially marked node, return the maximum directed weighted distance to any node.'],[([[[0,1],[0,2]]],'Starting at nodes 0,1,2 takes 2,4,3 time respectively to reach every node.'),([[[0,1]]],'From zero, odd node one costs one; from one, even node zero costs two.')],[[e] for e in [[[0,1],[1,2]],[[0,1],[0,2],[0,3]],[[0,1],[1,2],[1,3]],[[0,1],[1,2],[2,3]],[[0,2],[2,1]],[[0,1],[0,2],[2,3]],[[0,3],[3,2],[2,1]],[[0,1],[1,2],[2,3],[3,4]],[[0,1],[0,2],[1,3],[1,4]],[[0,2],[2,4],[0,1],[2,3]],[[0,1],[0,2],[2,3],[2,4],[4,5]],[[0,1],[1,2],[1,3],[3,4],[3,5]],[[0,5],[5,4],[4,3],[3,2],[2,1]],[[0,1],[0,2],[1,3],[2,4],[2,5]]]],TIMES,[TIMES.replace('(1 if node%2 else 2)','(1 if child%2 else 2)'),TIMES.replace('max(down[node],up[node])','down[node]')],['Charges the child’s weight again when rerooting upward instead of the parent’s.','Reports only descendants under root zero and ignores paths through a parent.'],time_oracle,random_tree,lesson('Marking time along a path is the sum of entry costs of every node after the source.','Compute longest downward paths, then reroot while carrying the best path through parent or a sibling.','For each child use the parent entry cost plus max(parent-up, best other child branch).','The two passes partition every destination path by its first edge, so each source receives its exact weighted eccentricity.'),'O(n log degree)','O(n)',8),
3244:entry('shortest_noncrossing_road_distances',[('n','int'),('queries','list[list[int]]')],'list[int]',['graphs','greedy','linked lists'],['3≤n≤100,000 and the initial directed chain contains i→i+1.','Every query adds a forward shortcut, and no two shortcut intervals cross.','Return the current shortest 0-to-(n-1) edge count after every query.'],[([5,[[2,4],[0,2],[0,4]]],'The maintained route lengths become three, two, then one.'),([4,[[0,3],[0,2]]],'Once the direct edge exists, the distance remains one.')],[[n,q] for n,q in [(3,[[0,2]]),(4,[[0,2]]),(4,[[1,3]]),(5,[[0,3]]),(5,[[1,4]]),(6,[[0,2],[2,5]]),(6,[[0,4],[1,3]]),(7,[[1,6],[2,5]]),(7,[[0,6]]),(8,[[0,3],[3,7]]),(8,[[1,7],[2,6],[3,5]]),(9,[[0,4],[4,8]]),(10,[[0,5],[1,4],[5,9]]),(6,[[0,4],[0,3],[0,5]])]],ROADS,[ROADS.replace('distance-=1','distance+=1'),ROADS.replace('answer.append(distance)','answer.append(n-1)')],['Increases distance when bypassing a chain edge.','Always reports the original chain length after shortcuts.'],road_oracle,random_noncrossing,lesson('Noncrossing shortcuts let the current shortest route be represented as one forward linked chain.','When a useful shortcut arrives, splice out every active chain node strictly inside its interval.','Each removed link reduces the route length once; mark removed nodes with zero so they are never processed again.','Laminar intervals ensure a discarded chain segment can never be needed later, giving amortized linear splicing.'),'O(n+q)','O(n)',8),
3250:entry('count_monotonic_array_pairs',[('nums','list[int]')],'int',['dynamic programming','prefix sums'],['1≤len(nums)≤2,000 and 1≤nums[i]≤50.','Count nonnegative arrays arr1 and arr2 with arr1 nondecreasing, arr2 nonincreasing, and arr1[i]+arr2[i]=nums[i].','Return the count modulo 1,000,000,007.'],[([[2,3,2]],'Exactly four compatible choices of the nondecreasing first array determine valid second arrays.'),([[5,5,5,5]],'The number of nondecreasing four-term choices from zero through five is 126.')],[[a] for a in [[1],[2],[1,1],[1,2],[2,1],[2,2],[1,2,1],[3,1,3],[3,2,1],[1,2,3],[2,3,2],[4,4],[5,1],[1,5],[2,2,3],[3,3,2]]],MONOTONE,[MONOTONE.replace('min(first,first+nums[index-1]-nums[index])','first'),MONOTONE.replace('prefix[min(limit,len(prefix)-1)]','prefix[0]')],['Enforces only arr1 monotonicity and ignores the derived arr2 condition.','Counts only transitions from arr1 value zero.'],monotone_oracle,random_monotone,lesson('Choosing arr1 fixes arr2, so each transition only needs bounds on the previous arr1 value.','DP by index and current arr1 value; valid predecessors end at min(current, current+previous_num-current_num).','Use prefix sums of the previous DP row to total all valid predecessors in O(1).','The bound simultaneously expresses arr1 nondecreasing and arr2 nonincreasing, so every valid pair is counted once.'),'O(n max(nums))','O(max(nums))',7),
3253:entry('minimum_string_construction_cost',[('target','str'),('words','list[str]'),('costs','list[int]')],'int',['tries','dynamic programming','strings'],['target and words use lowercase letters; words and positive costs have equal length at most 50.','Starting empty, append any listed word any number of times and pay its cost each time.','Return the minimum cost to form target exactly, or -1 if impossible.'],[(['abcdef',['abdef','abc','d','def','ef'],[100,1,1,10,5]],'Appending abc, d, and ef costs 1+1+5=7.'),(['aaaa',['z','zz','zzz'],[1,10,100]],'No listed word can begin the target, so construction is impossible.')],[[t,w,c] for t,w,c in [('a',['a'],[3]),('a',['b'],[1]),('aa',['a','aa'],[2,5]),('aa',['a','aa'],[3,4]),('abc',['a','bc'],[2,3]),('abc',['ab','c'],[5,1]),('abc',['a','b'],[1,1]),('aaaa',['a','aa'],[2,3]),('abab',['ab','a','b'],[5,2,2]),('catcat',['cat','c','at'],[4,2,1]),('xyz',['x','y','z','xyz'],[2,2,2,7]),('leetcode',['leet','code','le','etcode'],[3,4,2,10]),('bbb',['b','bb'],[4,5]),('abcabc',['abc','ab','c'],[8,2,1])]],COST,[COST.replace("min(node.get('$',10**30),cost)","cost+1"),COST.replace('dp[start]+node[\'$\']','node[\'$\']')],['Adds an erroneous one-point surcharge every time a word is appended.','Forgets construction cost accumulated before the current word.'],cost_oracle,random_cost,lesson('A valid construction partitions target into dictionary words, which is a shortest-path DP over prefix positions.','Store words in a trie so every matching word from a prefix is found in one forward scan.','For each reachable start, walk the trie through target and relax dp[end+1] at terminal nodes.','Every append corresponds to one prefix edge; DP relaxation considers all such edges and therefore finds the minimum path cost.'),'O(total word length+n²)','O(total word length+n)',6),
}
