"""Preorder validation, alternating differences, marble moves, power partitions, and black blocks batch 181."""
from functools import lru_cache
from .import_batch_055 import entry

def preorder_oracle(a):
 nodes=a[0];parents={node:parent for node,parent in nodes};root=nodes[0][0]
 if nodes[0][1]!=-1 or any(parent!=-1 and parent not in parents for _,parent in nodes):return False
 children={node:[] for node,_ in nodes}
 for node,parent in nodes:
  if parent!=-1:children[parent].append(node)
 target=[node for node,_ in nodes]
 def orders(node):
  if not children[node]:return [[node]]
  out=[]
  from itertools import permutations,product
  for sequence in permutations(children[node]):
   for pieces in product(*(orders(child) for child in sequence)):out.append([node]+sum((list(p) for p in pieces),[]))
  return out
 return target in orders(root)
def random_preorder(r):
 n=r.randint(1,7);parents=[-1]+[r.randrange(i) for i in range(1,n)];order=list(range(n));r.shuffle(order);return [[[node,parents[node]] for node in order]]
def alternate_oracle(a):
 nums=a[0];return max((j-i for i in range(len(nums)) for j in range(i+2,len(nums)+1) if all(nums[k]-nums[k-1]==(1 if (k-i)%2 else -1) for k in range(i+1,j))),default=-1)
def random_alternate(r):return [[r.randint(0,12) for _ in range(r.randint(2,30))]]
def marbles_oracle(a):
 nums,moveFrom,moveTo=a;places=set(nums)
 for old,new in zip(moveFrom,moveTo):places.remove(old);places.add(new)
 return sorted(places)
def random_marbles(r):
 places=set(r.sample(range(1,30),r.randint(1,8)));initial=list(places);old=[];new=[]
 for _ in range(r.randint(1,8)):
  source=r.choice(tuple(places));target=r.randint(1,35);old.append(source);new.append(target);places.remove(source);places.add(target)
 return [initial,old,new]
def partition_oracle(a):
 s=a[0];powers={bin(5**i)[2:] for i in range(10)};best=99
 for mask in range(1<<(len(s)-1)):
  parts=[];start=0
  for i in range(len(s)-1):
   if mask>>i&1:parts.append(s[start:i+1]);start=i+1
  parts.append(s[start:])
  if all(part in powers for part in parts):best=min(best,len(parts))
 return -1 if best==99 else best
def random_partition(r):return [''.join(r.choice('01') for _ in range(r.randint(1,12)))]
def blocks_oracle(a):
 m,n,coordinates=a;black={tuple(x) for x in coordinates};answer=[0]*5
 for row in range(m-1):
  for col in range(n-1):answer[sum((row+dr,col+dc) in black for dr in (0,1) for dc in (0,1))]+=1
 return answer
def random_blocks(r):
 m,n=r.randint(2,8),r.randint(2,8);cells=[(i,j) for i in range(m) for j in range(n)];return [m,n,[list(x) for x in r.sample(cells,r.randint(0,min(len(cells),15)))]]

