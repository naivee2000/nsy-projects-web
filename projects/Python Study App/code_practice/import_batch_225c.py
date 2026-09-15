"""Pizza scheduling, special intervals, recursive diagonal paths, prefixes, and row limits."""
from itertools import combinations, permutations

from .import_batch_055 import entry


def pizza_oracle(args):
    pizzas=args[0];days=len(pizzas)//4;answer=0
    for order in permutations(pizzas):
        total=0
        for day in range(days):
            group=sorted(order[day*4:day*4+4],reverse=True);total+=group[0] if day%2==0 else group[1]
        answer=max(answer,total)
    return answer


def random_pizza(rng):
    n=rng.choice((4,8));return [[rng.randint(1,10) for _ in range(n)]]


def special_oracle(args):
    text,k=args;n=len(text);intervals=[]
    for left in range(n):
        for right in range(left,n):
            if left==0 and right==n-1:continue
            chosen=set(text[left:right+1])
            if all(char not in chosen for char in text[:left]+text[right+1:]):intervals.append((left,right))
    by_start=[[] for _ in range(n)]
    for left,right in intervals:by_start[left].append(right)
    best=[0]*(n+1)
    for left in range(n-1,-1,-1):
        best[left]=best[left+1]
        for right in by_start[left]:best[left]=max(best[left],1+best[right+1])
    return best[0]>=k


def random_special(rng):
    return [''.join(rng.choice('abcde') for _ in range(rng.randint(1,9))),rng.randint(1,4)]


DIRS=((1,1),(1,-1),(-1,-1),(-1,1))


def diagonal_path_oracle(args):
    grid=args[0];rows=len(grid);columns=len(grid[0]);answer=0
    def extend(row,column,direction,turned,expected,length):
        nonlocal answer
        answer=max(answer,length)
        choices=[(direction,turned)]
        if not turned:choices.append(((direction+1)%4,True))
        for following,new_turned in choices:
            dr,dc=DIRS[following];nr,nc=row+dr,column+dc
            if 0<=nr<rows and 0<=nc<columns and grid[nr][nc]==expected:extend(nr,nc,following,new_turned,2-expected,length+1)
    for row in range(rows):
        for column in range(columns):
            if grid[row][column]==1:
                for direction in range(4):extend(row,column,direction,False,2,1)
    return answer


def random_diagonal_path(rng):
    rows,columns=rng.randint(1,5),rng.randint(1,5)
    return [[[rng.randrange(3) for _ in range(columns)] for _ in range(rows)]]


def prefix_oracle(args):
    source,target=args;answer=0
    for removed in range(-1,len(source)):
        candidate=source if removed<0 else source[:removed]+source[removed+1:];length=0
        while length<min(len(candidate),len(target)) and candidate[length]==target[length]:length+=1
        answer=max(answer,length)
    return answer


def random_prefix(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,15))),''.join(rng.choice('abcd') for _ in range(rng.randint(1,15)))]


def grid_sum_oracle(args):
    grid,limits,k=args;cells=[(value,row) for row,values in enumerate(grid) for value in values];answer=0
    for size in range(min(k,len(cells))+1):
        for selected in combinations(cells,size):
            if all(sum(row==candidate for _,row in selected)<=limits[candidate] for candidate in range(len(grid))):answer=max(answer,sum(value for value,_ in selected))
    return answer


def random_grid_sum(rng):
    rows,columns=rng.randint(1,3),rng.randint(1,3);grid=[[rng.randint(1,15) for _ in range(columns)] for _ in range(rows)]
    return [grid,[rng.randint(0,columns) for _ in range(rows)],rng.randint(0,rows*columns)]


PIZZA='''def maximum_pizza_weight_gain(pizzas):
    pizzas=sorted(pizzas);days=len(pizzas)//4;odd=(days+1)//2;even=days-odd;answer=sum(pizzas[-odd:]);index=len(pizzas)-odd-2
    for _ in range(even):answer+=pizzas[index];index-=2
    return answer
'''

