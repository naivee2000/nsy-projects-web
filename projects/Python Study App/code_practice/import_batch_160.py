"""Rerooting, TreeNode levels, prime splits, knapsack, and vowel batch 160."""

from collections import Counter, deque
from math import gcd

from .import_batch_055 import entry


def roots_oracle(args):
    edges, guesses, k = args
    n = len(edges) + 1
    graph = [[] for _ in range(n)]
    for left, right in edges:
        graph[left].append(right)
        graph[right].append(left)
    answer = 0
    for root in range(n):
        parent = {root: -1}
        stack = [root]
        while stack:
            node = stack.pop()
            for neighbor in graph[node]:
                if neighbor not in parent:
                    parent[neighbor] = node
                    stack.append(neighbor)
        answer += (
            sum(parent.get(child) == parent_guess for parent_guess, child in guesses)
            >= k
        )
    return answer


def random_roots(rng):
    n = rng.randint(2, 12)
    edges = [[node, rng.randrange(node)] for node in range(1, n)]
    candidates = list({tuple(edge) for edge in edges} | {(b, a) for a, b in edges})
    rng.shuffle(candidates)
    guesses = [list(pair) for pair in candidates[: rng.randint(1, len(candidates))]]
    return [edges, guesses, rng.randint(0, len(guesses))]


def levels_oracle(args):
    values, k = args
    if not values:
        return -1
    root = [values[0], None, None]
    queue = deque([root])
    index = 1
    while queue and index < len(values):
        node = queue.popleft()
        for side in (1, 2):
            if index < len(values) and values[index] is not None:
                node[side] = [values[index], None, None]
                queue.append(node[side])
            index += 1
    level = [root]
    sums = []
    while level:
        sums.append(sum(node[0] for node in level))
        level = [child for node in level for child in node[1:] if child is not None]
    return sorted(sums, reverse=True)[k - 1] if k <= len(sums) else -1


def random_levels(rng):
    size = rng.randint(1, 31)
    values = [rng.randint(-20, 30) for _ in range(size)]
    return [values, rng.randint(1, 8)]


def split_oracle(args):
    nums = args[0]
    for index in range(len(nums) - 1):
        left = 1
        right = 1
        for value in nums[: index + 1]:
            left *= value
        for value in nums[index + 1 :]:
            right *= value
        if gcd(left, right) == 1:
            return index
    return -1


def random_split(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(2, 10))]]


def points_oracle(args):
    target, types = args

    def visit(index, remaining):
        if index == len(types):
            return int(remaining == 0)
        count, marks = types[index]
        return sum(
            visit(index + 1, remaining - used * marks)
            for used in range(count + 1)
            if used * marks <= remaining
        )

    return visit(0, target) % (10**9 + 7)


def random_points(rng):
    return [
        rng.randint(0, 30),
        [[rng.randint(1, 6), rng.randint(1, 10)] for _ in range(rng.randint(1, 6))],
    ]


def vowel_oracle(args):
    words, left, right = args
    vowels = set("aeiou")
    return sum(
        word[0] in vowels and word[-1] in vowels for word in words[left : right + 1]
    )


def random_vowel(rng):
    count = rng.randint(1, 20)
    words = [
        "".join(rng.choice("abcdeiou") for _ in range(rng.randint(1, 8)))
        for _ in range(count)
    ]
    left, right = sorted((rng.randrange(count), rng.randrange(count)))
    return [words, left, right]


ROOTS = """\
def count_possible_tree_roots(edges,guesses,k):
    graph=[[] for _ in range(len(edges)+1)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    guessed=set(map(tuple,guesses));initial=0
    def count(node,parent):
        nonlocal initial
        for neighbor in graph[node]:
            if neighbor!=parent:initial+=(node,neighbor) in guessed;count(neighbor,node)
    count(0,-1);answer=0
    def reroot(node,parent,current):
        nonlocal answer
        answer+=current>=k
        for neighbor in graph[node]:
            if neighbor!=parent:reroot(neighbor,node,current-((node,neighbor) in guessed)+((neighbor,node) in guessed))
    reroot(0,-1,initial)
    return answer
"""

LEVELS = """\
def kth_largest_tree_level_sum(root,k):
    from collections import deque
    if root is None:return -1
    queue=deque([root]);sums=[]
    while queue:
        total=0
        for _ in range(len(queue)):
            node=queue.popleft();total+=node.val
            if node.left:queue.append(node.left)
            if node.right:queue.append(node.right)
        sums.append(total)
    sums.sort(reverse=True)
    return sums[k-1] if k<=len(sums) else -1
"""

