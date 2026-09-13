"""Reviewed path-DP, matrix, interval-DP, greedy, and encoded-tree imports."""
from collections import deque
from functools import lru_cache

from .import_batch_055 import entry


def coin_path_oracle(args):
    coins, jump = args
    if not coins or coins[0] < 0 or coins[-1] < 0: return []
    best = None
    def search(index, path, cost):
        nonlocal best
        if index == len(coins) - 1:
            candidate = (cost, path)
            if best is None or candidate < best: best = candidate
            return
        for following in range(index + 1, min(len(coins), index + jump + 1)):
            if coins[following] >= 0:
                search(following, path + [following + 1], cost + coins[following])
    search(0, [1], coins[0])
    return [] if best is None else best[1]


def smoother_oracle(args):
    image = args[0]
    rows, columns = len(image), len(image[0])
    answer = []
    for row in range(rows):
        output_row = []
        for column in range(columns):
            values = [image[r][c] for r in range(max(0, row - 1), min(rows, row + 2))
                      for c in range(max(0, column - 1), min(columns, column + 2))]
            output_row.append(sum(values) // len(values))
        answer.append(output_row)
    return answer


def printer_oracle(args):
    text = args[0]
    @lru_cache(None)
    def solve(fragment):
        if not fragment: return 0
        answer = 1 + solve(fragment[1:])
        for index in range(1, len(fragment)):
            if fragment[index] == fragment[0]:
                answer = min(answer, solve(fragment[1:index]) + solve(fragment[index:]))
        return answer
    return solve(text)


def nondecreasing_oracle(args):
    nums = args[0]
    if all(a <= b for a, b in zip(nums, nums[1:])): return True
    low, high = min(nums) - 1, max(nums) + 1
    for index in range(len(nums)):
        original = nums[index]
        for value in range(low, high + 1):
            changed = nums[:index] + [value] + nums[index + 1:]
            if all(a <= b for a, b in zip(changed, changed[1:])): return True
        nums[index] = original
    return False


def encoded_path_oracle(args):
    nodes = {value // 10: value % 10 for value in args[0]}
    total = 0
    for position in nodes:
        depth, place = divmod(position, 10)
        left = (depth + 1) * 10 + place * 2 - 1
        right = left + 1
        if left in nodes or right in nodes: continue
        path_total, current_depth, current_place = 0, depth, place
        while current_depth:
            path_total += nodes[current_depth * 10 + current_place]
            current_place = (current_place + 1) // 2
            current_depth -= 1
        total += path_total
    return total


def random_coin_path(rng):
    length = rng.randint(2, 10)
    coins = [rng.randint(0, 12) if rng.random() > .2 else -1 for _ in range(length)]
    coins[0] = rng.randint(0, 8); coins[-1] = rng.randint(0, 8)
    return [coins, rng.randint(1, min(4, length - 1))]


def random_image(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randint(0, 255) for _ in range(columns)] for _ in range(rows)]]


def random_printer(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 9)))]


def random_nondecreasing(rng):
    return [[rng.randint(-5, 5) for _ in range(rng.randint(1, 10))]]


def random_encoded_tree(rng):
    positions = [(1, 1)]
    for depth in range(1, 4):
        for d, place in list(positions):
            if d != depth: continue
            for child in (place * 2 - 1, place * 2):
                if rng.random() < .55: positions.append((depth + 1, child))
    values = sorted(depth * 100 + place * 10 + rng.randint(0, 9) for depth, place in positions)
    return [values]


COIN_PATH = '''\
def cheapest_coin_path(coins, max_jump):
    n = len(coins)
    best = [None] * n
    if coins[-1] >= 0: best[-1] = (coins[-1], [n])
    for index in range(n - 2, -1, -1):
        if coins[index] < 0: continue
        choices = []
        for following in range(index + 1, min(n, index + max_jump + 1)):
            if best[following] is not None:
                choices.append((coins[index] + best[following][0], [index + 1] + best[following][1]))
        if choices: best[index] = min(choices)
    return [] if best[0] is None else best[0][1]
'''


SMOOTHER = '''\
def smooth_image(img):
    rows, columns = len(img), len(img[0])
    answer = [[0] * columns for _ in range(rows)]
    for row in range(rows):
        for column in range(columns):
            total = count = 0
            for r in range(max(0, row - 1), min(rows, row + 2)):
                for c in range(max(0, column - 1), min(columns, column + 2)):
                    total += img[r][c]
                    count += 1
            answer[row][column] = total // count
    return answer
'''


PRINTER = '''\
def strange_printer_turns(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for left in range(n - 1, -1, -1):
        dp[left][left] = 1
        for right in range(left + 1, n):
            dp[left][right] = 1 + dp[left + 1][right]
            for same in range(left + 1, right + 1):
                if s[same] == s[left]:
                    middle = dp[left + 1][same - 1] if same > left + 1 else 0
                    dp[left][right] = min(dp[left][right], middle + dp[same][right])
    return dp[0][n - 1]
'''


