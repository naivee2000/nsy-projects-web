"""Third reviewed group of workbook batch 111."""

from collections import deque
from functools import lru_cache
from math import isqrt

from .import_batch_055 import entry


def triples_oracle(arguments):
    n = arguments[0]
    squares = {value * value: value for value in range(1, n + 1)}
    return sum(first * first + second * second in squares
               for first in range(1, n + 1) for second in range(1, n + 1))


def exit_oracle(arguments):
    maze, entrance = arguments
    rows, columns = len(maze), len(maze[0])
    start = tuple(entrance)
    queue = deque([(start[0], start[1], 0)])
    seen = {start}
    while queue:
        row, column, distance = queue.popleft()
        if (row, column) != start and (row in (0, rows - 1) or column in (0, columns - 1)):
            return distance
        for row_step, column_step in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            neighbor = row + row_step, column + column_step
            if (0 <= neighbor[0] < rows and 0 <= neighbor[1] < columns
                    and maze[neighbor[0]][neighbor[1]] == "." and neighbor not in seen):
                seen.add(neighbor)
                queue.append((neighbor[0], neighbor[1], distance + 1))
    return -1


def sum_game_oracle(arguments):
    number = arguments[0]
    half = len(number) // 2
    left_sum = sum(int(char) for char in number[:half] if char != "?")
    right_sum = sum(int(char) for char in number[half:] if char != "?")
    left_unknown = number[:half].count("?")
    right_unknown = number[half:].count("?")

    @lru_cache(maxsize=None)
    def play(left, right, left_open, right_open, alice_turn):
        if left_open + right_open == 0:
            return left != right
        outcomes = []
        if left_open:
            outcomes.extend(play(left + digit, right, left_open - 1, right_open, not alice_turn)
                            for digit in range(10))
        if right_open:
            outcomes.extend(play(left, right + digit, left_open, right_open - 1, not alice_turn)
                            for digit in range(10))
        return any(outcomes) if alice_turn else all(outcomes)

    return play(left_sum, right_sum, left_unknown, right_unknown, True)


def travel_oracle(arguments):
    maximum_time, edges, fees = arguments
    graph = [[] for _ in fees]
    for first, second, travel in edges:
        graph[first].append((second, travel))
        graph[second].append((first, travel))

    @lru_cache(maxsize=None)
    def cheapest(city, remaining):
        if city == len(fees) - 1:
            return fees[city]
        best = None
        for neighbor, travel in graph[city]:
            if travel <= remaining:
                suffix = cheapest(neighbor, remaining - travel)
                if suffix is not None:
                    candidate = fees[city] + suffix
                    best = candidate if best is None else min(best, candidate)
        return best

    result = cheapest(0, maximum_time)
    return -1 if result is None else result


def concatenate_oracle(arguments):
    nums = arguments[0]
    return [nums[index % len(nums)] for index in range(2 * len(nums))]


def random_triples(rng):
    return [rng.randint(1, 50)]


def random_exit(rng):
    rows, columns = rng.randint(1, 8), rng.randint(1, 8)
    maze = [[rng.choice("...+") for _ in range(columns)] for _ in range(rows)]
    row, column = rng.randrange(rows), rng.randrange(columns)
    maze[row][column] = "."
    return [maze, [row, column]]


def random_sum_game(rng):
    length = rng.choice((2, 4, 6))
    while True:
        value = "".join(rng.choice("0123456789??") for _ in range(length))
        if value.count("?") <= 6:
            return [value]


def random_travel(rng):
    cities = rng.randint(2, 7)
    edges = []
    for city in range(1, cities):
        parent = rng.randrange(city)
        edges.append([parent, city, rng.randint(1, 6)])
    existing = {tuple(sorted(edge[:2])) for edge in edges}
    for first in range(cities):
        for second in range(first + 1, cities):
            if (first, second) not in existing and rng.random() < 0.25:
                edges.append([first, second, rng.randint(1, 6)])
    return [rng.randint(1, 18), edges, [rng.randint(1, 12) for _ in range(cities)]]


def random_concatenate(rng):
    return [[rng.randint(1, 1000) for _ in range(rng.randint(1, 30))]]


TRIPLES = '''\
def count_ordered_square_sum_triples(n):
    from math import isqrt
    answer = 0
    for first in range(1, n + 1):
        for second in range(1, n + 1):
            root = isqrt(first * first + second * second)
            if root <= n and root * root == first * first + second * second:
                answer += 1
    return answer
'''

