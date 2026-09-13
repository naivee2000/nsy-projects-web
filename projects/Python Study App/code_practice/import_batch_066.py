"""Reviewed binary-search, combinatorics, sequence, string, and stack imports."""
from itertools import combinations, product

from .import_batch_055 import entry


def table_oracle(args):
    rows, columns, k = args
    return sorted(r * c for r in range(1, rows + 1) for c in range(1, columns + 1))[k - 1]


def swap_oracle(args):
    digits = list(str(args[0]))
    best = args[0]
    for left in range(len(digits)):
        for right in range(left, len(digits)):
            changed = digits[:]
            changed[left], changed[right] = changed[right], changed[left]
            best = max(best, int(''.join(changed)))
    return best


def bulbs_oracle(args):
    count, presses = args
    count = min(count, 6)
    start = (1 << count) - 1
    masks = []
    for rule in range(4):
        mask = 0
        for index in range(1, count + 1):
            if rule == 0 or rule == 1 and index % 2 == 0 or rule == 2 and index % 2 == 1 or rule == 3 and index % 3 == 1:
                mask |= 1 << (index - 1)
        masks.append(mask)
    states = {start}
    for _ in range(presses):
        states = {state ^ mask for state in states for mask in masks}
    return len(states)


def lis_count_oracle(args):
    nums = args[0]
    best_length = count = 0
    for size in range(1, len(nums) + 1):
        found = 0
        for indices in combinations(range(len(nums)), size):
            if all(nums[indices[i]] < nums[indices[i + 1]] for i in range(size - 1)):
                found += 1
        if found:
            best_length, count = size, found
    return count


def wildcard_parentheses_oracle(args):
    text = args[0]
    stars = [index for index, char in enumerate(text) if char == '*']
    for replacements in product('() ', repeat=len(stars)):
        candidate = list(text)
        for index, value in zip(stars, replacements): candidate[index] = value
        balance = 0
        valid = True
        for char in candidate:
            if char == ' ': continue
            balance += 1 if char == '(' else -1
            if balance < 0: valid = False; break
        if valid and balance == 0: return True
    return False


def near_palindrome_oracle(args):
    text = args[0]
    if text == text[::-1]: return True
    return any(text[:index] + text[index + 1:] == (text[:index] + text[index + 1:])[::-1]
               for index in range(len(text)))


def next_time_oracle(args):
    time = args[0]
    allowed = set(time.replace(':', ''))
    hour, minute = map(int, time.split(':'))
    start = hour * 60 + minute
    for elapsed in range(1, 24 * 60 + 1):
        value = (start + elapsed) % (24 * 60)
        candidate = f'{value // 60:02d}:{value % 60:02d}'
        if set(candidate.replace(':', '')) <= allowed: return candidate


def baseball_oracle(args):
    scores = []
    for operation in args[0]:
        if operation == 'C': scores.pop()
        elif operation == 'D': scores.append(2 * scores[-1])
        elif operation == '+': scores.append(scores[-1] + scores[-2])
        else: scores.append(int(operation))
    return sum(scores)


def random_table(rng):
    rows, columns = rng.randint(1, 12), rng.randint(1, 12)
    return [rows, columns, rng.randint(1, rows * columns)]


def random_swap(rng): return [rng.randint(0, 99_999_999)]
def random_bulbs(rng): return [rng.randint(1, 6), rng.randint(0, 4)]


def random_lis(rng):
    return [[rng.randint(-8, 8) for _ in range(rng.randint(1, 11))]]


def random_wildcard(rng):
    text = ''.join(rng.choice('()**') for _ in range(rng.randint(1, 10)))
    while text.count('*') > 6: text = text.replace('*', rng.choice('()'), 1)
    return [text]


def random_near_palindrome(rng): return [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 16)))]


def random_time(rng): return [f'{rng.randrange(24):02d}:{rng.randrange(60):02d}']


def random_baseball(rng):
    operations, scores = [], []
    for _ in range(rng.randint(1, 15)):
        choices = ['number']
        if scores: choices += ['C', 'D']
        if len(scores) >= 2: choices.append('+')
        choice = rng.choice(choices)
        if choice == 'number':
            value = rng.randint(-30, 30); operations.append(str(value)); scores.append(value)
        elif choice == 'C': operations.append('C'); scores.pop()
        elif choice == 'D': operations.append('D'); scores.append(2 * scores[-1])
        else: operations.append('+'); scores.append(scores[-1] + scores[-2])
    return [operations]


