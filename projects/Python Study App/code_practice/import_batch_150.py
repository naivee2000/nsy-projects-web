"""Sliding-window, binary-search, dynamic-programming, Fenwick, and prime batch 150."""

from itertools import combinations
from math import isqrt

from .import_batch_055 import entry


def take_oracle(args):
    s, k = args
    best = len(s) + 1
    for left in range(len(s) + 1):
        for right in range(len(s) - left + 1):
            taken = s[:left] + (s[len(s) - right :] if right else "")
            if all(taken.count(char) >= k for char in "abc"):
                best = min(best, left + right)
    return -1 if best > len(s) else best


def random_take(rng):
    return [
        "".join(rng.choice("abc") for _ in range(rng.randint(1, 12))),
        rng.randint(0, 5),
    ]


def tastiness_oracle(args):
    prices, k = args
    return max(
        min(abs(a - b) for a, b in combinations(chosen, 2))
        for chosen in combinations(prices, k)
    )


def random_tastiness(rng):
    n = rng.randint(2, 10)
    return [[rng.randint(1, 40) for _ in range(n)], rng.randint(2, n)]


def partitions_oracle(args):
    nums, k = args
    answer = 0
    total = sum(nums)
    for mask in range(1 << len(nums)):
        first = sum(value for index, value in enumerate(nums) if mask >> index & 1)
        answer += first >= k and total - first >= k
    return answer % (10**9 + 7)


def random_partitions(rng):
    return [
        [rng.randint(1, 12) for _ in range(rng.randint(1, 12))],
        rng.randint(1, 25),
    ]


def big_oracle(args):
    nums, k = args
    return sum(
        sum(value < nums[index] for value in nums[:index]) >= k
        and sum(value < nums[index] for value in nums[index + 1 :]) >= k
        for index in range(len(nums))
    )


def random_big(rng):
    n = rng.randint(1, 25)
    return [[rng.randint(1, n) for _ in range(n)], rng.randint(1, n)]


def prime_oracle(args):
    factors = set()
    for candidate in range(2, max(args[0]) + 1):
        if all(candidate % divisor for divisor in range(2, isqrt(candidate) + 1)):
            if any(value % candidate == 0 for value in args[0]):
                factors.add(candidate)
    return len(factors)


def random_prime(rng):
    return [[rng.randint(2, 1000) for _ in range(rng.randint(1, 15))]]


TAKE = """\
def minimum_end_takes(s,k):
    available={char:s.count(char) for char in 'abc'}
    if any(available[char]<k for char in 'abc'):return -1
    left=0;longest=0
    for right,char in enumerate(s):
        available[char]-=1
        while available[char]<k:
            available[s[left]]+=1;left+=1
        longest=max(longest,right-left+1)
    return len(s)-longest
"""

TASTINESS = """\
def maximum_candy_tastiness(price,k):
    price=sorted(price)
    def possible(gap):
        chosen=1;last=price[0]
        for value in price[1:]:
            if value-last>=gap:chosen+=1;last=value
        return chosen>=k
    low=0;high=price[-1]-price[0]
    while low<high:
        middle=(low+high+1)//2
        if possible(middle):low=middle
        else:high=middle-1
    return low
"""

PARTITIONS = """\
def count_great_partitions(nums,k):
    modulus=10**9+7
    if sum(nums)<2*k:return 0
    small=[0]*k;small[0]=1
    for value in nums:
        for total in range(k-1,value-1,-1):
            small[total]=(small[total]+small[total-value])%modulus
    return (pow(2,len(nums),modulus)-2*sum(small))%modulus
"""

BIG = """\
def count_k_big_indices(nums,k):
    values=sorted(set(nums));rank={value:index+1 for index,value in enumerate(values)}
    def add(tree,index,delta):
        while index<len(tree):tree[index]+=delta;index+=index&-index
    def query(tree,index):
        total=0
        while index:total+=tree[index];index-=index&-index
        return total
    left=[0]*(len(values)+1);right=[0]*(len(values)+1)
    for value in nums:add(right,rank[value],1)
    answer=0
    for value in nums:
        position=rank[value];add(right,position,-1)
        if query(left,position-1)>=k and query(right,position-1)>=k:answer+=1
        add(left,position,1)
    return answer
"""

PRIMES = """\
def count_distinct_product_primes(nums):
    factors=set()
    for value in nums:
        divisor=2
        while divisor*divisor<=value:
            if value%divisor==0:
                factors.add(divisor)
                while value%divisor==0:value//=divisor
            divisor+=1
        if value>1:factors.add(value)
    return len(factors)
"""


