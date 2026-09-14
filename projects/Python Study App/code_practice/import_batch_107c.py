"""Third reviewed group of workbook batch 107."""
from itertools import permutations
from .import_batch_055 import entry
def sorted_o(a):
 s=a[0];return sum(''.join(candidate)<s for candidate in set(permutations(s)))%(10**9+7)
def pangram_o(a):return all(chr(97+index) in a[0] for index in range(26))
def cream_o(a):
 costs,coins=a;best=0
 for mask in range(1<<len(costs)):
  if sum(costs[i] for i in range(len(costs)) if mask>>i&1)<=coins:best=max(best,mask.bit_count())
 return best
def cpu_o(a):
 tasks=a[0];time=0;remaining=set(range(len(tasks)));answer=[]
 while remaining:
  available=[index for index in remaining if tasks[index][0]<=time]
  if not available:time=min(tasks[index][0] for index in remaining);available=[index for index in remaining if tasks[index][0]<=time]
  chosen=min(available,key=lambda index:(tasks[index][1],index));remaining.remove(chosen);answer.append(chosen);time+=tasks[chosen][1]
 return answer
def and_o(a):
 answer=0
 for left in a[0]:
  for right in a[1]:answer^=left&right
 return answer
def rsorted(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,8)))]
def rpangram(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,60)))]
def rcream(r):return [[r.randint(1,15) for _ in range(r.randint(1,12))],r.randint(0,50)]
def rcpu(r):return [[[r.randint(0,15),r.randint(1,10)] for _ in range(r.randint(1,10))]]
def rand(r):return [[r.randint(0,63) for _ in range(r.randint(1,12))],[r.randint(0,63) for _ in range(r.randint(1,12))]]
SORTED='''def operations_to_sort_string(s):
 from collections import Counter
 mod=10**9+7;n=len(s);factorial=[1]*(n+1)
 for index in range(1,n+1):factorial[index]=factorial[index-1]*index%mod
 inverse=[pow(value,mod-2,mod) for value in factorial];counts=Counter(s);answer=0
 for index,char in enumerate(s):
  smaller=sum(amount for key,amount in counts.items() if key<char);ways=factorial[n-index-1]*smaller%mod
  for amount in counts.values():ways=ways*inverse[amount]%mod
  answer=(answer+ways)%mod;counts[char]-=1
  if counts[char]==0:del counts[char]
 return answer
'''
PANGRAM='''def is_pangram(sentence):
 return len(set(sentence))==26
'''
CREAM='''def maximum_ice_cream_bars(costs, coins):
 bought=0
 for cost in sorted(costs):
  if cost>coins:break
  coins-=cost;bought+=1
 return bought
'''
CPU='''def single_threaded_cpu_order(tasks):
 import heapq
 ordered=sorted((start,duration,index) for index,(start,duration) in enumerate(tasks));heap=[];answer=[];time=0;cursor=0
 while cursor<len(ordered) or heap:
  if not heap:time=max(time,ordered[cursor][0])
  while cursor<len(ordered) and ordered[cursor][0]<=time:
   start,duration,index=ordered[cursor];heapq.heappush(heap,(duration,index));cursor+=1
  duration,index=heapq.heappop(heap);answer.append(index);time+=duration
 return answer
'''
AND='''def xor_sum_of_pairwise_and(arr1, arr2):
 left=right=0
 for value in arr1:left^=value
 for value in arr2:right^=value
 return left&right
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1830:E('operations_to_sort_string',[('s','str')],'int',['strings','combinatorics','counting','math'],['One operation moves to the immediately previous distinct lexicographic permutation using the stated swap-and-reverse rule.','Return operations needed to reach sorted ascending order, modulo 1,000,000,007.'],[(['cba'],'The descending permutation has five distinct smaller permutations before abc.'),(['aabaa'],'Exactly two distinct permutations are lexicographically smaller.')],[[s] for s in ['a','ab','ba','abc','cba','aabaa','aa','baca','dcba','abab','cabaa','ddcc','abcd','cbad']],SORTED,[SORTED.replace('key<char','key>char'),SORTED.replace('factorial[n-index-1]','factorial[n-index]')],['Counts lexicographically larger choices instead of smaller ones.','Permutes one too many remaining positions.'],sorted_o,rsorted,H('The answer is the zero-based lexicographic rank among distinct permutations of the multiset.', 'At each position, count smaller remaining characters and the multiset permutations of the suffix.', 'Use factorials and modular inverse factorials to divide by duplicate counts.', 'Every smaller permutation differs first at one position with a smaller available character; summing those disjoint groups gives the exact rank and operation count.'),'O(n*alphabet)','O(n+alphabet)',8),
1832:E('is_pangram',[('sentence','str')],'bool',['strings','sets'],['The sentence contains only lowercase English letters.','Return whether every one of the 26 letters occurs at least once.'],[(['thequickbrownfoxjumpsoverthelazydog'],'This sentence contains every lowercase letter.'),(['leetcode'],'Many letters are absent, so it is not a pangram.')],[[s] for s in ['abcdefghijklmnopqrstuvwxyz','thequickbrownfoxjumpsoverthelazydog','leetcode','a','aaaaaaaaaaaaaaaaaaaaaaaaaa','abcdefghijklmnopqrstuvwxy','zyxwvutsrqponmlkjihgfedcba','packmyboxwithfivedozenliquorjugs','sphinxofblackquartzjudgemyvow','abcxyz','abcdefghijklmnopqrstuvwxyza','qwertyuiopasdfghjklzxcvbnm','helloabcdefghijklmnopqrstuvwxyz','abcdefghijklmnopqrstuvwxzz']],PANGRAM,[PANGRAM.replace('==26','>=25'),PANGRAM.replace('set(sentence)','set(sentence[:-1])')],['Accepts sentences containing only twenty-five distinct letters.','Ignores the final character, which may be the only occurrence of a required letter.'],pangram_o,rpangram,H('Repeated letters do not matter, so keep only distinct characters.','A lowercase pangram has exactly 26 distinct letters.','Build a set and compare its size with 26.','The alphabet contains 26 allowed symbols; having all of them is equivalent to the set reaching size 26.'),'O(n)','O(1) alphabet',3),
1833:E('maximum_ice_cream_bars',[('costs','list[int]'),('coins','int')],'int',['arrays','sorting','greedy'],['Each bar may be purchased once and costs a positive integer amount.','Maximize the number bought without spending more than coins.'],[([[1,3,2,4,1],7],'Buying costs 1,1,2,3 uses all seven coins for four bars.'),([[10,6,8,7,7,8],5],'Every bar costs more than the budget, so buy none.')],[[*x] for x in [([1],1),([2],1),([1,3,2,4,1],7),([10,6,8,7,7,8],5),([1,6,3,1,2,5],20),([5,5,5],10),([2,1],2),([4,3,2,1],6),([1,1,1],0),([7],100),([2,2,3],4),([9,1,8,2],3),([5,4,3],7),([1,2,10,10],12)]],CREAM,[CREAM.replace('sorted(costs)','reversed(sorted(costs))'),CREAM.replace('cost>coins','cost>=coins')],['Buys expensive bars first.', 'Refuses a bar whose cost exactly equals the remaining budget.'],cream_o,rcream,H('To maximize a count under one budget, cheaper bars should be chosen first.','Sort costs ascending and purchase until the next cost exceeds remaining coins.','Subtract each affordable cost and increment the count.', 'If a solution buys a more expensive bar while skipping a cheaper one, swapping them never hurts feasibility; repeated exchanges yield the greedy prefix.'),'O(n log n)','O(n)',5),
1834:E('single_threaded_cpu_order',[('tasks','list[list[int]]')],'list[int]',['arrays','sorting','heaps','simulation'],['Each task is [enqueue_time,processing_time] and the CPU runs one task to completion.','Among available tasks choose shortest processing time, breaking ties by original index; return processing order.'],[([[[1,2],[2,4],[3,2],[4,1]]],'Task zero runs first; then priorities select tasks two, three, and one.'),([[[7,10],[7,12],[7,5],[7,4],[7,2]]],'All arrive together, so duration and then index order gives [4,3,2,0,1].')],[[x] for x in [[[0,1]],[[1,2],[2,4],[3,2],[4,1]],[[7,10],[7,12],[7,5],[7,4],[7,2]],[[5,2],[1,3]],[[0,3],[1,1]],[[0,2],[0,2]],[[2,1],[2,1],[2,1]],[[1,5],[2,1],[3,1]],[[10,1],[20,1]],[[0,10],[1,1],[2,1]],[[3,3],[1,9],[2,6]],[[1,2],[1,1],[2,1]],[[4,4],[4,3],[4,2],[4,1]],[[2,5],[5,2],[6,1]]]],CPU,[CPU.replace('(duration,index)','(index,duration)',1),CPU.replace('time+=duration','time+=duration+1')],['Prioritizes original index before processing duration.', 'Adds an idle time unit after every completed task.'],cpu_o,rcpu,H('Sort tasks by arrival and keep currently available work in a priority queue.', 'The heap key is processing time followed by original index.', 'When empty, jump time to the next arrival; enqueue all tasks now available, pop one, and advance time.', 'The heap exactly represents eligible tasks at every decision, so choosing its minimum follows both scheduling rules without preemption.'),'O(n log n)','O(n)',7),
1835:E('xor_sum_of_pairwise_and',[('arr1','list[int]'),('arr2','list[int]')],'int',['arrays','bit-manipulation','math'],['Form the bitwise AND for every cross-array pair and XOR all results.','Return the resulting integer.'],[([[1,2,3],[6,5]],'The XOR of all six pairwise AND values is zero.'),([[12],[4]],'The single pair contributes 12 AND 4, which is four.')],[[*x] for x in [([1],[1]),([0],[7]),([1,2,3],[6,5]),([12],[4]),([1,1],[1]),([1],[1,1]),([2,4],[3,5]),([7,7],[7,7]),([0,1,2],[3]),([5,10,15],[3,6]),([8,16],[24,7]),([1,2],[4,8]),([31],[15,16]),([3,5,6],[9,10])]],AND,[AND.replace('left&right','left^right'),AND.replace('right^=value','right|=value')],['Combines the two aggregate XORs with XOR instead of AND.', 'Aggregates the second array with OR, which violates XOR cancellation.'],and_o,rand,H('Bitwise AND distributes over XOR.', 'XOR every value in each array separately.', 'Return xor(arr1) AND xor(arr2).', 'Expanding the distributive identity produces every pairwise AND term exactly once, and XOR parity cancels repeated bit contributions correctly.'),'O(n+m)','O(1)',8),
}
