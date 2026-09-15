"""Alloy search, semi-decreasing spans, towers, frequency deletion, and bitwise splits."""
from collections import Counter

from .import_batch_055 import entry


def alloys_oracle(args):
    _, _, budget, composition, stock, costs = args; answer = 0
    for recipe in composition:
        made = 0
        while sum(max(0,(made+1)*need-have)*price for need,have,price in zip(recipe,stock,costs)) <= budget: made += 1
        answer = max(answer,made)
    return answer


def random_alloys(rng):
    metals=rng.randint(1,4);machines=rng.randint(1,4)
    return [metals,machines,rng.randint(0,80),[[rng.randint(1,5) for _ in range(metals)] for _ in range(machines)],[rng.randint(0,15) for _ in range(metals)],[rng.randint(1,8) for _ in range(metals)]]


def semi_decreasing_oracle(args):
    nums=args[0]
    return max((right-left+1 for left in range(len(nums)) for right in range(left+1,len(nums)) if nums[left]>nums[right]),default=0)


def random_semi_decreasing(rng):return [[rng.randint(-20,20) for _ in range(rng.randint(1,25))]]


def towers_oracle(args):
    heights=args[0];answer=0
    for peak in range(len(heights)):
        total=current=heights[peak]
        for index in range(peak-1,-1,-1):current=min(current,heights[index]);total+=current
        current=heights[peak]
        for index in range(peak+1,len(heights)):current=min(current,heights[index]);total+=current
        answer=max(answer,total)
    return answer


def random_towers(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,20))]]


