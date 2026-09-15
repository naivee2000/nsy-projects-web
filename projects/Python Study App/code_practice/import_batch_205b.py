"""Matrix search/DP, prefix sums, and linked-list binary conversion."""
from collections import deque
from itertools import product

from .import_batch_055 import entry


def flips_oracle(args):
    matrix = args[0]
    rows, columns = len(matrix), len(matrix[0])
    start = sum(matrix[row][column] << (row * columns + column)
                for row in range(rows) for column in range(columns))
    masks = []
    for row in range(rows):
        for column in range(columns):
            mask = 0
            for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = row + dr, column + dc
                if 0 <= nr < rows and 0 <= nc < columns:
                    mask ^= 1 << (nr * columns + nc)
            masks.append(mask)
    answer = rows * columns + 1
    for chosen in range(1 << len(masks)):
        state = start
        for index, mask in enumerate(masks):
            if chosen >> index & 1:
                state ^= mask
        if state == 0:
            answer = min(answer, chosen.bit_count())
    return answer if answer <= rows * columns else -1


def random_flips(rng):
    rows, columns = rng.randint(1, 3), rng.randint(1, 3)
    return [[[rng.randint(0, 1) for _ in range(columns)] for _ in range(rows)]]


def falling_oracle(args):
    grid = args[0]
    size = len(grid)
    best = grid[0][:]
    for row in range(1, size):
        best = [grid[row][column] + min(
            (best[previous] for previous in range(size) if previous != column),
            default=0,
        ) for column in range(size)]
    return min(best)


def random_falling(rng):
    size = rng.randint(1, 6)
    return [[[rng.randint(-9, 9) for _ in range(size)] for _ in range(size)]]


def binary_list_oracle(args):
    value = 0
    for bit in args[0]:
        value = value * 2 + bit
    return value


def random_binary_list(rng):
    length = rng.randint(1, 30)
    return [[rng.randint(0, 1) for _ in range(length)]]


def square_oracle(args):
    matrix, threshold = args
    rows, columns = len(matrix), len(matrix[0])
    answer = 0
    for side in range(1, min(rows, columns) + 1):
        if any(sum(matrix[row][column]
                   for row in range(top, top + side)
                   for column in range(left, left + side)) <= threshold
               for top in range(rows - side + 1)
               for left in range(columns - side + 1)):
            answer = side
    return answer


