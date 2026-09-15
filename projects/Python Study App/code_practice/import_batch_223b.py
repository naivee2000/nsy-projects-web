"""Frequency editing, XOR paths, grid cuts, unique modes, and distinct assignments."""
from collections import Counter, deque
from itertools import combinations
from math import comb

from .import_batch_055 import entry

MOD = 1_000_000_007


def frequency_oracle(args):
    first = min(map(ord, args[0])); last = max(map(ord, args[0]))
    counts = tuple(Counter(args[0])[chr(code)] for code in range(first, last + 1))
    limit = 2 * len(args[0]); queue = deque([(counts, 0)]); seen = {counts}
    while queue:
        state, distance = queue.popleft()
        positive = [value for value in state if value]
        if positive and len(set(positive)) == 1:
            return distance
        for index in range(len(state)):
            candidates = []
            if state[index]:
                removed = list(state); removed[index] -= 1; candidates.append(tuple(removed))
                if index + 1 < len(state):
                    moved = list(state); moved[index] -= 1; moved[index + 1] += 1; candidates.append(tuple(moved))
            if sum(state) < limit:
                added = list(state); added[index] += 1; candidates.append(tuple(added))
            for candidate in candidates:
                if candidate not in seen:
                    seen.add(candidate); queue.append((candidate, distance + 1))


def random_frequency(rng):
    return [''.join(rng.choice('abc') for _ in range(rng.randint(3, 8)))]


def xor_oracle(args):
    grid, target = args; rows = len(grid); columns = len(grid[0]); answer = 0
    def visit(row, column, value):
        nonlocal answer
        value ^= grid[row][column]
        if row == rows - 1 and column == columns - 1:
            answer += value == target; return
        if row + 1 < rows: visit(row + 1, column, value)
        if column + 1 < columns: visit(row, column + 1, value)
    visit(0, 0, 0); return answer % MOD


def random_xor(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randrange(16) for _ in range(columns)] for _ in range(rows)], rng.randrange(16)]


def cuts_oracle(args):
    _, rectangles = args
    def possible(axis):
        starts = sorted({rectangle[axis] for rectangle in rectangles} | {rectangle[axis + 2] for rectangle in rectangles})
        for first, second in combinations(starts, 2):
            groups = [0, 0, 0]; valid = True
            for rectangle in rectangles:
                low, high = rectangle[axis], rectangle[axis + 2]
                if high <= first: groups[0] += 1
                elif low >= second: groups[2] += 1
                elif low >= first and high <= second: groups[1] += 1
                else: valid = False; break
            if valid and all(groups): return True
        return False
    return possible(0) or possible(1)


def random_cuts(rng):
    n = rng.randint(4, 8); cells = rng.sample([(x, y) for x in range(n) for y in range(n)], rng.randint(3, min(9, n * n)))
    return [n, [[x, y, x + 1, y + 1] for x, y in cells]]


def mode_oracle(args):
    nums = args[0]; answer = 0
    for indices in combinations(range(len(nums)), 5):
        values = [nums[index] for index in indices]; counts = Counter(values); middle = values[2]
        answer += counts[middle] > max((count for value, count in counts.items() if value != middle), default=0)
    return answer % MOD


def random_mode(rng):
    return [[rng.randint(-3, 3) for _ in range(rng.randint(5, 11))]]


def distinct_oracle(args):
    nums, k = args; choices = [range(value - k, value + k + 1) for value in nums]; best = 0
    def search(index, used):
        nonlocal best
        if index == len(nums): best = max(best, len(used)); return
        if len(used) + len(nums) - index <= best: return
        for value in choices[index]: search(index + 1, used | {value})
    search(0, set()); return best


def random_distinct(rng):
    return [[rng.randint(1, 10) for _ in range(rng.randint(1, 7))], rng.randint(0, 2)]


FREQUENCY = '''def minimum_equal_frequency_operations(s):
    from collections import Counter
    counts=[Counter(s).get(chr(97+index),0) for index in range(26)];answer=len(s)
    for target in range(1,max(counts)+1):
        dp=[10**30]*27;dp[0]=0
        for index in range(26):
            current=counts[index]
            dp[index+1]=min(dp[index+1],dp[index]+min(current,abs(current-target)))
            if index+1<26:
                following=counts[index+1];pair=10**30
                for first in (0,target):
                    for second in (0,target):
                        moved=min(max(current-first,0),max(second-following,0))
                        pair=min(pair,abs(current-first)+abs(following-second)-moved)
                dp[index+2]=min(dp[index+2],dp[index]+pair)
        answer=min(answer,dp[26])
    return answer
'''

