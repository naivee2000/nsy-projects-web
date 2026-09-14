"""Final group of batch 105: greedy, shortest paths, XOR DP, and strings."""
from itertools import product
from .import_batch_055 import entry


def elements_oracle(args):
    nums, limit, goal = args
    gap = abs(goal - sum(nums))
    count = 0
    while gap > 0:
        gap -= limit
        count += 1
    return count


def restricted_oracle(args):
    n, edges = args
    inf = 10**18
    dist = [[inf] * n for _ in range(n)]
    graph = [[] for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, weight in edges:
        u -= 1
        v -= 1
        dist[u][v] = dist[v][u] = min(dist[u][v], weight)
        graph[u].append(v)
        graph[v].append(u)
    for mid in range(n):
        for left in range(n):
            for right in range(n):
                dist[left][right] = min(dist[left][right], dist[left][mid] + dist[mid][right])
    memo = {}
    def visit(node):
        if node == n - 1:
            return 1
        if node not in memo:
            memo[node] = sum(visit(nxt) for nxt in graph[node] if dist[node][n - 1] > dist[nxt][n - 1]) % 1_000_000_007
        return memo[node]
    return visit(0)


def xor_oracle(args):
    nums, k = args
    groups = [nums[offset::k] for offset in range(k)]
    best = len(nums)
    for prefix in product(range(8), repeat=max(0, k - 1)):
        chosen = list(prefix)
        chosen.append(0 if k == 1 else __import__('functools').reduce(int.__xor__, prefix, 0))
        changes = sum(sum(value != chosen[index] for value in group) for index, group in enumerate(groups))
        best = min(best, changes)
    return best


def garden_oracle(args):
    flowers = args[0]
    best = -10**18
    for mask in range(1 << len(flowers)):
        kept = [value for index, value in enumerate(flowers) if mask >> index & 1]
        if len(kept) >= 2 and kept[0] == kept[-1]:
            best = max(best, sum(kept))
    return best


def swap_oracle(args):
    first, second = args
    if first == second:
        return True
    chars = list(first)
    for left in range(len(chars)):
        for right in range(left, len(chars)):
            chars[left], chars[right] = chars[right], chars[left]
            if ''.join(chars) == second:
                return True
            chars[left], chars[right] = chars[right], chars[left]
    return False


def random_elements(rng):
    limit = rng.randint(1, 20)
    return [[rng.randint(-limit, limit) for _ in range(rng.randint(1, 10))], limit, rng.randint(-100, 100)]


def random_graph(rng):
    n = rng.randint(2, 7)
    edges = [[node, node + 1, rng.randint(1, 9)] for node in range(1, n)]
    present = {(edge[0], edge[1]) for edge in edges}
    for left in range(1, n + 1):
        for right in range(left + 2, n + 1):
            if (left, right) not in present and rng.random() < .3:
                edges.append([left, right, rng.randint(1, 9)])
    return [n, edges]


def random_xor(rng):
    length = rng.randint(1, 9)
    return [[rng.randint(0, 7) for _ in range(length)], rng.randint(1, min(4, length))]


def random_garden(rng):
    length = rng.randint(2, 9)
    flowers = [rng.randint(-6, 8) for _ in range(length)]
    flowers[-1] = flowers[0]
    return [flowers]


def random_swap(rng):
    length = rng.randint(1, 8)
    first = ''.join(rng.choice('abcd') for _ in range(length))
    second = ''.join(rng.choice('abcd') for _ in range(length))
    return [first, second]


ELEMENTS = '''def minimum_elements_for_goal(nums, limit, goal):
 gap=abs(goal-sum(nums))
 return (gap+limit-1)//limit
'''
RESTRICTED = '''def count_restricted_paths(n, edges):
 import heapq
 mod=10**9+7;graph=[[] for _ in range(n+1)]
 for u,v,w in edges:graph[u].append((v,w));graph[v].append((u,w))
 distance=[float('inf')]*(n+1);distance[n]=0;heap=[(0,n)]
 while heap:
  current,node=heapq.heappop(heap)
  if current!=distance[node]:continue
  for neighbor,weight in graph[node]:
   candidate=current+weight
   if candidate<distance[neighbor]:distance[neighbor]=candidate;heapq.heappush(heap,(candidate,neighbor))
 order=sorted(range(1,n+1),key=lambda node:distance[node]);ways=[0]*(n+1);ways[n]=1
 for node in order:
  for neighbor,_ in graph[node]:
   if distance[neighbor]>distance[node]:ways[neighbor]=(ways[neighbor]+ways[node])%mod
 return ways[1]
'''
XOR = '''def minimum_zero_xor_changes(nums, k):
 from collections import Counter
 size=1<<10;cost=[10**9]*size;cost[0]=0
 for offset in range(k):
  group=nums[offset::k];counts=Counter(group);baseline=min(cost)+len(group);next_cost=[baseline]*size
  for xor_value in range(size):
   for value,frequency in counts.items():next_cost[xor_value]=min(next_cost[xor_value],cost[xor_value^value]+len(group)-frequency)
  cost=next_cost
 return cost[0]
'''
GARDEN = '''def maximum_garden_beauty(flowers):
 positive_prefix=0;first={};answer=-10**18
 for value in flowers:
  if value in first:answer=max(answer,positive_prefix-first[value]+2*value)
  else:first[value]=positive_prefix+max(value,0)
  positive_prefix+=max(value,0)
 return answer
'''
SWAP = '''def can_equal_with_one_swap(s1, s2):
 mismatches=[(a,b) for a,b in zip(s1,s2) if a!=b]
 return not mismatches or (len(mismatches)==2 and mismatches[0]==mismatches[1][::-1])
'''


def hints(a, b, c, d):
    return [a, b, c, d]


def E(*args):
    return entry(*args)


BATCH = {
1785: E('minimum_elements_for_goal', [('nums', 'list[int]'), ('limit', 'int'), ('goal', 'int')], 'int', ['arrays', 'greedy'], ['Every existing and added value must have absolute value at most limit.', 'Return the minimum number of added elements needed to make the total equal goal.'], [([[1,-1,1],3,-4], 'The sum must decrease by five; values -3 and -2 achieve it in two additions.'), ([[1,-10,9,1],100,0], 'The current sum is one, so adding -1 reaches zero in one step.')], [[[1,-1,1],3,-4],[[1,-10,9,1],100,0],[[1],1,1],[[1],1,5],[[-5],2,4],[[0],7,-15],[[3,-2,4],3,20],[[10,-10],10,0],[[2,2,2],2,-3],[[-1,-1],1,4],[[5],5,-6],[[1,2,3],4,7],[[4,-2],3,-8],[[100,-50],20,-11]], ELEMENTS, [ELEMENTS.replace('abs(goal-sum(nums))','goal-sum(nums)'), ELEMENTS.replace('gap+limit-1','gap')], ['Fails when the current sum is greater than the goal.', 'Uses floor division and undercounts any non-divisible remaining gap.'], elements_oracle, random_elements, hints('Each added number can close at most limit units of the sum gap.', 'Compute the absolute difference between the current sum and goal.', 'Divide the gap by limit and round upward.', 'No single addition can contribute more than limit toward the gap, while full-limit values plus one remainder always achieve the ceiling.'), 'O(n)', 'O(1)', 5),
1786: E('count_restricted_paths', [('n', 'int'), ('edges', 'list[list[int]]')], 'int', ['graphs', 'shortest-path', 'dynamic-programming', 'heaps'], ['The graph is connected, undirected, weighted, and uses node labels 1 through n.', 'A restricted path must strictly decrease the shortest distance to node n at every step; return its count modulo 1,000,000,007.'], [([5,[[1,2,3],[1,3,3],[2,3,1],[1,4,2],[5,2,2],[3,5,1],[5,4,10]]], 'The valid paths are 1-2-5, 1-2-3-5, and 1-3-5.'), ([7,[[1,3,1],[4,1,2],[7,3,4],[2,5,3],[5,6,1],[6,7,2],[7,5,3],[2,6,4]]], 'Only 1-3-7 decreases the shortest remaining distance at both steps.')], [[2,[[1,2,1]]],[3,[[1,2,1],[2,3,1]]],[3,[[1,2,2],[2,3,2],[1,3,5]]],[4,[[1,2,1],[2,4,4],[1,3,2],[3,4,2]]],[4,[[1,2,5],[2,4,1],[1,3,1],[3,4,5],[2,3,1]]],[5,[[1,2,2],[2,3,2],[3,4,2],[4,5,2],[1,5,20]]],[5,[[1,2,1],[1,3,1],[2,4,1],[3,4,1],[4,5,1]]],[5,[[1,2,3],[2,5,3],[1,3,2],[3,5,4],[1,4,1],[4,5,5]]],[6,[[1,2,1],[2,3,1],[3,6,1],[1,4,2],[4,5,2],[5,6,2]]],[4,[[1,2,1],[2,3,1],[3,4,1],[1,4,3]]],[3,[[1,2,10],[2,3,1],[1,3,2]]],[5,[[1,2,4],[2,5,4],[1,3,2],[3,4,2],[4,5,2],[2,3,1]]],[6,[[1,2,3],[2,6,3],[1,3,2],[3,4,2],[4,6,2],[2,5,1],[5,6,4]]],[2,[[1,2,9]]]], RESTRICTED, [RESTRICTED.replace('distance[neighbor]>distance[node]','distance[neighbor]>=distance[node]'), RESTRICTED.replace('ways[n]=1','ways[1]=1')], ['Allows equal-distance moves, which are forbidden.', 'Seeds the path count at the starting node instead of the destination.'], restricted_oracle, random_graph, hints('First compute every node’s shortest distance to node n.', 'Dijkstra from n gives those distances; they orient every valid step into a decreasing-distance DAG.', 'Process nodes from smaller to larger distance and propagate path counts to larger-distance neighbors.', 'Every restricted path follows the distance order, so dynamic programming counts each path once after Dijkstra fixes the ordering.'), 'O((n+edges) log n)', 'O(n+edges)', 7),
1787: E('minimum_zero_xor_changes', [('nums', 'list[int]'), ('k', 'int')], 'int', ['arrays', 'bit-manipulation', 'dynamic-programming', 'counting'], ['All length-k segments must have XOR zero after changing as few elements as possible.', 'Values are between 0 and 1023; overlapping windows force indices with the same remainder modulo k to share a value.'], [([[1,2,0,3,0],1], 'With k=1 every element must be zero, so the three nonzero values change.'), ([[3,4,5,2,1,7,3,4,7],3], 'Changing one value in each remainder group yields repeating triples whose XOR is zero.')], [[nums,k] for nums,k in [([0],1),([1],1),([1,1],2),([1,2],2),([1,2,3],3),([1,2,4,1,2,5,1,2,6],3),([0,0,0],2),([7,7,7,7],2),([1,2,1,2],2),([1,0,1,0,1],2),([2,3,2,3,2,3],3),([1,2,3,4],4),([6,1,7,6,1,7],3),([3,3,0,3,3,0],3)]], XOR, [XOR.replace('cost[0]=0','cost[1]=0'), XOR.replace('cost[xor_value^value]','cost[xor_value]')], ['Targets total XOR one instead of zero.', 'Ignores how choosing a group value changes the accumulated XOR state.'], xor_oracle, random_xor, hints('All positions with the same index modulo k must become equal.', 'Treat each remainder class as a group and keep the cheapest cost for every possible accumulated XOR.', 'For each group, either choose a value already present or pay to replace the entire group with another value.', 'The 1024 XOR states cover every possible value; group DP minimizes changes, and state zero after all k groups is exactly the required repeating-block XOR.'), 'O(k*1024*(1024+distinct))', 'O(1024+k)', 8),
1788: E('maximum_garden_beauty', [('flowers', 'list[int]')], 'int', ['arrays', 'hash-maps', 'prefix-sums', 'greedy'], ['Remove any flowers while preserving the relative order of those kept.', 'The remaining garden needs at least two flowers with equal first and last values; maximize its total beauty.'], [([[1,2,3,1,2]], 'Keep [2,3,1,2], whose equal endpoints and positive interior sum to eight.'), ([[100,1,1,-3,1]], 'Use the three flowers of value one and discard 100 before the first endpoint and negative three.')], [[[1,2,3,1,2]],[[100,1,1,-3,1]],[[-1,-2,0,-1]],[[1,1]],[[0,0]],[[5,-10,5]],[[2,-1,2,3,2]],[[3,4,-9,4]],[[1,-2,3,-4,1]],[[7,1,2,7]],[[2,2,2]],[[4,-1,5,-1,4]],[[0,5,0]],[[6,-3,2,-4,6]]], GARDEN, [GARDEN.replace('max(value,0)','value'), GARDEN.replace('2*value','value')], ['Forces negative interior flowers to remain instead of removing them.', 'Counts only one of the two required equal endpoints.'], garden_oracle, random_garden, hints('Once equal endpoints are chosen, keep every positive interior flower and remove every negative one.', 'Maintain a prefix sum of positive values and remember the best first occurrence state for each endpoint value.', 'At a repeated value v, combine 2v with the positive contributions strictly between its first useful occurrence and now.', 'The formula includes both required endpoints and exactly all beneficial interior flowers; retaining the earliest prefix baseline maximizes every later match.'), 'O(n)', 'O(n)', 8),
1790: E('can_equal_with_one_swap', [('s1', 'str'), ('s2', 'str')], 'bool', ['strings', 'counting'], ['The strings have equal length and contain lowercase English letters.', 'Return whether zero or one swap of two positions in exactly one string can make the strings equal.'], [(['bank','kanb'], 'The two mismatches cross-match, so swapping the first and last characters makes the strings equal.'), (['attack','defend'], 'There are more than two mismatches, so one swap cannot repair them.')], [[a,b] for a,b in [('bank','kanb'),('attack','defend'),('kelb','kelb'),('a','a'),('a','b'),('ab','ba'),('ab','ab'),('abcd','abdc'),('abcd','badc'),('aa','bb'),('abc','acb'),('aaaa','aaaa'),('abcd','abcc'),('aaab','aaba')]], SWAP, [SWAP.replace('not mismatches or ','not mismatches and '), SWAP.replace("mismatches[0]==mismatches[1][::-1]","len(mismatches)==2")], ['Rejects strings that are already equal.', 'Accepts any two mismatches even when their characters do not cross-match.'], swap_oracle, random_swap, hints('One swap changes either zero or exactly two mismatching positions.', 'Collect the aligned character pairs that differ.', 'Accept no mismatches, or exactly two pairs that are reverses of each other.', 'Reverse mismatch pairs are precisely the two characters exchanged by one swap; every other mismatch count or pairing is impossible.'), 'O(n)', 'O(n)', 3),
}
