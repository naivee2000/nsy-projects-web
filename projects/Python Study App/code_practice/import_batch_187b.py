"""Easy parity, interval, rotation, and bit-count problems for workbook batch 187."""
from .import_batch_055 import entry

def parity_oracle(a):
    s,t=a
    return sorted((s[0],s[2]))==sorted((t[0],t[2])) and sorted((s[1],s[3]))==sorted((t[1],t[3]))
def random_parity(r):return [''.join(r.choice('abcd') for _ in range(4)),''.join(r.choice('abcd') for _ in range(4))]
def symmetric(n):
    s=str(n)
    return len(s)%2==0 and sum(map(int,s[:len(s)//2]))==sum(map(int,s[len(s)//2:]))
def symmetric_oracle(a):return sum(symmetric(n) for n in range(a[0],a[1]+1))
def random_symmetric(r):
    lo=r.randint(1,9000);return [lo,r.randint(lo,min(10000,lo+500))]
def points_oracle(a):return len({x for left,right in a[0] for x in range(left,right+1)})
def random_points(r):return [[[min(x,y),max(x,y)] for x,y in ((r.randint(1,100),r.randint(1,100)) for _ in range(r.randint(1,20)))]]
def shifts_oracle(a):
    nums=a[0]
    for k in range(len(nums)):
        shifted=nums[-k:]+nums[:-k] if k else nums[:]
        if all(x<=y for x,y in zip(shifted,shifted[1:])):return k
    return -1
def random_shifts(r):return [[r.randint(-20,20) for _ in range(r.randint(1,30))]]
def bit_index_oracle(a):return sum(value for index,value in enumerate(a[0]) if bin(index).count('1')==a[1])
def random_bit_index(r):return [[r.randint(-50,50) for _ in range(r.randint(1,80))],r.randint(0,7)]

PARITY='''\
def can_swap_same_parity_indices(s1,s2):
    return sorted(s1[::2])==sorted(s2[::2]) and sorted(s1[1::2])==sorted(s2[1::2])
'''
SYMMETRIC='''\
def count_symmetric_integers(low,high):
    answer=0
    for value in range(low,high+1):
        digits=str(value);half=len(digits)//2
        if len(digits)%2==0 and sum(map(int,digits[:half]))==sum(map(int,digits[half:])):answer+=1
    return answer
'''
POINTS='''\
def count_covered_integer_points(intervals):
    covered=set()
    for left,right in intervals:covered.update(range(left,right+1))
    return len(covered)
'''
SHIFTS='''\
def minimum_right_shifts_to_sort(nums):
    drops=[i for i in range(len(nums)) if nums[i]>nums[(i+1)%len(nums)]]
    if not drops:return 0
    if len(drops)>1:return -1
    shift=len(nums)-1-drops[0]
    return shift
'''
BIT_INDEX='''\
def sum_at_k_set_bit_indices(nums,k):
    return sum(value for index,value in enumerate(nums) if index.bit_count()==k)
'''

BATCH={
2839:entry('can_swap_same_parity_indices',[('s1','str'),('s2','str')],'bool',['strings','sorting','parity'],['Both strings contain exactly four lowercase characters.','An operation may swap positions zero and two or positions one and three any number of times.','Return whether s1 can be transformed into s2.'],[(['abcd','cdab'],'Swapping both even positions and both odd positions changes abcd into cdab.'),(['abcd','dacb'],'The character groups available at even and odd positions do not match.')],[[a,b] for a,b in [('abcd','abcd'),('abcd','cbad'),('abcd','adcb'),('aaaa','aaaa'),('aabb','bbaa'),('abca','aacb'),('xyxy','xyxy'),('xyxy','yxyx'),('zzab','azzb'),('code','edoc'),('abab','baba'),('abcc','cbca'),('wxyz','yxwz'),('aabc','aacb')]],PARITY,[PARITY.replace('and sorted','or sorted'),PARITY.replace('s2[1::2]','s2[::2]')],['Accepts when only one parity group matches.','Compares the odd-position characters against the wrong target group.'],parity_oracle,random_parity,['Allowed swaps never move a character between even and odd indices.','Within each two-position parity group, arbitrary order is reachable.','Sort and compare the two even-position multisets and the two odd-position multisets.','Matching both invariant groups is necessary, and the permitted swap realizes either ordering inside each group, so it is sufficient.'],'O(1)','O(1)',3),
2843:entry('count_symmetric_integers',[('low','int'),('high','int')],'int',['math','digits','enumeration'],['A positive integer is symmetric when it has an even number of decimal digits.','The digit sum of its first half must equal the digit sum of its second half.','Count symmetric integers in the inclusive range low through high.'],[([1,100],'The nine two-digit repeated-digit numbers 11 through 99 are symmetric.'),([1200,1230],'Only 1203 and 1212 have matching half sums in this range.')],[[a,b] for a,b in [(1,1),(10,10),(11,11),(12,12),(98,99),(99,100),(100,999),(1000,1000),(1001,1001),(9999,10000),(200,300),(5000,5100),(1,10),(90,120)]],SYMMETRIC,[SYMMETRIC.replace('len(digits)%2==0','True'),SYMMETRIC.replace('==sum(map(int,digits[half:]))','!=sum(map(int,digits[half:]))')],['Incorrectly permits odd digit lengths.','Counts unequal half sums instead of equal ones.'],symmetric_oracle,random_symmetric,['Inspect every integer because the workbook domain ends at ten thousand.','Reject odd digit counts before comparing halves.','Split the decimal representation in the middle and compare the two digit sums.','The loop visits every value in the inclusive range once, and the predicate is exactly the definition.'],'O((high-low+1)*digits)','O(digits)',3),
2848:entry('count_covered_integer_points',[('intervals','list[list[int]]')],'int',['arrays','intervals','sets'],['Each closed interval [start,end] marks every integer point from start through end.','Intervals may overlap or touch.','Return the number of distinct marked integer points.'],[([[[3,6],[1,5],[4,7]]],'Together the intervals cover every integer from one through seven.'),([[[1,3],[5,8]]],'The disjoint intervals contain three and four integer points, totaling seven.')],[[x] for x in [[[1,1]],[[1,2]],[[1,1],[1,1]],[[1,2],[2,3]],[[1,2],[3,4]],[[10,20]],[[1,100]],[[5,5],[7,7]],[[3,6],[1,5],[4,7]],[[1,3],[5,8]],[[20,30],[25,40]],[[2,4],[8,10],[3,9]],[[99,100]],[[1,10],[1,10],[1,10]]]],POINTS,[POINTS.replace('range(left,right+1)','range(left,right)'),POINTS.replace('return len(covered)','return sum(right-left+1 for left,right in intervals)')],['Treats closed interval endpoints as excluded.','Adds interval lengths without removing overlap duplicates.'],points_oracle,random_points,['A set directly represents distinct covered integer coordinates.','For every interval, add the inclusive range start through end.','Return the final set size.','Every covered coordinate is inserted at least once, and set uniqueness ensures overlapping intervals contribute it only once.'],'O(total covered lengths)','O(number of coordinates)',3),
2855:entry('minimum_right_shifts_to_sort',[('nums','list[int]')],'int',['arrays','circular arrays'],['A right shift removes the last element and inserts it at the front.','Return the minimum number of right shifts needed to make nums nondecreasing.','Return -1 if no rotation of nums is nondecreasing.'],[([[3,4,5,1,2]],'Two right shifts rotate the final 1,2 prefix into place.'),([[2,1,4]],'No rotation removes both descending boundaries, so the result is -1.')],[[x] for x in [[1],[1,2],[2,1],[1,1],[3,4,5,1,2],[2,1,4],[1,2,3],[3,2,1],[2,2,1,2],[2,3,1],[5,1,2,3,4],[1,3,3,2],[4,4,4],[10,-2,0,5]]],SHIFTS,[SHIFTS.replace('len(drops)>1','len(drops)>0'),SHIFTS.replace('len(nums)-1-drops[0]','drops[0]+1')],['Rejects every rotated sorted array containing its one circular drop.','Returns the left-rotation distance rather than the requested right-shift count.'],shifts_oracle,random_shifts,['A sorted circular rotation has at most one adjacent descent around the circle.','Find indices whose value is greater than the next circular value.','No drops means already sorted; one drop determines how many suffix values must move to the front; more than one is impossible.','Rotating immediately after the unique drop places the global low segment before the high segment, and all internal pairs are already ordered.'],'O(n)','O(n)',3),
2859:entry('sum_at_k_set_bit_indices',[('nums','list[int]'),('k','int')],'int',['arrays','bit manipulation'],['Use each element’s zero-based array index.','An index qualifies when its binary representation contains exactly k one bits.','Return the sum of values at all qualifying indices.'],[([[5,10,1,5,2],1],'Indices one, two, and four each have one set bit, contributing 10+1+2=13.'),([[4,3,2,1],2],'Only index three has two set bits, contributing one.')],[[nums,k] for nums,k in [([7],0),([7],1),([1,2],0),([1,2],1),([1,2,3,4],1),([1,2,3,4],2),([0,0,0],1),([-1,2,-3,4],1),([5]*8,3),(list(range(10)),2),(list(range(16)),4),([9,8,7,6,5],0),([10,-10,20,-20,30],1),([1,1,1,1,1,1],2)]],BIT_INDEX,[BIT_INDEX.replace('index.bit_count()==k','value.bit_count()==k'),BIT_INDEX.replace('==k','<=k')],['Counts set bits in each value instead of its index.','Includes indices with fewer than k set bits.'],bit_index_oracle,random_bit_index,['The selection rule concerns indices, not stored values.','Use integer bit_count on every enumerated index.','Add the corresponding value exactly when the count equals k.','Enumeration considers every index once and the equality test implements the qualification exactly.'],'O(n)','O(1)',3),
}
BATCH[2839]['boundaries'].append(['abcd','abcc'])
BATCH[2848]['params'][0]=('nums','list[list[int]]','raw')
