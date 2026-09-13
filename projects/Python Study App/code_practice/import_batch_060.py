"""Reviewed string, scheduling, array, and factorization workbook imports."""
from collections import Counter
from itertools import combinations

from .import_batch_003 import entry


def bold_oracle(args):
    text, words = args
    marked = [False] * len(text)
    for start in range(len(text)):
        for word in words:
            if text.startswith(word, start):
                marked[start:start + len(word)] = [True] * len(word)
    out, index = [], 0
    while index < len(text):
        if marked[index]:
            end = index
            while end < len(text) and marked[end]: end += 1
            out.extend(("<b>", text[index:end], "</b>")); index = end
        else:
            out.append(text[index]); index += 1
    return "".join(out)


def scheduler_oracle(args):
    tasks, cooldown = args
    counts = Counter(tasks)
    ready = {task: 0 for task in counts}
    time = 0
    while counts:
        choices = [task for task in counts if ready[task] <= time]
        if choices:
            task = max(choices, key=lambda item: (counts[item], item))
            counts[task] -= 1
            ready[task] = time + cooldown + 1
            if counts[task] == 0: del counts[task]
        time += 1
    return time


def distance_oracle(args):
    arrays = args[0]
    return max(abs(left - right) for i, first in enumerate(arrays) for j, second in enumerate(arrays)
               if i < j for left in first for right in second)


