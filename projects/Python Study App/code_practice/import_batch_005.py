"""Reviewed grid DP, binary search, and enumeration problems with independent oracles."""
from itertools import combinations, product
from math import comb

from .import_batch_003 import entry


PHONE = {str(i): letters for i, letters in enumerate(("abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"), 2)}


def phone_oracle(args):
    return ["".join(chars) for chars in product(*(PHONE[d] for d in args[0]))]


def sum_oracle(args):
    candidates, target = args
    values = sorted(candidates)
    # Enumerate multiplicity vectors, not recursive pick/skip paths.
    return [[v for v, count in zip(values, counts) for _ in range(count)]
            for counts in product(*(range(target // v + 1) for v in values))
            if sum(v * count for v, count in zip(values, counts)) == target]


def paths_oracle(args):
    m, n = args
    return comb(m + n - 2, m - 1)


def monotone_paths(rows, cols):
    for downward in combinations(range(rows + cols - 2), rows - 1):
        down = set(downward)
        row = col = 0
        path = [(0, 0)]
        for step in range(rows + cols - 2):
            if step in down:
                row += 1
            else:
                col += 1
            path.append((row, col))
        yield path


def obstacles_oracle(args):
    grid, = args
    return sum(all(grid[r][c] == 0 for r, c in path) for path in monotone_paths(len(grid), len(grid[0])))


def cost_oracle(args):
    grid, = args
    return min(sum(grid[r][c] for r, c in path) for path in monotone_paths(len(grid), len(grid[0])))


def matrix_oracle(args):
    matrix, target = args
    return any(target == value for row in matrix for value in row)


def combinations_oracle(args):
    return [list(values) for values in combinations(range(1, args[0] + 1), args[1])]


def subsets_oracle(args):
    values, = args
    return [[v for index, v in enumerate(values) if mask & (1 << index)] for mask in range(1 << len(values))]


def duplicate_subsets_oracle(args):
    values, = args
    return [list(row) for row in sorted({tuple(sorted(v for i, v in enumerate(values) if mask & (1 << i)))
                                        for mask in range(1 << len(values))})]


def decode_oracle(args):
    text, = args
    # Enumerate every cut between digits; valid segments are exactly 1..26.
    total = 0
    for mask in range(1 << (len(text) - 1)):
        cuts = [0] + [i + 1 for i in range(len(text) - 1) if mask & (1 << i)] + [len(text)]
        parts = [text[a:b] for a, b in zip(cuts, cuts[1:])]
        total += all(part[0] != "0" and 1 <= int(part) <= 26 for part in parts)
    return total


def ip_oracle(args):
    text, = args
    out = []
    for a, b, c in combinations(range(1, len(text)), 3):
        parts = [text[:a], text[a:b], text[b:c], text[c:]]
        if all(1 <= len(part) <= 3 and (len(part) == 1 or part[0] != "0") and int(part) <= 255 for part in parts):
            out.append(".".join(parts))
    return out


def random_phone(rng):
    return ["".join(rng.choice("23456789") for _ in range(rng.randint(1, 4)))]


def random_sum(rng):
    return [rng.sample(range(2, 16), rng.randint(1, 5)), rng.randint(1, 20)]


def random_paths(rng):
    return [rng.randint(1, 15), rng.randint(1, 15)]


def random_obstacles(rng):
    rows, cols = rng.randint(1, 5), rng.randint(1, 5)
    return [[[int(rng.random() < .3) for _ in range(cols)] for _ in range(rows)]]


def random_cost(rng):
    rows, cols = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randint(0, 20) for _ in range(cols)] for _ in range(rows)]]


def random_matrix(rng):
    rows, cols = rng.randint(1, 8), rng.randint(1, 8)
    values = sorted(rng.sample(range(-500, 501), rows * cols))
    return [[values[i:i + cols] for i in range(0, len(values), cols)],
            rng.choice(values) if rng.random() < .5 else rng.randint(-500, 500)]


def random_combinations(rng):
    n = rng.randint(1, 10)
    return [n, rng.randint(1, n)]


def random_subsets(rng):
    return [rng.sample(range(-10, 11), rng.randint(1, 10))]


