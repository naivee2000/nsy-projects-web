"""Third reviewed group of workbook batch 110."""

from collections import deque

from .import_batch_055 import entry


def peak_oracle(arguments):
    matrix = arguments[0]
    rows, columns = len(matrix), len(matrix[0])
    for row in range(rows):
        for column in range(columns):
            neighbors = []
            for row_step, column_step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                next_row, next_column = row + row_step, column + column_step
                if 0 <= next_row < rows and 0 <= next_column < columns:
                    neighbors.append(matrix[next_row][next_column])
            if all(matrix[row][column] > value for value in neighbors):
                return [row, column]
    raise AssertionError("a peak must exist")


def bst_depth_oracle(arguments):
    order = arguments[0]
    root = [order[0], None, None]
    maximum = 1
    for value in order[1:]:
        node = root
        depth = 1
        while True:
            branch = 1 if value < node[0] else 2
            depth += 1
            if node[branch] is None:
                node[branch] = [value, None, None]
                break
            node = node[branch]
        maximum = max(maximum, depth)
    return maximum


def odd_oracle(arguments):
    number = arguments[0]
    candidates = [number[:end] for end in range(1, len(number) + 1)
                  if int(number[end - 1]) % 2 == 1]
    return max(candidates, key=int, default="")


def rounds_oracle(arguments):
    login, logout = arguments
    start = int(login[:2]) * 60 + int(login[3:])
    finish = int(logout[:2]) * 60 + int(logout[3:])
    if finish < start:
        finish += 1440
    return sum(round_start >= start and round_start + 15 <= finish
               for round_start in range(0, 2880, 15))


def sub_islands_oracle(arguments):
    grid1, grid2 = arguments
    rows, columns = len(grid1), len(grid1[0])
    seen = set()
    answer = 0
    for start_row in range(rows):
        for start_column in range(columns):
            if not grid2[start_row][start_column] or (start_row, start_column) in seen:
                continue
            component = {(start_row, start_column)}
            queue = deque(component)
            seen.add((start_row, start_column))
            while queue:
                row, column = queue.popleft()
                for row_step, column_step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    neighbor = row + row_step, column + column_step
                    if (0 <= neighbor[0] < rows and 0 <= neighbor[1] < columns
                            and grid2[neighbor[0]][neighbor[1]] and neighbor not in seen):
                        seen.add(neighbor)
                        component.add(neighbor)
                        queue.append(neighbor)
            answer += all(grid1[row][column] for row, column in component)
    return answer


def random_peak(rng):
    rows, columns = rng.randint(1, 8), rng.randint(1, 8)
    peak_row, peak_column = rng.randrange(rows), rng.randrange(columns)
    matrix = [[10000 - abs(row - peak_row) * (columns + 1) - abs(column - peak_column)
               for column in range(columns)] for row in range(rows)]
    return [matrix]


def random_bst(rng):
    length = rng.randint(1, 11)
    order = list(range(1, length + 1))
    rng.shuffle(order)
    return [order]


def random_odd(rng):
    length = rng.randint(1, 30)
    return [rng.choice("123456789") + "".join(rng.choice("0123456789") for _ in range(length - 1))]


def random_rounds(rng):
    first, second = rng.sample(range(1440), 2)
    return [f"{first // 60:02d}:{first % 60:02d}", f"{second // 60:02d}:{second % 60:02d}"]


