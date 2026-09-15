"""Triplet scan, infinite windows, product merging, processor pairing, and beautiful strings."""
from itertools import combinations

from .import_batch_055 import entry


def triplet_oracle(args):
    nums=args[0]
    return max([0]+[(nums[i]-nums[j])*nums[k] for i in range(len(nums)) for j in range(i+1,len(nums)) for k in range(j+1,len(nums))])


def random_triplet(rng):return [[rng.randint(1,30) for _ in range(rng.randint(3,15))]]


def infinite_oracle(args):
    nums,target=args;repeat=target//min(nums)+2;values=nums*repeat;best=len(values)+1
    for left in range(len(values)):
        total=0
        for right in range(left,len(values)):
            total+=values[right]
            if total==target:best=min(best,right-left+1);break
            if total>target:break
    return -1 if best>len(values) else best


def random_infinite(rng):return [[rng.randint(1,10) for _ in range(rng.randint(1,8))],rng.randint(1,80)]


def products_oracle(args):
    nums,limit=args;memo={}
    def visit(values):
        key=tuple(values)
        if key in memo:return memo[key]
        best=len(values)
        for index in range(len(values)-1):
            product=values[index]*values[index+1]
            if product<=limit:best=min(best,visit(values[:index]+[product]+values[index+2:]))
        memo[key]=best;return best
    return visit(nums)


def random_products(rng):return [[rng.randint(0,8) for _ in range(rng.randint(1,9))],rng.randint(1,30)]


def processing_oracle(args):
    processors,tasks=args
    def assign(remaining,index):
        if index==len(processors):return 0
        best=float('inf')
        for chosen_indices in combinations(range(len(remaining)),4):
            chosen=set(chosen_indices);finish=processors[index]+max(remaining[i] for i in chosen_indices)
            rest=[value for i,value in enumerate(remaining) if i not in chosen]
            best=min(best,max(finish,assign(rest,index+1)))
        return best
    return assign(tasks,0)


def random_processing(rng):
    size=rng.randint(1,2)
    return [[rng.randint(0,15) for _ in range(size)],[rng.randint(1,20) for _ in range(4*size)]]


def beautiful_oracle(args):
    text,count=args;candidates=[]
    for left in range(len(text)):
        for right in range(left+1,len(text)+1):
            piece=text[left:right]
            if piece.count('1')==count:candidates.append(piece)
    return min(candidates,key=lambda value:(len(value),value),default='')


def random_beautiful(rng):
    text=''.join(rng.choice('01') for _ in range(rng.randint(1,14)))
    return [text,rng.randint(1,len(text))]


TRIPLET='''def maximum_ordered_triplet_value(nums):
    best_value=0;best_prefix=nums[0];best_difference=0
    for value in nums[1:]:
        best_value=max(best_value,best_difference*value)
        best_difference=max(best_difference,best_prefix-value)
        best_prefix=max(best_prefix,value)
    return best_value
'''


NEGATIVE_TRIPLET='''def maximum_ordered_triplet_value(nums):
    return max((nums[i]-nums[j])*nums[k] for i in range(len(nums)) for j in range(i+1,len(nums)) for k in range(j+1,len(nums)))
'''


INFINITE='''def minimum_infinite_subarray_length(nums,target):
    cycle=sum(nums);whole,remainder=divmod(target,cycle);base=whole*len(nums)
    if remainder==0:return base
    values=nums*2;left=0;total=0;best=len(values)+1
    for right,value in enumerate(values):
        total+=value
        while total>remainder:total-=values[left];left+=1
        if total==remainder:best=min(best,right-left+1)
    return -1 if best>len(values) else base+best
'''


PRODUCTS='''def minimum_product_merge_length(nums,k):
    if 0 in nums:return 1
    groups=1;product=nums[0]
    for value in nums[1:]:
        if product*value<=k:product*=value
        else:groups+=1;product=value
    return groups
'''


PROCESSING='''def minimum_processing_time(processor_time,tasks):
    processors=sorted(processor_time);durations=sorted(tasks,reverse=True);answer=0
    for index,available in enumerate(processors):answer=max(answer,available+durations[4*index])
    return answer
'''


