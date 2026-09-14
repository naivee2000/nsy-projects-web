"""Heap simulation, time search, bit counting, knight tours, and subsets batch 162."""

from itertools import combinations
from math import isqrt

from .import_batch_055 import entry


def marking_oracle(args):
    nums = args[0]
    marked = set()
    score = 0
    while len(marked) < len(nums):
        index = min(
            (i for i in range(len(nums)) if i not in marked), key=lambda i: (nums[i], i)
        )
        score += nums[index]
        marked.update(i for i in (index - 1, index, index + 1) if 0 <= i < len(nums))
    return score


def random_marking(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 20))]]


def repair_oracle(args):
    ranks, cars = args
    time = 0
    while sum(isqrt(time // rank) for rank in ranks) < cars:
        time += 1
    return time


def random_repair(rng):
    return [[rng.randint(1, 8) for _ in range(rng.randint(1, 7))], rng.randint(1, 30)]


def bits_oracle(args):
    value = args[0]
    result = [0, 0]
    for index, bit in enumerate(reversed(bin(value)[2:])):
        result[index % 2] += bit == "1"
    return result


def random_bits(rng):
    return [rng.randint(1, 10**9)]


def knight_oracle(args):
    grid = args[0]
    positions = {}
    for row, values in enumerate(grid):
        for column, value in enumerate(values):
            positions[value] = (row, column)
    if positions.get(0) != (0, 0) or set(positions) != set(range(len(grid) ** 2)):
        return False
    return all(
        sorted(
            (
                abs(positions[step][0] - positions[step - 1][0]),
                abs(positions[step][1] - positions[step - 1][1]),
            )
        )
        == [1, 2]
        for step in range(1, len(grid) ** 2)
    )


def random_knight(rng):
    n = rng.randint(1, 6)
    values = list(range(n * n))
    rng.shuffle(values)
    return [[values[row * n : (row + 1) * n] for row in range(n)]]


def subsets_oracle(args):
    nums, k = args
    answer = 0
    for mask in range(1, 1 << len(nums)):
        chosen = [nums[index] for index in range(len(nums)) if mask >> index & 1]
        answer += all(abs(a - b) != k for a, b in combinations(chosen, 2))
    return answer


def random_subsets(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(1, 14))], rng.randint(1, 8)]


MARKING = """\
def score_after_marking(nums):
    import heapq
    heap=[(value,index) for index,value in enumerate(nums)];heapq.heapify(heap);marked=set();score=0
    while heap:
        value,index=heapq.heappop(heap)
        if index in marked:continue
        score+=value;marked.update((index-1,index,index+1))
    return score
"""

REPAIR = """\
def minimum_car_repair_time(ranks,cars):
    import math
    def possible(time):return sum(math.isqrt(time//rank) for rank in ranks)>=cars
    low=0;high=min(ranks)*cars*cars
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return low
"""

BITS = """\
def count_even_odd_set_bits(n):
    result=[0,0];index=0
    while n:
        result[index]+=n&1;n>>=1;index^=1
    return result
"""

KNIGHT = """\
def valid_knight_tour(grid):
    n=len(grid)
    if grid[0][0]!=0:return False
    positions=[None]*(n*n)
    for row in range(n):
        for column in range(n):positions[grid[row][column]]=(row,column)
    for first,second in zip(positions,positions[1:]):
        dr=abs(first[0]-second[0]);dc=abs(first[1]-second[1])
        if (dr,dc) not in ((1,2),(2,1)):return False
    return True
"""

SUBSETS = """\
def count_beautiful_difference_subsets(nums,k):
    counts={};answer=-1
    def visit(index):
        nonlocal answer
        if index==len(nums):answer+=1;return
        visit(index+1);value=nums[index]
        if counts.get(value-k,0)==0 and counts.get(value+k,0)==0:
            counts[value]=counts.get(value,0)+1;visit(index+1);counts[value]-=1
    visit(0)
    return answer
"""


