"""Fourth reviewed group of workbook batch 113."""

from functools import reduce
from itertools import product
from math import gcd

from .import_batch_055 import entry


def gcd_oracle(args):
    nums = args[0]
    return gcd(min(nums), max(nums))


def difference_oracle(args):
    matrix, target = args
    return min(abs(sum(choice) - target) for choice in product(*matrix))


def widest_oracle(args):
    first, second = args
    best = 0
    for left in range(len(first)):
        sum_first = sum_second = 0
        for right in range(left, len(first)):
            sum_first += first[right]; sum_second += second[right]
            if sum_first == sum_second:
                best = max(best, right - left + 1)
    return best


def scores_oracle(args):
    nums, k = args
    return min(max(group) - min(group) for group in __import__('itertools').combinations(nums, k))


def kth_oracle(args):
    nums, k = args
    return sorted(nums, key=lambda value: (len(value), value), reverse=True)[k - 1]


def random_gcd(rng):
    return [[rng.randint(1, 1000) for _ in range(rng.randint(2, 30))]]


def random_difference(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randint(1, 20) for _ in range(columns)] for _ in range(rows)], rng.randint(1, 80)]


def random_widest(rng):
    size = rng.randint(1, 30)
    return [[rng.randint(0, 10) for _ in range(size)], [rng.randint(0, 10) for _ in range(size)]]


def random_scores(rng):
    size = rng.randint(1, 10)
    return [[rng.randint(0, 100) for _ in range(size)], rng.randint(1, size)]


def random_kth(rng):
    size = rng.randint(1, 30)
    values = rng.sample(range(1, 100000), size)
    return [[str(value) for value in values], rng.randint(1, size)]


GCD = '''\
def greatest_common_divisor_of_extremes(nums):
    from math import gcd
    return gcd(min(nums), max(nums))
'''

DIFFERENCE = '''\
def minimize_chosen_row_difference(mat, target):
    possible = {0}
    for row in mat:
        possible = {total + value for total in possible for value in row}
    return min(abs(total - target) for total in possible)
'''

WIDEST = '''\
def widest_equal_range_sum(nums1, nums2):
    first_index = {0: -1}
    difference = 0
    answer = 0
    for index, (left, right) in enumerate(zip(nums1, nums2)):
        difference += left - right
        if difference in first_index:
            answer = max(answer, index - first_index[difference])
        else:
            first_index[difference] = index
    return answer
'''

SCORES = '''\
def minimum_selected_score_difference(nums, k):
    nums = sorted(nums)
    return min(nums[right] - nums[right - k + 1] for right in range(k - 1, len(nums)))
'''

