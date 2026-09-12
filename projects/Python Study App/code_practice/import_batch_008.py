"""Reviewed nearest-sum, prefix matching, recursive encoding, and digit arithmetic."""
from itertools import combinations, groupby

from .import_batch_003 import entry


def closest_oracle(args):
    nums, target = args
    sums = {sum(triple) for triple in combinations(nums, 3)}
    distance = min(abs(total - target) for total in sums)
    winners = [total for total in sums if abs(total - target) == distance]
    if len(winners) != 1:
        raise ValueError("Closest-sum inputs must have a unique closest sum")
    return winners[0]


def occurrence_oracle(args):
    return args[0].find(args[1])


def say_oracle(args):
    term = "1"
    for _ in range(args[0] - 1):
        term = "".join(str(sum(1 for _ in run)) + digit for digit, run in groupby(term))
    return term


def product_oracle(args):
    # Whole-number conversion is permitted only in this offline oracle, never
    # in the learner-facing reference, which operates on individual digits.
    return str(int(args[0]) * int(args[1]))


def random_closest(rng):
    for _ in range(1000):
        args = [[rng.randint(-1000, 1000) for _ in range(rng.randint(3, 12))], rng.randint(-10000, 10000)]
        try:
            closest_oracle(args)
            return args
        except ValueError:
            continue
    raise ValueError("Could not generate a unique nearest sum")


def random_occurrence(rng):
    haystack = "".join(rng.choice("abc") for _ in range(rng.randint(1, 70)))
    if rng.random() < .5:
        left = rng.randrange(len(haystack))
        needle = haystack[left:rng.randint(left + 1, len(haystack))]
    else:
        needle = "".join(rng.choice("abc") for _ in range(rng.randint(1, 25)))
    return [haystack, needle]


def random_say(rng):
    return [rng.randint(1, 30)]


def random_product(rng):
    def number():
        if rng.random() < .1:
            return "0"
        return rng.choice("123456789") + "".join(rng.choice("0123456789") for _ in range(rng.randrange(60)))
    return [number(), number()]


CLOSEST = '''\
def three_sum_closest(nums, target):
    values = sorted(nums)
    best = sum(values[:3])
    for first in range(len(values) - 2):
        left, right = first + 1, len(values) - 1
        while left < right:
            total = values[first] + values[left] + values[right]
            if abs(total - target) < abs(best - target):
                best = total
            if total == target:
                return total
            if total < target:
                left += 1
            else:
                right -= 1
    return best
'''
OCCURRENCE = '''\
def first_occurrence(haystack, needle):
    prefix = [0] * len(needle)
    matched = 0
    for i in range(1, len(needle)):
        while matched and needle[i] != needle[matched]:
            matched = prefix[matched - 1]
        if needle[i] == needle[matched]:
            matched += 1
        prefix[i] = matched
    matched = 0
    for i, char in enumerate(haystack):
        while matched and char != needle[matched]:
            matched = prefix[matched - 1]
        if char == needle[matched]:
            matched += 1
        if matched == len(needle):
            return i - len(needle) + 1
    return -1
'''
SAY = '''\
def count_and_say(n):
    if n == 1:
        return "1"
    previous = count_and_say(n - 1)
    parts, start = [], 0
    while start < len(previous):
        end = start + 1
        while end < len(previous) and previous[end] == previous[start]:
            end += 1
        parts.append(str(end - start) + previous[start])
        start = end
    return "".join(parts)
'''
PRODUCT = '''\
def multiply_strings(num1, num2):
    if num1 == "0" or num2 == "0":
        return "0"
    digits = [0] * (len(num1) + len(num2))
    for i in range(len(num1) - 1, -1, -1):
        for j in range(len(num2) - 1, -1, -1):
            total = digits[i + j + 1] + (ord(num1[i]) - ord("0")) * (ord(num2[j]) - ord("0"))
            digits[i + j + 1] = total % 10
            digits[i + j] += total // 10
    start = 0
    while start < len(digits) - 1 and digits[start] == 0:
        start += 1
    return "".join(str(digit) for digit in digits[start:])
'''

