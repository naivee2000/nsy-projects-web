"""Final reviewed group of workbook batch 112."""

from itertools import combinations

from .import_batch_055 import entry


MOD = 1_000_000_007


def garden_oracle(arguments):
    needed = arguments[0]
    radius = apples = 0
    while apples < needed:
        radius += 1
        apples += 12 * radius * radius
    return 8 * radius


def special_oracle(arguments):
    nums = arguments[0]
    answer = 0
    for mask in range(1, 1 << len(nums)):
        values = [nums[index] for index in range(len(nums)) if mask >> index & 1]
        if 0 in values and 1 in values and 2 in values:
            first_one = values.index(1)
            first_two = values.index(2)
            if (first_one > 0 and first_two > first_one and set(values[:first_one]) == {0}
                    and set(values[first_one:first_two]) == {1} and set(values[first_two:]) == {2}):
                answer += 1
    return answer % MOD


def _parities(lower, upper):
    if lower > upper:
        return set()
    return {lower & 1} if lower == upper else {0, 1}


def virus_oracle(arguments):
    points, required = arguments

    def possible(days):
        for chosen in combinations(points, required):
            low_u = max(x + y - days for x, y in chosen)
            high_u = min(x + y + days for x, y in chosen)
            low_v = max(x - y - days for x, y in chosen)
            high_v = min(x - y + days for x, y in chosen)
            if _parities(low_u, high_u).intersection(_parities(low_v, high_v)):
                return True
        return False

    lower, upper = 0, 200
    while lower < upper:
        middle = (lower + upper) // 2
        if possible(middle):
            upper = middle
        else:
            lower = middle + 1
    return lower


def fancy_oracle(arguments):
    text = arguments[0]
    answer = ""
    for char in text:
        if len(answer) < 2 or answer[-2:] != char * 2:
            answer += char
    return answer


def move_oracle(arguments):
    board, row, column, color = arguments
    other = "W" if color == "B" else "B"
    for row_step, column_step in product_directions():
        r, c = row + row_step, column + column_step
        length = 0
        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == other:
            length += 1
            r += row_step
            c += column_step
        if length and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == color:
            return True
    return False


def product_directions():
    return [(row, column) for row in (-1, 0, 1) for column in (-1, 0, 1) if row or column]


def board_case(move, placements):
    board = [["."] * 8 for _ in range(8)]
    for row, column, color in placements:
        board[row][column] = color
    return [board, move[0], move[1], move[2]]


def random_garden(rng):
    return [rng.randint(1, 10**10)]


def random_special(rng):
    return [[rng.randint(0, 2) for _ in range(rng.randint(1, 15))]]


def random_virus(rng):
    count = rng.randint(2, 8)
    points = rng.sample([[x, y] for x in range(1, 10) for y in range(1, 10)], count)
    return [points, rng.randint(2, count)]


def random_fancy(rng):
    return ["".join(rng.choice("abcde") for _ in range(rng.randint(1, 80)))]


def random_move(rng):
    board = [[rng.choice(".BW") for _ in range(8)] for _ in range(8)]
    row, column = rng.randrange(8), rng.randrange(8)
    board[row][column] = "."
    return [board, row, column, rng.choice("BW")]


GARDEN = '''\
def minimum_garden_perimeter(needed_apples):
    def apples(radius):
        return 2 * radius * (radius + 1) * (2 * radius + 1)
    lower, upper = 0, 1
    while apples(upper) < needed_apples:
        upper *= 2
    while lower < upper:
        middle = (lower + upper) // 2
        if apples(middle) >= needed_apples:
            upper = middle
        else:
            lower = middle + 1
    return 8 * lower
'''

SPECIAL = '''\
def count_special_zero_one_two_subsequences(nums):
    mod = 1_000_000_007
    zeros = ones = twos = 0
    for value in nums:
        if value == 0:
            zeros = (2 * zeros + 1) % mod
        elif value == 1:
            ones = (2 * ones + zeros) % mod
        else:
            twos = (2 * twos + ones) % mod
    return twos
'''

