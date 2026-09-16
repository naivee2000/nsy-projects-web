"""Parity DSU, grid increments, mirror counts, cube sums, and peak costs."""
from collections import Counter
from itertools import product
from .import_batch_055 import entry


def edge_oracle(args):
    n,edges=args;accepted=[]
    for edge in edges:
        trial=accepted+[edge]
        if any(all((bits[u]^bits[v])==weight for u,v,weight in trial) for bits in product((0,1),repeat=n)):accepted.append(edge)
    return len(accepted)
def random_edges(rng):
    n=rng.randint(1,7);edges=[]
    for _ in range(rng.randint(1,15)):
        u=rng.randrange(n);v=rng.randrange(n)
        while v==u and n>1:v=rng.randrange(n)
        edges.append([u,v,rng.randint(0,1)])
    return [n,edges]

def grid_oracle(args):
    grid,k=args;rows=len(grid);columns=len(grid[0]);positions=[(r,c) for r in range(rows-k+1) for c in range(columns-k+1)];best=None
    for counts in product(range(5),repeat=len(positions)):
        values=[row[:] for row in grid]
        for (r,c),count in zip(positions,counts):
            for i in range(r,r+k):
                for j in range(c,c+k):values[i][j]+=count
        if len({value for row in values for value in row})==1:
            total=sum(counts);best=total if best is None else min(best,total)
    return -1 if best is None else best
def random_grid(rng):
    rows=rng.randint(1,3);columns=rng.randint(1,3);k=min(rows,columns);return [[[rng.randint(0,3) for _ in range(columns)] for _ in range(rows)],k]

def mirror(character):return chr(219-ord(character)) if character.isalpha() else str(9-int(character))
def mirror_oracle(args):
    counts=Counter(args[0]);seen=set();answer=0
    for character in 'abcdefghijklmnopqrstuvwxyz0123456789':
        if character in seen:continue
        other=mirror(character);seen|={character,other};answer+=abs(counts[character]-counts[other])
    return answer
def random_mirror(rng):return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(rng.randint(1,80)))]

def cubes_oracle(args):
    limit=args[0];counts={};bound=int(limit**(1/3))+2
    for a in range(1,bound+1):
        for b in range(a,bound+1):
            value=a**3+b**3
            if value<=limit:counts[value]=counts.get(value,0)+1
    return sorted(value for value,count in counts.items() if count>=2)
def random_cubes(rng):return [rng.randint(1,100_000)]

def peak_oracle(args):
    nums=args[0];interior=range(1,len(nums)-1);best_count=-1;best_cost=10**30
    for mask in range(1<<max(0,len(nums)-2)):
        chosen=[i for i in interior if mask>>(i-1)&1]
        if any(chosen[i+1]-chosen[i]==1 for i in range(len(chosen)-1)):continue
        cost=sum(max(0,max(nums[i-1],nums[i+1])+1-nums[i]) for i in chosen)
        if len(chosen)>best_count or len(chosen)==best_count and cost<best_cost:best_count=len(chosen);best_cost=cost
    return best_cost
def random_peak(rng):return [[rng.randint(-20,20) for _ in range(rng.randint(1,15))]]

EDGES='''def count_even_cycle_edges(n,edges):
    parent=list(range(n));parity=[0]*n;size=[1]*n
    def find(node):
        if parent[node]!=node:
            original=parent[node];parent[node]=find(original);parity[node]^=parity[original]
        return parent[node]
    answer=0
    for u,v,weight in edges:
        root_u=find(u);root_v=find(v);relation=parity[u]^parity[v]
        if root_u==root_v:
            if relation==weight:answer+=1
            continue
        if size[root_u]<size[root_v]:root_u,root_v=root_v,root_u;u,v=v,u
        parent[root_v]=root_u;parity[root_v]=parity[u]^parity[v]^weight;size[root_u]+=size[root_v];answer+=1
    return answer
'''

