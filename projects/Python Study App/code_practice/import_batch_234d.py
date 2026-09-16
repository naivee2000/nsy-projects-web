"""Greater permutations, scalable parity balance, reversals, digit scores, and array transforms."""
from itertools import permutations
from functools import lru_cache
from .import_batch_055 import entry


def permutation_oracle(args):
    s,target=args
    choices=sorted({''.join(values) for values in permutations(s) if ''.join(values)>target})
    return choices[0] if choices else ''

def random_permutation(rng):
    n=rng.randint(1,8);return [''.join(rng.choice('abcd') for _ in range(n)),''.join(rng.choice('abcd') for _ in range(n))]

def balanced_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            values=set(nums[left:right+1]);even=sum(value%2==0 for value in values)
            if even==len(values)-even:answer=max(answer,right-left+1)
    return answer

def random_balanced(rng):return [[rng.randint(1,15) for _ in range(rng.randint(1,14))]]

def reverse_oracle(args):
    s=args[0];values=[]
    for length in range(1,len(s)+1):
        values.extend((s[:length][::-1]+s[length:],s[:-length]+s[-length:][::-1]))
    return min(values)

def random_reverse(rng):return [''.join(rng.choice('abcdef') for _ in range(rng.randint(1,15)))]

def digit_oracle(args):
    length,total=args
    if total>9*length:return ''
    @lru_cache(None)
    def solve(position,remaining):
        if position==length:return (0,'') if remaining==0 else None
        best=None
        for digit in range(9,-1,-1):
            if position==0 and digit==0:continue
            if digit>remaining:continue
            tail=solve(position+1,remaining-digit)
            if tail is None:continue
            candidate=(digit*digit+tail[0],str(digit)+tail[1])
            if best is None or candidate>best:best=candidate
        return best
    result=solve(0,total);return '' if result is None else result[1]

def random_digit(rng):
    length=rng.randint(1,5);return [length,rng.randint(1,min(25,9*length+3))]

def transform_oracle(args):
    first,second=args;target=second[-1];base=1+sum(abs(a-b) for a,b in zip(first,second));extra=None
    for a,b in zip(first,second):
        for value in range(min(a,b),max(a,b)+1):
            distance=abs(value-target);extra=distance if extra is None else min(extra,distance)
    return base+extra

def random_transform(rng):
    n=rng.randint(1,8);return [[rng.randint(1,20) for _ in range(n)],[rng.randint(1,20) for _ in range(n+1)]]


PERMUTATION='''def smallest_greater_permutation(s,target):
    from collections import Counter
    counts=Counter(s);prefix=[]
    for character in target:
        if counts[character]==0:break
        counts[character]-=1;prefix.append(character)
    for index in range(len(prefix),-1,-1):
        if index<len(target):
            for character in 'abcdefghijklmnopqrstuvwxyz':
                if character>target[index] and counts[character]:
                    counts[character]-=1
                    return ''.join(prefix[:index])+character+''.join(c*counts[c] for c in 'abcdefghijklmnopqrstuvwxyz')
        if index:counts[prefix[index-1]]+=1
    return ''
'''

BALANCED='''def longest_distinct_parity_balanced_subarray_fast(nums):
    n=len(nums);minimum=[0]*(4*(n+1));maximum=[0]*(4*(n+1));lazy=[0]*(4*(n+1))
    def apply(node,value):minimum[node]+=value;maximum[node]+=value;lazy[node]+=value
    def push(node):
        if lazy[node]:apply(node*2,lazy[node]);apply(node*2+1,lazy[node]);lazy[node]=0
    def add(node,left,right,start,end,value):
        if start<=left and right<=end:apply(node,value);return
        push(node);middle=(left+right)//2
        if start<=middle:add(node*2,left,middle,start,end,value)
        if end>middle:add(node*2+1,middle+1,right,start,end,value)
        minimum[node]=min(minimum[node*2],minimum[node*2+1]);maximum[node]=max(maximum[node*2],maximum[node*2+1])
    def first(node,left,right,target):
        if left==right:return left
        push(node);middle=(left+right)//2
        if minimum[node*2]<=target<=maximum[node*2]:return first(node*2,left,middle,target)
        return first(node*2+1,middle+1,right,target)
    last={};current=answer=0
    for index,value in enumerate(nums,1):
        delta=1 if value%2 else -1
        if value in last:add(1,0,n,last[value],n,-delta);current-=delta
        last[value]=index;add(1,0,n,index,n,delta);current+=delta
        answer=max(answer,index-first(1,0,n,current))
    return answer
'''

