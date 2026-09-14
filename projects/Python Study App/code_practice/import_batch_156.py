"""Two windows, recursive matrix paths, range arithmetic, prefixes, and capability batch 156."""

from itertools import combinations

from .import_batch_055 import entry


def win_oracle(args):
    positions, k = args
    starts = {value for value in positions} | {value - k for value in positions}
    return max(
        sum(
            first <= value <= first + k or second <= value <= second + k
            for value in positions
        )
        for first in starts
        for second in starts
    )


def random_win(rng):
    return [
        sorted(rng.randint(1, 30) for _ in range(rng.randint(1, 16))),
        rng.randint(0, 10),
    ]


def has_path(grid):
    rows, columns = len(grid), len(grid[0])
    reachable = [[False] * columns for _ in range(rows)]
    reachable[0][0] = bool(grid[0][0])
    for row in range(rows):
        for column in range(columns):
            if grid[row][column] and (row or column):
                reachable[row][column] = (row > 0 and reachable[row - 1][column]) or (
                    column > 0 and reachable[row][column - 1]
                )
    return reachable[-1][-1]


def cut_oracle(args):
    grid = args[0]
    if not has_path(grid):
        return True
    for row in range(len(grid)):
        for column in range(len(grid[0])):
            if (row, column) in {(0, 0), (len(grid) - 1, len(grid[0]) - 1)}:
                continue
            changed = [line[:] for line in grid]
            changed[row][column] ^= 1
            if not has_path(changed):
                return True
    return False


