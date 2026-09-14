"""Almost-missing values, fruit placement, even numbers, unique sums, and phone prefixes."""
from itertools import permutations
from .import_batch_055 import entry

def missing_oracle(a):
    nums,k=a;counts={v:0 for v in nums}
    for i in range(len(nums)-k+1):
        for v in set(nums[i:i+k]):counts[v]+=1
    return max((v for v,c in counts.items() if c==1),default=-1)
def random_missing(r):
    n=r.randint(1,20);return [[r.randint(0,15) for _ in range(n)],r.randint(1,n)]
def fruits_oracle(a):
    fruits,baskets=a;used=[False]*len(baskets);left=0
    for fruit in fruits:
        for i,capacity in enumerate(baskets):
            if not used[i] and capacity>=fruit:used[i]=True;break
        else:left+=1
    return left
def random_fruits(r):
    n=r.randint(1,25);return [[r.randint(1,30) for _ in range(n)],[r.randint(1,30) for _ in range(n)]]
def even_oracle(a):
    digits=a[0];values=set()
    for indexes in permutations(range(len(digits)),3):
        x,y,z=(digits[i] for i in indexes)
        if x and z%2==0:values.add(100*x+10*y+z)
    return len(values)
def random_even(r):return [[r.randint(0,9) for _ in range(r.randint(3,9))]]
def unique_sum_oracle(a):
    nums=a[0];best=max(nums)
    for mask in range(1,1<<len(nums)):
        chosen=[nums[i] for i in range(len(nums)) if mask>>i&1]
        if len(chosen)==len(set(chosen)):best=max(best,sum(chosen))
    return best
def random_unique_sum(r):return [[r.randint(-10,15) for _ in range(r.randint(1,12))]]
def phone_oracle(a):
    numbers=a[0]
    return not any(i!=j and right.startswith(left) for i,left in enumerate(numbers) for j,right in enumerate(numbers))
def random_phone(r):
    count=r.randint(1,20);return [[''.join(str(r.randrange(10)) for _ in range(r.randint(1,8))) for _ in range(count)]]

MISSING='''def largest_almost_missing_integer(nums,k):
    appearances={value:0 for value in nums}
    for start in range(len(nums)-k+1):
        for value in set(nums[start:start+k]):appearances[value]+=1
    return max((value for value,count in appearances.items() if count==1),default=-1)
'''
FRUITS='''def count_unplaced_fruits(fruits,baskets):
    available=[True]*len(baskets)
    unplaced=0
    for fruit in fruits:
        for i,capacity in enumerate(baskets):
            if available[i] and capacity>=fruit:
                available[i]=False
                break
        else:unplaced+=1
    return unplaced
'''
EVEN='''def count_unique_three_digit_even_numbers(digits):
    values=set()
    for i,a in enumerate(digits):
        for j,b in enumerate(digits):
            for k,c in enumerate(digits):
                if len({i,j,k})==3 and a!=0 and c%2==0:values.add(100*a+10*b+c)
    return len(values)
'''
UNIQUE='''def maximum_unique_subarray_sum_after_deletion(nums):
    positive={value for value in nums if value>0}
    return sum(positive) if positive else max(nums)
'''
PHONE='''def is_phone_number_list_consistent(numbers):
    ordered=sorted(numbers)
    return all(not right.startswith(left) for left,right in zip(ordered,ordered[1:]))
'''

