"""Digit construction, ranked voting, linked-list/tree recursion, 0-1 BFS, and tree DP."""
import heapq
from itertools import permutations

from .import_batch_055 import entry


class Node:
    def __init__(self,value):self.val=value;self.left=self.right=None
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
def random_tree(rng,maximum=16):
    values=[rng.randint(1,8)];frontier=1;nodes=1
    while frontier and nodes<maximum:
        frontier-=1
        for _ in range(2):
            if nodes<maximum and rng.random()<.7:values.append(rng.randint(1,8));frontier+=1;nodes+=1
            else:values.append(None)
    while values and values[-1] is None:values.pop()
    return values


def multiple_oracle(args):
    digits=args[0];best=''
    for mask in range(1,1<<len(digits)):
        selected=[digits[i] for i in range(len(digits)) if mask>>i&1]
        if sum(selected)%3:continue
        candidate=''.join(map(str,sorted(selected,reverse=True)))
        candidate='0' if candidate and candidate[0]=='0' else candidate
        if (len(candidate),candidate)>(len(best),best):best=candidate
    return best
def random_multiple(rng):return [[rng.randint(0,9) for _ in range(rng.randint(1,9))]]


def votes_oracle(args):
    votes=args[0];teams=votes[0];counts={team:[0]*len(teams) for team in teams}
    for vote in votes:
        for rank,team in enumerate(vote):counts[team][rank]+=1
    return ''.join(sorted(teams,key=lambda team:tuple(-value for value in counts[team])+(team,)))
def random_votes(rng):
    teams=''.join(chr(65+i) for i in range(rng.randint(1,7)));votes=[]
    for _ in range(rng.randint(1,12)):
        values=list(teams);rng.shuffle(values);votes.append(''.join(values))
    return [votes]


def subpath_oracle(args):
    wanted,values=args;root=make_tree(values);nodes=[];queue=[root]
    while queue:
        node=queue.pop(0);nodes.append(node)
        if node.left:queue.append(node.left)
        if node.right:queue.append(node.right)
    for start in nodes:
        states=[(start,0)]
        while states:
            node,index=states.pop()
            if node is None or node.val!=wanted[index]:continue
            if index==len(wanted)-1:return True
            states.extend(((node.left,index+1),(node.right,index+1)))
    return False
def random_subpath(rng):
    tree=random_tree(rng);return [[rng.randint(1,8) for _ in range(rng.randint(1,6))],tree]


def grid_cost_oracle(args):
    grid=args[0];rows,columns=len(grid),len(grid[0]);dist={(0,0):0};heap=[(0,0,0)];dirs=((0,1),(0,-1),(1,0),(-1,0))
    while heap:
        cost,row,column=heapq.heappop(heap)
        if cost!=dist[(row,column)]:continue
        if (row,column)==(rows-1,columns-1):return cost
        for code,(dr,dc) in enumerate(dirs,1):
            nr,nc=row+dr,column+dc
            if 0<=nr<rows and 0<=nc<columns:
                nxt=cost+(grid[row][column]!=code)
                if nxt<dist.get((nr,nc),10**9):dist[(nr,nc)]=nxt;heapq.heappush(heap,(nxt,nr,nc))
def random_grid_cost(rng):
    rows,columns=rng.randint(1,5),rng.randint(1,5);return [[[rng.randint(1,4) for _ in range(columns)] for _ in range(rows)]]


def zigzag_oracle(args):
    root=make_tree(args[0]);nodes=[];queue=[root]
    while queue:
        node=queue.pop(0);nodes.append(node)
        if node.left:queue.append(node.left)
        if node.right:queue.append(node.right)
    answer=0
    for start in nodes:
        for first_left in (True,False):
            node=start;left=first_left;length=0
            while node:
                node=node.left if left else node.right
                if node:length+=1;answer=max(answer,length)
                left=not left
    return answer
def random_zigzag(rng):return [random_tree(rng)]


