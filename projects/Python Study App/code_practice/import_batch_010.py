"""Reviewed duplicate-aware search, string DP, and resource-allocation contracts."""
from itertools import combinations
import posixpath

from .import_batch_003 import entry


def path_oracle(args):
    # POSIX normpath deliberately preserves exactly two leading slashes;
    # this problem instead mandates one, so normalize that prefix first.
    return posixpath.normpath("/" + args[0].lstrip("/"))


def search_oracle(args):
    return args[1] in args[0]


def interleave_oracle(args):
    first, second, result = args
    if len(first) + len(second) != len(result):
        return False
    for chosen in combinations(range(len(result)), len(first)):
        selected = set(chosen)
        if ("".join(result[i] for i in chosen) == first
                and "".join(char for i, char in enumerate(result) if i not in selected) == second):
            return True
    return False


def subsequences_oracle(args):
    source, target = args
    return sum("".join(source[i] for i in indexes) == target
               for indexes in combinations(range(len(source)), len(target)))


def unlimited_oracle(args):
    prices = args[0]
    # Exhaust every buy/sell/wait history on small inputs, rather than summing
    # positive changes as the reference does. Same-day round trips add zero.
    def choose(day, holding):
        if day == len(prices):
            return -float("inf") if holding else 0
        wait = choose(day + 1, holding)
        trade = (prices[day] if holding else -prices[day]) + choose(day + 1, not holding)
        return max(wait, trade)
    return choose(0, False)


def two_trades_oracle(args):
    prices = args[0]
    candidates = [0]
    candidates.extend(prices[sell] - prices[buy] for buy, sell in combinations(range(len(prices)), 2))
    candidates.extend(prices[b] - prices[a] + prices[d] - prices[c]
                      for a, b, c, d in combinations(range(len(prices)), 4))
    # Trades touching on the same day can be merged without changing profit,
    # so strict four-day pairs plus all single trades cover that case too.
    return max(candidates)


def feasible_starts(gas, cost):
    valid = []
    for start in range(len(gas)):
        tank = 0
        for offset in range(len(gas)):
            index = (start + offset) % len(gas)
            tank += gas[index] - cost[index]
            if tank < 0:
                break
        else:
            valid.append(start)
    return valid


def gas_oracle(args):
    candidates = feasible_starts(*args)
    if len(candidates) > 1:
        raise ValueError("Gas Station source contract guarantees a unique feasible start")
    return candidates[0] if candidates else -1


def candy_oracle(args):
    ratings = args[0]
    candies = [1] * len(ratings)
    # Least fixed point of all neighbor lower bounds, independent of the
    # reference's directional two-pass invariant. Ratings strictly orient
    # dependencies, so repeated relaxation terminates without a cycle.
    changed = True
    while changed:
        changed = False
        for index in range(len(ratings)):
            lower = 1
            for neighbor in (index - 1, index + 1):
                if 0 <= neighbor < len(ratings) and ratings[index] > ratings[neighbor]:
                    lower = max(lower, candies[neighbor] + 1)
            if lower > candies[index]:
                candies[index] = lower
                changed = True
    return sum(candies)


def random_path(rng):
    names = ("a", "b", "ABC", "file_1", ".", "..", "...", "....", ".cache", "x.y")
    path = "/" * rng.randint(1, 4)
    for _ in range(rng.randrange(15)):
        path += rng.choice(names) + "/" * rng.randint(1, 4)
    return [path if rng.random() < .5 else path.rstrip("/") or "/"]


def random_rotated(rng):
    values = sorted(rng.randint(-10, 10) for _ in range(rng.randint(1, 60)))
    pivot = rng.randrange(len(values))
    target = rng.choice(values) if rng.random() < .6 else rng.randint(-15, 15)
    return [values[pivot:] + values[:pivot], target]


def random_interleave(rng):
    first = "".join(rng.choice("abc") for _ in range(rng.randrange(7)))
    second = "".join(rng.choice("abc") for _ in range(rng.randrange(7)))
    if rng.random() < .6:
        i = j = 0
        pieces = []
        while i < len(first) or j < len(second):
            if i < len(first) and (j == len(second) or rng.random() < .5):
                pieces.append(first[i])
                i += 1
            else:
                pieces.append(second[j])
                j += 1
        result = "".join(pieces)
    else:
        result = "".join(rng.choice("abc") for _ in range(rng.randrange(14)))
    return [first, second, result]


