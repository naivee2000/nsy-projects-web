"""Replacement products, drone schedules, palindromes, fast reversals, and majorities."""
from itertools import combinations,permutations
from .import_batch_055 import entry


def product_oracle(args):
    nums=args[0];answer=None
    for replaced in range(len(nums)):
        for value in (-100000,100000):
            changed=nums[:];changed[replaced]=value
            for indices in combinations(range(len(nums)),3):
                result=changed[indices[0]]*changed[indices[1]]*changed[indices[2]]
                answer=result if answer is None else max(answer,result)
    return answer

def random_product(rng):return [[rng.randint(-20,20) for _ in range(rng.randint(3,9))]]

def delivery_oracle(args):
    deliveries,recharge=args;states={(0,0)};hour=0
    while (deliveries[0],deliveries[1]) not in states:
        hour+=1;updated=set(states)
        for first,second in states:
            if hour%recharge[0] and first<deliveries[0]:updated.add((first+1,second))
            if hour%recharge[1] and second<deliveries[1]:updated.add((first,second+1))
        states=updated
    return hour

def random_delivery(rng):return [[rng.randint(1,5),rng.randint(1,5)],[rng.randint(2,7),rng.randint(2,7)]]

def palindrome_oracle(args):
    s,target=args
    choices=sorted({''.join(order) for order in permutations(s) if order==order[::-1] and ''.join(order)>target})
    return choices[0] if choices else ''

def random_palindrome(rng):
    n=rng.randint(1,9);return [''.join(rng.choice('abcd') for _ in range(n)),''.join(rng.choice('abcd') for _ in range(n))]

def reverse_oracle(args):
    s=args[0];values=[]
    for length in range(1,len(s)+1):values.extend((s[:length][::-1]+s[length:],s[:-length]+s[-length:][::-1]))
    return min(values)

def random_reverse(rng):return [''.join(rng.choice('abcdef') for _ in range(rng.randint(1,16)))]

def majority_oracle(args):
    nums,target=args;answer=0
    for left in range(len(nums)):
        count=0
        for right in range(left,len(nums)):
            count+=nums[right]==target;answer+=count*2>right-left+1
    return answer

def random_majority(rng):return [[rng.randint(1,6) for _ in range(rng.randint(1,16))],rng.randint(1,7)]


PRODUCT='''def maximum_product_after_replacement(nums):
    values=sorted(nums);limit=100000
    return max(values[0]*values[1]*limit,values[-2]*values[-1]*limit,values[0]*values[-1]*-limit)
'''

DELIVERY='''def minimum_delivery_time(d,r):
    from math import gcd
    common=r[0]//gcd(r[0],r[1])*r[1]
    def possible(time):
        first=time-time//r[0];second=time-time//r[1];either=time-time//common
        return first>=d[0] and second>=d[1] and either>=d[0]+d[1]
    low=1;high=2*(d[0]+d[1])+max(r)
    while not possible(high):high*=2
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return low
'''

PALINDROME='''def smallest_greater_palindromic_permutation(s,target):
    from collections import Counter
    counts=Counter(s);odd=[character for character,value in counts.items() if value%2]
    if len(odd)>1:return ''
    center=odd[0] if odd else '';half_counts={character:value//2 for character,value in counts.items()};length=len(s)//2
    def build(half):return half+center+half[::-1]
    exact=[];available=half_counts.copy()
    for character in target[:length]:
        if available.get(character,0)==0:break
        available[character]-=1;exact.append(character)
    if len(exact)==length:
        candidate=build(''.join(exact))
        if candidate>target:return candidate
    prefix=[];available=half_counts.copy()
    for character in target[:length]:
        if available.get(character,0)==0:break
        available[character]-=1;prefix.append(character)
    for index in range(len(prefix),-1,-1):
        if index<length:
            for character in 'abcdefghijklmnopqrstuvwxyz':
                if character>target[index] and available.get(character,0):
                    available[character]-=1
                    half=''.join(prefix[:index])+character+''.join(c*available.get(c,0) for c in 'abcdefghijklmnopqrstuvwxyz')
                    return build(half)
        if index:available[prefix[index-1]]=available.get(prefix[index-1],0)+1
    return ''
'''

