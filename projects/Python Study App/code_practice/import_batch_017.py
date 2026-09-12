"""Distinct text/array contracts and backward dungeon dynamic programming."""
from itertools import combinations, zip_longest
import re

from .import_batch_003 import entry


def words_oracle(args):
    return " ".join(re.findall(r"[^ ]+", args[0])[::-1])


def product_oracle(args):
    nums = args[0]
    best = nums[0]
    for start in range(len(nums)):
        value = 1
        for end in range(start, len(nums)):
            value *= nums[end]
            best = max(best, value)
    return best


def minimum_oracle(args):
    return min(args[0])


def two_char_oracle(args):
    text = args[0]
    return max(end - start for start in range(len(text)) for end in range(start + 1, len(text) + 1)
               if len(set(text[start:end])) <= 2)


def one_edit_oracle(args):
    first, second = args
    distance = [[0] * (len(second) + 1) for _ in range(len(first) + 1)]
    for i in range(len(first) + 1):
        distance[i][0] = i
    for j in range(len(second) + 1):
        distance[0][j] = j
    for i in range(1, len(first) + 1):
        for j in range(1, len(second) + 1):
            distance[i][j] = min(distance[i-1][j] + 1, distance[i][j-1] + 1,
                                 distance[i-1][j-1] + (first[i-1] != second[j-1]))
    return distance[-1][-1] == 1


def ranges_oracle(args):
    nums, lower, upper = args
    present = set(nums)
    missing = [value for value in range(lower, upper + 1) if value not in present]
    groups = []
    for value in missing:
        if groups and value == groups[-1][1] + 1:
            groups[-1][1] = value
        else:
            groups.append([value, value])
    return groups


def versions_oracle(args):
    first, second = (list(map(int, value.split("."))) for value in args)
    for a, b in zip_longest(first, second, fillvalue=0):
        if a != b:
            return 1 if a > b else -1
    return 0


def dungeon_oracle(args):
    dungeon = args[0]
    rows, columns = len(dungeon), len(dungeon[0])
    best = float("inf")
    for down_steps in combinations(range(rows + columns - 2), rows - 1):
        down_steps = set(down_steps)
        row = column = 0
        balance = lowest = dungeon[0][0]
        for step in range(rows + columns - 2):
            if step in down_steps:
                row += 1
            else:
                column += 1
            balance += dungeon[row][column]
            lowest = min(lowest, balance)
        best = min(best, max(1, 1 - lowest))
    return best


def random_words(rng):
    words = ["".join(rng.choice("aAbB019") for _ in range(rng.randint(1, 6))) for _ in range(rng.randint(1, 8))]
    return [" " * rng.randrange(4) + (" " * rng.randint(1, 4)).join(words) + " " * rng.randrange(4)]


def random_product(rng):
    return [[rng.randint(-3, 3) for _ in range(rng.randint(1, 12))]]


def random_minimum(rng):
    nums = sorted(rng.randint(-20, 20) for _ in range(rng.randint(1, 60)))
    pivot = rng.randrange(len(nums))
    return [nums[pivot:] + nums[:pivot]]


def random_two_char(rng):
    return ["".join(rng.choice("abcABC") for _ in range(rng.randint(1, 24)))]


def random_one_edit(rng):
    first = "".join(rng.choice("abcAB01") for _ in range(rng.randrange(11)))
    index = rng.randrange(len(first) + 1)
    operation = rng.randrange(5)
    if operation == 0:
        second = first[:index] + rng.choice("abcAB01") + first[index:]
    elif operation == 1:
        second = first[:index] + first[index + 1:]
    elif operation == 2:
        second = first[:index] + rng.choice("abcAB01") + first[index + 1:]
    elif operation == 3:
        second = first
    else:
        second = "".join(rng.choice("abcAB01") for _ in range(rng.randrange(11)))
    return [first, second]


def random_ranges(rng):
    lower = rng.randint(-30, 30)
    upper = lower + rng.randrange(41)
    return [sorted(value for value in range(lower, upper + 1) if rng.random() < .5), lower, upper]


