"""Grid-state, subsequence, pair-sweep, heap, and subset-DP imports."""
from functools import lru_cache
from itertools import combinations, product

from .import_batch_055 import entry


PAIR = ((0, 0, 0), (0, -60, -10), (0, -10, 40))


def happiness_oracle(args):
    rows, cols, introverts, extroverts = args; cells = rows * cols; best = 0
    for assignment in product(range(3), repeat=cells):
        if assignment.count(1) > introverts or assignment.count(2) > extroverts:continue
        score = sum(120 if value == 1 else 40 if value == 2 else 0 for value in assignment)
        for index, value in enumerate(assignment):
            if index % cols and value and assignment[index - 1]:score += PAIR[value][assignment[index - 1]]
            if index >= cols and value and assignment[index - cols]:score += PAIR[value][assignment[index - cols]]
        best = max(best, score)
    return best


def random_happiness(rng):
    rows, cols = rng.choice([(1,1),(1,2),(1,3),(2,2),(2,3)])
    return [rows, cols, rng.randint(0, min(4, rows * cols)), rng.randint(0, min(4, rows * cols))]


def mountain_oracle(args):
    nums = args[0]; best = 0
    for mask in range(1 << len(nums)):
        values = [value for index, value in enumerate(nums) if mask >> index & 1]
        if len(values) < 3:continue
        for peak in range(1, len(values) - 1):
            if all(values[i] < values[i + 1] for i in range(peak)) and all(values[i] > values[i + 1] for i in range(peak, len(values) - 1)):
                best = max(best, len(values));break
    return len(nums) - best


def random_mountain(rng):
    while True:
        values = [rng.randint(1, 12) for _ in range(rng.randint(3, 10))]
        if mountain_oracle([values]) < len(values):return [values]


def complementary_oracle(args):
    nums, limit = args; best = len(nums)
    for target in range(2, 2 * limit + 1):
        moves = 0
        for left, right in zip(nums, reversed(nums)):
            if left + right == target:cost = 0
            elif 1 + min(left, right) <= target <= limit + max(left, right):cost = 1
            else:cost = 2
            moves += cost
        best = min(best, moves // 2)
    return best


def random_complementary(rng):
    limit = rng.randint(1, 9); size = 2 * rng.randint(1, 6)
    return [[rng.randint(1, limit) for _ in range(size)], limit]


def deviation_oracle(args):
    choices = []
    for value in args[0]:
        maximum = value * 2 if value % 2 else value; values = []
        while True:
            values.append(maximum)
            if maximum % 2:break
            maximum //= 2
        choices.append(values)
    return min(max(values) - min(values) for values in product(*choices))


def random_deviation(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 7))]]


def incompatibility_oracle(args):
    nums, groups = args; size = len(nums) // groups; full = (1 << len(nums)) - 1
    @lru_cache(None)
    def visit(mask):
        if mask == full:return 0
        first = next(index for index in range(len(nums)) if not mask >> index & 1)
        answer = float('inf')
        available = [index for index in range(first + 1, len(nums)) if not mask >> index & 1]
        for rest in combinations(available, size - 1):
            chosen = (first,) + rest; values = [nums[index] for index in chosen]
            if len(set(values)) < size:continue
            following = mask
            for index in chosen:following |= 1 << index
            answer = min(answer, max(values) - min(values) + visit(following))
        return answer
    result = visit(0)
    return -1 if result == float('inf') else result


def random_incompatibility(rng):
    length = rng.choice([2,4,6,8]); groups = rng.choice([value for value in range(1, length + 1) if length % value == 0])
    return [[rng.randint(1, 6) for _ in range(length)], groups]


