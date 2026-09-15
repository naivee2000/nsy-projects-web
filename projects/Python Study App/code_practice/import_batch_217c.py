"""Spell spacing, mutable peaks, rook balancing, and fixed/suffix bit flips."""
from collections import Counter
from itertools import combinations

from .import_batch_055 import entry


def damage_oracle(args):
    power=args[0];best=0
    for mask in range(1<<len(power)):
        chosen=[power[i] for i in range(len(power)) if mask>>i&1]
        if all(abs(a-b)>2 or a==b for a,b in combinations(chosen,2)):best=max(best,sum(chosen))
    return best


def random_damage(rng):return [[rng.randint(1,15) for _ in range(rng.randint(1,11))]]


def is_peak(nums,index):return 0<index<len(nums)-1 and nums[index]>nums[index-1] and nums[index]>nums[index+1]


def peaks_oracle(args):
    nums,queries=args;nums=nums[:];answer=[]
    for query in queries:
        if query[0]==1:answer.append(sum(is_peak(nums,index) for index in range(query[1]+1,query[2])))
        else:nums[query[1]]=query[2]
    return answer


def random_peaks(rng):
    nums=[rng.randint(0,20) for _ in range(rng.randint(3,15))];queries=[]
    for _ in range(rng.randint(1,15)):
        if rng.random()<.55:
            left=rng.randint(0,len(nums)-2);queries.append([1,left,rng.randint(left+1,len(nums)-1)])
        else:queries.append([2,rng.randrange(len(nums)),rng.randint(0,20)])
    if not any(q[0]==1 for q in queries):queries.append([1,0,len(nums)-1])
    return [nums,queries]


def rooks_oracle(args):
    rooks=args[0];n=len(rooks)
    best_rows=min(sum(abs(rooks[p[i]][0]-i) for i in range(n)) for p in __import__('itertools').permutations(range(n)))
    best_cols=min(sum(abs(rooks[p[i]][1]-i) for i in range(n)) for p in __import__('itertools').permutations(range(n)))
    return best_rows+best_cols


def random_rooks(rng):
    n=rng.randint(1,7);cells=rng.sample([(r,c) for r in range(n) for c in range(n)],n);return [[list(x) for x in cells]]


def triple_oracle(args):
    start=tuple(args[0]);queue=[(start,0)];seen={start};n=len(start)
    while queue:
        state,moves=queue.pop(0)
        if all(state):return moves
        for index in range(n-2):
            nxt=list(state)
            for j in range(index,index+3):nxt[j]^=1
            value=tuple(nxt)
            if value not in seen:seen.add(value);queue.append((value,moves+1))
    return -1


def random_triple(rng):return [[rng.randint(0,1) for _ in range(rng.randint(1,10))]]


def suffix_oracle(args):
    nums=args[0];state=tuple(nums);queue=[(state,0)];seen={state}
    while queue:
        current,moves=queue.pop(0)
        if all(current):return moves
        for index in range(len(nums)):
            nxt=current[:index]+tuple(1-v for v in current[index:])
            if nxt not in seen:seen.add(nxt);queue.append((nxt,moves+1))


def random_suffix(rng):return [[rng.randint(0,1) for _ in range(rng.randint(1,10))]]


DAMAGE='''def maximum_spell_damage(power):
    from collections import Counter
    counts=Counter(power);values=sorted(counts);dp=[0]*(len(values)+1)
    for index,value in enumerate(values,1):
        prior=index-1
        while prior and values[prior-1]>=value-2:prior-=1
        dp[index]=max(dp[index-1],dp[prior]+value*counts[value])
    return dp[-1]
'''


PEAKS='''def dynamic_peak_counts(nums,queries):
    n=len(nums);tree=[0]*(n+1)
    def peak(index):return int(0<index<n-1 and nums[index]>nums[index-1] and nums[index]>nums[index+1])
    def add(index,delta):
        index+=1
        while index<=n:tree[index]+=delta;index+=index&-index
    def prefix(index):
        total=0
        while index>0:total+=tree[index];index-=index&-index
        return total
    for index in range(1,n-1):add(index,peak(index))
    answer=[]
    for query in queries:
        if query[0]==1:answer.append(prefix(query[2])-prefix(query[1]+1))
        else:
            position,value=query[1],query[2];affected=range(max(1,position-1),min(n-1,position+1)+1);old={i:peak(i) for i in affected};nums[position]=value
            for i in affected:add(i,peak(i)-old[i])
    return answer
'''


