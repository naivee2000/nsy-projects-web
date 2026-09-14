"""Second group of batch 103: greedy, components, counting, BFS, and prefixes."""
from collections import Counter,deque
from functools import lru_cache
from .import_batch_055 import entry

def removal_o(a):
 s,x,y=a
 @lru_cache(None)
 def solve(text):
  best=0
  for i in range(len(text)-1):
   pair=text[i:i+2]
   if pair=='ab':best=max(best,x+solve(text[:i]+text[i+2:]))
   if pair=='ba':best=max(best,y+solve(text[:i]+text[i+2:]))
  return best
 return solve(s)
def hamming_o(a):
 source,target,swaps=a;n=len(source);graph=[[] for _ in range(n)]
 for x,y in swaps:graph[x].append(y);graph[y].append(x)
 answer=0;seen=set()
 for start in range(n):
  if start in seen:continue
  stack=[start];seen.add(start);indices=[]
  while stack:
   node=stack.pop();indices.append(node)
   for nxt in graph[node]:
    if nxt not in seen:seen.add(nxt);stack.append(nxt)
  counts=Counter(source[i] for i in indices)
  for i in indices:
   if counts[target[i]]:counts[target[i]]-=1
   else:answer+=1
 return answer
def tuples_o(a):
 nums=a[0];groups=Counter(nums[i]*nums[j] for i in range(len(nums)) for j in range(i+1,len(nums)))
 return sum(count*(count-1)//2*8 for count in groups.values())
def food_o(a):
 grid=a[0];rows=len(grid);cols=len(grid[0]);start=next((r,c) for r in range(rows) for c in range(cols) if grid[r][c]=='*');queue=deque([(start[0],start[1],0)]);seen={start}
 while queue:
  r,c,d=queue.popleft()
  for nr,nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
   if 0<=nr<rows and 0<=nc<cols and (nr,nc) not in seen and grid[nr][nc]!='X':
    if grid[nr][nc]=='#':return d+1
    seen.add((nr,nc));queue.append((nr,nc,d+1))
 return -1
def altitude_o(a):
 current=best=0
 for gain in a[0]:current+=gain;best=max(best,current)
 return best

def rremoval(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,9))),r.randint(1,10),r.randint(1,10)]
def rhamming(r):
 n=r.randint(1,14);source=[r.randrange(6) for _ in range(n)];target=[r.randrange(6) for _ in range(n)];swaps=[[i,j] for i in range(n) for j in range(i+1,n) if r.random()<.12];return [source,target,swaps]
