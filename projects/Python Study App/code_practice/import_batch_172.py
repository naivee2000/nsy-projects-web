"""Subset power, circular passes, XOR cycles, grid moves, and cliques batch 172."""

from itertools import combinations

from .import_batch_055 import entry

MOD=1_000_000_007


def power_oracle(args):
    nums=args[0];answer=0
    for size in range(1,len(nums)+1):
        for subset in combinations(nums,size):answer=(answer+max(subset)**2*min(subset))%MOD
    return answer


def random_power(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,14))]]


def losers_oracle(args):
    n,k=args;received=set();current=0;turn=1
    while current not in received:
        received.add(current);current=(current+turn*k)%n;turn+=1
    return [friend for friend in range(1,n+1) if friend-1 not in received]


def random_losers(rng):return [rng.randint(1,50),rng.randint(1,50)]


def xor_oracle(args):
    derived=args[0];n=len(derived)
    for mask in range(1<<n):
        values=[mask>>index&1 for index in range(n)]
        if all(values[index]^values[(index+1)%n]==derived[index] for index in range(n)):return True
    return False


def random_xor(rng):return [[rng.randint(0,1) for _ in range(rng.randint(1,16))]]


def moves_oracle(args):
    grid=args[0];rows=len(grid);columns=len(grid[0])
    def visit(row,column):
        best=0
        if column+1<columns:
            for nr in range(max(0,row-1),min(rows,row+2)):
                if grid[nr][column+1]>grid[row][column]:best=max(best,1+visit(nr,column+1))
        return best
    return max(visit(row,0) for row in range(rows))


def random_moves(rng):
    rows,columns=rng.randint(1,6),rng.randint(1,7)
    return [[[rng.randint(1,30) for _ in range(columns)] for _ in range(rows)]]


def complete_oracle(args):
    n,edges=args;neighbors=[set() for _ in range(n)]
    for left,right in edges:neighbors[left].add(right);neighbors[right].add(left)
    seen=set();answer=0
    for start in range(n):
        if start in seen:continue
        component={start};stack=[start];seen.add(start)
        while stack:
            node=stack.pop()
            for neighbor in neighbors[node]:
                if neighbor not in seen:seen.add(neighbor);component.add(neighbor);stack.append(neighbor)
        answer+=all((component-{node})==neighbors[node] for node in component)
    return answer


def random_complete(rng):
    n=rng.randint(1,12);possible=list(combinations(range(n),2));rng.shuffle(possible)
    return [n,[list(edge) for edge in possible[:rng.randint(0,len(possible))]]]


POWER="""\
def sum_hero_subset_power(nums):
    mod=1000000007;prefix=answer=0
    for maximum in sorted(nums):
        answer=(answer+maximum*maximum%mod*(maximum+prefix))%mod
        prefix=(2*prefix+maximum)%mod
    return answer
"""

LOSERS="""\
def circular_game_losers(n,k):
    visited=set();position=0;turn=1
    while position not in visited:
        visited.add(position);position=(position+turn*k)%n;turn+=1
    return [friend for friend in range(1,n+1) if friend-1 not in visited]
"""

XOR="""\
def valid_neighbor_xor_array(derived):
    result=0
    for value in derived:result^=value
    return result==0
"""

MOVES="""\
def maximum_increasing_grid_moves(grid):
    rows=len(grid);columns=len(grid[0]);reachable=set(range(rows))
    for column in range(columns-1):
        following=set()
        for row in reachable:
            for nr in range(max(0,row-1),min(rows,row+2)):
                if grid[nr][column+1]>grid[row][column]:following.add(nr)
        if not following:return column
        reachable=following
    return columns-1
"""

COMPLETE="""\
def count_complete_graph_components(n,edges):
    graph=[set() for _ in range(n)]
    for left,right in edges:graph[left].add(right);graph[right].add(left)
    seen=set();answer=0
    for start in range(n):
        if start in seen:continue
        stack=[start];seen.add(start);nodes=[];degree_sum=0
        while stack:
            node=stack.pop();nodes.append(node);degree_sum+=len(graph[node])
            for neighbor in graph[node]:
                if neighbor not in seen:seen.add(neighbor);stack.append(neighbor)
        answer+=degree_sum==len(nodes)*(len(nodes)-1)
    return answer
"""


