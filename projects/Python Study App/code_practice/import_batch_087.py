"""Reviewed DP, parsing, graph, greedy, BFS, and matrix imports."""
from collections import deque
from itertools import combinations
from bisect import bisect_right
from .import_batch_055 import entry

MOD=1_000_000_007
def deletion_oracle(a):
 arr=a[0];best=max(arr)
 for i in range(len(arr)):
  for j in range(i,len(arr)):
   values=arr[i:j+1];best=max(best,sum(values),*(sum(values)-values[k] for k in range(len(values)) if len(values)>1))
 return best
def increasing_oracle(a):
 arr1,arr2=a;states={-10**10:0}
 for value in arr1:
  following={}
  for previous,cost in states.items():
   for candidate,extra in [(value,0),*((x,1) for x in set(arr2))]:
    if candidate>previous:following[candidate]=min(following.get(candidate,10**9),cost+extra)
  states=following
 return min(states.values(),default=-1)
def reverse_oracle(a):
 s=a[0]
 def parse(i):
  out=''
  while i<len(s) and s[i]!=')':
   if s[i]=='(':inner,i=parse(i+1);out+=inner[::-1]
   else:out+=s[i]
   i+=1
  return out,i
 return parse(0)[0]
def concat_oracle(a):
 arr,k=a;values=arr*k;return max([0]+[sum(values[i:j]) for i in range(len(values)) for j in range(i+1,len(values)+1)])%MOD
def bridges_oracle(a):
 n,edges=a;answer=[]
 for removed in range(len(edges)):
  adjacent=[[] for _ in range(n)]
  for i,(x,y) in enumerate(edges):
   if i!=removed:adjacent[x].append(y);adjacent[y].append(x)
  seen={0};q=[0]
  for node in q:
   for other in adjacent[node]:
    if other not in seen:seen.add(other);q.append(other)
  if len(seen)<n:answer.append(sorted(edges[removed]))
 return sorted(answer)
def apples_oracle(a):
 w=a[0];return max((len(c) for size in range(len(w)+1) for c in combinations(w,size) if sum(c)<=5000),default=0)
def knight_oracle(a):
 target=(a[0],a[1]);q=deque([(0,0,0)]);seen={(0,0)};limit=max(abs(a[0]),abs(a[1]))+4
 while q:
  x,y,d=q.popleft()
  if (x,y)==target:return d
  for dx,dy in ((1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)):
   p=(x+dx,y+dy)
   if p not in seen and abs(p[0])<=limit and abs(p[1])<=limit:seen.add(p);q.append((*p,d+1))
def common_oracle(a):
 shared=set(a[0][0])
 for row in a[0][1:]:shared&=set(row)
 return min(shared,default=-1)

def random_arr(r):return [[r.randint(-10,10) for _ in range(r.randint(1,10))]]
def random_inc(r):return [[r.randint(0,12) for _ in range(r.randint(1,7))],[r.randint(0,12) for _ in range(r.randint(1,6))]]
def random_parens(r):
 def make(d=0):
  raw=''.join(r.choice('abc') for _ in range(r.randint(0,3)))
  return raw if d>2 or r.random()<.5 else raw+'('+make(d+1)+')'+''.join(r.choice('abc') for _ in range(r.randint(0,3)))
 s=make()
 return [s or 'a']
def random_concat(r):return [[r.randint(-8,8) for _ in range(r.randint(1,7))],r.randint(1,5)]
def random_graph(r):
 n=r.randint(2,8);edges=[[i,i+1] for i in range(n-1)]
 for i in range(n):
  for j in range(i+2,n):
   if r.random()<.25:edges.append([i,j])
 return [n,edges]
def random_apples(r):return [[r.randint(1,3000) for _ in range(r.randint(1,12))]]
def random_knight(r):return [r.randint(-12,12),r.randint(-12,12)]
def random_mat(r):
 rows=[]
 for _ in range(r.randint(1,6)):rows.append(sorted(r.sample(range(1,25),r.randint(1,8))))
 return [rows]

