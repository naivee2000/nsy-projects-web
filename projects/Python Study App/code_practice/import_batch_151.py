"""Greedy strings, sieves, window scores, bit identities, and power batch 151."""

from collections import Counter
from itertools import product
from math import isqrt

from .import_batch_055 import entry


def partition_oracle(args):
    s, k = args
    best = [len(s) + 1] * (len(s) + 1)
    best[0] = 0
    for end in range(1, len(s) + 1):
        for start in range(end):
            if int(s[start:end]) <= k:
                best[end] = min(best[end], best[start] + 1)
    return -1 if best[-1] > len(s) else best[-1]


def random_partition(rng):
    return [
        "".join(rng.choice("123456789") for _ in range(rng.randint(1, 14))),
        rng.randint(1, 5000),
    ]


def is_prime(value):
    return value >= 2 and all(value % d for d in range(2, isqrt(value) + 1))


def closest_oracle(args):
    left, right = args
    primes = [value for value in range(left, right + 1) if is_prime(value)]
    return min(
        ([a, b] for a, b in zip(primes, primes[1:])),
        key=lambda pair: pair[1] - pair[0],
        default=[-1, -1],
    )


def random_closest(rng):
    left = rng.randint(1, 1500)
    return [left, left + rng.randint(0, 300)]


def frequency_oracle(args):
    nums, k = args
    modulus = 10**9 + 7
    return max(
        sum(
            pow(value, count, modulus)
            for value, count in Counter(nums[i : i + k]).items()
        )
        % modulus
        for i in range(len(nums) - k + 1)
    )


def random_frequency(rng):
    n = rng.randint(1, 20)
    return [[rng.randint(1, 15) for _ in range(n)], rng.randint(1, n)]


def beauty_oracle(args):
    nums = args[0]
    answer = 0
    for first, second, third in product(nums, repeat=3):
        answer ^= (first | second) & third
    return answer


def random_beauty(rng):
    return [[rng.randint(1, 255) for _ in range(rng.randint(1, 8))]]


def power_oracle(args):
    stations, radius, extra = args
    best = -1

    def visit(index, left, additions):
        nonlocal best
        if index == len(stations) - 1:
            candidate = additions + [left]
            powers = [
                sum(stations[max(0, city - radius) : city + radius + 1])
                + sum(candidate[max(0, city - radius) : city + radius + 1])
                for city in range(len(stations))
            ]
            best = max(best, min(powers))
            return
        for amount in range(left + 1):
            visit(index + 1, left - amount, additions + [amount])

    visit(0, extra, [])
    return best


def random_power(rng):
    n = rng.randint(1, 6)
    return [
        [rng.randint(0, 6) for _ in range(n)],
        rng.randint(0, n - 1),
        rng.randint(0, 7),
    ]


PARTITION = """\
def minimum_bounded_partition(s,k):
    pieces=0;start=0
    while start<len(s):
        value=0;end=start
        while end<len(s) and value*10+int(s[end])<=k:
            value=value*10+int(s[end]);end+=1
        if end==start:return -1
        pieces+=1;start=end
    return pieces
"""

CLOSEST = """\
def closest_primes_in_range(left,right):
    composite=[False]*(right+1)
    for value in range(2,int(right**0.5)+1):
        if not composite[value]:
            for multiple in range(value*value,right+1,value):composite[multiple]=True
    previous=None;answer=[-1,-1]
    for value in range(max(2,left),right+1):
        if not composite[value]:
            if previous is not None and (answer[0]<0 or value-previous<answer[1]-answer[0]):answer=[previous,value]
            previous=value
    return answer
"""

FREQUENCY = """\
def maximum_window_frequency_score(nums,k):
    modulus=10**9+7;counts={};score=0
    def change(value,delta):
        nonlocal score
        old=counts.get(value,0)
        if old:score-=pow(value,old,modulus)
        counts[value]=old+delta
        if counts[value]:score+=pow(value,counts[value],modulus)
        score%=modulus
    for value in nums[:k]:change(value,1)
    answer=score
    for index in range(k,len(nums)):
        change(nums[index-k],-1);change(nums[index],1);answer=max(answer,score)
    return answer
"""

BEAUTY = """\
def xor_beauty(nums):
    answer=0
    for value in nums:answer^=value
    return answer
"""

POWER = """\
def maximum_minimum_city_power(stations,r,k):
    n=len(stations);prefix=[0]
    for value in stations:prefix.append(prefix[-1]+value)
    base=[prefix[min(n,i+r+1)]-prefix[max(0,i-r)] for i in range(n)]
    def possible(target):
        changes=[0]*(n+1);active=0;remaining=k
        for city in range(n):
            active+=changes[city]
            need=max(0,target-base[city]-active)
            if need>remaining:return False
            remaining-=need;active+=need
            changes[min(n,city+2*r+1)]-=need
        return True
    low=min(base);high=low+k
    while low<high:
        middle=(low+high+1)//2
        if possible(middle):low=middle
        else:high=middle-1
    return low
"""


