"""Inclusion counting, swap components, grid-state BFS, palindrome deletion, and path DFS."""
from itertools import combinations
from math import gcd
from .import_batch_055 import entry

def ugly_o(a):
    n,x,y,z=a;count=0;value=0
    while count<n:
        value+=1
        if value%x==0 or value%y==0 or value%z==0:count+=1
    return value
def rugly(r):return [r.randint(1,80),r.randint(2,12),r.randint(2,12),r.randint(2,12)]

def swaps_o(a):
    text,pairs=a;graph=[[] for _ in text]
    for x,y in pairs:graph[x].append(y);graph[y].append(x)
    answer=list(text);seen=set()
    for start in range(len(text)):
        if start in seen:continue
        component=[];seen.add(start);todo=[start]
        while todo:
            node=todo.pop();component.append(node)
            for nxt in graph[node]:
                if nxt not in seen:seen.add(nxt);todo.append(nxt)
        for index,char in zip(sorted(component),sorted(text[i] for i in component)):answer[index]=char
    return ''.join(answer)
def rswaps(r):
    n=r.randint(1,12);text=''.join(r.choice('abcde') for _ in range(n));pairs=[]
    for i in range(n):
        for j in range(i):
            if r.random()<.15:pairs.append([i,j])
    return [text,pairs]

def snake_states(grid):
    n=len(grid);states=[]
    for r in range(n):
        for c in range(n-1):
            if grid[r][c]==grid[r][c+1]==0:states.append((r,c,0))
    for r in range(n-1):
        for c in range(n):
            if grid[r][c]==grid[r+1][c]==0:states.append((r,c,1))
    return states
def snake_o(a):
    grid=a[0];states=snake_states(grid);index={state:i for i,state in enumerate(states)};edges=[[] for _ in states]
    for p,(r,c,o) in enumerate(states):
        candidates=[]
        if o==0:
            candidates.extend(((r,c+1,0),(r+1,c,0),(r,c,1)))
        else:candidates.extend(((r+1,c,1),(r,c+1,1),(r,c,0)))
        for state in candidates:
            if state in index:
                if state[2]!=o:
                    if r+1>=len(grid) or c+1>=len(grid) or grid[r+1][c] or grid[r+1][c+1]:continue
                edges[p].append(index[state])
    if (0,0,0) not in index or (len(grid)-1,len(grid)-2,0) not in index:return -1
    distance=[999]*len(states);distance[index[(0,0,0)]]=0
    for _ in states:
        for i in range(len(states)):
            for j in edges[i]:distance[j]=min(distance[j],distance[i]+1)
    answer=distance[index[(len(grid)-1,len(grid)-2,0)]];return answer if answer<999 else -1
def rsnake(r):
    n=r.randint(2,6);grid=[[0 if r.random()<.75 else 1 for _ in range(n)] for _ in range(n)];grid[0][0]=grid[0][1]=grid[-1][-1]=grid[-1][-2]=0;return [grid]

def palindrome_o(a):
    text,k=a;n=len(text)
    for kept in range(n,n-k-1,-1):
        for indexes in combinations(range(n),kept):
            value=''.join(text[i] for i in indexes)
            if value==value[::-1]:return True
    return False
def rpalindrome(r):
    text=''.join(r.choice('abcd') for _ in range(r.randint(1,10)));return [text,r.randint(0,len(text))]

def gold_o(a):
    grid=a[0];rows=len(grid);cols=len(grid[0]);cells=[(i,j) for i in range(rows) for j in range(cols) if grid[i][j]];position={cell:k for k,cell in enumerate(cells)};memo={}
    def visit(cell,mask):
        key=(cell,mask)
        if key in memo:return memo[key]
        i,j=cell;best=grid[i][j]
        for nxt in ((i+1,j),(i-1,j),(i,j+1),(i,j-1)):
            bit=1<<position[nxt] if nxt in position else 0
            if bit and not mask&bit:best=max(best,grid[i][j]+visit(nxt,mask|bit))
        memo[key]=best;return best
    return max((visit(cell,1<<position[cell]) for cell in cells),default=0)
