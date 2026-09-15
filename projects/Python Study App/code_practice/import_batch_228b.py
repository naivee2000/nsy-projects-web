"""Magical sequences, zeroing operations, exact-edge paths, subtree inversions, and grid cuts."""
from functools import lru_cache
from itertools import product

from .import_batch_055 import entry


def magical_oracle(args):
    m,k,nums=args;modulo=1000000007;answer=0
    for sequence in product(range(len(nums)),repeat=m):
        if sum(1<<index for index in sequence).bit_count()==k:
            value=1
            for index in sequence:value=value*nums[index]%modulo
            answer=(answer+value)%modulo
    return answer


def random_magical(rng):
    length=rng.randint(1,5);m=rng.randint(1,5);return [m,rng.randint(1,m),[rng.randint(1,12) for _ in range(length)]]


def zero_oracle(args):
    start=tuple(args[0]);queue=[start];distance={start:0}
    for state in queue:
        if not any(state):return distance[state]
        for left in range(len(state)):
            for right in range(left,len(state)):
                segment=state[left:right+1]
                if not segment or 0 in segment:continue
                minimum=min(segment)
                nxt=tuple(0 if left<=i<=right and value==minimum else value for i,value in enumerate(state))
                if nxt not in distance:distance[nxt]=distance[state]+1;queue.append(nxt)


def random_zero(rng):return [[rng.randint(0,4) for _ in range(rng.randint(1,7))]]


def path_oracle(args):
    n,edges,k,limit=args;graph=[[] for _ in range(n)]
    for source,target,weight in edges:graph[source].append((target,weight))
    answer=-1
    def visit(node,left,total):
        nonlocal answer
        if left==0:
            if total<limit:answer=max(answer,total)
            return
        for nxt,weight in graph[node]:visit(nxt,left-1,total+weight)
    for node in range(n):visit(node,k,0)
    return answer


def random_path(rng):
    n=rng.randint(1,8);order=list(range(n));rng.shuffle(order);position={node:i for i,node in enumerate(order)};edges=[]
    for u in range(n):
        for v in range(n):
            if position[u]<position[v] and rng.randrange(4)==0:edges.append([u,v,rng.randint(1,10)])
    return [n,edges,rng.randint(0,min(5,n)),rng.randint(1,35)]


def inversion_oracle(args):
    edges,nums,k=args;n=len(nums);graph=[[] for _ in range(n)]
    for u,v in edges:graph[u].append(v);graph[v].append(u)
    parent=[-1]*n;depth=[0]*n;order=[0]
    for node in order:
        for nxt in graph[node]:
            if nxt!=parent[node]:parent[nxt]=node;depth[nxt]=depth[node]+1;order.append(nxt)
    ancestors=[]
    for node in range(n):
        path=[];current=node
        while current!=-1:path.append(current);current=parent[current]
        ancestors.append(path)
    best=-10**30
    for mask in range(1<<n):
        chosen=[node for node in range(n) if mask>>node&1];valid=True
        for descendant in chosen:
            for ancestor in chosen:
                if ancestor!=descendant and ancestor in ancestors[descendant] and depth[descendant]-depth[ancestor]<k:valid=False
        if not valid:continue
        total=0
        for node,value in enumerate(nums):total+=value*(-1 if sum(mask>>ancestor&1 for ancestor in ancestors[node])%2 else 1)
        best=max(best,total)
    return best


def random_inversion(rng):
    n=rng.randint(2,9);edges=[[rng.randrange(node),node] for node in range(1,n)]
    return [edges,[rng.randint(-10,10) for _ in range(n)],rng.randint(1,min(4,n))]


def partition_oracle(args):
    grid=args[0];rows=len(grid);cols=len(grid[0]);total=sum(map(sum,grid))
    return any(sum(sum(row) for row in grid[:cut])*2==total for cut in range(1,rows)) or any(sum(grid[r][c] for r in range(rows) for c in range(cut))*2==total for cut in range(1,cols))


def random_partition(rng):
    rows=rng.randint(1,5);cols=rng.randint(1,5)
    if rows*cols<2:cols=2
    return [[[rng.randint(1,9) for _ in range(cols)] for _ in range(rows)]]


