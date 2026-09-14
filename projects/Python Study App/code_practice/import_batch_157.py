"""Fruit swaps, fair pairs, binary substrings, subsequences, and score batch 157."""

from collections import Counter
from heapq import heappop, heappush
from itertools import combinations

from .import_batch_055 import entry


def fruits_oracle(args):
    first, second = args
    target = tuple(sorted((first + second))[::2])
    if Counter(first + second) != Counter(value for value in target for _ in range(2)):
        return -1
    start = tuple(sorted(first))
    goal = tuple(sorted(target))
    heap = [(0, start)]
    best = {start: 0}
    second_start = list(second)
    while heap:
        cost, state = heappop(heap)
        if state == goal:
            return cost
        if cost != best[state]:
            continue
        remaining = Counter(first + second)
        remaining.subtract(state)
        other = list(remaining.elements())
        for i, left in enumerate(state):
            for right in other:
                changed = list(state)
                changed[i] = right
                following = tuple(sorted(changed))
                new = cost + min(left, right)
                if new < best.get(following, 10**30):
                    best[following] = new
                    heappush(heap, (new, following))
    return -1


def random_fruits(rng):
    n = rng.randint(1, 7)
    return [
        [rng.randint(1, 8) for _ in range(n)],
        [rng.randint(1, 8) for _ in range(n)],
    ]


def pairs_oracle(args):
    nums, lower, upper = args
    return sum(
        lower <= nums[i] + nums[j] <= upper
        for i, j in combinations(range(len(nums)), 2)
    )


def random_pairs(rng):
    n = rng.randint(1, 25)
    lower, upper = sorted((rng.randint(-30, 20), rng.randint(-20, 30)))
    return [[rng.randint(-20, 20) for _ in range(n)], lower, upper]


def xor_oracle(args):
    text, queries = args
    answer = []
    for first, second in queries:
        target = first ^ second
        candidates = []
        for left in range(len(text)):
            value = 0
            for right in range(left, len(text)):
                value = value * 2 + int(text[right])
                if value == target:
                    candidates.append([left, right])
        answer.append(
            min(
                candidates,
                key=lambda pair: (pair[1] - pair[0], pair[0]),
                default=[-1, -1],
            )
        )
    return answer


def random_xor(rng):
    text = "".join(rng.choice("01") for _ in range(rng.randint(1, 14)))
    return [
        text,
        [[rng.randint(0, 31), rng.randint(0, 31)] for _ in range(rng.randint(1, 10))],
    ]


def is_subsequence(needle, haystack):
    position = 0
    for char in haystack:
        if position < len(needle) and needle[position] == char:
            position += 1
    return position == len(needle)


def subsequence_oracle(args):
    source, target = args
    for length in range(len(target) + 1):
        for start in range(len(target) - length + 1):
            if is_subsequence(target[:start] + target[start + length :], source):
                return length


def random_subsequence(rng):
    return [
        "".join(rng.choice("abcd") for _ in range(rng.randint(1, 12))),
        "".join(rng.choice("abcdz") for _ in range(rng.randint(1, 10))),
    ]


def change_oracle(args):
    nums = args[0]
    return min(
        max(nums[index] for index in kept) - min(nums[index] for index in kept)
        for kept in combinations(range(len(nums)), len(nums) - 2)
    )


def random_change(rng):
    return [[rng.randint(-30, 30) for _ in range(rng.randint(3, 15))]]


FRUITS = """\
def minimum_fruit_rearrangement_cost(basket1,basket2):
    counts={}
    for value in basket1:counts[value]=counts.get(value,0)+1
    for value in basket2:counts[value]=counts.get(value,0)-1
    smallest=min(basket1+basket2);extras=[]
    for value,difference in counts.items():
        if difference%2:return -1
        extras.extend([value]*(abs(difference)//2))
    extras.sort()
    return sum(min(value,2*smallest) for value in extras[:len(extras)//2])
"""

PAIRS = """\
def count_fair_sum_pairs(nums,lower,upper):
    import bisect
    nums=sorted(nums);answer=0
    for index,value in enumerate(nums):
        start=bisect.bisect_left(nums,lower-value,index+1)
        end=bisect.bisect_right(nums,upper-value,index+1)
        answer+=end-start
    return answer
"""

