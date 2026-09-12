"""Flexible in-place arrays, recursive games, selected trees, grids, and cycles."""
from collections import Counter, deque
from itertools import combinations, product

from .import_batch_003 import entry
from .import_batch_024 import flatten_tree, right_chain, tree_positions


INF = 2**31 - 1


def wiggle_oracle(args):
    values = sorted(args[0])
    for index in range(1, len(values) - 1, 2):
        values[index], values[index + 1] = values[index + 1], values[index]
    return values


def expression_oracle(args):
    digits, target = args
    answers = []
    for cuts in range(1 << (len(digits) - 1)):
        parts, start = [], 0
        for index in range(len(digits) - 1):
            if cuts & (1 << index):
                parts.append(digits[start:index + 1])
                start = index + 1
        parts.append(digits[start:])
        if any(len(part) > 1 and part[0] == "0" for part in parts):
            continue
        numbers = list(map(int, parts))
        for operators in product("+-*", repeat=len(parts) - 1):
            total, current = 0, numbers[0]
            for operator, number in zip(operators, numbers[1:]):
                if operator == "*":
                    current *= number
                else:
                    total += current
                    current = number if operator == "+" else -number
            if total + current == target:
                answers.append(parts[0] + "".join(operator + part for operator, part in zip(operators, parts[1:])))
    return answers


def move_zeroes_oracle(args):
    values = args[0]
    nonzero = [value for value in values if value != 0]
    return nonzero + [0] * (len(values) - len(nonzero))


def successor_oracle(args):
    tree, selected = args
    larger = [value for value in tree_positions(tree).values() if value > selected]
    return min(larger) if larger else None


def walls_and_gates_oracle(args):
    original = args[0]
    rows, columns = len(original), len(original[0])
    result = [row[:] for row in original]
    for start_row in range(rows):
        for start_column in range(columns):
            if original[start_row][start_column] != INF:
                continue
            queue = deque([(start_row, start_column, 0)])
            seen = {(start_row, start_column)}
            while queue:
                row, column, distance = queue.popleft()
                if original[row][column] == 0:
                    result[start_row][start_column] = distance
                    break
                for next_row, next_column in ((row - 1, column), (row + 1, column),
                                              (row, column - 1), (row, column + 1)):
                    if (0 <= next_row < rows and 0 <= next_column < columns
                            and original[next_row][next_column] != -1
                            and (next_row, next_column) not in seen):
                        seen.add((next_row, next_column))
                        queue.append((next_row, next_column, distance + 1))
    return result


def duplicate_oracle(args):
    return next(value for value, count in Counter(args[0]).items() if count > 1)


def life_oracle(args):
    board = args[0]
    rows, columns = len(board), len(board[0])
    result = [[0] * columns for _ in range(rows)]
    for row in range(rows):
        for column in range(columns):
            neighbors = sum(
                board[other_row][other_column]
                for other_row in range(max(0, row - 1), min(rows, row + 2))
                for other_column in range(max(0, column - 1), min(columns, column + 2))
                if (other_row, other_column) != (row, column)
            )
            result[row][column] = int(neighbors == 3 or board[row][column] == 1 and neighbors == 2)
    return result


def word_pattern_oracle(args):
    pattern, text = args
    if len(pattern) > len(text):
        return False
    for cuts in combinations(range(1, len(text)), len(pattern) - 1):
        boundaries = (0,) + cuts + (len(text),)
        pieces = [text[boundaries[index]:boundaries[index + 1]] for index in range(len(pattern))]
        forward, backward, valid = {}, {}, True
        for character, piece in zip(pattern, pieces):
            if ((character in forward and forward[character] != piece)
                    or (piece in backward and backward[piece] != character)):
                valid = False
                break
            forward[character] = piece
            backward[piece] = character
        if valid:
            return True
    return False


def nim_oracle(args):
    stones = args[0]
    winning = [False] * (stones + 1)
    for count in range(1, stones + 1):
        winning[count] = any(not winning[count - take] for take in range(1, min(3, count) + 1))
    return winning[stones]


def flip_moves_oracle(args):
    state = args[0]
    return [state[:index] + "--" + state[index + 2:]
            for index in range(len(state) - 1) if state[index:index + 2] == "++"]


def flip_win_oracle(args):
    memo = {}
    def wins(state):
        if state in memo:
            return memo[state]
        memo[state] = any(not wins(next_state) for next_state in flip_moves_oracle([state]))
        return memo[state]
    return wins(args[0])


