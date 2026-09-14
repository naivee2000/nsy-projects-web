"""Second reviewed group of workbook batch 106."""
from math import gcd
from .import_batch_055 import entry

def coins_o(a):
 coins=a[0];possible={0}
 for coin in coins:possible|={value+coin for value in list(possible)}
 answer=0
 while answer in possible:answer+=1
 return answer
def operations_o(a):
 nums=a[0]
 def visit(values,step):
  if not values:return 0
  return max(step*gcd(values[i],values[j])+visit(values[:i]+values[i+1:j]+values[j+1:],step+1) for i in range(len(values)) for j in range(i+1,len(values)))
 return visit(nums,1)
def ascending_o(a):
 nums=a[0];return max(sum(nums[left:right+1]) for left in range(len(nums)) for right in range(left,len(nums)) if all(nums[i]<nums[i+1] for i in range(left,right)))
def backlog_o(a):
 buy=[];sell=[]
 for price,amount,kind in a[0]:
  opposite=sell if kind==0 else buy
  while amount:
   eligible=[item for item in opposite if item[1]<=price] if kind==0 else [item for item in opposite if item[1]>=price]
   if not eligible:break
   chosen=min(eligible,key=lambda item:item[1]) if kind==0 else max(eligible,key=lambda item:item[1]);matched=min(amount,chosen[0]);amount-=matched;chosen[0]-=matched
   if chosen[0]==0:opposite.remove(chosen)
  if amount:(buy if kind==0 else sell).append([amount,price])
 return sum(item[0] for item in buy+sell)%1_000_000_007
def bounded_o(a):
 n,index,max_sum=a
 def required(peak):return sum(max(1,peak-abs(position-index)) for position in range(n))
 peak=1
 while required(peak+1)<=max_sum:peak+=1
 return peak
def rcoins(r):return [[r.randint(1,12) for _ in range(r.randint(1,12))]]
def roperations(r):return [[r.randint(1,30) for _ in range(2*r.randint(1,3))]]
def rascending(r):return [[r.randint(1,30) for _ in range(r.randint(1,12))]]
def rbacklog(r):return [[[r.randint(1,10),r.randint(1,12),r.randint(0,1)] for _ in range(r.randint(1,10))]]
def rbounded(r):
 n=r.randint(1,15);return [n,r.randrange(n),r.randint(n,n+80)]
