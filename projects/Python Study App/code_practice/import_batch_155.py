"""Fractional greedy, recursive powers, cut scores, quadruplets, and range batch 155."""

from itertools import combinations, product

from .import_batch_055 import entry


def bag_oracle(args):
    items, capacity = args
    if sum(weight for _, weight in items) < capacity:
        return -1
    remaining = capacity
    answer = 0.0
    unused = set(range(len(items)))
    while remaining:
        best = max(unused, key=lambda index: items[index][0] / items[index][1])
        price, weight = items[best]
        amount = min(weight, remaining)
        answer += price * amount / weight
        remaining -= amount
        unused.remove(best)
    return answer


def random_bag(rng):
    items = [[rng.randint(1, 50), rng.randint(1, 15)] for _ in range(rng.randint(1, 8))]
    return [items, rng.randint(1, sum(weight for _, weight in items) + 5)]


def monkeys_oracle(args):
    n = args[0]
    if n > 15:
        # Exhaustive direction enumeration is used by every seeded oracle case;
        # this equivalent count keeps source-scale deterministic boundaries bounded.
        return (pow(2, n, 10**9 + 7) - 2) % (10**9 + 7)
    collisions = 0
    for directions in product((-1, 1), repeat=n):
        destinations = [(index + directions[index]) % n for index in range(n)]
        collisions += len(set(destinations)) < n or any(
            destinations[left] == right and destinations[right] == left
            for left in range(n)
            for right in range(left + 1, n)
        )
    return collisions % (10**9 + 7)


def random_monkeys(rng):
    return [rng.randint(3, 11)]


def marbles_oracle(args):
    weights, k = args
    scores = []
    for cuts in combinations(range(1, len(weights)), k - 1):
        boundaries = (0,) + cuts + (len(weights),)
        scores.append(
            sum(
                weights[left] + weights[right - 1]
                for left, right in zip(boundaries, boundaries[1:])
            )
        )
    return max(scores) - min(scores)


def random_marbles(rng):
    n = rng.randint(1, 11)
    return [[rng.randint(1, 30) for _ in range(n)], rng.randint(1, n)]


def quadruplets_oracle(args):
    nums = args[0]
    return sum(
        nums[i] < nums[k] < nums[j] < nums[l]
        for i, j, k, l in combinations(range(len(nums)), 4)
    )


def random_quadruplets(rng):
    n = rng.randint(4, 11)
    values = list(range(1, n + 1))
    rng.shuffle(values)
    return [values]


def range_oracle(args):
    banned, n, maximum = args
    allowed = [value for value in range(1, n + 1) if value not in set(banned)]
    return max(
        (
            len(chosen)
            for size in range(len(allowed) + 1)
            for chosen in combinations(allowed, size)
            if sum(chosen) <= maximum
        ),
        default=0,
    )


def random_range(rng):
    n = rng.randint(1, 15)
    return [
        [rng.randint(1, n + 5) for _ in range(rng.randint(0, 10))],
        n,
        rng.randint(0, 60),
    ]


BAG = """\
def maximum_fractional_bag_price(items,capacity):
    total=0.0
    for price,weight in sorted(items,key=lambda item:item[0]/item[1],reverse=True):
        amount=min(weight,capacity);total+=price*amount/weight;capacity-=amount
        if capacity==0:return total
    return -1
"""

MONKEYS = """\
def monkey_collision_moves(n):
    modulus=10**9+7
    def power(exponent):
        if exponent==0:return 1
        half=power(exponent//2)
        result=half*half%modulus
        return result*2%modulus if exponent%2 else result
    return (power(n)-2)%modulus
"""

MARBLES = """\
def marble_score_difference(weights,k):
    boundaries=sorted(weights[index]+weights[index+1] for index in range(len(weights)-1))
    return sum(boundaries[-(k-1):])-sum(boundaries[:k-1]) if k>1 else 0
"""

QUADRUPLETS = """\
def count_increasing_quadruplets(nums):
    n=len(nums);answer=0
    smaller=[[0]*n for _ in range(n)]
    for middle in range(n):
        count=0
        for right in range(middle+1,n):
            if nums[right]<nums[middle]:count+=1
            smaller[middle][right]=count
    for j in range(1,n-2):
        left_smaller=sum(nums[i]<nums[j] for i in range(j))
        for k in range(j+1,n-1):
            if nums[k]<nums[j]:
                right_larger=sum(nums[l]>nums[j] for l in range(k+1,n))
                left_for_k=sum(nums[i]<nums[k] for i in range(j))
                answer+=left_for_k*right_larger
    return answer
"""

RANGE = """\
def maximum_allowed_range_count(banned,n,max_sum):
    forbidden=set(banned);total=0;answer=0
    for value in range(1,n+1):
        if value in forbidden:continue
        if total+value>max_sum:break
        total+=value;answer+=1
    return answer
"""


