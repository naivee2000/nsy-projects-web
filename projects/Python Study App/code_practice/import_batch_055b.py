"""Second half of batch 55: matrix, graph, DP, and expression functions."""
from collections import deque
from fractions import Fraction
from math import gcd
import re

from .import_batch_003 import entry


EXTRA_BOUNDARIES = {
    "contest_matches": [[1], [8192]],
    "province_count": [[[[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]]]],
    "longest_one_line": [[[[1, 1, 1], [1, 1, 1], [1, 1, 1]]]],
    "largest_nesting_set": [[[6, 0, 1, 2, 3, 4, 5]], [[1, 2, 0]]],
    "minimum_delete_steps": [["abc", "acb"]],
}


def reviewed_entry(*args, **kwargs):
    """Reject overlapping visible/hidden fixtures while retaining twelve hidden cases."""
    spec = entry(*args, **kwargs)
    fingerprints = {repr(arguments) for arguments, _ in spec["examples"]}
    boundaries = []
    for arguments in spec["boundaries"]:
        fingerprint = repr(arguments)
        if fingerprint not in fingerprints:
            fingerprints.add(fingerprint)
            boundaries.append(arguments)
    for arguments in EXTRA_BOUNDARIES.get(spec["name"], []):
        if len(boundaries) >= 12:
            break
        fingerprint = repr(arguments)
        if fingerprint not in fingerprints:
            fingerprints.add(fingerprint)
            boundaries.append(arguments)
    if len(boundaries) < 12:
        raise ValueError(f"{spec['name']}: add distinct hidden cases")
    spec["boundaries"] = boundaries
    return spec


def hints(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial], editorial


def matrix_distance_oracle(args):
    mat = args[0]
    rows, cols = len(mat), len(mat[0])
    return [[min(abs(row - r) + abs(col - c) for r in range(rows) for c in range(cols) if mat[r][c] == 0)
             for col in range(cols)] for row in range(rows)]


