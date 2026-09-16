"""Beautiful subsequences, weighted modes, bowls, binary palindromes, and inventory windows."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from math import gcd
from .import_batch_055 import entry


def beauty_oracle(args):
    nums=args[0];answer=0
    for size in range(1,len(nums)+1):
        for indices in combinations(range(len(nums)),size):
            values=[nums[i] for i in indices]
            if all(a<b for a,b in zip(values,values[1:])):
                value=0
                for x in values:value=gcd(value,x)
                answer+=value
    return answer%(10**9+7)

def random_beauty(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,10))]]

def modes_oracle(args):
    nums,k=args;answer=0
    for left in range(len(nums)-k+1):
        counts=Counter(nums[left:left+k]);frequency=max(counts.values());mode=min(value for value,count in counts.items() if count==frequency);answer+=frequency*mode
    return answer

def random_modes(rng):
    n=rng.randint(1,20);return [[rng.randint(1,9) for _ in range(n)],rng.randint(1,n)]

def bowls_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        for right in range(left+2,len(nums)):
            answer+=min(nums[left],nums[right])>max(nums[left+1:right])
    return answer

def random_bowls(rng):
    n=rng.randint(3,15);return [rng.sample(range(1,100),n)]

@lru_cache(None)
def binary_palindromes():
    values=[0]
    for length in range(1,51):
        half=(length+1)//2
        for prefix in range(1<<(half-1),1<<half):
            text=bin(prefix)[2:];palindrome=text+text[-1-(length%2)::-1];values.append(int(palindrome,2))
    return tuple(sorted(values))

def palindrome_oracle(args):
    import bisect
    return bisect.bisect_right(binary_palindromes(),args[0])

def random_palindrome(rng):return [rng.randint(0,10**15)]

def inventory_oracle(args):
    arrivals,w,m=args;n=len(arrivals);best=n
    for mask in range(1<<n):
        kept=mask.bit_count()
        if n-kept>=best:continue
        valid=True
        for right in range(n):
            counts=Counter(arrivals[i] for i in range(max(0,right-w+1),right+1) if mask>>i&1)
            if counts and max(counts.values())>m:valid=False;break
        if valid:best=n-kept
    return best

def random_inventory(rng):
    n=rng.randint(1,11);w=rng.randint(1,n);return [[rng.randint(1,5) for _ in range(n)],w,rng.randint(1,w)]


BEAUTY='''def sum_beautiful_subsequences(nums):
    import bisect,math
    mod=10**9+7;maximum=max(nums);phi=list(range(maximum+1))
    for prime in range(2,maximum+1):
        if phi[prime]==prime:
            for value in range(prime,maximum+1,prime):phi[value]-=phi[value]//prime
    buckets={}
    for value in nums:
        root=math.isqrt(value)
        for divisor in range(1,root+1):
            if value%divisor==0:
                buckets.setdefault(divisor,[]).append(value)
                other=value//divisor
                if other!=divisor:buckets.setdefault(other,[]).append(value)
    answer=0
    for divisor,sequence in buckets.items():
        coordinates=sorted(set(sequence));tree=[0]*(len(coordinates)+1);subtotal=0
        def query(index):
            total=0
            while index>0:total+=tree[index];index-=index&-index
            return total%mod
        def add(index,value):
            while index<len(tree):tree[index]=(tree[index]+value)%mod;index+=index&-index
        for value in sequence:
            index=bisect.bisect_left(coordinates,value)+1;ways=(1+query(index-1))%mod;add(index,ways);subtotal=(subtotal+ways)%mod
        answer=(answer+phi[divisor]*subtotal)%mod
    return answer
'''

MODES='''def sum_weighted_window_modes(nums,k):
    import heapq
    counts={};heap=[]
    def change(value,delta):
        counts[value]=counts.get(value,0)+delta;heapq.heappush(heap,(-counts[value],value))
    def weight():
        while -heap[0][0]!=counts.get(heap[0][1],0):heapq.heappop(heap)
        frequency,value=heap[0]
        return -frequency*value
    for value in nums[:k]:change(value,1)
    answer=weight()
    for right in range(k,len(nums)):
        change(nums[right-k],-1);change(nums[right],1);answer+=weight()
    return answer
'''

BOWLS='''def count_bowl_subarrays(nums):
    stack=[];answer=0
    for right,value in enumerate(nums):
        while stack and nums[stack[-1]]<value:
            left=stack.pop()
            if right-left>=2:answer+=1
        if stack and right-stack[-1]>=2:answer+=1
        stack.append(right)
    return answer
'''

PALINDROMES='''def count_binary_palindromes(n):
    if n==0:return 1
    length=n.bit_length();answer=1
    for bits in range(1,length):answer+=1<<((bits+1)//2-1)
    half=(length+1)//2;prefix=n>>(length-half);first=1<<(half-1);answer+=prefix-first
    text=bin(prefix)[2:];candidate=int(text+text[-1-(length%2)::-1],2)
    return answer+(candidate<=n)
'''

INVENTORY='''def minimum_inventory_discards(arrivals,w,m):
    counts={};kept=[False]*len(arrivals);answer=0
    for day,item in enumerate(arrivals):
        expired=day-w
        if expired>=0 and kept[expired]:counts[arrivals[expired]]-=1
        if counts.get(item,0)>=m:answer+=1
        else:kept[day]=True;counts[item]=counts.get(item,0)+1
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

B_CASES=[[x] for x in ([1],[2,1],[1,1],[3,2,1],[1,3,2,4],[2,4,8],[6,3,9],[5,10,15,20],[4,2,8,6],[7,14,21,28],[2,3,5,7],[12,6,18,9,27])]
M_CASES=[[a,k] for a,k in (([1],1),([1,2],1),([1,2],2),([2,2,1],2),([3,1,3,1],3),([5,4,3,2],2),([1,1,1,1],3),([2,3,2,3,4],4),([9,8,7],3),([4,4,5,5,5],3),([1,2,3,4,5],4),([6,1,6,2,6,2],5))]
O_CASES=[[x] for x in ([3,1,2],[1,2,3],[3,2,1],[6,1,2,3,5],[2,5,3,1,4,6],[10,1,9,2,8],[4,2,3,1],[7,3,5,1,6,2,4],[100,50,75],[6,4,1,5,2,3],[9,1,8,2,7,3],[11,5,9,1,8,2,7])]
P_CASES=[[n] for n in (1,2,3,4,5,6,7,8,15,16,12345,10**15)]
I_CASES=[[a,w,m] for a,w,m in (([1],1,1),([1,1],2,1),([1,2,1],2,1),([1,1,1],3,2),([1,2,3,3,3,5],3,2),([2,2,2,2],2,1),([1,2,1,2,1,2],4,2),([5,5,4,5,4,5],3,1),([1,1,2,2,1,1],5,2),([3,1,3,1,3,1,3],3,1),([1,2,3,4,5],5,5),([7,7,7,8,7,7,7],4,2))]

BATCH={
3671:entry('sum_beautiful_subsequences',[('nums','list[int]')],'int',['arrays','number theory','fenwick trees'],['Up to 10,000 positive values no greater than 70,000.','Count every nonempty strictly increasing subsequence by indices.','Sum each subsequence GCD modulo 1,000,000,007.'],[([[1,2,3]],'The GCD contributions of all increasing subsequences sum to ten.'),([[2,4,6]],'All seven nonempty subsequences are increasing and contribute total twelve.')],B_CASES,BEAUTY,[BEAUTY.replace('query(index-1)','query(index)'),BEAUTY.replace('phi[divisor]*subtotal','divisor*subtotal')],['Counts equal values as valid extensions despite strict increase.','Uses the divisor itself instead of Euler phi in the GCD divisor identity.'],beauty_oracle,random_beauty,lesson('For every g, g equals the sum of phi(d) over divisors d of g.','Count increasing subsequences whose every value is divisible by each d, then weight by phi(d).','Bucket values by their divisors; within each bucket use a Fenwick tree over values to count strict increasing subsequences.','Each subsequence enters exactly the buckets dividing its GCD, whose phi weights sum back to that GCD.'),'O(sum tau(nums[i]) log n + V log log V)','O(sum tau(nums[i])+V)',8),
3672:entry('sum_weighted_window_modes',[('nums','list[int]'),('k','int')],'int',['arrays','sliding windows','heaps'],['One to 100,000 positive values.','For each length-k window choose highest frequency, breaking ties by smaller value.','Add mode times its frequency across all windows.'],[([[1,2,2,3],3],'The two windows contribute four each, totaling eight.'),([[1,2,3],2],'Both tied windows select their smaller value, contributing one then two.')],M_CASES,MODES,[MODES.replace('return -frequency*value','return value'),MODES.replace('(-counts[value],value)','(-counts[value],-value)').replace('counts.get(heap[0][1],0)','counts.get(-heap[0][1],0)').replace('return -frequency*value','return frequency*value')],['Adds only the mode value and omits its frequency.','Breaks frequency ties in favor of the larger value.'],modes_oracle,random_modes,lesson('A heap of (-frequency,value) exposes the required mode and tie rule.','Update counts as the window slides and push fresh heap snapshots, discarding stale tops lazily.','Initialize the first window, read its weighted mode, then remove and add one value per shift.','The cleaned heap top always has current maximum frequency and minimum tied value, so every window contributes correctly.'),'O(n log n)','O(n)',5),
3676:entry('count_bowl_subarrays',[('nums','list[int]')],'int',['arrays','monotonic stacks'],['Three to 100,000 distinct positive integers.','Both endpoints must exceed every strictly interior value.','Count contiguous subarrays of length at least three.'],[([[2,5,3,1,4]],'The bowls are [3,1,4] and [5,3,1,4].'),([[5,1,2,3,4]],'The left endpoint five forms bowls ending at two, three, and four.')],O_CASES,BOWLS,[BOWLS.replace('right-left>=2','right-left>=1'),BOWLS.replace('if stack and right-stack[-1]>=2:answer+=1','if False:pass')],['Counts adjacent visible pairs even though bowls need an interior element.','Misses bowls whose left endpoint is the remaining larger stack top.'],bowls_oracle,random_bowls,lesson('A bowl’s endpoints are a visible pair: no interior value reaches the smaller endpoint.','A decreasing stack enumerates each visible pair when the right endpoint arrives.','Count popped smaller endpoints and the surviving larger top, excluding adjacent indices.','Every pair satisfying the interior-maximum rule is exposed exactly once by the monotonic scan.'),'O(n)','O(n)',5),
3677:entry('count_binary_palindromes',[('n','int')],'int',['bit manipulation','combinatorics'],['Zero <= n <= 10^15.','Binary representations have no leading zeros; zero is represented by 0.','Count palindromic representations in the inclusive range.'],[([9],'Zero, one, three, five, seven, and nine are the six palindromes.'),([0],'Zero itself is included and considered palindromic.')],P_CASES,PALINDROMES,[PALINDROMES.replace('candidate<=n','candidate<n'),PALINDROMES.replace('answer=1','answer=0',1)],['Excludes n itself when n is binary-palindromic.','Forgets to count zero.'],palindrome_oracle,random_palindrome,lesson('A length-L binary palindrome is determined by its first ceil(L/2) bits, whose leading bit is one.','Count all shorter lengths, then compare the palindrome mirrored from n’s own leading half.','Add 2^(ceil(L/2)-1) per shorter length, count smaller current-length prefixes, and conditionally include the mirrored candidate.','Prefixes order their mirrored palindromes monotonically, so the prefix count plus one comparison gives the exact inclusive rank.'),'O(log n)','O(log n)',8),
3679:entry('minimum_inventory_discards',[('arrivals','list[int]'),('w','int'),('m','int')],'int',['arrays','hash maps','sliding windows'],['Up to 100,000 arrivals, with one <= m <= w <= n.','Every kept type occurs at most m times in every trailing w-day window.','Discard only on arrival day and minimize discards.'],[([[1,2,1,3,1],4,2],'No four-day window keeps more than two copies of a type.'),([[1,2,3,3,3,4],3,2],'Discard the third consecutive type-three arrival only.')],I_CASES,INVENTORY,[INVENTORY.replace('if expired>=0 and kept[expired]','if expired>=0'),INVENTORY.replace('>=m','>m')],['Removes discarded arrivals from counts as though they had been kept.','Allows m+1 kept copies before discarding.'],inventory_oracle,random_inventory,lesson('For a fixed type, keeping an arrival whenever the current window has room cannot hurt future choices.','Track counts of kept arrivals only and expire the kept decision from exactly w days ago.','Discard when the type count is already m; otherwise mark the arrival kept and increment it.','An earlier kept item expires no later than a current one, so exchanging any optimal discard for the greedy keep never reduces future capacity.'),'O(n)','O(n)',5),
}
