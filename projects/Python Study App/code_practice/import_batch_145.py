"""Heap, dynamic-programming, tree, and LCM workbook batch 145."""

from collections import deque
from math import gcd
from .import_batch_055 import entry


def hiring_oracle(args):
    costs, k, candidates = args
    remaining = list(range(len(costs)))
    total = 0
    for _ in range(k):
        eligible = (
            remaining[:candidates]
            + remaining[max(candidates, len(remaining) - candidates) :]
        )
        chosen = min(set(eligible), key=lambda index: (costs[index], index))
        total += costs[chosen]
        remaining.remove(chosen)
    return total


def random_hiring(rng):
    n = rng.randint(1, 25)
    return [
        [rng.randint(1, 50) for _ in range(n)],
        rng.randint(1, n),
        rng.randint(1, n),
    ]


def split_oracle(args):
    nums = args[0]
    best = [10**9] * (len(nums) + 1)
    best[0] = 0
    for end in range(1, len(nums) + 1):
        for start in range(end):
            if gcd(nums[start], nums[end - 1]) > 1:
                best[end] = min(best[end], best[start] + 1)
    return best[-1] if best[-1] < 10**9 else -1


def random_split(rng):
    return [[rng.randint(1, 40) for _ in range(rng.randint(1, 22))]]


def strings_oracle(args):
    low, high, zero, one = args
    queue = deque([0])
    count = 0
    mod = 10**9 + 7
    while queue:
        length = queue.popleft()
        if low <= length <= high:
            count += 1
        if length + zero <= high:
            queue.append(length + zero)
        if length + one <= high:
            queue.append(length + one)
    return count % mod


def random_strings(rng):
    high = rng.randint(1, 14)
    return [rng.randint(1, high), high, rng.randint(1, 5), rng.randint(1, 5)]


def profit_oracle(args):
    edges, bob, amount = args
    n = len(amount)
    graph = [[] for _ in range(n)]
    for left, right in edges:
        graph[left].append(right)
        graph[right].append(left)
    parent = [-1] * n
    depth = [0] * n
    queue = deque([0])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor != parent[node]:
                parent[neighbor] = node
                depth[neighbor] = depth[node] + 1
                queue.append(neighbor)
    bob_time = {}
    time = 0
    while bob != -1:
        bob_time[bob] = time
        bob = parent[bob]
        time += 1
    best = -(10**30)
    stack = [(0, -1, 0)]
    while stack:
        node, previous, total = stack.pop()
        arrival = depth[node]
        total += (
            amount[node]
            if arrival < bob_time.get(node, 10**9)
            else amount[node] // 2 if arrival == bob_time.get(node) else 0
        )
        children = [x for x in graph[node] if x != previous]
        if not children:
            best = max(best, total)
        for child in children:
            stack.append((child, node, total))
    return best


def random_profit(rng):
    n = rng.randint(2, 20)
    edges = [[node, rng.randrange(node)] for node in range(1, n)]
    return [edges, rng.randint(1, n - 1), [2 * rng.randint(-15, 15) for _ in range(n)]]


def lcm_oracle(args):
    nums, k = args
    answer = 0
    for left in range(len(nums)):
        common = 1
        for right in range(left, len(nums)):
            common = common * nums[right] // gcd(common, nums[right])
            answer += common == k
    return answer


def random_lcm(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(1, 18))], rng.randint(1, 30)]


