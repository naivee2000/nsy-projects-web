"""Second reviewed group of workbook batch 109."""

from functools import lru_cache
from itertools import permutations

from .import_batch_055 import entry


def stone_game_oracle(arguments):
    start = tuple(arguments[0])

    @lru_cache(maxsize=None)
    def play(stones, alice_turn):
        if len(stones) == 1:
            return 0
        outcomes = []
        prefix = 0
        for taken in range(1, len(stones)):
            prefix += stones[taken - 1]
            merged = prefix + stones[taken]
            next_stones = (merged,) + stones[taken + 1:]
            continuation = play(next_stones, not alice_turn)
            outcomes.append((merged if alice_turn else -merged) + continuation)
        return (max if alice_turn else min)(outcomes)

    return play(start, True)


def product_sum_oracle(arguments):
    first, second = arguments
    return min(sum(left * right for left, right in zip(order, second))
               for order in permutations(first))


def distinct_three_oracle(arguments):
    s = arguments[0]
    return sum(s[left] != s[left + 1] and s[left] != s[left + 2]
               and s[left + 1] != s[left + 2] for left in range(len(s) - 2))


def pair_sum_oracle(arguments):
    start = tuple(sorted(arguments[0]))

    @lru_cache(maxsize=None)
    def arrange(values):
        if not values:
            return 0
        best = float("inf")
        for partner in range(1, len(values)):
            remaining = values[1:partner] + values[partner + 1:]
            best = min(best, max(values[0] + values[partner], arrange(remaining)))
        return best

    return arrange(start)


def rhombus_oracle(arguments):
    grid = arguments[0]
    rows, columns = len(grid), len(grid[0])
    values = {value for row in grid for value in row}
    for top in range(rows):
        for column in range(columns):
            radius = 1
            while top + 2 * radius < rows and column - radius >= 0 and column + radius < columns:
                center_row = top + radius
                border = 0
                for row in range(top, top + 2 * radius + 1):
                    for candidate_column in range(column - radius, column + radius + 1):
                        if abs(row - center_row) + abs(candidate_column - column) == radius:
                            border += grid[row][candidate_column]
                values.add(border)
                radius += 1
    return sorted(values, reverse=True)[:3]


def random_stones(rng):
    return [[rng.randint(-10, 10) for _ in range(rng.randint(2, 8))]]


def random_product_sum(rng):
    length = rng.randint(1, 6)
    return [[rng.randint(1, 10) for _ in range(length)],
            [rng.randint(1, 10) for _ in range(length)]]


def random_distinct_three(rng):
    return ["".join(rng.choice("abcde") for _ in range(rng.randint(1, 100)))]


def random_pair_sum(rng):
    return [[rng.randint(1, 30) for _ in range(2 * rng.randint(1, 4))]]


