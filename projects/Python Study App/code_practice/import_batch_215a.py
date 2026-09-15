"""Permutation ranks, point covers, disappearing paths, boundary maxima, and primes."""
from itertools import permutations
from math import isqrt

from .import_batch_055 import entry


def permutation_oracle(args):
    perm = tuple(args[0]); ordered = permutations(range(1, len(perm) + 1))
    return next(index for index, candidate in enumerate(ordered) if candidate == perm) % 1_000_000_007


def random_permutation(rng):
    values = list(range(1, rng.randint(1, 8) + 1)); rng.shuffle(values); return [values]


def rectangles_oracle(args):
    coordinates = sorted({point[0] for point in args[0]}); width = args[1]
    dp = [10**9] * (len(coordinates) + 1); dp[0] = 0
    for covered in range(len(coordinates)):
        end = covered
        while end < len(coordinates) and coordinates[end] - coordinates[covered] <= width:
            end += 1
        dp[end] = min(dp[end], dp[covered] + 1)
    return dp[-1]


def random_rectangles(rng):
    return [[[rng.randint(0, 30), rng.randint(0, 30)] for _ in range(rng.randint(1, 12))],
            rng.randint(0, 10)]


def disappearing_oracle(args):
    size, edges, disappear = args; infinity = 10**9; distance = [infinity] * size; distance[0] = 0
    for _ in range(size - 1):
        changed = False
        for left, right, weight in edges:
            if distance[left] + weight < distance[right] and distance[left] + weight < disappear[right]:
                distance[right] = distance[left] + weight; changed = True
            if distance[right] + weight < distance[left] and distance[right] + weight < disappear[left]:
                distance[left] = distance[right] + weight; changed = True
        if not changed:
            break
    return [-1 if value == infinity else value for value in distance]


def random_disappearing(rng):
    size = rng.randint(1, 9); edges = []
    for left in range(size):
        for right in range(left + 1, size):
            if rng.random() < .3:
                edges.append([left, right, rng.randint(1, 10)])
    disappear = [rng.randint(1, 30) for _ in range(size)]; disappear[0] = max(disappear[0], 1)
    return [size, edges, disappear]


def boundary_oracle(args):
    nums = args[0]; answer = 0
    for left in range(len(nums)):
        maximum = nums[left]
        for right in range(left, len(nums)):
            maximum = max(maximum, nums[right])
            answer += nums[left] == nums[right] == maximum
    return answer


def random_boundary(rng):
    return [[rng.randint(1, 12) for _ in range(rng.randint(1, 18))]]


def prime_difference_oracle(args):
    def prime(value):
        return value >= 2 and all(value % divisor for divisor in range(2, isqrt(value) + 1))
    positions = [index for index, value in enumerate(args[0]) if prime(value)]
    return positions[-1] - positions[0]


def random_prime_difference(rng):
    size = rng.randint(2, 20); nums = [rng.randint(1, 100) for _ in range(size)]
    nums[rng.randrange(size)] = rng.choice((2, 3, 5, 7, 11))
    return [nums]


PERMUTATION = '''def permutation_lexicographic_index(perm):
    modulo=1000000007;size=len(perm);tree=[0]*(size+1);factorial=[1]*size
    for index in range(1,size):factorial[index]=factorial[index-1]*index%modulo
    def add(index):
        while index<=size:tree[index]+=1;index+=index&-index
    def used_through(index):
        total=0
        while index:total+=tree[index];index-=index&-index
        return total
    answer=0
    for index,value in enumerate(perm):
        smaller_unused=value-1-used_through(value)
        answer=(answer+smaller_unused*factorial[size-index-1])%modulo
        add(value)
    return answer
'''


RECTANGLES = '''def minimum_width_rectangles(points,w):
    xs=sorted(point[0] for point in points);answer=0;covered=-1
    for x in xs:
        if x>covered:answer+=1;covered=x+w
    return answer
'''


DISAPPEAR = '''def minimum_disappearing_node_times(n,edges,disappear):
    from heapq import heappop,heappush
    graph=[[] for _ in range(n)]
    for left,right,weight in edges:
        graph[left].append((right,weight));graph[right].append((left,weight))
    infinity=10**30;distance=[infinity]*n;distance[0]=0;heap=[(0,0)]
    while heap:
        time,node=heappop(heap)
        if time!=distance[node]:continue
        for neighbor,weight in graph[node]:
            arrival=time+weight
            if arrival<distance[neighbor] and arrival<disappear[neighbor]:
                distance[neighbor]=arrival;heappush(heap,(arrival,neighbor))
    return [-1 if value==infinity else value for value in distance]
'''


BOUNDARY = '''def count_boundary_maximum_subarrays(nums):
    stack=[];answer=0
    for value in nums:
        while stack and stack[-1][0]<value:stack.pop()
        if not stack or stack[-1][0]>value:stack.append([value,1])
        else:stack[-1][1]+=1
        answer+=stack[-1][1]
    return answer
'''


