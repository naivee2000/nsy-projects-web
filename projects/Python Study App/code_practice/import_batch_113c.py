"""Third reviewed group of workbook batch 113."""

from collections import deque
from heapq import heappop, heappush

from .import_batch_055 import entry


MOD = 1_000_000_007


def path_oracle(args):
    n, edges, source, destination = args
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    return find(source) == find(destination)


def descendants_oracle(args):
    values = args[0]
    if not values:
        return 0
    children = [[None, None] for _ in values]
    queue = deque([0])
    index = 1
    while queue and index < len(values):
        parent = queue.popleft()
        for side in range(2):
            if index < len(values) and values[index] is not None:
                children[parent][side] = index
                queue.append(index)
            index += 1
    def visit(node):
        if node is None:
            return 0, 0
        left_sum, left_count = visit(children[node][0])
        right_sum, right_count = visit(children[node][1])
        value = values[node]
        return value + left_sum + right_sum, left_count + right_count + (value == left_sum + right_sum)
    return visit(0)[1]


def typing_oracle(args):
    word = args[0]
    position = 0
    total = len(word)
    for char in word:
        target = ord(char) - 97
        clockwise = (target - position) % 26
        counterclockwise = (position - target) % 26
        total += min(clockwise, counterclockwise)
        position = target
    return total


def matrix_oracle(args):
    flat = [value for row in args[0] for value in row]
    total = sum(abs(value) for value in flat)
    if sum(value < 0 for value in flat) % 2:
        total -= 2 * min(map(abs, flat))
    return total


def routes_oracle(args):
    n, roads = args
    graph = [[] for _ in range(n)]
    for a, b, time in roads:
        graph[a].append((b, time)); graph[b].append((a, time))
    distance = [10 ** 30] * n
    ways = [0] * n
    distance[0] = 0; ways[0] = 1
    queue = [(0, 0)]
    while queue:
        elapsed, node = heappop(queue)
        if elapsed != distance[node]:
            continue
        for neighbor, cost in graph[node]:
            candidate = elapsed + cost
            if candidate < distance[neighbor]:
                distance[neighbor] = candidate; ways[neighbor] = ways[node]
                heappush(queue, (candidate, neighbor))
            elif candidate == distance[neighbor]:
                ways[neighbor] = (ways[neighbor] + ways[node]) % MOD
    return ways[-1]


def random_path(rng):
    n = rng.randint(1, 25)
    edges = []
    for a in range(n):
        for b in range(a + 1, n):
            if rng.random() < .12:
                edges.append([a, b])
    return [n, edges, rng.randrange(n), rng.randrange(n)]


def random_tree(rng):
    size = rng.randint(0, 31)
    if not size:
        return [[]]
    values = [rng.randint(-10, 10)]
    for _ in range(1, size):
        values.append(None if rng.random() < .22 else rng.randint(-10, 10))
    while values and values[-1] is None:
        values.pop()
    return [values]


def random_word(rng):
    return [''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(rng.randint(1, 100)))]


def random_matrix(rng):
    rows, columns = rng.randint(1, 8), rng.randint(1, 8)
    return [[[rng.randint(-20, 20) for _ in range(columns)] for _ in range(rows)]]


def random_routes(rng):
    n = rng.randint(2, 10)
    roads = [[i - 1, i, rng.randint(1, 10)] for i in range(1, n)]
    present = {(a, b) for a, b, _ in roads}
    for a in range(n):
        for b in range(a + 2, n):
            if (a, b) not in present and rng.random() < .2:
                roads.append([a, b, rng.randint(1, 15)])
    return [n, roads]


PATH = '''\
def valid_graph_path(n, edges, source, destination):
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)
    stack = [source]
    seen = {source}
    while stack:
        node = stack.pop()
        if node == destination:
            return True
        for neighbor in graph[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return False
'''

DESCENDANTS = '''\
def count_nodes_equal_to_descendants(root):
    answer = 0
    def subtree(node):
        nonlocal answer
        if node is None:
            return 0
        descendant_sum = subtree(node.left) + subtree(node.right)
        if node.val == descendant_sum:
            answer += 1
        return node.val + descendant_sum
    subtree(root)
    return answer
'''

TYPE = '''\
def minimum_typewriter_time(word):
    position = 0
    answer = len(word)
    for char in word:
        target = ord(char) - ord('a')
        distance = abs(target - position)
        answer += min(distance, 26 - distance)
        position = target
    return answer
'''

MATRIX = '''\
def maximum_matrix_sum(matrix):
    absolute_sum = sum(abs(value) for row in matrix for value in row)
    negative_count = sum(value < 0 for row in matrix for value in row)
    smallest = min(abs(value) for row in matrix for value in row)
    return absolute_sum if negative_count % 2 == 0 else absolute_sum - 2 * smallest
'''

