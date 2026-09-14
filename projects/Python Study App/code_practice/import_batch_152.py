"""Heap, counting, dynamic-programming, and event-simulation workbook batch 152."""

from collections import Counter, deque
from functools import lru_cache
from itertools import product

from .import_batch_055 import entry


def score_oracle(args):
    nums, k = args

    @lru_cache(None)
    def visit(state, steps):
        if not steps:
            return 0
        return max(
            value
            + visit(
                tuple(sorted(state[:index] + ((value + 2) // 3,) + state[index + 1 :])),
                steps - 1,
            )
            for index, value in enumerate(state)
        )

    return visit(tuple(sorted(nums)), k)


def random_score(rng):
    return [
        [rng.randint(1, 30) for _ in range(rng.randint(1, 6))],
        rng.randint(1, 8),
    ]


def swap_oracle(args):
    first, second = args
    for i in range(len(first)):
        for j in range(len(second)):
            a = list(first)
            b = list(second)
            a[i], b[j] = b[j], a[i]
            if len(set(a)) == len(set(b)):
                return True
    return False


def random_swap(rng):
    return [
        "".join(rng.choice("abcde") for _ in range(rng.randint(1, 8))),
        "".join(rng.choice("abcde") for _ in range(rng.randint(1, 8))),
    ]


def bridge_oracle(args):
    boxes, _, times = args
    total_boxes = boxes
    waiting_left = set(range(len(times)))
    waiting_right = set()
    busy_left = []
    busy_right = []
    delivered = 0
    now = 0

    def priority(worker):
        return times[worker][0] + times[worker][2], worker

    while True:
        newly_left = [(ready, worker) for ready, worker in busy_left if ready <= now]
        busy_left = [(ready, worker) for ready, worker in busy_left if ready > now]
        waiting_left.update(worker for _, worker in newly_left)
        newly_right = [(ready, worker) for ready, worker in busy_right if ready <= now]
        busy_right = [(ready, worker) for ready, worker in busy_right if ready > now]
        waiting_right.update(worker for _, worker in newly_right)
        if waiting_right:
            worker = max(waiting_right, key=priority)
            waiting_right.remove(worker)
            now += times[worker][2]
            delivered += 1
            if delivered == total_boxes:
                return now
            busy_left.append((now + times[worker][3], worker))
        elif boxes and waiting_left:
            worker = max(waiting_left, key=priority)
            waiting_left.remove(worker)
            now += times[worker][0]
            boxes -= 1
            busy_right.append((now + times[worker][1], worker))
        else:
            now = min(ready for ready, _ in busy_left + busy_right)


def random_bridge(rng):
    workers = rng.randint(1, 4)
    return [
        rng.randint(1, 5),
        workers,
        [[rng.randint(1, 5) for _ in range(4)] for _ in range(workers)],
    ]


def good_oracle(args):
    low, high, one, zero = args
    answer = 0
    for length in range(low, high + 1):
        for bits in product("01", repeat=length):
            text = "".join(bits)
            runs = []
            start = 0
            for index in range(1, length + 1):
                if index == length or text[index] != text[start]:
                    runs.append((text[start], index - start))
                    start = index
            if all(size % (one if bit == "1" else zero) == 0 for bit, size in runs):
                answer += 1
    return answer % (10**9 + 7)


def random_good(rng):
    high = rng.randint(1, 11)
    return [rng.randint(1, high), high, rng.randint(1, 5), rng.randint(1, 5)]


def door_oracle(args):
    arrival, state = args
    queues = [deque(), deque()]
    answer = [0] * len(arrival)
    index = 0
    now = 0
    previous = 1
    while index < len(arrival) or queues[0] or queues[1]:
        if (
            not queues[0]
            and not queues[1]
            and index < len(arrival)
            and arrival[index] > now
        ):
            now = arrival[index]
            previous = 1
        while index < len(arrival) and arrival[index] <= now:
            queues[state[index]].append(index)
            index += 1
        direction = previous if queues[previous] else 1 - previous
        person = queues[direction].popleft()
        answer[person] = now
        previous = direction
        now += 1
    return answer


def random_door(rng):
    count = rng.randint(1, 20)
    arrival = []
    now = 0
    for _ in range(count):
        now += rng.randint(0, 3)
        arrival.append(now)
    return [arrival, [rng.randint(0, 1) for _ in range(count)]]


SCORE = """\
def maximum_replacement_score(nums,k):
    import heapq
    heap=[-value for value in nums];heapq.heapify(heap);score=0
    for _ in range(k):
        value=-heapq.heappop(heap);score+=value
        heapq.heappush(heap,-((value+2)//3))
    return score
"""

SWAP = """\
def can_equalize_distinct_counts(word1,word2):
    first={char:word1.count(char) for char in set(word1)}
    second={char:word2.count(char) for char in set(word2)}
    for left,left_count in first.items():
        for right,right_count in second.items():
            if left==right:
                if len(first)==len(second):return True
            else:
                new_first=len(first)-(left_count==1)+(right not in first)
                new_second=len(second)-(right_count==1)+(left not in second)
                if new_first==new_second:return True
    return False
"""

BRIDGE = """\
def last_box_bridge_time(n,k,time):
    import heapq
    priority=lambda worker:(-(time[worker][0]+time[worker][2]),-worker)
    left=[priority(worker) for worker in range(k)];heapq.heapify(left)
    right=[];busy_left=[];busy_right=[];now=0;delivered=0;total=n
    while delivered<total:
        while busy_left and busy_left[0][0]<=now:
            _,worker=heapq.heappop(busy_left);heapq.heappush(left,priority(worker))
        while busy_right and busy_right[0][0]<=now:
            _,worker=heapq.heappop(busy_right);heapq.heappush(right,priority(worker))
        if right:
            _,negative=heapq.heappop(right);worker=-negative
            now+=time[worker][2];delivered+=1
            if delivered==total:return now
            heapq.heappush(busy_left,(now+time[worker][3],worker))
        elif n and left:
            _,negative=heapq.heappop(left);worker=-negative
            now+=time[worker][0];n-=1
            heapq.heappush(busy_right,(now+time[worker][1],worker))
        else:
            ready=[]
            if busy_left:ready.append(busy_left[0][0])
            if busy_right:ready.append(busy_right[0][0])
            now=max(now,min(ready))
"""

GOOD = """\
def count_good_binary_strings(min_length,max_length,one_group,zero_group):
    modulus=10**9+7;ways=[0]*(max_length+1);ways[0]=1
    for length in range(1,max_length+1):
        if length>=one_group:ways[length]+=ways[length-one_group]
        if length>=zero_group:ways[length]+=ways[length-zero_group]
        ways[length]%=modulus
    return sum(ways[min_length:])%modulus
"""

DOOR = """\
def door_crossing_times(arrival,state):
    from collections import deque
    queues=[deque(),deque()];answer=[0]*len(arrival);index=0;now=0;previous=1
    while index<len(arrival) or queues[0] or queues[1]:
        if not queues[0] and not queues[1] and index<len(arrival) and now<arrival[index]:now=arrival[index];previous=1
        while index<len(arrival) and arrival[index]<=now:queues[state[index]].append(index);index+=1
        direction=previous if queues[previous] else 1-previous
        answer[queues[direction].popleft()]=now;previous=direction;now+=1
    return answer
"""


BATCH = {
    2530: entry(
        "maximum_replacement_score",
        [("nums", "list[int]"), ("k", "int")],
        "int",
        ["arrays", "greedy", "heaps"],
        [
            "Perform exactly k operations, choosing one current array value each time.",
            "Add the chosen value to the score, then replace it with ceiling(value/3).",
            "Return the maximum achievable score.",
        ],
        [
            (
                [[10, 10, 10, 10, 10], 5],
                "Taking each ten once produces the maximum total fifty.",
            ),
            (
                [[1, 10, 3, 3, 3], 3],
                "Greedily taking 10, then 4, then 3 yields score 17.",
            ),
        ],
        [
            [a, k]
            for a, k in [
                ([1], 1),
                ([1], 5),
                ([2], 3),
                ([3], 3),
                ([4], 3),
                ([1, 2], 2),
                ([5, 5], 3),
                ([9, 1], 4),
                ([2, 8, 4], 3),
                ([100, 1, 1], 5),
                ([6, 7, 8], 6),
                ([1, 1, 1, 1], 7),
                ([20, 10, 5, 2], 8),
                ([3, 9, 27], 6),
            ]
        ],
        SCORE,
        [
            SCORE.replace("(value+2)//3", "value//3"),
            SCORE.replace("-value", "value", 1),
        ],
        [
            "Rounds the replacement down instead of up.",
            "Builds a min-heap and repeatedly chooses the smallest value.",
        ],
        score_oracle,
        random_score,
        [
            "The current largest value always gives the greatest immediate score.",
            "Choosing a smaller value cannot improve its replacement enough to overtake choosing the larger one first.",
            "Store negated values in a Python min-heap, pop one maximum, and push its ceiling-divided replacement.",
            "An exchange argument moves the largest available choice before any smaller choice without reducing either current or future score.",
        ],
        "O((n+k) log n)",
        "O(n)",
        5,
    ),
    2531: entry(
        "can_equalize_distinct_counts",
        [("word1", "str"), ("word2", "str")],
        "bool",
        ["strings", "hash maps", "counting"],
        [
            "Perform exactly one swap between one character position in each nonempty word.",
            "After the swap, compare the numbers of distinct characters in the two words.",
            "Return whether some allowed swap makes those counts equal.",
        ],
        [
            (
                ["ac", "b"],
                "Any swap leaves the first word with two distinct characters and the second with one.",
            ),
            (
                ["abcc", "aab"],
                "Swapping c from the first word with a from the second leaves two distinct characters in each.",
            ),
        ],
        [
            [a, b]
            for a, b in [
                ("a", "a"),
                ("a", "b"),
                ("ab", "cd"),
                ("aa", "b"),
                ("abc", "a"),
                ("aabb", "ccdd"),
                ("abc", "defg"),
                ("aaaa", "bc"),
                ("abca", "zz"),
                ("xyz", "xy"),
                ("aab", "bcc"),
                ("abcde", "aabb"),
                ("qwert", "qqqq"),
                ("abac", "cddd"),
            ]
        ],
        SWAP,
        [
            SWAP.replace("if left==right:", "if left!=right:"),
            SWAP.replace("(left_count==1)", "(left_count>1)"),
        ],
        [
            "Uses the unchanged-count shortcut for different swapped characters.",
            "Removes a distinct character when multiple copies remain.",
        ],
        swap_oracle,
        random_swap,
        [
            "Only character frequencies matter, not the positions selected.",
            "Try every distinct character present in the first word against every distinct character in the second.",
            "For different characters, a distinct count falls only when the removed frequency was one and rises only when the received character was absent.",
            "The alphabet is bounded, so enumerating frequency-map keys covers every positional swap while avoiding repeated equivalent work.",
        ],
        "O(n+m+alphabet squared)",
        "O(alphabet)",
        5,
    ),
    2532: entry(
        "last_box_bridge_time",
        [("n", "int"), ("k", "int"), ("time", "list[list[int]]")],
        "int",
        ["simulation", "heaps", "event queues"],
        [
            "Each worker row gives left-to-right, pick, right-to-left, and put times.",
            "When the bridge is free, a waiting right-side worker goes first; otherwise dispatch a left worker only while boxes remain.",
            "Within one side choose the least efficient worker: greatest crossing-time sum, breaking ties by greatest original index.",
            "Return when the final box finishes crossing back to the left; its put time is not included.",
        ],
        [
            (
                [1, 3, [[1, 1, 2, 1], [1, 1, 3, 1], [1, 1, 4, 1]]],
                "Worker two is least efficient and returns the only box at time six.",
            ),
            (
                [3, 2, [[1, 9, 1, 8], [10, 10, 10, 10]]],
                "Following right-side priority and worker efficiency delivers the third box at time fifty.",
            ),
        ],
        [
            [n, len(t), t]
            for n, t in [
                (1, [[1, 1, 1, 1]]),
                (2, [[1, 1, 1, 1]]),
                (3, [[2, 1, 3, 1]]),
                (1, [[1, 2, 3, 4], [2, 1, 2, 1]]),
                (2, [[1, 2, 3, 4], [2, 1, 2, 1]]),
                (4, [[1, 1, 1, 1], [2, 2, 2, 2]]),
                (3, [[5, 1, 1, 1], [1, 1, 5, 1]]),
                (5, [[1, 3, 2, 4], [2, 1, 3, 2], [3, 2, 1, 3]]),
                (2, [[4, 4, 4, 4], [4, 4, 4, 4]]),
                (6, [[1, 2, 1, 2], [2, 1, 2, 1]]),
                (3, [[10, 1, 1, 10], [1, 10, 10, 1]]),
                (7, [[2, 3, 4, 5], [5, 4, 3, 2], [1, 1, 1, 1]]),
                (4, [[3, 1, 7, 2], [4, 2, 6, 1], [5, 1, 5, 3]]),
                (8, [[1, 5, 2, 6], [2, 4, 3, 5], [3, 3, 4, 4], [4, 2, 5, 3]]),
            ]
        ],
        BRIDGE,
        [
            BRIDGE.replace("if right:", "if right and not (n and left):"),
            BRIDGE.replace("-worker)", "worker)"),
        ],
        [
            "Dispatches another left-side worker while a right-side worker is waiting with a box.",
            "Breaks efficiency ties in favor of the smaller worker index.",
        ],
        bridge_oracle,
        random_bridge,
        [
            "Separate waiting workers on each bank from workers still picking or putting a box.",
            "Use availability-time min-heaps for busy workers and priority heaps for waiting workers.",
            "At each bridge-free time, release completed work, prefer the right queue, and otherwise dispatch left only if an unassigned box remains.",
            "Event jumps skip idle time, and the queue priorities exactly implement the stated policy; the final right-to-left crossing determines the answer.",
        ],
        "O((n+k) log k)",
        "O(k)",
        8,
    ),
    2533: entry(
        "count_good_binary_strings",
        [
            ("min_length", "int"),
            ("max_length", "int"),
            ("one_group", "int"),
            ("zero_group", "int"),
        ],
        "int",
        ["dynamic programming", "strings", "counting"],
        [
            "Begin with an empty string and repeatedly append either one_group ones or zero_group zeros.",
            "Count constructible binary strings whose lengths lie from min_length through max_length inclusive.",
            "Return the count modulo 1,000,000,007.",
        ],
        [
            ([2, 3, 1, 2], "The constructible strings are 11, 00, 111, 100, and 001."),
            ([4, 4, 4, 3], "Only the block 1111 has the required length four."),
        ],
        [
            [a, b, o, z]
            for a, b, o, z in [
                (1, 1, 1, 1),
                (1, 2, 1, 1),
                (2, 2, 2, 2),
                (1, 5, 2, 3),
                (3, 6, 2, 3),
                (4, 8, 1, 3),
                (5, 9, 4, 2),
                (1, 10, 5, 5),
                (6, 10, 2, 4),
                (2, 7, 3, 1),
                (7, 11, 4, 5),
                (3, 3, 1, 2),
                (8, 12, 3, 4),
                (1, 12, 2, 5),
            ]
        ],
        GOOD,
        [
            GOOD.replace("length>=one_group", "length>one_group"),
            GOOD.replace("sum(ways[min_length:])", "sum(ways[min_length:max_length])"),
        ],
        [
            "Misses strings consisting of exactly one one-block.",
            "Excludes constructible strings of exactly max_length.",
        ],
        good_oracle,
        random_good,
        [
            "Let ways[length] count constructions ending at exactly that length, with ways[0] equal to one.",
            "A final ones block comes from length-one_group; a final zeros block comes from length-zero_group.",
            "Add both predecessor counts for every reachable length, then sum the requested interval.",
            "Every nonempty construction has one uniquely determined final block choice and predecessor, so the recurrence counts each valid string once.",
        ],
        "O(max_length)",
        "O(max_length)",
        6,
    ),
    2534: entry(
        "door_crossing_times",
        [("arrival", "list[int]"), ("state", "list[int]")],
        "list[int]",
        ["simulation", "queues", "arrays"],
        [
            "Arrival times are nondecreasing; state zero means entering and one means exiting.",
            "One person crosses per second, preserving index order within each direction.",
            "If used in the previous second, prefer that direction; after an idle second, prefer exiting.",
            "Return each person's crossing second in original index order.",
        ],
        [
            (
                [[0, 1, 1, 2, 4], [0, 1, 0, 0, 1]],
                "Door priorities schedule the five people at times [0,3,1,2,4].",
            ),
            (
                [[0, 0, 0], [1, 0, 1]],
                "Exiters keep priority, so indices zero and two cross before the entering person: [0,2,1].",
            ),
        ],
        [
            [a, s]
            for a, s in [
                ([0], [0]),
                ([0], [1]),
                ([5], [0]),
                ([0, 0], [0, 1]),
                ([0, 0], [1, 0]),
                ([0, 1], [0, 0]),
                ([0, 2], [0, 1]),
                ([0, 0, 1], [0, 1, 0]),
                ([0, 1, 1], [1, 0, 1]),
                ([1, 1, 1, 1], [0, 0, 1, 1]),
                ([0, 3, 3], [1, 0, 1]),
                ([0, 1, 2, 3], [0, 1, 0, 1]),
                ([2, 2, 4, 4, 4], [1, 0, 0, 1, 0]),
                ([0, 0, 0, 2, 2, 5], [0, 1, 0, 1, 0, 1]),
            ]
        ],
        DOOR,
        [
            DOOR.replace("previous=1", "previous=0"),
            DOOR.replace(
                "direction=previous if queues[previous] else 1-previous",
                "direction=1-previous if queues[1-previous] else previous",
            ),
        ],
        [
            "After idle time, incorrectly gives entering people priority.",
            "Always prefers the opposite of the direction used previously.",
        ],
        door_oracle,
        random_door,
        [
            "Keep separate FIFO queues for entering and exiting people.",
            "Enqueue everyone whose arrival time has been reached before choosing the next direction.",
            "Continue the previous direction when possible; if the door was idle, reset the preferred direction to exit.",
            "Each person enters and leaves one queue once, and the direction rule is applied at every occupied second, exactly reproducing the schedule.",
        ],
        "O(n)",
        "O(n)",
        8,
    ),
}
