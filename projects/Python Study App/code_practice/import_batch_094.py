"""First half of batch 94: trees, graphs, windows, and combinatorial DP."""
from collections import deque
from functools import lru_cache
from itertools import product
from .import_batch_055 import entry

MOD=1_000_000_007
def tree(raw):
 if not raw:return None
 nodes=[None if x is None else [x,None,None] for x in raw];children=iter(nodes[1:])
 for node in nodes:
  if node is not None:
   node[1]=next(children,None);node[2]=next(children,None)
 return nodes[0]
def sequence_o(a):
 root,arr=tree(a[0]),a[1]
 def walk(node,i):return bool(node) and i<len(arr) and node[0]==arr[i] and ((i==len(arr)-1 and node[1] is None and node[2] is None) or (i<len(arr)-1 and (walk(node[1],i+1) or walk(node[2],i+1))))
 return walk(root,0)
def hats_o(a):
 likes=a[0];answer=0
 def assign(person,used):
  nonlocal answer
  if person==len(likes):answer+=1;return
  for hat in likes[person]:
   if hat not in used:assign(person+1,used|{hat})
 assign(0,set());return answer%MOD
def destination_o(a):
 starts={x for x,_ in a[0]};return next(y for _,y in a[0] if y not in starts)
def apart_o(a):
 ones=[i for i,x in enumerate(a[0]) if x];return all(y-x>a[1] for x,y in zip(ones,ones[1:]))
def window_o(a):
 nums,limit=a;return max(j-i for i in range(len(nums)) for j in range(i+1,len(nums)+1) if max(nums[i:j])-min(nums[i:j])<=limit)
def kth_o(a):
 mat,k=a;sums=sorted(sum(x) for x in product(*mat));return sums[k-1]
def stack_o(a):
 target,n=a;out=[];wanted=set(target)
 for value in range(1,target[-1]+1):
  out.append('Push')
  if value not in wanted:out.append('Pop')
 return out
def xor_o(a):
 arr=a[0];return sum(__import__('functools').reduce(int.__xor__,arr[i:k+1],0)==0 for i in range(len(arr)) for k in range(i+1,len(arr)) for _ in range(k-i))
def apples_o(a):
 n,edges,apples=a;g=[[] for _ in range(n)]
 for x,y in edges:g[x].append(y);g[y].append(x)
 parent={0:-1};queue=[0]
 for node in queue:
  for child in g[node]:
   if child not in parent:parent[child]=node;queue.append(child)
 used=set()
 for node,has in enumerate(apples):
  while has and parent[node]!=-1:used.add((parent[node],node));node=parent[node]
 return 2*len(used)
def pizza_o(a):
 pizza,k=a;rows,cols=len(pizza),len(pizza[0])
 def apples(r1,c1,r2,c2):return any(pizza[r][c]=='A' for r in range(r1,r2) for c in range(c1,c2))
 @lru_cache(None)
 def cut(r,c,pieces):
  if pieces==1:return int(apples(r,c,rows,cols))
  return (sum(cut(nr,c,pieces-1) for nr in range(r+1,rows) if apples(r,c,nr,cols))+sum(cut(r,nc,pieces-1) for nc in range(c+1,cols) if apples(r,c,rows,nc)))%MOD
 return cut(0,0,k)

def rseq(r):
 values=[r.randint(0,4) for _ in range(r.randint(1,20))];arr=[values[0]]
 while len(arr)<8 and r.random()<.7:arr.append(r.randint(0,4))
 return [values,arr]
def rhats(r):
 people=r.randint(1,4);return [[sorted(r.sample(range(1,11),r.randint(1,5))) for _ in range(people)]]
def rdest(r):
 n=r.randint(1,10);names=[f'C{i}' for i in range(n+1)];return [[[names[i],names[i+1]] for i in r.sample(range(n),n)]]
def rapart(r):return [[r.randint(0,1) for _ in range(r.randint(1,30))],r.randint(0,10)]
def rwindow(r):return [[r.randint(-20,20) for _ in range(r.randint(1,20))],r.randint(0,20)]
def rkth(r):
 mat=[sorted(r.randint(1,20) for _ in range(r.randint(1,4))) for _ in range(r.randint(1,4))];total=1
 for row in mat:total*=len(row)
 return [mat,r.randint(1,total)]
