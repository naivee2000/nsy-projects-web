"""Medians, recursive trees, parentheses, grids, union-find, and dynamic programming."""
from collections import Counter, deque
from functools import lru_cache
from itertools import product

from .import_batch_002 import random_tree
from .import_batch_003 import entry
from .import_batch_024 import right_chain, tree_positions


def meeting_oracle(args):
    grid = args[0]
    homes = [(row, column) for row, values in enumerate(grid)
             for column, value in enumerate(values) if value == 1]
    return min(sum(abs(row - home_row) + abs(column - home_column)
                   for home_row, home_column in homes)
               for row in range(len(grid)) for column in range(len(grid[0])))


def consecutive_tree_oracle(args):
    mapping = tree_positions(args[0])
    longest = 0
    for path, value in mapping.items():
        length = 1
        parent = path[:-1]
        while parent in mapping and mapping[parent] + 1 == value:
            length += 1
            value = mapping[parent]
            parent = parent[:-1]
        longest = max(longest, length)
    return longest


def bulls_oracle(args):
    secret, guess = args
    bulls = sum(left == right for left, right in zip(secret, guess))
    shared = sum((Counter(secret) & Counter(guess)).values())
    return f"{bulls}A{shared - bulls}B"


def valid_parentheses(text):
    balance = 0
    for character in text:
        if character == "(":
            balance += 1
        elif character == ")":
            balance -= 1
            if balance < 0:
                return False
    return balance == 0


def invalid_parentheses_oracle(args):
    text = args[0]
    parentheses = [index for index, character in enumerate(text) if character in "()"]
    valid = set()
    longest = -1
    for mask in range(1 << len(parentheses)):
        kept = {parentheses[index] for index in range(len(parentheses)) if mask & (1 << index)}
        candidate = "".join(character for index, character in enumerate(text)
                            if character not in "()" or index in kept)
        if valid_parentheses(candidate):
            if len(candidate) > longest:
                valid, longest = {candidate}, len(candidate)
            elif len(candidate) == longest:
                valid.add(candidate)
    return sorted(valid)


def rectangle_oracle(args):
    image = args[0]
    black = [(row, column) for row, values in enumerate(image)
             for column, value in enumerate(values) if value == "1"]
    rows = [row for row, _ in black]
    columns = [column for _, column in black]
    return (max(rows) - min(rows) + 1) * (max(columns) - min(columns) + 1)


def islands_oracle(args):
    rows, columns, positions = args
    land = set()
    answers = []
    for row, column in positions:
        land.add((row, column))
        unseen = set(land)
        count = 0
        while unseen:
            count += 1
            queue = [unseen.pop()]
            while queue:
                current_row, current_column = queue.pop()
                for neighbor in ((current_row - 1, current_column),
                                 (current_row + 1, current_column),
                                 (current_row, current_column - 1),
                                 (current_row, current_column + 1)):
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        queue.append(neighbor)
        answers.append(count)
    return answers


def additive_oracle(args):
    digits = args[0]
    for first_end in range(1, len(digits) - 1):
        first_text = digits[:first_end]
        if len(first_text) > 1 and first_text[0] == "0":
            break
        for second_end in range(first_end + 1, len(digits)):
            second_text = digits[first_end:second_end]
            if len(second_text) > 1 and second_text[0] == "0":
                break
            left, right, index = int(first_text), int(second_text), second_end
            terms = 2
            while index < len(digits):
                next_text = str(left + right)
                if not digits.startswith(next_text, index):
                    break
                index += len(next_text)
                left, right = right, left + right
                terms += 1
            if index == len(digits) and terms >= 3:
                return True
    return False


def cooldown_oracle(args):
    prices = tuple(args[0])

    @lru_cache(None)
    def search(day, holding, cooldown):
        if day == len(prices):
            return 0 if not holding else -10**18
        if holding:
            return max(search(day + 1, True, False),
                       prices[day] + search(day + 1, False, True))
        rest = search(day + 1, False, False)
        return rest if cooldown else max(rest, -prices[day] + search(day + 1, True, False))

    return search(0, False, False)


def height_tree_oracle(args):
    node_count, edges = args
    if node_count == 1:
        return [0]
    graph = [[] for _ in range(node_count)]
    for left, right in edges:
        graph[left].append(right)
        graph[right].append(left)
    heights = []
    for root in range(node_count):
        seen, queue, height = {root}, deque([(root, 0)]), 0
        while queue:
            node, depth = queue.popleft()
            height = max(height, depth)
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, depth + 1))
        heights.append(height)
    minimum = min(heights)
    return [node for node, height in enumerate(heights) if height == minimum]


def matrix_product_oracle(args):
    left, right = args
    return [[sum(left[row][middle] * right[middle][column]
                 for middle in range(len(right)))
             for column in range(len(right[0]))]
            for row in range(len(left))]