TABLE = '''\
def kth_multiplication_value(m, n, k):
    low, high = 1, m * n
    while low < high:
        middle = (low + high) // 2
        count = sum(min(n, middle // row) for row in range(1, m + 1))
        if count >= k: high = middle
        else: low = middle + 1
    return low
'''


SWAP = '''\
def maximum_one_swap(num):
    digits = list(str(num))
    last = {digit: index for index, digit in enumerate(digits)}
    for index, digit in enumerate(digits):
        for larger in range(9, int(digit), -1):
            position = last.get(str(larger), -1)
            if position > index:
                digits[index], digits[position] = digits[position], digits[index]
                return int(''.join(digits))
    return num
'''


BULBS = '''\
def distinct_bulb_states(n, presses):
    if presses == 0: return 1
    n = min(n, 3)
    if n == 1: return 2
    if n == 2: return 3 if presses == 1 else 4
    if presses == 1: return 4
    if presses == 2: return 7
    return 8
'''


LIS_COUNT = '''\
def number_of_longest_increasing(nums):
    lengths = [1] * len(nums)
    counts = [1] * len(nums)
    for right in range(len(nums)):
        for left in range(right):
            if nums[left] >= nums[right]: continue
            candidate = lengths[left] + 1
            if candidate > lengths[right]:
                lengths[right], counts[right] = candidate, counts[left]
            elif candidate == lengths[right]:
                counts[right] += counts[left]
    longest = max(lengths)
    return sum(count for length, count in zip(lengths, counts) if length == longest)
'''


WILDCARD = '''\
def valid_wildcard_parentheses(s):
    low = high = 0
    for char in s:
        if char == '(':
            low += 1; high += 1
        elif char == ')':
            low = max(0, low - 1); high -= 1
        else:
            low = max(0, low - 1); high += 1
        if high < 0: return False
    return low == 0
'''


NEAR_PALINDROME = '''\
def valid_after_one_deletion(s):
    def palindrome(left, right):
        while left < right:
            if s[left] != s[right]: return False
            left += 1; right -= 1
        return True
    left, right = 0, len(s) - 1
    while left < right and s[left] == s[right]:
        left += 1; right -= 1
    return left >= right or palindrome(left + 1, right) or palindrome(left, right - 1)
'''


NEXT_TIME = '''\
def next_reusable_time(time):
    allowed = set(time.replace(':', ''))
    hour, minute = map(int, time.split(':'))
    current = hour * 60 + minute
    while True:
        current = (current + 1) % (24 * 60)
        candidate = f'{current // 60:02d}:{current % 60:02d}'
        if set(candidate.replace(':', '')) <= allowed:
            return candidate
'''


