"""Shortest-path edges, right triangles, stable arrays, and two deletions."""
from itertools import combinations

from .import_batch_055 import entry


def path_edges_oracle(args):
    size, edges = args; infinity = 10**9
    distance = [[infinity] * size for _ in range(size)]
    for node in range(size):distance[node][node] = 0
    for left, right, weight in edges:
        distance[left][right] = min(distance[left][right], weight)
        distance[right][left] = min(distance[right][left], weight)
    for middle in range(size):
        for left in range(size):
            for right in range(size):
                distance[left][right] = min(distance[left][right], distance[left][middle] + distance[middle][right])
    target = distance[0][size - 1]
    return [target < infinity and (distance[0][left] + weight + distance[right][size-1] == target or
            distance[0][right] + weight + distance[left][size-1] == target)
            for left, right, weight in edges]


def random_path_edges(rng):
    size = rng.randint(2, 8); edges = []
    for left in range(size):
        for right in range(left + 1, size):
            if rng.random() < .35:edges.append([left, right, rng.randint(1, 12)])
    return [size, edges]


def triangles_oracle(args):
    grid = args[0]; ones = [(r,c) for r,row in enumerate(grid) for c,value in enumerate(row) if value]
    answer = 0
    for pivot in ones:
        for horizontal in ones:
            for vertical in ones:
                if horizontal != pivot and vertical != pivot and horizontal[0] == pivot[0] and vertical[1] == pivot[1]:
                    answer += 1
    return answer


