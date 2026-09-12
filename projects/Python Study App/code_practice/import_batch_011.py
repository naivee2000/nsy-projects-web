"""Original in-place contracts: inspect the actual argument, not a returned copy."""
from collections import Counter
from itertools import permutations

from .import_batch_003 import entry


def prefix(values):
    return {"return": len(values), "prefix": values}


def unique_oracle(args):
    return prefix(sorted(set(args[0])))


def remove_oracle(args):
    return prefix([value for value in args[0] if value != args[1]])


def twice_oracle(args):
    counts = Counter(args[0])
    return prefix([value for value in sorted(counts) for _ in range(min(2, counts[value]))])


def next_oracle(args):
    ordered = sorted(set(permutations(args[0])))
    index = ordered.index(tuple(args[0]))
    return list(ordered[(index + 1) % len(ordered)])


def rotate_oracle(args):
    matrix = args[0]
    size = len(matrix)
    return [[matrix[size - 1 - column][row] for column in range(size)] for row in range(size)]


def zero_oracle(args):
    matrix = args[0]
    zeros = [(r, c) for r, row in enumerate(matrix) for c, value in enumerate(row) if value == 0]
    return [[0 if any(r == zr or c == zc for zr, zc in zeros) else value
             for c, value in enumerate(row)] for r, row in enumerate(matrix)]


def colors_oracle(args):
    return sorted(args[0])


def merge_oracle(args):
    first, m, second, n = args
    return sorted(first[:m] + second[:n])


def random_sorted(rng):
    return [sorted(rng.randint(-100, 100) for _ in range(rng.randint(1, 60)))]


def random_remove(rng):
    return [[rng.randrange(51) for _ in range(rng.randrange(101))], rng.randrange(101)]


def random_next(rng):
    return [[rng.randrange(6) for _ in range(rng.randint(1, 7))]]


def random_square(rng):
    size = rng.randint(1, 8)
    return [[[rng.randint(-1000, 1000) for _ in range(size)] for _ in range(size)]]


def random_matrix(rng):
    rows, columns = rng.randint(1, 8), rng.randint(1, 8)
    return [[[rng.randint(-3, 3) for _ in range(columns)] for _ in range(rows)]]


def random_colors(rng):
    return [[rng.randrange(3) for _ in range(rng.randint(1, 100))]]


def random_merge(rng):
    total = rng.randint(1, 100)
    m = rng.randint(0, total)
    n = total - m
    return [sorted(rng.randint(-100, 100) for _ in range(m)) + [0] * n, m,
            sorted(rng.randint(-100, 100) for _ in range(n)), n]


UNIQUE = '''\
def remove_duplicates(nums):
    write = 0
    for value in nums:
        if write == 0 or value != nums[write - 1]:
            nums[write] = value
            write += 1
    return write
'''
REMOVE = '''\
def remove_element(nums, val):
    write = 0
    for value in nums:
        if value != val:
            nums[write] = value
            write += 1
    return write
'''
TWICE = '''\
def remove_duplicates_twice(nums):
    write = 0
    for value in nums:
        if write < 2 or value != nums[write - 2]:
            nums[write] = value
            write += 1
    return write
'''
NEXT = '''\
def next_permutation(nums):
    pivot = len(nums) - 2
    while pivot >= 0 and nums[pivot] >= nums[pivot + 1]:
        pivot -= 1
    if pivot >= 0:
        successor = len(nums) - 1
        while nums[successor] <= nums[pivot]:
            successor -= 1
        nums[pivot], nums[successor] = nums[successor], nums[pivot]
    left, right = pivot + 1, len(nums) - 1
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left += 1
        right -= 1
'''
ROTATE = '''\
def rotate_image(matrix):
    for row in range(len(matrix)):
        for column in range(row + 1, len(matrix)):
            matrix[row][column], matrix[column][row] = matrix[column][row], matrix[row][column]
    for row in matrix:
        row.reverse()
'''
ZERO = '''\
def set_matrix_zeroes(matrix):
    first_row = any(value == 0 for value in matrix[0])
    first_column = any(row[0] == 0 for row in matrix)
    for row in range(1, len(matrix)):
        for column in range(1, len(matrix[0])):
            if matrix[row][column] == 0:
                matrix[row][0] = matrix[0][column] = 0
    for row in range(1, len(matrix)):
        for column in range(1, len(matrix[0])):
            if matrix[row][0] == 0 or matrix[0][column] == 0:
                matrix[row][column] = 0
    if first_row:
        for column in range(len(matrix[0])):
            matrix[0][column] = 0
    if first_column:
        for row in matrix:
            row[0] = 0
'''
COLORS = '''\
def sort_colors(nums):
    low = current = 0
    high = len(nums) - 1
    while current <= high:
        if nums[current] == 0:
            nums[low], nums[current] = nums[current], nums[low]
            low += 1
            current += 1
        elif nums[current] == 2:
            nums[current], nums[high] = nums[high], nums[current]
            high -= 1
        else:
            current += 1
'''
MERGE = '''\
def merge_sorted_array(nums1, m, nums2, n):
    left, right, write = m - 1, n - 1, m + n - 1
    while right >= 0:
        if left >= 0 and nums1[left] > nums2[right]:
            nums1[write] = nums1[left]
            left -= 1
        else:
            nums1[write] = nums2[right]
            right -= 1
        write -= 1
'''

