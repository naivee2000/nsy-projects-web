"""Greedy, heap, number theory, and prefix-sum batch 163."""

from collections import deque
from itertools import product

from .import_batch_055 import entry


def mex_oracle(args):
    nums, value = args

    def can_cover(limit):
        choices = [[i for i, number in enumerate(nums) if (number - target) % value == 0]
                   for target in range(limit)]
        used = set()

        def match(target):
            if target == limit:
                return True
            for index in choices[target]:
                if index not in used:
                    used.add(index)
                    if match(target + 1):
                        return True
                    used.remove(index)
            return False

        return match(0)

    answer = 0
    while answer < len(nums) and can_cover(answer + 1):
        answer += 1
    return answer


def random_mex(rng):
    return [[rng.randint(-30, 30) for _ in range(rng.randint(1, 8))], rng.randint(1, 8)]


def prefix_oracle(args):
    start = tuple(args[0])

    def valid(values):
        total = 0
        for value in values:
            total += value
            if total < 0:
                return False
        return True

    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        values, moves = queue.popleft()
        if valid(values):
            return moves
        for index in range(len(values) - 1):
            following = values[:index] + values[index + 1 :] + (values[index],)
            if following not in seen:
                seen.add(following)
                queue.append((following, moves + 1))
    raise AssertionError("random inputs must have non-negative total")


def random_prefix(rng):
    length = rng.randint(1, 7)
    values = [rng.randint(-8, 8) for _ in range(length)]
    if sum(values) < 0:
        values[rng.randrange(length)] += -sum(values)
    return [values]


def items_oracle(args):
    ones, zeros, negatives, k = args
    best = -10**9
    for take_ones in range(min(ones, k) + 1):
        for take_zeros in range(min(zeros, k - take_ones) + 1):
            take_negatives = k - take_ones - take_zeros
            if take_negatives <= negatives:
                best = max(best, take_ones - take_negatives)
    return best


def random_items(rng):
    counts = [rng.randint(0, 12) for _ in range(3)]
    if sum(counts) == 0:
        counts[rng.randrange(3)] = 1
    return counts + [rng.randint(1, sum(counts))]


def prime_oracle(args):
    def primes_below(value):
        result = []
        for candidate in range(2, value):
            if all(candidate % divisor for divisor in range(2, int(candidate**0.5) + 1)):
                result.append(candidate)
        return result

    choices = [[value] + [value - prime for prime in primes_below(value)] for value in args[0]]
    return any(all(a < b for a, b in zip(values, values[1:])) for values in product(*choices))


def random_prime(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 6))]]


def operations_oracle(args):
    nums, queries = args
    return [sum(abs(value - query) for value in nums) for query in queries]


def random_operations(rng):
    return [
        [rng.randint(1, 60) for _ in range(rng.randint(1, 12))],
        [rng.randint(1, 60) for _ in range(rng.randint(1, 10))],
    ]


MEX = """\
def maximum_mex_after_steps(nums,value):
    counts=[0]*value
    for number in nums:counts[number%value]+=1
    answer=0
    while counts[answer%value]:
        counts[answer%value]-=1;answer+=1
    return answer
"""

PREFIX = """\
def minimum_moves_for_nonnegative_prefix(nums):
    import heapq
    negatives=[];total=moves=0
    for value in nums:
        total+=value
        if value<0:heapq.heappush(negatives,value)
        if total<0:
            total-=heapq.heappop(negatives);moves+=1
    return moves
"""

ITEMS = """\
def maximum_k_item_sum(numOnes,numZeros,numNegOnes,k):
    take=min(numOnes,k);answer=take;k-=take
    k-=min(numZeros,k)
    return answer-k
"""

PRIME = """\
def can_increase_by_prime_subtraction(nums):
    limit=max(nums);is_prime=[True]*limit
    if limit>0:is_prime[0]=False
    if limit>1:is_prime[1]=False
    for value in range(2,int(limit**0.5)+1):
        if is_prime[value]:
            for multiple in range(value*value,limit,value):is_prime[multiple]=False
    previous=0
    for value in nums:
        chosen=value
        for prime in range(value-1,1,-1):
            if is_prime[prime] and value-prime>previous:
                chosen=value-prime;break
        if chosen<=previous:return False
        previous=chosen
    return True
"""

OPERATIONS = """\
def operations_to_match_queries(nums,queries):
    import bisect
    ordered=sorted(nums);prefix=[0]
    for value in ordered:prefix.append(prefix[-1]+value)
    answer=[]
    for query in queries:
        index=bisect.bisect_left(ordered,query)
        left=query*index-prefix[index]
        right=prefix[-1]-prefix[index]-query*(len(ordered)-index)
        answer.append(left+right)
    return answer
"""