REVERSE='''def smallest_string_after_one_reverse(s):
    answer=s
    for length in range(1,len(s)+1):
        answer=min(answer,s[:length][::-1]+s[length:],s[:-length]+s[-length:][::-1])
    return answer
'''

DIGITS='''def maximum_digit_square_number(num,sum):
    if sum>9*num:return ''
    nines,remainder=divmod(sum,9)
    return '9'*nines+(str(remainder) if remainder else '')+'0'*(num-nines-(1 if remainder else 0))
'''

TRANSFORM='''def minimum_array_transform_operations(nums1,nums2):
    target=nums2[-1];answer=1;extra=None
    for first,second in zip(nums1,nums2):
        answer+=abs(first-second);low=min(first,second);high=max(first,second)
        distance=0 if low<=target<=high else min(abs(low-target),abs(high-target))
        extra=distance if extra is None else min(extra,distance)
    return answer+extra
'''

def lesson(a,b,c,d):return [a,b,c,d]

P_CASES=[[s,t] for s,t in (('a','a'),('a','b'),('ab','aa'),('ab','ba'),('aab','aba'),('abc','aaa'),('baba','bbab'),('aabc','abca'),('zzxy','zyzz'),('leetcode','eeltcode'),('aabbcc','abcabc'),('dcba','abcd'))]
B_CASES=[[[*values]] for values in ([1],[2],[1,2],[2,4],[1,3],[2,2,3],[1,2,3,2],[2,5,4,5],[3,2,2,5,6],[2,2,4,4,1,3],[1,1,2,2,3,4],[6,7,6,9,8,11,10])]
S_CASES=[[s] for s in ('a','ab','ba','abc','cba','abbc','zxy','abcdef','fedcba','banana','cabbaa','zzxyabc')]
D_CASES=[[n,s] for n,s in ((1,1),(1,9),(1,10),(2,1),(2,16),(3,3),(3,18),(4,10),(4,36),(5,22),(6,49),(8,72))]
T_CASES=[[a,b] for a,b in (([1],[1,1]),([2],[3,4]),([1,3],[2,4,3]),([2,8],[1,7,4]),([5,5],[5,5,5]),([1,10],[10,1,6]),([3,7,2],[5,4,9,6]),([10,20,30],[15,15,25,18]),([2,2,2,2],[1,3,1,3,2]),([9,1,9],[1,9,1,5]),([4,8,12,16],[5,7,13,15,10]),([20,3,17,8,12],[1,9,15,11,20,7]))]

