"""Rank replacements, prime indices, valued islands, recovery paths, and popcount depth."""
from itertools import combinations
from math import comb
from .import_batch_055 import entry

def replacements_oracle(args):
    ranks=args[0];return sum(value<min(ranks[:i]) for i,value in enumerate(ranks[1:],1))

def random_replacements(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,30))]]

def is_prime(value):
    if value<2:return False
    return all(value%factor for factor in range(2,int(value**0.5)+1))

def split_oracle(args):
    nums=args[0];a=sum(value for index,value in enumerate(nums) if is_prime(index));b=sum(value for index,value in enumerate(nums) if not is_prime(index))
    return abs(a-b)

def random_split(rng):return [[rng.randint(-100,100) for _ in range(rng.randint(1,40))]]

def islands_oracle(args):
    grid,k=args;m=len(grid);n=len(grid[0]);parent=list(range(m*n))
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for r in range(m):
        for c in range(n):
            if not grid[r][c]:continue
            for dr,dc in ((1,0),(0,1)):
                nr,nc=r+dr,c+dc
                if nr<m and nc<n and grid[nr][nc]:
                    a,b=find(r*n+c),find(nr*n+nc);parent[a]=b
    sums={}
    for r in range(m):
        for c in range(n):
            if grid[r][c]:root=find(r*n+c);sums[root]=sums.get(root,0)+grid[r][c]
    return sum(total%k==0 for total in sums.values())

def random_islands(rng):
    m=rng.randint(1,6);n=rng.randint(1,6)
    return [[[rng.randint(0,8) for _ in range(n)] for _ in range(m)],rng.randint(1,10)]

def recovery_oracle(args):
    edges,online,k=args;n=len(online);graph=[[] for _ in range(n)]
    for u,v,cost in edges:graph[u].append((v,cost))
    answer=-1
    def visit(node,total,score):
        nonlocal answer
        if total>k:return
        if node==n-1:answer=max(answer,score);return
        for nxt,cost in graph[node]:
            if nxt==n-1 or online[nxt]:visit(nxt,total+cost,min(score,cost))
    visit(0,0,10**30);return answer

def random_recovery(rng):
    n=rng.randint(2,8);pairs=[(u,v) for u in range(n) for v in range(u+1,n)];rng.shuffle(pairs)
    edges=[[u,v,rng.randint(0,15)] for u,v in pairs[:rng.randint(0,min(12,len(pairs)))]]
    online=[rng.randrange(4)!=0 for _ in range(n)];online[0]=online[-1]=True
    return [edges,online,rng.randint(0,40)]

def depth(value):
    steps=0
    while value!=1:value=value.bit_count();steps+=1
    return steps

def popcount_oracle(args):
    n,k=args;return sum(depth(value)==k for value in range(1,n+1))

def random_popcount(rng):return [rng.randint(1,3000),rng.randint(0,5)]

REPLACEMENTS='''def count_student_replacements(ranks):
    current=ranks[0];answer=0
    for rank in ranks[1:]:
        if rank<current:current=rank;answer+=1
    return answer
'''

SPLIT='''def prime_index_sum_difference(nums):
    n=len(nums);prime=[True]*n
    if n>0:prime[0]=False
    if n>1:prime[1]=False
    for value in range(2,int(n**0.5)+1):
        if prime[value]:
            for multiple in range(value*value,n,value):prime[multiple]=False
    prime_sum=sum(nums[i] for i in range(n) if prime[i])
    return abs(prime_sum-(sum(nums)-prime_sum))
'''

ISLANDS='''def count_divisible_value_islands(grid,k):
    m=len(grid);n=len(grid[0]);seen=set();answer=0
    for row in range(m):
        for column in range(n):
            if not grid[row][column] or (row,column) in seen:continue
            seen.add((row,column));stack=[(row,column)];total=0
            while stack:
                r,c=stack.pop();total+=grid[r][c]
                for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr,nc=r+dr,c+dc
                    if 0<=nr<m and 0<=nc<n and grid[nr][nc] and (nr,nc) not in seen:seen.add((nr,nc));stack.append((nr,nc))
            answer+=total%k==0
    return answer
'''

RECOVERY='''def maximum_recovery_path_score(edges,online,k):
    import heapq
    n=len(online);graph=[[] for _ in range(n)];maximum=0
    for u,v,cost in edges:
        if online[u] and online[v]:graph[u].append((v,cost));maximum=max(maximum,cost)
    def feasible(score):
        distance=[float('inf')]*n;distance[0]=0;heap=[(0,0)]
        while heap:
            total,node=heapq.heappop(heap)
            if total!=distance[node]:continue
            if node==n-1:return total<=k
            for nxt,cost in graph[node]:
                candidate=total+cost
                if cost>=score and candidate<distance[nxt]:distance[nxt]=candidate;heapq.heappush(heap,(candidate,nxt))
        return False
    low,high=0,maximum
    while low<high:
        middle=(low+high+1)//2
        if feasible(middle):low=middle
        else:high=middle-1
    return low if feasible(low) else -1
'''

