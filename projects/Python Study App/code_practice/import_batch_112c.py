"""Third reviewed group of workbook batch 112."""

from functools import lru_cache
from itertools import permutations
from math import isqrt

from .import_batch_055 import entry


def compatibility_oracle(arguments):
    students, mentors = arguments
    return max(sum(sum(a == b for a, b in zip(students[index], mentors[mentor]))
                   for index, mentor in enumerate(order)) for order in permutations(range(len(mentors))))


def folders_oracle(arguments):
    root = {}
    for path in arguments[0]:
        node = root
        for name in path:
            node = node.setdefault(name, {})
    counts = {}

    def describe(node):
        signature = tuple((name, describe(child)) for name, child in sorted(node.items()))
        if signature:
            counts[signature] = counts.get(signature, 0) + 1
        return signature

    signatures = {}

    def record(node):
        signature = tuple((name, record(child)) for name, child in sorted(node.items()))
        signatures[id(node)] = signature
        return signature

    describe(root)
    record(root)
    answer = []

    def visit(node, path):
        for name, child in node.items():
            signature = signatures[id(child)]
            if signature and counts[signature] > 1:
                continue
            answer.append(path + [name])
            visit(child, path + [name])

    visit(root, [])
    return sorted(answer)


def window_oracle(arguments):
    nums = arguments[0]
    answer = []
    for width in range(1, len(nums) + 1):
        answer.append(max(min(nums[left:left + width]) for left in range(len(nums) - width + 1)))
    return answer


def divisors_oracle(arguments):
    number = arguments[0]
    return sum(number % candidate == 0 for candidate in range(1, number + 1)) == 3


def weeks_oracle(arguments):
    milestones = tuple(arguments[0])
    if sum(milestones) > 20:
        total, largest = sum(milestones), max(milestones)
        return min(total, 2 * (total - largest) + 1)

    @lru_cache(maxsize=None)
    def search(remaining, previous):
        best = 0
        for project, amount in enumerate(remaining):
            if amount and project != previous:
                following = list(remaining)
                following[project] -= 1
                best = max(best, 1 + search(tuple(following), project))
        return best

    return search(milestones, -1)


def random_compatibility(rng):
    people, questions = rng.randint(1, 6), rng.randint(1, 7)
    matrix = lambda: [[rng.randint(0, 1) for _ in range(questions)] for _ in range(people)]
    return [matrix(), matrix()]


def random_folders(rng):
    paths = [[rng.choice("abc")]]
    seen = {tuple(paths[0])}
    for _ in range(rng.randint(1, 15)):
        parent = rng.choice([()] + list(seen))
        candidates = [name for name in "abcxyz" if parent + (name,) not in seen]
        if not candidates:
            continue
        path = parent + (rng.choice(candidates),)
        for length in range(1, len(path) + 1):
            prefix = path[:length]
            if prefix not in seen:
                seen.add(prefix)
                paths.append(list(prefix))
    return [paths]


def random_window(rng):
    return [[rng.randint(0, 50) for _ in range(rng.randint(1, 30))]]


def random_divisors(rng):
    return [rng.randint(1, 10_000)]


def random_weeks(rng):
    return [[rng.randint(1, 6) for _ in range(rng.randint(1, 6))]]


COMPATIBILITY = '''\
def maximum_compatibility_sum(students, mentors):
    people = len(students)
    scores = [[sum(a == b for a, b in zip(student, mentor)) for mentor in mentors] for student in students]
    best = [-1] * (1 << people)
    best[0] = 0
    for mask in range(1 << people):
        student = mask.bit_count()
        if student == people or best[mask] < 0:
            continue
        for mentor in range(people):
            if not mask >> mentor & 1:
                following = mask | 1 << mentor
                best[following] = max(best[following], best[mask] + scores[student][mentor])
    return best[-1]
'''

FOLDERS = '''\
def delete_duplicate_folders(paths):
    root = {}
    for path in paths:
        node = root
        for name in path:
            node = node.setdefault(name, {})
    signatures = {}
    counts = {}

    def encode(node):
        children = tuple((name, encode(child)) for name, child in sorted(node.items()))
        signature = children
        signatures[id(node)] = signature
        if signature:
            counts[signature] = counts.get(signature, 0) + 1
        return signature

    encode(root)
    answer = []

    def collect(node, path):
        for name, child in node.items():
            signature = signatures[id(child)]
            if signature and counts[signature] > 1:
                continue
            answer.append(path + [name])
            collect(child, path + [name])

    collect(root, [])
    return answer
'''

