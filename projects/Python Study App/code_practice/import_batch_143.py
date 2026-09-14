"""Sets, implicit trees, and GCD workbook batch 143."""

from collections import deque
from math import gcd
from .import_batch_055 import entry


def reverse_number(value):
    return int(str(value)[::-1])


def distinct_oracle(args):
    return len(set(args[0] + [reverse_number(value) for value in args[0]]))


def random_distinct(rng):
    return [[rng.randint(1, 100000) for _ in range(rng.randint(1, 30))]]


def sum_reverse_oracle(args):
    target = args[0]
    for candidate in range(target + 1):
        digits = 0
        value = candidate
        while value:
            digits = digits * 10 + value % 10
            value //= 10
        if candidate + digits == target:
            return True
    return target == 0


def random_sum_reverse(rng):
    return [rng.randint(0, 100000)]


def tree_oracle(args):
    n, queries = args
    values = [0] * (n + 1)
    for root in queries:
        for node in range(1, n + 1):
            ancestor = node
            while ancestor > root:
                ancestor //= 2
            if ancestor == root:
                values[node] ^= 1
    return sum(values)


def random_tree(rng):
    n = rng.randint(1, 80)
    return [n, [rng.randint(1, n) for _ in range(rng.randint(1, 30))]]


def gcd_oracle(args):
    nums, k = args
    answer = 0
    for left in range(len(nums)):
        for right in range(left, len(nums)):
            common = nums[left]
            for value in nums[left + 1 : right + 1]:
                common = gcd(common, value)
            answer += common == k
    return answer


def random_gcd(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 18))], rng.randint(1, 15)]


def binary_oracle(args):
    text, k = args
    seen = {text}
    queue = deque([text])
    while queue:
        current = queue.popleft()
        for start in range(len(text) - k + 1):
            changed = (
                current[:start]
                + "".join("1" if c == "0" else "0" for c in current[start : start + k])
                + current[start + k :]
            )
            if changed not in seen:
                seen.add(changed)
                queue.append(changed)
    return len(seen) % (10**9 + 7)


def random_binary(rng):
    n = rng.randint(1, 11)
    return ["".join(rng.choice("01") for _ in range(n)), rng.randint(1, n)]


DISTINCT = """\
def count_distinct_with_reversals(nums):
    values=set(nums)
    for number in nums:values.add(int(str(number)[::-1]))
    return len(values)
"""
SUM_REVERSE = """\
def is_sum_of_number_and_reverse(num):
    for candidate in range(num+1):
        if candidate+int(str(candidate)[::-1])==num:return True
    return False
"""
TREE = """\
def count_one_nodes_after_subtree_flips(n,queries):
    odd=set()
    for node in queries:
        if node in odd:odd.remove(node)
        else:odd.add(node)
    answer=0
    def visit(node,flipped):
        nonlocal answer
        if node>n:return
        flipped^=node in odd;answer+=flipped
        visit(node*2,flipped);visit(node*2+1,flipped)
    visit(1,False);return answer
"""
GCD_SUBARRAYS = """\
def count_subarrays_with_gcd(nums,k):
    from math import gcd
    previous={};answer=0
    for value in nums:
        current={value:1}
        for common,count in previous.items():
            reduced=gcd(common,value);current[reduced]=current.get(reduced,0)+count
        answer+=current.get(k,0);previous=current
    return answer
"""
BINARY = """\
def count_strings_after_k_flips(s,k):
    return pow(2,len(s)-k+1,10**9+7)
"""