GRID='''def minimum_square_increments(grid,k):
    rows=len(grid);columns=len(grid[0]);maximum=max(map(max,grid))
    coefficient=[[0]*(columns+2) for _ in range(rows+2)];constant=[[0]*(columns+2) for _ in range(rows+2)];forced=None
    for i in range(1,rows+1):
        for j in range(1,columns+1):
            coefficient[i][j]+=coefficient[i-1][j]+coefficient[i][j-1]-coefficient[i-1][j-1]
            constant[i][j]+=constant[i-1][j]+constant[i][j-1]-constant[i-1][j-1]
            current_coefficient=coefficient[i][j];current_constant=grid[i-1][j-1]+constant[i][j]
            if i+k-1<=rows and j+k-1<=columns:
                add_coefficient=1-current_coefficient;add_constant=-current_constant
                coefficient[i][j]+=add_coefficient;coefficient[i+k][j]-=add_coefficient;coefficient[i][j+k]-=add_coefficient;coefficient[i+k][j+k]+=add_coefficient
                constant[i][j]+=add_constant;constant[i+k][j]-=add_constant;constant[i][j+k]-=add_constant;constant[i+k][j+k]+=add_constant
            elif current_coefficient==1:
                if current_constant!=0:return -1
            else:
                numerator=-current_constant;denominator=current_coefficient-1
                if numerator%denominator:return -1
                candidate=numerator//denominator
                if forced is not None and forced!=candidate:return -1
                forced=candidate
    target=forced if forced is not None else maximum
    def check(target):
        diff=[[0]*(columns+2) for _ in range(rows+2)];operations=0
        for i in range(1,rows+1):
            for j in range(1,columns+1):
                diff[i][j]+=diff[i-1][j]+diff[i][j-1]-diff[i-1][j-1]
                current=grid[i-1][j-1]+diff[i][j]
                if current>target:return -1
                if current<target:
                    if i+k-1>rows or j+k-1>columns:return -1
                    amount=target-current;operations+=amount;diff[i][j]+=amount
                    diff[i+k][j]-=amount;diff[i][j+k]-=amount;diff[i+k][j+k]+=amount
        return operations
    return check(target) if target>=maximum else -1
'''

MIRROR='''def mirror_frequency_distance(s):
    from collections import Counter
    counts=Counter(s);seen=set();answer=0
    for character in counts:
        other=chr(219-ord(character)) if character.isalpha() else str(9-int(character))
        if character in seen:continue
        seen.add(character);seen.add(other);answer+=abs(counts[character]-counts[other])
    return answer
'''

CUBES='''def repeated_two_cube_sums(n):
    counts={};bound=int(n**(1/3))+2
    cubes=[value**3 for value in range(bound+1)]
    for a in range(1,bound+1):
        for b in range(a,bound+1):
            value=cubes[a]+cubes[b]
            if value>n:break
            counts[value]=counts.get(value,0)+1
    return sorted(value for value,count in counts.items() if count>1)
'''

PEAK='''def minimum_increase_for_max_peaks(nums):
    n=len(nums)
    if n<3:return 0
    cost=[0]*n
    for i in range(1,n-1):cost[i]=max(0,max(nums[i-1],nums[i+1])+1-nums[i])
    no_skip=[0]*(n+3);one_skip=[0]*(n+3)
    for i in range(n-2,0,-1):
        no_skip[i]=cost[i]+no_skip[i+2]
        one_skip[i]=min(cost[i]+one_skip[i+2],no_skip[i+1])
    return one_skip[1] if n%2==0 else no_skip[1]
'''