MULTIPLE='''def largest_multiple_of_three(digits):
    counts=[0]*10
    for digit in digits:counts[digit]+=1
    remainder=sum(digits)%3
    def remove(modulo,amount):
        for digit in range(10):
            while amount and digit%3==modulo and counts[digit]:counts[digit]-=1;amount-=1
        return amount==0
    if remainder and not remove(remainder,1):
        if not remove(3-remainder,2):return ''
    answer=''.join(str(digit)*counts[digit] for digit in range(9,-1,-1))
    return '0' if answer and answer[0]=='0' else answer
'''
VOTES='''def rank_teams_by_votes(votes):
    width=len(votes[0]);counts={team:[0]*width for team in votes[0]}
    for vote in votes:
        for rank,team in enumerate(vote):counts[team][rank]+=1
    return ''.join(sorted(counts,key=lambda team:tuple(-value for value in counts[team])+(team,)))
'''
SUBPATH='''def linked_list_path_in_tree(head,root):
    def matches(node,item):
        if item is None:return True
        if node is None or node.val!=item.val:return False
        return matches(node.left,item.next) or matches(node.right,item.next)
    if root is None:return False
    return matches(root,head) or linked_list_path_in_tree(head,root.left) or linked_list_path_in_tree(head,root.right)
'''
COST='''def minimum_direction_change_cost(grid):
    from collections import deque
    rows,columns=len(grid),len(grid[0]);distance=[[10**9]*columns for _ in range(rows)];distance[0][0]=0;queue=deque([(0,0)]);dirs=((0,1),(0,-1),(1,0),(-1,0))
    while queue:
        row,column=queue.popleft();cost=distance[row][column]
        for code,(dr,dc) in enumerate(dirs,1):
            nr,nc=row+dr,column+dc
            if 0<=nr<rows and 0<=nc<columns:
                nxt=cost+(grid[row][column]!=code)
                if nxt<distance[nr][nc]:
                    distance[nr][nc]=nxt
                    if nxt==cost:queue.appendleft((nr,nc))
                    else:queue.append((nr,nc))
    return distance[-1][-1]
'''
ZIGZAG='''def longest_tree_zigzag(root):
    answer=0
    def visit(node,left_length,right_length):
        nonlocal answer
        if node is None:return
        answer=max(answer,left_length,right_length)
        visit(node.left,right_length+1,0);visit(node.right,0,left_length+1)
    visit(root,0,0);return answer
'''

