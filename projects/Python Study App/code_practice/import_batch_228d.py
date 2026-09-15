"""Weighted tree queries, window repair, prime substrings, intervals, and edge weights."""
from collections import deque
from math import isqrt

from .import_batch_055 import entry


def subtree_oracle(args):
    edges, queries = args; n = len(edges) + 1; graph = [[] for _ in range(n)]; weights = {}
    for u, v, weight in edges:
        graph[u].append(v); graph[v].append(u); weights[tuple(sorted((u, v)))] = weight
    def path(source, target):
        parent = {source: -1}; queue = [source]
        for node in queue:
            if node == target: break
            for nxt in graph[node]:
                if nxt not in parent: parent[nxt] = node; queue.append(nxt)
        result = set(); node = target
        while parent[node] != -1: result.add(tuple(sorted((node, parent[node])))); node = parent[node]
        return result
    return [sum(weights[edge] for edge in path(first, destination) | path(second, destination)) for first, second, destination in queries]


def random_subtree(rng):
    n = rng.randint(3, 11); edges = [[rng.randrange(node), node, rng.randint(1, 20)] for node in range(1, n)]; rng.shuffle(edges)
    queries = [rng.sample(range(n), 3) for _ in range(rng.randint(1, 8))]
    return [edges, queries]


def window_oracle(args):
    nums, k = args; answer = []
    for start in range(len(nums) - k + 1):
        window = nums[start:start + k]; ordered = sorted(window); changed = [i for i, pair in enumerate(zip(window, ordered)) if pair[0] != pair[1]]
        answer.append(0 if not changed else changed[-1] - changed[0] + 1)
    return answer


def random_window(rng):
    nums = [rng.randint(-20, 20) for _ in range(rng.randint(1, 18))]
    return [nums, rng.randint(1, len(nums))]


def prime_oracle(args):
    s = args[0]; values = {int(s[left:right]) for left in range(len(s)) for right in range(left + 1, len(s) + 1)}
    limit = isqrt(max(values, default=0)); sieve = [True] * (limit + 1)
    if limit >= 0: sieve[0] = False
    if limit >= 1: sieve[1] = False
    for value in range(2, isqrt(limit) + 1):
        if sieve[value]:
            for multiple in range(value * value, limit + 1, value): sieve[multiple] = False
    divisors = [value for value in range(2, limit + 1) if sieve[value]]
    primes = [value for value in values if value >= 2 and all(value % divisor for divisor in divisors if divisor * divisor <= value)]
    return sum(sorted(primes)[-3:])


def random_prime(rng): return [''.join(rng.choice('0123456789') for _ in range(rng.randint(1, 7)))]


def substring_oracle(args):
    word = args[0]; n = len(word); best = [0] * (n + 1)
    for end in range(1, n + 1):
        best[end] = best[end - 1]
        for start in range(end - 3):
            if word[start] == word[end - 1]: best[end] = max(best[end], best[start] + 1)
    return best[n]


def random_substrings(rng): return [''.join(rng.choice('abcde') for _ in range(rng.randint(1, 25)))]


def edge_weight_oracle(args):
    edges = args[0]; n = len(edges) + 1; graph = [[] for _ in range(n + 1)]
    for u, v in edges: graph[u].append(v); graph[v].append(u)
    depth = [-1] * (n + 1); depth[1] = 0; queue = [1]
    for node in queue:
        for nxt in graph[node]:
            if depth[nxt] < 0: depth[nxt] = depth[node] + 1; queue.append(nxt)
    distance = max(depth); answer = 0
    for mask in range(1 << distance):
        if sum(1 if mask >> i & 1 else 2 for i in range(distance)) % 2: answer += 1
    return answer % 1_000_000_007


def random_edge_weights(rng):
    n = rng.randint(2, 11); edges = [[rng.randint(1, node - 1), node] for node in range(2, n + 1)]; rng.shuffle(edges)
    return [edges]