HIRING = """\
def total_worker_hiring_cost(costs,k,candidates):
    import heapq
    left=[];right=[];i=0;j=len(costs)-1
    while i<=j and len(left)<candidates:heapq.heappush(left,(costs[i],i));i+=1
    while i<=j and len(right)<candidates:heapq.heappush(right,(costs[j],j));j-=1
    total=0
    for _ in range(k):
        if not right or left and left[0]<=right[0]:
            cost,index=heapq.heappop(left)
            if i<=j:heapq.heappush(left,(costs[i],i));i+=1
        else:
            cost,index=heapq.heappop(right)
            if i<=j:heapq.heappush(right,(costs[j],j));j-=1
        total+=cost
    return total
"""
SPLIT = """\
def minimum_valid_endpoint_splits(nums):
    from math import gcd
    dp=[10**9]*(len(nums)+1);dp[0]=0
    for start in range(len(nums)):
        if dp[start]==10**9:continue
        for end in range(start,len(nums)):
            if gcd(nums[start],nums[end])>1:dp[end+1]=min(dp[end+1],dp[start]+1)
    return dp[-1] if dp[-1]<10**9 else -1
"""
STRINGS = """\
def count_good_length_strings(low,high,zero,one):
    mod=10**9+7;ways=[0]*(high+1);ways[0]=1;answer=0
    for length in range(high+1):
        if length>=low:answer=(answer+ways[length])%mod
        if length+zero<=high:ways[length+zero]=(ways[length+zero]+ways[length])%mod
        if length+one<=high:ways[length+one]=(ways[length+one]+ways[length])%mod
    return answer
"""
PROFIT = """\
def most_profitable_tree_path(edges,bob,amount):
    graph=[[] for _ in amount]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    parent=[-1]*len(amount);depth=[0]*len(amount);stack=[0]
    for node in stack:
        for neighbor in graph[node]:
            if neighbor!=parent[node]:parent[neighbor]=node;depth[neighbor]=depth[node]+1;stack.append(neighbor)
    bob_time=[10**9]*len(amount);time=0
    while bob!=-1:bob_time[bob]=time;time+=1;bob=parent[bob]
    answer=-10**30;stack=[(0,-1,0)]
    while stack:
        node,previous,total=stack.pop()
        if depth[node]<bob_time[node]:total+=amount[node]
        elif depth[node]==bob_time[node]:total+=amount[node]//2
        children=[neighbor for neighbor in graph[node] if neighbor!=previous]
        if not children:answer=max(answer,total)
        for child in children:stack.append((child,node,total))
    return answer
"""
LCM = """\
def count_subarrays_with_lcm(nums,k):
    from math import gcd
    previous={};answer=0
    for value in nums:
        current={value:1}
        for common,count in previous.items():
            merged=common*value//gcd(common,value)
            if merged<=k and k%merged==0:current[merged]=current.get(merged,0)+count
        answer+=current.get(k,0);previous=current
    return answer
"""

