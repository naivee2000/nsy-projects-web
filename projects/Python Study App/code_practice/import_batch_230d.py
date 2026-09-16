"""Timed directed paths, GCD stability, power grids, component timing, and reverse grid moves."""
from collections import deque
from itertools import combinations
from math import gcd
from .import_batch_055 import entry

def timed_oracle(args):
    n,edges=args;distance=[10**30]*n;distance[0]=0
    changed=True
    while changed:
        changed=False
        for u,v,start,end in edges:
            leave=max(distance[u],start)
            if leave<=end and leave+1<distance[v]:distance[v]=leave+1;changed=True
    return -1 if distance[-1]==10**30 else distance[-1]

def random_timed(rng):
    n=rng.randint(1,7);pairs=[(u,v) for u in range(n) for v in range(n) if u!=v];rng.shuffle(pairs)
    edges=[]
    for u,v in pairs[:rng.randint(0,min(14,len(pairs)))]:
        start=rng.randint(0,12);edges.append([u,v,start,rng.randint(start,15)])
    return [n,edges]

def stability_oracle(args):
    nums,max_changes=args;n=len(nums);answer=n
    for count in range(max_changes+1):
        for changed in combinations(range(n),count):
            values=nums[:]
            for index in changed:values[index]=1
            longest=0
            for left in range(n):
                common=0
                for right in range(left,n):
                    common=gcd(common,values[right])
                    if common<2:break
                    longest=max(longest,right-left+1)
            answer=min(answer,longest)
    return answer

def random_stability(rng):
    n=rng.randint(1,8)
    return [[rng.randint(1,30) for _ in range(n)],rng.randint(0,n)]

def maintenance_oracle(args):
    c,connections,queries=args;graph=[[] for _ in range(c+1)]
    for u,v in connections:graph[u].append(v);graph[v].append(u)
    component=[0]*(c+1)
    for start in range(1,c+1):
        if component[start]:continue
        component[start]=start;queue=[start]
        for node in queue:
            for nxt in graph[node]:
                if not component[nxt]:component[nxt]=start;queue.append(nxt)
    online=set(range(1,c+1));answer=[]
    for kind,x in queries:
        if kind==2:online.discard(x)
        elif x in online:answer.append(x)
        else:answer.append(min((node for node in online if component[node]==component[x]),default=-1))
    return answer

def random_maintenance(rng):
    c=rng.randint(1,8);pairs=list(combinations(range(1,c+1),2));rng.shuffle(pairs)
    connections=[list(edge) for edge in pairs[:rng.randint(0,min(12,len(pairs)))]]
    queries=[[rng.choice((1,1,2)),rng.randint(1,c)] for _ in range(rng.randint(1,15))]
    return [c,connections,queries]

def components_oracle(args):
    n,edges,k=args
    for time in sorted({0}|{edge[2] for edge in edges}):
        parent=list(range(n))
        def find(x):
            while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
            return x
        for u,v,removed in edges:
            if removed>time:
                a,b=find(u),find(v)
                if a!=b:parent[a]=b
        if len({find(i) for i in range(n)})>=k:return time
    return 0

def random_components(rng):
    n=rng.randint(1,8);pairs=list(combinations(range(n),2));rng.shuffle(pairs)
    return [n,[[u,v,rng.randint(1,15)] for u,v in pairs[:rng.randint(0,min(12,len(pairs)))]],rng.randint(1,n)]

def moves_oracle(args):
    sx,sy,tx,ty=args;queue=deque([(sx,sy,0)]);seen={(sx,sy)}
    while queue:
        x,y,moves=queue.popleft()
        if (x,y)==(tx,ty):return moves
        step=max(x,y)
        if step==0:continue
        for state in ((x+step,y),(x,y+step)):
            if state[0]<=tx and state[1]<=ty and state not in seen:seen.add(state);queue.append((*state,moves+1))
    return -1

def random_moves(rng):
    sx,sy=rng.randint(0,5),rng.randint(0,5);tx,ty=sx,sy
    if rng.randrange(2):
        for _ in range(rng.randint(0,7)):
            step=max(tx,ty)
            if not step:break
            if rng.randrange(2):tx+=step
            else:ty+=step
    else:tx+=rng.randint(0,25);ty+=rng.randint(0,25)
    return [sx,sy,tx,ty]

