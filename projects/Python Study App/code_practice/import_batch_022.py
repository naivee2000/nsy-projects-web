"""Nearby pairs, expression evaluation, ranges, voting, and matrix elimination."""
from collections import Counter
from math import prod

from .import_batch_003 import entry


def nearby_oracle(args):
    nums, limit = args
    return any(nums[i] == nums[j] for i in range(len(nums))
               for j in range(i + 1, min(len(nums), i + limit + 1)))


def almost_oracle(args):
    nums, index_limit, value_limit = args
    return any(abs(nums[i] - nums[j]) <= value_limit for i in range(len(nums))
               for j in range(i + 1, min(len(nums), i + index_limit + 1)))


def calculator_oracle(args):
    text = args[0]

    def parse(index):
        total, sign = 0, 1
        while index < len(text):
            char = text[index]
            if char == " ":
                index += 1
            elif char == "+":
                sign, index = 1, index + 1
            elif char == "-":
                sign, index = -1, index + 1
            elif char == "(":
                value, index = parse(index + 1)
                total += sign * value
                sign = 1
            elif char == ")":
                return total, index + 1
            else:
                end = index
                while end < len(text) and text[end].isdigit():
                    end += 1
                total += sign * int(text[index:end])
                sign, index = 1, end
        return total, index

    return parse(0)[0]


def calculator_two_oracle(args):
    text = args[0].replace(" ", "")
    numbers, operators, index = [], [], 0
    while index < len(text):
        end = index
        while end < len(text) and text[end].isdigit():
            end += 1
        numbers.append(int(text[index:end]))
        if end < len(text):
            operators.append(text[end])
        index = end + 1
    position = 0
    while position < len(operators):
        operator = operators[position]
        if operator not in "*/":
            position += 1
            continue
        left, right = numbers[position], numbers[position + 1]
        if operator == "*":
            value = left * right
        else:
            value = abs(left) // right * (-1 if left < 0 else 1)
        numbers[position:position + 2] = [value]
        operators.pop(position)
    result = numbers[0]
    for operator, number in zip(operators, numbers[1:]):
        result = result + number if operator == "+" else result - number
    return result


def ranges_oracle(args):
    nums = args[0]
    answer, start = [], 0
    while start < len(nums):
        stop = start
        while stop + 1 < len(nums) and nums[stop + 1] - nums[stop] == 1:
            stop += 1
        answer.append(str(nums[start]) if start == stop else f"{nums[start]}->{nums[stop]}")
        start = stop + 1
    return answer


def thirds_oracle(args):
    nums = args[0]
    threshold = len(nums) // 3
    return [value for value, count in Counter(nums).items() if count > threshold]


def digit_one_oracle(args):
    return sum(str(value).count("1") for value in range(args[0] + 1))


def product_oracle(args):
    nums = args[0]
    return [prod(nums[:index] + nums[index + 1:]) for index in range(len(nums))]


def matrix_oracle(args):
    matrix, target = args
    return any(value == target for row in matrix for value in row)


def parentheses_oracle(args):
    expression = args[0]
    numbers, operators, index = [], [], 0
    while index < len(expression):
        end = index
        while end < len(expression) and expression[end].isdigit():
            end += 1
        numbers.append(int(expression[index:end]))
        if end < len(expression):
            operators.append(expression[end])
        index = end + 1
    table = {(i, i): [value] for i, value in enumerate(numbers)}
    for width in range(2, len(numbers) + 1):
        for left in range(len(numbers) - width + 1):
            right, values = left + width - 1, []
            for split in range(left, right):
                for a in table[left, split]:
                    for b in table[split + 1, right]:
                        values.append(a + b if operators[split] == "+" else
                                      a - b if operators[split] == "-" else a * b)
            table[left, right] = values
    return table[0, len(numbers) - 1]


def random_nearby(rng):
    return [[rng.randint(-6, 6) for _ in range(rng.randint(1, 30))], rng.randint(0, 30)]


def random_almost(rng):
    nums = [rng.randint(-30, 30) for _ in range(rng.randint(2, 30))]
    return [nums, rng.randint(1, len(nums)), rng.randint(0, 10)]


