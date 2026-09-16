"""Tree rerooting batch: independently checked distance sums."""

from collections import deque
from .import_batch_003 import entry


def distance_sum_oracle(arguments):
    count, edges = arguments
    graph = [[] for _ in range(count)]
    for left, right in edges:
        graph[left].append(right)
        graph[right].append(left)
    result = []
    for root in range(count):
        distance = [-1] * count
        distance[root] = 0
        queue = deque([root])
        while queue:
            node = queue.popleft()
            for neighbor in graph[node]:
                if distance[neighbor] < 0:
                    distance[neighbor] = distance[node] + 1
                    queue.append(neighbor)
        result.append(sum(distance))
    return result


def random_tree(rng):
    count = rng.randint(1, 9)
    edges = [[node, rng.randrange(node)] for node in range(1, count)]
    rng.shuffle(edges)
    return [count, edges]


def tree_case(parents):
    return [len(parents) + 1, [[node, parent] for node, parent in enumerate(parents, 1)]]


REFERENCE = '''def sum_of_distances_in_tree(n, edges):
    graph=[[] for _ in range(n)]
    for left,right in edges:
        graph[left].append(right)
        graph[right].append(left)
    parent=[-1]*n
    parent[0]=0
    order=[0]
    for node in order:
        for neighbor in graph[node]:
            if neighbor!=parent[node]:
                parent[neighbor]=node
                order.append(neighbor)
    subtree_size=[1]*n
    answer=[0]*n
    for node in reversed(order[1:]):
        previous=parent[node]
        subtree_size[previous]+=subtree_size[node]
        answer[previous]+=answer[node]+subtree_size[node]
    for node in order[1:]:
        answer[node]=answer[parent[node]]+n-2*subtree_size[node]
    return answer
'''


HIDDEN = [tree_case(parents) for parents in (
    [], [0], [0, 0], [0, 1, 2], [0, 0, 0], [0, 0, 1, 1],
    [0, 1, 2, 3], [0, 0, 0, 0, 0], [0, 0, 1, 1, 2],
    [0, 1, 2, 3, 4, 5], [0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 2, 2, 4],
)]


CHAIN_LENGTH = 1000
CHAIN = [[node - 1, node] for node in range(1, CHAIN_LENGTH)]
CHAIN_EXPECTED = [
    index * (index + 1) // 2
    + (CHAIN_LENGTH - index - 1) * (CHAIN_LENGTH - index) // 2
    for index in range(CHAIN_LENGTH)
]


BATCH = {
    834: entry(
        name='sum_of_distances_in_tree',
        params=[('n', 'int'), ('edges', 'list[list[int]]')],
        returns='list[int]',
        topics=['trees', 'graphs', 'depth first search', 'dynamic programming'],
        constraints=[
            'n is 1 through 100,000, with nodes numbered zero through n-1.',
            'edges contains exactly n-1 undirected edges forming one connected tree.',
            'Return one distance sum per node in numeric node order.',
        ],
        examples=[
            ([6, [[0, 1], [0, 2], [2, 3], [2, 4], [2, 5]]],
             'From node zero the distances are 0,1,1,2,2,2, summing to eight; rerooting gives [8,12,6,10,10,10].'),
            ([3, [[0, 1], [1, 2]]],
             'The two endpoints each have distances 0,1,2 (sum three); the middle node has sum two.'),
        ],
        hidden=HIDDEN,
        reference=REFERENCE,
        wrong=[
            REFERENCE.replace(
                'answer[node]=answer[parent[node]]+n-2*subtree_size[node]',
                'answer[node]=answer[parent[node]]'),
            REFERENCE.replace(
                'answer[node]=answer[parent[node]]+n-2*subtree_size[node]',
                'answer[node]=answer[parent[node]]+n-subtree_size[node]'),
        ],
        reasons=[
            'Computes the root sum but never adjusts it when moving the root to another node.',
            'Subtracts the child subtree only once; rerooting must remove and add its contribution.',
        ],
        oracle=distance_sum_oracle,
        generator=random_tree,
        hints=[
            'First compute every subtree size and the distance sum from node zero.',
            'A bottom-up pass gives the root sum; a top-down pass can then move the root across each edge.',
            'Moving into a child makes its subtree nodes one step closer and all other nodes one step farther: new = old + n - 2*subtree_size[child].',
            'An iterative traversal avoids Python recursion depth limits on long chains; the two passes each visit every edge a constant number of times.',
        ],
        editorial=(
            'Build a parent-first traversal of the tree. Reverse it to accumulate subtree sizes and the sum of distances from node zero. '
            'For each parent-to-child edge, reroot: the child subtree becomes one edge closer while all remaining nodes become one edge farther. '
            'Thus answer[child] = answer[parent] + n - 2*subtree_size[child]. Both passes are linear and use no recursive call stack.'
        ),
        time='O(n)',
        space='O(n)',
        difficulty=8,
        stress=[([CHAIN_LENGTH, CHAIN], CHAIN_EXPECTED)],
    ),
}
