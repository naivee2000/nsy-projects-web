"""Reviewed binary-tree width, partition, BST, and path imports."""
from collections import deque

from .import_batch_055 import entry


def from_level(values):
    if not values:return None
    root=[values[0],None,None];queue=deque([root]);index=1
    while queue and index<len(values):
        node=queue.popleft()
        for side in (1,2):
            if index<len(values) and values[index] is not None:
                node[side]=[values[index],None,None];queue.append(node[side])
            index+=1
    return root


def to_level(root):
    if root is None:return []
    result=[];queue=deque([root])
    while queue:
        node=queue.popleft()
        if node is None:result.append(None)
        else:result.append(node[0]);queue.extend((node[1],node[2]))
    while result and result[-1] is None:result.pop()
    return result


def width_oracle(args):
    root=from_level(args[0])
    if root is None:return 0
    answer=0;level=[(root,0)]
    while level:
        answer=max(answer,level[-1][1]-level[0][1]+1)
        level=[(child,index*2+offset) for node,index in level for offset,child in enumerate((node[1],node[2])) if child]
    return answer


def equal_partition_oracle(args):
    root=from_level(args[0]);sums=[]
    def total(node):
        if node is None:return 0
        value=node[0]+total(node[1])+total(node[2]);sums.append(value);return value
    whole=total(root)
    return whole%2==0 and whole//2 in sums[:-1]


def trim_oracle(args):
    root,low,high=from_level(args[0]),args[1],args[2]
    def trim(node):
        if node is None:return None
        if node[0]<low:return trim(node[2])
        if node[0]>high:return trim(node[1])
        return [node[0],trim(node[1]),trim(node[2])]
    return to_level(trim(root))


def second_oracle(args):
    values=sorted(set(value for value in args[0] if value is not None))
    return values[1] if len(values)>1 else -1


def univalue_oracle(args):
    root=from_level(args[0]);best=0
    def visit(node):
        nonlocal best
        if node is None:return 0
        left=visit(node[1]);right=visit(node[2])
        left=left+1 if node[1] and node[1][0]==node[0] else 0
        right=right+1 if node[2] and node[2][0]==node[0] else 0
        best=max(best,left+right);return max(left,right)
    visit(root);return best


def random_node(rng,depth=0,limit=5):
    if depth>=limit or (depth and rng.random()<.35):return None
    return [rng.randint(-4,4),random_node(rng,depth+1,limit),random_node(rng,depth+1,limit)]


def random_tree(rng):return to_level(random_node(rng,limit=rng.randint(1,5)))
def random_width(rng):return [random_tree(rng)]
def random_partition(rng):return [random_tree(rng)]


def random_trim(rng):
    values=rng.sample(range(-30,31),rng.randint(1,15));root=None
    for value in values:
        if root is None:root=[value,None,None];continue
        node=root
        while True:
            side=1 if value<node[0] else 2
            if node[side] is None:node[side]=[value,None,None];break
            node=node[side]
    low,high=sorted(rng.sample(range(-35,36),2))
    return [to_level(root),low,high]


def special_node(rng,value=1,depth=0):
    if depth>=4 or (depth and rng.random()<.45):return [value,None,None]
    left=value
    right=value if rng.random()<.55 else value+rng.randint(1,5)
    if rng.random()<.5:left,right=right,left
    return [value,special_node(rng,left,depth+1),special_node(rng,right,depth+1)]


def random_second(rng):return [to_level(special_node(rng,rng.randint(0,5)))]
def random_univalue(rng):return [random_tree(rng)]


WIDTH='''\
def maximum_tree_width(root):
    if not root:return 0
    answer=0;level=[(root,0)]
    while level:
        base=level[0][1]
        normalized=[(node,index-base) for node,index in level]
        answer=max(answer,normalized[-1][1]+1)
        level=[(child,index*2+offset) for node,index in normalized for offset,child in enumerate((node.left,node.right)) if child]
    return answer
'''


PARTITION='''\
def can_partition_tree(root):
    if not root:return False
    sums={};order=[];stack=[(root,False)]
    while stack:
        node,visited=stack.pop()
        if visited:
            value=node.val+sums.get(id(node.left),0)+sums.get(id(node.right),0)
            sums[id(node)]=value;order.append(value)
        else:
            stack.append((node,True))
            if node.right:stack.append((node.right,False))
            if node.left:stack.append((node.left,False))
    total=order[-1]
    return total%2==0 and total//2 in order[:-1]
'''


TRIM='''\
def trim_bst(root, low, high):
    while root and (root.val<low or root.val>high):
        root=root.right if root.val<low else root.left
    if not root:return None
    stack=[root]
    while stack:
        node=stack.pop()
        while node.left and node.left.val<low:
            node.left=node.left.right
        while node.right and node.right.val>high:
            node.right=node.right.left
        if node.left:stack.append(node.left)
        if node.right:stack.append(node.right)
    return root
'''


