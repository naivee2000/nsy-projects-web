"""Final reviewed group of workbook batch 110."""

from functools import lru_cache

from .import_batch_055 import entry


def difference_oracle(arguments):
    nums, queries = arguments
    answer = []
    for left, right in queries:
        values = sorted(set(nums[left:right + 1]))
        answer.append(min((values[index] - values[index - 1] for index in range(1, len(values))), default=-1))
    return answer


def nim_oracle(arguments):
    @lru_cache(maxsize=None)
    def winning(state):
        for index, stones in enumerate(state):
            for remaining in range(stones):
                candidate = state[:index] + (remaining,) + state[index + 1:]
                if not winning(candidate):
                    return True
        return False
    return winning(tuple(arguments[0]))


def increasing_oracle(arguments):
    nums = arguments[0]
    def strict(values):
        return all(values[index - 1] < values[index] for index in range(1, len(values)))
    return strict(nums) or any(strict(nums[:removed] + nums[removed + 1:]) for removed in range(len(nums)))


def occurrences_oracle(arguments):
    value, part = arguments
    while True:
        position = value.find(part)
        if position < 0:
            return value
        value = value[:position] + value[position + len(part):]


def alternating_oracle(arguments):
    nums = arguments[0]
    best = 0
    for mask in range(1 << len(nums)):
        chosen = [value for index, value in enumerate(nums) if mask >> index & 1]
        total = sum(value if index % 2 == 0 else -value for index, value in enumerate(chosen))
        best = max(best, total)
    return best


def random_difference(rng):
    nums = [rng.randint(1, 100) for _ in range(rng.randint(2, 25))]
    queries = []
    for _ in range(rng.randint(1, 12)):
        left = rng.randint(0, len(nums) - 2)
        queries.append([left, rng.randint(left + 1, len(nums) - 1)])
    return [nums, queries]


def random_nim(rng):
    return [[rng.randint(1, 5) for _ in range(rng.randint(1, 5))]]


def random_increasing(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(2, 12))]]


def random_occurrences(rng):
    part = "".join(rng.choice("ab") for _ in range(rng.randint(1, 4)))
    return ["".join(rng.choice("ab") for _ in range(rng.randint(1, 20))), part]


def random_alternating(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 12))]]


DIFFERENCE = '''\
def minimum_difference_queries(nums, queries):
    prefix = [[0] * 101 for _ in range(len(nums) + 1)]
    for index, value in enumerate(nums, 1):
        prefix[index] = prefix[index - 1][:]
        prefix[index][value] += 1
    answer = []
    for left, right in queries:
        previous = None
        best = 101
        for value in range(1, 101):
            if prefix[right + 1][value] > prefix[left][value]:
                if previous is not None:
                    best = min(best, value - previous)
                previous = value
        answer.append(-1 if best == 101 else best)
    return answer
'''

DIFFERENCE_DUPLICATES = '''\
def minimum_difference_queries(nums, queries):
    answer=[]
    for left,right in queries:
        values=sorted(nums[left:right+1])
        answer.append(min((values[i]-values[i-1] for i in range(1,len(values))),default=-1))
    return answer
'''

NIM = '''\
def first_player_wins_nim(piles):
    combined = 0
    for stones in piles:
        combined ^= stones
    return combined != 0
'''

NIM_TOTAL = '''\
def first_player_wins_nim(piles):
    return sum(piles) % 2 == 1
'''

NIM_ODD = '''\
def first_player_wins_nim(piles):
    return any(stones % 2 == 1 for stones in piles)
'''

INCREASING = '''\
def can_remove_one_for_strict_increase(nums):
    def valid_without(removed):
        previous = None
        for index, value in enumerate(nums):
            if index == removed:
                continue
            if previous is not None and previous >= value:
                return False
            previous = value
        return True
    violation = 0
    while violation + 1 < len(nums) and nums[violation] < nums[violation + 1]:
        violation += 1
    return valid_without(violation) or valid_without(violation + 1)
'''

REMOVE_RIGHT_ONLY = '''\
def can_remove_one_for_strict_increase(nums):
    for index in range(len(nums)-1):
        if nums[index] >= nums[index+1]:
            candidate=nums[:index+1]+nums[index+2:]
            return all(candidate[i-1]<candidate[i] for i in range(1,len(candidate)))
    return True
'''

OCCURRENCES = '''\
def remove_all_leftmost_occurrences(s, part):
    stack = []
    length = len(part)
    for char in s:
        stack.append(char)
        if len(stack) >= length and "".join(stack[-length:]) == part:
            del stack[-length:]
    return "".join(stack)
'''

REMOVE_ONCE = '''\
def remove_all_leftmost_occurrences(s, part):
    return s.replace(part, "", 1)
'''

