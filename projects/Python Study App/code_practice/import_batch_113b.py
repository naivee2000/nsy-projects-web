"""Second reviewed group of workbook batch 113; flexible-output 1968 remains pending."""

from collections import deque

from .import_batch_055 import entry


MOD = 1_000_000_007


def obstacle_oracle(arguments):
    values = arguments[0]
    best = []
    for right in range(len(values)):
        lengths = [1] * (right + 1)
        for index in range(right + 1):
            lengths[index] = 1 + max((lengths[prior] for prior in range(index) if values[prior] <= values[index]), default=0)
        best.append(lengths[right])
    return best


def searchable_oracle(arguments):
    nums = arguments[0]
    return sum(all(value < nums[index] for value in nums[:index])
               and all(value > nums[index] for value in nums[index + 1:]) for index in range(len(nums)))


def substring_oracle(arguments):
    patterns, word = arguments
    return sum(any(word[start:start + len(pattern)] == pattern for start in range(len(word) - len(pattern) + 1))
               for pattern in patterns)


def product_oracle(arguments):
    p = arguments[0]
    maximum = (1 << p) - 1
    if p > 10:
        return maximum % MOD * pow(maximum - 1, (maximum - 1) // 2, MOD) % MOD
    value = maximum
    for _ in range((maximum - 1) // 2):
        value = value * (maximum - 1) % MOD
    return value


def cross_oracle(arguments):
    rows, columns, cells = arguments

    def possible(day):
        water = {tuple(cell) for cell in cells[:day]}
        queue = deque((1, column) for column in range(1, columns + 1) if (1, column) not in water)
        seen = set(queue)
        while queue:
            row, column = queue.popleft()
            if row == rows:
                return True
            for neighbor in ((row-1,column),(row+1,column),(row,column-1),(row,column+1)):
                if (1 <= neighbor[0] <= rows and 1 <= neighbor[1] <= columns
                        and neighbor not in water and neighbor not in seen):
                    seen.add(neighbor)
                    queue.append(neighbor)
        return False

    return max(day for day in range(rows * columns + 1) if possible(day))


def random_obstacle(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 30))]]


def random_searchable(rng):
    length = rng.randint(1, 30)
    return [rng.sample(range(-100, 101), length)]


def random_substring(rng):
    word = "".join(rng.choice("abcd") for _ in range(rng.randint(1, 20)))
    return [["".join(rng.choice("abcd") for _ in range(rng.randint(1, 8))) for _ in range(rng.randint(1, 20))], word]


def random_product(rng):
    return [rng.randint(1, 10)]


def random_cross(rng):
    rows, columns = rng.randint(2, 5), rng.randint(2, 5)
    cells = [[row, column] for row in range(1, rows + 1) for column in range(1, columns + 1)]
    rng.shuffle(cells)
    return [rows, columns, cells]


OBSTACLE = '''\
def longest_obstacle_course_at_each_position(obstacles):
    from bisect import bisect_right
    tails = []
    answer = []
    for height in obstacles:
        length = bisect_right(tails, height)
        if length == len(tails):
            tails.append(height)
        else:
            tails[length] = height
        answer.append(length + 1)
    return answer
'''

SEARCHABLE = '''\
def count_binary_searchable_numbers(nums):
    size = len(nums)
    prefix = [float("-inf")] * size
    largest = float("-inf")
    for index in range(size):
        prefix[index] = largest
        largest = max(largest, nums[index])
    answer = 0
    smallest = float("inf")
    for index in range(size - 1, -1, -1):
        if prefix[index] < nums[index] < smallest:
            answer += 1
        smallest = min(smallest, nums[index])
    return answer
'''

SUBSTRING = '''\
def count_patterns_in_word(patterns, word):
    return sum(pattern in word for pattern in patterns)
'''

PRODUCT = '''\
def minimum_nonzero_bit_swap_product(p):
    mod = 1_000_000_007
    maximum = (1 << p) - 1
    pairs = (maximum - 1) // 2
    return maximum % mod * pow(maximum - 1, pairs, mod) % mod
'''

