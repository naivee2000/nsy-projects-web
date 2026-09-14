"""Prefix divisibility, greedy pairing, timed grids, geometry, and intervals batch 159."""

from collections import deque
from itertools import combinations

from .import_batch_055 import entry


def divisibility_oracle(args):
    word, divisor = args
    return [int(int(word[: index + 1]) % divisor == 0) for index in range(len(word))]


def random_divisibility(rng):
    return [
        "".join(rng.choice("0123456789") for _ in range(rng.randint(1, 18))),
        rng.randint(1, 1000),
    ]


def marked_oracle(args):
    nums = args[0]
    best = 0

    def visit(remaining, count):
        nonlocal best
        best = max(best, count)
        for first, second in combinations(range(len(remaining)), 2):
            low, high = sorted((remaining[first], remaining[second]))
            if 2 * low <= high:
                visit(
                    [
                        value
                        for index, value in enumerate(remaining)
                        if index not in (first, second)
                    ],
                    count + 2,
                )

    visit(nums, 0)
    return best


def random_marked(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 10))]]


def timed_oracle(args):
    grid = args[0]
    rows, columns = len(grid), len(grid[0])
    queue = deque([(0, 0, 0)])
    seen = {(0, 0, 0)}
    limit = max(max(row) for row in grid) + 2 * rows * columns + 5
    while queue:
        time, row, column = queue.popleft()
        if (row, column) == (rows - 1, columns - 1):
            return time
        if time >= limit:
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            r, c = row + dr, column + dc
            state = (time + 1, r, c)
            if (
                0 <= r < rows
                and 0 <= c < columns
                and time + 1 >= grid[r][c]
                and state not in seen
            ):
                seen.add(state)
                queue.append(state)
    return -1


def random_timed(rng):
    rows, columns = rng.randint(2, 5), rng.randint(2, 5)
    grid = [[rng.randint(0, 12) for _ in range(columns)] for _ in range(rows)]
    grid[0][0] = 0
    return [grid]


def colored_oracle(args):
    minute = args[0]
    if minute > 100:
        # The 500 seeded cases use explicit geometric enumeration; this closed
        # form keeps source-scale deterministic boundaries bounded.
        return 1 + 2 * minute * (minute - 1)
    radius = minute - 1
    return sum(
        abs(row) + abs(column) <= radius
        for row in range(-radius, radius + 1)
        for column in range(-radius, radius + 1)
    )


def random_colored(rng):
    return [rng.randint(1, 30)]


def ranges_oracle(args):
    ranges = args[0]
    graph = [[] for _ in ranges]
    for first, second in combinations(range(len(ranges)), 2):
        if max(ranges[first][0], ranges[second][0]) <= min(
            ranges[first][1], ranges[second][1]
        ):
            graph[first].append(second)
            graph[second].append(first)
    components = 0
    seen = set()
    for start in range(len(ranges)):
        if start in seen:
            continue
        components += 1
        stack = [start]
        seen.add(start)
        while stack:
            for neighbor in graph[stack.pop()]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return pow(2, components, 10**9 + 7)


def random_ranges(rng):
    result = []
    for _ in range(rng.randint(1, 14)):
        left = rng.randint(0, 30)
        result.append([left, left + rng.randint(0, 10)])
    return [result]


DIVISIBILITY = """\
def prefix_divisibility_array(word,m):
    remainder=0;answer=[]
    for digit in word:
        remainder=(remainder*10+int(digit))%m
        answer.append(1 if remainder==0 else 0)
    return answer
"""

MARKED = """\
def maximum_marked_indices(nums):
    nums=sorted(nums);left=0
    for right in range((len(nums)+1)//2,len(nums)):
        if 2*nums[left]<=nums[right]:left+=1
    return 2*left
"""

TIMED = """\
def minimum_timed_grid_visit(grid):
    import heapq
    rows=len(grid);columns=len(grid[0])
    if grid[0][1]>1 and grid[1][0]>1:return -1
    distance=[[10**30]*columns for _ in range(rows)];distance[0][0]=0;heap=[(0,0,0)]
    while heap:
        time,row,column=heapq.heappop(heap)
        if time!=distance[row][column]:continue
        if (row,column)==(rows-1,columns-1):return time
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            r,c=row+dr,column+dc
            if 0<=r<rows and 0<=c<columns:
                arrival=time+1
                if arrival<grid[r][c]:arrival=grid[r][c]+(grid[r][c]-arrival)%2
                if arrival<distance[r][c]:distance[r][c]=arrival;heapq.heappush(heap,(arrival,r,c))
"""

COLORED = """\
def total_colored_cells(n):
    return 1+2*n*(n-1)
"""

RANGES = """\
def count_overlapping_range_groups(ranges):
    components=0;farthest=-1
    for start,end in sorted(ranges):
        if start>farthest:components+=1
        farthest=max(farthest,end)
    return pow(2,components,10**9+7)
"""


