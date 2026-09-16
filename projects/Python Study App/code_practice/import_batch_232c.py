"""Reversible paths, grid teleports, strategy windows, range products, and deletion DP."""
from functools import lru_cache
from .import_batch_055 import entry


def reversal_oracle(args):
    n,edges=args;expanded=[]
    for u,v,w in edges:expanded.append((u,v,w));expanded.append((v,u,2*w))
    inf=10**30;distance=[inf]*n;distance[0]=0
    for _ in range(n-1):
        changed=False
        for u,v,w in expanded:
            if distance[u]+w<distance[v]:distance[v]=distance[u]+w;changed=True
        if not changed:break
    return -1 if distance[-1]==inf else distance[-1]

def random_reversal(rng):
    n=rng.randint(2,8);edges=[]
    for u in range(n):
        for v in range(n):
            if u!=v and rng.randrange(5)==0:edges.append([u,v,rng.randint(1,12)])
    if not edges:edges=[[rng.randrange(n),rng.randrange(1,n),rng.randint(1,12)]]
    return [n,edges]

def teleport_oracle(args):
    grid,k=args;rows=len(grid);cols=len(grid[0]);cells=rows*cols;inf=10**30
    distance=[[inf]*(k+1) for _ in range(cells)];distance[0][0]=0;used=set()
    while True:
        choice=None
        for cell in range(cells):
            for teleports in range(k+1):
                if (cell,teleports) not in used and distance[cell][teleports]<inf and (choice is None or distance[cell][teleports]<choice[0]):choice=(distance[cell][teleports],cell,teleports)
        if choice is None:break
        cost,cell,teleports=choice;used.add((cell,teleports));r,c=divmod(cell,cols)
        for nr,nc in ((r+1,c),(r,c+1)):
            if nr<rows and nc<cols:
                target=nr*cols+nc;distance[target][teleports]=min(distance[target][teleports],cost+grid[nr][nc])
        if teleports<k:
            for target in range(cells):
                tr,tc=divmod(target,cols)
                if grid[tr][tc]<=grid[r][c]:distance[target][teleports+1]=min(distance[target][teleports+1],cost)
    return min(distance[-1])

def random_teleport(rng):
    rows=rng.randint(2,4);cols=rng.randint(2,4)
    return [[[rng.randint(0,12) for _ in range(cols)] for _ in range(rows)],rng.randint(0,3)]

def strategy_oracle(args):
    prices,strategy,k=args;answer=sum(a*b for a,b in zip(prices,strategy))
    for left in range(len(prices)-k+1):
        changed=strategy[:]
        for i in range(left,left+k//2):changed[i]=0
        for i in range(left+k//2,left+k):changed[i]=1
        answer=max(answer,sum(a*b for a,b in zip(prices,changed)))
    return answer

def random_strategy(rng):
    n=rng.randint(2,16);k=2*rng.randint(1,n//2)
    return [[rng.randint(1,30) for _ in range(n)],[rng.randint(-1,1) for _ in range(n)],k]

def xor_oracle(args):
    nums,queries=args;nums=nums[:];mod=10**9+7
    for left,right,step,factor in queries:
        index=left
        while index<=right:nums[index]=nums[index]*factor%mod;index+=step
    answer=0
    for value in nums:answer^=value
    return answer

def random_xor(rng):
    n=rng.randint(1,12);nums=[rng.randint(1,10**9) for _ in range(n)];queries=[]
    for _ in range(rng.randint(1,12)):
        left=rng.randrange(n);right=rng.randrange(left,n);queries.append([left,right,rng.randint(1,n),rng.randint(1,10**5)])
    return [nums,queries]

def deletion_oracle(args):
    nums,k=args
    @lru_cache(None)
    def solve(values):
        best=sum(values)
        for left in range(len(values)):
            total=0
            for right in range(left,len(values)):
                total+=values[right]
                if total%k==0:best=min(best,solve(values[:left]+values[right+1:]))
        return best
    return solve(tuple(nums))

def random_deletion(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,9))],rng.randint(1,10)]


