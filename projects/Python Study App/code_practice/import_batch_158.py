"""Bitwise, lazy-range, integer reduction, subset-DP, and LCP batch 158."""

from collections import deque

from .import_batch_055 import entry


def impossible_oracle(args):
    values = {0}
    for number in args[0]:
        values |= {current | number for current in list(values)}
    candidate = 1
    while candidate in values:
        candidate += 1
    return candidate


def random_impossible(rng):
    return [[rng.randint(1, 63) for _ in range(rng.randint(1, 12))]]


def queries_oracle(args):
    bits, numbers, queries = args
    bits = bits[:]
    total = sum(numbers)
    answer = []
    for operation, first, second in queries:
        if operation == 1:
            for index in range(first, second + 1):
                bits[index] ^= 1
        elif operation == 2:
            total += first * sum(bits)
        else:
            answer.append(total)
    return answer


def random_queries(rng):
    n = rng.randint(1, 12)
    queries = []
    for _ in range(rng.randint(1, 20)):
        operation = rng.randint(1, 3)
        if operation == 1:
            left, right = sorted((rng.randrange(n), rng.randrange(n)))
            queries.append([1, left, right])
        elif operation == 2:
            queries.append([2, rng.randint(0, 10), 0])
        else:
            queries.append([3, 0, 0])
    return [
        [rng.randint(0, 1) for _ in range(n)],
        [rng.randint(0, 20) for _ in range(n)],
        queries,
    ]


def reduce_oracle(args):
    start = args[0]
    powers = [1 << bit for bit in range(start.bit_length() + 1)]
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        value, steps = queue.popleft()
        if value == 0:
            return steps
        for power in powers:
            for following in (value - power, value + power):
                if 0 <= following <= 2 * max(start, 1) and following not in seen:
                    seen.add(following)
                    queue.append((following, steps + 1))


def random_reduce(rng):
    return [rng.randint(1, 200)]


def square_free(value):
    factor = 2
    while factor * factor <= value:
        if value % (factor * factor) == 0:
            return False
        factor += 1
    return True


def subsets_oracle(args):
    nums = args[0]
    answer = 0
    for mask in range(1, 1 << len(nums)):
        product = 1
        for index, value in enumerate(nums):
            if mask >> index & 1:
                product *= value
        answer += square_free(product)
    return answer % (10**9 + 7)


def random_subsets(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 14))]]


def compute_lcp(text):
    n = len(text)
    matrix = [[0] * n for _ in range(n)]
    for left in range(n - 1, -1, -1):
        for right in range(n - 1, -1, -1):
            if text[left] == text[right]:
                matrix[left][right] = 1 + (
                    matrix[left + 1][right + 1] if left + 1 < n and right + 1 < n else 0
                )
    return matrix


def lcp_oracle(args):
    matrix = args[0]
    n = len(matrix)
    parent = list(range(n))

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for left in range(n):
        for right in range(n):
            if matrix[left][right] > 0:
                a, b = find(left), find(right)
                parent[b] = a
    letters = {}
    result = []
    for index in range(n):
        root = find(index)
        if root not in letters:
            if len(letters) == 26:
                return ""
            letters[root] = chr(97 + len(letters))
        result.append(letters[root])
    text = "".join(result)
    return text if compute_lcp(text) == matrix else ""


def random_lcp(rng):
    n = rng.randint(1, 8)
    if rng.random() < 0.7:
        return [compute_lcp("".join(rng.choice("abcd") for _ in range(n)))]
    matrix = [[rng.randint(0, n) for _ in range(n)] for _ in range(n)]
    return [matrix]


IMPOSSIBLE = """\
def minimum_impossible_subsequence_or(nums):
    present=set(nums);value=1
    while value in present:value*=2
    return value
"""

QUERIES = """\
def handle_sum_queries(nums1,nums2,queries):
    n=len(nums1);tree=[0]*(4*n);lazy=[False]*(4*n)
    def build(node,left,right):
        if left==right:tree[node]=nums1[left];return
        middle=(left+right)//2;build(node*2,left,middle);build(node*2+1,middle+1,right);tree[node]=tree[node*2]+tree[node*2+1]
    def flip(node,left,right,start,end):
        if start<=left and right<=end:tree[node]=right-left+1-tree[node];lazy[node]=not lazy[node];return
        middle=(left+right)//2
        if lazy[node]:
            for child,a,b in ((node*2,left,middle),(node*2+1,middle+1,right)):
                tree[child]=b-a+1-tree[child];lazy[child]=not lazy[child]
            lazy[node]=False
        if start<=middle:flip(node*2,left,middle,start,end)
        if end>middle:flip(node*2+1,middle+1,right,start,end)
        tree[node]=tree[node*2]+tree[node*2+1]
    build(1,0,n-1);total=sum(nums2);answer=[]
    for operation,first,second in queries:
        if operation==1:flip(1,0,n-1,first,second)
        elif operation==2:total+=first*tree[1]
        else:answer.append(total)
    return answer
"""