KTH = '''\
def kth_largest_integer_string(nums, k):
    nums = sorted(nums, key=lambda value: (len(value), value), reverse=True)
    return nums[k - 1]
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1979: entry('greatest_common_divisor_of_extremes',[('nums','list[int]')],'int',['arrays','math','number theory'],
        ['nums contains 2 through 1000 positive integers, each at most 1000.','Find the minimum and maximum values in the entire list.','Return their greatest common divisor.'],
        [([[2,5,6,9,10]],'The extreme values are two and ten, whose greatest common divisor is two.'),([[7,5,6,8,3]],'The minimum three and maximum eight are coprime, so the result is one.')],
        [[a] for a in [[1,1],[1,1000],[2,4],[6,9,15],[12,18,24],[5,10,15,20],[7,7,7],[8,12,16,20],[9,27,81],[14,21,35,49],[100,25,75],[17,34,51],[6,10,15,8],[999,333,666]]],
        GCD,[GCD.replace('min(nums), max(nums)','nums[0], nums[-1]'),GCD.replace('gcd(min(nums), max(nums))','min(nums)')],
        ['Assumes the input is already sorted, so it may use the wrong extremes.','Returns the minimum itself instead of computing a greatest common divisor.'],gcd_oracle,random_gcd,
        lesson('Only the smallest and largest values affect the requested result.','Scan for both extremes, then apply Euclid’s greatest-common-divisor operation.','return gcd(min(nums),max(nums)).','The two extrema are identified exactly, and Euclid’s algorithm returns their greatest positive common divisor.'),'O(n + log V)','O(1)',3),
    1981: entry('minimize_chosen_row_difference',[('mat','list[list[int]]'),('target','int')],'int',['matrices','dynamic programming','sets'],
        ['mat has 1 through 70 rows and columns, with positive values at most 70.','Choose exactly one number from each row.','Return the minimum absolute difference between the chosen sum and target.'],
        [([[[1,2,3],[4,5,6],[7,8,9]],13],'Choosing one, five, and seven reaches thirteen exactly, so the difference is zero.'),([[[1],[2],[3]],100],'The only possible sum is six, which is ninety-four away from the target.')],
        [[m,t] for m,t in [([[1]],1),([[1]],5),([[1,2]],2),([[1],[2],[3]],6),([[1],[2],[3]],100),([[1,2],[3,4]],5),([[1,2],[3,4]],10),([[5,5],[5,5]],10),([[1,10],[1,10],[1,10]],21),([[2,4,6],[1,3,5]],7),([[7,8],[9,10]],1),([[1,2,3],[4,5,6],[7,8,9]],13),([[1,20],[2,30],[3,40]],25),([[6,1,8],[7,2,9],[3,4,5]],14)]],
        DIFFERENCE,[DIFFERENCE.replace('for row in mat:','for row in mat[:-1]:'),DIFFERENCE.replace('for value in row','for value in row[:1]')],
        ['Skips the final row and therefore does not make exactly one choice per row.','Considers only the first entry of every row and misses better alternatives.'],difference_oracle,random_difference,
        lesson('After each row, only the set of reachable partial sums matters.','Start with sum zero and combine every reachable sum with every value in the next row.','possible={0}; for row: possible={s+x for s in possible for x in row}; minimize distance to target.','Induction shows the set contains exactly all sums formed by one choice from every processed row, so the final minimum checks every legal selection.'),'O(rows * reachable_sums * columns)','O(reachable_sums)',6),
    1983: entry('widest_equal_range_sum',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','prefix sums','hash maps'],
        ['The two lists have equal length from 1 through 100000 and contain nonnegative integers.','A range qualifies when its sum in nums1 equals its sum at the same indices in nums2.','Return the maximum qualifying range length, or zero when none exists.'],
        [([[1,1,0,1],[0,1,1,0]],'The range from index zero through two has equal sums, giving width three.'),([[0,1],[1,1]],'Only the second position has equal values, so the widest range has length one.')],
        [[a,b] for a,b in [([1],[1]),([1],[0]),([0],[0]),([1,1],[1,1]),([1,2],[2,1]),([0,1],[1,1]),([1,1,0,1],[0,1,1,0]),([3,0,2],[1,2,2]),([5,5,5],[0,0,0]),([0,0,0],[1,1,1]),([2,1,3,1],[1,2,1,3]),([10,0,0,10],[0,10,10,0]),([1,2,3,4,5],[5,4,3,2,1]),([4,1,0,2],[2,0,1,4])]],
        WIDEST,[WIDEST.replace('first_index = {0: -1}','first_index = {}'),WIDEST.replace("else:\n            first_index[difference] = index","first_index[difference] = index")],
        ['Omits the virtual prefix before index zero and misses qualifying ranges that start at zero.','Overwrites the earliest occurrence of a prefix difference, producing ranges that are too short.'],widest_oracle,random_widest,
        lesson('Equal range sums mean the prefix difference has the same value at both range boundaries.','Track the earliest index for each cumulative nums1-minus-nums2 difference.','Seed difference zero at -1; on repeats maximize current index minus earliest index.','Subtracting equal prefix differences cancels everything outside the range, and retaining the earliest index gives the widest range for each endpoint.'),'O(n)','O(n)',5),
    1984: entry('minimum_selected_score_difference',[('nums','list[int]'),('k','int')],'int',['arrays','sorting','sliding windows'],
        ['nums has 1 through 1000 scores from 0 through 100000; 1 <= k <= len(nums).','Select exactly k scores.','Return the smallest possible difference between the largest and smallest selected scores.'],
        [([[9,4,1,7],2],'Selecting seven and nine gives difference two, which is minimum.'),([[90],1],'Selecting the only score gives a difference of zero.')],
        [[a,k] for a,k in [([1],1),([1,2],1),([1,2],2),([9,4,1,7],2),([9,4,1,7],3),([9,4,1,7],4),([5,5,5],2),([0,100000],2),([3,1,2],2),([10,1,9,2,8],3),([4,8,1,5,9],4),([7,3,3,8],2),([100,50,75,25],2),([6,2,11,3,9,4],3)]],
        SCORES,[SCORES.replace('nums[right - k + 1]','nums[right - k]'),SCORES.replace('range(k - 1, len(nums))','range(k, len(nums))')],
        ['Uses a window of k+1 scores instead of exactly k.','Starts one position late and can miss the best first sorted window.'],scores_oracle,random_scores,
        lesson('For fixed minimum and maximum, choosing interior scores cannot improve the span.','Sort scores; an optimal selection appears inside some consecutive window of k sorted values.','Minimize sorted[i+k-1]-sorted[i] over all windows.','Any k selected scores span at least the k-value sorted window beginning at their smallest rank, so checking every such window includes an optimum.'),'O(n log n)','O(n)',3),
    1985: entry('kth_largest_integer_string',[('nums','list[str]'),('k','int')],'str',['strings','sorting','large integers'],
        ['nums contains 1 through 10000 distinct strings representing positive integers without leading zeros; each has at most 100 digits.','Order values numerically without requiring fixed-width machine integers.','Return the kth largest original string.'],
        [([['3','6','7','10'],4],'In descending numeric order the values are ten, seven, six, and three, so the fourth is three.'),([['2','21','12','1'],3],'The descending order is twenty-one, twelve, two, one; the third value is two.')],
        [[a,k] for a,k in [(['1'],1),(['1','2'],1),(['1','2'],2),(['3','6','7','10'],4),(['2','21','12','1'],3),(['9','10','100'],2),(['999','1000','100'],1),(['12345678901234567890','9'],1),(['5','50','500','5000'],3),(['11','2','10'],2),(['100','99','9'],2),(['8','80','800'],1),(['314','159','265','358'],4),(['100000000000000000000','99999999999999999999'],2)]],
        KTH,[KTH.replace("key=lambda value: (len(value), value)","key=lambda value: value"),KTH.replace('reverse=True','reverse=False')],
        ['Sorts lexicographically, which misorders strings with different lengths.','Sorts from smallest to largest while still indexing as though the order were descending.'],kth_oracle,random_kth,
        lesson('Without leading zeros, more digits always means a larger positive integer; equal-length strings compare lexicographically.','Sort by the pair (length,string) in descending order.','ordered=sorted(nums,key=lambda s:(len(s),s),reverse=True); return ordered[k-1].','The key exactly reproduces numeric ordering for canonical decimal strings without converting values of unbounded size.'),'O(n log n * digits)','O(n)',5),
}