SPECIAL='''def can_select_k_special_substrings(s,k):
    if k==0:return True
    first={char:index for index,char in reversed(list(enumerate(s)))};last={char:index for index,char in enumerate(s)};intervals=[]
    for start,char in enumerate(s):
        if first[char]!=start:continue
        end=last[char];position=start;valid=True
        while position<=end:
            current=s[position]
            if first[current]<start:valid=False;break
            end=max(end,last[current]);position+=1
        if valid and not (start==0 and end==len(s)-1):intervals.append((end,start))
    count=0;previous=-1
    for end,start in sorted(intervals):
        if start>previous:count+=1;previous=end
    return count>=k
'''

DIAGONAL='''def longest_clockwise_v_diagonal(grid):
    from functools import lru_cache
    rows=len(grid);columns=len(grid[0]);directions=((1,1),(1,-1),(-1,-1),(-1,1))
    @lru_cache(None)
    def extend(row,column,direction,turns):
        expected=2 if grid[row][column]==1 else 2-grid[row][column];dr,dc=directions[direction];nr,nc=row+dr,column+dc
        if not (0<=nr<rows and 0<=nc<columns) or grid[nr][nc]!=expected:return 0
        answer=extend(nr,nc,direction,turns)
        if turns:answer=max(answer,extend(nr,nc,(direction+1)%4,0))
        return answer+1
    answer=0
    for row in range(rows):
        for column in range(columns):
            if grid[row][column]==1:
                for direction in range(4):answer=max(answer,extend(row,column,direction,1)+1)
    return answer
'''

PREFIX='''def longest_prefix_after_one_source_removal(s,t):
    source=target=0;removed=False
    while source<len(s) and target<len(t):
        if s[source]!=t[target]:
            if removed:break
            removed=True
        else:target+=1
        source+=1
    return target
'''

