"""Reviewed tree, recursive grid, interval, prefix, and greedy imports."""
from collections import Counter, deque
from functools import lru_cache
from itertools import permutations, product
from math import isqrt

from .import_batch_055 import entry

MOD=1_000_000_007

def tree_data(serial):
 if not serial:return [],[]
 values=[serial[0]];edges=[];queue=deque([0]);position=1
 while queue and position<len(serial):
  parent=queue.popleft()
  for _ in range(2):
   if position>=len(serial):break
   value=serial[position];position+=1
   if value is not None:
    child=len(values);values.append(value);edges.append((parent,child));queue.append(child)
 return values,edges

def coins_oracle(a):
 values,edges=tree_data(a[0]);n=len(values);adj=[set() for _ in values]
 for x,y in edges:adj[x].add(y);adj[y].add(x)
 balance=[v-1 for v in values];degree=[len(x) for x in adj];leaves=deque(i for i,d in enumerate(degree) if d<=1);moves=0;done=set()
 while leaves:
  node=leaves.popleft()
  if node in done:continue
  done.add(node);moves+=abs(balance[node])
  for other in adj[node]:
   if other not in done:
    balance[other]+=balance[node];degree[other]-=1
    if degree[other]<=1:leaves.append(other)
 return moves
def paths_oracle(a):
 grid=a[0];rows=len(grid);cols=len(grid[0]);start=next((r,c) for r in range(rows) for c in range(cols) if grid[r][c]==1);walkable=sum(v!=-1 for row in grid for v in row)
 def visit(r,c,seen):
  if grid[r][c]==2:return len(seen)==walkable
  return sum(visit(nr,nc,seen|{(nr,nc)}) for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)) for nr,nc in [(r+dr,c+dc)] if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]!=-1 and (nr,nc) not in seen)
 return visit(*start,{start})
def triples_oracle(a):
 nums=a[0];return sum((x&y&z)==0 for x in nums for y in nums for z in nums)
def tickets_oracle(a):
 days,costs=a;travel=set(days)
 @lru_cache(None)
 def solve(day):
  if day>days[-1]:return 0
  if day not in travel:return solve(day+1)
  return min(cost+solve(day+duration) for cost,duration in zip(costs,(1,7,30)))
 return solve(days[0])
def even_queries_oracle(a):
 nums,queries=a;nums=nums[:];out=[]
 for value,index in queries:nums[index]+=value;out.append(sum(x for x in nums if x%2==0))
 return out
def interval_oracle(a):
 first,second=a;return [[max(x,u),min(y,v)] for x,y in first for u,v in second if max(x,u)<=min(y,v)]
def leaf_string_oracle(a):
 values,edges=tree_data(a[0]);children=[[] for _ in values]
 for x,y in edges:children[x].append(y)
 answers=[]
 def walk(node,path):
  path=chr(97+values[node])+path
  if not children[node]:answers.append(path)
  for child in children[node]:walk(child,path)
 walk(0,'');return min(answers)
def array_add_oracle(a):return [int(c) for c in str(int(''.join(map(str,a[0])))+a[1])]
def equations_oracle(a):
 equations=a[0];reach=[[i==j for j in range(26)] for i in range(26)]
 for e in equations:
  if e[1:3]=='==':x,y=ord(e[0])-97,ord(e[3])-97;reach[x][y]=reach[y][x]=True
 for k in range(26):
  for i in range(26):
   for j in range(26):reach[i][j]|=reach[i][k] and reach[k][j]
 return all(e[1:3]!='!=' or not reach[ord(e[0])-97][ord(e[3])-97] for e in equations)
def calculator_oracle(a):
 start,target=a
 if target<=start:return start-target
 q=deque([(start,0)]);seen={start};limit=2*target+2
 while q:
  value,steps=q.popleft()
  if value==target:return steps
  for nxt in (value*2,value-1):
   if 0<nxt<=limit and nxt not in seen:seen.add(nxt);q.append((nxt,steps+1))
def distinct_oracle(a):
 nums,k=a;return sum(len(set(nums[i:j]))==k for i in range(len(nums)) for j in range(i+1,len(nums)+1))
def cousins_oracle(a):
 values,edges=tree_data(a[0]);x,y=a[1:];children=[[] for _ in values]
 for p,c in edges:children[p].append(c)
 info={values[0]:(0,None)};q=deque([0])
 while q:
  p=q.popleft()
  for c in children[p]:info[values[c]]=(info[values[p]][0]+1,p);q.append(c)
 return info[x][0]==info[y][0] and info[x][1]!=info[y][1]
def oranges_oracle(a):
 grid=[row[:] for row in a[0]];minutes=0
 while True:
  rot={(nr,nc) for r,row in enumerate(grid) for c,v in enumerate(row) if v==2 for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)) for nr,nc in [(r+dr,c+dc)] if 0<=nr<len(grid) and 0<=nc<len(row) and grid[nr][nc]==1}
  if not rot:break
  for r,c in rot:grid[r][c]=2
  minutes+=1
 return -1 if any(1 in row for row in grid) else minutes
def flips_oracle(a):
 nums,k=a;n=len(nums);best=None
 for mask in range(1<<(n-k+1)):
  out=nums[:]
  for i in range(n-k+1):
   if mask>>i&1:
    for j in range(i,i+k):out[j]^=1
  if all(out):best=mask.bit_count() if best is None else min(best,mask.bit_count())
 return -1 if best is None else best
def squareful_oracle(a):
 def square(x):return isqrt(x)**2==x
 return sum(all(square(p[i]+p[i+1]) for i in range(len(p)-1)) for p in set(permutations(a[0])))
def judge_oracle(a):
 n,trust=a;score=[0]*n
 for x,y in trust:score[x-1]-=1;score[y-1]+=1
 return next((i+1 for i,v in enumerate(score) if v==n-1),-1)