PRE='''\
def is_valid_tree_preorder(nodes):
    stack=[]
    for node,parent in nodes:
        if parent==-1:
            if stack:return False
            stack=[node];continue
        while stack and stack[-1]!=parent:stack.pop()
        if not stack:return False
        stack.append(node)
    return bool(stack)
'''
ALT='''\
def longest_plus_minus_alternating_subarray(nums):
    answer=-1;length=1
    for index in range(1,len(nums)):
        difference=nums[index]-nums[index-1]
        if difference==1:length=length+1 if length%2==1 else 2
        elif difference==-1 and length%2==0:length+=1
        else:length=1
        if length>=2:answer=max(answer,length)
    return answer
'''
MARBLES='''\
def final_marble_positions(nums,moveFrom,moveTo):
    positions=set(nums)
    for source,target in zip(moveFrom,moveTo):positions.remove(source);positions.add(target)
    return sorted(positions)
'''
PART='''\
def minimum_power_of_five_partitions(s):
    powers={bin(5**power)[2:] for power in range(22)}
    dp=[float('inf')]*(len(s)+1);dp[0]=0
    for end in range(1,len(s)+1):
        for start in range(end):
            if s[start:end] in powers:dp[end]=min(dp[end],dp[start]+1)
    return -1 if dp[-1]==float('inf') else dp[-1]
'''
BLOCKS='''\
def count_black_two_by_two_blocks(m,n,coordinates):
    black={tuple(cell) for cell in coordinates};counts={}
    for row,column in black:
        for top in (row-1,row):
            for left in (column-1,column):
                if 0<=top<m-1 and 0<=left<n-1:counts[(top,left)]=counts.get((top,left),0)+1
    answer=[0]*5
    for value in counts.values():answer[value]+=1
    answer[0]=(m-1)*(n-1)-len(counts)
    return answer
'''
BATCH={
2764:entry('is_valid_tree_preorder',[('nodes','list[list[int]]')],'bool',['trees','arrays','stacks'],['Each pair is [node,parent], with parent -1 only for the root.','Determine whether the listed node order can be a preorder traversal of the described rooted binary tree.','Return false when a parent is not an active ancestor at its child’s position.'],[([[[0,-1],[1,0],[2,0],[3,2],[4,2]]],'After finishing node one, preorder returns to root zero before entering node two and its children.'),([[[0,-1],[1,0],[2,1],[3,0],[4,2]]],'Node four names two as parent after traversal already left two, so the order is invalid.')],[[x] for x in [[[0,-1]],[[0,-1],[1,0]],[[0,-1],[1,0],[2,0]],[[0,-1],[1,0],[2,0],[3,2],[4,2]],[[0,-1],[1,0],[2,1],[3,0]],[[0,-1],[2,1]],[[1,-1],[0,1]],[[0,-1],[1,0],[2,1],[3,2]],[[0,-1],[1,0],[2,1],[3,0],[4,3]],[[0,-1],[1,0],[2,0],[3,1]],[[0,-1],[1,0],[2,1],[3,1]],[[0,-1],[1,0],[2,-1]],[[0,1],[1,-1]],[[0,-1],[1,0],[2,1],[3,2],[4,0]]]],PRE,[PRE.replace('while stack and stack[-1]!=parent','while stack and stack[-1]==parent'),PRE.replace('if stack:return False','if False:return False')],['Pops while the correct parent is on top instead of while searching for it.','Allows a second root to restart traversal.'],preorder_oracle,random_preorder,['Preorder keeps the current root-to-node ancestor path.','Maintain that path as a stack.','Before a non-root node, pop completed subtrees until its parent is on top; fail if absent.','A node may appear next exactly when its parent remains an active ancestor, which the stack represents.'],'O(n)','O(height)',5),
2765:entry('longest_plus_minus_alternating_subarray',[('nums','list[int]')],'int',['arrays','dynamic programming'],['A qualifying subarray has length at least two.','Its consecutive differences must be +1,-1,+1,-1 and so on, beginning with +1.','Return the maximum length, or -1 when none exists.'],[([[2,3,4,3,4]],'The suffix 3,4,3,4 has differences +1,-1,+1 and length four.'),([[4,3,2]],'No adjacent pair begins with a +1 difference, so return -1.')],[[x] for x in [[1,2],[2,1],[2,3,4,3,4],[4,3,2],[1,2,1],[1,2,1,2],[3,4,3,4,5],[0,1,0,1,0],[5,6,5,7],[2,3,2,1],[1,1,2],[9,10,9,10],[3,2,3,2],[7,8,7,8,7,9]]],ALT,[ALT.replace('difference==1','difference==-1',1),ALT.replace('length%2==0','length%2==1')],['Starts the alternating pattern with -1 instead of +1.','Extends a -1 step at the wrong parity.'],alternate_oracle,random_alternate,['Track the longest valid suffix.','A +1 step starts length two or extends only after an odd-length suffix; a -1 step extends only after even length.','Reset otherwise and record lengths at least two.','The expected next sign is determined entirely by suffix parity, so the recurrence preserves exactly the longest valid ending here.'],'O(n)','O(1)',5),
2766:entry('final_marble_positions',[('nums','list[int]'),('moveFrom','list[int]'),('moveTo','list[int]')],'list[int]',['arrays','hash maps','simulation'],['A marble exists at every distinct position in nums.','For each operation, move every marble at moveFrom[i] to moveTo[i]; the source is guaranteed occupied.','Return the distinct occupied positions in increasing order.'],[([[1,6,7,8],[1,7,2],[2,9,5]],'Moves produce occupied positions five, six, eight, and nine.'),([[1,2],[1],[2]],'Moving onto an occupied position merges occupancy, leaving only position two.')],[[a,b,c] for a,b,c in [([1],[1],[2]),([1,2],[1],[2]),([1,6,7,8],[1,7,2],[2,9,5]),([1,2,3],[2],[5]),([5,10],[5,10],[10,15]),([1,3],[1,3],[2,4]),([2,4,6],[2,4],[4,6]),([9],[9],[9]),([1,5,9],[5],[1]),([3,7,11],[3,7,11],[4,8,12]),([1,2,4],[4,2],[2,3]),([10,20],[10],[30]),([2,8,12],[8,2],[12,5]),([1,4,7,10],[1,4,7],[4,7,13])]],MARBLES,[MARBLES.replace('positions.remove(source)','positions.discard(target)'),MARBLES.replace('return sorted(positions)','return list(positions)')],['Removes the destination rather than the occupied source.','Returns hash-set iteration order instead of increasing order.'],marbles_oracle,random_marbles,['A set models distinct occupied positions and naturally merges moves onto occupied destinations.','For each move, remove its source and add its destination.','Sort the final set.','Each operation changes exactly those two occupancy facts, so induction matches the marble configuration after every move.'],'O((n+m) log n)','O(n)',3),
2767:entry('minimum_power_of_five_partitions',[('s','str')],'int',['strings','dynamic programming','recursion'],['Partition the binary string into nonempty contiguous substrings.','Every part must have no leading zero and represent a positive power of five.','Return the minimum part count, or -1 if impossible.'],[(['1011'],'Split as 101 and 1, representing five and one, so two parts suffice.'),(['0'],'A leading-zero part is forbidden, so no partition exists.')],[[s] for s in ['1','0','101','1011','111','11001','101101','10','1001','11001101','1111101','10101','001','10111001']],PART,[PART.replace('dp[0]=0','dp[0]=1'),PART.replace('for start in range(end)','for start in range(1,end)')],['Starts with one part before consuming any characters.','Never permits a valid part beginning at index zero.'],partition_oracle,random_partition,['Precompute binary representations of powers of five.','Let dp[i] be the fewest valid parts covering the first i bits.','For every end, test all earlier starts whose substring is a power representation.','Every partition has a unique final cut, so minimizing over valid final parts exhausts all solutions.'],'O(n²)','O(n)',8),
2768:entry('count_black_two_by_two_blocks',[('m','int'),('n','int'),('coordinates','list[list[int]]')],'list[int]',['matrices','hash maps','counting'],['An m by n grid contains black cells at the distinct coordinates; all others are white.','For k from zero through four, count 2-by-2 blocks containing exactly k black cells.','Return the five counts in that order.'],[([3,3,[[0,0]]],'The black corner belongs to one block; the other three blocks contain zero black cells, giving [3,1,0,0,0].'),([2,2,[[0,0],[1,1]]],'The only 2-by-2 block contains exactly two black cells.')],[[m,n,c] for m,n,c in [(2,2,[]),(2,2,[[0,0]]),(2,2,[[0,0],[1,1]]),(2,2,[[0,0],[0,1],[1,0],[1,1]]),(3,3,[[0,0]]),(3,3,[[1,1]]),(3,4,[[0,1],[1,2]]),(4,4,[[1,1],[1,2],[2,1],[2,2]]),(2,5,[[0,2]]),(5,2,[[3,1]]),(4,5,[[0,0],[3,4]]),(3,3,[[0,1],[1,0]]),(5,5,[[2,2],[2,3],[3,2]]),(4,3,[[0,0],[1,1],[2,2],[3,1]])]],BLOCKS,[BLOCKS.replace('0<=top<m-1','0<top<m-1'),BLOCKS.replace('-len(counts)','-sum(counts.values())')],['Excludes valid 2-by-2 blocks whose top row is zero.','Subtracts black incidences rather than the number of nonzero blocks when counting empty blocks.'],blocks_oracle,random_blocks,['Each black cell affects at most four neighboring 2-by-2 blocks.','Count black incidences keyed by valid block top-left coordinates.','Bucket nonzero block counts and derive zero blocks from total blocks minus touched blocks.','Every black cell contributes once to each containing block, so the stored incidence is exactly that block’s black-cell count.'],'O(b)','O(b)',5),
}
