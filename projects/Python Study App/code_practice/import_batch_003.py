"""Reviewed number, string, and array exercises with independently computed answers."""
from collections import Counter
from math import comb, isqrt
from textwrap import dedent


def reverse_oracle(args):
    x, = args
    value = int(str(abs(x))[::-1]) * (-1 if x < 0 else 1)
    return value if -(2**31) <= value < 2**31 else 0


def palindrome_oracle(args):
    text = str(args[0])
    return text == text[::-1]


def prefix_oracle(args):
    words, = args
    shortest = min(words, key=len)
    return max((shortest[:i] for i in range(len(shortest) + 1)
                if all(w.startswith(shortest[:i]) for w in words)), key=len)


def last_word_oracle(args):
    return len(args[0].split()[-1])


def plus_oracle(args):
    return [int(c) for c in str(int("".join(map(str, args[0]))) + 1)]


def binary_oracle(args):
    return bin(int(args[0], 2) + int(args[1], 2))[2:]


def sqrt_oracle(args):
    return isqrt(args[0])


def pascal_oracle(args):
    return [[comb(row, col) for col in range(row + 1)] for row in range(args[0])]


def row_oracle(args):
    return [comb(args[0], col) for col in range(args[0] + 1)]


def single_oracle(args):
    return next(value for value, count in Counter(args[0]).items() if count == 1)


