"""Fair digits, inequality counting, matrix paths, fixed bounds, and weighted median."""
from .import_batch_055 import entry


def fair_oracle(args):
    value = args[0]
    while True:
        digits = str(value)
        if sum(int(digit) % 2 for digit in digits) * 2 == len(digits):
            return value
        value += 1


def random_fair(rng):
    return [rng.randint(1, 20000)]


def inequality_oracle(args):
    nums1, nums2, diff = args
    return sum(
        nums1[left] - nums1[right] <= nums2[left] - nums2[right] + diff
        for left in range(len(nums1)) for right in range(left + 1, len(nums1))
    )


def random_inequality(rng):
    size = rng.randint(2, 20)
    return [[rng.randint(-20, 20) for _ in range(size)], [rng.randint(-20, 20) for _ in range(size)], rng.randint(-10, 10)]


def divisible_paths_oracle(args):
    grid, divisor = args
    rows, cols = len(grid), len(grid[0])
    stack = [(0, 0, grid[0][0])]
    answer = 0
    while stack:
        row, col, total = stack.pop()
        if row == rows - 1 and col == cols - 1:
            answer += total % divisor == 0
            continue
        if row + 1 < rows:
            stack.append((row + 1, col, total + grid[row + 1][col]))
        if col + 1 < cols:
            stack.append((row, col + 1, total + grid[row][col + 1]))
    return answer % 1_000_000_007


def random_divisible_paths(rng):
    rows, cols = rng.randint(1, 4), rng.randint(1, 4)
    return [[[rng.randint(0, 12) for _ in range(cols)] for _ in range(rows)], rng.randint(1, 7)]


def fixed_bounds_oracle(args):
    nums, minimum, maximum = args
    answer = 0
    for left in range(len(nums)):
        low = high = nums[left]
        for right in range(left, len(nums)):
            low = min(low, nums[right]); high = max(high, nums[right])
            answer += low == minimum and high == maximum
    return answer


def random_fixed_bounds(rng):
    minimum = rng.randint(1, 8); maximum = rng.randint(minimum, 10)
    return [[rng.randint(0, 11) for _ in range(rng.randint(2, 20))], minimum, maximum]


def equal_cost_oracle(args):
    nums, costs = args
    return min(sum(abs(value - target) * cost for value, cost in zip(nums, costs)) for target in range(min(nums), max(nums) + 1))


def random_equal_cost(rng):
    size = rng.randint(1, 12)
    return [[rng.randint(1, 20) for _ in range(size)], [rng.randint(1, 12) for _ in range(size)]]


FAIR = '''def closest_fair_integer(n):
    def fair(value):
        digits=str(value)
        return len(digits)%2==0 and sum(int(digit)%2 for digit in digits)*2==len(digits)
    length=len(str(n))
    if length%2:
        zeros=(length+1)//2
        return int('1'+'0'*zeros+'1'*(zeros-1))
    while not fair(n):n+=1
    return n
'''


INEQUALITY = '''def count_pairs_satisfying_inequality(nums1,nums2,diff):
    import bisect
    values=[left-right for left,right in zip(nums1,nums2)];coordinates=sorted(set(values));tree=[0]*(len(coordinates)+1)
    def add(index):
        index+=1
        while index<len(tree):tree[index]+=1;index+=index&-index
    def prefix(end):
        total=0
        while end:total+=tree[end];end-=end&-end
        return total
    answer=0
    for value in values:
        answer+=prefix(bisect.bisect_right(coordinates,value+diff))
        add(bisect.bisect_left(coordinates,value))
    return answer
'''


DIVISIBLE_PATHS = '''def count_divisible_matrix_paths(grid,k):
    mod=1000000007;rows=len(grid);cols=len(grid[0]);dp=[[[0]*k for _ in range(cols)] for _ in range(rows)]
    dp[0][0][grid[0][0]%k]=1
    for row in range(rows):
        for col in range(cols):
            if row==0 and col==0:continue
            value=grid[row][col]%k
            for remainder in range(k):
                previous=(remainder-value)%k
                if row:dp[row][col][remainder]+=dp[row-1][col][previous]
                if col:dp[row][col][remainder]+=dp[row][col-1][previous]
                dp[row][col][remainder]%=mod
    return dp[-1][-1][0]
'''


FIXED_BOUNDS = '''def count_fixed_bound_subarrays(nums,min_k,max_k):
    invalid=last_min=last_max=-1;answer=0
    for index,value in enumerate(nums):
        if value<min_k or value>max_k:invalid=index
        if value==min_k:last_min=index
        if value==max_k:last_max=index
        answer+=max(0,min(last_min,last_max)-invalid)
    return answer
'''


EQUAL_COST = '''def minimum_cost_to_equal_array(nums,cost):
    pairs=sorted(zip(nums,cost));half=(sum(cost)+1)//2;weight=0;target=pairs[0][0]
    for value,current in pairs:
        weight+=current
        if weight>=half:target=value;break
    return sum(abs(value-target)*current for value,current in pairs)
'''


