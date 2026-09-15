"""Tree path parity, removal strings, hierarchy knapsack, and grid path cover."""
from collections import deque

from .import_batch_055 import entry


def weights_oracle(args):
    edges, queries = args; n = len(edges) + 1; graph = [[] for _ in range(n + 1)]
    for u, v in edges: graph[u].append(v); graph[v].append(u)
    answer = []
    for source, target in queries:
        parent = {source: 0}; queue = [source]
        for node in queue:
            if node == target: break
            for nxt in graph[node]:
                if nxt not in parent: parent[nxt] = node; queue.append(nxt)
        length = 0; node = target
        while node != source: length += 1; node = parent[node]
        answer.append(sum(sum(1 if mask >> bit & 1 else 2 for bit in range(length)) % 2 for mask in range(1 << length)) % 1_000_000_007)
    return answer


def random_weights(rng):
    n = rng.randint(2, 11); edges = [[rng.randint(1, node - 1), node] for node in range(2, n + 1)]; rng.shuffle(edges)
    return [edges, [[rng.randint(1, n), rng.randint(1, n)] for _ in range(rng.randint(1, 8))]]


def leftmost_oracle(args):
    text = args[0]
    while True:
        index = next((i for i in range(len(text) - 1) if abs(ord(text[i]) - ord(text[i + 1])) in (1, 25)), -1)
        if index < 0: return text
        text = text[:index] + text[index + 2:]


def random_leftmost(rng): return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1, 35)))]


def profit_oracle(args):
    n, present, future, hierarchy, budget = args; parent = [0] * n
    for boss, employee in hierarchy: parent[employee - 1] = boss - 1
    best = 0
    for mask in range(1 << n):
        cost = gain = 0
        for employee in range(n):
            if mask >> employee & 1:
                price = present[employee] // 2 if employee and mask >> parent[employee] & 1 else present[employee]
                cost += price; gain += future[employee] - price
        if cost <= budget: best = max(best, gain)
    return best


def random_profit(rng):
    n = rng.randint(1, 8); hierarchy = [[rng.randint(1, employee - 1), employee] for employee in range(2, n + 1)]
    return [n, [rng.randint(1, 12) for _ in range(n)], [rng.randint(1, 15) for _ in range(n)], hierarchy, rng.randint(1, 24)]


def smallest_oracle(args):
    start = args[0]; seen = {start}; queue = deque([start]); answer = start
    while queue:
        text = queue.popleft(); answer = min(answer, text)
        for index in range(len(text) - 1):
            if abs(ord(text[index]) - ord(text[index + 1])) in (1, 25):
                following = text[:index] + text[index + 2:]
                if following not in seen: seen.add(following); queue.append(following)
    return answer


def random_smallest(rng): return [''.join(rng.choice('abcdefxyz') for _ in range(rng.randint(1, 10)))]


def grid_oracle(args):
    grid, k = args; rows = len(grid); columns = len(grid[0]); cells = [(r, c) for r in range(rows) for c in range(columns)]; solutions = []
    def visit(path, used, expected):
        row, column = path[-1]; value = grid[row][column]
        if value:
            if value != expected: return
            expected += 1
        if len(path) == len(cells):
            if expected == k + 1: solutions.append(tuple(path))
            return
        for nxt in sorted(((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1))):
            if nxt in used or nxt not in cells: continue
            next_value = grid[nxt[0]][nxt[1]]
            if next_value not in (0, expected): continue
            visit(path + [nxt], used | {nxt}, expected)
    for start in cells:
        if grid[start[0]][start[1]] in (0, 1): visit([start], {start}, 1)
    direction_rank = {(0, 1): 0, (1, 0): 1, (0, -1): 2, (-1, 0): 3}
    def priority(path):
        moves = tuple(direction_rank[(b[0] - a[0], b[1] - a[1])] for a, b in zip(path, path[1:]))
        return (path[0][0] * columns + path[0][1], moves)
    return [list(point) for point in min(solutions, key=priority)] if solutions else []