def flip_grundy_wins(state):
    maximum = max((len(run) for run in state.split("-") if run), default=0)
    grundy = [0] * (maximum + 1)
    for length in range(2, maximum + 1):
        reachable = {grundy[left] ^ grundy[length - left - 2]
                     for left in range(length - 1)}
        value = 0
        while value in reachable:
            value += 1
        grundy[length] = value
    outcome = 0
    for run in state.split("-"):
        outcome ^= grundy[len(run)]
    return outcome != 0


def random_wiggle(rng):
    return [[rng.randint(-100, 100) for _ in range(rng.randint(1, 30))]]


def random_expression(rng):
    length = rng.randint(1, 7)
    return ["".join(rng.choice("0123456789") for _ in range(length)), rng.randint(-30, 30)]


def random_move_zeroes(rng):
    return [[rng.randint(-5, 5) for _ in range(rng.randint(1, 50))]]


def random_bst_successor(rng):
    values = rng.sample(range(-1000, 1001), rng.randint(1, 30))
    mapping = {}
    for value in values:
        path = ()
        while path in mapping:
            path += (0 if value < mapping[path] else 1,)
        mapping[path] = value
    return [flatten_tree(mapping), rng.choice(values)]


def random_rooms(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    choices = [INF, INF, INF, -1, 0]
    return [[[rng.choice(choices) for _ in range(columns)] for _ in range(rows)]]


def random_duplicate(rng):
    maximum = rng.randint(1, 30)
    duplicate = rng.randint(1, maximum)
    repetitions = rng.randint(2, maximum + 1)
    others = rng.sample([value for value in range(1, maximum + 1) if value != duplicate],
                        maximum + 1 - repetitions)
    values = [duplicate] * repetitions + others
    rng.shuffle(values)
    return [values]


def random_life(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randint(0, 1) for _ in range(columns)] for _ in range(rows)]]


def random_word_pattern(rng):
    length = rng.randint(1, 5)
    pattern = "".join(rng.choice("abc") for _ in range(length))
    text = "".join(rng.choice("abc") for _ in range(rng.randint(length, 10)))
    return [pattern, text]


def random_nim(rng):
    return [rng.randint(1, 200)]


def random_flip(rng, maximum=20):
    return ["".join(rng.choice("+-") for _ in range(rng.randint(1, maximum)))]


def random_flip_win(rng):
    return random_flip(rng, 12)


WIGGLE = '''\
def wiggle_sort(nums):
    for index in range(1, len(nums)):
        wrong = nums[index - 1] > nums[index] if index % 2 else nums[index - 1] < nums[index]
        if wrong:
            nums[index - 1], nums[index] = nums[index], nums[index - 1]
'''


EXPRESSION = '''\
def add_operators(num, target):
    answer = []
    def build(index, expression, total, last):
        if index == len(num):
            if total == target:
                answer.append(expression)
            return
        for end in range(index + 1, len(num) + 1):
            if end > index + 1 and num[index] == "0":
                break
            token = num[index:end]
            value = int(token)
            if index == 0:
                build(end, token, value, value)
            else:
                build(end, expression + "+" + token, total + value, value)
                build(end, expression + "-" + token, total - value, -value)
                build(end, expression + "*" + token, total - last + last * value, last * value)
    build(0, "", 0, 0)
    return answer
'''


MOVE_ZEROES = '''\
def move_zeroes(nums):
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1
'''


SUCCESSOR = '''\
def inorder_successor(root, p):
    successor = None
    current = root
    while current:
        if p.val < current.val:
            successor = current
            current = current.left
        else:
            current = current.right
    return successor
'''


WALLS = '''\
def walls_and_gates(rooms):
    rows, columns = len(rooms), len(rooms[0])
    queue = deque((row, column) for row in range(rows) for column in range(columns)
                  if rooms[row][column] == 0)
    while queue:
        row, column = queue.popleft()
        for next_row, next_column in ((row - 1, column), (row + 1, column),
                                      (row, column - 1), (row, column + 1)):
            if (0 <= next_row < rows and 0 <= next_column < columns
                    and rooms[next_row][next_column] == 2147483647):
                rooms[next_row][next_column] = rooms[row][column] + 1
                queue.append((next_row, next_column))
'''


FIND_DUPLICATE = '''\
def find_duplicate(nums):
    slow = fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
'''


GAME_OF_LIFE = '''\
def game_of_life(board):
    rows, columns = len(board), len(board[0])
    for row in range(rows):
        for column in range(columns):
            live = sum(
                board[other_row][other_column] in (1, 2)
                for other_row in range(max(0, row - 1), min(rows, row + 2))
                for other_column in range(max(0, column - 1), min(columns, column + 2))
                if (other_row, other_column) != (row, column)
            )
            if board[row][column] == 1 and live not in (2, 3):
                board[row][column] = 2
            elif board[row][column] == 0 and live == 3:
                board[row][column] = 3
    for row in range(rows):
        for column in range(columns):
            board[row][column] %= 2
'''


