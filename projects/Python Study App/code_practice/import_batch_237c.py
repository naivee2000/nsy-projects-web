"""All-ones multiples, balanced digits, product blocks, distinct windows, and envelopes."""
from math import factorial
from .import_batch_055 import entry


def ones_oracle(args):
    k=args[0];value=0
    for length in range(1,k+1):
        value=value*10+1
        if value%k==0:return length
    return -1

def random_ones(rng):return [rng.randint(2,100)]

def balanced(value):
    digits=str(value);return len(digits)>=2 and sum(map(int,digits[::2]))==sum(map(int,digits[1::2]))
def balanced_oracle(args):return sum(balanced(value) for value in range(args[0],args[1]+1))
def random_balanced(rng):
    left=rng.randint(1,4000);return [left,rng.randint(left,min(5000,left+700))]

def blocks_oracle(args):
    mod=10**9+7;answer=0;start=1
    for size in range(1,args[0]+1):
        end=start+size-1;answer=(answer+factorial(end)//factorial(start-1))%mod;start=end+1
    return answer
def random_blocks(rng):return [rng.randint(1,30)]

def distinct_sum_oracle(args):
    nums,k=args;answer=len(nums)+1
    for left in range(len(nums)):
        values=set()
        for right in range(left,len(nums)):
            values.add(nums[right])
            if sum(values)>=k:answer=min(answer,right-left+1);break
    return answer if answer<=len(nums) else -1
def random_distinct_sum(rng):
    n=rng.randint(1,25);return [[rng.randint(1,20) for _ in range(n)],rng.randint(1,80)]

def constrained_oracle(args):
    n,restrictions,diff=args;anchors=[(0,0)]+[tuple(item) for item in restrictions];prefix=[0]
    for value in diff:prefix.append(prefix[-1]+value)
    return max(min(cap+abs(prefix[i]-prefix[index]) for index,cap in anchors) for i in range(n))
def random_constrained(rng):
    n=rng.randint(2,20);indices=rng.sample(range(1,n),rng.randint(1,n-1))
    return [n,[[i,rng.randint(1,30)] for i in indices],[rng.randint(1,10) for _ in range(n-1)]]


ONES='''def smallest_all_ones_multiple_length(k):
    if k%2==0 or k%5==0:return -1
    remainder=0
    for length in range(1,k+1):
        remainder=(remainder*10+1)%k
        if remainder==0:return length
    return -1
'''
ONES_WRONG='''def smallest_all_ones_multiple_length(k):
    if k%2==0:return -1
    return k
'''

BALANCED='''def count_balanced_integers(low,high):
    from functools import lru_cache
    def count(limit):
        if limit<11:return 0
        digits=list(map(int,str(limit)))
        @lru_cache(None)
        def search(position,difference,tight):
            if position==len(digits):return int(difference==0)
            upper=digits[position] if tight else 9;answer=0
            for digit in range(upper+1):
                answer+=search(position+1,difference+(digit if position%2==0 else -digit),tight and digit==upper)
            return answer
        return search(0,0,True)-1
    return count(high)-count(low-1)
'''

BLOCKS='''def sum_increasing_product_blocks(n):
    mod=1000000007;answer=0;next_value=1
    for size in range(1,n+1):
        product=1
        for value in range(next_value,next_value+size):product=product*value%mod
        answer=(answer+product)%mod;next_value+=size
    return answer
'''

WINDOW='''def minimum_distinct_sum_subarray(nums,k):
    counts={};distinct_sum=0;left=0;answer=len(nums)+1
    for right,value in enumerate(nums):
        counts[value]=counts.get(value,0)+1
        if counts[value]==1:distinct_sum+=value
        while distinct_sum>=k:
            answer=min(answer,right-left+1);outgoing=nums[left];counts[outgoing]-=1
            if counts[outgoing]==0:distinct_sum-=outgoing
            left+=1
    return answer if answer<=len(nums) else -1
'''

CONSTRAINED='''def maximum_constrained_sequence_value(n,restrictions,diff):
    infinity=10**30;upper=[infinity]*n;upper[0]=0
    for index,maximum in restrictions:upper[index]=min(upper[index],maximum)
    for index in range(1,n):upper[index]=min(upper[index],upper[index-1]+diff[index-1])
    for index in range(n-2,-1,-1):upper[index]=min(upper[index],upper[index+1]+diff[index])
    return max(upper)
'''

def lesson(a,b,c,d):return [a,b,c,d]

O_CASES=[[k] for k in (2,3,5,7,9,11,13,17,19,21,25,27,37,41)]
B_CASES=[[a,b] for a,b in ((1,10),(1,100),(11,11),(12,21),(120,129),(1234,1234),(1,999),(100,200),(1000,2000),(9990,10020),(1111,1221),(50000,51000),(99999,101000),(1,5000))]
P_CASES=[[n] for n in (1,2,3,4,5,6,7,8,10,12,20,30,50,100)]
W_CASES=[[a,k] for a,k in (([1],1),([1],2),([2,2,3,1],4),([3,2,3,4],5),([5,5,4],5),([1,1,1],1),([1,1,1],2),([1,2,1,2],3),([10,1,10],11),([4,2,4,3],7),([2,3,5,2,1],8),([7,7,1,2,3],10),([1,2,3,4,5],15),([9,1,8,1,7,1],16))]
C_CASES=[[n,r,d] for n,r,d in ((2,[[1,1]],[1]),(3,[[2,1]],[2,2]),(10,[[3,1],[8,1]],[2,2,3,1,4,5,1,1,2]),(8,[[3,2]],[3,5,2,4,2,3,1]),(4,[[1,1]],[2,3,4]),(4,[[3,1]],[5,5,5]),(5,[[2,2]],[1,2,3,4]),(5,[[1,10],[4,1]],[3,3,3,3]),(6,[[2,1],[5,2]],[2,4,1,5,2]),(6,[[1,1],[3,2],[5,1]],[10,1,10,1,10]),(7,[[4,3]],[1,2,3,4,5,6]),(7,[[2,8],[6,2]],[4,4,4,4,4,4]),(8,[[1,2],[4,5],[7,1]],[2,3,1,4,2,5,1]),(9,[[3,10],[5,1],[8,3]],[1,2,3,4,5,6,7,8]))]

BATCH={
3790:entry('smallest_all_ones_multiple_length',[('k','int')],'int',['math','modular arithmetic','hash maps'],['2≤k≤100,000.','The sought positive integer contains only decimal digit one.','Return its digit count, or -1 when no such multiple exists.'],[([3],'The first divisible repunit is 111, which has three digits.'),([7],'111111 is divisible by seven, while every shorter repunit is not.')],O_CASES,ONES,[ONES_WRONG,ONES.replace('range(1,k+1)','range(1,k)')],['Assumes every odd divisor requires exactly k digits and overlooks factors of five.','Stops before testing the kth distinct remainder, missing valid length-k answers.'],ones_oracle,random_ones,lesson('Building the integer itself is unnecessary; only its remainder modulo k matters.','Append a one with remainder=(remainder·10+1) mod k.','At most k nonzero remainders can occur before repetition; return when zero appears.','A repunit exists exactly when k has no factor two or five, and the finite remainder sequence must then reach zero.'),'O(k)','O(1)',5),
3791:entry('count_balanced_integers',[('low','int'),('high','int')],'int',['digit dynamic programming','math'],['1≤low≤high≤10^15.','A balanced integer has at least two digits.','Positions count from one at the left; odd-position and even-position digit sums must match.'],[([1,100],'The balanced values are 11,22,…,99, for a total of nine.'),([120,129],'Only 121 has equal odd- and even-position digit sums.')],B_CASES,BALANCED,[BALANCED.replace('if limit<11:return 0','if limit<1:return 0').replace("return search(0,0,True)-1","return search(0,0,True)"),BALANCED.replace('difference==0','difference==1')],['Counts the all-zero padded value and permits one-digit values.','Accepts numbers whose alternating digit sums differ by one.'],balanced_oracle,random_balanced,lesson('Count valid values up to a bound, then subtract the count below low.','Digit DP tracks position, alternating-sum difference, and whether the prefix is tight to the bound.','Add a digit to the difference at even zero-based positions and subtract it at odd positions; accept final difference zero.','Leading zero padding may swap parity for shorter lengths but equality with zero is invariant under sign, while removing the all-zero value enforces at least two digits after starting at 11.'),'O(d²·d·10)','O(d²)',8),
3792:entry('sum_increasing_product_blocks',[('n','int')],'int',['math','simulation'],['1≤n≤1,000.','Block i multiplies the next i unused positive integers.','Return the sum of the first n block products modulo 1,000,000,007.'],[([3],'The products are 1, 2·3=6, and 4·5·6=120, totaling 127.'),([7],'The seven block products total 6,006,997,207, whose remainder is 6,997,165.')],P_CASES,BLOCKS,[BLOCKS.replace('next_value+=size','next_value+=size+1'),BLOCKS.replace('range(next_value,next_value+size)','range(next_value,next_value+size-1)')],['Skips one integer between consecutive blocks.','Multiplies only size-1 integers in every block.'],blocks_oracle,random_blocks,lesson('The blocks partition the positive integers into lengths one, two, three, and so on.','Maintain the first unused integer and multiply exactly the next block length values.','Add each modular product and advance the first unused integer by the block length.','This visits every required factor once in its unique block and modular reduction preserves the final remainder.'),'O(n²)','O(1)',5),
3795:entry('minimum_distinct_sum_subarray',[('nums','list[int]'),('k','int')],'int',['arrays','hash maps','sliding windows'],['nums contains up to 100,000 positive integers and k is positive.','A window score sums each distinct value exactly once.','Return the shortest score-at-least-k window, or -1 when none exists.'],[([[2,2,3,1],4],'The length-two window [2,3] has distinct sum five.'),([[5,5,4],5],'A single value five already reaches the target.')],W_CASES,WINDOW,[WINDOW.replace('if counts[value]==1:distinct_sum+=value','distinct_sum+=value').replace('if counts[outgoing]==0:distinct_sum-=outgoing','distinct_sum-=outgoing'),WINDOW.replace('if counts[outgoing]==0:distinct_sum-=outgoing','distinct_sum-=outgoing')],['Sums duplicate occurrences instead of distinct values.','Subtracts a value when any copy leaves, even if another copy remains in the window.'],distinct_sum_oracle,random_distinct_sum,lesson('Positive values make the distinct-value score nondecreasing when extending right and nonincreasing when removing left.','Track window frequencies and add or subtract a value only when its frequency crosses zero.','For every right endpoint, shrink left while the score stays at least k and record lengths.','The final feasible window before each shrink failure is the shortest for that right endpoint; scanning all endpoints finds the global minimum.'),'O(n)','O(n)',5),
3796:entry('maximum_constrained_sequence_value',[('n','int'),('restrictions','list[list[int]]'),('diff','list[int]')],'int',['arrays','greedy','dynamic programming'],['2≤n≤100,000; diff has n-1 positive entries.','a[0]=0, every a[i] is nonnegative, and adjacent change is at most diff[i].','Each unique restricted index has an upper bound; maximize the largest attainable value.'],[([10,[[3,1],[8,1]],[2,2,3,1,4,5,1,1,2]],'Propagating all bounds leaves a largest attainable value six.'),([8,[[3,2]],[3,5,2,4,2,3,1]],'The suffix can rise from the restriction to twelve at the final position.')],C_CASES,CONSTRAINED,[CONSTRAINED.replace('for index in range(n-2,-1,-1):upper[index]=min(upper[index],upper[index+1]+diff[index])',''),CONSTRAINED.replace('for index,maximum in restrictions:upper[index]=min(upper[index],maximum)','')],['Propagates constraints only left-to-right, so later restrictions do not cap earlier peaks.','Ignores every explicit upper-bound restriction.'],constrained_oracle,random_constrained,lesson('Every fixed upper bound creates a cone: position i is at most cap plus the path-distance from its anchor.','Initialize anchor caps, propagate reachable upper bounds forward, then backward using diff edge lengths.','The resulting array is the pointwise minimum of all cones; its largest entry is the answer.','The envelope obeys every adjacent bound and anchor cap, and choosing a equal to that envelope attains all its nonnegative values.'),'O(n+r)','O(n)',6),
}
