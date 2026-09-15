"""Stone assignment, grid components, pair removals, XOR points, and happy cuts."""
from functools import lru_cache
from itertools import permutations

from .import_batch_055 import entry


def stones_oracle(args):
    grid = args[0]; extras = []; empty = []
    for row in range(3):
        for col in range(3):
            empty.extend([(row,col)] * (grid[row][col] == 0))
            extras.extend([(row,col)] * max(0, grid[row][col] - 1))
    return min((sum(abs(a-c)+abs(b-d) for (a,b),(c,d) in zip(extras,order)) for order in permutations(empty)), default=0)


def random_stones(rng):
    cells = [0] * 9
    for _ in range(9): cells[rng.randrange(9)] += 1
    return [[cells[index:index+3] for index in range(0,9,3)]]


def remoteness_oracle(args):
    grid = args[0]; size = len(grid); answer = 0
    all_cells = [(r,c) for r in range(size) for c in range(size) if grid[r][c] != -1]
    for start in all_cells:
        seen = {start}; stack = [start]
        while stack:
            row,col = stack.pop()
            for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nxt=(row+dr,col+dc)
                if 0<=nxt[0]<size and 0<=nxt[1]<size and grid[nxt[0]][nxt[1]]!=-1 and nxt not in seen:
                    seen.add(nxt);stack.append(nxt)
        answer += sum(grid[row][col] for row,col in all_cells if (row,col) not in seen)
    return answer


def random_remoteness(rng):
    size=rng.randint(1,4);grid=[[rng.choice([-1,rng.randint(1,12)]) for _ in range(size)] for _ in range(size)]
    if all(value==-1 for row in grid for value in row):grid[0][0]=1
    return [grid]


def removals_oracle(args):
    start=tuple(args[0])
    @lru_cache(None)
    def visit(values):
        best=len(values)
        for left in range(len(values)):
            for right in range(left+1,len(values)):
                if values[left]<values[right]:best=min(best,visit(values[:left]+values[left+1:right]+values[right+1:]))
        return best
    return visit(start)


def random_removals(rng): return [sorted(rng.randint(1,6) for _ in range(rng.randint(1,11)))]


def xor_pairs_oracle(args):
    points,target=args
    return sum((points[i][0]^points[j][0])+(points[i][1]^points[j][1])==target for i in range(len(points)) for j in range(i+1,len(points)))


def random_xor_pairs(rng): return [[[rng.randint(0,31),rng.randint(0,31)] for _ in range(rng.randint(2,20))],rng.randint(0,20)]


def happy_oracle(args):
    nums=args[0];answer=0
    for mask in range(1<<len(nums)):
        selected=mask.bit_count()
        if all((selected>value) if mask>>index&1 else (selected<value) for index,value in enumerate(nums)):answer+=1
    return answer


def random_happy(rng):
    size=rng.randint(1,10)
    return [[rng.randrange(size) for _ in range(size)]]


STONES='''def minimum_stone_spread_moves(grid):
    extras=[];empty=[]
    for row in range(3):
        for col in range(3):
            if grid[row][col]==0:empty.append((row,col))
            for _ in range(max(0,grid[row][col]-1)):extras.append((row,col))
    dp={0:0}
    for source in extras:
        following={}
        for mask,cost in dp.items():
            for index,target in enumerate(empty):
                if not mask>>index&1:
                    distance=abs(source[0]-target[0])+abs(source[1]-target[1]);new=mask|1<<index
                    following[new]=min(following.get(new,float('inf')),cost+distance)
        dp=following
    return min(dp.values(),default=0)
'''


GREEDY_STONES='''def minimum_stone_spread_moves(grid):
    extras=[];empty=[]
    for row in range(3):
        for col in range(3):
            empty.extend([(row,col)]*(grid[row][col]==0));extras.extend([(row,col)]*max(0,grid[row][col]-1))
    answer=0
    for source in extras:
        target=min(empty,key=lambda cell:abs(source[0]-cell[0])+abs(source[1]-cell[1]));empty.remove(target)
        answer+=abs(source[0]-target[0])+abs(source[1]-target[1])
    return answer
'''


REUSED_TARGET_STONES='''def minimum_stone_spread_moves(grid):
    extras=[];empty=[]
    for row in range(3):
        for col in range(3):
            empty.extend([(row,col)]*(grid[row][col]==0));extras.extend([(row,col)]*max(0,grid[row][col]-1))
    return sum(min(abs(source[0]-target[0])+abs(source[1]-target[1]) for target in empty) for source in extras) if empty else 0
'''


REMOTENESS='''def sum_cell_remoteness(grid):
    size=len(grid);total=sum(value for row in grid for value in row if value!=-1);seen=set();components=[]
    for start_row in range(size):
        for start_col in range(size):
            if grid[start_row][start_col]==-1 or (start_row,start_col) in seen:continue
            stack=[(start_row,start_col)];seen.add((start_row,start_col));count=0;subtotal=0
            while stack:
                row,col=stack.pop();count+=1;subtotal+=grid[row][col]
                for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nxt=(row+dr,col+dc)
                    if 0<=nxt[0]<size and 0<=nxt[1]<size and grid[nxt[0]][nxt[1]]!=-1 and nxt not in seen:
                        seen.add(nxt);stack.append(nxt)
            components.append((count,subtotal))
    return sum(count*(total-subtotal) for count,subtotal in components)
'''


