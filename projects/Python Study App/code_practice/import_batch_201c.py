"""Prefix reversals, monster strength, shift processing, drones, and GCD splits."""
from collections import deque
from math import gcd
from .import_batch_055 import entry

def pancake_oracle(a):
    nums,pre=a;target=tuple(range(len(nums)));start=tuple(nums);distance={start:0};q=deque([start])
    while q:
        state=q.popleft()
        if state==target:return distance[state]
        for length in pre:
            nxt=tuple(reversed(state[:length]))+state[length:]
            if nxt not in distance:distance[nxt]=distance[state]+1;q.append(nxt)
    return -1
def random_pancake(r):
    n=r.randint(1,7);nums=list(range(n));r.shuffle(nums);return [nums,r.sample(range(1,n+1),r.randint(1,n))]
def strength_oracle(a):
    monsters,boosts=a;bonus=[0]*len(monsters)
    for left,right,value in boosts:
        for i in range(left,right+1):bonus[i]+=value
    def wins(initial):
        current=initial
        for need,extra in zip(monsters,bonus):
            if current+extra<need:return False
            current=max(0,current-need)
        return True
    return next(initial for initial in range(sum(monsters)+1) if wins(initial))
def random_strength(r):
    n=r.randint(1,10);boosts=[]
    for _ in range(r.randint(0,8)):
        left=r.randrange(n);boosts.append([left,r.randint(left,n-1),r.randint(0,20)])
    return [[r.randint(1,30) for _ in range(n)],boosts]
def tasks_oracle(a):
    tasks,shifts=a;index=progress=0;answer=[]
    for available in shifts:
        while index<len(tasks) and available>=tasks[index]-progress:
            available-=tasks[index]-progress;index+=1;progress=0
        if index==len(tasks):index=progress=0;answer.append(0)
        else:progress+=available;answer.append(len(tasks)-index)
    return answer
def random_tasks(r):return [[r.randint(1,12) for _ in range(r.randint(1,10))],[r.randint(0,50) for _ in range(r.randint(1,15))]]
def drone_oracle(a):
    drones,target=a;eligible=[]
    for i,(x,y,radius) in enumerate(drones):
        distance=abs(x-target[0])+abs(y-target[1])
        if distance<=radius:eligible.append((distance,i))
    return min(eligible)[1] if eligible else -1
def random_drone(r):return [[[r.randint(-20,20),r.randint(-20,20),r.randint(0,30)] for _ in range(r.randint(1,20))],[r.randint(-20,20),r.randint(-20,20)]]
def splits_oracle(a):
    nums=a[0];best=0
    for removed in range(-1,len(nums)):
        arr=[x for i,x in enumerate(nums) if i!=removed]
        best=max(best,sum(gcd(*arr[:i+1])==gcd(*arr[i+1:]) for i in range(len(arr)-1)))
    return best
def random_splits(r):return [[r.randint(1,50) for _ in range(r.randint(1,10))]]

PANCAKE='''def minimum_prefix_reversal_sort(nums,pre):
    from collections import deque
    start=tuple(nums);target=tuple(range(len(nums)))
    if start==target:return 0
    seen={start};queue=deque([(start,0)])
    while queue:
        state,distance=queue.popleft()
        for length in pre:
            nxt=state[:length][::-1]+state[length:]
            if nxt==target:return distance+1
            if nxt not in seen:seen.add(nxt);queue.append((nxt,distance+1))
    return -1
'''
STRENGTH='''def minimum_initial_monster_strength(monsters,boosts):
    delta=[0]*(len(monsters)+1)
    for left,right,value in boosts:delta[left]+=value;delta[right+1]-=value
    def wins(initial):
        bonus=0
        for need,change in zip(monsters,delta):
            bonus+=change
            if initial+bonus<need:return False
            initial=max(0,initial-need)
        return True
    low,high=0,sum(monsters)
    while low<high:
        middle=(low+high)//2
        if wins(middle):high=middle
        else:low=middle+1
    return low
'''
TASKS='''def unfinished_tasks_after_shifts(tasks,shifts):
    from itertools import accumulate
    prefix=list(accumulate(tasks,initial=0));count=len(tasks);index=progress=0;answer=[]
    for available in shifts:
        if available<tasks[index]-progress:progress+=available;answer.append(count-index);continue
        left=available-(tasks[index]-progress)
        if left>=prefix[-1]-prefix[index+1]:index=progress=0;answer.append(0);continue
        low,high=index+1,count
        while low<high:
            middle=(low+high)//2
            if left<prefix[middle+1]-prefix[index+1]:high=middle
            else:low=middle+1
        progress=left-(prefix[low]-prefix[index+1]);index=low;answer.append(count-index)
    return answer
'''
DRONE='''def nearest_reaching_drone(drones,target):
    answer=-1;best=float('inf')
    for i,(x,y,radius) in enumerate(drones):
        distance=abs(x-target[0])+abs(y-target[1])
        if distance<=radius and distance<best:best=distance;answer=i
    return answer
'''
SPLITS='''def maximum_gcd_split_positions(nums):
    from math import gcd
    def score(arr):
        prefix=[];value=0
        for x in arr:value=gcd(value,x);prefix.append(value)
        suffix=[0]*len(arr);value=0
        for i in range(len(arr)-1,-1,-1):value=gcd(value,arr[i]);suffix[i]=value
        return sum(prefix[i]==suffix[i+1] for i in range(len(arr)-1))
    return max([score(nums)]+[score(nums[:i]+nums[i+1:]) for i in range(len(nums))])
'''