REVERSAL='''def minimum_reversal_path_cost(n,edges):
    import heapq
    graph=[[] for _ in range(n)]
    for u,v,weight in edges:graph[u].append((v,weight));graph[v].append((u,2*weight))
    inf=10**30;distance=[inf]*n;distance[0]=0;queue=[(0,0)]
    while queue:
        cost,node=heapq.heappop(queue)
        if cost!=distance[node]:continue
        if node==n-1:return cost
        for neighbor,weight in graph[node]:
            new=cost+weight
            if new<distance[neighbor]:distance[neighbor]=new;heapq.heappush(queue,(new,neighbor))
    return -1
'''

TELEPORT='''def minimum_teleport_grid_cost(grid,k):
    rows=len(grid);cols=len(grid[0]);inf=10**30
    previous=[[inf]*cols for _ in range(rows)];previous[0][0]=0
    for r in range(rows):
        for c in range(cols):
            if r:previous[r][c]=min(previous[r][c],previous[r-1][c]+grid[r][c])
            if c:previous[r][c]=min(previous[r][c],previous[r][c-1]+grid[r][c])
    answer=previous[-1][-1];groups={}
    for r,row in enumerate(grid):
        for c,value in enumerate(row):groups.setdefault(value,[]).append((r,c))
    values=sorted(groups,reverse=True)
    for _ in range(k):
        current=[[inf]*cols for _ in range(rows)];best=inf
        for value in values:
            for r,c in groups[value]:best=min(best,previous[r][c])
            for r,c in groups[value]:current[r][c]=best
        for r in range(rows):
            for c in range(cols):
                if r:current[r][c]=min(current[r][c],current[r-1][c]+grid[r][c])
                if c:current[r][c]=min(current[r][c],current[r][c-1]+grid[r][c])
        answer=min(answer,current[-1][-1]);previous=current
    return answer
'''

STRATEGY='''def maximum_strategy_profit(prices,strategy,k):
    n=len(prices);original=[0]*(n+1);prices_sum=[0]*(n+1)
    for i,(price,action) in enumerate(zip(prices,strategy),1):
        original[i]=original[i-1]+price*action;prices_sum[i]=prices_sum[i-1]+price
    answer=original[n]
    for right in range(k,n+1):
        removed=original[right]-original[right-k]
        selling=prices_sum[right]-prices_sum[right-k//2]
        answer=max(answer,original[n]-removed+selling)
    return answer
'''

XOR_RANGE='''def xor_after_range_products(nums,queries):
    mod=10**9+7;nums=nums[:]
    for left,right,step,factor in queries:
        for index in range(left,right+1,step):nums[index]=nums[index]*factor%mod
    answer=0
    for value in nums:answer^=value
    return answer
'''

DELETION='''def minimum_sum_after_divisible_deletions(nums,k):
    inf=10**30;prefix=0;best={0:0}
    for value in nums:
        kept=best.get(prefix,inf)+value
        prefix=(prefix+value)%k
        best[prefix]=min(best.get(prefix,inf),kept)
    return best[prefix]
'''

def lesson(a,b,c,d):return [a,b,c,d]