def random_subsequences(rng):
    return ["".join(rng.choice("abAB") for _ in range(rng.randint(1, 12))),
            "".join(rng.choice("abAB") for _ in range(rng.randint(1, 8)))]


def random_prices(rng):
    return [[rng.randrange(21) for _ in range(rng.randint(1, 10))]]


def random_gas(rng):
    for _ in range(1000):
        size = rng.randint(1, 10)
        args = [[rng.randrange(9) for _ in range(size)], [rng.randrange(9) for _ in range(size)]]
        if len(feasible_starts(*args)) <= 1:
            return args
    raise ValueError("Could not generate a unique-or-impossible circuit")


def random_candy(rng):
    return [[rng.randrange(11) for _ in range(rng.randint(1, 15))]]


PATH = '''\
def simplify_path(path):
    names = []
    for part in path.split("/"):
        if part == "..":
            if names:
                names.pop()
        elif part not in ("", "."):
            names.append(part)
    return "/" + "/".join(names)
'''
SEARCH = '''\
def rotated_contains(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return True
        if nums[left] == nums[mid] == nums[right]:
            left += 1
            right -= 1
        elif nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return False
'''
INTERLEAVE = '''\
def is_interleave(s1, s2, s3):
    if len(s1) + len(s2) != len(s3):
        return False
    possible = [True] + [False] * len(s2)
    for i in range(len(s1) + 1):
        for j in range(len(s2) + 1):
            if i == j == 0:
                continue
            possible[j] = ((i > 0 and possible[j] and s1[i - 1] == s3[i + j - 1])
                           or (j > 0 and possible[j - 1] and s2[j - 1] == s3[i + j - 1]))
    return possible[-1]
'''
GREEDY_INTERLEAVE = '''\
def is_interleave(s1, s2, s3):
    i = j = 0
    for char in s3:
        if i < len(s1) and s1[i] == char:
            i += 1
        elif j < len(s2) and s2[j] == char:
            j += 1
        else:
            return False
    return i == len(s1) and j == len(s2)
'''
SUBSEQUENCES = '''\
def count_subsequences(s, t):
    ways = [1] + [0] * len(t)
    for char in s:
        for length in range(len(t), 0, -1):
            if char == t[length - 1]:
                ways[length] += ways[length - 1]
    return ways[-1]
'''
UNLIMITED = '''\
def stock_profit_unlimited(prices):
    return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices)))
'''
TWO_TRADES = '''\
def stock_profit_two(prices):
    buy1 = buy2 = -prices[0]
    sell1 = sell2 = 0
    for price in prices:
        buy1 = max(buy1, -price)
        sell1 = max(sell1, buy1 + price)
        buy2 = max(buy2, sell1 - price)
        sell2 = max(sell2, buy2 + price)
    return sell2
'''
SINGLE_TRADE = '''\
def stock_profit_unlimited(prices):
    low, best = prices[0], 0
    for price in prices:
        low = min(low, price)
        best = max(best, price - low)
    return best
'''
GAS = '''\
def gas_station_start(gas, cost):
    total = tank = start = 0
    for index, (fuel, expense) in enumerate(zip(gas, cost)):
        delta = fuel - expense
        total += delta
        tank += delta
        if tank < 0:
            start = index + 1
            tank = 0
    return start if total >= 0 else -1
'''
CANDY = '''\
def minimum_candies(ratings):
    candies = [1] * len(ratings)
    for i in range(1, len(ratings)):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1
    for i in range(len(ratings) - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)
    return sum(candies)
'''

