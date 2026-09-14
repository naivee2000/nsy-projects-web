"""Second slice of workbook batch 135."""

from .import_batch_055 import entry


def remap_oracle(args):
    text=str(args[0]);values=[]
    for old in '0123456789':
        for new in '0123456789':values.append(int(text.replace(old,new)))
    return max(values)-min(values)


def random_remap(rng):return [rng.randint(1,99999999)]


def merge_arrays_oracle(args):
    result={}
    for key,value in args[0]+args[1]:result[key]=result.get(key,0)+value
    return [[key,result[key]] for key in sorted(result)]


def random_merge_arrays(rng):
    ids=list(range(1,20));rng.shuffle(ids);a=ids[:rng.randint(1,8)];rng.shuffle(ids);b=ids[:rng.randint(1,8)]
    return [[[i,rng.randint(1,20)] for i in a],[[i,rng.randint(1,20)] for i in b]]


def differences_oracle(args):
    nums=args[0]
    return [abs(sum(nums[:index])-sum(nums[index+1:])) for index in range(len(nums))]


def random_differences(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,20))]]


def split_oracle(args):
    from itertools import product
    digits=list(str(args[0]));best=10**20
    for sides in product((0,1),repeat=len(digits)):
        if 0 not in sides or 1 not in sides:continue
        left=''.join(sorted(d for d,s in zip(digits,sides) if s==0));right=''.join(sorted(d for d,s in zip(digits,sides) if s==1))
        best=min(best,int(left)+int(right))
    return best


def random_split(rng):return [rng.randint(10,999999)]


def pillow_oracle(args):
    n,time=args;position=1;direction=1
    for _ in range(time):
        if position==n:direction=-1
        elif position==1:direction=1
        position+=direction
    return position


def random_pillow(rng):return [rng.randint(2,20),rng.randint(0,200)]


REMAP='''\
def maximum_remap_difference(num):
    text=str(num);high_digit=next((char for char in text if char!='9'),None);low_digit=text[0]
    high=int(text.replace(high_digit,'9')) if high_digit else num
    low=int(text.replace(low_digit,'0'))
    return high-low
'''

MERGE='''\
def merge_id_value_arrays(nums1,nums2):
    values={}
    for key,value in nums1+nums2:values[key]=values.get(key,0)+value
    return [[key,values[key]] for key in sorted(values)]
'''

DIFFERENCES='''\
def left_right_sum_differences(nums):
    right=sum(nums);left=0;answer=[]
    for value in nums:
        right-=value;answer.append(abs(left-right));left+=value
    return answer
'''

SPLIT='''\
def minimum_digit_split_sum(num):
    digits=sorted(str(num));first=''.join(digits[::2]);second=''.join(digits[1::2])
    return int(first)+int(second)
'''

PILLOW='''\
def pillow_holder(n,time):
    offset=time%(2*(n-1))
    return 1+offset if offset<n else 2*n-1-offset
'''


