"""Matrix, sliding-window, tree-DP, combinatorics, and transfer batch 153."""

from collections import Counter

from .import_batch_055 import entry


def matrix_oracle(args):
    n, queries = args
    result = [[0] * n for _ in range(n)]
    for top, left, bottom, right in queries:
        for row in range(top, bottom + 1):
            for column in range(left, right + 1):
                result[row][column] += 1
    return result


def random_matrix(rng):
    n = rng.randint(1, 7)
    queries = []
    for _ in range(rng.randint(1, 12)):
        top, bottom = sorted((rng.randrange(n), rng.randrange(n)))
        left, right = sorted((rng.randrange(n), rng.randrange(n)))
        queries.append([top, left, bottom, right])
    return [n, queries]


def subarrays_oracle(args):
    nums, k = args
    answer = 0
    for left in range(len(nums)):
        counts = Counter()
        pairs = 0
        for right in range(left, len(nums)):
            pairs += counts[nums[right]]
            counts[nums[right]] += 1
            answer += pairs >= k
    return answer


def random_subarrays(rng):
    return [
        [rng.randint(1, 7) for _ in range(rng.randint(1, 25))],
        rng.randint(1, 30),
    ]


def tree_oracle(args):
    n, edges, prices = args
    graph = [[] for _ in range(n)]
    for left, right in edges:
        graph[left].append(right)
        graph[right].append(left)
    answer = 0
    for root in range(n):
        stack = [(root, -1, prices[root])]
        maximum = prices[root]
        while stack:
            node, parent, total = stack.pop()
            maximum = max(maximum, total)
            for neighbor in graph[node]:
                if neighbor != parent:
                    stack.append((neighbor, node, total + prices[neighbor]))
        answer = max(answer, maximum - prices[root])
    return answer


def random_tree(rng):
    n = rng.randint(1, 14)
    return [
        n,
        [[node, rng.randrange(node)] for node in range(1, n)],
        [rng.randint(1, 20) for _ in range(n)],
    ]


def subsequences_oracle(args):
    text = args[0]
    answer = 0
    for mask in range(1, 1 << len(text)):
        counts = Counter(text[index] for index in range(len(text)) if mask >> index & 1)
        answer += len(set(counts.values())) == 1
    return answer % (10**9 + 7)


def random_subsequences(rng):
    return ["".join(rng.choice("abcde") for _ in range(rng.randint(1, 14)))]


