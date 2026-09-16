"""Tree subset DP, digit DP, stateful paths, depth weights, and paired squares."""
from itertools import combinations
from .import_batch_055 import entry

MOD=1_000_000_007

def subsets_oracle(args):
    parent,nums,k=args;n=len(nums);answer=0
    for mask in range(1,1<<n):
        if any(mask>>i&1 and mask>>parent[i]&1 for i in range(1,n)):continue
        answer+=sum(nums[i] for i in range(n) if mask>>i&1)%k==0
    return answer%MOD
def random_subsets(rng):
    n=rng.randint(1,11);return [[-1]+[rng.randrange(i) for i in range(1,n)],[rng.randint(1,20) for _ in range(n)],rng.randint(1,7)]

def good(value,k):
    digits=str(value);return all(abs(int(a)-int(b))<=k for a,b in zip(digits,digits[1:]))
def digits_oracle(args):
    left,right,k=args;return sum(good(value,k) for value in range(left,right+1))
def random_digits(rng):
    left=rng.randint(10,4500);return [left,rng.randint(left,min(5000,left+400)),rng.randint(0,9)]

def path_oracle(args):
    n,edges,labels,k=args;states=[(node,run) for node in range(n) for run in range(1,k+1)];inf=10**15;distance={(0,1):0}
    for _ in range(len(states)-1):
        changed=False
        for u,v,weight in edges:
            for run in range(1,k+1):
                if (u,run) not in distance:continue
                nxt=run+1 if labels[u]==labels[v] else 1
                if nxt<=k and distance[(u,run)]+weight<distance.get((v,nxt),inf):distance[(v,nxt)]=distance[(u,run)]+weight;changed=True
        if not changed:break
    return min((distance.get((n-1,run),inf) for run in range(1,k+1)),default=inf) if any((n-1,r) in distance for r in range(1,k+1)) else -1
def random_path(rng):
    n=rng.randint(1,7);possible=[(u,v) for u in range(n) for v in range(n) if u!=v];chosen=rng.sample(possible,rng.randint(0,min(15,len(possible))))
    return [n,[[u,v,rng.randint(1,12)] for u,v in chosen],''.join(rng.choice('abc') for _ in range(n)),rng.randint(1,4)]

def weighted_oracle(args):
    parent,nums=args;memo={0:1}
    def depth(node):
        if node not in memo:memo[node]=depth(parent[node])+1
        return memo[node]
    depths=[depth(node) for node in range(len(parent))];height=max(depths)
    return sum(value*(height-level+1) for value,level in zip(nums,depths))
def random_weighted(rng):
    n=rng.randint(1,20);return [[-1]+[rng.randrange(i) for i in range(1,n)],[rng.randint(1,30) for _ in range(n)]]

def squares_oracle(args):
    matrix=args[0];rows=len(matrix);cols=len(matrix[0]);best=0
    for size in range(1,min(rows,cols)+1):
        valid=[]
        for row in range(rows-size+1):
            for col in range(cols-size+1):
                if all(matrix[r][c] for r in range(row,row+size) for c in range(col,col+size)):valid.append((row,col))
        if any(abs(a-c)>=size or abs(b-d)>=size for (a,b),(c,d) in combinations(valid,2)):best=size*size
    return best
def random_squares(rng):
    rows=rng.randint(1,7);cols=rng.randint(1,7);return [[[rng.randint(0,1) for _ in range(cols)] for _ in range(rows)]]

SUBSETS='''def count_non_adjacent_divisible_subsets(parent,nums,k):
    modulus=1_000_000_007;n=len(nums);children=[[] for _ in range(n)]
    for node in range(1,n):children[parent[node]].append(node)
    skipped=[[0]*k for _ in range(n)];chosen=[[0]*k for _ in range(n)]
    for node in range(n-1,-1,-1):
        skipped[node][0]=1;chosen[node][nums[node]%k]=1
        for child in children[node]:
            total=[(skipped[child][r]+chosen[child][r])%modulus for r in range(k)];next_skipped=[0]*k;next_chosen=[0]*k
            for left in range(k):
                for right in range(k):
                    next_skipped[(left+right)%k]=(next_skipped[(left+right)%k]+skipped[node][left]*total[right])%modulus
                    next_chosen[(left+right)%k]=(next_chosen[(left+right)%k]+chosen[node][left]*skipped[child][right])%modulus
            skipped[node],chosen[node]=next_skipped,next_chosen
    return (skipped[0][0]+chosen[0][0]-1)%modulus
'''