def random_triangles(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    return [[[rng.randrange(2) for _ in range(columns)] for _ in range(rows)]]


def stable_oracle(args):
    zeros, ones, limit = args; size = zeros + ones; answer = 0
    for zero_positions in combinations(range(size), zeros):
        chosen = set(zero_positions); run = 0; previous = None; valid = True
        for index in range(size):
            value = 0 if index in chosen else 1
            run = run + 1 if value == previous else 1; previous = value
            if run > limit:valid = False; break
        answer += valid
    return answer % 1_000_000_007


def random_stable(rng):
    return [rng.randint(1, 6), rng.randint(1, 6), rng.randint(1, 5)]


def added_oracle(args):
    first, second = args; answer = 10**9
    for removed in combinations(range(len(first)), 2):
        kept = [value for index, value in enumerate(first) if index not in removed]
        offsets = {right - left for left, right in zip(sorted(kept), sorted(second))}
        if len(offsets) == 1:answer = min(answer, offsets.pop())
    return answer


def random_added(rng):
    size = rng.randint(3, 10); first = [rng.randint(-15, 20) for _ in range(size)]
    removed = set(rng.sample(range(size), 2)); offset = rng.randint(-10, 10)
    second = [value + offset for index, value in enumerate(first) if index not in removed]
    rng.shuffle(second); return [first, second]


PATHS = '''def edges_on_any_shortest_path(n,edges):
    from heapq import heappop,heappush
    graph=[[] for _ in range(n)]
    for index,(left,right,weight) in enumerate(edges):
        graph[left].append((right,weight));graph[right].append((left,weight))
    def dijkstra(start):
        distance=[10**30]*n;distance[start]=0;heap=[(0,start)]
        while heap:
            cost,node=heappop(heap)
            if cost!=distance[node]:continue
            for neighbor,weight in graph[node]:
                candidate=cost+weight
                if candidate<distance[neighbor]:distance[neighbor]=candidate;heappush(heap,(candidate,neighbor))
        return distance
    start=dijkstra(0);finish=dijkstra(n-1);shortest=start[n-1]
    return [start[left]+weight+finish[right]==shortest or start[right]+weight+finish[left]==shortest
            for left,right,weight in edges]
'''


TRIANGLES = '''def count_axis_aligned_right_triangles(grid):
    rows=[sum(row) for row in grid];columns=[sum(grid[row][column] for row in range(len(grid))) for column in range(len(grid[0]))]
    return sum((rows[row]-1)*(columns[column]-1) for row in range(len(grid))
        for column in range(len(grid[0])) if grid[row][column])
'''


STABLE_I = '''def stable_binary_arrays_small(zero,one,limit):
    from functools import lru_cache
    modulo=1000000007
    @lru_cache(None)
    def search(zeros,ones,last,run):
        if zeros==0 and ones==0:return 1
        answer=0
        if zeros and (last!=0 or run<limit):answer+=search(zeros-1,ones,0,run+1 if last==0 else 1)
        if ones and (last!=1 or run<limit):answer+=search(zeros,ones-1,1,run+1 if last==1 else 1)
        return answer%modulo
    return search(zero,one,2,0)
'''


STABLE_II = '''def stable_binary_arrays_large(zero,one,limit):
    modulo=1000000007
    ending_zero=[[0]*(one+1) for _ in range(zero+1)];ending_one=[[0]*(one+1) for _ in range(zero+1)]
    for z in range(1,min(zero,limit)+1):ending_zero[z][0]=1
    for o in range(1,min(one,limit)+1):ending_one[0][o]=1
    for z in range(1,zero+1):
        for o in range(1,one+1):
            ending_zero[z][o]=(ending_zero[z-1][o]+ending_one[z-1][o]-(ending_one[z-limit-1][o] if z>limit else 0))%modulo
            ending_one[z][o]=(ending_zero[z][o-1]+ending_one[z][o-1]-(ending_zero[z][o-limit-1] if o>limit else 0))%modulo
    return (ending_zero[zero][one]+ending_one[zero][one])%modulo
'''


ADDED = '''def minimum_added_after_two_removals(nums1,nums2):
    first=sorted(nums1);second=sorted(nums2);answer=10**30
    for candidate_index in range(3):
        offset=second[0]-first[candidate_index];left=right=removed=0
        while left<len(first) and right<len(second):
            if first[left]+offset==second[right]:right+=1
            else:removed+=1
            left+=1
        if right==len(second) and removed+len(first)-left<=2:answer=min(answer,offset)
    return answer
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3123: entry('edges_on_any_shortest_path',[('n','int'),('edges','list[list[int]]')],'list[bool]',['graphs','Dijkstra','shortest paths'],['n≥2 and edges is an undirected positive-weight edge list in input order; the graph may be disconnected or contain parallel edges.','Return one Boolean per edge indicating whether that exact edge belongs to at least one shortest path from node zero to node n-1.','If the destination is unreachable, every result is false.'],[([6,[[0,1,4],[0,2,1],[1,3,2],[1,4,3],[1,5,1],[2,3,1],[3,5,3],[4,5,2]]],'Both length-five routes contribute seven marked edges; edge 1-4-5 is longer and remains false.'),([3,[[0,1,1]],],'Node two is unreachable, so the only edge is not part of a source-to-destination shortest path.')],[[n,e] for n,e in [(2,[]),(2,[[0,1,1]]),(3,[[0,1,1]]),(3,[[0,1,1],[1,2,1],[0,2,2]]),(3,[[0,1,5],[0,1,1],[1,2,1]]),(4,[[0,1,1],[1,3,1],[0,2,1],[2,3,1]]),(4,[[0,1,1],[1,2,1],[2,3,1],[0,3,10]]),(5,[[0,1,2],[1,4,2],[0,2,1],[2,3,1],[3,4,2]]),(4,[[0,1,3],[2,3,3]]),(5,[[0,1,1],[1,2,1],[2,4,1],[0,3,2],[3,4,2]]),(3,[[0,1,2],[1,2,1]]),(6,[[0,1,4],[0,2,1],[1,3,2],[1,4,3],[1,5,1],[2,3,1],[3,5,3],[4,5,2]]),(5,[[0,1,2],[1,2,2],[2,4,2],[0,3,6],[3,4,1]]),(4,[[0,1,7],[1,3,5],[0,2,2],[2,3,10]])]],PATHS,[PATHS.replace('==shortest or','==shortest and'),PATHS.replace('finish=dijkstra(n-1)','finish=start')],['Requires the same undirected edge to satisfy both path orientations instead of either orientation.','Uses source distances for both sides instead of distances from the destination.'],path_edges_oracle,random_path_edges,lesson('An undirected edge lies on a shortest route iff one orientation joins a shortest prefix and suffix with exact total distance.','Run Dijkstra from both endpoints, then test each input edge in both orientations.','Mark (u,v,w) when d0[u]+w+dn[v]=d0[n-1] or d0[v]+w+dn[u]=d0[n-1].','Any marked equality concatenates into a shortest path, and every edge on a shortest path satisfies one orientation equality.'),'O((n+edges) log n)','O(n+edges)',8),
3128: entry('count_axis_aligned_right_triangles',[('grid','list[list[int]]')],'int',['matrices','counting','combinatorics'],['grid is a nonempty rectangular binary matrix.','Choose three one-cells forming a right angle whose legs follow one shared row and one shared column; distances may be any positive amount.','Count distinct triangles, with the right-angle cell distinguishing each choice.'],[([[[0,1,0],[0,1,1],[0,1,0]]],'The center one can pair with the right one and either vertical one, producing two triangles.'),([[[1,1],[1,1]]],'Every corner can serve as the right-angle vertex, producing four triangles.')],[[g] for g in [[[0]],[[1]],[[1,1]],[[1],[1]],[[1,1],[1,1]],[[0,1,0],[0,1,1],[0,1,0]],[[1,0],[0,1]],[[1,1,1]],[[1],[1],[1]],[[1,0,1],[0,1,0],[1,0,1]],[[1,1,0],[1,0,0],[1,1,1]],[[0,0],[0,0]],[[1,0,1],[1,0,1]],[[1,1,1],[1,1,1]]]],TRIANGLES,[TRIANGLES.replace('(rows[row]-1)*(columns[column]-1)','rows[row]*columns[column]'),TRIANGLES.replace('if grid[row][column]','')],['Includes the pivot itself as choices for both triangle legs.','Counts zero-cells as possible right-angle vertices.'],triangles_oracle,random_triangles,lesson('For each one-cell pivot, any other one in its row can pair with any other one in its column.','Precompute row and column one-counts, then sum (rowCount-1)*(columnCount-1) over one-cells.','Count rows and columns; for each grid[r][c]=1 add (rows[r]-1)(cols[c]-1).','Each factor independently chooses one endpoint, and every axis-aligned right triangle has exactly one right-angle pivot.'),'O(rows*columns)','O(rows+columns)',5),
3129: entry('stable_binary_arrays_small',[('zero','int'),('one','int'),('limit','int')],'int',['dynamic programming','recursion','binary arrays'],['zero, one, and limit are positive integers in the version-I constraint range.','Use exactly zero zeros and one ones, with no run of equal bits longer than limit.','Return the number of valid arrays modulo 1,000,000,007.'],[([1,1,2],'Both 01 and 10 are valid, so the result is two.'),([3,1,1],'Only 0101 could alternate fully, but it has two ones; no valid array exists.')],[[z,o,l] for z,o,l in [(1,1,1),(1,1,2),(2,1,1),(1,2,1),(2,2,1),(2,2,2),(3,1,1),(3,1,2),(3,2,2),(4,3,2),(1,4,3),(5,2,3),(3,3,1),(4,4,4)]],STABLE_I,[STABLE_I.replace('run<limit','run<=limit'),STABLE_I.replace('return search(zero,one,2,0)','return search(zero,one,0,limit)')],['Allows runs of length limit+1.','Pretends an already-full zero run precedes the array, incorrectly forbidding a leading zero.'],stable_oracle,random_stable,lesson('A partial array is determined for future choices by remaining counts, its last bit, and current run length.','Memoize that state and append either bit only when its run stays within limit.','Recurse on placing zero or one; reset run on a bit change and return one after both counts reach zero.','The states enumerate every binary arrangement once, and the transition guard is exactly the maximum-run condition.'),'O(zero*one*limit)','O(zero*one*limit)',5),
3130: entry('stable_binary_arrays_large',[('zero','int'),('one','int'),('limit','int')],'int',['dynamic programming','prefix sums','binary arrays'],['zero, one, and limit are positive integers and may reach the larger version-II limits.','Use exactly zero zeros and one ones, with no run of equal bits longer than limit.','Return the count modulo 1,000,000,007 using a quadratic-state recurrence.'],[([1,1,2],'The two arrays 01 and 10 are both valid.'),([3,3,1],'Strict alternation permits exactly 010101 and 101010, so the answer is two.')],[[z,o,l] for z,o,l in [(1,1,1),(1,1,2),(2,1,1),(1,2,1),(2,2,1),(2,2,2),(3,1,1),(3,1,2),(3,2,2),(4,3,2),(1,4,3),(5,2,3),(3,3,1),(4,4,4)]],STABLE_II,[STABLE_II.replace('z-limit-1','z-limit'),STABLE_II.replace('o-limit-1','o-limit')],['Subtracts zero-run states of length exactly limit instead of only overlong runs.','Subtracts one-run states of length exactly limit instead of only overlong runs.'],stable_oracle,random_stable,lesson('Counts ending in each bit can be extended from either ending state, except extensions that create a run longer than limit.','Use two DP tables and subtract the opposite-ending state that would start an overlong run.','end0[z][o]=end0[z-1][o]+end1[z-1][o]-end1[z-limit-1][o], symmetrically for end1.','The additions cover all one-bit extensions, and the subtracted boundary states are exactly those whose new terminal run has limit+1 equal bits.'),'O(zero*one)','O(zero*one)',8),
3132: entry('minimum_added_after_two_removals',[('nums1','list[int]'),('nums2','list[int]')],'int',['sorting','two pointers','enumeration'],['nums1 has exactly two more integer elements than nums2.','Remove exactly two nums1 indices, then add the same integer x to every remaining value so its multiset equals nums2.','At least one solution exists; return the smallest possible x.'],[([[4,20,16,12,8],[14,18,10]],'Remove four and eight; adding negative two to [20,16,12] produces [18,14,10], exactly the target multiset.'),([[3,5,5,3],[7,7]],'Remove both threes and add two to the two fives, producing [7,7].')],[[a,b] for a,b in [([1,2,3],[4]),([1,1,1],[2]),([3,5,5,3],[7,7]),([4,20,16,12,8],[14,18,10]),([1,2,3,4],[3,4]),([10,10,20,20],[15,25]),([-5,-1,3],[0]),([0,0,1,1,2],[2,2,3]),([9,1,5,3],[4,6]),([2,2,2,3,3],[5,5,6]),([100,1,2,3],[11,12]),([7,4,10,1,13],[9,12,15]),([-3,-2,-1,0],[5,6]),([8,6,4,2,0],[1,3,5])]],ADDED,[ADDED.replace('for candidate_index in range(3)','for candidate_index in range(1)'),ADDED.replace('answer=min(answer,offset)','answer=max(answer,offset)')],['Assumes the smallest nums1 value is kept and misses solutions deleting it.','Maximizes the valid offset instead of returning the smallest one.'],added_oracle,random_added,lesson('After sorting, nums2’s smallest value must align with one of nums1’s first three values because only two nums1 values are removed.','Try those three offsets and greedily skip at most two mismatches with two pointers.','For candidate i=0,1,2 set x=nums2[0]-nums1[i]; scan sorted arrays, matching shifted values and counting skips; minimize valid x.','Every solution exposes its first kept nums1 value among the first three, and sorted matching uniquely determines whether that offset can delete only two values.'),'O(n log n)','O(n)',5),
}
