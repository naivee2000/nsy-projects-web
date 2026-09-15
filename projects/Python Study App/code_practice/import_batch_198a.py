"""Bitonic sums, prime ranges, kth powers, limited runs, and password scores."""
from math import isqrt
from .import_batch_055 import entry

def bitonic_oracle(a):
    nums=a[0];p=max(range(len(nums)),key=nums.__getitem__);left=sum(nums[:p+1]);right=sum(nums[p:])
    return -1 if left==right else 0 if left>right else 1
def random_bitonic(r):
    p=r.randint(0,12);left=sorted(r.sample(range(1,100),p+1));right=sorted(r.sample(range(1,left[-1]),r.randint(0,min(10,left[-1]-1))),reverse=True)
    return [left+right]
def prime(n):return n>=2 and all(n%d for d in range(2,isqrt(n)+1))
def primes_oracle(a):
    n=a[0];v=int(str(n)[::-1]);return sum(x for x in range(min(n,v),max(n,v)+1) if prime(x))
def random_primes(r):return [r.randint(1,999)]
def roots_oracle(a):
    l,h,k=a;return sum(l<=x**k<=h for x in range(1,h+1))
def random_roots(r):return [r.randint(1,100),r.randint(100,500),r.randint(1,6)]
def limit_oracle(a):
    nums,k=a;return [x for i,x in enumerate(nums) if i<k or x!=nums[i-k]]
def random_limit(r):return [sorted(r.randint(-5,5) for _ in range(r.randint(1,50))),r.randint(1,8)]
def strength_oracle(a):
    return sum(1 if c.islower() else 2 if c.isupper() else 3 if c.isdigit() else 5 for c in set(a[0]))
def random_strength(r):return [''.join(r.choice('abcXYZ019!@#$') for _ in range(r.randint(1,50)))]

BITONIC='''def compare_bitonic_part_sums(nums):
    peak=max(range(len(nums)),key=nums.__getitem__)
    left=sum(nums[:peak+1]);right=sum(nums[peak:])
    return -1 if left==right else 0 if left>right else 1
'''
PRIMES='''def sum_primes_between_reverse(n):
    from math import isqrt
    def prime(value):
        return value>=2 and all(value%d for d in range(2,isqrt(value)+1))
    other=int(str(n)[::-1]);low,high=sorted((n,other))
    return sum(value for value in range(low,high+1) if prime(value))
'''
ROOTS='''def count_kth_powers_in_range(low,high,k):
    if k==1:return high-low+1
    answer=0;x=1
    while x**k<=high:
        if x**k>=low:answer+=1
        x+=1
    return answer
'''
LIMIT='''def limit_sorted_occurrences(nums,k):
    return [value for i,value in enumerate(nums) if i<k or value!=nums[i-k]]
'''
STRENGTH='''def password_strength(password):
    return sum(1 if c.islower() else 2 if c.isupper() else 3 if c.isdigit() else 5 for c in set(password))
'''

