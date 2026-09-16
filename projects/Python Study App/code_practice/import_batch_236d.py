"""Tree rerooting, vowel transforms, circular balance, dynamic strings, and paths."""
from itertools import combinations
from .import_batch_055 import entry


def tree_score_oracle(args):
    n,edges,good=args;adj=[[] for _ in range(n)]
    for a,b in edges:adj[a].append(b);adj[b].append(a)
    answer=[-10**9]*n
    for mask in range(1,1<<n):
        nodes=[i for i in range(n) if mask>>i&1];seen={nodes[0]};stack=[nodes[0]]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if v not in seen and mask>>v&1:seen.add(v);stack.append(v)
        if len(seen)==len(nodes):
            score=sum(1 if good[i] else -1 for i in nodes)
            for i in nodes:answer[i]=max(answer[i],score)
    return answer

def random_tree_score(rng):
    n=rng.randint(2,9);edges=[[i,rng.randrange(i)] for i in range(1,n)]
    return [n,edges,[rng.randrange(2) for _ in range(n)]]

def vowel_oracle(args):
    words=args[0].split(' ');count=sum(c in 'aeiou' for c in words[0])
    return ' '.join([words[0]]+[word[::-1] if sum(c in 'aeiou' for c in word)==count else word for word in words[1:]])

def random_vowel(rng):
    words=[''.join(rng.choice('abcdeiouxyz') for _ in range(rng.randint(1,8))) for _ in range(rng.randint(1,10))]
    return [' '.join(words)]

def balance_oracle(args):
    values=args[0]
    if sum(values)<0:return -1
    negative=next((i for i,x in enumerate(values) if x<0),None)
    if negative is None:return 0
    units=[];n=len(values)
    for i,value in enumerate(values):units.extend([min((i-negative)%n,(negative-i)%n)]*value)
    return sum(sorted(units)[: -values[negative]])

def random_balance(rng):
    n=rng.randint(1,10);values=[rng.randint(0,7) for _ in range(n)]
    if rng.random()<.8:values[rng.randrange(n)]=-rng.randint(1,12)
    return [values]

def alternating_oracle(args):
    chars=list(args[0]);answer=[]
    for query in args[1]:
        if query[0]==1:
            index=query[1];chars[index]='B' if chars[index]=='A' else 'A'
        else:
            _,left,right=query;answer.append(sum(chars[i]==chars[i-1] for i in range(left+1,right+1)))
    return answer

def random_alternating(rng):
    n=rng.randint(1,18);s=''.join(rng.choice('AB') for _ in range(n));queries=[]
    for _ in range(rng.randint(1,25)):
        if rng.random()<.45:queries.append([1,rng.randrange(n)])
        else:
            left=rng.randrange(n);queries.append([2,left,rng.randrange(left,n)])
    if not any(q[0]==2 for q in queries):queries.append([2,0,n-1])
    return [s,queries]

def path_oracle(args):
    n,edges=args;adj=[[] for _ in range(n)]
    for a,b,w in edges:adj[a].append((b,w));adj[b].append((a,w))
    best=10**18
    def visit(node,seen,total,largest):
        nonlocal best
        if node==n-1:best=min(best,total-largest);return
        for nxt,weight in adj[node]:
            if nxt not in seen:visit(nxt,seen|{nxt},total+weight,max(largest,weight))
    visit(0,{0},0,0);return best

def random_path(rng):
    n=rng.randint(2,8);pairs=set();edges=[]
    for node in range(1,n):
        parent=rng.randrange(node);pairs.add((parent,node));edges.append([parent,node,rng.randint(1,20)])
    possible=[pair for pair in combinations(range(n),2) if pair not in pairs]
    rng.shuffle(possible)
    for a,b in possible[:rng.randint(0,min(5,len(possible)))]:edges.append([a,b,rng.randint(1,20)])
    return [n,edges]


TREE='''def maximum_subgraph_scores(n,edges,good):
    graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    parent=[-1]*n;order=[0]
    for node in order:
        for child in graph[node]:
            if child!=parent[node]:parent[child]=node;order.append(child)
    down=[1 if value else -1 for value in good]
    for node in reversed(order[1:]):down[parent[node]]+=max(0,down[node])
    answer=down[:]
    for node in order[1:]:
        outside=answer[parent[node]]-max(0,down[node]);answer[node]+=max(0,outside)
    return answer
'''

