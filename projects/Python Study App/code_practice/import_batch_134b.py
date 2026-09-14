"""Second slice of workbook batch 134."""

from .import_batch_055 import entry


def dividing_oracle(args):
    number=args[0]
    return sum(digit!='0' and number%int(digit)==0 for digit in str(number))


def random_dividing(rng):return [rng.randint(1,999999)]


def box_oracle(args):
    length,width,height,mass=args
    bulky=max(length,width,height)>=10000 or length*width*height>=1_000_000_000
    heavy=mass>=100
    if bulky and heavy:return 'Both'
    if bulky:return 'Bulky'
    if heavy:return 'Heavy'
    return 'Neither'


def random_box(rng):return [rng.randint(1,15000),rng.randint(1,15000),rng.randint(1,15000),rng.randint(1,200)]


def sign_count_oracle(args):
    nums=args[0]
    return max(sum(value<0 for value in nums),sum(value>0 for value in nums))


def random_sign_count(rng):return [sorted(rng.randint(-20,20) for _ in range(rng.randint(1,30)))]


def sum_difference_oracle(args):
    nums=args[0];digits=[]
    for value in nums:digits.extend(int(char) for char in str(value))
    return abs(sum(nums)-sum(digits))


def random_sum_difference(rng):return [[rng.randint(1,9999) for _ in range(rng.randint(1,20))]]


def common_oracle(args):
    common=set(args[0])&set(args[1]);return min(common,default=-1)


def random_common(rng):
    return [sorted(set(rng.randint(1,50) for _ in range(rng.randint(1,15)))),sorted(set(rng.randint(1,50) for _ in range(rng.randint(1,15))))]


DIVIDING='''\
def count_dividing_digits(num):
    return sum(digit!='0' and num%int(digit)==0 for digit in str(num))
'''

BOX='''\
def categorize_box(length,width,height,mass):
    bulky=max(length,width,height)>=10000 or length*width*height>=1000000000
    heavy=mass>=100
    if bulky and heavy:return 'Both'
    if bulky:return 'Bulky'
    if heavy:return 'Heavy'
    return 'Neither'
'''

SIGNS='''\
def maximum_positive_or_negative_count(nums):
    from bisect import bisect_left,bisect_right
    negatives=bisect_left(nums,0);positives=len(nums)-bisect_right(nums,0)
    return max(negatives,positives)
'''

DIFFERENCE='''\
def element_digit_sum_difference(nums):
    return abs(sum(nums)-sum(int(char) for number in nums for char in str(number)))
'''

COMMON='''\
def minimum_common_sorted_value(nums1,nums2):
    left=right=0
    while left<len(nums1) and right<len(nums2):
        if nums1[left]==nums2[right]:return nums1[left]
        if nums1[left]<nums2[right]:left+=1
        else:right+=1
    return -1
'''


