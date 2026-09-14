"""Third reviewed group of workbook batch 119."""
from collections import deque
from itertools import combinations, permutations
from .import_batch_055 import entry

def isolated_o(a):
 grid=a[0];ones=[(r,c) for r,row in enumerate(grid) for c,v in enumerate(row) if v]
 edges=[(x,y) for i,x in enumerate(ones) for y in ones[i+1:] if abs(x[0]-y[0])+abs(x[1]-y[1])==1]
 for size in range(len(ones)+1):
  for removed in combinations(ones,size):
   chosen=set(removed)
   if all(x in chosen or y in chosen for x,y in edges):return size
def beams_o(a):
 counts=[row.count('1') for row in a[0] if '1' in row];return sum(x*y for x,y in zip(counts,counts[1:]))
def asteroids_o(a):
 mass,values=a
 for x in sorted(values):
  if mass<x:return False
  mass+=x
 return True
def invitations_o(a):
 favorite=a[0];n=len(favorite)
 for size in range(n,1,-1):
  for chosen in combinations(range(n),size):
   first=chosen[0]
   for rest in permutations(chosen[1:]):
    order=(first,)+rest
    if all(favorite[person] in (order[(i-1)%size],order[(i+1)%size]) for i,person in enumerate(order)):return size
 return 1
def flips_o(a):
 grid=a[0];first=grid[0]
 return all(row==first or all(x!=y for x,y in zip(row,first)) for row in grid)
def risolated(r):
 rows,cols=r.randint(1,3),r.randint(1,3);return [[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)]]
def rbeams(r):
 rows,cols=r.randint(1,10),r.randint(1,10);return [[''.join(r.choice('01') for _ in range(cols)) for _ in range(rows)]]
def rasteroids(r):return [r.randint(1,30),[r.randint(1,40) for _ in range(r.randint(1,12))]]
def rinvitations(r):
 n=r.randint(2,7);return [[r.choice([j for j in range(n) if j!=i]) for i in range(n)]]
def rflips(r):
 rows,cols=r.randint(1,6),r.randint(1,6);return [[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)]]

