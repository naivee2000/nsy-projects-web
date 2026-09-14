"""Diagonal primes, equal-value distances, pair thresholds, grid jumps, and subsets batch 166."""

from collections import deque

from .import_batch_055 import entry


def diagonal_oracle(args):
    grid = args[0];n = len(grid);answer = 0
    for row in range(n):
        for value in {grid[row][row], grid[row][n-row-1]}:
            if value > 1 and not any(value % divisor == 0 for divisor in range(2, value)):
                answer = max(answer, value)
    return answer


def random_diagonal(rng):
    n = rng.randint(1, 7)
    return [[[rng.randint(1, 100) for _ in range(n)] for _ in range(n)]]


def distances_oracle(args):
    nums = args[0]
    return [sum(abs(index-other) for other, candidate in enumerate(nums) if candidate == value)
            for index, value in enumerate(nums)]


def random_distances(rng):
    return [[rng.randint(-5, 5) for _ in range(rng.randint(1, 40))]]


def pairs_oracle(args):
    nums, target = args

    def visit(remaining, chosen):
        if chosen == target:
            return 0
        if len(remaining) < 2 * (target-chosen):
            return 10**9
        first = remaining[0]
        best = visit(remaining[1:], chosen)
        for index in range(1, len(remaining)):
            rest = remaining[1:index] + remaining[index+1:]
            best = min(best, max(abs(first-remaining[index]), visit(rest, chosen+1)))
        return best

    return visit(tuple(nums), 0)


