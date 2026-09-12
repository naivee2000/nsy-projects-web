"""Word positions, rotated numerals, cyclic strings, intervals, factors, and DP."""
from itertools import combinations_with_replacement, product
from math import prod

from .import_batch_003 import entry


ROTATE = {"0": "0", "1": "1", "6": "9", "8": "8", "9": "6"}


def word_distance_oracle(args):
    words, first, second = args
    left = [index for index, word in enumerate(words) if word == first]
    right = [index for index, word in enumerate(words) if word == second]
    return min(abs(i - j) for i in left for j in right)


def word_distance_three_oracle(args):
    words, first, second = args
    positions = [index for index, word in enumerate(words) if word == first]
    if first == second:
        return min(b - a for a, b in zip(positions, positions[1:]))
    other = [index for index, word in enumerate(words) if word == second]
    return min(abs(i - j) for i in positions for j in other)


def is_strobogrammatic_oracle(args):
    text = args[0]
    return all(char in ROTATE and ROTATE[char] == text[-1 - index]
               for index, char in enumerate(text))


def strobogrammatic_list_oracle(args):
    length = args[0]
    half = length // 2
    pairs = (("0", "0"), ("1", "1"), ("6", "9"), ("8", "8"), ("9", "6"))
    answers = []
    for chosen in product(pairs, repeat=half):
        if length > 1 and chosen and chosen[0][0] == "0":
            continue
        left = "".join(pair[0] for pair in chosen)
        right = "".join(pair[1] for pair in reversed(chosen))
        if length % 2:
            answers.extend(left + middle + right for middle in "018")
        else:
            answers.append(left + right)
    return answers


def strobogrammatic_range_oracle(args):
    low, high = map(int, args)
    return sum(is_strobogrammatic_oracle([str(value)]) for value in range(low, high + 1))


def shifted_oracle(args):
    groups = []
    for text in args[0]:
        for group in groups:
            first = group[0]
            if len(first) == len(text) and any(
                    all(chr((ord(char) - 97 + shift) % 26 + 97) == other
                        for char, other in zip(first, text)) for shift in range(26)):
                group.append(text)
                break
        else:
            groups.append([text])
    return groups


def meetings_oracle(args):
    intervals = args[0]
    return all(max(a[0], b[0]) >= min(a[1], b[1])
               for index, a in enumerate(intervals) for b in intervals[index + 1:])


def factors_oracle(args):
    number = args[0]
    factors = [value for value in range(2, number) if number % value == 0]
    answers = []
    for length in range(2, number.bit_length() + 1):
        for chosen in combinations_with_replacement(factors, length):
            value = prod(chosen)
            if value == number:
                answers.append(list(chosen))
    return answers


def paint_oracle(args):
    costs = args[0]
    return min(sum(costs[index][color] for index, color in enumerate(colors))
               for colors in product(range(3), repeat=len(costs))
               if all(colors[index] != colors[index - 1] for index in range(1, len(colors))))


def digital_root_oracle(args):
    value = args[0]
    while value >= 10:
        value = sum(map(int, str(value)))
    return value


def random_word_distance(rng):
    alphabet = ["a", "b", "c", "d"]
    words = [rng.choice(alphabet) for _ in range(rng.randint(2, 30))]
    present = list(set(words))
    if len(present) < 2:
        words[-1] = "b" if words[0] != "b" else "a"
        present = list(set(words))
    first, second = rng.sample(present, 2)
    return [words, first, second]


def random_word_distance_three(rng):
    alphabet = ["a", "b", "c", "d"]
    words = [rng.choice(alphabet) for _ in range(rng.randint(2, 30))]
    present = list(set(words))
    if rng.random() < .4:
        repeated = [word for word in present if words.count(word) >= 2]
        if not repeated:
            words.append(words[0])
            repeated = [words[0]]
        first = second = rng.choice(repeated)
    else:
        if len(present) < 2:
            words.append("b" if words[0] != "b" else "a")
            present = list(set(words))
        first, second = rng.sample(present, 2)
    return [words, first, second]


def random_strobogrammatic(rng):
    length = rng.randint(1, 50)
    first = rng.choice("123456789")
    return [first + "".join(rng.choice("0123456789") for _ in range(length - 1))]


def random_strobogrammatic_length(rng):
    return [rng.randint(1, 8)]


