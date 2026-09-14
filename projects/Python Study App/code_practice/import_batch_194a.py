"""Distance race, digit product, character groups, deletions, and digit-index checks."""
from collections import Counter
from .import_batch_055 import entry

def closest_oracle(a):
    x,y,z=a;return 1 if abs(x-z)<abs(y-z) else 2 if abs(y-z)<abs(x-z) else 0
def random_closest(r):return [r.randint(1,100),r.randint(1,100),r.randint(1,100)]
def product_oracle(a):
    d=sorted(map(int,str(a[0])));return d[-1]*d[-2]
def random_product(r):return [r.randint(10,999999999)]
def common_oracle(a):
    c=Counter(a[0]);return max((v for k,v in c.items() if k in 'aeiou'),default=0)+max((v for k,v in c.items() if k not in 'aeiou'),default=0)
def random_common(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,80)))]
def deletions_oracle(a):
    s,k=a;values=sorted(Counter(s).values());return sum(values[:max(0,len(values)-k)])
def random_deletions(r):return [''.join(r.choice('abcdef') for _ in range(r.randint(1,60))),r.randint(1,6)]
def index_oracle(a):return next((i for i,v in enumerate(a[0]) if sum(map(int,str(v)))==i),-1)
def random_index(r):return [[r.randint(0,9999) for _ in range(r.randint(1,40))]]

CLOSEST='''def closest_person(x,y,z):
    first=abs(x-z);second=abs(y-z)
    return 1 if first<second else 2 if second<first else 0
'''
PRODUCT='''def maximum_product_of_two_digits(n):
    digits=sorted(int(char) for char in str(n))
    return digits[-1]*digits[-2]
'''
COMMON='''def most_frequent_vowel_consonant_sum(s):
    from collections import Counter
    counts=Counter(s)
    vowel=max((count for char,count in counts.items() if char in 'aeiou'),default=0)
    consonant=max((count for char,count in counts.items() if char not in 'aeiou'),default=0)
    return vowel+consonant
'''
DELETIONS='''def minimum_deletions_for_k_distinct(s,k):
    from collections import Counter
    frequencies=sorted(Counter(s).values())
    return sum(frequencies[:max(0,len(frequencies)-k)])
'''
INDEX='''def smallest_digit_sum_index(nums):
    for i,value in enumerate(nums):
        if sum(int(char) for char in str(value))==i:return i
    return -1
'''