BATCH={
3991:entry('minimum_prefix_reversal_sort',[('nums','list[int]'),('pre','list[int]')],'int',['arrays','breadth-first search'],['nums is a permutation of 0..n-1 and pre contains allowed prefix lengths.','One operation reverses the first x elements for an x in pre.','Return the minimum operations to sort, or -1 if unreachable.'],[([[2,0,1],[2,3]],'Two allowed prefix reversals reach 0,1,2.'),([[0,1,2],[2]],'The permutation is already sorted, requiring zero operations.')],[[n,p] for n,p in [([0],[1]),([1,0],[2]),([0,1,2],[2]),([2,0,1],[2,3]),([2,1,0],[3]),([1,2,0],[2]),([3,2,1,0],[2,4]),([1,0,2],[2]),([2,3,0,1],[3]),([1,3,2,0],[2,3,4]),([4,3,2,1,0],[5]),([0,2,1,3],[2,3]),([3,0,2,1],[2,4]),([2,1,3,0],[1,2,3,4])]],PANCAKE,[PANCAKE.replace('distance+1','distance+2'),PANCAKE.replace('return -1','return 0')],['Charges two operations for every prefix reversal.','Reports unreachable permutations as already sorted.'],pancake_oracle,random_pancake,['The state space is finite permutations and every operation has unit cost.','Breadth-first search from the input using each allowed prefix length.','Return the first distance reaching sorted order; return -1 if the queue empties.','BFS explores all states by nondecreasing operation count, so its first target distance is minimal.'],'O(n!*|pre|*n)','O(n!)',5),
4008:entry('minimum_initial_monster_strength',[('monsters','list[int]'),('boosts','list[list[int]]')],'int',['arrays','binary search'],['Fight monsters in index order; interval boosts temporarily add to strength only while checking their covered indices.','After victory, subtract monster strength and clamp permanent strength at zero.','Return the least initial permanent strength that defeats all monsters.'],[([[5,10,15],[[1,1,10]]],'Despite the middle boost, initial strength thirty is required to sustain all three fights.'),([[5],[[0,0,5]]],'The boost alone meets the requirement, so zero initial strength suffices.')],[[m,b] for m,b in [([1],[]),([5],[[0,0,5]]),([5,10,15],[[1,1,10]]),([3,3],[]),([10,1],[[0,0,9]]),([5,5,5],[[0,2,5]]),([8,2,8],[[0,0,4],[2,2,4]]),([1,10,1],[[1,1,20]]),([20,5],[[0,1,10]]),([4,7,2],[[0,1,3],[1,2,2]]),([100],[[0,0,99]]),([6,6,6,6],[[1,2,6]]),([2,9,2,9],[[0,3,1],[1,1,8]]),([10,20,30],[[0,2,5],[1,2,10]])]],STRENGTH,[STRENGTH.replace('initial=max(0,initial-need)','initial-=need'),STRENGTH.replace('bonus+=change','bonus=change')],['Allows permanent strength to become negative rather than clamping it.','Uses only the latest difference-array change instead of the accumulated active bonus.'],strength_oracle,random_strength,['Precompute interval bonuses with a difference array.','Feasibility is monotone in initial strength, enabling lower-bound binary search.','Simulate all fights for each candidate, accumulating bonuses and clamping post-fight strength.','Any strength above a feasible candidate remains feasible, so binary search returns the minimum.'],'O((n+b)*log(sum monsters))','O(n)',5),
4012:entry('unfinished_tasks_after_shifts',[('tasks','list[int]'),('shifts','list[int]')],'list[int]',['arrays','binary search'],['Tasks are processed in order and partial progress carries to the next shift.','When a shift completes all remaining tasks, its extra time is discarded and the next shift restarts from task zero.','Return the number of unfinished tasks after each shift.'],[([[1,4,4],[9,1,4]],'The first shift finishes all tasks; later shifts leave two and then one unfinished.'),([[5,5],[3,3]],'The first shift leaves two tasks; the second finishes task zero and leaves one.')],[[t,s] for t,s in [([1],[0]),([1],[1]),([1,4,4],[9,1,4]),([5,5],[3,3]),([2,3],[1,1,1]),([2,3],[5,5]),([1,1,1],[2]),([10],[3,3,4]),([3,1,4],[4,4]),([2,2,2],[7]),([4,5],[4,0,5]),([1,2,3],[1,2,3]),([6,2,5],[7,3,3]),([2,8,1],[20,1])]],TASKS,[TASKS.replace('progress+=available','progress=available'),TASKS.replace('answer.append(0);continue','answer.append(count);continue')],['Replaces prior partial progress rather than carrying it forward.','Reports all tasks unfinished immediately after completing a full cycle.'],tasks_oracle,random_tasks,['Prefix sums locate how many complete tasks fit after the current partial task.','Handle a shift that remains inside the current task directly; otherwise binary-search the completion boundary.','Reset to task zero only when every remaining task finishes.','The cumulative work interval uniquely determines the next task and its partial progress.'],'O((tasks+shifts)*log tasks)','O(tasks)',5),
4024:entry('nearest_reaching_drone',[('drones','list[list[int]]'),('target','list[int]')],'int',['arrays','geometry'],['Each drone is [x,y,range] and distance is Manhattan distance.','A drone qualifies when its distance to target is at most its range.','Return the closest qualifying index, breaking ties by smaller index, or -1.'],[([[[0,0,8],[2,2,9]],[3,4]],'Both qualify, and drone one is only three steps away.'),([[[0,0,1]],[3,3]],'The only drone cannot reach the target, so return -1.')],[[d,t] for d,t in [([[0,0,0]],[0,0]),([[0,0,1]],[3,3]),([[0,0,8],[2,2,9]],[3,4]),([[1,1,2],[3,3,2]],[2,2]),([[-1,-1,4],[5,5,1]],[0,0]),([[0,0,5],[2,0,3]],[4,0]),([[1,2,0]],[1,2]),([[10,10,10],[0,0,30]],[5,5]),([[0,1,1],[1,0,1]],[0,0]),([[3,4,7]],[0,0]),([[0,0,2],[0,0,3]],[1,0]),([[-5,0,5],[5,0,5]],[0,0]),([[2,2,1],[2,3,0]],[2,3]),([[100,100,1],[0,0,0]],[0,0])]],DRONE,[DRONE.replace('distance<=radius','distance<radius'),DRONE.replace('distance<best','distance<=best')],['Excludes drones whose range exactly equals the distance.','Lets a later equal-distance drone replace the required smaller index.'],drone_oracle,random_drone,['Compute Manhattan distance independently for each drone.','Keep a drone only if distance is within range, then improve the answer only on a strict distance decrease.','Scan in index order with best distance initialized to infinity.','Strict improvement preserves the first, and therefore smallest-index, drone on ties.'],'O(n)','O(1)',3),
4035:entry('maximum_gcd_split_positions',[('nums','list[int]')],'int',['arrays','math'],['Remove zero or one element while preserving order.','A split is valid when the GCD of its nonempty prefix equals the GCD of its nonempty suffix.','Return the maximum number of valid split positions after the optional removal.'],[([[10,30,15,10]],'An optimal optional removal leaves two valid GCD split positions.'),([[2]],'A one-element result has no split positions.')],[[x] for x in [[1],[2],[2,2],[2,3],[10,30,15,10],[6,10,15],[4,8,12,16],[3,6,9,12],[5,7,11],[2,4,8,3],[12,18,24,30],[7,7,7,7],[6,2,4,8,16],[9,3,6,12,15]]],SPLITS,[SPLITS.replace('range(len(nums))','range(1,len(nums))'),SPLITS.replace('prefix[i]==suffix[i+1]','prefix[i]!=suffix[i+1]')],['Never considers removing the first element.','Counts unequal prefix/suffix GCDs instead of equal ones.'],splits_oracle,random_splits,['For any fixed remaining array, prefix and suffix GCD arrays score every split in linear time.','Evaluate the original and each possible one-element removal.','Build both GCD scans and count equal adjacent-side values.','The outer enumeration covers every permitted result; the inner scan checks every legal split exactly.'],'O(n^2)','O(n)',5),
}
BATCH[4035]['boundaries'].append([[1,2,2]])
