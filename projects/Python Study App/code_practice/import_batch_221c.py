"""Alphabet matrix powers, parity runs, timed grids, and balanced digit permutations."""
from collections import Counter
from functools import lru_cache
from itertools import permutations,product
from math import comb
from .import_batch_055 import entry


MOD=1_000_000_007


def transform_oracle(args):
    text,t,steps=args
    for _ in range(t):
        text=''.join(''.join(chr(97+(ord(char)-97+j)%26) for j in range(1,steps[ord(char)-97]+1)) for char in text)
    return len(text)%MOD


def random_transform(rng):
    steps=[rng.randint(1,3) for _ in range(26)]
    return [''.join(rng.choice('awxyz') for _ in range(rng.randint(1,7))),rng.randint(1,3),steps]


def even_oracle(args):
    n,m,k=args;answer=0
    for values in product(range(1,m+1),repeat=n):
        answer+=sum(values[i]%2==0 and values[i+1]%2==0 for i in range(n-1))==k
    return answer%MOD


def random_even(rng):
    n=rng.randint(1,7);m=rng.randint(1,5)
    return [n,m,rng.randint(0,n-1)]


def grid_oracle(args,alternating=False):
    rooms=args[0];rows=len(rooms);cols=len(rooms[0]);infinity=10**30
    distance=[[infinity]*cols for _ in range(rows)];distance[0][0]=0
    for _ in range(rows*cols):
        changed=False
        for row in range(rows):
            for col in range(cols):
                if distance[row][col]==infinity:continue
                cost=(row+col)%2+1 if alternating else 1
                for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr,nc=row+dr,col+dc
                    if 0<=nr<rows and 0<=nc<cols:
                        value=max(distance[row][col],rooms[nr][nc])+cost
                        if value<distance[nr][nc]:distance[nr][nc]=value;changed=True
        if not changed:break
    return distance[-1][-1]


def grid_one_oracle(args):return grid_oracle(args)
def grid_two_oracle(args):return grid_oracle(args,True)


def random_grid(rng):
    rows=rng.randint(2,4);cols=rng.randint(2,4)
    return [[[rng.randint(0,15) for _ in range(cols)] for _ in range(rows)]]


def balanced_oracle(args):
    num=args[0];seen=set(permutations(num));answer=0
    for digits in seen:
        answer+=sum(map(int,digits[::2]))==sum(map(int,digits[1::2]))
    return answer%MOD


def random_balanced(rng):return [''.join(str(rng.randint(0,5)) for _ in range(rng.randint(2,7)))]


TRANSFORM='''def generalized_transformed_length(s,t,nums):
    modulo=1000000007;size=26
    matrix=[[0]*size for _ in range(size)]
    for letter,steps in enumerate(nums):
        for step in range(1,steps+1):matrix[letter][(letter+step)%size]=1
    def multiply(left,right):
        result=[[0]*size for _ in range(size)]
        for row in range(size):
            for middle in range(size):
                if left[row][middle]:
                    for column in range(size):result[row][column]=(result[row][column]+left[row][middle]*right[middle][column])%modulo
        return result
    power=[[int(row==column) for column in range(size)] for row in range(size)]
    while t:
        if t&1:power=multiply(power,matrix)
        matrix=multiply(matrix,matrix);t//=2
    counts=[0]*size
    for char in s:counts[ord(char)-97]+=1
    return sum(counts[row]*sum(power[row]) for row in range(size))%modulo
'''

EVEN='''def count_k_even_arrays(n,m,k):
    modulo=1000000007;even=m//2;odd=m-even
    previous=[[0,0] for _ in range(k+1)];previous[0]=[odd,even]
    for _ in range(1,n):
        current=[[0,0] for _ in range(k+1)]
        for used in range(k+1):
            current[used][0]=(current[used][0]+sum(previous[used])*odd)%modulo
            current[used][1]=(current[used][1]+previous[used][0]*even)%modulo
            if used:current[used][1]=(current[used][1]+previous[used-1][1]*even)%modulo
        previous=current
    return sum(previous[k])%modulo
'''

GRID_ONE='''def minimum_room_time(move_time):
    import heapq
    rows=len(move_time);cols=len(move_time[0]);distance=[[float('inf')]*cols for _ in range(rows)]
    distance[0][0]=0;heap=[(0,0,0)]
    while heap:
        elapsed,row,col=heapq.heappop(heap)
        if elapsed!=distance[row][col]:continue
        if row==rows-1 and col==cols-1:return elapsed
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=row+dr,col+dc
            if 0<=nr<rows and 0<=nc<cols:
                arrival=max(elapsed,move_time[nr][nc])+1
                if arrival<distance[nr][nc]:distance[nr][nc]=arrival;heapq.heappush(heap,(arrival,nr,nc))
'''

