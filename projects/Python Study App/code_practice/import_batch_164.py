"""Tree pruning, interval coverage, Kadane, and cycle-median batch 164."""

from collections import deque
from itertools import combinations_with_replacement
from math import gcd

from .import_batch_055 import entry


def coins_oracle(args):
    coins, edges = args
    n = len(coins)
    graph = [[] for _ in range(n)]
    for left, right in edges:
        graph[left].append(right)
        graph[right].append(left)
    cover = []
    for start in range(n):
        seen = {start}
        queue = deque([(start, 0)])
        mask = 0
        while queue:
            node, distance = queue.popleft()
            if coins[node]:
                mask |= 1 << node
            if distance < 2:
                for neighbor in graph[node]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        queue.append((neighbor, distance + 1))
        cover.append(mask)
    target = sum((1 << i) for i, coin in enumerate(coins) if coin)
    if not target:
        return 0
    best = 10**9
    for start in range(n):
        queue = deque([(start, cover[start], 0)])
        seen = {(start, cover[start])}
        while queue:
            node, mask, distance = queue.popleft()
            if node == start and mask & target == target:
                best = min(best, distance)
                break
            for neighbor in graph[node]:
                state = (neighbor, mask | cover[neighbor])
                if state not in seen:
                    seen.add(state)
                    queue.append((neighbor, state[1], distance + 1))
    return best


def random_coins(rng):
    n = rng.randint(1, 8)
    edges = [[node, rng.randrange(node)] for node in range(1, n)]
    return [[rng.randint(0, 1) for _ in range(n)], edges]


def grains_oracle(args):
    hens, grains = map(sorted, args)
    best = 10**9
    # In an optimal line assignment, each hen receives a contiguous (possibly empty) grain block.
    for cuts in combinations_with_replacement(range(len(grains) + 1), len(hens) - 1):
        bounds = (0,) + cuts + (len(grains),)
        worst = 0
        for index, hen in enumerate(hens):
            block = grains[bounds[index] : bounds[index + 1]]
            if block:
                left, right = block[0], block[-1]
                worst = max(worst, right - left + min(abs(hen - left), abs(hen - right)))
        best = min(best, worst)
    return best


def random_grains(rng):
    hens = rng.sample(range(0, 31), rng.randint(1, 4))
    grains = rng.sample(range(0, 31), rng.randint(1, 7))
    return [hens, grains]


def digits_oracle(args):
    first, second = map(set, args)
    for number in range(1, 100):
        digits = {int(char) for char in str(number)}
        if digits & first and digits & second:
            return number
    raise AssertionError("digit sets are non-empty")


def random_digits(rng):
    digits = list(range(1, 10))
    rng.shuffle(digits)
    split = rng.randint(1, 8)
    first = digits[:split]
    rng.shuffle(digits)
    second = digits[: rng.randint(1, 8)]
    return [first, second]


def substring_oracle(args):
    s, chars, vals = args
    values = dict(zip(chars, vals))
    costs = [values.get(char, ord(char) - 96) for char in s]
    return max([0] + [sum(costs[left:right]) for left in range(len(s)) for right in range(left + 1, len(s) + 1)])


def random_substring(rng):
    alphabet = "abcdefghi"
    s = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 18)))
    chars = "".join(rng.sample(list(alphabet), rng.randint(0, 6)))
    return [s, chars, [rng.randint(-20, 20) for _ in chars]]


def circular_oracle(args):
    arr, k = args
    n = len(arr)
    step = gcd(n, k)
    total = 0
    for start in range(step):
        group = arr[start:n:step]
        total += min(sum(abs(value - target) for value in group) for target in range(min(group), max(group) + 1))
    return total


def random_circular(rng):
    n = rng.randint(1, 12)
    return [[rng.randint(1, 30) for _ in range(n)], rng.randint(1, n)]