NONDECREASING = '''\
def can_be_nondecreasing(nums):
    changed = list(nums)
    edits = 0
    for index in range(1, len(changed)):
        if changed[index - 1] <= changed[index]: continue
        edits += 1
        if edits > 1: return False
        if index < 2 or changed[index - 2] <= changed[index]:
            changed[index - 1] = changed[index]
        else:
            changed[index] = changed[index - 1]
    return True
'''


PATH_SUM = '''\
def encoded_tree_path_sum(nums):
    nodes = {value // 10: value % 10 for value in nums}
    def visit(depth, position, running):
        key = depth * 10 + position
        if key not in nodes: return 0
        running += nodes[key]
        left = visit(depth + 1, position * 2 - 1, running)
        right = visit(depth + 1, position * 2, running)
        return running if left == right == 0 else left + right
    return visit(1, 1, 0)
'''


COIN_FEWEST = '''\
def cheapest_coin_path(coins, max_jump):
    from collections import deque
    queue = deque([(0, [1])]); seen = {0}
    while queue:
        index, path = queue.popleft()
        if index == len(coins) - 1: return path
        for following in range(index + 1, min(len(coins), index + max_jump + 1)):
            if coins[following] >= 0 and following not in seen:
                seen.add(following); queue.append((following, path + [following + 1]))
    return []
'''


COIN_LARGER_TIE = COIN_PATH.replace('if choices: best[index] = min(choices)', 'if choices: best[index] = min(choices, key=lambda item: (item[0], [-x for x in item[1]]))')
SMOOTHER_NO_CENTER = SMOOTHER.replace("total += img[r][c]\n                    count += 1", "if r != row or c != column:\n                        total += img[r][c]\n                        count += 1").replace('total // count', 'total // max(1, count)')
SMOOTHER_NINE = SMOOTHER.replace('total // count', 'total // 9')
PRINTER_RUNS = "def strange_printer_turns(s):\n    return 1 + sum(a != b for a, b in zip(s, s[1:]))\n"
PRINTER_UNIQUE = "def strange_printer_turns(s):\n    return len(set(s))\n"
NONDECREASING_DESCENTS = "def can_be_nondecreasing(nums):\n    return sum(a > b for a, b in zip(nums, nums[1:])) <= 1\n"
NONDECREASING_LOWER_RIGHT = NONDECREASING.replace("if index < 2 or changed[index - 2] <= changed[index]:\n            changed[index - 1] = changed[index]\n        else:\n            changed[index] = changed[index - 1]", "changed[index] = changed[index - 1]")
PATH_SUM_ALL = "def encoded_tree_path_sum(nums):\n    return sum(value % 10 for value in nums)\n"
PATH_SUM_LEFT = PATH_SUM.replace("right = visit(depth + 1, position * 2, running)", "right = 0")


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial], editorial


