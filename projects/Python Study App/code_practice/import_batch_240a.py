"""Block reversal, GCD pairing, multiset equalization, digit DP, and arithmetic repair."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import factorial,gcd
from .import_batch_055 import entry


def reverse_oracle(args):
    nums,k=args;size=len(nums)//k;answer=[]
    for block in range(k):
        part=nums[block*size:(block+1)*size]
        for index in range(len(part)-1,-1,-1):answer.append(part[index])
    return answer
def random_reverse(rng):
    k=rng.randint(1,8);size=rng.randint(1,8);return [[rng.randint(-20,20) for _ in range(k*size)],k]

def gcd_oracle(args):
    values=[];largest=None
    for value in args[0]:
        largest=value if largest is None or value>largest else largest
        values.append(gcd(value,largest))
    values=sorted(values);answer=0
    while len(values)>1:answer+=gcd(values.pop(0),values.pop())
    return answer
def random_gcd(rng):return [[rng.randint(1,100) for _ in range(rng.randint(1,30))]]

def equalize_oracle(args):
    first,second=args;combined=Counter(first)+Counter(second)
    if any(count%2 for count in combined.values()):return -1
    target={value:count//2 for value,count in combined.items()};current=Counter(first)
    return sum(max(0,current[value]-target[value]) for value in combined)
def random_equalize(rng):
    n=rng.randint(1,12);return [[rng.randint(1,7) for _ in range(n)],[rng.randint(1,7) for _ in range(n)]]

def monotone_digits(value):
    digits=list(map(int,str(value)))
    return len(digits)==1 or all(digits[i]<digits[i+1] for i in range(len(digits)-1)) or all(digits[i]>digits[i+1] for i in range(len(digits)-1))
def fancy_oracle(args):
    left,right=args
    return sum(monotone_digits(value) or monotone_digits(sum(map(int,str(value)))) for value in range(left,right+1))
def random_fancy(rng):
    left=rng.randint(1,5000);return [left,left+rng.randint(0,300)]

def can_repair(values):
    if len(values)<=2:return True
    for i,j in combinations(range(len(values)),2):
        difference=Fraction(values[j]-values[i],j-i);start=Fraction(values[i])-difference*i
        predicted=[start+difference*index for index in range(len(values))]
        if all(value.denominator==1 for value in predicted) and sum(predicted[index]!=values[index] for index in range(len(values)))<=1:return True
    return False
def arithmetic_oracle(args):
    nums=args[0];answer=1
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            if can_repair(nums[left:right+1]):answer=max(answer,right-left+1)
    return answer
def random_arithmetic(rng):return [[rng.randint(-15,15) for _ in range(rng.randint(1,14))]]

REVERSE='''def reverse_equal_blocks(nums,k):
    size=len(nums)//k;answer=nums[:]
    for start in range(0,len(nums),size):answer[start:start+size]=answer[start:start+size][::-1]
    return answer
'''

GCD_SUM='''def sum_prefix_max_gcd_pairs(nums):
    from math import gcd
    values=[];maximum=0
    for value in nums:
        maximum=max(maximum,value);values.append(gcd(value,maximum))
    values.sort()
    return sum(gcd(values[i],values[-i-1]) for i in range(len(values)//2))
'''

EQUALIZE='''def minimum_cross_swaps_to_equal(nums1,nums2):
    from collections import Counter
    remaining=Counter(nums2);excess=Counter()
    for value in nums1:
        if remaining[value]:remaining[value]-=1
        else:excess[value]+=1
    answer=0
    for count in excess.values():
        if count%2:return -1
        answer+=count//2
    if any(count%2 for count in remaining.values()):return -1
    return answer
'''

FANCY='''def count_fancy_numbers(left,right):
    from functools import lru_cache
    def good_sum(total):
        digits=list(map(int,str(total)))
        return len(digits)==1 or all(digits[i]<digits[i+1] for i in range(len(digits)-1)) or all(digits[i]>digits[i+1] for i in range(len(digits)-1))
    def count(limit):
        if limit<=0:return 0
        digits=list(map(int,str(limit)))
        @lru_cache(None)
        def visit(position,total,previous,state,started,tight):
            if position==len(digits):return int(started and (state!=3 or good_sum(total)))
            upper=digits[position] if tight else 9;answer=0
            for digit in range(upper+1):
                next_tight=tight and digit==upper
                if not started and digit==0:answer+=visit(position+1,total,0,0,False,next_tight);continue
                if not started:next_state=0
                elif state==3:next_state=3
                elif state==0:next_state=1 if digit>previous else 2 if digit<previous else 3
                elif state==1:next_state=1 if digit>previous else 3
                else:next_state=2 if digit<previous else 3
                answer+=visit(position+1,total+digit,digit,next_state,True,next_tight)
            return answer
        return visit(0,0,0,0,False,True)
    return count(right)-count(left-1)
'''

ARITHMETIC='''def longest_arithmetic_after_change(nums):
    n=len(nums)
    if n<=2:return n
    left=[2]*n;right=[2]*n;left[0]=right[-1]=1
    for i in range(2,n):
        if nums[i]-nums[i-1]==nums[i-1]-nums[i-2]:left[i]=left[i-1]+1
    for i in range(n-3,-1,-1):
        if nums[i+1]-nums[i]==nums[i+2]-nums[i+1]:right[i]=right[i+1]+1
    answer=min(3,n)
    for i in range(n):
        answer=max(answer,left[i],right[i])
        if i>0:answer=max(answer,min(n,left[i-1]+1))
        if i+1<n:answer=max(answer,min(n,right[i+1]+1))
        if 0<i<n-1 and (nums[i+1]-nums[i-1])%2==0:
            difference=(nums[i+1]-nums[i-1])//2;length=3
            if i>1 and nums[i-1]-nums[i-2]==difference:length+=left[i-1]-1
            if i<n-2 and nums[i+2]-nums[i+1]==difference:length+=right[i+1]-1
            answer=max(answer,length)
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]
R_CASES=[[a,k] for a,k in (([1,2,4,3,5,6],3),([1],1),([1,2],1),([1,2],2),([1,2,3,4],2),([1,2,3,4],4),([5,4,3,2,1,0],2),([1,1,2,2,3,3],3),([-1,-2,-3,-4],2),([9,8,7,6,5,4,3,2],4),([0,1,0,1,0,1],2),([1,2,3,4,5,6,7,8,9],3),([10,20,30,40,50,60],6),([2,4,6,8,10,12],3),([7,0,7,0],2))]
G_CASES=[[[*v]] for v in ([2,6,4],[1],[2,4],[3,6,9],[5,10,15,20],[7,7,7],[2,3,5,7],[6,4,8,2],[12,18,24,30],[1,2,3,4,5],[9,3,6,12],[10,25,15,20],[8,16,4,32],[11,22,33,44,55],[100,75,50,25])]
E_CASES=[[a,b] for a,b in (([10,20],[20,10]),([1],[1]),([1],[2]),([1,1],[2,2]),([1,2],[1,2]),([1,1,2],[1,2,2]),([1,1,1],[1,1,1]),([1,2,3],[3,2,1]),([1,1,2,2],[3,3,4,4]),([1,2,2],[1,1,2]),([5,5,6,6],[5,6,5,6]),([1,1,1,2],[1,2,2,2]),([7,8,9],[7,8,10]),([0,0],[1,1]),([2,3,2,3],[3,2,3,2]))]
F_CASES=[[a,b] for a,b in ((8,10),(1,1),(9,9),(10,12),(98,102),(120,130),(145,145),(100,110),(200,220),(1,20),(80,99),(300,330),(999,1010),(1234,1250),(5000,5050))]
A_CASES=[[[*v]] for v in ([9,7,5,10,1],[1],[1,2],[1,2,3],[1,2,4],[1,3,8,7,9],[5,5,5,5],[1,4,7,10,20],[10,8,6,5,2],[1,10,3,4,5],[0,2,4,7,8],[3,1,-1,-3],[1,3,5,100,9],[8,6,4,2,1],[2,9,6,8,10])]

BATCH={
3865:entry('reverse_equal_blocks',[('nums','list[int]'),('k','int')],'list[int]',['arrays','two pointers'],['nums is nonempty, k is positive, and len(nums) is divisible by k.','Partition nums into exactly k contiguous blocks of equal length.','Reverse every block and return their concatenation.'],[([[1,2,4,3,5,6],3],'The three length-two blocks reverse to [2,1], [3,4], and [6,5].'),([[1,2,3,4],2],'Two length-two blocks become [2,1,4,3].')],R_CASES,REVERSE,[REVERSE.replace('size=len(nums)//k','size=k'),REVERSE.replace('[::-1]','')],['Uses k as the block length instead of the number of blocks.','Leaves each block in its original order.'],reverse_oracle,random_reverse,lesson('Exactly k equal blocks means each block has length n//k.','Walk block starts in steps of that length and reverse each slice.','Write the reversed slices into a copied array so the input contract stays clear.','The blocks are disjoint and cover every index once, so reversing each produces exactly the required concatenation.'),'O(n)','O(n)',5),
3867:entry('sum_prefix_max_gcd_pairs',[('nums','list[int]')],'int',['arrays','number theory','sorting','two pointers'],['nums is a nonempty array of positive integers.','For each position, store gcd(nums[i], maximum value in nums[0:i+1]).','Sort those values, pair smallest with largest inward, ignore a middle unpaired value, and sum pair gcds.'],[([[2,6,4]],'The derived values are [2,6,2], sorted to [2,2,6]; gcd(2,6)=2 and the middle is ignored.'),([[3,6,9]],'Derived values [3,6,9] pair three with nine for gcd three.')],G_CASES,GCD_SUM,[GCD_SUM.replace('maximum=max(maximum,value);values.append(gcd(value,maximum))','values.append(gcd(value,nums[0]))'),GCD_SUM.replace('values[-i-1]','values[i+1]')],['Uses the first value rather than the evolving prefix maximum.','Pairs neighboring sorted values rather than the smallest with the largest.'],gcd_oracle,random_gcd,lesson('The prefix maximum can be maintained incrementally.','Build each gcd value, sort the derived array, then use symmetric indices from both ends.','Only floor(n/2) pairs contribute, so an odd middle value is naturally skipped.','The construction follows the two prescribed phases exactly; sorted symmetric indices are precisely the requested extreme pairs.'),'O(n log n)','O(n)',5),
3868:entry('minimum_cross_swaps_to_equal',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','greedy','counting'],['nums1 and nums2 have equal positive length.','Reordering within either array is free; swapping one element between arrays costs one.','Return the minimum cross-array swaps needed to make their multisets equal, or -1.'],[([[10,20],[20,10]],'Free reordering already makes the arrays identical, so the cost is zero.'),([[1,1],[2,2]],'One cross swap gives both arrays one 1 and one 2, so the cost is one.')],E_CASES,EQUALIZE,[EQUALIZE.replace('count//2','count'),EQUALIZE.replace('return -1','return answer')],['Counts each excess copy as a separate swap instead of exchanging two-sided excesses.','Ignores odd combined multiplicities and reports a cost for impossible inputs.'],equalize_oracle,random_equalize,lesson('Free internal swaps mean only each array’s multiset matters.','Cancel matching copies, then examine unmatched counts by value on both sides.','Every combined multiplicity must be even; half of each even excess in nums1 must cross and determines the cost.','One cross swap fixes one needed transfer in each direction, so the counted nums1 transfers are both achievable and necessary.'),'O(n)','O(n)',6),
3869:entry('count_fancy_numbers',[('l','int'),('r','int')],'int',['digit dynamic programming','math'],['1≤l≤r≤10^18.','A number is good when its decimal digits are strictly increasing or strictly decreasing; one digit is good.','A number is fancy when it is good or its digit sum is good; count fancy values in the inclusive range.'],[([8,10],'Eight and nine are one-digit good numbers; ten has digit sum one, also good, so all three qualify.'),([145,145],'Digits 1<4<5 are strictly increasing, so 145 is fancy.')],F_CASES,FANCY,[FANCY.replace('state!=3 or good_sum(total)','state!=3 and good_sum(total)'),FANCY.replace('return count(right)-count(left-1)','return count(right)-count(left)')],['Requires both the number and digit sum to be good instead of either one.','Excludes the inclusive left endpoint from the range subtraction.'],fancy_oracle,random_fancy,lesson('Digit DP can track whether the built digits remain increasing, decreasing, undecided, or already invalid.','Also carry the digit sum so an invalid number can still qualify through its sum at the end.','Count valid positive integers up to each bound using tight and started flags, then subtract prefix counts.','The state records exactly the monotonicity history; the terminal union implements “number good or digit sum good,” and prefix subtraction gives the inclusive interval.'),'O(D²S)','O(DS)',8),
3872:entry('longest_arithmetic_after_change',[('nums','list[int]')],'int',['arrays','dynamic programming'],['nums is a nonempty integer array.','Choose a contiguous subarray and change at most one of its elements to any integer.','Return the greatest possible length having one constant adjacent difference.'],[([[9,7,5,10,1]],'Changing ten to three makes the whole array 9,7,5,3,1 with difference -2.'),([[1,2,4]],'Changing four to three makes all three elements arithmetic.')],A_CASES,ARITHMETIC,[ARITHMETIC.replace('difference=(nums[i+1]-nums[i-1])//2','difference=nums[i+1]-nums[i-1]'),ARITHMETIC.replace('answer=max(answer,min(n,left[i-1]+1))','answer=max(answer,left[i-1])')],['Uses the two-step gap as the adjacent difference without halving it.','Fails to extend a left arithmetic run by changing its next endpoint.'],arithmetic_oracle,random_arithmetic,lesson('Precompute unchanged arithmetic-run lengths ending and starting at every position.','A changed element can extend one side by one, or bridge both sides when its neighbors differ by an even amount.','For a bridge, use half the neighbor gap and join matching runs on each side.','Every optimal subarray places its optional change at an endpoint or interior bridge; the precomputed states evaluate all such locations exactly.'),'O(n)','O(n)',7),
}
