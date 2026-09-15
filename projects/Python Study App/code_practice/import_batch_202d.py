"""Rising-water paths, skylines, linked components, islands, cards, and complete trees."""
from collections import deque
from heapq import heappop,heappush
from .import_batch_055 import entry

def swim_oracle(a):
    grid=a[0];n=len(grid);best={(0,0):grid[0][0]};heap=[(grid[0][0],0,0)]
    while heap:
        cost,i,j=heappop(heap)
        if (i,j)==(n-1,n-1):return cost
        if cost!=best[i,j]:continue
        for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
            x,y=i+di,j+dj
            if 0<=x<n and 0<=y<n and max(cost,grid[x][y])<best.get((x,y),10**9):best[x,y]=max(cost,grid[x][y]);heappush(heap,(best[x,y],x,y))
def random_swim(r):
    n=r.randint(1,6);values=list(range(n*n));r.shuffle(values);return [[values[i*n:(i+1)*n] for i in range(n)]]
def skyline_oracle(a):
    grid=a[0];return sum(min(max(grid[i]),max(row[j] for row in grid))-grid[i][j] for i in range(len(grid)) for j in range(len(grid[0])))
def random_skyline(r):
    n=r.randint(1,8);return [[[r.randint(0,30) for _ in range(n)] for _ in range(n)]]
def components_oracle(a):
    values,chosen=a;wanted=set(chosen);return sum(value in wanted and (i==0 or values[i-1] not in wanted) for i,value in enumerate(values))
def random_components(r):
    values=r.sample(range(100),r.randint(1,30));return [values,r.sample(values,r.randint(1,len(values)))]
def bridge_oracle(a):
    grid=a[0];n=len(grid);seen=set();islands=[]
    for i in range(n):
        for j in range(n):
            if grid[i][j] and (i,j) not in seen:
                island=set();todo=[(i,j)];seen.add((i,j))
                while todo:
                    x,y=todo.pop();island.add((x,y))
                    for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
                        p,q=x+di,y+dj
                        if 0<=p<n and 0<=q<n and grid[p][q] and (p,q) not in seen:seen.add((p,q));todo.append((p,q))
                islands.append(island)
    return min(abs(a-c)+abs(b-d)-1 for a,b in islands[0] for c,d in islands[1])
def random_bridge(r):
    n=r.randint(2,8);a=(r.randrange(n),r.randrange(n));b=(r.randrange(n),r.randrange(n))
    while b==a or abs(a[0]-b[0])+abs(a[1]-b[1])==1:b=(r.randrange(n),r.randrange(n))
    grid=[[0]*n for _ in range(n)];grid[a[0]][a[1]]=grid[b[0]][b[1]]=1;return [grid]
def deck_oracle(a):
    deck=a[0];positions=deque(range(len(deck)));answer=[0]*len(deck)
    for value in sorted(deck):
        answer[positions.popleft()]=value
        if positions:positions.append(positions.popleft())
    return answer
def random_deck(r):return [r.sample(range(1,1000),r.randint(1,40))]
def complete_oracle(a):
    tree=_canonical_tree(a[0]);gap=False
    for value in tree:
        if value is None:gap=True
        elif gap:return False
    return True
def random_complete(r):
    n=r.randint(1,30);tree=[r.randint(0,99)]
    for _ in range(1,n):tree.append(None if r.random()<.25 else r.randint(0,99))
    while tree and tree[-1] is None:tree.pop()
    return [_canonical_tree(tree or [1])]

def _canonical_tree(values):
    if not values:return []
    root=[values[0],None,None];queue=[root];index=1
    while queue and index<len(values):
        node=queue.pop(0)
        for child in (1,2):
            if index<len(values) and values[index] is not None:
                node[child]=[values[index],None,None];queue.append(node[child])
            index+=1
    out=[];queue=[root]
    while queue:
        node=queue.pop(0)
        if node is None:out.append(None)
        else:out.append(node[0]);queue.extend(node[1:])
    while out and out[-1] is None:out.pop()
    return out