BATCH = {
    2462: entry(
        "total_worker_hiring_cost",
        [("costs", "list[int]"), ("k", "int"), ("candidates", "int")],
        "int",
        ["heaps", "two pointers", "simulation"],
        [
            "Hire exactly k workers in k sessions.",
            "At each session, candidates are the first and last candidates unhired workers; choose minimum cost, then smallest original index on a tie.",
            "Return the sum of hired costs.",
        ],
        [
            (
                [[17, 12, 10, 2, 7, 2, 11, 20, 8], 3, 4],
                "The eligible choices lead to costs 2, 2, and 7, totaling eleven.",
            ),
            (
                [[1, 2, 4, 1], 3, 3],
                "All remaining workers are eligible each round; costs 1, 1, and 2 total four.",
            ),
        ],
        [
            [a, k, c]
            for a, k, c in [
                ([5], 1, 1),
                ([5, 1], 1, 1),
                ([5, 1], 2, 1),
                ([3, 2, 1], 2, 1),
                ([1, 2, 3], 2, 1),
                ([2, 1, 2, 2], 2, 1),
                ([9, 1, 8, 2], 2, 1),
                ([9, 1, 8, 2], 3, 2),
                ([5, 3, 4, 2, 1], 4, 2),
                ([1, 100, 2, 99], 2, 1),
                ([7, 6, 5, 4, 3, 2], 3, 2),
                ([2, 1, 1, 2], 2, 1),
                ([10, 9, 8, 1], 3, 3),
                ([8, 2, 6, 4, 5], 5, 2),
            ]
        ],
        HIRING,
        [
            HIRING.replace("left[0]<=right[0]", "left[0][0]<right[0][0]"),
            HIRING.replace("costs[j],j", "costs[i],i"),
        ],
        [
            "Breaks equal-cost side ties toward the larger right-side index.",
            "Refills the right heap from the left pointer instead of the right pointer.",
        ],
        hiring_oracle,
        random_hiring,
        [
            "Maintain min-heaps for the currently eligible left and right candidate pools.",
            "Compare heap tops by (cost,index), which implements both priorities.",
            "After hiring from one side, expose the next worker from that same side if any unexposed workers remain.",
            "The heaps contain exactly the legal candidates each round, so choosing their global minimum reproduces every required session.",
        ],
        "O((k+c) log c)",
        "O(c)",
        6,
    ),
    2464: entry(
        "minimum_valid_endpoint_splits",
        [("nums", "list[int]")],
        "int",
        ["dynamic programming", "number theory"],
        [
            "Partition the full array into contiguous nonempty subarrays.",
            "A group is valid when the GCD of its first and last values is greater than one; interior values do not affect validity.",
            "Return the fewest groups, or -1 when no complete split exists.",
        ],
        [
            (
                [[2, 6, 3, 4, 3]],
                "Split as [2,6,3,4] and [3]; endpoint GCDs are two and three, so two groups suffice.",
            ),
            (
                [[1, 2, 1]],
                "Every possible first group begins with 1 and has endpoint GCD one, so no valid split exists.",
            ),
        ],
        [
            [x]
            for x in [
                [2],
                [1],
                [2, 3],
                [2, 4],
                [2, 3, 4],
                [6, 5, 10],
                [3, 2, 6, 5],
                [7, 11, 13],
                [4, 9, 6, 8],
                [2, 1, 2],
                [15, 2, 3, 10],
                [6, 7, 5, 9],
                [10, 3, 5, 7, 14],
                [8, 3, 9, 2, 4],
            ]
        ],
        SPLIT,
        [
            SPLIT.replace(
                "gcd(nums[start],nums[end])>1", "gcd(nums[start],nums[end])>=1"
            ),
            SPLIT.replace("dp[start]+1", "dp[start]"),
        ],
        [
            "Treats every endpoint pair as valid, including GCD one.",
            "Does not charge a group for each chosen subarray.",
        ],
        split_oracle,
        random_split,
        [
            "Let dp[i] be the minimum valid groups covering the first i elements.",
            "From every reachable start, try each possible group end.",
            "When the two endpoint values have GCD above one, relax dp[end+1] by one group.",
            "Every partition has a unique sequence of endpoints, all of which are examined, so the minimum relaxation is exact.",
        ],
        "O(n^2 log V)",
        "O(n)",
        5,
    ),
    2466: entry(
        "count_good_length_strings",
        [("low", "int"), ("high", "int"), ("zero", "int"), ("one", "int")],
        "int",
        ["dynamic programming"],
        [
            "Start from the empty string.",
            "One operation appends zero copies of character 0 or one copies of character 1.",
            "Count construction sequences whose final length is between low and high inclusive, modulo 1,000,000,007.",
        ],
        [
            (
                [3, 3, 1, 1],
                "All eight binary strings of length three can be constructed, so the answer is eight.",
            ),
            (
                [2, 3, 1, 2],
                "The valid constructions have lengths two or three; counting their distinct append sequences gives five.",
            ),
        ],
        [
            [a, b, z, o]
            for a, b, z, o in [
                (1, 1, 1, 1),
                (1, 2, 1, 1),
                (2, 2, 2, 3),
                (1, 3, 2, 2),
                (3, 5, 2, 3),
                (5, 5, 1, 5),
                (1, 10, 3, 4),
                (4, 8, 2, 2),
                (2, 7, 1, 3),
                (6, 9, 4, 5),
                (10, 12, 2, 3),
                (1, 4, 5, 1),
                (7, 14, 3, 5),
                (20, 25, 4, 6),
            ]
        ],
        STRINGS,
        [
            STRINGS.replace("length>=low", "length>low"),
            STRINGS.replace("ways[0]=1", "ways[0]=0"),
        ],
        [
            "Excludes valid strings whose length equals the lower bound.",
            "Loses the empty construction seed, making every count zero.",
        ],
        strings_oracle,
        random_strings,
        [
            "Store the number of construction sequences reaching each length.",
            "Seed length zero with one empty construction.",
            "Propagate each count to length+zero and length+one, and add counts at all lengths in the inclusive target range.",
            "Every construction has a unique final append operation, so the two transitions count all sequences without overlap.",
        ],
        "O(high)",
        "O(high)",
        5,
    ),
    2467: entry(
        "most_profitable_tree_path",
        [("edges", "list[list[int]]"), ("bob", "int"), ("amount", "list[int]")],
        "int",
        ["trees", "graphs", "depth-first search"],
        [
            "The undirected tree is rooted at 0; Alice starts at 0 and chooses a root-to-leaf path while Bob starts at bob and follows the unique path to 0.",
            "At a node Alice receives the full even amount if she arrives before Bob, half if simultaneous, and zero if Bob arrived first; negative amounts are costs.",
            "Return Alice’s maximum total over all root-to-leaf paths.",
        ],
        [
            (
                [[[0, 1], [1, 2], [1, 3], [3, 4]], 3, [-2, 4, 2, -4, 6]],
                "Alice’s best path reaches node 4; applying Bob’s arrival times yields total six.",
            ),
            (
                [[[0, 1]], 1, [-7280, 2350]],
                "Alice opens the root before Bob arrives and pays 7280; Bob already opened node 1, so her total is -7280.",
            ),
        ],
        [
            [e, b, a]
            for e, b, a in [
                ([[0, 1]], 1, [2, 4]),
                ([[0, 1], [0, 2]], 1, [0, 10, 20]),
                ([[0, 1], [1, 2]], 2, [6, 4, 2]),
                ([[0, 1], [1, 2], [1, 3]], 2, [2, -4, 8, 6]),
                ([[0, 1], [0, 2], [2, 3]], 3, [-2, 4, 6, 8]),
                ([[0, 1], [1, 2], [2, 3]], 1, [4, 2, 2, 10]),
                ([[0, 1], [0, 2], [1, 3], [1, 4]], 4, [2, 4, 6, 8, 10]),
                ([[0, 1], [1, 2], [2, 3], [3, 4]], 4, [10, -2, -4, 8, 6]),
                ([[0, 1], [0, 2], [2, 3], [2, 4]], 3, [0, 2, -6, 12, 4]),
                ([[0, 1], [1, 2], [0, 3], [3, 4]], 2, [2, 10, 4, 6, 8]),
                ([[0, 1], [1, 2], [1, 3], [3, 4]], 2, [-2, -4, -6, -8, -10]),
                ([[0, 1], [0, 2], [0, 3]], 2, [8, 2, 4, 6]),
                ([[0, 1], [1, 2], [2, 3], [1, 4]], 3, [2, 2, 2, 2, 20]),
                ([[0, 1], [0, 2], [1, 3], [2, 4], [4, 5]], 5, [4, -2, 8, 6, -4, 10]),
            ]
        ],
        PROFIT,
        [
            PROFIT.replace("depth[node]<bob_time[node]", "depth[node]<=bob_time[node]"),
            PROFIT.replace("amount[node]//2", "0"),
        ],
        [
            "Awards the full amount rather than half when Alice and Bob arrive together.",
            "Awards zero instead of half at simultaneous arrivals.",
        ],
        profit_oracle,
        random_profit,
        [
            "Root the tree to compute each node’s parent and Alice arrival depth.",
            "Walk Bob through parent links and record his arrival time on that path.",
            "Traverse every Alice root-to-leaf path, adding full, half, or zero according to arrival comparison.",
            "Both paths in a tree are unique, so recorded times are exact; maximizing totals at leaves examines every legal Alice choice.",
        ],
        "O(n)",
        "O(n)",
        6,
    ),
    2470: entry(
        "count_subarrays_with_lcm",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "dynamic programming", "number theory"],
        [
            "A subarray is a nonempty contiguous segment.",
            "Compute the least common multiple of its elements.",
            "Return the number of subarrays whose LCM is exactly k.",
        ],
        [
            (
                [[3, 6, 2, 7, 1], 6],
                "The qualifying segments are [3,6], [3,6,2], [6], and [6,2], giving four.",
            ),
            (
                [[2, 3, 4], 12],
                "Only the complete subarray has LCM twelve, so the answer is one.",
            ),
        ],
        [
            [a, k]
            for a, k in [
                ([1], 1),
                ([2], 1),
                ([2], 2),
                ([2, 4], 4),
                ([2, 3], 6),
                ([2, 3, 6], 6),
                ([1, 1, 1], 1),
                ([4, 8, 16], 8),
                ([3, 6, 9], 18),
                ([5, 10, 2], 10),
                ([2, 5, 7], 10),
                ([6, 6, 6], 6),
                ([1, 2, 4, 8], 8),
                ([12, 3, 4, 6], 12),
            ]
        ],
        LCM,
        [
            LCM.replace("current={value:1}", "current={}"),
            LCM.replace("current.get(k,0)", "current.get(k+1,0)"),
        ],
        ["Omits all single-element subarrays.", "Counts LCM k+1 instead of exactly k."],
        lcm_oracle,
        random_lcm,
        [
            "Track counts of distinct LCM values among subarrays ending at the previous index.",
            "Start the singleton at the current value, then append the value to every prior ending subarray and merge equal LCM states.",
            "Discard merged values that cannot divide k, and add the count at k.",
            "Every ending subarray is uniquely generated, while LCM can only stay or increase, making discarded non-divisors unable to recover to k.",
        ],
        "O(n*t log V)",
        "O(t)",
        5,
    ),
}