DIGITS='''def count_good_integers(l,r,k):
    from functools import lru_cache
    def count(limit):
        digits=list(map(int,str(limit)))
        @lru_cache(None)
        def dp(position,previous,started,tight):
            if position==len(digits):return int(started)
            answer=0;maximum=digits[position] if tight else 9
            for digit in range(maximum+1):
                next_tight=tight and digit==maximum
                if not started and digit==0:answer+=dp(position+1,10,False,next_tight)
                elif not started or abs(previous-digit)<=k:answer+=dp(position+1,digit,True,next_tight)
            return answer
        return dp(0,10,False,True)
    return count(r)-count(l-1)
'''

PATH='''def shortest_limited_label_path(n,edges,labels,k):
    import heapq
    graph=[[] for _ in range(n)]
    for u,v,weight in edges:graph[u].append((v,weight))
    infinity=10**30;distance=[[infinity]*(k+1) for _ in range(n)];distance[0][1]=0;heap=[(0,0,1)]
    while heap:
        cost,node,run=heapq.heappop(heap)
        if cost!=distance[node][run]:continue
        if node==n-1:return cost
        for nxt,weight in graph[node]:
            next_run=run+1 if labels[node]==labels[nxt] else 1
            if next_run<=k and cost+weight<distance[nxt][next_run]:distance[nxt][next_run]=cost+weight;heapq.heappush(heap,(cost+weight,nxt,next_run))
    return -1
'''

WEIGHTED='''def weighted_tree_sum(parent,nums):
    from collections import deque
    n=len(parent);children=[[] for _ in range(n)]
    for node in range(1,n):children[parent[node]].append(node)
    depth=[0]*n;queue=deque([0]);depth[0]=1
    while queue:
        node=queue.popleft()
        for child in children[node]:depth[child]=depth[node]+1;queue.append(child)
    height=max(depth)
    return sum(value*(height-level+1) for value,level in zip(nums,depth))
'''

SQUARES='''def maximum_two_square_area(mat):
    matrix=mat
    rows=len(matrix);cols=len(matrix[0]);prefix=[[0]*(cols+1) for _ in range(rows+1)]
    for row in range(rows):
        for col in range(cols):prefix[row+1][col+1]=matrix[row][col]+prefix[row][col+1]+prefix[row+1][col]-prefix[row][col]
    def possible(size):
        min_row=rows;max_row=-1;min_col=cols;max_col=-1
        for row in range(rows-size+1):
            for col in range(cols-size+1):
                total=prefix[row+size][col+size]-prefix[row][col+size]-prefix[row+size][col]+prefix[row][col]
                if total==size*size:min_row=min(min_row,row);max_row=max(max_row,row);min_col=min(min_col,col);max_col=max(max_col,col)
        return max_row-min_row>=size or max_col-min_col>=size
    left=1;right=min(rows,cols);best=0
    while left<=right:
        middle=(left+right)//2
        if possible(middle):best=middle;left=middle+1
        else:right=middle-1
    return best*best
'''

