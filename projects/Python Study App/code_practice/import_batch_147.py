"""Linked-list, ratio, pairing, and graph workbook batch 147."""

from math import gcd
from .import_batch_055 import entry


def remove_oracle(args):
    values = args[0]
    answer = []
    largest = -(10**30)
    for value in reversed(values):
        if value >= largest:
            answer.append(value)
            largest = value
    return answer[::-1]


def random_remove(rng):
    return [[rng.randint(0, 50) for _ in range(rng.randint(0, 30))]]


def ratio_oracle(args):
    text, zero_ratio, one_ratio = args
    answer = 0
    for left in range(len(text)):
        zeros = ones = 0
        for char in text[left:]:
            zeros += char == "0"
            ones += char == "1"
            answer += zeros * one_ratio == ones * zero_ratio
    return answer


def random_ratio(rng):
    a, b = rng.sample(range(1, 8), 2)
    while gcd(a, b) != 1:
        a, b = rng.sample(range(1, 8), 2)
    return ["".join(rng.choice("01") for _ in range(rng.randint(1, 30))), a, b]


def players_oracle(args):
    skills = args[0]

    def search(values, target):
        if not values:
            return 0
        first = values[0]
        best = None
        for index in range(1, len(values)):
            if first + values[index] == target:
                result = search(values[1:index] + values[index + 1 :], target)
                if result is not None:
                    best = first * values[index] + result
                    break
        return best

    total = sum(skills)
    pairs = len(skills) // 2
    if total % pairs:
        return -1
    result = search(list(skills), total // pairs)
    return result if result is not None else -1


def random_players(rng):
    n = 2 * rng.randint(1, 5)
    return [[rng.randint(1, 15) for _ in range(n)]]


def score_oracle(args):
    n, roads = args
    graph = [[] for _ in range(n + 1)]
    for a, b, w in roads:
        graph[a].append((b, w))
        graph[b].append((a, w))
    seen = {1}
    stack = [1]
    answer = 10**30
    while stack:
        node = stack.pop()
        for neighbor, weight in graph[node]:
            answer = min(answer, weight)
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return answer


def random_score(rng):
    n = rng.randint(2, 20)
    roads = [
        [node + 1, rng.randrange(node) + 1, rng.randint(1, 50)] for node in range(1, n)
    ]
    return [n, roads]


def even_oracle(args):
    nums = args[0]
    answer = 0
    for left in range(len(nums)):
        product = 1
        for value in nums[left:]:
            product *= value
            answer += product % 2 == 0
    return answer


def random_even(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(1, 40))]]


REMOVE = """\
def remove_nodes_with_larger_right(head):
    if head is None:return None
    head.next=remove_nodes_with_larger_right(head.next)
    if head.next is not None and head.val<head.next.val:return head.next
    return head
"""
RATIO = """\
def count_fixed_ratio_substrings(s,num1,num2):
    counts={0:1};zeros=ones=answer=0
    for character in s:
        zeros+=character=='0';ones+=character=='1'
        balance=ones*num1-zeros*num2
        answer+=counts.get(balance,0);counts[balance]=counts.get(balance,0)+1
    return answer
"""
PLAYERS = """\
def equal_skill_pair_chemistry(skill):
    values=sorted(skill);target=values[0]+values[-1];answer=0
    for left in range(len(values)//2):
        right=len(values)-1-left
        if values[left]+values[right]!=target:return -1
        answer+=values[left]*values[right]
    return answer
"""
SCORE = """\
def minimum_path_score(n,roads):
    graph=[[] for _ in range(n+1)]
    for left,right,distance in roads:graph[left].append((right,distance));graph[right].append((left,distance))
    seen={1};stack=[1];answer=10**30
    while stack:
        node=stack.pop()
        for neighbor,distance in graph[node]:
            answer=min(answer,distance)
            if neighbor not in seen:seen.add(neighbor);stack.append(neighbor)
    return answer
"""
EVEN = """\
def count_even_product_subarrays(nums):
    last_even=-1;answer=0
    for index,value in enumerate(nums):
        if value%2==0:last_even=index
        answer+=last_even+1
    return answer
"""

