"""Multiword grid recursion, skyline sweep, square DP, and planar union area."""
from .import_batch_003 import entry


def words_oracle(args):
    board, words = args
    rows, columns = len(board), len(board[0])
    letters = [char for row in board for char in row]
    adjacent = []
    for cell in range(len(letters)):
        r, c = divmod(cell, columns)
        adjacent.append([nr * columns + nc for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                         if 0 <= nr < rows and 0 <= nc < columns])
    answer = []
    # Enumerate reachable (endpoint, used-cell mask) states for each word,
    # independently of the reference's shared trie and recursive board marking.
    for word in words:
        states = {(cell, 1 << cell) for cell, char in enumerate(letters) if char == word[0]}
        for char in word[1:]:
            states = {(nxt, mask | (1 << nxt)) for cell, mask in states for nxt in adjacent[cell]
                      if not mask & (1 << nxt) and letters[nxt] == char}
            if not states:
                break
        if states:
            answer.append(word)
    return answer


def skyline_oracle(args):
    buildings = args[0]
    coordinates = sorted({x for left, right, _ in buildings for x in (left, right)})
    answer = []
    for x in coordinates:
        height = max((height for left, right, height in buildings if left <= x < right), default=0)
        if not answer or answer[-1][1] != height:
            answer.append([x, height])
    return answer


def square_oracle(args):
    matrix = args[0]
    rows, columns = len(matrix), len(matrix[0])
    best = 0
    for r in range(rows):
        for c in range(columns):
            for side in range(1, min(rows - r, columns - c) + 1):
                if all(matrix[i][j] == "1" for i in range(r, r + side) for j in range(c, c + side)):
                    best = max(best, side * side)
    return best


def area_oracle(args):
    rectangles = [args[:4], args[4:]]
    xs = sorted({x for left, _, right, _ in rectangles for x in (left, right)})
    ys = sorted({y for _, bottom, _, top in rectangles for y in (bottom, top)})
    area = 0
    # Coordinate cells are either wholly covered or wholly uncovered. Integer
    # doubled midpoints avoid floating point and work for degenerate rectangles.
    for left, right in zip(xs, xs[1:]):
        for bottom, top in zip(ys, ys[1:]):
            x2, y2 = left + right, bottom + top
            if any(2 * a <= x2 < 2 * c and 2 * b <= y2 < 2 * d for a, b, c, d in rectangles):
                area += (right - left) * (top - bottom)
    return area


def random_words(rng):
    rows, columns = rng.randint(1, 4), rng.randint(1, 4)
    board = [[rng.choice("abc") for _ in range(columns)] for _ in range(rows)]
    words = {"".join(rng.choice("abcd") for _ in range(rng.randint(1, 6))) for _ in range(rng.randint(1, 12))}
    # Include a legal walk often, so generated checks do not mostly test misses.
    r, c = rng.randrange(rows), rng.randrange(columns)
    used, chars = {(r, c)}, [board[r][c]]
    for _ in range(rng.randrange(5)):
        choices = [(nr, nc) for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                   if 0 <= nr < rows and 0 <= nc < columns and (nr, nc) not in used]
        if not choices:
            break
        r, c = rng.choice(choices)
        used.add((r, c))
        chars.append(board[r][c])
    words.add("".join(chars))
    return [board, sorted(words)]


def random_skyline(rng):
    buildings = []
    for _ in range(rng.randint(1, 14)):
        left = rng.randrange(20)
        buildings.append([left, rng.randint(left + 1, 24), rng.randint(1, 20)])
    return [sorted(buildings, key=lambda building: building[0])]