COINS='''def maximum_consecutive_coin_values(coins):
 reach=1
 for coin in sorted(coins):
  if coin>reach:break
  reach+=coin
 return reach
'''
OPERATIONS='''def maximum_gcd_operation_score(nums):
 from math import gcd
 size=len(nums);dp=[0]*(1<<size)
 for mask in range(1<<size):
  used=mask.bit_count()
  if used%2:continue
  step=used//2+1
  for i in range(size):
   if mask>>i&1:continue
   for j in range(i+1,size):
    if mask>>j&1==0:
     nxt=mask|(1<<i)|(1<<j);dp[nxt]=max(dp[nxt],dp[mask]+step*gcd(nums[i],nums[j]))
 return dp[-1]
'''
ASCENDING='''def maximum_ascending_subarray_sum(nums):
 current=answer=nums[0]
 for index in range(1,len(nums)):
  current=current+nums[index] if nums[index]>nums[index-1] else nums[index]
  answer=max(answer,current)
 return answer
'''
BACKLOG='''def backlog_order_count(orders):
 import heapq
 buys=[];sells=[]
 for price,amount,kind in orders:
  if kind==0:
   while amount and sells and sells[0][0]<=price:
    sell_price,sell_amount=heapq.heappop(sells);matched=min(amount,sell_amount);amount-=matched;sell_amount-=matched
    if sell_amount:heapq.heappush(sells,(sell_price,sell_amount))
   if amount:heapq.heappush(buys,(-price,amount))
  else:
   while amount and buys and -buys[0][0]>=price:
    negative,buy_amount=heapq.heappop(buys);matched=min(amount,buy_amount);amount-=matched;buy_amount-=matched
    if buy_amount:heapq.heappush(buys,(negative,buy_amount))
   if amount:heapq.heappush(sells,(price,amount))
 return sum(amount for _,amount in buys+sells)%(10**9+7)
'''
BOUNDED='''def maximum_bounded_value(n, index, max_sum):
 def side(peak,length):
  descending=min(peak-1,length)
  return descending*(2*peak-descending-1)//2+(length-descending)
 def needed(peak):return peak+side(peak,index)+side(peak,n-index-1)
 low,high=1,max_sum
 while low<high:
  middle=(low+high+1)//2
  if needed(middle)<=max_sum:low=middle
  else:high=middle-1
 return low
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1798:E('maximum_consecutive_coin_values',[('coins','list[int]')],'int',['arrays','sorting','greedy'],['Each positive coin may be used at most once; duplicate values are separate coins.','Return how many consecutive sums beginning with zero are constructible.'],[([[1,3]],'Only zero and one are constructible before the gap at two, so return two.'),([[1,1,1,4]],'Every value zero through seven is constructible, so return eight.')],[[x] for x in [[1],[2],[1,2],[1,1],[1,4,10,3,1],[2,3,4],[1,2,2,5],[1,1,3,10],[5,1,1],[1,2,4,8],[1,1,1,1],[3,1,2],[1,6,2,3],[10,20]]],COINS,[COINS.replace('coin>reach','coin>=reach'),COINS.replace('reach+=coin','reach+=1')],['Stops when a coin exactly bridges the next missing value.','Adds one rather than extending reach by the coin value.'],coins_o,rcoins,H('Maintain the first value that is not yet constructible.','Sort coins; a coin no larger than reach extends the constructible interval.','Start reach at one and add each usable coin until a gap appears.','If sums through reach-1 exist, adding coin<=reach covers continuously through reach+coin-1; coin>reach can never fill reach.'),'O(n log n)','O(n)',5),
1799:E('maximum_gcd_operation_score',[('nums','list[int]')],'int',['arrays','bitmask','dynamic-programming','backtracking','number-theory'],['The array has even length at most fourteen; each element is removed exactly once.','At one-indexed operation i, a chosen pair contributes i times its gcd; maximize total score.'],[([[1,2]],'The only pair has gcd one and is chosen at operation one.'),([[3,4,6,8]],'Pair 3 with 6 first and 4 with 8 second for score 3+8=11.')],[[x] for x in [[2,4],[3,6],[1,2,3,4],[3,4,6,8],[1,2,3,4,5,6],[2,2,2,2],[6,10,15,25],[7,11,13,17],[2,3,4,9],[12,18,24,30],[5,10,20,25,30,40],[1,1,1,1],[8,12,16,20],[9,15,21,27]]],OPERATIONS,[OPERATIONS.replace('step=used//2+1','step=used//2'),OPERATIONS.replace('max(dp[nxt],','min(dp[nxt],')],['Uses zero-based operation multipliers.','Minimizes transitions instead of maximizing the score.'],operations_o,roperations,H('The future depends only on which indices have already been used.','Use a bitmask DP and add every possible unused pair as the next operation.','The operation number is half the used-bit count plus one.','Each pairing order corresponds to one path through masks, and maximizing every transition explores all legal schedules without recomputing equivalent used sets.'),'O(2^m*m²)','O(2^m)',8),
1800:E('maximum_ascending_subarray_sum',[('nums','list[int]')],'int',['arrays'],['All values are positive integers.','Return the largest sum of a contiguous strictly increasing subarray.'],[([[10,20,30,5,10,50]],'The final run [5,10,50] has sum sixty-five, larger than the first run.'),([[10,20,30,40,50]],'The entire array is strictly increasing and sums to one hundred fifty.')],[[x] for x in [[1],[2,1],[1,2],[1,1],[12,17,15,13,10,11,12],[5,4,3,2],[1,2,3,1,2],[10,20,30,5,10,50],[3,5,7,2,9],[100],[4,4,5],[1,3,2,4,6],[9,1,2,3],[2,10,1,20]]],ASCENDING,[ASCENDING.replace('>nums[index-1]','>=nums[index-1]'),ASCENDING.replace('answer=max(answer,current)','answer=current')],['Treats equal adjacent values as strictly increasing.','Returns only the last run sum rather than the maximum over all runs.'],ascending_o,rascending,H('Split the array wherever strict increase fails.','Maintain the sum of the current increasing run and the best sum seen.','Extend on nums[i]>nums[i-1]; otherwise restart at nums[i].','Every increasing subarray lies within one maximal increasing run, and positivity makes the whole maximal run its best-sum member.'),'O(n)','O(1)',3),
1801:E('backlog_order_count',[('orders','list[list[int]]')],'int',['arrays','simulation','heaps'],['Each order is [price,amount,type], where zero buys and one sells.','Match buys against the cheapest affordable sell and sells against the highest sufficiently priced buy; return remaining amount modulo 1,000,000,007.'],[([[[10,5,0],[15,2,1],[25,1,1],[30,4,0]]],'The final backlog contains five buys at ten and one at thirty.'),([[[7,1000000000,1],[15,3,0],[5,999999995,0],[5,1,1]]],'After matching, the remaining 1,999,999,991 orders reduce to 999,999,984 modulo 1,000,000,007.')],[[x] for x in [[[5,1,0]],[[5,1,1]],[[5,2,0],[5,1,1]],[[5,1,1],[5,2,0]],[[10,3,0],[9,2,1]],[[10,3,0],[11,2,1]],[[5,2,1],[6,1,1],[10,3,0]],[[10,2,0],[9,2,0],[8,3,1]],[[1,5,0],[2,3,1]],[[3,4,1],[3,2,0]],[[8,2,0],[4,3,1],[5,1,0]],[[2,10,0],[3,4,1],[1,2,1]],[[9,3,1],[10,2,0],[8,4,0]],[[5,5,0],[5,5,1]]]],BACKLOG,[BACKLOG.replace('sells[0][0]<=price','sells[0][0]<price'),BACKLOG.replace('-buys[0][0]>=price','-buys[0][0]>price')],['Fails to match buy and sell orders at equal prices.','Likewise rejects equal-price matches when processing sells.'],backlog_o,rbacklog,H('Keep the best available opposite-side price accessible.', 'Use a min-heap for sells and a negated min-heap for buys.', 'Consume compatible heap tops until the new amount is exhausted or the best opposite price no longer matches.', 'Only the cheapest sell or highest buy can be the required next match; heap simulation preserves every unmatched remainder exactly.'),'O(orders log orders)','O(orders)',6),
1802:E('maximum_bounded_value',[('n','int'),('index','int'),('max_sum','int')],'int',['binary-search','math','greedy'],['Construct n positive integers with adjacent differences at most one and total at most max_sum.','Return the largest possible value at the given zero-based index.'],[([4,2,6],'Peak two can form [1,2,2,1], while peak three needs more than six total.'),([6,1,10],'A peak of three is feasible, but four would force the minimum total above ten.')],[[*x] for x in [(1,0,1),(1,0,10),(2,0,2),(2,1,3),(3,1,3),(3,1,6),(4,2,6),(6,1,10),(5,0,15),(5,4,15),(7,3,7),(7,3,20),(10,5,30),(4,0,100)]],BOUNDED,[BOUNDED.replace('middle=(low+high+1)//2','middle=(low+high)//2'),BOUNDED.replace('peak-1','peak')],['Uses a lower midpoint and can stall when low and high are adjacent.','Makes each side start at the peak rather than peak minus one, overestimating required sum.'],bounded_o,rbounded,H('For a fixed peak, the minimum-sum array falls by one away from index until reaching one.', 'Compute that minimum sum arithmetically on both sides.', 'Binary-search the largest peak whose required sum does not exceed max_sum.', 'Every feasible array with a given peak has at least this tent-shaped sum, and that exact shape is constructible, making the predicate necessary and sufficient.'),'O(log max_sum)','O(1)',7),
}
BATCH[1802]['wrong'][0]=BOUNDED.replace('<=max_sum','<max_sum')
BATCH[1802]['wrong_reasons'][0]='Rejects peaks whose minimum required sum exactly equals max_sum.'
