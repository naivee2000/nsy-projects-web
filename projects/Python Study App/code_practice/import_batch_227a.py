"""Median windows, parallel splitting, alternating products, pair merging, and positive arrays."""
from functools import lru_cache

from .import_batch_055 import entry


def equal_windows_oracle(args):
    nums, width, needed = args
    costs = []
    for start in range(len(nums) - width + 1):
        window = sorted(nums[start : start + width])
        median = window[width // 2]
        costs.append(sum(abs(value - median) for value in window))

    @lru_cache(None)
    def solve(start, left):
        if left == 0:
            return 0
        if len(nums) - start < left * width:
            return float("inf")
        return min(solve(start + 1, left), costs[start] + solve(start + width, left - 1))

    return solve(0, needed)


def random_equal_windows(rng):
    width = rng.randint(2, 5)
    needed = rng.randint(1, min(3, 12 // width))
    size = rng.randint(width * needed, 12)
    return [[rng.randint(-8, 8) for _ in range(size)], width, needed]


def elimination_oracle(args):
    values, split = args
    values = tuple(values)

    @lru_cache(None)
    def solve(indices):
        if len(indices) == 1:
            return values[indices[0]]
        first = indices[0]
        rest = indices[1:]
        answer = float("inf")
        for mask in range(1 << len(rest)):
            left = (first,) + tuple(rest[i] for i in range(len(rest)) if mask >> i & 1)
            if len(left) == len(indices):
                continue
            right = tuple(index for index in indices if index not in left)
            answer = min(answer, split + max(solve(tuple(sorted(left))), solve(tuple(sorted(right)))))
        return answer

    return solve(tuple(range(len(values))))


def random_elimination(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(2, 7))], rng.randint(1, 8)]


def product_oracle(args):
    nums, target, limit = args
    answer = -1
    for mask in range(1, 1 << len(nums)):
        chosen = [nums[i] for i in range(len(nums)) if mask >> i & 1]
        alternating = sum(value if i % 2 == 0 else -value for i, value in enumerate(chosen))
        product = 1
        for value in chosen:
            product *= value
        if alternating == target and product <= limit:
            answer = max(answer, product)
    return answer


def random_product(rng):
    return [
        [rng.randint(0, 6) for _ in range(rng.randint(1, 11))],
        rng.randint(-15, 15),
        rng.randint(1, 100),
    ]


def pair_removal_oracle(args):
    values = list(args[0])
    operations = 0
    while any(values[i] > values[i + 1] for i in range(len(values) - 1)):
        left = min(range(len(values) - 1), key=lambda i: (values[i] + values[i + 1], i))
        values[left : left + 2] = [values[left] + values[left + 1]]
        operations += 1
    return operations


def random_pair_removal(rng):
    return [[rng.randint(-15, 15) for _ in range(rng.randint(1, 12))]]


def positive_oracle(args):
    nums = args[0]
    bad = []
    for left in range(len(nums)):
        total = 0
        for right in range(left, len(nums)):
            total += nums[right]
            if right - left + 1 >= 3 and total <= 0:
                bad.append((left, right))
    for count in range(len(nums) + 1):
        for mask in range(1 << len(nums)):
            if mask.bit_count() != count:
                continue
            if all(any(mask >> index & 1 for index in range(left, right + 1)) for left, right in bad):
                return count


def random_positive(rng):
    return [[rng.randint(-8, 8) for _ in range(rng.randint(3, 11))]]


def xor_triplets_oracle(args):
    nums = args[0]
    return len({nums[i] ^ nums[j] ^ nums[k] for i in range(len(nums)) for j in range(i, len(nums)) for k in range(j, len(nums))})


def random_xor_triplets(rng):
    return [[rng.randint(1, 31) for _ in range(rng.randint(1, 10))]]


def palindrome_rearrangement_oracle(args):
    from itertools import permutations
    text = args[0]
    return min(''.join(candidate) for candidate in set(permutations(text)) if candidate == candidate[::-1])


def random_palindrome_rearrangement(rng):
    size = rng.randint(0, 3)
    half = ''.join(rng.choice('abcde') for _ in range(size))
    middle = rng.choice('abcde') if rng.randrange(2) else ''
    return [half + middle + half[::-1]]


EQUAL_WINDOWS = '''def minimum_equal_subarray_operations(nums, x, k):
    values=sorted(set(nums));rank={value:i+1 for i,value in enumerate(values)};size=len(values)
    counts=[0]*(size+1);sums=[0]*(size+1)
    def add(tree,index,delta):
        while index<=size:tree[index]+=delta;index+=index&-index
    def prefix(tree,index):
        total=0
        while index:total+=tree[index];index-=index&-index
        return total
    def kth(order):
        index=0;step=1<<(size.bit_length()-1)
        while step:
            candidate=index+step
            if candidate<=size and counts[candidate]<order:order-=counts[candidate];index=candidate
            step//=2
        return index+1
    costs=[]
    for index,value in enumerate(nums):
        position=rank[value];add(counts,position,1);add(sums,position,value)
        if index>=x:
            old=nums[index-x];position=rank[old];add(counts,position,-1);add(sums,position,-old)
        if index>=x-1:
            middle=kth((x+1)//2);median=values[middle-1]
            left_count=prefix(counts,middle);left_sum=prefix(sums,middle);total_sum=prefix(sums,size)
            costs.append(median*left_count-left_sum+(total_sum-left_sum)-median*(x-left_count))
    infinity=10**30;previous=[0]*(len(nums)+1)
    for _ in range(k):
        current=[infinity]*(len(nums)+1)
        for end in range(1,len(nums)+1):
            current[end]=current[end-1]
            if end>=x:current[end]=min(current[end],previous[end-x]+costs[end-x])
        previous=current
    return previous[-1]
'''


ELIMINATION = '''def minimum_elimination_time(time_req, split_time):
    import heapq
    heap=list(time_req);heapq.heapify(heap)
    while len(heap)>1:
        first=heapq.heappop(heap);second=heapq.heappop(heap)
        heapq.heappush(heap,second+split_time)
    return heap[0]
'''


PRODUCT = '''def maximum_limited_alternating_product(nums, k, limit):
    states=set();answer=-1
    for value in nums:
        additions={(value,1,min(value,limit+1))}
        for alternating,parity,product in states:
            next_product=0 if value==0 else min(product*value,limit+1)
            additions.add((alternating-value if parity else alternating+value,1-parity,next_product))
        states.update(additions)
    for alternating,_,product in states:
        if alternating==k and product<=limit:answer=max(answer,product)
    return answer
'''


PAIR_REMOVAL = '''def minimum_pair_removal_operations(nums):
    import heapq
    n=len(nums)
    if n<2:return 0
    values=list(nums);previous=[i-1 for i in range(n)];following=[i+1 for i in range(n)];following[-1]=-1
    alive=[True]*n;versions=[0]*n;heap=[]
    def push(left):
        right=following[left]
        if right!=-1:heapq.heappush(heap,(values[left]+values[right],left,right,versions[left],versions[right]))
    inversions=sum(values[i]>values[i+1] for i in range(n-1))
    for i in range(n-1):push(i)
    operations=0
    while inversions:
        while True:
            _,left,right,left_version,right_version=heapq.heappop(heap)
            if alive[left] and alive[right] and following[left]==right and versions[left]==left_version and versions[right]==right_version:break
        before=previous[left];after=following[right]
        if before!=-1:inversions-=values[before]>values[left]
        inversions-=values[left]>values[right]
        if after!=-1:inversions-=values[right]>values[after]
        values[left]+=values[right];versions[left]+=1;alive[right]=False
        following[left]=after
        if after!=-1:previous[after]=left
        if before!=-1:inversions+=values[before]>values[left]
        if after!=-1:inversions+=values[left]>values[after]
        if before!=-1:versions[before]+=1;push(before)
        push(left);operations+=1
    return operations
'''


POSITIVE = '''def minimum_positive_array_replacements(nums):
    boundary=-1;answer=0;prefix=0;largest_eligible=0
    for right,value in enumerate(nums):
        prefix+=value
        if right-boundary>2 and prefix<=largest_eligible:
            answer+=1;boundary=right;prefix=0;largest_eligible=0
        elif right-boundary>=2:
            largest_eligible=max(largest_eligible,prefix-value-nums[right-1])
    return answer
'''


XOR_TRIPLETS = '''def count_unique_xor_triplets(nums):
    pair_values={first^second for first in nums for second in nums}
    return len({pair^third for pair in pair_values for third in nums})
'''


PALINDROME_REARRANGEMENT = '''def smallest_palindromic_rearrangement(s):
    from collections import Counter
    counts=Counter(s);left=[];middle=''
    for char in sorted(counts):
        left.append(char*(counts[char]//2))
        if counts[char]%2:middle=char
    half=''.join(left)
    return half+middle+half[::-1]
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


EQUAL_CASES = [[nums, x, k] for nums, x, k in [
    ([5,-2,1,3,7,3,6,4,-1],3,2),([9,-2,-2,-2,1,5],2,2),([1,1],2,1),
    ([1,5,2,4],2,2),([8,1,9,2,7,3],3,2),([0,0,0,0],2,2),([-5,5,-5,5],2,1),
    ([1,2,100,101,3,4],2,2),([7,1,4,9,2,6,3],3,1),([10,-10,10,-10,10,-10],2,3),
    ([3,3,8,8,2,2],2,3),([6,1,2,9,10,11,4,5],3,2),([-3,-1,-2,8,7,9],3,2),([4,0,4,0,4,0,4,0],2,3)
]]
ELIMINATION_CASES = [[values, split] for values, split in [
    ([10,4,5],2),([10,4],5),([1,1],1),([3,8,2,6],4),([100,1,1],10),([5,5,5,5],2),
    ([9,2,7,1,4],3),([20,19],1),([2,3,5,7,11,13],2),([1,10,100,1000],7),
    ([8,6,4,2,1],9),([12,12,3],4),([99,2,2,2,2],5),([4,9,1,7,3,8,2],6)
]]
PRODUCT_CASES = [[nums, target, limit] for nums, target, limit in [
    ([1,2,3],2,10),([0,2,3],-5,12),([2,2,3,3],0,9),([5],5,5),([5],5,4),
    ([0],0,1),([1,1],0,2),([3,1,4],6,20),([2,5,2],-3,30),([6,6,6],6,40),
    ([1,2,4,8],3,100),([0,4,0,4],0,20),([2,3,5,7],1,200),([12,1,12,1],22,5000)
]]
PAIR_CASES = [[[value for value in values]] for values in [
    [5,2,3,1],[1,2,2],[1],[3,2],[2,1,1],[-1,-2,-3],[4,-2,3,-5,6],[5,5,4,4],
    [10,-10,10,-10],[3,1,2,1,3],[0,0,0],[9,7,5,3,1],[1,3,2,4,0],[8,-1,-1,8,-1]
]]
POSITIVE_CASES = [[[value for value in values]] for values in [
    [-10,15,-12],[-1,-2,3,-1,2,6],[1,2,3],[0,0,0],[-1,-1,-1,-1],[5,-10,5,5],
    [3,-2,-2,3,-2,-2,3],[10,-1,-1,-1,10],[-5,2,2,-5,2,2],[1,1,-3,1,1],
    [8,-9,1,1,1,1],[-2,5,-4,5,-2],[0,1,0,1,0],[7,-20,7,-20,7,7]
]]
XOR_CASES = [[[value for value in values]] for values in [
    [1,3],[6,7,8,9],[1],[1,2],[2,2],[1,2,3],[4,4,7],[1,1,2,2],[5,10,15],
    [7,8,9,10,11],[16,1,31],[3,6,12,24],[1,4,4,9,16],[2,5,8,11,14,17]
]]
PALINDROME_CASES = [[text] for text in [
    'z','babab','daccad','a','aa','aba','cbbc','zzxyxzz','racecar','aabccbaa','m','noon','aaccaa','edcbaabcde'
]]


BATCH = {
    3505: entry('minimum_equal_subarray_operations',[('nums','list[int]'),('x','int'),('k','int')],'int',['arrays','sliding windows','dynamic programming','fenwick trees'],['nums has up to 100,000 integers; 2 <= x and k*x <= len(nums); k <= 15.','One operation changes one value by one. Choose at least k non-overlapping length-x subarrays whose values become equal within each chosen subarray.','Different chosen subarrays may use different final values; minimize the total operations.'],[([[5,-2,1,3,7,3,6,4,-1],3,2],'Choosing indices 1..3 and 5..7 costs five and three changes, totaling eight.'),([[9,-2,-2,-2,1,5],2,2],'The two adjacent -2 pairs can be formed with three total changes.')],EQUAL_CASES,EQUAL_WINDOWS,[EQUAL_WINDOWS.replace('(x+1)//2','1'),EQUAL_WINDOWS.replace('previous[end-x]+costs[end-x]','previous[end-1]+costs[end-x]')],['Always chooses the window minimum instead of a median, so its absolute-change cost is not minimal.','Allows selected windows to overlap by advancing only one position after taking a window.'],equal_windows_oracle,random_equal_windows,lesson('A fixed window is cheapest to equalize at a median; after computing every window cost, the remaining choice is weighted non-overlapping interval DP.','Maintain window counts and sums in Fenwick trees to obtain a median and absolute-distance cost in logarithmic time.','Precompute each length-x cost, then repeat k DP layers where each prefix either skips its last position or takes the ending window.','Median optimality proves every window weight, and the prefix transition enumerates exactly all non-overlapping selections.'),'O(n log n + kn)','O(n)',8),
    3506: entry('minimum_elimination_time',[('time_req','list[int]'),('split_time','int')],'int',['greedy','heaps','parallel scheduling'],['time_req contains 2 to 100,000 positive task durations.','One worker may finish one strain and stop, or spend split_time to create two workers that proceed in parallel.','Strains may be assigned in any order; minimize the time when every strain is eliminated.'],[([[10,4,5],2],'Split once for the ten-unit strain and split the other branch again for four and five; all finish by time twelve.'),([[10,4],5],'One split lets both eliminations run in parallel, finishing after fifteen units.')],ELIMINATION_CASES,ELIMINATION,[ELIMINATION.replace('second+split_time','first+split_time'),ELIMINATION.replace('heapq.heappush(heap,second+split_time)','heapq.heappush(heap,first+second+split_time)')],['Combines from the smaller completion time and underestimates the slower branch.','Adds both branch durations even though the two child workers operate in parallel.'],elimination_oracle,random_elimination,lesson('A split node finishes at split_time plus the slower child; building the schedule backward therefore combines the two smallest completion requirements.','Use a min-heap and repeatedly replace the two smallest requirements by the larger one plus split_time.','Heapify a copy, pop two values, push second+split_time, and continue to one value.','The standard exchange argument moves the two earliest leaves to deepest sibling positions without worsening the maximum completion time.'),'O(n log n)','O(n)',8),
    3509: entry('maximum_limited_alternating_product',[('nums','list[int]'),('k','int'),('limit','int')],'int',['arrays','dynamic programming','subsequences'],['nums has up to 150 values between 0 and 12; limit is 1 to 5,000.','Choose a nonempty subsequence in original order. Its alternating sum is even-position sum minus odd-position sum.','Among subsequences with alternating sum k and product at most limit, return the largest product, or -1 if none exists.'],[([[1,2,3],2,10],'The full subsequence has alternating sum 1-2+3=2 and product six.'),([[2,2,3,3],0,9],'The pair [3,3] has alternating sum zero and the largest permitted product, nine.')],PRODUCT_CASES,PRODUCT,[PRODUCT.replace('alternating-value if parity else alternating+value','alternating+value if parity else alternating-value'),PRODUCT.replace('product<=limit','product<limit')],['Uses the wrong sign for the next selected position.','Rejects products equal to the allowed limit.'],product_oracle,random_product,lesson('A subsequence state needs its alternating sum, the parity of its chosen length, and its product; all three affect a future choice.','Process values in order and extend a snapshot of existing states so each array position is used at most once.','Start a one-value state, extend every prior state with the parity-selected sign, and retain products with one overflow sentinel so a later zero can still make them legal.','Induction over processed prefixes represents every legal subsequence exactly by its sufficient state, including zero-product choices.'),'O(n * reachable states)','O(reachable states)',8),
    3510: entry('minimum_pair_removal_operations',[('nums','list[int]')],'int',['arrays','linked lists','heaps','simulation'],['nums has up to 100,000 signed integers.','While the array is not non-decreasing, merge the adjacent pair with minimum sum; ties use the leftmost pair.','Return how many forced merges occur before the array becomes non-decreasing.'],[([[5,2,3,1]],'Merge 3+1, then the leftmost minimum pair 2+4; [5,6] is non-decreasing after two operations.'),([[1,2,2]],'The input is already non-decreasing, so no merge is performed.')],PAIR_CASES,PAIR_REMOVAL,[PAIR_REMOVAL.replace('values[left]+values[right],left','-(values[left]+values[right]),left'),PAIR_REMOVAL.replace(',left,right,left_version',',-left,right,left_version')],['Uses the maximum-sum adjacent pair instead of the required minimum.','Breaks equal-sum ties toward the right rather than the left.'],pair_removal_oracle,random_pair_removal,lesson('Only the merged pair and its two neighbors change, so rebuilding the whole array after every operation is unnecessary.','Represent current order with previous/next arrays, use a heap for pair sums, and lazily discard stale heap entries.','Track the number of adjacent inversions; merge the valid heap minimum and update only nearby inversion contributions and pairs.','The heap key enforces minimum sum and leftmost ties, while local relinking exactly simulates each forced operation until no inversion remains.'),'O(n log n)','O(n)',8),
    3511: entry('minimum_positive_array_replacements',[('nums','list[int]')],'int',['arrays','greedy','prefix sums'],['nums has 3 to 100,000 signed integers.','A positive array has strictly positive sum for every contiguous subarray of length at least three.','One operation may replace one element by any integer from -10^18 to 10^18; minimize replacements.'],[([[-10,15,-12]],'The only length-three subarray sums to -7, and replacing one of its entries is sufficient.'),([[-1,-2,3,-1,2,6]],'All non-positive long subarrays share an early position, so one replacement fixes them.')],POSITIVE_CASES,POSITIVE,[POSITIVE.replace('right-boundary>2','right-boundary>3'),POSITIVE.replace('prefix<=largest_eligible','prefix<largest_eligible')],['Checks only subarrays of length at least four and misses bad length-three windows.','Treats a zero-sum subarray as valid even though every required sum must be strictly positive.'],positive_oracle,random_positive,lesson('Replacing one selected position by a huge positive value fixes every bad subarray containing it, reducing the task to stabbing all non-positive intervals of length at least three.','Scan by right endpoint and greedily replace the current right endpoint as soon as any uncovered bad interval appears.','Track the prefix sum and largest eligible earlier prefix since the last replacement; reset both after selecting an endpoint.','Earliest-ending interval stabbing is optimal: any solution must hit the detected interval, and moving that hit to its right endpoint cannot hurt a later interval.'),'O(n)','O(1)',6),
    3514: entry('count_unique_xor_triplets',[('nums','list[int]')],'int',['arrays','bit manipulation','enumeration'],['nums has 1 to 1,500 positive integers, each at most 1,500.','A triplet value is nums[i] XOR nums[j] XOR nums[k] for indices i <= j <= k; repeated indices are allowed.','Return the number of distinct values among all such triplets.'],[([[1,3]],'The four ordered-index choices produce only values one and three, so the answer is two.'),([[6,7,8,9]],'Although many triplets exist, their XOR results collapse to four distinct values.')],XOR_CASES,XOR_TRIPLETS,[XOR_TRIPLETS.replace('pair^third','pair|third'),XOR_TRIPLETS.replace('first^second','first^first')],['Uses bitwise OR for the third combination instead of XOR.','Treats every pair XOR as zero and returns only distinct input values.'],xor_triplets_oracle,random_xor_triplets,lesson('Because XOR is commutative and indices may repeat, choosing any three array values can be reordered into nondecreasing indices.','First enumerate every reachable pair XOR, then combine each pair value with every input value.','Build a set of a XOR b, then a set of pair XOR c, and return its size.','The first set represents all two-choice prefixes and the second represents exactly every legal triplet value, with sets removing duplicates.'),'O(n^2 + nP)','O(P)',6),
    3517: entry('smallest_palindromic_rearrangement',[('s','str')],'str',['strings','counting','greedy'],['s is a nonempty lowercase palindrome with length up to 100,000.','Rearrange all characters to form another palindrome.','Return the lexicographically smallest possible palindromic rearrangement.'],[(['z'],'A one-character string is its only rearrangement.'),(['babab'],'Putting the available a pair before the b pair gives abbba, the smallest palindrome.')],PALINDROME_CASES,PALINDROME_REARRANGEMENT,[PALINDROME_REARRANGEMENT.replace('for char in sorted(counts):','for char in sorted(counts,reverse=True):'),PALINDROME_REARRANGEMENT.replace('half[::-1]','half')],['Builds the left half in descending order and returns the largest arrangement.','Copies the left half without reversing it, which can break the palindrome.'],palindrome_rearrangement_oracle,random_palindrome_rearrangement,lesson('A palindrome is fixed by its left half and optional odd-count center; lexicographic order is decided from the left edge.','Place half of every character count into the left side in ascending character order.','Count characters, append count//2 copies in sorted order, choose the odd character as center, and mirror the left half.','Every valid palindrome must use those exact half-counts, and sorting the first half makes the entire result lexicographically minimal.'),'O(n)','O(n)',5),
}
