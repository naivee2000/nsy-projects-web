"""Inverse coins, equalized tree paths, staged river transport, bit states, and alternating grids."""
from collections import Counter, deque
from heapq import heappop, heappush
from itertools import combinations

from .import_batch_055 import entry


def inverse_oracle(args):
    target = args[0]; n = len(target); matches = []
    for mask in range(1 << n):
        ways = [1] + [0] * n
        for coin in range(1, n + 1):
            if mask >> (coin - 1) & 1:
                for amount in range(coin, n + 1): ways[amount] += ways[amount - coin]
        if ways[1:] == target: matches.append([coin for coin in range(1, n + 1) if mask >> (coin - 1) & 1])
    return matches[0] if len(matches) == 1 else []


def random_inverse(rng):
    n = rng.randint(1, 10); coins = [coin for coin in range(1, n + 1) if rng.randrange(3) == 0]; ways = [1] + [0] * n
    for coin in coins:
        for amount in range(coin, n + 1): ways[amount] += ways[amount - coin]
    result = ways[1:]
    if rng.randrange(4) == 0: result[rng.randrange(n)] += rng.choice((1, 2))
    return [result]


def increment_oracle(args):
    n, edges, cost = args; graph = [[] for _ in range(n)]
    for u, v in edges: graph[u].append(v); graph[v].append(u)
    parent = [-1] * n; parent[0] = 0; children = [[] for _ in range(n)]; order = [0]
    for node in order:
        for nxt in graph[node]:
            if parent[nxt] < 0: parent[nxt] = node; children[node].append(nxt); order.append(nxt)
    leaves = [node for node in range(n) if not children[node]]; paths = []
    for leaf in leaves:
        path = []; node = leaf
        while True:
            path.append(node)
            if node == 0: break
            node = parent[node]
        paths.append(set(path))
    sums = [sum(cost[node] for node in path) for path in paths]; target = max(sums); deficits = [target - value for value in sums]
    limits = [min((deficits[i] for i, path in enumerate(paths) if node in path), default=0) for node in range(n)]; best = n
    added = [0] * len(paths)
    def search(node, used):
        nonlocal best
        if used >= best: return
        if node == n:
            if added == deficits: best = used
            return
        affected = [i for i, path in enumerate(paths) if node in path]
        for delta in range(limits[node] + 1):
            if any(added[i] + delta > deficits[i] for i in affected): break
            for i in affected: added[i] += delta
            search(node + 1, used + (delta > 0))
            for i in affected: added[i] -= delta
    search(0, 0)
    return best


def random_increment(rng):
    n = rng.randint(2, 5); edges = [[rng.randrange(node), node] for node in range(1, n)]; rng.shuffle(edges)
    return [n, edges, [rng.randint(1, 4) for _ in range(n)]]


def _groups(mask, n, k):
    remaining = ((1 << n) - 1) ^ mask; subset = remaining
    while subset:
        if subset.bit_count() <= k: yield subset
        subset = (subset - 1) & remaining


def transport_oracle(args):
    n, k, m, times, multipliers = args; full = (1 << n) - 1; distance = {(0, 0): 0.0}; queue = deque([(0, 0)]); in_queue = {(0, 0)}
    while queue:
        mask, stage = queue.popleft(); in_queue.discard((mask, stage)); current = distance[mask, stage]
        for group in _groups(mask, n, k):
            crossing = max(times[i] for i in range(n) if group >> i & 1) * multipliers[stage]
            next_stage = (stage + int(crossing) % m) % m; across = mask | group
            transitions = [(across, next_stage, crossing)] if across == full else []
            if across != full:
                for person in range(n):
                    if across >> person & 1:
                        returning = times[person] * multipliers[next_stage]
                        transitions.append((across ^ (1 << person), (next_stage + int(returning) % m) % m, crossing + returning))
            for following_mask, following_stage, extra in transitions:
                state = (following_mask, following_stage); candidate = current + extra
                if candidate + 1e-12 < distance.get(state, float('inf')):
                    distance[state] = candidate
                    if state not in in_queue: in_queue.add(state); queue.append(state)
    answer = min((value for (mask, _), value in distance.items() if mask == full), default=float('inf'))
    return -1.0 if answer == float('inf') else answer


