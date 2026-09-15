"""Bitwise array bounds, frequency intervals, digit products, and increasing runs."""
from collections import Counter
from functools import lru_cache
from .import_batch_055 import entry


def sized_total(n):
    pair_or=0;bit=0
    while 1<<bit<n:
        half=1<<bit;cycle=half*2
        zeros=(n//cycle)*half+min(n%cycle,half)
        pair_or+=(n*n-zeros*zeros)*half;bit+=1
    return n*(n-1)//2*pair_or


def sized_oracle(args):
    s=args[0];n=1
    while sized_total(n+1)<=s:n+=1
    return n


def random_sized(rng):return [rng.randint(0,2_000_000)]


def frequency_oracle(args):
    nums,k,operations=args;answer=0
    for target in range(min(nums)-k,max(nums)+k+1):
        reachable=sum(abs(value-target)<=k for value in nums)
        existing=sum(value==target for value in nums)
        answer=max(answer,min(reachable,existing+operations))
    return answer


def random_frequency(rng):
    return [[rng.randint(1,20) for _ in range(rng.randint(1,9))],rng.randint(0,6),0]


def random_frequency(rng):
    nums=[rng.randint(1,20) for _ in range(rng.randint(1,9))]
    return [nums,rng.randint(0,6),rng.randint(0,len(nums))]


FACTORS={1:(0,0,0,0),2:(1,0,0,0),3:(0,1,0,0),4:(2,0,0,0),5:(0,0,1,0),6:(1,1,0,0),7:(0,0,0,1),8:(3,0,0,0),9:(0,2,0,0)}


def digit_requirements(t):
    values=[]
    for prime in (2,3,5,7):
        count=0
        while t%prime==0:t//=prime;count+=1
        values.append(count)
    return tuple(values) if t==1 else None


def product_oracle(args):
    num,t=args;required=digit_requirements(t)
    if required is None:return '-1'
    value=int(num)
    while 1:
        text=str(value)
        if '0' not in text:
            product=1
            for char in text:product*=int(char)
            if product%t==0:return text
        value+=1


def random_product(rng):
    num=str(rng.randint(10,999));t=1
    for _ in range(rng.randint(0,5)):t*=rng.choice((2,3,5,7))
    if rng.random()<.08:t*=11
    return [num,t]


def increasing_oracle(args):
    nums=args[0];answer=1
    for length in range(1,len(nums)//2+1):
        for start in range(len(nums)-2*length+1):
            first=all(nums[i]<nums[i+1] for i in range(start,start+length-1))
            second=all(nums[i]<nums[i+1] for i in range(start+length,start+2*length-1))
            if first and second:answer=max(answer,length)
    return answer


def random_increasing(rng):return [[rng.randint(-15,15) for _ in range(rng.randint(2,18))]]


SIZED='''def maximum_sized_bitwise_array(s):
    def total(n):
        pair_or=0;bit=0
        while 1<<bit<n:
            half=1<<bit;cycle=half*2
            zeros=(n//cycle)*half+min(n%cycle,half)
            pair_or+=(n*n-zeros*zeros)*half;bit+=1
        return n*(n-1)//2*pair_or
    low=1;high=2
    while total(high)<=s:high*=2
    while low<high:
        middle=(low+high+1)//2
        if total(middle)<=s:low=middle
        else:high=middle-1
    return low
'''

FREQUENCY='''def maximum_frequency_after_operations(nums,k,num_operations):
    from collections import Counter,defaultdict
    existing=Counter(nums);events=defaultdict(int)
    for value in nums:
        events[value-k]+=1;events[value+k+1]-=1;events[value]+=0
    reachable=0;answer=0
    for target,change in sorted(events.items()):
        reachable+=change
        answer=max(answer,min(reachable,existing[target]+num_operations))
    return answer
'''

PRODUCT='''def smallest_zero_free_product_number(num,t):
    from functools import lru_cache
    required=[]
    for prime in (2,3,5,7):
        count=0
        while t%prime==0:t//=prime;count+=1
        required.append(count)
    if t!=1:return '-1'
    factors={1:(0,0,0,0),2:(1,0,0,0),3:(0,1,0,0),4:(2,0,0,0),5:(0,0,1,0),6:(1,1,0,0),7:(0,0,0,1),8:(3,0,0,0),9:(0,2,0,0)}
    def consume(need,digit):return tuple(max(0,need[i]-factors[digit][i]) for i in range(4))
    @lru_cache(None)
    def two_three(a,b):
        if a==0 and b==0:return ()
        best=None
        for digit in (2,3,4,6,8,9):
            da,db=factors[digit][:2];next_state=(max(0,a-da),max(0,b-db))
            if next_state==(a,b):continue
            candidate=tuple(sorted((digit,)+two_three(*next_state)))
            if best is None or (len(candidate),candidate)<(len(best),best):best=candidate
        return best
    def digits_for(need):return tuple(sorted(two_three(need[0],need[1])+(5,)*need[2]+(7,)*need[3]))
    need=tuple(required);prefix_need=[need];first_zero=None
    for index,char in enumerate(num):
        if char=='0':first_zero=index;break
        prefix_need.append(consume(prefix_need[-1],int(char)))
    if first_zero is None and not any(prefix_need[-1]):return num
    limit=len(num)-1 if first_zero is None else first_zero
    for index in range(limit,-1,-1):
        need=prefix_need[index];remaining=len(num)-index-1
        for digit in range(int(num[index])+1,10):
            suffix_digits=digits_for(consume(need,digit))
            if len(suffix_digits)<=remaining:
                return num[:index]+str(digit)+'1'*(remaining-len(suffix_digits))+''.join(map(str,suffix_digits))
    suffix_digits=digits_for(tuple(required));length=max(len(num)+1,len(suffix_digits))
    return '1'*(length-len(suffix_digits))+''.join(map(str,suffix_digits))
'''

INCREASING='''def maximum_adjacent_increasing_length(nums):
    answer=previous=current=0
    for index,value in enumerate(nums):
        current+=1
        if index==len(nums)-1 or value>=nums[index+1]:
            answer=max(answer,current//2,min(previous,current))
            previous,current=current,0
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


SIZED_CASES=[[value] for value in [0,1,2,3,4,9,10,11,50,100,999,10_000,1_000_000,10**12]]
FREQUENCY_CASES=[[a,k,o] for a,k,o in [([1],0,0),([1],5,1),([1,2],0,2),([1,3],1,2),([1,4,5],1,1),([1,4,5],2,2),([5,5,5],0,0),([5,5,10],5,1),([1,10,20],4,3),([2,4,6,8],2,2),([1,2,2,3],1,1),([100,1,100],0,2),([3,9,15],6,2),([1,100],50,1)]]
PRODUCT_CASES=[[num,t] for num,t in [('10',1),('10',2),('11',1),('15',5),('19',2),('99',9),('100',8),('12355',50),('11111',26),('999',16),('222',64),('777',49),('808',15),('9999',2*3*5*7)]]
INCREASING_CASES=[[[x for x in values]] for values in [[1,2],[2,1],[1,2,3,4],[1,3,2,4],[1,2,3,1,2,3],[3,2,1,3,2,1],[1,1,1,1],[1,2,2,3,3,4],[5,6,7,1,2],[1,2,3,4,0,1,2],[0,1,0,1,0,1],[4,3,2,1,2,3,4,5],[1,5,2,3,4,6],[9,8,7,6,5,4]]]


BATCH={
3344:entry('maximum_sized_bitwise_array',[('s','int')],'int',['bit manipulation','binary search','combinatorics'],['0 <= s <= 1,000,000,000,000,000.','For dimensions n³, cell (i,j,k) equals i multiplied by (j OR k), with indices from zero.','Return the largest positive n whose complete cell sum is at most s.'],[([10],'Dimension two sums to three, while dimension three already exceeds ten, so return two.'),([0],'The single cell for n=1 is zero and any larger dimension has positive sum.')],SIZED_CASES,SIZED,[SIZED.replace('zeros*zeros','zeros'),SIZED.replace('total(middle)<=s','total(middle)<s')],['Subtracts only the number of zero-bit values rather than zero-bit ordered pairs.','Uses a strict budget test and rejects dimensions whose sum equals s.'],sized_oracle,random_sized,lesson('The i factor separates from the sum of j OR k over all ordered pairs.','For every bit, count pairs where at least one operand has it set; multiply by sum(i).','Compute zero-bit counts by periodic blocks, form the total, and binary-search the largest feasible n.','Bit contributions are independent and ordered pairs lacking a bit are exactly zero_count², so their complement gives the OR sum.'),'O(log² s)','O(1)',7),
3346:entry('maximum_frequency_after_operations',[('nums','list[int]'),('k','int'),('num_operations','int')],'int',['arrays','sweep line','sorting'],['nums has 1–100,000 values in 1..100,000; k is nonnegative and num_operations is at most len(nums).','Each selected index may change once by any integer in [-k,k], including zero.','Return the largest achievable frequency after exactly num_operations selections.'],[([[1,4,5],1,2],'Changing five to four yields frequency two; the other required selection may add zero.'),([[5,11,20,20],5,1],'The existing pair of twenties already gives frequency two, and the operation may add zero elsewhere.')],FREQUENCY_CASES,FREQUENCY,[FREQUENCY.replace('existing[target]+num_operations','num_operations'),FREQUENCY.replace('events[value+k+1]-=1','events[value+k]-=1')],['Forgets existing target values do not consume change operations.','Ends each reachable interval one coordinate too early.'],frequency_oracle,random_frequency,lesson('A value x can reach every integer target in the interval [x-k,x+k].','Sweep interval events while separately counting values already equal to each candidate target.','At each event coordinate, cap reachable values by existing[target]+available operations.','The sweep gives every target’s convertible population, and only nonmatching members of that population require operations.'),'O(n log n)','O(n)',6),
3347:entry('maximum_large_frequency_after_operations',[('nums','list[int]'),('k','int'),('num_operations','int')],'int',['arrays','sweep line','sorting'],['nums has 1–100,000 values in 1..1,000,000,000; k is nonnegative and num_operations is at most len(nums).','Each index can be selected at most once and changed by an integer in [-k,k].','Return the maximum achievable frequency without iterating across the numeric coordinate range.'],[([[1,4,5],1,2],'One change converts five to four, achieving two equal values.'),([[5,11,20,20],5,1],'Keeping the duplicate twenties and spending the operation harmlessly preserves frequency two.')],FREQUENCY_CASES,FREQUENCY.replace('maximum_frequency_after_operations','maximum_large_frequency_after_operations'),[FREQUENCY.replace('maximum_frequency_after_operations','maximum_large_frequency_after_operations').replace('events[value]+=0',''),FREQUENCY.replace('maximum_frequency_after_operations','maximum_large_frequency_after_operations').replace('existing[target]+num_operations','existing[target]+num_operations+1')],['Omits original values as candidate coordinates, which can miss the benefit of existing duplicates.','Allows one more changed index than num_operations permits.'],frequency_oracle,random_frequency,lesson('Only interval boundaries and original values can change the best target calculation.','Use a sparse difference map so billion-sized coordinates do not affect runtime.','Add +1/-1 reachability events and zero events at original values; sweep sorted coordinates.','Between events reachability and existing frequency are unchanged, so evaluating exactly these sparse points covers every optimum.'),'O(n log n)','O(n)',7),
3348:entry('smallest_zero_free_product_number',[('num','str'),('t','int')],'str',['strings','greedy','number theory'],['num has 2–200,000 digits with no leading zero; 1 <= t <= 100,000,000,000,000.','Return the smallest zero-free decimal number at least num whose digit product is divisible by t.','Return -1 only when t contains a prime factor other than 2, 3, 5, or 7.'],[(['1234',256],'Keeping prefix 1, increasing 2 to 4, and using suffix 88 produces the minimum valid 1488.'),(['12355',50],'The input is already zero-free and its digit product 150 is divisible by 50.')],PRODUCT_CASES,PRODUCT,[PRODUCT.replace('return num\n    limit','return str(int(num)+1)\n    limit'),PRODUCT.replace('range(limit,-1,-1)','range(0,limit+1)')],['Returns the numeric successor instead of preserving an already valid input.','Increases the earliest feasible digit rather than the rightmost one, so the result is not minimal.'],product_oracle,random_product,lesson('A decimal digit contributes only prime factors 2,3,5,7; any other required prime makes the task impossible.','Preserve the longest feasible prefix, increase its rightmost possible digit, then fill the suffix with the smallest factor-covering digits.','Track residual prime exponents across the prefix; test larger digits right-to-left; pack remaining 2/3 exponents optimally and append required 5/7 digits after leading ones.','The rightmost feasible increase minimizes the fixed-length result, and the shortest sorted factor multiset maximizes leading ones in its suffix.'),'O(len(num)+log t)','O(len(num)+log t)',8),
3350:entry('maximum_adjacent_increasing_length',[('nums','list[int]')],'int',['arrays','greedy','runs'],['nums has 2–200,000 integers.','Find two adjacent length-k subarrays such that both are strictly increasing.','Return the largest possible positive k.'],[([[2,5,7,8,9,2,3,4,3,1]],'Increasing runs of lengths five and three meet at the split, supporting adjacent length-three subarrays.'),([[1,2,3,4,4,4,4,5,6,7]],'The first run can split into two length-two pieces, and no construction supports three.')],INCREASING_CASES,INCREASING,[INCREASING.replace('current//2','current'),INCREASING.replace('min(previous,current)','max(previous,current)')],['Uses an entire increasing run for both halves instead of splitting it.','Uses the larger neighboring run even though both adjacent pieces must fit.'],increasing_oracle,random_increasing,lesson('A valid pair either splits one increasing run or lies across the boundary of two consecutive runs.','At each run end, compare half its length with the smaller of this and the previous run length.','Scan maximal increasing runs and update max(current//2, min(previous,current)).','Those are the only two ways adjacent increasing blocks can sit inside the maximal-run partition.'),'O(n)','O(1)',5),
}
