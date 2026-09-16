"""Alternating XOR partitions, tree edge toggles, machine capacity, and deletion."""
from collections import Counter,deque
from itertools import combinations
from .import_batch_055 import entry


def xor_oracle(args):
    nums,first,second=args;answer=0;n=len(nums)
    for mask in range(1<<(n-1)):
        start=0;block=0;valid=True
        for end in range(n):
            block^=nums[end]
            if end==n-1 or mask>>end&1:
                expected=first if start%2==0 else second
                if block!=expected:valid=False;break
                start+=1;block=0
        answer+=valid
    return answer%1000000007
def random_xor(rng):
    n=rng.randint(1,10);first=rng.randint(0,15);second=rng.randint(0,15)
    if first==second:second^=1
    return [[rng.randint(0,15) for _ in range(n)],first,second]

def toggles_oracle(args):
    n,edges,start,target=args;needed=[int(a!=b) for a,b in zip(start,target)];best=None
    for mask in range(1<<(n-1)):
        colors=[0]*n;chosen=[]
        for index,(a,b) in enumerate(edges):
            if mask>>index&1:colors[a]^=1;colors[b]^=1;chosen.append(index)
        if colors==needed and (best is None or len(chosen)<len(best)):best=chosen
    return [-1] if best is None else best
def random_toggles(rng):
    n=rng.randint(2,9);edges=[[i,rng.randrange(i)] for i in range(1,n)]
    return [n,edges,''.join(rng.choice('01') for _ in range(n)),''.join(rng.choice('01') for _ in range(n))]

def capacity_oracle(args):
    costs,capacity,budget=args;answer=0
    for size in (1,2):
        for indices in combinations(range(len(costs)),size):
            if sum(costs[i] for i in indices)<budget:answer=max(answer,sum(capacity[i] for i in indices))
    return answer
def random_capacity(rng):
    n=rng.randint(1,15);return [[rng.randint(1,30) for _ in range(n)],[rng.randint(1,50) for _ in range(n)],rng.randint(1,50)]

def deletion_oracle(args):
    start=args[0];seen={start};queue=deque([start]);best=start
    while queue:
        value=queue.popleft();best=min(best,value);counts=Counter(value)
        for i,char in enumerate(value):
            if counts[char]>=2:
                nxt=value[:i]+value[i+1:]
                if nxt not in seen:seen.add(nxt);queue.append(nxt)
    return best
def random_deletion(rng):return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,10)))]


XOR='''def count_alternating_xor_partitions(nums,target1,target2):
    mod=1000000007;waiting_first={0:1};waiting_second={};prefix=0;answer=0
    for value in nums:
        prefix^=value
        make_first=waiting_first.get(prefix^target1,0)
        make_second=waiting_second.get(prefix^target2,0)
        answer=(make_first+make_second)%mod
        waiting_second[prefix]=(waiting_second.get(prefix,0)+make_first)%mod
        waiting_first[prefix]=(waiting_first.get(prefix,0)+make_second)%mod
    return answer
'''

TOGGLES='''def minimum_tree_edge_toggles(n,edges,start,target):
    graph=[[] for _ in range(n)]
    for index,(a,b) in enumerate(edges):graph[a].append((b,index));graph[b].append((a,index))
    parent=[-1]*n;parent_edge=[-1]*n;order=[0]
    for node in order:
        for child,index in graph[node]:
            if child!=parent[node]:parent[child]=node;parent_edge[child]=index;order.append(child)
    need=[start[i]!=target[i] for i in range(n)];answer=[]
    for node in reversed(order[1:]):
        if need[node]:
            answer.append(parent_edge[node]);need[parent[node]]=not need[parent[node]]
    return [-1] if need[0] else sorted(answer)
'''

