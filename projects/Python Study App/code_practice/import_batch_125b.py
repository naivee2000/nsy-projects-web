"""Second slice of workbook batch 125."""

from collections import deque

from .import_batch_055 import entry


def average_oracle(args):
    nums = args[0]
    candidates = []
    for index in range(len(nums)):
        left = sum(nums[:index + 1]) // (index + 1)
        right = sum(nums[index + 1:]) // (len(nums) - index - 1) if index + 1 < len(nums) else 0
        candidates.append(abs(left - right))
    return candidates.index(min(candidates))


def random_average(rng):
    return [[rng.randint(0, 100) for _ in range(rng.randint(1, 30))]]


def guards_oracle(args):
    rows, columns, guards, walls = args
    blocked = {tuple(cell) for cell in guards + walls}
    seen = set()
    for row, column in guards:
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = row + dr, column + dc
            while 0 <= nr < rows and 0 <= nc < columns and (nr,nc) not in blocked:
                seen.add((nr,nc)); nr += dr; nc += dc
    return rows * columns - len(blocked) - len(seen)


def random_guards(rng):
    rows, columns = rng.randint(1, 7), rng.randint(1, 7)
    cells = [(r,c) for r in range(rows) for c in range(columns)]
    rng.shuffle(cells)
    first = rng.randint(0, len(cells))
    second = rng.randint(first, len(cells))
    return [rows, columns, [list(cell) for cell in cells[:first]], [list(cell) for cell in cells[first:second]]]


def fire_oracle(args):
    grid = args[0]
    rows, columns = len(grid), len(grid[0])
    directions = ((1,0),(-1,0),(0,1),(0,-1))

    def spread(fire):
        result = set(fire)
        for row, column in fire:
            for dr, dc in directions:
                nr, nc = row + dr, column + dc
                if 0 <= nr < rows and 0 <= nc < columns and grid[nr][nc] != 2:
                    result.add((nr,nc))
        return result

    def escape(wait):
        fire = {(r,c) for r in range(rows) for c in range(columns) if grid[r][c] == 1}
        for _ in range(wait):
            fire = spread(fire)
            if (0,0) in fire:
                return False
        people = {(0,0)}
        visited = {(0,0)}
        while people:
            moved = set()
            for row, column in people:
                for dr, dc in directions:
                    cell = row + dr, column + dc
                    if cell == (rows-1,columns-1) and cell not in fire:
                        return True
                    if 0 <= cell[0] < rows and 0 <= cell[1] < columns and grid[cell[0]][cell[1]] == 0 and cell not in fire and cell not in visited:
                        moved.add(cell); visited.add(cell)
            fire = spread(fire)
            people = moved - fire
        return False

    if not escape(0):
        return -1
    limit = rows * columns * 2 + 5
    if escape(limit):
        return 1_000_000_000
    answer = 0
    for wait in range(1, limit + 1):
        if escape(wait): answer = wait
        else: break
    return answer


def random_fire(rng):
    rows, columns = rng.randint(2, 5), rng.randint(2, 5)
    grid = [[rng.choices([0,1,2],[7,1,2])[0] for _ in range(columns)] for _ in range(rows)]
    grid[0][0] = grid[-1][-1] = 0
    return [grid]


def remove_oracle(args):
    number, digit = args
    return max(number[:index] + number[index + 1:] for index, char in enumerate(number) if char == digit)


def random_remove(rng):
    number = "".join(str(rng.randint(1 if index == 0 else 0, 9)) for index in range(rng.randint(2, 15)))
    return [number, rng.choice(number)]


def cards_oracle(args):
    cards = args[0]
    lengths = [right - left + 1 for left in range(len(cards)) for right in range(left + 1, len(cards)) if cards[left] == cards[right]]
    return min(lengths, default=-1)


def random_cards(rng):
    return [[rng.randint(1, 12) for _ in range(rng.randint(1, 35))]]