def random_meeting(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    grid = [[int(rng.random() < .25) for _ in range(columns)] for _ in range(rows)]
    if not any(map(any, grid)):
        grid[rng.randrange(rows)][rng.randrange(columns)] = 1
    return [grid]


def random_consecutive_tree(rng):
    return [random_tree(rng, nonempty=True)]


def random_bulls(rng):
    length = rng.randint(1, 20)
    return ["".join(rng.choice("0123456789") for _ in range(length)),
            "".join(rng.choice("0123456789") for _ in range(length))]


def random_invalid_parentheses(rng):
    return ["".join(rng.choice("()ab") for _ in range(rng.randint(1, 10)))]


def random_rectangle(rng):
    rows, columns = rng.randint(1, 8), rng.randint(1, 8)
    row, column = rng.randrange(rows), rng.randrange(columns)
    black = {(row, column)}
    for _ in range(rng.randint(0, rows * columns * 2)):
        base_row, base_column = rng.choice(tuple(black))
        next_row, next_column = rng.choice(((base_row - 1, base_column),
                                             (base_row + 1, base_column),
                                             (base_row, base_column - 1),
                                             (base_row, base_column + 1)))
        if 0 <= next_row < rows and 0 <= next_column < columns:
            black.add((next_row, next_column))
    image = [["1" if (r, c) in black else "0" for c in range(columns)] for r in range(rows)]
    selected = rng.choice(tuple(black))
    return [image, selected[0], selected[1]]


def random_islands(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    positions = [[rng.randrange(rows), rng.randrange(columns)]
                 for _ in range(rng.randint(1, min(20, rows * columns + 4)))]
    return [rows, columns, positions]


def random_additive(rng):
    if rng.random() < .45:
        left, right = rng.randint(0, 99), rng.randint(0, 99)
        values = [left, right]
        while len("".join(map(str, values))) < rng.randint(3, 12):
            values.append(values[-1] + values[-2])
        return ["".join(map(str, values))[:35]]
    return ["".join(rng.choice("0123456789") for _ in range(rng.randint(1, 12)))]


def random_cooldown(rng):
    return [[rng.randint(0, 20) for _ in range(rng.randint(1, 10))]]


def random_height_tree(rng):
    node_count = rng.randint(1, 15)
    edges = [[node, rng.randrange(node)] for node in range(1, node_count)]
    rng.shuffle(edges)
    return [node_count, edges]


def random_matrix_product(rng):
    rows, middle, columns = rng.randint(1, 5), rng.randint(1, 5), rng.randint(1, 5)
    value = lambda: 0 if rng.random() < .7 else rng.randint(-5, 5)
    return [[[value() for _ in range(middle)] for _ in range(rows)],
            [[value() for _ in range(columns)] for _ in range(middle)]]


MEETING = '''\
def min_total_distance(grid):
    rows = []
    columns = []
    for row in range(len(grid)):
        for column in range(len(grid[0])):
            if grid[row][column] == 1:
                rows.append(row)
                columns.append(column)
    columns.sort()
    row_median = rows[len(rows) // 2]
    column_median = columns[len(columns) // 2]
    return sum(abs(row - row_median) for row in rows) + sum(abs(column - column_median) for column in columns)
'''


CONSECUTIVE_TREE = '''\
def longest_consecutive_tree(root):
    longest = 0
    stack = [(root, None, 0)]
    while stack:
        node, parent_value, parent_length = stack.pop()
        if node is None:
            continue
        length = parent_length + 1 if parent_value is not None and node.val == parent_value + 1 else 1
        longest = max(longest, length)
        stack.append((node.left, node.val, length))
        stack.append((node.right, node.val, length))
    return longest
'''


BULLS = '''\
def bulls_and_cows(secret, guess):
    bulls = 0
    secret_unmatched = [0] * 10
    guess_unmatched = [0] * 10
    for left, right in zip(secret, guess):
        if left == right:
            bulls += 1
        else:
            secret_unmatched[ord(left) - 48] += 1
            guess_unmatched[ord(right) - 48] += 1
    cows = sum(min(left, right) for left, right in zip(secret_unmatched, guess_unmatched))
    return f"{bulls}A{cows}B"
'''


REMOVE_INVALID = '''\
def remove_invalid_parentheses(s):
    answers = []

    def remove(text, scan_start, removal_start, opening, closing):
        balance = 0
        for index in range(scan_start, len(text)):
            if text[index] == opening:
                balance += 1
            elif text[index] == closing:
                balance -= 1
            if balance >= 0:
                continue
            for remove_at in range(removal_start, index + 1):
                if (text[remove_at] == closing
                        and (remove_at == removal_start or text[remove_at - 1] != closing)):
                    remove(text[:remove_at] + text[remove_at + 1:], index, remove_at, opening, closing)
            return
        reversed_text = text[::-1]
        if opening == "(":
            remove(reversed_text, 0, 0, ")", "(")
        else:
            answers.append(reversed_text)

    remove(s, 0, 0, "(", ")")
    return answers
'''


RECTANGLE = '''\
def smallest_black_rectangle(image, x, y):
    rows, columns = len(image), len(image[0])

    def row_has_black(row):
        return any(value == "1" for value in image[row])

    def column_has_black(column):
        return any(image[row][column] == "1" for row in range(rows))

    def first_true(low, high, predicate):
        while low < high:
            middle = (low + high) // 2
            if predicate(middle):
                high = middle
            else:
                low = middle + 1
        return low

    def first_false(low, high, predicate):
        while low < high:
            middle = (low + high) // 2
            if predicate(middle):
                low = middle + 1
            else:
                high = middle
        return low

    top = first_true(0, x + 1, row_has_black)
    bottom = first_false(x, rows, row_has_black)
    left = first_true(0, y + 1, column_has_black)
    right = first_false(y, columns, column_has_black)
    return (bottom - top) * (right - left)
'''


ISLANDS = '''\
def count_islands_after_additions(m, n, positions):
    parent = {}
    size = {}
    islands = 0
    answers = []

    def find(cell):
        while parent[cell] != cell:
            parent[cell] = parent[parent[cell]]
            cell = parent[cell]
        return cell

    for row, column in positions:
        cell = (row, column)
        if cell in parent:
            answers.append(islands)
            continue
        parent[cell] = cell
        size[cell] = 1
        islands += 1
        for neighbor in ((row - 1, column), (row + 1, column),
                         (row, column - 1), (row, column + 1)):
            if neighbor not in parent:
                continue
            left, right = find(cell), find(neighbor)
            if left == right:
                continue
            if size[left] < size[right]:
                left, right = right, left
            parent[right] = left
            size[left] += size[right]
            islands -= 1
        answers.append(islands)
    return answers
'''


ADDITIVE = '''\
def is_additive_number(num):
    length = len(num)
    for first_end in range(1, length - 1):
        if num[0] == "0" and first_end > 1:
            break
        first_value = int(num[:first_end])
        for second_end in range(first_end + 1, length):
            if num[first_end] == "0" and second_end > first_end + 1:
                break
            first, second = first_value, int(num[first_end:second_end])
            index = second_end
            while index < length:
                expected = str(first + second)
                if not num.startswith(expected, index):
                    break
                index += len(expected)
                first, second = second, first + second
            if index == length:
                return True
    return False
'''


COOLDOWN = '''\
def max_profit_with_cooldown(prices):
    holding = -prices[0]
    sold = 0
    resting = 0
    for price in prices[1:]:
        previous_holding, previous_sold, previous_resting = holding, sold, resting
        holding = max(previous_holding, previous_resting - price)
        sold = previous_holding + price
        resting = max(previous_resting, previous_sold)
    return max(sold, resting)
'''


MIN_HEIGHT = '''\
def minimum_height_tree_roots(n, edges):
    if n == 1:
        return [0]
    graph = [set() for _ in range(n)]
    for left, right in edges:
        graph[left].add(right)
        graph[right].add(left)
    leaves = [node for node in range(n) if len(graph[node]) == 1]
    remaining = n
    while remaining > 2:
        remaining -= len(leaves)
        next_leaves = []
        for leaf in leaves:
            neighbor = graph[leaf].pop()
            graph[neighbor].remove(leaf)
            if len(graph[neighbor]) == 1:
                next_leaves.append(neighbor)
        leaves = next_leaves
    return leaves
'''


SPARSE_PRODUCT = '''\
def multiply_sparse_matrices(mat1, mat2):
    rows, columns = len(mat1), len(mat2[0])
    result = [[0] * columns for _ in range(rows)]
    for row, values in enumerate(mat1):
        for middle, left_value in enumerate(values):
            if left_value == 0:
                continue
            for column, right_value in enumerate(mat2[middle]):
                if right_value != 0:
                    result[row][column] += left_value * right_value
    return result
'''


MEAN_MEETING_WRONG = '''\
def min_total_distance(grid):
    homes = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value]
    row = round(sum(r for r, _ in homes) / len(homes))
    column = round(sum(c for _, c in homes) / len(homes))
    return sum(abs(r - row) + abs(c - column) for r, c in homes)
'''


MIDPOINT_MEETING_WRONG = '''\
def min_total_distance(grid):
    homes = [(r, c) for r, row in enumerate(grid) for c, value in enumerate(row) if value]
    row = (min(r for r, _ in homes) + max(r for r, _ in homes)) // 2
    column = (min(c for _, c in homes) + max(c for _, c in homes)) // 2
    return sum(abs(r - row) + abs(c - column) for r, c in homes)
'''


GLOBAL_CONSECUTIVE_WRONG = '''\
def longest_consecutive_tree(root):
    values, stack = set(), [root]
    while stack:
        node = stack.pop()
        if node:
            values.add(node.val)
            stack.extend((node.left, node.right))
    return max((sum(start + offset in values for offset in range(len(values)))
                for start in values), default=0)
'''


BIDIRECTIONAL_CONSECUTIVE_WRONG = CONSECUTIVE_TREE.replace(
    'node.val == parent_value + 1', 'abs(node.val - parent_value) == 1')


UNIQUE_BULLS_WRONG = '''\
def bulls_and_cows(secret, guess):
    bulls = sum(left == right for left, right in zip(secret, guess))
    shared = len(set(secret) & set(guess))
    return f"{bulls}A{shared - bulls}B"
'''


OVERCOUNT_BULLS_WRONG = '''\
def bulls_and_cows(secret, guess):
    bulls = sum(left == right for left, right in zip(secret, guess))
    cows = sum(character in secret for index, character in enumerate(guess) if character != secret[index])
    return f"{bulls}A{cows}B"
'''


GREEDY_INVALID_WRONG = '''\
def remove_invalid_parentheses(s):
    kept = []
    balance = 0
    for character in s:
        if character == "(" :
            balance += 1
            kept.append(character)
        elif character == ")":
            if balance:
                balance -= 1
                kept.append(character)
        else:
            kept.append(character)
    while balance:
        kept.pop(len(kept) - 1 - kept[::-1].index("("))
        balance -= 1
    return ["".join(kept)]
'''


ONE_REMOVAL_WRONG = '''\
def remove_invalid_parentheses(s):
    if valid(s):
        return [s]
    answers = set()
    for index, character in enumerate(s):
        if character in "()":
            candidate = s[:index] + s[index + 1:]
            if valid(candidate):
                answers.add(candidate)
    return list(answers)

def valid(text):
    balance = 0
    for character in text:
        balance += character == "(" 
        balance -= character == ")"
        if balance < 0:
            return False
    return balance == 0
'''


COUNT_PIXELS_WRONG = '''\
def smallest_black_rectangle(image, x, y):
    return sum(value == "1" for row in image for value in row)
'''


CROSS_SECTION_WRONG = '''\
def smallest_black_rectangle(image, x, y):
    columns = [column for column, value in enumerate(image[x]) if value == "1"]
    rows = [row for row in range(len(image)) if image[row][y] == "1"]
    return (max(rows) - min(rows) + 1) * (max(columns) - min(columns) + 1)
'''


DUPLICATE_ISLAND_WRONG = ISLANDS.replace(
    'if cell in parent:\n            answers.append(islands)\n            continue',
    'if cell in parent:\n            islands += 1\n            answers.append(islands)\n            continue')


FIRST_NEIGHBOR_ISLAND_WRONG = ISLANDS.replace(
    'for neighbor in ((row - 1, column), (row + 1, column),\n                         (row, column - 1), (row, column + 1)):',
    'for neighbor in ((row - 1, column), (row + 1, column),\n                         (row, column - 1), (row, column + 1))[:1]:')


LEADING_ZERO_ADDITIVE_WRONG = ADDITIVE.replace(
    'if num[0] == "0" and first_end > 1:\n            break',
    'if False:\n            break').replace(
    'if num[first_end] == "0" and second_end > first_end + 1:\n                break',
    'if False:\n                break')


FIRST_DIGITS_ADDITIVE_WRONG = '''\
def is_additive_number(num):
    if len(num) < 3:
        return False
    left, right, index = int(num[0]), int(num[1]), 2
    while index < len(num):
        expected = str(left + right)
        if not num.startswith(expected, index):
            return False
        index += len(expected)
        left, right = right, left + right
    return True
'''


UNLIMITED_STOCK_WRONG = '''\
def max_profit_with_cooldown(prices):
    return sum(max(0, right - left) for left, right in zip(prices, prices[1:]))
'''


ONE_TRADE_STOCK_WRONG = '''\
def max_profit_with_cooldown(prices):
    lowest = prices[0]
    answer = 0
    for price in prices[1:]:
        answer = max(answer, price - lowest)
        lowest = min(lowest, price)
    return answer
'''


INITIAL_LEAVES_WRONG = '''\
def minimum_height_tree_roots(n, edges):
    if n == 1:
        return [0]
    degree = [0] * n
    for left, right in edges:
        degree[left] += 1
        degree[right] += 1
    return [node for node in range(n) if degree[node] == 1]
'''


MIN_DEGREE_WRONG = '''\
def minimum_height_tree_roots(n, edges):
    degree = [0] * n
    for left, right in edges:
        degree[left] += 1
        degree[right] += 1
    minimum = min(degree)
    return [node for node in range(n) if degree[node] == minimum]
'''


ELEMENTWISE_PRODUCT_WRONG = '''\
def multiply_sparse_matrices(mat1, mat2):
    return [[mat1[row][column] * mat2[row][column]
             for column in range(len(mat2[0]))]
            for row in range(len(mat1))]
'''


ADDITION_PRODUCT_WRONG = '''\
def multiply_sparse_matrices(mat1, mat2):
    return [[sum(mat1[row][middle] + mat2[middle][column]
                 for middle in range(len(mat2)))
             for column in range(len(mat2[0]))]
            for row in range(len(mat1))]
'''


large_meeting = [[0] * 200 for _ in range(200)]
for large_row, large_column in ((0, 0), (0, 199), (199, 0), (199, 199), (100, 100)):
    large_meeting[large_row][large_column] = 1
large_black_image = [["0"] * 100 for _ in range(100)]
for large_index in range(100):
    large_black_image[0][large_index] = "1"
    large_black_image[large_index][99] = "1"
large_positions = [[row, column] for row in range(100) for column in range(100)]
large_prices = list(range(5_000))
large_path_edges = [[node - 1, node] for node in range(1, 20_000)]
large_sparse_left = [[0] * 100 for _ in range(100)]
large_sparse_right = [[0] * 100 for _ in range(100)]
large_sparse_expected = [[0] * 100 for _ in range(100)]
for large_index in range(100):
    large_sparse_left[large_index][large_index] = large_index
    large_sparse_right[large_index][large_index] = 2
    large_sparse_expected[large_index][large_index] = large_index * 2


BATCH = {
    296: entry(
        "min_total_distance", [("grid", "list[list[int]]")], "int",
        ["matrices", "math", "sorting", "medians"],
        [
            "grid is a rectangular 1–200 by 1–200 matrix containing only 0 and 1, with at least one home marked 1.",
            "Return the minimum sum of four-direction Manhattan distances from every home to one meeting cell. The meeting cell may be any grid cell.",
        ],
        [
            ([[[1,0,0,0,1],[0,0,0,0,0],[0,0,1,0,0]]], "Choosing row 0 and column 2 gives distances 2, 2, and 2, for the minimum total 6."),
            ([[[1,0,0,0,0,1]]], "Any cell between the two endpoint homes has total distance 5, so the minimum is 5."),
        ],
        [[grid] for grid in (
            [[1]], [[1,1]], [[1,0,1]], [[1],[0],[1]], [[1,0],[0,1]],
            [[1,1,1],[0,0,0]], [[1,0,0],[1,0,0],[1,0,1]],
            [[0,1,0],[1,0,1],[0,1,0]], [[1,0,0,0],[0,0,0,1]],
            [[1,1,0,0,0,1]], [[1,0],[1,0],[0,0],[1,1]],
            [[0,0,1],[0,0,0],[1,0,0],[1,0,0]], [[1,0,1],[0,1,0]],
        )],
        MEETING, [MEAN_MEETING_WRONG, MIDPOINT_MEETING_WRONG],
        [
            "Uses the arithmetic mean, but absolute distances are minimized by a median; an outlying home can move the mean away from every optimum.",
            "Uses the midpoint of the extreme homes, which ignores how many homes lie on either side and can differ from the median.",
        ],
        meeting_oracle, random_meeting,
        [
            "Manhattan distance separates into an independent row distance plus an independent column distance.",
            "For one-dimensional absolute distances, every median minimizes the total; the mean is not generally optimal.",
            "Collect all home rows in row-major order and collect/sort all home columns. Sum distances to the median of each list.",
            "Row-major scanning already sorts row coordinates. Sorting only the columns gives O(h log h), where h is the number of homes.",
        ],
        "For any meeting cell (r,c), the total is the sum of |home_row-r| plus the separate sum of |home_column-c|. A median minimizes each one-dimensional absolute-distance sum, so choosing the row median and column median is globally optimal. Row-major traversal yields sorted rows; columns are sorted explicitly. The independent oracle evaluates every possible meeting cell on small generated grids.",
        "O(mn + h log h)", "O(h)", difficulty=8,
        stress=[([large_meeting], meeting_oracle([large_meeting]))],
    ),
    298: entry(
        "longest_consecutive_tree", [("root", "TreeNode")], "int",
        ["trees", "depth-first-search", "recursion"],
        [
            "root is a nonempty binary tree containing at most 30000 nodes with integer values from -30000 through 30000.",
            "Return the greatest number of nodes on a downward parent-to-child path whose values increase by exactly one at every step. The path may start at any node and cannot move from a child to its parent.",
        ],
        [
            ([[1,None,3,2,4,None,None,None,5]], "The downward path 3→4→5 increases by exactly one and has length 3; node 2 is not a child after 1 in that direction."),
            ([[2,3,2,None,4,None,1]], "The left branch 2→3→4 is consecutive, while the right branch decreases and starts a separate length-one run."),
        ],
        [[tree] for tree in (
            [1], [1,2], [2,1], [1,None,2,None,3], [3,2,4,1,None,None,5],
            [1,2,3,3,4,2,4], [5,6,6,7,None,None,7], [0,-1,1,-2,None,None,2],
            [1,3,2,4,None,None,3], [10,11,None,12], [1,2,2,3,None,None,3],
            [4,5,3,6,None,None,2], [7,7,8,8,9], [1,None,3,2,4],
        )],
        CONSECUTIVE_TREE, [GLOBAL_CONSECUTIVE_WRONG, BIDIRECTIONAL_CONSECUTIVE_WRONG],
        [
            "Counts consecutive values anywhere in the tree even when those values do not form one downward parent-child path.",
            "Allows values to decrease by one, although the required path must increase from parent to child.",
        ],
        consecutive_tree_oracle, random_consecutive_tree,
        [
            "At each node, only its parent value and the run length ending at that parent are needed.",
            "Extend the run when node.val equals parent.val+1; otherwise restart the run at one.",
            "Traverse every node with a stack or recursion, pass the current value and run length to both children, and maintain a global maximum.",
            "A path may begin below the root, so restarting rather than discarding a broken branch is essential.",
        ],
        "Each node has exactly one parent, so the best consecutive path ending there is determined by one comparison with that parent. Extend the inherited length only for value+1; otherwise the node begins a new path of length one. Visiting every node and tracking the largest length covers paths that start anywhere. The independent compact-tree oracle computes the run ending at each stored path by walking its ancestors.",
        "O(n)", "O(h)", difficulty=5,
        stress=[([right_chain(10_000)], 10_000)],
    ),
    299: entry(
        "bulls_and_cows", [("secret", "str"), ("guess", "str")], "str",
        ["strings", "hash-maps", "counting"],
        [
            "secret and guess contain the same 1–1000 number of decimal digits; repeated digits and leading zeroes are allowed.",
            "Return a hint formatted as xAyB. A bull is an equal digit at the same index; a cow is a remaining equal digit matched at a different index. Each occurrence can be used at most once.",
        ],
        [
            (["1807", "7810"], "Digit 8 is the one bull. Digits 1, 0, and 7 match at different positions, giving 1A3B."),
            (["1123", "0111"], "The second digit is a bull and only one remaining 1 can be matched as a cow, so duplicates are capped at 1A1B."),
        ],
        [[secret, guess] for secret, guess in (
            ("1","1"),("1","0"),("01","10"),("11","11"),("11","10"),
            ("1122","2211"),("1122","0001"),("0000","0000"),("0123","0123"),
            ("1234","4321"),("1231","1111"),("987667","678976"),("0012","1200"),
            ("99990","09999"),("1234567890","0987654321"),
        )],
        BULLS, [UNIQUE_BULLS_WRONG, OVERCOUNT_BULLS_WRONG],
        [
            "Uses sets, which lose duplicate counts and can even subtract too many bulls from the shared-digit total.",
            "Counts every misplaced guess occurrence whose digit appears somewhere in secret, reusing a secret occurrence multiple times.",
        ],
        bulls_oracle, random_bulls,
        [
            "Separate same-position matches before counting misplaced digits.",
            "For each digit, the number of cows is the smaller unmatched frequency in secret and guess.",
            "Scan the strings once into two ten-slot frequency arrays, skipping bull positions, then sum per-digit minima.",
            "Removing bulls first prevents one occurrence from being counted both as a bull and as a cow.",
        ],
        "A same-index match is reserved as a bull. Every remaining occurrence of digit d can participate in at most one cow, so exactly min(unmatched_secret[d], unmatched_guess[d]) copies match. Ten fixed counters make the scan linear and constant-space. The independent oracle intersects full Counters, subtracting the already identified bulls from the total shared multiplicity.",
        "O(n)", "O(1)", difficulty=5,
        stress=[(["0123456789" * 100, "9876543210" * 100], bulls_oracle(["0123456789" * 100, "9876543210" * 100]))],
    ),
    301: entry(
        "remove_invalid_parentheses", [("s", "str")], "list[str]",
        ["strings", "backtracking", "recursion", "breadth-first-search"],
        [
            "s contains 1–25 lowercase English letters and parentheses.",
            "Remove the fewest parentheses needed to make s valid. Return every distinct result that uses that minimum number of removals, in any order. Letters cannot be removed.",
        ],
        [
            (["()())()"], "Removing either of the duplicate middle closing parentheses produces the two distinct minimum results (())() and ()()()."),
            (["(a)())()"], "Letters remain fixed; the two minimum valid results are (a())() and (a)()()."),
        ],
        [[text] for text in (
            "(", ")", "()", "(a)", ")(", "(()", "())", "()()", "((a))",
            "(a))(", "n", "a)b(c)d", "(((k()", "(()))(", "a((b)c))d(",
        )],
        REMOVE_INVALID, [GREEDY_INVALID_WRONG, ONE_REMOVAL_WRONG],
        [
            "Returns only one greedy repair, missing other distinct strings with the same minimum number of removals.",
            "Tries deleting only one parenthesis, so it returns no answer when validity requires two or more removals.",
        ],
        invalid_parentheses_oracle, random_invalid_parentheses,
        [
            "When a left-to-right balance first becomes negative, some closing parenthesis at or before that index must be removed.",
            "Try each distinct closing parenthesis in that prefix, recurse, and stop the current scan; skipping equal adjacent removals avoids duplicate answers.",
            "After the forward scan has no surplus closing parenthesis, reverse the text and repeat with the parenthesis roles swapped to remove surplus opening parentheses.",
            "Only removals forced by the first imbalance are explored, so every final result uses the minimum count while letters remain untouched.",
        ],
        "The two-pass recursive removal algorithm waits until the first invalid prefix. Every valid minimum repair must delete one closing parenthesis from that prefix, so branching only there is complete and never removes an unnecessary character. Duplicate equal deletions are skipped. Reversing the surviving text and swapping the roles applies the same proof to excess opening parentheses. The independent oracle enumerates all parenthesis subsets on short generated strings, retains valid strings of maximum length, and compares the complete set.",
        "O(2^p · n) worst case", "O(n) recursion excluding output", difficulty=8,
        stress=[([")" * 12 + "a" + "(" * 12], ["a"])],
    ),
    302: entry(
        "smallest_black_rectangle", [("image", "list[list[str]]"), ("x", "int"), ("y", "int")], "int",
        ["matrices", "binary-search", "geometry"],
        [
            "image is a rectangular 1–100 by 1–100 matrix of strings '0' and '1'. All black pixels form one four-direction connected region, and image[x][y] is '1'.",
            "Return the area of the smallest axis-aligned rectangle containing every black pixel. The target running time must be better than scanning all mn cells.",
        ],
        [
            ([[["0","0","1","0"],["0","1","1","0"],["0","1","0","0"]],0,2], "Black rows span 0..2 and columns span 1..2, so the enclosing rectangle has area 3×2=6."),
            ([[["1","0"],["1","1"]],0,0], "The connected L shape reaches both rows and both columns; its enclosing rectangle has area 4 even though only three pixels are black."),
        ],
        [[image, x, y] for image, x, y in (
            ([["1"]],0,0), ([["1","1"]],0,1), ([["1"],["1"]],1,0),
            ([["0","1","0"]],0,1), ([["0"],["1"],["0"]],1,0),
            ([["1","1"],["0","1"]],0,0), ([["0","1"],["1","1"]],1,0),
            ([["0","1","0"],["1","1","1"]],0,1),
            ([["1","0","0"],["1","1","1"]],0,0),
            ([["0","0","1"],["1","1","1"]],0,2),
            ([["0","1","0"],["0","1","0"],["1","1","0"]],2,0),
            ([["1","1","1"],["0","0","1"],["0","0","1"]],0,1),
            ([["0","0","0"],["0","1","0"],["0","0","0"]],1,1),
            ([["1","1","0"],["0","1","1"],["0","0","1"]],1,1),
        )],
        RECTANGLE, [COUNT_PIXELS_WRONG, CROSS_SECTION_WRONG],
        [
            "Returns the number of black pixels, which differs from the bounding rectangle area when the connected region has holes or bends.",
            "Examines only the selected pixel's row and column, missing black pixels reached after the connected region turns.",
        ],
        rectangle_oracle, random_rectangle,
        [
            "Connectivity guarantees that the set of rows containing black is one interval, and the same is true for columns.",
            "Use the known black row x and column y to split four monotone searches: first/last black row and first/last black column.",
            "Binary-search whether a candidate row contains any black pixel; repeat for columns, then multiply the boundary differences.",
            "Each row probe scans n cells and each column probe scans m, giving O(m log n+n log m), which is below O(mn) for the intended dimensions.",
        ],
        "A four-direction connected black region cannot skip an entire row or column between two occupied ones, so occupied rows and columns each form contiguous intervals. The known black pixel lies inside both intervals. Binary searches find their lower and exclusive upper boundaries using row/column existence probes. Their spans determine the rectangle. The independent oracle scans every generated cell and directly takes minimum and maximum coordinates.",
        "O(m log n + n log m)", "O(1)", difficulty=8,
        stress=[([large_black_image,0,0], 10_000)],
    ),
    305: entry(
        "count_islands_after_additions", [("m", "int"), ("n", "int"), ("positions", "list[list[int]]")], "list[int]",
        ["graphs", "matrices", "union-find"],
        [
            "m and n are from 1 through 10000. positions contains 1–10000 valid [row,column] cells and may repeat a cell.",
            "The m×n grid starts as water. After each position is changed to land, append the current number of four-direction islands. Re-adding existing land leaves the count unchanged.",
        ],
        [
            ([3,3,[[0,0],[0,1],[1,2],[2,1]]], "The additions form one joined pair followed by two separate cells, so the island counts are 1,1,2,3."),
            ([1,2,[[0,0],[0,0],[0,1]]], "The repeated first cell changes nothing, and the last cell joins it, so every reported count is 1."),
        ],
        [[m,n,positions] for m,n,positions in (
            (1,1,[[0,0]]), (1,1,[[0,0],[0,0]]), (1,3,[[0,0],[0,2],[0,1]]),
            (3,1,[[0,0],[2,0],[1,0]]), (2,2,[[0,0],[1,1]]),
            (2,2,[[0,0],[0,1],[1,0],[1,1]]), (3,3,[[0,1],[1,0],[1,2],[2,1],[1,1]]),
            (3,4,[[0,0],[0,3],[2,0],[2,3],[1,1],[1,2]]),
            (4,4,[[1,1],[1,2],[2,1],[2,2],[0,0]]),
            (2,3,[[0,0],[0,2],[1,1],[0,1]]), (5,5,[[2,2],[2,3],[3,2],[1,2],[2,2]]),
            (3,3,[[0,0],[0,2],[2,0],[2,2],[1,1]]),
            (4,3,[[0,1],[1,1],[2,1],[3,1],[2,0],[2,2]]),
        )],
        ISLANDS, [DUPLICATE_ISLAND_WRONG, FIRST_NEIGHBOR_ISLAND_WRONG],
        [
            "Treats a repeated position as new land and increments the count even though the grid state did not change.",
            "Checks only one neighboring direction, so it misses merges through the other three sides.",
        ],
        islands_oracle, random_islands,
        [
            "Only added land cells need storage; the full m×n grid can remain implicit.",
            "Create one disjoint-set component for a new cell, then union it with every active four-direction neighbor.",
            "Increase the island count for a genuinely new cell and decrease it once for each union of two different roots. Append unchanged count for duplicates.",
            "Path compression and union by size make each operation nearly constant amortized time while preserving the count invariant.",
        ],
        "Each active cell is one disjoint-set node. A new node initially creates one island. Every union with a distinct adjacent root merges two islands and subtracts one; repeated positions and already-connected neighbors do not change the count. Sparse dictionaries avoid allocating m×n when few cells are added. The independent oracle rebuilds connected components directly after every operation on small generated grids.",
        "O(k α(k))", "O(k)", difficulty=8,
        stress=[([100,100,large_positions], [1] * len(large_positions))],
    ),
    306: entry(
        "is_additive_number", [("num", "str")], "bool",
        ["strings", "backtracking", "math"],
        [
            "num contains 1–35 decimal digits.",
            "Return whether all digits can be split into at least three integers where every integer after the first two equals their sum. No multi-digit integer may start with zero.",
        ],
        [
            (["112358"], "The complete split 1,1,2,3,5,8 is additive because each term is the sum of the preceding two."),
            (["1023"], "The tempting split 1,02,3 is forbidden by the leading zero, and no other complete additive split exists."),
        ],
        [[digits] for digits in (
            "1", "12", "000", "101", "111", "112", "123", "199100199", "1203",
            "0235813", "011235", "12122436", "8917", "999", "101202303", "198019823962",
        )],
        ADDITIVE, [LEADING_ZERO_ADDITIVE_WRONG, FIRST_DIGITS_ADDITIVE_WRONG],
        [
            "Parses multi-digit values with leading zeroes, accepting sequences that the contract forbids.",
            "Fixes the first two terms to one digit each, missing valid sequences whose first or second term has multiple digits.",
        ],
        additive_oracle, random_additive,
        [
            "Once the first two numbers are chosen, every later number is forced.",
            "Enumerate the two initial split points, rejecting a multi-digit part that begins with zero.",
            "Repeatedly form str(first+second) and require it at the current index, then shift the pair forward.",
            "Accept only when the forced sequence consumes every digit; matching a prefix is not sufficient.",
        ],
        "Every valid sequence is uniquely determined by its first two boundaries. For each legal pair, generate the decimal text of the required sum and match it at the next position. A mismatch ends that pair; consuming the whole string proves a sequence of at least three terms because both initial boundaries leave a suffix. The independent oracle uses separately structured split loops and the same arithmetic definition on 500 seeded strings.",
        "O(n³)", "O(n)", difficulty=5,
        stress=[(["1" * 35], False)],
    ),
    309: entry(
        "max_profit_with_cooldown", [("prices", "list[int]")], "int",
        ["arrays", "dynamic-programming", "state-machines"],
        [
            "prices contains 1–5000 integers from 0 through 1000.",
            "Return the maximum profit from any number of buy/sell transactions. You may hold at most one share, must sell before buying again, and cannot buy on the day immediately after a sale.",
        ],
        [
            ([[1,2,3,0,2]], "Buy at 1, sell at 2, cool down, then buy at 0 and sell at 2 for total profit 3."),
            ([[1]], "With no later day to sell, the maximum profit is 0."),
        ],
        [[prices] for prices in (
            [1,2], [2,1], [1,2,3], [3,2,1], [1,3,2,4], [2,1,4], [6,1,6,4,3,0,2],
            [1,2,4,0,2], [2,4,1,7], [0,0,0], [0,1,0,1], [5,1,2,3,0,4],
            [1,4,2,7,0,3], [3,3,5,0,0,3,1,4], [10,1,10,1,10],
        )],
        COOLDOWN, [UNLIMITED_STOCK_WRONG, ONE_TRADE_STOCK_WRONG],
        [
            "Adds every positive adjacent rise as if a sale could be followed by an immediate next-day purchase.",
            "Allows only one transaction and misses profit from separated transactions with a legal cooldown day.",
        ],
        cooldown_oracle, random_cooldown,
        [
            "At the end of each day, the relevant states are holding a share, just sold, or resting without a share.",
            "A new holding state can come only from an earlier holding state or yesterday's resting state, not yesterday's sold state.",
            "Update holding=max(old_holding,old_rest-price), sold=old_holding+price, and rest=max(old_rest,old_sold).",
            "The answer is max(sold,rest); ending while holding cannot realize that share's value as profit.",
        ],
        "The three states encode exactly the one-day restriction. Buying is permitted only from rest, selling is permitted only from hold, and a sold state flows into rest on the following day. Keeping only the previous day's values makes the DP constant-space. The independent oracle recursively explores buy, sell, and wait actions with explicit holding/cooldown flags on short generated price lists.",
        "O(n)", "O(1)", difficulty=5,
        stress=[([large_prices], 4_999)],
    ),
    310: entry(
        "minimum_height_tree_roots", [("n", "int"), ("edges", "list[list[int]]")], "list[int]",
        ["graphs", "breadth-first-search", "topological-trimming"],
        [
            "n is from 1 through 20000. edges contains exactly n-1 undirected edges connecting all labels 0..n-1 into a tree.",
            "Return every node that gives the minimum possible tree height when chosen as root, in any order.",
        ],
        [
            ([4,[[1,0],[1,2],[1,3]]], "Root 1 reaches every leaf in one edge, while any leaf root has height two, so [1] is the answer."),
            ([6,[[3,0],[3,1],[3,2],[3,4],[5,4]]], "The tree's two centers are 3 and 4; rooting at either minimizes the maximum distance to a leaf."),
        ],
        [[n,edges] for n,edges in (
            (1,[]), (2,[[0,1]]), (3,[[0,1],[1,2]]), (4,[[0,1],[1,2],[2,3]]),
            (5,[[0,1],[1,2],[2,3],[3,4]]), (5,[[0,1],[0,2],[0,3],[0,4]]),
            (6,[[0,1],[1,2],[1,3],[3,4],[3,5]]), (7,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]]),
            (7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]]),
            (8,[[0,1],[1,2],[2,3],[3,4],[4,5],[4,6],[6,7]]),
            (9,[[0,1],[1,2],[2,3],[3,4],[2,5],[5,6],[5,7],[7,8]]),
            (10,[[0,1],[0,2],[0,3],[3,4],[3,5],[5,6],[5,7],[7,8],[7,9]]),
            (6,[[0,5],[1,5],[2,5],[3,5],[4,5]]),
        )],
        MIN_HEIGHT, [INITIAL_LEAVES_WRONG, MIN_DEGREE_WRONG],
        [
            "Returns the original leaves, which maximize rather than minimize height on paths and most branching trees.",
            "Chooses minimum-degree nodes, even though tree centers depend on global distances rather than local degree.",
        ],
        height_tree_oracle, random_height_tree,
        [
            "A tree has one or two centers, located at the middle of every longest path.",
            "Remove all current leaves simultaneously. This strips one equal-distance layer from every outside direction without changing the centers.",
            "Track neighbor sets and repeatedly enqueue nodes whose degree becomes one until at most two nodes remain.",
            "The remaining one or two labels are exactly the roots with minimum maximum depth.",
        ],
        "Layer-by-layer leaf removal is the tree analogue of trimming both ends of a path. Every longest path loses one vertex from each end per round, so its middle and the set of optimal roots are preserved. When no more than two vertices remain, they are the unique center or adjacent centers. The independent oracle roots each small generated tree at every label and directly measures its BFS height.",
        "O(n)", "O(n)", difficulty=5,
        stress=[([20_000,large_path_edges], [9_999,10_000])],
    ),
    311: entry(
        "multiply_sparse_matrices", [("mat1", "list[list[int]]"), ("mat2", "list[list[int]]")], "list[list[int]]",
        ["matrices", "hash-maps", "simulation"],
        [
            "mat1 is an m×k matrix and mat2 is a k×n matrix, with 1≤m,k,n≤100 and values from -100 through 100.",
            "Return the standard matrix product mat1×mat2. Exploit zero entries so multiplication work is concentrated on nonzero contributions.",
        ],
        [
            ([[[1,0,0],[-1,0,3]],[[7,0,0],[0,0,0],[0,0,1]]], "The nonzero products give rows [7,0,0] and [-7,0,3]."),
            ([[[0,0]],[[1],[2]]], "Every entry in the left matrix is zero, so the 1×1 product is [[0]]."),
        ],
        [[left,right] for left,right in (
            ([[1]],[[2]]), ([[0]],[[5]]), ([[-2]],[[3]]), ([[1,2]],[[3],[4]]),
            ([[1],[2]],[[3,4]]), ([[1,0],[0,1]],[[5,6],[7,8]]),
            ([[0,2],[3,0]],[[4,0],[0,5]]), ([[1,-1],[1,-1]],[[1],[1]]),
            ([[1,2,3]],[[1,0],[0,1],[1,1]]), ([[1,0],[2,3]],[[0,4,0],[5,0,6]]),
            ([[0,0,1],[0,0,0]],[[1,2],[3,4],[5,6]]),
            ([[2,-1,0],[0,3,4]],[[1,0],[2,1],[0,-1]]),
            ([[1,1],[1,1]],[[1,1],[1,1]]),
        )],
        SPARSE_PRODUCT, [ELEMENTWISE_PRODUCT_WRONG, ADDITION_PRODUCT_WRONG],
        [
            "Multiplies same-coordinate entries elementwise instead of taking row-by-column dot products.",
            "Adds paired entries inside each dot product rather than multiplying them before summing.",
        ],
        matrix_product_oracle, random_matrix_product,
        [
            "Each nonzero mat1[row][middle] contributes to every nonzero value in mat2[middle].",
            "Initialize an m×n zero result and skip an entire inner row contribution whenever the left factor is zero.",
            "For each nonzero left value, scan the matching row of mat2 and add left_value×right_value to result[row][column].",
            "The accumulation is still standard matrix multiplication; skipping zero factors changes only the work performed, not the sum.",
        ],
        "The product entry (i,j) sums mat1[i][t]×mat2[t][j] over the shared dimension. Reordering those sums by each nonzero left factor lets one update all affected output columns while skipping zero work. A second zero check avoids multiplying by sparse right entries. The independent oracle uses the direct three-loop row/column definition on generated matrices.",
        "O(mkn) worst case; proportional to nonzero contributions", "O(mn) output", difficulty=5,
        stress=[([large_sparse_left,large_sparse_right], large_sparse_expected)],
    ),
}


for problem_id in (301, 310):
    BATCH[problem_id]["comparator"] = "unordered"
BATCH[298]["params"] = [("root", "TreeNode", "treenode")]