VOWELS='''def reverse_words_with_same_vowels(s):
    words=s.split(' ');vowels=set('aeiou');target=sum(char in vowels for char in words[0])
    for index in range(1,len(words)):
        if sum(char in vowels for char in words[index])==target:words[index]=words[index][::-1]
    return ' '.join(words)
'''

BALANCE='''def minimum_circular_balance_moves(balance):
    if sum(balance)<0:return -1
    try:target=next(index for index,value in enumerate(balance) if value<0)
    except StopIteration:return 0
    need=-balance[target];n=len(balance);sources=[]
    for index,value in enumerate(balance):
        if value>0:sources.append((min((index-target)%n,(target-index)%n),value))
    answer=0
    for distance,available in sorted(sources):
        moved=min(need,available);answer+=distance*moved;need-=moved
        if not need:break
    return answer
'''

ALTERNATING='''def minimum_alternating_deletions(s,queries):
    n=len(s);chars=list(s);tree=[0]*(n+1);equal=[0]*n
    def add(index,delta):
        index+=1
        while index<=n:tree[index]+=delta;index+=index&-index
    def prefix(index):
        total=0
        while index:total+=tree[index];index-=index&-index
        return total
    for index in range(1,n):
        equal[index]=int(chars[index]==chars[index-1]);add(index,equal[index])
    answer=[]
    for query in queries:
        if query[0]==1:
            changed=query[1];chars[changed]='B' if chars[changed]=='A' else 'A'
            for index in (changed,changed+1):
                if 0<index<n:
                    value=int(chars[index]==chars[index-1]);add(index,value-equal[index]);equal[index]=value
        else:
            _,left,right=query;answer.append(prefix(right+1)-prefix(left+1))
    return answer
'''

PATH='''def minimum_cost_excluding_max(n,edges):
    from heapq import heappop,heappush
    graph=[[] for _ in range(n)]
    for a,b,weight in edges:graph[a].append((b,weight));graph[b].append((a,weight))
    infinity=10**30;distance=[[infinity,infinity] for _ in range(n)];distance[0][0]=0;queue=[(0,0,0)]
    while queue:
        cost,node,used=heappop(queue)
        if cost!=distance[node][used]:continue
        for neighbor,weight in graph[node]:
            normal=cost+weight
            if normal<distance[neighbor][used]:distance[neighbor][used]=normal;heappush(queue,(normal,neighbor,used))
            if not used and cost<distance[neighbor][1]:distance[neighbor][1]=cost;heappush(queue,(cost,neighbor,1))
    return distance[n-1][1]
'''

PATH_WRONG_1='''def minimum_cost_excluding_max(n,edges):
    from heapq import heappop,heappush
    graph=[[] for _ in range(n)]
    for a,b,w in edges:graph[a].append((b,w));graph[b].append((a,w))
    distance=[10**30]*n;distance[0]=0;queue=[(0,0)]
    while queue:
        cost,node=heappop(queue)
        if cost!=distance[node]:continue
        for nxt,w in graph[node]:
            if cost+w<distance[nxt]:distance[nxt]=cost+w;heappush(queue,(cost+w,nxt))
    return distance[-1]
'''
PATH_WRONG_2=PATH.replace('normal=cost+weight','normal=cost').replace('if not used and cost<distance[neighbor][1]','if False and cost<distance[neighbor][1]')

def lesson(a,b,c,d):return [a,b,c,d]

