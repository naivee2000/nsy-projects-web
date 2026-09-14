"""Middle of batch 101: greedy sales, Fenwick costs, BFS, and prefix invariants."""
from bisect import bisect_left,insort
from collections import Counter,deque
from heapq import heapify,heappop,heappush
from .import_batch_055 import entry
MOD=1_000_000_007
def sales_o(a):
 inventory,orders=a;heap=[-x for x in inventory];heapify(heap);answer=0
 for _ in range(orders):value=-heappop(heap);answer+=value;heappush(heap,-(value-1))
 return answer%MOD
def cost_o(a):
 ordered=[];answer=0
 for value in a[0]:
  less=bisect_left(ordered,value);greater=len(ordered)-__import__('bisect').bisect_right(ordered,value);answer+=min(less,greater);insort(ordered,value)
 return answer%MOD
def bomb_o(a):
 code,k=a;n=len(code)
 return [sum(code[(i+step)%n] for step in (range(1,k+1) if k>0 else range(k,0))) if k else 0 for i in range(n)]
def balanced_o(a):
 s=a[0];return min(s[:cut].count('b')+s[cut:].count('a') for cut in range(len(s)+1))
def jumps_o(a):
 forbidden,forward,backward,target=a;blocked=set(forbidden);queue=deque([(0,False,0)]);seen={(0,False)};limit=max([target]+forbidden)+forward+backward+50
 while queue:
  position,went_back,distance=queue.popleft()
  if position==target:return distance
  for nxt,back in ((position+forward,False),(position-backward,True)):
   if 0<=nxt<=limit and nxt not in blocked and (nxt,back) not in seen and not (went_back and back):seen.add((nxt,back));queue.append((nxt,back,distance+1))
 return -1
def close_o(a):
 left,right=map(Counter,a);return set(left)==set(right) and sorted(left.values())==sorted(right.values())
def reduce_o(a):
 nums,x=a;best=len(nums)+1
 for left in range(len(nums)+1):
  for right in range(len(nums)-left+1):
   if sum(nums[:left])+sum(nums[len(nums)-right:])==x:best=min(best,left+right)
 return best if best<=len(nums) else -1
def arrays_o(a):return ''.join(a[0])==''.join(a[1])
def smallest_o(a):
 n,k=a;answer=['a']*n;remaining=k-n
 for index in range(n-1,-1,-1):add=min(25,remaining);answer[index]=chr(97+add);remaining-=add
 return ''.join(answer)
def fair_o(a):
 nums=a[0];return sum(sum((nums[:i]+nums[i+1:])[::2])==sum((nums[:i]+nums[i+1:])[1::2]) for i in range(len(nums)))
def rsales(r):
 inv=[r.randint(1,15) for _ in range(r.randint(1,6))];return [inv,r.randint(1,sum(inv))]
def rcost(r):return [[r.randint(1,30) for _ in range(r.randint(1,30))]]
def rbomb(r):
 n=r.randint(2,12);k=r.randint(-(n-1),n-1);return [[r.randint(1,20) for _ in range(n)],k]
def rbalanced(r):return [''.join(r.choice('ab') for _ in range(r.randint(1,30)))]
def rjumps(r):
 forward,back,target=r.randint(1,8),r.randint(1,8),r.randint(0,25);forbidden=r.sample([i for i in range(1,30) if i!=target],r.randint(0,5));return [forbidden,forward,back,target]
def rclose(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,15))),''.join(r.choice('abcd') for _ in range(r.randint(1,15)))]
def rreduce(r):
 nums=[r.randint(1,10) for _ in range(r.randint(1,15))];return [nums,r.randint(1,sum(nums)+5)]
def rarrays(r):
 text=''.join(r.choice('abc') for _ in range(r.randint(1,20)));cuts=sorted(r.sample(range(1,len(text)),r.randint(0,max(0,len(text)-1)))) if len(text)>1 else [];parts=[];start=0
 for end in cuts+[len(text)]:parts.append(text[start:end]);start=end
 other=list(parts);r.shuffle(other)
 if r.random()<.6:other=[];start=0;cuts2=sorted(r.sample(range(1,len(text)),r.randint(0,max(0,len(text)-1)))) if len(text)>1 else []
 if not other:
  for end in cuts2+[len(text)]:other.append(text[start:end]);start=end
 return [parts,other]
