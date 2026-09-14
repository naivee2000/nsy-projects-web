"""Second reviewed group of workbook batch 111."""

from itertools import combinations, permutations
from math import hypot

from .import_batch_055 import entry


def permutation_oracle(arguments):
    nums = arguments[0]
    return [nums[nums[index]] for index in range(len(nums))]


def monsters_oracle(arguments):
    distances, speeds = arguments
    arrivals = sorted((distance + speed - 1) // speed for distance, speed in zip(distances, speeds))
    for minute, arrival in enumerate(arrivals):
        if arrival <= minute:
            return minute
    return len(arrivals)


def good_numbers_oracle(arguments):
    n = arguments[0]
    return pow(5, (n + 1) // 2, 1_000_000_007) * pow(4, n // 2, 1_000_000_007) % 1_000_000_007


def common_subpath_oracle(arguments):
    _, paths = arguments
    for length in range(min(map(len, paths)), -1, -1):
        common = None
        for path in paths:
            pieces = {tuple(path[start:start + length]) for start in range(len(path) - length + 1)}
            common = pieces if common is None else common & pieces
        if common:
            return length
    return 0


def circle_from_pair(first, second):
    center_x = (first[0] + second[0]) / 2
    center_y = (first[1] + second[1]) / 2
    return center_x, center_y, hypot(first[0] - second[0], first[1] - second[1]) / 2


def circle_from_three(first, second, third):
    ax, ay = first
    bx, by = second
    cx, cy = third
    denominator = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(denominator) < 1e-12:
        return None
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay)
          + (cx * cx + cy * cy) * (ay - by)) / denominator
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx)
          + (cx * cx + cy * cy) * (bx - ax)) / denominator
    return ux, uy, hypot(ux - ax, uy - ay)


def encloses(circle, points):
    return all(hypot(point[0] - circle[0], point[1] - circle[1]) <= circle[2] + 1e-8 for point in points)


def fence_oracle(arguments):
    points = arguments[0]
    candidates = [(float(x), float(y), 0.0) for x, y in points]
    candidates += [circle_from_pair(first, second) for first, second in combinations(points, 2)]
    candidates += [circle for triple in combinations(points, 3)
                   if (circle := circle_from_three(*triple)) is not None]
    best = min((circle for circle in candidates if encloses(circle, points)), key=lambda circle: circle[2])
    return list(best)


def random_permutation(rng):
    nums = list(range(rng.randint(1, 20)))
    rng.shuffle(nums)
    return [nums]


def random_monsters(rng):
    length = rng.randint(1, 15)
    return [[rng.randint(1, 30) for _ in range(length)], [rng.randint(1, 10) for _ in range(length)]]


def random_good_numbers(rng):
    return [rng.randint(1, 10**15)]


def random_paths(rng):
    city_count = rng.randint(2, 10)
    paths = []
    for _ in range(rng.randint(2, 6)):
        path = [rng.randrange(city_count)]
        for _ in range(rng.randint(0, 9)):
            choices = [city for city in range(city_count) if city != path[-1]]
            path.append(rng.choice(choices))
        paths.append(path)
    return [city_count, paths]


def random_fence(rng):
    count = rng.randint(1, 8)
    points = rng.sample([(x, y) for x in range(8) for y in range(8)], count)
    return [[list(point) for point in points]]


PERMUTATION = '''\
def build_array_from_permutation(nums):
    return [nums[value] for value in nums]
'''

MONSTERS = '''\
def eliminate_maximum_monsters(dist, speed):
    latest_minutes = sorted((distance - 1) // velocity for distance, velocity in zip(dist, speed))
    for minute, latest in enumerate(latest_minutes):
        if latest < minute:
            return minute
    return len(latest_minutes)
'''

MONSTERS_DISTANCE = '''\
def eliminate_maximum_monsters(dist, speed):
    answer=0
    for minute,index in enumerate(sorted(range(len(dist)),key=lambda i:dist[i])):
        if dist[index] <= minute*speed[index]:return answer
        answer+=1
    return answer
'''

GOOD_NUMBERS = '''\
def count_good_digit_strings(n):
    modulus = 1_000_000_007
    def power(base, exponent):
        if exponent == 0:
            return 1
        half = power(base, exponent // 2)
        result = half * half % modulus
        return result * base % modulus if exponent % 2 else result
    even_positions = (n + 1) // 2
    odd_positions = n // 2
    return power(5, even_positions) * power(4, odd_positions) % modulus
'''

