"""First reviewed group of workbook batch 114."""

from functools import lru_cache
from itertools import combinations

from .import_batch_055 import entry


MOD = 1_000_000_007


def sessions_oracle(args):
    tasks, limit = args
    size = len(tasks)
    valid = []
    for mask in range(1, 1 << size):
        if sum(tasks[index] for index in range(size) if mask >> index & 1) <= limit:
            valid.append(mask)
    best = [size + 1] * (1 << size)
    best[0] = 0
    for mask in range(1 << size):
        for group in valid:
            if mask & group == 0:
                best[mask | group] = min(best[mask | group], best[mask] + 1)
    return best[-1]


def subsequences_oracle(args):
    binary = args[0]
    found = set()
    for mask in range(1, 1 << len(binary)):
        text = ''.join(binary[index] for index in range(len(binary)) if mask >> index & 1)
        if text == '0' or text[0] == '1':
            found.add(text)
    return len(found) % MOD


def caught_oracle(args):
    team, distance = args
    agents = [index for index, value in enumerate(team) if value == 0]
    targets = [index for index, value in enumerate(team) if value == 1]
    @lru_cache(None)
    def match(at, used):
        if at == len(agents):
            return 0
        answer = match(at + 1, used)
        for target_index, position in enumerate(targets):
            if not (used >> target_index & 1) and abs(agents[at] - position) <= distance:
                answer = max(answer, 1 + match(at + 1, used | 1 << target_index))
        return answer
    return match(0, 0)


def middle_oracle(args):
    nums = args[0]
    for index in range(len(nums)):
        if sum(nums[:index]) == sum(nums[index + 1:]):
            return index
    return -1


def farmland_oracle(args):
    land = args[0]
    rows, columns = len(land), len(land[0])
    seen = set(); answer = []
    for row in range(rows):
        for column in range(columns):
            if not land[row][column] or (row, column) in seen:
                continue
            stack = [(row, column)]; seen.add((row, column)); cells = []
            while stack:
                r, c = stack.pop(); cells.append((r, c))
                for nr, nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                    if 0 <= nr < rows and 0 <= nc < columns and land[nr][nc] and (nr,nc) not in seen:
                        seen.add((nr,nc)); stack.append((nr,nc))
            answer.append([min(r for r, _ in cells), min(c for _, c in cells),
                           max(r for r, _ in cells), max(c for _, c in cells)])
    return answer


def random_sessions(rng):
    limit = rng.randint(1, 12)
    return [[rng.randint(1, limit) for _ in range(rng.randint(1, 9))], limit]


def random_binary(rng):
    return [''.join(rng.choice('01') for _ in range(rng.randint(1, 15)))]


def random_caught(rng):
    return [[rng.randint(0, 1) for _ in range(rng.randint(1, 10))], rng.randint(0, 6)]


def random_middle(rng):
    return [[rng.randint(-20, 20) for _ in range(rng.randint(1, 50))]]


def random_farmland(rng):
    rows, columns = rng.randint(1, 7), rng.randint(1, 7)
    land = [[0] * columns for _ in range(rows)]
    for _ in range(rng.randint(0, 4)):
        top, bottom = sorted((rng.randrange(rows), rng.randrange(rows)))
        left, right = sorted((rng.randrange(columns), rng.randrange(columns)))
        if all(land[r][c] == 0 for r in range(top, bottom + 1) for c in range(left, right + 1)):
            if all(not (0 <= r < rows and 0 <= c < columns and land[r][c])
                   for r in range(top - 1, bottom + 2) for c in range(left - 1, right + 2)
                   if r in (top - 1, bottom + 1) or c in (left - 1, right + 1)):
                for r in range(top, bottom + 1):
                    for c in range(left, right + 1):
                        land[r][c] = 1
    return [land]


SESSIONS = '''\
def minimum_work_sessions(tasks, session_time):
    tasks = sorted(tasks, reverse=True)
    sessions = []
    best = len(tasks)
    def search(index):
        nonlocal best
        if len(sessions) >= best:
            return
        if index == len(tasks):
            best = len(sessions)
            return
        duration = tasks[index]
        tried = set()
        for position in range(len(sessions)):
            if sessions[position] in tried or sessions[position] + duration > session_time:
                continue
            tried.add(sessions[position])
            sessions[position] += duration
            search(index + 1)
            sessions[position] -= duration
        sessions.append(duration)
        search(index + 1)
        sessions.pop()
    search(0)
    return best
'''

SUBSEQUENCES = '''\
def number_of_unique_good_subsequences(binary):
    mod = 1_000_000_007
    ending_zero = ending_one = 0
    has_zero = 0
    for digit in binary:
        if digit == '1':
            ending_one = (ending_zero + ending_one + 1) % mod
        else:
            ending_zero = (ending_zero + ending_one) % mod
            has_zero = 1
    return (ending_zero + ending_one + has_zero) % mod
'''