T_CASES=[[n,e,g] for n,e,g in ((2,[[0,1]],[0,0]),(2,[[0,1]],[1,1]),(3,[[0,1],[1,2]],[1,0,1]),(3,[[0,1],[0,2]],[0,0,0]),(4,[[0,1],[0,2],[0,3]],[0,1,1,1]),(4,[[0,1],[1,2],[2,3]],[0,1,0,1]),(4,[[0,1],[0,2],[2,3]],[1,0,0,1]),(5,[[0,1],[1,2],[1,3],[3,4]],[0,1,0,1,1]),(5,[[0,1],[0,2],[2,3],[2,4]],[1,0,0,0,1]),(6,[[0,1],[1,2],[1,3],[3,4],[3,5]],[0,0,1,1,0,1]),(6,[[0,1],[0,2],[2,3],[3,4],[4,5]],[1,0,1,0,1,0]),(7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[0,1,0,1,1,0,1]),(8,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]],[0,0,1,1,0,1,0,1]),(9,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6],[6,7],[6,8]],[1,0,0,1,0,1,0,1,1]))]
V_CASES=[[s] for s in ('a','cat dog','sky why','ae io ou','book is nice','banana healthy','one two three','rhythm apple','education queue idea','a e i o u','code practice daily','leetcode algorithms are useful','hello world again','crypts myths fly')]
B_CASES=[[[*values]] for values in ([0],[5],[-1],[5,1,-4],[1,2,-5,2],[-3,2],[0,-4,0,4],[3,0,0,-3],[1,-5,4,0,0],[10,-6,0,0,0],[2,0,-7,0,6],[4,0,0,-9,0,5,0,0],[8,0,0,0,-5],[1,1,1,-3,0])]
A_CASES=[[s,q] for s,q in (('A',[[2,0,0]]),('AA',[[2,0,1]]),('AB',[[2,0,1],[1,1],[2,0,1]]),('ABA',[[2,1,2],[1,1],[2,0,2]]),('ABB',[[2,0,2],[1,2],[2,0,2]]),('BABA',[[2,0,3],[1,1],[2,1,3]]),('AAAA',[[2,0,3]]),('AABB',[[2,0,3],[1,2],[2,0,3]]),('ABBAA',[[2,1,4],[1,0],[2,0,4]]),('BAABAB',[[2,0,5],[1,2],[2,1,4]]),('ABABABA',[[1,3],[2,0,6],[1,0],[2,0,3]]),('BBAAABBB',[[2,0,7],[1,4],[2,2,6],[1,7],[2,0,7]]),('BABBB',[[2,0,4],[1,3],[2,2,4]]),('AAABABAAB',[[2,1,7],[1,5],[2,0,8]]))]
P_CASES=[[n,e] for n,e in ((2,[[0,1,5]]),(3,[[0,1,1],[1,2,1],[0,2,50000]]),(5,[[0,1,2],[1,2,7],[2,3,7],[3,4,4]]),(3,[[0,1,5],[1,2,2]]),(4,[[0,1,8],[1,3,3],[0,2,4],[2,3,4]]),(4,[[0,1,1],[1,2,10],[2,3,1],[0,3,20]]),(5,[[0,1,2],[1,4,9],[0,2,4],[2,3,4],[3,4,4]]),(5,[[0,1,10],[1,2,1],[2,4,10],[0,3,8],[3,4,8]]),(6,[[0,1,3],[1,5,7],[0,2,2],[2,3,2],[3,5,9]]),(3,[[0,1,6],[1,2,6],[0,2,9]]),(4,[[0,1,2],[1,2,2],[2,3,2],[0,3,7]]),(5,[[0,1,1],[1,2,5],[2,4,1],[0,3,3],[3,4,3],[1,3,2]]),(6,[[0,1,4],[1,2,7],[2,5,4],[0,3,6],[3,4,1],[4,5,6]]),(4,[[0,1,12],[1,3,2],[0,2,5],[2,3,9],[1,2,1]]))]

