"""Hard workbook batch 149."""

from collections import Counter, deque
from heapq import heappop, heappush
from math import factorial
from .import_batch_055 import entry


def unequal_oracle(args):
    start, target = args
    start = tuple(start)
    heap = [(0, start)]
    best = {start: 0}
    while heap:
        cost, state = heappop(heap)
        if cost != best[state]:
            continue
        if all(a != b for a, b in zip(state, target)):
            return cost
        for left in range(len(state)):
            for right in range(left + 1, len(state)):
                changed = list(state)
                changed[left], changed[right] = changed[right], changed[left]
                changed = tuple(changed)
                new = cost + left + right
                if new < best.get(changed, 10**30):
                    best[changed] = new
                    heappush(heap, (new, changed))
    return -1


def random_unequal(rng):
    n = rng.randint(1, 6)
    return [
        [rng.randint(1, 4) for _ in range(n)],
        [rng.randint(1, 4) for _ in range(n)],
    ]


def points_oracle(args):
    grid, queries = args
    height = len(grid)
    width = len(grid[0])
    answer = []
    for limit in queries:
        if grid[0][0] >= limit:
            answer.append(0)
            continue
        seen = {(0, 0)}
        queue = deque([(0, 0)])
        while queue:
            row, column = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                r, c = row + dr, column + dc
                if (
                    0 <= r < height
                    and 0 <= c < width
                    and (r, c) not in seen
                    and grid[r][c] < limit
                ):
                    seen.add((r, c))
                    queue.append((r, c))
        answer.append(len(seen))
    return answer


def random_points(rng):
    h = rng.randint(1, 8)
    w = rng.randint(1, 8)
    return [
        [[rng.randint(1, 30) for _ in range(w)] for _ in range(h)],
        [rng.randint(1, 35) for _ in range(rng.randint(1, 12))],
    ]


def even_degrees_oracle(args):
    n, edges = args
    existing = {tuple(sorted(edge)) for edge in edges}
    missing = [
        (a, b)
        for a in range(1, n + 1)
        for b in range(a + 1, n + 1)
        if (a, b) not in existing
    ]
    degree = [0] * (n + 1)
    for a, b in existing:
        degree[a] += 1
        degree[b] += 1
    for count in range(3):
        for added in __import__("itertools").combinations(missing, count):
            parity = degree[:]
            for a, b in added:
                parity[a] += 1
                parity[b] += 1
            if all(value % 2 == 0 for value in parity[1:]):
                return True
    return False


def random_even_degrees(rng):
    n = rng.randint(1, 8)
    all_edges = [(a, b) for a in range(1, n + 1) for b in range(a + 1, n + 1)]
    rng.shuffle(all_edges)
    return [n, [list(edge) for edge in all_edges[: rng.randint(0, len(all_edges))]]]


def cycles_oracle(args):
    _, queries = args
    answer = []
    for first, second in queries:
        ancestors = {}
        steps = 0
        node = first
        while node:
            ancestors[node] = steps
            steps += 1
            node //= 2
        steps = 0
        node = second
        while node not in ancestors:
            steps += 1
            node //= 2
        answer.append(ancestors[node] + steps + 1)
    return answer


def random_cycles(rng):
    n = rng.randint(2, 15)
    maximum = (1 << n) - 1
    return [
        n,
        [
            [rng.randint(1, maximum), rng.randint(1, maximum)]
            for _ in range(rng.randint(1, 15))
        ],
    ]


def anagrams_oracle(args):
    result = 1
    for word in args[0].split():
        ways = factorial(len(word))
        for count in Counter(word).values():
            ways //= factorial(count)
        result = result * ways % (10**9 + 7)
    return result


def random_anagrams(rng):
    return [
        " ".join(
            "".join(rng.choice("abcde") for _ in range(rng.randint(1, 9)))
            for _ in range(rng.randint(1, 6))
        )
    ]


