"""First half of batch 97: interval closure, bitwise sets, trees, and prefix counting."""
from collections import Counter,deque
from itertools import combinations
from .import_batch_055 import entry
MOD=1_000_000_007

def substr_o(a):
 s=a[0];first={c:s.index(c) for c in set(s)};last={c:s.rindex(c) for c in set(s)};valid=[]
 for left in range(len(s)):
  for right in range(left,len(s)):
   if all(first[c]>=left and last[c]<=right for c in set(s[left:right+1])):valid.append((left,right))
 best=None
 for size in range(len(valid)+1):
  for chosen in combinations(valid,size):
   if all(a[1]<b[0] or b[1]<a[0] for a,b in combinations(chosen,2)):
    key=(-size,sum(y-x+1 for x,y in chosen))
    if best is None or key<best[0]:best=(key,chosen)
 return [s[x:y+1] for x,y in best[1]]
def and_o(a):
 arr,target=a;return min(abs(target-_and(arr[i:j])) for i in range(len(arr)) for j in range(i+1,len(arr)+1))
def _and(values):
 out=values[0]
 for value in values[1:]:out&=value
 return out
def _nary_graph(raw):
 if not raw:return []
 graph=[[]];queue=[0];index=2;next_node=1
 for parent in queue:
  while index<len(raw) and raw[index] is not None:
   graph.append([]);graph[parent].append(next_node);graph[next_node].append(parent);queue.append(next_node);next_node+=1;index+=1
  index+=1
 return graph
def diameter_o(a):
 graph=_nary_graph(a[0]);n=len(graph)
 answer=0
 for start in range(n):
  distance=[-1]*n;distance[start]=0;queue=[start]
  for node in queue:
   for child in graph[node]:
    if distance[child]<0:distance[child]=distance[node]+1;queue.append(child)
  answer=max(answer,max(distance))
 return answer
def odds_o(a):return sum(value%2 for value in range(a[0],a[1]+1))
def oddsum_o(a):
 arr=a[0];return sum(sum(arr[i:j])%2 for i in range(len(arr)) for j in range(i+1,len(arr)+1))%MOD
def splits_o(a):
 s=a[0];return sum(len(set(s[:i]))==len(set(s[i:])) for i in range(1,len(s)))
def increments_o(a):
 target=a[0];return sum(sum(target[i]>=height and (i==0 or target[i-1]<height) for i in range(len(target))) for height in range(1,max(target,default=0)+1))
def shuffle_o(a):
 s,indices=a;out=['']*len(s)
 for char,index in zip(s,indices):out[index]=char
 return ''.join(out)
def flips_o(a):
 target=a[0];start='0'*len(target);queue=deque([(start,0)]);seen={start}
 while queue:
  value,moves=queue.popleft()
  if value==target:return moves
  for index in range(len(value)):
   nxt=value[:index]+''.join('1' if c=='0' else '0' for c in value[index:])
   if nxt not in seen:seen.add(nxt);queue.append((nxt,moves+1))
def tree(raw):
 if not raw:return None
 nodes=[None if x is None else [x,None,None] for x in raw];kids=iter(nodes[1:])
 for node in nodes:
  if node is not None:node[1]=next(kids,None);node[2]=next(kids,None)
 return nodes[0]
def leaf_o(a):
 root=tree(a[0]);limit=a[1];nodes=[];graph={};leaves=[]
 def visit(node,parent=None):
  if not node:return
  index=len(nodes);nodes.append(node);graph[index]=[]
  if parent is not None:graph[index].append(parent);graph[parent].append(index)
  if not node[1] and not node[2]:leaves.append(index)
  visit(node[1],index);visit(node[2],index)
 visit(root);answer=0
 for i,start in enumerate(leaves):
  distance={start:0};queue=[start]
  for node in queue:
   for child in graph[node]:
    if child not in distance:distance[child]=distance[node]+1;queue.append(child)
  answer+=sum(distance[end]<=limit for end in leaves[i+1:])
 return answer

def rsubstr(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,9)))]
def rand(r):return [[r.randint(0,1023) for _ in range(r.randint(1,12))],r.randint(0,1023)]
def rdiameter(r):
 n=r.randint(1,20);children=[[] for _ in range(n)]
 for node in range(1,n):children[r.randrange(node)].append(node)
 raw=[0,None];queue=[0]
 for parent in queue:
  for child in children[parent]:raw.append(child);queue.append(child)
  raw.append(None)
 while raw and raw[-1] is None:raw.pop()
 return [raw]