ISOLATED='''\
def minimum_isolation_flips(grid):
    rows,cols=len(grid),len(grid[0]);graph={}
    for row in range(rows):
        for col in range(cols):
            if grid[row][col] and (row+col)%2:
                node=row*cols+col;graph[node]=[]
                for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr,nc=row+dr,col+dc
                    if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]:graph[node].append(nr*cols+nc)
    match={}
    def augment(node,seen):
        for neighbor in graph[node]:
            if neighbor in seen:continue
            seen.add(neighbor)
            if neighbor not in match or augment(match[neighbor],seen):match[neighbor]=node;return True
        return False
    return sum(augment(node,set()) for node in graph)
'''
BEAMS='''\
def bank_laser_beams(bank):
    answer=previous=0
    for row in bank:
        devices=row.count('1')
        if devices:answer+=previous*devices;previous=devices
    return answer
'''
ASTEROIDS='''\
def can_destroy_asteroids(mass,asteroids):
    for asteroid in sorted(asteroids):
        if asteroid>mass:return False
        mass+=asteroid
    return True
'''
INVITATIONS='''\
def maximum_meeting_invitations(favorite):
    from collections import deque
    n=len(favorite);indegree=[0]*n;depth=[1]*n
    for person in favorite:indegree[person]+=1
    queue=deque(i for i,d in enumerate(indegree) if d==0)
    while queue:
        node=queue.popleft();target=favorite[node];depth[target]=max(depth[target],depth[node]+1);indegree[target]-=1
        if indegree[target]==0:queue.append(target)
    pairs=0;longest=0
    for i in range(n):
        if indegree[i]==0:continue
        length=0;node=i
        while indegree[node]:
            indegree[node]=0;length+=1;node=favorite[node]
        if length==2:pairs+=depth[i]+depth[favorite[i]]
        else:longest=max(longest,length)
    return max(longest,pairs)
'''
FLIPS='''\
def can_remove_ones_by_flips(grid):
    first=grid[0]
    for row in grid[1:]:
        same=all(a==b for a,b in zip(row,first));opposite=all(a!=b for a,b in zip(row,first))
        if not (same or opposite):return False
    return True
'''
def L(*x):return list(x)
BATCH={
2123:entry('minimum_isolation_flips',[('grid','list[list[int]]')],'int',['matrices','graphs','bipartite matching'],['grid is a nonempty binary matrix.','One operation changes one 1 to 0; afterward no horizontal or vertical neighboring pair may both be one.','Return the minimum operations.'],[([[[1,1,0],[0,1,1],[1,1,1]]],'Removing a minimum vertex cover of three occupied cells breaks every adjacent pair.'),([[[1,0,1],[0,1,0],[1,0,1]]],'The ones are already isolated, so zero operations are needed.')],[[g] for g in [[[0]],[[1]],[[1,1]],[[1],[1]],[[1,0],[0,1]],[[1,1],[1,1]],[[1,1,1]],[[1],[1],[1]],[[1,0,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]],[[1,1,0],[0,1,1]],[[0,0],[0,0]],[[1,0,1],[0,0,0],[1,0,1]],[[1,1,1],[1,1,1]]]],ISOLATED,[ISOLATED.replace('(row+col)%2','(row+col)%2==0'),ISOLATED.replace('return sum(augment(node,set()) for node in graph)','return len(graph)')],['Builds both sides from the even partition but searches edges from the wrong endpoint set.','Counts all occupied partition nodes instead of a minimum vertex cover.'],isolated_o,risolated,L('Occupied cells with adjacency edges form a bipartite graph by checkerboard parity.','By Konig’s theorem, minimum removed vertices equals maximum matching.','Build edges from one parity to occupied neighbors and count successful augmenting paths.','Removing a vertex cover breaks every adjacent-one edge, and bipartite maximum matching has the same minimum size.'),'O((rows*cols)^2)','O(rows*cols)',8),
2125:entry('bank_laser_beams',[('bank','list[str]')],'int',['matrices','strings','counting'],['Each row is a binary string of equal length.','Devices in consecutive nonempty rows each form one beam per cross-row pair; empty rows are ignored between them.','Return the total number of beams.'],[([['011001','000000','010100','001000']],'Device counts two, two, and one on nonempty rows contribute 2*2+2*1=6? The exact grid yields eight beams.'),([['000','111','000']],'Only one nonempty row exists, so no cross-row beam is formed.')],[[b] for b in [['0'],['1'],['1','1'],['10','01'],['11','11'],['1','0','1'],['101','000','010'],['000','000'],['111','000','111'],['100','010','001'],['11','00','01','10'],['1010','0101'],['1','0','0','1'],['001','011','111']]],BEAMS,[BEAMS.replace('previous*devices','previous+devices'),BEAMS.replace('if devices:','if devices>=0:')],['Adds device counts instead of multiplying cross-row pairs.','Treats empty rows as separators that reset the previous device count.'],beams_o,rbeams,L('Only device counts in consecutive nonempty rows matter; empty rows create no endpoint and do not block beams.','Track the previous nonzero row count and multiply it by the next nonzero count.','For each devices>0, add previous*devices then set previous=devices.','Every valid beam is one unique pair between two consecutive nonempty rows, so the products count each exactly once.'),'O(total cells)','O(1)',5),
2126:entry('can_destroy_asteroids',[('mass','int'),('asteroids','list[int]')],'bool',['arrays','greedy','sorting'],['Planet and asteroid masses are positive.','The planet destroys an asteroid when its current mass is at least that asteroid mass, then gains its mass.','Return whether some collision order destroys every asteroid.'],[([10,[3,9,19,5,21]],'Processing masses 3,5,9,19,21 lets the planet grow enough to destroy all.'),([5,[4,9,23,4]],'After both fours the planet reaches thirteen, destroys nine to reach twenty-two, but cannot destroy twenty-three.')],[[m,a] for m,a in [(1,[1]),(1,[2]),(5,[5]),(10,[20,1,2,3,4]),(3,[1,2,3]),(2,[3,1]),(100,[1,2,3]),(5,[6,7]),(4,[2,8]),(7,[7,14,28]),(10,[9,1,20]),(1,[1,1,1,4]),(6,[2,3,20]),(50,[100,25,25])]],ASTEROIDS,[ASTEROIDS.replace('sorted(asteroids)','sorted(asteroids,reverse=True)'),ASTEROIDS.replace('asteroid>mass','asteroid>=mass')],['Attempts the largest asteroid first and may fail despite a valid increasing order.','Rejects an asteroid whose mass exactly equals the planet mass.'],asteroids_o,rasteroids,L('If the smallest remaining asteroid cannot be destroyed, no larger one can; if it can, taking it only increases future capacity.','Sort asteroid masses ascending and greedily consume each affordable one.','For asteroid in sorted list, fail if asteroid>mass, otherwise mass+=asteroid.','The exchange argument permits moving the smallest remaining asteroid first in any successful order without harming later feasibility.'),'O(n log n)','O(n)',5),
2127:entry('maximum_meeting_invitations',[('favorite','list[int]')],'int',['graphs','topological sorting','cycles'],['Each employee favors exactly one different employee and must sit beside that person at a circular table.','Invite a subset and arrange it around one circle.','Return the maximum possible invited count.'],[([[2,2,1,2]],'Employees one and two form a mutual pair, and one incoming employee can sit on its outer side, totaling three.'),([[1,2,0]],'The three employees form a cycle and can all sit together.')],[[f] for f in [[1,0],[1,2,0],[1,0,1],[2,2,1,2],[1,0,3,2],[1,0,1,2],[2,0,1,2],[1,2,3,0],[1,2,3,4,0],[1,0,0,2,3],[1,0,3,2,2,4],[2,2,1],[3,0,1,2],[1,0,3,2,5,4]]],INVITATIONS,[INVITATIONS.replace('depth[target]=max(depth[target],depth[node]+1)','depth[target]=depth[node]+1'),INVITATIONS.replace('return max(longest,pairs)','return longest')],['Overwrites the longest incoming chain instead of retaining the maximum among branches.','Ignores mutual pairs and their attachable chains, considering only cycles longer than two.'],invitations_o,rinvitations,L('After pruning noncycle nodes, only directed cycles remain; incoming chains can attach only to the ends of mutual pairs.','Topologically remove trees while recording longest depth into each node.','Take the maximum of the longest cycle and the sum of both chain depths for every two-cycle.','Longer cycles fill both neighbor seats and cannot accept chains, while separate mutual-pair components and their best chains can be concatenated around one table.'),'O(n)','O(n)',8),
2128:entry('can_remove_ones_by_flips',[('grid','list[list[int]]')],'bool',['matrices','bit patterns'],['A move flips every bit in one whole row or one whole column.','Return whether some sequence of moves changes the entire binary matrix to zero.','The input matrix is nonempty and rectangular.'],[([[[0,1,0],[1,0,1],[0,1,0]]],'Every row equals the first row or its bitwise complement, so coordinated row and column flips can clear the grid.'),([[[1,1,0],[0,0,0]]],'The second row is neither equal to nor the complement of the first, so clearing is impossible.')],[[g] for g in [[[0]],[[1]],[[0,1]],[[0],[1]],[[0,0],[0,0]],[[1,1],[0,0]],[[0,1],[1,0]],[[0,1],[0,1]],[[0,1],[1,1]],[[1,0,1],[0,1,0]],[[1,0],[1,0],[0,1]],[[0,0,1],[1,1,0],[0,0,1]],[[1,1,1],[1,1,1]],[[0,1,0],[1,0,1],[1,0,1]]]],FLIPS,[FLIPS.replace('same or opposite','same and opposite'),FLIPS.replace('row in grid[1:]','row in grid[2:]')],['Requires a row to be both identical and complementary, rejecting valid multirow grids.','Skips checking the second row and can accept an incompatible pattern.'],flips_o,rflips,L('Column flips affect every row equally, so pairwise row XOR patterns never change.','Every row must initially equal the first row or its complement; then row flips can align them and column flips clear the common pattern.','Check all(a==b) or all(a!=b) against the first row for every later row.','The relation is necessary under shared column flips and sufficient by complementing opposite rows before clearing one columns pattern.'),'O(rows*cols)','O(1)',5)
}
BATCH[2123]['wrong'][0]=ISOLATED.replace("((1,0),(-1,0),(0,1),(0,-1))","((1,1),(-1,-1),(1,-1),(-1,1))")
BATCH[2123]['wrong_reasons'][0]='Treats diagonal occupied cells as adjacent instead of the required four directions.'
BATCH[2127]['wrong'][0]=INVITATIONS.replace('max(depth[target],depth[node]+1)','min(depth[target],depth[node]+1)')
BATCH[2127]['wrong_reasons'][0]='Keeps the shortest incoming branch instead of the longest chain attachable to a mutual pair.'
