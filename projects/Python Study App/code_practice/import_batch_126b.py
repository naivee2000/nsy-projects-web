"""Second slice of workbook batch 126."""

from collections import deque

from .import_batch_055 import entry


def closest_oracle(args):
    n, edges, queries = args
    graph = [[] for _ in range(n)]
    for left, right in edges:
        graph[left].append(right); graph[right].append(left)
    answers = []
    for start, end, target in queries:
        parent = {start: -1}; queue = deque([start])
        while queue:
            node = queue.popleft()
            if node == end: break
            for neighbor in graph[node]:
                if neighbor not in parent: parent[neighbor] = node; queue.append(neighbor)
        path = []; node = end
        while node != -1: path.append(node); node = parent[node]
        distance = {target: 0}; queue = deque([target])
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if neighbor not in distance: distance[neighbor] = distance[node] + 1; queue.append(neighbor)
        answers.append(min(path, key=lambda node: distance[node]))
    return answers


def random_closest(rng):
    n = rng.randint(1, 15)
    edges = [[node, rng.randrange(node)] for node in range(1, n)]
    queries = [[rng.randrange(n), rng.randrange(n), rng.randrange(n)] for _ in range(rng.randint(1, 12))]
    return [n, edges, queries]


def percent_oracle(args):
    text, letter = args
    return sum(char == letter for char in text) * 100 // len(text)


def random_percent(rng):
    text = "".join(rng.choice("abcdef") for _ in range(rng.randint(1, 40)))
    return [text, rng.choice("abcdef")]


def bags_oracle(args):
    capacity, rocks, extra = args
    needs = [maximum - current for maximum, current in zip(capacity, rocks)]
    best = 0
    for mask in range(1 << len(needs)):
        selected = [needs[index] for index in range(len(needs)) if mask >> index & 1]
        if sum(selected) <= extra: best = max(best, len(selected))
    return best


def random_bags(rng):
    n = rng.randint(1, 10); capacity = [rng.randint(1, 20) for _ in range(n)]
    return [capacity, [rng.randint(0, value) for value in capacity], rng.randint(0, 30)]


def lines_oracle(args):
    points = sorted(args[0])
    if len(points) < 2: return 0
    answer = 1
    for index in range(2, len(points)):
        x0,y0=points[index-2];x1,y1=points[index-1];x2,y2=points[index]
        answer += (y1-y0)*(x2-x1) != (y2-y1)*(x1-x0)
    return answer


def random_lines(rng):
    days = rng.sample(range(1, 50), rng.randint(1, 12))
    return [[[day, rng.randint(1, 40)] for day in days]]


def strength_oracle(args):
    values = args[0]; answer = 0
    for left in range(len(values)):
        total = 0; minimum = 10**18
        for right in range(left, len(values)):
            total += values[right]; minimum = min(minimum, values[right]); answer += total * minimum
    return answer % 1_000_000_007


def random_strength(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(1, 11))]]


CLOSEST = '''\
def closest_nodes_on_tree_paths(n,edges,query):
    graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    levels=max(1,n.bit_length());up=[[0]*n for _ in range(levels)];depth=[0]*n;stack=[(0,-1)]
    while stack:
        node,parent=stack.pop();up[0][node]=node if parent<0 else parent
        for neighbor in graph[node]:
            if neighbor!=parent:depth[neighbor]=depth[node]+1;stack.append((neighbor,node))
    for level in range(1,levels):
        for node in range(n):up[level][node]=up[level-1][up[level-1][node]]
    def lca(left,right):
        if depth[left]<depth[right]:left,right=right,left
        difference=depth[left]-depth[right]
        for level in range(levels):
            if difference>>level&1:left=up[level][left]
        if left==right:return left
        for level in range(levels-1,-1,-1):
            if up[level][left]!=up[level][right]:left=up[level][left];right=up[level][right]
        return up[0][left]
    return [max((lca(start,end),lca(start,target),lca(end,target)),key=lambda node:depth[node]) for start,end,target in query]
'''