CAPACITY='''def maximum_machine_capacity(costs,capacity,budget):
    from bisect import bisect_left
    items=sorted((costs[i],capacity[i],i) for i in range(len(costs)));ordered_cost=[item[0] for item in items]
    top=[];prefix=[]
    for cost,value,index in items:
        top=sorted(top+[(value,index)],reverse=True)[:2];prefix.append(top[:])
    answer=max((value for cost,value,_ in items if cost<budget),default=0)
    for cost,value,index in items:
        limit=bisect_left(ordered_cost,budget-cost)
        if not limit:continue
        candidates=prefix[limit-1]
        partner=next((other for other,other_index in candidates if other_index!=index),None)
        if partner is not None:answer=max(answer,value+partner)
    return answer
'''

DELETE='''def lexicographically_smallest_duplicate_deletion(s):
    from collections import Counter
    remaining=Counter(s);stack=[]
    for char in s:
        while stack and stack[-1]>char and remaining[stack[-1]]>1:
            removed=stack.pop();remaining[removed]-=1
        stack.append(char)
    while stack and remaining[stack[-1]]>1:
        removed=stack.pop();remaining[removed]-=1
    return ''.join(stack)
'''

def lesson(a,b,c,d):return [a,b,c,d]

X_CASES=[[a,b,c] for a,b,c in (([2,3,1,4],1,5),([1,0,0],1,0),([7],1,7),([1],1,0),([0],0,1),([1,1],1,0),([1,2,3],0,1),([0,0,0],0,1),([5,5,5,5],0,5),([1,0,1,0],1,0),([2,2,3,3],0,1),([7,1,6,2,4],6,7),([1,2,1,2,1],3,0),([0,1,0,1,0,1],1,0))]
T_CASES=[[n,e,s,t] for n,e,s,t in ((2,[[0,1]],'00','01'),(2,[[0,1]],'00','11'),(3,[[0,1],[1,2]],'010','100'),(3,[[0,1],[0,2]],'000','110'),(4,[[0,1],[1,2],[2,3]],'0000','1001'),(4,[[0,1],[0,2],[0,3]],'0101','1010'),(5,[[0,1],[1,2],[1,3],[3,4]],'00110','10101'),(5,[[0,1],[0,2],[2,3],[2,4]],'11111','00000'),(6,[[0,1],[1,2],[1,3],[3,4],[3,5]],'000000','110011'),(6,[[0,1],[0,2],[2,3],[3,4],[4,5]],'101010','010101'),(7,[[0,1],[1,2],[2,3],[3,4],[3,5],[1,6]],'0011000','0010001'),(7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],'0000000','1111110'),(8,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]],'00000000','10000001'),(9,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6],[6,7],[6,8]],'010101010','101010101'))]
C_CASES=[[a,b,k] for a,b,k in (([4,8,5,3],[1,5,2,7],8),([3,5,7,4],[2,4,3,6],7),([2,2,2],[3,5,4],5),([5],[10],5),([5],[10],6),([1,2],[3,4],3),([1,2],[3,4],4),([10,1,9],[100,1,90],11),([4,4,4],[1,10,5],9),([3,8,2,7],[9,20,8,15],10),([1,1,1],[2,3,4],2),([6,2,5,3],[5,8,7,9],9),([20,10,5],[100,20,10],16),([7,7,1,1],[30,20,5,4],9))]
D_CASES=[[s] for s in ('a','z','aa','aaccb','abca','cbacdcbc','bbcaac','zzza','banana','cbaabc','aaaa','abacb','dcbaabcd','mississippi')]