VIRUS = '''\
def minimum_virus_spread_time(points, k):
    transformed = [(x + y, x - y) for x, y in points]

    def possible(days):
        boundaries = {u - days for u, _ in transformed} | {u + days for u, _ in transformed}
        u_candidates = boundaries | {value - 1 for value in boundaries} | {value + 1 for value in boundaries}
        for u in u_candidates:
            intervals = [(v - days, v + days) for center_u, v in transformed if abs(center_u - u) <= days]
            for lower, upper in intervals:
                candidate = lower if (lower & 1) == (u & 1) else lower + 1
                if candidate <= upper and sum(a <= candidate <= b for a, b in intervals) >= k:
                    return True
        return False

    lower, upper = 0, 200
    while lower < upper:
        middle = (lower + upper) // 2
        if possible(middle):
            upper = middle
        else:
            lower = middle + 1
    return lower
'''

FANCY = '''\
def make_fancy_string(s):
    answer = []
    for char in s:
        if len(answer) < 2 or answer[-1] != char or answer[-2] != char:
            answer.append(char)
    return "".join(answer)
'''

MOVE = '''\
def legal_reversi_move(board, r_move, c_move, color):
    other = "W" if color == "B" else "B"
    for row_step in (-1, 0, 1):
        for column_step in (-1, 0, 1):
            if row_step == column_step == 0:
                continue
            row, column = r_move + row_step, c_move + column_step
            opponents = 0
            while 0 <= row < 8 and 0 <= column < 8 and board[row][column] == other:
                opponents += 1
                row += row_step
                column += column_step
            if opponents and 0 <= row < 8 and 0 <= column < 8 and board[row][column] == color:
                return True
    return False
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


V = lambda move, pieces: board_case(move, pieces)


BATCH = {
    1954: entry(
        "minimum_garden_perimeter", [("needed_apples", "int")], "int", ["math", "binary search"],
        ["1 <= needed_apples <= 1000000000000000.", "The square is centered at the origin with corners (r,r), (r,-r), (-r,r), and (-r,-r).",
         "A tree at integer coordinate (x,y) produces abs(x)+abs(y) apples; return the smallest perimeter 8r meeting the target."],
        [([1], "Radius one already supplies twelve apples, so its perimeter eight is minimal."),
         ([13], "Radius one supplies only twelve; radius two is required and has perimeter sixteen.")],
        [[n] for n in [2,11,12,13,60,61,100,168,1000,10000,1000000,10**9,10**12,10**15-1,10**15]],
        GARDEN,
        [GARDEN.replace("return 8 * lower", "return 4 * lower"), GARDEN.replace(">= needed_apples", "> needed_apples")],
        ["Returns a side-length multiple rather than the perimeter of all four sides.", "Uses a strict target comparison and overshoots when the apple count equals the requirement."],
        garden_oracle, random_garden,
        lesson("The total apples inside radius r is 2*r*(r+1)*(2*r+1), which increases monotonically.",
               "Binary-search the smallest integer radius whose closed-form total reaches needed_apples, then multiply the side length 2r by four.",
               "Double an upper radius until feasible; lower-bound search on apples(r)>=target; return 8*r.",
               "Summing each newly added square ring gives 12r^2 and summing rings yields the formula. Monotonicity makes lower-bound binary search return the unique minimum radius."),
        "O(log answer)", "O(1)", 5),
    1955: entry(
        "count_special_zero_one_two_subsequences", [("nums", "list[int]")], "int", ["arrays", "dynamic programming"],
        ["nums has 1 through 100000 values, each 0, 1, or 2.",
         "A special subsequence contains a positive number of zeros, then a positive number of ones, then a positive number of twos.",
         "Different selected index sets count separately; return the count modulo 1000000007."],
        [([[0,1,2,2]], "Choose the zero and one, then either two alone or both twos, giving three subsequences."),
         ([[2,2,0,0]], "No one occurs after the zeros, so no special subsequence exists.")],
        [[a] for a in [[0],[1],[2],[0,1,2],[0,1,2,2],[0,0,1,2],[0,1,1,2],[0,0,1,1,2,2],
                       [2,2,0,0],[0,2,1,2],[1,0,1,2],[0,1,2,0,1,2],[0,0,0,1,2,2,2],
                       [2,0,2,1,1,2,0]]],
        SPECIAL,
        [SPECIAL.replace("2 * zeros + 1", "zeros + 1"), SPECIAL.replace("2 * twos + ones", "twos + ones")],
        ["Fails to count both taking and skipping an additional zero after a valid zero-prefix exists.",
         "Fails to double completed subsequences when another two may be taken or skipped."],
        special_oracle, random_special,
        lesson("Track counts of valid prefixes ending in the zero, one, and two phases.",
               "A matching new value can be skipped or appended, doubling its phase count; it can also start/extend from the preceding phase.",
               "On 0: z=2z+1; on 1: o=2o+z; on 2: t=2t+o, always modulo M.",
               "The two doubled choices partition subsequences by excluding or including the new index, while the added predecessor count represents every legal phase transition exactly once."),
        "O(n)", "O(1)", 8),
    1956: entry(
        "minimum_virus_spread_time", [("points", "list[list[int]]"), ("k", "int")], "int",
        ["geometry", "binary search", "coordinate transforms"],
        ["points contains 2 through 50 unique integer coordinates with each x,y from 1 through 100.", "2 <= k <= len(points).",
         "Each variant spreads one Manhattan-distance step per day; find the first day some integer grid point has at least k variants."],
        [([[[1,1],[6,1]],2], "The two Manhattan diamonds first share an integer grid point after three days."),
         ([[[3,3],[1,2],[9,2]],2], "Variants at (3,3) and (1,2) can both reach (2,2) after two days.")],
        [[p,k] for p,k in [([[1,1],[2,1]],2),([[1,1],[3,1]],2),([[1,1],[6,1]],2),([[1,1],[1,6]],2),
                            ([[1,1],[6,6]],2),([[1,1],[2,2],[3,3]],3),([[1,1],[10,1],[5,5]],2),
                            ([[1,1],[10,10],[1,10],[10,1]],3),([[3,3],[1,2],[9,2]],2),
                            ([[1,1],[100,100]],2),([[1,100],[100,1]],2),([[5,5],[6,5],[5,6],[6,6]],4),
                            ([[1,1],[4,1],[7,1],[10,1]],3),([[2,8],[8,2],[5,5]],3)]],
        VIRUS,
        [VIRUS.replace("sum(a <= candidate <= b for a, b in intervals) >= k", "sum(a < candidate < b for a, b in intervals) >= k"),
         VIRUS.replace("candidate = lower if (lower & 1) == (u & 1) else lower + 1", "candidate = lower")],
        ["Treats each spread diamond as open and misses points reached exactly on day t.",
         "Ignores the parity constraint required for transformed coordinates to map back to an integer grid point."],
        virus_oracle, random_virus,
        lesson("The transform u=x+y, v=x-y turns each Manhattan diamond into an axis-aligned square, with valid grid points requiring u and v to share parity.",
               "Binary-search days. At each square u-boundary, gather covering v-intervals and test same-parity endpoints for overlap by at least k intervals.",
               "Transform centers; feasible(t) checks boundary u values and parity-adjusted interval starts; lower-bound search the first feasible t.",
               "Any k-square intersection contains a boundary coordinate of one participating square, and its v intersection contains a parity-compatible endpoint when an integer point exists. Thus the feasibility test is complete and monotone."),
        "O(log C*n^3)", "O(n)", 8),
    1957: entry(
        "make_fancy_string", [("s", "str")], "str", ["strings", "greedy"],
        ["s has 1 through 100000 lowercase English letters.", "Delete the minimum characters so no three consecutive result characters are equal.",
         "Preserve the relative order of all retained characters."],
        [(["leeetcode"], "Removing one e from the run eee produces leetcode."),
         (["aaabaaaa"], "Keeping at most two characters from each a-run produces aabaa.")],
        [[s] for s in ["a","aa","aaa","aaaa","abc","aabbcc","leeetcode","aaabaaaa","aabaa","zzzzzz",
                       "abbbaccc","mississippi","xxxyyyzzz","abababab"]],
        FANCY,
        [FANCY.replace("len(answer) < 2", "len(answer) < 3"), FANCY.replace("answer[-2] != char", "answer[-2] == char")],
        ["Allows a third equal character before filtering begins.", "Keeps the next character only when the character two positions back is equal, reversing the intended condition."],
        fancy_oracle, random_fancy,
        lesson("Within each equal-character run, keeping its first two characters is both sufficient and maximal.",
               "Scan left to right and append unless the last two retained characters already equal the current one.",
               "If output[-2:]==char+char, skip; otherwise append.",
               "A third run character must be deleted in every valid result, while deleting either of the first two is unnecessary. Applying this independently to each run minimizes deletions."),
        "O(n)", "O(n)", 3),
    1958: entry(
        "legal_reversi_move", [("board", "list[list[str]]"), ("r_move", "int"), ("c_move", "int"), ("color", "str")], "bool",
        ["matrices", "simulation", "directional search"],
        ["board is exactly 8 by 8 and contains '.', 'B', and 'W'.", "The selected row and column are in range and currently contain '.'.",
         "A legal move must form a straight line in one of eight directions with at least one opposite-color piece between the new piece and an existing piece of color."],
        [(V((3,4,"B"),[(3,1,"B"),(3,2,"W"),(3,3,"W")]), "Placing black at (3,4) brackets two white pieces horizontally with black at (3,1)."),
         (V((4,4,"W"),[(1,1,"W"),(2,2,"B"),(3,3,"B")]), "Placing white at (4,4) brackets two black pieces diagonally with white at (1,1).")],
        [V(move,pieces) for move,pieces in [
            ((0,0,"B"),[]),((0,0,"B"),[(0,1,"B")]),((0,0,"B"),[(0,1,"W"),(0,2,"B")]),
            ((0,7,"W"),[(1,7,"B"),(2,7,"W")]),((7,0,"B"),[(6,1,"W"),(5,2,"B")]),
            ((7,7,"W"),[(6,6,"B"),(5,5,"B"),(4,4,"W")]),((3,3,"B"),[(2,3,"W"),(1,3,"B")]),
            ((3,3,"W"),[(4,3,"B"),(5,3,"W")]),((3,3,"B"),[(3,2,"W"),(3,1,"W")]),
            ((3,3,"B"),[(2,2,"W"),(1,1,"W")]),((4,4,"W"),[(3,5,"B"),(2,6,"W")]),
            ((4,4,"B"),[(5,3,"W"),(6,2,"W"),(7,1,"B")]),((4,4,"B"),[(4,5,"W"),(4,6,"B"),(3,4,"W")]),
            ((1,1,"W"),[(2,2,"B"),(3,3,"."),(4,4,"W")])]],
        MOVE,
        [MOVE.replace("for row_step in (-1, 0, 1):", "for row_step in (0,):"),
         MOVE.replace("if opponents and 0 <= row", "if 0 <= row")],
        ["Checks horizontal directions only and misses legal vertical or diagonal lines.", "Allows an adjacent same-color piece without at least one bracketed opponent."],
        move_oracle, random_move,
        lesson("A move is legal if any one of the eight rays starts with one or more opponent pieces and ends at your color before leaving the board or reaching a gap.",
               "Walk each direction from the move, count consecutive opponent cells, then check for an in-bounds same-color endpoint.",
               "For each nonzero (dr,dc): advance through other color; accept when count>0 and the next cell equals color.",
               "The scan tests every possible straight line through the new piece. Requiring an opponent run and same-color endpoint is exactly the good-line definition."),
        "O(1)", "O(1)", 5),
}
