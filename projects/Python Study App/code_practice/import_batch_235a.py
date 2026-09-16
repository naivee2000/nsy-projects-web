"""Coprime row choices, alternating squares, stable ranges, distinct ranges, and jumps."""
from itertools import product,permutations
from math import gcd
from .import_batch_055 import entry

MOD=10**9+7

def coprime_oracle(args):
    answer=0
    for values in product(*args[0]):
        common=0
        for value in values:common=gcd(common,value)
        answer+=common==1
    return answer%MOD

def random_coprime(rng):
    rows=rng.randint(1,5);cols=rng.randint(1,4)
    return [[[rng.randint(1,20) for _ in range(cols)] for _ in range(rows)]]

def alternating_oracle(args):
    return max(sum((1 if i%2==0 else -1)*value*value for i,value in enumerate(order)) for order in permutations(args[0]))

def random_alternating(rng):return [[rng.randint(-12,12) for _ in range(rng.randint(1,8))]]

def stable_oracle(args):
    values=args[0];answer=0
    for left in range(len(values)):
        for right in range(left+2,len(values)):
            answer+=values[left]==values[right]==sum(values[left+1:right])
    return answer

def random_stable(rng):return [[rng.randint(-8,8) for _ in range(rng.randint(3,16))]]

def distinct_oracle(args):
    nums,k=args;seen=set()
    for left in range(len(nums)):
        total=0
        for right in range(left,len(nums)):
            total+=nums[right]
            if total%k==0:seen.add(tuple(nums[left:right+1]))
    return len(seen)

def random_distinct(rng):
    return [sorted(rng.randint(1,12) for _ in range(rng.randint(1,14))),rng.randint(1,12)]

def calorie_oracle(args):
    return max(sum((order[i]-(0 if i==0 else order[i-1]))**2 for i in range(len(order))) for order in permutations(args[0]))

def random_calorie(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,8))]]


COPRIME='''def count_coprime_row_choices(mat):
    from math import gcd
    mod=10**9+7;states={0:1}
    for row in mat:
        updated={}
        for common,ways in states.items():
            for value in row:
                key=gcd(common,value);updated[key]=(updated.get(key,0)+ways)%mod
        states=updated
    return states.get(1,0)
'''

ALTERNATING='''def maximum_alternating_square_sum(nums):
    squares=sorted(value*value for value in nums);negative=len(nums)//2
    return sum(squares[negative:])-sum(squares[:negative])
'''

STABLE='''def count_stable_boundary_subarrays(capacity):
    prefix=[0]
    for value in capacity:prefix.append(prefix[-1]+value)
    waiting={};answer=0
    for right in range(2,len(capacity)):
        left=right-2;key=(capacity[left],capacity[left]+prefix[left+1]);waiting[key]=waiting.get(key,0)+1
        answer+=waiting.get((capacity[right],prefix[right]),0)
    return answer
'''

DISTINCT='''def count_distinct_divisible_subarrays(nums,k):
    counts={0:1};remainder=answer=0
    for value in nums:
        remainder=(remainder+value)%k;answer+=counts.get(remainder,0);counts[remainder]=counts.get(remainder,0)+1
    start=0
    while start<len(nums):
        end=start+1
        while end<len(nums) and nums[end]==nums[start]:end+=1
        length=end-start
        for size in range(1,length+1):
            if size*nums[start]%k==0:answer-=length-size
        start=end
    return answer
'''

