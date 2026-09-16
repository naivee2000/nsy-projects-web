"""Array, graph, digit-DP, and number-theory workbook imports."""
from collections import Counter, deque
from itertools import combinations, permutations
from math import comb

from .import_batch_055 import entry


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


def middle_oracle(args):
    nums = args[0]
    return -1 if len(nums) < 3 else sorted(nums)[1]


def random_middle(rng):
    return [rng.sample(range(1, 101), rng.randint(1, 15))]


def time_oracle(args):
    first, second, limit = args
    n = len(first)
    for elapsed in range(n + 1):
        baseline = sum(first) + elapsed * sum(second)
        best = 0
        for order in permutations(range(n), elapsed):
            best = max(best, sum(first[index] + (turn + 1) * second[index]
                                 for turn, index in enumerate(order)))
        if baseline - best <= limit:
            return elapsed
    return -1


def random_time(rng):
    n = rng.randint(1, 7)
    return [[rng.randint(0, 12) for _ in range(n)],
            [rng.randint(0, 8) for _ in range(n)], rng.randint(0, 45)]


def safest_oracle(args):
    grid = args[0]
    n = len(grid)
    thieves = [(r, c) for r in range(n) for c in range(n) if grid[r][c]]
    distance = [[min(abs(r-a) + abs(c-b) for a, b in thieves) for c in range(n)] for r in range(n)]
    for threshold in range(2 * n, -1, -1):
        if distance[0][0] < threshold:
            continue
        seen = {(0, 0)}
        pending = [(0, 0)]
        while pending:
            r, c = pending.pop()
            if (r, c) == (n - 1, n - 1):
                return threshold
            for nr, nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen and distance[nr][nc] >= threshold:
                    seen.add((nr, nc)); pending.append((nr, nc))
    return 0


