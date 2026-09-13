"""Weighted rolling paths, affordable projects, circular stacks, and ring states."""
from collections import deque
from functools import cache
from random import Random

from .import_batch_003 import entry


def rolling_oracle(args, hole=False):
    """Build literal rays, then use synchronous Bellman-Ford, not heap search."""
    maze,start,target=args
    rows,cols=len(maze),len(maze[0])
    cells=[(r,c) for r in range(rows) for c in range(cols) if not maze[r][c]]
    edges=[]
    for r,c in cells:
        for letter,ray in [('u',[(i,c) for i in range(r-1,-1,-1)]),
                           ('d',[(i,c) for i in range(r+1,rows)]),
                           ('l',[(r,j) for j in range(c-1,-1,-1)]),
                           ('r',[(r,j) for j in range(c+1,cols)])]:
            traversed=[]
            for cell in ray:
                if maze[cell[0]][cell[1]]:break
                traversed.append(cell)
                if hole and list(cell)==target:break
            if traversed:edges.append(((r,c),traversed[-1],len(traversed),letter))
    best={tuple(start):(0,'')}
    # Positive-distance edges imply an optimal route never repeats a stop.
    for _ in range(len(cells)-1):
        updated=best.copy()
        for a,b,d,letter in edges:
            if a not in best or (hole and list(a)==target):continue
            candidate=(best[a][0]+d,best[a][1]+letter)
            if b not in updated or candidate<updated[b]:updated[b]=candidate
        if updated==best:break
        best=updated
    answer=best.get(tuple(target))
    return (answer[1] if hole else answer[0]) if answer else ('impossible' if hole else -1)


def hole_oracle(args):return rolling_oracle(args,True)
def maze_oracle(args):return rolling_oracle(args)


def ipo_oracle(args):
    k,w,profits,capital=args
    @cache
    def search(mask,left):
        money=w+sum(p for i,p in enumerate(profits) if mask>>i&1)
        best=money
        if left:
            for i,needed in enumerate(capital):
                if not mask>>i&1 and needed<=money:
                    best=max(best,search(mask|1<<i,left-1))
        return best
    return search(0,min(k,len(profits)))


def circular_oracle(args):
    nums=args[0];n=len(nums)
    return [next((nums[(i+d)%n] for d in range(1,n) if nums[(i+d)%n]>value),-1)
            for i,value in enumerate(nums)]


def ring_oracle(args):
    """Literal unit-action BFS: rotate one position or press one matching letter."""
    ring,key=args
    queue=deque([(0,0,0)]);seen={(0,0)}
    while queue:
        position,spelled,steps=queue.popleft()
        if spelled==len(key):return steps
        choices=[((position+1)%len(ring),spelled),((position-1)%len(ring),spelled)]
        if ring[position]==key[spelled]:choices.append((position,spelled+1))
        for state in choices:
            if state not in seen:
                seen.add(state);queue.append((*state,steps+1))


def random_maze(rng):
    rows,cols=rng.randint(1,5),rng.randint(2,5)
    maze=[[int(rng.random()<.3) for _ in range(cols)] for _ in range(rows)]
    a,b=rng.sample(range(rows*cols),2)
    start,target=list(divmod(a,cols)),list(divmod(b,cols))
    for r,c in (start,target):maze[r][c]=0
    return [maze,start,target]


def random_ipo(rng):
    n=rng.randint(1,7)
    return [rng.randint(1,8),rng.randrange(6),[rng.randrange(6) for _ in range(n)],
            [rng.randrange(15) for _ in range(n)]]


def random_circular(rng):return [[rng.randint(-5,5) for _ in range(rng.randint(1,20))]]
def random_ring(rng):
    ring=''.join(rng.choice('abcd') for _ in range(rng.randint(1,9)))
    return [ring,''.join(rng.choice(ring) for _ in range(rng.randint(1,10)))]


