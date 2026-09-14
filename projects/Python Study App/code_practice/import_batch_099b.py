"""Second half of batch 99: matrices, MST, prefix remainders, and backtracking."""
from collections import deque
from itertools import combinations,permutations
from .import_batch_055 import entry
MOD=1_000_000_007
def special_o(a):
 mat=a[0];return sum(value==1 and sum(mat[r])==1 and sum(row[c] for row in mat)==1 for r,row in enumerate(mat) for c,value in enumerate(row))
def unhappy_o(a):
 n,preferences,pairs=a;partner={}
 for x,y in pairs:partner[x]=y;partner[y]=x
 rank=[[0]*n for _ in range(n)]
 for person,order in enumerate(preferences):
  for index,other in enumerate(order):rank[person][other]=index
 return sum(any(rank[x][u]<rank[x][partner[x]] and rank[u][x]<rank[u][partner[u]] for u in range(n) if u!=x) for x in range(n))
def mst_o(a):
 points=a[0];n=len(points);edges=[(abs(points[i][0]-points[j][0])+abs(points[i][1]-points[j][1]),i,j) for i in range(n) for j in range(i+1,n)];best=10**9
 for chosen in combinations(edges,n-1):
  graph=[[] for _ in range(n)]
  for _,x,y in chosen:graph[x].append(y);graph[y].append(x)
  seen={0};stack=[0]
  while stack:
   for nxt in graph[stack.pop()]:
    if nxt not in seen:seen.add(nxt);stack.append(nxt)
  if len(seen)==n:best=min(best,sum(edge[0] for edge in chosen))
 return 0 if n==1 else best
def transform_o(a):
 s,t=a
 if sorted(s)!=sorted(t):return False
 queue=deque([s]);seen={s}
 while queue:
  value=queue.popleft()
  if value==t:return True
  for left in range(len(s)):
   for right in range(left+2,len(s)+1):
    nxt=value[:left]+''.join(sorted(value[left:right]))+value[right:]
    if nxt not in seen:seen.add(nxt);queue.append(nxt)
 return False
def odd_o(a):
 arr=a[0];return sum(sum(arr[i:j]) for i in range(len(arr)) for j in range(i+1,len(arr)+1,2))
def requests_o(a):
 nums,requests=a;return max(sum(sum(order[left:right+1]) for left,right in requests) for order in permutations(nums))%MOD
def divisible_o(a):
 nums,p=a;best=len(nums)+1
 for left in range(len(nums)):
  for right in range(left,len(nums)):
   if right-left+1<len(nums) and (sum(nums)-sum(nums[left:right+1]))%p==0:best=min(best,right-left+1)
 return 0 if sum(nums)%p==0 else (-1 if best>len(nums) else best)
def printer_o(a):
 grid=a[0];colors=sorted({v for row in grid for v in row});bounds={}
 for color in colors:
  cells=[(r,c) for r,row in enumerate(grid) for c,v in enumerate(row) if v==color];bounds[color]=(min(r for r,c in cells),max(r for r,c in cells),min(c for r,c in cells),max(c for r,c in cells))
 for order in permutations(colors):
  canvas=[[0]*len(grid[0]) for _ in grid]
  for color in order:
   top,bottom,left,right=bounds[color]
   for r in range(top,bottom+1):
    for c in range(left,right+1):canvas[r][c]=color
  if canvas==grid:return True
 return False
def spaces_o(a):
 text=a[0];words=text.split();spaces=text.count(' ')
 if len(words)==1:return words[0]+' '*spaces
 gap,leftover=divmod(spaces,len(words)-1);return (' '*gap).join(words)+' '*leftover
def unique_o(a):
 s=a[0];best=0
 for mask in range(1<<(len(s)-1)):
  parts=[];start=0
  for index in range(len(s)-1):
   if mask>>index&1:parts.append(s[start:index+1]);start=index+1
  parts.append(s[start:]);
  if len(parts)==len(set(parts)):best=max(best,len(parts))
 return best
def rspecial(r):
 rows,cols=r.randint(1,6),r.randint(1,6);return [[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)]]
def runhappy(r):
 n=2*r.randint(1,4);preferences=[]
 for person in range(n):
  order=[x for x in range(n) if x!=person];r.shuffle(order);preferences.append(order)
 people=list(range(n));r.shuffle(people);return [n,preferences,[[people[i],people[i+1]] for i in range(0,n,2)]]
