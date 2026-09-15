"""Boolean trees, XOR tree cuts, assignment, and divisor-count imports."""
from itertools import combinations, permutations, product
from math import comb

from .import_batch_055 import entry


class Node:
    def __init__(self, value, left=None, right=None):self.val=value;self.left=left;self.right=right


def make_tree(values):
    if not values:return None
    nodes=[None if value is None else Node(value) for value in values]
    children=iter(nodes[1:])
    for node in nodes:
        if node is None:continue
        node.left=next(children,None);node.right=next(children,None)
    return nodes[0]


def flips_oracle(args):
    root=make_tree(args[0]);desired=args[1];leaves=[]
    def collect(node):
        if node.left is None and node.right is None:leaves.append(node);return
        if node.left:collect(node.left)
        if node.right:collect(node.right)
    collect(root);original=[node.val for node in leaves];best=len(leaves)+1
    def evaluate(node):
        if node.left is None and node.right is None:return bool(node.val)
        left=evaluate(node.left) if node.left else False
        if node.val==5:return not left
        right=evaluate(node.right)
        return left or right if node.val==2 else left and right if node.val==3 else left!=right
    for bits in product((0,1),repeat=len(leaves)):
        for node,value in zip(leaves,bits):node.val=value
        if evaluate(root)==desired:best=min(best,sum(a!=b for a,b in zip(bits,original)))
    for node,value in zip(leaves,original):node.val=value
    return best


def random_flips(rng):
    # Complete depth-two trees keep exhaustive leaf enumeration inexpensive.
    root=rng.choice([2,3,4]);left=rng.choice([2,3,4,5]);right=rng.choice([2,3,4,5])
    values=[root,left,right]
    for operation in (left,right):
        if operation==5:values.extend([rng.randrange(2),None])
        else:values.extend([rng.randrange(2),rng.randrange(2)])
    return [values,bool(rng.randrange(2))]


def score_oracle(args):
    nums,edges=args;size=len(nums);best=float('inf')
    for removed in combinations(range(len(edges)),2):
        graph=[[] for _ in range(size)]
        for index,(left,right) in enumerate(edges):
            if index not in removed:graph[left].append(right);graph[right].append(left)
        seen=set();values=[]
        for start in range(size):
            if start in seen:continue
            stack=[start];seen.add(start);value=0
            while stack:
                node=stack.pop();value^=nums[node]
                for neighbor in graph[node]:
                    if neighbor not in seen:seen.add(neighbor);stack.append(neighbor)
            values.append(value)
        best=min(best,max(values)-min(values))
    return best


def random_score(rng):
    size=rng.randint(3,9);edges=[[node,rng.randrange(node)] for node in range(1,size)]
    rng.shuffle(edges)
    return [[rng.randint(0,31) for _ in range(size)],edges]


