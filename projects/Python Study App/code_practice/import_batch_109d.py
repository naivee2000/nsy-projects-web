"""Final reviewed group of workbook batch 109."""

from math import isqrt

from .import_batch_055 import entry


def egg_oracle(arguments):
    floors = arguments[0]
    discriminant_root = isqrt(1 + 8 * floors)
    moves = max(0, (discriminant_root - 1) // 2)
    while moves * (moves + 1) // 2 < floors:
        moves += 1
    return moves


def count_pairs_oracle(arguments):
    first, second = arguments
    return sum(first[left] + first[right] > second[left] + second[right]
               for left in range(len(first)) for right in range(left + 1, len(first)))


def rotation_oracle(arguments):
    matrix, target = arguments
    current = [row[:] for row in matrix]
    for _ in range(4):
        if current == target:
            return True
        current = [list(row) for row in zip(*current[::-1])]
    return False


def reductions_oracle(arguments):
    values = arguments[0][:]
    operations = 0
    while len(set(values)) > 1:
        largest = max(values)
        next_largest = max(value for value in values if value < largest)
        values[values.index(largest)] = next_largest
        operations += 1
    return operations


def flips_oracle(arguments):
    s = arguments[0]
    best = len(s)
    for shift in range(len(s)):
        rotated = s[shift:] + s[:shift]
        for first in "01":
            mismatches = sum(char != (first if index % 2 == 0 else str(1 - int(first)))
                             for index, char in enumerate(rotated))
            best = min(best, mismatches)
    return best


def random_egg(rng):
    return [rng.randint(1, 1000)]


def random_count_pairs(rng):
    length = rng.randint(1, 20)
    return [[rng.randint(1, 30) for _ in range(length)],
            [rng.randint(1, 30) for _ in range(length)]]


def random_rotation(rng):
    size = rng.randint(1, 6)
    matrix = [[rng.randint(0, 1) for _ in range(size)] for _ in range(size)]
    if rng.random() < 0.7:
        target = [row[:] for row in matrix]
        for _ in range(rng.randrange(4)):
            target = [list(row) for row in zip(*target[::-1])]
    else:
        target = [[rng.randint(0, 1) for _ in range(size)] for _ in range(size)]
    return [matrix, target]


def random_reductions(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(1, 20))]]


def random_flips(rng):
    return ["".join(rng.choice("01") for _ in range(rng.randint(1, 30)))]


EGG = '''\
def minimum_two_egg_drop_moves(n):
    moves = 0
    covered = 0
    while covered < n:
        moves += 1
        covered += moves
    return moves
'''

EGG_BINARY = '''\
def minimum_two_egg_drop_moves(n):
    moves = 0
    while (1 << moves) - 1 < n:
        moves += 1
    return moves
'''

COUNT_PAIRS = '''\
def count_dominating_index_pairs(nums1, nums2):
    differences = sorted(first - second for first, second in zip(nums1, nums2))
    answer = 0
    left, right = 0, len(differences) - 1
    while left < right:
        if differences[left] + differences[right] > 0:
            answer += right - left
            right -= 1
        else:
            left += 1
    return answer
'''

COUNT_POSITIVE = '''\
def count_dominating_index_pairs(nums1, nums2):
    return sum(first > second for first, second in zip(nums1, nums2))
'''

ROTATION = '''\
def can_obtain_matrix_by_rotation(mat, target):
    size = len(mat)
    matches_zero = matches_one = matches_two = matches_three = True
    for row in range(size):
        for column in range(size):
            value = target[row][column]
            matches_zero &= mat[row][column] == value
            matches_one &= mat[size - 1 - column][row] == value
            matches_two &= mat[size - 1 - row][size - 1 - column] == value
            matches_three &= mat[column][size - 1 - row] == value
    return matches_zero or matches_one or matches_two or matches_three
'''

ROTATION_HALF = '''\
def can_obtain_matrix_by_rotation(mat, target):
    once = [list(row) for row in zip(*mat[::-1])]
    return mat == target or once == target
'''

ROTATION_TRANSPOSE = '''\
def can_obtain_matrix_by_rotation(mat, target):
    return mat == target or [list(row) for row in zip(*mat)] == target
'''

REDUCTIONS = '''\
def reduction_operations_to_equal(nums):
    ordered = sorted(nums)
    levels_below = 0
    operations = 0
    for index in range(1, len(ordered)):
        if ordered[index] != ordered[index - 1]:
            levels_below += 1
        operations += levels_below
    return operations
'''

REDUCTION_LEVELS = '''\
def reduction_operations_to_equal(nums):
    return len(set(nums)) - 1
'''

