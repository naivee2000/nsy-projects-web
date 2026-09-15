"""Good subsequences, popcount reductions, range capacity, and missing-value gaps."""
from itertools import combinations,product
from math import comb,gcd
from .import_batch_055 import entry


MOD=1_000_000_007


def good_oracle(args):
    nums=args[0];answer=0
    for size in range(1,len(nums)+1):
        for indices in combinations(range(len(nums)),size):
            values=[nums[index] for index in indices]
            if all(abs(values[i]-values[i-1])==1 for i in range(1,size)):answer+=sum(values)
    return answer%MOD


def random_good(rng):return [[rng.randint(0,8) for _ in range(rng.randint(1,11))]]


def reduction_steps(value):
    steps=0
    while value!=1:value=value.bit_count();steps+=1
    return steps


def reducible_oracle(args):
    s,k=args
    return sum(reduction_steps(value)<=k for value in range(1,int(s,2)))%MOD


def random_reducible(rng):return [bin(rng.randint(1,5000))[2:],rng.randint(1,5)]


def zero_one_oracle(args):
    nums,queries=args
    return all(sum(left<=index<=right for left,right in queries)>=value for index,value in enumerate(nums))


def random_zero_one(rng):
    n=rng.randint(1,9);queries=[]
    for _ in range(rng.randint(1,9)):
        left=rng.randrange(n);right=rng.randrange(left,n);queries.append([left,right])
    return [[rng.randint(0,5) for _ in range(n)],queries]


def prefix_capacity(nums,queries,count):
    return all(sum(value for left,right,value in queries[:count] if left<=index<=right)>=need for index,need in enumerate(nums))


def zero_two_oracle(args):
    nums,queries=args
    for count in range(len(queries)+1):
        if prefix_capacity(nums,queries,count):return count
    return -1


def random_zero_two(rng):
    n=rng.randint(1,8);queries=[]
    for _ in range(rng.randint(1,8)):
        left=rng.randrange(n);right=rng.randrange(left,n);queries.append([left,right,rng.randint(1,5)])
    return [[rng.randint(0,12) for _ in range(n)],queries]


def missing_oracle(args):
    nums=args[0];missing=[i for i,value in enumerate(nums) if value==-1]
    if not missing:return max((abs(nums[i]-nums[i-1]) for i in range(1,len(nums))),default=0)
    maximum=max((value for value in nums if value!=-1),default=1);answer=10**9
    for x in range(1,maximum+1):
        for y in range(x,maximum+1):
            for choices in product((x,y),repeat=len(missing)):
                values=list(nums)
                for index,value in zip(missing,choices):values[index]=value
                answer=min(answer,max(abs(values[i]-values[i-1]) for i in range(1,len(values))))
    return answer


def random_missing(rng):
    values=[-1 if rng.random()<.45 else rng.randint(1,8) for _ in range(rng.randint(2,8))]
    return [values]


GOOD='''def sum_good_subsequences(nums):
    modulo=1000000007;counts={};sums={}
    for value in nums:
        new_count=1+counts.get(value-1,0)+counts.get(value+1,0)
        new_sum=value+sums.get(value-1,0)+counts.get(value-1,0)*value+sums.get(value+1,0)+counts.get(value+1,0)*value
        counts[value]=(counts.get(value,0)+new_count)%modulo
        sums[value]=(sums.get(value,0)+new_sum)%modulo
    return sum(sums.values())%modulo
'''

REDUCIBLE='''def count_k_reducible_below(s,k):
    from math import comb
    modulo=1000000007;length=len(s)
    def steps(value):
        answer=0
        while value!=1:value=value.bit_count();answer+=1
        return answer
    def with_ones(count):
        answer=used=0
        for index,char in enumerate(s):
            if char=='1':
                remaining=length-index-1;needed=count-used
                if 0<=needed<=remaining:answer=(answer+comb(remaining,needed))%modulo
                used+=1
        return answer
    return sum(with_ones(count) for count in range(1,length+1) if steps(count)<k)%modulo
'''

