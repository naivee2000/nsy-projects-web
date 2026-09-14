"""First half of batch 96: arithmetic, masks, remainders, and monotonic queues."""
from collections import Counter,deque
from functools import lru_cache
from itertools import combinations
from .import_batch_055 import entry
MOD=1_000_000_007
def avg_o(a):
 x=a[0];return (sum(x)-min(x)-max(x))/(len(x)-2)
def factor_o(a):
 n,k=a;v=[x for x in range(1,n+1) if n%x==0];return v[k-1] if k<=len(v) else -1
def ones_o(a):
 x=a[0];return max(sum(x[i:j])-0 for i in range(len(x)) for j in range(i+1,len(x)+1) if (j-i)-sum(x[i:j])<=1)-1 if all(x) else max(j-i-1 for i in range(len(x)) for j in range(i+1,len(x)+1) if (j-i)-sum(x[i:j])<=1)
def courses_o(a):
 n,relations,k=a;need=[0]*n
 for x,y in relations:need[y-1]|=1<<(x-1)
 @lru_cache(None)
 def solve(mask):
  if mask==(1<<n)-1:return 0
  ready=[i for i in range(n) if not mask>>i&1 and need[i]&mask==need[i]];best=n
  for size in range(1,min(k,len(ready))+1):
   for chosen in combinations(ready,size):best=min(best,1+solve(mask|sum(1<<i for i in chosen)))
  return best
 return solve(0)
def cross_o(a):
 x=y=0;seen={(0,0)}
 for c in a[0]:dx,dy={'N':(0,1),'S':(0,-1),'E':(1,0),'W':(-1,0)}[c];x+=dx;y+=dy;seen.add((x,y))
 return len(seen)<len(a[0])+1
def pairs_o(a):
 arr,k=a;c=Counter(x%k for x in arr)
 return c[0]%2==0 and all(c[r]==c[k-r] for r in range(1,k))
def subs_o(a):
 nums,target=a;answer=0
 for mask in range(1,1<<len(nums)):
  values=[nums[i] for i in range(len(nums)) if mask>>i&1]
  answer+=min(values)+max(values)<=target
 return answer%MOD
def equation_o(a):
 p,k=a;return max(y1+y2+x2-x1 for i,(x1,y1) in enumerate(p) for x2,y2 in p[i+1:] if x2-x1<=k)
def progression_o(a):
 x=sorted(a[0]);return all(x[i]-x[i-1]==x[1]-x[0] for i in range(2,len(x)))
def ants_o(a):
 n,left,right=a;return max([0]+left+[n-x for x in right])
def ravg(r):return [r.sample(range(1000,10000),r.randint(3,20))]
def rfactor(r):return [r.randint(1,200),r.randint(1,30)]
def rones(r):return [[r.randint(0,1) for _ in range(r.randint(1,30))]]
def rcourse(r):
 n=r.randint(1,8);order=list(range(1,n+1));r.shuffle(order);rels=[]
 for i in range(n):
  for j in range(i+1,n):
   if r.random()<.15:rels.append([order[i],order[j]])
 return [n,rels,r.randint(1,n)]
def rcross(r):return [''.join(r.choice('NSEW') for _ in range(r.randint(1,40)))]
def rpairs(r):
 n=2*r.randint(1,15);return [[r.randint(-30,30) for _ in range(n)],r.randint(1,12)]
def rsubs(r):return [[r.randint(1,20) for _ in range(r.randint(1,10))],r.randint(2,30)]
def requation(r):
 xs=sorted(r.sample(range(0,50),r.randint(2,10)));gap=min(b-a for a,b in zip(xs,xs[1:]));return [[[x,r.randint(-20,20)] for x in xs],r.randint(gap,max(gap,30))]
def rprog(r):return [[r.randint(-30,30) for _ in range(r.randint(2,20))]]
def rants(r):
 n=r.randint(1,30);positions=list(range(n+1));r.shuffle(positions);cut=r.randint(0,len(positions));return [n,positions[:cut],positions[cut:]]
