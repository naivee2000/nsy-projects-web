"""First reviewed group of workbook batch 109."""

from fractions import Fraction
from functools import lru_cache
from itertools import permutations
from math import ceil

from .import_batch_055 import entry


@lru_cache(maxsize=None)
def _sticks_bruteforce(n, k):
    total = 0
    for order in permutations(range(1, n + 1)):
        tallest = visible = 0
        for stick in order:
            if stick > tallest:
                tallest, visible = stick, visible + 1
        total += visible == k
    return total % 1_000_000_007


def sticks_oracle(arguments):
    return _sticks_bruteforce(*arguments)


def encode(values):
    result = []
    for value in values:
        if result and result[-1][0] == value:
            result[-1][1] += 1
        else:
            result.append([value, 1])
    return result


def rle_product_oracle(arguments):
    left = [value for value, count in arguments[0] for _ in range(count)]
    right = [value for value, count in arguments[1] for _ in range(count)]
    return encode([first * second for first, second in zip(left, right)])


def longer_ones_oracle(arguments):
    s = arguments[0]
    longest = {"0": 0, "1": 0}
    start = 0
    while start < len(s):
        end = start + 1
        while end < len(s) and s[end] == s[start]:
            end += 1
        longest[s[start]] = max(longest[s[start]], end - start)
        start = end
    return longest["1"] > longest["0"]


def speed_oracle(arguments):
    distances, hour = arguments
    limit = Fraction(str(hour))
    if limit <= len(distances) - 1:
        return -1
    for speed in range(1, 10_000_001):
        elapsed = sum(ceil(Fraction(distance, speed)) for distance in distances[:-1])
        elapsed += Fraction(distances[-1], speed)
        if elapsed <= limit:
            return speed
    return -1


def jump_oracle(arguments):
    s, minimum, maximum = arguments
    reachable = {0}
    frontier = [0]
    while frontier:
        index = frontier.pop(0)
        for destination in range(index + minimum, min(len(s), index + maximum + 1)):
            if s[destination] == "0" and destination not in reachable:
                reachable.add(destination)
                frontier.append(destination)
    return len(s) - 1 in reachable


def random_sticks(rng):
    n = rng.randint(1, 7)
    return [n, rng.randint(1, n)]


def random_rle(rng):
    length = rng.randint(1, 18)
    return [encode([rng.randint(1, 6) for _ in range(length)]),
            encode([rng.randint(1, 6) for _ in range(length)])]


def random_longer_ones(rng):
    return ["".join(rng.choice("01") for _ in range(rng.randint(1, 100)))]


def random_speed(rng):
    distances = [rng.randint(1, 20) for _ in range(rng.randint(1, 6))]
    minimum_whole = max(0, len(distances) - 1)
    hour = minimum_whole + rng.randint(1, 80) / 4
    return [distances, hour]


def random_jump(rng):
    length = rng.randint(2, 20)
    s = "0" + "".join(rng.choice("0011") for _ in range(length - 1))
    minimum = rng.randint(1, length - 1)
    return [s, minimum, rng.randint(minimum, length - 1)]


STICKS = '''\
def count_visible_stick_arrangements(n, k):
    modulus = 1_000_000_007
    previous = [0] * (k + 1)
    previous[0] = 1
    for sticks in range(1, n + 1):
        current = [0] * (k + 1)
        for visible in range(1, min(sticks, k) + 1):
            current[visible] = (previous[visible - 1] +
                                previous[visible] * (sticks - 1)) % modulus
        previous = current
    return previous[k]
'''

RLE_PRODUCT = '''\
def multiply_run_length_arrays(encoded1, encoded2):
    answer = []
    left = right = 0
    left_remaining = encoded1[0][1]
    right_remaining = encoded2[0][1]
    while left < len(encoded1) and right < len(encoded2):
        used = min(left_remaining, right_remaining)
        product = encoded1[left][0] * encoded2[right][0]
        if answer and answer[-1][0] == product:
            answer[-1][1] += used
        else:
            answer.append([product, used])
        left_remaining -= used
        right_remaining -= used
        if left_remaining == 0:
            left += 1
            if left < len(encoded1):
                left_remaining = encoded1[left][1]
        if right_remaining == 0:
            right += 1
            if right < len(encoded2):
                right_remaining = encoded2[right][1]
    return answer
'''

LONGER_ONES = '''\
def ones_run_is_strictly_longer(s):
    longest_zero = longest_one = 0
    current_zero = current_one = 0
    for char in s:
        if char == "1":
            current_one += 1
            current_zero = 0
            longest_one = max(longest_one, current_one)
        else:
            current_zero += 1
            current_one = 0
            longest_zero = max(longest_zero, current_zero)
    return longest_one > longest_zero
'''

LONGER_TOTALS = '''\
def ones_run_is_strictly_longer(s):
    return s.count("1") > s.count("0")
'''