SECOND='''\
def second_minimum_tree_value(root):
    smallest=root.val;answer=None;stack=[root]
    while stack:
        node=stack.pop()
        if node.val>smallest:
            answer=node.val if answer is None else min(answer,node.val)
        else:
            if node.left:stack.append(node.left)
            if node.right:stack.append(node.right)
    return -1 if answer is None else answer
'''


UNIVALUE='''\
def longest_equal_value_path(root):
    if not root:return 0
    downward={};answer=0;stack=[(root,False)]
    while stack:
        node,visited=stack.pop()
        if visited:
            left=downward.get(id(node.left),0)+1 if node.left and node.left.val==node.val else 0
            right=downward.get(id(node.right),0)+1 if node.right and node.right.val==node.val else 0
            answer=max(answer,left+right);downward[id(node)]=max(left,right)
        else:
            stack.append((node,True))
            if node.right:stack.append((node.right,False))
            if node.left:stack.append((node.left,False))
    return answer
'''


WIDTH_COUNT=WIDTH.replace('answer=max(answer,normalized[-1][1]+1)','answer=max(answer,len(normalized))')
WIDTH_NO_GAPS=WIDTH.replace('index*2+offset','len(level)')
PARTITION_ROOT=PARTITION.replace('total//2 in order[:-1]','total//2 in order')
PARTITION_VALUES="def can_partition_tree(root):\n    values=[];stack=[root]\n    while stack:\n        node=stack.pop();values.append(node.val)\n        if node.left:stack.append(node.left)\n        if node.right:stack.append(node.right)\n    return sum(values)%2==0 and sum(values)//2 in values\n"
TRIM_STRICT=TRIM.replace('root.val<low','root.val<=low').replace('root.val>high','root.val>=high').replace('node.left.val<low','node.left.val<=low').replace('node.right.val>high','node.right.val>=high')
TRIM_ONLY_ROOT="def trim_bst(root,low,high):\n    return root if root and low<=root.val<=high else None\n"
SECOND_CHILD="def second_minimum_tree_value(root):\n    values=[node.val for node in (root.left,root.right) if node]\n    return min(values) if values else -1\n"
SECOND_MAX=SECOND.replace('min(answer,node.val)','max(answer,node.val)')
UNIVALUE_NODES=UNIVALUE.replace('return answer','return answer+1')
UNIVALUE_ONE_SIDE=UNIVALUE.replace('answer=max(answer,left+right)','answer=max(answer,left,right)')


def lesson(a,b,c,d):return [a,b,c,d],d


