"""Sudoku validation, number grammar, exact justification, and matrix rectangles."""
from itertools import combinations
import re

from .import_batch_003 import entry


def sudoku_oracle(args):
    filled = [(r, c, digit) for r, row in enumerate(args[0]) for c, digit in enumerate(row) if digit != "."]
    return not any(a == b and (r == s or c == d or (r // 3, c // 3) == (s // 3, d // 3))
                   for (r, c, a), (s, d, b) in combinations(filled, 2))


def number_oracle(args):
    return re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", args[0]) is not None


def justification_oracle(args):
    words, width = args
    # Exhaustively enumerate break placements, then maximize successive line
    # word counts lexicographically. This independently enforces greedy packing.
    best, best_key = None, None
    for mask in range(1 << (len(words) - 1)):
        groups, start = [], 0
        for end in range(1, len(words) + 1):
            if end == len(words) or mask & (1 << (end - 1)):
                group = words[start:end]
                if sum(map(len, group)) + len(group) - 1 > width:
                    break
                groups.append(group)
                start = end
        else:
            key = tuple(map(len, groups))
            if best_key is None or key > best_key:
                best, best_key = groups, key
    output = []
    for index, group in enumerate(best):
        if index == len(best) - 1 or len(group) == 1:
            output.append(" ".join(group).ljust(width))
            continue
        # Round-robin insertion into gaps, rather than quotient/remainder math.
        gaps = [""] * (len(group) - 1)
        for space in range(width - sum(map(len, group))):
            gaps[space % len(gaps)] += " "
        output.append("".join(word + gap for word, gap in zip(group[:-1], gaps)) + group[-1])
    return output


def rectangle_oracle(args):
    matrix = args[0]
    rows, columns = len(matrix), len(matrix[0])
    zeros = [[0] * (columns + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(columns):
            zeros[r+1][c+1] = zeros[r][c+1] + zeros[r+1][c] - zeros[r][c] + (matrix[r][c] == "0")
    best = 0
    for top in range(rows):
        for bottom in range(top + 1, rows + 1):
            for left in range(columns):
                for right in range(left + 1, columns + 1):
                    count = zeros[bottom][right] - zeros[top][right] - zeros[bottom][left] + zeros[top][left]
                    if count == 0:
                        best = max(best, (bottom - top) * (right - left))
    return best


def board_with(*cells):
    board = [["."] * 9 for _ in range(9)]
    for row, column, digit in cells:
        board[row][column] = digit
    return board


SOLVED = [[str((r * 3 + r // 3 + c) % 9 + 1) for c in range(9)] for r in range(9)]


def random_sudoku(rng):
    if rng.random() < .5:
        digits = rng.sample(list("123456789"), 9)
        board = [[digits[int(value) - 1] if rng.random() < .65 else "." for value in row] for row in SOLVED]
    else:
        board = [[rng.choice("123456789") if rng.random() < .3 else "." for _ in range(9)] for _ in range(9)]
    return [board]


def random_number(rng):
    if rng.random() < .5:
        return ["".join(rng.choice("0123456789eE.+-abcXYZ") for _ in range(rng.randint(1, 20))) ]
    digits = lambda: "".join(rng.choice("0123456789") for _ in range(rng.randint(1, 4)))
    left, right = digits(), digits()
    mantissa = rng.choice((left, left + ".", "." + right, left + "." + right))
    result = rng.choice(("", "+", "-")) + mantissa
    if rng.random() < .6:
        result += rng.choice("eE") + rng.choice(("", "+", "-")) + digits()
    return [result]


def random_justification(rng):
    width = rng.randint(1, 12)
    words = ["".join(rng.choice("aAbB!?.") for _ in range(rng.randint(1, min(width, 6))))
             for _ in range(rng.randint(1, 9))]
    return [words, width]


def random_rectangle(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    probability = rng.choice((.2, .5, .8))
    return [[["1" if rng.random() < probability else "0" for _ in range(columns)] for _ in range(rows)]]


SUDOKU = '''\
def valid_sudoku(board):
    rows = [set() for _ in range(9)]
    columns = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for row in range(9):
        for column in range(9):
            digit = board[row][column]
            if digit == ".":
                continue
            box = row // 3 * 3 + column // 3
            if digit in rows[row] or digit in columns[column] or digit in boxes[box]:
                return False
            rows[row].add(digit)
            columns[column].add(digit)
            boxes[box].add(digit)
    return True
'''
NUMBER = '''\
def valid_number(s):
    digit_seen = dot_seen = exponent_seen = False
    for index, char in enumerate(s):
        if "0" <= char <= "9":
            digit_seen = True
        elif char in "+-":
            if index != 0 and s[index - 1] not in "eE":
                return False
        elif char == ".":
            if dot_seen or exponent_seen:
                return False
            dot_seen = True
        elif char in "eE":
            if exponent_seen or not digit_seen:
                return False
            exponent_seen = True
            digit_seen = False
        else:
            return False
    return digit_seen
'''
FLOAT_WRONG = '''\
def valid_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
'''
JUSTIFY = '''\
def justify_text(words, maxWidth):
    output = []
    start = 0
    while start < len(words):
        end = start
        letters = 0
        while end < len(words) and letters + len(words[end]) + end - start <= maxWidth:
            letters += len(words[end])
            end += 1
        count = end - start
        if end == len(words) or count == 1:
            line = " ".join(words[start:end]).ljust(maxWidth)
        else:
            spaces, extra = divmod(maxWidth - letters, count - 1)
            parts = []
            for offset in range(count - 1):
                parts.append(words[start + offset] + " " * (spaces + (offset < extra)))
            line = "".join(parts) + words[end - 1]
        output.append(line)
        start = end
    return output
'''
RECTANGLE = '''\
def maximal_rectangle(matrix):
    columns = len(matrix[0])
    heights = [0] * (columns + 1)
    best = 0
    for row in matrix:
        for column in range(columns):
            heights[column] = heights[column] + 1 if row[column] == "1" else 0
        stack = [-1]
        for column in range(columns + 1):
            while stack[-1] != -1 and heights[stack[-1]] > heights[column]:
                height = heights[stack.pop()]
                best = max(best, height * (column - stack[-1] - 1))
            stack.append(column)
    return best
'''
ROW_ONLY = '''\
def maximal_rectangle(matrix):
    best = 0
    for row in matrix:
        run = 0
        for value in row:
            run = run + 1 if value == "1" else 0
            best = max(best, run)
    return best
'''
TOTAL_ONES = '''\
def maximal_rectangle(matrix):
    return sum(value == "1" for row in matrix for value in row)
'''


SUDOKU_SAMPLE = [list(row) for row in ("53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79")]
SUDOKU_INVALID = [row[:] for row in SUDOKU_SAMPLE]
SUDOKU_INVALID[0][0] = "8"
UNSOLVABLE = board_with(*[(0, index, str(index + 1)) for index in range(8)], (1, 8, "9"))
JUSTIFY_SAMPLE = [["This", "is", "an", "example", "of", "text", "justification."], 16]


def grid(*rows):
    return [list(row) for row in rows]


BATCH = {
    36: entry("valid_sudoku", [("board", "list[list[str]]")], "bool", ["matrices", "hash-maps"],
        ["The board is exactly 9×9. Each cell is '.', meaning empty, or a digit character from '1' through '9'.",
         "Validate only the filled cells: no repeated digit in any row, column, or aligned 3×3 box. Empty cells may repeat freely. Do not fill the board or require that a completion exists."],
        [([SUDOKU_SAMPLE], "Every filled digit is unique within its row, column and 3×3 box. Empty dots are ignored, so this partial board is valid."),
         ([SUDOKU_INVALID], "Changing the top-left 5 to 8 repeats 8 in the top-left box and first column, so the board is invalid.")],
        [[board] for board in (board_with(), board_with((0, 0, "1")), board_with((0, 0, "1"), (0, 4, "1")),
                               board_with((0, 0, "2"), (4, 0, "2")), board_with((0, 0, "3"), (1, 1, "3")),
                               board_with((0, 0, "4"), (4, 4, "4")), SOLVED, UNSOLVABLE,
                               board_with((7, 7, "5"), (8, 8, "5")), board_with((8, 0, "6"), (8, 8, "6")),
                               board_with((0, 8, "7"), (8, 8, "7")), board_with((0, 0, "9"), (3, 3, "9"), (6, 6, "9")))],
        SUDOKU, [SUDOKU.replace(" or digit in boxes[box]", ""), SUDOKU.replace('if digit == ".":', 'if False:')],
        ["Checks rows and columns but misses repeats confined to a 3×3 box.", "Treats repeated empty dots as repeated filled values."],
        sudoku_oracle, random_sudoku,
        ["This checks consistency of filled cells, not whether you can solve the puzzle.",
         "Track seen digits independently for each row, each column, and each 3×3 box.",
         "Skip dots. Compute box=(row//3)*3+column//3, reject an already-seen digit in any of its three sets, then add it to all three.",
         "Two matching digits can share a box without sharing a row or column; all three checks are necessary."],
        "Scan the 81 cells and maintain three groups of nine sets. A duplicate in any relevant unit violates Sudoku's rules; otherwise the partial board is valid, even if a blank cell cannot later be filled. A deliberate valid-but-unsolvable fixture guards that distinction. The independent oracle compares pairs of filled cells and checks whether matching digits share a row, column, or box instead of maintaining unit sets. Time and storage are constant for the fixed 9×9 domain.",
        "O(81), constant for a 9×9 board", "O(81), constant for a 9×9 board", difficulty=5),
    65: entry("valid_number", [("s", "str")], "bool", ["strings", "state-machines"],
        ["1–20 characters, each an English letter, decimal digit, '+', '-', or '.'. Whitespace is not part of the input domain.",
         "A mantissa is an optionally signed integer or decimal with at least one digit; a decimal may omit digits on one side of its dot, but not both.",
         "An optional e/E exponent must be an optionally signed integer with at least one digit and no dot. Special floating-point spellings such as NaN and Infinity are not valid numbers."],
        [(["0"], "A single digit is an integer, and no exponent is required."),
         (["99e2.5"], "The mantissa 99 is valid, but an exponent cannot contain a decimal point, so this string is invalid.")],
        [[value] for value in (".", "e", "+", "-.9", "4.", "2e10", "-90E3", "1e", "--6", "NaN", "Infinity", "+6e-1")],
        NUMBER, [FLOAT_WRONG, NUMBER.replace("if dot_seen or exponent_seen:",
                 'if dot_seen or exponent_seen or index == 0 or index == len(s) - 1 or not ("0" <= s[index - 1] <= "9"):')],
        ["Delegates to Python float parsing, which accepts forbidden NaN and Infinity spellings.",
         "Incorrectly requires digits on both sides of every decimal point."], number_oracle, random_number,
        ["Separate the mantissa rules from the stricter exponent rules.", "Scan once while tracking whether a digit, dot, and exponent marker have appeared.",
         "Allow a sign only at the beginning or immediately after e/E. At e/E require a mantissa digit and reset the digit flag so exponent digits become mandatory.",
         "After an exponent, reject dots and another exponent. Accept only if the current digit flag is true at the end."],
        "Use state flags to validate syntax without converting the number or risking overflow. A dot is legal at most once and only before the exponent. The exponent marker requires an existing digit and clears that flag to enforce a nonempty exponent. A sign is permitted only at the beginning or just after the exponent marker. The independent oracle uses an anchored regular-expression grammar; regression tests also enumerate short strings against a separate grammar decomposition. Numeric magnitude is irrelevant: an exponent may be too large for machine floats while its spelling is valid.",
        "O(n)", "O(1)", difficulty=8,
        stress=[(["9" * 20], True), (["1e" + "9" * 18], True)]),
    68: entry("justify_text", [("words", "list[str]"), ("maxWidth", "int")], "list[str]", ["strings", "greedy"],
        ["1–300 words; each has 1–20 non-space English letters or symbols. maxWidth is 1–100 and is at least every word's length.",
         "Pack as many whole words as fit on each line, keeping their original order. Every output line must be exactly maxWidth characters, including spaces.",
         "On nonfinal lines distribute spaces evenly between words, placing leftover spaces in the leftmost gaps. Single-word lines and the final line use single spaces between words, then trailing spaces."],
        [(JUSTIFY_SAMPLE, "At width 16 the first line has four spaces in each gap: 'This    is    an'. The next line is 'example  of text', with the extra space in the left gap; 'justification.  ' ends with two spaces."),
         ([["What", "must", "be", "acknowledgment", "shall", "be"], 16], "The first line uses three spaces in each gap; the one-word second line gets two trailing spaces. The final 'shall be' uses one internal space and eight trailing spaces.")],
        [[words, width] for words, width in ((["a"], 1), (["a"], 5), (["a", "b"], 1), (["a", "b"], 3),
                                            (["a", "b", "c", "dddd"], 6), (["aa", "b", "c", "dddd"], 7),
                                            (["abc", "de", "f"], 3), (["a", "b", "c"], 5),
                                            (["abcd", "e", "f"], 4), (["A!", "B?", "C."], 6),
                                            (["ab", "cd", "ef", "g"], 6), (["x", "yy", "zzz", "w"], 5))],
        JUSTIFY, [JUSTIFY.replace("if end == len(words) or count == 1:", "if count == 1:"),
                  JUSTIFY.replace("(offset < extra)", "(offset >= count - 1 - extra)")],
        ["Fully justifies the final multiword line instead of left-justifying it.",
         "Places leftover spaces in the rightmost gaps rather than the leftmost gaps."], justification_oracle, random_justification,
        ["Choose line breaks before deciding how many spaces each gap gets.", "Greedily take the longest word prefix that fits with one required space per gap.",
         "For a nonfinal line with k>1 words, divmod(width-letter_count, k-1) gives the base gap and number of leftmost gaps receiving one extra space.",
         "Treat the last line and single-word lines separately: join with single spaces and pad only on the right. Spaces are part of the exact answer."],
        "First scan to the maximal fitting word group, counting letters and the minimum gaps. On ordinary multiword lines, divide the available space budget across the gaps and allocate the remainder from left to right. Last lines and single-word lines are left-justified. The reference is linear in the total emitted characters plus input traversal; output padding must be counted in that cost. The independent oracle enumerates every legal break pattern on small inputs, chooses the lexicographically greatest sequence of per-line word counts, and inserts spaces round-robin. The workbook example lost repeated spaces; its original text and explicit correction are retained in the validation report.",
        "O(total input characters + output characters)", "O(maxWidth) auxiliary, plus output", difficulty=8,
        stress=[([["x" * 20] * 300, 20], ["x" * 20] * 300)]),
    85: entry("maximal_rectangle", [("matrix", "list[list[str]]")], "int", ["matrices", "stacks", "dynamic-programming"],
        ["A rectangular matrix with 1–200 rows and 1–200 columns contains only the characters '0' and '1'.",
         "Return the area of the largest axis-aligned rectangle of contiguous cells containing only '1'. It may be nonsquare. Return 0 when there are no ones; do not rearrange rows or columns."],
        [([grid("10100", "10111", "11111", "10010")], "Rows 2–3 and columns 3–5 (one-based) form an all-one 2×3 rectangle, giving area 6."),
         ([grid("111", "111")], "The entire 2×3 matrix is a rectangle of ones, so its area is 6; restricting the answer to squares would give only 4.")],
        [[matrix] for matrix in (grid("0"), grid("1"), grid("000"), grid("1111"), grid("1", "1", "1"),
                                grid("10", "01"), grid("101", "101"), grid("111", "010"), grid("010", "111"),
                                grid("1100", "1110", "1111"), grid("111", "000", "111"), grid("0110", "1111", "0110"))],
        RECTANGLE, [ROW_ONLY, TOTAL_ONES],
        ["Considers only rectangles of height one and misses rectangles spanning rows.",
         "Counts every one without requiring the cells to form a single rectangle."], rectangle_oracle, random_rectangle,
        ["For each bottom row, record how many consecutive ones end there in every column.",
         "Each resulting height array is a histogram; find its largest rectangle with a monotonic stack.",
         "Reset heights at zeros. Pop taller bars when a shorter bar arrives, calculating popped_height × distance_between_smaller_boundaries; append a zero-height sentinel to flush the stack.",
         "Keep row-to-row heights, but reset the index stack for every row. Every matrix rectangle has some bottom row and is represented by that row's histogram."],
        "Accumulate consecutive-one column heights as rows are scanned. A monotonic stack calculates the maximum histogram area for each bottom row; each bar is pushed and popped at most once per row. The largest area across all rows is the answer. This combines a two-dimensional matrix with the existing histogram pattern, rather than duplicating its input/output contract. The independent oracle enumerates all top/bottom/left/right rectangles and uses a two-dimensional zero-count prefix table to reject any containing a zero.",
        "O(rows × columns)", "O(columns)", difficulty=8,
        stress=[([[list("1" * 200) for _ in range(200)]], 40000),
                ([[[str((r + c) % 2) for c in range(200)] for r in range(200)]], 1)]),
}
BATCH[65]["prerequisites"] = ["strings"]
BATCH[68]["prerequisites"] = ["strings", "greedy"]
BATCH[85]["prerequisites"] = ["stacks", "matrices"]
BATCH[68]["sample_correction"] = {
    "original_expected": ["This is an", "example of text", "justification. "],
    "corrected_expected": ["This    is    an", "example  of text", "justification.  "],
    "reason": "The workbook collapses repeated spaces. The retained upstream Example 1 and maxWidth=16 contract require lines of length 16, left-biased extra gaps, and two trailing spaces on the last line. Input words and order are unchanged.",
}
