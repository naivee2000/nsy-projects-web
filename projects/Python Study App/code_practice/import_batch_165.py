"""Graph BFS, binary runs, reward selection, reversal BFS, and geometry batch 165."""

from collections import deque
from itertools import combinations

from .import_batch_055 import entry


def cycle_oracle(args):
    n, edges = args
    graph = [[] for _ in range(n)]
    for edge_index, (left, right) in enumerate(edges):
        graph[left].append((right, edge_index));graph[right].append((left, edge_index))
    best = 10**9
    for removed, (start, target) in enumerate(edges):
        queue = deque([(start, 0)]);seen = {start}
        while queue:
            node, distance = queue.popleft()
            if node == target:
                best = min(best, distance + 1);break
            for neighbor, edge_index in graph[node]:
                if edge_index != removed and neighbor not in seen:
                    seen.add(neighbor);queue.append((neighbor, distance + 1))
    return -1 if best == 10**9 else best


def random_cycle(rng):
    n = rng.randint(2, 9)
    possible = list(combinations(range(n), 2));rng.shuffle(possible)
    return [n, [list(edge) for edge in possible[: rng.randint(0, min(len(possible), 14))]]]


def balanced_oracle(args):
    s = args[0];best = 0
    for left in range(len(s)):
        for right in range(left + 1, len(s) + 1):
            part = s[left:right]
            if len(part) % 2 == 0 and part == "0" * (len(part)//2) + "1" * (len(part)//2):
                best = max(best, len(part))
    return best


def random_balanced(rng):
    return ["".join(rng.choice("01") for _ in range(rng.randint(1, 50)))]


def cheese_oracle(args):
    first, second, k = args
    return max(sum(first[i] if i in chosen else second[i] for i in range(len(first)))
               for chosen in map(set, combinations(range(len(first)), k)))


def random_cheese(rng):
    n = rng.randint(1, 9)
    return [[rng.randint(1, 30) for _ in range(n)], [rng.randint(1, 30) for _ in range(n)], rng.randint(0, n)]


def reverse_oracle(args):
    n, p, banned, k = args
    blocked = set(banned);answer = [-1] * n;answer[p] = 0;queue = deque([p])
    while queue:
        position = queue.popleft()
        for left in range(max(0, position-k+1), min(position, n-k)+1):
            following = 2*left+k-1-position
            if following not in blocked and answer[following] < 0:
                answer[following] = answer[position] + 1;queue.append(following)
    return answer


def random_reverse(rng):
    n = rng.randint(1, 18);p = rng.randrange(n);k = rng.randint(1, n)
    banned = [i for i in range(n) if i != p and rng.random() < .25]
    return [n, p, banned, k]


def pair_oracle(args):
    first, second = args
    return list(min(combinations(range(len(first)), 2),
                    key=lambda pair: (abs(first[pair[0]]-first[pair[1]]) + abs(second[pair[0]]-second[pair[1]]), pair)))


def random_pair(rng):
    n = rng.randint(2, 24)
    return [[rng.randint(-30, 30) for _ in range(n)], [rng.randint(-30, 30) for _ in range(n)]]


CYCLE = """\
def shortest_undirected_cycle(n,edges):
    from collections import deque
    graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    best=n+1
    for start in range(n):
        distance=[-1]*n;parent=[-1]*n;distance[start]=0;queue=deque([start])
        while queue:
            node=queue.popleft()
            for neighbor in graph[node]:
                if distance[neighbor]<0:
                    distance[neighbor]=distance[node]+1;parent[neighbor]=node;queue.append(neighbor)
                elif parent[node]!=neighbor:
                    best=min(best,distance[node]+distance[neighbor]+1)
    return -1 if best==n+1 else best
"""

BALANCED = """\
def longest_ordered_balanced_binary_substring(s):
    best=zeros=ones=0
    for char in s:
        if char=='0':
            if ones:zeros=0;ones=0
            zeros+=1
        else:
            ones+=1;best=max(best,2*min(zeros,ones))
    return best
"""

CHEESE = """\
def maximum_mice_cheese_reward(reward1,reward2,k):
    gains=sorted((a-b for a,b in zip(reward1,reward2)),reverse=True)
    return sum(reward2)+sum(gains[:k])
"""

REVERSE = """\
def minimum_fixed_reverse_moves(n,p,banned,k):
    import bisect
    from collections import deque
    blocked=set(banned)|{p};values=[[],[]]
    for index in range(n):
        if index not in blocked:values[index%2].append(index)
    parents=[list(range(len(row)+1)) for row in values]
    def find(parents,index):
        while parents[index]!=index:
            parents[index]=parents[parents[index]];index=parents[index]
        return index
    answer=[-1]*n;answer[p]=0;queue=deque([p])
    while queue:
        position=queue.popleft()
        low=max(position-k+1,k-1-position)
        high=min(position+k-1,2*n-k-1-position)
        parity=low%2;row=values[parity];parent=parents[parity]
        index=find(parent,bisect.bisect_left(row,low))
        while index<len(row) and row[index]<=high:
            following=row[index];answer[following]=answer[position]+1;queue.append(following)
            parent[index]=find(parent,index+1);index=find(parent,index)
    return answer
"""

PAIR = """\
def closest_manhattan_pair(nums1,nums2):
    points=sorted((x,y,index) for index,(x,y) in enumerate(zip(nums1,nums2)))
    best=(10**30,len(nums1),len(nums1))
    def visit(left,right):
        nonlocal best
        if right-left<=3:
            for i in range(left,right):
                for j in range(i+1,right):
                    a,b=sorted((points[i][2],points[j][2]))
                    best=min(best,(abs(points[i][0]-points[j][0])+abs(points[i][1]-points[j][1]),a,b))
            return
        middle=(left+right)//2;x=points[middle][0]
        visit(left,middle);visit(middle,right)
        strip=sorted((point for point in points[left:right] if abs(point[0]-x)<=best[0]),key=lambda point:point[1])
        for i in range(len(strip)):
            for j in range(i+1,len(strip)):
                if strip[j][1]-strip[i][1]>best[0]:break
                a,b=sorted((strip[i][2],strip[j][2]))
                best=min(best,(abs(strip[i][0]-strip[j][0])+abs(strip[i][1]-strip[j][1]),a,b))
    visit(0,len(points))
    return [best[1],best[2]]
"""


BATCH = {
    2608: entry(
        "shortest_undirected_cycle", [("n", "int"), ("edges", "list[list[int]]")], "int", ["graphs", "breadth-first search"],
        ["Vertices are numbered zero through n-1 and edges are distinct undirected pairs.", "Return the number of edges in the shortest simple cycle.", "Return -1 when the graph contains no cycle."],
        [
            ([7, [[0,1],[1,2],[2,0],[3,4],[4,5],[5,6],[6,3]]], "The triangle among zero, one, and two is the shortest cycle, of length three."),
            ([4, [[0,1],[1,2],[2,3]]], "This path has no cycle, so the result is negative one."),
        ],
        [[n,e] for n,e in [
            (2,[]),(2,[[0,1]]),(3,[[0,1],[1,2],[2,0]]),(4,[[0,1],[1,2],[2,3],[3,0]]),
            (5,[[0,1],[1,2],[2,0],[2,3],[3,4],[4,2]]),(6,[[0,1],[1,2],[2,3],[3,4],[4,5]]),
            (6,[[0,1],[1,2],[2,0],[0,3],[3,4],[4,5],[5,0]]),(5,[[0,1],[0,2],[0,3],[0,4]]),
            (4,[[0,1],[1,2],[2,0],[2,3],[3,1]]),(7,[[0,1],[1,2],[2,3],[3,4],[4,0],[2,5],[5,6],[6,2]]),
            (3,[]),(8,[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4]]),
            (5,[[0,1],[1,2],[2,3],[3,1]]),(6,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,0],[0,3]]),
        ]],
        CYCLE,
        [CYCLE.replace("parent[node]!=neighbor", "parent[neighbor]!=node"), CYCLE.replace("distance[node]+distance[neighbor]+1", "distance[node]+distance[neighbor]")],
        ["Uses the neighbor's parent test and mistakes each tree edge for a cycle.", "Omits the closing edge from every detected cycle length."],
        cycle_oracle, random_cycle,
        ["Run breadth-first search from every vertex.", "Store each discovered node's distance and BFS parent.", "An edge to a visited non-parent neighbor closes a cycle of the two distances plus one.", "Every shortest cycle is exposed by a BFS rooted on it, while parent checks exclude immediate backtracking edges."],
        "O(n*(n+e))", "O(n+e)", 8,
    ),
    2609: entry(
        "longest_ordered_balanced_binary_substring", [("s", "str")], "int", ["strings", "two pointers"],
        ["A balanced substring consists of some zeros followed by the same number of ones.", "The zero and one blocks must each be contiguous and nonempty.", "Return the maximum balanced substring length, or zero if none exists."],
        [(["01000111"], "The final 000111 block is balanced and has length six."), (["00111"], "Two zeros followed by the first two ones form a length-four balanced substring.")],
        [[s] for s in ["0","1","01","10","0011","000111","00011","00111","0101","111000","0000","1111","1010011","0010111"]],
        BALANCED,
        [BALANCED.replace("min(zeros,ones)", "max(zeros,ones)"), BALANCED.replace("if ones:zeros=0;ones=0", "if ones:ones=0")],
        ["Uses the larger run length and can claim unmatched characters.", "Fails to clear the preceding zero run when a new zero block begins."],
        balanced_oracle, random_balanced,
        ["Only the boundary between a zero run and its following one run matters.", "Count zeros in the current zero run and ones in the following one run.", "At each one, a balanced suffix uses twice the smaller run count; reset both counts when zeros resume after ones.", "Every valid substring lies at one such run boundary, and taking the smaller count is both feasible and maximal there."],
        "O(n)", "O(1)", 3,
    ),
    2611: entry(
        "maximum_mice_cheese_reward", [("reward1", "list[int]"), ("reward2", "list[int]"), ("k", "int")], "int", ["arrays", "greedy", "sorting"],
        ["Exactly one mouse eats each cheese type.", "Mouse one must eat exactly k types; mouse two eats all remaining types.", "Return the maximum total reward earned by both mice."],
        [
            ([[1,1,3,4],[4,4,1,1],2], "Giving mouse one the last two cheeses and mouse two the first two earns fifteen."),
            ([[1,1],[1,1],2], "Mouse one must take both cheeses, and the total reward is two."),
        ],
        [[a,b,k] for a,b,k in [
            ([1],[2],0),([1],[2],1),([5,1],[1,5],1),([1,1],[1,1],0),([1,1],[1,1],1),
            ([3,8,2],[7,1,5],2),([10,1,1],[1,10,10],1),([4,5,6],[6,5,4],3),
            ([2,9,4,7],[8,1,6,3],2),([100,1],[1,100],1),([3,3,3,3],[1,2,3,4],2),
            ([1,2,3,4,5],[5,4,3,2,1],2),([7,2,9],[4,8,1],0),([7,2,9],[4,8,1],3),
        ]],
        CHEESE,
        [CHEESE.replace("reverse=True", "reverse=False"), CHEESE.replace("sum(reward2)", "sum(reward1)")],
        ["Chooses the k smallest advantages for mouse one.", "Uses mouse one's rewards as the baseline before adding its advantage again."],
        cheese_oracle, random_cheese,
        ["Start by assigning every cheese to mouse two.", "For cheese i, switching it to mouse one changes the total by reward1[i]-reward2[i].", "Sort those gains and take exactly the largest k.", "Every legal allocation is a size-k set of switches, and the k largest independent gains maximize their sum."],
        "O(n log n)", "O(n)", 5,
    ),
    2612: entry(
        "minimum_fixed_reverse_moves", [("n", "int"), ("p", "int"), ("banned", "list[int]"), ("k", "int")], "list[int]", ["arrays", "breadth-first search", "disjoint sets"],
        ["A length-n binary array has its only one at p; an operation reverses any contiguous length-k subarray.", "The one may not land on a banned index.", "Return each index's minimum operations from p, using -1 when unreachable."],
        [
            ([4,0,[1,2],4], "Reversing the whole array moves the one from zero to three; banned indices remain unreachable."),
            ([5,0,[],2], "Successive length-two reversals move the one one step at a time, giving distances zero through four."),
        ],
        [[n,p,b,k] for n,p,b,k in [
            (1,0,[],1),(2,0,[],1),(2,0,[],2),(3,1,[],2),(4,0,[],3),(4,2,[0],2),
            (5,2,[1,3],3),(6,0,[2,4],2),(6,5,[1],4),(7,3,[],1),(7,0,[],7),
            (8,2,[0,5],5),(9,4,[1,7],4),(10,0,[3,6,8],6),
        ]],
        REVERSE,
        [REVERSE.replace("low=max(position-k+1,k-1-position)", "low=min(position-k+1,k-1-position)"), REVERSE.replace("parity=low%2", "parity=(low+1)%2")],
        ["Uses the smaller lower-bound expression and admits impossible reversal endpoints.", "Searches the opposite parity class from every reachable range."],
        reverse_oracle, random_reverse,
        ["For one position, valid reversal starts map it to a same-parity interval [low, high].", "Breadth-first search supplies minimum operation counts.", "Keep unvisited non-banned indices split by parity, with successor disjoint sets that skip indices after removal.", "Each reachable index is enqueued and removed once; interval bounds enumerate exactly all one-reversal destinations."],
        "O(n log n)", "O(n)", 8,
    ),
    2613: entry(
        "closest_manhattan_pair", [("nums1", "list[int]"), ("nums2", "list[int]")], "list[int]", ["arrays", "divide and conquer", "geometry", "sorting"],
        ["Point i has coordinates (nums1[i], nums2[i]).", "Return i<j minimizing Manhattan distance |x_i-x_j|+|y_i-y_j|.", "Break equal-distance ties by the lexicographically smallest [i,j]."],
        [
            ([[1,2,3,2,4],[2,3,1,2,3]], "Points zero and three are identical, so [0,3] has minimum distance zero."),
            ([[1,4,7],[1,5,2]], "The first two points have distance seven and the last two have distance six, so return [1,2]."),
        ],
        [[a,b] for a,b in [
            ([0,1],[0,0]),([0,0],[0,0]),([1,2,3],[1,2,3]),([1,4,7],[1,5,2]),
            ([5,1,5],[2,2,2]),([0,10,20,30],[0,1,0,1]),([-5,5],[-5,5]),
            ([1,1,2,2],[1,2,1,2]),([9,0,4,8],[3,7,1,6]),([1,5,9,13,17],[10,8,6,4,2]),
            ([3,3,3,3],[4,4,5,5]),([-10,-9,10,11],[0,5,0,5]),([2,8,2,8,5],[7,1,6,2,4]),
            ([100,0,50,51],[100,0,50,52]),([10,0],[0,0]),
        ]],
        PAIR,
        [PAIR.replace("best=min(best,", "best=max(best,"), PAIR.replace("a,b=sorted((points[i][2],points[j][2]))", "a,b=points[i][2],points[j][2]")],
        ["Keeps the farthest candidate rather than the closest one.", "Fails to normalize pair indices before lexicographic tie-breaking."],
        pair_oracle, random_pair,
        ["Sort points by x and recursively solve the left and right halves.", "Only points within the current best x-distance of the split can improve the answer.", "Sort that strip by y and compare forward until the y gap exceeds the best distance.", "Every closest pair is either contained in a half or crosses the split and therefore appears in the strip scan; tuple comparison enforces index ties."],
        "O(n log² n)", "O(n)", 8,
    ),
}