DELETE='''def maximum_subarray_one_deletion(arr):
 keep=arr[0];drop=float('-inf');answer=arr[0]
 for value in arr[1:]:drop=max(drop+value,keep);keep=max(value,keep+value);answer=max(answer,keep,drop)
 return answer
'''
INCREASE='''def minimum_replacements_increasing(arr1, arr2):
 from bisect import bisect_right
 choices=sorted(set(arr2));states={-float('inf'):0}
 for value in arr1:
  following={}
  for previous,cost in states.items():
   if value>previous:following[value]=min(following.get(value,float('inf')),cost)
   at=bisect_right(choices,previous)
   if at<len(choices):following[choices[at]]=min(following.get(choices[at],float('inf')),cost+1)
  states=following
 return min(states.values(),default=-1)
'''
REVERSE='''def reverse_parenthesized_substrings(s):
 stack=['']
 for char in s:
  if char=='(':stack.append('')
  elif char==')':piece=stack.pop();stack[-1]+=piece[::-1]
  else:stack[-1]+=char
 return stack[0]
'''
CONCAT='''def k_concatenation_max_sum(arr, k):
 mod=1000000007
 def kadane(values):
  best=current=0
  for value in values:current=max(0,current+value);best=max(best,current)
  return best
 if k==1:return kadane(arr)%mod
 return (kadane(arr*2)+max(0,sum(arr))*(k-2))%mod
'''
BRIDGES='''def critical_network_connections(n, connections):
 adjacent=[[] for _ in range(n)]
 for x,y in connections:adjacent[x].append(y);adjacent[y].append(x)
 discovery=[-1]*n;low=[0]*n;answer=[];clock=0
 def visit(node,parent):
  nonlocal clock
  discovery[node]=low[node]=clock;clock+=1
  for other in adjacent[node]:
   if other==parent:continue
   if discovery[other]<0:
    visit(other,node);low[node]=min(low[node],low[other])
    if low[other]>discovery[node]:answer.append(sorted([node,other]))
   else:low[node]=min(low[node],discovery[other])
 visit(0,-1);return sorted(answer)
'''
APPLES='''def maximum_apples_in_basket(weight):
 total=count=0
 for value in sorted(weight):
  if total+value>5000:break
  total+=value;count+=1
 return count
'''
KNIGHT='''def minimum_knight_moves(x, y):
 from collections import deque
 x,y=abs(x),abs(y);q=deque([(0,0,0)]);seen={(0,0)}
 while q:
  a,b,d=q.popleft()
  if (a,b)==(x,y):return d
  for da,db in ((1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)):
   p=(a+da,b+db)
   if p not in seen and p[0]>=-2 and p[1]>=-2 and p[0]<=x+2 and p[1]<=y+2:seen.add(p);q.append((*p,d+1))
'''
COMMON='''def smallest_common_row_value(mat):
 shared=set(mat[0])
 for row in mat[1:]:shared.intersection_update(row)
 return min(shared,default=-1)
'''
E=entry
BATCH={
1186:E('maximum_subarray_one_deletion',[('arr','list[int]')],'int',['dynamic-programming','arrays'],['Choose a nonempty contiguous subarray.','Delete at most one element while leaving at least one.'],[([[1,-2,0,3]],'Delete -2 from the full interval to obtain sum four.'),([[1,-2,-2,3]],'Keeping either endpoint alone gives the maximum three.')],[[x] for x in [[1],[-1],[1,2],[-1,-2],[1,-2,3],[1,-2,0,3],[1,-2,-2,3],[5,-10,4],[0,0,0],[-5,10,-5,10],[8,-1,-1,8],[-1,2,3,-10,4],[3,-4,5,-1,2],[-2,-1,-3]]],DELETE,[DELETE.replace('drop=max(drop+value,keep)','drop=drop+value'),DELETE.replace('answer=max(answer,keep,drop)','answer=max(answer,keep)')],['Never starts a deleted-state subarray at the previous kept sum.','Ignores every result that uses a deletion.'],deletion_oracle,random_arr,['Track the best sum ending here with no deletion and with one deletion.','The kept state either starts at this value or extends; the deleted state either extends or deletes this value from the kept state.','Update the answer from both states at every position.','These transitions enumerate the sole possible deletion location without allowing an empty result.'],'O(n)','O(1)',5),
1187:E('minimum_replacements_increasing',[('arr1','list[int]'),('arr2','list[int]')],'int',['dynamic-programming','binary-search'],['Each arr1 position may be replaced by any arr2 value.','Return -1 when strict increase is impossible.'],[([[1,5,3,6,7],[1,3,2,4]],'Replacing five with two makes the array strictly increasing in one operation.'),([[1,5,3,6,7],[1,6,3,3]],'No sequence of replacements can make arr1 strictly increasing.')],[[a,b] for a,b in [([1],[1]),([2,1],[3]),([1,2,3],[1]),([3,2,1],[1,2,3]),([1,5,3,6,7],[1,3,2,4]),([1,5,3,6,7],[4,3,1]),([1,5,3,6,7],[1,6,3,3]),([5,4],[1,2,3]),([0,10,5],[1,6]),([1,1,1],[2,3]),([10,20,30],[5]),([4,3,2,1],[2,5,6]),([1,7,4,8],[2,3,6]),([5,5],[5])]],INCREASE,[INCREASE.replace('bisect_right','bisect_left'),INCREASE.replace('cost+1','cost')],['Allows a replacement equal to the previous value.','Does not charge for replacement operations.'],increasing_oracle,random_inc,['A state maps the last chosen value to the fewest replacements so far.','At each position, keep arr1 value if it exceeds the previous state value.','Also binary-search the smallest arr2 value strictly larger than the previous value and charge one.','Keeping only minimum cost per ending value preserves every potentially optimal continuation.'],'O(n*m log m)','O(m)',8),
1190:E('reverse_parenthesized_substrings',[('s','str')],'str',['stacks','strings'],['Parentheses are balanced.','Reverse innermost contents first and omit all parentheses.'],[(['(abcd)'],'Reversing the enclosed text yields dcba.'),(['(u(love)i)'],'Inner love becomes evol, then the outer reversal yields iloveu.')],[[s] for s in ['a','()','(a)','(ab)','a(bc)d','(a(bc)d)','((abc))','(ed(et(oc))el)','abc(def(gh)i)j','(())','x(y(z))','(abc)(def)','a((bc))d','((a)b(c))']],REVERSE,[REVERSE.replace('piece[::-1]','piece'),REVERSE.replace("stack[-1]+=piece[::-1]","stack[-1]=piece[::-1]")],['Removes parentheses without reversing their contents.','Overwrites preceding outer content when closing a group.'],reverse_oracle,random_parens,['Use a stack of text buffers, one per open parenthesis depth.','Letters append to the current buffer; an opening parenthesis starts a new buffer.','On closing, pop, reverse, and append the piece to its parent buffer.','Innermost buffers close first, exactly matching the required reversal order.'],'O(n^2)','O(n)',5),
1191:E('k_concatenation_max_sum',[('arr','list[int]'),('k','int')],'int',['dynamic-programming','prefix-sums'],['The empty subarray is allowed with sum zero.','Return the result modulo 1,000,000,007.'],[([[1,2],3],'All six repeated positive values sum to nine.'),([[-1,-2],7],'Every nonempty subarray is negative, so choose the empty subarray.')],[[a,k] for a,k in [([1],1),([1],5),([-1],3),([1,-2,1],2),([1,-2,3],3),([2,-1],4),([-2,5,-1],2),([0,0],10),([5,-10,5],3),([1,2],3),([-1,-2],7),([3,-1,3],1),([3,-1,3],5),([-5,10,-5],4)]],CONCAT,[CONCAT.replace('max(0,sum(arr))','sum(arr)'),CONCAT.replace('arr*2','arr')],['Extends through negative whole-copy sums.','Checks only one copy for cross-boundary subarrays.'],concat_oracle,random_concat,['Kadane’s algorithm gives the best subarray in one or two copies.','For k=1, use one copy directly.','For larger k, the best boundary prefix/suffix appears within two copies; positive total copies between them can all be included.','Thus two-copy best plus max(0,total)*(k-2) covers every optimal structure.'],'O(n)','O(n)',5),
1192:E('critical_network_connections',[('n','int'),('connections','list[list[int]]')],'list[list[int]]',['graphs','depth-first-search'],['The undirected network is connected.','Return every bridge edge.'],[([4,[[0,1],[1,2],[2,0],[1,3]]],'Only edge 1-3 disconnects the graph when removed.'),([2,[[0,1]]],'The only edge is necessarily critical.')],[[n,e] for n,e in [(3,[[0,1],[1,2]]),(3,[[0,1],[1,2],[2,0]]),(4,[[0,1],[1,2],[2,3]]),(4,[[0,1],[1,2],[2,0],[1,3]]),(5,[[0,1],[1,2],[2,0],[1,3],[3,4]]),(4,[[0,1],[0,2],[0,3]]),(5,[[0,1],[1,2],[2,3],[3,4],[4,0]]),(6,[[0,1],[1,2],[2,0],[2,3],[3,4],[4,5],[5,3]]),(3,[[0,1],[0,2]]),(5,[[0,1],[1,2],[2,3],[1,4]]),(6,[[0,1],[1,2],[2,0],[3,4],[4,5],[5,3],[2,3]]),(4,[[0,1],[1,2],[2,3],[0,2]]),(5,[[0,1],[1,2],[2,0],[0,3],[3,4]]),(7,[[0,1],[1,2],[2,0],[2,3],[3,4],[4,5],[5,3],[5,6]])]],BRIDGES,[BRIDGES.replace('low[other]>discovery[node]','low[other]>=discovery[node]'),BRIDGES.replace('else:low[node]=min(low[node],discovery[other])','else:pass')],['Marks cycle edges whose low-link merely equals the parent discovery time.','Overwrites rather than minimizes low-link values on back edges.'],bridges_oracle,random_graph,['DFS discovery times identify ancestor order.','low[node] is the earliest discovery reachable through its subtree plus one back edge.','After visiting a child, its edge is a bridge exactly when child low is greater than parent discovery.','No alternate path then crosses that tree edge; every other edge lies on a cycle.'],'O(n+edges)','O(n+edges)',8),
1196:E('maximum_apples_in_basket',[('weight','list[int]')],'int',['sorting','greedy'],['Basket capacity is 5000.','Every apple may be chosen at most once.'],[([[100,200,150,1000]],'All four apples weigh only 1450.'),([[900,950,800,1000,700,800]],'The five lightest fit, while all six exceed capacity.')],[[w] for w in [[1],[5000],[5001],[100,200,150,1000],[2500,2500,1],[1000]*6,[4999,2],[200,300,400,500,600],[900,950,800,1000,700,800],[1]*12,[3000,1000,1000,1],[1200,1300,1400,1500],[50,5000,50],[700,700,700,700,700,700,700,700]]],APPLES,[APPLES.replace('sorted(weight)','sorted(weight,reverse=True)'),APPLES.replace('>5000','>=5000')],['Chooses heaviest apples first.','Rejects a selection whose total is exactly the capacity.'],apples_oracle,random_apples,['To maximize count under one capacity, lighter apples always dominate heavier ones.','Sort weights ascending and add them in that order.','Stop when the next apple would exceed 5000.','Any same-size selection has at least the prefix weight, so no larger feasible count was skipped.'],'O(n log n)','O(n)',3),
1197:E('minimum_knight_moves',[('x','int'),('y','int')],'int',['breadth-first-search','graphs'],['The board is infinite and coordinates may be negative.','Return the minimum number of knight moves from (0,0).'],[([2,1],'A knight reaches 2,1 in one move.'),([5,5],'A shortest route requires four moves.')],[[x,y] for x,y in [(0,0),(1,0),(0,1),(1,1),(2,0),(2,1),(3,3),(4,4),(5,5),(-2,-1),(-5,5),(10,0),(7,3),(12,12)]],KNIGHT,[KNIGHT.replace('x,y=abs(x),abs(y)','x,y=x,y'),KNIGHT.replace('p[0]>=-2 and p[1]>=-2','p[0]>=0 and p[1]>=0')],['Fails to use board symmetry for negative targets and applies one-sided bounds.','Forbids the small negative detours required near the origin.'],knight_oracle,random_knight,['Reflect the target into the nonnegative quadrant using symmetry.','Breadth-first search guarantees the first visit has minimum move count.','Allow coordinates down to -2 because shortest paths near the axes may briefly cross them; upper bounds need only target+2.','All farther excursions can be reflected or shortened, so the bounded BFS retains an optimal route.'],'O(x*y)','O(x*y)',5),
1198:E('smallest_common_row_value',[('mat','list[list[int]]')],'int',['matrix','hash-maps'],['Every row is strictly increasing.','Return -1 when the row intersection is empty.'],[([[[1,2,3,4,5],[2,4,5,8,10],[3,5,7,9,11],[1,3,5,7,9]]],'Five is the smallest value shared by all four rows.'),([[[1,2],[3,4]]],'The rows have no common value.')],[[m] for m in [[[1]],[[1],[1]],[[1],[2]],[[1,2],[2,3]],[[1,2,3],[2,3,4],[3,4,5]],[[1,2],[1,2]],[[1,3,5],[2,3,5]],[[1,2],[2,3],[3,4]],[[5,6],[1,5],[5,9]],[[1,4,7],[2,4,8],[3,4,9]],[[1,2,3],[1],[1,4]],[[10,20],[5,10,15],[0,10]],[[1,5,9],[2,5,8],[3,5,7]],[[1,2,3],[3],[2,3]]]],COMMON,[COMMON.replace('intersection_update','update'),COMMON.replace('min(shared','max(shared')],['Unions rows instead of intersecting them.','Returns the largest shared value rather than smallest.'],common_oracle,random_mat,['Start with the set of values in the first row.','Intersect it with each subsequent row’s values.','Return the minimum remaining value, or -1 if none remains.','Set intersection preserves exactly values appearing in every processed row.'],'O(total cells)','O(columns)',5),
}
BATCH[1192]['comparator']='unordered_nested'
