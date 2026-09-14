"""First reviewed group of workbook batch 111."""

from itertools import permutations

from .import_batch_055 import entry


def product_difference_oracle(arguments):
    nums = arguments[0]
    return max(nums[a] * nums[b] - nums[c] * nums[d]
               for a, b, c, d in permutations(range(len(nums)), 4))


def layer_coordinates(rows, columns, layer):
    coordinates = []
    coordinates.extend((layer, column) for column in range(layer, columns - layer - 1))
    coordinates.extend((row, columns - layer - 1) for row in range(layer, rows - layer - 1))
    coordinates.extend((rows - layer - 1, column) for column in range(columns - layer - 1, layer, -1))
    coordinates.extend((row, layer) for row in range(rows - layer - 1, layer, -1))
    return coordinates


def rotation_oracle(arguments):
    grid, k = arguments
    answer = [row[:] for row in grid]
    for layer in range(min(len(grid), len(grid[0])) // 2):
        coordinates = layer_coordinates(len(grid), len(grid[0]), layer)
        for _ in range(k % len(coordinates)):
            first = answer[coordinates[0][0]][coordinates[0][1]]
            for index in range(len(coordinates) - 1):
                row, column = coordinates[index]
                next_row, next_column = coordinates[index + 1]
                answer[row][column] = answer[next_row][next_column]
            last_row, last_column = coordinates[-1]
            answer[last_row][last_column] = first
    return answer


def wonderful_oracle(arguments):
    word = arguments[0]
    answer = 0
    for left in range(len(word)):
        counts = {}
        for right in range(left, len(word)):
            char = word[right]
            counts[char] = counts.get(char, 0) + 1
            answer += sum(amount % 2 for amount in counts.values()) <= 1
    return answer


def rooms_oracle(arguments):
    parents = arguments[0]
    answer = 0
    for order in permutations(range(1, len(parents))):
        built = {0}
        valid = True
        for room in order:
            if parents[room] not in built:
                valid = False
                break
            built.add(room)
        answer += valid
    return answer % 1_000_000_007


def subarray_oracle(arguments):
    nums, k = arguments
    sums = []
    for left in range(len(nums)):
        total = 0
        for right in range(left, len(nums)):
            total += nums[right]
            sums.append(total)
    return sorted(sums)[k - 1]


def random_product_difference(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(4, 8))]]


def random_rotation(rng):
    rows, columns = rng.choice((2, 4, 6)), rng.choice((2, 4, 6))
    return [[[rng.randint(1, 40) for _ in range(columns)] for _ in range(rows)], rng.randint(1, 100)]


def random_wonderful(rng):
    return ["".join(rng.choice("abcdefghij") for _ in range(rng.randint(1, 30)))]


def random_rooms(rng):
    n = rng.randint(2, 8)
    return [[-1] + [rng.randrange(room) for room in range(1, n)]]


