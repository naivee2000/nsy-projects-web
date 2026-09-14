"""Frequency sums, missing multiples, zero removal, missing ranges, and equalization moves."""
from collections import Counter
from .import_batch_055 import entry

def frequency_oracle(a):
    nums,k=a;c=Counter(nums);return sum(v for v in nums if c[v]%k==0)
def random_frequency(r):return [[r.randint(1,12) for _ in range(r.randint(1,50))],r.randint(1,10)]
def multiple_oracle(a):
    nums,k=a;seen=set(nums);x=k
    while x in seen:x+=k
    return x
def random_multiple(r):return [[r.randint(1,100) for _ in range(r.randint(1,40))],r.randint(1,20)]
def zeros_oracle(a):return int(''.join(c for c in str(a[0]) if c!='0') or '0')
def random_zeros(r):return [r.randint(1,10**12)]
def missing_oracle(a):
    nums=a[0];seen=set(nums);return [v for v in range(min(nums),max(nums)+1) if v not in seen]
def random_missing(r):return [r.sample(range(-30,31),r.randint(1,30))]
def moves_oracle(a):return max(a[0])*len(a[0])-sum(a[0])
def random_moves(r):return [[r.randint(-50,50) for _ in range(r.randint(1,40))]]

FREQUENCY='''def sum_values_with_frequency_divisible_by_k(nums,k):
    from collections import Counter
    counts=Counter(nums)
    return sum(value for value in nums if counts[value]%k==0)
'''
MULTIPLE='''def smallest_missing_positive_multiple(nums,k):
    seen=set(nums);value=k
    while value in seen:value+=k
    return value
'''
ZEROS='''def remove_decimal_zeros(n):
    return int(str(n).replace('0',''))
'''
MISSING='''def missing_values_inside_range(nums):
    seen=set(nums)
    return [value for value in range(min(nums),max(nums)+1) if value not in seen]
'''
MOVES='''def minimum_increment_moves_to_equal(nums):
    target=max(nums)
    return sum(target-value for value in nums)
'''