MAGICAL='''def magical_sequence_product_sum(m,k,nums):
    from functools import lru_cache
    from math import comb
    modulo=1000000007
    @lru_cache(None)
    def solve(index,left,bits,carry):
        if bits<0:return 0
        if index==len(nums):return int(left==0 and bits-carry.bit_count()==0)
        answer=0
        for count in range(left+1):
            combined=carry+count
            answer=(answer+comb(left,count)*pow(nums[index],count,modulo)*solve(index+1,left-count,bits-(combined&1),combined>>1))%modulo
        return answer
    return solve(0,m,k,0)
'''


ZERO='''def minimum_zeroing_operations(nums):
    stack=[];answer=0
    for value in nums:
        while stack and stack[-1]>value:stack.pop();answer+=1
        if value and (not stack or stack[-1]!=value):stack.append(value)
    return answer+len(stack)
'''


PATH='''def maximum_k_edge_path_weight(n,edges,k,t):
    current=[{0} for _ in range(n)]
    for _ in range(k):
        following=[set() for _ in range(n)]
        for source,target,weight in edges:
            for total in current[source]:
                if total+weight<t:following[target].add(total+weight)
        current=following
    return max((total for values in current for total in values),default=-1)
'''


INVERSION='''def maximum_subtree_inversion_sum(edges,nums,k):
    n=len(nums);graph=[[] for _ in range(n)]
    for u,v in edges:graph[u].append(v);graph[v].append(u)
    parent=[-1]*n;children=[[] for _ in range(n)];order=[0]
    for node in order:
        for nxt in graph[node]:
            if nxt!=parent[node]:parent[nxt]=node;children[node].append(nxt);order.append(nxt)
    dp=[None]*n
    for node in reversed(order):
        table=[[-10**30]*(k+1) for _ in range(2)]
        for parity in range(2):
            signed=-nums[node] if parity else nums[node]
            for distance in range(k+1):
                keep=signed+sum(dp[child][parity][min(k,distance+1)] for child in children[node])
                best=keep
                if distance==k:
                    invert=-signed+sum(dp[child][1-parity][min(k,1)] for child in children[node])
                    best=max(best,invert)
                table[parity][distance]=best
        dp[node]=table
    return dp[0][0][k]
'''


PARTITION='''def can_equal_partition_grid(grid):
    total=sum(map(sum,grid));running=0
    for row in grid[:-1]:
        running+=sum(row)
        if running*2==total:return True
    running=0
    for column in range(len(grid[0])-1):
        running+=sum(row[column] for row in grid)
        if running*2==total:return True
    return False
'''


def lesson(a,b,c,d):return [a,b,c,d]


