"""Final reviewed group of workbook batch 116."""
from collections import deque
from .import_batch_055 import entry

def plates_o(a):
 s,queries=a;out=[]
 for left,right in queries:
  candles=[i for i in range(left,right+1) if s[i]=='|']
  out.append(0 if len(candles)<2 else s[candles[0]:candles[-1]+1].count('*'))
 return out
def index_o(a):return next((i for i,x in enumerate(a[0]) if i%10==x),-1)
def critical_o(a):
 values=a[0];points=[i for i in range(1,len(values)-1) if (values[i]-values[i-1])*(values[i]-values[i+1])>0]
 return [-1,-1] if len(points)<2 else [min(b-a for a,b in zip(points,points[1:])),points[-1]-points[0]]
def operations_o(a):
 nums,start,goal=a;q=deque([(start,0)]);seen={start}
 while q:
  value,steps=q.popleft()
  for x in nums:
   for nxt in (value+x,value-x,value^x):
    if nxt==goal:return steps+1
    if 0<=nxt<=1000 and nxt not in seen:seen.add(nxt);q.append((nxt,steps+1))
 return -1
def robot_o(a):
 room=a[0];rows=len(room);cols=len(room[0]);r=c=d=0;seen=set();clean=set();moves=((0,1),(1,0),(0,-1),(-1,0))
 while (r,c,d) not in seen:
  seen.add((r,c,d));clean.add((r,c));nr,nc=r+moves[d][0],c+moves[d][1]
  if not (0<=nr<rows and 0<=nc<cols) or room[nr][nc]:d=(d+1)%4
  else:r,c=nr,nc
 return len(clean)
def rplates(r):
 s=''.join(r.choice('*|') for _ in range(r.randint(1,30)));q=[]
 for _ in range(r.randint(1,10)):
  x,y=sorted((r.randrange(len(s)),r.randrange(len(s))));q.append([x,y])
 return [s,q]
def rindex(r):return [[r.randint(0,9) for _ in range(r.randint(1,50))]]
def rcritical(r):return [[r.randint(-10,10) for _ in range(r.randint(2,30))]]
def roperations(r):return [r.sample(range(-20,21),r.randint(1,8)),r.randint(0,1000),r.randint(-50,1050)]
def rrobot(r):
 rows,cols=r.randint(1,7),r.randint(1,7);room=[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)];room[0][0]=0;return [room]