SWIM='''def minimum_swim_time(grid):
    from heapq import heappop,heappush
    n=len(grid);heap=[(grid[0][0],0,0)];seen=set()
    while heap:
        time,row,col=heappop(heap)
        if (row,col) in seen:continue
        seen.add((row,col))
        if (row,col)==(n-1,n-1):return time
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            r,c=row+dr,col+dc
            if 0<=r<n and 0<=c<n and (r,c) not in seen:heappush(heap,(max(time,grid[r][c]),r,c))
'''
SKYLINE='''def maximum_skyline_increase(grid):
    rows=[max(row) for row in grid];cols=[max(column) for column in zip(*grid)]
    return sum(min(rows[i],cols[j])-value for i,row in enumerate(grid) for j,value in enumerate(row))
'''
COMPONENTS='''def linked_list_component_count(head,nums):
    wanted=set(nums);answer=0;inside=False
    while head:
        if head.val in wanted:
            if not inside:answer+=1
            inside=True
        else:inside=False
        head=head.next
    return answer
'''
BRIDGE='''def shortest_island_bridge(grid):
    from collections import deque
    n=len(grid);queue=deque();seen=set()
    start=next((i,j) for i in range(n) for j in range(n) if grid[i][j]);stack=[start];seen.add(start)
    while stack:
        i,j=stack.pop();queue.append((i,j,0))
        for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
            x,y=i+di,j+dj
            if 0<=x<n and 0<=y<n and grid[x][y] and (x,y) not in seen:seen.add((x,y));stack.append((x,y))
    while queue:
        i,j,distance=queue.popleft()
        for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
            x,y=i+di,j+dj
            if 0<=x<n and 0<=y<n and (x,y) not in seen:
                if grid[x][y]:return distance
                seen.add((x,y));queue.append((x,y,distance+1))
'''
DECK='''def deck_order_for_increasing_reveal(deck):
    from collections import deque
    queue=deque()
    for value in sorted(deck,reverse=True):
        if queue:queue.appendleft(queue.pop())
        queue.appendleft(value)
    return list(queue)
'''
COMPLETE='''def is_complete_binary_tree(root):
    from collections import deque
    queue=deque([root]);gap=False
    while queue:
        node=queue.popleft()
        if node is None:gap=True;continue
        if gap:return False
        queue.extend((node.left,node.right))
    return True
'''

