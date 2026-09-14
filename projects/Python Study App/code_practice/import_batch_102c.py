"""Final half of batch 102: graph queries, queues, simulation, and greedy selection."""
from collections import Counter,deque
from .import_batch_055 import entry
MOD=1_000_000_007
def jump_o(a):
 nums,k=a;dp=[-10**9]*len(nums);dp[0]=nums[0]
 for i in range(1,len(nums)):dp[i]=nums[i]+max(dp[max(0,i-k):i])
 return dp[-1]
def paths_o(a):
 n,edges,queries=a;answer=[]
 for source,target,limit in queries:
  graph=[[] for _ in range(n)]
  for x,y,w in edges:
   if w<limit:graph[x].append(y);graph[y].append(x)
  seen={source};stack=[source]
  while stack:
   for nxt in graph[stack.pop()]:
    if nxt not in seen:seen.add(nxt);stack.append(nxt)
  answer.append(target in seen)
 return answer
def lunch_o(a):
 students,sandwiches=a;counts=Counter(students)
 for sandwich in sandwiches:
  if counts[sandwich]==0:return sum(counts.values())
  counts[sandwich]-=1
 return 0
def waiting_o(a):
 current=total=0
 for arrival,duration in a[0]:current=max(current,arrival)+duration;total+=current-arrival
 return total/len(a[0])
def binary_o(a):
 s=a[0];zeros=s.count('0')
 if zeros<2:return s
 position=s.index('0')+zeros-1
 return '1'*position+'0'+'1'*(len(s)-position-1)
def halves_o(a):
 s=a[0];v=set('aeiouAEIOU');middle=len(s)//2;return sum(c in v for c in s[:middle])==sum(c in v for c in s[middle:])
def balls_o(a):
 grid=a[0];answer=[]
 for start in range(len(grid[0])):
  column=start
  for row in grid:
   nxt=column+row[column]
   if nxt<0 or nxt>=len(row) or row[nxt]!=row[column]:column=-1;break
   column=nxt
  answer.append(column)
 return answer
def largest_o(a):
 nums,k=a;return max((nums[i:i+k] for i in range(len(nums)-k+1)))
def units_o(a):
 boxes,size=a;expanded=[]
 for count,value in boxes:expanded.extend([value]*count)
 return sum(sorted(expanded,reverse=True)[:size])
def meals_o(a):
 values=a[0];return sum(((values[i]+values[j])&(values[i]+values[j]-1))==0 and values[i]+values[j]>0 for i in range(len(values)) for j in range(i+1,len(values)))%MOD
def rjump(r):
    nums=[r.randint(-20,20) for _ in range(r.randint(1,20))]
    return [nums,r.randint(1,len(nums))]
def rpaths(r):
 n=r.randint(2,8);edges=[[i,j,r.randint(1,20)] for i in range(n) for j in range(i+1,n) if r.random()<.3];queries=[[r.randrange(n),r.randrange(n),r.randint(1,21)] for _ in range(r.randint(1,10))];return [n,edges,queries]
def rlunch(r):
 n=r.randint(1,30);return [[r.randrange(2) for _ in range(n)],[r.randrange(2) for _ in range(n)]]
def rwaiting(r):
 now=0;customers=[]
 for _ in range(r.randint(1,20)):now+=r.randint(1,5);customers.append([now,r.randint(1,10)])
 return [customers]
def rbinary(r):return [''.join(r.choice('01') for _ in range(r.randint(1,30)))]
def rhalves(r):
 n=2*r.randint(1,20);return [''.join(r.choice('abcdeiouXYZ') for _ in range(n))]
def rballs(r):
 rows,cols=r.randint(1,8),r.randint(1,8);return [[[r.choice((-1,1)) for _ in range(cols)] for _ in range(rows)]]
def rlargest(r):
 n=r.randint(1,15);nums=r.sample(range(-30,31),n);return [nums,r.randint(1,n)]
def runits(r):
 boxes=[[r.randint(1,8),r.randint(1,20)] for _ in range(r.randint(1,8))];return [boxes,r.randint(1,sum(x[0] for x in boxes))]
