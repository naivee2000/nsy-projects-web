"""First half of batch 92: parity, hierarchy, matrix, and constrained-path tasks."""
from collections import Counter, deque
from .import_batch_055 import entry

VOWELS=set('aeiou')
def vowels_o(a):
 s=a[0];return max([0]+[j-i for i in range(len(s)) for j in range(i+1,len(s)+1) if all(s[i:j].count(v)%2==0 for v in VOWELS)])
def aligned_o(a):
 on=set();answer=0
 for i,pos in enumerate(a[0],1):on.add(pos);answer+=on==set(range(1,i+1))
 return answer
def inform_o(a):
 n,head,manager,times=a
 def elapsed(i):return 0 if i==head else times[manager[i]]+elapsed(manager[i])
 return max(elapsed(i) for i in range(n))
def lucky_o(a):
 m=a[0];return [m[i][j] for i in range(len(m)) for j in range(len(m[0])) if m[i][j]==min(m[i]) and m[i][j]==max(row[j] for row in m)]
def distance_o(a):return sum(all(abs(x-y)>a[2] for y in a[1]) for x in a[0])
def cinema_o(a):
 n,reserved=a;rows=Counter(r for r,s in reserved if 2<=s<=9);blocked={}
 for r,s in reserved:
  if 2<=s<=9:blocked.setdefault(r,set()).add(s)
 answer=2*(n-len(blocked))
 for seats in blocked.values():answer+=2 if not seats&set(range(2,6)) and not seats&set(range(6,10)) else int(not seats&set(range(4,8)) or not seats&set(range(2,6)) or not seats&set(range(6,10)))
 return answer
def power_o(a):
 def steps(x):
  n=0
  while x!=1:x=3*x+1 if x%2 else x//2;n+=1
  return n
 lo,hi,k=a;return sorted(range(lo,hi+1),key=lambda x:(steps(x),x))[k-1]
def target_o(a):
 out=[]
 for v,i in zip(a[0],a[1]):out.insert(i,v)
 return out
def divisors_o(a):
 total=0
 for n in a[0]:
  ds=[d for d in range(1,n+1) if n%d==0]
  if len(ds)==4:total+=sum(ds)
 return total
def streets_o(a):
 g=a[0];h=len(g);w=len(g[0]);ports={1:{(0,-1),(0,1)},2:{(-1,0),(1,0)},3:{(0,-1),(1,0)},4:{(0,1),(1,0)},5:{(0,-1),(-1,0)},6:{(0,1),(-1,0)}};q=[(0,0)];seen={(0,0)}
 for i,j in q:
  if (i,j)==(h-1,w-1):return True
  for di,dj in ports[g[i][j]]:
   x,y=i+di,j+dj
   if 0<=x<h and 0<=y<w and (-di,-dj) in ports[g[x][y]] and (x,y) not in seen:seen.add((x,y));q.append((x,y))
 return False

def rv(r):return [''.join(r.choice('aeioubcdfg') for _ in range(r.randint(1,18)))]
def ra(r):
 n=r.randint(1,30);x=list(range(1,n+1));r.shuffle(x);return [x]
def ri(r):
 n=r.randint(1,20);manager=[-1]+[r.randrange(i) for i in range(1,n)];times=[r.randint(0,8) for _ in range(n)];bosses=set(manager[1:])
 for i in range(n):
  if i not in bosses:times[i]=0
 return [n,0,manager,times]
def rl(r):
 h,w=r.randint(1,6),r.randint(1,6);values=r.sample(range(1,1000),h*w);return [[values[i*w:(i+1)*w] for i in range(h)]]
def rdist(r):return [[r.randint(-20,20) for _ in range(r.randint(1,15))],[r.randint(-20,20) for _ in range(r.randint(1,15))],r.randint(0,10)]
def rcin(r):
 n=r.randint(1,20);seats={(r.randint(1,n),r.randint(1,10)) for _ in range(r.randint(0,min(40,n*10)))};return [n,[list(x) for x in seats]]
def rpow(r):
 lo=r.randint(1,500);hi=lo+r.randint(0,30);return [lo,hi,r.randint(1,hi-lo+1)]
def rtar(r):
 n=r.randint(1,20);nums=[r.randint(-9,9) for _ in range(n)];return [nums,[r.randint(0,i) for i in range(n)]]
def rdiv(r):return [[r.randint(1,500) for _ in range(r.randint(1,15))]]
def rstreet(r):
 h,w=r.randint(1,5),r.randint(1,5);return [[[r.randint(1,6) for _ in range(w)] for _ in range(h)]]