SPLIT = """\
def earliest_coprime_product_split(nums):
    last={}
    for index,value in enumerate(nums):
        factor=2
        while factor*factor<=value:
            if value%factor==0:
                last[factor]=index
                while value%factor==0:value//=factor
            factor+=1
        if value>1:last[value]=index
    farthest=0
    for index,value in enumerate(nums[:-1]):
        factor=2
        while factor*factor<=value:
            if value%factor==0:
                farthest=max(farthest,last[factor])
                while value%factor==0:value//=factor
            factor+=1
        if value>1:farthest=max(farthest,last[value])
        if index==farthest:return index
    return -1
"""

POINTS = """\
def count_target_point_ways(target,types):
    modulus=10**9+7;ways=[0]*(target+1);ways[0]=1
    for count,marks in types:
        following=[0]*(target+1)
        for total in range(target+1):
            if ways[total]:
                for used in range(count+1):
                    score=total+used*marks
                    if score>target:break
                    following[score]=(following[score]+ways[total])%modulus
        ways=following
    return ways[target]
"""

VOWEL = """\
def count_vowel_boundary_words(words,left,right):
    vowels=set('aeiou')
    return sum(word[0] in vowels and word[-1] in vowels for word in words[left:right+1])
"""


BATCH = {
    2581: entry(
        "count_possible_tree_roots",
        [("edges", "list[list[int]]"), ("guesses", "list[list[int]]"), ("k", "int")],
        "int",
        ["trees", "recursion", "rerooting", "hash maps"],
        [
            "edges form an undirected tree on nodes zero through n-1.",
            "Each directed guess [parent,child] predicts one edge orientation.",
            "Return how many root choices make at least k guesses correct.",
        ],
        [
            (
                [[[0, 1], [1, 2], [1, 3], [4, 2]], [[1, 3], [0, 1], [1, 0], [2, 4]], 3],
                "Roots zero, one, and four each satisfy at least three guesses.",
            ),
            (
                [[[0, 1], [1, 2]], [[0, 1]], 1],
                "Only root zero preserves the guessed orientation, so the answer is one.",
            ),
        ],
        [
            [e, g, k]
            for e, g, k in [
                ([[0, 1]], [[0, 1]], 0),
                ([[0, 1]], [[0, 1]], 1),
                ([[0, 1]], [[1, 0]], 1),
                ([[0, 1], [1, 2]], [[0, 1], [1, 2]], 2),
                ([[0, 1], [0, 2]], [[1, 0], [2, 0]], 1),
                ([[0, 1], [1, 2], [2, 3]], [[0, 1], [2, 1]], 1),
                ([[0, 1], [0, 2], [0, 3]], [[0, 1], [0, 2]], 2),
                ([[0, 1], [1, 2], [1, 3]], [[2, 1], [3, 1]], 2),
                ([[0, 1], [1, 2], [2, 3], [3, 4]], [[1, 0], [1, 2], [3, 2]], 2),
                ([[0, 1], [0, 2], [2, 3], [2, 4]], [[0, 2], [2, 3], [4, 2]], 2),
                ([[0, 1], [1, 2], [1, 3], [3, 4]], [[1, 0], [1, 2], [3, 1], [3, 4]], 3),
                (
                    [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5]],
                    [[0, 1], [0, 2], [1, 4], [5, 2]],
                    3,
                ),
                (
                    [[0, 1], [1, 2], [2, 3], [2, 4], [4, 5]],
                    [[1, 0], [2, 1], [2, 3], [4, 2], [4, 5]],
                    4,
                ),
                (
                    [[0, 1], [0, 2], [2, 3], [3, 4], [3, 5]],
                    [[0, 2], [2, 3], [3, 4], [5, 3]],
                    2,
                ),
            ]
        ],
        ROOTS,
        [
            ROOTS.replace(
                "current-((node,neighbor) in guessed)+((neighbor,node) in guessed)",
                "current+((node,neighbor) in guessed)-((neighbor,node) in guessed)",
            ),
            ROOTS.replace("current>=k", "current>k"),
        ],
        [
            "Updates guess correctness in the wrong direction when rerooting across an edge.",
            "Requires more than k correct guesses instead of at least k.",
        ],
        roots_oracle,
        random_roots,
        [
            "First root the tree at zero and count correct directed guesses.",
            "Moving the root across edge parent-child reverses only that edge's orientation.",
            "Subtract a guessed old orientation and add a guessed reversed orientation while recursing.",
            "Every node is reached once with its exact rerooted count, so thresholding those counts returns all possible roots in linear time.",
        ],
        "O(n+guesses)",
        "O(n+guesses)",
        8,
    ),
    2583: entry(
        "kth_largest_tree_level_sum",
        [("root", "TreeNode | None"), ("k", "int")],
        "int",
        ["trees", "breadth-first search", "sorting"],
        [
            "Compute the sum of node values at each depth of a nonempty binary tree.",
            "Return the kth largest level sum.",
            "Return -1 when the tree has fewer than k levels.",
        ],
        [
            (
                [[5, 8, 9, 2, 1, 3, 7, 4, 6], 2],
                "Level sums are 5, 17, 13, and 10, so the second largest is 13.",
            ),
            ([[1], 1], "The only level sum is one."),
        ],
        [
            [[1], 2],
            [[1, 2], 1],
            [[1, None, 2], 2],
            [[1, 2, 3], 2],
            [[1, 2, 3, 4, 5], 3],
            [[5, -2, 7], 1],
            [[10, 5, 15, 2, 7, 12, 20], 3],
            [[0, -1, 1, -2, None, None, 2], 2],
            [[3, 9, 20, None, None, 15, 7], 2],
            [[1, 1, 1, 1, 1, 1, 1], 4],
            [[8, 4, 12, 2, 6, 10, 14], 3],
            [[5, 3, 8, None, 4], 2],
            [[100, -50, -40, 10, 20], 1],
            [[7, 2, 9, 1, None, 8, 10], 3],
        ],
        LEVELS,
        [
            LEVELS.replace("reverse=True", "reverse=False"),
            LEVELS.replace("k<=len(sums)", "k<len(sums)"),
        ],
        [
            "Sorts level sums ascending instead of descending.",
            "Rejects the valid boundary where k equals the number of levels.",
        ],
        levels_oracle,
        random_levels,
        [
            "Traverse the tree one level at a time with a queue.",
            "At each iteration, process exactly the queue length captured at the start and accumulate those node values.",
            "Sort all completed level sums descending and select index k-1.",
            "Breadth-first queue boundaries exactly match depths, so every level contributes one complete sum.",
        ],
        "O(nodes+levels log levels)",
        "O(nodes)",
        6,
    ),
    2584: entry(
        "earliest_coprime_product_split",
        [("nums", "list[int]")],
        "int",
        ["arrays", "prime factorization", "greedy"],
        [
            "Split after index i with both sides nonempty.",
            "The products of the two sides must have greatest common divisor one.",
            "Return the smallest valid i, or -1.",
        ],
        [
            (
                [[4, 7, 8, 15, 3, 5]],
                "After index two, left primes are two and seven while right primes are three and five, so the products are coprime.",
            ),
            (
                [[4, 7, 15, 8, 3, 5]],
                "Every split shares at least one prime across the boundary.",
            ),
        ],
        [
            [a]
            for a in [
                [1, 1],
                [2, 3],
                [2, 2],
                [6, 35],
                [6, 10, 15],
                [2, 3, 5, 7],
                [4, 8, 16, 3],
                [6, 5, 10, 7],
                [2, 9, 15, 7],
                [30, 7, 11, 13],
                [4, 6, 5, 9],
                [2, 3, 6, 5, 7],
                [12, 25, 7, 18, 5],
                [2, 15, 14, 9, 25, 11],
            ]
        ],
        SPLIT,
        [
            SPLIT.replace("if index==farthest", "if index+1==farthest"),
            SPLIT.replace("last[factor]=index", "last.setdefault(factor,index)"),
        ],
        [
            "Uses an off-by-one boundary when deciding that all active prime intervals have closed.",
            "Stores the first prime occurrence instead of its last occurrence.",
        ],
        split_oracle,
        random_split,
        [
            "A split is valid exactly when no prime factor appears on both sides.",
            "Record the last index containing each prime factor.",
            "Scan left to right while extending the farthest required endpoint for factors seen so far.",
            "The first index equal to that farthest endpoint closes every active prime interval, and therefore is the earliest coprime split.",
        ],
        "O(n sqrt(max value))",
        "O(distinct primes)",
        8,
    ),
    2585: entry(
        "count_target_point_ways",
        [("target", "int"), ("types", "list[list[int]]")],
        "int",
        ["dynamic programming", "bounded knapsack", "counting"],
        [
            "Each type [count,marks] supplies up to count indistinguishable questions worth marks points each.",
            "Count choices of quantities by type that total exactly target.",
            "Return the count modulo 1,000,000,007.",
        ],
        [
            (
                [6, [[6, 1], [3, 2], [2, 3]]],
                "Seven different per-type quantity choices total exactly six points.",
            ),
            (
                [5, [[1, 2], [1, 3]]],
                "Taking one question of each type is the only way to score five.",
            ),
        ],
        [
            [t, a]
            for t, a in [
                (0, [[1, 1]]),
                (1, [[1, 1]]),
                (2, [[1, 1]]),
                (4, [[2, 2]]),
                (3, [[3, 1], [1, 2]]),
                (5, [[2, 1], [2, 2]]),
                (10, [[5, 2], [2, 5]]),
                (7, [[3, 2], [3, 3]]),
                (8, [[2, 4], [4, 2]]),
                (6, [[1, 6], [6, 1]]),
                (9, [[2, 3], [3, 2], [1, 5]]),
                (12, [[4, 3], [3, 4]]),
                (15, [[5, 1], [5, 2], [5, 3]]),
                (20, [[2, 5], [3, 4], [4, 2]]),
            ]
        ],
        POINTS,
        [
            POINTS.replace("range(count+1)", "range(count)"),
            POINTS.replace("ways[0]=1", "ways[0]=0"),
        ],
        [
            "Never allows using the full available count of a question type.",
            "Removes the single empty construction that seeds every valid score combination.",
        ],
        points_oracle,
        random_points,
        [
            "Use bounded knapsack DP where ways[score] counts quantity choices after processed types.",
            "For one type, try every used quantity from zero through its count.",
            "Transfer each reachable old score to old+used*marks in a fresh array.",
            "Using a fresh layer prevents reusing a type beyond its bound, and each final quantity vector follows one unique sequence of transitions.",
        ],
        "O(types times target times maximum count)",
        "O(target)",
        8,
    ),
    2586: entry(
        "count_vowel_boundary_words",
        [("words", "list[str]"), ("left", "int"), ("right", "int")],
        "int",
        ["arrays", "strings", "counting"],
        [
            "A word qualifies when both its first and last lowercase characters are vowels.",
            "Inspect the inclusive index interval from left through right.",
            "Return the number of qualifying words.",
        ],
        [
            (
                [["are", "amy", "u"], 0, 2],
                "Words are and u start and end with vowels, so the answer is two.",
            ),
            (
                [["hey", "aeo", "mu", "ooo", "artro"], 1, 4],
                "Only aeo and ooo have vowels at both boundaries.",
            ),
        ],
        [
            [w, l, r]
            for w, l, r in [
                (["a"], 0, 0),
                (["b"], 0, 0),
                (["aa", "bb"], 0, 1),
                (["ab", "ba"], 0, 1),
                (["e", "i", "o"], 1, 2),
                (["apple", "orange"], 0, 1),
                (["ice", "owl", "emu"], 0, 2),
                (["cat", "eye", "area"], 1, 2),
                (["u", "x", "o"], 0, 1),
                (["ae", "ea", "ii"], 2, 2),
                (["unit", "idea", "echo"], 0, 1),
                (["a", "b", "e", "c", "i"], 1, 3),
                (["oo", "no", "on"], 0, 2),
                (["ice", "owl", "emu", "ant"], 0, 3),
            ]
        ],
        VOWEL,
        [
            VOWEL.replace("word[-1] in vowels", "word[-1] not in vowels"),
            VOWEL.replace("right+1", "right"),
        ],
        [
            "Counts words ending with consonants instead of vowels.",
            "Treats the inclusive right endpoint as exclusive.",
        ],
        vowel_oracle,
        random_vowel,
        [
            "Store the five vowels in a set.",
            "Slice or scan the inclusive range only.",
            "For each word, test both boundary characters and add the resulting Boolean.",
            "Every word is independently counted exactly when both defining conditions hold.",
        ],
        "O(right-left+1)",
        "O(1)",
        3,
    ),
}

BATCH[2583]["params"][0] = ("root", "TreeNode | None", "treenode")
