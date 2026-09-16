"""Coordinate activation, peak windows, parity construction, XOR removal, and OR subarrays."""
from itertools import combinations,product
from .import_batch_055 import entry


def activated_count(points,new):
    values=points+[new];seen={len(values)-1};stack=[len(values)-1]
    while stack:
        i=stack.pop()
        for j in range(len(values)):
            if j not in seen and (values[i][0]==values[j][0] or values[i][1]==values[j][1]):seen.add(j);stack.append(j)
    return len(seen)
def activated_oracle(args):
    points=args[0];xs={x for x,_ in points}|{10**9+1};ys={y for _,y in points}|{10**9+1}
    return max(activated_count(points,[x,y]) for x in xs for y in ys if [x,y] not in points)
def random_activated(rng):
    cells=rng.sample([(x,y) for x in range(6) for y in range(6)],rng.randint(1,14));return [[list(cell) for cell in cells]]

def peaks_oracle(args):
    nums,k=args;peaks=[i for i in range(1,len(nums)-1) if nums[i]>nums[i-1] and nums[i]>nums[i+1]];answer=0
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            inside=[p for p in peaks if left<=p<=right]
            answer+=len(inside)==1 and inside[0]-left<=k and right-inside[0]<=k
    return answer
def random_peaks(rng):return [[rng.randint(-20,20) for _ in range(rng.randint(1,25))],rng.randint(0,8)]

def uniform_oracle(args):
    nums=args[0];possible=[]
    for i,value in enumerate(nums):
        choices={value%2}
        for j,other in enumerate(nums):
            if i!=j and value-other>=1:choices.add((value-other)%2)
        possible.append(choices)
    return all(0 in choices for choices in possible) or all(1 in choices for choices in possible)
def random_uniform(rng):return [rng.sample(range(1,60),rng.randint(1,12))]

def removals_oracle(args):
    nums,target=args;best=-1
    for mask in range(1<<len(nums)):
        value=0;kept=0
        for i,item in enumerate(nums):
            if mask>>i&1:value^=item;kept+=1
        if value==target:best=max(best,kept)
    return -1 if best<0 else len(nums)-best
def random_removals(rng):return [[rng.randint(0,31) for _ in range(rng.randint(1,14))],rng.randint(0,63)]

def good_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        value=0
        for right in range(left,len(nums)):
            value|=nums[right];answer+=value in nums[left:right+1]
    return answer
def random_good(rng):return [[rng.randint(0,63) for _ in range(rng.randint(1,30))]]

ACTIVATED='''def maximum_activated_points(points):
    parent={};size={}
    def find(item):
        if item not in parent:parent[item]=item;size[item]=0
        if parent[item]!=item:parent[item]=find(parent[item])
        return parent[item]
    def union(a,b):
        a=find(a);b=find(b)
        if a==b:return
        if size[a]<size[b]:a,b=b,a
        parent[b]=a;size[a]+=size[b]
    offset=3_000_000_001
    for x,y in points:
        union(x,y+offset);size[find(x)]+=1
    components={}
    for x,_ in points:components[find(x)]=size[find(x)]
    largest=sorted(components.values(),reverse=True)
    return 1+sum(largest[:2])
'''

PEAKS='''def count_single_peak_subarrays(nums,k):
    peaks=[i for i in range(1,len(nums)-1) if nums[i]>nums[i-1] and nums[i]>nums[i+1]];answer=0
    for index,peak in enumerate(peaks):
        left=max(0,peak-k,peaks[index-1]+1 if index else 0)
        right=min(len(nums)-1,peak+k,peaks[index+1]-1 if index+1<len(peaks) else len(nums)-1)
        answer+=(peak-left+1)*(right-peak+1)
    return answer
'''

UNIFORM='''def can_construct_uniform_parity(nums):
    smallest_odd=min((value for value in nums if value%2),default=None)
    return smallest_odd is None or all(value>=smallest_odd for value in nums if value%2==0)
'''

REMOVALS='''def minimum_xor_removals(nums,target):
    states={0:0}
    for value in nums:
        updated=states.copy()
        for xor,count in states.items():updated[xor^value]=max(updated.get(xor^value,-1),count+1)
        states=updated
    return -1 if target not in states else len(nums)-states[target]
'''