BATCH={
3720:entry('smallest_greater_permutation',[('s','str'),('target','str')],'str',['strings','greedy','counting'],['s and target contain the same one to 300 lowercase-letter positions.','The answer must use exactly the multiset of characters in s.','Return the lexicographically smallest permutation strictly greater than target, or the empty string.'],[(['abc','bba'],'Matching b then increasing the second position to c yields the smallest answer bca.'),(['baba','bbaa'],'bbaa is the greatest permutation, so no strictly greater answer exists.')],P_CASES,PERMUTATION,[PERMUTATION.replace('character>target[index]','character>=target[index]'),PERMUTATION.replace("'abcdefghijklmnopqrstuvwxyz'","'zyxwvutsrqponmlkjihgfedcba'",1)],['Allows equality at the first changed position instead of requiring a greater character.','Tries replacement letters from largest to smallest and loses lexicographic minimality.'],permutation_oracle,random_permutation,lesson('The answer should match target as long as possible, then exceed it by the smallest available character.','Greedily consume an equal prefix, then backtrack from its end until some position can be raised.','At the chosen position take the smallest available larger letter and append all remaining letters in sorted order.','Trying positions from latest to earliest maximizes the equal prefix, and the sorted suffix is minimal once the first greater position is fixed.'),'O(n·alphabet)','O(alphabet+n)',6),
3721:entry('longest_distinct_parity_balanced_subarray_fast',[('nums','list[int]')],'int',['arrays','segment trees','hash maps'],['nums contains up to 100,000 positive integers.','Balance compares counts of distinct even and distinct odd values in a contiguous subarray.','Return the maximum balanced subarray length.'],[([[2,5,4,3]],'The full array has two distinct values of each parity, so its length is four.'),([[3,2,2,5,4]],'The full array has two distinct odd and two distinct even values, so its length is five.')],B_CASES,BALANCED,[BALANCED.replace("if value in last:add(1,0,n,last[value],n,-delta);current-=delta","if False:add(1,0,n,last[value],n,-delta);current-=delta"),BALANCED.replace('return first(node*2,left,middle,target)','return first(node*2+1,middle+1,right,target)')],['Never cancels a value’s previous occurrence, so it counts duplicates.','Searches the right child when the earliest matching balance lies in the left child.'],balanced_oracle,random_balanced,lesson('For every possible left boundary, maintain distinct odd-minus-even count for the current right endpoint.','When a value repeats, remove its old contribution from all earlier eligible left boundaries, then add its new contribution to later boundaries.','A lazy segment tree range-adds those changes and finds the earliest boundary with the current prefix balance.','Equal balances mean the intervening subarray has net distinct-parity count zero; choosing the earliest boundary maximizes its length.'),'O(n log n)','O(n)',8),
3722:entry('smallest_string_after_one_reverse',[('s','str')],'str',['strings','enumeration'],['s contains one to 1,000 lowercase letters.','Perform exactly one operation: reverse a prefix or a suffix of any length from one through n.','Return the lexicographically smallest obtainable string.'],[(['dcab'],'Reversing the first three characters changes dca to acd and produces acdb.'),(['abba'],'Reversing the final three characters produces aabb.')],S_CASES,REVERSE,[REVERSE.replace('range(1,len(s)+1)','range(1,len(s))'),REVERSE.replace("s[:-length]+s[-length:][::-1]","s[:-length]+s[-length:]")],['Never considers reversing the entire string.','Leaves suffix candidates unchanged instead of reversing them.'],reverse_oracle,random_reverse,lesson('There are only two allowed operations for each length.','Enumerate every prefix reversal and every suffix reversal and retain the smallest result.','Include length one and the full string; length one also represents a no-visible-change legal operation.','The enumeration contains every permitted single operation exactly by its side and length, so its minimum is optimal.'),'O(n²)','O(n)',5),
3723:entry('maximum_digit_square_number',[('num','int'),('sum','int')],'str',['greedy','math'],['num is at most 200,000 and sum at most two million.','Return an exactly num-digit positive integer whose digits total sum.','Maximize the sum of squared digits, breaking score ties toward the numerically largest integer; return empty when impossible.'],[([2,3],'Concentrating the sum in the leading digit gives 30 with score nine.'),([2,17],'Digits nine and eight maximize the score, and 98 is the larger tied arrangement.')],D_CASES,DIGITS,[DIGITS.replace('divmod(sum,9)','divmod(sum,8)'),DIGITS.replace("'9'*nines","'9'*max(0,nines-1)")],['Concentrates the sum into eights rather than nines.','Drops one required leading nine while leaving the remaining construction inconsistent.'],digit_oracle,random_digit,lesson('For a fixed digit sum, moving one unit from a smaller positive digit to a larger digit increases the square total.','Concentrate the sum into as many nines as possible, then one remainder, then zeros.','Place the largest digits first to obtain the largest integer among arrangements with the same maximal score.','The convex exchange argument forces this digit multiset, and feasibility is exactly sum≤9·num.'),'O(num)','O(num)',5),
3724:entry('minimum_array_transform_operations',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','greedy'],['nums1 has n values and nums2 has n+1 positive values, with n up to 100,000.','An operation increments or decrements one existing value, or appends a copy of a current value.','Return the minimum operations needed to reach nums2.'],[([[2,8],[1,7,3]],'Two decrements transform the original positions; append two and increment it once, totaling four.'),([[1,3,6],[2,4,5,3]],'Three original-position changes plus one append reach the target in four operations.')],T_CASES,TRANSFORM,[TRANSFORM.replace('answer=1','answer=0'),TRANSFORM.replace('distance=0 if low<=target<=high else min(abs(low-target),abs(high-target))','distance=abs(first-target)')],['Forgets that appending an element itself costs one operation.','Considers only copying the original value and ignores values encountered during its transformation.'],transform_oracle,random_transform,lesson('Changing original position i costs |nums1[i]-nums2[i]| regardless of when a copy is appended.','During that change, any integer between the endpoints appears and can be copied; choose the closest such interval to the new final target.','Add all fixed position costs, one append, and the minimum distance from the target to any transformation interval.','Every strategy must pay the fixed costs and append once, while copying at the closest encountered value constructs the matching upper bound.'),'O(n)','O(1)',6),
}
