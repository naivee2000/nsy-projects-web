"""Circular removals, bowling, painting, special roads, and beautiful strings batch 170."""

from collections import deque
from itertools import product

from .import_batch_055 import entry


def empty_oracle(args):
    values=deque(args[0]);operations=0
    while values:
        if values[0]==min(values):values.popleft()
        else:values.append(values.popleft())
        operations+=1
    return operations


def random_empty(rng):
    size=rng.randint(1,12)
    return [rng.sample(range(-30,31),size)]


def bowling_oracle(args):
    def score(values):
        total=0
        for index,value in enumerate(values):
            bonus=any(values[prior]==10 for prior in (index-1,index-2) if prior>=0)
            total+=value*(2 if bonus else 1)
        return total
    first,second=map(score,args)
    return 1 if first>second else 2 if second>first else 0


def random_bowling(rng):
    n=rng.randint(1,20)
    return [[rng.randint(0,10) for _ in range(n)],[rng.randint(0,10) for _ in range(n)]]


def paint_oracle(args):
    order,matrix=args;rows=len(matrix);columns=len(matrix[0]);painted=set()
    for step,value in enumerate(order):
        painted.add(value)
        if any(all(matrix[row][column] in painted for column in range(columns)) for row in range(rows)):return step
        if any(all(matrix[row][column] in painted for row in range(rows)) for column in range(columns)):return step


def random_paint(rng):
    rows,columns=rng.randint(1,5),rng.randint(1,5);values=list(range(1,rows*columns+1));rng.shuffle(values)
    matrix=[values[row*columns:(row+1)*columns] for row in range(rows)];order=values.copy();rng.shuffle(order)
    return [order,matrix]


def roads_oracle(args):
    start,target,roads=args
    points=[tuple(start),tuple(target)]
    for x1,y1,x2,y2,_ in roads:points.extend(((x1,y1),(x2,y2)))
    points=list(dict.fromkeys(points));index={point:i for i,point in enumerate(points)};n=len(points)
    distance=[[abs(a[0]-b[0])+abs(a[1]-b[1]) for b in points] for a in points]
    for x1,y1,x2,y2,cost in roads:
        left,right=index[(x1,y1)],index[(x2,y2)];distance[left][right]=min(distance[left][right],cost)
    for middle in range(n):
        for left in range(n):
            for right in range(n):distance[left][right]=min(distance[left][right],distance[left][middle]+distance[middle][right])
    return distance[index[tuple(start)]][index[tuple(target)]]


def random_roads(rng):
    start=[rng.randint(0,15),rng.randint(0,15)];target=[rng.randint(0,15),rng.randint(0,15)];roads=[]
    for _ in range(rng.randint(0,7)):
        x1,y1,x2,y2=[rng.randint(0,15) for _ in range(4)];roads.append([x1,y1,x2,y2,rng.randint(1,20)])
    return [start,target,roads]


def beautiful_oracle(args):
    s,k=args;alphabet='abcdefghijklmnopqrstuvwxyz'[:k]
    for chars in product(alphabet,repeat=len(s)):
        candidate=''.join(chars)
        if candidate>s and all((i<1 or candidate[i]!=candidate[i-1]) and (i<2 or candidate[i]!=candidate[i-2]) for i in range(len(candidate))):return candidate
    return ''


def random_beautiful(rng):
    k=rng.randint(3,5);length=rng.randint(1,6);valid=[]
    for chars in product('abcde'[:k],repeat=length):
        word=''.join(chars)
        if all((i<1 or word[i]!=word[i-1]) and (i<2 or word[i]!=word[i-2]) for i in range(length)):valid.append(word)
    return [rng.choice(valid),k]


def distinct_oracle(args):
    nums=args[0]
    return [len(set(nums[:index+1]))-len(set(nums[index+1:])) for index in range(len(nums))]


def random_distinct(rng):return [[rng.randint(-10,10) for _ in range(rng.randint(1,40))]]


EMPTY="""\
def operations_to_empty_distinct_array(nums):
    class Fenwick:
        def __init__(self,n):self.tree=[0]*(n+1)
        def add(self,index,delta):
            index+=1
            while index<len(self.tree):self.tree[index]+=delta;index+=index&-index
        def prefix(self,end):
            total=0
            while end:total+=self.tree[end];end-=end&-end
            return total
        def range(self,left,right):return self.prefix(right)-self.prefix(left)
    n=len(nums);tree=Fenwick(n)
    for index in range(n):tree.add(index,1)
    positions={value:index for index,value in enumerate(nums)};current=0;answer=0
    for value in sorted(nums):
        target=positions[value]
        if current<=target:answer+=tree.range(current,target+1)
        else:answer+=tree.range(current,n)+tree.range(0,target+1)
        tree.add(target,-1);current=(target+1)%n
    return answer
"""

