"""Bit ranges, numeric cycles, sequence invariants, and shortest palindromes."""
from functools import reduce
from math import isqrt
from operator import and_

from .import_batch_003 import entry


def reverse_oracle(args):
    return int(f"{args[0]:032b}"[::-1], 2)


def range_oracle(args):
    return reduce(and_, range(args[0], args[1] + 1))


def happy_oracle(args):
    value, seen = args[0], set()
    while value != 1 and value not in seen:
        seen.add(value)
        value = sum(int(char)**2 for char in str(value))
    return value == 1


def prime_oracle(args):
    return sum(all(value % divisor for divisor in range(2, isqrt(value) + 1))
               for value in range(2, args[0]))


def isomorphic_oracle(args):
    first, second = args
    return [first.index(char) for char in first] == [second.index(char) for char in second]


def window_oracle(args):
    target, nums = args
    best = len(nums) + 1
    for left in range(len(nums)):
        total = 0
        for right in range(left, len(nums)):
            total += nums[right]
            if total >= target:
                best = min(best, right - left + 1)
                break
    return 0 if best > len(nums) else best


def circle_oracle(args):
    nums = args[0]
    best = 0
    for mask in range(1 << len(nums)):
        if len(nums) > 1 and any(mask & (1 << i) and mask & (1 << ((i + 1) % len(nums))) for i in range(len(nums))):
            continue
        best = max(best, sum(value for i, value in enumerate(nums) if mask & (1 << i)))
    return best


def palindrome_oracle(args):
    text = args[0]
    for end in range(len(text), -1, -1):
        if text[:end] == text[:end][::-1]:
            return text[end:][::-1] + text


def combinations_oracle(args):
    k, target = args
    result = []
    for mask in range(1 << 9):
        if mask.bit_count() == k:
            chosen = [i + 1 for i in range(9) if mask & (1 << i)]
            if sum(chosen) == target:
                result.append(chosen)
    return result


def random_reverse(rng):
    return [2 * rng.randrange(2**30)]


def random_range(rng):
    left = rng.randrange(2**31)
    return [left, min(2**31 - 1, left + rng.randrange(129))]


def random_happy(rng):
    return [rng.randint(1, 2**31 - 1)]


def random_prime(rng):
    return [rng.randrange(501)]


def random_isomorphic(rng):
    alphabet = "Aab0 \t\n\x00\x7f"
    first = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 40)))
    if rng.random() < .5:
        mapping = dict(zip(alphabet, rng.sample([chr(i) for i in range(128)], len(alphabet))))
        second = "".join(mapping[char] for char in first)
    else:
        second = "".join(rng.choice(alphabet) for _ in first)
    return [first, second]


def random_window(rng):
    nums = [rng.randint(1, 20) for _ in range(rng.randint(1, 30))]
    return [rng.randint(1, sum(nums) + 20), nums]


def random_circle(rng):
    return [[rng.randrange(21) for _ in range(rng.randint(1, 11))]]


def random_palindrome(rng):
    return ["".join(rng.choice("abc") for _ in range(rng.randrange(51)))]


def random_combinations(rng):
    return [rng.randint(2, 9), rng.randint(1, 60)]