ZERO_ONE='''def can_make_zero_array(nums,queries):
    difference=[0]*(len(nums)+1)
    for left,right in queries:difference[left]+=1;difference[right+1]-=1
    capacity=0
    for index,value in enumerate(nums):
        capacity+=difference[index]
        if value>capacity:return False
    return True
'''

ZERO_TWO='''def minimum_zero_array_queries(nums,queries):
    def possible(count):
        difference=[0]*(len(nums)+1)
        for left,right,value in queries[:count]:difference[left]+=value;difference[right+1]-=value
        capacity=0
        for index,need in enumerate(nums):
            capacity+=difference[index]
            if need>capacity:return False
        return True
    low=0;high=len(queries)+1
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return -1 if low>len(queries) else low
'''

MISSING='''def minimum_missing_adjacent_difference(nums):
    def stabbed(intervals,distance=None):
        if not intervals:return True
        first=min(right for left,right in intervals)
        remaining=[(left,right) for left,right in intervals if left>first]
        if not remaining:return True
        second_left=max(left for left,right in remaining);second_right=min(right for left,right in remaining)
        if second_left>second_right:return False
        return distance is None or second_left-first<=distance
    segments=[];index=0
    while index<len(nums):
        if nums[index]!=-1:index+=1;continue
        start=index
        while index<len(nums) and nums[index]==-1:index+=1
        left=nums[start-1] if start else None;right=nums[index] if index<len(nums) else None
        segments.append((left,right,index-start))
    fixed=max((abs(nums[i]-nums[i-1]) for i in range(1,len(nums)) if nums[i]!=-1 and nums[i-1]!=-1),default=0)
    def possible(limit):
        if fixed>limit:return False
        close=[];separate=[]
        for left,right,length in segments:
            if left is None and right is None:continue
            if left is None:
                interval=(max(1,right-limit),right+limit)
                if close is not None:close.append(interval)
                if separate is not None:separate.append(interval)
            elif right is None:
                interval=(max(1,left-limit),left+limit)
                if close is not None:close.append(interval)
                if separate is not None:separate.append(interval)
            else:
                if close is not None:close.extend(((max(1,left-limit),left+limit),(max(1,right-limit),right+limit)))
                intersection=(max(1,max(left,right)-limit),min(left,right)+limit)
                if length==1:
                    if intersection[0]>intersection[1]:close=None
                    elif close is not None:close.append(intersection)
                if intersection[0]>intersection[1]:separate=None
                elif separate is not None:separate.append(intersection)
        return (close is not None and stabbed(close,limit)) or (separate is not None and stabbed(separate))
    low=fixed;high=10**9
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return low
'''


def lesson(a,b,c,d):return [a,b,c,d]