def majority_oracle(args):
    return next(value for value, count in Counter(args[0]).items() if count > len(args[0]) // 2)


def ones_oracle(args):
    return bin(args[0]).count("1")


def duplicate_oracle(args):
    ordered = sorted(args[0])
    return any(a == b for a, b in zip(ordered, ordered[1:]))


def power_oracle(args):
    return args[0] in {2**exponent for exponent in range(31)}


def missing_oracle(args):
    return next(iter(set(range(len(args[0]) + 1)) - set(args[0])))


def bits_oracle(args):
    return [bin(value).count("1") for value in range(args[0] + 1)]


def random_signed(rng):
    return [rng.randint(-(2**31), 2**31 - 1)]


def random_palindrome(rng):
    if rng.random() < .5:
        start = str(rng.randint(1, 9999))
        return [int(start + (start[:-1] if rng.random() < .5 else start)[::-1])]
    return random_signed(rng)


def random_words(rng):
    prefix = "".join(rng.choice("abc") for _ in range(rng.randrange(5)))
    return [[prefix + "".join(rng.choice("abc") for _ in range(rng.randrange(8))) for _ in range(rng.randint(1, 8))]]


def random_last(rng):
    words = ["".join(rng.choice("abcXYZ") for _ in range(rng.randint(1, 10))) for _ in range(rng.randint(1, 5))]
    return [" " * rng.randrange(4) + (" " * rng.randint(1, 4)).join(words) + " " * rng.randrange(4)]


def random_digits(rng):
    return [[int(c) for c in str(rng.randint(0, 10**40))]]


def random_binary(rng):
    return [bin(rng.getrandbits(rng.randint(1, 100)))[2:], bin(rng.getrandbits(rng.randint(1, 100)))[2:]]


def random_sqrt(rng):
    if rng.random() < .5:
        base = rng.randrange(46341)
        return [max(0, min(2**31 - 1, base * base + rng.choice([-1, 0, 1])))]
    return [rng.randrange(2**31)]


def random_pascal(rng):
    return [rng.randint(1, 30)]


def random_row(rng):
    return [rng.randrange(34)]


def random_single(rng):
    values = rng.sample(range(-100, 101), rng.randint(1, 30))
    nums = [values[0]] + [v for v in values[1:] for _ in range(2)]
    rng.shuffle(nums)
    return [nums]


def random_majority(rng):
    n = rng.randint(1, 30)
    majority = rng.randint(-100, 100)
    count = rng.randint(n // 2 + 1, n)
    nums = [majority] * count + [majority + rng.randint(1, 20) for _ in range(n - count)]
    rng.shuffle(nums)
    return [nums]


def random_positive(rng):
    return [rng.randint(1, 2**31 - 1)]


def random_array(rng):
    return [[rng.randint(-20, 20) for _ in range(rng.randint(1, 30))]]


def random_power(rng):
    return [rng.choice([1 << rng.randrange(31), rng.randint(-(2**31), 2**31 - 1)])]


def random_missing(rng):
    n = rng.randint(1, 60)
    missing = rng.randrange(n + 1)
    nums = [i for i in range(n + 1) if i != missing]
    rng.shuffle(nums)
    return [nums]


def random_bits(rng):
    return [rng.randrange(501)]


def entry(name, params, returns, topics, constraints, examples, hidden, reference, wrong,
          reasons, oracle, generator, hints, editorial, time, space, difficulty=3, stress=()):
    return dict(name=name, params=[(n, t, "raw") for n, t in params], returns=returns, adapter="raw",
        topics=topics, constraints=constraints, examples=examples, boundaries=hidden,
        reference=dedent(reference), wrong=[dedent(s) for s in wrong], wrong_reasons=reasons,
        oracle=oracle, generator=generator, hints=hints, editorial=editorial,
        time=time, space=space, difficulty=difficulty, stress=list(stress))


REVERSE = '''\
def reverse_integer(x):
    negative = x < 0
    remaining = x if negative else -x
    limit_digit = -8 if negative else -7
    result = 0
    while remaining:
        quotient = remaining // 10
        if remaining % 10:
            quotient += 1
        digit = remaining - quotient * 10
        if result < -214748364 or (result == -214748364 and digit < limit_digit):
            return 0
        result = result * 10 + digit
        remaining = quotient
    return result if negative else -result
'''
PALINDROME = '''\
def palindrome_number(x):
    if x < 0 or (x != 0 and x % 10 == 0):
        return False
    reversed_half = 0
    while x > reversed_half:
        reversed_half = reversed_half * 10 + x % 10
        x //= 10
    return x == reversed_half or x == reversed_half // 10
'''
PREFIX = '''\
def longest_common_prefix(strs):
    first = strs[0]
    for index, char in enumerate(first):
        if any(index >= len(word) or word[index] != char for word in strs[1:]):
            return first[:index]
    return first
'''
LAST = '''\
def length_of_last_word(s):
    right = len(s) - 1
    while s[right] == " ":
        right -= 1
    end = right
    while right >= 0 and s[right] != " ":
        right -= 1
    return end - right
'''
PLUS = '''\
def plus_one(digits):
    answer = digits.copy()
    for i in range(len(answer) - 1, -1, -1):
        if answer[i] < 9:
            answer[i] += 1
            return answer
        answer[i] = 0
    return [1] + answer
'''
BINARY = '''\
def add_binary(a, b):
    i, j, carry = len(a) - 1, len(b) - 1, 0
    out = []
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += int(a[i])
        if j >= 0:
            total += int(b[j])
        carry, bit = divmod(total, 2)
        out.append(str(bit))
        i -= 1
        j -= 1
    return "".join(reversed(out))
'''
SQRT = '''\
def integer_sqrt(x):
    left, right, answer = 0, x, 0
    while left <= right:
        middle = (left + right) // 2
        if middle == 0 or middle <= x // middle:
            answer = middle
            left = middle + 1
        else:
            right = middle - 1
    return answer
'''
PASCAL = '''\
def pascal_triangle(num_rows):
    answer = []
    for row in range(num_rows):
        current = [1] * (row + 1)
        for col in range(1, row):
            current[col] = answer[-1][col-1] + answer[-1][col]
        answer.append(current)
    return answer
'''
ROW = '''\
def pascal_row(row_index):
    row = [1]
    for size in range(1, row_index + 1):
        row.append(1)
        for col in range(size - 1, 0, -1):
            row[col] += row[col - 1]
    return row
'''
SINGLE = '''\
def single_number(nums):
    result = 0
    for value in nums:
        result ^= value
    return result
'''
MAJORITY = '''\
def majority_element(nums):
    candidate, votes = None, 0
    for value in nums:
        if votes == 0:
            candidate = value
        votes += 1 if value == candidate else -1
    return candidate
'''
ONES = '''\
def number_of_one_bits(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
'''
DUPLICATE = '''\
def contains_duplicate(nums):
    seen = set()
    for value in nums:
        if value in seen:
            return True
        seen.add(value)
    return False
'''
POWER = '''\
def power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0
'''
MISSING = '''\
def missing_number(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)
'''
BITS = '''\
def counting_bits(n):
    answer = [0] * (n + 1)
    for value in range(1, n + 1):
        answer[value] = answer[value >> 1] + (value & 1)
    return answer
'''

BATCH = {
    7: entry("reverse_integer", [("x","int")], "int", ["math"], ["-2^31 <= x <= 2^31 - 1.", "Return zero on reversed-value overflow. Keep intermediate arithmetic within signed 32-bit bounds."],
        [([123],"Reading the digits of 123 backward gives 321."), ([-123],"Reverse the magnitude and preserve the minus sign, giving -321.")],
        [[x] for x in (0,1,-1,10,-10,100,-100,1200,1534236469,-2147483648,1463847412,1563847412)],
        REVERSE, [REVERSE.replace("return result if negative else -result", "return result"), REVERSE.replace("if result < -214748364 or (result == -214748364 and digit < limit_digit):", "if False:")],
        ["Returns a negative result for positive inputs.", "Omits the overflow check before appending a digit."], reverse_oracle, random_signed,
        ["Appending one reversed digit multiplies the accumulated answer by ten.", "Check whether the next multiplication/addition would overflow before performing it.", "Extract the last digit, check the boundary, append it to the reversed accumulator, and remove it from the input.", "A negative accumulator can represent the full signed range, including -2^31."],
        "Keep both the unprocessed input and accumulated result nonpositive so the asymmetric minimum signed integer is representable. Extract a negative digit with division truncated toward zero. Before multiplying the result by ten, compare against -214748364 and the final permitted digit (-8 or -7). Return zero if that step would overflow. Negate only the final result of an originally positive input.", "O(log |x|)", "O(1)", difficulty=5),
    9: entry("palindrome_number", [("x","int")], "bool", ["math", "two-pointers"], ["-2^31 <= x <= 2^31 - 1.", "Negative integers are not palindromes because the minus sign is not mirrored."],
        [([121],"The decimal digits read 121 in both directions."), ([-121],"The minus sign is only at the beginning, so a negative number is not a palindrome.")],
        [[x] for x in (0,1,10,11,12,100,101,1001,10001,1221,12321,2147483647)],
        PALINDROME, [PALINDROME.replace("if x < 0 or (x != 0 and x % 10 == 0):", "if x < 0:"), PALINDROME.replace(" or x == reversed_half // 10", "")],
        ["Accepts numbers with a trailing zero after discarding that zero.", "Fails odd-length palindromes by not ignoring the middle digit."], palindrome_oracle, random_palindrome,
        ["Negative values and nonzero trailing-zero values can be rejected immediately.", "Reverse only the last half of the digits and compare it with the first half.", "Move last digits into a reversed half until it meets the remaining first half; compare, ignoring one middle digit for odd length.", "Reversing only half the number also avoids whole-number reversal overflow."],
        "Reject negatives and positive numbers ending in zero. Repeatedly move the final digit into a reversed accumulator until the remaining prefix is no larger than that accumulator. For even length, the halves must match exactly. For odd length, discard the accumulator's middle digit before comparing. Zero is a palindrome.", "O(log |x|)", "O(1)"),
    14: entry("longest_common_prefix", [("strs","list[str]")], "str", ["strings"], ["1–200 strings, each with 0–200 lowercase English letters.", "A prefix must start at position zero in every string."],
        [([["flower","flow","flight"]],"All three words begin with fl; the next letters differ."), ([["dog","racecar","car"]],"The first letters differ, so no nonempty prefix is shared.")],
        [[[""]], [["a"]], [["a","a"]], [["a",""]], [["","a"]], [["abc","ab"]], [["ab","abc"]], [["abc","ax"]], [["same","same","same"]], [["aa","aaa","a"]], [["prefix","preform","prevent"]], [["a","b"]]],
        PREFIX, [PREFIX.replace("return first[:index]", "return first[:index+1]"), PREFIX.replace("strs[1:]", "strs[1:2]")],
        ["Includes the first mismatching character.", "Checks only the first two strings."], prefix_oracle, random_words,
        ["The answer cannot be longer than the shortest string.", "Compare one character position across every word before advancing.", "At the first missing or unequal character, return the earlier prefix; otherwise return the whole first word.", "An empty string makes the common prefix empty."],
        "Scan the first word from left to right. At each index, ensure every other word has that index and the same character. Stop immediately when either condition fails. All earlier indices are known to match, so the prefix before that index is maximal. If the first word ends without failure, it is the common prefix.", "O(total characters)", "O(1) excluding output"),
    58: entry("length_of_last_word", [("s","str")], "int", ["strings"], ["1 <= len(s) <= 10,000.", "s contains English letters and spaces, with at least one word."],
        [(["Hello World"],"The final word is World, which has five letters."), (["   fly me   to   the moon  "],"Ignore trailing spaces; moon is the final word and has length four.")],
        [[s] for s in ("a","a "," a"," abc ","a b","a bb ","abc defg","Z","abc","  abc  d  ","one two three","abcd     ")],
        LAST, [LAST.replace("while s[right] == \" \":", "while False:"), LAST.replace("return end - right", "return end - right + 1")],
        ["Counts trailing spaces as part of the final word.", "Adds one after the boundary difference already gives the length."], last_word_oracle, random_last,
        ["Trailing spaces do not belong to any word.", "Scan backward past trailing spaces, then count letters until the next space or the start.", "Remember the last non-space index, move left over its word, and subtract the boundary indices.", "The source guarantees a word exists, so the trailing-space scan will reach a letter."],
        "Move a pointer left from the end until it reaches a non-space character. Save that endpoint, then continue left while characters are not spaces. The difference between the endpoint and the stopping index is the final word's length. This avoids splitting the entire string into a new list.", "O(n)", "O(1)"),
    66: entry("plus_one", [("digits","list[int]")], "list[int]", ["arrays", "math"], ["The array contains 1–100 decimal digits, most significant first.", "No leading zero occurs except for the number zero."],
        [([[1,2,3]],"123 + 1 = 124; only the final digit changes."), ([[9,9]],"99 + 1 = 100, so carrying creates an additional leading digit.")],
        [[[0]], [[1]], [[8]], [[9]], [[1,0]], [[1,9]], [[9,0]], [[9,8]], [[1,9,9]], [[9,0,9]], [[9,9,9]], [[9]*100]],
        PLUS, [PLUS.replace("return [1] + answer", "return answer"), PLUS.replace("answer[i] = 0", "answer[i] = 9")],
        ["Drops the new leading digit after every original digit carries.", "Leaves a carried-from nine unchanged."], plus_oracle, random_digits,
        ["Incrementing may propagate a carry left through several nines.", "Work from the least significant digit toward the front.", "If a digit is below nine, increment and return. Otherwise set it to zero and continue. If all carry, prepend one.", "Only an all-nine input needs a longer output."],
        "Scan from right to left. A digit below nine absorbs the increment and ends the work. A nine becomes zero and propagates the increment to its left neighbor. If every digit was nine, the result is a leading one followed by those zeros. The reference copies the input so the returned digits do not alter it.", "O(n)", "O(n) including output"),
    67: entry("add_binary", [("a","str"),("b","str")], "str", ["strings", "math"], ["Each input has 1–10,000 binary digits.", "There are no leading zeros except for the string 0."],
        [(["11","1"],"Binary 11 is three and 1 is one. Their sum four is binary 100."), (["1010","1011"],"Ten plus eleven is twenty-one, represented by 10101.")],
        [["0","0"],["0","1"],["1","0"],["1","1"],["10","1"],["1","10"],["10","10"],["111","1"],["101","10"],["1000","0"],["111","111"],["1"*100,"1"]],
        BINARY, [BINARY.replace(" or carry:", ":"), BINARY.replace("total = carry", "total = 0")],
        ["Discards a final carry after both input strings end.", "Does not carry from one binary position into the next."], binary_oracle, random_binary,
        ["Binary column addition has a carry just like decimal addition.", "Read both strings from the right, treating a missing digit as zero.", "Add the two bits and carry, append sum modulo two, and carry sum divided by two. Continue while any input or carry remains.", "Reverse the collected least-significant-first output bits at the end."],
        "Maintain one pointer per string and a carry. At each bit position, add present digits to the carry, append the remainder modulo two, and retain the quotient for the next position. The loop must include the final carry after both inputs finish. Reversing the accumulated bits produces the usual most-significant-first result.", "O(n + m)", "O(n + m) including output"),
    69: entry("integer_sqrt", [("x","int")], "int", ["binary-search", "math"], ["0 <= x <= 2^31 - 1.", "Return the nonnegative floor of the square root without exponent or square-root functions in your solution."],
        [([4],"2 squared equals 4, so the integer square root is exactly 2."), ([8],"2 squared is at most 8 but 3 squared exceeds it, so round down to 2.")],
        [[x] for x in (0,1,2,3,9,10,15,16,17,2147395599,2147395600,2147483647)],
        SQRT, [SQRT.replace("return answer", "return left"), SQRT.replace("middle <= x // middle", "middle < x // middle")],
        ["Returns the first infeasible integer instead of the largest feasible one.", "Treats exact perfect squares as too large."], sqrt_oracle, random_sqrt,
        ["The predicate candidate squared <= x changes from true to false once.", "Binary-search for the largest feasible candidate, saving it before moving right.", "If middle is feasible, record it and raise the lower bound; otherwise lower the upper bound.", "Comparing middle <= x // middle avoids multiplication overflow; handle middle zero separately."],
        "Search a nonnegative interval for the last value whose square does not exceed x. When a midpoint is feasible, remember it and search higher values. Otherwise search below it. At termination the saved candidate is the floor square root. Integer division provides the comparison without floating-point rounding or exponent operations.", "O(log(x + 1))", "O(1)"),
    118: entry("pascal_triangle", [("num_rows","int")], "list[list[int]]", ["arrays", "dynamic-programming"], ["1 <= num_rows <= 30.", "The first row is [1]; every interior value is the sum of the two above it."],
        [([5],"The five rows end in [1,4,6,4,1], with 6 obtained from 3+3 in the previous row."), ([1],"One row contains only [1].")],
        [[i] for i in (2,3,4,6,7,8,9,10,12,15,20,30)],
        PASCAL, [PASCAL.replace("range(num_rows)", "range(num_rows - 1)"), PASCAL.replace(" + answer[-1][col]", "")],
        ["Generates one fewer row than requested.", "Copies only one parent instead of adding both."], pascal_oracle, random_pascal,
        ["Every row begins and ends with one.", "Create the next row from the preceding row's neighboring pairs.", "Initialize a row of ones, fill interior index j from previous[j-1]+previous[j], then append it.", "Each row must be a separate list so later updates do not change earlier rows."],
        "Build rows in order. Leave the first and last entries as one, and fill interior entries with sums from adjacent positions of the preceding row. The independent oracle uses binomial coefficients instead of this recurrence. There are a quadratic number of returned entries, so quadratic time and output space are necessary.", "O(r²)", "O(r²) including output"),
    119: entry("pascal_row", [("row_index","int")], "list[int]", ["arrays", "dynamic-programming"], ["0 <= row_index <= 33.", "Rows are zero-indexed, so row zero is [1]."],
        [([3],"The fourth row, at index three, is [1,3,3,1]."), ([0],"The first row is [1].")],
        [[i] for i in (1,2,4,5,6,7,8,9,10,16,25,33)],
        ROW, [ROW.replace("range(size - 1, 0, -1)", "range(1, size)"), ROW.replace("range(1, row_index + 1)", "range(1, row_index)")],
        ["Updates left to right and reuses overwritten values from the current row.", "Stops at the previous row."], row_oracle, random_row,
        ["Only the preceding row is needed, so a single array can be reused.", "Update interior values from right to left to retain both old parents until they are used.", "Append one for the new boundary, then add row[j-1] into row[j] for descending interior indices.", "Row index zero needs no updates."],
        "Start with [1]. Each iteration extends the array with a final one and updates the interior in descending index order. This order preserves each previous-row value until its last use, unlike a left-to-right update. The final array has row_index+1 entries and uses linear extra space; the reference recurrence takes quadratic time.", "O(r²)", "O(r) including output"),
    136: entry("single_number", [("nums","list[int]")], "int", ["arrays", "bit-manipulation"], ["1 <= len(nums) <= 30,000.", "-30,000 <= nums[i] <= 30,000.", "Exactly one value occurs once; every other distinct value occurs exactly twice."],
        [([[2,2,1]],"The two 2 values cancel as a pair, leaving the singleton 1."), ([[4,1,2,1,2]],"Both 1 and 2 appear twice; only 4 appears once.")],
        [[[0]], [[1]], [[-1]], [[1,1,2]], [[0,0,3]], [[-2,1,-2]], [[3,2,3]], [[5,1,5,2,2]], [[7,7,0]], [[-3,-3,-2]], [[30000,-30000,30000]], [[1,2,3,2,1]]],
        SINGLE, [SINGLE.replace("result ^= value", "result |= value"), SINGLE.replace("for value in nums:", "for value in nums[:-1]:")],
        ["Uses bitwise OR, which does not cancel paired values.", "Skips the final element, leaving an uncanceled value."], single_oracle, random_single,
        ["A value XOR itself is zero, and zero XOR a value preserves it.", "XOR every input value into one accumulator.", "Initialize zero, XOR each value, then return the accumulator.", "Commutativity means duplicate pairs cancel even when separated."],
        "XOR is associative and commutative. Therefore the whole-array XOR can be regrouped into duplicate pairs, each contributing zero, and the single remaining value. Accumulate that XOR in one variable. Unlike a frequency dictionary, this needs constant extra space under the fixed integer bounds.", "O(n)", "O(1)"),
    169: entry("majority_element", [("nums","list[int]")], "int", ["arrays", "counting"], ["1 <= len(nums) <= 50,000.", "-10^9 <= nums[i] <= 10^9.", "A value occurring strictly more than half the time is guaranteed to exist."],
        [([[3,2,3]],"3 occurs twice among three positions, exceeding half."), ([[2,2,1,1,1,2,2]],"2 occurs four times among seven positions, so it is the majority.")],
        [[[1]], [[-1]], [[1,1]], [[1,2,2]], [[2,1,2]], [[2,2,1]], [[0,0,1]], [[-3,2,-3]], [[5,5,5,1]], [[1,2,3,3,3]], [[9,9,2,2,9]], [[1000000000,-1000000000,1000000000]]],
        MAJORITY, [MAJORITY.replace("else -1", "else 1"), "def majority_element(nums):\n    return max(nums)\n"],
        ["Never cancels opposing votes, so the first candidate can never be replaced.", "Confuses the largest value with the most frequent value."], majority_oracle, random_majority,
        ["Removing two different values cannot eliminate an existing strict majority.", "Maintain a candidate and a vote balance, resetting the candidate when the balance reaches zero.", "Equal values add a vote; different values subtract one. Replace an exhausted candidate on the next element.", "Because a majority is guaranteed, the final surviving candidate needs no additional existence check."],
        "Boyer–Moore voting pairs each occurrence of a candidate with an opposing value whenever possible. A strict majority cannot be canceled entirely by all other values, so it is the final surviving candidate. Track only the candidate and its balance. If the existence guarantee were removed, a second pass would be required to verify the candidate.", "O(n)", "O(1)"),
    191: entry("number_of_one_bits", [("n","int")], "int", ["bit-manipulation"], ["1 <= n <= 2^31 - 1."],
        [([11],"11 is binary 1011, with three set bits."), ([128],"128 is binary 10000000, with one set bit.")],
        [[n] for n in (1,2,3,4,7,8,15,16,31,32,1023,2147483647)],
        ONES, [ONES.replace("n &= n - 1", "n >>= 1"), ONES.replace("count = 0", "count = 1")],
        ["Counts bit positions rather than set bits.", "Starts counting at one and overcounts every input."], ones_oracle, random_positive,
        ["Subtracting one changes the lowest set bit and the zeros below it.", "AND n with n-1 to clear exactly its lowest set bit.", "Repeat that clearing operation until n is zero, counting each iteration.", "The number of iterations equals the number of set bits."],
        "The operation n & (n-1) clears one set bit without affecting the higher set bits. Count how many times it can be applied before the value becomes zero. This visits only set bits; the independent oracle counts ones in the binary string representation.", "O(number of set bits)", "O(1)"),
    217: entry("contains_duplicate", [("nums","list[int]")], "bool", ["arrays", "hash-maps"], ["1 <= len(nums) <= 100,000.", "-10^9 <= nums[i] <= 10^9."],
        [([[1,2,3,1]],"The value 1 occurs twice even though its occurrences are separated."), ([[1,2,3,4]],"All four values are distinct.")],
        [[[1]], [[0]], [[1,1]], [[1,2]], [[2,1]], [[0,0]], [[-1,2,-1]], [[3,2,1,3]], [[1,1,1]], [[-3,-2,-1]], [[1000000000,-1000000000]], [[5,4,3,2,1,5]]],
        DUPLICATE, ["def contains_duplicate(nums):\n    return any(a == b for a,b in zip(nums, nums[1:]))\n", DUPLICATE.replace("for value in nums:", "for value in nums[:-1]:")],
        ["Checks only adjacent elements without sorting, missing separated duplicates.", "Does not check whether the final value repeats."], duplicate_oracle, random_array,
        ["A value is a duplicate when it has been seen at any earlier position.", "Keep a set of earlier values and test membership before inserting the current one.", "Return true when a value is already present; if the scan finishes, return false.", "The independent oracle sorts and compares adjacent values instead of using a set."],
        "Scan once while storing earlier values in a hash set. Encountering an existing member proves a repetition immediately, regardless of the distance between occurrences. If no membership check succeeds, every value was unique. Expected running time and worst-case set space are linear.", "O(n) expected", "O(n)"),
    231: entry("power_of_two", [("n","int")], "bool", ["bit-manipulation", "math"], ["-2^31 <= n <= 2^31 - 1.", "The exponent is a nonnegative integer; 1 equals 2^0."],
        [([1],"1 equals 2 to the zeroth power, so it qualifies."), ([3],"3 lies between consecutive powers 2 and 4 and is not a power of two.")],
        [[n] for n in (0,-1,-2,2,4,5,6,8,16,1024,1073741824,2147483647)],
        POWER, [POWER.replace("n > 0 and ", ""), "def power_of_two(n):\n    return n == 1 or (n > 0 and n % 2 == 0)\n"],
        ["Accepts zero because zero also satisfies the bit-clearing equation.", "Assumes every positive even number is a power of two."], power_oracle, random_power,
        ["A positive power of two has exactly one set bit.", "Clearing the lowest set bit should leave zero, but positivity must be checked separately.", "Return n>0 and n&(n-1)==0.", "Zero is not a power of two even though its bit-clearing result is zero."],
        "For a positive integer, n & (n-1) clears its lowest one bit. The result is zero exactly when that was the only one bit, which characterizes powers of two. The positivity condition excludes zero and negatives. The independent oracle compares against the complete finite set of powers allowed by the 32-bit input range.", "O(1) for 32-bit inputs", "O(1)"),
    268: entry("missing_number", [("nums","list[int]")], "int", ["arrays", "math"], ["1 <= len(nums) <= 10,000.", "There are n distinct values from 0 through n, with exactly one of the n+1 possibilities missing."],
        [([[3,0,1]],"Among 0,1,2,3, only 2 is absent."), ([[0,1]],"For length two the full range is 0,1,2, so the missing value is 2.")],
        [[[0]], [[1]], [[0,2]], [[1,2]], [[0,1,2]], [[1,2,3]], [[0,2,3]], [[2,1,0]], [[4,0,2,1]], [[4,3,2,1]], [[0,1,2,3,4]], [[5,0,1,3,4]]],
        MISSING, [MISSING.replace("n * (n + 1)", "n * (n - 1)"), MISSING.replace("- sum(nums)", "- sum(nums[:-1])")],
        ["Uses the sum through n-1 instead of including n.", "Fails to subtract the final input value."], missing_oracle, random_missing,
        ["The complete range has a known sum.", "Subtract the actual array sum from the sum of 0 through n.", "Compute n*(n+1)//2 - sum(nums).", "The absent value can be zero or n, so both endpoints belong to the range."],
        "Because all input values are distinct and exactly one is absent, subtracting their sum from n(n+1)/2 cancels every present value and leaves the missing one. The sum formula must include n, not stop at n-1. The independent oracle constructs the full range as a set and takes the set difference.", "O(n)", "O(1)"),
    338: entry("counting_bits", [("n","int")], "list[int]", ["bit-manipulation", "dynamic-programming"], ["0 <= n <= 100,000.", "Return counts for every integer from zero through n inclusive without calling a built-in bit-count function."],
        [([2],"Binary representations 0,1,10 contain 0,1,1 set bits."), ([5],"Counts for 0 through 5 are [0,1,1,2,1,2].")],
        [[n] for n in (0,1,3,4,6,7,8,9,15,16,31,1000)],
        BITS, [BITS.replace("range(1, n + 1)", "range(1, n)"), BITS.replace("(value & 1)", "1")],
        ["Leaves the requested final integer's count uncomputed.", "Adds one for every last bit, including zero bits."], bits_oracle, random_bits,
        ["Removing the last binary digit produces a smaller integer whose count is already known.", "Reuse the count for value//2 and add the last bit.", "Set answer[0]=0, then answer[i]=answer[i>>1]+(i&1) for i from 1 through n.", "Each result requires constant work after its smaller predecessor is available."],
        "Right-shifting an integer removes its last bit. Therefore its set-bit count is the earlier count for half the value plus either zero or one for that removed bit. Fill the array in increasing order so the earlier count is always ready. Include both endpoints zero and n. Time is linear in the output length.", "O(n)", "O(n) including output"),
}
