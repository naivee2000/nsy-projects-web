"""Distinct tree paths, direction counting, XOR grids, digit-sum arrays, and rotations."""
from functools import lru_cache
from itertools import product
from .import_batch_055 import entry

MOD=1_000_000_007

def tree_graph(values):
    if not values:return [],[]
    nodes=[];edges=[];queue=[];cursor=0
    if values[0] is None:return [],[]
    nodes.append(values[0]);edges.append([]);queue=[0];cursor=1
    while queue and cursor<len(values):
        parent=queue.pop(0)
        for _ in range(2):
            if cursor>=len(values):break
            value=values[cursor];cursor+=1
            if value is not None:
                child=len(nodes);nodes.append(value);edges.append([]);edges[parent].append(child);edges[child].append(parent);queue.append(child)
    return nodes,edges
def tree_oracle(args):
    values,edges=tree_graph(args[0]);best=-10**30
    def walk(node,parent,seen,total):
        nonlocal best
        if values[node] in seen:return
        seen=seen|{values[node]};total+=values[node];best=max(best,total)
        for nxt in edges[node]:
            if nxt!=parent:walk(nxt,node,seen,total)
    for start in range(len(values)):walk(start,-1,set(),0)
    return best
def random_tree(rng):return [[rng.randint(-10,20) for _ in range(rng.randint(1,11))]]

def direction_oracle(args):
    n,pos,k=args;answer=0
    for choices in product((0,1),repeat=n):
        visible=sum(choices[i]==0 for i in range(pos))+sum(choices[i]==1 for i in range(pos+1,n))
        answer+=visible==k
    return answer%MOD
def random_direction(rng):
    n=rng.randint(1,16);return [n,rng.randrange(n),rng.randint(0,n)]

def xor_oracle(args):
    grid=args[0];best=10**30
    def walk(row,column,value):
        nonlocal best
        value^=grid[row][column]
        if row==len(grid)-1 and column==len(grid[0])-1:best=min(best,value);return
        if row+1<len(grid):walk(row+1,column,value)
        if column+1<len(grid[0]):walk(row,column+1,value)
    walk(0,0,0);return best
def random_xor(rng):
    rows=rng.randint(1,5);columns=rng.randint(1,5);return [[[rng.randint(0,63) for _ in range(columns)] for _ in range(rows)]]

@lru_cache(None)
def values_with_sum(total):return tuple(value for value in range(5001) if sum(map(int,str(value)))==total)
def digits_oracle(args):
    sums=args[0]
    @lru_cache(None)
    def count(index,minimum):
        if index==len(sums):return 1
        return sum(count(index+1,value) for value in values_with_sum(sums[index]) if value>=minimum)%MOD
    return count(0,0)
def random_digits(rng):return [[rng.choice((0,1,2,3,25,30,35,40)) for _ in range(rng.randint(1,4))]]

def rotations(values):return [values[i:]+values[:i] for i in range(len(values))]
def sortable_oracle(args):
    nums=args[0];target=sorted(nums);answer=0
    for size in range(1,len(nums)+1):
        if len(nums)%size:continue
        choices=[rotations(nums[i:i+size]) for i in range(0,len(nums),size)]
        if any([item for block in selected for item in block]==target for selected in product(*choices)):answer+=size
    return answer
def random_sortable(rng):return [[rng.randint(0,8) for _ in range(rng.randint(1,8))]]

TREE='''def maximum_distinct_tree_path_sum(root):
    graph={}
    def build(node,parent):
        if node is None:return
        graph.setdefault(node,[])
        if parent is not None:graph[node].append(parent);graph[parent].append(node)
        build(node.left,node);build(node.right,node)
    build(root,None);answer=-10**30
    def walk(node,parent,seen,total):
        nonlocal answer
        if node.val in seen:return
        seen.add(node.val);total+=node.val;answer=max(answer,total)
        for nxt in graph[node]:
            if nxt is not parent:walk(nxt,node,seen,total)
        seen.remove(node.val)
    for node in graph:walk(node,None,set(),0)
    return answer
'''

DIRECTION='''def count_direction_assignments(n,pos,k):
    if k<0 or k>n-1:return 0
    modulus=1_000_000_007
    choose=1
    for value in range(1,k+1):choose=choose*(n-value)//value
    return 2*choose%modulus
'''

XOR='''def minimum_grid_path_xor(grid):
    states=[[set() for _ in row] for row in grid];states[0][0].add(grid[0][0])
    for row in range(len(grid)):
        for column in range(len(grid[0])):
            if row==0 and column==0:continue
            previous=set()
            if row:previous|=states[row-1][column]
            if column:previous|=states[row][column-1]
            states[row][column]={value^grid[row][column] for value in previous}
    return min(states[-1][-1])
'''