XOR = """\
def substring_xor_answers(s,queries):
    locations={}
    for left in range(len(s)):
        value=0
        for right in range(left,min(len(s),left+32)):
            value=value*2+int(s[right])
            if value not in locations:locations[value]=[left,right]
            if value==0:break
    return [locations.get(first^second,[-1,-1]) for first,second in queries]
"""

SUBSEQUENCE = """\
def minimum_subsequence_removal_score(s,t):
    n=len(t);prefix=[-1]*n;suffix=[-1]*n
    position=0
    for index,char in enumerate(t):
        found=s.find(char,position)
        if found<0:break
        prefix[index]=found;position=found+1
    position=len(s)
    for index in range(n-1,-1,-1):
        found=s.rfind(t[index],0,position)
        if found<0:break
        suffix[index]=found;position=found
    answer=n;right=0
    for left in range(-1,n):
        if left>=0 and prefix[left]<0:break
        right=max(right,left+1)
        while right<n and (suffix[right]<0 or suffix[right]<=(-1 if left<0 else prefix[left])):right+=1
        answer=min(answer,right-left-1)
    return answer
"""

CHANGE = """\
def minimum_score_after_two_changes(nums):
    nums=sorted(nums)
    return min(nums[-1]-nums[2],nums[-2]-nums[1],nums[-3]-nums[0])
"""


