"""Sliding-window, scheduling, bitmask-DP, segment-tree, and prefix imports."""
from itertools import permutations

from .import_batch_055 import entry


def robots_oracle(args):
    charge_times, running_costs, budget = args
    best = 0
    for left in range(len(charge_times)):
        running = 0
        charge = 0
        for right in range(left, len(charge_times)):
            running += running_costs[right]
            charge = max(charge, charge_times[right])
            size = right - left + 1
            if charge + size * running <= budget:
                best = max(best, size)
    return best


def random_robots(rng):
    size = rng.randint(1, 10)
    return [
        [rng.randint(1, 30) for _ in range(size)],
        [rng.randint(1, 15) for _ in range(size)],
        rng.randint(1, 500),
    ]


def meetings_oracle(args):
    room_count, meetings = args
    free_at = [0] * room_count
    counts = [0] * room_count
    for start, end in sorted(meetings):
        available = [room for room in range(room_count) if free_at[room] <= start]
        if available:
            room = available[0]
            actual_start = start
        else:
            room = min(range(room_count), key=lambda value: (free_at[value], value))
            actual_start = free_at[room]
        free_at[room] = actual_start + end - start
        counts[room] += 1
    return min(range(room_count), key=lambda room: (-counts[room], room))


def random_meetings(rng):
    room_count = rng.randint(1, 4)
    count = rng.randint(1, 9)
    starts = rng.sample(range(25), count)
    meetings = [[start, start + rng.randint(1, 10)] for start in starts]
    rng.shuffle(meetings)
    return [room_count, meetings]


