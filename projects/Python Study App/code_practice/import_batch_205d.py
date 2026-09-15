"""Recursive trees, echo substrings, connectivity, and two-finger dynamic programming."""
from itertools import product

from .import_batch_055 import entry


class OracleNode:
    def __init__(self, value):
        self.val, self.left, self.right = value, None, None


def tree_from_values(values):
    if not values:
        return None
    root = OracleNode(values[0]);queue=[root];index=1
    while queue and index < len(values):
        node=queue.pop(0)
        if index < len(values) and values[index] is not None:
            node.left=OracleNode(values[index]);queue.append(node.left)
        index += 1
        if index < len(values) and values[index] is not None:
            node.right=OracleNode(values[index]);queue.append(node.right)
        index += 1
    return root


def tree_values(root):
    if root is None:return []
    result=[];queue=[root]
    while queue:
        node=queue.pop(0)
        if node is None:result.append(None)
        else:result.append(node.val);queue.extend((node.left,node.right))
    while result and result[-1] is None:result.pop()
    return result


def random_tree(rng, maximum=18):
    values=[rng.randint(1,12)];frontier=1;nodes=1
    while frontier and nodes<maximum:
        frontier-=1
        for _ in range(2):
            if nodes<maximum and rng.random()<.7:
                values.append(rng.randint(1,12));frontier+=1;nodes+=1
            else:values.append(None)
    while values and values[-1] is None:values.pop()
    return values


def grandparent_oracle(args):
    root=tree_from_values(args[0]);answer=0;queue=[(root,None,None)]
    while queue:
        node,parent,grandparent=queue.pop(0)
        if grandparent is not None and grandparent%2==0:answer+=node.val
        if node.left:queue.append((node.left,node.val,parent))
        if node.right:queue.append((node.right,node.val,parent))
    return answer


def random_grandparent(rng):return [random_tree(rng)]


def echo_oracle(args):
    text=args[0];found=set()
    for left in range(len(text)):
        for right in range(left+2,len(text)+1,2):
            middle=(left+right)//2
            if text[left:middle]==text[middle:right]:found.add(text[left:right])
    return len(found)


def random_echo(rng):return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,12)))]


def connected_oracle(args):
    size,connections=args
    if len(connections)<size-1:return -1
    graph=[[] for _ in range(size)]
    for left,right in connections:graph[left].append(right);graph[right].append(left)
    seen=set();components=0
    for start in range(size):
        if start in seen:continue
        components+=1;stack=[start];seen.add(start)
        while stack:
            for neighbor in graph[stack.pop()]:
                if neighbor not in seen:seen.add(neighbor);stack.append(neighbor)
    return components-1


def random_connected(rng):
    size=rng.randint(1,12);all_edges=[(a,b) for a in range(size) for b in range(a+1,size)]
    rng.shuffle(all_edges);count=rng.randint(0,len(all_edges))
    return [size,[list(edge) for edge in all_edges[:count]]]


def finger_distance(first,second):
    if first<0:return 0
    ar,ac=divmod(first,6);br,bc=divmod(second,6)
    return abs(ar-br)+abs(ac-bc)


def fingers_oracle(args):
    letters=[ord(char)-65 for char in args[0]];answer=10**9
    for choices in product((0,1),repeat=len(letters)):
        positions=[-1,-1];cost=0
        for letter,which in zip(letters,choices):
            cost+=finger_distance(positions[which],letter);positions[which]=letter
        answer=min(answer,cost)
    return answer


def random_fingers(rng):return [''.join(rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(rng.randint(2,10)))]


def delete_oracle(args):
    root=tree_from_values(args[0]);target=args[1]
    def prune(node):
        if node is None:return None
        node.left=prune(node.left);node.right=prune(node.right)
        return None if node.left is None and node.right is None and node.val==target else node
    return tree_values(prune(root))


def random_delete(rng):
    values=random_tree(rng);return [values,rng.randint(1,12)]


