"""BST subtree DP, frog probability, balanced BST construction, team heaps, and circular selection."""
from itertools import combinations

from .import_batch_055 import entry


class Node:
    def __init__(self,value,left=None,right=None):self.val=value;self.left=left;self.right=right
def make_tree(values):
    if not values:return None
    root=Node(values[0]);queue=[root];index=1
    while queue and index<len(values):
        node=queue.pop(0)
        if index<len(values) and values[index] is not None:node.left=Node(values[index]);queue.append(node.left)
        index+=1
        if index<len(values) and values[index] is not None:node.right=Node(values[index]);queue.append(node.right)
        index+=1
    return root
def serialize(root):
    if root is None:return []
    result=[];queue=[root]
    while queue:
        node=queue.pop(0)
        if node is None:result.append(None)
        else:result.append(node.val);queue.extend((node.left,node.right))
    while result and result[-1] is None:result.pop()
    return result
def random_tree(rng,maximum=16):
    values=[rng.randint(-12,12)];frontier=1;nodes=1
    while frontier and nodes<maximum:
        frontier-=1
        for _ in range(2):
            if nodes<maximum and rng.random()<.7:values.append(rng.randint(-12,12));frontier+=1;nodes+=1
            else:values.append(None)
    while values and values[-1] is None:values.pop()
    return values


def bst_sum_oracle(args):
    root=make_tree(args[0]);answer=0
    def inspect(node):
        nonlocal answer
        if node is None:return True,float('inf'),float('-inf'),0
        lv,lmin,lmax,ls=inspect(node.left);rv,rmin,rmax,rs=inspect(node.right)
        valid=lv and rv and lmax<node.val<rmin;total=ls+rs+node.val
        if valid:answer=max(answer,total);return True,min(lmin,node.val),max(rmax,node.val),total
        return False,0,0,total
    inspect(root);return answer
def random_bst_sum(rng):return [random_tree(rng)]