def empty_array_oracle(args):
    answer=0
    for frequency in Counter(args[0]).values():
        possible=[twos+threes for twos in range(frequency//2+1) for threes in range(frequency//3+1) if 2*twos+3*threes==frequency]
        if not possible:return -1
        answer+=min(possible)
    return answer


def random_empty_array(rng):return [[rng.randint(1,7) for _ in range(rng.randint(2,25))]]


def split_and_oracle(args):
    nums=args[0];best_sum=None;best_parts=0
    for cuts in range(1<<(len(nums)-1)):
        total=0;current=nums[0];parts=1
        for index in range(len(nums)-1):
            if cuts>>index&1:total+=current;current=nums[index+1];parts+=1
            else:current&=nums[index+1]
        total+=current
        if best_sum is None or total<best_sum:best_sum=total;best_parts=parts
        elif total==best_sum:best_parts=max(best_parts,parts)
    return best_parts


def random_split_and(rng):return [[rng.randint(0,31) for _ in range(rng.randint(1,11))]]


ALLOYS='''def maximum_alloys(n,k,budget,composition,stock,cost):
    answer=0
    for recipe in composition:
        def affordable(count):
            return sum(max(0,count*need-have)*price for need,have,price in zip(recipe,stock,cost))<=budget
        low=0;high=1
        while affordable(high):high*=2
        while low<high:
            middle=(low+high+1)//2
            if affordable(middle):low=middle
            else:high=middle-1
        answer=max(answer,low)
    return answer
'''


SEMI='''def longest_semi_decreasing_subarray(nums):
    candidates=[];answer=0
    for index,value in enumerate(nums):
        if not candidates or value>nums[candidates[-1]]:candidates.append(index)
    for right in range(len(nums)-1,-1,-1):
        while candidates and nums[candidates[-1]]>nums[right]:
            answer=max(answer,right-candidates.pop()+1)
    return answer
'''


TOWERS='''def maximum_beautiful_tower_sum(heights):
    size=len(heights);left=[0]*size;stack=[]
    for index,height in enumerate(heights):
        while stack and heights[stack[-1]]>height:stack.pop()
        previous=stack[-1] if stack else -1
        left[index]=(left[previous] if previous>=0 else 0)+height*(index-previous);stack.append(index)
    right=[0]*size;stack=[]
    for index in range(size-1,-1,-1):
        height=heights[index]
        while stack and heights[stack[-1]]>height:stack.pop()
        following=stack[-1] if stack else size
        right[index]=(right[following] if following<size else 0)+height*(following-index);stack.append(index)
    return max(left[index]+right[index]-heights[index] for index in range(size))
'''


EMPTY='''def minimum_operations_to_empty_array(nums):
    from collections import Counter
    answer=0
    for frequency in Counter(nums).values():
        if frequency==1:return -1
        answer+=(frequency+2)//3
    return answer
'''


SPLIT_AND='''def maximum_minimum_score_subarrays(nums):
    segments=0;current=-1
    for value in nums:
        current&=value
        if current==0:segments+=1;current=-1
    return max(1,segments)
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
2861:entry('maximum_alloys',[('n','int'),('k','int'),('budget','int'),('composition','list[list[int]]'),('stock','list[int]'),('cost','list[int]')],'int',['binary search','arrays','optimization'],['n is the number of metals, k is the number of machine recipes, and dimensions agree.','All alloys use one chosen machine; missing units may be purchased at per-metal costs within budget.','Return the maximum number of alloys one machine can produce.'],[([3,2,15,[[1,1,1],[1,1,10]],[0,0,0],[1,2,3]],'The first recipe produces two alloys for twelve coins, while a third exceeds budget.'),([3,2,15,[[1,1,1],[1,1,10]],[0,0,100],[1,2,3]],'Stocked third metal lets the second machine produce five alloys for fifteen coins.')],[[n,k,b,c,s,p] for n,k,b,c,s,p in [(1,1,0,[[1]],[0],[1]),(1,1,10,[[2]],[0],[2]),(1,2,5,[[1],[2]],[0],[1]),(2,1,0,[[1,1]],[1,1],[5,5]),(2,3,10,[[2,1],[1,2],[1,1]],[1,1],[5,5]),(2,2,20,[[1,3],[2,1]],[4,0],[2,3]),(3,1,0,[[1,1,1]],[10,10,10],[1,1,1]),(3,2,8,[[1,2,1],[2,1,2]],[1,4,0],[2,1,3]),(1,1,100,[[5]],[10],[2]),(2,2,1,[[1,1],[3,1]],[0,0],[1,1]),(3,3,30,[[1,4,2],[2,1,3],[3,2,1]],[2,2,2],[3,2,4]),(2,1,15,[[2,2]],[5,0],[1,5]),(4,2,50,[[1,1,1,1],[2,3,1,4]],[0,5,2,9],[1,2,3,1]),(2,2,0,[[1,2],[2,1]],[100,1],[5,5])]],ALLOYS,[ALLOYS.replace('max(0,count*need-have)','count*need'),ALLOYS.replace('for recipe in composition:','for recipe in composition[:1]:')],['Pays for every required unit and ignores existing stock.','Considers only the first machine instead of choosing the best recipe.'],alloys_oracle,random_alloys,lesson('For one recipe, purchase cost grows monotonically with the alloy count.','Binary-search each machine’s maximum affordable count, then take the best.','Compute missing units max(0,count*need-stock), multiply by costs, and expand an upper bound before binary search.','Monotone affordability makes the last true count exact for each machine, and the outer maximum enforces the single-machine choice.'),'O(k*n*log answer)','O(1)',5),
2863:entry('longest_semi_decreasing_subarray',[('nums','list[int]')],'int',['monotonic stacks','arrays'],['nums is nonempty and may contain negative values.','A subarray is semi-decreasing when its first value is strictly greater than its last value; interior order is irrelevant.','Return the greatest such length, or zero if none exists.'],[([[7,6,5,4,3,2,1,6,10,11]],'The prefix ending at the second six has length eight and starts with seven.'),([[57,55,50,60,61,58,63,59,64,60,63]],'The longest qualifying endpoints are sixty-one and sixty, spanning six values.')],[[n] for n in [[1],[1,2],[2,1],[1,1],[3,2,1],[1,3,2],[3,1,2],[1,2,3,4],[4,3,2,1],[2,1,2,1],[5,1,4,2,3],[0,-1,2,-2],[3,3,2,3],[10,5,9,4,8,3]]],SEMI,[SEMI.replace('>nums[right]','>=nums[right]'),SEMI.replace('+1)',')')],['Treats equal endpoints as semi-decreasing.','Returns the index distance rather than the inclusive subarray length.'],semi_decreasing_oracle,random_semi_decreasing,lesson('Only an early large endpoint and a late smaller endpoint matter.','Keep indices of increasing prefix maxima, then scan right endpoints backward and pop every maximum that is larger.','Each popped index is paired with its farthest possible qualifying right endpoint.','A dominated earlier candidate is never useful; reverse scanning ensures the first successful pairing for each retained left index has maximum width.'),'O(n)','O(n)',5),
2865:entry('maximum_beautiful_tower_sum',[('heights','list[int]')],'int',['monotonic stacks','dynamic programming','arrays'],['heights is a nonempty array of positive upper bounds.','Choose positive heights no greater than their bounds that are nondecreasing to a peak and nonincreasing afterward.','Return the maximum possible total chosen height.'],[([[5,3,4,1,1]],'Choosing [5,3,3,1,1] with its peak at index zero totals thirteen.'),([[6,5,3,9,2,7]],'The optimal mountain [3,3,3,9,2,2] totals twenty-two.')],[[h] for h in [[1],[1,1],[1,2],[2,1],[1,2,3],[3,2,1],[2,1,2],[3,3,3],[5,1,5],[3,2,5,5,2,3],[10,1,1,10],[2,7,3,6,4],[8,6,7,5,9],[1,5,2,4,3]]],TOWERS,[TOWERS.replace('return max(left[index]+right[index]-heights[index] for index in range(size))','return sum(heights)'),TOWERS.replace('-heights[index]','')],['Returns the original bounds’ sum even when they are not mountain-shaped.','Counts the peak twice when joining left and right constrained sums.'],towers_oracle,random_towers,lesson('Fixing a peak determines the greatest feasible heights outward by repeated minima.','Use monotonic stacks to compute the optimal constrained prefix and suffix sum for every possible peak.','For each peak combine left_sum+right_sum-peak_height and take the maximum.','The nearest lower bound found by each stack compresses the repeated-minimum runs, producing exactly the same mountain as outward clamping for every peak.'),'O(n)','O(n)',5),
2870:entry('minimum_operations_to_empty_array',[('nums','list[int]')],'int',['counting','greedy','hash maps'],['nums contains at least two positive integers.','One operation removes exactly two or exactly three equal-valued elements.','Return the minimum operations to empty the array, or -1 if impossible.'],[([[2,3,3,2,2,4,2,3,4]],'Frequencies four, three, and two require two, one, and one operations.'),([[2,1,2,2,3,3]],'The lone value one cannot be removed, so the result is -1.')],[[n] for n in [[1,1],[1,2],[1,1,1],[1,1,1,1],[1,1,1,1,1],[1,1,1,1,1,1],[1,1,2,2],[1,1,1,2,2],[1,1,1,1,2,2,2],[2,2,3,3,4,4],[1,2,2,2],[5,5,5,5,5,5,5],[1,1,1,1,1,2,2,2,2],[3,3,3,4,4,4,5,5]]],EMPTY,[EMPTY.replace('(frequency+2)//3','frequency//3'),EMPTY.replace('if frequency==1:return -1','if frequency<1:return -1')],['Uses only groups of three and discards a needed final pair.','Fails to reject a value occurring exactly once.'],empty_array_oracle,random_empty_array,lesson('Each value’s frequency is removed independently using groups of two and three.','Reject frequency one; otherwise use as many threes as possible, replacing one three by two pairs when needed.','The minimum operation count for frequency f>=2 is ceil(f/3)=(f+2)//3.','No operation removes more than three, giving the lower bound ceil(f/3); every f>=2 can attain it using the appropriate mix of twos and threes.'),'O(n)','O(n)',5),
2871:entry('maximum_minimum_score_subarrays',[('nums','list[int]')],'int',['bit manipulation','greedy','arrays'],['nums is a nonempty array of nonnegative integers.','Partition all elements into contiguous nonempty subarrays and minimize the sum of each part’s bitwise-AND score.','Among minimum-score partitions, return the maximum number of parts.'],[([[1,0,2,0,1,2]],'Three consecutive groups can each achieve AND zero, the global minimum sum.'),([[5,7,1,3]],'The entire array AND is one; splitting would increase the minimum total score, so return one.')],[[n] for n in [[0],[1],[0,0],[1,0],[1,1],[1,2],[1,2,3],[7,3,1],[3,0,3],[1,0,2,0],[7,6,4,0,3],[5,5,5],[8,4,2,1],[15,7,3,1,0,6]]],SPLIT_AND,[SPLIT_AND.replace('return max(1,segments)','return segments'),SPLIT_AND.replace('current==0','current==1')],['Returns zero parts when the full-array AND is nonzero, though at least one part is required.','Cuts when the running AND is one rather than zero.'],split_and_oracle,random_split_and,lesson('The smallest possible score sum is the AND of the entire array, and when that value is zero every optimal part can score zero.','Greedily cut whenever the running AND first becomes zero; if it never does, keep one part.','Reset the running AND after every zero segment and count the cuts.','AND can only lose bits as a segment grows, so the earliest zero cut preserves the most suffix opportunities; if total AND is nonzero, every extra positive-score part would increase the sum.'),'O(n)','O(1)',5),
}
