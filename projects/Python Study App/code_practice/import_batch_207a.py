"""Graph traversal, geometry, spanning-tree, and scheduling imports."""
from itertools import combinations
from math import acos, atan2, cos, hypot, pi, sin

from .import_batch_055 import entry


def watched_oracle(args):
    videos, friends, start, level = args
    frontier = {start}
    seen = {start}
    for _ in range(level):
        frontier = {friend for person in frontier for friend in friends[person] if friend not in seen}
        seen.update(frontier)
    counts = {}
    for person in frontier:
        for title in videos[person]:
            counts[title] = counts.get(title, 0) + 1
    return sorted(counts, key=lambda title: (counts[title], title))


def random_watched(rng):
    size = rng.randint(1, 9)
    edges = [{index + 1} for index in range(size - 1)] + [set()]
    for index in range(size - 1):
        edges[index + 1].add(index)
    for left in range(size):
        for right in range(left + 2, size):
            if rng.random() < .25:
                edges[left].add(right); edges[right].add(left)
    videos = [[rng.choice(['a', 'b', 'c', 'd', 'e']) for _ in range(rng.randint(1, 4))] for _ in range(size)]
    start = rng.randrange(size)
    return [videos, [sorted(row) for row in edges], start, rng.randint(0, size)]


def darts_oracle(args):
    points, radius = args
    if not points:
        return 0
    centers = [(float(x), float(y)) for x, y in points]
    for first, second in combinations(points, 2):
        x1, y1 = first; x2, y2 = second
        dx, dy = x2 - x1, y2 - y1
        distance = hypot(dx, dy)
        if distance == 0 or distance > 2 * radius + 1e-10:
            continue
        middle_x, middle_y = (x1 + x2) / 2, (y1 + y2) / 2
        offset = (max(0.0, radius * radius - distance * distance / 4)) ** .5
        ux, uy = -dy / distance, dx / distance
        centers.extend([(middle_x + ux * offset, middle_y + uy * offset),
                        (middle_x - ux * offset, middle_y - uy * offset)])
    return max(sum(hypot(x - cx, y - cy) <= radius + 1e-8 for x, y in points) for cx, cy in centers)


def random_darts(rng):
    size = rng.randint(1, 9)
    points = rng.sample([(x, y) for x in range(-6, 7) for y in range(-6, 7)], size)
    return [[list(point) for point in points], rng.randint(1, 5)]


def mst_oracle(args):
    size, edges = args
    trees = []
    for chosen in combinations(range(len(edges)), size - 1):
        parent = list(range(size))
        def find(node):
            while parent[node] != node:
                parent[node] = parent[parent[node]]; node = parent[node]
            return node
        valid = True
        for index in chosen:
            left, right, _ = edges[index]
            a, b = find(left), find(right)
            if a == b:
                valid = False; break
            parent[a] = b
        if valid and len({find(node) for node in range(size)}) == 1:
            trees.append((sum(edges[index][2] for index in chosen), set(chosen)))
    best = min(weight for weight, _ in trees)
    winners = [chosen for weight, chosen in trees if weight == best]
    critical = [index for index in range(len(edges)) if all(index in chosen for chosen in winners)]
    pseudo = [index for index in range(len(edges)) if index not in critical and any(index in chosen for chosen in winners)]
    return [critical, pseudo]


def random_mst(rng):
    size = rng.randint(2, 6)
    pairs = [(left, right) for left in range(size) for right in range(left + 1, size)]
    chosen = {(index, index + 1) for index in range(size - 1)}
    for pair in pairs:
        if rng.random() < .3:
            chosen.add(pair)
    edges = [[left, right, rng.randint(1, 8)] for left, right in sorted(chosen)]
    rng.shuffle(edges)
    return [size, edges]


def busiest_oracle(args):
    size, arrival, load = args
    free = [0] * size; handled = [0] * size
    for index, (time, duration) in enumerate(zip(arrival, load)):
        for offset in range(size):
            server = (index + offset) % size
            if free[server] <= time:
                handled[server] += 1; free[server] = time + duration; break
    best = max(handled)
    return [index for index, count in enumerate(handled) if count == best]


