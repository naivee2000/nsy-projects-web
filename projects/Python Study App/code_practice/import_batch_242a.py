"""Point generations, threshold paths, joined words, divisible reductions, and taxed roads."""
from collections import Counter,deque
from itertools import combinations
from .import_batch_055 import entry

def generation_oracle(args):
    points,target=args;known={tuple(point):0 for point in points};generation=0
    if tuple(target) in known:return 0
    while True:
        values=list(known);created=set()
        for a,b in combinations(values,2):created.add(tuple((x+y)//2 for x,y in zip(a,b)))
        created-=set(known)
        if not created:return -1
        generation+=1
        if tuple(target) in created:return generation
        for point in created:known[point]=generation
def random_generation(rng):
    points=[list(point) for point in rng.sample([(x,y,z) for x in range(3) for y in range(3) for z in range(3)],rng.randint(1,5))]
    return [points,[rng.randint(0,2) for _ in range(3)]]

def threshold_oracle(args):
    n,edges,source,target,k=args
    if source==target:return 0
    graph=[[] for _ in range(n)]
    for u,v,w in edges:graph[u].append((v,w));graph[v].append((u,w))
    def feasible(bound):
        distance=[10**9]*n;distance[source]=0;queue=deque([source])
        while queue:
            node=queue.popleft()
            for nxt,weight in graph[node]:
                candidate=distance[node]+(weight>bound)
                if candidate<distance[nxt]:distance[nxt]=candidate;queue.append(nxt)
        return distance[target]<=k
    for bound in [0]+sorted({w for _,_,w in edges}):
        if feasible(bound):return bound
    return -1
def random_threshold(rng):
    n=rng.randint(1,8);all_edges=[(i,j) for i in range(n) for j in range(i+1,n)];chosen=rng.sample(all_edges,rng.randint(0,min(len(all_edges),12)))
    return [n,[[u,v,rng.randint(1,20)] for u,v in chosen],rng.randrange(n),rng.randrange(n),rng.randint(0,5)]

def words_oracle(args):
    text=''.join(args[0]);tokens=[];current=''
    for i,character in enumerate(text):
        joiner=character=='-' and i>0 and i+1<len(text) and text[i-1].islower() and text[i+1].islower()
        if character.islower() or joiner:current+=character
        elif current:tokens.append(current);current=''
    if current:tokens.append(current)
    counts=Counter(tokens);return [counts[query] for query in args[1]]
def random_words(rng):
    text=''.join(rng.choice('abc- 1_') for _ in range(rng.randint(1,60)));cuts=sorted(rng.sample(range(1,len(text)),rng.randint(0,min(5,max(0,len(text)-1))))) if len(text)>1 else []
    chunks=[text[a:b] for a,b in zip([0]+cuts,cuts+[len(text)])];queries=[''.join(rng.choice('abc-') for _ in range(rng.randint(1,6))) for _ in range(rng.randint(1,8))]
    return [chunks,queries]

def divisible_oracle(args):
    nums=args[0];return sum(min(value for value in nums if original%value==0) for original in nums)
def random_divisible(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,20))]]

def apples_oracle(args):
    n,prices,roads=args;inf=10**15;empty=[[inf]*n for _ in range(n)];loaded=[[inf]*n for _ in range(n)]
    for i in range(n):empty[i][i]=loaded[i][i]=0
    for u,v,cost,tax in roads:empty[u][v]=empty[v][u]=min(empty[u][v],cost);loaded[u][v]=loaded[v][u]=min(loaded[u][v],cost*tax)
    for mid in range(n):
        for i in range(n):
            for j in range(n):empty[i][j]=min(empty[i][j],empty[i][mid]+empty[mid][j]);loaded[i][j]=min(loaded[i][j],loaded[i][mid]+loaded[mid][j])
    return [min(prices[j]+empty[i][j]+loaded[i][j] for j in range(n)) for i in range(n)]
def random_apples(rng):
    n=rng.randint(1,7);all_edges=[(i,j) for i in range(n) for j in range(i+1,n)];chosen=rng.sample(all_edges,rng.randint(0,min(len(all_edges),10)))
    return [n,[rng.randint(1,30) for _ in range(n)],[[u,v,rng.randint(1,10),rng.randint(1,5)] for u,v in chosen]]

GENERATIONS='''def minimum_point_generation(points,target):
    known={tuple(point) for point in points};target=tuple(target)
    if target in known:return 0
    generation=0
    while True:
        values=list(known);created=set()
        for i in range(len(values)):
            for j in range(i+1,len(values)):created.add(tuple((values[i][axis]+values[j][axis])//2 for axis in range(3)))
        created-=known
        if not created:return -1
        generation+=1
        if target in created:return generation
        known|=created
'''