def random_calculator(rng):
    def build(depth):
        if depth >= 3 or rng.random() < .35:
            return str(rng.randint(0, 30))
        parts = [build(depth + 1)]
        for _ in range(rng.randint(1, 3)):
            parts.extend((rng.choice(("+", "-")), build(depth + 1)))
        return "(" + " ".join(parts) + ")"
    result = build(0)
    return [("-" if rng.random() < .2 else "") + result]


def random_calculator_two(rng):
    pieces = [str(rng.randint(0, 20))]
    for _ in range(rng.randint(0, 7)):
        operator = rng.choice("+-*/")
        pieces.extend((operator, str(rng.randint(1 if operator == "/" else 0, 20))))
    return [" ".join(pieces)]


def random_ranges(rng):
    return [sorted(rng.sample(range(-60, 61), rng.randint(0, 20)))]


def random_thirds(rng):
    return [[rng.randint(-5, 5) for _ in range(rng.randint(1, 30))]]


def random_digit_one(rng):
    return [rng.randint(0, 10000)]


def random_product(rng):
    return [[rng.randint(-3, 3) for _ in range(rng.randint(2, 10))]]


def random_matrix(rng):
    rows, columns = rng.randint(1, 8), rng.randint(1, 8)
    row_values, column_values = [rng.randint(-20, 0)], [rng.randint(-20, 0)]
    for _ in range(1, rows):
        row_values.append(row_values[-1] + rng.randint(0, 4))
    for _ in range(1, columns):
        column_values.append(column_values[-1] + rng.randint(0, 4))
    matrix = [[row_values[row] + column_values[column] for column in range(columns)]
              for row in range(rows)]
    target = rng.choice(rng.choice(matrix)) if rng.random() < .5 else rng.randint(-45, 20)
    return [matrix, target]


def random_parentheses(rng):
    pieces = [str(rng.randint(0, 20))]
    for _ in range(rng.randint(0, 5)):
        pieces.extend((rng.choice("+-*"), str(rng.randint(0, 20))))
    return ["".join(pieces)]


NEARBY = '''\
def contains_nearby_duplicate(nums, k):
    latest = {}
    for index, value in enumerate(nums):
        if value in latest and index - latest[value] <= k:
            return True
        latest[value] = index
    return False
'''
ALMOST = '''\
def contains_nearby_almost_duplicate(nums, index_diff, value_diff):
    width = value_diff + 1
    buckets = {}
    for index, value in enumerate(nums):
        bucket = value // width
        if bucket in buckets:
            return True
        if bucket - 1 in buckets and value - buckets[bucket - 1] <= value_diff:
            return True
        if bucket + 1 in buckets and buckets[bucket + 1] - value <= value_diff:
            return True
        buckets[bucket] = value
        if index >= index_diff:
            old = nums[index - index_diff]
            del buckets[old // width]
    return False
'''
CALCULATOR = '''\
def basic_calculator(s):
    total = number = 0
    sign = 1
    stack = []
    for char in s:
        if char.isdigit():
            number = number * 10 + int(char)
        elif char in "+-":
            total += sign * number
            number = 0
            sign = 1 if char == "+" else -1
        elif char == "(":
            stack.extend((total, sign))
            total, sign = 0, 1
        elif char == ")":
            total += sign * number
            number = 0
            total = stack.pop() * total + stack.pop()
    return total + sign * number
'''
CALCULATOR_TWO = '''\
def basic_calculator_two(s):
    total = current = number = 0
    operator = "+"
    for index, char in enumerate(s):
        if char.isdigit():
            number = number * 10 + int(char)
        if char in "+-*/" or index == len(s) - 1:
            if operator == "+":
                total += current
                current = number
            elif operator == "-":
                total += current
                current = -number
            elif operator == "*":
                current *= number
            else:
                current = abs(current) // number * (-1 if current < 0 else 1)
            operator, number = char, 0
    return total + current
'''
RANGES = '''\
def summary_ranges(nums):
    result = []
    start = 0
    while start < len(nums):
        stop = start
        while stop + 1 < len(nums) and nums[stop + 1] == nums[stop] + 1:
            stop += 1
        if start == stop:
            result.append(str(nums[start]))
        else:
            result.append(str(nums[start]) + "->" + str(nums[stop]))
        start = stop + 1
    return result
'''
THIRDS = '''\
def majority_over_third(nums):
    first = second = None
    first_count = second_count = 0
    for value in nums:
        if value == first:
            first_count += 1
        elif value == second:
            second_count += 1
        elif first_count == 0:
            first, first_count = value, 1
        elif second_count == 0:
            second, second_count = value, 1
        else:
            first_count -= 1
            second_count -= 1
    return [candidate for candidate in (first, second)
            if candidate is not None and nums.count(candidate) > len(nums) // 3]
'''
DIGIT_ONE = '''\
def count_digit_one(n):
    total, place = 0, 1
    while place <= n:
        lower = n % place
        digit = (n // place) % 10
        higher = n // (place * 10)
        if digit == 0:
            total += higher * place
        elif digit == 1:
            total += higher * place + lower + 1
        else:
            total += (higher + 1) * place
        place *= 10
    return total
'''
PRODUCT = '''\
def product_except_self(nums):
    answer = [1] * len(nums)
    prefix = 1
    for index, value in enumerate(nums):
        answer[index] = prefix
        prefix *= value
    suffix = 1
    for index in range(len(nums) - 1, -1, -1):
        answer[index] *= suffix
        suffix *= nums[index]
    return answer
'''
MATRIX = '''\
def search_sorted_matrix(matrix, target):
    row, column = 0, len(matrix[0]) - 1
    while row < len(matrix) and column >= 0:
        value = matrix[row][column]
        if value == target:
            return True
        if value > target:
            column -= 1
        else:
            row += 1
    return False
'''
PARENTHESES = '''\
def all_parenthesized_results(expression):
    from functools import cache
    @cache
    def solve(text):
        results = []
        for index, operator in enumerate(text):
            if operator not in "+-*":
                continue
            for left in solve(text[:index]):
                for right in solve(text[index + 1:]):
                    results.append(left + right if operator == "+" else
                                   left - right if operator == "-" else left * right)
        return results or [int(text)]
    return solve(expression)
'''


