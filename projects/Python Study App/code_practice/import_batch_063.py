"""Reviewed trie-style strings, queues, DP, search, greedy, and math imports."""
from collections import Counter, deque

from .import_batch_055 import entry


def variable_average_oracle(args):
    nums, k = args
    return max(sum(nums[start:end]) / (end - start)
               for start in range(len(nums)) for end in range(start + k, len(nums) + 1))


def replace_oracle(args):
    roots, sentence = args
    output = []
    for word in sentence.split():
        choices = [root for root in roots if word.startswith(root)]
        output.append(min(choices, key=len) if choices else word)
    return ' '.join(output)


def senate_oracle(args):
    senate = args[0]
    radiant = deque(i for i, party in enumerate(senate) if party == 'R')
    dire = deque(i for i, party in enumerate(senate) if party == 'D')
    size = len(senate)
    while radiant and dire:
        r, d = radiant.popleft(), dire.popleft()
        if r < d: radiant.append(r + size)
        else: dire.append(d + size)
    return 'Radiant' if radiant else 'Dire'


def two_keys_oracle(args):
    target = args[0]
    queue = deque([(1, 0, 0)])
    visited = {(1, 0)}
    while queue:
        screen, clipboard, steps = queue.popleft()
        if screen == target: return steps
        for following in ((screen, screen), (screen + clipboard, clipboard)):
            if following[0] <= target and following not in visited and following != (screen, clipboard):
                visited.add(following); queue.append((*following, steps + 1))


def four_keys_oracle(args):
    presses = args[0]
    from functools import lru_cache
    @lru_cache(None)
    def search(remaining, screen, clipboard):
        if remaining == 0: return screen
        best = search(remaining - 1, screen + 1, clipboard)
        if remaining >= 2 and screen:
            best = max(best, search(remaining - 2, screen, screen))
        if clipboard:
            best = max(best, search(remaining - 1, screen + clipboard, clipboard))
        return best
    return search(presses, 0, 0)


def robot_oracle(args):
    moves = args[0]
    return moves.count('L') == moves.count('R') and moves.count('U') == moves.count('D')


def closest_oracle(args):
    arr, k, x = args
    return sorted(sorted(arr, key=lambda value: (abs(value - x), value))[:k])


def split_oracle(args):
    nums = args[0]
    memo = {}
    def search(index, sequences):
        key = (index, tuple(sorted(sequences)))
        if key in memo: return memo[key]
        if index == len(nums):
            return all(length >= 3 for _, length in sequences)
        value = nums[index]
        options = set()
        for position, (end, length) in enumerate(sequences):
            if end == value - 1 and (end, length) not in options:
                options.add((end, length))
                updated = list(sequences); updated[position] = (value, length + 1)
                if search(index + 1, tuple(updated)):
                    memo[key] = True; return True
        if search(index + 1, sequences + ((value, 1),)):
            memo[key] = True; return True
        memo[key] = False; return False
    return search(0, tuple())


def remove_nine_oracle(args):
    remaining, value = args[0], 0
    while remaining:
        value += 1
        if '9' not in str(value): remaining -= 1
    return value


def random_variable_average(rng):
    nums = [rng.randint(-50, 50) for _ in range(rng.randint(1, 16))]
    return [nums, rng.randint(1, len(nums))]


def random_replace(rng):
    roots = {''.join(rng.choice('abcd') for _ in range(rng.randint(1, 4))) for _ in range(rng.randint(1, 6))}
    words = [''.join(rng.choice('abcd') for _ in range(rng.randint(1, 8))) for _ in range(rng.randint(1, 7))]
    return [sorted(roots), ' '.join(words)]


def random_senate(rng):
    text = ''.join(rng.choice('RD') for _ in range(rng.randint(1, 25)))
    return [text]


def random_two_keys(rng): return [rng.randint(1, 40)]
def random_four_keys(rng): return [rng.randint(1, 12)]
def random_robot(rng): return [''.join(rng.choice('LRUD') for _ in range(rng.randint(1, 40)))]