def rstack(r):
 n=r.randint(1,20);target=sorted(r.sample(range(1,n+1),r.randint(1,n)));return [target,n]
def rxor(r):return [[r.randint(0,15) for _ in range(r.randint(1,20))]]
def rapple(r):
 n=r.randint(1,20);edges=[[i,r.randrange(i)] for i in range(1,n)];return [n,edges,[bool(r.getrandbits(1)) for _ in range(n)]]
def rpizza(r):
 rows,cols=r.randint(1,5),r.randint(1,5);return [[''.join(r.choice('A.') for _ in range(cols)) for _ in range(rows)],r.randint(1,5)]

SEQUENCE='''def is_valid_root_leaf_sequence(root, arr):
 def visit(node,index):
  if not node or index==len(arr) or node.val!=arr[index]:return False
  if index==len(arr)-1:return node.left is None and node.right is None
  return visit(node.left,index+1) or visit(node.right,index+1)
 return visit(root,0)
'''
HATS='''def count_hat_assignments(hats):
 from functools import lru_cache
 people_by_hat=[[] for _ in range(41)]
 for person,choices in enumerate(hats):
  for hat in choices:people_by_hat[hat].append(person)
 full=(1<<len(hats))-1
 @lru_cache(None)
 def solve(hat,mask):
  if mask==full:return 1
  if hat==41:return 0
  answer=solve(hat+1,mask)
  for person in people_by_hat[hat]:
   if not mask>>person&1:answer+=solve(hat+1,mask|1<<person)
  return answer%1000000007
 return solve(1,0)
'''
DEST='''def destination_city(paths):
 origins={origin for origin,_ in paths}
 return next(destination for _,destination in paths if destination not in origins)
'''
FIRST_DEST='''def destination_city(paths):
 return paths[0][1]
'''
APART='''def ones_are_k_apart(nums, k):
 previous=-k-1
 for index,value in enumerate(nums):
  if value:
   if index-previous<=k:return False
   previous=index
 return True
'''
WINDOW='''def longest_bounded_difference_subarray(nums, limit):
 minima=deque();maxima=deque();left=answer=0
 for right,value in enumerate(nums):
  while minima and nums[minima[-1]]>=value:minima.pop()
  while maxima and nums[maxima[-1]]<=value:maxima.pop()
  minima.append(right);maxima.append(right)
  while nums[maxima[0]]-nums[minima[0]]>limit:
   if minima[0]==left:minima.popleft()
   if maxima[0]==left:maxima.popleft()
   left+=1
  answer=max(answer,right-left+1)
 return answer
'''
KTH='''def kth_smallest_matrix_sum(mat, k):
 import heapq
 sums=[0]
 for row in mat:
  heap=[]
  for total in sums:
   for value in row:heapq.heappush(heap,total+value)
  sums=[heapq.heappop(heap) for _ in range(min(k,len(heap)))]
 return sums[k-1]
'''
STACK='''def build_target_with_stack(target, n):
 operations=[];wanted=set(target)
 for value in range(1,target[-1]+1):
  operations.append('Push')
  if value not in wanted:operations.append('Pop')
 return operations
'''
XOR='''def count_equal_xor_triplets(arr):
 answer=0
 for i in range(len(arr)):
  value=0
  for k in range(i,len(arr)):
   value^=arr[k]
   if value==0:answer+=k-i
 return answer
'''
APPLES='''def minimum_apple_collection_time(n, edges, has_apple):
 graph=[[] for _ in range(n)]
 for left,right in edges:graph[left].append(right);graph[right].append(left)
 def visit(node,parent):
  cost=0
  for child in graph[node]:
   if child!=parent:
    below=visit(child,node)
    if below or has_apple[child]:cost+=below+2
  return cost
 return visit(0,-1)
'''
PIZZA='''def pizza_cutting_ways(pizza, k):
 from functools import lru_cache
 rows,cols=len(pizza),len(pizza[0]);suffix=[[0]*(cols+1) for _ in range(rows+1)]
 for r in range(rows-1,-1,-1):
  for c in range(cols-1,-1,-1):suffix[r][c]=(pizza[r][c]=='A')+suffix[r+1][c]+suffix[r][c+1]-suffix[r+1][c+1]
 @lru_cache(None)
 def ways(r,c,pieces):
  if pieces==1:return int(suffix[r][c]>0)
  answer=sum(ways(nr,c,pieces-1) for nr in range(r+1,rows) if suffix[r][c]-suffix[nr][c]>0)
  answer+=sum(ways(r,nc,pieces-1) for nc in range(c+1,cols) if suffix[r][c]-suffix[r][nc]>0)
  return answer%1000000007
 return ways(0,0,k)
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1430:S('is_valid_root_leaf_sequence',[('root','TreeNode | None'),('arr','list[int]')],'bool',['trees','recursion'],['arr must match node values from root through an actual leaf.','Stopping at an internal node or continuing after a leaf is invalid.'],[([[0,1,0,0,1,0,None,None,1,0,0],[0,1,0,1]],'The values follow a root-to-leaf branch ending at the leaf one.'),([[0,1,0],[0,1]],'The matching value one is a leaf, so this shorter path is valid.')],[[t,a] for t,a in [([1],[1]),([1],[1,2]),([1,2,3],[1]),([1,2,3],[1,2]),([1,2,3],[1,3]),([0,1,0,0,1,0,None,None,1,0,0],[0,1,0,1]),([1,2,None,3],[1,2,3]),([1,None,2],[1,2]),([1,2,3,4,5],[1,2,5]),([1,2,3,4,5],[1,2,4]),([2,2,2],[2,2]),([5,4,6,None,3],[5,4,3]),([0],[1]),([1,0,1],[1,1])]],SEQUENCE,[SEQUENCE.replace('node.left is None and node.right is None','True'),SEQUENCE.replace('node.val!=arr[index]','node.val==arr[index]')],['Accepts a sequence ending at an internal node.','Rejects matching node values and follows mismatches.'],sequence_o,rseq,['Match the current node to arr at the current index.','At the final index require both children to be absent.','Before the final index recurse into either child.','These conditions enforce every position and the root-to-leaf endpoint exactly.'],'O(nodes)','O(height)',5),
1434:S('count_hat_assignments',[('hats','list[list[int]]')],'int',['dynamic-programming','bit-masks'],['hats[i] lists distinct hats person i is willing to wear.','Assign every person one liked hat with no shared hat; return the count modulo 1,000,000,007.'],[([[[3,4],[4,5],[5]]],'Only the assignment 3,4,5 gives all three people distinct liked hats.'),([[[3,5,1],[3,5]]],'Four ordered assignments choose distinct hats from the shared choices.')],[[h] for h in [[[1]],[[1],[1]],[[1],[2]],[[1,2],[1,2]],[[3,4],[4,5],[5]],[[3,5,1],[3,5]],[[1,2,3],[2,3,4],[1,4]],[[1,2],[2,3],[3,4]],[[5],[5,6],[6,7]],[[1,2,3,4],[1,2,3,4]],[[1],[2],[3],[4]],[[1,2],[1,2],[1,2]],[[10,20],[20,30],[30,40]],[[1,3,5],[2,4,6],[1,2,6],[3,4,5]]]],HATS,[HATS.replace('if not mask>>person&1','if mask>>person&1'),HATS.replace('answer=solve(hat+1,mask)','answer=0')],['Assigns hats only to people already assigned.','Forces every considered hat to be worn and cannot skip unused hats.'],hats_o,rhats,['Represent assigned people as a bit mask.','Process hats rather than people so a hat can never be reused.','For each hat, either skip it or give it to one unassigned person who likes it.','The state (hat,mask) uniquely partitions all injective assignments.'],'O(40*people*2^people)','O(40*2^people)',8),
1436:S('destination_city',[('paths','list[list[str]]')],'str',['graphs','hash-maps'],['The directed paths form one chain with exactly one terminal city.','Return the city that never appears as an origin.'],[([[['London','New York'],['New York','Lima'],['Lima','Sao Paulo']]],'Sao Paulo is the only destination never used as an origin.'),([[['B','C'],['D','B'],['C','A']]],'Following D to B to C ends at A.')],[[p] for p in [[['A','B']],[['A','B'],['B','C']],[['B','C'],['A','B']],[['London','New York'],['New York','Lima'],['Lima','Sao Paulo']],[['B','C'],['D','B'],['C','A']],[['X','Y'],['Y','Z'],['Z','W']],[['2','1'],['3','2']],[['red','blue'],['blue','green']],[['a','z'],['m','a']],[['start','middle'],['middle','end']],[['q','r'],['p','q'],['r','s']],[['u','v'],['t','u'],['v','w'],['s','t']],[['one','two'],['two','three'],['three','four']],[['left','right']]]],DEST,[FIRST_DEST,'''def destination_city(paths):
 destinations={destination for _,destination in paths}
 return next(origin for origin,_ in paths if origin not in destinations)