BATCH={
3909:entry('compare_bitonic_part_sums',[('nums','list[int]')],'int',['arrays','bitonic arrays'],['nums strictly increases to one peak and then strictly decreases; either side may contain only the peak.','Both part sums include the peak.','Return 0 when the ascending sum is larger, 1 when the descending sum is larger, and -1 on a tie.'],[([[1,3,2,1]],'The ascending part sums to four and the descending part to six, so return one.'),([[1,2,3,2,1]],'Both sides sum to six, so return negative one.')],[[x] for x in [[1],[1,2],[2,1],[1,3,2,1],[1,2,3,2,1],[1,5,4],[4,3,2],[2,7,1],[1,4,9,8,3],[3,10,9,1],[1,6,5,4,3,2],[5,9,2],[2,3,8,7,6],[1,10,2,1]]],BITONIC,[BITONIC.replace('sum(nums[peak:])','sum(nums[peak+1:])'),BITONIC.replace('0 if left>right else 1','1 if left>right else 0')],['Omits the shared peak from the descending part.','Swaps the two greater-sum return codes.'],bitonic_oracle,random_bitonic,['Locate the unique maximum, which is the peak.','Sum through the peak from each side, deliberately including it twice across the two comparisons.','Compare the two totals with the specified three-way codes.','The bitonic invariant makes the maximum index the exact split point.'],'O(n)','O(1)',5),
3918:entry('sum_primes_between_reverse',[('n','int')],'int',['math','prime testing'],['Reverse the decimal digits of positive n, dropping leading zeros created by reversal.','Use the inclusive interval between n and that reversed value.','Return the sum of all primes in the interval.'],[([13],'The interval 13 through 31 contains primes summing to 132.'),([20],'The reverse is two; primes from two through twenty sum to 77.')],[[n] for n in [1,2,10,11,13,20,31,101,107,113,200,503,909,999]],PRIMES,[PRIMES.replace('range(low,high+1)','range(low,high)'),PRIMES.replace('value>=2','value>=1')],['Excludes a prime at the upper endpoint.','Incorrectly treats one as prime.'],primes_oracle,random_primes,['Reverse n through its decimal text.','Test every value in the closed interval for primality.','A candidate is prime when it is at least two and has no divisor through its square root.','Summing exactly the passing candidates implements the definition independently of interval direction.'],'O(range*sqrt(max))','O(1)',5),
3932:entry('count_kth_powers_in_range',[('l','int'),('r','int'),('k','int')],'int',['math','enumeration'],['Count integer values y in the inclusive interval [l,r].','A value qualifies when y=x^k for a positive integer x.','Count each distinct power once.'],[([1,9,3],'The cubes one and eight lie in the interval.'),([4,16,2],'The squares four, nine, and sixteen give three results.')],[[l,h,k] for l,h,k in [(1,1,1),(1,9,3),(4,16,2),(2,7,2),(8,27,3),(9,9,2),(10,100,2),(1,100,1),(50,500,3),(16,81,4),(2,2,5),(100,1000,3),(1,64,6),(65,1000,6)]],ROOTS.replace('low,high','l,r').replace('high-low','r-l').replace('high','r').replace('low','l'),[ROOTS.replace('low,high','l,r').replace('high-low','r-l').replace('high','r').replace('low','l').replace('x**k>=l','x**k>l'),ROOTS.replace('low,high','l,r').replace('high-low','r-l').replace('high','r').replace('low','l').replace('if k==1:return r-l+1','if k==1:return 1')],['Excludes a power equal to the lower endpoint.','Mishandles the k=1 interval where every value qualifies.'],roots_oracle,random_roots,['Enumerate positive bases beginning at one.','Stop after the power exceeds r.','Count powers at least l, with a direct k=1 shortcut.','Positive kth powers increase with the base, so the scan neither skips nor repeats a result.'],'O(r^(1/k))','O(1)',5),
3940:entry('limit_sorted_occurrences',[('nums','list[int]'),('k','int')],'list[int]',['arrays','two pointers'],['nums is sorted and k is positive.','Keep each distinct value min(original frequency,k) times.','Return the retained sequence in its original order.'],[([[1,1,1,2,2,3],2],'The third one is removed while two copies of one and two are retained.'),([[1,1,2],1],'Keeping one copy per run produces one, two.')],[[a,k] for a,k in [([1],1),([1,1],1),([1,1,1,2,2,3],2),([1,1,2],1),([1,2,3],2),([0,0,0],2),([-1,-1,0,0],1),([1,1,1,1],3),([1,2,2,2,3],2),([5,5,6,6,6],4),([1,1,2,2],2),([2,2,2,3,3],1),([0,1,1,1,2],2),([9,9,9,9,10],2)]],LIMIT,[LIMIT.replace('i<k','i<=k'),LIMIT.replace('nums[i-k]','nums[i-1]')],['Keeps k+1 copies at the beginning of a run.','Compares only with the previous value and drops nearly every repeat.'],limit_oracle,random_limit,['Because nums is sorted, equal values form runs.','For index i>=k, retain nums[i] exactly when it differs from nums[i-k].','Earlier indices cannot exceed any frequency cap.','Looking k positions back detects whether k identical copies already occupy the output prefix.'],'O(n)','O(n)',3),
3941:entry('password_strength',[('password','str')],'int',['strings','sets'],['Each distinct lowercase letter is worth one, uppercase letter two, digit three, and character from !@#$ five.','Repeated copies of the same character contribute only once.','Return the total strength.'],[(['aA1!'],'The four distinct character classes contribute 1+2+3+5=11.'),(['aaAA11!!'],'Duplicates do not add points, so the same four unique characters still total eleven.')],[[s] for s in ['a','A','1','!','aA1!','aaAA11!!','abc','XYZ','123','!@#$','a1a1','Aa','0$','abcXYZ019!@#$']],STRENGTH,[STRENGTH.replace('set(password)','password'),STRENGTH.replace('3 if c.isdigit()','1 if c.isdigit()')],['Scores repeated character occurrences more than once.','Awards digits one point instead of three.'],strength_oracle,random_strength,['Convert the password to a set so each character is visited once.','Classify each unique character by lowercase, uppercase, digit, or special.','Add the class weight.','Deduplication before classification enforces the at-most-once rule exactly.'],'O(n)','O(alphabet)',3),
}