WINDOWS = '''\
def maximum_of_window_minimums(nums):
    size = len(nums)
    left = [-1] * size
    stack = []
    for index, value in enumerate(nums):
        while stack and nums[stack[-1]] >= value:
            stack.pop()
        left[index] = stack[-1] if stack else -1
        stack.append(index)
    right = [size] * size
    stack = []
    for index in range(size - 1, -1, -1):
        while stack and nums[stack[-1]] > nums[index]:
            stack.pop()
        right[index] = stack[-1] if stack else size
        stack.append(index)
    answer = [-1] * size
    for index, value in enumerate(nums):
        width = right[index] - left[index] - 1
        answer[width - 1] = max(answer[width - 1], value)
    for index in range(size - 2, -1, -1):
        answer[index] = max(answer[index], answer[index + 1])
    return answer
'''

DIVISORS = '''\
def has_exactly_three_divisors(n):
    from math import isqrt
    root = isqrt(n)
    if root * root != n or root < 2:
        return False
    return all(root % divisor for divisor in range(2, isqrt(root) + 1))
'''

WEEKS = '''\
def maximum_work_weeks(milestones):
    total = sum(milestones)
    largest = max(milestones)
    others = total - largest
    return total if largest <= others + 1 else 2 * others + 1
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


BATCH = {
    1947: entry(
        "maximum_compatibility_sum", [("students", "list[list[int]]"), ("mentors", "list[list[int]]")], "int",
        ["dynamic programming", "bitmasking", "matching"],
        ["students and mentors each contain m answer rows, with 1 <= m <= 8.", "Every row has the same 1 through 8 binary answers.",
         "Pair every student with a distinct mentor and maximize the total number of equal answer positions."],
        [([[[1,1,0],[1,0,1],[0,0,1]],[[1,0,0],[0,0,1],[1,1,0]]], "An optimal one-to-one assignment has total compatibility eight."),
         ([[[0,0],[0,0],[0,0]],[[1,1],[1,1],[1,1]]], "Every pairing scores zero, so the total is zero.")],
        [[s,m] for s,m in [([[0]],[[0]]),([[0]],[[1]]),([[0],[1]],[[0],[1]]),([[0],[1]],[[1],[0]]),
                            ([[0,1],[1,0]],[[0,1],[1,0]]),([[0,0],[1,1]],[[0,1],[1,0]]),
                            ([[1,1,0],[1,0,1],[0,0,1]],[[1,0,0],[0,0,1],[1,1,0]]),
                            ([[0,0],[0,0],[0,0]],[[1,1],[1,1],[1,1]]),
                            ([[1,0,1],[0,1,0]],[[1,1,1],[0,0,0]]),([[1,1],[1,0],[0,0]],[[0,0],[1,1],[0,1]]),
                            ([[1,0,0],[0,1,0],[0,0,1]],[[1,0,0],[0,1,0],[0,0,1]]),
                            ([[1,1,1],[0,0,0],[1,0,1]],[[0,0,0],[1,1,1],[1,0,1]]),
                            ([[0,1,0,1],[1,0,1,0]],[[1,0,1,0],[0,1,0,1]]),
                            ([[1,0],[1,0],[0,1],[0,1]],[[1,0],[0,1],[1,1],[0,0]])]],
        COMPATIBILITY,
        ['''def maximum_compatibility_sum(students, mentors):\n    return sum(max(sum(a == b for a, b in zip(student, mentor)) for mentor in mentors) for student in students)\n''',
         '''def maximum_compatibility_sum(students, mentors):\n    return sum(sum(a == b for a, b in zip(student, mentor)) for student, mentor in zip(students, mentors))\n'''],
        ["Lets multiple students reuse the same best mentor.", "Uses only the input order instead of optimizing the one-to-one assignment."],
        compatibility_oracle, random_compatibility,
        lesson("A bitmask of used mentors captures everything needed after assigning the first k students.",
               "Precompute pair scores; for each mask, k=popcount(mask), and try each unused mentor for student k.",
               "dp[mask]=best score; update dp[mask|1<<mentor] with the next student's compatibility.",
               "Every perfect matching has one unique sequence of growing masks, and every transition preserves distinct mentors, so the final full mask maximizes exactly the legal assignments."),
        "O(m^2*2^m)", "O(2^m+m^2)", 6),
    1948: entry(
        "delete_duplicate_folders", [("paths", "list[list[str]]")], "list[list[str]]", ["trees", "tries", "hash maps", "depth-first search"],
        ["paths contains 1 through 20000 distinct absolute folder paths, and every non-root folder's parent is included.",
         "Folder names have 1 through 10 lowercase letters; total name characters are at most 200000.",
         "Two nonempty folders are duplicates when their complete nonempty child-name/subtree structures match; mark once, delete marked folders and descendants, and return remaining paths in any order."],
        [([[['a'],['c'],['d'],['a','b'],['c','b'],['d','a']]], "Folders a and c both contain only an empty b folder, so both subtrees are removed and d with d/a remains."),
         ([[['a'],['c'],['a','b'],['c','b'],['a','b','x'],['c','b','x'],['a','b','x','y']]], "The b subtrees differ because only a/b/x has child y, so no folder is deleted.")],
        [[p] for p in [[['a']],[['a'],['b']],[['a'],['a','x'],['b'],['b','x']],
                       [['a'],['b'],['a','x'],['b','y']],[['a'],['b'],['a','x'],['b','x'],['a','x','z'],['b','x','z']],
                       [['a'],['c'],['d'],['a','b'],['c','b'],['d','a']],
                       [['a'],['b'],['c'],['a','x'],['b','x'],['c','y']],
                       [['a'],['a','b'],['a','c']],[['a'],['b'],['a','x'],['b','x'],['b','y']],
                       [['a'],['b'],['a','x'],['b','x'],['a','x','p'],['b','x','q']],
                       [['a'],['b'],['a','x'],['b','x'],['a','x','p'],['b','x','p']],
                       [['root'],['root','a'],['root','b'],['root','a','x'],['root','b','x']],
                       [['a'],['b'],['a','x'],['a','y'],['b','x'],['b','y']],
                       [['a'],['b'],['c'],['a','x'],['b','x'],['c','x'],['c','x','z']]]],
        FOLDERS,
        [FOLDERS.replace("if signature:\n            counts[signature]", "if True:\n            counts[signature]").replace(
            "if signature and counts[signature] > 1:", "if counts[signature] > 1:"),
         '''def delete_duplicate_folders(paths):\n    children = {}\n    for path in paths:\n        children.setdefault(tuple(path[:-1]), set()).add(path[-1])\n    repeated = {frozenset(names) for names in children.values() if sum(set(other) == names for other in children.values()) > 1}\n    return [path for path in paths if frozenset(children.get(tuple(path), set())) not in repeated]\n'''],
        ["Treats all leaf folders as duplicate empty structures, although duplicate folders must contain at least one subfolder.",
         "Compares only immediate child names and ignores deeper descendant structure and subtree deletion."],
        folders_oracle, random_folders,
        lesson("A folder's complete structure has a canonical bottom-up signature made from each child name paired with that child's signature.",
               "Build a trie, count every nonempty subtree signature, then traverse again while skipping roots whose signature count exceeds one.",
               "encode children in sorted-name order; count nonempty encodings; collect paths unless the child's encoding is duplicated.",
               "Equal canonical signatures are equivalent exactly when all named descendants match recursively. Counting precedes deletion, so folders made equal only afterward are correctly retained."),
        "O(total characters log degree)", "O(total characters)", 8),
    1950: entry(
        "maximum_of_window_minimums", [("nums", "list[int]")], "list[int]", ["arrays", "monotonic stacks"],
        ["nums has 1 through 100000 values from 0 through 1000000000.",
         "For every window size 1..n, return the largest among all window minimums.", "Output index width-1 corresponds to that window width."],
        [([[0,1,2,4]], "The best minimums for widths one through four are four, two, one, and zero."),
         ([[10,20,50,10]], "The best minimums are fifty, twenty, ten, and ten.")],
        [[a] for a in [[0],[5],[1,2],[2,1],[1,1],[0,1,2,4],[10,20,50,10],[4,3,2,1],[1,2,3,4],
                       [2,2,2,2],[3,1,4,1,5],[1000000000,0,1000000000],[5,4,5,4,5],[8,1,7,2,6,3,5,4]]],
        WINDOWS,
        [WINDOWS.replace("answer[index] = max(answer[index], answer[index + 1])", "answer[index] = answer[index + 1]"),
         WINDOWS.replace("for index in range(size - 2, -1, -1):", "return answer\n    for index in range(size - 2, -1, -1):")],
        ["Overwrites a known smaller-window candidate instead of taking its maximum with the propagated larger-window answer.",
         "Returns only widths that were maximal spans for some element and never propagates larger-window minima to smaller widths."],
        window_oracle, random_window,
        lesson("Each value is the minimum of the widest interval bounded by the nearest strictly smaller value on each side.",
               "Use monotonic stacks for those boundaries, place each value at its maximum supported width, then propagate answers from larger widths downward.",
               "Find left smaller and right smaller-or-equal; update answer[width-1]; scan backward taking max with answer[next].",
               "Every window minimum supports its window width, and its maximal span records that support. Any value valid for a larger width is also attainable for every smaller width, justifying backward propagation."),
        "O(n)", "O(n)", 6),
    1952: entry(
        "has_exactly_three_divisors", [("n", "int")], "bool", ["math", "number theory"],
        ["1 <= n <= 10000.", "Count positive divisors, including one and n itself.",
         "Return true exactly when the total divisor count is three."],
        [([2], "Two has only divisors one and two, so the answer is false."),
         ([4], "Four has exactly divisors one, two, and four.")],
        [[n] for n in [1,3,5,8,9,16,25,27,36,49,64,81,121,10000]],
        DIVISORS,
        [DIVISORS.replace("root * root != n", "root * root == n"), DIVISORS.replace("range(2, isqrt(root) + 1)", "range(2, isqrt(root))")],
        ["Rejects perfect squares instead of requiring them.", "Misses a possible divisor exactly at the square root of the candidate root."],
        divisors_oracle, random_divisors,
        lesson("A number has exactly three divisors precisely when it is the square of a prime.",
               "Check that n is a perfect square, then test its integer square root for primality.",
               "r=isqrt(n); require r*r==n and no divisor from 2 through isqrt(r).",
               "Divisors normally pair. Exactly one unpaired middle divisor requires a square p^2, and having only 1,p,p^2 requires p to be prime."),
        "O(sqrt(sqrt(n)))", "O(1)", 3),
    1953: entry(
        "maximum_work_weeks", [("milestones", "list[int]")], "int", ["arrays", "greedy"],
        ["milestones has 1 through 100000 positive counts, each at most 1000000000.",
         "Complete one milestone per week and never use the same project in consecutive weeks.",
         "Return the maximum schedulable number of weeks; you may stop before every milestone is completed."],
        [([[1,2,3]], "The projects can be alternated to complete all six milestones."),
         ([[5,2,1]], "The three milestones from other projects can separate four from the largest project, giving seven weeks.")],
        [[m] for m in [[1],[2],[1,1],[1,2],[1,3],[1,2,3],[5,2,1],[10,1],[4,4,4],[7,3,2],
                       [1000000000],[1000000000,1000000000],[1000000000,1,1],[2,2,1,1]]],
        WEEKS,
        [WEEKS.replace("2 * others + 1", "2 * others + 2"), WEEKS.replace("2 * others + 1", "2 * others")],
        ["Allows two more largest-project milestones than the available separators can support.", "Omits the final largest-project week in an imbalanced schedule."],
        weeks_oracle, random_weeks,
        lesson("Only the largest project can run out of separators; all smaller projects together supply those separators.",
               "Let largest=M and others=S. If M<=S+1, schedule everything; otherwise alternate S other milestones with S+1 from the largest.",
               "Return total when largest<=others+1, else 2*others+1.",
               "The balanced condition permits a full alternating arrangement. In the imbalanced case each non-largest milestone separates at most two largest-project weeks, proving both the upper bound and the alternating construction."),
        "O(n)", "O(1)", 5),
}

BATCH[1948]["comparator"] = "unordered"
BATCH[1952]["sample_contract_adapter"] = {
    "source_sample": "Input n = 2 → Output false Explantion: 2 has only two divisors: 1 and 2.",
    "arguments": [2],
    "expected": False,
    "reason": "The workbook appends misspelled explanation prose directly after the boolean output, so the raw output is not a parseable literal; the stated input and boolean are preserved.",
}