REDUCE = """\
def minimum_power_operations_to_zero(n):
    operations=0
    while n:
        lowest=n&-n
        if n& (lowest*2):n+=lowest
        else:n-=lowest
        operations+=1
    return operations
"""

SUBSETS = """\
def count_square_free_subsets(nums):
    primes=[2,3,5,7,11,13,17,19,23,29];modulus=10**9+7;ways={0:1}
    for value in nums:
        mask=0;valid=True
        for bit,prime in enumerate(primes):
            if value%(prime*prime)==0:valid=False;break
            if value%prime==0:mask|=1<<bit
        if not valid:continue
        updated=ways.copy()
        for state,count in ways.items():
            if not state&mask:updated[state|mask]=(updated.get(state|mask,0)+count)%modulus
        ways=updated
    return (sum(ways.values())-1)%modulus
"""

LCP = """\
def smallest_string_from_lcp(lcp):
    n=len(lcp);letters=['']*n;next_letter=0
    for index in range(n):
        if letters[index]:continue
        if next_letter==26:return ''
        char=chr(97+next_letter);next_letter+=1
        for other in range(index,n):
            if lcp[index][other]>0:letters[other]=char
    for left in range(n-1,-1,-1):
        for right in range(n-1,-1,-1):
            expected=1+(lcp[left+1][right+1] if left+1<n and right+1<n else 0) if letters[left]==letters[right] else 0
            if lcp[left][right]!=expected:return ''
    return ''.join(letters)
"""


