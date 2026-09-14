"""Prefix ordering, XOR subarrays, interval scheduling, distribution, and matching batch 161."""

from itertools import combinations, permutations

from .import_batch_055 import entry


def prefix_oracle(args):
    nums = args[0]
    return max(
        sum(total > 0 for total in __import__("itertools").accumulate(order))
        for order in set(permutations(nums))
    )


def random_prefix(rng):
    return [[rng.randint(-8, 8) for _ in range(rng.randint(1, 8))]]


def beautiful_oracle(args):
    nums = args[0]
    answer = 0
    for left in range(len(nums)):
        mask = 0
        for right in range(left, len(nums)):
            mask ^= nums[right]
            answer += mask == 0
    return answer


def random_beautiful(rng):
    return [[rng.randint(0, 31) for _ in range(rng.randint(1, 25))]]


def tasks_oracle(args):
    tasks = args[0]
    maximum = max(end for _, end, _ in tasks)
    for count in range(maximum + 2):
        for active in combinations(range(maximum + 1), count):
            chosen = set(active)
            if all(
                sum(second in chosen for second in range(start, end + 1)) >= duration
                for start, end, duration in tasks
            ):
                return count


def random_tasks(rng):
    tasks = []
    for _ in range(rng.randint(1, 8)):
        start = rng.randint(0, 10)
        end = rng.randint(start, 12)
        tasks.append([start, end, rng.randint(1, end - start + 1)])
    return [tasks]


def money_oracle(args):
    money, children = args
    if money < children:
        return -1
    best = -1

    def visit(index, remaining, values):
        nonlocal best
        if index == children - 1:
            if remaining >= 1 and remaining != 4:
                best = max(best, sum(value == 8 for value in values + [remaining]))
            return
        for value in range(1, remaining - (children - index - 1) + 1):
            if value != 4:
                visit(index + 1, remaining - value, values + [value])

    visit(0, money, [])
    return best


def random_money(rng):
    children = rng.randint(1, 5)
    return [rng.randint(1, 20), children]


def greatness_oracle(args):
    nums = args[0]
    n = len(nums)
    best = [0] * (1 << n)
    for mask in range(1 << n):
        index = mask.bit_count()
        if index == n:
            continue
        for chosen in range(n):
            if not mask >> chosen & 1:
                following = mask | (1 << chosen)
                best[following] = max(
                    best[following], best[mask] + (nums[chosen] > nums[index])
                )
    return best[-1]


def random_greatness(rng):
    return [[rng.randint(1, 10) for _ in range(rng.randint(1, 10))]]


PREFIX = """\
def maximum_positive_prefix_score(nums):
    total=answer=0
    for value in sorted(nums,reverse=True):
        total+=value
        if total<=0:break
        answer+=1
    return answer
"""

BEAUTIFUL = """\
def count_beautiful_xor_subarrays(nums):
    counts={0:1};prefix=answer=0
    for value in nums:
        prefix^=value;answer+=counts.get(prefix,0);counts[prefix]=counts.get(prefix,0)+1
    return answer
"""

TASKS = """\
def minimum_active_task_time(tasks):
    tasks=sorted(tasks,key=lambda task:task[1]);active=set()
    for start,end,duration in tasks:
        needed=duration-sum(second in active for second in range(start,end+1))
        second=end
        while needed>0:
            if second not in active:active.add(second);needed-=1
            second-=1
    return len(active)
"""

MONEY = """\
def maximum_eight_dollar_children(money,children):
    if money<children:return -1
    money-=children
    eights=min(children,money//7);money-=eights*7
    if eights==children and money>0:eights-=1
    elif eights==children-1 and money==3:eights-=1
    return eights
"""

GREATNESS = """\
def maximum_array_greatness(nums):
    ordered=sorted(nums);small=0
    for value in ordered:
        if value>ordered[small]:small+=1
    return small
"""


