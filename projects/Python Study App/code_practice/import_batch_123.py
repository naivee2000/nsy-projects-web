"""First slice of workbook batch 123."""

from collections import Counter, deque

from .import_batch_055 import entry


def top_oracle(args):
    nums, moves = args
    states = {(tuple(nums), ())}
    for _ in range(moves):
        updated = set()
        for pile, removed in states:
            if pile:
                updated.add((pile[1:], tuple(sorted((*removed, pile[0])))))
            for index, value in enumerate(removed):
                remaining = removed[:index] + removed[index + 1 :]
                updated.add(((value, *pile), remaining))
        states = updated
    return max((pile[0] for pile, _ in states if pile), default=-1)


def random_top(rng):
    return [[rng.randint(0, 20) for _ in range(rng.randint(1, 6))], rng.randint(0, 7)]


def weighted_oracle(args):
    n, edges, first, second, destination = args
    infinity = 10**30
    distance = [[infinity] * n for _ in range(n)]
    for node in range(n):
        distance[node][node] = 0
    for left, right, weight in edges:
        distance[left][right] = min(distance[left][right], weight)
    for middle in range(n):
        for left in range(n):
            for right in range(n):
                distance[left][right] = min(distance[left][right], distance[left][middle] + distance[middle][right])
    answer = min(distance[first][node] + distance[second][node] + distance[node][destination] for node in range(n))
    return -1 if answer >= infinity else answer


def random_weighted(rng):
    n = rng.randint(3, 7)
    edges = [[left, right, rng.randint(1, 20)] for left in range(n) for right in range(n) if left != right and rng.randrange(4) == 0]
    first, second, destination = rng.sample(range(n), 3)
    return [n, edges, first, second, destination]


def cycle_oracle(args):
    n, edges = args
    graph = [[] for _ in range(n)]
    for left, right in edges:
        graph[left].append(right)
        graph[right].append(left)
    cycle = set()
    for left, right in edges:
        seen = {left}
        queue = deque([left])
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if {node, neighbor} == {left, right}:
                    continue
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        if right in seen:
            cycle.update((left, right))
    distance = [-1] * n
    queue = deque(cycle)
    for node in cycle:
        distance[node] = 0
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if distance[neighbor] < 0:
                distance[neighbor] = distance[node] + 1
                queue.append(neighbor)
    return distance


def random_cycle(rng):
    n = rng.randint(3, 10)
    cycle_size = rng.randint(3, n)
    edges = [[index, (index + 1) % cycle_size] for index in range(cycle_size)]
    for node in range(cycle_size, n):
        edges.append([node, rng.randrange(node)])
    rng.shuffle(edges)
    return [n, edges]


def pairs_oracle(args):
    return all(count % 2 == 0 for count in Counter(args[0]).values())


def random_pairs(rng):
    return [[rng.randint(1, 10) for _ in range(2 * rng.randint(1, 15))]]


def subsequences(text, pattern):
    return sum(text[left] == pattern[0] and text[right] == pattern[1] for left in range(len(text)) for right in range(left + 1, len(text)))


def subsequence_oracle(args):
    text, pattern = args
    return max(
        subsequences(text[:index] + char + text[index:], pattern)
        for index in range(len(text) + 1)
        for char in pattern
    )


def random_subsequence(rng):
    return ["".join(rng.choice("abcde") for _ in range(rng.randint(1, 18))), "".join(rng.choice("abcde") for _ in range(2))]


TOP = '''\
def maximum_top_after_moves(nums,k):
    if k==0:return nums[0]
    if len(nums)==1:return nums[0] if k%2==0 else -1
    candidates=nums[:min(len(nums),k-1)]
    if k<len(nums):candidates.append(nums[k])
    return max(candidates,default=-1)
'''

