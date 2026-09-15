"""Box reachability, scored paths, binary trees, and palindrome insertion DP."""
from collections import deque

from .import_batch_055 import entry


def candies_oracle(args):
    status, candies, keys, contained, initial = args
    owned, unlocked, opened = set(initial), {i for i, value in enumerate(status) if value}, set()
    changed = True
    while changed:
        changed = False
        for box in list(owned & unlocked - opened):
            opened.add(box)
            unlocked.update(keys[box])
            owned.update(contained[box])
            changed = True
    return sum(candies[box] for box in opened)


def random_candies(rng):
    size = rng.randint(1, 12)
    status = [rng.randint(0, 1) for _ in range(size)]
    candies = [rng.randint(1, 20) for _ in range(size)]
    keys = [rng.sample(range(size), rng.randint(0, min(size, 4))) for _ in range(size)]
    contained = [[] for _ in range(size)]
    for box in range(1, size):
        if rng.random() < .65:
            contained[rng.randrange(box)].append(box)
    initial = rng.sample(range(size), rng.randint(0, size))
    return [status, candies, keys, contained, initial]


def score_paths_oracle(args):
    board = args[0]
    size = len(board)
    best, count = -1, 0

    def visit(row, column, score):
        nonlocal best, count
        if row < 0 or column < 0 or board[row][column] == 'X':
            return
        if board[row][column].isdigit():
            score += int(board[row][column])
        if (row, column) == (0, 0):
            if score > best:
                best, count = score, 1
            elif score == best:
                count += 1
            return
        visit(row - 1, column, score)
        visit(row, column - 1, score)
        visit(row - 1, column - 1, score)

    visit(size - 1, size - 1, 0)
    return [0, 0] if best < 0 else [best, count % 1_000_000_007]


def random_score_paths(rng):
    size = rng.randint(2, 5)
    board = [[rng.choice('0123456789X') for _ in range(size)] for _ in range(size)]
    board[0][0], board[-1][-1] = 'E', 'S'
    return [''.join(row) for row in board],


def deepest_oracle(args):
    values = args[0]
    if not values:
        return 0
    queue, index, last = [values[0]], 1, 0
    while queue:
        last = sum(queue)
        following = []
        for _ in queue:
            for _ in range(2):
                if index < len(values):
                    child = values[index]
                    index += 1
                    if child is not None:
                        following.append(child)
        queue = following
    return last


def random_tree_values(rng, maximum=18, allow_empty=False):
    if allow_empty and rng.random() < .15:
        return []
    values, frontier, nodes = [rng.randint(-20, 20)], [0], 1
    while frontier and nodes < maximum:
        frontier.pop(0)
        for _ in range(2):
            if nodes < maximum and rng.random() < .7:
                values.append(rng.randint(-20, 20));frontier.append(nodes);nodes += 1
            else:
                values.append(None)
    while values and values[-1] is None:
        values.pop()
    return values


def random_deepest(rng):
    return [random_tree_values(rng, allow_empty=False)]


def all_bst_oracle(args):
    return sorted(value for tree in args for value in tree if value is not None)


def bst_serialized(values):
    if not values:
        return []
    tree = [values[0]]
    children = {values[0]: [None, None]}
    for value in values[1:]:
        node = values[0]
        while True:
            side = 0 if value < node else 1
            child = children[node][side]
            if child is None:
                children[node][side] = value
                children[value] = [None, None]
                break
            node = child
    queue, result = [values[0]], []
    while queue:
        node = queue.pop(0)
        result.append(node)
        if node is not None:
            queue.extend(children[node])
    while result and result[-1] is None:
        result.pop()
    return result


def random_two_bsts(rng):
    universe = list(range(-40, 41))
    rng.shuffle(universe)
    first_size, second_size = rng.randint(0, 12), rng.randint(0, 12)
    return [bst_serialized(universe[:first_size]),
            bst_serialized(universe[first_size:first_size + second_size])]


def insertions_oracle(args):
    text = args[0]
    longest = 0
    for mask in range(1 << len(text)):
        subsequence = ''.join(text[index] for index in range(len(text)) if mask >> index & 1)
        if subsequence == subsequence[::-1]:
            longest = max(longest, len(subsequence))
    return len(text) - longest


def random_insertions(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 10)))]


CANDIES = '''def maximum_box_candies(status,candies,keys,containedBoxes,initialBoxes):
    from collections import deque
    owned=set(initialBoxes);unlocked={i for i,value in enumerate(status) if value};opened=set();queue=deque(owned&unlocked);answer=0
    while queue:
        box=queue.popleft()
        if box in opened:continue
        opened.add(box);answer+=candies[box]
        unlocked.update(keys[box]);owned.update(containedBoxes[box])
        for candidate in owned&unlocked-opened:queue.append(candidate)
    return answer
'''