BOWLING="""\
def bowling_game_winner(player1,player2):
    def score(values):
        total=0
        for index,value in enumerate(values):
            doubled=(index>=1 and values[index-1]==10) or (index>=2 and values[index-2]==10)
            total+=value*(2 if doubled else 1)
        return total
    first,second=score(player1),score(player2)
    return 1 if first>second else 2 if second>first else 0
"""

PAINT="""\
def first_complete_painted_line(arr,mat):
    rows=len(mat);columns=len(mat[0]);position={mat[r][c]:(r,c) for r in range(rows) for c in range(columns)}
    row_counts=[0]*rows;column_counts=[0]*columns
    for step,value in enumerate(arr):
        row,column=position[value];row_counts[row]+=1;column_counts[column]+=1
        if row_counts[row]==columns or column_counts[column]==rows:return step
"""

ROADS="""\
def minimum_special_road_cost(start,target,specialRoads):
    import heapq
    def distance(first,second):return abs(first[0]-second[0])+abs(first[1]-second[1])
    heap=[(0,start[0],start[1])];best={tuple(start):0};answer=distance(start,target)
    while heap:
        cost,x,y=heapq.heappop(heap)
        if cost!=best[(x,y)]:continue
        answer=min(answer,cost+distance((x,y),target))
        for x1,y1,x2,y2,road_cost in specialRoads:
            following=cost+distance((x,y),(x1,y1))+road_cost;point=(x2,y2)
            if following<best.get(point,10**30):best[point]=following;heapq.heappush(heap,(following,x2,y2))
    return answer
"""

BEAUTIFUL="""\
def next_beautiful_string(s,k):
    chars=list(s);limit=ord('a')+k
    for index in range(len(chars)-1,-1,-1):
        for code in range(ord(chars[index])+1,limit):
            char=chr(code)
            if index>0 and chars[index-1]==char or index>1 and chars[index-2]==char:continue
            chars[index]=char
            for following in range(index+1,len(chars)):
                for replacement in map(chr,range(ord('a'),limit)):
                    if following>0 and chars[following-1]==replacement or following>1 and chars[following-2]==replacement:continue
                    chars[following]=replacement;break
            return ''.join(chars)
    return ''
"""

DISTINCT="""\
def distinct_prefix_suffix_differences(nums):
    suffix=[0]*(len(nums)+1);seen=set()
    for index in range(len(nums)-1,-1,-1):seen.add(nums[index]);suffix[index]=len(seen)
    seen.clear();answer=[]
    for index,value in enumerate(nums):seen.add(value);answer.append(len(seen)-suffix[index+1])
    return answer
"""


