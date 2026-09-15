"""Graph labeling, connected grid cuts, polynomial products, swaps, and portals."""
from collections import deque
from itertools import permutations

from .import_batch_055 import entry


def edge_score_oracle(args):
    n, edges = args
    best = 0
    for values in permutations(range(1, n + 1)):
        best = max(best, sum(values[u] * values[v] for u, v in edges))
    return best


def random_edge_score(rng):
    n = rng.randint(2, 7)
    nodes = list(range(n)); rng.shuffle(nodes)
    edges = [[nodes[i], nodes[i + 1]] for i in range(n - 1)]
    if n >= 3 and rng.randrange(2): edges.append([nodes[-1], nodes[0]])
    rng.shuffle(edges)
    return [n, edges]


def _connected_after_removal(cells, removed):
    remaining = set(cells) - {removed}
    if not remaining: return False
    seen = {next(iter(remaining))}; queue = list(seen)
    for row, column in queue:
        for nxt in ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)):
            if nxt in remaining and nxt not in seen: seen.add(nxt); queue.append(nxt)
    return len(seen) == len(remaining)


def partition_discount_oracle(args):
    grid = args[0]; rows = len(grid); columns = len(grid[0])
    def valid(first, second):
        sum_first = sum(grid[r][c] for r, c in first); sum_second = sum(grid[r][c] for r, c in second)
        if sum_first == sum_second: return True
        heavy, difference = (first, sum_first - sum_second) if sum_first > sum_second else (second, sum_second - sum_first)
        return any(grid[r][c] == difference and _connected_after_removal(heavy, (r, c)) for r, c in heavy)
    for cut in range(1, rows):
        top = [(r, c) for r in range(cut) for c in range(columns)]
        bottom = [(r, c) for r in range(cut, rows) for c in range(columns)]
        if valid(top, bottom): return True
    for cut in range(1, columns):
        left = [(r, c) for r in range(rows) for c in range(cut)]
        right = [(r, c) for r in range(rows) for c in range(cut, columns)]
        if valid(left, right): return True
    return False


def random_partition_discount(rng):
    rows = rng.randint(1, 4); columns = rng.randint(1, 4)
    if rows * columns == 1: columns = 2
    return [[[rng.randint(1, 8) for _ in range(columns)] for _ in range(rows)]]


def polynomial_oracle(args):
    first, second = args; answer = [0] * (len(first) + len(second) - 1)
    for i, a in enumerate(first):
        for j, b in enumerate(second): answer[i + j] += a * b
    return answer


def random_polynomial(rng):
    return [[rng.randint(-20, 20) for _ in range(rng.randint(1, 7))], [rng.randint(-20, 20) for _ in range(rng.randint(1, 7))]]


def swap_oracle(args):
    start = tuple(args[0]); target = tuple(sorted(start, key=lambda value: (sum(map(int, str(value))), value)))
    queue = deque([start]); distance = {start: 0}
    while queue:
        state = queue.popleft()
        if state == target: return distance[state]
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                following = list(state); following[i], following[j] = following[j], following[i]; following = tuple(following)
                if following not in distance: distance[following] = distance[state] + 1; queue.append(following)


def random_swaps(rng):
    length = rng.randint(1, 8)
    return [rng.sample(range(1, 500), length)]


def portal_oracle(args):
    matrix = args[0]; rows = len(matrix); columns = len(matrix[0]); letters = sorted({c for row in matrix for c in row if c.isalpha()})
    bit = {letter: 1 << i for i, letter in enumerate(letters)}; portals = {letter: [] for letter in letters}
    for row in range(rows):
        for column in range(columns):
            if matrix[row][column].isalpha(): portals[matrix[row][column]].append((row, column))
    queue = deque([(0, 0, 0)]); distance = {(0, 0, 0): 0}
    while queue:
        row, column, used = queue.popleft(); current = distance[row, column, used]
        if (row, column) == (rows - 1, columns - 1): return current
        letter = matrix[row][column]
        if letter.isalpha() and not used & bit[letter]:
            following_used = used | bit[letter]
            for next_row, next_column in portals[letter]:
                state = (next_row, next_column, following_used)
                if state not in distance or current < distance[state]:
                    distance[state] = current; queue.appendleft(state)
        for next_row, next_column in ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)):
            state = (next_row, next_column, used)
            if 0 <= next_row < rows and 0 <= next_column < columns and matrix[next_row][next_column] != '#' and state not in distance:
                distance[state] = current + 1; queue.append(state)
    return -1


def random_portal(rng):
    rows = rng.randint(1, 4); columns = rng.randint(1, 4); alphabet = '.##ABC'
    matrix = [''.join(rng.choice(alphabet) for _ in range(columns)) for _ in range(rows)]
    matrix[0] = '.' + matrix[0][1:]
    return [matrix]