SCORE = '''def maximum_score_paths(board):
    size=len(board);mod=10**9+7;scores=[[None]*size for _ in range(size)];ways=[[0]*size for _ in range(size)]
    scores[-1][-1]=0;ways[-1][-1]=1
    for row in range(size-1,-1,-1):
        for column in range(size-1,-1,-1):
            if board[row][column] in 'XS':continue
            options=[(nr,nc) for dr,dc in ((1,0),(0,1),(1,1)) if (nr:=row+dr)<size and (nc:=column+dc)<size and scores[nr][nc] is not None]
            if options:
                best=max(scores[nr][nc] for nr,nc in options);scores[row][column]=best+(int(board[row][column]) if board[row][column].isdigit() else 0)
                ways[row][column]=sum(ways[nr][nc] for nr,nc in options if scores[nr][nc]==best)%mod
    return [0,0] if scores[0][0] is None else [scores[0][0],ways[0][0]]
'''

DEEPEST = '''def deepest_leaf_sum(root):
    from collections import deque
    queue=deque([root]);answer=0
    while queue:
        answer=0
        for _ in range(len(queue)):
            node=queue.popleft();answer+=node.val
            if node.left:queue.append(node.left)
            if node.right:queue.append(node.right)
    return answer
'''

ALL_BST = '''def sorted_values_from_two_bsts(root1,root2):
    def inorder(root):
        values=[];stack=[]
        while root or stack:
            while root:stack.append(root);root=root.left
            root=stack.pop();values.append(root.val);root=root.right
        return values
    first,second=inorder(root1),inorder(root2);answer=[];left=right=0
    while left<len(first) and right<len(second):
        if first[left]<=second[right]:answer.append(first[left]);left+=1
        else:answer.append(second[right]);right+=1
    return answer+first[left:]+second[right:]
'''

INSERTIONS = '''def minimum_palindrome_insertions(s):
    size=len(s);dp=[[0]*size for _ in range(size)]
    for length in range(2,size+1):
        for left in range(size-length+1):
            right=left+length-1
            if s[left]==s[right]:dp[left][right]=dp[left+1][right-1] if length>2 else 0
            else:dp[left][right]=1+min(dp[left+1][right],dp[left][right-1])
    return dp[0][-1]
'''