def monsters_oracle(args):
    power = args[0]
    return min(
        sum((value + gain - 1) // gain for gain, value in enumerate(order, 1))
        for order in permutations(power)
    )


def random_monsters(rng):
    return [[rng.randint(1, 40) for _ in range(rng.randint(1, 7))]]


def limited_lis_oracle(args):
    nums, limit = args
    lengths = [1] * len(nums)
    for right in range(len(nums)):
        for left in range(right):
            if nums[left] < nums[right] and nums[right] - nums[left] <= limit:
                lengths[right] = max(lengths[right], lengths[left] + 1)
    return max(lengths)


def random_limited_lis(rng):
    return [[rng.randint(1, 25) for _ in range(rng.randint(1, 24))], rng.randint(1, 12)]


def prefix_scores_oracle(args):
    words = args[0]
    return [
        sum(sum(other.startswith(word[:length]) for other in words) for length in range(1, len(word) + 1))
        for word in words
    ]


def random_prefix_scores(rng):
    words = []
    for _ in range(rng.randint(1, 10)):
        words.append("".join(rng.choice("abc") for _ in range(rng.randint(1, 7))))
    return [words]


ROBOTS = '''def maximum_robots_within_budget(charge_times,running_costs,budget):
    from collections import deque
    maxima=deque();running=0;left=0;best=0
    for right,charge in enumerate(charge_times):
        running+=running_costs[right]
        while maxima and charge_times[maxima[-1]]<=charge:maxima.pop()
        maxima.append(right)
        while maxima and charge_times[maxima[0]]+(right-left+1)*running>budget:
            if maxima[0]==left:maxima.popleft()
            running-=running_costs[left];left+=1
        best=max(best,right-left+1)
    return best
'''


MEETINGS = '''def most_booked_room(n,meetings):
    import heapq
    idle=list(range(n));heapq.heapify(idle);busy=[];counts=[0]*n
    for start,end in sorted(meetings):
        while busy and busy[0][0]<=start:
            _,room=heapq.heappop(busy);heapq.heappush(idle,room)
        if idle:
            room=heapq.heappop(idle);finish=end
        else:
            available,room=heapq.heappop(busy);finish=available+end-start
        heapq.heappush(busy,(finish,room));counts[room]+=1
    return min(range(n),key=lambda room:(-counts[room],room))
'''


MONSTERS = '''def minimum_monster_days(power):
    from functools import lru_cache
    size=len(power)
    @lru_cache(None)
    def visit(mask):
        if mask==(1<<size)-1:return 0
        gain=mask.bit_count()+1;best=float('inf')
        for index,value in enumerate(power):
            if not mask>>index&1:
                best=min(best,(value+gain-1)//gain+visit(mask|1<<index))
        return best
    return visit(0)
'''


LIMITED_LIS = '''def longest_limited_increasing_subsequence(nums,k):
    import bisect
    values=sorted(set(nums));size=1
    while size<len(values):size*=2
    tree=[0]*(2*size)
    def query(left,right):
        left+=size;right+=size;best=0
        while left<right:
            if left&1:best=max(best,tree[left]);left+=1
            if right&1:right-=1;best=max(best,tree[right])
            left//=2;right//=2
        return best
    def update(index,value):
        index+=size;tree[index]=max(tree[index],value);index//=2
        while index:
            tree[index]=max(tree[2*index],tree[2*index+1]);index//=2
    answer=1
    for value in nums:
        left=bisect.bisect_left(values,value-k);position=bisect.bisect_left(values,value)
        length=query(left,position)+1;update(position,length);answer=max(answer,length)
    return answer
'''


PREFIX_SCORES = '''def sum_prefix_scores(words):
    root=[0,{}]
    for word in words:
        node=root
        for char in word:
            node=node[1].setdefault(char,[0,{}]);node[0]+=1
    answer=[]
    for word in words:
        node=root;score=0
        for char in word:
            node=node[1][char];score+=node[0]
        answer.append(score)
    return answer
'''

PREFIX_COMPLETE_ONLY = '''def sum_prefix_scores(words):
    counts={word:words.count(word) for word in words}
    return [len(word)*counts[word] for word in words]
'''


def lesson(concept, strategy, pseudocode, editorial):
    return [concept, strategy, pseudocode, editorial]


BATCH = {
    2398: entry(
        'maximum_robots_within_budget', [('charge_times', 'list[int]'), ('running_costs', 'list[int]'), ('budget', 'int')], 'int',
        ['sliding window', 'monotonic queues', 'arrays'],
        ['Both cost arrays have equal length from 1 through 50000.', 'A consecutive window of k robots costs max(charge_times)+k*sum(running_costs).', 'Return the greatest affordable window length; return zero when even one robot exceeds budget.'],
        [([[3,6,1,3,4], [2,1,3,4,5], 25], 'The first three robots cost 6+3*(2+1+3)=24, while no length-four window fits.'), ([[11,12,19], [10,8,7], 19], 'Every individual charge plus running cost exceeds nineteen, so the answer is zero.')],
        [[c,r,b] for c,r,b in [([1],[1],2),([2],[3],4),([2],[3],5),([5,1],[1,1],8),([5,1],[1,1],9),([1,2,3],[1,1,1],12),([10,1,1],[1,1,1],15),([4,4,4],[2,2,2],20),([9,2,8,1],[3,1,2,1],30),([1,10,1,10],[1,1,1,1],25),([6,2,4,7,1],[2,5,1,3,2],40),([100,1],[1,1],99),([3,1,5],[10,1,1],32),([2,8,2,8,2],[1,2,1,2,1],36)]],
        ROBOTS,
        [ROBOTS.replace('(right-left+1)*running', 'running'), ROBOTS.replace('charge_times[maxima[0]]+', 'charge_times[right]+')],
        ['Omits the window-size multiplier from the running cost.', 'Uses the newest robot charge instead of the maximum charge in the window.'],
        robots_oracle, random_robots,
        lesson('Affordability is monotone when the left boundary moves right.', 'Maintain the running-cost sum and a decreasing deque of charge-time indices for the current window maximum.', 'Extend right, shrink left while max_charge+length*running_sum exceeds budget, and record the largest valid length.', 'Every window considered by the two pointers has an exact O(1) cost query; once a window is too expensive, extending it cannot restore affordability, so discarding its left endpoint is safe.'),
        'O(n)', 'O(n)', 8,
    ),
    2402: entry(
        'most_booked_room', [('n', 'int'), ('meetings', 'list[list[int]]')], 'int',
        ['heaps', 'sorting', 'simulation'],
        ['Rooms are numbered 0 through room_count-1 and meeting start times are unique.', 'Use the lowest-numbered idle room; if none is idle, delay the meeting to the earliest room while preserving its duration.', 'Return the room with the most meetings, breaking count ties by the lowest room number.'],
        [([2, [[0,10],[1,5],[2,7],[3,4]]], 'Both rooms host two meetings after delays, so the lower room number zero wins the tie.'), ([3, [[1,20],[2,10],[3,5],[4,9],[6,8]]], 'Rooms one and two each host two meetings, and room one is the smaller tied index.')],
        [[n,m] for n,m in [(1,[[0,1]]),(1,[[0,5],[1,2],[2,3]]),(2,[[0,1]]),(2,[[0,5],[5,6]]),(2,[[0,5],[1,2],[2,3]]),(3,[[0,4],[1,5],[2,6]]),(3,[[0,10],[1,3],[2,4],[3,5]]),(2,[[5,8],[0,2],[3,4]]),(4,[[0,8],[1,2],[2,3],[3,4],[4,5]]),(2,[[0,2],[1,10],[2,3],[3,4]]),(3,[[0,2],[1,3],[2,4],[3,10],[4,5]]),(2,[[0,10],[2,3],[4,5],[6,7]]),(3,[[10,20],[0,5],[6,9],[2,4]]),(2,[[0,4],[1,5],[2,7],[6,8],[7,9]])]],
        MEETINGS,
        [MEETINGS.replace('finish=available+end-start', 'finish=end'), MEETINGS.replace('key=lambda room:(-counts[room],room)', 'key=lambda room:(-counts[room],-room)')],
        ['Ends delayed meetings at their original end time instead of preserving duration.', 'Breaks a most-used-room tie in favor of the larger room number.'],
        meetings_oracle, random_meetings,
        lesson('Scheduling needs one ordering for free times and another for idle room numbers.', 'Keep idle room numbers and busy (finish,room) pairs in separate min-heaps.', 'Release rooms by start time, assign the smallest idle room or delay onto the earliest busy room, then increment that room count.', 'Heap ordering enforces every tie rule directly; processing unique starts in sorted order also preserves the required priority among delayed meetings.'),
        'O(m log m+m log n)', 'O(n+m)', 8,
    ),
    2403: entry(
        'minimum_monster_days', [('power', 'list[int]')], 'int',
        ['dynamic programming', 'bitmasks', 'permutations'],
        ['power contains 1 through 17 positive monster strengths.', 'Gain starts at one, increases after each defeated monster, and accumulated mana resets to zero after a defeat.', 'Return the minimum total days needed to defeat every monster.'],
        [([[3,1,4]], 'Defeat strengths one, four, and three at gains one, two, and three for 1+2+1=4 days.'), ([[1,2,4,9]], 'An optimal order needs six total days as the gain rises from one through four.')],
        [[[p for p in values]] for values in [[1],[2],[10],[1,1],[2,3],[4,1],[3,1,4],[1,1,4],[5,5,5],[2,7,3],[9,1,8,2],[1,2,3,5],[10,20,30],[6,2,9,3,12]]],
        MONSTERS,
        [MONSTERS.replace('(value+gain-1)//gain', 'value//gain'), MONSTERS.replace('gain=mask.bit_count()+1', 'gain=mask.bit_count()+2')],
        ['Rounds required days down when a power is not divisible by gain.', 'Starts with gain two instead of one.'],
        monsters_oracle, random_monsters,
        lesson('Only the set of defeated monsters determines the current gain.', 'Use a bitmask state and try every remaining monster as the next defeat.', 'For each mask, add ceil(power/gain) days for one remaining monster and memoize the cheapest continuation.', 'The recurrence considers every possible defeat order while merging orders with the same defeated set; optimal substructure makes the minimum continuation exact.'),
        'O(n*2^n)', 'O(2^n)', 8,
    ),
    2407: entry(
        'longest_limited_increasing_subsequence', [('nums', 'list[int]'), ('k', 'int')], 'int',
        ['segment trees', 'dynamic programming', 'binary search'],
        ['nums is nonempty and contains positive integers; k is positive.', 'The subsequence preserves input order, increases strictly, and each adjacent difference is at most k.', 'Return its maximum possible length.'],
        [([[4,2,1,4,3,4,5,8,15], 3], 'One longest valid subsequence is [1,3,4,5,8], whose length is five.'), ([[1,5], 1], 'The jump from one to five exceeds k, so either single element is optimal.')],
        [[n,k] for n,k in [([1],1),([1,1],1),([1,2],1),([1,3],1),([3,2,1],5),([1,2,3,4],1),([1,3,5,7],2),([1,4,2,5,3,6],3),([5,1,2,10,3],2),([2,2,2,3],1),([10,1,9,2,8,3],10),([1,10,2,11,3,12],2),([7,4,5,1,8,12,4,7],5),([3,6,4,7,5,8,20],3)]],
        LIMITED_LIS,
        [LIMITED_LIS.replace('left=bisect.bisect_left(values,value-k)', 'left=0'), LIMITED_LIS.replace('query(left,position)', 'query(left,bisect.bisect_right(values,value))')],
        ['Ignores the maximum allowed adjacent difference and computes ordinary LIS.', 'Includes equal values in the predecessor range, violating strict increase.'],
        limited_lis_oracle, random_limited_lis,
        lesson('For a new value v, only earlier sequence endings in [v-k,v-1] may precede it.', 'Store the best length by ending value in a range-maximum segment tree over compressed values.', 'Query the valid predecessor interval, add one, and point-update v without lowering an existing best.', 'The DP recurrence is exact, and the segment tree replaces its linear predecessor scan with logarithmic range queries while input-order processing preserves subsequence order.'),
        'O(n log n)', 'O(n)', 8,
    ),
    2416: entry(
        'sum_prefix_scores', [('words', 'list[str]')], 'list[int]',
        ['tries', 'strings', 'counting'],
        ['words contains 1 through 1000 nonempty lowercase strings.', 'A prefix score is the number of input words beginning with that nonempty prefix, including the word itself.', 'Return one sum in input order for all nonempty prefixes of each word.'],
        [([["abc","ab","bc","b"]], 'For abc the prefix counts are 2,2,1; analogous sums produce [5,4,3,2].'), ([["abcd"]], 'Its four prefixes each occur once, so its score sum is four.')],
        [[[w for w in words]] for words in [['a'],['a','a'],['a','ab'],['ab','a'],['abc','abd'],['a','ab','abc'],['b','ba','bb'],['aa','aaa','aaaa'],['cat','car','dog'],['x','xy','xyz','xz'],['abc','abc','ab'],['z','za','zb','zc'],['apple','app','ape'],['aaa','aab','aba','baa']]],
        PREFIX_SCORES,
        [PREFIX_COMPLETE_ONLY, PREFIX_SCORES.replace('for char in word:\n            node=node[1][char];score+=node[0]', 'for char in word[:-1]:\n            node=node[1][char];score+=node[0]')],
        ['Counts only complete-word duplicates instead of all shared prefixes.', 'Omits each word’s full-length prefix from its score.'],
        prefix_scores_oracle, random_prefix_scores,
        lesson('Every trie node can count how many words share the prefix ending there.', 'Insert all words while incrementing each traversed node, then traverse each word again and add those counts.', 'Build prefix counts once; for each word, follow its characters and accumulate the visited counts.', 'Each word contributes once to exactly the nodes representing its prefixes, so every stored count equals that prefix’s score and summing the path gives the required answer.'),
        'O(total characters)', 'O(total characters)', 8,
    ),
}