def rgold(r):
    rows,cols=r.randint(1,4),r.randint(1,4);grid=[[r.randint(0,8) if r.random()<.6 else 0 for _ in range(cols)] for _ in range(rows)]
    while sum(v>0 for row in grid for v in row)>10:
        i,j=r.randrange(rows),r.randrange(cols);grid[i][j]=0
    return [grid]

UGLY='''from math import gcd
def nth_three_divisor_number(n,a,b,c):
    def lcm(x,y):return x//gcd(x,y)*y
    ab,ac,bc=lcm(a,b),lcm(a,c),lcm(b,c);abc=lcm(ab,c)
    left,right=1,n*min(a,b,c)
    while left<right:
        middle=(left+right)//2;count=middle//a+middle//b+middle//c-middle//ab-middle//ac-middle//bc+middle//abc
        if count>=n:right=middle
        else:left=middle+1
    return left
'''
SMALLEST='''def smallest_string_with_swaps(s,pairs):
    parent=list(range(len(s)))
    def find(x):
        if parent[x]!=x:parent[x]=find(parent[x])
        return parent[x]
    for a,b in pairs:parent[find(a)]=find(b)
    groups={}
    for i,char in enumerate(s):groups.setdefault(find(i),[]).append(char)
    for chars in groups.values():chars.sort(reverse=True)
    return ''.join(groups[find(i)].pop() for i in range(len(s)))
'''
SNAKE='''def minimum_snake_moves(grid):
    n=len(grid);start=(0,0,0);goal=(n-1,n-2,0);queue=[(start,0)];seen={start}
    for (row,col,vertical),distance in queue:
        if (row,col,vertical)==goal:return distance
        moves=[]
        if not vertical:
            if col+2<n and grid[row][col+2]==0:moves.append((row,col+1,0))
            if row+1<n and grid[row+1][col]==grid[row+1][col+1]==0:moves.extend(((row+1,col,0),(row,col,1)))
        else:
            if row+2<n and grid[row+2][col]==0:moves.append((row+1,col,1))
            if col+1<n and grid[row][col+1]==grid[row+1][col+1]==0:moves.extend(((row,col+1,1),(row,col,0)))
        for move in moves:
            if move not in seen:seen.add(move);queue.append((move,distance+1))
    return -1
'''
PALINDROME='''def is_k_deletion_palindrome(s,k):
    n=len(s);dp=[[0]*n for _ in range(n)]
    for length in range(2,n+1):
        for left in range(n-length+1):
            right=left+length-1
            if s[left]==s[right]:dp[left][right]=dp[left+1][right-1] if length>2 else 0
            else:dp[left][right]=1+min(dp[left+1][right],dp[left][right-1])
    return dp[0][n-1]<=k
'''
GOLD='''def maximum_gold_path(grid):
    rows,cols=len(grid),len(grid[0])
    def visit(row,col):
        value=grid[row][col];grid[row][col]=0;best=0
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            r,c=row+dr,col+dc
            if 0<=r<rows and 0<=c<cols and grid[r][c]:best=max(best,visit(r,c))
        grid[row][col]=value;return value+best
    return max((visit(i,j) for i in range(rows) for j in range(cols) if grid[i][j]),default=0)
'''