THRESHOLD='''def minimum_heavy_edge_threshold(n,edges,source,target,k):
    from collections import deque
    if source==target:return 0
    graph=[[] for _ in range(n)]
    for u,v,weight in edges:graph[u].append((v,weight));graph[v].append((u,weight))
    def feasible(bound):
        distance=[10**9]*n;distance[source]=0;queue=deque([source])
        while queue:
            node=queue.popleft()
            for nxt,weight in graph[node]:
                candidate=distance[node]+(weight>bound)
                if candidate<distance[nxt]:
                    distance[nxt]=candidate
                    if weight<=bound:queue.appendleft(nxt)
                    else:queue.append(nxt)
        return distance[target]<=k
    candidates=[0]+sorted({weight for _,_,weight in edges});left=0;right=len(candidates)-1
    if not feasible(candidates[right]):return -1
    while left<right:
        middle=(left+right)//2
        if feasible(candidates[middle]):right=middle
        else:left=middle+1
    return candidates[left]
'''

WORDS='''def count_joined_words(chunks,queries):
    from collections import Counter
    text=''.join(chunks);words=[];current=[]
    for i,character in enumerate(text):
        joiner=character=='-' and i>0 and i+1<len(text) and text[i-1].islower() and text[i+1].islower()
        if character.islower() or joiner:current.append(character)
        elif current:words.append(''.join(current));current=[]
    if current:words.append(''.join(current))
    counts=Counter(words);return [counts[query] for query in queries]
'''

DIVISIBLE='''def minimum_divisible_replacement_sum(nums):
    maximum=max(nums);present=[False]*(maximum+1)
    for value in nums:present[value]=True
    best=list(range(maximum+1))
    for divisor in range(1,maximum+1):
        if present[divisor]:
            for multiple in range(divisor,maximum+1,divisor):best[multiple]=min(best[multiple],divisor)
    return sum(best[value] for value in nums)
'''

