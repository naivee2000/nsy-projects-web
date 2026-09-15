"""Trie, geometry, heap, weighted-tree, and matrix-prefix workbook imports."""
from collections import deque
from itertools import combinations

from .import_batch_055 import entry


def border_pairs_oracle(args):
    words = args[0]
    return sum(
        words[j].startswith(words[i]) and words[j].endswith(words[i])
        for i in range(len(words)) for j in range(i + 1, len(words))
    )


def random_border_pairs(rng):
    return [["".join(rng.choice("abcd") for _ in range(rng.randint(1, 8)))
             for _ in range(rng.randint(1, 12))]]


def square_oracle(args):
    lower, upper = args
    best = 0
    for i in range(len(lower)):
        for j in range(i + 1, len(lower)):
            width = min(upper[i][0], upper[j][0]) - max(lower[i][0], lower[j][0])
            height = min(upper[i][1], upper[j][1]) - max(lower[i][1], lower[j][1])
            for side in range(1, max(0, min(width, height)) + 1):
                best = max(best, side * side)
    return best


def random_square(rng):
    lower, upper = [], []
    for _ in range(rng.randint(2, 8)):
        x, y = rng.randint(-8, 8), rng.randint(-8, 8)
        lower.append([x, y])
        upper.append([x + rng.randint(1, 8), y + rng.randint(1, 8)])
    return [lower, upper]


def threshold_oracle(args):
    values, target = sorted(args[0]), args[1]
    operations = 0
    while values[0] < target:
        first, second = values.pop(0), values.pop(0)
        combined = 2 * first + second
        index = 0
        while index < len(values) and values[index] < combined:
            index += 1
        values.insert(index, combined)
        operations += 1
    return operations


def random_threshold(rng):
    values = [rng.randint(1, 30) for _ in range(rng.randint(2, 12))]
    combined = sorted(values)
    while len(combined) > 1:
        first, second = combined.pop(0), combined.pop(0)
        value = 2 * first + second
        index = 0
        while index < len(combined) and combined[index] < value:
            index += 1
        combined.insert(index, value)
    return [values, rng.randint(1, combined[0])]


def server_oracle(args):
    edges, speed = args
    size = len(edges) + 1
    graph = [[] for _ in range(size)]
    for left, right, weight in edges:
        graph[left].append((right, weight)); graph[right].append((left, weight))
    answer = []
    for center in range(size):
        first_branch = [-1] * size
        distance = [0] * size
        queue = deque()
        for neighbor, weight in graph[center]:
            first_branch[neighbor] = neighbor
            distance[neighbor] = weight
            queue.append((neighbor, center))
        while queue:
            node, parent = queue.popleft()
            for neighbor, weight in graph[node]:
                if neighbor == parent:
                    continue
                first_branch[neighbor] = first_branch[node]
                distance[neighbor] = distance[node] + weight
                queue.append((neighbor, node))
        total = 0
        for left in range(size):
            for right in range(left + 1, size):
                if (left != center and right != center and
                    first_branch[left] != first_branch[right] and
                    distance[left] % speed == 0 and distance[right] % speed == 0):
                    total += 1
        answer.append(total)
    return answer


def random_server(rng):
    edges = []
    for node in range(1, rng.randint(2, 10)):
        edges.append([node, rng.randrange(node), rng.randint(1, 15)])
    rng.shuffle(edges)
    return [edges, rng.randint(1, 8)]


def top_left_oracle(args):
    grid, target = args
    answer = 0
    for bottom in range(len(grid)):
        for right in range(len(grid[0])):
            total = sum(grid[row][column]
                        for row in range(bottom + 1)
                        for column in range(right + 1))
            answer += total <= target
    return answer


def random_top_left(rng):
    rows, columns = rng.randint(1, 6), rng.randint(1, 6)
    return [[[rng.randint(0, 12) for _ in range(columns)] for _ in range(rows)],
            rng.randint(0, 100)]


BORDER = '''def count_prefix_suffix_pairs(words):
    trie={};answer=0
    for word in words:
        node=trie
        for pair in zip(word,reversed(word)):
            node=node.setdefault(pair,{})
            answer+=node.get(None,0)
        node[None]=node.get(None,0)+1
    return answer
'''


