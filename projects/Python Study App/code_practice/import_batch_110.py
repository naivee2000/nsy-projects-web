"""First reviewed group of workbook batch 110."""

from bisect import bisect_right

from .import_batch_055 import entry


def packaging_oracle(arguments):
    packages, suppliers = arguments
    candidates = []
    for boxes in suppliers:
        if any(not any(box >= package for box in boxes) for package in packages):
            continue
        candidates.append(sum(min(box for box in boxes if box >= package) - package
                              for package in packages))
    return -1 if not candidates else min(candidates) % 1_000_000_007


def ribbon_oracle(arguments):
    ribbons, required = arguments
    return max((length for length in range(1, max(ribbons) + 1)
                if sum(ribbon // length for ribbon in ribbons) >= required), default=0)


def coverage_oracle(arguments):
    ranges, left, right = arguments
    return all(any(start <= value <= end for start, end in ranges)
               for value in range(left, right + 1))


def chalk_oracle(arguments):
    chalk, k = arguments
    remainder = k % sum(chalk)
    used = 0
    for index, amount in enumerate(chalk):
        used += amount
        if used > remainder:
            return index


def magic_oracle(arguments):
    grid = arguments[0]
    rows, columns = len(grid), len(grid[0])
    for size in range(min(rows, columns), 0, -1):
        for top in range(rows - size + 1):
            for left in range(columns - size + 1):
                row_sums = [sum(grid[row][left:left + size]) for row in range(top, top + size)]
                column_sums = [sum(grid[row][column] for row in range(top, top + size))
                               for column in range(left, left + size)]
                diagonal_one = sum(grid[top + offset][left + offset] for offset in range(size))
                diagonal_two = sum(grid[top + offset][left + size - 1 - offset] for offset in range(size))
                if len(set(row_sums + column_sums + [diagonal_one, diagonal_two])) == 1:
                    return size
    return 1


def random_packaging(rng):
    packages = [rng.randint(1, 25) for _ in range(rng.randint(1, 8))]
    suppliers = []
    for _ in range(rng.randint(1, 6)):
        suppliers.append(rng.sample(range(1, 31), rng.randint(1, 8)))
    return [packages, suppliers]


def random_ribbon(rng):
    return [[rng.randint(1, 40) for _ in range(rng.randint(1, 12))], rng.randint(1, 80)]


def random_coverage(rng):
    ranges = []
    for _ in range(rng.randint(1, 10)):
        start = rng.randint(1, 50)
        ranges.append([start, rng.randint(start, 50)])
    left = rng.randint(1, 50)
    return [ranges, left, rng.randint(left, 50)]


def random_chalk(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 15))], rng.randint(1, 2000)]