AVG='''def average_middle_salary(salary):
 return (sum(salary)-min(salary)-max(salary))/(len(salary)-2)
'''
FACTOR='''def kth_factor(n, k):
 for value in range(1,n+1):
  if n%value==0:k-=1
  if k==0:return value
 return -1
'''
ONES='''def longest_ones_after_one_deletion(nums):
 left=zeros=answer=0
 for right,value in enumerate(nums):
  zeros+=value==0
  while zeros>1:zeros-=nums[left]==0;left+=1
  answer=max(answer,right-left)
 return answer
'''
COURSES='''def minimum_course_semesters(n, relations, k):
 from functools import lru_cache
 requirements=[0]*n
 for before,after in relations:requirements[after-1]|=1<<(before-1)
 @lru_cache(None)
 def solve(mask):
  if mask==(1<<n)-1:return 0
  available=0
  for course in range(n):
   if not mask>>course&1 and requirements[course]&mask==requirements[course]:available|=1<<course
  choices=[];subset=available
  while subset:
   if subset.bit_count()<=k:choices.append(subset)
   subset=(subset-1)&available
  return 1+min(solve(mask|chosen) for chosen in choices)
 return solve(0)
'''
COURSES_NO_EDGES='''def minimum_course_semesters(n, relations, k):
 return (n+k-1)//k
'''
CROSS='''def path_crosses_itself(path):
 x=y=0;seen={(0,0)};moves={'N':(0,1),'S':(0,-1),'E':(1,0),'W':(-1,0)}
 for char in path:
  dx,dy=moves[char];x+=dx;y+=dy
  if (x,y) in seen:return True
  seen.add((x,y))
 return False
'''
PAIRS='''def can_pair_divisible(arr, k):
 from collections import Counter
 counts=Counter(value%k for value in arr)
 if counts[0]%2:return False
 return all(counts[r]==counts[k-r] for r in range(1,k))
'''
PAIRS_NO_ZERO='''def can_pair_divisible(arr, k):
 from collections import Counter
 counts=Counter(value%k for value in arr)
 return all(counts[r]==counts[k-r] for r in range(1,k))
'''
SUBS='''def count_bounded_subsequences(nums, target):
 nums=sorted(nums);powers=[1]*len(nums)
 for i in range(1,len(nums)):powers[i]=powers[i-1]*2%1000000007
 left,right=0,len(nums)-1;answer=0
 while left<=right:
  if nums[left]+nums[right]<=target:answer=(answer+powers[right-left])%1000000007;left+=1
  else:right-=1
 return answer
'''
EQUATION='''def maximum_point_equation(points, k):
 queue=deque();answer=-10**18
 for x,y in points:
  while queue and x-queue[0][0]>k:queue.popleft()
  if queue:answer=max(answer,x+y+queue[0][1])
  value=y-x
  while queue and queue[-1][1]<=value:queue.pop()
  queue.append((x,value))
 return answer
'''
PROGRESSION='''def can_form_arithmetic_progression(arr):
 arr=sorted(arr);difference=arr[1]-arr[0]
 return all(arr[i]-arr[i-1]==difference for i in range(2,len(arr)))
'''
ANTS='''def last_ant_fall_moment(n, left, right):
 return max([0]+left+[n-position for position in right])
'''
E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1491:S('average_middle_salary',[('salary','list[int]')],'float',['arrays','math'],['At least three distinct salaries are provided.','Return the average after excluding one minimum and one maximum.'],[([[4000,3000,1000,2000]],'Removing one thousand and four thousand leaves average 2500.'),([[1000,2000,3000]],'The single middle salary is two thousand.')],[[x] for x in [[1,2,3],[4000,3000,1000,2000],[1000,2000,3000],[5,1,9,3],[10,20,30,40,50],[1,100,50],[7,9,11,13],[100,200,400,800],[2,4,8,16],[999,1000,1001],[3,10,20,30],[12,15,18,21],[50,60,70,90],[1000,5000,9000,7000]]],AVG,[AVG.replace('-min(salary)','+min(salary)'),AVG.replace('len(salary)-2','len(salary)')],['Adds the minimum instead of excluding it.','Divides by the original count.'],avg_o,ravg,['Subtract the unique minimum and maximum from the total.','The remaining count is len-2.','Divide remaining sum by remaining count.','Distinctness ensures exactly the intended two entries are removed.'],'O(n)','O(1)',3),
1492:S('kth_factor',[('n','int'),('k','int')],'int',['math','enumeration'],['Positive factors are ordered increasingly.','Return the kth one, or -1 when fewer than k factors exist.'],[([12,3],'The factors 1,2,3 make three the third.'),([7,2],'The factors of seven are one and seven.')],[[n,k] for n,k in [(1,1),(1,2),(2,1),(2,2),(12,3),(12,6),(12,7),(7,2),(16,4),(36,5),(100,9),(25,3),(30,8),(49,2)]],FACTOR,[FACTOR.replace('range(1,n+1)','range(2,n+1)'),FACTOR.replace('k-=1','k-=2')],['Skips factor one.','Advances the rank twice per factor.'],factor_o,rfactor,['Scan candidate values from one through n.','Decrement k whenever a candidate divides n.','Return when k reaches zero.','Increasing scan order makes that divisor exactly the requested rank.'],'O(n)','O(1)',5),
1493:S('longest_ones_after_one_deletion',[('nums','list[int]')],'int',['sliding-window','arrays'],['Delete exactly one element.','Return the longest remaining contiguous subarray containing only ones.'],[([[1,1,0,1]],'Deleting the zero joins three ones.'),([[1,1,1]],'A deletion is mandatory, leaving two ones.')],[[x] for x in [[0],[1],[1,1],[0,0],[1,1,0,1],[1,1,1],[0,1,1],[1,1,0,1,1,1,0,1,1],[1,0,1],[0,1,0],[1,0,0,1],[0,0,1,1],[1,1,0,0],[1,0,1,1,0,1]]],ONES,[ONES.replace('zeros>1','zeros>=1'),ONES.replace('right-left','right-left+1')],['Allows no zero in the maintained window.','Forgets that one element must be deleted from the window.'],ones_o,rones,['Maintain a window containing at most one zero.','Shrink from the left when a second zero enters.','Window length minus one is the number of ones after deleting its zero or one mandatory element.','Every feasible joined run is represented by such a window.'],'O(n)','O(1)',5),
1494:S('minimum_course_semesters',[('n','int'),('relations','list[list[int]]'),('k','int')],'int',['dynamic-programming','bit-masks'],['Relations form a DAG of prerequisites.','Take at most k currently available courses per semester and minimize semesters.'],[([4,[[2,1],[3,1],[1,4]],2],'Courses two and three precede one, then course four, requiring three semesters.'),([5,[[2,1],[3,1],[4,1],[1,5]],2],'Two prerequisite courses can be taken per initial semester, producing four semesters total.')],[[n,e,k] for n,e,k in [(1,[],1),(2,[],1),(2,[],2),(2,[[1,2]],2),(4,[[2,1],[3,1],[1,4]],2),(5,[[2,1],[3,1],[4,1],[1,5]],2),(4,[],3),(4,[[1,3],[2,3]],2),(6,[[1,4],[2,4],[3,5],[4,6],[5,6]],2),(3,[[1,2],[2,3]],1),(5,[],5),(5,[[1,5],[2,5],[3,5],[4,5]],2),(6,[[1,3],[2,3],[3,4],[3,5]],3),(7,[[1,4],[2,4],[3,5],[4,6],[5,6],[6,7]],2)]],COURSES,[COURSES.replace('<=k','<k'),COURSES_NO_EDGES],['Refuses to take exactly k courses in a semester.','Ignores prerequisite relations and batches courses only by count.'],courses_o,rcourse,['Encode completed courses as a bit mask.','Derive all unfinished courses whose prerequisite masks are contained in it.','Try every available subset of size at most k and memoize the best remaining semesters.','Every legal semester choice appears once; mask contains all history relevant to future availability.'],'O(3^n)','O(2^n)',8),
1496:S('path_crosses_itself',[('path','str')],'bool',['hash-maps','simulation'],['Start at coordinate (0,0) and move one unit per N,S,E,W character.','Return whether any coordinate is visited more than once.'],[(['NES'],'The visited coordinates are all distinct.'),(['NESWW'],'The final west move revisits an earlier coordinate.')],[[s] for s in ['N','NS','NES','NESW','NESWW','NNNN','EW','NSE','SSEN','NENW','EEEEW','NSNS','WNES','SSEEWWNN']],CROSS,[CROSS.replace('if (x,y) in seen:return True','if (x,y) not in seen:return True'),CROSS.replace('seen.add((x,y))','')],['Reports a crossing at every new coordinate.','Never records positions after the origin.'],cross_o,rcross,['Store the origin in a visited set.','Update coordinates for each move.','Return true before adding if the new coordinate is already visited.','The set contains exactly the path prefix positions, so membership detects every revisit.'],'O(n)','O(n)',3),
1497:S('can_pair_divisible',[('arr','list[int]'),('k','int')],'bool',['counting','modular-arithmetic'],['arr has even length and may contain negatives.','Partition all occurrences into pairs whose sums are divisible by k.'],[([[1,2,3,4,5,10,6,7,8,9],5],'Complementary remainder counts match, including the zero-remainder pair.'),([[1,2,3,4,5,6],7],'Remainders one through six pair complementarily.')],[[a,k] for a,k in [([1,1],2),([1,2],2),([1,2,3,4,5,10,6,7,8,9],5),([1,2,3,4,5,6],7),([1,2,3,4,5,6],10),([-1,1],5),([-1,-4],5),([0,0],3),([0,1],3),([2,2,2,2],4),([2,2,2,6],4),([1,3,2,2],4),([5,10,15,20],5),([-3,3,-2,2],6)]],PAIRS,[PAIRS_NO_ZERO,PAIRS.replace('counts[k-r]','counts[r]')],['Does not require zero-remainder occurrences to pair evenly.','Compares each remainder count with itself.'],pairs_o,rpairs,['Normalize every value by value modulo k.','Remainder zero must occur evenly; when k is even, k/2 is covered by the same equality and must pair internally.','Every other remainder r needs one k-r occurrence.','Matching all complementary counts is necessary and lets each bucket be paired exhaustively.'],'O(n+k)','O(k)',5),
1498:S('count_bounded_subsequences',[('nums','list[int]'),('target','int')],'int',['two-pointers','sorting'],['Count non-empty subsequences whose minimum plus maximum is at most target.','Return modulo 1,000,000,007; order within a subsequence follows input but only selected values affect validity.'],[([[3,5,6,7],9],'Four valid subsequences have minimum plus maximum at most nine.'),([[3,3,6,8],10],'Six subsequences meet the bound.')],[[a,t] for a,t in [([1],2),([2],3),([3,5,6,7],9),([3,3,6,8],10),([2,3,3,4,6,7],12),([5,5],10),([5,5],9),([1,2,3],4),([1,2,3],6),([10,1,1],11),([1,1,1,1],2),([4,2,5,1],6),([7,8,9],20),([2,4,6,8],8)]],SUBS,[SUBS.replace('powers[right-left]','powers[right-left-1]'),SUBS.replace('left<=right','left<right')],['Uses one fewer free middle choice for each valid minimum.','Omits singleton subsequences.'],subs_o,rsubs,['Sort values and precompute powers of two.','With endpoints left and right, if their sum fits, every subset of the middle values paired with nums[left] is valid.','Add 2^(right-left) and advance left; otherwise decrease right.','Each subsequence is counted under its unique smallest sorted selected index.'],'O(n log n)','O(n)',5),
1499:S('maximum_point_equation',[('points','list[list[int]]'),('k','int')],'int',['monotonic-queue','geometry'],['Points have strictly increasing x coordinates and at least one eligible pair.','Maximize yi+yj+|xi-xj| over i<j with xj-xi<=k.'],[([[[1,3],[2,0],[5,10],[6,-10]],1],'Only adjacent-distance-one pairs qualify; the first pair gives four.'),([[[0,0],[3,0],[9,2]],3],'The first two points give value three.')],[[p,k] for p,k in [([[0,0],[1,0]],1),([[1,3],[2,0],[5,10],[6,-10]],1),([[0,0],[3,0],[9,2]],3),([[0,5],[2,4]],2),([[1,-1],[2,-2]],1),([[0,0],[5,10],[6,1]],6),([[1,10],[3,5],[4,20]],3),([[0,-5],[2,10],[4,-1]],4),([[1,1],[2,2],[3,3]],2),([[0,100],[10,0]],10),([[2,-10],[3,20]],1),([[0,0],[1,100],[2,0]],2),([[5,5],[8,8],[9,1]],4),([[-5,2],[-2,7],[0,3]],5)]],EQUATION,[EQUATION.replace('y-x','y+x'),EQUATION.replace('>k','>=k')],['Stores y+x rather than y-x for prior points.','Expires pairs exactly at the allowed distance k.'],equation_o,requation,['For i<j, the equation becomes (yi-xi)+(yj+xj).','Maintain eligible prior yi-xi values in decreasing order.','Expire points farther than k before using the deque front, then insert the current transformed value monotonically.','The front is the maximum valid prior contribution for each j.'],'O(n)','O(n)',8),
1502:S('can_form_arithmetic_progression',[('arr','list[int]')],'bool',['sorting','arrays'],['Rearrange all values if possible.','Return whether consecutive values can have one common difference.'],[([[3,5,1]],'Sorted values 1,3,5 have constant difference two.'),([[1,2,4]],'Sorted differences one and two do not match.')],[[x] for x in [[1,2],[3,5,1],[1,2,4],[7,7,7],[0,-1,1],[-5,-1,3],[10,0,5],[1,3,3,5],[100,50,0],[-3,-2,-1,0],[2,4,8,6],[9,1,5,13],[0,0,1],[6,2,4]]],PROGRESSION,[PROGRESSION.replace('sorted(arr)','arr'),PROGRESSION.replace('==difference','<=difference')],['Checks only the provided order without rearranging.','Accepts nonconstant differences no larger than the first.'],progression_o,rprog,['Sort the values.','Compute the first adjacent difference.','Require every later adjacent difference to equal it.','A sorted arithmetic progression has this property, and any rearrangeable progression sorts into exactly that order.'],'O(n log n)','O(n)',3),
1503:S('last_ant_fall_moment',[('n','int'),('left','list[int]'),('right','list[int]')],'int',['math','simulation'],['Ants move at unit speed; on collision they reverse direction.','Return the last fall time for left-moving and right-moving starting positions.'],[([4,[4,3],[0,1]],'A left-moving ant at four takes four seconds, the maximum.'),([7,[],[0,1,2,3,4,5,6,7]],'The right-moving ant at zero takes seven seconds.')],[[n,l,r] for n,l,r in [(1,[0],[]),(1,[],[1]),(4,[4,3],[0,1]),(7,[],[0,1,2,3,4,5,6,7]),(7,[0,1,2,3,4,5,6,7],[]),(10,[2,6],[3,7]),(5,[2],[2]),(9,[1,8],[4]),(20,[19],[1]),(3,[],[0]),(3,[3],[]),(8,[2,4,6],[1,3,5]),(100,[50],[50]),(6,[0,6],[]) ]],ANTS,[ANTS.replace('n-position','position'),ANTS.replace('[0]+left','[0]')],['Uses starting position instead of distance to the right edge.','Ignores every left-moving ant.'],ants_o,rants,['Colliding identical-speed ants can be viewed as passing through each other because identities do not affect fall times.','A left-moving ant falls after its position; a right-moving one after n-position.','Take the maximum of all such distances.','The pass-through equivalence preserves the multiset of positions and directions after each collision.'],'O(ants)','O(1)',5),
}
BATCH[1491]['comparator']='float'
