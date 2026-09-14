"""Monobit values, dominant suffixes, bulb toggles, frequency pairs, and vowel trimming."""
from collections import Counter
from .import_batch_055 import entry

def monobit_oracle(a):return sum(v==0 or len(set(bin(v)[2:]))==1 for v in range(a[0]+1))
def random_monobit(r):return [r.randint(0,100000)]
def dominant_oracle(a):
    nums=a[0];return sum(nums[i]*(len(nums)-i-1)>sum(nums[i+1:]) for i in range(len(nums)-1))
def random_dominant(r):return [[r.randint(-30,50) for _ in range(r.randint(2,40))]]
def bulbs_oracle(a):
    on=set()
    for b in a[0]:on.symmetric_difference_update([b])
    return sorted(on)
def random_bulbs(r):return [[r.randint(1,100) for _ in range(r.randint(1,60))]]
def pair_oracle(a):
    c=Counter(a[0]);values=sorted(c)
    return next(([x,y] for x in values for y in values if x!=y and c[x]!=c[y]),[-1,-1])
def random_pair(r):return [[r.randint(1,12) for _ in range(r.randint(2,40))]]
def trim_oracle(a):return a[0].rstrip('aeiou')
def random_trim(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,50)))]

MONOBIT='''def count_monobit_integers(n):
    answer=1;value=1
    while value<=n:
        answer+=1
        value=value*2+1
    return answer
'''
DOMINANT='''def count_dominant_suffix_indices(nums):
    suffix=sum(nums);answer=0
    for i in range(len(nums)-1):
        suffix-=nums[i]
        if nums[i]*(len(nums)-i-1)>suffix:answer+=1
    return answer
'''
BULBS='''def toggled_on_bulbs(bulbs):
    on=set()
    for bulb in bulbs:
        if bulb in on:on.remove(bulb)
        else:on.add(bulb)
    return sorted(on)
'''
PAIR='''def smallest_different_frequency_pair(nums):
    from collections import Counter
    counts=Counter(nums);values=sorted(counts)
    for first in values:
        for second in values:
            if first!=second and counts[first]!=counts[second]:return [first,second]
    return [-1,-1]
'''
TRIM='''def trim_trailing_vowels(s):
    return s.rstrip('aeiou')
'''

