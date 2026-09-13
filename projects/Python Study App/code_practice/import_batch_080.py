"""Reviewed greedy, graph, tree, string, heap, and dynamic-programming imports."""
from collections import Counter, deque
from functools import lru_cache
from itertools import combinations

from .import_batch_055 import entry
from .import_batch_079 import tree_data


def city_oracle(a):
 c=a[0];n=len(c)//2
 return min(sum(c[i][0] if i in chosen else c[i][1] for i in range(len(c))) for chosen in combinations(range(len(c)),n))
def cells_oracle(a):
 rows,cols,rr,cc=a
 return sorted(([r,c] for r in range(rows) for c in range(cols)),key=lambda p:(abs(p[0]-rr)+abs(p[1]-cc),p[0],p[1]))
def windows_oracle(a):
 nums,x,y=a;best=-10**9
 for i in range(len(nums)-x+1):
  for j in range(len(nums)-y+1):
   if i+x<=j or j+y<=i:best=max(best,sum(nums[i:i+x])+sum(nums[j:j+y]))
 return best
def three_stones_oracle(a):
 x,y,z=sorted(a);g1=y-x-1;g2=z-y-1
 low=0 if g1==g2==0 else 1 if g1<=1 or g2<=1 else 2
 return [low,g1+g2]
def border_oracle(a):
 grid,row,col,color=a;grid=[x[:] for x in grid];old=grid[row][col];seen={(row,col)};q=deque([(row,col)]);border=[]
 while q:
  r,c=q.popleft();edge=r==0 or c==0 or r==len(grid)-1 or c==len(grid[0])-1
  for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
   nr,nc=r+dr,c+dc
   if not (0<=nr<len(grid) and 0<=nc<len(grid[0])) or grid[nr][nc]!=old:edge=True
   elif (nr,nc) not in seen:seen.add((nr,nc));q.append((nr,nc))
  if edge:border.append((r,c))
 for r,c in border:grid[r][c]=color
 return grid
def lines_oracle(a):
 x,y=a
 @lru_cache(None)
 def solve(i,j):
  if i==len(x) or j==len(y):return 0
  if x[i]==y[j]:return 1+solve(i+1,j+1)
  return max(solve(i+1,j),solve(i,j+1))
 return solve(0,0)
def maze_oracle(a):
 blocked,source,target=a;walls={tuple(x) for x in blocked};q=deque([tuple(source)]);seen={tuple(source)}
 if not blocked and max(source+target)>20:return True
 while q:
  point=q.popleft()
  if point==tuple(target):return True
  for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
   nxt=(point[0]+dr,point[1]+dc)
   if 0<=nxt[0]<=20 and 0<=nxt[1]<=20 and nxt not in walls and nxt not in seen:seen.add(nxt);q.append(nxt)
 return False
def boomerang_oracle(a):
 p=a[0];return (p[1][0]-p[0][0])*(p[2][1]-p[0][1])!=(p[1][1]-p[0][1])*(p[2][0]-p[0][0])
def greater_tree_oracle(a):
 serial=a[0];values,edges=tree_data(serial);ordered=sorted(values);converted={v:sum(x for x in ordered if x>=v) for v in values}
 return [None if value is None else converted[value] for value in serial]
def triangle_oracle(a):
 v=a[0]
 @lru_cache(None)
 def solve(i,j):
  if j-i<2:return 0
  return min(solve(i,k)+solve(k,j)+v[i]*v[k]*v[j] for k in range(i+1,j))
 return solve(0,len(v)-1)
def stones_two_oracle(a):
 s=sorted(a[0]);n=len(s);high=max(s[-1]-s[1]-n+2,s[-2]-s[0]-n+2);low=n
 for i in range(n):
  for j in range(i,n):
   if s[j]-s[i]+1<=n:low=min(low,n-(j-i+1) if not (j-i+1==n-1 and s[j]-s[i]==n-2) else 2)
 return [low,high]
def robot_oracle(a):
 x=y=d=0;dirs=((0,1),(1,0),(0,-1),(-1,0))
 for ch in a[0]:
  if ch=='G':x+=dirs[d][0];y+=dirs[d][1]
  elif ch=='L':d=(d-1)%4
  else:d=(d+1)%4
 return (x,y)==(0,0) or d!=0
def flowers_oracle(a):
 n,paths=a;adj=[set() for _ in range(n)]
 for x,y in paths:adj[x-1].add(y-1);adj[y-1].add(x-1)
 out=[0]*n
 def fill(i):
  if i==n:return True
  for color in range(1,5):
   if all(out[j]!=color for j in adj[i]):
    out[i]=color
    if fill(i+1):return True
  out[i]=0;return False
 fill(0);return out
def partition_oracle(a):
 arr,k=a
 @lru_cache(None)
 def solve(i):
  if i==len(arr):return 0
  return max(max(arr[i:j])* (j-i)+solve(j) for j in range(i+1,min(len(arr),i+k)+1))
 return solve(0)
def duplicate_oracle(a):
 s=a[0]
 for size in range(len(s)-1,0,-1):
  found=sorted({s[i:i+size] for i in range(len(s)-size+1) if s.find(s[i:i+size],i+1)>=0})
  if found:return found[0]
 return ''
def smash_oracle(a):
 stones=a[0][:]
 while len(stones)>1:
  stones.sort();x=stones.pop();y=stones.pop()
  if x!=y:stones.append(x-y)
 return stones[0] if stones else 0
def dedupe_oracle(a):
 s=a[0]
 while True:
  out=[];i=0
  while i<len(s):
   if i+1<len(s) and s[i]==s[i+1]:i+=2
   else:out.append(s[i]);i+=1
  nxt=''.join(out)
  if nxt==s:return s
  s=nxt