SORTED = [[0], [1], [-1], [1, 1], [1, 2], [1, 1, 1], [-2, -2, -1],
          [-3, -2, -1], [0, 0, 0, 1], [-100, -100, 100], [1, 2, 2, 3], [2, 2, 2, 2]]
MATRICES = [[[0]], [[1]], [[-1]], [[1, 2], [3, 4]], [[0, 1], [2, 3]],
            [[1, 0], [2, 3]], [[1, 2], [0, 3]], [[1, 2], [3, 0]],
            [[0, 0], [0, 0]], [[1, 1], [1, 1]], [[-1, 2], [3, -4]],
            [[1, 2, 3], [4, 5, 6], [7, 8, 0]]]

BATCH = {
    26: entry("remove_duplicates", [("nums", "list[int]")], "int", ["arrays", "two-pointers"],
        ["1–30000 sorted integers, each between -100 and 100.", "Modify nums in place so each distinct value appears once in sorted order at the front; return that prefix length k.",
         "The judge checks both return and nums[:k]. Entries beyond k are ignored; returning a new list or only counting values is insufficient."],
        [([[1, 1, 2]], "Return 2 and place [1,2] in nums[:2]. The third slot is ignored."),
         ([[0, 0, 1, 1, 1, 2, 2, 3, 3, 4]], "Return 5 with prefix [0,1,2,3,4]; nothing is required of the last five slots.")],
        [[values] for values in SORTED], UNIQUE,
        ["def remove_duplicates(nums):\n    return len(set(nums))\n", UNIQUE.replace("return write", "return write - 1")],
        ["Returns the correct count but does not compact the caller's list.", "Returns the last written index instead of the prefix length."],
        unique_oracle, random_sorted,
        ["Sorted input puts equal values next to each other.", "Keep a write position for the end of the distinct prefix.",
         "For each value, write it if the prefix is empty or its last value differs; increment write only after keeping a value.",
         "Return the number written. The untouched tail does not matter."],
        "Scan left-to-right and maintain a sorted distinct prefix before the write index. A value differs from the last accepted value exactly when it begins a new run. Write only those run starts. The write index never overtakes the read position, so input that remains to be processed is safe. The oracle builds a sorted set and reports both its length and contents; the judge independently observes the original input list.", "O(n)", "O(1)", difficulty=3,
        stress=[([[1] * 30000], prefix([1]))]),
    27: entry("remove_element", [("nums", "list[int]"), ("val", "int")], "int", ["arrays", "two-pointers"],
        ["0–100 entries with values 0–50; val is between 0 and 100.", "Modify nums so its first k entries contain every original value unequal to val, and return k. Prefix order is unrestricted; multiplicity must be preserved.",
         "The judge shows {return, prefix}. It ignores the list tail and permits resizing, but returning another list without updating nums does not satisfy the contract."],
        [([[3, 2, 2, 3], 3], "Return 2 with prefix [2,2]. Both copies of 2 must remain."),
         ([[0, 1, 2, 2, 3, 0, 4, 2], 2], "Return 5. A valid prefix is [0,1,3,0,4]; any permutation of those five values is accepted.")],
        [[[], 0], [[1], 1], [[1], 2], [[0, 0], 0], [[0, 1], 0], [[0, 1], 1], [[2, 2, 3], 2],
         [[3, 2, 3], 3], [[1, 2, 3], 4], [[0, 50, 0], 0], [[50, 50], 100], [[1, 1, 2, 2], 1]], REMOVE,
        [REMOVE.replace("if value != val:", "if value == val:"), "def remove_element(nums, val):\n    return sum(value != val for value in nums)\n"],
        ["Keeps the removed value instead of retaining other values.", "Computes k without moving the surviving values into the required prefix."],
        remove_oracle, random_remove,
        ["Every original occurrence unequal to val must survive, including duplicates.", "Compact survivors toward the front with a write index.",
         "For each value different from val, assign nums[write]=value and increment write; return write.",
         "Do not remove from the list while blindly advancing a read index, which can skip shifted values."],
        "Copy each surviving value to the next write position. Since writes never move ahead of the current read position, unread values are preserved. This stable reference also satisfies the more permissive any-order contract. The oracle filters a separate list, while the judge compares the returned count and the modified prefix as a multiset, retaining duplicate counts.", "O(n)", "O(1)", difficulty=3),
    80: entry("remove_duplicates_twice", [("nums", "list[int]")], "int", ["arrays", "two-pointers"],
        ["1–30000 sorted integers, each between -10000 and 10000.", "Modify nums in place so each value occurs at most twice in a sorted prefix. Return its length k; the rest of nums is ignored. Use constant extra space."],
        [([[1, 1, 1, 2, 2, 3]], "Return 5 with prefix [1,1,2,2,3], dropping only the third 1."),
         ([[0, 0, 1, 1, 1, 1, 2, 3, 3]], "Return 7 with prefix [0,0,1,1,2,3,3]. Values occurring once are still retained.")],
        [[values] for values in SORTED], TWICE,
        [TWICE.replace("write < 2", "write < 1").replace("nums[write - 2]", "nums[write - 1]"),
         TWICE.replace("return write", "return len(nums)")],
        ["Keeps only one copy of each distinct value.", "Returns the original list length rather than the compacted length."],
        twice_oracle, random_sorted,
        ["A third copy can be detected by looking two positions back in the accepted prefix.", "Keep the first two values automatically, then compare each candidate with nums[write-2].",
         "If write<2 or the candidate differs from nums[write-2], write it at nums[write] and advance write.",
         "Compare against the accepted prefix, not a fixed two-position lookback in the original input."],
        "Maintain a prefix in which every value occurs at most twice. Once two entries have been written, the value two positions behind the write index identifies whether two copies of the candidate are already retained. Sorted order makes this one comparison sufficient. The oracle uses independent occurrence counts capped at two and returns the expected count/prefix pair.", "O(n)", "O(1)", difficulty=5,
        stress=[([[0] * 30000], prefix([0, 0]))]),
    31: entry("next_permutation", [("nums", "list[int]")], "None", ["arrays", "two-pointers"],
        ["1–100 integers with values 0–100, including possible duplicates.", "Rearrange nums into its immediate next lexicographic permutation, wrapping the largest arrangement to the smallest. Modify the input with constant extra memory; no returned list is used."],
        [([[1, 2, 3]], "Change nums to [1,3,2], the smallest arrangement larger than [1,2,3]."),
         ([[3, 2, 1]], "No larger arrangement exists, so wrap to [1,2,3].")],
        [[[1]], [[1, 1]], [[1, 2]], [[2, 1]], [[1, 1, 5]], [[1, 5, 1]], [[5, 1, 1]],
         [[1, 3, 2]], [[2, 1, 3]], [[2, 3, 1]], [[1, 2, 2, 1]], [[0, 2, 1, 2]]], NEXT,
        [NEXT.replace("while left < right:", "while False:"), "def next_permutation(nums):\n    nums.sort()\n"],
        ["Swaps a pivot but leaves the suffix descending instead of minimizing it.", "Always returns to ascending order rather than finding the immediate successor."],
        next_oracle, random_next,
        ["Change the rightmost position that can be increased, keeping the earlier prefix unchanged.", "Find the pivot just before the longest nonincreasing suffix, swap with its smallest larger suffix value, and reverse the suffix.",
         "Scan rightward-to-left for the pivot; scan from the end for a value strictly larger; swap and reverse after the pivot. Without a pivot, reverse all values.",
         "Use strict increase when selecting a successor so equal values do not create the same permutation."],
        "A nonincreasing suffix is already its largest arrangement. The preceding pivot is therefore the rightmost position that can increase. The rightmost suffix value strictly greater than it is the smallest valid replacement. After swapping, reverse the still-nonincreasing suffix into its minimum order. No pivot means the entire input is maximal and must wrap. The independent oracle enumerates and sorts unique permutations on small inputs.", "O(n)", "O(1)", difficulty=5,
        stress=[([list(range(99, -1, -1))], list(range(100)))]),
    48: entry("rotate_image", [("matrix", "list[list[int]]")], "None", ["matrices", "arrays"],
        ["A square matrix with side length 1–20 and values between -1000 and 1000.", "Rotate 90 degrees clockwise by modifying matrix directly. Do not allocate a second matrix. The judge reads matrix after the call, not a returned copy."],
        [([[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "The first column [1,4,7] becomes the top row in reverse order [7,4,1]; the other columns transform the same way."),
         ([[[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]], "The new top row is [15,13,2,5], and the new bottom row is [16,7,10,11].")],
        [[matrix] for matrix in MATRICES], ROTATE,
        [ROTATE.replace("row.reverse()", "pass"), "def rotate_image(matrix):\n    return [list(row) for row in zip(*matrix[::-1])]\n"],
        ["Transposes but omits the horizontal reflection needed for clockwise rotation.", "Returns a rotated copy while leaving the input image unchanged."],
        rotate_oracle, random_square,
        ["A clockwise rotation can be decomposed into a transpose followed by reversing each row.", "Swap across the main diagonal once per pair, then reverse each row in place.",
         "For row r, swap positions (r,c) and (c,r) only for c>r. Then reverse the contents of every row.",
         "Swapping every diagonal pair twice cancels the transpose; allocating and returning a copy does not mutate the input."],
        "Transpose by exchanging the upper-triangle cells with their lower-triangle partners, then reverse each row. These two reflections map each original (r,c) to (c,n-1-r), a clockwise quarter-turn. Both transformations modify the original matrix using constant auxiliary storage. The oracle constructs a separate output directly from the coordinate formula.", "O(n²)", "O(1)", difficulty=5),
    73: entry("set_matrix_zeroes", [("matrix", "list[list[int]]")], "None", ["matrices", "arrays"],
        ["1–200 rows and columns; values are signed 32-bit integers.", "Every zero in the original matrix clears its entire row and column. Newly written zeros must not trigger additional clearing. Modify matrix in place; target constant extra space."],
        [([[[1, 1, 1], [1, 0, 1], [1, 1, 1]]], "Only the center's original row and column clear, leaving the four corners equal to 1."),
         ([[[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]], "The first row clears along with columns 0 and 3. The other rows retain their middle entries.")],
        [[matrix] for matrix in MATRICES], ZERO,
        [ZERO.replace("if first_row:", "if False:"), ZERO.replace("matrix[row][0] == 0 or matrix[0][column] == 0", "matrix[row][0] == 0 and matrix[0][column] == 0")],
        ["Forgets to clear the first row when it originally contained a zero.", "Clears only intersections of marked rows and columns instead of their union."],
        zero_oracle, random_matrix,
        ["Remember which rows and columns originally contained zeros before clearing other cells.", "Store row and column flags in the matrix's first column and row, with separate booleans for those two borders.",
         "Record the two border flags, mark interior zeros, clear interiors using either marker, then clear flagged borders last.",
         "Processing border markers too early destroys the distinction between original zeros and generated zeros."],
        "Use the first row and column as marker storage for the remaining matrix. Record whether each border initially needs clearing, because their shared corner cannot encode both facts. Scan the interior to mark affected rows/columns, clear marked interior cells, and only then clear the two borders according to their saved flags. The oracle instead lists original zero coordinates and builds each output cell from that immutable snapshot.", "O(rows × columns)", "O(1)", difficulty=5,
        stress=[([[[1] * 200 for _ in range(200)]], [[1] * 200 for _ in range(200)])]),
    75: entry("sort_colors", [("nums", "list[int]")], "None", ["arrays", "two-pointers"],
        ["1–300 values, each 0, 1, or 2.", "Reorder nums in place with 0s first, then 1s, then 2s. Do not use a library sort. Target one pass and constant extra space."],
        [([[2, 0, 2, 1, 1, 0]], "Two occurrences of each color become [0,0,1,1,2,2] in the original list."),
         ([[2, 0, 1]], "Move the one 0 to the front and the one 2 to the back, leaving [0,1,2].")],
        [[[0]], [[1]], [[2]], [[0, 0]], [[1, 1]], [[2, 2]], [[2, 0]], [[1, 0]], [[2, 1]],
         [[1, 2, 0]], [[0, 1, 2]], [[2, 2, 0, 1, 0, 1]]], COLORS,
        [COLORS.replace("high -= 1", "high -= 1\n            current += 1"), "def sort_colors(nums):\n    return sorted(nums)\n"],
        ["Skips examining the unknown value swapped in from the high end.", "Returns sorted values without changing the original list."],
        colors_oracle, random_colors,
        ["Maintain finished regions for zeros and twos, with unknown values in between.", "Use low, current, and high pointers: move 0 left, 2 right, and advance past 1.",
         "A 0 swap advances low and current. A 2 swap decrements high but leaves current unchanged. A 1 advances current.",
         "The value arriving from high is unclassified and must be examined before advancing."],
        "Maintain zeros before low, ones between low and current, unknown values from current through high, and twos after high. Every operation reduces the unknown region. A swap with the high end brings in an unknown value, so do not advance current; a swap with low brings in an already classified value and can advance. The oracle sorts a separate copy; the learner-facing reference performs no sort call.", "O(n)", "O(1)", difficulty=5,
        stress=[([[2, 1, 0] * 100], [0] * 100 + [1] * 100 + [2] * 100)]),
    88: entry("merge_sorted_array", [("nums1", "list[int]"), ("m", "int"), ("nums2", "list[int]"), ("n", "int")], "None", ["arrays", "two-pointers"],
        ["0<=m,n and 1<=m+n<=200. nums1 has length m+n; its first m entries and all n entries of nums2 are independently sorted.",
         "The last n entries of nums1 are zero placeholders, not input values. Real values may also be zero and range from -10^9 to 10^9.",
         "Write the merged sorted values into nums1 itself. The function's returned value is ignored."],
        [([[1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3], "Merge [1,2,3] with [2,5,6] into nums1=[1,2,2,3,5,6]; the three placeholders are overwritten."),
         ([[0], 0, [1], 1], "nums1 initially contains no real values. Replace its single placeholder with 1.")],
        [[[1], 1, [], 0], [[0], 1, [], 0], [[0], 0, [0], 1], [[2, 0], 1, [1], 1], [[1, 0], 1, [2], 1],
         [[1, 0], 1, [1], 1], [[-1, 0], 1, [0], 1], [[0, 0], 0, [-2, -1], 2],
         [[1, 2, 0], 2, [0], 1], [[0, 0, 0], 1, [-1, 1], 2], [[-3, -1, 0, 0], 2, [-2, 0], 2],
         [[-1000000000, 0], 1, [1000000000], 1]], MERGE,
        ["def merge_sorted_array(nums1, m, nums2, n):\n    nums1[:] = sorted(nums1 + nums2)\n",
         "def merge_sorted_array(nums1, m, nums2, n):\n    return sorted(nums1[:m] + nums2)\n"],
        ["Treats the placeholder tail as real elements and produces too many values.", "Returns the merged values but does not store them in nums1."],
        merge_oracle, random_merge,
        ["Writing from the front risks overwriting unread nums1 values; the tail is free storage.", "Merge backwards from the largest remaining values of the two inputs.",
         "Compare nums1[m-1] with nums2[n-1], write the larger at the final free slot, and move the corresponding pointer; continue until nums2 is exhausted.",
         "Remaining nums1 values are already in place. Remaining nums2 values still need copying, including when m starts at zero."],
        "Use read pointers at the final real entry of each array and a write pointer at the end of nums1. The larger unread value belongs in the write slot. Moving backwards prevents overwriting unmerged nums1 entries. Once nums2 is exhausted, any remaining nums1 prefix already occupies its correct positions. The oracle sorts only the two real input prefixes. This differs from the original return-a-new-list merge exercise because mutation of caller-owned storage is graded.", "O(m+n)", "O(1)", difficulty=3),
}

for pid, spec in BATCH.items():
    spec["result_mode"] = "returned_prefix" if pid in (26, 27, 80) else "mutated_argument"
    spec["mutated_parameter"] = 0
BATCH[27]["comparator"] = "unordered"