CROSS = '''\
def latest_crossing_day(row, col, cells):
    from collections import deque

    def can_cross(day):
        water = {tuple(cell) for cell in cells[:day]}
        queue = deque((1, column) for column in range(1, col + 1) if (1, column) not in water)
        seen = set(queue)
        while queue:
            r, c = queue.popleft()
            if r == row:
                return True
            for nr, nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if 1 <= nr <= row and 1 <= nc <= col and (nr,nc) not in water and (nr,nc) not in seen:
                    seen.add((nr,nc))
                    queue.append((nr,nc))
        return False

    lower, upper = 0, row * col
    while lower < upper:
        middle = (lower + upper + 1) // 2
        if can_cross(middle):
            lower = middle
        else:
            upper = middle - 1
    return lower
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1964: entry("longest_obstacle_course_at_each_position", [("obstacles","list[int]")], "list[int]",
        ["arrays","binary search","longest increasing subsequence"],
        ["obstacles has 1 through 100000 positive heights, each at most 10000000.", "For each index, the course must end at that index and choose earlier positions in order.", "Course heights must be nondecreasing, so equal heights may extend a course."],
        [([[1,2,3,2]], "The final height two extends the course [1,2], producing lengths [1,2,3,3]."),
         ([[2,2,1]], "The second equal height extends to length two, while the final lower height starts a new course.")],
        [[a] for a in [[1],[1,2],[2,1],[2,2],[1,2,3,2],[3,1,5,6,4,2],[5,4,3,2,1],[1,1,1,1],
                       [2,1,2,1,2],[10,1,9,2,8,3],[1,3,2,4,3,5],[10000000,1],[4,2,2,3,1,5],[7,7,6,7,8]]],
        OBSTACLE,[OBSTACLE.replace("bisect_right", "bisect_left"),OBSTACLE.replace("answer.append(length + 1)", "answer.append(len(tails))")],
        ["Uses strict-increasing insertion and fails to extend equal heights.", "Returns the global tails length rather than the best course ending at the current obstacle."],
        obstacle_oracle,random_obstacle,lesson("This is a longest nondecreasing subsequence ending at every position.","Maintain the smallest possible tail for each course length and use upper-bound search for the current height.","i=bisect_right(tails,height); replace/append tails[i]; answer i+1.","Upper bound permits equality. The tail invariant makes i the longest extendable length, so i+1 is optimal specifically at this position."),
        "O(n log n)","O(n)",8),
    1966: entry("count_binary_searchable_numbers",[("nums","list[int]")],"int",["arrays","prefix maxima","suffix minima"],
        ["nums has 1 through 100000 distinct integers from -100000 through 100000.", "A target is guaranteed under arbitrary pivots exactly when every value left of it is smaller and every value right of it is larger.", "Count values satisfying this property."],
        [([[7]],"The sole value cannot be discarded by another pivot, so it is searchable."),([[1,3,2,4]],"Only one and four have all smaller values to the left and all larger values to the right.")],
        [[a] for a in [[0],[1,2],[2,1],[1,2,3],[3,2,1],[1,3,2,4],[7,1,5,3],[3,1,2],[2,3,1],[-3,-2,-1],[-1,-3,-2],[5,1,2,3,4],[1,5,2,3,6],[-5,0,5,-1,10]]],
        SEARCHABLE,[SEARCHABLE.replace("prefix[index] < nums[index] < smallest","prefix[index] <= nums[index]"),SEARCHABLE.replace("smallest = min(smallest, nums[index])","smallest = nums[index]")],
        ["Checks only the left side and ignores a smaller value to the right.","Tracks only the immediate right neighbor rather than the minimum of the entire suffix."],searchable_oracle,random_searchable,
        lesson("Any smaller-or-equal left pivot or larger-or-equal right pivot could discard the target.","Precompute the maximum strictly left of each index, then scan right-to-left with the minimum strictly right.","Count i when left_max[i]<nums[i]<right_min; update right_min.","Those inequalities prevent every possible pivot from discarding the target; violating either supplies a pivot choice that removes it."),"O(n)","O(n)",5),
    1967: entry("count_patterns_in_word",[("patterns","list[str]"),("word","str")],"int",["strings","arrays"],
        ["patterns has 1 through 100 lowercase strings of length 1 through 100; duplicates are allowed.","word has 1 through 100 lowercase letters.","Count each pattern position whose whole string occurs contiguously in word."],
        [([["a","abc","bc","d"],"abc"],"a, abc, and bc are substrings, so three pattern entries count."),([ ["a","a","b"],"a"],"Both copies of a count separately, giving two.")],
        [[p,w] for p,w in [(["a"],"a"),(["a"],"b"),(["ab"],"zabz"),(["a","a"],"a"),(["abc","bc","c"],"abc"),(["abcd"],"abc"),(["x","xy","yx"],"xyx"),(["aa","aaa"],"aaaa"),(["cat","dog"],"catalog"),(["z"],"zzzz"),(["abc","d"],"defabc"),(["aba","bab"],"ababa"),(["longpattern"],"short"),(["a","b","c","d"],"abcd")]],
        SUBSTRING,[SUBSTRING.replace("pattern in word","word in pattern"),'''def count_patterns_in_word(patterns, word):\n    return len({pattern for pattern in patterns if pattern in word})\n'''],
        ["Reverses the containment direction.","Deduplicates equal pattern entries even though indices count separately."],substring_oracle,random_substring,
        lesson("Each pattern is an independent membership question, including duplicate entries.","Use the language's contiguous substring test for every list element and sum the booleans.","return sum(pattern in word for pattern in patterns).","The membership predicate is true exactly for a contiguous occurrence, and summing over positions preserves duplicate multiplicity."),"O(total pattern length*word length)","O(1)",3),
    1969: entry("minimum_nonzero_bit_swap_product",[("p","int")],"int",["math","greedy","modular arithmetic"],
        ["1 <= p <= 60.","The initial multiset contains every integer from 1 through 2^p-1.","Swapping same-position bits preserves each bit column; minimize a nonzero product and return it modulo 1000000007."],
        [([1],"The array contains only one, so the product is one."),([2],"The values can become one, two, and three, whose minimum nonzero product is six.")],
        [[p] for p in [3,4,5,6,7,8,10,15,20,30,40,50,59,60]],PRODUCT,
        [PRODUCT.replace("maximum - 1, pairs","maximum - 2, pairs"),PRODUCT.replace("pairs, mod","pairs - 1, mod")],
        ["Uses 2^p-3 as the repeated paired value instead of 2^p-2.","Uses one too few paired factors."],product_oracle,random_product,
        lesson("Pair each x with its bitwise complement: preserving one all-ones value lets every other pair become 1 and 2^p-2.","The product is (2^p-1)*(2^p-2)^(2^(p-1)-1) modulo M.","maximum=2^p-1; pairs=(maximum-1)//2; multiply maximum by modular_power(maximum-1,pairs).","For a fixed pair sum, pushing positive factors to 1 and sum-1 minimizes their product. Complement pairs have the needed conserved bits, while the all-ones value remains unpaired."),"O(log(2^p))","O(1)",5),
    1970: entry("latest_crossing_day",[("row","int"),("col","int"),("cells","list[list[int]]")],"int",["matrices","binary search","breadth-first search"],
        ["2 <= row,col <= 20000, row*col <= 20000, and cells is a permutation of every 1-based grid coordinate.","On day d, the first d cells are water; movement uses four directions through land.","Return the greatest day when some top-row land cell connects to some bottom-row land cell."],
        [([2,2,[[1,1],[2,1],[1,2],[2,2]]],"A right-column path remains on day two, but no crossing remains on day three."),([2,2,[[1,1],[1,2],[2,1],[2,2]]],"Flooding both top cells takes two days, so day one is the last crossing day.")],
        [[r,c,cells] for r,c,cells in [(2,2,[[1,1],[2,1],[1,2],[2,2]]),(2,2,[[1,1],[1,2],[2,1],[2,2]]),(2,3,[[1,1],[2,1],[1,2],[2,2],[1,3],[2,3]]),(3,2,[[1,1],[2,1],[3,1],[1,2],[2,2],[3,2]]),(3,3,[[1,1],[2,2],[3,3],[1,2],[2,1],[3,2],[1,3],[2,3],[3,1]]),(2,2,[[2,2],[1,1],[2,1],[1,2]]),(2,3,[[2,2],[1,2],[1,1],[2,1],[1,3],[2,3]]),(3,2,[[2,1],[2,2],[1,1],[3,1],[1,2],[3,2]]),(2,4,[[1,1],[2,1],[1,2],[2,2],[1,3],[2,3],[1,4],[2,4]]),(4,2,[[1,1],[2,1],[3,1],[4,1],[1,2],[2,2],[3,2],[4,2]]),(3,3,[[2,2],[1,1],[3,3],[1,3],[3,1],[2,1],[2,3],[1,2],[3,2]]),(2,3,[[1,3],[2,2],[1,1],[2,1],[1,2],[2,3]]),(3,2,[[3,1],[2,2],[1,1],[2,1],[1,2],[3,2]]),(2,5,[[1,1],[2,1],[1,2],[2,2],[1,3],[2,3],[1,4],[2,4],[1,5],[2,5]]),(3,3,[[3,1],[1,2],[1,3],[2,1],[2,2],[2,3],[3,2],[3,3],[1,1]])]],
        CROSS,[CROSS.replace("cells[:day]","cells[:day + 1]"),CROSS.replace("(r,c-1),(r,c+1)","(r-1,c),(r+1,c)")],
        ["Floods one extra cell and reports a day too early.","Allows vertical movement only and misses crossings that must change columns."],cross_oracle,random_cross,
        lesson("Crossability is monotone: once flooding disconnects top from bottom, later days cannot restore a path.","Binary-search the last feasible day; each check floods the prefix and runs multi-source BFS from all dry top cells.","can_cross(d): BFS four-direction land after first d floods; upper-bound binary search over 0..row*col.","BFS exactly recognizes a land connection, and monotonic flooding partitions days into feasible then infeasible, so upper-bound search returns the last feasible day."),"O(row*col*log(row*col))","O(row*col)",8),
}