WORD_PATTERN = '''\
def word_pattern_match(pattern, s):
    mapping = {}
    used = set()
    def match(pattern_index, text_index):
        if pattern_index == len(pattern):
            return text_index == len(s)
        remaining_pattern = len(pattern) - pattern_index - 1
        character = pattern[pattern_index]
        if character in mapping:
            value = mapping[character]
            return s.startswith(value, text_index) and match(pattern_index + 1, text_index + len(value))
        maximum_end = len(s) - remaining_pattern
        for end in range(text_index + 1, maximum_end + 1):
            value = s[text_index:end]
            if value in used:
                continue
            mapping[character] = value
            used.add(value)
            if match(pattern_index + 1, end):
                return True
            used.remove(value)
            del mapping[character]
        return False
    return match(0, 0)
'''


NIM = '''\
def can_win_nim(n):
    return n % 4 != 0
'''


FLIP_MOVES = '''\
def generate_flip_moves(current_state):
    return [current_state[:index] + "--" + current_state[index + 2:]
            for index in range(len(current_state) - 1)
            if current_state[index:index + 2] == "++"]
'''


FLIP_WIN = '''\
def can_win_flip_game(current_state):
    longest = max((len(run) for run in current_state.split("-") if run), default=0)
    grundy = [0] * (longest + 1)
    for length in range(2, longest + 1):
        reachable = {grundy[left] ^ grundy[length - left - 2]
                     for left in range(length - 1)}
        value = 0
        while value in reachable:
            value += 1
        grundy[length] = value
    outcome = 0
    for run in current_state.split("-"):
        outcome ^= grundy[len(run)]
    return outcome != 0
'''


def single_gate_wrong_source():
    return '''\
def walls_and_gates(rooms):
    rows, columns = len(rooms), len(rooms[0])
    gate = next(((r, c) for r in range(rows) for c in range(columns) if rooms[r][c] == 0), None)
    if gate is None:
        return
    queue = deque([(gate[0], gate[1], 0)])
    seen = {gate}
    while queue:
        row, column, distance = queue.popleft()
        if rooms[row][column] == 2147483647:
            rooms[row][column] = distance
        for nr, nc in ((row-1,column),(row+1,column),(row,column-1),(row,column+1)):
            if 0 <= nr < rows and 0 <= nc < columns and rooms[nr][nc] != -1 and (nr,nc) not in seen:
                seen.add((nr,nc)); queue.append((nr,nc,distance+1))
'''


large_wiggle = list(range(10_000, 0, -1))
large_move = [0 if index % 3 == 0 else index for index in range(10_000)]
large_rooms = [[INF] * 250 for _ in range(250)]
large_rooms[125][125] = 0
large_rooms_expected = [[abs(row - 125) + abs(column - 125) for column in range(250)]
                        for row in range(250)]
large_life = [[(row * 17 + column * 31) % 5 == 0 for column in range(25)] for row in range(25)]
large_life = [[int(value) for value in row] for row in large_life]
large_duplicate = list(range(1, 100_001)) + [54_321]