CALORIES='''def maximum_jump_calories(heights):
    values=sorted(heights);left=0;right=len(values)-1;previous=answer=0
    while left<right:
        answer+=(values[right]-previous)**2;answer+=(values[left]-values[right])**2
        previous=values[left];left+=1;right-=1
    answer+=(values[right]-previous)**2
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

C_ROWS=[((1,),),((2,),),((2,3),(4,5)),((2,2),(2,4)),((1,3),(3,4)),((6,10),(9,15),(14,21)),((2,4,6),(3,6,9)),((5,7),(10,14),(15,21)),((8,9,10),(12,15,18),(7,14,28)),((2,3),(4,9),(8,27),(16,81)),((30,42,70),(25,35,55)),((4,6,9),(10,15,21),(14,22,33),(25,49,77))]
C_CASES=[[[list(row) for row in rows]] for rows in C_ROWS]
A_CASES=[[[*values]] for values in ([1],[1,-1],[2,3],[0,2,5],[1,-1,2,-2,3,-4],[4,4,1],[5,-2,7,-1],[0,0,0,9],[3,6,9,12],[8,-8,2,-2,1],[10,1,9,2,8,3,7],[4,-5,6,-7,8,-9,10])]
S_CASES=[[[*values]] for values in ([1,1,1],[0,0,0],[3,1,2,3],[9,3,3,3,8],[1,2,3,4,6],[-4,4,0,0,-8,-4],[5,-2,7,5],[2,1,1,2,1,1,2],[6,3,3,6,3,3,6],[10,5,0,5,10],[4,2,2,4,4,8],[7,-1,3,5,-7,7])]
D_CASES=[[a,k] for a,k in (([1],1),([1,1,1],1),([2,2,2,2,2],6),([1,2,3],2),([1,1,2,2],3),([3,3,3,6,6],6),([1,2,2,3,3,4],5),([5,5,5,5],10),([2,4,6,8],4),([1,1,1,2,2,3],3),([7,7,8,8,9,9],7),([2,3,3,3,4,5,5],9))]
J_CASES=[[[*values]] for values in ([1],[3,3],[1,2],[1,7,8],[5,2,3],[1,2,3,4],[10,1,9,2],[5,5,5,1],[2,8,3,7,4],[1,10,2,9,3,8],[4,12,6,10,8],[20,1,19,2,18,3,17])]

BATCH={
3725:entry('count_coprime_row_choices',[('mat','list[list[int]]')],'int',['matrices','dynamic programming','number theory'],['mat has up to 150 rows and 150 columns, with values from one through 150.','Choose exactly one value from every row.','Count choices whose overall greatest common divisor is one, modulo 1,000,000,007.'],[([[[1,2],[3,4]]],'Three of the four row choices have greatest common divisor one.'),([[[2,2],[2,2]]],'Every selection has greatest common divisor two, so the answer is zero.')],C_CASES,COPRIME,[COPRIME.replace('key=gcd(common,value)','key=common*value'),COPRIME.replace('return states.get(1,0)','return sum(states.values())%mod')],['Multiplies state values instead of taking their greatest common divisor.','Counts every row selection regardless of its final greatest common divisor.'],coprime_oracle,random_coprime,lesson('After processing some rows, only the gcd of the chosen values affects future choices.','Store the number of ways to reach each gcd and combine every state with every value in the next row.','Merge equal new gcds modulo the required modulus and finally read the gcd-one state.','The transition partitions all choices by their exact running gcd, so induction gives every complete selection once.'),'O(rows·cols·V log V)','O(V)',8),
3727:entry('maximum_alternating_square_sum',[('nums','list[int]')],'int',['arrays','sorting','greedy'],['nums contains up to 100,000 signed integers.','Rearrange every value, then add squares at even positions and subtract squares at odd positions.','Return the maximum possible score.'],[([[1,2,3]],'Place squares four and nine in positive positions and square one in a negative position, giving twelve.'),([[1,-1,2,-2,3,-3]],'Assign the three largest squares to positive positions for score sixteen.')],A_CASES,ALTERNATING,[ALTERNATING.replace('negative=len(nums)//2','negative=(len(nums)+1)//2'),ALTERNATING.replace('sorted(value*value for value in nums)','sorted(abs(value) for value in nums)')],['Uses too many negative positions for odd-length arrays.','Optimizes absolute values instead of squared values.'],alternating_oracle,random_alternating,lesson('Only squared magnitudes matter, and the number of positive and negative slots is fixed.','Assign the largest squares to positive even positions and the smallest squares to negative odd positions.','Sort all squares, subtract the first floor(n/2), and add the remainder.','Any arrangement with a smaller square in a positive slot and a larger one in a negative slot improves by swapping them.'),'O(n log n)','O(n)',5),
3728:entry('count_stable_boundary_subarrays',[('capacity','list[int]')],'int',['arrays','prefix sums','hash maps'],['capacity contains three to 100,000 signed integers.','A stable subarray has length at least three.','Its first and last values are equal to each other and to the sum of all strict interior values.'],[([[9,3,3,3,9]],'The whole array and the middle [3,3,3] are stable, giving two.'),([[1,2,3,4,5]],'No equal-boundary subarray also matches its interior sum.')],S_CASES,STABLE,[STABLE.replace('left=right-2','left=right-1'),STABLE.replace('capacity[left]+prefix[left+1]','capacity[left]-prefix[left+1]')],['Admits length-two candidates even though the minimum length is three.','Stores the wrong prefix-sum key for potential left boundaries.'],stable_oracle,random_stable,lesson('For endpoints l and r, stability is equivalent to equal boundary values and prefix[r]=capacity[l]+prefix[l+1].','As r advances, add l=r-2 to a map keyed by exactly those two required left-side quantities.','Query the map with (capacity[r], prefix[r]) and add its frequency.','Every eligible left endpoint enters before its matching rights and the key equality is algebraically identical to both stability conditions.'),'O(n)','O(n)',6),
3729:entry('count_distinct_divisible_subarrays',[('nums','list[int]'),('k','int')],'int',['arrays','prefix sums','hash maps'],['nums is a sorted nondecreasing array of up to 100,000 positive integers.','A subarray is good when its sum is divisible by positive k.','Count distinct value sequences rather than distinct index intervals.'],[([[1,2,3],3],'The distinct good sequences are [1,2], [3], and [1,2,3].'),([[2,2,2,2,2,2],6],'Only lengths three and six form distinct divisible sequences, so the answer is two.')],D_CASES,DISTINCT,[DISTINCT.replace('answer-=length-size','answer-=length-size+1'),DISTINCT.replace('if size*nums[start]%k==0','if nums[start]%k==0')],['Subtracts one too many duplicate occurrences for each equal-value sequence.','Tests a single value instead of the full repeated-sequence sum.'],distinct_oracle,random_distinct,lesson('Ordinary prefix remainders count good index intervals, so only duplicate value sequences need correction.','In a sorted array, a repeated subarray sequence can occur at multiple positions only when it consists of one repeated value.','Count all divisible intervals, then for each equal-value run and qualifying length h subtract runLength-h duplicate copies.','Every nonconstant sorted sequence has a unique boundary location, while each constant sequence is thereby reduced to one count.'),'O(n)','O(k+n)',8),
3730:entry('maximum_jump_calories',[('heights','list[int]')],'int',['arrays','sorting','two pointers','greedy'],['heights contains one to 100,000 positive block heights.','Start at ground height zero and visit each block exactly once without returning to ground.','A jump from a to b scores (a-b)²; maximize the total.'],[([[1,7,9]],'The order 9,1,7 scores 81+64+36=181.'),([[5,2,4]],'The order 5,2,4 scores 25+9+4=38.')],J_CASES,CALORIES,[CALORIES.replace('right=len(values)-1','right=len(values)-2'),CALORIES.replace('previous=values[left]','previous=values[right]')],['Skips the tallest block when initializing the high pointer.','Continues from the high block after jumping down instead of from the low block.'],calorie_oracle,random_calorie,lesson('Squared distance rewards repeatedly crossing the widest remaining height gap.','Because ground is below all blocks, visit the current largest height first, then the current smallest, and repeat inward.','Sort heights and use two pointers while tracking the most recently visited low endpoint.','A convex exchange argument moves extremes earlier without decreasing score; alternating remaining extremes realizes every such improving choice.'),'O(n log n)','O(n)',6),
}