def random_grid(rng):
    rows = rng.randint(1, 2); columns = rng.randint(2, 4); total = rows * columns; k = rng.randint(1, min(4, total))
    chosen = rng.sample(range(total), k); grid = [[0] * columns for _ in range(rows)]
    for value, index in enumerate(chosen, 1): grid[index // columns][index % columns] = value
    return [grid, k]


WEIGHTS = '''def count_odd_path_assignments(edges,queries):
    modulo=1000000007;n=len(edges)+1;graph=[[] for _ in range(n+1)]
    for u,v in edges:graph[u].append(v);graph[v].append(u)
    parent=[0]*(n+1);depth=[0]*(n+1);order=[1]
    for node in order:
        for nxt in graph[node]:
            if nxt!=parent[node]:parent[nxt]=node;depth[nxt]=depth[node]+1;order.append(nxt)
    levels=[parent]
    for _ in range(1,n.bit_length()):levels.append([levels[-1][levels[-1][node]] for node in range(n+1)])
    def lca(first,second):
        if depth[first]<depth[second]:first,second=second,first
        difference=depth[first]-depth[second]
        for bit in range(len(levels)):
            if difference>>bit&1:first=levels[bit][first]
        if first==second:return first
        for bit in range(len(levels)-1,-1,-1):
            if levels[bit][first]!=levels[bit][second]:first=levels[bit][first];second=levels[bit][second]
        return parent[first]
    answer=[]
    for first,second in queries:
        distance=depth[first]+depth[second]-2*depth[lca(first,second)]
        answer.append(0 if distance==0 else pow(2,distance-1,modulo))
    return answer
'''


LEFTMOST = '''def resulting_string_leftmost(s):
    stack=[]
    for letter in s:
        if stack and abs(ord(letter)-ord(stack[-1])) in (1,25):stack.pop()
        else:stack.append(letter)
    return ''.join(stack)
'''


PROFIT = '''def maximum_discount_stock_profit(n,present,future,hierarchy,budget):
    children=[[] for _ in range(n+1)]
    for boss,employee in hierarchy:children[boss].append(employee)
    def solve(employee):
        merged=[[0,0] for _ in range(budget+1)]
        for child in children[employee]:
            child_dp=solve(child);following=[[0,0] for _ in range(budget+1)]
            for capacity in range(budget+1):
                for used in range(capacity+1):
                    for bought in (0,1):following[capacity][bought]=max(following[capacity][bought],merged[capacity-used][bought]+child_dp[used][bought])
            merged=following
        result=[[0,0] for _ in range(budget+1)]
        for capacity in range(budget+1):
            for boss_bought in (0,1):
                cost=present[employee-1]//(2 if boss_bought else 1);result[capacity][boss_bought]=merged[capacity][0]
                if cost<=capacity:result[capacity][boss_bought]=max(result[capacity][boss_bought],merged[capacity-cost][1]+future[employee-1]-cost)
        return result
    return solve(1)[budget][0]
'''


SMALLEST = '''def lexicographically_smallest_after_removals(s):
    n=len(s);empty=[[False]*n for _ in range(n)]
    def adjacent(a,b):return abs(ord(a)-ord(b)) in (1,25)
    for length in range(2,n+1,2):
        for left in range(n-length+1):
            right=left+length-1
            for middle in range(left+1,right+1,2):
                if adjacent(s[left],s[middle]) and (middle==left+1 or empty[left+1][middle-1]) and (middle==right or empty[middle+1][right]):
                    empty[left][right]=True;break
    best=['']*(n+1)
    for left in range(n-1,-1,-1):
        answer=s[left]+best[left+1]
        for middle in range(left+1,n):
            if adjacent(s[left],s[middle]) and (middle==left+1 or empty[left+1][middle-1]):answer=min(answer,best[middle+1])
        best[left]=answer
    return best[0]
'''


GRID = '''def sequential_grid_path(grid,k):
    rows=len(grid);columns=len(grid[0]);total=rows*columns;used=set();path=[]
    def visit(row,column,expected):
        value=grid[row][column]
        if value:
            if value!=expected:return False
            expected+=1
        used.add((row,column));path.append([row,column])
        if len(path)==total:return expected==k+1
        candidates=((row,column+1),(row+1,column),(row,column-1),(row-1,column))
        for next_row,next_column in candidates:
            if 0<=next_row<rows and 0<=next_column<columns and (next_row,next_column) not in used and grid[next_row][next_column] in (0,expected):
                if visit(next_row,next_column,expected):return True
        path.pop();used.remove((row,column));return False
    for row in range(rows):
        for column in range(columns):
            if grid[row][column] in (0,1) and visit(row,column,1):return path
    return []
'''


GREEDY_SMALLEST = '''def lexicographically_smallest_after_removals(s):
    stack=[]
    for letter in s:
        if stack and abs(ord(letter)-ord(stack[-1])) in (1,25):stack.pop()
        else:stack.append(letter)
    return ''.join(stack)
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]


WEIGHT_CASES=[[edges,queries] for edges,queries in [([[1,2],[1,3]],[[2,3],[1,1]]),([[1,2],[2,3]],[[1,3],[2,3]]),([[1,2],[1,3],[3,4],[3,5]],[[1,4],[3,4],[2,5]]),([[1,2],[2,3],[3,4]],[[1,4],[2,4],[3,3]]),([[1,2],[1,3],[1,4]],[[2,3],[2,4],[3,4]]),([[1,2],[2,3],[2,4],[4,5]],[[1,5],[3,5]]),([[1,2],[1,3],[2,4],[2,5],[3,6]],[[4,6],[5,6]]),([[1,2],[2,3],[3,4],[4,5]],[[1,5],[2,4]]),([[1,2],[1,3],[3,4],[4,5],[4,6]],[[2,5],[5,6]]),([[1,2],[2,3],[1,4],[4,5],[5,6]],[[3,6],[4,6]]),([[1,2],[2,3],[2,4],[3,5],[5,6]],[[4,6],[1,6]]),([[1,2],[1,3],[1,4],[4,5],[5,6],[6,7]],[[2,7],[3,5]]),([[1,2],[2,3],[3,4],[2,5],[5,6],[5,7]],[[4,7],[6,7]]),([[1,2],[1,3],[2,4],[4,5],[3,6],[6,7]],[[5,7],[1,7]])]]
LEFTMOST_CASES=[[s] for s in ['a','ab','ba','az','za','abc','adcb','zadb','ac','abb','abccba','xyzabc','zabz','mnopon']]
PROFIT_CASES=[[n,p,f,h,b] for n,p,f,h,b in [(1,[5],[9],[],5),(1,[7],[3],[],10),(2,[3,4],[5,8],[[1,2]],4),(3,[4,6,8],[7,9,11],[[1,2],[1,3]],10),(3,[5,2,3],[8,5,6],[[1,2],[2,3]],7),(2,[10,10],[1,20],[[1,2]],10),(3,[10,8,8],[2,20,20],[[1,2],[1,3]],18),(4,[4,5,6,7],[8,9,10,11],[[1,2],[1,3],[3,4]],12),(3,[1,10,10],[2,20,20],[[1,2],[2,3]],11),(4,[9,3,7,5],[12,8,13,9],[[1,2],[2,3],[2,4]],15),(2,[2,9],[3,20],[[1,2]],6),(3,[6,6,6],[7,12,12],[[1,2],[1,3]],12),(5,[2,4,6,8,10],[5,8,12,16,20],[[1,2],[1,3],[2,4],[2,5]],18),(4,[12,1,10,10],[13,2,20,20],[[1,2],[2,3],[2,4]],13)]]
SMALLEST_CASES=[[s] for s in ['a','ab','az','abc','bcda','zdce','adcb','zadb','abcd','abca','azby','cabd','abcdef','zyxabc']]
GRID_CASES=[[grid,k] for grid,k in [([[1,2]],2),([[2,1]],2),([[1,0,2]],2),([[0,1,2]],2),([[1,0],[0,2]],2),([[0,0],[1,2]],2),([[1,0],[3,2]],3),([[0,0,0],[0,1,2]],2),([[1,0,0],[0,0,2]],2),([[1,0,3],[0,0,2]],3),([[2,0,1],[0,0,3]],3),([[1,0],[0,0],[0,2]],2),([[0,1,0],[0,3,2]],3),([[1,0,0,4],[2,3,0,0]],4)]]


BATCH={
3559:entry('count_odd_path_assignments',[('edges','list[list[int]]'),('queries','list[list[int]]')],'list[int]',['trees','lowest common ancestor','combinatorics'],['edges form a tree of up to 100,000 nodes labeled 1 through n.','Each query independently assigns weights one or two only to edges on its path.','Return the number of assignments with odd path cost modulo 1,000,000,007; an empty path has zero ways.'],[([[[1,2]],[[1,1],[1,2]]],'The empty path has zero assignments, while the one-edge path has one odd assignment.'),([[[1,2],[1,3],[3,4],[3,5]],[[1,4],[3,4],[2,5]]],'Path lengths two, one, and three produce 2, 1, and 4 odd assignments.')],WEIGHT_CASES,WEIGHTS,[WEIGHTS.replace('distance-1','distance'),WEIGHTS.replace('-2*depth[lca(first,second)]','-depth[lca(first,second)]')],['Counts all 2^distance assignments instead of exactly half.','Computes path length with an incorrect LCA subtraction.'],weights_oracle,random_weights,lesson('For a path of positive length d, exactly half of its 2^d binary edge-weight assignments have odd total.','Preprocess depth and binary-lifting ancestors so each query’s path length is found with one LCA.','Compute d=depth[u]+depth[v]-2*depth[lca]; return zero for d=0, otherwise 2^(d-1).','Changing one fixed edge between weights one and two pairs odd and even assignments, while LCA decomposes the unique tree path into two ancestor paths.'),'O((n+queries) log n)','O(n log n)',8),
3561:entry('resulting_string_leftmost',[('s','str')],'str',['strings','stacks','simulation'],['s contains up to 100,000 lowercase letters.','Repeatedly remove the leftmost adjacent alphabet-consecutive pair in either order.','The alphabet is circular, so a and z are consecutive.'],[(['abc'],'Removing the leftmost pair ab leaves c.'),(['adcb'],'Remove dc first, exposing ab, which is then removed to leave the empty string.')],LEFTMOST_CASES,LEFTMOST,[LEFTMOST.replace('in (1,25)','==1'),LEFTMOST.replace('stack.pop()','stack.pop(0)')],['Forgets the circular adjacency between a and z.','Removes from the front of the retained prefix instead of the character adjacent to the current letter.'],leftmost_oracle,random_leftmost,lesson('After all earlier leftmost removals, only the surviving suffix’s last character can form the next newly exposed pair.','Use a stack of survivors; pop when the incoming letter is alphabet-adjacent to the top, otherwise push it.','Scan left to right, treating absolute code differences one and 25 as removable, then join the stack.','The stack exactly represents the fully reduced processed prefix; any removable pair inside it would already have been the leftmost pair and removed.'),'O(n)','O(n)',5),
3562:entry('maximum_discount_stock_profit',[('n','int'),('present','list[int]'),('future','list[int]'),('hierarchy','list[list[int]]'),('budget','int')],'int',['trees','dynamic programming','knapsack'],['There are at most 160 employees and budget is at most 160.','Buying a boss gives each direct child a floor-half purchase price; each stock may be bought once.','All purchases use the original budget, not future profits.'],[([2,[1,2],[4,3],[[1,2]],3],'Buying both costs two after the child discount and earns total profit five.'),([2,[3,4],[5,8],[[1,2]],4],'The budget cannot buy both, so buying employee two alone earns four.')],PROFIT_CASES,PROFIT,[PROFIT.replace('present[employee-1]//(2 if boss_bought else 1)','present[employee-1]//2'),PROFIT.replace('capacity-cost][1]+future','capacity-cost][0]+future')],['Gives every employee the half-price discount even when their direct boss was not purchased.','Combines purchased employees with children evaluated as though their boss was not purchased.'],profit_oracle,random_profit,lesson('A child subtree only needs to know whether its direct boss was bought, plus the budget allocated to that subtree.','Compute two budget-knapsack arrays per employee and merge child subtrees before considering whether to buy the employee.','Convolve child DP arrays for current bought/unbought states; compare skipping with buying at the price determined by the parent state.','Conditioning on the employee’s purchase makes child subtrees independent, and knapsack convolution considers every allocation of the fixed original budget.'),'O(n*budget^2)','O(n*budget)',8),
3563:entry('lexicographically_smallest_after_removals',[('s','str')],'str',['strings','dynamic programming','intervals'],['s contains up to 250 lowercase letters.','Remove any adjacent alphabet-consecutive pair in either order, with circular a-z adjacency.','Operations are optional; return the lexicographically smallest reachable string.'],[(['abc'],'Removing bc leaves a, which is lexicographically smallest.'),(['zdce'],'Although dc can be removed, keeping the original zdce is smaller than ze.')],SMALLEST_CASES,SMALLEST,[SMALLEST.replace('in (1,25)','==1'),GREEDY_SMALLEST],['Forgets circular a-z removals.','Greedily removes the first exposed pair instead of considering that keeping it may lead to a smaller final string.'],smallest_oracle,random_smallest,lesson('Two characters can become adjacent exactly when the entire interval between them can be deleted.','First compute which intervals can vanish; then build the smallest suffix by either keeping its first character or pairing it across a vanishing interior.','Fill empty[left][right] by possible partners, then set best[left] to the minimum of s[left]+best[left+1] and best[partner+1].','Every valid result either keeps its first original character or removes it with one uniquely exposed partner; these cases exhaust the first operation affecting that character.'),'O(n^3)','O(n^2)',8),
3565:entry('sequential_grid_path',[('grid','list[list[int]]'),('k','int')],'list[list[int]]',['matrices','backtracking','Hamiltonian paths'],['The small grid contains each marker 1 through k exactly once and all other cells are zero.','Visit every cell exactly once with orthogonal moves, encountering positive markers in numerical order.','For deterministic feedback, try starts in row-major order and moves in right, down, left, up priority; return the first valid path, or an empty list.'],[([[[0,0,0],[0,1,2]],2],'The fixed search priority yields the shown cover, visiting marker one before marker two and covering all six cells.'),([[[1,2]],2],'The only valid cover visits marker one and then marker two.')],GRID_CASES,GRID,[GRID.replace('in (0,1) and visit','==1 and visit'),GRID.replace('in (0,expected):','in (0,expected+1):')],['Allows only marker one as a starting cell and misses valid paths beginning on zero.','Allows the next marker to be skipped and enters the following marker too early.'],grid_oracle,random_grid,lesson('The state is the current cell, used-cell set, and next required marker; all choices must be explored because the path is Hamiltonian.','Use row-major starts and right/down/left/up neighbors so the first completion follows the deterministic app tie-break.','Enter only zero or the expected marker, advance expectation on a marker, backtrack used cells, and accept only after covering the grid.','Depth-first search follows the published priority and prunes every prefix that repeats a cell or violates marker order, so its first completion is the canonical valid path.'),'O((rows*columns)!)','O(rows*columns)',6),
}