BATCH={
1363:entry('largest_multiple_of_three',[('digits','list[int]')],'str',['arrays','greedy','counting'],['digits contains one to ten thousand digits from zero through nine.','Choose and rearrange any nonempty subset to make the numerically largest multiple of three.','Return it without leading zeroes; return "0" for all-zero choices and an empty string when impossible.'],[([[8,1,9]],'All three digits form descending 981, which is divisible by three.'),([[0,0,0,0]],'Every arrangement is zero, represented canonically as one zero.')],[[x] for x in ([1],[3],[0],[0,0,0,0],[8,1,9],[8,6,7,1,0],[1,1],[2,2],[1,1,1],[2,2,2],[9,8,6,5],[5,5,5,2],[4,4,1,1],[9,0,0,0])],MULTIPLE,[MULTIPLE.replace('for digit in range(10)','for digit in range(9,-1,-1)',1),MULTIPLE.replace("return '0' if answer and answer[0]=='0' else answer","return answer")],['Removes the largest remainder-fixing digits instead of the smallest, producing a smaller number.','Returns multiple leading zeroes instead of the canonical single zero.'],multiple_oracle,random_multiple,['Divisibility by three depends only on the digit sum.','If the sum remainder is one or two, remove the fewest and smallest digits whose remainders repair it.','Then emit all retained digits from nine down to zero and collapse an all-zero answer.','Maximizing retained digit count dominates; among equal lengths, removing smaller digits maximizes descending lexicographic value.'],'Count digits and inspect the total modulo three. Repair remainder one by removing one smallest remainder-one digit or two smallest remainder-two digits; use the symmetric rule for remainder two. Prefer removing one digit whenever possible. The oracle independently enumerates every subset on seeded short inputs and constructs its best descending number.','O(n)','O(1)',8),
1366:entry('rank_teams_by_votes',[('votes','list[str]')],'str',['strings','sorting','counting'],['Every vote ranks the same distinct uppercase teams exactly once.','Compare teams by first-place counts, then second-place counts, continuing through every rank.','If all position counts tie, rank alphabetically.'],[([['ABC','ACB','ABC','ACB','ACB']],'A has five first-place votes; C beats B on second-place votes, producing ACB.'),([['ZMNAGUEDSJYLBOPHRQICWFXTVK']],'With one vote, return its ranking unchanged.')],[[v] for v in (["ABC"],["ABC","ACB","ABC","ACB","ACB"],["WXYZ","XYZW"],["BCA","CAB","CBA","ABC","ACB","BAC"],["M","M"],["AB","BA"],["ABC","BCA","CAB"],["ZMNAGUEDSJYLBOPHRQICWFXTVK"],["ABC","ABC"],["CBA","CBA","ABC"],["ABCD","BACD","BCAD"],["XY","XY","YX"],["QWER","WQER","EWQR","RWQE"],["ABCDE","EDCBA"])],VOTES,[VOTES.replace('tuple(-value for value in counts[team])','(-counts[team][0],)'),VOTES.replace('+(team,)','+(-ord(team),)')],['Uses only first-place totals and ignores lower-rank tie breakers.','Breaks complete ties in reverse alphabetical order.'],votes_oracle,random_votes,['Count each team separately at every rank position.','Sort by the negated vector of position counts, then by the team letter.','Tuple comparison applies the first differing rank automatically.','This ordering is exactly the rule’s lexicographic sequence of tie breakers.'],'Build one count vector per team. Sorting by its negated entries gives descending vote counts at each successive rank; appending the letter gives ascending alphabetical fallback. The oracle independently constructs the same rule with explicit positional counts and a separate tuple key.','O(votes*teams+teams log teams)','O(teams^2)',5),
1367:entry('linked_list_path_in_tree',[('head','ListNode'),('root','TreeNode')],'bool',['linked lists','trees','recursion'],['head and root are nonempty.','Match the linked-list values along a downward parent-to-child path that may start at any tree node.','Return whether every list node can be matched contiguously.'],[([[4,2,8],[1,4,4,None,2,2,None,1,None,6,8,None,None,None,None,1,3]],'Starting at the right child valued four gives the downward sequence four, two, eight.'),([[1,4,2,6],[1,4,4,None,2,2,None,1,None,6,8]],'No single downward branch contains the whole list in order.')],[[a,t] for a,t in (([1],[1]),([2],[1]),([1,2],[1,2]),([1,3],[1,2,3]),([4,2,8],[1,4,4,None,2,2,None,1,None,6,8,None,None,None,None,1,3]),([1,4,2,6],[1,4,4,None,2,2,None,1,None,6,8]),([1,2,3],[1,2,None,3]),([2,4],[1,2,3,4,5]),([3,6],[1,2,3,4,5,6,7]),([1,1,1],[1,1,1,1]),([5,4],[5,4,6]),([4,5],[1,2,3,4,5]),([7,8],[7,None,8]),([2,1],[1,2,2,1,None,None,1]))],SUBPATH,[SUBPATH.replace('return matches(root,head) or linked_list_path_in_tree(head,root.left) or linked_list_path_in_tree(head,root.right)','return matches(root,head)'),SUBPATH.replace('matches(node.left,item.next) or matches(node.right,item.next)','matches(node.left,item.next) and matches(node.right,item.next)')],['Tests a matching path only from the tree root instead of every possible start.','Requires both child branches to match the remaining list instead of either one.'],subpath_oracle,random_subpath,['Separate choosing a starting tree node from matching an already-started path.','The matcher compares current values and recursively follows either child with head.next.','At each tree node, try the matcher there, then search both subtrees for another start.','Every downward path has one starting node, and the two recursive layers enumerate every start and every child choice.'],'Use one recursion to match a fixed start and another to enumerate starting tree nodes. A match advances the list and exactly one tree edge per step; reaching the end of the list succeeds. The oracle independently builds a tree and explores explicit (tree node, list index) stacks from every node.','O(tree nodes*list length)','O(tree height+list length)',5),
1368:entry('minimum_direction_change_cost',[('grid','list[list[int]]')],'int',['matrices','graphs','zero-one breadth-first search'],['Cell values one, two, three, and four point right, left, down, and up respectively.','Moving in the indicated direction costs zero; choosing any other direction means changing that cell and costs one.','Return the minimum cost of a path from top-left to bottom-right.'],[([[[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]]],'Following each row and changing direction between rows costs three.'),([[[1,2],[4,3]]],'The signs already permit a zero-cost route to the destination.')],[[g] for g in ([[1]],[[1,1]],[[2,2]],[[3],[3]],[[4],[4]],[[1,2],[4,3]],[[1,1],[1,1]],[[2,2],[2,2]],[[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]],[[3,3,1],[2,2,2],[1,1,4]],[[4,4],[4,4]],[[1,3],[2,4]],[[2,1,3],[4,3,2]],[[1,4,3],[3,2,1],[4,1,2]])],COST,[COST.replace('dirs=((0,1),(0,-1),(1,0),(-1,0))','dirs=((0,-1),(0,1),(1,0),(-1,0))'),COST.replace('nxt=cost+(grid[row][column]!=code)','nxt=cost+1')],['Swaps the meaning of right and left arrows.','Charges one for every move, even when following the existing sign.'],grid_cost_oracle,random_grid_cost,['Treat each cell as a graph node with outgoing edge weights zero or one.','Use a deque: zero-cost moves go to the front and changed-sign moves go to the back.','Relax a neighbor only when its new cost improves the stored distance.','Zero-one BFS processes these binary-weight edges in nondecreasing distance like Dijkstra without a heap.'],'The four possible outgoing moves have cost zero for the cell’s current arrow and one otherwise. A 0–1 BFS pushes zero edges to the deque front and one edges to the back while applying ordinary distance relaxation. The oracle independently uses heap-based Dijkstra on seeded grids.','O(rows*columns)','O(rows*columns)',8),
1372:entry('longest_tree_zigzag',[('root','TreeNode')],'int',['trees','recursion','dynamic programming'],['root is nonempty.','A ZigZag path alternates left and right child edges and may start at any node.','Return its length in edges, so a one-node path has length zero.'],[([[1,None,1,1,1,None,None,1,1,None,1,None,None,None,1]],'The longest alternating downward path contains three edges.'),([[1]],'A single node has a zero-edge ZigZag path.')],[[t] for t in ([1],[1,2],[1,None,2],[1,2,3],[1,2,3,4,None,None,5],[1,None,1,1,1,None,None,1,1,None,1,None,None,None,1],[1,2,None,None,3,4,None,None,5],[1,2,3,None,4,5,None],[1,2,3,4,5,6,7],[1,None,2,None,3,None,4],[1,2,None,3,None,4],[1,2,3,None,4,None,5],[8,4,12,2,6,10,14],[1,1,1,1,1,1,1])],ZIGZAG,[ZIGZAG.replace('answer=max(answer,left_length,right_length)','answer=max(answer,left_length+1,right_length+1)'),ZIGZAG.replace('visit(node.left,right_length+1,0);visit(node.right,0,left_length+1)','visit(node.left,right_length+1,0)')],['Counts nodes rather than edges, making every result one too large.','Traverses only left children and misses ZigZag paths inside right subtrees.'],zigzag_oracle,random_zigzag,['At each node, track the current path length whose latest edge came from each direction.','Moving left extends the prior right-ending path and resets the left-ending alternative; moving right is symmetric.','Update a global maximum, then recurse with the two transformed lengths.','Every start is represented by a reset-to-zero state, while every alternating continuation extends the opposite direction only.'],'Depth-first traversal carries the best alternating length ending at each node from each incoming direction. A left edge extends a right-ending path and resets the other state, and vice versa. Taking a maximum at every node covers all starts. The oracle independently walks a forced alternating direction from every node.','O(n)','O(height)',5),
}
BATCH[1367]['params']=[('head','ListNode','listnode'),('root','TreeNode','treenode')]
for problem_id in (1372,):BATCH[problem_id]['params'][0]=('root','TreeNode','treenode')