def random_duplicates(rng):
    return [[rng.randint(-3, 3) for _ in range(rng.randint(1, 8))]]


def random_decode(rng):
    return ["".join(rng.choice("0011223679") for _ in range(rng.randint(1, 10)))]


def random_ip(rng):
    if rng.random() < .5:
        return ["".join(str(rng.randrange(256)) for _ in range(4))]
    return ["".join(rng.choice("0123569") for _ in range(rng.randint(1, 20)))]


PHONE_REFERENCE = '''\
def phone_combinations(digits):
    mapping = {"2":"abc", "3":"def", "4":"ghi", "5":"jkl", "6":"mno", "7":"pqrs", "8":"tuv", "9":"wxyz"}
    answer, path = [], []
    def visit(index):
        if index == len(digits):
            answer.append("".join(path))
            return
        for letter in mapping[digits[index]]:
            path.append(letter)
            visit(index + 1)
            path.pop()
    visit(0)
    return answer
'''
SUM = '''\
def combination_sum(candidates, target):
    values = sorted(candidates)
    answer, path = [], []
    def visit(start, remaining):
        if remaining == 0:
            answer.append(path.copy())
            return
        for i in range(start, len(values)):
            if values[i] > remaining:
                break
            path.append(values[i])
            visit(i, remaining - values[i])
            path.pop()
    visit(0, target)
    return answer
'''
PATHS = '''\
def unique_paths(m, n):
    ways = [1] * n
    for row in range(1, m):
        for col in range(1, n):
            ways[col] += ways[col - 1]
    return ways[-1]
'''
OBSTACLES = '''\
def obstacle_paths(obstacle_grid):
    rows, cols = len(obstacle_grid), len(obstacle_grid[0])
    memo = {}
    def visit(row, col):
        if row >= rows or col >= cols or obstacle_grid[row][col] == 1:
            return 0
        if row == rows - 1 and col == cols - 1:
            return 1
        if (row, col) not in memo:
            memo[row, col] = visit(row + 1, col) + visit(row, col + 1)
        return memo[row, col]
    return visit(0, 0)
'''
COST = '''\
def minimum_path_sum(grid):
    costs = [float("inf")] * len(grid[0])
    costs[0] = 0
    for row in grid:
        for col, value in enumerate(row):
            costs[col] = value + min(costs[col], costs[col - 1] if col else float("inf"))
    return costs[-1]
'''
MATRIX = '''\
def search_matrix(matrix, target):
    rows, cols = len(matrix), len(matrix[0])
    left, right = 0, rows * cols - 1
    while left <= right:
        middle = (left + right) // 2
        value = matrix[middle // cols][middle % cols]
        if value == target:
            return True
        if value < target:
            left = middle + 1
        else:
            right = middle - 1
    return False
'''
COMBINATIONS = '''\
def choose_numbers(n, k):
    answer, path = [], []
    def visit(start):
        if len(path) == k:
            answer.append(path.copy())
            return
        needed = k - len(path)
        for value in range(start, n - needed + 2):
            path.append(value)
            visit(value + 1)
            path.pop()
    visit(1)
    return answer
'''
SUBSETS = '''\
def subsets(nums):
    answer, path = [], []
    def visit(index):
        if index == len(nums):
            answer.append(path.copy())
            return
        visit(index + 1)
        path.append(nums[index])
        visit(index + 1)
        path.pop()
    visit(0)
    return answer
'''
DUPLICATES = '''\
def subsets_with_duplicates(nums):
    values = sorted(nums)
    answer, path = [], []
    def visit(start):
        answer.append(path.copy())
        for i in range(start, len(values)):
            if i > start and values[i] == values[i - 1]:
                continue
            path.append(values[i])
            visit(i + 1)
            path.pop()
    visit(0)
    return answer
'''
DECODE = '''\
def decode_ways(s):
    two_back, one_back = 1, int(s[0] != "0")
    for i in range(1, len(s)):
        current = one_back if s[i] != "0" else 0
        if 10 <= int(s[i-1:i+1]) <= 26:
            current += two_back
        two_back, one_back = one_back, current
    return one_back
'''
IP = '''\
def restore_ip_addresses(s):
    answer, parts = [], []
    def visit(start):
        slots = 4 - len(parts)
        remaining = len(s) - start
        if remaining < slots or remaining > slots * 3:
            return
        if slots == 0:
            answer.append(".".join(parts))
            return
        for length in range(1, 4):
            part = s[start:start + length]
            if len(part) != length or (length > 1 and part[0] == "0") or int(part) > 255:
                continue
            parts.append(part)
            visit(start + length)
            parts.pop()
    visit(0)
    return answer
'''

