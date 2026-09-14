"""Shortest-path, tree, matrix, and prefix workbook batch 146."""

from collections import deque
from .import_batch_055 import entry


def apples_oracle(args):
    n, roads, costs, k = args
    inf = 10**12
    distance = [[inf] * n for _ in range(n)]
    for i in range(n):
        distance[i][i] = 0
    for a, b, w in roads:
        a -= 1
        b -= 1
        distance[a][b] = distance[b][a] = min(distance[a][b], w)
    for mid in range(n):
        for left in range(n):
            for right in range(n):
                distance[left][right] = min(
                    distance[left][right], distance[left][mid] + distance[mid][right]
                )
    return [
        min(costs[target] + distance[start][target] * (k + 1) for target in range(n))
        for start in range(n)
    ]


def random_apples(rng):
    n = rng.randint(2, 9)
    roads = [
        [node + 1, rng.randrange(node) + 1, rng.randint(1, 15)] for node in range(1, n)
    ]
    existing = {(min(a, b), max(a, b)) for a, b, _ in roads}
    for _ in range(rng.randint(0, n)):
        a, b = rng.sample(range(1, n + 1), 2)
        key = (min(a, b), max(a, b))
        if key not in existing:
            roads.append([a, b, rng.randint(1, 15)])
            existing.add(key)
    return [n, roads, [rng.randint(1, 100) for _ in range(n)], rng.randint(0, 5)]


def fuel_oracle(args):
    roads, seats = args
    n = len(roads) + 1
    graph = [[] for _ in range(n)]
    for a, b in roads:
        graph[a].append(b)
        graph[b].append(a)
    parent = [-1] * n
    order = [0]
    for node in order:
        for child in graph[node]:
            if child != parent[node]:
                parent[child] = node
                order.append(child)
    people = [1] * n
    fuel = 0
    for node in reversed(order[1:]):
        fuel += (people[node] + seats - 1) // seats
        people[parent[node]] += people[node]
    return fuel


def random_fuel(rng):
    n = rng.randint(1, 30)
    return [[[node, rng.randrange(node)] for node in range(1, n)], rng.randint(1, 8)]


def matrix_oracle(args):
    grid = args[0]
    height = len(grid)
    width = len(grid[0])
    answer = []
    for row in range(height):
        line = []
        for column in range(width):
            ones = sum(grid[row]) + sum(grid[r][column] for r in range(height))
            line.append(ones - (width + height - ones))
        answer.append(line)
    return answer


def random_matrix(rng):
    h = rng.randint(1, 10)
    w = rng.randint(1, 10)
    return [[[rng.randrange(2) for _ in range(w)] for _ in range(h)]]


def closing_oracle(args):
    text = args[0]
    penalties = []
    for hour in range(len(text) + 1):
        penalties.append(
            sum(c == "N" for c in text[:hour]) + sum(c == "Y" for c in text[hour:])
        )
    return min(range(len(penalties)), key=lambda hour: (penalties[hour], hour))


def random_closing(rng):
    return ["".join(rng.choice("YN") for _ in range(rng.randint(1, 40)))]


def append_oracle(args):
    source, target = args
    for matched in range(len(target), -1, -1):
        iterator = iter(source)
        if all(any(char == wanted for char in iterator) for wanted in target[:matched]):
            return len(target) - matched


def random_append(rng):
    return [
        "".join(rng.choice("abcde") for _ in range(rng.randint(1, 30))),
        "".join(rng.choice("abcde") for _ in range(rng.randint(1, 30))),
    ]