GOOD='''def count_or_element_subarrays(nums):
    n=len(nums);left=[-1]*n;stack=[]
    for i,value in enumerate(nums):
        while stack and nums[stack[-1]]<value and nums[stack[-1]]|value==value:stack.pop()
        left[i]=stack[-1] if stack else -1;stack.append(i)
    right=[n]*n;stack=[]
    for i in range(n-1,-1,-1):
        while stack and nums[stack[-1]]|nums[i]==nums[i]:stack.pop()
        right[i]=stack[-1] if stack else n;stack.append(i)
    return sum((i-left[i])*(right[i]-i) for i in range(n))
'''

def lesson(a,b,c,d):return [a,b,c,d]
C_CASES=[[[list(p) for p in points]] for points in (((1,1),(1,2),(2,2)),((0,0),),((0,0),(1,1)),((0,0),(0,1)),((0,0),(1,0)),((0,0),(0,1),(5,5)),((1,1),(1,2),(3,3),(3,4)),((1,1),(2,1),(3,2),(4,2)),((0,0),(0,1),(1,1),(5,5)),((1,2),(3,2),(3,4),(5,6)),((0,0),(1,0),(1,1),(2,1)),((2,3),(2,4),(5,4),(8,9)),((1,1),(2,2),(3,3),(4,4)),((0,1),(0,2),(3,2),(3,4),(8,8)),((1,5),(2,5),(2,6),(7,8),(7,9)))]
P_CASES=[[a,k] for a,k in (([1,3,2],1),([1],1),([1,2],2),([1,2,1],0),([1,2,1],1),([1,3,2,4,1],2),([3,2,1],3),([1,3,1,3,1],1),([1,4,2,3,1],2),([0,5,0,4,0],4),([1,2,3,2,1],1),([5,1,5,1,5],2),([1,10,9,8,7],3),([2,1,2,3,2],1),([1,3,2,1,2,1],2))]
U_CASES=[[[*v]] for v in ([1,4,7],[2],[1],[2,4],[1,3],[1,2],[3,2],[5,2,8],[7,4,10],[9,2,6],[2,5,8],[11,3,4],[6,8,10,12],[1,6,10],[13,2,7,8])]
R_CASES=[[a,t] for a,t in (([1,2,3],2),([1],1),([1],0),([0],0),([1,1],0),([1,2],3),([1,2],4),([3,3,3],3),([1,2,4,8],15),([5,1,5],1),([0,1,2],3),([7,7,2,2],0),([10,12,6],4),([31,1,30],0),([2,4,6,8],12))]
G_CASES=[[[*v]] for v in ([4,2,3],[1],[0],[1,2],[1,3],[2,3],[1,2,3],[7,3,1],[4,4],[1,1,3],[8,4,12],[5,2,7,1],[0,1,0],[3,5,6,7],[16,8,24,4])]