def random_transport(rng):
    n = rng.randint(1, 6); m = rng.randint(1, 4)
    return [n, rng.randint(1, min(4, n)), m, [rng.randint(1, 12) for _ in range(n)], [rng.choice((0.5, 0.75, 1.0, 1.25, 1.5, 2.0)) for _ in range(m)]]


def once_twice_oracle(args):
    counts = Counter(args[0]); once = next(value for value, count in counts.items() if count == 1); twice = next(value for value, count in counts.items() if count == 2)
    return [once, twice]


def random_once_twice(rng):
    values = rng.sample(range(-100, 101), rng.randint(2, 7)); once, twice = values[:2]; nums = [once, twice, twice]
    for value in values[2:]: nums.extend([value] * 3)
    rng.shuffle(nums); return [nums]


def alternating_oracle(args):
    m, n = args; distance = {(0, 0, 1): 1}; queue = deque([(0, 0, 1)])
    while queue:
        row, column, odd = queue.popleft(); current = distance[row, column, odd]
        moves = ((0, 1), (1, 0)) if odd else ((0, -1), (-1, 0))
        for dr, dc in moves:
            nr, nc = row + dr, column + dc
            if 0 <= nr < m and 0 <= nc < n:
                state = (nr, nc, 1 - odd); candidate = current + (nr + 1) * (nc + 1)
                if candidate < distance.get(state, 10**30): distance[state] = candidate; queue.append(state)
    return min((value for (row, column, _), value in distance.items() if (row, column) == (m - 1, n - 1)), default=-1)


def random_alternating(rng): return [rng.randint(1, 10), rng.randint(1, 10)]


INVERSE = '''def recover_coin_denominations(numWays):
    n=len(numWays);ways=[1]+[0]*n;coins=[]
    for amount in range(1,n+1):
        if ways[amount]==numWays[amount-1]:continue
        if ways[amount]+1!=numWays[amount-1]:return []
        coins.append(amount)
        for total in range(amount,n+1):ways[total]+=ways[total-amount]
    return coins if ways[1:]==numWays else []
'''


INCREMENTS = '''def minimum_nodes_to_equalize_paths(n,edges,cost):
    graph=[[] for _ in range(n)]
    for u,v in edges:graph[u].append(v);graph[v].append(u)
    parent=[-1]*n;parent[0]=0;children=[[] for _ in range(n)];order=[0]
    for node in order:
        for nxt in graph[node]:
            if parent[nxt]<0:parent[nxt]=node;children[node].append(nxt);order.append(nxt)
    score=[0]*n;answer=0
    for node in reversed(order):
        if not children[node]:score[node]=cost[node];continue
        target=max(score[child] for child in children[node])
        answer+=sum(score[child]<target for child in children[node]);score[node]=cost[node]+target
    return answer
'''


TRANSPORT = '''def minimum_transport_time(n,k,m,time,mul):
    import heapq
    full=(1<<n)-1;group_time=[0.0]*(1<<n)
    for mask in range(1,1<<n):
        bit=mask&-mask;person=bit.bit_length()-1;group_time[mask]=max(group_time[mask^bit],time[person])
    distance={(0,0):0.0};heap=[(0.0,0,0)]
    while heap:
        current,mask,stage=heapq.heappop(heap)
        if current!=distance.get((mask,stage)):continue
        if mask==full:return current
        remaining=full^mask;group=remaining
        while group:
            if group.bit_count()<=k:
                crossing=group_time[group]*mul[stage];next_stage=(stage+int(crossing)%m)%m;across=mask|group
                if across==full:
                    state=(across,next_stage);candidate=current+crossing
                    if candidate<distance.get(state,float('inf')):distance[state]=candidate;heapq.heappush(heap,(candidate,*state))
                else:
                    people=across
                    while people:
                        bit=people&-people;person=bit.bit_length()-1;returning=time[person]*mul[next_stage]
                        state=(across^bit,(next_stage+int(returning)%m)%m);candidate=current+crossing+returning
                        if candidate<distance.get(state,float('inf')):distance[state]=candidate;heapq.heappush(heap,(candidate,*state))
                        people^=bit
            group=(group-1)&remaining
    return -1.0
'''