def random_versions(rng):
    return [".".join("0" * rng.randrange(5) + str(rng.randint(0, 9999)) for _ in range(rng.randint(1, 8))) for _ in range(2)]


def random_dungeon(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randint(-15, 15) for _ in range(columns)] for _ in range(rows)]]


WORDS = '''\
def reverse_words(s):
    words = []
    end = len(s) - 1
    while end >= 0:
        while end >= 0 and s[end] == " ":
            end -= 1
        if end < 0:
            break
        start = end
        while start >= 0 and s[start] != " ":
            start -= 1
        words.append(s[start + 1:end + 1])
        end = start - 1
    return " ".join(words)
'''
PRODUCT = '''\
def maximum_product(nums):
    highest = lowest = best = nums[0]
    for index in range(1, len(nums)):
        value = nums[index]
        a, b = value * highest, value * lowest
        highest = max(value, a, b)
        lowest = min(value, a, b)
        best = max(best, highest)
    return best
'''
MAX_ONLY = '''\
def maximum_product(nums):
    ending = best = nums[0]
    for value in nums[1:]:
        ending = max(value, ending * value)
        best = max(best, ending)
    return best
'''
MINIMUM = '''\
def rotated_minimum(nums):
    left, right = 0, len(nums) - 1
    while left < right:
        middle = (left + right) // 2
        if nums[middle] > nums[right]:
            left = middle + 1
        elif nums[middle] < nums[right]:
            right = middle
        else:
            right -= 1
    return nums[left]
'''
TWO_CHAR = '''\
def longest_two_distinct(s):
    counts = {}
    left = best = 0
    for right, char in enumerate(s):
        counts[char] = counts.get(char, 0) + 1
        while len(counts) > 2:
            departing = s[left]
            counts[departing] -= 1
            if counts[departing] == 0:
                del counts[departing]
            left += 1
        best = max(best, right - left + 1)
    return best
'''
ONE_EDIT = '''\
def one_edit_apart(s, t):
    if abs(len(s) - len(t)) > 1:
        return False
    i = j = edits = 0
    while i < len(s) and j < len(t):
        if s[i] == t[j]:
            i += 1
            j += 1
            continue
        edits += 1
        if edits > 1:
            return False
        if len(s) >= len(t):
            i += 1
        if len(t) >= len(s):
            j += 1
    return edits + (i < len(s)) + (j < len(t)) == 1
'''
RANGES = '''\
def missing_ranges(nums, lower, upper):
    result = []
    following = lower
    for value in nums:
        if following < value:
            result.append([following, value - 1])
        following = value + 1
    if following <= upper:
        result.append([following, upper])
    return result
'''
VERSIONS = '''\
def compare_versions(version1, version2):
    def revision(text, index):
        value = 0
        while index < len(text) and text[index] != ".":
            value = value * 10 + ord(text[index]) - ord("0")
            index += 1
        return value, index + 1
    i = j = 0
    while i < len(version1) or j < len(version2):
        first, i = revision(version1, i)
        second, j = revision(version2, j)
        if first != second:
            return 1 if first > second else -1
    return 0
'''
DUNGEON = '''\
def minimum_initial_health(dungeon):
    columns = len(dungeon[0])
    needed = [float("inf")] * (columns + 1)
    needed[columns - 1] = 1
    for row in reversed(dungeon):
        for column in range(columns - 1, -1, -1):
            needed[column] = max(1, min(needed[column], needed[column + 1]) - row[column])
    return needed[0]
'''
FINAL_HEALTH_WRONG = '''\
def minimum_initial_health(dungeon):
    scores = [float("-inf")] * len(dungeon[0])
    scores[0] = 0
    for row in dungeon:
        for column, value in enumerate(row):
            scores[column] = max(scores[column], scores[column - 1] if column else float("-inf")) + value
    return max(1, 1 - scores[-1])
'''