BATCH={
3873:entry('maximum_activated_points',[('points','list[list[int]]')],'int',['graphs','union find','hash maps'],['points contains distinct integer coordinate pairs.','Activated points propagate through shared x or shared y coordinates.','Add one new point at an unused coordinate pair and maximize the activated count, including it.'],[([[[1,1],[1,2],[2,2]]],'The original three points are connected; the new point can join them and is also counted, giving four.'),([[[0,0],[1,1]]],'Place the new point at (0,1) to connect both isolated points, activating all three.')],C_CASES,ACTIVATED,[ACTIVATED.replace('largest[:2]','largest[:1]'),ACTIVATED.replace('return 1+sum','return sum')],['Connects the new point to only one existing component instead of up to two.','Fails to include the newly added point in the activated total.'],activated_oracle,random_activated,lesson('Treat every x coordinate and every y coordinate as vertices of a bipartite graph; each point is an edge.','Union each point’s x vertex with its y vertex and count point-edges per connected component.','A new point can choose an x from one component and a y from another, joining the two largest components plus itself.','One new edge touches at most two components, and choosing coordinates from the two largest attains that upper bound.'),'O(n α(n))','O(n)',8),
3874:entry('count_single_peak_subarrays',[('nums','list[int]'),('k','int')],'int',['arrays','combinatorics'],['A global peak i satisfies 0<i<n-1 and nums[i] exceeds both neighbors.','A valid subarray contains exactly one such peak p, with each endpoint at distance at most k from p.','Count all valid contiguous subarrays.'],[([[1,3,2],1],'The sole peak is index one; each endpoint may be at the peak or one position away, giving four subarrays.'),([[1,2,1],0],'Only the singleton containing the peak has both endpoint distances zero.')],P_CASES,PEAKS,[PEAKS.replace('peak+k','peak+k-1'),PEAKS.replace('peaks[index+1]-1','peaks[index+1]')],['Allows only k-1 positions to the right of each peak.','Allows the next peak into the current peak’s subarrays, causing double counting and invalid windows.'],peaks_oracle,random_peaks,lesson('List global peak indices, then assign every valid subarray to its unique peak.','For peak p, its left endpoint is bounded by p-k, the array start, and one past the previous peak; the right is symmetric.','Multiply the independent numbers of left and right endpoint choices.','Neighbor-peak bounds enforce uniqueness, distance bounds enforce k, and every valid subarray is counted once at its sole peak.'),'O(n)','O(n)',6),
3876:entry('can_construct_uniform_parity',[('nums1','list[int]')],'bool',['arrays','math','parity'],['nums1 contains distinct integers.','At i, keep nums1[i] or replace it by a positive difference nums1[i]-nums1[j] for j≠i.','Return whether all resulting values can be made the same parity.'],[([[1,4,7]],'Keep the odd values and replace four by 4-1=3, producing all odd values.'),([[1,2]],'Two can become one by subtracting one, so both positions can be odd.')],U_CASES,UNIFORM,[UNIFORM.replace('smallest_odd=min','smallest_odd=max'),UNIFORM.replace('if value%2==0','if value%2==1')],['Uses the largest odd as the subtraction source, rejecting valid arrays with a smaller usable odd.','Checks odd values against the smallest odd instead of determining whether every even can become odd.'],uniform_oracle,random_uniform,lesson('An all-even result is automatic only when every original value is even; otherwise target odd parity.','Every odd value may stay unchanged. An even value can become positive odd exactly by subtracting a smaller odd value.','Find the smallest odd value and verify that every even value is larger than it.','That smallest odd supplies every needed conversion; if an even is smaller, no positive odd subtraction is available for that position.'),'O(n)','O(1)',5),
3877:entry('minimum_xor_removals',[('nums','list[int]'),('target','int')],'int',['arrays','bit manipulation','dynamic programming'],['nums is nonempty and contains nonnegative integers.','Remove any elements so the XOR of those remaining equals target; empty XOR is zero.','Return the fewest removals, or -1 if target cannot be formed.'],[([[1,2,3],2],'Keeping one and three gives XOR two, so removing only the value two is optimal.'),([[1],0],'Remove the sole element to obtain empty XOR zero, costing one removal.')],R_CASES,REMOVALS,[REMOVALS.replace('updated=states.copy()','updated={}'),REMOVALS.replace('len(nums)-states[target]','states[target]')],['Drops every skip transition, so it considers only subsets containing the latest processed element.','Returns the number kept rather than the number removed.'],removals_oracle,random_removals,lesson('Minimizing removals is equivalent to maximizing how many kept elements produce the target XOR.','Maintain a map from reachable XOR to the greatest kept count after each element.','For every state, either skip the element or keep it and transition to xor^value.','The two transitions enumerate every subset, while retaining only the greatest count is safe for all future XOR operations.'),'O(nU)','O(U)',6),
3878:entry('count_or_element_subarrays',[('nums','list[int]')],'int',['arrays','bit manipulation','monotonic stacks'],['nums is a nonempty array of nonnegative integers.','A subarray is good when its bitwise OR is equal to at least one element inside that subarray.','Count all good contiguous subarrays.'],[([[4,2,3]],'The three singletons qualify, and [2,3] has OR three equal to its final element, giving four.'),([[1,3]],'Both singletons qualify and the pair has OR three, which is present, giving three.')],G_CASES,GOOD,[GOOD.replace('(i-left[i])*(right[i]-i)','right[i]-left[i]'),GOOD.replace('nums[stack[-1]]<value and ','')],['Adds boundary spans instead of multiplying independent left and right choices.','Pops equal or larger subset values on the left, breaking the unique representative rule.'],good_oracle,random_good,lesson('For a good subarray, choose a contained element equal to its OR; every other element must have no bit outside that representative.','Use monotonic-style stacks to find how far each value can extend through bitwise subsets, with asymmetric ties so each subarray has one representative.','Multiply valid left and right endpoint choices for every index.','The boundaries exclude the first incompatible value; tie asymmetry prevents duplicate counting when multiple equal representatives occur.'),'O(n)','O(n)',8),
}