VOWEL='''def longest_even_vowel_substring(s):
 bit={'a':1,'e':2,'i':4,'o':8,'u':16};first={0:-1};mask=answer=0
 for i,char in enumerate(s):
  mask^=bit.get(char,0)
  if mask in first:answer=max(answer,i-first[mask])
  else:first[mask]=i
 return answer
'''
ALIGNED='''def prefix_aligned_moments(flips):
 maximum=answer=0
 for moment,position in enumerate(flips,1):maximum=max(maximum,position);answer+=maximum==moment
 return answer
'''
INFORM='''def total_informing_minutes(n, head_id, manager, inform_time):
 children=[[] for _ in range(n)]
 for employee,boss in enumerate(manager):
  if boss!=-1:children[boss].append(employee)
 def visit(employee):return inform_time[employee]+max((visit(child) for child in children[employee]),default=0)
 return visit(head_id)
'''
LUCKY='''def lucky_matrix_numbers(matrix):
 row_min=[min(row) for row in matrix];col_max=[max(row[j] for row in matrix) for j in range(len(matrix[0]))]
 return [matrix[i][j] for i in range(len(matrix)) for j in range(len(matrix[0])) if matrix[i][j]==row_min[i]==col_max[j]]
'''
DISTANCE='''def array_distance_value(arr1, arr2, d):
 return sum(all(abs(x-y)>d for y in arr2) for x in arr1)
'''
CINEMA='''def maximum_cinema_families(n, reserved_seats):
 rows={}
 for row,seat in reserved_seats:
  if 2<=seat<=9:rows[row]=rows.get(row,0)|(1<<seat)
 answer=2*(n-len(rows))
 for mask in rows.values():
  left=all(not(mask>>s&1) for s in range(2,6));middle=all(not(mask>>s&1) for s in range(4,8));right=all(not(mask>>s&1) for s in range(6,10));answer+=2 if left and right else int(left or middle or right)
 return answer
'''
POWER='''def kth_collatz_power_value(lo, hi, k):
 memo={1:0}
 def power(x):
  if x not in memo:memo[x]=1+power(3*x+1 if x%2 else x//2)
  return memo[x]
 return sorted(range(lo,hi+1),key=lambda x:(power(x),x))[k-1]
'''
TARGET='''def create_target_array(nums, index):
 target=[]
 for value,at in zip(nums,index):target.insert(at,value)
 return target
'''
DIVISORS='''def sum_values_with_four_divisors(nums):
 answer=0
 for number in nums:
  count=total=0;factor=1
  while factor*factor<=number:
   if number%factor==0:
    other=number//factor;count+=1 if factor==other else 2;total+=factor if factor==other else factor+other
   factor+=1
  if count==4:answer+=total
 return answer
'''
STREETS='''def has_valid_street_path(grid):
 ports={1:{(0,-1),(0,1)},2:{(-1,0),(1,0)},3:{(0,-1),(1,0)},4:{(0,1),(1,0)},5:{(0,-1),(-1,0)},6:{(0,1),(-1,0)}};h,w=len(grid),len(grid[0]);stack=[(0,0)];seen={(0,0)}
 while stack:
  i,j=stack.pop()
  if (i,j)==(h-1,w-1):return True
  for di,dj in ports[grid[i][j]]:
   x,y=i+di,j+dj
   if 0<=x<h and 0<=y<w and (-di,-dj) in ports[grid[x][y]] and (x,y) not in seen:seen.add((x,y));stack.append((x,y))
 return False
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1371:S('longest_even_vowel_substring',[('s','str')],'int',['prefix-sums','bit-manipulation'],['A substring qualifies when a,e,i,o,u each occur an even number of times.','Other lowercase letters do not change vowel parity.'],[(['eleetminicoworoep'],'The longest valid substring has length thirteen.'),(['leetcodeisgreat'],'A parity-state prefix match identifies the longest valid range.')],[[s] for s in ['b','a','aa','ae','aeae','abc','eleet','bcbcbc','aaaaa','aeiouaeiou','abcdeiou','zzzaeaezzz','uoiea','aabbccddeeiioouu']],VOWEL,['''def longest_even_vowel_substring(s):
 bit={'a':1,'e':2,'i':4,'o':8,'u':16};first={0:-1};mask=answer=0
 for i,char in enumerate(s):
  mask^=bit.get(char,0)
  if mask in first:answer=max(answer,i-first[mask])
  first[mask]=i
 return answer