def lesson(a,b,c,d):return [a,b,c,d]
E_CASES=[[n,e] for n,e in ((3,[[0,1,1],[1,2,1],[0,2,1]]),(1,[[0,0,0]]),(2,[[0,1,0]]),(2,[[0,1,1],[0,1,1]]),(2,[[0,1,1],[0,1,0]]),(3,[[0,1,0],[1,2,0],[0,2,0]]),(3,[[0,1,1],[1,2,0],[0,2,1]]),(4,[[0,1,1],[2,3,1],[1,2,0]]),(4,[[0,1,1],[1,2,1],[2,3,1],[3,0,1]]),(3,[[0,1,0],[1,2,1],[2,0,1]]),(5,[[0,1,1],[1,2,0],[3,4,1],[2,3,1],[0,4,1]]),(3,[[0,1,1],[0,1,0],[1,2,1]]),(4,[[0,1,0],[1,2,0],[2,3,0],[0,3,1]]),(2,[[0,1,0],[0,1,0],[0,1,0]]),(5,[[0,1,1],[1,2,1],[2,0,0],[3,4,1]]))]
Q_CASES=[[g,k] for g,k in (([[3,3,5],[3,3,5]],2),([[1]],1),([[1,2]],1),([[1,1],[1,1]],2),([[0,1],[1,2]],1),([[1,0],[0,1]],2),([[2,2,3],[2,2,3]],2),([[0,0,1],[0,0,1],[1,1,2]],2),([[3,1],[3,1]],2),([[0,2,0]],1),([[1,2],[3,4]],1),([[5,5,5],[5,5,5]],2),([[0,1,0],[1,2,1],[0,1,0]],3),([[2,0,2],[2,0,2]],2),([[1,1,2],[1,1,2],[2,2,3]],2))]
M_CASES=[[s] for s in ('ab1z9','a','z','az','09','aaz','abcxyz','112889','hello123','abcdefghijklmnopqrstuvwxyz','0123456789','mnnm','a1z8','code404','zzzz')]
C_CASES=[[n] for n in (4104,1,8,1728,1729,1730,4099,5000,10000,20000,50000,100000,32832,40000,99999)]
P_CASES=[[[*v]] for v in ([1,2,2],[1],[1,2],[1,2,1],[2,1,2],[1,1,1],[1,3,1,3,1],[5,1,5,1,5,1],[1,2,3,4],[4,3,2,1],[0,0,0,0,0],[10,1,10,1,10,1],[1,5,2,4,1,3],[3,1,4,1,5],[2,9,2,8,2,7])]