WEIGHTED = '''\
def minimum_shared_weighted_subgraph(n,edges,src1,src2,dest):
    import heapq
    graph=[[] for _ in range(n)];reverse=[[] for _ in range(n)]
    for left,right,weight in edges:graph[left].append((right,weight));reverse[right].append((left,weight))
    def shortest(start,adjacency):
        distance=[float('inf')]*n;distance[start]=0;heap=[(0,start)]
        while heap:
            current,node=heapq.heappop(heap)
            if current!=distance[node]:continue
            for neighbor,weight in adjacency[node]:
                candidate=current+weight
                if candidate<distance[neighbor]:distance[neighbor]=candidate;heapq.heappush(heap,(candidate,neighbor))
        return distance
    first=shortest(src1,graph);second=shortest(src2,graph);to_dest=shortest(dest,reverse)
    answer=min(first[node]+second[node]+to_dest[node] for node in range(n))
    return -1 if answer==float('inf') else answer
'''

CYCLE = '''\
def distances_to_unique_cycle(n,edges):
    from collections import deque
    graph=[[] for _ in range(n)];degree=[0]*n
    for left,right in edges:graph[left].append(right);graph[right].append(left);degree[left]+=1;degree[right]+=1
    queue=deque(node for node in range(n) if degree[node]==1)
    while queue:
        node=queue.popleft();degree[node]=0
        for neighbor in graph[node]:
            if degree[neighbor]>0:
                degree[neighbor]-=1
                if degree[neighbor]==1:queue.append(neighbor)
    distance=[-1]*n;queue=deque()
    for node in range(n):
        if degree[node]>0:distance[node]=0;queue.append(node)
    while queue:
        node=queue.popleft()
        for neighbor in graph[node]:
            if distance[neighbor]<0:distance[neighbor]=distance[node]+1;queue.append(neighbor)
    return distance
'''

PAIRS = '''\
def can_divide_into_equal_pairs(nums):
    from collections import Counter
    return all(count%2==0 for count in Counter(nums).values())
'''

SUBSEQUENCE = '''\
def maximum_pattern_subsequences(text,pattern):
    first=seen=pairs=0
    for char in text:
        if char==pattern[1]:pairs+=seen
        if char==pattern[0]:seen+=1
    return pairs+max(seen,text.count(pattern[1]))
'''