GOOD_CASES=[[[x for x in values]] for values in [[0],[1],[1,1],[1,2],[2,1],[0,1,2],[1,3,2],[2,3,2],[5,4,3,2],[0,2,1,2],[3,3,4],[1,2,3,2],[8,7,8,7],[0,1,0,1]]]
REDUCIBLE_CASES=[[s,k] for s,k in [('1',1),('10',1),('11',1),('100',1),('101',2),('110',2),('1000',1),('1000',3),('1111',2),('10000',2),('10101',3),('11111',1),('100000',4),('1100100',2)]]
ZERO_ONE_CASES=[[a,q] for a,q in [([0],[[0,0]]),([1],[[0,0]]),([2],[[0,0]]),([2],[[0,0],[0,0]]),([1,1],[[0,1]]),([1,2],[[0,1]]),([0,3,0],[[1,1],[0,2],[1,2]]),([2,1,2],[[0,1],[1,2]]),([1,1,1],[[0,0],[1,1],[2,2]]),([3,0,1],[[0,2],[0,0],[0,0]]),([1,2,1,2],[[0,3],[1,3]]),([5,5],[[0,1]]*5),([0,0,0],[[0,2]]),([2,3,2],[[0,2],[1,1],[0,2]])]]
ZERO_TWO_CASES=[[a,q] for a,q in [([0],[[0,0,1]]),([1],[[0,0,1]]),([2],[[0,0,1]]),([2],[[0,0,1],[0,0,1]]),([1,1],[[0,1,1]]),([1,2],[[0,1,1],[1,1,1]]),([3,0,2],[[0,2,1],[0,0,2],[2,2,1]]),([1,1,1],[[0,0,1],[1,1,1],[2,2,1]]),([5,5],[[0,1,2],[0,1,3]]),([2,4,1],[[0,2,1],[1,1,2],[1,1,1]]),([0,0],[[0,1,5]]),([10],[[0,0,5]]),([4,3,2],[[1,2,2],[0,1,1],[0,0,3]]),([2,2,2],[[0,0,2],[1,2,1],[1,2,1]])]]
MISSING_CASES=[[[x for x in values]] for values in [[-1,-1],[1,2],[1,-1],[1,-1,3],[1,-1,4],[1,-1,-1,7],[-1,10,-1,8],[1,-1,10,-1,1],[5,-1,-1,-1,5],[1,100,-1],[1,-1,-1,100],[3,-1,8,9],[10,-1,1,-1,10],[-1,4,8,-1]]]


