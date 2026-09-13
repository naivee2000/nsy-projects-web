"""Reviewed hash-map, dynamic-programming, greedy, heap, and math imports."""
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from math import factorial, isqrt

from .import_batch_055 import entry


def duplicate_files_oracle(args):
    groups = defaultdict(list)
    for description in args[0]:
        directory, *files = description.split()
        for file_data in files:
            opening = file_data.index("(")
            groups[file_data[opening + 1:-1]].append(directory + "/" + file_data[:opening])
    return [paths for paths in groups.values() if len(paths) >= 2]


def inverse_pairs_oracle(args):
    n, wanted = args
    if wanted < 0 or wanted > n * (n - 1) // 2:
        return 0
    counts = [1]
    for size in range(1, n + 1):
        following = [0] * (min(wanted, size * (size - 1) // 2) + 1)
        for previous, ways in enumerate(counts):
            for added in range(size):
                if previous + added < len(following):
                    following[previous + added] += ways
        counts = following
    return counts[wanted] % 1_000_000_007 if wanted < len(counts) else 0


def courses_oracle(args):
    courses = args[0]
    for size in range(len(courses), -1, -1):
        for chosen in combinations(courses, size):
            elapsed = 0
            feasible = True
            for duration, deadline in sorted(chosen, key=lambda course: course[1]):
                elapsed += duration
                if elapsed > deadline:
                    feasible = False
                    break
            if feasible:
                return size
    return 0


def range_oracle(args):
    best = None
    for selected in product(*args[0]):
        candidate = [min(selected), max(selected)]
        if best is None or (candidate[1] - candidate[0], candidate[0]) < (best[1] - best[0], best[0]):
            best = candidate
    return best


def square_sum_oracle(args):
    c = args[0]
    squares = {value * value for value in range(isqrt(c) + 1)}
    return any(c - square in squares for square in squares)


def derangement_oracle(args):
    n = args[0]
    # Inclusion-exclusion: n! * sum((-1)^i / i!), evaluated with integers.
    total = 0
    for fixed in range(n + 1):
        term = factorial(n) // factorial(fixed)
        total += term if fixed % 2 == 0 else -term
    return total % 1_000_000_007


def random_duplicate_files(rng):
    contents = ["".join(rng.choice("abcd") for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(1, 5))]
    rows = []
    serial = 0
    for directory_index in range(rng.randint(1, 5)):
        files = []
        for _ in range(rng.randint(1, 4)):
            serial += 1
            files.append(f"f{serial}.txt({rng.choice(contents)})")
        rows.append(f"root/d{directory_index} " + " ".join(files))
    return [rows]


def random_inverse_pairs(rng):
    n = rng.randint(1, 7)
    return [n, rng.randint(0, n * (n - 1) // 2 + 2)]


def random_courses(rng):
    return [[[rng.randint(1, 12), rng.randint(1, 35)] for _ in range(rng.randint(1, 9))]]


def random_ranges(rng):
    lists = []
    for _ in range(rng.randint(1, 4)):
        lists.append(sorted({rng.randint(-15, 15) for _ in range(rng.randint(1, 4))}))
    return [lists]


def random_square_sum(rng):
    return [rng.randint(0, 50_000)]


def random_derangement(rng):
    return [rng.randint(1, 30)]


DUPLICATES = '''\
def find_duplicate_files(paths):
    from collections import defaultdict
    groups = defaultdict(list)
    for description in paths:
        directory, *files = description.split()
        for file_data in files:
            opening = file_data.index('(')
            content = file_data[opening + 1:-1]
            groups[content].append(directory + '/' + file_data[:opening])
    return [group for group in groups.values() if len(group) > 1]
'''


INVERSE_PAIRS = '''\
def count_inverse_pair_arrays(n, k):
    mod = 1_000_000_007
    counts = [1] + [0] * k
    for size in range(1, n + 1):
        prefix = [0]
        for ways in counts:
            prefix.append((prefix[-1] + ways) % mod)
        counts = [(prefix[inversions + 1] - prefix[max(0, inversions - size + 1)]) % mod
                  for inversions in range(k + 1)]
    return counts[k]
'''


COURSES = '''\
def maximum_courses(courses):
    import heapq
    selected = []
    elapsed = 0
    for duration, deadline in sorted(courses, key=lambda course: course[1]):
        heapq.heappush(selected, -duration)
        elapsed += duration
        if elapsed > deadline:
            elapsed += heapq.heappop(selected)
    return len(selected)
'''


SMALLEST_RANGE = '''\
def smallest_covering_range(nums):
    import heapq
    heap = []
    current_max = -float('inf')
    for list_index, values in enumerate(nums):
        heapq.heappush(heap, (values[0], list_index, 0))
        current_max = max(current_max, values[0])
    best = [heap[0][0], current_max]
    while True:
        current_min, list_index, value_index = heapq.heappop(heap)
        if (current_max - current_min, current_min) < (best[1] - best[0], best[0]):
            best = [current_min, current_max]
        if value_index + 1 == len(nums[list_index]):
            return best
        following = nums[list_index][value_index + 1]
        current_max = max(current_max, following)
        heapq.heappush(heap, (following, list_index, value_index + 1))
'''


SQUARE_SUM = '''\
def is_square_sum(c):
    from math import isqrt
    left, right = 0, isqrt(c)
    while left <= right:
        value = left * left + right * right
        if value == c:
            return True
        if value < c:
            left += 1
        else:
            right -= 1
    return False
'''


DERANGEMENTS = '''\
def count_derangements(n):
    mod = 1_000_000_007
    previous_two, previous_one = 1, 0
    for size in range(2, n + 1):
        previous_two, previous_one = previous_one, (size - 1) * (previous_one + previous_two) % mod
    return previous_one
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial], editorial


BATCH = {
    609: entry('find_duplicate_files', [('paths', 'list[str]')], 'list[list[str]]', ['hash-maps', 'strings'],
        ['1 <= len(paths) <= 20,000; each directory description contains at least one file.', 'Return only content groups containing at least two paths; group and path order do not matter.'],
        [([['root/a 1.txt(abcd) 2.txt(efgh)', 'root/c 3.txt(abcd)', 'root/c/d 4.txt(efgh)', 'root 4.txt(efgh)']], 'Files with content abcd form one group, while the three efgh files form the other.'),
         ([['root/a 1.txt(x) 2.txt(y)', 'root/b 3.txt(z)']], 'All contents are unique, so there are no duplicate groups.')],
        [[[row]] for row in ('root/a 1.txt(x) root.txt(y)', 'r a.txt(x) b.txt(x)', 'r a.txt(x) b.txt(y) c.txt(x)', 'root/a same.txt(1) other.txt(2)', 'root a(abc) b(abc)', 'x/y a.txt(k) b.txt(k) c.txt(k)', 'a f.txt() b.txt()', 'a f.txt(space) b.txt(space)', 'a one.txt(123) two.txt(456)', 'a 1.txt(q) 2.txt(w) 3.txt(e)', 'deep/path z.txt(content)', 'a x.txt(A) y.txt(a)')],
        DUPLICATES,
        [DUPLICATES.replace('if len(group) > 1', 'if len(group) >= 1'),
         DUPLICATES.replace('groups[content].append', 'groups[file_data[:opening]].append')],
        ['Returns singleton content groups instead of duplicates only.', 'Groups files by filename rather than file content.'], duplicate_files_oracle, random_duplicate_files,
        *lesson('File content is the grouping key.', 'Parse each file token and map its content to the complete path.', 'For every token, split name from parenthesized content; return map values of size at least two.', 'A hash map gathers files that are far apart in the input without comparing every pair.'), 'O(total input characters)', 'O(total input characters)', 5),
    629: entry('count_inverse_pair_arrays', [('n', 'int'), ('k', 'int')], 'int', ['dynamic-programming', 'combinatorics'],
        ['1 <= n <= 1,000; 0 <= k <= 1,000.', 'Count permutations of 1 through n with exactly k inverse pairs; return the result modulo 1,000,000,007.'],
        [([3, 0], 'Only [1,2,3] has no inverse pairs.'), ([3, 1], 'The permutations [1,3,2] and [2,1,3] each have one inverse pair.')],
        [[n, k] for n, k in ((1,1),(2,0),(2,1),(2,2),(3,2),(3,3),(4,1),(4,3),(4,6),(5,5),(10,12),(50,200))],
        INVERSE_PAIRS,
        [INVERSE_PAIRS.replace('inversions - size + 1', 'inversions - size + 2'),
         INVERSE_PAIRS.replace(" % mod\n                  for inversions", "\n                  for inversions")],
        ['Allows one too few insertion positions in each transition.', 'Does not reduce the rapidly growing count modulo the required value.'], inverse_pairs_oracle, random_inverse_pairs,
        *lesson('Inserting the new largest value adds from zero through size minus one inversions.', 'Use dynamic programming and a sliding prefix sum over the previous row.', 'For each size and k, sum the previous counts from k-size+1 through k.', 'The direct transition is correct but cubic; prefix differences reduce every range sum to constant time.'), 'O(n * k)', 'O(k)', 8),
    630: entry('maximum_courses', [('courses', 'list[list[int]]')], 'int', ['greedy', 'sorting', 'heaps'],
        ['1 <= len(courses) <= 10,000; each course is [duration, deadline] with positive integers.', 'Courses run continuously from day one; return the maximum number that can finish by their deadlines.'],
        [([[[100,200],[200,1300],[1000,1250],[2000,3200]]], 'Taking durations 100, 1000, and 200 meets all three deadlines.'),
         ([[[3,2],[4,3]]], 'Each course alone exceeds its own deadline, so none can be completed.')],
        [[courses] for courses in ([[1,2]],[[1,1]],[[2,1]],[[1,2],[2,3]],[[2,2],[1,2]],[[5,5],[4,6],[2,6]],[[3,5],[2,6],[4,6]],[[10,20],[5,5],[4,6]],[[2,5],[2,5],[2,5]],[[8,9],[1,10],[1,10]],[[7,7],[6,13],[5,18]],[[4,3],[3,10],[2,5],[1,4]])],
        COURSES,
        [COURSES.replace("if elapsed > deadline:\n            elapsed += heapq.heappop(selected)", "if elapsed > deadline:\n            heapq.heappop(selected)"),
         COURSES.replace("sorted(courses, key=lambda course: course[1])", "sorted(courses, key=lambda course: course[0])")],
        ['Removes a course but forgets to subtract its duration from elapsed time.', 'Processes shortest durations first instead of respecting deadline order.'], courses_oracle, random_courses,
        *lesson('When a deadline is missed, discard the longest selected duration.', 'Process deadlines in order and keep selected durations in a max-heap.', 'Add each course; if total time exceeds its deadline, remove the longest course.', 'Replacing the longest course preserves the count while leaving the most time for every future deadline.'), 'O(n log n)', 'O(n)', 8),
    632: entry('smallest_covering_range', [('nums', 'list[list[int]]')], 'list[int]', ['heaps', 'two-pointers', 'arrays'],
        ['1 <= len(nums) <= 3,500; every inner list is nonempty and sorted.', 'The range must contain at least one value from every list; break equal-width ties by the smaller left endpoint.'],
        [([[[4,10,15,24,26],[0,9,12,20],[5,18,22,30]]], 'The range [20,24] contains 24, 20, and 22 from the three lists.'),
         ([[[1,2,3],[1,2,3],[1,2,3]]], 'The single-point range [1,1] touches every list.')],
        [[lists] for lists in ([[1]],[[1],[2]],[[1,5],[2,4]],[[0,10],[1,9],[2,8]],[[1,2],[3,4],[5,6]],[[1,10],[2,9],[3,8]],[[0,4],[2,6],[3,5]],[[1,1],[1],[1,2]], [[-10,-5],[-8,-4],[-7,-3]], [[1,4,7],[2,5,8]], [[0,100],[20,30],[25]], [[1,3],[2,4]])],
        SMALLEST_RANGE,
        [SMALLEST_RANGE.replace("current_max = max(current_max, following)", "current_max = following"),
         SMALLEST_RANGE.replace("(current_max - current_min, current_min) <", "(current_max - current_min, -current_min) <")],
        ['Loses the maximum contributed by another list when advancing the minimum.', 'Breaks equal-width ties in favor of the larger left endpoint.'], range_oracle, random_ranges,
        *lesson('A candidate range is determined by the current minimum and maximum across one value per list.', 'Keep one cursor per sorted list in a min-heap and remember the current maximum.', 'Pop the minimum, update the answer, then advance only that value’s list.', 'Only advancing the list holding the minimum can shrink the range; stopping at an exhausted list is unavoidable.'), 'O(total values * log number of lists)', 'O(number of lists)', 8),
    633: entry('is_square_sum', [('c', 'int')], 'bool', ['math', 'two-pointers', 'binary-search'],
        ['0 <= c <= 2^31 - 1.', 'Return true when two nonnegative integers a and b satisfy a² + b² = c.'],
        [([5], 'One squared plus two squared equals five.'), ([3], 'No pair of integer squares sums to three.')],
        [[value] for value in (0,1,2,4,8,9,10,13,25,27,50,2_147_483_647)],
        SQUARE_SUM,
        [SQUARE_SUM.replace('left, right = 0, isqrt(c)', 'left, right = 1, isqrt(c)'),
         SQUARE_SUM.replace('while left <= right:', 'while left < right:')],
        ['Excludes representations that use zero.', 'Excludes representations using the same integer twice.'], square_sum_oracle, random_square_sum,
        *lesson('The sum increases with the smaller pointer and decreases with the larger pointer.', 'Start at zero and the integer square root, then move one bound at a time.', 'Compare left²+right² with c; increase left if low, otherwise decrease right.', 'Monotonic movement eliminates an entire row or column of candidate pairs at each step.'), 'O(sqrt(c))', 'O(1)', 5),
    634: entry('count_derangements', [('n', 'int')], 'int', ['dynamic-programming', 'combinatorics'],
        ['1 <= n <= 1,000,000.', 'Count permutations in which no value remains in its original position; return modulo 1,000,000,007.'],
        [([3], 'The valid permutations are [2,3,1] and [3,1,2].'), ([2], 'Only [2,1] moves both values away from their original positions.')],
        [[n] for n in (1,4,5,6,7,8,9,10,20,50,100,1000)],
        DERANGEMENTS,
        [DERANGEMENTS.replace('previous_two, previous_one = 1, 0', 'previous_two, previous_one = 1, 1'),
         DERANGEMENTS.replace('(size - 1) * (previous_one + previous_two)', '(previous_one + previous_two)')],
        ['Uses one derangement for a one-element array.', 'Omits the size-minus-one choices in the recurrence.'], derangement_oracle, random_derangement,
        *lesson('Place the first value elsewhere, then distinguish whether that displaced value returns to position one.', 'Use D(n) = (n-1) * (D(n-1) + D(n-2)).', 'Start with D(0)=1 and D(1)=0; roll the recurrence through n modulo the limit.', 'The two cases correspond to closing a two-cycle or leaving the displaced position for a larger derangement.'), 'O(n)', 'O(1)', 5),
}

BATCH[609]["comparator"] = "unordered_nested"
