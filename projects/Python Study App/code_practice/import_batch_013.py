"""Consecutive values, minimum palindrome cuts, signed bits, and postfix evaluation."""
from collections import Counter
from fractions import Fraction

from .import_batch_003 import entry


def consecutive_oracle(args):
    ordered = sorted(set(args[0]))
    best = run = 0
    previous = None
    for value in ordered:
        run = run + 1 if previous is not None and value == previous + 1 else 1
        best = max(best, run)
        previous = value
    return best


def cuts_oracle(args):
    text = args[0]
    best = len(text) - 1
    # Enumerate cuts directly instead of expanding palindrome centers or DP.
    for mask in range(1 << (len(text) - 1)):
        count = mask.bit_count()
        if count >= best:
            continue
        start = 0
        for end in range(1, len(text) + 1):
            if end == len(text) or mask & (1 << (end - 1)):
                piece = text[start:end]
                if piece != piece[::-1]:
                    break
                start = end
        else:
            best = count
    return best


def single_oracle(args):
    counts = Counter(args[0])
    if sum(count == 1 for count in counts.values()) != 1 or any(count not in (1, 3) for count in counts.values()):
        raise ValueError("Single Number II needs one singleton and all other counts equal to three")
    return next(value for value, count in counts.items() if count == 1)


def arithmetic(left, right, operator):
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    return int(Fraction(left, right))


def rpn_oracle(args):
    tokens = iter(reversed(args[0]))
    def expression():
        token = next(tokens)
        if token not in {"+", "-", "*", "/"}:
            return int(token)
        right = expression()
        left = expression()
        return arithmetic(left, right, token)
    result = expression()
    if next(tokens, None) is not None:
        raise ValueError("Postfix input contains more than one expression")
    return result


def random_consecutive(rng):
    values = [rng.randint(-30, 30) for _ in range(rng.randrange(81))]
    rng.shuffle(values)
    return [values]


def random_cuts(rng):
    return ["".join(rng.choice("abc") for _ in range(rng.randint(1, 10)))]


def random_single(rng):
    chosen = rng.sample(list(range(-30, 31)) + [-(2**31), 2**31 - 1], rng.randint(1, 12))
    values = [chosen[0]] + [value for value in chosen[1:] for _ in range(3)]
    rng.shuffle(values)
    return [values]


def random_rpn(rng):
    def make(depth):
        if depth == 0 or rng.random() < .3:
            value = rng.randint(-200, 200)
            return [str(value)], value
        left, a = make(depth - 1)
        right, b = make(depth - 1)
        operator = rng.choice(("+", "-", "*", "/") if b else ("+", "-", "*"))
        value = arithmetic(a, b, operator)
        if not -(2**31) <= value < 2**31:
            return ["0"], 0
        return left + right + [operator], value
    return [make(rng.randint(0, 4))[0]]


CONSECUTIVE = '''\
def longest_consecutive(nums):
    values = set(nums)
    best = 0
    for value in values:
        if value - 1 not in values:
            end = value
            while end in values:
                end += 1
            best = max(best, end - value)
    return best
'''
ADJACENT = '''\
def longest_consecutive(nums):
    best = run = 0
    previous = None
    for value in nums:
        run = run + 1 if previous is not None and value == previous + 1 else 1
        best = max(best, run)
        previous = value
    return best
'''
COUNT_DUPLICATES = '''\
def longest_consecutive(nums):
    best = run = 0
    previous = None
    for value in sorted(nums):
        run = run + 1 if previous is not None and value - previous in (0, 1) else 1
        best = max(best, run)
        previous = value
    return best
'''
CUTS = '''\
def minimum_palindrome_cuts(s):
    cuts = list(range(-1, len(s)))
    for center in range(len(s)):
        for left, right in ((center, center), (center, center + 1)):
            while left >= 0 and right < len(s) and s[left] == s[right]:
                cuts[right + 1] = min(cuts[right + 1], cuts[left] + 1)
                left -= 1
                right += 1
    return cuts[-1]
'''
SINGLE = '''\
def single_number_three(nums):
    result = 0
    for bit in range(32):
        count = sum((value >> bit) & 1 for value in nums)
        if count % 3:
            result |= 1 << bit
    if result >= 1 << 31:
        result -= 1 << 32
    return result
'''
XOR = '''\
def single_number_three(nums):
    result = 0
    for value in nums:
        result ^= value
    return result
'''
RPN = '''\
def evaluate_rpn(tokens):
    stack = []
    for token in tokens:
        if token not in ("+", "-", "*", "/"):
            stack.append(int(token))
            continue
        right, left = stack.pop(), stack.pop()
        if token == "+":
            value = left + right
        elif token == "-":
            value = left - right
        elif token == "*":
            value = left * right
        else:
            quotient = abs(left) // abs(right)
            value = -quotient if (left < 0) != (right < 0) else quotient
        stack.append(value)
    return stack[0]
'''

