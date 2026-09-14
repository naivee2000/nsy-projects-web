"""Heap selection, number theory, sorting, bit states, and interval-DP batch 154."""

from collections import Counter, deque
from itertools import combinations
from math import gcd

from .import_batch_055 import entry


def score_oracle(args):
    first, second, k = args
    return max(
        sum(first[index] for index in chosen) * min(second[index] for index in chosen)
        for chosen in combinations(range(len(first)), k)
    )


def random_score(rng):
    n = rng.randint(1, 10)
    return [
        [rng.randint(1, 30) for _ in range(n)],
        [rng.randint(1, 30) for _ in range(n)],
        rng.randint(1, n),
    ]


def reachable_oracle(args):
    common = gcd(*args)
    while common and common % 2 == 0:
        common //= 2
    return common == 1


def random_reachable(rng):
    return [rng.randint(1, 10**6), rng.randint(1, 10**6)]


def students_oracle(args):
    scores, exam = args
    remaining = [row[:] for row in scores]
    answer = []
    while remaining:
        best = max(range(len(remaining)), key=lambda index: remaining[index][exam])
        answer.append(remaining.pop(best))
    return answer


def random_students(rng):
    rows, columns = rng.randint(1, 10), rng.randint(1, 7)
    values = rng.sample(range(1, 2000), rows * columns)
    return [
        [values[row * columns : (row + 1) * columns] for row in range(rows)],
        rng.randrange(columns),
    ]


def strings_oracle(args):
    start, target = args
    queue = deque([start])
    seen = {start}
    while queue:
        state = queue.popleft()
        if state == target:
            return True
        for first in range(len(state)):
            for second in range(first + 1, len(state)):
                bits = list(state)
                a, b = int(bits[first]), int(bits[second])
                bits[first], bits[second] = str(a | b), str(a ^ b)
                following = "".join(bits)
                if following not in seen:
                    seen.add(following)
                    queue.append(following)
                bits = list(state)
                bits[second], bits[first] = str(a | b), str(a ^ b)
                following = "".join(bits)
                if following not in seen:
                    seen.add(following)
                    queue.append(following)
    return False


def random_strings(rng):
    length = rng.randint(1, 8)
    return [
        "".join(rng.choice("01") for _ in range(length)),
        "".join(rng.choice("01") for _ in range(length)),
    ]


def split_oracle(args):
    nums, base = args
    best = 10**30
    for cuts in range(1 << (len(nums) - 1)):
        total = 0
        start = 0
        for index in range(len(nums)):
            if index == len(nums) - 1 or cuts >> index & 1:
                counts = Counter(nums[start : index + 1])
                total += base + sum(count for count in counts.values() if count > 1)
                start = index + 1
        best = min(best, total)
    return best


def random_split(rng):
    return [
        [rng.randint(1, 7) for _ in range(rng.randint(1, 12))],
        rng.randint(1, 10),
    ]


SCORE = """\
def maximum_subsequence_score(nums1,nums2,k):
    import heapq
    chosen=[];total=0;answer=0
    for minimum,value in sorted(zip(nums2,nums1),reverse=True):
        heapq.heappush(chosen,value);total+=value
        if len(chosen)>k:total-=heapq.heappop(chosen)
        if len(chosen)==k:answer=max(answer,total*minimum)
    return answer
"""

REACHABLE = """\
def point_is_reachable(target_x,target_y):
    import math
    common=math.gcd(target_x,target_y)
    return common&(common-1)==0
"""

STUDENTS = """\
def sort_students_by_exam(score,k):
    return sorted(score,key=lambda row:row[k],reverse=True)
"""

STRINGS = """\
def can_make_binary_strings_equal(s,target):
    return ('1' in s)==('1' in target)
"""

SPLIT = """\
def minimum_array_split_cost(nums,k):
    n=len(nums);best=[0]+[10**30]*n
    for end in range(1,n+1):
        counts={};trimmed=0
        for start in range(end-1,-1,-1):
            value=nums[start];counts[value]=counts.get(value,0)+1
            if counts[value]==2:trimmed+=2
            elif counts[value]>2:trimmed+=1
            best[end]=min(best[end],best[start]+k+trimmed)
    return best[n]
"""


