"""Denomination order, AND partitions, pothole runs, letter order, and grid columns."""
from itertools import combinations, product
from math import gcd

from .import_batch_055 import entry


def denomination_oracle(args):
    coins, rank = args; found = 0; amount = 0
    while found < rank:
        amount += 1
        found += any(amount % coin == 0 for coin in coins)
    return amount


def random_denomination(rng):
    size = rng.randint(1, 6)
    return [rng.sample(range(2, 18), size), rng.randint(1, 60)]


def division_oracle(args):
    nums, targets = args; best = 10**30
    for cuts in combinations(range(1, len(nums)), len(targets) - 1):
        starts = (0,) + cuts; ends = cuts + (len(nums),); valid = True; total = 0
        for start, end, target in zip(starts, ends, targets):
            value = nums[start]
            for index in range(start + 1, end):
                value &= nums[index]
            if value != target:
                valid = False; break
            total += nums[end - 1]
        if valid:
            best = min(best, total)
    return -1 if best == 10**30 else best


def random_division(rng):
    size = rng.randint(1, 9); nums = [rng.randint(0, 31) for _ in range(size)]
    return [nums, [rng.randint(0, 31) for _ in range(rng.randint(1, min(4, size)))]]


def potholes_oracle(args):
    road, budget = args; runs = [len(run) for run in road.replace('.', ' ').split()]; best = 0

    def choose(index, remaining, fixed):
        nonlocal best
        if index == len(runs):
            best = max(best, fixed); return
        choose(index + 1, remaining, fixed)
        for holes in range(1, runs[index] + 1):
            if holes + 1 <= remaining:
                choose(index + 1, remaining - holes - 1, fixed + holes)
    choose(0, budget, 0)
    return best


def random_potholes(rng):
    return [''.join(rng.choice('x.') for _ in range(rng.randint(1, 14))), rng.randint(0, 18)]


def special_oracle(args):
    word = args[0]; answer = 0
    for offset in range(26):
        lower, upper = chr(97 + offset), chr(65 + offset)
        lowers = [index for index, char in enumerate(word) if char == lower]
        uppers = [index for index, char in enumerate(word) if char == upper]
        answer += bool(lowers and uppers and max(lowers) < min(uppers))
    return answer


def random_special(rng):
    alphabet = 'abcABCxyzXYZ'
    return [''.join(rng.choice(alphabet) for _ in range(rng.randint(1, 20)))]


def columns_oracle(args):
    grid = args[0]; rows, columns = len(grid), len(grid[0]); best = rows * columns
    for assigned in product(range(10), repeat=columns):
        if any(assigned[index] == assigned[index - 1] for index in range(1, columns)):
            continue
        cost = sum(grid[row][column] != assigned[column]
                   for row in range(rows) for column in range(columns))
        best = min(best, cost)
    return best


def random_columns(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 3)
    return [[[rng.randrange(10) for _ in range(columns)] for _ in range(rows)]]


DENOMINATION = '''def kth_single_denomination_amount(coins,k):
    from math import gcd
    def lcm(left,right):return left//gcd(left,right)*right
    def enough(limit):
        count=0
        for mask in range(1,1<<len(coins)):
            multiple=1
            for index,coin in enumerate(coins):
                if mask>>index&1:
                    multiple=lcm(multiple,coin)
                    if multiple>limit:break
            contribution=limit//multiple
            count+=contribution if mask.bit_count()%2 else -contribution
        return count>=k
    low,high=1,min(coins)*k
    while low<high:
        middle=(low+high)//2
        if enough(middle):high=middle
        else:low=middle+1
    return low
'''


DIVISION = '''def minimum_and_partition_sum(nums,and_values):
    from functools import lru_cache
    infinity=10**30;size=len(nums);groups=len(and_values)
    @lru_cache(None)
    def search(index,group,current):
        if size-index<groups-group:return infinity
        if group==groups:return 0 if index==size else infinity
        current&=nums[index]
        if current<and_values[group]:return infinity
        answer=search(index+1,group,current)
        if current==and_values[group]:answer=min(answer,search(index+1,group+1,-1)+nums[index])
        return answer
    answer=search(0,0,-1)
    return -1 if answer>=infinity else answer
'''


POTHOLES = '''def maximum_repaired_potholes(road,budget):
    runs=[];length=0
    for char in road+'.':
        if char=='x':length+=1
        elif length:runs.append(length);length=0
    runs.sort(reverse=True);answer=0
    for length in runs:
        repaired=min(length,max(0,budget-1))
        if repaired:answer+=repaired;budget-=repaired+1
        if budget<=1:break
    return answer
'''