BATCH = {
    2593: entry(
        "score_after_marking",
        [("nums", "list[int]")],
        "int",
        ["arrays", "heaps", "simulation"],
        [
            "Repeatedly select the smallest unmarked value, breaking ties by smallest index.",
            "Add it to the score and mark that index and its existing neighbors.",
            "Return the score after every index is marked.",
        ],
        [
            (
                [[2, 1, 3, 4, 5, 2]],
                "Select values one, two, and four at indices one, five, and three for total score seven.",
            ),
            ([[2, 3, 5, 1, 3, 2]], "The required marking order produces score five."),
        ],
        [
            [a]
            for a in [
                [1],
                [1, 2],
                [2, 1],
                [1, 1],
                [1, 2, 3],
                [3, 2, 1],
                [2, 2, 2],
                [5, 1, 5],
                [1, 3, 2, 4],
                [4, 1, 3, 1, 4],
                [5, 4, 3, 2, 1],
                [1, 5, 2, 5, 1],
                [7, 3, 9, 2, 8, 1],
                [2, 1, 2, 1, 2, 1, 2],
            ]
        ],
        MARKING,
        [
            MARKING.replace("(value,index)", "(-value,index)"),
            MARKING.replace(
                "marked.update((index-1,index,index+1))", "marked.add(index)"
            ),
        ],
        [
            "Uses a max-heap and selects the largest unmarked value.",
            "Marks only the selected index and leaves its neighbors available.",
        ],
        marking_oracle,
        random_marking,
        [
            "Put every (value,index) pair in a min-heap to implement both ordering rules.",
            "Maintain a set of indices already marked.",
            "Skip stale heap entries; for a live entry add its value and mark it with both neighbors.",
            "Every index is popped once, and the heap's first live entry is exactly the rule's next selection.",
        ],
        "O(n log n)",
        "O(n)",
        5,
    ),
    2594: entry(
        "minimum_car_repair_time",
        [("ranks", "list[int]"), ("cars", "int")],
        "int",
        ["arrays", "binary search", "math"],
        [
            "A mechanic of rank r repairs c cars in r*c^2 minutes.",
            "Mechanics work simultaneously and each car is assigned to one mechanic.",
            "Return the minimum time by which at least cars repairs can finish.",
        ],
        [
            (
                [[4, 2, 3, 1], 10],
                "At time sixteen the mechanics can repair 2, 2, 2, and 4 cars, totaling ten.",
            ),
            (
                [[5, 1, 8], 6],
                "The rank-one mechanic and the others can finish six cars by time sixteen.",
            ),
        ],
        [
            [r, c]
            for r, c in [
                ([1], 1),
                ([1], 5),
                ([4], 3),
                ([1, 1], 4),
                ([2, 3], 5),
                ([5, 10], 1),
                ([3, 3, 3], 9),
                ([1, 4, 9], 7),
                ([10, 1], 10),
                ([2, 5, 7], 12),
                ([8, 6, 4, 2], 15),
                ([100, 50], 3),
                ([1, 2, 3, 4, 5], 20),
                ([7, 7, 7, 7], 25),
            ]
        ],
        REPAIR,
        [
            REPAIR.replace("time//rank", "(time-1)//rank"),
            REPAIR.replace(">=cars", ">cars"),
        ],
        [
            "Tests one minute too early when calculating each mechanic's capacity.",
            "Requires enough capacity for more than the requested number of cars.",
        ],
        repair_oracle,
        random_repair,
        [
            "For a proposed time T, rank r can finish floor(sqrt(T/r)) cars.",
            "Sum those independent mechanic capacities and compare with cars.",
            "This feasibility condition is monotone, so binary-search the first feasible time.",
            "The fastest mechanic repairing every car supplies a finite upper bound; the first feasible integer is the optimal completion time.",
        ],
        "O(mechanics log answer)",
        "O(1)",
        6,
    ),
    2595: entry(
        "count_even_odd_set_bits",
        [("n", "int")],
        "list[int]",
        ["bit manipulation"],
        [
            "Index binary bits from zero at the least significant bit.",
            "Count set bits separately at even and odd indices.",
            "Return [even_count,odd_count].",
        ],
        [
            (
                [50],
                "Binary 110010 has one set bit at an even index and two at odd indices.",
            ),
            ([2], "Binary 10 has its only set bit at odd index one, yielding [0,1]."),
        ],
        [[n] for n in [1, 3, 4, 5, 7, 8, 10, 15, 16, 31, 32, 63, 255, 1024]],
        BITS,
        [
            BITS.replace("result[index]+=", "result[1-index]+="),
            BITS.replace("index^=1", "index=0"),
        ],
        [
            "Adds each bit to the opposite parity bucket.",
            "Never alternates parity while shifting through the bits.",
        ],
        bits_oracle,
        random_bits,
        [
            "Read bits from least significant to most significant by shifting right.",
            "Maintain a parity index beginning at even zero.",
            "Add the current low bit to that bucket, then toggle the parity.",
            "Every shift advances exactly one binary position, so each set bit reaches its correct parity count.",
        ],
        "O(log n)",
        "O(1)",
        3,
    ),
    2596: entry(
        "valid_knight_tour",
        [("grid", "list[list[int]]")],
        "bool",
        ["matrices", "simulation", "graphs"],
        [
            "The n by n grid contains every visit label from zero through n^2-1 exactly once.",
            "The tour must begin at grid[0][0] with label zero.",
            "Return whether every consecutive label is separated by one knight move.",
        ],
        [
            (
                [
                    [
                        [0, 11, 16, 5, 20],
                        [17, 4, 19, 10, 15],
                        [12, 1, 8, 21, 6],
                        [3, 18, 23, 14, 9],
                        [24, 13, 2, 7, 22],
                    ]
                ],
                "Every consecutive label follows a knight displacement and zero begins at the top-left.",
            ),
            (
                [[[0, 3, 6], [5, 8, 1], [2, 7, 4]]],
                "Labels zero and one are not a knight move apart, so the configuration is invalid.",
            ),
        ],
        [
            [g]
            for g in [
                [[0]],
                [[0, 1], [2, 3]],
                [[1, 0], [2, 3]],
                [[0, 3, 2], [7, 4, 1], [6, 5, 8]],
                [[0, 5, 2], [3, 8, 7], [6, 1, 4]],
                [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
                [[0, 7, 2], [3, 4, 5], [6, 1, 8]],
                [
                    [0, 11, 16, 5, 20],
                    [17, 4, 19, 10, 15],
                    [12, 1, 8, 21, 6],
                    [3, 18, 23, 14, 9],
                    [24, 13, 2, 7, 22],
                ],
                [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]],
                [[0, 6, 1], [4, 8, 5], [7, 3, 2]],
                [[0, 9, 4, 15], [7, 14, 11, 2], [12, 5, 8, 3], [13, 6, 1, 10]],
                [[0, 2], [3, 1]],
                [[0, 4, 8], [7, 3, 2], [6, 1, 5]],
                [[0, 10, 3, 15], [5, 14, 9, 2], [12, 1, 6, 11], [7, 4, 13, 8]],
            ]
        ],
        KNIGHT,
        [
            KNIGHT.replace("grid[0][0]!=0", "grid[0][0]==0"),
            KNIGHT.replace("(1,2),(2,1)", "(1,2)"),
        ],
        [
            "Rejects every correctly anchored tour.",
            "Accepts only one orientation of a knight displacement.",
        ],
        knight_oracle,
        random_knight,
        [
            "Invert the grid into a label-to-coordinate array.",
            "Verify label zero is at the top-left.",
            "For every adjacent label pair, compute absolute row and column differences.",
            "A valid knight move has differences (1,2) or (2,1); checking the complete label sequence proves the tour.",
        ],
        "O(n squared)",
        "O(n squared)",
        5,
    ),
    2597: entry(
        "count_beautiful_difference_subsets",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "backtracking", "hash maps"],
        [
            "Count nonempty index subsets.",
            "A subset is beautiful when no selected pair has absolute difference k.",
            "Equal values at different indices remain distinct choices.",
        ],
        [
            (
                [[2, 4, 6], 2],
                "The valid nonempty subsets are each singleton and {2,6}, giving four.",
            ),
            ([[1], 1], "The sole singleton contains no pair, so it is beautiful."),
        ],
        [
            [a, k]
            for a, k in [
                ([1, 2], 1),
                ([1, 3], 1),
                ([1, 1], 1),
                ([1, 1, 2], 2),
                ([1, 2, 3], 1),
                ([1, 3, 5], 2),
                ([2, 2, 4], 2),
                ([1, 4, 7, 10], 3),
                ([5, 5, 5], 2),
                ([1, 2, 4, 8], 3),
                ([2, 4, 6, 8], 2),
                ([3, 1, 4, 1, 5], 2),
                ([1, 3, 3, 5, 5], 2),
                ([2, 7, 1, 8, 2, 8], 6),
            ]
        ],
        SUBSETS,
        [SUBSETS.replace("value-k", "value"), SUBSETS.replace("answer=-1", "answer=0")],
        [
            "Blocks duplicate values even though their difference is zero rather than positive k.",
            "Includes the empty subset in the returned count.",
        ],
        subsets_oracle,
        random_subsets,
        [
            "Backtrack over each index with skip and take branches.",
            "Track frequencies of values currently selected.",
            "Take value x only when neither x-k nor x+k is present, then undo its frequency after recursion.",
            "The traversal enumerates every index subset once, and the frequency condition is exactly the forbidden-difference rule; subtract the empty subset.",
        ],
        "O(2^n)",
        "O(n)",
        6,
    ),
}