BATCH = {
    2542: entry(
        "maximum_subsequence_score",
        [("nums1", "list[int]"), ("nums2", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "greedy", "heaps", "sorting"],
        [
            "Choose exactly k common indices from the equal-length arrays.",
            "The score is the selected nums1 sum multiplied by the minimum selected nums2 value.",
            "Return the largest possible score.",
        ],
        [
            (
                [[1, 3, 3, 2], [2, 1, 3, 4], 3],
                "Choosing indices zero, two, and three gives sum six and minimum two, scoring twelve.",
            ),
            (
                [[4, 2, 3, 1, 1], [7, 5, 10, 9, 6], 1],
                "For one index, nums1[2] times nums2[2] gives the maximum score thirty.",
            ),
        ],
        [
            [a, b, k]
            for a, b, k in [
                ([1], [1], 1),
                ([5], [9], 1),
                ([1, 2], [2, 1], 1),
                ([1, 2], [2, 1], 2),
                ([2, 2, 2], [3, 2, 1], 2),
                ([10, 1, 1], [1, 10, 9], 2),
                ([3, 1, 4], [1, 5, 9], 3),
                ([5, 4, 3, 2], [1, 2, 3, 4], 2),
                ([1, 10, 3, 8], [7, 2, 9, 4], 3),
                ([9, 8, 7, 6], [1, 1, 1, 1], 2),
                ([2, 7, 1, 8, 2], [8, 1, 8, 2, 8], 3),
                ([100, 1, 50], [2, 100, 3], 2),
                ([6, 5, 4, 3, 2], [2, 3, 4, 5, 6], 4),
                ([1, 3, 3, 7, 4], [9, 8, 7, 6, 5], 3),
            ]
        ],
        SCORE,
        [
            SCORE.replace("reverse=True", "reverse=False"),
            SCORE.replace(
                "heapq.heappop(chosen)", "heapq.heappop(chosen);heapq.heappop(chosen)"
            ),
        ],
        [
            "Processes candidate minimum values in ascending order, invalidating the threshold invariant.",
            "Removes two small nums1 values whenever the heap exceeds k.",
        ],
        score_oracle,
        random_score,
        [
            "Sort index pairs by nums2 from largest to smallest.",
            "At each position, the current nums2 is the minimum for any selection formed from the processed prefix.",
            "Maintain the k largest nums1 values in that prefix with a min-heap and track their sum.",
            "For every possible selected minimum, the heap maximizes the accompanying sum; checking all thresholds therefore finds the global optimum.",
        ],
        "O(n log n+n log k)",
        "O(n+k)",
        6,
    ),
    2543: entry(
        "point_is_reachable",
        [("target_x", "int"), ("target_y", "int")],
        "bool",
        ["math", "greatest common divisor", "number theory"],
        [
            "Start at coordinate (1,1) on an unbounded integer grid.",
            "Allowed moves subtract one coordinate from the other or double either coordinate.",
            "Return whether the positive target coordinate is reachable in finitely many moves.",
        ],
        [
            (
                [6, 9],
                "The greatest common divisor is three, which cannot be produced solely through doubling.",
            ),
            (
                [4, 7],
                "The coordinates are coprime, so Euclidean reductions reach (1,1).",
            ),
        ],
        [
            [a, b]
            for a, b in [
                (1, 1),
                (1, 2),
                (2, 2),
                (3, 3),
                (4, 4),
                (6, 10),
                (8, 12),
                (12, 20),
                (7, 21),
                (15, 25),
                (32, 48),
                (64, 96),
                (17, 34),
                (999, 1000),
            ]
        ],
        REACHABLE,
        [
            REACHABLE.replace("common&(common-1)==0", "common%2==0"),
            REACHABLE.replace("math.gcd(target_x,target_y)", "target_x+target_y"),
        ],
        [
            "Accepts every even greatest common divisor, including values with odd factors.",
            "Tests the coordinate sum instead of their greatest common divisor.",
        ],
        reachable_oracle,
        random_reachable,
        [
            "Subtraction preserves the greatest common divisor, while doubling multiplies it by at most a factor of two.",
            "Starting from gcd one means no odd prime can ever enter the gcd.",
            "Compute gcd(target_x,target_y) and test whether it is a power of two.",
            "Euclidean subtraction removes relative factors, and reverse halvings remove every factor of two, making the condition both necessary and sufficient.",
        ],
        "O(log min coordinate)",
        "O(1)",
        8,
    ),
    2545: entry(
        "sort_students_by_exam",
        [("score", "list[list[int]]"), ("k", "int")],
        "list[list[int]]",
        ["matrices", "sorting", "arrays"],
        [
            "Each row stores one student's exam scores.",
            "All scores are distinct, and k is a zero-based exam column.",
            "Return complete rows sorted by column k in descending order.",
        ],
        [
            (
                [[[10, 6, 9, 1], [7, 5, 11, 2], [4, 8, 3, 15]], 2],
                "Column two values 11, 9, and 3 determine the returned row order.",
            ),
            (
                [[[3, 4], [5, 6]], 0],
                "First-exam scores five and three place the second row first.",
            ),
        ],
        [
            [m, k]
            for m, k in [
                ([[1]], 0),
                ([[1, 2]], 1),
                ([[1], [2]], 0),
                ([[9, 1], [8, 2], [7, 3]], 1),
                ([[1, 9], [2, 8], [3, 7]], 0),
                ([[4, 1, 7], [3, 9, 2]], 1),
                ([[10, 20], [30, 40], [50, 60]], 0),
                ([[6, 2, 8], [1, 9, 3], [7, 4, 5]], 2),
                ([[100, 1], [2, 99], [50, 51]], 1),
                ([[5, 8, 1], [9, 2, 7], [3, 6, 4]], 0),
                ([[1, 8, 4, 7], [2, 6, 9, 3]], 3),
                ([[11, 5], [3, 17], [13, 7], [19, 2]], 0),
                ([[20, 3, 14], [8, 18, 1], [9, 2, 17]], 1),
                ([[4, 12, 20], [8, 16, 24], [6, 18, 2], [10, 14, 22]], 2),
            ]
        ],
        STUDENTS,
        [
            STUDENTS.replace("reverse=True", "reverse=False"),
            STUDENTS.replace("row[k]", "row[0]"),
        ],
        [
            "Sorts the selected exam scores in ascending order.",
            "Always sorts by the first exam rather than the requested column.",
        ],
        students_oracle,
        random_students,
        [
            "Treat each entire student row as one sortable record.",
            "Use the kth entry as the sort key.",
            "Request descending order while preserving every row unchanged.",
            "Distinct scores in the selected column make the key order unambiguous.",
        ],
        "O(m log m)",
        "O(m)",
        5,
    ),
    2546: entry(
        "can_make_binary_strings_equal",
        [("s", "str"), ("target", "str")],
        "bool",
        ["strings", "bit manipulation", "invariants"],
        [
            "The equal-length strings contain only zero and one.",
            "An operation replaces bits i,j simultaneously by their OR and XOR values.",
            "Return whether any sequence of operations transforms s into target.",
        ],
        [
            (
                ["1010", "0110"],
                "Both strings contain a one, and operations can reposition and change the count of ones.",
            ),
            (
                ["11", "00"],
                "An operation can never eliminate the final remaining one, so all-zero target is unreachable.",
            ),
        ],
        [
            [a, b]
            for a, b in [
                ("0", "0"),
                ("0", "1"),
                ("1", "0"),
                ("1", "1"),
                ("00", "00"),
                ("00", "01"),
                ("01", "10"),
                ("01", "11"),
                ("10", "01"),
                ("111", "001"),
                ("000", "000"),
                ("000", "111"),
                ("10101", "01010"),
                ("10000", "11111"),
            ]
        ],
        STRINGS,
        [STRINGS.replace("==", "!="), STRINGS.replace("'1'", "'0'")],
        [
            "Reverses the necessary and sufficient invariant.",
            "Compares the presence of zero even though zeros are not preserved in the same way.",
        ],
        strings_oracle,
        random_strings,
        [
            "Study the operation on pairs 00, 01, 10, and 11.",
            "An all-zero string remains all zero, while a string containing one can never lose its final one.",
            "With at least one one, the allowed pair transformations can arrange any desired nonzero binary state.",
            "Therefore reachability depends only on whether both strings contain at least one one or both contain none.",
        ],
        "O(n)",
        "O(1)",
        5,
    ),
    2547: entry(
        "minimum_array_split_cost",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "dynamic programming", "hash maps"],
        [
            "Split nums into one or more nonempty contiguous subarrays.",
            "A part costs k plus the number of its elements whose values occur more than once in that part.",
            "Return the minimum total split cost.",
        ],
        [
            (
                [[1, 2, 1, 2, 1, 3, 3], 2],
                "Balancing new-part fees against repeated elements yields minimum total cost eight.",
            ),
            ([[1, 2, 1, 2, 1], 2], "The optimal split has cost six."),
        ],
        [
            [a, k]
            for a, k in [
                ([1], 1),
                ([1, 1], 1),
                ([1, 2], 1),
                ([1, 1, 1], 2),
                ([1, 2, 1], 2),
                ([1, 2, 3], 5),
                ([1, 2, 1, 2], 1),
                ([2, 2, 3, 3], 3),
                ([1, 1, 2, 3, 3], 2),
                ([5, 4, 5, 4, 5], 4),
                ([1, 2, 3, 1, 2, 3], 2),
                ([7, 7, 7, 8, 8], 3),
                ([1, 2, 1, 3, 2, 3, 1], 5),
                ([4, 1, 4, 2, 4, 1, 2, 3], 3),
            ]
        ],
        SPLIT,
        [
            SPLIT.replace("trimmed+=2", "trimmed+=1"),
            SPLIT.replace("best[start]+k+trimmed", "best[start]+trimmed"),
        ],
        [
            "Counts only one element when a value first becomes duplicated, rather than both copies.",
            "Omits the fixed k charge for every created part.",
        ],
        split_oracle,
        random_split,
        [
            "Let best[end] be the minimum cost for the prefix ending just before index end.",
            "For each end, extend a candidate last part backward while maintaining its value frequencies and trimmed length.",
            "A frequency changing from one to two adds two trimmed elements; every later copy adds one.",
            "Trying every last-part start covers every possible final cut, and adding the optimal preceding prefix gives the standard optimal-substructure recurrence.",
        ],
        "O(n squared)",
        "O(n)",
        8,
    ),
}