APPLES = """\
def minimum_apple_costs(n,roads,apple_cost,k):
    import heapq
    graph=[[] for _ in range(n)]
    for left,right,weight in roads:
        left-=1;right-=1;graph[left].append((right,weight));graph[right].append((left,weight))
    answer=[]
    for start in range(n):
        distance=[10**30]*n;distance[start]=0;heap=[(0,start)];best=10**30
        while heap:
            current,node=heapq.heappop(heap)
            if current!=distance[node]:continue
            best=min(best,apple_cost[node]+current*(k+1))
            for neighbor,weight in graph[node]:
                candidate=current+weight
                if candidate<distance[neighbor]:distance[neighbor]=candidate;heapq.heappush(heap,(candidate,neighbor))
        answer.append(best)
    return answer
"""
FUEL = """\
def minimum_fuel_to_capital(roads,seats):
    graph=[[] for _ in range(len(roads)+1)]
    for left,right in roads:graph[left].append(right);graph[right].append(left)
    fuel=0
    def visit(node,parent):
        nonlocal fuel
        people=1
        for child in graph[node]:
            if child!=parent:people+=visit(child,node)
        if node:fuel+=(people+seats-1)//seats
        return people
    visit(0,-1);return fuel
"""
MATRIX = """\
def ones_minus_zeros_matrix(grid):
    height=len(grid);width=len(grid[0]);rows=[sum(row) for row in grid];columns=[sum(grid[row][column] for row in range(height)) for column in range(width)]
    return [[2*(rows[row]+columns[column])-height-width for column in range(width)] for row in range(height)]
"""
CLOSING = """\
def earliest_minimum_penalty_closing(customers):
    penalty=customers.count('Y');best=penalty;answer=0
    for hour,customer in enumerate(customers,1):
        penalty+=1 if customer=='N' else -1
        if penalty<best:best=penalty;answer=hour
    return answer
"""
APPEND = """\
def minimum_appended_characters(s,t):
    matched=0
    for character in s:
        if matched<len(t) and character==t[matched]:matched+=1
    return len(t)-matched
"""