BATCH={
3772:entry('maximum_subgraph_scores',[('n','int'),('edges','list[list[int]]'),('good','list[int]')],'list[int]',['trees','dynamic programming','rerooting'],['2≤n≤100,000 and edges is a valid tree with n-1 edges.','good[i] is one for a good node and zero for a bad node.','For each node, maximize good nodes minus bad nodes over connected subgraphs containing it.'],[([3,[[0,1],[1,2]],[1,0,1]],'The entire chain scores one and is optimal for every node.'),([5,[[0,1],[1,2],[1,3],[3,4]],[0,1,0,1,1]],'The best scores are [2,3,2,3,3] after excluding harmful branches where possible.')],T_CASES,TREE,[TREE.replace('answer=down[:]','answer=[down[0]]*n'),TREE.replace("down=[1 if value else -1 for value in good]","down=[1 if value else 0 for value in good]")],['Uses the root score for every node instead of rerooting contributions.','Treats bad nodes as neutral rather than subtracting one.'],tree_score_oracle,random_tree_score,lesson('Give each good node weight +1 and each bad node weight -1.','First compute the best downward contribution, discarding negative child branches.','Reroot: a child may also take the positive part of its parent-side contribution.','Every connected subgraph through a node consists independently of that node plus beneficial incident branches.'),'O(n)','O(n)',8),
3775:entry('reverse_words_with_same_vowels',[('s','str')],'str',['strings','simulation'],['s has up to 100,000 lowercase letters with single spaces between words.','Count vowels a, e, i, o, u in the first word.','Reverse each later word with that same count; never reverse the first word.'],[(['cat and mice'],'cat has one vowel, so and reverses to dna while mice remains unchanged.'),(['book is nice'],'book has two vowels; only nice matches and becomes ecin.')],V_CASES,VOWELS,[VOWELS.replace('range(1,len(words))','range(len(words))'),VOWELS.replace('==target','!=target')],['Incorrectly reverses the first word when it matches its own vowel count.','Reverses words with a different vowel count instead of the same count.'],vowel_oracle,random_vowel,lesson('The first word establishes one fixed target vowel count.','Scan each remaining word once and compare its vowel count with the target.','Reverse only matching later words, then join with single spaces.','Each word decision depends only on its own count and the unchanged first-word target.'),'O(n)','O(n)',3),
3776:entry('minimum_circular_balance_moves',[('balance','list[int]')],'int',['arrays','greedy','sorting'],['balance has up to 100,000 integers and at most one is negative.','One move transfers one unit to a circular neighbor.','Return the minimum moves to make every balance nonnegative, or -1 when total balance is negative.'],[([[5,1,-4]],'The negative position takes one nearby unit and three units across one circular edge, costing four moves.'),([[1,2,-5,2]],'Four adjacent units and one unit two edges away cost six moves total.')],B_CASES,BALANCE,[BALANCE.replace('min((index-target)%n,(target-index)%n)','abs(index-target)'),BALANCE.replace('if sum(balance)<0:return -1','if False:return -1')],['Uses linear rather than circular distance, missing wraparound transfers.','Fails to reject arrays whose total balance cannot cover the deficit.'],balance_oracle,random_balance,lesson('Only the single negative position needs incoming units.','Each available unit has a circular distance to that position; closer units should move first.','Sort positive sources by distance and consume until the deficit is filled.','Exchanging a farther chosen unit for a nearer available unit never increases feasibility and strictly lowers cost.'),'O(n log n)','O(n)',5),
3777:entry('minimum_alternating_deletions',[('s','str'),('queries','list[list[int]]')],'list[int]',['strings','fenwick trees','dynamic queries'],['s contains up to 100,000 A/B characters and there are up to 100,000 queries.','[1,j] flips s[j]; [2,l,r] asks for the minimum deletions in the current substring.','Return answers only for type-two queries.'],[(['ABA',[[2,1,2],[1,1],[2,0,2]]],'BA is already alternating; after the flip the full string is AAA and needs two deletions.'),(['ABB',[[2,0,2],[1,2],[2,0,2]]],'ABB needs one deletion, then flipping the last character makes ABA need zero.')],A_CASES,ALTERNATING,[ALTERNATING.replace('prefix(right+1)-prefix(left+1)','prefix(right+1)-prefix(left)'),ALTERNATING.replace('for index in (changed,changed+1):','for index in (changed,):')],['Includes the adjacency immediately before the requested substring.','Updates only the left adjacency touched by a flip and misses the right one.'],alternating_oracle,random_alternating,lesson('For a binary string, one deletion is needed for each equal adjacent pair in the retained interval.','Store equality indicators for boundaries (i-1,i) in a Fenwick tree.','A flip changes only boundaries j and j+1; a range answer sums boundaries l+1 through r.','Runs of equal characters contribute length minus one, exactly matching their required deletions, and runs add independently.'),'O((n+q) log n)','O(n)',8),
3778:entry('minimum_cost_excluding_max',[('n','int'),('edges','list[list[int]]')],'int',['graphs','shortest paths','dijkstra'],['2≤n≤50,000; edges form a connected simple undirected graph with positive weights.','A path costs its edge sum minus one occurrence of its maximum edge.','Return the minimum possible cost from node zero to node n-1.'],[([5,[[0,1,2],[1,2,7],[2,3,7],[3,4,4]]],'The only path sums to twenty; excluding one maximum-weight edge leaves thirteen.'),([3,[[0,1,1],[1,2,1],[0,2,50000]]],'Taking the direct edge and excluding it gives cost zero.')],P_CASES,PATH,[PATH_WRONG_1,PATH_WRONG_2],['Returns the ordinary shortest-path sum without excluding an edge.','Makes every traversed edge free instead of excluding exactly one maximum edge.'],path_oracle,random_path,lesson('For any fixed path, excluding its maximum edge is equivalent to choosing one edge to traverse for free optimally.','Run Dijkstra on states (node, free-edge-used).','Each edge either adds its weight or, if unused, consumes the one free traversal at zero cost.','The minimum over all paths and free-edge choices always chooses a maximum edge on its selected path.'),'O((n+m) log n)','O(n+m)',7),
}