BATCH={
2659:entry('operations_to_empty_distinct_array',[('nums','list[int]')],'int',['arrays','fenwick trees','greedy','sorting'],
 ['nums contains distinct integers.','Repeatedly remove the first value when it is currently smallest; otherwise move that first value to the end.','Return the total number of removals and moves until the array is empty.'],
 [([[3,4,-1]],'Rotate twice to expose -1, then each remaining value is removed, for five operations.'),([[1,2,4,3]],'One and two are removed immediately, then four rotates behind three before both are removed, for five operations.')],
 [[a] for a in [[1],[2,1],[1,2],[3,2,1],[1,3,2],[3,4,-1],[5,1,4,2,3],[-3,-1,-2],[10,0,-10],[2,5,1,4,3],[6,1,5,2,4,3],[1,5,2,6,3,7,4],[9,8,1,7,2,6,3],[4,-2,7,0,9]]],
 EMPTY,[EMPTY.replace("else:answer+=tree.range(current,n)+tree.range(0,target+1)","else:answer+=tree.range(current,n)"),EMPTY.replace('tree.add(target,-1)','tree.add(current,-1)')],
 ['Omits the wrapped prefix cost when the next smallest value lies before the current position.','Removes the scan-start position rather than the selected smallest value.'],empty_oracle,random_empty,
 ['Remove values in increasing numeric order; only rotations determine the cost between removals.','A Fenwick tree stores which original indices remain alive.','Count live indices from the current position through the target, wrapping at n when necessary; remove the target and continue after it.','Original circular order among survivors never changes, so each counted live index corresponds to exactly one move or final removal.'],'O(n log n)','O(n)',8),
2660:entry('bowling_game_winner',[('player1','list[int]'),('player2','list[int]')],'int',['arrays','simulation'],
 ['Both arrays give pins knocked down on equal numbers of turns.','A turn scores double when either of the preceding two turns for that player knocked down ten pins.','Return 1 for a higher player-one score, 2 for player two, or 0 for a tie.'],
 [([[5,10,3,2],[6,5,7,3]],'Player one receives doubled scores after the ten-pin turn and wins.'),([[3,5,7,6],[8,10,10,2]],'Player two receives the larger bonus-adjusted total and wins.')],
 [[a,b] for a,b in [([0],[0]),([10],[10]),([10,1],[0,3]),([0,3],[10,1]),([10,0,5],[0,5,5]),([1,10,2,3],[1,1,10,2]),([10,10,1],[10,1,1]),([5,5,5],[5,5,5]),([0,10,0,10],[10,0,10,0]),([10,2,2,2],[9,9,1,1]),([1,2,10,4,5],[3,3,3,3,3]),([10,0,0],[0,0,10]),([4,10,6,1],[5,5,5,5]),([10,10,10,10],[9,9,9,9])]],
 BOWLING,[BOWLING.replace('index>=2 and values[index-2]==10','index>2 and values[index-2]==10'),BOWLING.replace('(2 if doubled else 1)','(2 if value==10 else 1)')],
 ['Misses the two-turn bonus at index two.','Doubles only a strike itself instead of following turns.'],bowling_oracle,random_bowling,
 ['Score each player independently.','For turn i, inspect indices i-1 and i-2 only when they exist.','Double the current pins if either inspected value is ten, then compare totals.','The loop applies the rule to every turn exactly once; the final three-way comparison directly implements the required winner code.'],'O(n)','O(1)',3),
2661:entry('first_complete_painted_line',[('arr','list[int]'),('mat','list[list[int]]')],'int',['arrays','hash maps','matrices'],
 ['arr and mat each contain every integer one through rows*columns exactly once.','Paint the cell containing arr[i] at step i.','Return the earliest zero-based step that completes any full row or full column.'],
 [([[1,3,4,2],[[1,4],[2,3]]],'After steps zero through two, the right column containing four and three is complete, so return two.'),([[2,8,7,4,1,3,5,6,9],[[3,2,5],[1,4,6],[8,7,9]]],'The middle column is completed when four is painted at step three.')],
 [[a,m] for a,m in [([1],[[1]]),([1,2],[[1,2]]),([2,1],[[1],[2]]),([1,2,3,4],[[1,2],[3,4]]),([1,3,2,4],[[1,2],[3,4]]),([4,3,2,1],[[1,2],[3,4]]),([1,4,2,5,3,6],[[1,2,3],[4,5,6]]),([1,2,3,4,5,6],[[1,4],[2,5],[3,6]]),([5,1,9,2,6,3,7,4,8],[[1,2,3],[4,5,6],[7,8,9]]),([2,1,4,3],[[4,1],[2,3]]),([3,1,2],[[1,2,3]]),([3,2,1],[[1],[2],[3]]),([6,5,4,3,2,1],[[1,2],[3,4],[5,6]]),([1,6,2,5,3,4],[[1,2,3],[4,5,6]])]],
 PAINT,[PAINT.replace('or column_counts[column]==rows','and column_counts[column]==rows'),PAINT.replace('return step','return step+1')],
 ['Requires the newly painted row and column to complete simultaneously.','Returns a one-based step instead of the required zero-based index.'],paint_oracle,random_paint,
 ['Map every matrix value to its row and column.','Maintain painted counts for every row and column.','For each value in arr, increment its two counts and return as soon as either reaches its full length.','Unique values mean each step paints one new cell, so a count reaches its dimension exactly at the first completion of that line.'],'O(rows*columns)','O(rows+columns+rows*columns)',5),
2662:entry('minimum_special_road_cost',[('start','list[int]'),('target','list[int]'),('specialRoads','list[list[int]]')],'int',['graphs','shortest paths','heaps'],
 ['Ordinary travel between any two integer-coordinate points costs their Manhattan distance.','A directed special road [x1,y1,x2,y2,cost] may be used any number of times after ordinary travel to its start.','Return the minimum total cost from start to target.'],
 [([[1,1],[4,5],[[1,2,3,3,2],[3,4,4,5,1]]],'Ordinary movement into the two special roads produces minimum total cost five.'),([[3,2],[5,7],[[3,2,3,4,4],[3,3,5,5,3],[5,5,5,7,2]]],'Combining useful directed roads and ordinary movement costs five.')],
 [[s,t,r] for s,t,r in [([0,0],[0,0],[]),([0,0],[3,4],[]),([0,0],[3,0],[[0,0,3,0,1]]),([0,0],[3,0],[[3,0,0,0,1]]),([1,1],[4,5],[[1,2,3,3,2],[3,4,4,5,1]]),([0,0],[10,10],[[0,0,5,5,20],[5,5,10,10,1]]),([0,0],[10,0],[[2,0,8,0,1]]),([5,5],[0,0],[[5,5,1,1,2]]),([0,0],[5,5],[[0,0,3,3,2],[3,3,0,0,1]]),([2,2],[8,8],[[0,0,8,8,1]]),([1,5],[9,1],[[1,5,5,5,2],[5,5,9,1,3]]),([0,0],[6,6],[[1,1,2,2,1],[2,2,5,5,2]]),([10,10],[1,1],[[10,10,5,5,3],[5,5,1,1,4]]),([0,0],[4,4],[[0,0,4,4,20]])]],
 ROADS,[ROADS.replace('+road_cost','+0'),ROADS.replace('distance((x,y),(x1,y1))','distance((x,y),(x2,y2))')],
 ['Treats every special road as free after reaching its start.','Charges ordinary travel to the road endpoint rather than its start.'],roads_oracle,random_roads,
 ['Treat the start and every special-road endpoint as shortest-path states.','From a state, update the direct Manhattan route to target.','For every special road, pay Manhattan distance to its start plus road cost, and relax its endpoint in Dijkstra’s heap.','Any optimal route alternates ordinary segments with special roads; each alternation is represented, and nonnegative costs make Dijkstra finalization valid.'],'O(r² log r)','O(r)',6),
2663:entry('next_beautiful_string',[('s','str'),('k','int')],'str',['strings','greedy','backtracking'],
 ['s uses the first k lowercase letters and contains no equal characters at distance one or two.','Return the lexicographically smallest valid string of the same length that is strictly greater than s.','Return an empty string when no such string exists.'],
 [(['abcz',26],'Incrementing the third position to d permits the smallest suffix a, producing abda.'),(['dc',4],'No larger length-two string over a through d avoids equal adjacent characters, so return empty.')],
 [[s,k] for s,k in [('a',3),('c',3),('ab',3),('ac',3),('ba',3),('cb',3),('abc',3),('acb',3),('cba',3),('abcd',4),('abdc',4),('dcba',4),('abcabc',3),('abac',4)]],
 BEAUTIFUL,[BEAUTIFUL.replace('range(len(chars)-1,-1,-1)','range(0,len(chars))'),BEAUTIFUL.replace("chars[following-2]==replacement","chars[following-1]==replacement")],
 ['Attempts to increase the leftmost position first and skips smaller valid successors.','Checks the immediately previous character twice and can create length-three palindromes.'],beautiful_oracle,random_beautiful,
 ['Try to increase positions from right to left, analogous to carrying in base k.','At a position, reject a new character equal to either of the previous two characters.','After the first valid increase, greedily fill every suffix position with its smallest allowed character.','The rightmost feasible increase changes the shortest possible prefix, and the greedy suffix is the lexicographically least valid completion of that prefix.'],'O(n*k)','O(n)',8),
2670:entry('distinct_prefix_suffix_differences',[('nums','list[int]')],'list[int]',['arrays','hash maps','prefix sums'],
 ['For each index i, count distinct values in nums[0:i+1] and in nums[i+1:n].','Set answer[i] to prefix_distinct minus suffix_distinct.','Return all differences from left to right; the suffix after the final index is empty.'],
 [([[1,2,3,4,5]],'Prefix distinct counts one through five minus suffix counts four through zero give -3, -1, 1, 3, and 5.'),([[3,2,3,4,2]],'Repeated values affect only first appearances within each prefix or suffix set.')],
 [[a] for a in [[1],[1,1],[1,2],[2,1],[1,2,3],[1,1,2],[1,2,1],[3,2,3,4,2],[5,4,3,2,1],[0,0,0,0],[-1,0,-1,1],[1,2,2,3,3,1],[4,1,4,2,4,3],[1,2,1,3,2,4,1]]],
 DISTINCT,[DISTINCT.replace('len(seen)-suffix[index+1]','suffix[index+1]-len(seen)'),DISTINCT.replace('suffix[index+1]','suffix[index]')],
 ['Subtracts prefix distinct count from suffix distinct count in the wrong order.','Includes nums[i] in both the prefix and suffix counts.'],distinct_oracle,random_distinct,
 ['Precompute the number of distinct values in every suffix, including the empty suffix.','Scan left to right with a set of values seen in the prefix.','After inserting nums[i], subtract suffix_distinct[i+1] from the prefix set size.','The two maintained counts exactly describe the disjoint index ranges required at every position.'],'O(n)','O(n)',3),
}

BATCH[2659]['sample_contract_adapter']={
    'source_sample':'Input nums = [3,4,-1] → Output 5 Operation Array 1 [4, -1, 3] 2 [-1, 3, 4] 3 [3, 4] 4 [4] 5 [].',
    'arguments':[[3,4,-1]],
    'expected':5,
    'reason':'The workbook appends the operation trace to the output literal; this adapter preserves its input and stated result while separating that explanatory trace.',
}
