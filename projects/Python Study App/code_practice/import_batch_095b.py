"""Second half of batch 95: interval DP, binary search, and frequency tasks."""
from collections import Counter
from functools import lru_cache
from itertools import product
from .import_batch_055 import entry

def strong_o(a):
 arr,k=a;median=sorted(arr)[(len(arr)-1)//2];return sorted(arr,key=lambda x:(abs(x-median),x),reverse=True)[:k]
def paint_o(a):
 houses,cost,m,n,target=a;best=10**18
 for colors in product(range(1,n+1),repeat=houses.count(0)):
  result=[];it=iter(colors);total=0
  for i,color in enumerate(houses):
   chosen=color or next(it);result.append(chosen);total+=0 if color else cost[i][chosen-1]
  if 1+sum(x!=y for x,y in zip(result,result[1:]))==target:best=min(best,total)
 return -1 if best==10**18 else best
def prices_o(a):
 p=a[0];return [x-next((y for y in p[i+1:] if y<=x),0) for i,x in enumerate(p)]
def subarrays_o(a):
 arr,target=a;intervals=[(i,j) for i in range(len(arr)) for j in range(i+1,len(arr)+1) if sum(arr[i:j])==target];best=min((b-a+d-c for a,b in intervals for c,d in intervals if b<=c or d<=a),default=10**9);return -1 if best==10**9 else best
def mail_o(a):
 houses,k=a;h=sorted(houses)
 def cost(i,j):
  med=h[(i+j)//2];return sum(abs(h[x]-med) for x in range(i,j+1))
 @lru_cache(None)
 def solve(i,boxes):
  if boxes==1:return cost(i,len(h)-1)
  return min(cost(i,j)+solve(j+1,boxes-1) for j in range(i,len(h)-boxes+1))
 return solve(0,k)
def running_o(a):
 total=0;out=[]
 for x in a[0]:total+=x;out.append(total)
 return out
def unique_o(a):
 arr,k=a;counts=Counter(arr)
 for x in sorted(counts,key=counts.get):
  if counts[x]<=k:k-=counts[x];del counts[x]
  else:break
 return len(counts)
def bouquets_o(a):
 bloom,m,k=a
 if m*k>len(bloom):return -1
 for day in sorted(set(bloom)):
  flowers=made=0
  for value in bloom:
   flowers=flowers+1 if value<=day else 0
   if flowers==k:made+=1;flowers=0
  if made>=m:return day
def xor_o(a):
 n,start=a;answer=0
 for i in range(n):answer^=start+2*i
 return answer
def names_o(a):
 used=set();out=[]
 for name in a[0]:
  candidate=name;suffix=1
  while candidate in used:candidate=f'{name}({suffix})';suffix+=1
  used.add(candidate);out.append(candidate)
 return out

def rstrong(r):
 arr=[r.randint(-30,30) for _ in range(r.randint(1,20))];return [arr,r.randint(1,len(arr))]
def rpaint(r):
 m,n=r.randint(1,6),r.randint(1,3);houses=[0 if r.random()<.7 else r.randint(1,n) for _ in range(m)];return [houses,[[r.randint(1,10) for _ in range(n)] for _ in range(m)],m,n,r.randint(1,m)]
def rprices(r):return [[r.randint(1,50) for _ in range(r.randint(1,25))]]
def rsub(r):return [[r.randint(1,10) for _ in range(r.randint(2,20))],r.randint(1,25)]
def rmail(r):
 n=r.randint(1,8);return [r.sample(range(1,50),n),r.randint(1,n)]
def rrun(r):return [[r.randint(-20,20) for _ in range(r.randint(1,30))]]
def runique(r):
 arr=[r.randint(0,12) for _ in range(r.randint(1,30))];return [arr,r.randint(0,len(arr))]
def rbloom(r):
 v=[r.randint(1,30) for _ in range(r.randint(1,25))];return [v,r.randint(1,10),r.randint(1,8)]
def rxor(r):return [r.randint(1,100),r.randint(0,100)]
def rnames(r):
 base=['a','b','x','file','doc','a(1)'];return [[r.choice(base) for _ in range(r.randint(1,25))]]

STRONG='''def strongest_values(arr, k):
 median=sorted(arr)[(len(arr)-1)//2]
 return sorted(arr,key=lambda value:(abs(value-median),value),reverse=True)[:k]
'''
PAINT='''def minimum_house_paint_cost(houses, cost, m, n, target):
 from functools import lru_cache
 inf=10**15
 @lru_cache(None)
 def solve(index,previous,groups):
  if groups>target:return inf
  if index==m:return 0 if groups==target else inf
  choices=[houses[index]] if houses[index] else range(1,n+1);answer=inf
  for color in choices:
   price=0 if houses[index] else cost[index][color-1]
   answer=min(answer,price+solve(index+1,color,groups+(color!=previous)))
  return answer
 result=solve(0,0,0);return -1 if result==inf else result
'''
PRICES='''def final_discounted_prices(prices):
 answer=prices[:];stack=[]
 for index,value in enumerate(prices):
  while stack and prices[stack[-1]]>=value:old=stack.pop();answer[old]-=value
  stack.append(index)
 return answer
'''
SUBARRAYS='''def minimum_two_target_subarrays(arr, target):
 n=len(arr);best=[10**9]*n;left=total=0;shortest=answer=10**9
 for right,value in enumerate(arr):
  total+=value
  while total>target:total-=arr[left];left+=1
  if total==target:
   length=right-left+1
   if left>0:answer=min(answer,length+best[left-1])
   shortest=min(shortest,length)
  best[right]=shortest
 return -1 if answer==10**9 else answer
'''
MAIL='''def allocate_mailboxes(houses, k):
 from functools import lru_cache
 houses=sorted(houses);n=len(houses)
 def segment(left,right):
  median=houses[(left+right)//2]
  return sum(abs(houses[i]-median) for i in range(left,right+1))
 @lru_cache(None)
 def solve(left,boxes):
  if boxes==1:return segment(left,n-1)
  return min(segment(left,right)+solve(right+1,boxes-1) for right in range(left,n-boxes+1))
 return solve(0,k)
'''
RUNNING='''def running_sum(nums):
 answer=[];total=0
 for value in nums:total+=value;answer.append(total)
 return answer
'''
UNIQUE='''def least_unique_after_removals(arr, k):
 from collections import Counter
 frequencies=sorted(Counter(arr).values());remaining=len(frequencies)
 for count in frequencies:
  if count>k:break
  k-=count;remaining-=1
 return remaining
'''
BOUQUETS='''def minimum_bouquet_day(bloom_day, m, k):
 if m*k>len(bloom_day):return -1
 def possible(day):
  consecutive=made=0
  for bloom in bloom_day:
   consecutive=consecutive+1 if bloom<=day else 0
   if consecutive==k:made+=1;consecutive=0
  return made>=m
 low,high=min(bloom_day),max(bloom_day)
 while low<high:
  middle=(low+high)//2
  if possible(middle):high=middle
  else:low=middle+1
 return low
'''
XOR='''def xor_sequence_operation(n, start):
 answer=0
 for i in range(n):answer^=start+2*i
 return answer
'''
NAMES='''def unique_folder_names(names):
 next_suffix={};answer=[]
 for name in names:
  if name not in next_suffix:answer.append(name);next_suffix[name]=1;continue
  suffix=next_suffix[name]
  while f'{name}({suffix})' in next_suffix:suffix+=1
  candidate=f'{name}({suffix})';answer.append(candidate);next_suffix[name]=suffix+1;next_suffix[candidate]=1
 return answer
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1471:S('strongest_values',[('arr','list[int]'),('k','int')],'list[int]',['sorting','arrays'],['Median is sorted_arr[(n-1)//2].','Strength compares absolute distance from median, breaking ties by larger value; return any order of the k strongest occurrences.'],[([[1,2,3,4,5],2],'Median three makes five and one strongest, with five first under the tie rule.'),([[1,1,3,5,5],2],'The two fives are the two strongest occurrences.')],[[a,k] for a,k in [([1],1),([1,2],1),([1,2,3,4,5],2),([1,1,3,5,5],2),([6,7,11,7,6,8],5),([-7,22,17,3],2),([5,5,5],2),([-5,-1,0,4,9],3),([10,1,2,3],4),([2,8,3,5,1],3),([0,0,1,-1],2),([100,-100,0],1),([4,4,2,2,3],4),([9,8,7,6,5,4],2)]],STRONG,[STRONG.replace('(abs(value-median),value)','(abs(value-median),-value)'),STRONG.replace('(len(arr)-1)//2','len(arr)//2')],['Breaks equal strengths in favor of smaller values.','Uses the upper rather than required lower median for even lengths.'],strong_o,rstrong,['Sort a copy to obtain the specified lower median.','Rank each occurrence by the pair (absolute distance from median, value).','Sort descending and take the first k.','The tuple encodes the primary strength and exact tie-break rule; duplicates remain separate occurrences.'],'O(n log n)','O(n)',5),
1473:S('minimum_house_paint_cost',[('houses','list[int]'),('cost','list[list[int]]'),('m','int'),('n','int'),('target','int')],'int',['dynamic-programming','memoization'],['Zero houses are unpainted; positive values are fixed colors 1..n and cost nothing.','A neighborhood is a maximal same-color run; reach exactly target at minimum added cost, or -1.'],[([ [0,0,0,0,0],[[1,10],[10,1],[10,1],[1,10],[5,1]],5,2,3],'Painting colors 1,2,2,1,1 costs nine and forms three neighborhoods.'),([ [0,2,1,2,0],[[1,10],[10,1],[10,1],[1,10],[5,1]],5,2,3],'The fixed middle colors permit a minimum-cost exact-three-neighborhood completion.')],[[h,c,m,n,t] for h,c,m,n,t in [([0],[[5,1]],1,2,1),([1],[[5,1]],1,2,1),([1],[[5,1]],1,2,2),([0,0],[[1,2],[2,1]],2,2,1),([0,0],[[1,2],[2,1]],2,2,2),([0,0,0,0,0],[[1,10],[10,1],[10,1],[1,10],[5,1]],5,2,3),([0,2,1,2,0],[[1,10],[10,1],[10,1],[1,10],[5,1]],5,2,3),([3,1,2,3],[[1,1,1]]*4,4,3,4),([3,1,2,3],[[1,1,1]]*4,4,3,3),([0,1,0],[[2,3],[1,1],[3,2]],3,2,3),([0,1,0],[[2,3],[1,1],[3,2]],3,2,1),([2,2,0,1],[[1,2],[1,2],[5,1],[1,2]],4,2,2),([0,0,0],[[1,5],[1,5],[1,5]],3,2,1),([0,0,0],[[1,5],[1,5],[1,5]],3,2,3)]],PAINT,[PAINT.replace('color!=previous','color==previous'),PAINT.replace('price=0 if houses[index]','price=cost[index][color-1] if houses[index]')],['Increments neighborhoods when adjacent colors match rather than change.','Charges repainting cost for houses that are already painted.'],paint_o,rpaint,['Memoize by house index, previous color, and neighborhoods formed.','Fixed houses offer one zero-cost color; unpainted houses offer every color with its listed cost.','Increment the group count only when chosen color differs from previous.','The state preserves all history affecting future neighborhoods, and minimizing all legal choices yields the optimum.'],'O(m*n*target)','O(m*n*target)',8),
1475:S('final_discounted_prices',[('prices','list[int]')],'list[int]',['stacks','arrays'],['For each price, subtract the first later price less than or equal to it.','Leave the price unchanged when no later discount qualifies.'],[([[8,4,6,2,3]],'Discounts four, two, two, none, none produce 4,2,4,2,3.'),([[1,2,3,4,5]],'No later value is less than or equal to an earlier one.')],[[x] for x in [[1],[8,4,6,2,3],[1,2,3,4,5],[10,1,1,6],[5,5],[5,4,3,2,1],[1,2,1],[9,7,8,3],[2,3,2,1],[100,20,30,10],[4,1,2,4],[6,6,6],[3,1,3,1],[8,2,4,6,1]]],PRICES,[PRICES.replace('>=value','>value'),PRICES.replace('while stack','if stack')],['Requires a strictly smaller discount and misses equal prices.','Discounts only one waiting price instead of every prior price resolved by the current value.'],prices_o,rprices,['Keep indices whose first qualifying later price has not appeared.','Maintain their prices in increasing stack order by resolving while top price >= current.','Subtract the current price from every popped index.','An index is popped at its first qualifying later value, exactly matching the discount definition.'],'O(n)','O(n)',3),
1477:S('minimum_two_target_subarrays',[('arr','list[int]'),('target','int')],'int',['sliding-window','dynamic-programming'],['arr contains positive integers.','Choose two non-overlapping subarrays each summing to target and minimize their combined lengths; return -1 if impossible.'],[([[3,2,2,4,3],3],'The two singleton threes are disjoint and have total length two.'),([[7,3,4,7],7],'The two singleton sevens give total length two.')],[[a,t] for a,t in [([1,1],1),([3,2,2,4,3],3),([7,3,4,7],7),([4,3,2,6,2,3,4],6),([5,5,4,4,5],3),([1,2,2,3,2,1],3),([1,1,1,1],2),([2,2,2],2),([1,2,3,4,5],5),([5,1,1,5],6),([1,6,1,6],7),([3,3,3],6),([2,1,2,1,2],3),([10,1,9,10],10)]],SUBARRAYS,[SUBARRAYS.replace('best[left-1]','best[right-1]'),SUBARRAYS.replace('shortest=min(shortest,length)','shortest=length')],['Combines with a potentially overlapping best interval ending near the current right edge.','Forgets shorter earlier intervals and stores only the latest target window.'],subarrays_o,rsub,['Positive values allow one sliding window to find every target-sum interval.','Store at each index the shortest target interval ending at or before it.','When a new interval starts at left, combine it with the stored best through left-1.','This considers every right-hand interval with the optimal non-overlapping left partner.'],'O(n)','O(n)',5),
1478:S('allocate_mailboxes',[('houses','list[int]'),('k','int')],'int',['dynamic-programming','sorting'],['Place k mailboxes anywhere to minimize the sum of each house’s distance to its nearest mailbox.','House positions are distinct and k does not exceed their count.'],[([[1,4,8,10,20],3],'Grouping 1,4; 8,10; and 20 costs 3+2+0=5.'),([[2,3,5,12,18],2],'Optimal contiguous groups around their medians have total distance nine.')],[[h,k] for h,k in [([1],1),([1,10],1),([1,10],2),([1,4,8,10,20],3),([2,3,5,12,18],2),([7,4,6,1],1),([7,4,6,1],4),([1,2,3,100],2),([1,5,9,13],2),([10,20,30],2),([1,3,6,10,15],3),([2,8,14,20],1),([5,6,7,8,9],2),([1,50,51,100],2)]],MAIL,[MAIL.replace('(left+right)//2','left'),MAIL.replace('return solve(0,k)','return solve(0,max(1,k-1))')],['Places each segment mailbox at its leftmost house instead of a median.','Uses one fewer mailbox than requested whenever k is greater than one.'],mail_o,rmail,['Sort houses; an optimal nearest-mailbox assignment forms contiguous groups.','One group’s distance sum is minimized by a median house.','DP by leftmost unassigned house and remaining mailbox count, trying every valid group endpoint.','Every contiguous partition is considered, and each segment cost is independently optimal at its median.'],'O(k*n³)','O(k*n)',8),
1480:S('running_sum',[('nums','list[int]')],'list[int]',['arrays','prefix-sums'],['Output position i is the sum of nums[0] through nums[i].','Preserve output order and length.'],[([[1,2,3,4]],'Cumulative totals are 1,3,6,10.'),([[3,1,2,10,1]],'Successive prefix sums are 3,4,6,16,17.')],[[x] for x in [[1],[0],[-1],[1,2],[1,2,3,4],[3,1,2,10,1],[-1,1,-1,1],[5,5,5],[10,-5,-5],[0,0,0],[100,-50,25],[-3,-2,-1],[1,-2,3,-4],[2,4,6,8,10]]],RUNNING,[RUNNING.replace('total+=value','total=value'),RUNNING.replace('answer.append(total)','answer.insert(0,total)')],['Resets the total at each element instead of accumulating.','Returns prefix sums in reverse order.'],running_o,rrun,['Maintain a cumulative total initialized to zero.','Add each input value and append the updated total.','Continue in input order.','After index i, the invariant total=sum(nums[:i+1]) proves every emitted value.'],'O(n)','O(n)',3),
1481:S('least_unique_after_removals',[('arr','list[int]'),('k','int')],'int',['greedy','counting'],['Remove exactly k array occurrences.','Return the minimum possible number of distinct integers remaining.'],[([[5,5,4],1],'Removing the lone four leaves only value five.'),([[4,3,1,1,3,3,2],3],'Removing singleton two and four plus one remaining occurrence leaves two distinct values.')],[[a,k] for a,k in [([1],0),([1],1),([5,5,4],1),([4,3,1,1,3,3,2],3),([1,2,3],1),([1,1,2,2],2),([1,1,1,2],2),([0,0,1,2,2],2),([5,4,3,2,1],5),([1,2,2,3,3,3],3),([7,7,8,8,9],1),([10,10,10],2),([1,1,2,3,4,4],3),([2,2,2,3,3,4],4)]],UNIQUE,[UNIQUE.replace('sorted(Counter(arr).values())','sorted(Counter(arr).values(),reverse=True)'),UNIQUE.replace('if count>k:break','if count>=k:break')],['Removes the most frequent values first.','Refuses to remove a value whose frequency exactly equals remaining k.'],unique_o,runique,['Count occurrences of every distinct value.','Removing all occurrences of a value is the only way to reduce the distinct count.','Spend removals on frequencies from smallest upward while affordable.','This greedy order eliminates the most distinct values per removal; leftover partial removal cannot reduce the count.'],'O(n log n)','O(n)',5),
1482:S('minimum_bouquet_day',[('bloom_day','list[int]'),('m','int'),('k','int')],'int',['binary-search','greedy'],['A bouquet needs k adjacent flowers bloomed by the chosen day, and flowers cannot be reused.','Return the earliest day for m bouquets, or -1 when there are too few flowers.'],[([[1,10,3,10,2],3,1],'By day three, flowers at days one, three, and two make three single-flower bouquets.'),([[1,10,3,10,2],3,2],'Six flowers would be required but only five exist, so return -1.')],[[b,m,k] for b,m,k in [([1],1,1),([1],2,1),([1,10,3,10,2],3,1),([1,10,3,10,2],3,2),([7,7,7,7,12,7,7],2,3),([1000000000,1000000000],1,1),([1,2,3,4],1,4),([1,2,3,4],2,2),([5,1,5,1,5],2,1),([5,1,5,1,5],2,2),([2,2,2,2],2,2),([3,1,2,4,5,6],2,2),([10,9,8,7,6],1,3),([1,100,1,100,1],3,1)]],BOUQUETS,[BOUQUETS.replace('bloom<=day','bloom<day'),BOUQUETS.replace('consecutive=0','consecutive=1')],['Treats flowers blooming exactly on the tested day as unavailable.','Reuses one flower from each completed bouquet as the start of the next run.'],bouquets_o,rbloom,['Feasibility by a fixed day is monotone as the day increases.','Scan consecutive bloomed flowers, consuming each full run of k as one bouquet.','Binary-search the first feasible day between minimum and maximum bloom values.','The greedy scan maximizes disjoint adjacent bouquets for a day, and monotonicity makes lower-bound search valid.'],'O(n log range)','O(1)',5),
1486:S('xor_sequence_operation',[('n','int'),('start','int')],'int',['bit-manipulation','arrays'],['Define nums[i]=start+2*i for i from zero through n-1.','Return the bitwise XOR of every generated value.'],[([5,0],'The sequence 0,2,4,6,8 has XOR eight.'),([4,3],'The sequence 3,5,7,9 has XOR eight.')],[[n,s] for n,s in [(1,0),(1,5),(2,0),(2,1),(5,0),(4,3),(3,2),(10,5),(7,7),(20,0),(6,100),(2,999),(15,16),(100,25)]],XOR,[XOR.replace('start+2*i','start+i'),XOR.replace('answer^=','answer+=')],['Generates consecutive rather than every-other values.','Adds values instead of applying bitwise XOR.'],xor_o,rxor,['Generate each term directly from its index.','Accumulate with bitwise XOR starting from zero.','Visit exactly n indices.','XOR is associative and zero is its identity, so the accumulator equals the required full reduction.'],'O(n)','O(1)',3),
1487:S('unique_folder_names',[('names','list[str]')],'list[str]',['hash-maps','strings'],['Process requested names in order; keep an unused name unchanged.','For a duplicate, append the smallest positive (k) suffix that makes it unused.'],[([['pes','fifa','gta','pes(2019)']],'Every requested name is initially distinct, so none changes.'),([['gta','gta(1)','gta','avalon']],'The duplicate gta skips existing gta(1) and becomes gta(2).')],[[x] for x in [['a'],['a','a'],['a','a','a'],['pes','fifa','gta','pes(2019)'],['gta','gta(1)','gta','avalon'],['onepiece','onepiece(1)','onepiece(2)','onepiece(3)','onepiece'],['wano','wano','wano','wano'],['a','a(1)','a','a(1)'],['x','y','x','y'],['doc','doc(2)','doc','doc'],['file(1)','file','file'],['a(1)','a','a'],['z','z(1)','z(2)','z'],['name','name(1)','name(1)(1)','name(1)']]],NAMES,[NAMES.replace('suffix=next_suffix[name]','suffix=next_suffix[name]+1'),NAMES.replace("while f'{name}({suffix})' in next_suffix",'while False')],['Skips the currently smallest candidate suffix before checking it.','Never checks whether a generated suffix name is already used.'],names_o,rnames,['Map every used name to the next suffix worth trying.','Unused names are emitted unchanged and initialized at suffix one.','For a duplicate, advance until name(k) is unused, emit it, and update both base and generated-name entries.','The stored lower bound skips known collisions while the loop guarantees the smallest currently available suffix.'],'O(total suffix probes)','O(n)',5),
}
BATCH[1471]['comparator']='unordered'