def random_rhombus(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    return [[[rng.randint(1, 30) for _ in range(columns)] for _ in range(rows)]]


STONE_GAME = '''\
def optimal_stone_game_difference(stones):
    prefix = []
    running = 0
    for value in stones:
        running += value
        prefix.append(running)
    best = prefix[-1]
    for index in range(len(stones) - 2, 0, -1):
        best = max(best, prefix[index] - best)
    return best
'''

PRODUCT_SUM = '''\
def minimum_product_sum(nums1, nums2):
    ascending = sorted(nums1)
    descending = sorted(nums2, reverse=True)
    return sum(first * second for first, second in zip(ascending, descending))
'''

DISTINCT_THREE = '''\
def count_distinct_length_three_substrings(s):
    counts = {}
    answer = 0
    for index, char in enumerate(s):
        counts[char] = counts.get(char, 0) + 1
        if index >= 3:
            leaving = s[index - 3]
            counts[leaving] -= 1
            if counts[leaving] == 0:
                del counts[leaving]
        if index >= 2 and len(counts) == 3:
            answer += 1
    return answer
'''

PAIR_SUM = '''\
def minimize_maximum_pair_sum(nums):
    ordered = sorted(nums)
    answer = 0
    left, right = 0, len(ordered) - 1
    while left < right:
        answer = max(answer, ordered[left] + ordered[right])
        left += 1
        right -= 1
    return answer
'''

RHOMBUS = '''\
def three_largest_rhombus_border_sums(grid):
    rows, columns = len(grid), len(grid[0])
    down_right = [[0] * (columns + 1) for _ in range(rows + 1)]
    down_left = [[0] * (columns + 1) for _ in range(rows + 1)]
    for row in range(rows):
        for column in range(columns):
            down_right[row + 1][column + 1] = grid[row][column] + down_right[row][column]
        for column in range(columns - 1, -1, -1):
            down_left[row + 1][column] = grid[row][column] + down_left[row][column + 1]
    values = set()
    for top in range(rows):
        for column in range(columns):
            values.add(grid[top][column])
            radius = 1
            while top + 2 * radius < rows and column - radius >= 0 and column + radius < columns:
                right_row, bottom_row = top + radius, top + 2 * radius
                first = down_right[right_row + 1][column + radius + 1] - down_right[top][column]
                second = down_left[bottom_row + 1][column] - down_left[right_row][column + radius + 1]
                third = down_right[bottom_row + 1][column + 1] - down_right[right_row][column - radius]
                fourth = down_left[right_row + 1][column - radius] - down_left[top][column + 1]
                border = first + second + third + fourth
                border -= (grid[top][column] + grid[right_row][column + radius] +
                           grid[bottom_row][column] + grid[right_row][column - radius])
                values.add(border)
                radius += 1
    return sorted(values, reverse=True)[:3]
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1872: entry(
        "optimal_stone_game_difference", [("stones", "list[int]")], "int",
        ["arrays", "dynamic-programming", "game-theory", "prefix-sums"],
        ["2 <= len(stones) <= 100000.", "-10000 <= stones[i] <= 10000.",
         "A move replaces at least the first two stones by their sum and awards that sum to the current player."],
        [([[-1,2,-3,4,-5]], "Optimal play gives Alice a final score advantage of five."),
         ([[7,-6,5,10,5,-2,-6]], "Considering every legal prefix through the suffix recurrence gives thirteen.")],
        [[stones] for stones in [
            [1,2],[-1,2],[1,2,3],[-1,2,-3,4,-5],[7,-6,5,10,5,-2,-6],
            [-10,-5,-2],[5,-1,2,-3],[0,0],[10,-10,10],[-3,8,-2,4],
            [1,-2,3,-4,5],[-5,9,1,-7,3,2],[4,4,4,4],[-8,2,6,-1,7],
        ]],
        STONE_GAME,
        [STONE_GAME.replace("best = prefix[-1]", "best = 0"),
         STONE_GAME.replace("best = max(best, prefix[index] - best)", "best = min(best, prefix[index] - best)")],
        ["Assumes the player may stop with zero advantage even though play must continue until one stone remains.",
         "Minimizes the current player's best advantage instead of maximizing it."],
        stone_game_oracle, random_stones,
        lesson("Every merged leading stone equals a prefix sum of the original array.",
               "Let best represent the optimal advantage after the game has reached a given prefix.",
               "Scan prefix endpoints backward using best = max(best, prefix[i] - best).",
               "At each state the player either preserves the later optimal choice or takes prefix i and leaves the opponent the stored advantage; backward induction proves the recurrence."),
        "O(n)", "O(n)", 8),
    1874: entry(
        "minimum_product_sum", [("nums1", "list[int]"), ("nums2", "list[int]")], "int",
        ["arrays", "sorting", "greedy"],
        ["The arrays have equal length from 1 through 100000.", "Every value is between 1 and 100.",
         "Rearrange either array to minimize the sum of corresponding products."],
        [([[5,3,4,2],[4,2,2,5]], "Pairing [2,3,4,5] with [5,4,2,2] gives the minimum sum forty."),
         ([[2,1,4,5,7],[3,2,4,8,6]], "Pairing opposite sorted orders yields sixty-five.")],
        [[left,right] for left,right in [
            ([1],[1]),([1,2],[3,4]),([5,3,4,2],[4,2,2,5]),([2,1,4,5,7],[3,2,4,8,6]),
            ([1,1,1],[9,2,5]),([10,1,5],[3,3,3]),([1,2,3],[1,2,3]),([5,5],[5,5]),
            ([9,8,7,6],[1,2,3,4]),([2,9,1,8,3,7],[6,1,5,2,4,3]),
            ([100,1],[100,1]),([4,2,4,2],[3,9,1,7]),([6,5,4],[9,1,2]),([3,1,2,3],[4,4,1,2]),
        ]],
        PRODUCT_SUM,
        [PRODUCT_SUM.replace("sorted(nums2, reverse=True)", "sorted(nums2)"),
         PRODUCT_SUM.replace("descending = sorted(nums2, reverse=True)", "descending = nums2")],
        ["Sorts both arrays in the same direction, maximizing rather than minimizing aligned products.",
         "Leaves the second array in its original order instead of choosing the optimal rearrangement."],
        product_sum_oracle, random_product_sum,
        lesson("A large value should be paired with a small value to avoid a large product.",
               "Sort one array ascending and the other descending, then multiply aligned values.",
               "Sum all opposite-order products.",
               "If two pairs are similarly ordered, swapping their partners never increases the sum; repeatedly removing inversions yields the opposite-order optimum."),
        "O(n*log(n))", "O(n)", 6),
    1876: entry(
        "count_distinct_length_three_substrings", [("s", "str")], "int",
        ["strings", "sliding-windows", "hash-maps"],
        ["1 <= len(s) <= 100.", "s contains lowercase English letters.",
         "Count occurrences separately, even when two valid substrings have the same text."],
        [(["xyzzaz"], "Only the first window, xyz, contains three distinct characters."),
         (["aababcabc"], "The valid windows are abc, bca, cab, and the later abc, for four occurrences." )],
        [[s] for s in ["a","ab","abc","aaa","aab","xyzzaz","aababcabc","abcdef","abac","abbc","zzzaaa","ababab","pwwkew","abcabc","abcded"]],
        DISTINCT_THREE,
        [DISTINCT_THREE.replace("len(counts) == 3", "len(counts) >= 2"),
         DISTINCT_THREE.replace("index >= 2 and", "index > 2 and")],
        ["Accepts windows containing only two distinct characters.",
         "Skips the first length-three window."],
        distinct_three_oracle, random_distinct_three,
        lesson("Only a window of exactly three characters matters.",
               "Maintain character counts while adding the new character and removing the character three positions back.",
               "Once the window has length three, count it exactly when the map has three keys.",
               "The map represents precisely the current length-three window, so three keys is equivalent to all three characters being distinct."),
        "O(n)", "O(1)", 3),
    1877: entry(
        "minimize_maximum_pair_sum", [("nums", "list[int]")], "int",
        ["arrays", "sorting", "two-pointers", "greedy"],
        ["len(nums) is even and between 2 and 100000.", "1 <= nums[i] <= 100000.",
         "Use every element exactly once and minimize the largest resulting pair sum."],
        [([[3,5,2,3]], "Sorted extremes form sums seven and six, so the minimized maximum is seven."),
         ([[3,5,4,2,4,6]], "Pairing extremes produces sums eight, nine, and eight; no arrangement has maximum below nine.")],
        [[nums] for nums in [
            [1,1],[1,2],[3,5,2,3],[3,5,4,2,4,6],[1,2,3,4],[1,1,9,9],
            [5,5,5,5],[1,2,2,100],[8,1,7,2,6,3],[10,20,30,40,50,60],
            [4,9,1,7,3,8,2,6],[100,1],[2,3,3,4,8,9],[6,2,5,1,9,4],
        ]],
        PAIR_SUM,
        [PAIR_SUM.replace("ordered[left] + ordered[right]", "ordered[left] + ordered[left + 1]"),
         PAIR_SUM.replace("ordered[left] + ordered[right]", "ordered[left] + ordered[len(ordered)//2 + left]")],
        ["Pairs adjacent small elements while leaving the largest values paired together.",
         "Pairs the lower and upper halves in the same order instead of opposite order."],
        pair_sum_oracle, random_pair_sum,
        lesson("The smallest remaining value should absorb the largest remaining value.",
               "Sort the array and pair the two extremes while moving inward.",
               "Track the maximum sum among those pairs.",
               "Any pairing of the largest element uses some partner at least as large as the smallest; exchanging crossed partners cannot reduce the optimum below the extreme pairing."),
        "O(n*log(n))", "O(n)", 6),
    1878: entry(
        "three_largest_rhombus_border_sums", [("grid", "list[list[int]]")], "list[int]",
        ["matrices", "prefix-sums", "geometry", "sorting"],
        ["1 <= rows, columns <= 50.", "1 <= grid[row][column] <= 100000.",
         "A one-cell rhombus is valid; return at most three distinct border sums in descending order."],
        [([[[3,4,5,1,3],[3,3,4,2,3],[20,30,200,40,10],[1,5,5,4,1],[4,3,2,2,5]]],
          "Enumerating all centers and radii gives the three largest distinct borders 228, 216, and 211."),
         ([[[1,2,3],[4,5,6],[7,8,9]]], "The radius-one border sums to twenty, followed by singleton values nine and eight.")],
        [[grid] for grid in [
            [[1]],[[1,2]],[[1],[2]],[[1,2],[3,4]],[[1,2,3],[4,5,6],[7,8,9]],
            [[5,5,5],[5,5,5],[5,5,5]],[[1,2,1],[2,9,2],[1,2,1]],
            [[3,4,5,1,3],[3,3,4,2,3],[20,30,200,40,10],[1,5,5,4,1],[4,3,2,2,5]],
            [[7,1,4,2],[3,9,5,8],[6,2,1,3],[4,8,7,5]],
            [[1,2,3,4,5],[6,7,8,9,10],[11,12,13,14,15]],
            [[9,1,9],[1,9,1],[9,1,9],[1,9,1],[9,1,9]],
            [[2,8,3,7],[6,1,5,4],[9,2,8,3]],
            [[10,20,30],[40,50,60],[70,80,90],[15,25,35]],
            [[4,3,2,1],[5,6,7,8],[9,1,2,3],[4,5,6,7],[8,9,1,2]],
        ]],
        RHOMBUS,
        [RHOMBUS.replace("grid[bottom_row][column] + grid[right_row][column - radius]", "grid[right_row][column - radius]"),
         RHOMBUS.replace("            values.add(grid[top][column])", "            pass")],
        ["Double-counts the bottom vertex of every nontrivial rhombus.",
         "Omits all valid one-cell rhombi."],
        rhombus_oracle, random_rhombus,
        lesson("Rhombus borders follow the two diagonal directions of the grid.",
               "Build a prefix table for each diagonal direction so every edge sum is available in constant time.",
               "Enumerate each top vertex and fitting radius, add four edge sums, then subtract the four duplicated corners.",
               "Every valid rhombus has one unique top vertex and radius; diagonal prefixes produce its exact border, and a set enforces distinct output values."),
        "O(rows*columns*min(rows,columns))", "O(rows*columns)", 7),
}
