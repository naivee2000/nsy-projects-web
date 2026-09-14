"""Second slice of workbook batch 124."""

from itertools import product

from .import_batch_055 import entry


def candies_oracle(args):
    candies, children = args
    return max((share for share in range(1, max(candies) + 1)
                if sum(pile // share for pile in candies) >= children), default=0)


def random_candies(rng):
    return [[rng.randint(1, 40) for _ in range(rng.randint(1, 9))], rng.randint(1, 60)]


def consecutive_oracle(args):
    nums = args[0]
    return set(nums) == set(range(min(nums), min(nums) + len(nums)))


def random_consecutive(rng):
    return [[rng.randint(-12, 12) for _ in range(rng.randint(1, 15))]]


def parity_oracle(args):
    digits = str(args[0])
    candidates = []
    for replacement in product(*["02468" if int(char) % 2 == 0 else "13579" for char in digits]):
        if replacement[0] != "0" and sorted(c for c in replacement if int(c) % 2) == sorted(c for c in digits if int(c) % 2) and sorted(c for c in replacement if int(c) % 2 == 0) == sorted(c for c in digits if int(c) % 2 == 0):
            candidates.append(int("".join(replacement)))
    return max(candidates)


def random_parity(rng):
    return [rng.randint(1, 99999)]


def product_oracle(args):
    nums, increments = args
    best = 0
    def allocate(index, remaining, values):
        nonlocal best
        if index == len(values) - 1:
            candidate = values[:]
            candidate[index] += remaining
            result = 1
            for value in candidate:
                result *= value
            best = max(best, result)
            return
        for amount in range(remaining + 1):
            values[index] += amount
            allocate(index + 1, remaining - amount, values)
            values[index] -= amount
    allocate(0, increments, list(nums))
    return best % 1_000_000_007


def random_product(rng):
    return [[rng.randint(0, 9) for _ in range(rng.randint(1, 6))], rng.randint(0, 8)]


def addition_oracle(args):
    left, right = args
    return left - (-right)


def random_addition(rng):
    return [rng.randint(-10000, 10000), rng.randint(-10000, 10000)]


CANDIES = '''\
def maximum_equal_candy_share(candies,k):
    low,high=1,max(candies);answer=0
    while low<=high:
        middle=(low+high)//2
        if sum(pile//middle for pile in candies)>=k:answer=middle;low=middle+1
        else:high=middle-1
    return answer
'''

CONSECUTIVE = '''\
def is_consecutive_array(nums):
    return len(set(nums))==len(nums) and max(nums)-min(nums)+1==len(nums)
'''

PARITY = '''\
def largest_integer_by_parity_swaps(num):
    digits=list(str(num));even=sorted((char for char in digits if int(char)%2==0),reverse=True);odd=sorted((char for char in digits if int(char)%2),reverse=True)
    return int(''.join((odd if int(char)%2 else even).pop(0) for char in digits))
'''

PRODUCT = '''\
def maximum_product_after_increments(nums,k):
    import heapq
    values=list(nums);heapq.heapify(values)
    for _ in range(k):heapq.heapreplace(values,values[0]+1)
    answer=1
    for value in values:answer=answer*value%1000000007
    return answer
'''

ADDITION = '''\
def add_two_integers(num1,num2):
    return num1+num2
'''


BATCH = {
    2226: entry('maximum_equal_candy_share',[('candies','list[int]'),('k','int')],'int',['arrays','binary search'],['A pile may be split into smaller piles, but piles cannot be combined.','Each of k children receives one pile containing the same positive number of candies.','Unused candies are allowed; return zero if every child cannot receive even one.'],[([[5,8,6],3],'Shares of five produce one portion from every pile, while six produces only two portions.'),([[2,5],11],'Only seven candies exist, so eleven children cannot each receive one candy.')],[[c,k] for c,k in [([5,8,6],3),([2,5],11),([1],1),([1],2),([10],3),([4,4,4],6),([100,1],2),([7,7],1),([3,6,9],5),([9,10,11],7),([1,1,1,1],4),([8,16,24],8),([5,5,5],20),([20,30],9),([2,100,2],10),([6,7,8,9],12)]],CANDIES,[CANDIES.replace('>=k','>k'),CANDIES.replace('high=middle-1','high=middle')],['Requires more than k portions and rejects a share that serves exactly k children.','Does not move the upper boundary below an infeasible midpoint, so some searches stall or time out.'],candies_oracle,random_candies,['For a proposed share x, pile//x portions can be made, and feasibility decreases monotonically as x grows.','Binary-search the largest x whose total portion count is at least k.','Move low above feasible midpoints while saving them; move high below infeasible midpoints.','Monotonicity preserves all possible answers in the search interval, and the final saved feasible midpoint is the maximum equal share.'],'O(n log max(candies))','O(1)',6),
    2229: entry('is_consecutive_array',[('nums','list[int]')],'bool',['arrays','hash sets'],['The array is consecutive when it contains every integer from its minimum through its maximum exactly once.','The original order does not matter and values may be negative.','Return false for duplicates or any missing value.'],[([[1,3,4,2]],'The set is exactly {1,2,3,4}, so all four consecutive values are present.'),([[1,3]],'The value two is missing between the minimum and maximum.')],[[x] for x in [[1],[1,3,4,2],[1,3],[-2,-1,0],[0,0],[5,4,3,2],[10,12,11],[-3,-1,-2,0],[1,2,2,3],[100,101],[7,9,8,10],[-1,1,0],[-5,-3,-4],[2,4,5,3],[9,8,7,6,5],[1,2,4,5]]],CONSECUTIVE,[CONSECUTIVE.replace('len(set(nums))==len(nums)','True'),CONSECUTIVE.replace('+1==len(nums)','==len(nums)')],['Checks only the numeric span and accepts duplicates that conceal missing values.','Omits the inclusive endpoint adjustment and rejects valid consecutive arrays.'],consecutive_oracle,random_consecutive,['A consecutive set has no duplicates and its inclusive numeric span equals its size.','Use a set for uniqueness, then compare max-min+1 with the array length.','Return len(set(nums))==len(nums) and max(nums)-min(nums)+1==len(nums).','Distinct integers filling an interval of exactly n positions must occupy every position; either failed condition proves a duplicate or gap.'],'O(n)','O(n)',3),
    2231: entry('largest_integer_by_parity_swaps',[('num','int')],'int',['greedy','sorting'],['You may swap digits only when both digits have the same parity.','Thus each position keeps its original even-or-odd class.','Return the largest integer reachable through any number of allowed swaps.'],[([1234],'Place the largest odd digits in odd positions and largest even digits in even positions to obtain 3412.'),([65875],'Reordering evens 6,8 and odds 5,7,5 yields 87655.')],[[x] for x in [1,2,10,12,1234,65875,13579,2468,10203,987654,1000,1112,9090,314159,80817,7654321]],PARITY,[PARITY.replace('reverse=True','reverse=False'),PARITY.replace("odd if int(char)%2 else even","even if int(char)%2 else odd")],['Places the smallest available same-parity digit first, producing the minimum arrangement.','Pulls digits from the opposite parity pool and violates the allowed-swap invariant.'],parity_oracle,random_parity,['Allowed swaps can permute all even digits among even positions and all odd digits among odd positions.','To maximize lexicographically, place the largest available digit of the required parity at each position.','Sort both parity groups descending and consume the matching group while scanning the original positions.','The earliest position dominates every later one, so choosing its largest feasible same-parity digit is greedily optimal.'],'O(d log d)','O(d)',3),
    2233: entry('maximum_product_after_increments',[('nums','list[int]'),('k','int')],'int',['arrays','greedy','heaps'],['Perform exactly k increments, each adding one to one array value.','Choose increments to maximize the ordinary product, then return it modulo 1,000,000,007.','Input values are nonnegative and k may be zero.'],[([[0,4],5],'Balancing the values at four and five gives the maximum product twenty.'),([[6,3,3,2],2],'Incrementing two to four and one three to four produces 288.')],[[n,k] for n,k in [([0,4],5),([6,3,3,2],2),([1],0),([1],5),([0,0],1),([0,0],2),([1,1],2),([1,2,3],3),([5,5],1),([2,8],4),([0,1,2],4),([9,9,9],3),([3,1,4],0),([1,1,1,1],7),([7,2,5],6),([100,1],3)]],PRODUCT,[PRODUCT.replace('values[0]+1','-values[0]+1'),PRODUCT.replace('range(k)','range(max(0,k-1))')],['Replaces the smallest value using a sign-flipped update rather than incrementing it.','Performs only k-1 increments and leaves one operation unused.'],product_oracle,random_product,['For nonnegative factors, an increment has the greatest multiplicative benefit on a currently smallest value.','Maintain the values in a min-heap and increment its root k times.','After all increments, multiply the heap values modulo 1,000,000,007.','If one value exceeds a smaller value by at least two, moving an increment from the larger to the smaller increases the product, proving the balancing greedy choice.'],'O((n+k) log n)','O(n)',6),
    2235: entry('add_two_integers',[('num1','int'),('num2','int')],'int',['math'],['Both inputs are integers and may be positive, zero, or negative.','Return their arithmetic sum.','The result fits in the supported integer range.'],[([12,5],'Twelve plus five equals seventeen.'),([-10,4],'Adding four to negative ten gives negative six.')],[[a,b] for a,b in [(0,0),(1,2),(12,5),(-10,4),(-1,-1),(100,-100),(999,1),(-50,75),(7,-9),(12345,67890),(-1000,-2000),(42,0),(0,-42),(214,386)]],ADDITION,[ADDITION.replace('num1+num2','num1-num2'),ADDITION.replace('num1+num2','abs(num1)+abs(num2)')],['Subtracts the second input instead of adding it.','Adds magnitudes and therefore mishandles negative operands.'],addition_oracle,random_addition,['The result is the standard arithmetic sum of the two inputs.','Python integer addition already handles signs and zero correctly.','Return num1 + num2 directly.','The addition operator implements exactly the required operation for every permitted integer pair.'],'O(1)','O(1)',1),
}

# Keep known-wrong fixtures quick and demonstrably incorrect, and map the
# workbook's simplest exercise to the catalog rubric's minimum supported level.
BATCH[2226]['wrong'][1] = CANDIES.replace('high=middle-1', 'high=middle-2')
BATCH[2226]['wrong_reasons'][1] = 'Moves the upper boundary two positions and can skip the true maximum share.'
BATCH[2229]['wrong'][0] = '''\
def is_consecutive_array(nums):
    return max(nums)-min(nums)+1<=len(nums)
'''
BATCH[2229]['wrong_reasons'][0] = 'Accepts repeated values whenever duplicates make the array at least as long as its numeric span.'
BATCH[2231]['wrong'][1] = '''\
def largest_integer_by_parity_swaps(num):
    return int(''.join(sorted(str(num),reverse=True)))
'''
BATCH[2231]['wrong_reasons'][1] = 'Sorts all digits together and therefore performs swaps between opposite parities.'
BATCH[2235]['difficulty'] = 3
