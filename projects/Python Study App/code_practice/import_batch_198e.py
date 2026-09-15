"""Replacement slots for three candidates retained in quarantine after two attempts."""
from collections import Counter
from math import gcd
from .import_batch_055 import entry

def vowel_oracle(a):
    s=a[0];counts=Counter(c for c in s if c in 'aeiou');first={c:s.index(c) for c in counts};ordered=[]
    for c in sorted(counts,key=lambda c:(-counts[c],first[c])):ordered.extend(c for _ in range(counts[c]))
    it=iter(ordered);return ''.join(next(it) if c in 'aeiou' else c for c in s)
def random_vowels(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,60)))]
def pair_oracle(a):return max((x*y//gcd(x,y)**2 for i,x in enumerate(a[0]) for y in a[0][i+1:]),default=0)
def random_pair(r):return [[r.randint(1,100) for _ in range(r.randint(2,20))]]
def missing_oracle(a):
    nums,lower,upper=a;missing=[x for x in range(lower,upper+1) if x not in set(nums)];out=[]
    for x in missing:
        if out and x==out[-1][1]+1:out[-1][1]=x
        else:out.append([x,x])
    return out
def random_missing(r):
    lower=r.randint(-20,10);upper=r.randint(lower,lower+30);return [[r.randint(lower-10,upper+10) for _ in range(r.randint(0,30))],lower,upper]

VOWELS='''def sort_vowels_by_frequency(s):
    from collections import Counter
    counts=Counter(c for c in s if c in 'aeiou');first={c:s.index(c) for c in counts}
    ordered=[]
    for vowel in sorted(counts,key=lambda c:(-counts[c],first[c])):ordered.extend([vowel]*counts[vowel])
    it=iter(ordered)
    return ''.join(next(it) if c in 'aeiou' else c for c in s)
'''
PAIR='''def maximum_pair_strength(nums):
    from math import gcd
    return max(nums[i]*nums[j]//gcd(nums[i],nums[j])**2 for i in range(len(nums)) for j in range(i+1,len(nums)))
'''
MISSING='''def missing_number_ranges(nums,lower,upper):
    present=sorted(x for x in set(nums) if lower<=x<=upper);answer=[];previous=lower-1
    for value in present+[upper+1]:
        if value>previous+1:answer.append([previous+1,value-1])
        previous=value
    return answer
'''

BATCH={
3913:entry('sort_vowels_by_frequency',[('s','str')],'str',['strings','sorting','hash maps'],['Only vowel positions may change; consonants remain fixed.','Group vowels by decreasing total frequency.','Break equal-frequency ties by the vowel’s first occurrence in s.'],[(['leetcode'],'e occurs three times and o once, so the vowel positions become e,e,e,o and the result is leetcedo.'),(['banana'],'The tied vowels a and a form the only vowel group, so the string is unchanged.')],[[s] for s in ['a','b','leetcode','banana','aeiou','uoiea','bookkeeper','rhythm','education','sequoia','aaeei','eaa','programming','mississippi']],VOWELS,[VOWELS.replace('-counts[c]','counts[c]'),VOWELS.replace('first[c]','-first[c]')],['Sorts vowel groups by increasing frequency.','Reverses the required first-occurrence tie break.'],vowel_oracle,random_vowels,['Count each vowel and record where it first appears.','Sort distinct vowels by negative frequency then first index.','Expand the ordered groups into a stream.','Replace only vowel positions from that stream, leaving consonants untouched.'],'O(n+v log v)','O(n)',5),
4010:entry('maximum_pair_strength',[('nums','list[int]')],'int',['arrays','math','gcd'],['Choose two distinct indices.','Their strength is nums[i]*nums[j] divided by gcd(nums[i],nums[j]) squared.','Return the maximum strength.'],[([[2,3,5]],'The pair three and five is coprime and has strength fifteen.'),([[6,10]],'Their gcd is two, so the strength is sixty divided by four, or fifteen.')],[[x] for x in [[1,1],[2,3,5],[6,10],[4,8],[7,11],[2,4,6],[12,18,25],[5,10,15],[9,27,8],[100,99],[3,6,12,24],[1,100],[16,24,40],[14,21,35]]],PAIR,[PAIR.replace('**2',''),PAIR.replace('max(','min(',1)],['Divides by only one gcd factor.','Returns the minimum pair strength.'],pair_oracle,random_pair,['Enumerate each unordered index pair once.','Compute its gcd.','Divide the product by the square of that gcd using integer arithmetic.','Track the greatest computed strength.'],'O(n^2 log value)','O(1)',5),
4031:entry('missing_number_ranges',[('nums','list[int]'),('lower','int'),('upper','int')],'list[list[int]]',['arrays','sorting','intervals'],['Consider every integer in the inclusive range [lower,upper].','Ignore nums values outside the range and duplicate present values.','Return maximal missing ranges [start,end] in ascending order.'],[([[3,9,7],1,12],'Present values split the missing integers into [1,2], [4,6], [8,8], and [10,12].'),([[1,2,3],1,3],'Every value in the range is present, so return an empty list.')],[[n,l,u] for n,l,u in [([3,9,7],1,12),([1,2,3],1,3),([],1,3),([2],1,3),([1],1,1),([0,4],1,3),([1,1,3],1,3),([-2,0,2],-2,2),([10],1,5),([1,5],1,5),([2,3,4],1,5),([5,4,3,2,1],1,5),([0,1,2,10],1,3),([-10,10],-2,2)]],MISSING,[MISSING.replace('lower<=x<=upper','lower<x<=upper'),MISSING.replace('previous=lower-1','previous=lower')],['Treats a present lower endpoint as absent.','Starts after lower and omits a missing lower endpoint.'],missing_oracle,random_missing,['Sort the distinct present values that lie inside the requested range.','Use sentinels immediately before lower and after upper.','A gap larger than one yields one missing interval.','Scanning in order produces maximal, sorted, nonoverlapping ranges.'],'O(n log n)','O(n)',5),
}
