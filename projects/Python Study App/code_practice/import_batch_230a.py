"""Weighted medians, parity swaps, triangle area, prime gaps, and subtree XOR ranks."""
from collections import deque
from itertools import combinations, permutations

from .import_batch_055 import entry


def median_oracle(args):
    n, edges, queries = args; graph = [[] for _ in range(n)]
    for u, v, weight in edges: graph[u].append((v, weight)); graph[v].append((u, weight))
    answer = []
    for source, target in queries:
        parent = {source: (-1, 0)}; queue = [source]
        for node in queue:
            if node == target: break
            for nxt, weight in graph[node]:
                if nxt not in parent: parent[nxt] = (node, weight); queue.append(nxt)
        path = []; node = target
        while node != source:
            previous, weight = parent[node]; path.append((node, weight)); node = previous
        path.reverse(); total = sum(weight for _, weight in path); traveled = 0; result = source
        for node, weight in path:
            traveled += weight; result = node
            if 2 * traveled >= total: break
        answer.append(result)
    return answer


def random_median(rng):
    n = rng.randint(2, 11); edges = [[rng.randrange(node), node, rng.randint(1, 20)] for node in range(1, n)]; rng.shuffle(edges)
    return [n, edges, [[rng.randrange(n), rng.randrange(n)] for _ in range(rng.randint(1, 9))]]


def parity_oracle(args):
    nums = tuple(args[0]); queue = deque([(nums, 0)]); seen = {nums}
    while queue:
        state, moves = queue.popleft()
        if all((state[i] ^ state[i + 1]) & 1 for i in range(len(state) - 1)): return moves
        for index in range(len(state) - 1):
            following = list(state); following[index], following[index + 1] = following[index + 1], following[index]; following = tuple(following)
            if following not in seen: seen.add(following); queue.append((following, moves + 1))
    return -1


def random_parity(rng): return [rng.sample(range(1, 60), rng.randint(1, 8))]


def triangle_oracle(args):
    best = -1
    for first, second, third in combinations(args[0], 3):
        if not (first[0] == second[0] or first[0] == third[0] or second[0] == third[0] or first[1] == second[1] or first[1] == third[1] or second[1] == third[1]): continue
        area = abs((second[0] - first[0]) * (third[1] - first[1]) - (second[1] - first[1]) * (third[0] - first[0]))
        if area: best = max(best, area)
    return best


def random_triangle(rng):
    count = rng.randint(1, 10); points = rng.sample([(x, y) for x in range(1, 8) for y in range(1, 8)], count); return [[list(point) for point in points]]


def _prime(value):
    if value < 2: return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0: return False
        divisor += 1
    return True


def prime_gap_oracle(args):
    nums, k = args; answer = 0
    for left in range(len(nums)):
        primes = []
        for right in range(left, len(nums)):
            if _prime(nums[right]): primes.append(nums[right])
            if len(primes) >= 2 and max(primes) - min(primes) <= k: answer += 1
    return answer


def random_prime_gap(rng):
    nums = [rng.randint(1, 50) for _ in range(rng.randint(1, 14))]; return [nums, rng.randint(0, 15)]


def xor_oracle(args):
    par, vals, queries = args; n = len(vals); children = [[] for _ in range(n)]; path_xor = vals[:]
    for node in range(1, n): children[par[node]].append(node)
    stack = [0]
    while stack:
        node = stack.pop()
        for child in children[node]: path_xor[child] ^= path_xor[node]; stack.append(child)
    answer = []
    for root, k in queries:
        nodes = []; stack = [root]
        while stack:
            node = stack.pop(); nodes.append(node); stack.extend(children[node])
        values = sorted({path_xor[node] for node in nodes}); answer.append(values[k - 1] if k <= len(values) else -1)
    return answer


def random_xor(rng):
    n = rng.randint(1, 12); par = [-1] + [rng.randrange(node) for node in range(1, n)]; vals = [rng.randint(0, 63) for _ in range(n)]
    return [par, vals, [[rng.randrange(n), rng.randint(1, n)] for _ in range(rng.randint(1, 10))]]