def operations_oracle(args):
    first, second, k = args
    if k == 0:
        return 0 if first == second else -1
    differences = [a - b for a, b in zip(first, second)]
    if any(value % k for value in differences) or sum(differences):
        return -1
    return sum(max(0, value // k) for value in differences)


def random_operations(rng):
    n = rng.randint(1, 12)
    first = [rng.randint(0, 30) for _ in range(n)]
    k = rng.randint(0, 6)
    if k and n > 1 and rng.random() < 0.6:
        second = first[:]
        for _ in range(rng.randint(0, 5)):
            source, target = rng.sample(range(n), 2)
            if second[source] >= k:
                second[source] -= k
                second[target] += k
    else:
        second = [rng.randint(0, 30) for _ in range(n)]
    return [first, second, k]


MATRIX = """\
def increment_submatrices(n,queries):
    difference=[[0]*(n+1) for _ in range(n+1)]
    for top,left,bottom,right in queries:
        difference[top][left]+=1;difference[bottom+1][left]-=1
        difference[top][right+1]-=1;difference[bottom+1][right+1]+=1
    result=[[0]*n for _ in range(n)]
    for row in range(n):
        for column in range(n):
            value=difference[row][column]
            if row:value+=result[row-1][column]
            if column:value+=result[row][column-1]
            if row and column:value-=result[row-1][column-1]
            result[row][column]=value
    return result
"""

SUBARRAYS = """\
def count_good_pair_subarrays(nums,k):
    counts={};pairs=0;left=0;answer=0
    for right,value in enumerate(nums):
        pairs+=counts.get(value,0);counts[value]=counts.get(value,0)+1
        while pairs>=k:
            answer+=len(nums)-right
            outgoing=nums[left];counts[outgoing]-=1;pairs-=counts[outgoing];left+=1
    return answer
"""

TREE = """\
def maximum_root_path_difference(n,edges,price):
    graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    answer=0
    def visit(node,parent):
        nonlocal answer
        included=price[node];excluded=0
        for neighbor in graph[node]:
            if neighbor==parent:continue
            child_included,child_excluded=visit(neighbor,node)
            answer=max(answer,included+child_excluded,excluded+child_included)
            included=max(included,price[node]+child_included)
            excluded=max(excluded,price[node]+child_excluded)
        return included,excluded
    visit(0,-1)
    return answer
"""

SUBSEQUENCES = """\
def count_equal_frequency_subsequences(s):
    modulus=10**9+7;counts={}
    for char in s:counts[char]=counts.get(char,0)+1
    maximum=max(counts.values());factorial=[1]*(maximum+1)
    for value in range(1,maximum+1):factorial[value]=factorial[value-1]*value%modulus
    inverse=[pow(value,modulus-2,modulus) for value in factorial]
    def choose(total,taken):return factorial[total]*inverse[taken]%modulus*inverse[total-taken]%modulus
    answer=0
    for frequency in range(1,maximum+1):
        ways=1
        for count in counts.values():
            if count>=frequency:ways=ways*(choose(count,frequency)+1)%modulus
        answer=(answer+ways-1)%modulus
    return answer
"""

OPERATIONS = """\
def minimum_balanced_transfer_operations(nums1,nums2,k):
    if k==0:return 0 if nums1==nums2 else -1
    supplied=needed=0
    for first,second in zip(nums1,nums2):
        difference=first-second
        if difference%k:return -1
        if difference>0:supplied+=difference//k
        else:needed-=difference//k
    return supplied if supplied==needed else -1
"""


BATCH = {
    2536: entry(
        "increment_submatrices",
        [("n", "int"), ("queries", "list[list[int]]")],
        "list[list[int]]",
        ["matrices", "prefix sums", "arrays"],
        [
            "Begin with an n by n zero matrix.",
            "Each query [top,left,bottom,right] adds one to every cell in that inclusive rectangle.",
            "Return the matrix after all queries.",
        ],
        [
            (
                [3, [[1, 1, 2, 2], [0, 0, 1, 1]]],
                "The two rectangles overlap only at cell (1,1), producing value two there.",
            ),
            (
                [2, [[0, 0, 1, 1]]],
                "One full-matrix query increments all four cells to one.",
            ),
        ],
        [
            [n, q]
            for n, q in [
                (1, [[0, 0, 0, 0]]),
                (2, [[0, 0, 0, 0]]),
                (2, [[1, 1, 1, 1]]),
                (2, [[0, 1, 1, 1]]),
                (3, [[0, 0, 2, 2]]),
                (3, [[0, 0, 0, 2]]),
                (3, [[0, 0, 2, 0]]),
                (3, [[0, 0, 1, 1], [1, 1, 2, 2]]),
                (4, [[1, 0, 3, 2]]),
                (4, [[0, 1, 2, 3], [1, 0, 3, 2]]),
                (5, [[2, 2, 2, 2]]),
                (5, [[0, 0, 4, 4], [1, 1, 3, 3]]),
                (3, [[0, 2, 2, 2], [2, 0, 2, 2]]),
                (4, [[0, 0, 0, 0], [3, 3, 3, 3]]),
            ]
        ],
        MATRIX,
        [MATRIX.replace("bottom+1", "bottom"), MATRIX.replace("right+1", "right")],
        [
            "Ends each vertical update one row too early.",
            "Ends each horizontal update one column too early.",
        ],
        matrix_oracle,
        random_matrix,
        [
            "A two-dimensional difference matrix records rectangle boundaries instead of touching every covered cell.",
            "Add at the top-left, subtract just below and just right, then restore the double-subtracted bottom-right corner.",
            "Take two-dimensional prefix sums to recover each cell's total increment.",
            "Each rectangle contributes one exactly inside both of its row and column intervals, so summing boundary effects reproduces all queries.",
        ],
        "O(n squared+queries)",
        "O(n squared)",
        6,
    ),
    2537: entry(
        "count_good_pair_subarrays",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "sliding window", "hash maps"],
        [
            "A pair consists of two different indices in a subarray holding equal values.",
            "A subarray is good when it contains at least k such unordered pairs.",
            "Return the number of good contiguous subarrays.",
        ],
        [
            (
                [[1, 1, 1, 1, 1], 10],
                "All five elements form exactly ten equal-value pairs, so only the full array qualifies.",
            ),
            (
                [[3, 1, 4, 3, 2, 2, 4], 2],
                "Exactly four subarrays accumulate at least two matching pairs.",
            ),
        ],
        [
            [a, k]
            for a, k in [
                ([1], 1),
                ([1, 1], 1),
                ([1, 2], 1),
                ([1, 1, 1], 1),
                ([1, 1, 1], 3),
                ([1, 2, 1], 1),
                ([1, 2, 1, 2], 2),
                ([2, 2, 3, 3], 1),
                ([1, 2, 3, 4], 1),
                ([5, 5, 5, 5], 4),
                ([1, 1, 2, 2, 1], 3),
                ([3, 3, 1, 3, 1, 1], 4),
                ([2, 1, 2, 1, 2, 1], 5),
                ([7, 7, 8, 8, 7, 8, 7], 6),
            ]
        ],
        SUBARRAYS,
        [
            SUBARRAYS.replace("pairs>=k", "pairs>k"),
            SUBARRAYS.replace("len(nums)-right", "len(nums)-right-1"),
        ],
        [
            "Rejects windows containing exactly k pairs.",
            "Omits one valid right extension for every minimal qualifying window.",
        ],
        subarrays_oracle,
        random_subarrays,
        [
            "Adding a value creates one new pair with every equal value already in the window.",
            "Once a window has at least k pairs, every extension to its right is also good.",
            "Count all those extensions, remove the left value, and continue while the window remains good.",
            "Each good subarray is counted when its left endpoint is removed from the first qualifying window ending at or before its right endpoint.",
        ],
        "O(n)",
        "O(distinct values)",
        6,
    ),
    2538: entry(
        "maximum_root_path_difference",
        [("n", "int"), ("edges", "list[list[int]]"), ("price", "list[int]")],
        "int",
        ["trees", "recursion", "dynamic programming"],
        [
            "The edges form a connected undirected tree and every node price is positive.",
            "For a chosen root, consider sums of all paths starting at that root, including the root-only path.",
            "Return the largest possible difference between maximum and minimum path sums over every root choice.",
        ],
        [
            (
                [6, [[0, 1], [1, 2], [1, 3], [3, 4], [3, 5]], [9, 8, 7, 6, 10, 5]],
                "Root zero has maximum path sum 33 and minimum root-only sum 9, giving the optimal difference 24.",
            ),
            (
                [3, [[0, 1], [1, 2]], [1, 1, 1]],
                "Choosing either endpoint yields path-sum difference two.",
            ),
        ],
        [
            [n, e, p]
            for n, e, p in [
                (1, [], [5]),
                (2, [[0, 1]], [1, 2]),
                (2, [[0, 1]], [10, 1]),
                (3, [[0, 1], [0, 2]], [5, 2, 3]),
                (4, [[0, 1], [1, 2], [2, 3]], [1, 2, 3, 4]),
                (4, [[0, 1], [0, 2], [0, 3]], [9, 1, 1, 1]),
                (5, [[0, 1], [1, 2], [1, 3], [3, 4]], [2, 7, 1, 8, 2]),
                (5, [[0, 1], [0, 2], [2, 3], [2, 4]], [10, 1, 4, 1, 9]),
                (6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]], [6, 5, 4, 3, 2, 1]),
                (6, [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]], [1, 2, 3, 4, 5, 6]),
                (
                    7,
                    [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]],
                    [3, 1, 4, 1, 5, 9, 2],
                ),
                (4, [[0, 1], [1, 2], [1, 3]], [100, 1, 1, 1]),
                (5, [[0, 1], [1, 2], [2, 3], [2, 4]], [1, 100, 1, 100, 1]),
                (
                    8,
                    [[0, 1], [1, 2], [1, 3], [3, 4], [3, 5], [5, 6], [5, 7]],
                    [8, 6, 7, 5, 3, 2, 9, 4],
                ),
            ]
        ],
        TREE,
        [
            TREE.replace("excluded=0", "excluded=price[node]"),
            TREE.replace("included+child_excluded", "included+child_included"),
        ],
        [
            "Forces both combined paths to include their endpoint prices instead of allowing one excluded endpoint.",
            "Combines two fully included paths and counts their connecting node price twice.",
        ],
        tree_oracle,
        random_tree,
        [
            "Because prices are positive, the minimum path from a root is its root-only path.",
            "At each node track the best downward path including its endpoint and the best variant excluding one endpoint price.",
            "Combine one child path with the best accumulated path from previously processed branches before updating either state.",
            "Every candidate optimal path has a unique highest joining node; the paired included/excluded states count its prices exactly once.",
        ],
        "O(n)",
        "O(n)",
        8,
    ),
    2539: entry(
        "count_equal_frequency_subsequences",
        [("s", "str")],
        "int",
        ["strings", "combinatorics", "counting"],
        [
            "Count nonempty subsequences in which every selected distinct character occurs equally often.",
            "Different choices of source indices count as different subsequences.",
            "Return the count modulo 1,000,000,007.",
        ],
        [
            (
                ["aabb"],
                "Ten one-frequency choices plus the subsequence using both copies of one or both letters give eleven.",
            ),
            (
                ["leet"],
                "There are twelve good index subsequences across common frequencies one and two.",
            ),
        ],
        [
            [s]
            for s in [
                "a",
                "aa",
                "ab",
                "aaa",
                "abc",
                "aab",
                "abb",
                "abab",
                "abcabc",
                "aaaa",
                "aaab",
                "aabbcc",
                "abacaba",
                "aabcddd",
            ]
        ],
        SUBSEQUENCES,
        [
            SUBSEQUENCES.replace(
                "choose(count,frequency)+1", "choose(count,frequency)"
            ),
            SUBSEQUENCES.replace("ways-1", "ways"),
        ],
        [
            "Forces every available character to be selected instead of allowing it to be absent.",
            "Includes the empty selection once at every candidate frequency.",
        ],
        subsequences_oracle,
        random_subsequences,
        [
            "Fix the common positive frequency f, then decide independently whether to use each character.",
            "A character appearing c times offers C(c,f) index choices when selected, plus one choice to omit it.",
            "Multiply these choices across characters, subtract the all-omitted choice, and sum over feasible f.",
            "Every good subsequence has one unique common frequency, so the frequency cases are disjoint and exhaustive.",
        ],
        "O(alphabet times maximum frequency)",
        "O(maximum frequency)",
        6,
    ),
    2541: entry(
        "minimum_balanced_transfer_operations",
        [("nums1", "list[int]"), ("nums2", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "greedy", "math"],
        [
            "One operation increases one nums1 element by k and decreases another nums1 element by k.",
            "Return the minimum operations making nums1 equal nums2, or -1 if impossible.",
            "When k is zero, only already-equal arrays can be transformed.",
        ],
        [
            (
                [[4, 3, 1, 4], [1, 3, 7, 1], 3],
                "Two units of size three must move from surplus positions to the deficit position.",
            ),
            (
                [[3, 8, 5, 2], [2, 4, 1, 6], 1],
                "The total sums differ, so transfers cannot make the arrays equal.",
            ),
        ],
        [
            [a, b, k]
            for a, b, k in [
                ([1], [1], 0),
                ([1], [2], 0),
                ([1], [1], 1),
                ([2, 0], [0, 2], 1),
                ([4, 0], [0, 4], 2),
                ([3, 0], [0, 3], 2),
                ([1, 2], [2, 1], 1),
                ([5, 5, 0], [0, 5, 5], 5),
                ([10, 0, 0], [0, 5, 5], 5),
                ([1, 2, 3], [3, 2, 1], 2),
                ([7, 1, 4], [1, 7, 4], 3),
                ([9, 6, 3], [3, 6, 9], 3),
                ([0, 0, 12, 0], [3, 3, 3, 3], 3),
                ([8, 4, 0, 4], [4, 4, 4, 4], 4),
            ]
        ],
        OPERATIONS,
        [
            OPERATIONS.replace("difference%k", "abs(difference)%k or difference==0"),
            OPERATIONS.replace("supplied==needed", "supplied>=needed"),
        ],
        [
            "Incorrectly rejects positions that already match.",
            "Accepts unmatched total surplus instead of requiring exact balance.",
        ],
        operations_oracle,
        random_operations,
        [
            "Each operation preserves the total sum and changes two positions by exact multiples of k.",
            "Reject any non-divisible difference and separately total the surplus and deficit units.",
            "If k is zero, compare the arrays directly; otherwise require the two unit totals to match.",
            "Every operation pairs one surplus unit with one deficit unit, so their common total is both necessary and sufficient and is the minimum count.",
        ],
        "O(n)",
        "O(1)",
        5,
    ),
}