GRANDPARENT='''def sum_even_grandparent_nodes(root):
    def visit(node,parent,grandparent):
        if node is None:return 0
        own=node.val if grandparent is not None and grandparent%2==0 else 0
        return own+visit(node.left,node.val,parent)+visit(node.right,node.val,parent)
    return visit(root,None,None)
'''

ECHO='''def count_distinct_echo_substrings(text):
    size=len(text);base=911382323;mod1=1000000007;mod2=1000000009
    def hashes(mod):
        prefix=[0]*(size+1);powers=[1]*(size+1)
        for index,char in enumerate(text):prefix[index+1]=(prefix[index]*base+ord(char))%mod;powers[index+1]=powers[index]*base%mod
        return prefix,powers
    first,power1=hashes(mod1);second,power2=hashes(mod2)
    def part(prefix,powers,left,right,mod):return (prefix[right]-prefix[left]*powers[right-left])%mod
    found=set()
    for half in range(1,size//2+1):
        for left in range(size-2*half+1):
            middle=left+half;right=middle+half
            a=(part(first,power1,left,middle,mod1),part(second,power2,left,middle,mod2))
            b=(part(first,power1,middle,right,mod1),part(second,power2,middle,right,mod2))
            if a==b:found.add((2*half,part(first,power1,left,right,mod1),part(second,power2,left,right,mod2)))
    return len(found)
'''

CONNECTED='''def minimum_network_operations(n,connections):
    if len(connections)<n-1:return -1
    parent=list(range(n))
    def find(node):
        while parent[node]!=node:parent[node]=parent[parent[node]];node=parent[node]
        return node
    components=n
    for left,right in connections:
        a,b=find(left),find(right)
        if a!=b:parent[a]=b;components-=1
    return components-1
'''

FINGERS='''def minimum_two_finger_distance(word):
    def distance(first,second):
        if first<0:return 0
        ar,ac=divmod(first,6);br,bc=divmod(second,6);return abs(ar-br)+abs(ac-bc)
    states={(-1,-1):0}
    for char in word:
        letter=ord(char)-65;following={}
        for (left,right),cost in states.items():
            for state,total in (((letter,right),cost+distance(left,letter)),((left,letter),cost+distance(right,letter))):
                following[state]=min(following.get(state,10**9),total)
        states=following
    return min(states.values())
'''

DELETE='''def delete_target_leaves(root,target):
    if root is None:return None
    root.left=delete_target_leaves(root.left,target);root.right=delete_target_leaves(root.right,target)
    if root.left is None and root.right is None and root.val==target:return None
    return root
'''

DELETE_PREORDER='''def delete_target_leaves(root,target):
    if root is None:return None
    if root.left is None and root.right is None and root.val==target:return None
    root.left=delete_target_leaves(root.left,target);root.right=delete_target_leaves(root.right,target)
    return root
'''


