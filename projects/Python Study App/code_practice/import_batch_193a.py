"""Circular differences, variable windows, parity partitions, digit pairs, and frequency parity."""
from collections import Counter
from .import_batch_055 import entry

def circular_oracle(a):
    nums=a[0];return max(abs(nums[i]-nums[(i+1)%len(nums)]) for i in range(len(nums)))
def random_circular(r):return [[r.randint(-100,100) for _ in range(r.randint(2,30))]]
def variable_oracle(a):
    nums=a[0];return sum(sum(nums[max(0,i-nums[i]):i+1]) for i in range(len(nums)))
def random_variable(r):return [[r.randint(0,20) for _ in range(r.randint(1,30))]]
def partitions_oracle(a):
    nums=a[0];return sum((sum(nums[:i])-sum(nums[i:]))%2==0 for i in range(1,len(nums)))
def random_partitions(r):return [[r.randint(-50,50) for _ in range(r.randint(2,40))]]
def pair_oracle(a):
    s=a[0];counts=Counter(s)
    return next((s[i:i+2] for i in range(len(s)-1) if s[i]!=s[i+1] and counts[s[i]]==int(s[i]) and counts[s[i+1]]==int(s[i+1])), '')
def random_pair(r):return [''.join(str(r.randint(1,5)) for _ in range(r.randint(2,30)))]
def frequency_oracle(a):
    values=list(Counter(a[0]).values());return max(v for v in values if v%2)-min(v for v in values if v%2==0)
def random_frequency(r):
    while True:
        s=''.join(r.choice('abcdef') for _ in range(r.randint(3,50)));v=Counter(s).values()
        if any(x%2 for x in v) and any(x%2==0 for x in v):return [s]

CIRCULAR='''def maximum_circular_adjacent_difference(nums):
    return max(abs(value-nums[(i+1)%len(nums)]) for i,value in enumerate(nums))
'''
VARIABLE='''def sum_variable_length_subarrays(nums):
    prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    return sum(prefix[i+1]-prefix[max(0,i-value)] for i,value in enumerate(nums))
'''
PARTITIONS='''def count_even_difference_partitions(nums):
    return len(nums)-1 if sum(nums)%2==0 else 0
'''
PAIR='''def first_valid_adjacent_digit_pair(s):
    from collections import Counter
    counts=Counter(s)
    for left,right in zip(s,s[1:]):
        if left!=right and counts[left]==int(left) and counts[right]==int(right):return left+right
    return ''
'''
FREQUENCY='''def maximum_odd_even_frequency_difference(s):
    from collections import Counter
    values=Counter(s).values()
    return max(value for value in values if value%2)-min(value for value in values if value%2==0)
'''

