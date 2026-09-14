"""Bitmask, interval, and preprocessing workbook batch 141."""

from itertools import combinations
from math import comb
from .import_batch_055 import entry


def rows_oracle(args):
    matrix, count = args
    columns = range(len(matrix[0]))
    best = 0
    for chosen in combinations(columns, count):
        selected = set(chosen)
        best = max(
            best,
            sum(
                all(not value or index in selected for index, value in enumerate(row))
                for row in matrix
            ),
        )
    return best


def random_rows(rng):
    height = rng.randint(1, 10)
    width = rng.randint(1, 8)
    return [
        [[rng.randrange(2) for _ in range(width)] for _ in range(height)],
        rng.randint(0, width),
    ]


def ways_oracle(args):
    start, end, steps = args
    states = {start: 1}
    mod = 10**9 + 7
    for _ in range(steps):
        following = {}
        for position, count in states.items():
            following[position - 1] = (following.get(position - 1, 0) + count) % mod
            following[position + 1] = (following.get(position + 1, 0) + count) % mod
        states = following
    return states.get(end, 0)


def random_ways(rng):
    return [rng.randint(-10, 10), rng.randint(-10, 10), rng.randint(0, 30)]


def groups_oracle(args):
    events = []
    for left, right in args[0]:
        events.extend(((left, 1), (right + 1, -1)))
    active = best = 0
    for _, change in sorted(events):
        active += change
        best = max(best, active)
    return best


def random_groups(rng):
    intervals = []
    for _ in range(rng.randint(1, 25)):
        left = rng.randint(0, 40)
        intervals.append([left, rng.randint(left, left + 15)])
    return [intervals]


def subarrays_oracle(args):
    nums = args[0]
    answer = []
    for start in range(len(nums)):
        target = 0
        for value in nums[start:]:
            target |= value
        current = 0
        for end in range(start, len(nums)):
            current |= nums[end]
            if current == target:
                answer.append(end - start + 1)
                break
    return answer


def random_subarrays(rng):
    return [[rng.randint(0, 1023) for _ in range(rng.randint(1, 30))]]


def good_oracle(args):
    nums, k = args
    answer = []
    for index in range(k, len(nums) - k):
        before = nums[index - k : index]
        after = nums[index + 1 : index + k + 1]
        if all(before[i] >= before[i + 1] for i in range(k - 1)) and all(
            after[i] <= after[i + 1] for i in range(k - 1)
        ):
            answer.append(index)
    return answer