BATCH = {
    219: entry("contains_nearby_duplicate", [("nums", "list[int]"), ("k", "int")], "bool", ["arrays", "hash-maps", "sliding-window"],
        ["nums contains 1–100000 integers from -10^9 to 10^9; 0 ≤ k ≤ 100000.", "Return True only when two DISTINCT indices hold equal values and their distance is at most k. A zero distance limit can never qualify."],
        [([[1, 2, 3, 1], 3], "The equal 1 values are at indices 0 and 3, exactly the allowed distance, so return True."), ([[1, 2, 3, 1, 2, 3], 2], "Each repeated value is three positions apart, outside the distance limit, so return False.")],
        [[nums, k] for nums, k in (([1], 0), ([1, 1], 0), ([1, 1], 1), ([1, 2, 1], 1), ([1, 2, 1], 2), ([1, 0, 1, 1], 1), ([0, 1, 2, 0], 2), ([0, 1, 2, 0], 3), ([-1, 2, -1], 2), ([1, 2, 3, 4], 4), ([1, 2, 1, 1], 1), ([5, 5, 5], 1))],
        NEARBY, [NEARBY.replace("<= k", "< k"), 'def contains_nearby_duplicate(nums, k):\n    return len(nums) != len(set(nums))\n'],
        ["Treats the inclusive distance limit as strict and misses pairs exactly k positions apart.", "Detects duplicates anywhere in the array even when all equal values are farther apart than k."], nearby_oracle, random_nearby,
        ["Only the most recent position of each value can be closest to the current index.", "Scan left to right and store each value's latest index.", "Before updating a value's index, compare the current index with its saved index and accept when the gap is at most k.", "A global set is insufficient because the qualifying pair must also lie inside the index window."],
        "For a current value, any earlier occurrence before its latest occurrence is even farther away, so retaining only the latest index loses no possible match. The independent oracle examines every pair whose index distance is within k. Each array position is processed once.", "O(n)", "O(min(n, distinct values))", difficulty=3,
        stress=[([list(range(99999)) + [0], 99999], True), ([list(range(100000)), 99999], False)]),
    220: entry("contains_nearby_almost_duplicate", [("nums", "list[int]"), ("index_diff", "int"), ("value_diff", "int")], "bool", ["arrays", "hash-maps", "bucket-sort", "sliding-window"],
        ["nums contains 2–100000 integers from -10^9 to 10^9; 1 ≤ index_diff ≤ len(nums); 0 ≤ value_diff ≤ 10^9.", "Find distinct indices at distance at most index_diff whose VALUES differ by at most value_diff. Both inequalities are inclusive, including for negative values."],
        [([[1, 2, 3, 1], 3, 0], "Indices 0 and 3 meet the exact index boundary, and their equal values have difference zero."), ([[1, 5, 9, 1, 5, 9], 2, 3], "Every nearby pair differs by at least 4, while equal values are three indices apart, so no pair meets both limits." )],
        [[nums, i, v] for nums, i, v in (([1, 2], 1, 1), ([1, 3], 1, 1), ([-3, -2], 1, 1), ([-1, 1], 1, 2), ([0, 10, 0], 2, 0), ([0, 10, 0], 1, 0), ([1, 4, 7], 1, 3), ([1, 4, 7], 1, 2), ([5, 5], 1, 0), ([-10, -5, 0], 2, 5), ([1000000000, 0, -1000000000], 2, 1000000000), ([1, 100, 2], 1, 1))],
        ALMOST, [ALMOST.replace("        if bucket - 1 in buckets and value - buckets[bucket - 1] <= value_diff:\n            return True\n        if bucket + 1 in buckets and buckets[bucket + 1] - value <= value_diff:\n            return True\n", ""), '''\
def contains_nearby_almost_duplicate(nums, index_diff, value_diff):
    width = value_diff + 1
    buckets = {}
    for index, value in enumerate(nums):
        if index >= index_diff:
            old = nums[index - index_diff]
            del buckets[old // width]
        bucket = value // width
        if bucket in buckets:
            return True
        if bucket - 1 in buckets and value - buckets[bucket - 1] <= value_diff:
            return True
        if bucket + 1 in buckets and buckets[bucket + 1] - value <= value_diff:
            return True
        buckets[bucket] = value
    return False
'''],
        ["Checks only the same bucket and misses qualifying values split across adjacent bucket boundaries.", "Evicts the oldest value before comparing the current item and misses pairs exactly index_diff positions apart."], almost_oracle, random_almost,
        ["A window of the previous index_diff elements enforces the index condition.", "Partition values into buckets of width value_diff+1; two qualifying values occupy the same or neighboring buckets.", "For each value check its bucket and both neighbors, insert it, then evict the value that will be outside the next window.", "Python floor division gives consistent buckets for negative values. Exact distance and value boundaries count."],
        "A bucket's width is one more than the allowed value difference, so two values in one bucket always qualify by value. A qualifying cross-boundary pair can only occupy adjacent buckets, which are checked explicitly. Keeping only the prior index_diff values enforces the index bound. The independent oracle enumerates bounded index pairs directly.", "O(n)", "O(index_diff)", difficulty=8,
        stress=[([list(range(100000)), 99999, 0], False), ([list(range(99999)) + [0], 99999, 0], True)]),
    224: entry("basic_calculator", [("s", "str")], "int", ["strings", "stacks", "recursion", "math"],
        ["s is a valid 1–300000 character expression containing digits, spaces, +, -, and parentheses. Every number and running result fits signed 32-bit.", "Unary minus is allowed, including before a parenthesized expression; unary plus and built-in expression evaluators are forbidden. Parentheses can be deeply nested."],
        [(["1 + 1"], "Adding the two operands gives 2; spaces do not affect the expression."), (["(1+(4+5+2)-3)+(6+8)"], "The inner group is 11, the first outer group is 9, and adding 14 gives 23.")],
        [[s] for s in ("0", "-1", " 2-1 + 2 ", "1-(2-3)", "-(2+3)", "1-(-2)", "((7))", "10-(2+(3-4))", "1-(0-(0-5))", "2147483647", "-2147483648", "100-(20-(3+4))")],
        CALCULATOR, ['def basic_calculator(s):\n    s = s.replace("(", "").replace(")", "")\n    total, sign, number = 0, 1, 0\n    for c in s + "+":\n        if c.isdigit(): number = number * 10 + int(c)\n        elif c in "+-": total += sign * number; number = 0; sign = 1 if c == "+" else -1\n    return total\n', CALCULATOR.replace("stack.extend((total, sign))", "stack.extend((total, 1))")],
        ["Ignores grouping and evaluates the expression as a flat sequence.", "Drops the sign that applies to a parenthesized group, so unary or binary subtraction before '(' is wrong."], calculator_oracle, random_calculator,
        ["A sign applies to the number or complete parenthesized group that follows it.", "Keep the current subtotal and sign; save both when entering a parenthesis.", "On ')', finish the inner subtotal, multiply it by the saved sign, and add the saved outer subtotal.", "Use an explicit stack rather than recursive evaluation so valid very deep parentheses do not hit Python's recursion limit."],
        "Numbers are accumulated digit by digit. Plus or minus commits the preceding number and selects the next sign. An opening parenthesis saves the outer subtotal and sign; a closing parenthesis combines the completed inner value with that context. The independent oracle uses recursive descent on small generated expressions, while deterministic deep fixtures verify that the submitted approach must tolerate source-scale nesting.", "O(len(s))", "O(parenthesis depth)", difficulty=8,
        stress=[(["1+" * 149999 + "1"], 150000), (["(" * 100000 + "1" + ")" * 100000], 1)]),
    227: entry("basic_calculator_two", [("s", "str")], "int", ["strings", "stacks", "math"],
        ["s is a valid 1–300000 character expression made from nonnegative integers, spaces, and binary +, -, *, /. Parentheses and eval are not allowed.", "Apply multiplication and division before addition and subtraction. Integer division truncates toward zero; every intermediate result and the answer fit signed 32-bit."],
        [(["3+2*2"], "Multiplication has priority, so 3+(2×2)=7 rather than (3+2)×2."), ([" 3+5 / 2 "], "Integer 5/2 truncates to 2, then 3+2=5.")],
        [[s] for s in ("0", "42", "3/2", "1-7/2", "14-3/2", "2*3+4", "2+3*4", "8/3*3", "100/10/2", "1+2*3-4/2", "0-7/2", "18/4+2*3")],
        CALCULATOR_TWO, ['def basic_calculator_two(s):\n    values, operators, number = [], [], 0\n    for c in s + "+":\n        if c.isdigit(): number = number * 10 + int(c)\n        elif c in "+-*/":\n            if not values: values.append(number)\n            else:\n                op = operators[-1]; values[-1] = values[-1] + number if op == "+" else values[-1] - number if op == "-" else values[-1] * number if op == "*" else int(values[-1] / number)\n            operators.append(c); number = 0\n    return values[-1]\n', CALCULATOR_TWO.replace('current = abs(current) // number * (-1 if current < 0 else 1)', 'current = current // number')],
        ["Evaluates every operator left to right and ignores multiplication/division precedence.", "Uses floor division for a negative running term instead of truncating toward zero."], calculator_two_oracle, random_calculator_two,
        ["Only the current multiplication/division term must be resolved before later addition or subtraction.", "Keep a committed total and one current term. A new + or - commits the current term; * and / update it in place.", "Parse each full number, apply the previous operator, and return total+current after the final token.", "For negative division, divide absolute values and restore the sign; Python // alone rounds downward."],
        "The running current term contains all pending multiplication and division. Low-precedence operators commit that term into the total, preserving standard precedence without storing every token. Truncation toward zero is implemented with integer arithmetic. The independent oracle tokenizes the expression, collapses multiplication/division in a separate pass, then applies addition/subtraction.", "O(len(s))", "O(1)", difficulty=5,
        stress=[(["1+" * 149999 + "1"], 150000)]),
    228: entry("summary_ranges", [("nums", "list[int]")], "list[str]", ["arrays", "intervals"],
        ["nums is a sorted, unique list of 0–20 signed 32-bit integers.", "Return the smallest sorted ranges covering exactly the input values. Format a singleton as 'a' and a longer consecutive run as 'a->b'; do not invent missing integers."],
        [([[0, 1, 2, 4, 5, 7]], "The consecutive runs are 0 through 2, 4 through 5, and the singleton 7."), ([[0, 2, 3, 4, 6, 8, 9]], "Gaps split the output into '0', '2->4', '6', and '8->9'.")],
        [[nums] for nums in ([], [0], [-1], [-2, -1, 0], [-3, -1], [1, 3, 5], [1, 2], [-2, -1, 1, 2], [-2147483648, -2147483647], [2147483646, 2147483647], [-2147483648, 2147483647], list(range(-5, 6)))],
        RANGES, [RANGES.replace('result.append(str(nums[start]))', 'result.append(str(nums[start]) + "->" + str(nums[stop]))'), 'def summary_ranges(nums):\n    return [] if not nums else [str(nums[0]) + "->" + str(nums[-1])]\n'],
        ["Formats singleton ranges as a->a instead of the required single number.", "Spans from the first value to the last and includes integers missing across gaps."], ranges_oracle, random_ranges,
        ["A new range begins after any gap larger than one.", "Track the first and last indices of the current consecutive run.", "Extend while the next value equals current+1, format the finished run, then continue after it.", "Handle empty input and singleton formatting separately; signed-32-bit endpoints must work without sentinels."],
        "Each maximal consecutive run is exactly one required range. Scanning until a gap produces the unique smallest cover because merging across that gap would include a missing integer. The independent oracle detects adjacency by subtraction and formats each maximal run.", "O(n)", "O(1) excluding output", difficulty=3),
    229: entry("majority_over_third", [("nums", "list[int]")], "list[int]", ["arrays", "counting", "boyer-moore-voting"],
        ["nums contains 1–50000 integers from -10^9 to 10^9.", "Return every value occurring STRICTLY more than floor(n/3) times, in any order. There can be zero, one, or two such values."],
        [([[3, 2, 3]], "With n=3, a value must occur more than once; 3 occurs twice."), ([[1, 2]], "floor(2/3)=0, so both one-occurrence values qualify and both must be returned." )],
        [[nums] for nums in ([1], [1, 2, 3], [1, 1, 2, 2, 3], [1, 1, 1, 2, 2, 2, 3], [0, 0, 0], [-1, -1, 2], [1, 2, 3, 4], [1, 1, 2, 3], [1, 2, 1, 2], [5, 6, 5, 6, 7, 5, 6], [9] * 4 + [8] * 3 + [7] * 2, [1, 2, 3, 1, 2, 1])],
        THIRDS, [THIRDS.replace("> len(nums) // 3", ">= len(nums) // 3"), THIRDS.replace("return [candidate for candidate in (first, second)", "return [candidate for candidate in (first,)")],
        ["Uses a non-strict threshold and admits values occurring exactly floor(n/3) times.", "Tracks only one candidate even though two different values can both exceed one third."], thirds_oracle, random_thirds,
        ["At most two values can each occur more than one third of the time.", "Maintain two Boyer–Moore candidates and cancel groups of three different values.", "First select candidates in one pass; then count both candidates in the original list and retain only strict majorities.", "Candidate selection alone is not proof. The final verification pass handles arrays with no qualifying value."],
        "Canceling one occurrence from each of three distinct values cannot remove a true over-one-third majority from candidacy. Two counters therefore suffice, but the survivors must be verified because cancellation can leave nonmajorities. The independent oracle directly counts every distinct value.", "O(n)", "O(1) excluding output", difficulty=5,
        stress=[([[1] * 16667 + [2] * 16667 + [3] * 16666], [1, 2])]),
    233: entry("count_digit_one", [("n", "int")], "int", ["math", "digit-dynamic-programming", "place-value"],
        ["0 ≤ n ≤ 10^9.", "Count every occurrence of digit '1' in the ordinary decimal representations of all integers from 0 through n inclusive. Leading zeroes are not written."],
        [([13], "The numbers 1,10,11,12,13 contain 1+1+2+1+1=6 occurrences."), ([0], "The only included number is 0, whose representation contains no digit 1.")],
        [[n] for n in (1, 2, 9, 10, 11, 12, 19, 20, 21, 99, 100, 101)],
        DIGIT_ONE, [DIGIT_ONE.replace("def count_digit_one(n):", "def count_digit_one(n):\n    n -= 1"), DIGIT_ONE.replace("total += higher * place + lower + 1", "total += higher * place").replace("total += (higher + 1) * place", "total += higher * place")],
        ["Counts only values below n and omits any ones in n itself.", "Counts only complete place-value cycles and misses the partial cycle determined by the current digit and lower digits."], digit_one_oracle, random_digit_one,
        ["Count ones independently at the ones, tens, hundreds, and higher positions.", "At place p, split n into digits higher than p, the current digit, and lower digits.", "Add high×p for full cycles, then add 0, low+1, or p according as the current digit is 0, 1, or greater than 1.", "Advance p by a factor of ten. This avoids enumerating up to one billion numbers."],
        "For each decimal place, every complete block of 10p numbers contributes p ones at that place. The current partial block contributes nothing when its digit is zero, lower+1 when it is one, and a full p when greater. Summing all places counts each written one exactly once. The independent oracle converts and counts every number for bounded seeded inputs; the full 10^9 boundary has a separately derived closed-form fixture.", "O(log n)", "O(1)", difficulty=8,
        stress=[([1000000000], 900000001)]),
    238: entry("product_except_self", [("nums", "list[int]")], "list[int]", ["arrays", "prefix-products", "suffix-products"],
        ["nums contains 2–100000 integers from -30 to 30; every required prefix, suffix, and answer fits signed 32-bit.", "Return at each index the product of every OTHER element in O(n) time without / or //. The output list does not count as auxiliary space."],
        [([[1, 2, 3, 4]], "For index 0 multiply 2×3×4=24; applying the same exclusion gives [24,12,8,6]."), ([[-1, 1, 0, -3, 3]], "Only excluding the zero leaves a nonzero product, (-1)×1×(-3)×3=9." )],
        [[nums] for nums in ([1, 1], [2, 3], [0, 1], [0, 0], [0, 2, 3], [-1, -2, -3], [-1, 1, -1, 1], [2, 0, -2], [1, 2, 0, 4], [3, 3, 3], [-30, 1, 1], [1] * 20)],
        PRODUCT, ['def product_except_self(nums):\n    total = 1\n    for value in nums: total *= value\n    return [total // value if value else 0 for value in nums]\n', PRODUCT.replace("answer[index] *= suffix", "answer[index] = suffix")],
        ["Divides the total product and fails whenever exactly one input value is zero, in addition to violating the no-division rule.", "Overwrites the prefix product with the suffix product instead of multiplying the two sides."], product_oracle, random_product,
        ["The excluded-index product is the product to its left times the product to its right.", "Write all prefix products into the answer, then sweep backward with one running suffix product.", "Before multiplying nums[i] into the suffix, multiply answer[i] by the current suffix.", "Zeros need no special case: prefixes and suffixes naturally propagate them. Do not divide."],
        "The forward invariant makes answer[i] equal to the product strictly before i. The backward invariant holds the product strictly after i, so multiplying them excludes exactly nums[i]. The independent oracle constructs each answer by directly multiplying all other positions. The implementation uses only the output plus two scalars.", "O(n)", "O(1) auxiliary excluding output", difficulty=5,
        stress=[([[1] * 100000], [1] * 100000)]),
    240: entry("search_sorted_matrix", [("matrix", "list[list[int]]"), ("target", "int")], "bool", ["matrices", "binary-search", "divide-and-conquer"],
        ["matrix has 1–300 rows and 1–300 equal-length columns; values and target are from -10^9 to 10^9.", "Every row is nondecreasing left to right and every column is nondecreasing top to bottom. Return whether target occurs; duplicate values are allowed."],
        [([[[1, 4, 7, 11, 15], [2, 5, 8, 12, 19], [3, 6, 9, 16, 22], [10, 13, 14, 17, 24], [18, 21, 23, 26, 30]], 5], "Starting at the top right eliminates columns when too large and rows when too small, eventually reaching 5."), ([[[1, 4, 7], [2, 5, 8], [3, 6, 9]], 10], "Ten exceeds every matrix entry, so each row is eliminated and the search returns False." )],
        [[matrix, target] for matrix, target in (([[1]], 1), ([[1]], 0), ([[-5, -3], [-4, -1]], -4), ([[1, 1], [1, 1]], 1), ([[1, 2], [3, 4]], 3), ([[1, 2], [3, 4]], 2), ([[1, 4], [2, 5]], 3), ([[1, 4], [2, 5]], 4), ([[1, 4, 7]], 7), ([[1], [2], [3]], 2), ([[1, 3, 5], [2, 4, 6]], 0), ([[-10, 0, 10], [-5, 5, 15]], -5))],
        MATRIX, ['def search_sorted_matrix(matrix, target):\n    return target in matrix[0]\n', MATRIX.replace("if value > target:\n            column -= 1\n        else:\n            row += 1", "if value > target:\n            row += 1\n        else:\n            column -= 1")],
        ["Searches only the first row and misses values that occur below it.", "Eliminates a row when the corner is too large and a column when too small—the reverse of the valid dominance argument."], matrix_oracle, random_matrix,
        ["At the top-right corner, moving left always decreases or preserves the value, while moving down increases or preserves it.", "If the corner is too large, discard its column; if too small, discard its row.", "Start at row 0 and the last column, compare, and move left or down until found or out of bounds.", "This uses both sorting directions and takes at most rows+columns comparisons, unlike searching each row separately."],
        "The top-right element is the largest remaining value in its row and smallest remaining value in its column. If it is too large, its entire column is too large at that row and cannot be reached by moving down to a solution in the current search boundary; discard the column. If too small, the entire row to its left is no larger; discard the row. The independent oracle scans every cell directly.", "O(rows+columns)", "O(1)", difficulty=5,
        stress=[([[[row * 300 + column for column in range(300)] for row in range(300)], 89999], True), ([[[row * 300 + column for column in range(300)] for row in range(300)], 90000], False)]),
    241: entry("all_parenthesized_results", [("expression", "str")], "list[int]", ["recursion", "memoization", "dynamic-programming", "strings"],
        ["expression has 1–20 characters and alternates unsigned integers from 0 to 99 with +, -, or *. It has no spaces or written parentheses.", "Return one result for EVERY complete binary grouping, in any order. Preserve duplicate results when different groupings yield the same value; all results fit signed 32-bit and there are at most 10000."],
        [(["2-1-1"], "The groupings (2-1)-1 and 2-(1-1) produce 0 and 2."), (["2*3-4*5"], "Five groupings produce [-34,-14,-10,-10,10]; -10 appears twice because two different groupings yield it." )],
        [[expression] for expression in ("0", "12", "1+2", "3-4", "2*3", "1+2+3", "1-2-3", "2*2*2", "10+5*2", "11-2*3", "0-0-0", "2*3-4+5")],
        PARENTHESES, ['''\
def all_parenthesized_results(expression):
    total, term, number, operator = 0, 0, 0, "+"
    for char in expression + "+":
        if char.isdigit():
            number = number * 10 + int(char)
        else:
            if operator == "+":
                total += term
                term = number
            elif operator == "-":
                total += term
                term = -number
            else:
                term *= number
            operator, number = char, 0
    return [total + term]
''', PARENTHESES.replace("return solve(expression)", "return list(set(solve(expression)))")],
        ["Evaluates only one precedence order instead of enumerating all complete groupings.", "Deduplicates numeric values and loses the required multiplicity of different groupings."], parentheses_oracle, random_parentheses,
        ["The final operation of a grouping can be any operator in the expression.", "Split at each operator; independently enumerate results from its left and right substrings, then combine every pair.", "Memoize each substring so repeated subexpressions are solved once. A substring with no operator is one integer result.", "Do not convert the output to a set: different grouping trees may produce the same numeric result, and both occurrences belong in the answer."],
        "Every complete parenthesization has one final root operator. Splitting at each operator and taking the Cartesian product of left/right results enumerates every possible binary expression tree exactly once. Memoization avoids recomputing identical substrings. The independent oracle uses bottom-up interval dynamic programming over parsed number/operator tokens, and the comparator ignores ordering while preserving multiplicity.", "O(Catalan(m) × m) output-sensitive for m operators", "O(Catalan(m) × m) including output and memoized lists", difficulty=5,
        stress=[(["1*1*1*1*1*1*1*1*1*1"], [1] * 4862)]),
}
BATCH[229]["comparator"] = "unordered"
BATCH[241]["comparator"] = "unordered"
BATCH[220]["prerequisites"] = ["arrays", "sliding-window", "hash-maps"]
BATCH[224]["prerequisites"] = ["strings", "stacks", "recursion"]
BATCH[233]["prerequisites"] = ["math", "dynamic-programming"]