def rodds(r):
 low=r.randint(0,10000);return [low,r.randint(low,low+10000)]
def roddsum(r):return [[r.randint(0,30) for _ in range(r.randint(1,40))]]
def rsplits(r):return [''.join(r.choice('abcde') for _ in range(r.randint(2,40)))]
def rincrements(r):return [[r.randint(0,8) for _ in range(r.randint(1,12))]]
def rshuffle(r):
 n=r.randint(1,20);indices=list(range(n));r.shuffle(indices);return [''.join(r.choice('abcXYZ') for _ in range(n)),indices]
def rflips(r):return [''.join(r.choice('01') for _ in range(r.randint(1,10)))]
def rleaf(r):
 raw=[r.randint(0,20) for _ in range(r.randint(1,20))]
 for i in range(1,len(raw)):
  if r.random()<.2:raw[i]=None
 return [raw,r.randint(1,8)]

SUBSTR='''def maximum_closed_substrings(s):
 first={char:len(s) for char in set(s)};last={}
 for index,char in enumerate(s):first[char]=min(first[char],index);last[char]=index
 intervals=[]
 for left,char in enumerate(s):
  if first[char]!=left:continue
  right=last[char];index=left;valid=True
  while index<=right:
   if first[s[index]]<left:valid=False;break
   right=max(right,last[s[index]]);index+=1
  if valid:intervals.append((left,right))
 intervals.sort(key=lambda item:item[1]);chosen=[];end=-1
 for left,right in intervals:
  if left>end:chosen.append(s[left:right+1]);end=right
 return chosen
'''
AND='''def closest_subarray_and(arr, target):
 answer=float('inf');ending=set()
 for value in arr:
  ending={value}|{previous&value for previous in ending}
  answer=min(answer,min(abs(candidate-target) for candidate in ending))
 return answer
'''
DIAMETER='''def nary_tree_diameter(root):
 if not root:return 0
 graph=[[]];queue=[0];index=2;next_node=1
 for parent in queue:
  while index<len(root) and root[index] is not None:
   graph.append([]);graph[parent].append(next_node);graph[next_node].append(parent);queue.append(next_node);next_node+=1;index+=1
  index+=1
 answer=0
 def visit(node,parent):
  nonlocal answer
  longest=second=0
  for child in graph[node]:
   if child==parent:continue
   depth=visit(child,node)+1
   if depth>longest:second,longest=longest,depth
   elif depth>second:second=depth
  answer=max(answer,longest+second)
  return longest
 visit(0,-1)
 return answer
'''
ODDS='''def count_odds_in_interval(low, high):
 return (high+1)//2-low//2
'''
ODDSUM='''def count_odd_sum_subarrays(arr):
 even,odd=1,0;parity=answer=0
 for value in arr:
  parity^=value&1
  if parity:answer+=even;odd+=1
  else:answer+=odd;even+=1
 return answer%1000000007
'''
SPLITS='''def count_good_string_splits(s):
 right=Counter(s);left=set();answer=0
 for char in s[:-1]:
  left.add(char);right[char]-=1
  if right[char]==0:del right[char]
  answer+=len(left)==len(right)
 return answer
'''
INCREMENTS='''def minimum_subarray_increments(target):
 answer=previous=0
 for value in target:
  if value>previous:answer+=value-previous
  previous=value
 return answer
'''
SHUFFLE='''def restore_shuffled_string(s, indices):
 answer=['']*len(s)
 for index,char in enumerate(s):answer[indices[index]]=char
 return ''.join(answer)
'''
FLIPS='''def minimum_suffix_flips(target):
 flips=0;current='0'
 for bit in target:
  if bit!=current:flips+=1;current=bit
 return flips
'''
LEAVES='''def count_close_leaf_pairs(root, distance):
 answer=0
 def visit(node):
  nonlocal answer
  if not node:return []
  if not node.left and not node.right:return [1]
  left,right=visit(node.left),visit(node.right)
  answer+=sum(a+b<=distance for a in left for b in right)
  return [depth+1 for depth in left+right if depth+1<distance]
 visit(root)
 return answer
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1520:S('maximum_closed_substrings',[('s','str')],'list[str]',['strings','greedy'],['Every returned substring must contain every occurrence in s of each character it contains.','Maximize the number of non-overlapping substrings, then minimize their total length.'],[(['adefaddaccc'],'The minimal valid choices e, f, and ccc are disjoint and give the maximum count three.'),(['abbaccd'],'The minimal maximum-count answer is bb, cc, and d; choosing abba would be longer.')],[[s] for s in ['a','ab','aa','adefaddaccc','abbaccd','abab','cabcccbaa','eccbbbbdec','abcab','abac','aabbcc','abca','abcdedcba','caedbdedda']],SUBSTR,[SUBSTR.replace('if first[s[index]]<left:valid=False;break',''),SUBSTR.replace('intervals.sort(key=lambda item:item[1])','intervals.sort()')],['Accepts intervals that omit earlier occurrences of a contained character.','Chooses by starting position instead of earliest finishing valid interval.'],substr_o,rsubstr,['Record the first and last occurrence of every character.','Only a first occurrence can start a minimal closed interval; expand its end for every character encountered.','Reject an interval if an encountered character begins before it.','Earliest-finish interval scheduling maximizes the count, while minimal closed candidates give the unique minimum total length.'],'O(n*alphabet)','O(alphabet)',8),
1521:S('closest_subarray_and',[('arr','list[int]'),('target','int')],'int',['bit-manipulation','arrays'],['For each non-empty contiguous subarray, func is the bitwise AND of all its values.','Return the minimum absolute difference between such a value and target.'],[([[9,12,3,7,15],5],'A subarray AND can reach seven, whose distance from five is two.'),([[1,2,4,8,16],0],'The AND of adjacent distinct powers of two is zero, matching the target.')],[[a,t] for a,t in [([1],0),([5],5),([9,12,3,7,15],5),([1,2,4,8,16],0),([8,8],7),([7,3],2),([15,14,12],10),([0,1,2],3),([1023,511,255],256),([5,6,7],4),([10,10,10],1),([1,3,7,15],6),([12,5,10],8),([31,30,28,24],25)]],AND,[AND.replace('previous&value','previous|value'),AND.replace("ending={value}|{previous&value for previous in ending}","ending={value}")],['Uses bitwise OR rather than bitwise AND.','Considers only single-element subarrays.'],and_o,rand,['Track the distinct AND values of subarrays ending at the previous index.','At a new value, start a singleton and AND it with every previous ending value.','Measure every resulting value against target.','AND only clears bits, so duplicate states collapse and the set stays logarithmically small in the value range.'],'O(n*bits)','O(bits)',8),
1522:S('nary_tree_diameter',[('root','list[int | None]')],'int',['trees','depth-first-search'],['root is an N-ary tree in level order, with null separating consecutive parents’ child groups.','Return the longest path between two nodes measured in edges.'],[([[1,None,3,2,4,None,5,6]],'The longest path from five or six through node three and the root to node two or four uses three edges.'),([[1]],'A one-node tree has no edges, so its diameter is zero.')],[[x] for x in [[1],[1,None,2],[1,None,2,3],[1,None,2,None,3,None,4],[1,None,3,2,4,None,5,6],[1,None,2,3,None,4,5],[1,None,2,3,4],[1,None,2,None,3,4,None,5],[1,None,2,3,None,4,None,5,6],[1,None,2,3,4,5],[1,None,2,None,3,None,4,None,5],[1,None,2,3,None,4,5,None,6],[1,None,2,3,4,None,5,None,6],[1,None,2,3,None,None,4]]],DIAMETER,[DIAMETER.replace('longest+second','longest'),DIAMETER.replace('return longest','return longest+1')],['Records only the greatest downward depth, missing paths joining two branches.','Adds an extra edge at every recursive return.'],diameter_o,rdiameter,['Parse each null-delimited child group into an adjacency list.','Each DFS call returns its longest downward branch.','Keep the two longest child branches and update the global diameter with their sum.','Every simple path has a highest node where its two branches meet, so that node evaluates its exact length.'],'O(n)','O(n)',5),
1523:S('count_odds_in_interval',[('low','int'),('high','int')],'int',['math'],['low and high are nonnegative and low<=high.','Count odd integers in the inclusive interval.'],[([3,7],'The odd values are three, five, and seven, for three total.'),([8,10],'Only nine is odd, so the answer is one.')],[[a,b] for a,b in [(0,0),(0,1),(1,1),(3,7),(8,10),(2,2),(2,3),(10,20),(11,21),(100,1000),(999,1001),(4,9),(15,15),(16,16)]],ODDS,[ODDS.replace('(high+1)//2','high//2'),ODDS.replace('low//2','(low+1)//2')],['Excludes an odd high endpoint.','Subtracts as though an odd low endpoint were outside the interval.'],odds_o,rodds,['The number of positive odds at most x is (x+1)//2.','Subtract the count at most low-1, which is low//2.','The difference includes both endpoints.','This prefix-count subtraction partitions all odd values exactly.'],'O(1)','O(1)',3),
1524:S('count_odd_sum_subarrays',[('arr','list[int]')],'int',['prefix-sums','dynamic-programming'],['Count non-empty contiguous subarrays with odd sum.','Return the count modulo 1,000,000,007.'],[([[1,3,5]],'The three singleton sums and the full-array sum are odd, giving four.'),([[2,4,6]],'Every subarray sum is even, so the answer is zero.')],[[x] for x in [[1],[2],[1,3,5],[2,4,6],[1,2],[2,1],[1,1],[1,2,3,4],[0,1,0],[5,5,5],[2,3,4,5],[0,0,1],[7,2,7,2],[10,11,12,13]]],ODDSUM,[ODDSUM.replace('if parity:answer+=even','if parity:answer+=odd'),ODDSUM.replace('parity^=value&1','parity=value&1')],['Pairs odd prefixes with odd prefixes instead of earlier even prefixes.','Uses only the current element parity rather than cumulative prefix parity.'],oddsum_o,roddsum,['A subarray sum is odd exactly when its two endpoint prefix parities differ.','Begin with one even empty prefix.','For each cumulative parity, add the count of earlier opposite parities, then record it.','Every subarray corresponds to exactly one ordered pair of prefixes.'],'O(n)','O(1)',5),
1525:S('count_good_string_splits',[('s','str')],'int',['strings','prefix-counting'],['Split s after any position that leaves two non-empty strings.','Count splits whose left and right sides contain the same number of distinct characters.'],[(['aacaba'],'Splits after the third and fourth characters give equal distinct counts, so there are two.'),(['abcd'],'Only the middle split gives two distinct characters on each side.')],[[s] for s in ['aa','ab','aacaba','abcd','aaaa','abab','abcabc','aabb','abca','xyzzy','abcdeabc','aabcc','abbccc','abacaba']],SPLITS,[SPLITS.replace('==len(right)','<=len(right)'),SPLITS.replace('s[:-1]','s[1:-1]')],['Counts unequal splits whenever the left has fewer distinct characters.','Skips the first possible split.'],splits_o,rsplits,['Count all right-side character frequencies initially.','Move one character per split into a left-side set and decrement it on the right.','Delete a right key when its count reaches zero, then compare distinct counts.','The maintained structures exactly represent both non-empty sides at each possible split.'],'O(n)','O(alphabet)',5),
1526:S('minimum_subarray_increments',[('target','list[int]')],'int',['arrays','greedy'],['Start from an all-zero array of target’s length.','One operation increments every position in a chosen contiguous subarray; return the minimum operations to form target.'],[([[1,2,3,2,1]],'One full increment plus nested increments on the middle three and center makes the target in three operations.'),([[3,1,1,2]],'Three layers begin at index zero and one additional layer begins at the final index, totaling four.')],[[x] for x in [[0],[1],[1,2,3,2,1],[3,1,1,2],[1,1,1],[1,2,3],[3,2,1],[0,2,0],[2,0,2],[5,5,1,4],[0,0,0],[1,3,2,5],[4,1,4,1],[2,2,5,5,3]]],INCREMENTS,[INCREMENTS.replace('if value>previous:answer+=value-previous','answer+=value'),INCREMENTS.replace('if value>previous:','if value!=previous:').replace('value-previous','abs(value-previous)')],['Counts every target unit separately and ignores sharing one operation across a subarray.','Also charges for downward transitions, though ending active layers costs no operation.'],increments_o,rincrements,['Visualize target as horizontal unit-height layers.','An operation must start whenever the current height rises above the previous height.','Add each positive adjacent rise, treating the height before index zero as zero.','Existing active layers extend through flat or lower heights for free; every new layer start is necessary and sufficient.'],'O(n)','O(1)',8),
1528:S('restore_shuffled_string',[('s','str'),('indices','list[int]')],'str',['strings','arrays'],['indices is a permutation of positions 0 through len(s)-1.','Character s[i] must move to position indices[i].'],[(['codeleet',[4,5,6,7,0,2,1,3]],'Placing every character at its listed destination spells leetcode.'),(['abc',[0,1,2]],'The identity permutation leaves abc unchanged.')],[[s,i] for s,i in [('a',[0]),('abc',[0,1,2]),('codeleet',[4,5,6,7,0,2,1,3]),('aiohn',[3,1,4,2,0]),('art',[1,0,2]),('abc',[2,1,0]),('abcd',[1,2,3,0]),('hello',[4,3,2,1,0]),('xy',[1,0]),('aaaa',[2,0,3,1]),('python',[5,4,3,2,1,0]),('study',[2,0,4,1,3]),('matrix',[1,3,5,0,2,4]),('recursion',[8,7,6,5,4,3,2,1,0])]],SHUFFLE,[SHUFFLE.replace('answer[indices[index]]=char','answer[index]=s[indices[index]]'),SHUFFLE.replace("answer=['']*len(s)","answer=['']*len(s);indices=list(reversed(indices))")],['Reads characters from destination indices instead of moving each source character there.','Reverses the destination mapping before placement.'],shuffle_o,rshuffle,['Allocate an output slot for every character.','For each source index i, place s[i] into output[indices[i]].','Join the filled slots.','Because indices is a permutation, every output position is filled exactly once with its specified source.'],'O(n)','O(n)',3),
1529:S('minimum_suffix_flips',[('target','str')],'int',['strings','greedy'],['Start with an all-zero string of target’s length.','A move flips every bit from one chosen index through the end; return the minimum moves to reach target.'],[(['10111'],'Transitions 0→1, 1→0, and 0→1 require three suffix flips.'),(['00000'],'The initial string already matches, so no flips are needed.')],[[s] for s in ['0','1','00','01','10','11','10111','00000','001011101','11111','01010','11001','10000','00001']],FLIPS,[FLIPS.replace('flips+=1;current=bit','flips+=bit==\'1\';current=bit'),FLIPS.replace("current='0'","current=target[0]")],['Counts only transitions into one, missing flips needed to return to zero.','Pretends the initial suffix state already equals the first target bit.'],flips_o,rflips,['All positions at and after the latest flip share one current effective bit.','Scan target left to right; when its bit differs from that state, a flip is necessary.','Count the flip and update the effective bit.','Earlier positions can no longer be changed without breaking them, so every mismatch forces exactly one optimal flip.'],'O(n)','O(1)',5),
1530:S('count_close_leaf_pairs',[('root','TreeNode | None'),('distance','int')],'int',['trees','recursion'],['A leaf has no children; each unordered pair of distinct leaves is considered once.','Count pairs whose shortest path contains at most distance edges.'],[([[1,2,3,None,4],3],'Leaves four and three are three edges apart, so they form one good pair.'),([[1,2,3,4,5,6,7],2],'Sibling leaf pairs four-five and six-seven are the only pairs within two edges.')],[[t,d] for t,d in [([1],1),([1,2],1),([1,2,3],2),([1,2,3,None,4],3),([1,2,3,4,5,6,7],2),([1,2,3,4,5,6,7],3),([1,2,None,3,None,4],3),([1,None,2,None,3],4),([1,2,3,4,None,None,5],4),([0,-1,1,-2,None,None,2],3),([1,2,3,4,5],4),([1,2,3,None,4,None,5],5),([9,8,7,6,5,4,3],6),([1,2,3,4,None,5,None,6],4)]],LEAVES,[LEAVES.replace('a+b<=distance','a+b<distance'),LEAVES.replace('return [1]','return [0]')],['Uses a strict distance bound and loses pairs exactly at the limit.','Measures each leaf as distance zero from its parent, undercounting every path.'],leaf_o,rleaf,['Return the distances from the current node to leaves in its subtree.','Pairs whose lowest common ancestor is current combine one left and one right distance.','Count sums within the limit, then increment distances when returning upward and prune those already too large.','Every leaf pair has one unique lowest common ancestor, so it is counted exactly once.'],'O(n*distance²)','O(n*distance)',5),
}
BATCH[1520]['comparator']='unordered'
BATCH[1530]['params'][0]=('root','TreeNode | None','treenode')
