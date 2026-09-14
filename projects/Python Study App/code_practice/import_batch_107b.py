"""Second reviewed group of workbook batch 107."""
from collections import deque
from .import_batch_055 import entry
def jumps_o(a):
 obstacles=a[0];n=len(obstacles)-1;dist={(0,2):0};queue=deque([(0,2)])
 while queue:
  position,lane=queue.popleft();cost=dist[position,lane]
  moves=[]
  if position<n and obstacles[position+1]!=lane:moves.append((position+1,lane,0))
  moves += [(position,other,1) for other in (1,2,3) if other!=lane and obstacles[position]!=other]
  for next_position,next_lane,extra in moves:
   if cost+extra<dist.get((next_position,next_lane),10**9):dist[next_position,next_lane]=cost+extra;(queue.appendleft if extra==0 else queue.append)((next_position,next_lane))
 return min(dist.get((n,lane),10**9) for lane in (1,2,3))
def sensor_o(a):
 first,second=a;n=len(first)
 one=any(first[:drop]==second[:drop] and first[drop:n-1]==second[drop+1:] for drop in range(n))
 two=any(second[:drop]==first[:drop] and second[drop:n-1]==first[drop+1:] for drop in range(n))
 return 1 if one and not two else 2 if two and not one else -1
def increasing_o(a):
 nums=a[0];previous=-10**18;answer=0
 for value in nums:chosen=max(value,previous+1);answer+=chosen-value;previous=chosen
 return answer
def circles_o(a):
 points,queries=a;return [sum((px-x)**2+(py-y)**2<=radius**2 for px,py in points) for x,y,radius in queries]
def maxxor_o(a):
 nums,bits=a;answer=[];current=nums[:]
 while current:
  value=0
  for item in current:value^=item
  answer.append(max(range(1<<bits),key=lambda candidate:value^candidate));current.pop()
 return answer
def rjumps(r):
 length=r.randint(1,20);values=[0];last=0
 for _ in range(length-1):last=r.randint(0,3);values.append(last)
 values.append(0);return [values]
def rsensor(r):
 n=r.randint(2,10);base=[r.randint(0,8) for _ in range(n)]
 if r.random()<.2:return [base[:],base[:]]
 drop=r.randrange(n-1);replacement=r.choice([value for value in range(9) if value!=base[drop]]);faulty=base[:drop]+base[drop+1:]+[replacement]
 return [faulty,base] if r.random()<.5 else [base,faulty]
def rincreasing(r):return [[r.randint(0,20) for _ in range(r.randint(1,15))]]
def rcircles(r):return [[[r.randint(-10,10),r.randint(-10,10)] for _ in range(r.randint(1,12))],[[r.randint(-10,10),r.randint(-10,10),r.randint(1,12)] for _ in range(r.randint(1,8))]]
def rmaxxor(r):
 bits=r.randint(1,5);nums=sorted(r.randint(0,(1<<bits)-1) for _ in range(r.randint(1,12)));return [nums,bits]
