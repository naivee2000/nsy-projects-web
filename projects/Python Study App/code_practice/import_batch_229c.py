"""Distinct triplets, long/short trading, GCD scoring, digit trees, and sign flips."""
from functools import lru_cache
from itertools import combinations
from math import gcd

from .import_batch_055 import entry


def triplet_oracle(args):
    x, y = args; best = -1
    for first, second, third in combinations(range(len(x)), 3):
        if len({x[first], x[second], x[third]}) == 3: best = max(best, y[first] + y[second] + y[third])
    return best


def random_triplet(rng):
    n = rng.randint(3, 12); return [[rng.randint(1, 6) for _ in range(n)], [rng.randint(1, 30) for _ in range(n)]]


def stock_oracle(args):
    prices, k = args
    @lru_cache(None)
    def solve(day, remaining):
        if remaining == 0 or day >= len(prices) - 1: return 0
        best = solve(day + 1, remaining)
        for close in range(day + 1, len(prices)):
            best = max(best, abs(prices[close] - prices[day]) + solve(close + 1, remaining - 1))
        return best
    return solve(0, k)


def random_stock(rng):
    n = rng.randint(2, 10); return [[rng.randint(1, 30) for _ in range(n)], rng.randint(1, n // 2)]


def gcd_oracle(args):
    nums, k = args; best = 0; n = len(nums)
    for doubled in range(1 << n):
        if doubled.bit_count() > k: continue
        values = [value * (2 if doubled >> index & 1 else 1) for index, value in enumerate(nums)]
        for left in range(n):
            common = 0
            for right in range(left, n): common = gcd(common, values[right]); best = max(best, common * (right - left + 1))
    return best


def random_gcd(rng):
    nums = [rng.randint(1, 30) for _ in range(rng.randint(1, 8))]; return [nums, rng.randint(1, len(nums))]


def _digit_mask(value):
    mask = 0
    for char in str(value):
        bit = 1 << int(char)
        if mask & bit: return -1
        mask |= bit
    return mask


def subtree_oracle(args):
    vals, par = args; n = len(vals); children = [[] for _ in range(n)]
    for node in range(1, n): children[par[node]].append(node)
    answer = 0
    for root in range(n):
        nodes = []; stack = [root]
        while stack:
            node = stack.pop(); nodes.append(node); stack.extend(children[node])
        best = 0
        for chosen in range(1 << len(nodes)):
            used = total = 0; valid = True
            for offset, node in enumerate(nodes):
                if chosen >> offset & 1:
                    mask = _digit_mask(vals[node])
                    if mask < 0 or used & mask: valid = False; break
                    used |= mask; total += vals[node]
            if valid: best = max(best, total)
        answer += best
    return answer % 1_000_000_007


def random_subtree(rng):
    n = rng.randint(1, 9); return [[rng.randint(1, 999) for _ in range(n)], [-1] + [rng.randrange(node) for node in range(1, n)]]


def equal_oracle(args):
    nums, k = args; start = tuple(nums); queue = [(start, 0)]; seen = {start}
    for state, moves in queue:
        if len(set(state)) == 1: return True
        if moves == k: continue
        for index in range(len(state) - 1):
            following = list(state); following[index] *= -1; following[index + 1] *= -1; following = tuple(following)
            if following not in seen: seen.add(following); queue.append((following, moves + 1))
    return False


def random_equal(rng):
    nums = [rng.choice((-1, 1)) for _ in range(rng.randint(1, 10))]; return [nums, rng.randint(1, len(nums))]


TRIPLET = '''def maximum_distinct_x_triplet_sum(x,y):
    best={}
    for key,value in zip(x,y):best[key]=max(best.get(key,0),value)
    if len(best)<3:return -1
    return sum(sorted(best.values(),reverse=True)[:3])
'''


STOCK = '''def maximum_long_short_stock_profit(prices,k):
    negative=-10**30;cash=[0]*(k+1);long=[negative]*(k+1);short=[negative]*(k+1)
    for price in prices:
        previous_cash=cash[:];previous_long=long[:];previous_short=short[:]
        for transactions in range(1,k+1):
            cash[transactions]=max(previous_cash[transactions],previous_long[transactions]+price,previous_short[transactions]-price)
            long[transactions]=max(previous_long[transactions],previous_cash[transactions-1]-price)
            short[transactions]=max(previous_short[transactions],previous_cash[transactions-1]+price)
    return cash[k]
'''


GCD_SCORE = '''def maximum_subarray_gcd_score(nums,k):
    from math import gcd
    powers=[]
    for value in nums:
        count=0
        while value%2==0:count+=1;value//=2
        powers.append(count)
    answer=0
    for left in range(len(nums)):
        common=0;minimum=10**30;minimum_count=0
        for right in range(left,len(nums)):
            common=gcd(common,nums[right])
            if powers[right]<minimum:minimum=powers[right];minimum_count=1
            elif powers[right]==minimum:minimum_count+=1
            score=common*(2 if minimum_count<=k else 1)*(right-left+1)
            answer=max(answer,score)
    return answer
'''


SUBTREE = '''def maximum_good_subtree_score(vals,par):
    modulo=1000000007;n=len(vals);children=[[] for _ in range(n)]
    for node in range(1,n):children[par[node]].append(node)
    order=[0]
    for node in order:order.extend(children[node])
    tables=[None]*n;answer=0
    for node in reversed(order):
        mask=0;valid=True
        for char in str(vals[node]):
            bit=1<<int(char)
            if mask&bit:valid=False;break
            mask|=bit
        current=[-1]*1024;current[0]=0
        if valid:current[mask]=vals[node]
        for child in children[node]:
            other=tables[child];following=current[:]
            for first in range(1024):
                if current[first]<0:continue
                available=1023^first;second=available
                while True:
                    if other[second]>=0:following[first|second]=max(following[first|second],current[first]+other[second])
                    if second==0:break
                    second=(second-1)&available
            current=following
        tables[node]=current;answer=(answer+max(current))%modulo
    return answer
'''


EQUAL = '''def can_transform_to_equal(nums,k):
    def operations(target):
        incoming=1;used=0
        for value in nums[:-1]:
            if value*incoming!=target:incoming=-1;used+=1
            else:incoming=1
        return used if nums[-1]*incoming==target else 10**30
    return min(operations(1),operations(-1))<=k
'''


def lesson(concept, strategy, pseudocode, editorial): return [concept, strategy, pseudocode, editorial]


TRIPLET_CASES=[[x,y] for x,y in [([1,1,1],[1,2,3]),([1,2,1,2],[4,5,6,7]),([1,2,3],[1,2,3]),([1,2,1,3,2],[5,3,4,6,2]),([1,2,3,4],[10,1,2,3]),([1,1,2,3],[9,8,7,6]),([5,4,3,2,1],[1,2,3,4,5]),([1,2,3,1,2,3],[1,1,1,10,20,30]),([7,8,9,10],[100,1,1,1]),([1,2,3,4,5],[5,4,3,2,1]),([2,2,3,4,4],[8,9,10,11,12]),([1,3,5,7],[2,4,6,8]),([10,20,30,10],[7,8,9,100]),([1,2,3,4,1],[6,5,4,3,20])]]
STOCK_CASES=[[prices,k] for prices,k in [([1,2],1),([2,1],1),([1,1],1),([1,7,9,8,2],2),([12,16,19,19,8,1,19,13,9],3),([1,5,1],1),([5,1,5],1),([1,5,1,5],2),([5,1,5,1],2),([3,2,6,5,0,3],2),([10,9,8,7,6,5],3),([1,2,3,4,5,6],3),([4,1,7,2,9,3],2),([8,2,6,1,7,3,9,4],3)]]
GCD_CASES=[[nums,k] for nums,k in [([1],1),([2],1),([2,4],1),([3,5,7],2),([5,5,5],1),([2,2,2],1),([4,8,16],2),([6,10,14],1),([3,6,9],2),([1,2,4,8],1),([12,18,24],2),([7,14,21,28],2),([8,3,12,6],3),([16,24,40,56],1)]]
SUBTREE_CASES=[[vals,par] for vals,par in [([1],[-1]),([22],[-1]),([2,3],[-1,0]),([1,5,2],[-1,0,0]),([34,1,2],[-1,0,1]),([3,22,5],[-1,0,1]),([12,3,45],[-1,0,0]),([10,2,3],[-1,0,1]),([98,7,6,5],[-1,0,0,1]),([11,2,3],[-1,0,0]),([123,45,67],[-1,0,1]),([9,80,71,62],[-1,0,0,2]),([5,44,3,2,1],[-1,0,0,1,1]),([102,3,45,67],[-1,0,1,1])]]
EQUAL_CASES=[[nums,k] for nums,k in [([1],1),([-1],1),([1,-1],1),([1,1],1),([1,-1,1],1),([1,-1,1,-1,1],3),([-1,-1,-1,1,1,1],5),([1,-1,-1,1],1),([-1,1,1,-1],2),([1,1,-1,-1],2),([1,-1,-1,-1,1],4),([-1,1,-1,1],3),([1,1,1,-1],3),([-1,-1,1,-1,-1],2)]]


BATCH={
3572:entry('maximum_distinct_x_triplet_sum',[('x','list[int]'),('y','list[int]')],'int',['arrays','hash maps','greedy'],['x and y have equal length between 3 and 100,000.','Choose three indices whose x values are pairwise distinct.','Maximize the corresponding y sum, or return -1 if fewer than three x values exist.'],[([[1,2,1,3,2],[5,3,4,6,2]],'The best y value for x values one, two, and three gives 5+3+6=14.'),([[1,2,1,2],[4,5,6,7]],'Only two distinct x values exist, so no valid triplet exists.')],TRIPLET_CASES,TRIPLET,[TRIPLET.replace('max(best.get(key,0),value)','value'),TRIPLET.replace('[:3]','[:2]')],['Overwrites a better earlier y value for the same x group.','Chooses only two distinct x groups instead of three.'],triplet_oracle,random_triplet,lesson('Only the largest y paired with each distinct x can appear in an optimal triplet.','Aggregate best y per x, then select the three largest group maxima.','Update best[x]=max(best[x],y); if fewer than three keys return -1; otherwise sum the top three.','Replacing any selected index by a larger y from the same x preserves distinctness and improves or maintains the sum.'),'O(n log n)','O(n)',5),
3573:entry('maximum_long_short_stock_profit',[('prices','list[int]'),('k','int')],'int',['arrays','dynamic programming','state machines'],['prices has 2 to 1,000 days and 1 <= k <= len(prices)//2.','A transaction is either buy-then-sell or short-sell-then-buy-back on later days.','Transactions cannot overlap or close and reopen on the same day.'],[([[1,7,9,8,2],2],'Buy at one and sell at nine for eight, then short at eight and cover at two for six, totaling 14.'),([[12,16,19,19,8,1,19,13,9],3],'A long profit seven, short profit eleven, and long profit eighteen total 36.')],STOCK_CASES,STOCK,[STOCK.replace('previous_short[transactions]-price','previous_short[transactions]+price'),STOCK.replace('previous_cash[transactions-1]+price','previous_cash[transactions-1]-price')],['Adds the cover price when closing a short instead of subtracting it.','Opens short positions by subtracting the sale proceeds instead of adding them.'],stock_oracle,random_stock,lesson('For each transaction allowance, the end-of-day state is closed, holding a long position, or holding a short position.','Update every state from the previous day only, preventing a close and a new open on the same day.','Closed may stay or close long/short; open states may stay or open from closed with one fewer allowed transaction.','The three states cover every legal position, and previous-day transitions enforce ordering and non-overlap while maximizing profit for each prefix.'),'O(nk)','O(k)',5),
3574:entry('maximum_subarray_gcd_score',[('nums','list[int]'),('k','int')],'int',['arrays','greatest common divisor','enumeration'],['nums has up to 1,500 positive integers; each element may be doubled at most once.','Use at most k doublings, where 1 <= k <= len(nums).','A subarray score is its length times its GCD after selected doublings.'],[([[2,4],1],'Doubling two to four makes the length-two subarray GCD four, for score eight.'),([[3,5,7],2],'Doubling the singleton seven produces score fourteen, which is optimal.')],GCD_CASES,GCD_SCORE,[GCD_SCORE.replace('minimum_count<=k','minimum_count<k'),GCD_SCORE.replace('(2 if minimum_count<=k else 1)','(2 if minimum<=k else 1)')],['Requires strictly more operations than necessary when the minimum count equals k.','Compares the minimum power of two with k instead of how many elements attain that minimum.'],gcd_oracle,random_gcd,lesson('Doubling a subarray’s GCD is possible exactly when every element with the minimum power-of-two exponent is doubled.','Enumerate each subarray while maintaining its GCD, minimum two-adic exponent, and the count attaining that minimum.','Extend rightward; update GCD and minimum-count; multiply GCD by two only when that count is at most k.','Odd prime factors cannot be improved by doubling, and the shared power of two rises exactly when all minimum-exponent elements receive the operation.'),'O(n^2 log V)','O(n)',8),
3575:entry('maximum_good_subtree_score',[('vals','list[int]'),('par','list[int]')],'int',['trees','dynamic programming','bitmasking'],['The rooted tree has up to 500 nodes and par[0] is -1.','Across selected node values, every decimal digit zero through nine may appear at most once.','For each subtree find its maximum good-subset sum, then return the sum of those maxima modulo 1,000,000,007.'],[([[2,3],[-1,0]],'The root subtree selects both values for five, and the leaf subtree selects three, totaling eight.'),([[3,22,5],[-1,0,1]],'Value 22 is individually invalid; the subtree maxima are eight, five, and five, totaling eighteen.')],SUBTREE_CASES,SUBTREE,[SUBTREE.replace('if mask&bit:valid=False;break','if False:valid=False;break'),SUBTREE.replace('if other[second]>=0','if other[second]>=0 and first&second')],['Allows repeated digits within one selected node value.','Combines only overlapping digit masks instead of disjoint masks.'],subtree_oracle,random_subtree,lesson('The goodness constraint is fully represented by a ten-bit mask of digits already used.','Compute a mask-sum knapsack bottom-up for every subtree, rejecting node values with repeated internal digits.','Initialize empty and optional-node states; merge each child using only disjoint masks; add the table maximum to the answer.','Every good subset splits uniquely into independent child-subtree subsets plus an optional root, and disjoint-mask merging enforces exactly the global digit condition.'),'O(n*3^10)','O(n*2^10)',8),
3576:entry('can_transform_to_equal',[('nums','list[int]'),('k','int')],'bool',['arrays','greedy','parity'],['nums has up to 100,000 entries, each either one or negative one.','One operation flips the signs of two adjacent entries; the same pair may be chosen repeatedly.','Return whether either uniform target is reachable using at most k operations.'],[([[1,-1,1,-1,1],3],'Two adjacent-pair flips make every entry one, within the limit.'),([[-1,-1,-1,1,1,1],5],'Neither all-one nor all-negative-one is reachable within the limit.')],EQUAL_CASES,EQUAL,[EQUAL.replace('min(operations(1),operations(-1))','operations(nums[0])'),EQUAL.replace("return used if nums[-1]*incoming==target else 10**30","return used")],['Checks only the target equal to the first original value and misses a cheaper opposite target.','Does not verify that the forced flips also make the final element equal to the target.'],equal_oracle,random_equal,lesson('Once a target sign is chosen, scanning left to right forces whether each adjacent pair must be flipped.','Greedily fix each position using its pair with the next position, then verify the last sign; test both targets.','Track whether the preceding pair flipped the current position; flip the next pair when the effective value differs, then verify the final value.','No later operation can change a position after its right-adjacent pair is passed, so every greedy choice is forced and therefore uses the unique minimum count for that target.'),'O(n)','O(1)',5),
}
