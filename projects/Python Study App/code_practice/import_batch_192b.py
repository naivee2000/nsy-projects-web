"""Typed-string, balanced-digits, divisible-product, adjacent-window, and zero-walk exercises."""
from .import_batch_055 import entry

def typed_oracle(a):return 1+sum(x==y for x,y in zip(a[0],a[0][1:]))
def random_typed(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,80)))]
def balanced_oracle(a):return sum(map(int,a[0][::2]))==sum(map(int,a[0][1::2]))
def random_balanced(r):return [''.join(str(r.randrange(10)) for _ in range(2*r.randint(1,30)))]
def product(n):
    out=1
    for c in str(n):out*=int(c)
    return out
def divisible_oracle(a):
    n,t=a
    while product(n)%t:n+=1
    return n
def random_divisible(r):return [r.randint(1,1000),r.randint(1,10)]
def adjacent_oracle(a):
    nums,k=a
    return any(all(nums[j]<nums[j+1] for j in range(i,i+k-1)) and all(nums[j]<nums[j+1] for j in range(i+k,i+2*k-1)) for i in range(len(nums)-2*k+1))
def random_adjacent(r):
    n=r.randint(2,30);return [[r.randint(-20,20) for _ in range(n)],r.randint(1,n//2)]
def zero_walk_oracle(a):
    nums=a[0];answer=0
    for start,v in enumerate(nums):
        if v:continue
        for direction in (-1,1):
            values=nums[:];i=start;d=direction
            while 0<=i<len(values):
                if values[i]:values[i]-=1;d=-d
                i+=d
            answer+=all(v==0 for v in values)
    return answer
def random_zero_walk(r):return [[r.randint(0,4) for _ in range(r.randint(1,15))]]

TYPED='''def count_possible_original_strings(word):
    return 1+sum(word[i]==word[i-1] for i in range(1,len(word)))
'''
BALANCED='''def is_balanced_digit_string(num):
    even=sum(int(num[i]) for i in range(0,len(num),2))
    odd=sum(int(num[i]) for i in range(1,len(num),2))
    return even==odd
'''
DIVISIBLE='''def smallest_number_with_divisible_digit_product(n,t):
    def product(value):
        answer=1
        for char in str(value):answer*=int(char)
        return answer
    while product(n)%t:n+=1
    return n
'''
ADJACENT='''def has_adjacent_increasing_subarrays(nums,k):
    for start in range(len(nums)-2*k+1):
        first=all(nums[i]<nums[i+1] for i in range(start,start+k-1))
        second=all(nums[i]<nums[i+1] for i in range(start+k,start+2*k-1))
        if first and second:return True
    return False
'''
ZERO='''def count_valid_zero_walk_selections(nums):
    total=sum(nums);left=0;answer=0
    for value in nums:
        right=total-left-value
        if value==0:
            if left==right:answer+=2
            elif abs(left-right)==1:answer+=1
        left+=value
    return answer
'''

BATCH={
3330:entry('count_possible_original_strings',[('word','str')],'int',['strings','counting'],['The displayed word may contain at most one accidental long key press.','The intended word is either unchanged or formed by deleting one character from a run of equal letters.','Return the number of distinct possible intended strings.'],[(['abbcccc'],'The unchanged word plus one deletion position per adjacent equal pair gives five possibilities.'),(['abcd'],'No letter could be removed as an overlong press, so only the unchanged word is possible.')],[[s] for s in ['a','aa','aaa','ab','aab','abb','abba','zzzzz','abcdd','aabbcc','mississippi','book','committee','xxyzz','abababa']],TYPED,[TYPED.replace('1+sum','sum'),TYPED.replace('==','!=')],['Omits the unchanged original word.','Counts changes between runs instead of removable repeated characters.'],typed_oracle,random_typed,['Always count the displayed word itself.','Within a run of length m, deleting any of its m-1 repeated positions produces m-1 distinct shorter candidates across run lengths.','Each adjacent equal pair contributes one such candidate.','Add all adjacent equal pairs to one.'],'O(n)','O(1)',3),
3340:entry('is_balanced_digit_string',[('num','str')],'bool',['strings','sums','parity'],['A digit string is balanced when digits at even indices and odd indices have equal sums.','Indices are zero based.','Return whether the two sums match.'],[(['1234'],'Even-index digits total four while odd-index digits total six, so the string is not balanced.'),(['24123'],'Even indices total seven and odd indices also total seven.')],[[s] for s in ['00','11','10','12','99','1230','0000','9090','1111','1212','2468642','987789','1001','555555']],BALANCED,[BALANCED.replace('even==odd','even!=odd'),BALANCED.replace('range(1,len(num),2)','range(0,len(num),2)')],['Returns the inverse balance condition.','Sums even positions twice.'],balanced_oracle,random_balanced,['Accumulate digits at positions 0,2,4,... separately.','Accumulate positions 1,3,5,... in the other sum.','Compare the completed sums.','The two slices partition every position by the required parity.'],'O(n)','O(1)',3),
3345:entry('smallest_number_with_divisible_digit_product',[('n','int'),('t','int')],'int',['math','digits','brute force'],['Search integers starting at n.','For each candidate, multiply its decimal digits.','Return the first candidate whose digit product is divisible by t.'],[([10,2],'The digit product of ten is zero, which is divisible by two, so return ten.'),([15,3],'The product 1*5 is not divisible by three; 1*6 is, so return sixteen.')],[[n,t] for n,t in [(1,1),(1,2),(8,9),(9,10),(11,2),(15,3),(19,7),(25,6),(33,5),(47,8),(88,9),(99,7),(101,4),(123,10)]],DIVISIBLE,[DIVISIBLE.replace('product(n)%t','product(n)==t'),DIVISIBLE.replace('n+=1','n+=2')],['Tests equality with t rather than divisibility by t.','Skips every other candidate and can miss the minimum.'],divisible_oracle,random_divisible,['Test candidates in increasing order beginning with n.','Compute a candidate’s digit product by multiplying its decimal digits.','Stop when the remainder modulo t is zero.','Increasing enumeration makes the first valid candidate necessarily minimal.'],'O(answer-n times digits)','O(1)',3),
3349:entry('has_adjacent_increasing_subarrays',[('nums','list[int]'),('k','int')],'bool',['arrays','subarrays'],['Choose two adjacent subarrays, each of length k.','Every neighboring pair inside each chosen subarray must be strictly increasing.','Return whether any valid adjacent pair exists.'],[([[2,5,7,8,9,2,3,4,3,1],3],'The adjacent subarrays [7,8,9] and [2,3,4] are both strictly increasing.'),([[1,2,3,4],2],'The adjacent subarrays [1,2] and [3,4] are both strictly increasing.')],[[n,k] for n,k in [([1,1],1),([2,1],1),([1,2,3,4],2),([1,2,1,2],2),([1,2,3,2,3,4],3),([3,2,1,3,4,5],3),([1,3,2,4],2),([1,2,2,3],2),([5,4,3,2],2),([1,2,3,4,5,6],3),([0,1,0,1,0,1],2),([1,4,7,2,5,8],3),([2,3,4,1,2,0],2),([9,8],1),([1,1,2,3,4,5],3)]],ADJACENT,[ADJACENT.replace('start+k','start+k+1'),ADJACENT.replace('<','<=')],['Starts the second window one position too late.','Allows equal neighbors despite strict increase.'],adjacent_oracle,random_adjacent,['Try every possible start of a combined length-2k region.','Check strict increases within its first k positions.','Check the same property independently in the immediately following k positions.','Return true exactly when both checks succeed for one start.'],'O(n*k)','O(1)',3),
3354:entry('count_valid_zero_walk_selections',[('nums','list[int]')],'int',['arrays','prefix sums','simulation'],['Choose an index currently containing zero and an initial direction.','Move one step repeatedly; on a positive value decrement it, reverse direction, then continue.','A selection is valid when the walk leaves the array after reducing every value to zero; return the number of valid index-direction selections.'],[([[1,0,2,0,3]],'Exactly two start-and-direction selections reduce all values to zero.'),([[2,3,4,0,4,1,0]],'No zero has sufficiently balanced sums on its two sides.')],[[x] for x in [[0],[1],[0,0],[1,0],[0,1],[1,0,1],[2,0,1],[1,0,2],[1,0,2,0,3],[2,3,4,0,4,1,0],[0,2,0,2],[3,0,3],[0,1,0],[2,0,2,0],[4,0,3]]],ZERO,[ZERO.replace('left==right','left==right+1'),ZERO.replace('abs(left-right)==1','abs(left-right)<=2')],['Awards two directions for an off-by-one imbalance.','Accepts side sums that differ by two.'],zero_walk_oracle,random_zero_walk,['For a zero start, only the total positive mass on each side matters.','Equal side sums work in both initial directions.','A difference of one works only when starting toward the heavier side; larger differences cannot recover.','Prefix sums compute the two side totals for every zero in one scan.'],'O(n)','O(1)',5),
}