REMOVE_RIGHTMOST = '''\
def remove_all_leftmost_occurrences(s, part):
    while part in s:
        index=s.rfind(part);s=s[:index]+s[index+len(part):]
    return s
'''

ALTERNATING = '''\
def maximum_alternating_subsequence_sum(nums):
    addition = 0
    subtraction = 0
    for value in nums:
        next_addition = max(addition, subtraction + value)
        next_subtraction = max(subtraction, addition - value)
        addition, subtraction = next_addition, next_subtraction
    return addition
'''

ALTERNATING_ALL = '''\
def maximum_alternating_subsequence_sum(nums):
    return sum(value if index % 2 == 0 else -value for index,value in enumerate(nums))
'''

ALTERNATING_ONE = '''\
def maximum_alternating_subsequence_sum(nums):
    return max(nums)
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1906: entry(
        "minimum_difference_queries", [("nums", "list[int]"), ("queries", "list[list[int]]")], "list[int]",
        ["arrays", "prefix-sums", "queries"],
        ["2 <= len(nums) <= 100000 and every value is from 1 through 100.",
         "There are at most 20000 inclusive [left,right] queries with left < right.",
         "For each range, compare distinct values; return -1 when fewer than two distinct values occur."],
        [([[1,3,4,8],[[0,1],[1,2],[2,3],[0,3]]], "The distinct-value gaps in the four ranges are 2, 1, 4, and 1."),
         ([[4,5,2,2,7,10],[[2,3],[0,2],[0,5],[3,5]]], "The first range has only value two, while the other minimum gaps are 1, 1, and 3.")],
        [[nums,queries] for nums,queries in [
            ([1,1],[[0,1]]),([1,2],[[0,1]]),([1,3,4,8],[[0,3]]),
            ([1,3,4,8],[[0,1],[1,2],[2,3],[0,3]]),([4,5,2,2,7,10],[[2,3],[0,2],[0,5],[3,5]]),
            ([100,1,50],[[0,2]]),([5,5,5,6],[[0,2],[0,3]]),([1,100,1,100],[[0,3]]),
            ([2,4,6,8,10],[[1,3]]),([9,3,9,4],[[0,3]]),([7,7,8,9],[[0,1],[0,3]]),
            ([1,2,2,3],[[1,2],[0,3]]),([20,10,30,10],[[0,3]]),([6,1,6,2,6],[[1,4]]),
        ]],
        DIFFERENCE,
        [DIFFERENCE_DUPLICATES, DIFFERENCE.replace("prefix[right + 1][value]", "prefix[right][value]")],
        ["Treats equal duplicate values as a valid pair with difference zero.",
         "Excludes the query's right endpoint from its frequency range."],
        difference_oracle, random_difference,
        lesson("The small value bound allows a prefix-frequency table for values 1 through 100.",
               "For each query, scan values in order and test presence by subtracting two prefix counts.",
               "The minimum difference must occur between consecutive present distinct values.",
               "Prefix subtraction exactly identifies the range's value set, and sorted consecutive gaps contain the minimum pairwise distance."),
        "O((len(nums)+queries)*100)", "O(len(nums)*100)", 6),
    1908: entry(
        "first_player_wins_nim", [("piles", "list[int]")], "bool",
        ["arrays", "bit-manipulation", "game-theory", "recursion"],
        ["There are 1 through 7 nonempty piles, each containing 1 through 7 stones.",
         "A move removes any positive number of stones from exactly one pile.",
         "The player unable to move loses; both players play optimally."],
        [([[1]], "Alice removes the only stone and Bob has no move."),
         ([[1,1]], "Whatever Alice removes, Bob mirrors by emptying the other pile, so Alice loses.")],
        [[piles] for piles in [
            [1],[1,1],[1,2],[2,2],[1,2,3],[3,4,5],[7,7,7],[4,4,4,4],
            [1,1,1],[2,3],[5,6],[1,3,5,7],[2,4,6],[7,1,2],
        ]],
        NIM,
        [NIM_TOTAL, NIM_ODD],
        ["Uses the parity of the total stones, which does not characterize multi-pile Nim positions.",
         "Assumes any odd-sized pile guarantees a win instead of combining pile Grundy values."],
        nim_oracle, random_nim,
        lesson("Each pile's Grundy value is its size because a move can reach every smaller size.",
               "Combine independent piles with bitwise XOR.",
               "A nonzero XOR lets the current player move to zero; every move from zero makes it nonzero.",
               "Those paired invariants make zero-XOR states losing and every nonzero-XOR state winning under optimal play."),
        "O(number of piles)", "O(1)", 6),
    1909: entry(
        "can_remove_one_for_strict_increase", [("nums", "list[int]")], "bool",
        ["arrays", "greedy"],
        ["2 <= len(nums) <= 1000 and values are positive.",
         "The remaining sequence must be strictly increasing.",
         "Return true when the input already qualifies or can qualify after removing at most one element."],
        [([[1,2,10,5,7]], "Removing ten leaves 1,2,5,7, which is strictly increasing."),
         ([[2,3,1,2]], "Removing either side of the first violation still leaves another violation.")],
        [[nums] for nums in [
            [1,2],[2,1],[1,2,10,5,7],[2,3,1,2],[1,1],[1,2,3],[3,2,1],
            [1,3,2],[1,2,2,3],[10,1,2,3],[1,2,3,0],[1,5,3,4],
            [1,4,2,3,5],[5,6,7,4,8],[1,2,5,3,4],[1,1,2,2],
        ]],
        INCREASING,
        [INCREASING.replace("previous >= value", "previous > value"), REMOVE_RIGHT_ONLY],
        ["Accepts equal adjacent values by checking nondecreasing rather than strictly increasing order.",
         "Tries removing only the right side of the first violation, though sometimes the left value must be removed."],
        increasing_oracle, random_increasing,
        lesson("Only the first non-increasing adjacent pair can require a removal.",
               "Try omitting either endpoint of that pair and scan the remainder for strict increase.",
               "If the array has no violation, either check already succeeds.",
               "Any one-element repair must remove an endpoint of the first violation, so the two checks are exhaustive and sufficient."),
        "O(n)", "O(1)", 3),
    1910: entry(
        "remove_all_leftmost_occurrences", [("s", "str"), ("part", "str")], "str",
        ["strings", "stacks", "simulation"],
        ["s and part are nonempty lowercase strings of length at most 1000.",
         "Repeatedly remove the current leftmost occurrence of part.",
         "Continue until no occurrence remains, including occurrences newly formed by earlier removals."],
        [(["daabcbaabcbc","abc"], "Removing the two abc occurrences and then the newly formed abc leaves dab."),
         (["axxxxyyyyb","xy"], "Four repeated leftmost removals consume every x-y boundary pair and leave ab.")],
        [[s,part] for s,part in [
            ("a","a"),("abc","x"),("daabcbaabcbc","abc"),("axxxxyyyyb","xy"),
            ("aaaaa","aa"),("ababa","aba"),("mississippi","issi"),("abcabc","abc"),
            ("cabba","bb"),("abababab","ab"),("baaab","aa"),("cccbcc","cb"),
            ("xyzxyzx","yzx"),("aabbaabb","aab"),
        ]],
        OCCURRENCES,
        [REMOVE_ONCE, REMOVE_RIGHTMOST],
        ["Removes only the first occurrence and stops before newly exposed matches are processed.",
         "Removes the rightmost occurrence first, which can produce a different final string when matches overlap."],
        occurrences_oracle, random_occurrences,
        lesson("Characters before the current scan point are final except for a suffix that may complete part.",
               "Push each character, and whenever the stack suffix equals part, delete that suffix immediately.",
               "Join the remaining stack after the scan.",
               "Immediate suffix deletion reproduces the next leftmost available removal; induction over consumed input characters proves equivalence to the repeated process."),
        "O(len(s)*len(part))", "O(len(s))", 5),
    1911: entry(
        "maximum_alternating_subsequence_sum", [("nums", "list[int]")], "int",
        ["arrays", "dynamic-programming", "subsequences"],
        ["There are 1 through 100000 positive values.",
         "For a chosen subsequence, add values at positions 0,2,4,... and subtract values at positions 1,3,5,....",
         "Preserve original order while maximizing the resulting alternating sum."],
        [([[4,2,5,3]], "Choosing 4,2,5 gives alternating sum 4-2+5 = 7."),
         ([[5,6,7,8]], "Choosing 8 alone gives the maximum value eight.")],
        [[nums] for nums in [
            [1],[4,2,5,3],[5,6,7,8],[6,2,1,2,4,5],[1,1],[1,2],[2,1],
            [10,1,10],[3,8,2,9],[9,8,7,6],[1,3,2,4,3,5],[5,1,4,2,3],
            [100,1,1,100],[7,3,5,1,6],
        ]],
        ALTERNATING,
        [ALTERNATING_ALL, ALTERNATING_ONE],
        ["Forces every input value into the subsequence instead of allowing elements to be skipped.",
         "Chooses only one value and misses profitable add-subtract-add combinations."],
        alternating_oracle, random_alternating,
        lesson("Track the best sum after an even-position addition and after an odd-position subtraction.",
               "For each value, either skip it, add it after a subtraction state, or subtract it after an addition state.",
               "Update both states from the previous pair and return the best addition state.",
               "These states partition all subsequences by their next sign, and the transitions cover both choosing and skipping each value."),
        "O(n)", "O(1)", 6),
}
