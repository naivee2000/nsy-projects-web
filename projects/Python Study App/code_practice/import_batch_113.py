"""First reviewed group of workbook batch 113."""

from collections import deque
from functools import lru_cache

from .import_batch_055 import entry


def resizing_oracle(arguments):
    nums, operations = arguments

    @lru_cache(maxsize=None)
    def solve(start, groups):
        if start == len(nums):
            return 0
        best = float("inf")
        maximum = total = 0
        for end in range(start, len(nums)):
            maximum = max(maximum, nums[end])
            total += nums[end]
            if groups > 1 or end == len(nums) - 1:
                best = min(best, maximum * (end - start + 1) - total + solve(end + 1, groups - 1))
        return best

    return solve(0, operations + 1)


def palindrome_product_oracle(arguments):
    text = arguments[0]
    palindromes = []
    for left in range(len(text)):
        for right in range(left, len(text)):
            value = text[left:right + 1]
            if len(value) % 2 and value == value[::-1]:
                palindromes.append((left, right, len(value)))
    return max(first[2] * second[2] for first in palindromes for second in palindromes if first[1] < second[0])


def prefix_oracle(arguments):
    text, words = arguments
    current = ""
    for word in words:
        current += word
        if current == text:
            return True
        if not text.startswith(current):
            return False
    return False