def common_oracle(a):
 words=a[0];answer=Counter(words[0])
 for word in words[1:]:answer&=Counter(word)
 return sorted(answer.elements())
def valid_oracle(a):
 s=a[0]
 while 'abc' in s:s=s.replace('abc','')
 return not s
def ones_oracle(a):
 nums,k=a;return max((j-i for i in range(len(nums)) for j in range(i+1,len(nums)+1) if nums[i:j].count(0)<=k),default=0)
def negations_oracle(a):
 nums,k=a;best=-10**9
 for mask in range(1<<len(nums)):
  used=mask.bit_count()
  if used<=k and (k-used)%2==0:best=max(best,sum(-x if mask>>i&1 else x for i,x in enumerate(nums)))
 return best

def random_coin_tree(r):
 n=r.randint(1,9);coins=[0]*n
 for _ in range(n):coins[r.randrange(n)]+=1
 return [coins]
def random_path_grid(r):
 rows,cols=r.randint(1,3),r.randint(2,4);cells=rows*cols;start,end=r.sample(range(cells),2);grid=[[0]*cols for _ in range(rows)];grid[start//cols][start%cols]=1;grid[end//cols][end%cols]=2
 for i in range(cells):
  if i not in (start,end) and r.random()<.2:grid[i//cols][i%cols]=-1
 return [grid]
def random_small_nums(r):return [[r.randrange(16) for _ in range(r.randint(1,7))]]
def random_tickets(r):return [sorted(r.sample(range(1,50),r.randint(1,12))),[r.randint(1,10),r.randint(5,25),r.randint(15,50)]]
def random_queries(r):
 nums=[r.randint(-10,10) for _ in range(r.randint(1,9))];return [nums,[[r.randint(-8,8),r.randrange(len(nums))] for _ in range(r.randint(1,9))]]
def random_intervals(r):
 def make():
  out=[];point=0
  for _ in range(r.randint(0,6)):
   left=point+r.randint(0,3);right=left+r.randint(0,4);out.append([left,right]);point=right+1+r.randint(0,2)
  return out
 return [make(),make()]
def random_leaf_tree(r):return [[r.randrange(6) for _ in range(r.randint(1,15))]]
def random_array_add(r):return [[int(c) for c in str(r.randint(0,999999))],r.randint(0,999999)]
def random_equations(r):return [[''.join((r.choice('abcde'),r.choice(('==','!=')),r.choice('abcde'))) for _ in range(r.randint(1,10))]]
def random_calc(r):return [r.randint(1,20),r.randint(1,30)]
def random_distinct(r):
 nums=[r.randrange(5) for _ in range(r.randint(1,12))];return [nums,r.randint(1,5)]
def random_cousins(r):
 n=r.randint(3,15);tree=list(range(1,n+1));x,y=r.sample(tree[1:],2);return [tree,x,y]
def random_oranges(r):
 rows,cols=r.randint(1,4),r.randint(1,4);return [[[r.randrange(3) for _ in range(cols)] for _ in range(rows)]]
def random_flips(r):
 nums=[r.randrange(2) for _ in range(r.randint(1,10))];return [nums,r.randint(1,len(nums))]
def random_squareful(r):return [[r.randint(0,20) for _ in range(r.randint(1,7))]]
def random_trust(r):
 n=r.randint(1,8);return [n,[[i,j] for i in range(1,n+1) for j in range(1,n+1) if i!=j and r.random()<.2]]
def random_words(r):return [[''.join(r.choice('abcde') for _ in range(r.randint(1,7))) for _ in range(r.randint(1,7))]]
def random_valid(r):
 s=''
 for _ in range(r.randint(0,6)):
  i=r.randint(0,len(s));s=s[:i]+'abc'+s[i:]
 if r.random()<.3:s+=r.choice('ac')
 return [s or 'abc']
def random_ones(r):
 nums=[r.randrange(2) for _ in range(r.randint(1,15))];return [nums,r.randint(0,len(nums))]
def random_negations(r):return [[r.randint(-10,10) for _ in range(r.randint(1,8))],r.randint(0,8)]

COINS='''def distribute_tree_coins(root):
 moves=0
 def balance(node):
  nonlocal moves
  if node is None:return 0
  left=balance(node.left);right=balance(node.right);moves+=abs(left)+abs(right)
  return node.val+left+right-1
 balance(root);return moves
'''
PATHS='''def unique_covering_paths(grid):
 rows,cols=len(grid),len(grid[0]);remaining=sum(v!=-1 for row in grid for v in row);start=next((r,c) for r in range(rows) for c in range(cols) if grid[r][c]==1)
 def dfs(r,c,left):
  if grid[r][c]==2:return int(left==1)
  old=grid[r][c];grid[r][c]=-1;answer=0
  for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
   nr,nc=r+dr,c+dc
   if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]!=-1:answer+=dfs(nr,nc,left-1)
  grid[r][c]=old;return answer
 return dfs(*start,remaining)
'''
TRIPLES='''def zero_and_triple_count(nums):
 from collections import Counter
 pairs=Counter(x&y for x in nums for y in nums)
 return sum(count for value,count in pairs.items() for z in nums if value&z==0)
'''
TICKETS='''def minimum_ticket_cost(days, costs):
 dp={0:0}
 for day in days:dp[day]=min(dp[max((d for d in dp if d<day),default=0)]+costs[0],dp[max((d for d in dp if d<day-6),default=0)]+costs[1],dp[max((d for d in dp if d<day-29),default=0)]+costs[2])
 return dp[days[-1]]
'''
EVEN='''def even_sums_after_queries(nums, queries):
 total=sum(x for x in nums if x%2==0);answer=[]
 for value,index in queries:
  if nums[index]%2==0:total-=nums[index]
  nums[index]+=value
  if nums[index]%2==0:total+=nums[index]
  answer.append(total)
 return answer
'''
INTERVALS='''def interval_intersections(first_list, second_list):
 answer=[];i=j=0
 while i<len(first_list) and j<len(second_list):
  left=max(first_list[i][0],second_list[j][0]);right=min(first_list[i][1],second_list[j][1])
  if left<=right:answer.append([left,right])
  if first_list[i][1]<second_list[j][1]:i+=1
  else:j+=1
 return answer
'''
LEAF='''def smallest_leaf_string(root):
 best=None
 def dfs(node,path):
  nonlocal best
  if node is None:return
  path=chr(97+node.val)+path
  if node.left is None and node.right is None:best=path if best is None else min(best,path)
  dfs(node.left,path);dfs(node.right,path)
 dfs(root,'');return best
'''
ARRAYADD='''def add_to_array_number(num, k):
 answer=[];i=len(num)-1;carry=k
 while i>=0 or carry:
  if i>=0:carry+=num[i];i-=1
  answer.append(carry%10);carry//=10
 return (num[:i+1] if i>=0 else [])+answer[::-1]
'''
EQUATIONS='''def equations_are_satisfiable(equations):
 parent=list(range(26))
 def find(x):
  if parent[x]!=x:parent[x]=find(parent[x])
  return parent[x]
 for e in equations:
  if e[1:3]=='==':parent[find(ord(e[0])-97)]=find(ord(e[3])-97)
 return all(e[1:3]=='==' or find(ord(e[0])-97)!=find(ord(e[3])-97) for e in equations)
'''
CALC='''def broken_calculator_steps(start_value, target):
 steps=0
 while target>start_value:
  target=target//2 if target%2==0 else target+1;steps+=1
 return steps+start_value-target
'''
DISTINCT='''def subarrays_with_k_distinct(nums, k):
 def at_most(limit):
  counts={};left=answer=0
  for right,value in enumerate(nums):
   counts[value]=counts.get(value,0)+1
   while len(counts)>limit:
    old=nums[left];counts[old]-=1;left+=1
    if counts[old]==0:del counts[old]
   answer+=right-left+1
  return answer
 return at_most(k)-at_most(k-1)
'''
COUSINS='''def are_tree_cousins(root, x, y):
 queue=[(root,None)]
 while queue:
  found={node.val:parent for node,parent in queue if node.val in (x,y)}
  if found:return len(found)==2 and found[x] is not found[y]
  queue=[(child,node) for node,parent in queue for child in (node.left,node.right) if child]
 return False
'''
ORANGES='''def minutes_to_rot_all(grid):
 rows,cols=len(grid),len(grid[0]);queue=__import__('collections').deque((r,c,0) for r in range(rows) for c in range(cols) if grid[r][c]==2);fresh=sum(v==1 for row in grid for v in row);minutes=0
 while queue:
  r,c,minutes=queue.popleft()
  for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
   nr,nc=r+dr,c+dc
   if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==1:grid[nr][nc]=2;fresh-=1;queue.append((nr,nc,minutes+1))
 return -1 if fresh else minutes
'''
FLIPS='''def minimum_k_bit_flips(nums, k):
 active=answer=0;started=[0]*len(nums)
 for i,bit in enumerate(nums):
  if i>=k:active^=started[i-k]
  if bit==active:
   if i+k>len(nums):return -1
   started[i]=1;active^=1;answer+=1
 return answer
'''
SQUAREFUL='''def squareful_permutation_count(nums):
 from collections import Counter
 from math import isqrt
 counts=Counter(nums)
 def dfs(previous,left):
  if not left:return 1
  answer=0
  for value in counts:
   if counts[value] and (previous is None or isqrt(previous+value)**2==previous+value):counts[value]-=1;answer+=dfs(value,left-1);counts[value]+=1
  return answer
 return dfs(None,len(nums))
'''
JUDGE='''def find_town_judge(n, trust):
 score=[0]*(n+1)
 for a,b in trust:score[a]-=1;score[b]+=1
 return next((person for person in range(1,n+1) if score[person]==n-1),-1)
'''
COMMON='''def common_characters(words):
 from collections import Counter
 shared=Counter(words[0])
 for word in words[1:]:shared&=Counter(word)
 return sorted(shared.elements())
'''
VALID='''def is_valid_abc_expansion(s):
 stack=[]
 for c in s:
  stack.append(c)
  if len(stack)>=3 and stack[-3:]==['a','b','c']:del stack[-3:]
 return not stack
'''
ONES='''def longest_ones_after_flips(nums, k):
 left=zeros=best=0
 for right,value in enumerate(nums):
  zeros+=value==0
  while zeros>k:zeros-=nums[left]==0;left+=1
  best=max(best,right-left+1)
 return best
'''
NEGATE='''def maximum_sum_after_negations(nums, k):
 nums=sorted(nums)
 for i in range(len(nums)):
  if k and nums[i]<0:nums[i]=-nums[i];k-=1
 if k%2:nums[nums.index(min(nums))]*=-1
 return sum(nums)
'''

def lesson(a,b,c,d):return [a,b,c,d],d
def E(name,params,ret,topics,constraints,examples,bounds,ref,wrongs,reasons,oracle,gen,hints,time,space,diff):
 return entry(name,params,ret,topics,constraints,examples,bounds,ref,wrongs,reasons,oracle,gen,*lesson(*hints),time,space,diff)

BATCH={
979:E('distribute_tree_coins',[('root','TreeNode')],'int',['trees','recursion','depth-first-search'],['The tree has n nodes and exactly n coins total.','One move transfers one coin across one parent-child edge; return minimum moves.'],[([[3,0,0]],'Two coins move from the root, one to each child.'),([[0,3,0]],'Two moves send coins from the left child through the root to the right child.')],[[t] for t in [[1],[2,0],[0,2],[3,0,0],[0,3,0],[1,1,1],[4,0,None,0,0],[0,1,2],[0,0,3],[1,0,0,2],[0,2,0,1],[5,0,0,0,0],[0,0,0,4],[2,0,1]]],COINS,[COINS.replace('abs(left)+abs(right)','left+right'),COINS.replace('node.val+left+right-1','node.val-1')],['Adds signed balances instead of required edge transfers.','Does not propagate child surplus or deficit upward.'],coins_oracle,random_coin_tree,['Each subtree must send its coin surplus—or receive its deficit—through its parent edge.','Postorder returns subtree coins minus subtree nodes.','Add absolute child balances to moves and return node.val+left+right-1.','Every cut requires exactly its imbalance in transfers, and postorder realizes all those lower bounds.'],'O(n)','O(height)',5),
980:E('unique_covering_paths',[('grid','list[list[int]]')],'int',['backtracking','matrices','recursion'],['Walk orthogonally from 1 to 2 while visiting every non-obstacle square exactly once.','Return the number of valid paths.'],[([[[1,0,0,0],[0,0,0,0],[0,0,2,-1]]],'Exactly two routes cover all eleven walkable squares before reaching the end.'),([[[1,0,0,0],[0,0,0,0],[0,0,0,2]]],'Four Hamiltonian routes cover every square.')],[[g] for g in [[[1,2]],[[1,0,2]],[[1,-1,2]],[[1,0],[0,2]],[[1,-1],[0,2]],[[1,0,0],[0,-1,2]],[[1,0,2],[0,0,0]],[[0,1],[2,0]],[[1,0,0,2]],[[1,0],[-1,2]],[[1,0,0],[0,0,2]],[[1,-1,0],[0,0,2]],[[1,0,-1],[0,0,2]],[[1,0,0],[0,-1,0],[0,0,2]]]],PATHS,[PATHS.replace('left==1','left>=1'),PATHS.replace('grid[r][c]=-1','grid[r][c]=old')],['Allows reaching the destination before every square is visited.','Fails to mark visited squares and counts revisiting walks.'],paths_oracle,random_path_grid,['This is a Hamiltonian-path count on the walkable grid cells.','Backtrack from the start while counting remaining unvisited cells.','Mark a cell blocked, recurse to unvisited neighbors, restore it, and accept end only when one cell remains.','Mark/restore enforces exactly-once visits while exploring every possible route.'],'O(4^walkable)','O(walkable)',8),
982:E('zero_and_triple_count',[('nums','list[int]')],'int',['bit-manipulation','counting'],['Count ordered triples of indices (i,j,k) whose three values AND to zero.','Indices may repeat.'],[([[2,1,3]],'Twelve of the twenty-seven ordered index triples have AND zero.'),([[0,0]],'Every one of the eight ordered triples has AND zero.')],[[x] for x in ([0],[1],[0,0],[1,1],[0,1],[1,2],[1,2,3],[7,7,0],[2,2,1],[3,5,6],[0,1,2,4],[15,7,3,1],[2,1,3],[8,4,2,1])],TRIPLES,[TRIPLES.replace('value&z==0','value|z==0'),TRIPLES.replace('for x in nums for y in nums','for x,y in zip(nums,nums)')],['Uses OR instead of AND for the final compatibility test.','Counts only same-position pairs rather than all ordered pairs.'],triples_oracle,random_small_nums,['Precompute how often each pairwise AND value occurs.','For each pair-mask, every number disjoint from it completes that many triples.','Counter(x&y for all ordered pairs), then sum count when mask&z==0.','Grouping the first two indices by AND preserves multiplicity and makes the third test direct.'],'O(n^2+n*masks)','O(masks)',8),
983:E('minimum_ticket_cost',[('days','list[int]'),('costs','list[int]')],'int',['dynamic-programming'],['days is strictly increasing; passes cover 1, 7, or 30 consecutive calendar days.','Return minimum cost covering every travel day.'],[([[1,4,6,7,8,20],[2,7,15]],'A seven-day pass for days 1–7 plus one-day passes for 8 and 20 costs eleven.'),([[1,2,3,4,5,6,7,8,9,10,30,31],[2,7,15]],'Two seven-day passes and two one-day passes cost seventeen.')],[[d,c] for d,c in [([1],[2,7,15]),([1,2],[2,7,15]),([1,7],[2,7,15]),([1,8],[2,7,15]),([1,30],[2,7,15]),([1,2,3,4,5,6,7],[3,8,20]),([1,4,6,7,8,20],[2,7,15]),([10,11,12],[5,6,20]),([1,15,30],[2,5,6]),([1,2,8,9,15,16],[2,7,20]),([100,101,130],[4,9,20]),([1,31,61],[3,8,15]),([1,2,3,28,29,30],[2,8,14]),([5,6,7,8,9,10,11,12],[2,7,50])]],TICKETS,[TICKETS.replace("(1,7,30)","(1,6,29)"),TICKETS.replace('min(','max(')],['Makes seven- and thirty-day passes expire one day early.','Chooses the most expensive plan.'],tickets_oracle,random_tickets,['At each uncovered travel day, choose which duration pass begins there.','Memoize the minimum cost from a calendar day onward.','Skip nontravel days; on travel days minimize cost+solve(day+duration).','Every valid plan buys some pass for the first uncovered day, so the recurrence is exhaustive.'],'O(last day)','O(last day)',5),
985:E('even_sums_after_queries',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['arrays','simulation'],['Each query [value,index] adds value to nums[index].','After each query return the sum of all current even values.'],[([[1,2,3,4],[[1,0],[-3,1],[-4,0],[2,3]]],'Updating only the changed value yields even sums 8,6,2,4.'),([[1],[[4,0]]],'The updated value five is odd, so the even sum is zero.')],[[n,q] for n,q in [([1],[[1,0]]),([2],[[1,0]]),([0],[[0,0]]),([1,2],[[1,0]]),([1,2],[[2,1]]),([-2,3],[[1,1]]),([1,2,3],[[1,0],[1,1]]),([0,0],[[2,0],[-2,1]]),([5,-5],[[5,0],[5,1]]),([2,4],[[2,0],[-1,1]]),([1,1,1],[[1,0],[1,1],[1,2]]),([-4,-2],[[3,0],[3,1]]),([10,1],[[0,0],[1,1]]),([3,6,9],[[3,0],[-3,1],[1,2]])]],EVEN,[EVEN.replace('if nums[index]%2==0:total-=nums[index]',''),EVEN.replace('total+=nums[index]','total-=nums[index]')],['Leaves the old even value in the running total.','Subtracts newly even values instead of adding them.'],even_queries_oracle,random_queries,['Only the queried position can change the even sum.','Remove its old contribution when even, mutate it, then add its new contribution when even.','Append the running total after every query.','All untouched values retain parity and value, so their contribution never needs recomputation.'],'O(n+queries)','O(queries output)',5),
986:E('interval_intersections',[('firstList','list[list[int]]'),('secondList','list[list[int]]')],'list[list[int]]',['intervals','two-pointers'],['Each list contains sorted, pairwise-disjoint closed intervals.','Return all nonempty intersections in increasing order.'],[([[[0,2],[5,10],[13,23],[24,25]],[[1,5],[8,12],[15,24],[25,26]]],'The two-pointer scan produces six closed intersections, including touching endpoints.'),([[[1,3],[5,9]],[]],'An empty second list has no intersections.')],[[a,b] for a,b in [([],[]),([[1,2]],[]),([],[[1,2]]),([[1,3]],[[2,4]]),([[1,2]],[[3,4]]),([[1,2]],[[2,3]]),([[1,5]],[[2,3]]),([[2,3]],[[1,5]]),([[1,2],[5,6]],[[2,5]]),([[0,0]],[[0,0]]),([[-5,-1]],[[ -3,2]]),([[1,4],[7,10]],[[2,3],[8,12]]),([[1,2],[4,5]],[[0,10]]),([[0,2],[5,10]],[[1,5],[8,12]])]],INTERVALS,[INTERVALS.replace('left<=right','left<right'),INTERVALS.replace('else:j+=1','else:i+=1')],['Drops valid one-point intersections.','Advances the wrong pointer when the second interval ends first.'],interval_oracle,random_intervals,['Two current intervals intersect from max starts to min ends when that range is nonempty.','Advance whichever interval ends first.','Append [max(lefts),min(rights)] when start<=end, then move the earlier end pointer.','The earlier-ending interval cannot intersect any later interval in the other list after this comparison.'],'O(a+b)','O(output)',5),
988:E('smallest_leaf_string',[('root','TreeNode')],'str',['trees','recursion','depth-first-search'],['Node values 0..25 map to a..z.','Build strings from leaf to root and return the lexicographically smallest.'],[([[0,1,2,3,4,3,4]],'Leaf-to-root candidates include dba and dca; dba is smallest.'),([[25,1,3,1,3,0,2]],'The smallest leaf-origin string is adz.')],[[t] for t in [[0],[1],[0,1],[0,None,1],[0,1,2],[2,1,0],[25,0,1],[0,1,2,3],[3,2,1,0],[0,0,0],[1,0,2,3,4],[5,4,3,2,1],[0,25,1,None,None,0,2],[2,2,2,1,3]]],LEAF,[LEAF.replace("chr(97+node.val)+path","path+chr(97+node.val)"),LEAF.replace('min(best,path)','max(best,path)')],['Builds root-to-leaf strings in the wrong direction.','Chooses the lexicographically largest leaf string.'],leaf_string_oracle,random_leaf_tree,['Comparison is on leaf-to-root strings, so prepend each visited character.','DFS carries the current reversed path and compares only at leaves.','At a leaf update best=min(best,path); otherwise recurse into children.','Every leaf contributes exactly its required string and the global minimum answers the problem.'],'O(n*height)','O(height)',5),
989:E('add_to_array_number',[('num','list[int]'),('k','int')],'list[int]',['arrays','math'],['num is a decimal digit array without leading zero unless it is [0].','Return the digit array for its value plus nonnegative k.'],[([[1,2,0,0],34],'1200+34=1234, so return digits 1,2,3,4.'),([[2,7,4],181],'274+181=455.')],[[n,k] for n,k in [([0],0),([0],5),([1],9),([9],1),([9,9],1),([1,0],90),([1,2,3],0),([1,2,3],877),([9,9,9],999),([5,0,0],500),([1,0,0,0],1),([8,9],11),([2,7,4],181),([1,2,0,0],34)]],ARRAYADD,[ARRAYADD.replace('carry+=num[i]','carry=num[i]'),ARRAYADD.replace('answer[::-1]','answer')],['Overwrites rather than adds the incoming carry.','Returns computed digits in reverse order.'],array_add_oracle,random_array_add,['Treat k as the initial carry and add from the least significant digit.','Repeatedly append carry modulo ten and divide carry by ten.','While digits or carry remain, add the next digit, emit one result digit, then reverse.','This is ordinary column addition without converting an arbitrarily long input array to an integer.'],'O(len(num)+log k)','O(output)',3),
990:E('equations_are_satisfiable',[('equations','list[str]')],'bool',['union-find','graphs'],['Each equation compares two lowercase one-letter variables with == or !=.','Return whether all equations can hold simultaneously.'],[([['a==b','b!=a']],'Equality makes a and b identical, contradicting their inequality.'),([['b==a','a==b']],'Both equations consistently require the same equality.')],[[e] for e in [['a==a'],['a!=a'],['a==b'],['a!=b'],['a==b','b==c','a!=c'],['a==b','b!=c'],['a!=b','b!=c','a==c'],['a==b','c==d','a!=d'],['x==y','y==z','x==z'],['x==y','y!=z','x==z'],['a!=b','b!=a'],['a==b','b==a'],['a==b','c==b','a!=c'],['a!=z','z==z']]],EQUATIONS,[EQUATIONS.replace("e[1:3]=='!='","e[1:3]=='=='"),EQUATIONS.replace("if e[1:3]=='=='","if e[1:3]=='!='")],['Checks equality equations for contradiction instead of inequalities.','Unions variables connected by inequality.'],equations_oracle,random_equations,['Equalities form connected components that must share one value.','Union every equality first, then inspect inequalities.','Reject an inequality whose endpoints have the same representative.','Components satisfy all equalities, and distinct component values can satisfy every remaining inequality.'],'O(e alpha(26))','O(26)',5),
991:E('broken_calculator_steps',[('startValue','int'),('target','int')],'int',['greedy','math'],['Starting from startValue, either double the display or subtract one.','Return the minimum operations to reach target.'],[([2,3],'Double 2 to 4, then subtract one: two operations.'),([5,8],'Subtract to 4, then double to 8: two operations.')],[[s,t] for s,t in [(1,1),(2,1),(2,2),(2,3),(2,4),(3,10),(5,8),(10,1),(1,16),(4,15),(7,20),(20,7),(9,9),(3,19)]],CALC,[CALC.replace('target+1','target-1'),CALC.replace('start_value-target','target-start_value')],['Moves an odd target downward, which cannot reverse a final subtraction.','Adds the final direct-decrement distance with the wrong sign.'],calculator_oracle,random_calc,['Reverse the operations: an even target can be halved; an odd target must first be incremented.','Work backward while target exceeds startValue.','Even: target//=2; odd: target+=1; finally add startValue-target decrements.','These forced reverse choices dominate forward search and reduce the target exponentially.'],'O(log target+start-target)','O(1)',5),
992:E('subarrays_with_k_distinct',[('nums','list[int]'),('k','int')],'int',['sliding-window','hash-maps'],['Count contiguous subarrays containing exactly k distinct integers.','Return the total count.'],[([[1,2,1,2,3],2],'Seven subarrays contain exactly two distinct values.'),([[1,2,1,3,4],3],'Three subarrays contain exactly three distinct values.')],[[n,k] for n,k in [([1],1),([1],2),([1,1],1),([1,2],1),([1,2],2),([1,2,1],2),([1,2,3],2),([1,1,2,2],2),([1,2,1,2,3],1),([1,2,1,2,3],3),([0,0,0],1),([1,2,3,4],4),([1,2,3,1,2],3),([2,1,2,1,2],2)]],DISTINCT,[DISTINCT.replace('at_most(k)-at_most(k-1)','at_most(k)'),DISTINCT.replace('len(counts)>limit','len(counts)>=limit')],['Counts at most k distinct rather than exactly k.','Shrinks windows that contain exactly the allowed number of values.'],distinct_oracle,random_distinct,['Exactly k equals at-most-k minus at-most-(k-1).','Compute each at-most count with a frequency-map sliding window.','After shrinking to at most limit, add right-left+1 valid endings.','Every subarray is counted in both thresholds unless its distinct count is exactly k.'],'O(n)','O(k)',8),
993:E('are_tree_cousins',[('root','TreeNode'),('x','int'),('y','int')],'bool',['trees','breadth-first-search'],['Tree values are unique and x,y exist.','Return whether x and y have the same depth but different parents.'],[([[1,2,3,4],4,3],'Four is one level deeper than three, so they are not cousins.'),([[1,2,3,None,4,None,5],5,4],'Four and five share depth two and have different parents.')],[[t,x,y] for t,x,y in [([1,2,3],2,3),([1,2,3,4],4,3),([1,2,3,4],4,2),([1,2,3,4,5],4,5),([1,2,3,4,None,None,5],4,5),([1,2,3,None,4,None,5],4,5),([1,None,2,3,4],3,4),([1,2,3,4,5,6,7],4,6),([1,2,3,4,5,6,7],4,5),([10,5,15,3,7,13,18],3,13),([1,2,None,3,None,4],3,4),([1,None,2,3,None,4],3,4),([1,2,3,None,4,5],4,5),([1,2,3,4,None,5],4,5)]],COUSINS,[COUSINS.replace('found[x] is not found[y]','found[x] is found[y]'),COUSINS.replace('len(found)==2 and ','')],['Requires the same parent, identifying siblings instead.','Accepts when just one target appears at a level.'],cousins_oracle,random_cousins,['Cousins must be found on the same BFS level with different recorded parents.','Traverse level by level while pairing nodes with parent identities.','If either target appears, return true only when both appear and parents differ.','BFS level boundaries encode equal depth and recorded parents distinguish siblings.'],'O(n)','O(width)',3),
994:E('minutes_to_rot_all',[('grid','list[list[int]]')],'int',['breadth-first-search','matrices'],['Zero is empty, one fresh, and two rotten; rotting spreads orthogonally each minute.','Return minutes until no fresh orange remains, or -1.'],[([[[2,1,1],[1,1,0],[0,1,1]]],'Layered spread reaches the last orange after four minutes.'),([[[2,1,1],[0,1,1],[1,0,1]]],'The isolated lower-left fresh orange can never rot, so return -1.')],[[g] for g in [[[0]],[[1]],[[2]],[[2,1]],[[1,2]],[[1,1]],[[2,1,1]],[[2,0,1]],[[2,1],[1,1]],[[2,0],[0,1]],[[2,1,1],[1,1,1]],[[0,2]],[[1,2,1],[1,1,1]],[[2,1,0],[0,1,2]]]],ORANGES,[ORANGES.replace('minutes+1','minutes'),ORANGES.replace('return -1 if fresh else minutes','return minutes')],['Does not advance time between BFS layers.','Returns elapsed time even when fresh oranges remain unreachable.'],oranges_oracle,random_oranges,['All initially rotten oranges spread simultaneously, so use multi-source BFS.','Queue every rotten cell at minute zero and count fresh cells.','Rot each fresh neighbor once, decrement fresh, and enqueue with minute+1.','BFS distance is earliest rot time; remaining fresh cells prove impossibility.'],'O(rows*columns)','O(rows*columns)',5),
995:E('minimum_k_bit_flips',[('nums','list[int]'),('k','int')],'int',['greedy','sliding-window'],['A move flips exactly k consecutive bits.','Return the minimum moves to make every bit one, or -1 if impossible.'],[([[0,1,0],1],'Flip each zero individually, requiring two moves.'),([[1,1,0],2],'The final zero cannot be flipped without changing a preceding one, so return -1.')],[[n,k] for n,k in [([1],1),([0],1),([0,0],1),([0,0],2),([0,1],2),([0,1,0],1),([0,1,0],2),([1,1,0],2),([0,0,0],3),([1,0,1,0],2),([0,1,1,0],2),([1,0,0,1],2),([0,0,1,0,1],3),([1,1,1,1],4)]],FLIPS,[FLIPS.replace('if bit==active','if bit!=active'),FLIPS.replace('active^=started[i-k]','active=started[i-k]')],['Starts flips when the effective bit is already one.','Replaces rather than removes an expiring flip parity.'],flips_oracle,random_flips,['At position i, no later window can change it, so an effective zero forces a flip starting there.','Track active flip parity and when each flip began.','Expire i-k, compare bit with parity, and start a flip or fail if fewer than k cells remain.','Every greedy flip is forced, making the result minimal and unique when feasible.'],'O(n)','O(n)',8),
996:E('squareful_permutation_count',[('nums','list[int]')],'int',['backtracking','counting'],['Count distinct permutations where every adjacent sum is a perfect square.','Duplicate input values must not duplicate the count.'],[([[1,17,8]],'The valid distinct orders are 1,8,17 and 17,8,1.'),([[2,2,2]],'The only distinct permutation is valid because 2+2=4.')],[[x] for x in ([1],[1,1],[1,2],[1,8],[1,17,8],[2,2,2],[0,0],[0,1],[0,1,0],[2,7,9],[1,8,8,17],[3,6,10],[4,5,11],[1,3,6,10])],SQUAREFUL,[SQUAREFUL.replace('counts[value]-=1','counts[value]=0'),SQUAREFUL.replace('return dfs(None,len(nums))','return dfs(None,len(nums))//2')],['Consumes all duplicate copies at once.','Divides the valid count by two without symmetry justification.'],squareful_oracle,random_squareful,['Backtrack over remaining value frequencies rather than positions to avoid duplicate permutations.','A candidate may follow previous only when their sum is a perfect square.','Decrement its count, recurse, restore, and return one when no positions remain.','Each distinct value sequence chooses one frequency branch at every depth exactly once.'],'O(unique^n)','O(n+unique)',8),
997:E('find_town_judge',[('n','int'),('trust','list[list[int]]')],'int',['graphs','counting'],['The judge trusts nobody and is trusted by every other person.','Return the judge label, or -1 when none exists.'],[([2,[[1,2]]],'Person two has incoming trust from everyone else and no outgoing trust.'),([3,[[1,3],[2,3],[3,1]]],'Person three trusts one, so no town judge exists.')],[[n,t] for n,t in [(1,[]),(2,[]),(2,[[1,2]]),(2,[[2,1]]),(3,[[1,3],[2,3]]),(3,[[1,2],[2,3]]),(3,[[1,3],[2,3],[3,1]]),(4,[[1,4],[2,4],[3,4]]),(4,[[1,4],[2,4]]),(4,[[1,3],[2,3],[4,3]]),(5,[[1,5],[2,5],[3,5],[4,5]]),(3,[[1,2],[3,2],[2,1]]),(2,[[1,2],[2,1]]),(5,[])]],JUDGE,[JUDGE.replace('score[a]-=1','score[a]+=1'),JUDGE.replace('score[person]==n-1','score[person]>=n-2')],['Counts outgoing trust positively instead of disqualifying it.','Accepts a person missing one required incoming edge.'],judge_oracle,random_trust,['Net score indegree-outdegree equals n-1 only for a judge.','Subtract one from truster and add one to trusted person.','Return the label with score n-1, otherwise -1.','Reaching n-1 requires all n-1 incoming edges and zero outgoing edges under distinct trust pairs.'],'O(n+trust)','O(n)',3),
1002:E('common_characters',[('words','list[str]')],'list[str]',['counting','strings'],['Return every character common to all words, including repeated copies.','Output order is irrelevant.'],[([['bella','label','roller']],'All words contain e once and l twice, so return e,l,l.'),([['cool','lock','cook']],'The shared letters are c and o.')],[[w] for w in [['a'],['a','a'],['a','b'],['ab','ba'],['aa','aaa'],['abc','bcd'],['cool','lock','cook'],['bella','label','roller'],['zzz','zz','z'],['abc','abc','abc'],['aab','aba','baa'],['hello','world'],['miss','swim'],['xyzz','zzyx','yzxz']]],COMMON,[COMMON.replace('shared&=Counter(word)','shared|=Counter(word)'),COMMON.replace('shared.elements()','shared.keys()')],['Takes the union of character counts instead of their intersection.','Drops repeated shared copies.'],common_oracle,random_words,['For each character, the common multiplicity is the minimum count across words.','Intersect Counter objects successively.','Expand the final counter into repeated characters.','Counter intersection computes the coordinate-wise minimum required by every word.'],'O(total characters)','O(alphabet)',3),
1003:E('is_valid_abc_expansion',[('s','str')],'bool',['stacks','strings'],['Start from abc and repeatedly insert another abc anywhere.','Return whether s can be produced.'],[(['aabcbc'],'Remove an inner abc and then the remaining abc, so the string is valid.'),(['abccba'],'Removing the first abc leaves cba, so it is invalid.')],[[s] for s in ['abc','aabcbc','abcabc','abccba','cababc','ab','abcd','aabbcc','aaabcbcbc','aabc','abcabcabc','abbc','bac','aabcbcc']],VALID,[VALID.replace("stack[-3:]==['a','b','c']","stack[-3:]==['a','c','b']"),VALID.replace('return not stack','return True')],['Removes acb instead of abc.','Accepts every string.'],valid_oracle,random_valid,['Reverse the insertion process by removing every completed abc block.','A stack can remove a block as soon as its suffix becomes a,b,c.','Push each character; when the last three equal abc, delete them; accept an empty stack.','Immediate removal is safe because inserted blocks are properly nested or adjacent in the reverse construction.'],'O(n)','O(n)',5),
1004:E('longest_ones_after_flips',[('nums','list[int]'),('k','int')],'int',['sliding-window'],['Flip at most k zeros to ones.','Return the longest contiguous run of ones obtainable.'],[([[1,1,1,0,0,0,1,1,1,1,0],2],'The best window has length six and contains two zeros.'),([[0,0,1,1,1,0,0],0],'Without flips, the longest existing run has length three.')],[[n,k] for n,k in [([1],0),([0],0),([0],1),([1,1],0),([0,0],1),([1,0,1],1),([1,0,0,1],1),([1,0,0,1],2),([0,0,0],3),([1,1,1],0),([0,1,0,1,0],2),([1,1,0,1,1],1),([0,0,1,1,1,0,0],2),([1,0,1,1,0,1],1)]],ONES,[ONES.replace('zeros>k','zeros>=k'),ONES.replace('best=max(best,right-left+1)','best=max(best,right-left)')],['Shrinks a window that uses exactly k flips.','Undercounts every valid window by one.'],ones_oracle,random_ones,['A window is feasible exactly when it contains at most k zeros.','Expand right and shrink left only while zero count exceeds k.','After restoring feasibility, update maximum window length.','The maintained left edge is the earliest feasible start for each right endpoint.'],'O(n)','O(1)',5),
1005:E('maximum_sum_after_negations',[('nums','list[int]'),('k','int')],'int',['greedy','sorting'],['Perform exactly k operations, each negating one chosen element; an index may be reused.','Return the maximum final sum.'],[([[4,2,3],1],'Negating two gives the maximum sum five.'),([[3,-1,0,2],3],'Flip -1 once and use remaining flips on zero, yielding sum six.')],[[n,k] for n,k in [([1],0),([1],1),([-1],1),([-1],2),([0],5),([1,2],1),([-1,2],1),([-1,-2],1),([-1,-2],2),([4,2,3],1),([3,-1,0,2],3),([-8,3,-5,-3,-5,-2],6),([2,2,2],4),([-2,0,3],5)]],NEGATE,[NEGATE.replace('nums[i]<0','nums[i]>0'),NEGATE.replace('min(nums)','max(nums)')],['Flips positive values before negative ones.','Uses the largest magnitude for an unavoidable odd leftover flip.'],negations_oracle,random_negations,['Flip negative values from most negative upward; each such flip gives the largest immediate gain.','After useful negative flips, only parity matters because two flips cancel.','If one odd flip remains, negate the smallest absolute current value.','Exchange arguments maximize every beneficial gain and minimize the only unavoidable loss.'],'O(n log n)','O(n)',3),
}
for pid in (979,988,993):BATCH[pid]['params'][0]=('root','TreeNode | None','treenode')
BATCH[1002]['comparator']='unordered'

# Targeted review repairs. Keep these assignments adjacent so the validation
# evidence hashes the complete reviewed batch rather than hidden helper state.
BATCH[979]['boundaries'] = [
 [([1,0,0,3] if args[0] == [1,0,0,2] else [0,3,0,1] if args[0] == [0,2,0,1] else args[0])]
 for args in BATCH[979]['boundaries']
]
BATCH[980]['wrong'][1] = PATHS.replace('return dfs(*start,remaining)', 'return dfs(*start,remaining-1)')
BATCH[980]['wrong_reasons'][1] = 'Starts the remaining-square count one too low.'
BATCH[983]['wrong'][0] = TICKETS.replace('day-6', 'day-5').replace('day-29', 'day-28')
BATCH[990]['wrong'][0] = EQUATIONS.replace(
 "return all(e[1:3]=='==' or find(ord(e[0])-97)!=find(ord(e[3])-97) for e in equations)",
 "return all(e[1:3]=='==' or e[0]!=e[3] for e in equations)",
)
BATCH[990]['wrong_reasons'][0] = 'Checks only direct variable names and misses transitive equality contradictions.'
BATCH[993]['wrong'][1] = COUSINS.replace(
 'if found:return len(found)==2 and found[x] is not found[y]',
 'if found:return len(found)>=1',
)