def rmeals(r):return [[r.randint(0,32) for _ in range(r.randint(1,30))]]
JUMP='''def maximum_jump_score(nums, k):
 scores=[0]*len(nums);scores[0]=nums[0];window=deque([0])
 for index in range(1,len(nums)):
  while window[0]<index-k:window.popleft()
  scores[index]=nums[index]+scores[window[0]]
  while window and scores[window[-1]]<=scores[index]:window.pop()
  window.append(index)
 return scores[-1]
'''
PATHS='''def distance_limited_paths_exist(n, edge_list, queries):
 parent=list(range(n))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 indexed=sorted(enumerate(queries),key=lambda item:item[1][2]);edges=sorted(edge_list,key=lambda edge:edge[2]);answer=[False]*len(queries);cursor=0
 for qi,(source,target,limit) in indexed:
  while cursor<len(edges) and edges[cursor][2]<limit:
   left,right,_=edges[cursor];parent[find(left)]=find(right);cursor+=1
  answer[qi]=find(source)==find(target)
 return answer
'''
LUNCH='''def students_unable_to_eat(students, sandwiches):
 counts=Counter(students)
 for sandwich in sandwiches:
  if counts[sandwich]==0:return counts[0]+counts[1]
  counts[sandwich]-=1
 return 0
'''
WAIT='''def average_customer_waiting_time(customers):
 finish=total=0
 for arrival,duration in customers:finish=max(finish,arrival)+duration;total+=finish-arrival
 return total/len(customers)
'''
MAXBINARY='''def maximum_binary_after_changes(binary):
 zeros=binary.count('0')
 if zeros<2:return binary
 zero=binary.index('0')+zeros-1
 return '1'*zero+'0'+'1'*(len(binary)-zero-1)
'''
HALVES='''def string_halves_are_alike(s):
 vowels=set('aeiouAEIOU');middle=len(s)//2
 return sum(char in vowels for char in s[:middle])==sum(char in vowels for char in s[middle:])
'''
BALLS='''def ball_exit_columns(grid):
 answer=[]
 for start in range(len(grid[0])):
  column=start
  for row in grid:
   nxt=column+row[column]
   if nxt<0 or nxt>=len(row) or row[nxt]!=row[column]:column=-1;break
   column=nxt
  answer.append(column)
 return answer
'''
LARGEST='''def largest_length_k_subarray(nums, k):
 start=max(range(len(nums)-k+1),key=lambda index:nums[index])
 return nums[start:start+k]
'''
UNITS='''def maximum_truck_units(box_types, truck_size):
 answer=0
 for count,units in sorted(box_types,key=lambda item:item[1],reverse=True):
  loaded=min(count,truck_size);answer+=loaded*units;truck_size-=loaded
  if truck_size==0:break
 return answer
'''
MEALS='''def count_power_of_two_meals(deliciousness):
 counts=Counter();answer=0
 for value in deliciousness:
  for power in (1<<bit for bit in range(22)):answer+=counts[power-value]
  counts[value]+=1
 return answer%1000000007
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1696:E('maximum_jump_score',[('nums','list[int]'),('k','int')],'int',['dynamic-programming','monotonic-queues'],['Start at index zero and jump forward 1 through k positions until the final index.','Score includes every visited value; return the maximum possible score.'],[([[1,-1,-2,4,-7,3],2],'The route 0,1,3,5 scores seven.'),([[10,-5,-2,4,0,3],3],'Optimal jumps produce score seventeen.')],[[*x] for x in [([1,-1,-2,4,-7,3],2),([10,-5,-2,4,0,3],3),([1],1),([1,2],1),([1,-1,2],2),([-1,-2,-3],1),([5,-10,5],2),([1,2,3,4],2),([4,3,2,1],3),([0,0,0],2),([10,-100,-100,10],2),([1,-2,3,-4,5],3),([-5,10,-5,10],1),([2,9,-8,7,6],2)]],JUMP,[JUMP.replace('window[0]<index-k','window[0]<=index-k'),JUMP.replace('scores[window[-1]]<=scores[index]','scores[window[-1]]>=scores[index]')],['Expires the predecessor exactly k positions away even though that jump is allowed.','Maintains an increasing queue and selects the smallest prior score.'],jump_o,rjump,L('The DP transition needs the largest score among the previous k indices.','Maintain those candidate scores in decreasing deque order.','Remove expired front indices, add nums[i] to the front score, pop dominated backs, and append i.','The deque front is always the maximum valid predecessor, and dominated smaller scores expire no later than the new score.'),'O(n)','O(k)',5),
1697:E('distance_limited_paths_exist',[('n','int'),('edge_list','list[list[int]]'),('queries','list[list[int]]')],'list[bool]',['graphs','union-find'],['Undirected weighted graph; each query is [source,target,limit].','A valid path uses only edges with weight strictly less than limit. Return answers in query order.'],[([3,[[0,1,2],[1,2,4],[2,0,8],[1,0,16]],[[0,1,2],[0,2,5]]],'Weight two is not strictly below the first limit, while edges two and four connect zero to two below limit five.'),([5,[[0,1,10],[1,2,5],[2,3,9],[3,4,13]],[[0,4,14],[1,4,13]]],'The first query can use every needed edge; the second excludes weight thirteen.')],[[*x] for x in [(3,[[0,1,2],[1,2,4],[2,0,8],[1,0,16]],[[0,1,2],[0,2,5]]),(5,[[0,1,10],[1,2,5],[2,3,9],[3,4,13]],[[0,4,14],[1,4,13]]),(2,[],[[0,1,1]]),(2,[[0,1,1]],[[0,1,2]]),(2,[[0,1,2]],[[0,1,2]]),(3,[[0,1,1],[1,2,1]],[[0,2,2]]),(3,[[0,1,1]],[[0,2,10]]),(3,[],[[1,1,0]]),(4,[[0,1,5],[2,3,5]],[[0,3,6]]),(4,[[0,1,5],[1,2,6],[2,3,7]],[[0,3,8]]),(4,[[0,1,5],[1,2,6]],[[0,2,6]]),(3,[[0,2,10],[0,1,3],[1,2,4]],[[0,2,5]]),(5,[[0,1,1],[1,2,2],[2,3,3],[3,4,4]],[[0,4,5],[4,0,4]]),(3,[[0,1,2]],[[0,0,1],[0,1,3]])]],PATHS,[PATHS.replace('edges[cursor][2]<limit','edges[cursor][2]<=limit'),PATHS.replace('answer[qi]','answer[cursor%len(answer)]')],['Treats an edge equal to the limit as allowed.','Writes answers by edge cursor rather than original query index.'],paths_o,rpaths,L('Queries become incremental connectivity checks when sorted by their limits.','Sort edges by weight and queries by limit; union every edge strictly below the current limit.','For each indexed query, advance the edge cursor, compare roots, and store by original query index.','The union-find contains exactly the graph induced by eligible edges, so shared roots are equivalent to an allowed path.'),'O((edges+queries) log(edges+queries))','O(n+queries)',8),
1700:E('students_unable_to_eat',[('students','list[int]'),('sandwiches','list[int]')],'int',['queues','counting'],['Students and sandwiches contain only zero and one and have equal lengths.','Students may rotate freely until nobody wants the current sandwich; return the number left.'],[([[1,1,0,0],[0,1,0,1]],'Every sandwich preference can be matched, leaving zero students.'),([[1,1,1,0,0,1],[1,0,0,0,1,1]],'Three students remain when the next sandwich type has no interested student.')],[[*x] for x in [([1,1,0,0],[0,1,0,1]),([1,1,1,0,0,1],[1,0,0,0,1,1]),([0],[0]),([0],[1]),([1],[0]),([0,1],[1,0]),([0,0],[1,0]),([1,1],[1,1]),([0,1,0],[0,0,1]),([1,0,1],[0,1,1]),([0,0,1,1],[1,1,0,0]),([1,0,0],[1,1,0]),([0,1,1,1],[0,0,1,1]),([1,0,1,0,1],[1,1,0,0,1])]],LUNCH,[LUNCH.replace('counts[sandwich]==0','counts[sandwich]<=1'),LUNCH.replace('counts[sandwich]-=1','counts[1-sandwich]-=1')],['Stops even when exactly one student wants the current sandwich.','Removes a student with the opposite preference.'],lunch_o,rlunch,L('Queue rotations change order but not the count of each remaining preference.','Consume the top sandwich whenever its preference count is positive; otherwise stop.','Count zeros and ones, scan sandwiches, decrement a matching count, and return remaining total at the first zero count.','If a matching student exists rotations bring one forward; if none exists no future action can remove the top sandwich.'),'O(n)','O(1)',3),
1701:E('average_customer_waiting_time',[('customers','list[list[int]]')],'float',['simulation','arrays'],['Customers arrive in increasing order and have positive preparation times.','Waiting time runs from arrival through completion; return the average.'],[([[[1,2],[2,5],[4,3]]],'Completion times three, eight, and eleven give waits two, six, and seven, averaging five.'),([[[5,2],[5,4],[10,3],[20,1]]],'The chef may idle before arrivals; the average wait is 3.25.')],[[c] for c in [[[1,2],[2,5],[4,3]],[[5,2],[5,4],[10,3],[20,1]],[[1,1]],[[10,5]],[[1,5],[2,1]],[[1,1],[10,1]],[[0,3],[1,3],[2,3]],[[2,2],[4,2]],[[1,10],[2,1],[3,1]],[[5,5],[5,5]],[[1,2],[100,3]],[[0,1],[1,1],[2,1]],[[3,7],[4,2],[20,4]],[[1,4],[3,2],[4,1]]]],WAIT,[WAIT.replace('max(finish,arrival)','finish'),WAIT.replace('finish-arrival','finish')],['Never lets an idle chef advance to a later arrival time.','Averages absolute completion times rather than customer waiting times.'],waiting_o,rwaiting,L('Each order starts at the later of its arrival and the previous completion.','Track the chef’s finish time and add finish-arrival for each customer.','Update finish=max(finish,arrival)+duration, accumulate its wait, then divide by customer count.','Single-chef input order fixes every start once the prior finish is known, so the simulation is exact.'),'O(n)','O(1)',5),
1702:E('maximum_binary_after_changes',[('binary','str')],'str',['strings','greedy'],['Nonempty binary string.','Allowed rewrites are 00 to 10 and 10 to 01; return the lexicographically maximum reachable string.'],[(['000110'],'Three zeros collapse to one zero at index three, producing 111011.'),(['01'],'With fewer than two zeros no improving rewrite exists.')],[[s] for s in ['000110','01','0','1','00','10','11','0000','1000','0100','0011','101010','111000','000111']],MAXBINARY,[MAXBINARY.replace('zeros<2','zeros<3'),MAXBINARY.replace("binary.index('0')+zeros-1","binary.index('0')")],['Leaves a two-zero string unchanged even though it can improve.','Places the sole remaining zero at the first original zero instead of shifting it right for every additional zero.'],binary_o,rbinary,L('All reachable maxima contain at most one zero; each extra zero can shift that remaining zero right.','Count zeros and locate the first zero.','If fewer than two zeros return input; otherwise return ones with one zero at first_zero+zero_count-1.','The rewrites move zero mass right while converting pairs to ones, and the stated position is the furthest achievable sole zero.'),'O(n)','O(n)',5),
1704:E('string_halves_are_alike',[('s','str')],'bool',['strings','counting'],['s has positive even length and may mix letter cases.','Split at the midpoint and compare vowel counts case-insensitively.'],[(['book'],'Each half contains one o, so they are alike.'),(['textbook'],'The first half has one vowel and the second has two.')],[[s] for s in ['book','textbook','aa','ab','ba','AE','AbCd','MerryChristmas','aAee','zzzz','uoie','PythonPY','xYxY','leetcode']],HALVES,[HALVES.replace("set('aeiouAEIOU')","set('aeiou')"),HALVES.replace('==sum','!=sum')],['Ignores uppercase vowels.','Returns true when the vowel counts differ.'],halves_o,rhalves,L('Only vowel membership and the fixed midpoint matter.','Count vowels independently in the two equal-length slices.','Build a case-aware vowel set and compare the two membership sums.','Each character belongs to exactly one half, so equal sums are exactly the definition of alike halves.'),'O(n)','O(1)',3),
1706:E('ball_exit_columns',[('grid','list[list[int]]')],'list[int]',['matrices','simulation'],['Each cell is 1 or -1 and directs a ball diagonally right or left.','A ball sticks at a wall or V-shaped adjacent pair; return its exit column or -1 for every starting column.'],[([[[1,1,1,-1,-1],[1,1,1,-1,-1],[-1,-1,-1,1,1],[1,1,1,1,-1],[-1,-1,-1,-1,-1]]],'Only the first ball crosses every row and exits at column one.'),([[[-1]]],'The only ball immediately points into the left wall and sticks.')],[[g] for g in [[[-1]],[[1]],[[1,1]],[[1,-1]],[[1,1],[-1,-1]],[[-1,-1],[1,1]],[[1,1,1],[-1,-1,-1]],[[1,-1,1]],[[1,1,-1,-1]],[[1,1,1,-1,-1],[1,1,1,-1,-1],[-1,-1,-1,1,1],[1,1,1,1,-1],[-1,-1,-1,-1,-1]],[[1,1],[1,1]],[[1,-1],[-1,1]],[[-1,1,1],[1,1,-1]],[[1,1,-1],[1,-1,-1]]]],BALLS,[BALLS.replace('row[nxt]!=row[column]','row[nxt]==row[column]'),BALLS.replace('column=nxt','column=start')],['Treats matching adjacent slopes as a V-shaped trap.','Resets each row to the starting column instead of following the ball’s path.'],balls_o,rballs,L('A move succeeds only when the destination column is in bounds and its board has the same slope.','Simulate each ball row by row.','Compute next=column+grid[row][column]; reject wall or opposite neighbor, otherwise assign next.','Equal neighboring slopes form a continuous channel; opposite slopes form exactly the V trap described.'),'O(rows*columns)','O(columns)',5),
1708:E('largest_length_k_subarray',[('nums','list[int]'),('k','int')],'list[int]',['arrays','greedy'],['nums contains distinct integers and 1 <= k <= len(nums).','Among contiguous length-k slices, return the lexicographically largest.'],[([[1,4,5,2,3],3],'Eligible starts are one, four, and five; the slice starting at five is 5,2,3.'),([[1,4,5,2,3],4],'Only starts one and four fit; 4,5,2,3 is larger.')],[[*x] for x in [([1,4,5,2,3],3),([1,4,5,2,3],4),([1],1),([2,1],1),([2,1],2),([3,1,2],2),([1,2,3],2),([5,4,3,2],3),([-1,-2,-3],2),([1,9,2,8],2),([7,1,6,2,5],3),([0,10,-1],2),([4,2,9,1,3],2),([8,3,7,2,6,1],4)]],LARGEST,[LARGEST.replace('len(nums)-k+1','len(nums)-k'),LARGEST.replace('key=lambda index:nums[index]','key=lambda index:-nums[index]')],['Omits the final valid start position.','Chooses the smallest rather than largest starting value.'],largest_o,rlargest,L('Distinct values make the first element alone decide between any two candidate slices.','Choose the maximum start value among indices that leave k elements.','Search starts 0 through n-k, then return nums[start:start+k].','Every pair of candidate slices differs immediately because their first elements come from distinct indices with distinct values.'),'O(n)','O(k)',3),
1710:E('maximum_truck_units',[('box_types','list[list[int]]'),('truck_size','int')],'int',['greedy','sorting'],['Each type gives [available boxes, units per box]; load at most truck_size boxes.','Maximize total units.'],[([[[1,3],[2,2],[3,1]],4],'Load one three-unit box, two two-unit boxes, and one one-unit box for eight.'),([[[5,10],[2,5],[4,7],[3,9]],10],'Taking boxes from highest unit values first yields ninety-one.')],[[*x] for x in [([[1,3],[2,2],[3,1]],4),([[5,10],[2,5],[4,7],[3,9]],10),([[1,1]],1),([[5,2]],3),([[1,10],[10,1]],1),([[2,5],[2,5]],3),([[3,1],[1,100]],2),([[2,3],[4,2]],6),([[1,9],[1,8],[1,7]],2),([[10,1],[1,2]],5),([[3,4],[2,6]],4),([[5,5],[5,4]],7),([[1,20],[2,10],[3,5]],3),([[4,2],[1,9],[2,3]],5)]],UNITS,[UNITS.replace('reverse=True','reverse=False'),UNITS.replace('loaded*units','count*units')],['Loads the least valuable box types first.','Adds units for every available box even when truck capacity takes fewer.'],units_o,runits,L('Every box uses one capacity slot, so higher units always dominate lower units.','Sort types by units descending and take as many as capacity allows.','For each type load min(count,remaining), add loaded*units, and stop at zero capacity.','Exchanging a loaded lower-unit box for an available higher-unit box improves the total, proving greedy order.'),'O(types log types)','O(types)',3),
1711:E('count_power_of_two_meals',[('deliciousness','list[int]')],'int',['hash-maps','counting'],['Nonnegative values; choose two distinct indices.','Count index pairs whose sum is a positive power of two, modulo 1,000,000,007.'],[([[1,3,5,7,9]],'Valid pairs sum to four, eight, or sixteen, giving four pairs.'),([[1,1,1,3,3,3,7]],'Index multiplicities produce fifteen good pairs.')],[[x] for x in [[1,3,5,7,9],[1,1,1,3,3,3,7],[0],[0,1],[0,0],[1,1],[1,2],[2,2],[1,7],[3,5],[0,8,8],[4,4,4],[2,6,10,14],[1,15,17,31]]],MEALS,[MEALS.replace('range(22)','range(1,22)'),MEALS.replace('counts[value]+=1','counts[value]=1')],['Omits the valid power-of-two target one.','Stores presence rather than multiplicity of prior values.'],meals_o,rmeals,L('When processing one value, every earlier complement for each power of two forms one new pair.','Count prior values and query power-value across the finite power range.','Add counts[2^bit-value] for each bit, then increment this value; reduce the total modulo M.','Each unordered index pair is counted once when its later endpoint arrives and exactly for its unique sum.'),'O(n log maxValue)','O(n)',5),
}
BATCH[1701]['comparator']='float'
