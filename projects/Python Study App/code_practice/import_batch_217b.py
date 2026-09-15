"""Optimized good subsequences, repeated prefixes, rewards, bounded coins, and day pairs."""
from itertools import combinations

from .import_batch_055 import entry


def good_oracle(args):
    nums, limit = args; best = 0
    for size in range(1, len(nums)+1):
        for selected in combinations(range(len(nums)),size):
            if sum(nums[selected[i]] != nums[selected[i-1]] for i in range(1,size)) <= limit:best = size
    return best


def random_good(rng):return [[rng.randint(1,6) for _ in range(rng.randint(1,10))],rng.randint(0,4)]


def seconds_oracle(args):
    n, seconds = args; values = [1]*n
    for _ in range(seconds):
        for index in range(1,n):values[index]=(values[index]+values[index-1])%1_000_000_007
    return values[-1]


def random_seconds(rng):return [rng.randint(1,12),rng.randint(0,15)]


def reward_oracle(args):
    values = args[0]; best = 0
    def search(total,used):
        nonlocal best;best=max(best,total)
        for index,value in enumerate(values):
            if not used>>index&1 and value>total:search(total+value,used|1<<index)
    search(0,0);return best


def random_reward(rng):return [[rng.randint(1,25) for _ in range(rng.randint(1,10))]]