BATCH={
3471:entry('largest_almost_missing_integer',[('nums','list[int]'),('k','int')],'int',['arrays','sliding windows','sets'],['Consider every contiguous subarray of length k.','A value is almost missing when it occurs in exactly one such subarray, regardless of repetitions inside that subarray.','Return the largest almost-missing value, or -1 if none exists.'],[([[3,9,2,1,7],3],'Values three and seven each appear in one length-three window; seven is larger.'),([[1,1,1],2],'One occurs in both windows, so no value qualifies.')],[[n,k] for n,k in [([1],1),([1,2],1),([1,2],2),([1,1,1],2),([3,9,2,1,7],3),([5,5,1],2),([1,2,3,1],2),([9,1,2,9],3),([4,3,2,1],2),([7,7],2),([0,1,0],1),([8,6,8,5],2),([2,3,4],3),([1,2,1,3,4],3)]],MISSING,[MISSING.replace('set(nums[start:start+k])','nums[start:start+k]'),MISSING.replace('count==1','count==2')],['Counts repeated occurrences within one window more than once.','Selects values appearing in two windows rather than exactly one.'],missing_oracle,random_missing,['Track in how many windows each distinct value appears.','Use a set per window so repetition inside one window counts once.','Select values whose window count is exactly one.','Taking their maximum, with -1 as default, gives the required result.'],'O(n*k)','O(distinct values)',3),
3477:entry('count_unplaced_fruits',[('fruits','list[int]'),('baskets','list[int]')],'int',['arrays','greedy','simulation'],['Process fruit quantities from left to right.','Place each in the leftmost unused basket whose capacity is at least that quantity.','Return how many fruit types cannot be placed.'],[([[4,2,5],[3,5,4]],'Four uses capacity five, two uses capacity three, and five has no remaining fit, so one is unplaced.'),([[1,2],[2,3]],'Each fruit fits the leftmost remaining basket, so none is unplaced.')],[[f,b] for f,b in [([1],[1]),([2],[1]),([4,2,5],[3,5,4]),([1,2],[2,3]),([3,3],[3,3]),([5,1],[1,5]),([2,4],[3,4]),([4,2],[2,4]),([1,1,1],[1,1,1]),([9,8,7],[7,8,9]),([2,2,5],[2,4,5]),([6,1,6],[6,6,1]),([3,1,2],[2,3,1]),([10,1],[9,2])]],FRUITS,[FRUITS.replace('capacity>=fruit','capacity>fruit'),FRUITS.replace('enumerate(baskets)','enumerate(reversed(baskets))')],['Rejects exact-capacity fits.','Searches baskets from the right instead of choosing the leftmost fit.'],fruits_oracle,random_fruits,['Maintain whether each basket remains unused.','For each fruit, scan baskets from the left.','Consume the first unused basket with sufficient capacity; otherwise increment the unplaced count.','This direct simulation enforces both processing and leftmost-choice order.'],'O(n^2)','O(n)',3),
3483:entry('count_unique_three_digit_even_numbers',[('digits','list[int]')],'int',['arrays','enumeration','sets'],['Choose three distinct input positions to form a number.','The hundreds digit cannot be zero and the units digit must be even.','Return the count of distinct three-digit even values obtainable.'],[([[1,2,3,4]],'Twelve distinct three-digit even numbers can be formed.'),([[0,2,2]],'Only 202 and 220 can be formed from the available positions.')],[[x] for x in [[1,2,3],[1,2,4],[0,2,2],[0,0,2],[2,2,2],[1,2,3,4],[0,1,2,3],[9,8,7],[1,1,2],[4,0,4],[5,6,7,8],[0,1,0,2],[2,4,6],[3,3,4,4]]],EVEN,[EVEN.replace('len({i,j,k})==3','len({i,j,k})>=2'),EVEN.replace('a!=0','a>=0')],['Reuses an input position.','Allows a leading zero.'],even_oracle,random_even,['Enumerate ordered triples of distinct positions.','Reject zero in the hundreds position and odd units digits.','Insert each valid numeric value into a set.','The set removes duplicates caused by equal digits at different positions.'],'O(n^3)','O(results)',3),
3487:entry('maximum_unique_subarray_sum_after_deletion',[('nums','list[int]')],'int',['arrays','sets','greedy'],['Delete any elements while keeping the remaining order, but keep at least one.','Choose the retained array so its values are distinct and its sum is maximal.','Return that maximum sum.'],[([[1,2,3,4,5]],'Keeping every distinct positive value gives sum fifteen.'),([[1,1,0,1,1]],'Keep one occurrence of one; adding zero does not improve the sum.')],[[x] for x in [[1],[-1],[0],[1,1],[1,2,3,4,5],[1,1,0,1,1],[-5,-2,-3],[-1,2,2,3],[5,-1,5],[0,0,0],[3,3,2,2,1],[-2,0,-1],[10,-10,5],[4,1,4,2]]],UNIQUE,[UNIQUE.replace('value>0','value>=-1'),UNIQUE.replace('max(nums)','min(nums)')],['Incorrectly keeps negative one whenever it appears.','Chooses the smallest value when every value is nonpositive.'],unique_sum_oracle,random_unique_sum,['Each distinct positive value can improve the sum and should be kept once.','Duplicates add no new allowed value, while negative values reduce the sum.','If any positive exists, sum the set of positives.','Otherwise the nonempty requirement makes the largest single value optimal.'],'O(n)','O(n)',3),
3491:entry('is_phone_number_list_consistent',[('numbers','list[str]')],'bool',['strings','sorting'],['A phone-number list is consistent when no entry is a prefix of another distinct entry.','Return false if any prefix conflict exists and true otherwise.','Compare complete strings, including leading zeros.'],[([['1','2','4','3']],'No number prefixes another, so the list is consistent.'),([['911','97625999','91125426']],'911 prefixes 91125426, so return false.')],[[x] for x in [['1'],['1','2'],['1','10'],['12','123'],['1','2','4','3'],['911','97625999','91125426'],['01','1'],['0','00'],['123','124','125'],['9','98','97'],['555','55'],['10','101','11'],['001','002'],['3','30','300']]],PHONE,[PHONE.replace('not right.startswith(left)','right.startswith(left)'),PHONE.replace('sorted(numbers)','numbers')],['Returns true precisely for adjacent prefix conflicts.','Checks only the original neighboring order and can miss a conflict.'],phone_oracle,random_phone,['Sort phone strings lexicographically.','If one number prefixes another, it prefixes the next string after it in sorted order.','Check every adjacent sorted pair for that relation.','Absence of any adjacent conflict proves global consistency.'],'O(n log n)','O(n)',3),
}