ROUTES = '''\
def count_shortest_routes(n, roads):
    from heapq import heappop, heappush
    mod = 1_000_000_007
    graph = [[] for _ in range(n)]
    for a, b, travel_time in roads:
        graph[a].append((b, travel_time))
        graph[b].append((a, travel_time))
    distance = [float('inf')] * n
    ways = [0] * n
    distance[0] = 0
    ways[0] = 1
    heap = [(0, 0)]
    while heap:
        elapsed, node = heappop(heap)
        if elapsed > distance[node]:
            continue
        for neighbor, cost in graph[node]:
            candidate = elapsed + cost
            if candidate < distance[neighbor]:
                distance[neighbor] = candidate
                ways[neighbor] = ways[node]
                heappush(heap, (candidate, neighbor))
            elif candidate == distance[neighbor]:
                ways[neighbor] = (ways[neighbor] + ways[node]) % mod
    return ways[n - 1]
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1971: entry('valid_graph_path',[('n','int'),('edges','list[list[int]]'),('source','int'),('destination','int')],'bool',['graphs','depth-first search'],
        ['1 <= n <= 200000; vertices are numbered 0 through n-1.','edges contains undirected connections and has at most 200000 entries.','Return whether source and destination belong to the same connected component.'],
        [([3,[[0,1],[1,2],[2,0]],0,2],'Every vertex lies in one cycle, so zero can reach two.'),([6,[[0,1],[0,2],[3,5],[5,4],[4,3]],0,5],'The endpoints lie in separate components, so no path exists.')],
        [[n,e,s,d] for n,e,s,d in [(1,[],0,0),(2,[],0,1),(2,[[0,1]],0,1),(4,[[0,1],[2,3]],1,3),(4,[[0,1],[1,2]],0,2),(5,[[0,1],[1,2],[2,3],[3,4]],4,0),(5,[[0,1],[1,2]],2,2),(5,[[0,1],[0,2],[0,3],[0,4]],1,4),(6,[[0,1],[2,3],[3,4]],2,4),(6,[[0,1],[1,2],[3,4],[4,5]],0,5),(3,[[0,1]],2,0),(7,[[0,1],[1,2],[2,0],[4,5],[5,6]],4,6),(4,[[0,1],[1,2],[2,3]],3,1),(8,[[0,7]],0,7)]],
        PATH,[PATH.replace("graph[b].append(a)","# directed only"),PATH.replace("if node == destination:","if node != destination:")],
        ['Treats undirected edges as directed and misses paths traversed backward.','Reverses the destination test and returns before actually reaching the target.'],path_oracle,random_path,
        lesson('Reachability asks whether the destination is in the source connected component.','Build both directions, then traverse while recording visited vertices.','Push source; repeatedly pop, return on destination, and push each unseen neighbor.','Traversal reaches exactly the vertices connected by a path; the visited set bounds each vertex to one expansion.'),'O(n + edges)','O(n + edges)',3),
    1973: entry('count_nodes_equal_to_descendants',[('root','TreeNode | None')],'int',['trees','recursion','postorder traversal'],
        ['The tree contains 1 through 100000 nodes with values from -100000 through 100000.','A node matches when its value equals the sum of every strict descendant; a leaf therefore matches exactly when its value is zero.','Return the number of matching nodes.'],
        [([[10,3,4,2,1]],'Node three equals two plus one, and root ten equals all four descendants, so two nodes match.'),([[0,0,0]],'Both zero leaves and the zero root equal their descendant sums, so all three match.')],
        [[t] for t in [[1],[0],[1,1],[1,0],[3,1,2],[6,3,1,1,2],[10,3,4,2,1],[0,0,0],[-3,-1,-2],[5,2,3,None,None,1,2],[4,4,None,0],[7,3,4,1,2,2,2],[1,-1,2],[8,3,5,1,2,None,5]]],
        DESCENDANTS,[DESCENDANTS.replace('node.val == descendant_sum','node.val == descendant_sum + node.val'),DESCENDANTS.replace('return node.val + descendant_sum','return descendant_sum')],
        ['Compares against a sum that includes the node itself.','Fails to include child values when returning a subtree sum to the parent.'],descendants_oracle,random_tree,
        lesson('A parent needs the total of each child subtree, making this a postorder computation.','Return subtree sums upward and compare each node with the two child sums before adding its own value.','left=subtree(left); right=subtree(right); count if val==left+right; return val+left+right.','Induction on subtree height proves each return is its exact total, so every comparison uses precisely all strict descendants.'),'O(n)','O(height)',5),
    1974: entry('minimum_typewriter_time',[('word','str')],'int',['strings','greedy','circular distance'],
        ['word contains 1 through 100 lowercase English letters.','The pointer begins at a on a circular alphabet; each clockwise or counterclockwise step costs one second.','Typing the current letter costs one second; return the minimum total time.'],
        [(['abc'],'Move zero, one, and one steps and spend three seconds typing, totaling five.'),(['bza'],'The circular moves cost one, two, and one, plus three typing seconds, totaling seven.')],
        [[w] for w in ['a','z','az','za','abc','bza','zzz','aaa','m','n','an','na','leetcode','algorithm','abcdefghijklmnopqrstuvwxyz','zyxwvutsrqponmlkjihgfedcba']],
        TYPE,[TYPE.replace('min(distance, 26 - distance)','distance'),TYPE.replace('answer = len(word)','answer = 0')],
        ['Always rotates directly through the alphabet and ignores the shorter wraparound route.','Counts movement but omits the one-second cost of typing each letter.'],typing_oracle,random_word,
        lesson('Between consecutive letters only their circular distance matters.','For alphabet indices x and y, add min(abs(x-y),26-abs(x-y)), then one for typing.','Start at index zero; accumulate circular movement and word length.','Each move is independent and the two directions have complementary lengths, so choosing the shorter direction at every step is globally optimal.'),'O(n)','O(1)',3),
    1975: entry('maximum_matrix_sum',[('matrix','list[list[int]]')],'int',['matrices','greedy','parity'],
        ['matrix is nonempty, square, and has side length at most 250.','One operation negates two orthogonally adjacent entries; operations may repeat.','Return the largest possible sum after any number of operations.'],
        [([[[1,-1],[-1,1]]],'Two negatives have even parity, so all four magnitudes can contribute positively for a sum of four.'),([[[-1,2],[3,4]]],'With odd negative parity, magnitude one must remain negative, giving eight.')],
        [[m] for m in [[[0]],[[1]],[[-1]],[[1,-1],[-1,1]],[[-1,2],[3,4]],[[1,2],[3,4]],[[-1,-2],[-3,-4]],[[0,-2],[3,4]],[[5,-1,2],[3,-4,6],[7,8,-9]],[[0,0],[0,0]],[[10,-10],[-10,10]],[[-5]],[[1,-2,3],[-4,5,-6],[7,-8,9]],[[2,2],[-2,2]]]],
        MATRIX,[MATRIX.replace('negative_count % 2 == 0','negative_count % 2 == 1'),MATRIX.replace('2 * smallest','smallest')],
        ['Reverses the parity condition and penalizes even-negative matrices.','Subtracts the unavoidable magnitude only once instead of changing it from positive to negative.'],matrix_oracle,random_matrix,
        lesson('Pair negations let signs move through the connected grid, so only negative-count parity is invariant unless a zero absorbs it.','Take every absolute value; if parity is odd, leave the smallest magnitude negative.','total=sum(abs); if negatives odd subtract 2*min(abs).','Any even set of signs can be corrected through adjacent operations. Odd parity forces one negative, and choosing the smallest magnitude loses the least sum.'),'O(rows*columns)','O(1)',5),
    1976: entry('count_shortest_routes',[('n','int'),('roads','list[list[int]]')],'int',['graphs','Dijkstra','dynamic programming'],
        ['2 <= n <= 200; roads is an undirected connected graph with positive travel times and no duplicate edge.','Count distinct paths from zero to n-1 whose travel time is minimum.','Return the count modulo 1000000007.'],
        [([7,[[0,6,7],[0,1,2],[1,2,3],[1,3,3],[6,3,3],[3,5,1],[6,5,1],[2,5,1],[0,4,5],[4,6,2]]],'Four distinct routes reach node six in the minimum time seven.'),([2,[[1,0,10]]],'The only road is the single shortest route, so the answer is one.')],
        [[n,r] for n,r in [(2,[[0,1,1]]),(2,[[0,1,10]]),(3,[[0,1,1],[1,2,1],[0,2,2]]),(3,[[0,1,2],[1,2,2],[0,2,3]]),(4,[[0,1,1],[1,3,1],[0,2,1],[2,3,1]]),(4,[[0,1,1],[1,2,1],[2,3,1],[0,3,5]]),(5,[[0,1,1],[1,4,3],[0,2,2],[2,4,2],[0,3,3],[3,4,1]]),(5,[[0,1,2],[1,2,2],[2,4,2],[0,3,1],[3,4,10]]),(6,[[0,1,1],[1,5,4],[0,2,2],[2,5,3],[0,3,3],[3,5,2],[0,4,4],[4,5,1]]),(3,[[0,1,5],[1,2,5]]),(4,[[0,1,10],[0,2,1],[2,1,1],[1,3,1],[2,3,10]]),(5,[[0,1,1],[1,2,1],[2,4,1],[0,3,2],[3,4,1]]),(6,[[0,1,2],[1,5,2],[0,2,1],[2,3,1],[3,5,2],[2,4,1],[4,5,2]]),(4,[[0,1,1],[1,2,1],[2,3,1]])]],
        ROUTES,[ROUTES.replace('ways[neighbor] = ways[node]','ways[neighbor] += ways[node]'),ROUTES.replace("elif candidate == distance[neighbor]:","elif candidate < distance[neighbor]:")],
        ['Carries stale route counts when a strictly shorter distance replaces the old one.','Treats a longer-or-equal candidate as another shortest route.'],routes_oracle,random_routes,
        lesson('Shortest-path counting extends Dijkstra by storing how many best routes reach each vertex.','On improvement replace both distance and count; on an equal distance add the predecessor count.','Pop minimum distance; relax each edge; set ways[v]=ways[u] for shorter and add for equal.','Positive weights ensure a popped shortest distance is final, and the two relaxation cases partition shortest paths by their final edge.'),'O((n + roads) log n)','O(n + roads)',6),
}

BATCH[1973]['params'][0] = ('root', 'TreeNode | None', 'treenode')