COMMON_PATH = '''\
def longest_common_city_subpath(n, paths):
    moduli = (1_000_000_007, 1_000_000_009)
    base = 911382323
    maximum = max(map(len, paths))
    powers = []
    for modulus in moduli:
        current = [1] * (maximum + 1)
        for index in range(1, maximum + 1):
            current[index] = current[index - 1] * base % modulus
        powers.append(current)
    def hashes(path, length):
        if length == 0:
            return {(0, 0)}
        result = set()
        rolling = [0, 0]
        for index, city in enumerate(path):
            for part, modulus in enumerate(moduli):
                rolling[part] = (rolling[part] * base + city + 1) % modulus
                if index >= length:
                    rolling[part] = (rolling[part] - (path[index - length] + 1) * powers[part][length]) % modulus
            if index + 1 >= length:
                result.add(tuple(rolling))
        return result
    ordered = sorted(paths, key=len)
    def shared(length):
        common = hashes(ordered[0], length)
        for path in ordered[1:]:
            common &= hashes(path, length)
            if not common:
                return False
        return bool(common)
    left, right = 0, len(ordered[0])
    while left < right:
        middle = (left + right + 1) // 2
        if shared(middle):
            left = middle
        else:
            right = middle - 1
    return left
'''

COMMON_CITIES = '''\
def longest_common_city_subpath(n, paths):
    common=set(paths[0])
    for path in paths[1:]:common &= set(path)
    return len(common)
'''

FENCE = '''\
def minimum_enclosing_fence_circle(trees):
    from math import hypot
    from random import Random
    points = [tuple(map(float, point)) for point in trees]
    Random(1924).shuffle(points)
    def inside(circle, point):
        return hypot(point[0] - circle[0], point[1] - circle[1]) <= circle[2] + 1e-9
    def pair(first, second):
        x = (first[0] + second[0]) / 2
        y = (first[1] + second[1]) / 2
        return x, y, hypot(first[0] - second[0], first[1] - second[1]) / 2
    def three(first, second, third):
        ax, ay = first; bx, by = second; cx, cy = third
        denominator = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(denominator) < 1e-12:
            candidates = [pair(first, second), pair(first, third), pair(second, third)]
            return min((circle for circle in candidates if all(inside(circle, point) for point in (first, second, third))), key=lambda circle: circle[2])
        x = ((ax*ax + ay*ay) * (by-cy) + (bx*bx + by*by) * (cy-ay) + (cx*cx + cy*cy) * (ay-by)) / denominator
        y = ((ax*ax + ay*ay) * (cx-bx) + (bx*bx + by*by) * (ax-cx) + (cx*cx + cy*cy) * (bx-ax)) / denominator
        return x, y, hypot(x-ax, y-ay)
    circle = (points[0][0], points[0][1], 0.0)
    for first_index, first in enumerate(points):
        if inside(circle, first):
            continue
        circle = (first[0], first[1], 0.0)
        for second_index in range(first_index):
            second = points[second_index]
            if inside(circle, second):
                continue
            circle = pair(first, second)
            for third_index in range(second_index):
                third = points[third_index]
                if not inside(circle, third):
                    circle = three(first, second, third)
    return list(circle)
'''

FENCE_CENTROID = '''\
def minimum_enclosing_fence_circle(trees):
    from math import hypot
    x=sum(p[0] for p in trees)/len(trees);y=sum(p[1] for p in trees)/len(trees)
    return [x,y,max(hypot(p[0]-x,p[1]-y) for p in trees)]
'''