def sum_oracle(args):
    target=args[0];answer=0
    for fours in range(3):
        remaining=target-4*fours
        if remaining<0:continue
        for sixes in range(remaining//6+1):answer+=(remaining-6*sixes)//2+1
    return answer%1_000_000_007


def random_sum(rng):return [rng.randint(0,100)]


def day_oracle(args):
    hours=args[0]
    return sum((hours[i]+hours[j])%24==0 for i in range(len(hours)) for j in range(i+1,len(hours)))


def random_day(rng):return [[rng.randint(1,200) for _ in range(rng.randint(1,20))]]


GOOD = '''def longest_good_subsequence_optimized(nums,k):
    states={};leaders=[[(-1,None),(-1,None)] for _ in range(k+1)];answer=0
    for value in nums:
        row=states.setdefault(value,[0]*(k+1))
        for changes in range(k,-1,-1):
            candidate=row[changes]+1
            if changes:
                first,second=leaders[changes-1]
                other=first if first[1]!=value else second
                candidate=max(candidate,other[0]+1)
            if candidate>row[changes]:row[changes]=candidate
            first,second=leaders[changes]
            if first[1]==value:first=(max(first[0],candidate),value)
            elif second[1]==value:second=(max(second[0],candidate),value)
            elif candidate>first[0]:second=first;first=(candidate,value)
            elif candidate>second[0]:second=(candidate,value)
            if second[0]>first[0]:first,second=second,first
            leaders[changes]=[first,second];answer=max(answer,candidate)
    return answer
'''


SECONDS = '''def nth_value_after_seconds(n,k):
    modulo=1000000007;answer=1
    for value in range(1,n):answer=answer*(k+value)%modulo*pow(value,modulo-2,modulo)%modulo
    return answer
'''


REWARD = '''def maximum_total_reward(rewardValues):
    reachable=1
    for value in sorted(set(rewardValues)):reachable|=(reachable&((1<<value)-1))<<value
    return reachable.bit_length()-1
'''


WAYS = '''def ways_to_make_sum(n):
    modulo=1000000007;ways=[0]*(n+1);ways[0]=1
    for coin in (1,2,6):
        for total in range(coin,n+1):ways[total]=(ways[total]+ways[total-coin])%modulo
    return sum(ways[n-4*count] for count in range(3) if n>=4*count)%modulo
'''


DAY = '''def complete_day_pairs(hours):
    counts=[0]*24;answer=0
    for value in hours:
        remainder=value%24;answer+=counts[-remainder%24];counts[remainder]+=1
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
3177:entry('longest_good_subsequence_optimized',[('nums','list[int]'),('k','int')],'int',['dynamic programming','hash tables','subsequences'],['nums is nonempty and k is nonnegative.','Choose a subsequence in original order with at most k adjacent chosen pairs having different values.','Return its maximum length; the intended solution must scale without comparing every pair of indices.'],[([[1,2,1,1,3],2],'A length-four subsequence such as 1,2,1,1 uses two changes.'),([[1,1,2,2,1],1],'Taking all five values creates two changes, but four values can be chosen with at most one.')],[[n,k] for n,k in [([1],0),([1,2,1,1,3],2),([1,1,2,2,1],1),([1,1,1],0),([1,2,3],2),([1,2,3],0),([1,2,1,2],1),([3,3,2,2,1],2),([5,4,3,2,1],3),([1,1,2,2,3,3],1),([2,1,2,1,2],2),([7,7,8,7,8,8],1),([1,2,3,1,2,3],3),([4,1,4,2,4,3],1)]],GOOD,["""def longest_good_subsequence_optimized(nums,k):
    return min(len(nums),max(nums.count(value) for value in set(nums))+k)
""","""def longest_good_subsequence_optimized(nums,k):
    best=left=0;changes=0
    for right in range(len(nums)):
        if right and nums[right]!=nums[right-1]:changes+=1
        while changes>k:
            left+=1
            if nums[left]!=nums[left-1]:changes-=1
        best=max(best,right-left+1)
    return best
"""],['Assumes each permitted change can add only one element beyond the most frequent value.','Finds only a contiguous window even though arbitrary intervening indices may be skipped.'],good_oracle,random_good,lesson('For each change budget, extension needs the best prior length ending in the same value or the best ending in a different value.','Store per-value states plus the top two lengths with distinct ending values for every budget.','Process budgets descending; take same-value state+1 or best different value at budget-1+1; refresh top two.','The top-two structure returns the true best eligible different endpoint in constant time, and descending updates prevent reusing the current index.'),'O(nk)','O(distinct values*k)',8),
3179:entry('nth_value_after_seconds',[('n','int'),('k','int')],'int',['combinatorics','prefix sums'],['n is positive and k is nonnegative.','Begin with n ones; during each second replace each position by the prefix sum through that position.','Return the final value at index n-1 modulo 1,000,000,007.'],[([4,5],'Five rounds of prefix sums make the fourth value 56.'),([1,100],'The first position always remains one regardless of the number of seconds.')],[[n,k] for n,k in [(1,0),(1,100),(4,5),(2,1),(2,5),(3,2),(5,0),(5,1),(6,3),(10,10),(3,20),(12,4),(8,15),(20,2)]],SECONDS,[SECONDS.replace('range(1,n)','range(1,n+1)'),SECONDS.replace('k+value','k+value-1')],['Computes one extra multiplicative term and returns the next array position.','Uses the wrong shifted binomial factors, corresponding to one fewer prefix-sum round.'],seconds_oracle,random_seconds,lesson('Repeated prefix sums count weak compositions and yield the binomial coefficient C(k+n-1,n-1).','Compute that coefficient multiplicatively modulo the prime using modular inverses.','Multiply (k+i)/i for i from one through n-1.','The hockey-stick identity advances one prefix-sum round, proving the closed form by induction on k.'),'O(n log modulo)','O(1)',5),
3180:entry('maximum_total_reward',[('rewardValues','list[int]')],'int',['bitsets','dynamic programming','sorting'],['rewardValues is a nonempty positive-integer array.','Start at total zero; choose each index at most once and only when its reward is strictly greater than the current total.','Return the maximum reachable total.'],[([[1,1,3,3]],'Choose one reward one and then one reward three to total four.'),([[1,6,4,3,2]],'Choosing one, two, four, then six is illegal at the last step; choosing one, four, then six reaches the optimal total eleven.')],[[v] for v in [[1],[1,1,3,3],[1,6,4,3,2],[1,2],[2,2],[1,2,4,8],[2,3,4],[5,1,2],[3,6,10],[1,1,1],[4,7,9],[2,5,11,12],[10,20,21],[1,3,7,15]]],REWARD,[REWARD.replace('(1<<value)-1','(1<<(value+1))-1'),REWARD.replace('sorted(set(rewardValues))','sorted(rewardValues,reverse=True)')],['Allows a prior total equal to the chosen reward even though the inequality is strict.','Processes large rewards first, losing reachable totals that require smaller rewards beforehand.'],reward_oracle,random_reward,lesson('A bitset can mark every reachable total; reward v may extend only bits at positions below v.','Process distinct rewards ascending and shift the eligible low prefix by v.','reachable |= (reachable & ((1<<v)-1)) << v; answer highest set bit.','Each shift represents exactly one legal append of v, and ascending distinct processing is sufficient because any legal sequence is strictly increasing in chosen reward.'),'O(max reward*distinct/word size)','O(max reward)',5),
3183:entry('ways_to_make_sum',[('n','int')],'int',['dynamic programming','knapsack'],['n is nonnegative.','Coins valued one, two, and six are unlimited; at most two coins valued four are available.','Count unordered coin multisets summing to n, modulo 1,000,000,007.'],[([4],'Using no four gives 1+1+1+1, 1+1+2, or 2+2; using one four gives the fourth way.'),([8],'Count unlimited-coin ways for residual sums eight, four, and zero, corresponding to zero, one, or two four-coins.')],[[n] for n in [0,1,2,3,4,5,6,7,8,9,10,12,20,50]],WAYS,[WAYS.replace('range(3)','range(2)'),WAYS.replace('(1,2,6)','(1,2,4,6)')],['Allows at most one four-valued coin instead of two.','Treats four as unlimited rather than restricting it to two copies.'],sum_oracle,random_sum,lesson('Separate the bounded four-valued coin from the three unlimited denominations.','Compute ordinary combination DP for coins 1,2,6, then choose zero, one, or two fours and look up the residual.','ways[0]=1; loop coins then totals ascending; return ways[n]+ways[n-4]+ways[n-8].','Coin-first DP counts unordered multisets once, and the three disjoint four-coin counts exhaust the bounded choices.'),'O(n)','O(n)',5),
3185:entry('complete_day_pairs',[('hours','list[int]')],'int',['hash tables','counting','modular arithmetic'],['hours is a nonempty positive-integer array.','Count index pairs i<j whose sum is an exact multiple of 24.','Equal hour values at different indices count as distinct choices.'],[([[12,12,30,24,24]],'The two twelves form one pair and the two multiples of 24 form another, totaling two.'),([[24,48,72]],'Every pair sums to a multiple of 24, so all three pairs count.')],[[h] for h in [[1],[12,12,30,24,24],[24,48,72],[1,23],[1,2,3],[6,18,30,42],[12,36,60],[5,19,29,43],[24,1,23],[10,14,34,38],[7,17,7,17],[100,20,44],[11,13,35,37],[48,96],[25,47]]],DAY,[DAY.replace('counts[-remainder%24]','counts[(24-remainder)%23]'),DAY.replace('remainder=value%24','remainder=value%23')],['Wraps complement buckets with modulus 23 instead of 24.','Reduces hours modulo 23 instead of one complete 24-hour day.'],day_oracle,random_day,lesson('Only each hour modulo 24 matters; a remainder r pairs with (-r) modulo 24.','Scan left to right, counting matching earlier complements before inserting the current remainder.','answer+=count[(-r)%24]; count[r]+=1.','Every valid pair is counted exactly once when its later index is processed.'),'O(n)','O(1)',5),
}