REVERSE = '''\
def reverse_bits(n):
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result
'''
RANGE = '''\
def range_bitwise_and(left, right):
    while left < right:
        right &= right - 1
    return right
'''
HAPPY = '''\
def is_happy(n):
    def step(value):
        total = 0
        while value:
            value, digit = divmod(value, 10)
            total += digit * digit
        return total
    slow, fast = step(n), step(step(n))
    while fast != 1 and slow != fast:
        slow = step(slow)
        fast = step(step(fast))
    return fast == 1
'''
PRIMES = '''\
def count_primes(n):
    if n <= 2:
        return 0
    flags = bytearray([1]) * n
    flags[0] = flags[1] = 0
    prime = 2
    while prime * prime < n:
        if flags[prime]:
            start = prime * prime
            flags[start:n:prime] = bytes((n - 1 - start) // prime + 1)
        prime += 1
    return sum(flags)
'''
ISOMORPHIC = '''\
def isomorphic_strings(s, t):
    forward, backward = {}, {}
    for a, b in zip(s, t):
        if forward.get(a, b) != b or backward.get(b, a) != a:
            return False
        forward[a], backward[b] = b, a
    return True
'''
WINDOW = '''\
def minimum_subarray_length(target, nums):
    left, total, best = 0, 0, len(nums) + 1
    for right, value in enumerate(nums):
        total += value
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best > len(nums) else best
'''
CIRCLE = '''\
def circular_house_profit(nums):
    if len(nums) == 1:
        return nums[0]
    def rob(start, stop):
        previous, current = 0, 0
        for i in range(start, stop):
            previous, current = current, max(current, previous + nums[i])
        return current
    return max(rob(0, len(nums) - 1), rob(1, len(nums)))
'''
PALINDROME = '''\
def shortest_front_palindrome(s):
    joined = s + "#" + s[::-1]
    prefix = [0] * len(joined)
    for i in range(1, len(joined)):
        match = prefix[i - 1]
        while match and joined[i] != joined[match]:
            match = prefix[match - 1]
        if joined[i] == joined[match]:
            match += 1
        prefix[i] = match
    return s[prefix[-1]:][::-1] + s
'''
APPEND_WRONG = '''\
def shortest_front_palindrome(s):
    for start in range(len(s) + 1):
        if s[start:] == s[start:][::-1]:
            return s + s[:start][::-1]
'''
COMBINATIONS = '''\
def fixed_digit_combinations(k, n):
    result, path = [], []
    def search(start, slots, remaining):
        if slots == 0:
            if remaining == 0:
                result.append(path[:])
            return
        if remaining < slots * (2 * start + slots - 1) // 2 or remaining > slots * (19 - slots) // 2:
            return
        for value in range(start, 11 - slots):
            path.append(value)
            search(value + 1, slots - 1, remaining - value)
            path.pop()
    search(1, k, n)
    return result
'''

