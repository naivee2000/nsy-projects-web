"""Reviewed geometry, ordering, stack, graph, greedy, and DP imports."""
from collections import Counter, deque
from functools import lru_cache
from itertools import combinations, permutations, product

from .import_batch_055 import entry

MOD=1_000_000_007

def rectangle_oracle(a):
 pts={tuple(p) for p in a[0]};best=None
 for x1,y1 in pts:
  for x2,y2 in pts:
   if x1<x2 and y1<y2 and (x1,y2) in pts and (x2,y1) in pts:
    area=(x2-x1)*(y2-y1);best=area if best is None else min(best,area)
 return best or 0
def subseq_oracle(a):
 s=a[0];return (len({''.join(s[i] for i in range(len(s)) if mask>>i&1) for mask in range(1,1<<len(s))}))%MOD
def mountain_oracle(a):
 x=a[0]
 return len(x)>=3 and any(all(x[i]<x[i+1] for i in range(p)) and all(x[i]>x[i+1] for i in range(p,len(x)-1)) for p in range(1,len(x)-1))
def delete_one_oracle(a):
 rows=a[0];return sum(any(rows[r][c]>rows[r+1][c] for r in range(len(rows)-1)) for c in range(len(rows[0])))
def stack_oracle(a):
 pushed,popped=a;stack=[];j=0
 for value in pushed:
  stack.append(value)
  while stack and j<len(popped) and stack[-1]==popped[j]:stack.pop();j+=1
 return j==len(popped)
def stones_oracle(a):
 stones=a[0];seen=set();components=0
 for start in range(len(stones)):
  if start in seen:continue
  components+=1;seen.add(start);queue=[start]
  while queue:
   i=queue.pop()
   for j in range(len(stones)):
    if j not in seen and (stones[i][0]==stones[j][0] or stones[i][1]==stones[j][1]):seen.add(j);queue.append(j)
 return len(stones)-components
def tokens_oracle(a):
 tokens,power=a
 @lru_cache(None)
 def play(remaining,p,s):
  best=s
  for i,value in enumerate(remaining):
   rest=remaining[:i]+remaining[i+1:]
   if p>=value:best=max(best,play(rest,p-value,s+1))
   if s:best=max(best,play(rest,p+value,s-1))
  return best
 return play(tuple(tokens),power,0)
def time_oracle(a):
 valid=[p for p in permutations(a[0]) if 10*p[0]+p[1]<24 and 10*p[2]+p[3]<60]
 return '' if not valid else '%d%d:%d%d'%max(valid)
def alien_oracle(a):
 words,order=a;rank={c:i for i,c in enumerate(order)}
 def less(x,y):
  for a,b in zip(x,y):
   if a!=b:return rank[a]<rank[b]
  return len(x)<=len(y)
 return all(less(a,b) for a,b in zip(words,words[1:]))
def doubled_oracle(a):
 values=tuple(a[0])
 @lru_cache(None)
 def pair(state):
  if not state:return True
  first=state[0]
  for i in range(1,len(state)):
   if state[i]==2*first or first==2*state[i]:
    if pair(state[1:i]+state[i+1:]):return True
  return False
 return pair(values)
def delete_two_oracle(a):
 rows=a[0];m=len(rows[0])
 for removed in range(m+1):
  for cut in combinations(range(m),removed):
   keep=[i for i in range(m) if i not in cut]
   if all(tuple(row[i] for i in keep)<=tuple(nxt[i] for i in keep) for row,nxt in zip(rows,rows[1:])):return removed
def billboard_oracle(a):
 rods=a[0];best=0
 for choices in product((-1,0,1),repeat=len(rods)):
  left=sum(v for v,c in zip(rods,choices) if c<0);right=sum(v for v,c in zip(rods,choices) if c>0)
  if left==right:best=max(best,left)
 return best
def prison_oracle(a):
 cells,n=a;state=tuple(cells);seen={};history=[]
 while n and state not in seen:
  seen[state]=len(history);history.append(state)
  state=(0,)+tuple(int(state[i-1]==state[i+1]) for i in range(1,7))+(0,)
  n-=1
 if n:
  cycle_start=seen[state]
  state=history[cycle_start+n%(len(history)-cycle_start)]
 return list(state)
def regions_oracle(a):
 grid=a[0];n=len(grid);board=[[0]*(3*n) for _ in range(3*n)]
 for r,row in enumerate(grid):
  for c,ch in enumerate(row):
   marks=((0,2),(1,1),(2,0)) if ch=='/' else ((0,0),(1,1),(2,2)) if ch=='\\' else ()
   for dr,dc in marks:board[3*r+dr][3*c+dc]=1
 seen=set();regions=0
 for r in range(3*n):
  for c in range(3*n):
   if board[r][c] or (r,c) in seen:continue
   regions+=1;seen.add((r,c));q=[(r,c)]
   while q:
    x,y=q.pop()
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
     nx,ny=x+dx,y+dy
     if 0<=nx<3*n and 0<=ny<3*n and not board[nx][ny] and (nx,ny) not in seen:seen.add((nx,ny));q.append((nx,ny))
 return regions
def delete_three_oracle(a):
 rows=a[0];m=len(rows[0]);best=0
 for mask in range(1<<m):
  cols=[i for i in range(m) if mask>>i&1]
  if all(all(row[x]<=row[y] for x,y in zip(cols,cols[1:])) for row in rows):best=max(best,len(cols))
 return m-best
def repeated_oracle(a):return Counter(a[0]).most_common(1)[0][0]
def ramp_oracle(a):
 x=a[0];return max((j-i for i in range(len(x)) for j in range(i,len(x)) if x[i]<=x[j]),default=0)
def divisible_oracle(a):
 nums,k=a;return sum(sum(nums[i:j])%k==0 for i in range(len(nums)) for j in range(i+1,len(nums)+1))
def perimeter_oracle(a):
 nums=a[0];return max((sum(t) for t in combinations(nums,3) if 2*max(t)<sum(t)),default=0)
def squares_oracle(a):return sorted(x*x for x in a[0])
def unival_oracle(a):
 values=[x for x in a[0] if x is not None];return len(set(values))<=1
