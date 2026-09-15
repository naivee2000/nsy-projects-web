"""Tree matching, digit construction, infection, subsequence-heap, and matrix-search imports."""
from itertools import combinations, permutations

from .import_batch_055 import entry


class Node:
    def __init__(self,value):self.val=value;self.left=None;self.right=None


def make_tree(values):
    if not values:return None
    nodes=[None if value is None else Node(value) for value in values];children=iter(nodes[1:])
    for node in nodes:
        if node is not None:node.left=next(children,None);node.right=next(children,None)
    return nodes[0]


def edge_score_oracle(args):
    edges=args[0];best=0
    for mask in range(1<<(len(edges)-1)):
        used=set();score=0;valid=True
        for child in range(1,len(edges)):
            if mask>>(child-1)&1:
                parent,weight=edges[child]
                if child in used or parent in used:valid=False;break
                used.update((child,parent));score+=weight
        if valid:best=max(best,score)
    return best


def random_edge_score(rng):
    size=rng.randint(1,10);edges=[[-1,-1]]
    for node in range(1,size):edges.append([rng.randrange(node),rng.randint(-5,15)])
    return [edges]


def palindrome_oracle(args):
    num=args[0];best='0'
    for length in range(1,len(num)+1):
        for order in set(permutations(num,length)):
            if length>1 and order[0]=='0':continue
            value=''.join(order)
            if value==value[::-1] and (len(value)>len(best) or len(value)==len(best) and value>best):best=value
    return best


def random_palindrome(rng):return [''.join(str(rng.randint(0,5)) for _ in range(rng.randint(1,7)))]


def infection_oracle(args):
    root=make_tree(args[0]);start=args[1];graph={}
    def connect(node,parent=None):
        if node is None:return
        graph.setdefault(node.val,[])
        if parent is not None:graph[node.val].append(parent.val);graph[parent.val].append(node.val)
        connect(node.left,node);connect(node.right,node)
    connect(root);seen={start};frontier={start};minutes=-1
    while frontier:
        minutes+=1;frontier={neighbor for node in frontier for neighbor in graph[node] if neighbor not in seen};seen.update(frontier)
    return minutes


def random_infection(rng):
    size=rng.randint(1,12);values=list(range(1,size+1));serialized=[values[0]];queue=[0];next_value=1
    while queue and next_value<size:
        queue.pop(0)
        for _ in range(2):
            if next_value<size and (rng.random()<.75 or not queue):serialized.append(values[next_value]);queue.append(next_value);next_value+=1
            else:serialized.append(None)
    while serialized and serialized[-1] is None:serialized.pop()
    return [serialized,rng.choice(values)]


def ksum_oracle(args):
    nums,k=args
    sums=[sum(nums[index] for index in range(len(nums)) if mask>>index&1) for mask in range(1<<len(nums))]
    return sorted(sums,reverse=True)[k-1]


def random_ksum(rng):
    size=rng.randint(1,10);nums=[rng.randint(-15,15) for _ in range(size)]
    return [nums,rng.randint(1,1<<size)]


