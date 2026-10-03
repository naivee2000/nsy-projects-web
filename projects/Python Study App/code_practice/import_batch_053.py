"""Prefix residues, collision-free abbreviations, mine reveals, and BST gaps."""
from collections import Counter
from copy import deepcopy

from .import_batch_003 import entry
from .import_batch_050 import balanced,chain


def multiple_oracle(args):
    nums,k=args
    for left in range(len(nums)):
        total=nums[left]
        for right in range(left+1,len(nums)):
            total+=nums[right]
            if total%k==0:return True
    return False


def abbreviated(word,prefix):
    count=len(word)-prefix-1
    candidate=word[:prefix]+str(count)+word[-1] if count>0 else word
    return candidate if len(candidate)<len(word) else word


def abbreviation_oracle(args):
    # Literal simultaneous collision-resolution process, no trie or LCP search.
    words=args[0];prefixes=[1]*len(words)
    while True:
        result=[abbreviated(word,prefix) for word,prefix in zip(words,prefixes)]
        counts=Counter(result)
        colliding=[i for i,value in enumerate(result) if counts[value]>1]
        if not colliding:return result
        for i in colliding:prefixes[i]+=1


def neighbors(r,c,rows,cols):
    return [(x,y) for x in range(max(0,r-1),min(rows,r+2))
            for y in range(max(0,c-1),min(cols,c+2)) if (x,y)!=(r,c)]


def mine_oracle(args):
    board,click=args;out=deepcopy(board);rows=len(board);cols=len(board[0]);start=tuple(click)
    if board[start[0]][start[1]]=='M':out[start[0]][start[1]]='X';return out
    cells=[(r,c) for r in range(rows) for c in range(cols)]
    counts={(r,c):sum(board[x][y]=='M' for x,y in neighbors(r,c,rows,cols)) for r,c in cells}
    zeros={p for p in cells if board[p[0]][p[1]]=='E' and counts[p]==0}
    # The revealed zeros are exactly one undirected component. Union its edges,
    # then include its numbered E boundary; no simulated reveal traversal.
    parent={p:p for p in zeros}
    def find(p):
        while parent[p]!=p:parent[p]=parent[parent[p]];p=parent[p]
        return p
    for r,c in zeros:
        for q in neighbors(r,c,rows,cols):
            if q in zeros:parent[find((r,c))]=find(q)
    reveal={start}
    if start in zeros:
        component={p for p in zeros if find(p)==find(start)}
        reveal|=component
        for r,c in component:reveal.update(p for p in neighbors(r,c,rows,cols) if board[p[0]][p[1]]=='E')
    for r,c in reveal:out[r][c]=str(counts[r,c]) if counts[r,c] else 'B'
    return out


def gap_oracle(args):
    values=[v for v in args[0] if v is not None]
    return min(abs(a-b) for i,a in enumerate(values) for b in values[i+1:])


def random_multiple(rng):
    nums=[rng.randrange(21) for _ in range(rng.randint(1,45))]
    return [nums,rng.choice([1,2,3,7,31,2**31-1])]


def random_abbreviation(rng):
    words=set();n=rng.randint(1,20)
    while len(words)<n:
        length=rng.randint(2,18)
        words.add(''.join(rng.choice('abcde') for _ in range(length)))
    result=sorted(words);rng.shuffle(result)
    return [result]


def random_mine(rng):
    rows=rng.randint(1,6);cols=rng.randint(1,6)
    board=[['M' if rng.random()<.25 else 'E' for _ in range(cols)] for _ in range(rows)]
    if rng.random()<.4:
        empties=[(r,c) for r in range(rows) for c in range(cols) if board[r][c]=='E']
        if empties:board=mine_oracle([board,list(rng.choice(empties))])
    choices=[(r,c) for r in range(rows) for c in range(cols) if board[r][c] in 'ME']
    if not choices:board=[['E']];choices=[(0,0)]
    return [board,list(rng.choice(choices))]


def random_gap(rng):
    values=sorted(rng.sample(range(100001),rng.randint(2,35)))
    shape=rng.randrange(3)
    return [balanced(values) if shape==0 else chain(values) if shape==1 else chain(values[::-1],True)]


