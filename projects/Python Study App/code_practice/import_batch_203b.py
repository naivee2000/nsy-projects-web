"""Reverse arithmetic, sequence DP, subset search, tree pruning, and transit BFS."""
from itertools import combinations
from .import_batch_055 import entry

def reach_o(a):
    sx,sy,tx,ty=a;seen={(sx,sy)};todo=[(sx,sy)]
    while todo:
        x,y=todo.pop(0)
        if (x,y)==(tx,ty):return True
        for nxt in ((x+y,y),(x,x+y)):
            if nxt[0]<=tx and nxt[1]<=ty and nxt not in seen:seen.add(nxt);todo.append(nxt)
    return False
def rreach(r):
    sx,sy=r.randint(1,5),r.randint(1,5);return [sx,sy,r.randint(sx,30),r.randint(sy,30)]

def swaps_o(a):
    first,second=a;n=len(first);best=n+1
    for mask in range(1<<n):
        x=first[:];y=second[:]
        for i in range(n):
            if mask>>i&1:x[i],y[i]=y[i],x[i]
        if all(x[i]>x[i-1] and y[i]>y[i-1] for i in range(1,n)):best=min(best,mask.bit_count())
    return best
def rswaps(r):
    n=r.randint(1,8);a=[];b=[];x=y=0
    for _ in range(n):x+=r.randint(1,5);y+=r.randint(1,5);a.append(x);b.append(y)
    for i in range(n):
        if r.random()<.4:a[i],b[i]=b[i],a[i]
    return [a,b]