MEDIAN = '''def weighted_median_nodes(n,edges,queries):
    graph=[[] for _ in range(n)]
    for u,v,weight in edges:graph[u].append((v,weight));graph[v].append((u,weight))
    parent=[-1]*n;parent[0]=0;depth=[0]*n;distance=[0]*n;order=[0]
    for node in order:
        for nxt,weight in graph[node]:
            if parent[nxt]<0:parent[nxt]=node;depth[nxt]=depth[node]+1;distance[nxt]=distance[node]+weight;order.append(nxt)
    levels=[parent]
    for _ in range(1,n.bit_length()):levels.append([levels[-1][levels[-1][node]] for node in range(n)])
    def lca(first,second):
        if depth[first]<depth[second]:first,second=second,first
        difference=depth[first]-depth[second]
        for bit in range(len(levels)):
            if difference>>bit&1:first=levels[bit][first]
        if first==second:return first
        for bit in range(len(levels)-1,-1,-1):
            if levels[bit][first]!=levels[bit][second]:first=levels[bit][first];second=levels[bit][second]
        return parent[first]
    answer=[]
    for first,second in queries:
        if first==second:answer.append(first);continue
        middle=lca(first,second);up_weight=distance[first]-distance[middle];total=up_weight+distance[second]-distance[middle]
        if 2*up_weight>=total:
            node=first;traveled=0
            for bit in range(len(levels)-1,-1,-1):
                ancestor=levels[bit][node]
                if depth[ancestor]>=depth[middle]:
                    step=distance[node]-distance[ancestor]
                    if 2*(traveled+step)<total:traveled+=step;node=ancestor
            answer.append(parent[node])
        else:
            node=second
            for bit in range(len(levels)-1,-1,-1):
                ancestor=levels[bit][node]
                if depth[ancestor]>=depth[middle] and 2*(up_weight+distance[ancestor]-distance[middle])>=total:node=ancestor
            answer.append(node)
    return answer
'''


PARITY = '''def minimum_alternating_parity_swaps(nums):
    positions=[[],[]]
    for index,value in enumerate(nums):positions[value&1].append(index)
    if abs(len(positions[0])-len(positions[1]))>1:return -1
    def cost(parity):return sum(abs(actual-target) for actual,target in zip(positions[parity],range(0,len(nums),2)))
    if len(positions[0])>len(positions[1]):return cost(0)
    if len(positions[1])>len(positions[0]):return cost(1)
    return min(cost(0),cost(1))
'''


TRIANGLE = '''def maximum_axis_parallel_triangle_area(coords):
    def evaluate(swapped):
        groups={};low=float('inf');high=-float('inf')
        for first,second in coords:
            x,y=(second,first) if swapped else (first,second);low=min(low,x);high=max(high,x)
            if x not in groups:groups[x]=[y,y]
            else:groups[x][0]=min(groups[x][0],y);groups[x][1]=max(groups[x][1],y)
        answer=0
        for x,(bottom,top) in groups.items():answer=max(answer,(top-bottom)*max(x-low,high-x))
        return answer
    answer=max(evaluate(False),evaluate(True))
    return answer if answer else -1
'''


PRIME_GAP = '''def count_prime_gap_balanced_subarrays(nums,k):
    from collections import deque
    limit=max(nums,default=1);prime=bytearray(b'\\x01')*(limit+1)
    if limit>=0:prime[0]=0
    if limit>=1:prime[1]=0
    for value in range(2,int(limit**0.5)+1):
        if prime[value]:prime[value*value:limit+1:value]=b'\\x00'*(((limit-value*value)//value)+1)
    positions=[];values=[]
    for index,value in enumerate(nums):
        if prime[value]:positions.append(index);values.append(value)
    if len(positions)<2:return 0
    start_ways=[positions[0]+1]+[positions[i]-positions[i-1] for i in range(1,len(positions))]
    prefix=[0]
    for ways in start_ways:prefix.append(prefix[-1]+ways)
    maximum=deque();minimum=deque();left=0;answer=0
    for right,value in enumerate(values):
        while maximum and values[maximum[-1]]<=value:maximum.pop()
        while minimum and values[minimum[-1]]>=value:minimum.pop()
        maximum.append(right);minimum.append(right)
        while values[maximum[0]]-values[minimum[0]]>k:
            if maximum[0]==left:maximum.popleft()
            if minimum[0]==left:minimum.popleft()
            left+=1
        if right>left:
            right_ways=(positions[right+1] if right+1<len(positions) else len(nums))-positions[right]
            answer+=(prefix[right]-prefix[left])*right_ways
    return answer
'''


