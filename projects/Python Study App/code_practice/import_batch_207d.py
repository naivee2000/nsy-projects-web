"""Palindromic, stacking, partition, median, and expiration-heap imports."""
from functools import lru_cache
from itertools import permutations, product
from math import factorial

from .import_batch_055 import entry


def good_palindrome_oracle(args):
    text = args[0]; best = 0
    for mask in range(1 << len(text)):
        value = ''.join(text[index] for index in range(len(text)) if mask >> index & 1)
        if len(value) % 2 or value != value[::-1]:continue
        middle = len(value) // 2
        if all(value[index] != value[index + 1] for index in range(max(0, middle - 1))):best = max(best, len(value))
    return best


def random_good_palindrome(rng):
    return [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 10)))]


def cuboid_oracle(args):
    cuboids = args[0]; best = 0
    orientations = [list(set(permutations(cuboid))) for cuboid in cuboids]
    def visit(base, used, height):
        nonlocal best
        best = max(best, height)
        for index in range(len(cuboids)):
            if used >> index & 1:continue
            for width, length, tall in orientations[index]:
                if width <= base[0] and length <= base[1] and tall <= base[2]:
                    visit((width, length, tall), used | 1 << index, height + tall)
    visit((float('inf'),) * 3, 0, 0)
    return best


def random_cuboids(rng):
    return [[[rng.randint(1, 9) for _ in range(3)] for _ in range(rng.randint(1, 5))]]


def candy_oracle(args):
    count, bags = args
    if bags > count:return 0
    labeled = sum(len(set(assignment)) == bags for assignment in product(range(bags), repeat=count))
    return labeled // factorial(bags) % 1_000_000_007


def random_candy(rng):
    count = rng.randint(1, 8)
    return [count, rng.randint(1, count)]


def swaps_oracle(args):
    nums, needed = args; positions = [index for index, value in enumerate(nums) if value]
    best = float('inf')
    for start in range(len(nums) - needed + 1):
        for chosen in __import__('itertools').combinations(positions, needed):
            best = min(best, sum(abs(position - (start + offset)) for offset, position in enumerate(chosen)))
    return best


def random_swaps(rng):
    length = rng.randint(1, 10); nums = [rng.randrange(2) for _ in range(length)]
    if not any(nums):nums[rng.randrange(length)] = 1
    return [nums, rng.randint(1, sum(nums))]


def apples_oracle(args):
    apples, days = args
    @lru_cache(None)
    def visit(day, batches):
        active = [(expires, count) for expires, count in batches if expires > day and count]
        if day < len(apples) and apples[day]:active.append((day + days[day], apples[day]))
        active.sort(); state = tuple(active)
        if day >= len(apples) and not state:return 0
        best = visit(day + 1, state)
        for index, (expires, count) in enumerate(state):
            following = list(state)
            if count == 1:following.pop(index)
            else:following[index] = (expires, count - 1)
            best = max(best, 1 + visit(day + 1, tuple(following)))
        return best
    return visit(0, ())


def random_apples(rng):
    count = rng.randint(1, 7); apples=[]; days=[]
    for _ in range(count):
        amount = rng.randint(0, 3);apples.append(amount);days.append(rng.randint(1, 4) if amount else 0)
    return [apples, days]


GOOD = '''def longest_good_palindromic_subsequence(s):
    n=len(s);alphabet=26;dp=[[[0]*alphabet for _ in range(n)] for _ in range(n)]
    for length in range(2,n+1):
        for left in range(n-length+1):
            right=left+length-1
            for char in range(alphabet):
                dp[left][right][char]=max(dp[left+1][right][char],dp[left][right-1][char])
            if s[left]==s[right]:
                char=ord(s[left])-97;inside=0
                if left+1<=right-1:inside=max((dp[left+1][right-1][other] for other in range(alphabet) if other!=char),default=0)
                dp[left][right][char]=max(dp[left][right][char],inside+2)
    return max(dp[0][n-1],default=0)
'''

ORDINARY = '''def longest_good_palindromic_subsequence(s):
    n=len(s);dp=[[0]*n for _ in range(n)]
    for i in range(n):dp[i][i]=1
    for length in range(2,n+1):
        for i in range(n-length+1):
            j=i+length-1
            dp[i][j]=dp[i+1][j-1]+2 if s[i]==s[j] else max(dp[i+1][j],dp[i][j-1])
    return dp[0][-1]
'''

ONE_PAIR = '''def longest_good_palindromic_subsequence(s):
    return 2 if any(s.count(char)>=2 for char in set(s)) else 0
'''

CUBOIDS = '''def maximum_cuboid_stack_height(cuboids):
    boxes=sorted(sorted(box) for box in cuboids);dp=[box[2] for box in boxes]
    for top in range(len(boxes)):
        for bottom in range(top):
            if all(boxes[bottom][axis]<=boxes[top][axis] for axis in range(3)):
                dp[top]=max(dp[top],dp[bottom]+boxes[top][2])
    return max(dp)
'''