def powerful_oracle(a):
 x,y,bound=a;values=set();a_power=1
 while a_power<=bound:
  b_power=1
  while a_power+b_power<=bound:
   values.add(a_power+b_power)
   if y==1:break
   b_power*=y
  if x==1:break
  a_power*=x
 return sorted(values)
def turbulent_oracle(a):
 arr=a[0];best=1
 for i in range(len(arr)):
  for j in range(i+1,len(arr)):
   signs=[(arr[k]>arr[k+1])-(arr[k]<arr[k+1]) for k in range(i,j)]
   if all(signs[k] and signs[k]==-signs[k-1] for k in range(1,len(signs))) and signs[0]:best=max(best,j-i+1)
 return best

def random_points(r):
 pts=list({(r.randrange(6),r.randrange(6)) for _ in range(r.randint(1,15))});return [[list(p) for p in pts]]
def random_text(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,10)))]
def random_numbers(r):return [[r.randint(-10,15) for _ in range(r.randint(1,12))]]
def random_rows(r):
 n,m=r.randint(1,6),r.randint(1,7);return [[''.join(r.choice('abcd') for _ in range(m)) for _ in range(n)]]
def random_stack(r):
 pushed=list(range(r.randint(1,9)));popped=pushed[:];r.shuffle(popped);return [pushed,popped]
def random_stones(r):
 pts=list({(r.randrange(6),r.randrange(6)) for _ in range(r.randint(1,10))});return [[list(p) for p in pts]]
def random_tokens(r):return [[r.randint(1,30) for _ in range(r.randint(0,7))],r.randint(0,40)]
def random_time(r):return [[r.randrange(10) for _ in range(4)]]
def random_alien(r):
 order=list('abcdefghijklmnopqrstuvwxyz');r.shuffle(order);words=[''.join(r.choice(order[:8]) for _ in range(r.randint(1,6))) for _ in range(r.randint(1,8))];return [words,''.join(order)]
def random_doubled(r):return [[r.randint(-6,6) for _ in range(2*r.randint(1,5))]]
def random_billboard(r):return [[r.randint(1,12) for _ in range(r.randint(1,8))]]
def random_prison(r):return [[r.randrange(2) for _ in range(8)],r.randint(0,40)]
def random_grid(r):
 n=r.randint(1,4);return [[''.join(r.choice(' /\\') for _ in range(n)) for _ in range(n)]]
def random_repeated(r):
 n=r.randint(2,7);repeated=r.randrange(20);others=r.sample([x for x in range(20) if x!=repeated],n);x=[repeated]*n+others;r.shuffle(x);return [x]
def random_divisible(r):return [[r.randint(-10,10) for _ in range(r.randint(1,15))],r.randint(2,9)]
def random_positive(r):return [[r.randint(1,20) for _ in range(r.randint(3,12))]]
def random_sorted(r):return [sorted(r.randint(-20,20) for _ in range(r.randint(1,15)))]
def random_tree_values(r):
 size=r.randint(1,15);value=r.randint(-3,3);tree=[value]*size
 if r.random()<.35:
  tree[r.randrange(size)]=value+1
 return [tree]
def random_powerful(r):return [r.randint(1,6),r.randint(1,6),r.randint(1,200)]
def random_turbulent(r):return [[r.randint(0,9) for _ in range(r.randint(1,15))]]

