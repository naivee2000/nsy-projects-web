"""Product partitions, sliding matrices, energy search, prime splits, and superstrings."""
from collections import deque
from itertools import combinations

from .import_batch_055 import entry


def product_oracle(args):
    nums, target = args
    for size in range(1, len(nums)):
        for chosen in combinations(range(len(nums)), size):
            selected = set(chosen); first = second = 1
            for index, value in enumerate(nums):
                if index in selected: first *= value
                else: second *= value
            if first == second == target: return True
    return False


def random_product(rng):
    nums = rng.sample(range(1, 20), rng.randint(3, 9))
    if rng.randrange(3) == 0:
        chosen = set(rng.sample(range(len(nums)), rng.randint(1, len(nums) - 1))); target = 1
        for index in chosen: target *= nums[index]
    else: target = rng.randint(1, 500)
    return [nums, target]


def matrix_oracle(args):
    grid, k = args; rows = len(grid); columns = len(grid[0]); answer = []
    for top in range(rows - k + 1):
        row = []
        for left in range(columns - k + 1):
            values = {grid[r][c] for r in range(top, top + k) for c in range(left, left + k)}
            row.append(min((abs(a - b) for a, b in combinations(values, 2)), default=0))
        answer.append(row)
    return answer


def random_matrix(rng):
    rows = rng.randint(1, 5); columns = rng.randint(1, 5); grid = [[rng.randint(-15, 15) for _ in range(columns)] for _ in range(rows)]
    return [grid, rng.randint(1, min(rows, columns))]


def classroom_oracle(args):
    classroom, energy = args; rows = len(classroom); columns = len(classroom[0]); litter = {}; start = None
    for r in range(rows):
        for c in range(columns):
            if classroom[r][c] == 'S': start = (r, c)
            elif classroom[r][c] == 'L': litter[r, c] = len(litter)
    full = (1 << len(litter)) - 1; queue = deque([(start[0], start[1], energy, full, 0)]); seen = {(start[0], start[1], energy, full)}
    while queue:
        row, column, remaining, mask, moves = queue.popleft()
        if mask == 0: return moves
        if remaining == 0: continue
        for nr, nc in ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)):
            if not (0 <= nr < rows and 0 <= nc < columns) or classroom[nr][nc] == 'X': continue
            following_energy = energy if classroom[nr][nc] == 'R' else remaining - 1
            following_mask = mask & ~(1 << litter[nr, nc]) if (nr, nc) in litter else mask
            state = (nr, nc, following_energy, following_mask)
            if state not in seen: seen.add(state); queue.append((*state, moves + 1))
    return -1


def random_classroom(rng):
    rows = rng.randint(1, 4); columns = rng.randint(1, 4); total = rows * columns; start = rng.randrange(total)
    cells = [rng.choice('...RX') for _ in range(total)]; cells[start] = 'S'
    available = [index for index in range(total) if index != start]
    for index in rng.sample(available, rng.randint(0, min(3, len(available)))): cells[index] = 'L'
    return [[''.join(cells[r * columns:(r + 1) * columns]) for r in range(rows)], rng.randint(1, 6)]


def prime_split_oracle(args):
    nums, queries = args; values = list(nums)
    def prime(value):
        if value < 2: return False
        divisor = 2
        while divisor * divisor <= value:
            if value % divisor == 0: return False
            divisor += 1
        return True
    answer = []
    for index, value in queries:
        values[index] = value; best = 0
        for cut in range(1, len(values)):
            best = max(best, len({x for x in values[:cut] if prime(x)}) + len({x for x in values[cut:] if prime(x)}))
        answer.append(best)
    return answer


def random_prime_split(rng):
    length = rng.randint(2, 12); nums = [rng.randint(1, 50) for _ in range(length)]
    queries = [[rng.randrange(length), rng.randint(1, 50)] for _ in range(rng.randint(1, 10))]
    return [nums, queries]


def superstring_oracle(args):
    first, second = args
    if first in second: return second
    if second in first: return first
    candidates = []
    for left, right in ((first, second), (second, first)):
        for overlap in range(min(len(left), len(right)), -1, -1):
            if left.endswith(right[:overlap]): candidates.append(left + right[overlap:]); break
    return min(candidates, key=lambda text: (len(text), text))


def random_superstring(rng):
    alphabet = 'abcd'; return [''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 10))), ''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 10)))]


PRODUCT = '''def can_partition_equal_products(nums,target):
    total=1
    for value in nums:total*=value
    if total!=target*target:return False
    for mask in range(1,(1<<len(nums))-1):
        product=1
        for index,value in enumerate(nums):
            if mask>>index&1:
                product*=value
                if product>target:break
        if product==target:return True
    return False
'''