REVERSE_FAST='''def smallest_string_after_one_reverse_fast(s):
    n=len(s)
    if n<2 or len(set(s))==1:return s
    reverse=s[::-1];moduli=(1000000007,1000000009);base=911382323;powers=[];hashes=[]
    for mod in moduli:
        power=[1]*(n+1)
        for i in range(n):power[i+1]=power[i]*base%mod
        pair=[]
        for text in (s,reverse):
            prefix=[0]*(n+1)
            for i,character in enumerate(text):prefix[i+1]=(prefix[i]*base+ord(character))%mod
            pair.append(prefix)
        powers.append(power);hashes.append(pair)
    def segment(which,left,right,slot):
        mod=moduli[slot];prefix=hashes[slot][which]
        return (prefix[right]-prefix[left]*powers[slot][right-left])%mod
    def prefix_hash(candidate,length,slot):
        first,start1,end1,second,start2,end2=candidate;first_length=end1-start1
        if length<=first_length:return segment(first,start1,start1+length,slot)
        remaining=length-first_length
        return (segment(first,start1,end1,slot)*powers[slot][remaining]+segment(second,start2,start2+remaining,slot))%moduli[slot]
    def character(candidate,index):
        first,start1,end1,second,start2,end2=candidate;first_length=end1-start1
        return (s if first==0 else reverse)[start1+index] if index<first_length else (s if second==0 else reverse)[start2+index-first_length]
    def smaller(first,second):
        low=0;high=n
        while low<high:
            middle=(low+high+1)//2
            if all(prefix_hash(first,middle,slot)==prefix_hash(second,middle,slot) for slot in range(2)):low=middle
            else:high=middle-1
        return low<n and character(first,low)<character(second,low)
    best=(0,0,n,0,n,n)
    minimum=min(s)
    for length in range(1,n+1):
        prefix=(1,n-length,n,0,length,n)
        if character(prefix,0)==minimum and smaller(prefix,best):best=prefix
        suffix=(0,0,n-length,1,0,length)
        if character(suffix,0)==minimum and smaller(suffix,best):best=suffix
    return ''.join(character(best,index) for index in range(n))
'''

