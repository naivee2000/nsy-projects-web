"""First half of batch 99: connectivity, combinatorics, routes, and matching."""
from collections import Counter
from functools import lru_cache
from itertools import combinations,permutations
from math import comb
from .import_batch_055 import entry
MOD=1_000_000_007
def islands(grid):
 rows,cols=len(grid),len(grid[0]);seen=set();count=0
 for r in range(rows):
  for c in range(cols):
   if not grid[r][c] or (r,c) in seen:continue
   count+=1;seen.add((r,c));stack=[(r,c)]
   while stack:
    x,y=stack.pop()
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
     nx,ny=x+dx,y+dy
     if 0<=nx<rows and 0<=ny<cols and grid[nx][ny] and (nx,ny) not in seen:seen.add((nx,ny));stack.append((nx,ny))
 return count
def disconnect_o(a):
 grid=a[0]
 if islands(grid)!=1:return 0
 land=[(r,c) for r,row in enumerate(grid) for c,v in enumerate(row) if v]
 for size in (1,2):
  for removed in combinations(land,size):
   copy=[row[:] for row in grid]
   for r,c in removed:copy[r][c]=0
   if islands(copy)!=1:return size
def shape(order):
 root=None
 for value in order:
  if root is None:root=[value,None,None];continue
  node=root
  while True:
   side=1 if value<node[0] else 2
   if node[side] is None:node[side]=[value,None,None];break
   node=node[side]
 def form(node):return None if node is None else (form(node[1]),form(node[2]))
 return form(root)
def reorder_o(a):
 nums=a[0];wanted=shape(nums);return (sum(shape(p)==wanted for p in permutations(nums))-1)%MOD
def split_o(a):
 s=a[0];return sum(s[:i].count('1')==s[i:j].count('1')==s[j:].count('1') for i in range(1,len(s)-1) for j in range(i+1,len(s)))%MOD
def remove_o(a):
 arr=a[0]
 for size in range(len(arr)+1):
  for start in range(len(arr)-size+1):
   keep=arr[:start]+arr[start+size:]
   if all(x<=y for x,y in zip(keep,keep[1:])):return size
def routes_o(a):
 locations,start,finish,fuel=a
 @lru_cache(None)
 def go(city,left):
  answer=city==finish
  for nxt in range(len(locations)):
   cost=abs(locations[city]-locations[nxt])
   if nxt!=city and cost<=left:answer+=go(nxt,left-cost)
  return answer%MOD
 return go(start,fuel)
def replace_o(a):
 s=a[0];best=None
 def visit(index,built):
  nonlocal best
  if index==len(s):best=built if best is None or built<best else best;return
  choices='abc' if s[index]=='?' else s[index]
  for char in choices:
   if not built or built[-1]!=char:visit(index+1,built+char)
 visit(0,'');return best
def triplets_o(a):
 x,y=a;answer=0
 for value in x:
  answer+=sum(value*value==y[i]*y[j] for i in range(len(y)) for j in range(i+1,len(y)))
 for value in y:
  answer+=sum(value*value==x[i]*x[j] for i in range(len(x)) for j in range(i+1,len(x)))
 return answer
def rope_o(a):
 colors,cost=a;answer=0
 for mask in range(1<<len(colors)):
  kept=[i for i in range(len(colors)) if mask>>i&1]
  if all(colors[x]!=colors[y] for x,y in zip(kept,kept[1:])):answer=max(answer,sum(cost[i] for i in kept))
 return sum(cost)-answer
def traversable(n,edges,person):
 graph=[[] for _ in range(n)]
 for kind,u,v in edges:
  if kind==3 or kind==person:graph[u-1].append(v-1);graph[v-1].append(u-1)
 seen={0};stack=[0]
 while stack:
  for nxt in graph[stack.pop()]:
   if nxt not in seen:seen.add(nxt);stack.append(nxt)
 return len(seen)==n
def edges_o(a):
 n,edges=a;best=-1
 for mask in range(1<<len(edges)):
  keep=[edge for i,edge in enumerate(edges) if mask>>i&1]
  if traversable(n,keep,1) and traversable(n,keep,2):best=max(best,len(edges)-len(keep))
 return best
def boxes_o(a):
 boxes,warehouse=a;effective=[max(min(warehouse[:i+1]),min(warehouse[i:])) for i in range(len(warehouse))];best=0
 for size in range(1,min(len(boxes),len(warehouse))+1):
  for chosen in combinations(boxes,size):
   if any(all(box<=room for box,room in zip(order,rooms)) for order in permutations(chosen) for rooms in combinations(effective,size)):best=size;break
 return best