UNEQUAL = """\
def minimum_cost_to_make_arrays_unequal(nums1,nums2):
    counts={};same=cost=0
    for index,(left,right) in enumerate(zip(nums1,nums2)):
        if left==right:counts[left]=counts.get(left,0)+1;same+=1;cost+=index
    dominant=None;needed=0
    for value,count in counts.items():
        if count*2>same:dominant=value;needed=count*2-same;break
    for index,(left,right) in enumerate(zip(nums1,nums2)):
        if needed and left!=right and left!=dominant and right!=dominant:cost+=index;needed-=1
    return -1 if needed else cost
"""
POINTS = """\
def maximum_grid_query_points(grid,queries):
    import heapq
    height=len(grid);width=len(grid[0]);ordered=sorted((value,index) for index,value in enumerate(queries));answer=[0]*len(queries)
    heap=[(grid[0][0],0,0)];seen={(0,0)};count=0
    for limit,query_index in ordered:
        while heap and heap[0][0]<limit:
            _,row,column=heapq.heappop(heap);count+=1
            for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                r,c=row+dr,column+dc
                if 0<=r<height and 0<=c<width and (r,c) not in seen:seen.add((r,c));heapq.heappush(heap,(grid[r][c],r,c))
        answer[query_index]=count
    return answer
"""
EVEN_DEGREES = """\
def can_make_all_degrees_even(n,edges):
    graph=[set() for _ in range(n+1)]
    for left,right in edges:graph[left].add(right);graph[right].add(left)
    odd=[node for node in range(1,n+1) if len(graph[node])%2]
    if not odd:return True
    if len(odd)==2:
        left,right=odd
        if right not in graph[left]:return True
        return any(node not in (left,right) and node not in graph[left] and node not in graph[right] for node in range(1,n+1))
    if len(odd)==4:
        a,b,c,d=odd
        return (b not in graph[a] and d not in graph[c]) or (c not in graph[a] and d not in graph[b]) or (d not in graph[a] and c not in graph[b])
    return False
"""
CYCLES = """\
def added_edge_cycle_lengths(n,queries):
    answer=[]
    for first,second in queries:
        length=1
        while first!=second:
            if first>second:first//=2
            else:second//=2
            length+=1
        answer.append(length)
    return answer
"""
ANAGRAMS = """\
def count_wordwise_anagrams(s):
    modulus=10**9+7
    answer=1
    for word in s.split():
        counts={}
        numerator=denominator=1
        for index,character in enumerate(word,1):
            numerator=numerator*index%modulus
            counts[character]=counts.get(character,0)+1
            denominator=denominator*counts[character]%modulus
        answer=answer*numerator*pow(denominator,-1,modulus)%modulus
    return answer
"""