BATCH = {
    2442: entry(
        "count_distinct_with_reversals",
        [("nums", "list[int]")],
        "int",
        ["arrays", "sets"],
        [
            "For every original positive integer, reverse its decimal digits and append that numeric value conceptually.",
            "Leading zeroes disappear when the reversal is interpreted as an integer.",
            "Return the number of distinct original and reversed values.",
        ],
        [
            (
                [[1, 13, 10, 12, 31]],
                "The combined distinct values are 1, 13, 10, 12, 31, and 21, giving six.",
            ),
            (
                [[100, 1]],
                "Reversing 100 produces 1, already present, and reversing 1 stays 1, so there are two distinct values.",
            ),
        ],
        [
            [x]
            for x in [
                [1],
                [10],
                [12],
                [12, 21],
                [1000],
                [101],
                [90, 9],
                [123, 321],
                [11, 22, 33],
                [1, 2, 3],
                [120, 12, 21],
                [100, 10, 1],
                [9876, 6789],
                [5, 50, 500],
            ]
        ],
        DISTINCT,
        [
            DISTINCT.replace("int(str(number)[::-1])", "number"),
            DISTINCT.replace("set(nums)", "set()"),
        ],
        [
            "Adds each original number twice instead of adding its reversal.",
            "Counts only reversed values and omits originals that have no reversed counterpart.",
        ],
        distinct_oracle,
        random_distinct,
        [
            "Insert every original value into a set.",
            "Reverse each value’s decimal text, convert it back to an integer, and insert it.",
            "Return the set size.",
            "A set removes duplicates across both the original and generated values, exactly matching the requested distinct count.",
        ],
        "O(n*d)",
        "O(n)",
        3,
    ),
    2443: entry(
        "is_sum_of_number_and_reverse",
        [("num", "int")],
        "bool",
        ["math", "enumeration"],
        [
            "Choose any non-negative integer x.",
            "Reverse x’s decimal digits, dropping leading zeroes in the reversed numeric value.",
            "Return whether x + reverse(x) equals num.",
        ],
        [
            ([443], "Choose x=172; reverse(172)=271 and their sum is 443."),
            ([63], "No non-negative integer plus its decimal reversal equals 63."),
        ],
        [[x] for x in [0, 1, 2, 10, 11, 20, 22, 33, 44, 100, 101, 110, 121, 1000]],
        SUM_REVERSE,
        [
            SUM_REVERSE.replace("range(num+1)", "range(num)"),
            SUM_REVERSE.replace("int(str(candidate)[::-1])", "candidate"),
        ],
        [
            "Never checks x=num, which matters for zero and values paired with a zero reversal.",
            "Adds the candidate to itself instead of using its reversal.",
        ],
        sum_reverse_oracle,
        random_sum_reverse,
        [
            "Enumerate x from zero through num because larger x cannot be part of a non-negative sum equaling num.",
            "Reverse its decimal representation and convert back to an integer.",
            "Return true on the first equality, otherwise false after the search.",
            "The finite loop examines every possible non-negative candidate and tests the defining equation directly.",
        ],
        "O(num*d)",
        "O(d)",
        3,
    ),
    2445: entry(
        "count_one_nodes_after_subtree_flips",
        [("n", "int"), ("queries", "list[int]")],
        "int",
        ["trees", "recursion"],
        [
            "Nodes 1 through n form an implicit binary tree where parent(v)=floor(v/2).",
            "All values start at zero; each query flips its node and every descendant between 0 and 1.",
            "Return the number of nodes whose final value is one.",
        ],
        [
            (
                [5, [1, 2, 5]],
                "The root flip affects all nodes, the node-2 flip affects 2,4,5, and the node-5 flip affects 5; three nodes finish as one.",
            ),
            (
                [3, [1, 1]],
                "Flipping the entire tree twice restores every node to zero.",
            ),
        ],
        [
            [n, q]
            for n, q in [
                (1, [1]),
                (1, [1, 1]),
                (2, [2]),
                (3, [2]),
                (7, [2]),
                (7, [2, 3]),
                (7, [1, 2, 3]),
                (10, [5]),
                (10, [2, 5]),
                (15, [4, 4, 8]),
                (6, [1, 6]),
                (20, [2, 4, 8]),
                (31, [1, 2, 4, 8, 16]),
                (12, [3, 6, 12, 12]),
            ]
        ],
        TREE,
        [
            TREE.replace("flipped^=node in odd", "flipped=node in odd"),
            TREE.replace("if node in odd:odd.remove(node)", "if node in odd:pass"),
        ],
        [
            "Ignores flip parity inherited from ancestors.",
            "Does not cancel duplicate queries, so even repetitions remain active.",
        ],
        tree_oracle,
        random_tree,
        [
            "Only nodes queried an odd number of times matter; cancel even repetitions in a set.",
            "Recursively visit the implicit tree from node one.",
            "Carry the ancestor flip parity and toggle it when the current node is in the odd-query set.",
            "A node’s final bit is the XOR of exactly the queried ancestors on its root path, which the recursion carries once per node.",
        ],
        "O(n+q)",
        "O(n+q)",
        5,
    ),
    2447: entry(
        "count_subarrays_with_gcd",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "dynamic programming", "number theory"],
        [
            "A subarray is a nonempty contiguous segment.",
            "Compute the greatest common divisor of every segment’s values.",
            "Return how many subarrays have GCD exactly k.",
        ],
        [
            (
                [[9, 3, 1, 2, 6, 3], 3],
                "The valid subarrays are [9,3], [3], [6,3], and the final [3], giving four.",
            ),
            (
                [[4, 8, 12], 4],
                "The subarrays [4], [4,8], [4,8,12], and [8,12] have GCD four, giving four.",
            ),
        ],
        [
            [a, k]
            for a, k in [
                ([1], 1),
                ([2], 1),
                ([2], 2),
                ([2, 4], 2),
                ([3, 6, 9], 3),
                ([6, 10, 15], 5),
                ([5, 5, 5], 5),
                ([2, 3, 5], 1),
                ([8, 12, 16], 4),
                ([7, 14, 21], 7),
                ([4, 6, 8], 2),
                ([10, 20, 30, 40], 10),
                ([1, 1, 1], 1),
                ([12, 18, 24, 30], 6),
            ]
        ],
        GCD_SUBARRAYS,
        [
            GCD_SUBARRAYS.replace("current={value:1}", "current={}"),
            GCD_SUBARRAYS.replace("current.get(k,0)", "current.get(k+1,0)"),
        ],
        [
            "Omits single-element subarrays from the state.",
            "Counts GCD k+1 instead of exactly k.",
        ],
        gcd_oracle,
        random_gcd,
        [
            "Track counts of each GCD among subarrays ending at the previous index.",
            "Start a new one-element subarray, then append the current value to every prior ending subarray and merge equal resulting GCDs.",
            "Add the count stored under k.",
            "Every subarray ending here is either the singleton or uniquely extends one ending previously, so all and only qualifying segments are counted.",
        ],
        "O(n log V)",
        "O(log V)",
        5,
    ),
    2450: entry(
        "count_strings_after_k_flips",
        [("s", "str"), ("k", "int")],
        "int",
        ["strings", "linear algebra"],
        [
            "An operation flips every bit in any contiguous substring of length k.",
            "Apply operations any number of times and count distinct binary strings reachable from s.",
            "Return the count modulo 1,000,000,007.",
        ],
        [
            (
                ["1001", 3],
                "There are two possible length-three windows, and independently choosing whether to flip each produces four distinct strings.",
            ),
            (
                ["0", 1],
                "The sole bit can be flipped or left unchanged, so two strings are reachable.",
            ),
        ],
        [
            [s, k]
            for s, k in [
                ("0", 1),
                ("1", 1),
                ("00", 1),
                ("00", 2),
                ("01", 2),
                ("000", 1),
                ("000", 2),
                ("000", 3),
                ("1010", 2),
                ("1010", 4),
                ("11111", 3),
                ("010101", 2),
                ("000000", 5),
                ("1100101", 4),
            ]
        ],
        BINARY,
        [BINARY.replace("len(s)-k+1", "len(s)-k"), BINARY.replace("pow(2", "pow(3")],
        [
            "Forgets one of the n-k+1 possible windows.",
            "Incorrectly gives each binary flip window three choices.",
        ],
        binary_oracle,
        random_binary,
        [
            "There are n-k+1 possible starting positions for a length-k flip.",
            "Each window is either flipped an odd number of times or an even number, giving a binary choice.",
            "The flip vectors are linearly independent because each has a unique leftmost position not present in later vectors.",
            "Therefore all 2^(n-k+1) parity selections produce distinct reachable strings.",
        ],
        "O(log n)",
        "O(1)",
        5,
    ),
}
