"""Reviewed stack, backtracking, string-DP, parsing, array, and greedy imports."""
from collections import Counter
from itertools import combinations, permutations, product

from .import_batch_055 import entry


MOD = 1_000_000_007


def exclusive_oracle(args):
    n, logs = args
    answer = [0] * n
    active = []
    previous = 0
    for log in logs:
        function, action, raw_time = log.split(':')
        function, timestamp = int(function), int(raw_time)
        if timestamp > previous and active:
            answer[active[-1]] += timestamp - previous
        if action == 'start':
            active.append(function)
            previous = timestamp
        else:
            answer[active.pop()] += 1
            previous = timestamp + 1
    return answer


def shopping_oracle(args):
    price, offers, needs = args
    best = sum(cost * count for cost, count in zip(price, needs))
    def search(index, remaining, paid):
        nonlocal best
        if index == len(offers):
            best = min(best, paid + sum(cost * count for cost, count in zip(price, remaining)))
            return
        quantities, offer_price = offers[index][:-1], offers[index][-1]
        limit = min((remaining[i] // quantities[i] for i in range(len(needs)) if quantities[i]), default=0)
        for uses in range(limit + 1):
            search(index + 1, [remaining[i] - uses * quantities[i] for i in range(len(needs))], paid + uses * offer_price)
    search(0, needs, 0)
    return best


def ordinary_decode(text):
    previous_two, previous_one = 1, 1
    for index, char in enumerate(text):
        current = previous_one if char != '0' else 0
        if index and 10 <= int(text[index - 1:index + 1]) <= 26:
            current += previous_two
        previous_two, previous_one = previous_one, current
    return previous_one


def decode_oracle(args):
    text = args[0]
    stars = [index for index, char in enumerate(text) if char == '*']
    total = 0
    for values in product('123456789', repeat=len(stars)):
        expanded = list(text)
        for index, value in zip(stars, values):
            expanded[index] = value
        total += ordinary_decode(''.join(expanded))
    return total % MOD


def equation_parts(side):
    coefficient = constant = 0
    sign, number, seen_number = 1, 0, False
    for char in side + '+':
        if char.isdigit():
            number = number * 10 + int(char)
            seen_number = True
        elif char == 'x':
            coefficient += sign * (number if seen_number else 1)
            number, seen_number = 0, False
        else:
            if seen_number:
                constant += sign * number
            number, seen_number = 0, False
            sign = 1 if char == '+' else -1
    return coefficient, constant


def equation_oracle(args):
    left, right = args[0].split('=')
    left_x, left_value = equation_parts(left)
    right_x, right_value = equation_parts(right)
    coefficient, value = left_x - right_x, right_value - left_value
    if coefficient == 0:
        return 'Infinite solutions' if value == 0 else 'No solution'
    return f'x={value // coefficient}'


def average_oracle(args):
    nums, k = args
    return max(sum(nums[start:start + k]) / k for start in range(len(nums) - k + 1))


def mismatch_oracle(args):
    counts = Counter(args[0])
    duplicate = next(value for value, count in counts.items() if count == 2)
    missing = next(value for value in range(1, len(args[0]) + 1) if value not in counts)
    return [duplicate, missing]


def chain_oracle(args):
    pairs = args[0]
    best = 0
    for size in range(1, len(pairs) + 1):
        if any(all(order[i][1] < order[i + 1][0] for i in range(size - 1))
               for order in permutations(pairs, size)):
            best = size
    return best


def palindrome_oracle(args):
    text = args[0]
    return sum(text[start:end] == text[start:end][::-1]
               for start in range(len(text)) for end in range(start + 1, len(text) + 1))


def random_logs(rng):
    n = rng.randint(1, 4)
    root, child = rng.randrange(n), rng.randrange(n)
    start = rng.randint(0, 5)
    if rng.random() < .55:
        child_start = start + rng.randint(1, 3)
        child_end = child_start + rng.randint(0, 3)
        root_end = child_end + rng.randint(1, 3)
        logs = [f'{root}:start:{start}', f'{child}:start:{child_start}', f'{child}:end:{child_end}', f'{root}:end:{root_end}']
    else:
        logs = [f'{root}:start:{start}', f'{root}:end:{start + rng.randint(0, 5)}']
    return [n, logs]


def random_shopping(rng):
    kinds = rng.randint(1, 4)
    price = [rng.randint(1, 8) for _ in range(kinds)]
    needs = [rng.randint(0, 5) for _ in range(kinds)]
    if not any(needs): needs[rng.randrange(kinds)] = 1
    offers = []
    for _ in range(rng.randint(0, 4)):
        quantities = [rng.randint(0, max(1, need)) for need in needs]
        if not any(quantities): quantities[rng.randrange(kinds)] = 1
        offers.append(quantities + [rng.randint(1, 18)])
    return [price, offers, needs]


def random_decode(rng):
    length = rng.randint(1, 6)
    text = ''.join(rng.choice('0123456789*') for _ in range(length))
    while text.count('*') > 3:
        text = text.replace('*', str(rng.randint(0, 9)), 1)
    return [text]


def format_side(coefficient, constant):
    terms = []
    if coefficient:
        terms.append(('' if coefficient == 1 else '-' if coefficient == -1 else str(coefficient)) + 'x')
    if constant or not terms:
        terms.append(str(constant))
    return '+'.join(terms).replace('+-', '-')


def random_equation(rng):
    left_x, right_x = rng.randint(-5, 5), rng.randint(-5, 5)
    left_value, right_value = rng.randint(-15, 15), rng.randint(-15, 15)
    difference = left_x - right_x
    if difference and (right_value - left_value) % difference:
        right_value = left_value + difference * rng.randint(-8, 8)
    return [format_side(left_x, left_value) + '=' + format_side(right_x, right_value)]


def random_average(rng):
    nums = [rng.randint(-100, 100) for _ in range(rng.randint(1, 20))]
    return [nums, rng.randint(1, len(nums))]


def random_mismatch(rng):
    n = rng.randint(2, 30)
    missing, duplicate = rng.sample(range(1, n + 1), 2)
    nums = [duplicate if value == missing else value for value in range(1, n + 1)]
    rng.shuffle(nums)
    return [nums]


def random_chain(rng):
    pairs = []
    for _ in range(rng.randint(1, 7)):
        start = rng.randint(-12, 10)
        pairs.append([start, start + rng.randint(1, 6)])
    return [pairs]


def random_palindrome(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 14)))]