PRIMES = '''def maximum_prime_index_distance(nums):
    from math import isqrt
    def prime(value):return value>=2 and all(value%divisor for divisor in range(2,isqrt(value)+1))
    left=next(index for index,value in enumerate(nums) if prime(value))
    right=next(index for index in range(len(nums)-1,-1,-1) if prime(nums[index]))
    return right-left
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3109: entry('permutation_lexicographic_index',[('perm','list[int]')],'int',['Fenwick trees','combinatorics','permutations'],['perm is a permutation of integers 1 through n.','Index all permutations in zero-based lexicographic order.','Return perm’s index modulo 1,000,000,007.'],[([[1,2]],'The ascending permutation is first, so its zero-based index is zero.'),([[3,1,2]],'The four earlier permutations begin with one or two, so [3,1,2] has index four.')],[[p] for p in [[1],[1,2],[2,1],[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1],[1,4,2,3],[4,3,2,1],[2,4,1,3],[5,1,2,3,4],[3,5,1,4,2]]],PERMUTATION,[PERMUTATION.replace('value-1-used_through(value)','value-used_through(value)'),PERMUTATION.replace('factorial[size-index-1]','factorial[index]')],['Counts the current value itself among smaller unused values.','Uses the factorial of the processed prefix instead of the remaining suffix length.'],permutation_oracle,random_permutation,lesson('At each position, every smaller unused value starts a block of (remaining length)! earlier permutations.','Use a Fenwick tree to count used values and precompute factorials modulo the target.','smallerUnused=value-1-usedThrough(value); add smallerUnused*(n-index-1)!; then mark value used.','Lexicographic blocks partition all earlier permutations by their first differing position, so summing their sizes gives the exact zero-based rank.'),'O(n log n)','O(n)',5),
3111: entry('minimum_width_rectangles',[('points','list[list[int]]'),('w','int')],'int',['greedy','sorting','geometry'],['points is nonempty and w is nonnegative.','A rectangle may have any height and horizontal interval [x1,x2] with x2-x1≤w; its bottom lies on y=0.','Return the minimum number of such rectangles covering every point; only x-coordinates affect coverage.'],[([[[2,1],[1,0],[1,4],[1,8],[3,5],[4,6]],1],'One rectangle covers x from one through two and another covers three through four, so two suffice.'),([[[0,5],[2,1],[4,9]],2],'Intervals [0,2] and [4,6] cover all points with two rectangles.')],[[p,w] for p,w in [([[0,0]],0),([[0,1],[0,9]],0),([[0,0],[1,1]],0),([[0,0],[1,1]],1),([[0,5],[2,1],[4,9]],2),([[2,1],[1,0],[1,4],[1,8],[3,5],[4,6]],1),([[1,1],[2,2],[3,3]],10),([[1,1],[3,2],[5,3]],1),([[5,1],[1,2],[3,3]],2),([[0,0],[2,0],[3,0],[5,0]],2),([[10,1],[10,2],[20,3]],5),([[1,100],[2,0],[7,50],[8,2]],1),([[0,1],[4,1],[8,1],[12,1]],4),([[3,3],[6,6],[9,9],[12,12]],2)]],RECTANGLES,[RECTANGLES.replace('covered=x+w','covered=x+w-1'),RECTANGLES.replace('if x>covered','if x>=covered')],['Treats the continuous inclusive width as if the right boundary were excluded.','Starts a new rectangle for a point exactly on the current inclusive right boundary.'],rectangles_oracle,random_rectangles,lesson('A rectangle starting at the leftmost uncovered x should extend its full width rightward; moving it left cannot cover any additional remaining point.','Sort x-coordinates and greedily start a rectangle at each first coordinate beyond the current covered boundary.','Maintain coveredRight; when x>coveredRight, increment and set coveredRight=x+w.','The first uncovered point forces a new rectangle, and the greedy placement maximizes its reach without sacrificing any earlier coverage.'),'O(n log n)','O(n)',5),
3112: entry('minimum_disappearing_node_times',[('n','int'),('edges','list[list[int]]'),('disappear','list[int]')],'list[int]',['graphs','Dijkstra','heaps'],['Vertices are 0 through n-1; edges are undirected with positive travel times and may repeat.','A node can be entered only at a time strictly earlier than disappear[node].','Starting at node zero at time zero, return each minimum arrival time or -1 when it cannot be reached in time.'],[([3,[[0,1,2],[1,2,1],[0,2,4]],[1,1,5]],'Node one disappears before arrival; node two is reached directly at time four, producing [0,-1,4].'),([4,[[0,1,2],[1,2,2],[0,3,10]],[5,5,5,10]],'Nodes one and two are reached at times two and four, while arrival at node three equals its disappearance and is forbidden.')],[[n,e,d] for n,e,d in [(1,[],[1]),(2,[],[1,5]),(2,[[0,1,1]],[1,2]),(2,[[0,1,2]],[1,2]),(3,[[0,1,2],[1,2,1],[0,2,4]],[1,1,5]),(3,[[0,1,2],[1,2,2]],[9,3,5]),(3,[[0,1,5],[0,1,2],[1,2,1]],[10,10,10]),(4,[[0,1,2],[1,2,2],[0,3,10]],[5,5,5,10]),(4,[[0,1,1],[1,2,1],[2,3,1]],[10,2,3,4]),(4,[[0,1,1],[2,3,1]],[5,5,5,5]),(5,[[0,1,3],[0,2,7],[1,3,2],[3,4,2]],[9,4,8,6,8]),(3,[[0,1,0],[1,2,1]],[2,2,2]),(5,[[0,1,2],[1,2,2],[2,3,2],[3,4,2]],[20,20,5,20,20]),(4,[[0,1,8],[0,2,3],[2,1,3],[1,3,1]],[10,7,5,9])]],DISAPPEAR,[DISAPPEAR.replace('arrival<disappear[neighbor]','arrival<=disappear[neighbor]'),DISAPPEAR.replace('arrival<disappear[neighbor]','time<disappear[neighbor]')],['Allows arrival exactly when the destination disappears.','Checks departure time instead of arrival time against the destination’s disappearance.'],disappearing_oracle,random_disappearing,lesson('Positive weights make the earliest unsettled arrival final, but a relaxation is usable only before the destination vanishes.','Run Dijkstra and reject candidate arrivals greater than or equal to the neighbor’s disappearance time.','Pop minimum time, skip stale entries, and relax when arrival<distance and arrival<disappear; map infinity to -1.','Dijkstra’s ordering proves minimum arrival among all time-valid paths, and every accepted relaxation respects the strict availability boundary.'),'O((n+edges) log n)','O(n+edges)',5),
3113: entry('count_boundary_maximum_subarrays',[('nums','list[int]')],'int',['monotonic stacks','arrays','counting'],['nums contains positive integers.','Count nonempty contiguous subarrays whose first and last values are equal to the maximum value appearing anywhere inside that subarray.','Every one-element subarray qualifies.'],[([[1,4,3,3,2]],'All five singletons qualify, and subarray [3,3] adds one, for six total.'),([[3,1,3,3]],'Four singletons plus [3,1,3], the final [3,3], and the whole array give seven.')],[[n] for n in [[1],[1,1],[1,2],[2,1],[1,4,3,3,2],[3,1,3,3],[2,2,2],[3,2,1,3],[1,3,2,3,1],[5,1,5,1,5],[1,2,3,2,1],[4,4,3,4],[2,1,2,3,2],[7,6,7,5,7,8,7]]],BOUNDARY,[BOUNDARY.replace('stack[-1][0]<value','stack[-1][0]<=value'),BOUNDARY.replace('answer+=stack[-1][1]','answer+=1')],['Pops equal values, losing earlier equal boundaries that should pair with the current endpoint.','Counts only singleton subarrays and ignores qualifying longer intervals.'],boundary_oracle,random_boundary,lesson('For a right boundary value x, valid left boundaries are earlier equal x values with no intervening value greater than x.','Maintain a decreasing stack of values and counts since the most recent larger blocker.','Pop smaller values; push x with count one or increment its equal top count; add that count to the answer.','After popping, the equal top entries are exactly the valid left boundaries ending here, including the current singleton.'),'O(n)','O(n)',8),
3115: entry('maximum_prime_index_distance',[('nums','list[int]')],'int',['number theory','arrays','primality'],['nums contains at least two positive integers and includes at least one prime value.','Distance is the absolute difference between array indices containing prime numbers.','Return the maximum such distance; with one prime position the result is zero.'],[([[4,2,9,5,3]],'The first prime is at index one and the last at index four, giving distance three.'),([[4,6,8,11,12]],'Only eleven is prime, so both selected prime indices are three and the distance is zero.')],[[n] for n in [[2,4],[4,2],[2,3],[4,2,9,5,3],[4,6,8,11,12],[1,1,2,1,1],[17,4,6,8,19],[0,2,4,6,7],[49,25,11,13,15],[97,1,1,1,2],[8,9,10,11,12,13],[2,4,5,6,7,8],[100,101,102],[3,3,3,3]]],PRIMES,[PRIMES.replace('value>=2','value>2'),PRIMES.replace('isqrt(value)+1','isqrt(value)')],['Treats two as nonprime and can choose later endpoints.','Stops trial division before the square root and misclassifies perfect squares as prime.'],prime_difference_oracle,random_prime_difference,lesson('The farthest pair of qualifying indices is always the first and last prime occurrence.','Scan from each end using a square-root primality test.','Find leftmost prime and rightmost prime, then return right-left.','Every prime index lies between those extremes, so no other pair has greater index distance.'),'O(n*sqrt(max value))','O(1)',5),
}
