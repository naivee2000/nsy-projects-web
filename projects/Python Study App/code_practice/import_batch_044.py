"""Simple polygons, bounded bits, self-describing strings and rolling grids."""
from collections import deque
from itertools import combinations
import random

from .import_batch_003 import entry


def cross(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def polygon_oracle(args):
    points = args[0]
    # A convex polygon lies wholly on one side of every boundary edge.
    for a,b in zip(points,points[1:]+points[:1]):
        sides = {1 if value>0 else -1 for p in points if (value:=cross(a,b,p))}
        if len(sides)>1:
            return False
    return True


def complement_oracle(args):
    return int(''.join('1' if char=='0' else '0' for char in bin(args[0])[2:]),2)


def distance_oracle(args):
    return sum(sum(x!=y for x,y in zip(f'{a:030b}',f'{b:030b}')) for a,b in combinations(args[0],2))


def magical_prefix(n):
    # Expand every declared run in a whole prefix, rather than maintaining a
    # read pointer in a growing list. Each expansion extends the same fixed point.
    text = '122'
    while len(text)<n:
        text = ''.join(str(1+i%2)*int(char) for i,char in enumerate(text))
    return text[:n]


def magical_oracle(args):
    return magical_prefix(args[0]).count('1')


def license_oracle(args):
    text,k = args
    clean = ''.join(char.upper() for char in text if char!='-')
    return '-'.join(reversed([clean[max(0,end-k):end] for end in range(len(clean),0,-k)]))


def maze_oracle(args):
    """A cell/direction automaton, not a graph whose edges are complete rolls."""
    maze,start,destination = args
    rows,cols = len(maze),len(maze[0])
    queue = deque([(*start,0,0)])
    seen = set(queue)
    while queue:
        r,c,dr,dc = queue.popleft()
        if (dr,dc)==(0,0):
            if [r,c]==destination:
                return True
            successors = [(r,c,a,b) for a,b in ((1,0),(-1,0),(0,1),(0,-1))]
        elif 0<=r+dr<rows and 0<=c+dc<cols and maze[r+dr][c+dc]==0:
            successors = [(r+dr,c+dc,dr,dc)]
        else:
            successors = [(r,c,0,0)]
        for state in successors:
            if state not in seen:
                seen.add(state)
                queue.append(state)
    return False


def random_polygon(rng):
    xs = sorted(rng.sample(range(-10,11),rng.randint(2,6)))
    lower = [[x,-rng.randint(1,10)] for x in xs]
    upper = [[x,rng.randint(1,10)] for x in reversed(xs)]
    points = lower+upper
    if rng.random()<.5:
        points.reverse()
    shift = rng.randrange(len(points))
    return [points[shift:]+points[:shift]]


def random_complement(rng):
    return [rng.randint(1,2**31-1)]


def random_distance(rng):
    return [[rng.randint(0,10**9) for _ in range(rng.randint(1,12))]]


def random_magical(rng):
    return [rng.randint(1,300)]


def random_license(rng):
    return [''.join(rng.choice('aAzZ019-') for _ in range(rng.randint(1,40))),rng.randint(1,12)]


def random_maze(rng,rows=None,cols=None):
    rows,cols = rows or rng.randint(1,6),cols or rng.randint(1,6)
    if rows*cols==1:
        cols=2
    maze=[[int(rng.random()<.3) for _ in range(cols)] for _ in range(rows)]
    a,b=rng.sample(range(rows*cols),2)
    start,destination = list(divmod(a,cols)),list(divmod(b,cols))
    maze[start[0]][start[1]]=maze[destination[0]][destination[1]]=0
    return [maze,start,destination]


POLYGON='''\
def is_convex_polygon(points):
    direction=0
    n=len(points)
    for i in range(n):
        a,b,c=points[i],points[(i+1)%n],points[(i+2)%n]
        turn=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
        if turn:
            sign=1 if turn>0 else -1
            if direction and sign!=direction:
                return False
            direction=sign
    return True
'''
COMPLEMENT='''\
def number_complement(num):
    mask=(1<<num.bit_length())-1
    return mask^num
'''
DISTANCE='''\
def total_hamming_distance(nums):
    n=len(nums)
    total=0
    for bit in range(30):
        ones=sum((value>>bit)&1 for value in nums)
        total+=ones*(n-ones)
    return total
'''
MAGICAL='''\
def magical_string_ones(n):
    sequence=[1,2,2]
    read=2
    while len(sequence)<n:
        digit=3-sequence[-1]
        sequence.extend([digit]*sequence[read])
        read+=1
    return sequence[:n].count(1)
'''
LICENSE='''\
def format_license_key(s,k):
    clean=s.replace('-','').upper()
    if not clean:
        return ''
    first=len(clean)%k or k
    groups=[clean[:first]]
    groups.extend(clean[i:i+k] for i in range(first,len(clean),k))
    return '-'.join(groups)
'''
MAZE='''\
def rolling_maze_path(maze,start,destination):
    rows,cols=len(maze),len(maze[0])
    stack=[tuple(start)]
    seen=set(stack)
    goal=tuple(destination)
    while stack:
        row,col=stack.pop()
        if (row,col)==goal:
            return True
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            r,c=row,col
            while 0<=r+dr<rows and 0<=c+dc<cols and maze[r+dr][c+dc]==0:
                r,c=r+dr,c+dc
            if (r,c) not in seen:
                seen.add((r,c))
                stack.append((r,c))
    return False
'''

PERIMETER=([[i,0] for i in range(2500)]+[[2500,i] for i in range(2500)]
           +[[2500-i,2500] for i in range(2500)]+[[0,2500-i] for i in range(2500)])
NOTCHED=[point[:] for point in PERIMETER]
NOTCHED[6250][1]-=1
STANDARD_MAZE=[[0,0,1,0,0],[0,0,0,0,0],[0,0,0,1,0],[1,1,0,1,1],[0,0,0,0,0]]
DENSE_MAZE=random_maze(random.Random(490490),100,100)

BATCH={
469: entry('is_convex_polygon',[('points','list[list[int]]')],'bool',['arrays','geometry'],
    ['3 <= points.length <= 10,000; points are distinct integer pairs with coordinates in -10,000..10,000.',
     'Points are already in boundary order and form a simple, non-self-intersecting polygon. Do not sort them.',
     'Return whether the polygon is convex. Collinear boundary points are permitted; either clockwise or counterclockwise order is valid.'],
    [([[[0,0],[0,5],[5,5],[5,0]]],'The four corners form a convex square in clockwise order; clockwise is not an error.'),
     ([[[0,0],[0,10],[10,10],[10,0],[5,5]]],'The final point creates an inward notch, so the turn direction changes and the polygon is not convex.')],
    [[p] for p in ([[0,0],[2,0],[0,2]],[[0,0],[0,2],[2,0]],
      [[0,0],[1,0],[2,0],[2,2],[0,2]],[[0,0],[3,0],[3,1],[1,1],[1,3],[0,3]],
      [[0,0],[2,0],[3,1],[2,2],[0,2],[-1,1]],[[0,0],[4,0],[2,1],[4,4],[0,4]],
      [[-2,-2],[-2,2],[2,2],[2,-2]],[[0,0],[1,0],[1,1],[0,1]],
      [[0,0],[2,0],[2,1],[2,2],[0,2]],[[0,0],[4,0],[4,4],[2,2],[0,4]],
      [[-10000,-10000],[10000,-10000],[10000,10000],[-10000,10000]],
      [[0,0],[0,3],[1,3],[1,1],[3,1],[3,0]])],
    POLYGON,[POLYGON.replace('if turn:','if not turn:\n            return False\n        if turn:'),
             POLYGON.replace('if turn:','if turn < 0:\n            return False\n        if turn:')],
    ['Rejects a zero turn even when the extra point lies on a straight boundary edge.', 'Accepts only counterclockwise polygons.'],
    polygon_oracle,random_polygon,
    ['For a simple polygon, every nonzero boundary turn must have the same sign.',
     'Use integer cross products of consecutive edges; ignore zero products from straight portions.',
     'Walk every cyclic triple, recording the first nonzero sign and rejecting a later opposite sign.',
     'Include the closing edges and do not impose clockwise versus counterclockwise orientation. Simplicity is an input guarantee.'],
    'A simple convex boundary never reverses its turning direction. The signed cross product detects '
    'that direction without division or floating-point rounding; zero turns preserve convexity. '
    'The independent oracle checks that every other point lies on a single side of each whole edge. '
    'Tests use only simple polygons, including collinear boundary points and extreme integer coordinates.',
    'O(n)','O(1)',difficulty=5,stress=[([PERIMETER],True),([NOTCHED],False)]),
476: entry('number_complement',[('num','int')],'int',['math','bit-manipulation'],
    ['1 <= num < 2^31. Flip only the significant bits of the positive integer, not an arbitrary fixed-width word.',
     'Return the resulting nonnegative integer. Leading zero bits are not part of the input representation.'],
    [([5],'101 becomes 010, whose integer value is 2.'),([8],'1000 becomes 0111, giving 7; only these four positions are flipped.')],
    [[n] for n in (1,2,3,4,6,7,9,15,16,31,2**30,2**31-1)],
    COMPLEMENT,['def number_complement(num):\n    return ~num\n',
      'def number_complement(num):\n    return num^((1<<31)-1)\n'],
    ['Uses the unbounded signed Python complement.', 'Always flips 31 bits, introducing unwanted leading ones.'],
    complement_oracle,random_complement,
    ['Find the number of significant bits before flipping.', 'Create an all-one mask of exactly that width.',
     'Compute mask=(1<<num.bit_length())-1 and return mask XOR num.',
     'A power of two becomes one less than itself; an all-one representation becomes zero.'],
    'XOR with a same-width all-one mask flips precisely the original bit positions. Python\'s bare '
    '~ operator also changes infinitely many sign-extension bits, so it is not this contract. '
    'The independent oracle flips literal binary characters and parses the resulting string.',
    'O(log num) bit complexity','O(log num) bits',difficulty=3,
    stress=[([2**31-2],1)]),
477: entry('total_hamming_distance',[('nums','list[int]')],'int',['arrays','bit-manipulation','math'],
    ['1 <= nums.length <= 10,000; 0 <= nums[i] <= 1,000,000,000; the answer fits a signed 32-bit integer.',
     'Sum Hamming distances over unordered pairs of different indices. Repeated values at different indices remain separate entries.',
     'This is a total over an array, not the two-number Hamming Distance function.'],
    [([[4,14,2]],'The three pair distances are 2,2,2, totaling 6. Count each pair once.'),
     ([[4,14,4]],'The two occurrences of 4 each contribute distance 2 to 14; their mutual distance is zero. Total: 4.')],
    [[a] for a in ([0],[1],[0,0],[0,1],[1,2],[1,1,2],[0,0,1,1],[0,2**29],
       [10**9,0],[1,2,3],[7,7,7],[0,1,2,3])],
    DISTANCE,[DISTANCE.replace('range(30)','range(29)'),DISTANCE.replace('n=len(nums)','nums=list(set(nums))\n    n=len(nums)')],
    ['Misses the highest possible input bit.', 'Deduplicates the array and loses index-pair multiplicities.'],
    distance_oracle,random_distance,
    ['Count pair disagreements one bit position at a time.', 'If a bit has c ones and n-c zeros, it contributes c*(n-c) pairs.',
     'For each of 30 bit positions, count ones and add ones*(n-ones).',
     'Every unordered disagreeing pair selects one member from each group exactly once; no division by two is needed.'],
    'Summing distances over pairs can be reordered into summing disagreements over bits. At one bit, '
    'a differing pair contains one one-bit entry and one zero-bit entry. Their group-size product '
    'counts unordered pairs directly, including repeated values. The oracle enumerates pairs and '
    'compares padded binary strings position by position.',
    'O(30*n)','O(1)',difficulty=5,
    stress=[([[0]*5000+[2**29-1]*5000],29*5000**2),([[10**9]*10000],0)]),
481: entry('magical_string_ones',[('n','int')],'int',['strings','two-pointers'],
    ['1 <= n <= 100,000. The magical sequence begins 1221121221221121122...',
     'Its run lengths, read as digits, reproduce the sequence itself. Return the number of 1s in the first n digits only.',
     'The final requested prefix may end partway through a run. Do not count characters appended beyond n.'],
    [([6],'The first six digits are 122112, containing three 1s.'),
     ([4],'The first four digits are 1221, containing two 1s. Extending the last run to 12211 would count an unwanted fifth digit.')],
    [[n] for n in (1,2,3,5,7,8,9,10,11,12,13,14,15,16)],
    MAGICAL,['def magical_string_ones(n):\n    return n//2\n',MAGICAL.replace('sequence[:n].count(1)','sequence.count(1)')],
    ['Assumes the two digits occur equally often in every prefix.', 'Counts a completed run beyond the requested prefix length.'],
    magical_oracle,random_magical,
    ['Use the already generated digits as future run lengths.', 'Start from 122 and read run lengths beginning at its third digit.',
     'Append the opposite digit one or two times according to the next read digit, then advance the read pointer.',
     'Stop once the list is long enough, but count only its first n entries. The read pointer advances more slowly than generation.'],
    'The seed fixes the first two runs. Each later read digit determines the length of the next '
    'alternating run. Appending whole runs preserves the self-description invariant, but the requested '
    'prefix may truncate the final one. The independent oracle repeatedly expands every run of an '
    'entire prefix, rather than indexing a growing sequence in place.',
    'O(n)','O(n)',difficulty=5,stress=[([100000],magical_oracle([100000]))]),
482: entry('format_license_key',[('s','str'),('k','int')],'str',['strings'],
    ['1 <= s.length <= 100,000; English letters, digits, and dashes only; 1 <= k <= 10,000.',
     'Remove existing dashes, uppercase letters, then group from the right in groups of k. Only the first group may be shorter.',
     'Return an empty string if the input contains only dashes. Never add a leading or trailing separator.'],
    [(['5F3Z-2e-9-w',4],'Ignoring old dashes gives 5F3Z2E9W; split into two groups of four: 5F3Z-2E9W.'),
     (['2-5g-3-J',2],'Five characters require a one-character first group: 2-5G-3J, not 25-G3-J.')],
    [[s,k] for s,k in (('-',1),('---',3),('a',1),('a',2),('abc',2),('abcd',2),('abcde',3),
       ('-a-b-',1),('a--b---c',2),('12345',4),('AbC',10),('z9-',2))],
    LICENSE,["def format_license_key(s,k):\n    clean=s.replace('-','').upper()\n    return '-'.join(clean[i:i+k] for i in range(0,len(clean),k))\n",LICENSE.replace(".upper()",'')],
    ['Places the short group at the end instead of the beginning.', 'Fails to normalize lowercase letters.'],
    license_oracle,random_license,
    ['Old dash positions do not constrain the new groups.', 'After cleaning, the first group length is total%k, or k if divisible.',
     'Emit that first group, then full groups of k joined by a single dash.',
     'Handle an all-dash input before creating the first group; uppercase letters without changing digits or order.'],
    'Only the first group may be short, so its length is determined by the cleaned length modulo k. '
    'All remaining groups are full-sized. The oracle independently slices backward from the right end '
    'and reverses the group order, covering partial first groups and empty cleaned inputs.',
    'O(len(s))','O(len(s))',difficulty=3,
    stress=[(['a'*100000,10000],'-'.join(['A'*10000]*10)),
            (['a-'*50000,1],'-'.join(['A']*50000)),(['-'*100000,10000],'')]),
490: entry('rolling_maze_path',[('maze','list[list[int]]'),('start','list[int]'),('destination','list[int]')],'bool',
    ['matrices','graphs','depth-first-search','recursion'],
    ['The rectangular maze has 1..100 rows and columns; 0 is open and 1 is a wall. Outside the array acts as a wall.',
     'Start and destination are different open cells given as [row,column]; at least two cells are open.',
     'The ball rolls horizontally or vertically until the next cell is blocked. It may choose a new direction only after stopping.',
     'Return whether it can STOP at the destination. Merely passing through it is not enough.'],
    [([STANDARD_MAZE,[0,4],[4,4]],'One sequence of complete rolls is left, down, left, down, right, down, right. The final stop is [4,4].'),
     ([[[0,0,0,0]],[0,0],[0,2]],'The ball passes [0,2] but stops only at [0,3] or [0,0]. It cannot stop at the requested cell.')],
    [args for args in (
      [[[0,0]],[0,0],[0,1]], [[[0],[0]],[0,0],[1,0]], [[[0,1,0]],[0,0],[0,2]],
      [[[0,0,0]],[0,1],[0,2]], [[[0,0,0]],[0,0],[0,1]], [[[0,0],[0,0]],[0,0],[1,1]],
      [[[0,1],[1,0]],[0,0],[1,1]], [[[0,0],[1,0]],[0,0],[1,1]],
      [[[0,1],[0,0]],[0,0],[1,1]], [[[0,0,0],[1,1,0]],[0,0],[1,2]],
      [[[0,0,0],[0,0,0],[0,0,0]],[0,0],[1,1]], [[[0,0,0],[0,1,0],[0,0,0]],[0,0],[2,2]],
      [STANDARD_MAZE,[0,4],[3,2]], [[[0,0]],[0,1],[0,0]])],
    MAZE,[MAZE.replace('while 0<=r+dr<rows','if 0<=r+dr<rows'),MAZE.replace('((1,0),(-1,0),(0,1),(0,-1))','((1,0),(0,1))')],
    ['Treats every adjacent open cell as a legal stopping and turning point.', 'Restricts moves to down/right and misses paths requiring up or left.'],
    maze_oracle,random_maze,
    ['Search states are stopping positions, not all cells the ball passes.', 'From each stopped position, roll in all four directions to the next stop.',
     'Use DFS or BFS over those stops, recording visited states and accepting only when a stopped state equals the destination.',
     'An explicit DFS stack avoids recursion-depth limits on large grids. Do not mark intermediate rolling cells as visited stops.'],
    'Each legal roll is one graph edge between stopped positions. Searching that graph explores all '
    'possible direction choices while preserving the requirement to stop at the target. The reference '
    'uses an explicit DFS stack for deep inputs; recursive DFS teaches the same state definition. '
    'The oracle independently simulates one moving cell at a time with a direction in the state, '
    'and only permits new directions after a wall creates a stopped state.',
    'O(rows*cols*(rows+cols))','O(rows*cols)',difficulty=6,
    stress=[([[[0]*100 for _ in range(100)],[0,0],[99,99]],True),
            ([[[0]*100 for _ in range(100)],[0,0],[50,50]],False),
            (DENSE_MAZE,maze_oracle(DENSE_MAZE))]),
}