BATCH={
3887:entry('count_even_cycle_edges',[('n','int'),('edges','list[list[int]]')],'int',['graphs','union find','parity'],['Nodes are 0 through n-1 and each edge weight is zero or one.','Process edges in order, accepting an edge only when every cycle in the accepted graph has even weight sum.','Return the number accepted.'],[([3,[[0,1,1],[1,2,1],[0,2,1]]],'The first two edges are accepted; the third creates weight sum three, so the answer is two.'),([2,[[0,1,1],[0,1,1]]],'The repeated edge forms a cycle of weight two, so both are accepted.')],E_CASES,EDGES,[EDGES.replace('relation==weight','relation!=weight'),EDGES.replace('parity[root_v]=parity[u]^parity[v]^weight','parity[root_v]=weight')],['Accepts precisely inconsistent cycle edges instead of consistent ones.','Stores the new edge weight without accounting for endpoint path parities.'],edge_oracle,random_edges,lesson('All cycles have even weight sum exactly when vertices admit binary potentials with p[u] xor p[v]=edge weight.','Maintain those relative potentials in a parity union-find.','An intra-component edge is accepted only if its required parity matches; a merging edge sets the child-root parity consistently.','The potential equations imply even XOR around every cycle, and any odd cycle produces the detected contradiction.'),'O(q α(n))','O(n)',8),
3888:entry('minimum_square_increments',[('grid','list[list[int]]'),('k','int')],'int',['matrices','difference arrays','greedy'],['grid is nonempty and k does not exceed either dimension.','One operation increments every cell of a chosen k×k submatrix by one.','Return the minimum operations making all cells equal, or -1.'],[([[[3,3,5],[3,3,5]],2],'Increment the left 2×2 square twice so every value becomes five, using two operations.'),([[[1]],1],'The single cell is already uniform, so zero operations are needed.')],Q_CASES,GRID,[GRID.replace('target=forced if forced is not None else maximum','target=maximum'),GRID.replace('operations+=amount','operations+=1')],['Assumes the initial maximum is always the target instead of honoring the boundary-forced target.','Counts each selected square once rather than once per unit increment.'],grid_oracle,random_grid,lesson('Scan symbolically first because every forced increment is an affine function of the final target.','At cells where no new k×k square can start, equality yields a target equation; all such equations must agree.','Run a numeric 2D-difference scan at that forced target, greedily adding the exact deficit at each startable cell.','The symbolic boundary equations find the only feasible target (or show none); the numeric scan is forced at every cell and therefore minimal.'),'O(mn)','O(mn)',8),
3889:entry('mirror_frequency_distance',[('s','str')],'int',['strings','hash maps','counting'],['s contains lowercase letters and decimal digits.','Letter mirrors are a↔z, b↔y, and so on; digit mirrors are 0↔9, 1↔8, and so on.','For each mirror pair, add the absolute frequency difference exactly once.'],[(['ab1z9'],'Pair a/z differs by zero, b/y by one, 1/8 by one, and 0/9 by one, totaling three.'),(['az'],'a and z have equal frequency, so their pair contributes zero.')],M_CASES,MIRROR,[MIRROR.replace('seen.add(character);seen.add(other)','seen.add(character)'),MIRROR.replace('abs(counts[character]-counts[other])','(counts[character]-counts[other])**2')],['Marks only one side of a mirror pair and counts it again when the mirror appears.','Squares each frequency difference instead of taking its absolute value.'],mirror_oracle,random_mirror,lesson('Mirroring is an involution, so characters form disjoint pairs.','Count all characters, then visit each encountered pair only if neither side was handled.','Add the absolute difference and mark both characters seen.','Every pair is counted once, including a missing mirror through its zero default frequency.'),'O(n)','O(1)',5),
3890:entry('repeated_two_cube_sums',[('n','int')],'list[int]',['math','enumeration','counting'],['n is positive and at most 1,000,000,000.','Use positive integers a≤b and count distinct pairs satisfying x=a³+b³.','Return ascending x≤n that have at least two such pairs.'],[([4104],'1729 and 4104 each have two distinct positive cube-pair representations.'),([1729],'1729=1³+12³=9³+10³, so it is the first returned value.')],C_CASES,CUBES,[CUBES.replace('range(a,bound+1)','range(1,bound+1)'),CUBES.replace('count>1','count>2')],['Counts ordered pairs separately, falsely turning one representation into multiple ones.','Requires three representations instead of at least two.'],cubes_oracle,random_cubes,lesson('Both cube bases are bounded by the cube root of n.','Enumerate a≤b, stop each inner loop once the sum exceeds n, and count each sum.','Filter counts greater than one and sort the keys.','The ordering constraint makes every mathematical pair appear once, so the counts exactly measure distinct representations.'),'O(n^(2/3))','O(n^(2/3))',6),
3891:entry('minimum_increase_for_max_peaks',[('nums','list[int]')],'int',['arrays','dynamic programming','greedy'],['nums is a nonempty integer array.','Only interior indices may be peaks; an operation increases one element by one.','First maximize the number of peaks, then return the minimum operations needed to attain that maximum.'],[([[1,2,2]],'Only index one can be a peak; increasing it once makes 3>1 and 3>2.'),([[1,3,1]],'The middle is already a peak, so zero operations are needed.')],P_CASES,PEAK,[PEAK.replace('one_skip[1] if n%2==0 else no_skip[1]','no_skip[1]'),PEAK.replace('+1-nums[i]','-nums[i]')],['For even lengths, never considers the one necessary parity shift among maximum-size peak placements.','Allows equality with a neighbor instead of requiring a strictly greater peak.'],peak_oracle,random_peak,lesson('A maximum set of interior peaks uses alternating indices; even lengths allow one parity shift.','Compute the independent cost of raising each candidate above its two original neighbors.','A two-state suffix DP either follows the current parity or spends the one allowed skip before continuing.','Adjacent peaks are impossible, and maximum cardinality leaves at most one extra gap; the DP enumerates exactly those layouts and minimizes their additive costs.'),'O(n)','O(n)',6),
}
