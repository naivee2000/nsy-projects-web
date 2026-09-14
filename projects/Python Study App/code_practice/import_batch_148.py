"""Graph stars, frog paths, sets, and factorization workbook batch 148."""

from itertools import combinations
from .import_batch_055 import entry


def star_oracle(args):
    values, edges, k = args
    neighbors = [[] for _ in values]
    for a, b in edges:
        neighbors[a].append(values[b])
        neighbors[b].append(values[a])
    return max(
        value + sum(sorted((x for x in neighbors[i] if x > 0), reverse=True)[:k])
        for i, value in enumerate(values)
    )


def random_star(rng):
    n = rng.randint(1, 16)
    possible = list(combinations(range(n), 2))
    rng.shuffle(possible)
    return [
        [rng.randint(-20, 25) for _ in range(n)],
        [list(edge) for edge in possible[: rng.randint(0, len(possible))]],
        rng.randint(0, min(6, n - 1)),
    ]


def frog_oracle(args):
    stones = args[0]
    middle = range(1, len(stones) - 1)
    best = 10**30
    for mask in range(1 << len(middle)):
        outward = (
            [0]
            + [i for bit, i in enumerate(middle) if mask >> bit & 1]
            + [len(stones) - 1]
        )
        returning = (
            [0]
            + [i for bit, i in enumerate(middle) if not mask >> bit & 1]
            + [len(stones) - 1]
        )
        cost = max(
            [stones[b] - stones[a] for a, b in zip(outward, outward[1:])]
            + [stones[b] - stones[a] for a, b in zip(returning, returning[1:])]
        )
        best = min(best, cost)
    return best


def random_frog(rng):
    n = rng.randint(2, 12)
    return [sorted(rng.sample(range(0, 80), n))]


def streak_oracle(args):
    nums = args[0]
    best = -1
    for size in range(2, len(nums) + 1):
        for chosen in combinations(nums, size):
            ordered = sorted(chosen)
            if all(ordered[i] == ordered[i - 1] ** 2 for i in range(1, size)):
                best = max(best, size)
    return best


def random_streak(rng):
    return [[rng.randint(2, 100) for _ in range(rng.randint(1, 10))]]


def sum_or_oracle(args):
    nums = args[0]
    answer = 0
    for mask in range(1 << len(nums)):
        answer |= sum(nums[i] for i in range(len(nums)) if mask >> i & 1)
    return answer


def random_sum_or(rng):
    return [[rng.randint(0, 50) for _ in range(rng.randint(1, 14))]]


def factor_sum(value):
    original = value
    total = 0
    factor = 2
    while factor * factor <= value:
        while value % factor == 0:
            total += factor
            value //= factor
        factor += 1
    if value > 1:
        total += value
    return total if original > 1 else original


def factor_oracle(args):
    value = args[0]
    while True:
        following = factor_sum(value)
        if following >= value:
            return value
        value = following


def random_factor(rng):
    return [rng.randint(2, 100000)]


STAR = """\
def maximum_graph_star_sum(vals,edges,k):
    neighbors=[[] for _ in vals]
    for left,right in edges:
        if vals[right]>0:neighbors[left].append(vals[right])
        if vals[left]>0:neighbors[right].append(vals[left])
    answer=-10**30
    for node,value in enumerate(vals):answer=max(answer,value+sum(sorted(neighbors[node],reverse=True)[:k]))
    return answer
"""
FROG = """\
def minimum_round_trip_frog_jump(stones):
    answer=stones[1]-stones[0]
    for index in range(2,len(stones)):answer=max(answer,stones[index]-stones[index-2])
    return answer
"""
STREAK = """\
def longest_square_streak(nums):
    values=set(nums);answer=-1
    for start in values:
        length=0;current=start
        while current in values: length+=1;current*=current
        if length>=2:answer=max(answer,length)
    return answer
"""
SUM_OR = """\
def bitwise_or_of_subsequence_sums(nums):
    bit_counts=[0]*64
    for value in nums:
        for bit in range(63):bit_counts[bit]+=value>>bit&1
    answer=0
    for bit in range(63):
        if bit_counts[bit]:answer|=1<<bit
        bit_counts[bit+1]+=bit_counts[bit]//2
    return answer
"""
FACTOR = """\
def smallest_prime_factor_sum_value(n):
    while True:
        original=n;total=0;factor=2
        while factor*factor<=n:
            while n%factor==0:total+=factor;n//=factor
            factor+=1
        if n>1:total+=n
        if total==original:return original
        n=total
"""