BATCH = {
    2561: entry(
        "minimum_fruit_rearrangement_cost",
        [("basket1", "list[int]"), ("basket2", "list[int]")],
        "int",
        ["arrays", "greedy", "hash maps", "sorting"],
        [
            "The two baskets have equal size; one swap exchanges one fruit across baskets.",
            "A swap costs the smaller of its two fruit values.",
            "Return minimum cost to make sorted baskets identical, or -1 if impossible.",
        ],
        [
            (
                [[4, 2, 2, 2], [1, 4, 1, 2]],
                "One direct swap involving fruit value one achieves equality at cost one.",
            ),
            (
                [[2, 3, 4, 1], [3, 2, 5, 1]],
                "The combined count of values four and five is odd, so identical baskets are impossible.",
            ),
        ],
        [
            [a, b]
            for a, b in [
                ([1], [1]),
                ([1], [2]),
                ([1, 2], [2, 1]),
                ([1, 1], [2, 2]),
                ([1, 1, 2, 2], [1, 1, 2, 2]),
                ([1, 1, 10, 10], [2, 2, 9, 9]),
                ([1, 5, 5, 5], [1, 5, 5, 5]),
                ([2, 2, 3, 3], [2, 3, 4, 4]),
                ([1, 1, 4, 4], [2, 2, 3, 3]),
                ([3, 3, 8, 8, 9, 9], [3, 3, 7, 7, 10, 10]),
                ([1, 1, 100, 100], [50, 50, 60, 60]),
                ([2, 2, 2, 4, 4, 4], [2, 2, 2, 5, 5, 5]),
                ([1, 1, 8, 8, 9, 9], [2, 2, 3, 3, 1, 1]),
                ([5, 5, 6, 6, 7, 7], [5, 5, 8, 8, 9, 9]),
            ]
        ],
        FRUITS,
        [
            FRUITS.replace("2*smallest", "smallest"),
            FRUITS.replace("extras[:len(extras)//2]", "extras[len(extras)//2:]"),
        ],
        [
            "Prices the two-swap route through the global minimum as one minimum instead of two.",
            "Pays for the larger half of unmatched values rather than pairing them against that half.",
        ],
        fruits_oracle,
        random_fruits,
        [
            "Combined fruit counts must be even; each basket needs half of every value.",
            "Collect the absolute half-surpluses from both baskets and sort them.",
            "Only the smaller half determines direct swap costs; each can instead travel through the global minimum for cost twice that minimum.",
            "Pairing smallest surplus values with largest opposite values minimizes direct costs, while the minimum-fruit detour caps every pair independently.",
        ],
        "O(n log n)",
        "O(n)",
        8,
    ),
    2563: entry(
        "count_fair_sum_pairs",
        [("nums", "list[int]"), ("lower", "int"), ("upper", "int")],
        "int",
        ["arrays", "binary search", "sorting"],
        [
            "Count index pairs i<j.",
            "A pair is fair when lower <= nums[i]+nums[j] <= upper.",
            "Return the number of fair pairs.",
        ],
        [
            (
                [[0, 1, 7, 4, 4, 5], 3, 6],
                "Six index pairs have sums between three and six inclusive.",
            ),
            (
                [[1, 7, 9, 2, 5], 11, 11],
                "Only values two and nine sum to exactly eleven.",
            ),
        ],
        [
            [a, l, u]
            for a, l, u in [
                ([1], 0, 2),
                ([1, 2], 3, 3),
                ([1, 2], 4, 5),
                ([-1, 1], 0, 0),
                ([0, 0, 0], 0, 0),
                ([1, 2, 3], 3, 5),
                ([-5, -2, 1, 4], -4, 2),
                ([1, 1, 2, 2], 2, 3),
                ([10, -10, 5, -5], -5, 5),
                ([3, 3, 3, 3], 6, 6),
                ([-3, -2, -1], -5, -3),
                ([2, 4, 6, 8], 7, 13),
                ([1, 5, 2, 7, 3], 4, 8),
                ([-10, 0, 10, 20], 0, 20),
            ]
        ],
        PAIRS,
        [
            PAIRS.replace("bisect_right", "bisect_left"),
            PAIRS.replace("index+1", "index"),
        ],
        [
            "Excludes sums equal to the inclusive upper bound.",
            "Allows the current index to pair with itself.",
        ],
        pairs_oracle,
        random_pairs,
        [
            "Sort the values so valid partners for one value form a contiguous interval.",
            "For each index, binary-search the first partner reaching lower-value.",
            "Binary-search just after the last partner at most upper-value, restricting both searches to later indices.",
            "The difference of those bounds counts every fair pair once at its smaller index.",
        ],
        "O(n log n)",
        "O(n)",
        6,
    ),
    2564: entry(
        "substring_xor_answers",
        [("s", "str"), ("queries", "list[list[int]]")],
        "list[list[int]]",
        ["strings", "bit manipulation", "hash maps"],
        [
            "For each [first,second], seek a binary substring whose value equals first XOR second.",
            "Choose minimum substring length, then minimum starting index.",
            "Return [start,end] or [-1,-1] for every query.",
        ],
        [
            (
                ["101101", [[0, 5], [1, 2]]],
                "Targets five and three first appear as shortest substrings at [0,2] and [2,3].",
            ),
            (
                ["0101", [[12, 8]]],
                "Target four has no binary substring, so the result is [-1,-1].",
            ),
        ],
        [
            [s, q]
            for s, q in [
                ("0", [[0, 0]]),
                ("1", [[0, 1]]),
                ("0", [[1, 1]]),
                ("10", [[0, 2]]),
                ("01", [[0, 1]]),
                ("111", [[1, 6]]),
                ("000", [[5, 5]]),
                ("1010", [[2, 7]]),
                ("00101", [[0, 5]]),
                ("11011", [[3, 4], [1, 2]]),
                ("10000", [[0, 16]]),
                ("010101", [[7, 5]]),
                ("111000", [[1, 7], [4, 0]]),
                ("10101101", [[10, 7], [3, 12]]),
            ]
        ],
        XOR,
        [
            XOR.replace("left+32", "left+3"),
            XOR.replace("if value not in locations", "if value in locations"),
        ],
        [
            "Examines only three bits and misses larger query targets.",
            "Overwrites only existing mappings and never records a first occurrence.",
        ],
        xor_oracle,
        random_xor,
        [
            "Each query asks for the fixed target first XOR second.",
            "Precompute the shortest earliest substring for every representable value.",
            "At each start, inspect at most 32 bits because query integers fit that width; stop immediately after a leading zero.",
            "Scanning starts then ends in increasing order makes the first stored representation shortest for a fixed start and earliest among equal lengths.",
        ],
        "O(32 times string length+queries)",
        "O(32 times string length)",
        6,
    ),
    2565: entry(
        "minimum_subsequence_removal_score",
        [("s", "str"), ("t", "str")],
        "int",
        ["strings", "two pointers", "prefix and suffix matching"],
        [
            "Remove any characters from t so the remainder becomes a subsequence of s.",
            "The score is last removed index minus first removed index plus one, or zero if none are removed.",
            "Return the minimum score.",
        ],
        [
            (
                ["abacaba", "bzaa"],
                "Removing only z leaves baa, a subsequence of s, for score one.",
            ),
            (
                ["cde", "xyz"],
                "No target character occurs, so the entire length-three interval must be removed.",
            ),
        ],
        [
            [s, t]
            for s, t in [
                ("a", "a"),
                ("a", "b"),
                ("abc", "abc"),
                ("abc", "ac"),
                ("abc", "abcd"),
                ("aaaa", "aa"),
                ("abc", "zzz"),
                ("abca", "baa"),
                ("ace", "abcde"),
                ("banana", "banaa"),
                ("xyzabc", "xqzabc"),
                ("abab", "baba"),
                ("mississippi", "misisipi"),
                ("algorithm", "logarithm"),
            ]
        ],
        SUBSEQUENCE,
        [
            SUBSEQUENCE.replace("suffix[right]<=", "suffix[right]<"),
            SUBSEQUENCE.replace("right-left-1", "right-left"),
        ],
        [
            "Allows prefix and suffix matches to reuse the same source position.",
            "Adds one too many to every removed interval length.",
        ],
        subsequence_oracle,
        random_subsequence,
        [
            "Precompute where every prefix of t can finish earliest in s.",
            "Precompute where every suffix of t can start latest in s.",
            "For each kept prefix, advance a suffix pointer until its source position lies strictly after that prefix match.",
            "The removed interval between those two kept pieces is sufficient, and every feasible removal has exactly such a prefix-suffix decomposition.",
        ],
        "O(len(s)+len(t))",
        "O(len(t))",
        8,
    ),
    2567: entry(
        "minimum_score_after_two_changes",
        [("nums", "list[int]")],
        "int",
        ["arrays", "greedy", "sorting"],
        [
            "You may change exactly two array elements to arbitrary integer values.",
            "Score is the smallest pairwise difference plus the largest pairwise difference.",
            "Return the minimum achievable score.",
        ],
        [
            (
                [[1, 4, 7, 8, 5]],
                "Changing the two extreme-impact elements leaves an optimal score three.",
            ),
            (
                [[1, 4, 3]],
                "With three elements, two changes can make every value equal, yielding zero.",
            ),
        ],
        [
            [a]
            for a in [
                [1, 1, 1],
                [1, 2, 3],
                [1, 10, 20],
                [5, 4, 3, 2],
                [0, 0, 10, 10],
                [-5, 0, 5, 10],
                [1, 2, 100, 101],
                [3, 1, 4, 1, 5],
                [10, 20, 30, 40, 50],
                [-10, -5, -1, 7, 9],
                [2, 2, 3, 9, 9],
                [1, 3, 6, 10, 15, 21],
                [100, 1, 2, 3, 4, 99],
                [-20, 5, 5, 6, 7, 30],
            ]
        ],
        CHANGE,
        [
            CHANGE.replace("return min(", "return max("),
            CHANGE.replace("nums[-2]-nums[1]", "nums[-2]-nums[0]"),
        ],
        [
            "Chooses the worst of the three extreme-change patterns instead of the best.",
            "Fails to change one low extreme in the balanced one-from-each-side case.",
        ],
        change_oracle,
        random_change,
        [
            "Sort the array; only extreme values affect the largest difference after changes.",
            "The useful choices are changing two smallest, one smallest and one largest, or two largest values.",
            "Compute the remaining range for each of those three cases.",
            "Changed values can be placed inside the retained range so the minimum pairwise difference becomes zero, leaving exactly the smallest retained range.",
        ],
        "O(n log n)",
        "O(n)",
        5,
    ),
}