def median_oracle(args):
    values=sorted(value for row in args[0] for value in row)
    return values[len(values)//2]


def random_median(rng):
    rows,cols=rng.choice([1,3,5]),rng.choice([1,3,5])
    return [[sorted(rng.randint(1,30) for _ in range(cols)) for _ in range(rows)]]


EDGE_SCORE='''def maximum_nonadjacent_edge_score(edges):
    children=[[] for _ in edges]
    for node in range(1,len(edges)):
        parent,weight=edges[node];children[parent].append((node,weight))
    def visit(node):
        blocked=0;child_states=[]
        for child,weight in children[node]:
            child_free,child_blocked=visit(child);blocked+=child_free;child_states.append((weight,child_free,child_blocked))
        free=blocked
        for weight,child_free,child_blocked in child_states:free=max(free,blocked-child_free+child_blocked+weight)
        return free,blocked
    return visit(0)[0]
'''

PALINDROME='''def largest_digit_palindrome(num):
    counts=[num.count(str(digit)) for digit in range(10)];left=[]
    for digit in range(9,0,-1):left.extend(str(digit) for _ in range(counts[digit]//2))
    if left:left.extend('0' for _ in range(counts[0]//2))
    middle=next((str(digit) for digit in range(9,-1,-1) if counts[digit]%2), '')
    if not left:return middle or '0'
    return ''.join(left)+middle+''.join(reversed(left))
'''

INFECTION='''def binary_tree_infection_time(root,start):
    graph={};stack=[(root,None)]
    while stack:
        node,parent=stack.pop();graph.setdefault(node.val,[])
        if parent is not None:graph[node.val].append(parent.val);graph[parent.val].append(node.val)
        if node.left:stack.append((node.left,node))
        if node.right:stack.append((node.right,node))
    seen={start};frontier=[start];minutes=-1
    while frontier:
        minutes+=1;following=[]
        for node in frontier:
            for neighbor in graph[node]:
                if neighbor not in seen:seen.add(neighbor);following.append(neighbor)
        frontier=following
    return minutes
'''

KSUM='''def kth_largest_subsequence_sum(nums,k):
    import heapq
    maximum=sum(value for value in nums if value>0);values=sorted(abs(value) for value in nums)
    if k==1:return maximum
    heap=[(values[0],0)];removed=0
    for _ in range(k-1):
        removed,index=heapq.heappop(heap)
        if index+1<len(values):
            heapq.heappush(heap,(removed+values[index+1],index+1))
            heapq.heappush(heap,(removed-values[index]+values[index+1],index+1))
    return maximum-removed
'''

MEDIAN='''def row_sorted_matrix_median(grid):
    import bisect
    low=min(row[0] for row in grid);high=max(row[-1] for row in grid);needed=(len(grid)*len(grid[0]))//2+1
    while low<high:
        middle=(low+high)//2
        count=sum(bisect.bisect_right(row,middle) for row in grid)
        if count>=needed:high=middle
        else:low=middle+1
    return low
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
2378:entry('maximum_nonadjacent_edge_score',[('edges','list[list[int]]')],'int',['trees','dynamic programming','matching'],['edges[i]=[parent,weight] describes the rooted weighted edge to node i; edges[0]=[-1,-1].','Choose edges sharing no endpoint; choosing none is allowed.','Return the maximum possible weight sum, even when some weights are negative.'],[([[[-1,-1],[0,5],[0,10],[2,6],[2,4]]],'Choose the weight-five edge at the root and the weight-six edge below node two, totaling eleven.'),([[[-1,-1],[0,-2],[0,-3]]],'Every available edge is negative, so choosing no edge gives zero.')],[[e] for e in [[[-1,-1]],[[-1,-1],[0,5]],[[-1,-1],[0,-5]],[[-1,-1],[0,2],[0,3]],[[-1,-1],[0,2],[1,3]],[[-1,-1],[0,2],[1,3],[1,4]],[[-1,-1],[0,5],[0,1],[1,10]],[[-1,-1],[0,4],[0,4],[1,4],[1,4]],[[-1,-1],[0,1],[1,2],[2,3]],[[-1,-1],[0,10],[0,9],[1,8],[2,7]],[[-1,-1],[0,-1],[1,5],[1,6]],[[-1,-1],[0,3],[0,8],[2,4],[2,9]],[[-1,-1],[0,2],[1,2],[2,2],[3,2]],[[-1,-1],[0,7],[0,6],[1,5],[1,4],[2,3]]]],EDGE_SCORE,[EDGE_SCORE.replace('return visit(0)[0]','return sum(max(0, weight) for _, weight in edges[1:])'),EDGE_SCORE.replace('return visit(0)[0]',"return max([0]+[weight for _,weight in edges[1:]])")],['Adds every positive edge even when selected edges share an endpoint.','Chooses only one edge and misses solutions containing disjoint edges.'],edge_score_oracle,random_edge_score,lesson('For each node, compare states where its parent edge is unavailable versus may be chosen.','Without choosing a child edge, add each child’s unrestricted optimum; choosing one child edge switches that child to its blocked state.','Compute the baseline and the best single child-edge improvement.','A matching can use at most one edge incident to the current node, so these states enumerate every local possibility and independent child subtrees add.'),'O(n)','O(height)',8),
2384:entry('largest_digit_palindrome',[('num','str')],'str',['strings','counting','greedy'],['num has 1 through 100000 decimal digits.','Use at least one available digit to form the numerically largest palindrome with no leading zero.','Not every digit must be used; return the result as a string.'],[(['444947137'],'Use paired sevens and fours around the best remaining middle digit nine to form 7449447.'),(['00009'],'Zero cannot lead a multi-digit number, so the best palindrome is the single digit nine.')],[[s] for s in ['0','9','00','000','11','101','1000','123','1122','00011','98766789','543210','9998887','1000001']],PALINDROME,[PALINDROME.replace('range(9,0,-1)','range(8,0,-1)'),PALINDROME.replace("if left:left.extend('0'","if True:left.extend('0'")],['Never uses digit nine as an outer pair.','Uses zero pairs even when they become forbidden leading zeros.'],palindrome_oracle,random_palindrome,lesson('The left half determines the palindrome’s length and most significant digits.','Take every available nonzero pair from nine downward, then zero pairs only after a nonzero leading pair exists.','Choose the largest remaining odd-count digit as the optional middle and mirror the left half.','More paired digits always increases length, and within a fixed length descending outer digits maximize the number lexicographically.'),'O(n)','O(n) output',5),
2385:entry('binary_tree_infection_time',[('root','TreeNode'),('start','int')],'int',['trees','breadth-first search','graphs'],['The binary tree has 1 through 100000 nodes with unique integer values, and start occurs exactly once.','At minute zero start is infected; each minute infection crosses every parent-child edge from infected nodes.','Return the first minute when all nodes are infected.'],[([[1,5,3,None,4,10,6,9,2],3],'The farthest nodes nine and two are four edges from value three, so infection needs four minutes.'),([[1],1],'The only node is infected at minute zero, so return zero.')],[[t,s] for t,s in [([1,2],1),([1,2],2),([1,None,2,None,3],1),([1,None,2,None,3],3),([2,1,3],1),([2,1,3],2),([4,2,6,1,3,5,7],1),([4,2,6,1,3,5,7],4),([1,2,3,4,None,None,5],4),([1,2,3,4,None,None,5],5),([10,5,15,2,7,12,20],7),([5,4,None,3,None,2,None,1],5),([5,4,None,3,None,2,None,1],1),([8,3,10,1,6,None,14,None,None,4,7,13],6)]],INFECTION,[INFECTION.replace('graph[node.val].append(parent.val);graph[parent.val].append(node.val)','graph[parent.val].append(node.val)'),INFECTION.replace('minutes=-1','minutes=0')],['Builds only parent-to-child edges, preventing infection from moving upward.','Starts the minute counter at zero before processing the initial frontier and overcounts by one.'],infection_oracle,random_infection,lesson('Infection can move both down to children and up to a parent.','Convert the tree into an undirected adjacency map, then run breadth-first layers from start.','Each completed frontier corresponds to one elapsed minute; stop after the last nonempty layer.','BFS distance is infection time, so the maximum layer distance is exactly the time to reach every node.'),'O(nodes)','O(nodes)',5),
2386:entry('kth_largest_subsequence_sum',[('nums','list[int]'),('k','int')],'int',['heaps','sorting','subsequences'],['nums has up to 100000 signed integers; k is at most min(2000,2^n).','Every index may be included or excluded, and equal sums from different subsequences count separately.','Return the kth largest subsequence sum, including the empty subsequence sum zero.'],[([[2,4,-2],5],'The descending sums are 6,4,4,2,2,0,0,-2, so the fifth is two.'),([[1,-2,3,4,-10,12],16],'Best-first enumeration of removed absolute values makes ten the sixteenth-largest sum.')],[[n,k] for n,k in [([1],1),([1],2),([-1],1),([-1],2),([0],1),([0],2),([1,2],3),([1,-1],2),([1,-1],3),([2,2],4),([3,-2,1],4),([5,-4,-3],5),([0,0,0],8),([4,1,-2,3],10)]],KSUM,[KSUM.replace('maximum=sum(value for value in nums if value>0)','maximum=sum(nums)'),KSUM.replace('for _ in range(k-1)','for _ in range(max(0,k-2))')],['Starts from the sum of every value instead of the maximum sum containing only positives.','Pops one fewer excluded-cost state, returning the preceding rank.'],ksum_oracle,random_ksum,lesson('The largest subsequence sum includes every positive value and excludes every negative value.','Any other sum subtracts a subset of absolute values from that maximum.','Sort absolute values and use a min-heap to enumerate subset-removal costs in increasing order without generating all subsets.','The two heap transitions uniquely extend or replace the latest chosen absolute value, producing removal costs in order; subtracting the kth cost reverses them into descending subsequence sums.'),'O(n log n+k log k)','O(n+k)',8),
2387:entry('row_sorted_matrix_median',[('grid','list[list[int]]')],'int',['binary search','matrices'],['grid has odd row and column counts up to 500, each row is nondecreasing, and values are 1 through 1000000.','The total number of entries is odd.','Return the middle value of all entries without flattening the matrix; target time is below O(rows*columns).'],[([[[1,1,2],[2,3,3],[1,3,4]]],'Five of nine entries are at most two, making two the median.'),([[[1,1,3,3,4]]],'The middle of the five sorted row values is three.')],[[g] for g in [[[1]],[[1,2,3]],[[1],[2],[3]],[[1,1,1],[1,1,1],[1,1,1]],[[1,2,9],[3,4,8],[5,6,7]],[[1,5,9],[2,6,10],[3,7,11]],[[1,2,3,4,5]],[[5],[5],[9]],[[1,100,100],[2,3,4],[5,6,7]],[[1,1,9],[2,2,8],[3,3,7]],[[10,20,30],[1,2,3],[4,5,6]],[[1,4,7,10,13],[2,5,8,11,14],[3,6,9,12,15]],[[1000000]],[[1,2,2],[2,2,3],[2,4,5]]]],MEDIAN,[MEDIAN.replace('bisect.bisect_right','bisect.bisect_left'),MEDIAN.replace('//2+1','//2')],['Counts values strictly below the candidate and mishandles duplicate medians.','Searches for only half the entries rather than the one-based middle rank.'],median_oracle,random_median,lesson('For a candidate value, each sorted row reveals its count of entries at most that candidate by binary search.','The total count is monotone as the candidate increases.','Binary-search the smallest value whose cumulative count reaches total//2+1.','That lower-bound value has at least the median rank at or below it while every smaller value has fewer, which characterizes the median.'),'O(rows*log(value_range)*log(cols))','O(1)',5),
}
BATCH[2385]['params'][0]=('root','TreeNode','treenode')
