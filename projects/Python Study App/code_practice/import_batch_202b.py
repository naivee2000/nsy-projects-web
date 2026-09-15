"""BST insertion/conversion, tree parsing/boundaries, and grid-path recursion."""
from functools import lru_cache
from .import_batch_055 import entry

def _tree(values):
    if not values:return None
    root=[values[0],None,None];queue=[root];index=1
    while queue and index<len(values):
        node=queue.pop(0)
        for child in (1,2):
            if index<len(values) and values[index] is not None:
                node[child]=[values[index],None,None];queue.append(node[child])
            index+=1
    return root

def _values(root):
    if root is None:return []
    out=[];queue=[root]
    while queue:
        node=queue.pop(0)
        if node is None:out.append(None)
        else:out.append(node[0]);queue.extend(node[1:])
    while out and out[-1] is None:out.pop()
    return out

def insert_oracle(a):
    values,value=a;root=_tree(values)
    if root is None:return [value]
    node=root
    while True:
        child=1 if value<node[0] else 2
        if node[child] is None:node[child]=[value,None,None];break
        node=node[child]
    return _values(root)
def random_insert(r):
    values=r.sample(range(-100,101),r.randint(0,12));tree=[]
    for value in values:tree=insert_oracle([tree,value])
    value=r.choice([x for x in range(-100,101) if x not in values]);return [tree,value]
def parse_oracle(a):
    s=a[0];index=0
    def parse():
        nonlocal index
        sign=-1 if s[index]=='-' else 1
        if s[index]=='-':index+=1
        value=0
        while index<len(s) and s[index].isdigit():value=value*10+int(s[index]);index+=1
        node=[sign*value,None,None]
        for child in (1,2):
            if index<len(s) and s[index]=='(':
                index+=1
                if s[index]!=')':node[child]=parse()
                index+=1
        return node
    root=parse();out=[];queue=[root]
    while queue:
        node=queue.pop(0)
        if node is None:out.append(None)
        else:out.append(node[0]);queue.extend(node[1:])
    while out and out[-1] is None:out.pop()
    return out
def random_parse(r):
    def make(depth):
        value=str(r.randint(-20,20))
        if depth==0 or r.random()<.35:return value
        left=make(depth-1) if r.random()<.8 else ''
        right=make(depth-1) if r.random()<.5 else ''
        return value+'('+left+')'+(('('+right+')') if right or r.random()<.3 else '')
    return [make(3)]
def greater_oracle(a):
    tree=a[0];values=sorted((x for x in tree if x is not None),reverse=True);total=0;mapping={}
    for value in values:total+=value;mapping[value]=total
    return [None if x is None else mapping[x] for x in tree]
def random_bst(r):
    values=r.sample(range(0,200),r.randint(1,15));tree=[]
    for value in values:tree=insert_oracle([tree,value])
    return [tree]
def boundary_oracle(a):
    root=_tree(a[0])
    if root is None:return []
    def leaf(node):return node is not None and node[1] is None and node[2] is None
    answer=[root[0]];node=root[1]
    while node:
        if not leaf(node):answer.append(node[0])
        node=node[1] or node[2]
    def leaves(node):
        if node is None:return
        if leaf(node):
            if node is not root:answer.append(node[0])
        else:leaves(node[1]);leaves(node[2])
    leaves(root);right=[];node=root[2]
    while node:
        if not leaf(node):right.append(node[0])
        node=node[2] or node[1]
    return answer+right[::-1]
def random_boundary(r):
    tree=[r.randint(0,99)]
    for i in range(r.randint(0,20)):
        if i>=len(tree) or tree[i] is None:continue
        tree.extend([r.randint(0,99) if r.random()<.7 else None,r.randint(0,99) if r.random()<.7 else None])
    while tree and tree[-1] is None:tree.pop()
    return [tree]
def paths_oracle(a):
    m,n,moves,row,col=a;states={(row,col):1};answer=0
    for _ in range(moves):
        nxt={}
        for (i,j),count in states.items():
            for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
                x,y=i+di,j+dj
                if 0<=x<m and 0<=y<n:nxt[x,y]=nxt.get((x,y),0)+count
                else:answer+=count
        states=nxt
    return answer%(10**9+7)
def random_paths(r):
    m,n=r.randint(1,5),r.randint(1,5);return [m,n,r.randint(0,8),r.randrange(m),r.randrange(n)]