BATCH={
3827:entry('count_monobit_integers',[('n','int')],'int',['math','bit manipulation'],['Count integers from zero through n whose binary representation contains only one repeated bit value.','Zero qualifies with representation 0; positive qualifying values are 1, 3, 7, 15, and so on.','Return the total count.'],[([1],'Both zero and one are monobit, so return two.'),([7],'Zero plus one, three, and seven gives four values.')],[[n] for n in [0,2,3,4,6,7,8,14,15,16,31,32,100,999]],MONOBIT,[MONOBIT.replace('answer=1','answer=0'),MONOBIT.replace('value=value*2+1','value*=2')],['Omits zero from the count.','Counts powers of two rather than all-one bit masks.'],monobit_oracle,random_monobit,['Count zero initially.','Positive monobit representations cannot contain zero, so they are all-one masks.','Generate successive masks by value=2*value+1.','Count masks no greater than n.'],'O(log n)','O(1)',3),
3833:entry('count_dominant_suffix_indices',[('nums','list[int]')],'int',['arrays','suffix sums'],['An index before the last is dominant when its value is greater than the average of all following values.','Do not count the final index.','Return the number of dominant indices.'],[([[5,4,3]],'Five exceeds the following average 3.5 and four exceeds three, so both indices count.'),([[1,2,3]],'Neither earlier value exceeds its following average.')],[[x] for x in [[5,4,3],[1,2,3],[1,1],[2,1],[1,2],[0,0,0],[-1,-2,-3],[10,0,0],[3,1,2,0],[5,5,4],[1,10,1],[9,8,7,6],[2,4,1,3],[100,1]]],DOMINANT,[DOMINANT.replace('>suffix','>=suffix'),DOMINANT.replace('len(nums)-1','len(nums)-2')],['Uses greater-than-or-equal instead of strict greater-than.','Never checks the penultimate index.'],dominant_oracle,random_dominant,['Maintain the sum of elements strictly after i.','Avoid floating point by comparing nums[i]*suffix_count with suffix_sum.','Use strict greater-than.','Stop before the final index because its suffix is empty.'],'O(n)','O(1)',3),
3842:entry('toggled_on_bulbs',[('bulbs','list[int]')],'list[int]',['arrays','sets','simulation'],['Each listed bulb ID toggles once in sequence.','Bulbs begin off; a repeated ID alternates between on and off.','Return all IDs left on in increasing order.'],[([[10,30,20,10]],'Ten toggles twice and is off; twenty and thirty remain on.'),([[1,1]],'The same bulb toggles on then off, leaving an empty result.')],[[x] for x in [[1],[1,1],[1,2],[10,30,20,10],[5,5,5],[3,2,1],[1,2,1,2],[100,1,100],[4,4,3],[9,8,9,7],[2,2,2,2],[6,5,6],[1,3,2,3],[7,7,8,8,9]]],BULBS,[BULBS.replace('on.remove(bulb)','pass'),BULBS.replace('return sorted(on)','return sorted(on,reverse=True)')],['Never turns an already-on bulb off.','Returns bulbs in descending order.'],bulbs_oracle,random_bulbs,['Store currently on bulb IDs in a set.','Remove a listed ID if present; otherwise add it.','This symmetric toggle handles any repetition count.','Sort the final on-set for the required output order.'],'O(n log n)','O(n)',3),
3852:entry('smallest_different_frequency_pair',[('nums','list[int]')],'list[int]',['arrays','hash maps','sorting'],['Choose two distinct values having different occurrence frequencies.','Minimize the first value, then minimize the second value under that first choice.','Return the pair, or [-1,-1] if no such values exist.'],[([[1,1,2,2,3,4]],'One is the smallest value; three is the smallest value with a different frequency.'),([[1,1,2,2]],'Both distinct values have equal frequency, so no pair exists.')],[[x] for x in [[1,2],[1,1],[1,1,2,2],[1,1,2],[1,1,2,2,3,4],[3,3,2,1],[5,4,4,5,3],[1,2,2,3,3,3],[9,8,7],[2,2,2,1,1],[4,4,1,2],[6,5,6,4,4,4],[10,10,9],[1,1,1,2,3]]],PAIR,[PAIR.replace('values=sorted(counts)','values=sorted(counts,reverse=True)'),PAIR.replace('counts[first]!=counts[second]','counts[first]==counts[second]')],['Maximizes values instead of returning the smallest pair.','Chooses equal-frequency values.'],pair_oracle,random_pair,['Count occurrences per distinct value.','Sort distinct values increasingly.','Nested scanning in sorted order tests candidate pairs lexicographically.','Return the first pair with unequal counts, or the sentinel if none exists.'],'O(n+d^2)','O(d)',3),
3856:entry('trim_trailing_vowels',[('s','str')],'str',['strings'],['Remove every consecutive vowel from the end of lowercase s.','Do not remove vowels elsewhere in the string.','Return the remaining prefix, which may be empty.'],[(['idea'],'Trailing e and a are removed, leaving id.'),(['apple'],'Only the final e is removed, leaving appl.')],[[s] for s in ['a','b','idea','apple','aeiou','hello','rhythm','queue','code','banana','sky','audio','leetcode','xai']],TRIM,[TRIM.replace("rstrip('aeiou')","lstrip('aeiou')"),TRIM.replace("rstrip('aeiou')","rstrip('aeio')")],['Removes leading rather than trailing vowels.','Fails to remove trailing u.'],trim_oracle,random_trim,['Start from the string end.','Move left while the current character is one of the five vowels.','Keep the prefix through the final nonvowel.','A trailing-strip operation implements exactly that scan.'],'O(n)','O(n)',3),
}