ONCE_TWICE = '''def find_once_and_twice(nums):
    mask32=(1<<32)-1;ones=twos=0
    for value in nums:
        value&=mask32;twos|=ones&value;ones^=value;common=ones&twos;ones&=~common&mask32;twos&=~common&mask32
    distinguishing=(ones|twos)&-(ones|twos);group=[[0,0],[0,0]]
    for value in nums:
        value&=mask32;index=1 if value&distinguishing else 0;one,two=group[index];two|=one&value;one^=value;common=one&two;group[index]=[one&~common&mask32,two&~common&mask32]
    if ones&distinguishing:once,twice=group[1][0],group[0][1]
    else:once,twice=group[0][0],group[1][1]
    def signed(value):return value-(1<<32) if value>>31 else value
    return [signed(once),signed(twice)]
'''


ALTERNATING = '''def minimum_alternating_direction_grid_cost(m,n):
    if m==1 and n==1:return 1
    if (m,n) in ((1,2),(2,1)):return 3
    return -1
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]


INVERSE_CASES=[[[*ways]] for ways in [[0],[1],[0,1],[1,1],[1,2,2,3,4],[1,2,3,4,15],[0,1,0,2,0,3,0,4,0,5],[0,0,1,0,0,2],[1,1,1,1],[0,1,1,1],[1,2,2,3,3,4],[0,0,0,1,0,0,0,2],[1,2,3],[0,1,0,1,0,2]]]
INCREMENT_CASES=[[n,edges,cost] for n,edges,cost in [(2,[[0,1]],[1,2]),(3,[[0,1],[0,2]],[2,1,3]),(3,[[0,1],[1,2]],[5,1,4]),(5,[[0,4],[0,1],[1,2],[1,3]],[3,4,1,1,7]),(4,[[0,1],[0,2],[0,3]],[1,1,2,3]),(4,[[0,1],[1,2],[1,3]],[2,3,1,4]),(5,[[0,1],[0,2],[1,3],[1,4]],[1,2,3,4,5]),(5,[[0,1],[1,2],[2,3],[3,4]],[1,2,3,4,5]),(6,[[0,1],[0,2],[1,3],[1,4],[2,5]],[2,1,3,2,4,1]),(6,[[0,1],[1,2],[1,3],[0,4],[4,5]],[1,2,1,3,2,4]),(4,[[0,1],[0,2],[2,3]],[3,1,2,1]),(5,[[0,1],[0,2],[2,3],[2,4]],[2,5,1,2,3]),(6,[[0,1],[0,2],[0,3],[3,4],[3,5]],[1,2,3,4,1,2]),(5,[[0,1],[1,2],[1,3],[3,4]],[4,1,2,3,1])]]
TRANSPORT_CASES=[[n,k,m,times,mul] for n,k,m,times,mul in [(1,1,1,[5],[1.0]),(1,1,2,[5],[1.0,1.3]),(2,1,2,[10,10],[2.0,2.0]),(2,2,1,[3,7],[1.0]),(3,2,3,[2,5,8],[1.0,1.5,0.75]),(3,3,2,[2,4,6],[1.0,2.0]),(3,2,1,[1,2,5],[1.0]),(4,2,2,[1,2,5,10],[1.0,0.5]),(4,3,3,[2,3,7,9],[1.25,0.75,1.0]),(2,1,1,[1,2],[1.0]),(5,3,2,[1,4,6,8,10],[1.5,0.5]),(4,2,4,[3,5,7,11],[0.5,1.0,1.5,2.0]),(3,2,2,[10,1,10],[2.0,0.5]),(6,4,3,[1,2,3,5,8,13],[1.0,0.75,1.25])]]
ONCE_CASES=[[[*nums]] for nums in [[1,2,2],[2,2,3],[2,2,3,2,5,5,5,7,7],[0,1,1,2,2,2],[-1,4,4,3,3,3],[-5,-5,7,8,8,8],[-2,-2,-2,-3,4,4],[10,10,11,12,12,12],[-10,5,5,6,6,6],[1,1,2,2,2,3,3,3,4],[99,-1,-1,7,7,7],[0,0,-4,5,5,5],[-8,-8,-9,-10,-10,-10],[42,17,17,9,9,9]]]
ALTERNATING_CASES=[[m,n] for m,n in [(1,1),(1,2),(2,1),(2,2),(1,3),(3,1),(2,3),(3,2),(3,3),(4,1),(1,4),(4,4),(5,2),(2,5)]]


BATCH={
3592:entry('recover_coin_denominations',[('numWays','list[int]')],'list[int]',['dynamic programming','coin change','reconstruction'],['numWays has length at most 100 and gives unordered infinite-coin combination counts for amounts one through n.','Denominations are unique positive integers at most n.','Return the unique sorted denomination set, or an empty list when the counts are inconsistent.'],[([[0,1,0,2,0,3,0,4,0,5]],'The counts force denominations two, four, and six.'),([[1,2,3,4,15]],'The final count cannot be produced by any denomination set, so the result is empty.')],INVERSE_CASES,INVERSE,[INVERSE.replace('ways[amount]+1','ways[amount]'),INVERSE.replace('range(amount,n+1)','range(amount+1,n+1)')],['Requires a new denomination to add zero ways at its own amount instead of exactly one.','Fails to update the number of ways for the denomination amount itself.'],inverse_oracle,random_inverse,lesson('At amount d, larger coins cannot contribute and adding coin d creates exactly one new combination: the coin alone.','Reconstruct denominations from small to large while maintaining the forward coin-change DP produced so far.','If current ways equals target, skip d; if it is exactly one smaller, add d and update ascending totals; otherwise reject.','Induction fixes every denomination uniquely because all smaller choices are already known and no larger denomination affects the current amount.'),'O(n^2)','O(n)',5),
3593:entry('minimum_nodes_to_equalize_paths',[('n','int'),('edges','list[list[int]]'),('cost','list[int]')],'int',['trees','dynamic programming','greedy'],['The positive-cost tree has up to 100,000 nodes and is rooted at zero.','Increase chosen node costs by arbitrary nonnegative amounts.','Minimize how many nodes are increased so every root-to-leaf path has equal total cost.'],[([3,[[0,1],[0,2]],[2,1,3]],'Raise node one by two so both root-to-leaf scores become five; one node changes.'),([3,[[0,1],[1,2]],[5,1,4]],'There is only one root-to-leaf path, so no increment is needed.')],INCREMENT_CASES,INCREMENTS,[INCREMENTS.replace('score[child]<target','score[child]<=target'),INCREMENTS.replace('target=max','target=min')],['Counts every child branch including those already at the target score.','Balances children down to the minimum path score, which cannot be achieved using increments only.'],increment_oracle,random_increment,lesson('At a node, every lower child-subtree maximum must be raised to the largest child maximum, and one increment at that child root raises all its leaf paths together.','Process bottom-up, returning the common node-to-leaf score and counting each deficient child branch once.','Set target=max(child scores), add the number below target, and return cost[node]+target.','Increasing the deficient child root is sufficient with one changed node, while any solution must change at least one node inside each independently deficient branch.'),'O(n)','O(n)',5),
3594:entry('minimum_transport_time',[('n','int'),('k','int'),('m','int'),('time','list[int]'),('mul','list[float]')],'float',['graphs','bitmasking','shortest paths'],['There are at most 12 people, boat capacity at most five, and at most five cyclic environment stages.','A crossing group moves at its slowest member time times the current multiplier; stages advance by the floored duration modulo m.','Unless everyone has crossed, one person on the destination side must return with the boat.'],[([1,1,2,[5],[1.0,1.3]],'The lone person crosses at stage zero in five minutes.'),([3,2,3,[2,5,8],[1.0,1.5,0.75]],'The optimal send-return-send sequence takes 8 + 1.5 + 5 = 14.5 minutes.')],TRANSPORT_CASES,TRANSPORT,[TRANSPORT.replace('int(crossing)%m','round(crossing)%m'),TRANSPORT.replace("(next_stage+int(returning)%m)%m","next_stage")],['Rounds crossing durations when advancing the stage instead of taking the floor.','Forgets that a return trip also advances the environmental stage.'],transport_oracle,random_transport,lesson('A reusable state is the set of people across and the current environmental stage, with the boat back at base unless complete.','Run Dijkstra; each edge sends a capacity-bounded subset and, when needed, chooses any person across to return.','Precompute group slowest times, update stages with floor(duration) mod m, and relax combined crossing-return transitions.','Every legal strategy decomposes into these send-return cycles plus a final send, and all durations are nonnegative, so Dijkstra finds the minimum total time.'),'O(m*3^n*n)','O(m*2^n)',8),
3595:entry('find_once_and_twice',[('nums','list[int]')],'list[int]',['bit manipulation','finite state machines','arrays'],['Exactly one signed 32-bit integer appears once, another appears twice, and every other value appears three times.','Return [once, twice].','Use linear time and constant auxiliary space.'],[([[2,2,3,2,5,5,5,7,7]],'Three appears once and seven appears twice.'),([[-1,4,4,3,3,3]],'Negative one appears once and four appears twice.')],ONCE_CASES,ONCE_TWICE,[ONCE_TWICE.replace('distinguishing=(ones|twos)&-(ones|twos)','distinguishing=ones&-ones'),ONCE_TWICE.replace('if ones&distinguishing','if twos&distinguishing')],['Chooses a distinguishing bit only from the once-only residue, failing when the values differ only in the twice-only residue.','Reverses which frequency group owns the distinguishing bit and swaps the recovered roles.'],once_twice_oracle,random_once_twice,lesson('Bit counts modulo three reveal bits exclusive to the once and twice values; any such bit separates the two exceptions into different groups.','Use two bit-state accumulators, split by one differing bit, then recover the modulo-three residue in each group according to its known frequency.','Compute global ones/twos states, choose a bit from their union, run the same states per bit group, and convert 32-bit results back to signed integers.','Triplicate values vanish modulo three in each group; the separating bit identifies which group contains the once-occurring versus twice-occurring exception.'),'O(n)','O(1)',5),
3596:entry('minimum_alternating_direction_grid_cost',[('m','int'),('n','int')],'int',['grids','state graphs','invariants'],['Start at (0,0), paying its entry cost one.','Odd-numbered moves may go right or down; even-numbered moves may go left or up.','Entering (i,j) costs (i+1)(j+1); return the minimum cost to the bottom-right or -1.'],[([1,1],'The start is already the destination and costs one.'),([1,2],'One right move reaches the destination, adding entry cost two for total three.')],ALTERNATING_CASES,ALTERNATING,[ALTERNATING.replace('((1,2),(2,1))','((1,2),)'),ALTERNATING.replace('return -1','return m*n')],['Forgets the symmetric one-column reachable case.','Returns a fabricated area cost for destinations that are unreachable under alternating directions.'],alternating_oracle,random_alternating,lesson('After one right or down move, the required left or up move can only undo progress toward the bottom-right from the origin boundary.','Therefore only the start and its two immediate right/down neighbors can ever be first reached at the correct move parity.','Return one for 1x1, three for 1x2 or 2x1, and -1 otherwise.','Every even move from a cell reached directly from the origin points back toward the origin; induction shows no state farther in either coordinate is reachable.'),'O(1)','O(1)',5),
}
BATCH[3594]['comparator']='float'