def contest_oracle(args):
    teams = [str(i) for i in range(1, args[0] + 1)]
    while len(teams) > 1:
        teams = [f"({teams[index]},{teams[-1-index]})" for index in range(len(teams) // 2)]
    return teams[0]


def province_oracle(args):
    grid = args[0]
    seen, count = set(), 0
    for start in range(len(grid)):
        if start not in seen:
            count += 1
            queue = [start]
            seen.add(start)
            for city in queue:
                for neighbor, connected in enumerate(grid[city]):
                    if connected and neighbor not in seen:
                        seen.add(neighbor)
                        queue.append(neighbor)
    return count


def split_oracle(args):
    words = args[0]
    choices = [[word, word[::-1]] for word in words]
    best = ""
    def search(index, built):
        nonlocal best
        if index == len(choices):
            for cut in range(len(built)):
                best = max(best, built[cut:] + built[:cut])
            return
        for word in choices[index]:
            search(index + 1, built + word)
    search(0, "")
    return best


def line_oracle(args):
    mat = args[0]
    rows, cols, best = len(mat), len(mat[0]), 0
    for row in range(rows):
        for col in range(cols):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                length, r, c = 0, row, col
                while 0 <= r < rows and 0 <= c < cols and mat[r][c] == 1:
                    length += 1
                    r += dr
                    c += dc
                best = max(best, length)
    return best


def nesting_oracle(args):
    nums = args[0]
    best = 0
    for start in range(len(nums)):
        chain, value = set(), start
        while value not in chain:
            chain.add(value)
            value = nums[value]
        best = max(best, len(chain))
    return best


def squirrel_oracle(args):
    _, _, tree, squirrel, nuts = args
    distance = lambda left, right: abs(left[0] - right[0]) + abs(left[1] - right[1])
    return sum(2 * distance(nut, tree) for nut in nuts) - max(distance(nut, tree) - distance(nut, squirrel) for nut in nuts)


def kill_oracle(args):
    pids, parents, target = args
    children = {}
    for pid, parent in zip(pids, parents):
        children.setdefault(parent, []).append(pid)
    out, queue = [], [target]
    for pid in queue:
        out.append(pid)
        queue.extend(children.get(pid, []))
    return out


def deletion_oracle(args):
    left, right = args
    table = [[0] * (len(right) + 1) for _ in range(len(left) + 1)]
    for row, first in enumerate(left, 1):
        for col, second in enumerate(right, 1):
            table[row][col] = table[row-1][col-1] + 1 if first == second else max(table[row-1][col], table[row][col-1])
    return len(left) + len(right) - 2 * table[-1][-1]


def fraction_oracle(args):
    total = Fraction(0)
    for sign, numerator, denominator in re.findall(r'([+-]?)(\d+)/(\d+)', args[0]):
        total += (-1 if sign == '-' else 1) * Fraction(int(numerator), int(denominator))
    return f"{total.numerator}/{total.denominator}"


def random_matrix(rng):
    rows, cols = rng.randint(1, 6), rng.randint(1, 6)
    mat = [[rng.randint(0, 1) for _ in range(cols)] for _ in range(rows)]
    mat[rng.randrange(rows)][rng.randrange(cols)] = 0
    return [mat]


def random_contest(rng): return [2 ** rng.randint(1, 8)]


def random_provinces(rng):
    size = rng.randint(1, 10)
    grid = [[int(row == col) for col in range(size)] for row in range(size)]
    for row in range(size):
        for col in range(row):
            if rng.random() < .3:
                grid[row][col] = grid[col][row] = 1
    return [grid]


def random_split(rng):
    return [["".join(rng.choice("abcxyz") for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(1, 5))]]


def random_line(rng):
    rows, cols = rng.randint(1, 7), rng.randint(1, 7)
    return [[[rng.randint(0, 1) for _ in range(cols)] for _ in range(rows)]]


def random_nesting(rng):
    nums = list(range(rng.randint(1, 12)))
    rng.shuffle(nums)
    return [nums]


def random_squirrel(rng):
    height, width = rng.randint(2, 12), rng.randint(2, 12)
    point = lambda: [rng.randrange(height), rng.randrange(width)]
    return [height, width, point(), point(), [point() for _ in range(rng.randint(1, 10))]]


def random_processes(rng):
    count = rng.randint(1, 25)
    pids = list(range(1, count + 1))
    parents = [0] + [rng.randint(1, pid - 1) for pid in pids[1:]]
    return [pids, parents, rng.choice(pids)]


def random_words(rng):
    return ["".join(rng.choice("abcd") for _ in range(rng.randint(1, 10))), "".join(rng.choice("abcd") for _ in range(rng.randint(1, 10)))]


def random_fraction(rng):
    terms = [f"{rng.randint(1, 10)}/{rng.randint(1, 10)}" for _ in range(rng.randint(1, 7))]
    return [terms[0] + "".join(rng.choice("+-") + term for term in terms[1:])]


DISTANCE = '''\
def nearest_zero_distances(mat):
    rows, cols = len(mat), len(mat[0])
    answer = [[-1] * cols for _ in range(rows)]
    queue = deque()
    for row in range(rows):
        for col in range(cols):
            if mat[row][col] == 0:
                answer[row][col] = 0
                queue.append((row, col))
    while queue:
        row, col = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt_row, nxt_col = row + dr, col + dc
            if 0 <= nxt_row < rows and 0 <= nxt_col < cols and answer[nxt_row][nxt_col] == -1:
                answer[nxt_row][nxt_col] = answer[row][col] + 1
                queue.append((nxt_row, nxt_col))
    return answer
'''
CONTEST = '''\
def contest_matches(n):
    teams = [str(team) for team in range(1, n + 1)]
    while len(teams) > 1:
        teams = [f"({teams[index]},{teams[-1-index]})" for index in range(len(teams) // 2)]
    return teams[0]
'''
PROVINCES = '''\
def province_count(is_connected):
    seen = set()
    def visit(city):
        seen.add(city)
        for neighbor, connected in enumerate(is_connected[city]):
            if connected and neighbor not in seen:
                visit(neighbor)
    answer = 0
    for city in range(len(is_connected)):
        if city not in seen:
            answer += 1
            visit(city)
    return answer
'''
SPLIT = '''\
def largest_loop_string(strs):
    choices = [max(word, word[::-1]) for word in strs]
    answer = ""
    for index, word in enumerate(choices):
        rest = ''.join(choices[index+1:] + choices[:index])
        for candidate in (strs[index], strs[index][::-1]):
            for cut in range(len(candidate)):
                answer = max(answer, candidate[cut:] + rest + candidate[:cut])
    return answer
'''
LINE = '''\
def longest_one_line(mat):
    rows, cols = len(mat), len(mat[0])
    dp = [[[0, 0, 0, 0] for _ in range(cols)] for _ in range(rows)]
    best = 0
    for row in range(rows):
        for col in range(cols):
            if mat[row][col]:
                dp[row][col][0] = (dp[row][col-1][0] if col else 0) + 1
                dp[row][col][1] = (dp[row-1][col][1] if row else 0) + 1
                dp[row][col][2] = (dp[row-1][col-1][2] if row and col else 0) + 1
                dp[row][col][3] = (dp[row-1][col+1][3] if row and col + 1 < cols else 0) + 1
                best = max(best, *dp[row][col])
    return best
'''
NEST = '''\
def largest_nesting_set(nums):
    seen, best = set(), 0
    for start in range(len(nums)):
        if start in seen:
            continue
        length, value = 0, start
        while value not in seen:
            seen.add(value)
            length += 1
            value = nums[value]
        best = max(best, length)
    return best
'''
SQUIRREL = '''\
def minimum_squirrel_distance(height, width, tree, squirrel, nuts):
    def distance(left, right):
        return abs(left[0] - right[0]) + abs(left[1] - right[1])
    total = sum(2 * distance(nut, tree) for nut in nuts)
    saving = max(distance(nut, tree) - distance(nut, squirrel) for nut in nuts)
    return total - saving
'''
KILL = '''\
def killed_processes(pid, ppid, kill):
    children = {}
    for child, parent in zip(pid, ppid):
        children.setdefault(parent, []).append(child)
    answer = []
    queue = [kill]
    for process in queue:
        answer.append(process)
        queue.extend(children.get(process, []))
    return answer
'''
DELETE = '''\
def minimum_delete_steps(word1, word2):
    previous = list(range(len(word2) + 1))
    for row, first in enumerate(word1, 1):
        current = [row] + [0] * len(word2)
        for col, second in enumerate(word2, 1):
            current[col] = previous[col-1] if first == second else 1 + min(previous[col], current[col-1])
        previous = current
    return previous[-1]
'''
FRACTION = '''\
import re
from math import gcd

def fraction_sum(expression):
    numerator, denominator = 0, 1
    for sign, top, bottom in re.findall(r'([+-]?)(\\d+)/(\\d+)', expression):
        top = int(top) * (-1 if sign == '-' else 1)
        bottom = int(bottom)
        numerator = numerator * bottom + top * denominator
        denominator *= bottom
        divisor = gcd(abs(numerator), denominator)
        numerator //= divisor
        denominator //= divisor
    return f"{numerator}/{denominator}"
'''


BATCH = {
    542: reviewed_entry('nearest_zero_distances', [('mat', 'list[list[int]]')], 'list[list[int]]', ['matrices', 'graphs', 'breadth-first-search'],
        ['1 <= rows, columns; rows * columns <= 10,000.', 'mat contains 0 and 1 and has at least one zero.'],
        [([[[0, 0, 0], [0, 1, 0], [0, 0, 0]]], 'Every 1 touches a zero, so its distance is one.'),
         ([[[0, 0, 0], [0, 1, 0], [1, 1, 1]]], 'The lower row inherits increasing distances 1, 2, 1 from the nearest zeros.')],
        [[matrix] for matrix in ([[0]], [[1, 0]], [[0, 1]], [[0, 1, 1]], [[1, 1, 0]], [[0, 1], [1, 1]], [[1, 0], [1, 1]], [[0, 0], [0, 0]], [[1, 1, 1], [1, 0, 1], [1, 1, 1]], [[0, 1, 1, 1]], [[1], [1], [0]], [[0, 1, 0], [1, 1, 1]])],
        DISTANCE, [DISTANCE.replace('answer[row][col] + 1', 'answer[row][col]'), DISTANCE.replace('queue.append((row, col))', 'pass')],
        ['Never increments the breadth-first distance.', 'Never starts propagation from zero cells.'], matrix_distance_oracle, random_matrix,
        *hints('Distance expands one grid edge at a time.', 'Start every zero simultaneously so the first visit is nearest.', 'Queue all zeros at distance zero, then BFS into unvisited cells.', 'Multi-source BFS assigns each cell at its shortest arrival because BFS processes increasing path length.'), 'O(rows * columns)', 'O(rows * columns)', 5),
    544: reviewed_entry('contest_matches', [('n', 'int')], 'str', ['strings', 'simulation'], ['n is a power of two: 1 <= n <= 2^13.', 'In every round, strongest remaining team pairs with weakest remaining team.'],
        [([4], 'First pair 1 with 4 and 2 with 3, then pair those two matches.'), ([8], 'The same outer-to-inner pairing rule repeats for each round.')],
        [[n] for n in (2, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8, 4)], CONTEST,
        [CONTEST.replace('teams[-1-index]', 'teams[index]'), CONTEST.replace('while len(teams) > 1:', 'if len(teams) > 1:')],
        ['Pairs neighbors rather than strongest with weakest.', 'Stops after only the first round.'], contest_oracle, random_contest,
        *hints('A match becomes one team-like item in the next round.', 'Keep the current bracket entries in strength order.', 'Pair index i with index -1-i until one bracket string remains.', 'The construction directly mirrors the required pairing order at every round.'), 'O(n)', 'O(n)', 3),
    547: reviewed_entry('province_count', [('is_connected', 'list[list[int]]')], 'int', ['graphs', 'depth-first-search'], ['1 <= n <= 200.', 'is_connected is symmetric and its diagonal entries are one.'],
        [([[[1, 1, 0], [1, 1, 0], [0, 0, 1]]], 'Cities 0 and 1 form one connected component; city 2 forms another.'),
         ([[[1, 0, 0], [0, 1, 0], [0, 0, 1]]], 'No city connects to another, so each city is its own province.')],
        [[grid] for grid in ([[ [1] ]], [[1, 1], [1, 1]], [[1, 0], [0, 1]], [[1, 1, 1], [1, 1, 1], [1, 1, 1]], [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]], [[1, 0, 1], [0, 1, 0], [1, 0, 1]], [[1, 1, 0], [1, 1, 1], [0, 1, 1]], [[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]], [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], [[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 1]], [[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]], [[1, 1, 0], [1, 1, 0], [0, 0, 1]])], PROVINCES,
        [PROVINCES.replace('if city not in seen:', 'if True:'), PROVINCES.replace('if connected and neighbor not in seen:', 'if False:')],
        ['Counts every city even after its component was visited.', 'Traverses only already visited neighbors.'], province_oracle, random_provinces,
        *hints('A province is a connected component.', 'Explore all reachable cities once, then begin another component only when needed.', 'For each unvisited city, increment count and DFS through connected neighbors.', 'The outer loop starts precisely once per connected component.'), 'O(n^2)', 'O(n)', 5),
    555: reviewed_entry('largest_loop_string', [('strs', 'list[str]')], 'str', ['strings', 'greedy'], ['1 <= len(strs) <= 50; total character count <= 1,000.', 'Each string may be kept or reversed before choosing a cut in the circular concatenation.'],
        [([['abc', 'xyz']], 'Use zyx as the first segment and reverse abc after it, yielding zyxcba.'), ([['abc']], 'Every cut and both orientations are considered; cba is largest.')],
        [[words] for words in (['a'], ['ab'], ['ba'], ['ab', 'cd'], ['abc', 'aba'], ['aaa', 'bbb'], ['az', 'za'], ['ab', 'xy', 'za'], ['abc', 'xyz', 'aba'], ['cba', 'abc'], ['z', 'aa', 'by'], ['abc', 'def', 'ghi'])], SPLIT,
        [SPLIT.replace('max(word, word[::-1])', 'word'), SPLIT.replace('for cut in range(len(candidate)):', 'for cut in range(1):')],
        ['Never reverses individual strings.', 'Only cuts at the beginning of a selected string.'], split_oracle, random_split,
        *hints('Lexicographic order rewards the best possible first character and suffix.', 'All non-cut strings can independently use their larger orientation.', 'Try every string as the cut string, both orientations, and all cuts.', 'Only the cut string is split; every other string should be placed in its individually best orientation.'), 'O(total_length^2)', 'O(total_length)', 7),
    562: reviewed_entry('longest_one_line', [('mat', 'list[list[int]]')], 'int', ['matrices', 'dynamic-programming'], ['1 <= rows * columns <= 10,000.', 'mat contains only zero and one; a line may be horizontal, vertical, diagonal, or anti-diagonal.'],
        [([[[0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 1]]], 'The best horizontal, vertical, and diagonal runs all have length three.'),
         ([[[1, 0], [0, 1]]], 'The two diagonal ones form a length-two line.')],
        [[mat] for mat in ([[0]], [[1]], [[0, 0]], [[1, 1, 1]], [[1], [1], [1]], [[1, 0], [0, 1]], [[0, 1], [1, 0]], [[1, 1], [1, 1]], [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [[0, 0, 1], [0, 1, 0], [1, 0, 0]], [[1, 0, 1], [1, 1, 1], [0, 1, 0]], [[0, 1, 0], [1, 0, 1], [0, 1, 0]])], LINE,
        [LINE.replace('range(cols)', 'range(cols - 1)'), LINE.replace('return best', 'return 0')],
        ['Skips the last column.', 'Never counts anti-diagonal runs.'], line_oracle, random_line,
        *hints('Each one can extend four lines ending at its cell.', 'Remember the previous length in each direction.', 'For a one, add one to left/up/up-left/up-right predecessor counts.', 'Every maximal line has a final cell, so tracking runs ending at each cell finds the global maximum.'), 'O(rows * columns)', 'O(rows * columns)', 6),
    565: reviewed_entry('largest_nesting_set', [('nums', 'list[int]')], 'int', ['arrays', 'graphs', 'cycle-detection'], ['1 <= len(nums) <= 100,000.', 'nums is a permutation of 0 through n-1.'],
        [([[5, 4, 0, 3, 1, 6, 2]], 'Starting at 0 visits 5, 6, 2, 0, so the largest set has four values.'),
         ([[0]], 'The self-loop contains one distinct value.')],
        [[nums] for nums in ([0, 1], [1, 0], [0, 2, 1], [1, 2, 0], [2, 0, 1], [1, 0, 3, 2], [4, 0, 1, 2, 3], [0, 1, 2, 3], [3, 4, 0, 1, 2], [1, 2, 3, 4, 0], [2, 3, 4, 5, 0, 1], [5, 4, 0, 3, 1, 6, 2])], NEST,
        [NEST.replace('while value not in seen:', 'if value not in seen:'), NEST.replace('best = max(best, length)', 'best = min(best, length)')],
        ['Follows only one link from every start.', 'Never marks a previously explored cycle.'], nesting_oracle, random_nesting,
        *hints('A permutation decomposes into disjoint cycles.', 'Once a cycle has been counted, no later start inside it can improve the answer.', 'Follow each unvisited start until it reaches seen values; track the length.', 'Marking values globally makes the total traversal linear because each array index is visited at most once.'), 'O(n)', 'O(n)', 5),
    573: reviewed_entry('minimum_squirrel_distance', [('height', 'int'), ('width', 'int'), ('tree', 'list[int]'), ('squirrel', 'list[int]'), ('nuts', 'list[list[int]]')], 'int', ['math', 'greedy', 'matrices'], ['2 <= height, width <= 100; 1 <= len(nuts) <= 5,000.', 'All positions lie in the garden; moves are orthogonal with Manhattan distance.'],
        [([5, 7, [2, 2], [4, 4], [[3, 0], [2, 5]]], 'A round trip from tree for each nut costs 14; starting with the best nut saves two, for 12.'),
         ([2, 2, [0, 0], [1, 1], [[1, 1]]], 'The squirrel starts on the only nut, so it needs only the trip from nut to tree.')],
        [[2, 2, [0, 0], [0, 0], [[1, 1]]], [3, 3, [1, 1], [0, 0], [[2, 2]]], [3, 4, [0, 3], [2, 0], [[1, 1], [2, 3]]], [5, 5, [2, 2], [2, 2], [[0, 0], [4, 4]]], [4, 4, [0, 0], [3, 3], [[0, 3], [3, 0]]], [10, 10, [5, 5], [0, 0], [[9, 9]]], [3, 3, [1, 1], [2, 2], [[1, 1]]], [3, 3, [1, 1], [0, 2], [[0, 0], [2, 2]]], [4, 2, [3, 1], [0, 0], [[1, 0], [2, 1]]], [2, 5, [0, 4], [1, 0], [[1, 4], [0, 0]]], [4, 4, [1, 2], [3, 0], [[0, 1], [3, 3], [2, 2]]], [6, 6, [3, 3], [5, 5], [[0, 0], [5, 0]]]], SQUIRREL,
        [SQUIRREL.replace('max(distance(nut, tree) - distance(nut, squirrel) for nut in nuts)', '0'), SQUIRREL.replace('2 * distance(nut, tree)', 'distance(nut, tree)')],
        ['Always makes the squirrel return to its initial position.', 'Counts every nut trip only once.'], squirrel_oracle, random_squirrel,
        *hints('Except for the first nut, each nut requires a tree-to-nut-to-tree trip.', 'Start from all round trips, then choose the nut with the greatest first-trip saving.', 'Compute 2*tree-distance for every nut; subtract max(tree-distance minus squirrel-distance).', 'Only the first carried nut changes the usual round-trip route, so the choices are independent.'), 'O(number of nuts)', 'O(1)', 5),
    582: reviewed_entry('killed_processes', [('pid', 'list[int]'), ('ppid', 'list[int]'), ('kill', 'int')], 'list[int]', ['trees', 'graphs', 'breadth-first-search'], ['1 <= len(pid) <= 50,000; every pid is unique.', 'ppid[i] is the parent of pid[i], with 0 for the root. Return descendants in breadth-first input-child order.'],
        [([[1, 3, 10, 5], [3, 0, 5, 3], 5], 'Killing 5 also kills its child 10, so return 5 then 10.'),
         ([[1, 2, 3], [0, 1, 1], 1], 'The root and both direct children are terminated in breadth-first order.')],
        [[pids, parents, target] for pids, parents, target in (([1], [0], 1), ([1, 2], [0, 1], 2), ([1, 2], [0, 1], 1), ([1, 2, 3], [0, 1, 2], 2), ([1, 2, 3], [0, 1, 2], 1), ([1, 2, 3, 4], [0, 1, 1, 2], 1), ([1, 2, 3, 4], [0, 1, 1, 2], 2), ([10, 20, 30], [0, 10, 10], 10), ([5, 4, 3, 2, 1], [0, 5, 5, 4, 4], 5), ([1, 3, 10, 5], [3, 0, 5, 3], 3), ([7, 8, 9, 10], [0, 7, 7, 9], 7), ([2, 4, 6, 8], [0, 2, 2, 6], 6))], KILL,
        [KILL.replace('queue = [kill]', 'queue = []'), KILL.replace('queue.extend(children.get(process, []))', 'pass')],
        ['Omits the requested process entirely.', 'Returns only the target and direct descendants.'], kill_oracle, random_processes,
        *hints('Parent identifiers define child adjacency lists.', 'Once a process is reached, all of its children must be reached too.', 'Map parent to children, then BFS from kill and append each dequeued process.', 'The traversal visits exactly the rooted subtree of kill; input order of each child list makes output deterministic.'), 'O(n)', 'O(n)', 5),
    583: reviewed_entry('minimum_delete_steps', [('word1', 'str'), ('word2', 'str')], 'int', ['strings', 'dynamic-programming'], ['0 <= len(word1), len(word2) <= 500.', 'Each operation deletes one character from either word.'],
        [(['sea', 'eat'], 'Keep the common subsequence ea; delete s and t for two operations.'),
         (['leetcode', 'etco'], 'The longest shared subsequence has four characters, leaving four deletions.')],
        [[left, right] for left, right in (('', ''), ('a', ''), ('', 'a'), ('a', 'a'), ('a', 'b'), ('ab', 'ba'), ('abc', 'abc'), ('abc', 'def'), ('sea', 'eat'), ('park', 'spake'), ('aaaa', 'aa'), ('abcde', 'ace'))], DELETE,
        [DELETE.replace('previous[col-1] if first == second', '1 + previous[col-1] if first == second'), DELETE.replace('1 + min(previous[col], current[col-1])', 'min(previous[col], current[col-1])')],
        ['Deletes even when matching characters can be retained.', 'Forgets the deletion cost for a mismatch.'], deletion_oracle, random_words,
        *hints('Keeping a common subsequence avoids deleting its characters.', 'Either compute LCS, or directly compute the edit cost for every prefix pair.', 'Use DP: equal chars copy diagonal; otherwise one plus min(delete from either word).', 'The prefix recurrence considers the last operation of an optimal deletion sequence.'), 'O(len(word1) * len(word2))', 'O(len(word2))', 6),
    592: reviewed_entry('fraction_sum', [('expression', 'str')], 'str', ['strings', 'math', 'parsing'], ['expression has 1 to 10 fractions; numerator and denominator are 1 to 10 in magnitude.', 'Terms are joined by + or -; return reduced numerator/denominator.'],
        [(['-1/2+1/2'], 'The fractions cancel, so the reduced result is 0/1.'), (['1/3-1/2'], 'A common denominator gives 2/6-3/6, or -1/6.')],
        [[expression] for expression in ('1/2', '-1/2', '1/2+1/2', '1/3+1/6', '2/3-1/6', '-1/3-1/6', '5/7+3/7', '1/10+1/10+1/10', '3/4-2/3', '10/1-1/2', '1/2-1/2+1/3', '-5/6+1/3')], FRACTION,
        [FRACTION.replace('divisor = gcd(abs(numerator), denominator)', 'divisor = 1'), FRACTION.replace("(-1 if sign == '-' else 1)", '1')],
        ['Never reduces the resulting fraction.', 'Ignores negative signs.'], fraction_oracle, random_fraction,
        *hints('Maintain one running reduced fraction.', 'For a/b plus c/d, use numerator a*d+c*b and denominator b*d.', 'Parse each signed term, combine with the accumulator, then divide both by gcd.', 'Reducing after each addition keeps values small while preserving the exact rational value.'), 'O(number of terms)', 'O(1)', 5),
}