def jobs_oracle(args):
    jobs,workers=args
    return min(max((job+worker-1)//worker for job,worker in zip(jobs,order)) for order in permutations(workers))


def random_jobs(rng):
    size=rng.randint(1,7)
    return [[rng.randint(1,30) for _ in range(size)],[rng.randint(1,12) for _ in range(size)]]


def evaluate_oracle(args):
    def visit(node):
        if node.left is None:return bool(node.val)
        left,right=visit(node.left),visit(node.right)
        return left or right if node.val==2 else left and right
    return visit(make_tree(args[0]))


def random_evaluate(rng):
    return [[rng.choice([2,3]),rng.choice([2,3]),rng.choice([2,3]),rng.randrange(2),rng.randrange(2),rng.randrange(2),rng.randrange(2)]]


def ideal_oracle(args):
    length,maximum=args;count=0
    def visit(prefix):
        nonlocal count
        if len(prefix)==length:count+=1;return
        start=1 if not prefix else prefix[-1]
        for value in range(start,maximum+1):
            if not prefix or value%prefix[-1]==0:visit(prefix+[value])
    visit([]);return count%1_000_000_007


def random_ideal(rng):return [rng.randint(1,5),rng.randint(1,12)]


FLIPS='''def minimum_boolean_tree_flips(root,result):
    inf=10**9
    def visit(node):
        if node.left is None and node.right is None:return (node.val,1-node.val)
        left=visit(node.left) if node.left else (0,inf)
        if node.val==5:return (left[1],left[0])
        right=visit(node.right)
        false=true=inf
        for a in (0,1):
            for b in (0,1):
                value=a|b if node.val==2 else a&b if node.val==3 else a^b
                cost=left[a]+right[b]
                if value:false=min(false,inf);true=min(true,cost)
                else:false=min(false,cost)
        return false,true
    return visit(root)[int(result)]
'''

SCORE='''def minimum_tree_xor_score(nums,edges):
    import sys
    sys.setrecursionlimit(10000);n=len(nums);graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    parent=[-1]*n;tin=[0]*n;tout=[0]*n;subtree=[0]*n;clock=0
    def dfs(node,previous):
        nonlocal clock
        parent[node]=previous;tin[node]=clock;clock+=1;value=nums[node]
        for child in graph[node]:
            if child!=previous:dfs(child,node);value^=subtree[child]
        subtree[node]=value;tout[node]=clock
    dfs(0,-1);total=subtree[0];answer=float('inf')
    nodes=range(1,n)
    for first in nodes:
        for second in range(first+1,n):
            if tin[first]<=tin[second]<tout[first]:parts=(subtree[second],subtree[first]^subtree[second],total^subtree[first])
            elif tin[second]<=tin[first]<tout[second]:parts=(subtree[first],subtree[second]^subtree[first],total^subtree[second])
            else:parts=(subtree[first],subtree[second],total^subtree[first]^subtree[second])
            answer=min(answer,max(parts)-min(parts))
    return answer
'''

JOBS='''def minimum_job_days(jobs,workers):
    jobs=sorted(jobs);workers=sorted(workers)
    return max((job+worker-1)//worker for job,worker in zip(jobs,workers))
'''

EVALUATE='''def evaluate_boolean_tree(root):
    if root.left is None:return bool(root.val)
    left=evaluate_boolean_tree(root.left);right=evaluate_boolean_tree(root.right)
    return left or right if root.val==2 else left and right
'''

IDEAL='''def count_ideal_arrays(n,max_value):
    mod=1000000007;answer=0
    for value in range(1,max_value+1):
        remaining=value;ways=1;factor=2
        while factor*factor<=remaining:
            exponent=0
            while remaining%factor==0:remaining//=factor;exponent+=1
            if exponent:ways=ways*__import__('math').comb(n-1+exponent,exponent)%mod
            factor+=1
        if remaining>1:ways=ways*n%mod
        answer=(answer+ways)%mod
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
2313:entry('minimum_boolean_tree_flips',[('root','TreeNode'),('result','bool')],'int',['trees','dynamic programming','recursion'],['Leaves contain zero or one; internal nodes use 2=OR, 3=AND, 4=XOR, and unary 5=NOT.','One operation flips one leaf value.','Return the minimum flips needed for the root to evaluate to result.'],[([[3,5,4,2,None,1,1,1,0],True],'The cheapest assignment flips two leaves so the AND root becomes true.'),([[2,0,1],False],'The OR root is currently true; flipping its sole true leaf makes it false in one operation.')],[[t,r] for t,r in [([0],False),([0],True),([1],False),([1],True),([2,0,0],True),([2,0,1],True),([3,1,1],False),([3,1,0],True),([4,1,0],True),([4,1,1],True),([5,0],True),([5,1],True),([2,3,4,1,0,1,0],False),([3,2,5,0,1,0],True)]],FLIPS,[FLIPS.replace('left[1],left[0]','left[0],left[1]'),FLIPS.replace('a^b','a&b')],['Treats NOT as an identity operation.','Evaluates XOR as AND.'],flips_oracle,random_flips,lesson('Each subtree needs two answers: cost to make it false and cost to make it true.','Combine child target values through the node’s truth table.','Leaves cost zero for their current value and one for the opposite; internal nodes minimize child-cost sums for each possible result.','Truth-table enumeration considers every child-result assignment, while subtree independence lets their minimum costs add.'),'O(nodes)','O(height)',8),
2322:entry('minimum_tree_xor_score',[('nums','list[int]'),('edges','list[list[int]]')],'int',['trees','depth-first search','bit manipulation'],['nums has 3 through 1000 values and edges form a zero-indexed tree.','Remove two distinct edges; XOR node values within each of the resulting three components.','Minimize maximum component XOR minus minimum component XOR.'],[([[1,5,5,4,11],[[0,1],[1,2],[1,3],[3,4]]],'The best pair of cuts produces component XOR values whose range is nine.'),([[5,5,2,4,4,2],[[0,1],[1,2],[5,2],[4,3],[1,3]]],'Choosing the optimal two edges makes all three component XOR values equal, so the score is zero.')],[[n,e] for n,e in [([1,2,3],[[0,1],[1,2]]),([1,1,1],[[0,1],[0,2]]),([0,0,0],[[0,1],[1,2]]),([1,2,4,8],[[0,1],[1,2],[2,3]]),([1,2,4,8],[[0,1],[0,2],[0,3]]),([7,7,7,7],[[0,1],[1,2],[2,3]]),([3,1,4,1,5],[[0,1],[0,2],[2,3],[2,4]]),([31,1,2,3,4],[[0,1],[1,2],[1,3],[3,4]]),([2,4,6,8,10,12],[[0,1],[1,2],[2,3],[3,4],[4,5]]),([1,2,3,4,5,6],[[0,1],[0,2],[0,3],[0,4],[0,5]]),([9,8,7,6,5],[[1,0],[2,1],[3,1],[4,3]]),([1,0,1,0,1],[[0,1],[1,2],[2,3],[3,4]]),([16,8,4,2,1],[[0,1],[0,2],[2,3],[2,4]]),([5,10,15,20,25,30],[[0,1],[1,2],[1,3],[3,4],[3,5]])]],SCORE,[SCORE.replace('total^subtree[first]^subtree[second]','total^subtree[first]'),SCORE.replace('max(parts)-min(parts)','max(parts)')],['For disjoint cut subtrees, forgets to remove the second subtree XOR from the remainder.','Minimizes only the maximum XOR instead of the range between maximum and minimum.'],score_oracle,random_score,lesson('Root the tree and compute every subtree XOR plus ancestor intervals.','Each removed edge corresponds to the child-side subtree below it.','For two cut nodes, use ancestor intervals to distinguish nested subtrees from disjoint subtrees and derive the three XORs.','Subtree XOR cancellation gives each component exactly; enumerating all cut-node pairs covers every pair of removed edges.'),'O(n²)','O(n)',8),
2323:entry('minimum_job_days',[('jobs','list[int]'),('workers','list[int]')],'int',['sorting','greedy','assignment'],['jobs and workers have equal length up to 100000; each positive worker capacity is work completed per day.','Assign exactly one job to each worker and one worker to each job.','Minimize the maximum ceiling(job_size/worker_capacity) across assignments.'],[([[5,2,4],[1,7,5]],'Pairing jobs and workers in sorted order finishes every job within two days.'),([[3,18,15,9],[6,5,1,3]],'Sorted pairing yields completion times three, three, three, and three, so the answer is three days.')],[[j,w] for j,w in [([1],[1]),([5],[2]),([1,2],[1,2]),([2,1],[1,2]),([10,1],[1,10]),([5,5],[2,3]),([1,2,3],[3,2,1]),([3,6,9],[1,2,3]),([4,8,12],[2,2,4]),([100,1,50],[10,1,5]),([7,11,13,17],[2,3,5,7]),([1,100,101],[1,99,100]),([9,9,1,1],[1,2,8,9]),([20,30,40,50],[2,3,4,5])]],JOBS,[JOBS.replace('workers=sorted(workers)','workers=sorted(workers,reverse=True)'),JOBS.replace('(job+worker-1)//worker','job//worker')],['Pairs the smallest job with the largest worker, leaving a poor bottleneck at the opposite end.','Uses floor division and undercounts jobs requiring a partial final day.'],jobs_oracle,random_jobs,lesson('For a proposed day limit, a worker can handle every job no larger than days*capacity.','Sorting both sides pairs their ranks and avoids crossing assignments.','Pair sorted jobs with sorted workers and take the maximum ceiling ratio.','If two assignments cross, swapping them into sorted order cannot worsen their larger completion ratio; repeated exchanges yield the sorted optimum.'),'O(n log n)','O(n)',5),
2331:entry('evaluate_boolean_tree',[('root','TreeNode')],'bool',['trees','recursion','boolean logic'],['The input is a full binary tree: leaves contain zero/one and internal nodes contain 2=OR or 3=AND.','Evaluate leaves as booleans and apply each internal operation to its two children.','Return the root result.'],[([[2,1,3,None,None,0,1]],'The right AND child is false, then true OR false makes the root true.'),([[3,1,0]],'True AND false evaluates to false.')],[[t] for t in [[0],[1],[2,0,0],[2,0,1],[2,1,1],[3,0,0],[3,0,1],[3,1,1],[2,2,3,0,1,1,1],[3,2,2,1,0,0,1],[2,3,3,1,1,1,0],[3,2,3,0,0,1,1],[2,2,2,1,0,1,0],[3,3,2,1,0,1,1]]],EVALUATE,[EVALUATE.replace('left or right','left and right'),EVALUATE.replace('left and right','left or right')],['Evaluates OR nodes as AND.','Evaluates AND nodes as OR.'],evaluate_oracle,random_evaluate,lesson('Leaves are the recursion base case.','Evaluate both child subtrees before applying the current node’s operator.','Return bool(value) at a leaf; otherwise return left OR right for two and left AND right for three.','Structural recursion mirrors the expression tree, so every operation receives exactly its recursively evaluated operands.'),'O(nodes)','O(height)',3),
2338:entry('count_ideal_arrays',[('n','int'),('max_value','int')],'int',['math','combinatorics','prime factorization'],['1 <= n <= 10000 and 1 <= max_value <= 10000.','Count length-n positive arrays with values at most max_value where every value divides the next.','Return the count modulo 1000000007.'],[([2,5],'The five constant arrays plus pairs 1-2, 1-3, 1-4, 1-5, and 2-4 give ten.'),([5,3],'Arrays using only one and a fixed number of later copies of two or three total eleven.')],[[n,m] for n,m in [(1,1),(1,5),(2,1),(2,2),(2,3),(3,2),(3,3),(3,4),(4,2),(4,5),(5,1),(5,4),(6,6),(8,10)]],IDEAL,[IDEAL.replace('ways=ways*__import__(\'math\').comb(n-1+exponent,exponent)%mod','ways=ways*(n**exponent)%mod'),IDEAL.replace('answer=(answer+ways)%mod','answer=ways')],['Places prime-factor increments independently into n choices but ignores combinations with repetition.','Overwrites the running total and returns only the contribution from max_value.'],ideal_oracle,random_ideal,lesson('Factor each possible final value into prime exponents.','For exponent e, distribute e indistinguishable multiplication events among n positions with combinations with repetition.','Multiply C(n-1+e,e) across prime factors, then sum over every final value.','Each divisibility chain is uniquely described by when each prime exponent first appears, and independent primes multiply their choices.'),'O(max_value*sqrt(max_value))','O(1) excluding arithmetic tables',8),
}
BATCH[2313]['params'][0]=('root','TreeNode','treenode')
BATCH[2331]['params'][0]=('root','TreeNode','treenode')