EDGE_SCORE = '''def maximum_edge_value_sum(n,edges):
    if n<=1:return 0
    if len(edges)==n:
        order=[n]+list(range(n-1,0,-2))+list(range(1 if n%2 else 2,n,2))
        return sum(order[i]*order[(i+1)%n] for i in range(n))
    order=list(range(2,n+1,2))+list(range(n if n%2 else n-1,0,-2))
    return sum(a*b for a,b in zip(order,order[1:]))
'''


PARTITION_DISCOUNT = '''def can_partition_grid_with_discount(grid):
    def check(values):
        rows=len(values);columns=len(values[0]);lower=sum(map(sum,values));upper=0;seen={};remaining={}
        for row in values:
            for value in row:remaining[value]=remaining.get(value,0)+1
        for cut in range(rows-1):
            for value in values[cut]:
                upper+=value;lower-=value;seen[value]=seen.get(value,0)+1;remaining[value]-=1
            if upper==lower:return True
            heavy,difference=(seen,upper-lower) if upper>lower else (remaining,lower-upper)
            if not heavy.get(difference):continue
            if columns>1 and ((cut+1 if upper>lower else rows-cut-1)>1):return True
            section=values[:cut+1] if upper>lower else values[cut+1:]
            if len(section)==1:
                if section[0][0]==difference or section[0][-1]==difference:return True
            elif columns==1 and (section[0][0]==difference or section[-1][0]==difference):return True
        return False
    if check(grid):return True
    return check([list(column) for column in zip(*grid)])
'''


POLYNOMIAL = '''def multiply_polynomials(poly1,poly2):
    import math
    size=len(poly1)+len(poly2)-1;n=1
    while n<size:n*=2
    first=list(map(complex,poly1))+[0j]*(n-len(poly1));second=list(map(complex,poly2))+[0j]*(n-len(poly2))
    def fft(values,invert):
        j=0
        for i in range(1,n):
            bit=n>>1
            while j&bit:j^=bit;bit>>=1
            j^=bit
            if i<j:values[i],values[j]=values[j],values[i]
        length=2
        while length<=n:
            angle=2*math.pi/length*(-1 if invert else 1);root=complex(math.cos(angle),math.sin(angle))
            for start in range(0,n,length):
                factor=1+0j
                for offset in range(length//2):
                    left=values[start+offset];right=values[start+offset+length//2]*factor
                    values[start+offset]=left+right;values[start+offset+length//2]=left-right;factor*=root
            length*=2
        if invert:
            for i in range(n):values[i]/=n
    fft(first,False);fft(second,False)
    for i in range(n):first[i]*=second[i]
    fft(first,True)
    return [round(first[i].real) for i in range(size)]
'''


SWAPS = '''def minimum_digit_sum_sort_swaps(nums):
    ordered=sorted(nums,key=lambda value:(sum(map(int,str(value))),value));destination={value:i for i,value in enumerate(ordered)}
    visited=[False]*len(nums);answer=0
    for start in range(len(nums)):
        if visited[start]:continue
        length=0;index=start
        while not visited[index]:visited[index]=True;length+=1;index=destination[nums[index]]
        answer+=max(0,length-1)
    return answer
'''