RECT='''def minimum_axis_aligned_rectangle(points):
 seen=set();best=float('inf')
 for x,y in points:
  for px,py in seen:
   if px!=x and py!=y and (px,y) in seen and (x,py) in seen:best=min(best,abs(x-px)*abs(y-py))
  seen.add((x,y))
 return 0 if best==float('inf') else best
'''
SUBSEQ='''def distinct_nonempty_subsequences(s):
 total=1;last={}
 for c in s:
  new=2*total-last.get(c,0);last[c]=total;total=new%1000000007
 return (total-1)%1000000007
'''
MOUNTAIN='''def is_valid_mountain(arr):
 if len(arr)<3:return False
 i=0
 while i+1<len(arr) and arr[i]<arr[i+1]:i+=1
 if i==0 or i==len(arr)-1:return False
 while i+1<len(arr) and arr[i]>arr[i+1]:i+=1
 return i==len(arr)-1
'''
DELETE1='''def unsorted_column_count(strs):
 return sum(any(a>b for a,b in zip(column,column[1:])) for column in zip(*strs))
'''
STACK='''def validate_stack_sequences(pushed, popped):
 stack=[];j=0
 for value in pushed:
  stack.append(value)
  while stack and j<len(popped) and stack[-1]==popped[j]:stack.pop();j+=1
 return not stack
'''
STONES='''def maximum_removable_stones(stones):
 parent={}
 def find(x):
  parent.setdefault(x,x)
  if parent[x]!=x:parent[x]=find(parent[x])
  return parent[x]
 for r,c in stones:
  a,b=find(('r',r)),find(('c',c));parent[a]=b
 return len(stones)-len({find(('r',r)) for r,c in stones})
'''
TOKENS='''def maximum_token_score(tokens, power):
 tokens=sorted(tokens);left=score=best=0;right=len(tokens)-1
 while left<=right:
  if power>=tokens[left]:power-=tokens[left];left+=1;score+=1;best=max(best,score)
  elif score:power+=tokens[right];right-=1;score-=1
  else:break
 return best
'''
TIME='''def largest_clock_time(arr):
 from itertools import permutations
 valid=[p for p in permutations(arr) if p[0]*10+p[1]<24 and p[2]*10+p[3]<60]
 return '' if not valid else '%d%d:%d%d'%max(valid)
'''
ALIEN='''def words_are_alien_sorted(words, order):
 rank={c:i for i,c in enumerate(order)}
 for a,b in zip(words,words[1:]):
  for x,y in zip(a,b):
   if x!=y:
    if rank[x]>rank[y]:return False
    break
  else:
   if len(a)>len(b):return False
 return True
'''
DOUBLED='''def can_reorder_doubled(arr):
 from collections import Counter
 counts=Counter(arr)
 for x in sorted(counts,key=abs):
  if counts[x]>counts[2*x]:return False
  counts[2*x]-=counts[x]
 return True
'''
DELETE2='''def minimum_lexicographic_column_deletions(strs):
 fixed=[False]*(len(strs)-1);answer=0
 for c in range(len(strs[0])):
  if any(not fixed[r] and strs[r][c]>strs[r+1][c] for r in range(len(strs)-1)):answer+=1;continue
  for r in range(len(strs)-1):fixed[r]|=strs[r][c]<strs[r+1][c]
 return answer
'''
BILLBOARD='''def tallest_equal_billboard(rods):
 dp={0:0}
 for rod in rods:
  old=dp.copy()
  for difference,shorter in old.items():
   dp[difference+rod]=max(dp.get(difference+rod,0),shorter)
   new=abs(difference-rod);dp[new]=max(dp.get(new,0),shorter+min(difference,rod))
 return dp[0]
'''
PRISON='''def prison_cells_after_days(cells, n):
 seen={};state=tuple(cells)
 while n:
  if state in seen:
   cycle=seen[state]-n;n%=cycle
  seen[state]=n
  if n:n-=1;state=(0,)+tuple(int(state[i-1]==state[i+1]) for i in range(1,7))+(0,)
 return list(state)
'''
REGIONS=r'''def slash_region_count(grid):
 n=len(grid);parent=list(range(4*n*n))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b:parent[a]=b
 for r,row in enumerate(grid):
  for c,ch in enumerate(row):
   base=4*(r*n+c)
   if ch!='/':union(base,base+1);union(base+2,base+3)
   if ch!='\\':union(base,base+3);union(base+1,base+2)
   if r:union(base,4*((r-1)*n+c)+2)
   if c:union(base+3,4*(r*n+c-1)+1)
 return len({find(i) for i in range(4*n*n)})
'''
DELETE3='''def minimum_columns_for_rowwise_order(strs):
 m=len(strs[0]);dp=[1]*m
 for j in range(m):
  for i in range(j):
   if all(row[i]<=row[j] for row in strs):dp[j]=max(dp[j],dp[i]+1)
 return m-max(dp)
'''
REPEATED='''def repeated_half_element(nums):
 seen=set()
 for value in nums:
  if value in seen:return value
  seen.add(value)
'''
RAMP='''def maximum_width_ramp(nums):
 stack=[]
 for i,value in enumerate(nums):
  if not stack or value<nums[stack[-1]]:stack.append(i)
 best=0
 for j in range(len(nums)-1,-1,-1):
  while stack and nums[stack[-1]]<=nums[j]:best=max(best,j-stack.pop())
 return best
'''
DIVISIBLE='''def divisible_subarray_count(nums, k):
 counts={0:1};prefix=answer=0
 for value in nums:
  prefix=(prefix+value)%k;answer+=counts.get(prefix,0);counts[prefix]=counts.get(prefix,0)+1
 return answer
'''
PERIMETER='''def largest_triangle_perimeter(nums):
 nums=sorted(nums,reverse=True)
 for a,b,c in zip(nums,nums[1:],nums[2:]):
  if b+c>a:return a+b+c
 return 0
'''
SQUARES='''def sorted_squares(nums):
 answer=[0]*len(nums);left=0;right=len(nums)-1
 for i in range(len(nums)-1,-1,-1):
  if abs(nums[left])>abs(nums[right]):answer[i]=nums[left]**2;left+=1
  else:answer[i]=nums[right]**2;right-=1
 return answer
'''
UNIVAL='''def is_univalued_tree(root):
 target=root.val;stack=[root]
 while stack:
  node=stack.pop()
  if node.val!=target:return False
  if node.left:stack.append(node.left)
  if node.right:stack.append(node.right)
 return True
'''
POWERFUL='''def powerful_integers(x, y, bound):
 answer=set();a=1
 while a<=bound:
  b=1
  while a+b<=bound:
   answer.add(a+b)
   if y==1:break
   b*=y
  if x==1:break
  a*=x
 return sorted(answer)
'''
TURBULENT='''def longest_turbulent_subarray(arr):
 up=down=best=1
 for a,b in zip(arr,arr[1:]):
  if a<b:up=down+1;down=1
  elif a>b:down=up+1;up=1
  else:up=down=1
  best=max(best,up,down)
 return best
'''

def lesson(a,b,c,d):return [a,b,c,d],d
def E(name,params,ret,topics,constraints,examples,bounds,ref,wrongs,reasons,oracle,gen,hints,time,space,diff):
 return entry(name,params,ret,topics,constraints,examples,bounds,ref,wrongs,reasons,oracle,gen,*lesson(*hints),time,space,diff)

