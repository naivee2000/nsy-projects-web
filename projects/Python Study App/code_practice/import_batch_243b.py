"""Tree recursion, linked-list traversal/splicing, and expression enumeration."""
from collections import deque
from functools import lru_cache
from .import_batch_055 import entry


def decode(values):
    if not values:
        return None
    nodes = [[values[0], None, None]]
    queue = deque([0]); index = 1
    while queue and index < len(values):
        parent = queue.popleft()
        for side in (1, 2):
            if index >= len(values):
                break
            value = values[index]; index += 1
            if value is not None:
                nodes.append([value, None, None]); child = len(nodes) - 1
                nodes[parent][side] = child; queue.append(child)
    return nodes


def encode(nodes, root=0):
    if nodes is None or root is None:
        return []
    answer=[]; queue=deque([root])
    while queue:
        node=queue.popleft()
        if node is None: answer.append(None); continue
        answer.append(nodes[node][0]); queue.extend((nodes[node][1],nodes[node][2]))
    while answer and answer[-1] is None: answer.pop()
    return answer


def random_tree(rng, maximum=11, unique=False):
    n=rng.randint(1,maximum)
    values=(rng.sample(range(-50,51),n) if unique else [rng.randint(-5,5) for _ in range(n)])
    nodes=[[values[0],None,None]]; slots=[(0,1),(0,2)]
    for value in values[1:]:
        choice=rng.randrange(len(slots)); parent,side=slots.pop(choice)
        nodes.append([value,None,None]); child=len(nodes)-1; nodes[parent][side]=child
        slots.extend(((child,1),(child,2)))
    return encode(nodes)


def same_tree(a, ai, b, bi):
    if ai is None or bi is None: return ai is bi
    return (a[ai][0]==b[bi][0] and same_tree(a,a[ai][1],b,b[bi][1])
            and same_tree(a,a[ai][2],b,b[bi][2]))


def subtree_oracle(args):
    root,sub=map(decode,args)
    if sub is None:return True
    if root is None:return False
    return any(same_tree(root,node,sub,0) for node in range(len(root)))
def random_subtree(rng):
    tree=random_tree(rng,10)
    if rng.random()<.55:
        nodes=decode(tree); return [tree,encode(nodes,rng.randrange(len(nodes)))]
    return [tree,random_tree(rng,6)]