def chain_oracle(a):
 words=a[0]
 def pred(x,y):return len(y)==len(x)+1 and any(x==y[:i]+y[i+1:] for i in range(len(y)))
 @lru_cache(None)
 def end(word):return 1+max((end(other) for other in words if pred(other,word)),default=0)
 return max(map(end,words))
def last_two_oracle(a):
 stones=a[0];total=sum(stones)
 possible={sum(stones[i] for i in chosen) for size in range(len(stones)+1) for chosen in combinations(range(len(stones)),size)}
 return min(abs(total-2*x) for x in possible)
def height_oracle(a):return sum(x!=y for x,y in zip(a[0],sorted(a[0])))

def random_city(r):
 n=r.randint(1,5);return [[[r.randint(1,100),r.randint(1,100)] for _ in range(2*n)]]
def random_cells(r):
 rows,cols=r.randint(1,6),r.randint(1,6);return [rows,cols,r.randrange(rows),r.randrange(cols)]
def random_windows(r):
 n=r.randint(2,10);x=r.randint(1,n-1);y=r.randint(1,n-x);return [[r.randint(0,20) for _ in range(n)],x,y]
def random_three(r):return r.sample(range(1,30),3)
def random_border(r):
 rows,cols=r.randint(1,5),r.randint(1,5);g=[[r.randint(1,3) for _ in range(cols)] for _ in range(rows)];return [g,r.randrange(rows),r.randrange(cols),r.randint(1,4)]
def random_lines(r):return [[r.randrange(5) for _ in range(r.randint(1,9))],[r.randrange(5) for _ in range(r.randint(1,9))]]
def random_maze(r):
 target=[r.randint(0,8),r.randint(0,8)];blocked=[]
 for p in ([r.randint(0,8),r.randint(0,8)] for _ in range(r.randint(0,8))):
  if p not in blocked and p not in ([0,0],target):blocked.append(p)
 return [blocked,[0,0],target]
def random_points(r):return [[[r.randint(-8,8),r.randint(-8,8)] for _ in range(3)]]
def random_greater(r):
 values=r.sample(range(0,80),r.randint(1,12));root=None
 for v in values:
  if root is None:root=[v,None,None];continue
  node=root
  while True:
   side=1 if v<node[0] else 2
   if node[side] is None:node[side]=[v,None,None];break
   node=node[side]
 out=[];q=deque([root])
 while q:
  node=q.popleft()
  if node is None:out.append(None)
  else:out.append(node[0]);q.extend(node[1:])
 while out and out[-1] is None:out.pop()
 return [out]
def random_triangle(r):return [[r.randint(1,10) for _ in range(r.randint(3,8))]]
def random_stones_two(r):return [sorted(r.sample(range(1,40),r.randint(3,9)))]
def random_robot(r):return [''.join(r.choice('GLR') for _ in range(r.randint(1,20)))]
def random_flowers(r):
 n=r.randint(1,10);edges=[];degree=[0]*n
 pairs=[(i,j) for i in range(n) for j in range(i+1,n)];r.shuffle(pairs)
 for i,j in pairs:
  if degree[i]<3 and degree[j]<3 and r.random()<.2:edges.append([i+1,j+1]);degree[i]+=1;degree[j]+=1
 return [n,edges]
def random_partition(r):return [[r.randint(0,20) for _ in range(r.randint(1,9))],r.randint(1,4)]
def random_duplicate(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,16)))]
def random_smash(r):return [[r.randint(1,20) for _ in range(r.randint(1,9))]]
def random_text(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,30)))]
def random_chain(r):
 words={''.join(r.choice('abcd') for _ in range(r.randint(1,6))) for _ in range(r.randint(1,9))};return [list(words) or ['a']]
def random_last_two(r):return [[r.randint(1,20) for _ in range(r.randint(1,10))]]
def random_heights(r):return [[r.randint(1,20) for _ in range(r.randint(1,20))]]