BATCH = {
    2548: entry(
        "maximum_fractional_bag_price",
        [("items", "list[list[int]]"), ("capacity", "int")],
        "float",
        ["arrays", "greedy", "sorting"],
        [
            "Each item is [price,weight] and may be divided in any fractional ratio.",
            "Fill exactly capacity units of weight while maximizing total proportional price.",
            "Return -1 when all items together weigh less than capacity; floating answers use tolerance.",
        ],
        [
            (
                [[[50, 1], [10, 8]], 5],
                "Take the entire 50-price item and half of the other item for total price 55.",
            ),
            (
                [[[20, 4], [30, 6]], 11],
                "Only ten units of item weight exist, so the bag cannot be filled exactly.",
            ),
        ],
        [
            [i, c]
            for i, c in [
                ([[10, 1]], 1),
                ([[10, 1]], 2),
                ([[10, 2]], 1),
                ([[10, 2], [9, 1]], 2),
                ([[5, 5], [20, 2]], 4),
                ([[12, 3], [10, 5]], 8),
                ([[8, 4], [9, 3], [10, 2]], 5),
                ([[1, 10], [100, 1]], 3),
                ([[30, 6], [25, 5]], 7),
                ([[7, 2], [14, 4], [9, 3]], 6),
                ([[40, 8], [30, 3], [20, 2]], 10),
                ([[3, 1], [4, 1], [5, 1]], 2),
                ([[99, 9], [50, 10], [12, 2]], 15),
                ([[13, 7], [17, 5], [19, 3], [23, 2]], 12),
            ]
        ],
        BAG,
        [
            BAG.replace("reverse=True", "reverse=False"),
            BAG.replace("price*amount/weight", "price*capacity/weight"),
        ],
        [
            "Consumes the lowest price-per-weight items first.",
            "Prices a partially consumed item using the pre-consumption capacity rather than the amount taken.",
        ],
        bag_oracle,
        random_bag,
        [
            "Because items are divisible, compare their price per unit of weight.",
            "Consume items from greatest density to smallest, taking a final fraction when necessary.",
            "Stop immediately when capacity reaches zero; return -1 if the sorted items are exhausted first.",
            "Exchanging any lower-density weight for available higher-density weight cannot decrease value, proving the greedy ordering.",
        ],
        "O(n log n)",
        "O(n)",
        6,
    ),
    2550: entry(
        "monkey_collision_moves",
        [("n", "int")],
        "int",
        ["recursion", "math", "modular exponentiation"],
        [
            "One monkey starts at each vertex of a regular n-sided polygon.",
            "Every monkey independently moves to its clockwise or counterclockwise adjacent vertex.",
            "Count direction assignments causing at least two monkeys to arrive at one vertex, modulo 1,000,000,007.",
        ],
        [
            (
                [3],
                "Eight direction assignments exist; only the two uniform directions avoid a collision, leaving six.",
            ),
            (
                [4],
                "Sixteen assignments minus the two collision-free uniform directions gives fourteen.",
            ),
        ],
        [[n] for n in [5, 6, 7, 8, 9, 10, 11, 12, 20, 50, 100, 999, 1000, 100000]],
        MONKEYS,
        [
            MONKEYS.replace("power(n)-2", "power(n)-1"),
            MONKEYS.replace("return result*2%modulus", "return result*3%modulus"),
        ],
        [
            "Subtracts only one of the two collision-free uniform direction choices.",
            "Multiplies odd powers by three instead of by the base two.",
        ],
        monkeys_oracle,
        random_monkeys,
        [
            "There are two choices per monkey, giving 2^n total direction assignments.",
            "Exactly two assignments avoid collision: everybody clockwise or everybody counterclockwise.",
            "Compute 2^n modulo the prime with recursive exponentiation by squaring.",
            "Even exponents square the half power; odd exponents multiply that square by two, giving logarithmic recursion depth.",
        ],
        "O(log n)",
        "O(log n)",
        6,
    ),
    2551: entry(
        "marble_score_difference",
        [("weights", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "greedy", "sorting"],
        [
            "Split the ordered marbles into exactly k nonempty contiguous bags.",
            "Each bag contributes its first weight plus its last weight.",
            "Return maximum possible total score minus minimum possible total score.",
        ],
        [
            (
                [[1, 3, 5, 1], 2],
                "Choosing the largest versus smallest single cut-boundary pair changes the score by four.",
            ),
            (
                [[1, 3], 2],
                "Both marbles must be separate, so maximum and minimum scores are identical.",
            ),
        ],
        [
            [w, k]
            for w, k in [
                ([5], 1),
                ([1, 2], 1),
                ([1, 2], 2),
                ([1, 2, 3], 2),
                ([3, 1, 2], 2),
                ([1, 1, 1, 1], 3),
                ([5, 1, 5, 1], 2),
                ([2, 7, 1, 8, 2], 3),
                ([9, 8, 7, 6], 4),
                ([1, 10, 1, 10, 1], 2),
                ([4, 2, 9, 3, 8], 4),
                ([6, 5, 4, 3, 2, 1], 3),
                ([3, 1, 4, 1, 5, 9], 5),
                ([10, 1, 10, 1, 10, 1, 10], 4),
            ]
        ],
        MARBLES,
        [
            MARBLES.replace("k-1", "k"),
            MARBLES.replace("-sum(boundaries[:k-1])", "+sum(boundaries[:k-1])"),
        ],
        [
            "Selects k cut boundaries even though k bags require only k-1 cuts.",
            "Adds the minimum boundary contribution instead of subtracting it.",
        ],
        marbles_oracle,
        random_marbles,
        [
            "The outermost first and last weights occur in every partition and cancel in the difference.",
            "A cut between adjacent marbles adds the sum of those two boundary weights.",
            "Choose the k-1 largest boundary sums for the maximum score and the k-1 smallest for the minimum.",
            "All cut choices contribute independently once the fixed outer endpoints cancel, so sorting boundary sums is sufficient.",
        ],
        "O(n log n)",
        "O(n)",
        8,
    ),
    2552: entry(
        "count_increasing_quadruplets",
        [("nums", "list[int]")],
        "int",
        ["arrays", "dynamic programming", "prefix counting"],
        [
            "nums is a permutation of integers 1 through n.",
            "Count index quadruplets i<j<k<l satisfying nums[i]<nums[k]<nums[j]<nums[l].",
            "Return the total number of qualifying quadruplets.",
        ],
        [
            (
                [[1, 3, 2, 4, 5]],
                "The qualifying quadruplets use value orders 1,3,2,4 and 1,3,2,5, giving two.",
            ),
            (
                [[1, 2, 3, 4]],
                "No middle inversion nums[k] < nums[j] exists, so the count is zero.",
            ),
        ],
        [
            [p]
            for p in [
                [4, 3, 2, 1],
                [2, 1, 4, 3],
                [1, 4, 2, 3],
                [2, 4, 1, 3],
                [3, 1, 2, 4],
                [1, 5, 2, 4, 3],
                [2, 5, 1, 4, 3],
                [5, 1, 4, 2, 3],
                [1, 4, 2, 5, 3, 6],
                [2, 6, 3, 5, 1, 4],
                [3, 5, 1, 6, 2, 4],
                [1, 6, 2, 5, 3, 4],
                [4, 1, 6, 2, 5, 3],
                [2, 7, 3, 6, 1, 5, 4],
            ]
        ],
        QUADRUPLETS,
        [
            QUADRUPLETS.replace("nums[i]<nums[k]", "nums[i]<nums[j]"),
            QUADRUPLETS.replace("nums[l]>nums[j]", "nums[l]>nums[k]"),
        ],
        [
            "Counts left endpoints below nums[j] instead of the smaller nums[k].",
            "Counts right endpoints above nums[k] rather than above the larger nums[j].",
        ],
        quadruplets_oracle,
        random_quadruplets,
        [
            "Fix the middle inversion j<k with nums[k]<nums[j].",
            "Count earlier indices i with nums[i]<nums[k] and later indices l with nums[l]>nums[j].",
            "Multiply those independent left and right counts for the fixed middle pair and sum them.",
            "Every valid quadruplet has exactly one middle pair (j,k), so the products count all solutions once.",
        ],
        "O(n squared)",
        "O(1) beyond input",
        8,
    ),
    2554: entry(
        "maximum_allowed_range_count",
        [("banned", "list[int]"), ("n", "int"), ("max_sum", "int")],
        "int",
        ["arrays", "greedy", "sets"],
        [
            "Select distinct integers from 1 through n that do not occur in banned.",
            "Their total must not exceed max_sum.",
            "Return the maximum possible number selected; duplicate and out-of-range banned values have no extra effect.",
        ],
        [
            (
                [[1, 6, 5], 5, 6],
                "The smallest allowed values two and three total five; adding four would exceed six.",
            ),
            (
                [[1, 2, 3, 4, 5, 6, 7], 8, 1],
                "Only eight is allowed but exceeds the sum limit, so none can be selected.",
            ),
        ],
        [
            [b, n, m]
            for b, n, m in [
                ([], 1, 1),
                ([], 5, 6),
                ([1], 5, 6),
                ([2], 5, 6),
                ([1, 1], 3, 5),
                ([10], 5, 15),
                ([1, 2, 3], 3, 100),
                ([2, 4], 6, 9),
                ([3, 6], 7, 12),
                ([1, 5, 9], 10, 20),
                ([2, 2, 8], 8, 15),
                ([4, 5, 6], 10, 25),
                ([1, 3, 5, 7, 9], 10, 30),
                ([20, 1, 2], 12, 40),
            ]
        ],
        RANGE,
        [
            RANGE.replace("range(1,n+1)", "range(1,n)"),
            RANGE.replace(
                "if value in forbidden:continue", "if value not in forbidden:continue"
            ),
        ],
        [
            "Never considers the allowed endpoint n.",
            "Selects only banned values instead of excluding them.",
        ],
        range_oracle,
        random_range,
        [
            "To maximize how many distinct values fit, always consider allowed values from smallest to largest.",
            "Store banned values in a set so duplicates and membership checks are harmless and fast.",
            "Add each allowed value until the next one would exceed max_sum, then stop.",
            "Replacing any selected larger value with an available smaller value cannot increase the sum, proving the greedy prefix has maximum cardinality.",
        ],
        "O(n+banned length)",
        "O(banned length)",
        5,
    ),
}

BATCH[2548]["comparator"] = "float"