def random_strobogrammatic_range(rng):
    low = rng.randint(0, 5000)
    high = rng.randint(low, min(9999, low + 1000))
    return [str(low), str(high)]


def random_shifted(rng):
    return [["".join(rng.choice("abcdefghijklmnopqrstuvwxyz")
                     for _ in range(rng.randint(1, 8))) for _ in range(rng.randint(1, 20))]]


def random_meetings(rng):
    intervals = []
    for _ in range(rng.randint(0, 20)):
        start = rng.randint(0, 100)
        intervals.append([start, start + rng.randint(1, 20)])
    return [intervals]


def random_factors(rng):
    return [rng.randint(1, 100)]


def random_paint(rng):
    return [[[rng.randint(1, 20) for _ in range(3)] for _ in range(rng.randint(1, 8))]]


def random_digital_root(rng):
    return [rng.randint(0, 2**31 - 1)]


WORD_DISTANCE = '''\
def shortest_word_distance(words, word1, word2):
    latest_first = latest_second = -1
    best = len(words)
    for index, word in enumerate(words):
        if word == word1:
            latest_first = index
        elif word == word2:
            latest_second = index
        if latest_first >= 0 and latest_second >= 0:
            best = min(best, abs(latest_first - latest_second))
    return best
'''
WORD_DISTANCE_THREE = '''\
def shortest_word_distance_allow_same(words, word1, word2):
    best = len(words)
    if word1 == word2:
        previous = -1
        for index, word in enumerate(words):
            if word == word1:
                if previous >= 0:
                    best = min(best, index - previous)
                previous = index
        return best
    latest_first = latest_second = -1
    for index, word in enumerate(words):
        if word == word1:
            latest_first = index
        elif word == word2:
            latest_second = index
        if latest_first >= 0 and latest_second >= 0:
            best = min(best, abs(latest_first - latest_second))
    return best
'''
IS_STROBO = '''\
def is_strobogrammatic(num):
    rotated = {"0": "0", "1": "1", "6": "9", "8": "8", "9": "6"}
    left, right = 0, len(num) - 1
    while left <= right:
        if num[left] not in rotated or rotated[num[left]] != num[right]:
            return False
        left += 1
        right -= 1
    return True
'''
LIST_STROBO = '''\
def strobogrammatic_numbers(n):
    pairs = (("0", "0"), ("1", "1"), ("6", "9"), ("8", "8"), ("9", "6"))
    def build(length, outer):
        if length == 0:
            return [""]
        if length == 1:
            return ["0", "1", "8"]
        answers = []
        for middle in build(length - 2, False):
            for left, right in pairs:
                if outer and left == "0":
                    continue
                answers.append(left + middle + right)
        return answers
    return build(n, True)
'''
RANGE_STROBO = '''\
def count_strobogrammatic_range(low, high):
    pairs = (("0", "0"), ("1", "1"), ("6", "9"), ("8", "8"), ("9", "6"))
    def build(length, total):
        if length == 0:
            return [""]
        if length == 1:
            return ["0", "1", "8"]
        answers = []
        for middle in build(length - 2, total):
            for left, right in pairs:
                if length == total and left == "0":
                    continue
                answers.append(left + middle + right)
        return answers
    answer = 0
    for length in range(len(low), len(high) + 1):
        for value in build(length, length):
            if (length > len(low) or value >= low) and (length < len(high) or value <= high):
                answer += 1
    return answer
'''
SHIFTED = '''\
def group_shifted_strings(strings):
    groups = {}
    for text in strings:
        key = tuple((ord(text[index]) - ord(text[index - 1])) % 26
                    for index in range(1, len(text)))
        groups.setdefault(key, []).append(text)
    return list(groups.values())
'''
MEETINGS = '''\
def can_attend_all_meetings(intervals):
    ordered = sorted(intervals)
    return all(ordered[index - 1][1] <= ordered[index][0]
               for index in range(1, len(ordered)))
'''
FACTORS = '''\
def factor_combinations(n):
    answers, path = [], []
    def search(start, remaining):
        divisor = start
        while divisor * divisor <= remaining:
            if remaining % divisor == 0:
                path.append(divisor)
                answers.append(path + [remaining // divisor])
                search(divisor, remaining // divisor)
                path.pop()
            divisor += 1
    search(2, n)
    return answers
'''
PAINT = '''\
def minimum_paint_cost(costs):
    previous = costs[0][:]
    for red, blue, green in costs[1:]:
        previous = [red + min(previous[1], previous[2]),
                    blue + min(previous[0], previous[2]),
                    green + min(previous[0], previous[1])]
    return min(previous)
'''
DIGITAL_ROOT = '''\
def add_digits(num):
    return 0 if num == 0 else 1 + (num - 1) % 9
'''