BATCH = {
    2473: entry(
        "minimum_apple_costs",
        [
            ("n", "int"),
            ("roads", "list[list[int]]"),
            ("apple_cost", "list[int]"),
            ("k", "int"),
        ],
        "list[int]",
        ["graphs", "shortest paths", "heaps"],
        [
            "Cities are numbered 1 through n and roads are undirected weighted edges.",
            "Starting from each city, buy one apple in any city and include round-trip travel priced at (k+1) times the one-way shortest distance.",
            "Return the minimum total cost for every starting city.",
        ],
        [
            (
                [
                    4,
                    [[1, 2, 4], [2, 3, 2], [2, 4, 5], [3, 4, 1], [1, 3, 4]],
                    [56, 42, 102, 301],
                    2,
                ],
                "Comparing local purchases with shortest-path travel gives costs [54,42,48,51].",
            ),
            (
                [2, [[1, 2, 3]], [10, 1], 1],
                "City 1 can travel to city 2 and buy for total 1+2*3=7, while city 2 buys locally for one.",
            ),
        ],
        [
            [n, r, a, k]
            for n, r, a, k in [
                (1, [], [5], 0),
                (2, [[1, 2, 1]], [5, 10], 0),
                (2, [[1, 2, 1]], [5, 10], 2),
                (3, [[1, 2, 2], [2, 3, 2]], [9, 8, 1], 1),
                (3, [[1, 2, 5], [1, 3, 1]], [20, 3, 10], 2),
                (4, [[1, 2, 1], [2, 3, 1], [3, 4, 1]], [9, 9, 9, 1], 1),
                (4, [[1, 2, 10], [1, 3, 2], [3, 4, 2]], [1, 50, 50, 50], 3),
                (3, [[1, 2, 4], [2, 3, 4], [1, 3, 1]], [10, 2, 9], 0),
                (
                    5,
                    [[1, 2, 1], [2, 3, 2], [3, 4, 3], [4, 5, 4]],
                    [30, 20, 10, 5, 1],
                    2,
                ),
                (2, [[1, 2, 100]], [1, 2], 5),
                (4, [[1, 2, 2], [2, 3, 2], [3, 4, 2], [4, 1, 2]], [7, 6, 5, 4], 1),
                (3, [[1, 2, 1], [2, 3, 1]], [0, 5, 9], 4),
                (5, [[1, 2, 5], [1, 3, 5], [1, 4, 5], [1, 5, 5]], [100, 1, 2, 3, 4], 1),
                (3, [[1, 2, 3], [2, 3, 3]], [8, 8, 8], 2),
            ]
        ],
        APPLES,
        [
            APPLES.replace("current*(k+1)", "current*k"),
            APPLES.replace("graph[right].append((left,weight))", ""),
        ],
        [
            "Charges only k times distance instead of the required outbound-plus-return factor k+1.",
            "Treats undirected roads as one-way edges.",
        ],
        apples_oracle,
        random_apples,
        [
            "Build an undirected adjacency list.",
            "Run Dijkstra from each starting city.",
            "For every settled city, combine its apple price with shortest distance times k+1 and keep the minimum.",
            "Dijkstra supplies exact nonnegative shortest paths, and evaluating every purchase city gives the exact best total for each start.",
        ],
        "O(n*(roads log n))",
        "O(n+roads)",
        6,
    ),
    2477: entry(
        "minimum_fuel_to_capital",
        [("roads", "list[list[int]]"), ("seats", "int")],
        "int",
        ["trees", "recursion", "postorder traversal"],
        [
            "Cities form a tree rooted at capital 0, and every non-capital city has one representative and one seats-capacity car.",
            "Representatives may share cars; moving one car across one road costs one liter.",
            "Return the minimum fuel needed to bring every representative to city 0.",
        ],
        [
            (
                [[[0, 1], [0, 2], [0, 3]], 5],
                "Each leaf requires one car across its edge to the capital, totaling three liters.",
            ),
            (
                [[[0, 1], [1, 2], [1, 3]], 2],
                "Three representatives below edge 0-1 need two cars there, while edges from 2 and 3 each need one, totaling four.",
            ),
        ],
        [
            [r, s]
            for r, s in [
                ([], 1),
                ([[0, 1]], 1),
                ([[0, 1]], 5),
                ([[0, 1], [0, 2]], 2),
                ([[0, 1], [1, 2]], 2),
                ([[0, 1], [1, 2], [2, 3]], 2),
                ([[0, 1], [0, 2], [0, 3], [0, 4]], 3),
                ([[0, 1], [1, 2], [1, 3], [3, 4]], 2),
                ([[0, 1], [1, 2], [2, 3], [3, 4]], 5),
                ([[0, 1], [0, 2], [2, 3], [2, 4]], 1),
                ([[0, 1], [1, 2], [1, 3], [1, 4]], 3),
                ([[0, 1], [1, 2], [0, 3], [3, 4]], 2),
                ([[0, 1], [1, 2], [2, 3], [2, 4], [4, 5]], 4),
                ([[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]], 2),
            ]
        ],
        FUEL,
        [
            FUEL.replace("(people+seats-1)//seats", "people//seats"),
            FUEL.replace("if node:fuel+=", "fuel+="),
        ],
        [
            "Rounds the required car count down instead of up.",
            "Charges fuel at the capital even though no edge remains to cross.",
        ],
        fuel_oracle,
        random_fuel,
        [
            "Postorder traversal returns the number of representatives in each subtree.",
            "Across a non-root node’s parent edge, ceil(people/seats) cars are necessary and sufficient.",
            "Add that cost once per edge while merging child subtree sizes.",
            "Every representative has a unique route to the root, and maximal car sharing on each edge realizes the ceiling lower bound independently.",
        ],
        "O(n)",
        "O(tree height)",
        5,
    ),
    2482: entry(
        "ones_minus_zeros_matrix",
        [("grid", "list[list[int]]")],
        "list[list[int]]",
        ["matrices", "counting"],
        [
            "For every cell, compute row ones + column ones - row zeros - column zeros.",
            "The cell itself participates once through its row and once through its column.",
            "Return the full difference matrix with the same shape.",
        ],
        [
            (
                [[[0, 1, 1], [1, 0, 1], [0, 0, 1]]],
                "Row and column counts produce [[0,0,4],[0,0,4],[-2,-2,2]].",
            ),
            (
                [[[1, 1]]],
                "The row has two ones and each column one, with no zeros, so both entries equal three.",
            ),
        ],
        [
            [g]
            for g in [
                [[0]],
                [[1]],
                [[0, 0]],
                [[1, 0]],
                [[1], [0]],
                [[1, 1], [1, 1]],
                [[0, 0], [0, 0]],
                [[1, 0], [0, 1]],
                [[1, 1, 0], [0, 1, 0]],
                [[1], [1], [0]],
                [[0, 1, 0, 1]],
                [[1, 0, 1], [1, 0, 1]],
                [[0, 0, 1], [1, 1, 0], [1, 0, 0]],
                [[1, 0], [1, 0], [0, 1]],
            ]
        ],
        MATRIX,
        [
            MATRIX.replace("-height-width", "-height"),
            MATRIX.replace("rows[row]+columns[column]", "rows[row]-columns[column]"),
        ],
        [
            "Subtracts only row width/height terms and omits column zero counts.",
            "Subtracts column ones instead of adding them.",
        ],
        matrix_oracle,
        random_matrix,
        [
            "Count ones once for every row and column.",
            "Row zeros equal width-row_ones, and column zeros equal height-column_ones.",
            "Substitute those values to obtain 2*(row_ones+column_ones)-height-width.",
            "The formula is algebraically identical to the definition and fills each output cell in constant time after preprocessing.",
        ],
        "O(m*n)",
        "O(m+n)",
        5,
    ),
    2483: entry(
        "earliest_minimum_penalty_closing",
        [("customers", "str")],
        "int",
        ["strings", "prefix sums"],
        [
            "Closing at hour j means the shop is open during positions before j and closed from j onward.",
            "Penalty adds one for each open N and each closed Y.",
            "Return the earliest hour from 0 through len(customers) attaining minimum penalty.",
        ],
        [
            (
                ["YYNY"],
                "Closing after hour two incurs only the final Y while closed, giving the earliest minimum penalty.",
            ),
            (
                ["NNNN"],
                "Closing immediately at hour zero avoids every open-without-customer penalty.",
            ),
        ],
        [
            [s]
            for s in [
                "Y",
                "N",
                "YY",
                "NN",
                "YN",
                "NY",
                "YYY",
                "NNN",
                "YNY",
                "NYN",
                "YYNN",
                "NNYY",
                "YNNY",
                "NYYN",
            ]
        ],
        CLOSING,
        [
            CLOSING.replace("penalty<best", "penalty<=best"),
            CLOSING.replace("1 if customer=='N' else -1", "1 if customer=='Y' else -1"),
        ],
        [
            "Updates on equal penalties and returns the latest rather than earliest optimum.",
            "Reverses the penalty changes for open N and newly served Y hours.",
        ],
        closing_oracle,
        random_closing,
        [
            "Start with closing at hour zero, whose penalty is the total number of Y hours.",
            "Moving closing one hour later adds one for N or removes one for Y.",
            "Update the answer only when the penalty strictly improves.",
            "The scan computes every closing hour’s penalty incrementally, and strict updates preserve the earliest minimum.",
        ],
        "O(n)",
        "O(1)",
        3,
    ),
    2486: entry(
        "minimum_appended_characters",
        [("s", "str"), ("t", "str")],
        "int",
        ["strings", "two pointers"],
        [
            "Append characters only to the end of s.",
            "After appending, t must be a subsequence of the resulting string.",
            "Return the minimum number of appended characters.",
        ],
        [
            (
                ["coaching", "coding"],
                "Scanning coaching matches only the prefix co of coding, so the four-character suffix ding must be appended.",
            ),
            (
                ["abcde", "a"],
                "The target is already a subsequence, so no characters are appended.",
            ),
        ],
        [
            [s, t]
            for s, t in [
                ("a", "a"),
                ("a", "b"),
                ("abc", "abc"),
                ("abc", "abcd"),
                ("abc", "ac"),
                ("abc", "ca"),
                ("aaaa", "aaa"),
                ("xyz", "xzy"),
                ("", "abc"),
                ("abc", ""),
                ("leetcode", "code"),
                ("axbycz", "abc"),
                ("hello", "world"),
                ("subsequence", "sue"),
            ]
        ],
        APPEND,
        [
            APPEND.replace("character==t[matched]", "character in t[matched:]"),
            APPEND.replace("return len(t)-matched", "return matched"),
        ],
        [
            "Accepts any later target character and can skip unmatched target-prefix positions.",
            "Returns the matched prefix length instead of the remaining append count.",
        ],
        append_oracle,
        random_append,
        [
            "Greedily match the next unmatched target character while scanning s left to right.",
            "The scan length is the longest prefix of t already present as a subsequence of s.",
            "Only the unmatched suffix of t must be appended, in its existing order.",
            "Greedy earliest matches leave the most source characters available for later target positions, so no other matching can cover a longer prefix.",
        ],
        "O(len(s)+len(t))",
        "O(1)",
        3,
    ),
}