MAJORITY='''def count_target_majority_subarrays(nums,target):
    answer=0
    for left in range(len(nums)):
        count=0
        for right in range(left,len(nums)):
            count+=nums[right]==target
            if count*2>right-left+1:answer+=1
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

X_CASES=[[[*values]] for values in ([1,2,3],[-1,-2,-3],[0,10,0],[-5,7,1],[-4,-2,-1,-2],[2,2,2,2],[-10,0,5,6],[100000,-100000,1],[3,-7,4,-8,2],[0,0,0,0],[9,8,-1,-2,-3],[5,-6,7,-8,9,-10])]
D_CASES=[[a,b] for a,b in (([1,1],[2,3]),([2,1],[3,4]),([1,3],[2,3]),([2,2],[3,4]),([4,2],[2,5]),([5,5],[3,4]),([3,2],[7,11]),([6,1],[2,3]),([2,7],[4,6]),([8,3],[5,7]),([10,10],[2,2]),([20,15],[7,9]))]
P_CASES=[[s,t] for s,t in (('a','a'),('aa','aa'),('ab','aa'),('aab','abb'),('aac','aca'),('aabb','baab'),('baba','bbab'),('aabbcc','abccba'),('aaaabb','abaaba'),('aabbccd','abcdcba'),('zzxzzx','xzzxzz'),('aabbccdd','bddccbba'))]
R_CASES=[[s] for s in ('a','ab','ba','abc','cba','abbc','zxy','abcdef','fedcba','banana','cabbaa','zzxyabc')]
M_CASES=[[a,t] for a,t in (([1],1),([1],2),([1,1],1),([1,2],1),([1,2,2,4],2),([1,1,1,2],1),([1,2,3],4),([2,2,1,2,3],2),([5,4,5,5,6],5),([3,3,2,3,2,3],3),([7,8,7,9,7,7],7),([1,2,1,2,1,3,1],1))]

BATCH={
3732:entry('maximum_product_after_replacement',[('nums','list[int]')],'int',['arrays','sorting','greedy'],['nums contains three to 100,000 integers in [-100000,100000].','Replace exactly one element by any integer in that same range.','After replacement, maximize the product of values at three distinct indices.'],[([[-5,7,0]],'Replacing zero by -100000 gives product 3,500,000.'),([[-4,-2,-1,-3]],'Two large-magnitude negatives with a replacement of 100000 give 1,200,000.')],X_CASES,PRODUCT,[PRODUCT.replace('values[0]*values[-1]*-limit','values[0]*values[-1]*limit'),PRODUCT.replace('values[-2]*values[-1]*limit','values[-3]*values[-2]*limit')],['Uses a positive replacement with opposite-signed extremes, making that candidate negative.','Uses the wrong two largest retained elements for a positive replacement.'],product_oracle,random_product,lesson('The replacement appears in an optimal triple and its best value is one of the allowed range endpoints.','After sorting, only the two smallest, two largest, or one smallest plus one largest retained values can maximize the paired factor.','Evaluate those three pair patterns with replacement +100000 or -100000 as appropriate.','For a linear product in the replacement, an endpoint is optimal; the extreme-pair property covers the maximum product of any two retained values or its negation.'),'O(n log n)','O(n)',6),
3733:entry('minimum_delivery_time',[('d','list[int]'),('r','list[int]')],'int',['binary search','math','scheduling'],['d and r each contain exactly two positive values; delivery counts may reach one billion.','Drone i cannot deliver at hours divisible by r[i], and at most one drone delivers per hour.','Return the earliest hour by which both required counts can be scheduled.'],[([[3,1],[2,3]],'Drone one can use hours 1,3,5 and drone two hour 2, completing by hour five.'),([[1,3],[2,2]],'Both drones lose even hours, so four deliveries require the odd hours through seven.')],D_CASES,DELIVERY,[DELIVERY.replace('either=time-time//common','either=time'),DELIVERY.replace('first>=d[0] and second>=d[1]','first>d[0] and second>d[1]')],['Counts hours when both drones recharge as usable union capacity.','Requires each drone to have one unnecessary extra available hour.'],delivery_oracle,random_delivery,lesson('For a candidate time T, count hours available to each drone and hours available to at least one drone.','Individual counts are T-floor(T/rᵢ); union capacity excludes only common recharge multiples, found with the lcm.','The three Hall-style inequalities test feasibility, and binary search finds the first feasible T.','They are necessary for each job set and their union, and with only two drones they are also sufficient for a disjoint assignment.'),'O(log answer)','O(1)',6),
3734:entry('smallest_greater_palindromic_permutation',[('s','str'),('target','str')],'str',['strings','greedy','counting'],['s and target have the same length up to 300 and contain lowercase letters.','Use every character of s to form a palindrome strictly greater than target.','Return the lexicographically smallest valid palindrome, or empty when none exists.'],[(['baba','abba'],'The two palindromes are abba and baab; baab is the smallest one above target.'),(['aac','abb'],'The only palindrome aca is greater than abb.')],P_CASES,PALINDROME,[PALINDROME.replace('if candidate>target','if candidate>=target'),PALINDROME.replace('character>target[index]','character>=target[index]')],['Returns a palindrome equal to target even though the comparison must be strict.','Allows equality at the first changed half position.'],palindrome_oracle,random_palindrome,lesson('A palindrome is determined by a permutation of half the character counts plus the unique odd center, if any.','First test an exactly matching half because its mirrored suffix may already exceed target; otherwise find the next greater half permutation.','Backtrack through the matched half, raise the latest possible position minimally, and sort the remaining half.','Half strings order their palindromes lexicographically except for the exact-half suffix case, which is checked explicitly.'),'O(n·alphabet)','O(n+alphabet)',8),
3735:entry('smallest_string_after_one_reverse_fast',[('s','str')],'str',['strings','rolling hash','binary search'],['s contains one to 100,000 lowercase letters.','Perform exactly one prefix reversal or suffix reversal of any length.','Return the lexicographically smallest obtainable string.'],[(['dcab'],'Reversing the first three letters produces acdb, the smallest result.'),(['abba'],'Reversing the final three letters produces aabb.')],R_CASES,REVERSE_FAST,[REVERSE_FAST.replace('minimum=min(s)','minimum=s[0]'),REVERSE_FAST.replace('range(1,n+1)','range(1,n)')],['Filters candidates using the original first character instead of the global minimum.','Never evaluates reversing the complete string.'],reverse_oracle,random_reverse,lesson('Each candidate is a concatenation of at most two substrings from s and its reversal.','Represent candidates by those segments and compare them with binary-searched longest common prefixes from double rolling hashes.','Inspect every prefix and suffix length, retaining only candidates whose first character can match the global minimum.','The segment representation exactly describes each legal reversal, while hash-based LCP comparison orders two candidates without constructing them.'),'O(n log n)','O(n)',8),
3737:entry('count_target_majority_subarrays',[('nums','list[int]'),('target','int')],'int',['arrays','counting','enumeration'],['nums contains up to 1,000 positive integers.','A subarray qualifies when target appears strictly more than half its length.','Return the total number of qualifying contiguous subarrays.'],[([[1,2,2,3],2],'Five subarrays contain two strictly more than half the time.'),([[1,1,1,1],1],'Every one of the ten subarrays has target one as its majority.')],M_CASES,MAJORITY,[MAJORITY.replace('count*2>right-left+1','count*2>=right-left+1'),MAJORITY.replace('count+=nums[right]==target','count+=nums[right]!=target')],['Counts tied-frequency subarrays even though the majority must be strict.','Counts non-target values instead of occurrences of target.'],majority_oracle,random_majority,lesson('Fixing a left boundary lets the target count update in constant time as the right boundary grows.','Enumerate all right endpoints, increment the count on target matches, and test twice the count against the window length.','Add one exactly when the strict-majority inequality holds.','Every contiguous subarray has one enumerated endpoint pair and its maintained count is exact.'),'O(n²)','O(1)',5),
}