CANDIES = '''def candy_distribution_ways(n,k):
    mod=1000000007;dp=[0]*(k+1);dp[0]=1
    for candies in range(1,n+1):
        following=[0]*(k+1)
        for bags in range(1,min(candies,k)+1):
            following[bags]=(dp[bags-1]+bags*dp[bags])%mod
        dp=following
    return dp[k]
'''

CANDIES_LABELED = '''def candy_distribution_ways(n,k):
    return pow(k,n,1000000007)
'''

CANDIES_ONE = '''def candy_distribution_ways(n,k):
    return 1
'''

SWAPS = '''def minimum_swaps_for_consecutive_ones(nums,k):
    positions=[index-order for order,index in enumerate(i for i,value in enumerate(nums) if value)]
    prefix=[0]
    for value in positions:prefix.append(prefix[-1]+value)
    answer=float('inf')
    for left in range(len(positions)-k+1):
        right=left+k;middle=left+k//2;median=positions[middle]
        cost=median*(middle-left)-(prefix[middle]-prefix[left])
        cost+=(prefix[right]-prefix[middle+1])-median*(right-middle-1)
        answer=min(answer,cost)
    return answer
'''

APPLES = '''def maximum_eaten_apples(apples,days):
    import heapq
    heap=[];day=eaten=0
    while day<len(apples) or heap:
        if day<len(apples) and apples[day]:heapq.heappush(heap,[day+days[day],apples[day]])
        while heap and (heap[0][0]<=day or heap[0][1]==0):heapq.heappop(heap)
        if heap:
            heap[0][1]-=1;eaten+=1
            if heap[0][1]==0:heapq.heappop(heap)
        day+=1
    return eaten
'''