BATCH = {
    2587: entry(
        "maximum_positive_prefix_score",
        [("nums", "list[int]")],
        "int",
        ["arrays", "greedy", "sorting", "prefix sums"],
        [
            "Reorder all integers arbitrarily.",
            "Score the ordering by how many prefix sums are strictly positive.",
            "Return the maximum possible score.",
        ],
        [
            (
                [[2, -1, 0, 1, -3, 3, -3]],
                "Descending order keeps the first six prefix sums positive.",
            ),
            (
                [[-2, -3, 4]],
                "Putting four first makes two prefixes positive before the total becomes negative.",
            ),
        ],
        [
            [a]
            for a in [
                [1],
                [-1],
                [0],
                [1, -1],
                [1, -1, 0],
                [3, -1, -1],
                [-1, -2, -3],
                [5, -2, -2, -2],
                [1, 2, 3, -10],
                [10, -3, -3, -3],
                [4, 0, -1, -2],
                [2, 2, -5, 1],
                [7, -4, 3, -8, 2],
                [5, -1, -1, -1, -1, -1],
            ]
        ],
        PREFIX,
        [
            PREFIX.replace("reverse=True", "reverse=False"),
            PREFIX.replace("total<=0", "total<0"),
        ],
        [
            "Places harmful negative values before larger positive values.",
            "Counts a zero prefix even though prefixes must be strictly positive.",
        ],
        prefix_oracle,
        random_prefix,
        [
            "Sort values descending so every early prefix is as large as possible.",
            "Accumulate until the total becomes nonpositive.",
            "Every later value is no larger, so once a prefix is nonpositive no continuation can restore an additional earlier positive prefix optimally.",
            "The descending order majorizes every other order's prefix sums, making its positive-prefix count maximal.",
        ],
        "O(n log n)",
        "O(n)",
        5,
    ),
    2588: entry(
        "count_beautiful_xor_subarrays",
        [("nums", "list[int]")],
        "int",
        ["arrays", "bit manipulation", "prefix sums", "hash maps"],
        [
            "An operation clears the same set bit from two different elements.",
            "A subarray is beautiful exactly when every bit occurs an even number of times across its elements.",
            "Return the number of beautiful contiguous subarrays.",
        ],
        [
            (
                [[4, 3, 1, 2, 4]],
                "Exactly two subarrays have XOR zero and therefore even parity at every bit.",
            ),
            (
                [[0, 0]],
                "Both one-element zero subarrays and the full subarray are beautiful, giving three.",
            ),
        ],
        [
            [a]
            for a in [
                [0],
                [1],
                [1, 1],
                [1, 2],
                [1, 2, 3],
                [0, 1, 0, 1],
                [2, 2, 2],
                [3, 3, 3, 3],
                [1, 1, 2, 2],
                [4, 1, 5],
                [7, 3, 4, 0],
                [8, 4, 2, 1],
                [5, 5, 0, 5, 5],
                [1, 2, 1, 2, 3, 3],
            ]
        ],
        BEAUTIFUL,
        [
            BEAUTIFUL.replace("counts={0:1}", "counts={}"),
            BEAUTIFUL.replace("prefix^=value", "prefix|=value"),
        ],
        [
            "Fails to seed the empty prefix, losing beautiful subarrays starting at index zero.",
            "Tracks prefix OR rather than bit parity through prefix XOR.",
        ],
        beautiful_oracle,
        random_beautiful,
        [
            "Clearing equal bits in pairs is possible exactly when every bit count is even.",
            "That condition is equivalent to the subarray XOR being zero.",
            "A subarray XOR is zero when the XOR prefixes at its two boundaries are equal.",
            "Count prior occurrences of each running XOR; each match contributes one distinct beautiful subarray.",
        ],
        "O(n)",
        "O(n)",
        6,
    ),
    2589: entry(
        "minimum_active_task_time",
        [("tasks", "list[list[int]]")],
        "int",
        ["intervals", "greedy", "sorting"],
        [
            "Task [start,end,duration] needs at least duration active integer seconds in its inclusive interval.",
            "One active second may satisfy multiple tasks.",
            "Return the minimum number of seconds the computer is active.",
        ],
        [
            (
                [[[2, 3, 1], [4, 5, 1], [1, 5, 2]]],
                "Activating seconds three and five satisfies all three tasks with total time two.",
            ),
            (
                [[[1, 3, 2], [2, 5, 3], [5, 6, 2]]],
                "A minimum schedule uses four active seconds.",
            ),
        ],
        [
            [t]
            for t in [
                [[0, 0, 1]],
                [[1, 2, 1]],
                [[1, 2, 2]],
                [[1, 3, 1], [2, 4, 1]],
                [[1, 3, 2], [2, 4, 2]],
                [[0, 5, 3], [2, 3, 2]],
                [[1, 10, 1], [2, 9, 2], [3, 8, 3]],
                [[0, 2, 2], [3, 5, 2]],
                [[1, 5, 5], [2, 4, 2]],
                [[2, 6, 2], [4, 8, 3]],
                [[0, 4, 2], [1, 3, 3]],
                [[5, 7, 1], [1, 6, 4]],
                [[0, 10, 5], [2, 8, 4], [4, 6, 2]],
                [[1, 4, 2], [2, 5, 2], [3, 6, 2]],
            ]
        ],
        TASKS,
        [
            TASKS.replace("task[1]", "task[0]"),
            TASKS.replace("second=end", "second=start"),
        ],
        [
            "Processes tasks by start rather than deadline, losing the earliest-deadline invariant.",
            "Adds needed time from the interval start instead of its end.",
        ],
        tasks_oracle,
        random_tasks,
        [
            "Process tasks by increasing end time.",
            "Count already-active seconds in the current interval and add only the remaining requirement.",
            "Choose new seconds from the end backward so they are most likely to help later-ending tasks.",
            "An exchange moves any earlier chosen second to a later available second without hurting processed tasks and can only help future tasks, proving greedy optimality.",
        ],
        "O(tasks times time range)",
        "O(time range)",
        8,
    ),
    2591: entry(
        "maximum_eight_dollar_children",
        [("money", "int"), ("children", "int")],
        "int",
        ["math", "greedy"],
        [
            "Distribute all money while every child receives at least one dollar.",
            "No child may receive exactly four dollars.",
            "Return the maximum number receiving exactly eight dollars, or -1 if the minimum distribution is impossible.",
        ],
        [
            (
                [20, 3],
                "After giving everyone one dollar, one child can receive seven more without forcing a four-dollar child.",
            ),
            ([16, 2], "Both children can receive exactly eight dollars."),
        ],
        [
            [m, c]
            for m, c in [
                (1, 1),
                (2, 2),
                (1, 2),
                (4, 1),
                (8, 1),
                (9, 1),
                (8, 2),
                (11, 2),
                (12, 2),
                (15, 2),
                (17, 2),
                (23, 3),
                (24, 3),
                (28, 4),
            ]
        ],
        MONEY,
        [
            MONEY.replace("money<children", "money<=children"),
            MONEY.replace("money==3", "money==4"),
        ],
        [
            "Rejects the valid case where every child receives exactly one dollar.",
            "Handles the forbidden four-dollar remainder at the wrong value.",
        ],
        money_oracle,
        random_money,
        [
            "First reserve one dollar for every child; if that is impossible, return -1.",
            "Use each complete block of seven remaining dollars to raise one child from one to eight.",
            "If all children reached eight but money remains, reduce the count by one; also avoid leaving exactly three extra dollars on the sole non-eight child.",
            "These are the only two boundary corrections because every other remainder can be absorbed without creating a four-dollar child.",
        ],
        "O(1)",
        "O(1)",
        3,
    ),
    2592: entry(
        "maximum_array_greatness",
        [("nums", "list[int]")],
        "int",
        ["arrays", "greedy", "two pointers", "sorting"],
        [
            "Permute nums into a new array using every occurrence exactly once.",
            "Greatness counts positions where the permuted value is strictly greater than the original value.",
            "Return the maximum possible greatness.",
        ],
        [
            (
                [[1, 3, 5, 2, 1, 3, 1]],
                "Four larger values can be matched to four smaller original positions.",
            ),
            (
                [[1, 2, 3, 4]],
                "Values two, three, and four beat one, two, and three respectively, giving greatness three.",
            ),
        ],
        [
            [a]
            for a in [
                [1],
                [1, 1],
                [1, 2],
                [2, 1],
                [1, 2, 3],
                [3, 2, 1],
                [1, 1, 2, 2],
                [5, 5, 5],
                [1, 3, 2, 4],
                [2, 2, 3, 3, 4],
                [1, 10, 1, 10],
                [4, 1, 4, 2, 4],
                [1, 2, 2, 3, 3, 4],
                [7, 1, 7, 2, 7, 3],
            ]
        ],
        GREATNESS,
        [
            GREATNESS.replace("value>ordered[small]", "value>=ordered[small]"),
            GREATNESS.replace("small+=1", "small+=2"),
        ],
        [
            "Counts equal values as successful strictly-greater matches.",
            "Consumes two small targets for each successful large value.",
        ],
        greatness_oracle,
        random_greatness,
        [
            "Sort both the source targets and candidate permuted values.",
            "Scan candidates from smallest upward and match a candidate only when it strictly exceeds the smallest unmatched target.",
            "Advance the target pointer on each successful match.",
            "Using the smallest possible winning candidate preserves all larger candidates, so the greedy matching has maximum cardinality.",
        ],
        "O(n log n)",
        "O(n)",
        5,
    ),
}
