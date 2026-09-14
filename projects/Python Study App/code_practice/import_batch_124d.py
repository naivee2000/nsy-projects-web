"""Fourth slice of workbook batch 124."""

from collections import Counter
from itertools import permutations

from .import_batch_055 import entry


def digit_sum_oracle(args):
    text, size = args
    while len(text) > size:
        text = "".join(str(sum(map(int, text[start:start + size]))) for start in range(0, len(text), size))
    return text


def random_digit_sum(rng):
    return ["".join(str(rng.randrange(10)) for _ in range(rng.randint(2, 40))), rng.randint(2, 8)]


def rounds_oracle(args):
    answer = 0
    for count in Counter(args[0]).values():
        possible = [twos + threes for twos in range(count // 2 + 1) for threes in range(count // 3 + 1)
                    if 2 * twos + 3 * threes == count]
        if not possible:
            return -1
        answer += min(possible)
    return answer


def random_rounds(rng):
    return [[rng.randint(1, 8) for _ in range(rng.randint(1, 35))]]


def factors(value):
    twos = fives = 0
    while value % 2 == 0:
        twos += 1
        value //= 2
    while value % 5 == 0:
        fives += 1
        value //= 5
    return twos, fives


def zeros_oracle(args):
    grid = args[0]
    rows, columns = len(grid), len(grid[0])
    best = 0
    for row in range(rows):
        for column in range(columns):
            for vertical in (-1, 1):
                vertical_cells = [(row, column)]
                nr = row + vertical
                while 0 <= nr < rows:
                    vertical_cells.append((nr, column)); nr += vertical
                for horizontal in (-1, 1):
                    horizontal_cells = []
                    nc = column + horizontal
                    while 0 <= nc < columns:
                        horizontal_cells.append((row, nc)); nc += horizontal
                    for vlen in range(1, len(vertical_cells) + 1):
                        for hlen in range(len(horizontal_cells) + 1):
                            counts = [factors(grid[r][c]) for r, c in vertical_cells[:vlen] + horizontal_cells[:hlen]]
                            best = max(best, min(sum(x for x, _ in counts), sum(y for _, y in counts)))
    return best


def random_zeros(rng):
    rows, columns = rng.randint(1, 4), rng.randint(1, 4)
    return [[[rng.randint(1, 100) for _ in range(columns)] for _ in range(rows)]]


def path_oracle(args):
    parent, labels = args
    graph = [[] for _ in parent]
    for node in range(1, len(parent)):
        graph[parent[node]].append(node); graph[node].append(parent[node])
    best = 1
    def walk(node, previous, length):
        nonlocal best
        best = max(best, length)
        for neighbor in graph[node]:
            if neighbor != previous and labels[neighbor] != labels[node]:
                walk(neighbor, node, length + 1)
    for start in range(len(parent)):
        walk(start, -1, 1)
    return best


def random_path(rng):
    n = rng.randint(1, 11)
    return [[-1] + [rng.randrange(node) for node in range(1, n)], "".join(rng.choice("abc") for _ in range(n))]


def trip_oracle(args):
    n, highways, steps = args
    costs = {tuple(sorted((left, right))): cost for left, right, cost in highways}
    best = -1
    for route in permutations(range(n), steps + 1):
        edges = [tuple(sorted((route[index], route[index + 1]))) for index in range(steps)]
        if all(edge in costs for edge in edges):
            best = max(best, sum(costs[edge] for edge in edges))
    return best


def random_trip(rng):
    n = rng.randint(2, 8)
    highways = [[left, right, rng.randint(1, 30)] for left in range(n) for right in range(left + 1, n) if rng.randrange(3) == 0]
    return [n, highways, rng.randint(0, min(n - 1, 5))]


DIGIT_SUM = '''\
def repeated_group_digit_sum(s,k):
    while len(s)>k:
        pieces=[]
        for start in range(0,len(s),k):pieces.append(str(sum(int(char) for char in s[start:start+k])))
        s=''.join(pieces)
    return s
'''

ROUNDS = '''\
def minimum_task_rounds(tasks):
    from collections import Counter
    answer=0
    for count in Counter(tasks).values():
        if count==1:return -1
        answer+=(count+2)//3
    return answer
'''

ZEROS = '''\
def maximum_corner_path_trailing_zeros(grid):
    rows,columns=len(grid),len(grid[0]);two=[[0]*columns for _ in range(rows)];five=[[0]*columns for _ in range(rows)]
    for row in range(rows):
        for column in range(columns):
            value=grid[row][column]
            while value%2==0:two[row][column]+=1;value//=2
            while value%5==0:five[row][column]+=1;value//=5
    row_two=[[0]*(columns+1) for _ in range(rows)];row_five=[[0]*(columns+1) for _ in range(rows)]
    col_two=[[0]*columns for _ in range(rows+1)];col_five=[[0]*columns for _ in range(rows+1)]
    for row in range(rows):
        for column in range(columns):
            row_two[row][column+1]=row_two[row][column]+two[row][column];row_five[row][column+1]=row_five[row][column]+five[row][column]
            col_two[row+1][column]=col_two[row][column]+two[row][column];col_five[row+1][column]=col_five[row][column]+five[row][column]
    answer=0
    for row in range(rows):
        for column in range(columns):
            arms=[(row_two[row][column+1],row_five[row][column+1]),(row_two[row][columns]-row_two[row][column],row_five[row][columns]-row_five[row][column]),(col_two[row+1][column],col_five[row+1][column]),(col_two[rows][column]-col_two[row][column],col_five[rows][column]-col_five[row][column])]
            for horizontal in arms[:2]:
                for vertical in arms[2:]:answer=max(answer,min(horizontal[0]+vertical[0]-two[row][column],horizontal[1]+vertical[1]-five[row][column]))
    return answer
'''

PATH = '''\
def longest_different_adjacent_path(parent,s):
    children=[[] for _ in parent]
    for node in range(1,len(parent)):children[parent[node]].append(node)
    answer=1
    def visit(node):
        nonlocal answer
        first=second=0
        for child in children[node]:
            length=visit(child)
            if s[child]==s[node]:continue
            if length>first:second,first=first,length
            elif length>second:second=length
        answer=max(answer,first+second+1)
        return first+1
    visit(0)
    return answer
'''

TRIP = '''\
def maximum_k_highway_trip(n,highways,k):
    graph=[[] for _ in range(n)]
    for left,right,cost in highways:graph[left].append((right,cost));graph[right].append((left,cost))
    states={(1<<node,node):0 for node in range(n)}
    for _ in range(k):
        updated={}
        for (mask,node),value in states.items():
            for neighbor,cost in graph[node]:
                if mask>>neighbor&1==0:
                    key=(mask|1<<neighbor,neighbor);updated[key]=max(updated.get(key,-1),value+cost)
        states=updated
    return max(states.values(),default=-1)
'''


BATCH = {
    2243: entry('repeated_group_digit_sum',[('s','str'),('k','int')],'str',['strings','simulation'],['s contains digits and k is at least two.','While len(s)>k, partition from the left into consecutive groups of at most k digits.','Replace each group by its decimal digit sum and concatenate the sums.'],[(['11111222223',3],'The first grouping gives 3465; grouping that result gives 135.'),(['00000000',3],'Every group sum is zero, so repeated transformation returns 000.')],[[s,k] for s,k in [('12',2),('123',2),('11111222223',3),('00000000',3),('987654321',4),('9999',2),('1010101',3),('5',2),('123456',6),('1234567',6),('2222222222',4),('3141592653',3),('1000000001',2),('909090909',5)]],DIGIT_SUM,[DIGIT_SUM.replace('len(s)>k','len(s)>=k'),DIGIT_SUM.replace('range(0,len(s),k)','range(0,len(s)-k,k)')],['Transforms again when length already equals k, contrary to the stopping rule.','Drops the final group, especially when its length is less than k.'],digit_sum_oracle,random_digit_sum,['Each transformation is a direct left-to-right grouping pass.','Convert each group’s characters to integers, sum them, stringify the result, and concatenate.','Repeat full passes only while the current length exceeds k.','A pass constructs exactly the specified replacement string; length decreases until the stopping condition is reached.'],'O(total processed characters)','O(n)',3),
    2244: entry('minimum_task_rounds',[('tasks','list[int]')],'int',['arrays','hash maps','greedy'],['Each round completes exactly two or exactly three tasks of one difficulty.','All tasks must be completed; tasks of different difficulties cannot share a round.','Return -1 if any difficulty occurs only once.'],[([[2,2,3,3,2,4,4,4,4,4]],'The counts three, two, and five need one, one, and two rounds, totaling four.'),([[2,3,3]],'Difficulty two occurs once, making completion impossible.')],[[x] for x in [[1],[1,1],[1,1,1],[1,1,1,1],[2,2,3,3,2,4,4,4,4,4],[2,3,3],[1,1,2,2],[5,5,5,5,5],[1,1,1,2,2,2],[7,7,7,7,7,7,7],[1,2,3],[4,4,4,4,4,4],[9,9,9,9,9,9,9,9],[1,1,2,2,2,3,3,3,3]]],ROUNDS,[ROUNDS.replace('(count+2)//3','count//3'),ROUNDS.replace('count==1','count<3')],['Uses floor division and undercounts remainders that need a two-task round.','Incorrectly declares every count of two impossible.'],rounds_oracle,random_rounds,['Each difficulty count can be handled independently.','Use as many groups of three as possible, replacing a remainder one with two groups of two.','If count is one return -1; otherwise add ceil(count/3), written (count+2)//3.','For every count at least two, ceil(count/3) groups suffice using twos and threes and fewer groups cannot cover all tasks.'],'O(n)','O(distinct difficulties)',5),
    2245: entry('maximum_corner_path_trailing_zeros',[('grid','list[list[int]]')],'int',['matrices','prefix sums','math'],['A path moves horizontally and vertically, turns at most once, and never revisits a cell.','Its product trailing-zero count is min(total factors of two,total factors of five).','Return the maximum over straight paths, single cells, and all four corner orientations.'],[([[[23,17,15,3,20],[8,1,20,27,11],[9,4,6,2,21],[40,9,1,10,6],[22,7,4,5,3]]],'An optimal corner product contains three matched factor pairs of two and five.'),([[[10,20],[25,4]]],'A path through all but one suitable corner can accumulate three trailing zeros.')],[[g] for g in [[[1]],[[10]],[[2,5]],[[10,20],[25,4]],[[1,1],[1,1]],[[25,2],[4,5]],[[100,1,1]],[[2],[5],[10]],[[4,5,10],[25,2,8]],[[3,6],[9,12]],[[50,40,25],[8,5,2]],[[7,10,7],[5,4,20]],[[2,4,8],[5,25,125]],[[10,1,10],[1,10,1],[10,1,10]]]],ZEROS,[ZEROS.replace('-two[row][column]','').replace('-five[row][column]',''),ZEROS.replace('min(horizontal[0]+vertical[0]-two[row][column],horizontal[1]+vertical[1]-five[row][column])','max(horizontal[0]+vertical[0]-two[row][column],horizontal[1]+vertical[1]-five[row][column])')],['Counts the turning cell twice in both factor totals.','Uses the larger prime-factor total instead of the matched minimum that forms powers of ten.'],zeros_oracle,random_zeros,['Trailing zeros depend only on counts of prime factors two and five.','Build row and column prefix sums for both factor counts, then combine one horizontal arm with one vertical arm at each turn.','Subtract the pivot once because both inclusive arms contain it; score each orientation with min(twos,fives).','Every allowed corner chooses one of four arm pairs, and prefix sums give its exact factor totals, so taking their maximum covers all paths.'],'O(rows*columns*log value)','O(rows*columns)',7),
    2246: entry('longest_different_adjacent_path',[('parent','list[int]'),('s','str')],'int',['trees','depth first search','dynamic programming'],['parent describes a rooted tree at node zero and s gives one character per node.','A valid simple path may start and end anywhere, but adjacent path nodes must have different characters.','Return path length measured in nodes.'],[([[-1,0,0,1,1,2],'abacbe'],'The longest valid path contains three nodes.'),([[-1,0,0,0],'aabc'],'A path through the root can join the b and c children for length three.')],[[p,s] for p,s in [([-1],'a'),([-1,0],'ab'),([-1,0],'aa'),([-1,0,0,1,1,2],'abacbe'),([-1,0,0,0],'aabc'),([-1,0,1,2],'abcd'),([-1,0,1,2],'aaaa'),([-1,0,0,1,1],'ababa'),([-1,0,0,1,2,2],'abcdef'),([-1,0,0,0,0],'abcde'),([-1,0,1,1,2,2],'ababab'),([-1,0,0,2,2,4],'abbaca'),([-1,0,1,1,3,3,5],'abacaba'),([-1,0,0,1,1,2,2],'bacabca')]],PATH,[PATH.replace('first+second+1','first+1'),PATH.replace('s[child]==s[node]','s[child]!=s[node]')],['Keeps only one descending branch and misses paths joining two children.','Skips children with different characters and retains invalid equal-character edges.'],path_oracle,random_path,['A longest path has a highest node where up to two downward chains meet.','Postorder DFS returns the longest valid downward chain and tracks the two best compatible child chains.','At each node update the global answer with first+second+1 and return first+1.','Every simple tree path has a unique highest node; its two branches are considered there, while returned chains support ancestors.'],'O(n)','O(n)',8),
    2247: entry('maximum_k_highway_trip',[('n','int'),('highways','list[list[int]]'),('k','int')],'int',['graphs','bitmask dynamic programming'],['Highways are undirected weighted edges between distinct cities.','A trip crosses exactly k highways and may visit each city at most once; it may start anywhere.','Return the maximum toll sum or -1 if no such simple trip exists.'],[([5,[[0,1,4],[2,1,3],[1,4,11],[3,2,3],[3,4,2]],3],'The best three-highway simple trip costs seventeen.'),([3,[[0,1,2]],2],'Only one highway is available, so no trip can cross exactly two.')],[[n,h,k] for n,h,k in [(2,[],0),(2,[[0,1,5]],1),(3,[[0,1,2]],2),(5,[[0,1,4],[2,1,3],[1,4,11],[3,2,3],[3,4,2]],3),(4,[[0,1,1],[1,2,2],[2,3,3]],3),(4,[[0,1,5],[0,2,6],[0,3,7]],2),(5,[[0,1,10],[1,2,10],[2,3,1],[3,4,1],[0,4,50]],2),(3,[[0,1,4],[1,2,5],[0,2,3]],2),(6,[[0,1,1],[1,2,2],[2,3,3],[3,4,4],[4,5,5]],4),(4,[],1),(5,[[0,1,8],[2,3,9]],1),(5,[[0,1,2],[1,2,3],[2,0,4],[2,3,5],[3,4,6]],4),(6,[[0,1,7],[1,2,6],[2,3,5],[3,4,4],[4,5,3],[0,5,20]],3),(4,[[0,1,2],[1,2,2],[2,3,2],[3,0,2]],3)]],TRIP,[TRIP.replace('range(k)','range(max(0,k-1))'),TRIP.replace('mask>>neighbor&1==0','True')],['Builds trips with only k-1 highways.','Allows revisiting cities and can score an invalid cyclic walk.'],trip_oracle,random_trip,['The visited-city set and current endpoint completely describe what extensions remain legal.','Store the best cost for each (bitmask,last city), starting with every one-city trip.','Repeat k times: extend along an edge only to an unvisited city and maximize the new state.','Each transition appends one distinct city and one highway; after k layers the states are exactly all legal trips of the required length.'],'O(k*2^n*edges)','O(2^n*n)',8),
}
