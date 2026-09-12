"""Reviewed conversion, interval, permutation-rank, and linked-rotation contracts."""
from itertools import islice, permutations
from math import factorial
import re

from .import_batch_003 import entry


def zigzag_oracle(args):
    text, rows = args
    if rows == 1:
        return text
    cycle = 2 * (rows - 1)
    ordered = sorted((min(i % cycle, cycle - i % cycle), i, char) for i, char in enumerate(text))
    return "".join(char for _, _, char in ordered)


def atoi_oracle(args):
    match = re.match(r" *([+-]?[0-9]+)", args[0])
    number = int(match[1]) if match else 0
    return max(-(2**31), min(2**31 - 1, number))


ROMAN_PLACES = (
    ("", "M", "MM", "MMM"),
    ("", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"),
    ("", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"),
    ("", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"),
)


def roman_oracle(args):
    n = args[0]
    return "".join(table[n // place % 10] for table, place in zip(ROMAN_PLACES, (1000, 100, 10, 1)))


ROMAN_LOOKUP = {roman_oracle([n]): n for n in range(1, 4000)}


def numeral_oracle(args):
    return ROMAN_LOOKUP[args[0]]


def division_oracle(args):
    dividend, divisor = args
    quotient = abs(dividend) // abs(divisor)
    if (dividend < 0) != (divisor < 0):
        quotient = -quotient
    return max(-(2**31), min(2**31 - 1, quotient))


def interval_oracle(args):
    # Connected components of the interval-intersection graph, independent of
    # the reference's sorted one-pass insertion and merging windows.
    intervals = args[0] + [args[1]]
    pending, answer = set(range(len(intervals))), []
    while pending:
        seed = pending.pop()
        stack, component = [seed], [intervals[seed]]
        while stack:
            index = stack.pop()
            left, right = intervals[index]
            for other in list(pending):
                start, end = intervals[other]
                if left <= end and start <= right:
                    pending.remove(other)
                    stack.append(other)
                    component.append(intervals[other])
        answer.append([min(p[0] for p in component), max(p[1] for p in component)])
    return sorted(answer)


def spiral_oracle(args):
    n = args[0]
    grid = [[0] * n for _ in range(n)]
    row = col = direction = 0
    steps = ((0, 1), (1, 0), (0, -1), (-1, 0))
    for value in range(1, n * n + 1):
        grid[row][col] = value
        dr, dc = steps[direction]
        nr, nc = row + dr, col + dc
        if not (0 <= nr < n and 0 <= nc < n) or grid[nr][nc]:
            direction = (direction + 1) % 4
            dr, dc = steps[direction]
        row, col = row + dr, col + dc
    return grid


def permutation_oracle(args):
    n, k = args
    return "".join(map(str, next(islice(permutations(range(1, n + 1)), k - 1, None))))


def rotation_oracle(args):
    values, k = args
    if not values:
        return []
    shift = k % len(values)
    return [values[(i - shift) % len(values)] for i in range(len(values))]


def random_zigzag(rng):
    return ["".join(rng.choice("abcXYZ,.") for _ in range(rng.randint(1, 60))), rng.randint(1, 70)]


def random_atoi(rng):
    if rng.random() < .7:
        return [" " * rng.randrange(5) + rng.choice(("", "+", "-")) + "0" * rng.randrange(4)
                + str(rng.randrange(10**15)) + rng.choice(("", "words", ".5", "+1", " 9"))]
    return ["".join(rng.choice(" +-abcXYZ.0123456789") for _ in range(rng.randrange(40)))]


def random_roman(rng):
    return [rng.randint(1, 3999)]


def random_numeral(rng):
    return [roman_oracle(random_roman(rng))]


def random_division(rng):
    dividend = rng.randint(-(2**31), 2**31 - 1)
    divisor = rng.choice((-1, 1, rng.randint(-(2**31), -1), rng.randint(1, 2**31 - 1)))
    return [dividend, divisor]


def random_intervals(rng):
    intervals, cursor = [], rng.randrange(5)
    for _ in range(rng.randrange(11)):
        end = cursor + rng.randrange(6)
        intervals.append([cursor, end])
        cursor = end + rng.randint(1, 4)
    a, b = rng.randint(0, cursor + 5), rng.randint(0, cursor + 5)
    return [intervals, [min(a, b), max(a, b)]]


def random_spiral(rng):
    return [rng.randint(1, 20)]


def random_permutation(rng):
    n = rng.randint(1, 7)
    return [n, rng.randint(1, factorial(n))]


def random_rotation(rng):
    values = [rng.randint(-100, 100) for _ in range(rng.randrange(61))]
    return [values, rng.choice((0, len(values), rng.randint(0, 2 * 10**9)))]


ZIGZAG = '''\
def convert(s, num_rows):
    if num_rows == 1 or num_rows >= len(s):
        return s
    rows = [[] for _ in range(num_rows)]
    row, direction = 0, 1
    for char in s:
        rows[row].append(char)
        if row == 0:
            direction = 1
        elif row == num_rows - 1:
            direction = -1
        row += direction
    return "".join("".join(values) for values in rows)
'''
ATOI = '''\
def my_atoi(s):
    index, sign, value = 0, 1, 0
    while index < len(s) and s[index] == " ":
        index += 1
    if index < len(s) and s[index] in "+-":
        sign = -1 if s[index] == "-" else 1
        index += 1
    while index < len(s) and "0" <= s[index] <= "9":
        value = value * 10 + ord(s[index]) - ord("0")
        index += 1
    value *= sign
    return max(-2147483648, min(2147483647, value))
'''
ROMAN = '''\
def integer_to_roman(num):
    tokens = [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]
    parts = []
    for value, token in tokens:
        while num >= value:
            parts.append(token)
            num -= value
    return "".join(parts)
'''
NUMERAL = '''\
def roman_to_integer(s):
    values = {"I":1,"V":5,"X":10,"L":50,"C":100,"D":500,"M":1000}
    total = 0
    for i, char in enumerate(s):
        if i + 1 < len(s) and values[char] < values[s[i + 1]]:
            total -= values[char]
        else:
            total += values[char]
    return total
'''
DIVISION = '''\
def divide_integers(dividend, divisor):
    minimum = -2147483648
    negative = (dividend < 0) != (divisor < 0)
    remaining = dividend if dividend < 0 else -dividend
    base = divisor if divisor < 0 else -divisor
    quotient = 0
    for shift in range(31, -1, -1):
        if base >= (minimum >> shift):
            multiple = base << shift
            if remaining <= multiple:
                remaining -= multiple
                quotient += (-1 << shift)
    if not negative and quotient == minimum:
        return 2147483647
    return quotient if negative else -quotient
'''
INTERVAL = '''\
def insert_interval(intervals, new_interval):
    answer, index = [], 0
    start, end = new_interval
    while index < len(intervals) and intervals[index][1] < start:
        answer.append(intervals[index].copy())
        index += 1
    while index < len(intervals) and intervals[index][0] <= end:
        start = min(start, intervals[index][0])
        end = max(end, intervals[index][1])
        index += 1
    answer.append([start, end])
    answer.extend(row.copy() for row in intervals[index:])
    return answer
'''
SPIRAL = '''\
def generate_spiral(n):
    grid = [[0] * n for _ in range(n)]
    top, bottom, left, right, value = 0, n - 1, 0, n - 1, 1
    while top <= bottom and left <= right:
        for col in range(left, right + 1):
            grid[top][col] = value
            value += 1
        top += 1
        for row in range(top, bottom + 1):
            grid[row][right] = value
            value += 1
        right -= 1
        if top <= bottom:
            for col in range(right, left - 1, -1):
                grid[bottom][col] = value
                value += 1
            bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):
                grid[row][left] = value
                value += 1
            left += 1
    return grid
'''
PERMUTATION = '''\
def permutation_sequence(n, k):
    from math import factorial
    available = [str(value) for value in range(1, n + 1)]
    rank, answer = k - 1, []
    for remaining in range(n, 0, -1):
        index, rank = divmod(rank, factorial(remaining - 1))
        answer.append(available.pop(index))
    return "".join(answer)
'''
ROTATE = '''\
def rotate_list(head, k):
    if head is None or head.next is None:
        return head
    size, tail = 1, head
    while tail.next:
        size += 1
        tail = tail.next
    k %= size
    if k == 0:
        return head
    tail.next = head
    new_tail = head
    for _ in range(size - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    return new_head
'''

BATCH = {
    6: entry("convert", [("s","str"),("num_rows","int")], "str", ["strings","simulation"],
        ["1–1000 characters: uppercase/lowercase English letters, commas, or periods.","1 <= num_rows <= 1000. Write characters down the rows then diagonally upward repeatedly; read rows from top to bottom."],
        [(["PAYPALISHIRING",3],"The rows contain PAHN, APLSIIG, and YIR; joining them gives PAHNAPLSIIGYIR."),
         (["PAYPALISHIRING",4],"The four rows read PIN, ALSIG, YAHR, and PI, giving PINALSIGYAHRPI.")],
        [["A",1],["AB",1],["AB",2],["AB",5],["ABC",2],["ABCD",2],["ABCDE",3],["ABCDEF",4],["ABCDEFG",3],["Ab,C.d",2],["aaaaaa",3],["ABCDEFGHI",5]],
        ZIGZAG, [ZIGZAG.replace('for values in rows)', 'for values in rows[::-1])'),
                 'def convert(s, num_rows):\n    return "".join(s[row::num_rows] for row in range(num_rows))\n'],
        ["Reads the zigzag rows bottom-to-top instead of top-to-bottom.","Writes columns repeatedly without the diagonal upward traversal."], zigzag_oracle, random_zigzag,
        ["Only each character's destination row matters; a full visual grid is unnecessary.","Append to row buckets while changing direction at the top and bottom rows.","For each character, append it, set direction at a boundary, and move the row pointer; join all row buckets at the end.","One row, or at least as many rows as characters, leaves the input unchanged."],
        "Simulate the current row and travel direction. Every character goes into exactly one row bucket. Reverse direction at the first and last row, then concatenate buckets in reading order. The reference uses lists to avoid repeated immutable-string concatenation. The oracle instead computes the triangular-wave row index using the cycle length 2(rows−1), then orders characters by row and original position.","O(len(s))","O(len(s))",difficulty=5),
    8: entry("my_atoi", [("s","str")], "int", ["strings","simulation"],
        ["0–200 characters consisting of English letters, digits, spaces, '+', '-', and '.'.", "Skip leading spaces, consume at most one sign, then read consecutive digits until the first other character. No digits means zero.", "Clamp to [-2^31, 2^31−1]. Spaces after a sign are not skipped."],
        [(["42"],"Both characters are digits, so return 42."),(["   -042words"],"Skip the leading spaces, retain the minus sign, read 042, and stop at w. The result is -42.")],
        [[s] for s in (""," ","+","-","+-12","words and 987","4193 with words","3.14159","- 12","2147483648","-2147483649","00000-42a1234")],
        ATOI, [ATOI.replace('sign = -1 if s[index] == "-" else 1','sign = 1'),
               ATOI.replace('return max(-2147483648, min(2147483647, value))','return value')],
        ["Ignores the negative sign.","Returns out-of-range values instead of clamping to signed 32-bit bounds."], atoi_oracle, random_atoi,
        ["Parsing has ordered phases: spaces, optional sign, digits, then stop.","Use an index and stop digit accumulation immediately on a non-digit.","Skip only initial spaces, consume one sign, repeatedly multiply the value by ten and add a digit, then apply sign and clamp.","A second sign or a space after the sign ends parsing before any digits are read."],
        "Walk the input once. The initial-space loop must happen before sign handling, not during digit parsing. After an optional sign, accumulate only the consecutive digit run. Applying the sign to a zero accumulator naturally handles missing digits. Clamp the signed result to the 32-bit interval. A regular-expression prefix capture plus Python integer conversion provides an independent oracle.","O(n)","O(n) bits for the bounded input accumulator",difficulty=5),
    12: entry("integer_to_roman", [("num","int")], "str", ["math","greedy","strings"],
        ["1 <= num <= 3999.","Use I,V,X,L,C,D,M and canonical subtractive pairs IV,IX,XL,XC,CD,CM. Do not produce additive alternatives such as IIII."],
        [([3749],"3000→MMM, 700→DCC, 40→XL, 9→IX; concatenate to MMMDCCXLIX."),([1994],"1000→M, 900→CM, 90→XC, 4→IV, giving MCMXCIV.")],
        [[n] for n in (1,3,4,5,9,10,40,90,400,900,3888,3999)],
        ROMAN, [ROMAN.replace('(900,"CM"),','').replace('(400,"CD"),','').replace('(90,"XC"),','').replace('(40,"XL"),','').replace('(9,"IX"),','').replace('(4,"IV"),',''),
                ROMAN.replace('while num >= value:','if num >= value:')],
        ["Omits subtractive forms and emits noncanonical repetitions.","Uses each denomination at most once, losing repeated symbols such as MMM."], roman_oracle, random_roman,
        ["Treat each subtractive pair as a denomination alongside the single symbols.","Consume denominations in descending order, repeatedly while they fit.","Append the chosen token, subtract its value, and continue; the table includes 900,400,90,40,9,4.","The input bound guarantees a canonical representation without symbols above M."],
        "Process a descending table of canonical tokens, including every subtractive pair. Repeatedly take a token while its value fits the remaining number. The table encodes canonical hundreds, tens, and ones while M handles thousands. The independent oracle concatenates four place-value lookup strings rather than subtracting denominations. Under the fixed 1…3999 domain, both running time and output size have constant bounds.","O(output length); bounded by the input range","O(output length)",difficulty=5),
    13: entry("roman_to_integer", [("s","str")], "int", ["strings","math"],
        ["s is a valid canonical Roman numeral representing 1–3999, with length 1–15.","Symbols are I,V,X,L,C,D,M. A smaller symbol immediately before a larger symbol contributes negatively."],
        [(["III"],"Three I symbols add to 3."),(["MCMXCIV"],"M contributes 1000, CM 900, XC 90, and IV 4, totaling 1994.")],
        [[s] for s in ("I","II","IV","V","IX","X","XL","XC","CD","CM","MMMDCCCLXXXVIII","MMMCMXCIX")],
        NUMERAL, [NUMERAL.replace('total -= values[char]','total += values[char]'),
                  NUMERAL.replace('if i + 1 < len(s) and', 'if char == "I" and i + 1 < len(s) and')],
        ["Adds every symbol even when it precedes a larger one.","Recognizes subtractive I pairs but not X or C pairs."], numeral_oracle, random_numeral,
        ["Compare a symbol with the next symbol before choosing addition or subtraction.","Subtract it when the next value is larger; otherwise add it.","Scan all positions, treating the final symbol as additive because it has no successor.","Validity is guaranteed, so no separate Roman grammar validator is required."],
        "Map symbols to values and inspect adjacent values. For each valid subtractive pair, subtracting its first symbol and later adding the second produces the pair's value. All other symbols add normally. The input guarantee rules out malformed combinations. The independent oracle looks up the entire numeral in a table generated from canonical decimal-place encodings for 1…3999.","O(len(s))","O(1)",difficulty=3),
    29: entry("divide_integers", [("dividend","int"),("divisor","int")], "int", ["math","bit-manipulation"],
        ["Dividend and divisor are signed 32-bit integers; divisor is nonzero.","Do not use multiplication, division, floor division, or modulo. Truncate the quotient toward zero and clamp overflow to signed 32-bit limits."],
        [([10,3],"Three whole groups of 3 fit into 10; discard the fractional remainder."),([-7,3],"Truncation toward zero gives -2, not the floor-division result -3.")],
        [[0,1],[1,1],[-1,1],[1,-1],[-1,-1],[7,-3],[-7,-3],[1,2],[-1,2],[-2147483648,-1],[-2147483648,1],[2147483647,2]],
        DIVISION, [DIVISION.replace('return quotient if negative else -quotient','return -quotient'),
                   DIVISION.replace('if not negative and quotient == minimum:', 'if False:')],
        ["Always returns a nonnegative quotient.","Fails to clamp the one positive overflow case, minimum-int divided by -1."], division_oracle, random_division,
        ["Build the quotient from powers of two rather than subtracting the divisor one unit at a time.","Use negative magnitudes so the minimum signed integer remains representable.","Try shifted divisor multiples from the largest safe shift downward; subtract fitting multiples and add their negative powers of two to the quotient.","Check a shift before performing it, then restore the sign and handle the positive overflow boundary."],
        "Keep the remaining dividend, divisor, and accumulated quotient nonpositive. For each of 32 shifts, first verify that shifting the negative divisor stays within the signed range. If that multiple fits, subtract it from the remaining dividend and add the corresponding negative quotient bit. This uses only shifts, additions, subtractions, and comparisons. Restore the required sign afterward, clamping −2^31/−1. The oracle uses ordinary exact integer division on magnitudes and applies truncation and clamping independently.","O(32) for signed 32-bit inputs","O(1)",difficulty=5),
    57: entry("insert_interval", [("intervals","list[list[int]]"),("new_interval","list[int]")], "list[list[int]]", ["intervals","arrays"],
        ["0–10,000 existing intervals are sorted by start and pairwise non-overlapping.", "Every interval is closed [start,end], with 0<=start<=end<=100,000. Insert one new interval, merging all overlaps including shared endpoints."],
        [([[[1,3],[6,9]],[2,5]],"The new interval overlaps [1,3], producing [1,5]; [6,9] remains separate."),
         ([[[1,2],[3,5],[6,7],[8,10],[12,16]],[4,8]],"The insertion joins [3,5], [6,7], and [8,10] into [3,10], including the shared endpoint 8.")],
        [[[],[1,2]],[[],[0,0]],[[[1,2]],[3,4]],[[[3,4]],[1,2]],[[[1,2]],[2,3]],[[[2,3]],[1,2]],
         [[[1,10]],[3,5]],[[[3,5]],[1,10]],[[[1,2],[4,5]],[2,4]],[[[0,0],[2,2]],[1,1]],
         [[[1,2],[4,5]],[6,7]],[[[1,2],[4,5]],[0,100000]]],
        INTERVAL, [INTERVAL.replace('intervals[index][0] <= end', 'intervals[index][0] < end'),
                   INTERVAL.replace('end = max(end, intervals[index][1])','end = intervals[index][1]')],
        ["Fails to merge intervals touching at a closed endpoint.","Shrinks the merged right endpoint when an existing interval lies inside the inserted interval."], interval_oracle, random_intervals,
        ["Sorted non-overlapping inputs split into an unchanged prefix, an overlapping middle, and an unchanged suffix.","Copy intervals before the new one; expand its bounds while overlap continues; then append the remainder.","Before means old_end<new_start. Merge while old_start<=current_end, taking min start and max end.","The merged end can only increase, and shared endpoints count as overlaps."],
        "Scan once. Intervals ending before the insertion begins are copied directly. Each following interval whose start is at most the merged end belongs to the overlapping middle and extends its bounds if needed. Append the resulting merged interval, then the untouched suffix. The monotonic ordering removes the need to sort. The oracle instead finds connected components in the full interval-intersection graph and takes each component's outer bounds.","O(n)","O(n) including output",difficulty=5),
    59: entry("generate_spiral", [("n","int")], "list[list[int]]", ["matrices","simulation"],
        ["1 <= n <= 20.","Return an n×n matrix filled with 1 through n² in clockwise spiral order, starting at the top-left and moving right."],
        [([3],"The outside holds 1 through 8 clockwise; the remaining center cell receives 9."),([1],"The only cell receives 1.")],
        [[n] for n in (2,4,5,6,7,8,9,10,12,15,18,20)],
        SPIRAL, [SPIRAL.replace('0, n - 1, 0, n - 1, 1','0, n - 1, 0, n - 1, 0'),
                 SPIRAL.replace('return grid','return [list(row) for row in zip(*grid)]')],
        ["Starts numbering at zero instead of one.","Transposes row and column positions, producing the wrong traversal orientation."], spiral_oracle, random_spiral,
        ["The unfilled cells form a rectangle bounded by top, bottom, left, and right.","Fill its four edges clockwise, shrinking each boundary after use.","Fill top then right; fill bottom and left only if those edges still exist. Increase the next value after every assignment.","Boundary checks avoid filling the center row or column twice."],
        "Maintain four boundaries and the next integer. Fill the top edge left-to-right, the right edge downward, the bottom edge right-to-left if present, and the left edge upward if present. Shrink boundaries as edges are consumed. Each cell is assigned once. The independent oracle follows a direction vector, turning whenever the next position is outside the board or already filled.","O(n²)","O(n²) including output",difficulty=5),
    60: entry("permutation_sequence", [("n","int"),("k","int")], "str", ["math","combinatorics"],
        ["1 <= n <= 9; 1 <= k <= n!.","Return the kth lexicographically ordered permutation of digits 1 through n as a string. k is one-indexed."],
        [([3,3],"The order begins 123,132,213, so the third permutation is 213."),([4,9],"Each first-digit block has 3!=6 permutations. The ninth lies in the 2-prefix block and is 2314.")],
        [[1,1],[2,1],[2,2],[3,1],[3,2],[3,4],[3,5],[3,6],[4,1],[4,24],[5,42],[9,362880]],
        PERMUTATION, [PERMUTATION.replace('rank, answer = k - 1, []','rank, answer = k, []'),
                      PERMUTATION.replace('range(1, n + 1)', 'range(n, 0, -1)')],
        ["Uses the one-indexed rank directly for zero-indexed block selection.","Uses descending available digits instead of lexicographic ascending order."], permutation_oracle, random_permutation,
        ["Permutations sharing the first digit form equal-size factorial blocks.","Convert k to a zero-based rank, select its block, then repeat within that block.","Divide rank by (remaining-1)! to choose an unused digit; retain the remainder for the suffix.","Remove each chosen digit so it cannot be selected twice."],
        "Convert to zero-based rank. With r digits remaining, each next-digit choice contributes (r−1)! consecutive permutations. The quotient selects the next digit from the sorted unused list, while the remainder is the rank within that block. Remove the selected digit and continue. List removal gives O(n²) total time, far less than enumerating n! strings. The independent oracle does enumerate permutations lazily and selects the kth entry.","O(n²)","O(n)",difficulty=8),
    61: entry("rotate_list", [("head","ListNode | None"),("k","int")], "ListNode | None", ["linked-lists","two-pointers"],
        ["0–500 nodes; values are between -100 and 100. 0<=k<=2×10^9.","Rotate right by k positions by reconnecting the original nodes, preserving their values. Return None for an empty list."],
        [([[1,2,3,4,5],2],"The last two nodes move to the front, giving 4→5→1→2→3."),
         ([[0,1,2],4],"Four rotations of a three-node list equal one rotation, giving 2→0→1.")],
        [[[],0],[[],7],[[1],0],[[1],2000000000],[[1,2],0],[[1,2],1],[[1,2],2],[[1,2],3],
         [[1,2,3],1],[[1,2,3],3],[[1,1,2,2],2],[[-100,0,100],2000000000]],
        ROTATE, [ROTATE.replace('k %= size','k = k'),ROTATE.replace('return new_head','return new_tail')],
        ["Does not reduce k modulo the list length.","Returns the new tail instead of the head of the rotated chain."], rotation_oracle, random_rotation,
        ["Only k modulo the list length matters.","Locate the old tail, temporarily link it to the head, and choose where to break the cycle.","The new tail is at zero-based position size-k-1; save its next node as the new head, then clear its next pointer.","Empty, single-node, and zero-effective-rotation cases need no rewiring."],
        "Measure the list and reduce k modulo its length. For a nonzero shift, connect the old tail to the head to form a temporary ring. The node just before the last k original nodes becomes the new tail. Save its next node as the new head and sever that link to restore a finite chain. The reference uses constant pointer storage and never changes a node's value. The oracle computes the rotated sequence with modular indexing, independently of pointer rewiring.","O(n)","O(1)",difficulty=5),
}
BATCH[60]["prerequisites"] = ["combinatorics"]
BATCH[61]["params"][0] = ("head", "ListNode | None", "listnode")
BATCH[61]["adapter"] = "listnode"
BATCH[61]["node_policy"] = "reuse_input_nodes"