BATCH={
3423:entry('maximum_circular_adjacent_difference',[('nums','list[int]')],'int',['arrays','circular arrays'],['Treat the first and last array elements as adjacent as well as ordinary neighboring pairs.','Compute the absolute difference for every circular edge.','Return the greatest such difference.'],[([[1,2,4]],'The circular edge from four back to one has difference three, the maximum.'),([[5,5]],'Both circular edges have difference zero.')],[[x] for x in [[1,2],[5,5],[0,10],[-5,5],[1,2,3,4],[4,1,2,3],[10,1,9],[3,-2,7],[-10,-5,-1],[100,0,50],[2,8,2],[1,100,99],[7,3,9,4],[0,1,0,1]]],CIRCULAR,[CIRCULAR.replace('%len(nums)','%(len(nums)-1)'),CIRCULAR.replace('abs(','(')],['Fails to wrap the last element to the first.','Uses signed rather than absolute differences.'],circular_oracle,random_circular,['Enumerate each index as the left endpoint of one circular edge.','Use modulo n to wrap the successor of the final index to zero.','Take the absolute endpoint difference.','The maximum over these n edges covers every adjacent circular pair exactly once.'],'O(n)','O(1)',3),
3427:entry('sum_variable_length_subarrays',[('nums','list[int]')],'int',['arrays','prefix sums'],['For every index i, form the subarray from max(0,i-nums[i]) through i inclusive.','Add the sums of all these variable-length subarrays.','An element may contribute to several subarrays.'],[([[2,3,1]],'The chosen subarrays are [2], [2,3], and [3,1], whose sums total eleven.'),([[0,1,0]],'The subarrays are [0], [0,1], and [0], totaling one.')],[[x] for x in [[0],[1],[5],[0,0],[1,1],[2,3,1],[0,1,0],[3,0,2,1],[1,2,3,4],[10,0,0],[2,0,2],[5,4,3,2,1],[0,2,1,3],[9,9,9]]],VARIABLE,[VARIABLE.replace('i-value','i-value+1'),VARIABLE.replace('prefix[i+1]','prefix[i]')],['Starts every variable window one position too late.','Excludes the value at the ending index.'],variable_oracle,random_variable,['Build prefix sums so any subarray sum is a difference of two prefixes.','For index i, clamp its requested start to zero.','Subtract the prefix before that start from the prefix through i.','Summing these exact contributions gives the requested total.'],'O(n)','O(n)',3),
3432:entry('count_even_difference_partitions',[('nums','list[int]')],'int',['arrays','math','parity'],['Partition after any index before the last element.','Count partitions where left sum minus right sum is even.','Both sides must be nonempty.'],[([[10,10,3,7,6]],'The total sum is even, so all four possible partitions have even difference.'),([[1,2,4]],'The total is odd, making every left-right difference odd.')],[[x] for x in [[1,1],[1,2],[2,2],[0,0],[10,10,3,7,6],[1,2,4],[-1,1],[1,-2,3],[2,4,6,8],[1,3,5],[0,1,1],[7,7,7,7],[5,-5,2],[9,0,2]]],PARTITIONS,[PARTITIONS.replace('sum(nums)%2==0','sum(nums)%2!=0'),PARTITIONS.replace('len(nums)-1','len(nums)')],['Counts partitions only for odd total parity.','Includes an invalid partition after the final element.'],partitions_oracle,random_partitions,['Write right sum as total-left.','Then left-right equals 2*left-total, which has the same parity as total.','If total is even, all n-1 partitions qualify; if odd, none do.','This parity identity avoids recomputing every side sum.'],'O(n)','O(1)',3),
3438:entry('first_valid_adjacent_digit_pair',[('s','str')],'str',['strings','hash maps','counting'],['Find adjacent distinct digits in s.','Each digit in the pair must occur in the entire string exactly as many times as its numeric value.','Return the first valid pair from left to right, or an empty string.'],[(['2523533'],'The first qualifying adjacent pair is 23: digit two occurs twice and digit three occurs three times.'),(['221'],'No adjacent pair has both required whole-string frequencies.')],[[s] for s in ['12','21','221','122','2523533','1122','1112','2333','33322','444455555','12345','11122333','555551','21233']],PAIR,[PAIR.replace('left!=right','left==right'),PAIR.replace('counts[right]==int(right)','counts[right]!=int(right)')],['Allows a pair containing the same digit twice.','Accepts a second digit with the wrong frequency.'],pair_oracle,random_pair,['Count every digit in the full string once.','Scan adjacent positions from left to right.','Check distinctness and compare both global counts with the digit values.','Returning at the first success enforces the required order.'],'O(n)','O(1)',3),
3442:entry('maximum_odd_even_frequency_difference',[('s','str')],'int',['strings','hash maps','counting'],['Count every lowercase character in s.','Choose one character with odd frequency and one with even frequency.','Return the maximum odd frequency minus the minimum even frequency.'],[(['aaaaabbc'],'a occurs five times and b twice, giving the maximum difference three.'),(['aabbccc'],'The best odd frequency is three and the even frequency is two, giving one.')],[[s] for s in ['aab','aabbc','aabbccc','aaaaabbc','aaabbbb','abbbcc','aaaabbc','zzzyy','aabbbbccccc','xxxyyyyzz','abcdd','ppqqq','mnnnpp','aaaaaabbc']],FREQUENCY,[FREQUENCY.replace('max(value','min(value'),FREQUENCY.replace('min(value for value in values if value%2==0)','max(value for value in values if value%2==0)')],['Chooses the smallest odd frequency.','Subtracts the largest even frequency instead of the smallest.'],frequency_oracle,random_frequency,['Build a frequency table.','Among odd counts, the largest maximizes the positive term.','Among even counts, the smallest minimizes the subtracted term.','Their difference is therefore maximal over all allowed character pairs.'],'O(n)','O(1)',3),
}