def average_o(a):
    nums=a[0];total=sum(nums);n=len(nums)
    return any(sum(choice)*n==total*size for size in range(1,n//2+1) for choice in combinations(nums,size))
def raverage(r):return [[r.randint(0,15) for _ in range(r.randint(2,10))]]

def _tree(values):
    if not values:return None
    root=[values[0],None,None];queue=[root];i=1
    while queue and i<len(values):
        node=queue.pop(0)
        for child in (1,2):
            if i<len(values) and values[i] is not None:node[child]=[values[i],None,None];queue.append(node[child])
            i+=1
    return root
def _values(root):
    if root is None:return []
    out=[];queue=[root]
    while queue:
        node=queue.pop(0)
        if node is None:out.append(None)
        else:out.append(node[0]);queue.extend(node[1:])
    while out and out[-1] is None:out.pop()
    return out
def prune_o(a):
    root=_tree(a[0])
    def keep(node):
        if node is None:return None
        node[1]=keep(node[1]);node[2]=keep(node[2])
        return node if node[0] or node[1] or node[2] else None
    return _values(keep(root))
def rprune(r):
    values=[r.randint(0,1)]
    for _ in range(r.randint(0,20)):values.append(None if r.random()<.25 else r.randint(0,1))
    while values and values[-1] is None:values.pop()
    return [values or [0]]

def buses_o(a):
    routes,source,target=a
    if source==target:return 0
    containing={}
    for i,route in enumerate(routes):
        for stop in route:containing.setdefault(stop,[]).append(i)
    starts=containing.get(source,[]);goals=set(containing.get(target,[]));seen=set(starts);todo=[(route,1) for route in starts]
    while todo:
        route,distance=todo.pop(0)
        if route in goals:return distance
        for stop in routes[route]:
            for nxt in containing.get(stop,[]):
                if nxt not in seen:seen.add(nxt);todo.append((nxt,distance+1))
    return -1
def rbuses(r):
    stops=list(range(r.randint(3,15)));routes=[]
    for _ in range(r.randint(1,8)):routes.append(r.sample(stops,r.randint(1,min(6,len(stops)))))
    return [routes,r.choice(stops),r.choice(stops)]

REACH='''def can_reach_point(sx,sy,tx,ty):
    while tx>sx and ty>sy:
        if tx>ty:tx%=ty
        else:ty%=tx
    return (tx==sx and ty>=sy and (ty-sy)%sx==0) or (ty==sy and tx>=sx and (tx-sx)%sy==0)
'''
SWAPS='''def minimum_sequence_swaps(nums1,nums2):
    keep,swap=0,1
    for i in range(1,len(nums1)):
        next_keep=next_swap=float('inf')
        if nums1[i]>nums1[i-1] and nums2[i]>nums2[i-1]:next_keep=keep;next_swap=swap+1
        if nums1[i]>nums2[i-1] and nums2[i]>nums1[i-1]:next_keep=min(next_keep,swap);next_swap=min(next_swap,keep+1)
        keep,swap=next_keep,next_swap
    return min(keep,swap)
'''
AVERAGE='''def can_split_same_average(nums):
    n=len(nums);total=sum(nums);possible=[set() for _ in range(n//2+1)];possible[0].add(0)
    for value in nums:
        for size in range(n//2,0,-1):
            possible[size].update(previous+value for previous in possible[size-1])
    return any(total*size%n==0 and total*size//n in possible[size] for size in range(1,n//2+1))
'''
PRUNE='''def prune_zero_subtrees(root):
    if root is None:return None
    root.left=prune_zero_subtrees(root.left);root.right=prune_zero_subtrees(root.right)
    if root.val==0 and root.left is None and root.right is None:return None
    return root
'''
BUSES='''def minimum_buses(routes,source,target):
    if source==target:return 0
    stops={}
    for route,line in enumerate(routes):
        for stop in line:stops.setdefault(stop,[]).append(route)
    queue=[(source,0)];seen_stops={source};seen_routes=set()
    for stop,count in queue:
        for route in stops.get(stop,[]):
            if route in seen_routes:continue
            seen_routes.add(route)
            for nxt in routes[route]:
                if nxt==target:return count+1
                if nxt not in seen_stops:seen_stops.add(nxt);queue.append((nxt,count+1))
    return -1
'''

BATCH={
780:entry('can_reach_point',[('sx','int'),('sy','int'),('tx','int'),('ty','int')],'bool',['math','reverse simulation'],['Start with positive coordinates sx, sy.','One move changes (x,y) to (x+y,y) or (x,x+y).','Return whether target tx, ty is reachable.'],[([1,1,3,5],'Reversing five modulo three reaches the starting pair.'),([1,1,2,2],'Neither forward addition can create equal coordinates two,two.')],[[*x] for x in [(1,1,1,1),(1,1,3,5),(1,1,2,2),(1,2,3,2),(1,2,5,2),(2,3,2,9),(3,5,8,5),(2,4,6,4),(4,7,11,18),(2,2,4,2),(5,3,5,18),(3,7,24,7),(2,5,19,12),(4,6,10,16)]],REACH,[REACH.replace('tx%=ty','tx-=ty'),REACH.replace('(ty-sy)%sx==0','(ty-sy)%sx==1')],['Subtracts only once instead of reversing all repeated additions.','Uses the wrong divisibility remainder when one coordinate reaches its start.'],reach_o,rreach,['Reverse additions from the larger target coordinate.','Modulo removes as many repeated additions of the smaller coordinate as possible.','When one coordinate reaches its start, check whether the other differs by a nonnegative multiple.','Forward moves strictly increase one coordinate, so the reverse choice is forced until a starting coordinate is reached.'],'O(log(max target))','O(1)',8),
801:entry('minimum_sequence_swaps',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','dynamic programming'],['Arrays have equal positive length and some swap set makes both strictly increasing.','At index i, swapping exchanges nums1[i] and nums2[i].','Return the minimum number of indices to swap.'],[([[1,3,5,4],[1,2,3,7]],'Swapping the final pair makes both arrays strictly increasing.'),([[0,3,5,8,9],[2,1,4,6,9]],'Swapping at index one is sufficient.')],[[a,b] for a,b in [([1],[2]),([1,3,5,4],[1,2,3,7]),([0,3,5,8,9],[2,1,4,6,9]),([1,2],[2,3]),([1,5,3],[1,2,7]),([3,3,8,9,10],[1,7,4,6,8]),([1,4,6],[2,3,7]),([0,4,4,5,9],[0,1,6,8,10]),([1,2,7,8],[3,4,5,9]),([1,10],[2,9]),([0,2,5],[1,3,6]),([2,6,7,10],[1,4,8,9]),([1,7,8],[2,3,9]),([0,5,6,9],[1,2,7,8])]],SWAPS,[SWAPS.replace('keep,swap=0,1','keep,swap=1,0'),SWAPS.replace('min(keep,swap)','max(keep,swap)')],['Charges a swap for keeping index zero and none for swapping it.','Returns the more expensive final state.'],swaps_o,rswaps,['Track minimum costs ending with the current index kept or swapped.','Same-orientation inequalities extend like states; cross inequalities transition between states.','Compute both next costs from the previous pair.','Every solution has exactly one of two orientations at each index, and the valid transitions enumerate all possibilities.'],'O(n)','O(1)',5),
805:entry('can_split_same_average',[('nums','list[int]')],'bool',['arrays','dynamic programming'],['nums contains at least two nonnegative integers.','Split it into two nonempty groups whose averages are equal.','Return whether such a split exists.'],[([[1,2,3,4,5,6,7,8]],'The values can be divided into groups with common average four and one half.'),([[3,1]],'Two unequal singleton groups cannot have the same average.')],[[x] for x in [[1,2],[1,1],[3,1],[1,2,3,4,5,6,7,8],[0,0],[0,1,2],[2,4,6,8],[5,3,11,19,2],[1,2,5],[6,8,10,12,14],[1,7,15,29],[3,3,3,4],[0,2,3,5],[10,1,2,7]]],AVERAGE,[AVERAGE.replace('range(n//2,0,-1)','range(1,n//2+1)'),AVERAGE.replace('range(1,n//2+1)','range(1,n//2)')],['Updates subset sizes upward and reuses the same value more than once.','Never considers a subset of size exactly half the array.'],average_o,raverage,['A subset of size k must have sum total*k/n.','Build reachable sums by subset size, updating sizes downward for each value.','Check sizes one through half only.','Downward updates use each input once, and any valid larger group has a complementary valid group no larger than half.'],'O(n^2*sum(nums))','O(n*sum(nums))',8),
814:entry('prune_zero_subtrees',[('root','TreeNode | None')],'TreeNode | None',['trees','recursion'],['Every node value is zero or one.','Remove every subtree that contains no value one.','Return the remaining root, or None if the entire tree is removed.'],[([[1,None,0,0,1]],'The zero leaf is removed while the branch containing one remains.'),([[0,0,0]],'No subtree contains one, so the whole tree is removed.')],[[t] for t in [[],[0],[1],[1,None,0,0,1],[0,0,0],[1,0,1,0,0,0,1],[1,0,None,1],[0,1],[1,None,0,None,1],[1,1,0],[0,None,1],[1,0,0,0,1],[0,0,1,0,0],[1,0,1,None,None,0,0]]],PRUNE,[PRUNE.replace('root.val==0','root.val==1'),PRUNE.replace('and root.right is None','or root.right is None')],['Prunes leaf nodes containing one instead of zero.','Prunes a zero node when either child is missing even if the other contains one.'],prune_o,rprune,['Process children before deciding about their parent.','After pruning both children, a zero node with no children contains no one and should disappear.','Return every other node.','Postorder ensures remaining children represent exactly the subtrees that contain a one.'],'O(n)','O(height)',5),
815:entry('minimum_buses',[('routes','list[list[int]]'),('source','int'),('target','int')],'int',['graphs','breadth-first search'],['Each route repeats indefinitely and contains distinct stop numbers.','You may board any route containing your current stop and transfer at shared stops.','Return the minimum buses needed from source to target, or -1.'],[([[[1,2,7],[3,6,7]],1,6],'Ride the first route to seven and transfer to the second route.'),([[[7,12],[4,5,15],[6],[15,19],[9,12,13]],15,12],'No sequence of shared stops connects the source and target routes.')],[[r,s,t] for r,s,t in [([[1]],1,1),([[1,2]],1,2),([[1,2,7],[3,6,7]],1,6),([[1,2],[3,4]],1,4),([[1,2],[2,3],[3,4]],1,4),([[7,12],[4,5,15],[6],[15,19],[9,12,13]],15,12),([[1,5,7],[2,3,5],[3,9]],1,9),([[0,1,2]],2,0),([[1,2],[2,1]],1,2),([[10,20],[20,30],[30,40]],10,40),([[1,3,5],[2,4,6]],3,6),([[1,2,3],[3,4],[4,5]],2,5),([[5],[5,6],[6,7]],5,7),([[1,9],[9,8],[8,7],[7,6]],1,6)]],BUSES,[BUSES.replace('return count+1','return count'),BUSES.replace('seen_routes.add(route)','seen_stops.add(route)')],['Does not count the bus that first reaches the target.','Stores route indices in the stop-visited set and repeatedly reboards routes.'],buses_o,rbuses,['Index routes by every stop they serve.','Breadth-first search reachable stops while boarding each route at most once.','Boarding a new route advances the bus count once and exposes all its stops.','BFS layers count buses, and marking routes prevents redundant scans without removing any transfer path.'],'O(total route entries)','O(total route entries)',8),
}
BATCH[814]['params'][0]=('root','TreeNode | None','treenode');BATCH[814]['adapter']='treenode'
BATCH[780]['wrong'][0]=REACH.replace('tx%=ty','tx%=sx')
BATCH[780]['wrong_reasons'][0]='Reduces the larger target coordinate by the starting x coordinate instead of the other current coordinate.'
BATCH[805]['wrong'][0]=AVERAGE.replace('total*size%n==0','total*size%n==1')
BATCH[805]['wrong_reasons'][0]='Requires an impossible remainder of one instead of divisibility by the array length.'
BATCH[815]['wrong'][1]=BUSES.replace('if route in seen_routes:continue','if True:continue')
BATCH[815]['wrong_reasons'][1]='Skips every available route before exposing any of its stops.'
