"""Ordered sliding medians with an independent sort-each-window oracle."""
import random

from .import_batch_003 import entry


def median_oracle(args):
    nums,k = args
    answer = []
    for start in range(len(nums)-k+1):
        ordered = sorted(nums[start:start+k])
        answer.append((ordered[(k-1)//2]+ordered[k//2])/2)
    return answer


def random_medians(rng):
    n = rng.randint(1,24)
    pool = [-2**31,2**31-1,-1,0,1]+[rng.randint(-100,100) for _ in range(4)]
    return [[rng.choice(pool) for _ in range(n)],rng.randint(1,n)]


MEDIANS = '''\
def sliding_window_medians(nums, k):
    if k == 1:
        return nums[:]
    if k == len(nums):
        ordered = sorted(nums)
        return [(ordered[(k-1)//2]+ordered[k//2])/2]
    values = sorted(set(nums))
    ranks = {value:i+1 for i,value in enumerate(values)}
    size = len(values)
    tree = [0]*(size+1)
    def update(value, delta):
        index = ranks[value]
        while index <= size:
            tree[index] += delta
            index += index & -index
    highest = 1 << (size.bit_length()-1)
    def select(rank):
        index = 0
        bit = highest
        while bit:
            following = index+bit
            if following <= size and tree[following] < rank:
                index = following
                rank -= tree[following]
            bit >>= 1
        return values[index]
    for value in nums[:k]:
        update(value, 1)
    lower_rank = (k+1)//2
    answer = []
    for end in range(k-1,len(nums)):
        if end >= k:
            update(nums[end-k], -1)
            update(nums[end], 1)
        lower = select(lower_rank)
        answer.append(lower if k%2 else (lower+select(lower_rank+1))/2)
    return answer
'''

UP = list(range(100000))
DOWN = UP[::-1]
ALTERNATING = [-2**31,2**31-1]*50000

BATCH = {
480: entry('sliding_window_medians',[('nums','list[int]'),('k','int')],'list[float]',
    ['arrays','sliding-window','binary-search','order-statistics'],
    ['1 <= k <= nums.length <= 100,000; -2^31 <= nums[i] <= 2^31-1.',
     'Return exactly nums.length-k+1 medians, in left-to-right window order. Duplicate values remain separate occurrences.',
     'For even k, average the two middle values; do not round or select only the lower or upper value.',
     'Each answer must be within 0.00001 absolute error of the true median. Integers and finite decimals are accepted.'],
    [([[1,3,-1,-3,5,3,6,7],3],'The first two windows sort to [-1,1,3] and [-3,-1,3], giving 1 and -1. Continue left to right: [1,-1,-1,3,5,6].'),
     ([[1,4,2,3],2],'The windows [1,4], [4,2], and [2,3] have averages 2.5, 3, and 2.5. These are not rounded to integers.')],
    [[a,k] for a,k in (([1],1),([1,2],1),([1,2],2),([-2,-1],2),([2,1,3],2),
      ([5,5,5,5],3),([0,0,1,0,0],3),([9,1,2,3,4],3),([1,2,3,4,5],4),
      ([5,4,3,2,1],3),([-2**31,2**31-1],2),([2**31-1,2**31-1],2),
      ([-2**31,-2**31],2),([1,1,2,2,2,1],4))],
    MEDIANS,[MEDIANS.replace('(lower+select(lower_rank+1))/2','lower').replace('(ordered[(k-1)//2]+ordered[k//2])/2','ordered[(k-1)//2]'),
      MEDIANS.replace('update(nums[end-k], -1)','update(nums[end], -1)')],
    ['Uses the lower middle instead of averaging the two central values in even windows.',
     'Removes the entering value rather than the expired value, leaving the old window distribution in place.'],
    median_oracle,random_medians,
    ['The median is an order statistic of the current window, counting repeated occurrences.',
     'Coordinate-compress all values and maintain their window frequencies in a Fenwick tree. Sliding changes just two counts.',
     'Add the entering value, remove the expired one, and select cumulative ranks (k+1)//2 and k//2+1; average only for even k.',
     'Binary lifting finds a rank from prefix frequencies without scanning all values. Alternatively, two balanced heaps need correct delayed deletion and logical sizes.'],
    'Coordinate compression preserves value order while a Fenwick tree stores current-window multiplicities. '
    'An update changes one count; rank selection skips prefix blocks whose total is smaller than the requested rank. '
    'For odd k one rank suffices, while even k needs the mean of adjacent middle ranks. '
    'Removing the expired occurrence is essential, especially with duplicates. Preprocessing and all sliding operations '
    'take O(n log n), with O(n) storage including compressed values and output. Sorting each window is the independent '
    'small-input oracle, not the reference algorithm. The complete source specifies 10^-5 absolute tolerance; '
    'this corrects the workbook summary\'s looser 10^-4 wording.',
    'O(n log n)','O(n)',difficulty=8,
    stress=[([UP,50000],[i+24999.5 for i in range(50001)]),
            ([DOWN,50001],[74999-i for i in range(50000)]),
            ([ALTERNATING,500],[ -0.5 ]*99501),
            ([ALTERNATING,1],ALTERNATING[:]),
            ([DOWN,100000],[49999.5])]),
}
BATCH[480]['comparator'] = 'float_list'
BATCH[480]['prerequisites'] = ['arrays','binary-search','sliding-window']
BATCH[480]['statement'] = ('For each length-k sliding window, return its median in left-to-right order. '
    'Sort conceptually: an odd window uses its middle value, and an even window uses the average of its two middle values. '
    'Answers within 0.00001 absolute error per position are accepted. The entry point is a function returning a list; helper classes are optional.')
