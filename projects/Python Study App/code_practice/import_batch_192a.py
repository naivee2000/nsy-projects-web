"""Duplicate-number, digit-sum, string-game, bitwise-array, and x-sum exercises."""
from collections import Counter
from .import_batch_055 import entry

def sneaky_oracle(a):
    nums=a[0];return sorted(v for v,c in Counter(nums).items() if c==2)
def random_sneaky(r):
    n=r.randint(2,40);dupes=r.sample(range(n),2);nums=list(range(n))+dupes;r.shuffle(nums);return [nums]
def digit_sum_oracle(a):return min(sum(map(int,str(v))) for v in a[0])
def random_digit_sum(r):return [[r.randint(1,9999) for _ in range(r.randint(1,30))]]
def kth_oracle(a):
    word='a'
    while len(word)<a[0]:word+=''.join(chr((ord(c)-96)%26+97) for c in word)
    return word[a[0]-1]
def random_kth(r):return [r.randint(1,500)]
def bit_array_oracle(a):
    return [next((x for x in range(v) if x|(x+1)==v),-1) for v in a[0]]
def random_bit_array(r):return [[r.choice([2,3,5,7,11,13,17,19,23,29,31]) for _ in range(r.randint(1,20))]]
def xsum_oracle(a):
    nums,k,x=a;out=[]
    for i in range(len(nums)-k+1):
        counts={v:nums[i:i+k].count(v) for v in set(nums[i:i+k])}
        out.append(sum(v*c for v,c in sorted(counts.items(),key=lambda p:(p[1],p[0]),reverse=True)[:x]))
    return out
def random_xsum(r):
    n=r.randint(1,30);k=r.randint(1,n);return [[r.randint(1,12) for _ in range(n)],k,r.randint(1,k)]

SNEAKY='''def find_two_sneaky_numbers(nums):
    seen=set();answer=[]
    for value in nums:
        if value in seen:answer.append(value)
        else:seen.add(value)
    return sorted(answer)
'''
DIGIT='''def minimum_digit_sum_element(nums):
    return min(sum(int(char) for char in str(value)) for value in nums)
'''
KTH='''def kth_character_string_game_one(k):
    return chr(97+(k-1).bit_count()%26)
'''
BIT='''def construct_minimum_bitwise_array(nums):
    answer=[]
    for value in nums:
        if value==2:answer.append(-1);continue
        bit=1
        while value&bit:bit<<=1
        answer.append(value-(bit>>1))
    return answer
'''
XSUM='''def x_sum_of_k_subarrays(nums,k,x):
    from collections import Counter
    answer=[]
    for left in range(len(nums)-k+1):
        counts=Counter(nums[left:left+k])
        chosen=sorted(counts,key=lambda value:(counts[value],value),reverse=True)[:x]
        answer.append(sum(value*counts[value] for value in chosen))
    return answer
'''