BATCH = {
    151: entry("reverse_words", [("s", "str")], "str", ["strings", "two-pointers"],
        ["1–10000 English letters, digits, and ordinary spaces; at least one word exists.", "Reverse word order, not the characters within a word. Remove leading/trailing spaces and use exactly one space between output words."],
        [(["the sky is blue"], "The four words become blue, is, sky, the; each word's spelling stays unchanged."),
         (["  hello   world  "], "The output is 'world hello': three internal spaces and both outer margins are normalized away.")],
        [[s] for s in ("a", "ab", " a", "a ", "  a  ", "a b", "a  b", "one two three", "A1 b2", "same same", "x Y z", "0  12  345")],
        WORDS, ['def reverse_words(s):\n    return s[::-1].strip()\n', 'def reverse_words(s):\n    return " ".join(s.split(" ")[::-1])\n'],
        ["Reverses individual characters along with word order.", "Treats empty pieces between spaces as words and retains extra spaces."], words_oracle, random_words,
        ["Keep each word intact and change only the order of words.", "Scan backward, skipping spaces and collecting complete word slices.", "Find each word's end and beginning, append the slice, then join collected words with one space.", "An all-spaces segment adds no word; leading and trailing spaces must not survive."],
        "Scanning from right to left discovers words in their required order. Skip spaces before each word, then scan to its beginning without reversing its characters. Joining the collected words inserts exactly one space. The independent oracle extracts non-space runs with a regular expression and reverses that sequence. Python strings are immutable, so O(n) output/intermediate storage is appropriate; the source's mutable-string follow-up does not change the Python return contract.",
        "O(n)", "O(n)", difficulty=5, stress=[(["a " * 4999 + "b"], "b " + "a " * 4998 + "a")]),
    152: entry("maximum_product", [("nums", "list[int]")], "int", ["arrays", "dynamic-programming"],
        ["1–20000 integers from -10 to 10. Every contiguous subarray product fits signed 32-bit range.", "Choose a nonempty contiguous subarray. Zero separates potential runs; a negative value can turn the smallest ending product into the largest."],
        [([[2, 3, -2, 4]], "The contiguous pair [2,3] has product 6, better than the later products."),
         ([[-2, 0, -1]], "The maximum is 0. The two negative values cannot be joined across the intervening zero.")],
        [[a] for a in ([0], [1], [-1], [-10], [2, 3], [-2, 3, -4], [-2, -3], [-2, -3, -4], [0, -2, -3, 0], [1, -2, -3, 4], [-10] * 9, [2, 0, 3])],
        PRODUCT, [MAX_ONLY, PRODUCT.replace("    highest =", "    nums = [value for value in nums if value != 0] or [0]\n    highest =", 1)],
        ["Tracks only the maximum ending product, discarding the negative minimum that can later become positive.", "Removes zeros and joins pieces that are not a contiguous subarray."], product_oracle, random_product,
        ["Multiplying by a negative number reverses the ordering of products.", "Keep both the minimum and maximum product ending at the previous position.", "At each value, consider starting anew or multiplying either previous extreme; update both extremes and the global best.", "Compute both products before overwriting either previous extreme, and do not skip zeros."],
        "Unlike maximum-sum subarrays, a product needs both extremes because a negative multiplier swaps their roles. Each position either starts a new nonempty subarray or extends a previous one. Keeping only the ending minimum and maximum is sufficient to describe the next extremes. The oracle explicitly enumerates every contiguous start/end interval and multiplies its values. All generated products stay within the source's signed-32-bit guarantee.",
        "O(n)", "O(1)", difficulty=5,
        stress=[([[1, -1, 0, 2, 2, 0] * 3333 + [0, 1]], 4)]),
    154: entry("rotated_minimum", [("nums", "list[int]")], "int", ["arrays", "binary-search"],
        ["1–5000 integers from -5000 to 5000 form a rotated nondecreasing array. Duplicates are allowed; a full rotation may leave the array sorted.", "Return the minimum value, not its index. Eliminate half the search interval whenever comparisons allow; equal endpoints may require shrinking one position."],
        [([[1, 3, 5]], "A full rotation leaves the array sorted, so its minimum is the first value, 1."),
         ([[2, 2, 2, 0, 1]], "The repeated 2 values do not identify the pivot; the minimum 0 is inside the array.")],
        [[a] for a in ([0], [1, 1], [3, 1, 3], [1, 1, 1, 0, 1], [2, 2, 0, 1, 2], [4, 5, 1, 2, 3], [2, 1], [-1, -3, -2], [5, 5, 5, 5], [1, 0, 1, 1, 1], [1, 1, 0, 1, 1], [5000, -5000])],
        MINIMUM, [MINIMUM.replace("right -= 1", "right = middle"), 'def rotated_minimum(nums):\n    return min(nums[0], nums[-1])\n'],
        ["Discards half the interval on equality even though the unseen minimum may be there.", "Checks only endpoint values and misses an interior pivot."], minimum_oracle, random_minimum,
        ["Compare the midpoint with the right edge of the remaining rotated interval.", "A larger midpoint puts the minimum to its right; a smaller midpoint keeps the midpoint and left side.", "On equality, discard only the rightmost duplicate. Continue until left and right meet.", "Duplicates make an O(n) worst case unavoidable for this comparison strategy; distinct values retain O(log n) behavior."],
        "Maintain an interval containing a minimum. Midpoint comparisons against its right edge normally eliminate half. Equality cannot determine which side contains a smaller value, but deleting the rightmost equal copy preserves at least one minimum. The independent oracle performs a full minimum scan. This is distinct from target searching: there is no target argument and the result is a minimum value. Without duplicate ambiguity, the same reference takes logarithmic time; all-equal inputs illustrate its linear worst case.",
        "O(log n) without ambiguous equalities; O(n) worst case with duplicates", "O(1)", difficulty=8,
        stress=[([[1] * 5000], 1), ([[1] * 4321 + [0] + [1] * 678], 0)]),
    159: entry("longest_two_distinct", [("s", "str")], "int", ["strings", "sliding-window", "hash-maps"],
        ["1–100000 English letters; uppercase and lowercase are different characters.", "Find a contiguous substring with at most two distinct characters. Repeated occurrences of either character are allowed; one-character substrings also qualify."],
        [(["eceba"], "The substring 'ece' has two distinct characters, e and c, and length 3 despite the repeated e."),
         (["ccaabbb"], "The suffix 'aabbb' contains only a and b and has length 5.")],
        [[s] for s in ("a", "aaaa", "ab", "abc", "aab", "abac", "aabbcc", "abcabc", "aAa", "AaB", "abbbbbc", "aabbbaaac")],
        TWO_CHAR, [TWO_CHAR.replace("len(counts) > 2", "len(counts) > 3"), TWO_CHAR.replace("len(counts) > 2", "right - left + 1 > len(counts)")],
        ["Permits three distinct characters instead of two.", "Solves the no-repeated-characters problem and incorrectly rejects repeated letters in a valid two-character window."], two_char_oracle, random_two_char,
        ["The limit applies to distinct characters, not total window length or repeated occurrences.", "Count characters in a window and shrink its left edge whenever a third distinct character enters.", "Add the new right character; while there are more than two keys, decrement the left character and delete zero counts; update the largest width.", "The shrink step may need several removals before a character count reaches zero."],
        "A frequency map describes the current window. Expanding right may introduce a third distinct character; removing from the left restores the invariant. Each pointer advances at most n times, and at most three map entries exist during an update. The independent oracle enumerates substrings and measures the distinct-character set directly. Unlike the existing no-repeat exercise, arbitrarily many repetitions of the same two letters are allowed.",
        "O(n)", "O(1), at most three character counts", difficulty=5, stress=[(["a" * 100000], 100000)]),
    161: entry("one_edit_apart", [("s", "str"), ("t", "str")], "bool", ["strings", "two-pointers"],
        ["Each string has 0–10000 English letters or digits.", "Return True only for exactly one insertion, deletion, or replacement by a different character. Equal strings require zero edits and therefore return False."],
        [(["ab", "acb"], "Insert c between a and b to obtain acb in exactly one edit."),
         (["", ""], "The strings are already equal, so their distance is zero rather than one.")],
        [[a, b] for a, b in (("", "a"), ("a", ""), ("a", "a"), ("a", "b"), ("ab", "ab"), ("ab", "ba"), ("abc", "ab"), ("abc", "xbc"), ("abc", "abx"), ("ab", "cab"), ("A1", "A2"), ("a", "abc"))],
        ONE_EDIT, [ONE_EDIT.replace("== 1\n", "<= 1\n"), 'def one_edit_apart(s, t):\n    return sum(a != b for a, b in zip(s, t)) + abs(len(s) - len(t)) == 1\n'],
        ["Accepts identical strings as at most one edit instead of requiring exactly one.", "Compares aligned positions without shifting after an insertion or deletion."], one_edit_oracle, random_one_edit,
        ["A length difference greater than one makes exactly one edit impossible.", "Scan both strings until a mismatch; skip one character in the longer string or one in each if lengths match.", "Count mismatches, reject a second, and include any one trailing unmatched character in the edit total.", "An unchanged scan is accepted only if one string has a single extra trailing character."],
        "The known one-edit limit removes the need for a full distance table. At the first mismatch, the relative lengths determine which pointer advances; any later mismatch proves that more than one edit is required. End-of-string leftovers account for an insertion/deletion at the end. The independent oracle computes the full Levenshtein dynamic-programming table on small strings and checks whether the distance equals one. The returned Boolean and linear-time goal distinguish this exercise from the existing general edit-distance problem.",
        "O(len(s) + len(t))", "O(1)", difficulty=5,
        stress=[(["a" * 10000, "a" * 9999 + "b"], True), (["a" * 10000, "a" * 10000], False)]),
    163: entry("missing_ranges", [("nums", "list[int]"), ("lower", "int"), ("upper", "int")], "list[list[int]]", ["arrays", "intervals"],
        ["-10^9 ≤ lower ≤ upper ≤ 10^9. nums contains 0–100 sorted unique values inside that inclusive interval.", "Return sorted inclusive [start,end] pairs covering all and only missing integers. Merge adjacent missing integers into the fewest ranges; singleton gaps use [x,x]."],
        [([[0, 1, 3, 50, 75], 0, 99], "Missing integers form [2,2], [4,49], [51,74], and [76,99]; each present value separates neighboring gaps."),
         ([[-1], -1, -1], "The only integer in the allowed interval is present, so there are no missing ranges.")],
        [[a, lo, hi] for a, lo, hi in (([], 0, 0), ([], 1, 5), ([0], 0, 0), ([1], 0, 2), ([0, 2], 0, 2), ([1, 2, 3], 1, 3), ([2], 0, 4), ([-2, 0, 2], -3, 3), ([0], -1, 0), ([0], 0, 1), ([-1000000000], -1000000000, -999999996), ([1000000000], 999999996, 1000000000))],
        RANGES, [RANGES.replace("[following, value - 1]", "[following, value]"), RANGES.replace("if following <= upper:", "if False:")],
        ["Includes the next present value as the endpoint of a missing range.", "Forgets the final gap after the last present value, including an entirely empty input."], ranges_oracle, random_ranges,
        ["Present numbers split the inclusive interval into possible missing gaps.", "Track the next integer that has not yet been covered, beginning at lower.", "Before each present value x, emit [next,x-1] if nonempty, then set next=x+1. Finish with [next,upper] if needed.", "Do not enumerate a billion missing values; emit one range for a long gap."],
        "Because the present values are sorted and unique, each gap can be emitted in one step. Track the next unaccounted value, skip every present number, and include the final trailing gap. This uses linear time in the number of present values, independent of the numeric interval width. The oracle explicitly enumerates missing values only on bounded small intervals, then groups adjacent values. A full [-10^9,10^9] stress interval has the directly known single-range answer.",
        "O(len(nums))", "O(1) auxiliary, plus output", difficulty=3,
        stress=[([[], -1000000000, 1000000000], [[-1000000000, 1000000000]])]),
    165: entry("compare_versions", [("version1", "str"), ("version2", "str")], "int", ["strings", "two-pointers"],
        ["Each valid version string contains 1–500 digits and dots, with nonempty numeric revisions separated by single dots.", "Every revision value fits a nonnegative signed-32-bit integer, ignoring leading zeros. Missing trailing revisions count as zero. Return exactly -1, 0, or 1."],
        [(["1.2", "1.10"], "Compare the second revisions numerically: 2 is less than 10, so the answer is -1."),
         (["1.01", "1.001"], "Leading zeros do not change a revision's value; both versions represent revisions [1,1] and compare equal.")],
        [[a, b] for a, b in (("1", "1.0"), ("0.0", "0"), ("1.0.1", "1"), ("1", "1.0.1"), ("2", "10"), ("10", "2"), ("01", "1"), ("0.1", "0.01"), ("1.2.0", "1.2"), ("2.0", "1.99"), ("2147483647", "2147483646"), ("0", "1"))],
        VERSIONS, ['def compare_versions(version1, version2):\n    return (version1 > version2) - (version1 < version2)\n',
                   'def compare_versions(version1, version2):\n    a, b = tuple(map(int, version1.split("."))), tuple(map(int, version2.split(".")))\n    return (a > b) - (a < b)\n'],
        ["Uses lexicographic string order instead of numeric revision order.", "Treats a shorter revision tuple as smaller even when every extra revision is zero."], versions_oracle, random_versions,
        ["Dots separate independent integer revisions, not digits of a decimal fraction.", "Scan corresponding revisions from left to right, treating an exhausted version as zeros.", "Accumulate each revision's numeric value until a dot; return on the first mismatch, otherwise continue through both strings.", "Leading zeros and any number of trailing zero revisions do not affect equality."],
        "The first unequal revision determines ordering. The reference parses one revision at a time without allocating split arrays; an exhausted input contributes zero while the other continues. Its numeric accumulator remains bounded by the source's 32-bit revision guarantee even when many leading zeros are present. The independent oracle splits into integer lists and uses zero-filled pairwise comparison.",
        "O(len(version1) + len(version2))", "O(1)", difficulty=5,
        stress=[(["0" * 490 + "2147483647", "2147483647"], 0)]),
    174: entry("minimum_initial_health", [("dungeon", "list[list[int]]")], "int", ["matrices", "dynamic-programming", "recursion"],
        ["A rectangular dungeon has 1–200 rows and columns, with cell changes from -1000 to 1000.", "Start at the top-left, move only right or down, and include the first and last cells' health changes. Health must stay at least 1 after every visited cell. Return the smallest sufficient positive initial health."],
        [([[[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]], "Starting with 7 and moving right,right,down,down gives health 5,2,5,6,1; starting with 6 would die at the final cell on this route."),
         ([[[0]]], "Even a harmless single cell needs initial health 1 because zero health is not allowed.")],
        [[grid] for grid in ([[-1]], [[1]], [[-1000]], [[1000]], [[-2, 5]], [[5, -10]], [[-5, 100]], [[-1], [-2]], [[1, -3, 3]], [[-2, -3], [-5, -10]], [[10, -20], [-5, -5]], [[0, 0], [0, 0]])],
        DUNGEON, [DUNGEON.replace("max(1,", "max(0,"), FINAL_HEALTH_WRONG],
        ["Allows health to reach zero by clamping the requirement at zero instead of one.", "Optimizes only final health and ignores lethal negative prefixes along a route."], dungeon_oracle, random_dungeon,
        ["Final total health is not enough: an earlier room can kill the knight before later gains arrive.", "Work backward, asking the minimum health required on entering each room.", "For each cell compute max(1, min(required_down,required_right)-cell_value), with a requirement of 1 just after the destination.", "Reuse one DP row; a recursive memoized formulation expresses the same dependency, but backward iteration avoids recursion depth concerns."],
        "The required health at a room is determined by the cheaper valid continuation, minus that room's change, and clamped at one. Backward DP therefore tracks exactly the quantity that must remain feasible throughout the path. The reference stores only one row of requirements. The independent oracle enumerates every right/down route on small grids, computes the minimum prefix balance on each route, and chooses the least required starting health. This differs from minimum path sum: even a route with positive final gain can need substantial health to survive its beginning.",
        "O(rows × columns)", "O(columns)", difficulty=8,
        stress=[([[[-1000] * 200 for _ in range(200)]], 399001), ([[[1000] * 200 for _ in range(200)]], 1)]),
}
BATCH[154]["prerequisites"] = ["binary-search"]
BATCH[174]["prerequisites"] = ["matrices", "dynamic-programming"]
