"""Second half of batch 98: DAGs, grid cycles, interval groups, and game DP."""
from functools import lru_cache
from itertools import combinations,permutations
from .import_batch_055 import entry
MOD=1_000_000_007
def vertices_o(a):
 n,edges=a;reachable={y for _,y in edges};return [node for node in range(n) if node not in reachable]
def calls_o(a):
 nums=a[0];calls=0
 while any(nums):
  odds=sum(value%2 for value in nums);calls+=odds
  if odds:nums=[value-(value%2) for value in nums]
  else:nums=[value//2 for value in nums];calls+=1
 return calls
def cycle_o(a):
 grid=a[0];rows,cols=len(grid),len(grid[0]);seen=set()
 for start_r in range(rows):
  for start_c in range(cols):
   if (start_r,start_c) in seen:continue
   stack=[(start_r,start_c)];seen.add((start_r,start_c));vertices=edges=0
   while stack:
    row,col=stack.pop();vertices+=1
    for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
     nr,nc=row+dr,col+dc
     if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]==grid[row][col]:
      edges+=1
      if (nr,nc) not in seen:seen.add((nr,nc));stack.append((nr,nc))
   if edges//2>=vertices:return True
 return False
def sectors_o(a):
 n,rounds=a;count=[0]*(n+1);position=rounds[0];count[position]+=1
 for end in rounds[1:]:
  while position!=end:position=position%n+1;count[position]+=1
 best=max(count);return [i for i in range(1,n+1) if count[i]==best]
def coins_o(a):
 @lru_cache(None)
 def solve(values):
  if not values:return 0
  return max(sorted((values[i],values[j],values[k]))[1]+solve(tuple(v for x,v in enumerate(values) if x not in (i,j,k))) for i,j,k in combinations(range(len(values)),3))
 return solve(tuple(a[0]))
def group_o(a):
 arr,m=a;bits=[0]*len(arr);answer=-1
 for step,position in enumerate(arr,1):
  bits[position-1]=1;index=0
  while index<len(bits):
   if not bits[index]:index+=1;continue
   end=index
   while end<len(bits) and bits[end]:end+=1
   if end-index==m:answer=step;break
   index=end
 return answer
def stone_o(a):
 values=tuple(a[0])
 @lru_cache(None)
 def play(state):
  if len(state)==1:return 0
  best=0
  for cut in range(1,len(state)):
   left,right=state[:cut],state[cut:];x,y=sum(left),sum(right)
   if x<=y:best=max(best,x+play(left))
   if y<=x:best=max(best,y+play(right))
  return best
 return play(values)
def boxes_o(a):
 boxes,warehouse=a;best=0;effective=[];height=10**9
 for room in warehouse:height=min(height,room);effective.append(height)
 for size in range(1,min(len(boxes),len(warehouse))+1):
  for selected in combinations(range(len(boxes)),size):
   for rooms in combinations(range(len(warehouse)),size):
    if any(all(boxes[box]<=effective[room] for box,room in zip(order,rooms)) for order in permutations(selected)):best=size
 return best
def pattern_o(a):
 arr,m,k=a;return any(all(arr[start+offset]==arr[start+offset%m] for offset in range(m*k)) for start in range(len(arr)-m*k+1))
def positive_o(a):
 nums=a[0];best=0
 for i in range(len(nums)):
  product=1
  for j in range(i,len(nums)):product*=nums[j];best=max(best,j-i+1 if product>0 else 0)
 return best
def rvertices(r):
 n=r.randint(1,15);edges=[]
 for x in range(n):
  for y in range(x+1,n):
   if r.random()<.15:edges.append([x,y])
 return [n,edges]
def rcalls(r):return [[r.randint(0,31) for _ in range(r.randint(1,8))]]
def rcycle(r):
 rows,cols=r.randint(1,6),r.randint(1,6);return [[[r.choice('abc') for _ in range(cols)] for _ in range(rows)]]
