"""Garden intervals, reversal gain, job partitions, subtree products, and bounded jumps."""
from itertools import combinations

from .import_batch_055 import entry


def taps_oracle(args):
    length,ranges=args;intervals=[(max(0,i-radius),min(length,i+radius)) for i,radius in enumerate(ranges)]
    for count in range(len(intervals)+1):
        for chosen in combinations(intervals,count):
            end=0
            for left,right in sorted(chosen):
                if left>end:break
                end=max(end,right)
            else:
                if end>=length:return count
    return -1
def random_taps(rng):
    length=rng.randint(1,8);return [length,[rng.randint(0,length) for _ in range(length+1)]]


def reversal_oracle(args):
    nums=args[0];best=0
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            candidate=nums[:left]+list(reversed(nums[left:right+1]))+nums[right+1:]
            best=max(best,sum(abs(a-b) for a,b in zip(candidate,candidate[1:])))
    return best
def random_reversal(rng):return [[rng.randint(-15,15) for _ in range(rng.randint(2,9))]]


def jobs_oracle(args):
    jobs,days=args
    if days>len(jobs):return -1
    return min(sum(max(jobs[a:b]) for a,b in zip((0,)+cuts,cuts+(len(jobs),)))
               for cuts in combinations(range(1,len(jobs)),days-1))
def random_jobs(rng):
    size=rng.randint(1,10);return [[rng.randint(0,20) for _ in range(size)],rng.randint(1,size+2)]


class Node:
    def __init__(self,value):self.val=value;self.left=self.right=None
def make_tree(values):
    root=Node(values[0]);queue=[root];index=1
    while queue and index<len(values):
        node=queue.pop(0)
        if index<len(values) and values[index] is not None:node.left=Node(values[index]);queue.append(node.left)
        index+=1
        if index<len(values) and values[index] is not None:node.right=Node(values[index]);queue.append(node.right)
        index+=1
    return root
def product_oracle(args):
    root=make_tree(args[0]);sums=[]
    def total(node):
        if node is None:return 0
        value=node.val+total(node.left)+total(node.right);sums.append(value);return value
    whole=total(root);return max(value*(whole-value) for value in sums[:-1])%(10**9+7)
def random_product(rng):
    count=rng.randint(2,15);values=[rng.randint(1,20)];frontier=1;nodes=1
    while frontier and nodes<count:
        frontier-=1
        for _ in range(2):
            if nodes<count and (rng.random()<.75 or frontier==0):values.append(rng.randint(1,20));frontier+=1;nodes+=1
            else:values.append(None)
    while values[-1] is None:values.pop()
    return [values]


def jumps_oracle(args):
    values,distance=args;answer=1
    for start in range(len(values)):
        stack=[(start,1)]
        while stack:
            index,length=stack.pop();answer=max(answer,length)
            for step in (-1,1):
                for gap in range(1,distance+1):
                    target=index+step*gap
                    if not 0<=target<len(values) or values[target]>=values[index]:break
                    stack.append((target,length+1))
    return answer
def random_jumps(rng):
    size=rng.randint(1,9);return [[rng.randint(1,20) for _ in range(size)],rng.randint(1,size)]


TAPS='''def minimum_garden_taps(n,ranges):
    farthest=[0]*(n+1)
    for center,radius in enumerate(ranges):
        left=max(0,center-radius);farthest[left]=max(farthest[left],min(n,center+radius))
    taps=0;current=next_end=0
    for point in range(n):
        next_end=max(next_end,farthest[point])
        if next_end<=point:return -1
        if point==current:taps+=1;current=next_end
    return taps
'''
REVERSE='''def maximum_value_after_reverse(nums):
    base=sum(abs(a-b) for a,b in zip(nums,nums[1:]));gain=0
    for left,right in zip(nums,nums[1:]):
        gain=max(gain,abs(nums[0]-right)-abs(left-right),abs(nums[-1]-left)-abs(left-right))
    highest_low=max(min(left,right) for left,right in zip(nums,nums[1:]));lowest_high=min(max(left,right) for left,right in zip(nums,nums[1:]))
    gain=max(gain,2*(highest_low-lowest_high))
    return base+gain
'''
JOBS='''def minimum_job_schedule_difficulty(jobDifficulty,d):
    size=len(jobDifficulty)
    if d>size:return -1
    previous=[10**18]*(size+1);previous[0]=0
    for day in range(1,d+1):
        current=[10**18]*(size+1)
        for end in range(day,size+1):
            hardest=0
            for start in range(end,day-1,-1):
                hardest=max(hardest,jobDifficulty[start-1]);current[end]=min(current[end],previous[start-1]+hardest)
        previous=current
    return previous[size]
'''
PRODUCT='''def maximum_split_tree_product(root):
    sums=[]
    def total(node):
        if node is None:return 0
        value=node.val+total(node.left)+total(node.right);sums.append(value);return value
    whole=total(root)
    return max(value*(whole-value) for value in sums[:-1])%(10**9+7)
'''
JUMPS='''def maximum_decreasing_jumps(arr,d):
    from functools import lru_cache
    @lru_cache(None)
    def visit(index):
        answer=1
        for step in (-1,1):
            for gap in range(1,d+1):
                target=index+step*gap
                if not 0<=target<len(arr) or arr[target]>=arr[index]:break
                answer=max(answer,1+visit(target))
        return answer
    return max(visit(index) for index in range(len(arr)))
'''