APPLES='''def minimum_apple_costs(n,prices,roads):
    import heapq
    empty=[[] for _ in range(n)];loaded=[[] for _ in range(n)]
    for u,v,cost,tax in roads:empty[u].append((v,cost));empty[v].append((u,cost));loaded[u].append((v,cost*tax));loaded[v].append((u,cost*tax))
    def distances(graph,start):
        result=[10**30]*n;result[start]=0;heap=[(0,start)]
        while heap:
            distance,node=heapq.heappop(heap)
            if distance!=result[node]:continue
            for nxt,weight in graph[node]:
                candidate=distance+weight
                if candidate<result[nxt]:result[nxt]=candidate;heapq.heappush(heap,(candidate,nxt))
        return result
    answer=[]
    for start in range(n):
        outward=distances(empty,start);returning=distances(loaded,start)
        answer.append(min(prices[shop]+outward[shop]+returning[shop] for shop in range(n)))
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]
G_CASES=[[p,t] for p,t in (([[0,0,0],[6,6,6]],[3,3,3]),([[0,0,0],[5,5,5]],[1,1,1]),([[0,0,0],[2,2,2],[3,3,3]],[2,2,2]),([[1,2,3]],[5,5,5]),([[0,0,0],[1,1,1]],[0,0,0]),([[0,0,0],[4,0,0]],[1,0,0]),([[0,0,0],[0,4,0]],[0,3,0]),([[0,0,0],[0,0,4]],[0,0,2]),([[1,1,1],[6,6,6]],[3,3,3]),([[0,6,0],[6,0,6]],[3,3,3]),([[0,0,0],[6,6,0],[6,0,6]],[3,3,3]),([[2,2,2],[4,4,4]],[3,3,3]),([[0,0,0],[6,6,6]],[1,1,1]),([[1,0,2],[5,6,4]],[3,3,3]),([[0,1,2],[6,5,4],[3,3,3]],[3,3,3]))]
T_CASES=[[n,e,s,t,k] for n,e,s,t,k in ((6,[[0,1,5],[1,2,3],[3,4,4],[4,5,1],[1,4,2]],0,3,1),(1,[],0,0,0),(2,[],0,1,1),(2,[[0,1,5]],0,1,0),(2,[[0,1,5]],0,1,1),(3,[[0,1,2],[1,2,4]],0,2,0),(3,[[0,1,2],[1,2,4]],0,2,1),(4,[[0,1,2],[1,2,2],[2,3,2],[3,0,2]],0,0,0),(4,[[0,1,10],[1,3,1],[0,2,5],[2,3,5]],0,3,0),(3,[[0,1,3],[1,2,7],[0,2,10]],0,2,1),(5,[[0,1,1],[1,2,9],[2,4,1],[0,3,5],[3,4,5]],0,4,1),(3,[[0,1,4]],0,2,2),(4,[[0,1,8],[1,2,6],[2,3,4]],0,3,2),(3,[[0,1,1],[1,2,1]],0,2,0),(5,[[0,1,7],[1,4,7],[0,2,2],[2,3,2],[3,4,9]],0,4,1))]
W_CASES=[[c,q] for c,q in ((['hello wor','ld hello'],['hello','world','wor']),(['a-b'],['a-b','a','b']),(['a-','b'],['a-b']),(['a--b'],['a','b','a--b']),(['one,two'],['one','two']),(['abc123def'],['abc','def']),([' hi '],['hi']),(['x-y z'],['x-y','z']),(['a_b'],['a','b']),(['foo','-bar'],['foo-bar']),(['a-!'],['a-','a']),(['a b a'],['a','b']),(['abc'],['abc','']),(['a1b2c'],['a','b','c']),(['well-formed!well'],['well-formed','well']))]
D_CASES=[[[*v]] for v in ([3,6,2],[4,2,8,3],[7,5,9],[1],[2,4],[6,10,15],[5,25,10],[8,12,18],[3,9,27],[2,3,6,12],[11,22,33],[4,6,9],[16,8,4,2],[5,7,35],[10,100,25,50])]
A_CASES=[[n,p,r] for n,p,r in ((2,[8,3],[[0,1,1,2]]),(1,[5],[]),(2,[1,10],[]),(3,[9,4,6],[[0,1,1,3],[1,2,4,2]]),(3,[10,11,1],[[0,2,1,3],[1,2,3,4],[0,1,5,2]]),(2,[10,1],[[0,1,2,1]]),(3,[8,7,2],[[0,1,1,2],[1,2,1,3]]),(4,[20,15,10,5],[[0,1,2,2],[1,2,2,2],[2,3,2,2]]),(3,[5,100,1],[[0,1,1,5],[1,2,1,1]]),(3,[30,2,30],[[0,1,3,2],[1,2,3,2]]),(4,[9,8,7,6],[]),(3,[50,40,1],[[0,1,2,10],[0,2,8,1],[1,2,2,1]]),(2,[100,1],[[0,1,10,3]]),(4,[1,20,20,20],[[0,1,1,2],[1,2,1,2],[2,3,1,2]]),(3,[12,6,3],[[0,1,2,3],[1,2,2,4],[0,2,10,1]]))]

BATCH={
3923:entry('minimum_point_generation',[('points','list[list[int]]'),('target','list[int]')],'int',['arrays','breadth-first search','geometry'],['points contains 1–20 distinct 3D integer points with coordinates 0–6; target has the same bounds.','Each generation simultaneously adds coordinate-wise floored midpoints of every pair of distinct known points.','Return the first generation containing target, or -1 when closure stops growing.'],[([[[0,0,0],[6,6,6]],[3,3,3]],'The two initial points produce target [3,3,3] in generation one.'),([[[0,0,0],[5,5,5]],[1,1,1]],'Generation one adds [2,2,2], which pairs with zero to add target in generation two.')],G_CASES,GENERATIONS,[GENERATIONS.replace('+values[j][axis])//2','+values[j][axis]+1)//2'),GENERATIONS.replace('generation+=1','generation+=2')],['Rounds every midpoint coordinate upward instead of downward.','Advances the reported generation by two each round.'],generation_oracle,random_generation,lesson('The coordinate bounds limit the closure to at most 343 distinct points.','Maintain all known points and generate every pair midpoint in synchronous rounds.','Remove points already known; if no new point appears, the target is impossible.','Round batching matches generation semantics, and finite closure guarantees termination.'),'O(P³)','O(P)',6),
3924:entry('minimum_heavy_edge_threshold',[('n','int'),('edges','list[list[int]]'),('source','int'),('target','int'),('k','int')],'int',['graphs','binary search','zero-one BFS'],['Edges are undirected with positive weights; k is nonnegative.','For a threshold, an edge is heavy exactly when its weight is greater than the threshold.','Return the minimum nonnegative threshold allowing a source-target path with at most k heavy edges, or -1.'],[([6,[[0,1,5],[1,2,3],[3,4,4],[4,5,1],[1,4,2]],0,3,1],'Threshold four makes only weight-five edge heavy on path 0-1-4-3.'),([4,[[0,1,2],[1,2,2],[2,3,2],[3,0,2]],0,0,0],'Source equals target, so threshold zero suffices without traversing edges.')],T_CASES,THRESHOLD,[THRESHOLD.replace('weight>bound','weight>=bound'),THRESHOLD.replace('distance[target]<=k','distance[target]<k')],['Treats edges equal to the threshold as heavy.','Requires strictly fewer than k heavy edges instead of at most k.'],threshold_oracle,random_threshold,lesson('Feasibility is monotone as the threshold increases.','For a fixed threshold, assign light edges cost zero and heavy edges cost one, then use 0-1 BFS for the fewest heavy edges.','Binary-search the sorted distinct edge weights plus zero.','The first feasible candidate is minimal because feasibility changes only when an edge weight crosses the threshold.'),'O((n+e)log e)','O(n+e)',8),
3926:entry('count_joined_words',[('chunks','list[str]'),('queries','list[str]')],'list[int]',['strings','parsing','hash maps'],['Concatenate chunks without separators.','A hyphen belongs to a word only when both adjacent original characters are lowercase letters; lowercase letters and joiner hyphens form maximal words.','Every other character separates words; return occurrence counts for each query.'],[([['hello wor','ld hello'],['hello','world','wor']],'Concatenation forms words hello, world, hello, producing [2,1,0].'),([['a-','b'],['a-b']],'The chunk boundary does not matter: the hyphen lies between lowercase letters, so a-b occurs once.')],W_CASES,WORDS,[WORDS.replace("text=''.join(chunks)","text=' '.join(chunks)"),WORDS.replace("text[i-1].islower() and text[i+1].islower()","(text[i-1].islower() or text[i+1].islower())")],['Inserts separators between chunks instead of concatenating them directly.','Treats a hyphen as a joiner when only one adjacent character is lowercase.'],words_oracle,random_words,lesson('Chunk boundaries disappear before lexical analysis.','Scan the joined text, treating lowercase letters and only two-sided letter hyphens as word characters.','Flush the current maximal token at every other character and count tokens.','Local neighbor checks exactly identify joiner hyphens, while flushing produces maximal words without overlap.'),'O(total characters)','O(total characters)',5),
3927:entry('minimum_divisible_replacement_sum',[('nums','list[int]')],'int',['arrays','number theory','sieve'],['nums is nonempty and contains positive values up to 100,000.','A value may be replaced by another currently present value that divides it.','Return the minimum sum after any number of replacements.'],[([[3,6,2]],'Six can become two; neither three nor two can decrease, producing sum seven.'),([[4,2,8,3]],'Four and eight become two while three remains, producing [2,2,2,3] with sum nine.')],D_CASES,DIVISIBLE,[DIVISIBLE.replace('range(divisor,maximum+1,divisor)','range(divisor+1,maximum+1,divisor)'),DIVISIBLE.replace('min(best[multiple],divisor)','max(best[multiple],divisor)')],['Starts one past each divisor, updating nonmultiples instead of its multiples.','Keeps the larger candidate divisor instead of the smallest.'],divisible_oracle,random_divisible,lesson('Operations never introduce a value outside the initial value set.','Each original value can independently reach the smallest initially present divisor of that value.','Sieve every present divisor across its multiples, recording the minimum.','Keeping a divisor occurrence unchanged makes it permanently available, so all independent minima are simultaneously attainable.'),'O(M log M+n)','O(M)',6),
3928:entry('minimum_apple_costs',[('n','int'),('prices','list[int]'),('roads','list[list[int]]')],'list[int]',['graphs','dijkstra','shortest paths'],['Each road [u,v,cost,tax] is bidirectional.','Travel empty pays cost; returning with apples pays cost×tax, and the two routes may differ.','For every starting shop, minimize outbound travel plus apple price plus loaded return travel.'],[([2,[8,3],[[0,1,1,2]]],'From shop zero, buying at one costs 1+3+2=6; shop one buys locally for three.'),([3,[10,11,1],[[0,2,1,3],[1,2,3,4],[0,1,5,2]]],'Shop zero reaches shop two empty for one and returns for three, totaling five; local choices remain best for shops one and two.')],A_CASES,APPLES,[APPLES.replace('cost*tax','cost'),APPLES.replace('outward[shop]+returning[shop]','2*outward[shop]')],['Charges the unloaded road cost on the return trip and ignores tax.','Forces the return route to have the same metric as outbound travel.'],apples_oracle,random_apples,lesson('Outbound and loaded return travel define two different shortest-path metrics.','From each start, run Dijkstra once using cost and once using cost×tax.','For every buying shop j, combine empty distance, prices[j], and loaded distance, taking the minimum.','Shortest routes in the two phases are independent, so separately minimizing each phase for a fixed j is necessary and sufficient.'),'O(n e log n)','O(n+e)',8),
}