R_CASES=[[n,e] for n,e in ((2,[[0,1,5]]),(2,[[1,0,5]]),(3,[[0,1,2],[2,1,3]]),(3,[[1,0,1],[1,2,4]]),(4,[[0,1,1],[1,2,1],[2,3,1]]),(4,[[1,0,1],[2,1,1],[3,2,1]]),(5,[[0,2,5],[3,2,1],[3,4,2]]),(3,[[0,1,9]]),(5,[[0,1,10],[2,1,1],[2,4,3],[0,3,20],[3,4,1]]),(6,[[0,1,2],[2,1,2],[2,5,2],[0,3,1],[4,3,1],[4,5,10]]),(4,[[0,2,2],[1,2,1],[1,3,7]]),(7,[[0,1,4],[2,1,2],[2,3,3],[4,3,1],[4,6,5]]))]
T_CASES=[[g,k] for g,k in (([[1,2],[3,4]],0),([[4,1],[2,3]],1),([[5,1],[1,5]],1),([[9,8],[7,1]],1),([[0,0],[0,0]],3),([[1,9,2],[8,7,3]],2),([[6,5],[4,3],[2,1]],1),([[1,2,3],[4,5,6],[7,8,9]],2),([[9,1,9],[1,9,1],[9,1,9]],1),([[3,3],[3,3]],2),([[10,2,8],[7,6,5],[4,3,1]],3),([[2,100],[100,2]],0))]
S_CASES=[[p,s,k] for p,s,k in (([1,1],[0,0],2),([5,4,2],[1,1,0],2),([2,9],[-1,-1],2),([8,1,7,2],[0,0,0,0],4),([3,6,9,12],[-1,1,-1,1],2),([10,1,1,10],[1,-1,-1,1],4),([4,5,6,7,8],[1,0,-1,0,1],2),([9,8,7,6,5,4],[-1,-1,0,0,1,1],6),([1,100,1,100],[1,-1,1,-1],2),([7,3,9,2,8,4],[0,1,-1,1,-1,0],4),([5,5,5,5],[1,1,1,1],2),([2,4,6,8,10,12],[-1,0,1,-1,0,1],4))]
X_CASES=[[a,q] for a,q in (([1],[[0,0,1,2]]),([2,3],[[1,1,1,4]]),([1,2,3],[[0,2,2,5]]),([10,20,30,40],[[0,3,1,1]]),([10**9],[[0,0,1,10**5]]),([2,3,5],[[0,2,1,10**5],[1,2,1,10**5]]),([7,7,7,7],[[0,3,3,2]]),([1,2,4,8,16],[[1,4,2,3],[0,4,4,5]]),([999999999,1],[[0,1,1,100000]]),([3,6,9,12,15],[[0,4,2,7],[1,3,1,11]]),([5,10,20],[[0,0,3,4],[2,2,2,6]]),([1,3,5,7,9,11],[[0,5,5,2],[1,5,2,3],[2,4,1,4]]))]
D_CASES=[[a,k] for a,k in (([1],1),([1],2),([2,4],3),([1,2,3],3),([2,2,2],4),([5,1,5],5),([4,7,2,9],6),([3,1,4,1,5],4),([10,20,30],7),([1,2,4,8,16],5),([6,6,5,5,4],6),([9,1,2,8,3,7],10))]