BATCH={
3289:entry('find_two_sneaky_numbers',[('nums','list[int]')],'list[int]',['arrays','hash maps','counting'],['nums contains every value from 0 through n-1 once, except two distinct values appear twice.','Return the two repeated values in increasing order.','Do not rely on the duplicates being adjacent.'],[([[0,1,1,0]],'Zero and one are the two values that occur twice.'),([[0,3,2,1,3,2]],'Two and three are repeated among otherwise unique values.')],[[x] for x in [[0,1,2,0,2],[1,0,3,2,1,3],[4,1,0,2,3,2,4],[0,1,2,3,4,0,1],[5,0,1,2,3,4,5,3],[2,0,1,3,4,1,4],[0,2,1,3,2,3],[6,5,4,3,2,1,0,6,1],[0,1,2,3,4,5,2,5],[3,0,2,1,0,3],[1,2,0,1,2],[7,0,1,2,3,4,5,6,7,4],[2,1,0,2,0],[4,3,2,1,0,4,1]]],SNEAKY,[SNEAKY.replace('sorted(answer)','answer'),SNEAKY.replace('if value in seen','if value not in seen')],['Returns encounter order instead of the required increasing order.','Collects first occurrences instead of repeated values.'],sneaky_oracle,random_sneaky,['Track values already encountered.','A value belongs in the answer exactly when it is seen a second time.','Sort the two collected duplicates before returning.','The input multiplicity guarantee makes each duplicate appear exactly once in the collected result.'],'O(n)','O(n)',3),
3300:entry('minimum_digit_sum_element',[('nums','list[int]')],'int',['arrays','digits'],['Replace every number conceptually by the sum of its decimal digits.','Return the smallest resulting digit sum.','All input values are positive integers.'],[([[10,12,13,14]],'The digit sums are 1, 3, 4, and 5, so the minimum is 1.'),([[999,19,28]],'The digit sums are 27, 10, and 10, so return 10.')],[[x] for x in [[1],[9],[10],[11,20],[99,100],[123,456],[9999,8888],[5,14,23],[700,80,9],[101,202,303],[9876,1234],[1000,999],[42,24],[555,111]]],DIGIT,[DIGIT.replace('min(','max(',1),DIGIT.replace('for char in str(value)','for char in str(nums[0])')],['Returns the largest transformed value.','Uses the first number’s digits for every element.'],digit_sum_oracle,random_digit_sum,['Compute each number’s decimal digit sum independently.','Keep the minimum transformed value.','String conversion offers a direct way to enumerate decimal digits.','Every conceptual replacement is inspected, so the maintained minimum is the requested answer.'],'O(total digits)','O(1)',3),
3304:entry('kth_character_string_game_one',[('k','int')],'str',['strings','bit manipulation','simulation'],['Start with word equal to a.','In each operation append a copy of the whole word with every letter advanced by one cyclic alphabet step.','Return the one-indexed k-th character once the word is long enough.'],[([5],'The words grow as a, ab, abbc, and abbcbccd; position five is b.'),([1],'The first character is the initial a.')],[[k] for k in [2,3,4,6,7,8,9,10,16,17,31,32,63,100]],KTH,[KTH.replace('(k-1).bit_count()','k.bit_count()'),KTH.replace('(k-1).bit_count()%26','((k-1).bit_count()+1)%26')],['Counts set bits in k rather than the zero-based position.','Advances every answer by one extra alphabet step.'],kth_oracle,random_kth,['Each expansion doubles the word.','A position in the appended half comes from the matching earlier position plus one letter.','The number of appended-half choices on the path to k-1 equals its set-bit count.','Advance a by that count modulo 26.'],'O(1)','O(1)',3),
3314:entry('construct_minimum_bitwise_array',[('nums','list[int]')],'list[int]',['arrays','bit manipulation'],['For each prime value p, find the smallest nonnegative x such that x bitwise-OR (x+1) equals p.','Return -1 for a value with no solution.','Produce one answer for every input value in the same order.'],[([[2,3,5,7]],'Two has no solution; the minimum values for 3, 5, and 7 are 1, 4, and 3.'),([[11,13]],'Nine OR ten is eleven, while twelve OR thirteen is thirteen.')],[[x] for x in [[2],[3],[5],[7],[11],[13],[17],[19],[23],[29],[31],[2,31],[3,5,7],[11,17,29]]],BIT,[BIT.replace('value-(bit>>1)','value-1'),BIT.replace('value==2','value==3')],['Always clears the lowest bit instead of the highest bit in the trailing-one run.','Treats three as impossible and mishandles two.'],bit_array_oracle,random_bit_array,['Two is the only even prime and has no valid predecessor.','For an odd value, locate the first zero above its trailing run of one bits.','Clear the highest one in that trailing run.','This creates the required carry in x+1 and clears the largest possible bit, yielding the minimum x.'],'O(total bits)','O(n)',3),
3318:entry('x_sum_of_k_subarrays',[('nums','list[int]'),('k','int'),('x','int')],'list[int]',['arrays','sliding windows','hash maps','sorting'],['For every contiguous subarray of length k, count each distinct value.','Keep the x values with greatest frequency, breaking frequency ties in favor of the larger value.','The x-sum is the ordinary sum of all occurrences of the kept values.'],[([[1,1,2,2,3,4,2,3],6,2],'The three windows have x-sums 6, 10, and 12 after frequency and value tie-breaking.'),([[3,8,7,8,7,5],2,2],'Because x equals the window length, every two-element window keeps both occurrences.')],[[n,k,x] for n,k,x in [([1],1,1),([1,2],1,1),([1,2],2,1),([2,2,1],3,1),([1,2,3],3,2),([5,5,5],2,1),([3,2,2,3],3,1),([1,1,2,3,3],4,2),([9,8,7,6],2,1),([4,4,1,1],4,1),([2,1,2,1,3],3,2),([10,10,9],2,2),([1,2,2,3,3,3],4,2),([7,6,7,6],2,1)]],XSUM,[XSUM.replace('(counts[value],value)','(counts[value],-value)'),XSUM.replace('[:x]','[:1]')],['Breaks equal-frequency ties toward the smaller value.','Always keeps one distinct value instead of x values.'],xsum_oracle,random_xsum,['Build a frequency table for each length-k window.','Rank distinct values by frequency first and numeric value second, both descending.','Take at most x ranked values and add value times frequency.','Repeating this for every start produces exactly one x-sum per window.'],'O((n-k+1)*k log k)','O(k)',3),
}