SPEED = '''\
def minimum_train_speed(dist, hour):
    hour_hundredths = round(hour * 100)
    def arrives(speed):
        waiting_hours = sum((distance + speed - 1) // speed for distance in dist[:-1])
        remaining_hundredths = hour_hundredths - 100 * waiting_hours
        return remaining_hundredths > 0 and remaining_hundredths * speed >= 100 * dist[-1]
    left, right = 1, 10_000_000
    while left < right:
        middle = (left + right) // 2
        if arrives(middle):
            right = middle
        else:
            left = middle + 1
    return left if arrives(left) else -1
'''

JUMP = '''\
def can_reach_binary_string_end(s, min_jump, max_jump):
    reachable = [False] * len(s)
    reachable[0] = True
    window = 0
    for index in range(1, len(s)):
        entering = index - min_jump
        if entering >= 0:
            window += reachable[entering]
        leaving = index - max_jump - 1
        if leaving >= 0:
            window -= reachable[leaving]
        reachable[index] = s[index] == "0" and window > 0
    return reachable[-1]
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1866: entry(
        "count_visible_stick_arrangements", [("n", "int"), ("k", "int")], "int",
        ["dynamic-programming", "combinatorics", "math"],
        ["1 <= k <= n <= 1000.", "Stick lengths are the distinct integers from 1 through n.",
         "A stick is visible from the left only if every earlier stick is shorter."],
        [([3, 2], "The orders [1,3,2], [2,3,1], and [2,1,3] each expose exactly two sticks."),
         ([5, 5], "All five sticks are visible only in strictly increasing order, so there is one arrangement.")],
        [[*case] for case in [(1,1),(2,1),(2,2),(3,1),(3,2),(3,3),(4,2),(4,3),(5,1),(5,2),(5,4),(6,3),(7,2),(7,7)]],
        STICKS,
        [STICKS.replace("previous[visible] * (sticks - 1)", "previous[visible]"),
         STICKS.replace("(sticks - 1)", "sticks")],
        ["Forgets the multiple insertion positions that hide the newly added shortest stick.",
         "Counts one extra insertion position when the new stick is not visible."],
        sticks_oracle, random_sticks,
        lesson("Build arrangements by inserting the shortest new stick into a smaller arrangement.",
               "Putting it first adds one visible stick; any of the other i-1 positions leaves visibility unchanged.",
               "Use dp[i][j] = dp[i-1][j-1] + (i-1)*dp[i-1][j], retaining only the previous row.",
               "The two insertion cases are disjoint and cover every permutation exactly once, which proves the recurrence."),
        "O(n*k)", "O(k)", 8),
    1868: entry(
        "multiply_run_length_arrays", [("encoded1", "list[list[int]]"), ("encoded2", "list[list[int]]")],
        "list[list[int]]", ["arrays", "two-pointers", "run-length-encoding"],
        ["Each [value, frequency] pair has positive integers.", "Each encoding has at most 100000 runs.",
         "The two expanded arrays have equal length; return the shortest valid encoding of their products."],
        [([[[1,3],[2,3]], [[6,3],[3,3]]], "Both product regions equal six, so they merge into the single run [6,6]."),
         ([[[1,3],[2,1],[3,2]], [[2,3],[3,3]]], "Aligned run boundaries produce product runs [2,3], [6,1], and [9,2].")],
        [[left,right] for left,right in [
            ([[1,1]],[[2,1]]), ([[1,3]],[[4,3]]), ([[1,3],[2,3]],[[6,3],[3,3]]),
            ([[1,2],[2,2]],[[3,1],[4,3]]), ([[2,1],[1,4]],[[3,3],[6,2]]),
            ([[5,2],[2,1]],[[1,1],[5,2]]), ([[2,4]],[[3,1],[4,1],[5,2]]),
            ([[1,1],[2,1],[1,1]],[[2,1],[1,1],[2,1]]),
            ([[4,5],[1,2]],[[2,3],[8,4]]), ([[3,2],[6,3]],[[2,4],[1,1]]),
            ([[7,1],[1,5]],[[1,3],[7,3]]), ([[2,2],[4,2]],[[6,3],[3,1]]),
            ([[9,6]],[[1,2],[2,2],[3,2]]), ([[1,2],[3,3],[2,1]],[[6,1],[2,5]]),
        ]],
        RLE_PRODUCT,
        [RLE_PRODUCT.replace("if answer and answer[-1][0] == product:", "if False:"),
         '''def multiply_run_length_arrays(encoded1, encoded2):
 left=[v for v,c in encoded1 for _ in range(c)];right=[v for v,c in encoded2 for _ in range(c)]
 return [[a*b,1] for a,b in zip(left,right)]