def random_square(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    matrix = [[rng.randint(0, 9) for _ in range(columns)] for _ in range(rows)]
    return [matrix, rng.randint(0, 60)]


def obstacle_oracle(args):
    grid, allowed = args
    rows, columns = len(grid), len(grid[0])
    queue = deque([(0, 0, 0, 0)])
    seen = {(0, 0, 0)}
    while queue:
        row, column, removed, distance = queue.popleft()
        if (row, column) == (rows - 1, columns - 1):
            return distance
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, column + dc
            if 0 <= nr < rows and 0 <= nc < columns:
                nxt = removed + grid[nr][nc]
                state = (nr, nc, nxt)
                if nxt <= allowed and state not in seen:
                    seen.add(state)
                    queue.append((nr, nc, nxt, distance + 1))
    return -1


def random_obstacle(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    grid = [[rng.randint(0, 1) for _ in range(columns)] for _ in range(rows)]
    grid[0][0] = grid[-1][-1] = 0
    return [grid, rng.randint(1, rows * columns)]


FLIPS = '''def minimum_matrix_flips(mat):
    from collections import deque
    rows,columns=len(mat),len(mat[0]);start=0;masks=[]
    for row in range(rows):
        for column in range(columns):
            start|=mat[row][column]<<(row*columns+column);mask=0
            for dr,dc in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
                nr,nc=row+dr,column+dc
                if 0<=nr<rows and 0<=nc<columns:mask^=1<<(nr*columns+nc)
            masks.append(mask)
    queue=deque([(start,0)]);seen={start}
    while queue:
        state,distance=queue.popleft()
        if state==0:return distance
        for mask in masks:
            nxt=state^mask
            if nxt not in seen:seen.add(nxt);queue.append((nxt,distance+1))
    return -1
'''

FLIPS_NO_CENTER = FLIPS.replace(
    "((0,0),(1,0),(-1,0),(0,1),(0,-1))",
    "((1,0),(-1,0),(0,1),(0,-1))",
)

FALLING = '''def minimum_shifted_falling_sum(grid):
    previous=grid[0][:]
    for row in grid[1:]:
        first=min(range(len(previous)),key=previous.__getitem__)
        second=min((i for i in range(len(previous)) if i!=first),key=previous.__getitem__)
        previous=[value+previous[second if column==first else first] for column,value in enumerate(row)]
    return min(previous)
'''

BINARY_LIST = '''def binary_linked_list_value(head):
    answer=0
    while head:
        answer=answer*2+head.val
        head=head.next
    return answer
'''

SQUARE = '''def maximum_square_side(mat,threshold):
    rows,columns=len(mat),len(mat[0]);prefix=[[0]*(columns+1) for _ in range(rows+1)]
    for row in range(rows):
        for column in range(columns):
            prefix[row+1][column+1]=mat[row][column]+prefix[row][column+1]+prefix[row+1][column]-prefix[row][column]
    def exists(side):
        return any(prefix[top+side][left+side]-prefix[top][left+side]-prefix[top+side][left]+prefix[top][left]<=threshold
                   for top in range(rows-side+1) for left in range(columns-side+1))
    low,high=0,min(rows,columns)
    while low<high:
        middle=(low+high+1)//2
        if exists(middle):low=middle
        else:high=middle-1
    return low
'''

OBSTACLE = '''def shortest_path_with_eliminations(grid,k):
    from collections import deque
    rows,columns=len(grid),len(grid[0]);queue=deque([(0,0,k,0)]);best={(0,0):k}
    while queue:
        row,column,left,distance=queue.popleft()
        if (row,column)==(rows-1,columns-1):return distance
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=row+dr,column+dc
            if 0<=nr<rows and 0<=nc<columns:
                remaining=left-grid[nr][nc]
                if remaining>=0 and remaining>best.get((nr,nc),-1):
                    best[(nr,nc)]=remaining;queue.append((nr,nc,remaining,distance+1))
    return -1
'''


BATCH = {
    1284: entry(
        'minimum_matrix_flips', [('mat', 'list[list[int]]')], 'int',
        ['matrices', 'breadth-first search', 'bit manipulation'],
        ['mat has one to three rows and columns and contains only zeroes and ones.',
         'One move flips a selected cell plus each existing edge-neighbor.',
         'Return the fewest moves to reach all zeroes, or -1 if impossible.'],
        [([[[0, 0], [0, 1]]], 'Three cross-shaped flips can clear the lone one.'),
         ([[[0]]], 'The matrix is already zero, so no move is needed.')],
        [[matrix] for matrix in (
            [[1]], [[0, 1]], [[1, 1]], [[1], [0]], [[1], [1]],
            [[1, 0], [0, 0]], [[1, 1], [1, 1]], [[1, 0, 0], [1, 0, 0]],
            [[1, 0], [0, 1]], [[0, 1, 0], [1, 0, 1]],
            [[1, 1, 1]], [[1], [0], [1]],
            [[1, 0, 1], [0, 1, 0], [1, 0, 1]],
            [[0, 0], [0, 1]],
        )],
        FLIPS,
        [FLIPS_NO_CENTER, FLIPS.replace('if state==0:return distance', 'if state==0:return distance+1')],
        ['Flips only neighbors and leaves the selected cell unchanged.',
         'Counts the already-reached zero state as an additional move.'],
        flips_oracle, random_flips,
        ['Encode the small matrix as one bitmask.',
         'Precompute the XOR mask produced by selecting every cell.',
         'Breadth-first search bitmask states; each edge is one flip.',
         'BFS visits states by move count, so its first zero state is optimal.'],
        'There are at most 2^9 matrix states. Encode each cell as one bit and XOR the five-cell move mask to produce a neighbor. Breadth-first search from the input state therefore explores every reachable flip sequence in nondecreasing length. The independent oracle enumerates every subset of cell flips; flipping twice cancels, so a shortest solution never needs a cell twice.',
        'O((m*n)*2^(m*n))', 'O(2^(m*n))', 8,
    ),
    1289: entry(
        'minimum_shifted_falling_sum', [('grid', 'list[list[int]]')], 'int',
        ['matrices', 'dynamic programming'],
        ['grid is a nonempty square matrix.',
         'Choose one value from each row; adjacent choices must use different columns.',
         'Return the minimum possible total, including negative values.'],
        [([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], 'Choosing one, five, and seven uses different adjacent columns and totals thirteen.'),
         ([[[7]]], 'The only one-row path has sum seven.')],
        [[grid] for grid in (
            [[0]], [[-5]], [[1, 2], [3, 4]], [[1, 1], [1, 1]],
            [[-1, 2], [3, -4]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            [[7]], [[5, 1, 5], [2, 9, 2], [8, 3, 8]],
            [[-1, -2, -3], [-4, -5, -6], [-7, -8, -9]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[1, 100], [100, 1]], [[10, -1], [-2, 20]],
            [[3, 1, 2], [6, 5, 4], [7, 9, 8]],
            [[2, 8, 3, 5], [6, 1, 7, 4], [9, 2, 8, 3], [1, 6, 5, 7]],
        )],
        FALLING,
        [FALLING.replace('second if column==first else first', 'first'),
         FALLING.replace('return min(previous)', 'return max(previous)')],
        ['Allows consecutive rows to reuse the same minimum column.',
         'Returns the greatest final path total instead of the least.'],
        falling_oracle, random_falling,
        ['Let each column store the best total ending there in the previous row.',
         'For a new column, add the smallest prior total from a different column.',
         'Track the smallest and second-smallest prior columns to make each transition constant time.',
         'Every valid path has one previous column; the recurrence minimizes over exactly those allowed predecessors.'],
        'Dynamic programming keeps the best total ending in each column. Only the smallest previous total is needed unless it comes from the forbidden same column, in which case the second-smallest is used. This produces each row in linear time. The oracle independently checks every other previous column for every transition.',
        'O(n^2)', 'O(n)', 8,
    ),
    1290: entry(
        'binary_linked_list_value', [('head', 'ListNode')], 'int',
        ['linked lists', 'math'],
        ['head is a nonempty linked list of at most thirty nodes.',
         'Every node value is zero or one, with the most significant bit first.',
         'Return the represented nonnegative integer without changing the list.'],
        [([[1, 0, 1]], 'Reading 101 in base two gives decimal five.'),
         ([[0]], 'A single zero bit represents zero.')],
        [[bits] for bits in (
            [1], [1, 1], [1, 0], [0, 1], [1, 0, 1], [0],
            [1, 1, 1, 1], [1, 0, 0, 0], [0, 0, 1], [1, 0, 1, 0, 1],
            [1] * 10, [1] + [0] * 10, [0, 1, 1, 0], [1, 0, 0, 1, 1, 0],
        )],
        BINARY_LIST,
        [BINARY_LIST.replace('answer=answer*2+head.val', 'answer+=head.val'),
         BINARY_LIST.replace('answer=answer*2+head.val', 'answer+=head.val<<1')],
        ['Adds bits without shifting the accumulated prefix.',
         'Gives every bit the same value-two place instead of advancing place values.'],
        binary_list_oracle, random_binary_list,
        ['Process bits from the most significant end.',
         'Appending one binary bit doubles the existing prefix, then adds that bit.',
         'Traverse nodes and update answer = answer * 2 + node.val.',
         'The loop invariant says answer equals exactly the binary prefix already visited.'],
        'Maintain the integer represented by the visited prefix. Appending the current bit is a left shift followed by adding that bit. Advance through the actual ListNode chain once. The independent oracle performs the same positional definition over serialized input values rather than linked nodes.',
        'O(n)', 'O(1)', 3,
    ),
    1292: entry(
        'maximum_square_side', [('mat', 'list[list[int]]'), ('threshold', 'int')], 'int',
        ['matrices', 'prefix sums', 'binary search'],
        ['mat is a nonempty rectangular matrix of nonnegative integers.',
         'A candidate must be a contiguous square whose total is at most threshold.',
         'Return its maximum side length, or zero when even every one-cell square is too large.'],
        [([[[1, 1, 3, 2, 4, 3, 2], [1, 1, 3, 2, 4, 3, 2], [1, 1, 3, 2, 4, 3, 2]], 4], 'A two-by-two block of ones totals four; no larger square fits.'),
         ([[[2, 2], [2, 2]], 1], 'Every one-cell square exceeds one, so the answer is zero.')],
        [[matrix, limit] for matrix, limit in (
            ([[0]], 0), ([[1]], 0), ([[1]], 1), ([[1, 2]], 3),
            ([[1], [2]], 2), ([[1, 1], [1, 1]], 4),
            ([[1, 1], [1, 1]], 3), ([[5, 1], [1, 1]], 4),
            ([[2, 2], [2, 2]], 1),
            ([[1, 1, 3, 2, 4, 3, 2], [1, 1, 3, 2, 4, 3, 2], [1, 1, 3, 2, 4, 3, 2]], 4),
            ([[0, 0, 0], [0, 0, 0]], 0), ([[9, 1, 1], [1, 1, 1]], 4),
            ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 12),
            ([[3, 0, 3], [0, 0, 0], [3, 0, 3]], 0),
        )],
        SQUARE,
        [SQUARE.replace('<=threshold', '<threshold'),
         SQUARE.replace('for top in range(rows-side+1) for left in range(columns-side+1)', 'for top in range(1) for left in range(1)')],
        ['Uses a strict threshold and rejects squares whose sum equals the limit.',
         'Checks only the top-left square for each side length.'],
        square_oracle, random_square,
        ['Build a two-dimensional prefix-sum table.',
         'Use four prefix values to test any square sum in constant time.',
         'Because entries are nonnegative, binary-search the largest side having at least one valid square.',
         'If a side works, every smaller side inside it works; this monotonicity makes binary search valid.'],
        'A padded 2D prefix table answers every square sum with inclusion-exclusion. Nonnegative cells guarantee that a valid square contains a valid square of every smaller side, so existence is monotone by side length. Binary search that predicate. The oracle directly sums every cell of every candidate square.',
        'O(m*n*log(min(m,n)))', 'O(m*n)', 5,
    ),
    1293: entry(
        'shortest_path_with_eliminations', [('grid', 'list[list[int]]'), ('k', 'int')], 'int',
        ['matrices', 'breadth-first search', 'graphs'],
        ['grid is a nonempty zero-one matrix whose start and destination are zero.',
         'Move one cell up, down, left, or right and eliminate at most k entered obstacles.',
         'Return the fewest moves from top-left to bottom-right, or -1 when unreachable.'],
        [([[[0, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 1], [0, 0, 0]], 1], 'Eliminating the obstacle at row three, column two gives a six-step path.'),
         ([[[0, 1, 1], [1, 1, 1], [1, 0, 0]], 1], 'Every route needs at least two eliminations, so none is allowed.')],
        [[grid, allowed] for grid, allowed in (
            ([[0]], 1), ([[0, 0]], 1), ([[0], [0]], 1), ([[0, 1, 0]], 1),
            ([[0, 1, 0]], 2), ([[0, 0], [0, 0]], 1),
            ([[0, 1], [1, 0]], 1), ([[0, 1], [1, 0]], 0),
            ([[0, 0, 0], [1, 1, 0], [0, 0, 0], [0, 1, 1], [0, 0, 0]], 1),
            ([[0, 1, 1], [1, 1, 1], [1, 0, 0]], 1),
            ([[0, 1, 1], [1, 1, 1], [1, 0, 0]], 2),
            ([[0, 0, 1], [1, 0, 1], [1, 0, 0]], 0),
            ([[0, 1, 0], [0, 1, 0], [0, 0, 0]], 0),
            ([[0, 1, 1, 0], [0, 0, 1, 0], [1, 0, 0, 0]], 1),
        )],
        OBSTACLE,
        [OBSTACLE.replace('remaining=left-grid[nr][nc]', 'remaining=left'),
         OBSTACLE.replace('remaining>=0', 'remaining>0')],
        ['Walks through obstacles without spending an elimination.',
         'Rejects a move that validly spends the final available elimination.'],
        obstacle_oracle, random_obstacle,
        ['A position alone is not a complete state; remaining eliminations matter.',
         'BFS by distance while retaining the greatest remaining budget seen at each cell.',
         'Enter a neighbor by subtracting its obstacle bit; enqueue only if its remaining budget improves that cell.',
         'An equal-or-smaller budget at the same cell and no shorter distance can never enable a better continuation.'],
        'Breadth-first search guarantees nondecreasing path length. At a cell, a state with more eliminations remaining dominates one reached no earlier with fewer, so store only the greatest remaining budget per cell. This safely prunes the third state dimension. The independent oracle retains every exact row, column, and number-removed state.',
        'O(m*n*k)', 'O(m*n)', 8,
    ),
}

BATCH[1290]['params'][0] = ('head', 'ListNode', 'listnode')