SPECIAL = '''def count_ordered_case_letters(word):
    from string import ascii_lowercase
    answer=0
    for lower in ascii_lowercase:
        upper=lower.upper()
        if lower in word and upper in word and word.rfind(lower)<word.find(upper):answer+=1
    return answer
'''


COLUMNS = '''def minimum_grid_condition_changes(grid):
    rows=len(grid);columns=len(grid[0]);previous=[0]*10
    for column in range(columns):
        counts=[0]*10
        for row in range(rows):counts[grid[row][column]]+=1
        current=[10**30]*10
        for digit in range(10):
            current[digit]=rows-counts[digit]+min(previous[other] for other in range(10) if other!=digit)
        previous=current
    return min(previous)
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3116: entry('kth_single_denomination_amount',[('coins','list[int]'),('k','int')],'int',['binary search','inclusion-exclusion','number theory'],['coins contains distinct positive denominations and k is positive.','An amount qualifies when it is a positive multiple of at least one denomination; different denominations are never mixed in one construction.','Sort distinct qualifying amounts and return the k-th smallest.'],[([[3,6,9],3],'The distinct qualifying amounts begin 3, 6, 9, so the third is nine.'),([[2,3],5],'The ordered union is 2,3,4,6,8, so the fifth amount is eight.')],[[c,k] for c,k in [([2],1),([2],10),([2,3],1),([2,3],5),([3,6,9],3),([4,6],7),([5,7],10),([2,4,8],8),([6,10,15],12),([3,5,7],20),([11,13],15),([2,3,5,7],25),([4,9,25],30),([8,12,18],40)]],DENOMINATION,[DENOMINATION.replace('count+=contribution if mask.bit_count()%2 else -contribution','count+=contribution'),DENOMINATION.replace('min(coins)*k','min(coins)*k-1')],['Adds all multiple counts without inclusion-exclusion, double-counting common multiples.','Uses an exclusive upper boundary and can omit the exact k-th multiple of the smallest denomination.'],denomination_oracle,random_denomination,lesson('The count of amounts at most x divisible by any coin is a union size computed by inclusion-exclusion over subset LCMs.','Binary-search the smallest x whose union count reaches k.','For each nonempty coin subset add or subtract floor(x/lcm); use that monotone count in lower-bound search.','Inclusion-exclusion counts every qualifying integer once, and the first x with count≥k is exactly the k-th ordered distinct amount.'),'O(2^coins*coins*log answer)','O(1)',8),
3117: entry('minimum_and_partition_sum',[('nums','list[int]'),('and_values','list[int]')],'int',['dynamic programming','bit manipulation','partitions'],['nums and and_values contain nonnegative integers, and the target list is nonempty.','Partition all of nums into exactly len(and_values) nonempty contiguous groups whose bitwise ANDs match the targets in order.','The cost is the sum of each group’s final array element; return the minimum cost or -1 when impossible.'],[([[1,4,3,3,2],[0,3,3,2]],'The only feasible four groups end with values four, three, three, and two, whose sum is twelve.'),([[2,3,5,7,7],[2,1,7]],'Groups [2,3], [5], and [7,7] have ANDs two, five, and seven, so this target is impossible and returns -1.')],[[n,a] for n,a in [([1],[1]),([1],[0]),([1,2],[0]),([1,2],[1,2]),([7,7],[7]),([1,4,3,3,2],[0,3,3,2]),([2,3,5,7,7],[2,1,7]),([6,3,7],[2,7]),([15,7,3],[7,3]),([0,0,0],[0,0]),([8,4,2,1],[0]),([5,5,5],[5,5,5]),([7,6,5,4],[6,4]),([3,2,1,0,7],[2,0,7])]],DIVISION,[DIVISION.replace('+nums[index]','+nums[index-1]'),DIVISION.replace('if current==and_values[group]','if current>=and_values[group]')],['Charges the element before a group endpoint rather than the endpoint itself.','Closes a group while its AND is still greater than the required target.'],division_oracle,random_division,lesson('While extending a group its AND only loses bits; a group may close exactly when it equals the current target.','Memoize scan index, target group, and running AND; either extend or close and pay the current final value.','Prune when elements left are fewer than groups or running AND is below target; after all groups require all elements consumed.','The recursion enumerates every ordered partition boundary once, and its accumulated endpoint costs match the objective exactly.'),'O(n*m*distinct AND states)','O(n*m*distinct AND states)',8),
3119: entry('maximum_repaired_potholes',[('road','str'),('budget','int')],'int',['greedy','strings','sorting'],['road contains x for potholes and dot for intact positions; budget is nonnegative.','Repairing any positive number h of consecutive potholes within one run costs h+1.','Return the greatest number of potholes repairable without exceeding budget; partial run repairs are allowed.'],[(['..',5],'There are no potholes, so the answer is zero regardless of budget.'),(['xx.xxx',5],'Repairing the three-hole run costs four, leaving insufficient budget for another repair, so three holes is optimal.')],[[r,b] for r,b in [('.',0),('x',0),('x',1),('x',2),('..',5),('xxx',3),('xxx',4),('xx.xxx',5),('xx.xxx',6),('x.x.x',4),('xxxx.xx',7),('...xxx...',2),('xxxxx',4),('xx..xxxx..x',8)]],POTHOLES,[POTHOLES.replace('budget-1','budget'),POTHOLES.replace('runs.sort(reverse=True)','runs.sort()')],['Forgets the one-unit setup cost for each repaired run.','Repairs shorter runs first, wasting setup costs that could cover more holes in a long run.'],potholes_oracle,random_potholes,lesson('Every used run pays one setup unit, so spending on the longest available run yields the most holes per setup.','Sort run lengths descending and repair as much as the remaining budget permits in each run.','For each length, take min(length,budget-1); if positive add it and subtract taken+1.','Exchanging a repair from a shorter run to an available longer run never reduces holes and cannot increase setup cost, proving the greedy order.'),'O(n log n)','O(n)',5),
3121: entry('count_ordered_case_letters',[('word','str')],'int',['strings','hash maps','indices'],['word contains English letters.','A letter is special only if both cases appear and every lowercase occurrence precedes every uppercase occurrence.','Return the number of distinct special letters.'],[(['aaAbcBC'],'For a, b, and c, the last lowercase occurs before the first uppercase, so all three are special.'),(['AbBCab'],'Lowercase a occurs after uppercase A and lowercase b occurs after uppercase B, so neither is special.')],[[w] for w in ['a','aA','Aa','aaAA','aAa','aaAbcBC','AbBCab','abcABC','ABCabc','zZyY','zzZZz','aAbBcC','leetcode','xYzXYZ']],SPECIAL,[SPECIAL.replace('word.rfind(lower)<word.find(upper)','word.find(lower)<word.find(upper)'),SPECIAL.replace('lower in word and upper in word and ','')],['Checks only the first lowercase occurrence and ignores a later lowercase after uppercase.','Compares missing-index values and can count letters that do not appear in both cases.'],special_oracle,random_special,lesson('“All lowercase before all uppercase” is equivalent to last(lowercase)<first(uppercase).','For each alphabet letter, require both cases and compare those two boundary indices.','Count lower where lower and upper occur and rfind(lower)<find(upper).','If the last lowercase is earlier than the first uppercase, every pair has the required order; otherwise that boundary pair is a counterexample.'),'O(26*n)','O(1)',5),
3122: entry('minimum_grid_condition_changes',[('grid','list[list[int]]')],'int',['dynamic programming','matrices','counting'],['grid is a nonempty rectangular matrix whose values are digits zero through nine.','Every column must become constant from top to bottom, and horizontally adjacent columns must use different digits.','One operation changes one cell; return the minimum operations.'],[([[[1,0,2],[1,0,2]]],'Columns are already constant and neighboring digits differ, so zero operations are needed.'),([[[1,1],[0,0],[1,1]]],'Choosing column digits one and zero changes one cell in each column, for two operations.')],[[g] for g in [[[0]],[[9]],[[1,0,2],[1,0,2]],[[1,1],[0,0],[1,1]],[[0,0]],[[0],[1]],[[1,2],[2,1]],[[3,3,3],[3,3,3]],[[0,1,0],[0,1,0],[0,1,0]],[[9,8,7],[6,5,4],[3,2,1]],[[1,2,3,4]],[[1],[2],[3],[4]],[[5,5,6],[5,6,6]],[[0,9,0,9],[9,0,9,0]]]],COLUMNS,[COLUMNS.replace('if other!=digit','if other==digit'),COLUMNS.replace('rows-counts[digit]','counts[digit]')],['Requires adjacent columns to use the same digit rather than different digits.','Charges cells already equal to the chosen digit instead of cells that must change.'],columns_oracle,random_columns,lesson('Vertical equality means each column chooses one digit; horizontal inequality couples only adjacent column choices.','Count digit frequencies per column and run DP over the ten possible previous digits.','dp[column][digit]=rows-count[column][digit]+min(dp[column-1][other]) for other≠digit.','The local change cost is exact for a constant column, and the transition enforces precisely the only cross-column condition.'),'O(rows*columns+100*columns)','O(10)',5),
}