FENCE_BOX = '''\
def minimum_enclosing_fence_circle(trees):
    from math import hypot
    x=(min(p[0] for p in trees)+max(p[0] for p in trees))/2;y=(min(p[1] for p in trees)+max(p[1] for p in trees))/2
    return [x,y,max(hypot(p[0]-x,p[1]-y) for p in trees)]
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1920: entry(
        "build_array_from_permutation", [("nums", "list[int]")], "list[int]",
        ["arrays", "simulation", "indexing"],
        ["nums is a permutation of 0 through len(nums)-1 with length at most 1000.",
         "For every index i, output nums[nums[i]].", "Do not reorder the input before following its indices."],
        [([[0,2,1,5,3,4]], "Following each value as a second index gives [0,1,2,4,5,3]."),
         ([[5,0,1,2,3,4]], "Each value points to the next value in the permutation cycle, giving [4,5,0,1,2,3].")],
        [[nums] for nums in [[0],[0,1],[1,0],[0,2,1,5,3,4],[5,0,1,2,3,4],[2,0,1],
                             [1,2,3,0],[3,2,1,0],[4,3,2,1,0],[1,0,3,2],[2,1,0,4,3],
                             [6,0,5,1,4,2,3],[0,3,1,2],[2,3,0,1]]],
        PERMUTATION,
        [PERMUTATION.replace("nums[value]", "value"), PERMUTATION.replace("for value in nums", "for value in sorted(nums)")],
        ["Copies the permutation values instead of using each as another index.",
         "Sorts the permutation before indexing and loses the original position mapping."],
        permutation_oracle, random_permutation,
        lesson("Each permutation value is guaranteed to be a valid index.",
               "For each value in original order, use it to index nums once more.",
               "Collect those second-lookups in the answer.",
               "The comprehension directly applies the required equation independently at every index, so it preserves order and produces every specified value."),
        "O(n)", "O(n)", 3),
    1921: entry(
        "eliminate_maximum_monsters", [("dist", "list[int]"), ("speed", "list[int]")], "int",
        ["arrays", "sorting", "greedy"],
        ["The equal-length arrays contain 1 through 100000 positive values.",
         "One monster may be eliminated at minute 0 and one more at each later integer minute.",
         "The game ends before firing when any living monster reaches the city."],
        [([[1,3,4],[1,1,1]], "The monsters reach at minutes one, three, and four, so all three can be eliminated first."),
         ([[1,1,2,3],[1,1,1,1]], "Two monsters arrive at minute one; after the minute-zero shot, another reaches the city, so only one is eliminated.")],
        [[dist,speed] for dist,speed in [
            ([1],[1]),([1,3,4],[1,1,1]),([1,1,2,3],[1,1,1,1]),([3,2,4],[5,3,2]),
            ([10,10],[1,2]),([2,2],[1,1]),([2,3],[2,1]),([5,4,3],[1,1,1]),
            ([6,8,10],[2,2,2]),([1,10,20],[1,10,10]),([9,3,6,12],[3,1,2,4]),
            ([100,1],[1,1]),([7,7,7],[2,3,4]),([4,9,2,8],[2,3,1,4]),
        ]],
        MONSTERS,
        [MONSTERS.replace("(distance - 1) // velocity", "distance // velocity"), MONSTERS_DISTANCE],
        ["Allows firing at the exact minute a monster reaches the city, which is already too late.",
         "Sorts by starting distance instead of arrival time, ignoring different speeds."],
        monsters_oracle, random_monsters,
        lesson("Convert each monster to the last integer minute when it can safely be shot: floor((distance-1)/speed).",
               "Sort these deadlines and schedule one shot per minute in earliest-deadline order.",
               "Stop when the next deadline is earlier than its assigned minute.",
               "Earliest-deadline scheduling is optimal by exchange: swapping an earlier deadline ahead never makes either shot less feasible."),
        "O(n*log(n))", "O(n)", 6),
    1922: entry(
        "count_good_digit_strings", [("n", "int")], "int",
        ["math", "recursion", "modular-arithmetic"],
        ["1 <= n <= 1000000000000000.",
         "Even indices allow digits 0,2,4,6,8; odd indices allow 2,3,5,7.",
         "Return the number of length-n strings modulo 1000000007."],
        [([1], "The only position is even-indexed and has five choices."),
         ([4], "Two even positions and two odd positions give 5^2 * 4^2 = 400 strings.")],
        [[n] for n in [1,2,3,4,5,10,11,20,50,100,999,1000,10**6,10**15]],
        GOOD_NUMBERS,
        [GOOD_NUMBERS.replace("power(5, even_positions) * power(4, odd_positions)", "power(5, n)"),
         GOOD_NUMBERS.replace("power(5, even_positions) * power(4, odd_positions)", "power(5, odd_positions) * power(4, even_positions)")],
        ["Gives every position five choices and ignores the four-choice restriction at odd indices.",
         "Swaps the five-choice and four-choice position counts, which fails for odd lengths."],
        good_numbers_oracle, random_good_numbers,
        lesson("There are ceil(n/2) even indices with five choices and floor(n/2) odd indices with four choices.",
               "Multiply 5^ceil(n/2) by 4^floor(n/2) modulo the prime.",
               "Compute each power recursively by squaring the half exponent, multiplying once more when the exponent is odd.",
               "Position choices are independent, and exponentiation by squaring preserves the power invariant while reducing the exponent logarithmically."),
        "O(log(n))", "O(log(n))", 6),
    1923: entry(
        "longest_common_city_subpath", [("n", "int"), ("paths", "list[list[int]]")], "int",
        ["arrays", "binary-search", "rolling-hash", "strings"],
        ["There are at least two paths; total path length and n are at most 100000.",
         "Cities range from 0 through n-1 and consecutive cities in a path differ.",
         "A common subpath must be contiguous and appear in the same order in every path."],
        [([5,[[0,1,2,3,4],[2,3,4],[4,0,1,2,3]]], "The paths [2,3] and [3,4] occur in all routes, but no common length-three route does."),
         ([3,[[0],[1],[2]]], "No city occurs in every path, so the maximum common length is zero.")],
        [[n,paths] for n,paths in [
            (2,[[0],[0]]),(3,[[0],[1],[2]]),(5,[[0,1,2,3,4],[2,3,4],[4,0,1,2,3]]),
            (4,[[0,1],[0,1],[0,1]]),(4,[[0,1,2],[1,2,3]]),(3,[[0,1,0],[1,0,1]]),
            (6,[[1,2,3,4],[0,1,2,3,5],[1,2,3]]),(5,[[0,2,4],[0,4,2]]),
            (2,[[0,1,0,1],[1,0,1,0]]),(7,[[1,3,5],[1,3,5,6],[0,1,3,5]]),
            (5,[[0,1,2],[2,1,0],[1,2]]),(4,[[3,2,1,0],[3,2],[2,1]]),
            (8,[[1,2,1,2,3],[0,1,2,1,2,4],[1,2,1,2]]),(3,[[0,1],[1,2],[2,0]]),
        ]],
        COMMON_PATH,
        [COMMON_PATH.replace("common &= hashes(path, length)", "common |= hashes(path, length)"), COMMON_CITIES],
        ["Unions path hashes and therefore accepts a subpath seen in any route instead of every route.",
         "Counts shared city values without enforcing contiguous order or repeated-position structure."],
        common_subpath_oracle, random_paths,
        lesson("If a common subpath of length L exists, every shorter prefix length is also achievable.",
               "Double-hash every length-L window in each path and intersect the per-path hash sets.",
               "Binary-search the greatest length with a nonempty intersection, starting from the shortest path.",
               "Rolling hashes represent contiguous ordered windows, set intersection enforces presence in every path, and monotonicity validates the binary search."),
        "O(total path length*log(min path length))", "O(total path length)", 8),
    1924: entry(
        "minimum_enclosing_fence_circle", [("trees", "list[list[int]]")], "list[float]",
        ["geometry", "randomized-algorithms", "arrays", "math"],
        ["There are 1 through 3000 points with coordinates between 0 and 3000.",
         "Return [center_x, center_y, radius] for the minimum-radius circle containing every point.",
         "Answers within floating-point tolerance are accepted."],
        [([[[1,1],[2,2],[2,0],[2,4],[3,3],[4,2]]], "The minimum circle is centered at (2,2) with radius two."),
         ([[[1,1]]], "One point is enclosed by a radius-zero circle centered on that point.")],
        [[points] for points in [
            [[1,1]],[[0,0],[2,0]],[[0,0],[0,2],[2,0]],[[1,1],[2,2],[2,0],[2,4],[3,3],[4,2]],
            [[0,0],[4,0],[2,1]],[[0,0],[1,0],[2,0]],[[1,1],[1,1]],
            [[0,0],[0,4],[4,0],[4,4]],[[1,2],[3,5],[6,1]],[[2,2],[5,2],[3,6]],
            [[0,1],[1,0],[-0+2,1],[1,2]],[[10,10],[20,10],[15,18]],
            [[3,1],[3,7],[8,4],[1,4]],[[0,0],[3,0],[0,3],[1,1]],
        ]],
        FENCE,
        [FENCE_CENTROID, FENCE_BOX],
        ["Centers the circle at the average point, which need not minimize the farthest distance.",
         "Centers at the bounding-box midpoint, which can be suboptimal for asymmetric point sets."],
        fence_oracle, random_fence,
        lesson("A minimum enclosing circle is determined by at most three boundary points.",
               "Process points in a fixed random order; when a point lies outside, rebuild a circle constrained through that point and earlier outside points.",
               "Use a diameter circle for two boundary points and a circumcircle—or the farthest-pair diameter when collinear—for three.",
               "The nested invariant encloses every processed point, while boundary reconstruction examines the only circles that can become the new minimum."),
        "O(number of points) expected", "O(number of points)", 8),
}

BATCH[1924]["comparator"] = "float_list"