BATCH = {
    2598: entry(
        "maximum_mex_after_steps",
        [("nums", "list[int]"), ("value", "int")],
        "int",
        ["arrays", "hash maps", "greedy", "math"],
        [
            "You may add or subtract value from any array element any number of times.",
            "The MEX is the smallest non-negative integer missing after those operations.",
            "Return the largest MEX that can be achieved.",
        ],
        [
            ([[1, -10, 7, 13, 6, 8], 5], "Residues can represent zero through three, so the best MEX is four."),
            ([[1, -10, 7, 13, 6, 8], 7], "Only zero and one can both be represented before residue two is unavailable."),
        ],
        [[a, v] for a, v in [
            ([0], 1), ([1], 2), ([-1], 3), ([0, 1], 2), ([2, 2], 2),
            ([-5, 0, 5], 5), ([3, 6, 9], 3), ([1, 2, 3], 5),
            ([7, -7, 14, 1], 7), ([0, 0, 0, 0], 2), ([4, 8, 12, 16], 4),
            ([-8, -3, 2, 7], 5), ([10, 11, 12, 13, 14], 5), ([6, 13, 20, 27, 34, 0], 7),
        ]],
        MEX,
        [MEX.replace("for number in nums:counts[number%value]+=1", "for number in nums:\n        if number>=0:counts[number%value]+=1"), MEX.replace("answer%value", "(answer+1)%value")],
        ["Ignores negative input values even though operations can move them into the non-negative range.", "Checks the next residue instead of the current candidate's residue."],
        mex_oracle,
        random_mex,
        [
            "Adding or subtracting value never changes an integer's remainder modulo value.",
            "Count how many input values belong to each remainder class.",
            "Try to construct zero, one, two, and so on, consuming one matching remainder each time.",
            "The first candidate whose remainder count is exhausted is exactly the maximum achievable MEX.",
        ],
        "O(n + answer)", "O(value)", 6,
    ),
    2599: entry(
        "minimum_moves_for_nonnegative_prefix",
        [("nums", "list[int]")],
        "int",
        ["arrays", "greedy", "heaps", "prefix sums"],
        [
            "One operation removes any element and appends it to the end.",
            "All prefix sums in the final order must be non-negative; a solution is guaranteed.",
            "Return the minimum number of operations.",
        ],
        [
            ([[2, 3, -5, 4]], "The prefix sums are already 2, 5, 0, and 4, so no move is needed."),
            ([[3, -5, -2, 6]], "Moving negative five to the end produces non-negative prefix sums in one operation."),
        ],
        [[a] for a in [
            [0], [5], [1, -1], [-1, 1], [2, -3, 1], [4, -5, 2],
            [1, 2, -4, 2], [5, -2, -2, -2, 1], [1, -2, 3, -2],
            [10, -20, 5, 5], [2, -1, -5, 4, 3], [3, -4, -4, 5, 2],
            [6, -7, -1, 2], [1, -5, 2, 2, 0],
        ]],
        PREFIX,
        [PREFIX.replace("return moves", "return moves+1 if moves else 0"), PREFIX.replace("if total<0:", "if total<=0 and negatives:")],
        ["Counts one extra operation after any repair has been made.", "Treats a zero prefix as invalid and moves a negative unnecessarily."],
        prefix_oracle,
        random_prefix,
        [
            "Scan the original order and track its running sum.",
            "Keep every negative value seen so far in a min-heap.",
            "When the sum becomes negative, defer the most negative available value; this restores the most capacity with one move.",
            "Each forced repair is necessary, and choosing the largest-magnitude negative leaves the best possible prefix for later positions.",
        ],
        "O(n log n)", "O(n)", 6,
    ),
    2600: entry(
        "maximum_k_item_sum",
        [("numOnes", "int"), ("numZeros", "int"), ("numNegOnes", "int"), ("k", "int")],
        "int",
        ["greedy", "math"],
        [
            "A bag contains the given counts of items valued one, zero, and negative one.",
            "Choose exactly k available items.",
            "Return the maximum possible sum.",
        ],
        [
            ([3, 2, 0, 2], "Choose two one-valued items for sum two."),
            ([3, 2, 0, 4], "Choose all three ones and one zero for sum three."),
        ],
        [[o, z, n, k] for o, z, n, k in [
            (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (2, 0, 3, 4),
            (0, 2, 3, 4), (5, 0, 5, 7), (1, 5, 2, 6), (4, 4, 4, 12),
            (10, 1, 10, 10), (2, 3, 4, 5), (0, 7, 2, 3), (6, 0, 0, 0),
            (1, 1, 8, 9), (12, 8, 5, 17),
        ]],
        ITEMS,
        [ITEMS.replace("take=min(numOnes,k)", "take=min(numZeros,k)"), ITEMS.replace("return answer-k", "return answer+k")],
        ["Selects zero-valued items before ones.", "Adds required negative-one items instead of subtracting them."],
        items_oracle,
        random_items,
        [
            "Every one-valued item is better than every zero or negative-one item.",
            "Take as many ones as possible, then zeros.",
            "Any remaining required items must be negative ones and reduce the result.",
            "This fixed priority is optimal because exchanging a lower-valued chosen item for a higher-valued available one always improves the sum.",
        ],
        "O(1)", "O(1)", 3,
    ),
    2601: entry(
        "can_increase_by_prime_subtraction",
        [("nums", "list[int]")],
        "bool",
        ["arrays", "binary search", "greedy", "number theory"],
        [
            "For each index at most once, you may subtract a prime strictly smaller than its value.",
            "Determine whether the resulting array can be strictly increasing.",
            "Return True when possible and False otherwise.",
        ],
        [
            ([[4, 9, 6, 10]], "Subtracting three and seven from the first two values yields [1, 2, 6, 10]."),
            ([[5, 8, 3]], "The final value three leaves too little room for both earlier positions."),
        ],
        [[a] for a in [
            [1], [2], [1, 2], [2, 2], [3, 3], [4, 3], [5, 4], [6, 8, 11, 12],
            [10, 5], [2, 1], [7, 7, 7], [9, 6, 10], [20, 10, 15], [3, 5, 4, 9],
        ]],
        PRIME,
        [PRIME.replace("range(value-1,1,-1)", "range(2,value)"), PRIME.replace("value-prime>previous", "value-prime>=previous")],
        ["Chooses the smallest usable prime instead of minimizing the current resulting value.", "Allows equal adjacent values rather than requiring strict increase."],
        prime_oracle,
        random_prime,
        [
            "Process left to right and make each value as small as possible while remaining above the previous result.",
            "Precompute primality up to the largest input value.",
            "For each value, subtract the largest prime that still leaves a result greater than previous.",
            "The greedy choice leaves maximum room for every later element; if even the unchanged value is too small, no solution exists.",
        ],
        "O(M log log M + nM)", "O(M)", 6,
    ),
    2602: entry(
        "operations_to_match_queries",
        [("nums", "list[int]"), ("queries", "list[int]")],
        "list[int]",
        ["arrays", "binary search", "prefix sums", "sorting"],
        [
            "For each query, independently make every number equal to that query using unit increments or decrements.",
            "The array resets before the next query.",
            "Return the minimum operation count for every query in order.",
        ],
        [
            ([[3, 1, 6, 8], [1, 5]], "The absolute differences total fourteen for one and ten for five."),
            ([[2, 9, 6, 3], [10]], "Increasing all four values to ten takes 8 + 1 + 4 + 7 = 20 operations."),
        ],
        [[a, q] for a, q in [
            ([1], [1]), ([1], [2]), ([5], [1, 5, 10]), ([1, 2], [1]),
            ([1, 2], [3]), ([1, 3, 5], [3]), ([10, 10, 10], [1, 10, 20]),
            ([1, 100], [50]), ([4, 1, 7, 2], [0, 4, 8]), ([2, 8, 3, 9], [5, 6]),
            ([1, 2, 3, 4, 5], [1, 5]), ([9, 2, 6, 3, 8], [4]),
            ([1000000000, 1], [500000000]), ([7, 1, 7, 1, 7], [1, 7, 4]),
        ]],
        OPERATIONS,
        [OPERATIONS.replace("query*(len(ordered)-index)", "query*(len(ordered)-index-1)"), OPERATIONS.replace("left+right", "abs(left-right)")],
        ["Omits one value from the right side's query contribution.", "Subtracts the two sides' costs instead of adding them."],
        operations_oracle,
        random_operations,
        [
            "Sort nums once and build prefix sums.",
            "Binary-search the first value not smaller than each query.",
            "Use the prefix sum to compute the cost of raising the left side and lowering the right side.",
            "Adding those independent costs gives the minimum for one query in logarithmic time after sorting.",
        ],
        "O((n + q) log n)", "O(n)", 6,
    ),
}
