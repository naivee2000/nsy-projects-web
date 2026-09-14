"""First half of batch 98: recursive strings, interval DP, graph paths, and search."""
from collections import deque
from functools import lru_cache
from itertools import combinations
from .import_batch_055 import entry
MOD=1_000_000_007
def kth_o(a):
 n,k=a;s='0'
 for _ in range(2,n+1):s=s+'1'+''.join('1' if c=='0' else '0' for c in reversed(s))
 return s[k-1]
def overlap_o(a):
 nums,target=a;intervals=[(i,j) for i in range(len(nums)) for j in range(i,len(nums)) if sum(nums[i:j+1])==target]
 @lru_cache(None)
 def choose(index):return max([0]+[1+choose(end+1) for start,end in intervals if start>=index])
 return choose(0)
def cuts_o(a):
 n,cuts=a;points=[0]+sorted(cuts)+[n]
 @lru_cache(None)
 def solve(left,right):return 0 if right-left<=1 else points[right]-points[left]+min(solve(left,middle)+solve(middle,right) for middle in range(left+1,right))
 return solve(0,len(points)-1)
def path_o(a):
 n,roads,names,target=a;graph=[[] for _ in range(n)]
 for x,y in roads:graph[x].append(y);graph[y].append(x)
 paths=[(0,(city,)) for city in range(n)]
 for index,wanted in enumerate(target):
  if index==0:paths=[(names[city]!=wanted,(city,)) for city in range(n)];continue
  paths=[(cost+(names[neighbor]!=wanted),route+(neighbor,)) for cost,route in paths for neighbor in graph[route[-1]]]
 best=min(paths,key=lambda item:(item[0],item[1]));return list(best[1])
def odds_o(a):return any(all(value%2 for value in a[0][i:i+3]) for i in range(len(a[0])-2))
def equal_o(a):
 n=a[0];arr=[2*i+1 for i in range(n)];target=n;return sum(abs(value-target) for value in arr)//2
def force_o(a):
 positions,m=a;return max(min(b-a for a,b in zip(chosen,chosen[1:])) for chosen in combinations(sorted(positions),m))