def random_busiest(rng):
    size = rng.randint(1, 8); count = rng.randint(1, 20)
    arrival = []; time = 0
    for _ in range(count):
        time += rng.randint(1, 4); arrival.append(time)
    return [size, arrival, [rng.randint(1, 10) for _ in range(count)]]


def visible_oracle(args):
    points, angle, location = args
    same = sum(point == location for point in points)
    directions = [atan2(y - location[1], x - location[0]) % (2 * pi) for x, y in points if [x, y] != location]
    if angle == 360:
        return len(points)
    width = angle * pi / 180
    return same + max((sum((direction - start) % (2 * pi) <= width + 1e-12 for direction in directions)
                       for start in directions), default=0)


def random_visible(rng):
    location = [rng.randint(-3, 3), rng.randint(-3, 3)]
    points = [[rng.randint(-6, 6), rng.randint(-6, 6)] for _ in range(rng.randint(1, 12))]
    return [points, rng.randint(0, 360), location]


WATCHED = '''def videos_at_friend_level(watched_videos,friends,id,level):
    frontier={id};seen={id}
    for _ in range(level):
        following=set()
        for person in frontier:
            for friend in friends[person]:
                if friend not in seen:following.add(friend)
        seen.update(following);frontier=following
    counts={}
    for person in frontier:
        for title in watched_videos[person]:counts[title]=counts.get(title,0)+1
    return sorted(counts,key=lambda title:(counts[title],title))
'''

DARTS = '''def maximum_darts_in_circle(points,r):
    import math
    answer=1
    for index,(x1,y1) in enumerate(points):
        events=[]
        for other,(x2,y2) in enumerate(points):
            if index==other:continue
            distance=math.hypot(x2-x1,y2-y1)
            if distance>2*r+1e-10:continue
            direction=math.atan2(y2-y1,x2-x1)
            delta=math.acos(min(1.0,distance/(2*r)))
            start=(direction-delta)%(2*math.pi);end=(direction+delta)%(2*math.pi)
            events.append((start,1));events.append((end,-1))
            if start>end:events.append((0,1));events.append((2*math.pi,-1))
        current=1
        for _,kind in sorted(events,key=lambda item:(item[0],-item[1])):
            current+=kind;answer=max(answer,current)
    return answer
'''

MST = '''def classify_mst_edges(n,edges):
    ordered=sorted([(weight,left,right,index) for index,(left,right,weight) in enumerate(edges)])
    def cost(skip=-1,force=-1):
        parent=list(range(n))
        def find(node):
            while parent[node]!=node:
                parent[node]=parent[parent[node]];node=parent[node]
            return node
        total=used=0
        if force>=0:
            left,right,weight=edges[force];parent[find(left)]=find(right);total=weight;used=1
        for weight,left,right,index in ordered:
            if index==skip or index==force:continue
            a,b=find(left),find(right)
            if a!=b:parent[a]=b;total+=weight;used+=1
        return total if used==n-1 else float('inf')
    best=cost();critical=[];pseudo=[]
    for index in range(len(edges)):
        if cost(skip=index)>best:critical.append(index)
        elif cost(force=index)==best:pseudo.append(index)
    return [critical,pseudo]
'''

BUSIEST = '''def busiest_servers(k,arrival,load):
    import heapq
    available=list(range(k));busy=[];count=[0]*k
    for index,(time,duration) in enumerate(zip(arrival,load)):
        while busy and busy[0][0]<=time:
            _,server=heapq.heappop(busy);heapq.heappush(available,index+(server-index)%k)
        if not available:continue
        server=heapq.heappop(available)%k;count[server]+=1
        heapq.heappush(busy,(time+duration,server))
    best=max(count)
    return [server for server,value in enumerate(count) if value==best]
'''

BUSIEST_PREFERRED = '''def busiest_servers(k,arrival,load):
    free=[0]*k;count=[0]*k
    for index,(time,duration) in enumerate(zip(arrival,load)):
        server=index%k
        if free[server]<=time:
            free[server]=time+duration;count[server]+=1
    best=max(count)
    return [server for server,value in enumerate(count) if value==best]
'''