def stones_oracle(arguments):
    piles, operations = arguments

    @lru_cache(maxsize=None)
    def solve(state, remaining):
        if remaining == 0:
            return sum(state)
        return min(solve(tuple(sorted(state[:index] + (value - value // 2,) + state[index + 1:])), remaining - 1)
                   for index, value in enumerate(state))

    return solve(tuple(sorted(piles)), operations)


def _balanced(text):
    balance = 0
    for char in text:
        balance += 1 if char == "[" else -1
        if balance < 0:
            return False
    return balance == 0


def swaps_oracle(arguments):
    start = arguments[0]
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        text, distance = queue.popleft()
        if _balanced(text):
            return distance
        for left in range(len(text)):
            for right in range(left + 1, len(text)):
                if text[left] != text[right]:
                    following = text[:left] + text[right] + text[left + 1:right] + text[left] + text[right + 1:]
                    if following not in seen:
                        seen.add(following)
                        queue.append((following, distance + 1))


def random_resizing(rng):
    length = rng.randint(1, 10)
    return [[rng.randint(1, 30) for _ in range(length)], rng.randint(0, length - 1)]


def random_palindrome_product(rng):
    return ["".join(rng.choice("abcd") for _ in range(rng.randint(2, 14)))]


def random_prefix(rng):
    words = ["".join(rng.choice("abc") for _ in range(rng.randint(1, 5))) for _ in range(rng.randint(1, 8))]
    joined = "".join(words[:rng.randint(1, len(words))]) if rng.random() < .6 else "".join(rng.choice("abc") for _ in range(rng.randint(1, 20)))
    return [joined, words]


def random_stones(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(1, 6))], rng.randint(1, 6)]


def random_swaps(rng):
    pairs = rng.randint(1, 5)
    chars = list("[" * pairs + "]" * pairs)
    rng.shuffle(chars)
    return ["".join(chars)]


RESIZING = '''\
def minimum_resizing_waste(nums, k):
    size = len(nums)
    segment = [[0] * size for _ in range(size)]
    for left in range(size):
        maximum = total = 0
        for right in range(left, size):
            maximum = max(maximum, nums[right])
            total += nums[right]
            segment[left][right] = maximum * (right - left + 1) - total
    previous = [segment[0][right] for right in range(size)]
    for groups in range(2, k + 2):
        current = [float("inf")] * size
        for right in range(groups - 1, size):
            current[right] = min(previous[split - 1] + segment[split][right] for split in range(groups - 1, right + 1))
        previous = current
    return previous[-1]
'''

PALINDROMES = '''\
def maximum_odd_palindrome_product(s):
    size = len(s)
    radius = [0] * size
    left = 0
    right = -1
    for center in range(size):
        reach = 1 if center > right else min(radius[left + right - center], right - center + 1)
        while center - reach >= 0 and center + reach < size and s[center - reach] == s[center + reach]:
            reach += 1
        radius[center] = reach
        if center + reach - 1 > right:
            left, right = center - reach + 1, center + reach - 1
    prefix = [0] * size
    suffix = [0] * size
    for center, reach in enumerate(radius):
        length = 2 * reach - 1
        prefix[center + reach - 1] = max(prefix[center + reach - 1], length)
        suffix[center - reach + 1] = max(suffix[center - reach + 1], length)
    for index in range(size - 2, -1, -1):
        prefix[index] = max(prefix[index], prefix[index + 1] - 2)
    for index in range(1, size):
        prefix[index] = max(prefix[index], prefix[index - 1])
        suffix[index] = max(suffix[index], suffix[index - 1] - 2)
    for index in range(size - 2, -1, -1):
        suffix[index] = max(suffix[index], suffix[index + 1])
    return max(prefix[index] * suffix[index + 1] for index in range(size - 1))
'''

PREFIX = '''\
def is_prefix_string(s, words):
    length = 0
    for word in words:
        length += len(word)
        if length > len(s) or s[length - len(word):length] != word:
            return False
        if length == len(s):
            return True
    return False
'''

STONES = '''\
def minimum_stone_total(piles, k):
    from heapq import heapify, heappop, heappush
    heap = [-pile for pile in piles]
    heapify(heap)
    for _ in range(k):
        pile = -heappop(heap)
        heappush(heap, -(pile - pile // 2))
    return -sum(heap)
'''

SWAPS = '''\
def minimum_bracket_balance_swaps(s):
    balance = 0
    deficit = 0
    for char in s:
        balance += 1 if char == "[" else -1
        deficit = max(deficit, -balance)
    return (deficit + 1) // 2
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


BATCH = {
    1959: entry(
        "minimum_resizing_waste", [("nums", "list[int]"), ("k", "int")], "int", ["arrays", "dynamic programming", "prefix sums"],
        ["nums has 1 through 200 positive values, each at most 1000000.", "0 <= k < len(nums); the initial array size is free and you may resize at most k times.",
         "At each time the chosen capacity must be at least nums[t], and waste is capacity-nums[t]."],
        [([[10,20],0], "One capacity must cover both times, so capacity twenty wastes ten in total."),
         ([[10,20,15,30,20],2], "Three constant-capacity segments can achieve total waste fifteen.")],
        [[a,k] for a,k in [([1],0),([10,20],1),([20,10],0),([20,10],1),([1,2,3],0),([1,2,3],2),
                           ([3,1,4,1,5],1),([10,20,15,30,20],2),([5,5,5],0),([5,1,5],1),
                           ([1,100,1],1),([8,2,6,4],2),([4,9,2,10,3],3),([1000000,1],0)]],
        RESIZING,
        [RESIZING.replace("k + 2", "k + 1"), RESIZING.replace("maximum * (right - left + 1) - total", "nums[left] * (right - left + 1) - total")],
        ["Uses only k capacity segments instead of the initial segment plus k allowed resizes.",
         "Sets a segment capacity from its first value rather than its maximum, which can undercount waste and violate capacity."],
        resizing_oracle, random_resizing,
        lesson("Once resize boundaries are fixed, each segment's cheapest legal capacity is its maximum demand.",
               "Precompute every segment's waste, then partition the prefix into at most k+1 segments with dynamic programming.",
               "cost[l][r]=max(nums[l:r+1])*length-sum; dp[g][r]=min(dp[g-1][split-1]+cost[split][r]).",
               "The segment maximum is necessary and sufficient capacity. Trying every final split enumerates every legal resize schedule, and extra zero-benefit splits mean using exactly up to k+1 groups is safe."),
        "O(k*n^2)", "O(n^2)", 6),
    1960: entry(
        "maximum_odd_palindrome_product", [("s", "str")], "int", ["strings", "palindromes", "Manacher algorithm"],
        ["s has 2 through 100000 lowercase English letters.", "Choose two nonoverlapping substrings in left-to-right order.",
         "Both palindromes must have odd positive length; maximize the product of their lengths."],
        [(["ababbb"], "Choose aba of length three and bbb of length three for product nine."),
         (["zaaaxbbby"], "The nonoverlapping aaa and bbb palindromes give product nine.")],
        [[s] for s in ["aa","ab","aaa","aba","abba","aaaa","ababbb","zaaaxbbby","racecarxaba",
                       "abcbaabcdcba","aaaaabaaaaa","abacdcaba","xyzzyx","aabaaacaa"]],
        PALINDROMES,
        [PALINDROMES.replace("prefix[index] * suffix[index + 1]", "prefix[index] + suffix[index + 1]"),
         '''def maximum_odd_palindrome_product(s):\n    best = 1\n    for center in range(len(s)):\n        radius = 0\n        while center-radius >= 0 and center+radius < len(s) and s[center-radius] == s[center+radius]:\n            best = max(best, 2*radius+1)\n            radius += 1\n    return best * best\n'''],
        ["Adds the two lengths instead of multiplying them.", "Squares one longest palindrome as though two nonoverlapping copies were available."],
        palindrome_product_oracle, random_palindrome_product,
        lesson("Odd Manacher radii give every center's longest palindrome; shorter nested palindromes propagate two characters at a time toward earlier ends and later starts.",
               "Build the best palindrome contained in every prefix and suffix, then test each split between adjacent characters.",
               "Compute radii; seed exact end/start lengths; propagate nested lengths and prefix/suffix maxima; maximize left[i]*right[i+1].",
               "Every candidate pair is separated by some split. The propagated arrays store the longest legal palindrome on each side of every split, so their product dominates every pair and is itself attainable."),
        "O(n)", "O(n)", 8),
    1961: entry(
        "is_prefix_string", [("s", "str"), ("words", "list[str]")], "bool", ["strings", "arrays", "two pointers"],
        ["words has 1 through 100 nonempty lowercase words, each of length at most 20.", "s has 1 through 1000 lowercase letters.",
         "Return true only when s equals words[0]+...+words[k] for some complete-word endpoint k."],
        [(["iloveleetcode",["i","love","leetcode","apples"]], "The first three complete words concatenate exactly to s."),
         (["iloveleetcode",["apples","i","love","leetcode"]], "The concatenation disagrees from the first word, so s is not a prefix string.")],
        [[s,w] for s,w in [("a",["a"]),("a",["ab"]),("ab",["a","b"]),("ab",["ab","c"]),
                            ("abc",["a","bc"]),("abc",["ab","cd"]),("hello",["he","llo","x"]),
                            ("hell",["hello"]),("iloveleetcode",["i","love","leetcode","apples"]),
                            ("i",["i","love"]),("love",["i","love"]),("aaa",["a","a","a"]),
                            ("aaaa",["aa","a","a"]),("xyz",["x","y","z","more"])]],
        PREFIX,
        ['''def is_prefix_string(s, words):\n    return s.startswith(words[0])\n''',
         '''def is_prefix_string(s, words):\n    return "".join(words).startswith(s)\n'''],
        ["Checks only alignment with the first word and ignores the required remaining concatenation.", "Checks whether s is a character prefix of the full join, ignoring complete-word boundaries."],
        prefix_oracle, random_prefix,
        lesson("Matching characters is not enough: success is allowed only immediately after consuming a whole word.",
               "Accumulate complete words while comparing each newly occupied slice of s, returning true exactly at equal total length.",
               "For each word, advance length; reject overflow or slice mismatch; accept when length==len(s).",
               "The invariant says s[:length] equals the concatenation of processed whole words. Equality at a boundary proves success; mismatch, overflow, or exhausting words proves no later valid prefix."),
        "O(len(s))", "O(1)", 3),
    1962: entry(
        "minimum_stone_total", [("piles", "list[int]"), ("k", "int")], "int", ["heaps", "arrays", "greedy"],
        ["piles has 1 through 100000 positive counts, each at most 10000.", "1 <= k <= 100000.",
         "Each operation chooses one current pile and removes floor(pile/2), leaving ceil(pile/2); perform exactly k operations."],
        [([[5,4,9],2], "Reducing nine to five and then five to three leaves totals 5+4+3=12."),
         ([[4,3,6,7],3], "Repeatedly reducing a largest pile leaves twelve stones.")],
        [[p,k] for p,k in [([1],1),([2],1),([3],1),([5,4,9],1),([5,4,9],2),([4,3,6,7],3),
                           ([10,1],2),([8,8],2),([1,1,1],5),([10000],10),([9,8,7],4),
                           ([2,2,2,2],3),([100,50,25],5),([6,5,4,3,2,1],6)]],
        STONES,
        [STONES.replace("heappush(heap, -(pile - pile // 2))", "heappush(heap, -(pile // 2))"),
         STONES.replace("pile = -heappop(heap)", "pile = -heap.pop()")],
        ["Leaves floor(pile/2) instead of ceil(pile/2), removing too many stones from odd piles.",
         "Pops an arbitrary heap-array tail rather than the largest pile."],
        stones_oracle, random_stones,
        lesson("One operation removes more stones from a larger pile, so always choose the current maximum.",
               "Store negative pile sizes in a min-heap; pop the largest, replace it with ceil(pile/2), and repeat k times.",
               "heapify negatives; repeat: p=-pop; push(-(p-p//2)); return -sum(heap).",
               "If an operation chose a smaller pile while a larger existed, swapping that operation to the larger removes at least as many now and cannot reduce future options, proving the greedy choice."),
        "O((n+k) log n)", "O(n)", 5),
    1963: entry(
        "minimum_bracket_balance_swaps", [("s", "str")], "int", ["strings", "greedy", "brackets"],
        ["s has even length 2 through 1000000 and contains only '[' and ']'.", "The counts of opening and closing brackets are equal.",
         "One operation may swap any two positions; return the minimum swaps needed for a balanced bracket string."],
        [(["][]["], "One swap can transform the string into a balanced arrangement."),
         (["]]][[["], "The deepest prefix deficit is three, so two arbitrary-position swaps are necessary and sufficient.")],
        [[s] for s in ["[]","][","[[]]","[][]","]]][[[","][[]","[]][","]][][[",
                         "[[[]]]","[][][]","]][[","][[][]","[[]]][","]][[]["]],
        SWAPS,
        [SWAPS.replace("(deficit + 1) // 2", "deficit // 2"), SWAPS.replace("deficit = max(deficit, -balance)", "deficit += balance < 0")],
        ["Rounds an odd maximum deficit down instead of up.", "Counts every negative prefix rather than the maximum number of unmatched closing brackets."],
        swaps_oracle, random_swaps,
        lesson("The most negative prefix balance measures the maximum number of unmatched closing brackets seen at once.",
               "One arbitrary swap brings an opening bracket forward and can repair two units of maximum deficit, so round half the deficit upward.",
               "Scan balance (+1 for [, -1 for ]), retain deficit=max(deficit,-balance), return (deficit+1)//2.",
               "Each swap changes the affected prefix balance by two, giving the lower bound; swapping an early unmatched close with a later open repeatedly attains that bound."),
        "O(n)", "O(1)", 5),
}