BATCH = {
    280: entry("wiggle_sort", [("nums", "list[int]")], "None", ["arrays", "greedy", "in-place"],
        ["nums contains 1–10000 integers from -10^9 through 10^9; duplicate values are allowed.", "Rearrange the original list into any permutation satisfying nums[0]≤nums[1]≥nums[2]≤nums[3] and so on. Return nothing."],
        [([[3,5,2,1,6,4]], "One valid in-place arrangement is 3,5,1,6,2,4, which preserves every value and alternates valley/peak comparisons."), ([[3,3,2,2]], "The arrangement 3,3,2,2 is valid because equality is allowed: 3≤3≥2≤2.")],
        [[values] for values in ([1],[2,1],[1,2],[1,2,3],[3,2,1],[1,1,1],[1,3,2,2,3,1],[-1,-3,-2,0],[4,1,1,4,2,2],[5,4,3,2,1,0],[0,1,0,1,0],[10,-10,10,-10])],
        WIGGLE, ['def wiggle_sort(nums):\n    nums.sort()\n', 'def wiggle_sort(nums):\n    for index in range(1, len(nums), 2):\n        if nums[index] < nums[index-1]: nums[index], nums[index-1] = nums[index-1], nums[index]\n'],
        ["Sorts monotonically, so a length-three increasing list has no peak at index one.", "Repairs only odd peak positions and can leave a later even valley above its predecessor."], wiggle_oracle, random_wiggle,
        ["Each adjacent comparison can be repaired locally without sorting the entire list.", "At odd indices require the previous value≤current; at even indices require previous≥current.", "Scan left to right and swap the current adjacent pair whenever its required inequality is violated.", "Earlier inequalities stay valid because the swapped value moves into the role that already has the correct relation to the previous position."],
        "A one-pass local invariant is enough. Before processing index i, every earlier comparison has the required direction. If the new comparison is wrong, swap only positions i-1 and i; the extremal value placed at i-1 also preserves the prior comparison. The property comparator accepts any valid permutation, not one fixed arrangement. The independent oracle sorts a copy and swaps alternating adjacent ranks, while exhaustive regression checks every short array and every valid alternative.", "O(n)", "O(1)", difficulty=3,
        stress=[([large_wiggle],wiggle_oracle([large_wiggle]))]),
    282: entry("add_operators", [("num", "str"), ("target", "int")], "list[str]", ["strings", "backtracking", "recursion"],
        ["num contains 1–10 decimal digits and target is a signed 32-bit integer.", "Insert '+', '-', or '*' between some digits so each returned expression evaluates to target. Do not reorder or drop digits, do not use unary operators, and do not form a multi-digit operand with a leading zero. Return all valid expressions in any order."],
        [(["123",6], "Both 1+2+3 and 1*2*3 use every digit in order and evaluate to 6."), (["105",5], "The valid expressions are 1*0+5 and 10-5; 1*05 is forbidden because 05 has a leading zero.")],
        [[digits,target] for digits,target in (("1",1),("1",2),("00",0),("00",1),("232",8),("123",7),("345",15),("111",3),("101",2),("000",0),("12",12),("12",-1),("999",81),("214",8))],
        EXPRESSION, [EXPRESSION.replace('total - last + last * value, last * value', 'total * value, last * value'), EXPRESSION.replace('if end > index + 1 and num[index] == "0":\n                break', 'if False:\n                break')],
        ["Handles multiplication as a left-to-right operation instead of giving it precedence over the previous term.", "Allows operands such as 05, producing expressions forbidden by the contract."], expression_oracle, random_expression,
        ["Each recursion level chooses the next operand boundary and, except first, the operator before it.", "Track the total plus the most recent signed term so multiplication can replace that term without reevaluating the expression.", "For multiplication use total-last+last*value; for plus/minus start a new signed last term. Stop extending an operand after a leading zero.", "Only append at the end of num when total equals target. Backtracking strings avoids eval and preserves digit order."],
        "Depth-first search enumerates every legal operand split and operator choice. Addition and subtraction update both the total and the latest signed term. Multiplication has precedence, so it removes that latest term and substitutes its product. A leading zero may stand alone but cannot begin a longer operand. The independent oracle first enumerates all digit partitions, then operator products, and evaluates precedence with a separate term accumulator.", "O(4^n·n)", "O(n) recursion excluding output", difficulty=8,
        stress=[(["3456237490",9191],[])]),
    283: entry("move_zeroes", [("nums", "list[int]")], "None", ["arrays", "two-pointers", "in-place"],
        ["nums contains 1–10000 signed 32-bit integers.", "Move every zero to the end of the original list while preserving the relative order of nonzero values. Return nothing and use constant auxiliary space."],
        [([[0,1,0,3,12]], "The nonzero subsequence 1,3,12 keeps its order and the two zeros occupy the final positions."), ([[0]], "The only element is already a trailing zero, so the list remains unchanged.")],
        [[values] for values in ([1],[1,0],[0,1],[0,0],[1,2,3],[0,0,1],[1,0,0],[1,0,2,0,3],[0,-1,0,-2],[4,0,5,0,0,6],[0,0,0,1],[1,0,1,0,1])],
        MOVE_ZEROES, ['def move_zeroes(nums):\n    left, right = 0, len(nums) - 1\n    while left < right:\n        if nums[left] == 0:\n            nums[left], nums[right] = nums[right], nums[left]\n            right -= 1\n        else:\n            left += 1\n', 'def move_zeroes(nums):\n    nums[:] = [value for value in nums if value != 0]\n'],
        ["Swaps each zero with the current last value, which can reverse or otherwise reorder the nonzero subsequence.", "Removes zeros without restoring the original list length with trailing zeros."], move_zeroes_oracle, random_move_zeroes,
        ["Maintain the first position where the next nonzero value belongs.", "Scan with a read index; when its value is nonzero, swap it into the write position and advance write.", "Because write never passes read, each swap moves a nonzero forward and a zero toward the suffix.", "Nonzero values are encountered and written in original order; no separate output list is needed."],
        "The write pointer counts nonzero values already placed. Each new nonzero swaps into that next position. Since reads progress left to right, stable nonzero order is preserved, and every displaced zero eventually remains in the suffix. The independent oracle explicitly collects the nonzero subsequence and appends the exact number of zeros.", "O(n)", "O(1)", difficulty=3,
        stress=[([large_move],move_zeroes_oracle([large_move]))]),
    285: entry("inorder_successor", [("root", "TreeNode"), ("p", "TreeNode")], "TreeNode | None", ["trees", "binary-search", "binary-search-trees"],
        ["root contains 1–10000 TreeNode objects with unique values from -10^9 through 10^9 and strict BST ordering. p is an actual node in root.", "Return the existing node with the smallest value strictly greater than p.val, or None when p is the maximum. Do not change the tree."],
        [([[2,1,3],1], "Inorder values are 1,2,3, so the existing node 2 immediately follows node 1."), ([[2,1,3],3], "Node 3 is the maximum value, so no inorder successor exists and the answer is None.")],
        [[tree,p] for tree,p in (([1],1),([2,1],1),([2,1],2),([2,1,3],2),([5,3,7,2,4,6,8],4),([5,3,7,2,4,6,8],5),([5,3,7,2,4,6,8],8),([0,-2,3,-4,-1,2,5],-2),([0,-2,3,-4,-1,2,5],2),([10,5,15,2,7,12,20],7),([10,5,15,2,7,12,20],12),([8,4,12,2,6,10,14],10))],
        SUCCESSOR, ['def inorder_successor(root, p):\n    return p.right\n', 'def inorder_successor(root, p):\n    return root\n'],
        ["Returns the right child directly, missing both ancestors and the leftmost descendant inside a right subtree.", "Always returns the root, including when the successor is elsewhere or does not exist."], successor_oracle, random_bst_successor,
        ["The successor is the smallest BST value greater than p.val.", "Search from root; whenever current.val is greater, remember it and move left for a smaller qualifying value.", "When current.val≤p.val, move right. Return the last remembered node after the path ends.", "Keep the TreeNode itself, not only its value, because the judge requires the existing input object. None is valid at the maximum."],
        "BST ordering turns successor search into one root-to-leaf path. A node greater than p is a candidate, but its left subtree may contain a smaller qualifying node; a node at most p can only lead to a successor on its right. The final candidate is the least greater value. The judge checks its identity and that all tree links and values remain unchanged. The independent oracle globally scans compact-tree values.", "O(h)", "O(1)", difficulty=5,
        stress=[([right_chain(10_000),9998],9999)]),
    286: entry("walls_and_gates", [("rooms", "list[list[int]]")], "None", ["matrices", "breadth-first-search", "graphs"],
        ["rooms is a rectangular 1–250 by 1–250 matrix containing only -1 walls, 0 gates, and 2147483647 empty rooms.", "Replace each reachable empty room in place with its shortest four-direction distance to any gate. Walls, gates, and unreachable empty rooms remain unchanged. Return nothing."],
        [([[[INF,-1,0,INF],[INF,INF,INF,-1],[INF,-1,INF,-1],[0,-1,INF,INF]]], "Starting simultaneously from both gates assigns every reachable empty room its nearest path distance, while walls remain -1."), ([[[INF,-1,0]]], "The wall blocks the empty room from the gate, so it remains 2147483647.")],
        [[rooms] for rooms in ([[0]],[[INF]],[[-1]],[[0,INF]],[[INF,0]],[[0,-1,INF]],[[0,INF,INF]],[[0,INF],[INF,INF]],[[0,-1],[INF,INF]],[[0,INF,0]],[[INF,INF],[INF,0]],[[0,INF,-1,INF,0]],[[INF,-1,0],[INF,INF,INF],[0,-1,INF]])],
        WALLS, ['def walls_and_gates(rooms):\n    gates = [(r,c) for r,row in enumerate(rooms) for c,v in enumerate(row) if v == 0]\n    for r,row in enumerate(rooms):\n        for c,v in enumerate(row):\n            if v == 2147483647 and gates: rooms[r][c] = min(abs(r-a)+abs(c-b) for a,b in gates)\n', single_gate_wrong_source()],
        ["Uses Manhattan distance through walls instead of the shortest traversable path.", "Expands from only the first gate, missing a nearer second gate."], walls_and_gates_oracle, random_rooms,
        ["Reversing the search direction avoids running a separate search from every empty room.", "Put every gate into one queue at distance zero, then expand them together.", "When an adjacent cell is still INF, assign current+1 and enqueue it. Ignore walls and already assigned cells.", "The first wave reaching a room is globally shortest because breadth-first layers from all gates advance together."],
        "Multi-source breadth-first search treats every gate as a simultaneous origin. Queue order processes distance layers, so the first visit to an empty room proves its nearest-gate distance and marks it against revisits. Walls never enter the queue. The independent oracle instead starts a separate BFS from each empty room on small grids.", "O(mn)", "O(mn)", difficulty=5,
        stress=[([large_rooms],large_rooms_expected)]),
    287: entry("find_duplicate", [("nums", "list[int]")], "int", ["arrays", "two-pointers", "cycle-detection"],
        ["nums has n+1 elements for 1≤n≤100000. Every value lies in 1..n, and exactly one value occurs more than once; it may occur more than twice.", "Return the repeated value without modifying nums and using constant auxiliary space."],
        [([[1,3,4,2,2]], "Following indices as pointers creates a cycle whose entry is value 2, the repeated number."), ([[3,1,3,4,2]], "Value 3 appears twice and every other value once, so the answer is 3.")],
        [[values] for values in ([1,1],[2,2,2],[1,1,1,1],[2,1,2],[2,2,1,2],[3,1,3,2],[4,1,4,2,3],[5,4,3,2,1,5],[2,5,1,1,4,3],[6,2,4,1,3,5,6],[3,3,3,1,2],[1,4,4,4,2,3])],
        FIND_DUPLICATE, ['def find_duplicate(nums):\n    n = len(nums) - 1\n    return sum(nums) - n * (n + 1) // 2\n', 'def find_duplicate(nums):\n    result = 0\n    for index, value in enumerate(nums): result ^= value\n    for value in range(1, len(nums)): result ^= value\n    return result\n'],
        ["The sum difference works only when every other value appears once and the duplicate appears exactly twice.", "XOR cancellation has the same exactly-twice assumption and fails when the duplicate has higher multiplicity."], duplicate_oracle, random_duplicate,
        ["Treat each array value as the next pointer from its index.", "n+1 positions mapping into values 1..n guarantee a cycle, and the duplicate is the cycle entry reachable from nums[0].", "Run slow=nums[slow] and fast=nums[nums[fast]] until they meet. Reset slow to nums[0], then advance both one step to their next meeting.", "Floyd's cycle proof uses no marks or array changes; the second meeting identifies the entry rather than an arbitrary cycle position."],
        "The array defines a linked functional graph: from value x move to nums[x]. The duplicated value has multiple incoming edges and becomes the cycle entry on the path beginning at nums[0]. Floyd's tortoise and hare first meet inside the cycle; resetting one pointer to the path start and moving equally makes their next meeting the entry. The independent oracle counts values directly. The judge also snapshots nums and rejects a correct returned value if the input was modified.", "O(n)", "O(1)", difficulty=5,
        stress=[([large_duplicate],54321)]),
    289: entry("game_of_life", [("board", "list[list[int]]")], "None", ["matrices", "simulation", "in-place"],
        ["board is a rectangular 1–25 by 1–25 matrix containing only 0 and 1.", "Update every cell in place to the next Game of Life generation using all eight neighbors and the original generation simultaneously. Return nothing and use constant auxiliary space beyond local variables."],
        [([[[0,1,0],[0,0,1],[1,1,1],[0,0,0]]], "Simultaneous neighbor counts produce rows 000,101,011,010 in the next generation."), ([[[1,1],[1,1]]], "Each live corner has exactly three live neighbors, so the 2×2 block remains unchanged.")],
        [[board] for board in ([[0]],[[1]],[[0,0]],[[1,1]],[[1,1,1]],[[0,1,0]],[[1,0],[0,1]],[[1,1],[1,0]],[[0,1,0],[1,1,1],[0,1,0]],[[1,0,1],[0,1,0],[1,0,1]],[[0,0,0],[0,1,0],[0,0,0]],[[1,1,1],[1,1,1],[1,1,1]])],
        GAME_OF_LIFE, [GAME_OF_LIFE.replace('board[other_row][other_column] in (1, 2)', 'board[other_row][other_column] == 1'), GAME_OF_LIFE.replace('for other_row in range(max(0, row - 1), min(rows, row + 2))\n                for other_column in range(max(0, column - 1), min(columns, column + 2))', 'for other_row, other_column in ((row-1,column),(row+1,column),(row,column-1),(row,column+1))\n                if 0 <= other_row < rows and 0 <= other_column < columns')],
        ["Counts already-updated transitional cells as dead, so later cells do not use one simultaneous original generation.", "Counts only four orthogonal neighbors instead of all eight surrounding cells."], life_oracle, random_life,
        ["Each cell needs both its old state and enough information to store its new state during the first pass.", "Use temporary codes: 2 for live→dead and 3 for dead→live. Both 1 and 2 count as originally live.", "Count eight neighbors from values in (1,2), assign transition codes, then take every cell modulo 2 in a second pass.", "The encoded board supplies the old generation to every cell while still retaining the next generation in place."],
        "Two bits of state fit in each integer cell. During the first pass, values 1 and 2 both mean originally live, while 2 and 3 record a changed next state. This prevents row-order cascades. A final modulo pass maps unchanged/transition codes to the next 0/1 generation. The independent oracle reads only an untouched input matrix and writes a separate result.", "O(mn)", "O(1)", difficulty=5,
        stress=[([large_life],life_oracle([large_life]))]),
    291: entry("word_pattern_match", [("pattern", "str"), ("s", "str")], "bool", ["strings", "backtracking", "recursion"],
        ["pattern and s contain 1–20 and 1–50 lowercase English letters, respectively.", "Return whether every pattern character can map bijectively to one nonempty substring so concatenating the mapped substrings in pattern order equals all of s."],
        [(["abab","redblueredblue"], "Mapping a→red and b→blue expands abab to the complete text."), (["ab","aa"], "Both one-character splits would map a and b to the same substring a, violating the bijection.")],
        [[pattern,text] for pattern,text in (("a","x"),("a","xyz"),("aa","xx"),("aa","xy"),("ab","xy"),("aba","redbluered"),("abba","redbluebluered"),("aaaa","asdasdasdasd"),("abab","redblueredgreen"),("abc","xyz"),("abc","aaaa"),("abca","onetwothreeone"),("aabb","xyzabcxzyabc"),("abcabc","catdogpigcatdogpig"))],
        WORD_PATTERN, [WORD_PATTERN.replace('if value in used:\n                continue', 'if False:\n                continue'), 'def word_pattern_match(pattern, s):\n    if len(s) % len(pattern): return False\n    size = len(s) // len(pattern)\n    mapping = {}\n    for index, character in enumerate(pattern):\n        piece = s[index*size:(index+1)*size]\n        if character in mapping and mapping[character] != piece: return False\n        mapping[character] = piece\n    return len(set(mapping.values())) == len(mapping)\n'],
        ["Allows two different pattern characters to reuse one substring, violating the one-to-one requirement.", "Forces every mapped substring to have equal length, missing valid mappings such as red and blue."], word_pattern_oracle, random_word_pattern,
        ["Mappings must be consistent in both directions: character→substring and used substrings.", "At an unmapped character, try each nonempty next substring that leaves at least one character per remaining pattern position.", "Assign an unused candidate, recurse on both advanced indices, then remove it on failure. Reuse an existing mapping only when s starts with it.", "Succeed only when both pattern and text end together; exhausting just one side is not a complete match."],
        "Backtracking consumes the pattern and text from left to right. Existing mappings force one exact prefix. A new character tries each feasible unused substring, and the used set enforces bijection. Removing speculative assignments restores the search state. The independent oracle enumerates every way to partition short generated text into exactly len(pattern) nonempty pieces and checks the two mappings directly.", "O(n^(m-1)·m) worst case", "O(m+n) recursion and mappings", difficulty=8,
        stress=[(["abababababababababab","redblue" * 10],True)]),
    292: entry("can_win_nim", [("n", "int")], "bool", ["math", "game-theory", "dynamic-programming"],
        ["n is an integer from 1 through 2^31-1.", "You move first; each move removes 1, 2, or 3 stones, and whoever removes the last stone wins. Return whether you can force a win against optimal play."],
        [([4], "Every first move leaves 1–3 stones, which the opponent removes to win, so four is losing."), ([7], "Remove three stones to leave the losing count four; every opponent reply can then be complemented to four.")],
        [[n] for n in (1,2,3,5,6,8,9,10,11,12,15,16,100,101,999)],
        NIM, ['def can_win_nim(n):\n    return n % 2 == 1\n', 'def can_win_nim(n):\n    return n > 4\n'],
        ["Uses parity, even though six and ten are winning while odd counts can also be characterized only through modulo four.", "Treats every count above four as winning and misses later losing multiples of four."], nim_oracle, random_nim,
        ["Look for a position from which every legal move gives the opponent a winning response.", "Counts 1,2,3 are winning and 4 is losing; after that the pattern repeats every four.", "If n is not divisible by four, remove n mod 4 stones. If it is divisible by four, every move leaves a nonmultiple for the opponent.", "Complement the opponent's removal to four on each pair of turns, preserving a multiple-of-four pile for them."],
        "Multiples of four are losing positions. From one, every move leaves a nonmultiple; from a nonmultiple, removing its remainder modulo four leaves a multiple. After that, respond to each opponent move x by removing 4-x. The reference therefore needs one modulo check. The independent oracle computes winning and losing states bottom-up for generated counts.", "O(1)", "O(1)", difficulty=3,
        stress=[([2**31-1],True)]),
    293: entry("generate_flip_moves", [("current_state", "str")], "list[str]", ["strings", "simulation"],
        ["current_state contains 1–500 characters, each '+' or '-'.", "Return every state reachable by changing exactly one occurrence of consecutive '++' to '--'. Return unique states in any order; do not modify any other character."],
        [(["++++"], "Flipping the pair at positions 0, 1, or 2 yields --++, +--+, and ++--."), (["+--+"], "No two plus signs are adjacent, so there is no legal move.")],
        [[state] for state in ("+","-","++","--","+++","+-+","-++","++-","+++++","++--++","+-+-++","++++++++","---++---")],
        FLIP_MOVES, ['def generate_flip_moves(current_state):\n    index = current_state.find("++")\n    return [] if index < 0 else [current_state[:index] + "--" + current_state[index+2:]]\n', 'def generate_flip_moves(current_state):\n    return [current_state.replace("++", "--")] if "++" in current_state else []\n'],
        ["Returns only the first legal move and omits later overlapping or separated pairs.", "Flips every nonoverlapping pair at once instead of exactly one selected pair."], flip_moves_oracle, random_flip,
        ["Each legal answer corresponds to one start index where two adjacent characters are plus.", "Scan every adjacent pair and construct one new string for each '++'.", "For index i, concatenate state[:i], '--', and state[i+2:].", "Different start indices change different positions, so their resulting states are unique even for overlapping pairs."],
        "A single left-to-right scan finds every legal pair. Strings are immutable, so each answer is built from the untouched prefix and suffix around one replacement. Overlapping pairs are separate moves and must both appear. The independent oracle uses the same direct move definition, with exhaustive regression over short binary states.", "O(n²) including constructed output strings", "O(n²) output", difficulty=3,
        stress=[(["+" * 500],flip_moves_oracle(["+" * 500]))]),
    294: entry("can_win_flip_game", [("current_state", "str")], "bool", ["strings", "recursion", "game-theory", "dynamic-programming"],
        ["current_state contains 1–60 characters, each '+' or '-'.", "Players alternate changing one '++' pair to '--'. Return whether the first player can force a win when the player with no move loses."],
        [(["++++"], "Flipping the middle pair leaves +--+, which has no reply, so the first player can force a win."), (["+--+"], "There is no legal first move, so the first player loses.")],
        [[state] for state in ("+","-","++","--","+++","+-+","-++","++-","+++++","++--++","+-+-++","++++++++","---++---","++++--++++","+-+-+-+-")],
        FLIP_WIN, ['def can_win_flip_game(current_state):\n    return "++" in current_state\n', 'def can_win_flip_game(current_state):\n    return current_state.count("++") % 2 == 1\n'],
        ["Assumes any legal move wins, ignoring whether the opponent has a forced response.", "Counts nonoverlapping text occurrences and treats their parity as the game outcome, ignoring overlapping choices and split subgames."], flip_win_oracle, random_flip_win,
        ["A flip divides one consecutive run of plus signs into independent left and right subgames.", "Assign each run length a Grundy number: the mex of left-Grundy XOR right-Grundy over every flip position.", "Build grundy[length] from smaller lengths, XOR the values for every plus run separated by minus signs, and return whether the total is nonzero.", "The Sprague-Grundy XOR rule combines independent impartial games and avoids enumerating exponentially many whole strings."],
        "Each minus sign separates moves into independent plus runs. Flipping positions i,i+1 inside a run of length L leaves subruns of lengths i and L-i-2. Their game value is the XOR of previously computed Grundy numbers; the current value is the smallest nonnegative number not reachable by one move. XORing all run values determines whether the whole position is winning. The independent oracle recursively explores and memoizes every reachable short generated string.", "O(n²)", "O(n)", difficulty=5,
        stress=[(["+" * 60],flip_grundy_wins("+" * 60))]),
}


for problem_id in (280, 283, 286, 289):
    BATCH[problem_id]["result_mode"] = "mutated_argument"
    BATCH[problem_id]["mutated_parameter"] = 0
BATCH[280]["comparator"] = "wiggle"
BATCH[282]["comparator"] = "unordered"
BATCH[285]["params"] = [("root", "TreeNode", "treenode"), ("p", "TreeNode", "treenode_ref")]
BATCH[285]["adapter"] = "treenode_value"
BATCH[285]["node_policy"] = "return_input_node"
BATCH[285]["parameter_sources"] = {1: 0}
BATCH[287]["immutable_parameters"] = [0]
BATCH[291]["prerequisites"] = ["backtracking", "recursion"]
BATCH[293]["comparator"] = "unordered"
