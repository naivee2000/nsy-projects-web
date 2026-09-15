"""Equal-value jumps, exam seating, event scheduling, reverse construction, and divisors."""
from collections import deque
from functools import lru_cache
from math import gcd,isqrt

from .import_batch_055 import entry


def jump_oracle(args):
    values=args[0];queue=deque([(0,0)]);seen={0}
    while queue:
        index,distance=queue.popleft()
        if index==len(values)-1:return distance
        for target in range(len(values)):
            if (abs(target-index)==1 or values[target]==values[index]) and target not in seen:
                seen.add(target);queue.append((target,distance+1))
def random_jump(rng):return [[rng.randint(-4,4) for _ in range(rng.randint(1,14))]]


def students_oracle(args):
    seats=args[0];positions=[(r,c) for r,row in enumerate(seats) for c,value in enumerate(row) if value=='.'];best=0
    for mask in range(1<<len(positions)):
        if mask.bit_count()<=best:continue
        chosen={positions[i] for i in range(len(positions)) if mask>>i&1}
        if all((r,c-1) not in chosen and (r-1,c-1) not in chosen and (r-1,c+1) not in chosen for r,c in chosen):best=mask.bit_count()
    return best
def random_students(rng):
    rows,columns=rng.randint(1,4),rng.randint(1,4)
    return [[''.join(rng.choice('.#') for _ in range(columns)) for _ in range(rows)]]


def events_oracle(args):
    events=args[0];last=max(end for _,end in events)
    @lru_cache(None)
    def visit(day,used):
        if day>last:return 0
        answer=visit(day+1,used)
        for index,(start,end) in enumerate(events):
            if not used>>index&1 and start<=day<=end:answer=max(answer,1+visit(day+1,used|1<<index))
        return answer
    return visit(1,0)
def random_events(rng):
    events=[]
    for _ in range(rng.randint(1,9)):
        start=rng.randint(1,8);events.append([start,rng.randint(start,10)])
    return [events]


def possible_oracle(args):
    target=tuple(args[0])
    if len(target)==1:return target==(1,)
    start=(1,)*len(target);queue=deque([start]);seen={start}
    while queue:
        state=queue.popleft()
        if state==target:return True
        total=sum(state)
        for index in range(len(state)):
            if total<=target[index]:
                nxt=state[:index]+(total,)+state[index+1:]
                if all(a<=b for a,b in zip(nxt,target)) and nxt not in seen:seen.add(nxt);queue.append(nxt)
    return False
def random_possible(rng):
    size=rng.randint(1,3)
    if rng.random()<.55:
        state=[1]*size
        for _ in range(rng.randint(0,5)):
            index=rng.randrange(size);state[index]=sum(state)
            if max(state)>30:break
        return [state]
    return [[rng.randint(1,10) for _ in range(size)]]