EXIT = '''\
def nearest_maze_exit(maze, entrance):
    from collections import deque
    rows, columns = len(maze), len(maze[0])
    start = tuple(entrance)
    queue = deque([(start[0], start[1], 0)])
    seen = {start}
    while queue:
        row, column, distance = queue.popleft()
        for row_step, column_step in ((-1,0),(1,0),(0,-1),(0,1)):
            next_row, next_column = row + row_step, column + column_step
            if (0 <= next_row < rows and 0 <= next_column < columns and
                    maze[next_row][next_column] == "." and (next_row, next_column) not in seen):
                if next_row in (0, rows - 1) or next_column in (0, columns - 1):
                    return distance + 1
                seen.add((next_row, next_column))
                queue.append((next_row, next_column, distance + 1))
    return -1
'''

EXIT_DISTANCE = '''\
def nearest_maze_exit(maze, entrance):
    row,column=entrance;rows,columns=len(maze),len(maze[0])
    distances=[row,rows-1-row,column,columns-1-column]
    positive=[value for value in distances if value>0]
    return min(positive,default=-1)
'''

SUM_GAME = '''\
def alice_wins_sum_game(num):
    half = len(num) // 2
    left_unknown = num[:half].count("?")
    right_unknown = num[half:].count("?")
    left_sum = sum(int(char) for char in num[:half] if char != "?")
    right_sum = sum(int(char) for char in num[half:] if char != "?")
    if (left_unknown + right_unknown) % 2 == 1:
        return True
    return left_sum - right_sum != 9 * (right_unknown - left_unknown) // 2
'''

SUM_GAME_ZERO = '''\
def alice_wins_sum_game(num):
    half=len(num)//2
    return sum(int(c) for c in num[:half] if c!='?') != sum(int(c) for c in num[half:] if c!='?')
'''

TRAVEL = '''\
def minimum_fee_within_time(max_time, edges, passing_fees):
    infinity = 10**30
    costs = [[infinity] * len(passing_fees) for _ in range(max_time + 1)]
    costs[0][0] = passing_fees[0]
    for elapsed in range(1, max_time + 1):
        for first, second, travel in edges:
            if travel <= elapsed:
                costs[elapsed][first] = min(costs[elapsed][first], costs[elapsed - travel][second] + passing_fees[first])
                costs[elapsed][second] = min(costs[elapsed][second], costs[elapsed - travel][first] + passing_fees[second])
    answer = min(costs[elapsed][-1] for elapsed in range(max_time + 1))
    return -1 if answer == infinity else answer
'''

TRAVEL_FASTEST = '''\
def minimum_fee_within_time(max_time, edges, passing_fees):
    from heapq import heappop,heappush
    graph=[[] for _ in passing_fees]
    for a,b,t in edges:graph[a].append((b,t));graph[b].append((a,t))
    heap=[(0,0,passing_fees[0])];seen=set()
    while heap:
        elapsed,city,cost=heappop(heap)
        if city==len(passing_fees)-1:return cost if elapsed<=max_time else -1
        if city in seen:continue
        seen.add(city)
        for nxt,t in graph[city]:heappush(heap,(elapsed+t,nxt,cost+passing_fees[nxt]))
    return -1
'''