PLATES='''\
def plates_between_candles(s,queries):
    prefix=[0]*(len(s)+1);left=[-1]*len(s);last=-1
    for i,char in enumerate(s):
        prefix[i+1]=prefix[i]+(char=='*')
        if char=='|':last=i
        left[i]=last
    right=[-1]*len(s);last=-1
    for i in range(len(s)-1,-1,-1):
        if s[i]=='|':last=i
        right[i]=last
    answer=[]
    for start,end in queries:
        first=right[start];last=left[end]
        answer.append(0 if first<0 or last<0 or first>=last else prefix[last]-prefix[first])
    return answer
'''
INDEX='''\
def smallest_equal_value_index(nums):
    for index,value in enumerate(nums):
        if index%10==value:return index
    return -1
'''
CRITICAL='''\
def critical_point_distances(head):
    positions=[];previous=head;node=head.next if head else None;index=1
    while node and node.next:
        if (node.val-previous.val)*(node.val-node.next.val)>0:positions.append(index)
        previous,node=node,node.next;index+=1
    if len(positions)<2:return [-1,-1]
    return [min(b-a for a,b in zip(positions,positions[1:])),positions[-1]-positions[0]]
'''
OPERATIONS='''\
def minimum_number_conversion_operations(nums,start,goal):
    from collections import deque
    queue=deque([(start,0)]);seen={start}
    while queue:
        value,steps=queue.popleft()
        for operand in nums:
            for candidate in (value+operand,value-operand,value^operand):
                if candidate==goal:return steps+1
                if 0<=candidate<=1000 and candidate not in seen:
                    seen.add(candidate);queue.append((candidate,steps+1))
    return -1
'''
ROBOT='''\
def cleaned_robot_spaces(room):
    rows,cols=len(room),len(room[0]);directions=((0,1),(1,0),(0,-1),(-1,0));row=column=direction=0
    states=set();cleaned=set()
    while (row,column,direction) not in states:
        states.add((row,column,direction));cleaned.add((row,column))
        nr=row+directions[direction][0];nc=column+directions[direction][1]
        if not (0<=nr<rows and 0<=nc<cols) or room[nr][nc]==1:direction=(direction+1)%4
        else:row,column=nr,nc
    return len(cleaned)
'''
def L(*x):return list(x)
BATCH={
2055:entry('plates_between_candles',[('s','str'),('queries','list[list[int]]')],'list[int]',['prefix sums','binary search','strings'],['s contains plates * and candles |; each query gives inclusive valid endpoints.','Count plates lying between a candle on their left and a candle on their right within each query.','Return answers in query order.'],[(['**|**|***|',[[2,5],[5,9]]],'The closed candle pairs enclose two and three plates respectively.'),(['***',[[0,2]]],'Without two candles, no plate is enclosed.')],[[s,q] for s,q in [('|*|',[[0,2]]),('***',[[0,2]]),('|||',[[0,2]]),('**|**|***|',[[2,5],[5,9]]),('|**|',[[1,2]]),('|**|',[[0,3]]),('*|*|*',[[0,4]]),('|',[[0,0]]),('**||**',[[0,5]]),('|*|*|',[[0,4],[1,3]]),('***|***',[[0,6]]),('|***|**|',[[0,7]]),('*||*',[[0,3]]),('||**||',[[1,4]])]],PLATES,[PLATES.replace('right[start]','left[start]'),PLATES.replace('prefix[last]-prefix[first]','prefix[last+1]-prefix[first]')],['Uses the nearest candle to the left of the query start instead of the first candle at or after it.','Includes the right candle position with an off-by-one prefix boundary.'],plates_o,rplates,L('Each query needs its nearest inward candle on both ends plus a fast plate count.','Precompute nearest candle to the left and right of every index and a prefix count of plates.','first=right[start], last=left[end]; if first<last return prefix[last]-prefix[first], else zero.','The inward candles define exactly the enclosed region, and the prefix difference counts precisely its plate characters.'),'O(n+queries)','O(n)',5),
2057:entry('smallest_equal_value_index',[('nums','list[int]')],'int',['arrays','simulation'],['nums has 1 through 100 integers from 0 through 9.','Find an index i satisfying i modulo 10 equals nums[i].','Return the smallest such index, or -1 if none exists.'],[([[0,1,2]],'Index zero satisfies zero modulo ten equals zero, so it is the smallest.'),([[4,3,2,1]],'Index two satisfies two modulo ten equals two.')],[[x] for x in [[0],[1],[0,1,2],[4,3,2,1],[9,9,9],[1,1],[5,1,2],[3,0,1,3],[9,8,7,6,5,4,3,2,1,0],[1,2,3,4,5,6,7,8,9,0,0],[2,0,2],[7,7,7,7,7,7,7,7],[0,0,0],[6,5,4,3,2,1,0]]],INDEX,[INDEX.replace('index%10==value','index==value'),INDEX.replace('return index','return index+1')],['Compares the full index and misses valid indices ten or greater.','Returns a one-based index instead of the required zero-based position.'],index_o,rindex,L('The condition can be tested independently at each position.','Scan from left to right and return immediately on index modulo ten equality.','for i,x: if i%10==x return i; return -1.','Left-to-right order makes the first match the smallest, and exhausting the list proves no match exists.'),'O(n)','O(1)',3),
2058:entry('critical_point_distances',[('head','ListNode | None')],'list[int]',['linked lists','local extrema'],['The linked list has at least two nodes.','A non-endpoint is critical when strictly greater than both neighbors or strictly less than both.','Return [minimum consecutive critical distance,first-to-last distance], or [-1,-1] with fewer than two points.'],[([[3,1]],'No node has both neighbors, so there are fewer than two critical points.'),([[5,3,1,2,5,1,2]],'Critical indices two, four, and five give minimum distance one and maximum three.')],[[x] for x in [[1,2],[3,1],[1,2,1],[1,2,3],[3,2,1],[1,3,2,4,1],[5,3,1,2,5,1,2],[1,1,1,1],[2,1,2,1,2],[1,5,1,5],[5,1,5,1],[0,-1,0,-1,0],[1,2,2,1],[4,2,3,1,5,0]]],CRITICAL,[CRITICAL.replace('>0','>=0'),CRITICAL.replace('positions[-1]-positions[0]','positions[-2]-positions[0]')],['Treats flat equal-neighbor positions as strict extrema.','Uses the second-to-last critical point when computing maximum distance.'],critical_o,rcritical,L('Criticality depends on a three-node window, and only the positions of critical nodes matter afterward.','Walk with previous,current,next, recording indices where the two differences have the same positive sign.','If fewer than two return [-1,-1]; minimum is adjacent-position gap and maximum is last-first.','Every critical node is detected once; the closest pair in sorted positions is adjacent, while the farthest pair is the endpoints.'),'O(n)','O(number of critical points)',5),
2059:entry('minimum_number_conversion_operations',[('nums','list[int]'),('start','int'),('goal','int')],'int',['breadth-first-search','graphs','bit manipulation'],['nums contains distinct integers; start is within 0..1000 and goal may be outside.','From x, one step may produce x+v, x-v, or x xor v for any v in nums.','An out-of-range result may equal goal but cannot be expanded; return minimum steps or -1.'],[([[2,4,12],2,12],'A shortest sequence reaches twelve in two operations.'),([[3,5,7],0,-4],'Subtracting values can reach the outside-range goal in two operations.')],[[n,s,g] for n,s,g in [([1],0,1),([1],0,2),([2,4,12],2,12),([3,5,7],0,-4),([2],0,3),([5],5,0),([1],1000,1001),([10],0,-10),([2,3],1,7),([4,6],2,8),([-1],0,-2),([7,9],5,3),([1000],1,1001),([2,5,10],7,0)]],OPERATIONS,[OPERATIONS.replace('if candidate==goal','if 0<=candidate<=1000 and candidate==goal'),OPERATIONS.replace('value^operand','value|operand')],['Rejects a valid final operation when the goal lies outside 0..1000.','Uses bitwise OR instead of the required XOR operation.'],operations_o,roperations,L('The bounded expandable values form an unweighted graph, with the possibly out-of-range goal checked as a terminal neighbor.','BFS from start; generate plus, minus, and xor results, return immediately on goal, and enqueue unseen in-range results.','Queue (value,steps); test candidate==goal before the 0..1000 expansion guard.','BFS explores operation counts in increasing order, and the guard matches the rule that outside results are terminal.'),'O(1001*len(nums))','O(1001)',5),
2061:entry('cleaned_robot_spaces',[('room','list[list[int]]')],'int',['matrices','simulation','cycle detection'],['room is a nonempty binary matrix and room[0][0] is empty.','The robot starts at top-left facing right, moves forward when possible, otherwise turns clockwise in place.','Return the number of distinct empty cells cleaned before its behavior repeats forever.'],[([[[0,0,0],[1,1,0],[0,0,0]]],'The deterministic route reaches seven distinct empty cells before repeating a state.'),([[[0]]],'The robot cleans only its starting cell.')],[[m] for m in [[[0]],[[0,0]],[[0],[0]],[[0,0],[0,0]],[[0,0,0],[1,1,0],[0,0,0]],[[0,1],[0,0]],[[0,0],[1,0]],[[0,1,0],[0,0,0]],[[0,0,0],[0,1,0],[0,0,0]],[[0,1,1],[0,0,0],[1,1,0]],[[0,0,1],[1,0,1],[1,0,0]],[[0,0,0,0]],[[0],[0],[0],[0]],[[0,1,0,0],[0,0,0,1]]]],ROBOT,[ROBOT.replace('(row,column,direction)','(row,column)',1),ROBOT.replace('direction=(direction+1)%4','direction=(direction-1)%4')],['Stops when revisiting a cell from a new direction even though future behavior differs.','Turns counterclockwise instead of clockwise at obstacles.'],robot_o,rrobot,L('Movement is deterministic, so repeating the same cell and direction means the entire future will repeat.','Simulate while tracking full states and a separate set of cleaned cells.','On blockage rotate direction=(direction+1)%4; otherwise move; stop at repeated (row,column,direction).','There are only four states per cell, guaranteeing termination, and deterministic state repetition proves no new cell can appear afterward.'),'O(rows*columns)','O(rows*columns)',5)
}
BATCH[2058]['params'][0]=('head','ListNode | None','listnode')
BATCH[2055]['wrong'][1]=PLATES.replace('prefix[last]-prefix[first]','prefix[last]-prefix[first]-1')
BATCH[2055]['wrong_reasons'][1]='Subtracts one extra plate from every nonempty enclosed region.'
BATCH[2061]['wrong'][0]=ROBOT.replace('(row,column,direction)','(row,column)')
BATCH[2061]['wrong_reasons'][0]='Stops when revisiting a cell from a new direction even though future behavior differs.'
