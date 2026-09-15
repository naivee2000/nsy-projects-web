"""Unit graphs, wrapped string matches, topological profit, covered buildings, and graph components."""
from functools import lru_cache

from .import_batch_055 import entry


def conversion_oracle(args):
    conversions=args[0];n=len(conversions)+1;graph=[[] for _ in range(n)]
    for source,target,factor in conversions:graph[source].append((target,factor))
    answer=[]
    for target in range(n):
        stack=[(0,1)];found=0
        while stack:
            node,value=stack.pop()
            if node==target:found=value;break
            for nxt,factor in graph[node]:stack.append((nxt,value*factor))
        answer.append(found%1000000007)
    return answer


def random_conversion(rng):
    n=rng.randint(2,10);edges=[]
    for node in range(1,n):edges.append([rng.randrange(node),node,rng.randint(1,20)])
    rng.shuffle(edges);return [edges]


def overlap_oracle(args):
    grid,pattern=args;rows=len(grid);cols=len(grid[0]);horizontal=''.join(''.join(row) for row in grid);vertical=''.join(grid[row][col] for col in range(cols) for row in range(rows));h=set();v=set()
    for start in range(len(horizontal)-len(pattern)+1):
        if horizontal[start:start+len(pattern)]==pattern:h.update(range(start,start+len(pattern)))
    for start in range(len(vertical)-len(pattern)+1):
        if vertical[start:start+len(pattern)]==pattern:v.update(range(start,start+len(pattern)))
    return sum(index in h and (index%cols)*rows+index//cols in v for index in range(rows*cols))


def random_overlap(rng):
    rows=rng.randint(1,5);cols=rng.randint(1,5);grid=[[rng.choice('abc') for _ in range(cols)] for _ in range(rows)]
    return [grid,''.join(rng.choice('abc') for _ in range(rng.randint(1,rows*cols)))]


def topo_oracle(args):
    n,edges,scores=args;prereq=[0]*n
    for u,v in edges:prereq[v]|=1<<u
    @lru_cache(None)
    def solve(mask):
        if mask==(1<<n)-1:return 0
        position=mask.bit_count()+1
        return max(scores[node]*position+solve(mask|1<<node) for node in range(n) if not mask>>node&1 and prereq[node]&mask==prereq[node])
    return solve(0)


def random_topo(rng):
    n=rng.randint(1,8);order=list(range(n));rng.shuffle(order);position={node:i for i,node in enumerate(order)};edges=[]
    for u in range(n):
        for v in range(n):
            if position[u]<position[v] and rng.randrange(5)==0:edges.append([u,v])
    return [n,edges,[rng.randint(1,20) for _ in range(n)]]


def covered_oracle(args):
    _,buildings=args;points={tuple(point) for point in buildings}
    return sum(any(a==x and b<y for a,b in points) and any(a==x and b>y for a,b in points) and any(b==y and a<x for a,b in points) and any(b==y and a>x for a,b in points) for x,y in points)


def random_covered(rng):
    n=rng.randint(2,8);points=[[x,y] for x in range(1,n+1) for y in range(1,n+1)];rng.shuffle(points)
    return [n,points[:rng.randint(1,min(len(points),15))]]


def path_oracle(args):
    n,nums,max_diff,queries=args;graph=[[] for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            if nums[j]-nums[i]<=max_diff:graph[i].append(j);graph[j].append(i)
    answer=[]
    for source,target in queries:
        seen={source};stack=[source]
        while stack:
            node=stack.pop()
            for nxt in graph[node]:
                if nxt not in seen:seen.add(nxt);stack.append(nxt)
        answer.append(target in seen)
    return answer


def random_path(rng):
    n=rng.randint(1,12);nums=sorted(rng.randint(0,30) for _ in range(n));queries=[[rng.randrange(n),rng.randrange(n)] for _ in range(rng.randint(1,15))]
    return [n,nums,rng.randint(0,10),queries]


CONVERSION='''def base_unit_conversions(conversions):
    modulo=1000000007;n=len(conversions)+1;graph=[[] for _ in range(n)]
    for source,target,factor in conversions:graph[source].append((target,factor))
    answer=[0]*n;answer[0]=1;stack=[0]
    while stack:
        node=stack.pop()
        for target,factor in graph[node]:answer[target]=answer[node]*factor%modulo;stack.append(target)
    return answer
'''


OVERLAP='''def count_horizontal_vertical_pattern_cells(grid,pattern):
    rows=len(grid);cols=len(grid[0]);horizontal=''.join(''.join(row) for row in grid);vertical=''.join(grid[row][col] for col in range(cols) for row in range(rows))
    def covered(text):
        combined=pattern+'#'+text;prefix=[0]*len(combined);difference=[0]*(len(text)+1)
        for i in range(1,len(combined)):
            j=prefix[i-1]
            while j and combined[i]!=combined[j]:j=prefix[j-1]
            if combined[i]==combined[j]:j+=1
            prefix[i]=j
            if j==len(pattern):
                end=i-len(pattern)-1;start=end-len(pattern)+1;difference[start]+=1;difference[end+1]-=1
        active=0;result=[]
        for i in range(len(text)):active+=difference[i];result.append(active>0)
        return result
    horizontal_hits=covered(horizontal);vertical_hits=covered(vertical)
    return sum(horizontal_hits[index] and vertical_hits[(index%cols)*rows+index//cols] for index in range(rows*cols))
'''


TOPO='''def maximum_topological_profit(n,edges,score):
    prerequisites=[0]*n
    for source,target in edges:prerequisites[target]|=1<<source
    negative=-10**30;dp=[negative]*(1<<n);dp[0]=0
    for mask in range(1<<n):
        if dp[mask]==negative:continue
        position=mask.bit_count()+1
        for node in range(n):
            if not mask>>node&1 and prerequisites[node]&mask==prerequisites[node]:
                nxt=mask|1<<node;dp[nxt]=max(dp[nxt],dp[mask]+score[node]*position)
    return dp[-1]
'''


COVERED='''def count_covered_buildings(n,buildings):
    rows={};columns={}
    for x,y in buildings:
        if x not in rows:rows[x]=[y,y]
        else:rows[x][0]=min(rows[x][0],y);rows[x][1]=max(rows[x][1],y)
        if y not in columns:columns[y]=[x,x]
        else:columns[y][0]=min(columns[y][0],x);columns[y][1]=max(columns[y][1],x)
    return sum(rows[x][0]<y<rows[x][1] and columns[y][0]<x<columns[y][1] for x,y in buildings)
'''


PATHS='''def path_existence_by_value_gaps(n,nums,max_diff,queries):
    component=[0]*n
    for index in range(1,n):component[index]=component[index-1]+(nums[index]-nums[index-1]>max_diff)
    return [component[left]==component[right] for left,right in queries]
'''


def lesson(a,b,c,d):return [a,b,c,d]


CONVERSION_CASES=[[edges] for edges in [
[[0,1,2],[1,2,3]],[[0,1,2],[0,2,3],[1,3,4],[1,4,5],[2,5,2],[4,6,3],[5,7,4]],[[0,1,1]],
[[0,1,1000000007]],[[0,1,2],[0,2,5]],[[0,2,3],[2,1,4]],[[0,1,7],[1,2,11],[2,3,13]],
[[0,1,2],[1,3,3],[0,2,5],[2,4,7]],[[0,3,2],[3,2,2],[2,1,2]],[[0,1,999999999],[1,2,999999999]],
[[0,1,4],[0,2,6],[2,3,8],[2,4,10]],[[0,1,3],[1,4,5],[4,2,7],[2,3,9]],
[[0,5,2],[5,4,3],[4,3,4],[3,2,5],[2,1,6]],[[0,1,2],[1,2,2],[1,3,2],[3,4,2],[3,5,2]]]]
OVERLAP_CASES=[[grid,pattern] for grid,pattern in [
([['a','a','c','c'],['b','b','b','c'],['a','a','b','a'],['c','a','a','c'],['a','a','b','a']],'abaca'),
([['c','a','a','a'],['a','a','b','a'],['b','b','a','a'],['a','a','b','a']],'aba'),([['a']],'a'),([['a','b']],'ab'),([['a'],['b']],'ab'),
([['a','a'],['a','a']],'aa'),([['a','b'],['c','d']],'bc'),([['a','b'],['b','a']],'aba'),([['x','y','x']],'x'),
([['a'],['a'],['b'],['a']],'aa'),([['a','b','c'],['a','b','c']],'abc'),([['a','b'],['c','a'],['b','c']],'abc'),
([['z','z'],['z','z']],'zzz'),([['a','b','a'],['b','a','b'],['a','b','a']],'aba')]]
TOPO_CASES=[list(case) for case in [
(2,[[0,1]],[2,3]),(3,[[0,1],[0,2]],[1,6,3]),(1,[],[5]),(3,[],[1,2,3]),(3,[[0,1],[1,2]],[3,1,2]),
(4,[[0,2],[1,2]],[5,1,9,4]),(4,[[0,1],[0,2],[1,3],[2,3]],[2,8,3,7]),(5,[],[5,4,3,2,1]),
(5,[[0,2],[1,2],[2,4],[3,4]],[7,6,5,4,3]),(2,[],[100,1]),(4,[[0,3],[1,3],[2,3]],[9,1,5,7]),
(6,[[0,2],[0,3],[1,3],[2,4],[3,4],[4,5]],[1,2,3,4,5,6]),(3,[[2,1]],[4,9,2]),(5,[[0,1],[0,2],[0,3],[0,4]],[10,1,2,3,4])]]
COVERED_CASES=[[n,points] for n,points in [
(3,[[1,2],[2,2],[3,2],[2,1],[2,3]]),(3,[[1,1],[1,2],[2,1],[2,2]]),(5,[[1,3],[3,2],[3,3],[3,5],[5,3]]),
(2,[[1,1]]),(4,[[1,2],[2,2],[3,2],[4,2]]),(4,[[2,1],[2,2],[2,3],[2,4]]),(5,[[1,3],[2,3],[3,1],[3,2],[3,3],[3,4],[3,5],[4,3],[5,3]]),
(3,[[1,1],[2,2],[3,3]]),(6,[[1,4],[4,1],[4,4],[4,6],[6,4]]),(5,[[2,2],[2,4],[4,2],[4,4]]),
(7,[[1,3],[3,1],[3,3],[3,7],[7,3],[5,3],[3,5]]),(3,[[1,1],[1,3],[3,1],[3,3],[2,2]]),
(5,[[1,2],[2,1],[2,2],[2,5],[5,2]]),(4,[[1,1],[1,2],[1,3],[2,2],[3,2],[4,2]])]]
PATH_CASES=[[n,nums,diff,queries] for n,nums,diff,queries in [
(2,[1,3],1,[[0,0],[0,1]]),(4,[2,5,6,8],2,[[0,1],[0,2],[1,3],[2,3]]),(1,[5],0,[[0,0]]),
(3,[1,1,1],0,[[0,2]]),(3,[1,2,4],1,[[0,1],[1,2],[0,2]]),(5,[0,2,4,6,8],2,[[0,4],[1,3]]),
(5,[0,2,5,6,10],2,[[0,1],[1,3],[3,4]]),(4,[1,10,11,12],1,[[0,3],[1,3]]),(6,[1,2,3,20,21,22],2,[[0,2],[0,5],[3,5]]),
(2,[0,100000],100000,[[0,1]]),(4,[3,3,7,7],0,[[0,1],[2,3],[1,2]]),(5,[1,4,7,10,13],3,[[0,4]]),
(7,[0,1,5,6,7,20,21],1,[[0,1],[2,4],[5,6],[1,2]]),(3,[2,5,9],4,[[0,2],[1,2]])]]


BATCH={
3528:entry('base_unit_conversions',[('conversions','list[list[int]]')],'list[int]',['graphs','depth first search','modular arithmetic'],['There are len(conversions)+1 units and every unit is uniquely reachable from unit 0 along directed conversions.','[source,target,factor] means one source unit equals factor target units.','Return each amount equivalent to one unit 0 modulo 1,000,000,007.'],[([[[0,1,2],[1,2,3]]],'Unit zero converts to two unit-one values and then six unit-two values.'),([[[0,1,2],[0,2,3],[1,3,4],[1,4,5],[2,5,2],[4,6,3],[5,7,4]]],'Multiplying factors along each unique path gives [1,2,3,8,10,6,30,24].')],CONVERSION_CASES,CONVERSION,[CONVERSION.replace('answer[node]*factor','factor'),CONVERSION.replace('%modulo','')],['Uses only the final edge factor and ignores earlier conversions on the path.','Fails to reduce potentially enormous path products modulo the required modulus.'],conversion_oracle,random_conversion,lesson('Unique directed reachability makes every unit’s conversion the product along exactly one path from unit zero.','Traverse outward from unit zero and propagate the current product modulo the fixed modulus.','Set unit zero to one; for each directed edge assign child=parent*factor mod M and visit the child.','Induction on path length proves every assigned value equals its unique root-path factor product.'),'O(n)','O(n)',6),
3529:entry('count_horizontal_vertical_pattern_cells',[('grid','list[list[str]]'),('pattern','str')],'int',['matrices','strings','kmp'],['grid has at most 100,000 cells and pattern length is at most the cell count.','Horizontal reading is row-major and vertical reading is column-major; neither order wraps after its final cell.','Count cells covered by at least one pattern match in both reading orders.'],[([[['a','a','c','c'],['b','b','b','c'],['a','a','b','a'],['c','a','a','c'],['a','a','b','a']],'abaca'],'The single row-major and column-major matches overlap at exactly one cell.'),([[['c','a','a','a'],['a','a','b','a'],['b','b','a','a'],['a','a','b','a']],'aba'],'All matches together cover four cells in both reading directions.')],OVERLAP_CASES,OVERLAP,[OVERLAP.replace("vertical=''.join(grid[row][col] for col in range(cols) for row in range(rows))","vertical=horizontal"),OVERLAP.replace('difference[end+1]-=1','difference[start+1]-=1')],['Uses row-major order for both directions and never performs the required column-major scan.','Marks only the first character of each match rather than every covered character.'],overlap_oracle,random_overlap,lesson('The wrapping rules are simply substring matches in row-major and column-major flattened strings.','Use KMP to find every match, difference arrays to mark full matched ranges, then map each cell between the two flattenings.','Build coverage booleans for both flattened strings and count row-major cells whose corresponding column-major position is also covered.','KMP finds all overlapping matches, range differences mark their union, and the index mapping identifies the same physical cell.'),'O(mn+pattern length)','O(mn+pattern length)',7),
3530:entry('maximum_topological_profit',[('n','int'),('edges','list[list[int]]'),('score','list[int]')],'int',['graphs','bitmask dynamic programming','topological sorting'],['The graph is a DAG with n <= 22 and positive node scores.','Every edge u->v requires u before v; positions are one-based.','Maximize sum(score[node]*position) over valid topological orders.'],[([2,[[0,1]],[2,3]],'The forced order [0,1] earns 2*1+3*2=8.'),([3,[[0,1],[0,2]],[1,6,3]],'After node zero, placing score three before score six yields profit 25.')],TOPO_CASES,TOPO,[TOPO.replace('score[node]*position','score[node]*(n-position+1)'),TOPO.replace('prerequisites[node]&mask==prerequisites[node]','True')],['Uses reversed position multipliers and optimizes the wrong objective.','Ignores prerequisite masks and permits invalid orders.'],topo_oracle,random_topo,lesson('With at most 22 nodes, the set already placed is a complete state; its size fixes the next multiplier.','Encode each node’s prerequisites as a bitmask and perform maximum-profit subset DP.','For every reachable mask, append each unchosen node whose prerequisite mask is contained, adding score times the next position.','Every transition preserves topological validity, and every valid order corresponds to one complete sequence of transitions.'),'O(n*2^n)','O(2^n)',8),
3531:entry('count_covered_buildings',[('n','int'),('buildings','list[list[int]]')],'int',['arrays','hash maps','geometry'],['Buildings are unique integer coordinates within an n by n city; there may be up to 100,000.','A building is covered only when another exists left and right in its row and above and below in its column.','Return the number of covered buildings.'],[([3,[[1,2],[2,2],[3,2],[2,1],[2,3]]],'Only the center building has neighbors on both row sides and both column sides.'),([3,[[1,1],[1,2],[2,1],[2,2]]],'Every building is extreme in its row or column, so none is covered.')],COVERED_CASES,COVERED,[COVERED.replace("columns[y][0]<x<columns[y][1]","columns[y][0]<=x<=columns[y][1]"),COVERED.replace('and columns[y][0]<x<columns[y][1]','or columns[y][0]<x<columns[y][1]')],['Allows the building itself to satisfy above and below because column comparisons are non-strict.','Requires row coverage or column coverage instead of all four directions.'],covered_oracle,random_covered,lesson('Only the extreme occupied coordinates in each row and column matter for four-direction coverage.','Record minimum and maximum y per row and x per column.','For each building, count it when its y lies strictly between its row extremes and x strictly between its column extremes.','Strict interior position is equivalent to having at least one occupied coordinate on each required side.'),'O(buildings)','O(buildings)',5),
3532:entry('path_existence_by_value_gaps',[('n','int'),('nums','list[int]'),('max_diff','int'),('queries','list[list[int]]')],'list[bool]',['arrays','graphs','connected components'],['nums is sorted, has length n up to 100,000, and max_diff is nonnegative.','Nodes i and j share an undirected edge whenever abs(nums[i]-nums[j]) <= max_diff.','For every [u,v], report whether the two nodes are connected by any path.'],[([2,[1,3],1,[[0,0],[0,1]]],'A node reaches itself, but the gap of two separates nodes zero and one.'),([4,[2,5,6,8],2,[[0,1],[0,2],[1,3],[2,3]]],'The initial gap separates node zero; consecutive later gaps connect nodes one through three.')],PATH_CASES,PATHS,[PATHS.replace('>max_diff','>=max_diff'),PATHS.replace('nums[index]-nums[index-1]','nums[index]-nums[0]')],['Splits components when a consecutive gap equals the allowed maximum.','Compares every value to the first instead of detecting barriers between consecutive sorted values.'],path_oracle,random_path,lesson('In sorted order, a gap larger than max_diff is an uncrossable component boundary; every smaller consecutive gap provides a connecting edge.','Assign component IDs in one scan, incrementing after each oversized consecutive gap.','Build component[index] from component[index-1], then compare IDs for every query.','No edge can cross an oversized sorted gap, while consecutive allowed edges connect every index inside a gap-free interval.'),'O(n+queries)','O(n)',5),
}