def rmst(r):return [[[r.randint(-10,10),r.randint(-10,10)] for _ in range(r.randint(1,6))]]
def rtransform(r):
 n=r.randint(1,7);s=''.join(r.choice('01234') for _ in range(n));t=''.join(r.choice('01234') for _ in range(n));return [s,t]
def rodd(r):return [[r.randint(1,20) for _ in range(r.randint(1,30))]]
def rrequests(r):
 n=r.randint(1,7);nums=[r.randint(1,20) for _ in range(n)];requests=[]
 for _ in range(r.randint(1,8)):
  left=r.randrange(n);requests.append([left,r.randint(left,n-1)])
 return [nums,requests]
def rdivisible(r):return [[r.randint(1,30) for _ in range(r.randint(1,20))],r.randint(2,20)]
def rprinter(r):
 rows,cols=r.randint(1,4),r.randint(1,4);return [[[r.randint(1,4) for _ in range(cols)] for _ in range(rows)]]
def rspaces(r):
 words=[''.join(r.choice('abc') for _ in range(r.randint(1,5))) for _ in range(r.randint(1,6))];spaces=r.randint(len(words)-1,20);gaps=[0]*(len(words)+1)
 for _ in range(spaces):gaps[r.randrange(len(gaps))]+=1
 return [''.join(' '*gaps[i]+word for i,word in enumerate(words))+' '*gaps[-1]]