TIMED='''def minimum_directed_arrival_time(n,edges):
    import heapq
    graph=[[] for _ in range(n)]
    for u,v,start,end in edges:graph[u].append((v,start,end))
    distance=[float('inf')]*n;distance[0]=0;heap=[(0,0)]
    while heap:
        time,node=heapq.heappop(heap)
        if time!=distance[node]:continue
        if node==n-1:return time
        for nxt,start,end in graph[node]:
            leave=max(time,start)
            if leave<=end and leave+1<distance[nxt]:distance[nxt]=leave+1;heapq.heappush(heap,(leave+1,nxt))
    return -1
'''

STABILITY='''def minimum_array_stability(nums,maxC):
    from math import gcd
    n=len(nums);logs=[0]*(n+1)
    for i in range(2,n+1):logs[i]=logs[i//2]+1
    table=[nums[:]]
    while 1<<len(table)<=n:
        step=1<<(len(table)-1);previous=table[-1]
        table.append([gcd(previous[i],previous[i+step]) for i in range(n-2*step+1)])
    def range_gcd(left,right):
        level=logs[right-left+1];width=1<<level
        return gcd(table[level][left],table[level][right-width+1])
    def possible(limit):
        changes=0;last_changed=-1
        for right in range(limit,n):
            left=right-limit
            if left>last_changed and range_gcd(left,right)>=2:
                changes+=1;last_changed=right
                if changes>maxC:return False
        return True
    low,high=0,n
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return low
'''

MAINTENANCE='''def process_power_grid_queries(c,connections,queries):
    import heapq
    parent=list(range(c+1))
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for u,v in connections:
        u=find(u);v=find(v)
        if u!=v:parent[u]=v
    heaps={}
    for station in range(1,c+1):heapq.heappush(heaps.setdefault(find(station),[]),station)
    online=[True]*(c+1);answer=[]
    for kind,x in queries:
        root=find(x);heap=heaps[root]
        if kind==2:online[x]=False
        elif online[x]:answer.append(x)
        else:
            while heap and not online[heap[0]]:heapq.heappop(heap)
            answer.append(heap[0] if heap else -1)
    return answer
'''

COMPONENTS='''def minimum_component_removal_time(n,edges,k):
    if k<=1:return 0
    parent=list(range(n));components=n
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for u,v,time in sorted(edges,key=lambda edge:edge[2],reverse=True):
        u=find(u);v=find(v)
        if u!=v:
            parent[u]=v;components-=1
            if components<k:return time
    return 0
'''