def random_subarray(rng):
    nums = [rng.randint(1, 20) for _ in range(rng.randint(1, 15))]
    return [nums, rng.randint(1, len(nums) * (len(nums) + 1) // 2)]


PRODUCT_DIFFERENCE = '''\
def maximum_product_pair_difference(nums):
    ordered = sorted(nums)
    return ordered[-1] * ordered[-2] - ordered[0] * ordered[1]
'''

GRID_ROTATION = '''\
def rotate_grid_layers(grid, k):
    rows, columns = len(grid), len(grid[0])
    answer = [row[:] for row in grid]
    for layer in range(min(rows, columns) // 2):
        coordinates = []
        coordinates += [(layer, column) for column in range(layer, columns - layer - 1)]
        coordinates += [(row, columns - layer - 1) for row in range(layer, rows - layer - 1)]
        coordinates += [(rows - layer - 1, column) for column in range(columns - layer - 1, layer, -1)]
        coordinates += [(row, layer) for row in range(rows - layer - 1, layer, -1)]
        values = [grid[row][column] for row, column in coordinates]
        shift = k % len(values)
        values = values[shift:] + values[:shift]
        for (row, column), value in zip(coordinates, values):
            answer[row][column] = value
    return answer
'''

WONDERFUL = '''\
def count_wonderful_substrings(word):
    frequencies = {0: 1}
    mask = 0
    answer = 0
    for char in word:
        mask ^= 1 << (ord(char) - ord("a"))
        answer += frequencies.get(mask, 0)
        for bit in range(10):
            answer += frequencies.get(mask ^ (1 << bit), 0)
        frequencies[mask] = frequencies.get(mask, 0) + 1
    return answer
'''

ROOMS = '''\
def count_valid_room_build_orders(prev_room):
    modulus = 1_000_000_007
    children = [[] for _ in prev_room]
    for room in range(1, len(prev_room)):
        children[prev_room[room]].append(room)
    order = [0]
    for room in order:
        order.extend(children[room])
    subtree_size = [1] * len(prev_room)
    for room in reversed(order[1:]):
        subtree_size[prev_room[room]] += subtree_size[room]
    factorial = 1
    for value in range(2, len(prev_room) + 1):
        factorial = factorial * value % modulus
    denominator = 1
    for size in subtree_size:
        denominator = denominator * size % modulus
    return factorial * pow(denominator, modulus - 2, modulus) % modulus
'''

ROOMS_IGNORE_SUBTREES = '''\
def count_valid_room_build_orders(prev_room):
    answer=1
    for value in range(2,len(prev_room)):answer=answer*value%(10**9+7)
    return answer
'''

SUBARRAY = '''\
def kth_smallest_positive_subarray_sum(nums, k):
    def at_least_k(limit):
        left = 0
        total = 0
        count = 0
        for right, value in enumerate(nums):
            total += value
            while total > limit:
                total -= nums[left]
                left += 1
            count += right - left + 1
        return count >= k
    left, right = min(nums), sum(nums)
    while left < right:
        middle = (left + right) // 2
        if at_least_k(middle):
            right = middle
        else:
            left = middle + 1
    return left
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1913: entry(
        "maximum_product_pair_difference", [("nums", "list[int]")], "int",
        ["arrays", "sorting", "greedy"],
        ["4 <= len(nums) <= 10000 and all values are positive.",
         "Choose four distinct indices for two products.",
         "Maximize first_product minus second_product."],
        [([[5,6,2,7,4]], "The two largest values produce 42 and the two smallest produce 8, giving 34."),
         ([[4,2,5,9,7,4,8]], "Products 9*8 and 2*4 give the maximum difference 64.")],
        [[nums] for nums in [
            [1,2,3,4],[5,6,2,7,4],[4,2,5,9,7,4,8],[1,1,1,1],[1,1,9,9],
            [2,3,4,5],[10,2,8,3,7],[5,5,2,2,9],[100,1,50,2],[7,6,5,4,3],
            [9,9,8,1,1],[3,10,3,10,2,2],[4,8,1,6,2,9],[20,15,10,5],
        ]],
        PRODUCT_DIFFERENCE,
        [PRODUCT_DIFFERENCE.replace("ordered[0] * ordered[1]", "ordered[0] * ordered[-2]"),
         PRODUCT_DIFFERENCE.replace("ordered[-1] * ordered[-2]", "ordered[-1] * ordered[0]")],
        ["Reuses a large value in the product being subtracted instead of choosing the two smallest remaining values.",
         "Uses the largest and smallest values for the positive product rather than the two largest."],
        product_difference_oracle, random_product_difference,
        lesson("Positive products grow with either factor.",
               "Sort the values; maximize the added product with the two largest and minimize the subtracted product with the two smallest.",
               "Subtract those two extreme products.",
               "The four selected indices are distinct because the array has at least four elements, and monotonicity of positive multiplication proves both extreme choices."),
        "O(n*log(n))", "O(n)", 3),
    1914: entry(
        "rotate_grid_layers", [("grid", "list[list[int]]"), ("k", "int")], "list[list[int]]",
        ["matrices", "simulation", "arrays"],
        ["The grid has even dimensions from 2 through 50 and positive values.", "1 <= k <= 1000000000.",
         "Rotate every concentric layer counter-clockwise by k positions."],
        [([[[40,10],[30,20]],1], "The four values each move one counter-clockwise edge position, producing [[10,20],[40,30]]."),
         ([[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]],2], "Both the outer ring and inner 2-by-2 ring rotate counter-clockwise twice.")],
        [[grid,k] for grid,k in [
            ([[40,10],[30,20]],1),([[1,2],[3,4]],2),([[1,2],[3,4]],5),
            ([[1,2,3,4],[5,6,7,8]],1),([[1,2,3,4],[5,6,7,8]],3),
            ([[1,2],[3,4],[5,6],[7,8]],2),
            ([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]],1),
            ([[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]],2),
            ([[5,5],[5,5]],100),([[1,2,3,4,5,6],[7,8,9,10,11,12]],7),
            ([[1,2],[3,4],[5,6],[7,8],[9,10],[11,12]],9),
            ([[2,4,6,8],[1,3,5,7],[9,11,13,15],[10,12,14,16]],5),
            ([[1,1,2,2],[3,3,4,4]],4),([[9,8,7,6],[5,4,3,2]],1000000000),
        ]],
        GRID_ROTATION,
        [GRID_ROTATION.replace("values[shift:] + values[:shift]", "values[-shift:] + values[:-shift]"),
         GRID_ROTATION.replace("for layer in range(min(rows, columns) // 2):", "for layer in range(1):")],
        ["Rotates each ring clockwise rather than counter-clockwise.",
         "Rotates only the outer ring and leaves inner layers unchanged."],
        rotation_oracle, random_rotation,
        lesson("Each concentric layer is an independent cycle of perimeter coordinates.",
               "List a layer's coordinates in clockwise order and read its values in that same order.",
               "A counter-clockwise rotation assigns the list shifted left by k modulo its perimeter length.",
               "Every cell belongs to exactly one layer cycle, and cyclic indexing maps each value to precisely its position after k moves."),
        "O(rows*columns)", "O(rows*columns)", 6),
    1915: entry(
        "count_wonderful_substrings", [("word", "str")], "int",
        ["strings", "bit-manipulation", "prefix-sums", "hash-maps"],
        ["word has 1 through 100000 letters from a through j.",
         "A substring is wonderful when at most one character count is odd.",
         "Count occurrences by position, including identical substring text at different positions."],
        [(["aba"], "The wonderful substrings are a, b, a, and aba, for four total."),
         (["aabb"], "Nine of the ten substrings qualify; only the middle substring ab has two odd-frequency characters." )],
        [[word] for word in [
            "a","aa","ab","aba","aabb","abc","aaaa","abcdefghij","jjj","abacaba",
            "aabbcc","abcabc","ijij","abcdefghija","baced", "ddddccbb",
        ]],
        WONDERFUL,
        [WONDERFUL.replace("for bit in range(10):", "for bit in range(0):"),
         WONDERFUL.replace("for bit in range(10):", "for bit in range(10):\n            for other in range(bit + 1, 10):\n                answer += frequencies.get(mask ^ (1 << bit) ^ (1 << other), 0)")],
        ["Counts only substrings with zero odd-frequency characters and omits the allowed single odd count.",
         "Also counts substrings with two odd-frequency characters, exceeding the definition's limit."],
        wonderful_oracle, random_wonderful,
        lesson("A ten-bit prefix mask records which character counts are currently odd.",
               "A substring has zero odd counts when its endpoint masks match, or one odd count when the masks differ by one bit.",
               "For each prefix, add frequencies of the same mask and all ten one-bit neighbors, then record the current mask.",
               "XOR of two prefix parity masks is exactly the substring parity mask, so the counted cases are necessary and sufficient."),
        "O(10*len(word))", "O(1024)", 6),
    1916: entry(
        "count_valid_room_build_orders", [("prev_room", "list[int]")], "int",
        ["trees", "combinatorics", "tree-dp", "depth-first-search"],
        ["2 <= len(prev_room) <= 100000, prev_room[0] is -1, and each later parent index is smaller than its room index.",
         "A room may be built only after its parent, starting with room zero already available.",
         "Count distinct valid construction orders modulo 1000000007."],
        [([[-1,0,1]], "The chain forces order 0,1,2, so exactly one construction order exists."),
         ([[-1,0,0,1,2]], "The two child subtrees can be interleaved in six parent-respecting orders.")],
        [[parents] for parents in [
            [-1,0],[-1,0,1],[-1,0,0],[-1,0,0,1,2],[-1,0,0,0],
            [-1,0,1,1],[-1,0,0,1,1],[-1,0,1,2,3],[-1,0,0,2,2],
            [-1,0,0,1,2,3],[-1,0,1,1,2,2],[-1,0,0,0,1,2,3],
            [-1,0,1,0,3,2],[-1,0,0,1,1,2,2,3],
        ]],
        ROOMS,
        [ROOMS.replace("range(2, len(prev_room) + 1)", "range(2, len(prev_room))"), ROOMS_IGNORE_SUBTREES],
        ["Uses (n-1)! in the numerator while still dividing by the root's size n.",
         "Assumes every ordering after room zero is valid and ignores all non-root dependencies."],
        rooms_oracle, random_rooms,
        lesson("Valid build orders are linear extensions of the rooted parent tree.",
               "Compute every subtree size with an iterative postorder traversal.",
               "The number of orders is n! divided by the product of all subtree sizes; use a modular inverse for division.",
               "At each node, multinomially interleaving independently valid child-subtree orders yields the hook-length formula, and induction over the tree proves it."),
        "O(n + log(modulus))", "O(n)", 8),
    1918: entry(
        "kth_smallest_positive_subarray_sum", [("nums", "list[int]"), ("k", "int")], "int",
        ["arrays", "binary-search", "sliding-windows"],
        ["1 <= len(nums) <= 20000 and every value is positive.",
         "1 <= k <= n*(n+1)/2.",
         "Sort the sums of all nonempty contiguous subarrays conceptually and return the one-based kth value."],
        [([[2,1,3],4], "The sorted sums are 1,2,3,3,4,6, so the fourth is three."),
         ([[3,3,5,5],7], "Counting sums by threshold shows that the seventh smallest sum is eight.")],
        [[nums,k] for nums,k in [
            ([1],1),([2,1,3],4),([3,3,5,5],7),([1,1],1),([1,1],3),
            ([1,2,3],6),([5,1,2],2),([10,10,10],4),([1,2,1,2],5),
            ([4,3,2,1],7),([2,2,2,2],8),([9,1,8,2],6),([1,3,6,10],9),
            ([5,5,1,1,5],10),
        ]],
        SUBARRAY,
        [SUBARRAY.replace("while total > limit:", "while total >= limit:"),
         SUBARRAY.replace("return count >= k", "return count >= k + 1")],
        ["Counts only subarray sums strictly below the threshold instead of sums at most the threshold.",
         "Treats k as zero-based and searches for the next order statistic."],
        subarray_oracle, random_subarray,
        lesson("Because values are positive, a sliding window counts subarrays with sum at most a threshold in linear time.",
               "For each right endpoint, shrink the left edge until the sum fits, then add the number of valid starts.",
               "Binary-search the smallest threshold whose count reaches k.",
               "The count is monotonic in the threshold, and the first threshold with at least k sums is exactly the kth sorted sum."),
        "O(n*log(sum(nums)))", "O(1)", 6),
}