SQUARE = '''def largest_square_intersection_area(bottom_left,top_right):
    from itertools import combinations
    answer=0
    rectangles=zip(bottom_left,top_right)
    for (low1,high1),(low2,high2) in combinations(rectangles,2):
        width=min(high1[0],high2[0])-max(low1[0],low2[0])
        height=min(high1[1],high2[1])-max(low1[1],low2[1])
        side=min(width,height)
        if side>0:answer=max(answer,side*side)
    return answer
'''


THRESHOLD = '''def minimum_threshold_combinations(nums,k):
    from heapq import heapify,heappop,heappush
    heap=list(nums);heapify(heap);answer=0
    while heap[0]<k:
        first=heappop(heap);second=heappop(heap)
        heappush(heap,2*first+second)
        answer+=1
    return answer
'''


SERVERS = '''def connectable_server_pairs(edges,signal_speed):
    size=len(edges)+1;graph=[[] for _ in range(size)]
    for left,right,weight in edges:
        graph[left].append((right,weight));graph[right].append((left,weight))
    def count_branch(node,parent,distance):
        total=int(distance%signal_speed==0)
        for neighbor,weight in graph[node]:
            if neighbor!=parent:total+=count_branch(neighbor,node,distance+weight)
        return total
    answer=[0]*size
    for center in range(size):
        earlier=0
        for neighbor,weight in graph[center]:
            current=count_branch(neighbor,center,weight)
            answer[center]+=earlier*current
            earlier+=current
    return answer
'''