GRID_SUM='''def maximum_row_limited_grid_sum(grid,limits,k):
    import heapq
    chosen=[]
    for row,limit in zip(grid,limits):
        for value in sorted(row,reverse=True)[:limit]:
            heapq.heappush(chosen,value)
            if len(chosen)>k:heapq.heappop(chosen)
    return sum(chosen)
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


PIZZA_CASES=[[[value for value in pizzas]] for pizzas in [[1,2,3,4,5,6,7,8],[1,2,3,4],[4,4,4,4],[1,1,1,10],[9,8,7,6,5,4,3,2],[1,3,5,7,2,4,6,8],[10,10,9,9,1,1,1,1],[2,2,3,3,4,4,5,5],[1,20,2,19,3,18,4,17],[5,1,5,1,5,1,5,1],[8,1,7,2],[6,6,2,2,9,9,1,1],[3,8,2,7,4,6,1,5],[100,1,1,1,99,2,2,2]]]
SPECIAL_CASES=[[text,k] for text,k in [('abcdbaefab',2),('abcd',3),('a',1),('ab',1),('aa',1),('abac',1),('abac',2),('adefaddaccc',3),('abcba',1),('eccbbbbdec',1),('abab',1),('abcabcx',1),('xyzzxyab',2),('qwerty',4)]]
DIAGONAL_CASES=[[[row[:] for row in grid]] for grid in [[[2,2,1,2,2],[2,0,2,2,0],[2,0,1,1,0],[1,0,2,2,2],[2,0,0,2,2]],[[1]],[[0]],[[1,2],[2,0]],[[1,0],[0,2]],[[1,2,0],[2,0,2],[0,2,0]],[[0,0,1],[0,2,0],[0,0,0]],[[1,2,0,2]],[[1],[2],[0],[2]],[[2,0,2],[0,1,0],[2,0,2]],[[1,2,0],[0,0,2],[0,0,0]],[[0,0,1],[0,2,0],[0,0,2]],[[1,2,0,2],[2,0,2,0],[0,2,0,2],[2,0,2,0]],[[1,1],[2,2]]]]
PREFIX_CASES=[[source,target] for source,target in [('madxa','madam'),('leetcode','letcode'),('a','a'),('a','b'),('ab','b'),('abc','abc'),('abc','ac'),('xabcd','abcd'),('abxcd','abcd'),('abcdx','abcd'),('aaaa','aaa'),('banana','banaa'),('kitten','sitting'),('abcde','abfde')]]
GRID_SUM_CASES=[[grid,limits,k] for grid,limits,k in [([[1,2],[3,4]],[1,2],2),([[5]],[1],1),([[5]],[0],1),([[1,2,3]],[2],3),([[9,1],[8,2]],[1,1],1),([[9,1],[8,2]],[1,1],2),([[5,4,3],[9,1,1]],[2,1],2),([[1,10],[2,9],[3,8]],[1,1,1],2),([[7,7],[7,7]],[2,2],3),([[100,1,1],[50,49,48]],[1,2],3),([[4,6],[5,3]],[0,2],2),([[2,8,1],[7,3,9]],[3,1],3),([[10,9],[8,7],[6,5]],[1,1,1],0),([[1,20,3],[4,5,16],[7,14,9]],[2,2,2],4)]]


BATCH={
3457:entry('maximum_pizza_weight_gain',[('pizzas','list[int]')],'int',['arrays','sorting','greedy'],['pizzas contains a positive multiple of four positive weights and every pizza is eaten exactly once.','Each day uses four pizzas; odd days gain the heaviest selected weight and even days gain the second-heaviest.','Choose daily groups to maximize total gained weight.'],[([[1,2,3,4,5,6,7,8]],'Use eight as the odd-day maximum and place seven above six on the even day, gaining eight plus six equals fourteen.'),([[1,2,3,4]],'The sole odd day gains the heaviest pizza, four.')],PIZZA_CASES,PIZZA,[PIZZA.replace('odd=(days+1)//2','odd=days//2'),PIZZA.replace('index=len(pizzas)-odd-2','index=len(pizzas)-odd-1')],['Uses floor division for odd-day count and omits one gain when days is odd.','Selects the heaviest remaining pizza on even days instead of the required second-heaviest.'],pizza_oracle,random_pizza,lesson('Largest weights should be reserved for odd-day maxima; each even-day gain needs one larger sacrificial pizza.','Sort, take the largest odd-day count directly, then take every second remaining value for even days.','Let odd=ceil(days/2); sum that many largest weights, skip one larger partner before each even gain, and use smallest leftovers as fillers.','Exchange arguments move any larger gain candidate into an odd slot or the best feasible even second position without decreasing the total.'),'O(n log n)','O(n)',6),
3458:entry('can_select_k_special_substrings',[('s','str'),('k','int')],'bool',['strings','greedy','intervals'],['s has 1–50,000 lowercase letters.','A special substring is not all of s and every character it contains occurs nowhere outside it.','Return whether at least k pairwise non-overlapping special substrings can be selected.'],[(['abcdbaefab',2],'Two closed character intervals can be selected without overlap.'),(['aa',1],'The only closed interval is the whole string, which is forbidden, so return false.')],SPECIAL_CASES,SPECIAL,[SPECIAL.replace("and not (start==0 and end==len(s)-1)",''),SPECIAL.replace('end=max(end,last[current])','end=end')],['Counts the whole string as a valid special substring.','Does not expand an interval to include every occurrence of newly encountered characters.'],special_oracle,random_special,lesson('A special substring is a closed interval containing every global occurrence of each character it touches.','Construct the minimal valid closure from each character’s first occurrence, then greedily schedule valid intervals by end.','Expand the right edge using last occurrences; reject if any character began before the start; exclude the whole string and count disjoint intervals.','Minimal closures dominate larger choices, and earliest-finish interval scheduling maximizes how many non-overlapping closures fit.'),'O(26*n)','O(26)',6),
3459:entry('longest_clockwise_v_diagonal',[('grid','list[list[int]]')],'int',['matrices','recursion','memoization'],['grid is a nonempty matrix of 0, 1, and 2 values.','A path starts at 1 and then alternates 2,0,2,0 along diagonal steps.','It may continue straight or make at most one clockwise 90-degree turn; return its maximum length.'],[([[[2,2,1,2,2],[2,0,2,2,0],[2,0,1,1,0],[1,0,2,2,2],[2,0,0,2,2]]],'The longest valid diagonal follows the alternating sequence through five cells with one clockwise turn.'),([[[1]]],'A single starting one is itself a valid segment of length one.')],DIAGONAL_CASES,DIAGONAL,[DIAGONAL.replace('(direction+1)%4','(direction-1)%4'),DIAGONAL.replace('if grid[row][column]==1:','if grid[row][column]==2:')],['Allows a counterclockwise turn instead of the required clockwise turn.','Starts paths from value two rather than value one.'],diagonal_path_oracle,random_diagonal_path,lesson('The future depends on cell, direction, and whether the single clockwise turn remains.','Memoize a recursive extension for each state and start it from every cell containing one.','Require the next alternating value; recurse straight, and when available also recurse after rotating the direction clockwise.','Every valid segment has one start and a unique sequence of straight/turn choices, all represented by the memoized state graph.'),'O(rows*cols)','O(rows*cols)',8),
3460:entry('longest_prefix_after_one_source_removal',[('s','str'),('t','str')],'int',['strings','two pointers'],['s and t are nonempty lowercase strings.','Remove at most one character from s only; leaving s unchanged is allowed.','Return the maximum common-prefix length between the resulting s and t.'],[(['madxa','madam'],'After matching mad, remove x from s and match a, producing prefix length four.'),(['xabcd','abcd'],'Removing the initial x lets all four target characters match.')],PREFIX_CASES,PREFIX,[PREFIX.replace('removed=True','removed=True;target+=1'),PREFIX.replace('return target','return source')],['Advances the target at the mismatch, effectively removing from t instead of s.','Counts consumed source characters, including the removed mismatch, rather than matched prefix characters.'],prefix_oracle,random_prefix,lesson('Before the first mismatch, skipping that source character is the only removal that can extend the prefix.','Scan both strings; on the first mismatch advance only s, then require exact matches thereafter.','Advance both pointers on equality, consume the one removal on mismatch, and stop at a second mismatch.','Removing earlier equal characters would immediately shorten the prefix, while removing later cannot repair the first mismatch.'),'O(min(len(s),len(t)))','O(1)',5),
3462:entry('maximum_row_limited_grid_sum',[('grid','list[list[int]]'),('limits','list[int]'),('k','int')],'int',['matrices','sorting','heaps'],['grid is a nonempty positive-integer matrix and limits has one value per row.','Choose at most k cells total and no more than limits[i] cells from row i.','Return the maximum possible sum.'],[([[[1,2],[3,4]],[1,2],2],'The second row permits two selections, so taking four and three gives the maximum sum seven.'),([[[9,1],[8,2]],[1,1],1],'The global limit permits only the value nine.')],GRID_SUM_CASES,GRID_SUM,[GRID_SUM.replace('sorted(row,reverse=True)','sorted(row)'),GRID_SUM.replace('[:limit]','')],['Takes the smallest allowed values from each row.','Ignores row limits and makes every cell globally eligible.'],grid_sum_oracle,random_grid_sum,lesson('Only the largest limits[i] values of a row can belong to any optimal selection.','Collect those row-eligible values while retaining only the global k largest in a min-heap.','Sort each row descending, feed its allowed prefix to the heap, and pop whenever the heap exceeds k.','Any excluded row value is dominated by an included value from the same row, and the heap then enforces the remaining uniform global limit.'),'O(total_cells log columns+eligible log k)','O(k)',6),
}