MATRIX = '''def sliding_submatrix_min_difference(grid,k):
    rows=len(grid);columns=len(grid[0]);answer=[]
    for top in range(rows-k+1):
        output=[]
        for left in range(columns-k+1):
            values=sorted({grid[row][column] for row in range(top,top+k) for column in range(left,left+k)})
            output.append(min((b-a for a,b in zip(values,values[1:])),default=0))
        answer.append(output)
    return answer
'''


CLASSROOM = '''def minimum_classroom_cleaning_moves(classroom,energy):
    from collections import deque
    rows=len(classroom);columns=len(classroom[0]);litter={};start=None
    for row in range(rows):
        for column in range(columns):
            if classroom[row][column]=='S':start=(row,column)
            elif classroom[row][column]=='L':litter[row,column]=len(litter)
    full=(1<<len(litter))-1;queue=deque([(start[0],start[1],energy,full,0)]);seen={(start[0],start[1],energy,full)}
    while queue:
        row,column,remaining,mask,moves=queue.popleft()
        if mask==0:return moves
        if remaining==0:continue
        for next_row,next_column in ((row-1,column),(row+1,column),(row,column-1),(row,column+1)):
            if 0<=next_row<rows and 0<=next_column<columns and classroom[next_row][next_column]!='X':
                next_energy=energy if classroom[next_row][next_column]=='R' else remaining-1
                next_mask=mask
                if (next_row,next_column) in litter:next_mask&=~(1<<litter[next_row,next_column])
                state=(next_row,next_column,next_energy,next_mask)
                if state not in seen:seen.add(state);queue.append((*state,moves+1))
    return -1
'''


PRIME_SPLIT = '''def maximum_distinct_prime_split_counts(nums,queries):
    import heapq
    limit=100000;prime=bytearray(b'\\x01')*(limit+1);prime[:2]=b'\\x00\\x00'
    for value in range(2,int(limit**0.5)+1):
        if prime[value]:prime[value*value:limit+1:value]=b'\\x00'*(((limit-value*value)//value)+1)
    n=len(nums);positions={};low_heaps={};high_heaps={}
    for index,value in enumerate(nums):
        if prime[value]:
            positions.setdefault(value,set()).add(index);low_heaps.setdefault(value,[]).append(index);high_heaps.setdefault(value,[]).append(-index)
    for heap in low_heaps.values():heapq.heapify(heap)
    for heap in high_heaps.values():heapq.heapify(heap)
    size=max(1,n-1);tree=[0]*(4*size);lazy=[0]*(4*size)
    def add(node,left,right,start,end,delta):
        if start>right or end<left:return
        if start<=left and right<=end:tree[node]+=delta;lazy[node]+=delta;return
        middle=(left+right)//2;add(node*2,left,middle,start,end,delta);add(node*2+1,middle+1,right,start,end,delta)
        tree[node]=lazy[node]+max(tree[node*2],tree[node*2+1])
    def ends(value):
        members=positions[value];low=low_heaps[value];high=high_heaps[value]
        while low and low[0] not in members:heapq.heappop(low)
        while high and -high[0] not in members:heapq.heappop(high)
        return low[0],-high[0]
    def interval(value,delta):
        if value in positions and len(positions[value])>=2:
            first,last=ends(value)
            if first<last:add(1,1,n-1,first+1,last,delta)
    distinct=len(positions)
    for value in list(positions):interval(value,1)
    answer=[]
    for index,value in queries:
        old=nums[index]
        if old!=value:
            if prime[old]:
                interval(old,-1);positions[old].remove(index)
                if not positions[old]:distinct-=1
                else:interval(old,1)
            nums[index]=value
            if prime[value]:
                if value in positions and positions[value]:interval(value,-1)
                else:
                    positions.setdefault(value,set());low_heaps.setdefault(value,[]);high_heaps.setdefault(value,[]);distinct+=1
                positions[value].add(index);heapq.heappush(low_heaps[value],index);heapq.heappush(high_heaps[value],-index);interval(value,1)
        answer.append(distinct+tree[1])
    return answer
'''


