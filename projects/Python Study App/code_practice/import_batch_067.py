"""Reviewed backtracking, graph, string, probability, and window-DP imports."""
from fractions import Fraction
from itertools import combinations, permutations

from .import_batch_055 import entry


def game24_oracle(args):
    @staticmethod
    def unused(): pass
    def search(values):
        if len(values) == 1: return values[0] == 24
        for left in range(len(values)):
            for right in range(left + 1, len(values)):
                rest = [values[i] for i in range(len(values)) if i not in (left, right)]
                a, b = values[left], values[right]
                choices = {a + b, a - b, b - a, a * b}
                if b: choices.add(a / b)
                if a: choices.add(b / a)
                if any(search(rest + [value]) for value in choices): return True
        return False
    return search([Fraction(value) for value in args[0]])


def empty_slots_oracle(args):
    bulbs, empty = args
    active = set()
    for day, position in enumerate(bulbs, 1):
        active.add(position)
        if position - empty - 1 in active and not any(p in active for p in range(position - empty, position)):
            return day
        if position + empty + 1 in active and not any(p in active for p in range(position + 1, position + empty + 1)):
            return day
    return -1


def redundant_oracle(args):
    graph = {}
    for left, right in args[0]:
        stack, seen = [left], set()
        while stack:
            node = stack.pop()
            if node == right: return [left, right]
            if node in seen: continue
            seen.add(node); stack.extend(graph.get(node, ()))
        graph.setdefault(left, set()).add(right)
        graph.setdefault(right, set()).add(left)


def valid_rooted_tree(edges):
    nodes = {value for edge in edges for value in edge}
    indegree = {node: 0 for node in nodes}
    graph = {node: [] for node in nodes}
    for parent, child in edges:
        indegree[child] += 1
        graph[parent].append(child)
    roots = [node for node in nodes if indegree[node] == 0]
    if len(roots) != 1 or any(value > 1 for value in indegree.values()): return False
    seen, stack = set(), [roots[0]]
    while stack:
        node = stack.pop()
        if node in seen: return False
        seen.add(node); stack.extend(graph[node])
    return len(seen) == len(nodes)


def directed_redundant_oracle(args):
    edges = args[0]
    for index in range(len(edges) - 1, -1, -1):
        if valid_rooted_tree(edges[:index] + edges[index + 1:]): return edges[index]