BATCH = {
    2568: entry(
        "minimum_impossible_subsequence_or",
        [("nums", "list[int]")],
        "int",
        ["arrays", "bit manipulation", "invariants"],
        [
            "Choose any subsequence, including multiple array elements, and OR its values.",
            "Return the smallest positive integer that no subsequence can produce.",
            "Input values are positive integers.",
        ],
        [
            (
                [[2, 1]],
                "Powers one and two are present and can form one through three, while four is impossible.",
            ),
            ([[5, 3, 2]], "Power one is absent, so one is immediately impossible."),
        ],
        [
            [a]
            for a in [
                [1],
                [2],
                [1, 2],
                [1, 4],
                [1, 2, 4],
                [3, 5, 7],
                [8, 1, 2, 4],
                [1, 1, 2, 2],
                [16, 8, 4, 2, 1],
                [6, 10, 12],
                [1, 3, 7, 15],
                [2, 4, 8, 16],
                [1, 2, 8, 32],
                [31, 63, 127],
            ]
        ],
        IMPOSSIBLE,
        [
            IMPOSSIBLE.replace("value*=2", "value+=1"),
            IMPOSSIBLE.replace("present=set(nums)", "present=set(nums[1:])"),
        ],
        [
            "Searches every integer in the input rather than the first missing power of two.",
            "Ignores the first array value when building the necessary-power set.",
        ],
        impossible_oracle,
        random_impossible,
        [
            "Any answer must itself be a power of two.",
            "A power of two can appear as an OR only if some selected value contains that bit without higher bits; for the exact smallest missing bit, this requires that power itself.",
            "Insert all values into a set and scan powers of two from one upward.",
            "All smaller powers being present can OR-build every smaller positive value, while the first missing power cannot be built, proving minimality.",
        ],
        "O(n+word size)",
        "O(n)",
        6,
    ),
    2569: entry(
        "handle_sum_queries",
        [
            ("nums1", "list[int]"),
            ("nums2", "list[int]"),
            ("queries", "list[list[int]]"),
        ],
        "list[int]",
        ["arrays", "segment trees", "lazy propagation"],
        [
            "Type 1 [1,l,r] flips every nums1 bit in the inclusive range.",
            "Type 2 [2,p,0] adds p times the current nums1-one count to the total nums2 sum.",
            "Type 3 records the current nums2 sum; return all recorded values.",
        ],
        [
            (
                [[1, 0, 1], [0, 0, 0], [[1, 1, 1], [2, 1, 0], [3, 0, 0]]],
                "The flip makes three ones, so the update raises the sum to three.",
            ),
            (
                [[1], [5], [[3, 0, 0], [1, 0, 0], [2, 4, 0], [3, 0, 0]]],
                "The recorded sums are five before the flip and five afterward because no ones remain.",
            ),
        ],
        [
            [a, b, q]
            for a, b, q in [
                ([0], [0], [[3, 0, 0]]),
                ([1], [2], [[2, 3, 0], [3, 0, 0]]),
                ([0], [5], [[1, 0, 0], [2, 2, 0], [3, 0, 0]]),
                ([1, 0], [0, 0], [[1, 0, 1], [3, 0, 0]]),
                ([1, 1], [1, 1], [[1, 0, 0], [2, 5, 0], [3, 0, 0]]),
                ([0, 0, 0], [3, 4, 5], [[2, 9, 0], [3, 0, 0]]),
                ([1, 0, 1, 0], [0, 0, 0, 0], [[1, 1, 2], [2, 3, 0], [3, 0, 0]]),
                ([1, 1, 1], [1, 2, 3], [[1, 0, 2], [2, 4, 0], [3, 0, 0]]),
                ([0, 1, 0], [5, 5, 5], [[1, 0, 1], [1, 1, 2], [2, 2, 0], [3, 0, 0]]),
                ([1, 0, 0, 1], [2, 2, 2, 2], [[3, 0, 0], [2, 10, 0], [3, 0, 0]]),
                ([0, 0, 1, 1], [0, 1, 2, 3], [[1, 0, 3], [2, 1, 0], [3, 0, 0]]),
                ([1, 0, 1, 0, 1], [1, 1, 1, 1, 1], [[1, 2, 4], [2, 7, 0], [3, 0, 0]]),
                (
                    [0, 1, 1, 0, 1],
                    [9, 8, 7, 6, 5],
                    [[1, 1, 3], [2, 6, 0], [1, 0, 4], [3, 0, 0]],
                ),
                (
                    [1, 1, 0, 0, 1, 0],
                    [1, 2, 3, 4, 5, 6],
                    [[2, 3, 0], [1, 0, 5], [2, 2, 0], [3, 0, 0]],
                ),
            ]
        ],
        QUERIES,
        [
            QUERIES.replace("right-left+1-tree[node]", "right-left-tree[node]"),
            QUERIES.replace("first*tree[1]", "second*tree[1]"),
        ],
        [
            "Uses a range length one too small when flipping a fully covered segment.",
            "Uses the unused third query field instead of multiplier p.",
        ],
        queries_oracle,
        random_queries,
        [
            "Only nums1's current count of ones and nums2's total sum are needed.",
            "A lazy segment tree stores one counts and flips a covered node to segment length minus its count.",
            "Propagate pending flips only before descending into a partially covered node.",
            "Range flips remain logarithmic, and each type-two query uses the root count to update the scalar total exactly.",
        ],
        "O((n+queries) log n)",
        "O(n)",
        8,
    ),
    2571: entry(
        "minimum_power_operations_to_zero",
        [("n", "int")],
        "int",
        ["bit manipulation", "greedy", "dynamic programming"],
        [
            "In one operation add or subtract any nonnegative power of two.",
            "Keep intermediate integers nonnegative without loss of optimality.",
            "Return the minimum operations reducing positive n to zero.",
        ],
        [
            (
                [39],
                "Subtracting 8, adding 1, then subtracting 32 reaches zero in three operations.",
            ),
            ([54], "A shortest signed-power representation uses three operations."),
        ],
        [[n] for n in [1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 31, 32, 63, 100]],
        REDUCE,
        [
            REDUCE.replace("n& (lowest*2)", "n& (lowest*4)"),
            REDUCE.replace("n+=lowest", "n-=lowest"),
        ],
        [
            "Looks two bit positions ahead instead of detecting an adjacent run of ones.",
            "Always clears a set bit and misses cheaper carries across long runs of ones.",
        ],
        reduce_oracle,
        random_reduce,
        [
            "The lowest set bit can either be subtracted away or added to create a carry.",
            "For isolated ones, subtract; at the start of consecutive ones, adding once collapses the run through carrying.",
            "Repeat on the new integer until it becomes zero.",
            "This constructs the minimum-weight signed binary representation: each isolated bit costs one, while every run is optimally represented by its two boundaries.",
        ],
        "O(log n)",
        "O(1)",
        6,
    ),
    2572: entry(
        "count_square_free_subsets",
        [("nums", "list[int]")],
        "int",
        ["arrays", "dynamic programming", "bitmasks", "number theory"],
        [
            "Count nonempty index subsets whose product has no squared prime divisor.",
            "Equal values at different indices are distinct choices.",
            "Every value is from one through thirty; return the count modulo 1,000,000,007.",
        ],
        [
            (
                [[3, 4, 4, 5]],
                "Only subsets [3], [5], and [3,5] have square-free products.",
            ),
            ([[1]], "The one-element subset has product one, which is square-free."),
        ],
        [
            [a]
            for a in [
                [2],
                [4],
                [1, 1],
                [2, 3],
                [2, 2],
                [6, 10],
                [1, 2, 3],
                [3, 5, 7],
                [4, 9, 25],
                [2, 6, 15],
                [1, 1, 2, 2],
                [30, 1, 7],
                [5, 10, 15, 30],
                [2, 3, 5, 7, 11],
            ]
        ],
        SUBSETS,
        [
            SUBSETS.replace("if not state&mask", "if state&mask"),
            SUBSETS.replace("sum(ways.values())-1", "sum(ways.values())"),
        ],
        [
            "Combines values only when their prime masks overlap, producing squared factors.",
            "Includes the empty subset in the returned count.",
        ],
        subsets_oracle,
        random_subsets,
        [
            "Represent the ten primes through thirty as bits in a mask.",
            "Discard any value divisible by a prime square; otherwise its mask lists primes used once.",
            "For each value, extend only states whose masks do not overlap, keeping the skip states too.",
            "Disjoint masks are exactly the condition that no prime exponent reaches two, and subtracting the empty state leaves all nonempty square-free subsets.",
        ],
        "O(n times 2^10)",
        "O(2^10)",
        6,
    ),
    2573: entry(
        "smallest_string_from_lcp",
        [("lcp", "list[list[int]]")],
        "str",
        ["strings", "matrices", "greedy", "dynamic programming"],
        [
            "lcp[i][j] must equal the common-prefix length of suffixes beginning at i and j.",
            "Return the lexicographically smallest lowercase string realizing the matrix.",
            "Return an empty string when the matrix is inconsistent or needs more than 26 character groups.",
        ],
        [
            (
                [[[4, 0, 2, 0], [0, 3, 0, 1], [2, 0, 2, 0], [0, 1, 0, 1]]],
                "Positions sharing positive LCP form alternating a and b groups, producing abab.",
            ),
            (
                [[[1, 1], [1, 1]]],
                "No length-two string can have diagonal LCP values one, so the matrix is invalid.",
            ),
        ],
        [
            [m]
            for m in [
                [[1]],
                [[2, 0], [0, 1]],
                [[2, 1], [1, 1]],
                [[2, 1], [0, 1]],
                [[3, 2, 1], [2, 2, 1], [1, 1, 1]],
                [[3, 0, 0], [0, 2, 0], [0, 0, 1]],
                [[3, 1, 0], [1, 2, 0], [0, 0, 1]],
                [[4, 0, 2, 0], [0, 3, 0, 1], [2, 0, 2, 0], [0, 1, 0, 1]],
                [[4, 3, 2, 1], [3, 3, 2, 1], [2, 2, 2, 1], [1, 1, 1, 1]],
                [[3, 0, 1], [0, 2, 0], [1, 0, 1]],
                [[2, 2], [2, 2]],
                [[1, 0], [0, 1]],
                [[3, 2, 0], [2, 2, 0], [0, 0, 1]],
                [[4, 1, 0, 1], [1, 3, 0, 1], [0, 0, 2, 0], [1, 1, 0, 1]],
            ]
        ],
        LCP,
        [
            LCP.replace("lcp[index][other]>0", "lcp[index][other]>=0"),
            LCP.replace("next_letter+=1", "next_letter+=2"),
        ],
        [
            "Assigns every later position the same letter even when its LCP is zero.",
            "Skips alphabet letters and therefore does not produce the lexicographically smallest valid string.",
        ],
        lcp_oracle,
        random_lcp,
        [
            "A positive LCP means the two starting characters must be equal; zero means they differ.",
            "Process the first unassigned position and give its entire positive-LCP group the next smallest letter.",
            "After constructing characters, verify every matrix cell backward using the LCP recurrence.",
            "Greedy first-occurrence labeling is lexicographically minimal, while full recurrence validation rejects all inconsistent equality lengths.",
        ],
        "O(n squared)",
        "O(n)",
        8,
    ),
}