BATCH = {
    2202: entry('maximum_top_after_moves',[('nums','list[int]'),('k','int')],'int',['arrays','greedy'],['The first list element is the pile top.','Each of exactly k moves either removes the current top or returns one previously removed value to the top.','Return the greatest achievable top value, or -1 when every exact-k outcome is empty.'],[([[5,2,2,4,0,6],4],'Remove up to three candidates and return five on move four; no larger reachable top exists.'),([[2],1],'The sole value must be removed and nothing can be returned during the same move, leaving an empty pile.')],[[a,k] for a,k in [([1],0),([1],1),([1],2),([5,2],1),([5,2],2),([5,2],3),([5,2,2,4,0,6],4),([1,2,3],0),([1,2,3],1),([1,2,3],2),([1,2,3],3),([9,1,8,2],3),([0,5,4],2),([7],6)]],TOP,[TOP.replace('k-1','k'),TOP.replace('nums[0] if k%2==0 else -1','nums[0] if k%2==1 else -1')],['Includes nums[k-1], which cannot be both removed and restored within k moves.','Reverses the exact-move parity rule for a one-element pile.'],top_oracle,random_top,['After k moves, candidates are values removed during the first k-1 moves or the untouched value at index k.','Handle the one-element parity trap, then inspect exactly those reachable candidates.','For n>1 take max(nums[:k-1]) and also nums[k] when in range; special-case k=0 and n=1.','Any earlier removed value can be restored on the last move, while reaching nums[k] uses all k removals; no other value can be top in exactly k moves.'],'O(min(n,k))','O(min(n,k))',6),
    2203: entry('minimum_shared_weighted_subgraph',[('n','int'),('edges','list[list[int]]'),('src1','int'),('src2','int'),('dest','int')],'int',['graphs','shortest paths','dijkstra'],['The directed graph has nonnegative edge weights and may contain parallel edges.','Choose a subgraph containing paths from both sources to dest; shared suffix edges are paid only once.','Return its minimum total weight, or -1 when no valid subgraph exists.'],[([6,[[0,2,2],[0,5,6],[1,0,3],[1,4,5],[2,1,1],[2,3,3],[2,3,4],[3,4,2],[4,5,1]],0,1,5],'The best paths merge before the destination and their union has total weight nine.'),([3,[[0,1,1]],0,1,2],'Neither source can reach destination two, so return -1.')],[[n,e,a,b,d] for n,e,a,b,d in [(3,[[0,2,5],[1,2,7]],0,1,2),(3,[[0,1,1]],0,1,2),(4,[[0,2,2],[1,2,3],[2,3,4]],0,1,3),(4,[[0,3,10],[1,3,8],[0,2,1],[1,2,1],[2,3,2]],0,1,3),(6,[[0,2,2],[0,5,6],[1,0,3],[1,4,5],[2,1,1],[2,3,3],[2,3,4],[3,4,2],[4,5,1]],0,1,5),(5,[[0,2,1],[1,2,1],[2,4,1],[0,3,5],[1,3,5],[3,4,1]],0,1,4),(3,[[0,2,5],[1,2,5],[0,2,2]],0,1,2),(5,[[0,1,1],[1,4,1],[2,3,1],[3,4,1]],0,2,4),(4,[[0,1,1],[1,2,1],[2,3,1],[0,3,10]],0,1,3),(5,[],0,1,4),(3,[[0,1,2],[1,0,2],[0,2,9],[1,2,3]],0,1,2),(6,[[0,3,1],[1,3,2],[3,4,3],[4,5,4],[2,5,1]],0,1,5),(4,[[0,2,5],[1,2,6],[2,3,1],[1,3,20]],0,1,3),(5,[[0,4,9],[1,4,8],[0,2,2],[1,3,2],[2,4,2],[3,4,2]],0,1,4)]],WEIGHTED,[WEIGHTED.replace('shortest(dest,reverse)','shortest(dest,graph)'),WEIGHTED.replace('first[node]+second[node]+to_dest[node]','first[node]+to_dest[node]')],['Runs destination distances on forward edges instead of reversed edges.','Ignores the second source’s path cost entirely.'],weighted_oracle,random_weighted,['Any optimal pair of paths can be viewed as two prefixes meeting at a node followed by one shared suffix.','Compute distances from each source and distances to dest by running Dijkstra from dest on reversed edges.','Minimize dist1[v]+dist2[v]+to_dest[v] over every possible meeting node.','The formula constructs a valid union for every meeting node, while the first common node of any optimal paths yields a candidate no heavier than that union.'],'O((n+edges) log n)','O(n+edges)',8),
    2204: entry('distances_to_unique_cycle',[('n','int'),('edges','list[list[int]]')],'list[int]',['graphs','breadth first search','topological pruning'],['The connected undirected graph has n nodes and exactly one cycle.','Cycle nodes have distance zero; other nodes need their shortest edge distance to any cycle node.','Return one distance per node in numeric order.'],[([7,[[1,2],[2,4],[4,3],[3,1],[0,1],[5,2],[6,5]]],'Nodes one through four form the cycle; the branches give distances [1,0,0,0,0,1,2].'),([3,[[0,1],[1,2],[2,0]]],'Every node lies on the only cycle, so every distance is zero.')],[[n,e] for n,e in [(3,[[0,1],[1,2],[2,0]]),(4,[[0,1],[1,2],[2,0],[2,3]]),(5,[[0,1],[1,2],[2,0],[0,3],[3,4]]),(5,[[0,1],[1,2],[2,3],[3,0],[1,4]]),(6,[[0,1],[1,2],[2,0],[2,3],[3,4],[4,5]]),(7,[[1,2],[2,4],[4,3],[3,1],[0,1],[5,2],[6,5]]),(6,[[0,1],[1,2],[2,3],[3,0],[0,4],[0,5]]),(8,[[0,1],[1,2],[2,0],[2,3],[3,4],[4,5],[5,6],[6,7]]),(4,[[0,1],[1,2],[2,3],[3,0]]),(7,[[0,1],[1,2],[2,0],[0,3],[0,4],[4,5],[4,6]]),(5,[[0,1],[1,2],[2,0],[1,3],[1,4]]),(6,[[0,1],[1,2],[2,3],[3,1],[0,4],[4,5]]),(9,[[0,1],[1,2],[2,0],[1,3],[3,4],[4,5],[5,6],[6,7],[7,8]]),(5,[[0,1],[1,2],[2,0],[2,3],[2,4]])]],CYCLE,[CYCLE.replace('degree[node]==1','degree[node]==0'),CYCLE.replace('distance[neighbor]=distance[node]+1','distance[neighbor]=distance[node]')],['Starts pruning from zero-degree nodes, so attached trees are incorrectly treated as cycle nodes.','Fails to increase distance when expanding outward from the cycle.'],cycle_oracle,random_cycle,['Repeatedly removing leaves exposes exactly the nodes on the unique cycle.','Prune degree-one nodes, then start a multi-source BFS from every unpruned node.','Mark cycle nodes distance zero and assign each unseen neighbor parent distance plus one.','A unicyclic graph’s non-cycle portion is a forest peeled completely by leaf pruning; multi-source BFS then gives shortest distance to the remaining cycle.'],'O(n)','O(n)',8),
    2206: entry('can_divide_into_equal_pairs',[('nums','list[int]')],'bool',['arrays','counting','hash maps'],['nums has even length.','Every pair must contain two equal values and every element must be used once.','Return true exactly when such a partition exists.'],[([[3,2,3,2,2,2]],'Counts are two threes and four twos, both even, so equal pairs can be formed.'),([[1,2,3,4]],'Every value occurs once, so no equal pairing can use all elements.')],[[x] for x in [[1,1],[1,2],[3,2,3,2,2,2],[1,2,3,4],[5,5,5,5],[1,1,2,2],[1,1,1,2,2,2],[0,0,-1,-1],[7,8,7,8,9,9],[2,2,2,2,3,3],[4,4,5,6],[10,10,20,20,30,30],[1,2,1,2,1,2],[9,9]]],PAIRS,[PAIRS.replace('count%2==0','count>1'),PAIRS.replace('all(','any(')],['Accepts any repeated value count, including odd counts greater than one.','Returns true when just one value has even frequency rather than requiring every value.'],pairs_oracle,random_pairs,['Equal pairing is possible independently for each distinct value.','Every frequency must be even.','Count nums and return all(count % 2 == 0 for count in frequencies).','Even counts can be partitioned into pairs, while any odd count necessarily leaves one unmatched occurrence.'],'O(n)','O(distinct values)',3),
    2207: entry('maximum_pattern_subsequences',[('text','str'),('pattern','str')],'int',['strings','greedy','prefix counts'],['pattern has exactly two lowercase characters, which may be equal.','Insert exactly one occurrence of either pattern character anywhere in text.','Maximize the number of pattern occurrences as length-two subsequences.'],[(['abdcdbc','ac'],'The text already has two ac subsequences; inserting a at the front adds two more, totaling four.'),(['aabb','ab'],'Four ab subsequences already exist; the best insertion adds two, giving six.')],[[t,p] for t,p in [('a','aa'),('b','ab'),('ab','ab'),('ba','ab'),('aaaa','aa'),('abdcdbc','ac'),('aabb','ab'),('xyz','xy'),('ccbb','cb'),('abab','ab'),('bbbb','bb'),('abcabc','ac'),('zzza','za'),('cabca','ca')]],SUBSEQUENCE,[SUBSEQUENCE.replace('pairs+=seen','pairs+=1'),SUBSEQUENCE.replace('max(seen,text.count(pattern[1]))','min(seen,text.count(pattern[1]))')],['Adds one per second-pattern character instead of all preceding first characters.','Chooses the smaller insertion gain rather than the larger one.'],subsequence_oracle,random_subsequence,['Count existing subsequences, then compare the gain from inserting either endpoint character.','A new first character at the front pairs with every existing second; a new second at the end pairs with every existing first.','Scan to count existing ordered pairs and first-character occurrences; add max(first_count,second_count).','Front and end placements maximize the respective insertion’s partners, and insertion does not change any preexisting subsequence.'],'O(n)','O(1)',6),
}
