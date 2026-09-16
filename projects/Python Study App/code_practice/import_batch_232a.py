"""Balanced shipments, activation time, trionic sums, repeat windows, and permutation masks."""
from functools import lru_cache
from .import_batch_055 import entry


def shipments_oracle(args):
    weight=args[0];n=len(weight)
    @lru_cache(None)
    def solve(start):
        if start>=n:return 0
        best=solve(start+1);maximum=weight[start]
        for end in range(start+1,n):
            maximum=max(maximum,weight[end])
            if weight[end]<maximum:best=max(best,1+solve(end+1))
        return best
    return solve(0)

def random_shipments(rng):return [[rng.randint(1,20) for _ in range(rng.randint(2,10))]]

def activation_oracle(args):
    s,order,k=args;n=len(s)
    for time in range(n):
        starred=set(order[:time+1]);valid=0
        for left in range(n):
            for right in range(left,n):valid+=any(index in starred for index in range(left,right+1))
        if valid>=k:return time
    return -1

def random_activation(rng):
    n=rng.randint(1,10);order=list(range(n));rng.shuffle(order)
    return [''.join(rng.choice('abc') for _ in range(n)),order,rng.randint(1,n*(n+1)//2)]

def is_trionic(values):
    n=len(values)
    for first in range(1,n-2):
        if not all(values[i-1]<values[i] for i in range(1,first+1)):continue
        for second in range(first+1,n-1):
            if all(values[i-1]>values[i] for i in range(first+1,second+1)) and all(values[i-1]<values[i] for i in range(second+1,n)):return True
    return False

def trionic_oracle(args):
    nums=args[0];answer=None
    for left in range(len(nums)):
        for right in range(left+4,len(nums)+1):
            values=nums[left:right]
            if is_trionic(values):answer=sum(values) if answer is None else max(answer,sum(values))
    return answer

def random_trionic(rng):
    a=rng.randint(1,3);b=rng.randint(1,3);c=rng.randint(1,3);values=[rng.randint(-15,5)]
    for _ in range(a):values.append(values[-1]+rng.randint(1,6))
    for _ in range(b):values.append(values[-1]-rng.randint(1,6))
    for _ in range(c):values.append(values[-1]+rng.randint(1,6))
    return [values]

def repeating_oracle(args):
    nums,k=args;answer=0
    for left in range(len(nums)):
        counts={}
        for right in range(left,len(nums)):
            counts[nums[right]]=counts.get(nums[right],0)+1
            if sum(count>1 for count in counts.values())<=k:answer=max(answer,right-left+1)
    return answer

def random_repeating(rng):
    n=rng.randint(1,15);return [[rng.randint(1,7) for _ in range(n)],rng.randint(0,n)]

def permutation_oracle(args):
    nums=args[0]
    misplaced=[value for index,value in enumerate(nums) if index!=value]
    if not misplaced:return 0
    answer=misplaced[0]
    for value in misplaced[1:]:answer&=value
    return answer

def random_permutation(rng):
    nums=list(range(rng.randint(1,10)));rng.shuffle(nums);return [nums]


SHIPMENTS='''def maximum_balanced_shipments(weight):
    answer=maximum=0
    for value in weight:
        maximum=max(maximum,value)
        if value<maximum:
            answer+=1;maximum=0
    return answer
'''

ACTIVATION='''def minimum_activation_time(s,order,k):
    n=len(s);total=n*(n+1)//2
    def active(time):
        starred=[False]*n
        for index in order[:time+1]:starred[index]=True
        invalid=run=0
        for index in range(n+1):
            if index<n and not starred[index]:run+=1
            else:invalid+=run*(run+1)//2;run=0
        return total-invalid>=k
    if not active(n-1):return -1
    low=0;high=n-1
    while low<high:
        middle=(low+high)//2
        if active(middle):high=middle
        else:low=middle+1
    return low
'''

TRIONIC='''def maximum_trionic_subarray_sum(nums):
    impossible=None;single=nums[0];increase=decrease=final=impossible;answer=impossible
    for index in range(1,len(nums)):
        value=nums[index];old_single=single;old_increase=increase;old_decrease=decrease;old_final=final
        single=value;increase=decrease=final=impossible
        if nums[index-1]<value:
            increase=max(old_single+value,old_increase+value if old_increase is not None else old_single+value)
            if old_decrease is not None:final=old_decrease+value
            if old_final is not None:final=max(final,old_final+value) if final is not None else old_final+value
        elif nums[index-1]>value:
            if old_increase is not None:decrease=old_increase+value
            if old_decrease is not None:decrease=max(decrease,old_decrease+value) if decrease is not None else old_decrease+value
        if final is not None:answer=final if answer is None else max(answer,final)
    return answer
'''

REPEATING='''def longest_semi_repeating_subarray(nums,k):
    counts={};repeated=0;left=0;answer=0
    for right,value in enumerate(nums):
        counts[value]=counts.get(value,0)+1
        if counts[value]==2:repeated+=1
        while repeated>k:
            old=nums[left];counts[old]-=1
            if counts[old]==1:repeated-=1
            left+=1
        answer=max(answer,right-left+1)
    return answer
'''

PERMUTATION='''def maximum_sorting_and_value(nums):
    answer=-1
    for index,value in enumerate(nums):
        if index!=value:answer&=value
    return max(answer,0)
'''

def lesson(a,b,c,d):return [a,b,c,d]

S_CASES=[[[1,2]],[[2,1]],[[4,5]],[[3,1,2]],[[5,4,3,2]],[[1,3,2,4,1]],[[9,1,9,1]],[[2,5,1,4,3,6]],[[1,1,2,1]],[[8,7,6,5,4,3]],[[1,10,2,9,3]],[[6,2,5,1,4,3]]]
A_CASES=[[s,o,k] for s,o,k in (('a',[0],1),('ab',[0,1],2),('ab',[1,0],3),('abc',[2,0,1],4),('abcd',[3,2,1,0],4),('abcde',[2,0,4,1,3],9),('aaaa',[1,3,0,2],10),('xyzxyz',[5,0,2,4,1,3],12),('pqrs',[0,1,2,3],1),('abcdefg',[3,1,5,0,6,2,4],20),('zzzzz',[4,3,2,1,0],6),('coding',[2,5,0,4,1,3],21))]
T_CASES=[[[2,4,1,3]],[[5,7,6,2,3]],[[-1,0,-2,1,3]],[[-5,-2,4,1,-3,2,8]],[[9,10,8,7,11]],[[1,2,3,2,1,4,5]],[[10,20,5,6]],[[0,4,3,2,9,10]],[[8,9,1,2,3]],[[3,8,2,7]],[[1,5,4,3,2,6]],[[20,21,10,0,1,2]]]
R_CASES=[[a,k] for a,k in (([1],0),([1,1],0),([1,1],1),([1,2,3,1],0),([1,2,3,1,2,4],1),([2,2,2,2],0),([1,1,1,1,1],1),([1,2,1,3,2,4],1),([3,3,2,2,1,1],2),([1,2,3,4],0),([5,4,5,4,5],1),([1,2,1,2,3,3,4],2))]
P_CASES=[[[0]],[[1,0]],[[0,2,1]],[[0,2,3,1]],[[3,2,1,0]],[[0,1,4,3,2]],[[2,1,0,3]],[[4,1,2,3,0]],[[1,2,3,4,0]],[[0,1,2,4,3,5]],[[7,6,5,4,3,2,1,0]],[[0,5,2,3,4,1]]]

BATCH={
3638:entry('maximum_balanced_shipments',[('weight','list[int]')],'int',['arrays','greedy'],['Two to 100,000 positive parcel weights.','A shipment is a contiguous subarray whose last weight is below its maximum.','Shipments may not overlap, and parcels may be skipped.'],[([[2,5,1,4,3]],'Split as [2,5,1] and [4,3] to form two balanced shipments.'),([[4,4]],'Equal final and maximum weights are not strictly balanced, so the answer is zero.')],S_CASES,SHIPMENTS,[SHIPMENTS.replace('value<maximum','value<=maximum'),SHIPMENTS.replace('answer+=1;maximum=0','answer+=1')],['Incorrectly treats equal weights as a valid drop.','Does not reset after closing a shipment, allowing overlapping evidence.'],shipments_oracle,random_shipments,lesson('A drop below the maximum seen since the last cut is the earliest possible balanced shipment end.','Scan left to right and greedily close a shipment at every such drop.','Track the segment maximum; on value < maximum, increment the answer and reset.','Using the earliest valid end leaves the largest suffix for later shipments, so no optimal solution can gain by delaying that cut.'),'O(n)','O(1)',5),
3639:entry('minimum_activation_time',[('s','str'),('order','list[int]'),('k','int')],'int',['strings','binary search','counting'],['The order array is a permutation of all string indices.','At time t, positions order[0] through order[t] become stars.','A substring is valid when it contains at least one star.'],[(['abc',[1,0,2],2],'At time zero, starring the middle character makes four substrings valid, meeting two.'),(['abc',[0,1,2],6],'All six substrings become valid only after the third position is starred at time two.')],A_CASES,ACTIVATION,[ACTIVATION.replace('total-invalid>=k','total-invalid>k'),ACTIVATION.replace('order[:time+1]','order[:time]')],['Requires strictly more than k valid substrings.','Activates only positions before time t and misses the current activation.'],activation_oracle,random_activation,lesson('The number of valid substrings never decreases as more positions become stars.','Binary-search the first time whose valid-substring count reaches k.','For a candidate time, subtract star-free segment substring counts from n(n+1)/2.','Monotonicity makes the first passing time searchable, and every invalid substring lies in exactly one maximal star-free segment.'),'O(n log n)','O(n)',5),
3640:entry('maximum_trionic_subarray_sum',[('nums','list[int]')],'int',['arrays','dynamic programming'],['The array has at least four signed integers.','A valid subarray has nonempty strictly increasing, decreasing, then increasing edge runs.','Return the maximum sum among all valid contiguous subarrays.'],[([[1,3,2,4]],'The entire array follows increase, decrease, increase and sums to ten.'),([[0,-2,-1,-3,0,2,-1]],'The best valid subarray is [-2,-1,-3,0,2], whose sum is negative four.')],T_CASES,TRIONIC,[TRIONIC.replace('if old_final is not None:final=max(final,old_final+value) if final is not None else old_final+value','if old_final is not None:pass'),TRIONIC.replace('if old_decrease is not None:decrease=max(decrease,old_decrease+value) if decrease is not None else old_decrease+value','if old_decrease is not None:pass')],['Restarts rather than extending the final increasing phase.','Fails to extend a decreasing phase beyond one edge.'],trionic_oracle,random_trionic,lesson('Track the best sum ending at each of the four pattern phases.','Update single, first increase, decrease, and final increase states from the previous index.','Strictly rising edges advance or extend increasing states; falling edges advance or extend the middle state.','Each state represents every valid phase-shaped subarray ending at the current index, so the final-state maximum is exactly the answer.'),'O(n)','O(1)',8),
3641:entry('longest_semi_repeating_subarray',[('nums','list[int]'),('k','int')],'int',['arrays','hash maps','sliding window'],['One to 100,000 integers.','At most k distinct values may have frequency greater than one in the window.','Return the maximum valid contiguous length.'],[([[1,2,3,1,2,3,4],2],'The length-six suffix [2,3,1,2,3,4] repeats only two distinct values.'),([[1,1,1,1,1],0],'With no repeated value allowed, only a single element can remain.')],R_CASES,REPEATING,[REPEATING.replace('counts[value]==2','counts[value]>1'),REPEATING.replace('counts[old]==1','counts[old]==0')],['Counts every extra copy as another repeated value.','Stops counting a value as repeated only after removing its final copy.'],repeating_oracle,random_repeating,lesson('A value changes the repeated-value count only when its frequency crosses between one and two.','Use a sliding window and shrink whenever more than k distinct values repeat.','Increment on frequency two; during shrinking, decrement after frequency falls to one.','The left boundary is the earliest valid boundary for each right endpoint, so every maximum window is considered.'),'O(n)','O(n)',5),
3644:entry('maximum_sorting_and_value',[('nums','list[int]')],'int',['arrays','bit manipulation'],['nums is a permutation of zero through n-1.','You may swap two values only when their bitwise AND equals the chosen k.','Return the largest k that permits sorting, or zero if already sorted.'],[([[0,3,2,1]],'Only three and one are misplaced; their AND is one.'),([[0,1,3,2]],'The misplaced values three and two have AND two.')],P_CASES,PERMUTATION,[PERMUTATION.replace('if index!=value:answer&=value','answer&=value'),PERMUTATION.replace('answer&=value','answer|=value')],['Includes fixed values, often forcing the result to zero.','Combines misplaced values with OR rather than AND.'],permutation_oracle,random_permutation,lesson('Only values outside their final positions need to participate in swaps.','The maximum feasible k is the bitwise AND of every misplaced value.','Initialize with all bits set, AND each value whose index differs, then map the sorted sentinel to zero.','Every required participant must contain every bit of k, while their shared AND is itself achievable and is the largest such mask.'),'O(n)','O(1)',5),
}
