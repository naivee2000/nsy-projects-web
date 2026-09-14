"""Flip costs, matrix ordering, free-hop paths, string deletion, and permutation batch 175."""

from collections import deque
from functools import lru_cache
from itertools import permutations

from .import_batch_055 import entry


def equal_cost_oracle(args):
    start=args[0];targets={'0'*len(start),'1'*len(start)};queue=deque([(start,0)]);best={start:0}
    while queue:
        value,cost=queue.popleft()
        if value in targets:return cost
        for cut in range(1,len(value)+1):
            for indexes in (range(cut),range(len(value)-cut,len(value))):
                following=list(value)
                for index in indexes:following[index]='1' if following[index]=='0' else '0'
                following=''.join(following);new_cost=cost+cut
                if new_cost<best.get(following,10**9):best[following]=new_cost;queue.append((following,new_cost))


def random_equal_cost(rng):return [''.join(rng.choice('01') for _ in range(rng.randint(1,8)))]


def cells_oracle(args):
    mat=args[0];rows=len(mat);columns=len(mat[0])
    @lru_cache(None)
    def visit(row,column):
        candidates=[visit(row,c) for c in range(columns) if mat[row][c]>mat[row][column]]
        candidates += [visit(r,column) for r in range(rows) if mat[r][column]>mat[row][column]]
        return 1+max(candidates,default=0)
    return max(visit(r,c) for r in range(rows) for c in range(columns))


def random_cells(rng):
    rows,columns=rng.randint(1,5),rng.randint(1,5)
    return [[[rng.randint(-8,8) for _ in range(columns)] for _ in range(rows)]]


def hops_oracle(args):
    n,edges,source,destination,k=args;graph=[[] for _ in range(n)]
    for left,right,weight in edges:graph[left].append((right,weight));graph[right].append((left,weight))
    best=10**18
    def visit(node,seen,weights):
        nonlocal best
        if node==destination:
            best=min(best,sum(sorted(weights)[:max(0,len(weights)-k)]));return
        for neighbor,weight in graph[node]:
            if neighbor not in seen:visit(neighbor,seen|{neighbor},weights+[weight])
    visit(source,{source},[])
    return -1 if best==10**18 else best


def random_hops(rng):
    n=rng.randint(2,7);edges=[]
    for node in range(1,n):
        if rng.random()<.85:edges.append([node,rng.randrange(node),rng.randint(1,15)])
    for left in range(n):
        for right in range(left+1,n):
            if rng.random()<.18 and not any(a==left and b==right or a==right and b==left for a,b,_ in edges):
                edges.append([left,right,rng.randint(1,15)])
    return [n,edges,rng.randrange(n),rng.randrange(n),rng.randint(0,3)]


def length_oracle(args):
    start=args[0];queue=deque([start]);seen={start};best=len(start)
    while queue:
        value=queue.popleft();best=min(best,len(value))
        for index,char in enumerate(value):
            left=value.rfind(char,0,index);right=value.find(char,index+1);remove={p for p in (left,right) if p!=-1}
            if remove:
                following=''.join(c for p,c in enumerate(value) if p not in remove)
                if following not in seen:seen.add(following);queue.append(following)
    return best


def random_length(rng):return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,7)))]


def semi_oracle(args):
    start=tuple(args[0]);queue=deque([(start,0)]);seen={start};largest=len(start)
    while queue:
        values,distance=queue.popleft()
        if values[0]==1 and values[-1]==largest:return distance
        for index in range(len(values)-1):
            following=list(values);following[index],following[index+1]=following[index+1],following[index];following=tuple(following)
            if following not in seen:seen.add(following);queue.append((following,distance+1))


def random_semi(rng):
    values=list(range(1,rng.randint(2,8)+1));rng.shuffle(values);return [values]


EQUAL_COST="""\
def minimum_uniform_binary_cost(s):
    total=0
    for index in range(1,len(s)):
        if s[index]!=s[index-1]:total+=min(index,len(s)-index)
    return total
"""

CELLS="""\
def maximum_increasing_matrix_cells(mat):
    rows=len(mat);columns=len(mat[0]);row_best=[0]*rows;column_best=[0]*columns;answer=0
    ordered=sorted((mat[row][column],row,column) for row in range(rows) for column in range(columns))
    index=0
    while index<len(ordered):
        end=index
        while end<len(ordered) and ordered[end][0]==ordered[index][0]:end+=1
        updates=[]
        for _,row,column in ordered[index:end]:
            length=1+max(row_best[row],column_best[column]);updates.append((row,column,length));answer=max(answer,length)
        for row,column,length in updates:row_best[row]=max(row_best[row],length);column_best[column]=max(column_best[column],length)
        index=end
    return answer
"""