'''],['Returns an intermediate destination that is also an origin.','Returns the chain origin rather than its terminal destination.'],destination_o,rdest,['Collect every path origin in a set.','Scan destinations for the one absent from that set.','The chain guarantee makes that city unique.','Every nonterminal city has an outgoing edge and therefore appears among origins.'],'O(paths)','O(paths)',3),
1437:S('ones_are_k_apart',[('nums','list[int]'),('k','int')],'bool',['arrays','indices'],['nums is a binary array.','Between every pair of consecutive ones there must be at least k zeroes.'],[([[1,0,0,0,1,0,0,1],2],'The gaps contain three and then two zeroes, both sufficient.'),([[1,0,1],2],'Only one zero separates the two ones.')],[[n,k] for n,k in [([0],0),([1],5),([1,1],0),([1,1],1),([1,0,1],1),([1,0,1],2),([1,0,0,1],2),([1,0,0,0,1,0,0,1],2),([0,0,0],3),([0,1,0,0],5),([1,0,0,1,0,0,1],2),([1,0,0,1],3),([0,1,0,1,0],1),([1,0,1,0,1],0)]],APART,[APART.replace('<=k','<k'),APART.replace('previous=-k-1','previous=0')],['Allows a gap with only k-1 zeroes.','Treats imaginary positions before the first one as a real prior one.'],apart_o,rapart,['Remember the index of the previous one.','At a new one, index difference must exceed k because the zero count is difference minus one.','Update the remembered position after validation.','Only consecutive ones need checking; any farther pair has an even larger gap.'],'O(n)','O(1)',3),
1438:S('longest_bounded_difference_subarray',[('nums','list[int]'),('limit','int')],'int',['sliding-window','monotonic-queue'],['Find the longest contiguous subarray whose maximum minus minimum is at most limit.','limit is nonnegative.'],[([[8,2,4,7],4],'The longest valid windows [2,4] and [4,7] have length two.'),([[10,1,2,4,7,2],5],'The window [2,4,7,2] has length four and range five.')],[[n,k] for n,k in [([1],0),([1,2],0),([1,2],1),([8,2,4,7],4),([10,1,2,4,7,2],5),([4,2,2,2,4,4,2,2],0),([1,1,1],0),([1,5,1,5],4),([-5,-1,-3],2),([9,8,7,6],1),([1,100,2,3,4],3),([5,4,3,2,1],10),([2,2,3,3,4,4],1),([0,-10,10,0],10)]],WINDOW,['''def longest_bounded_difference_subarray(nums, limit):
 return max([0]+[j-i for i in range(len(nums)) for j in range(i+1,len(nums)+1) if max(nums[i:j])-min(nums[i:j])<limit])
