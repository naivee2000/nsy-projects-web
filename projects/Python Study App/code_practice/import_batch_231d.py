"""Three-way bit partitions, XOR trie counts, balanced windows, rides, and range modes."""
from collections import Counter
from itertools import product
from .import_batch_055 import entry

def partition_oracle(args):
    nums=args[0];answer=0
    for assignment in product(range(3),repeat=len(nums)):
        xor_a=xor_c=0;and_b=None
        for value,group in zip(nums,assignment):
            if group==0:xor_a^=value
            elif group==1:and_b=value if and_b is None else and_b&value
            else:xor_c^=value
        answer=max(answer,xor_a+(and_b or 0)+xor_c)
    return answer

def random_partition(rng):return [[rng.randint(1,63) for _ in range(rng.randint(1,8))]]

def xor_oracle(args):
    nums,k=args;answer=0
    for left in range(len(nums)):
        value=0
        for right in range(left,len(nums)):value^=nums[right];answer+=value>=k
    return answer

def random_xor(rng):return [[rng.randint(0,63) for _ in range(rng.randint(1,20))],rng.randint(0,64)]

def balance_oracle(args):
    nums,k=args;n=len(nums);best=n
    for mask in range(1,1<<n):
        kept=[nums[i] for i in range(n) if mask>>i&1]
        if max(kept)<=k*min(kept):best=min(best,n-len(kept))
    return best

def random_balance(rng):
    n=rng.randint(1,10);return [[rng.randint(1,50) for _ in range(n)],rng.randint(1,8)]

def rides_oracle(args):
    land_start,land_duration,water_start,water_duration=args;answer=10**30
    for ls,ld in zip(land_start,land_duration):
        for ws,wd in zip(water_start,water_duration):
            answer=min(answer,max(ws,ls+ld)+wd,max(ls,ws+wd)+ld)
    return answer

def random_rides(rng):
    n=rng.randint(1,7);m=rng.randint(1,7)
    return [[rng.randint(1,20) for _ in range(n)],[rng.randint(1,10) for _ in range(n)],[rng.randint(1,20) for _ in range(m)],[rng.randint(1,10) for _ in range(m)]]

def majority_oracle(args):
    nums,queries=args;answer=[]
    for left,right,threshold in queries:
        counts=Counter(nums[left:right+1]);best=max(counts.values())
        answer.append(min(value for value,count in counts.items() if count==best) if best>=threshold else -1)
    return answer

def random_majority(rng):
    n=rng.randint(1,20);nums=[rng.randint(1,8) for _ in range(n)];queries=[]
    for _ in range(rng.randint(1,20)):
        left=rng.randrange(n);right=rng.randrange(left,n);queries.append([left,right,rng.randint(1,right-left+1)])
    return [nums,queries]

PARTITION='''def maximize_xor_and_partition(nums):
    n=len(nums);width=31;size=1<<n;subset_xor=[0]*size;subset_and=[0]*size;answer=0;all_xor=0
    for value in nums:all_xor^=value
    for selected in range(1,size):
        bit=selected&-selected;index=bit.bit_length()-1;previous=selected^bit
        subset_xor[selected]=subset_xor[previous]^nums[index]
        subset_and[selected]=nums[index] if previous==0 else subset_and[previous]&nums[index]
    for selected in range(size):
        and_value=subset_and[selected];total=all_xor^subset_xor[selected];remaining=[]
        for index,value in enumerate(nums):
            if not selected>>index&1:remaining.append(value)
        mask=((1<<width)-1)^total;basis=[0]*width
        for value in remaining:
            value&=mask
            while value:
                bit=value.bit_length()-1
                if basis[bit]:value^=basis[bit]
                else:basis[bit]=value;break
        projected=0
        for bit in range(width-1,-1,-1):projected=max(projected,projected^basis[bit])
        answer=max(answer,and_value+total+2*projected)
    return answer
'''

XOR_COUNT='''def count_subarrays_xor_at_least(nums,k):
    width=31;children=[[-1,-1]];counts=[0]
    def insert(value):
        node=0;counts[node]+=1
        for bit in range(width-1,-1,-1):
            side=value>>bit&1
            if children[node][side]<0:children[node][side]=len(children);children.append([-1,-1]);counts.append(0)
            node=children[node][side];counts[node]+=1
    def less(value,limit):
        node=0;answer=0
        for bit in range(width-1,-1,-1):
            if node<0:break
            side=value>>bit&1
            if limit>>bit&1:
                same=children[node][side]
                if same>=0:answer+=counts[same]
                node=children[node][side^1]
            else:node=children[node][side]
        return answer
    insert(0);prefix=0;below=0
    for value in nums:prefix^=value;below+=less(prefix,k);insert(prefix)
    total=len(nums)*(len(nums)+1)//2
    return total-below
'''

BALANCE='''def minimum_balanced_removals(nums,k):
    import bisect
    values=sorted(nums);best=1
    for left,value in enumerate(values):best=max(best,bisect.bisect_right(values,k*value)-left)
    return len(values)-best
'''