POPCOUNT='''def count_popcount_depth(n,k):
    from math import comb
    if k==0:return 1
    def count_with_ones(ones):
        answer=0;remaining=ones
        for position in range(n.bit_length()-1,-1,-1):
            if n>>position&1:
                if 0<=remaining<=position:answer+=comb(position,remaining)
                remaining-=1
                if remaining<0:break
        return answer+(remaining==0)
    answer=0
    for ones in range(1,n.bit_length()+1):
        value=ones;steps=0
        while value!=1:value=value.bit_count();steps+=1
        if steps==k-1:answer+=count_with_ones(ones)
    return answer-(k==1)
'''

def lesson(a,b,c,d):return [a,b,c,d]

R_CASES=[[x] for x in ([1],[1,2,3],[3,2,1],[5,4,4,3],[2,2,4],[10,1,9,0],[7,6,5,4],[1,1,1],[9,8,10,7,6],[4,3,2,1,0],[100,50,75,25],[3,1,2,0,4])]
S_CASES=[[x] for x in ([1],[1,2],[-1,5,7,1],[0,0,0],[1,2,3,4],[10,-10,5,-5],[7]*8,list(range(10)),[-5,-4,-3,-2,-1],[100,1,1,1,1,1],[-10,20,-30,40],[3,1,4,1,5,9,2])]
I_CASES=[[g,k] for g,k in (([[1]],1),([[1]],2),([[0]],3),([[3,0,6,0],[0,3,0,3],[3,0,3,0]],3),([[1,1],[1,1]],4),([[1,0],[0,1]],1),([[2,2,0],[0,3,3]],2),([[5,0,5]],5),([[1],[2],[3]],3),([[1,2,0],[3,0,4]],6),([[10,0],[0,10]],7),([[2,4,6],[0,0,0]],4))]
N_CASES=[[e,o,k] for e,o,k in (([],[True,True],0),([[0,1,0]],[True,True],0),([[0,1,5]],[True,True],4),([[0,1,5]],[True,True],5),([[0,1,5],[1,2,5]],[True,True,True],10),([[0,1,5],[1,2,5]],[True,False,True],10),([[0,1,0],[1,2,0]],[True,True,True],0),([[0,1,8],[0,2,4],[2,3,4],[1,3,1]],[True]*4,8),([[0,1,2],[1,3,9],[0,2,5],[2,3,5]],[True]*4,10),([[0,1,3],[1,4,3],[0,2,4],[2,3,4],[3,4,4]],[True]*5,12),([[0,2,7],[2,3,2]],[True,False,True,True],9),([[0,1,1],[1,2,1],[2,3,1]],[True]*4,2))]
P_CASES=[[n,k] for n,k in ((1,0),(1,1),(2,1),(3,2),(7,3),(8,1),(15,2),(16,1),(31,2),(63,3),(100,2),(1000,3))]