def random_closest(rng):
    arr = sorted(rng.sample(range(-50, 51), rng.randint(1, 20)))
    return [arr, rng.randint(1, len(arr)), rng.randint(-60, 60)]


def random_split(rng):
    return [sorted(rng.randint(0, 8) for _ in range(rng.randint(1, 10)))]


def random_remove_nine(rng): return [rng.randint(1, 400)]


VARIABLE_AVERAGE = '''\
def maximum_variable_average(nums, k):
    low, high = min(nums), max(nums)
    def possible(average):
        prefix = [0.0]
        for value in nums:
            prefix.append(prefix[-1] + value - average)
        smallest = 0.0
        for end in range(k, len(nums) + 1):
            smallest = min(smallest, prefix[end - k])
            if prefix[end] >= smallest:
                return True
        return False
    for _ in range(60):
        middle = (low + high) / 2
        if possible(middle): low = middle
        else: high = middle
    return low
'''


REPLACE = '''\
def replace_words(dictionary, sentence):
    roots = set(dictionary)
    answer = []
    for word in sentence.split():
        replacement = word
        for length in range(1, len(word) + 1):
            if word[:length] in roots:
                replacement = word[:length]
                break
        answer.append(replacement)
    return ' '.join(answer)
'''


SENATE = '''\
def senate_winner(senate):
    from collections import deque
    radiant = deque(i for i, party in enumerate(senate) if party == 'R')
    dire = deque(i for i, party in enumerate(senate) if party == 'D')
    size = len(senate)
    while radiant and dire:
        r, d = radiant.popleft(), dire.popleft()
        if r < d: radiant.append(r + size)
        else: dire.append(d + size)
    return 'Radiant' if radiant else 'Dire'
'''


TWO_KEYS = '''\
def minimum_copy_paste_steps(n):
    steps = 0
    factor = 2
    while factor * factor <= n:
        while n % factor == 0:
            steps += factor
            n //= factor
        factor += 1
    return steps + (n if n > 1 else 0)
'''


FOUR_KEYS = '''\
def maximum_keyboard_as(n):
    best = list(range(n + 1))
    for presses in range(1, n + 1):
        for breakpoint in range(1, presses - 2):
            best[presses] = max(best[presses], best[breakpoint] * (presses - breakpoint - 1))
    return best[n]
'''


ROBOT = '''\
def returns_to_origin(moves):
    horizontal = vertical = 0
    for move in moves:
        horizontal += (move == 'R') - (move == 'L')
        vertical += (move == 'U') - (move == 'D')
    return horizontal == 0 and vertical == 0
'''


CLOSEST = '''\
def k_closest_elements(arr, k, x):
    low, high = 0, len(arr) - k
    while low < high:
        middle = (low + high) // 2
        if x - arr[middle] > arr[middle + k] - x:
            low = middle + 1
        else:
            high = middle
    return arr[low:low + k]
'''


SPLIT = '''\
def can_split_consecutive(nums):
    available = Counter(nums)
    endings = Counter()
    for value in nums:
        if available[value] == 0: continue
        available[value] -= 1
        if endings[value - 1]:
            endings[value - 1] -= 1
            endings[value] += 1
        elif available[value + 1] and available[value + 2]:
            available[value + 1] -= 1
            available[value + 2] -= 1
            endings[value + 2] += 1
        else:
            return False
    return True
'''


