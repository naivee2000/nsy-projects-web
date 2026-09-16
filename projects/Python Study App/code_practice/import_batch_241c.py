"""Simultaneous flood fill, path digit DP, parity ranks, connected subsets, and missing evens."""
from collections import deque
from itertools import combinations
from .import_batch_055 import entry


def flood_oracle(args):
    n,m,sources=args;answer=[[0]*m for _ in range(n)]
    for row in range(n):
        for column in range(m):
            distance=min(abs(row-r)+abs(column-c) for r,c,_ in sources)
            answer[row][column]=max(color for r,c,color in sources if abs(row-r)+abs(column-c)==distance)
    return answer
def random_flood(rng):
    n=rng.randint(1,6);m=rng.randint(1,6);cells=rng.sample([(r,c) for r in range(n) for c in range(m)],rng.randint(1,min(n*m,8)))
    return [n,m,[[r,c,rng.randint(1,9)] for r,c in cells]]

def path_positions(directions):
    row=column=0;positions=[0]
    for move in directions:
        row+=move=='D';column+=move=='R';positions.append(row*4+column)
    return positions
def good_number(value,directions):
    digits=str(value).zfill(16);chosen=[digits[i] for i in path_positions(directions)]
    return all(chosen[i]<=chosen[i+1] for i in range(6))
def path_oracle(args):return sum(good_number(value,args[2]) for value in range(args[0],args[1]+1))
def random_path(rng):
    moves=list('DDDRRR');rng.shuffle(moves);left=rng.randint(0,5000);return [left,left+rng.randint(0,250),''.join(moves)]

def parity_oracle(args):
    nums=args[0]
    return [sum(nums[j]<value and (nums[j]-value)%2 for j in range(i+1,len(nums))) for i,value in enumerate(nums)]
def random_parity(rng):return [[rng.randint(-30,30) for _ in range(rng.randint(1,40))]]

def connected(mask,edges,n):
    start=(mask&-mask).bit_length()-1;seen={start};stack=[start]
    graph=[[] for _ in range(n)]
    for u,v in edges:graph[u].append(v);graph[v].append(u)
    while stack:
        node=stack.pop()
        for nxt in graph[node]:
            if mask>>nxt&1 and nxt not in seen:seen.add(nxt);stack.append(nxt)
    return len(seen)==mask.bit_count()
def subgraph_oracle(args):
    nums,edges=args;n=len(nums);return sum(sum(nums[i] for i in range(n) if mask>>i&1)%2==0 and connected(mask,edges,n) for mask in range(1,1<<n))
def random_subgraph(rng):
    n=rng.randint(1,10);all_edges=[(i,j) for i in range(n) for j in range(i+1,n)];chosen=rng.sample(all_edges,rng.randint(0,min(len(all_edges),15)))
    return [[rng.randint(0,1) for _ in range(n)],[list(edge) for edge in chosen]]

def missing_oracle(args):
    nums,queries=args;answer=[]
    for left,right,k in queries:
        present=set(nums[left:right+1]);value=2
        while True:
            if value not in present:
                k-=1
                if k==0:answer.append(value);break
            value+=2
    return answer
def random_missing(rng):
    n=rng.randint(1,25);nums=sorted(rng.sample(range(1,100),n));queries=[]
    for _ in range(rng.randint(1,20)):
        left=rng.randrange(n);right=rng.randint(left,n-1);queries.append([left,right,rng.randint(1,20)])
    return [nums,queries]

FLOOD='''def multi_source_flood_fill(n,m,sources):
    from collections import defaultdict
    grid=[[0]*m for _ in range(n)];frontier=[tuple(source) for source in sources]
    for row,column,color in frontier:grid[row][column]=color
    while frontier:
        candidates=defaultdict(int)
        for row,column,color in frontier:
            for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
                nr,nc=row+dr,column+dc
                if 0<=nr<n and 0<=nc<m and grid[nr][nc]==0:candidates[(nr,nc)]=max(candidates[(nr,nc)],color)
        frontier=[(row,column,color) for (row,column),color in candidates.items()]
        for row,column,color in frontier:grid[row][column]=color
    return grid
'''