XOR_PATHS = '''def count_grid_xor_paths(grid,k):
    modulo=1000000007;rows=len(grid);columns=len(grid[0]);previous=None
    for row in range(rows):
        current=[[0]*16 for _ in range(columns)]
        for column in range(columns):
            value=grid[row][column]
            if row==0 and column==0:current[column][value]=1;continue
            if row:
                for old,count in enumerate(previous[column]):current[column][old^value]=(current[column][old^value]+count)%modulo
            if column:
                for old,count in enumerate(current[column-1]):current[column][old^value]=(current[column][old^value]+count)%modulo
        previous=current
    return previous[-1][k]
'''

CUTS = '''def can_cut_grid_sections(n,rectangles):
    def groups(axis):
        intervals=sorted((rectangle[axis],rectangle[axis+2]) for rectangle in rectangles);count=0;end=-1
        for left,right in intervals:
            if left>=end:count+=1;end=right
            else:end=max(end,right)
        return count
    return groups(0)>=3 or groups(1)>=3
'''

MODE = '''def count_unique_middle_mode(nums):
    from collections import Counter
    from itertools import combinations
    from math import comb
    modulo=1000000007;right=Counter(nums);left=Counter();answer=0;n=len(nums)
    def choose2(value):return value*(value-1)//2
    for middle,x in enumerate(nums):
        right[x]-=1
        if right[x]==0:del right[x]
        left_size=middle;right_size=n-middle-1;lx=left.get(x,0);rx=right.get(x,0)
        ln=left_size-lx;rn=right_size-rx
        at_least_two=0
        for a in range(3):
            for b in range(3):
                if a+b>=2 and a<=lx and 2-a<=ln and b<=rx and 2-b<=rn:
                    at_least_two+=comb(lx,a)*comb(ln,2-a)*comb(rx,b)*comb(rn,2-b)
        pair_left=sum(left[a]*left[b] for a,b in combinations(left,2) if a!=x and b!=x)
        pair_right=sum(right[a]*right[b] for a,b in combinations(right,2) if a!=x and b!=x)
        correction_left=sum(left[value]*right.get(value,0)*(rn-right.get(value,0)) for value in left if value!=x)
        correction_right=sum(right[value]*left.get(value,0)*(ln-left.get(value,0)) for value in right if value!=x)
        distinct_three_left=ln*pair_right-correction_left
        distinct_three_right=rn*pair_left-correction_right
        answer=(answer+at_least_two+lx*distinct_three_left+rx*distinct_three_right)%modulo
        left[x]+=1
    return answer
'''

DISTINCT = '''def maximum_distinct_after_adjustment(nums,k):
    previous=float('-inf');answer=0
    for value in sorted(nums):
        chosen=min(value+k,max(value-k,previous+1))
        if chosen>previous:answer+=1;previous=chosen
    return answer
'''


def lesson(a,b,c,d): return [a,b,c,d]


FREQUENCY_CASES=[[s] for s in ['acab','aaa','abc','aabb','aabbb','zzzz','yyyzz','abbccc','aaaab','abcc','aabbccdd','abcddd','xyzzz','aaabbbbcc']]
XOR_CASES=[[grid,k] for grid,k in [
    ([[2,1,5],[7,10,0],[12,6,4]],11),([[0]],0),([[1]],0),([[1,2]],3),([[1],[2]],3),
    ([[1,2],[3,4]],7),([[1,1],[1,1]],1),([[0,0],[0,0]],0),([[15,15],[15,15]],15),
    ([[1,2,3],[4,5,6]],0),([[2,4],[8,1],[3,7]],6),([[0,1,2],[3,4,5],[6,7,8]],9),
    ([[5,5,5,5]],0),([[1],[2],[4],[8]],15)]]
