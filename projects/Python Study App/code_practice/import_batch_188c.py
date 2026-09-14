"""Number-game, bit, prefix, geometry, and frequency problems for workbook batch 188."""
from collections import Counter
from .import_batch_055 import entry

def game_oracle(a):
    values=a[0][:];out=[]
    while values:
        first=min(values);values.remove(first);second=min(values);values.remove(second);out.extend((second,first))
    return out
def random_game(r):return [[r.randint(1,100) for _ in range(2*r.randint(1,20))]]
def trailing_oracle(a):
    nums=a[0]
    return any((nums[i]|nums[j])&1==0 for i in range(len(nums)) for j in range(i+1,len(nums)))
def random_trailing(r):return [[r.randint(1,100) for _ in range(r.randint(2,30))]]
def missing_oracle(a):
    nums=a[0];total=nums[0]
    for previous,value in zip(nums,nums[1:]):
        if value!=previous+1:break
        total+=value
    values=set(nums)
    while total in values:total+=1
    return total
def random_missing(r):return [[r.randint(1,30) for _ in range(r.randint(1,30))]]
def area_oracle(a):
    best_diagonal=-1;best_area=0
    for length,width in a[0]:
        diagonal=length*length+width*width;area=length*width
        if diagonal>best_diagonal or diagonal==best_diagonal and area>best_area:best_diagonal,best_area=diagonal,area
    return best_area
def random_area(r):return [[[r.randint(1,100) for _ in range(2)] for _ in range(r.randint(1,25))]]
def frequency_oracle(a):
    counts=Counter(a[0]);highest=max(counts.values());return sum(count for count in counts.values() if count==highest)
def random_frequency(r):return [[r.randint(1,20) for _ in range(r.randint(1,80))]]

GAME='''\
def minimum_number_game(nums):
    values=sorted(nums);answer=[]
    for i in range(0,len(values),2):answer.extend((values[i+1],values[i]))
    return answer
'''
TRAILING='''\
def has_pair_or_with_trailing_zero(nums):
    return sum(value%2==0 for value in nums)>=2
'''
MISSING='''\
def smallest_missing_after_sequential_prefix(nums):
    total=nums[0]
    for i in range(1,len(nums)):
        if nums[i]!=nums[i-1]+1:break
        total+=nums[i]
    present=set(nums)
    while total in present:total+=1
    return total
'''
AREA='''\
def largest_area_at_longest_diagonal(dimensions):
    length,width=max(dimensions,key=lambda item:(item[0]*item[0]+item[1]*item[1],item[0]*item[1]))
    return length*width
'''
FREQUENCY='''\
def count_elements_at_maximum_frequency(nums):
    from collections import Counter
    counts=Counter(nums);highest=max(counts.values())
    return sum(count for count in counts.values() if count==highest)
'''

