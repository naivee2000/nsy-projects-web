"""Final reviewed group of workbook batch 108."""

from collections import deque

from .import_batch_055 import entry


def rotating_box_oracle(arguments):
    original = arguments[0]
    rows, columns = len(original), len(original[0])
    rotated = [[original[rows - 1 - column][row] for column in range(rows)]
               for row in range(columns)]
    changed = True
    while changed:
        changed = False
        for row in range(len(rotated) - 2, -1, -1):
            for column in range(len(rotated[0])):
                if rotated[row][column] == "#" and rotated[row + 1][column] == ".":
                    rotated[row][column], rotated[row + 1][column] = ".", "#"
                    changed = True
    return rotated


def floored_pairs_oracle(arguments):
    nums = arguments[0]
    return sum(numerator // denominator for numerator in nums for denominator in nums) % 1_000_000_007


def subset_xor_oracle(arguments):
    nums = arguments[0]
    combined = 0
    for value in nums:
        combined |= value
    return combined * (1 << (len(nums) - 1))


def alternating_swaps_oracle(arguments):
    start = arguments[0]
    if all(start[index] != start[index - 1] for index in range(1, len(start))):
        return 0
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        value, distance = queue.popleft()
        for left in range(len(value)):
            for right in range(left + 1, len(value)):
                if value[left] == value[right]:
                    continue
                candidate = list(value)
                candidate[left], candidate[right] = candidate[right], candidate[left]
                candidate = "".join(candidate)
                if candidate in seen:
                    continue
                if all(candidate[index] != candidate[index - 1] for index in range(1, len(candidate))):
                    return distance + 1
                seen.add(candidate)
                queue.append((candidate, distance + 1))
    return -1


def random_box(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 6)
    return [[[rng.choice("##...*") for _ in range(columns)] for _ in range(rows)]]


def random_floored(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 14))]]


def random_subset_xor(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(1, 12))]]


def random_alternating(rng):
    return ["".join(rng.choice("01") for _ in range(rng.randint(1, 8)))]


ROTATING_BOX = '''\
def rotate_box_after_gravity(box_grid):
    rows, columns = len(box_grid), len(box_grid[0])
    settled = [row[:] for row in box_grid]
    for row in range(rows):
        landing = columns - 1
        for column in range(columns - 1, -1, -1):
            if settled[row][column] == "*":
                landing = column - 1
            elif settled[row][column] == "#":
                settled[row][column] = "."
                settled[row][landing] = "#"
                landing -= 1
    return [[settled[rows - 1 - column][row] for column in range(rows)]
            for row in range(columns)]
'''

FLOORED_PAIRS = '''\
def sum_of_floored_pairs(nums):
    modulus = 1_000_000_007
    maximum = max(nums)
    frequency = [0] * (maximum + 1)
    for value in nums:
        frequency[value] += 1
    prefix = frequency[:]
    for value in range(1, maximum + 1):
        prefix[value] += prefix[value - 1]
    answer = 0
    for denominator in range(1, maximum + 1):
        if frequency[denominator] == 0:
            continue
        quotient = 1
        lower = denominator
        while lower <= maximum:
            upper = min(maximum, lower + denominator - 1)
            numerators = prefix[upper] - prefix[lower - 1]
            answer += frequency[denominator] * quotient * numerators
            quotient += 1
            lower += denominator
    return answer % modulus
'''

SUBSET_XOR = '''\
def sum_of_subset_xor_totals(nums):
    def search(index, current):
        if index == len(nums):
            return current
        without_current = search(index + 1, current)
        with_current = search(index + 1, current ^ nums[index])
        return without_current + with_current
    return search(0, 0)
'''