BATCH = {
    128: entry("longest_consecutive", [("nums", "list[int]")], "int", ["arrays", "hash-maps"],
        ["0–100000 integers, each between -10^9 and 10^9.", "Find the longest run of distinct consecutive values, regardless of input position. Repeated copies do not lengthen a run; an empty input returns 0.",
         "Target O(n) expected time, without sorting the input."],
        [([[100, 4, 200, 1, 3, 2]], "Values 1,2,3,4 form a run of length 4 even though they are scattered in the input."),
         ([[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], "Every value from 0 through 8 exists, giving length 9; the second zero adds nothing.")],
        [[values] for values in ([], [0], [1, 1, 1], [2, 1], [1, 3], [-2, -1, 0], [5, 4, 3, 2, 1],
                                 [1, 2, 2, 3], [10, 11, 1, 2, 3], [-1000000000, -999999999],
                                 [999999999, 1000000000], [0, 2, 4, 6])],
        CONSECUTIVE, [ADJACENT, COUNT_DUPLICATES],
        ["Measures consecutive positions in the original array instead of consecutive values anywhere.",
         "Counts duplicate values as extra positions in a consecutive run."], consecutive_oracle, random_consecutive,
        ["Use membership checks to connect values, not their original positions.", "A run starts at value x only when x-1 is absent.",
         "Put values in a set. From each start, advance while the next value exists and keep the largest run length.",
         "Only start a walk at the beginning of a run; starting at every value repeats work and can become quadratic."],
        "Deduplicate into a hash set. Every value without a predecessor begins exactly one consecutive run. Walking forward from these starts visits each unique value once overall, in addition to the initial predecessor checks. Expected time is linear under standard hash-set assumptions. This is different from the original longest increasing contiguous run problem: ordering and adjacency in the supplied array are irrelevant. The independent oracle sorts unique values and scans adjacent differences.",
        "O(n) expected", "O(n)", difficulty=5,
        stress=[([list(range(99999, -1, -1))], 100000)]),
    132: entry("minimum_palindrome_cuts", [("s", "str")], "int", ["strings", "dynamic-programming"],
        ["1–2000 lowercase English letters.", "Partition the complete string into nonempty contiguous palindromes and return the minimum number of cuts, not the number of pieces. A whole-string palindrome needs zero cuts."],
        [(["aab"], "The split aa|b uses one cut; splitting a|a|b would need two."),
         (["racecar"], "The entire string is already a palindrome, so no cut is required.")],
        [[text] for text in ("a", "ab", "aa", "aba", "abba", "abc", "aabb", "abac", "banana", "cdd", "abcbm", "ababbbabbababa")],
        CUTS, [CUTS.replace("((center, center), (center, center + 1))", "((center, center),)"),
               CUTS.replace("return cuts[-1]", "return cuts[-1] + 1")],
        ["Finds only odd-length palindromes and misses even-length choices.", "Returns the number of palindrome pieces instead of the number of cuts."],
        cuts_oracle, random_cuts,
        ["A palindrome ending at a position can extend an optimal partition of the prefix before it.",
         "Maintain minimum cuts for prefixes and discover palindromes by expanding odd and even centers.",
         "Initialize cuts[i]=i-1. For each palindrome s[left:right+1], minimize cuts[right+1] with cuts[left]+1.",
         "The empty prefix has -1 cuts so a palindrome starting at index zero gives zero, not one."],
        "Expand both possible center types and update prefix-cut minima for each discovered palindrome. Processing centers left-to-right ensures the prefix ending before a candidate palindrome has already received all relevant updates: its palindromes have earlier centers. The special empty-prefix cost -1 accounts for the fact that the first piece requires no preceding cut. The method uses O(n) storage and O(n²) comparisons in the worst case. The independent oracle explicitly enumerates all cut masks and checks every resulting piece on small inputs.",
        "O(n²)", "O(n)", difficulty=8,
        stress=[(["a" * 2000], 0), (["a" * 1999 + "b"], 1)]),
    137: entry("single_number_three", [("nums", "list[int]")], "int", ["arrays", "bit-manipulation"],
        ["1–30000 signed 32-bit integers. Exactly one distinct value appears once; every other distinct value appears exactly three times.",
         "Return the singleton using linear time and constant extra space. Negative values must retain their signed meaning."],
        [([[2, 2, 3, 2]], "Three occurrences of 2 cancel under bit counts modulo three, leaving 3."),
         ([[0, 1, 0, 1, 0, 1, 99]], "Zero and one occur three times each; only 99 occurs once.")],
        [[values] for values in ([0], [-1], [2147483647], [-2147483648], [1, 1, 1, -2],
                                 [-1, -1, -1, 2], [0, 0, 0, -2147483648], [-2147483648] * 3 + [0],
                                 [2147483647] * 3 + [-1], [5, 3, 5, 3, 5, 3, 7],
                                 [-2, -3, -2, -3, -2, -3, -4], [0, 2, 0, 2, 0, 2, 1])],
        SINGLE, [XOR, SINGLE.replace("if result >= 1 << 31:", "if False:")],
        ["Uses pair-canceling XOR even though repeated values occur three times.", "Returns an unsigned bit pattern for a negative singleton."], single_oracle, random_single,
        ["For each bit position, repeated values contribute a multiple of three set bits.",
         "Count the low 32 bits independently, reduce each count modulo three, and reconstruct the singleton's bit pattern.",
         "For bit 0 through 31, set that result bit if the count modulo three is nonzero; subtract 2^32 if the sign bit is set.",
         "Python shifts negative integers arithmetically; masking one bit with &1 still extracts the desired low-32-bit pattern."],
        "Sum each bit's occurrences modulo three. Every tripled value contributes zero modulo three, so the remaining bit pattern belongs to the singleton. Convert a pattern with bit 31 set from unsigned to signed by subtracting 2^32. There are always 32 passes, so time is O(n) for this fixed-width domain and auxiliary storage is constant. Unlike Single Number's pairs, triples do not cancel under plain XOR. The independent oracle verifies occurrence multiplicities and selects the unique count-one value.",
        "O(32n), hence O(n) for 32-bit values", "O(1)", difficulty=5,
        stress=[([[value for value in range(9999) for _ in range(3)] + [-2147483648]], -2147483648)]),
    150: entry("evaluate_rpn", [("tokens", "list[str]")], "int", ["stacks", "math"],
        ["1–10000 tokens form one valid postfix expression. Tokens are '+', '-', '*', '/', or integer strings with values from -200 to 200.",
         "Division truncates toward zero, not toward negative infinity. No division has a zero divisor, and all intermediate results and the final answer fit signed 32-bit integers."],
        [([["2", "1", "+", "3", "*"]], "First add 2+1, then multiply the result by 3: (2+1)×3=9."),
         ([["4", "13", "5", "/", "+"]], "13/5 truncates to 2, then 4+2=6.")],
        [[tokens] for tokens in (["0"], ["-200"], ["200"], ["7", "-3", "/"], ["-7", "3", "/"],
                                 ["-7", "-3", "/"], ["1", "2", "-"], ["2", "1", "-"], ["0", "3", "/"],
                                 ["2", "3", "4", "*", "+"], ["4", "2", "/", "3", "-"],
                                 ["5", "1", "2", "+", "4", "*", "+", "3", "-"])],
        RPN, [RPN.replace("value = -quotient if (left < 0) != (right < 0) else quotient", "value = left // right"),
              RPN.replace("right, left = stack.pop(), stack.pop()", "left, right = stack.pop(), stack.pop()")],
        ["Uses floor division, which gives the wrong result for negative nonintegral quotients.",
         "Reverses the left and right operands for subtraction and division."], rpn_oracle, random_rpn,
        ["An operator consumes the two most recent completed operand values.", "Use a stack: push integers, then pop right followed by left for each operator.",
         "Apply left operator right and push the result. For division, divide magnitudes and restore the sign to truncate toward zero.",
         "A negative integer token is not the subtraction operator; distinguish the entire token, not its first character."],
        "Scan the postfix tokens. Each integer becomes a completed operand. Each operator combines the two most recent operand results and replaces them with one result. Pop the right operand first because it was encountered later. Exact magnitude division with a restored sign avoids Python floor-division behavior on negatives. The independent oracle parses the expression recursively from the token sequence's end and uses exact rational truncation for division. The long stress expression has a directly known sum and is handled iteratively by the reference.",
        "O(number of tokens)", "O(number of tokens)", difficulty=5,
        stress=[([["1"] + ["1", "+"] * 4999], 5000)]),
}
BATCH[132]["prerequisites"] = ["strings", "dynamic-programming"]