def rsmall(r):
 n=r.randint(1,20);return [n,r.randint(n,26*n)]
def rfair(r):return [[r.randint(0,20) for _ in range(r.randint(1,20))]]
SALES='''def maximum_diminishing_ball_profit(inventory, orders):
 inventory=sorted(inventory,reverse=True)+[0];answer=0;colors=1
 for index in range(len(inventory)-1):
  high,low=inventory[index],inventory[index+1];available=colors*(high-low)
  take=min(orders,available);levels,remainder=divmod(take,colors)
  answer+=colors*(high+high-levels+1)*levels//2+remainder*(high-levels);orders-=take
  if orders==0:break
  colors+=1
 return answer%1000000007
'''
COST='''def sorted_array_insertion_cost(instructions):
 size=max(instructions)+1;tree=[0]*(size+1)
 def query(index):
  total=0
  while index>0:total+=tree[index];index-=index&-index
  return total
 def add(index):
  while index<len(tree):tree[index]+=1;index+=index&-index
 answer=0
 for inserted,value in enumerate(instructions):answer+=min(query(value-1),inserted-query(value));add(value)
 return answer%1000000007
'''
BOMB='''def decrypt_circular_code(code, k):
 n=len(code)
 if k==0:return [0]*n
 extended=code*2;answer=[]
 for index in range(n):
  if k>0:answer.append(sum(extended[index+1:index+k+1]))
  else:answer.append(sum((code*2)[index+n+k:index+n]))
 return answer
'''
BALANCED='''def minimum_balanced_string_deletions(s):
 deletions=seen_b=0
 for char in s:
  if char=='b':seen_b+=1
  else:deletions=min(deletions+1,seen_b)
 return deletions
'''
JUMPS='''def minimum_jumps_home(forbidden, a, b, x):
 blocked=set(forbidden);limit=max([x]+forbidden)+a+b+2000;queue=deque([(0,False,0)]);seen={(0,False)}
 while queue:
  position,backward,last=queue.popleft()
  if position==x:return last
  for nxt,went_back in ((position+a,False),(position-b,True)):
   state=(nxt,went_back)
   if 0<=nxt<=limit and nxt not in blocked and state not in seen and not (backward and went_back):seen.add(state);queue.append((nxt,went_back,last+1))
 return -1
'''
CLOSE='''def are_close_strings(word1, word2):
 first,second=Counter(word1),Counter(word2)
 return set(first)==set(second) and sorted(first.values())==sorted(second.values())
'''
REDUCE='''def minimum_end_removals_for_x(nums, x):
 target=sum(nums)-x
 if target<0:return -1
 left=0;current=0;longest=-1
 for right,value in enumerate(nums):
  current+=value
  while current>target and left<=right:current-=nums[left];left+=1
  if current==target:longest=max(longest,right-left+1)
 return -1 if longest<0 else len(nums)-longest
'''
ARRAYS='''def string_arrays_are_equal(word1, word2):
 return ''.join(word1)==''.join(word2)
'''
SMALLEST='''def smallest_numeric_value_string(n, k):
 answer=['a']*n;remaining=k-n
 for index in range(n-1,-1,-1):
  increase=min(25,remaining);answer[index]=chr(ord('a')+increase);remaining-=increase
 return ''.join(answer)
'''
FAIR='''def fair_array_removal_count(nums):
 total_even=sum(nums[::2]);total_odd=sum(nums[1::2]);left_even=left_odd=answer=0
 for index,value in enumerate(nums):
  if index%2==0:total_even-=value
  else:total_odd-=value
  if left_even+total_odd==left_odd+total_even:answer+=1
  if index%2==0:left_even+=value
  else:left_odd+=value
 return answer
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1648:E('maximum_diminishing_ball_profit',[('inventory','list[int]'),('orders','int')],'int',['greedy','sorting'],['Positive inventories; orders do not exceed total inventory.','Each sold ball earns its color’s current inventory, then that inventory decreases by one. Return maximum profit modulo 1,000,000,007.'],[([[2,5],4],'Sell values five, four, three, and two for fourteen.'),([[3,5],6],'Taking descending available values yields nineteen.')],[[*x] for x in [([2,5],4),([3,5],6),([1],1),([5],3),([2,2],3),([1,1],2),([10,1],5),([3,3,3],4),([4,2,1],7),([5,5],10),([6,4,2],5),([9,3],8),([2,8,4],9),([1,2,3,4],6)]],SALES,[SALES.replace('take=min(orders,available)','take=available'),SALES.replace('remainder*(high-levels)','remainder*(high-levels-1)')],['Sells an entire value level even when fewer orders remain.','Prices partial-level balls one unit too low.'],sales_o,rsales,L('Always sell a currently highest-valued ball.','Process equal-height inventory levels together using arithmetic-series sums.','Sort descending; lower the top color group toward the next height, stopping partway when orders run out.','Exchange any lower-valued sale with an available higher-valued ball to increase profit, proving descending sale order.'),'O(n log n)','O(n)',5),
1649:E('sorted_array_insertion_cost',[('instructions','list[int]')],'int',['fenwick-trees','sorting'],['1–100,000 positive instructions.','Before each insertion, cost is min(number strictly smaller, number strictly greater); equal values count toward neither.'],[([[1,5,6,2]],'Only inserting two costs one, so total cost is one.'),([[1,2,3,6,5,4]],'The last two insertions contribute one and two, totaling three.')],[[x] for x in [[1,5,6,2],[1,2,3,6,5,4],[1],[1,1],[2,1],[1,2],[3,3,3],[3,1,2],[5,1,5,1,5],[4,3,2,1],[1,2,1,2],[10,5,7,5],[2,4,6,1,3,5],[7,2,9,2,5]]],COST,[COST.replace('query(value-1)','query(value)'),COST.replace('inserted-query(value)','inserted-query(value-1)')],['Counts equal values as strictly smaller.','Counts equal values as strictly greater.'],cost_o,rcost,L('Prefix counts answer how many inserted values lie below a threshold.','Use a Fenwick tree keyed by value.','For each x, query x-1 for smaller and inserted-query(x) for greater, add their minimum, then insert x.','The tree contains exactly the prior multiset, so the two prefix expressions implement both strict comparisons.'),'O(n log M)','O(M)',8),
1652:E('decrypt_circular_code',[('code','list[int]'),('k','int')],'list[int]',['arrays','sliding-windows'],['2–100 values and |k|<n.','Replace each position by the next k values when k>0, previous -k values when k<0, or zero when k=0; indexing is circular.'],[([[5,7,1,4],3],'Each output sums the other three circular values.'),([[2,4,9,3],-2],'Each output sums its two preceding circular values.')],[[*x] for x in [([5,7,1,4],3),([2,4,9,3],-2),([1,2,3,4],0),([1,2],1),([1,2],-1),([5,5,5],2),([1,2,3],-2),([9,1,2,3,4],2),([9,1,2,3,4],-3),([1,10,100],1),([4,3,2,1],3),([4,3,2,1],-3),([7,8,9,10],2),([6,1,6,1,6],-2)]],BOMB,[BOMB.replace('index+1:index+k+1','index:index+k'),BOMB.replace('index+n+k:index+n','index+n+k+1:index+n+1')],['Includes the current value and omits the kth next value.','Shifts the negative window one position forward.'],bomb_o,rbomb,L('A doubled array turns circular neighbors into contiguous slices.','Choose the forward or backward slice around each original index.','For k>0 sum i+1 through i+k; for k<0 sum i+n+k through i+n-1; return zeros for k=0.','Doubling preserves cyclic order for every window shorter than n.'),'O(n*|k|)','O(n)',3),
1653:E('minimum_balanced_string_deletions',[('s','str')],'int',['strings','dynamic-programming'],['1–100,000 characters, each a or b.','After deletions, every a must precede every b.'],[(['aababbab'],'Deleting the b at index two and the later a leaves a balanced string using two deletions.'),(['bbaaaaabb'],'Deleting the first two b characters is optimal.')],[[s] for s in ['aababbab','bbaaaaabb','a','b','ab','ba','aa','bb','abab','baba','aaaabbbb','bbbbaaaa','aabba','baabbab']],BALANCED,[BALANCED.replace('min(deletions+1,seen_b)','deletions+1'),BALANCED.replace('seen_b+=1','seen_b=1')],['Always deletes an out-of-order a instead of optionally deleting all preceding b characters.','Forgets how many b characters have appeared.'],balanced_o,rbalanced,L('At each a, either delete it or delete every b retained before it.','Track preceding b count and the optimal deletions for the processed prefix.','On b increment its count; on a set deletions=min(deletions+1,seen_b).','These are the only two ways to prevent a processed b from remaining before the current a.'),'O(n)','O(1)',5),
1654:E('minimum_jumps_home',[('forbidden','list[int]'),('a','int'),('b','int'),('x','int')],'int',['graphs','breadth-first-search'],['Positions are nonnegative; forbidden positions cannot be visited.','Jump forward by a or backward by b, but never backward twice consecutively. Return minimum jumps or -1.'],[([[14,4,18,1,15],3,15,9],'Three forward jumps reach nine without touching a forbidden position.'),([[8,3,16,6,12,20],15,13,11],'No legal sequence reaches eleven.')],[[*x] for x in [([14,4,18,1,15],3,15,9),([8,3,16,6,12,20],15,13,11),([],1,1,0),([],2,1,4),([],3,2,1),([2],2,1,3),([1],2,1,1),([],5,3,7),([4],3,1,5),([5,10],4,3,8),([],7,4,6),([6],5,2,3),([3,9],4,2,8),([2,8],5,3,7)]],JUMPS,[JUMPS.replace('and not (backward and went_back)',''),JUMPS.replace('state=(nxt,went_back)','state=(nxt,False)')],['Allows consecutive backward jumps.','Merges states that differ in whether a backward jump is currently permitted.'],jumps_o,rjumps,L('Position alone is insufficient state because the previous jump controls the next legal moves.','Breadth-first search pairs each position with whether the last move was backward.','Enqueue forward always and backward only after a non-backward move; skip forbidden, negative, repeated, and safely out-of-range states.','BFS explores legal sequences by length, so its first target state has minimum jumps.'),'O(limit)','O(limit)',5),
1657:E('are_close_strings',[('word1','str'),('word2','str')],'bool',['strings','hash-maps'],['Lowercase strings up to length 100,000.','Swaps can reorder freely; global exchanges can reassign existing character frequencies only among characters present in both strings.'],[(['abc','bca'],'Reordering alone transforms one string into the other.'),(['a','aa'],'Different lengths and frequency multisets cannot be transformed.')],[[*x] for x in [('abc','bca'),('a','aa'),('cabbba','abbccc'),('cabbba','aabbss'),('a','a'),('ab','ba'),('ab','ac'),('aaab','bbba'),('abb','aab'),('abcd','dcba'),('abc','abb'),('zzxy','xyzz'),('aaabbc','xxyyzz'),('uau','ssx')]],CLOSE,[CLOSE.replace('set(first)==set(second)','len(first)==len(second)'),CLOSE.replace('sorted(first.values())==sorted(second.values())','first.values()==second.values()')],['Checks only the number of distinct characters and allows introducing unavailable characters.','Compares frequency iteration order instead of frequency multisets.'],close_o,rclose,L('Swaps remove positional information; global exchanges permute counts among the same character set.','Compare the set of present characters and the sorted multiset of their counts.','Build two Counters and require equal keys plus equal sorted values.','Both invariants are necessary, and swaps plus frequency-label exchanges can realize any arrangement satisfying them.'),'O(n log alphabet)','O(alphabet)',5),
1658:E('minimum_end_removals_for_x',[('nums','list[int]'),('x','int')],'int',['sliding-windows','prefix-sums'],['Positive nums with length up to 100,000.','Remove a prefix and suffix whose sum is exactly x; minimize the total removed length.'],[([[1,1,4,2,3],5],'Removing two values from the right subtracts five.'),([[5,6,7,8,9],4],'No combination of end removals sums to four.')],[[*x] for x in [([1,1,4,2,3],5),([5,6,7,8,9],4),([3,2,20,1,1,3],10),([1],1),([1],2),([1,2],3),([1,2,3],3),([1,2,3],6),([5,1,1],5),([1,1,5],5),([2,2,2],4),([10,1,2,3],6),([1,10,1],2),([4,3,2,1],5)]],REDUCE,[REDUCE.replace('target=sum(nums)-x','target=x'),REDUCE.replace('len(nums)-longest','longest')],['Keeps a middle window summing to x instead of total minus x.','Returns the kept-window length instead of the number removed.'],reduce_o,rreduce,L('Removing ends leaves one contiguous middle window.','Maximize the length of a positive-number window summing to total-x.','Slide a window, shrinking while its sum exceeds the target; convert longest kept length to removals.','Every prefix-plus-suffix removal corresponds uniquely to its remaining middle window, so maximizing kept elements minimizes operations.'),'O(n)','O(1)',5),
1662:E('string_arrays_are_equal',[('word1','list[str]'),('word2','list[str]')],'bool',['strings','arrays'],['Each array contains nonempty string pieces.','Compare the complete concatenations while preserving piece and character order.'],[([['ab','c'],['a','bc']],'Both arrays concatenate to abc.'),([['a','cb'],['ab','c']],'The concatenations acb and abc differ.')],[[*x] for x in [(['ab','c'],['a','bc']),(['a','cb'],['ab','c']),(['abc'],['abc']),(['a','b'],['ab']),(['ab'],['a','b']),(['a'],['b']),(['x','yz'],['xy','z']),(['aa','b'],['a','ab']),(['12','3'],['1','23']),(['hello','world'],['hell','oworld']),(['a','a'],['aa']),(['abc','d'],['ab','cd']),(['z'],['z']),(['ab','ab'],['a','bab'])]],ARRAYS,[ARRAYS.replace("''.join(word2)","''.join(reversed(word2))"),ARRAYS.replace("''.join(word1)","''.join(sorted(word1))")],['Reverses the order of the second array’s pieces.','Sorts the first array’s pieces before concatenating.'],arrays_o,rarrays,L('Piece boundaries do not affect the produced character sequence.','Concatenate each array in its given order and compare.','Join word1 and word2 separately, then return equality.','Joining removes only boundaries and preserves every character position, exactly matching the definition.'),'O(total characters)','O(total characters)',3),
1663:E('smallest_numeric_value_string',[('n','int'),('k','int')],'str',['strings','greedy'],['1 <= n <= 100, and n <= k <= 26n.','Character values are a=1 through z=26; return the lexicographically smallest length-n string totaling k.'],[([3,27],'Keep the earliest positions at a and put the remaining value into the suffix, producing aay.'),([5,73],'Filling from the right produces aaszz, the smallest valid string.')],[[*x] for x in [(3,27),(5,73),(1,1),(1,26),(2,2),(2,52),(2,27),(3,3),(3,78),(4,30),(5,5),(5,130),(10,20),(4,77)]],SMALLEST,[SMALLEST.replace('range(n-1,-1,-1)','range(n)'),SMALLEST.replace('min(25,remaining)','min(26,remaining)')],['Adds excess value to the front, making the result lexicographically larger.','Allows a character to increase by 26 past z.'],smallest_o,rsmall,L('Start from the minimum string of all a characters, then place required extra value as far right as possible.','Fill suffix positions with up to 25 extra value each.','Set remaining=k-n; scan right to left, adding min(25,remaining) at each position.','Moving any increment from an earlier position to a later available position strictly decreases the string lexicographically.'),'O(n)','O(n)',5),
1664:E('fair_array_removal_count',[('nums','list[int]')],'int',['prefix-sums','arrays'],['1–100,000 nonnegative integers.','After removing one index, later indices shift parity; count removals yielding equal even-index and odd-index sums.'],[([[2,1,6,4]],'Removing index one leaves 2,6,4 with even sum six and odd sum six.'),([[1,1,1]],'Removing any index leaves one at each parity, so all three removals work.')],[[x] for x in [[2,1,6,4],[1,1,1],[1,2,3],[1],[0],[0,0],[1,1],[1,2],[2,2,2,2],[5,0,5],[3,1,2,4],[10,20,30,40,50],[1,2,1,2,1],[4,3,2,7,6,2]]],FAIR,[FAIR.replace('left_even+total_odd==left_odd+total_even','left_even+total_even==left_odd+total_odd'),FAIR.replace('total_even-=value','total_odd-=value')],['Fails to swap the parity of the suffix after removal.','Subtracts an even-index removal from the odd suffix total.'],fair_o,rfair,L('Removing an index swaps the parity of every later element.','Maintain left parity sums and remaining right parity sums around the candidate.','Remove the candidate from its suffix total; compare left-even+right-odd with left-odd+right-even; then add it to the left.','The comparison applies the exact parity shift while each running sum represents a disjoint side of the removed index.'),'O(n)','O(1)',5),
}

BATCH[1662]['wrong'][1]=ARRAYS.replace("''.join(word1)","''.join(reversed(word1))")
BATCH[1662]['wrong_reasons'][1]='Reverses the order of the first array’s pieces.'