def rtuples(r):return [r.sample(range(1,35),r.randint(4,10))]
def rfood(r):
 rows,cols=r.randint(2,7),r.randint(2,7);cells=[['O' if r.random()>.25 else 'X' for _ in range(cols)] for _ in range(rows)];start,food=r.sample(range(rows*cols),2);cells[start//cols][start%cols]='*';cells[food//cols][food%cols]='#';return [cells]
def raltitude(r):return [[r.randint(-20,20) for _ in range(r.randint(1,30))]]

REMOVAL='''def maximum_removal_score(s, x, y):
 def remove(text,pair,score):
  stack=[];earned=0
  for char in text:
   if stack and stack[-1]+char==pair:stack.pop();earned+=score
   else:stack.append(char)
  return ''.join(stack),earned
 if x<y:s,first=remove(s,'ba',y);s,second=remove(s,'ab',x)
 else:s,first=remove(s,'ab',x);s,second=remove(s,'ba',y)
 return first+second
'''
HAMMING='''def minimum_hamming_after_swaps(source, target, allowed_swaps):
 from collections import Counter
 parent=list(range(len(source)))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for left,right in allowed_swaps:parent[find(left)]=find(right)
 available={}
 for index,value in enumerate(source):available.setdefault(find(index),Counter())[value]+=1
 answer=0
 for index,value in enumerate(target):
  counts=available[find(index)]
  if counts[value]:counts[value]-=1
  else:answer+=1
 return answer
'''
TUPLES='''def equal_product_tuple_count(nums):
 from collections import Counter
 products=Counter();answer=0
 for i in range(len(nums)):
  for j in range(i):
   product=nums[i]*nums[j];answer+=8*products[product];products[product]+=1
 return answer
'''
FOOD='''def shortest_path_to_food(grid):
 from collections import deque
 rows,cols=len(grid),len(grid[0]);start=next((r,c) for r in range(rows) for c in range(cols) if grid[r][c]=='*');queue=deque([(start[0],start[1],0)]);seen={start}
 while queue:
  row,col,distance=queue.popleft()
  for nr,nc in ((row+1,col),(row-1,col),(row,col+1),(row,col-1)):
   if 0<=nr<rows and 0<=nc<cols and (nr,nc) not in seen and grid[nr][nc]!='X':
    if grid[nr][nc]=='#':return distance+1
    seen.add((nr,nc));queue.append((nr,nc,distance+1))
 return -1
'''
ALTITUDE='''def highest_route_altitude(gain):
 altitude=highest=0
 for change in gain:altitude+=change;highest=max(highest,altitude)
 return highest
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1717:E('maximum_removal_score',[('s','str'),('x','int'),('y','int')],'int',['strings','greedy','stacks'],['Removing substring ab earns x points and removing ba earns y points; removals close the remaining characters together.','Return the maximum total after any sequence of removals.'],[(['cdbcbbaaabab',4,5],'Removing the higher-valued ba pairs first and then ab pairs earns nineteen.'),(['aabbaaxybbaabb',5,4],'Prioritizing ab earns twenty points across the independent letter blocks.')],[[*x] for x in [('cdbcbbaaabab',4,5),('aabbaaxybbaabb',5,4),('a',1,2),('ab',3,9),('ba',3,9),('abba',5,4),('abba',4,5),('abab',2,2),('baba',7,1),('cabac',10,1),('aaaa',5,6),('bbabb',3,8),('abcba',4,9),('baababb',6,3)]],REMOVAL,[REMOVAL.replace("if x<y","if x>y"),REMOVAL.replace("stack[-1]+char==pair","char+stack[-1]==pair")],['Prioritizes the lower-valued pair, which can destroy a more valuable overlapping removal.','Tests the pair in reversed character order inside both passes.'],removal_o,rremoval,L('Only runs over a and b interact; when pairs overlap, the higher-valued orientation should be removed first.','Use a stack pass for the higher score, then another for the lower score.','Pop when stack top plus current character equals the active pair; retain all other characters.','An exchange argument moves every available higher-valued overlapping removal before a lower one without reducing the number of later removals.'),'O(n)','O(n)',5),
1722:E('minimum_hamming_after_swaps',[('source','list[int]'),('target','list[int]'),('allowed_swaps','list[list[int]]')],'int',['graphs','union-find','counting'],['Any allowed index swap may be repeated, so values can be permuted anywhere inside a connected index component.','Return the minimum number of positions whose source and target values differ.'],[([[1,2,3,4],[2,1,4,5],[[0,1],[2,3]]],'The first component can match both values; the second still has one unmatched target value, so the answer is one.'),([[1,2,3,4],[1,3,2,4],[]],'Without allowed swaps, positions one and two remain mismatched.')],[[*x] for x in [([1,2,3,4],[2,1,4,5],[[0,1],[2,3]]),([1,2,3,4],[1,3,2,4],[]),([1],[1],[]),([1],[2],[]),([1,2],[2,1],[[0,1]]),([1,2],[2,1],[]),([1,1,2],[1,2,1],[[0,1],[1,2]]),([1,2,3],[3,2,1],[[0,1]]),([1,2,3,4],[4,3,2,1],[[0,1],[1,2],[2,3]]),([0,0,1],[1,0,0],[[0,2]]),([5,6,7],[7,5,6],[[0,1],[1,2]]),([1,2,1,2],[2,1,2,1],[[0,2],[1,3]]),([9,8,7,6],[9,7,8,6],[[1,2]]),([1,2,3,4,5],[2,1,5,4,3],[[0,1],[2,3]])]],HAMMING,[HAMMING.replace('for left,right in allowed_swaps:','for left,right in allowed_swaps[:1]:'),HAMMING.replace('counts[value]-=1','counts[value]=0')],['Uses only the first allowed edge and misses larger connected components.','Consumes all copies of a matched value at once, mishandling duplicates.'],hamming_o,rhamming,L('Repeated swaps make every connected component freely permutable.','Build components and compare the source and target multisets within each one.','Count source values per root; for each target value consume a matching count or add one mismatch.','All matched component values can be routed by swaps; every unmatched target occurrence necessarily contributes one Hamming difference.'),'O((n+swaps) alpha(n))','O(n)',5),
1726:E('equal_product_tuple_count',[('nums','list[int]')],'int',['arrays','hash-maps','counting'],['nums contains distinct positive integers.','Count ordered tuples (a,b,c,d) using four distinct array values with a*b == c*d.'],[([[2,3,4,6]],'The pair products 2*6 and 3*4 match, producing eight orderings.'),([[1,2,4,5,10]],'Two shared-product pairings produce sixteen ordered tuples.')],[[x] for x in [[2,3,4,6],[1,2,4,5,10],[1,2,3,4],[1,3,9,27],[2,4,8,16],[1,2,6,12],[3,5,6,10],[1,4,5,20],[2,3,5,7],[1,2,3,6,9,18],[4,6,8,12],[2,7,14,49],[1,5,10,25,50],[2,3,4,6,8,12]]],TUPLES,[TUPLES.replace('8*products[product]','4*products[product]'),TUPLES.replace('products[product]+=1','products[product]=1')],['Counts only half of the eight valid orderings for each pair-of-pairs.','Stores product presence rather than the number of prior pairs.'],tuples_o,rtuples,L('Each two unordered pairs with the same product use four distinct values because nums is distinct.','Count earlier pairs by product while enumerating each new pair.','A new pair forms products[product] pair-of-pairs, each contributing 2*2*2=8 ordered tuples.','The three factors of two choose pair order and the order within each pair, covering every valid tuple exactly once.'),'O(n^2)','O(n^2)',5),
1730:E('shortest_path_to_food',[('grid','list[list[str]]')],'int',['matrices','graphs','breadth-first-search'],['Grid characters are * for the single start, # for food, O for open cells, and X for blocked cells.','Move four-directionally and return the fewest steps to any food cell, or -1 if unreachable.'],[([[list(row) for row in ['XXXXXX','X*OOOX','XOO#OX','XXXXXX']]],'The nearest food is three moves from the start.'),([[list(row) for row in ['*O','X#']]],'Move right then down in two steps.')],[[[list(row) for row in g]] for g in [['*#'],['*O#'],['*X#'],['*O','X#'],['XXXXXX','X*OOOX','XOO#OX','XXXXXX'],['*OO','XXX','OO#'],['*OO','OXO','OO#'],['#O*'],['#X','O*'],['OO#','O*O','OOO'],['*XOO','OXO#','OOOO'],['*OOO','XXXX','OOO#'],['OX#','O*O','OO#'],['*OOOO','XXXXO','###OO']]],FOOD,[FOOD.replace('queue.popleft()','queue.pop()'),FOOD.replace("grid[nr][nc]!='X'","grid[nr][nc]=='O'")],['Uses depth-first order, which may return a non-shortest food path.','Allows only open cells and therefore never steps onto a food cell.'],food_o,rfood,L('All moves have equal cost, so breadth-first search discovers cells in nondecreasing distance.','Start a queue at * and expand unseen, nonblocked four-neighbors.','Return distance+1 when a neighbor is #; enqueue O cells; return -1 if the queue empties.','The first discovered food has the minimum possible number of edges by the BFS layer invariant.'),'O(rows*columns)','O(rows*columns)',5),
1732:E('highest_route_altitude',[('gain','list[int]')],'int',['arrays','prefix-sums'],['A biker starts at altitude zero; gain[i] is the signed altitude change to the next point.','Return the highest altitude among the starting point and every reached point.'],[([[-5,1,5,0,-7]],'The altitudes are 0,-5,-4,1,1,-6, so the highest is one.'),([[-4,-3,-2,-1,4,3,2]],'Every reached altitude is below zero, making the starting altitude zero the maximum.')],[[x] for x in [[],[1],[-1],[0],[-5,1,5,0,-7],[-4,-3,-2,-1,4,3,2],[1,2,3],[-1,-2,-3],[5,-10,10],[-2,5,-1],[0,0,0],[10,-1,-1,-1],[-10,20,-5],[-1,1,-1,1]]],ALTITUDE,[ALTITUDE.replace('altitude=highest=0','altitude=highest=gain[0] if gain else 0'),ALTITUDE.replace('highest=max(highest,altitude)','highest=min(highest,altitude)')],['Treats the first gain as the starting altitude and then adds it again.','Tracks the minimum altitude instead of the maximum.'],altitude_o,raltitude,L('Reached altitudes are prefix sums of gain, with an empty-prefix altitude of zero.','Accumulate gains while tracking the largest running total.','Initialize altitude=highest=0; for each change update altitude and highest.','Every route point corresponds to exactly one prefix, so the maximum observed prefix sum is the answer.'),'O(n)','O(1)',3),
}
BATCH[1730]['wrong'][0]=FOOD.replace('return distance+1','return distance')
BATCH[1730]['wrong_reasons'][0]='Returns the current cell distance without counting the final step into food.'
