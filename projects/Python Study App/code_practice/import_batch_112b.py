"""Second reviewed group of workbook batch 112."""

from .import_batch_055 import entry


def chair_oracle(arguments):
    times, target = arguments
    occupied = {}
    answer = None
    for arrival, friend in sorted((times[index][0], index) for index in range(len(times))):
        occupied = {chair: leaving for chair, leaving in occupied.items() if leaving > arrival}
        chair = 0
        while chair in occupied:
            chair += 1
        occupied[chair] = times[friend][1]
        if friend == target:
            answer = chair
            break
    return answer


def painting_oracle(arguments):
    segments = arguments[0]
    endpoints = sorted({point for left, right, _ in segments for point in (left, right)})
    answer = []
    for left, right in zip(endpoints, endpoints[1:]):
        color = sum(value for start, end, value in segments if start <= left and right <= end)
        if color:
            if answer and answer[-1][1] == left and answer[-1][2] == color:
                answer[-1][1] = right
            else:
                answer.append([left, right, color])
    return answer


def visible_oracle(arguments):
    heights = arguments[0]
    answer = [0] * len(heights)
    for left in range(len(heights)):
        between = -1
        for right in range(left + 1, len(heights)):
            if between < min(heights[left], heights[right]):
                answer[left] += 1
            between = max(between, heights[right])
    return answer


def digit_sum_oracle(arguments):
    text, rounds = arguments
    digits = "".join(str(ord(char) - 96) for char in text)
    value = digits
    for _ in range(rounds):
        value = str(sum(int(char) for char in value))
    return int(value)


def mutation_oracle(arguments):
    number, change = arguments
    candidates = [number]
    for left in range(len(number)):
        for right in range(left + 1, len(number) + 1):
            candidates.append(number[:left] + "".join(str(change[int(char)]) for char in number[left:right]) + number[right:])
    return max(candidates)


def random_chair(rng):
    size = rng.randint(2, 10)
    arrivals = rng.sample(range(1, 60), size)
    times = [[arrival, arrival + rng.randint(1, 15)] for arrival in arrivals]
    return [times, rng.randrange(size)]


def random_painting(rng):
    count = rng.randint(1, 8)
    colors = rng.sample(range(1, 40), count)
    segments = []
    for color in colors:
        left = rng.randint(1, 15)
        segments.append([left, rng.randint(left + 1, 20), color])
    return [segments]


def random_visible(rng):
    length = rng.randint(1, 20)
    return [rng.sample(range(1, 200), length)]


def random_digit_sum(rng):
    return ["".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(1, 30))), rng.randint(1, 10)]


def random_mutation(rng):
    return ["".join(rng.choice("0123456789") for _ in range(rng.randint(1, 9))),
            [rng.randint(0, 9) for _ in range(10)]]


CHAIR = '''\
def smallest_chair_for_friend(times, target_friend):
    from heapq import heappop, heappush
    available = list(range(len(times)))
    occupied = []
    for arrival, leaving, friend in sorted((start, end, index) for index, (start, end) in enumerate(times)):
        while occupied and occupied[0][0] <= arrival:
            _, chair = heappop(occupied)
            heappush(available, chair)
        chair = heappop(available)
        if friend == target_friend:
            return chair
        heappush(occupied, (leaving, chair))
'''

PAINTING = '''\
def describe_mixed_painting(segments):
    changes = {}
    for left, right, color in segments:
        changes[left] = changes.get(left, 0) + color
        changes[right] = changes.get(right, 0) - color
    answer = []
    color = 0
    previous = None
    for point in sorted(changes):
        if previous is not None and color:
            if answer and answer[-1][1] == previous and answer[-1][2] == color:
                answer[-1][1] = point
            else:
                answer.append([previous, point, color])
        color += changes[point]
        previous = point
    return answer
'''

VISIBLE = '''\
def visible_people_to_right(heights):
    answer = [0] * len(heights)
    stack = []
    for index in range(len(heights) - 1, -1, -1):
        while stack and heights[index] > stack[-1]:
            stack.pop()
            answer[index] += 1
        if stack:
            answer[index] += 1
        stack.append(heights[index])
    return answer
'''

DIGITS = '''\
def alphabet_conversion_digit_sum(s, k):
    value = "".join(str(ord(char) - 96) for char in s)
    for _ in range(k):
        value = str(sum(int(digit) for digit in value))
    return int(value)
'''

