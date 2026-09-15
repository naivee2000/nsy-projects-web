"""String components, graph-cover walks, prefix queues, leaf recursion, and knapsack."""
from .import_batch_055 import entry

def groups_o(a):
    words=a[0];graph=[[] for _ in words]
    for i in range(len(words)):
        for j in range(i):
            mismatches=sum(x!=y for x,y in zip(words[i],words[j]))
            if mismatches in (0,2):graph[i].append(j);graph[j].append(i)
    seen=set();answer=0
    for i in range(len(words)):
        if i in seen:continue
        answer+=1;seen.add(i);todo=[i]
        while todo:
            for nxt in graph[todo.pop()]:
                if nxt not in seen:seen.add(nxt);todo.append(nxt)
    return answer
def rgroups(r):
    base=list('abcdef'[:r.randint(2,6)]);words=set()
    for _ in range(r.randint(1,8)):
        copy=base[:];r.shuffle(copy);words.add(''.join(copy))
    return [list(words)]

def cover_o(a):
    graph=a[0];n=len(graph);distance=[[n+1]*n for _ in range(n)]
    for i in range(n):
        distance[i][i]=0
        for j in graph[i]:distance[i][j]=1
    for k in range(n):
        for i in range(n):
            for j in range(n):distance[i][j]=min(distance[i][j],distance[i][k]+distance[k][j])
    dp={(1<<i,i):0 for i in range(n)}
    for mask in range(1,1<<n):
        for end in range(n):
            if (mask,end) not in dp:continue
            for nxt in range(n):
                key=(mask|1<<nxt,nxt);dp[key]=min(dp.get(key,n*n),dp[mask,end]+distance[end][nxt])
    return min(dp[(1<<n)-1,i] for i in range(n))
def rcover(r):
    n=r.randint(1,7);edges={}
    for i in range(1,n):edges[tuple(sorted((i,r.randrange(i))))]=1
    for i in range(n):
        for j in range(i):
            if r.random()<.25:edges[(j,i)]=1
    graph=[[] for _ in range(n)]
    for i,j in edges:graph[i].append(j);graph[j].append(i)
    return [graph]

def shortest_o(a):
    nums,k=a;best=len(nums)+1
    for i in range(len(nums)):
        total=0
        for j in range(i,len(nums)):
            total+=nums[j]
            if total>=k:best=min(best,j-i+1);break
    return best if best<=len(nums) else -1
def rshort(r):return [[r.randint(-10,15) for _ in range(r.randint(1,30))],r.randint(1,40)]

def _leaves(values):
    if not values:return []
    root=[values[0],None,None];queue=[root];i=1
    while queue and i<len(values):
        node=queue.pop(0)
        for child in (1,2):
            if i<len(values) and values[i] is not None:node[child]=[values[i],None,None];queue.append(node[child])
            i+=1
    answer=[];todo=[root]
    while todo:
        node=todo.pop()
        if node[1] is None and node[2] is None:answer.append(node[0])
        else:
            if node[2]:todo.append(node[2])
            if node[1]:todo.append(node[1])
    return answer
def leaves_o(a):return _leaves(a[0])==_leaves(a[1])
def rleaves(r):
    def tree():
        values=[r.randint(0,8)]
        for _ in range(r.randint(0,18)):values.append(None if r.random()<.25 else r.randint(0,8))
        while values and values[-1] is None:values.pop()
        return values
    return [tree(),tree()]

def schemes_o(a):
    people,minimum,group,profit=a;answer=0
    for mask in range(1<<len(group)):
        used=sum(group[i] for i in range(len(group)) if mask>>i&1);earned=sum(profit[i] for i in range(len(group)) if mask>>i&1)
        answer+=used<=people and earned>=minimum
    return answer%(10**9+7)
def rschemes(r):
    jobs=r.randint(1,9);return [r.randint(1,12),r.randint(0,15),[r.randint(1,6) for _ in range(jobs)],[r.randint(0,8) for _ in range(jobs)]]

GROUPS='''def similar_string_groups(strs):
    parent=list(range(len(strs)))
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for i in range(len(strs)):
        for j in range(i):
            if sum(a!=b for a,b in zip(strs[i],strs[j]))<=2:
                a,b=find(i),find(j)
                if a!=b:parent[a]=b
    return len({find(i) for i in range(len(strs))})
'''
COVER='''def shortest_graph_cover_walk(graph):
    n=len(graph);full=(1<<n)-1;queue=[(i,1<<i,0) for i in range(n)];seen={(i,1<<i) for i in range(n)}
    for node,mask,distance in queue:
        if mask==full:return distance
        for nxt in graph[node]:
            state=(nxt,mask|1<<nxt)
            if state not in seen:seen.add(state);queue.append((nxt,state[1],distance+1))
'''
SHORTEST='''def shortest_subarray_at_least_k(nums,k):
    prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    queue=[];answer=len(nums)+1
    for i,total in enumerate(prefix):
        while queue and total-prefix[queue[0]]>=k:answer=min(answer,i-queue.pop(0))
        while queue and prefix[queue[-1]]>=total:queue.pop()
        queue.append(i)
    return answer if answer<=len(nums) else -1
'''
LEAVES='''def leaf_sequences_match(root1,root2):
    def leaves(root):
        answer=[]
        def visit(node):
            if node is None:return
            if node.left is None and node.right is None:answer.append(node.val);return
            visit(node.left);visit(node.right)
        visit(root);return answer
    return leaves(root1)==leaves(root2)
'''
SCHEMES='''def profitable_scheme_count(n,minProfit,group,profit):
    mod=10**9+7;dp=[[0]*(minProfit+1) for _ in range(n+1)];dp[0][0]=1
    for members,gain in zip(group,profit):
        for used in range(n,members-1,-1):
            for earned in range(minProfit,-1,-1):dp[used][min(minProfit,earned+gain)]=(dp[used][min(minProfit,earned+gain)]+dp[used-members][earned])%mod
    return sum(dp[used][minProfit] for used in range(n+1))%mod
'''