REMOVE_NINE = '''\
def nth_number_without_nine(n):
    digits = []
    while n:
        digits.append(str(n % 9))
        n //= 9
    return int(''.join(reversed(digits)))
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial], editorial


BATCH = {
    644: entry('maximum_variable_average', [('nums','list[int]'),('k','int')], 'float', ['binary-search','prefix-sums'],
        ['1 <= k <= len(nums) <= 10,000; values are between -10,000 and 10,000.', 'Return the maximum average of a contiguous subarray whose length is at least k, within 1e-5.'],
        [([[1,12,-5,-6,50,3],4], 'The best eligible subarray is [12,-5,-6,50], averaging 12.75.'), ([[5,10],1], 'The length-one subarray [10] has the largest average.')],
        [[nums,k] for nums,k in (([1],1),([1,2],2),([-1,-2,-3],1),([-1,-2,-3],2),([1,2,3],2),([5,0,5],2),([1,10,10],2),([10,-10,10,-10],3),([0,0,0],2),([3,3,4,4],3),([-5,100,-5],2),([1,2,100,100,100],2))],
        VARIABLE_AVERAGE, ["def maximum_variable_average(nums, k):\n    return max(sum(nums[i:i+k]) / k for i in range(len(nums)-k+1))\n", "def maximum_variable_average(nums, k):\n    return float(max(nums))\n"],
        ['Considers only subarrays of exactly k elements.', 'Returns the largest element even when k requires a longer subarray.'], variable_average_oracle, random_variable_average,
        *lesson('For a guessed average, subtract it from every value and ask whether an eligible subarray has nonnegative sum.', 'Binary-search the answer and test it using prefix minima.', 'For each end at least k, compare its prefix sum with the smallest prefix ending at most end-k.', 'The feasibility predicate is monotone: every average below an achievable one is also achievable.'), 'O(n log precision)', 'O(n)', 8),
    648: entry('replace_words', [('dictionary','list[str]'),('sentence','str')], 'str', ['strings','tries'],
        ['Dictionary roots and sentence words contain lowercase letters; words are separated by single spaces.', 'Replace each word with its shortest dictionary prefix, if one exists.'],
        [([['cat','bat','rat'],'the cattle was rattled by the battery'], 'The derivatives cattle, rattled, and battery use their shortest matching roots.'), ([['a','aa','aaa'],'aadsfasf absbs bbab cadsfafs'], 'Every word beginning with a becomes a; the other words remain unchanged.')],
        [[roots,s] for roots,s in ((['a'],'a'),(['a'],'abc'),(['ab'],'a'),(['cat','c'],'cattle'),(['x','xy'],'xyz xy'),(['dog'],'the dog'),(['bat','battery'],'battery'),(['a','b'],'apple banana'),(['z'],'alpha beta'),(['car','cat'],'cater carpool'),(['r','rat'],'rattled'),(['one','two'],'onefold threefold'))],
        REPLACE, [REPLACE.replace('range(1, len(word) + 1)','range(len(word), 0, -1)'), REPLACE.replace("replacement = word","replacement = ''")],
        ['Chooses the longest matching root rather than the shortest.', 'Deletes words that have no matching root.'], replace_oracle, random_replace,
        *lesson('Only prefixes matter, and the first matching length is optimal.', 'Store roots in a set and scan each word’s prefixes from shortest to longest.', 'For each word, stop at the first prefix in roots; otherwise keep the word.', 'Checking prefix lengths in increasing order directly enforces the shortest-root rule.'), 'O(total sentence characters squared)', 'O(total root characters)', 5),
    649: entry('senate_winner', [('senate','str')], 'str', ['queues','greedy'],
        ['1 <= len(senate) <= 10,000; every character is R or D.', 'Senators act cyclically in input order and each active senator bans one opponent.'],
        [(['RD'], 'Radiant acts first and bans the Dire senator.'), (['RDD'], 'After Radiant bans one Dire senator, the remaining Dire senator bans Radiant.')],
        [[s] for s in ('R','D','DR','RRD','DDR','RDR','DRD','RRDDD','DDRRR','RDRD','RRRRD','DRRRDD')],
        SENATE, ["def senate_winner(senate):\n    return 'Radiant' if senate.count('R') >= senate.count('D') else 'Dire'\n", "def senate_winner(senate):\n    return 'Radiant' if senate[0] == 'R' else 'Dire'\n"],
        ['Assumes the initial majority always wins.', 'Assumes the first senator’s party always wins.'], senate_oracle, random_senate,
        *lesson('Relative turn order determines which party receives each ban.', 'Queue the future turn indices of both parties.', 'Pop one from each queue; the earlier index survives and returns with index+n.', 'Pairing the earliest active senators models one ban while preserving the cyclic order of every survivor.'), 'O(n)', 'O(n)', 5),
    650: entry('minimum_copy_paste_steps', [('n','int')], 'int', ['math','dynamic-programming'],
        ['1 <= n <= 1,000.', 'Start with one A; Copy All and Paste each cost one operation.'],
        [([3], 'Copy once and paste twice to reach three As in three operations.'), ([1], 'The screen already contains the requested one A, so zero operations are needed.')],
        [[n] for n in (2,4,5,6,7,8,9,10,12,15,18,100)],
        TWO_KEYS, ["def minimum_copy_paste_steps(n):\n    return n\n", "def minimum_copy_paste_steps(n):\n    return 0 if n == 1 else 2 * (n.bit_length() - 1)\n"],
        ['Uses one copy followed by n-1 pastes for every target.', 'Assumes copy-paste can double the screen optimally at every stage.'], two_keys_oracle, random_two_keys,
        *lesson('A copy followed by pastes multiplies the current count by an integer factor.', 'Break n into prime factors; each factor costs that many operations.', 'Repeatedly divide n by its smallest factors and add each factor.', 'Splitting a composite multiplier a*b costs a+b, never more than the unsplit cost a*b, so prime factors are optimal.'), 'O(sqrt(n))', 'O(1)', 5),
    651: entry('maximum_keyboard_as', [('n','int')], 'int', ['dynamic-programming','math'],
        ['1 <= n <= 50.', 'Use A, Ctrl-A, Ctrl-C, and Ctrl-V to maximize the final number of As in at most n key presses.'],
        [([3], 'Pressing A three times produces three As.'), ([7], 'Type AAA, select all, copy, and paste twice to produce nine As.')],
        [[n] for n in (1,2,4,5,6,8,9,10,11,12,15,20)],
        FOUR_KEYS, ["def maximum_keyboard_as(n):\n    return n\n", FOUR_KEYS.replace('presses - breakpoint - 1','presses - breakpoint - 2')],
        ['Never uses copy and paste.', 'Undercounts the number of available pastes after select-all and copy.'], four_keys_oracle, random_four_keys,
        *lesson('An optimal copy phase starts from a previously optimal screen.', 'Try every breakpoint before Ctrl-A, Ctrl-C, and the remaining pastes.', 'dp[i]=max(i, dp[j]*(i-j-1)) for valid earlier j.', 'After the breakpoint, two setup keys preserve the screen and every remaining paste adds one saved copy.'), 'O(n^2)', 'O(n)', 5),
    657: entry('returns_to_origin', [('moves','str')], 'bool', ['strings','simulation'],
        ['1 <= len(moves) <= 20,000; moves contains only L, R, U, and D.', 'Return true exactly when the final horizontal and vertical coordinates are both zero.'],
        [(['UD'], 'The upward and downward moves cancel.'), (['LL'], 'Two left moves end away from the origin.')],
        [[s] for s in ('L','R','U','D','LR','RL','DU','LURD','LLRR','UUDD','LDR','RRUULLDD')],
        ROBOT, [ROBOT.replace("horizontal == 0 and vertical == 0","horizontal == 0 or vertical == 0"), ROBOT.replace("- (move == 'L')","+ (move == 'L')")],
        ['Accepts when only one coordinate returns to zero.', 'Moves left in the same direction as right.'], robot_oracle, random_robot,
        *lesson('Opposite moves contribute opposite signed coordinate changes.', 'Track horizontal and vertical displacement in one pass.', 'Add for R/U, subtract for L/D, then require both totals to be zero.', 'The order of translations does not affect their final vector sum.'), 'O(len(moves))', 'O(1)', 3),
    658: entry('k_closest_elements', [('arr','list[int]'),('k','int'),('x','int')], 'list[int]', ['binary-search','two-pointers'],
        ['1 <= k <= len(arr) <= 10,000; arr is sorted.', 'Return k closest values in ascending order; equal distances favor the smaller value.'],
        [([[1,2,3,4,5],4,3], 'The four closest values are one through four after the smaller-value tie break.'), ([[1,2,3,4,5],4,-1], 'When x lies left of the array, the first four values are closest.')],
        [[arr,k,x] for arr,k,x in (([1],1,0),([1,2],1,2),([1,2],1,0),([1,2,3],2,2),([1,2,3],2,10),([-5,-2,0,3],2,-1),([1,1,1,10],3,2),([0,2,4,6],2,3),([1,3,5,7,9],3,6),([1,2,3,4,5],5,3),([-10,0,10],1,5),([1,4,6,8],2,5))],
        CLOSEST, [CLOSEST.replace('> arr[middle + k] - x','>= arr[middle + k] - x'), CLOSEST.replace('len(arr) - k','len(arr) - k - 1')],
        ['Breaks distance ties toward the larger right window.', 'Excludes the final valid window start from binary search.'], closest_oracle, random_closest,
        *lesson('The k closest values form a contiguous window in sorted order.', 'Binary-search the window start by comparing its excluded boundary candidates.', 'If x-left > right-x, move the window right; otherwise keep the left side.', 'The boundary comparison is monotone across window starts and naturally applies the smaller-value tie break.'), 'O(log(n-k) + k)', 'O(k)', 5),
    659: entry('can_split_consecutive', [('nums','list[int]')], 'bool', ['greedy','hash-maps'],
        ['1 <= len(nums) <= 10,000; nums is sorted.', 'Partition every value into consecutive subsequences, each of length at least three.'],
        [([[1,2,3,3,4,5]], 'The values split into [1,2,3] and [3,4,5].'), ([[1,2,3,4,4,5]], 'The remaining [4,5] cannot form a length-three subsequence.')],
        [[[v for v in nums]] for nums in ([1,2,3],[1,2],[1,2,3,4],[1,2,3,3,4,5,5,6,7],[1,1,2,2,3,3],[1,2,3,4,5,5],[1,2,3,4,5,6],[1,2,4],[1,2,3,3,4,4,5,5],[0,1,2,2,3,4],[-2,-1,0],[1,2,3,3,4,5,6])],
        SPLIT, ["def can_split_consecutive(nums):\n    return all(b-a <= 1 for a,b in zip(nums, nums[1:]))\n", SPLIT.replace('available[value + 1] and available[value + 2]','available[value + 1]')],
        ['Checks only adjacent gaps and ignores subsequence multiplicities and lengths.', 'Starts a new chain without reserving its third value.'], split_oracle, random_split,
        *lesson('A value should extend an existing chain before starting a new one.', 'Track unused counts and how many chains end at each value.', 'Extend an ending at x-1; otherwise reserve x+1 and x+2 for a new chain; fail if neither works.', 'Extending protects short chains, while reserving two future values guarantees every newly created chain is already valid.'), 'O(n)', 'O(n)', 5),
    660: entry('nth_number_without_nine', [('n','int')], 'int', ['math','number-systems'],
        ['1 <= n <= 800,000,000.', 'Return the nth positive integer whose decimal representation contains no digit 9.'],
        [([9], 'After 1 through 8, decimal 9 is skipped, so the ninth value is 10.'), ([1], 'The first value is one.')],
        [[n] for n in (2,8,10,11,18,19,20,80,81,82,100,400)],
        REMOVE_NINE, [REMOVE_NINE.replace('n % 9','n % 10'), REMOVE_NINE.replace("return int(''.join(reversed(digits)))","return int(''.join(digits))")],
        ['Uses decimal digits and therefore fails to skip values containing nine.', 'Leaves the base-nine digits reversed.'], remove_nine_oracle, random_remove_nine,
        *lesson('The allowed decimal digits 0 through 8 behave exactly like base-nine digits.', 'Write n in base nine and interpret those digits as decimal.', 'Repeatedly collect n mod 9, reverse the digits, and parse the result.', 'Counting strings over nine allowed digits matches positional base-nine counting without ever producing digit 9.'), 'O(log n)', 'O(log n)', 8),
}

BATCH[644]['comparator'] = 'float'