''',VOWEL.replace("bit.get(char,0)","bit.get(char,1)")],['Overwrites the earliest parity position with the latest one.','Treats consonants as toggling the a bit.'],vowels_o,rv,['Encode five vowel parities as a five-bit mask.','Equal masks at two prefix positions mean every intervening vowel count is even.','Store the earliest index for each mask and maximize the distance on repeats.','The earliest equal state always gives the longest substring ending at the current index.'],'O(n)','O(32)',5),
1375:S('prefix_aligned_moments',[('flips','list[int]')],'int',['arrays','prefixes'],['flips is a permutation of positions 1..n turned on in order.','Count moments when every bit from one through the rightmost on bit is on.'],[([[3,2,4,1,5]],'Only moments four and five have an entirely on prefix.'),([[4,1,2,3]],'All four bits align only at the final moment.')],[[x] for x in [[1],[1,2],[2,1],[1,3,2],[3,2,1],[2,1,3],[4,1,2,3],[2,3,4,1],[5,4,3,2,1],[1,2,3,4,5],[3,1,2,5,4],[6,1,2,3,4,5],[2,4,1,3],[3,2,4,1,5]]],ALIGNED,['''def prefix_aligned_moments(flips):
 return sum(position==moment for moment,position in enumerate(flips,1))
''',ALIGNED.replace('maximum=max(maximum,position)','maximum=position')],['Counts only flips already made at their own position and misses later gap-closing moments.','Tracks only the latest flip instead of the rightmost flipped position.'],aligned_o,ra,['After moment m exactly m bits are on.','They form prefix 1..m exactly when the maximum flipped position so far equals m.','Track that maximum and count equal moments.','No holes can remain when m distinct on positions all lie within 1..m.'],'O(n)','O(1)',5),
1376:S('total_informing_minutes',[('n','int'),('head_id','int'),('manager','list[int]'),('inform_time','list[int]')],'int',['trees','depth-first-search'],['manager describes one rooted employee hierarchy.','A manager informs all direct reports simultaneously after inform_time minutes.'],[([1,0,[-1],[0]],'The sole employee needs no time to inform anyone.'),([6,2,[2,2,-1,2,2,2],[0,0,1,0,0,0]],'The head takes one minute to inform all employees directly.')],[[n,h,m,t] for n,h,m,t in [(2,0,[-1,0],[1,0]),(3,0,[-1,0,0],[2,0,0]),(3,0,[-1,0,1],[1,2,0]),(4,0,[-1,0,1,2],[1,1,1,0]),(4,1,[1,-1,1,2],[0,2,3,0]),(5,0,[-1,0,0,1,1],[1,2,0,0,0]),(5,0,[-1,0,1,1,2],[2,1,3,0,0]),(6,0,[-1,0,0,1,1,2],[1,2,3,0,0,0]),(2,1,[1,-1],[0,0]),(3,2,[2,0,-1],[1,0,2]),(4,3,[3,3,0,-1],[1,0,0,2]),(7,0,[-1,0,0,1,1,2,2],[1,2,3,0,0,0,0]),(5,4,[4,4,0,0,-1],[2,0,0,0,1]),(6,5,[5,0,1,2,3,-1],[1,1,1,1,0,1])]],INFORM,['''def total_informing_minutes(n, head_id, manager, inform_time):
 children=[[] for _ in range(n)]
 for employee,boss in enumerate(manager):
  if boss!=-1:children[boss].append(employee)
 def visit(employee):return inform_time[employee]+sum(visit(child) for child in children[employee])
 return visit(head_id)