HOPS="""\
def shortest_path_with_free_hops(n,edges,s,d,k):
    import heapq
    graph=[[] for _ in range(n)]
    for left,right,weight in edges:graph[left].append((right,weight));graph[right].append((left,weight))
    distances=[[float('inf')]*(k+1) for _ in range(n)];distances[s][0]=0;heap=[(0,s,0)]
    while heap:
        distance,node,used=heapq.heappop(heap)
        if distance!=distances[node][used]:continue
        if node==d:return distance
        for neighbor,weight in graph[node]:
            paid=distance+weight
            if paid<distances[neighbor][used]:distances[neighbor][used]=paid;heapq.heappush(heap,(paid,neighbor,used))
            if used<k and distance<distances[neighbor][used+1]:distances[neighbor][used+1]=distance;heapq.heappush(heap,(distance,neighbor,used+1))
    return -1
"""

LENGTH="""\
def minimum_string_length_after_deletions(s):
    return len(set(s))
"""

SEMI="""\
def semi_ordered_permutation_swaps(nums):
    one=nums.index(1);largest=nums.index(len(nums))
    return one+(len(nums)-1-largest)-(1 if one>largest else 0)
"""


BATCH={
2712:entry('minimum_uniform_binary_cost',[('s','str')],'int',['strings','greedy'],
 ['In one operation, choose a prefix or suffix, flip every bit in it, and pay its length.','Make every character equal, choosing either all zeroes or all ones.','Return the minimum total operation cost.'],
 [(['0011'],'The boundary can be removed by flipping the length-two prefix, costing two.'),(['010101'],'Each adjacent change contributes the cheaper distance to an end, for total nine.')],
 [[s] for s in ['0','1','00','01','10','0011','010','101','0101','10001','01110','010101','0010110','10110010']],
 EQUAL_COST,[EQUAL_COST.replace('min(index,len(s)-index)','index'),EQUAL_COST.replace("if s[index]!=s[index-1]","if s[index]==s[index-1]")],
 ['Always pays from the left even when the suffix is shorter.','Charges equal adjacent characters instead of transition boundaries.'],equal_cost_oracle,random_equal_cost,
 ['Only boundaries where adjacent bits differ need to be eliminated.','For a boundary at index i, flip either its i-character prefix or its n-i-character suffix.','Add min(i,n-i) independently for every adjacent transition.','Each flip toggles whether exactly one selected boundary crosses its endpoint; paying the nearer endpoint realizes every required boundary at minimum cost.'],'O(n)','O(1)',5),
2713:entry('maximum_increasing_matrix_cells',[('mat','list[list[int]]')],'int',['matrices','dynamic programming','sorting'],
 ['Start at any matrix cell.','Move within the same row or column only to a cell with a strictly larger value.','Return the greatest number of visited cells in a valid sequence.'],
 [([[[3,1],[3,4]]],'A sequence can move from one to three to four, but not between equal threes, so the maximum is three.'),([[[1,1],[1,1]]],'No strictly larger destination exists, so every valid sequence has one cell.')],
 [[m] for m in [[[1]],[[1,2]],[[2,1]],[[1],[2]],[[3,1],[3,4]],[[1,1],[1,1]],[[1,2],[3,4]],[[4,3],[2,1]],[[1,5,2],[4,3,6]],[[0,-1],[-2,3]],[[1,2,3],[1,2,3]],[[7,1,7],[2,8,3]],[[5,4,3],[6,1,2]],[[1,9],[8,2],[3,7]]]],
 CELLS,[CELLS.replace("        end=index\n        while end<len(ordered) and ordered[end][0]==ordered[index][0]:end+=1","        end=index+1"),CELLS.replace('max(row_best[row],column_best[column])','row_best[row]')],
 ['Updates equal-valued cells together with smaller cells, incorrectly allowing moves between equal values.','Ignores predecessors in the same column.'],cells_oracle,random_cells,
 ['Process cells in ascending value order.','Track the best completed sequence ending in each row and each column.','Compute all cells of one equal-value group before applying their row and column updates.','Every predecessor is smaller and already processed; delayed equal-value updates enforce strictness while row/column maxima capture every legal predecessor.'],'O(rc log(rc))','O(rc)',8),
2714:entry('shortest_path_with_free_hops',[('n','int'),('edges','list[list[int]]'),('s','int'),('d','int'),('k','int')],'int',['graphs','shortest path','heaps','dynamic programming'],
 ['The weighted edges form an undirected graph on nodes 0 through n-1.','During a path, traverse at most k chosen edges for zero cost; every other edge costs its weight.','Return the minimum source-to-destination cost, or -1 when no path exists.'],
 [([4,[[0,1,4],[0,2,2],[2,3,6]],1,3,2],'Following 1-0-2-3 and making weights four and six free leaves cost two.'),([3,[[0,1,5],[1,2,7]],0,2,0],'With no free hop, the only path costs five plus seven, or twelve.')],
 [[n,e,s,d,k] for n,e,s,d,k in [(2,[[0,1,5]],0,1,0),(2,[[0,1,5]],0,1,1),(2,[],0,1,2),(3,[[0,1,5],[1,2,7]],0,2,0),(3,[[0,1,5],[1,2,7]],0,2,1),(3,[[0,1,5],[1,2,7]],0,2,2),(4,[[0,1,4],[0,2,2],[2,3,6]],1,3,2),(4,[[0,1,10],[1,3,10],[0,2,1],[2,3,20]],0,3,1),(4,[[0,1,1],[1,2,1]],0,3,2),(1,[],0,0,3),(5,[[0,1,3],[1,2,4],[2,4,5],[0,3,20],[3,4,1]],0,4,1),(4,[[0,1,8],[1,2,2],[2,3,8],[0,3,30]],0,3,2),(3,[[0,1,2],[0,1,7],[1,2,4]],0,2,1),(5,[[0,1,9],[1,4,9],[0,2,2],[2,3,2],[3,4,2]],0,4,1)]],
 HOPS,[HOPS.replace('if used<k','if used+1<k'),HOPS.replace('distances[s][0]=0','distances[s][k]=0')],
 ['Allows only k-1 free edges.','Starts in the state where every free hop has already been consumed.'],hops_oracle,random_hops,
 ['A node alone is insufficient state because arriving after different numbers of free hops leaves different futures.','Run Dijkstra over states (node, free hops used).','Relax each edge once by paying its weight and, when available, once by consuming a free hop.','All expanded-state edges are nonnegative; Dijkstra therefore finalizes the globally cheapest valid source-to-state distance.'],'O((n+e)k log(nk))','O((n+e)k)',8),
2716:entry('minimum_string_length_after_deletions',[('s','str')],'int',['strings','hash maps','greedy'],
 ['Choose a character occurrence; if the same character occurs on its left, delete the closest such occurrence, and likewise on its right.','Repeat the operation any number of times.','Return the minimum achievable string length.'],
 [(['aaabc'],'Operations on a can delete two copies, leaving one each of a, b, and c for length three.'),(['cbbd'],'One operation centered on b deletes the other b, leaving three distinct characters.')],
 [[s] for s in ['a','aa','aaa','ab','aba','aaabc','cbbd','abcabc','aaaaaa','abccba','aabbcc','abcd','abacada','zzxyzz']],
 LENGTH,[LENGTH.replace('len(set(s))','len(s)'),LENGTH.replace('len(set(s))','sum(s.count(char)%2 for char in set(s))')],
 ['Performs no deletion.','Assumes only odd-frequency characters need remain, incorrectly allowing a character to disappear completely.'],length_oracle,random_length,
 ['At least one occurrence of every distinct character must remain.','Repeatedly center operations within occurrences of the same character to remove extras.','Count the number of distinct characters in s.','Operations never remove the selected center, so a character cannot disappear; extra occurrences can always be reduced until exactly one remains.'],'O(n)','O(alphabet)',3),
2717:entry('semi_ordered_permutation_swaps',[('nums','list[int]')],'int',['arrays','greedy'],
 ['nums is a permutation of 1 through n.','One operation swaps two adjacent elements.','Return the minimum swaps needed to place 1 first and n last; other values may be in any order.'],
 [([[2,1,4,3]],'Move one left once and four right once, for two adjacent swaps.'),([[2,4,1,3]],'The one crosses four while moving left, so that same crossing also shifts four right; two swaps suffice.')],
 [[p] for p in [[1,2],[2,1],[1,2,3],[3,2,1],[2,1,3],[1,3,2],[2,1,4,3],[2,4,1,3],[4,3,2,1],[3,1,2,4],[5,2,3,4,1],[2,3,4,5,1],[5,1,2,3,4],[3,5,2,1,4]]],
 SEMI,[SEMI.replace("-(1 if one>largest else 0)",''),SEMI.replace('nums.index(len(nums))','nums.index(len(nums)-1)')],
 ['Double-counts the crossing when one initially appears after n.','Moves n-1 to the end instead of the maximum n.'],semi_oracle,random_semi,
 ['Moving 1 left costs its zero-based index; moving n right costs n-1 minus its index.','If 1 begins to the right of n, their necessary crossing advances both goals in one swap.','Add the two distances and subtract one exactly when index(1) > index(n).','Every required displacement needs that many adjacent crossings, and the direct moves attain the lower bound with only the shared crossing counted once.'],'O(n)','O(1)',3),
}
