"""First half of batch 95: graph reachability, tree traversal, and dynamic programming."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from .import_batch_055 import entry

MOD=1_000_000_007
def tree(raw):
 if not raw:return None
 nodes=[None if x is None else [x,None,None] for x in raw];kids=iter(nodes[1:])
 for node in nodes:
  if node is not None:node[1]=next(kids,None);node[2]=next(kids,None)
 return nodes[0]
def dot_o(a):
 x,y=a;best=-10**18
 for n in range(1,min(len(x),len(y))+1):
  for p in combinations(x,n):
   for q in combinations(y,n):best=max(best,sum(i*j for i,j in zip(p,q)))
 return best
def equal_o(a):return Counter(a[0])==Counter(a[1])
def codes_o(a):
 s,k=a;return {s[i:i+k] for i in range(len(s)-k+1)}=={format(x,f'0{k}b') for x in range(1<<k)}
def courses_o(a):
 n,edges,queries=a;g=[[] for _ in range(n)]
 for x,y in edges:g[x].append(y)
 def reaches(start,target):
  stack=[start];seen={start}
  while stack:
   node=stack.pop()
   for child in g[node]:
    if child==target:return True
    if child not in seen:seen.add(child);stack.append(child)
  return False
 return [reaches(x,y) for x,y in queries]
def cherries_o(a):
 grid=a[0];rows,cols=len(grid),len(grid[0])
 @lru_cache(None)
 def play(r,x,y):
  if r==rows:return 0
  gain=grid[r][x]+(grid[r][y] if x!=y else 0)
  return gain+max(play(r+1,nx,ny) for nx in range(max(0,x-1),min(cols,x+2)) for ny in range(max(0,y-1),min(cols,y+2)))
 return play(0,0,cols-1)
def product_o(a):return max((x-1)*(y-1) for i,x in enumerate(a[0]) for y in a[0][i+1:])
def cake_o(a):
 h,w,hc,vc=a;hg=max(b-a for a,b in zip([0]+sorted(hc),sorted(hc)+[h]));vg=max(b-a for a,b in zip([0]+sorted(vc),sorted(vc)+[w]));return hg*vg%MOD
def routes_o(a):
 n,edges=a;g=[[] for _ in range(n)]
 for x,y in edges:g[x].append(y);g[y].append(x)
 parent={0:-1};queue=[0]
 for node in queue:
  for child in g[node]:
   if child not in parent:parent[child]=node;queue.append(child)
 return sum(parent[y]==x for x,y in edges)
def lonely_o(a):
 root=tree(a[0]);out=[];stack=[root]
 while stack:
  node=stack.pop()
  if not node:continue
  if bool(node[1])!=bool(node[2]):out.append((node[1] or node[2])[0])
  stack.extend((node[1],node[2]))
 return out
def shuffle_o(a):
 nums,n=a;return [v for pair in zip(nums[:n],nums[n:]) for v in pair]

def rdot(r):return [[r.randint(-10,10) for _ in range(r.randint(1,7))],[r.randint(-10,10) for _ in range(r.randint(1,7))]]
def requal(r):
 a=[r.randint(0,10) for _ in range(r.randint(1,25))];b=a[:] if r.random()<.5 else [r.randint(0,10) for _ in a];r.shuffle(b);return [a,b]
def rcodes(r):
 k=r.randint(1,5);return [''.join(r.choice('01') for _ in range(r.randint(k,40))),k]
def rcourse(r):
 n=r.randint(2,10);order=list(range(n));r.shuffle(order);edges=[]
 for i in range(n):
  for j in range(i+1,n):
   if r.random()<.2:edges.append([order[i],order[j]])
 return [n,edges,[[r.randrange(n),r.randrange(n)] for _ in range(r.randint(1,20))]]
def rcherry(r):
 rows,cols=r.randint(2,7),r.randint(2,5);return [[[r.randint(0,15) for _ in range(cols)] for _ in range(rows)]]
def rprod(r):return [[r.randint(1,30) for _ in range(r.randint(2,20))]]
def rcake(r):
 h,w=r.randint(2,30),r.randint(2,30);return [h,w,sorted(r.sample(range(1,h),r.randint(1,min(8,h-1)))),sorted(r.sample(range(1,w),r.randint(1,min(8,w-1))))]
def rroute(r):
 n=r.randint(2,20);edges=[]
 for i in range(1,n):
  p=r.randrange(i);edges.append([p,i] if r.random()<.5 else [i,p])
 return [n,edges]
def rlonely(r):return [[r.randint(-20,20) for _ in range(r.randint(1,25))]]
def rshuffle(r):
 n=r.randint(1,15);return [[r.randint(-20,20) for _ in range(2*n)],n]

DOT='''def maximum_subsequence_dot_product(nums1, nums2):
 rows,cols=len(nums1),len(nums2);dp=[[-10**18]*(cols+1) for _ in range(rows+1)]
 for i in range(1,rows+1):
  for j in range(1,cols+1):
   pair=nums1[i-1]*nums2[j-1];dp[i][j]=max(dp[i-1][j],dp[i][j-1],pair,pair+max(0,dp[i-1][j-1]))
 return dp[rows][cols]
'''
ONE_PAIR_DOT='''def maximum_subsequence_dot_product(nums1, nums2):
 return max(left*right for left in nums1 for right in nums2)
'''
EQUAL='''def arrays_equal_by_reversals(target, arr):
 from collections import Counter
 return Counter(target)==Counter(arr)
'''
CODES='''def contains_all_binary_codes(s, k):
 return len({s[i:i+k] for i in range(len(s)-k+1)})==1<<k
'''
COURSES='''def prerequisite_query_answers(num_courses, prerequisites, queries):
 reach=[[False]*num_courses for _ in range(num_courses)]
 for before,after in prerequisites:reach[before][after]=True
 for middle in range(num_courses):
  for start in range(num_courses):
   if reach[start][middle]:
    for end in range(num_courses):reach[start][end]|=reach[middle][end]
 return [reach[before][after] for before,after in queries]
'''
CHERRIES='''def maximum_two_robot_cherries(grid):
 rows,cols=len(grid),len(grid[0]);state={(0,cols-1):grid[0][0]+grid[0][cols-1]}
 for row in range(1,rows):
  new={}
  for (left,right),total in state.items():
   for x in range(max(0,left-1),min(cols,left+2)):
    for y in range(max(0,right-1),min(cols,right+2)):
     gain=grid[row][x]+(grid[row][y] if x!=y else 0);new[x,y]=max(new.get((x,y),-1),total+gain)
  state=new
 return max(state.values())
'''
PRODUCT='''def maximum_decremented_product(nums):
 largest=second=0
 for value in nums:
  if value>=largest:second,largest=largest,value
  elif value>second:second=value
 return (largest-1)*(second-1)
'''
CAKE='''def maximum_cake_piece_area(h, w, horizontal_cuts, vertical_cuts):
 horizontal=sorted([0,h]+horizontal_cuts);vertical=sorted([0,w]+vertical_cuts)
 max_h=max(b-a for a,b in zip(horizontal,horizontal[1:]));max_w=max(b-a for a,b in zip(vertical,vertical[1:]))
 return max_h*max_w%1000000007
'''
ROUTES='''def minimum_route_reorders(n, connections):
 graph=[[] for _ in range(n)]
 for source,target in connections:graph[source].append((target,1));graph[target].append((source,0))
 answer=0;stack=[(0,-1)]
 while stack:
  node,parent=stack.pop()
  for neighbor,cost in graph[node]:
   if neighbor!=parent:answer+=cost;stack.append((neighbor,node))
 return answer
'''
LONELY='''def lonely_tree_nodes(root):
 answer=[];stack=[root]
 while stack:
  node=stack.pop()
  if not node:continue
  if node.left and not node.right:answer.append(node.left.val)
  if node.right and not node.left:answer.append(node.right.val)
  stack.extend((node.left,node.right))
 return answer
'''
SHUFFLE='''def shuffle_array_halves(nums, n):
 answer=[]
 for i in range(n):answer.extend((nums[i],nums[i+n]))
 return answer
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1458:S('maximum_subsequence_dot_product',[('nums1','list[int]'),('nums2','list[int]')],'int',['dynamic-programming','subsequences'],['Choose non-empty subsequences of equal length while preserving each array’s order.','Return the maximum dot product; values may be negative.'],[([[2,1,-2,5],[3,0,-6]],'Pairing 2 with 3 and -2 with -6 gives eighteen.'),([[3,-2],[2,-6,7]],'The best one-pair subsequence is three times seven, giving twenty-one.')],[[a,b] for a,b in [([1],[1]),([-1],[1]),([-1],[-1]),([2,1,-2,5],[3,0,-6]),([3,-2],[2,-6,7]),([-1,-1],[1,1]),([1,2],[3,4]),([5,-4,3],[-2,6]),([0,0],[1,-1]),([-5,2,3],[4,-1]),([1,-2,3],[-4,5,-6]),([9],[0,1]),([2,2,2],[3,3]),([-3,-2],[-5,-4])]],DOT,[ONE_PAIR_DOT,DOT.replace(',pair,',',0,')],['Chooses only one pair and misses profitable longer subsequences.','Allows an empty subsequence with score zero.'],dot_o,rdot,['DP over prefixes of both arrays.','At each pair, skip either element, start with their product, or extend a positive diagonal result.','Keep the maximum of those choices.','Every valid pair of subsequences has a final matched pair and a preceding prefix solution, while explicit starting preserves non-emptiness.'],'O(n*m)','O(n*m)',8),
1460:S('arrays_equal_by_reversals',[('target','list[int]'),('arr','list[int]')],'bool',['arrays','counting'],['Any subarray may be reversed any number of times.','Return whether arr can become target.'],[([[1,2,3,4],[2,4,1,3]],'The arrays contain the same multiset, and reversals can realize any permutation.'),([[1,2,2,3],[1,1,2,3]],'The multiplicity of one and two differs, so conversion is impossible.')],[[a,b] for a,b in [([1],[1]),([1],[2]),([1,2],[2,1]),([1,2,3,4],[2,4,1,3]),([1,2,2,3],[1,1,2,3]),([0,0],[0,0]),([-1,2],[2,-1]),([1,1,2],[1,2,1]),([1,2,3],[1,2,3]),([5,4,3],[3,4,5]),([1,2,2],[1,1,2]),([10,20,10],[20,10,10]),([0,1,0,1],[1,0,1,0]),([7,8],[7,7])]],EQUAL,[EQUAL.replace('Counter(target)==Counter(arr)','set(target)==set(arr)'),EQUAL.replace('==','!=')],['Ignores duplicate multiplicities.','Returns the opposite of the required multiset equality.'],equal_o,requal,['A length-two reversal swaps adjacent elements.','Adjacent swaps generate any permutation, so only the multiset matters.','Compare value frequencies in target and arr.','Equal counters are sufficient by permutation reachability and necessary because reversal never changes values.'],'O(n)','O(n)',3),
1461:S('contains_all_binary_codes',[('s','str'),('k','int')],'bool',['strings','sliding-window'],['Consider every contiguous substring of length k.','Return whether all 2^k binary strings occur.'],[(['00110110',2],'The windows include 00, 01, 10, and 11.'),(['0110',2],'The length-two code 00 never appears.')],[[s,k] for s,k in [('0',1),('01',1),('00110110',2),('0110',2),('0000',2),('00110',2),('0001011100',3),('111000',3),('10101',1),('10101',2),('10101',3),('00011101',3),('00101110',2),('010101010',4)]],CODES,[CODES.replace('1<<k','(1<<k)-1'),CODES.replace('s[i:i+k]','s[i:i+k-1]')],['Accepts after seeing one fewer than all possible codes.','Collects windows of length k-1.'],codes_o,rcodes,['Collect every length-k window in a set.','There are exactly 2^k possible binary strings.','Return whether the distinct-window count reaches that number.','No other length-k values exist, so reaching the domain size proves complete coverage.'],'O(n*k)','O(2^k*k)',5),
1462:S('prerequisite_query_answers',[('num_courses','int'),('prerequisites','list[list[int]]'),('queries','list[list[int]]')],'list[bool]',['graphs','transitive-closure'],['Each prerequisite edge before->after belongs to a directed acyclic graph.','For every query return whether the first course is a direct or indirect prerequisite of the second.'],[([2,[[1,0]],[[0,1],[1,0]]],'Only course one reaches course zero.'),([3,[[1,2],[1,0],[2,0]],[[1,0],[1,2],[0,1]]],'The first two reachability queries are true; zero cannot reach one.')],[[n,e,q] for n,e,q in [(2,[],[[0,1]]),(2,[[0,1]],[[0,1],[1,0]]),(3,[[0,1],[1,2]],[[0,2],[2,0]]),(3,[[1,2],[1,0],[2,0]],[[1,0],[1,2],[0,1]]),(4,[[0,1],[2,3]],[[0,3],[2,3]]),(4,[[0,1],[1,2],[2,3]],[[0,3],[1,3],[3,0]]),(3,[],[[0,0],[1,1]]),(5,[[0,2],[2,4],[1,3]],[[0,4],[1,4]]),(2,[[1,0]],[[0,1],[1,0]]),(6,[[0,1],[0,2],[2,3],[3,4]],[[0,4],[1,4]]),(4,[[3,2],[2,1]],[[3,1],[1,3]]),(5,[[4,3],[3,2],[2,1],[1,0]],[[4,0],[3,0]]),(3,[[0,2],[1,2]],[[0,1],[0,2]]),(4,[[0,1],[0,2],[1,3],[2,3]],[[0,3],[1,2]])]],COURSES,[COURSES.replace('reach[start][end]|=reach[middle][end]','reach[start][end]=reach[middle][end]'),COURSES.replace('for middle in range(num_courses)','for middle in []')],['Overwrites existing reachability while propagating through a middle course.','Checks only direct edges by skipping transitive closure.'],courses_o,rcourse,['Store direct prerequisite reachability in a boolean matrix.','For each possible middle course, connect every start that reaches it to every end it reaches.','Then answer each query by its matrix cell.','Floyd-Warshall induction proves that after each middle, paths using processed intermediate vertices are represented.'],'O(courses³)','O(courses²)',5),
1463:S('maximum_two_robot_cherries',[('grid','list[list[int]]')],'int',['dynamic-programming','grids'],['Two robots start at row zero columns zero and last; each moves to column-1, same, or column+1 on the next row.','Collect a cell once when both robots occupy it; maximize total through the last row.'],[([[[3,1,1],[2,5,1],[1,5,5],[2,1,1]]],'Coordinated paths collect twenty-four cherries.'),([[[1,0,0,0,0,0,1],[2,0,0,0,0,3,0],[2,0,9,0,0,0,0],[0,3,0,5,4,0,0],[1,0,2,3,0,0,6]]],'The optimal pair collects twenty-eight.')],[[g] for g in [[[1,1]],[[1,2],[3,4]],[[3,1,1],[2,5,1],[1,5,5],[2,1,1]],[[0,0],[0,0]],[[1,2,3],[4,5,6]],[[5,1],[1,5],[5,1]],[[1,0,1],[0,9,0],[1,0,1]],[[1,2,3,4],[4,3,2,1]],[[1,1,1],[1,1,1],[1,1,1]],[[9,0,0,9],[0,9,9,0]],[[2,4,1],[3,0,5],[1,6,2]],[[1,0,0,1],[0,5,0,0],[0,0,5,0]],[[7,1],[2,3]],[[1,2,1],[2,1,2],[1,2,1],[2,1,2]]]],CHERRIES,[CHERRIES.replace("grid[row][y] if x!=y else 0","grid[row][y]"),CHERRIES.replace('range(max(0,left-1),min(cols,left+2))','range(left,left+1)')],['Double-counts a cell when both robots meet.','Prevents the first robot from changing columns.'],cherries_o,rcherry,['DP state after a row is the pair of robot columns and best collected total.','Try all nine legal next-column pairs.','Add both cells, but only once if columns coincide.','Every pair of robot paths has a unique prior state and next move, so row transitions enumerate all possibilities.'],'O(rows*cols²*9)','O(cols²)',8),
1464:S('maximum_decremented_product',[('nums','list[int]')],'int',['arrays','greedy'],['Choose two distinct indices and maximize (nums[i]-1)*(nums[j]-1).','Every value is positive.'],[([[3,4,5,2]],'Using five and four gives four times three, or twelve.'),([[1,5,4,5]],'The two fives give sixteen.')],[[x] for x in [[1,1],[1,2],[2,2],[3,4,5,2],[1,5,4,5],[10,2],[5,5],[2,3,4],[9,1,8],[100,99],[4,4,3,3],[1,1,10],[6,2,6,2],[7,8,9,10]]],PRODUCT,[PRODUCT.replace('value>=largest','value<=largest'),PRODUCT.replace('(largest-1)*(second-1)','largest*second')],['Tracks the smallest values instead of the largest two.','Forgets to decrement both chosen values.'],product_o,rprod,['Only the two largest values can maximize the product of nonnegative decremented values.','Track largest and second-largest in one scan.','Update both when a new maximum arrives, otherwise update the runner-up.','Monotonicity of multiplication on nonnegative operands proves no smaller pair can improve the result.'],'O(n)','O(1)',3),
1465:S('maximum_cake_piece_area',[('h','int'),('w','int'),('horizontal_cuts','list[int]'),('vertical_cuts','list[int]')],'int',['sorting','geometry'],['Cuts span the full cake at the given coordinates.','Return the largest rectangular piece area modulo 1,000,000,007.'],[([5,4,[1,2,4],[1,3]],'The largest horizontal and vertical gaps are both two, giving area four.'),([5,4,[3,1],[1]],'The largest gaps are two high and three wide, giving six.')],[[*x] for x in [(2,2,[1],[1]),(5,4,[1,2,4],[1,3]),(5,4,[3,1],[1]),(10,10,[5],[5]),(100,2,[1,99],[1]),(8,9,[2,6],[3,7]),(7,6,[1,2,3],[2,4]),(9,9,[8],[8]),(4,5,[1],[1,2,3]),(20,30,[2,10,19],[1,29]),(6,7,[5,1],[6,1]),(3,100,[1,2],[50]),(1000000000,1000000000,[1],[1]),(12,15,[3,6,9],[5,10])]],CAKE,[CAKE.replace('sorted([0,h]+horizontal_cuts)','sorted([0]+horizontal_cuts)'),CAKE.replace('max_h*max_w','max_h+max_w')],['Omits the far cake boundary when computing horizontal gaps.','Adds maximum gaps instead of multiplying them for area.'],cake_o,rcake,['Add zero and the full dimension to each cut list.','Sort and find the maximum gap between consecutive horizontal coordinates and likewise vertical coordinates.','Multiply the two independent maximum gaps and reduce modulo the modulus.','Every piece combines one horizontal and one vertical gap, so the largest of each yields the largest possible area.'],'O(cuts log cuts)','O(cuts)',5),
1466:S('minimum_route_reorders',[('n','int'),('connections','list[list[int]]')],'int',['graphs','trees'],['The underlying undirected graph is a tree, while each connection has its listed direction.','Reverse the fewest edges so every city can follow directed roads to city zero.'],[([6,[[0,1],[1,3],[2,3],[4,0],[4,5]]],'Three edges point away from zero in the rooted traversal and must reverse.'),([5,[[1,0],[1,2],[3,2],[3,4]]],'Two listed directions oppose travel toward zero.')],[[n,e] for n,e in [(2,[[0,1]]),(2,[[1,0]]),(3,[[0,1],[1,2]]),(3,[[1,0],[2,1]]),(6,[[0,1],[1,3],[2,3],[4,0],[4,5]]),(5,[[1,0],[1,2],[3,2],[3,4]]),(4,[[0,1],[2,0],[3,2]]),(4,[[1,0],[2,1],[3,2]]),(5,[[0,1],[0,2],[0,3],[0,4]]),(5,[[1,0],[2,0],[3,0],[4,0]]),(6,[[0,2],[3,2],[4,3],[4,5],[1,0]]),(7,[[1,0],[1,2],[3,1],[3,4],[5,3],[6,5]]),(3,[[2,0],[1,2]]),(8,[[0,1],[2,1],[2,3],[4,3],[4,5],[6,5],[7,6]])]],ROUTES,[ROUTES.replace("graph[source].append((target,1))","graph[source].append((target,0))"),ROUTES.replace('answer+=cost','answer+=1-cost')],['Marks originally outward edges as already correct.','Counts edges oriented toward zero rather than away from it.'],routes_o,rroute,['View the connections as an undirected tree rooted at zero while remembering each original direction.','Traversing from zero to a child costs one reversal exactly when the original edge points parent-to-child.','Sum those costs in DFS or BFS.','Every non-root node has one parent edge and must use it toward zero, so each incorrect edge is independently necessary and sufficient to reverse.'],'O(n)','O(n)',5),
1469:S('lonely_tree_nodes',[('root','TreeNode | None')],'list[int]',['trees','depth-first-search'],['A node is lonely when its parent has exactly one child.','Return all lonely node values in any order.'],[([[1,2,3,None,4]],'Node four is the only child of node two.'),([[7,1,None,6]],'Nodes one and six are each the sole child of their parent.')],[[t] for t in [[1],[1,2],[1,None,2],[1,2,3],[1,2,3,None,4],[7,1,None,6],[1,2,3,4],[1,2,3,None,None,4],[1,2,None,3,None,4],[0,-1,1,None,-2],[5,4,6,3,None,None,7],[1,None,2,3,4],[2,1,3,None,4,None,5],[9,8,None,7,None,6]]],LONELY,[LONELY.replace('not node.right','node.right'),LONELY.replace('answer.append(node.left.val)','answer.append(node.val)')],['Requires a left child to have a right sibling before recording it.','Returns the parent value for a lonely left child.'],lonely_o,rlonely,['Traverse every parent node.','When left exists without right, record left.val; when right exists without left, record right.val.','Continue into both present children.','The exclusive-child checks are exactly the definition of loneliness and visit every possible parent.'],'O(n)','O(n)',3),
1470:S('shuffle_array_halves',[('nums','list[int]'),('n','int')],'list[int]',['arrays','simulation'],['nums contains x1..xn followed by y1..yn.','Return x1,y1,x2,y2,...,xn,yn.'],[([[2,5,1,3,4,7],3],'Pairing aligned values from the two halves gives 2,3,5,4,1,7.'),([[1,2,3,4,4,3,2,1],4],'The aligned half pairs produce 1,4,2,3,3,2,4,1.')],[[v,n] for v,n in [([1,2],1),([2,5,1,3,4,7],3),([1,2,3,4,4,3,2,1],4),([1,1,2,2],2),([0,1,2,3],2),([-1,-2,1,2],2),([1,2,3,4,5,6],3),([9,8,7,6,5,4,3,2],4),([5,5],1),([1,10,2,20],2),([3,1,4,1,5,9],3),([0,0,0,0,0,0],3),([100,-100],1),([1,2,3,4,5,6,7,8,9,10],5)]],SHUFFLE,[SHUFFLE.replace('nums[i+n]','nums[i+n-1]'),SHUFFLE.replace('answer.extend((nums[i],nums[i+n]))','answer.extend((nums[i+n],nums[i]))')],['Offsets the second half one position too early.','Outputs each y before its aligned x.'],shuffle_o,rshuffle,['The first half occupies indices zero through n-1 and the second half starts at n.','For each i, append nums[i] followed by nums[i+n].','Repeat through n pairs.','Each source element appears once in the required interleaved position.'],'O(n)','O(n)',3),
}
for pid in (1469,):BATCH[pid]['params'][0]=('root','TreeNode | None','treenode')
BATCH[1469]['comparator']='unordered'