EXCLUSIVE = '''\
def exclusive_function_times(n, logs):
    answer = [0] * n
    stack = []
    previous = 0
    for log in logs:
        function, action, timestamp = log.split(':')
        function, timestamp = int(function), int(timestamp)
        if action == 'start':
            if stack:
                answer[stack[-1]] += timestamp - previous
            stack.append(function)
            previous = timestamp
        else:
            answer[stack.pop()] += timestamp - previous + 1
            previous = timestamp + 1
    return answer
'''


SHOPPING = '''\
def minimum_shopping_cost(price, special, needs):
    from functools import lru_cache
    @lru_cache(None)
    def solve(remaining):
        best = sum(price[i] * remaining[i] for i in range(len(price)))
        for offer in special:
            following = tuple(remaining[i] - offer[i] for i in range(len(price)))
            if all(value >= 0 for value in following):
                best = min(best, offer[-1] + solve(following))
        return best
    return solve(tuple(needs))
'''


DECODE = '''\
def wildcard_decode_count(s):
    mod = 1_000_000_007
    def single(char):
        return 9 if char == '*' else int(char != '0')
    def pair(left, right):
        if left == '*' and right == '*': return 15
        if left == '*': return 2 if right <= '6' else 1
        if right == '*': return 9 if left == '1' else 6 if left == '2' else 0
        return int(10 <= int(left + right) <= 26)
    previous_two, previous_one = 1, single(s[0])
    for index in range(1, len(s)):
        current = (single(s[index]) * previous_one + pair(s[index - 1], s[index]) * previous_two) % mod
        previous_two, previous_one = previous_one, current
    return previous_one
'''


EQUATION = '''\
def solve_linear_equation(equation):
    def parse(side):
        coefficient = constant = 0
        for term in side.replace('-', '+-').split('+'):
            if not term: continue
            if term.endswith('x'):
                raw = term[:-1]
                coefficient += -1 if raw == '-' else 1 if raw == '' else int(raw)
            else:
                constant += int(term)
        return coefficient, constant
    left, right = equation.split('=')
    left_x, left_value = parse(left)
    right_x, right_value = parse(right)
    coefficient, value = left_x - right_x, right_value - left_value
    if coefficient == 0:
        return 'Infinite solutions' if value == 0 else 'No solution'
    return 'x=' + str(value // coefficient)
'''


AVERAGE = '''\
def maximum_fixed_average(nums, k):
    window = sum(nums[:k])
    best = window
    for index in range(k, len(nums)):
        window += nums[index] - nums[index - k]
        best = max(best, window)
    return best / k
'''