PATH='''def count_nondecreasing_path_numbers(l,r,directions):
    from functools import lru_cache
    key=[False]*16;row=column=0;key[0]=True
    for move in directions:
        if move=='D':row+=1
        else:column+=1
        key[row*4+column]=True
    def count(limit):
        if limit<0:return 0
        digits=list(map(int,str(limit).zfill(16)))
        @lru_cache(None)
        def visit(position,last,tight):
            if position==16:return 1
            upper=digits[position] if tight else 9;lower=last if key[position] else 0;answer=0
            for digit in range(lower,upper+1):answer+=visit(position+1,digit if key[position] else last,tight and digit==upper)
            return answer
        return visit(0,0,True)
    return count(r)-count(l-1)
'''

PARITY='''def count_smaller_opposite_parity(nums):
    values=sorted(set(nums));tree=[[0]*(len(values)+1) for _ in range(2)]
    def add(parity,index):
        index+=1
        while index<len(tree[parity]):tree[parity][index]+=1;index+=index&-index
    def prefix(parity,index):
        total=0
        while index:total+=tree[parity][index];index-=index&-index
        return total
    from bisect import bisect_left
    answer=[0]*len(nums)
    for i in range(len(nums)-1,-1,-1):
        rank=bisect_left(values,nums[i]);answer[i]=prefix(1-(nums[i]&1),rank);add(nums[i]&1,rank)
    return answer
'''

SUBGRAPH='''def count_even_connected_subgraphs(nums,edges):
    n=len(nums);graph=[[] for _ in range(n)]
    for u,v in edges:graph[u].append(v);graph[v].append(u)
    answer=0
    for mask in range(1,1<<n):
        if sum(nums[i] for i in range(n) if mask>>i&1)%2:continue
        start=(mask&-mask).bit_length()-1;seen=1<<start;stack=[start]
        while stack:
            node=stack.pop()
            for nxt in graph[node]:
                if mask>>nxt&1 and not seen>>nxt&1:seen|=1<<nxt;stack.append(nxt)
        answer+=seen==mask
    return answer
'''