def middle_oracle(args):return args[0][len(args[0])//2:]
def random_middle(rng):return [[rng.randint(-30,30) for _ in range(rng.randint(1,60))]]


def flip_oracle(args):
    first,second=map(decode,args)
    @lru_cache(None)
    def equivalent(a,b):
        if a is None or b is None:return a is b
        if first[a][0]!=second[b][0]:return False
        return ((equivalent(first[a][1],second[b][1]) and equivalent(first[a][2],second[b][2]))
                or (equivalent(first[a][1],second[b][2]) and equivalent(first[a][2],second[b][1])))
    return equivalent(0 if first else None,0 if second else None)
def random_flip(rng):
    first=random_tree(rng,10,True); nodes=decode(first)
    if rng.random()<.55:
        for node in nodes:
            if rng.random()<.5:node[1],node[2]=node[2],node[1]
        second=encode(nodes)
    else:second=random_tree(rng,10,True)
    return [first,second]


def camera_oracle(args):
    nodes=decode(args[0]); n=len(nodes)
    parents=[None]*n
    for parent,node in enumerate(nodes):
        for child in node[1:]:
            if child is not None:parents[child]=parent
    for count in range(n+1):
        from itertools import combinations
        for selected in combinations(range(n),count):
            cameras=set(selected)
            if all(node in cameras or parents[node] in cameras
                   or any(child in cameras for child in nodes[node][1:] if child is not None)
                   for node in range(n)):return count
def random_camera(rng):return [random_tree(rng,9)]


def maximum_tree(values):
    if not values:return None
    pivot=max(range(len(values)),key=values.__getitem__)
    return (values[pivot],maximum_tree(values[:pivot]),maximum_tree(values[pivot+1:]))
def tuple_level(root):
    if root is None:return []
    answer=[];queue=deque([root])
    while queue:
        node=queue.popleft()
        if node is None:answer.append(None);continue
        answer.append(node[0]);queue.extend((node[1],node[2]))
    while answer and answer[-1] is None:answer.pop()
    return answer
def inorder(nodes,node=0):
    if nodes is None or node is None:return []
    return inorder(nodes,nodes[node][1])+[nodes[node][0]]+inorder(nodes,nodes[node][2])
def insert_max_oracle(args):return tuple_level(maximum_tree(inorder(decode(args[0]))+[args[1]]))
def random_insert_max(rng):
    n=rng.randint(1,10);values=rng.sample(range(1,80),n+1)
    return [tuple_level(maximum_tree(values[:-1])),values[-1]]


def two_bst_oracle(args):
    a,b,target=args;left=set(inorder(decode(a)))
    return any(target-value in left for value in inorder(decode(b)))
def bst(values):return tuple_level(maximum_tree(values))
def random_two_bst(rng):
    a=rng.sample(range(-30,31),rng.randint(1,10));b=rng.sample(range(-30,31),rng.randint(1,10))
    return [bst(a),bst(b),rng.randint(-50,50)]


def nearest_oracle(args):
    values,target=args;nodes=decode(values);queue=deque([(0,0)]);levels={}
    while queue:
        node,depth=queue.popleft();levels.setdefault(depth,[]).append(node)
        for child in nodes[node][1:]:
            if child is not None:queue.append((child,depth+1))
    for level in levels.values():
        for index,node in enumerate(level):
            if nodes[node][0]==target:return nodes[level[index+1]][0] if index+1<len(level) else None
def random_nearest(rng):
    tree=random_tree(rng,15,True);values=[node[0] for node in decode(tree)]
    return [tree,rng.choice(values)]


def merge_oracle(args):
    first,a,b,second=args
    return first[:a]+second+first[b+1:]
def random_merge(rng):
    first=[rng.randint(-50,50) for _ in range(rng.randint(3,25))]
    a=rng.randint(1,len(first)-2);b=rng.randint(a,len(first)-2)
    return [first,a,b,[rng.randint(-50,50) for _ in range(rng.randint(1,15))]]


def expression_value(text):
    left,right=text.split('+');best=None;answer=None
    for i in range(len(left)):
        for j in range(1,len(right)+1):
            value=(int(left[:i]) if i else 1)*(int(left[i:])+int(right[:j]))*(int(right[j:]) if j<len(right) else 1)
            candidate=f'{left[:i]}({left[i:]}+{right[:j]}){right[j:]}'
            if best is None or value<best:best,answer=value,candidate
    return answer
def minimize_oracle(args):return expression_value(args[0])
def random_expression(rng):
    def number():return str(rng.randint(1,99999))
    return [number()+'+'+number()]


def reverse_levels_oracle(args):
    values=list(args[0]);nodes=decode(values);queue=deque([(0,0)]);levels={}
    while queue:
        node,depth=queue.popleft();levels.setdefault(depth,[]).append(node)
        for child in nodes[node][1:]:
            if child is not None:queue.append((child,depth+1))
    for depth,level in levels.items():
        if depth%2:
            changed=[nodes[node][0] for node in reversed(level)]
            for node,value in zip(level,changed):nodes[node][0]=value
    return encode(nodes)
def perfect_tree(rng):
    depth=rng.randint(0,4);return rng.sample(range(1,200),2**(depth+1)-1)
def random_reverse_levels(rng):return [perfect_tree(rng)]


SUBTREE='''def is_subtree(root,sub_root):
    def same(a,b):
        if a is None or b is None:return a is b
        return a.val==b.val and same(a.left,b.left) and same(a.right,b.right)
    if sub_root is None:return True
    if root is None:return False
    return same(root,sub_root) or is_subtree(root.left,sub_root) or is_subtree(root.right,sub_root)
'''
MIDDLE='''def middle_linked_list(head):
    slow=fast=head
    while fast and fast.next:slow=slow.next;fast=fast.next.next
    return slow
'''
FLIP='''def flip_equivalent_trees(root1,root2):
    if root1 is None or root2 is None:return root1 is root2
    if root1.val!=root2.val:return False
    return ((flip_equivalent_trees(root1.left,root2.left) and flip_equivalent_trees(root1.right,root2.right))
            or (flip_equivalent_trees(root1.left,root2.right) and flip_equivalent_trees(root1.right,root2.left)))
'''
CAMERAS='''def minimum_tree_cameras(root):
    cameras=0
    def visit(node):
        nonlocal cameras
        if node is None:return 2
        left,right=visit(node.left),visit(node.right)
        if left==0 or right==0:cameras+=1;return 1
        if left==1 or right==1:return 2
        return 0
    if visit(root)==0:cameras+=1
    return cameras
'''
INSERT='''def insert_into_maximum_tree(root,val):
    if root is None or val>root.val:return TreeNode(val,root)
    root.right=insert_into_maximum_tree(root.right,val)
    return root
'''
TWO_BST='''def two_sum_binary_search_trees(root1,root2,target):
    values=set();stack=[root1]
    while stack:
        node=stack.pop()
        if node:values.add(node.val);stack.extend((node.left,node.right))
    stack=[root2]
    while stack:
        node=stack.pop()
        if node:
            if target-node.val in values:return True
            stack.extend((node.left,node.right))
    return False
'''
NEAREST='''def nearest_right_tree_node(root,u):
    from collections import deque
    queue=deque([root])
    while queue:
        width=len(queue)
        for index in range(width):
            node=queue.popleft()
            if node is u:return queue[0] if index+1<width else None
            if node.left:queue.append(node.left)
            if node.right:queue.append(node.right)
'''
MERGE='''def merge_between_linked_lists(list1,a,b,list2):
    before=list1
    for _ in range(a-1):before=before.next
    after=before
    for _ in range(b-a+2):after=after.next
    before.next=list2;tail=list2
    while tail.next:tail=tail.next
    tail.next=after
    return list1
'''
MINIMIZE='''def minimize_parenthesized_sum(expression):
    left,right=expression.split('+');best=float('inf');answer=''
    for i in range(len(left)):
        for j in range(1,len(right)+1):
            outer_left=int(left[:i]) if i else 1;outer_right=int(right[j:]) if j<len(right) else 1
            value=outer_left*(int(left[i:])+int(right[:j]))*outer_right
            if value<best:best=value;answer=f'{left[:i]}({left[i:]}+{right[:j]}){right[j:]}'
    return answer
'''
REVERSE='''def reverse_odd_tree_levels(root):
    from collections import deque
    queue=deque([root]);depth=0
    while queue:
        level=list(queue)
        if depth%2:
            values=[node.val for node in reversed(level)]
            for node,value in zip(level,values):node.val=value
        for _ in range(len(queue)):
            node=queue.popleft()
            if node.left:queue.extend((node.left,node.right))
        depth+=1
    return root
'''

def lesson(a,b,c,d):return [a,b,c,d]

TREE_CASES=[
([3,4,5,1,2],[4,1,2]),([3,4,5,1,2,None,None,None,None,0],[4,1,2]),([1],[1]),([1],[2]),
([1,1],[1]),([1,2,3],[2]),([1,2,3],[3]),([1,2,None,3],[2,3]),([1,None,2],[2]),
([0,-1,1,-2,None,None,2],[-1,-2]),([1,2,3,4,5],[2,4,5]),([1,2,3,4,None],[2,4]),
([5,5,5,5],[5,5]),([1,2,3],[1,2,None])]
MIDDLE_CASES=[[x] for x in ([1],[1,2],[1,2,3],[1,2,3,4],[1,2,3,4,5],[0,0],[-1,2,-3],[5,4,3,2,1,0],[9,8,7],[1,1,1,1],[10,-10,20,-20,30,40],[2,4,6,8,10,12,14],[7,6,5,4,3],[100])]
MIDDLE_CASES.extend(([[42,43]], [[9,7,5,3,1,-1]]))
FLIP_CASES=[[a,b] for a,b in [([1],[1]),([1],[2]),([1,2,3],[1,3,2]),([1,2,None],[1,None,2]),([1,2,3,4,5,6,None],[1,3,2,None,6,5,4]),([1,2,3],[1,2,None]),([1,2,2,3,None,None,3],[1,2,2,None,3,3]),([0,-1,1],[0,1,-1]),([1,2,3,4],[1,3,2,None,None,None,4]),([1,2,None,3],[1,None,2,None,3]),([5,3,8,1,4,7,9],[5,8,3,9,7,4,1]),([1,2,3,4,5],[1,3,2,None,None,5,4]),([2,1,3],[2,3,1]),([1,2,3,4,None],[1,3,2,None,None,None,4])]]
CAMERA_CASES=[[x] for x in ([0],[0,0],[0,None,0],[0,0,None,0,0],[0,0,0],[0,0,None,0,None,0,None],[0,0,0,0,0,0,0],[0,None,0,None,0,None,0],[0,0,None,None,0],[0,0,0,0],[0,0,0,None,None,0,0],[0,0,None,0,None,0],[0,0,0,0,None,None,0],[0,None,0,0,0])]
CAMERA_CASES.extend(([[0,0,0,None,0]], [[0,None,0,0,None,None,0]]))
INSERT_CASES=[[tree,value] for tree,value in [([4,1,3,None,None,2],5),([5,2,4,None,1],3),([5,2,3,None,1],4),([1],2),([2],1),([3,2,None,1],4),([4,1,3],2),([10,5,8,2,4,7],6),([6,5,None,4],3),([9,7,8],10),([9,7,8],6),([5,None,4,None,3],2),([8,3,7,1,2,6],5),([2,None,1],3)]]
TWO_CASES=[[a,b,t] for a,b,t in [([2,1,4],[1,0,3],5),([0,-10,10],[5,1,7],18),([1],[2],3),([1],[2],4),([5,3,7],[10,6,15],13),([5,3,7],[10,6,15],20),([0,-2,3],[1,-4,6],-6),([2,1,3],[2,1,3],4),([8,4,12,2,6,10,14],[5,3,7],21),([8,4,12],[5,3,7],6),([-1,-2,0],[-3,-4,1],0),([10,5,15],[20,17,25],40),([3,1,4],[6,5,7],8),([100],[0],100)]]
NEAR_CASES=[[tree,target] for tree,target in [([1,2,3,None,4,5,6],4),([3,None,4,2],2),([1],1),([1,2,3],2),([1,2,3],3),([1,2,None,3],3),([1,None,2,None,3],2),([5,3,8,1,4,7,9],4),([5,3,8,1,4,7,9],9),([0,-1,1,-2,None,None,2],-1),([10,5,15,2,7,12,20],12),([10,5,15,2,7,12,20],20),([1,2,3,4,5,None,6],5),([8,4,12,2,6,10,14],6)]]
MERGE_CASES=[[a,x,y,b] for a,x,y,b in [([10,1,13,6,9,5],3,4,[1000000,1000001,1000002]),([0,1,2,3,4,5,6],2,5,[1000000,1000001,1000002,1000003,1000004]),([1,2,3],1,1,[9]),([1,2,3,4],1,2,[8,9]),([1,2,3,4,5],2,3,[7]),([0,0,0],1,1,[1,2]),([-3,-2,-1,0],1,2,[5]),([9,8,7,6,5],3,3,[1,2,3]),([1,2,3,4,5,6],1,4,[0]),([10,20,30,40],2,2,[-1,-2]),([1,1,1,1],1,2,[2,2]),([5,4,3,2,1],2,3,[8,7,6]),([0,1,2,3,4],1,3,[9]),([100,200,300],1,1,[0,0,0])]]
EXPR_CASES=[[x] for x in ('247+38','12+34','999+999','1+1','10+20','123+45','5+678','100+2','2+100','55+55','99999+1','1+99999','321+123','98+76')]
REVERSE_CASES=[[x] for x in ([2,3,5,8,13,21,34],[7,13,11],[1],[1,2,3],[1,2,3,4,5,6,7],[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],[0,-1,1],[5,4,3,2,1,0,-2],[10,20,30,40,50,60,70],[9,8,7],[1,3,2,7,6,5,4],[100,1,99],[4,2,6,1,3,5,7],[8,4,12,2,6,10,14])]

BATCH={
572:entry('is_subtree',[('root','TreeNode | None'),('sub_root','TreeNode | None')],'bool',['trees','recursion','depth-first search'],['Each input is a binary tree serialized through TreeNode.','Return whether some node of root begins a subtree identical in values and structure to sub_root.'],[([TREE_CASES[0][0],TREE_CASES[0][1]],'The node valued four has children one and two, exactly matching the candidate subtree.'),([TREE_CASES[1][0],TREE_CASES[1][1]],'The extra zero below node two changes the structure, so the candidate is not a subtree.')],[[a,b] for a,b in TREE_CASES[2:]],SUBTREE,[SUBTREE.replace('and same(a.right,b.right)','or same(a.right,b.right)'),SUBTREE.replace('or is_subtree(root.right,sub_root)','')],['Accepts a partial one-sided match instead of requiring both child subtrees.','Searches only the left descendants and misses matches on the right.'],subtree_oracle,random_subtree,lesson('A match needs both a starting node and exact recursive structure.','At every root node, compare the two trees; otherwise search both child subtrees.','same handles paired nulls and equal values before recurring left and right.','Every possible subtree root is visited, and same proves structural equality from that root.'),'O(n*m)','O(n+m)',3),
876:entry('middle_linked_list',[('head','ListNode')],'ListNode',['linked lists','two pointers'],['The linked list contains 1 through 100 nodes.','Return the second middle node when the length is even, including the suffix beginning there.'],[([[1,2,3,4,5]],'Slow reaches value three when fast reaches the end, returning [3,4,5].'),([[1,2,3,4,5,6]],'For even length the second middle is value four, returning [4,5,6].')],MIDDLE_CASES[2:],MIDDLE,[MIDDLE.replace('fast.next','fast.next.next',1),MIDDLE.replace('slow=slow.next','slow=slow.next.next')],['Advances fast too far in the loop condition and can stop at the wrong node.','Moves slow twice per round and skips the middle.'],middle_oracle,random_middle,lesson('A pointer moving twice as fast covers the list while slow covers half.','Advance slow one node and fast two while two fast steps remain.','When fast reaches the end, return slow.','After each round slow has advanced half as many edges; even lengths therefore select the later middle.'),'O(n)','O(1)',3),
951:entry('flip_equivalent_trees',[('root1','TreeNode | None'),('root2','TreeNode | None')],'bool',['trees','recursion','depth-first search'],['A flip swaps a node’s left and right children.','Return whether any set of flips makes the two binary trees identical.'],[([FLIP_CASES[2][0],FLIP_CASES[2][1]],'Flipping the root changes children two,three into three,two.'),([FLIP_CASES[5][0],FLIP_CASES[5][1]],'The second tree is missing node three, so flips cannot make the trees equal.')],[[a,b] for a,b in FLIP_CASES[:2]+FLIP_CASES[3:5]+FLIP_CASES[6:]],FLIP,[FLIP.replace(' or (flip_equivalent_trees(root1.left,root2.right)',' and (flip_equivalent_trees(root1.left,root2.right)'),FLIP.replace('root1.val!=root2.val','root1.val==root2.val')],['Requires both the unflipped and flipped alignments simultaneously.','Rejects equal root values instead of unequal ones.'],flip_oracle,random_flip,lesson('Each node has only two possible child alignments.','After matching root values, recursively test unflipped pairs or crossed pairs.','Handle nulls, reject unequal values, then evaluate the two alignments.','A sequence of flips exists exactly when one alignment succeeds independently at every matched node.'),'O(n)','O(h)',5),
968:entry('minimum_tree_cameras',[('root','TreeNode')],'int',['trees','recursion','tree dynamic programming'],['A camera monitors its node, parent, and immediate children.','Return the minimum cameras needed to monitor every node.'],[([[0,0,None,0,0]],'One camera on the child of the root covers all four nodes.'),([[0,0,None,0,None,0,None]],'The length-four chain needs two cameras.')],CAMERA_CASES[2:],CAMERAS,[CAMERAS.replace('if left==0 or right==0','if left==0 and right==0'),CAMERAS.replace('if visit(root)==0:cameras+=1','')],['Places a camera only when both children are uncovered.','Leaves an uncovered root without a final camera.'],camera_oracle,random_camera,lesson('A subtree reports uncovered, camera, or covered-without-camera.','Postorder children first; an uncovered child forces a camera, while a child camera covers its parent.','Null is covered; count forced cameras and add one if the root remains uncovered.','Delaying a camera until a child requires it is optimal because that placement covers the parent and sibling direction too.'),'O(n)','O(h)',8),
998:entry('insert_into_maximum_tree',[('root','TreeNode | None'),('val','int')],'TreeNode',['trees','recursion','monotonic structure'],['root is the maximum binary tree of a unique-value array.','Append val to that original array and return its maximum tree.'],[([[4,1,3,None,None,2],5],'Five becomes the new maximum root with the old tree on its left.'),([[5,2,4,None,1],3],'Three is inserted along the right spine below four.')],INSERT_CASES[2:],INSERT,[INSERT.replace('val>root.val','val<root.val'),INSERT.replace('root.right=','root.left=')],['Makes a smaller appended value the new root.','Recurses down the left spine even though appending changes only the right spine.'],insert_max_oracle,random_insert_max,lesson('Appending can only change ancestors along the current right spine.','If val exceeds the current root it becomes a new root; otherwise recurse right.','Attach the old root as the new node’s left child at the first smaller ancestor.','This is exactly the Cartesian-tree construction for one appended array value.'),'O(h)','O(h)',5),
1214:entry('two_sum_binary_search_trees',[('root1','TreeNode | None'),('root2','TreeNode | None'),('target','int')],'bool',['trees','binary search trees','hash maps'],['Both inputs are binary search trees and may contain negative values.','Choose one node from each tree and return whether their values sum to target.'],[([[2,1,4],[1,0,3],5],'Pairs 2+3 and 4+1 both reach five.'),([[0,-10,10],[5,1,7],18],'No value from the first tree complements a value from the second to eighteen.')],TWO_CASES[2:],TWO_BST,[TWO_BST.replace('target-node.val in values','node.val in values'),TWO_BST.replace('stack=[root2]','stack=[root1]')],['Checks equal values instead of complementary values.','Searches the first tree twice and may reuse the wrong input.'],two_bst_oracle,random_two_bst,lesson('A value in one tree determines the only needed complement in the other.','Store every first-tree value in a set, then traverse the second tree.','Return true on target-current in the set; otherwise exhaust the second tree.','The set represents every permitted first choice, so each second choice is tested in constant expected time.'),'O(n+m)','O(n)',5),
1602:entry('nearest_right_tree_node',[('root','TreeNode'),('u','TreeNode')],'TreeNode | None',['trees','breadth-first search'],['Tree values are unique and u is a node in root.','Return the node immediately to the right of u on the same depth, or None if u is last.'],[([[1,2,3,None,4,5,6],4],'At depth two, node five immediately follows node four.'),([[3,None,4,2],2],'Node two is the only node at its depth, so no right neighbor exists.')],NEAR_CASES[2:],NEAREST,[NEAREST.replace('index+1<width','index<width'),NEAREST.replace('if node is u','if node.val==root.val')],['Returns the first node of the next level when u ends its level.','Compares every node with the root value rather than the selected node identity.'],nearest_oracle,random_nearest,lesson('Breadth-first search exposes one complete depth at a time.','Remember the level width before removing nodes.','When u is removed, return the next queued node only if another position remains in that same width.','Children are appended behind the current level, so the width boundary prevents crossing into the next depth.'),'O(n)','O(w)',5),
1669:entry('merge_between_linked_lists',[('list1','ListNode'),('a','int'),('b','int'),('list2','ListNode')],'ListNode',['linked lists','pointer splicing'],['0 < a <= b < len(list1)-1 and list2 is nonempty.','Remove list1 indices a through b inclusive and splice list2 in their place.'],[([MERGE_CASES[0][0],MERGE_CASES[0][1],MERGE_CASES[0][2],MERGE_CASES[0][3]],'Indices three and four are replaced by all three nodes of list2.'),([MERGE_CASES[1][0],MERGE_CASES[1][1],MERGE_CASES[1][2],MERGE_CASES[1][3]],'Indices two through five are removed before the second list is connected.')],MERGE_CASES[2:],MERGE,[MERGE.replace('range(b-a+2)','range(b-a+1)'),MERGE.replace('tail.next=after','tail.next=after.next')],['Keeps the final node at index b instead of removing it.','Skips the first retained node after the removed range.'],merge_oracle,random_merge,lesson('Only two cut boundaries and the tail of list2 are needed.','Find the node before a and the node after b, then connect through list2.','Walk a-1 edges, walk b-a+2 edges to the suffix, attach list2, find its tail, attach the suffix.','These two pointer rewrites preserve exactly the prefix, replacement list, and suffix in order.'),'O(a+len(list2)+b-a)','O(1)',5),
2232:entry('minimize_parenthesized_sum',[('expression','str')],'str',['strings','enumeration'],['expression contains two positive decimal integers separated by one plus sign.','Insert one pair of parentheses enclosing the plus sign; adjacent outside digits multiply the parenthesized sum.','Return the expression with minimum evaluated value.'],[(['247+38'],'Choosing 2(47+38) gives 170, the minimum over every left/right split.'),(['12+34'],'The minimum placement is 1(2+3)4, which evaluates to twenty.')],EXPR_CASES[2:],MINIMIZE,[MINIMIZE.replace('range(1,len(right)+1)','range(len(right))'),MINIMIZE.replace('if value<best','if value>best')],['Never allows the parentheses to include all right-hand digits and also permits an empty inner prefix.','Selects the largest evaluated placement rather than the smallest.'],minimize_oracle,random_expression,lesson('Each valid answer is determined by one cut in each operand.','Enumerate the left start and right end of the parenthesized addition.','Treat an absent outside factor as one, evaluate, and retain the first minimum string.','The two nested loops visit every legal parentheses placement exactly once.'),'O(L*R)','O(1)',5),
2415:entry('reverse_odd_tree_levels',[('root','TreeNode')],'TreeNode',['trees','breadth-first search'],['root is a perfect binary tree with unique values.','Reverse node values at every odd-numbered depth; keep the tree structure unchanged.'],[([[2,3,5,8,13,21,34]],'Depth one changes from 3,5 to 5,3 while depths zero and two remain.'),([[7,13,11]],'The two values at odd depth one swap positions.')],REVERSE_CASES[2:],REVERSE,[REVERSE.replace('if depth%2','if not depth%2'),REVERSE.replace('reversed(level)','level')],['Reverses even levels including the root instead of odd levels.','Copies each level in its existing order and changes nothing.'],reverse_levels_oracle,random_reverse_levels,lesson('All nodes to reverse are grouped by depth, not by subtree.','Traverse level by level and mirror the values in odd levels.','Snapshot the current queue, assign its reversed values, then enqueue paired children.','The perfect-tree structure is untouched and every odd level receives exactly its reversed value sequence.'),'O(n)','O(w)',5),
}

BATCH[951]['examples'][0]=([[1,2,3,4,5,6,None,None,None,7,8],[1,3,2,None,6,4,5,None,None,None,None,8,7]],'Flips at selected nodes align every value and child structure in the two trees.')
BATCH[1602]['wrong'][0]=NEAREST.replace('return queue[0] if index+1<width else None','return queue[0] if queue else None')
BATCH[1602]['wrong_reasons'][0]='Returns the next queued node even when it belongs to the following depth.'
BATCH[2232]['wrong'][0]='''def minimize_parenthesized_sum(expression):
    left,right=expression.split('+')
    return f'({left}+{right})'
'''
BATCH[2232]['wrong_reasons'][0]='Always encloses both complete operands and ignores placements with useful outside multipliers.'
BATCH[998]['wrong']=[
    '''def insert_into_maximum_tree(root,val):
    return TreeNode(val)
''',
    '''def insert_into_maximum_tree(root,val):
    return root
''',
]
BATCH[998]['wrong_reasons']=[
    'Returns only the appended value and discards the entire original maximum tree.',
    'Returns the original tree unchanged and never inserts the appended value.',
]

for pid in (572,951,1214):
    for index in range(2):BATCH[pid]['params'][index]=(BATCH[pid]['params'][index][0],BATCH[pid]['params'][index][1],'treenode')
BATCH[968]['params'][0]=('root','TreeNode','treenode')
BATCH[998]['params'][0]=('root','TreeNode | None','treenode');BATCH[998]['adapter']='treenode'
BATCH[1602]['params']=[('root','TreeNode','treenode'),('u','TreeNode','treenode_ref')];BATCH[1602]['adapter']='treenode_value';BATCH[1602]['node_policy']='return_input_node';BATCH[1602]['parameter_sources']={1:0};BATCH[1602]['immutable_parameters']=[0]
BATCH[876]['params'][0]=('head','ListNode','listnode');BATCH[876]['adapter']='listnode';BATCH[876]['immutable_parameters']=[0]
BATCH[1669]['params'][0]=('list1','ListNode','listnode');BATCH[1669]['params'][3]=('list2','ListNode','listnode');BATCH[1669]['adapter']='listnode'
BATCH[2415]['params'][0]=('root','TreeNode','treenode');BATCH[2415]['adapter']='treenode';BATCH[2415]['node_policy']='values'