''',INFORM.replace('return visit(head_id)','return max(visit(head_id),n)')],['Adds branch times as if managers informed reports sequentially.','Forces the result to be at least the employee count.'],inform_o,ri,['Build child lists from manager links.','The finish time below a manager is its inform_time plus the maximum child finish time.','Compute this recurrence by DFS from the head.','Children receive news simultaneously, so only the slowest branch determines completion.'],'O(n)','O(n)',5),
1380:S('lucky_matrix_numbers',[('matrix','list[list[int]]')],'list[int]',['matrices','counting'],['A lucky number is minimum in its row and maximum in its column.','Matrix values are distinct.'],[([[[3,7,8],[9,11,13],[15,16,17]]],'Fifteen is its row minimum and its column maximum.'),([[[7,8],[1,2]]],'Seven is the only row-minimum also maximal in its column.')],[[m] for m in [[[1]],[[1,2]],[[1],[2]],[[1,2],[3,4]],[[4,3],[2,1]],[[1,10],[2,9]],[[10,1],[9,2]],[[3,7,8],[9,11,13],[15,16,17]],[[1,2,3],[6,5,4]],[[9,8,7],[6,5,4],[3,2,1]],[[5,1,9],[4,3,8]],[[2,1],[4,3],[6,5]],[[8,3,4],[1,5,9]],[[10,20,30],[5,15,25]]]],LUCKY,[LUCKY.replace('row_min=[min(row)','row_min=[max(row)'),LUCKY.replace('col_max=[max(row[j]','col_max=[min(row[j]')],['Uses row maxima instead of row minima.','Uses column minima instead of column maxima.'],lucky_o,rl,['Precompute each row minimum and column maximum.','Scan cells and emit those equal to both precomputed extrema.','Preserve row-major order.','The two equalities are exactly the lucky-number definition.'],'O(rows*cols)','O(rows+cols)',3),
1385:S('array_distance_value',[('arr1','list[int]'),('arr2','list[int]'),('d','int')],'int',['arrays','binary-search'],['Count arr1 values whose distance from every arr2 value is greater than d.','d is nonnegative.'],[([[4,5,8],[10,9,1,8],2],'Four and five are farther than two from every arr2 value.'),([[1,4,2,3],[-4,-3,6,10,20,30],3],'Two arr1 values satisfy the strict distance condition.')],[[a,b,d] for a,b,d in [([1],[1],0),([1],[2],0),([1],[2],1),([1,2],[10],3),([1,5],[3],1),([1,5],[3],2),([-1,0,1],[5],3),([10,20],[13,17],2),([0],[100],99),([0],[100],100),([4,5,8],[10,9,1,8],2),([1,2,3],[2],0),([1,2,3],[2],1),([-5,-1],[0,5],2)]],DISTANCE,[DISTANCE.replace('>d','>=d'),DISTANCE.replace('for y in arr2','for y in arr1')],['Treats distance equal to d as acceptable.','Compares arr1 values against their own array instead of arr2.'],distance_o,rdist,['Each arr1 value qualifies only if no arr2 value lies in its closed d-neighborhood.','For direct validation, compare it to every arr2 value; a sorted arr2 can use binary search.','Count values whose every absolute difference is greater than d.','The universal comparison matches the definition exactly.'],'O(n*m)','O(1)',3),
1386:S('maximum_cinema_families',[('n','int'),('reserved_seats','list[list[int]]')],'int',['greedy','bit-manipulation'],['Each four-person family occupies seats 2-5, 4-7, or 6-9 in one row.','Rows without relevant reservations fit two families.'],[([3,[[1,2],[1,3],[1,8],[2,6],[3,1],[3,10]]],'Rows one and two fit one family each; row three fits two.'),([2,[[2,1],[1,8],[2,6]]],'Outer aisle seats do not matter, and valid blocks are checked independently.')],[[n,s] for n,s in [(1,[]),(1,[[1,1]]),(1,[[1,10]]),(1,[[1,2]]),(1,[[1,4]]),(1,[[1,6]]),(1,[[1,8]]),(1,[[1,4],[1,7]]),(2,[]),(2,[[1,2]]),(3,[[2,5]]),(3,[[1,1],[2,10]]),(4,[[1,2],[2,4],[3,6],[4,8]]),(100,[[1,2]])]],CINEMA,[CINEMA.replace('2*(n-len(rows))','n-len(rows)'),CINEMA.replace('left and right','left or right')],['Allocates only one family in every completely free row.','Counts two families when either outer block alone is free.'],cinema_o,rcin,['Only reservations in seats 2 through 9 affect family blocks.','Encode each affected row as a bit mask; untouched rows contribute two.','For an affected row, test left 2-5, middle 4-7, and right 6-9; two fit only when both outer blocks fit.','These are the only allowed blocks, so the case analysis is exhaustive.'],'O(reservations)','O(affected rows)',5),
1387:S('kth_collatz_power_value',[('lo','int'),('hi','int'),('k','int')],'int',['dynamic-programming','sorting'],['Power is the number of Collatz steps to reach one.','Sort by power then integer value and return the one-based kth value.'],[([12,15,2],'Powers order 12,13,14,15 with thirteen second under the tie rules.'),([1,1,1],'One has power zero and is the sole candidate.')],[[l,h,k] for l,h,k in [(1,2,1),(1,2,2),(2,3,1),(5,10,3),(10,20,1),(10,20,11),(12,15,1),(12,15,4),(7,7,1),(20,30,5),(1,50,25),(100,120,10),(50,60,6),(200,250,20)]],POWER,['''def kth_collatz_power_value(lo, hi, k):
 return list(range(lo,hi+1))[k-1]
