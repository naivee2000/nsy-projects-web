"""Knapsack, greedy, and number-theory workbook batch 142."""

from functools import lru_cache
from math import gcd
from .import_batch_055 import entry


def fruit_oracle(args):
    prices, tastes, budget, coupons = args
    best = 0

    def search(i, cost, used, total):
        nonlocal best
        if cost > budget:
            return
        if i == len(prices):
            best = max(best, total)
            return
        search(i + 1, cost, used, total)
        search(i + 1, cost + prices[i], used, total + tastes[i])
        if used < coupons:
            search(i + 1, cost + prices[i] // 2, used + 1, total + tastes[i])

    search(0, 0, 0, 0)
    return best


def random_fruit(rng):
    n = rng.randint(1, 9)
    return [
        [rng.randint(1, 20) for _ in range(n)],
        [rng.randint(1, 20) for _ in range(n)],
        rng.randint(0, 45),
        rng.randint(0, min(4, n)),
    ]


def robot_oracle(args):
    text = args[0]

    @lru_cache(None)
    def solve(index, stack):
        choices = []
        if index < len(text):
            choices.append(solve(index + 1, stack + (text[index],)))
        if stack:
            choices.append(stack[-1] + solve(index, stack[:-1]))
        return min(choices) if choices else ""

    return solve(0, ())


def random_robot(rng):
    return ["".join(rng.choice("abcdef") for _ in range(rng.randint(1, 9)))]


def splits_oracle(args):
    nums = args[0]
    dp = [10**9] * (len(nums) + 1)
    dp[0] = 0
    for end in range(1, len(nums) + 1):
        common = 0
        for start in range(end - 1, -1, -1):
            common = gcd(common, nums[start])
            if common > 1:
                dp[end] = min(dp[end], dp[start] + 1)
    return dp[-1]


def random_splits(rng):
    return [[rng.randint(2, 40) for _ in range(rng.randint(1, 20))]]


def products_oracle(args):
    n, queries = args
    values = [1 << bit for bit in range(n.bit_length()) if n >> bit & 1]
    mod = 10**9 + 7
    answer = []
    for left, right in queries:
        product = 1
        for value in values[left : right + 1]:
            product = product * value % mod
        answer.append(product)
    return answer


def random_products(rng):
    n = rng.randint(1, 2**20 - 1)
    size = n.bit_count()
    queries = []
    for _ in range(rng.randint(1, 12)):
        left = rng.randrange(size)
        queries.append([left, rng.randrange(left, size)])
    return [n, queries]


def minimize_oracle(args):
    nums = args[0]

    def feasible(limit):
        carry = 0
        for value in reversed(nums[1:]):
            carry = max(0, carry + value - limit)
        return nums[0] + carry <= limit

    for limit in range(max(nums) + 1):
        if feasible(limit):
            return limit


def random_minimize(rng):
    return [[rng.randint(0, 40) for _ in range(rng.randint(1, 25))]]


FRUIT = """\
def maximum_fruit_tastiness(price,tastiness,max_amount,max_coupons):
    states={(0,0):0}
    for cost,value in zip(price,tastiness):
        following=dict(states)
        for (spent,coupons),total in states.items():
            if spent+cost<=max_amount:following[(spent+cost,coupons)]=max(following.get((spent+cost,coupons),0),total+value)
            if coupons<max_coupons and spent+cost//2<=max_amount:following[(spent+cost//2,coupons+1)]=max(following.get((spent+cost//2,coupons+1),0),total+value)
        states=following
    return max(states.values())
"""

ROBOT = """\
def lexicographically_smallest_robot_output(s):
    remaining=[0]*26
    for character in s:remaining[ord(character)-97]+=1
    smallest=0;stack=[];answer=[]
    for character in s:
        remaining[ord(character)-97]-=1
        while smallest<25 and remaining[smallest]==0:smallest+=1
        stack.append(character)
        while stack and ord(stack[-1])-97<=smallest:answer.append(stack.pop())
    while stack:answer.append(stack.pop())
    return ''.join(answer)
"""

SPLITS = """\
def minimum_gcd_subarray_splits(nums):
    from math import gcd
    groups=1;common=0
    for value in nums:
        common=gcd(common,value)
        if common==1:groups+=1;common=value
    return groups
"""

PRODUCTS = """\
def power_range_products(n,queries):
    powers=[];bit=1
    while bit<=n:
        if n&bit:powers.append(bit)
        bit<<=1
    mod=10**9+7;answer=[]
    for left,right in queries:
        product=1
        for index in range(left,right+1):product=product*powers[index]%mod
        answer.append(product)
    return answer
"""

MINIMIZE = """\
def minimized_array_maximum(nums):
    prefix=0;answer=0
    for index,value in enumerate(nums):
        prefix+=value;answer=max(answer,(prefix+index)//(index+1))
    return answer
"""

BATCH = {
    2431: entry(
        "maximum_fruit_tastiness",
        [
            ("price", "list[int]"),
            ("tastiness", "list[int]"),
            ("max_amount", "int"),
            ("max_coupons", "int"),
        ],
        "int",
        ["dynamic programming", "knapsack"],
        [
            "Each fruit may be bought at most once or skipped.",
            "A coupon changes one chosen fruit’s price to floor(price/2), and at most max_coupons coupons may be used.",
            "Keep total cost at most max_amount and maximize total tastiness.",
        ],
        [
            (
                [[10, 20, 20], [5, 8, 8], 20, 1],
                "Buy the first fruit at full price and one twenty-price fruit with a coupon for cost twenty and tastiness thirteen.",
            ),
            (
                [[5, 4], [6, 5], 4, 1],
                "Using a coupon on the first fruit costs two and yields tastiness six, better than buying the second fruit normally.",
            ),
        ],
        [
            [p, t, b, c]
            for p, t, b, c in [
                ([1], [5], 0, 0),
                ([1], [5], 0, 1),
                ([10], [7], 5, 1),
                ([10], [7], 4, 1),
                ([2, 3], [4, 5], 5, 0),
                ([2, 3], [4, 5], 2, 1),
                ([9, 9], [1, 10], 9, 1),
                ([3, 5, 7], [4, 6, 8], 7, 2),
                ([1, 1, 1], [2, 3, 4], 1, 0),
                ([1, 1, 1], [2, 3, 4], 1, 2),
                ([8, 6, 4], [5, 5, 5], 9, 1),
                ([20, 1], [100, 1], 10, 1),
                ([7, 11, 13], [5, 9, 12], 12, 2),
                ([4, 4, 4, 4], [1, 2, 3, 4], 6, 1),
            ]
        ],
        FRUIT,
        [
            FRUIT.replace("coupons<max_coupons", "coupons<0"),
            FRUIT.replace("cost//2", "(cost+1)//2"),
        ],
        [
            "Never permits the discounted purchase transition.",
            "Rounds a discounted odd price upward instead of downward.",
        ],
        fruit_oracle,
        random_fruit,
        [
            "Maintain best tastiness by (money spent, coupons used).",
            "For each fruit, copy skip states, then add full-price and discounted transitions when affordable.",
            "Keep only the largest tastiness reaching each state.",
            "Every fruit has exactly the three enumerated choices, so iterating them once explores all legal purchase sets without reuse.",
        ],
        "O(n*amount*coupons)",
        "O(amount*coupons)",
        6,
    ),
    2434: entry(
        "lexicographically_smallest_robot_output",
        [("s", "str")],
        "str",
        ["strings", "stacks", "greedy"],
        [
            "Process source string s from left to right and maintain a robot stack t.",
            "An operation either moves the next source character onto t or pops t’s last character onto the output.",
            "Use all characters and return the lexicographically smallest output possible.",
        ],
        [
            (
                ["zza"],
                "Push until a is available, output a, then pop both z characters to obtain azz.",
            ),
            (
                ["bac"],
                "After pushing b and a, output a and b before processing c, producing abc.",
            ),
        ],
        [
            [s]
            for s in [
                "a",
                "aa",
                "ab",
                "ba",
                "cba",
                "abc",
                "bca",
                "cab",
                "leetcode",
                "bydizfve",
                "zzzz",
                "azaz",
                "dcab",
                "fedcba",
            ]
        ],
        ROBOT,
        [
            ROBOT.replace("<=smallest", "<smallest"),
            ROBOT.replace(
                "remaining[ord(character)-97]-=1", "remaining[ord(character)-97]+=1"
            ),
        ],
        [
            "Fails to pop a stack character equal to the smallest remaining source character.",
            "Increases remaining counts as characters are consumed and loses the true suffix minimum.",
        ],
        robot_oracle,
        random_robot,
        [
            "Count characters still unprocessed in the source.",
            "After pushing one character, advance the smallest remaining-letter pointer past exhausted counts.",
            "Pop while the stack top is no larger than the smallest character still available later.",
            "A larger top should wait for a smaller future character, while an eligible top cannot be improved by waiting; this greedy decision fixes the smallest possible next output.",
        ],
        "O(n+alphabet)",
        "O(n)",
        6,
    ),
    2436: entry(
        "minimum_gcd_subarray_splits",
        [("nums", "list[int]")],
        "int",
        ["arrays", "number theory", "greedy"],
        [
            "Partition the entire positive array into contiguous nonempty subarrays.",
            "Every group’s greatest common divisor must be strictly greater than one.",
            "Return the minimum number of groups.",
        ],
        [
            (
                [[12, 6, 3, 14, 8]],
                "The split [12,6,3] and [14,8] has GCDs three and two, so two groups suffice.",
            ),
            (
                [[2, 3]],
                "The pair has GCD one and must split into [2] and [3], requiring two groups.",
            ),
        ],
        [
            [x]
            for x in [
                [2],
                [7],
                [2, 4],
                [2, 3],
                [6, 10, 15],
                [6, 10, 7],
                [4, 8, 16, 3, 9],
                [2, 6, 3, 12],
                [5, 10, 15, 20],
                [14, 21, 35],
                [2, 3, 5, 7],
                [12, 18, 24, 5, 10],
                [8, 12, 18, 27],
                [30, 6, 10, 15],
            ]
        ],
        SPLITS,
        [
            SPLITS.replace("common==1", "common<=2"),
            SPLITS.replace("groups=1", "groups=0"),
        ],
        [
            "Incorrectly splits a valid group whose GCD is exactly two.",
            "Starts with zero groups and undercounts every nonempty input.",
        ],
        splits_oracle,
        random_splits,
        [
            "Extend the current group while maintaining its running GCD.",
            "When adding a value makes the GCD one, end the previous group and begin a new group at that value.",
            "Otherwise keep extending because delaying a split cannot reduce future feasibility.",
            "Once a prefix GCD reaches one it can never increase by adding values, so a split is mandatory; splitting at the latest possible point minimizes the group count.",
        ],
        "O(n log V)",
        "O(1)",
        5,
    ),
    2438: entry(
        "power_range_products",
        [("n", "int"), ("queries", "list[list[int]]")],
        "list[int]",
        ["bit manipulation", "arrays"],
        [
            "Represent positive n as the minimum number of distinct powers of two, sorted increasingly.",
            "For each inclusive query [left,right], multiply that slice of powers.",
            "Return every product modulo 1,000,000,007.",
        ],
        [
            (
                [15, [[0, 1], [2, 2], [0, 3]]],
                "Fifteen decomposes as [1,2,4,8], giving products 2, 4, and 64.",
            ),
            (
                [8, [[0, 0]]],
                "Eight has the single-power representation [8], so the only product is eight.",
            ),
        ],
        [
            [n, q]
            for n, q in [
                (1, [[0, 0]]),
                (2, [[0, 0]]),
                (3, [[0, 1]]),
                (5, [[0, 0], [1, 1], [0, 1]]),
                (10, [[0, 1]]),
                (16, [[0, 0]]),
                (21, [[0, 2], [1, 2]]),
                (31, [[0, 4], [2, 3]]),
                (42, [[0, 2]]),
                (255, [[0, 7]]),
                (1024, [[0, 0]]),
                (1025, [[0, 1]]),
                (7, [[1, 2]]),
                (13, [[0, 1], [1, 2]]),
            ]
        ],
        PRODUCTS,
        [
            PRODUCTS.replace("powers.append(bit)", "powers.insert(0,bit)"),
            PRODUCTS.replace("range(left,right+1)", "range(left,right)"),
        ],
        [
            "Stores the component powers in decreasing rather than increasing order.",
            "Treats the inclusive right query endpoint as exclusive.",
        ],
        products_oracle,
        random_products,
        [
            "Extract every set bit of n from least significant to most significant.",
            "Each set bit contributes its corresponding power of two, already in increasing order.",
            "Multiply the inclusive query slice while reducing modulo the requested modulus.",
            "Binary representation is the unique minimum-cardinality distinct-power decomposition, so the extracted array and every queried product are exact.",
        ],
        "O(bits+q*bits)",
        "O(bits)",
        5,
    ),
    2439: entry(
        "minimized_array_maximum",
        [("nums", "list[int]")],
        "int",
        ["arrays", "prefix sums", "greedy"],
        [
            "An operation moves one unit from index i to index i-1 for any i greater than zero.",
            "Apply any number of operations and minimize the largest array value.",
            "Return that minimum possible maximum.",
        ],
        [
            (
                [[3, 7, 1, 6]],
                "The first two values total ten, forcing a maximum of at least five; all prefixes fit under five per position, so five is achievable.",
            ),
            (
                [[10, 1]],
                "No operation can move mass rightward away from the initial ten, so the answer remains ten.",
            ),
        ],
        [
            [x]
            for x in [
                [0],
                [5],
                [0, 1],
                [1, 0],
                [0, 10],
                [10, 0],
                [1, 2, 3],
                [3, 2, 1],
                [0, 0, 9],
                [5, 0, 0, 5],
                [2, 2, 2, 2],
                [1, 100, 1],
                [7, 1, 7, 1],
                [0, 3, 0, 3, 0],
            ]
        ],
        MINIMIZE,
        [
            MINIMIZE.replace("(prefix+index)//(index+1)", "prefix//(index+1)"),
            MINIMIZE.replace(
                "answer=max(answer,(prefix+index)//(index+1))",
                "answer=(prefix+index)//(index+1)",
            ),
        ],
        [
            "Uses floor instead of ceiling for a prefix average.",
            "Checks only the final prefix average instead of the maximum constraint across all prefixes.",
        ],
        minimize_oracle,
        random_minimize,
        [
            "For each prefix ending at i, its total can move only within that prefix or farther left.",
            "Therefore its average rounded up is a lower bound on the final maximum.",
            "Take the largest ceiling prefix average.",
            "That maximum provides enough capacity across every prefix to redistribute excess leftward, so the strongest lower bound is also achievable.",
        ],
        "O(n)",
        "O(1)",
        5,
    ),
}