INSERT='''def insert_into_bst(root,val):
    if root is None:return TreeNode(val)
    node=root
    while True:
        if val<node.val:
            if node.left is None:node.left=TreeNode(val);break
            node=node.left
        else:
            if node.right is None:node.right=TreeNode(val);break
            node=node.right
    return root
'''
PARSE='''def construct_tree_from_string(s):
    index=0
    def parse():
        nonlocal index
        start=index
        if s[index]=='-':index+=1
        while index<len(s) and s[index].isdigit():index+=1
        node=TreeNode(int(s[start:index]))
        if index<len(s) and s[index]=='(':
            index+=1
            if s[index]!=')':node.left=parse()
            index+=1
        if index<len(s) and s[index]=='(':
            index+=1
            if s[index]!=')':node.right=parse()
            index+=1
        return node
    return parse()
'''
GREATER='''def convert_bst_to_greater_tree(root):
    total=0
    def visit(node):
        nonlocal total
        if node is None:return
        visit(node.right);total+=node.val;node.val=total;visit(node.left)
    visit(root);return root
'''
BOUNDARY='''def binary_tree_boundary(root):
    if root is None:return []
    answer=[root.val]
    node=root.left
    while node:
        if node.left or node.right:answer.append(node.val)
        node=node.left or node.right
    def leaves(node):
        if node is None:return
        if node.left is None and node.right is None:
            if node is not root:answer.append(node.val)
            return
        leaves(node.left);leaves(node.right)
    leaves(root);right=[];node=root.right
    while node:
        if node.left or node.right:right.append(node.val)
        node=node.right or node.left
    return answer+right[::-1]
'''
PATHS='''def count_out_of_boundary_paths(m,n,maxMove,startRow,startColumn):
    from functools import lru_cache
    mod=10**9+7
    @lru_cache(None)
    def visit(row,col,moves):
        if not (0<=row<m and 0<=col<n):return 1
        if moves==0:return 0
        return sum(visit(row+dr,col+dc,moves-1) for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)))%mod
    return visit(startRow,startColumn,maxMove)
'''