BATCH = {
    16: entry("three_sum_closest", [("nums", "list[int]"), ("target", "int")], "int",
        ["arrays", "two-pointers", "sorting"],
        ["3 <= len(nums) <= 500; -1000 <= nums[i] <= 1000; -10000 <= target <= 10000.",
         "Choose three distinct indices, not necessarily three different values. Return their sum, not their indices or distance from target.",
         "The closest sum is unique: two different sums cannot tie for the smallest absolute distance to target."],
        [([[-1, 2, 1, -4], 1], "Choosing -1, 2, and 1 gives 2, only 1 away from the target; every other triple is farther away."),
         ([[0, 0, 0], 1], "Use the three separate zero entries. Their values may be equal, and their sum is 0.")],
        [[[1, 2, 3], 0], [[1, 2, 3], 100], [[-5, -4, -3], -20], [[1, 1, 1, 1], 3],
         [[-2, 0, 2, 4], 2], [[0, 0, 1, 1], 0], [[-1000, 0, 1000], 10000],
         [[-1000, -999, -998], -10000], [[-5, -1, 2, 8], 0], [[-4, -1, 1, 5], 3],
         [[-8, -2, 3, 4, 9], 6], [[-3, -3, 2, 2, 7], 1]],
        CLOSEST,
        [CLOSEST.replace("left, right = first + 1,", "left, right = first,"),
         CLOSEST.replace("abs(total - target) < abs(best - target)", "abs(total) < abs(best)")],
        ["Allows the first index to be selected again as the left index.", "Minimizes distance to zero rather than to the given target."],
        closest_oracle, random_closest,
        ["Sorting makes the direction of sum changes predictable.", "Fix one index, then move two pointers over the remaining suffix.",
         "Record a sum when its absolute target distance improves. Increase the left pointer if too small; otherwise decrease the right pointer.",
         "Start the left pointer after the fixed index so each chosen position is different; duplicate values are allowed."],
        "Sort a copy and fix each possible first index. For the remaining suffix, start at its smallest and largest values. A sum below target can only improve by increasing the left value; a sum above target can only improve by decreasing the right value. Track the smallest absolute target distance and return immediately on an exact match. Each fixed-index pass is linear. The independent oracle enumerates all triples of distinct positions and rejects ambiguous inputs with two equally close sums.",
        "O(n²)", "O(n) for the sorted copy", difficulty=5, stress=[([[1] * 500, 0], 3)]),
    28: entry("first_occurrence", [("haystack", "str"), ("needle", "str")], "int",
        ["strings", "string-matching"],
        ["1 <= len(haystack), len(needle) <= 10000; both contain only lowercase English letters.",
         "Return the zero-based starting index of the first contiguous occurrence, or -1 when absent."],
        [(["sadbutsad", "sad"], "The pattern starts at indices 0 and 6; return 0 because it is the first occurrence."),
         (["leetcode", "leeto"], "The shared prefix leet is insufficient: the next characters differ, and the complete pattern never appears.")],
        [["a", "a"], ["a", "b"], ["a", "aa"], ["abc", "c"], ["abc", "abc"], ["aaaaa", "aaa"],
         ["aaaab", "aaab"], ["abababc", "ababc"], ["mississippi", "issip"], ["abcabc", "bca"],
         ["xyzabc", "abc"], ["abcdef", "ace"]],
        OCCURRENCE,
        [OCCURRENCE.replace("return i - len(needle) + 1", "return i"),
         OCCURRENCE.replace("matched = prefix[matched - 1]", "matched = 0")],
        ["Returns the final matched position rather than the start of the occurrence.",
         "Discards every matched prefix on a mismatch, missing overlapping matches."],
        occurrence_oracle, random_occurrence,
        ["Matching a substring requires consecutive characters; a subsequence is not enough.",
         "A direct sliding-window comparison is a useful first solution. For the linear target, reuse matched prefixes with a KMP prefix table.",
         "Build longest proper prefix/suffix lengths. On mismatch, fall back through those lengths; on a full match, return current_index-pattern_length+1.",
         "Repeated letters and overlapping prefixes are the important cases for testing fallback logic."],
        "A simple correct baseline checks the pattern at each possible start in O(haystack length × needle length) time. The reference meets the stronger linear target using KMP. Its prefix table records how much of a matched pattern can survive a mismatch, avoiding rechecking characters. Scan the text in order; the first full match therefore has the earliest start. The independent oracle uses Python's built-in substring search.",
        "O(len(haystack) + len(needle))", "O(len(needle))", difficulty=3,
        stress=[(["a" * 9999 + "b", "a" * 4999 + "b"], 5000)]),
    38: entry("count_and_say", [("n", "int")], "str", ["strings", "recursion"],
        ["1 <= n <= 30.", "Term 1 is the string '1'. Each later term describes maximal consecutive equal-digit runs in the previous term as count followed by digit.",
         "Return a string. Encode consecutive runs separately, not the total frequency of each digit."],
        [([4], "The terms are 1 → 11 → 21 → 1211: the fourth describes one 2 followed by one 1."),
         ([1], "The base term is defined as '1'; no encoding step is performed.")],
        [[n] for n in (2, 3, 5, 6, 7, 8, 9, 10, 12, 15, 20, 30)],
        SAY,
        [SAY.replace("str(end - start) + previous[start]", "previous[start] + str(end - start)"),
         SAY.replace("if n == 1:", "if n <= 2:")],
        ["Writes digit then count instead of count then digit.", "Mistakes the second term for another base case, shifting the sequence."],
        say_oracle, random_say,
        ["A recursive solution needs only the previous term and an encoder for consecutive runs.",
         "Use n=1 as the base case. Recursively obtain term n-1, then scan it with start/end pointers.",
         "Extend end while the digit equals the run's first digit; append the run length and digit, then begin at end.",
         "Do not merge equal digits separated by another digit. The same recurrence can also be implemented iteratively."],
        "The base term is '1'. Recursively calculate the previous term, then scan each maximal equal-digit run once, appending its length and digit. Join the pieces to obtain the requested term. This directly follows the recursive definition, with depth at most 30. If L_i is the length of term i, total work is proportional to the sum of generated term lengths; working storage is O(max L_i + n), including intermediate strings and call frames. An iterative itertools.groupby implementation provides the independent oracle.",
        "O(sum of lengths of terms 1 through n)", "O(maximum term length + n)", difficulty=5),
    43: entry("multiply_strings", [("num1", "str"), ("num2", "str")], "str",
        ["strings", "math", "simulation"],
        ["1–200 decimal digits per input. Inputs have no leading zeros except the single string '0'.",
         "Return the product as a decimal string without leading zeros, or '0' for a zero product.",
         "Do not convert whole input strings to integers or use a BigInteger library. Work with individual digits and carries."],
        [(["2", "3"], "Two multiplied by three is six, returned as the string '6'."),
         (["123", "456"], "The partial products are 738, 6150, and 49200; adding them gives the string '56088'.")],
        [["0", "0"], ["0", "12345"], ["987", "0"], ["1", "7"], ["9", "9"], ["99", "99"],
         ["10", "10"], ["101", "101"], ["1000", "1000"], ["999", "9"], ["1234", "5678"], ["11111", "11111"]],
        PRODUCT,
        [PRODUCT.replace("digits[i + j] += total // 10", "digits[i + j] += 0"),
         PRODUCT.replace("for digit in digits[start:])", "for digit in digits[start:] if digit != 0)")],
        ["Drops carry digits produced by column multiplication.", "Removes all zero digits, including meaningful interior or trailing zeros."],
        product_oracle, random_product,
        ["Use the same column multiplication used on paper; the result needs at most m+n digits.",
         "A product of input positions i and j contributes at output positions i+j and i+j+1.",
         "Process both inputs from right to left, add the existing lower-column value, write total%10, and carry total//10 left.",
         "Remove only leading zero positions. Keep interior and trailing zeros, and handle a zero input explicitly."],
        "Allocate m+n digit slots. Multiply individual digit values from right to left. For each pair, include the stored lower-column value, retain its units digit, and carry the tens contribution to the preceding slot. This ordering normalizes each lower position before it is finalized. Convert the digit list to a string after removing only leading zero slots. No whole-input numeric conversion is used. The independent offline oracle deliberately uses Python's exact whole-number multiplication instead.",
        "O(len(num1) × len(num2))", "O(len(num1) + len(num2))", difficulty=5,
        stress=[(["9" * 200, "9" * 200], str((10**200 - 1) ** 2))]),
}

# The spreadsheet's compressed wording incorrectly says distinct integers.
# The preserved upstream statement specifies distinct indices, allowing repeats.
BATCH[16]["statement"] = (
    "Given nums and target, choose three values at distinct indices whose sum is closest to target. "
    "The selected values may be equal. Return the sum, not the chosen indices. "
    "Each input has a unique closest sum."
)