BATCH={
3351:entry('sum_good_subsequences',[('nums','list[int]')],'int',['arrays','dynamic programming','hash maps'],['nums has 1–100,000 values in 0..100,000.','A nonempty subsequence is good when every consecutive selected-value difference has absolute value exactly one.','Return the sum of elements over all index-distinct good subsequences modulo 1,000,000,007.'],[([[1,2,1]],'The three singletons and subsequences 1,2; 2,1; and 1,2,1 contribute fourteen.'),([[3,4,5]],'Three singletons, two adjacent pairs, and the full sequence contribute forty.')],GOOD_CASES,GOOD,[GOOD.replace('counts.get(value+1,0)','counts.get(value,0)',1),GOOD.replace('new_sum=value+','new_sum=')],['Extends from equal prior values instead of value+1.','Omits the new value from every singleton and extension sum.'],good_oracle,random_good,lesson('For each ending value, retain both the number of good subsequences and their total element sum.','A new value x starts alone or extends sequences ending at x-1 and x+1.','For each neighbor, add its old sums plus x times its sequence count; accumulate under endpoint x.','These are exactly the legal predecessors, and processing left to right preserves subsequence index order.'),'O(n)','O(distinct values)',8),
3352:entry('count_k_reducible_below',[('s','str'),('k','int')],'int',['dynamic programming','combinatorics','bit manipulation'],['s is a 1–800 digit binary representation without leading zeros and 1 <= k <= 5.','A positive x is k-reducible when at most k repeated popcount operations turn it into one.','Count qualifying x strictly below the represented number, modulo 1,000,000,007.'],[(['111',1],'Below seven, only powers of two 1,2,4 reach one in at most one popcount.'),(['1000',2],'Values one through six qualify; seven needs one additional popcount step.')],REDUCIBLE_CASES,REDUCIBLE,[REDUCIBLE.replace('steps(count)<k','steps(count)<=k'),REDUCIBLE.replace('return answer\n    return sum','if used==count:answer+=1\n        return answer\n    return sum')],['Allows one too many reduction operations after the first popcount.','Counts the upper-bound number itself when its set-bit count matches.'],reducible_oracle,random_reducible,lesson('After the first operation, only the original number’s set-bit count matters.','Precompute reduction depth for each possible count and count smaller binary values with that many ones.','Scan the upper-bound bits; whenever it has one, place zero and choose the remaining ones combinatorially.','The first lower bit partitions all x<s uniquely, and depth(count)+1 gives their exact reduction requirement.'),'O(len(s)²)','O(1)',8),
3355:entry('can_make_zero_array',[('nums','list[int]'),('queries','list[list[int]]')],'bool',['arrays','difference arrays','prefix sums'],['nums and queries each contain up to 100,000 entries.','Each query permits independently decrementing any subset of indices in its inclusive range by one.','Return whether available query coverage can supply every index’s required number of decrements.'],[([[1,0,1],[[0,2]]],'The sole query can select indices zero and two while leaving index one unchanged.'),([[4,3,2,1],[[1,3],[0,2]]],'Index zero is covered only once but needs four decrements, so transformation is impossible.')],ZERO_ONE_CASES,ZERO_ONE,[ZERO_ONE.replace('difference[right+1]-=1','difference[right]-=1'),ZERO_ONE.replace('if value>capacity','if value>=capacity')],['Ends each inclusive range one index too early.','Rejects indices whose available capacity exactly equals their need.'],zero_one_oracle,random_zero_one,lesson('Selections are independent per index, so only the number of covering queries matters.','Accumulate inclusive range coverage with a difference array.','Add at l and subtract after r; prefix-sum capacity and compare it with nums[i].','Every covering query can spend its decrement independently, making coverage at least demand both necessary and sufficient.'),'O(n+q)','O(n)',5),
3356:entry('minimum_zero_array_queries',[('nums','list[int]'),('queries','list[list[int]]')],'int',['arrays','binary search','difference arrays'],['nums and queries each contain up to 100,000 entries; query values are positive.','Within each prefix query, every covered index independently receives any decrement from zero through val.','Return the shortest query prefix whose capacities cover nums, zero if already zero, or -1 if all queries fail.'],[([[2,0,2],[[0,2,1],[0,2,1],[1,1,3]]],'The first query supplies one at indices zero and two; the first two together supply the required two.'),([[4,3,2,1],[[1,3,2],[0,2,1]]],'Even the full prefix supplies only one unit at index zero, below its need four.')],ZERO_TWO_CASES,ZERO_TWO,[ZERO_TWO.replace('low=0;high=len(queries)+1','low=1;high=len(queries)+1'),ZERO_TWO.replace('difference[right+1]-=value','difference[right]-=value')],['Never considers the valid zero-query answer for an already-zero array.','Treats inclusive range endpoints as excluded.'],zero_two_oracle,random_zero_two,lesson('Feasibility is monotone: adding another query never removes decrement capacity.','Binary-search the prefix length and test it with a weighted difference array.','For a candidate prefix, sum range values at each index and require capacity >= nums[i].','Independent per-index decrement choices make the capacity test exact, and monotonicity makes lower-bound search valid.'),'O((n+q) log q)','O(n)',6),
3357:entry('minimum_missing_adjacent_difference',[('nums','list[int]')],'int',['arrays','binary search','interval stabbing'],['nums has 2–100,000 entries, each -1 or a positive integer up to one billion.','Choose two positive integers once and replace every -1 independently with either chosen value.','Minimize the maximum absolute difference between adjacent values.'],[([[1,2,-1,10,8]],'Choosing six and seven allows the missing value to be six, producing maximum adjacent difference four.'),([[-1,-1,-1]],'Choose equal positive values and replace every position identically for maximum difference zero.')],MISSING_CASES,MISSING,[MISSING.replace('if length==1:','if False:'),MISSING.replace('second_left-first<=distance','second_left-first<distance')],['Treats a one-position internal gap like a longer gap that can transition between both chosen values.','Rejects feasible chosen values whose separation equals the allowed difference.'],missing_oracle,random_missing,lesson('For a proposed limit, each known boundary creates an interval of replacement values that can touch it.','Reduce feasibility to stabbing interval families with at most two global values, separating close-value transitions from same-value gap coverage.','Check fixed edges; build boundary and gap-intersection intervals; greedily test two stabbing points, then binary-search the limit.','Two close chosen values can bridge long gaps, while a single-cell gap needs one value in both endpoint intervals; otherwise every gap must use one common covering value.'),'O(n log V)','O(n)',8),
}