BATCH={
3516:entry('closest_person',[('x','int'),('y','int'),('z','int')],'int',['math','simulation'],['Two people at x and y move toward the person at z at equal speed.','Return 1 if x is closer, 2 if y is closer, and 0 for equal distances.','Use absolute number-line distance.'],[([2,7,4],'Distances to four are two and three, so person one arrives first.'),([1,5,3],'Both people are two units away, so return zero.')],[[x,y,z] for x,y,z in [(1,2,3),(3,2,1),(1,5,3),(2,7,4),(10,1,6),(4,9,8),(100,1,50),(5,6,5),(7,7,2),(1,100,99),(20,30,25),(8,2,4),(9,3,8),(11,1,6)]],CLOSEST,[CLOSEST.replace('abs(x-z)','x-z'),CLOSEST.replace('return 1 if first<second else 2 if second<first else 0','return 2 if first<second else 1 if second<first else 0')],['Uses signed displacement rather than distance.','Swaps the winning person labels.'],closest_oracle,random_closest,['Compute each absolute distance to z.','The smaller distance arrives first because speeds match.','Return the matching label, or zero when equal.','No movement simulation is needed because time is proportional to distance.'],'O(1)','O(1)',3),
3536:entry('maximum_product_of_two_digits',[('n','int')],'int',['math','digits','sorting'],['Choose two digit occurrences from positive integer n.','Return the maximum product of the chosen digits.','Two equal digits may be used only when they occur in two positions.'],[([31],'The only product is three times one, equal to three.'),([999],'Two occurrences of nine produce product eighty-one.')],[[n] for n in [10,11,12,31,90,99,101,123,909,999,1203,5555,987654,4004]],PRODUCT,[PRODUCT.replace('digits[-1]*digits[-2]','digits[0]*digits[1]'),PRODUCT.replace('digits[-2]','digits[-1]')],['Multiplies the two smallest digits.','Reuses the single greatest digit regardless of its multiplicity.'],product_oracle,random_product,['Extract all decimal digit occurrences.','Sort them by value.','The product of the two largest nonnegative digits is maximal.','Using the final two positions respects multiplicity.'],'O(d log d)','O(d)',3),
3541:entry('most_frequent_vowel_consonant_sum',[('s','str')],'int',['strings','hash maps','counting'],['Count lowercase letters in s.','Find the greatest vowel frequency and greatest consonant frequency separately.','Return their sum, using zero when either group is absent.'],[(['successes'],'The most frequent vowel and consonant occur three times each, totaling six.'),(['aeiou'],'The greatest vowel frequency is one and no consonant exists, totaling one.')],[[s] for s in ['a','b','aeiou','bcdf','successes','banana','mississippi','aaaaab','zzzzaa','hello','queue','rhythm','abcabc','leetcode']],COMMON,[COMMON.replace("char not in 'aeiou'","char in 'aeiou'"),COMMON.replace('vowel+consonant','max(vowel,consonant)')],['Counts vowels for both groups.','Returns only the larger group frequency rather than their sum.'],common_oracle,random_common,['Build one character frequency table.','Take the maximum count among vowel keys.','Independently take the maximum among all other lowercase letters.','Defaults of zero correctly handle a missing group.'],'O(n)','O(1)',3),
3545:entry('minimum_deletions_for_k_distinct',[('s','str'),('k','int')],'int',['strings','hash maps','greedy'],['Delete characters so at most k distinct letters remain.','Return the minimum number of deleted character occurrences.','You may choose which letter groups to remove.'],[(['abc',2],'Deleting any one character leaves two distinct letters, costing one.'),(['aabbcc',2],'Delete one two-character group, costing two.')],[[s,k] for s,k in [('a',1),('abc',2),('abc',3),('aabbcc',2),('aaabbc',1),('aaaa',1),('abac',2),('mississippi',2),('leetcode',3),('xyzxyz',1),('aabbbbcc',2),('abcdef',5),('banana',2),('qqqwwert',3)]],DELETIONS,[DELETIONS.replace('sorted(','sorted(',1).replace('frequencies=sorted(Counter(s).values())','frequencies=sorted(Counter(s).values(),reverse=True)'),DELETIONS.replace('len(frequencies)-k','k')],['Deletes the largest-frequency groups first.','Deletes k groups rather than the excess distinct groups.'],deletions_oracle,random_deletions,['Count occurrences per distinct letter.','If too many groups exist, entire letter groups must be removed.','Delete the smallest frequencies until only k groups remain.','This exchange-optimal choice minimizes removed characters.'],'O(n+d log d)','O(d)',3),
3550:entry('smallest_digit_sum_index',[('nums','list[int]')],'int',['arrays','digits'],['For each array position i, sum the decimal digits of nums[i].','Return the smallest index whose digit sum equals i.','Return -1 if no index qualifies.'],[([[1,3,2]],'At index two, value two has digit sum two; earlier indices do not match.'),([[0,10,20]],'Index zero matches the digit sum of zero, so it is returned immediately.')],[[x] for x in [[1],[0],[1,3,2],[0,10,20],[9,1],[5,10,2],[99,8,7,6],[10,1,11],[3,12,30,3],[100,1,2,3],[8,8,8,8,4],[50,40,30,20,10,5],[7,6,5,4,3,2,1],[999,0,2]]],INDEX,[INDEX.replace('==i','!=i'),INDEX.replace('return i','return value')],['Accepts a mismatching digit sum.','Returns the array value rather than its index.'],index_oracle,random_index,['Scan indices from zero upward.','Compute the decimal digit sum of the current value.','Return immediately on equality with the index.','Left-to-right early return guarantees the smallest qualifying index.'],'O(total digits)','O(1)',3),
}