def random_magic(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    return [[[rng.randint(1, 12) for _ in range(columns)] for _ in range(rows)]]


PACKAGING = '''\
def minimum_packaging_waste(packages, boxes):
    from bisect import bisect_right
    ordered_packages = sorted(packages)
    package_prefix = [0]
    for package in ordered_packages:
        package_prefix.append(package_prefix[-1] + package)
    best = None
    for supplier in boxes:
        ordered_boxes = sorted(supplier)
        if ordered_boxes[-1] < ordered_packages[-1]:
            continue
        assigned = 0
        waste = 0
        for box in ordered_boxes:
            end = bisect_right(ordered_packages, box, lo=assigned)
            waste += (end - assigned) * box - (package_prefix[end] - package_prefix[assigned])
            assigned = end
            if assigned == len(ordered_packages):
                break
        best = waste if best is None else min(best, waste)
    return -1 if best is None else best % 1_000_000_007
'''

PACKAGING_FIRST = '''\
def minimum_packaging_waste(packages, boxes):
    for supplier in boxes:
        if max(supplier) >= max(packages):
            return sum(min(box for box in supplier if box >= package) - package for package in packages) % 1_000_000_007
    return -1
'''

RIBBON = '''\
def maximum_ribbon_piece_length(ribbons, k):
    left, right = 0, max(ribbons)
    while left < right:
        middle = (left + right + 1) // 2
        pieces = sum(ribbon // middle for ribbon in ribbons)
        if pieces >= k:
            left = middle
        else:
            right = middle - 1
    return left
'''

COVERAGE = '''\
def every_integer_is_covered(ranges, left, right):
    difference = [0] * 52
    for start, end in ranges:
        difference[start] += 1
        difference[end + 1] -= 1
    active = 0
    for value in range(1, 51):
        active += difference[value]
        if left <= value <= right and active == 0:
            return False
    return True
'''

COVERAGE_ENDPOINTS = '''\
def every_integer_is_covered(ranges, left, right):
    return any(a <= left <= b for a,b in ranges) and any(a <= right <= b for a,b in ranges)
'''

CHALK = '''\
def chalk_replacement_student(chalk, k):
    k %= sum(chalk)
    for index, amount in enumerate(chalk):
        if k < amount:
            return index
        k -= amount
'''

CHALK_UNIFORM = '''\
def chalk_replacement_student(chalk, k):
    return k % len(chalk)
'''

MAGIC = '''\
def largest_magic_square_size(grid):
    rows, columns = len(grid), len(grid[0])
    row_prefix = [[0] * (columns + 1) for _ in range(rows)]
    column_prefix = [[0] * columns for _ in range(rows + 1)]
    for row in range(rows):
        for column in range(columns):
            row_prefix[row][column + 1] = row_prefix[row][column] + grid[row][column]
            column_prefix[row + 1][column] = column_prefix[row][column] + grid[row][column]
    def is_magic(top, left, size):
        target = row_prefix[top][left + size] - row_prefix[top][left]
        for offset in range(size):
            row_sum = row_prefix[top + offset][left + size] - row_prefix[top + offset][left]
            column_sum = column_prefix[top + size][left + offset] - column_prefix[top][left + offset]
            if row_sum != target or column_sum != target:
                return False
        diagonal_one = sum(grid[top + offset][left + offset] for offset in range(size))
        diagonal_two = sum(grid[top + offset][left + size - 1 - offset] for offset in range(size))
        return diagonal_one == target and diagonal_two == target
    for size in range(min(rows, columns), 1, -1):
        for top in range(rows - size + 1):
            for left in range(columns - size + 1):
                if is_magic(top, left, size):
                    return size
    return 1
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1889: entry(
        "minimum_packaging_waste", [("packages", "list[int]"), ("boxes", "list[list[int]]")], "int",
        ["arrays", "sorting", "binary-search", "prefix-sums"],
        ["There are at most 100000 packages and suppliers in total.", "Package and box sizes are positive.",
         "Choose one supplier; each package uses that supplier's smallest fitting box, and return minimum waste modulo 1000000007 or -1."],
        [([[2,3,5],[[4,8],[2,8]]], "The second supplier uses sizes 2, 8, and 8, wasting six total units."),
         ([[2,3,5],[[1,4],[2,3],[3,4]]], "No supplier has a box large enough for size five, so packaging is impossible.")],
        [[packages,boxes] for packages,boxes in [
            ([1],[[1]]),([2,3,5],[[4,8],[2,8]]),([2,3,5],[[1,4],[2,3],[3,4]]),
            ([1,2],[[2],[1,2]]),([5,5],[[5],[6]]),([1,4,6],[[3,6],[4,7],[6]]),
            ([3,8,2],[[2,4,8],[3,9]]),([10],[[1,2,3],[10]]),([2,2,3],[[2,3],[4]]),
            ([7,1,5,3],[[4,8],[2,6,9]]),([9,9,1],[[9],[2,10]]),([4,6,8],[[5,7,9],[4,8]]),
            ([1,10,20],[[5,15,25],[20]]),([6,2,11,4],[[3,7,12],[2,6,11]]),
        ]],
        PACKAGING,
        [PACKAGING.replace("bisect_right(ordered_packages, box", "__import__('bisect').bisect_left(ordered_packages, box"), PACKAGING_FIRST],
        ["Uses a left boundary and fails to assign packages whose size exactly equals the box.",
         "Returns the first viable supplier instead of comparing waste across every supplier."],
        packaging_oracle, random_packaging,
        lesson("Sort packages once and consider each supplier independently in increasing box-size order.",
               "Binary-search how many remaining packages fit each box and use package prefix sums to add their waste as a group.",
               "Reject suppliers whose largest box cannot fit the largest package; minimize waste over the rest.",
               "Every package is assigned at the first fitting box for that supplier, which is individually optimal, and comparing suppliers gives the global optimum."),
        "O(n*log(n) + total_boxes*log(n))", "O(n)", 8),
    1891: entry(
        "maximum_ribbon_piece_length", [("ribbons", "list[int]"), ("k", "int")], "int",
        ["arrays", "binary-search"],
        ["There are at most 100000 ribbons, each with positive integer length.", "1 <= k <= 1000000000.",
         "Cut at least k equal integer-length pieces; return zero when even length one is impossible."],
        [([[9,7,5],3], "Length five yields one piece from each ribbon, while length six yields only two pieces."),
         ([[7,5,9],4], "Length four yields four pieces total, and length five yields only three.")],
        [[ribbons,k] for ribbons,k in [
            ([1],1),([1],2),([9,7,5],3),([7,5,9],4),([5,7,9],22),([10,10],4),
            ([10,10],3),([2,3],1),([2,3],6),([100],10),([8,8,8],6),([1,2,3,4],5),
            ([20,15,10],7),([4,4,9,9],8),
        ]],
        RIBBON,
        [RIBBON.replace("ribbon // middle", "(ribbon + middle - 1) // middle"),
         RIBBON.replace("pieces >= k", "pieces > k")],
        ["Counts a partial leftover as another full-length piece by using ceiling division.",
         "Rejects lengths that produce exactly the required number of pieces."],
        ribbon_oracle, random_ribbon,
        lesson("For a proposed length x, ribbon r produces floor(r/x) pieces.",
               "The total piece count never increases as x grows, so feasibility is monotonic.",
               "Use an upper-mid binary search and keep feasible lengths on the left boundary.",
               "The invariant retains every possible optimum, and termination at the largest feasible boundary returns exactly the requested maximum."),
        "O(n*log(max ribbon))", "O(1)", 6),
    1893: entry(
        "every_integer_is_covered", [("ranges", "list[list[int]]"), ("left", "int"), ("right", "int")], "bool",
        ["arrays", "prefix-sums", "intervals"],
        ["There are 1 through 50 inclusive intervals with endpoints between 1 and 50.", "1 <= left <= right <= 50.",
         "Every integer in the inclusive query range must belong to at least one inclusive interval."],
        [([[[1,2],[3,4],[5,6]],2,5], "Two through five are covered by the three adjacent intervals."),
         ([[[1,10],[10,20]],21,21], "Twenty-one lies outside every interval, so coverage fails.")],
        [[ranges,left,right] for ranges,left,right in [
            ([[1,1]],1,1),([[1,2],[3,4],[5,6]],2,5),([[1,10],[10,20]],21,21),
            ([[1,2],[4,5]],1,5),([[2,5]],2,5),([[2,5]],1,5),([[1,50]],1,50),
            ([[1,3],[5,7],[3,5]],2,6),([[10,20]],15,15),([[1,1],[3,3]],1,3),
            ([[5,8],[1,2],[3,4]],1,8),([[20,30],[31,40]],25,35),
            ([[1,10],[12,20]],10,12),([[7,7],[8,8],[9,9]],7,9),
        ]],
        COVERAGE,
        [COVERAGE.replace("difference[end + 1]", "difference[end]"), COVERAGE_ENDPOINTS],
        ["Treats interval ends as exclusive instead of inclusive.",
         "Checks only the query endpoints and can miss an uncovered gap between them."],
        coverage_oracle, random_coverage,
        lesson("An inclusive interval adds one at its start and removes one immediately after its end.",
               "Prefix-sum the difference array to obtain the active interval count at every integer.",
               "Reject when any value from left through right has active count zero.",
               "The prefix count equals the number of intervals covering each value, so positivity throughout the query is necessary and sufficient."),
        "O(number of ranges + 50)", "O(50)", 3),
    1894: entry(
        "chalk_replacement_student", [("chalk", "list[int]"), ("k", "int")], "int",
        ["arrays", "prefix-sums", "simulation"],
        ["There are at most 100000 students and every chalk requirement is positive.", "1 <= k <= 1000000000.",
         "A student proceeds when exactly enough chalk remains; replacement occurs only when remaining chalk is smaller than the requirement."],
        [([[5,1,5],22], "Two full rounds use twenty-two pieces, leaving zero, so student zero replaces the chalk."),
         ([[3,4,1,2],25], "Two full rounds leave five; student zero uses three and student one then lacks four, so return one.")],
        [[chalk,k] for chalk,k in [
            ([1],1),([1],10),([5,1,5],22),([3,4,1,2],25),([2,3],1),([2,3],2),
            ([2,3],4),([2,3],5),([10,1,1],9),([10,1,1],10),([4,4,4],20),
            ([1,2,3,4],100),([7,2,9],37),([6,1,8,3],55),
        ]],
        CHALK,
        [CHALK.replace("if k < amount:", "if k <= amount:"), CHALK_UNIFORM],
        ["Makes a student replace chalk when exactly enough remains, rather than letting that student use it.",
         "Treats every student as consuming one piece and reduces the process to a simple index modulo."],
        chalk_oracle, random_chalk,
        lesson("Whole class cycles always consume the same total chalk.",
               "Reduce k modulo the sum of all requirements to skip every complete cycle.",
               "Scan students once, returning before the first requirement larger than the remainder.",
               "Modulo removes only complete cycles with identical state, and the final scan exactly simulates the remaining partial cycle."),
        "O(n)", "O(1)", 5),
    1895: entry(
        "largest_magic_square_size", [("grid", "list[list[int]]")], "int",
        ["matrices", "prefix-sums", "simulation"],
        ["The grid has at most 50 rows and 50 columns.", "Cell values are positive and need not be distinct.",
         "Every row, every column, and both main diagonals of the chosen square must share one sum."],
        [([[[7,1,4,5,6],[2,5,1,6,4],[1,5,4,3,2],[1,2,7,3,4]]], "The largest valid region has side length three."),
         ([[[5,1,3,1],[9,3,3,1],[1,3,3,8]]], "A 2-by-2 region is magic, but no 3-by-3 region satisfies all required sums.")],
        [[grid] for grid in [
            [[1]],[[1,2]],[[1],[2]],[[1,1],[1,1]],[[1,2],[2,1]],
            [[8,1,6],[3,5,7],[4,9,2]],[[1,1,2],[1,1,2],[1,1,2]],
            [[7,1,4,5,6],[2,5,1,6,4],[1,5,4,3,2],[1,2,7,3,4]],
            [[5,1,3,1],[9,3,3,1],[1,3,3,8]],[[2,2,2],[2,2,2],[2,2,2]],
            [[1,2,3],[4,5,6],[7,8,9]],[[4,9,2,7],[3,5,7,1],[8,1,6,2]],
            [[10,10],[10,10]],[[6,1,8],[7,5,3],[2,9,4],[1,1,1]],
        ]],
        MAGIC,
        [MAGIC.replace("return diagonal_one == target and diagonal_two == target", "return True"),
         MAGIC.replace(" or column_sum != target", "")],
        ["Checks row and column sums but omits both required diagonals.",
         "Checks rows and diagonals but omits the column sums."],
        magic_oracle, random_magic,
        lesson("Row and column prefix sums make every candidate line sum available in constant time.",
               "Try side lengths from largest downward and compare every row and column with the first row's sum.",
               "Also compute both diagonals; return the first valid size, with size one as the fallback.",
               "Every square is examined at its size, all defining lines are checked, and descending order makes the first success the largest."),
        "O(rows*columns*min(rows,columns)^2)", "O(rows*columns)", 7),
}
