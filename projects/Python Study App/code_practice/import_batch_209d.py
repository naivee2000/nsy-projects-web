"""Equal-subarray, almost-unique window, divisible digits, modular counts, and grid reachability."""
from collections import deque

from .import_batch_055 import entry


def equal_subarray_oracle(args):
    nums, allowed = args; best = 0
    for value in set(nums):
        positions = [index for index, current in enumerate(nums) if current == value]
        for left in range(len(positions)):
            for right in range(left, len(positions)):
                kept = right - left + 1
                if positions[right] - positions[left] + 1 - kept <= allowed: best = max(best, kept)
    return best


def random_equal_subarray(rng): return [[rng.randint(1, 6) for _ in range(rng.randint(1, 22))], rng.randint(0, 8)]


def almost_unique_oracle(args):
    nums, required, width = args
    return max((sum(nums[left:left+width]) for left in range(len(nums)-width+1) if len(set(nums[left:left+width])) >= required), default=0)


def random_almost_unique(rng):
    size = rng.randint(1, 20); width = rng.randint(1, size)
    return [[rng.randint(1, 20) for _ in range(size)], rng.randint(1, width), width]


def special_number_oracle(args):
    number = args[0]; best = len(number)
    for mask in range(1 << len(number)):
        kept = ''.join(number[index] for index in range(len(number)) if mask >> index & 1)
        value = int(kept) if kept else 0
        if value % 25 == 0: best = min(best, len(number) - len(kept))
    return best


def random_special_number(rng):
    length = rng.randint(1, 10)
    return [str(rng.randint(1, 9)) + ''.join(str(rng.randint(0, 9)) for _ in range(length - 1))]


def interesting_oracle(args):
    nums, modulo, target = args; answer = 0
    for left in range(len(nums)):
        count = 0
        for right in range(left, len(nums)):
            count += nums[right] % modulo == target
            answer += count % modulo == target
    return answer


def random_interesting(rng):
    modulo = rng.randint(1, 8)
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 20))], modulo, rng.randrange(modulo)]


def reachable_oracle(args):
    sx, sy, fx, fy, seconds = args; frontier = {(sx, sy)}
    for _ in range(seconds):
        frontier = {(x+dx, y+dy) for x,y in frontier for dx in (-1,0,1) for dy in (-1,0,1) if dx or dy}
    return (fx, fy) in frontier


def random_reachable(rng):
    return [rng.randint(1,7), rng.randint(1,7), rng.randint(1,9), rng.randint(1,9), rng.randint(0,6)]


EQUAL_SUBARRAY = '''def longest_equal_subarray(nums,k):
    from collections import Counter
    counts=Counter();left=0;most=0
    for right,value in enumerate(nums):
        counts[value]+=1;most=max(most,counts[value])
        if right-left+1-most>k:
            counts[nums[left]]-=1;left+=1
    return most
'''


ALMOST_UNIQUE = '''def maximum_almost_unique_sum(nums,m,k):
    from collections import Counter
    counts=Counter(nums[:k]);total=sum(nums[:k]);answer=total if len(counts)>=m else 0
    for right in range(k,len(nums)):
        outgoing=nums[right-k];counts[outgoing]-=1
        if counts[outgoing]==0:del counts[outgoing]
        counts[nums[right]]+=1;total+=nums[right]-outgoing
        if len(counts)>=m:answer=max(answer,total)
    return answer
'''


SPECIAL_NUMBER = '''def minimum_special_number_deletions(num):
    answer=len(num)-1 if '0' in num else len(num)
    for ending in ('00','25','50','75'):
        right=num.rfind(ending[1])
        while right>=0:
            left=num.rfind(ending[0],0,right)
            if left>=0:answer=min(answer,len(num)-left-2);break
            right=num.rfind(ending[1],0,right)
    return answer
'''


NO_SINGLE_ZERO = '''def minimum_special_number_deletions(num):
    answer=len(num)
    for ending in ('00','25','50','75'):
        for right in range(len(num)-1,-1,-1):
            for left in range(right-1,-1,-1):
                if num[left]+num[right]==ending:return len(num)-left-2
    return answer
'''


INTERESTING = '''def count_interesting_subarrays(nums,modulo,k):
    from collections import Counter
    counts=Counter({0:1});prefix=0;answer=0
    for value in nums:
        prefix+=value%modulo==k
        answer+=counts[(prefix-k)%modulo]
        counts[prefix%modulo]+=1
    return answer
'''