def repeat_oracle(args):
    base, target = args
    text = ''
    for count in range(1, len(target) // len(base) + 3):
        text += base
        if target in text: return count
    return -1


def knight_oracle(args):
    size, moves, row, column = args
    states = {(row, column): 1}
    offsets = ((1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1))
    for _ in range(moves):
        following = {}
        for (r,c), count in states.items():
            for dr,dc in offsets:
                nr,nc=r+dr,c+dc
                if 0 <= nr < size and 0 <= nc < size:
                    following[(nr,nc)] = following.get((nr,nc),0) + count
        states = following
    return sum(states.values()) / (8 ** moves)


def three_windows_oracle(args):
    nums, k = args
    sums = [sum(nums[i:i+k]) for i in range(len(nums)-k+1)]
    best = None
    for a in range(len(sums)):
        for b in range(a+k,len(sums)):
            for c in range(b+k,len(sums)):
                candidate = (-(sums[a]+sums[b]+sums[c]), [a,b,c])
                if best is None or candidate < best: best = candidate
    return best[1]


def random_game(rng): return [[rng.randint(1,9) for _ in range(4)]]


def random_slots(rng):
    size=rng.randint(2,14); bulbs=list(range(1,size+1)); rng.shuffle(bulbs)
    return [bulbs,rng.randint(0,size-2)]


def random_redundant(rng):
    n=rng.randint(3,12)
    edges=[[rng.randint(1,node-1),node] for node in range(2,n+1)]
    existing={tuple(sorted(e)) for e in edges}
    choices=[(a,b) for a in range(1,n+1) for b in range(a+1,n+1) if (a,b) not in existing]
    edges.append(list(rng.choice(choices))); rng.shuffle(edges)
    return [edges]


def random_directed(rng):
    n=rng.randint(2,9)
    edges=[[rng.randint(1,node-1),node] for node in range(2,n+1)]
    existing={tuple(e) for e in edges}
    choices=[(a,b) for a in range(1,n+1) for b in range(1,n+1) if a!=b and (a,b) not in existing]
    edges.append(list(rng.choice(choices))); rng.shuffle(edges)
    return [edges]


def random_repeat(rng):
    a=''.join(rng.choice('abc') for _ in range(rng.randint(1,5)))
    b=''.join(rng.choice('abc') for _ in range(rng.randint(1,12)))
    return [a,b]


def random_knight(rng):
    n=rng.randint(1,7); return [n,rng.randint(0,5),rng.randrange(n),rng.randrange(n)]


def random_three_windows(rng):
    k=rng.randint(1,4); length=rng.randint(3*k, max(3*k,15))
    return [[rng.randint(0,20) for _ in range(length)],k]


GAME = '''\
def can_make_twenty_four(cards):
    def search(values):
        if len(values) == 1: return abs(values[0] - 24) < 1e-9
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                rest = [values[k] for k in range(len(values)) if k not in (i,j)]
                a,b=values[i],values[j]
                results=[a+b,a-b,b-a,a*b]
                if abs(b)>1e-12: results.append(a/b)
                if abs(a)>1e-12: results.append(b/a)
                if any(search(rest+[value]) for value in results): return True
        return False
    return search(list(map(float,cards)))
'''


SLOTS = '''\
def first_k_empty_slots(bulbs, k):
    days = [0] * len(bulbs)
    for day, position in enumerate(bulbs, 1): days[position - 1] = day
    answer = float('inf')
    left, right = 0, k + 1
    while right < len(days):
        limit = max(days[left], days[right])
        for index in range(left + 1, right):
            if days[index] < limit:
                left, right = index, index + k + 1
                break
        else:
            answer = min(answer, limit)
            left, right = right, right + k + 1
    return -1 if answer == float('inf') else answer
'''


REDUNDANT = '''\
def redundant_undirected_edge(edges):
    parent=list(range(len(edges)+1))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    for left,right in edges:
        a,b=find(left),find(right)
        if a==b:return [left,right]
        parent[a]=b
'''


DIRECTED = '''\
def redundant_directed_edge(edges):
    n=len(edges); parent_of=[0]*(n+1); first=second=None
    for edge in edges:
        parent,child=edge
        if parent_of[child]: first=[parent_of[child],child];second=edge
        else: parent_of[child]=parent
    parent=list(range(n+1))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    for edge in edges:
        if edge is second: continue
        left,right=edge;a,b=find(left),find(right)
        if a==b:return first if first else edge
        parent[b]=a
    return second
'''


REPEAT = '''\
def repeated_string_count(a, b):
    count=(len(b)+len(a)-1)//len(a)
    text=a*count
    if b in text:return count
    if b in text+a:return count+1
    return -1
'''


KNIGHT = '''\
def knight_stay_probability(n, k, row, column):
    states={(row,column):1.0}
    offsets=((1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1))
    for _ in range(k):
        following={}
        for (r,c),probability in states.items():
            for dr,dc in offsets:
                nr,nc=r+dr,c+dc
                if 0<=nr<n and 0<=nc<n:
                    following[(nr,nc)]=following.get((nr,nc),0)+probability/8
        states=following
    return sum(states.values())
'''


THREE_WINDOWS = '''\
def maximum_three_subarrays(nums, k):
    windows=[sum(nums[i:i+k]) for i in range(len(nums)-k+1)]
    left=[0]*len(windows);best=0
    for i in range(len(windows)):
        if windows[i]>windows[best]:best=i
        left[i]=best
    right=[0]*len(windows);best=len(windows)-1
    for i in range(len(windows)-1,-1,-1):
        if windows[i]>=windows[best]:best=i
        right[i]=best
    answer=None
    for middle in range(k,len(windows)-k):
        candidate=[left[middle-k],middle,right[middle+k]]
        score=sum(windows[i] for i in candidate)
        if answer is None or score>answer[0]:answer=(score,candidate)
    return answer[1]
'''


GAME_NO_DIVISION = GAME.replace("if abs(b)>1e-12: results.append(a/b)\n                if abs(a)>1e-12: results.append(b/a)","")
GAME_INTEGER_DIVISION = GAME.replace('results.append(a/b)','results.append(a//b)').replace('results.append(b/a)','results.append(b//a)')
SLOTS_OFF_BY_ONE=SLOTS.replace('days = [0] * len(bulbs)', 'k = max(0, k - 1)\n    days = [0] * len(bulbs)')
SLOTS_ADJACENT="def first_k_empty_slots(bulbs,k):\n    return next((day for day in range(2,len(bulbs)+1) if abs(bulbs[day-1]-bulbs[day-2])==k+1),-1)\n"
REDUNDANT_LAST="def redundant_undirected_edge(edges):\n    return edges[-1]\n"
REDUNDANT_SORT=REDUNDANT.replace('for left,right in edges:','for left,right in sorted(edges):')
DIRECTED_UNDIRECTED=DIRECTED.replace("if parent_of[child]: first=[parent_of[child],child];second=edge\n        else: parent_of[child]=parent", "parent_of[child]=parent").replace('return first if first else edge','return edge').replace('return second','return edges[-1]')
DIRECTED_SECOND="def redundant_directed_edge(edges):\n    seen={}\n    for edge in edges:\n        if edge[1] in seen:return edge\n        seen[edge[1]]=edge[0]\n    return edges[-1]\n"
REPEAT_CEIL=REPEAT.replace("if b in text+a:return count+1", "if b in text+a:return count")
REPEAT_LENGTH="def repeated_string_count(a,b):\n    count=(len(b)+len(a)-1)//len(a)\n    return count if b in a*count else -1\n"
KNIGHT_CONDITIONAL=KNIGHT.replace('following.get((nr,nc),0)+probability/8','following.get((nr,nc),0)+probability')
KNIGHT_ONE_LESS=KNIGHT.replace('for _ in range(k):','for _ in range(max(0,k-1)):')
THREE_GREEDY="def maximum_three_subarrays(nums,k):\n    windows=[sum(nums[i:i+k]) for i in range(len(nums)-k+1)]\n    return sorted(range(len(windows)),key=lambda i:(-windows[i],i))[:3]\n"
THREE_LATE=THREE_WINDOWS.replace('if windows[i]>=windows[best]:best=i\n        right[i]=best','if windows[i]>windows[best]:best=i\n        right[i]=best')


def lesson(a,b,c,d):return [a,b,c,d],d


BATCH={
679:entry('can_make_twenty_four',[('cards','list[int]')],'bool',['backtracking','math'],['cards contains exactly four integers from 1 through 9.','Use every card once with +, -, *, /, and parentheses; intermediate fractions are allowed.'],[([[4,1,8,7]],'Eight minus four is four and seven minus one is six, whose product is twenty-four.'),([[1,2,1,2]],'No ordering and operation combination reaches twenty-four.')],[[x] for x in ([1,1,1,8],[3,3,8,8],[1,5,5,5],[6,6,6,6],[1,2,3,4],[2,3,4,5],[9,9,9,9],[1,1,7,7],[2,2,6,6],[4,4,4,4],[1,3,4,6],[5,5,7,7])],GAME,[GAME_NO_DIVISION,GAME_INTEGER_DIVISION],['Omits division, missing fractional constructions.','Uses floor division and loses necessary fractional intermediate values.'],game24_oracle,random_game,*lesson('Any expression combines two current values into one until a single value remains.','Backtrack over unordered pairs and all noncommutative operation orders.','Choose two, replace them with each possible result, and recurse.','Every binary expression tree has a final pairwise operation, so recursive pair reduction enumerates all valid expressions.'),'O(constant search for four cards)','O(1)',8),
683:entry('first_k_empty_slots',[('bulbs','list[int]'),('k','int')],'int',['sliding-windows','arrays'],['bulbs is a permutation of positions 1 through n; 0 <= k <= n-2.','Return the earliest day when two lit bulbs have exactly k unlit positions between them, or -1.'],[([[1,3,2],1], 'On day two, positions one and three are lit while position two remains unlit.'),([[1,2,3],1], 'No day has one unlit bulb strictly between two lit endpoints.')],[[b,k] for b,k in (([1,2],0),([2,1],0),([1,3,2],0),([3,1,2],1),([2,1,3],1),([1,4,2,3],2),([4,1,3,2],1),([2,4,1,3],1),([1,5,3,2,4],3),([5,1,2,3,4],3),([2,5,1,4,3],2),([3,1,5,2,4],1))],SLOTS,[SLOTS_OFF_BY_ONE,SLOTS_ADJACENT],['Uses endpoint distance k instead of k+1.','Checks only bulbs lit on adjacent days rather than all active positions.'],empty_slots_oracle,random_slots,*lesson('Convert positions to the day each bulb turns on.','A valid position window has both endpoints earlier than every interior day.','Scan windows of width k+2; reset when an interior day is earlier than an endpoint.','If no interior bulb is lit by the later endpoint day, exactly k slots are empty at that time.'),'O(n)','O(n)',8),
684:entry('redundant_undirected_edge',[('edges','list[list[int]]')],'list[int]',['graphs','union-find'],['The edges describe a tree on n nodes plus one extra undirected edge.','Return the last input edge whose removal restores a tree.'],[([[[1,2],[1,3],[2,3]]], 'Adding two-three connects vertices already joined through one.'),([[[1,2],[2,3],[3,4],[1,4],[1,5]]], 'Edge one-four is the first edge that closes the unique cycle.')],[[e] for e in ([[1,2],[2,3],[1,3]],[[1,2],[3,4],[2,3],[1,4]],[[1,3],[3,2],[2,4],[4,1]],[[2,3],[1,2],[3,4],[1,4]],[[1,4],[2,3],[1,2],[3,4]],[[1,2],[2,4],[4,3],[3,1]],[[1,5],[5,4],[4,3],[3,2],[2,1]],[[2,1],[3,2],[4,3],[1,4]],[[1,2],[1,3],[1,4],[2,4]],[[1,2],[2,3],[3,1],[3,4]],[[4,1],[1,2],[2,3],[3,4]],[[1,3],[2,3],[2,4],[1,4]])],REDUNDANT,[REDUNDANT_LAST,REDUNDANT_SORT],['Assumes the extra edge is always last in the input.','Sorts edges before cycle detection and loses the required input-order tie behavior.'],redundant_oracle,random_redundant,*lesson('The redundant edge is the one whose endpoints are already connected by earlier edges.','Maintain connected components with union-find in input order.','Find both roots; return the edge if equal, otherwise union them.','Before the unique cycle closes, every edge joins components; the closing edge is exactly the removable answer required by input order.'),'O(n alpha(n))','O(n)',5),
685:entry('redundant_directed_edge',[('edges','list[list[int]]')],'list[int]',['graphs','union-find'],['A rooted directed tree on n nodes has one extra directed edge.','Remove one edge to restore a rooted tree; when multiple answers work, return the one occurring last.'],[([[[1,2],[1,3],[2,3]]], 'Node three has two parents; removing the later edge two-three restores the tree.'),([[[1,2],[2,3],[3,4],[4,1],[1,5]]], 'The directed cycle is broken by removing four-one.')],[[e] for e in ([[1,2],[2,1]],[[1,2],[2,3],[3,1]],[[2,1],[3,1],[4,2],[1,4]],[[1,2],[1,3],[3,4],[2,4]],[[4,2],[1,5],[5,2],[5,3],[2,4]],[[1,2],[2,3],[3,4],[4,2]],[[1,2],[2,3],[4,3],[3,4]],[[1,2],[2,3],[1,3]],[[3,1],[1,2],[2,3]],[[1,2],[3,2],[2,3]],[[2,3],[3,1],[1,2]],[[1,4],[2,1],[3,1],[4,2]])],DIRECTED,[DIRECTED_UNDIRECTED,DIRECTED_SECOND],['Treats the graph as an undirected cycle and mishandles two-parent cases.','Always removes the later incoming edge without checking whether the earlier edge participates in a cycle.'],directed_redundant_oracle,random_directed,*lesson('The extra edge creates either a cycle, a node with two parents, or both.','Record the two-parent candidates, then run union-find while skipping the later candidate.','On a remaining cycle choose the earlier parent edge; otherwise choose the skipped later edge.','These cases exhaust the two ways a rooted-tree invariant can fail: indegree and acyclicity.'),'O(n alpha(n))','O(n)',8),
686:entry('repeated_string_count',[('a','str'),('b','str')],'int',['strings','string-matching'],['1 <= len(a),len(b) <= 10,000.','Return the fewest repetitions of a whose concatenation contains b, or -1.'],[(['abcd','cdabcdab'], 'Three copies form abcdabcdabcd, which contains the target across copy boundaries.'),(['a','aa'], 'Two copies are necessary and sufficient.')],[[a,b] for a,b in (('a','b'),('abc','abc'),('abc','cab'),('abc','cabc'),('ab','baba'),('xyz','zxyzx'),('aa','aaaaa'),('abcd','dabcd'),('abcd','abcdabcd'),('abc','ac'),('aba','aaba'),('x','xxxxx'))],REPEAT,[REPEAT_CEIL,REPEAT_LENGTH],['Reports the ceiling repetition count even when one extra copy is required for a boundary-spanning match.','Never checks the one additional copy needed after reaching the target length.'],repeat_oracle,random_repeat,*lesson('A target match can begin near the end of one copy and finish in the next.','Build the ceiling number of copies, then test it and exactly one additional copy.','q=ceil(len(b)/len(a)); check a*q, then a*(q+1), else -1.','Any longer target needs enough copies for its length, and a start offset shorter than one base copy requires at most one extra copy.'),'O(len(a)+len(b))','O(len(a)+len(b))',5),
688:entry('knight_stay_probability',[('n','int'),('k','int'),('row','int'),('column','int')],'float',['dynamic-programming','probability'],['1 <= n <= 25; 0 <= k <= 100; the starting square is on the board.','Each of eight knight moves is equally likely; return the probability the knight remains on-board after k moves.'],[([3,2,0,0], 'Exactly four of the 64 two-move sequences remain on the board, giving 0.0625.'),([1,0,0,0], 'With zero moves, the knight remains on its starting square with probability one.')],[[n,k,r,c] for n,k,r,c in ((1,1,0,0),(2,1,0,0),(3,1,0,0),(3,1,1,1),(4,1,0,0),(4,2,1,1),(5,2,2,2),(5,3,0,0),(6,2,3,3),(3,3,1,1),(8,1,4,4),(8,4,0,0))],KNIGHT,[KNIGHT_CONDITIONAL,KNIGHT_ONE_LESS],['Renormalizes over only valid moves instead of counting off-board choices as lost probability.','Performs one fewer move than requested.'],knight_oracle,random_knight,*lesson('Probability mass that moves off-board disappears.','Propagate each square’s mass equally to its valid knight destinations for k rounds.','For every state, add probability/8 to each in-bounds destination; sum after k rounds.','Every length-k move sequence has probability 8^-k, and dynamic programming merges sequences ending on the same square.'),'O(k*n²)','O(n²)',5),
689:entry('maximum_three_subarrays',[('nums','list[int]'),('k','int')],'list[int]',['dynamic-programming','sliding-windows'],['3*k <= len(nums) <= 20,000; values are positive.','Return starts of three non-overlapping length-k subarrays with maximum total sum; break ties lexicographically.'],[([[1,2,1,2,6,7,5,1],2], 'The windows starting at 0, 3, and 5 have the maximum total.'), ([[1,2,1,2,1,2,1,2,1],2], 'Several triples tie, and [0,2,4] is lexicographically smallest.')],[[nums,k] for nums,k in (([1,1,1],1),([1,2,3],1),([3,2,1],1),([1,2,3,4,5,6],2),([5,1,1,5,1,1,5],1),([1,1,1,1,1,1],2),([9,1,1,9,1,1,9,1,1],2),([1,5,1,5,1,5,1],1),([4,4,4,4,4,4,4,4],2),([1,2,10,10,2,1,9,9,1],2),([10,1,1,10,1,1,10,1,1],1),([2,3,2,3,8,9,4,2,7],2))],THREE_WINDOWS,[THREE_GREEDY,THREE_LATE],['Chooses the three largest windows independently and permits overlap.','Uses later indices when equal sums require lexicographically earlier ones.'],three_windows_oracle,random_three_windows,*lesson('Fixing the middle window separates the optimal left and right choices.','Precompute window sums plus best prefix and suffix window indices with careful tie directions.','For each middle, combine left[middle-k], middle, and right[middle+k].','Strict prefix updates retain early ties, while reverse suffix updates retain the earliest suffix; scanning middles left-to-right completes lexicographic tie-breaking.'),'O(n)','O(n)',8),
}
BATCH[688]['comparator']='float'