def lesson(a,b,c,d):return [a,b,c,d]
S_CASES=[[p,v,k] for p,v,k in (([-1,0,1],[1,2,3],3),([-1,0,0,0],[2,1,2,1],3),([-1],[5],5),([-1],[4],3),([-1,0],[1,2],3),([-1,0],[3,3],3),([-1,0,0],[1,1,1],1),([-1,0,1,2],[1,2,3,4],5),([-1,0,0,1,1],[2,4,6,8,10],4),([-1,0,0,2],[5,1,2,3],2),([-1,0,1],[3,6,9],6),([-1,0,0,0,0],[1,2,3,4,5],7),([-1,0,1,1],[7,2,5,8],3),([-1,0,0,1,2],[10,11,12,13,14],5),([-1,0,1,2,3],[1,1,1,1,1],2))]
D_CASES=[[a,b,k] for a,b,k in ((10,15,1),(201,204,2),(10,10,0),(11,11,0),(98,102,9),(98,102,0),(100,130,1),(999,1005,2),(1234,1250,3),(500,600,4),(10,99,0),(10,99,8),(808,818,1),(4444,4460,0),(9870,9900,2))]
P_CASES=[[n,e,s,k] for n,e,s,k in ((3,[[0,1,1],[1,2,1],[0,2,3]],'aab',1),(3,[[0,1,1],[1,2,1],[0,2,3]],'aab',2),(3,[[0,1,1],[1,2,1]],'aaa',2),(1,[],'a',1),(2,[],'ab',1),(2,[[0,1,5]],'aa',1),(2,[[0,1,5]],'aa',2),(4,[[0,1,2],[1,3,2],[0,2,1],[2,3,8]],'abca',1),(4,[[0,1,1],[1,2,1],[2,3,1]],'aaaa',4),(4,[[0,1,1],[1,2,1],[2,3,1]],'aaaa',3),(3,[[0,1,5],[1,0,1],[1,2,2]],'aba',1),(3,[[0,2,10],[0,1,2],[1,2,3]],'abc',1),(5,[[0,1,1],[1,4,9],[0,2,3],[2,3,1],[3,4,1]],'abbba',2),(3,[[0,1,1],[0,1,2],[1,2,1]],'abb',2),(4,[[0,1,3],[1,2,3],[2,3,3],[0,3,20]],'aabb',1))]
W_CASES=[[p,v] for p,v in (([-1,0,0,0,2,2],[5,2,3,1,4,6]),([-1,0,1,2],[1,2,3,4]),([-1],[7]),([-1,0],[2,3]),([-1,2,0],[1,2,3]),([-1,0,0],[5,5,5]),([-1,0,1,1],[1,1,1,1]),([-1,0,0,2,2],[3,1,4,1,5]),([-1,0,1,2,3],[2,4,6,8,10]),([-1,0,0,0],[10,1,1,1]),([-1,0,3,0],[1,2,3,4]),([-1,2,0,2],[4,3,2,1]),([-1,0,0,1,3],[9,8,7,6,5]),([-1,0,1,1,2,2],[1,3,5,7,9,11]),([-1,0,0,2,3,3],[6,5,4,3,2,1]))]
Q_CASES=[[[*rows]] for rows in ([[1,1,1,0],[1,1,1,1],[0,0,1,1]],[[0,1],[1,0]],[[0,0],[0,1]],[[1]],[[1,1]],[[1],[1]],[[1,1],[1,1]],[[1,0,1]],[[1,1,1],[1,1,1]],[[1,1,0],[1,1,0],[0,0,1]],[[0]],[[1,0],[0,1],[1,0]],[[1,1,1,1],[1,1,1,1]],[[1,1,0,1,1],[1,1,0,1,1]],[[1,1,1],[0,1,0],[1,1,1]])]