def factor_oracle(args):
    number = args[0]
    if number < 10: return number
    best = None
    def search(remaining, digits, minimum):
        nonlocal best
        if remaining == 1:
            value = int("".join(map(str, sorted(digits))))
            best = value if best is None else min(best, value)
            return
        for digit in range(minimum, 10):
            if remaining % digit == 0:
                search(remaining // digit, digits + [digit], digit)
    search(number, [], 2)
    return 0 if best is None or best >= 2**31 else best


def product_oracle(args):
    return max(a * b * c for a, b, c in combinations(args[0], 3))


def random_bold(rng):
    text = "".join(rng.choice("abcxyz") for _ in range(rng.randint(1, 25)))
    words = ["".join(rng.choice("abcxyz") for _ in range(rng.randint(1, 5))) for _ in range(rng.randint(1, 6))]
    return [text, words]


def random_tasks(rng):
    return [[rng.choice("ABCDE") for _ in range(rng.randint(1, 18))], rng.randint(0, 5)]


def random_arrays(rng):
    arrays = []
    for _ in range(rng.randint(2, 7)):
        row = sorted(rng.randint(-30, 30) for _ in range(rng.randint(1, 8)))
        arrays.append(row)
    return [arrays]


def random_factor(rng): return [rng.randint(0, 2_000)]
def random_product(rng): return [[rng.randint(-100, 100) for _ in range(rng.randint(3, 30))]]


BOLD = '''\
def add_bold_tags(s, words):
    marked = [False] * len(s)
    for start in range(len(s)):
        for word in words:
            if s.startswith(word, start):
                for index in range(start, start + len(word)):
                    marked[index] = True
    answer = []
    index = 0
    while index < len(s):
        if not marked[index]:
            answer.append(s[index]); index += 1
            continue
        end = index
        while end < len(s) and marked[end]: end += 1
        answer.append('<b>' + s[index:end] + '</b>')
        index = end
    return ''.join(answer)
'''

SCHEDULER = '''\
def least_task_intervals(tasks, n):
    from collections import Counter
    counts = Counter(tasks)
    largest = max(counts.values())
    tied = sum(count == largest for count in counts.values())
    return max(len(tasks), (largest - 1) * (n + 1) + tied)
'''

DISTANCE = '''\
def maximum_array_distance(arrays):
    smallest, largest = arrays[0][0], arrays[0][-1]
    answer = 0
    for row in arrays[1:]:
        answer = max(answer, abs(row[-1] - smallest), abs(largest - row[0]))
        smallest = min(smallest, row[0])
        largest = max(largest, row[-1])
    return answer
'''

FACTOR = '''\
def minimum_factor_digits(num):
    if num < 10:
        return num
    digits = []
    for digit in range(9, 1, -1):
        while num % digit == 0:
            digits.append(digit)
            num //= digit
    if num != 1:
        return 0
    answer = int(''.join(map(str, reversed(digits))))
    return answer if answer < 2**31 else 0
'''

PRODUCT = '''\
def maximum_three_product(nums):
    nums = sorted(nums)
    return max(nums[-1] * nums[-2] * nums[-3], nums[0] * nums[1] * nums[-1])
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial], editorial


BATCH = {
    616: entry('add_bold_tags', [('s', 'str'), ('words', 'list[str]')], 'str', ['strings', 'intervals'],
        ['1 <= len(s) <= 1,000; 1 <= len(words) <= 100.', 'Wrap every matching substring; merge overlapping or adjacent bold regions.'],
        [(['abcxyz123', ['abc', '123']], 'The two separated matches receive separate bold regions.'),
         (['aaabbcc', ['aaa', 'aab', 'bc']], 'Overlapping and adjacent matches merge into one region covering aaabbc.')],
        [[s, words] for s, words in (('a', ['a']), ('a', ['b']), ('abc', ['abc']), ('abc', ['b']), ('aaaa', ['aa']), ('abcabc', ['abc']), ('abc', ['a','b']), ('abcdef', ['bc','de']), ('xyzabc', ['abc','xyz']), ('mississippi', ['iss','sip']), ('abababa', ['aba']), ('abcdef', ['x','y']))],
        BOLD, [BOLD.replace('while end < len(s) and marked[end]: end += 1', 'end = index + 1'), BOLD.replace("'<b>' + s[index:end] + '</b>'", "'<b>' + s[index:end]")],
        ['Stops each bold region after one character.', 'Omits the closing bold tag.'], bold_oracle, random_bold,
        *lesson('Treat matched characters as a union of intervals.', 'Mark every character covered by any match, then emit maximal marked runs.', 'Find all starts, mark spans, and surround each consecutive true run once.', 'A boolean coverage array automatically merges overlap and adjacency while preserving unmatched characters.'), 'O(len(s) * words * word_length)', 'O(len(s))', 5),
    621: entry('least_task_intervals', [('tasks', 'list[str]'), ('n', 'int')], 'int', ['greedy', 'hash-maps', 'scheduling'],
        ['1 <= len(tasks) <= 10,000; task labels are uppercase letters; 0 <= n <= 100.', 'Equal tasks must be separated by at least n intervening intervals; idle intervals are allowed.'],
        [([['A','A','A','B','B','B'], 2], 'Arrange A,B,idle,A,B,idle,A,B for eight intervals.'),
         ([['A','A','A','B','B','B'], 0], 'With no cooldown, all six tasks run consecutively.')],
        [[tasks, n] for tasks, n in ((['A'],2), (['A','A'],1), (['A','B'],3), (['A','A','B'],2), (['A','A','A','B'],2), (['A','A','B','B'],2), (['A','A','B','B','C','C'],2), (['A','A','A','A','B','C'],2), (['A','B','C','D'],10), (['A','A','A','B','B','C'],1), (['A','A','A','B','B','B','C','C'],2), (['A','A','B','C','D'],3))],
        SCHEDULER, [SCHEDULER.replace('+ tied', '+ 1'), SCHEDULER.replace('max(len(tasks), ', '') .replace(' + tied)', ' + tied')],
        ['Counts only one task tied for maximum frequency.', 'Forgets that abundant other tasks can fill every idle slot.'], scheduler_oracle, random_tasks,
        *lesson('The most frequent tasks create a frame of cooldown gaps.', 'Count the tallest frequency columns and how many share that height.', 'Return max(task count, (largest-1)*(n+1)+number_of_largest).', 'All but the final copies of the most frequent tasks require full cooldown frames; other tasks fill those frames before idle time is needed.'), 'O(number of tasks)', 'O(number of task types)', 5),
    624: entry('maximum_array_distance', [('arrays', 'list[list[int]]')], 'int', ['arrays', 'greedy'],
        ['2 <= len(arrays) <= 100,000; every inner array is nonempty and sorted.', 'Choose values from two different arrays and maximize their absolute difference.'],
        [([[[1,2,3],[4,5],[1,2,3]]], 'Choose 1 from the first array and 5 from the second, giving distance four.'),
         ([[[-10,-5],[0],[5,9]]], 'Choose -10 and 9 from different arrays, giving nineteen.')],
        [[arrays] for arrays in (([1],[2]), ([1,5],[2,3]), ([-2,-1],[0,1]), ([1,2],[3,4],[5,6]), ([0],[0]), ([-10,10],[0]), ([1,100],[2,99]), ([-5,-4],[-3],[-2,-1]), ([1],[1],[2]), ([1,2,3],[1,2,3]), ([-100],[0],[100]), ([2,4],[1,3],[5,7]))],
        DISTANCE, [DISTANCE.replace('arrays[1:]', 'arrays[2:]'), DISTANCE.replace('abs(row[-1] - smallest)', 'abs(row[0] - smallest)')],
        ['Skips the second array.', 'Compares minima instead of the current maximum to the earlier minimum.'], distance_oracle, random_arrays,
        *lesson('Only each sorted array’s endpoints can maximize distance.', 'Before incorporating a new array, compare its endpoints with extrema from earlier arrays.', 'Track global smallest/largest; test new max-old min and old max-new min.', 'Comparing before updating guarantees the two selected values come from different arrays.'), 'O(number of arrays)', 'O(1)', 3),
    625: entry('minimum_factor_digits', [('num', 'int')], 'int', ['math', 'greedy'],
        ['0 <= num <= 2^31 - 1.', 'Return the smallest positive integer whose decimal digits multiply to num, or zero if none fits signed 32-bit.'],
        [([48], 'Factor 48 as 6 times 8; arranging digits increasingly gives 68.'), ([15], 'Digits 3 and 5 produce the minimum answer 35.')],
        [[n] for n in (0,1,2,7,10,11,12,36,100,128,150,997,2_000)], FACTOR,
        [FACTOR.replace('range(9, 1, -1)', 'range(2, 10)'), FACTOR.replace('if num != 1:\n        return 0', 'if num != 1:\n        return num')],
        ['Extracts small factors first and can create more digits than necessary.', 'Returns a digit string even when a prime factor larger than nine remains.'], factor_oracle, random_factor,
        *lesson('Every output digit must be a factor from two through nine.', 'Extract larger digits first to minimize digit count, then sort them increasingly.', 'Repeatedly divide by 9 down to 2; reject leftover factors and overflow.', 'Fewer digits always make a smaller positive integer; among equal lengths, ascending digits are smallest.'), 'O(log num)', 'O(log num)', 5),
    628: entry('maximum_three_product', [('nums', 'list[int]')], 'int', ['arrays', 'sorting'],
        ['3 <= len(nums) <= 10,000; -1,000 <= nums[i] <= 1,000.', 'Return the maximum product of any three values at distinct indices.'],
        [([[1,2,3]], 'The only triple has product six.'), ([[-10,-10,5,2]], 'Two negative tens and positive five produce 500.')],
        [[[1,1,1]], [[0,0,0]], [[-1,-2,-3]], [[-1,-2,3]], [[-5,-4,-3,-2]], [[1,2,3,4]], [[-10,-10,1,2]], [[-3,-2,-1,0,1]], [[5,5,5,1]], [[-100,1,2,3,4]], [[-2,-2,0,1]], [[10,-9,-8,7,6]]],
        PRODUCT, [PRODUCT.replace('return max(nums[-1] * nums[-2] * nums[-3], nums[0] * nums[1] * nums[-1])', 'return nums[-1] * nums[-2] * nums[-3]'), PRODUCT.replace('nums = sorted(nums)', 'nums = list(nums)')],
        ['Considers only the three largest values and misses two large negatives.', 'Assumes input order is already sorted.'], product_oracle, random_product,
        *lesson('A maximum product uses either three large positives or two very negative values and one large positive.', 'Sort once and compare those two candidate products.', 'Return max(last three product, first two times last).', 'Any negative pair is maximized in magnitude by the two smallest values; otherwise the three largest values dominate.'), 'O(n log n)', 'O(n)', 3),
}