'''],
        ["Never merges adjacent runs that produce the same product.",
         "Expands correctly but returns one run per element instead of the minimum-length encoding."],
        rle_product_oracle, random_rle,
        lesson("Only the current run from each encoding can affect the next product segment.",
               "Consume the smaller remaining frequency, advancing whichever run is exhausted.",
               "Append a new product run unless its value equals the previous product, in which case merge frequencies.",
               "Each step consumes a nonempty aligned interval; these intervals partition both arrays and adjacent equal products are merged immediately."),
        "O(runs1+runs2)", "O(output runs)", 6),
    1869: entry(
        "ones_run_is_strictly_longer", [("s", "str")], "bool", ["strings", "counting"],
        ["1 <= len(s) <= 100.", "s contains only '0' and '1'.",
         "Compare the longest contiguous runs; the run of ones must be strictly longer."],
        [(["1101"], "The longest one-run has length two while the longest zero-run has length one."),
         (["111000"], "Both longest runs have length three, so the strict comparison is false.")],
        [[s] for s in ["0","1","01","10","00","11","1101","111000","110100010","0001111","1010101","001100","111011","0001000"]],
        LONGER_ONES,
        [LONGER_ONES.replace("longest_one > longest_zero", "longest_one >= longest_zero"), LONGER_TOTALS],
        ["Treats equal-length longest runs as a success despite the strict requirement.",
         "Compares total character counts instead of contiguous run lengths."],
        longer_ones_oracle, random_longer_ones,
        lesson("Track current and maximum run lengths separately for zero and one.",
               "Extend the matching run and reset the other run at every character.",
               "After the scan, compare the two maximums with a strict greater-than test.",
               "Every maximal run ends either at a different character or at the string boundary, and its length is recorded before comparison."),
        "O(n)", "O(1)", 3),
    1870: entry(
        "minimum_train_speed", [("dist", "list[int]"), ("hour", "float")], "int",
        ["arrays", "binary-search", "math"],
        ["1 <= len(dist) <= 100000 and 1 <= dist[i] <= 100000.", "hour has at most two decimal places.",
         "All non-final train times round up to the next integer hour; return -1 if speed 10000000 is insufficient."],
        [([[1,3,2], 6.0], "At speed one the trips take 1, 3, and 2 hours, meeting the six-hour limit."),
         ([[1,3,2], 2.7], "Speed three gives waits of 1 and 1 hours plus 2/3 hour, so it is minimal.")],
        [[dist,hour] for dist,hour in [
            ([1],1.0),([2],1.0),([1,3,2],6.0),([1,3,2],2.7),([1,3,2],1.9),
            ([5,3,4],4.0),([5,3,4],3.0),([10,10],2.0),([10,10],1.5),
            ([100,1],2.0),([1,100],1.01),([3,3,3],3.0),([3,3,3],2.5),([7,2,9,4],6.25),
        ]],
        SPEED,
        [SPEED.replace("(distance + speed - 1) // speed", "distance // speed"),
         SPEED.replace("dist[:-1]", "dist")],
        ["Rounds intermediate train times down instead of waiting for the next integer departure.",
         "Rounds the final train up and then also charges its fractional travel time."],
        speed_oracle, random_speed,
        lesson("Feasibility is monotonic: any speed above a feasible speed is also feasible.",
               "Round every non-final trip upward, but keep the final trip fractional.",
               "Binary-search speeds 1 through 10000000 using hundredths to avoid boundary rounding errors.",
               "The predicate exactly models departure waits, and binary search returns the first feasible integer in a monotonic range."),
        "O(n*log(10000000))", "O(1)", 6),
    1871: entry(
        "can_reach_binary_string_end", [("s", "str"), ("min_jump", "int"), ("max_jump", "int")], "bool",
        ["strings", "dynamic-programming", "sliding-windows"],
        ["2 <= len(s) <= 100000 and s[0] == '0'.", "1 <= min_jump <= max_jump < len(s).",
         "A destination is usable only when its character is '0'."],
        [(["011010",2,3], "Reach indices 0, 3, and 5 using jumps of three and two."),
         (["01101110",2,3], "Every route becomes blocked before the final position." )],
        [[s,a,b] for s,a,b in [
            ("00",1,1),("01",1,1),("011010",2,3),("01101110",2,3),("0000",1,1),
            ("0000",2,3),("0100",1,2),("0101",1,2),("001000",2,3),("0100010",2,4),
            ("0001000",2,3),("0111110",2,5),("00101",1,3),("0100001",2,3),
        ]],
        JUMP,
        [JUMP.replace("if leaving >= 0:\n            window -= reachable[leaving]", "if False:\n            window -= reachable[leaving]"),
         JUMP.replace("window > 0", "window >= 0")],
        ["Never removes old reachable indices after they leave the permitted jump window.",
         "Marks zero cells reachable even when the jump window contains no reachable origin."],
        jump_oracle, random_jump,
        lesson("For index i, only reachable indices in [i-max_jump, i-min_jump] can lead to it.",
               "Maintain the number of reachable indices in that interval as a sliding window.",
               "Add the new left candidate, remove the expired candidate, and mark i only when it is zero and the count is positive.",
               "The maintained count exactly represents all valid predecessors, so induction over indices proves every reachability value."),
        "O(n)", "O(n)", 6),
}