BATCH={
778:entry('minimum_swim_time',[('grid','list[list[int]]')],'int',['matrices','graphs','heaps'],['grid is n by n and contains each elevation 0..n^2-1 once.','At time t, traverse four-neighbor cells whose elevations are at most t.','Return the earliest time connecting top-left to bottom-right.'],[([[[0,2],[1,3]]],'Elevation three at the destination determines the earliest time.'),([[[0]]],'The start is already the destination at time zero.')],[[g] for g in [[[0]],[[0,2],[1,3]],[[3,2],[0,1]],[[0,1],[2,3]],[[8,7,6],[5,4,3],[2,1,0]],[[0,1,2],[5,4,3],[6,7,8]],[[0,5,2],[1,4,3],[8,7,6]],[[15,14,13,12],[11,10,9,8],[7,6,5,4],[3,2,1,0]],[[0,7,2],[1,6,3],[8,5,4]],[[5,0,1],[6,7,2],[4,3,8]],[[0,3],[2,1]],[[1,2],[3,0]],[[0,8,7],[1,2,6],[4,3,5]],[[24,23,22,21,20],[19,18,17,16,15],[14,13,12,11,10],[9,8,7,6,5],[4,3,2,1,0]]]],SWIM,[SWIM.replace('max(time,grid[r][c])','grid[r][c]'),SWIM.replace('heap=[(grid[0][0],0,0)]','heap=[(0,0,0)]')],['Forgets the maximum elevation already crossed.','Assumes the starting elevation is available at time zero.'],swim_oracle,random_swim,['Path cost is its maximum elevation, not a sum.','Use Dijkstra where extending a path costs max(previous cost,next elevation).','Pop the lowest-cost cell and stop at the destination.','The minimax path cost is monotone, so the first finalized destination cost is optimal.'],'O(n^2 log n)','O(n^2)',8),
807:entry('maximum_skyline_increase',[('grid','list[list[int]]')],'int',['matrices','greedy'],['grid is a nonempty square matrix of nonnegative heights.','Increasing buildings must preserve every row maximum and column maximum.','Return the greatest total increase.'],[([[[3,0,8,4],[2,4,5,7],[9,2,6,3],[0,3,1,0]]],'Raising each cell to the smaller of its row and column maxima adds thirty-five.'),([[[1]]],'A single building cannot increase without changing both skylines.')],[[g] for g in [[[1]],[[0]],[[1,2],[3,4]],[[3,0,8,4],[2,4,5,7],[9,2,6,3],[0,3,1,0]],[[1,1],[1,1]],[[0,5],[5,0]],[[1,2,3],[4,5,6],[7,8,9]],[[9,8,7],[6,5,4],[3,2,1]],[[0,0,0],[0,1,0],[0,0,0]],[[5,1,5],[2,2,2],[5,1,5]],[[10,0],[0,10]],[[2,7,3],[6,1,5],[4,8,0]],[[100,1,1],[1,1,100],[1,1,1]],[[3,3,1],[2,3,2],[1,3,3]]]],SKYLINE,[SKYLINE.replace('min(rows[i],cols[j])','max(rows[i],cols[j])'),SKYLINE.replace('-value','+value')],['Raises cells to the larger skyline and changes a view.','Adds original heights instead of subtracting them from their caps.'],skyline_oracle,random_skyline,['A cell may rise only to the smaller of its row and column skyline limits.','Compute all row and column maxima first.','Sum min(rowMax,colMax)-current for every cell.','Each independent increase reaches the greatest value that preserves both directional skylines.'],'O(n^2)','O(n)',5),
817:entry('linked_list_component_count',[('head','ListNode | None'),('nums','list[int]')],'int',['linked lists','sets'],['The list contains unique integers and nums is a subset of its values.','A component is a maximal consecutive run of nodes whose values belong to nums.','Return the number of components.'],[([[0,1,2,3],[0,1,3]],'Nodes zero-one form one component and node three forms another.'),([[0,1,2,3,4],[0,3,1,4]],'Membership runs zero-one and three-four produce two components.')],[[h,n] for h,n in [([0],[0]),([0,1],[0]),([0,1],[1]),([0,1,2,3],[0,1,3]),([0,1,2,3,4],[0,3,1,4]),([1,2,3],[1,2,3]),([1,2,3],[2]),([3,1,4,2],[3,4]),([5,6,7,8],[5,7]),([0,2,4,6],[0,2]),([9,8,7],[9,7]),([1,3,5,7,9],[3,5,9]),([10,20,30,40],[20,30]),([4,2,8,6],[4,8,6])]],COMPONENTS,[COMPONENTS.replace('if not inside:answer+=1','answer+=1'),COMPONENTS.replace('else:inside=False','else:pass')],['Counts every selected node rather than maximal runs.','Never ends a component when an unselected node appears.'],components_oracle,random_components,['Track whether the previous node was inside the selected set.','A new component begins exactly at a selected node following the list start or an unselected node.','Scan once with set membership and an inside flag.','Every maximal selected run has exactly one such first node.'],'O(list length + len(nums))','O(len(nums))',5),
934:entry('shortest_island_bridge',[('grid','list[list[int]]')],'int',['matrices','recursion','breadth-first search'],['grid is square and contains exactly two four-connected islands.','Changing one water cell to land costs one.','Return the minimum changes needed to connect the islands.'],[([[[0,1],[1,0]]],'Either single separating water cell connects the diagonal islands.'),([[[0,1,0],[0,0,0],[0,0,1]]],'The closest land cells have Manhattan distance three, requiring two water changes.')],[[g] for g in [[[0,1],[1,0]],[[0,1,0],[0,0,0],[0,0,1]],[[1,0,0],[0,0,0],[0,0,1]],[[1,1,0],[0,0,0],[0,1,1]],[[1,0,1],[0,0,0],[0,0,0]],[[1,1],[0,1]],[[1,0],[0,1]],[[0,0,1],[0,0,0],[1,0,0]],[[1,1,0,0],[0,0,0,0],[0,0,1,1],[0,0,1,1]],[[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,1]],[[0,1,0,0],[0,1,0,1],[0,0,0,1],[0,0,0,0]],[[1,1,1],[0,0,0],[0,1,0]],[[1,0,0],[1,0,1],[0,0,1]],[[0,0,0,1],[0,0,0,0],[1,0,0,0],[1,1,0,0]]]],BRIDGE,[BRIDGE.replace('return distance','return distance+1'),BRIDGE.replace('queue.append((x,y,distance+1))','queue.append((x,y,distance))')],['Counts the reached island cell as an additional water conversion.','Does not increase distance while crossing water.'],bridge_oracle,random_bridge,['Mark every cell of one island first.','Run a multi-source BFS outward through water from that entire island.','The first cell of the other island is reached after the minimum number of water layers.','BFS layers represent exactly the number of converted water cells on the shortest bridge.'],'O(n^2)','O(n^2)',5),
950:entry('deck_order_for_increasing_reveal',[('deck','list[int]')],'list[int]',['arrays','queues'],['deck contains distinct integers.','Repeatedly reveal the top card, then move the next top card to the bottom when present.','Return an initial ordering whose reveal sequence is increasing.'],[([[17,13,11,2,3,5,7]],'The ordering 2,13,3,11,5,17,7 reveals values 2,3,5,7,11,13,17.'),([[1,1000]],'Ordering one,1000 already reveals increasing values.')],[[x] for x in [[1],[1,2],[1,1000],[17,13,11,2,3,5,7],[3,1,2],[4,1,3,2],[10,20,30,40],[9,8,7,6,5],[2,100,3,99],[5,1,9,2,8,3],[42,7],[6,4,2,8],[11,3,17,5,19,7],[100,50,25,75]]],DECK,[DECK.replace('queue.appendleft(queue.pop())','queue.append(queue.popleft())'),DECK.replace('reverse=True','reverse=False')],['Rotates the reverse-construction queue in the wrong direction.','Places smaller cards last during reverse construction.'],deck_oracle,random_deck,['Reverse the reveal process while consuming cards from greatest to smallest.','Before placing each earlier revealed card, undo the move-to-bottom by rotating the current bottom to the top.','Then place the next value at the top.','Each reverse step exactly inverts the forward reveal operation, yielding the unique required arrangement.'],'O(n log n)','O(n)',5),
958:entry('is_complete_binary_tree',[('root','TreeNode')],'bool',['trees','breadth-first search'],['root is nonempty.','A complete tree fills all levels before the last, and last-level nodes occupy leftmost positions.','Return whether the tree is complete.'],[([[1,2,3,4,5,6]],'All earlier levels are full and last-level nodes occupy the leftmost slots.'),([[1,2,3,4,5,None,7]],'Node seven appears after a missing breadth-first position, so the tree is incomplete.')],[[t] for t in [[1],[1,2],[1,None,2],[1,2,3],[1,2,3,4,5,6],[1,2,3,4,5,None,7],[1,2,3,4],[1,2,3,None,5],[1,2,None,3],[1,2,3,4,5,6,7],[1,2,3,4,None,6],[1,2,3,None,None,6],[1,2,3,4,5],[1,None,2,None,None,3]]],COMPLETE,[COMPLETE.replace('if gap:return False','if False:return False'),COMPLETE.replace('queue.extend((node.left,node.right))','queue.extend((node.right,node.left))')],['Ignores nonnull nodes that appear after a missing position.','Enqueues right children first and applies the completeness order backward.'],complete_oracle,random_complete,['In breadth-first order, every real node must appear before every missing child position.','Once a None is dequeued, remember that a gap has begun.','Reject any later real node; otherwise enqueue left then right children.','This exactly encodes the left-packed final-level definition.'],'O(n)','O(n)',5),
}
BATCH[817]['params'][0]=('head','ListNode | None','listnode')
BATCH[958]['params'][0]=('root','TreeNode','treenode')
BATCH[934]['boundaries']=[args for args in BATCH[934]['boundaries'] if args != [[[1,1],[0,1]]]]
BATCH[934]['boundaries'].append([[[1,1,0],[0,0,0],[0,0,1]]])