CITY='''def minimum_two_city_cost(costs):
 costs.sort(key=lambda c:c[0]-c[1]);n=len(costs)//2
 return sum(c[0] for c in costs[:n])+sum(c[1] for c in costs[n:])
'''
CELLS='''def cells_by_manhattan_distance(rows, cols, r_center, c_center):
 return sorted(([r,c] for r in range(rows) for c in range(cols)),key=lambda p:(abs(p[0]-r_center)+abs(p[1]-c_center),p[0],p[1]))
'''
WINDOWS='''def maximum_two_window_sum(nums, first_len, second_len):
 prefix=[0]
 for value in nums:prefix.append(prefix[-1]+value)
 def order(left,right):
  best=answer=0
  for end in range(left+right,len(nums)+1):
   best=max(best,prefix[end-right]-prefix[end-right-left]);answer=max(answer,best+prefix[end]-prefix[end-right])
  return answer
 return max(order(first_len,second_len),order(second_len,first_len))
'''
THREE='''def moving_three_stones(a, b, c):
 a,b,c=sorted((a,b,c));x=b-a-1;y=c-b-1
 return [0 if x==y==0 else 1 if x<=1 or y<=1 else 2,x+y]
'''
BORDER='''def color_component_border(grid, row, col, color):
 old=grid[row][col];seen={(row,col)};stack=[(row,col)];border=[]
 while stack:
  r,c=stack.pop();is_border=r in (0,len(grid)-1) or c in (0,len(grid[0])-1)
  for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
   nr,nc=r+dr,c+dc
   if 0<=nr<len(grid) and 0<=nc<len(grid[0]):
    if grid[nr][nc]!=old:is_border=True
    elif (nr,nc) not in seen:seen.add((nr,nc));stack.append((nr,nc))
  if is_border:border.append((r,c))
 for r,c in border:grid[r][c]=color
 return grid
'''
LINES='''def maximum_uncrossed_lines(nums1, nums2):
 dp=[0]*(len(nums2)+1)
 for x in nums1:
  previous=0
  for j,y in enumerate(nums2,1):
   saved=dp[j];dp[j]=previous+1 if x==y else max(dp[j],dp[j-1]);previous=saved
 return dp[-1]
'''
MAZE='''def can_escape_large_maze(blocked, source, target):
 walls={tuple(x) for x in blocked};limit=len(blocked)*(len(blocked)-1)//2
 def open_area(start,goal):
  q=__import__('collections').deque([tuple(start)]);seen={tuple(start)}
  while q and len(seen)<=limit:
   r,c=q.popleft()
   if (r,c)==tuple(goal):return True
   for nr,nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
    if 0<=nr<10**6 and 0<=nc<10**6 and (nr,nc) not in walls and (nr,nc) not in seen:seen.add((nr,nc));q.append((nr,nc))
  return len(seen)>limit
 return open_area(source,target) and open_area(target,source)
'''
BOOM='''def is_valid_boomerang(points):
 (x1,y1),(x2,y2),(x3,y3)=points
 return (x2-x1)*(y3-y1)!=(y2-y1)*(x3-x1)
'''
GREATER='''def bst_to_greater_sum(root):
 total=0
 def visit(node):
  nonlocal total
  if node is None:return
  visit(node.right);total+=node.val;node.val=total;visit(node.left)
 visit(root);return root
'''
TRIANGLE='''def minimum_triangulation_score(values):
 n=len(values);dp=[[0]*n for _ in range(n)]
 for gap in range(2,n):
  for i in range(n-gap):
   j=i+gap;dp[i][j]=min(dp[i][k]+dp[k][j]+values[i]*values[k]*values[j] for k in range(i+1,j))
 return dp[0][-1]
'''
STONES2='''def moving_stones_until_consecutive(stones):
 stones.sort();n=len(stones);high=max(stones[-1]-stones[1]-n+2,stones[-2]-stones[0]-n+2);low=n;j=0
 for i in range(n):
  while j+1<n and stones[j+1]-stones[i]+1<=n:j+=1
  inside=j-i+1;low=min(low,2 if inside==n-1 and stones[j]-stones[i]==n-2 else n-inside)
 return [low,high]
'''
ROBOT='''def robot_is_bounded(instructions):
 x=y=direction=0;moves=((0,1),(1,0),(0,-1),(-1,0))
 for command in instructions:
  if command=='G':x+=moves[direction][0];y+=moves[direction][1]
  elif command=='L':direction=(direction-1)%4
  else:direction=(direction+1)%4
 return (x,y)==(0,0) or direction!=0
'''
FLOWERS='''def plant_gardens(n, paths):
 adjacent=[set() for _ in range(n)]
 for x,y in paths:adjacent[x-1].add(y-1);adjacent[y-1].add(x-1)
 answer=[0]*n
 for garden in range(n):answer[garden]=next(c for c in range(1,5) if all(answer[other]!=c for other in adjacent[garden]))
 return answer
'''
PARTITION='''def maximum_partition_sum(arr, k):
 dp=[0]*(len(arr)+1)
 for end in range(1,len(arr)+1):
  largest=0
  for size in range(1,min(k,end)+1):largest=max(largest,arr[end-size]);dp[end]=max(dp[end],dp[end-size]+largest*size)
 return dp[-1]
'''
DUPLICATE='''def longest_duplicate_substring(s):
 def repeated(size):
  seen={};base=911382323;mod=2**61-1;power=pow(base,size,mod);value=0
  for char in s[:size]:value=(value*base+ord(char))%mod
  seen[value]=[0];found=[]
  for i in range(size,len(s)):
   value=(value*base+ord(s[i])-ord(s[i-size])*power)%mod;start=i-size+1
   for old in seen.get(value,[]):
    if s[old:old+size]==s[start:start+size]:found.append(s[start:start+size]);break
   seen.setdefault(value,[]).append(start)
  return min(found) if found else ''
 low,high=0,len(s);answer=''
 while low<high:
  middle=(low+high+1)//2;candidate=repeated(middle)
  if candidate:low=middle;answer=candidate
  else:high=middle-1
 return repeated(low) if low else ''
'''
SMASH='''def last_stone_weight(stones):
 import heapq
 heap=[-x for x in stones];heapq.heapify(heap)
 while len(heap)>1:
  first=-heapq.heappop(heap);second=-heapq.heappop(heap)
  if first!=second:heapq.heappush(heap,second-first)
 return -heap[0] if heap else 0
'''
DEDUPE='''def remove_adjacent_duplicates(s):
 stack=[]
 for char in s:
  if stack and stack[-1]==char:stack.pop()
  else:stack.append(char)
 return ''.join(stack)
'''
CHAIN='''def longest_word_chain(words):
 dp={};answer=0
 for word in sorted(words,key=len):
  dp[word]=1+max((dp.get(word[:i]+word[i+1:],0) for i in range(len(word))),default=0);answer=max(answer,dp[word])
 return answer
'''
LAST2='''def minimum_last_stone_weight(stones):
 total=sum(stones);possible=1
 for stone in stones:possible|=possible<<stone
 half=total//2
 while not (possible>>half)&1:half-=1
 return total-2*half
'''
HEIGHT='''def misplaced_height_count(heights):
 return sum(a!=b for a,b in zip(heights,sorted(heights)))
'''