DIGITS='''def count_nondecreasing_digit_sum_arrays(digit_sum):
    modulus=1_000_000_007
    groups=[[] for _ in range(46)]
    for value in range(5001):groups[sum(map(int,str(value)))].append(value)
    previous=[0]*5001
    for value in groups[digit_sum[0]]:previous[value]=1
    for required in digit_sum[1:]:
        prefix=[0]*5001;running=0
        for value in range(5001):
            running=(running+previous[value])%modulus;prefix[value]=running
        current=[0]*5001
        for value in groups[required]:current[value]=prefix[value]
        previous=current
    return sum(previous)%modulus
'''

SORTABLE='''def sum_sortable_block_sizes(nums):
    target=sorted(nums)
    def rotation_equal(source,wanted):
        if not source:return True
        pattern=wanted;prefix=[0]*len(pattern)
        for i in range(1,len(pattern)):
            j=prefix[i-1]
            while j and pattern[i]!=pattern[j]:j=prefix[j-1]
            if pattern[i]==pattern[j]:j+=1
            prefix[i]=j
        matched=0
        for value in (source+source)[:-1]:
            while matched and value!=pattern[matched]:matched=prefix[matched-1]
            if value==pattern[matched]:matched+=1
            if matched==len(pattern):return True
        return False
    answer=0
    for size in range(1,len(nums)+1):
        if len(nums)%size==0 and all(rotation_equal(nums[i:i+size],target[i:i+size]) for i in range(0,len(nums),size)):answer+=size
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]
T_CASES=[[v] for v in ([2,2,1],[1],[-5],[1,2,3],[1,1,1],[5,3,7,2,4,6,8],[2,3,2],[10,5,15,None,7],[-1,-2,-3],[4,2,6,2,3,5,7],[8,4,12,2,6,10,14],[1,2,3,4,None,None,5],[5,1,5,2,3,4,6],[7,3,9,1,5,8,10],[0,-1,2,-3,None,1,4])]
D_CASES=[[n,p,k] for n,p,k in ((3,1,0),(1,0,0),(2,0,0),(2,1,1),(3,0,1),(3,2,2),(4,1,2),(4,2,1),(5,0,4),(5,4,0),(6,3,3),(7,2,5),(8,7,4),(10,5,9),(12,4,6))]
X_CASES=[[[*rows]] for rows in ([[1,2],[3,4]],[[0]],[[1,2]],[[1],[2]],[[1,2,3],[4,5,6]],[[7,3],[2,5],[1,4]],[[0,1],[1,0]],[[8,4,2],[1,3,7]],[[5,5],[5,5]],[[1,0,1],[0,1,0]],[[31,1],[2,16]],[[2,4,8],[16,32,1]],[[3,6,9],[12,15,18]],[[0,7,0],[7,0,7]],[[10,20],[30,40],[50,60]])]
N_CASES=[[[*v]] for v in ([25,1],[0],[1],[2],[25],[1,1],[1,2],[2,1],[3,3],[0,1],[1,0],[25,2],[30,1],[1,1,1],[40,0])]
S_CASES=[[[*v]] for v in ([3,1,2],[1],[2,1],[1,2],[3,2,1],[2,1,4,3],[1,1,1],[2,3,1,4],[4,1,3,2],[3,1,2,6,4,5],[5,4,3,2,1,0],[1,3,2,4,6,5],[2,2,1,1],[7,1,4,2,6,3],[0,2,1,3])]

BATCH={
3879:entry('maximum_distinct_tree_path_sum',[('root','TreeNode | None')],'int',['trees','depth-first search','hash sets'],['The tree is nonempty and node values may be negative.','A path may start and end at any nodes connected through parent-child edges.','All values on the path must be distinct; maximize their sum.'],[([[2,2,1]],'The path from the root value two to the right child value one has distinct values and sum three.'),([[-5]],'The only path contains the single value -5, so the answer is -5.')],T_CASES,TREE,[TREE.replace('if node.val in seen:return','if node.val in seen:answer=max(answer,total+node.val);return'),TREE.replace('answer=max(answer,total)','answer=max(answer,node.val)')],['Counts the first repeated-value node before stopping the path.','Tracks only individual node values instead of accumulated path sums.'],tree_oracle,random_tree,lesson('A tree path can be explored from each possible starting node in the undirected parent-child graph.','Maintain a set of values currently on the DFS path and stop before repeating one.','Accumulate the sum and update the maximum at every reached node, including negative-only paths.','Every simple path has one endpoint that serves as a start; DFS visits it once until a duplicate would invalidate it.'),'O(n²)','O(n)',6),
3881:entry('count_direction_assignments',[('n','int'),('pos','int'),('k','int')],'int',['combinatorics','math'],['There are n indexed people, 0≤pos<n, and each independently faces L or R.','Left-side people are visible from pos exactly when facing L; right-side people exactly when facing R.','Count assignments with exactly k visible people modulo 1,000,000,007; pos’s own direction is free.'],[([3,1,0],'Both other people must face away, while the person at pos has two choices, giving two.'),([1,0,0],'No other people exist and the sole direction is free, giving two.')],D_CASES,DIRECTION,[DIRECTION.replace('return 2*choose','return choose'),DIRECTION.replace('n-value','n-1-value')],['Forgets the two independent direction choices of the person at pos.','Computes the binomial coefficient from n-2 rather than n-1 other people.'],direction_oracle,random_direction,lesson('Each of the n-1 other people independently has exactly one direction that makes them visible.','Choose which k other people are visible, then multiply by two for pos’s unrestricted direction.','Compute C(n-1,k) multiplicatively and reduce the final result modulo the required prime.','Every assignment corresponds uniquely to its visible subset and pos direction, proving 2·C(n-1,k).'),'O(k)','O(1)',5),
3882:entry('minimum_grid_path_xor',[('grid','list[list[int]]')],'int',['matrices','dynamic programming','bit manipulation'],['grid is a nonempty rectangular matrix of nonnegative integers.','Move only right or down from the top-left to bottom-right cell.','XOR every visited cell and return the minimum path value.'],[([[[1,2],[3,4]]],'The right-down path has XOR 1^2^4=7; down-right has 1^3^4=6, so return six.'),([[[0]]],'The only path contains zero and has XOR zero.')],X_CASES,XOR,[XOR.replace('previous|=states[row][column-1]','previous=states[row][column-1]'),XOR.replace('return min','return max')],['When both predecessors exist, discards all paths arriving from above.','Returns the maximum reachable XOR rather than the minimum.'],xor_oracle,random_xor,lesson('One cell can be reached with multiple XOR values, and only retaining the smallest intermediate value is unsafe.','Store the full set of reachable XORs per cell.','Union predecessor sets, XOR each value with the current cell, and take the minimum only at the destination.','Every monotone path ends from above or left, so the recurrence enumerates exactly all path XOR values.'),'O(mnU)','O(mnU)',6),
3883:entry('count_nondecreasing_digit_sum_arrays',[('digitSum','list[int]')],'int',['arrays','dynamic programming','prefix sums'],['digitSum is nonempty and each value is between 0 and 45.','Choose arr[i] in [0,5000] with decimal digit sum digitSum[i].','Count nondecreasing arrays arr modulo 1,000,000,007.'],[([[25,1]],'Exactly six qualifying first values with digit sum 25 do not exceed the available second values with digit sum one.'),([[0]],'Only value zero has digit sum zero, so there is one array.')],N_CASES,DIGITS,[DIGITS.replace('running+previous[value]','running-previous[value]'),DIGITS.replace('current[value]=prefix[value]','current[value]=prefix[value-1] if value else 0')],['Subtracts prior counts while building the prefix transition.','Requires the previous value to be strictly smaller instead of allowing equality.'],digits_oracle,random_digits,lesson('Group every allowed integer by its digit sum once.','Process positions left to right; for each possible current value, sum counts ending at values no greater than it.','A prefix-sum array makes every such transition constant time.','The DP chooses exactly the required digit-sum group and its prefix transition enforces nondecreasing order, counting each array once.'),'O(nV)','O(V)',8),
3886:entry('sum_sortable_block_sizes',[('nums','list[int]')],'int',['arrays','sorting','string matching'],['nums is nonempty.','For a divisor k of n, split nums into blocks of length k and rotate each block independently.','Sum every k for which these rotations can make the whole array nondecreasing.'],[([[3,1,2]],'Only block size three works: rotate to [1,2,3], so the sum is three.'),([[1,2]],'Sizes one and two both work, contributing three.')],S_CASES,SORTABLE,[SORTABLE.replace('target=sorted(nums)','target=nums'),SORTABLE.replace('answer+=size','answer+=1')],['Compares rotations against the unsorted input instead of the required sorted target.','Counts valid block sizes rather than summing their values.'],sortable_oracle,random_sortable,lesson('The final nondecreasing array is uniquely sorted(nums).','For each divisor k, every source block must independently be a cyclic rotation of the corresponding target block.','Test rotation equality by searching the target block in source+source with a prefix-function matcher.','Blocks cannot exchange elements, so the per-block rotation condition is both necessary and sufficient; summing passing divisors gives the answer.'),'O(nτ(n))','O(n)',8),
}
BATCH[3879]['params'][0]=('root','TreeNode | None','treenode')