BATCH={
1201:entry('nth_three_divisor_number',[('n','int'),('a','int'),('b','int'),('c','int')],'int',['math','binary search'],['A positive integer is eligible when divisible by a, b, or c.','Return the nth eligible positive integer.','Inputs are positive and the answer fits a signed 32-bit integer.'],[([3,2,3,5],'The first three eligible values are two, three, and four.'),([4,2,3,4],'The fourth eligible value is six.')],[[*x] for x in [(1,2,3,5),(2,2,3,5),(3,2,3,5),(4,2,3,4),(5,2,4,8),(10,2,3,7),(7,3,5,11),(12,4,6,9),(20,5,7,9),(8,2,2,3),(15,6,10,15),(30,7,8,9),(25,3,11,13),(40,4,9,10)]],UGLY,[UGLY.replace('+middle//abc','-middle//abc'),UGLY.replace('count>=n','count>n')],['Subtracts the triple intersection instead of restoring it.','Finds the first value whose count exceeds n, skipping exact boundaries.'],ugly_o,rugly,['Count eligible values at or below a candidate with inclusion-exclusion.','Binary-search the smallest candidate whose count reaches n.','Use pair and triple least common multiples for intersections.','The count is monotone, and minimal feasibility identifies exactly the nth eligible value.'],'O(log answer)','O(1)',5),
1202:entry('smallest_string_with_swaps',[('s','str'),('pairs','list[list[int]]')],'str',['graphs','union find','strings'],['Each pair allows its two indices to swap any number of times.','Swaps compose transitively within connected index components.','Return the lexicographically smallest reachable string.'],[(['dcab',[[0,3],[1,2]]],'Sorting characters inside the two components produces bacd.'),(['dcab',[[0,3],[1,2],[0,2]]],'All indices connect, so the globally sorted string abcd is reachable.')],[[s,p] for s,p in [('a',[]),('dcab',[[0,3],[1,2]]),('dcab',[[0,3],[1,2],[0,2]]),('cba',[[0,1]]),('cba',[[1,2]]),('zxy',[]),('bbca',[[0,3]]),('edcba',[[0,1],[1,2],[3,4]]),('abc',[[0,2]]),('ba',[[0,1]]),('aaaa',[[0,3]]),('gfedcb',[[0,5],[1,4],[2,3]]),('algorithm',[[0,1],[1,2],[5,6]]),('cabba',[[0,4],[1,3]])]],SMALLEST,[SMALLEST.replace('sort(reverse=True)','sort()'),SMALLEST.replace('parent[find(a)]=find(b)','parent[a]=b')],['Sorts ascending but pops from the end, assigning largest characters first.','Links raw vertices rather than roots and can break transitive components.'],swaps_o,rswaps,['Connected swap indices can realize any permutation of their characters.','Union paired indices and collect characters by component root.','Sort each component’s characters and consume its smallest at indices from left to right.','Independent component sorting minimizes the earliest possible character at every output position.'],'O((n+p) alpha+n log n)','O(n)',5),
1210:entry('minimum_snake_moves',[('grid','list[list[int]]')],'int',['matrices','breadth-first search'],['The snake occupies two adjacent zero cells and begins horizontally at the top-left pair.','It may move right/down while horizontal, down/right while vertical, or rotate clockwise/counterclockwise through a clear two-by-two square.','Return minimum moves to finish horizontally in the bottom-right pair, or -1.'],[([[[0,0,0,0,0,1],[1,1,0,0,1,0],[0,0,0,0,1,1],[0,0,1,0,1,0],[0,1,1,0,0,0],[0,1,1,0,0,0]]],'A shortest legal sequence reaches the goal in eleven moves.'),([[[0,0],[0,0]]],'One downward move places the horizontal snake at the bottom goal.')],[[g] for g in [[[0,0],[0,0]],[[0,0],[1,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,0,1],[0,0,0],[0,0,0]],[[0,0,0],[1,1,0],[0,0,0]],[[0,0,0],[0,1,0],[0,0,0]],[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],[[0,0,1,0],[0,0,0,0],[0,1,0,0],[0,0,0,0]],[[0,0,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],[[0,0,0],[0,0,1],[0,0,0]],[[0,0,0],[1,0,0],[0,0,0]],[[0,0,0,0],[0,1,0,0],[0,0,0,0],[0,0,0,0]],[[0,0,0,0],[0,0,1,0],[0,0,0,0],[0,1,0,0]],[[0,0,0],[0,0,0],[1,0,0]]]],SNAKE,[SNAKE.replace('distance+1','distance+2'),SNAKE.replace("moves.extend(((row+1,col,0),(row,col,1)))","moves.append((row+1,col,0))")],['Charges two for each legal move.','Never permits clockwise rotation from horizontal to vertical.'],snake_o,rsnake,['Represent a state by the upper-left or leftmost cell plus orientation.','Breadth-first search legal translations and rotations, checking every newly occupied cell.','Deduplicate states and stop at the horizontal bottom-right state.','Every transition costs one, so BFS returns the minimum legal move count.'],'O(n^2)','O(n^2)',8),
1216:entry('is_k_deletion_palindrome',[('s','str'),('k','int')],'bool',['strings','dynamic programming'],['Delete at most k characters from s.','Return whether the remaining characters can form a palindrome without reordering.','s is nonempty and k is nonnegative.'],[(['abcdeca',2],'Deleting b and e leaves acdca, a palindrome.'),(['abbababa',1],'Deleting one suitable character produces a palindrome.')],[[*x] for x in [('a',0),('ab',0),('ab',1),('abcdeca',2),('abbababa',1),('racecar',0),('abcdef',5),('abc',1),('aaab',1),('banana',1),('abcdba',1),('cabba',1),('zzxyzz',2),('character',4)]],PALINDROME,[PALINDROME.replace('1+min','2+min'),PALINDROME.replace('<=k','<k')],['Charges two deletions whenever endpoint characters differ.','Rejects strings requiring exactly k deletions.'],palindrome_o,rpalindrome,['Compute minimum deletions for every substring.','Matching endpoints inherit the inner cost; differing endpoints delete one side plus the better remaining substring.','Fill intervals from short to long and compare the whole-string cost with k.','The recurrence exhausts the only two choices at a mismatch and preserves matching endpoints optimally.'],'O(n^2)','O(n^2)',8),
1219:entry('maximum_gold_path',[('grid','list[list[int]]')],'int',['matrices','recursion','backtracking'],['Start at any positive cell and move orthogonally.','Collect a cell’s gold once; zero cells cannot be entered and no cell may be revisited.','Return the maximum gold collectable by one path.'],[([[[0,6,0],[5,8,7],[0,9,0]]],'The path nine-eight-seven collects twenty-four.'),([[[1,0,7],[2,0,6],[3,4,5],[0,3,0],[9,0,20]]],'The best connected path collects twenty-eight.')],[[g] for g in [[[0]],[[5]],[[0,6,0],[5,8,7],[0,9,0]],[[1,0,7],[2,0,6],[3,4,5],[0,3,0],[9,0,20]],[[1,2],[3,4]],[[1,0],[0,2]],[[1,2,3]],[[1],[2],[3]],[[0,1,0],[2,3,4]],[[5,0,6],[7,8,9]],[[1,1],[1,1]],[[0,0],[0,0]],[[10,1,0],[0,2,3]],[[1,2,0],[4,3,5],[0,6,7]]]],GOLD,[GOLD.replace('value+best','best'),GOLD.replace('grid[row][col]=value','grid[row][col]=0',1)],['Omits the gold in the current cell from every path total.','Fails to restore cells after exploring one branch, corrupting later starts and alternatives.'],gold_o,rgold,['Try every positive cell as a starting point.','During DFS, temporarily mark the current cell zero, explore four positive unvisited neighbors, then restore it.','Return current gold plus the best continuation.','Temporary marking enforces simple paths, restoration makes branches independent, and exhaustive starts cover every possible path.'],'O(cells*4^positive cells)','O(positive cells)',5),
}
BATCH[1202]['sample_contract_adapter']={'source_sample':'Input s = "dcab", pairs = [[0,3],[1,2]] → Output "bacd" Explaination: Swap s[0] and s[3], s = "bcad" Swap s[1] and s[2], s = "bacd".','arguments':['dcab',[[0,3],[1,2]]],'expected':'bacd','reason':'The workbook appends a misspelled explanation to the output literal; this adapter preserves the stated inputs and result while separating that prose.'}
