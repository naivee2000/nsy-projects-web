"""Third reviewed group of workbook batch 109."""

from itertools import permutations

from .import_batch_055 import entry


def xor_sum_oracle(arguments):
    first, second = arguments
    return min(sum(left ^ right for left, right in zip(first, order))
               for order in permutations(second))


def word_sum_oracle(arguments):
    def value(word):
        return int("".join(str(ord(char) - ord("a")) for char in word))
    return value(arguments[0]) + value(arguments[1]) == value(arguments[2])


def insertion_oracle(arguments):
    number, digit = arguments
    first_position = 1 if number[0] == "-" else 0
    candidates = [number[:position] + str(digit) + number[position:]
                  for position in range(first_position, len(number) + 1)]
    return max(candidates, key=int)


def server_oracle(arguments):
    servers, tasks = arguments
    free_at = [0] * len(servers)
    answer = []
    time = 0
    for arrival, duration in enumerate(tasks):
        time = max(time, arrival)
        available = [index for index, release in enumerate(free_at) if release <= time]
        if not available:
            time = min(free_at)
            available = [index for index, release in enumerate(free_at) if release <= time]
        chosen = min(available, key=lambda index: (servers[index], index))
        answer.append(chosen)
        free_at[chosen] = time + duration
    return answer


def skips_oracle(arguments):
    distances, speed, hours_before = arguments
    rests = len(distances) - 1
    best = None
    for skipped_mask in range(1 << rests):
        elapsed = 0
        for index, distance in enumerate(distances):
            elapsed += distance
            if index < rests and not (skipped_mask >> index) & 1:
                elapsed = ((elapsed + speed - 1) // speed) * speed
        if elapsed <= hours_before * speed:
            skips = skipped_mask.bit_count()
            best = skips if best is None else min(best, skips)
    return -1 if best is None else best


def random_xor_sum(rng):
    length = rng.randint(1, 6)
    return [[rng.randint(0, 63) for _ in range(length)],
            [rng.randint(0, 63) for _ in range(length)]]


def random_word_sum(rng):
    def word():
        return "".join(rng.choice("abcdefghij") for _ in range(rng.randint(1, 8)))
    return [word(), word(), word()]


def random_insertion(rng):
    length = rng.randint(1, 12)
    number = "".join(rng.choice("123456789") for _ in range(length))
    if rng.random() < 0.5:
        number = "-" + number
    return [number, rng.randint(1, 9)]


def random_servers(rng):
    return [[rng.randint(1, 12) for _ in range(rng.randint(1, 6))],
            [rng.randint(1, 10) for _ in range(rng.randint(1, 12))]]


def random_skips(rng):
    distances = [rng.randint(1, 20) for _ in range(rng.randint(1, 8))]
    speed = rng.randint(1, 12)
    return [distances, speed, rng.randint(1, 20)]


XOR_SUM = '''\
def minimum_xor_assignment_sum(nums1, nums2):
    size = 1 << len(nums2)
    infinity = float("inf")
    best = [infinity] * size
    best[0] = 0
    for mask in range(size):
        index = mask.bit_count()
        if index == len(nums1):
            continue
        for candidate, value in enumerate(nums2):
            bit = 1 << candidate
            if mask & bit == 0:
                next_mask = mask | bit
                best[next_mask] = min(best[next_mask], best[mask] + (nums1[index] ^ value))
    return best[-1]
'''

XOR_GREEDY = '''\
def minimum_xor_assignment_sum(nums1, nums2):
    unused = set(range(len(nums2)))
    total = 0
    for value in nums1:
        chosen = min(unused, key=lambda index: value ^ nums2[index])
        total += value ^ nums2[chosen]
        unused.remove(chosen)
    return total
'''

WORD_SUM = '''\
def word_values_add_up(first_word, second_word, target_word):
    def value(word):
        result = 0
        for char in word:
            result = result * 10 + ord(char) - ord("a")
        return result
    return value(first_word) + value(second_word) == value(target_word)
'''

WORD_DIGIT_SUM = '''\
def word_values_add_up(first_word, second_word, target_word):
    def value(word):
        return sum(ord(char) - ord("a") for char in word)
    return value(first_word) + value(second_word) == value(target_word)
'''

INSERTION = '''\
def maximize_number_by_inserting_digit(n, x):
    digit = str(x)
    if n[0] == "-":
        position = 1
        while position < len(n) and n[position] <= digit:
            position += 1
    else:
        position = 0
        while position < len(n) and n[position] >= digit:
            position += 1
    return n[:position] + digit + n[position:]
'''

INSERT_APPEND = '''\
def maximize_number_by_inserting_digit(n, x):
    return n + str(x)
'''

INSERT_POSITIVE_RULE = '''\
def maximize_number_by_inserting_digit(n, x):
    digit = str(x)
    position = 1 if n[0] == "-" else 0
    while position < len(n) and n[position] >= digit:
        position += 1
    return n[:position] + digit + n[position:]
'''

SERVERS = '''\
def assign_tasks_to_servers(servers, tasks):
    from heapq import heapify, heappop, heappush
    idle = [(weight, index) for index, weight in enumerate(servers)]
    heapify(idle)
    busy = []
    answer = []
    time = 0
    for arrival, duration in enumerate(tasks):
        time = max(time, arrival)
        while busy and busy[0][0] <= time:
            release, weight, index = heappop(busy)
            heappush(idle, (weight, index))
        if not idle:
            time = busy[0][0]
            while busy and busy[0][0] <= time:
                release, weight, index = heappop(busy)
                heappush(idle, (weight, index))
        weight, index = heappop(idle)
        answer.append(index)
        heappush(busy, (time + duration, weight, index))
    return answer
'''

SERVERS_BY_INDEX = '''\
def assign_tasks_to_servers(servers, tasks):
    free_at = [0] * len(servers); answer = []; time = 0
    for arrival, duration in enumerate(tasks):
        time = max(time, arrival)
        available = [i for i, release in enumerate(free_at) if release <= time]
        if not available:
            time = min(free_at); available = [i for i, release in enumerate(free_at) if release <= time]
        chosen = min(available)
        answer.append(chosen); free_at[chosen] = time + duration
    return answer
'''

SKIPS = '''\
def minimum_rest_skips(dist, speed, hours_before):
    infinity = 10**30
    best = [infinity] * (len(dist) + 1)
    best[0] = 0
    for index, distance in enumerate(dist):
        updated = [infinity] * (len(dist) + 1)
        for skips in range(index + 1):
            travel = best[skips] + distance
            if index == len(dist) - 1:
                updated[skips] = min(updated[skips], travel)
            else:
                rested = ((travel + speed - 1) // speed) * speed
                updated[skips] = min(updated[skips], rested)
                updated[skips + 1] = min(updated[skips + 1], travel)
        best = updated
    budget = hours_before * speed
    for skips, elapsed in enumerate(best):
        if elapsed <= budget:
            return skips
    return -1
'''

SKIPS_ROUND_LAST = '''\
def minimum_rest_skips(dist, speed, hours_before):
    infinity = 10**30; best = [0] + [infinity] * len(dist)
    for index, distance in enumerate(dist):
        updated = [infinity] * (len(dist) + 1)
        for skips in range(index + 1):
            travel = best[skips] + distance
            updated[skips] = min(updated[skips], ((travel + speed - 1) // speed) * speed)
            if index < len(dist) - 1: updated[skips + 1] = min(updated[skips + 1], travel)
        best = updated
    for skips, elapsed in enumerate(best):
        if elapsed <= hours_before * speed: return skips
    return -1
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1879: entry(
        "minimum_xor_assignment_sum", [("nums1", "list[int]"), ("nums2", "list[int]")], "int",
        ["arrays", "bit-manipulation", "bitmask-dp", "dynamic-programming"],
        ["The arrays have equal length from 1 through 14.", "Values are between 0 and 10000000.",
         "Rearrange nums2 to minimize the sum of XORs at corresponding positions."],
        [([[1,2],[2,3]], "Pairing one with three and two with two gives XOR cost two."),
         ([[1,0,3],[5,3,4]], "The minimum over all one-to-one assignments is eight.")],
        [[left,right] for left,right in [
            ([0],[0]),([1],[2]),([1,2],[2,3]),([1,0,3],[5,3,4]),([0,1],[1,0]),
            ([5,5],[1,2]),([1,2,3],[3,2,1]),([7,8,9],[1,2,3]),([0,0,0],[1,2,4]),
            ([10,20,30,40],[7,17,27,37]),([4,1,7,3],[2,6,5,8]),([15,0,15],[8,7,6]),
            ([2,9,1,8,3],[6,5,4,3,2]),([63,31,15,7],[1,3,7,15]),
        ]],
        XOR_SUM,
        [XOR_SUM.replace("nums1[index] ^ value", "nums1[index] | value"), XOR_GREEDY],
        ["Uses bitwise OR as the pair cost instead of XOR.",
         "Chooses the cheapest current partner greedily, which can block a better global assignment."],
        xor_sum_oracle, random_xor_sum,
        lesson("A bitmask can record exactly which values from nums2 have already been assigned.",
               "The mask's set-bit count identifies the next nums1 position.",
               "Try every unused partner and relax the cost of the mask with that bit added.",
               "Every complete mask path represents one permutation, and dynamic programming retains the cheapest prefix for each equivalent set of remaining choices."),
        "O(n*2^n)", "O(2^n)", 8),
    1880: entry(
        "word_values_add_up", [("first_word", "str"), ("second_word", "str"), ("target_word", "str")], "bool",
        ["strings", "math", "simulation"],
        ["Each word has length 1 through 8.", "Letters range from 'a' through 'j'.",
         "Map a through j to digits 0 through 9 and concatenate those digits to form each value."],
        [(["acb","cba","cdb"], "The values 21 and 210 add to 231, the value of cdb."),
         (["aaa","a","aab"], "Zero plus zero does not equal one, so the statement is false.")],
        [[a,b,c] for a,b,c in [
            ("a","a","a"),("b","b","c"),("acb","cba","cdb"),("aaa","a","aab"),
            ("j","a","j"),("ba","a","ba"),("bc","de","fh"),("abc","def","egi"),
            ("jj","b","baa"),("i","b","j"),("aaaa","aaaa","aaaa"),("cab","ba","cbb"),
            ("hij","a","hij"),("bbbb","bbbb","cccc"),
        ]],
        WORD_SUM,
        [WORD_SUM.replace("ord(char) - ord(\"a\")", "ord(char) - ord(\"a\") + 1"), WORD_DIGIT_SUM],
        ["Maps letters to one through ten rather than digits zero through nine.",
         "Adds letter digits instead of concatenating them by place value."],
        word_sum_oracle, random_word_sum,
        lesson("Treat every mapped letter as the next decimal digit.",
               "Build a word's value by multiplying the current value by ten before adding the next digit.",
               "Convert all three words, then compare first plus second with target.",
               "The update is the standard positional-decimal recurrence, so induction over the letters proves it constructs the specified concatenation."),
        "O(total characters)", "O(1)", 3),
    1881: entry(
        "maximize_number_by_inserting_digit", [("n", "str"), ("x", "int")], "str",
        ["strings", "greedy"],
        ["n represents a nonzero integer using 1 through 100000 characters.", "Its digits and x are in 1 through 9.",
         "Insert x exactly once and never before a leading minus sign."],
        [(["99",9], "Every insertion produces the same maximal representation, 999."),
         (["-13",2], "Inserting two before three gives -123, which is greater than -213 or -132.")],
        [[n,x] for n,x in [
            ("1",1),("1",9),("9",1),("99",9),("73",6),("469975787943862651173569913153377",3),
            ("-13",2),("-55",2),("-999",9),("-123",9),("12345",3),("54321",3),
            ("-2468",5),("8888",7),("-1111",1),("314159",2),
        ]],
        INSERTION,
        [INSERT_APPEND, INSERT_POSITIVE_RULE],
        ["Always appends the digit, ignoring the first position that improves the number.",
         "Uses the positive-number comparison for negatives, where smaller magnitude digits must come earlier."],
        insertion_oracle, random_insertion,
        lesson("For a positive number, place x before the first smaller digit.",
               "For a negative number, maximize the value by minimizing magnitude: place x before the first larger digit.",
               "If no improving position exists, append x at the end.",
               "All earlier digits stay equal between candidates, so the first differing digit determines the larger integer and validates the greedy stopping point."),
        "O(len(n))", "O(len(n))", 5),
    1882: entry(
        "assign_tasks_to_servers", [("servers", "list[int]"), ("tasks", "list[int]")], "list[int]",
        ["arrays", "heaps", "simulation", "scheduling"],
        ["Each list has length 1 through 200000 and all values are positive.",
         "Task i arrives at second i and waiting tasks remain in arrival order.",
         "Choose a free server by lowest weight, then lowest index; if none is free, advance to the earliest release."],
        [([[3,3,2],[1,2,3,2,1,2]], "The weight-two server handles tasks whenever free, producing assignments [2,2,0,2,1,2]."),
         ([[5,1,4,3,2],[2,1,2,4,5,2,1]], "Tracking idle priority and release times yields [1,4,1,4,1,3,2].")],
        [[servers,tasks] for servers,tasks in [
            ([1],[1]),([1],[3,2,1]),([3,3,2],[1,2,3,2,1,2]),([5,1,4,3,2],[2,1,2,4,5,2,1]),
            ([1,2],[5,1,1]),([2,1],[5,1,1]),([3,3],[2,2,2,2]),([4,4,4],[3,3,3,3,3]),
            ([10,1,5],[1,10,1,1]),([2,8,1],[4,2,7,1,3]),([1,1,2],[5,5,1,1]),
            ([7,3,9,2],[8,1,1,8,2]),([6,5],[10,10,10]),([2,4,6],[1,1,1,1,1,1]),
            ([6,4],[4,8,5,1,7,9,2,3,5,2,6]),
        ]],
        SERVERS,
        [SERVERS_BY_INDEX, SERVERS.replace("time + duration", "arrival + duration")],
        ["Prioritizes server index while ignoring the required lower-weight preference.",
         "Schedules a delayed task from its original arrival time instead of the time a server becomes available."],
        server_oracle, random_servers,
        lesson("Use one heap for idle servers ordered by weight/index and another for busy servers ordered by release time.",
               "At each arrival, release every server available by the current time; if idle is empty, jump to the next release and release all ties.",
               "Take the best idle server and push its new release record into the busy heap.",
               "Tasks are processed in arrival order, while the two heap orderings exactly implement the server-choice and earliest-time rules."),
        "O((servers+tasks)*log(servers))", "O(servers)", 7),
    1883: entry(
        "minimum_rest_skips", [("dist", "list[int]"), ("speed", "int"), ("hours_before", "int")], "int",
        ["arrays", "dynamic-programming", "rounding"],
        ["1 <= len(dist) <= 1000 and distances are positive.", "speed and hours_before are positive integers.",
         "After each non-final road, either wait until the next integer hour or spend one skip to depart immediately."],
        [([[1,3,2],4,2], "Skipping the wait after the first road permits arrival within two hours, so one skip is sufficient."),
         ([[7,3,5,5],2,10], "Even skipping every rest cannot reduce pure travel time below ten hours, so the answer is -1.")],
        [[dist,speed,hours] for dist,speed,hours in [
            ([1],1,1),([2],1,1),([1,3,2],4,2),([7,3,5,5],2,10),([7,3,5,5],1,10),
            ([1,1,1],2,2),([1,1,1],3,1),([5,3,4],4,4),([5,3,4],4,3),
            ([6,2,8,3],5,5),([2,2,2,2],3,3),([9,1],10,1),([9,1],9,2),
            ([3,8,2,6,1],4,6),([10,10,10],10,3),([1,10,1],6,2),
        ]],
        SKIPS,
        [SKIPS.replace("updated[skips + 1] = min(updated[skips + 1], travel)",
                       "updated[skips + 1] = min(updated[skips + 1], rested)"),
         SKIPS.replace("((travel + speed - 1) // speed) * speed", "(travel // speed) * speed")],
        ["Carries the rounded rest time into the skip transition, so spending a skip provides no benefit.",
         "Rounds completed travel down at rests instead of waiting until the next whole hour."],
        skips_oracle, random_skips,
        lesson("Represent elapsed time in distance units so one hour equals speed units and all arithmetic stays exact.",
               "For each road and skip count, either round up at the rest or use another skip and keep the exact elapsed value.",
               "Do not round after the final road; then choose the smallest skip count within hours_before*speed.",
               "The DP retains the least elapsed time for every prefix and skip count, and the two transitions cover every possible rest decision."),
        "O(n^2)", "O(n)", 8),
}