BATCH={
1315:entry('sum_even_grandparent_nodes',[('root','TreeNode')],'int',['trees','recursion','depth-first search'],['root is a nonempty binary tree.','A node qualifies when its grandparent exists and has an even value.','Return the sum of all qualifying node values.'],[([[6,7,8,2,7,1,3,9,None,1,4,None,None,None,5]],'Nodes with even-valued grandparents sum to eighteen.'),([[1,2,3]],'No node has a grandparent, so the sum is zero.')],[[tree] for tree in ([2,1,3,4,5,6,7],[1],[2,1],[2,1,3,4],[1,2,3,4,5,6,7],[6,7,8,2,7,1,3,9,None,1,4,None,None,None,5],[1,2,3],[4,None,5,None,6],[2,3,4,None,None,5,6],[3,2,4,1,None,None,5],[8,1,3,2,4,None,6],[5,4,3,2,1],[10,9,8,7,6,5,4],[1,2,None,3,None,4])],GRANDPARENT,[GRANDPARENT.replace('grandparent%2==0','parent%2==0'),GRANDPARENT.replace('grandparent is not None and grandparent%2==0','grandparent is not None and grandparent%2==1')],['Checks the parent rather than the grandparent.','Sums nodes with odd-valued grandparents instead of even ones.'],grandparent_oracle,random_grandparent,['Pass parent and grandparent values down the recursion.','At each node, add its value only when the remembered grandparent is even.','Recurse to children with current value becoming parent and old parent becoming grandparent.','Each node is visited with exactly its two ancestors, so the predicate is evaluated once and correctly.'],'A depth-first traversal carries the previous two ancestor values. The current node contributes precisely when the older value exists and is even. Passing values rather than searching upward keeps every visit constant-time. The oracle independently reconstructs the serialized tree and performs breadth-first traversal with explicit ancestor tuples.','O(n)','O(height)',5),
1316:entry('count_distinct_echo_substrings',[('text','str')],'int',['strings','rolling hash'],['text is a nonempty lowercase string.','An echo substring is nonempty and equals some string concatenated with itself.','Count distinct echo substring values, not their number of occurrences.'],[(['abcabcabc'],'The distinct echoes are abcabc, bcabca, and cabcab.'),(['aaaaa'],'The distinct echo values are aa and aaaa.')],[[text] for text in 'a aa ab abab abcabc abcabcabc aaaaa ababa abcabca xyzxyzx aabbaabb bananaabcdabcd zzzzzzzz abcdef'.split()],ECHO,[ECHO.replace('found.add((2*half,', 'found.add((left,2*half,'),ECHO.replace('for half in range(1,size//2+1)', 'for half in range(1,min(2,size//2)+1)')],['Includes the start position in the identity and counts repeated occurrences separately.','Checks only echo halves of length one.'],echo_oracle,random_echo,['An echo has an even length and two equal adjacent halves.','Use prefix rolling hashes to compare each pair of halves in constant time.','Try every start and half-length; store the full substring hash together with its length in a set.','Every possible even substring is tested, while the set merges equal echo values from different positions.'],'Two prefix hashes make adjacent-half equality and full-substring identity constant-time for each of O(n²) candidates. Including length prevents values of different sizes from sharing an identity. The independent oracle uses direct substring equality and stores actual strings on short seeded inputs.','O(n^2)','O(number of distinct echoes+n)',8),
1319:entry('minimum_network_operations',[('n','int'),('connections','list[list[int]]')],'int',['graphs','union find'],['Computers are numbered zero through n-1 and connections are distinct undirected cables.','One operation may remove a redundant cable and reconnect two components.','Return the minimum operations to connect all computers, or -1 if there are fewer than n-1 cables.'],[([4,[[0,1],[0,2],[1,2]]],'One redundant cable can connect computer three to the existing component.'),([6,[[0,1],[0,2],[0,3],[1,2]]],'Four cables cannot connect six computers, so the answer is minus one.')],[[n,e] for n,e in ((1,[]),(2,[]),(2,[[0,1]]),(3,[[0,1]]),(3,[[0,1],[1,2]]),(3,[[0,1],[0,2],[1,2]]),(4,[[0,1],[0,2],[1,2]]),(6,[[0,1],[0,2],[0,3],[1,2]]),(5,[[0,1],[1,2],[2,3],[3,4]]),(5,[[0,1],[1,2],[0,2],[3,4]]),(4,[[0,1],[2,3],[1,2]]),(6,[[0,1],[1,2],[2,0],[3,4],[4,5]]),(7,[[0,1],[1,2],[2,0],[3,4],[4,5],[5,3]]),(4,[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]))],CONNECTED,[CONNECTED.replace('if len(connections)<n-1:return -1','if not connections:return -1'),CONNECTED.replace('return components-1','return n-1')],['Checks only whether any cable exists rather than whether enough cables exist.','Returns the cost of connecting isolated computers and ignores components already joined.'],connected_oracle,random_connected,['At least n-1 total cables are necessary.','Union endpoints while counting how many connected components remain.','If enough cables exist, every redundant cable can be moved, so return components minus one.','Joining c components requires and can be achieved with exactly c-1 replacement cables.'],'After the cable-count feasibility check, union-find determines the number of connected components. A graph with n nodes and c components contains enough redundant edges to join them whenever it has at least n-1 total edges, and exactly c-1 moves are necessary. The oracle independently builds adjacency lists and counts components by depth-first search.','O(n+connections*alpha(n))','O(n)',5),
1320:entry('minimum_two_finger_distance',[('word','str')],'int',['strings','dynamic programming'],['word contains two to three hundred uppercase letters on the six-column alphabet keyboard.','Moving a finger costs Manhattan distance; either finger may start anywhere for free.','Type letters in order and return the minimum total movement of two fingers.'],[(['CAKE'],'One finger types C then K for distance two, while the other types A then E for distance one.'),(['HAPPY'],'An optimal division of letters between the fingers costs six.')],[[word] for word in 'AB AA AZ CAKE HAPPY YEAR NEW CODE TYPE QUICK HELLO WORLD ABCXYZ QWERTY'.split()],FINGERS,[FINGERS.replace('{(-1,-1):0}','{(0,0):0}'),FINGERS.replace('return abs(ar-br)+abs(ac-bc)','return max(abs(ar-br),abs(ac-bc))')],['Starts both fingers on A and incorrectly charges for their initial placement.','Uses diagonal Chebyshev distance instead of Manhattan distance.'],fingers_oracle,random_fingers,['A state is the pair of letters currently occupied by the two fingers.','Both initial positions are unplaced, making their first movement cost zero.','For each next letter, transition by moving either the left or right finger and retain the cheapest duplicate state.','Every assignment of typed letters to the two fingers corresponds to exactly one transition sequence.'],'Dynamic programming maps the two current finger positions to minimum cost after each typed prefix. For the next letter, move either finger and merge identical resulting states by minimum. A sentinel position has zero distance to any first letter. The oracle independently enumerates all 2^n finger-choice sequences on seeded short words.','O(length*26^2)','O(26^2)',8),
1325:entry('delete_target_leaves',[('root','TreeNode | None'),('target','int')],'TreeNode | None',['trees','recursion','postorder'],['Remove every leaf whose value equals target.','A parent that becomes a matching leaf after child removal must also be removed.','Return the remaining tree root, or None if repeated removal deletes it.'],[([[1,2,3,2,None,2,4],2],'Removing the original twos makes the left parent two a leaf too, so it is also removed.'),([[1,3,3,3,2],3],'Only matching leaves are removed; the nonleaf root value one remains.')],[[tree,target] for tree,target in (([1],1),([1],2),([1,2],2),([2,2],2),([1,2,3,2,None,2,4],2),([1,3,3,3,2],3),([1,2,2,2,2],2),([2,2,2],2),([1,None,2,None,2],2),([5,4,6,4,None,None,4],4),([1,2,3],4),([3,3,None,3],3),([1,1,1,1],1),([7,2,7,2,2,7,2],2))],DELETE,[DELETE_PREORDER,DELETE.replace('root.left is None and root.right is None','root.left is None or root.right is None')],['Tests leaf status before recursion and misses parents that become matching leaves.','Treats a matching node with only one missing child as a leaf and discards a live subtree.'],delete_oracle,random_delete,['A parent can become removable only after both children have been processed.','Use postorder recursion and replace each child pointer with its pruned result.','After pruning children, return None exactly when both are absent and the current value equals target.','Postorder repeats the leaf-removal rule upward in one traversal, including deletion of the original root.'],'Recursively prune left and right subtrees before testing the current node. This converts the repeated global removal process into one postorder pass: every descendant deletion is already reflected when its parent is evaluated. The oracle independently constructs a separate tree, applies the same declarative fixed-point rule, and serializes the result.','O(n)','O(height)',5),
}

BATCH[1315]['params'][0]=('root','TreeNode','treenode')
BATCH[1325]['params'][0]=('root','TreeNode | None','treenode')
BATCH[1325]['adapter']='treenode'