MUTATION = '''\
def largest_mutated_number(num, change):
    digits = list(num)
    started = False
    for index, char in enumerate(digits):
        original = int(char)
        replacement = change[original]
        if replacement > original:
            started = True
            digits[index] = str(replacement)
        elif replacement == original and started:
            digits[index] = str(replacement)
        elif started:
            break
    return "".join(digits)
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


BATCH = {
    1942: entry(
        "smallest_chair_for_friend", [("times", "list[list[int]]"), ("target_friend", "int")], "int",
        ["heaps", "simulation", "sorting"],
        ["times contains 2 through 10000 [arrival, leaving] pairs with distinct arrival times.",
         "1 <= arrival < leaving <= 100000 and 0 <= target_friend < len(times).",
         "A chair freed at the same time as an arrival is immediately available; each arrival takes the smallest free chair."],
        [([[[1,4],[2,3],[4,6]],1], "Friend one arrives second and receives chair one."),
         ([[[3,10],[1,5],[2,6]],0], "At time three chairs zero and one are occupied, so the target receives chair two.")],
        [[t,f] for t,f in [([[1,2],[2,3]],1),([[2,3],[1,2]],0),([[1,10],[2,3]],1),([[5,6],[1,10]],0),
                            ([[1,4],[2,3],[4,6]],0),([[1,4],[2,3],[4,6]],2),([[1,2],[3,4],[5,6]],2),
                            ([[1,10],[2,9],[3,8],[4,7]],3),([[4,8],[1,2],[2,3],[3,4]],0),
                            ([[10,20],[1,100],[5,6]],0),([[1,5],[2,6],[5,7]],2),([[2,4],[1,3],[4,5]],2),
                            ([[7,9],[1,8],[3,4],[5,6]],0),([[1,100],[50,60]],1)]],
        CHAIR,
        [CHAIR.replace("occupied[0][0] <= arrival", "occupied[0][0] < arrival"),
         CHAIR.replace("available = list(range(len(times)))", "available = list(range(1, len(times) + 1))")],
        ["Fails to reuse a chair when its friend leaves exactly at the next arrival time.", "Numbers chairs from one rather than zero."],
        chair_oracle, random_chair,
        lesson("Two min-heaps track the earliest departures and the smallest currently free chair.",
               "Process arrivals chronologically, release every chair whose departure is at most the arrival, then take the smallest available chair.",
               "Sort (arrival, leaving, friend); pop expired occupied entries into available; pop one chair and stop when friend is target.",
               "All and only free chairs are in the available heap at each arrival, so its minimum is the mandated assignment; stopping at the target cannot affect its chair."),
        "O(n log n)", "O(n)", 5),
    1943: entry(
        "describe_mixed_painting", [("segments", "list[list[int]]")], "list[list[int]]",
        ["intervals", "prefix sums", "sorting"],
        ["segments contains 1 through 20000 triples [start, end, color].", "1 <= start < end <= 100000 and colors are distinct positive integers up to 1000000000.",
         "Return minimal nonoverlapping half-open intervals with positive mixed color sum, in increasing coordinate order."],
        [([[[1,4,5],[4,7,7],[1,7,9]]], "The mixed sums are fourteen on [1,4) and sixteen on [4,7)."),
         ([[[1,7,9],[6,8,15],[8,10,7]]], "The description is [1,6,9], [6,7,24], [7,8,15], and [8,10,7].")],
        [[s] for s in [[[1,2,5]],[[1,3,5],[3,5,7]],[[1,5,3],[2,4,7]],[[1,10,1],[1,10,2]],
                       [[1,4,5],[4,7,7],[1,7,9]],[[1,2,10],[3,4,20]],[[1,6,4],[2,5,8],[3,4,16]],
                       [[2,8,5],[2,4,7],[4,8,9]],[[1,3,3],[3,5,1],[3,5,2]],[[1,4,10],[2,3,20],[4,5,30]],
                       [[5,9,2],[1,6,3]],[[1,100000,1000000000]],[[1,2,1],[2,3,2],[3,4,3]],
                       [[1,5,2],[2,6,3],[3,7,5]]]],
        PAINTING,
        [PAINTING.replace("changes[right] = changes.get(right, 0) - color", "changes[right] = changes.get(right, 0) + color"),
         PAINTING.replace("if previous is not None and color:", "if previous is not None:")],
        ["Adds color at both endpoints, so colors never stop contributing.", "Emits intervals across unpainted gaps with color sum zero."],
        painting_oracle, random_painting,
        lesson("Only a segment endpoint can change the active color sum.",
               "Store +color at each start and -color at each end, then sweep endpoints in order while carrying the current sum.",
               "Before applying the delta at point x, emit [previous,x,current] when current is positive; merge an adjacent equal-sum interval.",
               "The active set is constant between consecutive endpoints, so its sum is correct throughout that interval; merging equal adjacent sums produces the minimum description."),
        "O(n log n)", "O(n)", 6),
    1944: entry(
        "visible_people_to_right", [("heights", "list[int]")], "list[int]", ["monotonic stacks", "arrays"],
        ["heights has 1 through 100000 distinct positive integers, each at most 100000.",
         "Person i sees j>i exactly when every person strictly between them is shorter than min(heights[i], heights[j]).",
         "Return one visibility count for every original queue position."],
        [([[10,6,8,5,11,9]], "The visibility counts from left to right are three, one, two, one, one, and zero."),
         ([[5,1,2,3,10]], "The first person sees heights one, two, three, and ten; each shorter person sees only its next taller blocker.")],
        [[h] for h in [[1],[1,2],[2,1],[1,2,3],[3,2,1],[10,6,8,5,11,9],[5,1,2,3,10],
                       [5,4,3,2,1],[1,5,2,4,3],[9,1,8,2,7,3],[2,9,1,8],[100000,1,99999],
                       [3,1,4,2,5],[6,2,5,1,4,3]]],
        VISIBLE,
        [VISIBLE.replace("if stack:\n            answer[index] += 1", "if False:\n            answer[index] += 1"),
         VISIBLE.replace("heights[index] > stack[-1]", "heights[index] < stack[-1]")],
        ["Counts shorter people popped from the stack but omits the first taller blocking person.", "Pops in the wrong height direction."],
        visible_oracle, random_visible,
        lesson("A person sees every shorter height removed from the right-side monotonic stack, plus the first remaining taller blocker.",
               "Scan right to left, popping and counting smaller heights; if the stack remains, count its top once; then push the current height.",
               "For each height: while taller than top, pop and increment; if nonempty increment; push height.",
               "Each popped shorter person has no intervening survivor tall enough to block it. The first unpopped taller person is visible and blocks everything behind it."),
        "O(n)", "O(n)", 8),
    1945: entry(
        "alphabet_conversion_digit_sum", [("s", "str"), ("k", "int")], "int", ["strings", "simulation"],
        ["s has 1 through 100 lowercase English letters.", "1 <= k <= 10.",
         "First concatenate each letter's one-based alphabet number, then replace the current number by its digit sum exactly k times."],
        [(["iiii",1], "Each i becomes nine, so 9999 has digit sum thirty-six."),
         (["leetcode",2], "The converted digit string sums to thirty-three, whose digits then sum to six.")],
        [[s,k] for s,k in [("a",1),("z",1),("z",2),("abc",1),("abc",2),("iiii",2),("leetcode",1),
                           ("zbax",2),("zzzz",3),("algorithm",1),("code",10),("az",1),("az",2),("xyz",4)]],
        DIGITS,
        [DIGITS.replace("ord(char) - 96", "ord(char) - 97"), DIGITS.replace("for _ in range(k):", "for _ in range(k - 1):")],
        ["Uses zero-based alphabet positions.", "Performs one fewer digit-sum transformation than requested."],
        digit_sum_oracle, random_digit_sum,
        lesson("The initial conversion is decimal concatenation, so letters ten through twenty-six contribute two digits.",
               "Build that digit string, then repeat a direct digit sum exactly k times.",
               "value=''.join(str(ord(c)-96)); repeat k: value=str(sum(int(d) for d in value)).",
               "The construction matches the required alphabet replacement digit for digit, and each loop iteration applies exactly one stated transformation to the whole current value."),
        "O(n+k*digits)", "O(n)", 3),
    1946: entry(
        "largest_mutated_number", [("num", "str"), ("change", "list[int]")], "str", ["strings", "greedy"],
        ["num has 1 through 100000 decimal digits.", "change has exactly ten replacement digits from 0 through 9.",
         "You may choose at most one contiguous substring and must replace every chosen digit d with change[d]."],
        [(["132",[9,8,5,0,3,6,4,2,6,8]], "Mutating the first two digits gives 832, the largest possible result."),
         (["021",[9,4,3,5,7,2,1,9,0,6]], "Mutating all three positions gives 934.")],
        [[n,c] for n,c in [("1",list(range(10))),("1",[9]*10),("123",list(range(10))),
                            ("132",[9,8,5,0,3,6,4,2,6,8]),("021",[9,4,3,5,7,2,1,9,0,6]),
                            ("214010",[6,7,9,7,4,0,3,4,4,7]),("999",[9]*10),("1000",[9,0,2,3,4,5,6,7,8,9]),
                            ("5551",[0,1,2,3,4,5,6,7,8,9]),("5551",[0,9,2,3,4,5,6,7,8,9]),
                            ("12345",[0,1,9,0,9,0,6,7,8,9]),("987654321",[9,8,7,6,5,4,3,2,1,0]),
                            ("109",[8,1,2,3,4,5,6,7,8,9]),("111222",[0,1,9,3,4,5,6,7,8,9])]],
        MUTATION,
        ['''def largest_mutated_number(num, change):\n    return "".join(str(max(int(char), change[int(char)])) for char in num)\n''',
         MUTATION.replace("elif replacement == original and started:", "elif False:")],
        ["Mutates profitable digits in multiple separated regions, violating the single-substring rule.",
         "Stops across equal replacements even though including them keeps the number unchanged and may reach later improvements."],
        mutation_oracle, random_mutation,
        lesson("The first increased digit dominates all later positions; after mutation begins, equal replacements may bridge to later gains but a decrease must end the substring.",
               "Skip until change[d]>d, then replace while change[d]>=d and stop permanently at the first decrease.",
               "Scan digits with a started flag: improve starts; equality continues only after start; decrease after start breaks.",
               "Starting at the earliest improvement maximizes the first changed position. Continuing through nondecreases cannot hurt, while crossing a decrease would make the first such position smaller regardless of later gains."),
        "O(n)", "O(n)", 5),
}
