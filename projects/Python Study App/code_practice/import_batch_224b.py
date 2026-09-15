"""Graph thresholds, increment windows, medians, array matching, and special paths."""
from itertools import permutations

from .import_batch_055 import entry


def graph_oracle(args):
    n,edges,_=args
    for limit in sorted({weight for _,_,weight in edges}):
        reverse=[[] for _ in range(n)]
        for left,right,weight in edges:
            if weight<=limit:reverse[right].append(left)
        seen={0};stack=[0]
        while stack:
            for node in reverse[stack.pop()]:
                if node not in seen:seen.add(node);stack.append(node)
        if len(seen)==n:return limit
    return -1


def random_graph(rng):
    n=rng.randint(2,8);possible=[(a,b) for a in range(n) for b in range(n) if a!=b]
    chosen=rng.sample(possible,rng.randint(1,min(len(possible),14)))
    return [n,[[a,b,rng.randint(1,15)] for a,b in chosen],rng.randint(1,n-1)]


def nondecreasing_cost(values):
    maximum=values[0];cost=0
    for value in values[1:]:maximum=max(maximum,value);cost+=maximum-value
    return cost


def subarrays_oracle(args):
    nums,k=args
    return sum(nondecreasing_cost(nums[left:right])<=k for left in range(len(nums)) for right in range(left+1,len(nums)+1))


def random_subarrays(rng):
    return [[rng.randint(1,12) for _ in range(rng.randint(1,12))],rng.randint(1,25)]