BATCH={
2520:entry('count_dividing_digits',[('num','int')],'int',['math','digits'],['Inspect each decimal digit occurrence in num.','A zero digit never counts because division by zero is undefined.','Count each nonzero digit that divides num evenly, including repeated occurrences.'],[([7],'The only digit seven divides seven, so the count is one.'),([121],'Both one occurrences and the digit two divide 121 only for the ones, giving two.')],[[n] for n in [1,10,11,12,15,22,101,128,1248,999,1000,777,360,12345]],DIVIDING,[DIVIDING.replace("digit!='0' and ",''),DIVIDING.replace('num%int(digit)==0','num%int(digit)!=0')],['Attempts modulo by a zero digit instead of skipping it.','Counts digits that do not divide the number rather than those that do.'],dividing_oracle,random_dividing,['Read the decimal representation one character at a time.','Skip zero before converting it into a divisor.','For every other digit, add one when num modulo digit is zero.','This independently tests every digit occurrence against the definition, preserving duplicates.'],'O(log num)','O(log num)',3),
2525:entry('categorize_box',[('length','int'),('width','int'),('height','int'),('mass','int')],'str',['simulation','boolean logic'],['A box is Bulky if any dimension is at least 10,000 or its volume is at least 1,000,000,000.','A box is Heavy if mass is at least 100.','Return Both, Bulky, Heavy, or Neither according to those two flags.'],[([1000,35,700,300],'The volume and dimensions are not bulky, but mass is heavy, so the category is Heavy.'),([10000,1,1,100],'A threshold dimension and threshold mass make the category Both.')],[[a,b,c,m] for a,b,c,m in [(1,1,1,1),(9999,1,1,99),(10000,1,1,99),(1,10000,1,1),(1,1,10000,1),(1000,1000,1000,1),(999,1000,1000,1),(10,10,10,100),(10000,1,1,100),(5000,5000,40,50),(20000,2,2,150),(100,100,100,99),(100,100,100,100),(9999,9999,2,50)]],BOX,[BOX.replace('>=10000','>10000'),BOX.replace('mass>=100','mass>100')],['Treats a dimension exactly at the bulky threshold as not bulky.','Treats mass exactly at the heavy threshold as not heavy.'],box_oracle,random_box,['Compute the bulky and heavy conditions as two independent booleans.','Bulky uses OR between the dimension threshold and volume threshold.','Return Both when both flags hold, otherwise the one matching label, otherwise Neither.','The four returns enumerate all combinations of the two defined predicates.'],'O(1)','O(1)',3),
2529:entry('maximum_positive_or_negative_count',[('nums','list[int]')],'int',['arrays','binary search'],['nums is sorted in nondecreasing order.','Zero is neither positive nor negative.','Return the larger of the positive-element count and negative-element count.'],[([[-2,-1,-1,1,2,3]],'There are three negative and three positive values, so the maximum count is three.'),([[-3,-2,-1,0,0,1,2]],'Three negatives exceed two positives, so the result is three.')],[[a] for a in [[0],[-1],[1],[-1,0,1],[-5,-4,-3], [1,2,3], [0,0,0],[-2,-1,0,0], [0,0,1,2],[-3,-2,-1,4],[-10,0,0,0,10],[-5,-5,1],[-1,2,2,2],[-4,-3,0,1]]],SIGNS,[SIGNS.replace('bisect_left(nums,0)','bisect_right(nums,0)'),SIGNS.replace('bisect_right(nums,0)','bisect_left(nums,0)',1)],['Includes zeroes in the negative count.','Includes zeroes in the positive suffix by starting it at the first zero.'],sign_count_oracle,random_sign_count,['In a sorted array, negatives form a prefix and positives form a suffix.','bisect_left(nums,0) gives the negative count.','len(nums)-bisect_right(nums,0) gives the positive count; return the larger.','The two binary-search boundaries exclude the entire contiguous zero block exactly.'],'O(log n)','O(1)',3),
2535:entry('element_digit_sum_difference',[('nums','list[int]')],'int',['arrays','digits'],['Element sum is the sum of all array values.','Digit sum is the sum of every decimal digit in every value.','Return the absolute difference between those two sums.'],[([[1,15,6,3]],'Element sum is twenty-five and digit sum is sixteen, giving difference nine.'),([[1,2,3,4]],'Each value is one digit, so the two sums are equal and the result is zero.')],[[a] for a in [[10],[99],[100],[5,10],[12,34],[999,1],[101,202],[7,8,9],[1000,2000],[11,11,11],[123,456,789],[1,20,300],[42,42],[9,90,900]]],DIFFERENCE,[DIFFERENCE.replace('sum(nums)-','sum(nums)+'),DIFFERENCE.replace('for char in str(number)','for char in str(nums[0])')],['Adds element and digit sums instead of taking their difference.','Uses the first number’s digits repeatedly for every array element.'],sum_difference_oracle,random_sum_difference,['Compute the element sum normally.','Use nested iteration over numbers and their decimal characters for the digit sum.','Return the absolute difference.','Both accumulations include every required element or digit once, directly matching the two definitions.'],'O(total digits)','O(1)',3),
2540:entry('minimum_common_sorted_value',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','two pointers'],['Both arrays are strictly increasing.','Return the smallest value present in both arrays.','Return -1 when their intersection is empty.'],[([[1,2,3],[2,4]],'Two is the first value shared by both sorted arrays.'),([[1,2,3],[4,5]],'The arrays have no common value, so the result is minus one.')],[[a,b] for a,b in [([1],[1]),([1],[2]),([1,2],[2]),([2],[1,2]),([1,3,5],[2,4,6]),([1,4,7],[0,4,8]),([2,3,9],[1,3,9]),([10,20],[5,10]),([1,2,100],[99,100]),([1,5,9],[1,5,9]),([3,6,9],[2,3,6]),([0,2,4],[1,2,3]),([7,8],[1,2,3]),([1,10,20],[5,10,15])]],COMMON,[COMMON.replace('return nums1[left]','return nums1[-1]'),COMMON.replace('left+=1','right+=1',1)],['Returns the final first-array value rather than the matching value.','Advances the wrong pointer when the first value is smaller, potentially missing a match.'],common_oracle,random_common,['Compare the current values at two pointers.','If equal, it is the smallest possible remaining common value, so return it.','Otherwise advance only the pointer holding the smaller value; return -1 if one array ends.','A smaller unmatched value cannot equal any later value in the other sorted array, so discarding it is safe.'],'O(n+m)','O(1)',3),
}

BATCH[2520]['wrong'][0]='''\
def count_dividing_digits(num):
    return sum(digit!='0' and num%int(digit)==0 for digit in set(str(num)))
'''
BATCH[2520]['wrong_reasons'][0]='Counts distinct digit values instead of counting every digit occurrence.'