PERCENT = '''\
def letter_percentage(s,letter):
    return s.count(letter)*100//len(s)
'''

BAGS = '''\
def maximum_full_rock_bags(capacity,rocks,additional_rocks):
    answer=0
    for needed in sorted(maximum-current for maximum,current in zip(capacity,rocks)):
        if needed>additional_rocks:break
        additional_rocks-=needed;answer+=1
    return answer
'''

LINES = '''\
def minimum_stock_chart_lines(stock_prices):
    points=sorted(stock_prices)
    if len(points)<2:return 0
    answer=1
    for index in range(2,len(points)):
        x0,y0=points[index-2];x1,y1=points[index-1];x2,y2=points[index]
        if (y1-y0)*(x2-x1)!=(y2-y1)*(x1-x0):answer+=1
    return answer
'''

STRENGTH = '''\
def sum_total_wizard_strength(strength):
    modulo=1000000007;n=len(strength);left=[-1]*n;right=[n]*n;stack=[]
    for index,value in enumerate(strength):
        while stack and strength[stack[-1]]>=value:stack.pop()
        left[index]=stack[-1] if stack else -1;stack.append(index)
    stack=[]
    for index in range(n-1,-1,-1):
        while stack and strength[stack[-1]]>strength[index]:stack.pop()
        right[index]=stack[-1] if stack else n;stack.append(index)
    prefix=[0]*(n+1)
    for index,value in enumerate(strength):prefix[index+1]=(prefix[index]+value)%modulo
    double=[0]*(n+2)
    for index,value in enumerate(prefix):double[index+1]=(double[index]+value)%modulo
    answer=0
    for index,value in enumerate(strength):
        starts=index-left[index];ends=right[index]-index
        right_sums=double[right[index]+1]-double[index+1]
        left_sums=double[index+1]-double[left[index]+1]
        answer=(answer+value*(starts*right_sums-ends*left_sums))%modulo
    return answer
'''