HAPPINESS = '''def maximum_grid_happiness(m,n,introverts_count,extroverts_count):
    pair=((0,0,0),(0,-60,-10),(0,-10,40));limit=3**n;digits=[];inside=[];intro=[];extro=[]
    for state in range(limit):
        row=[];value=state
        for _ in range(n):row.append(value%3);value//=3
        digits.append(row);intro.append(row.count(1));extro.append(row.count(2))
        score=sum(120 if value==1 else 40 if value==2 else 0 for value in row)
        score+=sum(pair[row[index-1]][row[index]] for index in range(1,n))
        inside.append(score)
    cross={(above,row):sum(pair[a][b] for a,b in zip(digits[above],digits[row])) for above in range(limit) for row in range(limit)}
    dp={(0,0,0):0}
    for _ in range(m):
        following={}
        for (previous,used_i,used_e),score in dp.items():
            for state in range(limit):
                ni,ne=used_i+intro[state],used_e+extro[state]
                if ni<=introverts_count and ne<=extroverts_count:
                    key=(state,ni,ne);following[key]=max(following.get(key,-1),score+inside[state]+cross[(previous,state)])
        dp=following
    return max(dp.values())
'''

MOUNTAIN = '''def minimum_mountain_removals(nums):
    n=len(nums);up=[1]*n;down=[1]*n
    for right in range(n):
        for left in range(right):
            if nums[left]<nums[right]:up[right]=max(up[right],up[left]+1)
    for left in range(n-1,-1,-1):
        for right in range(left+1,n):
            if nums[left]>nums[right]:down[left]=max(down[left],down[right]+1)
    longest=max(up[index]+down[index]-1 for index in range(1,n-1) if up[index]>1 and down[index]>1)
    return n-longest
'''

COMPLEMENT = '''def minimum_complementary_moves(nums,limit):
    delta=[0]*(2*limit+2);pairs=len(nums)//2
    for index in range(pairs):
        left,right=nums[index],nums[-1-index];low=1+min(left,right);high=limit+max(left,right);total=left+right
        delta[2]+=2;delta[low]-=1;delta[total]-=1;delta[total+1]+=1;delta[high+1]+=1
    answer=2*pairs;moves=0
    for target in range(2,2*limit+1):moves+=delta[target];answer=min(answer,moves)
    return answer
'''

DEVIATION = '''def minimum_array_deviation(nums):
    import heapq
    heap=[];minimum=float('inf')
    for value in nums:
        value=value*2 if value%2 else value;minimum=min(minimum,value);heapq.heappush(heap,-value)
    answer=float('inf')
    while True:
        maximum=-heapq.heappop(heap);answer=min(answer,maximum-minimum)
        if maximum%2:return answer
        maximum//=2;minimum=min(minimum,maximum);heapq.heappush(heap,-maximum)
'''

INCOMPATIBILITY = '''def minimum_total_incompatibility(nums,k):
    n=len(nums);group=n//k;size=1<<n;cost={}
    for mask in range(size):
        if mask.bit_count()!=group:continue
        values=[nums[index] for index in range(n) if mask>>index&1]
        if len(set(values))==group:cost[mask]=max(values)-min(values)
    dp=[float('inf')]*size;dp[0]=0
    for mask in range(size):
        if dp[mask]==float('inf') or mask==size-1:continue
        first=next(index for index in range(n) if not mask>>index&1)
        for subset,value in cost.items():
            if subset>>first&1 and not subset&mask:dp[mask|subset]=min(dp[mask|subset],dp[mask]+value)
    return -1 if dp[-1]==float('inf') else dp[-1]
'''

