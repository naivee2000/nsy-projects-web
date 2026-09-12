"""Bijective columns, decimal ordering, repeated DNA, and bounded stock trades."""
from itertools import combinations, groupby, permutations
from math import factorial

from .import_batch_003 import entry


def title_oracle(args):
    # Locate the length's block, then unrank ordinary zero-based base-26 digits.
    number = args[0]
    width, first, block = 1, 1, 26
    while number >= first + block:
        first += block
        width += 1
        block *= 26
    rank = number - first
    return "".join(chr(65 + rank // 26**place % 26) for place in reversed(range(width)))


def number_oracle(args):
    return sum((ord(char) - 64) * 26**place for place, char in enumerate(reversed(args[0])))


def zeroes_oracle(args):
    value = factorial(args[0])
    count = 0
    while value % 10 == 0:
        value //= 10
        count += 1
    return count


def largest_oracle(args):
    # Equal total output lengths make ordinary lexicographic maximization valid.
    best = max("".join(map(str, ordering)) for ordering in permutations(args[0]))
    return best.lstrip("0") or "0"


def dna_oracle(args):
    windows = sorted(args[0][i:i + 10] for i in range(len(args[0]) - 9))
    return [word for word, occurrences in groupby(windows) if sum(1 for _ in occurrences) >= 2]


def stock_oracle(args):
    # Enumerate every legal sequence of buy/sell days, without a trading DP.
    k, prices = args
    best = 0
    for count in range(1, min(k, len(prices) // 2) + 1):
        for days in combinations(range(len(prices)), 2 * count):
            profit = sum(prices[days[i + 1]] - prices[days[i]] for i in range(0, len(days), 2))
            best = max(best, profit)
    return best


def random_title(rng):
    return [rng.randint(1, 2**31 - 1)]


def random_number(rng):
    return [title_oracle(random_title(rng))]


def random_zeroes(rng):
    return [rng.randrange(501)]


def random_largest(rng):
    pool = [0, 1, 10, 100, 12, 121, 1212, 3, 30, 34, 9, 99, 830, 8308, 10**9]
    return [[rng.choice(pool) if rng.random() < .8 else rng.randrange(10000)
             for _ in range(rng.randint(1, 6))]]


def random_dna(rng):
    mode = rng.randrange(4)
    if mode == 0:
        return ["".join(rng.choice("ACGT") for _ in range(rng.randint(1, 70)))]
    if mode == 1:
        return ["".join(rng.choice("AC") for _ in range(rng.randint(1, 70)))]
    motif = "".join(rng.choice("ACGT") for _ in range(rng.randint(1, 10)))
    if mode == 2:
        return [motif * rng.randint(2, 9)]
    word = "".join(rng.choice("ACGT") for _ in range(10))
    return [motif + word + motif[::-1] + word]


def random_stock(rng):
    return [rng.choice([1, 2, 3, 4, 100]), [rng.randrange(11) for _ in range(rng.randint(1, 10))]]


TITLE = '''\
def column_title(column_number):
    letters = []
    while column_number:
        column_number, digit = divmod(column_number - 1, 26)
        letters.append(chr(65 + digit))
    return "".join(reversed(letters))
'''
NUMBER = '''\
def column_number(column_title):
    result = 0
    for char in column_title:
        result = result * 26 + ord(char) - 64
    return result
'''
ZEROES = '''\
def factorial_zeroes(n):
    result = 0
    while n:
        n //= 5
        result += n
    return result
'''
LARGEST = '''\
def largest_number(nums):
    from functools import cmp_to_key
    def compare(a, b):
        ab, ba = a + b, b + a
        return (ba > ab) - (ba < ab)
    words = sorted(map(str, nums), key=cmp_to_key(compare))
    if words[0] == "0":
        return "0"
    return "".join(words)
'''
DNA = '''\
def repeated_dna(s):
    codes = {"A": 0, "C": 1, "G": 2, "T": 3}
    mask = (1 << 20) - 1
    window = 0
    seen, reported = set(), set()
    result = []
    for index, char in enumerate(s):
        window = ((window << 2) | codes[char]) & mask
        if index < 9:
            continue
        if window in seen and window not in reported:
            result.append(s[index - 9:index + 1])
            reported.add(window)
        seen.add(window)
    return result
'''
NONOVERLAP_DNA = '''\
def repeated_dna(s):
    from collections import Counter
    counts = Counter(s[i:i + 10] for i in range(0, len(s) - 9, 10))
    return [word for word, count in counts.items() if count > 1]
'''
STOCK = '''\
def maximum_trade_profit(k, prices):
    if k >= len(prices) // 2:
        return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices)))
    cash = [0] * (k + 1)
    hold = [float("-inf")] * (k + 1)
    for price in prices:
        for limit in range(k, 0, -1):
            cash[limit] = max(cash[limit], hold[limit] + price)
            hold[limit] = max(hold[limit], cash[limit - 1] - price)
    return cash[k]
'''

BATCH = {
    168: entry("column_title", [("column_number", "int")], "str", ["math", "strings"],
        ["1 ≤ column_number ≤ 2^31 - 1.", "Use uppercase column labels with A=1, …, Z=26, AA=27, AB=28. There is no zero-valued letter; return the label as a string."],
        [([1], "Column 1 is A, the first single-letter label."),
         ([28], "After Z (26) comes AA (27), then AB (28). This is not ordinary base 26 with A equal to zero.")],
        [[n] for n in (2, 25, 26, 27, 52, 53, 676, 701, 702, 703, 18278, 18279)],
        TITLE, [TITLE.replace("column_number - 1", "column_number"), TITLE.replace("reversed(letters)", "letters")],
        ["Uses ordinary zero-based remainders and shifts column labels at alphabet boundaries.", "Returns least-significant letters first, reversing multi-letter labels."], title_oracle, random_title,
        ["Column letters represent digits 1 through 26, not 0 through 25.", "Subtract one before taking a remainder so the final letter maps to A through Z.", "Repeatedly divide number-1 by 26; append the remainder's letter and continue with the quotient; reverse at the end.", "At 26, the last letter is Z and the remaining quotient must be zero, not one."],
        "Subtracting one converts the current one-based digit into a zero-based remainder. Each division removes the final letter, so reverse the collected letters when finished. The independent oracle first locates the block of labels with a given length, then unranks the number within that block using ordinary positional base 26. The opposite conversion is a separate input/output contract, not a duplicate of this problem.",
        "O(log_26(column_number))", "O(log_26(column_number)), including output", difficulty=3,
        stress=[([2147483647], "FXSHRXW")]),
    171: entry("column_number", [("column_title", "str")], "int", ["math", "strings"],
        ["The label contains 1–7 uppercase English letters and represents a column from 1 through 2^31 - 1 (A through FXSHRXW in column order).", "A=1, …, Z=26. Each additional letter shifts previous positions by a factor of 26; this is not a sum of letter values."],
        [(["A"], "A is the first column, so its number is 1."),
         (["AB"], "A occupies the 26s position: 1×26 + 2 = 28.")],
        [[s] for s in ("B", "Y", "Z", "AA", "AZ", "BA", "YZ", "ZY", "ZZ", "AAA", "ZZZ", "AAAA")],
        NUMBER, [NUMBER.replace("ord(char) - 64", "ord(char) - 65"), NUMBER.replace("result * 26", "result")],
        ["Treats A as zero, which is incorrect for one-based column labels.", "Sums letter values and ignores their positional weights."], number_oracle, random_number,
        ["A letter's contribution depends on its position in the label.", "Read from left to right; each new letter multiplies the previous value by 26.", "Start at zero and update value = value×26 + (letter-'A'+1) for every letter.", "AZ is 1×26+26=52, whereas ZA is 26×26+1=677."],
        "The running value represents the entire prefix already read. Appending a letter shifts that prefix one position and adds the new one-based digit. The oracle independently sums explicit powers of 26 from right to left. Boundary cases distinguish one- and multi-letter labels, and the maximum label maps exactly to 2147483647, safely representable by the browser's JSON number format.",
        "O(len(column_title))", "O(1)", difficulty=3,
        stress=[(["FXSHRXW"], 2147483647)]),
    172: entry("factorial_zeroes", [("n", "int")], "int", ["math"],
        ["0 ≤ n ≤ 10000; 0! is 1.", "Count only consecutive zero digits at the end of n!, not zeroes elsewhere in its decimal representation. Aim for logarithmic time without constructing n!."],
        [([3], "3! is 6, whose decimal representation has no trailing zeroes."),
         ([25], "There are five multiples of 5 up to 25, and 25 supplies one additional factor of 5: the answer is 6, not 5.")],
        [[n] for n in (0, 1, 4, 5, 9, 10, 24, 26, 49, 50, 124, 125)],
        ZEROES, ['def factorial_zeroes(n):\n    return n // 5\n', 'def factorial_zeroes(n):\n    return n // 10\n'],
        ["Counts one factor per multiple of five but misses extra factors in 25, 125, and higher powers.", "Counts multiples of ten instead of pairs of factors two and five throughout the factorial."], zeroes_oracle, random_zeroes,
        ["A trailing zero comes from a factor of ten, formed by a two and a five.", "Factorials contain more factors of two than five; count every factor of five.", "Add floor(n/5), floor(n/25), floor(n/125), and so on, stopping when the quotient becomes zero.", "Repeated integer division by five computes those quotients without constructing the large factorial."],
        "Each multiple of five contributes at least one factor of five; multiples of 25 contribute another, and similarly for higher powers. There are enough twos to pair with all those fives, so their total determines the trailing zero count. The independent oracle builds the exact factorial for small inputs and repeatedly removes decimal zeroes with division by ten. Seeded comparisons cover n up to 500; the 10000 boundary is checked against 2000+400+80+16+3=2499 directly.",
        "O(log_5(n+1))", "O(1)", difficulty=5,
        stress=[([10000], 2499)]),
    179: entry("largest_number", [("nums", "list[int]")], "str", ["arrays", "strings", "sorting", "greedy"],
        ["1–100 nonnegative integers, each at most 10^9. Use every integer exactly once, keeping its digits together.", "Return the largest concatenation as a string. If all values are zero, return exactly '0', not repeated zeroes."],
        [([[10, 2]], "Putting 2 before 10 produces '210', which is larger than '102' even though 10 is numerically larger than 2."),
         ([[3, 30, 34, 5, 9]], "The best order is 9,5,34,3,30, giving '9534330'; 3 must precede 30 because '330' exceeds '303'.")],
        [[a] for a in ([121, 12], [8308, 830], [0, 0], [0], [9, 91], [432, 43243], [999999999, 1000000000], [12, 1212], [1, 10, 100], [3, 30], [34323, 3432], [0, 1, 0])],
        LARGEST, ['def largest_number(nums):\n    return "".join(map(str, sorted(nums, reverse=True))).lstrip("0") or "0"\n',
                  'def largest_number(nums):\n    return "".join(sorted(map(str, nums), reverse=True)).lstrip("0") or "0"\n'],
        ["Sorts by numeric value rather than which of two concatenation orders is larger.", "Sorts individual strings lexicographically and mishandles prefix pairs such as 12 and 121."], largest_oracle, random_largest,
        ["Choosing the largest number or the longest number first is not sufficient.", "For two strings a and b, compare a+b with b+a to decide their relative order.", "Sort using that pairwise concatenation comparator, join all strings, and normalize an all-zero result to '0'.", "Equal concatenations can use either relative order; compare the whole concatenation, not just first digits."],
        "Swapping an adjacent pair changes only a+b versus b+a, so placing the larger concatenation first cannot worsen the result. This comparison defines a consistent order (equivalently, compare each integer divided by 10^its_digit_count-1), allowing comparator-based sorting. The independent oracle enumerates every permutation of up to six values and selects the largest equal-length string; it does not reuse the sorting comparator. Output remains a string, including the 1000-digit stress case, so no large-number JSON precision is lost.",
        "O(n log n × d), d is the maximum digit count", "O(n × d), including output and sorting storage", difficulty=5,
        stress=[([[1000000000] * 100], "1000000000" * 100)]),
    187: entry("repeated_dna", [("s", "str")], "list[str]", ["strings", "sliding-window", "hash-maps", "bit-manipulation"],
        ["1–100000 characters, each A, C, G, or T.", "Return each distinct length-10 substring that occurs at least twice, in any order. Overlapping occurrences count. Each repeated sequence appears only once in the result."],
        [(["AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT"], "Both 'AAAAACCCCC' and 'CCCCCAAAAA' occur twice; no other length-10 sequence repeats."),
         (["AAAAAAAAAAAAA"], "The ten-letter sequence 'AAAAAAAAAA' starts at four overlapping positions, but is returned only once.")],
        [[s] for s in ("A", "ACGT", "AAAAAAAAA", "AAAAAAAAAA", "AAAAAAAAAAA", "AAAAAAAAAAAA", "ACGTACGTAC", "ACGTACGTACGTAC", "TTTTTTTTTTT", "CCCCCCCCCCGCCCCCCCCCC", "ACGTACGTACACGTACGTAC", "ACGTACGTAGACGTACGTAT")],
        DNA, [NONOVERLAP_DNA, DNA.replace("window in seen and window not in reported", "window in seen")],
        ["Looks only at disjoint ten-character blocks and misses overlapping repeats.", "Appends a sequence again on every occurrence after the first instead of returning distinct repeated sequences."], dna_oracle, random_dna,
        ["Every starting position can define a window, even if it overlaps a previous occurrence.", "Track windows seen before and separately track those already included in the answer.", "Encode each nucleotide in two bits; retain the last twenty bits. After ten characters, report a previously seen code only if it has not been reported yet.", "Leading A characters encode as zero, so wait until the window really contains ten characters before testing the code."],
        "A fixed ten-character DNA window fits exactly in twenty bits; the encoding has no collisions among windows of that length. Shifting in each new character and masking discards the oldest one. Separate seen and reported sets distinguish the first, second, and later occurrences. The independent oracle materializes and sorts all ten-character slices, then groups equal adjacent strings. Its comparisons include overlapping windows and preserve the requirement that each answer appear only once.",
        "O(len(s))", "O(min(len(s), 4^10)), including stored codes and output", difficulty=5,
        stress=[(["A" * 100000], ["A" * 10])]),
    188: entry("maximum_trade_profit", [("k", "int"), ("prices", "list[int]")], "int", ["arrays", "dynamic-programming"],
        ["1 ≤ k ≤ 100; prices has 1–1000 daily prices, each from 0 to 1000.", "Make at most k buy-then-sell transactions, holding at most one share at a time. Transactions need not be consecutive, and doing nothing is allowed. There is no fee or cooldown."],
        [([2, [2, 4, 1]], "Buy at 2 and sell at 4 for profit 2. A second transaction is optional and cannot improve the result."),
         ([2, [3, 2, 6, 5, 0, 3]], "Buy at 2 and sell at 6, then buy at 0 and sell at 3, for total profit 4+3=7.")],
        [[k, values] for k, values in ((1, [5]), (100, [0]), (1, [1, 2, 3, 4]), (2, [4, 3, 2, 1]),
            (1, [1, 5, 2, 8]), (2, [1, 5, 2, 8]), (3, [0, 3, 0, 3, 0, 3]), (2, [0, 3, 0, 3, 0, 3]),
            (100, [2, 2, 2]), (1, [0, 1000]), (2, [3, 1, 4, 0, 8]), (3, [1, 2, 1, 2, 1, 2, 1, 2]))],
        STOCK, ['def maximum_trade_profit(k, prices):\n    return sum(max(0, b-a) for a, b in zip(prices, prices[1:]))\n',
                STOCK.replace("    if k >=", "    k = min(k, 2)\n    if k >=", 1)],
        ["Takes every profitable rise even when that needs more than k transactions.", "Hard-codes at most two transactions and loses profit when the input permits three or more."], stock_oracle, random_stock,
        ["The best action depends on both whether a share is held and the transaction budget remaining.", "Maintain cash and holding states for each allowed transaction count.", "For each price and budget j: cash[j]=max(old_cash[j],old_hold[j]+price); hold[j]=max(old_hold[j],old_cash[j-1]-price). Return cash[k].", "Update budgets downward to retain previous-day dependencies. If k≥floor(n/2), the cap cannot restrict profit and every positive daily rise can be taken."],
        "cash[j] is the best realized profit with no stock and at most j buys; hold[j] is the best balance while holding with at most j buys. Selling preserves the budget, while buying uses one more than the previous cash state. Downward budget updates read the previous day's smaller-budget cash. With enough budget, sum positive adjacent rises instead. The independent oracle enumerates all even-length choices of transaction days and pairs them as buy/sell actions, selecting the best legal profit. Excluding same-day sell/buy pairs in this enumeration loses no optimum because such pairs can be merged without changing profit. The configurable budget is a distinct contract from the existing one- and two-trade exercises; tests require more than two trades as well as restrictive one-trade behavior.",
        "O(n × min(k,n)); O(n) when the transaction cap is nonbinding", "O(k) for bounded trading; O(1) for the unlimited shortcut", difficulty=8,
        stress=[([100, [0, 1000] * 500], 100000), ([100, [1000] * 1000], 0)]),
}
BATCH[187]["comparator"] = "unordered"
BATCH[188]["prerequisites"] = ["dynamic-programming"]