CAUGHT = '''\
def maximum_people_caught(team, dist):
    agents = [index for index, value in enumerate(team) if value == 0]
    people = [index for index, value in enumerate(team) if value == 1]
    left = right = answer = 0
    while left < len(agents) and right < len(people):
        if abs(agents[left] - people[right]) <= dist:
            answer += 1; left += 1; right += 1
        elif agents[left] < people[right]:
            left += 1
        else:
            right += 1
    return answer
'''

MIDDLE = '''\
def find_middle_index(nums):
    right = sum(nums)
    left = 0
    for index, value in enumerate(nums):
        right -= value
        if left == right:
            return index
        left += value
    return -1
'''

FARMLAND = '''\
def find_farmland_groups(land):
    rows, columns = len(land), len(land[0])
    answer = []
    for row in range(rows):
        for column in range(columns):
            if land[row][column] == 0 or (row > 0 and land[row-1][column]) or (column > 0 and land[row][column-1]):
                continue
            bottom, right = row, column
            while bottom + 1 < rows and land[bottom+1][column]:
                bottom += 1
            while right + 1 < columns and land[row][right+1]:
                right += 1
            answer.append([row, column, bottom, right])
    return answer
'''


def lesson(*parts):
    return list(parts)


BATCH = {
    1986: entry('minimum_work_sessions',[('tasks','list[int]'),('session_time','int')],'int',['backtracking','bitmask dynamic programming','sorting'],
        ['tasks has 1 through 14 positive durations, each no greater than session_time.','A session can contain any tasks whose total duration does not exceed session_time.','Return the fewest sessions needed to finish every task.'],
        [([[1,2,3],3],'Put durations one and two together and duration three alone, requiring two sessions.'),([[3,1,3,1,1],8],'One session can hold 3+3+1+1 and the remaining one requires a second session.')],
        [[t,s] for t,s in [([1],1),([1,1],1),([1,1],2),([1,2,3],3),([3,1,3,1,1],8),([5,5,5],5),([2,2,2,2],4),([1,2,3,4],5),([4,4,2,2],6),([7,1,1,1],8),([2,3,3,4],6),([6,5,4,3,2,1],10),([9,8,7],10),([1,1,1,1,1],3)]],
        SESSIONS,[SESSIONS.replace('sessions[position] + duration > session_time','sessions[position] + duration >= session_time'),SESSIONS.replace('best = len(sessions)','best = len(sessions) + 1',1)],
        ['Rejects a session whose tasks exactly fill the available time.','Initializes the upper bound one session too high and can return that value without improvement.'],sessions_oracle,random_sessions,
        lesson('This is bin packing over at most fourteen tasks, allowing exact search with strong pruning.','Place long tasks first; try each distinct current session load and also a new session, abandoning branches no better than the best.','Sort descending; recursively place task i in every fitting unique load or append a session.','Every legal assignment appears in a branch; equal-load symmetry and the incumbent bound remove only equivalent or non-improving branches.'),'O(sessions^n) worst case','O(n)',7),
    1987: entry('number_of_unique_good_subsequences',[('binary','str')],'int',['strings','dynamic programming','subsequences'],
        ['binary has 1 through 100000 zero and one characters.','A good subsequence has no leading zero unless it is exactly "0"; equal resulting strings count once.','Return the number of distinct good nonempty subsequences modulo 1000000007.'],
        [(['001'],'The distinct good subsequences are zero and one, so the answer is two.'),(['11'],'The distinct good subsequences are one and eleven, so the answer is two.')],
        [[s] for s in ['0','1','00','01','10','11','001','101','010','111','000','1001','1010','1100','00101','10101']],
        SUBSEQUENCES,[SUBSEQUENCES.replace('has_zero = 1','has_zero += 1'),SUBSEQUENCES.replace('+ 1) % mod',') % mod')],
        ['Counts each zero occurrence rather than the single distinct subsequence "0".','Never creates the one-character subsequence "1" when a one is read.'],subsequences_oracle,random_binary,
        lesson('Track distinct valid subsequences by their final character rather than storing the strings.','Reading one replaces the set ending in one with every old valid nonzero sequence plus "1"; reading zero similarly appends zero, while standalone zero is tracked once.','Update end1=end0+end1+1 on one, end0=end0+end1 on zero, then add has_zero.','Appending the current digit groups results by their unique prefix and last digit; replacement removes duplicates created by later equal digits.'),'O(n)','O(1)',8),
    1989: entry('maximum_people_caught',[('team','list[int]'),('dist','int')],'int',['arrays','greedy','two pointers'],
        ['team has 1 through 100000 entries: zero denotes an agent and one denotes a person.','Each agent catches at most one person within index distance dist, and each person can be caught once.','Return the maximum number of catches.'],
        [([[0,1,0,1,0],3],'The first two agents can match the two people, so two are caught.'),([[1,1,0,0],0],'No agent shares an index with a person, so distance zero permits no catches.')],
        [[t,d] for t,d in [([0],1),([1],1),([0,1],1),([0,1],0),([0,1,0,1,0],3),([1,1,0,0],0),([1,1,0,0],1),([0,0,1,1],1),([0,0,0,1],3),([1,0,1,0,1],1),([1,1,1,0],10),([0,0,0,1,1,1],2),([1,0,0,0,1],2),([0,1,1,1,0,0],1)]],
        CAUGHT,[CAUGHT.replace('<= dist','< dist'),CAUGHT.replace('agents[left] < people[right]','agents[left] > people[right]')],
        ['Disallows matches at exactly the permitted distance.','Advances the wrong unmatched pointer and can discard a future feasible match.'],caught_oracle,random_caught,
        lesson('After sorting positions, matching the earliest feasible pair leaves the most room for everything later.','Use one pointer for agents and one for people; match when close enough, otherwise discard whichever position is too far left.','If |a-p|<=dist advance both and count; else advance the smaller position.','An unmatched earlier position cannot reach any later opposite position when it already lies too far left, while exchanging a crossing match for the earliest pair never hurts feasibility.'),'O(n)','O(n)',5),
    1991: entry('find_middle_index',[('nums','list[int]')],'int',['arrays','prefix sums'],
        ['nums contains 1 through 100 integers from -1000 through 1000.','At a middle index, the sum strictly left equals the sum strictly right.','Return the leftmost middle index, or -1 if none exists.'],
        [([[2,3,-1,8,4]],'At index three, both sides sum to four.'),([[1,-1,4]],'At index two, the left sum is zero and the empty right side also sums to zero.')],
        [[a] for a in [[0],[1],[-1],[1,2],[1,-1],[2,3,-1,8,4],[1,-1,4],[1,7,3,6,5,6],[1,2,3],[-1,-1,-1],[0,0,0],[2,-2,0],[5,-2,-3,0],[10,0,-10],[3,1,2,1,3]]],
        MIDDLE,[MIDDLE.replace('right -= value','right += value'),MIDDLE.replace('return index','return index + 1')],
        ['Adds the current value to the right total instead of removing it.','Returns a one-based position instead of the required zero-based index.'],middle_oracle,random_middle,
        lesson('Maintain the sum on each side while scanning once.','Begin with the total on the right; remove the current value before comparing, then add it to the left after comparing.','right=sum(nums), left=0; for i,x: right-=x; compare; left+=x.','At comparison time the maintained totals contain exactly the elements strictly before and strictly after the current index; the first equality is therefore the required answer.'),'O(n)','O(1)',3),
    1992: entry('find_farmland_groups',[('land','list[list[int]]')],'list[list[int]]',['matrices','greedy','connected components'],
        ['land is a nonempty binary matrix with at most 300 rows and columns.','Each farmland group is a solid rectangle of ones, and distinct groups do not touch in four directions.','Return [top_row,left_column,bottom_row,right_column] for every group.'],
        [([[[1,0,0],[0,1,1],[0,1,1]]],'There is one single-cell group and one 2-by-2 rectangle.'),([[[1,1],[1,1]]],'All cells form the rectangle from zero,zero through one,one.')],
        [[m] for m in [[[0]],[[1]],[[1,1]],[[1],[1]],[[1,0],[0,1]],[[1,0,0],[0,1,1],[0,1,1]],[[1,1],[1,1]],[[0,0],[0,0]],[[0,1,1],[0,1,1],[0,0,0]],[[1,0,1]],[[1],[0],[1]],[[1,1,0],[1,1,0],[0,0,1]],[[0,1,0],[0,1,0],[0,1,0]],[[1,0,0,1],[0,0,0,1]]]],
        FARMLAND,[FARMLAND.replace('row > 0 and land[row-1][column]','False'),FARMLAND.replace('while right + 1 < columns','while right + 2 < columns')],
        ['Fails to reject cells below an existing group top and emits duplicate rectangles.','Stops horizontal expansion one column early near the right boundary.'],farmland_oracle,random_farmland,
        lesson('Only a rectangle’s top-left cell has no farmland immediately above or left.','Scan row-major; at each top-left, extend down and right to find the opposite corner.','Skip zero or cells with a one above/left; measure the run downward and rightward.','The rectangle guarantee makes these runs its exact bounds, while the top-left predicate selects every group exactly once.'),'O(rows*columns)','O(1)',5),
}