MAGICAL_CASES=[[m,k,nums] for m,k,nums in [(5,5,[1,10,100,10000,1000000]),(2,2,[5,4,3,2,1]),(1,1,[28]),(1,1,[1,2]),(2,1,[1]),(2,1,[2,3]),(3,2,[1,2]),(3,1,[2,2,2]),(4,2,[1,3,5]),(4,3,[2,4,6,8]),(5,1,[1,1]),(2,1,[10,20,30]),(3,3,[7,11,13]),(6,2,[1,2,3])]]
ZERO_CASES=[[[*values]] for values in [[0,2],[3,1,2,1],[1,2,1,2,1,2],[0],[1],[1,1],[2,1],[1,2],[2,2,1,2],[0,1,0,1],[4,3,2,1],[1,3,2,3,1],[5,1,5,1,5],[2,0,2,1,2]]]
PATH_CASES=[list(case) for case in [(3,[[0,1,1],[1,2,2]],2,4),(3,[[0,1,2],[0,2,3]],1,3),(3,[[0,1,6],[1,2,8]],1,6),(1,[],0,1),(2,[],1,10),(2,[[0,1,5]],0,1),(2,[[0,1,5]],1,6),(2,[[0,1,5]],1,5),(4,[[0,1,2],[1,2,3],[0,2,4],[2,3,1]],2,7),(4,[[0,1,10],[0,2,1],[2,3,2]],2,20),(5,[[0,1,1],[1,2,1],[2,3,1],[3,4,1]],4,5),(4,[[0,2,4],[1,2,5],[2,3,6]],2,20),(3,[[0,1,2],[1,2,2]],3,10),(5,[[0,1,3],[0,2,5],[1,3,7],[2,3,2],[3,4,4]],3,15)]]
INVERSION_CASES=[[edges,nums,k] for edges,nums,k in [
([[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[4,-8,-6,3,7,-2,5],2),([[0,1],[1,2],[2,3],[3,4]],[-1,3,-2,4,-5],2),([[0,1],[0,2]],[0,-1,-2],3),
([[0,1]],[1,2],1),([[0,1]],[-1,-2],1),([[0,1],[1,2]],[1,-5,2],2),([[0,1],[0,2]],[5,-3,-4],1),
([[0,1],[0,2],[0,3]],[-5,1,2,3],2),([[0,1],[1,2],[1,3]],[4,-2,7,-8],3),([[0,1],[1,2],[2,3]],[1,2,3,4],1),
([[0,1],[0,2],[2,3],[2,4]],[-3,6,-2,5,-7],2),([[0,1],[1,2],[2,3],[3,4],[4,5]],[9,-8,7,-6,5,-4],3),
([[0,1],[0,2],[1,3],[2,4]],[0,0,-1,2,-3],2),([[0,1],[1,2],[1,3],[3,4],[3,5]],[2,-9,4,6,-1,3],4)]]
PARTITION_CASES=[[grid] for grid in [[[1,4],[2,3]],[[1,3],[2,4]],[[1,1]],[[1],[1]],[[1,2,3,6]],[[1],[2],[3],[6]],[[1,2],[3,4]],[[2,2],[2,2]],[[1,1,1],[3,3,3]],[[5,1,2],[1,1,4]],[[10,1],[2,3],[4,2]],[[1,2,1],[2,1,2]],[[7,3,5,5]],[[4],[1],[1],[2]]]]


BATCH={
3539:entry('magical_sequence_product_sum',[('m','int'),('k','int'),('nums','list[int]')],'int',['dynamic programming','combinatorics','bit manipulation'],['1 <= k <= m <= 30; nums has up to 50 positive values.','An ordered length-m index sequence is magical when the popcount of sum(2^index) equals k.','Sum the corresponding products of nums values modulo 1,000,000,007.'],[([5,5,[1,10,100,10000,1000000]],'The 120 permutations using each index once contribute products of 10^13, reduced modulo the modulus.'),([2,2,[5,4,3,2,1]],'Exactly ordered pairs of distinct indices have two set bits; their products sum to 170.')],MAGICAL_CASES,MAGICAL,[MAGICAL.replace('bits-(combined&1)','bits'),MAGICAL.replace('comb(left,count)','1')],['Never consumes finalized carry bits and accepts sequences with the wrong popcount.','Omits multinomial position choices and counts each frequency allocation only once.'],magical_oracle,random_magical,lesson('Choosing how often each index occurs creates binary carries; the lowest carry bit is finalized before moving to the next index.','Memoize index, unassigned positions, remaining set bits, and carry, multiplying by combination counts and nums powers.','Try count occurrences, consume (carry+count)&1, shift the carry, and finish by checking its remaining popcount.','Every ordered sequence has one frequency allocation and one of comb(left,count) placements at each step, so the recurrence counts products with exact multiplicity.'),'O(len(nums)*m^3*k)','O(len(nums)*m^2*k)',8),
3542:entry('minimum_zeroing_operations',[('nums','list[int]')],'int',['arrays','greedy','monotonic stacks'],['nums has up to 100,000 nonnegative integers.','An operation chooses a subarray and turns every occurrence of its minimum positive value to zero.','Return the minimum operations required to make the whole array zero.'],[([[0,2]],'Selecting the second position removes value two in one operation.'),([[3,1,2,1]],'Remove both ones together, then the separated three and two, for three operations.')],ZERO_CASES,ZERO,[ZERO.replace('while stack and stack[-1]>value','if stack and stack[-1]>value'),ZERO.replace('stack[-1]!=value','stack[-1]==value')],['Pops only one larger active level when several must end at the new smaller value.','Pushes duplicate levels and skips new distinct positive levels.'],zero_oracle,random_zero,lesson('Equal positive minima can share an operation only while no lower value has separated their active region.','Maintain increasing active value levels; pop completed larger levels and push a new nonzero level only when distinct.','For each value, pop and count while top>value; push value if positive and different; count all remaining levels.','Each popped level must end before the smaller barrier, while identical surviving tops represent occurrences removable together.'),'O(n)','O(n)',6),
3543:entry('maximum_k_edge_path_weight',[('n','int'),('edges','list[list[int]]'),('k','int'),('t','int')],'int',['graphs','dynamic programming','sets'],['The graph is a DAG with at most 300 nodes and edges; weights are positive.','Choose a path with exactly k edges and total weight strictly less than t.','Return the maximum qualifying weight, or -1 if no path exists.'],[([3,[[0,1,1],[1,2,2]],2,4],'The only two-edge path weighs three, which is below four.'),([3,[[0,1,2],[0,2,3]],1,3],'Weight two qualifies while weight three equals the strict limit and does not.')],PATH_CASES,PATH,[PATH.replace('total+weight<t','total+weight<=t'),PATH.replace('current=[{0} for _ in range(n)]','current=[{0}]+[set() for _ in range(n-1)]')],['Allows path weight equal to the strict upper limit.','Requires every path to start at node zero although any node may be its start.'],path_oracle,random_path,lesson('The sufficient state after a fixed number of edges is the endpoint and every reachable total below t.','Start weight zero at every node and advance one edge layer at a time using sets to deduplicate totals.','For k rounds, add each edge weight to totals at its source when the result stays below t; maximize the final layer.','Layer number enforces exact edge count, and induction over edges records precisely every attainable bounded path weight.'),'O(k*edges*t)','O(n*t)',6),
3544:entry('maximum_subtree_inversion_sum',[('edges','list[list[int]]'),('nums','list[int]'),('k','int')],'int',['trees','dynamic programming','depth first search'],['edges form a tree rooted at zero with up to 50,000 nodes; k <= 50.','Inverting a node flips every value in its rooted subtree. Ancestor-descendant inversion nodes must be at least k edges apart.','Choose inversion nodes to maximize the final total value sum.'],[([[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[4,-8,-6,3,7,-2,5],2],'Inverting nodes 0,3,4,6 produces final sum 27 while respecting two-edge ancestor spacing.'),([[[0,1],[1,2],[2,3],[3,4]],[-1,3,-2,4,-5],2],'Inverting the last node alone changes -5 to 5 and gives total nine.')],INVERSION_CASES,INVERSION,[INVERSION.replace('if distance==k:','if True:'),INVERSION.replace('dp[child][1-parity]','dp[child][parity]')],['Allows inversions too close to an inverted ancestor.','Fails to toggle descendant parity when an ancestor subtree is inverted.'],inversion_oracle,random_inversion,lesson('A subtree value’s sign is the parity of selected ancestors, while legality depends only on capped distance to the closest selected ancestor.','Root the tree and compute bottom-up DP for sign parity and distance states.','Compare keeping the node with selecting it when distance=k; selection flips parity for children and resets their distance to one.','Children are independent given these two state variables, which capture every effect an ancestor choice can have on a descendant.'),'O(nk)','O(nk)',8),
3546:entry('can_equal_partition_grid',[('grid','list[list[int]]')],'bool',['matrices','prefix sums','enumeration'],['grid contains positive integers and between 2 and 100,000 total cells.','Make exactly one cut between rows or between columns, leaving both rectangular sections nonempty.','Return whether the two section sums can be equal.'],[([[[1,4],[2,3]]],'The horizontal cut separates row sums five and five.'),([[[1,3],[2,4]]],'Neither the horizontal nor vertical cut balances the total.')],PARTITION_CASES,PARTITION,[PARTITION.replace('running+=sum(row)','running=sum(row)'),PARTITION.replace('running+=sum(row[column] for row in grid)','running=sum(row[column] for row in grid)')],['Checks each row alone rather than cumulative row prefixes.','Checks each column alone rather than cumulative column prefixes.'],partition_oracle,random_partition,lesson('A balanced straight cut exists exactly when a proper row prefix or column prefix contains half the total sum.','Compute the total, then scan all non-final row and column boundaries with running sums.','Return true when twice a proper prefix sum equals total; otherwise false.','Every horizontal or vertical cut corresponds to exactly one proper prefix, and positivity ensures both sides remain represented only at valid boundaries.'),'O(rows*columns)','O(1)',5),
}