BEAUTIFUL='''def shortest_beautiful_binary_substring(s,k):
    left=0;ones=0;answer=''
    for right,char in enumerate(s):
        ones+=char=='1'
        while ones>k:ones-=s[left]=='1';left+=1
        while ones==k and left<right and s[left]=='0':left+=1
        if ones==k:
            candidate=s[left:right+1]
            if not answer or (len(candidate),candidate)<(len(answer),answer):answer=candidate
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
2874:entry('maximum_ordered_triplet_value',[('nums','list[int]')],'int',['arrays','dynamic programming'],['nums contains at least three positive integers.','Choose indices i<j<k and evaluate (nums[i]-nums[j])*nums[k].','Return the maximum value, or zero when every triplet value is negative.'],[([[12,6,1,2,7]],'Indices zero, two, and four give (12-1)*7=77.'),([[1,10,3,4,19]],'Indices one, two, and four give (10-3)*19=133.')],[[n] for n in [[1,2,3],[3,2,1],[3,1,2],[1,3,2],[5,5,5],[10,1,1],[2,9,1,8],[8,2,7,3],[4,1,6,2,9],[9,8,7,6],[1,10,1,10],[6,3,5,2,4],[100,1,2,3],[2,20,3,4,5]]],TRIPLET,[TRIPLET.replace('best_prefix-value','value-best_prefix'),NEGATIVE_TRIPLET],['Reverses the required subtraction order.','Returns a negative value when all ordered triplets are negative instead of clamping to zero.'],triplet_oracle,random_triplet,lesson('At k, only the best earlier difference nums[i]-nums[j] matters.','Scan once while maintaining the largest prefix value and largest valid difference before using the current value as k.','Update answer first, then difference, then prefix maximum to preserve index order.','Each state uses only earlier indices at the moment it contributes, and retains the maximum sufficient statistic for every future multiplication.'),'O(n)','O(1)',5),
2875:entry('minimum_infinite_subarray_length',[('nums','list[int]'),('target','int')],'int',['sliding windows','arrays','prefix sums'],['nums is nonempty and contains positive integers; target is positive.','Repeat nums infinitely and choose one finite contiguous subarray summing exactly to target.','Return its minimum length, or -1 if no such subarray exists.'],[([[1,2,3],5],'The consecutive values two and three form the shortest sum-five subarray.'),([[1,1,1,2,3],4],'Across a cycle boundary, three followed by one reaches four in two positions.')],[[n,t] for n,t in [([1],1),([1],5),([2],3),([2],4),([1,2],3),([1,2],4),([2,4,6,8],3),([2,4,6,8],20),([3,1,2],7),([5,1,1],6),([4,2,3],10),([1,3,5],18),([7,2,4],9),([2,2,3],13)]],INFINITE,[INFINITE.replace('values=nums*2','values=nums'),INFINITE.replace('base=whole*len(nums)','base=remainder*len(nums)')],['Searches only one copy and misses a remainder window crossing the cycle boundary.','Uses the remainder rather than the number of whole cycles when computing the base length.'],infinite_oracle,random_infinite,lesson('Any target decomposes into whole-array sums plus one cyclic remainder window.','Add the length of complete cycles and find the shortest remainder-sum window in two copies using positive-value sliding window.','For target=q*sum+r, return q*n plus the shortest r window; handle r=0 directly.','Every n consecutive infinite-array values sum to one cycle, and positivity makes the two-copy sliding window exhaustive and shrinkable for the residual portion.'),'O(n)','O(n)',5),
2892:entry('minimum_product_merge_length',[('nums','list[int]'),('k','int')],'int',['greedy','arrays'],['nums is nonempty and contains nonnegative integers; k is positive.','Adjacent values may merge into their product only when that product is at most k.','Return the minimum possible remaining array length.'],[([[2,3,3,7,3,5],20],'Greedy groups [2,3,3], [7], and [3,5] give length three.'),([[3,3,3,3],6],'Every adjacent product is nine, so no merge is possible.')],[[n,k] for n,k in [([1],1),([0],1),([2,3],6),([2,3],5),([0,100],1),([100,0,100],1),([1,1,1],1),([2,2,2],4),([2,2,2],8),([5,1,5],5),([3,4,2,2],12),([10,2,1,3],10),([2,5,2,5],10),([7,3,2,1,4],20)]],PRODUCTS,[PRODUCTS.replace('if 0 in nums:return 1','if 0 in nums:return 0'),PRODUCTS.replace('product*value<=k','product*value<k')],['Returns an impossible empty-array length when a zero can instead merge everything into one element.','Treats a product equal to k as forbidden.'],products_oracle,random_products,lesson('With positive values, extending the current merge group only increases its product; a zero can absorb the whole array.','Greedily make each left-to-right product group as long as allowed, starting a new group only when necessary.','Return one immediately for any zero; otherwise multiply while product*next<=k and count forced boundaries.','A failed product cannot be repaired by ending the current group later, while accepting a feasible next value never reduces future grouping options, so earliest maximal groups minimize count.'),'O(n)','O(1)',5),
2895:entry('minimum_processing_time',[('processor_time','list[int]'),('tasks','list[int]')],'int',['sorting','greedy','scheduling'],['There are four tasks per processor and every processor has four one-use cores.','A task finishes at its processor availability time plus its duration.','Assign every task to minimize the latest finishing time.'],[([[8,10],[2,2,3,1,8,7,4,5]],'Give the four longest tasks to the earlier processor; the latest finish is sixteen.'),([[10,20],[2,3,1,2,5,8,4,3]],'Pairing the shorter tasks with availability twenty keeps the optimum at twenty-three.')],[[p,t] for p,t in [([0],[1,2,3,4]),([5],[5,5,5,5]),([0,10],[1,2,3,4,5,6,7,8]),([10,0],[8,7,6,5,4,3,2,1]),([1,2],[9,9,9,9,1,1,1,1]),([3,3],[1,2,3,4,5,6,7,8]),([2,9],[10,1,9,2,8,3,7,4]),([100],[1,1,1,50]),([4,8],[2,2,2,2,6,6,6,6]),([7,1],[3,5,7,9,2,4,6,8]),([0,0],[10,9,8,7,6,5,4,3]),([6,12],[20,1,2,3,4,5,6,7]),([9,2],[11,10,9,8,7,6,5,4]),([5,15],[1,20,2,19,3,18,4,17])]],PROCESSING,[PROCESSING.replace('sorted(tasks,reverse=True)','sorted(tasks)'),PROCESSING.replace('sorted(processor_time)','sorted(processor_time,reverse=True)')],['Pairs the longest tasks with the latest processor group by sorting durations upward.','Pairs late processors with long tasks rather than balancing them against early availability.'],processing_oracle,random_processing,lesson('Only the longest task assigned to each four-core processor determines that processor’s finish.','Sort processors early-to-late and tasks long-to-short, assigning consecutive groups of four.','Pair each early availability with the next four longest remaining tasks and track availability plus the group maximum.','An exchange that pairs a longer task with an earlier processor cannot increase the maximum of the two affected completion times, establishing the opposite-order greedy assignment.'),'O(n log n)','O(n)',5),
2904:entry('shortest_beautiful_binary_substring',[('s','str'),('k','int')],'str',['sliding windows','strings'],['s is a nonempty binary string and k is positive.','A beautiful substring contains exactly k ones.','Return the shortest beautiful substring, breaking length ties lexicographically; return an empty string if none exists.'],[(['100011001',3],'The shortest candidates have length five, and 11001 is lexicographically smallest.'),(['1011',2],'The adjacent substring 11 is shorter than the other two-one candidates.')],[[s,k] for s,k in [('0',1),('1',1),('000',1),('111',1),('111',2),('101',2),('1001',2),('01010',2),('0011100',3),('1010101',3),('0001000',1),('110011',2),('1000010001',2),('0110100110',4)]],BEAUTIFUL,[BEAUTIFUL.replace("while ones==k and left<right and s[left]=='0'", "while ones==k and left<right and s[left]=='1'"),BEAUTIFUL.replace('(len(candidate),candidate)<(len(answer),answer)','len(candidate)<len(answer)')],['Trims leading ones instead of irrelevant leading zeros and loses required matches.','Keeps the first shortest candidate without applying the lexicographic tie-break.'],beautiful_oracle,random_beautiful,lesson('For exactly k ones, leading zeros only make a candidate longer.','Use a sliding window with at most k ones, trim leading zeros at equality, and compare candidates by (length,string).','Shrink past excess ones; when the count is k, remove left zeros and update the best tuple.','Every shortest k-one interval begins and ends with one, and the scan reaches that canonical interval for each right endpoint; tuple comparison enforces both objectives.'),'O(n^2) due to returned-string comparisons','O(n)',5),
}