EXACT_COUNT = '''def count_interesting_subarrays(nums,modulo,k):
    answer=0
    for left in range(len(nums)):
        count=0
        for right in range(left,len(nums)):
            count+=nums[right]%modulo==k
            answer+=count==k
    return answer
'''


REACHABLE = '''def cell_reachable_at_time(sx,sy,fx,fy,t):
    distance=max(abs(sx-fx),abs(sy-fy))
    if distance==0:return t!=1
    return distance<=t
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept,strategy,pseudocode,editorial]


BATCH = {
    2831: entry(
        'longest_equal_subarray',[('nums','list[int]'),('k','int')],'int',['sliding windows','hash maps','arrays'],
        ['nums is nonempty and k is nonnegative.','Delete at most k values; the answer is the longest contiguous equal block in the remaining array.','Return the number of retained equal values, not the original window width.'],
        [([[1,3,2,3,1,3],3],'Deleting two intervening values joins the three occurrences of three.'),([[1,1,2,2,1,1],2],'Deleting both twos joins four ones into the longest equal block.')],
        [[n,k] for n,k in [([1],0),([1,1],0),([1,2],0),([1,2],1),([1,2,1],0),([1,2,1],1),([1,2,3,1],2),([2,2,1,2,2],1),([1,2,1,2,1],2),([3,1,3,2,3,4,3],3),([1,1,2,3,1,1],2),([4,3,4,3,4,3,4],1),([1,2,3,4],4),([2,1,2,1,2,1,2,1],3)]],
        EQUAL_SUBARRAY,
        [EQUAL_SUBARRAY.replace('return most','return right-left+1'),EQUAL_SUBARRAY.replace('>k', '>=k')],
        ['Returns the pre-deletion window width rather than the retained equal count.','Shrinks when exactly k deletions are needed, treating the limit as strict.'],
        equal_subarray_oracle,random_equal_subarray,
        lesson('A window is usable when its non-majority elements can all be deleted.','Track value frequencies and the largest frequency while advancing a sliding window.','Shrink when window_length-most_frequency exceeds k; return the largest retained frequency.','Any feasible equal result corresponds to a window whose other values are deleted, and the window invariant retains every candidate capable of improving the best frequency.'),
        'O(n)','O(n)',5,
    ),
    2841: entry(
        'maximum_almost_unique_sum',[('nums','list[int]'),('m','int'),('k','int')],'int',['sliding windows','hash maps'],
        ['nums is nonempty and 1 <= m <= k <= len(nums).','Consider exactly length-k contiguous windows having at least m distinct values.','Return the largest qualifying sum, or zero if no window qualifies.'],
        [([[2,6,7,3,1,7],3,4],'The qualifying first window [2,6,7,3] has the maximum sum eighteen.'),([[5,9,9,2,4,5,4],1,3],'Every window qualifies, and [5,9,9] has maximum sum twenty-three.')],
        [[n,m,k] for n,m,k in [([1],1,1),([1,1],1,2),([1,1],2,2),([1,2],2,2),([1,2,3],2,2),([1,2,1,2,1],3,3),([5,1,5,2],2,3),([9,1,2,9],3,3),([1,2,3,4,5],4,4),([7,7,8,9],2,2),([2,4,6,8],1,3),([10,1,10,1,10],2,4),([3,3,3,4,5],3,3),([8,2,7,2,6,2],3,4)]],
        ALMOST_UNIQUE,
        [ALMOST_UNIQUE.replace('len(counts)>=m','len(counts)==m'),ALMOST_UNIQUE.replace('Counter(nums[:k])','Counter(nums[:m])').replace('sum(nums[:k])','sum(nums[:m])')],
        ['Accepts exactly m distinct values instead of at least m.','Initializes a length-m window while later sliding as though it had length k.'],
        almost_unique_oracle,random_almost_unique,
        lesson('A fixed-width window needs both its sum and distinct-value count.','Maintain a frequency map and running sum as one value enters and one leaves.','Delete zero-frequency keys, test distinct_count>=m, and update the maximum qualifying sum.','Each length-k window is visited once with exact frequency and sum state, so taking the maximum over qualifying states is exhaustive.'),
        'O(n)','O(k)',5,
    ),
    2844: entry(
        'minimum_special_number_deletions',[('num','str')],'int',['strings','greedy','digits'],
        ['num is a nonempty decimal string without leading zeros.','Delete any digits while preserving the order of those retained; deleting all digits represents zero.','Return the fewest deletions producing a multiple of 25.'],
        [(['2245047'],'Keeping the suffix pattern 50 and deleting the final two digits costs two.'),(['2908305'],'A best retained ending is 00 after three deletions.')],
        [[s] for s in ['1','0','10','25','50','75','100','2005','71345','50555','123456','7000','102030','999999','25001']],
        SPECIAL_NUMBER,
        [NO_SINGLE_ZERO,SPECIAL_NUMBER.replace("('00','25','50','75')","('00','25')")],
        ['Forgets that keeping one zero—or deleting everything—also represents a divisible result.','Searches only endings 00 and 25, omitting 50 and 75.'],
        special_number_oracle,random_special_number,
        lesson('A nonzero decimal multiple of 25 ends in 00, 25, 50, or 75.','Search backward for each two-digit ending and also consider retaining a single zero.','For a found pair at left<right, deletions equal digits after right plus digits between the pair.', 'Any retained number with at least two digits must use one of the four endings; choosing the rightmost feasible pair minimizes deletions for that ending, and the single-zero case covers all shorter results.'),
        'O(n)','O(1)',5,
    ),
    2845: entry(
        'count_interesting_subarrays',[('nums','list[int]'),('modulo','int'),('k','int')],'int',['prefix sums','hash maps','modular arithmetic'],
        ['nums is nonempty, modulo is positive, and 0 <= k < modulo.','Mark indices whose value remainder modulo equals k.','Count nonempty subarrays whose number of marked indices also has remainder k modulo.'],
        [([[3,2,4],2,1],'The three subarrays starting at value three each contain exactly one marked index.'),([[3,1,9,6],3,0],'Exactly two subarrays contain a marked count divisible by three.')],
        [[n,m,k] for n,m,k in [([1],1,0),([1],2,1),([2],2,1),([1,2],2,1),([1,2,3],2,0),([1,1,1],2,1),([3,6,9],3,0),([1,4,7],3,1),([2,5,8,11],3,2),([1,2,3,4],4,1),([5,5,5,5],5,0),([2,3,2,3,2],2,1),([10,20,30,40],3,1),([7,1,7,1,7,1],4,3)]],
        INTERESTING,
        [EXACT_COUNT,INTERESTING.replace('value%modulo==k','value%modulo==0')],
        ['Requires the marked count to equal k instead of merely having remainder k.','Marks multiples of modulo rather than values whose remainder equals k.'],
        interesting_oracle,random_interesting,
        lesson('A subarray marked count is a difference of two prefix marked counts.','Store frequencies of prefix counts modulo modulo and look up the required earlier remainder.','Before recording each current prefix, add count[(current-k) mod modulo] to the answer.','The remainder equation current-previous ≡ k identifies exactly the stored prefix class, and recording afterward excludes empty subarrays.'),
        'O(n)','O(modulo)',5,
    ),
    2849: entry(
        'cell_reachable_at_time',[('sx','int'),('sy','int'),('fx','int'),('fy','int'),('t','int')],'bool',['math','grids','geometry'],
        ['Coordinates are integers and t is nonnegative.','Each second requires a move to one of eight horizontally, vertically, or diagonally adjacent cells.','Return whether the destination can be occupied after exactly t seconds.'],
        [([2,4,7,7,6],'The Chebyshev distance is five, and one extra second can be spent by detouring.'),([3,1,7,3,3],'The Chebyshev distance is four, exceeding the available three seconds.')],
        [[*values] for values in [(1,1,1,1,0),(1,1,1,1,1),(1,1,1,1,2),(1,1,2,1,1),(1,1,2,2,1),(1,1,3,2,1),(1,1,3,2,2),(5,5,2,1,4),(5,5,2,1,3),(2,2,4,4,2),(2,3,8,3,6),(2,3,8,3,5),(10,10,1,1,9),(4,7,4,2,6)]],
        REACHABLE,
        [REACHABLE.replace('max(abs(sx-fx),abs(sy-fy))','abs(sx-fx)+abs(sy-fy)'),REACHABLE.replace('if distance==0:return t!=1','if distance==0:return True')],
        ['Uses Manhattan distance despite diagonal movement.','Misses the single exceptional case: staying at the start is impossible in exactly one required move.'],
        reachable_oracle,random_reachable,
        lesson('Eight-direction movement reaches a displacement in its larger coordinate difference.', 'Use Chebyshev distance, with a special case when start equals finish and t is one.', 'Return distance<=t except return false for zero distance with exactly one second.', 'A shortest route takes max(dx,dy) moves; any extra time can be consumed by two-step reversals or local detours, except a one-step trip cannot leave and return to the same cell.'),
        'O(1)','O(1)',5,
    ),
}