''','''def longest_bounded_difference_subarray(nums, limit):
 return 1+max((abs(nums[i]-nums[i+1])<=limit for i in range(len(nums)-1)),default=0)
'''],['Treats the inclusive difference limit as strict.','Checks only adjacent pairs and cannot extend longer windows.'],window_o,rwindow,['Maintain increasing indices for the minimum and decreasing indices for the maximum.','Their fronts give the current window extrema.','While the range exceeds limit, advance left and remove expired front indices.','After repair, the window is the longest valid one ending at right.'],'O(n)','O(n)',5),
1439:S('kth_smallest_matrix_sum',[('mat','list[list[int]]'),('k','int')],'int',['heaps','sorting'],['Each matrix row is sorted; choose exactly one value from every row.','Return the kth smallest possible sum, counting duplicate combinations.'],[([[[1,3,11],[2,4,6]],5],'Sorted combination sums are 3,5,5,7,7..., so the fifth is seven.'),([[[1,3,11],[2,4,6]],9],'There are nine combinations and the largest sum is seventeen.')],[[m,k] for m,k in [([[1]],1),([[1,2]],2),([[1],[2]],1),([[1,3],[2,4]],1),([[1,3],[2,4]],3),([[1,3,11],[2,4,6]],5),([[1,3,11],[2,4,6]],9),([[1,1],[1,1]],4),([[1,2],[3,4],[5,6]],4),([[2,4,8],[1,3]],3),([[1,10],[2,20],[3,30]],5),([[5],[1,2,3]],2),([[1,2,3],[1,2,3],[1,2,3]],10),([[0,5],[-2,3]],2)]],KTH,[KTH.replace('return sums[k-1]','return sums[k-2] if k>1 else sums[0]'),KTH.replace('heapq.heappush(heap,total+value)','heapq.heappush(heap,total-value)')],['Returns the preceding rank when k is greater than one.','Subtracts row values instead of adding them.'],kth_o,rkth,['Start with the single empty sum zero.','Merge one row at a time by forming every current-sum plus row-value pair.','Only the smallest k partial sums can contribute to the final kth result, so discard larger ones each round.','Induction preserves the smallest k sums after each processed row including multiplicities.'],'O(rows*k*width log(k*width))','O(k*width)',8),
1441:S('build_target_with_stack',[('target','list[int]'),('n','int')],'list[str]',['arrays','simulation'],['Read integers 1 through n in order; Push reads one and Pop removes the current top.','Stop as soon as the strictly increasing target is built.'],[([[1,3],3],'Push one; push then pop two; push three.'),([[1,2,3],3],'Every streamed value belongs to target, so only three Push operations are needed.')],[[t,n] for t,n in [([1],1),([1],5),([2],2),([3],5),([1,3],3),([1,2,3],3),([2,3,4],4),([1,4],5),([2,4],6),([5],5),([1,2,5],5),([3,4],4),([1,3,5,7],7),([2,5,6],8)]],STACK,['''def build_target_with_stack(target, n):
 return ['Push' for _ in range(target[-1])]