def divisor_oracle(args):
    number=args[0];pairs=[]
    for value in (number+1,number+2):
        pairs.extend(([factor,value//factor] for factor in range(1,value+1) if value%factor==0))
    return min(pairs,key=lambda pair:(abs(pair[0]-pair[1]),pair))
def random_divisor(rng):return [rng.randint(1,1_000_000)]


JUMP='''def minimum_equal_value_jumps(arr):
    from collections import defaultdict,deque
    positions=defaultdict(list)
    for index,value in enumerate(arr):positions[value].append(index)
    queue=deque([(0,0)]);seen={0}
    while queue:
        index,distance=queue.popleft()
        if index==len(arr)-1:return distance
        for target in positions.pop(arr[index],[])+[index-1,index+1]:
            if 0<=target<len(arr) and target not in seen:seen.add(target);queue.append((target,distance+1))
'''
STUDENTS='''def maximum_exam_students(seats):
    columns=len(seats[0]);previous={0:0}
    for row in seats:
        usable=sum((value=='.')<<column for column,value in enumerate(row));current={}
        for mask in range(1<<columns):
            if mask&~usable or mask&(mask<<1):continue
            for before,total in previous.items():
                if mask&(before<<1) or mask&(before>>1):continue
                current[mask]=max(current.get(mask,0),total+mask.bit_count())
        previous=current
    return max(previous.values())
'''
EVENTS='''def maximum_attended_events(events):
    import heapq
    events=sorted(events);heap=[];index=answer=0;day=events[0][0]
    while index<len(events) or heap:
        if not heap and day<events[index][0]:day=events[index][0]
        while index<len(events) and events[index][0]<=day:heapq.heappush(heap,events[index][1]);index+=1
        while heap and heap[0]<day:heapq.heappop(heap)
        if heap:heapq.heappop(heap);answer+=1;day+=1
    return answer
'''
POSSIBLE='''def can_construct_target_array(target):
    import heapq
    if len(target)==1:return target[0]==1
    total=sum(target);heap=[-value for value in target];heapq.heapify(heap)
    while True:
        maximum=-heapq.heappop(heap);rest=total-maximum
        if maximum==1 or rest==1:return True
        if rest==0 or maximum<=rest or maximum%rest==0:return False
        previous=maximum%rest;total=rest+previous;heapq.heappush(heap,-previous)
'''
PARITY='''def can_construct_target_array(target):
    return all(value%2==1 for value in target)
'''
COMMON='''def can_construct_target_array(target):
    from functools import reduce
    from math import gcd
    return reduce(gcd,target)==1
'''
DIVISORS='''def closest_factor_pair(num):
    best=None
    for value in (num+1,num+2):
        factor=int(value**0.5)
        while value%factor:factor-=1
        pair=[factor,value//factor]
        if best is None or pair[1]-pair[0]<best[1]-best[0]:best=pair
    return best
'''

EVENT_CASES = (
    [[1,1]], [[1,2],[2,3],[3,4]], [[1,2],[1,2],[3,3],[1,5],[1,5]],
    [[1,1],[1,1]], [[1,10],[2,2]], [[2,2]], [[1,2],[1,2],[1,2]],
    [[3,4],[1,1],[2,2]], [[1,3],[2,2],[3,3]], [[5,5],[1,10]],
    [[1,4],[4,4],[2,2]], [[2,5],[1,2],[3,3]], [[1,100],[100,100]],
    [[1,1],[2,2],[2,3],[3,3]],
)

SEAT_SAMPLE = ['#.##.#', '.####.', '#.##.#']
SEAT_CASES = (
    ['.'], ['#'], ['..'], ['.#.'], ['.#', '#.'], ['.', '.'],
    ['..', '..'], ['#.', '.#'], SEAT_SAMPLE, ['...', '...'],
    ['.#.', '...', '.#.'], ['####', '....'], ['.#.#', '#.#.'],
    ['....', '####', '....'],
)

BATCH={
1345:entry('minimum_equal_value_jumps',[('arr','list[int]')],'int',['arrays','breadth-first search','hash maps'],['Start at index zero and target the final index.','One move goes to an adjacent index or any other index containing the same value.','Return the minimum number of moves; the one-element array requires zero.'],[([[100,-23,-23,404,100,23,23,23,3,404]],'Jump from zero to equal value at four, step to three, then jump to the final equal 404 in three moves.'),([[7]],'The starting index is already the last index.')],[[x] for x in ([1,2],[1,1],[7],[100,-23,-23,404,100,23,23,23,3,404],[7,6,9,6,9,6,9,7],[6,1,9],[1,2,3,4],[1,2,1,2,1],[0,0,0,0],[1,2,3,1,4,3,5],[5,4,3,2,1],[1,-1,1,-1,2],[9,8,7,9,6,5,9],[2,3,4,5,2])],JUMP,[JUMP.replace('positions.pop(arr[index],[])','[]'),JUMP.replace('+[index-1,index+1]','+[]')],['Ignores equal-value teleport jumps and walks only between neighbors.','Uses equal-value jumps but omits adjacent moves.'],jump_oracle,random_jump,['Group all indices by value before searching.','Breadth-first search indices from zero using adjacent and equal-value neighbors.','After expanding one value group, remove it so the same large group is never scanned again.','BFS guarantees the first arrival at the last index is shortest, and clearing a group is safe after its earliest expansion.'],'Build a value-to-indices map, then BFS over indices. Adjacent edges and all equal-value edges each cost one. Once the first index of a value is expanded, all positions in that value group receive their earliest possible offers, so deleting the group prevents quadratic rescans. The oracle retains every group and scans all indices on short inputs.','O(n)','O(n)',8),
1349:entry('maximum_exam_students',[('seats','list[str]')],'int',['matrices','bitmask dynamic programming'],['A dot is usable and a hash is broken.','Students cannot occupy horizontally adjacent seats or diagonally adjacent seats in consecutive rows; vertical adjacency is allowed.','Return the greatest number of students that can be seated.'],[([SEAT_SAMPLE],'Four usable seats can be chosen without a forbidden horizontal or diagonal pair.'),([['.#','#.']],'The two usable seats are diagonally adjacent, so only one student can sit.')],[[seats] for seats in SEAT_CASES],STUDENTS,[STUDENTS.replace(' or mask&(mask<<1)',''),STUDENTS.replace('if mask&(before<<1) or mask&(before>>1):continue','if False:continue')],['Allows horizontally adjacent students in the same row.','Ignores diagonal cheating between consecutive rows.'],students_oracle,random_students,['Represent occupied seats in each row as a bitmask.','Enumerate submasks of usable seats that contain no adjacent bits.','Combine a row mask with prior masks only when neither diagonal shift intersects.','Every legal layout has one legal mask per row, and the DP maximizes over every compatible sequence.'],'For each row, enumerate masks contained in its usable-seat mask and reject horizontal adjacency. Dynamic programming combines each legal mask with compatible previous-row masks by testing both diagonal shifts. The oracle independently enumerates every subset of usable positions on seeded boards and checks forbidden coordinate pairs directly.','O(rows*4^columns)','O(2^columns)',8),
1353:entry('maximum_attended_events',[('events','list[list[int]]')],'int',['greedy','sorting','heaps'],['Each event may be attended on one integer day from its inclusive start through end.','Attend at most one event per day and each event at most once.','Return the maximum number of events that can be attended.'],[([[[1,2],[2,3],[3,4]]],'Attend one event on each of days one, two, and three.'),([[[1,2],[1,2],[3,3],[1,5],[1,5]]],'An earliest-ending choice each day permits attending all five events.')],[[events] for events in EVENT_CASES],EVENTS,[EVENTS.replace('heapq.heappop(heap);answer+=1','heapq.heappop(heap);heapq.heappop(heap) if heap else None;answer+=1'),EVENTS.replace('heapq.heappush(heap,events[index][1])','heapq.heappush(heap,-events[index][1])').replace('heap[0]<day','-heap[0]<day')],['Discards a second available event each attended day.','Prioritizes the latest-ending available event rather than the earliest-ending one.'],events_oracle,random_events,['Sort events by start day and keep active end days in a min-heap.','On each day, add newly started events and discard expired ones.','Attend the active event ending soonest; jump directly to the next start when the heap is empty.','Replacing any later-ending daily choice with the earliest-ending event cannot reduce future options.'],'Sweep days while adding events whose starts have arrived. Expired ends leave the min-heap, and selecting the smallest end preserves maximum room for later events. Empty periods are skipped. The oracle independently explores every event/day assignment with memoized used-event masks on short inputs.','O(n log n)','O(n)',5),
1354:entry('can_construct_target_array',[('target','list[int]')],'bool',['arrays','heaps','greedy'],['Begin with an array of ones.','A move replaces one element by the current total sum while leaving all others unchanged.','Return whether the positive target array can be constructed.'],[([[9,3,5]],'Reversing the largest values recovers [1,1,1], so the target is constructible.'),([[1,1,1,2]],'No forward replacement from all ones can create this target.')],[[x] for x in ([1],[2],[1,1],[1,2],[2,2],[9,3,5],[1,1,1,2],[8,5],[5,3],[3,1],[7,1,1],[4,1,1],[2,1,1],[13,5,1])],POSSIBLE,[PARITY,COMMON],['Assumes every target component must be odd, which is neither necessary nor sufficient.','Treats greatest common divisor one as sufficient and ignores the required replacement sequence.'],possible_oracle,random_possible,['Reverse the last move, which must have created the current largest value.','The other values sum to rest; the prior largest value is maximum modulo rest after skipping repeated reverse subtractions.','Use a max-heap, and handle rest equal to one as immediately reachable.','The largest value uniquely identifies the last changed position, so each reverse step is necessary and preserves equivalence.'],'Reverse the operation: if maximum was last replaced, its previous value differs by a positive multiple of the sum of all other entries. Modulo performs all repeated subtractions at once. Reject nonpositive predecessors and accept when all values reduce to one or the remainder sum is one. The oracle independently explores every bounded forward state on seeded small targets.','O(iterations*log n)','O(n)',8),
1362:entry('closest_factor_pair',[('num','int')],'list[int]',['math','factorization'],['Choose two positive integers whose product is num+1 or num+2.','Minimize their absolute difference; return the pair in either order.','num is between one and one billion.'],[([8],'Nine factors as three times three, the closest possible pair.'),([123],'One hundred twenty-five factors as five times twenty-five, closer than either factorization of one hundred twenty-four.')],[[n] for n in (1,2,3,4,5,8,10,15,20,31,99,123,999,10000)],DIVISORS,[DIVISORS.replace('for value in (num+1,num+2)','for value in (num+1,)'),DIVISORS.replace('factor=int(value**0.5)','factor=max(1,int(num**0.5))')],['Checks factorizations of num+1 only and ignores num+2.','Starts divisor search from the square root of num rather than each candidate product.'],divisor_oracle,random_divisor,['The closest factor pair straddles the square root of its product.','For each of num+1 and num+2, search downward from its integer square root for the first divisor.','Compare the differences of the two resulting pairs and return the smaller.', 'The first divisor found below the square root maximizes the smaller factor and therefore minimizes the pair gap.'],'Search downward from floor(sqrt(value)) until a divisor is found for each candidate product. These are their respective closest factor pairs, so compare the two gaps. The oracle independently enumerates every divisor of both candidate values on seeded inputs.','O(sqrt(num))','O(1)',5),
}
BATCH[1362]['comparator']='unordered'
BATCH[1349]['sample_contract_adapter']={
    'source_sample':'Input seats = [["#",".","#","#",".","#"], [".","#","#","#","#","."], ["#",".","#","#",".","#"]] → Output 4.',
    'arguments':[['#.##.#','.####.','#.##.#']],
    'expected':4,
    'reason':'The workbook serializes each row as a character list; the Python callable receives the equivalent row strings.',
}
