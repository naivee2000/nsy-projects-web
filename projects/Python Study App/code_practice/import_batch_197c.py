"""Split cost, digit quality, unique middle, digit ranges, and elapsed time."""
from .import_batch_055 import entry

def split_oracle(a):return sum(range(a[0]))
def random_split(r):return [r.randint(1,1000)]
def good_oracle(a):return sum(int(x)**2-int(x) for x in str(a[0]))>=50
def random_good(r):return [r.randint(1,10**9)]
def middle_oracle(a):return a[0].count(a[0][len(a[0])//2])==1
def random_middle(r):return [[r.randint(1,12) for _ in range(2*r.randint(0,20)+1)]]
def range_oracle(a):
    values=[max(map(int,str(x)))-min(map(int,str(x))) for x in a[0]];best=max(values);return sum(x for x,v in zip(a[0],values) if v==best)
def random_range(r):return [[r.randint(1,10**9) for _ in range(r.randint(1,30))]]
def seconds(s):h,m,v=map(int,s.split(':'));return h*3600+m*60+v
def elapsed_oracle(a):return seconds(a[1])-seconds(a[0])
def random_elapsed(r):
    x=r.randint(0,86399);y=r.randint(x,86399)
    return [f'{x//3600:02}:{x//60%60:02}:{x%60:02}',f'{y//3600:02}:{y//60%60:02}:{y%60:02}']

SPLIT='''def minimum_cost_to_split_into_ones(n):
    return n*(n-1)//2
'''
GOOD='''def is_good_digit_integer(n):
    return sum(int(digit)*(int(digit)-1) for digit in str(n))>=50
'''
MIDDLE='''def is_middle_element_unique(nums):
    return nums.count(nums[len(nums)//2])==1
'''
RANGE='''def sum_maximum_digit_range_numbers(nums):
    ranges=[max(map(int,str(x)))-min(map(int,str(x))) for x in nums]
    best=max(ranges)
    return sum(x for x,value in zip(nums,ranges) if value==best)
'''
ELAPSED='''def elapsed_seconds(start_time,end_time):
    def value(text):
        h,m,s=map(int,text.split(':'));return h*3600+m*60+s
    return value(end_time)-value(start_time)
'''

BATCH={
3958:entry('minimum_cost_to_split_into_ones',[('n','int')],'int',['math','invariants'],['Split a value x into positive a and b with a+b=x.','That split costs a*b; continue until all pieces are ones.','Return the minimum total cost.'],[([3],'Splitting 3 into 1+2 costs two, then 2 into 1+1 costs one, totaling three.'),([4],'Every complete sequence of splits costs six.')],[[n] for n in [1,2,3,4,5,6,7,8,10,25,100,999,100000,50000000]],SPLIT,[SPLIT.replace('n-1','n+1'),SPLIT.replace('//2','//3')],['Uses the wrong adjacent triangular product.','Divides the invariant total by three.'],split_oracle,random_split,['A split adds a*b cross-pairs between its two groups.','Across the full split tree, each pair of final ones is separated exactly once.','Count unordered pairs among n ones.','The invariant is n choose two regardless of split order, so it is also the minimum.'],'O(1)','O(1)',5),
3959:entry('is_good_digit_integer',[('n','int')],'bool',['math','digits'],['Let digitSum be the sum of decimal digits and squareSum their squared sum.','n is good when squareSum-digitSum is at least fifty.','Return that boolean.'],[([1000],'Both sums are one, so their difference is zero and the result is false.'),([19],'The difference is 82 minus 10, which is seventy-two and passes.')],[[n] for n in [1,9,10,19,55,56,66,77,88,99,1000,12345,909,4444,987654321]],GOOD,[GOOD.replace('>=50','>50'),GOOD.replace('int(digit)-1','int(digit)+1')],['Rejects a score exactly equal to fifty.','Adds rather than subtracts the ordinary digit sum.'],good_oracle,random_good,['For a digit d, its contribution is d squared minus d.','Compute d*(d-1) for each decimal digit.','Sum the contributions and compare with fifty inclusively.','Linearity makes this exactly squareSum-digitSum.'],'O(digits)','O(digits)',3),
3978:entry('is_middle_element_unique',[('nums','list[int]')],'bool',['arrays','counting'],['nums has odd positive length.','Read the element at index len(nums)//2.','Return whether that value occurs exactly once in the whole array.'],[([[1,2,3]],'The middle value two appears only once.'),([[1,2,1,2,3]],'The middle value one also appears at index zero, so it is not unique.')],[[x] for x in [[1],[1,2,3],[1,2,1,2,3],[1,1,1],[2,1,2],[5,4,3,2,1],[1,2,3,2,1],[7,8,9,7,6],[0,1,0],[-1,0,1],[3,3,2,3,3],[1,4,2,4,3],[9,8,7],[2,5,2]]],MIDDLE,[MIDDLE.replace('==1','==0'),MIDDLE.replace('len(nums)//2','0')],['Incorrectly requires the middle value to be absent.','Checks uniqueness of the first value instead of the middle value.'],middle_oracle,random_middle,['Locate the single middle index using integer division.','Capture its value.','Count that value throughout nums.','Exactly one occurrence means the middle value is unique.'],'O(n)','O(1)',3),
3982:entry('sum_maximum_digit_range_numbers',[('nums','list[int]')],'int',['arrays','digits'],['The digit range of a positive integer is its largest digit minus its smallest digit.','Find the maximum digit range among nums.','Return the sum of every number tied for that maximum.'],[([[5724,111,350]],'The ranges are five, zero, and five, so 5724 and 350 sum to 6074.'),([[7,88,999]],'Every single-valued digit set has range zero, so all three numbers are summed.')],[[x] for x in [[1],[5724,111,350],[7,88,999],[10,20],[123,456],[909,818],[100,99,8],[9876,1234,505],[11,12,13],[999,109],[2468,1357],[1000,1],[808,707,606],[123456789,90]]],RANGE,[RANGE.replace('if value==best','if value!=best'),RANGE.replace('max(ranges)','min(ranges)')],['Sums numbers outside the best range.','Chooses the minimum digit range instead of the maximum.'],range_oracle,random_range,['Compute each number’s minimum and maximum decimal digit.','Store their difference beside the number.','Find the largest difference.','Sum all original numbers whose stored difference equals it.'],'O(total digits)','O(n)',3),
3986:entry('elapsed_seconds',[('start_time','str'),('end_time','str')],'int',['strings','time arithmetic'],['Both inputs are valid same-day times in HH:MM:SS form.','start_time is no later than end_time.','Return the number of elapsed seconds.'],[(['01:00:00','01:00:25'],'Only twenty-five seconds separate the two times.'),(['23:59:58','23:59:59'],'The consecutive times differ by one second.')],[[a,b] for a,b in [('00:00:00','00:00:00'),('00:00:00','00:00:01'),('01:00:00','01:00:25'),('00:00:00','01:00:00'),('01:30:00','02:00:00'),('12:34:56','12:34:57'),('23:59:58','23:59:59'),('10:10:10','11:11:11'),('05:00:30','05:01:00'),('00:59:59','01:00:00'),('08:15:00','17:45:00'),('22:00:00','23:59:59'),('03:03:03','03:33:33'),('00:00:01','23:59:59')]],ELAPSED,[ELAPSED.replace('h*3600','h*60'),ELAPSED.replace('value(end_time)-value(start_time)','value(start_time)-value(end_time)')],['Converts hours as minutes rather than seconds.','Subtracts the times in reverse order.'],elapsed_oracle,random_elapsed,['Parse hours, minutes, and seconds.','Convert each time to seconds since midnight.','Subtract the start value from the end value.','The same-day ordering guarantees a nonnegative result.'],'O(1)','O(1)',3),
}