BATCH={
3712:entry('sum_values_with_frequency_divisible_by_k',[('nums','list[int]'),('k','int')],'int',['arrays','hash maps','counting'],['Count each distinct value in nums.','Include every occurrence of a value when that value’s frequency is divisible by k.','Return the resulting sum, or zero if no frequency qualifies.'],[([[1,2,2,3,3,3,3,4],2],'Twos and threes have divisible frequencies; all their occurrences sum to sixteen.'),([[1,2,3],2],'Every frequency is one, so return zero.')],[[n,k] for n,k in [([1],1),([1],2),([1,2,3],2),([1,1],2),([1,2,2,3,3,3,3,4],2),([2,2,2],3),([1,1,2,2],2),([5,5,5,5],2),([1,2,1,3],2),([0,0,1],2),([4,4,4,2,2],2),([9,8,7],1),([3,3,3,6,6,6],3),([10,10,5],4)]],FREQUENCY,[FREQUENCY.replace('%k==0','%k!=0'),FREQUENCY.replace('value for value in nums','value for value in counts')],['Includes values whose frequencies are not divisible by k.','Adds each qualifying distinct value once rather than every occurrence.'],frequency_oracle,random_frequency,['Build a frequency table.','Scan original occurrences, not only distinct keys.','Include an occurrence exactly when its table count has zero remainder modulo k.','This naturally multiplies each qualifying value by its frequency.'],'O(n)','O(n)',3),
3718:entry('smallest_missing_positive_multiple',[('nums','list[int]'),('k','int')],'int',['arrays','sets','math'],['Consider positive multiples k, 2k, 3k, and so on.','Return the first such multiple absent from nums.','Array values that are not multiples of k do not affect the answer.'],[([[8,2,3,4,6],2],'Two, four, six, and eight are present; ten is the first missing multiple.'),([[1,3,5],2],'Two is absent, so it is returned immediately.')],[[n,k] for n,k in [([1],1),([1],2),([2],2),([8,2,3,4,6],2),([1,3,5],2),([3,6,9],3),([3,9],3),([5,10,20],5),([4,8,12,16],4),([2,4,8],2),([7,14,21],7),([1,2,3,4],1),([10,30],10),([6,12,18,30],6)]],MULTIPLE,[MULTIPLE.replace('value=k','value=1'),MULTIPLE.replace('value+=k','value+=1')],['Starts from one even when one is not a multiple of k.','Checks consecutive integers rather than consecutive multiples.'],multiple_oracle,random_multiple,['Put all input values in a set.','Start with the first positive multiple k.','Advance by exactly k while the candidate is present.','The first absent candidate is the least missing positive multiple.'],'O(n+answer/k)','O(n)',3),
3726:entry('remove_decimal_zeros',[('n','int')],'int',['math','strings'],['Remove every zero digit from the positive integer’s decimal representation.','Keep all nonzero digits in their original order.','Return the resulting integer.'],[([1020030],'Removing zeros leaves the digits 123.'),([7],'A number without zeros is unchanged.')],[[n] for n in [1,7,10,100,101,1020030,9009,1002,123456,1000001,908070,1110,50505,1000000009]],ZEROS,[ZEROS.replace("replace('0','')","replace('0','1')"),ZEROS.replace("str(n)","str(n)[::-1]")],['Replaces zeros with ones instead of removing them.','Reverses the digit order before removing zeros.'],zeros_oracle,random_zeros,['Convert n to its decimal text.','Remove every zero character.','The positive-input guarantee leaves at least one nonzero digit.','Parsing the retained sequence produces the requested integer.'],'O(digits)','O(digits)',3),
3731:entry('missing_values_inside_range',[('nums','list[int]')],'list[int]',['arrays','sets','sorting'],['nums contains unique integers.','Within the inclusive range from its minimum to maximum, return every absent integer.','Return results in increasing order.'],[([[1,4,2,5]],'The range one through five contains only missing value three.'),([[3,4,5]],'Every integer in the range is present, so return an empty list.')],[[x] for x in [[1],[1,4,2,5],[3,4,5],[1,3],[-2,0,2],[5,1],[10,7,8],[-5,-3,-1],[0,2,1,4],[100,105],[-1,1],[9,6,3],[2,5,4],[7,10,8]]],MISSING,[MISSING.replace('range(min(nums),max(nums)+1)','range(min(nums),max(nums)+1,2)'),MISSING.replace('value not in seen','value in seen')],['Checks only every other integer in the range.','Returns present values rather than missing ones.'],missing_oracle,random_missing,['Build a membership set.','Enumerate every integer from minimum through maximum inclusive.','Retain values not found in the set.','Increasing range enumeration gives the required sorted order.'],'O(range+n)','O(n)',3),
3736:entry('minimum_increment_moves_to_equal',[('nums','list[int]')],'int',['arrays','greedy','math'],['One move increments one array element by one.','Return the minimum moves needed to make every element equal.','Values cannot be decreased.'],[([[2,1,3]],'Raise two to three once and one to three twice, totaling three moves.'),([[5,5]],'The values already match, requiring zero moves.')],[[x] for x in [[1],[5,5],[2,1,3],[0,1],[1,2,3,4],[-1,1],[10,0,10],[3,3,2],[5,1,1],[100,99],[0,0,5],[-5,-2,-3],[7,4,6],[9,8,7,6]]],MOVES,[MOVES.replace('target=max(nums)','target=min(nums)'),MOVES.replace('target-value','value-target')],['Targets the minimum even though decrements are unavailable.','Counts decreases to the minimum instead of increments to the maximum.'],moves_oracle,random_moves,['The common target cannot be below the current maximum.','Choosing the maximum avoids unnecessary extra increments.','Each value needs target-value moves independently.','Summing these deficits is achievable and minimal.'],'O(n)','O(1)',3),
}
