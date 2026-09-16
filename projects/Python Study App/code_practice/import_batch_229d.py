"""Unlock orders, bounded-range partitions, string operations, triplets, and subsequences."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations

from .import_batch_055 import entry


def unlock_oracle(args):
    complexity = args[0]; answer = 0
    for order in permutations(range(1, len(complexity))):
        unlocked = {0}; valid = True
        for computer in order:
            if not any(previous < computer and complexity[previous] < complexity[computer] for previous in unlocked): valid = False; break
            unlocked.add(computer)
        answer += valid
    return answer % 1_000_000_007


def random_unlock(rng): return [[rng.randint(1, 12) for _ in range(rng.randint(2, 8))]]


def partition_oracle(args):
    nums, k = args
    @lru_cache(None)
    def solve(start):
        if start == len(nums): return 1
        answer = 0; low = high = nums[start]
        for end in range(start, len(nums)):
            low = min(low, nums[end]); high = max(high, nums[end])
            if high - low <= k: answer += solve(end + 1)
        return answer % 1_000_000_007
    return solve(0)


def random_partition(rng):
    nums = [rng.randint(1, 20) for _ in range(rng.randint(2, 13))]; return [nums, rng.randint(0, 10)]


def _segment_cost(source, target):
    mismatch = [index for index, pair in enumerate(zip(source, target)) if pair[0] != pair[1]]
    @lru_cache(None)
    def matching(remaining):
        if not remaining: return 0
        first = remaining[0]; best = matching(remaining[1:])
        for offset in range(1, len(remaining)):
            second = remaining[offset]
            if source[first] == target[second] and source[second] == target[first]:
                best = max(best, 1 + matching(remaining[1:offset] + remaining[offset + 1:]))
        return best
    return len(mismatch) - matching(tuple(mismatch))


def conversion_oracle(args):
    word1, word2 = args; n = len(word1)
    @lru_cache(None)
    def solve(start):
        if start == n: return 0
        best = n
        for end in range(start + 1, n + 1):
            source = word1[start:end]; target = word2[start:end]
            cost = min(_segment_cost(source, target), 1 + _segment_cost(source[::-1], target))
            best = min(best, cost + solve(end))
        return best
    return solve(0)


def random_conversion(rng):
    length = rng.randint(1, 8); return [''.join(rng.choice('abcd') for _ in range(length)), ''.join(rng.choice('abcd') for _ in range(length))]


def triplet_oracle(args):
    nums = args[0]; answer = 0
    for i, j, k in combinations(range(len(nums)), 3):
        answer += nums[i] == 2 * nums[j] and nums[k] == 2 * nums[j]
    return answer % 1_000_000_007


def random_triplets(rng): return [[rng.randint(0, 15) for _ in range(rng.randint(3, 16))]]


def subsequence_oracle(args):
    nums, m = args
    return max(nums[indexes[0]] * nums[indexes[-1]] for indexes in combinations(range(len(nums)), m))


def random_subsequence(rng):
    nums = [rng.randint(-20, 20) for _ in range(rng.randint(1, 11))]; return [nums, rng.randint(1, len(nums))]


UNLOCK = '''def count_unlocking_permutations(complexity):
    modulo=1000000007
    if any(value<=complexity[0] for value in complexity[1:]):return 0
    answer=1
    for value in range(1,len(complexity)):answer=answer*value%modulo
    return answer
'''


PARTITIONS = '''def count_bounded_range_partitions(nums,k):
    from collections import deque
    modulo=1000000007;n=len(nums);maximum=deque();minimum=deque();left=0;dp=[0]*(n+1);prefix=[0]*(n+1);dp[0]=prefix[0]=1
    for right,value in enumerate(nums,1):
        while maximum and nums[maximum[-1]]<=value:maximum.pop()
        while minimum and nums[minimum[-1]]>=value:minimum.pop()
        maximum.append(right-1);minimum.append(right-1)
        while nums[maximum[0]]-nums[minimum[0]]>k:
            if maximum[0]==left:maximum.popleft()
            if minimum[0]==left:minimum.popleft()
            left+=1
        dp[right]=(prefix[right-1]-(prefix[left-1] if left else 0))%modulo
        prefix[right]=(prefix[right-1]+dp[right])%modulo
    return dp[n]
'''


CONVERSION = '''def minimum_string_conversion_operations(word1,word2):
    from collections import Counter
    n=len(word1)
    def cost(left,right,reversed_source):
        pending=Counter();answer=0
        for target_index in range(left,right+1):
            source_index=right-(target_index-left) if reversed_source else target_index
            source,target=word1[source_index],word2[target_index]
            if source!=target:
                if pending[target,source]:pending[target,source]-=1
                else:pending[source,target]+=1;answer+=1
        return answer
    dp=[10**9]*(n+1);dp[0]=0
    for end in range(1,n+1):
        for start in range(end):dp[end]=min(dp[end],dp[start]+cost(start,end-1,False),dp[start]+1+cost(start,end-1,True))
    return dp[n]
'''


TRIPLETS = '''def count_special_triplets(nums):
    from collections import Counter
    modulo=1000000007;left=Counter();right=Counter(nums);answer=0
    for middle in nums:
        right[middle]-=1;answer=(answer+left[2*middle]*right[2*middle])%modulo;left[middle]+=1
    return answer
'''


SUBSEQUENCE = '''def maximum_subsequence_endpoint_product(nums,m):
    minimum=float('inf');maximum=-float('inf');answer=-float('inf')
    for last in range(m-1,len(nums)):
        first=nums[last-m+1];minimum=min(minimum,first);maximum=max(maximum,first)
        answer=max(answer,nums[last]*minimum,nums[last]*maximum)
    return answer
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]


UNLOCK_CASES=[[[*values]] for values in [[1,2],[2,1],[1,2,3],[3,3,3,4,4,4],[1,1,2],[2,3,4],[5,6,7,8],[5,4,6,7],[1,10,2,3],[1,3,2,4,5],[7,8,9,10,11,12],[3,5,4,6],[9,10,11,9],[2,100,3,4,5]]]
PARTITION_CASES=[[nums,k] for nums,k in [([1,2],0),([1,1],0),([3,3,4],0),([9,4,1,3,7],4),([1,2,3],2),([1,5,1],0),([5,1,5],4),([1,10,1,10],9),([2,4,6,8],2),([8,6,4,2],3),([1,3,2,4,3],1),([7,7,7,7],0),([1,100,2,99],3),([4,1,3,2,5],2)]]
CONVERSION_CASES=[[a,b] for a,b in [('a','a'),('a','b'),('ab','ba'),('abcdf','dacbe'),('abceded','baecfef'),('abcdef','fedabc'),('abc','cba'),('abcd','badc'),('aaaa','bbbb'),('abca','aacb'),('xyz','zyx'),('abcabc','cbacba'),('abcd','dcab'),('acebdf','fedcba')]]
TRIPLET_CASES=[[[*nums]] for nums in [[6,3,6],[0,1,0,0],[8,4,2,8,4],[1,2,1],[2,1,2],[0,0,0],[4,2,4,2,4],[10,5,10,5,10],[1,1,1,1],[2,4,2,4,2],[12,6,3,12,6],[8,4,8,4,8,4],[3,6,3,6,3],[100000,50000,100000]]]
SUBSEQUENCE_CASES=[[nums,m] for nums,m in [([5],1),([-5],1),([1,2],2),([-1,-9,2,3,-2,-3,1],1),([1,3,-5,5,6,-4],3),([2,-1,2,-6,5,2,-5,7],2),([1,2,3,4],3),([-1,-2,-3,-4],2),([-10,1,2,-10],3),([0,5,-5,0],2),([9,-8,7,-6,5],4),([3,3,3],2),([-2,4,-6,8],1),([5,-10,2,3,-4,7],4)]]


BATCH={
3577:entry('count_unlocking_permutations',[('complexity','list[int]')],'int',['arrays','combinatorics','permutations'],['complexity has 2 to 100,000 entries; computer zero is the initially unlocked root.','Computer i can be unlocked from an unlocked j only when j<i and complexity[j]<complexity[i].','Count valid orders modulo 1,000,000,007.'],[([[1,2,3]],'Computer zero can unlock either other computer directly, so both remaining orders are valid.'),([[3,3,3,4,4,4]],'Computer one cannot be unlocked because its complexity is not greater than the root complexity.')],UNLOCK_CASES,UNLOCK,[UNLOCK.replace('<=complexity[0]','<complexity[0]'),UNLOCK.replace('range(1,len(complexity))','range(1,len(complexity)-1)')],['Allows a computer with complexity equal to the root even though the comparison must be strict.','Omits the final factorial factor and undercounts valid permutations for length at least three.'],unlock_oracle,random_unlock,lesson('Every computer is directly unlockable from root zero exactly when root has strictly smaller complexity than every other computer.','If that condition fails return zero; otherwise every ordering of the remaining n-1 labels is valid.','Check all complexity[i]>complexity[0], then compute (n-1)! modulo M.','Because root index zero is smaller than every other label, it is a universal predecessor when its complexity is the unique minimum; otherwise the earliest non-greater computer has no valid chain from root.'),'O(n)','O(1)',5),
3578:entry('count_bounded_range_partitions',[('nums','list[int]'),('k','int')],'int',['arrays','dynamic programming','monotonic queues'],['nums has 2 to 50,000 positive integers.','Partition it into nonempty contiguous segments whose maximum minus minimum is at most k.','Return the number of valid full partitions modulo 1,000,000,007.'],[([[9,4,1,3,7],4],'Exactly six segmentations keep every segment range within four.'),([[3,3,4],0],'Only the two partitions that keep value four separate are valid.')],PARTITION_CASES,PARTITIONS,[PARTITIONS.replace('>k','>=k'),PARTITIONS.replace('prefix[left-1] if left else 0','prefix[left] if left else 0')],['Shrinks windows whose range equals k even though equality is allowed.','Subtracts one extra prefix-DP term and omits partitions beginning at the earliest valid start.'],partition_oracle,random_partition,lesson('For each right endpoint, valid segment starts form one suffix interval because extending left can only widen the range.','Maintain that earliest start with monotonic max/min deques and sum prior DP values using prefix sums.','Shrink while max-min>k; set dp[right] to the prefix-sum range over valid starts; accumulate modulo M.','Every partition has one final segment, and the window invariant identifies exactly all starts that make that final segment valid.'),'O(n)','O(n)',5),
3579:entry('minimum_string_conversion_operations',[('word1','str'),('word2','str')],'int',['strings','dynamic programming','counting'],['The lowercase strings have equal length at most 100.','Partition word1 into substrings; within each, replacements, disjoint swaps, and at most one whole-substring reversal each cost one.','Minimize the total operations needed to produce word2.'],[(['abcdf','dacbe'],'Partitioning into ab, c, and df permits one reversal, one swap-equivalent correction, and replacements for a total of four.'),(['abcdef','fedabc'],'Reverse the whole source and then use one swap to reach the target in two operations.')],CONVERSION_CASES,CONVERSION,[CONVERSION.replace('1+cost(start,end-1,True)','cost(start,end-1,True)'),CONVERSION.replace('if pending[target,source]','if False and pending[target,source]')],['Treats substring reversal as free.','Never pairs inverse mismatches into one swap and replaces every mismatch separately.'],conversion_oracle,random_conversion,lesson('After an optional reversal, one swap fixes two mismatches exactly when their source-target pairs are inverses; all others need replacement.','Compute each interval cost in normal and reversed orientation, then use prefix DP over every final substring boundary.','Count directed mismatch pairs, cancel inverse pairs as swaps, compare normal cost with one plus reversed cost, and relax dp[end].','Every chosen partition is represented by its last boundary; within an interval, inverse pairing maximizes two-for-one corrections and remaining mismatches independently require replacements.'),'O(n^3)','O(n)',8),
3583:entry('count_special_triplets',[('nums','list[int]')],'int',['arrays','hash maps','counting'],['nums has 3 to 100,000 nonnegative values.','Count indices i<j<k where both outer values equal twice the middle value.','Return the result modulo 1,000,000,007.'],[([[6,3,6]],'The sole index triple has both outer values equal to twice three.'),([[0,1,0,0]],'Indices 0, 2, and 3 form the one valid all-zero triplet.')],TRIPLET_CASES,TRIPLETS,[TRIPLETS.replace('right[middle]-=1','right[middle]-=0'),TRIPLETS.replace('2*middle','middle')],['Leaves the middle occurrence in the right-side counts, creating invalid reuse when the doubled value equals the middle value zero.','Counts equal outer values instead of values twice the middle.'],triplet_oracle,random_triplets,lesson('For a fixed middle index, every earlier doubled value can pair with every later doubled value.','Maintain value frequencies on the left and right while moving the middle from left to right.','Remove the middle from right, add left[2*x]*right[2*x], then add it to left.','The two counters enforce index order, and their frequency product counts every valid choice of outer indices exactly once at its middle.'),'O(n)','O(n)',5),
3584:entry('maximum_subsequence_endpoint_product',[('nums','list[int]'),('m','int')],'int',['arrays','prefix extrema','subsequences'],['nums has up to 100,000 integers and 1 <= m <= len(nums).','Choose exactly m indices in increasing order.','Maximize the product of values at the first and last chosen indices; for m=1 this is the selected value squared.'],[([[-1,-9,2,3,-2,-3,1],1],'Choosing the singleton negative nine uses it as both endpoints, producing 81.'),([[1,3,-5,5,6,-4],3],'A subsequence beginning at negative five and ending at negative four produces 20.')],SUBSEQUENCE_CASES,SUBSEQUENCE,[SUBSEQUENCE.replace('last-m+1','last-m'),SUBSEQUENCE.replace('nums[last]*minimum,nums[last]*maximum','nums[last]*maximum')],['Allows the first endpoint too far right, leaving fewer than m chosen positions.','Tracks only the largest eligible first value and misses products of two negative endpoints.'],subsequence_oracle,random_subsequence,lesson('For a last index j, any first index at most j-m+1 can be completed to an m-element subsequence.','Maintain the minimum and maximum eligible first values; one of them maximizes its product with the current last value.','As j advances, add nums[j-m+1] to prefix extrema and test nums[j] times both extrema.','All intermediate indices can be chosen arbitrarily, so endpoint spacing is the only feasibility condition; extrema handle both positive and negative products.'),'O(n)','O(1)',5),
}