E=entry
BATCH={
1029:E('minimum_two_city_cost',[('costs','list[list[int]]')],'int',['greedy','sorting'],['There are 2n people and each row gives costs to cities A and B.','Send exactly n people to each city at minimum cost.'],[([[[10,20],[30,200],[400,50],[30,20]]],'Assign people one and four to A and the others to B for total 110.'),([[[259,770],[448,54],[926,667],[184,139],[840,118],[577,469]]],'Sorting cost differences yields total 1859.')],[[c] for c in [[[1,2],[2,1]],[[1,100],[2,100],[100,1],[100,2]],[[5,5],[5,5]],[[10,1],[20,2]],[[1,9],[2,8],[3,7],[9,1],[8,2],[7,3]],[[50,10],[10,50]],[[3,7],[4,8],[9,1],[10,2]],[[8,6],[7,5],[4,9],[3,10]],[[100,1],[1,100],[50,50],[60,60]],[[2,3],[3,2],[4,5],[5,4]],[[9,20],[30,4]],[[12,13],[13,12],[1,50],[50,1]],[[7,70],[8,80],[90,9],[100,10]],[[6,1],[5,2],[4,3],[3,4],[2,5],[1,6]]]],CITY,[CITY.replace('c[0]-c[1]','c[1]-c[0]'),CITY.replace("len(costs)//2","len(costs)//2+1")],['Sorts savings in the wrong direction.','Sends too many people to city A.'],city_oracle,random_city,['Start with everyone assigned conceptually, then compare relative savings.','Sort by costA-costB and send the first n to A.','Sum A costs for the first half and B costs for the rest.','Any inversion in difference can be swapped to no greater cost, proving the sorted split.'],'O(n log n)','O(n)',5),
1030:E('cells_by_manhattan_distance',[('rows','int'),('cols','int'),('rCenter','int'),('cCenter','int')],'list[list[int]]',['matrices','sorting'],['Return every cell exactly once ordered by Manhattan distance.','For equal distance, this exercise uses row then column order.'],[([1,2,0,0],'Cells 0,0 and 0,1 have distances zero and one.'),([2,2,0,1],'The center comes first, followed by tied cells in row-column order.')],[[r,c,rr,cc] for r,c,rr,cc in [(1,1,0,0),(2,1,0,0),(2,1,1,0),(2,2,0,0),(2,2,1,1),(3,3,1,1),(3,4,0,0),(3,4,2,3),(1,5,0,2),(5,1,2,0),(4,4,1,2),(2,5,1,4),(5,3,4,0),(6,6,3,3)]],CELLS,[CELLS.replace('abs(p[1]-c_center)','p[1]-c_center'),CELLS.replace(',p[0],p[1]','')],['Uses signed column displacement instead of absolute distance.','Omits the required deterministic row-column tie break.'],cells_oracle,random_cells,['Generate all coordinates, then rank them by their distance key.','The key is (absolute row difference + absolute column difference, row, column).','Sort the coordinate list once using that tuple.','Tuple ordering enforces increasing distance and the documented deterministic tie order.'],'O(rows*cols log(rows*cols))','O(rows*cols)',3),
1031:E('maximum_two_window_sum',[('nums','list[int]'),('firstLen','int'),('secondLen','int')],'int',['prefix-sums','dynamic-programming'],['Values are nonnegative and the requested lengths fit without overlap.','Either window may appear first.'],[([[0,6,5,2,2,5,1,9,4],1,2],'Length-one 9 plus length-two 6+5 gives twenty.'),([[3,8,1,3,2,1,8,9,0],3,2],'The best nonoverlapping windows total 29.')],[[n,a,b] for n,a,b in [([1,2],1,1),([1,2,3],1,2),([5,5,5,5],2,2),([1,2,3,4,5],1,1),([1,2,3,4,5],2,2),([9,1,1,9],1,1),([2,1,5,6,0,9,5,0,3,8],4,3),([4,0,4,0,4],2,1),([0,0,0,0],1,2),([10,1,1,1,10],2,2),([1,9,1,9,1],1,2),([3,3,1,3,3],2,2),([1,2,8,1,9,2],2,1),([7,1,2,3,8,1,2],3,2)]],WINDOWS,[WINDOWS.replace('end-right-left','end-right-left+1'),WINDOWS.replace('max(order(first_len,second_len),order(second_len,first_len))','order(first_len,second_len)')],['Builds the left window with one element too few.','Considers only the ordering with the first-length window first.'],windows_oracle,random_windows,['Prefix sums make each fixed-length window sum constant-time.','For each ordering, scan the later window while retaining the best earlier window.','Compute both first-before-second and second-before-first, then take the maximum.','Every nonoverlapping pair has exactly one of these two orders and is considered at its later endpoint.'],'O(n)','O(n)',5),
1033:E('moving_three_stones',[('a','int'),('b','int'),('c','int')],'list[int]',['greedy','sorting'],['The three positions are distinct.','Return minimum and maximum legal moves to consecutive positions.'],[([1,2,5],'Move five to three for the minimum one; the maximum is two.'),([4,3,2],'The stones are already consecutive, so both counts are zero.')],[[a,b,c] for a,b,c in [(1,3,5),(1,4,7),(1,2,3),(1,3,4),(2,5,9),(10,1,5),(100,50,51),(3,8,9),(1,10,20),(7,4,9),(2,4,20),(5,6,20),(1,99,100),(20,10,1)]],THREE,[THREE.replace('x<=1 or y<=1','x==0 or y==0'),THREE.replace('x+y','max(x,y)')],['Misses a one-empty-position shortcut.','Uses only the larger gap for the maximum moves.'],three_stones_oracle,random_three,['Sort positions and inspect the two empty gaps.','A gap of zero or one permits a one-move finish; otherwise two endpoint moves are required.','Maximum moves consume every empty position across both gaps.','Endpoint moves can close one gap per move, while the shortcut precisely captures placing an endpoint beside the other two.'],'O(1)','O(1)',3),
1034:E('color_component_border',[('grid','list[list[int]]'),('row','int'),('col','int'),('color','int')],'list[list[int]]',['matrices','depth-first-search','recursion'],['Use four-direction connectivity.','Recolor only component cells on the grid edge or adjacent to a different color.'],[([[[1,1],[1,2]],0,0,3],'The three connected ones are all boundary cells and become three.'),([[[1,2,2],[2,3,2]],0,1,3],'The connected twos touching 0,1 form a border and are recolored.')],[[g,r,c,k] for g,r,c,k in [([[1]],0,0,2),([[1,1]],0,0,2),([[1,1],[1,1]],0,0,2),([[1,1,1],[1,1,1],[1,1,1]],1,1,2),([[1,2],[2,2]],1,1,3),([[1,2,1],[2,2,2],[1,2,1]],1,1,4),([[1,1,2],[1,2,2]],0,0,3),([[2,2,2],[2,1,2],[2,2,2]],0,0,5),([[1,1,1],[1,2,1],[1,1,1]],1,1,3),([[3,3],[3,4]],0,1,3),([[1,2,3]],0,1,4),([[1],[1],[2]],1,0,5),([[1,1,1],[1,1,2]],0,0,9),([[2,1],[1,1]],1,1,2)]],BORDER,[BORDER.replace('if is_border:border.append((r,c))','border.append((r,c))'),BORDER.replace('grid[nr][nc]!=old','grid[nr][nc]==old')],['Recolors every component cell, including protected interior cells.','Marks same-color neighbors as exterior border evidence.'],border_oracle,random_border,['First discover the component without changing colors that connectivity checks rely on.','A component cell is border when on an edge or beside a noncomponent cell.','DFS/BFS records border coordinates, then recolor those coordinates afterward.','Discovery visits exactly the component and the local border predicate matches the definition.'],'O(rows*cols)','O(rows*cols)',5),
1035:E('maximum_uncrossed_lines',[('nums1','list[int]'),('nums2','list[int]')],'int',['dynamic-programming','longest-common-subsequence'],['Lines connect equal values and cannot cross or reuse endpoints.','Return the maximum line count.'],[([[1,4,2],[1,2,4]],'Choose matches for one and either four or two, giving two lines.'),([[2,5,1,2,5],[10,5,2,1,5,2]],'An order-preserving set of three equal matches is possible.')],[[x,y] for x,y in [([1],[1]),([1],[2]),([1,2],[1,2]),([1,2],[2,1]),([1,1],[1]),([1],[1,1]),([1,2,3],[3,2,1]),([1,2,1],[1,1]),([2,2,2],[2,2]),([1,3,7,1,7,5],[1,9,2,5,1]),([0,1,0],[1,0,1]),([4,5,6],[4,5,6]),([1,4,2],[1,2,4]),([2,5,1,2,5],[10,5,2,1,5,2])]],LINES,[LINES.replace('previous+1 if x==y','previous if x==y'),LINES.replace('max(dp[j],dp[j-1])','min(dp[j],dp[j-1])')],['Matches equal endpoints without adding the new line.','Keeps the smaller rather than larger skip alternative.'],lines_oracle,random_lines,['Noncrossing connections preserve index order, exactly the longest common subsequence condition.','Use one DP row and retain the prior diagonal value.','On equality take diagonal+1; otherwise take the larger top/left state.','The final state exhausts matching or skipping each pair of prefixes.'],'O(n*m)','O(m)',5),
1036:E('can_escape_large_maze',[('blocked','list[list[int]]'),('source','list[int]'),('target','list[int]')],'bool',['graphs','breadth-first-search'],['Coordinates lie in a million-square grid and blocked contains at most 200 cells.','Return whether source and target can connect without blocked cells.'],[([[[0,1],[1,0]],[0,0],[0,2]],'The two blocked neighbors trap the corner source.'),([[],[0,0],[999999,999999]],'With no blocked cells the endpoints connect.')],[[b,s,t] for b,s,t in [([], [0,0],[0,1]),([[0,1]],[0,0],[1,0]),([[0,1],[1,0]],[0,0],[2,2]),([[1,0],[1,1],[1,2]],[0,0],[2,0]),([[0,1],[1,1],[2,1]],[1,0],[1,2]),([[2,2]],[0,0],[4,4]),([[0,2],[1,1],[2,0]],[0,0],[3,3]),([[1,0],[1,2],[0,1],[2,1]],[1,1],[3,3]),([[5,5],[5,6],[6,5]],[0,0],[6,6]),([[0,1],[1,0]],[2,2],[0,0]),([[3,3],[3,4],[4,3]],[4,4],[0,0]),([[10,10]],[1,1],[8,8]),([[2,1],[2,2],[2,3]],[1,2],[3,2]),([[1,2],[2,1],[2,3],[3,2]],[2,2],[0,0])]],MAZE,[MAZE.replace('and open_area(target,source)','or open_area(target,source)'),MAZE.replace('len(seen)>limit','len(seen)>=limit')],['Accepts when only one endpoint is proven unconfined.','Treats reaching the enclosure bound as escaping one step too early.'],maze_oracle,random_maze,['At most b blocked cells can enclose at most b(b-1)/2 reachable cells.','Bounded BFS from both endpoints stops after exceeding that enclosure limit.','Succeed when each endpoint reaches the other or proves it is not enclosed.','If neither endpoint is enclosed, the vast remaining grid connects their open regions.'],'O(b^2)','O(b^2)',8),
1037:E('is_valid_boomerang',[('points','list[list[int]]')],'bool',['geometry','math'],['Exactly three two-dimensional integer points are provided.','Return true exactly when they are distinct and noncollinear.'],[([[[1,1],[2,3],[3,2]]],'The two displacement vectors have a nonzero cross product.'),([[[1,1],[2,2],[3,3]]],'All points lie on one diagonal, so this is not a boomerang.')],[[p] for p in [[[0,0],[1,0],[0,1]],[[0,0],[1,1],[2,2]],[[0,0],[0,1],[0,2]],[[1,1],[1,1],[2,3]],[[-1,0],[0,1],[1,0]],[[5,5],[6,7],[8,6]],[[0,0],[2,0],[1,3]],[[1,2],[3,4],[5,7]],[[10,0],[0,10],[10,10]],[[-2,-2],[-1,-1],[0,0]],[[3,1],[3,2],[4,1]],[[1,5],[2,3],[4,4]],[[0,1],[1,0],[2,1]],[[7,7],[8,9],[9,8]]]],BOOM,[BOOM.replace('!=','=='),BOOM.replace('(y2-y1)*(x3-x1)','(y2-y1)+(x3-x1)')],['Returns true for zero cross product instead of nonzero.','Adds one cross-product factor instead of multiplying it.'],boomerang_oracle,random_points,['Three points are noncollinear exactly when two displacement vectors have nonzero cross product.','Compute (x2-x1)(y3-y1)-(y2-y1)(x3-x1).','Return whether the two products differ.','A zero cross product includes duplicate points and all collinear configurations.'],'O(1)','O(1)',3),
1038:E('bst_to_greater_sum',[('root','TreeNode | None')],'TreeNode | None',['trees','binary-search-trees','recursion'],['BST values are distinct.','Replace each value by the sum of all original values greater than or equal to it.'],[([[4,1,6,0,2,5,7,None,None,None,3,None,None,None,8]],'Reverse inorder accumulates values from eight down to zero.'),([[0,None,1]],'One remains one and zero becomes one.')],[[t] for t in [[1],[2,1],[1,None,2],[2,1,3],[4,2,6,1,3,5,7],[5,3,8,2,4,7,9],[0],[10,5,None,1],[1,None,5,None,9],[3,1,4,None,2],[8,4,12,2,6,10,14],[6,3,9,1,4,8,10],[20,10,30,None,15,25,40],[7,5,9,3,6,8,10]]],GREATER,[GREATER.replace('visit(node.right)','visit(node.left)',1),GREATER.replace('total+=node.val','total=node.val')],['Traverses the smaller left subtree before updating the node.','Overwrites rather than accumulates the greater-value sum.'],greater_tree_oracle,random_greater,['Reverse inorder visits BST values from greatest to least.','Maintain a running sum across right-node-left traversal.','After the right subtree, add node.val to total and replace node.val with total.','At each node, total contains exactly its original value and every greater value.'],'O(n)','O(height)',5),
1039:E('minimum_triangulation_score',[('values','list[int]')],'int',['dynamic-programming','interval-dp'],['At least three positive vertex values describe a convex polygon in order.','Minimize the sum of triangle vertex products.'],[([[1,2,3]],'The sole triangle scores 1*2*3=6.'),([[3,7,4,5]],'Choosing the diagonal between values three and four gives score 144.')],[[x] for x in [[1,1,1],[1,2,3,4],[3,7,4,5],[1,3,1,4,1,5],[5,5,5],[2,3,4,5,6],[1,10,1,10],[2,2,3,3,4],[9,1,2,8,3],[1,2,1,2,1],[4,6,2,7,3],[10,9,8],[2,5,1,6,4],[7,3,5,2,8,1]]],TRIANGLE,[TRIANGLE.replace('min(dp[i][k]','max(dp[i][k]'),TRIANGLE.replace('values[i]*values[k]*values[j]','values[i]+values[k]+values[j]')],['Maximizes rather than minimizes interval triangulation cost.','Adds vertex values instead of multiplying triangle weight.'],triangle_oracle,random_triangle,['Every triangulation of interval i..j has one triangle using edge (i,j) and some middle k.','Use interval DP over increasing gaps.','Minimize dp[i][k]+dp[k][j]+values[i]*values[k]*values[j] across k.','Removing that boundary triangle splits the polygon into exactly the two independent subpolygons.'],'O(n^3)','O(n^2)',5),
1040:E('moving_stones_until_consecutive',[('stones','list[int]')],'list[int]',['sorting','sliding-window'],['At least three distinct stone positions are provided.','An endpoint move must place it strictly inside the remaining range and not leave it an endpoint.'],[([[7,4,9]],'Sorted positions 4,7,9 need one minimum move and allow two maximum moves.'),([[6,5,4,3,10]],'The special near-consecutive arrangement requires two minimum moves.')],[[s] for s in [[1,2,3],[1,3,5],[1,2,5],[4,7,9],[1,2,3,4,10],[1,3,4,5,6],[1,10,20],[2,4,6,8],[1,2,4,7],[5,6,7,8,20],[1,5,6,7,8],[3,8,9,10],[1,4,9,15],[2,3,10,11,12]]],STONES2,[STONES2.replace('stones[j+1]-stones[i]+1<=n','stones[j+1]-stones[i]+1<n'),STONES2.replace('max(stones[-1]-stones[1]-n+2,stones[-2]-stones[0]-n+2)','min(stones[-1]-stones[1]-n+2,stones[-2]-stones[0]-n+2)')],['Rejects a window spanning exactly n consecutive positions.','Uses the smaller endpoint-gap plan for maximum moves.'],stones_two_oracle,random_stones_two,['Maximum moves consume interior holes after choosing which endpoint gap to abandon.','Minimum moves maximize stones already fitting in an interval of width n using a sliding window.','Use n-window count, with the n-1 tightly packed special case requiring two moves.','Every normal missing spot can be filled by one endpoint move; the special rule prevents the apparent one-move finish.'],'O(n log n)','O(n)',8),
1041:E('robot_is_bounded',[('instructions','str')],'bool',['simulation','geometry'],['Instructions contain G, L, and R and repeat forever.','Return whether the path stays inside some circle.'],[(['GGLLGG'],'One cycle returns to the origin, so repetition is bounded.'),(['GG'],'The robot advances north every cycle without turning, so it is unbounded.')],[[s] for s in ['G','L','R','GL','GR','GG','LL','RR','GLGLG','GRGRG','GGLLGG','GLRLLG','GGRRGG','LRLR','GGGLLLL']],ROBOT,[ROBOT.replace("or direction!=0","and direction!=0"),ROBOT.replace("direction=(direction-1)%4","direction=(direction+1)%4")],['Requires both returning to origin and changing direction.','Turns left in the same direction as right.'],robot_oracle,random_robot,['After one cycle, only displacement and final direction determine all later cycles.','The path is bounded if displacement is zero or orientation changed.','Simulate one instruction string from origin facing north.','A changed direction rotates repeated displacement vectors to cancel within four cycles; unchanged nonzero displacement repeats forever.'],'O(n)','O(1)',5),
1042:E('plant_gardens',[('n','int'),('paths','list[list[int]]')],'list[int]',['graphs','greedy'],['Each garden has degree at most three.','Use the smallest available flower type from 1..4 for gardens in label order.'],[([3,[[1,2],[2,3],[3,1]]],'Greedy assigns the triangle flower types one, two, and three.'),([4,[[1,2],[3,4]]],'Disconnected edges receive deterministic colors one,two,one,two.')],[[n,p] for n,p in [(1,[]),(2,[]),(2,[[1,2]]),(3,[[1,2],[2,3]]),(3,[[1,2],[2,3],[1,3]]),(4,[[1,2],[2,3],[3,4],[4,1]]),(4,[[1,2],[1,3],[1,4]]),(5,[[1,2],[2,3],[3,4],[4,5]]),(5,[]),(6,[[1,2],[1,3],[2,4],[3,5],[4,6]]),(4,[[1,2],[2,3]]),(5,[[1,5],[2,5],[3,5]]),(6,[[1,2],[2,3],[3,1],[4,5]]),(7,[[1,2],[1,3],[1,4],[5,6],[6,7]])]],FLOWERS,[FLOWERS.replace('range(1,5)','range(1,4)'),FLOWERS.replace('answer[other]!=c','answer[other]==c')],['Offers only three colors despite a degree-three garden possibly needing the fourth.','Selects colors already used by neighbors.'],flowers_oracle,random_flowers,['At most three neighbor colors can be forbidden when processing a garden.','Choose the smallest type 1..4 absent from already colored neighbors.','Build adjacency sets, then fill gardens in label order.','Four choices guarantee one remains, and later gardens will respect this color in turn.'],'O(n+paths)','O(n+paths)',3),
1043:E('maximum_partition_sum',[('arr','list[int]'),('k','int')],'int',['dynamic-programming','arrays'],['Values are nonnegative and every partition length is at most k.','Replace a partition by its maximum repeated across its length.'],[([[1,15,7,9,2,5,10],3],'Optimal partitions produce total 84.'),([[1],1],'The only one-element partition retains value one.')],[[x,k] for x,k in [([1,2],1),([1,2],2),([5,1,2],2),([1,1,1],3),([9,1,1,9],2),([0,0,5],3),([3,7,2,8],2),([1,15,7,9,2,5,10],2),([1,15,7,9,2,5,10],1),([2,3,4,5],3),([10,1,1,1],4),([4,2,9,1,3],2),([6,5,4,3,2],3),([1,9,1,9,1],3)]],PARTITION,[PARTITION.replace('largest*size','largest'),PARTITION.replace('min(k,end)','min(k-1,end)')],['Adds the partition maximum once instead of once per replaced element.','Never considers partitions of the allowed maximum length k.'],partition_oracle,random_partition,['Let dp[end] be the best result for the prefix ending before end.','Try every final partition size up to k while maintaining its maximum.','Transition from dp[end-size]+maximum*size.','Every valid partitioning has exactly one final segment considered by this recurrence.'],'O(n*k)','O(n)',5),
1044:E('longest_duplicate_substring',[('s','str')],'str',['strings','rolling-hash','binary-search'],['Return the lexicographically smallest among equally longest repeated substrings.','Overlapping occurrences are allowed; return empty when none repeats.'],[(['banana'],'Ana occurs twice and is the unique longest duplicate.'),(['abcd'],'No nonempty substring repeats.')],[[s] for s in ['a','aa','aaa','abab','abcabc','mississippi','abcdabc','aaaaa','ababa','bananaaa','xyzxyzx','abcabca','zzxyzzxy','thethree']],DUPLICATE,[DUPLICATE.replace('low=middle;answer=candidate','high=middle-1'),DUPLICATE.replace('min(found)','max(found)')],['Shrinks the search after finding a repeated length.','Chooses the lexicographically largest tied duplicate.'],duplicate_oracle,random_duplicate,['Existence of a duplicate is monotone by substring length, enabling binary search.','Use a rolling hash to group equal-length windows, then verify text equality to avoid collisions.','Binary-search the greatest feasible length and select the smallest verified duplicate at that length.','Hashing finds candidate equal windows efficiently, while direct verification makes the result deterministic and collision-safe.'],'O(n log n)','O(n)',8),
1046:E('last_stone_weight',[('stones','list[int]')],'int',['heaps','simulation'],['Repeatedly smash the two greatest weights.','Return the last weight or zero when none remains.'],[([[2,7,4,1,8,1]],'Smashes ultimately leave weight one.'),([[1]],'A sole stone is already the result.')],[[s] for s in [[1,1],[1,2],[2,2,2],[3,7,2],[10,4,6],[5,5,5,5],[1,2,3,4,5],[9,3,2,10],[8,8,1],[2,7,4,1,8,2],[20,1,1,1],[6,4,3,2],[100,99],[3,3,3]]],SMASH,[SMASH.replace('second-first','first-second'),SMASH.replace('if first!=second','if first==second')],['Pushes a negative difference into the max-heap representation incorrectly.','Keeps a difference only when equal stones smash.'],smash_oracle,random_smash,['Python’s min-heap can represent a max-heap by negating weights.','Pop two largest; push their positive difference only when unequal.','Continue until at most one heap entry remains.','Each loop exactly simulates one mandated smash and preserves all remaining weights.'],'O(n log n)','O(n)',3),
1047:E('remove_adjacent_duplicates',[('s','str')],'str',['stacks','strings'],['Repeatedly delete adjacent equal pairs until stable.','The final string is unique.'],[(['abbaca'],'Remove bb, then aa, leaving ca.'),(['azxxzy'],'Removing xx exposes zz, leaving ay.')],[[s] for s in ['a','aa','aaa','aaaa','ab','abba','aabb','abcddcba','mississippi','ababab','ccbaab','zzxyyx','aabcca','abcdedcba']],DEDUPE,[DEDUPE.replace('stack.pop()','stack.append(char)'),DEDUPE.replace("stack[-1]==char","stack[-1]!=char")],['Duplicates an equal character instead of removing the pair.','Removes adjacent unequal characters.'],dedupe_oracle,random_text,['A new character can interact only with the current surviving suffix.','Maintain the reduced prefix as a stack.','Pop when the top equals the new character; otherwise push it.','The stack is stable after every prefix, so exposed chain reactions happen immediately.'],'O(n)','O(n)',3),
1048:E('longest_word_chain',[('words','list[str]')],'int',['dynamic-programming','strings'],['Words are distinct lowercase strings.','A predecessor deletes exactly one character from the longer word.'],[([['a','b','ba','bca','bda','bdca']],'One longest chain is a,ba,bda,bdca of length four.'),([['xbc','pcxbcf','xb','cxbc','pcxbc']],'The chain xb,xbc,cxbc,pcxbc,pcxbcf has length five.')],[[w] for w in [['a'],['a','ab'],['a','ba'],['ab','ac'],['a','ab','abc'],['abc','abdc'],['x','xy','xyz','wxyz'],['a','b','ba','bca'],['abcd','dbqca'],['a','aa','aaa','aaaa'],['cat','at','a'],['z','za','zab','zcab'],['ab','cab','scab','sscab'],['i','in','pin','spin']]],CHAIN,[CHAIN.replace('word[:i]+word[i+1:]','word[:i]'),CHAIN.replace('1+max','max')],['Checks only prefixes rather than every one-character deletion.','Fails to count the current word in a chain.'],chain_oracle,random_chain,['Processing by length guarantees every predecessor state is ready.','Generate all predecessors by deleting each character once.','Set dp[word]=1+maximum predecessor length and track the global maximum.','Every legal chain step is one of those deletions, so the best predecessor yields the best chain ending here.'],'O(total characters squared)','O(words)',5),
1049:E('minimum_last_stone_weight',[('stones','list[int]')],'int',['dynamic-programming','knapsack'],['Any two stones may be smashed in any order.','Return the minimum possible final weight.'],[([[2,7,4,1,8,1]],'Partition totals 11 and 12, whose difference is one.'),([[31,26,33,21,40]],'The closest achievable partition difference is five.')],[[s] for s in [[1],[1,1],[1,2],[2,2,2],[1,2,3],[5,5,10],[3,7,2],[8,1,1],[10,4,6],[2,7,4,1,8,2],[20,1,1,1],[6,4,3,2],[9,8,7,6],[15,5,5,5]]],LAST2,[LAST2.replace('possible|=possible<<stone','possible=possible<<stone'),LAST2.replace('half=total//2','half=total')],['Discards prior subset sums instead of unioning new choices.','Searches from the total rather than the half-total partition target.'],last_two_oracle,random_last_two,['The final weight equals the difference between two groups of original stones.','Find an achievable subset sum as close as possible to total/2.','Use a bitset where bit s marks an achievable sum; update with possible |= possible << stone.','The closest two-way partition minimizes total-2*s and every smash outcome corresponds to such signs.'],'O(n*sum stones)','O(sum stones)',5),
1051:E('misplaced_height_count',[('heights','list[int]')],'int',['arrays','sorting'],['Expected order is nondecreasing.','Count positions differing from the sorted sequence.'],[([[1,1,4,2,1,3]],'Sorted order is 1,1,1,2,3,4, differing at three positions.'),([[5,1,2,3,4]],'Every position differs from sorted order.')],[[h] for h in [[1],[1,1],[2,1],[1,2],[3,2,1],[1,2,3],[2,1,2],[5,1,2,3,4],[1,1,1,2,2],[2,2,1,1],[10,3,8,2],[4,4,3,4],[1,3,2,2,4],[9,8,7,6,5]]],HEIGHT,[HEIGHT.replace('a!=b','a==b'),HEIGHT.replace('sorted(heights)','sorted(heights,reverse=True)')],['Counts matching rather than misplaced positions.','Compares against descending rather than expected ascending order.'],height_oracle,random_heights,['The target lineup is uniquely determined by sorting.','Create the sorted copy and compare corresponding positions.','Count indices where actual and expected heights differ.','Each mismatch is exactly a student position that violates the requested expected sequence.'],'O(n log n)','O(n)',3),
}

BATCH[1030]['params']=[('rows','int','raw'),('cols','int','raw'),('r_center','int','raw'),('c_center','int','raw')]
BATCH[1042]['wrong'][0]='''def plant_gardens(n, paths):
 return [1]*n
'''
BATCH[1042]['wrong_reasons'][0]='Uses one flower type for every garden and ignores adjacent conflicts.'
BATCH[1042]['wrong'][1]='''def plant_gardens(n, paths):
 return [i%2+1 for i in range(n)]
'''
BATCH[1042]['wrong_reasons'][1]='Alternates only two colors by label, which fails edges connecting equal-parity labels.'
BATCH[1044]['wrong'][1]=DUPLICATE.replace("return repeated(low) if low else ''","return s[:low] if low else ''")
BATCH[1044]['wrong_reasons'][1]='Returns a prefix of the correct length without proving that prefix repeats.'
BATCH[1049]['wrong'][0]=LAST2.replace('possible|=possible<<stone','possible|=stone')
BATCH[1049]['wrong_reasons'][0]='Treats the stone value itself as a bit mask instead of shifting every achievable subset sum.'
for pid in (1038,):
 BATCH[pid]['params'][0]=('root','TreeNode | None','treenode');BATCH[pid]['adapter']='treenode'