def random_sub_islands(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    return [[[rng.randint(0, 1) for _ in range(columns)] for _ in range(rows)],
            [[rng.randint(0, 1) for _ in range(columns)] for _ in range(rows)]]


PEAK = '''\
def find_matrix_peak(mat):
    top, bottom = 0, len(mat) - 1
    while top < bottom:
        middle = (top + bottom) // 2
        column = max(range(len(mat[0])), key=lambda index: mat[middle][index])
        if mat[middle][column] > mat[middle + 1][column]:
            bottom = middle
        else:
            top = middle + 1
    column = max(range(len(mat[0])), key=lambda index: mat[top][index])
    return [top, column]
'''

PEAK_FIRST_ROW = '''\
def find_matrix_peak(mat):
    column = max(range(len(mat[0])), key=lambda index: mat[0][index])
    return [0, column]
'''

BST_DEPTH = '''\
def insertion_order_bst_depth(order):
    size = len(order)
    tree = [0] * (size + 1)
    depths = [0] * (size + 2)
    def add(index):
        while index <= size:
            tree[index] += 1
            index += index & -index
    def prefix(index):
        total = 0
        while index > 0:
            total += tree[index]
            index -= index & -index
        return total
    def kth(rank):
        index = 0
        step = 1 << (size.bit_length() - 1)
        while step:
            candidate = index + step
            if candidate <= size and tree[candidate] < rank:
                index = candidate
                rank -= tree[candidate]
            step //= 2
        return index + 1
    root = order[0]
    depths[root] = 1
    add(root)
    answer = 1
    for value in order[1:]:
        smaller = prefix(value - 1)
        inserted = prefix(size)
        predecessor = kth(smaller) if smaller else 0
        successor = kth(smaller + 1) if smaller < inserted else size + 1
        depths[value] = 1 + max(depths[predecessor], depths[successor])
        answer = max(answer, depths[value])
        add(value)
    return answer
'''

ODD = '''\
def largest_odd_numeric_substring(num):
    for index in range(len(num) - 1, -1, -1):
        if int(num[index]) % 2 == 1:
            return num[:index + 1]
    return ""
'''

ROUNDS = '''\
def completed_quarter_hour_rounds(login_time, logout_time):
    def minutes(value):
        return int(value[:2]) * 60 + int(value[3:])
    login = minutes(login_time)
    logout = minutes(logout_time)
    if logout < login:
        logout += 24 * 60
    first_start = (login + 14) // 15
    last_end = logout // 15
    return max(0, last_end - first_start)
'''

SUB_ISLANDS = '''\
def count_complete_sub_islands(grid1, grid2):
    rows, columns = len(grid1), len(grid1[0])
    visited = [[False] * columns for _ in range(rows)]
    answer = 0
    for start_row in range(rows):
        for start_column in range(columns):
            if not grid2[start_row][start_column] or visited[start_row][start_column]:
                continue
            stack = [(start_row, start_column)]
            visited[start_row][start_column] = True
            valid = True
            while stack:
                row, column = stack.pop()
                if grid1[row][column] == 0:
                    valid = False
                for row_step, column_step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    next_row, next_column = row + row_step, column + column_step
                    if (0 <= next_row < rows and 0 <= next_column < columns and
                            grid2[next_row][next_column] and not visited[next_row][next_column]):
                        visited[next_row][next_column] = True
                        stack.append((next_row, next_column))
            answer += valid
    return answer
'''

SUB_ISLAND_ANY = '''\
def count_complete_sub_islands(grid1, grid2):
    rows, columns = len(grid1), len(grid1[0]); seen = set(); answer = 0
    for sr in range(rows):
        for sc in range(columns):
            if not grid2[sr][sc] or (sr,sc) in seen: continue
            stack=[(sr,sc)];seen.add((sr,sc));valid=False
            while stack:
                r,c=stack.pop();valid |= bool(grid1[r][c])
                for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
                    nr,nc=r+dr,c+dc
                    if 0<=nr<rows and 0<=nc<columns and grid2[nr][nc] and (nr,nc) not in seen:
                        seen.add((nr,nc));stack.append((nr,nc))
            answer += valid
    return answer
'''

SUB_ISLAND_GRID1 = '''\
def count_complete_sub_islands(grid1, grid2):
    rows,columns=len(grid1),len(grid1[0]);seen=set();answer=0
    for sr in range(rows):
        for sc in range(columns):
            if not grid1[sr][sc] or (sr,sc) in seen: continue
            answer+=1;stack=[(sr,sc)];seen.add((sr,sc))
            while stack:
                r,c=stack.pop()
                for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
                    p=(r+dr,c+dc)
                    if 0<=p[0]<rows and 0<=p[1]<columns and grid1[p[0]][p[1]] and p not in seen:seen.add(p);stack.append(p)
    return answer
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1901: entry(
        "find_matrix_peak", [("mat", "list[list[int]]")], "list[int]",
        ["matrices", "binary-search", "arrays"],
        ["The matrix has 1 through 500 rows and columns with positive values.", "Orthogonally adjacent cells are unequal.",
         "Return coordinates of a cell strictly greater than every existing orthogonal neighbor in O(rows*log(columns)) or O(columns*log(rows))."],
        [([[[1,4],[3,2]]], "The value four at [0,1] is one valid peak because it exceeds its left and lower neighbors."),
         ([[[10,20,15],[21,30,14],[7,31,32]]], "The row-search follows larger downward values and returns the unique peak 32 at [2,2].")],
        [[matrix] for matrix in [
            [[1]],[[1,2]],[[2,1]],[[1],[2]],[[2],[1]],[[1,4],[2,3]],
            [[1,2,3],[4,5,6]],[[6,5,4],[3,2,1]],[[1,2],[3,4]],
            [[10,20,15],[21,30,14],[7,31,32]],[[9,8,7],[6,5,4],[3,2,1]],
            [[1,3,5,7],[2,4,6,8]],[[8,6,4,2],[7,5,3,1]],[[1,2,3],[2,3,4],[3,4,5]],
        ]],
        PEAK,
        [PEAK_FIRST_ROW, PEAK.replace("mat[middle][column] > mat[middle + 1][column]", "mat[middle][column] < mat[middle + 1][column]")],
        ["Always chooses the first row's maximum without checking vertical neighbors.",
         "Moves the row binary search away from the larger vertical neighbor."],
        peak_oracle, random_peak,
        lesson("Within a row, choose its maximum so horizontal neighbors cannot be larger.",
               "Compare that value with the cell directly below; move toward the larger of the two row directions.",
               "Binary-search rows until one remains, then return that row's maximum column.",
               "A larger vertical neighbor guarantees a peak exists in that direction, preserving the search invariant; the final row maximum is greater than all four neighbors."),
        "O(columns*log(rows))", "O(1)", 7),
    1902: entry(
        "insertion_order_bst_depth", [("order", "list[int]")], "int",
        ["trees", "binary-search-trees", "binary-search", "fenwick-trees"],
        ["order is a permutation of 1 through n, where 1 <= n <= 100000.",
         "Insert values into an initially empty binary search tree in the listed order.",
         "Return depth measured in nodes, so a root-only tree has depth one."],
        [([[2,1,4,3]], "Two is the root and three becomes the left child of four, creating depth three."),
         ([[3,2,1,5,4,6]], "The deepest inserted values are at depth three.")],
        [[order] for order in [
            [1],[1,2],[2,1],[2,1,4,3],[1,2,3,4],[4,3,2,1],[3,2,1,5,4,6],
            [4,2,6,1,3,5,7],[5,1,2,3,4],[2,5,4,1,3],[6,2,8,1,4,7,9,3,5],
            [3,1,4,2],[5,3,7,2,4,6,1],[7,1,6,2,5,3,4],[4,3,2,1,6,5,7],
        ]],
        BST_DEPTH,
        [BST_DEPTH.replace("max(depths[predecessor], depths[successor])", "min(depths[predecessor], depths[successor])"),
         BST_DEPTH.replace("answer = max(answer, depths[value])", "answer = depths[value]")],
        ["Uses the shallower ordered neighbor even though the new node attaches below the deeper predecessor or successor.",
         "Returns the most recently inserted node's depth instead of the maximum depth reached."],
        bst_depth_oracle, random_bst,
        lesson("A newly inserted key becomes a child below its nearest already-inserted predecessor or successor, whichever is deeper.",
               "Use a Fenwick tree over permutation values to find the immediate active predecessor and successor by rank.",
               "Set the new depth to one plus their maximum depth, activate the key, and track the global maximum.",
               "BST search can meet no other existing key between these ordered neighbors, so one of them is the parent; rank queries recover them in logarithmic time."),
        "O(n*log(n))", "O(n)", 7),
    1903: entry(
        "largest_odd_numeric_substring", [("num", "str")], "str",
        ["strings", "greedy", "math"],
        ["num has 1 through 100000 digits and no leading zero.",
         "Return the numerically largest odd-valued contiguous substring, or empty string when none exists.",
         "The returned representation must preserve its characters from num."],
        [(["52"], "The prefix 5 is the largest odd substring."),
         (["35427"], "The entire number already ends in an odd digit and is therefore the largest candidate.")],
        [[num] for num in ["1","2","52","4206","35427","1010","100","2468","13579","9998","123456","8887","7000","31415926"]],
        ODD,
        [ODD.replace("range(len(num) - 1, -1, -1)", "range(len(num))"),
         ODD.replace("return num[:index + 1]", "return num[index]")],
        ["Stops at the first odd digit from the left, producing a shorter and therefore smaller positive substring.",
         "Returns only the final odd digit rather than the full maximal prefix ending there."],
        odd_oracle, random_odd,
        lesson("A decimal integer is odd exactly when its final digit is odd.",
               "Scan from right to left for the last odd digit.",
               "Return the entire prefix through that digit; if none exists, return empty string.",
               "With no leading zero, every longer prefix is numerically larger, so the rightmost valid ending produces the largest possible odd substring."),
        "O(len(num))", "O(len(num))", 3),
    1904: entry(
        "completed_quarter_hour_rounds", [("login_time", "str"), ("logout_time", "str")], "int",
        ["strings", "math", "simulation"],
        ["Times use valid 24-hour HH:MM format and are unequal.", "Rounds begin every 15 minutes.",
         "If logout is earlier than login, the session crosses midnight; count only rounds fully contained in the session."],
        [(["09:31","10:14"], "Only the 09:45 through 10:00 round is fully contained."),
         (["20:00","06:00"], "The overnight ten-hour interval contains forty complete quarter-hour rounds.")],
        [[start,end] for start,end in [
            ("09:31","10:14"),("20:00","06:00"),("00:00","00:15"),("00:01","00:14"),
            ("12:00","12:30"),("12:01","12:31"),("23:50","00:20"),("23:45","00:00"),
            ("05:15","05:45"),("05:16","05:44"),("18:59","19:16"),("10:14","10:16"),
            ("22:30","01:30"),("06:07","07:53"),
        ]],
        ROUNDS,
        [ROUNDS.replace("if logout < login:\n        logout += 24 * 60", "if False:\n        logout += 24 * 60"),
         ROUNDS.replace("(login + 14) // 15", "login // 15")],
        ["Treats an overnight logout as earlier on the same day and loses all cross-midnight rounds.",
         "Rounds login down to a start before the user arrived, counting a partial opening round."],
        rounds_oracle, random_rounds,
        lesson("Convert both clock strings to minutes after midnight and add one day to an overnight logout.",
               "Round login up to the first round boundary and logout down to the last completed boundary.",
               "Subtract the resulting quarter-hour indices, clamping at zero.",
               "Those boundaries exclude both partial edge rounds and retain every full interior 15-minute interval exactly once."),
        "O(1)", "O(1)", 5),
    1905: entry(
        "count_complete_sub_islands", [("grid1", "list[list[int]]"), ("grid2", "list[list[int]]")], "int",
        ["matrices", "depth-first-search", "recursion", "graphs"],
        ["The two binary grids have identical dimensions up to 500 by 500.",
         "Land connects only orthogonally; each grid2 island is one maximal connected land component.",
         "Count a grid2 island only when every one of its cells is land in grid1."],
        [([[[1,1,1,0,0],[0,1,1,1,1],[0,0,0,0,0],[1,0,0,0,0],[1,1,0,1,1]],
           [[1,1,1,0,0],[0,0,1,1,1],[0,1,0,0,0],[1,0,1,1,0],[0,1,0,1,0]]],
          "Three grid2 components lie entirely on grid1 land."),
         ([[[1,0],[0,1]],[[1,1],[0,1]]], "The connected grid2 island includes a cell over grid1 water, so it is not a sub-island.")],
        [[first,second] for first,second in [
            ([[0]],[[0]]),([[1]],[[1]]),([[0]],[[1]]),([[1,0],[0,1]],[[1,1],[0,1]]),
            ([[1,1],[1,1]],[[1,0],[0,1]]),([[1,1,1],[1,0,1],[1,1,1]],[[1,1,1],[1,0,1],[1,1,1]]),
            ([[1,0,1],[1,0,1]],[[1,0,1],[1,0,1]]),([[1,1,0],[0,1,0]],[[1,1,0],[0,1,1]]),
            ([[0,0],[0,0]],[[1,0],[0,1]]),([[1,1,1]],[[1,0,1]]),
            ([[1],[1],[0],[1]],[[1],[1],[1],[1]]),
            ([[1,0,1],[0,1,0],[1,0,1]],[[1,0,1],[0,1,0],[1,0,1]]),
            ([[1,1,1],[1,1,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]]),
            ([[1,1,0,1],[1,0,0,1]],[[1,1,0,1],[0,1,0,1]]),
        ]],
        SUB_ISLANDS,
        [SUB_ISLAND_ANY, SUB_ISLAND_GRID1],
        ["Accepts a grid2 island when any one of its cells overlaps grid1 land instead of requiring every cell.",
         "Counts islands in grid1 itself and ignores the component structure and containment of grid2."],
        sub_islands_oracle, random_sub_islands,
        lesson("Treat each unvisited grid2 land cell as the start of one flood fill.",
               "Traverse its entire component using the four orthogonal directions while remembering whether any cell lies over grid1 water.",
               "Count the component only if that validity flag remains true; use an explicit stack to avoid recursion-depth failure on large grids.",
               "Flood fill visits every grid2 island exactly once, and checking every visited cell is precisely the definition of complete containment."),
        "O(rows*columns)", "O(rows*columns)", 6),
}