BATCH={
3616:entry('count_student_replacements',[('ranks','list[int]')],'int',['arrays','simulation'],['One to 100,000 positive ranks arrive in order.','Lower numbers are better.','The first student is selected without counting a replacement; later strict improvements count.'],[([[4,1,2]],'Rank one replaces rank four, while rank two does not.'),([[2,2,3]],'Equal and worse ranks cause no replacement.')],R_CASES,REPLACEMENTS,[REPLACEMENTS.replace('rank<current','rank<=current'),REPLACEMENTS.replace('current=ranks[0]','current=float(\'inf\')')],['Counts equal ranks as improvements.','Counts the initially selected student as a replacement.'],replacements_oracle,random_replacements,lesson('The selected rank is the smallest rank seen so far.','Scan arrivals while maintaining that running minimum.','On a strict new minimum, increment the answer and update the selected rank.','A replacement occurs exactly at a new strict prefix minimum after index zero.'),'O(n)','O(1)',3),
3618:entry('prime_index_sum_difference',[('nums','list[int]')],'int',['arrays','number theory','sieve'],['The array has up to 100,000 signed values.','Indices are zero-based; zero and one are not prime.','Return the absolute difference between prime-index and other-index sums.'],[([[2,3,4]],'Only index two is prime, producing |4-(2+3)|=1.'),([[-1,5,7,0]],'Prime indices two and three sum to seven; the other indices sum to four.')],S_CASES,SPLIT,[SPLIT.replace('if n>1:prime[1]=False','if n>1:prime[1]=True'),SPLIT.replace('if prime[i]','if is_prime(nums[i])').replace("def prime_index_sum_difference(nums):","def prime_index_sum_difference(nums):\n    def is_prime(x):return x>=2 and all(x%d for d in range(2,int(x**0.5)+1))")],['Incorrectly treats index one as prime.','Classifies elements by whether their values are prime rather than their indices.'],split_oracle,random_split,lesson('Membership depends on index primality, not the stored value.','Sieve prime indices once, then accumulate the two groups.','Sum values at prime indices and subtract the complementary sum.','The sieve classifies every index exactly once, so the two sums form a complete partition.'),'O(n log log n)','O(n)',5),
3619:entry('count_divisible_value_islands',[('grid','list[list[int]]'),('k','int')],'int',['matrices','graphs','flood fill'],['The grid has at most 100,000 cells.','Positive cells form four-neighbor islands; zero is water.','Count islands whose value sum is divisible by positive k.'],[([[[0,2,1,0,0],[0,5,0,0,5],[0,0,1,0,0],[0,1,4,7,0],[0,2,0,0,8]],5],'Exactly two of the four island sums are divisible by five.'),([[[3,0,3,0],[0,3,0,3],[3,0,3,0]],3],'Six isolated value-three islands all qualify.')],I_CASES,ISLANDS,[ISLANDS.replace("((1,0),(-1,0),(0,1),(0,-1))","((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1))"),ISLANDS.replace('total%k==0','total%k!=0')],['Incorrectly joins diagonally touching land.','Counts nondivisible island sums instead of divisible ones.'],islands_oracle,random_islands,lesson('Each positive cell belongs to one four-neighbor component.','Flood-fill every unseen land cell while accumulating its values.','After each component traversal, test its sum modulo k.','The traversals partition all land cells into exactly the defined islands, each counted once.'),'O(m*n)','O(m*n)',5),
3620:entry('maximum_recovery_path_score',[('edges','list[list[int]]'),('online','list[bool]'),('k','int')],'int',['graphs','shortest paths','binary search'],['The directed graph is acyclic with up to 50,000 nodes and 100,000 edges.','Only paths through online nodes are valid; endpoints are always online.','Total edge cost must not exceed k; maximize the minimum edge cost or return -1.'],[([[[0,1,5],[1,3,10],[0,2,3],[2,3,4]],[True,True,True,True],10],'Only the route with edge costs three and four fits the budget, scoring three.'),([[[0,1,7],[1,4,5],[0,2,6],[2,3,6],[3,4,2],[2,4,6]],[True,True,True,False,True],12],'The online path through node two scores six.')],N_CASES,RECOVERY,[RECOVERY.replace('if online[u] and online[v]','if True'),RECOVERY.replace('return total<=k','return total<k')],['Allows paths through offline intermediate nodes.','Rejects a path whose total cost equals the budget.'],recovery_oracle,random_recovery,lesson('Requiring every edge to meet a score threshold turns the objective into a monotone feasibility question.','Binary search the score; for each threshold, find the cheapest path using qualifying online edges.','Keep edges with cost at least the threshold and run Dijkstra, accepting destination cost at most k.','A feasible score implies every lower score is feasible, and shortest-path cost exactly tests the budget.'),'O((V+E) log V log W)','O(V+E)',8),
3621:entry('count_popcount_depth',[('n','int'),('k','int')],'int',['combinatorics','digit dynamic programming','bit manipulation'],['One <= n <= 10^15 and zero <= k <= five.','Depth is the minimum repeated-popcount applications needed to reach one.','Count integers from one through n with depth exactly k.'],[([4,1],'Powers two and four have one set bit and depth one.'),([7,2],'Three, five, and six have two set bits and depth two.')],P_CASES,POPCOUNT,[POPCOUNT.replace('if k==0:return 1','if k==0:return 0'),POPCOUNT.replace('return answer-(k==1)','return answer')],['Forgets that integer one is the unique depth-zero value.','Incorrectly counts integer one among depth-one values.'],popcount_oracle,random_popcount,lesson('For x>1, its depth is one plus the depth of popcount(x), which is at most the bit length.','Group integers by number of set bits and count each group up to n combinatorially.','Scan n from high bits to low, adding binomial choices whenever a one bit may be replaced by zero.','Every integer is counted by its unique first lower bit choice, and the small set-bit count determines its remaining depth.'),'O(log^2 n)','O(1)',8),
}