''',STACK.replace('target[-1]+1','n+1')],['Never pops streamed values absent from target.','Continues reading and operating after the complete target is built.'],stack_o,rstack,['Read each value only through the largest target value.','Every read always produces Push.','If the value is absent from target, immediately append Pop.','Target is increasing, so retained streamed values exactly form it and later input is unnecessary.'],'O(target[-1])','O(target[-1])',5),
1442:S('count_equal_xor_triplets',[('arr','list[int]')],'int',['prefix-xor','arrays'],['Count triples i<j<=k where XOR(arr[i:j]) equals XOR(arr[j:k+1]).','Different j values count as different triples.'],[([[2,3,1,6,7]],'Four triples split zero-XOR ranges at their valid internal positions.'),([[1,1,1,1,1]],'Ten triples satisfy the equal-XOR condition.')],[[x] for x in [[1],[1,1],[1,2],[0,0],[2,3,1,6,7],[1,1,1,1,1],[0,0,0],[1,2,3],[5,2,7],[4,4,4,4],[1,0,1,0],[3,3,0,3,3],[8,1,9,2,3],[2,2,2,2,2,2]]],XOR,[XOR.replace('answer+=k-i','answer+=1'),XOR.replace('if value==0','if value!=0')],['Counts each zero-XOR range once rather than once per internal split.','Counts nonzero-XOR ranges, which cannot have equal two-part XORs.'],xor_o,rxor,['The two segment XORs are equal exactly when the XOR from i through k is zero.','For each start i, extend k while maintaining that range XOR.','A zero-XOR range of length k-i+1 permits every j from i+1 through k, giving k-i triples.','This equivalence removes the need to inspect j separately.'],'O(n²)','O(1)',5),
1443:S('minimum_apple_collection_time',[('n','int'),('edges','list[list[int]]'),('has_apple','list[bool]')],'int',['trees','depth-first-search'],['The undirected edges form a tree rooted at zero; traversing an edge costs one second.','Start and finish at zero while collecting every apple.'],[([7,[[0,1],[0,2],[1,4],[1,5],[2,3],[2,6]],[False,False,True,False,True,True,False]],'The minimal required subtree uses four edges, each traversed out and back.'),([7,[[0,1],[0,2],[1,4],[1,5],[2,3],[2,6]],[False,False,True,False,False,True,False]],'Only paths to nodes two and five are retained, costing six.')],[[n,e,a] for n,e,a in [(1,[],[False]),(1,[],[True]),(2,[[0,1]],[False,True]),(2,[[0,1]],[True,False]),(3,[[0,1],[1,2]],[False,False,True]),(3,[[0,1],[0,2]],[False,True,True]),(4,[[0,1],[1,2],[1,3]],[False,False,True,False]),(7,[[0,1],[0,2],[1,4],[1,5],[2,3],[2,6]],[False,False,True,False,True,True,False]),(5,[[0,1],[0,2],[2,3],[2,4]],[False,False,False,True,False]),(6,[[0,1],[1,2],[2,3],[3,4],[4,5]],[False,False,False,False,False,True]),(4,[[0,1],[0,2],[0,3]],[False,False,False,False]),(5,[[0,1],[1,2],[2,3],[3,4]],[True,False,False,False,False]),(6,[[0,1],[0,2],[1,3],[1,4],[2,5]],[False,True,False,False,False,True]),(3,[[1,0],[2,1]],[False,True,False])]],APPLES,[APPLES.replace('cost+=below+2','cost+=below+1'),APPLES.replace('below or has_apple[child]','below and has_apple[child]')],['Charges only one direction for each required edge.','Keeps a branch only when its child root itself has an apple as well as deeper cost.'],apples_o,rapple,['Root the undirected tree during DFS by skipping the parent.','A child edge is needed if the child has an apple or its subtree returns positive travel cost.','Add the child cost plus two for traveling down and back.','The union of root-to-apple paths is the unique minimal subtree, and every included edge must be traversed twice.'],'O(n)','O(n)',5),
1444:S('pizza_cutting_ways',[('pizza','list[str]'),('k','int')],'int',['dynamic-programming','prefix-sums'],['Make k-1 horizontal or vertical cuts, always giving away the upper or left piece.','Every final piece needs at least one apple; return ways modulo 1,000,000,007.'],[([['A..','AAA','...'],3],'Three ordered cut sequences produce three apple-containing pieces.'),([['A..','AA.','...'],3],'Only one sequence distributes the three apples among three pieces.')],[[p,k] for p,k in [(['A'],1),(['.'],1),(['A'],2),(['AA'],2),(['A.'],2),(['A..','AAA','...'],3),(['A..','AA.','...'],3),(['...','...','...'],2),(['AAA'],3),(['A','A','A'],3),(['A.A','...','A.A'],2),(['AAAA','....'],2),(['A.','.A'],2),(['AA','AA'],4)]],PIZZA,[PIZZA.replace('>0)', '>=0)'),PIZZA.replace('pieces==1','pieces==0')],['Allows a removed piece containing no apple.','Uses zero remaining pieces as the base case instead of one.'],pizza_o,rpizza,['Precompute apple counts for every bottom-right suffix.','State is the remaining suffix top-left coordinate and number of pieces still required.','Try each horizontal or vertical cut whose removed top/left piece has an apple.','The final suffix must contain an apple; every ordered cut sequence has a unique first cut.'],'O(k*rows*cols*(rows+cols))','O(k*rows*cols)',8),
}
for pid in (1430,):BATCH[pid]['params'][0]=('root','TreeNode | None','treenode')
