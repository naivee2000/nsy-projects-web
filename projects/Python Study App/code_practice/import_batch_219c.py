"""Digit swaps, attack scheduling, streaming ranks, interval spacing, and safe grids."""
from functools import cmp_to_key
from itertools import permutations, product
from collections import deque
from .import_batch_055 import entry

def one_swaps(value):
    chars=list(str(value));values={value}
    for i in range(len(chars)):
        for j in range(i+1,len(chars)):
            copy=chars[:];copy[i],copy[j]=copy[j],copy[i];values.add(int(''.join(copy)))
    return values
def almost_oracle(args):
    nums=args[0];return sum(nums[j] in one_swaps(nums[i]) or nums[i] in one_swaps(nums[j]) for i in range(len(nums)) for j in range(i+1,len(nums)))
def random_almost(rng):return [[rng.randint(1,9999) for _ in range(rng.randint(2,12))]]

def damage_oracle(args):
    power,damage,health=args;times=[(value+power-1)//power for value in health];best=10**30
    for order in permutations(range(len(damage))):
        elapsed=total=0
        for enemy in order:elapsed+=times[enemy];total+=elapsed*damage[enemy]
        best=min(best,total)
    return best
def random_damage(rng):
    n=rng.randint(1,7);return [rng.randint(1,8),[rng.randint(1,15) for _ in range(n)],[rng.randint(1,20) for _ in range(n)]]

def nearest_oracle(args):
    queries,k=args;distances=[];answer=[]
    for x,y in queries:
        distances.append(abs(x)+abs(y));answer.append(sorted(distances)[k-1] if len(distances)>=k else -1)
    return answer
def random_nearest(rng):
    size=rng.randint(1,20);points=set()
    while len(points)<size:points.add((rng.randint(-20,20),rng.randint(-20,20)))
    return [[list(p) for p in points],rng.randint(1,25)]

def spacing_oracle(args):
    start,d=args;best=0
    for values in product(*(range(value,value+d+1) for value in start)):
        ordered=sorted(values);best=max(best,min(b-a for a,b in zip(ordered,ordered[1:])))
    return best
def random_spacing(rng):
    n=rng.randint(2,6);return [[rng.randint(0,15) for _ in range(n)],rng.randint(0,4)]

def safe_oracle(args):
    grid,health=args;m=len(grid);n=len(grid[0]);remaining=health-grid[0][0]
    if remaining<=0:return False
    queue=deque([(0,0,remaining)]);seen={(0,0,remaining)}
    while queue:
        r,c,left=queue.popleft()
        if (r,c)==(m-1,n-1):return True
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=r+dr,c+dc
            if 0<=nr<m and 0<=nc<n and left-grid[nr][nc]>0:
                state=(nr,nc,left-grid[nr][nc])
                if state not in seen:seen.add(state);queue.append(state)
    return False
def random_safe(rng):
    m=rng.randint(1,5);n=rng.randint(1,5)
    if m*n<2:n=2
    return [[[rng.randrange(2) for _ in range(n)] for _ in range(m)],rng.randint(1,m+n)]

ALMOST='''def count_one_digit_swap_pairs(nums):
    def variants(value):
        digits=list(str(value));result={value}
        for left in range(len(digits)):
            for right in range(left+1,len(digits)):
                copy=digits[:];copy[left],copy[right]=copy[right],copy[left]
                result.add(int(''.join(copy)))
        return result
    choices=[variants(value) for value in nums];answer=0
    for left in range(len(nums)):
        for right in range(left+1,len(nums)):
            answer+=nums[right] in choices[left] or nums[left] in choices[right]
    return answer
'''
DAMAGE='''def minimum_enemy_damage(power,damage,health):
    from functools import cmp_to_key
    enemies=[((hp+power-1)//power,hurt) for hp,hurt in zip(health,damage)]
    def compare(first,second):
        return first[0]*second[1]-second[0]*first[1]
    enemies.sort(key=cmp_to_key(compare));remaining=sum(damage);answer=0
    for seconds,hurt in enemies:
        answer+=remaining*seconds;remaining-=hurt
    return answer
'''
NEAREST='''def kth_nearest_obstacle_distances(queries,k):
    import heapq
    nearest=[];answer=[]
    for x,y in queries:
        heapq.heappush(nearest,-(abs(x)+abs(y)))
        if len(nearest)>k:heapq.heappop(nearest)
        answer.append(-nearest[0] if len(nearest)==k else -1)
    return answer
'''
SPACING='''def maximum_interval_choice_spacing(start,d):
    intervals=sorted(start)
    def possible(gap):
        chosen=intervals[0]
        for left in intervals[1:]:
            chosen=max(left,chosen+gap)
            if chosen>left+d:return False
        return True
    low=0;high=intervals[-1]+d-intervals[0]
    while low<high:
        middle=(low+high+1)//2
        if possible(middle):low=middle
        else:high=middle-1
    return low
'''
SAFE='''def has_positive_health_path(grid,health):
    import heapq
    m=len(grid);n=len(grid[0]);cost=[[10**9]*n for _ in range(m)];cost[0][0]=grid[0][0]
    heap=[(grid[0][0],0,0)]
    while heap:
        lost,row,column=heapq.heappop(heap)
        if lost!=cost[row][column]:continue
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=row+dr,column+dc
            if 0<=nr<m and 0<=nc<n and lost+grid[nr][nc]<cost[nr][nc]:
                cost[nr][nc]=lost+grid[nr][nc];heapq.heappush(heap,(cost[nr][nc],nr,nc))
    return cost[-1][-1]<health
'''
def lesson(a,b,c,d):return [a,b,c,d]

BATCH={
3265:entry('count_one_digit_swap_pairs',[('nums','list[int]')],'int',['enumeration','strings','hash maps'],['2≤len(nums)≤100 and values are positive integers up to 1,000,000.','A pair is almost equal if swapping at most two digit positions in either one number makes their integer values equal.','Leading zeros after a swap are allowed; count index pairs i<j.'],[([[3,12,30,17,21]],'The valid pairs are 3 with 30, and 12 with 21.'),([[1,1,1,1,1]],'All ten index pairs already have equal values.')],[[a] for a in [[123,231],[12,21],[3,30],[10,1],[100,1],[12,12],[13,31,103],[102,201],[100,10,1],[123,321,213],[11,11,11],[98,89,809],[120,102,210],[5,50,500]]],ALMOST,[ALMOST.replace("result={value}","result=set()"),ALMOST.replace('or nums[left] in choices[right]','and nums[left] in choices[right]')],['Requires a swap and misses pairs that are already equal.','Incorrectly requires both numbers to reach one another with separate swaps.'],almost_oracle,random_almost,lesson('Each number has only O(d²) values reachable by zero or one digit swap.','Generate that small set for every number, then test whether either endpoint reaches the other.','Parse swapped strings as integers so a leading zero naturally disappears; count each i<j once.','The allowed operation changes exactly one endpoint, so membership in either reachability set is necessary and sufficient.'),'O(n²d²)','O(nd²)',5),
3273:entry('minimum_enemy_damage',[('power','int'),('damage','list[int]'),('health','list[int]')],'int',['greedy','sorting'],['power is positive; damage and health are equal-length positive arrays with at most 100,000 enemies.','All living enemies deal damage before each attack; enemy i needs ceil(health[i]/power) attacks.','Choose the attack order minimizing all damage received before every enemy dies.'],[([4,[1,2,3,4],[4,5,6,8]],'Defeating enemies in order 3,2,0,1 yields total damage 39.'),([1,[1,1,1,1],[1,2,3,4]],'With equal damage rates, shortest required attack times first gives total 20.')],[[p,d,h] for p,d,h in [(8,[40],[59]),(1,[1],[1]),(5,[3,8],[10,5]),(2,[1,9],[10,2]),(3,[4,4],[7,8]),(4,[5,1,3],[8,4,6]),(10,[2,7,1],[9,11,20]),(1,[3,2,1],[1,2,3]),(6,[9,2,8],[12,18,6]),(4,[1,1,10],[8,4,12]),(7,[5,6,7,8],[1,8,15,22]),(3,[2,9,4],[20,5,11]),(5,[10,1,10],[6,30,7]),(2,[4,3,8,1],[5,6,7,8])]],DAMAGE,[DAMAGE.replace('first[0]*second[1]-second[0]*first[1]','second[0]*first[1]-first[0]*second[1]'),DAMAGE.replace('(hp+power-1)//power','hp//power')],['Sorts by the reverse exchange priority.','Uses floor division and undercounts attacks for partial final hits.'],damage_oracle,random_damage,lesson('Enemy i is a job of duration ceil(health/power) whose damage rate persists until completion.','Use the pairwise exchange rule: i precedes j when time_i*damage_j < time_j*damage_i.','Sort with exact cross multiplication, then add current total living damage for every attack second.','Swapping an inverted adjacent pair decreases total damage by the cross-product difference, so the sorted order is globally optimal.'),'O(n log n)','O(n)',8),
3275:entry('kth_nearest_obstacle_distances',[('queries','list[list[int]]'),('k','int')],'list[int]',['heaps','streaming'],['queries are distinct integer coordinates and k is positive.','After inserting each obstacle, rank all Manhattan distances |x|+|y|.','Return the kth-smallest distance, or -1 while fewer than k obstacles exist.'],[([[[1,2],[3,4],[2,3],[-3,0]],2],'The kth distances after insertion are unavailable, then 7, 5, and 3.'),([[[5,5],[4,4],[3,3]],1],'The nearest distance decreases from 10 to 8 to 6.')],[[q,k] for q,k in [([[0,0]],1),([[1,1]],2),([[1,0],[0,1]],1),([[1,0],[0,1]],2),([[-1,-2],[2,2],[0,5]],2),([[10,0],[1,1],[3,0]],1),([[10,0],[1,1],[3,0]],3),([[2,2],[-2,-2],[1,3]],2),([[5,5],[4,4],[3,3]],2),([[0,4],[0,3],[0,2],[0,1]],3),([[-5,0],[0,-1],[2,2]],2),([[7,8],[-1,-1],[3,4],[0,9]],2),([[1,2],[2,1],[-1,-2]],2),([[100,100],[1,0],[-2,0]],5)]],NEAREST,[NEAREST.replace('if len(nearest)>k','if len(nearest)>=k'),NEAREST.replace('-(abs(x)+abs(y))','abs(x)+abs(y)')],['Keeps only k-1 distances.','Uses a min-heap sign, discarding near obstacles instead of far ones.'],nearest_oracle,random_nearest,lesson('Only the k smallest distances can affect the kth-smallest value.','Maintain those distances in a size-k max-heap represented by negatives.','Push each distance; when size exceeds k, remove the largest retained distance.','Discarded distances are at least as large as every retained candidate, so the heap maximum is exactly rank k.'),'O(q log k)','O(k)',5),
3281:entry('maximum_interval_choice_spacing',[('start','list[int]'),('d','int')],'int',['binary search','greedy','sorting'],['start contains 2–100,000 interval starts; every selectable interval is [start[i],start[i]+d].','Choose one integer from every interval and score the minimum absolute difference among choices.','Return the maximum achievable score.'],[([[6,0,3],2],'Choosing 8,0,4 in the corresponding intervals gives minimum separation four.'),([[2,6,13,13],5],'Choices 2,7,13,18 achieve minimum separation five.')],[[s,d] for s,d in [([0,1],0),([0,1],1),([0,0],0),([0,0],5),([0,5],2),([1,2,3],0),([0,2,4],1),([5,0,10],3),([2,2,2],4),([1,4,7,10],2),([10,0,5],5),([3,8,8],2),([0,10,20,30],0),([4,1,9,2],3)]],SPACING,[SPACING.replace('chosen=max(left,chosen+gap)','chosen=chosen+gap'),SPACING.replace('chosen>left+d','chosen>=left+d')],['Forces every choice to follow the prior one even when the interval begins later.','Rejects a choice equal to the inclusive right endpoint.'],spacing_oracle,random_spacing,lesson('If a gap is feasible, every smaller gap is feasible, enabling binary search.','Sort intervals and greedily choose each value as early as possible while respecting the candidate gap.','Set chosen=max(interval start, previous+gap); fail if it exceeds start+d.','The earliest feasible choice leaves maximal room for all later intervals, so greedy feasibility is exact and monotone.'),'O(n log n+n log range)','O(n)',7),
3286:entry('has_positive_health_path',[('grid','list[list[int]]'),('health','int')],'bool',['graphs','matrices','shortest paths'],['grid is a nonempty binary matrix with at least two and at most 2,500 cells.','Start at the upper-left and move in four directions; each unsafe 1 cell entered, including the start, costs one health.','Return whether the lower-right is reachable while final health remains at least one.'],[([[[0,1,0,0,0],[0,1,0,1,0],[0,0,0,1,0]],1],'A path of only safe zero cells reaches the destination without losing health.'),([[[0,1,1,0,0,0],[1,0,1,0,0,0],[0,1,1,1,0,1],[0,0,1,0,1,0]],3],'Every path costs at least three health, leaving zero, so the result is false.')],[[g,h] for g,h in [([[0,0]],1),([[1,0]],1),([[1,0]],2),([[0],[1]],2),([[0,1],[0,0]],1),([[0,1],[1,0]],2),([[1,1],[1,1]],4),([[1,1],[1,1]],3),([[0,1,0],[0,1,0]],1),([[1,0,1],[1,0,1]],2),([[0,1,1],[0,0,1],[1,0,0]],1),([[1,1,1],[1,0,1],[1,1,1]],5),([[0,0,1],[1,0,1],[1,0,0]],1),([[1,0,0],[1,1,0]],2)]],SAFE,[SAFE.replace('cost[0][0]=grid[0][0]','cost[0][0]=0'),SAFE.replace('cost[-1][-1]<health','cost[-1][-1]<=health')],['Does not charge an unsafe starting cell.','Allows health to fall to zero at the destination.'],safe_oracle,random_safe,lesson('Maximizing remaining health is equivalent to minimizing the number of unsafe cells visited.','Run Dijkstra on the grid with cell values as entry costs.','Initialize with the starting-cell cost, relax four-neighbor costs, and require minimum loss < health.','All weights are nonnegative, so Dijkstra finds minimum loss; positive final health is exactly the strict inequality.'),'O(mn log(mn))','O(mn)',6),
}