BATCH={
662:entry('maximum_tree_width',[('root','TreeNode | None')],'int',['trees','breadth-first-search'],['The tree contains 1 to 3,000 nodes.','Width counts null positions between the leftmost and rightmost non-null nodes at a level, using complete-tree indexing.'],[([[1,3,2,5,3,None,9]],'At the third level, positions for 5 through 9 span four complete-tree slots.'),([[1,3,2,5]],'The maximum level width is two.')],[[t] for t in ([1],[1,2],[1,None,2],[1,2,3],[1,2,3,4,None,None,7],[1,2,None,3,None,4],[1,None,2,None,3,None,4],[1,2,3,4,5,6,7],[1,2,3,4,None,None,7,8,None,None,None,None,None,None,15],[-1,-2,-3,None,-4],[0,0,0,0,None,None,0],[1,2,3,None,5,6,None])],WIDTH,[WIDTH_COUNT,WIDTH_NO_GAPS],['Counts only present nodes and ignores internal null slots.','Assigns compact level positions instead of complete-tree positions.'],width_oracle,random_width,*lesson('Complete-tree indices preserve the horizontal gaps created by missing nodes.','Carry an index with every BFS node and normalize each level to avoid huge integers.','Width=last-first+1; children receive 2*i and 2*i+1 after normalization.','Index differences match the problem’s imaginary full tree while normalization keeps numbers bounded.'),'O(n)','O(tree width)',5),
663:entry('can_partition_tree',[('root','TreeNode | None')],'bool',['trees','postorder'],['The tree contains at least one node with integer values.','Remove exactly one parent-child edge so the two resulting component sums are equal.'],[([[5,10,10,None,None,2,3]],'Cutting the edge above the right ten creates components summing fifteen each.'),([[1,2,10]],'No single edge creates equal component sums.')],[[t] for t in ([1],[0,0],[0,1,-1],[1,1],[2,1,1],[1,-1,0],[5,10,10,None,None,3,2],[1,2,3],[10,5,5],[0,0,0],[3,-1,-2],[4,2,2,1,1])],PARTITION,[PARTITION_ROOT,PARTITION_VALUES],['Allows selecting the whole tree rather than cutting an edge, causing false positives when total is zero.','Checks individual node values instead of complete subtree sums.'],equal_partition_oracle,random_partition,*lesson('Cutting an edge selects one non-root subtree whose sum must equal half the total.','Compute every subtree sum in postorder, excluding the root candidate.','If total is even, test total/2 among non-root subtree sums.','The other component automatically has total minus the selected subtree sum, so equality is necessary and sufficient.'),'O(n)','O(n)',5),
669:entry('trim_bst',[('root','TreeNode | None'),('low','int'),('high','int')],'TreeNode | None',['trees','binary-search-trees'],['The input is a BST and low <= high.','Remove values outside the inclusive range while preserving the relative structure of retained nodes.'],[([[1,0,2],1,2],'Zero is removed and the original root with right child two remains.'),([[3,0,4,None,2,None,None,1],1,3],'The trimmed tree retains three with left subtree two-left-one.')],[[t,l,h] for t,l,h in (([1],1,1),([1],0,2),([2,1,3],2,3),([2,1,3],1,2),([2,1,3],3,4),([5,3,8,2,4,7,9],4,8),([5,3,8,2,4,7,9],6,10),([1,None,2,None,3],2,3),([3,2,None,1],1,2),([0,-2,2,-3,-1,1,3],-1,1),([4,2,6,1,3,5,7],3,5),([10,5,15,2,7,12,20],6,16))],TRIM,[TRIM_STRICT,TRIM_ONLY_ROOT],['Treats the inclusive bounds as exclusive.','Checks only the root and discards salvageable in-range descendants.'],trim_oracle,random_trim,*lesson('BST ordering tells which single subtree can contain in-range replacements for an out-of-range node.','Move the root into range, then bypass too-small left links and too-large right links iteratively.','For each retained node, replace invalid left by left.right and invalid right by right.left until valid.','Every bypass discards only values that ordering proves outside the range, preserving all valid descendants and their structure.'),'O(n)','O(n)',5),
671:entry('second_minimum_tree_value',[('root','TreeNode | None')],'int',['trees','depth-first-search'],['The special tree has each internal value equal to the smaller of its two child values.','Return the smallest distinct value greater than root.val, or -1 if no such value exists.'],[([[2,2,5,None,None,5,7]],'The distinct values are two, five, and seven, so five is second.'),([[2,2,2]],'No value is greater than the root minimum.')],[[t] for t in ([1],[1,1,2],[1,2,1],[1,2,3],[0,0,5,None,None,5,6],[2,2,5,2,2,5,7],[1,1,1,1,1,1,1],[3,3,8,None,None,8,9],[0,0,1],[5,5,10,5,5,10,11],[2,5,2],[1,4,1,4,5,1,1])],SECOND,[SECOND_CHILD,SECOND_MAX],['Looks only at the root’s immediate children and can miss the next distinct descendant.','Keeps the largest qualifying value rather than the smallest.'],second_oracle,random_second,*lesson('The root is the global minimum, and a node larger than it bounds its entire subtree from below.','Traverse minimum-valued branches; treat larger nodes as candidate answers without descending.','Track the smallest node.val>root.val; expand only nodes equal to root.val.','The special min-child property proves descendants of an already larger node cannot improve that candidate.'),'O(n)','O(n)',3),
687:entry('longest_equal_value_path',[('root','TreeNode | None')],'int',['trees','dynamic-programming'],['The tree contains 0 to 10,000 nodes.','Return path length in edges; the path may join matching downward chains from both children through a node.'],[([[5,4,5,1,1,None,5]],'The two right-side edges connect three nodes valued five.'),([[1,4,5,4,4,None,5]],'The longest equal-value path joins the two four children through their parent for two edges.')],[[t] for t in ([],[1],[1,1],[1,2],[1,1,1],[1,1,1,1,1],[1,2,2,2,None,None,2],[0,0,0,0,None,None,0],[1,None,1,None,1],[1,2,3,4,5,6,7],[2,2,3,2,None,None,3],[-1,-1,-1,None,-1])],UNIVALUE,[UNIVALUE_NODES,UNIVALUE_ONE_SIDE],['Counts nodes instead of edges.','Keeps only one downward branch and misses paths joining both children.'],univalue_oracle,random_univalue,*lesson('A parent can extend only child chains whose root value matches its own.','Compute longest matching downward chains in postorder and combine left plus right at each node.','Store max(left,right) upward; update global answer with left+right.','Every simple path has a highest node where its two downward portions meet, so checking that combination at every node is exhaustive.'),'O(n)','O(n)',5),
}
for pid in (662,663,669,671,687):BATCH[pid]['params'][0]=('root','TreeNode | None','treenode')
BATCH[669]['adapter']='treenode'