BATCH={
2566:entry('maximum_remap_difference',[('num','int')],'int',['strings','greedy','digits'],['For one remapping, choose a digit x and replace every occurrence of x by digit y.','Leading zeroes after remapping are allowed and simply disappear numerically.','Return the maximum obtainable number minus the minimum obtainable number, using independent remappings.'],[([11891],'Replacing one by nine gives 99899; replacing one by zero gives 890; their difference is 99009.'),([90],'The maximum remains ninety while replacing nine by zero gives zero, so the difference is ninety.')],[[n] for n in [1,9,10,11,99,100,909,123,555,9876,9999,10000,80808,12021]],REMAP,[REMAP.replace("char!='9'","char!='0'"),REMAP.replace('low_digit=text[0]','low_digit=text[-1]')],['Chooses the first nonzero digit rather than the first non-nine digit for maximizing.','Zeros the final digit’s value instead of the leading digit, which may not minimize the number.'],remap_oracle,random_remap,['To maximize, preserve leading nines and replace the first non-nine digit everywhere with nine.','To minimize, replace every occurrence of the leading digit with zero.','Compute the two remapped integers independently and subtract.','The earliest differing decimal position dominates all later positions, so both greedy digit choices are optimal.'],'O(digits)','O(digits)',3),
2570:entry('merge_id_value_arrays',[('nums1','list[list[int]]'),('nums2','list[list[int]]')],'list[list[int]]',['arrays','hash maps','sorting'],['Each entry is [id,value], with unique ids within each input array.','For each id, sum values contributed by both arrays.','Return [id,total] entries in increasing id order.'],[([[[1,2],[2,3],[4,5]],[[1,4],[3,2],[4,1]]],'Ids one and four combine across inputs, producing [[1,6],[2,3],[3,2],[4,6]].'),([[[2,4]],[[1,3]]],'Distinct ids are preserved and sorted as [[1,3],[2,4]].')],[[a,b] for a,b in [([[1,1]],[[1,1]]),([[1,1]],[[2,2]]),([[2,2]],[[1,1]]),([[1,5],[3,7]],[[2,6]]),([[1,5],[3,7]],[[1,2],[3,3]]),([[10,1]],[[1,10]]),([[2,8],[7,1]],[[2,2],[9,4]]),([[1,9],[8,2]],[[4,3],[8,7]]),([[6,6]],[[7,7]]),([[1,1],[5,5],[9,9]],[[2,2],[5,1]]),([[4,10],[2,1]],[[3,2],[4,5]]),([[100,1]],[[100,99]]),([[3,3],[6,6]],[[1,1],[9,9]]),([[8,4],[1,7]],[[1,2],[8,3]])]],MERGE,[MERGE.replace('nums1+nums2','nums1'),MERGE.replace('sorted(values)','values')],['Ignores all contributions from the second array.','Returns dictionary insertion order rather than increasing id order.'],merge_arrays_oracle,random_merge_arrays,['Accumulate values in a dictionary keyed by id.','Process entries from both arrays into the same map.','Build output by iterating sorted ids.','Every contribution is added exactly once to its id, and sorted keys enforce the required order.'],'O((n+m) log(n+m))','O(n+m)',3),
2574:entry('left_right_sum_differences',[('nums','list[int]')],'list[int]',['arrays','prefix sums'],['For each index, left sum excludes nums[index] and contains all earlier values.','Right sum excludes nums[index] and contains all later values.','Return the absolute difference at every index.'],[([[10,4,8,3]],'The four left/right differences are fifteen, one, eleven, and twenty-two.'),([[1]],'Both excluded-side sums are zero, so the only difference is zero.')],[[a] for a in [[1,2],[2,1],[1,2,3],[3,2,1],[5,5,5],[1,10,1],[2,4,6,8],[10,0,10],[1,1,2,3,5],[9,8,7,6],[100,1,1],[4,3,2,1],[7,7],[1,2,1,2]]],DIFFERENCES,[DIFFERENCES.replace('right-=value',''),DIFFERENCES.replace('left+=value','left-=value')],['Leaves the current value in the right-side sum.','Subtracts processed values from the left accumulator instead of adding them.'],differences_oracle,random_differences,['Initialize right as the total sum and left as zero.','Before recording an index, subtract its current value from right.','Append abs(left-right), then add the current value to left.','Those update positions maintain exactly the sums strictly before and strictly after each index.'],'O(n)','O(n)',3),
2578:entry('minimum_digit_split_sum',[('num','int')],'int',['sorting','greedy','digits'],['Use every decimal digit of num exactly once to form two new nonnegative integers.','Leading zeroes are allowed.','Return the minimum possible sum of the two integers.'],[([4325],'Sorted digits 2,3,4,5 split alternately into 24 and 35, summing to 59.'),([687],'Sorted digits split into 68 and 7, whose sum is 75.')],[[n] for n in [10,11,12,99,100,101,123,9876,5555,10203,90909,123456,100000,808]],SPLIT,[SPLIT.replace('digits[::2]','digits[:len(digits)//2]'),SPLIT.replace('digits=sorted(str(num))','digits=sorted(str(num),reverse=True)')],['Groups the smallest digits into one number instead of balancing place values between both numbers.','Places the largest digits in the highest positions, maximizing rather than minimizing the sum.'],split_oracle,random_split,['Sort all digits from smallest to largest.','Distribute them alternately between the two numbers.','This balances digit counts and assigns earlier small digits to the most significant available places.','Any unbalanced placement or inversion puts a larger digit at an equally or more significant place, so the alternating sorted construction minimizes the sum.'],'O(d log d)','O(d)',3),
2582:entry('pillow_holder',[('n','int'),('time','int')],'int',['math','simulation'],['People are numbered one through n in a line.','The pillow moves one person per second, reversing direction at either endpoint.','Person one holds it at time zero; return the holder after time seconds.'],[([4,5],'The holders are 1,2,3,4,3,2, so person two holds it after five seconds.'),([3,2],'After two forward passes, person three holds the pillow.')],[[n,t] for n,t in [(2,0),(2,1),(2,2),(2,3),(3,0),(3,1),(3,3),(3,4),(4,3),(4,4),(5,8),(5,9),(10,9),(10,18)]],PILLOW,[PILLOW.replace('2*(n-1)','n-1'),PILLOW.replace('2*n-1-offset','2*n-offset')],['Uses only a one-way period and loses the return journey.','Reflects from the far endpoint with an off-by-one position.'],pillow_oracle,random_pillow,['One complete forward-and-back cycle lasts 2*(n-1) seconds.','Reduce time modulo that cycle length.','Offsets below n move forward from person one; larger offsets reflect backward as 2*n-1-offset.','Periodic motion repeats exactly after returning to person one with forward direction, so the reduced formula matches every time.'],'O(1)','O(1)',3),
}

BATCH[2574]['wrong'][0]='''\
def left_right_sum_differences(nums):
    right=sum(nums);left=0;answer=[]
    for value in nums:
        answer.append(abs(left-right));right-=value;left+=value
    return answer
'''
BATCH[2574]['wrong_reasons'][0]='Computes each difference before removing the current value from the right-side sum.'