BATCH={
3939:entry('count_non_adjacent_divisible_subsets',[('parent','list[int]'),('nums','list[int]'),('k','int')],'int',['trees','dynamic programming','modular arithmetic'],['parent[0] is -1 and parent[i] < i for every other node.','Choose a nonempty independent set: no selected node may have its parent selected.','Count selections whose value sum is divisible by k, modulo 1,000,000,007.'],[([[-1,0,1],[1,2,3],3],'Only leaf node two alone has a sum divisible by three without selecting adjacent nodes.'),([[-1,0,0,0],[2,1,2,1],3],'The two valid sibling pairs have values 1+2 and 2+1.')],S_CASES,SUBSETS,[SUBSETS.replace('chosen[node][left]*skipped[child][right]','chosen[node][left]*total[right]'),SUBSETS.replace('-1)%modulus',')%modulus')],['Allows a selected parent to combine with a selected child.','Counts the empty subset when its sum is zero.'],subsets_oracle,random_subsets,lesson('For each subtree, separate counts where its root is skipped from counts where it is selected.','Store each state by its sum remainder modulo k.','A skipped parent may combine with either child state; a selected parent may combine only with a skipped child.','Convolve remainder arrays child by child, then add both root states at remainder zero and remove the empty selection.'),'O(nk²)','O(nk)',8),
3966:entry('count_good_integers',[('l','int'),('r','int'),('k','int')],'int',['digit dynamic programming','memoization','strings'],['10 <= l <= r <= 10^15 and 0 <= k <= 9.','An integer is good when every adjacent decimal digit differs by at most k.','Count both endpoints when they satisfy the rule.'],[([10,15,1],'Ten, eleven, and twelve satisfy the adjacent-difference limit.'),([201,204,2],'Only 201 and 202 keep both adjacent differences at most two.')],D_CASES,DIGITS,[DIGITS.replace('<=k','<k'),DIGITS.replace('count(l-1)','count(l)')],['Uses a strict digit-difference bound and rejects pairs differing exactly by k.','Subtracts through the left endpoint and makes the range half-open.'],digits_oracle,random_digits,lesson('Count valid values up to one bound, then subtract the count below the left endpoint.','A digit-DP state needs position, previous significant digit, whether the number started, and tightness.','Leading zeros do not participate in adjacency checks; once started, accept a digit only within k of the previous digit.','Memoization collapses all equal suffix states, giving work proportional to digit count rather than interval width.'),'O(d·10·11·2)','O(d·11·2)',8),
3970:entry('shortest_limited_label_path',[('n','int'),('edges','list[list[int]]'),('labels','str'),('k','int')],'int',['graphs','dijkstra','state expansion'],['Edges are directed and have positive weights.','The label sequence includes both endpoints and may contain at most k identical consecutive characters.','Return -1 when node n-1 is unreachable under that run constraint.'],[([3,[[0,1,1],[1,2,1],[0,2,3]],'aab',1],'The cheaper two-edge path begins with aa and is invalid, so the direct edge of cost three wins.'),([3,[[0,1,1],[1,2,1],[0,2,3]],'aab',2],'Allowing two equal labels makes the two-edge path valid with cost two.')],P_CASES,PATH,[PATH.replace('distance[0][1]=0;heap=[(0,0,1)]','distance[0][0]=0;heap=[(0,0,0)]'),PATH.replace('next_run<=k','next_run<k')],['Starts the initial label run at zero and permits one extra repeated label.','Rejects a run whose length equals the allowed maximum.'],path_oracle,random_path,lesson('The cheapest arrival at a node can still differ in how many repeated labels it carries.','Expand each graph node into states (node,current run length).','A different next label resets the run to one; an equal label increments it and is allowed only through k.','All weights are positive, so Dijkstra over the expanded states returns the first valid destination cost.'),'O((nk+ek)log(nk))','O(nk+e)',6),
4015:entry('weighted_tree_sum',[('parent','list[int]'),('nums','list[int]')],'int',['trees','breadth-first search','arrays'],['parent describes a valid tree rooted at zero; parent indices need not precede child indices.','Root depth is one and tree height is the maximum node depth.','Node i contributes nums[i] times (height-depth[i]+1).'],[([[-1,0,0,0,2,2],[5,2,3,1,4,6]],'The height is three; applying factors three, two, or one by depth gives total 37.'),([[-1,0,1,2],[1,2,3,4]],'The four-node chain has factors four through one, giving 4+6+6+4=20.')],W_CASES,WEIGHTED,[WEIGHTED.replace('height-level+1','height-level'),WEIGHTED.replace('height-level+1','level')],['Omits the inclusive current level, giving every deepest node zero weight.','Weights values by depth instead of remaining levels through the tree height.'],weighted_oracle,random_weighted,lesson('Build children from the parent array because a parent index may appear after its child.','Breadth-first traversal assigns every node depth from root depth one.','The largest assigned depth is the height.','A final pass multiplies each value by the number of levels from that node through the deepest level, inclusive.'),'O(n)','O(n)',5),
4016:entry('maximum_two_square_area',[('mat','list[list[int]]')],'int',['matrix','binary search','prefix sums'],['mat is nonempty, rectangular, binary, and has at most 500 rows and columns.','Choose two all-one square submatrices of equal side length that share no cell.','Return the area of either square, or zero if even two one-cell squares are impossible.'],[([[[1,1,1,0],[1,1,1,1],[0,0,1,1]]],'Two disjoint 2-by-2 all-one squares exist, so each has area four.'),([[[0,1],[1,0]]],'The two diagonal usable cells form two disjoint side-one squares.')],Q_CASES,SQUARES,[SQUARES.replace('max_row-min_row>=size or max_col-min_col>=size','max_row-min_row>size or max_col-min_col>size'),SQUARES.replace('total==size*size','total>=size*size-1')],['Requires a gap between squares and rejects squares that merely touch along an edge.','Allows each candidate square to contain one unusable cell.'],squares_oracle,random_squares,lesson('A two-dimensional prefix sum tests whether any square contains only ones in constant time.','For a fixed side length, track the minimum and maximum row and column among valid top-left corners.','Two equal squares are disjoint exactly when their row intervals or their column intervals are disjoint, so one coordinate span of at least k is sufficient.','Feasibility is monotone as k decreases, allowing binary search for the largest side length.'),'O(mn log min(m,n))','O(mn)',6),
}