BASEBALL = '''\
def baseball_score(ops):
    scores = []
    for operation in ops:
        if operation == 'C': scores.pop()
        elif operation == 'D': scores.append(2 * scores[-1])
        elif operation == '+': scores.append(scores[-1] + scores[-2])
        else: scores.append(int(operation))
    return sum(scores)
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial], editorial


BATCH = {
    668: entry('kth_multiplication_value',[('m','int'),('n','int'),('k','int')],'int',['binary-search','math'],
        ['1 <= m,n <= 30,000; 1 <= k <= m*n.','The table cell at row i and column j contains i*j; duplicates occupy separate ranked positions.'],
        [([3,3,5], 'The sorted table values are 1,2,2,3,3,4,6,6,9, so the fifth is three.'), ([2,3,6], 'The largest and sixth table entry is six.')],
        [[m,n,k] for m,n,k in ((1,1,1),(1,5,3),(5,1,4),(2,2,2),(2,2,3),(3,4,7),(4,4,8),(5,6,20),(10,10,50),(2,10,11),(6,7,1),(6,7,42))],
        TABLE,[TABLE.replace('count >= k','count > k'),TABLE.replace('min(n, middle // row)','min(n, (middle - 1) // row)')],['Uses a strict rank comparison and skips values at the boundary.','Counts values strictly below the candidate instead of at most the candidate.'],table_oracle,random_table,
        *lesson('For a candidate value, each row contributes a known prefix of entries no larger than it.','Binary-search the smallest value whose cumulative table count reaches k.','count(x)=sum(min(n,x//row)); move high when count>=k.','The count is monotone and includes duplicates, exactly matching ranked table positions.'),'O(m log(m*n))','O(1)',8),
    670: entry('maximum_one_swap',[('num','int')],'int',['greedy','math'],
        ['0 <= num <= 100,000,000.','Swap at most one pair of decimal digits to maximize the integer.'],
        [([2736], 'Swap two and seven to produce 7236.'), ([9973], 'No swap improves a number whose digits already descend.')],
        [[n] for n in (0,7,10,12,21,98368,1993,9090,109090,12345,54321,10000000)],
        SWAP,[SWAP.replace('position = last.get(str(larger), -1)','position = digits.index(str(larger)) if str(larger) in digits else -1'),SWAP.replace('range(9, int(digit), -1)','range(int(digit)+1, 10)')],['Uses the leftmost larger digit rather than its rightmost occurrence.','Chooses the smallest improving digit instead of the largest.'],swap_oracle,random_swap,
        *lesson('The earliest digit that can increase dominates every later improvement.','At that position, swap with the rightmost occurrence of the largest available digit.','Record each digit’s last index; scan left to right and digits 9 downward.','Rightmost placement leaves the displaced smaller digit as late as possible after maximizing the most significant change.'),'O(number of digits)','O(1)',5),
    672: entry('distinct_bulb_states',[('n','int'),('presses','int')],'int',['combinatorics','bit-manipulation'],
        ['1 <= n <= 1,000; 0 <= presses <= 1,000.','Count configurations reachable after exactly presses button presses using the four specified flip patterns.'],
        [([1,1], 'Either flipping all bulbs or one of the equivalent odd-position controls creates two distinct states.'), ([2,1], 'One press can reach three distinct two-bulb configurations.')],
        [[n,p] for n,p in ((1,0),(1,2),(2,0),(2,2),(2,3),(3,0),(3,1),(3,2),(3,3),(4,1),(5,2),(6,4))],
        BULBS,[BULBS.replace("if presses == 0: return 1","if presses == 0: return 2"),BULBS.replace("if n == 2: return 3 if presses == 1 else 4","if n == 2: return 3")],['Claims two states even when no button is pressed.','Misses the fourth two-bulb state reachable after multiple presses.'],bulbs_oracle,random_bulbs,
        *lesson('Only the first three bulb positions create independent behavior under the four periodic buttons.','Reduce n to three and use the small closed-form state counts by press count.','Handle zero presses, then n=1, n=2, and presses 1/2/3+ for n>=3.','Beyond three bulbs every position repeats one of the same parity/modulo-three patterns, so no new state distinctions arise.'),'O(1)','O(1)',5),
    673: entry('number_of_longest_increasing',[('nums','list[int]')],'int',['dynamic-programming','arrays'],
        ['1 <= len(nums) <= 2,000.','Count distinct index subsequences having maximum strictly increasing length.'],
        [([[1,3,5,4,7]], 'The longest subsequences end through either three-five-seven or three-four-seven, giving two.'), ([[2,2,2,2,2]], 'Each individual position is a distinct longest subsequence, giving five.')],
        [[[v for v in nums]] for nums in ([1],[1,2],[2,1],[1,1],[1,2,3],[3,2,1],[1,2,4,3,5],[1,3,2,4],[2,2,3,3],[1,5,2,3,4],[0,-1,0,1],[1,2,2,3])],
        LIS_COUNT,[LIS_COUNT.replace('return sum(count for length, count in zip(lengths, counts) if length == longest)','return longest'),LIS_COUNT.replace("elif candidate == lengths[right]:\n                counts[right] += counts[left]", "elif candidate == lengths[right]:\n                counts[right] = counts[left]")],['Returns the LIS length rather than the number of longest subsequences.','Overwrites equal-length path counts instead of adding them.'],lis_count_oracle,random_lis,
        *lesson('Each position needs both its best increasing length and how many ways achieve that length.','Extend every earlier smaller value and either replace or add its contribution.','On a longer candidate copy its count; on an equal candidate add its count; sum counts at global max length.','Index-distinct predecessors define disjoint subsequence sets, so equal best contributions add.'),'O(n²)','O(n)',5),
    678: entry('valid_wildcard_parentheses',[('s','str')],'bool',['greedy','strings','parentheses'],
        ['1 <= len(s) <= 100; s contains (, ), and * only.','Each * may independently become (, ), or the empty string.'],
        [(['()'], 'The ordinary matching pair is valid.'), (['(*)'], 'The wildcard may be empty, leaving ().')],
        [[s] for s in ('*','(',')','(*','*)','(**)','(*))','(((*)','((*)','***','())*','(*()')],
        WILDCARD,["def valid_wildcard_parentheses(s):\n    return s.replace('*','') == '()'\n",WILDCARD.replace("low = max(0, low - 1); high += 1","low += 1; high += 1")],['Treats every wildcard as empty and recognizes only one pair.','Treats every wildcard only as an opening parenthesis.'],wildcard_parentheses_oracle,random_wildcard,
        *lesson('After each prefix, wildcard choices produce a continuous range of possible open counts.','Track the minimum and maximum feasible balance, clamping the minimum at zero.','Update both bounds per character; fail if high<0 and accept if final low=0.','The interval compactly represents all reachable balances, avoiding exponential wildcard expansion.'),'O(len(s))','O(1)',5),
    680: entry('valid_after_one_deletion',[('s','str')],'bool',['two-pointers','strings'],
        ['1 <= len(s) <= 100,000; s contains lowercase letters.','Return true when s is already a palindrome or can become one by deleting exactly one optional character.'],
        [(['aba'], 'The string is already a palindrome.'), (['abca'], 'Deleting b or c leaves a palindrome.')],
        [[s] for s in ('a','ab','abc','abba','abcba','abcca','deeee','eeeed','abcdef','aguokepatgbnvfqmgmlcupupucu','raceacar','abbda')],
        NEAR_PALINDROME,["def valid_after_one_deletion(s):\n    return s == s[::-1]\n",NEAR_PALINDROME.replace('or palindrome(left, right - 1)','')],['Does not use the permitted deletion.','Tries deleting only the left character at the first mismatch.'],near_palindrome_oracle,random_near_palindrome,
        *lesson('Before the first mismatch, no deletion choice matters.','At the first mismatch, test the two possible one-character skips.','Walk inward; on mismatch check s[left+1:right] and s[left:right-1].','Any valid solution must delete one of the two mismatching boundary characters, so the two checks are exhaustive.'),'O(n)','O(1)',3),
    681: entry('next_reusable_time',[('time','str')],'str',['strings','enumeration'],
        ['time is a valid 24-hour HH:MM string.','Return the next time, possibly on the next day, using only digits present in the input.'],
        [(['19:34'], '19:39 is the first later valid time using digits 1,9,3,4.'), (['23:59'], 'The next reusable time is 22:22 on the following day.')],
        [[t] for t in ('00:00','11:11','12:34','13:55','20:48','01:32','22:23','05:50','09:59','18:48','14:41','21:12')],
        NEXT_TIME,[NEXT_TIME.replace('(current + 1)','(current + 2)'),"def next_reusable_time(time):\n    return time\n"],['Advances two minutes at a time and can skip the correct answer.','Accepts the current display instead of requiring the next time.'],next_time_oracle,random_time,
        *lesson('There are only 1,440 clock minutes to inspect.','Advance cyclically by one minute until all four displayed digits belong to the original digit set.','Convert to minutes, increment modulo 1440, format HH:MM, and test its digits.','Minute-by-minute enumeration guarantees the first accepted candidate is chronologically closest, including wraparound.'),'O(1)','O(1)',5),
    682: entry('baseball_score',[('ops','list[str]')],'int',['stacks','simulation'],
        ['1 <= len(operations) <= 1,000; every operation is valid given prior scores.','An integer records a score, C removes the previous score, D doubles it, and + sums the previous two.'],
        [([['5','2','C','D','+']], 'The record evolves to [5,10,15], totaling thirty.'), ([['5','-2','4','C','D','9','+','+']], 'Applying all stack operations produces twenty-seven.')],
        [[ops] for ops in (['1'],['-5'],['1','2','+'],['1','D'],['1','C','2'],['3','4','C'],['2','3','D','+'],['10','-5','+'],['1','2','3','C','+'],['5','D','C'],['7','8','+','D'],['-1','-2','+','D'])],
        BASEBALL,[BASEBALL.replace('2 * scores[-1]','scores[-1]'),BASEBALL.replace('scores.pop()','scores.pop(0)')],['Copies the previous score instead of doubling it.','Cancels the earliest score instead of the most recent score.'],baseball_oracle,random_baseball,
        *lesson('Every operation depends only on the current valid score record.','Use a stack so cancellation and recent-score references are direct.','Push integers/D/+ results, pop on C, then sum the stack.','The stack exactly mirrors the mutable record after each valid operation.'),'O(number of operations)','O(number of operations)',3),
}