BATCH = {
    656: entry('cheapest_coin_path',[('coins','list[int]'),('max_jump','int')],'list[int]',['dynamic-programming','arrays'],
        ['1 <= len(coins) <= 1,000; -1 marks a blocked position; max_jump is positive.', 'Return one-based indices minimizing paid coin cost; break cost ties lexicographically, or return [] if unreachable.'],
        [([[1,2,4,-1,2],2], 'The path 1,3,5 is the minimum-cost reachable route.'), ([[1,1,1,1],2], 'Paths 1,2,4 and 1,3,4 tie in cost, so 1,2,4 is lexicographically smaller.')],
        [[coins,jump] for coins,jump in (([1],1),([1,-1,2],1),([1,-1,2],2),([1,9,1,1],2),([1,1,9,1],2),([0,0,0,0],3),([1,5,1,5,1],2),([1,-1,-1,2],2),([1,-1,-1,2],3),([5,1,1,1,5],2),([1,2,2,1],3),([1,10,1,1,1],2))],
        COIN_PATH,[COIN_FEWEST,COIN_LARGER_TIE],['Minimizes the number of jumps instead of total coin cost.','Chooses the lexicographically larger route when costs tie.'],coin_path_oracle,random_coin_path,
        *lesson('The best suffix from each index determines the best full route.','Work backward and compare candidates by (total cost, full path).','For each reachable index, prepend it to every reachable next state and retain the smallest pair.','Tuple ordering enforces cost first and lexicographic path second without a separate tie-reconstruction pass.'),'O(n * max_jump * path length)','O(n²)',8),
    661: entry('smooth_image',[('img','list[list[int]]')],'list[list[int]]',['matrices','simulation'],
        ['1 <= rows, columns <= 200; cell values are from 0 through 255.','Each output cell is the floor of the average of itself and all in-bounds adjacent cells.'],
        [([[[1,1,1],[1,0,1],[1,1,1]]], 'Corner neighborhoods average to zero after flooring, as does the nine-cell center neighborhood.'), ([[[100]]], 'A one-cell image smooths to its own value.')],
        [[img] for img in ([[0]],[[0,100]],[[0],[100]],[[1,2],[3,4]],[[255,255],[255,0]],[[1,2,3]],[[1],[2],[3]],[[1,2,3],[4,5,6]],[[9,0,9],[0,9,0]],[[10,20],[30,40],[50,60]],[[0,1,0],[1,0,1],[0,1,0]],[[7,8,9],[1,2,3],[4,5,6]])],
        SMOOTHER,[SMOOTHER_NO_CENTER,SMOOTHER_NINE],['Excludes the cell itself from its neighborhood.','Always divides by nine, including at borders and corners.'],smoother_oracle,random_image,
        *lesson('Border cells have clipped neighborhoods rather than implicit zero neighbors.','Enumerate the at most nine valid coordinates around each cell.','Clamp row and column ranges, sum their values, and floor-divide by the count.','Every output depends only on the original matrix, so write results into a separate matrix.'),'O(rows * columns)','O(rows * columns)',3),
    664: entry('strange_printer_turns',[('s','str')],'int',['dynamic-programming','strings'],
        ['1 <= len(s) <= 100; the string contains lowercase letters.','One turn prints one repeated character over any contiguous interval and may overwrite earlier characters.'],
        [(['aaabbb'], 'Print all a characters in one turn and all b characters in a second turn.'), (['aba'], 'Print aaa, then overwrite the middle with b, using two turns.')],
        [[s] for s in ('a','aa','ab','abc','abba','abab','abcba','aaaa','abaaba','aabbaa','abcdc','baac')],
        PRINTER,[PRINTER_RUNS,PRINTER_UNIQUE],['Counts character runs and misses savings from overwriting between equal endpoints.','Assumes each distinct character needs only one turn regardless of separated structure.'],printer_oracle,random_printer,
        *lesson('Equal characters printed in one turn can cover material that is overwritten later.','Use interval DP and merge the first character’s turn with a later equal character.','Start with 1+dp[left+1][right]; for each equal s[k], try dp[left+1][k-1]+dp[k][right].','The final visible copy at the left endpoint either has its own turn or shares the turn producing a later equal endpoint.'),'O(n³)','O(n²)',8),
    665: entry('can_be_nondecreasing',[('nums','list[int]')],'bool',['arrays','greedy'],
        ['1 <= len(nums) <= 10,000.','You may change at most one element to any integer; decide whether the full array can become nondecreasing.'],
        [([[4,2,3]], 'Lowering four to two produces [2,2,3].'), ([[4,2,1]], 'One edit cannot repair both decreases.')],
        [[[v for v in nums]] for nums in ([1],[1,2],[2,1],[3,4,2,3],[5,7,1,8],[1,2,3],[3,2,2],[1,5,4,6,7,10,8,9],[10,5,7],[1,1,1],[2,3,3,2,4],[1,4,1,2])],
        NONDECREASING,[NONDECREASING_DESCENTS,NONDECREASING_LOWER_RIGHT],['Counts local descents but ignores whether one replacement can satisfy both neighboring boundaries.','Always raises the right value, which can create a new violation with its successor.'],nondecreasing_oracle,random_nondecreasing,
        *lesson('At a violation, either lower the previous value or raise the current one.','Choose the local edit that remains compatible with the value two positions back.','On nums[i-1]>nums[i], lower nums[i-1] if nums[i-2]<=nums[i]; otherwise raise nums[i].','This preserves a nondecreasing processed prefix while spending the only allowed edit as flexibly as possible.'),'O(n)','O(n)',5),
    666: entry('encoded_tree_path_sum',[('nums','list[int]')],'int',['trees','hash-maps','recursion'],
        ['1 <= len(nums) <= 15; each three-digit value encodes depth, position, and node value.','The encodings form a valid binary tree of depth at most four; sum every root-to-leaf path total.'],
        [([[113,215,221]], 'The paths 3→5 and 3→1 total eight and four, giving twelve.'), ([[113,221]], 'The only root-to-leaf path totals four.')],
        [[nums] for nums in ([111],[119],[111,212],[111,222],[111,212,223],[111,212,223,314],[115,215,225,315,325],[110,210,220],[119,219,229,319,329],[113,214,225,326,337],[111,211,221,311,321,331,341],[115,218,327,438])],
        PATH_SUM,[PATH_SUM_ALL,PATH_SUM_LEFT],['Adds each node once instead of once per root-to-leaf path containing it.','Ignores every right-child path.'],encoded_path_oracle,random_encoded_tree,
        *lesson('The hundreds and tens digits identify a node’s depth and position.','Store encoded positions in a map and recurse only into positions that exist.','Carry the running sum; at a node with no encoded children, contribute that sum.','Every leaf contributes exactly one root-to-leaf total, and shared ancestors are correctly included in each descendant leaf’s path.'),'O(number of nodes)','O(number of nodes)',5),
}