BATCH={
3650:entry('minimum_reversal_path_cost',[('n','int'),('edges','list[list[int]]')],'int',['graphs','dijkstra'],['Two to 50,000 vertices and up to 100,000 positive weighted directed edges.','Traverse a forward edge for w or reverse an incoming edge for a single move at cost 2w.','Return negative one when the destination is unreachable.'],[([4,[[0,1,3],[3,1,1],[2,3,4],[0,2,2]]],'The cheapest route costs three forward plus two for reversing 3->1.'),([4,[[0,2,1],[2,1,1],[1,3,1],[2,3,3]]],'Three forward edges of cost one reach the destination for total three.')],R_CASES,REVERSAL,[REVERSAL.replace('2*weight','weight'),REVERSAL.replace(";graph[v].append((u,2*weight))",'')],['Charges the original cost instead of double cost for a reversed traversal.','Never adds the temporary reversed traversal option.'],reversal_oracle,random_reversal,lesson('A positive-cost shortest path never needs to revisit a node, so its one-use switch cannot be reused.','Represent each original edge u->v,w by u->v,w and the one-move reversal v->u,2w.','Run Dijkstra from zero in the augmented directed graph.','Every legal move is an augmented edge, and every shortest augmented path is simple and therefore respects the per-node switch restriction.'),'O((n+e) log n)','O(n+e)',6),
3651:entry('minimum_teleport_grid_cost',[('grid','list[list[int]]'),('k','int')],'int',['matrices','dynamic programming','sorting'],['Both grid dimensions are between two and 80.','Right/down moves cost the destination value.','Up to k teleports may go free to any cell of value no greater than the source value.'],[([[[1,3,3],[2,5,4],[4,3,5]],2],'Move to value two, then five for cost seven and teleport to the final value five.'),([[[1,2],[2,3],[3,4]],1],'No useful non-increasing teleport improves the normal path cost nine.')],T_CASES,TELEPORT,[TELEPORT.replace('sorted(groups,reverse=True)','sorted(groups)'),TELEPORT.replace('current[r][c]=best','current[r][c]=best+grid[r][c]')],['Accumulates source values in ascending order and therefore permits upward-value teleports.','Incorrectly charges the destination cell value for a free teleport.'],teleport_oracle,random_teleport,lesson('For one more teleport, a destination of value v can inherit the best prior cost at any source value at least v.','Sweep cell-value groups downward while maintaining the best previous-layer cost, then relax normal right/down moves.','Build the zero-teleport DP, repeat the value sweep and grid DP k times, and keep the best final cost.','The descending sweep exactly implements every legal free teleport; the row-major relaxation then covers every normal path following that teleport.'),'O(k*m*n + m*n log(m*n))','O(m*n)',8),
3652:entry('maximum_strategy_profit',[('prices','list[int]'),('strategy','list[int]'),('k','int')],'int',['arrays','prefix sums','sliding windows'],['The arrays have equal length up to 100,000 and strategy entries are -1, 0, or 1.','k is even and between two and the array length.','Apply at most one modification: first half hold, second half sell.'],[([[4,2,8],[-1,0,1],2],'Changing the first two actions to hold then sell produces profit ten.'),([[5,4,3],[1,1,0],2],'Every modification is worse, so retain the original profit nine.')],S_CASES,STRATEGY,[STRATEGY.replace('answer=original[n]','answer=-10**30'),STRATEGY.replace('right-k//2','right-k')],['Forces a modification even when the original strategy is better.','Sets the whole selected window to sell instead of only its second half.'],strategy_oracle,random_strategy,lesson('A window modification replaces its original contribution with zero for the first half and prices for the second half.','Use prefix sums for original contributions and raw prices to score each window in constant time.','Start with the unmodified profit, subtract each window’s old contribution, and add its second-half price sum.','These are exactly the only changed terms, and checking every length-k window plus no modification covers all choices.'),'O(n)','O(n)',5),
3653:entry('xor_after_range_products',[('nums','list[int]'),('queries','list[list[int]]')],'int',['arrays','simulation'],['At most 1,000 values and 1,000 queries.','Each query multiplies indices left,left+step,...<=right modulo 1,000,000,007.','Apply queries in order and return the XOR of the final array.'],[([[1,1,1],[[0,2,1,4]]],'The array becomes [4,4,4], whose XOR is four.'),([[2,3,1,5,4],[[1,4,2,3],[0,2,1,2]]],'The final array [4,18,2,15,4] has XOR thirty-one.')],X_CASES,XOR_RANGE,[XOR_RANGE.replace('right+1','right'),XOR_RANGE.replace('nums[index]*factor%mod','nums[index]*factor')],['Treats the inclusive right endpoint as exclusive.','Omits the required modulus after each multiplication.'],xor_oracle,random_xor,lesson('The version-I limits permit direct execution of every touched index.','Process queries in order because later products apply to already-reduced values.','Step through range(left,right+1,step), multiply modulo M, then XOR the resulting array.','The loop visits exactly the specified arithmetic progression, and sequential updates match the query semantics.'),'O(sum touched indices)','O(n)',5),
3654:entry('minimum_sum_after_divisible_deletions',[('nums','list[int]'),('k','int')],'int',['arrays','dynamic programming','prefix remainders'],['Up to 100,000 positive integers and k up to 100,000.','Any contiguous current subarray with sum divisible by k may be deleted repeatedly.','Return the minimum sum of remaining elements.'],[([[1,1,1],2],'Delete two adjacent ones, leaving sum one.'),([[3,1,4,1,5],3],'Delete [1,4,1], then delete three, leaving five.')],D_CASES,DELETION,[DELETION.replace('best.get(prefix,inf)+value','best.get((prefix+value)%k,inf)+value'),DELETION.replace('return best[prefix]','return prefix')],['Looks up a state after consuming the current value rather than before it.','Returns only the total remainder instead of the minimum retained sum.'],deletion_oracle,random_deletion,lesson('The final kept elements form a subsequence whose removed gaps must each have sum divisible by k.','Track the minimum kept sum ending at each prefix-sum remainder.','Before consuming x, extend the state matching the current prefix remainder; store the new kept sum under the remainder after x.','Equal boundary remainders mean the deleted gap is divisible by k, so every transition is legal and every possible final kept subsequence is represented.'),'O(n)','O(k)',6),
}