BATCH = {
    2487: entry(
        "remove_nodes_with_larger_right",
        [("head", "ListNode | None")],
        "ListNode | None",
        ["linked lists", "recursion", "monotonic stacks"],
        [
            "Remove every node having a strictly larger node somewhere to its right.",
            "Equal values do not remove one another.",
            "Return the head of the surviving nodes in original relative order, reusing input nodes.",
        ],
        [
            (
                [[5, 2, 13, 3, 8]],
                "Nodes 5 and 2 are removed by 13, and 3 is removed by 8, leaving [13,8].",
            ),
            (
                [[1, 1, 1]],
                "No node has a strictly larger value to its right, so all equal nodes remain.",
            ),
        ],
        [
            [x]
            for x in [
                [],
                [1],
                [1, 2],
                [2, 1],
                [1, 1],
                [3, 2, 1],
                [1, 2, 3],
                [5, 2, 13, 3, 8],
                [10, 5, 6, 4],
                [2, 7, 4, 3, 5],
                [9, 1, 8, 2, 7],
                [0, 0, 1],
                [4, 3, 4, 2],
                [6, 1, 2, 3, 0],
            ]
        ],
        REMOVE,
        [
            REMOVE.replace("head.val<head.next.val", "head.val<=head.next.val"),
            REMOVE.replace(
                "return head.next", "return head.next.next if head.next else None"
            ),
        ],
        [
            "Incorrectly removes equal-valued nodes.",
            "Skips an extra surviving node whenever removing the current node.",
        ],
        remove_oracle,
        random_remove,
        [
            "Process the suffix before deciding whether the current node survives.",
            "After recursion, head.next points to the first surviving suffix node, which is the suffix maximum frontier.",
            "Remove head exactly when that next value is strictly larger; otherwise keep it.",
            "The recursively filtered suffix starts with its maximum value, so comparing against that one node is equivalent to comparing against every original node to the right.",
        ],
        "O(n)",
        "O(n) recursion",
        6,
    ),
    2489: entry(
        "count_fixed_ratio_substrings",
        [("s", "str"), ("num1", "int"), ("num2", "int")],
        "int",
        ["strings", "prefix sums", "hash maps"],
        [
            "num1 and num2 are positive and coprime.",
            "Count nonempty contiguous substrings whose number of zeroes to ones equals num1:num2.",
            "Return the total number of qualifying substrings.",
        ],
        [
            (
                ["0110011", 1, 2],
                "Four substrings contain zeroes and ones in the ratio one to two.",
            ),
            (
                ["01", 1, 1],
                "The complete string has one zero and one one, so exactly one substring qualifies.",
            ),
        ],
        [
            [s, a, b]
            for s, a, b in [
                ("0", 1, 1),
                ("1", 1, 1),
                ("01", 1, 1),
                ("001", 2, 1),
                ("011", 1, 2),
                ("0011", 1, 1),
                ("0101", 1, 1),
                ("000111", 1, 1),
                ("001011", 2, 3),
                ("1110000111", 2, 3),
                ("101010", 1, 2),
                ("00011", 3, 2),
                ("1100", 1, 1),
                ("0100110", 2, 1),
            ]
        ],
        RATIO,
        [
            RATIO.replace("ones*num1-zeros*num2", "ones*num2-zeros*num1"),
            RATIO.replace("counts={0:1}", "counts={}"),
        ],
        [
            "Cross-multiplies the ratio components in the wrong positions.",
            "Omits the empty prefix and loses substrings beginning at index zero.",
        ],
        ratio_oracle,
        random_ratio,
        [
            "For each prefix, track zero and one counts.",
            "A substring has the target ratio when the endpoint prefixes share balance ones*num1-zeroes*num2.",
            "Count previous occurrences of the current balance, seeding balance zero for the empty prefix.",
            "Equal balances cancel to zero cross-product difference, which is exactly the required ratio equation.",
        ],
        "O(n)",
        "O(n)",
        5,
    ),
    2491: entry(
        "equal_skill_pair_chemistry",
        [("skill", "list[int]")],
        "int",
        ["arrays", "sorting", "two pointers"],
        [
            "Pair every player exactly once, with all pairs required to have the same skill sum.",
            "A pair’s chemistry is the product of its two skills.",
            "Return total chemistry, or -1 if equal-sum pairing is impossible.",
        ],
        [
            (
                [[3, 2, 5, 1, 3, 4]],
                "Sorted extremes pair as (1,5), (2,4), and (3,3), each summing to six; chemistry totals 5+8+9=22.",
            ),
            (
                [[1, 1, 2, 3]],
                "No pairing can give every pair the same sum, so return -1.",
            ),
        ],
        [
            [x]
            for x in [
                [1, 1],
                [1, 2],
                [2, 2, 2, 2],
                [1, 4, 2, 3],
                [1, 1, 1, 1],
                [1, 2, 3, 4],
                [1, 2, 2, 3],
                [5, 1, 5, 1],
                [10, 2, 8, 4, 6, 6],
                [3, 3, 3, 3, 3, 3],
                [1, 5, 2, 4, 3, 3],
                [1, 1, 2, 2, 3, 3],
                [9, 1, 8, 2],
                [7, 4, 5, 6, 3, 8],
            ]
        ],
        PLAYERS,
        [
            PLAYERS.replace("values[0]+values[-1]", "values[0]+values[1]"),
            PLAYERS.replace(
                "answer+=values[left]*values[right]",
                "answer+=values[left]+values[right]",
            ),
        ],
        [
            "Uses the two smallest skills to define the target instead of opposite extremes.",
            "Adds pair skills rather than multiplying them for chemistry.",
        ],
        players_oracle,
        random_players,
        [
            "Sort skills and pair the smallest remaining value with the largest remaining value.",
            "Their sum fixes the only possible common target.",
            "Verify every inward pair has that sum while accumulating products.",
            "In any equal-sum pairing the global smallest must pair with the global largest; removing them repeats the same forced argument.",
        ],
        "O(n log n)",
        "O(n)",
        5,
    ),
    2492: entry(
        "minimum_path_score",
        [("n", "int"), ("roads", "list[list[int]]")],
        "int",
        ["graphs", "depth-first search"],
        [
            "Roads are undirected and at least one path connects city 1 to city n.",
            "A path may repeat vertices and roads; its score is the minimum road distance used.",
            "Return the smallest score achievable by any path from 1 to n.",
        ],
        [
            (
                [4, [[1, 2, 9], [2, 3, 6], [2, 4, 5], [1, 4, 7]]],
                "All cities are connected to city 1, and the smallest road in that component has distance five, which can be included in a walk to city 4.",
            ),
            ([2, [[1, 2, 10]]], "The sole road is required, so the path score is ten."),
        ],
        [
            [n, r]
            for n, r in [
                (2, [[2, 1, 1]]),
                (3, [[1, 2, 5], [2, 3, 7]]),
                (3, [[1, 3, 9], [1, 2, 2]]),
                (4, [[1, 2, 8], [2, 4, 6], [1, 3, 1]]),
                (4, [[1, 2, 3], [2, 3, 4], [3, 4, 5]]),
                (5, [[1, 2, 10], [2, 5, 9], [2, 3, 1], [3, 4, 2]]),
                (3, [[1, 2, 4], [2, 3, 4], [1, 3, 8]]),
                (5, [[1, 5, 20], [1, 2, 7], [2, 3, 6], [3, 4, 5]]),
                (4, [[1, 2, 2], [2, 3, 2], [3, 4, 2]]),
                (6, [[1, 2, 9], [2, 6, 8], [2, 3, 7], [3, 4, 1], [4, 5, 2]]),
                (3, [[1, 2, 100], [2, 3, 1]]),
                (4, [[1, 4, 7], [2, 3, 1]]),
                (5, [[1, 2, 4], [2, 5, 6], [3, 4, 1]]),
                (4, [[1, 2, 9], [1, 3, 8], [3, 4, 7], [2, 4, 6]]),
            ]
        ],
        SCORE,
        [
            SCORE.replace("answer=min(answer,distance)", "answer=max(answer,distance)"),
            SCORE.replace("graph[right].append((left,distance))", ""),
        ],
        [
            "Tracks the largest component edge instead of the smallest.",
            "Treats the undirected roads as one-way edges and can miss reachable cities.",
        ],
        score_oracle,
        random_score,
        [
            "Traverse the entire connected component containing city 1.",
            "Track the minimum distance of every incident road seen in that component.",
            "Because walks may repeat edges, a route from 1 can detour through the minimum edge and then continue to n.",
            "Thus every component edge can determine an achievable score, and no path can score below the minimum component edge.",
        ],
        "O(n+roads)",
        "O(n)",
        5,
    ),
    2495: entry(
        "count_even_product_subarrays",
        [("nums", "list[int]")],
        "int",
        ["arrays", "dynamic programming"],
        [
            "Count nonempty contiguous subarrays.",
            "A product is even exactly when the subarray contains at least one even value.",
            "Return the number of subarrays with even product.",
        ],
        [
            (
                [[9, 6, 7, 13]],
                "Every subarray containing the 6 is even; there are two starts and three ends around it, giving six.",
            ),
            ([[1, 3, 5]], "No subarray contains an even value, so the answer is zero."),
        ],
        [
            [x]
            for x in [
                [2],
                [1],
                [2, 2],
                [1, 2],
                [2, 1],
                [1, 1, 2],
                [2, 1, 1],
                [1, 2, 1],
                [2, 4, 6],
                [1, 3, 5],
                [0, 1],
                [1, 0, 1],
                [7, 8, 9, 10],
                [2, 1, 2, 1],
            ]
        ],
        EVEN,
        [
            EVEN.replace("last_even=index", "last_even=index-1"),
            EVEN.replace("value%2==0", "value%2==1"),
        ],
        [
            "Records the even position one index too early and undercounts starts.",
            "Treats odd values as the trigger for an even product.",
        ],
        even_oracle,
        random_even,
        [
            "Track the most recent index containing an even value.",
            "For each ending index, every start from zero through that recent even index forms an even-product subarray.",
            "Add last_even+1 to the answer at each end.",
            "These are exactly the subarrays ending here that include an even factor, so summing over ends counts each qualifying subarray once.",
        ],
        "O(n)",
        "O(1)",
        3,
    ),
}
BATCH[2487]["params"][0] = ("head", "ListNode | None", "listnode")
BATCH[2487]["adapter"] = "listnode"