MAZE='''\
def shortest_rolling_distance(maze, start, destination):
    from heapq import heappush, heappop
    rows,cols=len(maze),len(maze[0])
    best={tuple(start):0}
    heap=[(0,*start)]
    while heap:
        distance,r,c=heappop(heap)
        if distance!=best[(r,c)]:continue
        if [r,c]==destination:return distance
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            x,y,steps=r,c,0
            while 0<=x+dr<rows and 0<=y+dc<cols and maze[x+dr][y+dc]==0:
                x+=dr;y+=dc;steps+=1
            candidate=distance+steps
            if steps and candidate<best.get((x,y),float('inf')):
                best[(x,y)]=candidate
                heappush(heap,(candidate,x,y))
    return -1
'''
HOLE='''\
def shortest_hole_instructions(maze, ball, hole):
    from heapq import heappush, heappop
    rows,cols=len(maze),len(maze[0])
    best={tuple(ball):(0,'')}
    heap=[(0,'',*ball)]
    while heap:
        distance,path,r,c=heappop(heap)
        if (distance,path)!=best[(r,c)]:continue
        if [r,c]==hole:return path
        for letter,dr,dc in (('d',1,0),('l',0,-1),('r',0,1),('u',-1,0)):
            x,y,steps=r,c,0
            while 0<=x+dr<rows and 0<=y+dc<cols and maze[x+dr][y+dc]==0:
                x+=dr;y+=dc;steps+=1
                if [x,y]==hole:break
            candidate=(distance+steps,path+letter)
            if steps and ((x,y) not in best or candidate<best[(x,y)]):
                best[(x,y)]=candidate
                heappush(heap,(*candidate,x,y))
    return 'impossible'
'''
IPO='''\
def maximize_project_capital(k, w, profits, capital):
    from heapq import heappush, heappop
    projects=sorted(zip(capital,profits))
    available=[];index=0
    for _ in range(min(k,len(projects))):
        while index<len(projects) and projects[index][0]<=w:
            heappush(available,-projects[index][1])
            index+=1
        if not available:break
        w-=heappop(available)
    return w
'''
CIRCULAR='''\
def circular_next_greater(nums):
    n=len(nums);answer=[-1]*n;pending=[]
    for step in range(2*n):
        i=step%n
        while pending and nums[pending[-1]]<nums[i]:
            answer[pending.pop()]=nums[i]
        if step<n:pending.append(i)
    return answer
'''
RING='''\
def freedom_trail_steps(ring, key):
    from functools import cache
    positions={}
    for i,char in enumerate(ring):positions.setdefault(char,[]).append(i)
    n=len(ring)
    @cache
    def spell(index,position):
        if index==len(key):return 0
        return min(min(abs(q-position),n-abs(q-position))+1+spell(index+1,q)
                   for q in positions[key[index]])
    return spell(0,0)
'''

MAZE_SAMPLE=[[0,0,1,0,0],[0,0,0,0,0],[0,0,0,1,0],[1,1,0,1,1],[0,0,0,0,0]]
HOLE_SAMPLE=[[0,0,0,0,0],[1,1,0,0,1],[0,0,0,0,0],[0,1,0,0,1],[0,1,0,0,0]]
MAZE_BOUNDARIES=[[[[0,0]],[0,0],[0,1]],[[[0,0,0]],[0,0],[0,1]],
    [[[0,0,0]],[0,2],[0,0]],[[[0],[0],[0]],[0,0],[1,0]],
    [[[0,1,0]],[0,0],[0,2]],[[[0,0],[0,0]],[0,0],[1,1]],
    [[[0,0,0],[0,0,0],[0,0,0]],[0,0],[1,1]],
    [[[0,0,0],[0,0,0],[0,0,0]],[1,1],[0,0]],
    [[[0,1,0],[0,1,0],[0,0,0]],[0,0],[0,2]],
    [[[0,0,0],[1,1,0],[0,0,0]],[0,0],[2,0]],
    [[[0,0,0],[0,1,0],[0,0,0]],[0,0],[2,2]],
    [[[0,0,0,0],[1,0,1,0],[0,0,0,0]],[0,0],[2,1]],
    [[[0,0,0,0],[0,1,1,0],[0,0,0,0]],[0,3],[2,0]]]


def snake_maze():
    maze=[[1]*100 for _ in range(100)]
    for r in range(0,100,2):
        maze[r]=[0]*100
        if r+1<99:maze[r+1][99 if r%4==0 else 0]=0
    return maze


def dense_maze():
    rng=Random(505049)
    maze=[[int(rng.random()<.22) for _ in range(100)] for _ in range(100)]
    maze[0][0]=maze[99][99]=0
    return maze