BATCH={
701:entry('insert_into_bst',[('root','TreeNode | None'),('val','int')],'TreeNode',['trees','binary search trees'],['root is a valid BST with unique integer values and val is absent.','Insert val at the unique search position without changing existing values.','Return the root, or the new node for an empty tree.'],[([[4,2,7,1,3],5],'Five follows right from four then left from seven.'),([[],1],'An empty tree becomes a single node containing one.')],[[t,v] for t,v in [([],1),([4,2,7,1,3],5),([2,1,3],4),([2,1,3],0),([1],2),([1],0),([5,3,8],4),([10,5,15,None,7],6),([0],-1),([8,4,12,2,6,10,14],9),([3,1,5],2),([20,10,30],25),([7,3,9,1,5],8),([2,None,4],3)]],INSERT,[INSERT.replace('val<node.val','val>node.val'),INSERT.replace('return root','return node')],['Traverses the wrong BST branch.','Returns the inserted leaf rather than the tree root.'],insert_oracle,random_insert,['Follow the same comparisons used by BST search.','At the first missing child in val’s direction, attach a new node.','Handle an empty root, otherwise iterate until insertion.','Uniqueness makes the comparison path and missing attachment point deterministic.'],'O(height)','O(1)',5),
536:entry('construct_tree_from_string',[('s','str')],'TreeNode',['trees','recursion','parsing'],['s contains signed integers and balanced child parentheses.','After a node value, the first group is its left child and the optional second group is its right child; empty () denotes a missing child.','Return the represented tree.'],[(['4(2(3)(1))(6(5))'],'The root is four with subtrees rooted at two and six.'),(['-4(2)(3)'],'Signed root negative four has children two and three.')],[[s] for s in ['1','-1','4(2(3)(1))(6(5))','-4(2)(3)','1(2)','1()(2)','1(2)(3)','10(-2)(30)','5(4(3(2(1))))','1(2(4)(5))(3)','0(-1)(1)','7()(8(9))','12(3(-4))(5)','2(1)(4(3))']],PARSE,[PARSE.replace('node.left=parse()','node.right=parse()',1),PARSE.replace("if s[index]=='-'","if False")],['Stores the first child on the right.','Fails to parse negative node values.'],parse_oracle,random_parse,['A recursive call consumes exactly one signed node and its balanced child groups.','Maintain a shared string index so nested groups need no substring rescanning.','Parse the signed integer, then up to two parenthesized children in left-right order.','Balanced parentheses delimit each recursive subtree and the index returns just after its closing parenthesis.'],'O(len(s))','O(height)',5),
538:entry('convert_bst_to_greater_tree',[('root','TreeNode | None')],'TreeNode | None',['trees','recursion','binary search trees'],['root is a BST with distinct integer values.','Replace each value by its original value plus all original values greater than it.','Mutate and return the tree.'],[([[4,1,6,0,2,5,7,None,None,None,3,None,None,None,8]],'Reverse inorder accumulation produces the shown greater-tree values.'),([[1,0,2]],'Values become three, three, and two in level order.')],[[t] for t in [[],[1],[1,0,2],[4,1,6,0,2,5,7,None,None,None,3,None,None,None,8],[2,1,3],[5,3,8],[0,-2,3],[10,5,15,2,7,12,20],[3,None,4],[3,2,None,1],[8,4,12,2,6,10,14],[1,None,2,None,3],[5,1,9,None,3,7],[20,10,30]]],GREATER,[GREATER.replace('visit(node.right)','visit(node.left)',1),GREATER.replace('total+=node.val','total=node.val')],['Traverses smaller values first.','Resets rather than accumulates the greater-value sum.'],greater_oracle,random_bst,['Reverse inorder visits BST values from greatest to smallest.','Maintain a running sum of original visited values.','Visit right, add and replace node value, then visit left.','When a node is processed, the accumulator contains exactly it and every greater original value.'],'O(n)','O(height)',5),
545:entry('binary_tree_boundary',[('root','TreeNode | None')],'list[int]',['trees','recursion'],['Return root, nonleaf left boundary, all leaves left-to-right, then reversed nonleaf right boundary.','Do not duplicate leaves or the root.','An empty tree returns an empty list.'],[([[1,None,2,3,4]],'The boundary visits root one, leaves three and four, then right boundary two.'),([[1]],'A single root appears once.')],[[t] for t in [[],[1],[1,None,2,3,4],[1,2,3],[1,2,None,3],[1,None,2,None,3],[1,2,3,4,5,6,7],[1,2,3,None,4,None,5],[1,2,None,None,3,None,None,4],[1,None,2,3,None,4],[10,5,15,2,7,12,20],[1,2,3,4,None,None,7],[5,4,None,3,None,2],[5,None,6,None,7]]],BOUNDARY,[BOUNDARY.replace('right[::-1]','right'),BOUNDARY.replace('if node.left or node.right','if True',1)],['Returns the right boundary top-down instead of bottom-up.','Includes left-boundary leaves and duplicates them in the leaf traversal.'],boundary_oracle,random_boundary,['Separate the boundary into three nonoverlapping parts after the root.','Walk the outer left and right chains excluding leaves, and recursively collect leaves left-to-right.','Append the saved right chain in reverse.','Excluding leaves from side chains prevents duplicates while the traversal order matches the required perimeter.'],'O(n)','O(height)',5),
576:entry('count_out_of_boundary_paths',[('m','int'),('n','int'),('maxMove','int'),('startRow','int'),('startColumn','int')],'int',['matrices','recursion','dynamic programming'],['Start inside an m by n grid and move one cell in four directions.','Count paths that leave the grid in at most maxMove moves, modulo 1000000007.','Paths stop when they first leave.'],[([2,2,2,0,0],'Six move sequences leave the two-by-two grid within two moves.'),([1,3,3,0,1],'Twelve paths leave the one-row grid within three moves.')],[[m,n,k,r,c] for m,n,k,r,c in [(1,1,0,0,0),(1,1,1,0,0),(2,2,2,0,0),(1,3,3,0,1),(3,3,1,1,1),(3,3,2,1,1),(2,3,4,0,1),(4,4,3,2,2),(1,2,5,0,0),(5,1,4,2,0),(2,2,5,1,1),(3,4,0,1,2),(5,5,6,0,0),(4,2,7,3,1)]],PATHS,[PATHS.replace('if moves==0:return 0','if moves<=1:return 0'),PATHS.replace('return 1','return 0',1)],['Stops one move too early.','Does not count crossing the boundary as a completed path.'],paths_oracle,random_paths,['The state is row, column, and moves remaining.','Leaving contributes one immediately; staying inside with no moves contributes zero.','Memoize the sum of four next states modulo the limit.','Each move sequence has a unique first step and is counted exactly when it first crosses the grid edge.'],'O(m*n*maxMove)','O(m*n*maxMove)',5),
}
BATCH[701]['params'][0]=('root','TreeNode | None','treenode');BATCH[701]['adapter']='treenode'
BATCH[536]['adapter']='treenode'
BATCH[538]['params'][0]=('root','TreeNode | None','treenode');BATCH[538]['adapter']='treenode';BATCH[538]['node_policy']='reuse_input_nodes'
BATCH[545]['params'][0]=('root','TreeNode | None','treenode')
BATCH[538].pop('node_policy',None)
BATCH[536]['wrong'][1]=PARSE.replace("start=index\n        if s[index]=='-':index+=1","if s[index]=='-':index+=1\n        start=index")