BATCH={
2681:entry('sum_hero_subset_power',[('nums','list[int]')],'int',['arrays','dynamic programming','sorting'],
 ['For every nonempty index subset, its power is maximum_strength squared times minimum_strength.','Sum the powers of all subsets, treating equal-valued heroes at different indices as distinct choices.','Return the sum modulo 1,000,000,007.'],
 [([[2,1,4]],'The seven nonempty subsets have powers summing to 141.'),([[1,1,1]],'Every one of the seven nonempty index subsets has power one.')],
 [[a] for a in [[1],[2],[1,2],[2,1],[1,1],[1,2,3],[2,1,4],[3,3,3],[1,5,2,5],[10,1],[2,4,8,16],[5,4,3,2,1],[100,100],[1,1,2,2]]],
 POWER,[POWER.replace('maximum+prefix','maximum-prefix'),POWER.replace('2*prefix+maximum','prefix+maximum')],
 ['Subtracts earlier possible minima instead of adding their subset contributions.','Fails to double prior minimum contributions when the new maximum may join every prior subset.'],power_oracle,random_power,
 ['Sort strengths and treat each value as the maximum of newly counted subsets.','The singleton contributes maximum cubed; earlier values summarize possible minimum contributions.','Add maximum² times (maximum+prefix), then update prefix as 2*prefix+maximum.','Every earlier subset either excludes or includes the new maximum; grouping by unique final maximum counts every nonempty index subset exactly once.'],'O(n log n)','O(n)',8),
2682:entry('circular_game_losers',[('n','int'),('k','int')],'list[int]',['arrays','simulation','hash maps'],
 ['Friends are numbered one through n, and friend one initially holds the ball.','On turn t starting at one, pass t*k positions clockwise; stop before a friend would receive the ball a second time.','Return never-receiving friend IDs in ascending order.'],
 [([5,2],'Friends one, three, and two receive the ball before repetition, leaving four and five.'),([4,4],'The first pass returns immediately to friend one, so friends two, three, and four lose.')],
 [[n,k] for n,k in [(1,1),(2,1),(2,2),(3,1),(3,2),(4,1),(4,4),(5,2),(5,3),(6,1),(6,4),(7,2),(8,3),(10,5)]],
 LOSERS,[LOSERS.replace('turn*k','k'),LOSERS.replace('friend-1 not in visited','friend not in visited')],
 ['Uses a constant k-step pass instead of increasing the multiplier each turn.','Compares one-based friend IDs directly with zero-based visited positions.'],losers_oracle,random_losers,
 ['Track visited zero-based positions in a set.','Start at position zero and mark it before computing the next pass.','Advance by turn*k modulo n and increment the turn until the next position is already visited.','The simulation follows every rule transition exactly; complementing visited positions and converting to one-based IDs yields precisely the sorted losers.'],'O(n)','O(n)',3),
2683:entry('valid_neighbor_xor_array',[('derived','list[int]')],'bool',['arrays','bit manipulation'],
 ['derived is binary and should satisfy derived[i]=original[i] XOR original[(i+1) mod n].','Determine whether at least one circular binary original array can produce it.','Return True when possible and False otherwise.'],
 [([[1,1,0]],'Original [0,1,0] produces the three derived bits, so the answer is true.'),([[1,1]],'Original [0,1] produces [1,1], so a valid array exists.')],
 [[a] for a in [[0],[1],[0,0],[0,1],[1,0],[1,1],[0,0,0],[1,1,0],[1,0,1],[1,1,1],[0,1,1,0],[1,0,0,1],[1,1,1,1],[0,1,0,1,0]]],
 XOR,[XOR.replace('result==0','result==1'),XOR.replace('result^=value','result|=value')],
 ['Requires odd XOR parity instead of even parity.','Uses bitwise OR, rejecting every nonzero but otherwise valid derived array.'],xor_oracle,random_xor,
 ['XOR all equations around the circular array.','Every original bit appears exactly twice and therefore cancels.','A valid derived array must have total XOR zero; conversely choose original[0] arbitrarily and propagate the remaining bits.','The propagated final edge agrees with the starting choice exactly when derived XOR is zero, proving necessity and sufficiency.'],'O(n)','O(1)',5),
2684:entry('maximum_increasing_grid_moves',[('grid','list[list[int]]')],'int',['matrices','dynamic programming'],
 ['Start at any cell in the first column.','A move goes to the next column and changes row by -1, 0, or 1, only to a strictly larger value.','Return the greatest possible number of moves.'],
 [([[[2,4,3,5],[5,4,9,3],[3,4,2,11],[10,9,13,15]]],'A valid strictly increasing route crosses all four columns, making three moves.'),([[[3,2,4],[2,1,9],[1,1,7]]],'No first-column value can move to a larger adjacent value in column one, so return zero.')],
 [[g] for g in [[[1]],[[1,2]],[[2,1]],[[1],[2]],[[1,2],[2,3]],[[3,2],[1,4]],[[1,1],[1,1]],[[1,2,3],[3,2,1]],[[5,1,9],[4,6,7],[3,8,2]],[[1,100,1,100]],[[10,9,8],[1,2,3]],[[2,4,3,5],[5,4,9,3],[3,4,2,11],[10,9,13,15]],[[1,3],[2,2],[3,4]],[[9,1,2],[8,10,3],[7,6,11]]]],
 MOVES,[MOVES.replace('grid[nr][column+1]>grid[row][column]','grid[nr][column+1]>=grid[row][column]'),MOVES.replace('range(max(0,row-1),min(rows,row+2))','range(row,row+1)')],
 ['Allows equal-valued moves despite the strict-increase rule.','Allows only same-row moves and ignores both diagonals.'],moves_oracle,random_moves,
 ['Represent all rows reachable in the current column as a set.','For each reachable row, test the three bounded neighbor rows in the next column.','If no next row is reachable, the current column index equals the number of completed moves; otherwise continue.','The reachable set is exactly the frontier after each move count, so the last nonempty frontier gives the longest possible path.'],'O(rows*columns)','O(rows)',5),
2685:entry('count_complete_graph_components',[('n','int'),('edges','list[list[int]]')],'int',['graphs','depth-first search'],
 ['The inputs describe a simple undirected graph on vertices zero through n-1.','A connected component is complete when every pair of its vertices has an edge between them.','Return the number of complete connected components, including isolated vertices.'],
 [([6,[[0,1],[0,2],[1,2],[3,4]]],'The triangle, the two-vertex edge, and isolated vertex five are three complete components.'),([6,[[0,1],[0,2],[1,2],[3,4],[3,5]]],'The triangle is complete but the three-node path is not, so only one component qualifies.')],
 [[n,e] for n,e in [(1,[]),(2,[]),(2,[[0,1]]),(3,[[0,1],[1,2]]),(3,[[0,1],[0,2],[1,2]]),(4,[[0,1],[2,3]]),(4,[[0,1],[1,2],[2,3],[3,0]]),(5,[[0,1],[0,2],[1,2]]),(6,[[0,1],[0,2],[1,2],[3,4]]),(4,[]),(5,[[0,1],[0,2],[0,3],[0,4]]),(6,[[0,1],[1,2],[2,0],[3,4],[4,5],[5,3]]),(5,[[0,1],[1,2],[2,0],[3,4]]),(7,[[0,1],[0,2],[1,2],[3,4],[3,5],[4,5]])]],
 COMPLETE,[COMPLETE.replace('len(nodes)*(len(nodes)-1)','len(nodes)*(len(nodes)+1)'),COMPLETE.replace('degree_sum+=len(graph[node])','degree_sum+=1')],
 ['Requires the impossible edge count for self-loops as well as all pairs.','Counts component vertices rather than the sum of their degrees.'],complete_oracle,random_complete,
 ['Traverse each unseen connected component.','Count its vertices and sum their graph degrees.','A size-s complete simple component has degree sum s*(s-1).','Connectivity is guaranteed by traversal, and a simple component reaches the maximum possible internal edge count exactly when every vertex pair is adjacent.'],'O(n+edges)','O(n+edges)',5),
}
