"""First slice of workbook batch 135."""

from math import isqrt

from .import_batch_055 import entry


def alternating_oracle(args):
    digits=[int(char) for char in str(args[0])]
    return sum(value if index%2==0 else -value for index,value in enumerate(digits))


def random_alternating(rng):return [rng.randint(1,999999999)]


def board_oracle(args):
    values={args[0]}
    while True:
        added={candidate for number in values for candidate in range(1,args[0]+1) if number%candidate==1}
        if added<=values:return len(values)
        values|=added


def random_board(rng):return [rng.randint(1,100)]


def separate_oracle(args):
    result=[]
    for number in args[0]:result.extend(map(int,str(number)))
    return result


def random_separate(rng):return [[rng.randint(1,99999) for _ in range(rng.randint(1,15))]]


def gifts_oracle(args):
    gifts=list(args[0]);steps=args[1]
    for _ in range(steps):
        index=max(range(len(gifts)),key=gifts.__getitem__);gifts[index]=isqrt(gifts[index])
    return sum(gifts)


def random_gifts(rng):return [[rng.randint(1,1000) for _ in range(rng.randint(1,10))],rng.randint(1,15)]


def concatenate_oracle(args):
    nums=args[0];answer=0;left=0;right=len(nums)-1
    while left<=right:
        if left==right:answer+=nums[left]
        else:answer+=int(str(nums[left])+str(nums[right]))
        left+=1;right-=1
    return answer


def random_concatenate(rng):return [[rng.randint(1,999) for _ in range(rng.randint(1,15))]]


ALTERNATING='''\
def alternating_digit_sum(n):
    answer=0
    for index,char in enumerate(str(n)):answer+=int(char) if index%2==0 else -int(char)
    return answer
'''

BOARD='''\
def count_distinct_board_numbers(n):
    return 1 if n==1 else n-1
'''

SEPARATE='''\
def separate_array_digits(nums):
    return [int(char) for number in nums for char in str(number)]
'''

GIFTS='''\
def remaining_gifts_after_k(gifts,k):
    import heapq
    heap=[-value for value in gifts];heapq.heapify(heap)
    for _ in range(k):
        largest=-heapq.heappop(heap);heapq.heappush(heap,-__import__('math').isqrt(largest))
    return -sum(heap)
'''

CONCATENATE='''\
def array_concatenation_value(nums):
    left=0;right=len(nums)-1;answer=0
    while left<=right:
        if left==right:answer+=nums[left]
        else:answer+=int(str(nums[left])+str(nums[right]))
        left+=1;right-=1
    return answer
'''