def random_safest(rng):
    n = rng.randint(2, 6)
    grid = [[0] * n for _ in range(n)]
    for cell in rng.sample(range(n*n), rng.randint(1, max(1, n*n//3))):
        grid[cell//n][cell%n] = 1
    return [grid]


def elegance_oracle(args):
    items, k = args
    return max(sum(item[0] for item in chosen) + len({item[1] for item in chosen}) ** 2
               for chosen in combinations(items, k))


def random_elegance(rng):
    n = rng.randint(1, 9)
    return [[[rng.randint(1, 30), rng.randint(1, 5)] for _ in range(n)], rng.randint(1, n)]


def prime_score(value):
    score = 0
    factor = 2
    while factor * factor <= value:
        if value % factor == 0:
            score += 1
            while value % factor == 0:
                value //= factor
        factor += 1
    return score + (value > 1)


def score_oracle(args):
    nums, k = args
    choices = []
    scores = list(map(prime_score, nums))
    for left in range(len(nums)):
        for right in range(left, len(nums)):
            winner = max(range(left, right + 1), key=lambda index: (scores[index], -index))
            choices.append(nums[winner])
    answer = 1
    for value in sorted(choices, reverse=True)[:k]:
        answer = answer * value % 1_000_000_007
    return answer


def random_score(rng):
    nums = [rng.randint(1, 40) for _ in range(rng.randint(1, 9))]
    return [nums, rng.randint(1, min(20, len(nums)*(len(nums)+1)//2))]


def beautiful_oracle(args):
    low, high, divisor = args
    answer = 0
    for value in range(low, high + 1):
        text = str(value)
        answer += value % divisor == 0 and sum((int(char) % 2 == 0) - (int(char) % 2 == 1) for char in text) == 0
    return answer


def random_beautiful(rng):
    low = rng.randint(1, 3000)
    return [low, low + rng.randint(0, 800), rng.randint(1, 20)]


def can_subset(values, target):
    reachable = {0}
    for value in values:
        reachable |= {total + value for total in list(reachable) if total + value <= target}
    return target in reachable


def split_oracle(args):
    nums, target = args
    if sum(nums) < target:
        return -1
    start = tuple(sorted(nums))
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        values, moves = queue.popleft()
        if can_subset(values, target):
            return moves
        for index, value in enumerate(values):
            if value == 1:
                continue
            nxt = tuple(sorted(values[:index] + values[index+1:] + (value//2, value//2)))
            if nxt not in seen:
                seen.add(nxt); queue.append((nxt, moves + 1))
    return -1


def random_split(rng):
    nums = [1 << rng.randint(0, 5) for _ in range(rng.randint(1, 6))]
    return [nums, rng.randint(1, min(40, sum(nums) + 4))]


def beauty_oracle(args):
    text, k = args
    counts = Counter(text)
    if len(counts) < k:
        return 0
    best = ways = -1
    for letters in combinations(counts, k):
        beauty = sum(counts[letter] for letter in letters)
        count = 1
        for letter in letters:
            count *= counts[letter]
        if beauty > best:
            best, ways = beauty, count
        elif beauty == best:
            ways += count
    return ways % 1_000_000_007


def random_beauty(rng):
    text = ''.join(rng.choice('abcdefg') for _ in range(rng.randint(1, 18)))
    return [text, rng.randint(1, 8)]


def reversals_oracle(args):
    n, edges = args
    directed = {tuple(edge) for edge in edges}
    graph = [[] for _ in range(n)]
    for left, right in edges:
        graph[left].append(right); graph[right].append(left)
    answer = []
    for root in range(n):
        total = 0
        pending = [(root, -1)]
        while pending:
            node, parent = pending.pop()
            for other in graph[node]:
                if other != parent:
                    total += (node, other) not in directed
                    pending.append((other, node))
        answer.append(total)
    return answer


def random_reversals(rng):
    n = rng.randint(2, 12)
    edges = []
    for node in range(1, n):
        parent = rng.randrange(node)
        edges.append([parent, node] if rng.randrange(2) else [node, parent])
    return [n, edges]


def valid_paths_oracle(args):
    n, edges = args
    graph = [[] for _ in range(n + 1)]
    for left, right in edges:
        graph[left].append(right); graph[right].append(left)
    primes = [prime_score(value) == 1 and all(value % divisor for divisor in range(2, int(value**.5)+1)) for value in range(n + 1)]
    primes[0] = primes[1] = False
    answer = 0
    for start in range(1, n + 1):
        pending = [(start, 0, 0)]
        while pending:
            node, parent, count = pending.pop()
            count += primes[node]
            if node > start and count == 1:
                answer += 1
            if count <= 1:
                pending.extend((other, node, count) for other in graph[node] if other != parent)
    return answer


def random_paths(rng):
    n = rng.randint(2, 12)
    return [n, [[node, rng.randint(1, node-1)] for node in range(2, n+1)]]


MIDDLE = '''def neither_minimum_nor_maximum(nums):
    if len(nums)<3:return -1
    first=nums[:3]
    return sum(first)-min(first)-max(first)
'''

TIME = '''def minimum_time_for_small_sum(nums1,nums2,x):
    pairs=sorted(zip(nums2,nums1))
    n=len(nums1);best=[0]*(n+1)
    for growth,value in pairs:
        for count in range(n,0,-1):
            best[count]=max(best[count],best[count-1]+value+count*growth)
    base=sum(nums1);rate=sum(nums2)
    for elapsed in range(n+1):
        if base+elapsed*rate-best[elapsed]<=x:return elapsed
    return -1
'''

SAFEST = '''def maximum_safeness_factor(grid):
    from collections import deque
    import heapq
    n=len(grid);distance=[[-1]*n for _ in range(n)];queue=deque()
    for r in range(n):
        for c in range(n):
            if grid[r][c]:distance[r][c]=0;queue.append((r,c))
    while queue:
        r,c=queue.popleft()
        for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
            if 0<=nr<n and 0<=nc<n and distance[nr][nc]<0:
                distance[nr][nc]=distance[r][c]+1;queue.append((nr,nc))
    heap=[(-distance[0][0],0,0)];seen={(0,0)}
    while heap:
        safe,r,c=heapq.heappop(heap);safe=-safe
        if (r,c)==(n-1,n-1):return safe
        for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
            if 0<=nr<n and 0<=nc<n and (nr,nc) not in seen:
                seen.add((nr,nc));heapq.heappush(heap,(-min(safe,distance[nr][nc]),nr,nc))
'''

ELEGANCE = '''def maximum_subsequence_elegance(items,k):
    import heapq
    items=sorted(items,reverse=True);profit=0;seen=set();duplicates=[]
    for value,category in items[:k]:
        profit+=value
        if category in seen:heapq.heappush(duplicates,value)
        else:seen.add(category)
    answer=profit+len(seen)**2
    for value,category in items[k:]:
        if category not in seen and duplicates:
            profit+=value-heapq.heappop(duplicates);seen.add(category)
            answer=max(answer,profit+len(seen)**2)
    return answer
'''

SCORE = '''def maximum_prime_operation_score(nums,k):
    mod=1000000007
    def score(value):
        answer=0;factor=2
        while factor*factor<=value:
            if value%factor==0:
                answer+=1
                while value%factor==0:value//=factor
            factor+=1
        return answer+(value>1)
    scores=list(map(score,nums));n=len(nums);left=[-1]*n;right=[n]*n;stack=[]
    for i,value in enumerate(scores):
        while stack and scores[stack[-1]]<value:stack.pop()
        left[i]=stack[-1] if stack else -1;stack.append(i)
    stack=[]
    for i in range(n-1,-1,-1):
        while stack and scores[stack[-1]]<=scores[i]:stack.pop()
        right[i]=stack[-1] if stack else n;stack.append(i)
    answer=1
    for value,count in sorted(((nums[i],(i-left[i])*(right[i]-i)) for i in range(n)),reverse=True):
        use=min(k,count);answer=answer*pow(value,use,mod)%mod;k-=use
        if not k:break
    return answer
'''

BEAUTIFUL = '''def count_beautiful_integers(low,high,k):
    from functools import lru_cache
    def count(bound):
        digits=str(bound)
        @lru_cache(None)
        def solve(index,balance,remainder,tight,started):
            if index==len(digits):return int(started and balance==0 and remainder==0)
            total=0;limit=int(digits[index]) if tight else 9
            for digit in range(limit+1):
                next_started=started or digit!=0
                change=0 if not next_started else (1 if digit%2==0 else -1)
                total+=solve(index+1,balance+change,(remainder*10+digit)%k if next_started else 0,tight and digit==limit,next_started)
            return total
        return solve(0,0,0,True,False)
    return count(high)-count(low-1)
'''

SPLIT = '''def minimum_power_splits(nums,target):
    if sum(nums)<target:return -1
    counts=[0]*32
    for value in nums:counts[value.bit_length()-1]+=1
    operations=0
    for bit in range(31):
        if target>>bit&1:
            if counts[bit]:counts[bit]-=1
            else:
                higher=bit+1
                while higher<32 and not counts[higher]:higher+=1
                if higher==32:return -1
                while higher>bit:
                    counts[higher]-=1;counts[higher-1]+=2;operations+=1;higher-=1
                counts[bit]-=1
        counts[bit+1]+=counts[bit]//2
    return operations
'''

BEAUTY = '''def maximum_beauty_subsequence_count(s,k):
    from collections import Counter
    from math import comb
    mod=1000000007;counts=sorted(Counter(s).values(),reverse=True)
    if len(counts)<k:return 0
    cutoff=counts[k-1];above=sum(value>cutoff for value in counts);equal=counts.count(cutoff)
    answer=comb(equal,k-above)
    for value in counts[:above]:answer=answer*value%mod
    return answer*pow(cutoff,k-above,mod)%mod
'''

REVERSALS = '''def minimum_edge_reversals(n,edges):
    graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append((right,0));graph[right].append((left,1))
    answer=[0]*n
    def first(node,parent):
        for other,cost in graph[node]:
            if other!=parent:answer[0]+=cost;first(other,node)
    first(0,-1)
    def reroot(node,parent):
        for other,cost in graph[node]:
            if other!=parent:answer[other]=answer[node]+(1 if cost==0 else -1);reroot(other,node)
    reroot(0,-1);return answer
'''

PATHS = '''def count_one_prime_tree_paths(n,edges):
    graph=[[] for _ in range(n+1)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    prime=[True]*(n+1);prime[0]=prime[1]=False
    for value in range(2,int(n**.5)+1):
        if prime[value]:
            for multiple in range(value*value,n+1,value):prime[multiple]=False
    component=[0]*(n+1);sizes=[]
    for start in range(1,n+1):
        if prime[start] or component[start]:continue
        stack=[start];component[start]=len(sizes)+1;size=0
        while stack:
            node=stack.pop();size+=1
            for other in graph[node]:
                if not prime[other] and not component[other]:component[other]=component[start];stack.append(other)
        sizes.append(size)
    answer=0
    for node in range(1,n+1):
        if not prime[node]:continue
        total=0
        for other in graph[node]:
            if not prime[other]:
                size=sizes[component[other]-1];answer+=size+total*size;total+=size
    return answer
'''


CASES = {
2733: [[[3,2,1,4]],[[1,2]],[[2,1,3]],[[1]],[[9,2,7]],[[4,1,3,2]],[[5,4,3]],[[10,30,20]],[[1,100,50,75]],[[8,6,7,5]],[[2,9]],[[11,12,13]],[[99,1,2]],[[6,3,8,4,9]]],
2809: [[a,b,x] for a,b,x in [([1,2,3],[1,2,3],4),([1,2,3],[3,3,3],4),([0],[0],0),([5],[1],5),([5],[1],4),([1,1],[0,0],1),([10,1],[1,10],5),([0,0],[5,5],0),([4,2,7],[0,3,1],6),([9,8,7],[1,1,1],0),([1,10,1],[10,1,10],8),([2,4,6,8],[1,3,2,4],10),([0,5,0],[2,0,2],1),([3,1,4,1],[5,9,2,6],12)]],
2812: [[g] for g in [
 [[1,0,0],[0,0,0],[0,0,1]],[[0,0,1],[0,0,0],[0,0,0]],[[0,1],[0,0]],[[1,0],[0,0]],
 [[0,0],[0,1]],[[0,1,0],[0,0,0],[0,0,0]],[[0,0,0],[1,0,0],[0,0,0]],[[0,0,0],[0,1,0],[0,0,0]],
 [[0,0,0,1],[0,0,0,0],[0,0,0,0],[0,0,0,0]],[[0,1,0],[0,0,0],[1,0,0]],
 [[0,0,1],[0,1,0],[0,0,0]],[[0,0,0],[0,0,1],[0,0,0]],[[1,0],[0,1]],[[0,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,0,0]]]],
2813: [[i,k] for i,k in [([[3,2],[5,1],[10,1]],2),([[3,1],[3,1],[2,2],[5,3]],3),([[1,1]],1),([[5,1],[4,2]],1),([[5,1],[4,2]],2),([[10,1],[9,1],[1,2]],2),([[2,1],[2,2],[2,3]],2),([[8,3],[7,3],[6,2],[5,1]],3),([[1,1],[1,1],[1,1]],2),([[100,5],[1,1],[1,2]],2),([[4,1],[3,2],[2,2],[1,3]],3),([[9,1],[8,2],[7,3],[6,4]],2),([[6,1],[5,1],[4,2],[3,2]],3),([[2,9],[20,8],[3,9],[10,7],[5,6]],3)]],
2818: [[a,k] for a,k in [([8,3,9,3,8],2),([19,12,14,6,10,18],3),([2],1),([1],1),([2,3],2),([4,6,8],3),([5,5,5],4),([2,6,3],5),([10,15,21],2),([7,11,13],6),([1,2,1],3),([12,18,5,7],5),([30,2,3,5],4),([8,9,25,49,6],7)]],
2827: [[a,b,k] for a,b,k in [(10,20,3),(1,10,1),(5,5,2),(10,99,1),(100,200,7),(1,100,9),(12,12,3),(11,11,11),(20,30,2),(1000,1200,5),(1,999,13),(200,800,17),(98,102,2),(1234,2345,19)]],
2835: [[a,t] for a,t in [([1,2,8],7),([1,32,1,2],12),([1,32,1],35),([1],1),([2],1),([4],3),([1,1,1],2),([8,8],16),([16,1],9),([2,2,2],5),([32],17),([1,4,16],13),([8,2,2],6),([64,1,1,2],20)]],
2842: [[s,k] for s,k in [('bcca',2),('abbcd',4),('a',1),('a',2),('aaaa',1),('abc',2),('aabbcc',2),('aaabbc',2),('xyzxyz',3),('mississippi',3),('leetcode',4),('zzzyyxxw',2),('abababa',2),('abcdefg',7)]],
2858: [[n,e] for n,e in [(4,[[2,0],[2,1],[1,3]]),(3,[[1,2],[2,0]]),(2,[[0,1]]),(2,[[1,0]]),(5,[[0,1],[1,2],[2,3],[3,4]]),(5,[[1,0],[2,1],[3,2],[4,3]]),(4,[[0,1],[0,2],[0,3]]),(4,[[1,0],[2,0],[3,0]]),(6,[[0,1],[2,0],[2,3],[4,2],[4,5]]),(3,[[0,2],[1,2]]),(7,[[0,1],[2,0],[2,3],[3,4],[5,3],[5,6]]),(4,[[1,0],[1,2],[3,1]]),(5,[[0,2],[1,2],[2,3],[4,3]]),(6,[[1,0],[1,2],[3,2],[3,4],[5,4]])]],
2867: [[n,e] for n,e in [(5,[[1,2],[1,3],[2,4],[2,5]]),(6,[[1,2],[1,3],[2,4],[3,5],[3,6]]),(2,[[1,2]]),(3,[[1,2],[2,3]]),(4,[[1,2],[2,3],[3,4]]),(4,[[1,2],[1,3],[1,4]]),(5,[[1,2],[2,3],[3,4],[4,5]]),(6,[[1,4],[2,4],[3,4],[4,5],[5,6]]),(7,[[1,2],[2,3],[2,4],[4,5],[4,6],[6,7]]),(8,[[1,2],[1,3],[3,4],[3,5],[5,6],[5,7],[7,8]]),(3,[[1,3],[2,3]]),(5,[[1,5],[2,5],[3,5],[4,5]]),(6,[[1,6],[2,6],[3,6],[4,6],[5,6]]),(9,[[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9]])]],
}


BATCH = {
2733: entry('neither_minimum_nor_maximum',[('nums','list[int]')],'int',['arrays','sorting'],['nums has 1–100 distinct positive integers.','Return any element strictly between the minimum and maximum, or -1 when none exists.'],[([CASES[2733][0][0]],'Both two and three are valid; this implementation deterministically returns the middle of the first three values.'),([CASES[2733][1][0]],'Two values leave no element strictly between the extremes.')],CASES[2733][2:],MIDDLE,[MIDDLE.replace('nums[:3]','nums'),MIDDLE.replace('len(nums)<3','len(nums)<=3')],['Uses every array element in a three-value identity and returns an unrelated sum.','Rejects the valid length-three case.'],middle_oracle,random_middle,lesson('Any three distinct values contain one value between the other two.','Inspect only the first three values when available.','Return their sum minus their minimum and maximum.','The remaining value is neither the global minimum nor maximum because both a smaller and larger array value are present.'),'O(1)','O(1)',3),
2809: entry('minimum_time_for_small_sum',[('nums1','list[int]'),('nums2','list[int]'),('x','int')],'int',['dynamic programming','sorting'],['Arrays have equal length up to 1000 and nonnegative values.','Each second first adds nums2 everywhere, then permits one index to be reset to zero.','Return the first time with total at most x, or -1.'],[([*CASES[2809][0]],'Resetting indices in increasing growth-aware order reaches total four after three seconds.'),([*CASES[2809][1]],'Equal growth rates keep the total above four under every reset schedule.')],CASES[2809][2:],TIME,[TIME.replace('pairs=sorted','pairs=list'),TIME.replace('+count*growth','+(count-1)*growth')],['Processes reset choices without the growth-order exchange rule.','Credits each reset one second too early.'],time_oracle,random_time,lesson('For a fixed number of seconds, resets with larger growth should occur later.','Sort by nums2 and use knapsack DP for maximum removed contribution at every reset count.','dp[j]=max(dp[j],dp[j-1]+nums1+j*nums2); test baseline-dp[j].','An exchange argument orders selected growth rates, and the DP considers every selected subset in that order.'),'O(n²)','O(n)',8),
2812: entry('maximum_safeness_factor',[('grid','list[list[int]]')],'int',['graphs','breadth-first search','shortest paths'],['grid is n by n with at least one thief; movement is four-directional and may enter thief cells.','A path score is its minimum distance to any thief; maximize that score from top-left to bottom-right.'],[([CASES[2812][0][0]],'Both endpoints contain thieves, so every path has safeness zero.'),([CASES[2812][1][0]],'A route along the left and bottom edges stays at least distance two from the thief.')],CASES[2812][2:],SAFEST,[SAFEST.replace('min(safe,distance[nr][nc])','distance[nr][nc]'),SAFEST.replace('distance[r][c]+1','distance[r][c]')],['Uses only the destination cell distance instead of the minimum across the whole path.','Fails to increase distance layers away from thieves.'],safest_oracle,random_safest,lesson('First compute each cell’s nearest-thief distance with multi-source BFS.','Then run a widest-path search whose path value is the minimum cell distance seen.','Pop the currently safest frontier and push neighbors with min(path, neighbor distance).','The max-heap settles each cell at the largest possible bottleneck, exactly the safeness definition.'),'O(n² log n)','O(n²)',5),
2813: entry('maximum_subsequence_elegance',[('items','list[list[int]]'),('k','int')],'int',['greedy','sorting','heaps'],['Each item is [positive profit, category]; choose exactly k items.','Elegance is total profit plus the square of distinct category count.'],[([*CASES[2813][0]],'Choosing profits ten and three yields profit thirteen with two categories, for elegance seventeen.'),([*CASES[2813][1]],'The best three-item choice balances high profit with a third category.')],CASES[2813][2:],ELEGANCE,[ELEGANCE.replace('items=sorted(items,reverse=True)','items=sorted(items)'),ELEGANCE.replace('heapq.heappush(duplicates,value)','heapq.heappush(duplicates,-value)')],['Starts from the lowest-profit items.','Removes the largest duplicate profit instead of the smallest when adding a category.'],elegance_oracle,random_elegance,lesson('Start with maximum profit, then trade only duplicate-category items for new categories.','Sort by profit, keep duplicate profits in a min-heap, and scan unused new categories.','Replace the cheapest duplicate and update profit+distinct² after each replacement.','For each achievable category count, the greedy exchange retains the greatest possible profit, so the best recorded elegance is global.'),'O(n log n)','O(n)',8),
2818: entry('maximum_prime_operation_score',[('nums','list[int]'),('k','int')],'int',['monotonic stacks','greedy','number theory'],['Prime score counts distinct prime factors.','Each subarray selects its leftmost maximum-prime-score element; use at most k distinct subarrays.','Return the maximum product modulo 1,000,000,007.'],[([*CASES[2818][0]],'Two subarrays can select nine, producing eighty-one.'),([*CASES[2818][1]],'Prime-score dominance counts and descending values identify the best three multipliers.')],CASES[2818][2:],SCORE,[SCORE.replace('scores[stack[-1]]<value','scores[stack[-1]]<=value',1),SCORE.replace('sorted(((nums[i]','sorted(((1')],['Pops equal prime scores on the left and violates the smallest-index tie rule.','Ranks every selectable occurrence as value one instead of by its actual multiplier.'],score_oracle,random_score,lesson('Each index wins a rectangular set of subarrays bounded by greater-or-equal score on the left and strictly greater score on the right.','Use asymmetric monotonic stacks to count wins, then consume the largest numeric multipliers first.','Compute count=(i-left)*(right-i); sort (nums[i],count) descending and use up to k copies.','The boundaries encode the tie rule exactly, and choosing largest available factors maximizes a positive product.'),'O(n sqrt(max(nums))+n log n)','O(n)',8),
2827: entry('count_beautiful_integers',[('low','int'),('high','int'),('k','int')],'int',['digit dynamic programming','number theory'],['1 <= low <= high <= 1,000,000,000 and 1 <= k <= 20.','A beautiful integer has equal counts of even and odd digits and is divisible by k.'],[([*CASES[2827][0]],'Twelve and eighteen meet both conditions.'),([*CASES[2827][1]],'Ten is the only one-digit-range boundary result with balanced parity digits.')],CASES[2827][2:],BEAUTIFUL,[BEAUTIFUL.replace("change=0 if not next_started else (1 if digit%2==0 else -1)","change=0"),BEAUTIFUL.replace('and remainder==0','')],['Ignores the required equality between even- and odd-digit counts.','Counts parity-balanced values without requiring divisibility.'],beautiful_oracle,random_beautiful,lesson('Count qualifying values up to a bound, then subtract the prefix below low.','Digit DP tracks position, even-minus-odd balance, remainder, tightness, and whether a nonleading digit started.','Try each allowed next digit and accept started states with balance and remainder zero.','Those states retain exactly the information future digits need, so every bounded integer is counted once.'),'O(digits²*k*digits*10)','O(digits²*k)',8),
2835: entry('minimum_power_splits',[('nums','list[int]'),('target','int')],'int',['greedy','bit manipulation'],['Every nums value is a positive power of two.','One operation replaces 2^b by two copies of 2^(b-1); form target from a subsequence.'],[([*CASES[2835][0]],'Split eight once into two fours, then one, two, and four sum to seven.'),([*CASES[2835][1]],'Splitting thirty-two down twice supplies the missing eight needed for twelve.')],CASES[2835][2:],SPLIT,[SPLIT.replace('counts[bit+1]+=counts[bit]//2','pass'),SPLIT.replace('operations+=1','operations+=2')],['Never combines spare lower powers to satisfy higher target bits.','Charges two operations for every one-level split.'],split_oracle,random_split,lesson('Process target bits low to high because excess small powers can combine freely, while a missing bit requires splitting the nearest larger power.','Count powers by exponent and greedily satisfy each target bit.','Borrow the first higher count, split downward one level at a time, then carry unused pairs upward.','Borrowing any farther power costs more, and lower decisions cannot benefit from postponing an available exact bit.'),'O(log maximum value)','O(log maximum value)',8),
2842: entry('maximum_beauty_subsequence_count',[('s','str'),('k','int')],'int',['combinatorics','hash maps','sorting'],['s contains lowercase letters; selected subsequence characters must be distinct.','Beauty is the sum of whole-string frequencies of selected characters.','Count maximum-beauty index subsequences modulo 1,000,000,007.'],[([*CASES[2842][0]],'The two highest-frequency character choices and their occurrence choices determine the answer.'),([*CASES[2842][1]],'Four distinct characters must be chosen, so all available character classes contribute.')],CASES[2842][2:],BEAUTY,[BEAUTY.replace('comb(equal,k-above)','equal'),BEAUTY.replace('pow(cutoff,k-above,mod)','cutoff')],['Uses the number of cutoff-frequency characters instead of choosing the required number of them.','Counts only one cutoff character occurrence even when several cutoff classes are selected.'],beauty_oracle,random_beauty,lesson('Maximum beauty chooses the k greatest character frequencies; only ties at the cutoff create alternative character sets.','Multiply occurrence choices for forced frequencies and combine tied cutoff classes.','answer=C(equal,needed)*product(forced frequencies)*cutoff^needed.','Every optimal character set contains all frequencies above the cutoff and exactly needed tied classes; occurrence choices multiply independently.'),'O(n+alphabet log alphabet)','O(alphabet)',8),
2858: entry('minimum_edge_reversals',[('n','int'),('edges','list[list[int]]')],'list[int]',['trees','rerooting','depth-first search'],['Ignoring directions, edges form a tree on nodes 0 through n-1.','answer[i] is the reversals needed to make every node reachable from i.'],[([*CASES[2858][0]],'Rooting at each node gives reversal counts one, one, zero, and two.'),([*CASES[2858][1]],'The directed chain already points outward only from node one after one reroot adjustment.')],CASES[2858][2:],REVERSALS,[REVERSALS.replace('(right,0)','(right,1)',1),REVERSALS.replace("+(1 if cost==0 else -1)","+(1 if cost==1 else -1)")],['Assigns the forward direction a reversal cost of one from the initial root.','Uses the reroot delta in the opposite direction.'],reversals_oracle,random_reversals,lesson('After computing one root, moving the root across one edge changes only that edge’s required direction.','Store each undirected adjacency with whether traversal needs reversal; DFS once from zero, then reroot.','answer[child]=answer[parent]+1 for an originally parent-to-child edge, otherwise -1.','All other edges keep their parent-child orientation, so this single-edge delta produces every root’s optimum.'),'O(n)','O(n)',8),
2867: entry('count_one_prime_tree_paths',[('n','int'),('edges','list[list[int]]')],'int',['trees','number theory','connected components'],['Nodes are labeled 1 through n and edges form an undirected tree.','Count unordered endpoint pairs whose complete path contains exactly one prime-labeled node.'],[([*CASES[2867][0]],'The four qualifying endpoint pairs each pass through exactly one of nodes two or three.'),([*CASES[2867][1]],'Nonprime components adjacent to each prime determine all valid cross-component pairs.')],CASES[2867][2:],PATHS,[PATHS.replace('answer+=size+total*size','answer+=total*size'),PATHS.replace('if not prime[other]','if prime[other]',1)],['Counts only paths crossing two nonprime components and omits paths ending at the prime.','Builds components from prime neighbors instead of nonprime regions.'],valid_paths_oracle,random_paths,lesson('Removing prime nodes splits the tree into nonprime components; a valid path chooses one prime and endpoints in at most two adjacent components or at the prime.','Label nonprime components and accumulate their sizes around each prime.','For each adjacent size, add size for prime-to-component paths and size*previous_total for cross-component paths.','Any path with exactly one prime decomposes uniquely this way, and combining two different adjacent components cannot introduce another prime.'),'O(n log log n)','O(n)',8),
}
