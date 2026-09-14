"""Third slice of workbook batch 123."""

from itertools import combinations, product

from .import_batch_055 import entry


def difference_oracle(args):
    first, second = args
    return [sorted(set(first) - set(second)), sorted(set(second) - set(first))]


def random_difference(rng):
    return [
        [rng.randint(-10, 10) for _ in range(rng.randint(1, 20))],
        [rng.randint(-10, 10) for _ in range(rng.randint(1, 20))],
    ]


def beautiful(values):
    return len(values) % 2 == 0 and all(values[index] != values[index + 1] for index in range(0, len(values), 2))


def deletion_oracle(args):
    nums = args[0]
    for removed in range(len(nums) + 1):
        for omitted in combinations(range(len(nums)), removed):
            skipped = set(omitted)
            if beautiful([value for index, value in enumerate(nums) if index not in skipped]):
                return removed


def random_deletion(rng):
    return [[rng.randint(1, 6) for _ in range(rng.randint(1, 11))]]


def palindrome_oracle(args):
    queries, length = args
    start = 10 ** (length - 1)
    end = 10**length
    found = []
    for number in range(start, end):
        text = str(number)
        if text == text[::-1]:
            found.append(number)
    return [found[query - 1] if query <= len(found) else -1 for query in queries]


def random_palindrome(rng):
    length = rng.randint(1, 4)
    maximum = 9 * 10 ** ((length - 1) // 2)
    return [[rng.randint(1, maximum + 5) for _ in range(rng.randint(1, 10))], length]


def coins_oracle(args):
    piles, k = args
    best = 0
    for counts in product(*(range(len(pile) + 1) for pile in piles)):
        if sum(counts) == k:
            best = max(best, sum(sum(pile[:count]) for pile, count in zip(piles, counts)))
    return best


def random_coins(rng):
    piles = [[rng.randint(1, 30) for _ in range(rng.randint(1, 4))] for _ in range(rng.randint(1, 4))]
    return [piles, rng.randint(1, sum(map(len, piles)))]


def score_oracle(args):
    nums = args[0]
    return max(max(sum(nums[: index + 1]), sum(nums[index:])) for index in range(len(nums)))


def random_score(rng):
    return [[rng.randint(-30, 30) for _ in range(rng.randint(1, 30))]]


DIFFERENCE = '''\
def distinct_array_differences(nums1,nums2):
    first,second=set(nums1),set(nums2)
    return [list(first-second),list(second-first)]
'''

DELETE = '''\
def minimum_beautiful_array_deletions(nums):
    kept=[];deleted=0
    for value in nums:
        if len(kept)%2==1 and kept[-1]==value:deleted+=1
        else:kept.append(value)
    if len(kept)%2:deleted+=1
    return deleted
'''

PALINDROME = '''\
def fixed_length_kth_palindromes(queries,int_length):
    half_length=(int_length+1)//2;start=10**(half_length-1);end=10**half_length;answer=[]
    for query in queries:
        half=start+query-1
        if half>=end:answer.append(-1);continue
        text=str(half);answer.append(int(text+text[-2::-1] if int_length%2 else text+text[::-1]))
    return answer
'''

COINS = '''\
def maximum_k_coin_value(piles,k):
    dp=[0]+[-1]*k
    for pile in piles:
        prefix=[0]
        for value in pile:prefix.append(prefix[-1]+value)
        updated=list(dp)
        for used in range(k+1):
            if dp[used]<0:continue
            for take in range(1,min(len(pile),k-used)+1):
                updated[used+take]=max(updated[used+take],dp[used]+prefix[take])
        dp=updated
    return dp[k]
'''

SCORE = '''\
def maximum_prefix_suffix_score(nums):
    total=sum(nums);prefix=0;answer=float('-inf')
    for value in nums:
        prefix+=value
        answer=max(answer,prefix,total-prefix+value)
    return answer
'''


BATCH = {
    2215: entry('distinct_array_differences',[('nums1','list[int]'),('nums2','list[int]')],'list[list[int]]',['arrays','hash sets'],['Return two rows: values unique to nums1, then values unique to nums2.','Each row contains distinct integers only.','Order inside either row does not matter, but the two row meanings may not be swapped.'],[([[1,2,3],[2,4,6]],'The first-only values are one and three; the second-only values are four and six.'),([[1,2,3,3],[1,1,2,2]],'Only three is absent from the second array, while no value is unique to the second.')],[[a,b] for a,b in [([1],[2]),([1],[1]),([1,2,3],[2,4,6]),([1,2,3,3],[1,1,2,2]),([1,1],[2,2]),([0,-1],[0,1]),([1,2],[3,4]),([1,2,3],[1,2,3]),([5,4,5],[4,3]),([-3,-2,-1],[-2,0]),([10,20,30],[20]),([7,7,8],[8,9,9]),([1,4,7],[2,5,8]),([0,0,0],[1])]],DIFFERENCE,[DIFFERENCE.replace('first-second','first&second'),DIFFERENCE.replace('second-first','first-second')],['Returns the intersection in the first row instead of first-only values.','Uses the first-minus-second set for both rows.'],difference_oracle,random_difference,['Set subtraction directly expresses values present in one array but absent in the other.','Convert both arrays to sets to remove duplicates before subtracting.','Return [list(set1-set2), list(set2-set1)].','Each difference contains exactly the required membership predicate and set semantics guarantee no duplicate output values.'],'O(n+m)','O(n+m)',3),
    2216: entry('minimum_beautiful_array_deletions',[('nums','list[int]')],'int',['arrays','greedy','stacks'],['The final list length must be even.','At every even final index i, values at i and i+1 must differ.','Deletions preserve the order of remaining values, and the empty list is valid.'],[([[1,1,2,3,5]],'Delete one of the leading equal values to obtain [1,2,3,5], so one deletion is enough.'),([[1,1,2,2,3,3]],'Two deletions are required to form valid unequal pairs with even length.')],[[x] for x in [[1],[1,1],[1,2],[1,1,2],[1,1,2,3,5],[1,1,2,2,3,3],[1,2,3],[1,2,1,2],[2,2,2,2],[1,2,2,3],[3,1,3,1,3],[1,1,1,2,3],[4,5,5,4,4,6],[7,7,8,9,9]]],DELETE,[DELETE.replace('len(kept)%2==1','len(kept)%2==0'),DELETE.replace('if len(kept)%2:deleted+=1','if len(kept)%2:pass')],['Rejects equal values while starting a pair instead of while completing it.','Leaves an odd final length instead of deleting its unmatched last value.'],deletion_oracle,random_deletion,['Build the final sequence from left to right in pairs.','When one value is waiting at an even index, delete every equal next value until a different partner appears.','Append legal values, count rejected equals, then delete one final unmatched value if the kept length is odd.','Keeping the earliest legal partner never hurts later pairings, while an equal partner can never occupy the required odd position.'],'O(n)','O(n)',6),
    2217: entry('fixed_length_kth_palindromes',[('queries','list[int]'),('int_length','int')],'list[int]',['arrays','math','palindromes'],['For each 1-indexed query, return that smallest positive palindrome with exactly int_length digits.','No palindrome may have a leading zero.','Return -1 when the requested rank exceeds all palindromes of that length.'],[([[1,2,3,4,5,90],3],'The first half prefixes 10 through 99 mirror to 101 through 999, so rank ninety is 999.'),([[2,4,6],4],'Prefixes 11,13,15 mirror to 1111,1331,1551.')],[[q,l] for q,l in [([1],1),([9],1),([10],1),([1],2),([9],2),([10],2),([1,2,3,4,5,90],3),([2,4,6],4),([1,5,9],3),([90,91],3),([1,10],4),([5,15,25],2),([1,2],4),([45,50],3)]],PALINDROME,[PALINDROME.replace('start+query-1','start+query'),PALINDROME.replace('half>=end','half>end')],['Uses a zero-based rank offset and skips the first palindrome.','Allows the first out-of-range half prefix and returns an overlong value.'],palindrome_oracle,random_palindrome,['A palindrome is determined entirely by its leading half, including the middle digit for odd lengths.','The valid half prefixes are consecutive integers starting at the smallest nonzero half.','Add query-1 to the starting half; reject past the half-length limit; mirror all or all but the middle digit.','Numeric order of fixed-length palindromes matches numeric order of their leading halves, giving a direct rank mapping.'],'O(queries*int_length)','O(output)',6),
    2218: entry('maximum_k_coin_value',[('piles','list[list[int]]'),('k','int')],'int',['arrays','dynamic programming','prefix sums'],['Coins in each pile are ordered from top to bottom.','Taking x coins from a pile requires taking exactly its first x values.','Take exactly k coins across all piles and maximize their total value.'],[([[[1,100,3],[7,8,9]],2],'Taking the first two coins from the first pile gives 101, better than every other valid choice.'),([[[100],[100],[100],[100],[100],[100],[1,1,1,1,1,1,700]],7],'Take one hundred from each of six piles and then the top one from the last pile for 601.')],[[p,k] for p,k in [([[1]],1),([[1,2]],1),([[1,2]],2),([[1,100,3],[7,8,9]],2),([[5],[10]],1),([[5],[10]],2),([[1,2],[3,4]],3),([[100],[100],[1,1,700]],3),([[2,2,2],[3,3]],4),([[9,1],[8,7]],2),([[1,10,100],[20]],3),([[4,5],[6],[7,8]],4),([[3,30,3],[10,10]],3),([[5,1,1],[4,4,4]],5)]],COINS,[COINS.replace('prefix[take]','pile[take-1]'),COINS.replace('updated=list(dp)','updated=[-1]*(k+1)')],['Adds only the last selected coin instead of the whole required pile prefix.','Forgets the option to take zero coins from the current pile.'],coins_oracle,random_coins,['A state needs only how many coins have been taken after processing some piles.','Precompute each pile’s prefix values and try every feasible take count from that pile.','Carry dp[used], update dp[used+take] with prior value plus prefix[take], and preserve take zero.','Every legal selection chooses one prefix length per pile; the transitions enumerate these choices and retain the best total for each exact count.'],'O(k*total coins)','O(k)',8),
    2219: entry('maximum_prefix_suffix_score',[('nums','list[int]')],'int',['arrays','prefix sums'],['For every index i, compare the prefix sum nums[0:i+1] with the suffix sum nums[i:n].','The shared value nums[i] belongs to both sums independently.','Return the largest of all prefix and suffix scores, including negative arrays.'],[([[4,3,-2,5]],'The largest considered prefix or suffix sum is ten.'),([[-3,-5]],'The best score is the one-element prefix -3 rather than an empty sum.')],[[x] for x in [[1],[-1],[4,3,-2,5],[-3,-5],[1,2,3],[3,2,1],[-1,5,-2],[10,-20,30],[-5,-4,-3],[0,0,0],[5,-1,-1,-1],[1,-2,3,-4,5],[100,-100,100],[-2,7,-3,4]]],SCORE,[SCORE.replace('total-prefix+value','total-prefix'),SCORE.replace("answer=float('-inf')","answer=0")],['Omits nums[i] from the inclusive suffix sum.','Allows an invalid empty score of zero for all-negative arrays.'],score_oracle,random_score,['Maintain one running prefix and derive each inclusive suffix from the total.','After adding nums[i] to prefix, suffix is total-prefix+nums[i].','Update the maximum with both prefix and suffix at every index, starting from negative infinity.','The scan evaluates exactly the two scores defined for every index, so their maximum is the required result.'],'O(n)','O(1)',5),
}

BATCH[2215]['comparator'] = 'unordered_rows'
BATCH[2216]['wrong'][0] = DELETE.replace('kept[-1]==value', 'kept[-1]!=value')
BATCH[2216]['wrong_reasons'][0] = 'Deletes a different value that would complete a valid pair and keeps equal invalid partners.'
BATCH[2218]['examples'][1] = (
    [[[100], [100], [100], [100], [100], [100], [1, 1, 1, 1, 1, 1, 700]], 7],
    'Taking the entire final pile yields 706 and is better than taking one coin from each of the six hundred-value piles.',
)