JUMPS='''def minimum_side_jumps(obstacles):
 costs=[1,0,1]
 for obstacle in obstacles[1:]:
  if obstacle:costs[obstacle-1]=10**9
  best=min(costs)+1
  for lane in range(3):
   if obstacle!=lane+1:costs[lane]=min(costs[lane],best)
 return min(costs)
'''
SENSOR='''def identify_faulty_sensor(sensor1, sensor2):
 index=0
 while index<len(sensor1)-1 and sensor1[index]==sensor2[index]:index+=1
 while index<len(sensor1)-1:
  if sensor1[index+1]!=sensor2[index]:return 1
  if sensor1[index]!=sensor2[index+1]:return 2
  index+=1
 return -1
'''
INCREASING='''def minimum_increasing_operations(nums):
 operations=0;previous=nums[0]
 for value in nums[1:]:
  increase=max(0,previous+1-value);operations+=increase;previous=value+increase
 return operations
'''
CIRCLES='''def points_inside_circles(points, queries):
 answer=[]
 for x,y,radius in queries:answer.append(sum((px-x)**2+(py-y)**2<=radius**2 for px,py in points))
 return answer
'''
MAXXOR='''def maximum_xor_queries(nums, maximum_bit):
 mask=(1<<maximum_bit)-1;value=0
 for item in nums:value^=item
 answer=[]
 for item in reversed(nums):answer.append(value^mask);value^=item
 return answer
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1824:E('minimum_side_jumps',[('obstacles','list[int]')],'int',['arrays','dynamic-programming','greedy'],['The frog starts in lane two at point zero; endpoints contain no obstacle.','Forward moves cost zero and same-position lane changes cost one; return minimum side jumps.'],[([[0,1,2,3,0]],'The frog must change lanes twice to pass the three staggered obstacles.'),([[0,1,1,3,3,0]],'One early side jump reaches a lane that remains open.')],[[x] for x in [[0,0],[0,1,0],[0,2,0],[0,3,0],[0,1,2,3,0],[0,1,1,3,3,0],[0,2,1,0,3,0],[0,0,0,0],[0,3,2,1,0],[0,1,0,2,0,3,0],[0,2,3,1,2,0],[0,1,3,2,0],[0,3,0,3,0],[0,2,0,1,0]]],JUMPS,[JUMPS.replace('costs=[1,0,1]','costs=[0,1,0]'),JUMPS.replace('min(costs)+1','max(costs)+1')],['Starts as though the frog were in lanes one and three.', 'Bases every side jump on the worst rather than best reachable lane.'],jumps_o,rjumps,H('Track the cheapest cost to occupy each of the three lanes at the current point.','Block the obstacle lane before considering sideways changes.','For every open lane, keep its current cost or one plus the minimum open-lane cost.','Forward travel preserves cost, and every optimal side jump comes from the cheapest currently reachable open lane, so the three-state DP is complete.'),'O(n)','O(1)',5),
1826:E('identify_faulty_sensor',[('sensor1','list[int]'),('sensor2','list[int]')],'int',['arrays','two-pointers'],['At most one sensor dropped one non-final value, shifted later values left, and received an unrelated last value.','Return 1 or 2 when uniquely identifiable; otherwise return -1.'],[([[2,3,4,5],[2,1,3,4]],'Sensor one matches sensor two after dropping its value one, so sensor one is faulty.'),([[2,2,2,2],[2,2,2,2]],'Identical readings do not identify a defective sensor.')],[[*x] for x in [([2,3,4,5],[2,1,3,4]),([2,2,2,2],[2,2,2,2]),([1,2],[2,1]),([1,2,3],[1,3,4]),([1,3,4],[1,2,3]),([5,6,7,9],[5,6,8,7]),([0,1,2,3],[0,2,3,4]),([0,2,3,4],[0,1,2,3]),([1,1,2],[1,2,3]),([1,2,3],[1,1,2]),([4,5,6],[4,5,7]),([3,4,5,6],[3,4,5,6]),([9,1,2,3],[8,9,1,2]),([8,9,1,2],[9,1,2,3])]],SENSOR,[SENSOR.replace('return 1','return 2',1),SENSOR.replace('return -1','return 1')],['Reports the opposite sensor for the first decisive mismatch.', 'Claims sensor one even when the result is ambiguous.'],sensor_o,rsensor,H('Equal prefixes reveal nothing; start at the first mismatch.','Compare each sequence against the other shifted by one from that point.','A failure of one shifted alignment uniquely identifies the corresponding faulty sensor; if neither fails, return -1.','Dropping one value creates exactly a one-position suffix alignment, and checking both possible alignments covers all valid histories.'),'O(n)','O(1)',3),
1827:E('minimum_increasing_operations',[('nums','list[int]')],'int',['arrays','greedy'],['One operation increments one array element by one.','Return the minimum operations needed to make the array strictly increasing.'],[([[1,1,1]],'Raise the second value to two and the third to three, costing three increments.'),([[1,5,2,4,1]],'The cheapest increasing result is [1,5,6,7,8], requiring fourteen increments.')],[[x] for x in [[1],[1,1],[1,1,1],[1,2,3],[3,2,1],[1,5,2,4,1],[8],[0,0,0,0],[5,5,6],[2,1,2,1],[10,1],[1,3,3,5],[4,2,7,3],[2,2,4,4]]],INCREASING,[INCREASING.replace('previous+1-value','previous-value'),INCREASING.replace('previous=value+increase','previous=value')],['Allows equal adjacent values instead of strict increase.', 'Forgets increments when establishing the next lower bound.'],increasing_o,rincreasing,H('Each position only needs to exceed the finalized value immediately before it.','Leave a value unchanged when possible; otherwise raise it to previous+1.','Add the required increase and carry the adjusted value forward.','Any larger choice wastes increments and cannot help earlier positions, so the smallest legal value is greedily optimal at every step.'),'O(n)','O(1)',3),
1828:E('points_inside_circles',[('points','list[list[int]]'),('queries','list[list[int]]')],'list[int]',['arrays','geometry','math'],['Each query is [center_x,center_y,radius].','Count points on or inside each circle independently and return counts in query order.'],[([[[1,3],[3,3],[5,3],[2,2]],[[2,3,1],[4,3,1],[1,1,2]]],'The three circles contain three, two, and two points respectively.'), ([[[1,1],[2,2],[3,3]],[[1,1,0],[2,2,2]]],'The radius-zero circle contains its exact center; the second contains all three points.')],[[*x] for x in [([[0,0]],[[0,0,1]]),([[0,0]],[[2,0,1]]),([[1,3],[3,3],[5,3],[2,2]],[[2,3,1],[4,3,1],[1,1,2]]),([[1,1],[2,2],[3,3]],[[1,1,0],[2,2,2]]),([[0,0],[3,4]],[[0,0,5]]),([[-1,-1],[1,1]],[[0,0,1]]),([[-1,-1],[1,1]],[[0,0,2]]),([[2,0],[-2,0],[0,2],[0,-2]],[[0,0,2]]),([[5,5]],[[5,5,0],[0,0,10]]),([[1,0],[2,0],[3,0]],[[0,0,2]]),([[0,0],[10,10]],[[5,5,7]]),([[1,2],[2,1]],[[1,1,1]]),([[4,3],[3,4]],[[0,0,5]]),([[0,1],[0,2]],[[0,0,1],[0,0,2]])]],CIRCLES,[CIRCLES.replace('<=radius**2','<radius**2'),CIRCLES.replace('(px-x)**2+(py-y)**2','abs(px-x)+abs(py-y)')],['Excludes points exactly on the boundary.', 'Uses Manhattan distance instead of squared Euclidean distance.'],circles_o,rcircles,H('Avoid square roots by comparing squared distances.','For each query, scan all points and compute dx²+dy².','Count a point when squared distance is at most radius².','Squaring preserves nonnegative distance order, and the inclusive comparison includes both interior and boundary points exactly.'),'O(points*queries)','O(queries)',5),
1829:E('maximum_xor_queries',[('nums','list[int]'),('maximum_bit','int')],'list[int]',['arrays','bit-manipulation','prefix-xor'],['For each query maximize current-array XOR xor k over 0<=k<2^maximum_bit, then remove the last array value.','Return one maximizing k for each shrinking suffix query.'],[([[0,1,1,3],2],'Complementing the current XOR within two bits after each removal yields [0,3,2,3].'),([[2,3,4,7],3],'The four optimal values are [5,2,6,5].')],[[*x] for x in [([0],1),([1],1),([0,1],1),([0,1,1,3],2),([2,3,4,7],3),([0,0,0],2),([1,2,3],2),([1,2,4],3),([3,3,3],2),([0,7],3),([1,1,2,2],2),([5,6,7],3),([0,1,2,3,4],3),([15,15],4)]],MAXXOR,[MAXXOR.replace('value^mask','value'),MAXXOR.replace('value^=item','value+=item')],['Returns the current XOR rather than its bit-limited complement.', 'Updates the shrinking aggregate by addition instead of removing an element with XOR.'],maxxor_o,rmaxxor,H('For a fixed bit width, XOR is maximized by flipping every bit of the current aggregate XOR.','The required k is current_xor XOR ((1<<maximum_bit)-1).','Compute the full XOR once, answer, then remove each last value using XOR again.','Each result sets every permitted output XOR bit to one, which is the maximum possible value, while reversible XOR maintains the next prefix aggregate.'),'O(n)','O(n)',5),
}