BATCH={
2974:entry('minimum_number_game',[('nums','list[int]')],'list[int]',['arrays','sorting','simulation'],['nums has even length.','Repeatedly remove the smallest remaining value for Alice and then the smallest for Bob.','Append Bob’s value followed by Alice’s value until nums is empty; return the constructed array.'],[([[5,4,2,3]],'Sorted pairs (2,3) and (4,5) are appended in swapped order, yielding [3,2,5,4].'),([[2,5]],'Alice removes two, Bob removes five, and the answer is [5,2].')],[[x] for x in [[1,2],[2,1],[1,1],[5,4,2,3],[2,5],[1,2,3,4,5,6],[6,5,4,3,2,1],[2,2,1,1],[10,3,8,5],[9,9,9,9],[1,100,2,99],[4,1,4,1],[7,3,5,1,9,2],[20,10,30,40]]],GAME,[GAME.replace('(values[i+1],values[i])','(values[i],values[i+1])'),GAME.replace('sorted(nums)','nums')],['Appends Alice before Bob instead of the required reversed order.','Pairs values in input order instead of repeatedly taking minima.'],game_oracle,random_game,['Repeated minimum removals are revealed by sorting all values once.','In each adjacent sorted pair, Alice receives the first and Bob the second.','Append each pair in second-then-first order.','Sorting gives exactly the removal sequence, so swapping each consecutive pair reproduces the game.'],'O(n log n)','O(n)',3),
2980:entry('has_pair_or_with_trailing_zero',[('nums','list[int]')],'bool',['arrays','bit manipulation'],['Choose two different array elements.','Their bitwise OR has a trailing zero exactly when its least-significant bit is zero.','Return whether at least one qualifying pair exists.'],[([[1,2,3,4,5]],'The even values two and four have an even OR, so a qualifying pair exists.'),([[2,4,8,16]],'Any pair of these even values has a trailing zero.')],[[x] for x in [[1,1],[1,2],[2,2],[1,2,3,4,5],[2,4,8,16],[1,3,5],[0,1],[0,2],[7,8,9],[6,3,10],[11,13,14],[100,99],[5,6,7,8],[9,10,12]]],TRAILING,[TRAILING.replace('>=2','>=1'),TRAILING.replace('value%2==0','value%2==1')],['Accepts a single even value even though two distinct elements are required.','Counts odd values, whose OR necessarily ends in one.'],trailing_oracle,random_trailing,['An OR bit is zero only when that bit is zero in both operands.','The trailing bit is zero exactly for even integers.','Therefore test whether nums contains at least two even elements.','Two evens are sufficient, and any qualifying pair must consist of two evens, proving equivalence.'],'O(n)','O(1)',3),
2996:entry('smallest_missing_after_sequential_prefix',[('nums','list[int]')],'int',['arrays','sets','prefixes'],['Start with the longest prefix whose adjacent values increase by exactly one.','Sum every value in that sequential prefix.','Return the smallest integer no less than that sum which does not occur anywhere in nums.'],[([[1,2,3,2,5]],'The sequential prefix 1,2,3 sums to six, which is absent.'),([[3,4,5,1,12,14,13]],'The prefix sum is twelve; twelve, thirteen, and fourteen occur, so return fifteen.')],[[x] for x in [[1],[1,2],[2,1],[1,2,3,2,5],[3,4,5,1,12,14,13],[5,6,7],[2,3,5],[10,10],[1,3,4],[4,5,6,15],[7,8,9,24,25],[1,2,3,6],[9,10,11,30],[2,3,4,9,10]]],MISSING,[MISSING.replace('nums[i-1]+1','nums[i-1]'),MISSING.replace('while total in present','if total in present')],['Extends through equal values instead of consecutive increments.','Skips at most one present integer rather than continuing to the first missing value.'],missing_oracle,random_missing,['Scan only until the first break in the consecutive prefix.','Accumulate that prefix sum while scanning.','Put all array values in a set and increment the sum while it remains present.','The scan finds the specified maximal prefix and the final loop tests candidates in increasing order, so the first returned value is minimal.'],'O(n)','O(n)',3),
3000:entry('largest_area_at_longest_diagonal',[('dimensions','list[list[int]]')],'int',['arrays','geometry','sorting'],['Each rectangle is [length,width].','Choose a rectangle with the greatest diagonal length; compare squared diagonals to avoid square roots.','If diagonals tie, choose the greatest area; return that area.'],[([[[9,3],[8,6]]],'Both squared diagonals are ninety, so the larger area 48 wins.'),([[[3,4],[4,3]]],'The rectangles tie in diagonal and area, so return twelve.')],[[x] for x in [[[1,1]],[[3,4]],[[9,3],[8,6]],[[3,4],[4,3]],[[1,10],[7,7]],[[5,5],[6,4]],[[2,8],[6,6]],[[100,1],[70,70]],[[1,2],[2,1],[3,1]],[[10,10],[14,1]],[[6,8],[9,5]],[[20,15],[24,7]],[[4,4],[5,3],[6,1]],[[9,12],[15,1]]]],AREA,[AREA.replace('item[0]*item[0]+item[1]*item[1]','item[0]+item[1]'),AREA.replace(',item[0]*item[1]',',-item[0]*item[1]')],['Compares side sums rather than Euclidean diagonal lengths.','Chooses the smaller area when diagonals tie.'],area_oracle,random_area,['Squared diagonal length preserves diagonal ordering without floating-point error.','Use a pair key of squared diagonal followed by area.','Select the maximum rectangle under that key and return its area.','Lexicographic maximization implements the primary diagonal rule and then exactly the required tie-break.'],'O(n)','O(1)',3),
3005:entry('count_elements_at_maximum_frequency',[('nums','list[int]')],'int',['arrays','hash maps','counting'],['Count the frequency of every distinct value.','Find the largest frequency attained by any value.','Return the total number of array elements belonging to values with that maximum frequency.'],[([[1,2,2,3,1,4]],'One and two each occur twice, so their four elements are counted.'),([[1,2,3,4,5]],'Every value has maximum frequency one, so all five elements count.')],[[x] for x in [[1],[1,1],[1,2],[1,2,2,3,1,4],[1,2,3,4,5],[3,3,3],[1,1,2,2],[1,1,1,2,2],[5,4,5,4,3],[10,9,8,10],[2,2,3,3,4,4],[7,7,7,8,8,9],[1,2,1,2,1],[4,5,6,4,5]]],FREQUENCY,[FREQUENCY.replace('if count==highest','if count>=1'),FREQUENCY.replace('sum(count','sum(1')],['Counts elements of every value instead of only maximum-frequency values.','Counts qualifying distinct values rather than all their occurrences.'],frequency_oracle,random_frequency,['A frequency table groups all equal elements.','Determine its maximum count.','Add the full count for every key tied at that maximum.','The qualifying groups are disjoint and their stored counts equal their numbers of elements, so the sum is exact.'],'O(n)','O(distinct values)',3),
}