INCOMPATIBILITY_GREEDY = '''def minimum_total_incompatibility(nums,k):
    nums=sorted(nums);size=len(nums)//k
    total=0
    for start in range(0,len(nums),size):
        group=nums[start:start+size]
        if len(set(group))<size:return -1
        total+=group[-1]-group[0]
    return total
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH = {
1659: entry('maximum_grid_happiness',[('m','int'),('n','int'),('introverts_count','int'),('extroverts_count','int')],'int',['dynamic programming','state compression','grids'],['1 <= m,n <= 5 and each people count is between zero and six.','An introvert contributes 120 base happiness and loses 30 per occupied neighbor; an extrovert contributes 40 and gains 20 per occupied neighbor.','Place at most the supplied people to maximize total happiness.'],[([2,3,1,2],'One optimal placement separates the introvert while the two extroverts benefit from adjacency, totaling 240.'),([1,1,1,1],'Only one person fits; choosing the introvert gives 120 rather than the extrovert’s 40.')],[[m,n,i,e] for m,n,i,e in [(1,1,0,0),(1,1,1,0),(1,1,0,1),(1,2,1,1),(1,3,2,1),(2,1,2,0),(2,2,1,1),(2,2,2,2),(2,3,0,3),(2,3,3,0),(2,3,2,2),(3,2,1,3),(3,2,3,1),(2,2,4,4)]],HAPPINESS,[HAPPINESS.replace('+cross[(previous,state)]','+0'),HAPPINESS.replace('else 40 if value==2','else 120 if value==2')],['Ignores vertical neighbor effects between consecutive rows.','Gives extroverts the introvert base score of 120 instead of 40.'],happiness_oracle,random_happiness,lesson('A row’s ternary digits encode empty, introvert, or extrovert cells.','Precompute each row’s internal score and every adjacent-row interaction score.','DP by row, previous row state, and counts of each personality already used.','All effects are local to horizontal neighbors in the row and vertical neighbors in the preceding row, so the compressed state retains every fact needed for future scoring.'),'O(m*3^(2n)*I*E)','O(3^n*I*E)',8),
1671: entry('minimum_mountain_removals',[('nums','list[int]')],'int',['dynamic programming','longest increasing subsequence'],['nums has 3 through 1000 positive integers and can be reduced to a strict mountain.','A mountain strictly increases to an interior peak and then strictly decreases.','Return the fewest removals while preserving relative order.'],[([[1,3,1]],'The entire three-element array already strictly rises then falls, so no removal is needed.'),([[2,1,1,5,6,2,3,1]],'A longest mountain has five elements, so three of the eight values must be removed.')],[[x] for x in [[1,2,1],[1,2,3,2,1],[1,3,2],[3,5,3,2],[1,4,2,3,1],[2,2,3,2,1],[1,2,2,3,2,1],[5,1,2,3,1],[1,5,4,3,2],[1,2,4,3,5,2,1],[9,8,1,2,3,2,1],[1,3,5,4,2,6,1],[1,2,3,4,3,2,1],[4,1,3,2]]],MOUNTAIN,[MOUNTAIN.replace('<nums[right]','<=nums[right]'),MOUNTAIN.replace('up[index]+down[index]-1','up[index]')],['Allows equal adjacent values on the increasing side.','Uses only the increasing subsequence length and ignores the required descending side.'],mountain_oracle,random_mountain,lesson('For each possible peak, measure the longest strict rise ending there and strict fall starting there.','Compute LIS lengths from the left and mirrored LIS lengths from the right.','Only peaks with both lengths above one are valid; maximize left+right-1.','Every retained mountain has one peak and two such subsequences, while joining the best compatible sides at a peak creates a valid mountain.'),'O(n²)','O(n)',8),
1674: entry('minimum_complementary_moves',[('nums','list[int]'),('limit','int')],'int',['arrays','difference arrays','sweep line'],['nums has even length and every value lies from 1 through limit.','One move replaces one value with any integer in that same range.','Choose one target sum so every mirrored pair nums[i]+nums[n-1-i] equals it, minimizing moves.'],[([[1,2,4,3],4],'Using target sum four leaves pair one-plus-three unchanged and changes one value in pair two-plus-four.'),([[1,2,2,1],2],'Both mirrored pairs already sum to two, so return zero.')],[[x,l] for x,l in [([1,1],1),([1,2],2),([1,1,1,1],2),([1,2,1,2],2),([2,2,2,2],2),([1,3,2,2],3),([1,4,1,4],4),([1,4,2,3],4),([2,3,1,4,2,3],4),([5,1,2,4],5),([1,5,5,1,3,3],5),([2,2,4,4,1,5],5),([3,1,3,1],3),([1,2,3,4,5,6],6)]],COMPLEMENT,["def minimum_complementary_moves(nums,limit):\n    pairs=len(nums)//2\n    return min(sum(nums[i]+nums[-1-i]!=target for i in range(pairs)) for target in range(2,2*limit+1))\n", "def minimum_complementary_moves(nums,limit):\n    target=limit+1;pairs=len(nums)//2;answer=0\n    for i in range(pairs):\n        a,b=nums[i],nums[-1-i]\n        answer+=0 if a+b==target else 1 if 1+min(a,b)<=target<=limit+max(a,b) else 2\n    return answer\n"],['Assumes every mismatched pair costs one move, even when the target cannot be reached by changing only one value.','Checks only target limit+1 instead of sweeping every feasible common sum.'],complementary_oracle,random_complementary,lesson('For one mirrored pair, cost is two generally, one over a reachable interval, and zero at its current sum.','Encode those cost changes in a difference array over target sums.','Add transitions at 2, 1+min, current sum, current sum+1, limit+max+1; prefix-scan the minimum.','Summing pairwise piecewise costs gives the exact total cost for each target, and the sweep visits every possible target once.'),'O(n+limit)','O(limit)',5),
1675: entry('minimum_array_deviation',[('nums','list[int]')],'int',['greedy','heaps','math'],['nums contains 2 through 50000 positive integers at most 10^9.','An even value may be halved; an odd value may be doubled. Apply operations any number of times.','Minimize maximum value minus minimum value.'],[([[1,2,3,4]],'Normalize to two, two, six, four and halve six to three and four to two; range two through three has deviation one.'),([[4,1,5,20,3]],'The best reachable values have maximum five and minimum three, giving deviation two.')],[[x] for x in [[1,2],[2,4],[1,3],[3,5],[2,3],[4,10],[1,2,3],[2,8,6],[5,10,15],[7,14,28],[8,4,2],[9,4,2],[100,1],[6,10,15,20]]],DEVIATION,[DEVIATION.replace('value=value*2 if value%2 else value','value=value'),DEVIATION.replace('while True:','for _ in range(1):')],['Fails to double odd inputs before comparing their full reachable ranges.','Halves the current maximum at most once and can stop before reaching the best range.'],deviation_oracle,random_deviation,lesson('Normalize every number to its greatest reachable even value.','Track the current maximum in a max-heap and the current minimum separately.','Measure the range, then repeatedly halve the maximum while it is even, updating the minimum.','Only decreasing the current maximum can improve the range; when it becomes odd it cannot decrease again, so no further operation can improve that normalized search path.'),'O(n log V log n)','O(n)',8),
1681: entry('minimum_total_incompatibility',[('nums','list[int]'),('k','int')],'int',['dynamic programming','bitmasks','backtracking'],['nums has at most 16 positive integers and its length is divisible by k.','Partition all positions into k equal-size groups; duplicate values may not appear within one group.','A group costs max-min. Return the minimum total cost, or -1 when no valid partition exists.'],[([[1,2,1,4],2],'Groups [1,2] and [1,4] cost one and three, totaling four.'),([[6,3,8,1,3,1,2,2],4],'Four duplicate-free pairs can be selected with total incompatibility six.')],[[n,k] for n,k in [([1,2],1),([1,1],1),([1,1],2),([1,2,3,4],2),([1,1,2,2],2),([1,1,1,2],2),([1,2,3,4],4),([1,2,1,4],2),([1,2,1,2,1,2],3),([1,2,3,1,2,3],2),([1,2,3,4,5,6],3),([1,1,2,2,3,3,4,4],4),([1,1,1,1],2),([4,3,2,1,4,3,2,1],4)]],INCOMPATIBILITY,[INCOMPATIBILITY.replace('if len(set(values))==group','if True'),INCOMPATIBILITY_GREEDY],['Allows repeated values inside a group.','Sorts into consecutive groups greedily, which can be invalid or more expensive than interleaving values.'],incompatibility_oracle,random_incompatibility,lesson('Treat positions as distinct bits even when their values repeat.','Precompute every duplicate-free subset of one group size and its max-minus-min cost.','DP over used-position masks, requiring each next group to contain the first unused position to avoid group-order duplicates.','Every valid partition has exactly one sequence under the first-unused rule, and minimizing the sum over all compatible group subsets examines every partition.'),'O(3^n)','O(2^n)',8),
}