BATCH={
3811:entry('count_alternating_xor_partitions',[('nums','list[int]'),('target1','int'),('target2','int')],'int',['arrays','dynamic programming','prefix xor'],['nums has up to 100,000 values and target1 differs from target2.','Blocks are contiguous, nonempty, and cover all of nums.','Block XORs alternate target1,target2,… beginning with target1.'],[([[2,3,1,4],1,5],'The unique valid split is [2,3] with XOR one and [1,4] with XOR five.'),([[1,0,0],1,0],'The one-block partition and both legal two-block cuts give three.')],X_CASES,XOR,[XOR.replace('waiting_first={0:1}','waiting_first={}'),XOR.replace('prefix^target2','prefix^target1')],['Omits the empty prefix that starts the first target1 block.','Requires target1 for both odd and even blocks.'],xor_oracle,random_xor,lesson('A block XOR equals the XOR of its two boundary prefixes.','Track counts of prefix states waiting to close a target1 block and states waiting to close a target2 block.','At each prefix, query the complementary prefix XOR for each target, then register the newly completed partitions in the opposite waiting state.','Every partition’s final cut extends exactly one earlier alternating partition, so the recurrence counts each valid cut sequence once.'),'O(n)','O(n)',6),
3812:entry('minimum_tree_edge_toggles',[('n','int'),('edges','list[list[int]]'),('start','str'),('target','str')],'list[int]',['trees','greedy','depth-first search'],['2≤n≤100,000 and edges is a valid indexed tree.','Toggling an edge flips both endpoint bits.','Return the minimum toggle edge indices sorted, or [-1] if impossible.'],[([3,[[0,1],[1,2]],'010','100'],'Only edge zero must toggle, producing the target directly.'),([2,[[0,1]],'00','01'],'One endpoint alone cannot be toggled by the sole edge, so return [-1].')],T_CASES,TOGGLES,[TOGGLES.replace('for node in reversed(order[1:])','for node in order[1:]'),TOGGLES.replace('need[parent[node]]=not need[parent[node]]','')],['Processes parents before descendants, before child requirements are resolved.','Fails to propagate a selected child-edge toggle into the parent requirement.'],toggles_oracle,random_toggles,lesson('Root the tree; a non-root node can be fixed from below only by deciding whether to toggle its parent edge.','Process nodes bottom-up: if a node still differs, its parent edge is forced and also flips the parent’s requirement.','After all children, the root must already match or the transformation is impossible.','Every chosen edge is forced by its child endpoint, proving uniqueness and minimum size; sorting yields the required output order.'),'O(n)','O(n)',8),
3814:entry('maximum_machine_capacity',[('costs','list[int]'),('capacity','list[int]'),('budget','int')],'int',['arrays','sorting','binary search'],['costs and capacity have equal length up to 100,000.','Choose zero, one, or two distinct machines whose total cost is strictly less than budget.','Maximize their total capacity.'],[([[4,8,5,3],[1,5,2,7],8],'Costs four and three total seven and capacities one plus seven give eight.'),([[2,2,2],[3,5,4],5],'The two largest capacities cost four together and total nine.')],C_CASES,CAPACITY,[CAPACITY.replace('budget-cost','budget-cost+1'),CAPACITY.replace('other_index!=index','True')],['Uses a non-strict budget comparison and admits total cost equal to budget.','Allows selecting the same machine twice.'],capacity_oracle,random_capacity,lesson('Sort machines by cost and retain the two largest capacities in every cost prefix.','For each machine, binary-search the prefix with partner cost strictly below budget-current cost.','Choose the best prefix capacity whose original index differs, and also consider every affordable singleton.','Every legal pair is considered when either member is the current machine, while the two prefix leaders suffice after excluding at most one index.'),'O(n log n)','O(n)',6),
3816:entry('lexicographically_smallest_duplicate_deletion',[('s','str')],'str',['strings','greedy','monotonic stacks'],['s contains up to 100,000 lowercase letters.','An occurrence may be deleted only while its letter appears at least twice.','Return the lexicographically smallest reachable nonempty string.'],[(['aaccb'],'Deleting the first c gives aacb, which is smaller than every other reachable string.'),(['z'],'No letter repeats, so z cannot change.')],D_CASES,DELETE,[DELETE.replace('stack[-1]>char','stack[-1]>=char'),DELETE.replace("while stack and remaining[stack[-1]]>1:\n        removed=stack.pop();remaining[removed]-=1",'')],['Pops equal letters during the main scan and can discard a useful earlier occurrence.','Fails to remove deletable duplicate suffix characters after the scan.'],deletion_oracle,random_deletion,lesson('Each distinct letter must retain at least one occurrence; extra copies may be deleted.','Maintain the current result as a stack and pop a larger suffix character when another copy of it still remains.','After scanning, delete any still-redundant suffix because shortening a string after an equal prefix is lexicographically smaller.','The exchange removes the earliest avoidable larger character, and remaining counts guarantee every pop is legal.'),'O(n)','O(n)',8),
}