RIDES='''def earliest_two_ride_finish(landStartTime,landDuration,waterStartTime,waterDuration):
    def order(first_start,first_duration,second_start,second_duration):
        first_finish=min(start+duration for start,duration in zip(first_start,first_duration))
        return min(max(start,first_finish)+duration for start,duration in zip(second_start,second_duration))
    return min(order(landStartTime,landDuration,waterStartTime,waterDuration),order(waterStartTime,waterDuration,landStartTime,landDuration))
'''

MAJORITY='''def threshold_majority_queries(nums,queries):
    import heapq
    block=max(1,int(len(nums)**0.5));ordered=sorted(enumerate(queries),key=lambda item:(item[1][0]//block,item[1][1] if item[1][0]//block%2==0 else -item[1][1]))
    frequency={};heaps=[[] for _ in range(len(nums)+1)];maximum=0;left=0;right=-1;answer=[-1]*len(queries)
    def change(value,delta):
        nonlocal maximum
        new=frequency.get(value,0)+delta;frequency[value]=new
        if new>0:heapq.heappush(heaps[new],value)
        maximum=max(maximum,new)
        while maximum:
            while heaps[maximum] and frequency.get(heaps[maximum][0])!=maximum:heapq.heappop(heaps[maximum])
            if heaps[maximum]:break
            maximum-=1
    for index,(target_left,target_right,threshold) in ordered:
        while left>target_left:left-=1;change(nums[left],1)
        while right<target_right:right+=1;change(nums[right],1)
        while left<target_left:change(nums[left],-1);left+=1
        while right>target_right:change(nums[right],-1);right-=1
        if maximum>=threshold:answer[index]=heaps[maximum][0]
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

P_CASES=[[x] for x in ([1],[1,1],[1,2,3],[2,3,6,7],[7,7,7],[1,2,4,8],[5,10,12],[31,16,7,3],[2,2,3],[9,6,3,12],[1,15,8,7,4],[63,32,16,8,4])]
X_CASES=[[a,k] for a,k in (([0],0),([0],1),([1],1),([1],2),([0,0,0,0],0),([1,2,3],0),([1,2,3],4),([5,1,5],5),([7,7,7],1),([1,0,1,0],2),([8,4,2,1],7),([31,1,15,2],16))]
B_CASES=[[a,k] for a,k in (([1],1),([1,2],1),([1,2],2),([1,6,2,10],3),([4,6],2),([10,1,10],1),([2,4,8,16],2),([5,5,5],1),([1,100,2,50],10),([3,9,27],3),([7,14,21,28],2),([100,200,300,1000],3))]
R_CASES=[[*x] for x in (([1],[1],[1],[1]),([5],[3],[1],[9]),([1,10],[2,1],[4,8],[3,2]),([10],[1],[1],[1]),([2,8],[4,1],[7],[3]),([3,9],[5,2],[1,20],[10,1]),([1,2],[10,10],[30],[1]),([100],[100],[100],[100]),([1,50],[1,1],[25,60],[2,2]),([7,8],[3,4],[1,2],[9,10]),([4],[6],[5],[5]),([2,20,30],[2,2,2],[1,40],[20,1]))]
M_CASES=[[a,q] for a,q in (([1],[[0,0,1]]),([1,2],[[0,1,1]]),([1,2],[[0,1,2]]),([3,2,3,2,3,2,4],[[0,6,4],[1,5,2],[2,4,1],[3,3,1]]),([5,5,4,4],[[0,3,2]]),([2,1,2,1],[[0,3,2]]),([9,8,7],[[0,2,1]]),([1,1,1],[[1,2,2]]),([4,3,4,3,2,2],[[0,5,2],[1,4,2]]),([10,20,10,20],[[0,3,3]]),([6,6,5,5,4],[[0,4,2]]),([3,1,3,1,2],[[0,4,1],[1,3,2]]))]

BATCH={
3630:entry('maximize_xor_and_partition',[('nums','list[int]')],'int',['bit manipulation','linear basis','subset enumeration'],['One to 19 positive integers up to one billion.','Partition every element among three possibly empty subsequences.','Maximize XOR(A)+AND(B)+XOR(C), with empty operations worth zero.'],[([[2,3]],'Putting three in A and two in B gives five.'),([[1,3,2]],'Putting one, two, and three in separate groups gives six.')],P_CASES,PARTITION,[PARTITION.replace('value&=mask','value&=total'),PARTITION.replace('for selected in range(size)','for selected in range(1)')],['Projects the XOR basis onto total-XOR bits instead of complementary bits.','Considers only an empty AND group and misses beneficial nonempty choices.'],partition_oracle,random_partition,lesson('Fixing the elements assigned to B fixes its AND and leaves a two-way XOR split over the complement.','Enumerate every B subset and optimize the remaining split with a projected XOR basis.','For complement total XOR T, maximize x+(x xor T)=T+2*(x & ~T) by a basis projected onto complement bits.','Every partition has one enumerated B subset, and the linear basis considers every attainable XOR for A while C receives its complement.'),'O(2^n*n*log V)','O(2^n)',8),
3632:entry('count_subarrays_xor_at_least',[('nums','list[int]'),('k','int')],'int',['bitwise tries','prefix xor','counting'],['Up to 100,000 nonnegative values and threshold k.','Count contiguous subarrays whose XOR is at least k.','Return the exact count, which may exceed 32-bit range.'],[([[3,1,2,3],2],'Six subarrays have XOR at least two.'),([[0,0,0],0],'All six subarrays qualify when k is zero.')],X_CASES,XOR_COUNT,[XOR_COUNT.replace('less(prefix,k)','less(prefix,k+1)'),XOR_COUNT.replace('insert(0);prefix=0;below=0','prefix=0;below=0')],['Counts XOR values strictly greater than k instead of greater than or equal.','Omits the empty prefix and therefore misses subarrays beginning at index zero.'],xor_oracle,random_xor,lesson('A subarray XOR is the XOR of two prefix values.','Store earlier prefixes in a binary trie and count partners producing XOR below k.','For each new prefix, add count_less(prefix,k), insert it, then subtract the total below-k pairs from all subarrays.','The trie follows equal or differing bits according to k, counting every earlier prefix exactly once.'),'O(n log V)','O(n log V)',8),
3634:entry('minimum_balanced_removals',[('nums','list[int]'),('k','int')],'int',['arrays','sorting','binary search'],['One to 100,000 positive values.','A nonempty remainder is balanced when max <= k*min.','Return the minimum removal count.'],[([[2,1,5],2],'Keeping one and two removes only five.'),([[1,6,2,9],3],'The largest balanced subset has two elements, so remove two.')],B_CASES,BALANCE,[BALANCE.replace('bisect.bisect_right','bisect.bisect_left'),BALANCE.replace('return len(values)-best','return best')],['Treats equality with k times the minimum as invalid.','Returns the number kept instead of the number removed.'],balance_oracle,random_balance,lesson('After sorting, every maximum-size balanced selection can be taken as one contiguous value window.','Fix each minimum and binary-search the last value no greater than k times it.','Maximize the inclusive window length and remove everything else.','Any skipped in-range value can be added without changing the extremes, so an optimal subset is contiguous in sorted order.'),'O(n log n)','O(n)',5),
3635:entry('earliest_two_ride_finish',[('landStartTime','list[int]'),('landDuration','list[int]'),('waterStartTime','list[int]'),('waterDuration','list[int]')],'int',['arrays','greedy','scheduling'],['Each category has one to 50,000 rides.','Take exactly one ride from each category in either order.','A ride may start at or after its opening time.'],[([[2,8],[4,1],[6],[3]],'Land ride zero finishes at six, allowing the water ride to finish at nine.'),([[5],[3],[1],[10]],'Taking water first and then land finishes at fourteen.')],R_CASES,RIDES,[RIDES.replace('return min(order(landStartTime,landDuration,waterStartTime,waterDuration),order(waterStartTime,waterDuration,landStartTime,landDuration))','return order(landStartTime,landDuration,waterStartTime,waterDuration)'),RIDES.replace('max(start,first_finish)+duration','start+first_finish+duration')],['Considers only land-before-water order.','Adds an opening time and prior finish instead of waiting until their maximum.'],rides_oracle,random_rides,lesson('For a fixed order, only the earliest possible finish among first-category rides matters.','Compute that finish, then choose the second ride minimizing max(opening,first_finish)+duration.','Evaluate land-water and water-land orders and take the smaller result.','Any later first finish cannot improve a fixed second ride, so the earliest first finish dominates all alternatives.'),'O(n+m)','O(1)',5),
3636:entry('threshold_majority_queries',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['arrays','mo algorithm','frequency counting'],['The array has up to 10,000 values and there are up to 50,000 inclusive range queries.','Choose the highest-frequency value meeting threshold, breaking ties by smaller value.','Return -1 if the maximum frequency is below threshold.'],[([[1,1,2,2,1,1],[[0,5,4],[0,3,3],[2,3,2]]],'The answers are one, negative one, and two.'),([[3,2,3,2,3,2,3],[[0,6,4],[1,5,2],[2,4,1],[3,3,1]]],'Range modes and the smallest-value tie rule produce 3,2,3,2.')],M_CASES,MAJORITY,[MAJORITY.replace('maximum>=threshold','maximum>threshold'),MAJORITY.replace('answer[index]=heaps[maximum][0]','answer[index]=-heaps[maximum][0]')],['Rejects candidates occurring exactly threshold times.','Returns a negated heap value instead of the smallest tied value.'],majority_oracle,random_majority,lesson('Mo ordering changes only a few boundary elements between neighboring offline queries.','Maintain value frequencies plus lazy min-heaps indexed by frequency.','Add or remove boundary values, clean stale heap entries at the current maximum frequency, then test the threshold.','The highest nonempty frequency bucket is the range mode, and its min-heap root enforces the smallest-value tie rule.'),'O((n+q)*sqrt(n)*log n)','O(n+q)',8),
}