BATCH = {
    2277: entry('closest_nodes_on_tree_paths',[('n','int'),('edges','list[list[int]]'),('query','list[list[int]]')],'list[int]',['trees','lowest common ancestor','binary lifting'],['edges form one connected undirected tree on nodes zero through n-1.','Each query [start,end,target] asks for the node on the unique start-to-end path minimizing distance to target.','Return one node per query in input order.'],[([7,[[0,1],[0,2],[0,3],[1,4],[2,5],[2,6]],[[5,3,4],[5,3,6]]],'The projections of targets four and six onto path 5-2-0-3 are nodes zero and two.'),([1,[],[[0,0,0]]],'The only path and target contain node zero, so return zero.')],[[n,e,q] for n,e,q in [(1,[],[[0,0,0]]),(2,[[0,1]],[[0,1,0],[0,1,1]]),(7,[[0,1],[0,2],[0,3],[1,4],[2,5],[2,6]],[[5,3,4],[5,3,6]]),(4,[[0,1],[1,2],[2,3]],[[0,3,1],[0,1,3]]),(5,[[0,1],[0,2],[0,3],[0,4]],[[1,2,3],[1,4,0]]),(6,[[0,1],[1,2],[1,3],[3,4],[3,5]],[[2,4,5]]),(3,[[0,1],[0,2]],[[1,2,1]]),(7,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]],[[1,5,6],[2,4,0]]),(5,[[0,1],[1,2],[2,3],[2,4]],[[3,4,0]]),(6,[[0,1],[0,2],[2,3],[2,4],[4,5]],[[1,3,5]]),(4,[[0,1],[0,2],[2,3]],[[1,3,2]]),(8,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6],[6,7]],[[3,7,4]]),(3,[[0,1],[1,2]],[[1,1,2]]),(5,[[0,1],[0,2],[1,3],[1,4]],[[3,4,2]])]],CLOSEST,[CLOSEST.replace('key=lambda node:depth[node]','key=lambda node:-depth[node]'),CLOSEST.replace('lca(end,target)','lca(start,target)')],['Chooses the shallowest candidate rather than the deepest path projection.','Duplicates one LCA candidate and omits the endpoint-target relationship.'],closest_oracle,random_closest,['Root the tree and preprocess binary ancestors plus node depths for LCA queries.','For query (a,b,x), the path projection is the deepest of LCA(a,b), LCA(a,x), and LCA(b,x).','Compute those three candidates and select maximum depth.','The three pairwise LCAs capture the unique branching junction of the three nodes; its deepest candidate lies on a-b and minimizes distance from x.'],'O((n+queries) log n)','O(n log n)',8),
    2278: entry('letter_percentage',[('s','str'),('letter','str')],'int',['strings'],['Count occurrences of the one-character letter in nonempty string s.','Compute count*100/len(s) and round down.','Return the integer percentage from zero through one hundred.'],[(['foobar','o'],'Two of six characters are o, so floor(200/6) is thirty-three.'),(['jjjj','j'],'Every character matches, producing one hundred percent.')],[[s,c] for s,c in [('a','a'),('a','b'),('foobar','o'),('jjjj','j'),('abc','a'),('abc','z'),('aaaaab','a'),('mississippi','s'),('leetcode','e'),('xyzxyz','x'),('hello','l'),('banana','a'),('programming','m'),('qwerty','q')]],PERCENT,[PERCENT.replace('*100',''),PERCENT.replace('//','/')],['Returns the raw fraction count divided by length instead of a percentage.','Uses floating-point division instead of flooring to an integer.'],percent_oracle,random_percent,['The numerator is the matching-character count times one hundred.','Integer floor division performs the required rounding down.','Return s.count(letter)*100//len(s).','The expression is the exact percentage formula, and floor division maps it to the required whole number.'],'O(n)','O(1)',3),
    2279: entry('maximum_full_rock_bags',[('capacity','list[int]'),('rocks','list[int]'),('additional_rocks','int')],'int',['arrays','greedy','sorting'],['Bag i needs capacity[i]-rocks[i] additional rocks to become full.','Distribute at most additional_rocks rocks and maximize the number of full bags.','Already-full bags have zero cost and count toward the answer.'],[([[2,3,4,5],[1,2,4,4],2],'The deficits are one, one, zero, one; filling two one-deficit bags yields three full bags.'),([[10,2,2],[2,2,0],100],'The large supply can fill every bag, so return three.')],[[c,r,a] for c,r,a in [([1],[0],0),([1],[1],0),([2,3,4,5],[1,2,4,4],2),([10,2,2],[2,2,0],100),([5,5],[0,0],5),([3,4],[3,1],0),([2,2,2],[1,1,1],2),([10,10,10],[9,1,9],2),([1,2,3],[0,0,0],3),([5,6,7],[5,6,0],0),([8,3,9],[2,2,8],7),([4,4,4,4],[3,3,3,3],4),([100,1],[0,0],1),([7,8,9],[6,6,6],5)]],BAGS,[BAGS.replace('sorted(','sorted(',1).replace(')):', '),reverse=True):',1),BAGS.replace('needed>additional_rocks','needed>=additional_rocks')],['Fills the most expensive deficits first instead of the cheapest.','Refuses a bag whose deficit exactly equals the remaining rocks.'],bags_oracle,random_bags,['Each full bag is an item worth one with cost equal to its deficit.','To maximize item count under a budget, buy deficits from smallest to largest.','Sort capacity-rocks; consume affordable deficits until the next exceeds remaining rocks.','An exchange replacing any chosen larger deficit with an unchosen smaller one preserves count and never costs more, proving greedy optimality.'],'O(n log n)','O(n)',6),
    2280: entry('minimum_stock_chart_lines',[('stock_prices','list[list[int]]')],'int',['geometry','arrays','sorting'],['Every point has a distinct day coordinate.','After sorting by day, consecutive point pairs share one line segment exactly while their slopes are equal.','Return zero for one point; otherwise count maximal equal-slope runs using exact integer arithmetic.'],[([[[1,7],[2,6],[3,5],[4,4],[5,4],[6,3],[7,2],[8,1]]],'The sorted chart changes slope twice, so three line segments are required.'),([[[3,4],[1,2],[7,8],[2,3]]],'All sorted points lie on one line, so one segment suffices.')],[[p] for p in [[[1,1]],[[1,1],[2,2]],[[1,7],[2,6],[3,5],[4,4],[5,4],[6,3],[7,2],[8,1]],[[3,4],[1,2],[7,8],[2,3]],[[1,1],[3,2],[5,3]],[[1,1],[2,3],[3,6]],[[10,5],[1,5],[7,5]],[[1,10],[2,1],[4,1]],[[1,1],[1000000000,999999999],[999999999,999999998]],[[2,4],[1,2],[3,6],[4,9]],[[1,3],[2,2],[3,1]],[[5,5],[1,1],[3,3]],[[1,1],[2,2],[4,4],[5,6]],[[4,8],[2,4],[1,2]]]],LINES,[LINES.replace('!=','==',1),LINES.replace('points=sorted(stock_prices)','points=stock_prices')],['Counts a new line when slopes stay equal instead of when they change.','Uses the unsorted input order rather than chronological day order.'],lines_oracle,random_lines,['Sort points by day, because the chart connects them chronologically.','Compare adjacent slopes by cross multiplication to avoid floating-point precision errors.','Start with one line for at least two points and increment whenever dy1*dx2 differs from dy2*dx1.','Equal cross products mean consecutive segments are collinear; every inequality starts exactly one necessary new line.'],'O(n log n)','O(n)',6),
    2281: entry('sum_total_wizard_strength',[('strength','list[int]')],'int',['arrays','monotonic stacks','prefix sums'],['For every nonempty contiguous subarray, multiply its minimum value by its element sum.','Add those total-strength values and return modulo 1,000,000,007.','Equal minima must be assigned consistently so every subarray is counted exactly once.'],[([[1,3,1,2]],'The ten subarray total-strength values sum to forty-four.'),([[5,4,6]],'The six subarrays contribute 25,36,60,16,40,36, totaling 213.')],[[x] for x in [[1],[1,1],[1,3,1,2],[5,4,6],[1,2,3],[3,2,1],[2,2,2],[1,5,1],[10,1,10],[4,3,2,5],[5,1,2,1,5],[7,7,1,7],[2,6,3,4],[9,8,7,6]]],STRENGTH,[STRENGTH.replace('>=value','>value'),STRENGTH.replace('value*(starts*right_sums-ends*left_sums)','starts*right_sums-ends*left_sums')],['Uses strict boundaries on both sides and double-counts or omits subarrays with equal minima.','Sums subarray values but forgets to multiply each contribution by its minimum strength.'],strength_oracle,random_strength,['Assign each subarray to one minimum index using previous strictly smaller and next smaller-or-equal boundaries.','Double prefix sums aggregate the sums of all subarrays containing that minimum without enumerating endpoints.','For index i, combine start_count*right_prefix_total minus end_count*left_prefix_total, then multiply by strength[i].','The monotonic boundaries partition subarrays uniquely, and the double-prefix algebra equals the sum of every assigned subarray’s element sum.'],'O(n)','O(n)',8),
}

BATCH[2279]['wrong'][0] = '''\
def maximum_full_rock_bags(capacity,rocks,additional_rocks):
    answer=0
    for needed in sorted((maximum-current for maximum,current in zip(capacity,rocks)),reverse=True):
        if needed>additional_rocks:break
        additional_rocks-=needed;answer+=1
    return answer
'''
BATCH[2280]['boundaries'].append([[[1,1],[2,1],[4,2],[3,1]]])