BATCH={
939:E('minimum_axis_aligned_rectangle',[('points','list[list[int]]')],'int',['geometry','hash-maps'],['Points are distinct integer coordinates.','Return the minimum positive area of an axis-aligned rectangle, or zero if none exists.'],[([[[1,1],[1,3],[3,1],[3,3],[2,2]]],'The four corner points at x=1,3 and y=1,3 form area four.'),([[[1,1],[1,3],[3,1],[3,3],[4,1],[4,3]]],'The narrower rectangle between x=3 and x=4 has area two.')],[[p] for p in [[[0,0]],[[0,0],[1,1]],[[0,0],[0,1],[1,0],[1,1]],[[0,0],[0,2],[3,0],[3,2]],[[1,1],[1,2],[2,1]],[[0,0],[0,1],[2,0],[2,1],[1,0],[1,1]],[[1,1],[2,2],[3,3]],[[0,0],[0,5],[1,0],[1,5]],[[2,3],[2,4],[8,3],[8,4]],[[0,0],[0,1],[1,0],[1,1],[3,3]],[[1,0],[1,2],[4,0],[4,2],[2,0],[2,2]],[[0,1],[0,4],[5,1],[5,4]],[[1,1],[1,4],[3,1],[3,4],[3,2]],[[0,0],[2,0],[0,2],[2,2],[1,1]]]],RECT,[RECT.replace('min(best,','max(best,'),RECT.replace("and (x,py) in seen",'')],['Keeps the largest rectangle instead of the smallest.','Accepts three corners without checking the fourth.'],rectangle_oracle,random_points,['A rectangle is identified when a new point completes two older opposite/adjacent corners.','Store prior points in a set and test every prior diagonal candidate.','For (x,y) and (px,py), require both crossed corners and compute absolute side product.','All four corners are required and each real rectangle is eventually completed.'],'O(n^2)','O(n)',5),
940:E('distinct_nonempty_subsequences',[('s','str')],'int',['dynamic-programming','strings'],['1 <= len(s) <= 2,000; lowercase letters.','Count distinct nonempty subsequences modulo 1,000,000,007.'],[(['abc'],'The seven nonempty subsets of positions produce seven different subsequences.'),(['aba'],'The distinct results are a,b,aa,ab,ba,aba: six.')],[[s] for s in ['a','aa','ab','aaa','abb','abc','abab','abcd','aab','baa','abcabc','zzxy','abca','dddd']],SUBSEQ,[SUBSEQ.replace('last.get(c,0)','0'),SUBSEQ.replace('return (total-1)','return total')],['Double-counts subsequences ending at a repeated character.','Includes the empty subsequence.'],subseq_oracle,random_text,['Appending c doubles subsequences before removing duplicates created at its previous occurrence.','Track total including empty and the old total saved for each ending character.','new=2*total-last[c]; then last[c]=old total.','The subtracted family is exactly the subsequences that previously acquired the same final c.'],'O(n)','O(alphabet)',8),
941:E('is_valid_mountain',[('arr','list[int]')],'bool',['arrays','two-pointers'],['A mountain strictly rises then strictly falls, with both slopes nonempty.','Return whether the entire array is one mountain.'],[([[2,1]],'Two values cannot contain both a rise and a fall.'),([[0,3,2,1]],'The array rises to three and then strictly falls.')],[[x] for x in ([1],[1,2,1],[1,2,3],[3,2,1],[1,1,0],[0,1,1],[0,2,1,0],[0,1,2,1,2],[2,0,2],[0,5,4,3],[3,4,5,2],[1,3,2,2],[0,10,0],[1,2,3,2,1])],MOUNTAIN,[MOUNTAIN.replace('arr[i]<arr[i+1]','arr[i]<=arr[i+1]'),MOUNTAIN.replace('if i==0 or i==len(arr)-1:return False','')],['Allows flat steps on the ascent.','Allows a peak at an endpoint without both slopes.'],mountain_oracle,random_numbers,['Walk the strictly increasing slope, verify a genuine interior peak, then walk down.','A single index can mark the transition between the two phases.','Reject length<3, peak at either endpoint, flats, or leftover positions.','The two scans cover the whole array exactly when both required slopes exist.'],'O(n)','O(1)',3),
944:E('unsorted_column_count',[('strs','list[str]')],'int',['matrices','strings'],['All strings have equal length.','Delete each column whose top-to-bottom characters are not nondecreasing; return the count.'],[([['cba','daf','ghi']],'Only the second column b,a,h decreases, so one column is deleted.'),([['a','b']],'The single column is already sorted.')],[[x] for x in [['a'],['z','a'],['a','z'],['abc'],['abc','abc'],['ba','ab'],['zyx','wvu'],['abc','bcd','cde'],['aaa','aaa'],['az','by','cx'],['xga','xfb','yfa'],['rrjk','furt','guzm'],['aab','aac','aaa'],['abcd','abce']]],DELETE1,[DELETE1.replace('a>b','a<b'),'''def unsorted_column_count(strs):
 return len(strs[0])
'''],['Counts increasing columns as invalid.','Deletes every column regardless of order.'],delete_one_oracle,random_rows,['Columns are independent in this version.','Transpose conceptually and inspect adjacent characters in each column.','Count a column if any upper character is greater than the next lower one.','Adjacent nondecrease is necessary and sufficient for a fully sorted column.'],'O(rows*columns)','O(1)',3),
946:E('validate_stack_sequences',[('pushed','list[int]'),('popped','list[int]')],'bool',['stacks','simulation'],['pushed and popped are permutations of the same distinct values.','Return whether popped can be produced by pushes in pushed order and arbitrary pops.'],[([[1,2,3,4,5],[4,5,3,2,1]],'Push through four, pop four, then continue to realize the sequence.'),([[1,2,3,4,5],[4,3,5,1,2]],'After popping one, value two blocks the requested one, so it is impossible.')],[[p,q] for p,q in [([1],[1]),([1,2],[1,2]),([1,2],[2,1]),([1,2,3],[3,2,1]),([1,2,3],[2,3,1]),([1,2,3],[3,1,2]),([0,1,2,3],[1,0,3,2]),([0,1,2,3],[2,0,3,1]),([5,4,3],[4,3,5]),([1,2,3,4],[2,1,4,3]),([1,2,3,4],[3,4,2,1]),([1,2,3,4],[4,2,3,1]),([9,8,7,6],[6,7,8,9]),([1,3,5,7],[3,1,7,5])]],STACK,[STACK.replace('stack[-1]==popped[j]','stack[0]==popped[j]'),STACK.replace('return not stack','return True')],['Pops from the bottom like a queue.','Accepts every permutation.'],stack_oracle,random_stack,['When the requested next pop is available at the stack top, delaying it is never useful.','Push each value, then greedily pop matching requested values.','Advance popped pointer while stack[-1] equals popped[j].','Every legal execution can make these eager pops; remaining stack means the target order was blocked.'],'O(n)','O(n)',5),
947:E('maximum_removable_stones',[('stones','list[list[int]]')],'int',['graphs','union-find'],['A stone can be removed while another stone shares its row or column.','Return the maximum number removable.'],[([[[0,0],[0,1],[1,0],[1,2],[2,1],[2,2]]],'All six stones form one connected component, so five can be removed.'),([[[0,0]]],'The only stone has no partner and cannot be removed.')],[[x] for x in [[[0,0],[0,1]],[[0,0],[1,0]],[[0,0],[1,1]],[[0,0],[0,1],[1,0]],[[0,0],[1,1],[2,2]],[[0,0],[0,2],[2,2]],[[1,1],[1,2],[3,4]],[[0,1],[2,1],[2,3]],[[1,0],[1,1],[2,2],[3,2]],[[0,0],[0,1],[5,5],[5,6]],[[0,0],[1,0],[1,1],[2,1]],[[3,3],[3,4],[4,4],[5,5]],[[0,2],[1,2],[1,3],[4,3]],[[1,1],[2,1],[3,1]]]],STONES,[STONES.replace("return len(stones)-len",'return len(stones)-1-len'),STONES.replace("('c',c)","('r',c)")],['Removes one too many stones from every input.','Confuses row and column namespaces.'],stones_oracle,random_stones,['Within each connected row/column component, all but one stone can be removed.','Union row vertices with separately tagged column vertices.','Count distinct component roots among stones and return stones-components.','Connectivity supplies a removal order, while one final stone per component must remain.'],'O(n alpha(n))','O(n)',5),
948:E('maximum_token_score',[('tokens','list[int]'),('power','int')],'int',['greedy','two-pointers'],['Spend power to play a token face up for one score, or spend one score to play it face down for power.','Each token is used at most once; return maximum score reached.'],[([[100],50],'There is not enough power to gain the first score.'),([[100,200,300,400],200],'Buy 100, sell 400, then buy 200 and 300 to reach score two.')],[[t,p] for t,p in [([],10),([1],0),([1],1),([1,2],1),([1,2],2),([100,200],150),([10,20,30],25),([5,5,5],5),([1,100,101],2),([2,3,4,5],6),([50,60,70],100),([1,2,100],3),([8,9,10,11],17),([3,20,30,40],10)]],TOKENS,[TOKENS.replace('tokens[right]','tokens[left]'),TOKENS.replace('return best','return 0')],['Sells the cheapest remaining token instead of the most expensive.','Always reports zero score.'],tokens_oracle,random_tokens,['When buying, cheapest preserves power; when selling, largest maximizes the next opportunity.','Sort and maintain low/high pointers, current score, and best score.','Buy low when possible; otherwise sell high only with positive score.','Exchange arguments show these extremes dominate any other face-up or face-down choice.'],'O(n log n)','O(n)',5),
949:E('largest_clock_time',[('arr','list[int]')],'str',['permutations','strings'],['Use all four digits exactly once as HH:MM in 24-hour time.','Return the largest valid time or an empty string.'],[([[1,2,3,4]],'The latest valid arrangement is 23:41.'),([[5,5,5,5]],'No permutation forms an hour below 24, so return an empty string.')],[[x] for x in ([0,0,0,0],[2,3,5,9],[0,0,1,0],[2,4,0,0],[1,9,5,9],[2,3,5,5],[0,6,0,0],[1,2,5,9],[0,1,2,3],[2,2,3,4],[1,1,1,1],[0,0,2,4],[2,3,4,6],[0,5,5,9])],TIME,[TIME.replace('<24','<=24'),TIME.replace('max(valid)','min(valid)')],['Accepts invalid hour 24.','Returns the earliest valid time.'],time_oracle,random_time,['Only 24 permutations exist, so direct enumeration is reliable and clear.','Filter arrangements by hour<24 and minute<60.','Choose the lexicographically/numerically largest valid digit tuple and format it.','Every legal use of the four digits is a permutation and tuple order matches clock order.'],'O(1)','O(1)',5),
953:E('words_are_alien_sorted',[('words','list[str]'),('order','str')],'bool',['strings','hash-maps'],['order is a permutation of the lowercase alphabet.','Return whether adjacent words are lexicographically nondecreasing under that alphabet.'],[([['hello','leetcode'],'hlabcdefgijkmnopqrstuvwxyz'],'The first differing letters h and l occur in the required order.'),([['word','world','row'],'worldabcefghijkmnpqstuvxyz'],'Under this alphabet, world must precede word, so the list is unsorted.')],[[w,o] for w,o in [(['a'],'abcdefghijklmnopqrstuvwxyz'),(['a','b'],'abcdefghijklmnopqrstuvwxyz'),(['b','a'],'abcdefghijklmnopqrstuvwxyz'),(['app','apple'],'abcdefghijklmnopqrstuvwxyz'),(['apple','app'],'abcdefghijklmnopqrstuvwxyz'),(['z','a'],'zyxwvutsrqponmlkjihgfedcba'),(['za','zb'],'zyxwvutsrqponmlkjihgfedcba'),(['abc','abc'],'abcdefghijklmnopqrstuvwxyz'),(['a','aa','aaa'],'abcdefghijklmnopqrstuvwxyz'),(['aa','a'],'abcdefghijklmnopqrstuvwxyz'),(['x','y','z'],'xyzabcdefghijklmnopqrstuvw'),(['hello','hello'],'abcdefghijklmnopqrstuvwxyz'),(['kuvp','q'],'ngxlkthsjuoqcpavbfdermiywz'),(['a','c','b'],'acbdefghijklmnopqrstuvwxyz')]],ALIEN,[ALIEN.replace('rank[x]>rank[y]','rank[x]<rank[y]'),'''def words_are_alien_sorted(words, order):
 return True
'''],['Reverses the alien comparison.','Accepts every word ordering, including invalid prefixes.'],alien_oracle,random_alien,['Only the first differing character decides a pair unless one word is a prefix.','Map characters to ranks and compare adjacent words.','At first difference reject decreasing rank; if none, reject a longer first word.','Adjacent nondecrease is sufficient for the entire list to be sorted.'],'O(total characters)','O(alphabet)',3),
954:E('can_reorder_doubled',[('arr','list[int]')],'bool',['counting','sorting'],['Reorder the even-length array into pairs [x,2x].','Negative values and zero are allowed.'],[([[3,1,3,6]],'Only one three can pair with six, leaving the other unmatched.'),([[4,-2,2,-4]],'Pairs can be (-2,-4) and (2,4).')],[[x] for x in ([0,0],[0,0,0,0],[0,1],[-2,-4],[2,4],[-2,4],[-4,-2,2,4],[1,2,2,4],[1,2,4,8],[3,6,3,6],[-1,-2,-2,-4],[1,1,2,2],[2,4,4,8],[-3,-6,3,6])],DOUBLED,[DOUBLED.replace('key=abs',''),DOUBLED.replace('counts[2*x]-=counts[x]','counts[2*x]-=1')],['Processes negative values in numeric order and consumes partners incorrectly.','Consumes only one double regardless of multiplicity.'],doubled_oracle,random_doubled,['Values must be processed by absolute value so a number is matched before a farther-from-zero double.','Count values, then consume counts[x] copies from counts[2x].','Reject when the double count is insufficient.','Absolute ordering prevents a value from being consumed as a double before its own pairing demand is handled.'],'O(n log n)','O(n)',5),
955:E('minimum_lexicographic_column_deletions',[('strs','list[str]')],'int',['greedy','strings'],['Delete the same columns from every row so the row list becomes lexicographically sorted.','Return the minimum deletion count.'],[([['ca','bb','ac']],'Delete the first column; remaining rows a,b,c are sorted.'),([['xc','yb','za']],'The first column already fixes every adjacent row order, so delete none.')],[[x] for x in [['a'],['b','a'],['a','b'],['ab','aa'],['ba','ab'],['xc','yb','za'],['zyx','wvu','tsr'],['abc','bca','cab'],['aa','aa'],['az','by','cx'],['xga','xfb','yfa'],['ca','bb','ac'],['abx','agz','bgc','bfc'],['doeeqiy','yabhbqe','twckqte']]],DELETE2,[DELETE2.replace('not fixed[r] and ',''),'''def minimum_lexicographic_column_deletions(strs):
 return 0
'''],['Deletes a column for inversions in pairs whose order was already fixed earlier.','Never deletes an offending column.'],delete_two_oracle,random_rows,['Once an earlier kept column orders an adjacent pair, later columns cannot break that pair.','Track which adjacent row pairs are already strictly ordered.','Delete a column if it reverses any unresolved pair; otherwise mark new strict pairs.','Keeping every safe column is optimal because it only resolves constraints and never creates future ones.'],'O(rows*columns)','O(rows)',5),
956:E('tallest_equal_billboard',[('rods','list[int]')],'int',['dynamic-programming'],['Assign each rod to the left support, right support, or unused.','Return the greatest equal support height.'],[([[1,2,3,6]],'Rods 1+2+3 balance rod 6 at height six.'),([[1,2]],'No positive equal split exists, so the height is zero.')],[[x] for x in ([1],[1,1],[1,2],[1,2,3],[1,2,3,6],[1,2,3,4,5,6],[5,5,5,5],[3,4,7],[2,3,5,10],[1,1,2,2],[6,7,8,9],[10,20,30],[1,3,3,6,7],[2,4,6,8])],BILLBOARD,[BILLBOARD.replace('shorter+min(difference,rod)','shorter'),BILLBOARD.replace('return dp[0]','return max(dp.values())')],['Fails to increase the shorter support when a rod crosses the height difference.','Returns the largest shorter-side state even when supports are unequal.'],billboard_oracle,random_billboard,['Represent a partial assignment by height difference and the shorter support height.','For each rod, skip it, add it to taller, or add it to shorter.','Update difference and shorter height from a frozen copy of states.','The state retains exactly the information needed for all future balancing choices.'],'O(n*sum rods)','O(sum rods)',8),
957:E('prison_cells_after_days',[('cells','list[int]'),('n','int')],'list[int]',['simulation','hash-maps'],['There are exactly eight cells; endpoints become zero each day.','An interior cell becomes one exactly when its two neighbors were equal.'],[([[0,1,0,1,1,0,0,1],7],'Seven simultaneous daily updates produce 0,0,1,1,0,0,0,0.'),([[1,0,0,1,0,0,1,0],1_000_000_000],'Cycle detection reduces the large day count to the repeated state 0,0,1,1,1,1,1,0.')],[[c,n] for c,n in [([0]*8,0),([0]*8,1),([1]*8,1),([1,0,1,0,1,0,1,0],1),([1,0,1,0,1,0,1,0],2),([0,1,0,1,1,0,0,1],1),([0,1,0,1,1,0,0,1],6),([0,1,0,1,1,0,0,1],14),([1,1,0,0,1,1,0,0],7),([0,0,1,1,0,0,1,1],20),([1,0,0,0,0,0,0,1],5),([0,1,1,0,0,1,1,0],10),([1,1,1,0,1,1,1,0],15),([0,0,0,1,1,1,0,0],30)]],PRISON,[PRISON.replace('state[i-1]==state[i+1]','state[i-1]!=state[i+1]'),PRISON.replace('(0,)+','(state[0],)+')],['Uses unequal neighbors instead of equal neighbors.','Leaves the first endpoint unchanged.'],prison_oracle,random_prison,['Only 2^6 interior states exist after the first day, so repetition is guaranteed.','Remember each state with remaining days and jump by a detected cycle length.','On repetition reduce n modulo the difference in remaining-day counts.','The transition is deterministic, so revisiting a state repeats the entire future cycle.'],'O(min(n,64))','O(64)',5),
959:E('slash_region_count',[('grid','list[str]')],'int',['graphs','union-find','matrices'],['Each square contains slash, backslash, or space.','Count connected planar regions formed inside the grid.'],[([[' /','/ ']],'The two slashes enclose one area and leave the outside as another, giving two.'),([[' /','  ']],'The lone slash does not enclose a separate region, so the answer is one.')],[[g] for g in [[' '],['/'],['\\'],['  ','  '],['//','//'],['\\\\','\\\\'],['/\\','\\/'],[' /','/ '],['\\/','/\\'],['   ',' / ','   '],['/  ',' \\ ','  /'],[' /\\','\\/ ',' / '],['///','///','///'],['/ \\',' \\ ','\\ /']]],REGIONS,[REGIONS.replace("if ch!='\\\\'","if ch=='\\\\'"),REGIONS.replace('if r:union','if False:union')],['Joins the wrong internal triangles for backslashes.','Never connects cells vertically.'],regions_oracle,random_grid,['Split each square into four triangular nodes.','Union triangles not separated by the cell character, then union neighboring edges.','After all unions, count distinct roots among the 4*n*n triangles.','Connected triangles correspond exactly to connected planar regions.'],'O(n^2 alpha(n))','O(n^2)',5),
960:E('minimum_columns_for_rowwise_order',[('strs','list[str]')],'int',['dynamic-programming','strings'],['Delete columns so every individual remaining row is nondecreasing left to right.','Return the minimum deletions.'],[([['babca','bbazb']],'The longest jointly nondecreasing column subsequence has length two, so delete three.'),([['edcba']],'A decreasing five-letter row can retain only one column, so delete four.')],[[x] for x in [['a'],['ab'],['ba'],['abc','abc'],['cba','abc'],['babca','bbazb'],['edcba'],['ghi','def','abc'],['aaa','bbb'],['azby','axcy'],['xga','xfb','yfa'],['abcdef','fedcba'],['ace','bdf'],['zxy','zyx']]],DELETE3,[DELETE3.replace('row[i]<=row[j]','row[i]<row[j]'),'''def minimum_columns_for_rowwise_order(strs):
 return len(strs[0])-1
'''],['Forbids equal adjacent retained characters.','Assumes exactly one column can always be retained.'],delete_three_oracle,random_rows,['Retained column indices must form a nondecreasing subsequence simultaneously in every row.','Run longest-path DP over column pairs compatible in all rows.','dp[j]=1+max(dp[i]) for i<j where every row[i]<=row[j].','Any valid retained set is such a path; deleting all other columns is optimal.'],'O(rows*columns^2)','O(columns)',8),
961:E('repeated_half_element',[('nums','list[int]')],'int',['hash-maps','arrays'],['The length is 2n and exactly one value occurs n times; all others are distinct.','Return the repeated value.'],[([[1,2,3,3]],'Three is the first value encountered twice.'),([[2,1,2,5,3,2]],'Two occurs half of the six positions.')],[[x] for x in ([1,2,1,3],[5,5],[0,1,0,2],[4,1,2,4,3,4],[9,8,9,7],[2,3,4,2,5,2],[6,1,6,2,6,3],[7,7,1,2],[0,0],[10,1,2,10,3,10],[4,5,6,4],[8,1,8,2,8,3],[3,0,1,3],[11,12,11,13])],REPEATED,[REPEATED.replace('return value','return nums[0]'),REPEATED.replace('seen.add(value)','seen=set()')],['Always returns the first array value.','Clears memory each iteration and never finds a later duplicate.'],repeated_oracle,random_repeated,['The promised half-frequency value must appear at least twice.','Return the first duplicate found while scanning.','Keep a set of prior values; on membership return the current value.','All nonanswer values are distinct, so the only possible duplicate is the answer.'],'O(n)','O(n)',3),
962:E('maximum_width_ramp',[('nums','list[int]')],'int',['monotonic-stack','arrays'],['A ramp is i<=j with nums[i]<=nums[j].','Return the maximum j-i.'],[([[6,0,8,2,1,5]],'Indices 1 and 5 form width four: 0<=5.'),([[9,8,1,0,1,9,4,0,4,1]],'Indices 0 and 5 form the maximum width five.')],[[x] for x in ([1],[1,2],[2,1],[1,1],[3,2,1],[1,2,3],[6,0,8,2,1,5],[5,4,3,2,1,6],[2,2,2,2],[10,1,2,3,4],[4,1,4,0,4],[9,8,1,0,1,9],[3,0,2,0,3],[7,3,5,1,6])],RAMP,[RAMP.replace('value<nums[stack[-1]]','value>nums[stack[-1]]'),RAMP.replace('<=nums[j]','<nums[j]')],['Stores increasing candidates instead of new prefix minima.','Rejects equal-valued ramp endpoints.'],ramp_oracle,random_numbers,['Only indices establishing a new prefix minimum can be optimal left endpoints.','Store those in a decreasing stack, then scan right endpoints backward.','Pop every candidate whose value is <= current right value and update width.','The backward scan gives each popped left index its farthest feasible right endpoint.'],'O(n)','O(n)',5),
974:E('divisible_subarray_count',[('nums','list[int]'),('k','int')],'int',['prefix-sums','hash-maps'],['k is positive; nums may contain negative values.','Count nonempty contiguous subarrays whose sum is divisible by k.'],[([[4,5,0,-2,-3,1],5],'Seven subarrays have prefix endpoints with equal remainder modulo five.'),([[5],9],'Five is not divisible by nine, so the count is zero.')],[[x,k] for x,k in [([0],2),([1],2),([2],2),([1,1],2),([-1,1],3),([4,5,0,-2,-3,1],3),([1,2,3],3),([1,-1,1,-1],2),([5,5,5],5),([-5,0,5],5),([2,7,6,1,4,5],3),([10,-10],7),([3,1,2,7,4],5),([-2,-3,5],4)]],DIVISIBLE,[DIVISIBLE.replace('{0:1}','{}'),DIVISIBLE.replace('%k','%(k+1)')],['Omits the empty prefix and misses subarrays starting at index zero.','Uses the wrong modulus.'],divisible_oracle,random_divisible,['A subarray sum is divisible by k when its endpoint prefix remainders are equal.','Count previously seen remainders while scanning prefix sums.','Add count[current remainder], then increment it; seed remainder zero once.','Each equal-remainder prefix pair identifies exactly one qualifying subarray.'],'O(n)','O(k)',5),
976:E('largest_triangle_perimeter',[('nums','list[int]')],'int',['sorting','greedy'],['Choose three positive lengths forming a nondegenerate triangle.','Return the largest possible perimeter, or zero.'],[([[2,1,2]],'Lengths 1,2,2 form a triangle with perimeter five.'),([[1,2,1,10]],'No triple satisfies the strict triangle inequality.')],[[x] for x in ([1,1,1],[1,1,2],[2,3,4],[3,4,5],[10,1,1],[5,5,9],[5,5,10],[2,1,2],[1,2,1,10],[6,4,3,2],[100,50,51],[7,7,7,1],[9,8,3,2],[4,2,3,4])],PERIMETER,[PERIMETER.replace('b+c>a','b+c>=a'),PERIMETER.replace('return a+b+c','return b+c')],['Accepts degenerate collinear sides.','Omits the largest side from the perimeter.'],perimeter_oracle,random_positive,['After descending sort, the first consecutive triple satisfying b+c>a has maximum perimeter.','Test consecutive triples from largest downward.','Return a+b+c at the first strict inequality, otherwise zero.','If b+c cannot beat a, replacing b or c by smaller later sides cannot help that a.'],'O(n log n)','O(n)',3),
977:E('sorted_squares',[('nums','list[int]')],'list[int]',['two-pointers','sorting'],['nums is sorted in nondecreasing order.','Return the squares in nondecreasing order.'],[([[-4,-1,0,3,10]],'Squares 16,1,0,9,100 reorder to 0,1,9,16,100.'),([[-7,-3,2,3,11]],'The ordered squares are 4,9,9,49,121.')],[[x] for x in ([0],[1],[-1],[-2,-1],[-1,2],[1,2,3],[-3,-2,-1],[-2,0,2],[-5,-1,0,4],[-10,-5,1,2],[0,0,1],[-3,-3,2,2],[-8,-2,3,9],[-4,-1,0,3,10])],SQUARES,[SQUARES.replace('>abs(nums[right])','<abs(nums[right])'),SQUARES.replace('range(len(nums)-1,-1,-1)','range(len(nums))')],['Chooses the smaller absolute endpoint for the largest remaining slot.','Fills output from the front while choosing the largest square.'],squares_oracle,random_sorted,['The largest remaining square is always at one of the sorted array’s endpoints.','Compare absolute endpoint values and fill output from right to left.','Place the larger square, move that pointer, and decrement the output index.','Removing the largest absolute endpoint preserves the same invariant on the remaining interval.'],'O(n)','O(n)',3),
}
BATCH.update({
965:E('is_univalued_tree',[('root','TreeNode')],'bool',['trees','depth-first-search'],['The tree has at least one node.','Return whether every node has the same integer value.'],[([[1,1,1,1,1,None,1]],'Every present node stores one, so the tree is univalued.'),([[2,2,2,5,2]],'The node containing five differs from the root value.')],[[t] for t in [[0],[1,1],[1,None,1],[1,1,1],[1,1,2],[2,2,2,2],[0,0,0,None,0],[-1,-1,-1],[-1,-1,0],[5,5,5,5,None,5],[3,3,None,3],[2,2,2,None,None,2,3],[7,7,7,7,7,7,7],[1,1,None,None,2]]],UNIVAL,[UNIVAL.replace('node.val!=target','node.val==target'),UNIVAL.replace('return True','return False')],['Rejects nodes equal to the root.','Reports false even after all nodes match.'],unival_oracle,random_tree_values,['Every node can be compared with the root’s value.','Traverse the tree with a stack or recursion and stop at the first mismatch.','Push non-null children; return false when node.val differs, otherwise true after exhaustion.','A tree is univalued exactly when no visited node violates equality with the root.'],'O(n)','O(height)',3),
970:E('powerful_integers',[('x','int'),('y','int'),('bound','int')],'list[int]',['math','hash-maps'],['Return distinct values x^i+y^j <= bound for nonnegative i,j.','Output order is irrelevant; x or y may equal one.'],[([2,3,10],'The distinct sums within ten are 2,3,4,5,7,9,10.'),([3,5,15],'The values are 2,4,6,8,10,14.')],[[x,y,b] for x,y,b in [(1,1,1),(1,1,2),(1,2,10),(2,1,10),(2,2,3),(2,2,20),(3,5,15),(2,3,1),(2,3,2),(4,4,100),(5,2,50),(10,10,200),(3,1,30),(1,7,100)]],POWERFUL,[POWERFUL.replace('answer.add(a+b)','answer.add(a*b)'),POWERFUL.replace('if x==1:break','if x<=2:break')],['Multiplies powers instead of adding them.','Stops after one x power when x equals two.'],powerful_oracle,random_powerful,['Enumerate geometric powers of x and y, but guard bases equal to one.','Use nested loops over powers and a set for duplicate sums.','Break a power loop after its base-one iteration; otherwise multiply by the base.','Every exponent pair appears once in the loops and the bound makes both finite.'],'O(log_x(bound)*log_y(bound))','O(output)',5),
978:E('longest_turbulent_subarray',[('arr','list[int]')],'int',['dynamic-programming','arrays'],['Adjacent comparisons must alternate strictly between greater and less.','Return the maximum contiguous turbulent length.'],[([[9,4,2,10,7,8,8,1,9]],'The segment 4,2,10,7,8 alternates for length five.'),([[4,8,12,16]],'Every adjacent comparison has the same direction, so the maximum length is two.')],[[x] for x in ([1],[1,2],[2,1],[1,1],[1,2,1],[1,2,3],[3,2,1],[1,3,2,4,3],[1,3,3,2],[4,8,12,16],[9,4,2,10,7,8,8,1,9],[5,1,5,1,5],[0,1,0,1,2],[3,3,3,3])],TURBULENT,[TURBULENT.replace('up=down+1','up=up+1'),TURBULENT.replace('else:up=down=1','else:pass')],['Extends an upward run from the wrong prior direction.','Fails to reset at equal adjacent values.'],turbulent_oracle,random_turbulent,['Track the best turbulent suffix ending with an upward or downward final comparison.','An upward step extends the previous downward suffix, and vice versa.','On equality reset both lengths to one; update the maximum each step.','Alternation forces the prior comparison direction, so these two suffix states are sufficient.'],'O(n)','O(1)',5),
})
BATCH[965]['params'][0]=('root','TreeNode | None','treenode')
BATCH[970]['comparator']='unordered'