def random_good(rng):
    n = rng.randint(3, 30)
    return [[rng.randint(0, 20) for _ in range(n)], rng.randint(1, (n - 1) // 2)]


ROWS = """\
def maximum_covered_rows(matrix,num_select):
    masks=[]
    for row in matrix:
        mask=0
        for column,value in enumerate(row):
            if value:mask|=1<<column
        masks.append(mask)
    best=0;width=len(matrix[0])
    for selected in range(1<<width):
        if selected.bit_count()==num_select:best=max(best,sum(mask&selected==mask for mask in masks))
    return best
"""

WAYS = """\
def ways_to_reach_position(start_pos,end_pos,k):
    from math import comb
    distance=abs(end_pos-start_pos)
    if distance>k or (k-distance)%2:return 0
    return comb(k,(k+end_pos-start_pos)//2)%(10**9+7)
"""

GROUPS = """\
def minimum_nonoverlapping_interval_groups(intervals):
    import heapq
    endings=[]
    for left,right in sorted(intervals):
        if endings and endings[0]<left:heapq.heapreplace(endings,right)
        else:heapq.heappush(endings,right)
    return len(endings)
"""

SUBARRAYS = """\
def smallest_max_or_subarrays(nums):
    last=[-1]*32;answer=[1]*len(nums)
    for index in range(len(nums)-1,-1,-1):
        for bit in range(32):
            if nums[index]>>bit&1:last[bit]=index
        farthest=index
        for position in last:
            if position!=-1:farthest=max(farthest,position)
        answer[index]=farthest-index+1
    return answer
"""

GOOD = """\
def good_monotonic_indices(nums,k):
    n=len(nums);decreasing=[1]*n;increasing=[1]*n
    for index in range(1,n):
        if nums[index]<=nums[index-1]:decreasing[index]=decreasing[index-1]+1
    for index in range(n-2,-1,-1):
        if nums[index]<=nums[index+1]:increasing[index]=increasing[index+1]+1
    return [index for index in range(k,n-k) if decreasing[index-1]>=k and increasing[index+1]>=k]
"""

BATCH = {
    2397: entry(
        "maximum_covered_rows",
        [("matrix", "list[list[int]]"), ("num_select", "int")],
        "int",
        ["matrices", "bitmasks", "enumeration"],
        [
            "Select exactly num_select distinct matrix columns.",
            "A row is covered when every 1 in that row lies in a selected column; an all-zero row is always covered.",
            "Return the greatest number of rows covered by one selection.",
        ],
        [
            (
                [[[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 0, 1]], 2],
                "Selecting columns 0 and 2 covers the zero row and the two rows whose ones are confined to those columns, giving three.",
            ),
            (
                [[[1, 0], [0, 1]], 1],
                "Either single column covers exactly one row, so the maximum is one.",
            ),
        ],
        [
            [m, k]
            for m, k in [
                ([[0]], 0),
                ([[1]], 1),
                ([[1]], 0),
                ([[0, 0], [0, 0]], 1),
                ([[1, 1]], 2),
                ([[1, 1]], 1),
                ([[1, 0], [1, 0]], 1),
                ([[1, 0], [0, 1], [1, 1]], 2),
                ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1),
                ([[1, 1, 0], [0, 1, 1]], 2),
                ([[0, 0, 1], [0, 0, 0]], 0),
                ([[1, 0, 1], [1, 0, 1], [0, 1, 0]], 2),
                ([[1, 1, 1], [0, 0, 0]], 3),
                ([[1, 0, 0, 1], [0, 1, 1, 0]], 2),
            ]
        ],
        ROWS,
        [
            ROWS.replace(
                "selected.bit_count()==num_select", "selected.bit_count()>=num_select"
            ),
            ROWS.replace("mask&selected==mask", "mask&selected!=0"),
        ],
        [
            "Allows fewer than the required number of selected columns.",
            "Counts a row when any one is selected instead of requiring all its ones.",
        ],
        rows_oracle,
        random_rows,
        [
            "Encode each row’s one-columns as a bitmask.",
            "Enumerate column masks containing exactly num_select bits.",
            "A row is covered precisely when row_mask & selected equals row_mask.",
            "Every legal selection is enumerated, and the subset test exactly matches coverage, so the best count is optimal.",
        ],
        "O(2^n*m)",
        "O(m)",
        5,
    ),
    2400: entry(
        "ways_to_reach_position",
        [("start_pos", "int"), ("end_pos", "int"), ("k", "int")],
        "int",
        ["math", "combinatorics"],
        [
            "Each of exactly k steps moves one position left or right on an infinite number line.",
            "Two ways differ when their left/right step sequences differ.",
            "Return the number ending at end_pos modulo 1,000,000,007.",
        ],
        [
            (
                [1, 2, 3],
                "Two right steps and one left step can be ordered in three distinct ways, so the answer is three.",
            ),
            (
                [2, 5, 10],
                "The distance and step-count parity differ, making the destination unreachable in exactly ten steps.",
            ),
        ],
        [
            [a, b, k]
            for a, b, k in [
                (0, 0, 0),
                (0, 1, 0),
                (0, 1, 1),
                (0, 0, 2),
                (0, 2, 2),
                (0, 2, 3),
                (5, 1, 4),
                (-2, 2, 4),
                (-3, -5, 4),
                (10, 0, 5),
                (1, 1, 6),
                (3, 8, 7),
                (8, 3, 7),
                (0, 10, 10),
            ]
        ],
        WAYS,
        [
            WAYS.replace("(k-distance)%2", "(k-distance+1)%2"),
            WAYS.replace("//2", "//2+1"),
        ],
        [
            "Uses the opposite parity condition.",
            "Chooses one too many right steps in the binomial coefficient.",
        ],
        ways_oracle,
        random_ways,
        [
            "Let r be the number of right steps and l the number of left steps.",
            "Solve r+l=k and r-l=end_pos-start_pos.",
            "If the distance is too large or parity is wrong, return zero; otherwise choose which r of the k steps go right.",
            "Every valid sequence corresponds uniquely to a choice of right-step positions, so the binomial coefficient counts exactly all ways.",
        ],
        "O(1)",
        "O(1)",
        5,
    ),
    2406: entry(
        "minimum_nonoverlapping_interval_groups",
        [("intervals", "list[list[int]]")],
        "int",
        ["intervals", "sorting", "heaps"],
        [
            "Intervals are inclusive, so intervals sharing an endpoint overlap.",
            "Place every interval into a group whose intervals are pairwise non-overlapping.",
            "Return the minimum number of groups.",
        ],
        [
            (
                [[[5, 10], [6, 8], [1, 5], [2, 3], [1, 10]]],
                "At value 6, three intervals overlap, requiring three groups; three groups also suffice.",
            ),
            (
                [[[1, 2], [3, 4], [5, 6]]],
                "Each interval ends before the next begins, so all fit in one group.",
            ),
        ],
        [
            [x]
            for x in [
                [[1, 1]],
                [[1, 2], [2, 3]],
                [[1, 2], [3, 4]],
                [[1, 10], [2, 3], [4, 5]],
                [[0, 0], [0, 0]],
                [[1, 5], [1, 5], [1, 5]],
                [[1, 3], [2, 4], [3, 5]],
                [[5, 7], [1, 2], [3, 4]],
                [[1, 100], [20, 30]],
                [[2, 2], [1, 1], [3, 3]],
                [[1, 4], [2, 2], [3, 3], [4, 5]],
                [[10, 20], [0, 9]],
                [[0, 2], [2, 4], [4, 6]],
                [[7, 8], [1, 10], [2, 3]],
            ]
        ],
        GROUPS,
        [
            GROUPS.replace("endings[0]<left", "endings[0]<=left"),
            GROUPS.replace("sorted(intervals)", "intervals"),
        ],
        [
            "Treats touching inclusive intervals as non-overlapping.",
            "Processes intervals in input order, so heap reuse is not chronological.",
        ],
        groups_oracle,
        random_groups,
        [
            "Sort intervals by starting point.",
            "Keep a min-heap of the ending value for each active group.",
            "Reuse the earliest-ending group only when its end is strictly less than the new start; otherwise open another group.",
            "The heap size equals simultaneous overlap, a lower bound, and earliest-ending reuse attains that bound.",
        ],
        "O(n log n)",
        "O(n)",
        5,
    ),
    2411: entry(
        "smallest_max_or_subarrays",
        [("nums", "list[int]")],
        "list[int]",
        ["arrays", "bit manipulation"],
        [
            "For every index i, consider nonempty subarrays beginning at i.",
            "Find the maximum bitwise OR any such subarray can obtain.",
            "Return the shortest length attaining that maximum for each starting index.",
        ],
        [
            (
                [[1, 0, 2, 1, 3]],
                "From index 0 the maximum OR 3 first appears at length 3; repeating this gives [3,3,2,2,1].",
            ),
            (
                [[0, 0]],
                "Every subarray has OR zero, so length one is already sufficient at both indexes.",
            ),
        ],
        [
            [x]
            for x in [
                [0],
                [7],
                [1, 2],
                [2, 1],
                [1, 1],
                [0, 1, 0],
                [1, 2, 4],
                [4, 2, 1],
                [3, 0, 0],
                [8, 1, 2, 4],
                [5, 1, 5],
                [0, 0, 1],
                [0, 1 << 29],
                [1, 0, 0, 8],
            ]
        ],
        SUBARRAYS,
        [
            SUBARRAYS.replace("range(32)", "range(29)"),
            SUBARRAYS.replace(
                "farthest=max(farthest,position)", "farthest=min(farthest,position)"
            ),
        ],
        [
            "Never tracks bit 31 and fails for values using that bit.",
            "Takes the nearest required bit position instead of the farthest one.",
        ],
        subarrays_oracle,
        random_subarrays,
        [
            "Scan starts from right to left while recording the nearest position at or after i containing each bit.",
            "Update a bit’s last position when nums[i] contains it.",
            "The subarray must extend through the farthest recorded required-bit position.",
            "The suffix maximum OR contains exactly the bits with recorded positions, and reaching their farthest first occurrence is both necessary and sufficient.",
        ],
        "O(32n)",
        "O(1)",
        5,
    ),
    2420: entry(
        "good_monotonic_indices",
        [("nums", "list[int]"), ("k", "int")],
        "list[int]",
        ["arrays", "prefixes"],
        [
            "A good index has at least k elements on each side.",
            "The k immediately preceding values must be non-increasing.",
            "The k immediately following values must be non-decreasing; return all good indexes in ascending order.",
        ],
        [
            (
                [[2, 1, 1, 1, 3, 4, 1], 2],
                "Indexes 2 and 3 each have a non-increasing pair before and a non-decreasing pair after.",
            ),
            (
                [[2, 1, 1, 2], 2],
                "No index has two elements on both sides, so the result is empty.",
            ),
        ],
        [
            [a, k]
            for a, k in [
                ([1, 1, 1], 1),
                ([3, 2, 1, 2, 3], 2),
                ([1, 2, 3, 2, 1], 1),
                ([5, 4, 3, 2, 1], 1),
                ([1, 2, 3, 4, 5], 1),
                ([3, 3, 3, 3, 3], 2),
                ([4, 3, 2, 1, 2, 3, 4], 3),
                ([1, 3, 2, 2, 4, 5], 2),
                ([9, 8, 7, 6, 5, 6, 7, 8, 9], 4),
                ([2, 2, 1, 3, 3], 1),
                ([5, 1, 1, 1, 5], 2),
                ([1, 0, 2], 1),
                ([10, 9, 8, 7, 8, 9], 2),
                ([4, 4, 3, 2, 2, 3, 3], 2),
            ]
        ],
        GOOD,
        [
            GOOD.replace("nums[index]<=nums[index-1]", "nums[index]<nums[index-1]"),
            GOOD.replace("increasing[index+1]>=k", "increasing[index]>=k"),
        ],
        [
            "Rejects equal adjacent values in a non-increasing run.",
            "Includes the candidate index itself in the following run check.",
        ],
        good_oracle,
        random_good,
        [
            "Precompute the length of the non-increasing run ending at every position.",
            "Precompute the length of the non-decreasing run starting at every position.",
            "Index i is good when the run ending at i-1 and the run starting at i+1 both have length at least k.",
            "These two run lengths exactly summarize the required adjacent comparisons on each side, allowing a linear scan.",
        ],
        "O(n)",
        "O(n)",
        5,
    ),
}