BATCH = {
    2516: entry(
        "minimum_end_takes",
        [("s", "str"), ("k", "int")],
        "int",
        ["strings", "sliding window", "counting"],
        [
            "The string contains only a, b, and c and has length at least one.",
            "One move removes the current leftmost or rightmost character.",
            "Return the fewest moves collecting at least k of every character, or -1 if impossible.",
        ],
        [
            (
                ["aabaaaacaabc", 2],
                "Keeping the longest valid middle leaves eight characters to take from the ends.",
            ),
            (["a", 1], "No b or c exists, so collecting one of each is impossible."),
        ],
        [
            [s, k]
            for s, k in [
                ("a", 0),
                ("abc", 1),
                ("abc", 2),
                ("aaabbbccc", 2),
                ("aaabbbccc", 3),
                ("cba", 1),
                ("aaaa", 1),
                ("abccba", 1),
                ("abccba", 2),
                ("acbacbac", 2),
                ("bbbbacac", 2),
                ("cabac", 1),
                ("abcabcabc", 2),
                ("ccbaaabc", 2),
            ]
        ],
        TAKE,
        [
            TAKE.replace("available[char]<k", "available[char]<=k"),
            TAKE.replace("return len(s)-longest", "return longest"),
        ],
        [
            "Shrinks when exactly k copies remain outside, discarding valid middle characters.",
            "Returns the kept middle length rather than the number taken from both ends.",
        ],
        take_oracle,
        random_take,
        [
            "Taking a prefix and suffix is equivalent to leaving one contiguous middle substring.",
            "Count all letters, then grow a middle window while at least k of each remain outside it.",
            "Move the left boundary whenever adding the right character would leave too few copies outside.",
            "The longest valid middle minimizes the complementary prefix-plus-suffix length; insufficient totals make the task impossible.",
        ],
        "O(n)",
        "O(1)",
        6,
    ),
    2517: entry(
        "maximum_candy_tastiness",
        [("price", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "binary search", "greedy", "sorting"],
        [
            "Choose exactly k distinct candy positions; equal prices are allowed.",
            "Tastiness is the smallest absolute price difference among chosen candies.",
            "Return the largest achievable tastiness.",
        ],
        [
            (
                [[13, 5, 1, 8, 21, 2], 3],
                "Prices 5, 13, and 21 have minimum pairwise difference eight.",
            ),
            (
                [[1, 3, 1], 2],
                "Choosing prices one and three produces the maximum difference two.",
            ),
        ],
        [
            [p, k]
            for p, k in [
                ([7, 7], 2),
                ([1, 2], 2),
                ([1, 10, 20], 2),
                ([1, 10, 20], 3),
                ([5, 5, 5, 5], 3),
                ([1, 2, 4, 8], 3),
                ([8, 1, 4, 12], 2),
                ([2, 3, 5, 9, 12], 4),
                ([100, 1, 50, 75], 3),
                ([1, 1, 2, 2, 3], 3),
                ([4, 9, 15, 22, 30], 5),
                ([4, 9, 15, 22, 30], 2),
                ([2, 6, 13, 21, 31, 44], 4),
                ([9, 1, 9, 1, 5], 3),
            ]
        ],
        TASTINESS,
        [
            TASTINESS.replace("value-last>=gap", "value-last>gap"),
            TASTINESS.replace("chosen=1", "chosen=0"),
        ],
        [
            "Rejects selections whose minimum difference equals the tested gap.",
            "Forgets that the cheapest candy is already selected by the greedy feasibility check.",
        ],
        tastiness_oracle,
        random_tastiness,
        [
            "Sort prices so only adjacent chosen prices determine the minimum difference.",
            "For a proposed gap, greedily choose the earliest next price at least that far away.",
            "Binary-search the largest gap for which the greedy scan chooses at least k candies.",
            "Feasibility is monotone, and earliest choices leave maximum room for later candies, proving both the greedy check and binary search.",
        ],
        "O(n log n+n log range)",
        "O(n)",
        6,
    ),
    2518: entry(
        "count_great_partitions",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "dynamic programming", "counting"],
        [
            "Assign every positive array element to exactly one of two labeled groups.",
            "A partition is great when both group sums are at least k.",
            "Return the number of assignments modulo 1,000,000,007.",
        ],
        [
            (
                [[1, 2, 3, 4], 4],
                "Exactly six labeled assignments leave both group sums at least four.",
            ),
            (
                [[3, 3, 3], 4],
                "Every split leaves one group below four, so the answer is zero.",
            ),
        ],
        [
            [a, k]
            for a, k in [
                ([6, 6], 2),
                ([1], 1),
                ([2, 2], 2),
                ([1, 1, 1, 1], 2),
                ([1, 2, 3], 3),
                ([5, 1, 1], 2),
                ([10, 1, 1], 5),
                ([2, 3, 5, 7], 5),
                ([4, 4, 4, 4], 8),
                ([1, 2, 4, 8], 7),
                ([3, 6, 9], 6),
                ([2, 2, 3, 3, 4], 6),
                ([20, 1, 1, 1], 10),
                ([1, 1, 2, 2, 3, 3], 5),
            ]
        ],
        PARTITIONS,
        [
            PARTITIONS.replace("sum(nums)<2*k", "sum(nums)<=2*k"),
            PARTITIONS.replace("2*sum(small)", "sum(small)"),
        ],
        [
            "Rejects the valid boundary where total sum equals exactly twice k.",
            "Subtracts bad assignments for only one of the two labeled groups.",
        ],
        partitions_oracle,
        random_partitions,
        [
            "Start with all 2^n labeled assignments and subtract assignments with a group sum below k.",
            "When total sum is at least 2k, the events that either group is too small are disjoint and symmetric.",
            "Use descending one-dimensional subset-sum DP to count subsets for every sum from zero through k-1.",
            "Twice the number of small-sum subsets is exactly the number of bad labeled assignments; if total is below 2k no great partition exists.",
        ],
        "O(nk)",
        "O(k)",
        8,
    ),
    2519: entry(
        "count_k_big_indices",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "Fenwick trees", "coordinate compression"],
        [
            "An index is k-big when at least k earlier and k later values are strictly smaller than its value.",
            "Equal values do not count as smaller.",
            "Return the number of k-big indices.",
        ],
        [
            (
                [[2, 3, 6, 5, 2, 3], 2],
                "Values six and five each have two smaller values on both sides.",
            ),
            (
                [[1, 1, 1], 3],
                "No position has three indices on either side, much less smaller values.",
            ),
        ],
        [
            [a, k]
            for a, k in [
                ([1], 1),
                ([1, 2, 1], 1),
                ([1, 3, 1], 1),
                ([3, 1, 3], 1),
                ([1, 2, 3, 2, 1], 1),
                ([1, 2, 3, 2, 1], 2),
                ([2, 2, 3, 2, 2], 2),
                ([1, 4, 2, 5, 1], 1),
                ([5, 4, 3, 2, 1], 1),
                ([1, 2, 3, 4, 5], 1),
                ([2, 1, 4, 3, 2, 1], 2),
                ([1, 1, 5, 1, 1], 2),
                ([3, 1, 2, 4, 2, 1, 3], 2),
                ([1, 2, 6, 3, 5, 2, 1], 2),
            ]
        ],
        BIG,
        [
            BIG.replace(">=k", ">k"),
            BIG.replace(" and query(right,position-1)>=k", ""),
        ],
        [
            "Requires more than k smaller values on each side instead of accepting exactly k.",
            "Checks only the earlier side and ignores whether enough smaller later values exist.",
        ],
        big_oracle,
        random_big,
        [
            "Process each index while maintaining frequency structures for values to its left and right.",
            "Coordinate-compress values and use prefix sums through rank minus one to count strictly smaller values.",
            "Remove the current value from the right tree, query both trees, then add it to the left tree.",
            "The two Fenwick trees represent exactly the earlier and later indices at every step, so both threshold checks match the definition.",
        ],
        "O(n log n)",
        "O(n)",
        8,
    ),
    2521: entry(
        "count_distinct_product_primes",
        [("nums", "list[int]")],
        "int",
        ["arrays", "number theory", "prime factorization", "sets"],
        [
            "Every array value is an integer from 2 through 1000.",
            "A prime contributes once if it divides the product of all values, regardless of exponent.",
            "Return the number of distinct contributing primes.",
        ],
        [
            (
                [[2, 4, 3, 7, 10, 6]],
                "The product has exactly the prime factors 2, 3, 5, and 7.",
            ),
            (
                [[2, 4, 8, 16]],
                "Every value contains only prime factor two, so the distinct count is one.",
            ),
        ],
        [
            [values]
            for values in [
                [2],
                [3],
                [4],
                [6],
                [49],
                [997],
                [2, 3],
                [6, 10, 15],
                [12, 18, 25],
                [7, 14, 21, 35],
                [8, 9, 25, 49],
                [30, 30, 30],
                [2, 11, 121, 13],
                [1000, 999, 998],
            ]
        ],
        PRIMES,
        [
            PRIMES.replace("if value>1:factors.add(value)", ""),
            PRIMES.replace("factors.add(divisor)", "factors.add(value)"),
        ],
        [
            "Loses a prime factor that remains after trial division reaches its square root.",
            "Records the shrinking composite value instead of the prime divisor that was found.",
        ],
        prime_oracle,
        random_prime,
        [
            "A prime divides the total product exactly when it divides at least one array value.",
            "Factor each number independently and insert discovered primes into one shared set.",
            "After dividing out each small factor completely, add any residual value greater than one.",
            "Trial division finds every prime factor, and the set removes repetitions within and across numbers.",
        ],
        "O(n sqrt(max value))",
        "O(number of distinct primes)",
        5,
    ),
}
