"""Array-operation DP, weighted trees, outliers, and cross-tree target counts."""
from itertools import product

from .import_batch_055 import entry


def minimum_sum_oracle(args):
    nums, k, op1, op2 = args
    choices = []
    for value in nums:
        current = [(value, 0, 0), ((value + 1) // 2, 1, 0)]
        if value >= k:
            current.append((value - k, 0, 1))
            current.append(((value - k + 1) // 2, 1, 1))
        half = (value + 1) // 2
        if half >= k:
            current.append((half - k, 1, 1))
        choices.append(current)
    return min(sum(option[0] for option in selected)
               for selected in product(*choices)
               if sum(option[1] for option in selected) <= op1
               and sum(option[2] for option in selected) <= op2)


def random_minimum_sum(rng):
    size = rng.randint(1, 7)
    return [[rng.randint(0, 20) for _ in range(size)], rng.randint(1, 10),
            rng.randint(0, size), rng.randint(0, size)]


def weighted_tree_oracle(args):
    edges, k = args
    answer = 0
    for mask in range(1 << len(edges)):
        degrees = [0] * (len(edges) + 1)
        total = 0
        for index, (left, right, weight) in enumerate(edges):
            if mask >> index & 1:
                degrees[left] += 1
                degrees[right] += 1
                total += weight
        if max(degrees, default=0) <= k:
            answer = max(answer, total)
    return answer


def random_weighted_tree(rng):
    size = rng.randint(2, 8)
    edges = [[rng.randrange(node), node, rng.randint(1, 20)] for node in range(1, size)]
    rng.shuffle(edges)
    return [edges, rng.randint(1, size - 1)]


def outlier_oracle(args):
    nums = args[0]
    valid = []
    for outlier in range(len(nums)):
        for summed in range(len(nums)):
            if outlier != summed and sum(nums[index] for index in range(len(nums))
                                         if index not in (outlier, summed)) == nums[summed]:
                valid.append(nums[outlier])
    return max(valid)


def random_outlier(rng):
    special = [rng.randint(-8, 8) for _ in range(rng.randint(1, 6))]
    nums = special + [sum(special), rng.randint(-15, 15)]
    rng.shuffle(nums)
    return [nums]


def tree_graph(edges):
    graph = [[] for _ in range(len(edges) + 1)]
    for left, right in edges:
        graph[left].append(right)
        graph[right].append(left)
    return graph


def distances(graph, start):
    result = [-1] * len(graph)
    result[start] = 0
    queue = [start]
    for node in queue:
        for neighbor in graph[node]:
            if result[neighbor] < 0:
                result[neighbor] = result[node] + 1
                queue.append(neighbor)
    return result


def target_one_oracle(args):
    edges1, edges2, k = args
    first = tree_graph(edges1)
    second = tree_graph(edges2)
    answer = []
    for source in range(len(first)):
        best = 0
        for join1 in range(len(first)):
            first_distance = distances(first, source)[join1]
            for join2 in range(len(second)):
                count = sum(value <= k for value in distances(first, source))
                count += sum(first_distance + 1 + value <= k
                             for value in distances(second, join2))
                best = max(best, count)
        answer.append(best)
    return answer


def target_two_oracle(args):
    edges1, edges2 = args
    first = tree_graph(edges1)
    second = tree_graph(edges2)
    answer = []
    for source in range(len(first)):
        best = 0
        source_distances = distances(first, source)
        for join1 in range(len(first)):
            for join2 in range(len(second)):
                count = sum(value % 2 == 0 for value in source_distances)
                offset = source_distances[join1] + 1
                count += sum((offset + value) % 2 == 0
                             for value in distances(second, join2))
                best = max(best, count)
        answer.append(best)
    return answer


def random_tree_edges(rng, size):
    edges = [[rng.randrange(node), node] for node in range(1, size)]
    rng.shuffle(edges)
    return edges


def random_target_one(rng):
    return [random_tree_edges(rng, rng.randint(1, 7)),
            random_tree_edges(rng, rng.randint(1, 7)), rng.randint(0, 5)]


def random_target_two(rng):
    return [random_tree_edges(rng, rng.randint(2, 8)),
            random_tree_edges(rng, rng.randint(2, 8))]


MINIMUM_SUM = '''def minimum_array_sum(nums,k,op1,op2):
    states={(0,0):0}
    for value in nums:
        options=[(value,0,0),((value+1)//2,1,0)]
        if value>=k:
            options.append((value-k,0,1))
            options.append(((value-k+1)//2,1,1))
        half=(value+1)//2
        if half>=k:options.append((half-k,1,1))
        updated={}
        for (used1,used2),total in states.items():
            for result,add1,add2 in options:
                key=(used1+add1,used2+add2)
                if key[0]<=op1 and key[1]<=op2:
                    updated[key]=min(updated.get(key,float('inf')),total+result)
        states=updated
    return min(states.values())
'''

WEIGHTED_TREE = '''def maximum_weight_after_removals(edges,k):
    graph=[[] for _ in range(len(edges)+1)]
    for left,right,weight in edges:
        graph[left].append((right,weight));graph[right].append((left,weight))
    def solve(node,parent):
        base=0;gains=[]
        for child,weight in graph[node]:
            if child==parent:continue
            child_free,child_used=solve(child,node);base+=child_free
            gains.append(weight+child_used-child_free)
        gains.sort(reverse=True);gains=[gain for gain in gains if gain>0]
        return base+sum(gains[:k]),base+sum(gains[:k-1])
    return solve(0,-1)[0]
'''

OUTLIER = '''def largest_array_outlier(nums):
    from collections import Counter
    counts=Counter(nums);total=sum(nums);answer=None
    for candidate in nums:
        remaining=total-candidate
        if remaining%2:continue
        summed=remaining//2
        if counts[summed]-(summed==candidate)>0:
            answer=candidate if answer is None else max(answer,candidate)
    return answer
'''

TARGET_ONE = '''def maximum_distance_targets(edges1,edges2,k):
    def counts(edges,limit):
        graph=[[] for _ in range(len(edges)+1)]
        for left,right in edges:graph[left].append(right);graph[right].append(left)
        answer=[]
        for start in range(len(graph)):
            distance=[-1]*len(graph);distance[start]=0;queue=[start]
            for node in queue:
                for neighbor in graph[node]:
                    if distance[neighbor]<0:
                        distance[neighbor]=distance[node]+1;queue.append(neighbor)
            answer.append(sum(value<=limit for value in distance))
        return answer
    first=counts(edges1,k)
    bonus=max(counts(edges2,k-1)) if k>0 else 0
    return [value+bonus for value in first]
'''

TARGET_TWO = '''def maximum_even_distance_targets(edges1,edges2):
    def colors(edges):
        graph=[[] for _ in range(len(edges)+1)]
        for left,right in edges:graph[left].append(right);graph[right].append(left)
        color=[-1]*len(graph);color[0]=0;queue=[0]
        for node in queue:
            for neighbor in graph[node]:
                if color[neighbor]<0:color[neighbor]=color[node]^1;queue.append(neighbor)
        sizes=[color.count(0),color.count(1)]
        return color,sizes
    first,first_sizes=colors(edges1);second,second_sizes=colors(edges2)
    bonus=max(second_sizes)
    return [first_sizes[color]+bonus for color in first]
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


MINIMUM_CASES = [[nums, k, a, b] for nums, k, a, b in [
    ([0], 1, 0, 0), ([1], 1, 1, 1), ([2], 1, 1, 1), ([10], 5, 1, 1),
    ([8, 3], 3, 1, 1), ([2, 8, 3, 19, 3], 3, 1, 1),
    ([5, 5, 5], 4, 0, 2), ([7, 1, 9], 3, 2, 0), ([6, 6], 4, 2, 2),
    ([1, 2, 3, 4], 8, 4, 4), ([20, 1, 20], 7, 1, 2),
    ([9, 10, 11], 5, 2, 1), ([3, 3, 3], 3, 1, 3), ([4, 15], 6, 1, 1)]]
WEIGHT_CASES = [[edges, k] for edges, k in [
    ([[0, 1, 5]], 1), ([[0, 1, 5], [0, 2, 4]], 1),
    ([[0, 1, 4], [0, 2, 2], [2, 3, 12], [2, 4, 6]], 2),
    ([[0, 1, 1], [1, 2, 10], [1, 3, 9]], 1),
    ([[0, 1, 8], [1, 2, 7], [2, 3, 6]], 1),
    ([[0, 1, 2], [0, 2, 3], [0, 3, 4]], 2),
    ([[0, 1, 20], [1, 2, 1], [1, 3, 1], [3, 4, 20]], 2),
    ([[0, 1, 3], [1, 2, 4], [2, 3, 5], [3, 4, 6]], 3),
    ([[0, 1, 9], [0, 2, 8], [2, 3, 7]], 1),
    ([[0, 1, 1], [0, 2, 2], [0, 3, 3], [0, 4, 4]], 1),
    ([[0, 1, 5], [1, 2, 5], [1, 3, 5], [3, 4, 5]], 2),
    ([[0, 1, 4], [1, 2, 8], [0, 3, 7], [3, 4, 9]], 1),
    ([[0, 1, 2], [1, 2, 3]], 2), ([[0, 1, 6], [0, 2, 5], [2, 3, 4], [2, 4, 3]], 3)]]
OUTLIER_CASES = [[values] for values in [
    [2, 3, 5, 10], [-2, -1, -3, -6, 4], [1, 1, 2, 3], [0, 0, 0],
    [5, 5, 10, 20], [3, 4, 7, -2], [-5, 2, -3, 8], [1, 2, 3, 6, 9],
    [4, 4, 4, 8, 12], [-10, -5, -15, -20], [7, 0, 7, 14],
    [2, 2, 2, 6, 9], [-1, -1, -2, 5], [10, -3, 7, 4]]]
TARGET_ONE_CASES = [[a, b, k] for a, b, k in [
    ([], [], 0), ([], [], 1), ([[0, 1]], [], 1), ([], [[0, 1]], 2),
    ([[0, 1]], [[0, 1]], 1), ([[0, 1], [1, 2]], [[0, 1]], 2),
    ([[0, 1], [0, 2], [2, 3], [2, 4]], [[0, 1], [0, 2], [0, 3], [2, 4], [1, 5], [5, 6], [5, 7]], 2),
    ([[0, 1], [1, 2], [2, 3]], [[0, 1], [1, 2], [1, 3]], 3),
    ([[0, 1], [0, 2], [0, 3]], [[0, 1], [1, 2], [2, 3]], 2),
    ([[0, 1], [1, 2], [1, 3]], [[0, 1], [0, 2], [2, 3]], 1),
    ([[0, 1], [1, 2], [2, 3], [3, 4]], [[0, 1], [0, 2]], 4),
    ([[0, 1], [0, 2]], [[0, 1], [0, 2], [0, 3]], 3),
    ([[0, 1], [1, 2], [2, 3]], [[0, 1], [0, 2], [0, 3], [0, 4]], 2),
    ([[0, 1], [0, 2], [2, 3]], [[0, 1], [1, 2], [2, 3], [3, 4]], 1)]]
TARGET_TWO_CASES = [[a, b] for a, b in [
    ([[0, 1]], [[0, 1]]),
    ([[0, 1], [1, 2]], [[0, 1]]),
    ([[0, 1], [0, 2], [2, 3], [2, 4]], [[0, 1], [0, 2], [0, 3], [2, 4], [1, 5], [5, 6], [5, 7]]),
    ([[0, 1], [1, 2], [2, 3]], [[0, 1], [1, 2], [1, 3]]),
    ([[0, 1], [0, 2], [0, 3]], [[0, 1], [1, 2], [2, 3]]),
    ([[0, 1], [1, 2], [1, 3]], [[0, 1], [0, 2], [2, 3]]),
    ([[0, 1], [1, 2], [2, 3], [3, 4]], [[0, 1], [0, 2]]),
    ([[0, 1], [0, 2]], [[0, 1], [0, 2], [0, 3]]),
    ([[0, 1], [1, 2], [2, 3]], [[0, 1], [0, 2], [0, 3], [0, 4]]),
    ([[0, 1], [0, 2], [2, 3]], [[0, 1], [1, 2], [2, 3], [3, 4]]),
    ([[0, 1], [0, 2], [0, 3], [3, 4]], [[0, 1], [1, 2], [2, 3]]),
    ([[0, 1], [1, 2], [1, 3], [3, 4], [3, 5]], [[0, 1], [0, 2], [2, 3]]),
    ([[0, 1], [0, 2], [2, 3], [3, 4], [3, 5]], [[0, 1], [1, 2], [1, 3], [1, 4]]),
    ([[0, 1], [1, 2], [2, 3], [2, 4]], [[0, 1], [0, 2], [2, 3], [2, 4], [4, 5]])]]


BATCH = {
    3366: entry('minimum_array_sum', [('nums', 'list[int]'), ('k', 'int'), ('op1', 'int'), ('op2', 'int')], 'int',
                ['arrays', 'dynamic programming'],
                ['nums has 1–100 nonnegative integers; k is positive; 0 <= op1, op2 <= len(nums).',
                 'Operation one replaces an element by ceil(value/2), at most once per index and op1 times total.',
                 'Operation two subtracts k from a value at least k, at most once per index and op2 times total; both operations may affect one index in either order.'],
                [([[2, 8, 3, 19, 3], 3, 1, 1], 'Halve 19 to ten and subtract three from eight, reducing the original sum 35 to 23.'),
                 ([[10], 5, 1, 1], 'Halving first gives five, then subtracting five reaches zero.')],
                MINIMUM_CASES, MINIMUM_SUM,
                [MINIMUM_SUM.replace('(value+1)//2', 'value//2'),
                 MINIMUM_SUM.replace("            options.append(((value-k+1)//2,1,1))\n", '').replace("        if half>=k:options.append((half-k,1,1))\n", '')],
                ['Rounds odd halves down instead of up.', 'Never permits both operations on the same index.'],
                minimum_sum_oracle, random_minimum_sum,
                lesson('Each element has a small set of legal outcomes consuming zero or one of each operation.',
                       'Use dynamic programming keyed by how many operations of each type have been spent.',
                       'For every value, enumerate no operation, either operation, and both valid orders; relax the next budget table.',
                       'Every legal global plan chooses one local outcome per index, and the two budget counts contain all cross-index dependence.'),
                'O(n*op1*op2)', 'O(op1*op2)', 6),
    3367: entry('maximum_weight_after_removals', [('edges', 'list[list[int]]'), ('k', 'int')], 'int',
                ['trees', 'dynamic programming', 'greedy'],
                ['edges describes a connected n-node tree with positive weights; 1 <= k < n.',
                 'Remove any edges so every remaining node has degree at most k.',
                 'Return the maximum total weight of retained edges.'],
                [([[[0, 1, 4], [0, 2, 2], [2, 3, 12], [2, 4, 6]], 2], 'Node two has three incident edges, so dropping weight two retains total weight 22.'),
                 ([[[0, 1, 5], [0, 2, 4], [0, 3, 3]], 1], 'At most one star edge may remain; keeping weight five is optimal.')],
                WEIGHT_CASES, WEIGHTED_TREE,
                [WEIGHTED_TREE.replace('return solve(0,-1)[0]', 'return sum(weight for _,_,weight in edges)'),
                 WEIGHTED_TREE.replace('return solve(0,-1)[0]', 'return solve(0,-1)[1]')],
                ['Ignores the degree cap and keeps every edge.', 'Incorrectly reserves a parent-edge slot at the root.'],
                weighted_tree_oracle, random_weighted_tree,
                lesson('A node has k child slots unless its parent edge is retained, when only k-1 remain.',
                       'Compute each child edge’s gain over dropping it and take the largest positive gains that fit.',
                       'Postorder the tree; return values for parent edge absent and present.',
                       'Subtrees interact only through the node degree, so sorting independent marginal gains makes the local choice optimal.'),
                'O(n log n)', 'O(n)', 8),
    3371: entry('largest_array_outlier', [('nums', 'list[int]')], 'int', ['arrays', 'hash maps', 'math'],
                ['nums has at least three integers and contains n-2 special entries, their sum as another entry, and one outlier.',
                 'Values and roles are index-based, so duplicate numeric values may fill different roles.',
                 'Return the largest value that can serve as the outlier.'],
                [([[2, 3, 5, 10]], 'Two and three are special, five is their sum, and ten is the outlier.'),
                 ([[-2, -1, -3, -6, 4]], 'The first three values sum to negative six, leaving four as the outlier.')],
                OUTLIER_CASES, OUTLIER,
                [OUTLIER.replace("counts[summed]-(summed==candidate)>0", "summed in counts"),
                 OUTLIER.replace("answer=candidate if answer is None else max(answer,candidate)", "return candidate")],
                ['Uses one occurrence as both the outlier and sum entry.', 'Returns the first valid outlier rather than the largest.'],
                outlier_oracle, random_outlier,
                lesson('After removing an outlier x, the remaining total must equal twice the designated sum value.',
                       'Test every distinct candidate with a frequency map and preserve separate occurrences when values coincide.',
                       'Let remaining=total-x; if it is even and remaining/2 still occurs, update the maximum x.',
                       'The equation is necessary, and the remaining occurrence check constructs the required sum role, making it sufficient.'),
                'O(n)', 'O(n)', 5),
    3372: entry('maximum_distance_targets', [('edges1', 'list[list[int]]'), ('edges2', 'list[list[int]]'), ('k', 'int')], 'list[int]',
                ['trees', 'breadth-first search', 'graphs'],
                ['Each edge list describes a separate labeled tree; an empty edge list represents one node; k is nonnegative.',
                 'For each first-tree node independently, add one temporary edge between any nodes of the two trees.',
                 'A target lies at distance at most k; maximize the target count for each first-tree source.'],
                [([[[0, 1], [0, 2], [2, 3], [2, 4]], [[0, 1], [0, 2], [0, 3], [2, 7], [1, 4], [4, 5], [4, 6]], 2], 'Choosing the best second-tree endpoint for each query produces counts 9, 7, 9, 8, and 8.'),
                 ([[], [[0, 1]], 1], 'The only first-tree node reaches itself and one chosen second-tree endpoint, totaling two.')],
                TARGET_ONE_CASES, TARGET_ONE,
                [TARGET_ONE.replace('counts(edges2,k-1)', 'counts(edges2,k)'),
                 TARGET_ONE.replace('max(counts(edges2,k-1))', 'counts(edges2,k-1)[0]')],
                ['Forgets that the connecting edge consumes one unit of distance.', 'Always connects at second-tree node zero instead of its best center.'],
                target_one_oracle, random_target_one,
                lesson('The temporary edge separates every target path into a first-tree part, one bridge, and a second-tree part.',
                       'Count each first-tree radius-k neighborhood; the best second-tree radius-(k-1) neighborhood is a shared bonus.',
                       'Run a bounded traversal from every node in both trees, then add the maximum second-tree count to each first-tree count.',
                       'Choosing the first endpoint at the queried node never reduces the second-tree reach, so both optimized terms are independent.'),
                'O(n²+m²)', 'O(n+m)', 6),
    3373: entry('maximum_even_distance_targets', [('edges1', 'list[list[int]]'), ('edges2', 'list[list[int]]')], 'list[int]',
                ['trees', 'graph coloring', 'parity'],
                ['Each edge list describes a separate labeled tree with at least two nodes.',
                 'For each first-tree node independently, add one temporary edge between any nodes of the two trees.',
                 'A target has even path distance from the source; maximize the target count for every first-tree source.'],
                [([[[0, 1], [0, 2], [2, 3], [2, 4]], [[0, 1], [0, 2], [0, 3], [2, 7], [1, 4], [4, 5], [4, 6]]], 'Tree bipartitions give the five optimized totals 8, 7, 7, 8, and 8.'),
                 ([[[0, 1]], [[0, 1]]], 'Each source has one even-distance node in its own tree and can gain one from the other tree.')],
                TARGET_TWO_CASES, TARGET_TWO,
                [TARGET_TWO.replace('bonus=max(second_sizes)', 'bonus=min(second_sizes)'),
                 TARGET_TWO.replace('first_sizes[color]+bonus', 'first_sizes[color^1]+bonus')],
                ['Chooses the smaller second-tree parity class.', 'Counts the opposite parity class in the first tree.'],
                target_two_oracle, random_target_two,
                lesson('Every tree is bipartite, and two nodes have even distance exactly when their colors match.',
                       'Count the two color classes in each tree; bridge endpoints can select the larger second-tree class.',
                       'Two-color both trees; for each first node add its own color-class size and max(second color sizes).',
                       'The bridge flips parity once, while choosing its endpoints lets either second-tree color class become even-distance targets.'),
                'O(n+m)', 'O(n+m)', 8),
}