BATCH={
499:entry('shortest_hole_instructions',[('maze','list[list[int]]'),('ball','list[int]'),('hole','list[int]')],
    'str',['graphs','matrices','search','heaps','shortest-path'],
    ['1 <= rows, columns <= 100; maze is rectangular with only 0 (empty) and 1 (wall).',
     'ball and hole are distinct in-bounds empty cells, given as [row, column]. There are at least two empty cells.',
     'A roll continues to a wall or outside border, but entering the hole stops it immediately. A blocked direction is not a move.',
     'Minimize CELLS TRAVELED, not instruction count. Break distance ties by ordinary string order: d < l < r < u. Return "impossible" if unreachable.'],
    [([HOLE_SAMPLE,[4,3],[0,1]],'Both "lul" and "ul" travel 6 cells. Return "lul": l comes before u, even though "lul" uses more instructions.'),
     ([[[0,0,0,0,0]],[0,0],[0,2]],'Return "r": the ball falls into the hole after 2 cells, BEFORE reaching the right wall. A hole is not an ordinary stopping destination.')],
    MAZE_BOUNDARIES,
    HOLE,[HOLE.replace('if [x,y]==hole:break','if False:break'),
          HOLE.replace("candidate=(distance+steps,path+letter)","candidate=(distance+1,path+letter)")],
    ['Ignores a hole encountered before the wall.', 'Minimizes number of rolls instead of traveled cells.'],
    hole_oracle,random_maze,
    ['A state is a place where the ball stops; the hole can interrupt a roll.',
     'Use shortest-path labels containing both traveled distance and the instruction string.',
     'Pop the smallest (distance,path); simulate each nonempty roll until a wall or hole; relax using (distance+cells,path+direction).',
     'Compare full (distance,path) pairs, allowing a lexicographically better equal-distance update. Ignore stale heap entries and return only when the hole label is popped.'],
    'Each legal roll is a positive-weight edge. Dijkstra orders labels by distance first, '
    'then instruction string, so reaching the hole by fewer instructions is not necessarily optimal. '
    'A shortest path cannot revisit a stop, and equal-distance paths to one stop cannot be strict '
    'prefixes of one another (a suffix would be a positive-distance cycle). Thus lexicographic '
    'label dominance remains safe when appending a common suffix. The independent oracle builds '
    'literal directional rays and applies synchronous Bellman-Ford. With V=rows*columns and '
    'L at most V the largest stored instruction length, ray scanning costs O(V*(rows+columns)); '
    'string creation/comparison and heap work cost O(V*L*log V). Unlike The Maze, this returns an '
    'optimal string, and unlike The Maze II, the hole stops a roll before a wall.',
    'O(V*(rows+columns+L*log V))','O(V*L)',difficulty=8,
    stress=[([[[0]*100 for _ in range(100)],[0,0],[99,99]],'dr'),
            ([[[0]*100 for _ in range(100)],[0,0],[50,50]],'impossible'),
            ([[[0]*100],[0,0],[0,50]],'r'),
            ([snake_maze(),[0,0],[98,0]],'rdld'*24+'rdl'),
            ([dense_maze(),[0,0],[99,99]],'rdrdrdrurdrurdrurdrdrdrdrdrdldrurdrdrdldrdrdldldr')]),
502:entry('maximize_project_capital',[('k','int'),('w','int'),('profits','list[int]'),('capital','list[int]')],
    'int',['greedy','heaps','sorting'],
    ['1 <= k, n <= 100,000; profits and capital have equal length n.',
     '0 <= w, capital[i] <= 1,000,000,000; 0 <= profits[i] <= 10,000. The optimal final capital fits signed 32-bit.',
     'Select AT MOST k distinct project indices. Required capital is a threshold, NOT an expense; completing a project adds its pure profit.'],
    [([2,0,[1,2,3],[0,1,1]],'First take index 0 to grow capital from 0 to 1, then index 2 for profit 3. Final capital is 4; the threshold of 1 is not deducted.'),
     ([5,2,[4,7],[2,20]],'Only index 0 is affordable. It raises capital to 6, then you must stop: index 1 needs 20 and index 0 cannot be repeated. Return 6, although k is 5.')],
    [[1,0,[0],[0]],[1,0,[1],[1]],[1,1,[2],[1]],[3,0,[1],[0]],
     [1,0,[1,9],[0,0]],[2,0,[0,5],[0,1]],[3,0,[1,2,3],[0,1,2]],
     [2,1,[1,10,2],[0,2,0]],[1,10,[0,0],[0,10]],[4,2,[1,1,1],[2,2,2]],
     [2,0,[100,1],[2,0]],[2,10,[1,9,4],[10,9,10]],
     [1,10**9,[10000],[10**9]],[100000,0,[0],[0]]],
    IPO,[IPO.replace('w-=heappop(available)','w-=available[0]'),
         IPO.replace('projects[index][0]<=w','projects[index][0]<w')],
    ['Reuses the most profitable project rather than removing its index.', 'Rejects projects whose required capital exactly equals current capital.'],
    ipo_oracle,random_ipo,
    ['Capital requirements control eligibility; they are not subtracted.',
     'Sort by requirement and keep eligible, unused profits in a max-heap.',
     'Before each choice, push every newly affordable profit; pop the largest profit, add it to capital, and stop if the heap is empty.',
     'Because profits are nonnegative, choosing the largest affordable profit leaves at least as much capital for every future choice. Each index enters and leaves the heap at most once.'],
    'Exchange the first different choice of an optimal schedule with the largest currently '
    'affordable profit. Capital never decreases, so the replacement cannot make later choices '
    'infeasible; swapping a later occurrence avoids repeating a project. Sorted thresholds and '
    'a max-heap implement this greedy choice. Bound choices by min(k,n). The independent oracle '
    'enumerates feasible subsets in every possible order, preserving distinct indices.',
    'O(n log n + min(k,n)*log n)','O(n)',difficulty=8,
    stress=[([100000,0,[10000]*100000,[0]*100000],10**9),
            ([100000,0,[1]*100000,list(range(100000))],100000),
            ([100000,0,[10000]*100000,[1]*100000],0),
            ([100000,10**9,[10000]*100000,[10**9]*100000],2*10**9)]),
503:entry('circular_next_greater',[('nums','list[int]')],'list[int]',['arrays','stacks'],
    ['1 <= nums.length <= 10,000; -1,000,000,000 <= nums[i] <= 1,000,000,000.',
     'For each INDEX, scan right and wrap around once. Return the FIRST strictly greater value, or -1 if none; equal values do not qualify.'],
    [([[1,2,1]],'The last 1 wraps past the first 1 (equal is not greater) and finds 2. Return [2,-1,2].'),
     ([[5,1,3,2]],'The answers are [-1,3,5,5]. For 1, the first greater value is 3, not the global maximum 5.')],
    [[a] for a in ([1],[0],[-1],[1,1],[1,2],[2,1],[2,2,1],[1,1,2],[-3,-2,-1],
        [-1,-2,-3],[0,-1,0],[1,2,3,4,3],[3,1,2,1],[10**9,-10**9],[2,1,2,1])],
    CIRCULAR,[CIRCULAR.replace('range(2*n)','range(n)'),
              CIRCULAR.replace('nums[pending[-1]]<nums[i]','nums[pending[-1]]<=nums[i]')],
    ['Omits the wraparound pass.', 'Accepts equality as a greater value.'],
    circular_oracle,random_circular,
    ['Unanswered indices wait for their first greater value.',
     'Use a decreasing stack and scan the array twice to expose wraparound successors.',
     'At each scanned value, pop and answer smaller pending values; push original indices only during the first pass.',
     'Each index enters and leaves once. Keep the comparison strict so equal values do not answer each other; unanswered indices remain -1.'],
    'Pending indices have non-increasing values. The first later scanned larger value is '
    'their required successor. The second pass covers circular continuations without adding '
    'duplicate pending indices. This differs from the original linear Next Greater Values '
    'exercise: a successor can occur before the query index. The independent oracle scans '
    'each of the next n-1 positions literally. The output stores values, not distances or indices.',
    'O(n)','O(n)',difficulty=5,
    stress=[([list(range(10000))],list(range(1,10000))+[-1]),
            ([list(range(10000,0,-1))],[-1]+[10000]*9999),
            ([[7]*10000],[-1]*10000),([[0,1]*5000],[1,-1]*5000)]),
505:entry('shortest_rolling_distance',[('maze','list[list[int]]'),('start','list[int]'),('destination','list[int]')],
    'int',['graphs','matrices','search','heaps','shortest-path'],
    ['1 <= rows, columns <= 100; rectangular maze values are 0 (empty) or 1 (wall).',
     'start and destination are distinct in-bounds empty [row,column] cells; at least two empty cells exist.',
     'The ball rolls to a wall or outside border before it can turn. It must STOP at the destination, not merely pass through it.',
     'Minimize traveled cells, excluding the start and including the destination. Return -1 if stopping there is impossible.'],
    [([MAZE_SAMPLE,[0,4],[4,4]],'One optimal route travels left 1, down 1, left 3, down 1, right 2, down 2, right 2: 12 cells in total, not seven rolls.'),
     ([MAZE_SAMPLE,[0,4],[3,2]],'Return -1. A roll can cross [3,2] but cannot stop there; ordinary one-cell-at-a-time pathfinding would incorrectly accept it.')],
    MAZE_BOUNDARIES,
    MAZE,[MAZE.replace('candidate=distance+steps','candidate=distance+1'),
          MAZE.replace('x+=dr;y+=dc;steps+=1','x+=dr;y+=dc;steps+=1\n                if [x,y]==destination:break')],
    ['Counts rolls instead of cells traveled.', 'Treats the destination as a hole that stops a roll early.'],
    maze_oracle,random_maze,
    ['Only stopping positions are states where you may choose another direction.',
     'A roll is an edge weighted by how many cells it crosses, so use a weighted shortest-path search.',
     'Pop the smallest distance; roll in all four directions to a wall; relax endpoint distances by the number of crossed cells.',
     'Skip stale heap entries and zero-length moves. Accept the destination only as a popped stopping state, never while the ball passes through it.'],
    'Dijkstra applies because every nonempty roll has positive weight. A FIFO BFS minimizes '
    'roll count, not cell distance. Different paths can revisit an endpoint with a shorter distance, '
    'so a simple visited-on-discovery set is insufficient. The independent oracle constructs '
    'directional rays and uses synchronous Bellman-Ford. For V=rows*columns, scanning four '
    'rays at each endpoint costs O(V*(rows+columns)); heap operations add O(V log V). '
    'Unlike the existing Maze reachability task, the output must be the minimum travel distance.',
    'O(V*(rows+columns+log V))','O(V)',difficulty=6,
    stress=[([[[0]*100 for _ in range(100)],[0,0],[99,99]],198),
            ([[[0]*100 for _ in range(100)],[0,0],[50,50]],-1),
            ([[[0]*100],[0,0],[0,50]],-1),
            ([snake_maze(),[0,0],[98,0]],5048),
            ([dense_maze(),[0,0],[99,99]],234)]),
514:entry('freedom_trail_steps',[('ring','str'),('key','str')],'int',['strings','dynamic-programming','recursion'],
    ['1 <= len(ring), len(key) <= 100; both contain lowercase English letters.',
     'Every key character appears on the ring. Index 0 initially points upward; rotations persist between presses.',
     'Each one-position rotation in either direction costs 1. Pressing a matching letter also costs 1, even without rotation.'],
    [(['godding','gd'],'Press g at index 0 (1), rotate two positions to a d (2), and press d (1). Total 4.'),
     (['abcde','ee'],'Rotate one position backward to e and press twice. Total 3: the ring does not reset between letters, and each press costs a step.')],
    [['a','a'],['a','aaaa'],['ab','a'],['ab','b'],['ab','aba'],['abc','c'],['abc','ca'],
     ['godding','godding'],['aaa','aaa'],['abca','ac'],['abcab','bab'],['abcdef','fed'],
     ['abacada','dcba'],['aaaab','baba'],['abcbad','bdab'],['aabac','bac']],
    RING,[RING.replace('min(abs(q-position),n-abs(q-position))','abs(q-position)'),
          RING.replace('+1+spell(index+1,q)','+spell(index+1,q)')],
    ['Never uses circular wraparound to shorten a rotation.', 'Forgets that every button press costs one step.'],
    ring_oracle,random_ring,
    ['A repeated letter can be reached at several ring indices, which lead to different future costs.',
     'Memoize by next key index and current ring position, not by key index alone.',
     'For every matching ring index q, add min(abs(q-position),n-abs(q-position)) + 1 + spell(next,q); choose the minimum.',
     'The key index strictly increases, so recursive states are acyclic. Cache each state and keep the ring position after every press.'],
    'Every solution next chooses some occurrence of the required letter. The shorter circular '
    'distance is optimal for that transition; pressing costs one additional step. Minimize over '
    'all occurrences because a locally nearest choice can be worse for later letters. Memoizing '
    '(key index,ring index) gives O(m*n^2) time and O(m*n) space for m=len(key), n=len(ring). '
    'The independent oracle uses unit-action BFS over rotations and presses, not this recurrence.',
    'O(m*n^2)','O(m*n)',difficulty=8,
    stress=[(['a'*100,'a'*100],100),(['a'*99+'b','b'*100],101),
            (['ab'*50,'ab'*50],199),(['a'*50+'b'*50,'ab'*50],199)])
}

for pid in (499,505):
    BATCH[pid]['statement']=('Find the shortest rolling route. ' if pid==505 else 'Find the shortest instructions that drop a rolling ball into a hole. ')+ ' '.join(BATCH[pid]['constraints'][1:])
for pid in (499,502):BATCH[pid]['prerequisites']=['heaps','greedy'] if pid==502 else ['graphs','heaps']
BATCH[514]['prerequisites']=['recursion','dynamic-programming']