AVERAGE = '''\
def minimum_average_difference_index(nums):
    total=sum(nums);prefix=0;best=float('inf');answer=0
    for index,value in enumerate(nums):
        prefix+=value
        left=prefix//(index+1);right=(total-prefix)//(len(nums)-index-1) if index+1<len(nums) else 0
        difference=abs(left-right)
        if difference<best:best=difference;answer=index
    return answer
'''

GUARDS = '''\
def count_unguarded_cells(m,n,guards,walls):
    blocked={tuple(cell) for cell in guards+walls};guarded=set()
    for row,column in guards:
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=row+dr,column+dc
            while 0<=nr<m and 0<=nc<n and (nr,nc) not in blocked:
                guarded.add((nr,nc));nr+=dr;nc+=dc
    return m*n-len(blocked)-len(guarded)
'''

FIRE = '''\
def maximum_fire_wait(grid):
    from collections import deque
    rows,columns=len(grid),len(grid[0]);infinity=10**12;fire=[[infinity]*columns for _ in range(rows)];queue=deque()
    for row in range(rows):
        for column in range(columns):
            if grid[row][column]==1:fire[row][column]=0;queue.append((row,column))
    directions=((1,0),(-1,0),(0,1),(0,-1))
    while queue:
        row,column=queue.popleft()
        for dr,dc in directions:
            nr,nc=row+dr,column+dc
            if 0<=nr<rows and 0<=nc<columns and grid[nr][nc]!=2 and fire[nr][nc]==infinity:
                fire[nr][nc]=fire[row][column]+1;queue.append((nr,nc))
    def can(wait):
        if wait>=fire[0][0]:return False
        queue=deque([(0,0,wait)]);seen={(0,0)}
        while queue:
            row,column,time=queue.popleft()
            if (row,column)==(rows-1,columns-1):return True
            for dr,dc in directions:
                nr,nc=row+dr,column+dc;arrival=time+1
                if 0<=nr<rows and 0<=nc<columns and grid[nr][nc]==0 and (nr,nc) not in seen:
                    safe=arrival<=fire[nr][nc] if (nr,nc)==(rows-1,columns-1) else arrival<fire[nr][nc]
                    if safe:seen.add((nr,nc));queue.append((nr,nc,arrival))
        return False
    if not can(0):return -1
    if can(1000000000):return 1000000000
    low,high=0,1000000000
    while low<high:
        middle=(low+high+1)//2
        if can(middle):low=middle
        else:high=middle-1
    return low
'''

REMOVE = '''\
def remove_digit_for_largest_number(number,digit):
    best=''
    for index,char in enumerate(number):
        if char==digit:best=max(best,number[:index]+number[index+1:])
    return best
'''

CARDS = '''\
def minimum_matching_card_pickup(cards):
    latest={};answer=float('inf')
    for index,value in enumerate(cards):
        if value in latest:answer=min(answer,index-latest[value]+1)
        latest[value]=index
    return -1 if answer==float('inf') else answer
'''