SUPERSTRING = '''def shortest_two_string_superstring(s1,s2):
    if s1 in s2:return s2
    if s2 in s1:return s1
    candidates=[]
    for left,right in ((s1,s2),(s2,s1)):
        overlap=min(len(left),len(right))
        while overlap and not left.endswith(right[:overlap]):overlap-=1
        candidates.append(left+right[overlap:])
    return min(candidates,key=lambda text:(len(text),text))
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]


PRODUCT_CASES=[[nums,target] for nums,target in [([1,2,3],2),([1,2,4],4),([2,3,6],6),([1,3,8,24],24),([2,5,3,7],15),([1,2,3,6],6),([2,3,4,6],12),([1,5,10,2],10),([3,4,6,8],24),([1,7,14,2],14),([2,4,8],8),([1,2,6,12,3],36),([5,6,10,15],30),([1,3,6,8,4],24)]]
MATRIX_CASES=[[grid,k] for grid,k in [([[5]],1),([[3,-1]],1),([[1,1],[1,1]],2),([[1,2],[3,4]],2),([[1,-2,3],[2,3,5]],2),([[0,10,20]],1),([[0,10,20]],1),([[1,5,9],[2,6,10],[3,7,11]],2),([[-5,-1],[-3,-9]],2),([[1,1,2],[1,3,4]],2),([[100,-100],[50,0]],2),([[2,8,4],[6,0,10],[3,7,11]],3),([[1,2,1],[2,1,2],[1,2,1]],2),([[9,4,7,1],[3,8,2,6]],2)]]
CLASSROOM_CASES=[[room,e] for room,e in [(['S'],1),(['SL'],1),(['S.L'],2),(['S.L'],1),(['S.','XL'],2),(['LS','RL'],4),(['L.S','RXL'],3),(['SRL'],1),(['SXR','..L'],3),(['S..','XXX','L.R'],5),(['S.L','...','L.R'],3),(['SX','XL'],5),(['S.R','X.X','L.L'],4),(['L..','RS.','..L'],2)]]
PRIME_SPLIT_CASES=[[nums,queries] for nums,queries in [([2,3],[[0,3]]),([1,4],[[1,6]]),([2,1,4],[[0,1]]),([2,1,3,1,2],[[1,2],[3,3]]),([2,2,2],[[1,3]]),([2,3,5],[[1,2]]),([4,6,8],[[0,2],[2,3]]),([2,4,2,4],[[1,3],[2,5]]),([7,1,7,1,7],[[1,7]]),([2,3,2,3],[[0,5],[3,5]]),([11,13,17,19],[[2,13]]),([1,2,1,3,1,5],[[0,7],[5,1]]),([4,2,4,3,4],[[2,5],[1,4]]),([2,2,3,3,5,5],[[0,7],[5,7]])]]
SUPERSTRING_CASES=[[a,b] for a,b in [('a','b'),('a','a'),('ab','b'),('aba','bab'),('abc','bcd'),('bcd','abc'),('cat','atg'),('aaaa','aa'),('ab','ba'),('cab','abc'),('xyz','zab'),('hello','world'),('abcd','cdef'),('race','acer')]]


BATCH={
3566:entry('can_partition_equal_products',[('nums','list[int]'),('target','int')],'bool',['arrays','bit manipulation','enumeration'],['nums has 3 to 12 distinct positive integers, each at most 100.','Partition every element into two nonempty subsets.','Both subset products must equal target, which may be as large as 10^15.'],[([[3,1,6,8,4],24],'Products of [3,8] and [1,6,4] both equal 24.'),([[2,5,3,7],15],'No partition makes both subset products equal 15.')],PRODUCT_CASES,PRODUCT,[PRODUCT.replace('target*target','target'),PRODUCT.replace('if total!=target*target:return False','')],['Compares the full product with target rather than target squared.','Checks only whether some subset has product target, without requiring its complement to have the same product.'],product_oracle,random_product,lesson('If both subset products equal target, the product of the entire array must be target squared.','After the necessary total-product check, enumerate proper nonempty subset masks and test one side’s product.','Reject total!=target²; multiply selected elements for masks 1 through 2^n-2 and accept a product equal to target.','The complement is nonempty by the mask bounds and automatically has product target because the total is target².'),'O(n*2^n)','O(1)',5),
3567:entry('sliding_submatrix_min_difference',[('grid','list[list[int]]'),('k','int')],'list[list[int]]',['matrices','sorting','sliding windows'],['grid has at most 30 rows and columns; 1 <= k <= min(rows,columns).','For every contiguous k by k submatrix, compare distinct values only.','Return zero when a submatrix has fewer than two distinct values.'],[([[[1,8],[3,-2]],2],'Sorted distinct values are -2, 1, 3, and 8; the closest gap is two.'),([[[3,-1]],1],'Each one-cell submatrix has only one distinct value, producing zeros.')],MATRIX_CASES,MATRIX,[MATRIX.replace('sorted({','sorted([').replace('})','])'),MATRIX.replace('b-a','abs(b+a)')],['Keeps duplicate values, incorrectly producing a zero gap when two equal cells coexist with other values.','Adds adjacent values instead of subtracting them to measure their gap.'],matrix_oracle,random_matrix,lesson('In one window, the minimum difference among distinct values occurs between adjacent values in sorted order.','Collect a set for each k by k window, sort it, and scan neighboring gaps.','For each top-left coordinate, sort the window’s distinct values and append min(next-current), defaulting to zero.','Any nonadjacent sorted pair has a gap at least as large as one intervening adjacent gap, so checking neighbors is sufficient.'),'O((rows-k+1)(columns-k+1)k² log(k²))','O(k²)',5),
3568:entry('minimum_classroom_cleaning_moves',[('classroom','list[str]'),('energy','int')],'int',['graphs','breadth first search','bitmasking'],['The grid has at most 20 rows and columns, one start, and at most ten litter cells.','Each orthogonal move spends one energy; entering R immediately restores full energy and X is blocked.','Return the fewest moves collecting every litter item, or -1 when impossible.'],[([['S.','XL'],2],'Two moves around the obstacle reach and collect the litter.'),([['LS','RL'],4],'Collect the left litter, step onto the reset, then collect the second litter in three moves.')],CLASSROOM_CASES,CLASSROOM,[CLASSROOM.replace("=='R' else remaining-1","=='R' else remaining"),CLASSROOM.replace("if remaining==0:continue","if remaining<0:continue")],['Does not spend energy on ordinary moves.','Allows movement with zero energy away from a non-reset cell.'],classroom_oracle,random_classroom,lesson('Future choices depend on position, remaining energy, and which litter cells remain, so these form the BFS state.','Assign each litter a bit and breadth-first search transitions, resetting energy when entering R.','Pop states by move count; stop at mask zero; when energy is positive, enqueue legal neighbors with updated energy and mask.','BFS visits states in nondecreasing moves, and the state tuple contains every fact that can affect subsequent legal paths.'),'O(rows*columns*energy*2^litter)','O(rows*columns*energy*2^litter)',5),
3569:entry('maximum_distinct_prime_split_counts',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['segment trees','heaps','number theory'],['nums and queries each contain at most 50,000 entries; values are at most 100,000.','Updates persist, and every answer maximizes over nonempty prefix-suffix splits.','A prime appearing on both sides counts once in each side.'],[([[2,1,3,1,2],[[1,2],[3,3]]],'After the updates, optimal split scores are three and four.'),([[2,1,4],[[0,1]]],'After removing the only prime, every split scores zero.')],PRIME_SPLIT_CASES,PRIME_SPLIT,[PRIME_SPLIT.replace('answer.append(distinct+tree[1])','answer.append(distinct)'),PRIME_SPLIT.replace('max(tree[node*2],tree[node*2+1])','min(tree[node*2],tree[node*2+1])')],['Counts each distinct prime only once and omits the extra contribution from primes spanning the split.','Maintains minimum split coverage instead of the required maximum coverage.'],prime_split_oracle,random_prime_split,lesson('Every present prime contributes one; it contributes a second time exactly for splits after its first occurrence and at or before its last.','Maintain each prime’s extreme positions with lazy heaps and range-add its spanning split interval in a max segment tree.','Before an update remove old intervals, change position sets/heaps and distinct count, add new intervals, then return distinct+global maximum coverage.','For any split, the segment value counts precisely the primes present on both sides; adding the total distinct count equals the two side-set sizes.'),'O((n+queries) log n + V log log V)','O(n+V)',8),
3571:entry('shortest_two_string_superstring',[('s1','str'),('s2','str')],'str',['strings','overlaps','enumeration'],['Return a shortest string containing both inputs as substrings.','If one input contains the other, return the containing string.','For deterministic feedback, return the lexicographically smallest among equally short answers.'],[(['aba','bab'],'Both abab and baba are shortest; abab is lexicographically smaller.'),(['abc','bcd'],'Overlapping bc produces the shortest result abcd.')],SUPERSTRING_CASES,SUPERSTRING,[SUPERSTRING.replace('min(candidates,key=lambda text:(len(text),text))','candidates[0]'),SUPERSTRING.replace('if s2 in s1:return s1','if s2 in s1:return s1+s2')],['Always prefers the first orientation even when the reverse overlap is shorter.','Concatenates contained strings instead of returning the containing input.'],superstring_oracle,random_superstring,lesson('With two strings, an optimal answer either is the containing string or uses the largest suffix-prefix overlap in one of two orientations.','Build both maximal-overlap concatenations, then choose by length and lexicographic order.','Handle containment; for each ordering decrease overlap until suffix equals prefix; minimize (length,string).','Any superstring with neither input contained must place one before the other, and increasing their overlap never increases length, so the two maximal orientations exhaust all optima.'),'O((len(s1)+len(s2))^2)','O(len(s1)+len(s2))',3),
}