BATCH = {
    2497: entry(
        "maximum_graph_star_sum",
        [("vals", "list[int]"), ("edges", "list[list[int]]"), ("k", "int")],
        "int",
        ["graphs", "sorting", "greedy"],
        [
            "Choose any center node and at most k of its direct neighbors.",
            "The star sum is the center value plus chosen neighbor values.",
            "Return the maximum star sum; choosing zero neighbors is allowed.",
        ],
        [
            (
                [
                    [1, 2, 3, 4, 10, -10, -20],
                    [[0, 1], [1, 2], [1, 3], [3, 4], [3, 5], [3, 6]],
                    2,
                ],
                "Center 3 has value four; choosing neighbors valued ten and two gives the maximum star sum sixteen.",
            ),
            (
                [[-5, -2], [[0, 1]], 1],
                "All neighbor additions are negative, so choose center value -2 with no edges in the star.",
            ),
        ],
        [
            [v, e, k]
            for v, e, k in [
                ([1], [], 0),
                ([1, 2], [[0, 1]], 0),
                ([1, 2], [[0, 1]], 1),
                ([-1, -2], [[0, 1]], 1),
                ([5, -1, 4], [[0, 1], [0, 2]], 1),
                ([5, 4, 3], [[0, 1], [0, 2]], 2),
                ([0, 10, -5], [[0, 1], [0, 2]], 2),
                ([1, 2, 3, 4], [[0, 1], [0, 2], [0, 3]], 2),
                ([-10, 1, 2], [[0, 1], [0, 2]], 2),
                ([7, 7, 7], [[0, 1], [1, 2]], 1),
                ([1, -2, 8, 9], [[0, 1], [0, 2], [2, 3]], 1),
                ([3, 4, 5], [], 2),
                ([2, 10, 1, 9], [[0, 1], [0, 2], [0, 3]], 2),
                ([-3, 6, 5, 4], [[0, 1], [0, 2], [0, 3]], 3),
            ]
        ],
        STAR,
        [
            STAR.replace(">0", ">-10**30"),
            STAR.replace("[:k]", "[-k:]"),
        ],
        [
            "Includes negative neighbors even though selecting fewer than k edges is allowed.",
            "Chooses the smallest neighbor values rather than the largest positive values.",
        ],
        star_oracle,
        random_star,
        [
            "Negative neighbors can never improve a star because selecting fewer than k is allowed.",
            "Collect positive neighbor values for every possible center.",
            "Sort each center’s values descending and add its largest k to the center value.",
            "For a fixed center, the positive top-k choice is optimal; checking every center yields the global maximum.",
        ],
        "O(edges+n*d log d)",
        "O(edges)",
        5,
    ),
    2498: entry(
        "minimum_round_trip_frog_jump",
        [("stones", "list[int]")],
        "int",
        ["arrays", "greedy"],
        [
            "Stone positions are strictly increasing; the frog travels from the first to last and returns.",
            "Every intermediate stone may be visited at most once across the round trip.",
            "Minimize the largest single jump length.",
        ],
        [
            (
                [[0, 2, 5, 6, 7]],
                "Alternating intermediate stones between the two directions gives a minimum possible largest jump of five.",
            ),
            (
                [[0, 3, 9]],
                "The middle stone can serve only one direction, so the other direction jumps directly from zero to nine.",
            ),
        ],
        [
            [x]
            for x in [
                [0, 1],
                [0, 10],
                [0, 1, 2],
                [0, 2, 3],
                [0, 1, 3, 6],
                [0, 2, 5, 6, 7],
                [0, 5, 6, 7, 20],
                [0, 1, 10, 11],
                [0, 3, 4, 8, 9],
                [0, 2, 4, 8, 16],
                [1, 2, 100],
                [0, 7, 14, 21],
                [0, 1, 2, 50, 51],
                [0, 4, 5, 10, 11, 20],
            ]
        ],
        FROG,
        [FROG.replace("index-2", "index-1"), FROG.replace("max(answer", "min(answer")],
        [
            "Checks only adjacent gaps and ignores jumps that must skip an already used stone.",
            "Minimizes across required jumps instead of tracking the maximum cost.",
        ],
        frog_oracle,
        random_frog,
        [
            "An optimal trip alternates intermediate stones between outbound and return paths.",
            "Each pair of stones two indexes apart must be connected on at least one direction, giving a lower bound on their gap.",
            "Take the maximum two-apart gap, including the first adjacent gap.",
            "Alternating stones realizes exactly those jumps, so the unavoidable lower bound is achievable.",
        ],
        "O(n)",
        "O(1)",
        5,
    ),
    2501: entry(
        "longest_square_streak",
        [("nums", "list[int]")],
        "int",
        ["arrays", "sets"],
        [
            "Choose values from nums and sort the chosen subsequence in increasing order; original positions do not constrain the sorted streak.",
            "Each value after the first must equal the square of its predecessor.",
            "Return the greatest streak length, or -1 when no streak has at least two values.",
        ],
        [
            (
                [[4, 3, 6, 16, 8, 2]],
                "Choosing 2,4,16 creates a three-value square streak.",
            ),
            (
                [[2, 3, 5, 6, 7]],
                "No value’s square is present, so no length-two streak exists and the answer is -1.",
            ),
        ],
        [
            [x]
            for x in [
                [2],
                [2, 4],
                [4, 2],
                [2, 4, 16],
                [3, 9, 81],
                [2, 16, 4],
                [4, 16, 256],
                [2, 3, 4, 9],
                [10, 100, 10000],
                [5, 25, 625],
                [2, 2, 4],
                [99, 9801],
                [7, 49, 2401],
                [2, 4, 15, 16, 256],
            ]
        ],
        STREAK,
        [
            STREAK.replace("current*=current", "current+=current"),
            STREAK.replace("length>=2", "length>=1"),
        ],
        [
            "Doubles each value instead of squaring it.",
            "Accepts a one-value sequence instead of requiring at least two.",
        ],
        streak_oracle,
        random_streak,
        [
            "Store all values in a set for constant-time successor checks.",
            "From each possible start, repeatedly square while the value remains present.",
            "Keep lengths of at least two, otherwise return -1.",
            "Every valid streak is the deterministic chain x,x²,x⁴,... from its smallest member, so following every start finds the longest chain.",
        ],
        "O(n log log V)",
        "O(n)",
        5,
    ),
    2505: entry(
        "bitwise_or_of_subsequence_sums",
        [("nums", "list[int]")],
        "int",
        ["arrays", "bit manipulation"],
        [
            "Consider every subsequence, including the empty one, and compute its element sum.",
            "Bitwise-OR all resulting sums.",
            "Return the combined integer.",
        ],
        [
            (
                [[2, 1, 0, 3]],
                "Possible sums expose bits 0, 1, and 2, so their bitwise OR is seven.",
            ),
            (
                [[4, 4]],
                "Subsequence sums include four and eight, exposing bits two and three for result twelve.",
            ),
        ],
        [
            [x]
            for x in [
                [0],
                [1],
                [2],
                [1, 1],
                [2, 2],
                [4, 4],
                [1, 2, 3],
                [0, 0, 0],
                [7],
                [3, 3, 3],
                [8, 1],
                [5, 10],
                [1, 1, 1, 1],
                [2, 6, 10],
            ]
        ],
        SUM_OR,
        [
            SUM_OR.replace("bit_counts[bit]//2", "bit_counts[bit]//3"),
            SUM_OR.replace("if bit_counts[bit]", "if bit_counts[bit]>1"),
        ],
        [
            "Carries groups of three set bits instead of binary pairs.",
            "Omits bits achievable by a single chosen value.",
        ],
        sum_or_oracle,
        random_sum_or,
        [
            "Count how many input values contribute a one at each bit position.",
            "Any positive count makes that bit appear in some subsequence sum.",
            "Pairs of contributions at one bit create carries into the next bit; propagate count//2 upward.",
            "Choosing suitable subsets realizes both each present bit and every propagated binary carry, so marking all nonzero levels gives exactly the OR of all sums.",
        ],
        "O(64n)",
        "O(1)",
        6,
    ),
    2507: entry(
        "smallest_prime_factor_sum_value",
        [("n", "int")],
        "int",
        ["math", "prime factorization"],
        [
            "Repeatedly replace n by the sum of its prime factors with multiplicity.",
            "Stop when applying the operation would leave the value unchanged.",
            "Return that final smallest value.",
        ],
        [
            (
                [15],
                "Fifteen factors as 3*5, so it becomes eight; eight becomes 2+2+2=6, then 2+3=5, which is prime and stable.",
            ),
            ([4], "Four becomes 2+2=4 immediately, so the answer is four."),
        ],
        [[x] for x in [2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 27, 100]],
        FACTOR,
        [
            FACTOR.replace("while n%factor==0", "if n%factor==0"),
            FACTOR.replace("total+=factor", "total+=1"),
        ],
        [
            "Counts each distinct prime at most once rather than using multiplicity.",
            "Adds one per factor occurrence instead of the prime factor value.",
        ],
        factor_oracle,
        random_factor,
        [
            "Factor the current value by trial division, adding a prime once for each multiplicity.",
            "Add any remaining prime factor after trial division.",
            "If the factor sum equals the prior value, return it; otherwise repeat from the sum.",
            "Composite replacement never increases the value, and equality is exactly the fixed point, so iteration reaches the requested minimum.",
        ],
        "O(iterations*sqrt(n))",
        "O(1)",
        5,
    ),
}