GRID_TWO='''def minimum_alternating_room_time(move_time):
    import heapq
    rows=len(move_time);cols=len(move_time[0]);distance=[[float('inf')]*cols for _ in range(rows)]
    distance[0][0]=0;heap=[(0,0,0)]
    while heap:
        elapsed,row,col=heapq.heappop(heap)
        if elapsed!=distance[row][col]:continue
        if row==rows-1 and col==cols-1:return elapsed
        cost=(row+col)%2+1
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=row+dr,col+dc
            if 0<=nr<rows and 0<=nc<cols:
                arrival=max(elapsed,move_time[nr][nc])+cost
                if arrival<distance[nr][nc]:distance[nr][nc]=arrival;heapq.heappush(heap,(arrival,nr,nc))
'''

BALANCED='''def count_balanced_digit_permutations(num):
    from collections import Counter
    from functools import lru_cache
    from math import comb
    modulo=1000000007;counts=Counter(map(int,num));total=sum(map(int,num))
    if total%2:return 0
    @lru_cache(None)
    def search(digit,target,left_slots,right_slots):
        if digit==10:return int(target==0 and left_slots==0 and right_slots==0)
        answer=0
        for take_left in range(min(counts[digit],left_slots)+1):
            take_right=counts[digit]-take_left
            if take_right<=right_slots and take_left*digit<=target:
                ways=comb(left_slots,take_left)*comb(right_slots,take_right)
                answer=(answer+ways*search(digit+1,target-take_left*digit,left_slots-take_left,right_slots-take_right))%modulo
        return answer
    return search(0,total//2,len(num)//2,(len(num)+1)//2)
'''


def lesson(a,b,c,d):return [a,b,c,d]


ONES=[1]*26;TWOS=[2]*26
TRANSFORM_CASES=[[s,t,v] for s,t,v in [('a',1,ONES),('z',1,ONES),('z',1,TWOS),('y',1,[3]*26),('az',2,ONES),('abc',2,TWOS),('xyz',3,ONES),('hello',1,[3]*26),('wrap',2,[1+(i%3) for i in range(26)]),('zzz',3,[2]*26),('algorithm',2,[1+(i%2) for i in range(26)]),('a',4,[2]*26),('mnop',3,[1+(i%4) for i in range(26)]),('code',2,[3-(i%2) for i in range(26)])]]
EVEN_CASES=[[n,m,k] for n,m,k in [(1,1,0),(1,4,0),(2,1,0),(2,2,0),(2,2,1),(3,2,0),(3,2,1),(3,3,2),(4,3,1),(4,4,2),(5,2,3),(5,3,0),(6,2,5),(7,3,4)]]
GRID_CASES=[[[[0,a],[b,c]]] for a,b,c in [(0,0,0),(1,1,2),(5,0,0),(0,5,0),(10,1,2),(2,9,3),(4,4,5)]]+[[grid] for grid in [[[0,0,1],[0,0,0]],[[0,5,1],[2,8,0]],[[0,1],[2,3],[4,0]],[[0,9,0],[1,1,1],[8,2,0]],[[0,3,6],[2,5,1]],[[0,100],[1,0],[1,0]],[[0,2,4],[3,1,5],[7,2,0]]]]
BALANCED_CASES=[[value] for value in ['11','12','00','101','1234','1122','0000','12345','112233','0123','999999','121212','1001','012345']]