def rsectors(r):
 n=r.randint(2,12);return [n,[r.randint(1,n) for _ in range(r.randint(2,10))]]
def rcoins(r):
 n=r.randint(1,3);return [[r.randint(1,30) for _ in range(3*n)]]
def rgroup(r):
 n=r.randint(1,15);arr=list(range(1,n+1));r.shuffle(arr);return [arr,r.randint(1,n)]
def rstone(r):return [[r.randint(1,12) for _ in range(r.randint(1,9))]]
def rboxes(r):return [[r.randint(1,10) for _ in range(r.randint(1,7))],[r.randint(1,10) for _ in range(r.randint(1,7))]]
def rpattern(r):return [[r.randint(1,5) for _ in range(r.randint(1,30))],r.randint(1,6),r.randint(2,5)]
def rpositive(r):return [[r.randint(-5,5) for _ in range(r.randint(1,40))]]
VERTICES='''def minimum_start_vertices(n, edges):
 incoming=[False]*n
 for source,target in edges:incoming[target]=True
 return [node for node in range(n) if not incoming[node]]
'''
CALLS='''def minimum_target_array_calls(nums):
 increments=sum(value.bit_count() for value in nums)
 doublings=max((value.bit_length() for value in nums),default=0)-1
 return increments+max(0,doublings)
'''
CYCLE='''def contains_same_character_cycle(grid):
 rows,cols=len(grid),len(grid[0]);seen=set()
 def visit(row,col,parent):
  seen.add((row,col))
  for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
   neighbor=(row+dr,col+dc)
   if not (0<=neighbor[0]<rows and 0<=neighbor[1]<cols) or grid[neighbor[0]][neighbor[1]]!=grid[row][col] or neighbor==parent:continue
   if neighbor in seen or visit(*neighbor,(row,col)):return True
  return False
 for row in range(rows):
  for col in range(cols):
   if (row,col) not in seen and visit(row,col,None):return True
 return False
'''
SECTORS='''def most_visited_track_sectors(n, rounds):
 start,end=rounds[0],rounds[-1]
 if start<=end:return list(range(start,end+1))
 return list(range(1,end+1))+list(range(start,n+1))
'''
COINS='''def maximum_coin_piles(piles):
 piles=sorted(piles);answer=0;right=len(piles)-1
 for _ in range(len(piles)//3):
  right-=1;answer+=piles[right];right-=1
 return answer
'''
GROUP='''def latest_exact_one_group(arr, m):
 n=len(arr)
 if m==n:return n
 length=[0]*(n+2);groups=0;answer=-1
 for step,position in enumerate(arr,1):
  left,right=length[position-1],length[position+1]
  if left==m:groups-=1
  if right==m:groups-=1
  merged=left+1+right;length[position-left]=length[position+right]=merged
  if merged==m:groups+=1
  if groups:answer=step
 return answer
'''
STONE='''def maximum_stone_game_five_score(stone_value):
 from functools import lru_cache
 prefix=[0]
 for value in stone_value:prefix.append(prefix[-1]+value)
 @lru_cache(None)
 def play(left,right):
  if right-left==1:return 0
  best=0
  for cut in range(left+1,right):
   x=prefix[cut]-prefix[left];y=prefix[right]-prefix[cut]
   if x<=y:best=max(best,x+play(left,cut))
   if y<=x:best=max(best,y+play(cut,right))
  return best
 return play(0,len(stone_value))
'''
BOXES='''def maximum_warehouse_boxes(boxes, warehouse):
 boxes=sorted(boxes);effective=[];height=float('inf')
 for room in warehouse:height=min(height,room);effective.append(height)
 box=answer=0
 for room in reversed(effective):
  if box<len(boxes) and boxes[box]<=room:answer+=1;box+=1
 return answer
'''
PATTERN='''def contains_repeated_pattern(arr, m, k):
 needed=m*(k-1);matched=0
 for index in range(m,len(arr)):
  if arr[index]==arr[index-m]:
   matched+=1
   if matched==needed:return True
  else:matched=0
 return False
'''
POSITIVE='''def longest_positive_product_subarray(nums):
 positive=negative=answer=0
 for value in nums:
  if value==0:positive=negative=0
  elif value>0:positive+=1;negative=negative+1 if negative else 0
  else:positive,negative=(negative+1 if negative else 0),positive+1
  answer=max(answer,positive)
 return answer
'''
E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1557:S('minimum_start_vertices',[('n','int'),('edges','list[list[int]]')],'list[int]',['graphs','directed-acyclic-graphs'],['Nodes are zero through n-1 and edges form a DAG.','Return the unique minimum set of starting nodes from which every node is reachable; order does not matter.'],[([6,[[0,1],[0,2],[2,5],[3,4],[4,2]]],'Only nodes zero and three have no incoming edge, so both are necessary and together reach all nodes.'),([5,[[0,1],[2,1],[3,1],[1,4],[2,4]]],'Zero, two, and three have indegree zero and form the minimum source set.')],[[n,e] for n,e in [(1,[]),(2,[]),(2,[[0,1]]),(6,[[0,1],[0,2],[2,5],[3,4],[4,2]]),(5,[[0,1],[2,1],[3,1],[1,4],[2,4]]),(4,[[0,1],[1,2],[2,3]]),(4,[[0,2],[1,2]]),(5,[[0,1],[0,2],[0,3],[0,4]]),(5,[]),(6,[[0,3],[1,3],[2,4],[4,5]]),(3,[[0,1],[0,2]]),(7,[[0,1],[2,3],[4,5],[5,6]]),(4,[[1,2],[2,3]]),(8,[[0,2],[1,2],[2,4],[3,4],[5,6]])]],VERTICES,[VERTICES.replace('incoming[target]=True','incoming[source]=True'),VERTICES.replace('not incoming[node]','incoming[node]')],['Marks edge sources rather than targets as having incoming edges.','Returns non-source nodes instead of the required sources.'],vertices_o,rvertices,['Every indegree-zero node is unreachable from any other node, so each must be selected.','Every positive-indegree node has a predecessor.','Following predecessors in a finite DAG eventually reaches an indegree-zero source.','Therefore exactly the indegree-zero nodes are necessary and sufficient.'],'O(n+edges)','O(n)',5),
1558:S('minimum_target_array_calls',[('nums','list[int]')],'int',['bit-manipulation','greedy'],['Start with an all-zero array; one call increments any single element by one, and another doubles every element.','Return the minimum calls needed to construct nums.'],[([[1,5]],'Three one-bit increments and two global doublings construct one and five in five calls.'),([[2,2]],'Increment both positions once, then double the whole array, for three calls.')],[[x] for x in [[0],[1],[1,5],[2,2],[0,0],[3],[4],[7,7],[1,2,4],[8,1],[15,0],[16,31],[5,10,20],[0,3,6]]],CALLS,[CALLS.replace('sum(value.bit_count() for value in nums)','sum(nums)'),CALLS.replace('-1','')],['Counts every final unit as a separate increment.','Charges one extra global doubling.'],calls_o,rcalls,['Read each target in binary.','Each one bit requires one individual increment at the bit position where it is introduced.','All numbers share the global doublings, whose count is one less than the largest bit length.','Reversing the process forces removal of odd units before every simultaneous halving, proving optimality.'],'O(n)','O(1)',5),
1559:S('contains_same_character_cycle',[('grid','list[list[str]]')],'bool',['recursion','grids'],['Move orthogonally between cells containing the same character.','Return whether a path of at least four distinct cells can return to its start without immediately reversing an edge.'],[([[['a','a','a','a'],['a','b','b','a'],['a','b','b','a'],['a','a','a','a']]],'The outer ring of a cells forms a cycle.'),([[['c','c','d'],['c','d','d'],['e','f','d']]],'Each same-letter component is acyclic.')],[[g] for g in [[['a']],[['a','a']],[['a','a'],['a','a']],[['a','a','a','a'],['a','b','b','a'],['a','b','b','a'],['a','a','a','a']],[['c','c','d'],['c','d','d'],['e','f','d']],[['a','b'],['b','a']],[['a','a','a'],['a','b','a'],['a','a','a']],[['a','b','b'],['a','b','b']],[['x','x','y'],['z','x','y'],['z','z','y']],[['a','a','b'],['b','a','b'],['b','a','a']],[['a','b','c'],['d','e','f']],[['q','q','q','q']],[['a'],['a'],['a'],['a']],[['a','a','b','b'],['a','a','b','b']]]],CYCLE,[CYCLE.replace('neighbor==parent','False'),CYCLE.replace('if neighbor in seen or visit(*neighbor,(row,col)):return True','if False:return True')],['Treats the immediate parent edge as a two-cell cycle.','Traverses components but never reports a closing edge.'],cycle_o,rcycle,['Run DFS within each same-character component.','Pass the immediately previous cell so its undirected edge is ignored.','Encountering any other already visited same-character neighbor proves a cycle.','A simple orthogonal grid has no triangles, so every such undirected cycle has at least four cells.'],'O(rows*cols)','O(rows*cols)',5),
1560:S('most_visited_track_sectors',[('n','int'),('rounds','list[int]')],'list[int]',['arrays','simulation'],['Move from each listed sector to the next by increasing labels and wrap n to one.','Return every most-visited sector in increasing numeric order.'],[([4,[1,3,1,2]],'After complete laps cancel equally, sectors one and two lie on the final partial traversal and are visited most.'),([2,[2,1,2,1,2,1,2,1,2]],'Sector two is visited once more than sector one.')],[[n,r] for n,r in [(2,[1,2]),(4,[1,3,1,2]),(2,[2,1,2,1,2,1,2,1,2]),(7,[1,3,5,7]),(4,[4,1]),(5,[3,3]),(6,[5,2]),(3,[2,1]),(8,[1,8]),(5,[5,4,3,2,1]),(10,[7,2,7]),(3,[1,2,3,1]),(9,[9,1]),(6,[4,6,2,4])]],SECTORS,[SECTORS.replace('start,end=rounds[0],rounds[-1]','start,end=rounds[-1],rounds[0]'),SECTORS.replace('range(start,end+1)','range(start+1,end+1)')],['Reverses the traversal endpoints.','Omits the starting sector from the maximum set.'],sectors_o,rsectors,['Every complete lap visits all sectors equally and cannot affect which sectors tie for maximum.','Only the path from the first listed sector to the final listed sector receives one extra visit.','List that inclusive interval, splitting at the wrap when start>end.','Concatenating low labels before high labels returns the result in ascending order.'],'O(n)','O(n)',3),
1561:S('maximum_coin_piles',[('piles','list[int]')],'int',['sorting','greedy'],['The number of piles is a multiple of three; from each chosen triple Alice takes the largest, you take the next largest, and Bob takes the remaining pile.','Rearrange triples to maximize your total.'],[([[2,4,1,2,7,8]],'Pairing the largest piles lets you take seven and two, totaling nine.'),([[2,4,5]],'Alice takes five, you take four, and Bob takes two.')],[[x] for x in [[1,2,3],[2,4,5],[2,4,1,2,7,8],[9,8,7,6,5,1],[1,1,1],[1,2,2,3,3,4],[10,10,10,1,1,1],[1,2,3,4,5,6,7,8,9],[5,5,4,4,3,3],[100,1,99],[2,2,2,2,2,2],[1,10,11,12,13,14],[7,6,5],[3,8,9,1,2,7]]],COINS,[COINS.replace('right-=1;answer+=piles[right]','answer+=piles[right]'),COINS.replace('piles=sorted(piles)','piles=sorted(piles,reverse=True)')],['Lets you take Alice’s largest pile from each triple.','Reverses sorting while retaining indices designed for ascending order.'],coins_o,rcoins,['Sort all piles.','For each round, discard the current largest pile to Alice, take the next largest, and reserve the globally smallest piles for Bob.','Repeat for one third of the pile count.','Any larger pile given to Bob can be exchanged with a smaller unused pile without hurting Alice’s dominance and only improving your options.'],'O(n log n)','O(n)',5),
1562:S('latest_exact_one_group',[('arr','list[int]'),('m','int')],'int',['arrays','intervals'],['arr is a permutation of positions one through n, activated in order.','Return the latest one-based step containing at least one maximal consecutive-one group of exactly length m, or -1.'],[([[3,5,1,2,4],1],'At step four, position five remains an isolated one; the final step merges everything into length five.'),([[3,1,5,4,2],2],'No step contains a maximal group of exactly two ones.')],[[a,m] for a,m in [([1],1),([3,5,1,2,4],1),([3,1,5,4,2],2),([1,2],1),([2,1],1),([1,2,3],3),([1,2,3],2),([2,1,4,3],2),([4,3,2,1],1),([2,4,1,3,5],2),([5,1,2,3,4],1),([1,3,5,2,4],1),([2,3,1,5,4],3),([3,2,1,4,5],2)]],GROUP,[GROUP.replace('if left==m:groups-=1',''),GROUP.replace('if groups:answer=step','if merged==m:answer=step')],['Fails to remove a left group when it merges into a larger group.','Records only newly created size-m groups and forgets existing groups elsewhere.'],group_o,rgroup,['Track the lengths at both endpoints of every active group.','When a position activates, remove neighboring groups of size m from the count, merge their lengths, and add the merged group if its size is m.','Record each step where the count remains positive.','Endpoint lengths are sufficient because only groups adjacent to the new position can change.'],'O(n)','O(n)',5),
1563:S('maximum_stone_game_five_score',[('stone_value','list[int]')],'int',['dynamic-programming','recursion'],['Split the current row into two non-empty parts; the higher-sum part is discarded and the lower sum is scored.','On equal sums, choose which part remains; maximize the final accumulated score.'],[([[6,2,3,4,5,5]],'Optimal recursive splits produce a total score of eighteen.'),([[7,7,7,7,7,7,7]],'Balanced choices across equal-valued stones yield score twenty-eight.')],[[x] for x in [[1],[1,2],[6,2,3,4,5,5],[7,7,7,7,7,7,7],[4,5,5,4],[1,1,1],[10,1,1],[1,2,3,4],[5,3,1,4,2],[2,2,3,3],[9,8,7,6,5],[1,10,1,10,1],[3,1,3,1,3],[2,8,6,4,2]]],STONE,[STONE.replace('return play(0,len(stone_value))','return play(0,len(stone_value))//2'),STONE.replace('best=max(best,x+play(left,cut))','best=max(best,x)')],['Returns only half of the achievable optimal score.','Stops the game after scoring a left part instead of recursing into it.'],stone_o,rstone,['Use prefix sums for interval totals and memoize the best score for each interval.','Try every split and add the smaller side’s sum to the optimal continuation on that side.','When sums tie, consider continuing on either side.','Every play sequence begins with exactly one split, so maximizing these complete continuations yields optimal play.'],'O(n³)','O(n²)',8),
1564:S('maximum_warehouse_boxes',[('boxes','list[int]'),('warehouse','list[int]')],'int',['sorting','greedy'],['Boxes enter only from the warehouse’s left and cannot pass through a lower earlier room.','Rearrange boxes and place at most one per room to maximize the number stored.'],[([[4,3,4,1],[5,3,3,4,1]],'Effective room heights are 5,3,3,3,1; boxes 1,3,4 can be placed, for three total.'),([[1,2,2,3,4],[3,4,1,2]],'The height-one bottleneck prevents later rooms from accepting remaining boxes, so three fit.')],[[b,w] for b,w in [([1],[1]),([2],[1]),([4,3,4,1],[5,3,3,4,1]),([1,2,2,3,4],[3,4,1,2]),([1,2,3],[3,3,3]),([4,5],[10,3]),([2,2],[2,2]),([5,1,2],[4,4]),([1,1,1],[1,1]),([3,4,5],[5,4,3]),([10],[100,1]),([2,8,4],[9,3,5]),([6,5,4,3],[7,6,2,8]),([1,10,2,9],[3,3,3,3])]],BOXES,[BOXES.replace('height=min(height,room)','height=room'),BOXES.replace('reversed(effective)','effective')],['Ignores bottlenecks in earlier rooms.','Fills rooms from the entrance instead of using deepest constrained rooms first.'],boxes_o,rboxes,['Replace each room height by the minimum height along the entrance path.','Sort boxes from shortest to tallest.','Scan effective rooms from deepest to nearest and place the shortest remaining box whenever it fits.','Using the shortest fitting box preserves every taller box option, and deepest-first prevents wasting accessible constrained rooms.'],'O((boxes+rooms) log boxes)','O(rooms)',5),
1566:S('contains_repeated_pattern',[('arr','list[int]'),('m','int'),('k','int')],'bool',['arrays','patterns'],['Find a length-m block repeated k times consecutively without gaps or overlap.','Return whether any such starting position exists.'],[([[1,2,4,4,4,4],1,3],'The value four repeats in at least three consecutive length-one blocks.'),([[1,2,1,2,1,1,1,3],2,2],'No length-two block repeats twice consecutively.')],[[a,m,k] for a,m,k in [([1,1],1,2),([1,2,4,4,4,4],1,3),([1,2,1,2,1,1,1,3],2,2),([1,2,1,2],2,2),([1,2,3],1,2),([5,5,5,5],2,2),([1,2,3,1,2,3],3,2),([1],1,2),([1,1,2,2],1,2),([3,4,3,4,3,4],2,3),([1,2,1,2,1],2,2),([7,7,7],1,3),([1,2,3,1,2],3,2),([2,3,2,3,4,2,3],2,2)]],PATTERN,[PATTERN.replace('needed=m*(k-1)','needed=m*k'),PATTERN.replace('arr[index]==arr[index-m]','arr[index]==arr[index-1]')],['Requires one extra full repeated block.','Compares adjacent values instead of positions one pattern length apart.'],pattern_o,rpattern,['Compare each value with the value m positions earlier.','Count the consecutive successful comparisons.','Repeating a block k times creates exactly m*(k-1) such comparisons.','Reset on mismatch; reaching the threshold proves one uninterrupted repeated region.'],'O(n)','O(1)',3),
1567:S('longest_positive_product_subarray',[('nums','list[int]')],'int',['dynamic-programming','arrays'],['Return the greatest length of a contiguous subarray whose product is positive.','Zero breaks a candidate subarray; values may be negative.'],[([[1,-2,-3,4]],'Two negatives make the full four-value product positive.'),([[0,1,-2,-3,-4]],'The longest positive-product subarray has length three.')],[[x] for x in [[1],[-1],[0],[1,-2,-3,4],[0,1,-2,-3,-4],[-1,-2],[-1,-2,-3],[1,2,3],[0,0],[-1,0,-2,-3],[2,-5,-2,-4,3],[1,-1,1,-1],[5,0,-1,-1,2],[-2,3,-4,0,-1]]],POSITIVE,[POSITIVE.replace('positive,negative=(negative+1 if negative else 0),positive+1','positive,negative=0,positive+1'),POSITIVE.replace('if value==0:positive=negative=0','if value==0:positive=negative=1')],['After a negative value, discards a prior negative suffix that should become positive.','Treats zero as a positive-product subarray of length one.'],positive_o,rpositive,['Track longest positive-product and negative-product suffix lengths.','A positive value extends both; a negative value swaps their roles while extending; zero resets both.','Update the answer from the positive suffix.','Sign and length are the only suffix properties relevant to extending at the next element.'],'O(n)','O(1)',5),
}
BATCH[1557]['comparator']='unordered'