APPLES_NEWEST = '''def maximum_eaten_apples(apples,days):
    batches=[];day=eaten=0
    while day<len(apples) or batches:
        batches=[batch for batch in batches if batch[0]>day and batch[1]>0]
        if day<len(apples) and apples[day]:batches.append([day+days[day],apples[day]])
        if batches:
            batches[-1][1]-=1;eaten+=1
        day+=1
    return eaten
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH = {
1682: entry('longest_good_palindromic_subsequence',[('s','str')],'int',['strings','dynamic programming','subsequences'],['s contains 1 through 250 lowercase letters.','A good subsequence is an even-length palindrome with unequal consecutive characters except for its equal middle pair.','Return the maximum possible good-subsequence length; return zero when no pair exists.'],[(['bbabab'],'The subsequence baab is a good palindrome of length four; its only equal adjacent letters are the middle pair.'),(['dcbccacdb'],'The subsequence dccd has length four and satisfies the same adjacency rule.')],[[s] for s in ['a','aa','ab','aaa','aba','abba','bbbb','abab','aabb','abcba','abcabc','baab','abcddcba','aabbaa']],GOOD,[ORDINARY,ONE_PAIR],['Computes an ordinary longest palindromic subsequence and may return an odd length or repeated outer neighbors.','Returns only one matching pair and misses longer good palindromes with alternating outer characters.'],good_palindrome_oracle,random_good_palindrome,lesson('Record the outer character of each good palindrome, not just its length.','For equal endpoints c, wrap the best inner palindrome whose outer character is not c.','DP over intervals and 26 possible outer letters; also carry solutions from either smaller interval.','Wrapping adds an equal endpoint pair, and excluding the same inner outer character enforces every non-middle adjacency; every good palindrome decomposes this way.'),'O(26*n²)','O(26*n²)',8),
1691: entry('maximum_cuboid_stack_height',[('cuboids','list[list[int]]')],'int',['dynamic programming','sorting','geometry'],['There are 1 through 100 cuboids with three positive dimensions at most 100.','You may rotate each cuboid; a top cuboid must have all three oriented dimensions no greater than the one below it.','Choose any subset and maximize the sum of oriented heights.'],[([[[50,45,20],[95,37,53],[45,23,12]]],'After canonical rotations, all three cuboids stack with heights 45, 50, and 95 for total 190.'),([[[38,25,45],[76,35,3]]],'The cuboids cannot stack compatibly, so rotate the second cuboid to height 76 and use it alone.')],[[c] for c in [[[1,1,1]],[[1,2,3]],[[1,1,1],[1,1,1]],[[1,2,3],[2,3,4]],[[4,3,2],[3,2,1]],[[3,3,3],[2,2,5]],[[7,11,17],[7,17,11],[11,7,17]],[[5,4,3],[6,5,4],[7,6,5]],[[1,10,10],[9,9,9]],[[2,8,4],[3,7,5],[6,6,6]],[[10,1,1],[2,2,9]],[[4,4,1],[4,3,2],[3,3,3]],[[8,2,6],[7,3,5],[4,4,4]],[[100,100,1],[99,99,99]]]],CUBOIDS,[CUBOIDS.replace('sorted(box)','box'),CUBOIDS.replace('all(boxes[bottom][axis]<=boxes[top][axis] for axis in range(3))','boxes[bottom][0]<=boxes[top][0]')],['Sorts cuboids but never normalizes rotations within each cuboid.','Checks only one dimension when deciding whether two cuboids can stack.'],cuboid_oracle,random_cuboids,lesson('Sort each cuboid’s three dimensions so its largest dimension is the chosen height.','Sort the normalized cuboids and run a three-dimensional longest increasing subsequence.','For each bottom cuboid, extend every earlier cuboid whose three dimensions fit componentwise.','Any feasible orientation can be normalized without reducing height, and the sorted order provides a topological order for every componentwise stack relation.'),'O(n²)','O(n)',8),
1692: entry('candy_distribution_ways',[('n','int'),('k','int')],'int',['dynamic programming','combinatorics'],['There are n uniquely labeled candies and k unlabeled nonempty bags, with 1 <= k <= n <= 1000.','Bag order and candy order within a bag do not matter; only the partition into groups matters.','Return the number of distributions modulo 1000000007.'],[([3,2],'Choose which one candy stands alone; the other two share the second bag, giving three partitions.'),([4,2],'The seven partitions consist of four one-plus-three splits and three two-plus-two splits.')],[[n,k] for n,k in [(1,1),(2,1),(2,2),(3,1),(3,3),(4,1),(4,3),(4,4),(5,2),(5,3),(5,4),(6,2),(7,3),(8,4)]],CANDIES,[CANDIES_LABELED,CANDIES_ONE],['Treats bags as labeled and also permits them to remain empty.','Assumes there is only one partition for every valid n and k.'],candy_oracle,random_candy,lesson('Add labeled candies one at a time to an unlabeled set partition.','The new candy either starts a new bag or joins one of the existing bags.','S(n,k)=S(n-1,k-1)+k*S(n-1,k); build a fresh row for each candy.','The two cases are disjoint and exhaustive, and a fresh row retains the previous candy count for both terms.'),'O(n*k)','O(k)',8),
1703: entry('minimum_swaps_for_consecutive_ones',[('nums','list[int]'),('k','int')],'int',['arrays','medians','prefix sums'],['nums has up to 100000 binary values and contains at least k ones.','One move swaps adjacent values; make some k ones occupy consecutive positions.','Return the minimum number of swaps.'],[([[1,0,0,1,0,1],2],'Move the final one left once to join the middle one, requiring one swap.'),([[1,0,0,0,0,0,1,1],3],'Move the first one five positions right to join the final pair.')],[[a,k] for a,k in [([1],1),([1,1],2),([1,0,1],2),([1,0,0,1],2),([0,1,0,1,0],2),([1,1,0,1],2),([1,0,1,0,1],3),([0,0,1,0,1,1],2),([1,0,0,0,1,0,1],2),([1,0,0,0,1,0,1],3),([1,1,1,0,0],3),([0,1,0,0,1,0,0,1],2),([1,0,1,1,0,1],3),([1,0,0,1,0,0,1,0,1],4)]],SWAPS,[SWAPS.replace('index-order','index'),SWAPS.replace('median=positions[middle]','median=positions[left]')],['Uses raw one positions without removing the unavoidable spacing between consecutive target cells.','Aligns every window to its first adjusted position instead of the median.'],swaps_oracle,random_swaps,lesson('For a chosen consecutive block of k existing ones, their relative order never needs to change.','Subtract each one’s rank so consecutive target positions collapse to one common adjusted coordinate.','Use prefix sums to measure absolute distance to the median for every length-k adjusted-position window.','The median minimizes total absolute distance, and every optimal solution uses some consecutive group in the ordered list of original one positions.'),'O(n)','O(number of ones)',8),
1705: entry('maximum_eaten_apples',[('apples','list[int]'),('days','list[int]')],'int',['greedy','heaps','scheduling'],['apples and days have equal length up to 20000; a zero apple count has zero shelf life.','Apples grown on day i rot at the start of day i+days[i].','Eat at most one apple per day, continuing after the growing period, to maximize the total eaten.'],[([[1,2,3,5,2],[3,2,1,4,2]],'Always consuming the earliest-expiring available batch allows seven apples to be eaten.'),([[3,0,0,0,0,2],[3,0,0,0,0,2]],'Eat three early apples before day three and both later apples before day seven, totaling five.')],[[a,d] for a,d in [([0],[0]),([1],[1]),([2],[1]),([2],[2]),([1,1],[1,1]),([1,1],[2,2]),([3,0,0],[3,0,0]),([0,2],[0,2]),([1,2,0],[3,1,0]),([2,1,3],[2,2,1]),([1,0,2,0],[2,0,3,0]),([3,1,0,2],[1,3,0,2]),([1,2,3,0,0],[5,1,1,0,0]),([2,0,1,4],[2,0,4,1])]],APPLES,[APPLES_NEWEST,APPLES.replace('while day<len(apples) or heap:','while day<len(apples):')],['Consumes the newest batch first and can let an earlier-expiring batch rot.','Stops eating when the tree stops producing, discarding still-fresh stored apples.'],apples_oracle,random_apples,lesson('When eating today, choose the available apple with the earliest expiration.','A min-heap stores batches by expiration day and remaining count.','Add today’s batch, remove expired/empty batches, consume one from the earliest expiration, and continue while production or inventory remains.','An exchange argument replaces any later-expiring apple eaten before an earlier one without hurting future feasibility, proving the greedy order.'),'O(total days log batches)','O(batches)',5),
}