BATCH = {
    1298: entry(
        'maximum_box_candies', [('status', 'list[int]'), ('candies', 'list[int]'),
        ('keys', 'list[list[int]]'), ('containedBoxes', 'list[list[int]]'), ('initialBoxes', 'list[int]')], 'int',
        ['graphs', 'breadth-first search', 'simulation'],
        ['All five inputs describe the same n boxes; status one means initially unlocked.',
         'You may open only a box you possess and have unlocked, then gain its candy, keys, and contained boxes.',
         'Open each box at most once and return the maximum collectible candy total.'],
        [([[1,0,1,0],[7,5,4,100],[[],[],[1],[]],[[1,2],[3],[],[]],[0]], 'Opening zero reveals two; two supplies the key to one, for seven plus four plus five candy.'),
         ([[1,1],[4,6],[[],[]],[[],[]],[0,1]], 'Both initially owned open boxes contribute, totaling ten.')],
        [list(case) for case in (
            ([1],[5],[[]],[[]],[0]), ([0],[5],[[]],[[]],[0]), ([1],[5],[[]],[[]],[]),
            ([1,1],[4,6],[[],[]],[[],[]],[0,1]),
            ([1,0],[2,9],[[1],[]],[[1],[]],[0]),
            ([1,0],[2,9],[[],[]],[[1],[]],[0]),
            ([0,1],[2,9],[[],[0]],[[],[]],[1]),
            ([1,0,0],[1,2,3],[[1],[2],[]],[[1], [2], []],[0]),
            ([1,1,1],[1,2,3],[[],[],[]],[[1],[2],[]],[0]),
            ([1,0,1,0],[7,5,4,100],[[],[],[1],[]],[[1,2],[3],[],[]],[0]),
            ([1,0,0],[5,6,7],[[2],[],[1]],[[1],[],[]],[0]),
            ([0,0],[3,8],[[1],[]],[[],[]],[0]),
            ([1,0,1],[2,4,8],[[],[],[1]],[[],[],[]],[0,2]),
            ([1,0,0,0],[1,10,100,1000],[[1],[2],[3],[]],[[1],[2],[3],[]],[0]),
        )],
        CANDIES,
        [CANDIES.replace('unlocked.update(keys[box])', 'unlocked.update(())'),
         CANDIES.replace('owned.update(containedBoxes[box])', 'owned.update(())')],
        ['Ignores keys obtained from opened boxes.', 'Ignores newly obtained contained boxes.'],
        candies_oracle, random_candies,
        ['A box becomes usable only when both owned and unlocked.',
         'Track owned, unlocked, and already-opened sets separately.',
         'Queue each newly usable box; opening it may add keys and boxes that make more boxes usable.',
         'Every legal opening is eventually queued, and processing a box once collects its candy exactly once.'],
        'Maintain the two independent permissions—possession and an unlocked status—and their intersection is the frontier. Opening a frontier box grows both sets and may expose more frontier boxes. A processed set prevents duplicate candy. The independent oracle repeatedly scans the entire intersection to a fixed point rather than using event-driven queue updates.',
        'O(n+keys+contained boxes)', 'O(n)', 8,
    ),
    1301: entry(
        'maximum_score_paths', [('board', 'list[str]')], 'list[int]',
        ['matrices', 'dynamic programming'],
        ['board is square with E at top-left, S at bottom-right, digits, and blocked X cells.',
         'Move from S toward E using up, left, or up-left and sum entered digits.',
         'Return [maximum score, number of maximum-score paths modulo 1000000007], or [0,0] if unreachable.'],
        [([['E23','2X2','12S']], 'The unique best valid route collects digits totaling seven.'),
         ([['E12','1X1','21S']], 'Two symmetric maximum-score routes each total four.')],
        [[board] for board in (
            ['E1','1S'], ['EX','XS'], ['E0','0S'], ['E12','1X1','21S'],
            ['E23','2X2','12S'], ['E11','111','11S'], ['E99','9X9','99S'],
            ['E1X','111','X1S'], ['E00','0X0','00S'], ['E123','1111','1XX1','321S'],
            ['E1','XS'], ['EX','1S'], ['E12','XXX','21S'], ['E12','345','67S'],
        )],
        SCORE,
        [SCORE.replace("sum(ways[nr][nc] for nr,nc in options if scores[nr][nc]==best)", "next(ways[nr][nc] for nr,nc in options if scores[nr][nc]==best)"),
         SCORE.replace('((1,0),(0,1),(1,1))', '((1,0),(0,1))')],
        ['Counts only one optimal predecessor when several create distinct best paths.',
         'Omits diagonal moves.'],
        score_paths_oracle, random_score_paths,
        ['Compute from S toward E so all successor states are ready.',
         'Each cell stores both its greatest reachable score and the number of paths attaining it.',
         'Take the greatest successor score and sum counts only from successors tied at that score.',
         'Every path chooses exactly one first move, so tied successor counts are disjoint and complete.'],
        'Dynamic programming processes the board from bottom-right to top-left. At each digit, compare the down, right, and diagonal successor scores, retain their maximum, and sum only counts attaining that maximum. Blocked and unreachable cells remain absent. The oracle independently enumerates every legal path and aggregates only globally maximum totals.',
        'O(n^2)', 'O(n^2)', 8,
    ),
    1302: entry(
        'deepest_leaf_sum', [('root', 'TreeNode')], 'int',
        ['trees', 'breadth-first search'],
        ['root is a nonempty binary tree.',
         'Depth is the number of edges from the root.',
         'Return the sum of values belonging to leaves at the greatest depth.'],
        [([[1,2,3,4,5,None,6,7,None,None,None,None,8]], 'The deepest leaves are seven and eight, totaling fifteen.'),
         ([[5]], 'The root is the only and therefore deepest leaf.')],
        [[tree] for tree in (
            [1], [1,2], [1,None,3], [1,2,3], [1,2,3,4], [1,2,3,None,5,None,6],
            [1,2,3,4,5,None,6,7,None,None,None,None,8], [5], [1,2,3,4,5,6,7],
            [10,-2,3,None,4], [1,None,2,None,3,None,4], [0,-1,1,-2,None,None,2],
            [8,4,12,2,6,10,14,1], [3,9,20,None,None,15,7],
        )],
        DEEPEST,
        [DEEPEST.replace('answer=0\n        for', 'answer=answer\n        for'),
         DEEPEST.replace('return answer', 'return node.val')],
        ['Accumulates earlier levels instead of resetting the sum for each new depth.',
         'Returns only the final visited deepest node rather than the whole deepest level sum.'],
        deepest_oracle, random_deepest,
        ['Breadth-first search naturally groups nodes by depth.',
         'Reset the running sum at the start of every level.',
         'Consume exactly the current queue length, enqueue children, and retain the final level sum.',
         'After the last iteration, the saved sum contains exactly all nodes at maximum depth.'],
        'Traverse one breadth-first level at a time. Reset the answer before consuming that level, then enqueue every child. When the queue becomes empty, the most recently completed level is the deepest and its sum is the answer. The independent oracle walks the serialized tree level by level without constructing TreeNode objects.',
        'O(n)', 'O(width)', 5,
    ),
    1305: entry(
        'sorted_values_from_two_bsts', [('root1', 'TreeNode | None'), ('root2', 'TreeNode | None')], 'list[int]',
        ['trees', 'binary search trees', 'merge'],
        ['Each input is a binary search tree and may be empty.',
         'Include every node value from both trees, preserving duplicate occurrences.',
         'Return all values in nondecreasing order.'],
        [([[2,1,4],[1,0,3]], 'The two inorder sequences merge to zero, one, one, two, three, four.'),
         ([[],[5,3,7]], 'With the first tree empty, return the second tree values in sorted order.')],
        [[left,right] for left,right in (
            ([],[]), ([1],[]), ([],[1]), ([1],[2]), ([2],[1]), ([2,1,3],[2,1,3]),
            ([2,1,4],[1,0,3]), ([],[5,3,7]), ([5,3,7],[]),
            ([0,-2,3,-4,-1,2,5],[1,0,4]), ([3,1,5,None,2,4,6],[7]),
            ([10,5,15],[10,5,15]), ([-1,-2,0],[-3,None,-1]),
            ([8,4,12,2,6,10,14],[7,3,11,1,5,9,13]),
        )],
        ALL_BST,
        [ALL_BST.replace('return answer+first[left:]+second[right:]', 'return first+second'),
         ALL_BST.replace('return answer+first[left:]+second[right:]', 'return sorted(set(answer+first[left:]+second[right:]))')],
        ['Concatenates the two sorted traversals without merging their relative order.',
         'Uses a set and incorrectly removes duplicate node values.'],
        all_bst_oracle, random_two_bsts,
        ['Inorder traversal of a BST produces a sorted sequence.',
         'Traverse both trees, then merge their two sorted value lists.',
         'Compare the two current heads, append the smaller, and finally append either remainder.',
         'Each traversal is sorted and the standard merge selects the smallest unconsumed value each time.'],
        'Iterative inorder traversal creates one sorted list per BST without recursion-depth risk. Merge those lists with two pointers, retaining equal values from both. The oracle instead extracts every serialized non-null value and sorts the combined multiset, independently checking the BST-based construction.',
        'O(m+n)', 'O(m+n)', 5,
    ),
    1312: entry(
        'minimum_palindrome_insertions', [('s', 'str')], 'int',
        ['strings', 'dynamic programming'],
        ['s is a nonempty lowercase string.',
         'Insert characters anywhere without deleting or reordering existing characters.',
         'Return the minimum insertions needed to make the complete string a palindrome.'],
        [(['zzazz'], 'The input is already a palindrome, so zero insertions are needed.'),
         (['mbadm'], 'Two insertions can produce a palindrome such as mbdadbm.')],
        [[text] for text in (
            'a ab aa abc race zzazz mbadm leetcode google abcda banana aaaa abca cabba'.split()
        )],
        INSERTIONS,
        [INSERTIONS.replace('1+min(dp[left+1][right],dp[left][right-1])', '1+max(dp[left+1][right],dp[left][right-1])'),
         INSERTIONS.replace('if s[left]==s[right]', 'if False')],
        ['Chooses the more expensive mismatch repair rather than the cheaper side.',
         'Never recognizes matching ends and inserts around them unnecessarily.'],
        insertions_oracle, random_insertions,
        ['Matching ends can surround an optimal solution for the inside substring at no extra cost.',
         'For mismatched ends, insert a copy of either end and pay one plus the cheaper remaining interval.',
         'Fill intervals from shorter to longer using dp[left][right].',
         'The two cases exhaust the first and last characters of every target palindrome.'],
        'For matching endpoints, no insertion is required there and the inside interval determines the cost. For a mismatch, the target palindrome must pair either endpoint with an inserted copy, leaving one of two shorter intervals; choose the cheaper and add one. The oracle independently finds the longest palindromic subsequence by enumerating subsequences, and n minus that length equals the required insertions.',
        'O(n^2)', 'O(n^2)', 8,
    ),
}

for problem_id in (1302,):
    BATCH[problem_id]['params'][0] = ('root', 'TreeNode', 'treenode')
for problem_id in (1305,):
    BATCH[problem_id]['params'] = [('root1', 'TreeNode | None', 'treenode'), ('root2', 'TreeNode | None', 'treenode')]