def random_cut(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    grid = [[rng.randint(0, 1) for _ in range(columns)] for _ in range(rows)]
    grid[0][0] = grid[-1][-1] = 1
    return [grid]


def range_oracle(args):
    banned, n, maximum = args
    forbidden = set(banned)
    total = count = 0
    for value in range(1, n + 1):
        if value not in forbidden and total + value <= maximum:
            total += value
            count += 1
    return count


def random_range(rng):
    n = rng.randint(1, 100)
    return [
        [rng.randint(1, n + 20) for _ in range(rng.randint(0, 20))],
        n,
        rng.randint(0, 1000),
    ]


def vowels_oracle(args):
    words, queries = args
    vowels = set("aeiou")
    return [
        sum(
            word[0] in vowels and word[-1] in vowels for word in words[left : right + 1]
        )
        for left, right in queries
    ]


def random_vowels(rng):
    count = rng.randint(1, 20)
    words = [
        "".join(rng.choice("abcdeiou") for _ in range(rng.randint(1, 8)))
        for _ in range(count)
    ]
    queries = []
    for _ in range(rng.randint(1, 15)):
        left, right = sorted((rng.randrange(count), rng.randrange(count)))
        queries.append([left, right])
    return [words, queries]


def capability_oracle(args):
    nums, k = args
    return min(
        max(nums[index] for index in chosen)
        for size in range(k, len(nums) + 1)
        for chosen in combinations(range(len(nums)), size)
        if all(right > left + 1 for left, right in zip(chosen, chosen[1:]))
    )


def random_capability(rng):
    n = rng.randint(1, 12)
    return [[rng.randint(1, 40) for _ in range(n)], rng.randint(1, (n + 1) // 2)]


WIN = """\
def maximize_two_prize_segments(prize_positions,k):
    n=len(prize_positions);best_prefix=[0]*(n+1);answer=0;left=0
    for right,value in enumerate(prize_positions):
        while value-prize_positions[left]>k:left+=1
        window=right-left+1
        answer=max(answer,window+best_prefix[left])
        best_prefix[right+1]=max(best_prefix[right],window)
    return answer
"""

CUT = """\
def can_disconnect_down_right_path(grid):
    rows=len(grid);columns=len(grid[0])
    def erase(row,column):
        if row>=rows or column>=columns or not grid[row][column]:return False
        if row==rows-1 and column==columns-1:return True
        grid[row][column]=0
        return erase(row+1,column) or erase(row,column+1)
    first=erase(0,0);grid[0][0]=grid[-1][-1]=1
    second=erase(0,0)
    return not(first and second)
"""

RANGE = """\
def maximum_allowed_range_count_large(banned,n,max_sum):
    blocked=sorted({value for value in banned if 1<=value<=n})+[n+1]
    previous=0;answer=0
    for stop in blocked:
        available=stop-previous-1
        low=0;high=available
        while low<high:
            count=(low+high+1)//2
            cost=(previous+1+previous+count)*count//2
            if cost<=max_sum:low=count
            else:high=count-1
        answer+=low;max_sum-=(previous+1+previous+low)*low//2
        if low<available:return answer
        previous=stop
    return answer
"""

VOWELS = """\
def count_vowel_words_in_ranges(words,queries):
    vowels=set('aeiou');prefix=[0]
    for word in words:prefix.append(prefix[-1]+(word[0] in vowels and word[-1] in vowels))
    return [prefix[right+1]-prefix[left] for left,right in queries]
"""

CAPABILITY = """\
def minimum_robbery_capability(nums,k):
    def possible(limit):
        robbed=0;previous=-2
        for index,value in enumerate(nums):
            if value<=limit and index>previous+1:robbed+=1;previous=index
        return robbed>=k
    low=min(nums);high=max(nums)
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return low
"""


BATCH = {
    2555: entry(
        "maximize_two_prize_segments",
        [("prize_positions", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "sliding window", "dynamic programming"],
        [
            "Prize positions are sorted and may repeat.",
            "Choose two inclusive coordinate segments of length k; they may overlap.",
            "Return the maximum number of prizes covered by their union.",
        ],
        [
            (
                [[1, 1, 2, 2, 3, 3, 5], 2],
                "Segments [1,3] and [3,5] cover all seven prizes.",
            ),
            (
                [[1, 2, 3, 4], 0],
                "Each zero-length segment covers one distinct position, so two prizes can be collected.",
            ),
        ],
        [
            [p, k]
            for p, k in [
                ([1], 0),
                ([1, 1], 0),
                ([1, 2], 1),
                ([1, 3], 1),
                ([1, 2, 3], 1),
                ([1, 2, 3], 10),
                ([1, 1, 5, 5], 0),
                ([1, 2, 5, 6], 1),
                ([1, 2, 3, 10, 11], 2),
                ([2, 2, 2, 8, 8], 1),
                ([1, 4, 7, 10], 3),
                ([1, 2, 2, 3, 9, 10], 2),
                ([5, 5, 6, 7, 20, 21], 2),
                ([1, 3, 3, 5, 7, 9, 9], 2),
            ]
        ],
        WIN,
        [
            WIN.replace(">k", ">=k"),
            WIN.replace("best_prefix[left]", "best_prefix[right]"),
        ],
        [
            "Shrinks windows whose endpoint distance equals the allowed length.",
            "Combines the current segment with a prefix that may overlap it.",
        ],
        win_oracle,
        random_win,
        [
            "Use a sliding window for the best single segment ending at each prize.",
            "Store the best one-segment coverage for every completed prefix.",
            "Combine the current window with the best prefix ending before its left boundary.",
            "Every pair of segments can be ordered by right endpoint, and this scan evaluates its non-overlapping union without double counting.",
        ],
        "O(n)",
        "O(n)",
        6,
    ),
    2556: entry(
        "can_disconnect_down_right_path",
        [("grid", "list[list[int]]")],
        "bool",
        ["matrices", "recursion", "depth-first search"],
        [
            "Movement from the top-left to bottom-right is only down or right through cells containing one.",
            "You may flip at most one cell other than the endpoints.",
            "Return whether all such paths can be destroyed.",
        ],
        [
            (
                [[[1, 1, 1], [1, 0, 0], [1, 1, 1]]],
                "Every path uses a removable bottleneck, so one flip disconnects the endpoints.",
            ),
            (
                [[[1, 1, 1], [1, 1, 1]]],
                "Two internally disjoint routes remain, so one flip cannot disconnect them.",
            ),
        ],
        [
            [g]
            for g in [
                [[1]],
                [[1, 1]],
                [[1], [1]],
                [[1, 0], [0, 1]],
                [[1, 1], [1, 1]],
                [[1, 0, 1], [1, 1, 1]],
                [[1, 1, 1], [0, 0, 1]],
                [[1, 1, 0], [0, 1, 1]],
                [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
                [[1, 0, 0], [1, 1, 0], [0, 1, 1]],
                [[1, 1, 0], [1, 1, 1], [0, 1, 1]],
                [[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]],
                [[1, 0, 1, 1], [1, 1, 1, 0], [0, 1, 1, 1]],
                [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1]],
            ]
        ],
        CUT,
        [
            CUT.replace("grid[0][0]=grid[-1][-1]=1", "grid[-1][-1]=1"),
            CUT.replace("or erase(row,column+1)", "and erase(row,column+1)"),
        ],
        [
            "Fails to restore the start cell before searching for a second path.",
            "Requires both recursive branches instead of finding either valid path.",
        ],
        cut_oracle,
        random_cut,
        [
            "First find one down-right path and erase its internal cells during DFS.",
            "Restore the protected endpoints, then search again.",
            "If a second path exists after removing the first, no single internal cell intersects every path.",
            "Conversely, if no second path exists, one cell on the erased route is a separator, so the two DFS passes characterize one-flip disconnectability.",
        ],
        "O(rows times columns)",
        "O(rows+columns recursion)",
        6,
    ),
    2557: entry(
        "maximum_allowed_range_count_large",
        [("banned", "list[int]"), ("n", "int"), ("max_sum", "int")],
        "int",
        ["greedy", "binary search", "arithmetic series"],
        [
            "Choose distinct allowed integers from 1 through possibly very large n.",
            "The sum may not exceed max_sum; duplicate or out-of-range banned values are ignored.",
            "Return the maximum selection count without scanning the entire range.",
        ],
        [
            (
                [[1, 4, 6], 6, 4],
                "Only value two can be selected before any next allowed value exceeds the remaining sum.",
            ),
            (
                [[4, 3, 5, 6], 7, 18],
                "Values one, two, and seven total ten, and the remaining allowed choices exceed the budget for a fourth.",
            ),
        ],
        [
            [b, n, m]
            for b, n, m in [
                ([], 1, 1),
                ([], 5, 6),
                ([1], 5, 6),
                ([2], 5, 6),
                ([1, 1], 3, 5),
                ([10], 5, 15),
                ([1, 2, 3], 3, 100),
                ([2, 4], 6, 9),
                ([3, 6], 7, 12),
                ([1, 5, 9], 10, 20),
                ([2, 2, 8], 8, 15),
                ([4, 5, 6], 10, 25),
                ([1, 3, 5, 7, 9], 10, 30),
                ([20, 1, 2], 12, 40),
            ]
        ],
        RANGE,
        [
            RANGE.replace("+[n+1]", "+[n]"),
            RANGE.replace("cost<=max_sum", "cost<max_sum"),
        ],
        [
            "Uses n itself as a sentinel and can omit the allowed endpoint.",
            "Rejects an arithmetic prefix whose cost exactly equals the remaining budget.",
        ],
        range_oracle,
        random_range,
        [
            "Sort unique in-range banned values and treat gaps between them as consecutive allowed intervals.",
            "The cheapest count values in a gap form an arithmetic series.",
            "Binary-search how many values from each gap fit the remaining budget, then subtract their series sum.",
            "Greedy smallest-first selection is optimal for cardinality, and gap arithmetic skips arbitrarily large ranges safely.",
        ],
        "O(b log b log n)",
        "O(b)",
        6,
    ),
    2559: entry(
        "count_vowel_words_in_ranges",
        [("words", "list[str]"), ("queries", "list[list[int]]")],
        "list[int]",
        ["arrays", "strings", "prefix sums"],
        [
            "A vowel word starts and ends with a lowercase vowel.",
            "Each query [left,right] is an inclusive word-index range.",
            "Return the qualifying word count for every query.",
        ],
        [
            (
                [["aba", "bcb", "ece", "aa", "e"], [[0, 2], [1, 4], [1, 1]]],
                "Prefix differences give counts two, three, and zero.",
            ),
            ([["a", "e", "i"], [[0, 2]]], "All three one-letter vowel words qualify."),
        ],
        [
            [w, q]
            for w, q in [
                (["a"], [[0, 0]]),
                (["b"], [[0, 0]]),
                (["ab", "ba"], [[0, 1]]),
                (["aa", "bb", "ee"], [[0, 2]]),
                (["apple", "orange"], [[0, 1]]),
                (["abc", "ece", "iou"], [[1, 2]]),
                (["u", "x", "o"], [[0, 0], [1, 2]]),
                (["ae", "ea", "ii"], [[1, 1]]),
                (["cat", "eye", "area"], [[0, 2]]),
                (["a", "b", "e", "c", "i"], [[1, 3]]),
                (["oo", "no", "on"], [[0, 2]]),
                (["unit", "idea", "echo"], [[0, 1], [1, 2]]),
                (["a", "aa", "aaa", "b"], [[0, 3], [2, 2]]),
                (["ice", "owl", "emu", "ant"], [[0, 0], [0, 3]]),
            ]
        ],
        VOWELS,
        [
            VOWELS.replace("word[-1] in vowels", "word[-1] not in vowels"),
            VOWELS.replace("prefix[right+1]", "prefix[right]"),
        ],
        [
            "Counts words ending in consonants instead of vowels.",
            "Treats the inclusive query right endpoint as exclusive.",
        ],
        vowels_oracle,
        random_vowels,
        [
            "Convert each word to one when both boundary letters are vowels, otherwise zero.",
            "Build a prefix sum with a leading zero.",
            "For inclusive [left,right], subtract prefix[left] from prefix[right+1].",
            "Prefix differences contain exactly the indicator values in each query range, so queries become constant-time.",
        ],
        "O(total word count+queries)",
        "O(word count)",
        5,
    ),
    2560: entry(
        "minimum_robbery_capability",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "binary search", "greedy"],
        [
            "Rob at least k houses without choosing adjacent indices.",
            "Capability is the largest value among robbed houses.",
            "Return the minimum achievable capability.",
        ],
        [
            (
                [[2, 3, 5, 9], 2],
                "Houses zero and two are nonadjacent and cap the maximum robbed value at five.",
            ),
            (
                [[2, 7, 9, 3, 1], 2],
                "Robbing values two and one yields the minimum capability two.",
            ),
        ],
        [
            [a, k]
            for a, k in [
                ([1], 1),
                ([1, 2], 1),
                ([1, 2, 3], 2),
                ([3, 2, 1], 2),
                ([5, 5, 5], 2),
                ([1, 100, 1], 2),
                ([10, 1, 10, 1], 2),
                ([4, 2, 7, 3], 2),
                ([9, 8, 7, 6, 5], 3),
                ([2, 4, 1, 8, 3], 2),
                ([6, 1, 5, 2, 4, 3], 3),
                ([100, 1, 100, 1, 100], 3),
                ([3, 9, 2, 8, 1, 7], 3),
                ([5, 1, 4, 2, 3, 9, 1], 4),
            ]
        ],
        CAPABILITY,
        [
            CAPABILITY.replace("value<=limit", "value<limit"),
            CAPABILITY.replace("index>previous+1", "index>previous+2"),
        ],
        [
            "Rejects a house whose value equals the tested capability.",
            "Requires an unnecessary two-house gap between robberies.",
        ],
        capability_oracle,
        random_capability,
        [
            "Binary-search the capability threshold.",
            "For a fixed threshold, greedily rob the earliest eligible house and skip its neighbor.",
            "Count whether this scan reaches at least k houses.",
            "Feasibility is monotone, and choosing an earlier eligible house leaves at least as much room as any later choice, validating both greedy checking and binary search.",
        ],
        "O(n log value range)",
        "O(1)",
        6,
    ),
}