TOP_LEFT = '''def count_top_left_submatrices(grid,k):
    rows=len(grid);columns=len(grid[0]);prefix=[[0]*(columns+1) for _ in range(rows+1)]
    answer=0
    for row in range(1,rows+1):
        for column in range(1,columns+1):
            prefix[row][column]=(prefix[row-1][column]+prefix[row][column-1]
                -prefix[row-1][column-1]+grid[row-1][column-1])
            answer+=prefix[row][column]<=k
    return answer
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3045: entry('count_prefix_suffix_pairs',[('words','list[str]')],'int',['tries','strings','string matching'],['words contains nonempty lowercase strings.','Count ordered index pairs i<j where words[i] is both a prefix and a suffix of words[j].','Repeated words at different indices count as distinct pairs.'],[([['a','aba','ababa','aa']],'The word a borders each of the three later words, and aba borders ababa, giving four pairs.'),([['pa','papa','ma','mama']],'Pa borders papa and ma borders mama; neither short word borders the other family.')],[[w] for w in [['a'],['a','a'],['a','b'],['ab','ab'],['a','aa','aaa'],['ab','aba'],['ab','abab'],['abc','zabc'],['abc','abczabc'],['x','xyx','x'],['aa','aaaa','aa'],['ab','cababc','abab'],['z','zz','zzz','zzzz'],['abc','abcabc','bc']]],BORDER,["""def count_prefix_suffix_pairs(words):
    return sum(words[j].startswith(words[i]) for i in range(len(words)) for j in range(i+1,len(words)))
""","""def count_prefix_suffix_pairs(words):
    return sum(words[i]==words[j] for i in range(len(words)) for j in range(i+1,len(words)))
"""],['Checks the prefix condition but ignores the required suffix.','Counts only equal strings and misses proper borders.'],border_pairs_oracle,random_border_pairs,lesson('Pairing the next front and back characters lets one trie path represent being a prefix and suffix simultaneously.','Insert earlier words into a trie keyed by (front character, back character), adding terminal counts while scanning each new word.','For each word, walk zipped forward/reversed characters; add terminal count at every depth; mark the final node terminal.','At depth d the path matches exactly the first and last d characters, so every terminal encountered is precisely one earlier border word.'),'O(total characters)','O(total characters)',8),
3047: entry('largest_square_intersection_area',[('bottom_left','list[list[int]]'),('top_right','list[list[int]]')],'int',['geometry','arrays','enumeration'],['The two arrays describe at least two axis-aligned rectangles with positive width and height.','For every rectangle pair, a square may be placed anywhere inside their intersection.','Return the greatest possible square area, or zero when every pair has empty or line-only intersection.'],[([[[1,1],[2,2],[3,1]],[[3,3],[4,4],[6,6]]],'The first two rectangles overlap in a one-by-one square; no pair permits a larger one.'),([[[0,0],[2,1]],[[5,4],[7,6]]],'The overlap is three units wide and three high, so the maximum square area is nine.')],[[a,b] for a,b in [([[0,0],[2,2]],[[1,1],[3,3]]),([[0,0],[1,1]],[[1,1],[2,2]]),([[0,0],[3,1]],[[4,4],[6,5]]),([[0,0],[1,0]],[[4,2],[5,3]]),([[-3,-3],[-2,-2]],[[0,0],[1,1]]),([[0,0],[2,1],[1,2]],[[4,4],[6,5],[3,6]]),([[1,1],[1,1]],[[10,2],[2,10]]),([[0,0],[4,4]],[[10,10],[8,9]]),([[0,0],[2,2],[8,8]],[[5,5],[7,7],[9,9]]),([[0,0],[-1,-1]],[[2,8],[8,2]]),([[1,2],[3,1]],[[9,7],[8,9]]),([[0,0],[5,2],[2,5]],[[9,9],[7,7],[7,7]]),([[10,10],[11,11]],[[20,20],[19,19]]),([[0,0],[3,3],[4,4]],[[6,6],[7,7],[9,9]])]],SQUARE,[SQUARE.replace('side=min(width,height)','side=max(width,height)'),SQUARE.replace('side*side','width*height')],['Uses the longer overlap dimension even when the square cannot fit in the shorter one.','Returns the full rectangular intersection area rather than its largest inscribed square.'],square_oracle,random_square,lesson('A square inside an axis-aligned intersection is limited by the smaller overlap dimension.','Enumerate rectangle pairs and compute their horizontal and vertical overlap lengths.','For each pair set side=min(right-left,top-bottom); if positive maximize side squared.','Every qualifying square belongs to some pair intersection, and a rectangle of width w and height h contains a square of side min(w,h).'),'O(n^2)','O(1)',5),
3066: entry('minimum_threshold_combinations',[('nums','list[int]'),('k','int')],'int',['heaps','greedy','simulation'],['nums contains at least two positive integers and k is positive.','While some value is below k, remove the two smallest values x≤y and insert 2*x+y.','Return the number of operations needed until every remaining value is at least k.'],[([[2,11,10,1,3],10],'Combine one and two into four, then three and four into ten; all remaining values are at least ten after two operations.'),([[1,1,2,4,9],20],'Repeatedly combining the two current minima requires four operations before the final value reaches twenty.')],[[a,k] for a,k in [([1,2],3),([1,2],4),([5,6],5),([5,6],6),([1,1,1],3),([1,2,3],10),([2,2,2,2],7),([1,10,10],10),([3,4,5,6],20),([10,1,7,2],8),([100,1],101),([8,8,8],17),([1,2,4,8,16],30),([9,3,6,12,1],15)]],THRESHOLD,[THRESHOLD.replace('2*first+second','first+second'),THRESHOLD.replace('while heap[0]<k','while len(heap)>1 and heap[1]<k')],['Adds the two minima without doubling the smaller value.','Stops according to the second heap slot, which is neither necessarily the minimum nor the required stopping condition.'],threshold_oracle,random_threshold,lesson('The operation is forced by the two current minima, so the only task is maintaining that order efficiently.','Use a min-heap; repeatedly pop twice, push 2*x+y, and count until the heap minimum reaches k.','Heapify once; while heap[0]<k: x=pop, y=pop, push 2*x+y.','The heap exposes exactly the required two smallest values each round, and heap[0]≥k is equivalent to every remaining value meeting the threshold.'),'O(n log n)','O(n)',5),
3067: entry('connectable_server_pairs',[('edges','list[list[int]]'),('signal_speed','int')],'list[int]',['trees','depth-first search','weighted graphs'],['edges describes a connected weighted tree with vertices 0 through n-1 and positive weights.','For center c, both endpoint distances from c must be divisible by signal_speed and their paths from c must share no edge.','Return the qualifying unordered endpoint-pair count for every possible center.'],[([[[0,1,1],[1,2,5],[2,3,13],[3,4,9],[4,5,2]],1],'At internal centers, qualifying endpoints from different branches form 4, 6, 6, and 4 pairs; leaves have none.'),([[[0,1,3],[1,2,3],[1,3,1]],3],'At center one, servers zero and two are both distance three in different branches, producing one pair.')],[[e,s] for e,s in [([[0,1,1]],1),([[0,1,2]],3),([[0,1,1],[1,2,1]],1),([[0,1,1],[1,2,1]],2),([[0,1,2],[0,2,4]],2),([[0,1,2],[1,2,2],[1,3,2]],2),([[0,1,1],[0,2,1],[0,3,1]],1),([[0,1,1],[1,2,2],[2,3,3]],3),([[0,1,5],[0,2,10],[2,3,5]],5),([[0,1,2],[1,2,3],[1,3,4],[3,4,5]],2),([[0,1,7],[1,2,7],[1,3,7],[3,4,7]],7),([[0,1,1],[0,2,2],[2,3,1],[2,4,2]],2),([[0,1,6],[1,2,4],[2,3,2],[2,4,8]],2),([[0,1,3],[0,2,6],[0,3,9],[3,4,3]],3)]],SERVERS,[SERVERS.replace('answer[center]+=earlier*current','answer[center]+=current'),SERVERS.replace('distance%signal_speed==0','(distance+1)%signal_speed==0')],['Adds branch counts instead of cross-branch products, so it counts endpoints rather than endpoint pairs.','Adds one to every path distance before testing divisibility.'],server_oracle,random_server,lesson('Removing a center separates the tree into neighbor branches; two paths share no center-adjacent edge exactly when endpoints lie in different branches.','For each center, count speed-divisible distances within each neighbor branch, then combine branch counts pairwise.','DFS each branch with accumulated distance; add earlier_count*current_count and then extend earlier_count.','Each valid pair has one endpoint in each of two unique branches and is counted once when the later branch is combined with all earlier branches.'),'O(n^2)','O(n)',5),
3070: entry('count_top_left_submatrices',[('grid','list[list[int]]'),('k','int')],'int',['matrices','prefix sums','arrays'],['grid is a nonempty rectangular matrix of nonnegative integers.','Count submatrices whose upper-left corner is grid[0][0] and whose sum is at most k.','Each choice of bottom row and right column identifies one candidate.'],[([[[7,6,3],[6,6,1]],18],'Prefix rectangles ending at the first two cells of row zero and the first two cells of column zero contribute four qualifying sums.'),([[[1,2],[3,4]],7],'The one-cell, top row, and left column rectangles have sums one, three, and four; the full sum ten is too large.')],[[g,k] for g,k in [([[0]],0),([[1]],0),([[1]],1),([[1,2]],3),([[1,2]],2),([[1],[2]],3),([[1,2],[3,4]],10),([[1,2],[3,4]],9),([[0,0],[0,0]],0),([[5,0,0],[0,0,0]],5),([[2,1,3],[1,0,1]],4),([[9,1],[1,1],[1,1]],12),([[3,3,3],[3,3,3]],8),([[1,4,2],[0,1,3],[2,0,1]],9)]],TOP_LEFT,[TOP_LEFT.replace('<=k','<k'),TOP_LEFT.replace('-prefix[row-1][column-1]','+prefix[row-1][column-1]')],['Rejects submatrices whose sum equals k even though equality is allowed.','Adds the overlapping prefix twice instead of subtracting it in inclusion-exclusion.'],top_left_oracle,random_top_left,lesson('Every requested submatrix is a prefix rectangle, so one two-dimensional prefix value gives its entire sum.','Build the prefix table row by row and count each cell whose prefix sum is at most k.','prefix[r][c]=up+left-diagonal+grid[r-1][c-1]; increment when prefix[r][c]≤k.','The inclusion-exclusion formula equals the sum of exactly rows 0..r-1 and columns 0..c-1, covering every candidate once.'),'O(rows*columns)','O(rows*columns)',5),
}