BATCH = {
    17: entry("phone_combinations", [("digits","str")], "list[str]", ["strings","recursion","backtracking"],
        ["1–4 digits, each from 2 through 9.", "Mappings: 2→abc, 3→def, 4→ghi, 5→jkl, 6→mno, 7→pqrs, 8→tuv, 9→wxyz.", "Return every combination exactly once, in any order."],
        [(["23"],"Choose one of a/b/c followed by one of d/e/f: three times three gives nine strings."),
         (["7"],"Digit 7 has four letters, so return p, q, r, and s as separate one-letter strings.")],
        [[s] for s in ("2","9","22","79","92","234","2222","9999","2789","68","54","333")],
        PHONE_REFERENCE, [PHONE_REFERENCE.replace('"pqrs"','"pqr"').replace('"wxyz"','"wxy"'),
                          PHONE_REFERENCE.replace('for letter in mapping[digits[index]]:', 'for letter in mapping[digits[index]][:1]:')],
        ["Assumes every key has three letters, losing s and z.","Explores only the first letter at each position."], phone_oracle, random_phone,
        ["Each output chooses exactly one letter per input position.","Track a prefix and branch over the current digit's letters.","At the end save the joined prefix; otherwise append a letter, recurse to the next position, then undo the append.","Digits 7 and 9 have four branches, not three."],
        "The recursion depth identifies the next digit and the path stores letters already chosen. Explore each mapped letter, recurse, then remove it so sibling branches share only the unchanged prefix. Each leaf is a distinct choice vector and produces one output string. The maximum branching factor is four; output construction takes O(d·4^d) time and O(d) auxiliary stack space excluding results.", "O(d × 4^d)", "O(d) excluding output", difficulty=5),
    39: entry("combination_sum", [("candidates","list[int]"),("target","int")], "list[list[int]]", ["arrays","recursion","backtracking"],
        ["1–30 distinct candidates, each from 2 through 40; target is 1–40.","Reuse any candidate any number of times. At most 150 unique result combinations exist.","Order within and between combinations is ignored, but duplicate combinations are not allowed."],
        [([[2,3,6,7],7],"2+2+3 and 7 are the two combinations; reusing 2 is permitted."),
         ([[2,3,5],8],"The combinations are four 2s, 2+3+3, and 3+5. Different orderings of these same values are not additional results.")],
        [[[2],1],[[2],2],[[2],3],[[2],4],[[3],9],[[3,2],7],[[2,4],8],[[5,7],1],[[40],40],[[2,3],6],[[3,4,5],10],[[6,7,8],15]],
        SUM, [SUM.replace("visit(i, remaining - values[i])","visit(i + 1, remaining - values[i])"),
              SUM.replace("range(start, len(values))","range(0, len(values))")],
        ["Treats each candidate as single-use, dropping combinations that repeat a value.","Restarts from the first value and emits different orderings of the same combination."], sum_oracle, random_sum,
        ["A combination is determined by multiplicities, not the order of picks.","Sort candidates and never move backward in candidate index within a path.","For each candidate at or after start, recurse with that same index and reduced remainder. Save a copy when the remainder is zero.","Reusing the current index permits repetition; using index+1 would solve the different single-use problem."],
        "Keep candidate indices nondecreasing to generate each multiset once. At each choice, subtract its value and recurse starting at the same index so it remains reusable. Stop trying larger candidates when a value exceeds the remainder. Reaching remainder zero records a complete combination. The search is output-sensitive and exponential in the worst case; with depth d=target/min(candidate), O(c^d·d) is a conservative upper bound including result copies.","O(c^d × d), d = target/min(candidate)","O(c + d) excluding output",difficulty=5),
    62: entry("unique_paths", [("m","int"),("n","int")], "int", ["matrix","dynamic-programming"],
        ["1 <= m,n <= 100. The answer is at most 2×10^9.","Start at the top-left cell, finish at the bottom-right cell, and move only right or down."],
        [([3,7],"Each route contains two down moves and six right moves. Choosing the two down positions among eight gives 28 routes."),
         ([3,2],"The possible move orders are DDR, DRD, and RDD, so there are three routes.")],
        [[1,1],[1,2],[2,1],[2,2],[2,3],[3,3],[4,3],[3,4],[5,5],[10,10],[100,1],[1,100]],
        PATHS, [PATHS.replace("ways = [1] * n","ways = [0] * n"),PATHS.replace("range(1, m)","range(1, m - 1)")],
        ["Omits the first-row boundary routes.","Stops one row before the destination."], paths_oracle, random_paths,
        ["Every route into a cell comes from above or from its left.","Store path counts for one row and update them left to right.","Initialize a row of ones; on each later row set ways[c] += ways[c-1] for c>0.","A one-row or one-column grid has exactly one route, and a 1×1 grid needs no moves."],
        "All cells in the first row have one route because only right moves are possible. For each subsequent row, add the count from the previous column in the current row to the old count from the same column in the previous row. The final entry counts all routes to the destination. The oracle uses a binomial coefficient rather than this recurrence.","O(mn)","O(n)",difficulty=5),
    63: entry("obstacle_paths", [("obstacle_grid","list[list[int]]")], "int", ["matrix","recursion","dynamic-programming"],
        ["A rectangular 1–100 by 1–100 grid contains only 0 (open) or 1 (blocked).", "Move only right/down, never through blocked cells. The answer is at most 2×10^9."],
        [([[[0,0,0],[0,1,0],[0,0,0]]],"The center is blocked. Only the route along the top/right edges and the route along the left/bottom edges remain."),
         ([[[0,1],[0,0]]],"Right is blocked at the start, so the only route goes down then right.")],
        [[g] for g in ([[0]],[[1]],[[0,0]],[[0,1]],[[1,0]],[[0],[0]],[[0],[1]],[[1],[0]],[[0,0],[0,0]],[[0,0],[0,1]],[[1,0],[0,0]],[[0,1,0],[0,1,0],[0,0,0]])],
        OBSTACLES, [OBSTACLES.replace(" or obstacle_grid[row][col] == 1", ""),
                    OBSTACLES.replace("return 1", "return 0")],
        ["Ignores obstacles and counts routes through blocked cells.","Forgets that reaching an open destination completes one valid route."], obstacles_oracle, random_obstacles,
        ["An invalid or blocked cell contributes no routes; an open destination contributes one.","Recursively add the answers from the right and down neighbors, caching by coordinates.","Check bounds and obstacles first, then the destination. Memoize visit(r+1,c)+visit(r,c+1).", "Without caching, different paths repeatedly solve the same remaining subgrid."],
        "Define visit(r,c) as the number of valid routes from that cell to the destination. Outside or blocked cells return zero; the open destination returns one. Every other result is the sum from its two allowed next cells. Memoization ensures each coordinate is solved at most once. The recursion has depth at most m+n; a bottom-up row-array solution can reduce memory to O(n). The oracle independently enumerates complete move sequences and checks every visited cell.","O(mn)","O(mn) memo plus O(m+n) stack",difficulty=5,
        stress=[([[[1]*100 for _ in range(100)]],0), ([[[0]*100]],1),
                ([[[0 if row == 0 or col == 99 else 1 for col in range(100)] for row in range(100)]],1)]),
    64: entry("minimum_path_sum", [("grid","list[list[int]]")], "int", ["matrix","dynamic-programming","recursion"],
        ["A rectangular 1–200 by 1–200 grid has cell values between 0 and 200.","Move only right or down. Include both the starting and destination cell values in the total."],
        [([[[1,3,1],[1,5,1],[4,2,1]]],"Following right, right, down, down visits 1+3+1+1+1=7, the minimum."),
         ([[[1,2,3],[4,5,6]]],"The cheapest route visits 1,2,3,6 for a total of 12.")],
        [[g] for g in ([[0]],[[7]],[[1,2]],[[1],[2]],[[0,0],[0,0]],[[1,9],[2,3]],[[9,1],[1,9]],[[1,1,1]],[[1],[1],[1]],[[0,5,0],[1,1,1]],[[200,200],[200,200]],[[2,9,1],[1,9,1],[1,1,1]])],
        COST, [COST.replace("min(costs[col],", "max(costs[col],").replace('float("inf")', 'float("-inf")'),
               COST.replace("costs[0] = 0", "costs[0] = -grid[0][0]")],
        ["Computes the most expensive path rather than the cheapest one.","Leaves the starting cell out of the path sum."], cost_oracle, random_cost,
        ["A cheapest route to a cell must use a cheapest route to one of its two predecessors.","Add the current cell cost to the smaller reachable predecessor total.","Update a row array left to right; the old same-column value comes from above and the new previous-column value comes from the left.","Equivalently, recursively minimize the right/down continuation and memoize coordinates; boundaries must be unreachable, not free."],
        "The DP entry for a cell is its value plus the smaller cost from above or left. A single row array retains the previous row until each entry is replaced; initialize only the virtual predecessor of the starting cell to zero and other unreachable states to infinity. This includes both endpoints and handles zero costs correctly. The oracle enumerates complete routes and directly sums their cells.","O(mn)","O(n)",difficulty=5,
        stress=[([[[200]*200 for _ in range(200)]],79800)]),
    74: entry("search_matrix", [("matrix","list[list[int]]"),("target","int")], "bool", ["matrix","binary-search"],
        ["A rectangular grid has 1–100 rows and columns. Values and target are in [-10,000,10,000].", "Rows are nondecreasing; each row starts with a value strictly greater than the previous row's final value.", "Required search time is O(log(mn))."],
        [([[[1,3,5,7],[10,11,16,20],[23,30,34,60]],3],"The target 3 occurs at row zero, column one."),
         ([[[1,3,5,7],[10,11,16,20],[23,30,34,60]],13],"13 lies between 11 and 16 but is not present, so return false.")],
        [[[[1]],1],[[[1]],0],[[[1]],2],[[[1,2,3]],3],[[[1],[2],[3]],2],[[[-5,-2],[0,3]],-5],[[[-5,-2],[0,3]],3],[[[1,2],[4,5]],3],[[[1,1,2],[3,3,4]],3],[[[1,2,3],[4,5,6]],6],[[[1,2,3],[4,5,6]],7],[[[-10000,10000]],0]],
        MATRIX, [MATRIX.replace("while left <= right:","while left < right:"),"def search_matrix(matrix, target):\n    return target in matrix[0]\n"],
        ["Never examines the last remaining binary-search candidate.","Checks only the first row."], matrix_oracle, random_matrix,
        ["The row-boundary rule makes the entire row-major sequence sorted.","Binary-search a virtual array without allocating a flattened copy.","Translate midpoint to row=mid//column_count and column=mid%column_count, then update the usual search bounds.","Use the number of columns for index conversion, including rectangular and single-column grids."],
        "Treat the grid as one sorted sequence of length m×n. Its index i refers to matrix[i//n][i%n]. Binary-search this virtual sequence, retaining the equality case and examining the final remaining candidate. No flattening is needed, so the auxiliary space is constant. A linear scan serves as an independent correctness oracle, not as the reference complexity target.","O(log(mn))","O(1)",difficulty=5),
    77: entry("choose_numbers", [("n","int"),("k","int")], "list[list[int]]", ["recursion","backtracking"],
        ["1 <= k <= n <= 20.", "Choose k different values from 1 through n. Return each combination once; ordering is ignored."],
        [([4,2],"Choose any two of 1,2,3,4: the six combinations are 12,13,14,23,24,34."),([1,1],"The only possible selection is [1].")],
        [[2,1],[2,2],[3,1],[3,2],[3,3],[4,1],[4,3],[4,4],[5,2],[5,3],[20,1],[20,19]],
        COMBINATIONS, [COMBINATIONS.replace("answer.append(path.copy())","answer.append(path)"),COMBINATIONS.replace("n - needed + 2","n - needed + 1")],
        ["Saves the mutable path itself, so backtracking empties all recorded combinations.","Prunes the last feasible choice due to an exclusive-range off-by-one."], combinations_oracle, random_combinations,
        ["An increasing path represents a combination without redundant permutations.","After picking a value, only consider larger values in the next recursive call.","Save at length k. Otherwise iterate choices only while enough larger values remain to finish the path.","Undo the appended value after each recursive branch."],
        "Build strictly increasing paths. Starting the next call at chosen+1 prevents both repetition and reordering duplicates. If needed entries remain, the current choice can be at most n-needed+1; later choices cannot leave enough values to finish. Copy completed paths into the result. There are C(n,k) outputs of length k, with O(k) auxiliary recursion space.","O(k × C(n,k))","O(k) excluding output",difficulty=5),
    78: entry("subsets", [("nums","list[int]")], "list[list[int]]", ["arrays","recursion","backtracking"],
        ["1–10 distinct integers, each in [-10,10].", "Return all subsets, including empty and full, with no duplicate results. Element and result ordering are ignored."],
        [([[1,2,3]],"Each of three values is either selected or omitted, giving 2³=8 subsets including [] and [1,2,3]."),([[0]],"There are exactly two choices: [] and [0].")],
        [[v] for v in ([1],[-1],[1,2],[2,1],[-1,0],[3,1,2],[0,1,2,3],[-3,-2,-1],[5,0,-5],[10,-10],[1,3,5,7],list(range(10)))],
        SUBSETS, [SUBSETS.replace("answer.append(path.copy())","answer.append(path.copy()) if path else None"),SUBSETS.replace("answer.append(path.copy())","answer.append(path)")],
        ["Drops the empty subset.","Stores a shared mutable path that is later emptied during backtracking."], subsets_oracle, random_subsets,
        ["For each input value, make an independent include/exclude decision.","Recurse on the next position for both choices.","At the end, append a copy of the selected path. Restore the path after the include branch.","The empty path is a valid completed result, and saved paths must not share mutable storage."],
        "At every index explore two branches: omit the value, or include it and later undo that inclusion. A leaf corresponds to one unique bitmask of decisions. Since input values are distinct, all 2^n results are different. Copy the path at each leaf so future undo operations cannot change saved outputs. The oracle generates subsets directly from integer bitmasks.","O(n × 2^n)","O(n) excluding output",difficulty=5),
    90: entry("subsets_with_duplicates", [("nums","list[int]")], "list[list[int]]", ["arrays","recursion","backtracking"],
        ["1–10 integers, each in [-10,10]; duplicates are allowed.","Each array occurrence is usable at most once. Return each distinct multiset subset once, ignoring order."],
        [([[1,2,2]],"[2,2] is allowed because two copies exist, but choosing the first or second 2 alone must produce only one [2]. There are six distinct subsets."),
         ([[0]],"The subsets are [] and [0].")],
        [[v] for v in ([1],[1,1],[1,1,1],[2,1,2],[-1,-1],[0,0,0],[1,2],[2,2,3,3],[3,2,1],[-1,0,-1],[10,-10,10],[1]*10)],
        DUPLICATES, [DUPLICATES.replace("if i > start and values[i] == values[i - 1]:","if False:"),DUPLICATES.replace("sorted(nums)","sorted(set(nums))")],
        ["Explores equal sibling choices and emits duplicate subsets.","Removes duplicate occurrences, losing valid subsets with repeated values."], duplicate_subsets_oracle, random_duplicates,
        ["Equal values can be used multiple times when there are multiple occurrences, but equivalent choices at one depth should not repeat.","Sort the input and skip equal adjacent candidates only among siblings in the same recursive call.","Save the current subset. For i from start, skip when i>start and values[i]==values[i-1]; otherwise choose i and recurse from i+1.","Do not globally discard duplicates: [2,2] and [2] are distinct valid subsets."],
        "Sort to place equal values together. Within one call, selecting a later copy as the first new choice would duplicate the branch from the earlier copy, so skip it. Once a value has been selected, the next recursive level may select another occurrence. This permits every valid multiplicity while producing each multiset exactly once. The independent oracle enumerates all occurrence masks and deduplicates their sorted tuples.","O(n × 2^n)","O(n) excluding output",difficulty=5),
    91: entry("decode_ways", [("s","str")], "int", ["strings","dynamic-programming","recursion"],
        ["1–100 decimal digits; leading zeros are possible.","Valid codes are decimal strings 1 through 26, with no leading zero. Return the count of full-string decodings; the answer fits signed 32-bit."],
        [(["12"],"Decode as 1|2 (AB) or 12 (L), giving two ways."),(["11106"],"The valid segmentations are 1|1|10|6 and 11|10|6. A segment 06 is invalid.")],
        [[s] for s in ("0","1","9","10","20","30","06","26","27","100","101","226")],
        DECODE, [DECODE.replace('current = one_back if s[i] != "0" else 0','current = one_back'),DECODE.replace("10 <= int(s[i-1:i+1]) <= 26","1 <= int(s[i-1:i+1]) <= 26")],
        ["Treats a standalone zero as a valid code.","Allows two-digit codes with a leading zero, such as 06."], decode_oracle, random_decode,
        ["The final decoded letter consumes either one digit or two digits.","Add the count for each valid last segment, retaining only the preceding two prefix counts.","A nonzero last digit adds ways[i-1]; a pair between 10 and 26 adds ways[i-2]. Otherwise that contribution is zero.","A zero is usable only as part of 10 or 20. A memoized recursive suffix formulation uses the same choices."],
        "For each prefix, count the decodings ending with a valid one-digit code and those ending with a valid two-digit code. These groups are disjoint. Keep the previous two counts rather than an entire DP table. Initialize the empty-prefix count to one and the first-digit count according to whether it is nonzero. The oracle independently enumerates all positions of cuts and validates every resulting segment.","O(n)","O(1)",difficulty=5,
        stress=[(["10"*50],1),(["1"*45],1836311903)]),
    93: entry("restore_ip_addresses", [("s","str")], "list[str]", ["strings","recursion","backtracking"],
        ["1–20 decimal digits. Insert exactly three dots without deleting or reordering digits.","Every segment must be 0–255 with no leading zero except the single digit 0. Return all distinct valid addresses in any order."],
        [(["25525511135"],"The valid splits are 255|255|11|135 and 255|255|111|35."),(["0000"],"Only 0.0.0.0 is valid; longer segments such as 00 have forbidden leading zeros.")],
        [[s] for s in ("1","123","1111","11111","010010","101023","255255255255","256256256256","00000","9999","1234567890123","100100100100")],
        IP, [IP.replace('(length > 1 and part[0] == "0") or ',''), IP.replace(' or int(part) > 255','')],
        ["Accepts segments with leading zeros.","Accepts segment values above 255."], ip_oracle, random_ip,
        ["A valid address uses four segments, each one to three digits long.","Choose the next segment length, validate it, then recurse on the remaining digits.","Reject if remaining digit count cannot fit the remaining slots; accept only after four segments consume the entire string.","Check both the numerical upper bound and the no-leading-zero rule before descending."],
        "Backtrack over segment lengths one, two, and three. Reject leading-zero segments longer than one digit and values above 255. Track how many of the four segments remain and prune when the remaining digits cannot fill them. A completed choice is accepted only after consuming every digit. There are at most 3^4 length-choice branches; forming output strings adds a bounded factor of the input length. The oracle enumerates triples of cut positions instead.","O(n × 3^4)","O(n) excluding output",difficulty=5),
}

for source_id in (17, 93):
    BATCH[source_id]["comparator"] = "unordered"
for source_id in (39, 77, 78, 90):
    BATCH[source_id]["comparator"] = "unordered_nested"
for source_id in (62, 63, 64, 74):
    BATCH[source_id]["topics"] = ["matrices" if topic == "matrix" else topic for topic in BATCH[source_id]["topics"]]