REMOVALS='''def minimum_length_after_pair_removals(nums):
    from collections import Counter
    maximum=max(Counter(nums).values());size=len(nums)
    return max(size%2,2*maximum-size)
'''


XOR_PAIRS='''def count_xor_distance_pairs(coordinates,k):
    from collections import Counter
    seen=Counter();answer=0
    for x,y in coordinates:
        for left in range(k+1):answer+=seen[(x^left,y^(k-left))]
        seen[(x,y)]+=1
    return answer
'''


HAPPY='''def count_happy_student_groups(nums):
    values=sorted(nums);size=len(values);answer=0
    for selected in range(size+1):
        chosen_ok=selected==0 or values[selected-1]<selected
        unchosen_ok=selected==size or values[selected]>selected
        answer+=chosen_ok and unchosen_ok
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
2850:entry('minimum_stone_spread_moves',[('grid','list[list[int]]')],'int',['bitmasks','dynamic programming','matrices'],['grid is exactly 3x3, contains nonnegative counts, and totals nine stones.','One move transfers one stone across one shared side.','Return the minimum moves until every cell contains exactly one stone.'],[([[[1,1,0],[1,1,1],[1,2,1]]],'The surplus bottom-middle stone travels three grid edges to the empty top-right cell.'),([[[1,3,0],[1,0,0],[1,0,3]]],'Assigning the four surplus stones to the four empty cells costs four moves.')],[[g] for g in [[[1,1,1],[1,1,1],[1,1,1]],[[9,0,0],[0,0,0],[0,0,0]],[[0,0,0],[0,9,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,9]],[[2,0,1],[1,1,1],[1,1,1]],[[0,2,1],[1,1,1],[1,1,1]],[[3,0,0],[1,1,1],[1,1,1]],[[1,0,1],[1,3,0],[1,1,1]],[[2,2,0],[0,1,1],[1,1,1]],[[0,1,2],[1,2,0],[1,1,1]],[[4,0,0],[0,1,1],[1,1,1]],[[0,0,3],[1,1,0],[1,2,1]],[[2,0,2],[0,1,0],[1,2,1]],[[0,3,0],[2,0,1],[1,1,1]]]],STONES,[STONES.replace('abs(source[0]-target[0])+abs(source[1]-target[1])','max(abs(source[0]-target[0]),abs(source[1]-target[1]))'),REUSED_TARGET_STONES],['Uses diagonal distance even though moves may cross only shared sides.','Lets multiple surplus stones fill the same nearest empty cell instead of enforcing a one-to-one assignment.'],stones_oracle,random_stones,lesson('Each surplus stone must be assigned to one currently empty cell.','Use a bitmask of filled empty cells and add Manhattan assignment costs one surplus at a time.','Transition every state by assigning the next surplus to each unfilled target.','Every valid final placement is a bijection between surplus stones and empty cells; the DP enumerates all such bijections and minimizes their exact movement costs.'),'O(e^2*2^e)','O(2^e)',5),
2852:entry('sum_cell_remoteness',[('grid','list[list[int]]')],'int',['graphs','matrices','depth-first search'],['grid is square; each cell is positive or blocked with -1.','Movement connects non-blocked cells sharing a side.','For every non-blocked cell, sum values outside its connected component, then return the total.'],[([[[-1,1,-1],[5,-1,4],[-1,3,-1]]],'Four isolated cells see all other values, producing total remoteness thirty-nine.'),([[[-1,3,4],[-1,-1,-1],[3,-1,-1]]],'The top component and isolated bottom cell contribute thirteen in total.')],[[g] for g in [[[1]],[[-1]],[[1,2],[3,4]],[[1,-1],[-1,2]],[[1,-1],[2,3]],[[-1,5],[7,-1]],[[1,-1,2],[3,-1,4],[5,-1,6]],[[1,2,-1],[-1,-1,-1],[3,4,5]],[[1,-1,2],[-1,3,-1],[4,-1,5]],[[9,1],[2,-1]],[[1,2,3],[4,5,6],[7,8,9]],[[-1,-1],[-1,-1]],[[2,-1,8],[3,-1,7],[4,-1,6]],[[1,-1,10],[2,-1,20],[3,-1,30]]]],REMOTENESS,[REMOTENESS.replace('total-subtotal','total-count'),REMOTENESS.replace('count*(total-subtotal)','subtotal*(total-subtotal)')],['Subtracts the component’s cell count from the global value sum.','Weights outside values by the component value sum instead of its number of cells.'],remoteness_oracle,random_remoteness,lesson('Reachability partitions all open cells into connected components.','Find each component’s cell count and value sum, alongside the global value sum.','Add component_size*(global_sum-component_sum) for every component.','Every cell in one component has exactly the values outside that component as remote, so multiplying their sum by the component size counts each cell’s remoteness once.'),'O(n^2)','O(n^2)',5),
2856:entry('minimum_length_after_pair_removals',[('nums','list[int]')],'int',['greedy','counting','arrays'],['nums is a nonempty nondecreasing array.','Each operation removes two unequal values, with the smaller chosen before the larger.','Return the minimum remaining length.'],[([[1,2,3,4]],'Pairing one with three and two with four removes everything.'),([[1000000000,1000000000]],'Equal values cannot form a removable pair, so both remain.')],[[n] for n in [[1],[1,2],[1,1],[1,1,2],[1,2,2],[1,1,2,2],[1,1,1,2],[1,2,3],[1,1,2,2,3,3],[1,1,1,2,2],[2,3,4,4,4],[1,1,1,1,2,3],[1,2,2,2,3,3],[1,1,2,3,3,3,3]]],REMOVALS,[REMOVALS.replace('max(size%2,2*maximum-size)','size%2'),REMOVALS.replace('2*maximum-size','maximum-size//2')],['Assumes every pair can be made from unequal values.','Uses half the total size rather than the count of all non-majority values against the majority.'],removals_oracle,random_removals,lesson('Only an overrepresented value can force leftovers beyond parity.','Pair every majority occurrence possible with a different value; otherwise pair all elements except a parity remainder.','Let f be maximum frequency and n the length; return max(n mod 2,2f-n).','If f>n-f, exactly f-(n-f) majority items remain; otherwise distinct-value pairs can consume all items except the unavoidable odd one.'),'O(n)','O(n)',5),
2857:entry('count_xor_distance_pairs',[('coordinates','list[list[int]]'),('k','int')],'int',['bit manipulation','hash maps','arrays'],['coordinates contains at least two nonnegative integer points and k is nonnegative.','Distance is (x1 XOR x2)+(y1 XOR y2).','Count index pairs i<j at distance exactly k, including duplicate points.'],[([[[1,2],[4,2],[1,3],[5,2]],5],'Pairs (0,1) and (2,3) each have XOR-distance five.'),([[[1,3],[1,3],[1,3],[1,3],[1,3]],0],'All ten index pairs of identical points have distance zero.')],[[p,k] for p,k in [([[0,0],[0,0]],0),([[0,0],[1,0]],1),([[0,0],[1,1]],2),([[1,2],[3,4]],6),([[1,2],[3,4]],5),([[1,1],[2,2],[3,3]],4),([[0,1],[1,0],[2,3]],2),([[5,7],[5,7],[1,3]],0),([[2,4],[6,0],[3,5]],8),([[10,10],[12,9],[8,11]],3),([[1,0],[2,0],[3,0],[4,0]],3),([[7,7],[0,0],[7,0],[0,7]],14),([[4,2],[1,2],[5,2]],5),([[3,6],[5,1],[3,1],[5,6]],7)]],XOR_PAIRS,[XOR_PAIRS.replace('y^(k-left)','y^(k+left)'),XOR_PAIRS.replace('range(k+1)','range(k)')],['Combines the coordinate XOR contributions with addition instead of splitting k.','Never considers the split where the x-coordinate XOR contributes all k.'],xor_pairs_oracle,random_xor_pairs,lesson('The two nonnegative XOR contributions must split k.','For every new point, enumerate x-XOR a from zero through k and look up the required prior point.','The prior coordinates must be (x XOR a,y XOR (k-a)); add their stored frequency, then insert the new point.','Every qualifying prior pair has one unique split a, and inserting after querying enforces i<j without double counting.'),'O(n*k)','O(n)',5),
2860:entry('count_happy_student_groups',[('nums','list[int]')],'int',['sorting','enumeration','arrays'],['nums has n entries from zero through n-1.','A selected student requires selected_count>nums[i]; an unselected student requires selected_count<nums[i].','Count selection groups for which every student is happy.'],[([[1,1]],'Selecting none or selecting both students works, giving two groups.'),([[6,0,3,3,6,7,2,7]],'Exactly selection counts one, four, and eight separate valid sorted prefixes.')],[[n] for n in [[0],[1],[0,0],[0,1],[1,1],[0,2,2],[1,2,2],[0,1,2],[3,0,1,2],[0,0,3,3],[2,2,2,2],[0,4,1,3,2],[5,0,5,0,5,0],[1,4,2,3,0]]],HAPPY,[HAPPY.replace('values[selected-1]<selected','values[selected-1]<=selected'),HAPPY.replace('range(size+1)','range(1,size)')],['Uses non-strict comparison for selected students.','Forgets that selecting nobody or everybody may be valid.'],happy_oracle,random_happy,lesson('For a fixed group size, the selected students must be exactly those with thresholds below that size.','Sort thresholds and test every cut between selected and unselected prefixes.','At cut s require values[s-1]<s when s>0 and values[s]>s when s<n.','These inequalities make precisely the first s sorted students eligible for selection and every remaining student eligible for omission, so each valid size defines one valid group.'),'O(n log n)','O(n)',5),
}