SUBTREE = '''def minimum_required_subtree_weights(edges,queries):
    n=len(edges)+1;graph=[[] for _ in range(n)]
    for u,v,weight in edges:graph[u].append((v,weight));graph[v].append((u,weight))
    parent=[-1]*n;parent[0]=0;depth=[0]*n;distance=[0]*n;order=[0]
    for node in order:
        for nxt,weight in graph[node]:
            if parent[nxt]<0:
                parent[nxt]=node;depth[nxt]=depth[node]+1;distance[nxt]=distance[node]+weight;order.append(nxt)
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
    def dist(first,second):return distance[first]+distance[second]-2*distance[lca(first,second)]
    return [(dist(a,b)+dist(a,c)+dist(b,c))//2 for a,b,c in queries]
'''


WINDOW = '''def sliding_window_sort_lengths(nums,k):
    answer=[]
    for start in range(len(nums)-k+1):
        end=start+k;maximum=-float('inf');right=-1
        for index in range(start,end):
            if nums[index]<maximum:right=index
            else:maximum=nums[index]
        if right<0:answer.append(0);continue
        minimum=float('inf');left=end
        for index in range(end-1,start-1,-1):
            if nums[index]>minimum:left=index
            else:minimum=nums[index]
        answer.append(right-left+1)
    return answer
'''


PRIMES = '''def sum_largest_prime_substrings(s):
    def prime(value):
        if value<2:return False
        for divisor in (2,3,5,7,11,13,17,19,23,29,31,37):
            if value%divisor==0:return value==divisor
        odd=value-1;power=0
        while odd%2==0:power+=1;odd//=2
        for base in (2,3,5,7,11):
            if base>=value:continue
            current=pow(base,odd,value)
            if current in (1,value-1):continue
            for _ in range(power-1):
                current=current*current%value
                if current==value-1:break
            else:return False
        return True
    found=set()
    for left in range(len(s)):
        value=0
        for right in range(left,len(s)):
            value=value*10+int(s[right])
            if prime(value):found.add(value)
    return sum(sorted(found)[-3:])
'''


SUBSTRINGS = '''def maximum_nonintersecting_substrings(word):
    answer=0;first={}
    for index,letter in enumerate(word):
        if letter not in first:first[letter]=index
        if index-first[letter]>=3:
            answer+=1;first={}
    return answer
'''


