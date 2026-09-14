"""First reviewed group of workbook batch 112."""

from collections import Counter
from itertools import product

from .import_batch_055 import entry


def rungs_oracle(arguments):
    rungs, distance = arguments
    return sum((upper - lower - 1) // distance for lower, upper in zip([0] + rungs, rungs))


def points_oracle(arguments):
    points = arguments[0]
    return max(sum(points[row][columns[row]] for row in range(len(points)))
               - sum(abs(columns[row] - columns[row - 1]) for row in range(1, len(points)))
               for columns in product(range(len(points[0])), repeat=len(points)))


def genetic_oracle(arguments):
    parents, queries = arguments
    answer = []
    for node, value in queries:
        candidates = []
        while node != -1:
            candidates.append(value ^ node)
            node = parents[node]
        answer.append(max(candidates))
    return answer


def common_oracle(arguments):
    arrays = arguments[0]
    return sorted(set(arrays[0]).intersection(*(set(row) for row in arrays[1:])))


def frequency_oracle(arguments):
    amounts = list(Counter(arguments[0]).values())
    return all(amount == amounts[0] for amount in amounts)


def random_rungs(rng):
    values = sorted(rng.sample(range(1, 150), rng.randint(1, 20)))
    return [values, rng.randint(1, 20)]


def random_points(rng):
    rows, columns = rng.randint(1, 5), rng.randint(1, 5)
    return [[[rng.randint(0, 20) for _ in range(columns)] for _ in range(rows)]]


def random_genetic(rng):
    size = rng.randint(2, 15)
    parents = [-1] + [rng.randrange(node) for node in range(1, size)]
    queries = [[rng.randrange(size), rng.randint(0, 255)] for _ in range(rng.randint(1, 20))]
    return [parents, queries]


def random_common(rng):
    arrays = []
    for _ in range(rng.randint(2, 7)):
        arrays.append(sorted(rng.sample(range(1, 101), rng.randint(1, 20))))
    return [arrays]


def random_frequency(rng):
    return ["".join(rng.choice("abcdef") for _ in range(rng.randint(1, 50)))]


RUNGS = '''\
def minimum_added_rungs(rungs, dist):
    answer = 0
    previous = 0
    for height in rungs:
        answer += (height - previous - 1) // dist
        previous = height
    return answer
'''

POINTS = '''\
def maximum_points_with_movement_cost(points):
    columns = len(points[0])
    previous = points[0][:]
    for row in points[1:]:
        current = [0] * columns
        best = -10**30
        for column in range(columns):
            best = max(best, previous[column] + column)
            current[column] = row[column] + best - column
        best = -10**30
        for column in range(columns - 1, -1, -1):
            best = max(best, previous[column] - column)
            current[column] = max(current[column], row[column] + best + column)
        previous = current
    return max(previous)
'''

GENETIC = '''\
def maximum_genetic_differences(parents, queries):
    size = len(parents)
    children = [[] for _ in range(size)]
    root = 0
    for node, parent in enumerate(parents):
        if parent == -1:
            root = node
        else:
            children[parent].append(node)
    grouped = [[] for _ in range(size)]
    for index, (node, value) in enumerate(queries):
        grouped[node].append((index, value))
    highest = max(max(size - 1, max((value for _, value in queries), default=0)).bit_length() - 1, 0)
    trie = [{"children": [-1, -1], "count": 0}]

    def change(value, delta):
        current = 0
        trie[current]["count"] += delta
        for bit in range(highest, -1, -1):
            direction = (value >> bit) & 1
            child = trie[current]["children"][direction]
            if child == -1:
                child = len(trie)
                trie[current]["children"][direction] = child
                trie.append({"children": [-1, -1], "count": 0})
            current = child
            trie[current]["count"] += delta

    def best_xor(value):
        current = result = 0
        for bit in range(highest, -1, -1):
            direction = (value >> bit) & 1
            preferred = trie[current]["children"][direction ^ 1]
            if preferred != -1 and trie[preferred]["count"]:
                result |= 1 << bit
                current = preferred
            else:
                current = trie[current]["children"][direction]
        return result

    answer = [0] * len(queries)
    stack = [(root, False)]
    while stack:
        node, leaving = stack.pop()
        if leaving:
            change(node, -1)
            continue
        change(node, 1)
        for index, value in grouped[node]:
            answer[index] = best_xor(value)
        stack.append((node, True))
        stack.extend((child, False) for child in reversed(children[node]))
    return answer
'''

COMMON = '''\
def common_values_in_sorted_arrays(arrays):
    counts = [0] * 101
    for row in arrays:
        for value in row:
            counts[value] += 1
    return [value for value in range(1, 101) if counts[value] == len(arrays)]
'''

FREQUENCY = '''\
def equal_character_frequencies(s):
    from collections import Counter
    frequencies = set(Counter(s).values())
    return len(frequencies) == 1
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


BATCH = {
    1936: entry(
        "minimum_added_rungs", [("rungs", "list[int]"), ("dist", "int")], "int", ["arrays", "greedy"],
        ["rungs has 1 through 100000 strictly increasing positive heights, each at most 1000000000.",
         "1 <= dist <= 1000000000.", "Begin at floor height zero and insert rungs only at positive integer heights."],
        [([[1,3,5,10],2], "The final gap needs two inserted rungs, such as heights seven and eight."),
         ([[3,6,8,10],3], "Every gap from the floor onward is already at most three, so no rung is added.")],
        [[r,d] for r,d in [([1],1),([2],1),([10],3),([3,4,6,7],2),([1,2,3],5),([5,10,15],5),
                           ([5,10,15],4),([2,8],3),([100],10),([1,100],9),([4,9,15],5),([4,9,15],4),
                           ([10,20,31],10),([999999999,1000000000],1000000000)]],
        RUNGS,
        [RUNGS.replace("height - previous - 1", "height - previous"), RUNGS.replace("previous = 0", "previous = rungs[0]")],
        ["Uses ceiling division on the gap itself and inserts an extra rung when a gap is exactly divisible.",
         "Forgets that the first climb begins at the floor at height zero."],
        rungs_oracle, random_rungs,
        lesson("A gap of g needs exactly floor((g-1)/dist) inserted rungs.",
               "Process each consecutive gap independently, including the gap from floor zero to the first rung.",
               "Add (height-previous-1)//dist for every rung, then advance previous.",
               "That many insertions divide a gap into the minimum number of pieces whose lengths are all at most dist; different gaps do not interact."),
        "O(n)", "O(1)", 5),
    1937: entry(
        "maximum_points_with_movement_cost", [("points", "list[list[int]]")], "int", ["dynamic programming", "matrices"],
        ["points is a nonempty rectangular matrix with at most 100000 cells.", "Each value is from 0 through 100000.",
         "Select exactly one cell per row and subtract the absolute column change between adjacent selections."],
        [([[[1,2,3],[1,5,1],[3,1,1]]], "Columns two, one, and zero score 3+5+3 minus two moves, for nine."),
         ([[[1,5],[2,3],[4,2]]], "Columns one, one, and zero score twelve before one movement point, for eleven.")],
        [[matrix] for matrix in [[[0]],[[5]],[[1,2,3]],[[1],[2],[3]],[[0,0],[0,0]],[[10,0],[0,10]],
                                 [[5,1,5],[1,10,1]],[[1,100,1],[100,1,100]],[[3,1,4],[1,5,9],[2,6,5]],
                                 [[9,0,0],[0,0,9],[9,0,0]],[[2,2,2],[2,2,2]],[[0,5,0,0],[0,0,0,6]],
                                 [[100000,0],[0,100000]],[[1,2],[3,4],[5,6],[7,8]]]],
        POINTS,
        ['''def maximum_points_with_movement_cost(points):\n    return sum(max(row) for row in points)\n''',
         '''def maximum_points_with_movement_cost(points):\n    return max(sum(row[c] for row in points) for c in range(len(points[0])))\n'''],
        ["Chooses each row maximum independently and never subtracts movement cost.",
         "Forbids column changes entirely even when moving produces a higher score after its cost."],
        points_oracle, random_points,
        lesson("For each destination column, the previous-row transition separates into a best value from the left and from the right.",
               "Sweep left while maintaining max(previous[c]+c), then right with max(previous[c]-c).",
               "For every row compute both directional maxima, add the current cell, and retain the larger transition.",
               "The two sweeps partition every predecessor by whether it lies left or right of the destination and algebraically include the exact absolute-distance penalty."),
        "O(rows*columns)", "O(columns)", 6),
    1938: entry(
        "maximum_genetic_differences", [("parents", "list[int]"), ("queries", "list[list[int]]")], "list[int]",
        ["trees", "tries", "bit manipulation", "depth-first search"],
        ["parents describes one rooted tree of 2 through 100000 nodes; exactly one parent is -1.",
         "queries has 1 through 30000 pairs [node, value], with value from 0 through 200000.",
         "For each query, maximize value XOR ancestor over the queried node and every ancestor through the root."],
        [([[-1,0,1,1],[[0,2],[3,2],[2,5]]], "The best path values give XOR results two, three, and seven."),
         ([[3,7,-1,2,0,7,0,2],[[4,6],[1,15],[0,5]]], "The best ancestors for the three paths produce six, fourteen, and seven.")],
        [[p,q] for p,q in [([-1,0],[[0,0]]),([-1,0],[[1,0]]),([-1,0],[[1,3]]),([-1,0,0],[[1,2],[2,2]]),
                           ([-1,0,1,2],[[3,7]]),([-1,0,0,1,1],[[3,4],[4,7]]),([2,2,-1],[[0,1],[1,4],[2,3]]),
                           ([-1,0,0,2,2,4],[[5,31],[3,8]]),([-1,0,1,1,3],[[4,0]]),([-1,0,1,2,3,4],[[5,255]]),
                           ([-1,0,0,0],[[1,7],[2,7],[3,7]]),([-1,0,1,0,3],[[2,6],[4,6]]),
                           ([-1,0,1,2,3,4,5,6],[[7,200000]]),([1,-1,1,2],[[3,9],[0,2]])]],
        GENETIC,
        ['''def maximum_genetic_differences(parents, queries):\n    return [node ^ value for node, value in queries]\n''',
         '''def maximum_genetic_differences(parents, queries):\n    return [max(value ^ node for node in range(len(parents))) for _, value in queries]\n'''],
        ["Considers only the queried node and misses better ancestors.", "Uses nodes outside the queried root path."],
        genetic_oracle, random_genetic,
        lesson("During a DFS, the active root-to-current path is exactly the set of legal genetic values.",
               "Maintain those node numbers in a counted binary trie, answering each node's queries before removing it on DFS exit.",
               "Insert on entry; greedily choose the opposite query bit when available; remove on exit.",
               "The trie contains precisely the current ancestors. Greedy opposite-bit choice maximizes the most significant differing bit first, which dominates all lower bits."),
        "O((n+q)*log V)", "O(n*log V+q)", 8),
    1940: entry(
        "common_values_in_sorted_arrays", [("arrays", "list[list[int]]")], "list[int]", ["arrays", "hash maps", "counting"],
        ["arrays contains 2 through 100 arrays.", "Each row has 1 through 100 distinct values in strictly increasing order.",
         "Every value is from 1 through 100; return all values present in every row in increasing order."],
        [([[[1,3,4],[1,4,7,9]]], "Only one and four occur in both sorted arrays."),
         ([[[2,3,6,8],[1,2,3,5,6,7,10],[2,3,4,6,9]]], "Two, three, and six occur in all three arrays.")],
        [[a] for a in [[[1],[1]],[[1],[2]],[[1,2,3],[1,2,3]],[[1,2],[2,3]],[[1,3,5],[2,4,6]],
                       [[1,2,3],[2],[2,4]],[[100],[1,100]],[[1,50,100],[50,100],[50]],
                       [[1,2,4,8],[2,4,8,16],[4,8]],[[3,6,9],[3,6],[3,6,12]],
                       [[1,99],[1,50,99],[1,99]],[[10,20,30],[5,10,15,20,25,30]],
                       [[1,2,3,4,5],[6,7,8]],[[2,3,5,7],[2,3,5,7],[2,3,5,7]]]],
        COMMON,
        [COMMON.replace("== len(arrays)", ">= 1"), COMMON.replace("range(1, 101)", "range(1, 100)")],
        ["Returns the union rather than values shared by every row.", "Never checks value 100."],
        common_oracle, random_common,
        lesson("Strictly increasing rows contain each value at most once, so a global occurrence count equals a row count.",
               "Count every value across all rows and retain exactly those whose count equals the number of rows.",
               "Increment counts per row; scan values one through one hundred in order and emit full-count values.",
               "No row contributes a duplicate, hence count==number of rows is equivalent to membership in every row; the final numeric scan preserves sorted order."),
        "O(total values)", "O(1)", 5),
    1941: entry(
        "equal_character_frequencies", [("s", "str")], "bool", ["strings", "hash maps", "counting"],
        ["s has 1 through 1000 lowercase English letters.", "Compare only characters that actually occur in s.",
         "Return true exactly when all occurring characters have the same frequency."],
        [(["abacbc"], "a, b, and c each occur twice, so the string is good."),
         (["aaabb"], "a occurs three times while b occurs twice, so the string is not good.")],
        [[s] for s in ["a","aa","ab","abc","aabb","aab","zzzz","ababab","abcabcabc","aabbcccd",
                       "qwerty","mississippi","abcdefghijklmnopqrstuvwxyza","bbbccc","xyxyzz"]],
        FREQUENCY,
        [FREQUENCY.replace("== 1", "<= 2"), FREQUENCY.replace("Counter(s).values()", "Counter(s)")],
        ["Allows two different frequencies instead of requiring one.", "Compares the distinct character keys rather than their occurrence counts."],
        frequency_oracle, random_frequency,
        lesson("The actual character identities do not matter after their frequencies are counted.",
               "Build a frequency map and ask whether its values contain exactly one distinct amount.",
               "frequencies=set(Counter(s).values()); return len(frequencies)==1.",
               "Every occurring character contributes one count; one distinct count means all are equal, while two distinct counts exhibit a mismatch."),
        "O(n)", "O(1)", 3),
}