STROBO_15_COUNT = 3 + sum(4 * 5 ** ((length - 2) // 2) * (3 if length % 2 else 1)
                          for length in range(2, 16))


BATCH = {
    243: entry("shortest_word_distance", [("wordsDict", "list[str]"), ("word1", "str"), ("word2", "str")], "int", ["arrays", "strings", "two-pointers"],
        ["words contains 2–30000 lowercase words of length 1–10. word1 and word2 are distinct and both occur in words.", "Return the minimum absolute difference between an occurrence index of word1 and an occurrence index of word2."],
        [([["practice", "makes", "perfect", "coding", "makes"], "coding", "practice"], "The selected occurrences are at indices 3 and 0, so their distance is 3."), ([["practice", "makes", "perfect", "coding", "makes"], "makes", "coding"], "The occurrence of 'makes' at index 4 is adjacent to 'coding' at index 3, giving distance 1.")],
        [[words, a, b] for words, a, b in ((["a", "b"], "a", "b"), (["a", "x", "b"], "a", "b"), (["a", "b", "a"], "a", "b"), (["b", "a", "b"], "a", "b"), (["a", "x", "a", "b"], "a", "b"), (["a", "b", "x", "b"], "a", "b"), (["z", "a", "z", "b"], "a", "b"), (["aa", "bb", "aa", "cc"], "bb", "cc"), (["a", "c", "b", "c", "a"], "a", "b"), (["x", "y"] * 5, "x", "y"), (["a"] * 10 + ["b"], "a", "b"), (["a", "b"] + ["a"] * 10, "a", "b"))],
        WORD_DISTANCE, [WORD_DISTANCE.replace("best = min(best, abs(latest_first - latest_second))", "return abs(latest_first - latest_second)"), WORD_DISTANCE.replace("latest_second = index", "latest_first = index")],
        ["Returns the first pair encountered rather than continuing to find a closer later pair.", "Updates both positions in separate branches even though the source contract requires distinct words, corrupting a position on unrelated logic."], word_distance_oracle, random_word_distance,
        ["The closest pair involving the current occurrence uses the most recent occurrence of the other word.", "Track the latest index of each target while scanning once.", "After either index changes, update the best absolute gap when both have been seen.", "Do not stop at the first pair; later occurrences can be closer."],
        "For any current target occurrence, older occurrences of the other target are farther away than its latest occurrence. Tracking two latest indices therefore considers every potentially optimal cross-pair in one pass. The independent oracle lists every occurrence and compares their Cartesian product.", "O(n)", "O(1)", difficulty=3,
        stress=[([["a"] * 29999 + ["b"], "a", "b"], 1)]),
    245: entry("shortest_word_distance_allow_same", [("wordsDict", "list[str]"), ("word1", "str"), ("word2", "str")], "int", ["arrays", "strings", "two-pointers"],
        ["words contains 1–100000 lowercase words of length 1–10. Both targets occur; if they are equal, that word occurs at least twice.", "Return the minimum index distance between two INDIVIDUAL occurrences. When word1==word2, an occurrence cannot be paired with itself."],
        [([["practice", "makes", "perfect", "coding", "makes"], "makes", "coding"], "The targets at indices 4 and 3 are adjacent, so the answer is 1."), ([["practice", "makes", "perfect", "coding", "makes"], "makes", "makes"], "The two distinct 'makes' occurrences are at indices 1 and 4, so the distance is 3.")],
        [[words, a, b] for words, a, b in ((["a", "a"], "a", "a"), (["a", "x", "a"], "a", "a"), (["a", "a", "a"], "a", "a"), (["a", "b"], "a", "b"), (["a", "b", "a"], "a", "b"), (["a", "x", "b", "a"], "a", "b"), (["b", "a", "b"], "a", "b"), (["x", "a", "x", "x", "a"], "x", "x"), (["aa", "bb", "aa"], "aa", "aa"), (["c", "a", "b", "c"], "a", "b"), (["a"] * 5, "a", "a"), (["a", "b", "c", "a", "b"], "a", "b"))],
        WORD_DISTANCE_THREE, [WORD_DISTANCE.replace("def shortest_word_distance(", "def shortest_word_distance_allow_same("), WORD_DISTANCE_THREE.replace("previous = index", "previous = -1")],
        ["Uses the distinct-target algorithm, which pairs an occurrence with itself when both target strings are equal.", "For equal targets, discards each previous occurrence and never measures the gap between consecutive occurrences."], word_distance_three_oracle, random_word_distance_three,
        ["First decide whether the two target strings are equal.", "For distinct targets, track both latest positions. For one repeated target, track its previous occurrence only.", "On each matching repeated word, measure index-previous before replacing previous. Otherwise use the two-target scan.", "The guarantee refers to two individual occurrences, so a same-word answer is always positive."],
        "The distinct-target branch is the ordinary two-latest-index scan. In the equal-target branch, the minimum gap must occur between consecutive occurrences in occurrence order; skipping an intervening occurrence only increases the distance. The independent oracle explicitly lists positions and either checks consecutive gaps or every cross-target pair.", "O(n)", "O(1)", difficulty=5,
        stress=[([["a"] * 100000, "a", "a"], 1)]),
    246: entry("is_strobogrammatic", [("num", "str")], "bool", ["strings", "two-pointers", "hash-maps"],
        ["num contains 1–50 decimal digits and has no leading zero unless it is exactly '0'.", "After a 180-degree rotation, 0,1,8 map to themselves and 6/9 exchange. Digits 2,3,4,5,7 are invalid."],
        [(["69"], "Rotating and reversing swaps 6 with 9 and 9 with 6, producing the same string."), (["962"], "Digit 2 has no valid 180-degree rotation, so the number is not strobogrammatic.")],
        [[value] for value in ("0", "1", "8", "6", "9", "11", "88", "96", "101", "609", "818", "619", "123", "1001")],
        IS_STROBO, [IS_STROBO.replace('"6": "9", "8": "8", "9": "6"', '"6": "6", "8": "8", "9": "9"'), 'def is_strobogrammatic(num):\n    return num == num[::-1]\n'],
        ["Leaves 6 and 9 unchanged instead of rotating them into each other.", "Checks only ordinary palindromicity and ignores the digit rotation mapping."], is_strobogrammatic_oracle, random_strobogrammatic,
        ["Rotation reverses position order as well as changing certain digits.", "Compare symmetric characters with a map 0→0,1→1,6→9,8→8,9→6.", "Move two pointers inward; reject an unmapped left digit or a mapped value unequal to the right digit.", "The middle digit of an odd-length number must be 0, 1, or 8."],
        "A 180-degree rotation sends the leftmost digit to the rightmost position. Each symmetric pair must therefore match the five-entry rotation map. Two pointers verify all pairs in linear time. The independent oracle constructs the same condition position-by-position from an independently declared mapping.", "O(len(num))", "O(1)", difficulty=3),
    247: entry("strobogrammatic_numbers", [("n", "int")], "list[str]", ["recursion", "backtracking", "strings"],
        ["1 ≤ n ≤ 14.", "Return every length-n strobogrammatic decimal string in any order, with no leading zero. For n=1, '0' is valid."],
        [([2], "The four valid outer pairs without a leading zero are 11,69,88,96."), ([1], "The only one-digit values unchanged by rotation are 0,1,8.")],
        [[length] for length in range(3, 15)],
        LIST_STROBO, [LIST_STROBO.replace("if outer and left == \"0\":", "if False:"), LIST_STROBO.replace('("6", "9"), ', "")],
        ["Allows a zero outer pair and returns strings with forbidden leading zeroes.", "Omits the 6/9 rotation pair and therefore misses valid numbers such as 69 and 96."], strobogrammatic_list_oracle, random_strobogrammatic_length,
        ["Valid outer digit pairs are 00,11,69,88,96, but 00 is forbidden at the outermost layer when n>1.", "Build from the center outward: the empty center serves even lengths and 0/1/8 serve odd lengths.", "Recursively build length n-2 middles, wrap each in valid pairs, and suppress outer 00.", "Return all constructions; the output count grows exponentially and order does not matter."],
        "Every valid number decomposes uniquely into an outer rotation pair and a strobogrammatic middle. The two center base cases cover even and odd lengths. Excluding 00 only at the outermost call prevents leading zeroes without forbidding internal zero pairs. The independent oracle selects all half-string pair products iteratively and mirrors them around each permitted center.", "O(n × output size)", "O(n × output size) including returned strings", difficulty=5),
    248: entry("count_strobogrammatic_range", [("low", "str"), ("high", "str")], "int", ["recursion", "backtracking", "strings"],
        ["low and high are canonical decimal strings of length 1–15 with 0 ≤ low ≤ high and no leading zero except '0'.", "Count strobogrammatic integers in the inclusive interval [low,high]. Compare long bounds without converting them to fixed-width machine integers."],
        [(["50", "100"], "The included strobogrammatic values are 69,88,96, so the count is 3."), (["0", "0"], "Zero rotates to itself and both inclusive bounds equal zero, so the count is 1.")],
        [[low, high] for low, high in (("0", "1"), ("1", "1"), ("2", "8"), ("6", "9"), ("10", "11"), ("11", "11"), ("12", "68"), ("69", "96"), ("100", "1000"), ("101", "101"), ("808", "818"), ("1000", "10000"))],
        RANGE_STROBO, [RANGE_STROBO.replace("value >= low", "value > low"), RANGE_STROBO.replace("    return answer\n", "    return answer - (1 if low == \"0\" else 0)\n")],
        ["Treats the lower bound as exclusive and omits a strobogrammatic value equal to low.", "Incorrectly removes zero even when it lies in the inclusive range."], strobogrammatic_range_oracle, random_strobogrammatic_range,
        ["Generate only candidates whose lengths lie between the bound lengths.", "Use the same center-out construction as the generation problem, excluding leading zeroes.", "For boundary-length strings compare lexicographically with low/high; equal-length decimal strings share numeric order.", "Both endpoints are inclusive, and zero is a valid one-character candidate."],
        "Generate each strobogrammatic candidate once for every relevant length. Length alone accepts candidates strictly inside the bound lengths; equal-length candidates use lexicographic comparisons, avoiding machine-width concerns. The independent oracle enumerates each ordinary integer only for bounded seeded ranges and directly applies the rotation predicate. A closed-form full-domain fixture checks all lengths through 15.", "O(total generated candidates through 15 digits)", "O(total generated candidates through 15 digits)", difficulty=8,
        stress=[(["0", "999999999999999"], STROBO_15_COUNT)]),
    249: entry("group_shifted_strings", [("strings", "list[str]")], "list[list[str]]", ["strings", "hash-maps", "modular-arithmetic"],
        ["strings contains 1–200 lowercase strings, each of length 1–50; duplicate strings are retained as separate input occurrences.", "Group strings that differ by adding the same alphabetic shift modulo 26 to every position. Group order and order within each group do not matter."],
        [([["abc", "bcd", "acef", "xyz", "az", "ba", "a", "z"]], "The groups are [abc,bcd,xyz], [az,ba], [acef], and [a,z]; wraparound makes az equivalent to ba."), ([["a"]], "A single string forms one group by itself.")],
        [[strings] for strings in (["a", "z"], ["az", "ba"], ["abc", "bcd"], ["abc", "ace"], ["aa", "bb", "zz"], ["ab", "ac"], ["a", "a"], ["xyz", "yza", "zab"], ["az", "za"], ["ab", "bc", "cd", "ace"], ["aaa", "bbb", "aba"], ["z", "zz", "zzz"])],
        SHIFTED, [SHIFTED.replace("% 26", ""), 'def group_shifted_strings(strings):\n    groups = {}\n    for text in strings: groups.setdefault(len(text), []).append(text)\n    return list(groups.values())\n'],
        ["Uses raw adjacent differences and fails to recognize wraparound-equivalent strings such as az and ba.", "Groups solely by length even when strings require different position-wise shifts."], shifted_oracle, random_shifted,
        ["A global shift preserves the difference between every adjacent pair modulo 26.", "Use the tuple of cyclic adjacent differences as a canonical group key; all one-letter strings share the empty key.", "For each string compute (s[i]-s[i-1]) mod 26 and append it under that tuple.", "Modulo is essential at z/a wraparound, and duplicate input strings should remain duplicated in their group."],
        "Two equal-length strings share a shifting sequence exactly when all corresponding adjacent differences match modulo 26. This key is invariant under any global shift and uniquely identifies the sequence. The independent oracle tries all 26 shifts against a representative of each existing group instead of computing difference keys.", "O(total input characters)", "O(total input characters) including output", difficulty=5),
    252: entry("can_attend_all_meetings", [("intervals", "list[list[int]]")], "bool", ["intervals", "sorting", "arrays"],
        ["intervals contains 0–10000 pairs [start,end] with 0 ≤ start < end ≤ 10^6.", "Meetings are half-open for overlap purposes: one ending exactly when another starts does not overlap. Input order is arbitrary."],
        [([[[0, 30], [5, 10], [15, 20]]], "The meeting [5,10] starts before [0,30] ends, so the person cannot attend both."), ([[[7, 10], [2, 4]]], "After sorting, [2,4] ends before [7,10] begins, so both can be attended.")],
        [[intervals] for intervals in ([], [[0, 1]], [[0, 1], [1, 2]], [[0, 2], [1, 3]], [[5, 6], [0, 5]], [[5, 10], [0, 6]], [[0, 10], [2, 3]], [[2, 3], [0, 10]], [[0, 1], [2, 3], [1, 2]], [[0, 3], [3, 5], [2, 4]], [[1000000 - 1, 1000000]], [[2, 4], [7, 10], [4, 7]])],
        MEETINGS, [MEETINGS.replace("<= ordered[index][0]", "< ordered[index][0]"), 'def can_attend_all_meetings(intervals):\n    return all(intervals[i-1][1] <= intervals[i][0] for i in range(1, len(intervals)))\n'],
        ["Treats touching endpoints as overlapping even though back-to-back meetings are allowed.", "Checks adjacent intervals in the unsorted input and misses overlaps that become adjacent only by time order."], meetings_oracle, random_meetings,
        ["Only consecutive meetings in start-time order need to be compared.", "Sort by start time, then ensure every previous end is at most the next start.", "Return False on the first previous_end > current_start; otherwise return True, including for zero or one meeting.", "The inequality is strict for overlap: equality means the first meeting has already ended."],
        "If any meetings overlap, then after sorting by start time an overlapping predecessor exists next to or before the later meeting; comparing the immediately previous end suffices because any longer earlier meeting would also extend that previous maximum ordering conflict. The independent oracle checks every interval pair with half-open intersection arithmetic.", "O(n log n)", "O(n) for the sorted copy", difficulty=3,
        stress=[([[[2 * index, 2 * index + 1] for index in range(10000)]], True)]),
    254: entry("factor_combinations", [("n", "int")], "list[list[int]]", ["backtracking", "recursion", "number-theory"],
        ["1 ≤ n ≤ 10^7.", "Return each multiplicative factorization of n using factors from 2 through n-1 exactly once, in any order. A factor order is not a separate combination."],
        [([1], "One has no factors in the allowed range, so there are no combinations."), ([12], "The unique unordered factorizations are [2,6], [3,4], and [2,2,3].")],
        [[n] for n in (2, 4, 6, 8, 16, 24, 32, 36, 37, 64, 72, 100)],
        FACTORS, [FACTORS.replace("answers.append(path + [remaining // divisor])", "answers.append(path + [remaining // divisor])\n                return"), FACTORS.replace("search(divisor, remaining // divisor)", "search(2, remaining // divisor)")],
        ["Stops after the first divisor at each level and misses other valid factorizations.", "Restarts factor choices at 2, emitting permutations of the same factor combination."], factors_oracle, random_factors,
        ["Choosing factors in nondecreasing order prevents permutation duplicates.", "At a remaining product r, try divisors d from the previous choice through sqrt(r).", "When d divides r, record path+[r/d], then recurse with start=d and remaining=r/d.", "Numbers 1 and primes produce no combinations; include composite cofactors only as part of a length-at-least-two result."],
        "Every unordered factorization has a unique nondecreasing order. At each position its next factor cannot exceed the square root of the remaining product unless it is the final cofactor, so trial division finds every branch. The independent small-domain oracle enumerates nondecreasing tuples of actual proper divisors and filters by their direct product.", "O(number of candidate divisors and output size)", "O(log n) recursion excluding output", difficulty=5,
        stress=[([999983], [])]),
    256: entry("minimum_paint_cost", [("costs", "list[list[int]]")], "int", ["arrays", "dynamic-programming"],
        ["costs has 1–100 rows and exactly three integer costs from 1 to 20 per row.", "Choose one color per house so adjacent houses differ. Return the minimum total cost; the three columns consistently represent the same three colors."],
        [([[[17, 2, 17], [16, 16, 5], [14, 3, 19]]], "Choose color columns 1,2,1 for costs 2+5+3=10; adjacent colors differ."), ([[[7, 6, 2]]], "With one house there is no adjacency restriction, so choose its minimum cost 2.")],
        [[costs] for costs in ([[1, 1, 1]], [[1, 2, 3], [1, 2, 3]], [[1, 20, 20], [1, 20, 20]], [[1, 2, 3], [3, 2, 1]], [[20, 1, 20], [20, 1, 20], [20, 1, 20]], [[1, 20, 20], [20, 1, 20], [1, 20, 20]], [[5, 6, 7], [7, 6, 5], [5, 6, 7]], [[1, 2, 3]] * 4, [[3, 2, 1]] * 5, [[1, 20, 20], [20, 20, 1]], [[20, 1, 20], [1, 20, 20]], [[10, 10, 1], [1, 10, 10], [10, 1, 10]])],
        PAINT, ['def minimum_paint_cost(costs):\n    return sum(min(row) for row in costs)\n', 'def minimum_paint_cost(costs):\n    return min(sum(row[color] for row in costs) for color in range(3))\n'],
        ["Greedily chooses each row's cheapest color and can choose the same color for adjacent houses.", "Forces every house to use one fixed color instead of switching colors between adjacent houses."], paint_oracle, random_paint,
        ["The best cost ending in a color depends on the two different colors from the previous house.", "Keep three running costs, one for each possible last color.", "For each new row, add its red cost to min(previous blue,green), and analogously for the other colors.", "Use the previous three values together when computing the next row; in-place sequential updates would mix stages."],
        "The state for each color is the cheapest valid painting of the processed prefix ending in that color. Appending a house may use either of the other two prior states, giving the three transitions. Only one previous row is required. The independent oracle enumerates every color assignment for small seeded inputs and rejects adjacent equal colors.", "O(n)", "O(1)", difficulty=5,
        stress=[([[[1, 20, 20]] * 100], 1050)]),
    258: entry("add_digits", [("num", "int")], "int", ["math", "number-theory"],
        ["0 ≤ num ≤ 2^31-1.", "Repeatedly sum the decimal digits until one digit remains. Implement the O(1) arithmetic follow-up without a loop or recursion."],
        [([38], "38 becomes 3+8=11, then 1+1=2."), ([0], "Zero is already one digit and remains zero.")],
        [[number] for number in (1, 5, 9, 10, 11, 18, 19, 99, 100, 101, 999999999, 2147483647)],
        DIGITAL_ROOT, ['def add_digits(num):\n    return num % 9\n', 'def add_digits(num):\n    return sum(map(int, str(num)))\n'],
        ["Returns zero for positive multiples of nine, whose repeated digit sum is nine.", "Performs only one digit-summing round and can leave a multi-digit result."], digital_root_oracle, random_digital_root,
        ["Repeated digit sums preserve the number modulo 9.", "Positive multiples of 9 have digital root 9, while zero must remain 0.", "Return 0 for num==0; otherwise return 1+(num-1)%9.", "Subtracting one before the remainder maps each positive congruence class to the required range 1 through 9."],
        "Decimal place values are all congruent to one modulo nine, so replacing a number by its digit sum preserves its residue. Repetition ends at the unique representative from 1 through 9, except that input zero stays zero. The independent oracle performs the literal digit-summing process.", "O(1)", "O(1)", difficulty=3),
}
BATCH[247]["comparator"] = "unordered"
BATCH[249]["comparator"] = "unordered_nested"
BATCH[254]["comparator"] = "unordered_nested"
BATCH[248]["prerequisites"] = ["recursion", "backtracking", "strings"]