def random_pairs(rng):
    n = rng.randint(2, 10)
    return [[rng.randint(-20, 20) for _ in range(n)], rng.randint(0, n//2)]


def cells_oracle(args):
    grid = args[0];rows=len(grid);columns=len(grid[0]);distance=[[-1]*columns for _ in range(rows)]
    distance[0][0]=1;queue=deque([(0,0)])
    while queue:
        row,column=queue.popleft();reach=grid[row][column]
        for following in range(column+1,min(columns,column+reach+1)):
            if distance[row][following]<0:
                distance[row][following]=distance[row][column]+1;queue.append((row,following))
        for following in range(row+1,min(rows,row+reach+1)):
            if distance[following][column]<0:
                distance[following][column]=distance[row][column]+1;queue.append((following,column))
    return distance[-1][-1]


def random_cells(rng):
    rows,columns=rng.randint(1,5),rng.randint(1,5)
    return [[[rng.randint(0, max(rows,columns)) for _ in range(columns)] for _ in range(rows)]]


def subsets_oracle(args):
    nums,k=args;answer=0
    for mask in range(1<<len(nums)):
        chosen=[nums[index] for index in range(len(nums)) if mask>>index&1]
        if all(abs(first-second)!=k for i,first in enumerate(chosen) for second in chosen[i+1:]):answer+=1
    return answer


def random_subsets(rng):
    size=rng.randint(1,15)
    return [rng.sample(range(-30,31),size),rng.randint(1,12)]


DIAGONAL = """\
def largest_diagonal_prime(nums):
    import math
    def prime(value):
        if value<2:return False
        for divisor in range(2,math.isqrt(value)+1):
            if value%divisor==0:return False
        return True
    answer=0;n=len(nums)
    for row in range(n):
        for value in (nums[row][row],nums[row][n-row-1]):
            if prime(value):answer=max(answer,value)
    return answer
"""

DISTANCES = """\
def equal_value_index_distances(nums):
    from collections import defaultdict
    positions=defaultdict(list)
    for index,value in enumerate(nums):positions[value].append(index)
    answer=[0]*len(nums)
    for indexes in positions.values():
        total=sum(indexes);left_sum=0
        for rank,index in enumerate(indexes):
            left=index*rank-left_sum
            right=(total-left_sum-index)-index*(len(indexes)-rank-1)
            answer[index]=left+right;left_sum+=index
    return answer
"""

PAIRS = """\
def minimum_maximum_pair_difference(nums,p):
    nums=sorted(nums)
    def possible(limit):
        count=index=0
        while index+1<len(nums):
            if nums[index+1]-nums[index]<=limit:count+=1;index+=2
            else:index+=1
        return count>=p
    low=0;high=nums[-1]-nums[0]
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return low
"""

CELLS = """\
def minimum_visited_jump_cells(grid):
    import heapq
    rows=len(grid);columns=len(grid[0]);distance=[[-1]*columns for _ in range(rows)]
    row_heaps=[[] for _ in range(rows)];column_heaps=[[] for _ in range(columns)]
    for row in range(rows):
        for column in range(columns):
            while row_heaps[row] and row_heaps[row][0][1]<column:heapq.heappop(row_heaps[row])
            while column_heaps[column] and column_heaps[column][0][1]<row:heapq.heappop(column_heaps[column])
            if row==0 and column==0:distance[row][column]=1
            elif row_heaps[row] or column_heaps[column]:
                distance[row][column]=1+min(row_heaps[row][0][0] if row_heaps[row] else 10**9,column_heaps[column][0][0] if column_heaps[column] else 10**9)
            if distance[row][column]>0:
                heapq.heappush(row_heaps[row],(distance[row][column],column+grid[row][column]))
                heapq.heappush(column_heaps[column],(distance[row][column],row+grid[row][column]))
    return distance[-1][-1]
"""

SUBSETS = """\
def count_k_free_subsets(nums,k):
    from collections import defaultdict
    groups=defaultdict(list)
    for value in sorted(nums):groups[value%k].append(value)
    answer=1
    for values in groups.values():
        skip=take=1
        for index in range(1,len(values)):
            if values[index]-values[index-1]==k:skip,take=skip+take,skip
            else:skip,take=skip+take,skip+take
        answer*=skip+take
    return answer
"""


BATCH = {
    2614: entry(
        "largest_diagonal_prime", [("nums","list[list[int]]")], "int", ["matrices","math","number theory"],
        ["nums is a nonempty square integer matrix.", "Inspect both the main and anti-diagonal entries.", "Return the largest prime found there, or zero when neither diagonal contains a prime."],
        [
            ([[[1,2,3],[5,6,7],[9,10,11]]], "The diagonal primes are three, seven, and eleven; eleven is largest."),
            ([[[1,4],[6,8]]], "No diagonal value is prime, so return zero."),
        ],
        [[g] for g in [
            [[2]],[[1]],[[4]],[[2,3],[5,7]],[[4,2],[3,8]],[[17,1,19],[4,23,6],[29,8,31]],
            [[1,1,1],[1,2,1],[1,1,1]],[[49,1],[1,47]],[[97,4,6],[8,9,10],[12,14,89]],
            [[0,2,0],[3,0,5],[0,7,0]],[[25,7],[11,13]],[[101,1,1],[1,103,1],[1,1,107]],
            [[15,17,19,21],[23,25,27,29],[31,33,35,37],[39,41,43,45]],[[1,2,4],[6,8,10],[12,14,16]],
        ]],
        DIAGONAL,
        [DIAGONAL.replace("value<2", "value<1"),DIAGONAL.replace("nums[row][n-row-1]", "nums[row][row]")],
        ["Treats one as prime.", "Checks the main diagonal twice and ignores the anti-diagonal."],
        diagonal_oracle,random_diagonal,
        ["Only two cells per row can lie on the required diagonals.", "Test primality by trial divisors only through the integer square root.", "Update the maximum for both diagonal positions in every row.", "A composite has a factor no larger than its square root, so the test is complete and every eligible matrix cell is inspected."],
        "O(n*sqrt(M))","O(1)",3,
    ),
    2615: entry(
        "equal_value_index_distances", [("nums","list[int]")], "list[int]", ["arrays","hash maps","prefix sums"],
        ["For each index i, consider every other index j with nums[j] equal to nums[i].", "Set answer[i] to the sum of |i-j| across those indices.", "Return the full answer array; unique values receive zero."],
        [
            ([[1,3,1,1,2]], "The three ones occur at indices zero, two, and three, producing distances five, three, and four."),
            ([[0,5,3]], "Every value is unique, so every distance sum is zero."),
        ],
        [[a] for a in [[1],[1,1],[1,2],[2,1,2],[1,1,1],[1,2,1,2],[3,3,1,3,1],[-1,0,-1,0,-1],[5,4,3,2,1],[7,7,8,8,7,8],[0,0,0,1,0],[2,3,2,4,2,3],[9,1,9,1,9,1,9],[4,5,4,6,5,4,6]]],
        DISTANCES,
        [DISTANCES.replace("index*rank-left_sum", "index*(rank+1)-left_sum"),DISTANCES.replace("positions[value].append(index)", "positions[index].append(index)")],
        ["Counts the current index once on the left side.", "Groups positions by index instead of by equal value."],
        distances_oracle,random_distances,
        ["Group indices by their array value.", "Within one sorted index group, maintain the sum of processed indices and the total group sum.", "Compute left cost as index*left_count-left_sum and right cost symmetrically.", "Every equal-value index lies on exactly one side or is the current zero-distance index, so the two formulas sum precisely all required distances."],
        "O(n)","O(n)",5,
    ),
    2616: entry(
        "minimum_maximum_pair_difference", [("nums","list[int]"),("p","int")], "int", ["arrays","binary search","greedy","sorting"],
        ["Choose exactly p disjoint index pairs; p may be zero.", "A pair's difference is the absolute difference of its values.", "Return the smallest achievable maximum difference across the chosen pairs."],
        [
            ([[10,1,2,7,1,3],2], "Pair the two ones and pair two with three, so the maximum difference is one."),
            ([[4,2,1,2],1], "The two equal values can be paired for maximum difference zero."),
        ],
        [[a,p] for a,p in [([1,2],0),([1,2],1),([1,1],1),([1,5,9],1),([1,2,3,4],2),([4,3,2,1],2),([1,10,2,9],2),([5,5,5,5],2),([0,100,101,200],1),([-5,-1,0,8],2),([3,8,2,7,1,6],3),([1,2,100,101,200],2),([9,1,4,7,3,8],2),([0,0,10,10,20,20],3)]],
        PAIRS,
        [PAIRS.replace("count>=p", "count>p"),PAIRS.replace("index+=2", "index+=1")],
        ["Requires one more feasible pair than requested.", "Reuses an index by advancing only one position after forming a pair."],
        pairs_oracle,random_pairs,
        ["Sort values and binary-search a candidate maximum difference.", "For a fixed limit, scan left to right and greedily pair adjacent values whenever possible.", "After forming a pair, skip both elements; count whether at least p pairs are formed.", "The closest available partner for the smallest remaining value is adjacent, so taking it cannot reduce future feasibility; the predicate is monotone in the limit."],
        "O(n log R+n log n)","O(n)",6,
    ),
    2617: entry(
        "minimum_visited_jump_cells", [("grid","list[list[int]]")], "int", ["matrices","breadth-first search","heaps","dynamic programming"],
        ["Start at the top-left cell and count it as visited.", "From (r,c), move right or down by between one and grid[r][c] cells.", "Return the minimum cells visited to reach bottom-right, or -1 if unreachable."],
        [
            ([[[3,4,2,1],[4,2,3,1],[2,1,0,0],[2,4,0,0]]], "A shortest valid route reaches the destination after visiting four cells."),
            ([[[2,1,0],[1,0,0]]], "The destination cannot be reached because all routes stop before it."),
        ],
        [[g] for g in [
            [[0]],[[1,0]],[[0,0]],[[1],[0]],[[0],[0]],[[1,1],[1,0]],[[2,0],[0,0]],
            [[1,0],[0,0]],[[3,0,0,0]],[[1,1,1,0]],[[1],[1],[1],[0]],[[2,1,0],[1,1,0],[0,1,0]],
            [[1,2,0],[2,0,1],[0,1,0]],[[4,0,0],[0,0,0],[0,0,0]],
        ]],
        CELLS,
        [CELLS.replace("column+grid[row][column]", "column+grid[row][column]-1"),CELLS.replace("distance[row][column]=1", "distance[row][column]=0",1)],
        ["Expires row jumps one column too early.", "Counts moves rather than visited cells by assigning the start distance zero."],
        cells_oracle,random_cells,
        ["Process cells in row-major order; every legal predecessor is above or left and is already processed.", "Maintain a min-heap per row and column keyed by predecessor distance, with its farthest reachable coordinate.", "Discard expired heap entries, take the smaller live predecessor distance, then add one and publish this cell to both heaps.", "Heaps expose the best still-reaching predecessor; row-major direction makes the dynamic program acyclic and each heap entry is inserted and removed once."],
        "O(rows*columns*log(rows*columns))","O(rows*columns)",8,
    ),
    2638: entry(
        "count_k_free_subsets", [("nums","list[int]"),("k","int")], "int", ["arrays","dynamic programming","math","sorting"],
        ["nums contains distinct integers and k is positive.", "A subset is valid when no selected pair has absolute difference exactly k.", "Return the number of valid subsets, including the empty subset."],
        [
            ([[5,4,6],1], "The valid subsets are empty, each singleton, and {4,6}, for five total."),
            ([[2,3,5,8],5], "Only the pair {3,8} conflicts; twelve of the sixteen subsets remain valid."),
        ],
        [[a,k] for a,k in [([1],1),([1,2],1),([1,3],1),([1,3],2),([1,2,3],1),([1,2,3],2),([1,4,7],3),([1,4,8],3),([-3,0,3],3),([2,5,8,11],3),([1,2,4,5],3),([10,20,30],7),([0,1,2,3,4],2),([-5,-1,3,7],4)]],
        SUBSETS,
        [SUBSETS.replace("skip,take=skip+take,skip", "skip,take=skip+take,take"),SUBSETS.replace("answer*=skip+take", "answer*=skip")],
        ["When consecutive group values conflict, permits taking both through the prior take state.", "Counts only group solutions that omit the final value."],
        subsets_oracle,random_subsets,
        ["Only values with the same remainder modulo k can differ by exactly k.", "Sort each remainder group and use two states: subsets skipping or taking its current value.", "If adjacent values differ by k, taking current requires skipping previous; otherwise both previous states may extend either way.", "Remainder groups are independent, so multiplying their valid-subset counts forms every global subset exactly once."],
        "O(n log n)","O(n)",6,
    ),
}