ROOKS='''def minimum_rook_balance_moves(rooks):
    rows=sorted(row for row,_ in rooks);columns=sorted(column for _,column in rooks)
    return sum(abs(value-index) for index,value in enumerate(rows))+sum(abs(value-index) for index,value in enumerate(columns))
'''


TRIPLE='''def minimum_triple_bit_flips(nums):
    nums=nums[:];operations=0
    for index in range(len(nums)-2):
        if nums[index]==0:
            operations+=1
            for changed in range(index,index+3):nums[changed]^=1
    return operations if all(nums) else -1
'''


SUFFIX='''def minimum_suffix_bit_flips(nums):
    flipped=0;operations=0
    for value in nums:
        if value^flipped==0:operations+=1;flipped^=1
    return operations
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
3186:entry('maximum_spell_damage',[('power','list[int]')],'int',['dynamic programming','sorting','counting'],['power is a nonempty positive-integer array; equal values may repeat.','Casting damage x forbids casting any spell with damage x-2, x-1, x+1, or x+2; equal-x spells remain compatible.','Return the maximum total damage from any compatible multiset of indices.'],[([[1,1,3,4]],'Cast both one-damage spells and the four-damage spell for total six.'),([[7,1,6,6]],'Casting both six-damage spells gives twelve, better than combining one and seven.')],[[p] for p in [[1],[1,1,3,4],[7,1,6,6],[1,2],[1,3],[1,4],[2,2,4,4],[3,6,9],[1,2,3,4,5],[10,10,8,12],[2,5,5,8],[1,7,8,9],[4,4,4,6],[5,1,2,10]]],DAMAGE,[DAMAGE.replace('value-2','value-1'),DAMAGE.replace('value*counts[value]','value')],['Forbids only distance one and can combine damages differing by two.','Counts each distinct damage once and loses repeated compatible spells.'],damage_oracle,random_damage,lesson('All copies of one damage value should be taken together because they do not conflict and are positive.','Sort distinct values and use weighted interval DP, jumping back past values within two.','dp[i]=max(dp[i-1],weight[i]+dp[last value < current-2]).','Every optimum either omits the current value or takes all its copies and may combine only with the identified compatible prefix.'),'O(n log n)','O(distinct values)',5),
3187:entry('dynamic_peak_counts',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['binary indexed trees','arrays'],['nums has at least three integers; queries are [1,left,right] counts or [2,index,value] updates.','A counted peak must lie strictly inside the requested inclusive range and exceed both neighbors in the current full array.','Return one integer for each type-one query in order.'],[([[3,1,4,2,5],[[2,3,4],[1,0,4]]],'After changing index three to four, no interior value is strictly above both neighbors.'),([[1,3,1],[[1,0,2],[2,1,0],[1,0,2]]],'The initial middle value is a peak; after the update it is not, giving [1,0].')],[[n,q] for n,q in [([3,1,4,2,5],[[2,3,4],[1,0,4]]),([1,3,1],[[1,0,2],[2,1,0],[1,0,2]]),([1,2,3],[[1,0,2]]),([3,2,1],[[1,0,2]]),([1,5,1,5,1],[[1,0,4]]),([1,5,1,5,1],[[1,1,3]]),([2,1,2],[[2,1,3],[1,0,2]]),([5,4,3,2],[[2,2,10],[1,0,3]]),([0,1,0,1,0],[[2,2,5],[1,0,4]]),([9,1,8,2,7],[[1,0,4],[2,2,0],[1,0,4]]),([1,2,1,2],[[1,0,3]]),([4,4,4],[[1,0,2]]),([10,1,10,1,10],[[1,0,4]]),([3,9,2,8,1,7],[[2,0,10],[1,0,5]])]],PEAKS,[PEAKS.replace('prefix(query[2])-prefix(query[1]+1)','prefix(query[2]+1)-prefix(query[1])'),PEAKS.replace('position-1','position')],['Includes the query range endpoints even though they cannot count as peaks.','Refreshes only the updated index and misses changed peak status at its neighbors.'],peaks_oracle,random_peaks,lesson('Only an updated index and its two neighbors can change peak status.','Store peak indicators in a Fenwick tree for range sums; remove/restore affected indicators around updates.','Count indices left+1 through right-1; on update recompute position-1..position+1.','The indicator sum equals the number of current peaks, and locality proves no other indicator changes after one value replacement.'),'O((n+queries) log n)','O(n)',8),
3189:entry('minimum_rook_balance_moves',[('rooks','list[list[int]]')],'int',['greedy','sorting'],['There are n distinct rook cells on an n by n board with zero-based coordinates.','One move shifts one rook one cell horizontally or vertically; finish with exactly one rook per row and per column.','Return the minimum number of moves; a collision-free order of the moves is guaranteed to exist.'],[([[[0,0],[1,0],[1,1]]],'Sorted row targets cost one move and sorted column targets cost two, totaling three.'),([[[0,0],[1,1]]],'Each row and column already contains one rook, so zero moves are needed.')],[[r] for r in [[[0,0]],[[0,0],[1,1]],[[0,0],[1,0],[1,1]],[[0,0],[0,1],[0,2]],[[2,0],[2,1],[2,2]],[[0,2],[1,2],[2,2]],[[0,0],[0,3],[3,0],[3,3]],[[1,1],[1,2],[2,1]],[[0,1],[1,0],[2,2]],[[3,0],[2,1],[1,2],[0,3]],[[0,0],[0,1],[1,0],[2,2]],[[4,4],[4,3],[3,4],[2,2],[1,1]],[[0,4],[1,3],[2,2],[3,1],[4,0]],[[0,0],[1,0],[2,0],[3,0]]]],ROOKS,[ROOKS.replace('sorted(row for row,_ in rooks)','[row for row,_ in rooks]'),ROOKS.replace('+sum(abs(value-index) for index,value in enumerate(columns))','')],['Assigns row targets in input order instead of sorted order and can cross assignments unnecessarily.','Balances rows but ignores the required one-rook-per-column condition.'],rooks_oracle,random_rooks,lesson('Vertical and horizontal costs are independent, reducing the board problem to two one-dimensional assignments.','Sort row coordinates and match them to target rows 0..n-1; do the same for columns.','Return sum |sortedRows[i]-i| plus sum |sortedCols[i]-i|.','The uncrossing exchange argument makes sorted matching optimal in one dimension, and independent coordinate moves let the two minima add.'),'O(n log n)','O(n)',5),
3191:entry('minimum_triple_bit_flips',[('nums','list[int]')],'int',['greedy','arrays'],['nums is a nonempty binary array.','One operation flips exactly three consecutive elements.','Return the minimum operations that make every element one, or -1 when impossible.'],[([[0,1,1,1,0,0]],'Greedily flipping at indices zero, one, and three produces all ones in three operations.'),([[1,0]],'No length-three operation exists, so this array cannot be completed.')],[[n] for n in [[1],[0],[1,0],[0,0,0],[0,1,1,1,0,0],[1,1,1],[1,0,0],[0,1,0],[1,1,0,0],[0,0,1,1,1],[1,0,1,0,1],[0,0,0,0],[1,1,0,1,0],[0,1,1]]],TRIPLE,[TRIPLE.replace('nums[index]==0','nums[index]==1'),TRIPLE.replace('range(len(nums)-2)','range(len(nums)-3)')],['Flips when the leftmost unresolved bit is already one instead of zero.','Stops one starting position too early and misses a required final triple.'],triple_oracle,random_triple,lesson('Once the scan passes index i, no later length-three flip can change it.','Therefore flip at i exactly when its current value is zero, then verify the final two bits.','Scan i=0..n-3; if nums[i]==0 flip i..i+2 and increment; return count if all ones else -1.','The leftmost unresolved bit forces every greedy decision, establishing both necessity and minimality.'),'O(n)','O(n) copy',5),
3192:entry('minimum_suffix_bit_flips',[('nums','list[int]')],'int',['greedy','arrays'],['nums is a nonempty binary array.','An operation chooses an index and flips every element from it through the end.','Return the minimum operations needed to make all elements one.'],[([[0,1,1,0,1]],'The required effective bits alternate at four boundaries, so four suffix flips are necessary.'),([[1,1,1]],'Every bit is already one, so no operation is needed.')],[[n] for n in [[0],[1],[0,1,1,0,1],[1,1,1],[0,0],[1,0],[0,1],[0,1,0],[1,0,1],[0,0,0],[1,1,0,0],[0,0,1,1],[1,0,0,1],[0,1,0,1,0]]],SUFFIX,[SUFFIX.replace('value^flipped==0','value==0'),SUFFIX.replace('flipped^=1','flipped=1')],['Ignores the parity of earlier suffix flips when deciding the current effective bit.','Sets the flip state permanently instead of toggling it after every operation.'],suffix_oracle,random_suffix,lesson('Only the parity of prior suffix flips affects the current bit.','Scan left to right; when the effective bit is zero, a flip at this index is forced and toggles parity.','If value xor parity equals zero, increment operations and parity xor equals one.','Later flips cannot repair a current zero without also beginning here or earlier, so each greedy flip is necessary and sufficient.'),'O(n)','O(1)',5),
}