BUSIEST_ZERO = '''def busiest_servers(k,arrival,load):
    return [0]
'''

VISIBLE = '''def maximum_visible_points(points,angle,location):
    import math
    same=0;directions=[]
    for x,y in points:
        if [x,y]==location:same+=1
        else:directions.append(math.atan2(y-location[1],x-location[0])%(2*math.pi))
    if angle==360:return len(points)
    directions.sort();extended=directions+[value+2*math.pi for value in directions]
    width=angle*math.pi/180;left=0;answer=0
    for right,value in enumerate(extended):
        while value-extended[left]>width+1e-12:left+=1
        if left<len(directions):answer=max(answer,min(right-left+1,len(directions)))
    return answer+same
'''


def lesson(a, b, c, d):
    return [a, b, c, d]


BATCH = {
1311: entry('videos_at_friend_level',[('watched_videos','list[list[str]]'),('friends','list[list[int]]'),('id','int'),('level','int')],'list[str]',['graphs','breadth-first search','sorting'],['There are 1 through 100 people; friendship is undirected and every person is reachable from every other.','Collect videos watched by friends at exactly the requested shortest-path level, including repeated titles.','Sort titles by increasing frequency, breaking ties alphabetically.'],[([[['A','B'],['C'],['B','C'],['D']],[[1,2],[0,3],[0,3],[1,2]],0,1],'Level one contains people one and two. B and C each occur once, so alphabetical order gives B then C.'),([[['x'],['z','z'],['a'],['z']],[[1],[0,2],[1,3],[2]],0,2],'Only person two is exactly two edges away, so the answer is a.')],[[v,f,i,l] for v,f,i,l in [([['a']],[[]],0,0),([['a'],['b']],[[1],[0]],0,1),([['a'],['b']],[[1],[0]],1,0),([['a'],['b'],['c']],[[1],[0,2],[1]],0,2),([['a'],['b','b'],['a']],[[1,2],[0],[0]],0,1),([['z'],['b'],['a']],[[1,2],[0],[0]],0,1),([['a'],['x'],['x'],['y']],[[1,2],[0,3],[0,3],[1,2]],0,1),([['a'],['x'],['x'],['y']],[[1,2],[0,3],[0,3],[1,2]],0,2),([['m'],['a','z'],['z','a']],[[1,2],[0],[0]],0,1),([['q'],['c'],['b'],['a']],[[1],[0,2],[1,3],[2]],0,3),([['a','a'],['b'],['c']],[[1],[0,2],[1]],1,1),([['a'],['d'],['c'],['b']],[[1,2,3],[0],[0],[0]],0,1),([['a'],['b'],['b'],['a']],[[1,2],[0,3],[0,3],[1,2]],3,1),([['a'],['b'],['c'],['d'],['e']],[[1],[0,2],[1,3],[2,4],[3]],2,2)]],WATCHED,[WATCHED.replace('range(level)','range(max(0,level-1))'),WATCHED.replace('(counts[title],title)','(title,counts[title])')],['Stops one friendship layer early.','Sorts alphabetically before frequency instead of using frequency as the primary key.'],watched_oracle,random_watched,lesson('Breadth-first layers equal shortest friendship distance.','Expand a frontier while permanently marking every reached person.','After level expansions, count only that frontier’s titles and sort by (frequency,title).','A visited set prevents cycles and guarantees the frontier contains exactly the requested shortest-distance layer.'),'O(people+friendships+videos log videos)','O(people+titles)',5),
1453: entry('maximum_darts_in_circle',[('darts','list[list[int]]'),('r','int')],'int',['geometry','sliding windows'],['There are 1 through 100 distinct integer points and radius is positive.','Choose any circle of radius r and count points on or inside its boundary.','Return the greatest possible count.'],[([[[ -2,0],[2,0],[0,2],[0,-2]],2],'A radius-two circle centered at the origin contains all four boundary points.'),([[[1,2],[3,5],[1,-1],[2,3],[4,1],[1,3]],2],'A suitable radius-two circle contains four of the six points.')],[[p,r] for p,r in [([[0,0]],1),([[0,0],[2,0]],1),([[0,0],[3,0]],1),([[0,0],[1,0],[2,0]],1),([[0,0],[1,1],[-1,1]],1),([[0,0],[2,0],[1,1]],1),([[1,1],[1,-1],[-1,1],[-1,-1]],2),([[0,0],[4,0],[2,0]],2),([[0,0],[0,1],[0,2],[0,3]],1),([[0,0],[1,0],[0,1],[1,1]],1),([[-3,0],[0,0],[3,0]],2),([[5,5],[6,5],[5,6]],1),([[0,0],[2,0],[0,2],[2,2]],1),([[0,0],[1,2],[2,1],[-1,1]],2)]],DARTS,[DARTS.replace('distance>2*r+1e-10','distance>r+1e-10'),DARTS.replace('answer=1','answer=0')],['Rejects pairs farther than one radius even though their separation may be as large as the diameter.','Forgets that the fixed anchor point itself is always inside the candidate circle.'],darts_oracle,random_darts,lesson('Fix one contained point and describe possible circle centers by their direction around it.','Every other point within the diameter contributes an interval of center directions that includes both points.','Create interval start/end events with wraparound, then sweep for the maximum overlap.','An optimal circle can be shifted until a point reaches its boundary, so some anchored sweep represents it; overlapping intervals are exactly simultaneously covered points.'),'O(n² log n)','O(n)',8),
1489: entry('classify_mst_edges',[('n','int'),('edges','list[list[int]]')],'list[list[int]]',['graphs','minimum spanning trees','union-find'],['The connected undirected graph has 2 through 100 vertices and at most 200 uniquely indexed edges.','An edge is critical if removing it raises the MST weight; it is pseudo-critical if some, but not every, MST contains it.','Return [critical_indices, pseudo_critical_indices], each in increasing input-index order.'],[([5,[[0,1,1],[1,2,1],[2,3,2],[0,3,2],[0,4,3],[3,4,3],[1,4,6]]],'Edges zero and one occur in every minimum tree; edges two through five can each occur in at least one minimum tree.'),([4,[[0,1,1],[1,2,1],[2,3,1],[0,3,1]]],'Every edge belongs to some weight-three spanning tree, but none belongs to all of them.')],[[n,e] for n,e in [(2,[[0,1,1]]),(3,[[0,1,1],[1,2,2],[0,2,3]]),(3,[[0,1,1],[1,2,1],[0,2,1]]),(4,[[0,1,1],[1,2,2],[2,3,3],[0,3,10]]),(4,[[0,1,1],[1,2,1],[2,3,1],[0,3,1]]),(4,[[0,1,1],[0,2,1],[0,3,1],[1,2,2]]),(4,[[0,1,5],[1,2,1],[2,3,1],[0,3,1],[0,2,2]]),(5,[[0,1,1],[1,2,1],[2,3,1],[3,4,1],[0,4,2]]),(5,[[0,1,2],[1,2,2],[2,3,2],[3,4,2],[0,4,2]]),(3,[[0,1,2],[1,2,2],[0,2,3]]),(4,[[0,1,1],[1,2,2],[2,3,2],[0,3,2],[0,2,3]]),(5,[[0,1,1],[1,2,2],[2,3,1],[3,4,2],[0,4,3],[1,4,3]]),(6,[[0,1,1],[1,2,1],[2,3,1],[3,4,1],[4,5,1],[0,5,1]]),(4,[[0,1,1],[2,3,1],[1,2,5],[0,3,5]])]],MST,[MST.replace('cost(skip=index)>best','cost(skip=index)>=best'),MST.replace("elif cost(force=index)==best:pseudo.append(index)","else:pseudo.append(index)")],['Labels an edge critical even when excluding it leaves another MST of equal weight.','Labels every noncritical edge pseudo-critical without proving it can belong to an MST.'],mst_oracle,random_mst,lesson('Compare every edge against the unconstrained MST weight.','Re-run Kruskal once excluding the edge and once forcing it first.','A higher exclusion cost means critical; otherwise equal forced cost means pseudo-critical.','These tests directly encode membership in all optimal trees versus at least one optimal tree.'),'O(E² alpha(V))','O(V+E)',8),
1606: entry('busiest_servers',[('k','int'),('arrival','list[int]'),('load','list[int]')],'list[int]',['heaps','simulation','scheduling'],['There are k servers and strictly increasing arrival times; arrival and load have equal length.','Request i prefers i mod k and then the next available server cyclically; drop it if all servers are busy.','Return every server handling the maximum number of requests, in increasing index order.'],[([3,[1,2,3,4,5],[5,2,3,3,3]],'Server one handles two requests while servers zero and two handle one each.'),([3,[1,2,3,4],[1,2,1,2]],'Each request finds its preferred server available; server zero handles two and is busiest.')],[[k,a,l] for k,a,l in [(1,[1],[1]),(1,[1,2,3],[5,1,1]),(2,[1,2],[1,1]),(2,[1,2,3],[3,3,1]),(3,[1,2,3],[10,10,10]),(3,[1,3,5],[1,1,1]),(2,[1,5,6,7],[3,1,1,1]),(4,[1,2,3,4],[1,1,1,1]),(4,[1,2,3,4,5],[5,5,5,5,1]),(3,[1,2,10],[2,2,1]),(2,[1,2,4,5],[2,2,2,2]),(5,[1,2,3],[10,10,10]),(3,[1,2,3,4,5,6],[1,1,1,1,1,1]),(3,[1,4,5,6,10],[2,10,1,1,1])]],BUSIEST,[BUSIEST_PREFERRED,BUSIEST_ZERO],['Checks only the preferred server and fails to wrap to another available server.','Assumes server zero is always the unique busiest server.'],busiest_oracle,random_busiest,lesson('Maintain busy servers by finish time and available servers by cyclic preference order.','Release finished servers using shifted keys relative to the current request index.','Pop the smallest shifted available key, reduce modulo k, count it, and push its finish time.','The shift maps cyclic order starting at i mod k into ordinary increasing heap order.'),'O(requests log k)','O(k)',8),
1610: entry('maximum_visible_points',[('points','list[list[int]]'),('angle','int'),('location','list[int]')],'int',['geometry','sorting','sliding windows'],['There are 1 through 100000 points; the observer stays at location and may face any direction.','A point is visible when its direction lies in a closed viewing sector of angle degrees; points at location are always visible.','Return the maximum visible count.'],[([[[2,1],[2,2],[3,3]],90,[1,1]],'Facing northeast with a ninety-degree view includes all three directions.'),([[[2,1],[2,2],[3,4],[1,1]],30,[1,1]],'The point at the observer is always visible, and the best narrow sector contains two more points.')],[[p,a,l] for p,a,l in [([[1,0]],0,[0,0]),([[0,0]],0,[0,0]),([[1,0],[-1,0]],180,[0,0]),([[1,0],[-1,0]],179,[0,0]),([[1,0],[0,1]],90,[0,0]),([[1,0],[0,1]],89,[0,0]),([[1,1],[2,2],[3,3]],0,[0,0]),([[1,0],[0,-1]],90,[0,0]),([[1,0],[0,1],[-1,0],[0,-1]],90,[0,0]),([[2,2],[2,2],[0,0]],1,[1,1]),([[0,0],[1,0],[0,1]],360,[0,0]),([[5,5],[6,6],[7,5]],45,[5,5]),([[-1,0],[-2,0],[1,0]],0,[0,0]),([[2,1],[2,2],[3,4]],30,[1,1])]],VISIBLE,[VISIBLE.replace('if angle==360:return len(points)','if angle==360:return len(directions)'),VISIBLE.replace('answer+same','answer')],['Drops points located at the observer when the sector is a full circle.','Never adds points coincident with the observer to the directional-window count.'],visible_oracle,random_visible,lesson('Convert every noncoincident point to a polar direction.','Sort angles, duplicate them plus 2π, and find the longest window within the viewing width.','Advance a left pointer whenever the angular difference exceeds the closed sector width.','Duplicating directions linearizes sectors crossing zero; coincident points add to every orientation.'),'O(n log n)','O(n)',8),
}