COINS = """\
def minimum_coin_collection_walk(coins,edges):
    from collections import deque
    n=len(coins);graph=[set() for _ in range(n)]
    for left,right in edges:graph[left].add(right);graph[right].add(left)
    leaves=deque(i for i in range(n) if len(graph[i])==1 and coins[i]==0)
    while leaves:
        node=leaves.popleft()
        for neighbor in list(graph[node]):
            graph[neighbor].remove(node)
            if len(graph[neighbor])==1 and coins[neighbor]==0:leaves.append(neighbor)
        graph[node].clear()
    for _ in range(2):
        leaves=[i for i in range(n) if len(graph[i])==1]
        for node in leaves:
            for neighbor in list(graph[node]):graph[neighbor].remove(node)
            graph[node].clear()
    return sum(len(neighbors) for neighbors in graph)
"""

GRAINS = """\
def minimum_grain_collection_time(hens,grains):
    hens=sorted(hens);grains=sorted(grains)
    def possible(time):
        grain=0
        for hen in hens:
            if grain==len(grains):return True
            left=grains[grain]
            if left<hen-time:return False
            if left<=hen:
                reach=max(hen+(time-(hen-left))//2,hen+time-2*(hen-left))
            else:reach=hen+time
            while grain<len(grains) and grains[grain]<=reach:grain+=1
        return grain==len(grains)
    low=0;high=max(abs(hen-grain) for hen in hens for grain in grains)+grains[-1]-grains[0]
    while low<high:
        middle=(low+high)//2
        if possible(middle):high=middle
        else:low=middle+1
    return low
"""

DIGITS = """\
def smallest_number_from_digit_sets(nums1,nums2):
    shared=set(nums1)&set(nums2)
    if shared:return min(shared)
    first=min(nums1);second=min(nums2)
    return min(first*10+second,second*10+first)
"""

SUBSTRING = """\
def maximum_custom_substring_cost(s,chars,vals):
    custom=dict(zip(chars,vals));best=current=0
    for char in s:
        value=custom.get(char,ord(char)-ord('a')+1)
        current=max(0,current+value);best=max(best,current)
    return best
"""

CIRCULAR = """\
def minimum_equal_circular_sums_cost(arr,k):
    import math
    groups=math.gcd(len(arr),k);answer=0
    for start in range(groups):
        values=sorted(arr[start::groups]);median=values[len(values)//2]
        answer+=sum(abs(value-median) for value in values)
    return answer
"""