CUT_CASES=[[n,r] for n,r in [
    (5,[[1,0,5,2],[0,2,2,4],[3,2,5,3],[0,4,4,5]]),
    (4,[[0,0,1,1],[1,0,2,1],[2,0,3,1]]),(4,[[0,0,1,1],[0,1,1,2],[0,2,1,3]]),
    (4,[[0,0,2,2],[2,0,4,2],[0,2,4,4]]),(6,[[0,0,2,2],[2,0,4,2],[4,0,6,2]]),
    (6,[[0,0,6,1],[0,1,6,2],[0,2,6,3]]),(5,[[0,0,2,2],[2,2,4,4],[4,4,5,5]]),
    (5,[[0,0,3,1],[0,1,3,2],[2,2,5,3]]),(7,[[0,0,2,2],[3,0,5,2],[0,3,2,5],[3,3,5,5]]),
    (5,[[0,0,1,5],[1,0,2,5],[2,0,5,5]]),(8,[[0,0,8,2],[0,3,8,5],[0,6,8,8]]),
    (6,[[0,0,2,6],[2,0,4,6],[4,0,6,6]]),(5,[[0,0,2,2],[2,0,4,2],[1,2,3,4]]),
    (9,[[0,0,3,3],[3,3,6,6],[6,6,9,9]])]]
MODE_CASES=[[[v for v in values]] for values in [
    [1,1,1,1,1,1],[1,2,3,4,5],[1,1,2,3,4],[1,2,1,2,1],[0,0,0,0,0],
    [1,2,2,2,3,4],[1,1,2,2,3,3],[1,2,3,2,1,2],[5,4,5,3,5,2,5],
    [-1,-1,0,1,-1,2],[1,2,1,3,1,4,1],[2,2,3,2,3,2,4],
    [0,1,0,1,0,2,0,3],[3,3,3,2,2,1,1,3]]]
DISTINCT_CASES=[[nums,k] for nums,k in [
    ([1,2,2,3,3,4],2),([1],0),([1,1],0),([1,1],1),([1,2,3],0),([5,5,5],1),
    ([1,1,1,1],2),([1,3,5],1),([10,10,11,11],1),([1,2,2,2,3],1),
    ([100,100,100],100),([4,7,7,10],2),([1,5,9],0),([2,2,4,4,6,6],1)]]