''',POWER.replace('(power(x),x)','(power(x),-x)')],['Sorts only by numeric value and ignores Collatz power.','Breaks equal-power ties by larger integer first.'],power_o,rpow,['Memoize Collatz power values.','Recursively use one plus the power of x/2 when even or 3x+1 when odd.','Sort the inclusive range by (power,value) and choose k-1.','The recurrence follows the unique Collatz trajectory, and the tuple key implements both rankings.'],'O(range*trajectory)','O(visited values)',5),
1389:S('create_target_array',[('nums','list[int]'),('index','list[int]')],'list[int]',['arrays','simulation'],['At step i insert nums[i] at index[i] in the current target.','0 <= index[i] <= i.'],[([[0,1,2,3,4],[0,1,2,2,1]],'Sequential insertion produces 0,4,1,3,2.'),([[1,2,3,4,0],[0,1,2,3,0]],'The final zero is inserted at the front.')],[[a,b] for a,b in [([1],[0]),([1,2],[0,0]),([1,2],[0,1]),([1,2,3],[0,0,0]),([1,2,3],[0,1,1]),([1,2,3],[0,1,2]),([0,1,2,3,4],[0,1,2,2,1]),([5,4,3],[0,0,1]),([1,1,1],[0,1,1]),([-1,0,1],[0,0,1]),([9,8,7,6],[0,1,1,2]),([2,4,6,8],[0,0,2,1]),([3,1,4,1,5],[0,0,1,1,2]),([10,20,30],[0,1,0])]],TARGET,[TARGET.replace('target.insert(at,value)','target.append(value)'),TARGET.replace('zip(nums,index)','zip(index,nums)')],['Appends instead of inserting at the requested positions.','Swaps the value and insertion-index arrays.'],target_o,rtar,['Maintain the target built from the processed prefix.','Insert each nums[i] at index[i] using list insertion.','Continue in input order.','The operation directly reproduces the specified construction step by step.'],'O(n²)','O(n)',3),
1390:S('sum_values_with_four_divisors',[('nums','list[int]')],'int',['math','number-theory'],['For each number having exactly four positive divisors, add all four divisors.','Numbers with any other divisor count contribute zero.'],[([[21,4,7]],'Twenty-one has divisors 1,3,7,21 summing to 32; four and seven do not qualify.'),([[21,21]],'Each occurrence contributes independently, for total 64.')],[[x] for x in [[1],[2],[4],[6],[8],[10],[16],[21],[27],[30],[49],[6,10],[4,7],[100,14]]],DIVISORS,[DIVISORS.replace('count==4','count>=4'),DIVISORS.replace('factor*factor<=number','factor*factor<number')],['Includes numbers with more than four divisors.','Skips a square-root divisor and miscounts perfect squares.'],divisors_o,rdiv,['Enumerate divisor pairs up to the square root.','For each factor, add it and its paired quotient, counting one only when equal.','Contribute the accumulated sum only when the final count is exactly four.','Every divisor belongs to exactly one factor pair around the square root.'],'O(sum sqrt(n))','O(1)',5),
1391:S('has_valid_street_path',[('grid','list[list[int]]')],'bool',['graphs','matrices'],['Street types 1..6 have fixed openings; adjacent cells connect only when both face each other.','Determine reachability from top-left to bottom-right without rotating tiles.'],[([[[2,4,3],[6,5,2]]],'Compatible openings form a path through every turn to the bottom-right.'),([[[1,2,1],[1,2,1]]],'The start’s right opening meets a tile without a left opening, so no valid path exists.')],[[g] for g in [[[1]],[[1,1]],[[1,2]],[[2],[2]],[[1],[1]],[[2,4,3],[6,5,2]],[[1,2,1],[1,2,1]],[[1,1,2]],[[2,2],[2,2]],[[4,3],[6,5]],[[6,1,3]],[[2],[5],[2]],[[1,3],[4,5]],[[3,4],[6,5]]]],STREETS,[STREETS.replace('(-di,-dj) in ports[grid[x][y]]','(di,dj) in ports[grid[x][y]]'),STREETS.replace('stack=[(0,0)]','stack=[(h-1,w-1)]')],['Accepts neighbors opening in the same direction instead of back toward the current tile.','Searches from the destination but still tests for destination immediately, always returning true.'],streets_o,rstreet,['Map every tile type to its two opening direction vectors.','Traverse from the start through an opening only when the neighbor has the opposite opening.','Mark visited cells to avoid cycles and accept on reaching the destination.','The graph edges are exactly the mutually connected street borders, so graph reachability solves the problem.'],'O(rows*cols)','O(rows*cols)',5),
}