XOR = '''def kth_subtree_path_xor(par,vals,queries):
    n=len(vals);children=[[] for _ in range(n)]
    for node in range(1,n):children[par[node]].append(node)
    path_xor=vals[:];tin=[0]*n;tout=[0]*n;euler=[];stack=[(0,0)]
    while stack:
        node,state=stack.pop()
        if state==0:
            tin[node]=len(euler);euler.append(node);stack.append((node,1))
            for child in reversed(children[node]):path_xor[child]^=path_xor[node];stack.append((child,0))
        else:tout[node]=len(euler)-1
    block=max(1,int(n**0.5));ordered=[]
    for index,(node,k) in enumerate(queries):ordered.append((tin[node],tout[node],k,index))
    ordered.sort(key=lambda item:(item[0]//block,item[1] if item[0]//block%2==0 else -item[1]))
    limit=1
    while limit<=max(path_xor,default=0):limit*=2
    value_block=max(1,int(limit**0.5));frequencies=[0]*limit;buckets=[0]*((limit+value_block-1)//value_block);distinct=0;left=0;right=-1;answer=[-1]*len(queries)
    def change(position,delta):
        nonlocal distinct
        value=path_xor[euler[position]]
        if delta==1:
            if frequencies[value]==0:buckets[value//value_block]+=1;distinct+=1
            frequencies[value]+=1
        else:
            frequencies[value]-=1
            if frequencies[value]==0:buckets[value//value_block]-=1;distinct-=1
    def kth(k):
        if k>distinct:return -1
        bucket=0
        while k>buckets[bucket]:k-=buckets[bucket];bucket+=1
        value=bucket*value_block
        while value<min(limit,(bucket+1)*value_block):
            if frequencies[value]:
                k-=1
                if k==0:return value
            value+=1
        return -1
    for query_left,query_right,k,index in ordered:
        while left>query_left:left-=1;change(left,1)
        while right<query_right:right+=1;change(right,1)
        while left<query_left:change(left,-1);left+=1
        while right>query_right:change(right,-1);right-=1
        answer[index]=kth(k)
    return answer
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]


MEDIAN_CASES=[[n,edges,queries] for n,edges,queries in [(2,[[0,1,1]],[[0,0],[0,1],[1,0]]),(3,[[0,1,2],[0,2,4]],[[0,1],[2,0],[1,2]]),(3,[[0,1,5],[1,2,5]],[[0,2],[2,0]]),(4,[[0,1,1],[1,2,2],[2,3,3]],[[0,3],[3,0],[1,3]]),(4,[[0,1,10],[0,2,1],[0,3,1]],[[1,2],[2,1],[2,3]]),(5,[[0,1,2],[0,2,5],[1,3,1],[2,4,3]],[[3,4],[1,2]]),(5,[[0,1,3],[1,2,4],[1,3,5],[3,4,6]],[[2,4],[4,2]]),(6,[[0,1,1],[1,2,1],[2,3,1],[3,4,1],[4,5,1]],[[0,5],[5,0]]),(6,[[0,1,8],[0,2,2],[2,3,3],[2,4,4],[4,5,5]],[[1,5],[3,5]]),(7,[[0,1,2],[0,2,2],[1,3,7],[1,4,1],[2,5,5],[2,6,3]],[[3,6],[4,5]]),(4,[[0,1,2],[1,2,2],[1,3,2]],[[2,3],[3,2]]),(5,[[0,1,9],[1,2,1],[2,3,1],[3,4,1]],[[4,0],[0,4]]),(5,[[0,1,1],[0,2,10],[2,3,1],[3,4,1]],[[1,4],[4,1]]),(6,[[0,1,4],[1,2,6],[1,3,8],[3,4,2],[3,5,10]],[[2,5],[4,2]])]]
PARITY_CASES=[[[*nums]] for nums in [[1],[2],[1,2],[2,1],[2,4],[2,4,6,5,7],[2,4,5,7],[1,2,3],[4,5,6,8],[1,3,2,4],[2,6,1,3,4],[9,2,7,4,5,6],[8,3,6,1,4,5],[10,2,3,5,7]]]
TRIANGLE_CASES=[[points] for points in [[[1,1]],[[1,1],[2,2]],[[1,1],[2,2],[3,3]],[[1,1],[1,2],[3,2],[3,3]],[[1,1],[1,4],[5,2]],[[1,1],[4,1],[2,5]],[[1,1],[1,4],[1,7]],[[1,1],[2,1],[3,1]],[[1,1],[1,5],[6,3],[6,8]],[[2,2],[2,6],[5,4]],[[1,3],[4,3],[2,8],[2,1]],[[5,1],[5,10],[1,4],[9,7]],[[1,1],[3,1],[1,4]],[[2,5],[7,5],[4,1],[4,9]]]]
PRIME_CASES=[[nums,k] for nums,k in [([1],0),([2],0),([2,3],0),([1,2,3],1),([2,3,5,7],3),([4,6,8],10),([2,4,3],1),([5,1,1,7],2),([11,13,17],6),([2,2,2],0),([1,2,4,6,3,1],1),([7,4,5,9,11],4),([3,10,13,2],10),([17,1,19,1,23],4)]]
XOR_CASES=[[par,vals,queries] for par,vals,queries in [([-1],[0],[[0,1],[0,2]]),([-1,0],[1,2],[[0,1],[0,2],[1,1]]),([-1,0,0],[1,1,1],[[0,1],[0,2],[0,3]]),([-1,0,1],[5,2,7],[[0,1],[1,2],[1,3],[2,1]]),([-1,0,0,1],[1,2,3,4],[[0,2],[1,1]]),([-1,0,1,2],[7,7,7,7],[[0,1],[0,3],[2,2]]),([-1,0,0,0],[0,1,2,3],[[0,4],[1,1]]),([-1,0,1,1,2],[3,5,6,7,8],[[1,2],[2,2]]),([-1,0,0,2,2],[10,4,6,4,6],[[0,3],[2,2]]),([-1,0,1,2,3,4],[1,2,4,8,16,32],[[0,4],[3,2]]),([-1,0,0,1,1,2,2],[5,1,1,2,2,3,3],[[0,5],[1,3],[2,3]]),([-1,0,1,1],[8,4,2,1],[[1,1],[1,3]]),([-1,0,0,1,2],[15,7,3,1,2],[[0,2],[2,2]]),([-1,0,1,0,3,3],[9,5,12,7,3,10],[[0,4],[3,3]])]]


BATCH={
3585:entry('weighted_median_nodes',[('n','int'),('edges','list[list[int]]'),('queries','list[list[int]]')],'list[int]',['trees','lowest common ancestor','binary lifting'],['The positive-weight tree has up to 100,000 nodes rooted at zero.','For each ordered pair u,v, walk from u toward v.','Return the first node whose accumulated weight is at least half the total path weight.'],[([2,[[0,1,7]],[[1,0],[0,1]]],'The sole edge crosses halfway in either direction, so each answer is the destination.'),([5,[[0,1,2],[0,2,5],[1,3,1],[2,4,3]],[[3,4],[1,2]]],'Both weighted paths first cross their halfway point at node two.')],MEDIAN_CASES,MEDIAN,[MEDIAN.replace('2*(traveled+step)<total','2*(traveled+step)<=total'),MEDIAN.replace('for first,second in queries:','for first,second in queries:\n        first,second=second,first')],['Jumps across a node exactly at halfway and returns the following node.','Reverses every ordered query even though the weighted median depends on traversal direction.'],median_oracle,random_median,lesson('The answer lies either on the upward u-to-LCA segment or the downward LCA-to-v segment, selected by weighted distance.','Preprocess root distances and ancestors, then binary-lift to the boundary immediately before or at the half-weight threshold.','Find LCA and total weight; on the u side jump while still below half, otherwise lift from v to the highest descendant already at or beyond half.','Positive weights make accumulated path weight strictly increasing, so binary lifting locates the unique first threshold-crossing node.'),'O((n+queries) log n)','O(n log n)',8),
3587:entry('minimum_alternating_parity_swaps',[('nums','list[int]')],'int',['arrays','greedy','adjacent swaps'],['nums contains up to 100,000 distinct positive integers.','Only adjacent swaps are allowed, and adjacent parities must alternate in the result.','Return the minimum swaps, or -1 when parity counts differ by more than one.'],[([[2,4,6,5,7]],'Moving the odd values into alternating positions costs three adjacent swaps.'),([[2,4,5,7]],'One swap produces the alternating arrangement [2,5,4,7].')],PARITY_CASES,PARITY,[PARITY.replace('return min(cost(0),cost(1))','return cost(0)'),PARITY.replace('sum(abs(actual-target)','sum((actual-target)')],['When counts tie, considers only arrangements beginning with even and can miss the cheaper odd-first arrangement.','Uses signed displacement, allowing left and right movements to cancel instead of counting every adjacent swap.'],parity_oracle,random_parity,lesson('Stable ordering within each parity is optimal because crossing equal-parity elements only adds swaps.','Match parity positions in order to the alternating slots for each feasible starting parity.','Reject count imbalance; sum absolute position differences to slots 0,2,4,... and minimize when both starts are possible.','Each unit of displacement corresponds to one crossing with the opposite parity, and ordered matching minimizes total displacement without unnecessary same-parity crossings.'),'O(n)','O(n)',5),
3588:entry('maximum_axis_parallel_triangle_area',[('coords','list[list[int]]')],'int',['geometry','hash maps','extrema'],['coords has up to 100,000 distinct points with positive coordinates.','Choose a nonzero-area triangle having a horizontal or vertical side.','Return twice its maximum area, or -1 when none exists.'],[([[[1,1],[1,2],[3,2],[3,3]]],'A vertical base of length one and horizontal height two gives doubled area two.'),([[[1,1],[2,2],[3,3]]],'No pair shares an x or y coordinate, so no qualifying triangle exists.')],TRIANGLE_CASES,TRIANGLE,[TRIANGLE.replace('max(evaluate(False),evaluate(True))','evaluate(False)'),TRIANGLE.replace('max(x-low,high-x)','min(x-low,high-x)')],['Checks only vertical parallel sides and misses triangles whose qualifying side is horizontal.','Uses the nearer global x extreme instead of the farther one, reducing the possible height.'],triangle_oracle,random_triangle,lesson('For a vertical base at x, the longest base uses extreme y values and the greatest height uses the farther global x extreme.','Group y extrema by x, combine with global x extrema, then swap coordinate roles for horizontal bases.','For every x compute (maxY-minY)*max(x-minX,maxX-x); repeat with x and y exchanged.','Base and perpendicular height independently increase area, so replacing either by its available extreme cannot worsen a qualifying triangle.'),'O(n)','O(n)',5),
3589:entry('count_prime_gap_balanced_subarrays',[('nums','list[int]'),('k','int')],'int',['arrays','sliding windows','monotonic queues'],['nums has up to 50,000 values, each at most 50,000.','A counted subarray contains at least two prime values.','The maximum prime minus minimum prime in the subarray must be at most k.'],[([[1,2,3],1],'Both [2,3] and [1,2,3] contain the two primes with gap one.'),([[2,3,5,7],3],'Exactly four subarrays contain at least two primes whose value gap is at most three.')],PRIME_CASES,PRIME_GAP,[PRIME_GAP.replace('prefix[right]-prefix[left]','prefix[right+1]-prefix[left]'),PRIME_GAP.replace('>k','>=k')],['Includes the current prime as a possible first prime, thereby counting subarrays containing only one prime.','Rejects prime ranges whose gap equals k even though equality is allowed.'],prime_gap_oracle,random_prime_gap,lesson('Nonprime elements only multiply boundary choices; validity depends on consecutive prime occurrences and their value range.','Compress prime positions, maintain a valid prime-value window with monotonic deques, and weight each first/last-prime pair by available starts and ends.','For each right prime, shrink until max-min<=k; sum start gaps for eligible earlier primes and multiply by positions before the next prime.','Every subarray has unique first and last included primes, and the boundary factors count exactly all extensions that include neither neighboring prime.'),'O(n+V log log V)','O(n+V)',5),
3590:entry('kth_subtree_path_xor',[('par','list[int]'),('vals','list[int]'),('queries','list[list[int]]')],'list[int]',['trees','Mo algorithm','square root decomposition'],['The rooted tree has up to 50,000 nodes and values at most 100,000.','For each subtree, consider distinct root-to-node XOR values.','Return the kth smallest distinct value, or -1 when fewer than k exist.'],[([[-1,0,0],[1,1,1],[[0,1],[0,2],[0,3]]],'The root subtree has distinct XOR values zero and one, so the answers are 0, 1, and -1.'),([[-1,0,1],[5,2,7],[[0,1],[1,2],[1,3],[2,1]]],'The subtree distinct sets are [0,5,7], [0,7], and [0], producing the stated ranks.')],XOR_CASES,XOR,[XOR.replace('if frequencies[value]==0:buckets[value//value_block]+=1;distinct+=1','buckets[value//value_block]+=1;distinct+=1'),XOR.replace('path_xor[child]^=path_xor[node];','')],['Counts repeated XOR values as separate ranks instead of maintaining distinct presence.','Uses each node value alone instead of the XOR accumulated from the root path.'],xor_oracle,random_xor,lesson('Euler preorder turns every subtree into one array interval of root-path XOR values.','Process interval queries with Mo ordering, maintaining value frequencies, distinct-presence buckets, and kth lookup by bucket scan.','Compute path XORs and Euler bounds; add/remove interval endpoints; locate kth distinct by skipping bucket counts then scanning one value bucket.','The active Mo interval equals exactly the queried subtree, frequencies collapse duplicates, and ordered value buckets return the required distinct rank.'),'O((n+queries)*sqrt(n) + queries*sqrt(V))','O(n+V)',8),
}