BATCH = {
    2499: entry(
        "minimum_cost_to_make_arrays_unequal",
        [("nums1", "list[int]"), ("nums2", "list[int]")],
        "int",
        ["arrays", "greedy", "counting"],
        [
            "Swap any two positions i and j in nums1 at cost i+j.",
            "After all swaps, nums1[i] must differ from nums2[i] at every index.",
            "Return the minimum total cost, or -1 when impossible.",
        ],
        [
            (
                [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                "Swapping positions among the five conflicts can resolve all of them with total minimum index cost ten.",
            ),
            (
                [[1, 2, 2], [1, 2, 2]],
                "Value two dominates the conflicting positions and no safe extra position exists, so the task is impossible.",
            ),
        ],
        [
            [a, b]
            for a, b in [
                ([1], [2]),
                ([1], [1]),
                ([1, 2], [2, 1]),
                ([1, 2], [1, 2]),
                ([1, 1], [1, 2]),
                ([1, 2, 3], [1, 2, 3]),
                ([1, 1, 2], [1, 2, 1]),
                ([1, 2, 2], [2, 2, 1]),
                ([1, 2, 3, 4], [1, 3, 2, 4]),
                ([1, 1, 2, 2], [1, 2, 1, 2]),
                ([1, 2, 1, 2], [1, 1, 2, 2]),
                ([1, 2, 3, 1], [1, 2, 1, 3]),
                ([2, 2, 3, 3, 4], [2, 3, 3, 4, 4]),
                ([1, 2, 3, 4, 5, 6], [1, 3, 2, 4, 6, 5]),
            ]
        ],
        UNEQUAL,
        [
            UNEQUAL.replace("cost+=index", "cost+=1"),
            UNEQUAL.replace("left!=dominant and right!=dominant", "left!=dominant"),
        ],
        [
            "Counts participating swaps instead of paying their required index costs.",
            "Uses an extra position whose nums2 value equals the dominant conflict value, so it cannot safely repair the conflict.",
        ],
        unequal_oracle,
        random_unequal,
        [
            "Collect indexes where the arrays currently match; every such index must participate, so add their indexes to the base cost.",
            "Count conflict values and find whether one occurs more than half the conflicts.",
            "If dominant, add the cheapest non-conflicting indexes whose values on both arrays differ from it until the excess is balanced.",
            "Non-dominant conflicts can be cyclically swapped among themselves; each dominant excess requires one safe outside index, and choosing them in index order minimizes added cost.",
        ],
        "O(n)",
        "O(n)",
        8,
    ),
    2503: entry(
        "maximum_grid_query_points",
        [("grid", "list[list[int]]"), ("queries", "list[int]")],
        "list[int]",
        ["matrices", "graphs", "heaps"],
        [
            "For each query, start at the top-left cell and visit four-directionally connected cells whose values are strictly less than the query.",
            "Each visited cell contributes one point and may be used once for that query.",
            "Return maximum point counts in original query order.",
        ],
        [
            (
                [[[1, 2, 3], [2, 5, 7], [3, 5, 1]], [5, 6, 2]],
                "Thresholds five, six, and two reach five, eight, and one cells respectively.",
            ),
            (
                [[[5]], [5, 6]],
                "A query equal to the start value reaches zero cells, while six reaches the one cell.",
            ),
        ],
        [
            [g, q]
            for g, q in [
                ([[1]], [1]),
                ([[1]], [2]),
                ([[2, 1]], [2, 3]),
                ([[1, 2], [3, 4]], [3]),
                ([[1, 100], [1, 1]], [2]),
                ([[5, 1], [1, 1]], [5, 6]),
                ([[1, 2, 3]], [2, 4]),
                ([[1], [2], [3]], [3, 4]),
                ([[3, 2], [1, 4]], [2, 3, 5]),
                ([[1, 9, 1], [1, 9, 1], [1, 1, 1]], [2, 10]),
                ([[0, 0], [0, 0]], [1]),
                ([[10, 1], [1, 1]], [2, 11]),
                ([[1, 4, 2], [2, 3, 5]], [4]),
                ([[2, 2, 2], [2, 1, 2], [2, 2, 2]], [2, 3]),
            ]
        ],
        POINTS,
        [
            POINTS.replace("heap[0][0]<limit", "heap[0][0]<=limit"),
            POINTS.replace("answer[query_index]=count", "answer.append(count)"),
        ],
        [
            "Uses a non-strict threshold and includes cells equal to the query.",
            "Appends answers in sorted-query order instead of restoring original order.",
        ],
        points_oracle,
        random_points,
        [
            "Sort queries while retaining their original indexes.",
            "Maintain a min-heap frontier from the top-left and permanently expand cells below the current threshold.",
            "As thresholds increase, reuse the reached set and write its count to the saved query index.",
            "The heap always exposes the smallest boundary cell; all and only cells below each threshold become reachable before that query is recorded.",
        ],
        "O((cells+queries) log(cells+queries))",
        "O(cells+queries)",
        8,
    ),
    2508: entry(
        "can_make_all_degrees_even",
        [("n", "int"), ("edges", "list[list[int]]")],
        "bool",
        ["graphs", "parity", "enumeration"],
        [
            "The graph is simple and undirected on nodes 1 through n.",
            "Add zero, one, or two new edges without self-loops or duplicate existing edges.",
            "Return whether every node can have even degree.",
        ],
        [
            (
                [5, [[1, 2], [2, 3], [3, 4], [4, 2], [1, 4], [2, 5]]],
                "The odd-degree nodes can be paired by valid missing edges using at most two additions.",
            ),
            (
                [4, [[1, 2], [1, 3], [1, 4]]],
                "Four odd nodes exist, but the required pairings among them are already edges, so two legal additions cannot fix all degrees.",
            ),
        ],
        [
            [n, e]
            for n, e in [
                (1, []),
                (2, []),
                (2, [[1, 2]]),
                (3, [[1, 2]]),
                (3, [[1, 2], [2, 3]]),
                (3, [[1, 2], [1, 3], [2, 3]]),
                (4, []),
                (4, [[1, 2], [3, 4]]),
                (4, [[1, 2], [2, 3]]),
                (5, [[1, 2], [1, 3], [1, 4], [1, 5]]),
                (5, [[1, 2], [2, 3], [3, 4], [4, 5]]),
                (6, [[1, 2], [3, 4], [5, 6]]),
                (4, [[1, 2], [1, 3], [2, 4], [3, 4]]),
                (5, [[1, 2], [2, 3], [3, 1], [4, 5]]),
            ]
        ],
        EVEN_DEGREES,
        [
            EVEN_DEGREES.replace("if not odd:return True", "if not odd:return False"),
            EVEN_DEGREES.replace(
                "return any(node not in (left,right) and node not in graph[left] and node not in graph[right] for node in range(1,n+1))",
                "return False",
            ),
        ],
        [
            "Rejects graphs whose degrees are already all even.",
            "When the odd vertices are adjacent, never tries a shared intermediate vertex.",
        ],
        even_degrees_oracle,
        random_even_degrees,
        [
            "Only odd-degree nodes need parity changes, and each added edge toggles exactly two endpoints.",
            "Zero odds already succeeds; two odds need their direct missing edge or a shared intermediate node.",
            "Four odds require one of the three pairings to consist of two missing edges.",
            "More than four odds cannot be fixed by two edges, while these enumerated cases cover every possible parity toggle pattern.",
        ],
        "O(n+edges)",
        "O(n+edges)",
        8,
    ),
    2509: entry(
        "added_edge_cycle_lengths",
        [("n", "int"), ("queries", "list[list[int]]")],
        "list[int]",
        ["trees", "lowest common ancestor"],
        [
            "Nodes 1 through 2^n-1 form the implicit complete binary tree with parent floor(node/2).",
            "For each query, temporarily add one edge between its two nodes.",
            "Return the resulting cycle length, including the added edge, for each query.",
        ],
        [
            (
                [3, [[5, 3], [4, 7], [2, 3]]],
                "Tree-path distances are three, four, and two; including the added edge gives [4,5,3].",
            ),
            (
                [2, [[1, 3]]],
                "The tree edge path from one to three has length one, so adding the same connection forms a two-edge cycle by the query definition.",
            ),
        ],
        [
            [n, q]
            for n, q in [
                (2, [[2, 3]]),
                (3, [[4, 5]]),
                (3, [[4, 6]]),
                (3, [[1, 7]]),
                (4, [[8, 15]]),
                (4, [[10, 11]]),
                (5, [[16, 31]]),
                (5, [[7, 14]]),
                (6, [[32, 1]]),
                (6, [[20, 45]]),
                (3, [[2, 4], [3, 7]]),
                (4, [[9, 14], [12, 13]]),
                (10, [[512, 1023]]),
                (3, [[5, 3], [4, 7], [2, 3]]),
            ]
        ],
        CYCLES,
        [
            CYCLES.replace("length=1", "length=0"),
            CYCLES.replace(
                "if first>second:first//=2\n            else:second//=2",
                "first//=2\n            second//=2",
            ),
        ],
        [
            "Omits the newly added edge from the cycle length.",
            "Moves both nodes together, which loses paths whose endpoints begin at different depths.",
        ],
        cycles_oracle,
        random_cycles,
        [
            "The cycle is the existing tree path plus the added edge.",
            "Repeatedly move the larger node label to its parent; in this heap labeling it is always at least as deep as the smaller current label.",
            "Count one for the added edge and one for every parent move until the nodes meet.",
            "The meeting node is their LCA and the parent moves count the exact tree-path edges, so the total is the cycle length.",
        ],
        "O(log nodes per query)",
        "O(1)",
        8,
    ),
    2514: entry(
        "count_wordwise_anagrams",
        [("s", "str")],
        "int",
        ["strings", "combinatorics"],
        [
            "Words are separated by single spaces and remain in their original word positions.",
            "Within each word, permute its letters independently.",
            "Return the number of distinct resulting sentences modulo 1,000,000,007.",
        ],
        [
            (
                ["too hot"],
                "too has three distinct permutations and hot has six, giving eighteen sentences.",
            ),
            (
                ["aa"],
                "Both letters are identical, so there is only one distinct permutation.",
            ),
        ],
        [
            [s]
            for s in [
                "a",
                "ab",
                "aa",
                "abc",
                "aab",
                "aba",
                "a a",
                "ab cd",
                "aa bb",
                "abc def",
                "too hot",
                "leetcode",
                "aabb cc",
                "abcde edcba",
            ]
        ],
        ANAGRAMS,
        [
            ANAGRAMS.replace(
                "denominator=denominator*counts[character]%modulus",
                "denominator=denominator*1%modulus",
            ),
            ANAGRAMS.replace(
                "answer=answer*numerator*pow(denominator,-1,modulus)%modulus",
                "answer=(answer+numerator*pow(denominator,-1,modulus))%modulus",
            ),
        ],
        [
            "Counts repeated letters as distinct choices.",
            "Adds per-word permutation counts instead of multiplying independent choices.",
        ],
        anagrams_oracle,
        random_anagrams,
        [
            "For each word, begin with factorial(word length).",
            "Divide by factorial(frequency) for every repeated character to remove indistinguishable permutations.",
            "Multiply the independent per-word counts and reduce modulo the prime.",
            "The multinomial coefficient counts each word exactly, and the product rule combines independent word positions.",
        ],
        "O(total letters+alphabet per word)",
        "O(alphabet)",
        8,
    ),
}