BATCH = {
    2256: entry('minimum_average_difference_index',[('nums','list[int]')],'int',['arrays','prefix sums'],['For index i, floor the average of nums[0:i+1] and the average of nums[i+1:n].','The average of the empty suffix at the last index is zero.','Minimize the absolute difference and return the smallest index on ties.'],[([[2,5,3,9,5,3]],'The floored prefix and suffix averages have their smallest difference at index three.'),([[0]],'The only index compares zero with the empty-suffix average zero.')],[[x] for x in [[1],[0],[2,5,3,9,5,3],[1,1],[1,2],[10,0],[0,0,0],[1,2,3,4],[4,3,2,1],[5,5,1,1],[100,1,1,1],[3,9,3,9],[2,0,2,0,2],[7,1,5,3,9]]],AVERAGE,[AVERAGE.replace('//(index+1)','/(index+1)'),AVERAGE.replace('difference<best','difference<=best')],['Uses true division instead of the required floored integer average.','Updates on equal differences and returns the largest tied index.'],average_oracle,random_average,['A running prefix sum gives both sides without repeated summation.','At index i, left=prefix//(i+1) and right=(total-prefix)//remaining, using zero for an empty suffix.','Track the first strictly smaller absolute difference during one scan.','Every index is evaluated with its exact floored averages, and strict improvement preserves the smallest index among ties.'],'O(n)','O(1)',5),
    2257: entry('count_unguarded_cells',[('m','int'),('n','int'),('guards','list[list[int]]'),('walls','list[list[int]]')],'int',['matrices','simulation'],['Guards and walls occupy distinct grid cells.','A guard sees in four cardinal directions until a wall, guard, or boundary blocks the ray.','Count empty cells unseen by every guard.'],[([4,6,[[0,0],[1,1],[2,3]],[[0,1],[2,2],[1,4]]],'After all blocked sight lines are traced, seven empty cells remain unguarded.'),([3,3,[[1,1]],[]],'The center guard sees its row and column, leaving the four corners unguarded.')],[[m,n,g,w] for m,n,g,w in [(1,1,[],[]),(1,2,[[0,0]],[]),(4,6,[[0,0],[1,1],[2,3]],[[0,1],[2,2],[1,4]]),(3,3,[[1,1]],[]),(3,3,[[1,1]],[[1,2]]),(2,2,[],[]),(2,3,[[0,0]],[[0,1]]),(4,4,[[0,0],[3,3]],[]),(4,4,[[0,1]],[[2,1]]),(1,5,[[0,2]],[[0,3]]),(5,1,[[2,0]],[[1,0]]),(3,4,[[1,0],[1,3]],[[1,2]]),(5,5,[[2,2]],[[2,1],[1,2],[2,3],[3,2]]),(2,4,[[0,0],[1,3]],[[0,2]])]],GUARDS,[GUARDS.replace("guards+walls","walls"),GUARDS.replace('len(guarded)','0')],['Does not let other guards block sight lines.','Never subtracts guarded empty cells from the result.'],guards_oracle,random_guards,['Store all occupied guard and wall coordinates as blockers.','Cast four rays from every guard, marking each empty cell until the first blocker or boundary.','Return total cells minus occupied cells minus the union of guarded cells.','Each ray matches one line of sight exactly, and the set counts cells seen by multiple guards only once.'],'O(m*n*guards worst case)','O(m*n)',6),
    2258: entry('maximum_fire_wait',[('grid','list[list[int]]')],'int',['matrices','breadth first search','binary search'],['Grid values are zero for grass, one for initial fire, and two for walls; start and safehouse are grass.','After each person move, fire spreads one step; entering the safehouse at the same minute as fire is allowed, but ties elsewhere are unsafe.','Return the maximum initial wait, -1 if escape is impossible immediately, or 1,000,000,000 if waiting is unbounded.'],[([[[0,2,0,0,0,0,0],[0,0,0,2,2,1,0],[0,2,0,0,1,2,0],[0,0,2,2,2,0,2],[0,0,0,0,0,0,0]]],'Waiting three minutes is feasible, while a fourth minute makes every safe route too late.'),([[[0,0,0],[2,2,0],[1,2,0]]],'Walls isolate the fire from the only route, so the wait is unbounded.')],[[g] for g in [[[0,0],[0,0]],[[0,1],[0,0]],[[0,2],[2,0]],[[0,0,0],[2,2,0],[1,2,0]],[[0,2,0,0,0,0,0],[0,0,0,2,2,1,0],[0,2,0,0,1,2,0],[0,0,2,2,2,0,2],[0,0,0,0,0,0,0]],[[0,0,0],[0,1,0],[0,0,0]],[[0,2,0],[0,2,0],[0,0,0]],[[0,0,0],[1,2,0],[0,0,0]],[[0,0],[1,0]],[[0,0,0,0],[0,2,2,0],[1,0,0,0]],[[0,0,0],[0,2,0],[1,2,0]],[[0,0,0],[2,1,2],[0,0,0]],[[0,0,0,0],[2,2,2,0],[1,0,0,0]],[[0,0,2],[1,0,2],[0,0,0]]]],FIRE,[FIRE.replace('arrival<=fire[nr][nc]','arrival<fire[nr][nc]'),FIRE.replace('if wait>=fire[0][0]','if wait>fire[0][0]')],['Disallows arriving at the safehouse simultaneously with fire.','Allows waiting until the starting cell is already burning.'],fire_oracle,random_fire,['First compute the earliest fire-arrival minute for every non-wall cell with multi-source BFS.','For a chosen wait, BFS the person using strict arrival before fire except non-strict arrival at the safehouse.','Check immediate escape, unbounded wait, then binary-search the greatest feasible wait.','Fire times are fixed independent of the person, feasibility is monotone in waiting time, and the BFS enforces the exact move-before-spread timing.'],'O(m*n log 1e9)','O(m*n)',8),
    2259: entry('remove_digit_for_largest_number',[('number','str'),('digit','str')],'str',['strings','greedy'],['number is a positive decimal string and digit occurs at least once.','Remove exactly one occurrence of digit.','Return the numerically largest resulting string; all candidates have equal length, so lexicographic order is valid.'],[(['123','3'],'Removing the only three leaves 12.'),(['1231','1'],'Removing the leading one yields 231, larger than removing the final one and getting 123.')],[[n,d] for n,d in [('123','3'),('1231','1'),('551','5'),('133235','3'),('111','1'),('9879','9'),('1001','0'),('7654321','4'),('22212','2'),('90909','9'),('314159','1'),('44445','4'),('12121','1'),('99998','9')]],REMOVE,[REMOVE.replace('max(best','min(best'),REMOVE.replace('number[index+1:]','number[index+2:]')],['Chooses the lexicographically smallest removal candidate.','Removes the selected digit and the following digit, producing the wrong length.'],remove_oracle,random_remove,['Every legal answer comes from deleting one matching position.','Because candidate lengths are identical, ordinary string comparison matches numeric comparison.','Enumerate matching indices, construct the deletion result, and keep the maximum string.','The enumeration covers every allowed deletion exactly once, so its maximum is the optimal result.'],'O(n^2)','O(n)',3),
    2260: entry('minimum_matching_card_pickup',[('cards','list[int]')],'int',['arrays','hash maps','sliding window'],['Pick one contiguous segment containing at least two equal card values.','The number picked is the inclusive segment length.','Return the minimum possible length, or -1 when every value is unique.'],[([[3,4,2,3,4,7]],'The two threes span indices zero through three, so four cards are enough.'),([[1,2,3]],'No value repeats, so no valid pickup segment exists.')],[[x] for x in [[1],[1,1],[1,2,3],[3,4,2,3,4,7],[1,2,1],[1,2,3,2],[5,5,5],[1,2,3,4,1],[7,8,9,7,8],[0,1,0,1],[2,3,4,5,3,2],[10,20,30,20],[4,1,2,3,4,3],[9,8,7,6,5]]],CARDS,[CARDS.replace('+1',''),CARDS.replace('latest[value]=index','latest.setdefault(value,index)')],['Returns the index distance instead of inclusive card count.','Keeps only the first occurrence and can miss a closer later pair.'],cards_oracle,random_cards,['For any repeated value, only consecutive occurrences can form its shortest enclosing segment.','Remember the latest index of each card value while scanning.','On a repeat, minimize index-latest[value]+1, then update the latest index.','Every candidate minimum ends at some occurrence and pairs with the closest prior equal value, which the map stores.'],'O(n)','O(distinct values)',5),
}

BATCH[2258]['boundaries'].append([[[0,0,0,0,0],[0,0,0,2,0],[1,2,0,2,0],[2,2,0,0,0]]])
BATCH[2258]['wrong'][1] = FIRE.replace('if not can(0):return -1', 'if not can(0):return 0')
BATCH[2258]['wrong_reasons'][1] = 'Returns zero waiting time when escape is impossible even without waiting.'
BATCH[2260]['boundaries'].append([[1,2,1,1]])