def rdisconnect(r):
 rows,cols=r.randint(1,5),r.randint(1,5);return [[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)]]
def rreorder(r):
 n=r.randint(1,7);return [r.sample(range(1,n+1),n)]
def rsplit(r):return [''.join(r.choice('01') for _ in range(r.randint(3,30)))]
def rremove(r):return [[r.randint(-10,10) for _ in range(r.randint(1,15))]]
def rroutes(r):
 n=r.randint(2,7);loc=r.sample(range(1,30),n);return [loc,r.randrange(n),r.randrange(n),r.randint(0,15)]
def rreplace(r):
 out=[]
 for _ in range(r.randint(1,9)):
  choices=['a','b','?']
  if out and out[-1]!='?':choices.remove(out[-1])
  out.append(r.choice(choices))
 return [''.join(out)]
def rtriplets(r):return [[r.randint(1,12) for _ in range(r.randint(1,8))],[r.randint(1,12) for _ in range(r.randint(1,8))]]
def rrope(r):
 n=r.randint(1,10);return [''.join(r.choice('abc') for _ in range(n)),[r.randint(1,20) for _ in range(n)]]
def redges(r):
 n=r.randint(2,5);all_edges=[[kind,u,v] for kind in (1,2,3) for u in range(1,n+1) for v in range(u+1,n+1)];r.shuffle(all_edges);return [n,all_edges[:r.randint(1,min(8,len(all_edges)))]]