PORTALS = '''def minimum_portal_moves(matrix):
    from collections import defaultdict,deque
    rows=len(matrix);columns=len(matrix[0]);portals=defaultdict(list)
    for row in range(rows):
        for column,cell in enumerate(matrix[row]):
            if cell.isalpha():portals[cell].append((row,column))
    infinity=10**30;distance=[[infinity]*columns for _ in range(rows)];distance[0][0]=0;queue=deque([(0,0)])
    while queue:
        row,column=queue.popleft();current=distance[row][column]
        if (row,column)==(rows-1,columns-1):return current
        cell=matrix[row][column]
        if cell in portals:
            for next_row,next_column in portals.pop(cell):
                if current<distance[next_row][next_column]:distance[next_row][next_column]=current;queue.appendleft((next_row,next_column))
        for next_row,next_column in ((row-1,column),(row+1,column),(row,column-1),(row,column+1)):
            if 0<=next_row<rows and 0<=next_column<columns and matrix[next_row][next_column]!='#' and current+1<distance[next_row][next_column]:
                distance[next_row][next_column]=current+1;queue.append((next_row,next_column))
    return -1
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]


EDGE_CASES=[[n,edges] for n,edges in [(2,[[0,1]]),(3,[[0,1],[1,2]]),(3,[[0,1],[1,2],[2,0]]),(4,[[0,2],[2,1],[1,3]]),(4,[[0,1],[1,2],[2,3],[3,0]]),(5,[[0,1],[1,2],[2,3],[3,4]]),(5,[[0,2],[2,4],[4,1],[1,3],[3,0]]),(6,[[0,5],[5,2],[2,1],[1,4],[4,3]]),(6,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,0]]),(7,[[6,2],[2,0],[0,5],[5,1],[1,4],[4,3]]),(7,[[0,3],[3,6],[6,2],[2,5],[5,1],[1,4],[4,0]]),(8,[[0,7],[7,1],[1,6],[6,2],[2,5],[5,3],[3,4]]),(4,[[3,1],[1,0],[0,2]]),(5,[[4,0],[0,3],[3,1],[1,2]])]]
PARTITION_CASES=[[grid] for grid in [[[1,2],[3,4]],[[1,2,4],[2,3,5]],[[4,1,8],[3,2,6]],[[1,1]],[[1],[1]],[[1,2]],[[1],[2]],[[1,1,1]],[[1,2,1]],[[1],[2],[1]],[[1,3],[2,2]],[[5,1,2],[1,1,4]],[[2,7,2],[3,1,3]],[[9,1],[2,2],[3,3]]]]
POLYNOMIAL_CASES=[[a,b] for a,b in [([1],[1]),([0],[5]),([-1],[7]),([1,1],[1,1]),([1,-1],[1,1]),([0,0,1],[0,2]),([2,3],[4,5]),([-2,3],[4,-5]),([1,0,-2],[-1]),([1,5,-3],[-4,2,0]),([9,-8,7],[6,-5,4]),([0,1,0,1],[1,0,1]),([3],[1,2,3,4]),([2,-1,3,-4],[5,0,-2])]]
SWAP_CASES=[[[*nums]] for nums in [[1],[10,2],[2,10],[11,2,30],[9,18,27],[99,1,20,3],[12,21,3,30],[100,37,22,14],[18,43,34,16],[5,40,13,22,31],[91,82,73,64,55],[123,45,6,78],[19,28,37,46,55],[400,31,22,13,4]]]
PORTAL_CASES=[[matrix] for matrix in [['.'],['..'],['.#'],['...'],['.#.','...'],['A#A','...'],['A..','.A.','...'],['A#B','.#.','B.A'],['..#','###','...'],['AB','BA'],['A.B','###','B.A'],['....','....'],['.#...','.#.#.','.#.#.','...#.'],['A#..','.#A.','B..B','...#']]]


BATCH={
3547:entry('maximum_edge_value_sum',[('n','int'),('edges','list[list[int]]')],'int',['graphs','greedy','rearrangement'],['The graph is connected, has up to 50,000 nodes, and every node has degree at most two.','Assign every value from 1 through n to exactly one node.','Maximize the sum of endpoint-value products over all edges.'],[([4,[[0,1],[1,2],[2,3]]],'An optimal path ordering contributes 1*3 + 3*4 + 4*2 = 23.'),([6,[[0,3],[4,5],[2,0],[1,3],[2,4],[1,5]]],'The graph is a cycle; arranging nearby large values carefully gives score 82.')],EDGE_CASES,EDGE_SCORE,[EDGE_SCORE.replace("if len(edges)==n:","if len(edges)!=n:"),EDGE_SCORE.replace("list(range(2,n+1,2))","list(range(1,n+1,2))")],['Uses the cycle arrangement for paths and the path arrangement for cycles.','Starts the path with odd values, losing high-value adjacencies.'],edge_score_oracle,random_edge_score,lesson('A connected degree-two graph is either a path or a cycle, so only the best linear or circular ordering of 1..n matters.','Place large values next to other large values using the pendulum ordering; a cycle closes the two smallest endpoints.','Detect a cycle by edges==n, construct the corresponding alternating-parity order, and sum neighboring products.','The rearrangement exchange argument forces larger values to receive larger neighboring sums; the pendulum order satisfies those inequalities and is optimal.'),'O(n)','O(n)',8),
3548:entry('can_partition_grid_with_discount',[('grid','list[list[int]]')],'bool',['matrices','prefix sums','hash maps'],['The positive grid contains between 2 and 100,000 cells.','Make one horizontal or vertical cut into two nonempty rectangles.','The sums must match directly or after discounting one cell while its remaining section stays connected.'],[([[[1,4],[2,3]]],'A horizontal cut gives equal sums of five without a discount.'),([[[1,2],[3,4]]],'A vertical cut gives sums four and six; discounting the boundary value two preserves connectivity and balances them.')],PARTITION_CASES,PARTITION_DISCOUNT,[PARTITION_DISCOUNT.replace("if section[0][0]==difference or section[0][-1]==difference", "if difference in section[0]"),PARTITION_DISCOUNT.replace("if upper==lower:return True", "if upper==lower:return False")],['Allows removing an interior cell from a one-row section even though it disconnects that section.','Rejects already equal sections instead of accepting the cut immediately.'],partition_discount_oracle,random_partition_discount,lesson('For a fixed cut, only the heavier side can lose a positive cell, and the removed value must equal the sum difference.','Sweep row cuts while maintaining value counts on both sides, then transpose and repeat for column cuts.','At each boundary compare sums; otherwise locate the difference in the heavy side and enforce endpoint removal for one-dimensional sections.','Counts establish whether the needed value exists, while rectangular connectivity is automatic after one removal except for an interior cell of a single row or column.'),'O(rows*columns)','O(distinct values)',8),
3549:entry('multiply_polynomials',[('poly1','list[int]'),('poly2','list[int]')],'list[int]',['math','divide and conquer','fast Fourier transform'],['Each nonempty array stores coefficients in ascending exponent order.','Return exactly len(poly1)+len(poly2)-1 integer coefficients.','Use fast convolution rather than multiplying every coefficient pair for large inputs.'],[([[3,2,5],[1,4]],'The coefficients are 3, 3*4+2*1=14, 2*4+5*1=13, and 5*4=20.'),([[1,0,-2],[-1]],'Multiplication by the constant -1 negates every coefficient, giving [-1,0,2].')],POLYNOMIAL_CASES,POLYNOMIAL,[POLYNOMIAL.replace("range(size)","range(size-1)"),POLYNOMIAL.replace("first[i]*=second[i]","first[i]*=first[i]")],['Drops the highest-degree coefficient by returning one position too few.','Squares the first transformed polynomial instead of multiplying the two transforms.'],polynomial_oracle,random_polynomial,lesson('Polynomial multiplication is convolution: output degree k sums first[i]*second[k-i].','Pad to a power of two, transform both coefficient arrays, multiply pointwise, and apply the inverse transform.','Run iterative bit-reversal FFT, combine spectra, invert, divide by n, and round the real coefficients.','The Fourier transform converts convolution into pointwise multiplication; inverse transformation recovers every coefficient in O(n log n).'),'O((m+n) log(m+n))','O(m+n)',8),
3551:entry('minimum_digit_sum_sort_swaps',[('nums','list[int]')],'int',['arrays','sorting','permutations'],['nums contains up to 100,000 distinct positive integers.','Order values by digit sum, breaking ties by the numerical value.','A swap may exchange any two positions; return the minimum count.'],[([[37,100]],'Digit sums are ten and one, so the two values need one swap.'),([[22,14,33,7]],'Digit sums are already increasing from four through seven, so no swaps are needed.')],SWAP_CASES,SWAPS,[SWAPS.replace("sum(map(int,str(value)))","value"),SWAPS.replace("answer+=max(0,length-1)","answer+=length")],['Sorts by numeric value instead of digit sum with numeric tie-breaking.','Counts the number of elements in each cycle instead of the required cycle length minus one swaps.'],swap_oracle,random_swaps,lesson('Once the target order is fixed, current positions map to a permutation of target positions.','Sort by (digit sum,value), decompose the position mapping into cycles, and add cycle length minus one.','Build value-to-target-index, follow each unvisited cycle, and accumulate max(0,length-1).','A cycle of length L needs at least L-1 swaps and can always be corrected in exactly L-1 swaps; distinct values make the mapping unique.'),'O(n log n)','O(n)',5),
3552:entry('minimum_portal_moves',[('matrix','list[str]')],'int',['graphs','breadth first search','matrices'],['matrix has at most 1,000 rows and columns; the start is not blocked.','Orthogonal movement costs one; teleporting between equal uppercase letters costs zero.','Each portal letter may be activated at most once; return -1 when the goal is unreachable.'],[([['A..','.A.','...']],'Teleport from the starting A to the center for free, then take two moves to the goal.'),([['.#...','.#.#.','.#.#.','...#.']],'The only open route winds around the barriers and requires 13 moves.')],PORTAL_CASES,PORTALS,[PORTALS.replace("distance[next_row][next_column]=current;queue.appendleft", "distance[next_row][next_column]=current+1;queue.append"),PORTALS.replace("if cell in portals:", "if False and cell in portals:")],['Charges one move for a teleport although teleportation is free.','Never activates portals, so it misses shorter routes and portal-only connections.'],portal_oracle,random_portal,lesson('Grid moves have weight one and teleports weight zero, so shortest paths form a 0-1 BFS problem.','Index cells by portal letter; expand a letter once, putting zero-cost destinations at the deque front.','Pop a cell, expand and delete its portal group at the same distance, then enqueue unvisited walkable neighbors at distance+1.','The first expansion of a letter occurs at its minimum distance, so later expansions cannot improve any portal destination and the group is safely discarded.'),'O(rows*columns)','O(rows*columns)',5),
}