UNWEIGHTED_MEDIAN = '''def minimum_cost_to_equal_array(nums,cost):
    target=sorted(nums)[len(nums)//2]
    return sum(abs(value-target)*current for value,current in zip(nums,cost))
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


BATCH = {
    2417: entry(
        'closest_fair_integer', [('n', 'int')], 'int', ['math', 'digits', 'enumeration'],
        ['n is a positive integer at most 10^9.', 'A fair integer contains equal counts of even and odd decimal digits; zero is an even digit.', 'Return the smallest fair integer greater than or equal to n.'],
        [([2], 'No one-digit number can be fair; ten has one odd and one even digit.'), ([403], 'No three-digit number is fair, and 1001 is the first fair four-digit number at least 403.')],
        [[value] for value in [1,9,10,11,12,20,21,99,100,999,1000,1001,1234,9999]],
        FAIR,
        [FAIR.replace('int(digit)%2', "(int(digit)%2 or digit=='0')"), FAIR.replace('while not fair(n):n+=1', 'while not fair(n+1):n+=1\n    n+=1')],
        ['Misclassifies zero as odd when counting digit parity.', 'Always searches strictly above n even when n itself is already fair.'],
        fair_oracle, random_fair,
        lesson('A fair number must have an even number of digits.', 'If n has odd length, construct the smallest fair number of the next length; otherwise scan until the digit counts balance.', 'Count digit parities, handling the odd-length jump directly, and stop at the first balanced candidate.', 'The scan tests candidates in increasing order, while the constructed next-length value is lexicographically smallest with half odd and half even digits, so the first result is minimal.'),
        'O(answer-n)', 'O(1)', 5,
    ),
    2426: entry(
        'count_pairs_satisfying_inequality', [('nums1', 'list[int]'), ('nums2', 'list[int]'), ('diff', 'int')], 'int',
        ['binary indexed trees', 'coordinate compression', 'arrays'],
        ['nums1 and nums2 have equal length from 2 through 100000.', 'Count index pairs i<j satisfying nums1[i]-nums1[j] <= nums2[i]-nums2[j]+diff.', 'Values and diff may be negative; return the total number of qualifying pairs.'],
        [([[3,2,5], [2,2,1], 1], 'All three index pairs satisfy the rearranged inequality (nums1[i]-nums2[i]) <= (nums1[j]-nums2[j])+1.'), ([[3,-1], [-2,2], -1], 'The only pair fails the inequality, so the count is zero.')],
        [[a,b,d] for a,b,d in [([0,0],[0,0],0),([1,2],[0,0],0),([2,1],[0,0],0),([1,1],[1,1],-1),([-1,1],[1,-1],2),([1,2,3],[3,2,1],0),([3,2,1],[1,2,3],0),([5,-2,4],[1,3,-1],-2),([0,0,0],[1,2,3],1),([10,-10,5,-5],[0,0,0,0],3),([1,4,2,8],[3,1,5,0],-1),([-3,-2,-1],[3,2,1],4),([7,7,7],[2,2,2],0),([2,9,1,6,3],[5,0,4,1,8],2)]],
        INEQUALITY,
        [INEQUALITY.replace('bisect.bisect_right(coordinates,value+diff)', 'bisect.bisect_left(coordinates,value+diff)'), INEQUALITY.replace('left-right for left,right', 'left+right for left,right')],
        ['Counts only strict inequalities and loses equality cases.', 'Combines the arrays by addition instead of the required difference.'],
        inequality_oracle, random_inequality,
        lesson('Rearrange the condition to value[i] <= value[j]+diff where value=nums1-nums2.', 'Scan j from left to right and query how many earlier transformed values are at most the current threshold.', 'Coordinate-compress transformed values, use a Fenwick prefix count, then insert the current value.', 'Only earlier indices have been inserted, and the upper-bound prefix contains exactly the values satisfying the rearranged inequality, so every valid pair is counted once.'),
        'O(n log n)', 'O(n)', 8,
    ),
    2435: entry(
        'count_divisible_matrix_paths', [('grid', 'list[list[int]]'), ('k', 'int')], 'int',
        ['dynamic programming', 'matrices', 'modular arithmetic'],
        ['grid is a nonempty rectangular matrix and rows*columns is at most 50000.', 'Move only right or down from the top-left to the bottom-right cell.', 'Return modulo 1,000,000,007 the number of paths whose inclusive cell sum is divisible by k.'],
        [([[[5,2,4],[3,0,5],[0,7,2]], 3], 'Exactly two right/down paths have sums divisible by three.'), ([[[0,0]], 5], 'The only path sums to zero, which is divisible by five.')],
        [[g,k] for g,k in [([[0]],1),([[1]],1),([[1]],2),([[1,2]],3),([[1],[2]],3),([[1,2],[3,4]],2),([[1,2],[3,4]],3),([[0,0],[0,0]],4),([[7,3,4,9],[2,3,6,2],[2,3,7,0]],1),([[2,2,2],[2,2,2]],2),([[1,0,1],[0,1,0],[1,0,1]],2),([[5,1],[2,3],[4,0]],4),([[9,8,7],[6,5,4]],5),([[3,1,4],[1,5,9],[2,6,5]],7)]],
        DIVISIBLE_PATHS,
        [DIVISIBLE_PATHS.replace('return dp[-1][-1][0]', 'return dp[-1][-1][1%k]'), DIVISIBLE_PATHS.replace('previous=(remainder-value)%k', 'previous=(remainder+value)%k')],
        ['Returns paths with remainder one instead of remainder zero.', 'Reverses the modular transition and therefore tracks the wrong sums.'],
        divisible_paths_oracle, random_divisible_paths,
        lesson('Path counts need the sum remainder, not the potentially enormous full sum.', 'For every cell, store one count per remainder and extend states from its top and left neighbors.', 'For desired remainder r, add predecessor remainder (r-cell_value) mod k from both directions.', 'Every right/down path reaches a cell from exactly one of those two predecessors; the remainder transition preserves its sum, so the destination remainder-zero count is exact.'),
        'O(rows*cols*k)', 'O(rows*cols*k)', 8,
    ),
    2444: entry(
        'count_fixed_bound_subarrays', [('nums', 'list[int]'), ('min_k', 'int'), ('max_k', 'int')], 'int',
        ['sliding windows', 'arrays', 'counting'],
        ['nums has at least two integers and min_k <= max_k.', 'Count contiguous subarrays whose minimum is exactly min_k and maximum is exactly max_k.', 'Values outside [min_k,max_k] invalidate every subarray crossing their position.'],
        [([[1,3,5,2,7,5], 1, 5], 'The valid subarrays are [1,3,5] and [1,3,5,2].'), ([[1,1,1,1], 1, 1], 'All ten nonempty contiguous subarrays have both fixed bounds equal to one.')],
        [[n,a,b] for n,a,b in [([1,2],1,2),([2,1],1,2),([1,3],1,2),([2,2],1,2),([1,1],1,1),([1,2,1],1,2),([1,2,3,1,2],1,2),([0,1,2],1,2),([1,2,3],1,3),([3,1,3,1],1,3),([2,1,2,2],1,2),([5,4,5,6,5],4,6),([1,5,1,5,7,1,5],1,5),([2,3,2,1,3,2],2,3)]],
        FIXED_BOUNDS,
        [FIXED_BOUNDS.replace('value<min_k or value>max_k', 'value<=min_k or value>=max_k'), FIXED_BOUNDS.replace('min(last_min,last_max)', 'max(last_min,last_max)')],
        ['Treats occurrences of the required bounds as invalid values.', 'Uses the later bound occurrence and counts starts missing one required bound.'],
        fixed_bounds_oracle, random_fixed_bounds,
        lesson('For each right endpoint, valid starts must follow the last invalid value and include both most recent bounds.', 'Track the last positions of min_k, max_k, and any out-of-range value.', 'Add max(0,min(last_min,last_max)-last_invalid) for every endpoint.', 'A start after the invalid index stays within range, while a start at or before both bound positions includes each required extreme; their intersection has exactly the computed size.'),
        'O(n)', 'O(1)', 8,
    ),
    2448: entry(
        'minimum_cost_to_equal_array', [('nums', 'list[int]'), ('cost', 'list[int]')], 'int',
        ['greedy', 'sorting', 'weighted medians'],
        ['nums and cost are equally sized nonempty arrays of positive integers.', 'Changing nums[i] by one in either direction costs cost[i].', 'Return the minimum total cost needed to make all values equal.'],
        [([[1,3,5,2], [2,3,1,14]], 'Choosing target two costs 2+3+3=8, which is minimal.'), ([[2,2,2,2,2], [4,2,8,1,3]], 'Every value is already equal, so the minimum cost is zero.')],
        [[n,c] for n,c in [([1],[5]),([1,2],[1,1]),([1,2],[10,1]),([1,3],[1,2]),([3,1],[1,3]),([1,2,3],[1,1,1]),([1,10,20],[100,1,1]),([5,5,9],[2,7,3]),([1,4,7,10],[1,2,3,4]),([10,1,10,1],[5,1,1,5]),([2,8,3],[4,1,9]),([100,1,50],[2,20,3]),([1,2,100],[3,3,5]),([7,4,9,2,6],[1,8,2,7,3])]],
        EQUAL_COST,
        [UNWEIGHTED_MEDIAN, EQUAL_COST.replace('abs(value-target)*current', 'abs(value-target)')],
        ['Uses an ordinary median instead of the cost-weighted median.', 'Counts changed units but ignores their per-index costs.'],
        equal_cost_oracle, random_equal_cost,
        lesson('The objective is a weighted sum of absolute distances.', 'Sort values and choose the first value whose cumulative weight reaches half the total weight.', 'Find the weighted median, then sum abs(value-target)*cost.', 'Moving the target across a value transfers that weight from the decreasing side to the increasing side; the slope first becomes nonnegative at a weighted median, which therefore minimizes the convex cost.'),
        'O(n log n)', 'O(n)', 8,
    ),
}