def rboxes(r):return [[r.randint(1,10) for _ in range(r.randint(1,7))],[r.randint(1,10) for _ in range(r.randint(1,7))]]
DISCONNECT='''def minimum_island_disconnect_days(grid):
 rows,cols=len(grid),len(grid[0])
 def count():
  seen=set();components=0
  for row in range(rows):
   for col in range(cols):
    if not grid[row][col] or (row,col) in seen:continue
    components+=1;seen.add((row,col));stack=[(row,col)]
    while stack:
     x,y=stack.pop()
     for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
      nxt=(x+dx,y+dy)
      if 0<=nxt[0]<rows and 0<=nxt[1]<cols and grid[nxt[0]][nxt[1]] and nxt not in seen:seen.add(nxt);stack.append(nxt)
  return components
 if count()!=1:return 0
 for row in range(rows):
  for col in range(cols):
   if grid[row][col]:
    grid[row][col]=0;disconnected=count()!=1;grid[row][col]=1
    if disconnected:return 1
 return 2
'''
REORDER='''def same_bst_reorder_count(nums):
 from math import comb
 def count(values):
  if len(values)<3:return 1
  left=[v for v in values[1:] if v<values[0]];right=[v for v in values[1:] if v>values[0]]
  return comb(len(left)+len(right),len(left))*count(left)*count(right)%1000000007
 return (count(nums)-1)%1000000007
'''
SPLIT='''def equal_one_three_splits(s):
 ones=s.count('1')
 if ones%3:return 0
 if ones==0:return ((len(s)-1)*(len(s)-2)//2)%1000000007
 each=ones//3;seen=first=answer=0
 for char in s[:-1]:
  seen+=char=='1'
  if seen==each:first+=1
  elif seen==2*each:answer+=first
 return answer%1000000007
'''
REMOVE='''def shortest_sorted_removal(arr):
 n=len(arr);right=n-1
 while right and arr[right-1]<=arr[right]:right-=1
 if right==0:return 0
 answer=right;left=0
 while left==0 or arr[left-1]<=arr[left]:
  while right<n and arr[right]<arr[left]:right+=1
  answer=min(answer,right-left-1);left+=1
  if left==n:break
 return answer
'''
ROUTES='''def count_fueled_routes(locations, start, finish, fuel):
 from functools import lru_cache
 @lru_cache(None)
 def visit(city,remaining):
  answer=city==finish
  for nxt in range(len(locations)):
   cost=abs(locations[city]-locations[nxt])
   if nxt!=city and cost<=remaining:answer+=visit(nxt,remaining-cost)
  return answer%1000000007
 return visit(start,fuel)
'''
REPLACE='''def replace_questions_without_repeats(s):
 chars=list(s)
 for index,char in enumerate(chars):
  if char=='?':
   for choice in 'abc':
    if (index==0 or chars[index-1]!=choice) and (index+1==len(chars) or chars[index+1]!=choice):chars[index]=choice;break
 return ''.join(chars)
'''
TRIPLETS='''def count_square_product_triplets(nums1, nums2):
 def count(left,right):
  frequencies=Counter(right);answer=0
  for value in left:
   square=value*value
   for factor,amount in frequencies.items():
    if square%factor:continue
    other=square//factor
    if other not in frequencies:continue
    answer+=amount*(frequencies[other]-(factor==other))
  return answer//2
 return count(nums1,nums2)+count(nums2,nums1)
'''
ROPE='''def minimum_colorful_rope_removal(colors, needed_time):
 answer=0;index=0
 while index<len(colors):
  end=index+1;total=needed_time[index];largest=needed_time[index]
  while end<len(colors) and colors[end]==colors[index]:total+=needed_time[end];largest=max(largest,needed_time[end]);end+=1
  answer+=total-largest;index=end
 return answer
'''
EDGES='''def maximum_removable_traversal_edges(n, edges):
 class DSU:
  def __init__(self):self.parent=list(range(n+1));self.parts=n
  def find(self,x):
   while self.parent[x]!=x:self.parent[x]=self.parent[self.parent[x]];x=self.parent[x]
   return x
  def union(self,x,y):
   x,y=self.find(x),self.find(y)
   if x==y:return False
   self.parent[x]=y;self.parts-=1;return True
 alice=DSU();bob=DSU();used=0
 for kind,u,v in edges:
  if kind==3:
   merged=alice.union(u,v);bob.union(u,v);used+=merged
 for kind,u,v in edges:
  if kind==1:used+=alice.union(u,v)
  elif kind==2:used+=bob.union(u,v)
 return len(edges)-used if alice.parts==bob.parts==1 else -1
'''
BOXES='''def maximum_two_sided_warehouse_boxes(boxes, warehouse):
 capacities=[max(min(warehouse[:index+1]),min(warehouse[index:])) for index in range(len(warehouse))]
 boxes=sorted(boxes);capacities.sort();box=answer=0
 for room in capacities:
  if box<len(boxes) and boxes[box]<=room:answer+=1;box+=1
 return answer
'''
E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1568:S('minimum_island_disconnect_days',[('grid','list[list[int]]')],'int',['recursion','grids'],['Land uses four-directional connectivity; the grid is disconnected unless it contains exactly one island.','Each day removes one land cell; return the minimum days needed.'],[([[[0,1,1,0],[0,1,1,0],[0,0,0,0]]],'No single cell disconnects the two-by-two island, but removing two cells does.'),([[[1,1]]],'Removing either cell leaves one island, while removing both leaves zero islands, so two days are required.')],[[g] for g in [[[0]],[[1]],[[1,1]],[[1,0,1]],[[0,1,1,0],[0,1,1,0],[0,0,0,0]],[[1,1],[1,0]],[[1,1,1]],[[1,1,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]],[[1,0],[0,1]],[[1,1,0],[0,1,1]],[[1,1,1],[0,1,0]],[[0,0],[0,0]],[[1,1,1],[1,0,1],[1,1,1]]]],DISCONNECT,[DISCONNECT.replace('if disconnected:return 1','if disconnected:return 2'),DISCONNECT.replace('if count()!=1:return 0','if count()>1:return 0')],['Charges two days even when one articulation cell disconnects the island.','Treats an empty all-water grid as connected.'],disconnect_o,rdisconnect,['First count islands; anything other than exactly one is already disconnected.','Temporarily remove each land cell and recount, restoring it afterward.','Return one if any removal disconnects; otherwise return two.','A connected grid always becomes disconnected after at most two removals, so these exhaustive cases are sufficient.'],'O((rows*cols)²)','O(rows*cols)',8),
1569:S('same_bst_reorder_count',[('nums','list[int]')],'int',['trees','combinatorics'],['nums is a permutation; insert it into a BST in order.','Count other reorderings that create the identical BST, excluding the original ordering, modulo 1,000,000,007.'],[([[2,1,3]],'Either child order follows root two, giving two total orders; excluding the original leaves one.'),([[3,4,5,1,2]],'Five other interleavings preserve the same left and right BSTs.')],[[x] for x in [[1],[1,2],[2,1,3],[3,4,5,1,2],[3,1,2,5,4],[1,2,3,4],[4,3,2,1],[3,2,1,4,5],[5,2,1,3,6,7],[4,2,6,1,3,5,7],[2,3,1],[5,1,2,3,4],[3,1,4,2],[6,3,1,2,5,4,7]]],REORDER,[REORDER.replace('comb(len(left)+len(right),len(left))','1'),REORDER.replace('(count(nums)-1)','count(nums)')],['Does not count interleavings of left- and right-subtree insertion orders.','Includes the original ordering instead of excluding it.'],reorder_o,rreorder,['The first value fixes the root; partition later values into left and right subsequences.','Recursively count orders preserving each subtree.','Interleave those subsequences in C(left+right,left) ways while retaining their internal orders.','Multiply these independent choices, then subtract the original full ordering.'],'O(n²)','O(n²)',8),
1573:S('equal_one_three_splits',[('s','str')],'int',['strings','combinatorics'],['Split the binary string into three non-empty consecutive parts.','Count splits giving every part the same number of ones, modulo 1,000,000,007.'],[(['10101'],'Choose either zero around each one-third boundary, producing four splits.'),(['0000'],'Any two of the three internal boundaries work, producing three splits.')],[[s] for s in ['000','0000','10101','111','1001','100100','010010','1','01','111000111','000000','1010101','110011','00100100']],SPLIT,[SPLIT.replace('if ones==0:return ((len(s)-1)*(len(s)-2)//2)','if ones==0:return len(s)-2'),SPLIT.replace('elif seen==2*each','elif seen>=2*each')],['Counts only adjacent boundary placements when there are no ones.','Counts positions beyond the second one-third boundary.'],split_o,rsplit,['If the total ones is not divisible by three, no split works.','With zero ones, choose any two internal boundaries.','Otherwise count boundary positions after the first third and before the final third; multiply the two choices.','Each valid split chooses exactly one position from each independent zero gap.'],'O(n)','O(1)',5),
1574:S('shortest_sorted_removal',[('arr','list[int]')],'int',['two-pointers','arrays'],['Remove one contiguous subarray, possibly empty.','Minimize its length so the remaining values are non-decreasing.'],[([[1,2,3,10,4,2,3,5]],'Removing 10,4,2 leaves 1,2,3,3,5, so length three is optimal.'),([[5,4,3,2,1]],'Only one element can remain from a strictly decreasing array, requiring removal of four.')],[[x] for x in [[1],[1,2,3],[3,2,1],[1,2,3,10,4,2,3,5],[5,4,3,2,1],[1,1,1],[1,2,5,3,4],[1,2,3,0],[10,1,2,3],[1,3,2,4],[2,2,1,2],[1,5,6,2,3,4,7],[1,2,2,0,2,2],[4,1,2,3,0,5]]],REMOVE,[REMOVE.replace('arr[right-1]<=arr[right]','arr[right-1]<arr[right]'),REMOVE.replace('right-left-1','right-left')],['Treats equal adjacent values as unsorted.','Includes one retained boundary element in the removal length.'],remove_o,rremove,['Find the longest non-decreasing suffix and use removing its prefix as an initial answer.','Advance through the non-decreasing prefix while moving the suffix pointer until its first value can follow the current prefix value.','The gap between those pointers is the removal length.','Every valid remainder consists of a prefix joined to a suffix, and the monotone pointer checks each possible prefix end optimally.'],'O(n)','O(1)',5),
1575:S('count_fueled_routes',[('locations','list[int]'),('start','int'),('finish','int'),('fuel','int')],'int',['recursion','dynamic-programming'],['City positions are distinct; moving between cities costs their absolute coordinate distance and revisits are allowed.','Count every route that stops at finish with nonnegative fuel, including the length-zero route when start equals finish.'],[([[2,3,6,8,4],1,3,5],'Four distinct valid routes reach city three within five fuel.'),([[4,3,1],1,0,6],'Five routes reach city zero because revisiting intermediate cities creates additional sequences.')],[[*x] for x in [([2,3,6,8,4],1,3,5),([4,3,1],1,0,6),([5,2,1],0,2,3),([1,2],0,1,0),([1,2],0,0,0),([1,3,5],0,2,4),([1,3,5],0,2,3),([0,5,10],1,1,10),([2,4,7],0,2,7),([10,1,6],2,0,4),([1,2,4],1,2,5),([3,8],0,1,10),([1,4,6,9],0,3,8),([2,5,8],2,0,12)]],ROUTES,[ROUTES.replace('answer=city==finish','answer=0'),ROUTES.replace('cost<=remaining','cost<remaining')],['Fails to count a route each time it arrives at the finish city.','Rejects moves that use exactly all remaining fuel.'],routes_o,rroutes,['Memoize by current city and remaining fuel.','Count one route immediately when the current city is finish, because stopping now is valid.','Try every other city whose travel cost fits and add its continuations.','Distinct positions make every move consume positive fuel, so the state graph is acyclic by remaining fuel.'],'O(cities²*fuel)','O(cities*fuel)',8),
1576:S('replace_questions_without_repeats',[('s','str')],'str',['strings','greedy'],['Replace every question mark while leaving other lowercase letters unchanged and avoiding equal adjacent characters.','For deterministic practice, return the lexicographically smallest valid result.'],[(['?zs'],'Choosing a is valid and lexicographically smallest, producing azs.'),(['ubv?w'],'The smallest choice different from v and w is a, producing ubvaw.')],[[s] for s in ['?','??','?zs','ubv?w','a?b','a?a','???','b??b','ab?','?a','a??c','z?z','?b?','ab??ba']],REPLACE,[REPLACE.replace("for choice in 'abc'","for choice in 'cba'"),REPLACE.replace('chars[index+1]!=choice','True')],['Chooses valid replacements in reverse lexical order.','Ignores the fixed character immediately to the right.'],replace_o,rreplace,['Only the left replacement and immediate right original character can constrain the current question mark.','Try a, b, then c and choose the first differing from both neighbors.','Three letters guarantee at least one choice.','Greedy lexical choice is safe because later positions depend only on the chosen current character and still retain at least two alternatives.'],'O(n)','O(n)',3),
1577:S('count_square_product_triplets',[('nums1','list[int]'),('nums2','list[int]')],'int',['hash-maps','math'],['Count triples where one squared value from either array equals the product of two values at distinct indices in the other array.','Occurrences at different indices count separately.'],[([[7,4],[5,2,8,9]],'Four squared equals two times eight, producing one valid triple.'),([[1,1],[1,1,1]],'Each squared one combines with every index pair in the opposite array, giving nine triples across both directions.')],[[a,b] for a,b in [([7,4],[5,2,8,9]),([1,1],[1,1,1]),([1],[1,1]),([2],[1,4]),([3],[1,9]),([2,2],[2,2]),([4],[2,8]),([5,10],[2,25,50]),([1,2,3],[1,4,9]),([6],[3,12,2]),([2,3],[4,1,9]),([10],[5,20,2]),([4,4],[8,2,2]),([7],[7,7])]],TRIPLETS,[TRIPLETS.replace('return answer//2','return answer'),TRIPLETS.replace('frequencies[other]-(factor==other)','frequencies[other]')],['Counts each unordered factor pair in both orders.','Allows the same index to supply both equal factors.'],triplets_o,rtriplets,['Count value frequencies in the array supplying factor pairs.','For each squared value, iterate distinct factor values that divide it and look up the complementary factor.','Subtract one occurrence when both factors are equal, then divide ordered selections by two.','Run the calculation in both array directions and add the results.'],'O((n+m)*distinct)','O(distinct)',5),
1578:S('minimum_colorful_rope_removal',[('colors','str'),('needed_time','list[int]')],'int',['greedy','strings'],['Remove balloons so adjacent remaining balloons never share a color.','Removing position i costs needed_time[i]; minimize total cost.'],[(['abaac',[1,2,3,4,5]],'Within the aa run, remove the cheaper cost-three balloon.'),(['abc',[1,2,3]],'No equal adjacent colors occur, so no removal is needed.')],[[c,t] for c,t in [('a',[5]),('abaac',[1,2,3,4,5]),('abc',[1,2,3]),('aa',[1,2]),('aa',[2,1]),('aaa',[1,2,3]),('aabaa',[1,2,3,4,1]),('bbbaaa',[3,1,2,5,4,6]),('abccba',[1,2,3,4,5,6]),('aaaa',[5,5,5,5]),('aabbbcc',[1,10,2,3,4,8,1]),('xyyx',[4,3,2,1]),('abba',[1,2,3,4]),('ccacc',[5,1,2,9,3])]],ROPE,[ROPE.replace('total-largest','total'),ROPE.replace('largest=max(largest,needed_time[end])','largest=min(largest,needed_time[end])')],['Removes every balloon in a repeated run, including the one that should remain.','Keeps the cheapest rather than the most expensive balloon in each run.'],rope_o,rrope,['Process each maximal run of one color.','At least all but one balloon in that run must be removed.','Keep the balloon with greatest removal cost and pay the run total minus that maximum.','Runs become separated by other colors, so their optimal choices are independent.'],'O(n)','O(1)',5),
1579:S('maximum_removable_traversal_edges',[('n','int'),('edges','list[list[int]]')],'int',['graphs','union-find'],['Type one edges serve Alice, type two serve Bob, and type three serve both; nodes are one-based.','Remove as many edges as possible while both users can traverse the entire graph, or return -1.'],[([4,[[3,1,2],[3,2,3],[1,1,3],[1,2,4],[1,1,2],[2,3,4]]],'Four edges suffice for both users, so two of the six can be removed.'),([4,[[3,2,3],[1,1,2],[2,3,4]]],'Neither user can connect all four nodes, so the answer is negative one.')],[[n,e] for n,e in [(2,[[3,1,2]]),(2,[[1,1,2],[2,1,2]]),(4,[[3,1,2],[3,2,3],[1,1,3],[1,2,4],[1,1,2],[2,3,4]]),(4,[[3,2,3],[1,1,2],[2,3,4]]),(3,[[3,1,2],[3,2,3],[1,1,3]]),(3,[[1,1,2],[1,2,3],[2,1,2],[2,2,3]]),(3,[[3,1,2],[1,2,3],[2,2,3]]),(4,[[3,1,2],[3,3,4],[1,2,3],[2,2,3]]),(2,[[3,1,2],[3,1,2]]),(5,[[3,1,2],[3,2,3],[3,3,4],[3,4,5]]),(3,[[1,1,2],[2,1,2]]),(4,[[3,1,2],[1,2,3],[1,3,4],[2,2,3],[2,3,4]]),(3,[[3,1,2],[3,1,3],[1,2,3],[2,2,3]]),(5,[[3,1,2],[3,2,3],[1,3,4],[1,4,5],[2,3,4],[2,4,5]])]],EDGES,[EDGES.replace('if kind==3:','if kind==0:'),EDGES.replace('used+=merged','used+=merged*2')],['Never processes shared type-three edges before private edges.','Counts a shared edge twice even though it is one physical edge.'],edges_o,redges,['Use separate disjoint-set structures for Alice and Bob.','Process shared edges first, unioning both graphs but counting one physical edge when it joins components.','Then add useful private edges to their respective graph.','A spanning structure uses the minimum useful edges; everything else is removable, and disconnected final DSUs make the task impossible.'],'O(edges*alpha(n))','O(n)',8),
1580:S('maximum_two_sided_warehouse_boxes',[('boxes','list[int]'),('warehouse','list[int]')],'int',['sorting','greedy'],['Boxes may enter from either end and cannot pass through a lower room on that route.','Rearrange boxes and place at most one per room to maximize the count.'],[([[1,2,2,3,4],[3,4,1,2]],'Using both entrances allows four boxes to occupy all rooms.'),([[3,5,5,2],[2,1,3,4,5]],'The central height-one bottleneck and entrance limits allow three boxes.')],[[b,w] for b,w in [([1],[1]),([2],[1]),([1,2,2,3,4],[3,4,1,2]),([3,5,5,2],[2,1,3,4,5]),([1,2,3],[3,3,3]),([4,5],[3,10]),([2,2],[2,2]),([5,1,2],[4,4]),([1,1,1],[1,1]),([3,4,5],[5,4,3]),([10],[100,1]),([2,8,4],[9,3,5]),([6,5,4,3],[7,6,2,8]),([1,10,2,9],[3,3,3,3])]],BOXES,[BOXES.replace('max(min(warehouse[:index+1]),min(warehouse[index:]))','min(warehouse[:index+1])'),BOXES.replace('capacities.sort()','capacities.sort(reverse=True)')],['Considers entry from the left only instead of the better of both entrances.','Matches shortest boxes against largest capacities first and wastes constrained rooms.'],boxes_o,rboxes,['A room’s left-entry capacity is the minimum height from the left through that room; its right-entry capacity is the analogous suffix minimum.','Take the larger of those two capacities because the box may use either entrance.','Sort capacities and boxes, then match the shortest remaining box to each room from smallest capacity upward.','Greedy matching preserves taller boxes and larger rooms for later, maximizing cardinality.'],'O((boxes+rooms) log n)','O(rooms)',5),
}