FLIPS = '''\
def minimum_flips_after_rotations(s):
    length = len(s)
    doubled = s + s
    mismatch = 0
    answer = length
    for right, char in enumerate(doubled):
        mismatch += char != ("0" if right % 2 == 0 else "1")
        if right >= length:
            left = right - length
            mismatch -= doubled[left] != ("0" if left % 2 == 0 else "1")
        if right >= length - 1:
            answer = min(answer, mismatch, length - mismatch)
    return answer
'''

FLIPS_NO_ROTATION = '''\
def minimum_flips_after_rotations(s):
    mismatch = sum(char != ("0" if index % 2 == 0 else "1") for index, char in enumerate(s))
    return min(mismatch, len(s) - mismatch)
'''

FLIPS_AS_SWAPS = '''\
def minimum_flips_after_rotations(s):
    mismatch = sum(char != ("0" if index % 2 == 0 else "1") for index, char in enumerate(s))
    return min(mismatch, len(s) - mismatch) // 2
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1884: entry(
        "minimum_two_egg_drop_moves", [("n", "int")], "int",
        ["dynamic-programming", "math", "search"],
        ["1 <= n <= 1000.", "There are exactly two identical eggs.",
         "Determine the threshold in the worst case using the fewest drops."],
        [([2], "Dropping from either floor first may require a second drop, so the answer is two."),
         ([100], "Fourteen moves cover only 105 floors cumulatively, while thirteen cover 91; therefore fourteen is minimal.")],
        [[n] for n in [1,2,3,4,5,6,7,10,14,15,16,36,100,1000]],
        EGG,
        [EGG_BINARY, EGG.replace("while covered < n:", "while covered <= n:")],
        ["Uses the exponential coverage available with unlimited eggs instead of two eggs.",
         "Runs one extra move when the triangular coverage equals n exactly."],
        egg_oracle, random_egg,
        lesson("If the first drop is x floors above the last safe floor, a break leaves x-1 floors for the final egg.",
               "Choose successive gaps m, m-1, ..., 1 so both break and survival leave at most one fewer move.",
               "The smallest m whose triangular number m(m+1)/2 reaches n is sufficient.",
               "No m moves can cover more than the same triangular total with two eggs, while the decreasing-gap strategy attains it, proving minimality."),
        "O(sqrt(n))", "O(1)", 5),
    1885: entry(
        "count_dominating_index_pairs", [("nums1", "list[int]"), ("nums2", "list[int]")], "int",
        ["arrays", "sorting", "two-pointers"],
        ["The arrays have equal length from 1 through 100000.", "Values are between 1 and 100000.",
         "Count i < j only when nums1[i]+nums1[j] is strictly greater than nums2[i]+nums2[j]."],
        [([[2,1,2,1],[1,2,1,2]], "Only the two indices with positive difference form a strictly positive pair sum, so the answer is one."),
         ([[1,10,6,2],[1,4,1,5]], "The transformed differences [0,6,5,-3] contain four positive-sum index pairs.")],
        [[first,second] for first,second in [
            ([1],[1]),([2,1,2,1],[1,2,1,2]),([1,10,6,2],[1,4,1,5]),([1,2],[2,1]),
            ([3,3],[1,1]),([1,1],[3,3]),([5,5,5],[5,5,5]),([9,1,8],[2,7,3]),
            ([1,2,3,4],[4,3,2,1]),([10,20,30],[1,25,35]),([2,4,6,8],[1,3,7,9]),
            ([100,1,50,2],[10,20,30,40]),([7,7,1,1],[6,8,0,2]),([5,2,9,1,6],[3,4,2,8,5]),
        ]],
        COUNT_PAIRS,
        [COUNT_PAIRS.replace("> 0", ">= 0"), COUNT_POSITIVE],
        ["Counts equal pair sums even though the comparison must be strict.",
         "Counts individually positive differences instead of pairs whose two differences sum positively."],
        count_pairs_oracle, random_count_pairs,
        lesson("Move all terms to one side: a pair qualifies when two values of nums1[i]-nums2[i] sum above zero.",
               "Sort those differences and inspect the smallest and largest remaining values.",
               "If their sum is positive, the largest pairs with every remaining value; otherwise discard the smallest.",
               "Sorted order makes each bulk count or discard safe, so every qualifying pair is counted exactly once."),
        "O(n*log(n))", "O(n)", 6),
    1886: entry(
        "can_obtain_matrix_by_rotation", [("mat", "list[list[int]]"), ("target", "list[list[int]]")], "bool",
        ["matrices", "arrays", "geometry"],
        ["Both inputs are square matrices of equal size from 1 through 10.", "Cells contain only zero or one.",
         "Allowed transformations are zero, one, two, or three clockwise 90-degree rotations."],
        [([[[0,1],[1,0]],[[1,0],[0,1]]], "One clockwise rotation transforms mat into target."),
         ([[[0,1],[1,1]],[[1,0],[0,1]]], "None of the four orientations matches every target cell.")],
        [[mat,target] for mat,target in [
            ([[0]],[[0]]),([[0]],[[1]]),([[0,1],[1,0]],[[1,0],[0,1]]),([[0,1],[1,1]],[[1,0],[0,1]]),
            ([[1,0],[0,0]],[[0,1],[0,0]]),([[1,0],[0,0]],[[0,0],[0,1]]),
            ([[1,0],[0,0]],[[0,0],[1,0]]),([[1,1],[0,0]],[[0,1],[0,1]]),
            ([[1,1],[0,0]],[[0,0],[1,1]]),([[1,1],[0,0]],[[1,0],[1,0]]),
            ([[1,0,0],[0,1,0],[0,0,1]],[[0,0,1],[0,1,0],[1,0,0]]),
            ([[1,1,0],[0,1,0],[0,0,1]],[[0,0,1],[0,1,1],[1,0,0]]),
            ([[1,0,1],[0,1,0],[1,0,0]],[[1,0,1],[0,1,0],[0,0,1]]),
            ([[0,1,0],[1,0,0],[0,0,1]],[[0,1,0],[0,0,1],[1,0,0]]),
        ]],
        ROTATION,
        [ROTATION_HALF, ROTATION_TRANSPOSE],
        ["Checks only zero and one clockwise rotation, missing valid 180- and 270-degree cases.",
         "Accepts a transpose as though it were always a rotation and misses other valid rotations."],
        rotation_oracle, random_rotation,
        lesson("There are only four distinct orientations of a square under repeated quarter turns.",
               "For each target cell, compare the corresponding source coordinate in all four rotations.",
               "Keep a flag for each orientation and return true if any flag survives every cell.",
               "The coordinate mappings cover exactly 0, 90, 180, and 270 degrees; a surviving flag is therefore necessary and sufficient."),
        "O(n^2)", "O(1)", 3),
    1887: entry(
        "reduction_operations_to_equal", [("nums", "list[int]")], "int",
        ["arrays", "sorting", "counting"],
        ["1 <= len(nums) <= 50000.", "1 <= nums[i] <= 50000.",
         "One operation changes one current maximum element to the next smaller distinct value present."],
        [([[5,1,3]], "Five requires two reductions and three requires one, totaling three operations."),
         ([[1,1,1]], "All values are already equal, so no operation is needed.")],
        [[nums] for nums in [
            [1],[5,1,3],[1,1,1],[1,2],[2,2,1],[5,5,3,1],[1,2,3,4],
            [10,1,10,1],[4,4,4,2,2,1],[9,8,7,6,5],[3,1,3,2,3],
            [100,50,50,1],[2,5,2,5,8,8],[7,3,7,1,3,7],
        ]],
        REDUCTIONS,
        [REDUCTION_LEVELS, REDUCTIONS.replace("operations += levels_below", "operations += 1 if levels_below else 0")],
        ["Counts distinct value levels rather than reducing every occurrence that remains above the minimum.",
         "Adds only one operation per element regardless of how many levels it must cross."],
        reductions_oracle, random_reductions,
        lesson("After sorting, each higher value must cross every distinct lower level.",
               "Scan upward while tracking how many distinct level boundaries have appeared.",
               "Add that boundary count for each element.",
               "Each added unit corresponds to one required reduction of that element across one level, giving a one-to-one count of all operations."),
        "O(n*log(n))", "O(n)", 5),
    1888: entry(
        "minimum_flips_after_rotations", [("s", "str")], "int",
        ["strings", "sliding-windows", "dynamic-programming"],
        ["1 <= len(s) <= 100000 and s is binary.",
         "Moving the first character to the end costs nothing and may be repeated.",
         "A paid operation flips one chosen bit; minimize paid flips needed for an alternating result."],
        [(["111000"], "A free rotation followed by two flips is optimal."),
         (["010"], "The input is already alternating, so zero flips are needed.")],
        [[s] for s in [
            "0","1","01","10","00","11","010","101","111000","01001001101",
            "1110","0001","100","1100","10101","001011","11111","00000",
        ]],
        FLIPS,
        [FLIPS_NO_ROTATION, FLIPS_AS_SWAPS],
        ["Compares only the original orientation and ignores beneficial free rotations.",
         "Divides mismatches as if arbitrary swaps were allowed, but this problem charges individual bit flips."],
        flips_oracle, random_flips,
        lesson("Every rotation is a length-n window in the doubled string s+s.",
               "Track mismatches against the global 0101... pattern while adding the right character and removing the expired left character.",
               "For each full window, its mismatches against 1010... are n minus the tracked count.",
               "The doubled windows enumerate every rotation exactly once, and the two complementary counts cover both alternating targets."),
        "O(n)", "O(n)", 6),
}