MULTIPLE='''\
def has_multiple_sum_subarray(nums,k):
    first={0:-1};remainder=0
    for index,value in enumerate(nums):
        remainder=(remainder+value)%k
        if remainder in first:
            if index-first[remainder]>=2:return True
        else:first[remainder]=index
    return False
'''
ABBREVIATION='''\
def unique_word_abbreviations(words):
    groups={}
    for word in words:
        root=groups.setdefault((len(word),word[-1]),{})
        node=root
        for char in word:
            node=node.setdefault(char,{'count':0});node['count']+=1
    result=[]
    for word in words:
        node=groups[len(word),word[-1]];prefix=0
        for char in word:
            node=node[char];prefix+=1
            if node['count']==1:break
        skipped=len(word)-prefix-1
        candidate=word[:prefix]+str(skipped)+word[-1] if skipped>0 else word
        result.append(candidate if len(candidate)<len(word) else word)
    return result
'''
MINES='''\
def reveal_minesweeper(board,click):
    rows=len(board);cols=len(board[0]);r,c=click
    if board[r][c]=='M':board[r][c]='X';return board
    pending=[(r,c)];queued={(r,c)}
    while pending:
        r,c=pending.pop()
        adjacent=[(x,y) for x in range(max(0,r-1),min(rows,r+2))
                  for y in range(max(0,c-1),min(cols,c+2)) if (x,y)!=(r,c)]
        mines=sum(board[x][y]=='M' for x,y in adjacent)
        if mines:board[r][c]=str(mines)
        else:
            board[r][c]='B'
            for x,y in adjacent:
                if board[x][y]=='E' and (x,y) not in queued:
                    queued.add((x,y));pending.append((x,y))
    return board
'''
GAP='''\
def minimum_bst_difference(root):
    stack=[];node=root;previous=None;best=100001
    while stack or node is not None:
        while node is not None:stack.append(node);node=node.left
        node=stack.pop()
        if previous is not None:best=min(best,node.val-previous)
        previous=node.val;node=node.right
    return best
'''
GAP_PARENT='''\
def minimum_bst_difference(root):
    stack=[root];best=100001
    while stack:
        node=stack.pop()
        for child in (node.left,node.right):
            if child is not None:
                best=min(best,abs(node.val-child.val));stack.append(child)
    return best
'''
GAP_RANGE='''\
def minimum_bst_difference(root):
    stack=[root];values=[]
    while stack:
        node=stack.pop();values.append(node.val)
        if node.left is not None:stack.append(node.left)
        if node.right is not None:stack.append(node.right)
    return max(values)-min(values)
'''
WORDS=['like','god','internal','me','internet','interval','intension','face','intrusion']
MINE_BOARD=[list('EEEEE'),list('EEMEE'),list('EEEEE'),list('EEEEE')]
MINE_REVEALED=[list('B1E1B'),list('B1M1B'),list('B111B'),list('BBBBB')]
LATE_WORDS=['a'*397+chr(97+i//26)+chr(97+i%26)+'z' for i in range(400)]
EARLY_WORDS=['a'+chr(97+i//26)+chr(97+i%26)+'b'*396+'z' for i in range(400)]

BATCH={
523:entry('has_multiple_sum_subarray',[('nums','list[int]'),('k','int')],'bool',['arrays','prefix-sums','hash-maps'],
    ['1 <= len(nums) <= 100,000; 0 <= nums[i] <= 1,000,000,000; sum(nums) <= 2^31-1.',
     '1 <= k <= 2^31-1. The selected subarray must be contiguous and contain at least TWO elements.',
     'Its sum may be any multiple of k, including zero; it need not equal k.'],
    [([[23,2,4,6,7],6],'The adjacent values [2,4] sum to 6, a multiple of k, and have the required length two.'),
     ([[6,1],6],'Return false. The lone 6 is divisible by 6 but is too short; the only two-element subarray sums to 7.')],
    [args for args in ([[0],1],[[6],6],[[0,0],7],[[0,1],2],[[1,0],2],[[1,1],2],[[1,2],3],
        [[23,2,6,4,7],6],[[23,2,6,4,7],13],[[1,2,3],5],[[1,2,3],7],[[5,0,0],3],
        [[1,0,1],2],[[1,0,0],3],[[0,0,1],3],[[2,4],3],[[1,1,1],3])],
    MULTIPLE,[MULTIPLE.replace('>=2','>=1'),MULTIPLE.replace('else:first[remainder]=index','first[remainder]=index')],
    ['Accepts one-element subarrays.', 'Overwrites the earliest index of a remainder, losing a later valid length-two gap.'],
    multiple_oracle,random_multiple,
    ['Equal prefix remainders identify sums divisible by k.',
     'Keep the earliest index for each remainder, and require the two prefix positions to be at least two apart.',
     'Initialize first[0]=-1. Accumulate modulo k; if a seen remainder is far enough away return true; otherwise insert only an unseen remainder.',
     'Do not overwrite the earliest position. Zero is a valid multiple, but a single zero still fails the length requirement.'],
    'The difference between two prefixes is divisible by k exactly when their '
    'remainders agree. For each current prefix the earliest equal remainder '
    'gives the longest possible segment, so discarding later occurrences cannot '
    'lose a solution. Initial remainder zero at index -1 handles a segment '
    'starting at index zero. The independent oracle enumerates every contiguous '
    'subarray of length at least two and tests its literal sum.',
    'O(n)','O(min(n,k))',difficulty=5,
    stress=[([[1]*100000,100001],False),([[1]*100000,100000],True),
            ([[0]*100000,2**31-1],True),([[10**9,10**9,147483647],2**31-1],True),
            ([[10**9,10**9,147483646],2**31-1],False)]),
527:entry('unique_word_abbreviations',[('words','list[str]')],'list[str]',['strings','tries','hash-maps'],
    ['1 <= len(words) <= 400; 2 <= word length <= 400; distinct lowercase English words.',
     'Start with first letter + omitted-character count + last letter. Increase the prefix of EVERY colliding abbreviation until results are unique.',
     'Return results in input order. Keep a word unchanged if its abbreviation would not be strictly shorter.'],
    [([WORDS],'like becomes l2e, while internal and interval need prefixes so long that their original words are retained. intension and intrusion separate at inte4n and intr4n. Preserve input order.'),
     ([['abcdef','abndef']],'Both start as a4f, then both become ab3f. Their next prefixes differ, producing abc2f and abn2f; extending just one colliding word is not allowed.')],
    [[w] for w in (['aa'],['aaa'],['abcd'],['aa','aaa'],['ab','ac'],['abcd','abce'],['abcd','abcde'],
        ['abcd','abdd'],['apple','apply'],['abcdef','abcgef'],['aabcdefghz','babcdefghz'],
        ['abbbbbz','abbbbz'],['abcdefghi','abcxefghi','abcyefghi'],['like','love','live'],
        ['a'*12],['a'*11,'b'*11])],
    ABBREVIATION,["def unique_word_abbreviations(words):\n    return [w[0]+str(len(w)-2)+w[-1] if len(w)>3 else w for w in words]\n",
        ABBREVIATION.replace("result.append(candidate if len(candidate)<len(word) else word)","result.append(candidate)")],
    ['Returns initial abbreviations without resolving collisions.', 'Keeps abbreviations that are as long as or longer than the original word.'],
    abbreviation_oracle,random_abbreviation,
    ['Only words with equal length and final letter can collide at an equal prefix length.',
     'Build a prefix trie per length/final-letter group and count words passing through each node.',
     'For each word, walk until a node has count one. Use that prefix, the remaining internal count, and last letter; keep the original if no length is saved.',
     'A group key must include length and final letter. Use original input order for output, and expand all members of a collision group conceptually.'],
    'Within a fixed length/final-letter group, a prefix is unique exactly when '
    'its trie node belongs to one word. The first such prefix is precisely where '
    'the repeated collision-expansion process stops. Different groups cannot '
    'collide because the omitted count and final letter distinguish them. '
    'Construct and query the tries in O(S) time and space for S total input '
    'characters, then enforce strict shortening. An independent oracle directly '
    'simulates simultaneous abbreviation collisions instead of using a trie.',
    'O(S)','O(S)',difficulty=8,
    stress=[([LATE_WORDS],LATE_WORDS),([EARLY_WORDS],[w[:3]+'396z' for w in EARLY_WORDS]),
            ([['a'*400]],['a398a'])]),
529:entry('reveal_minesweeper',[('board','list[list[str]]'),('click','list[int]')],'list[list[str]]',['matrices','recursion','depth-first-search'],
    ['1 <= rows, columns <= 50. Input cells are M (unrevealed mine), E (unrevealed empty), B (revealed blank), or a digit 1..8.',
     'click=[row,column] is in bounds and points to M or E. Input boards contain no X; clicking M creates X and changes no other cell.',
     'Mine counts and expansion use all EIGHT neighbors, including diagonals. A revealed numbered cell stops expansion; a blank B expands to adjacent unrevealed empty cells.',
     'Return the resulting rectangular board. Existing revealed cells and unclicked mines remain unchanged. Returning a correctly updated copy is also allowed.'],
    [([MINE_BOARD,[3,0]],'The bottom-left empty region expands through blanks and stops at numbered cells beside the mine. E at [0,2] stays hidden behind that numbered boundary; expansion does not cross a numbered cell.'),
     ([MINE_REVEALED,[1,2]],'The clicked M becomes X. Every other cell, including the still-hidden E above it and all already-revealed cells, remains unchanged.')],
    [args for args in ([ [['E']],[0,0] ],[ [['M']],[0,0] ],
        [[list('EM')],[0,0]],[[list('ME')],[0,0]],[[list('EEE')],[0,1]],
        [[list('E'),list('E'),list('M')],[0,0]],[[list('EE'),list('EM')],[0,0]],
        [[list('MMM'),list('MEM'),list('MMM')],[1,1]],
        [[list('MEE'),list('EEE'),list('EEE')],[2,2]],
        [[list('EME'),list('EEE'),list('EME')],[1,1]],
        [[list('EEMEE')],[0,0]],[[list('EEE'),list('EEE')],[0,2]],
        [[list('MEE'),list('EEE'),list('EEM')],[1,1]],
        [[list('B1M'),list('B1E')],[1,2]],[[list('E1M')],[0,0]])],
    MINES,[MINES.replace("if (x,y)!=(r,c)]","if (x==r) != (y==c)]"),
           MINES.replace("if mines:board[r][c]=str(mines)","if mines:board[r][c]=str(mines)\n        elif pending is not None:board[r][c]='B'")],
    ['Counts and expands only orthogonal neighbors, missing diagonal mines.', 'Reveals only the clicked blank instead of expanding its empty region.'],
    mine_oracle,random_mine,
    ['Revealing a blank recursively exposes neighbors, but a number forms a stopping boundary.',
     'Use DFS or BFS from the click. Count adjacent mines before deciding whether to expand.',
     'If clicked M set X and stop. Otherwise pop an E cell, count eight neighbors; write a digit if nonzero, else B and enqueue unseen E neighbors.',
     'Mark queued cells to prevent repeated work. An explicit stack has the same recursive flood-fill behavior without overflowing Python on a 50-by-50 empty board.'],
    'Only zero-adjacent-mine empty cells propagate the reveal. Their connected '
    'component and its adjacent empty boundary determine every changed cell. '
    'The explicit stack implements the recursive rule, while a queued set '
    'ensures each cell is processed once. Every cell has at most eight neighbors, '
    'giving O(rows*columns) time and space. The independent oracle constructs '
    'connected components with union-find and reveals the selected component '
    'plus its numbered boundary rather than simulating the stack.',
    'O(rows*columns)','O(rows*columns)',difficulty=5,
    stress=[([[list('E'*50) for _ in range(50)],[0,0]],[list('B'*50) for _ in range(50)]),
            ([[list('M'*50) for _ in range(50)],[25,25]],
             [list('M'*50) if r!=25 else list('M'*25+'X'+'M'*24) for r in range(50)])]),
530:entry('minimum_bst_difference',[('root','TreeNode')],'int',['trees','binary-search-trees','recursion'],
    ['2 <= node count <= 10,000; tree height <= 200; 0 <= node.val <= 100,000; the input is a binary search tree.',
     'Return the smallest absolute value difference between ANY TWO DISTINCT nodes, not just parent/child pairs. Equal values at distinct nodes give zero.',
     'Do not change node values or links. Inorder values are non-decreasing; use this order rather than the JSON level-order sequence. Recursive or iterative traversal is allowed.'],
    [([[4,2,6,1,3]],'Return 1, for example between values 1 and 2. The tree serialization is level order, not a sorted list of values.'),
     ([[10,2,20,None,9]],'Return 1 between nodes 9 and 10. They are not parent and child: 9 is the right child of 2, inside the left subtree of 10.')],
    [[tree] for tree in ([0,None,100000],[100000,0],[2,1],[1,None,2],[2,1,3],[5,1,9],
        [1,0,48,None,None,12,49],[8,3,10,1,6,None,14,None,None,4,7,13],
        [5,5],[5,None,5],[10,0,100],[100,20,None,None,99],[20,10,30,None,19,21],
        [0,None,1,None,2],[3,2,None,1])],
    GAP,[GAP_PARENT,GAP_RANGE],
    ['Checks only edges rather than every possible pair of distinct nodes.', 'Returns the entire range instead of the minimum pair gap.'],
    gap_oracle,random_gap,
    ['In a sorted sequence, a closest pair appears at adjacent positions.',
     'Inorder traversal supplies that sorted sequence without sorting or changing the tree.',
     'Traverse left/node/right recursively or with a stack, compare each value to the previous visited value, and retain the smallest difference.',
     'Do not confuse an adjacent inorder pair with a parent/child edge. The tree height is at most 200, so ordinary recursive inorder traversal is supported.'],
    'For sorted values a<=b<=c, c-a is at least either neighboring gap. Thus '
    'the global minimum occurs between adjacent inorder visits. Track only the '
    'previous value and best gap using recursive inorder traversal or an explicit O(h) stack. Each '
    'node is pushed and popped once, so time is O(n). The independent oracle '
    'takes every pair of non-null JSON values; it does not traverse inorder or '
    'assume the closest pair is adjacent. Input nodes and links remain unchanged.',
    'O(n)','O(h)',difficulty=3,
    stress=[([chain(list(range(200)))],1),([chain(list(range(199,-1,-1)),True)],1),
            ([balanced(list(range(0,100000,10)))],10),([balanced([17]*10000)],0)])
}
BATCH[530]['params'][0]=('root','TreeNode','treenode')
BATCH[530]['immutable_parameters']=[0]
BATCH[527]['prerequisites']=['strings','hash-maps']