BATCH={
1326:entry('minimum_garden_taps',[('n','int'),('ranges','list[int]')],'int',['greedy','intervals'],['The garden is the continuous segment from zero through n.','Tap i waters [i-ranges[i], i+ranges[i]], clipped to the garden.','Return the fewest taps covering every point, or -1 if a gap cannot be covered.'],[([5,[3,4,1,1,0,0]],'The tap at position one alone covers the entire garden.'),([3,[0,0,0,0]],'No tap reaches beyond its own point, leaving every open interval dry.')],[[n,r] for n,r in ((1,[0,0]),(1,[1,0]),(2,[0,1,0]),(2,[1,0,1]),(3,[0,0,0,0]),(3,[1,1,1,1]),(4,[1,0,0,0,1]),(5,[3,4,1,1,0,0]),(5,[0,0,2,0,0,0]),(6,[1,2,0,1,0,2,0]),(7,[0,2,0,0,0,0,2,0]),(8,[4,0,0,0,0,0,0,0,4]),(4,[0,2,0,0,0]),(6,[0,1,2,0,1,0,1]))],TAPS,[TAPS.replace('left=max(0,center-radius)','left=center'),TAPS.replace('return taps','return taps-1')],['Treats every tap as if it cannot water left of its own position.','Under-counts the selected interval that reaches the garden end.'],taps_oracle,random_taps,['Convert taps into intervals grouped by their left endpoint.','Scan like minimum jumps, tracking the farthest point reachable by one more selected interval.','When the current chosen coverage ends, commit the interval reaching farthest; fail if it does not advance.','The exchange rule can replace any next interval by the farthest-reaching available interval without using more taps.'],'Compress all intervals starting at the same left position to their farthest right endpoint. A frontier scan greedily commits only when current coverage expires, choosing the farthest endpoint seen so far. This is the standard minimum interval-cover exchange argument. The independent oracle enumerates tap subsets on seeded small gardens and checks their sorted union.','O(n)','O(n)',8),
1330:entry('maximum_value_after_reverse',[('nums','list[int]')],'int',['arrays','greedy','math'],['nums has at least two integers.','Reverse one contiguous subarray; a length-one reversal is allowed.','Maximize the sum of absolute differences between adjacent values.'],[([[2,3,1,5,4]],'Reversing the middle segment can raise the adjacent-difference total to ten.'),([[2,4,9,24,2,1,10]],'The best reversal produces a total value of sixty-eight.')],[[x] for x in ([1,2],[2,1],[1,1],[1,3,2],[2,3,1,5,4],[2,4,9,24,2,1,10],[1,5,1],[0,-5,10],[-1,-2,-3,-4],[5,1,9,2],[3,3,1,3],[10,0,0,10],[4,7,2,9,1],[-10,10,-10,10])],REVERSE,[REVERSE.replace('gain=max(gain,2*(highest_low-lowest_high))','gain=gain'),REVERSE.replace('abs(nums[0]-right)','abs(nums[0]-left)')],['Considers only prefix and suffix reversals, missing profitable internal reversals.','Uses the old boundary endpoint when evaluating prefix reversals.'],reversal_oracle,random_reversal,['Only the edges crossing a reversed segment can change the total.','Handle prefix and suffix reversals by testing every original adjacent pair as the cut boundary.','For an internal reversal, the best gain is twice max(min endpoints) minus min(max endpoints).','Every reversal is prefix, suffix, or internal, and the formula captures exactly its two changed boundary edges.'],'The base adjacent-difference sum is unchanged inside a reversed segment. Prefix and suffix cases replace one boundary. For internal segments, algebra on the two boundary pairs reduces the maximum gain to twice the gap between the greatest lower endpoint and smallest upper endpoint. The oracle directly reverses every subarray on seeded small inputs.','O(n)','O(1)',8),
1335:entry('minimum_job_schedule_difficulty',[('jobDifficulty','list[int]'),('d','int')],'int',['arrays','dynamic programming'],['Jobs must be completed in the given order over exactly d days.','Every day receives at least one consecutive block; its difficulty is the maximum job in that block.','Return the minimum sum of daily difficulties, or -1 when there are fewer jobs than days.'],[([[6,5,4,3,2,1],2],'Putting the first five jobs on day one and the last job on day two costs six plus one.'),([[9,9,9],4],'Three jobs cannot fill four nonempty days.')],[[jobs,d] for jobs,d in (([1],1),([1],2),([6,5,4,3,2,1],2),([9,9,9],4),([1,1,1],3),([7,1,7,1,7,1],3),([11,111,22,222,33,333,44,444],6),([1,2,3,4],2),([4,3,2,1],3),([0,0,0],2),([5,1,5],1),([5,1,5],2),([8,2,6,4],4),([3,9,2,7,1],3))],JOBS,[JOBS.replace('hardest=max(hardest,jobDifficulty[start-1])','hardest=min(hardest,jobDifficulty[start-1])'),JOBS.replace('previous[0]=0','previous=[0]*(size+1)')],['Uses the easiest rather than hardest job as each day’s difficulty.','Initializes impossible zero-day prefixes as feasible, allowing empty early days.'],jobs_oracle,random_jobs,['Partition an ordered prefix into completed days.','For each final day endpoint, scan its possible start backward while maintaining that day’s maximum.', 'Add the previous-day optimum before the chosen start and minimize.','Every exact-day schedule has one final block, so testing all starts is exhaustive and subproblems are independent.'],'Dynamic programming stores the minimum difficulty for scheduling each prefix in an exact number of days. Scanning a final block backward updates its maximum in constant time per candidate. Impossible states remain infinite, which enforces nonempty days. The oracle independently enumerates all combinations of day-boundary cuts.','O(d*n^2)','O(n)',8),
1339:entry('maximum_split_tree_product',[('root','TreeNode')],'int',['trees','recursion','postorder'],['root contains at least two positive-valued nodes.','Remove exactly one edge, multiply the sums of the two resulting components, and maximize before applying modulo 1000000007.','Return that maximum product modulo 1000000007.'],[([[1,2,3,4,5,6]],'A best edge split produces component sums eleven and ten, whose product is one hundred ten.'),([[1,1]],'The only edge creates two unit-sum components, giving one.')],[[tree] for tree in ([1,1],[1,2],[1,2,3],[1,2,3,4,5,6],[2,3,9,10,7,8,6,5,4,11,1],[5,5,5],[10,1,None,1,None,1],[1,None,2,None,3],[4,2,6,1,3,5,7],[10000,10000],[3,1,4,None,2],[8,4,12,2,6,10,14],[1,1,1,1,1,1,1],[9,2,7,1,None,5,8])],PRODUCT,[PRODUCT.replace('value*(whole-value)','value*value'),PRODUCT.replace('sums[:-1]','sums[:1]')],['Squares one component sum instead of multiplying both resulting component sums.','Evaluates only the first postorder subtree rather than every removable edge.'],product_oracle,random_product,['Compute every subtree sum with postorder recursion.','After finding the total, each nonroot subtree defines one edge split with product sub*(total-sub).','Maximize the unmodded products and apply the modulus only once afterward.','Every removable parent edge corresponds uniquely to its child subtree sum, so all and only valid splits are tested.'],'One postorder traversal records every subtree sum and the root total. Removing the edge above any nonroot subtree yields exactly that sum and its complement, so maximize their product. Delaying the modulus preserves ordering. The oracle builds a separate tree and independently records component sums.','O(n)','O(n)',5),
1340:entry('maximum_decreasing_jumps',[('arr','list[int]'),('d','int')],'int',['arrays','recursion','dynamic programming'],['Start at any index and jump left or right by at most d positions.','A destination must be strictly lower than the current value, and every crossed position must also be lower than the current value.','Return the maximum number of visited indices including the start.'],[([[6,4,14,6,8,13,9,7,10,6,12],2],'An optimal decreasing jump sequence visits four indices.'),([[3,3,3,3,3],3],'Equal values block every jump, so any path visits only its start.')],[[arr,d] for arr,d in (([1],1),([1,2],1),([2,1],1),([3,3,3,3,3],3),([6,4,14,6,8,13,9,7,10,6,12],2),([7,6,5,4,3,2,1],3),([1,2,3,4,5],2),([7,1,7,1,7,1],2),([10,1,2,3],3),([4,3,2,1],1),([5,1,4,2,3],2),([9,8,1,7,6],4),([2,1,2,1,2],2),([100,1,99,2,98,3],3))],JUMPS,[JUMPS.replace('arr[target]>=arr[index]:break','arr[target]>=arr[index]:continue'),JUMPS.replace('for step in (-1,1)','for step in (1,)')],['Jumps over an equal-or-taller blocker to reach forbidden positions beyond it.','Searches only rightward jumps and misses paths requiring left moves.'],jumps_oracle,random_jumps,['Each valid jump strictly decreases value, so the state graph has no cycle.','Memoize the best path length starting at each index.','Scan outward in both directions up to d, stopping that direction at the first equal-or-higher blocker.','The recurrence tries every legal next index; strict decrease makes cached recursion well-founded.'],'Memoized depth-first search returns the longest decreasing path beginning at one index. In each direction, scan only until the distance limit or the first blocking value; positions beyond a blocker are illegal even if lower. Maximize over all starts. The oracle independently enumerates every legal path without memoization on seeded small arrays.','O(n*d)','O(n)',8),
}
BATCH[1339]['params'][0]=('root','TreeNode','treenode')