def oranges_o(a):
 n=a[0];distance={n:0};queue=deque([n])
 while queue:
  value=queue.popleft()
  if value==0:return distance[value]
  nxt={value-1}
  if value%2==0:nxt.add(value//2)
  if value%3==0:nxt.add(value//3)
  for child in nxt:
   if child not in distance:distance[child]=distance[value]+1;queue.append(child)
def differ_o(a):
 words=a[0];return any(sum(x!=y for x,y in zip(words[i],words[j]))==1 for i in range(len(words)) for j in range(i+1,len(words)))
def separator_o(a):
 digits=str(a[0]);parts=[]
 while digits:parts.append(digits[-3:]);digits=digits[:-3]
 return '.'.join(reversed(parts))
def rkth(r):
 n=r.randint(1,10);return [n,r.randint(1,(1<<n)-1)]
def roverlap(r):return [[r.randint(-5,5) for _ in range(r.randint(1,14))],r.randint(-8,8)]
def rcuts(r):
 n=r.randint(2,25);return [n,sorted(r.sample(range(1,n),r.randint(1,min(7,n-1))))]
def rpath(r):
 n=r.randint(2,6);roads=[[i,i+1] for i in range(n-1)]
 for i in range(n):
  for j in range(i+2,n):
   if r.random()<.25:roads.append([i,j])
 names=[r.choice(['ATL','PEK','LAX','DXB']) for _ in range(n)];target=[r.choice(['ATL','PEK','LAX','DXB']) for _ in range(r.randint(1,6))]
 return [n,roads,names,target]
def rodds(r):return [[r.randint(-50,50) for _ in range(r.randint(3,30))]]
def requal(r):return [r.randint(1,1000)]
def rforce(r):
 n=r.randint(2,10);positions=r.sample(range(1,60),n);return [positions,r.randint(2,n)]
def roranges(r):return [r.randint(0,1000)]
def rdiffer(r):
 length=r.randint(1,8);count=r.randint(2,min(10,4**length));words=set()
 while len(words)<count:words.add(''.join(r.choice('abcd') for _ in range(length)))
 return [list(words)]
def rseparator(r):return [r.randint(0,2_000_000_000)]
KTH='''def kth_recursive_binary_bit(n, k):
 if n==1:return '0'
 middle=1<<(n-1)
 if k==middle:return '1'
 if k<middle:return kth_recursive_binary_bit(n-1,k)
 bit=kth_recursive_binary_bit(n-1,(1<<n)-k)
 return '1' if bit=='0' else '0'
'''
OVERLAP='''def maximum_target_sum_subarrays(nums, target):
 seen={0};prefix=answer=0
 for value in nums:
  prefix+=value
  if prefix-target in seen:answer+=1;seen={0};prefix=0
  else:seen.add(prefix)
 return answer
'''
CUTS='''def minimum_stick_cut_cost(n, cuts):
 points=[0]+sorted(cuts)+[n];size=len(points);dp=[[0]*size for _ in range(size)]
 for gap in range(2,size):
  for left in range(size-gap):
   right=left+gap;dp[left][right]=points[right]-points[left]+min(dp[left][mid]+dp[mid][right] for mid in range(left+1,right))
 return dp[0][-1]
'''
PATH='''def most_similar_named_path(n, roads, names, target_path):
 graph=[[] for _ in range(n)]
 for x,y in roads:graph[x].append(y);graph[y].append(x)
 states=[(names[city]!=target_path[0],(city,)) for city in range(n)]
 for wanted in target_path[1:]:
  next_states=[]
  for city in range(n):
   candidates=[(cost+(names[city]!=wanted),path+(city,)) for cost,path in states if city in graph[path[-1]]]
   next_states.append(min(candidates,key=lambda item:(item[0],item[1])))
  states=next_states
 return list(min(states,key=lambda item:(item[0],item[1]))[1])
'''
ODDS='''def has_three_consecutive_odds(arr):
 run=0
 for value in arr:
  run=run+1 if value%2 else 0
  if run==3:return True
 return False
'''
EQUAL='''def minimum_equal_array_operations(n):
 return (n*n)//4
'''
FORCE='''def maximum_magnetic_distance(position, m):
 position=sorted(position)
 def possible(distance):
  count=1;last=position[0]
  for value in position[1:]:
   if value-last>=distance:count+=1;last=value
  return count>=m
 low,high=1,position[-1]-position[0]
 while low<=high:
  middle=(low+high)//2
  if possible(middle):low=middle+1
  else:high=middle-1
 return high
'''
ORANGES='''def minimum_orange_days(n):
 from functools import lru_cache
 @lru_cache(None)
 def solve(value):
  if value<=1:return value
  return 1+min(value%2+solve(value//2),value%3+solve(value//3))
 return solve(n)
'''
DIFFER='''def strings_differ_by_one(words):
 seen=set()
 for word in words:
  for index in range(len(word)):
   pattern=word[:index]+'*'+word[index+1:]
   if pattern in seen:return True
   seen.add(pattern)
 return False
'''
SEPARATOR='''def format_with_thousand_dots(n):
 digits=str(n);answer=[]
 for index,char in enumerate(reversed(digits)):
  if index and index%3==0:answer.append('.')
  answer.append(char)
 return ''.join(reversed(answer))
'''
E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1545:S('kth_recursive_binary_bit',[('n','int'),('k','int')],'str',['recursion','strings'],['S1 is 0; each later string is the prior string, then 1, then the reversed bitwise inverse of the prior string.','Return the one-based kth bit of Sn without constructing the exponential-length string.'],[([3,1],'The first bit remains zero through every construction level.'),([4,11],'Reflecting position eleven across the center of S4 and inverting gives bit one.')],[[n,k] for n,k in [(1,1),(2,1),(2,2),(2,3),(3,1),(3,4),(3,7),(4,11),(4,8),(5,16),(5,31),(6,17),(7,64),(8,100)]],KTH,[KTH.replace("if k==middle:return '1'","if k==middle:return '0'"),KTH.replace('(1<<n)-k','(1<<n)-k-1')],['Returns zero at the central bit instead of one.','Reflects right-half positions one place too far.'],kth_o,rkth,['The string length is 2^n-1 and its center is position 2^(n-1).','Positions left of center recurse unchanged into Sn-1.','Positions right of center reflect to 2^n-k in Sn-1 and invert the returned bit.','These cases follow directly from prefix, center, and reversed-inverted suffix construction.'],'O(n)','O(n)',5),
1546:S('maximum_target_sum_subarrays',[('nums','list[int]'),('target','int')],'int',['prefix-sums','greedy'],['Choose the greatest number of pairwise non-overlapping contiguous subarrays, each summing to target.','Values may be negative, zero, or positive.'],[([[1,1,1,1,1],2],'The first two and next two values form two non-overlapping target-sum subarrays.'),([[-1,3,5,1,4,2,-9],6],'Three disjoint target-sum intervals can be selected.')],[[a,t] for a,t in [([1],1),([1],2),([1,1,1,1,1],2),([-1,3,5,1,4,2,-9],6),([0,0,0],0),([1,-1,1,-1],0),([3,3,3],3),([1,2,3],3),([2,-2,2,-2,2],2),([5,-5,5],5),([1,2,-3,3],3),([-2,2,-2,2],0),([4,1,1,1,4],3),([10,-4,-6,10],0)]],OVERLAP,[OVERLAP.replace('seen={0};prefix=0','seen={0}'),OVERLAP.replace('if prefix-target in seen','if prefix==target')],['Does not reset the running prefix after committing a subarray.','Recognizes only subarrays beginning at the current segment start.'],overlap_o,roverlap,['Track prefix sums since the end of the last selected interval.','When prefix-target was seen, a target-sum subarray ends here.','Greedily select it immediately, increment the answer, and reset the segment prefix set.','Earliest finishing intervals maximize the count by the standard interval-scheduling exchange argument.'],'O(n)','O(n)',5),
1547:S('minimum_stick_cut_cost',[('n','int'),('cuts','list[int]')],'int',['dynamic-programming','intervals'],['A cut costs the current length of the stick segment containing it.','Perform every listed cut in an order minimizing total cost.'],[([7,[1,3,4,5]],'Cutting at three, then five, one, and four can achieve total cost sixteen.'),([9,[5,6,1,4,2]],'An optimal ordering costs twenty-two.')],[[n,c] for n,c in [(2,[1]),(7,[1,3,4,5]),(9,[5,6,1,4,2]),(10,[5]),(10,[2,8]),(8,[1,2,3]),(20,[2,4,7,13]),(6,[1,5]),(15,[3,6,9,12]),(5,[1,2,4]),(100,[25,50,75]),(12,[2,3,8,10]),(30,[1,29]),(11,[1,4,7,10])]],CUTS,[CUTS.replace('points[right]-points[left]+','n+'),CUTS.replace('min(dp[left][mid]+dp[mid][right]','max(dp[left][mid]+dp[mid][right]')],['Charges the full original stick length for every recursive cut.','Chooses the most expensive split instead of the least expensive one.'],cuts_o,rcuts,['Add endpoints zero and n and sort all cut positions.','Let dp[left][right] be the cheapest way to make all cuts strictly inside that interval.','Try each interior cut first, paying interval length plus the two resulting subproblems.','Every cutting order has one first cut per interval, so minimizing over it covers all orders.'],'O(cuts³)','O(cuts²)',8),
1548:S('most_similar_named_path',[('n','int'),('roads','list[list[int]]'),('names','list[str]'),('target_path','list[str]')],'list[int]',['graphs','dynamic-programming'],['Roads are bidirectional and the returned city-index sequence must use one road per consecutive pair.','Minimize positions whose city name differs from target_path; any optimal path is valid. Tests use a deterministic lexicographically smallest optimum when ties occur.'],[([5,[[0,2],[0,3],[1,2],[1,3],[1,4],[2,4]],['ATL','PEK','LAX','DXB','HND'],['ATL','DXB','HND','LAX']],'Path 0,2,4,2 follows roads and has one name mismatch, which is optimal.'),([2,[[0,1]],['A','B'],['A','B','A']],'Alternating along the only road gives path 0,1,0 with no mismatches.')],[[*x] for x in [(2,[[0,1]],['A','B'],['A','B','A']),(2,[[0,1]],['A','B'],['B','A']),(5,[[0,2],[0,3],[1,2],[1,3],[1,4],[2,4]],['ATL','PEK','LAX','DXB','HND'],['ATL','DXB','HND','LAX']),(3,[[0,1],[1,2]],['A','B','C'],['A','B','C']),(3,[[0,1],[1,2],[0,2]],['A','A','B'],['A','B']),(4,[[0,1],[1,2],[2,3]],['X','Y','X','Y'],['X','Y','X','Y']),(3,[[0,1],[0,2]],['A','B','C'],['B','A','C']),(4,[[0,1],[0,2],[0,3]],['A','B','B','C'],['B','A','B']),(2,[[0,1]],['X','X'],['X','X','X']),(5,[[0,1],[1,2],[2,3],[3,4],[4,0]],['A','B','C','D','E'],['A','E','D']),(3,[[0,1],[1,2]],['A','A','A'],['B']),(4,[[0,1],[1,2],[2,3],[0,3]],['A','B','A','B'],['B','A','B']),(3,[[0,1],[1,2],[2,0]],['A','B','C'],['C','B','A']),(5,[[0,1],[0,2],[1,3],[2,4],[3,4]],['A','B','C','D','E'],['A','D','E'])]],PATH,[PATH.replace('cost+(names[city]!=wanted)','cost'),PATH.replace('if city in graph[path[-1]]','')],['Ignores all name mismatches after the first position.','Allows jumps between cities without a connecting road.'],path_o,rpath,['DP by target position and ending city.','For each city, extend only states ending at one of its road neighbors and add one when its name mismatches.','Keep the lowest-cost path per ending city, with deterministic lexicographic tie-breaking.','Every valid path has exactly one prior neighbor state, so the recurrence considers all paths of the required length.'],'O(path*n*(n+edges))','O(path*n)',8),
1550:S('has_three_consecutive_odds',[('arr','list[int]')],'bool',['arrays','scanning'],['Return true if some three adjacent array values are all odd.','Negative odd values count as odd.'],[([[2,6,4,1]],'There is only one odd value at the end, so no run of three exists.'),([[1,3,5,2]],'The first three adjacent values are all odd.')],[[x] for x in [[1,3,5],[2,6,4,1],[1,3,5,2],[2,1,3,5],[1,2,3,5],[1,3],[0,1,3,5,0],[-1,-3,-5],[2,4,6],[1,1,1,1],[2,1,3,4,5,7,9],[9,8,7,5],[10,11,13,15],[1,3,4,5,7]]],ODDS,[ODDS.replace('run==3','run==4'),ODDS.replace('value%2','value%2==1 and value>0')],['Requires four consecutive odds instead of three.','Ignores negative odd integers.'],odds_o,rodds,['Track the current adjacent odd run length.','Increment for an odd value and reset to zero for an even value.','Return as soon as the run reaches three.','The counter equals the length of the odd suffix ending at each position.'],'O(n)','O(1)',3),
1551:S('minimum_equal_array_operations',[('n','int')],'int',['math','arrays'],['The conceptual array is arr[i]=2*i+1 for i from zero through n-1.','One operation decreases one element and increases another by one; return the minimum operations to make all values equal.'],[([3],'Array 1,3,5 becomes all threes in two transfers.'),([6],'Moving units toward the mean value six requires nine operations.')],[[n] for n in [1,2,3,4,5,6,7,8,9,10,99,100,999,1000]],EQUAL,[EQUAL.replace('//4','//2'),EQUAL.replace('n*n','n*(n-1)')],['Doubles the required transfer count.','Uses the wrong quadratic expression for the symmetric distances.'],equal_o,requal,['The invariant total sum makes the final value equal to n.','Each operation can fix one unit of deficit below n using one unit of surplus above n.','Sum the deficits of the lower half, which simplifies to floor(n²/4).','Symmetry guarantees equal total deficit and surplus, so that many transfers are necessary and sufficient.'],'O(1)','O(1)',5),
1552:S('maximum_magnetic_distance',[('position','list[int]'),('m','int')],'int',['binary-search','greedy'],['Place m balls in distinct basket positions.','Maximize the minimum distance between every pair of placed balls.'],[([[1,2,3,4,7],3],'Placing balls at one, four, and seven makes the minimum distance three.'),([[5,4,3,2,1,1000000000],2],'Using the extreme positions yields distance 999,999,999.')],[[p,m] for p,m in [([1,2],2),([1,2,3,4,7],3),([5,4,3,2,1,1000000000],2),([1,10,20],3),([1,10,20],2),([0,5,10,15],4),([0,5,10,15],3),([3,6,9,12,15],2),([1,2,8,12,17],3),([100,101,102],2),([1,100],2),([2,4,6,8,10],3),([1,3,7,9,15],4),([10,1,7,4],2)]],FORCE,[FORCE.replace('>=distance','>distance'),FORCE.replace('return high','return low')],['Rejects placements whose gap equals the candidate distance.','Returns the first infeasible distance rather than the last feasible one.'],force_o,rforce,['Sort basket positions.','For a candidate distance, greedily place the first ball leftmost and each later ball at the earliest feasible basket.','Binary-search the greatest feasible distance.','The leftmost greedy placement leaves maximal room for all remaining balls, making feasibility monotone.'],'O(n log range)','O(n)',5),
1553:S('minimum_orange_days',[('n','int')],'int',['recursion','memoization'],['Each day eat one orange, or when divisible by two eat n/2 oranges, or when divisible by three eat 2n/3 oranges.','Return the minimum days to reach zero.'],[([10],'Eat one to reach nine, then reduce by three twice and eat the final orange, totaling four days.'),([6],'Reduce six to two by the divide-by-three action, then reduce to one and eat it, totaling three days.')],[[n] for n in [0,1,2,3,4,5,6,7,8,9,10,20,56,100]],ORANGES,[ORANGES.replace('value%2+solve(value//2)','solve(value//2)'),ORANGES.replace('1+min','2+min')],['Allows division by two without first eating the remainder oranges.','Charges two days for every division step.'],oranges_o,roranges,['A divide-by-two route first spends n mod 2 one-orange days, then one division day; similarly for three.','Recursively take the cheaper route.','Memoize by remaining orange count.','After at most two one-orange days a division is available, so any longer sequence of singles cannot beat one of these two choices.'],'O(log² n)','O(log n)',8),
1554:S('strings_differ_by_one',[('dict','list[str]')],'bool',['strings','hash-maps'],['All words have equal length and are distinct.','Return true if two different words differ at exactly one position.'],[([['abcd','acbd','aacd']],'Words abcd and aacd differ only at their second character.'),([['ab','cd','yz']],'Every pair differs at both positions, so the answer is false.')],[[x] for x in [['a','b'],['a','c'],['ab','ba'],['abcd','acbd','aacd'],['ab','cd','yz'],['abc','abd'],['abc','xbc'],['abc','abx'],['aaa','bbb','aba'],['same','lame'],['aa','ab','bb'],['xyz','xyx','xzz'],['abcd','abce','zzzz'],['cat','dog'],['abcde','abfde']]],DIFFER,[DIFFER.replace("word[:index]+'*'+word[index+1:]","word[:index]+word[index+1:]"),DIFFER.replace('if pattern in seen:return True','if pattern in seen and index==0:return True')],['Deletes the position marker, so differences at different positions can collide.','Detects matching deletion patterns only at the first position.'],differ_o,rdiffer,['Replace one position at a time by a marker to form a deletion-position pattern.','Two distinct words share a pattern exactly when they agree everywhere except that marked position.','Return when a pattern was seen from an earlier word.','Including the marker position prevents deletions at different indices from colliding.'],'O(words*length²)','O(words*length²)',5),
1556:S('format_with_thousand_dots',[('n','int')],'str',['strings','formatting'],['n is a nonnegative integer.','Insert a dot before every group of three digits counted from the right.'],[([987],'Three digits need no separator.'),([123456789],'Grouping from the right yields 123.456.789.')],[[n] for n in [0,1,12,987,1000,1001,12345,123456,1234567,123456789,1000000000,999999999,10101010,2000000000]],SEPARATOR,[SEPARATOR.replace("if index and index%3==0","if index%3==0"),SEPARATOR.replace('reversed(digits)','digits')],['Adds a leading separator before the first rightmost group.','Scans from the left while still reversing the constructed result.'],separator_o,rseparator,['Scan digits from right to left.','Before every fourth processed digit, append a separator.','Reverse the accumulated characters at the end.','Counting from the right guarantees every group except the leftmost has exactly three digits.'],'O(digits)','O(digits)',3),
}