MISSING='''def kth_missing_even_queries(nums,queries):
    from bisect import bisect_right
    prefix=[0]
    for value in nums:prefix.append(prefix[-1]+(value%2==0))
    answer=[]
    for left,right,k in queries:
        low=1;high=k+right-left+1
        while low<high:
            middle=(low+high)//2;value=2*middle
            bound=min(right,bisect_right(nums,value)-1)
            count=prefix[bound+1]-prefix[left] if bound>=left else 0
            if middle-count>=k:high=middle
            else:low=middle+1
        answer.append(2*low)
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]
F_CASES=[[n,m,s] for n,m,s in ((3,3,[[0,0,1],[2,2,2]]),(1,1,[[0,0,5]]),(1,3,[[0,0,1]]),(2,2,[[0,0,3],[1,1,3]]),(2,3,[[0,0,1],[0,2,9]]),(3,1,[[0,0,2],[2,0,4]]),(3,3,[[1,1,7]]),(4,4,[[0,0,1],[3,3,2]]),(2,4,[[0,1,5],[1,3,6]]),(4,2,[[0,0,8],[3,1,1]]),(3,4,[[0,3,2],[2,0,9]]),(5,1,[[0,0,1],[4,0,5]]),(1,5,[[0,1,4],[0,4,7]]),(4,3,[[1,1,2],[3,2,6]]),(5,5,[[0,0,1],[0,4,2],[4,0,3],[4,4,4]]))]
P_CASES=[[l,r,d] for l,r,d in ((8,10,'DDDRRR'),(0,0,'DDDRRR'),(1,20,'RRRDDD'),(90,120,'DRDRDR'),(100,200,'RDRDRD'),(999,1050,'DDRRDR'),(0,50,'RRDDDR'),(500,700,'DRRDDR'),(1234,1300,'RDRRDD'),(10,99,'DDRDRR'),(1000,1100,'DRDDRR'),(42,142,'RRDRDD'),(7000,7100,'RDDDRR'),(1,1,'DRDRDR'),(9999,10050,'DDRRRD'))]
R_CASES=[[[*v]] for v in ([5,2,4,1,3],[1],[2,1],[1,2],[4,3,2,1],[1,3,5,2,4],[0,-1,2,-3],[7,4,6,3,5,2],[2,4,6,1,3,5],[9,8,7,6],[1,1,0,0],[10,3,8,1,6],[5,4,3,2,1],[0,2,1,3,4],[11,2,9,4,7,6])]
S_CASES=[[a,e] for a,e in (([1,0,1],[[0,1],[1,2]]),([0],[]),([1],[]),([0,0],[[0,1]]),([1,1],[[0,1]]),([1,1],[]),([0,1,0],[[0,1],[1,2]]),([1,0,1],[[0,1]]),([1,1,0],[[0,1],[1,2],[0,2]]),([0,0,0],[]),([1,0,0,1],[[0,1],[1,2],[2,3]]),([1,1,1,1],[[0,1],[1,2],[2,3]]),([0,1,1,0],[[0,1],[2,3]]),([1,0,1,0],[[0,1],[1,2],[2,3],[3,0]]),([0,1,0,1,0],[[0,1],[1,2],[2,3],[3,4]]))]
M_CASES=[[a,q] for a,q in (([1,4,7],[[0,2,1],[1,1,2],[0,0,3]]),([2],[[0,0,1]]),([1],[[0,0,2]]),([2,4],[[0,1,1]]),([2,4],[[0,1,3]]),([1,3,5],[[0,2,2]]),([2,6,10],[[0,2,2]]),([4,8,12],[[1,2,4]]),([1,2,3,4],[[1,3,1]]),([2,3,8,9],[[0,2,2]]),([10,20,30],[[0,2,6]]),([1,100],[[0,1,10]]),([2,4,6,8],[[1,2,2],[0,3,5]]),([7,14,21],[[1,1,4]]),([1,2,4,7,10],[[2,4,3]]))]

BATCH={
3905:entry('multi_source_flood_fill',[('n','int'),('m','int'),('sources','list[list[int]]')],'list[list[int]]',['matrices','breadth-first search'],['n and m are positive; sources contains distinct in-bounds [row,column,color] entries with positive colors.','Every round, colored cells spread to orthogonal uncolored neighbors simultaneously.','When colors arrive in the same earliest round, use the greatest color; return the filled grid.'],[([3,3,[[0,0,1],[2,2,2]]],'Distance ties favor color two, producing [[1,1,2],[1,2,2],[2,2,2]].'),([1,3,[[0,0,1]]],'The sole color spreads right each round, filling [1,1,1].')],F_CASES,FLOOD,[FLOOD.replace('candidates[(nr,nc)]=max(candidates[(nr,nc)],color)','candidates.setdefault((nr,nc),color)'),FLOOD.replace("((-1,0),(1,0),(0,-1),(0,1))","((-1,0),(1,0),(0,1))")],['Keeps the first simultaneous arrival instead of selecting the greatest color.','Omits spreading to the left, leaving some reachable cells uncolored or assigned too late.'],flood_oracle,random_flood,lesson('Arrival time is Manhattan-distance BFS from all sources.','Process one complete frontier per round and collect candidates for still-uncolored neighbors.','Resolve all same-round candidates by maximum color before writing any cell.','Level batching guarantees earliest arrival; delayed writes preserve simultaneity and the maximum rule.'),'O(nm)','O(nm)',5),
3906:entry('count_nondecreasing_path_numbers',[('l','int'),('r','int'),('directions','str')],'int',['digit dynamic programming','matrices'],['0≤l≤r<10^16 and directions contains exactly three D and three R moves.','Pad each integer to 16 digits, place them row-major in a 4×4 grid, and read the seven visited path positions.','Count values whose visited digits are nondecreasing.'],[([8,10,'DDDRRR'],'Eight and nine qualify after zero padding, while ten creates a decrease on the selected path, giving two.'),([0,0,'DDDRRR'],'All sixteen digits are zero, so the sole value qualifies.')],P_CASES,PATH,[PATH.replace('lower=last if key[position] else 0','lower=last'),PATH.replace('count(r)-count(l-1)','count(r)-count(l)')],['Forces unvisited digits to be at least the last path digit.','Excludes the inclusive left endpoint.'],path_oracle,random_path,lesson('Only seven digit positions constrain monotonicity, but all sixteen positions affect the numeric bound.','Digit DP tracks position, last selected-path digit, and tightness.','At a path position start choices at last; elsewhere allow zero through nine without changing last.','The state enforces exactly the path order while tightness counts padded numbers up to a bound; prefix subtraction gives [l,r].'),'O(16·10·10)','O(16·10)',8),
3907:entry('count_smaller_opposite_parity',[('nums','list[int]')],'list[int]',['arrays','fenwick trees','coordinate compression'],['nums is a nonempty integer array.','For each i, count later j with nums[j]<nums[i] and opposite parity.','Return one count per index.'],[([[5,2,4,1,3]],'Five sees later smaller evens two and four; two sees later odd one; four sees later odds one and three, giving [2,1,2,0,0].'),([[2,1]],'Two sees the smaller opposite-parity one, giving [1,0].')],R_CASES,PARITY,[PARITY.replace('1-(nums[i]&1)','nums[i]&1'),PARITY.replace('bisect_left(values,nums[i])','bisect_left(values,nums[i]+2)')],['Counts later values of the same parity.','Also counts the next larger opposite-parity value instead of requiring strict smaller order.'],parity_oracle,random_parity,lesson('Scan from right to left so data structures contain exactly later elements.','Coordinate-compress values and maintain one Fenwick tree for each parity.','Query the opposite-parity tree strictly below the current rank, then insert the current value into its parity tree.','Compression preserves order, and the prefix query implements both strict inequality and the later-index condition.'),'O(n log n)','O(n)',6),
3910:entry('count_even_connected_subgraphs',[('nums','list[int]'),('edges','list[list[int]]')],'int',['graphs','bit manipulation','enumeration'],['nums contains zero/one node values; edges defines an undirected simple graph.','Choose a nonempty node subset whose induced subgraph is connected.','Count subsets with even value sum.'],[([[1,0,1],[[0,1],[1,2]]],'The singleton zero node and the full connected path with sum two are the two qualifying subsets.'),([[0],[]],'The single zero-valued node is connected and has even sum, so the answer is one.')],S_CASES,SUBGRAPH,[SUBGRAPH.replace('if sum(nums[i] for i in range(n) if mask>>i&1)%2:continue',''),SUBGRAPH.replace('answer+=seen==mask','answer+=True')],['Counts odd-sum connected subsets as well.','Counts disconnected subsets because it ignores the reachability comparison.'],subgraph_oracle,random_subgraph,lesson('For the intended small n, enumerate every nonempty node mask.','Reject odd value sums, then run DFS restricted to nodes whose mask bits are set.','Count the mask only when DFS reaches every selected node.','Every induced subset has one mask and connectivity is exactly restricted reachability, so enumeration is complete without duplicates.'),'O(2^n(n+e))','O(n+e)',8),
3911:entry('kth_missing_even_queries',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['arrays','binary search','queries'],['nums is strictly increasing and queries are [left,right,k] with valid inclusive indices and positive k.','For each query, consider positive even integers absent from nums[left:right+1].','Return the kth smallest absent even integer.'],[([[1,4,7],[[0,2,1],[1,1,2],[0,0,3]]],'The missing-even lists begin [2,6], [2,6], and [2,4,6], producing [2,6,6].'),([[2],[[0,0,1]]],'Two is present, so the first missing positive even is four.')],M_CASES,MISSING,[MISSING.replace('middle-count>=k','middle-count>k'),MISSING.replace('answer.append(2*low)','answer.append(low)')],['Uses a strict binary-search threshold and skips exact kth boundaries.','Returns the even-number ordinal instead of the even value.'],missing_oracle,random_missing,lesson('Represent positive evens as 2q for ordinal q≥1.','Among the first q evens, subtract the count of subarray values that are even and at most 2q.','Binary-search the first q whose missing count reaches k; q≤k+subarray length is a safe upper bound.','The missing-count function is monotone, so its first threshold is exactly the kth absent even.'),'O(q log n log(k+n))','O(n)',8),
}