BATCH={
2544:entry('alternating_digit_sum',[('n','int')],'int',['math','digits'],['Read decimal digits from most significant to least significant.','Give the first digit a positive sign and alternate negative, positive, and so on.','Return the signed sum.'],[([521],'The signed digits are five minus two plus one, giving four.'),([111],'One minus one plus one gives one.')],[[n] for n in [1,9,10,11,12,99,100,101,1234,9876,1000,90909,123456789,808080]],ALTERNATING,[ALTERNATING.replace('index%2==0','index%2==1'),ALTERNATING.replace('else -int(char)','else int(char)')],['Starts with a negative sign instead of a positive sign.','Adds every digit and ignores alternating signs.'],alternating_oracle,random_alternating,['Convert n to its decimal string to preserve left-to-right order.','Use the digit index parity to choose its sign.','Add even-index digits and subtract odd-index digits.','Zero-based even positions are exactly the first, third, and later positive-sign positions.'],'O(log n)','O(log n)',3),
2549:entry('count_distinct_board_numbers',[('n','int')],'int',['math','invariants'],['Initially only n is on the board.','Repeatedly, for every board value x, add every positive i with x%i=1.','Return the number of distinct values after 10^9 days, when the process is stable.'],[([5],'Values four, three, and two are eventually added beside the original five, giving four distinct values.'),([1],'No new positive value satisfies one modulo i equals one, so only one remains.')],[[n] for n in [2,3,4,6,7,8,9,10,20,25,50,99,100,37]],BOARD,[BOARD.replace('n-1','n'),BOARD.replace('n==1','n<=2')],['Returns n and includes a value that the stable set does not gain for n greater than one.','Treats n=2 like the n=1 special case, returning one instead of n-1 coincidentally same; this negative is replaced below.'],board_oracle,random_board,['Handle n=1 separately.','For each x greater than two, x%(x-1)=1, so the process repeatedly adds x-1 down to two.','The stabilized count is therefore n-1.','Closure supplies exactly values two through n, while one can never be added because every value modulo one is zero.'],'O(1)','O(1)',3),
2553:entry('separate_array_digits',[('nums','list[int]')],'list[int]',['arrays','strings'],['Replace each positive integer by its decimal digits from left to right.','Preserve the original order of numbers and the digit order within each number.','Return one flattened list of integer digits.'],[([[13,25,83,77]],'Reading each number left to right yields [1,3,2,5,8,3,7,7].'),([[7,1,3,9]],'All values are already one digit, so the output is unchanged.')],[[a] for a in [[1],[10],[100],[9,99],[12,3],[999,1],[101,202],[5,67,890],[1000,2],[42,42],[8,80,800],[12345],[1,234,56],[90,1,10]]],SEPARATE,[SEPARATE.replace('str(number)','str(number)[::-1]'),SEPARATE.replace('for number in nums for char','for number in reversed(nums) for char')],['Reverses the digits within every number.','Reverses the order of the input numbers.'],separate_oracle,random_separate,['Iterate numbers in their original order.','Convert each number to a decimal string and iterate its characters left to right.','Convert each character back to an integer and append it.','The nested iteration order exactly matches the required number-major then digit-major output.'],'O(total digits)','O(total digits)',3),
2558:entry('remaining_gifts_after_k',[('gifts','list[int]'),('k','int')],'int',['arrays','heaps','simulation'],['Repeat exactly k times.','Each step chooses a currently largest pile and replaces it with floor(sqrt(pile)).','Return the sum of all pile sizes afterward.'],[([[25,64,9,4,100],4],'Repeatedly reducing the current largest piles leaves a total of twenty-nine gifts.'),([[1,1,1,1],4],'The square root of one is one, so the total remains four.')],[[g,k] for g,k in [([4],1),([4],2),([9,1],1),([16,9],2),([100,1],3),([2,2,2],2),([1],10),([25,36,49],3),([10,10],1),([64,16,4],4),([3,8,15],2),([1000,100,10],5),([5,5,5,5],3),([81,80],2)]],GIFTS,[GIFTS.replace('isqrt(largest)','largest//2'),GIFTS.replace('heapq.heappop(heap)','heap.pop()')],['Halves a pile instead of taking its integer square root.','Removes the end of the heap list rather than the heap maximum.'],gifts_oracle,random_gifts,['A max-priority queue is needed because every step selects the current largest pile.','Store negated sizes in Python’s min-heap.','Pop the largest, replace it by integer square root, push it back, and finally sum.','Heap extraction enforces the required greedy choice at every step, so the simulation matches the process exactly.'],'O((n+k) log n)','O(n)',3),
2562:entry('array_concatenation_value',[('nums','list[int]')],'int',['arrays','two pointers','strings'],['Repeatedly take the first and last remaining values.','When two values remain at the ends, concatenate their decimal representations in first-then-last order and add that integer.','If one middle value remains, add it directly.'],[([[7,52,2,4]],'The concatenations 74 and 522 sum to 596.'),([[5,14,13,8,12]],'Concatenations 512 and 148 plus the middle thirteen total 673.')],[[a] for a in [[1],[1,2],[10,2],[1,2,3],[12,34,56,78],[9,8,7],[100,1],[1,10],[5,5,5,5],[1,20,300],[99,1,2,88],[7,70,700],[123,4,56],[2,3,4,5,6,7]]],CONCATENATE,[CONCATENATE.replace("str(nums[left])+str(nums[right])","str(nums[right])+str(nums[left])"),CONCATENATE.replace('if left==right:answer+=nums[left]','if left==right:answer+=int(str(nums[left])*2)')],['Concatenates the last value before the first value.','Duplicates the unpaired middle number instead of adding it once.'],concatenate_oracle,random_concatenate,['Use one pointer at each end.','For distinct endpoints, concatenate their decimal strings in left-right order and parse the result.','When pointers meet, add the single value; then move both pointers inward.','Each operation removes exactly the endpoints represented by one loop iteration, preserving the specified process.'],'O(total digits)','O(total digits)',3),
}
BATCH[2549]['wrong'][1]='''\
def count_distinct_board_numbers(n):
    return max(1,n-2)
'''
BATCH[2549]['wrong_reasons'][1]='Omits one value from the stable set for every n greater than two.'
BATCH[2558]['wrong'][0]='''\
def remaining_gifts_after_k(gifts,k):
    import heapq
    heap=[-value for value in gifts];heapq.heapify(heap)
    for _ in range(k):
        largest=-heapq.heappop(heap);heapq.heappush(heap,-(largest//2))
    return -sum(heap)
'''
BATCH[2558]['wrong_reasons'][0]='Halves the selected pile instead of replacing it by floor of its square root.'