BATCH = {
    2603: entry(
        "minimum_coin_collection_walk", [("coins", "list[int]"), ("edges", "list[list[int]]")], "int",
        ["trees", "graphs", "queues", "topological sorting"],
        [
            "The inputs describe an undirected tree; coins[i] tells whether node i has a coin.",
            "From a node you collect every coin within distance two, or you may traverse an adjacent edge.",
            "Return the fewest edge traversals needed to collect every coin and finish where you started.",
        ],
        [
            ([[1, 0, 0, 0, 0, 1], [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]], "Starting at node two, walk once to node three and back; the two endpoint coins are within distance two."),
            ([[0, 0, 1, 0, 1, 0, 0, 1], [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [5, 6], [5, 7]]], "After irrelevant leaves and two free collection layers are removed, two core edges must each be crossed twice."),
        ],
        [
            [[0], []], [[1], []], [[1, 1], [[0, 1]]], [[1, 0, 1], [[0, 1], [1, 2]]],
            [[1, 0, 0, 1], [[0, 1], [1, 2], [2, 3]]], [[1, 0, 0, 0, 1], [[0, 1], [1, 2], [2, 3], [3, 4]]],
            [[1, 0, 0, 0, 0, 1], [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]]],
            [[0, 1, 0, 0, 1], [[0, 1], [1, 2], [1, 3], [3, 4]]],
            [[1, 0, 1, 0, 1], [[0, 1], [1, 2], [2, 3], [3, 4]]],
            [[0, 0, 0, 0], [[0, 1], [1, 2], [2, 3]]],
            [[1, 1, 1, 1], [[0, 1], [1, 2], [2, 3]]],
            [[1, 0, 0, 0, 0, 0, 1], [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]],
            [[0, 1, 0, 1, 0, 1], [[0, 1], [0, 2], [2, 3], [2, 4], [4, 5]]],
            [[1, 0, 1, 0, 0, 1, 0], [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]]],
        ],
        COINS,
        [COINS.replace("range(2)", "range(1)"), COINS.replace("coins[i]==0", "coins[i]==1")],
        ["Removes only one of the two layers whose coins can be collected without entering them.", "Prunes coin-bearing leaves as though they were irrelevant empty leaves."],
        coins_oracle, random_coins,
        [
            "First remove empty leaves: walking into them can never help collect a coin.",
            "After that pruning, every remaining leaf has a coin.",
            "Remove exactly two more leaf layers because their coins are collectable from two edges away.",
            "Every surviving edge lies in the necessary core and must be traversed in both directions to return to the start.",
        ],
        "O(n)", "O(n)", 8,
    ),
    2604: entry(
        "minimum_grain_collection_time", [("hens", "list[int]"), ("grains", "list[int]")], "int",
        ["arrays", "binary search", "sorting", "two pointers"],
        [
            "Hens and grains occupy positions on a line; every hen moves at most one unit per second.",
            "Hens move simultaneously and a hen eats every grain position it visits.",
            "Return the minimum time needed to eat all grains.",
        ],
        [
            ([[3, 6, 7], [2, 4, 7, 9]], "In two seconds the hens can cover the nearby grain groups simultaneously."),
            ([[4], [1, 7]], "The single hen must cover both endpoints, taking six seconds by visiting one side and then the other."),
        ],
        [[h, g] for h, g in [
            ([0], [0]), ([0], [5]), ([5], [0]), ([2], [1, 3]), ([10], [1, 2, 3]),
            ([1, 9], [2, 8]), ([5, 15], [0, 10, 20]), ([0, 10], [4, 5, 6]),
            ([3, 8, 12], [1, 4, 7, 13]), ([2, 20], [1, 3, 4, 19, 25]),
            ([7, 1], [6, 2, 10]), ([0, 30], [10, 11, 12, 20]),
            ([4, 14, 24], [0, 8, 16, 28]), ([5, 6, 7], [0, 20]),
        ]],
        GRAINS,
        [GRAINS.replace("max(hen+(time-(hen-left))//2,hen+time-2*(hen-left))", "hen+time-2*(hen-left)"), GRAINS.replace("left<hen-time", "left<=hen-time")],
        ["Considers only the route that visits the left side before going right.", "Rejects a leftmost grain reachable at exactly the time limit."],
        grains_oracle, random_grains,
        [
            "Sort both position arrays and binary-search the answer time.",
            "For a candidate time, assign grains from left to right to hens from left to right.",
            "When grains lie left of a hen, compare going left first with going right first to find its farthest reachable right position.",
            "Greedily consuming the longest prefix is safe on a line; feasibility is monotone, so binary search finds the minimum time.",
        ],
        "O((h + g) log R)", "O(h + g)", 8,
    ),
    2605: entry(
        "smallest_number_from_digit_sets", [("nums1", "list[int]"), ("nums2", "list[int]")], "int",
        ["arrays", "hash maps", "greedy"],
        [
            "Each input contains distinct digits from one through nine.",
            "Form the smallest positive integer containing a digit from each input; one shared digit may satisfy both.",
            "Return that integer.",
        ],
        [
            ([[4, 1, 3], [5, 7]], "There is no shared digit, and arranging the smallest choices as 15 is optimal."),
            ([[3, 5, 2, 6], [3, 1, 7]], "The shared digit three forms the one-digit answer three."),
        ],
        [[a, b] for a, b in [
            ([1], [1]), ([1], [2]), ([9], [8]), ([2, 7], [3, 8]), ([8, 4], [4, 9]),
            ([9, 1], [8, 2]), ([5, 6, 7], [1, 2, 3]), ([3, 1, 9], [7, 3]),
            ([2, 4, 6, 8], [1, 3, 5, 7, 9]), ([7, 8, 9], [6, 7]),
            ([1, 4, 8], [2, 4, 9]), ([6, 2], [5, 3]), ([9, 5, 1], [8, 6, 2]),
            ([4, 7], [1, 9]),
        ]],
        DIGITS,
        [DIGITS.replace("if shared:return min(shared)", "if shared:return min(nums1)"), DIGITS.replace("min(first*10+second,second*10+first)", "first*10+second")],
        ["Returns the first set's minimum even when that digit is not shared.", "Always places the first array's digit in the tens place."],
        digits_oracle, random_digits,
        [
            "Check whether the two sets share a digit.",
            "If so, the smallest shared digit is a one-digit answer and beats every two-digit answer.",
            "Otherwise take the minimum digit from each set and try both two-digit orders.",
            "No larger chosen digit can improve either place, so the smaller ordering of the two minima is globally optimal.",
        ],
        "O(n + m)", "O(n + m)", 3,
    ),
    2606: entry(
        "maximum_custom_substring_cost", [("s", "str"), ("chars", "str"), ("vals", "list[int]")], "int",
        ["strings", "hash maps", "dynamic programming"],
        [
            "A character's value is its one-based alphabet position unless chars assigns it the corresponding custom value.",
            "A substring's cost is the sum of its character values; the empty substring costs zero.",
            "Return the maximum cost among all substrings.",
        ],
        [
            (["adaa", "d", [-1000]], "The best substring is aa with cost two."),
            (["abc", "abc", [-1, -1, -1]], "Every non-empty substring is negative, so choose the empty substring for zero."),
        ],
        [[s, c, v] for s, c, v in [
            ("a", "", []), ("z", "z", [-5]), ("z", "", []), ("aaaa", "a", [-1]),
            ("abcd", "b", [-10]), ("cab", "ac", [-5, 20]), ("leetcode", "et", [-20, 30]),
            ("xyzxyz", "xyz", [5, -10, 4]), ("banana", "bn", [-8, -3]),
            ("abcabc", "c", [-100]), ("qwerty", "qw", [0, 0]), ("mississippi", "is", [-4, 7]),
            ("azazaz", "az", [-2, 3]), ("algorithm", "go", [-20, -20]),
        ]],
        SUBSTRING,
        [SUBSTRING.replace("custom=dict(zip(chars,vals))", "custom=dict(zip(chars,map(abs,vals)))"), SUBSTRING.replace("ord(char)-ord('a')+1", "ord(char)-ord('a')")],
        ["Treats negative custom character costs as positive.", "Uses zero-based default alphabet values."],
        substring_oracle, random_substring,
        [
            "Convert custom characters to a lookup table and use alphabet positions for the rest.",
            "Track the best cost of a substring ending at the current character.",
            "Either extend the previous substring or restart from the empty substring when the running cost would be negative.",
            "This is Kadane's recurrence; the largest running value seen is the best substring cost.",
        ],
        "O(n + c)", "O(c)", 5,
    ),
    2607: entry(
        "minimum_equal_circular_sums_cost", [("arr", "list[int]"), ("k", "int")], "int",
        ["arrays", "greedy", "math", "sorting"],
        [
            "Treat arr as circular and consider every length-k subarray.",
            "One operation increments or decrements one element by one.",
            "Return the minimum operations needed to make all length-k subarray sums equal.",
        ],
        [
            ([[1, 4, 1, 3], 2], "Only indices in the odd-position cycle differ; changing four to three costs one."),
            ([[2, 5, 5, 7], 3], "All indices belong to one cycle, whose median five gives total cost five."),
        ],
        [[a, k] for a, k in [
            ([1], 1), ([1, 2], 1), ([1, 2], 2), ([1, 2, 3], 1), ([1, 2, 3], 2),
            ([1, 2, 3], 3), ([5, 5, 5, 5], 2), ([1, 10, 1, 10], 2),
            ([1, 2, 3, 4, 5, 6], 2), ([6, 5, 4, 3, 2, 1], 3),
            ([2, 8, 3, 9, 4], 2), ([10, 1, 7, 3, 9, 2], 4),
            ([1, 100, 2, 99, 3, 98], 3), ([7, 1, 4, 9, 2, 6, 3, 8], 6),
        ]],
        CIRCULAR,
        [CIRCULAR.replace("math.gcd(len(arr),k)", "k"), CIRCULAR.replace("values[len(values)//2]", "values[0]")],
        ["Treats k itself as the number of independent index cycles.", "Moves every cycle to its minimum rather than a median."],
        circular_oracle, random_circular,
        [
            "Equal adjacent length-k sums imply arr[i] must equal arr[(i+k) mod n].",
            "Those index links form gcd(n, k) independent cycles.",
            "All values in one cycle must become equal, and absolute-change cost is minimized by a median.",
            "Sort each cycle, choose its median, and sum distances across all cycles.",
        ],
        "O(n log n)", "O(n)", 6,
    ),
}