BATCH = {
    2522: entry(
        "minimum_bounded_partition",
        [("s", "str"), ("k", "int")],
        "int",
        ["strings", "greedy", "dynamic programming"],
        [
            "The string contains digits 1 through 9, so substrings have no leading zero.",
            "Partition every digit into contiguous nonempty pieces whose integer values are at most k.",
            "Return the minimum piece count, or -1 if even one digit cannot fit.",
        ],
        [
            (
                ["165462", 60],
                "The minimum partition 16 | 54 | 6 | 2 uses four bounded values.",
            ),
            (
                ["238182", 5],
                "Digit eight exceeds five by itself, so no valid partition exists.",
            ),
        ],
        [
            [s, k]
            for s, k in [
                ("1", 1),
                ("9", 8),
                ("9", 9),
                ("123", 123),
                ("123", 12),
                ("999", 99),
                ("1111", 11),
                ("54321", 100),
                ("314159", 50),
                ("22222", 2),
                ("987654", 1000),
                ("123456789", 9999),
                ("818181", 81),
                ("19991", 200),
            ]
        ],
        PARTITION,
        [
            PARTITION.replace("<=k", "<k"),
            PARTITION.replace("pieces=0", "pieces=1"),
        ],
        [
            "Rejects a piece whose value is exactly k.",
            "Starts with an extra piece before consuming any digits.",
        ],
        partition_oracle,
        random_partition,
        [
            "Because all digits are positive, extending a piece can only increase its value.",
            "From each position, take the longest prefix whose numeric value does not exceed k.",
            "If the first digit already exceeds k, return -1; otherwise repeat from the first unused digit.",
            "Any solution must cut no later than the greedy cut, so exchanging its first cut for the greedy one cannot increase the remaining piece count.",
        ],
        "O(n)",
        "O(1)",
        5,
    ),
    2523: entry(
        "closest_primes_in_range",
        [("left", "int"), ("right", "int")],
        "list[int]",
        ["number theory", "sieve", "arrays"],
        [
            "Find two primes left <= first < second <= right with minimum difference.",
            "If several pairs tie, return the pair with the smaller first prime.",
            "Return [-1,-1] when the interval contains fewer than two primes.",
        ],
        [
            ([10, 19], "Primes 11 and 13 are the closest pair, separated by two."),
            ([4, 6], "The interval contains only prime five, so no pair exists."),
        ],
        [
            [a, b]
            for a, b in [
                (1, 2),
                (1, 3),
                (2, 3),
                (2, 2),
                (3, 5),
                (5, 11),
                (8, 20),
                (14, 16),
                (20, 30),
                (100, 140),
                (197, 211),
                (1, 100),
                (500, 600),
                (997, 1009),
            ]
        ],
        CLOSEST,
        [
            CLOSEST.replace("max(2,left)", "max(1,left)"),
            CLOSEST.replace(
                "value-previous<answer[1]-answer[0]",
                "value-previous<=answer[1]-answer[0]",
            ),
        ],
        [
            "Treats one as prime because the sieve marks only composites.",
            "Replaces an earlier closest pair when a later pair merely ties it.",
        ],
        closest_oracle,
        random_closest,
        [
            "Generate primality information once for every number through right.",
            "The Sieve of Eratosthenes marks multiples beginning at each prime's square.",
            "Scan primes inside the interval and compare each consecutive pair with the best gap.",
            "A minimum-gap prime pair must be consecutive in sorted prime order, and strict improvement preserves the earliest tied pair.",
        ],
        "O(right log log right)",
        "O(right)",
        5,
    ),
    2524: entry(
        "maximum_window_frequency_score",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "sliding window", "hash maps", "modular arithmetic"],
        [
            "For a window, each distinct value x with frequency f contributes x^f modulo 1,000,000,007.",
            "The window score is the modular sum of those contributions.",
            "Return the maximum score among all contiguous windows of exactly k elements.",
        ],
        [
            (
                [[1, 1, 1, 2, 1, 2], 3],
                "Window [1,2,1] scores 1^2 + 2^1 = 3, while [2,1,2] scores 2^2 + 1 = 5.",
            ),
            ([[1, 1, 2, 2], 4], "The only window scores 1^2 + 2^2 = 5."),
        ],
        [
            [a, k]
            for a, k in [
                ([1], 1),
                ([2, 2], 1),
                ([2, 2], 2),
                ([1, 2, 3], 2),
                ([3, 3, 3], 2),
                ([2, 3, 2, 3], 3),
                ([5, 1, 5, 1, 5], 3),
                ([4, 4, 2, 2, 4], 4),
                ([1, 2, 2, 2, 3], 3),
                ([10, 10, 1], 2),
                ([2, 4, 8, 16], 4),
                ([7, 7, 7, 1, 1], 3),
                ([3, 1, 3, 1, 3, 1], 2),
                ([6, 2, 6, 2, 6, 2], 5),
            ]
        ],
        FREQUENCY,
        [
            FREQUENCY.replace(
                "pow(value,counts[value],modulus)", "pow(value,counts[value]-1,modulus)"
            ),
            FREQUENCY.replace("answer=max(answer,score)", "answer=min(answer,score)"),
        ],
        [
            "Uses exponent frequency minus one for updated contributions.",
            "Keeps the minimum window score instead of the maximum.",
        ],
        frequency_oracle,
        random_frequency,
        [
            "Maintain a frequency map and the current score for one length-k window.",
            "Before changing a frequency, subtract its old power contribution; afterward add its new one.",
            "Slide one position at a time by removing the outgoing value and adding the incoming value.",
            "Each update preserves the exact score invariant, so taking the maximum over all window positions returns the required result.",
        ],
        "O(n log k) modular exponentiation",
        "O(distinct window values)",
        8,
    ),
    2527: entry(
        "xor_beauty",
        [("nums", "list[int]")],
        "int",
        ["arrays", "bit manipulation", "algebra"],
        [
            "For every ordered index triplet (i,j,k), compute (nums[i] OR nums[j]) AND nums[k].",
            "XOR all n cubed triplet values together.",
            "Return the resulting XOR-beauty.",
        ],
        [
            (
                [[1, 4]],
                "The XOR across all eight ordered triplets simplifies to 1 XOR 4 = 5.",
            ),
            (
                [[15, 45, 20, 2, 34, 35, 5, 44, 32, 30]],
                "Bitwise cancellation leaves the same value as XORing the array, which is 34.",
            ),
        ],
        [
            [values]
            for values in [
                [1],
                [2],
                [1, 1],
                [1, 2],
                [3, 5],
                [7, 7, 7],
                [1, 2, 3],
                [4, 8, 16],
                [255, 1],
                [6, 10, 12],
                [31, 63, 127],
                [2, 2, 3, 3],
                [5, 9, 17, 33],
                [100, 200, 255],
            ]
        ],
        BEAUTY,
        [
            BEAUTY.replace("answer^=value", "answer|=value"),
            BEAUTY.replace("answer^=value", "answer&=value"),
        ],
        [
            "Combines array values with OR instead of XOR after the cancellations.",
            "Combines values with AND from an initial zero, always producing zero.",
        ],
        beauty_oracle,
        random_beauty,
        [
            "Analyze each bit independently and use parity because the final operation is XOR.",
            "Expanding OR into XOR and AND terms makes all cross-index contributions appear an even number of times.",
            "Only each original value's surviving diagonal contribution remains.",
            "Therefore the cubic expression equals the XOR of all input values, which can be accumulated in one scan.",
        ],
        "O(n)",
        "O(1)",
        5,
    ),
    2528: entry(
        "maximum_minimum_city_power",
        [("stations", "list[int]"), ("r", "int"), ("k", "int")],
        "int",
        ["arrays", "binary search", "greedy", "prefix sums"],
        [
            "A station powers every city within distance r, including its own city.",
            "Place at most k additional stations at any city, allowing multiple stations together.",
            "Maximize the minimum total power received by any city.",
        ],
        [
            (
                [[1, 2, 4, 5, 0], 1, 2],
                "Placing both extra stations strategically raises every city's power to at least five.",
            ),
            (
                [[4, 4, 4, 4], 0, 3],
                "With radius zero, three additions cannot raise all four cities, so the minimum remains four.",
            ),
        ],
        [
            [a, r, k]
            for a, r, k in [
                ([0], 0, 0),
                ([0], 0, 5),
                ([3], 0, 2),
                ([0, 0], 0, 2),
                ([1, 0], 1, 1),
                ([1, 0, 0], 1, 3),
                ([0, 0, 0], 1, 2),
                ([1, 2, 3], 0, 3),
                ([1, 2, 3], 2, 4),
                ([5, 0, 0, 5], 1, 3),
                ([0, 1, 0, 1, 0], 1, 4),
                ([2, 0, 2, 0, 2], 2, 2),
                ([1, 1, 1, 1, 1], 0, 5),
                ([3, 1, 4, 1, 5, 9], 2, 6),
            ]
        ],
        POWER,
        [
            POWER.replace("city+2*r+1", "city+r+1"),
            POWER.replace("high=low+k", "high=low"),
        ],
        [
            "Expires a greedily placed station too early instead of after its full radius coverage.",
            "Never searches above the current minimum, ignoring all additional stations.",
        ],
        power_oracle,
        random_power,
        [
            "Use prefix sums to compute every city's initial power.",
            "Binary-search a target minimum and test whether at most k new stations can achieve it.",
            "Scan left to right; whenever a city is short, place the needed stations at the farthest city to its right that still covers it.",
            "The farthest placement maximizes help to future cities, while a difference array tracks when added coverage expires; this proves greedy feasibility is monotone.",
        ],
        "O(n log(answer range))",
        "O(n)",
        8,
    ),
}