CONCATENATE = '''\
def concatenate_array_twice(nums):
    return nums + nums
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1925: entry(
        "count_ordered_square_sum_triples", [("n", "int")], "int",
        ["math", "enumeration"],
        ["1 <= n <= 250.", "Count ordered positive triples (a,b,c) with every value at most n.",
         "The order of a and b matters, so (3,4,5) and (4,3,5) are separate triples."],
        [([5], "The ordered triples are (3,4,5) and (4,3,5), so the answer is two."),
         ([10], "The triples based on 3-4-5 and 6-8-10 contribute four ordered arrangements.")],
        [[n] for n in [1,2,3,4,5,6,7,8,9,10,12,15,25,50]],
        TRIPLES,
        [TRIPLES.replace("root <= n", "root < n"),
         TRIPLES.replace("answer += 1", "answer += first <= second")],
        ["Excludes triples whose hypotenuse is exactly n, creating an incorrect upper boundary.",
         "Counts only one ordering of the two legs instead of treating (a,b) as ordered."],
        triples_oracle, random_triples,
        lesson("Enumerate both ordered leg lengths a and b.",
               "Compute a²+b² and use integer square root to test whether it is a perfect square.",
               "Count it when the root is at most n.",
               "Every ordered pair is visited exactly once, and the perfect-square test is equivalent to the existence of the required integer c."),
        "O(n^2)", "O(1)", 3),
    1926: entry(
        "nearest_maze_exit", [("maze", "list[list[str]]"), ("entrance", "list[int]")], "int",
        ["matrices", "breadth-first-search", "graphs"],
        ["The maze has at most 100 rows and columns; '.' is open and '+' is a wall.",
         "The entrance is open but does not count as an exit even when it lies on the boundary.",
         "Move orthogonally and return the fewest steps to another boundary opening, or -1."],
        [([[['+','+','.','+'],['.','.','.','+'],['+','+','+','.']],[1,2]], "The open boundary cell directly above the entrance is one step away."),
         ([[['+','+','+'],['.','.','.'],['+','+','+']],[1,0]], "The boundary entrance is excluded, and the opposite boundary opening is two steps away.")],
        [[maze,entrance] for maze,entrance in [
            ([['.']],[0,0]),([['.','.']],[0,0]),([['+','+','.','+'],['.','.','.','+'],['+','+','+','.']],[1,2]),
            ([['+','+','+'],['.','.','.'],['+','+','+']],[1,0]),
            ([['+','.','+'],['.','.','.'],['+','+','+']],[1,1]),
            ([['+','+','+'],['+','.','+'],['+','+','+']],[1,1]),
            ([['.','+'],['.','.']],[1,1]),([['.','.','.']],[0,1]),
            ([['+','.','+','+'],['+','.','.','.'],['+','+','+','+']],[1,1]),
            ([['+','+','+','+'],['.','.','.','+'],['+','+','.','+'],['+','.','.','+']],[1,0]),
            ([['.','+','.'],['.','.','.'],['.','+','.']],[1,1]),
            ([['+','.','+'],['+','.','+'],['+','.','+']],[1,1]),
            ([['+','+','.'],['.','.','.']],[1,0]),
            ([['+','+','+'],['.','.','+'],['+','.','.']],[1,0]),
        ]],
        EXIT,
        [EXIT.replace("for row_step, column_step in", "if start[0] in (0, rows-1) or start[1] in (0, columns-1): return 0\n        for row_step, column_step in", 1), EXIT_DISTANCE],
        ["Incorrectly treats a boundary entrance itself as a zero-step exit.",
         "Uses geometric distance to the boundary and ignores walls and reachable routes."],
        exit_oracle, random_exit,
        lesson("Breadth-first search explores open cells in nondecreasing path length.",
               "Mark the entrance visited, expand four orthogonal neighbors, and accept the first boundary opening other than the entrance.",
               "Return -1 if the queue empties.",
               "BFS's layer order makes the first discovered valid exit nearest, while visited tracking prevents cycles and preserves all simple routes."),
        "O(rows*columns)", "O(rows*columns)", 6),
    1927: entry(
        "alice_wins_sum_game", [("num", "str")], "bool",
        ["strings", "game-theory", "greedy", "math"],
        ["num has even length up to 100000 and contains digits or '?'.",
         "Alice and Bob alternately replace one question mark with any digit; Alice moves first.",
         "Alice wins when final half sums differ, while Bob wins when they are equal; both optimize their result."],
        [(["5023"], "There are no choices and both halves sum to seven, so Bob wins and the result is false."),
         (["25??"], "Alice can force unequal half sums regardless of Bob's reply, so the result is true.")],
        [[num] for num in ["00","01","5023","25??","?3295???","????","?0","0?","1?","?1","12??","??12","9?0?","?5?5","?5","4?"]],
        SUM_GAME,
        [SUM_GAME.replace("if (left_unknown + right_unknown) % 2 == 1:\n        return True", "if False:\n        return True"), SUM_GAME_ZERO],
        ["Applies only the even-question balance equation and misses Alice's extra move when the question count is odd.",
         "Treats every question mark as zero instead of modeling alternating optimal digit choices."],
        sum_game_oracle, random_sum_game,
        lesson("Count question marks and fixed digit sums separately in the two halves.",
               "An odd total number of moves gives Alice one unmatched choice, so she can force a difference.",
               "With an even count, Bob can balance exactly only when the fixed difference equals 9/2 times the question-count imbalance.",
               "Pairing Alice and Bob's optimal digit choices contributes nine per move pair, yielding the balance equation and its negation as Alice's winning test."),
        "O(len(num))", "O(1)", 6),
    1928: entry(
        "minimum_fee_within_time", [("max_time", "int"), ("edges", "list[list[int]]"), ("passing_fees", "list[int]")], "int",
        ["graphs", "dynamic-programming", "shortest-paths"],
        ["1 <= max_time <= 1000; there are 2 through 1000 cities and at most 1000 undirected weighted edges.",
         "Pay a city's fee every time it is visited, including start and destination.",
         "Return minimum fee among walks reaching the last city within max_time, or -1 when impossible."],
        [([30,[[0,1,10],[1,2,10],[2,5,10],[0,3,1],[3,4,10],[4,5,15]],[5,1,2,20,20,3]], "The 0-1-2-5 path takes thirty minutes and costs 5+1+2+3 = 11."),
         ([25,[[0,1,10],[1,2,10],[2,5,10],[0,3,1],[3,4,10],[4,5,15]],[5,1,2,20,20,3]], "The cheap route is too slow, so the faster 0-3-4-5 route costs 48.")],
        [[time,edges,fees] for time,edges,fees in [
            (1,[[0,1,1]],[1,2]),(1,[[0,1,2]],[1,2]),
            (30,[[0,1,10],[1,2,10],[2,5,10],[0,3,1],[3,4,10],[4,5,15]],[5,1,2,20,20,3]),
            (25,[[0,1,10],[1,2,10],[2,5,10],[0,3,1],[3,4,10],[4,5,15]],[5,1,2,20,20,3]),
            (29,[[0,1,10],[1,2,10],[2,5,10],[0,3,1],[3,4,10],[4,5,15]],[5,1,2,20,20,3]),
            (5,[[0,1,2],[1,2,2],[0,2,5]],[5,1,10]),
            (4,[[0,1,2],[1,2,2],[0,2,5]],[5,1,10]),
            (10,[[0,1,3],[1,3,3],[0,2,1],[2,3,8]],[2,2,20,2]),
            (6,[[0,1,5],[1,2,1],[0,2,6]],[10,1,10]),
            (7,[[0,1,2],[1,2,2],[2,3,2],[0,3,7]],[1,1,1,20]),
            (3,[[0,1,1],[1,2,1],[0,2,3]],[4,9,4]),
            (8,[[0,1,2],[1,2,2],[2,3,2],[1,3,6]],[3,8,1,3]),
            (2,[[0,1,1],[1,2,1],[0,2,2]],[100,1,100]),
            (12,[[0,1,4],[1,2,4],[2,3,4],[0,3,11]],[2,1,1,20]),
        ]],
        TRAVEL,
        [TRAVEL_FASTEST, TRAVEL.replace("+ passing_fees[second]", "+ 0")],
        ["Chooses the fastest route first and never compares a slower route with lower fees within the same time budget.",
         "Omits the fee when arriving at the second endpoint of each stored edge."],
        travel_oracle, random_travel,
        lesson("Time is a bounded integer resource, so use dynamic programming over exact elapsed time and current city.",
               "For each time, relax both directions of every edge from the state at time minus its travel duration.",
               "Take the minimum destination cost over all elapsed times up to max_time.",
               "Every feasible walk ends with some edge and smaller exact-time state, so the recurrence covers all walks; minimizing each state preserves the cheapest one."),
        "O(max_time*edges)", "O(max_time*cities)", 8),
    1929: entry(
        "concatenate_array_twice", [("nums", "list[int]")], "list[int]",
        ["arrays", "simulation"],
        ["nums has 1 through 1000 positive values.",
         "Return an array of length twice len(nums).",
         "The first and second halves must both equal nums in their original order."],
        [([[1,2,1]], "Placing two copies consecutively gives [1,2,1,1,2,1]."),
         ([[1,3,2,1]], "The result is [1,3,2,1,1,3,2,1].")],
        [[nums] for nums in [[1],[1,2,1],[1,3,2,1],[5,5],[1,2,3,4],[9,8,7],
                             [10,20],[4,1,4,1],[1000],[2,3,5,7],[6,6,6],[1,9,2,8,3],
                             [7,4,2,9],[3,1,3,1,3]]],
        CONCATENATE,
        [CONCATENATE.replace("nums + nums", "nums"), CONCATENATE.replace("nums + nums", "nums + list(reversed(nums))")],
        ["Returns only one copy and therefore has the wrong output length.",
         "Appends a reversed copy rather than preserving the original order in the second half."],
        concatenate_oracle, random_concatenate,
        lesson("The result consists of two independent copies of the input sequence.",
               "Use list concatenation to place one complete copy after the other.",
               "Return the new list.",
               "Concatenation preserves each operand's order and length, so the result satisfies both required halves and has exactly twice the input length."),
        "O(n)", "O(n)", 3),
}