def median_oracle(args):
    nums,k=args;answer=10**30
    for left in range(len(nums)-k+1):
        window=sorted(nums[left:left+k]);median=window[k//2]
        answer=min(answer,sum(abs(value-median) for value in window))
    return answer


def random_median(rng):
    n=rng.randint(2,12)
    return [[rng.randint(-15,15) for _ in range(n)],rng.randint(2,n)]


def arrays_oracle(args):
    arr,brr,k=args;direct=sum(abs(a-b) for a,b in zip(arr,brr));reordered=10**30
    for order in permutations(arr):reordered=min(reordered,k+sum(abs(a-b) for a,b in zip(order,brr)))
    return min(direct,reordered)


def random_arrays(rng):
    n=rng.randint(1,7)
    return [[rng.randint(-9,9) for _ in range(n)],[rng.randint(-9,9) for _ in range(n)],rng.randint(0,15)]


def path_oracle(args):
    edges,values=args;n=len(values);graph=[[] for _ in range(n)]
    for left,right,weight in edges:graph[left].append((right,weight));graph[right].append((left,weight))
    parent=[-1]*n;distance=[0]*n;paths=[None]*n;paths[0]=[0];stack=[0]
    for node in stack:
        for child,weight in graph[node]:
            if child!=parent[node]:parent[child]=node;distance[child]=distance[node]+weight;paths[child]=paths[node]+[child];stack.append(child)
    best_length=0;best_nodes=1
    for end in range(n):
        path=paths[end]
        for start in range(len(path)):
            segment=path[start:]
            if len({values[node] for node in segment})==len(segment):
                length=distance[end]-distance[segment[0]];nodes=len(segment)
                if length>best_length or (length==best_length and nodes<best_nodes):best_length,best_nodes=length,nodes
    return [best_length,best_nodes]


def random_path(rng):
    n=rng.randint(2,9);edges=[[rng.randrange(node),node,rng.randint(1,9)] for node in range(1,n)]
    rng.shuffle(edges);return [edges,[rng.randint(0,5) for _ in range(n)]]


GRAPH='''def minimum_reachable_edge_limit(n,edges,threshold):
    reverse=[[] for _ in range(n)]
    for left,right,weight in edges:reverse[right].append((left,weight))
    def possible(limit):
        seen={0};stack=[0]
        while stack:
            node=stack.pop()
            for neighbor,weight in reverse[node]:
                if weight<=limit and neighbor not in seen:seen.add(neighbor);stack.append(neighbor)
        return len(seen)==n
    low=0;high=max((weight for _,_,weight in edges),default=0)+1
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return -1 if low>max((weight for _,_,weight in edges),default=0) else low
'''

SUBARRAYS='''def count_incrementable_nondecreasing_subarrays(nums,k):
    from collections import deque
    blocks=deque();cost=0;right=len(nums)-1;answer=0
    for left in range(len(nums)-1,-1,-1):
        while blocks and nums[blocks[-1]]<nums[left]:
            index=blocks.pop();boundary=blocks[-1] if blocks else right+1
            cost+=(boundary-index)*(nums[left]-nums[index])
        blocks.append(left)
        while cost>k:
            cost-=nums[blocks[0]]-nums[right]
            if blocks[0]==right:blocks.popleft()
            right-=1
        answer+=right-left+1
    return answer
'''

MEDIAN='''def minimum_window_equalization_operations(nums,k):
    values=sorted(set(nums));indices={value:index+1 for index,value in enumerate(values)};size=len(values);counts=[0]*(size+1);sums=[0]*(size+1)
    def add(value,delta):
        index=indices[value]
        while index<=size:counts[index]+=delta;sums[index]+=delta*value;index+=index&-index
    def prefix(tree,index):
        total=0
        while index:total+=tree[index];index-=index&-index
        return total
    def kth(order):
        index=0;bit=1<<(size.bit_length()-1)
        while bit:
            nxt=index+bit
            if nxt<=size and counts[nxt]<order:order-=counts[nxt];index=nxt
            bit//=2
        return index+1
    answer=10**30
    for right,value in enumerate(nums):
        add(value,1)
        if right>=k:
            add(nums[right-k],-1)
        if right>=k-1:
            middle=kth((k+1)//2);median=values[middle-1];left_count=prefix(counts,middle);left_sum=prefix(sums,middle);total=prefix(sums,size)
            answer=min(answer,median*left_count-left_sum+(total-left_sum)-median*(k-left_count))
    return answer
'''

ARRAYS='''def minimum_identical_array_cost(arr,brr,k):
    direct=sum(abs(left-right) for left,right in zip(arr,brr))
    reordered=k+sum(abs(left-right) for left,right in zip(sorted(arr),sorted(brr)))
    return min(direct,reordered)
'''

PATH='''def longest_unique_downward_tree_path(edges,nums):
    n=len(nums);graph=[[] for _ in range(n)]
    for left,right,weight in edges:graph[left].append((right,weight));graph[right].append((left,weight))
    last={};distances=[];best_length=0;best_nodes=1;stack=[('enter',0,-1,0,0,0)]
    while stack:
        action,node,parent,depth,distance,left=stack.pop();value=nums[node]
        if action=='exit':
            previous=left
            if previous<0:last.pop(value,None)
            else:last[value]=previous
            distances.pop();continue
        previous=last.get(value,-1);new_left=max(left,previous+1);last[value]=depth;distances.append(distance)
        length=distance-distances[new_left];nodes=depth-new_left+1
        if length>best_length or (length==best_length and nodes<best_nodes):best_length,best_nodes=length,nodes
        stack.append(('exit',node,parent,depth,distance,previous))
        for child,weight in reversed(graph[node]):
            if child!=parent:stack.append(('enter',child,node,depth+1,distance+weight,new_left))
    return [best_length,best_nodes]
'''


def lesson(a,b,c,d):return [a,b,c,d]


GRAPH_CASES=[[n,e,t] for n,e,t in [
    (5,[[1,0,1],[2,0,2],[3,0,1],[4,3,1],[2,1,1]],2),(2,[[1,0,5]],1),(2,[[0,1,1]],1),
    (3,[[1,0,4],[2,1,3]],1),(3,[[1,0,4],[2,0,7]],2),(4,[[1,0,8],[2,1,2],[3,2,5],[3,0,9]],1),
    (4,[[1,2,1],[2,1,2],[3,0,3]],2),(3,[[1,0,10],[1,0,2],[2,1,4]],1),
    (5,[[1,0,3],[2,0,3],[3,1,4],[4,2,5]],4),(4,[[0,1,1],[1,2,2],[2,3,3],[3,0,4]],1),
    (3,[[1,0,1],[2,0,1]],1),(6,[[1,0,6],[2,1,5],[3,2,4],[4,3,3],[5,4,2]],2),
    (4,[[1,0,2],[2,0,2],[3,1,2],[3,2,1]],1),(5,[[1,0,10],[2,1,1],[3,2,1],[4,3,1],[4,0,7]],3)]]
SUBARRAY_CASES=[[nums,k] for nums,k in [
    ([6,3,1,2,4,4],7),([1],1),([1,2,3],1),([3,2,1],1),([3,2,1],3),([5,1,5],4),
    ([2,2,2],1),([4,1,3,2],5),([10,1,1,10],9),([1,5,2,6,3],4),
    ([7,6,5,4],6),([1,3,2,2,4],2),([9,1,8,2,7,3],15),([4,4,1,1,4],6)]]
MEDIAN_CASES=[[nums,k] for nums,k in [
    ([4,-3,2,1,-4,6],3),([1,2],2),([1,1],2),([1,2,3],2),([1,2,3],3),([-3,-1,-2],2),
    ([5,1,5,1],3),([10,0,-10,0],4),([1,100,2,99],2),([4,4,4,4],3),
    ([-5,5,-5,5,-5],4),([7,2,9,1,8],3),([0,1,2,3,4,5],5),([6,-4,3,-2,1],2)]]
ARRAY_CASES=[[a,b,k] for a,b,k in [
    ([-7,9,5],[7,-2,-5],2),([1],[2],0),([1,2],[1,2],5),([1,2],[2,1],1),([1,10],[10,1],100),
    ([-1,-2],[-2,-1],0),([1,3,5],[2,4,6],3),([5,5,1],[1,5,5],2),([0,10,20],[20,10,0],5),
    ([1,2,100],[2,100,1],10),([-5,0,5],[5,0,-5],1),([4,1,7,2],[1,2,4,7],3),
    ([9,8,7],[1,2,3],4),([1,1,2,2],[2,2,1,1],0)]]
PATH_CASES=[[edges,values] for edges,values in [
    ([[0,1,2],[1,2,3],[1,3,5],[1,4,4],[2,5,6]],[2,1,2,1,3,1]),([[0,1,5]],[1,2]),
    ([[0,1,5]],[1,1]),([[0,1,2],[1,2,3]],[1,2,3]),([[0,1,2],[1,2,3]],[1,2,1]),
    ([[0,1,4],[0,2,5]],[1,2,3]),([[0,1,1],[1,2,1],[2,3,1]],[1,1,2,3]),
    ([[0,1,10],[1,2,1],[1,3,8]],[0,1,2,3]),([[0,1,3],[0,2,4],[2,3,5]],[1,2,1,3]),
    ([[0,1,2],[1,2,2],[2,3,2],[3,4,2]],[1,2,3,4,5]),
    ([[0,1,2],[1,2,2],[2,3,2],[3,4,2]],[1,2,1,2,3]),
    ([[0,1,7],[0,2,1],[2,3,9],[2,4,2]],[5,4,3,2,1]),
    ([[0,1,1],[1,2,10],[1,3,3],[3,4,8]],[0,1,2,2,3]),
    ([[0,1,6],[1,2,5],[1,3,4],[3,4,3],[3,5,2]],[1,2,3,1,4,5])]]


BATCH={
3419:entry('minimum_reachable_edge_limit',[('n','int'),('edges','list[list[int]]'),('threshold','int')],'int',['graphs','binary search','reachability'],['2 <= n <= 100,000; directed weighted edges have positive weights; threshold is at least one.','Remove edges so every node can reach node zero and each node retains at most threshold outgoing edges.','Minimize the largest retained edge weight, or return -1 when reachability is impossible.'],[([5,[[1,0,1],[2,0,2],[3,0,1],[4,3,1],[2,1,1]],2],'Using only weight-one edges still gives every node a path to zero, so the minimum limit is one.'),([2,[[0,1,1]],1],'Node one has no path to zero under any limit, so return -1.')],GRAPH_CASES,GRAPH,[GRAPH.replace('reverse[right].append((left,weight))','reverse[left].append((right,weight))'),GRAPH.replace('weight<=limit','weight<limit')],['Traverses outward from zero instead of reversing edges to test who can reach zero.','Treats an edge whose weight equals the candidate limit as unavailable.'],graph_oracle,random_graph,lesson('With threshold at least one, a reachable solution can keep one next edge per nonzero node, so the degree cap does not change feasibility.','Binary-search a weight limit and traverse reversed eligible edges from zero.','Keep edges of weight at most the limit; if reversed reachability visits n nodes, lower the limit.','Reverse reachability is equivalent to every original node reaching zero, and feasibility is monotone in the weight limit.'),'O((n+e) log W)','O(n+e)',6),
3420:entry('count_incrementable_nondecreasing_subarrays',[('nums','list[int]'),('k','int')],'int',['arrays','monotonic queues','sliding window'],['nums has up to 100,000 positive values and k is positive.','Within each chosen subarray, one operation increments one element by one.','Count subarrays requiring at most k operations to become non-decreasing.'],[([[6,3,1,2,4,4],7],'Seventeen subarrays can be raised to non-decreasing order within seven increments.'),([[3,2,1],1],'The singletons and subarray [3,2] qualify, giving four.')],SUBARRAY_CASES,SUBARRAYS,[SUBARRAYS.replace('while cost>k','while cost>=k'),SUBARRAYS.replace('cost+=(boundary-index)*(nums[left]-nums[index])','cost+=0')],['Uses a strict budget and discards windows costing exactly k.','Merges prefix-maximum blocks without charging the increments needed to raise them.'],subarrays_oracle,random_subarrays,lesson('For a fixed left boundary, the minimum increments equal the area needed to raise values to successive prefix maxima.','Scan leftward with a monotonic block deque and shrink the right edge while cost exceeds k.','Merge lower prefix-max blocks when adding a left value; subtract the rightmost block height gap when removing right.','The deque represents the exact raised profile, and cost monotonicity makes every shorter suffix of a feasible window feasible.'),'O(n)','O(n)',8),
3422:entry('minimum_window_equalization_operations',[('nums','list[int]'),('k','int')],'int',['arrays','sliding window','fenwick trees'],['nums has up to 100,000 integers and 2 <= k <= len(nums).','One operation increments or decrements one chosen element by one.','Return the fewest operations needed to make every element of some length-k subarray equal.'],[([[4,-3,2,1,-4,6],3],'The best length-three window can be moved to its median using five operations.'),([[1,2,3],3],'Moving one and three to median two costs two.')],MEDIAN_CASES,MEDIAN,[MEDIAN.replace("median*left_count-left_sum+(total-left_sum)-median*(k-left_count)","median*left_count-left_sum"),MEDIAN.replace('if right>=k-1:','if right==k-1:')],['Counts changes only on the lower half of each window.','Evaluates only the first window and ignores later candidates.'],median_oracle,random_median,lesson('The median minimizes total absolute distance within a window.','Maintain window counts and sums over compressed values with Fenwick trees.','Insert and remove endpoints, select the median by cumulative count, and compute lower/upper distance from prefix sums.','Fenwick aggregates produce the exact L1 cost in logarithmic time for every sliding window.'),'O(n log n)','O(n)',6),
3424:entry('minimum_identical_array_cost',[('arr','list[int]'),('brr','list[int]'),('k','int')],'int',['arrays','sorting','greedy'],['arr and brr have equal length up to 100,000; k is nonnegative.','Without rearranging, changing arr[i] to brr[i] costs their absolute difference.','Alternatively pay k once to reorder arbitrary contiguous pieces, which permits any permutation; return the cheaper total.'],[([[-7,9,5],[7,-2,-5],2],'Sorted matching plus the rearrangement fee costs thirteen, less than keeping positions.'),([[1,2],[2,1],1],'Pay one to swap singleton pieces, requiring no value changes.')],ARRAY_CASES,ARRAYS,[ARRAYS.replace('return min(direct,reordered)','return reordered'),ARRAYS.replace('return min(direct,reordered)','return direct')],['Always pays the rearrangement fee even when positional edits are cheaper.','Never considers rearranging pieces.'],arrays_oracle,random_arrays,lesson('Paying the rearrangement fee allows every element to be matched to any target position.','Compare direct positional cost with sorted-to-sorted minimum absolute matching plus k.','Compute both totals and return their minimum.','For absolute distance on a line, uncrossing any inverted pair never increases cost, proving sorted matching is optimal.'),'O(n log n)','O(n)',5),
3425:entry('longest_unique_downward_tree_path',[('edges','list[list[int]]'),('nums','list[int]')],'list[int]',['trees','depth-first search','sliding window'],['edges describes a rooted-at-zero weighted tree with up to 50,000 nodes and positive weights.','A special path travels downward from an ancestor to a descendant and contains unique node values.','Return [maximum edge-length sum, minimum node count among paths with that length].'],[([[[0,1,2],[1,2,3],[1,3,5],[1,4,4],[2,5,6]],[2,1,2,1,3,1]],'The best unique downward path has weight six and, among ties, two nodes.'),([[[0,1,5]],[1,1]],'Repeated values prevent using both nodes; the best length is zero with one node.')],PATH_CASES,PATH,[PATH.replace('new_left=max(left,previous+1)','new_left=left'),PATH.replace('nodes=depth-new_left+1','nodes=depth-new_left')],['Never advances past a repeated value and accepts non-unique paths.','Reports edge count rather than node count for tie-breaking.'],path_oracle,random_path,lesson('Along one root-to-node path, the valid ancestor range is a sliding window of unique values.','Track each value’s latest depth and prefix distance while depth-first traversal backtracks state.','Advance the left depth past repeats; measure distance to the current node and restore last positions on exit.','The window is the longest unique suffix ending at each node, and every downward ancestor path appears as such a suffix candidate.'),'O(n)','O(n)',8),
}