BATCH={
839:entry('similar_string_groups',[('strs','list[str]')],'int',['strings','union find'],['All strings are distinct anagrams of equal length.','Two strings are similar when equal or when swapping exactly two positions in one makes the other.','Return the number of connected similarity groups.'],[([['tars','rats','arts','star']],'Tars connects through rats to arts, while star forms a second group.'),([['omv','ovm']],'Swapping the final two positions connects the pair.')],[[x] for x in [['a'],['ab','ba'],['tars','rats','arts','star'],['omv','ovm'],['abc','acb','bac'],['abc','bca'],['abcd','badc','abdc'],['aaa'],['abc','cab','bac'],['abcd','abdc','acbd','acdb'],['xy','yx'],['abcde','abced'],['abc','cba','bca'],['abcd','cdab']]],GROUPS,[GROUPS.replace('<=2','==0'),GROUPS.replace('parent[a]=b','parent[i]=j')],['Connects only identical strings and misses valid swaps.','Links raw indices instead of component roots, which can split transitive groups.'],groups_o,rgroups,['Compare every pair by counting mismatched positions.','Union pairs with zero or two mismatches.','Count distinct component representatives.','For anagrams, exactly two mismatches are precisely one swap; union-find closes similarity transitively.'],'O(count^2*length)','O(count)',8),
847:entry('shortest_graph_cover_walk',[('graph','list[list[int]]')],'int',['graphs','breadth-first search','bitmasks'],['graph is connected, undirected, and has at most twelve vertices.','Start at any vertex and revisit vertices or edges freely.','Return the minimum number of edges in a walk visiting every vertex.'],[([[[1,2,3],[0],[0],[0]]],'Starting at one leaf and ending at another visits all four vertices in four edges.'),([[[1],[0,2,4],[1,3,4],[2],[1,2]]],'A four-edge walk can visit all five vertices.')],[[g] for g in [[[ ]],[[1],[0]],[[1,2,3],[0],[0],[0]],[[1],[0,2,4],[1,3,4],[2],[1,2]],[[1],[0,2],[1]],[[1,3],[0,2],[1,3],[0,2]],[[1,2],[0,2],[0,1]],[[1],[0,2],[1,3],[2,4],[3]],[[1,2,3,4],[0],[0],[0],[0]],[[1,2],[0,3],[0,3],[1,2]],[[1],[0,2,3],[1],[1]],[[1,2],[0],[0,3],[2]],[[1,3],[0,2],[1,3,4],[0,2],[2]],[[1,2,3],[0,2],[0,1,3],[0,2]]]],COVER,[COVER.replace('queue=[(i,1<<i,0) for i in range(n)]','queue=[(0,1,0)]'),COVER.replace('mask|1<<nxt','mask')],['Allows starting only at vertex zero.','Never records newly visited vertices in the state mask.'],cover_o,rcover,['A state needs the current vertex and a bitmask of visited vertices.','Start BFS simultaneously from every possible one-vertex state.','Move along edges while OR-ing the destination bit; stop at the full mask.','BFS permits revisits yet deduplicates equivalent states and first reaches full coverage with minimum edges.'],'O(n*2^n+edges*2^n)','O(n*2^n)',8),
862:entry('shortest_subarray_at_least_k',[('nums','list[int]'),('k','int')],'int',['prefix sums','monotonic queues'],['nums is nonempty and may contain negative values; k is positive.','Return the minimum length of a nonempty contiguous subarray with sum at least k.','Return -1 if none exists.'],[([[1],1],'The single value reaches the target.'),([[2,-1,2],3],'Only the entire length-three array reaches three.')],[[a,k] for a,k in [([1],1),([1],2),([2,-1,2],3),([1,2],3),([84,-37,32,40,95],167),([-1,-2],1),([5,-10,6],6),([3,1,1],4),([10],5),([1,-1,1,-1,5],5),([2,3,-10,10],5),([0,0,1],1),([-5,20],15),([4,-1,2,1],6)]],SHORTEST,[SHORTEST.replace('>=k','>k'),SHORTEST.replace('>=total','>total')],['Rejects subarrays whose sum equals k exactly.','Retains equal prefix sums and can miss the shortest starting index.'],shortest_o,rshort,['Use prefix sums so a subarray sum is a difference of two prefixes.','Keep candidate starting prefixes in increasing value order and increasing index order.','Pop the front while the target is met; pop the back while the new prefix is no larger.','Front pops produce shortest feasible endings, and dominated larger or older prefixes can never improve a future result.'],'O(n)','O(n)',8),
872:entry('leaf_sequences_match',[('root1','TreeNode | None'),('root2','TreeNode | None')],'bool',['trees','recursion'],['Read leaves from left to right in each binary tree.','Return whether the two leaf-value sequences are identical.','Internal node values do not affect the result.'],[([[3,5,1,6,2,9,8,None,None,7,4],[3,5,1,6,7,4,2,None,None,None,None,None,None,9,8]],'Both trees have leaf sequence six,seven,four,nine,eight.'),([[1,2,3],[1,3,2]],'The leaf sequences two,three and three,two differ.')],[[a,b] for a,b in [([1],[1]),([1],[2]),([1,2,3],[1,2,3]),([1,2,3],[1,3,2]),([3,5,1,6,2,9,8,None,None,7,4],[3,5,1,6,7,4,2,None,None,None,None,None,None,9,8]),([0,1],[9,1]),([1,None,2],[2]),([1,2,None,3],[9,3]),([1,2,3,4],[1,4,3]),([1,2,3,None,4],[8,4,3]),([5,1,2],[7,1,2]),([1,0,0],[2,0,0]),([1,None,2,None,3],[9,3]),([4,2,6,1,3,5,7],[0,2,8,1,3,5,7])]],LEAVES,[LEAVES.replace('visit(node.left);visit(node.right)','visit(node.right);visit(node.left)'),LEAVES.replace('return leaves(root1)==leaves(root2)','return sorted(leaves(root1))==sorted(leaves(root2))')],['Reads leaves right-to-left.','Ignores the required left-to-right order by sorting leaf values.'],leaves_o,rleaves,['Collect leaves using left-before-right depth-first traversal.','A node is a leaf exactly when both children are missing.','Compare the two collected sequences directly.','DFS encounters leaves in left-to-right order, while ignoring every internal value.'],'O(n+m)','O(height1+height2)',3),
879:entry('profitable_scheme_count',[('n','int'),('minProfit','int'),('group','list[int]'),('profit','list[int]')],'int',['dynamic programming','knapsack'],['Each job may be selected at most once and uses group[i] members.','Use at most n members and earn at least minProfit total profit.','Return the number of job subsets modulo 1000000007.'],[([5,3,[2,2],[2,3]],'Selecting the second job alone or both jobs gives two profitable schemes.'),([10,5,[2,3,5],[6,7,8]],'Every nonempty subset earns at least five and fits within ten members, giving seven.')],[[*x] for x in [(1,0,[1],[0]),(5,3,[2,2],[2,3]),(10,5,[2,3,5],[6,7,8]),(1,1,[1],[1]),(1,2,[1],[1]),(3,0,[1,2],[0,0]),(5,5,[5],[5]),(5,5,[6],[10]),(4,3,[2,2,2],[1,2,3]),(6,4,[2,3,4],[2,3,5]),(2,1,[1,1],[1,1]),(10,10,[2,4,6],[3,7,10]),(7,2,[2,2,3],[0,2,4]),(3,5,[1,1,1],[2,2,2])]],SCHEMES,[SCHEMES.replace('range(n,members-1,-1)','range(members,n+1)'),SCHEMES.replace('min(minProfit,earned+gain)','earned+gain')],['Updates people counts upward and reuses the same job repeatedly.','Does not cap profit states and indexes beyond the DP table.'],schemes_o,rschemes,['Track scheme counts by used members and profit capped at minProfit.','For each job, update used-member states downward so it is selected at most once.','Add the job’s gain while capping the profit coordinate.','Every subset has a unique last processed selected job, and capping merges exactly the states already meeting the threshold.'],'O(jobs*n*minProfit)','O(n*minProfit)',8),
}
for pid in (872,):
    BATCH[pid]['params'][0]=('root1','TreeNode | None','treenode');BATCH[pid]['params'][1]=('root2','TreeNode | None','treenode')
BATCH[862]['wrong'][1]=SHORTEST.replace('i-queue.pop(0)','i-queue.pop(0)+1')
BATCH[862]['wrong_reasons'][1]='Adds one to every qualifying subarray length.'
BATCH[872]['wrong'][0]=LEAVES.replace('leaves(root1)==leaves(root2)','leaves(root1)==list(reversed(leaves(root2)))')
BATCH[872]['wrong_reasons'][0]='Compares the first leaf sequence with the reverse of the second.'
BATCH[879]['wrong'][1]=SCHEMES.replace('min(minProfit,earned+gain)','min(minProfit,earned)')
BATCH[879]['wrong_reasons'][1]='Never adds the selected job’s profit to the state.'