def frog_oracle(args):
    size,edges,seconds,target=args;graph=[[] for _ in range(size+1)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    states={(1,0):1.0}
    for _ in range(seconds):
        following={}
        for (node,parent),probability in states.items():
            choices=[neighbor for neighbor in graph[node] if neighbor!=parent]
            if not choices:following[(node,parent)]=following.get((node,parent),0)+probability
            else:
                for neighbor in choices:following[(neighbor,node)]=following.get((neighbor,node),0)+probability/len(choices)
        states=following
    return sum(probability for (node,_),probability in states.items() if node==target)
def random_frog(rng):
    size=rng.randint(1,12);edges=[[node,rng.randint(1,node-1)] for node in range(2,size+1)]
    return [size,edges,rng.randint(1,12),rng.randint(1,size)]


def balanced_oracle(args):
    values=sorted(value for value in args[0] if value is not None)
    def build(left,right):
        if left>=right:return None
        middle=(left+right)//2;return Node(values[middle],build(left,middle),build(middle+1,right))
    return serialize(build(0,len(values)))
def bst_input(values):
    root=None
    for value in values:
        if root is None:root=Node(value);continue
        node=root
        while True:
            if value<node.val:
                if node.left is None:node.left=Node(value);break
                node=node.left
            else:
                if node.right is None:node.right=Node(value);break
                node=node.right
    return serialize(root)
def random_balance(rng):
    values=rng.sample(range(1,100),rng.randint(1,15));return [bst_input(values)]


def performance_oracle(args):
    size,speeds,efficiencies,limit=args;best=0
    for count in range(1,limit+1):
        for chosen in combinations(range(size),count):best=max(best,sum(speeds[i] for i in chosen)*min(efficiencies[i] for i in chosen))
    return best%(10**9+7)
def random_performance(rng):
    size=rng.randint(1,10);return [size,[rng.randint(1,20) for _ in range(size)],[rng.randint(1,20) for _ in range(size)],rng.randint(1,size)]


def pizza_oracle(args):
    slices=args[0];chosen=len(slices)//3;best=0
    for indices in combinations(range(len(slices)),chosen):
        selected=set(indices)
        if all((index+1)%len(slices) not in selected for index in selected):best=max(best,sum(slices[i] for i in indices))
    return best
def random_pizza(rng):
    count=3*rng.randint(1,4);return [[rng.randint(1,20) for _ in range(count)]]


BST_SUM='''def maximum_sum_bst_subtree(root):
    answer=0
    def visit(node):
        nonlocal answer
        if node is None:return True,float('inf'),float('-inf'),0
        left,lmin,lmax,lsum=visit(node.left);right,rmin,rmax,rsum=visit(node.right)
        if left and right and lmax<node.val<rmin:
            total=lsum+rsum+node.val;answer=max(answer,total);return True,min(lmin,node.val),max(rmax,node.val),total
        return False,0,0,0
    visit(root);return answer
'''
FROG='''def frog_probability(n,edges,t,target):
    graph=[[] for _ in range(n+1)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    def visit(node,parent,time,probability):
        choices=[neighbor for neighbor in graph[node] if neighbor!=parent]
        if time==t or not choices:return probability if node==target else 0.0
        return sum(visit(neighbor,node,time+1,probability/len(choices)) for neighbor in choices)
    return visit(1,0,0,1.0)
'''
BALANCE='''def balance_binary_search_tree(root):
    values=[];stack=[];node=root
    while node or stack:
        while node:stack.append(node);node=node.left
        node=stack.pop();values.append(node.val);node=node.right
    def build(left,right):
        if left>=right:return None
        middle=(left+right)//2;return TreeNode(values[middle],build(left,middle),build(middle+1,right))
    return build(0,len(values))
'''
UNBALANCED='''def balance_binary_search_tree(root):
    return root
'''
PERFORMANCE='''def maximum_team_performance(n,speed,efficiency,k):
    import heapq
    heap=[];total=answer=0
    for current_efficiency,current_speed in sorted(zip(efficiency,speed),reverse=True):
        heapq.heappush(heap,current_speed);total+=current_speed
        if len(heap)>k:total-=heapq.heappop(heap)
        answer=max(answer,total*current_efficiency)
    return answer%(10**9+7)
'''
PIZZA='''def maximum_pizza_slice_sum(slices):
    choose=len(slices)//3
    def line(values):
        previous=[0]*(choose+1);before=[0]*(choose+1)
        for value in values:
            current=previous[:]
            for count in range(1,choose+1):current[count]=max(previous[count],before[count-1]+value)
            before,previous=previous,current
        return previous[choose]
    return max(line(slices[:-1]),line(slices[1:]))
'''

BATCH={
1373:entry('maximum_sum_bst_subtree',[('root','TreeNode')],'int',['trees','binary search trees','recursion'],['A BST subtree requires every left value to be strictly smaller and every right value strictly larger recursively.','Choose any rooted subtree and maximize its node-value sum.','Return zero when every valid BST subtree has a negative sum.'],[([[1,4,3,2,4,2,5,None,None,None,None,None,None,4,6]],'The valid BST subtree rooted at three contains values two, four, five, and six and sums to twenty.'),([[4,3,None,1,2]],'The best valid BST subtree is the single node two.')],[[t] for t in ([2,2,3],[0],[-1],[2,1,3],[2,3,1],[1,4,3,2,4,2,5,None,None,None,None,None,None,4,6],[4,3,None,1,2],[5,4,8,3,None,6,3],[1,None,2,None,3],[3,2,4,1,None,None,5],[-4,-2,-5],[-1,-2,0],[10,5,15,1,8,7,20],[5,3,7,2,4,6,8])],BST_SUM,[BST_SUM.replace('lmax<node.val<rmin','lmax<=node.val<=rmin'),BST_SUM.replace('answer=max(answer,total)','answer=total')],['Allows duplicate boundary values even though the BST ordering must be strict.','Overwrites the best sum with the latest valid subtree instead of retaining the maximum.'],bst_sum_oracle,random_bst_sum,['Return whether a subtree is a BST together with its minimum, maximum, and sum.','A node is valid only when both children are valid and left.max < node.val < right.min.','For valid nodes, update a global maximum and return the combined summary; mark invalid nodes so ancestors reject them.','Postorder provides all child facts before the parent decision, and every rooted subtree is evaluated once.'],'Postorder recursion summarizes each subtree with validity, extrema, and sum. Infinite empty-tree bounds make leaves fit the same strict inequalities. Valid sums update a maximum initialized to zero. The oracle independently reconstructs and inspects every subtree using separate node objects.','O(n)','O(height)',8),
1377:entry('frog_probability',[('n','int'),('edges','list[list[int]]'),('t','int'),('target','int')],'float',['trees','graphs','probability'],['The undirected edges form a tree on vertices one through n, and the frog starts at one.','Each second it chooses uniformly among unvisited neighbors; at a leaf it remains in place.','Return its probability of occupying target after exactly t seconds.'],[([7,[[1,2],[1,3],[1,7],[2,4],[2,6],[3,5]],2,4],'The frog chooses vertex two with probability one third, then vertex four with probability one half, giving one sixth.'),([1,[],3,1],'With no neighbor, the frog remains at vertex one with probability one.')],[[n,e,t,x] for n,e,t,x in ((1,[],1,1),(1,[],3,1),(2,[[1,2]],1,2),(2,[[1,2]],3,2),(2,[[1,2]],2,1),(3,[[1,2],[1,3]],1,2),(3,[[1,2],[2,3]],2,3),(3,[[1,2],[2,3]],5,3),(7,[[1,2],[1,3],[1,7],[2,4],[2,6],[3,5]],2,4),(7,[[1,2],[1,3],[1,7],[2,4],[2,6],[3,5]],1,1),(4,[[1,2],[1,3],[3,4]],2,4),(5,[[1,2],[2,3],[2,4],[4,5]],3,5),(6,[[1,2],[1,3],[2,4],[2,5],[3,6]],2,5),(4,[[1,2],[2,3],[3,4]],2,4))],FROG,[FROG.replace("choices=[neighbor for neighbor in graph[node] if neighbor!=parent]","choices=graph[node]"),FROG.replace('if time==t or not choices','if time==t')],['Includes the already-visited parent among future choices.','Fails to keep the frog stationary at a leaf for remaining seconds.'],frog_oracle,random_frog,['Root the tree implicitly by carrying the parent node.','At a state, divide probability equally among neighbors other than the parent.','Stop at exactly t seconds, or earlier at a leaf because the frog then remains there.','A tree has a unique root-to-node route, so the product of branch probabilities gives the target probability.'],'Depth-first probability propagation carries the parent to exclude visited vertices. At a leaf, stopping early is equivalent to remaining there through all later seconds. Otherwise divide by the unvisited child count. The oracle independently advances an explicit probability distribution one second at a time.','O(n)','O(height)',8),
1382:entry('balance_binary_search_tree',[('root','TreeNode')],'TreeNode',['trees','binary search trees','divide and conquer'],['root is a nonempty BST with distinct values.','Return any height-balanced BST containing exactly the same values.','At every node, left and right subtree heights may differ by at most one.'],[([[1,None,2,None,3,None,4,None,None]],'Choosing a middle value as root produces a balanced tree with the same four values.'),([[2,1,3]],'The input is already balanced, though rebuilding it is allowed.')],[[t] for t in ([1],[1,None,2],[1,None,2,None,3],[1,None,2,None,3,None,4],[2,1,3],[3,2,4,1,None,None,5],[5,4,None,3,None,2,None,1],[4,2,6,1,3,5,7],[2,1,4,None,None,3,5],[10,5,15,2,7,12,20],[8,3,10,1,6,None,14,None,None,4,7,13],[1,None,3,2],[6,2,8,1,4,7,9],[20,10,30,5,15,25,35])],BALANCE,[UNBALANCED,BALANCE.replace('TreeNode(values[middle],build(left,middle),build(middle+1,right))','TreeNode(values[middle],build(middle+1,right),build(left,middle))')],['Returns the original potentially skewed BST without balancing it.','Swaps constructed left and right subtrees, violating BST ordering.'],balanced_oracle,random_balance,['Inorder traversal extracts BST values in sorted order.','Choose the middle of each sorted interval as its subtree root.','Recursively build the left and right halves and attach them to a new TreeNode.','Halving each interval preserves inorder order and keeps child subtree sizes within one.'],'Collect values by iterative inorder traversal, then recursively build from half-open intervals using each midpoint. The resulting inorder sequence is unchanged and balanced height follows from nearly equal interval sizes. The balanced-BST comparator accepts any valid balanced shape. The oracle independently sorts serialized values and constructs a canonical midpoint tree.','O(n)','O(n)',5),
1383:entry('maximum_team_performance',[('n','int'),('speed','list[int]'),('efficiency','list[int]'),('k','int')],'int',['greedy','sorting','heaps'],['speed and efficiency describe n engineers; choose one through k of them.','Team performance is total speed multiplied by its minimum efficiency.','Maximize the unmodded performance, then return it modulo 1000000007.'],[([6,[2,10,3,1,5,8],[5,4,3,9,7,2],2],'Engineers with speeds ten and five have total speed fifteen and minimum efficiency four, giving sixty.'),([3,[2,8,2],[2,7,1],2],'The engineer with speed eight alone gives performance fifty-six.')],[[n,s,e,k] for n,s,e,k in ((1,[5],[7],1),(2,[1,2],[3,4],1),(2,[1,2],[3,4],2),(6,[2,10,3,1,5,8],[5,4,3,9,7,2],2),(3,[2,8,2],[2,7,1],2),(6,[2,10,3,1,5,8],[5,4,3,9,7,2],3),(3,[5,5,5],[5,5,5],2),(4,[1,2,3,4],[4,3,2,1],4),(4,[10,1,1,1],[1,10,10,10],2),(5,[9,8,7,6,5],[1,2,3,4,5],3),(3,[1,100,1],[100,1,100],2),(5,[2,3,5,7,11],[11,7,5,3,2],1),(4,[4,4,4,4],[1,2,3,4],3),(6,[1,2,3,4,5,6],[6,5,4,3,2,1],5))],PERFORMANCE,[PERFORMANCE.replace('if len(heap)>k','if len(heap)>=k'),PERFORMANCE.replace('sorted(zip(efficiency,speed),reverse=True)','sorted(zip(efficiency,speed))')],['Keeps at most k-1 speeds by removing a member as soon as team size reaches k.','Processes efficiencies ascending, so the current efficiency is not a valid team minimum.'],performance_oracle,random_performance,['Process engineers from greatest efficiency to least.','At each engineer, current efficiency is the minimum for any team formed from the processed prefix.','Keep the k largest processed speeds in a min-heap and test current speed sum times current efficiency.','Every optimal team is considered when its least-efficient member is processed.'],'Sort by decreasing efficiency. A min-heap retains the largest k speeds among engineers whose efficiencies are at least the current threshold. Their sum times the current efficiency is the best team using that threshold; maximize before modulo. The oracle independently enumerates all allowed engineer subsets on seeded inputs.','O(n log n+n log k)','O(k)',8),
1388:entry('maximum_pizza_slice_sum',[('slices','list[int]')],'int',['arrays','dynamic programming'],['slices is a positive circular array whose length is three times the number you must select.','Select exactly length/3 slices with no two selected positions adjacent around the circle.','Return the greatest possible selected sum.'],[([[1,2,3,4,5,6]],'Choosing slices four and six gives ten without circular adjacency.'),([[8,9,8,6,1,1]],'Choosing the second and fourth slices gives fifteen.')],[[x] for x in ([1,2,3],[1,2,3,4,5,6],[8,9,8,6,1,1],[4,1,2],[3,3,3,3,3,3],[10,1,1,10,1,1],[1,2,3,4,5,6,7,8,9],[9,1,1,9,1,1,9,1,1],[5,2,7,3,9,1],[1,100,1],[6,5,4,3,2,1],[2,4,6,8,10,12],[7,1,7,1,7,1],[1,2,100,2,1,2])],PIZZA,[PIZZA.replace('return max(line(slices[:-1]),line(slices[1:]))','return line(slices[:-1])'),PIZZA.replace('before[count-1]+value','previous[count-1]+value')],['Solves only the case excluding the final slice and can miss an optimum using it.','Allows adjacent slices by transitioning from the immediately previous row.'],pizza_oracle,random_pizza,['Break the circle into cases excluding the first slice or excluding the last slice.','For a line, DP over prefixes and exact selection counts with take or skip choices.','Taking a slice adds it to the state two positions earlier; skipping keeps the prior state.','Every legal circular selection excludes at least one endpoint, so one of the two linear cases contains the optimum.'],'A circular independent set cannot contain both endpoints. Solve two linear arrays, one without each endpoint. Linear DP chooses exactly n slices and uses the prefix two positions back when taking the current slice, enforcing nonadjacency. The oracle independently enumerates exact-size index subsets and checks circular neighbors.','O(length^2)','O(length)',8),
}
BATCH[1373]['params'][0]=('root','TreeNode','treenode')
BATCH[1377]['comparator']='float'
BATCH[1382]['params'][0]=('root','TreeNode','treenode');BATCH[1382]['adapter']='treenode';BATCH[1382]['comparator']='balanced_bst'

# The existing balanced-BST property comparator accepts sorted arrays and linked
# lists, but not a BST input. Preserve this reviewed candidate for the later
# comparator upgrade without publishing it under an inaccurate exact contract.
QUARANTINED_1382 = BATCH.pop(1382)

def delete_list_oracle(args):
    values,keep,drop=args;answer=[];index=0
    while index<len(values):
        answer.extend(values[index:index+keep]);index+=keep+drop
    return answer

def random_delete_list(rng):
    return [[rng.randint(1,30) for _ in range(rng.randint(1,30))],rng.randint(1,8),rng.randint(1,8)]

DELETE_LIST='''def delete_nodes_after_groups(head,m,n):
    current=head
    while current:
        for _ in range(m-1):
            if current.next is None:return head
            current=current.next
        after=current.next
        for _ in range(n):
            if after is None:break
            after=after.next
        current.next=after;current=after
    return head
'''

BATCH[1474]=entry('delete_nodes_after_groups',[('head','ListNode'),('m','int'),('n','int')],'ListNode',['linked lists','in-place'],['head is a nonempty linked list.','Repeatedly retain m consecutive nodes and delete the following n nodes until the list ends.','Relink the existing chain and return its original head.'],[([[1,2,3,4,5,6,7,8,9,10,11,12,13],2,3],'Keeping pairs and deleting the following triples leaves one, two, six, seven, eleven, and twelve.'),([[1,2,3,4,5],1,1],'Alternately keeping and deleting nodes leaves one, three, and five.')],[[v,m,n] for v,m,n in (([1],1,1),([1,2],1,1),([1,2,3,4,5],1,1),([1,2,3,4,5],2,1),([1,2,3,4,5],1,2),([1,2,3,4,5],5,2),([1,2,3,4,5],2,10),([1,2,3,4,5,6],2,2),([1,2,3,4,5,6,7,8,9,10,11,12,13],2,3),([9,8,7],1,5),([1,1,1,1],2,1),([10,20,30,40,50,60,70],3,2),([1,2,3,4,5,6,7,8],1,3),([5,4,3,2,1],3,1))],DELETE_LIST,[DELETE_LIST.replace('for _ in range(n):','for _ in range(max(0,n-1)):'),DELETE_LIST.replace('range(m-1)','range(m)')],['Deletes only n-1 nodes after each retained group.','Keeps m+1 nodes before each deletion phase.'],delete_list_oracle,random_delete_list,['Stop on the final retained node of each m-node group.','Advance a second pointer across at most n nodes to find the next retained group.','Link the retained tail directly to that pointer, then repeat from it.','Each node is traversed once as retained or deleted, and every rewiring joins consecutive retained groups.'],'Walk to the mth retained node, then advance a temporary pointer through the next n nodes and reconnect the retained tail to what remains. Repeating this modifies the original list in place and handles incomplete final groups. The oracle independently applies keep/drop slicing to serialized values.','O(length)','O(1)',3)
BATCH[1474]['params'][0]=('head','ListNode','listnode');BATCH[1474]['adapter']='listnode'