MISMATCH = '''\
def find_set_mismatch(nums):
    expected = len(nums) * (len(nums) + 1) // 2
    duplicate = sum(nums) - sum(set(nums))
    missing = expected - (sum(nums) - duplicate)
    return [duplicate, missing]
'''


CHAIN = '''\
def longest_pair_chain(pairs):
    ending = -float('inf')
    length = 0
    for start, finish in sorted(pairs, key=lambda pair: pair[1]):
        if start > ending:
            length += 1
            ending = finish
    return length
'''


PALINDROMES = '''\
def count_palindromic_substrings(s):
    total = 0
    for center in range(2 * len(s) - 1):
        left = center // 2
        right = left + center % 2
        while left >= 0 and right < len(s) and s[left] == s[right]:
            total += 1
            left -= 1
            right += 1
    return total
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial], editorial


BATCH = {
    636: entry('exclusive_function_times', [('n','int'),('logs','list[str]')], 'list[int]', ['stacks','simulation'],
        ['1 <= n <= 100; logs form one valid single-threaded call stack.', 'An end timestamp is inclusive, and function IDs range from 0 through n-1.'],
        [([2,['0:start:0','1:start:2','1:end:5','0:end:6']], 'Function 0 runs for units 0-1 and 6; function 1 runs for units 2-5.'), ([1,['0:start:0','0:start:2','0:end:5','0:end:6']], 'Recursive calls share the same function ID, whose exclusive units total seven.')],
        [[n,logs] for n,logs in ((1,['0:start:0','0:end:0']),(2,['1:start:3','1:end:7']),(2,['0:start:0','1:start:1','1:end:1','0:end:2']),(3,['2:start:1','0:start:2','0:end:2','2:end:4']),(2,['0:start:0','1:start:1','1:end:1','0:end:3']),(3,['0:start:0','1:start:2','1:end:3','2:start:4','2:end:6','0:end:7']),(2,['0:start:5','0:end:5']),(4,['3:start:0','2:start:3','2:end:4','3:end:9']),(1,['0:start:10','0:end:20']),(2,['1:start:0','1:start:1','1:end:3','1:end:5']),(3,['0:start:0','2:start:5','2:end:8','0:end:10']),(2,['0:start:0','1:start:2','1:end:2','0:end:5']))],
        EXCLUSIVE, [EXCLUSIVE.replace('+ 1',''), EXCLUSIVE.replace('previous = timestamp + 1','previous = timestamp')],
        ['Treats inclusive end timestamps as exclusive.', 'Resumes the caller on the ending unit instead of the following unit.'], exclusive_oracle, random_logs,
        *lesson('Only the function on top of the call stack executes.', 'Charge elapsed time at every event, accounting for inclusive end events.', 'Pause the old top on start; finish and pop on end; move previous to end+1.', 'The previous timestamp marks the first uncharged unit, so every unit is assigned exactly once.'), 'O(number of logs)', 'O(n + call depth)', 5),
    638: entry('minimum_shopping_cost', [('price','list[int]'),('special','list[list[int]]'),('needs','list[int]')], 'int', ['dynamic-programming','backtracking'],
        ['1 <= len(price) <= 6; quantities and needs are nonnegative and needs are at most 10.', 'Buy exactly the requested quantities without exceeding any need; offers may be reused.'],
        [([[2,5],[[3,0,5],[1,2,10]],[3,2]], 'One three-unit first-item offer plus one mixed offer costs fourteen.'), ([[2,3,4],[[1,1,0,4],[2,2,1,9]],[1,2,1]], 'The first offer plus individual purchases costs eleven.')],
        [[price,offers,needs] for price,offers,needs in (([2],[],[3]),([2],[[1,1]],[3]),([5],[[2,8]],[4]),([2,3],[],[1,1]),([2,3],[[1,1,4]],[1,1]),([2,3],[[2,0,3]],[3,0]),([3,4],[[0,2,5]],[0,4]),([2,5],[[3,0,5]],[2,1]),([1,10],[[1,1,20]],[2,2]),([4,4],[[1,1,7]],[3,3]),([2,3,5],[[1,1,1,8]],[2,2,2]),([9,1],[[1,0,4],[0,2,1]],[2,4]))],
        SHOPPING, [SHOPPING.replace('if all(value >= 0 for value in following):','if all(value > 0 for value in following):'), SHOPPING.replace('best = min(best, offer[-1] + solve(following))','best = min(best, solve(following))')],
        ['Rejects valid offers that exactly satisfy one item.', 'Forgets to add the price of a chosen offer.'], shopping_oracle, random_shopping,
        *lesson('Remaining needs completely describe a reusable subproblem.', 'Memoize the cheapest cost for each remaining-quantity tuple.', 'Start with individual prices; try every offer that does not make a need negative.', 'Every offer strictly reduces some quantity, so recursion terminates and caching merges repeated purchase states.'), 'O(product of (need+1) * offers * item types)', 'O(product of (need+1))', 7),
    639: entry('wildcard_decode_count', [('s','str')], 'int', ['dynamic-programming','strings'],
        ['1 <= len(s) <= 100,000; s contains digits and * only.', '* represents a digit from 1 through 9; return the decoding count modulo 1,000,000,007.'],
        [(['*'], 'The wildcard may be any digit from one through nine.'), (['1*'], 'There are nine one-digit endings and nine valid two-digit endings, totaling eighteen.')],
        [[s] for s in ('0','1','10','20','30','**','*0','2*','3*','***','1*0','*1*','123*')],
        DECODE, [DECODE.replace("return 9 if char == '*'", "return 1 if char == '*'"), DECODE.replace("return 15", "return 9")],
        ['Counts a wildcard as only one possible single digit.', 'Counts too few valid two-digit values for two wildcards.'], decode_oracle, random_decode,
        *lesson('Each position contributes through one-character and two-character decodings with wildcard multiplicities.', 'Roll a two-state dynamic program and multiply by the number of valid substitutions.', 'current = singleWays*dp[i-1] + pairWays*dp[i-2], modulo the limit.', 'The final token of every decoding has length one or two, producing disjoint cases counted by the recurrence.'), 'O(len(s))', 'O(1)', 8),
    640: entry('solve_linear_equation', [('equation','str')], 'str', ['strings','math','parsing'],
        ['The equation contains integers, x, +, -, and exactly one = sign.', 'The equation has an integer solution, no solution, or infinitely many solutions.'],
        [(['x+5-3+x=6+x-2'], 'Collecting x terms and constants reduces the equation to x=2.'), (['x=x'], 'Both sides are identical for every value of x, so solutions are infinite.')],
        [[e] for e in ('x=2','2x=4','2x+3=7','x+1=x+2','0x=0','0x=1','-x=-3','3x-6=0','10=2x','2x+4=2x+4','5x-10=3x+2','x-1=0')],
        EQUATION, [EQUATION.replace("left_x - right_x, right_value - left_value", "left_x + right_x, right_value - left_value"), EQUATION.replace("'Infinite solutions' if value == 0 else 'No solution'", "'No solution' if value == 0 else 'Infinite solutions'")],
        ['Adds variable coefficients from both sides instead of moving the right side.', 'Swaps the no-solution and infinite-solution cases.'], equation_oracle, random_equation,
        *lesson('Each side reduces to one x coefficient and one constant.', 'Parse signed terms, move x terms left and constants right, then inspect the resulting coefficient.', 'Compute a*x=b; handle a=0 separately, otherwise return b//a.', 'Linear collection preserves equality and the zero coefficient precisely distinguishes contradictory from identical equations.'), 'O(len(equation))', 'O(len(equation))', 5),
    643: entry('maximum_fixed_average', [('nums','list[int]'),('k','int')], 'float', ['arrays','sliding-windows'],
        ['1 <= k <= len(nums) <= 100,000.', 'Return the largest average among all contiguous subarrays of exactly k values.'],
        [([[1,12,-5,-6,50,3],4], 'The subarray [12,-5,-6,50] has sum 51 and average 12.75.'), ([[5],1], 'The only length-one subarray has average five.')],
        [[nums,k] for nums,k in (([1,2],1),([1,2],2),([-1,-2,-3],2),([0,0,0],2),([5,-1,5],2),([10,0,0,10],3),([-5,100,-5],1),([1,2,3,4],3),([4,3,2,1],2),([7,7,7,7],3),([-10,0,10],2),([1,-1,1,-1,1],4))],
        AVERAGE, [AVERAGE.replace('best = window','best = 0'), AVERAGE.replace('nums[index - k]','nums[index - k + 1]')],
        ['Initializes the best sum to zero, failing all-negative arrays.', 'Removes the wrong element when the window slides.'], average_oracle, random_average,
        *lesson('Adjacent fixed-length windows differ by one entering and one leaving value.', 'Maintain the current sum instead of recomputing every subarray.', 'Initialize the first k values; slide and track the largest sum; divide once.', 'All windows have the same denominator, so maximizing their sums also maximizes their averages.'), 'O(n)', 'O(1)', 3),
    645: entry('find_set_mismatch', [('nums','list[int]')], 'list[int]', ['arrays','hash-maps','math'],
        ['2 <= len(nums) <= 10,000; values are from 1 through n.', 'Exactly one value occurs twice and exactly one different value is missing; return [duplicate, missing].'],
        [([[1,2,2,4]], 'Two is repeated and three is absent.'), ([[1,1]], 'One is repeated and two is absent.')],
        [[[v for v in values]] for values in ([2,2],[1,3,3],[1,2,2],[2,3,3],[1,1,3,4],[1,2,3,3],[4,2,2,1],[5,3,2,1,5],[1,2,4,4,5],[6,2,3,4,5,6],[1,3,4,5,5,6],[2,1,4,3,2])],
        MISMATCH, [MISMATCH.replace('sum(nums) - sum(set(nums))','sum(set(nums)) - sum(nums)'), MISMATCH.replace('return [duplicate, missing]','return [missing, duplicate]')],
        ['Reverses the subtraction used to recover the duplicate.', 'Returns the required two values in reverse order.'], mismatch_oracle, random_mismatch,
        *lesson('The duplicate is the excess over the distinct sum; the missing value completes the expected 1..n sum.', 'Use arithmetic sums and the set of observed values.', 'duplicate=sum(nums)-sum(set); missing=n(n+1)/2-(sum(nums)-duplicate).', 'Removing one copy of the duplicate leaves exactly the intended set minus the missing number.'), 'O(n)', 'O(n)', 3),
    646: entry('longest_pair_chain', [('pairs','list[list[int]]')], 'int', ['greedy','sorting'],
        ['1 <= len(pairs) <= 1,000; every pair [a,b] has a < b.', 'A pair may follow another only when its first value is strictly greater than the previous second value.'],
        [([[[1,2],[2,3],[3,4]]], 'Choose [1,2] followed by [3,4] for a chain of length two.'), ([[[-6,-4],[-3,0],[1,2]]], 'All three pairs form a valid increasing chain.')],
        [[pairs] for pairs in ([[1,2]],[[1,2],[3,4]],[[1,5],[2,3],[4,6]],[[1,10],[2,3],[4,5],[6,7]],[[3,4],[1,2]],[[1,2],[2,3]],[[0,1],[-2,-1],[2,3]],[[1,100],[2,3],[4,5]],[[5,6],[1,2],[3,4]],[[1,4],[2,5],[6,7]],[[0,2],[1,3],[3,5]],[[10,20],[-10,-5],[0,5]])],
        CHAIN, [CHAIN.replace("key=lambda pair: pair[1]", "key=lambda pair: pair[0]"), CHAIN.replace('start > ending','start >= ending')],
        ['Sorts by starting value, allowing a long early pair to block a better chain.', 'Allows touching endpoints even though the inequality must be strict.'], chain_oracle, random_chain,
        *lesson('The pair finishing earliest leaves the most room for all later pairs.', 'Sort by right endpoint and greedily take each compatible pair.', 'Track the last selected end; accept when the next start is greater.', 'Replacing any first choice by the earliest-finishing available pair cannot reduce the remaining options.'), 'O(n log n)', 'O(n)', 5),
    647: entry('count_palindromic_substrings', [('s','str')], 'int', ['strings','two-pointers'],
        ['1 <= len(s) <= 1,000.', 'Count every palindromic occurrence, including equal text at different positions.'],
        [(['abc'], 'Each single character is a palindrome, giving three.'), (['aaa'], 'Three singles, two length-two substrings, and one length-three substring give six.')],
        [[s] for s in ('a','aa','ab','aba','abba','abcd','racecar','aaaa','aabaa','abcba','abab','abbc')],
        PALINDROMES, [PALINDROMES.replace('range(2 * len(s) - 1)','range(len(s))'), PALINDROMES.replace('total += 1','total += right - left + 1')],
        ['Checks only odd centers and misses even-length palindromes.', 'Adds palindrome length instead of one occurrence per successful expansion.'], palindrome_oracle, random_palindrome,
        *lesson('Every palindrome has exactly one center, either a character or a gap.', 'Expand outward from all 2n-1 possible centers.', 'For each center, move left and right while characters match and increment the count.', 'Center expansion enumerates every palindromic interval exactly once without storing a quadratic table.'), 'O(n^2)', 'O(1)', 5),
}

BATCH[643]['comparator'] = 'float'