ALTERNATING = '''\
def minimum_swaps_to_alternate(s):
    zeros = s.count("0")
    ones = len(s) - zeros
    if abs(zeros - ones) > 1:
        return -1
    def swaps_when_starting(first):
        mismatches = sum(char != (first if index % 2 == 0 else str(1 - int(first)))
                         for index, char in enumerate(s))
        return mismatches // 2
    if zeros == ones:
        return min(swaps_when_starting("0"), swaps_when_starting("1"))
    return swaps_when_starting("0" if zeros > ones else "1")
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1861: entry(
        "rotate_box_after_gravity", [("box_grid", "list[list[str]]")], "list[list[str]]",
        ["arrays", "matrices", "two-pointers", "simulation"],
        ["1 <= rows, columns <= 500.", "Cells contain '#', '*', or '.'.",
         "Rotate clockwise; then stones fall until blocked by the bottom, a stone, or an obstacle."],
        [
            ([[["#", ".", "#"]]], "After rotation, the upper stone falls onto the lower stone."),
            ([[["#", ".", "*", "."], ["#", "#", "*", "."]]],
             "Each obstacle separates its row into independent gravity segments before rotation."),
        ],
        [[grid] for grid in [
            [["#"]], [["."]], [["*"]], [["#", "."]], [[".", "#"]],
            [["#", "*", "."]], [["#", ".", ".", "#"]],
            [["#", "."], [".", "#"]], [["*", "#"], ["#", "."]],
            [["#", "#", "*", ".", "*", "."], ["#", "#", "#", "*", ".", "."], ["#", "#", "#", ".", "#", "."]],
            [[".", ".", "#"], ["#", "*", "."]], [["#", "*", "#"], [".", ".", "."]],
            [["#", ".", "*", "#", "."]], [[".", "#", "."], ["*", ".", "#"], ["#", ".", "."]],
        ]],
        ROTATING_BOX,
        [ROTATING_BOX.replace("landing = column - 1", "landing = columns - 1"),
         ROTATING_BOX.replace("settled[row][column] = \".\"", "settled[row][column] = \"#\"")],
        ["Lets stones cross obstacles by resetting the landing slot incorrectly.",
         "Copies stones to their landing cells without emptying their previous cells."],
        rotating_box_oracle, random_box,
        lesson("After rotation, downward gravity corresponds to moving stones rightward in each original row.",
               "Scan each row from right to left and keep the next open landing position.",
               "Reset the landing position immediately left of every obstacle, then rotate the settled grid.",
               "Obstacles partition each row; compacting stones within every partition preserves their order and places them as far right as gravity permits."),
        "O(rows*columns)", "O(rows*columns)", 6),
    1862: entry(
        "sum_of_floored_pairs", [("nums", "list[int]")], "int",
        ["arrays", "math", "counting", "prefix-sums"],
        ["1 <= len(nums), nums[i] <= 100000.",
         "Sum floor(nums[i] / nums[j]) over every ordered pair of indices.",
         "Return the result modulo 1,000,000,007."],
        [
            ([[2, 5, 9]], "The nine ordered quotients sum to ten."),
            ([[7, 7, 7, 7, 7, 7, 7]], "Each of 49 ordered pairs contributes one."),
        ],
        [[nums] for nums in [
            [1], [1, 1], [1, 2], [2, 5, 9], [7] * 7, [1, 2, 3, 4], [2, 2, 4],
            [3, 6, 9, 12], [5, 1, 10], [10, 10, 1], [2, 3, 5, 7], [100, 1, 50],
            [4, 8, 15, 16, 23, 42], [1, 3, 3, 9, 27],
        ]],
        FLOORED_PAIRS,
        [FLOORED_PAIRS.replace("frequency[denominator] * quotient", "quotient"),
         FLOORED_PAIRS.replace("lower + denominator - 1", "lower + denominator")],
        ["Counts each distinct denominator only once instead of once per occurrence.",
         "Includes the next quotient bucket's first multiple in the current bucket."],
        floored_pairs_oracle, random_floored,
        lesson("Equal values can be grouped because they contribute identically as denominators.",
               "For denominator d, numerators in [q*d, (q+1)*d-1] contribute quotient q.",
               "Use value frequencies and prefix counts to count each quotient interval quickly.",
               "The quotient intervals partition all positive numerators, and multiplying by the denominator frequency accounts for every ordered index pair exactly once."),
        "O(n + M*log(M))", "O(M)", 8),
    1863: entry(
        "sum_of_subset_xor_totals", [("nums", "list[int]")], "int",
        ["arrays", "bit-manipulation", "recursion", "backtracking"],
        ["1 <= len(nums) <= 12.", "1 <= nums[i] <= 20.",
         "Index-distinct subsets are counted separately even when their values match."],
        [
            ([[1, 3]], "The subset XOR totals are 0, 1, 3, and 2, which sum to six."),
            ([[5, 1, 6]], "The eight subset XOR totals sum to twenty-eight."),
        ],
        [[nums] for nums in [
            [1], [2], [1, 1], [1, 3], [5, 1, 6], [3, 4, 5, 6, 7, 8], [2, 2, 2],
            [1, 2, 4], [7, 8], [20, 1, 20], [3, 3, 5], [6, 10, 12], [1] * 12, [4, 9, 15, 20],
        ]],
        SUBSET_XOR,
        [SUBSET_XOR.replace("return without_current + with_current", "return with_current"),
         SUBSET_XOR.replace("current ^ nums[index]", "current | nums[index]")],
        ["Explores only subsets that include every remaining element.",
         "Uses bitwise OR instead of XOR when adding an element."],
        subset_xor_oracle, random_subset_xor,
        lesson("At each index a subset either excludes or includes that value.",
               "Carry the current XOR down both branches of a recursion tree.",
               "At the base case return the accumulated XOR; add both branch totals while unwinding.",
               "Every subset corresponds to exactly one sequence of include/exclude choices, so the leaves enumerate all index-distinct subsets once."),
        "O(2^n)", "O(n)", 3),
    1864: entry(
        "minimum_swaps_to_alternate", [("s", "str")], "int",
        ["strings", "greedy", "counting"],
        ["1 <= len(s) <= 1000.", "s contains only '0' and '1'.",
         "One swap may exchange any two positions, not only adjacent positions."],
        [
            (["111000"], "Swapping one misplaced one with one misplaced zero produces an alternating string."),
            (["1110"], "The counts differ by more than one, so alternation is impossible."),
        ],
        [[value] for value in [
            "0", "1", "01", "10", "00", "11", "010", "101", "111000", "1110",
            "100", "1100", "1001", "101010", "0101010", "001011",
        ]],
        ALTERNATING,
        [ALTERNATING.replace("return mismatches // 2", "return mismatches"),
         ALTERNATING.replace("return swaps_when_starting(\"0\" if zeros > ones else \"1\")", "return swaps_when_starting(\"0\")")],
        ["Counts each misplaced position as a swap instead of pairing two mismatches per swap.",
         "Always starts with zero when counts force which character must appear first."],
        alternating_swaps_oracle, random_alternating,
        lesson("An alternating string can have character counts differing by at most one.",
               "Compare the input with each count-compatible pattern: 0101... or 1010....",
               "Count mismatched positions and divide by two because every swap fixes one zero and one one.",
               "When counts differ, only one pattern is possible; when equal, choosing the smaller mismatch count gives the minimum number of arbitrary swaps."),
        "O(n)", "O(1)", 5),
}