BATCH = {
    190: entry("reverse_bits", [("n", "int")], "int", ["bit-manipulation", "math"],
        ["The retained source contract specifies an EVEN integer n with 0 ≤ n ≤ 2^31 - 2.", "Reverse all 32 bit positions, including leading zeroes, and return the resulting integer. Do not reverse only the nonzero-width binary representation."],
        [([43261596], "The 32-bit pattern 00000010100101000001111010011100 reverses to 00111001011110000010100101000000, representing 964176192."),
         ([2147483644], "The two low zero bits become two high zero bits. Reversing the full 32-bit pattern gives 1073741822.")],
        [[n] for n in (0, 2, 4, 8, 16, 32, 64, 128, 256, 1024, 2147483646, 1073741824)],
        REVERSE, ['def reverse_bits(n):\n    return int(bin(n)[2:][::-1], 2)\n', REVERSE.replace("range(32)", "range(31)")],
        ["Drops leading zeroes before reversal and therefore shifts set bits into wrong positions.", "Reverses only 31 positions instead of the specified 32-bit width."], reverse_oracle, random_reverse,
        ["The width is fixed even when the input number needs only a few nonzero bit positions.", "Read the input from its least-significant bit while shifting the output left.", "Repeat exactly 32 times: append n&1 to the output, then shift n right by one.", "For n=2, the single set bit at position 1 moves to position 30, giving 1073741824."],
        "Each iteration removes one low input bit and appends it to the high-to-low construction of the answer. Exactly 32 iterations preserve leading zero positions. The independent oracle formats a 32-character binary string and reverses that string. Tests follow the retained upstream even, nonnegative signed-range constraint rather than importing historical unsigned examples outside this source snapshot. Under that constraint the returned number also fits a nonnegative signed-32-bit value.",
        "O(32), constant for the fixed width", "O(1)", difficulty=3),
    201: entry("range_bitwise_and", [("left", "int"), ("right", "int")], "int", ["bit-manipulation", "math"],
        ["0 ≤ left ≤ right ≤ 2^31 - 1.", "AND every integer in the inclusive interval, not only the two endpoints. Very wide intervals must not be enumerated."],
        [([5, 7], "Binary 101 AND 110 AND 111 is 100, so the answer is 4; just ANDing 5 and 7 would incorrectly give 5."),
         ([0, 1], "The interval includes zero, so the AND of all its values is zero.")],
        [[a, b] for a, b in ((0, 0), (1, 1), (2, 3), (4, 7), (8, 15), (6, 7), (5, 6), (10, 11), (10, 15), (12, 15), (2147483646, 2147483647), (2147483647, 2147483647))],
        RANGE, ['def range_bitwise_and(left, right):\n    return left & right\n', RANGE.replace("left < right", "left + 1 < right")],
        ["Ignores intermediate integers that clear bits shared by the endpoints.", "Stops before resolving adjacent endpoints, leaving a varying low bit set."], range_oracle, random_range,
        ["A bit survives only if it is one in every number across the interval.", "The answer is the common high-bit prefix of the endpoints, with lower varying bits cleared.", "While right exceeds left, clear right's lowest set bit using right &= right-1; return the remaining prefix.", "A single-value interval must return that value unchanged; wide intervals still need at most 31 bit-clearing steps."],
        "Crossing the boundary represented by the right endpoint's lowest set bit means that bit cannot survive the full interval AND. Repeatedly clearing such bits leaves the shared high-bit prefix. The independent oracle explicitly ANDs all integers in bounded small ranges. Large direct fixtures span billions of integers and have simple known prefixes, ensuring that the reference does not depend on interval width.",
        "O(31), bounded by integer bit width", "O(1)", difficulty=5,
        stress=[([1, 2147483647], 0), ([1073741824, 2147483647], 1073741824)]),
    202: entry("is_happy", [("n", "int")], "bool", ["math", "two-pointers", "cycle-detection"],
        ["1 ≤ n ≤ 2^31 - 1.", "Repeatedly replace n by the sum of the squares of its decimal digits. Return True if the sequence reaches 1; return False if it repeats without reaching 1."],
        [([19], "The sequence is 19→82→68→100→1, so 19 is happy even though its first transformation is not 1."),
         ([2], "The sequence eventually repeats the cycle 4→16→37→58→89→145→42→20→4 and never reaches 1.")],
        [[n] for n in (1, 7, 10, 13, 23, 28, 31, 32, 44, 46, 100, 2147483647)],
        HAPPY, ['def is_happy(n):\n    return sum(int(c)**2 for c in str(n)) == 1\n', 'def is_happy(n):\n    return n % 9 == 1\n'],
        ["Checks only one transformation instead of following the sequence to a terminal cycle.", "Confuses squared-digit iteration with an ordinary digit-sum/digital-root rule."], happy_oracle, random_happy,
        ["The next number is deterministic, so revisiting a number means the future will repeat.", "Use cycle detection: one pointer advances once and the other twice through the digit-square transformation.", "Stop when the fast pointer reaches 1 or the pointers meet; only reaching 1 is happy.", "Arithmetic digit extraction and two pointers avoid storing the full history; a visited set is another valid approach."],
        "The digit-square transformation quickly enters a bounded set of small numbers. Floyd's slow/fast pointers detect a repeated state without a history set. Reaching 1 is the successful fixed point; a meeting elsewhere is a nonhappy cycle. The independent oracle instead converts numbers to strings, squares each digit, and retains every visited value in a set.",
        "O(log n) to process the initial digits, then bounded-state cycle work for 32-bit inputs", "O(1)", difficulty=3),
    204: entry("count_primes", [("n", "int")], "int", ["math", "arrays", "sieve"],
        ["0 ≤ n ≤ 5000000.", "Count primes STRICTLY LESS than n. Zero and one are not prime; a prime equal to n is excluded."],
        [([10], "The four primes below 10 are 2,3,5,7."),
         ([2], "Although 2 is prime, it is not strictly less than itself, so the answer is 0.")],
        [[n] for n in (0, 1, 3, 4, 5, 6, 7, 8, 9, 11, 25, 26)],
        PRIMES, [PRIMES.replace("    if n <=", "    n += 1\n    if n <=", 1), PRIMES.replace("start = prime * prime", "start = prime * prime + prime")],
        ["Counts primes through n inclusively, violating the strict upper bound.", "Starts crossing off after p² and leaves prime squares incorrectly marked prime."], prime_oracle, random_prime,
        ["Instead of testing every candidate independently, let each prime eliminate its multiples.", "Maintain a compact prime-candidate array for values below n.", "For each surviving p with p²<n, clear p²,p²+p,… below n; count remaining candidates after excluding 0 and 1.", "Starting at p² is valid because smaller composite multiples already have a smaller prime factor."],
        "The sieve of Eratosthenes marks composites by prime factors. Byte storage and stepped slice marking keep the maximum input practical in Pyodide. The independent oracle trial-divides each small candidate through its integer square root. A separate Euler linear-sieve regression verifies the full 5000000 boundary count, 348513, rather than relying only on the reference to supply that expected result.",
        "O(n log log n)", "O(n)", difficulty=5, stress=[([5000000], 348513)]),
    205: entry("isomorphic_strings", [("s", "str"), ("t", "str")], "bool", ["strings", "hash-maps"],
        ["s and t have equal lengths from 1 to 50000 and contain valid ASCII characters, including spaces or control characters.", "Each source character maps consistently to exactly one target character, and two different source characters cannot share a target. Mapping a character to itself is allowed."],
        [(["egg", "add"], "Map e→a and g→d; both occurrences of g use the same target character."),
         (["foo", "bar"], "The two o positions would need different targets, a and r, so no consistent mapping exists.")],
        [[s, t] for s, t in (("a", "b"), ("aa", "ab"), ("ab", "aa"), ("ab", "ba"), ("paper", "title"), ("aabb", "abab"), ("abc", "def"), ("aba", "baa"), ("11", "22"), (" \t ", "a0a"), ("\x00A\x00", "\x7fz\x7f"), ("aA", "Aa"))],
        ISOMORPHIC, [ISOMORPHIC.replace(" or backward.get(b, a) != a", ""), 'def isomorphic_strings(s, t):\n    from collections import Counter\n    return sorted(Counter(s).values()) == sorted(Counter(t).values())\n'],
        ["Enforces consistency in only one direction and permits different source characters to merge.", "Compares frequency counts but ignores where the repeated characters occur."], isomorphic_oracle, random_isomorphic,
        ["The equality pattern of positions must be preserved in both directions.", "Track a source-to-target map and a target-to-source map.", "For each aligned pair, reject conflicts in either map, then record both mappings.", "Equal frequency lists are not enough: aabb and abab repeat at different positions."],
        "Two maps enforce a bijection between the characters actually encountered. A conflict in either direction invalidates the replacement rule. The independent oracle compares first-occurrence position sequences rather than character maps. This raw character-to-character contract differs from word-pattern mapping over whitespace-separated words: spaces, tabs, and control characters here are ordinary positions to map.",
        "O(len(s))", "O(1) for the fixed ASCII alphabet", difficulty=3,
        stress=[(["ab" * 25000, "xy" * 25000], True)]),
    209: entry("minimum_subarray_length", [("target", "int"), ("nums", "list[int]")], "int", ["arrays", "sliding-window", "two-pointers"],
        ["1 ≤ target ≤ 10^9. nums contains 1–100000 POSITIVE integers, each at most 10000.", "Return the shortest nonempty contiguous subarray length whose sum is at least target, or 0 if none exists. Do not reorder or skip intervening values."],
        [([7, [2, 3, 1, 2, 4, 3]], "The contiguous final pair [4,3] sums to 7 and has length 2; no single value reaches 7."),
         ([4, [1, 4, 4]], "A single 4 reaches the target, so the minimum length is 1.")],
        [[target, values] for target, values in ((1, [1]), (2, [1]), (5, [10]), (10, [1, 1, 1, 10]), (6, [1, 2, 3]), (7, [1, 2, 3]), (3, [1, 1, 1]), (3, [3, 1, 1]), (11, [1] * 8), (15, [1, 2, 3, 4, 5]), (8, [2] * 4), (9, [2] * 5))],
        WINDOW, [WINDOW.replace("total >= target", "total == target"), WINDOW.replace("while total >= target:", "if total >= target:")],
        ["Accepts only exact sums, missing shorter windows that exceed the target.", "Shrinks the left boundary only once and misses shorter still-valid windows."], window_oracle, random_window,
        ["Positive values make the window sum increase when extending right and decrease when removing left.", "Expand until the sum qualifies, then shrink repeatedly while it still qualifies.", "Add each right value; while sum≥target, record the width and remove the left value. Return zero if no qualifying width was found.", "The condition is at least the target, not exactly equal. Positivity is what makes the two-pointer reasoning valid."],
        "For each right boundary, shrink until the remaining window no longer qualifies, checking every candidate width on the way. Each index enters and leaves once, so the total work is linear. The independent oracle enumerates each possible left boundary and directly accumulates rightward sums. Unlike existing exact-sum or maximum-length exercises, this asks for a minimum width with an inequality and guaranteed positive input.",
        "O(n)", "O(1)", difficulty=5,
        stress=[([1000000000, [10000] * 100000], 100000), ([1, [10000] * 100000], 1)]),
    213: entry("circular_house_profit", [("nums", "list[int]")], "int", ["arrays", "dynamic-programming"],
        ["1–100 houses, each with 0–1000 money units.", "Houses form a circle: the first and last are adjacent. Choose no two adjacent houses; choosing none is allowed. A single house may be chosen."],
        [([[2, 3, 2]], "The two outer 2s are neighbors around the circle and cannot both be chosen; the best total is the middle 3."),
         ([[1, 2, 3, 1]], "Choose positions 0 and 2 for total 4; they are not adjacent, and the final house is skipped.")],
        [[a] for a in ([0], [5], [1, 2], [2, 1], [1, 1], [2, 2, 2], [5, 1, 1, 5], [10, 0, 0, 10], [1, 3, 1, 3, 100], [0] * 4, [1000, 1, 1000], [4, 1, 2, 7, 5, 3, 1])],
        CIRCLE, [CIRCLE.replace("max(rob(0, len(nums) - 1), rob(1, len(nums)))", "rob(0, len(nums))"), CIRCLE.replace("max(rob(0, len(nums) - 1), rob(1, len(nums)))", "rob(0, len(nums) - 1)")],
        ["Uses the linear-street recurrence and illegally takes both circular endpoints.", "Always excludes the final house, missing better solutions that instead exclude the first."], circle_oracle, random_circle,
        ["A valid choice cannot contain both endpoints of the array.", "Solve two linear ranges: one excludes the first house and the other excludes the last.", "Within each range track the best totals for the previous two positions; return the larger range answer, handling a singleton separately.", "Use index ranges rather than slices to keep auxiliary storage constant."],
        "Every valid circular selection omits at least one endpoint, so the two linear subproblems cover all possibilities. Each linear range uses the choose-or-skip recurrence with two running values. The independent oracle enumerates every subset of small circular inputs and explicitly rejects adjacent selected positions, including the wraparound edge. The singleton special case avoids treating a house as its own forbidden neighbor.",
        "O(n)", "O(1)", difficulty=5, stress=[([[1000] * 100], 50000)]),
    214: entry("shortest_front_palindrome", [("s", "str")], "str", ["strings", "string-matching", "prefix-function"],
        ["0–50000 lowercase English letters.", "Add characters ONLY before the original string. Return the shortest resulting palindrome, preserving the original string as a suffix. Empty input returns an empty string."],
        [(["aacecaaa"], "Its longest palindromic prefix is 'aacecaa'; prepend the reverse of the remaining 'a' to obtain 'aaacecaaa'."),
         (["abcd"], "Only the initial 'a' is a palindromic prefix; prepend 'dcb' to get 'dcbabcd'. Appending characters is not allowed.")],
        [[s] for s in ("", "a", "aa", "ab", "aba", "abb", "abba", "aab", "baa", "abcba", "abab", "aaab")],
        PALINDROME, ['def shortest_front_palindrome(s):\n    return s[::-1] + s\n', APPEND_WRONG],
        ["Always prepends the full reverse, producing a palindrome that is longer than necessary.", "Finds a palindrome by adding characters at the end instead of the permitted front."], palindrome_oracle, random_palindrome,
        ["The part of the original string that need not be mirrored is a palindromic prefix.", "Find the longest palindromic prefix, then prepend the reversed remaining suffix.", "Build the prefix-function for s + a separator + reverse(s); its final value is the longest palindromic-prefix length.", "Choose a separator outside lowercase letters. Prefix-function fallback avoids repeatedly rescanning long almost-matching prefixes."],
        "If the longest palindromic prefix has length p, mirroring the remaining suffix in front produces a palindrome using n-p added characters. Fewer added characters would imply a longer palindromic prefix, so this is minimal. The prefix-function on s#reverse(s) finds p in linear time because the separator cannot occur in s. The independent oracle scans candidate prefixes directly for palindromicity; an additional small-domain test enumerates possible prepended strings to verify minimality without assuming the prefix theorem.",
        "O(len(s))", "O(len(s))", difficulty=8,
        stress=[(["a" * 49999 + "b"], "b" + "a" * 49999 + "b"), (["abcd" * 12500], ("abcd" * 12500)[1:][::-1] + "abcd" * 12500)]),
    216: entry("fixed_digit_combinations", [("k", "int"), ("n", "int")], "list[list[int]]", ["backtracking", "recursion", "combinations"],
        ["2 ≤ k ≤ 9 and 1 ≤ n ≤ 60.", "Choose exactly k DISTINCT numbers from 1 through 9 whose sum is n. Return each combination once; combinations and the numbers within them may appear in any order."],
        [([3, 7], "The only three distinct digits summing to 7 are 1,2,4. Repeating a digit or using fewer than three does not qualify."),
         ([3, 9], "The three valid combinations are [1,2,6], [1,3,5], and [2,3,4]; each contains exactly three different digits.")],
        [[k, n] for k, n in ((2, 1), (2, 3), (2, 17), (2, 18), (3, 6), (3, 24), (4, 1), (4, 10), (4, 30), (9, 45), (9, 44), (8, 36))],
        COMBINATIONS, [COMBINATIONS.replace("search(value + 1,", "search(value,"), COMBINATIONS.replace("if slots == 0:", "if remaining == 0:")],
        ["Allows reuse of the current digit rather than advancing to the next unused digit.", "Accepts a target sum before exactly k digits have been chosen."], combinations_oracle, random_combinations,
        ["Both the digit count and the sum must match, and no digit can be reused.", "Choose digits in increasing order so each combination is constructed once.", "Recursively choose the next digit above the previous one, reduce the remaining count and sum, and record only when both reach zero.", "Prune when the remaining sum is below the smallest possible distinct-digit total or above the largest one."],
        "Increasing choices eliminate permutations of the same combination and prevent digit reuse. The recursion tracks the next allowed digit, remaining slots, and remaining sum. Minimum/maximum possible sums prune impossible branches. The independent oracle enumerates all 512 subsets of digits 1–9 and filters by size and sum. Although the input domain is finite, its 480 (k,n) pairs easily support distinct visible/hidden cases; a regression exhausts every pair, in addition to the 500 seeded comparisons.",
        "O(2^9 × 9), bounded by the nine available digits", "O(k) recursion excluding output", difficulty=5,
        stress=[([9, 60], [])]),
}
BATCH[214]["prerequisites"] = ["strings", "string-matching"]
BATCH[216]["comparator"] = "unordered_nested"