BATCH = {
    71: entry("simplify_path", [("path", "str")], "str", ["strings", "stacks"],
        ["1–3000 characters, starting with '/'; characters are English letters, digits, '.', '/', or '_'.",
         "Ignore empty components and '.'. '..' removes a preceding component if one exists; it cannot go above root.",
         "Other components, including '...' and '.cache', are literal names. Return one leading slash, single separators, and no trailing slash except for root '/'. No filesystem access is needed."],
        [(["/home/"], "Remove the trailing separator to obtain /home."),
         (["/.../a/../b/c/../d/./"], "Keep the literal directory ..., cancel a and c with their following .., and ignore .; the result is /.../b/d.")],
        [[path] for path in ("/", "//", "/../", "/../../a", "/a/./b", "/a//b///c/", "/a/b/../../", "/a/../../b", "/...", "/.cache/file_1", "/a/.../..", "/a/..b/....")],
        PATH,
        [PATH.replace("names.pop()", "pass"), PATH.replace('part not in ("", ".")', 'part != "" and not part.startswith(".")')],
        ["Ignores parent-directory components without removing the preceding directory.", "Treats all dot-prefixed names as navigation rather than literal names."],
        path_oracle, random_path,
        ["Resolve whole components between slashes, not individual dot characters.", "Keep the currently resolved directory names on a stack.",
         "Skip empty and '.' components, pop for '..' when possible, otherwise append the literal name; join with one leading slash.",
         "Root remains '/'. Names like '...' and '.cache' must survive unless a later '..' removes them."],
        "Split at slashes and maintain a stack of resolved directory names. A parent component cancels the newest surviving name, while a current-directory or empty component changes nothing. Join the stack under one leading slash. This is lexical normalization only, independent of actual files or symlinks. The oracle uses posixpath.normpath after normalizing its special double-leading-slash behavior to the problem's single-root rule.",
        "O(len(path))", "O(len(path))", difficulty=5),
    81: entry("rotated_contains", [("nums", "list[int]"), ("target", "int")], "bool", ["arrays", "binary-search"],
        ["1–5000 integers, each between -10000 and 10000; target is in the same numeric range.",
         "nums is a rotation of a nondecreasing array and may contain duplicates. Return a Boolean, not an index.",
         "Discard a sorted half when comparisons determine it; equal boundary/middle values may require shrinking the search interval one step."],
        [([[2, 5, 6, 0, 0, 1, 2], 0], "Zero occurs twice, so return True regardless of which matching position is found."),
         ([[2, 5, 6, 0, 0, 1, 2], 3], "Neither sorted portion contains 3, so return False.")],
        [[[1], 1], [[1], 0], [[1, 1, 1], 1], [[1, 1, 1], 2], [[1, 0, 1, 1, 1], 0],
         [[1, 1, 1, 0, 1], 0], [[3, 1], 1], [[1, 3], 3], [[1, 1, 3, 1], 3],
         [[-1, 0, 0, -3, -2], -3], [[2, 2, 3, 0, 1, 2], 4], [[0, 0, 0, 1, 0], 1]],
        SEARCH, [SEARCH.replace("if nums[left] == nums[mid] == nums[right]:", "if False:"),
                 SEARCH.replace("while left <= right:", "while left < right:")],
        ["Assumes distinct values, discarding the target hidden behind equal boundaries.", "Never checks the final remaining position."],
        search_oracle, random_rotated,
        ["One side is normally sorted, but duplicates can hide which side contains the rotation.",
         "Check the middle first. If left, middle, and right are equal, remove the two checked boundary values.",
         "Otherwise identify a sorted half, test whether its value interval includes the target, and keep only the relevant half.",
         "Do not promise worst-case logarithmic time: many equal values can force linear shrinking."],
        "Binary search normally identifies one sorted half from boundary and middle comparisons. If both boundaries equal the middle and the middle is not the target, both boundaries can be safely removed, but no entire half is justified. Otherwise use the sorted half's inclusive/exclusive value interval to choose the next search range. An interval with one element must still be checked. The independent oracle uses direct membership rather than interval elimination.",
        "O(log n) when halves are distinguishable; O(n) worst case with duplicates", "O(1)", difficulty=5,
        stress=[([[1] * 5000, 0], False)]),
    97: entry("is_interleave", [("s1", "str"), ("s2", "str"), ("s3", "str")], "bool", ["strings", "dynamic-programming"],
        ["s1 and s2 have 0–100 lowercase letters; s3 has 0–200 lowercase letters.",
         "Use every character of s1 and s2 exactly once while preserving each source's internal order. Characters may be taken from either source at each step."],
        [(["aabcc", "dbbca", "aadbbcbcac"], "The chunks aa + dbbc + bc + a + c alternate sources and preserve both source orders."),
         (["aabcc", "dbbca", "aadbbbaccc"], "The character counts fit, but no assignment of positions preserves both source orders, so return False.")],
        [["", "", ""], ["a", "", "a"], ["", "b", "b"], ["a", "b", "ab"], ["a", "b", "ba"],
         ["a", "b", "aa"], ["a", "b", "a"], ["ab", "cd", "acbd"], ["ab", "cd", "adbc"],
         ["aab", "aac", "aacaab"], ["aa", "aa", "aaaa"], ["abc", "", "cba"]],
        INTERLEAVE, [GREEDY_INTERLEAVE, "def is_interleave(s1, s2, s3):\n    return sorted(s1 + s2) == sorted(s3)\n"],
        ["Always consumes from the first source when both next characters match, losing valid alternate choices.", "Checks only character multiplicities and ignores ordering."],
        interleave_oracle, random_interleave,
        ["If both sources can supply the next character, a greedy choice can be wrong.",
         "Let a state say whether prefixes s1[:i] and s2[:j] can form s3[:i+j].",
         "A state is reachable from the previous s1 prefix or previous s2 prefix when the added character matches; update one row left-to-right.",
         "Reject unequal total length immediately, and initialize the empty-prefix state to True."],
        "A prefix state may consume its final character from either source. Combine both valid predecessor states with OR, preserving alternatives when characters repeat. With one row, the old current-column value represents the preceding s1 prefix and the already-updated left value represents the preceding s2 prefix. The length check and empty-prefix initialization cover empty inputs. The oracle independently enumerates positions assigned to s1 and checks the complementary positions against s2.",
        "O((len(s1)+1) × (len(s2)+1))", "O(len(s2)+1)", difficulty=5,
        stress=[(["a" * 100, "b" * 100, "ab" * 100], True), (["a" * 100, "b" * 100, "a" * 100 + "b" * 99 + "c"], False)]),
    115: entry("count_subsequences", [("s", "str"), ("t", "str")], "int", ["strings", "dynamic-programming"],
        ["1–1000 English letters per string, with uppercase and lowercase distinguished.",
         "Count strictly increasing index selections from s whose characters spell t; different index selections count separately even when their resulting text is identical.",
         "The final answer is guaranteed to fit a signed 32-bit integer; do not clamp, reduce modulo a number, or turn the count into a Boolean."],
        [(["rabbbit", "rabbit"], "Choose any two of the three consecutive b positions; the other letters are fixed, giving three index selections."),
         (["babgbag", "bag"], "The first b supports three choices of later a/g; the middle b supports one, and the final b supports one, totaling five.")],
        [["a", "a"], ["a", "b"], ["a", "aa"], ["aaa", "a"], ["aaa", "aa"], ["aaaa", "aa"],
         ["abc", "abc"], ["abc", "ac"], ["abc", "ca"], ["AaA", "AA"], ["AaA", "aa"], ["ababa", "aba"]],
        SUBSEQUENCES, [SUBSEQUENCES.replace("range(len(t), 0, -1)", "range(1, len(t) + 1)"),
                       SUBSEQUENCES.replace("return ways[-1]", "return int(ways[-1] > 0)")],
        ["Updates prefix lengths forward, using the same source position more than once.", "Counts only whether the target exists, not the number of index choices."],
        subsequences_oracle, random_subsequences,
        ["Count ways to form each target prefix using source characters processed so far.",
         "There is one way to form the empty target. A matching source character adds the count for the preceding target prefix.",
         "For each source character, iterate target lengths downward and add ways[length-1] when the last target character matches.",
         "The downward update is essential: it prevents a single source character from filling multiple target positions."],
        "Maintain one count per target-prefix length, initially one for the empty prefix and zero otherwise. A source character may be skipped or used to extend a matching shorter prefix. Process target lengths from right to left so every extension uses counts from before the current source position. The result counts index selections, not distinct resulting strings. Python integers preserve intermediate counts exactly; only the final result has the source's 32-bit guarantee. The independent oracle enumerates fixed-size combinations of source indexes.",
        "O(len(s) × len(t)) arithmetic updates", "O(len(t)) integer counters", difficulty=8,
        stress=[(["a" * 1000, "a" * 1000], 1), (["a" * 1000, "b" * 1000], 0)]),
    122: entry("stock_profit_unlimited", [("prices", "list[int]")], "int", ["arrays", "greedy"],
        ["1–30000 prices, each between 0 and 10000.", "Make any number of transactions while holding at most one share. Selling and buying again on the same day is allowed; doing nothing earns zero."],
        [([[7, 1, 5, 3, 6, 4]], "Buy at 1 and sell at 5 for 4, then buy at 3 and sell at 6 for 3; total profit is 7."),
         ([[1, 2, 3, 4, 5]], "Holding from 1 to 5 earns 4, the same as collecting the four consecutive rises.")],
        [[[0]], [[9]], [[1, 2]], [[2, 1]], [[2, 2]], [[1, 3, 1, 3]], [[3, 1, 4, 0, 5]],
         [[5, 4, 3, 2, 1]], [[0, 0, 1, 1]], [[2, 5, 2, 5, 2, 5]], [[10000, 0, 10000]], [[1, 5, 4, 6]]],
        UNLIMITED, [SINGLE_TRADE, UNLIMITED.replace("max(0, prices[i] - prices[i - 1])", "abs(prices[i] - prices[i - 1])")],
        ["Allows only one trade, missing profits from separated rises.", "Treats falling prices as profitable rises."],
        unlimited_oracle, random_prices,
        ["With no transaction cap or fee, separated rises can be collected independently.", "Sum positive differences between consecutive days.",
         "For each adjacent pair add after-before only if after is greater; otherwise add zero.",
         "A long increasing run telescopes to its last price minus its first, so this does not require holding multiple shares."],
        "Collect every positive adjacent change and ignore negative changes. Consecutive positive changes telescope into one buy-low/sell-high trade, and a sell followed by a buy on the same day is permitted. No feasible one-share strategy benefits from holding across an avoidable decline, so this total is optimal. The oracle exhausts all buy, sell, and wait choices on short price histories rather than using this greedy identity.",
        "O(n)", "O(1)", difficulty=5,
        stress=[([[0, 10000] * 15000], 150000000)]),
    123: entry("stock_profit_two", [("prices", "list[int]")], "int", ["arrays", "dynamic-programming"],
        ["1–100000 prices, each between 0 and 100000.", "Complete at most two buy-then-sell transactions. Hold at most one share, selling it before buying another. Zero or one transaction is also allowed."],
        [([[3, 3, 5, 0, 0, 3, 1, 4]], "Buy at 0 and sell at 3, then buy at 1 and sell at 4, for total profit 6."),
         ([[1, 2, 3, 4, 5]], "One trade from 1 to 5 earns 4; using the second trade is optional.")],
        [[[0]], [[5]], [[1, 2]], [[2, 1]], [[2, 2]], [[1, 3, 1, 3]], [[1, 3, 1, 3, 1, 3]],
         [[7, 6, 4, 3, 1]], [[3, 1, 4, 0, 5]], [[0, 100000, 0, 100000]], [[5, 1, 5, 0, 10]], [[1, 5, 4, 6]]],
        TWO_TRADES, [TWO_TRADES.replace("return sell2", "return sell1"),
                     UNLIMITED.replace("stock_profit_unlimited", "stock_profit_two")],
        ["Returns only the first completed-trade state.", "Collects unlimited rises and can exceed the two-transaction allowance."],
        two_trades_oracle, random_prices,
        ["Track whether the first or second transaction has been bought or sold.", "Four running states hold the best balance after buy1, sell1, buy2, and sell2.",
         "At each price, maximize buy1 with -price, sell1 with buy1+price, buy2 with sell1-price, and sell2 with buy2+price.",
         "The second purchase includes the first sale's profit; two independent global best trades could overlap illegally."],
        "The four states summarize all useful histories after each day without storing a table. A purchase subtracts today's price from the best eligible cash balance; a sale adds it to the best corresponding holding balance. Keeping prior state values represents waiting. Same-day zero-length transitions cannot improve profit improperly and allow the second-sale state to represent fewer than two trades. The oracle independently enumerates every single transaction and every ordered pair of nonoverlapping transactions.",
        "O(n)", "O(1)", difficulty=8,
        stress=[([[0, 100000] * 50000], 200000)]),
    134: entry("gas_station_start", [("gas", "list[int]"), ("cost", "list[int]")], "int", ["arrays", "greedy"],
        ["Arrays have equal length from 1 to 100000; every gas/cost value is between 0 and 10000.",
         "Start with an empty unlimited tank, collect gas at each station, then pay its outgoing cost. Complete a full clockwise circuit without a negative tank.",
         "Return the unique valid zero-based start if one exists; otherwise return -1. Inputs never have multiple valid starts."],
        [([[1, 2, 3, 4, 5], [3, 4, 5, 1, 2]], "Starting at index 3 leaves balances 3,6,4,2,0 after successive legs, completing the circle."),
         ([[2, 3, 4], [3, 4, 3]], "Total fuel is 9 while total cost is 10, so every starting choice fails.")],
        [[[0], [0]], [[0], [1]], [[2], [1]], [[1], [1]], [[0, 1], [1, 0]], [[1, 0], [0, 1]],
         [[1, 2], [2, 1]], [[0, 0, 3], [1, 1, 1]], [[3, 0, 0], [1, 1, 1]],
         [[0, 3, 0], [1, 1, 1]], [[1, 1, 1], [2, 2, 2]], [[2, 0, 1], [0, 3, 0]]],
        GAS, [GAS.replace("return start if total >= 0 else -1", "return start % len(gas)"),
              "def gas_station_start(gas, cost):\n    return -1 if sum(gas) < sum(cost) else max(range(len(gas)), key=lambda i: gas[i] - cost[i])\n"],
        ["Omits the global feasibility check and returns an index even when total fuel is insufficient.", "Chooses the largest local surplus, which can fail before completing the route."],
        gas_oracle, random_gas,
        ["Total fuel determines whether any complete circuit is possible, but not which station works.",
         "Scan once with a candidate start and its running tank; a negative tank invalidates every start in that attempted segment.",
         "After a failure set start=index+1 and tank=0; keep a separate total balance across all stations. Return -1 if the total is negative.",
         "Zero tank is allowed. A failure occurs only below zero, and the uniqueness guarantee removes any tie rule."],
        "If the tank from a candidate first becomes negative at station i, every later start inside that attempted segment also fails by i: it loses a nonnegative prefix balance. Skip the whole segment and try i+1. Track the global total separately; a negative total makes every circuit impossible. Otherwise the surviving candidate completes the circle. The independent oracle simulates all possible starts and explicitly rejects generated inputs violating the unique-answer guarantee.",
        "O(n)", "O(1)", difficulty=5,
        stress=[([[0] * 99999 + [1], [0] * 99998 + [1, 0]], 99999)]),
    135: entry("minimum_candies", [("ratings", "list[int]")], "int", ["arrays", "greedy"],
        ["1–50000 children; each rating is between 0 and 50000.", "Give every child at least one candy. A child with a strictly higher rating than an immediate neighbor needs strictly more candies than that neighbor.",
         "Equal ratings impose no relative candy requirement. Return the minimum total, not the assignment."],
        [([[1, 0, 2]], "The minimum assignment [2,1,2] satisfies both comparisons and totals 5."),
         ([[1, 2, 2]], "Use [1,2,1], totaling 4. The last two equal ratings need not get equal candies.")],
        [[[0]], [[5]], [[1, 1]], [[1, 2]], [[2, 1]], [[1, 2, 3]], [[3, 2, 1]], [[1, 2, 3, 2, 1]],
         [[1, 3, 4, 5, 2]], [[2, 2, 1]], [[1, 0, 1, 0, 1]], [[0, 50000, 0]]],
        CANDY, [CANDY.replace("range(len(ratings) - 2, -1, -1)", "range(0)"),
                CANDY.replace("ratings[i] > ratings[i - 1]", "ratings[i] >= ratings[i - 1]").replace("ratings[i] > ratings[i + 1]", "ratings[i] >= ratings[i + 1]")],
        ["Enforces only the left-neighbor requirement and misses descending runs.", "Requires extra candies for equal ratings, overestimating the minimum."],
        candy_oracle, random_candy,
        ["Each child's minimum must satisfy independent constraints from its two neighbors.",
         "Use a left-to-right pass for higher-than-left constraints, then a right-to-left pass for higher-than-right constraints.",
         "Begin with one each. Increase on a strict rise; in the reverse pass keep the maximum of the existing count and right_neighbor_count+1.",
         "Do not overwrite a larger left-pass count, and do not treat equal ratings as a strict rise."],
        "The first pass supplies the smallest counts satisfying left-neighbor comparisons. The second supplies right-neighbor lower bounds while preserving any larger first-pass requirement. Each resulting count is necessary for at least one monotone run, so their sum is minimal. Equal ratings break strict runs. The independent oracle repeatedly relaxes all local lower bounds from an all-ones assignment until stable, rather than relying on a two-pass directional invariant.",
        "O(n)", "O(n)", difficulty=8,
        stress=[([list(range(50000))], 1250025000)]),
}

BATCH[71]["statement"] = (
    "Return the lexical canonical form of an absolute Unix-style path. Skip empty and '.' components, "
    "resolve '..' without moving above root, and retain all other names literally. "
    "Use one leading slash and one separator between names; only root '/' ends with a slash. "
    "This is a string-processing exercise and does not inspect the actual filesystem."
)
BATCH[97]["statement"] = (
    "Determine whether s3 can be formed using every character of s1 and s2 exactly once, "
    "preserving the order within each source string. At each step take the next character "
    "from either source; repeated characters may require considering both choices."
)
BATCH[115]["prerequisites"] = ["strings", "dynamic-programming"]
BATCH[123]["prerequisites"] = ["dynamic-programming"]
BATCH[135]["prerequisites"] = ["greedy"]