def runique(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,10)))]
SPECIAL='''def count_special_binary_positions(mat):
 row_sums=[sum(row) for row in mat];col_sums=[sum(row[col] for row in mat) for col in range(len(mat[0]))]
 return sum(mat[row][col]==1 and row_sums[row]==1 and col_sums[col]==1 for row in range(len(mat)) for col in range(len(mat[0])))
'''
UNHAPPY='''def count_unhappy_friends(n, preferences, pairs):
 rank=[[0]*n for _ in range(n)]
 for person,order in enumerate(preferences):
  for index,other in enumerate(order):rank[person][other]=index
 partner=[0]*n
 for x,y in pairs:partner[x]=y;partner[y]=x
 answer=0
 for x in range(n):
  y=partner[x]
  for u in preferences[x]:
   if u==y:break
   if rank[u][x]<rank[u][partner[u]]:answer+=1;break
 return answer
'''
MST='''def minimum_manhattan_connection_cost(points):
 n=len(points);used=[False]*n;distance=[10**18]*n;distance[0]=0;answer=0
 for _ in range(n):
  node=min((distance[i],i) for i in range(n) if not used[i])[1];used[node]=True;answer+=distance[node]
  for nxt in range(n):
   if not used[nxt]:distance[nxt]=min(distance[nxt],abs(points[node][0]-points[nxt][0])+abs(points[node][1]-points[nxt][1]))
 return answer
'''
TRANSFORM='''def can_transform_by_substring_sorts(s, t):
 positions=[deque() for _ in range(10)]
 for index,char in enumerate(s):positions[int(char)].append(index)
 for char in t:
  digit=int(char)
  if not positions[digit]:return False
  index=positions[digit][0]
  if any(positions[smaller] and positions[smaller][0]<index for smaller in range(digit)):return False
  positions[digit].popleft()
 return True
'''
ODD='''def sum_odd_length_subarrays(arr):
 n=len(arr);answer=0
 for index,value in enumerate(arr):
  subarrays=(index+1)*(n-index);odd=(subarrays+1)//2;answer+=value*odd
 return answer
'''
REQUESTS='''def maximum_permuted_request_sum(nums, requests):
 difference=[0]*(len(nums)+1)
 for left,right in requests:difference[left]+=1;difference[right+1]-=1
 counts=[];current=0
 for delta in difference[:-1]:current+=delta;counts.append(current)
 return sum(value*count for value,count in zip(sorted(nums),sorted(counts)))%1000000007
'''
DIVISIBLE='''def shortest_removal_for_divisibility(nums, p):
 target=sum(nums)%p
 if target==0:return 0
 latest={0:-1};prefix=0;answer=len(nums)
 for index,value in enumerate(nums):
  prefix=(prefix+value)%p;needed=(prefix-target)%p
  if needed in latest:answer=min(answer,index-latest[needed])
  latest[prefix]=index
 return answer if answer<len(nums) else -1
'''
PRINTER='''def can_print_target_grid(target_grid):
 colors={value for row in target_grid for value in row};bounds={}
 for color in colors:
  cells=[(r,c) for r,row in enumerate(target_grid) for c,value in enumerate(row) if value==color]
  bounds[color]=(min(r for r,c in cells),max(r for r,c in cells),min(c for r,c in cells),max(c for r,c in cells))
 remaining=set(colors)
 while remaining:
  removable=[]
  for color in remaining:
   top,bottom,left,right=bounds[color]
   if all(target_grid[r][c] not in remaining or target_grid[r][c]==color for r in range(top,bottom+1) for c in range(left,right+1)):removable.append(color)
  if not removable:return False
  remaining.difference_update(removable)
 return True
'''
SPACES='''def redistribute_word_spaces(text):
 words=text.split();spaces=text.count(' ')
 if len(words)==1:return words[0]+' '*spaces
 gap,leftover=divmod(spaces,len(words)-1)
 return (' '*gap).join(words)+' '*leftover
'''
UNIQUE='''def maximum_unique_string_split(s):
 best=0
 def visit(index,used):
  nonlocal best
  if index==len(s):best=max(best,len(used));return
  if len(used)+len(s)-index<=best:return
  for end in range(index+1,len(s)+1):
   part=s[index:end]
   if part not in used:used.add(part);visit(end,used);used.remove(part)
 visit(0,set());return best
'''
E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1582:S('count_special_binary_positions',[('mat','list[list[int]]')],'int',['matrices','counting'],['A special position contains one and is the only one in both its row and column.','Return the number of special positions.'],[([[[1,0,0],[0,0,1],[1,0,0]]],'The one at row one, column two is alone in both its row and column.'),([[[1,0,0],[0,1,0],[0,0,1]]],'Every diagonal one is alone in its row and column, giving three.')],[[m] for m in [[[1]],[[0]],[[1,0],[0,1]],[[1,1],[0,0]],[[1,0,0],[0,0,1],[1,0,0]],[[1,0,0],[0,1,0],[0,0,1]],[[0,1,0],[0,0,0]],[[1,0],[1,0]],[[0,0],[0,0]],[[1,0,1],[0,1,0]],[[0,1],[1,0],[0,0]],[[1,0,0,0]],[[1],[0],[0]],[[1,0,0],[0,1,1]]]],SPECIAL,[SPECIAL.replace('and col_sums[col]==1',''),SPECIAL.replace('row_sums[row]==1','row_sums[row]>1')],['Checks row uniqueness but ignores another one in the same column.','Requires multiple ones in the row instead of exactly one.'],special_o,rspecial,['Precompute each row sum and column sum.','Inspect every one cell.','Count it exactly when its row and column sums are both one.','Those two equalities are precisely the definition of no other one in either direction.'],'O(rows*cols)','O(rows+cols)',3),
1583:S('count_unhappy_friends',[('n','int'),('preferences','list[list[int]]'),('pairs','list[list[int]]')],'int',['arrays','simulation'],['preferences[x] ranks every other friend from most to least preferred; pairs is a perfect matching.','Count people x for whom some u is preferred over x’s partner and u also prefers x over u’s partner.'],[([4,[[1,2,3],[3,2,0],[3,1,0],[1,2,0]],[[0,1],[2,3]]],'Friends one and three mutually prefer alternatives under the definition, giving two unhappy people.'),([2,[[1],[0]],[[1,0]]],'Each person is paired with their only possible friend, so neither is unhappy.')],[[*x] for x in [(2,[[1],[0]],[[0,1]]),(4,[[1,2,3],[3,2,0],[3,1,0],[1,2,0]],[[0,1],[2,3]]),(4,[[1,2,3],[0,2,3],[3,1,0],[2,1,0]],[[0,1],[2,3]]),(4,[[1,3,2],[2,3,0],[1,3,0],[0,2,1]],[[1,3],[0,2]]),(4,[[2,1,3],[3,2,0],[0,1,3],[1,2,0]],[[0,1],[2,3]]),(6,[[1,2,3,4,5],[0,2,3,4,5],[3,0,1,4,5],[2,0,1,4,5],[5,0,1,2,3],[4,0,1,2,3]],[[0,1],[2,3],[4,5]]),(4,[[3,2,1],[2,3,0],[1,0,3],[0,1,2]],[[0,3],[1,2]]),(4,[[1,2,3],[0,2,3],[0,1,3],[0,1,2]],[[0,1],[2,3]]),(4,[[2,3,1],[3,2,0],[0,1,3],[1,0,2]],[[0,1],[2,3]]),(2,[[1],[0]],[[1,0]]),(4,[[1,2,3],[2,0,3],[3,0,1],[2,1,0]],[[0,2],[1,3]]),(4,[[2,1,3],[2,3,0],[1,0,3],[1,2,0]],[[0,3],[1,2]]),(4,[[3,1,2],[2,3,0],[1,0,3],[0,1,2]],[[0,2],[1,3]]),(4,[[1,3,2],[0,2,3],[3,1,0],[2,0,1]],[[0,1],[2,3]])]],UNHAPPY,[UNHAPPY.replace('if u==y:break','if u==y:continue'),UNHAPPY.replace('rank[u][x]<rank[u][partner[u]]','rank[u][x]>rank[u][partner[u]]')],['Examines friends ranked below the current partner too.','Reverses whether the alternative friend prefers x over their partner.'],unhappy_o,runhappy,['Build a rank table for constant-time preference comparison and record every current partner.','For each x, inspect only friends appearing before x’s partner in x’s preference list.','If any such u ranks x before u’s partner, x is unhappy.','The two strict rank comparisons exactly encode the definition, and each unhappy person is counted once.'],'O(n²)','O(n²)',5),
1584:S('minimum_manhattan_connection_cost',[('points','list[list[int]]')],'int',['graphs','minimum-spanning-tree'],['Connect all points with Manhattan-distance edges so exactly one path exists between every pair.','Return the minimum total edge cost.'],[([[[0,0],[2,2],[3,10],[5,2],[7,0]]],'A minimum spanning tree connects all five points for total cost twenty.'),([[[3,12],[-2,5],[-4,1]]],'The two cheapest connecting edges total eighteen.')],[[p] for p in [[[0,0]],[[0,0],[1,1]],[[0,0],[2,2],[3,10],[5,2],[7,0]],[[3,12],[-2,5],[-4,1]],[[0,0],[0,1],[1,0]],[[1,1],[1,1]],[[0,0],[10,0],[5,0]],[[1,2],[3,4],[5,6]],[[0,0],[2,0],[0,2],[2,2]],[[-5,-5],[5,5],[0,0]],[[1,0],[-1,0],[0,10]],[[0,0],[1,2],[3,1],[4,4]],[[10,10],[10,-10],[-10,10],[-10,-10]],[[2,3],[2,8],[7,3],[7,8],[4,5]]]],MST,[MST.replace('answer+=distance[node]','answer+=0'),MST.replace('min(distance[nxt]','max(distance[nxt]')],['Never adds selected edge costs to the total.','Keeps the greatest known connection cost instead of the cheapest.'],mst_o,rmst,['Use Prim’s algorithm starting from any point.','Maintain each unconnected point’s cheapest Manhattan edge to the connected set.','Repeatedly add the cheapest such point and relax distances from it.','The cut property proves every selected cheapest crossing edge belongs to some minimum spanning tree.'],'O(n²)','O(n)',5),
1585:S('can_transform_by_substring_sorts',[('s','str'),('t','str')],'bool',['strings','greedy'],['A move sorts any non-empty substring of s in ascending digit order.','Return whether repeated moves can transform s exactly into t.'],[(['84532','34852'],'Digits three and four can move left across larger digits without crossing a smaller blocker, so transformation is possible.'),(['12345','12435'],'Four cannot move before the smaller three under ascending substring sorts, so transformation is impossible.')],[[s,t] for s,t in [('1','1'),('1','2'),('010','010'),('84532','34852'),('12345','12435'),('34521','23415'),('111','111'),('12','21'),('21','12'),('022','220'),('987654','456789'),('00123','00123'),('4321','1234'),('102','012'),('556677','565677')]],TRANSFORM,[TRANSFORM.replace('range(digit)','range(digit+1,10)'),TRANSFORM.replace('positions[digit].popleft()','positions[digit].pop()')],['Checks larger blockers instead of smaller digits that cannot be crossed.','Consumes the latest occurrence of each requested digit instead of the earliest.'],transform_o,rtransform,['Queue every source index by digit.','Read target left to right and consume the earliest unused source occurrence of its digit.','Before consuming digit d at index i, reject if any smaller digit has an unused occurrence before i.','Sorting can move d left across larger digits but never across a smaller digit, making this blocker condition necessary and sufficient.'],'O(10*n)','O(n)',8),
1588:S('sum_odd_length_subarrays',[('arr','list[int]')],'int',['arrays','math'],['Sum every contiguous subarray whose length is odd.','Array values are positive integers.'],[([[1,4,2,5,3]],'Adding the five length-one, three length-three, and one length-five subarray sums gives fifty-eight.'),([[10,11,12]],'Singletons total thirty-three and the full array adds thirty-three, giving sixty-six.')],[[x] for x in [[1],[1,2],[1,4,2,5,3],[10,11,12],[1,1,1],[1,2,3,4],[5,0,5],[2,4,6,8,10],[9,8,7],[3,1,4,1,5],[100],[1,2,1],[7,7,7,7],[1,3,5,7,9,11]]],ODD,[ODD.replace('(subarrays+1)//2','subarrays//2'),ODD.replace('answer+=value*odd','answer+=odd')],['Rounds down the number of odd-length containing subarrays.','Counts subarrays rather than summing their element contributions.'],odd_o,rodd,['An element at index i belongs to (i+1)*(n-i) total subarrays.','Among these start/end choices, half rounded up have odd length.','Multiply the element by that odd-subarray count.','Summing contributions counts every element of every odd-length subarray exactly once.'],'O(n)','O(1)',3),
1589:S('maximum_permuted_request_sum',[('nums','list[int]'),('requests','list[list[int]]')],'int',['prefix-sums','greedy'],['Permute nums once, then sum every inclusive requested range.','Maximize the total and return it modulo 1,000,000,007.'],[([[1,2,3,4,5],[[1,3],[0,1]]],'Usage counts align the largest values with the most requested indices, producing nineteen.'),([[1,2,3,4,5,6],[[0,1]]],'Place six and five in the only requested positions for total eleven.')],[[n,q] for n,q in [([1],[[0,0]]),([1,2,3,4,5],[[1,3],[0,1]]),([1,2,3,4,5,6],[[0,1]]),([5,5],[[0,1]]),([1,2,3],[[0,2],[0,2]]),([9,1,5],[[1,1]]),([1,2,3,4],[[0,0],[3,3]]),([10,20,30],[[0,1],[1,2]]),([1,1,2,2],[[0,3],[1,2]]),([7,8,9],[[0,0],[0,1],[0,2]]),([3,6,9,12],[[1,3]]),([1,100,2],[[0,0],[2,2]]),([4,3,2,1],[[0,3]]),([2,5,8,11,14],[[0,2],[2,4]])]],REQUESTS,[REQUESTS.replace('sorted(counts)','counts'),REQUESTS.replace('difference[right+1]-=1','difference[right]-=1')],['Does not align sorted values with sorted request frequencies.','Ends each inclusive request one index too early.'],requests_o,rrequests,['Use a difference array to count how many requests include each index.','Sort those usage counts and nums in the same order.','Pair the largest values with the largest counts.','The rearrangement inequality proves this pairing maximizes the dot product representing the total request sum.'],'O((n+requests) log n)','O(n)',5),
1590:S('shortest_removal_for_divisibility',[('nums','list[int]'),('p','int')],'int',['prefix-sums','modular-arithmetic'],['Remove one contiguous subarray, possibly empty, so the remaining sum is divisible by p.','The entire array may not be removed; return the minimum length or -1.'],[([[3,1,4,2],6],'Removing the single value four leaves sum six, divisible by six.'),([[6,3,5,2],9],'Removing values five and two leaves nine, so the minimum length is two.')],[[a,p] for a,p in [([3,1,4,2],6),([6,3,5,2],9),([1,2,3],3),([1,2,3],7),([5],5),([5],3),([1,1,1],2),([8,32],7),([4,4,4],5),([10,5,15],10),([2,3,1,4],5),([100,1,2],3),([7,7,7,1],7),([9,2,6,3],8)]],DIVISIBLE,[DIVISIBLE.replace('latest[prefix]=index','latest.setdefault(prefix,index)'),DIVISIBLE.replace('answer<len(nums)','answer<=len(nums)')],['Keeps the earliest prefix index instead of the latest, producing longer removals.','Allows removing the entire array.'],divisible_o,rdivisible,['Let target be the total-sum remainder that the removed subarray must have.','At each prefix remainder r, seek the latest earlier remainder r-target modulo p.','Use the index distance as a candidate and store the latest occurrence of r.','Prefix subtraction enumerates every subarray remainder, while latest indices minimize length.'],'O(n)','O(p)',5),
1591:S('can_print_target_grid',[('target_grid','list[list[int]]')],'bool',['graphs','topological-sort'],['Each color may be printed once as one solid rectangle, and later colors may overwrite it.','Return whether the target grid can be produced.'],[([[[1,1,1,1],[1,2,2,1],[1,2,2,1],[1,1,1,1]]],'Print the outer color-one rectangle first and overwrite its center with color two.'),([[[1,2,1],[2,1,2],[1,2,1]]],'Each color’s bounding rectangle requires the other both before and after it, forming an impossible cycle.')],[[g] for g in [[[1]],[[1,1],[1,1]],[[1,2],[1,2]],[[1,1,1,1],[1,2,2,1],[1,2,2,1],[1,1,1,1]],[[1,2,1],[2,1,2],[1,2,1]],[[1,2],[2,2]],[[1,2,3]],[[1,2],[3,4]],[[1,1,2],[1,3,2]],[[1,2,2],[1,2,2]],[[1,2,1]],[[1,1,1],[1,2,1],[1,1,1]],[[1,2,3],[1,2,3]],[[1,2],[2,1]]]],PRINTER,[PRINTER.replace('or target_grid[r][c]==color',''),PRINTER.replace('if not removable:return False','if not removable:return True')],['Requires every bounding-rectangle cell to have already removed color, including the candidate’s own cells.','Accepts cyclic color dependencies when no color can be removed.'],printer_o,rprinter,['Compute the bounding rectangle of every color.','A color can be the latest remaining print when every cell in its rectangle is itself or a color already removed from consideration.','Repeatedly remove all such colors; fail if a round removes none.','This is topological elimination of overwrite dependencies, so completing all colors is equivalent to a legal print order.'],'O(colors*rows*cols)','O(colors)',8),
1592:S('redistribute_word_spaces',[('text','str')],'str',['strings','formatting'],['Preserve word order and total string length.','Distribute spaces equally between adjacent words with the largest possible common gap, placing any remainder at the end.'],[([' this is a sentence '],'Five spaces give one between each pair and two trailing spaces.'),([' practice   makes   perfect'],'Six spaces across three words give three between each pair and none trailing.')],[[s] for s in ['a',' a','a ',' a ',' this is a sentence ',' practice   makes   perfect','hello   world','  walks  udp package   into  bar a','x y','   one','one   two   three ','a  b','  many   spaces  here','single     ']],SPACES,[SPACES.replace('divmod(spaces,len(words)-1)','(spaces//len(words),spaces%len(words))'),SPACES.replace("+' '*leftover",'')],['Divides spaces by the word count rather than the number of gaps.','Drops leftover spaces instead of appending them.'],spaces_o,rspaces,['Count spaces and split out the words.','With multiple words, divide spaces by gaps=words-1.','Join using the quotient and append the remainder; with one word, append every space.','The quotient is the largest equal gap that uses no more than the available spaces.'],'O(n)','O(n)',3),
1593:S('maximum_unique_string_split',[('s','str')],'int',['backtracking','recursion'],['Split s into non-empty contiguous substrings whose concatenation is s.','Require every chosen substring to be distinct and maximize the number of parts.'],[(['ababccc'],'One optimal split is a, b, ab, c, cc, giving five unique parts.'),(['aba'],'Splitting as a, b, a repeats a, so the best unique split has two parts.')],[[s] for s in ['a','ab','aa','aba','ababccc','abcdef','aaaa','abcabc','abac','banana','aabb','abcdeabc','zzzy','racecar']],UNIQUE,[UNIQUE.replace('if part not in used','if part in used'),UNIQUE.replace('used.remove(part)','')],['Chooses only substrings already used, so no first part is possible.','Never removes a substring while backtracking, leaking choices across branches.'],unique_o,runique,['Backtrack over every possible next substring boundary.','Choose a part only if it is absent from the current used set, then remove it after recursion.','Record the largest set size at the end of the string.','Every legal split corresponds to one root-to-leaf boundary sequence, and the used set enforces uniqueness exactly.'],'O(2^n*n)','O(n²)',5),
}

BATCH[1592]['sample_contract_adapter'] = {
    'source_sample': 'Input text = " this is a sentence " → Output "this is a sentence".',
    'arguments': [' this is a sentence '],
    'expected': 'this is a sentence  ',
    'reason': 'The workbook plain-text extraction trims the two required trailing spaces; this reviewed adapter preserves the input length and the source redistribution rule.',
}