BATCH={
3389:entry('minimum_equal_frequency_operations',[('s','str')],'int',['strings','dynamic programming','frequency counting'],['s has 3–20,000 lowercase letters.','One operation may delete a character, insert a character, or replace a character by its next alphabet letter; z cannot advance.','Make every character that remains occur the same positive number of times using the fewest operations.'],[(['acab'],'Changing c to b gives two a and two b characters in one operation.'),(['aabb'],'Both present letters already occur twice, so zero operations are needed.')],FREQUENCY_CASES,FREQUENCY,[FREQUENCY.replace("moved=min(max(current-first,0),max(second-following,0))","moved=0"),FREQUENCY.replace("for target in range(1,max(counts)+1)","for target in range(1,max(counts))")],['Never uses the cheaper next-letter replacement between adjacent frequencies.','Fails to consider keeping the current maximum frequency as the common target.'],frequency_oracle,random_frequency,lesson('For a fixed target, each letter is either removed or adjusted to that frequency.','Adjacent excess can replace into the next letter, saving one operation versus delete plus insert; optimal transfers form disjoint adjacent pairs.','Run a 26-position DP with single-letter and paired-letter transitions for every target frequency.','A letter that receives useful excess cannot also have excess to send, so the single/pair tiling captures every beneficial replacement.'),'O(26*n)','O(26)',8),
3393:entry('count_grid_xor_paths',[('grid','list[list[int]]'),('k','int')],'int',['matrices','dynamic programming','bit manipulation'],['grid has at most 300 rows and columns; every value and k is in 0..15.','Move only right or down from the top-left to bottom-right cell.','Count paths whose inclusive cell XOR equals k, modulo 1,000,000,007.'],[([[[2,1,5],[7,10,0],[12,6,4]],11],'Exactly three right/down paths produce XOR eleven.'),([[[0]],0],'The single-cell path has XOR zero, so it contributes one.')],XOR_CASES,XOR_PATHS,[XOR_PATHS.replace('old^value','old',1),XOR_PATHS.replace('previous[-1][k]','previous[-1][0]')],['Fails to include the current cell in transitions from above.','Always returns the count for XOR zero instead of the requested target.'],xor_oracle,random_xor,lesson('Only sixteen XOR states can reach each cell.','Accumulate path counts by ending cell and current XOR, reusing the previous row.','For each cell, XOR its value into every state arriving from above and left.','Every valid path has one unique final move, so the two predecessor distributions partition all paths.'),'O(rows*cols*16)','O(cols*16)',5),
3394:entry('can_cut_grid_sections',[('n','int'),('rectangles','list[list[int]]')],'bool',['intervals','sorting','greedy'],['The grid side n may reach one billion; at least three axis-aligned rectangles are pairwise non-overlapping.','Choose two horizontal or two vertical full-grid cuts that do not cross a rectangle.','Each of the three resulting sections must contain at least one whole rectangle.'],[([5,[[1,0,5,2],[0,2,2,4],[3,2,5,3],[0,4,4,5]]],'Horizontal boundaries separate the rectangles into three nonempty bands.'),([4,[[0,0,2,2],[2,0,4,2],[0,2,4,4]]],'Neither axis has three separable interval groups, so two valid cuts do not exist.')],CUT_CASES,CUTS,[CUTS.replace('left>=end','left>end'),CUTS.replace('groups(0)>=3 or groups(1)>=3','groups(0)>=2 or groups(1)>=2')],['Treats touching interval boundaries as overlapping and misses legal cuts.', 'Accepts only two sections instead of requiring three.'],cuts_oracle,random_cuts,lesson('Cuts along one axis depend only on rectangle projections onto that axis.','Merge overlapping projections and count separated interval groups.','Sort starts; begin a new group when the next start is at least the current merged end; test for three groups.', 'A cut can lie between every two consecutive merged groups, so two cuts exist exactly when some axis has at least three groups.'),'O(r log r)','O(r)',5),
3395:entry('count_unique_middle_mode',[('nums','list[int]')],'int',['arrays','combinatorics','frequency counting'],['nums has 5–1,000 integers.','Choose five indices in increasing order; the third selected value must be the unique most frequent value.','Return the count modulo 1,000,000,007.'],[([[1,1,1,1,1,1]],'Every choice of five positions has the middle value as its unique mode, giving six.'),([[1,2,3,4,5]],'All five values tie at frequency one, so the sole subsequence is invalid.')],MODE_CASES,MODE,[MODE.replace("correction_left=sum(left[value]*right.get(value,0)*(rn-right.get(value,0)) for value in left if value!=x)","correction_left=0").replace("correction_right=sum(right[value]*left.get(value,0)*(ln-left.get(value,0)) for value in right if value!=x)","correction_right=0"),MODE.replace('+lx*distinct_three_left+rx*distinct_three_right','')],['Allows another value to tie the middle value at frequency two.','Counts only subsequences containing at least three copies of the middle value.'],mode_oracle,random_mode,lesson('The middle value is uniquely modal if it appears at least three times, or exactly twice while the other three values are distinct.','Maintain left/right frequencies around each middle index and count both cases combinatorially.','Enumerate how extra middle copies split across sides; use distinct-value pair totals and overlap corrections for the exactly-two case.','The cases partition all valid length-five subsequences, and frequency products count every index choice exactly once.'),'O(n*d)','O(d)',8),
3397:entry('maximum_distinct_after_adjustment',[('nums','list[int]'),('k','int')],'int',['arrays','greedy','sorting'],['nums has up to 100,000 positive integers and k is nonnegative.','Each element may independently become any integer in its inclusive interval [value-k,value+k].','Maximize the number of distinct final values.'],[([[1,2,2,3,3,4],2],'Assign the six intervals consecutive values from negative one through four, making all elements distinct.'),([[5,5,5],1],'The three copies can become four, five, and six, so all three are distinct.')],DISTINCT_CASES,DISTINCT,[DISTINCT.replace('max(value-k,previous+1)','value-k'),DISTINCT.replace('previous+1','previous')],['Always takes each interval’s left endpoint and creates avoidable duplicates.','Allows the next assigned value to equal the previous one.'],distinct_oracle,random_distinct,lesson('Each number supplies an interval of possible final integer values.','Sort intervals by center and greedily take the smallest available integer after the previous assignment.','Choose min(right endpoint, max(left endpoint, previous+1)); count it when it advances.','Using the earliest feasible value leaves at least as much room for every later interval as any larger choice.'),'O(n log n)','O(n)',5),
}