MOVES='''def minimum_max_coordinate_moves(sx,sy,tx,ty):
    from functools import lru_cache
    infinity=10**30
    @lru_cache(None)
    def reverse(x,y):
        if (x,y)==(sx,sy):return 0
        if x<sx or y<sy or (x==0 and y==0):return infinity
        if x==y:return 1+min(reverse(0,y),reverse(x,0))
        if x>y:
            previous=x-y if x<2*y else x//2 if x%2==0 else -1
            return infinity if previous<0 else 1+reverse(previous,y)
        previous=y-x if y<2*x else y//2 if y%2==0 else -1
        return infinity if previous<0 else 1+reverse(x,previous)
    answer=reverse(tx,ty)
    return -1 if answer>=infinity else answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

T_CASES=[[n,e] for n,e in ((1,[]),(2,[]),(2,[[0,1,0,0]]),(2,[[0,1,2,2]]),(3,[[0,1,0,0],[1,2,0,0]]),(4,[[0,1,0,2],[1,3,5,7],[0,2,3,5],[2,3,4,9]]),(3,[[1,0,1,3],[1,2,3,5]]),(3,[[0,1,5,4]]),(4,[[0,1,0,10],[1,2,2,2],[2,3,3,3]]),(3,[[0,1,10,20],[0,2,2,2],[2,1,3,3]]),(5,[[0,1,0,0],[1,4,100,100],[0,2,1,9],[2,3,2,9],[3,4,3,9]]),(3,[[0,1,0,5],[0,1,2,2],[1,2,1,1]]))]
G_CASES=[[a,k] for a,k in (([1],0),([2],0),([2],1),([2,4],0),([2,4],1),([2,4,9,6],1),([6,10,15],0),([6,10,15],1),([1,1,1],0),([4,8,16,32],2),([2,3,5,7],1),([12,18,5,10,15],2))]
M_CASES=[[c,e,q] for c,e,q in ((1,[],[[1,1]]),(1,[],[[2,1],[1,1]]),(2,[],[[1,2],[2,2],[1,2]]),(3,[[1,2]],[[2,1],[1,1],[1,3]]),(4,[[1,2],[3,4]],[[2,1],[1,1],[2,2],[1,1]]),(5,[[1,2],[2,3],[3,4],[4,5]],[[2,5],[1,5],[2,1],[1,1]]),(4,[[1,2],[2,3]],[[2,2],[1,2],[2,1],[1,1]]),(3,[[1,2],[2,3]],[[2,1],[2,2],[2,3],[1,2]]),(6,[[1,4],[2,5],[3,6]],[[2,1],[1,1],[2,4],[1,1]]),(5,[[1,2],[1,3],[4,5]],[[1,3],[2,3],[1,3]]),(4,[[1,2],[2,3],[3,1]],[[2,1],[1,1]]),(5,[],[[2,3],[1,3],[1,4]]))]
C_CASES=[[n,e,k] for n,e,k in ((1,[],1),(2,[],2),(3,[[0,2,5]],2),(3,[[0,1,3],[1,2,7]],3),(4,[[0,1,1],[1,2,1],[2,3,1]],2),(4,[[0,1,5],[2,3,2]],3),(5,[[0,1,9],[1,2,7],[2,3,5],[3,4,3]],4),(3,[[0,1,2],[1,2,2],[0,2,2]],2),(5,[],5),(4,[[0,1,10]],4),(6,[[0,1,1],[1,2,4],[3,4,2],[4,5,8]],5),(3,[[0,1,1],[1,2,10]],1))]
R_CASES=[[*x] for x in ((0,0,0,0),(1,1,1,1),(1,1,2,2),(0,1,3,2),(1,2,1,4),(1,2,5,2),(2,1,2,5),(0,2,4,6),(2,0,6,4),(3,5,16,10),(1,3,7,6),(2,2,8,4))]

BATCH={
3604:entry('minimum_directed_arrival_time',[('n','int'),('edges','list[list[int]]')],'int',['graphs','shortest paths','priority queues'],['Up to 100,000 nodes and directed timed edges.','An edge may be entered at any integer time in its inclusive availability interval.','Waiting and traversing each take one time unit; return -1 when unreachable.'],[([3,[[0,1,0,1],[1,2,2,5]]],'Travel, wait once, then travel to arrive at time three.'),([4,[[0,1,0,3],[1,3,7,8],[0,2,1,5],[2,3,4,7]]],'The route through node two arrives at time five.')],T_CASES,TIMED,[TIMED.replace('leave=max(time,start)','leave=time'),TIMED.replace('leave<=end','leave<end')],['Never waits for an edge to open.','Treats the inclusive closing time as exclusive.'],timed_oracle,random_timed,lesson('Only the earliest arrival at a node can improve future departures.','Run Dijkstra with waiting folded into each edge relaxation.','Depart at max(arrival,start) when it is no later than end, then arrive one unit later.','Waiting preserves FIFO order, so later arrivals cannot dominate earlier ones.'),'O((V+E) log V)','O(V+E)',6),
3605:entry('minimum_array_stability',[('nums','list[int]'),('maxC','int')],'int',['arrays','gcd','binary search','sparse tables'],['Up to 100,000 positive integers.','A stable subarray has GCD at least two.','Change at most maxC values arbitrarily to minimize the longest stable length.'],[([[3,5,10],1],'Changing five breaks the only stable length-two subarray, leaving stability one.'),([[2,6,8],2],'Two changes can destroy every stable subarray longer than one.')],G_CASES,STABILITY,[STABILITY.replace('left>last_changed','left>=last_changed'),STABILITY.replace('range_gcd(left,right)>=2','range_gcd(left,right)>2')],['Fails to recognize that a window containing the most recent change is already broken.','Treats GCD exactly two as unstable.'],stability_oracle,random_stability,lesson('Bounding stability by L means every stable window of length L+1 must be hit by a change.','Use a GCD sparse table and greedily change the right endpoint of each unhit violating window.','Count right-endpoint changes, then binary search the smallest feasible L.','Equal-length violating windows are intervals; earliest-ending greedy stabbing minimizes changes, and GCD queries verify each interval.'),'O(n log n)','O(n log n)',8),
3607:entry('process_power_grid_queries',[('c','int'),('connections','list[list[int]]'),('queries','list[list[int]]')],'list[int]',['graphs','union find','priority queues'],['Stations are numbered one through c and initially online.','Offline stations remain in their original connected component.','A check uses itself when online, otherwise the smallest online station in its component or -1.'],[([5,[[1,2],[2,3],[3,4],[4,5]],[[1,3],[2,1],[1,1],[2,2],[1,2]]],'The three checks are resolved by stations three, two, and three.'),([3,[],[[1,1],[2,1],[1,1]]],'The isolated station first answers itself, then has no online replacement.')],M_CASES,MAINTENANCE,[MAINTENANCE.replace('elif online[x]:answer.append(x)','elif False:answer.append(x)'),MAINTENANCE.replace('online[x]=False','online[find(x)]=False')],['Always returns the component minimum instead of an online queried station.','Takes the component representative offline instead of the requested station.'],maintenance_oracle,random_maintenance,lesson('Connectivity never changes, so components can be built once.','Give each component a min-heap and lazily discard offline heap tops.','Answer online x directly; otherwise clean and read its component heap.','Union-find fixes membership and lazy deletion always exposes the smallest remaining online ID.'),'O((C+E+Q) alpha(C)+Q log C)','O(C+E)',6),
3608:entry('minimum_component_removal_time',[('n','int'),('edges','list[list[int]]'),('k','int')],'int',['graphs','union find','offline processing'],['Up to 100,000 nodes and undirected timed edges.','At time t, every edge with removal time at most t is absent.','Return the earliest time with at least k connected components.'],[([2,[[0,1,3]],2],'Removing the only edge at time three creates two components.'),([3,[[0,1,2],[1,2,4]],3],'Both edges are gone at time four, creating three components.')],C_CASES,COMPONENTS,[COMPONENTS.replace('reverse=True','reverse=False'),COMPONENTS.replace('if components<k','if components<=k')],['Adds edges in the wrong chronological direction.','Uses a non-strict threshold and returns one removal event too early.'],components_oracle,random_components,lesson('After time t, exactly edges with larger removal times remain.','Process edges from latest to earliest while unioning components.','When adding an edge would reduce components below k, its time is the earliest required removal threshold.','Reverse processing represents every interval between removal events and union-find maintains the surviving graph.'),'O(E log E)','O(n)',5),
3609:entry('minimum_max_coordinate_moves',[('sx','int'),('sy','int'),('tx','int'),('ty','int')],'int',['math','reverse simulation','memoization'],['Coordinates are nonnegative and targets do not lie below the source.','A move adds max(x,y) to exactly one coordinate.','Return the minimum move count or -1 when unreachable.'],[([1,2,5,4],'Increase y by two, then x by four, using two moves.'),([0,1,2,3],'The path (0,1), (1,1), (2,1), (2,3) uses three moves.')],R_CASES,MOVES,[MOVES.replace('x%2==0','x%2==1'),MOVES.replace('if x==y:return 1+min(reverse(0,y),reverse(x,0))','if x==y:return infinity')],['Halves an odd dominant coordinate and rejects valid even reversals.','Declares every equal-coordinate target unreachable instead of considering its two possible predecessors.'],moves_oracle,random_moves,lesson('The larger target coordinate uniquely determines the previous state except when both coordinates are equal.','Reverse moves using subtraction below twice the other coordinate and halving above it.','At equality, try the two axis predecessors; memoize the branches.','These cases invert every possible forward move, while both coordinates decrease toward the source.'),'O(log(max target))','O(log(max target))',8),
}