BATCH = {
    2575: entry(
        "prefix_divisibility_array",
        [("word", "str"), ("m", "int")],
        "list[int]",
        ["strings", "math", "modular arithmetic"],
        [
            "word is a nonempty decimal digit string and m is positive.",
            "Output one value per prefix: one when its decimal integer is divisible by m, otherwise zero.",
            "Do not convert the entire potentially long word to an integer.",
        ],
        [
            (
                ["998244353", 3],
                "Running remainders show prefixes 9, 99, 998244, and 9982443 are divisible by three.",
            ),
            (
                ["1010", 10],
                "Prefixes 10 and 1010 are divisible by ten, yielding [0,1,0,1].",
            ),
        ],
        [
            [w, m]
            for w, m in [
                ("0", 1),
                ("0", 7),
                ("1", 1),
                ("10", 2),
                ("10", 3),
                ("123", 3),
                ("123", 7),
                ("1000", 10),
                ("99999", 9),
                ("314159", 11),
                ("00012", 4),
                ("808080", 8),
                ("123456789", 37),
                ("100000000000000000", 97),
            ]
        ],
        DIVISIBILITY,
        [
            DIVISIBILITY.replace("remainder*10", "remainder"),
            DIVISIBILITY.replace("==0", "!=0"),
        ],
        [
            "Adds digits without shifting the previous decimal prefix by ten.",
            "Marks non-divisible prefixes instead of divisible ones.",
        ],
        divisibility_oracle,
        random_divisibility,
        [
            "Only the prefix remainder modulo m is needed.",
            "Appending digit d changes remainder r to (10r+d) modulo m.",
            "Append one exactly when the updated remainder is zero.",
            "Modular arithmetic preserves divisibility while keeping every intermediate bounded regardless of word length.",
        ],
        "O(word length)",
        "O(output length)",
        5,
    ),
    2576: entry(
        "maximum_marked_indices",
        [("nums", "list[int]")],
        "int",
        ["arrays", "greedy", "two pointers", "sorting"],
        [
            "A marking operation pairs two currently unmarked indices whose values can be ordered as 2*small <= large.",
            "Each index may be marked once.",
            "Return the maximum number of marked indices.",
        ],
        [
            (
                [[3, 5, 2, 4]],
                "After sorting, pair two with four; no second valid disjoint pair exists, so two indices are marked.",
            ),
            (
                [[9, 2, 5, 4]],
                "Pairs two with five and four with nine mark all four indices.",
            ),
        ],
        [
            [a]
            for a in [
                [1],
                [1, 2],
                [2, 3],
                [1, 2, 3],
                [1, 2, 4],
                [1, 1, 2, 2],
                [5, 5, 5, 5],
                [1, 3, 6, 12],
                [2, 4, 8, 16, 32],
                [10, 1, 2, 20],
                [3, 3, 6, 7, 8, 9],
                [1, 2, 2, 3, 4, 8],
                [7, 1, 14, 2, 28, 4],
                [5, 10, 11, 20, 21, 40],
            ]
        ],
        MARKED,
        [
            MARKED.replace("2*nums[left]<=", "2*nums[left]<"),
            MARKED.replace("(len(nums)+1)//2", "len(nums)//2"),
        ],
        [
            "Rejects pairs meeting the inequality exactly.",
            "Starts the large half too early for odd-length arrays, allowing one index to serve both roles.",
        ],
        marked_oracle,
        random_marked,
        [
            "Sort values and reserve a lower half as small candidates and an upper half as large candidates.",
            "Scan large candidates in order, pairing each with the earliest still-unpaired small value it can satisfy.",
            "Advance the small pointer only after a successful pair.",
            "Using the smallest available partner preserves larger small values for later, while the half split guarantees disjoint indices and maximum pair count.",
        ],
        "O(n log n)",
        "O(n)",
        6,
    ),
    2577: entry(
        "minimum_timed_grid_visit",
        [("grid", "list[list[int]]")],
        "int",
        ["matrices", "graphs", "shortest paths", "heaps"],
        [
            "Start at (0,0) at time zero and move one orthogonal cell every second; waiting in place is forbidden.",
            "A cell may be entered only at a time at least its grid value.",
            "Return the earliest bottom-right arrival, or -1 when the first move is impossible.",
        ],
        [
            (
                [[[0, 1, 3, 2], [5, 1, 2, 5], [4, 3, 8, 6]]],
                "Shortest-path search with parity-adjusted waits reaches the destination at time seven.",
            ),
            (
                [[[0, 2], [2, 0]]],
                "Neither neighbor can be entered at time one, so movement cannot begin.",
            ),
        ],
        [
            [g]
            for g in [
                [[0, 1], [1, 0]],
                [[0, 1], [3, 2]],
                [[0, 2], [1, 3]],
                [[0, 1, 5], [1, 2, 3]],
                [[0, 1], [1, 2], [4, 3]],
                [[0, 1, 4], [2, 3, 5]],
                [[0, 1, 2], [1, 2, 3], [2, 3, 4]],
                [[0, 1, 10], [1, 2, 3], [2, 3, 4]],
                [[0, 5, 1], [1, 2, 3], [4, 5, 6]],
                [[0, 1, 3, 4], [1, 2, 5, 6]],
                [[0, 1, 8], [1, 2, 7], [2, 3, 6]],
                [[0, 1], [1, 10]],
                [[0, 1, 2, 9], [1, 4, 3, 8], [2, 5, 6, 7]],
                [[0, 1, 6], [5, 2, 7], [4, 3, 8]],
            ]
        ],
        TIMED,
        [
            TIMED.replace("grid[r][c]+(grid[r][c]-arrival)%2", "grid[r][c]"),
            TIMED.replace(
                "grid[0][1]>1 and grid[1][0]>1", "grid[0][1]>1 or grid[1][0]>1"
            ),
        ],
        [
            "Waits directly in place and ignores the parity forced by moving back and forth.",
            "Declares failure when either first neighbor is blocked instead of when both are blocked.",
        ],
        timed_oracle,
        random_timed,
        [
            "If both starting neighbors require time beyond one, there is nowhere to move and the answer is -1.",
            "Otherwise use Dijkstra because reaching a cell earlier never harms future options.",
            "When a neighbor opens too late, oscillation adds time in steps of two; choose the first allowed time with the needed parity.",
            "The adjusted edge arrival is the earliest feasible arrival from the current state, so Dijkstra finalizes the globally earliest destination time.",
        ],
        "O(rows times columns log cells)",
        "O(rows times columns)",
        8,
    ),
    2579: entry(
        "total_colored_cells",
        [("n", "int")],
        "int",
        ["math", "geometry", "patterns"],
        [
            "At minute one only the center cell is colored.",
            "Each later minute colors every uncolored edge-adjacent cell of the existing region.",
            "Return the total colored cells after minute n.",
        ],
        [
            ([1], "Only the initial center is colored."),
            ([2], "The center and its four orthogonal neighbors give five cells."),
        ],
        [[n] for n in [3, 4, 5, 6, 7, 8, 9, 10, 20, 50, 100, 999, 1000, 100000]],
        COLORED,
        [COLORED.replace("2*n*(n-1)", "n*(n-1)"), COLORED.replace("n-1", "n")],
        [
            "Adds only half of each diamond ring.",
            "Uses radius n rather than n-1 and counts one extra ring.",
        ],
        colored_oracle,
        random_colored,
        [
            "After n minutes the region is a Manhattan-distance diamond of radius n-1.",
            "Ring radius r contains 4r cells for r>0.",
            "Sum one plus 4 times the integers from one through n-1.",
            "The arithmetic-series sum simplifies to 1+2n(n-1), matching every diamond layer exactly.",
        ],
        "O(1)",
        "O(1)",
        5,
    ),
    2580: entry(
        "count_overlapping_range_groups",
        [("ranges", "list[list[int]]")],
        "int",
        ["intervals", "sorting", "connected components"],
        [
            "Assign every closed interval to one of two labeled groups.",
            "Any directly or transitively overlapping intervals must be in the same group.",
            "Return the number of valid assignments modulo 1,000,000,007.",
        ],
        [
            (
                [[[6, 10], [5, 15]]],
                "The ranges overlap into one component, which may independently choose either group.",
            ),
            (
                [[[1, 3], [10, 20], [2, 5], [4, 8]]],
                "The first, third, and fourth ranges connect, while the second is separate, giving four assignments.",
            ),
        ],
        [
            [r]
            for r in [
                [[1, 1]],
                [[1, 2], [3, 4]],
                [[1, 2], [2, 3]],
                [[1, 5], [2, 3]],
                [[1, 2], [2, 3], [3, 4]],
                [[1, 10], [20, 30], [40, 50]],
                [[5, 7], [1, 3], [3, 5]],
                [[1, 4], [2, 6], [8, 10]],
                [[0, 0], [0, 0]],
                [[1, 100], [20, 30], [40, 50]],
                [[2, 3], [1, 2], [5, 8], [7, 9]],
                [[10, 20], [1, 5], [4, 11]],
                [[1, 2], [4, 5], [7, 8], [10, 11]],
                [[3, 9], [1, 2], [2, 4], [10, 12], [12, 15]],
            ]
        ],
        RANGES,
        [
            RANGES.replace("start>farthest", "start>=farthest"),
            RANGES.replace("pow(2,components", "pow(2,components-1"),
        ],
        [
            "Treats intervals touching at an endpoint as separate components.",
            "Returns only half of the two-group assignments.",
        ],
        ranges_oracle,
        random_ranges,
        [
            "Sort intervals by start and sweep while tracking the farthest end of the current overlap component.",
            "A start beyond that farthest end begins a new independent component.",
            "Each connected component must be assigned wholly to one group but has two labeled choices.",
            "Components are independent, so c components produce 2^c valid assignments.",
        ],
        "O(n log n)",
        "O(n)",
        6,
    ),
}