EDGE_WEIGHTS = '''def count_odd_path_edge_weights(edges):
    modulo=1000000007;n=len(edges)+1;graph=[[] for _ in range(n+1)]
    for u,v in edges:graph[u].append(v);graph[v].append(u)
    depth=[-1]*(n+1);depth[1]=0;queue=[1]
    for node in queue:
        for nxt in graph[node]:
            if depth[nxt]<0:depth[nxt]=depth[node]+1;queue.append(nxt)
    return pow(2,max(depth)-1,modulo)
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]


SUBTREE_CASES=[[edges,queries] for edges,queries in [([[0,1,1],[1,2,2]],[[0,1,2]]),([[0,1,4],[0,2,7]],[[1,2,0]]),([[0,1,2],[1,2,3],[2,3,4]],[[0,1,3],[0,2,3]]),([[0,1,5],[0,2,6],[0,3,7]],[[1,2,3]]),([[0,1,1],[1,2,1],[1,3,1],[3,4,1]],[[2,4,0],[0,2,4]]),([[0,1,9],[1,2,8],[1,3,7],[3,4,6],[3,5,5]],[[2,4,5],[0,2,5]]),([[0,1,2],[0,2,3],[2,3,5],[2,4,7],[4,5,11]],[[1,3,5]]),([[0,1,1],[1,2,2],[2,3,3],[3,4,4],[4,5,5]],[[0,2,5]]),([[0,1,10],[0,2,20],[1,3,30],[1,4,40],[2,5,50]],[[3,4,5],[3,5,2]]),([[0,1,3],[1,2,4],[1,3,5],[0,4,6]],[[2,3,4]]),([[0,1,1],[0,2,1],[2,3,1],[2,4,1],[4,5,1]],[[1,3,5],[0,3,4]]),([[0,1,12],[1,2,1],[2,3,12]],[[0,2,3]]),([[0,1,2],[1,2,3],[1,3,4],[3,4,5]],[[0,2,4],[2,3,4]]),([[0,1,4],[1,2,6],[0,3,8],[3,4,10],[3,5,12]],[[2,4,5]])]]
WINDOW_CASES=[[nums,k] for nums,k in [([1],1),([1,2,3],3),([3,2,1],3),([2,1,3],2),([1,3,2,4],2),([4,1,3,2,5],4),([1,1,1],2),([2,1,1],3),([1,2,1],3),([5,4,3,2,1],2),([1,5,3,4,2,6],5),([-1,-3,-2,0],3),([3,1,2,2,4],4),([9,7,8,6,5,10],3)]]
PRIME_CASES=[[s] for s in ['0','1','2','11','101','123','007','313','2222','12234','99991','1000000007','235711','01013']]
SUBSTRING_CASES=[[word] for word in ['a','aaaa','abcda','abcdef','abcdea','aaaaaaa','abcdeafdef','bcdaaaab','abcaefgha','zzzzzzzz','abcdabcd','aabcaabcaa','xyzaxyzbxyz','abcabcabcabc']]
EDGE_WEIGHT_CASES=[[edges] for edges in [[[1,2]],[[1,2],[1,3]],[[1,2],[2,3]],[[1,2],[1,3],[3,4],[3,5]],[[1,2],[2,3],[3,4]],[[1,2],[1,3],[1,4],[1,5]],[[1,2],[2,3],[2,4],[4,5]],[[1,2],[2,3],[3,4],[4,5],[5,6]],[[1,2],[1,3],[2,4],[2,5],[3,6]],[[1,2],[2,3],[1,4],[4,5],[5,6]],[[1,2],[1,3],[3,4],[4,5],[4,6]],[[1,2],[2,3],[2,4],[3,5],[5,6]],[[1,2],[1,3],[1,4],[4,5],[5,6],[6,7]],[[1,2],[2,3],[3,4],[2,5],[5,6],[5,7]]]]


BATCH={
3553:entry('minimum_required_subtree_weights',[('edges','list[list[int]]'),('queries','list[list[int]]')],'list[int]',['trees','lowest common ancestor','binary lifting'],['edges form a weighted tree of up to 100,000 zero-indexed nodes.','Each query contains three pairwise distinct nodes: two sources and one destination.','Return the minimum total weight of a connected subtree containing all three query nodes.'],[([[[0,1,2],[1,2,3],[1,3,5],[1,4,4],[2,5,6]],[[2,3,4],[0,2,5]]],'The two required path unions weigh 12 and 11.'),([[[1,0,8],[0,2,7]],[[0,1,2]]],'Both tree edges are necessary, so the subtree weighs 15.')],SUBTREE_CASES,SUBTREE,[SUBTREE.replace('//2','//3'),SUBTREE.replace('-2*distance[lca(first,second)]','-distance[lca(first,second)]')],['Divides the three pairwise distances by three instead of two.','Subtracts only one root distance in the pairwise distance formula.'],subtree_oracle,random_subtree,lesson('For three tree nodes, the union of their connecting paths counts every selected edge in exactly two of the three pairwise distances.','Preprocess root distances and binary-lifting ancestors, then answer each query with half the sum of its three pairwise distances.','Build parent jump levels; compute LCA-based distances for (a,b), (a,d), and (b,d); add and divide by two.','Unique tree paths make the required subtree their union, and every union edge separates one terminal from the other two, so it appears in exactly two pair distances.'),'O((n+queries) log n)','O(n log n)',8),
3555:entry('sliding_window_sort_lengths',[('nums','list[int]'),('k','int')],'list[int]',['arrays','sliding windows','scanning'],['1 <= k <= len(nums); values may repeat.','For each length-k window, sort one contiguous segment so the entire window becomes nondecreasing.','Return zero for windows already sorted.'],[([[1,3,2,4,5],3],'The windows need segment lengths 2, 2, and 0 respectively.'),([[3,2,1],3],'The entire three-element window must be sorted.')],WINDOW_CASES,WINDOW,[WINDOW.replace('nums[index]<maximum','nums[index]<=maximum'),WINDOW.replace('right-left+1','right-left')],['Treats equal adjacent values as inversions and changes already sorted duplicate windows.','Omits one endpoint when converting boundary indices to a segment length.'],window_oracle,random_window,lesson('The required segment begins at the rightmost value exceeding a later minimum and ends at the left-to-right inversion frontier.','Within each window, scan forward for its last out-of-order index and backward for its first out-of-order index.','Track maximum from the left and minimum from the right; return right-left+1, or zero when no inversion exists.','Everything outside these two boundaries is already ordered relative to the window; sorting inside fixes every remaining inversion and no shorter segment can include both witnesses.'),'O((n-k+1)k)','O(1)',5),
3556:entry('sum_largest_prime_substrings',[('s','str')],'int',['strings','number theory','enumeration'],['s contains 1 to 10 decimal digits.','Convert every nonempty substring to an integer, ignoring leading zeros.','Sum the three largest distinct primes, or every distinct prime when fewer than three exist.'],[(['12234'],'The distinct primes are 2, 3, 23, 223, and 1223; the largest three sum to 1469.'),(['111'],'The only distinct prime substring value is 11.')],PRIME_CASES,PRIMES,[PRIMES.replace('[-3:]','[:]'),PRIMES.replace('if value<2:return False','if value<1:return False')],['Sums every prime substring instead of retaining only the largest three distinct values.','Incorrectly classifies the value one as prime.'],prime_oracle,random_prime,lesson('There are only O(n²) substrings, but repeated numeric values must be deduplicated before selecting the largest three.','Build each substring value incrementally and use deterministic Miller-Rabin to test primality efficiently.','For every start, append digits to a running value, add primes to a set, then sort the set and sum its last three entries.','Incremental construction enumerates every substring once; the set enforces uniqueness, and deterministic witnesses correctly classify all values allowed by the ten-digit limit.'),'O(n² log(value))','O(n²)',5),
3557:entry('maximum_nonintersecting_substrings',[('word','str')],'int',['strings','greedy','interval scheduling'],['word has up to 200,000 lowercase letters.','Choose non-overlapping substrings of length at least four.','Each chosen substring must start and end with the same letter; maximize the count.'],[(['abcdeafdef'],'Choosing abcdea followed by fdef gives two non-intersecting substrings.'),(['bcdaaaab'],'The interval aaaa is valid, but the enclosing whole string overlaps it, so only one can be chosen.')],SUBSTRING_CASES,SUBSTRINGS,[SUBSTRINGS.replace('>=3','>=2'),SUBSTRINGS.replace('answer+=1;first={}','answer+=1')],['Accepts length-three substrings even though four characters are required.','Keeps earlier starts after choosing an interval and can count overlapping substrings.'],substring_oracle,random_substrings,lesson('This is interval scheduling over every substring whose endpoints match and whose length is at least four.','Greedily take the first valid finishing position, using the earliest occurrence of each letter since the last selected interval.','Record first positions; when current index is at least three later than its letter’s first position, count the interval and reset all starts.','Earliest-finish greedy leaves at least as much suffix as any competing first interval, so exchanging choices never reduces the attainable count.'),'O(n)','O(1)',5),
3558:entry('count_odd_path_edge_weights',[('edges','list[list[int]]')],'int',['trees','breadth first search','combinatorics'],['edges form a tree of up to 100,000 nodes labeled 1 through n and rooted at 1.','Choose any deepest node and consider only its root path.','Assign each path edge weight one or two; count assignments with odd total modulo 1,000,000,007.'],[([[[1,2]]],'Only weight one makes the one-edge path sum odd, giving one assignment.'),([[[1,2],[1,3],[3,4],[3,5]]],'A deepest path has two edges; (1,2) and (2,1) are the two odd-sum assignments.')],EDGE_WEIGHT_CASES,EDGE_WEIGHTS,[EDGE_WEIGHTS.replace('max(depth)-1','max(depth)'),EDGE_WEIGHTS.replace('max(depth)','min(value for value in depth[1:] if value>0)')],['Counts all 2^d assignments rather than exactly half of them.','Uses the shallowest non-root depth instead of the maximum depth.'],edge_weight_oracle,random_edge_weights,lesson('On a path of positive length d, toggling one chosen edge between weights one and two pairs every odd assignment with an even assignment.','Find the maximum root depth d; exactly half of the 2^d assignments have odd total, so return 2^(d-1).','Breadth-first search from node one to compute depths, take the maximum, and modularly exponentiate two to d-1.','The parity-flipping bijection proves the count is 2^(d-1), independent of which deepest node is selected.'),'O(n)','O(n)',5),
}