BATCH={
3337:entry('generalized_transformed_length',[('s','str'),('t','int'),('nums','list[int]')],'int',['strings','matrix exponentiation','dynamic programming'],['s has 1–100,000 lowercase letters, t is 1..1,000,000,000, and nums has 26 values in 1..25.','Letter i becomes the next nums[i] alphabet letters, wrapping after z.','Return the length after exactly t simultaneous transformations modulo 1,000,000,007.'],[(['abcyy',2,[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2]],'The first step forms bcdzz and the second forms cdeabab, of length seven.'),(['azbk',1,TWOS],'Each of four letters produces two successors, including z wrapping to ab, so the length is eight.')],TRANSFORM_CASES,TRANSFORM,[TRANSFORM.replace('(letter+step)%size','(letter+step+1)%size'),TRANSFORM.replace('range(1,steps+1)','range(steps)')],['Starts each replacement one letter too far ahead.','Includes the current letter and omits the final required successor.'],transform_oracle,random_transform,lesson('One transformation is a fixed 26-by-26 linear map of letter counts.','Exponentiate that transition matrix instead of applying up to one billion steps.','Build wrapped successor entries, binary-power the matrix, and multiply initial counts by the result.','Matrix composition exactly represents consecutive independent transformations; binary exponentiation reduces t steps to logarithmically many products.'),'O(26³ log t+len(s))','O(26²)',8),
3339:entry('count_k_even_arrays',[('n','int'),('m','int'),('k','int')],'int',['dynamic programming','parity'],['n is 1–750, m is 1–1,000, and 0 <= k < n.','An adjacent index qualifies exactly when arr[i]*arr[i+1]-arr[i]-arr[i+1] is even.','Count length-n arrays over 1..m with exactly k qualifying indices, modulo 1,000,000,007.'],[([3,4,2],'The expression is even only for two adjacent even values; all three entries must be one of two evens, giving 2³=8.'),([5,1,0],'The only array is all ones, and none of its four adjacent pairs qualifies.')],EVEN_CASES,EVEN,[EVEN.replace('previous[used-1][1]*even','sum(previous[used-1])*even'),EVEN.replace('even=m//2;odd=m-even','odd=m//2;even=m-odd')],['Counts any pair ending in an even value instead of requiring both values even.','Swaps the odd and even value counts when m is odd.'],even_oracle,random_even,lesson('The expression is even only when both adjacent values are even.','Track how many qualifying pairs exist and whether the latest value is even.','Append an odd without increasing the count; append an even and increment only from an even predecessor.','Parity and the count are the only future-relevant facts, and multiplying by available odd/even values counts every concrete array.'),'O(nk)','O(k)',6),
3341:entry('minimum_room_time',[('move_time','list[list[int]]')],'int',['graphs','matrices','dijkstra'],['move_time is a 2–50 by 2–50 nonnegative matrix.','Start at (0,0) at time zero; before entering a neighbor, wait until its opening time, then spend one second moving.','Return the earliest arrival at the bottom-right room using four-directional moves.'],[([[[0,4],[4,4]]],'Wait until time four, then two one-second moves arrive at time six.'),([[[0,0,0],[0,0,0]]],'With no waiting, the shortest three-edge route takes three seconds.')],GRID_CASES,GRID_ONE,[GRID_ONE.replace('max(elapsed,move_time[nr][nc])+1','max(elapsed,move_time[nr][nc])'),GRID_ONE.replace('move_time[nr][nc]','move_time[row][col]')],['Forgets the one second required to traverse an edge.','Waits for the room being left rather than the destination room.'],grid_one_oracle,random_grid,lesson('Reaching a room earlier can never hurt because waiting is allowed.','Use Dijkstra with arrival time as distance and a time-dependent but monotone edge relaxation.','For each neighbor compute max(current time, neighbor opens)+1 and relax it in a heap.','The relaxation has the FIFO property, so the first finalized destination time is globally minimal.'),'O(rc log(rc))','O(rc)',6),
3342:entry('minimum_alternating_room_time',[('move_time','list[list[int]]')],'int',['graphs','matrices','dijkstra'],['move_time is a 2–750 by 2–750 nonnegative matrix.','Starting at (0,0), move durations alternate 1,2,1,2,... while entry may wait for the destination opening time.','Return the earliest arrival at the bottom-right room using four-directional moves.'],[([[[0,4],[4,4]]],'After waiting to time four, moves of one and two seconds arrive at time seven.'),([[[0,0,0,0],[0,0,0,0]]],'Four moves cost 1+2+1+2, so the empty-opening grid takes six seconds.')],GRID_CASES,GRID_TWO,[GRID_TWO.replace('cost=(row+col)%2+1','cost=1'),GRID_TWO.replace('cost=(row+col)%2+1','cost=(row+col+1)%2+1')],['Charges one second for every move instead of alternating.','Starts the duration sequence with two seconds instead of one.'],grid_two_oracle,random_grid,lesson('Grid bipartiteness fixes move-count parity from (row+col), even when a route detours.','Use Dijkstra and derive the next duration as (row+col)%2+1 at the current room.','Wait for the neighbor to open, add the parity-derived duration, and relax its arrival.','Every route to one cell has the same step parity, so one best-time label per cell is sufficient and Dijkstra remains valid.'),'O(rc log(rc))','O(rc)',6),
3343:entry('count_balanced_digit_permutations',[('num','str')],'int',['dynamic programming','combinatorics','strings'],['num contains 2–80 decimal digits and repeated digits are indistinguishable.','A permutation is balanced when sums at zero-based even and odd indices are equal.','Return the number of distinct balanced permutations modulo 1,000,000,007.'],[(['123'],'The balanced distinct permutations are 132 and 231.'),(['112'],'Only 121 places digit two at the middle odd index and balances the two sides.')],BALANCED_CASES,BALANCED,[BALANCED.replace('(len(num)+1)//2','len(num)//2'),BALANCED.replace('range(min(counts[digit],left_slots)+1)','range(min(counts[digit],left_slots))')],['Allocates too few positions on the larger parity side for odd-length strings.','Never considers assigning zero or all available copies of a digit to the selected side at the loop boundary.'],balanced_oracle,random_balanced,lesson('Equal side sums require an even total and each digit count must be split between two position groups.','Process digits 0..9 while tracking remaining target sum and available slots on both sides.','Choose how many copies enter one side; multiply slot combinations for both sides and recurse on the next digit.','Choosing positions for indistinguishable copies counts each distinct permutation once, while the target and slot constraints enforce balance.'),'O(10*S*n²)','O(10*S*n²)',8),
}