def random_square(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    return [[[rng.choice("01") for _ in range(columns)] for _ in range(rows)]]


def random_area(rng):
    args = []
    for _ in range(2):
        xs, ys = sorted(rng.randint(-10, 10) for _ in range(2)), sorted(rng.randint(-10, 10) for _ in range(2))
        args.extend((xs[0], ys[0], xs[1], ys[1]))
    return args


WORDS = '''\
def find_board_words(board, words):
    from collections import Counter
    available = Counter(char for row in board for char in row)
    trie = {}
    for word in words:
        if any(count > available[char] for char, count in Counter(word).items()):
            continue
        node = trie
        for char in word:
            node = node.setdefault(char, {})
        node["$"] = word
    result = []
    rows, columns = len(board), len(board[0])
    def search(r, c, parent):
        char = board[r][c]
        node = parent[char]
        word = node.pop("$", None)
        if word is not None:
            result.append(word)
        board[r][c] = "#"
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < columns and board[nr][nc] in node:
                search(nr, nc, node)
        board[r][c] = char
        if not node:
            del parent[char]
    for r in range(rows):
        for c in range(columns):
            if board[r][c] in trie:
                search(r, c, trie)
    return result
'''
SKYLINE = '''\
def building_skyline(buildings):
    from heapq import heappush, heappop
    coordinates = sorted({x for left, right, height in buildings for x in (left, right)})
    active, result, index = [], [], 0
    for x in coordinates:
        while index < len(buildings) and buildings[index][0] <= x:
            left, right, height = buildings[index]
            heappush(active, (-height, right))
            index += 1
        while active and active[0][1] <= x:
            heappop(active)
        height = -active[0][0] if active else 0
        if not result or result[-1][1] != height:
            result.append([x, height])
    return result
'''
SQUARE = '''\
def maximal_square_area(matrix):
    dp = [0] * (len(matrix[0]) + 1)
    best = 0
    for row in matrix:
        diagonal = 0
        for column, char in enumerate(row, 1):
            above = dp[column]
            if char == "1":
                dp[column] = 1 + min(above, dp[column - 1], diagonal)
                best = max(best, dp[column])
            else:
                dp[column] = 0
            diagonal = above
    return best * best
'''
AREA = '''\
def rectangle_union_area(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    first = (ax2 - ax1) * (ay2 - ay1)
    second = (bx2 - bx1) * (by2 - by1)
    width = max(0, min(ax2, bx2) - max(ax1, bx1))
    height = max(0, min(ay2, by2) - max(ay1, by1))
    return first + second - width * height
'''


def large_dictionary():
    # Exactly 30,000 unique lowercase words. The b-prefixed words cannot occur
    # on the all-a stress board, while all ten a-prefix words must be found once.
    return ["a" * length for length in range(1, 11)] + [
        "b" + "".join(chr(97 + number // 26**place % 26) for place in (3, 2, 1, 0))
        for number in range(29990)]


BATCH = {
    212: entry("find_board_words", [("board", "list[list[str]]"), ("words", "list[str]")], "list[str]", ["matrices", "recursion", "backtracking", "tries"],
        ["The board has 1–12 rows and columns of lowercase English letters. words contains 1–30000 UNIQUE lowercase strings, each 1–10 letters long.", "A word follows horizontal/vertical neighbors; a cell cannot be reused within that word. Different words may reuse cells. Return each found dictionary word once, in any order."],
        [([[["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]], ["oath", "pea", "eat", "rain"]], "The board contains oath and eat along orthogonal paths; pea and rain have no valid paths. Either output order is accepted."),
         ([[["a", "b"], ["c", "d"]], ["abcb"]], "A matching route cannot reuse a cell, and the required second b cannot be reached legally; no word is returned.")],
        [[board, words] for board, words in (([["a"]], ["a", "b", "aa"]), ([["a", "b"]], ["a", "ab", "ba", "aba"]),
            ([["a", "b"], ["c", "d"]], ["ad", "bc"]), ([["a", "a"], ["a", "a"]], ["a", "aa", "aaa", "aaaa", "aaaaa"]),
            ([["a", "b"], ["b", "a"]], ["abba", "abab", "aba"]), ([["a"], ["b"], ["c"]], ["abc", "cba", "ac"]),
            ([["c", "a", "t"]], ["cat", "at", "ta", "tac"]), ([["x", "y"], ["z", "x"]], ["xyz", "xzx", "xyx"]),
            ([["a", "b", "c"], ["d", "e", "f"]], ["abef", "adef", "fed", "ace"]), ([["z"]], ["zz", "a"]),
            ([["a", "b", "a"]], ["aba", "ab", "ba"]), ([["a", "b", "x", "a"]], ["aba", "ab", "xba"]))],
        WORDS, [WORDS.replace('        board[r][c] = "#"', '        # Incorrectly leave the current cell reusable.'),
                WORDS.replace("((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))", "((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1), (r - 1, c - 1), (r + 1, c + 1), (r - 1, c + 1), (r + 1, c - 1))")],
        ["Reuses a cell within a word because the current path is not marked.", "Allows diagonal neighbors even though only horizontal and vertical movement is permitted."], words_oracle, random_words,
        ["Many dictionary words share prefixes, so their searches can share work too.", "Store words in a trie and explore board paths only while they match a trie prefix.", "Mark a cell during recursive exploration, follow matching orthogonal neighbors, restore the cell on return, and remove an emitted word marker to avoid duplicates.", "Keep longer continuations after finding a prefix word. Delete a trie branch only when it contains no remaining word or child."],
        "The trie shares prefix exploration across the dictionary. A board-frequency precheck removes impossible words before insertion. Recursive DFS marks only the current path, restores every cell, and emits each terminal word once. Empty trie branches can be removed after exploration because they contain no unfound words. Recursion depth is bounded by the maximum word length, ten, even on a 12×12 board. The independent oracle performs per-word breadth-by-character state expansion using explicit used-cell bitmasks, with no trie or board mutation. This returns a set of dictionary matches rather than the existing single-word Boolean.",
        "O(S + rows×columns×4×3^(L-1)) worst case, S is total dictionary length and L≤10", "O(S + L), excluding returned words", difficulty=8,
        stress=[([[["a"] * 12 for _ in range(12)], large_dictionary()], ["a" * length for length in range(1, 11)])]),
    218: entry("building_skyline", [("buildings", "list[list[int]]")], "list[list[int]]", ["geometry", "sweep-line", "heaps"],
        ["1–10000 buildings [left,right,height], sorted by nondecreasing left. 0 ≤ left < right ≤ 2^31-1 and 1 ≤ height ≤ 2^31-1. Buildings may coincide or overlap.", "Return increasing-x key points [x,current_max_height], including zero-height gaps and the final drop to zero. Combine all events at the same x and omit consecutive points with the same height."],
        [([[[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]], "The highest active building changes at 2,3,7,12,15,20,24. The point [12,0] records the ground gap before the next building at 15."),
         ([[[0, 2, 3], [2, 5, 3]]], "Touching buildings of equal height form one segment: [0,3] then [5,0], with no redundant point at x=2.")],
        [[buildings] for buildings in ([[0, 1, 1]], [[1, 3, 2]], [[0, 2, 2], [1, 3, 3]], [[0, 4, 5], [1, 2, 2]],
            [[0, 2, 3], [0, 3, 4]], [[0, 3, 4], [0, 2, 3]], [[0, 2, 3], [2, 4, 4]], [[0, 2, 4], [2, 4, 3]],
            [[0, 1, 2], [3, 4, 2]], [[0, 2, 3], [0, 2, 3]], [[0, 4, 2], [1, 3, 3], [2, 4, 4]], [[0, 2147483647, 2147483647]])],
        SKYLINE, [SKYLINE.replace("active[0][1] <= x", "active[0][1] < x"), SKYLINE.replace("if not result or result[-1][1] != height:", "if True:")],
        ["Keeps a building active at its right endpoint and delays the skyline drop.", "Emits every endpoint, including redundant points where the visible height does not change."], skyline_oracle, random_skyline,
        ["The skyline changes only at building endpoints, and the visible height is the maximum currently active height.", "Sweep endpoints in increasing x while a max-heap tracks active buildings and their right edges.", "At each x insert all started buildings, remove expired heap tops, and emit the resulting height only if it differs from the previous height.", "Process every start/end at the same coordinate before emitting a point; adjacent equal-height segments must merge."],
        "A heap ordered by negative height exposes the tallest active building. Expired shorter buildings may remain buried until they reach the top; removing expired tops is sufficient for the current maximum. All starts and ends at the same x are resolved together, and unchanged heights are omitted. Each building enters and leaves at most once, while endpoint sorting costs O(n log n). The independent oracle scans all buildings at every distinct endpoint, directly measuring the geometric upper envelope instead of maintaining an active heap.",
        "O(n log n)", "O(n)", difficulty=8,
        stress=[([[[i, i + 2, 1] for i in range(10000)]], [[0, 1], [10001, 0]]),
                ([[[i, 20000 - i, i + 1] for i in range(10000)]], [[i, i + 1] for i in range(10000)] + [[20000 - i, i] for i in range(9999, -1, -1)])]),
    221: entry("maximal_square_area", [("matrix", "list[list[str]]")], "int", ["matrices", "dynamic-programming"],
        ["1–300 rows and columns. Every entry is the STRING '0' or '1'; rows have equal length.", "Return the AREA of the largest axis-aligned square made entirely of ones. A rectangle with unequal sides does not qualify; if there are no ones, return 0."],
        [([[["1", "0", "1", "0", "0"], ["1", "0", "1", "1", "1"], ["1", "1", "1", "1", "1"], ["1", "0", "0", "1", "0"]]], "The largest all-one square has side length 2, so its area is 4—not 2, and not the area of a larger nonsquare rectangle."),
         ([[["0", "1"], ["1", "0"]]], "Each one is an isolated one-cell square. The 2×2 region contains zeroes, so the maximum area is 1.")],
        [[matrix] for matrix in ([["0"]], [["1"]], [["1", "1"]], [["1"], ["1"]], [["1", "1"], ["1", "1"]],
            [["0", "1"], ["1", "1"]], [["1", "0"], ["1", "1"]], [["1", "1"], ["0", "1"]],
            [["1"] * 3 for _ in range(3)], [["0"] * 3 for _ in range(2)], [["1"] * 4 for _ in range(2)],
            [["1", "1", "1"], ["1", "0", "1"], ["1", "1", "1"]])],
        SQUARE, [SQUARE.replace("return best * best", "return best"), SQUARE.replace("min(above, dp[column - 1], diagonal)", "min(above, dp[column - 1])")],
        ["Returns side length instead of the required area.", "Ignores the upper-left diagonal and allows a zero inside a supposedly all-one square."], square_oracle, random_square,
        ["A square ending at a cell depends on smaller squares ending above, left, and diagonally above-left.", "At a one cell, the largest ending side is one plus the minimum of those three sizes.", "Reuse one DP row and save the old above value as the next diagonal; reset the current size on zero cells, then square the largest side.", "Track the diagonal before overwriting its previous-row value. Return area rather than side length."],
        "A new bottom-right one can extend a square only as far as all three neighboring sub-squares support it. The minimum of their side lengths enforces both borders and the entire interior. A rolling row stores above values while the left value is already updated; a separate variable preserves the diagonal. The independent oracle enumerates square positions and side lengths and directly checks every contained cell. This differs from the existing maximal rectangle problem because both dimensions must be equal.",
        "O(rows×columns)", "O(columns)", difficulty=5,
        stress=[([[["1"] * 300 for _ in range(300)]], 90000),
                ([[[str((r + c) % 2) for c in range(300)] for r in range(300)]], 1)]),
    223: entry("rectangle_union_area", [(name, "int") for name in ("ax1", "ay1", "ax2", "ay2", "bx1", "by1", "bx2", "by2")], "int", ["geometry", "math"],
        ["All coordinates are integers from -10000 to 10000; ax1≤ax2, ay1≤ay2, bx1≤bx2, by1≤by2. Zero-width/height rectangles are allowed.", "Rectangles are axis-aligned, given by bottom-left and top-right corners. Return their union area, counting overlap once; touching only along an edge or corner adds no overlap area."],
        [([-3, 0, 3, 4, 0, -1, 9, 2], "The individual areas are 24 and 27. Their shared 3×2 region has area 6, so the union is 24+27−6=45."),
         ([-2, -2, 2, 2, -2, -2, 2, 2], "The rectangles coincide completely; count the shared 4×4 region only once, giving 16.")],
        [list(values) for values in ((0, 0, 1, 1, 0, 0, 1, 1), (0, 0, 2, 2, 1, 1, 3, 3),
            (0, 0, 4, 4, 1, 1, 2, 2), (0, 0, 1, 1, 2, 0, 3, 1), (0, 0, 1, 1, 0, 2, 1, 3),
            (0, 0, 1, 1, 2, 2, 3, 3), (0, 0, 1, 1, 1, 0, 2, 1), (0, 0, 1, 1, 1, 1, 2, 2),
            (0, 0, 0, 2, -1, -1, 1, 1), (0, 0, 0, 0, 1, 1, 2, 2),
            (-5, -5, -2, -2, -4, -4, -1, -1), (0, 0, 0, 5, 1, 1, 4, 1))],
        AREA, [AREA.replace(" - width * height", ""), AREA.replace("max(0, min(ax2, bx2) - max(ax1, bx1))", "min(ax2, bx2) - max(ax1, bx1)").replace("max(0, min(ay2, by2) - max(ay1, by1))", "min(ay2, by2) - max(ay1, by1)")],
        ["Adds both areas without subtracting their shared region.", "Multiplies negative overlap widths/heights for disjoint rectangles, producing fictitious overlap."], area_oracle, random_area,
        ["Adding the individual areas counts the shared region twice.", "Intersect the x intervals and the y intervals separately to find overlap dimensions.", "Clamp both overlap dimensions at zero, multiply them, and subtract that overlap from the two individual areas.", "Negative coordinates do not change the formula; degenerate rectangles and touching edges have zero overlap area."],
        "Inclusion-exclusion counts each point once: area(A)+area(B)−area(A∩B). The intersection of axis-aligned rectangles is an axis-aligned rectangle only when both overlap dimensions are positive, so clamp each dimension independently before multiplying. The independent oracle partitions the plane using all input x/y boundaries and sums coordinate cells covered by either rectangle; it does not reuse the overlap formula. All arithmetic remains integral, including the full-domain 400000000 area.",
        "O(1)", "O(1)", difficulty=5,
        stress=[([-10000, -10000, 0, 10000, 0, -10000, 10000, 10000], 400000000)]),
}
BATCH[212]["comparator"] = "unordered"
BATCH[212]["prerequisites"] = ["matrices", "recursion", "backtracking"]
BATCH[218]["prerequisites"] = ["heaps", "intervals"]
