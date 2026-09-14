"""Second slice of workbook batch 122."""

from collections import Counter
from functools import lru_cache

from .import_batch_055 import entry


def anagram_oracle(args):
    first, second = args
    alphabet = set(first + second)
    return sum(abs(first.count(char) - second.count(char)) for char in alphabet)


def random_anagram(rng):
    return [
        "".join(rng.choice("abcdef") for _ in range(rng.randint(1, 25))),
        "".join(rng.choice("abcdef") for _ in range(rng.randint(1, 25))),
    ]


def trips_oracle(args):
    times, total = args
    elapsed = 0
    while sum(elapsed // duration for duration in times) < total:
        elapsed += 1
    return elapsed


def random_trips(rng):
    return [[rng.randint(1, 15) for _ in range(rng.randint(1, 8))], rng.randint(1, 100)]


def race_oracle(args):
    tires, change, laps = args

    @lru_cache(None)
    def search(done, tire, streak):
        if done == laps:
            return 0
        best = float("inf")
        if tire >= 0:
            first, ratio = tires[tire]
            best = first * ratio**streak + search(done + 1, tire, streak + 1)
        for next_tire, (first, _) in enumerate(tires):
            best = min(best, (change if done else 0) + first + search(done + 1, next_tire, 1))
        return best

    return search(0, -1, 0)


def random_race(rng):
    tires = [[rng.randint(1, 8), rng.randint(2, 5)] for _ in range(rng.randint(1, 4))]
    return [tires, rng.randint(1, 10), rng.randint(1, 7)]


def cards_oracle(args):
    n = args[0]
    pieces = list(range(2, n + 1, 3))

    @lru_cache(None)
    def search(index, remaining):
        if remaining == 0:
            return 1
        if index == len(pieces) or remaining < 0:
            return 0
        return search(index + 1, remaining) + search(index + 1, remaining - pieces[index])

    return search(0, n)


def random_cards(rng):
    return [rng.randint(1, 80)]


def follower_oracle(args):
    nums, key = args
    counts = Counter(nums[index + 1] for index in range(len(nums) - 1) if nums[index] == key)
    return max(counts, key=counts.get)


def random_follower(rng):
    key = rng.randint(1, 5)
    winner = rng.randint(6, 9)
    nums = []
    for _ in range(rng.randint(1, 8)):
        nums.extend([key, winner])
        if rng.randrange(2):
            nums.append(rng.randint(1, 9))
    return [nums, key]


ANAGRAM = '''\
def minimum_append_steps_for_anagrams(s,t):
    from collections import Counter
    first,second=Counter(s),Counter(t)
    return sum(abs(first[char]-second[char]) for char in first.keys()|second.keys())
'''

TRIPS = '''\
def minimum_time_for_trips(time,total_trips):
    low,high=1,min(time)*total_trips
    while low<high:
        middle=(low+high)//2
        if sum(middle//duration for duration in time)>=total_trips:high=middle
        else:low=middle+1
    return low
'''

RACE = '''\
def minimum_race_finish_time(tires,change_time,num_laps):
    best=[float('inf')]*(num_laps+1)
    for first,ratio in tires:
        lap=first;total=0
        for length in range(1,num_laps+1):
            total+=lap;best[length]=min(best[length],total)
            lap*=ratio
            if lap>first+change_time:break
    dp=[float('inf')]*(num_laps+1);dp[0]=-change_time
    for laps in range(1,num_laps+1):
        for length in range(1,laps+1):
            if best[length]<float('inf'):
                dp[laps]=min(dp[laps],dp[laps-length]+change_time+best[length])
    return dp[num_laps]
'''

CARDS = '''\
def count_card_houses(n):
    ways=[0]*(n+1);ways[0]=1
    for row_cards in range(2,n+1,3):
        for total in range(n,row_cards-1,-1):
            ways[total]+=ways[total-row_cards]
    return ways[n]
'''

FOLLOWER = '''\
def most_frequent_value_after_key(nums,key):
    from collections import Counter
    counts=Counter(nums[index+1] for index in range(len(nums)-1) if nums[index]==key)
    return max(counts,key=counts.get)
'''


BATCH = {
    2186: entry('minimum_append_steps_for_anagrams',[('s','str'),('t','str')],'int',['strings','counting','hash maps'],['One step appends one lowercase letter to either string.','After all steps, the two strings must have identical character counts.','Return the minimum number of appended characters.'],[(['leetcode','coats'],'The total absolute difference across character counts is seven, so seven appends are necessary.'),(['night','thing'],'The strings already contain the same letters with the same counts, so return zero.')],[[a,b] for a,b in [('a','a'),('a','b'),('aa','a'),('abc','cde'),('leetcode','coats'),('night','thing'),('x','xxxx'),('abb','baa'),('hello','world'),('aaaa','bbbb'),('abcabc','aabbcc'),('zxy','xyz'),('paper','title'),('same','same')]],ANAGRAM,[ANAGRAM.replace('abs(first[char]-second[char])','first[char]-second[char]'),ANAGRAM.replace('first.keys()|second.keys()','first.keys()&second.keys()')],['Allows surplus letters in the second string to cancel deficits instead of counting both directions.','Ignores letters appearing in only one string.'],anagram_oracle,random_anagram,['Each character can be balanced independently because appending never removes an existing count.','For each letter, append exactly the absolute difference between its two counts.','Build two counters and sum abs(count_s-count_t) across their key union.','Every imbalance requires that many additions to the deficient side, and performing those additions makes the count vectors equal.'],'O(len(s)+len(t))','O(alphabet)',5),
    2187: entry('minimum_time_for_trips',[('time','list[int]'),('total_trips','int')],'int',['arrays','binary search'],['A bus with duration d completes floor(T/d) trips by time T.','All buses run independently and may start another trip immediately.','Return the smallest integer time at which at least total_trips are complete.'],[([[1,2,3],5],'At time three the buses complete 3+1+1=5 trips; time two completes only four.'),([[2],1],'The only bus completes its first trip at time two.')],[[a,t] for a,t in [([1],1),([2],1),([1],10),([1,2,3],5),([2,3],1),([5,10,10],9),([3,3,3],7),([7,2,5],20),([10],100),([4,6,8],12),([1,100],50),([9,3,6],25),([2,2],3),([11,13,17],30)]],TRIPS,[TRIPS.replace('>=total_trips','>total_trips'),TRIPS.replace('if sum(middle//duration for duration in time)>=total_trips:high=middle','if sum(middle//duration for duration in time)>=total_trips:low=middle+1')],['Requires strictly more than the requested trips and can return a time that is too large.','Moves the lower bound upward on a feasible midpoint, converging to the upper bound.'],trips_oracle,random_trips,['Trip count is monotone in elapsed time, enabling a lower-bound search.','Search between one and the fastest bus completing every requested trip alone.','At midpoint sum midpoint//duration; keep the feasible half including midpoint, otherwise move low to midpoint+1.','The invariant keeps the first feasible time in [low,high], and convergence returns that smallest time.'],'O(n log(min(time)*total_trips))','O(1)',6),
    2188: entry('minimum_race_finish_time',[('tires','list[list[int]]'),('change_time','int'),('num_laps','int')],'int',['arrays','dynamic programming'],['A tire [first,ratio] takes first*ratio^(x-1) seconds on its x-th consecutive lap.','Changing before a lap costs change_time; choosing the initial tire is free.','Return the minimum time for exactly num_laps laps, and a change may select any tire including the same type.'],[([[[2,3],[3,4]],5,4],'Combining short tire stints with one change completes four laps in 21 seconds.'),([[[1,10],[2,2],[3,4]],6,5],'The best sequence of tire stints completes five laps in 25 seconds.')],[[t,c,n] for t,c,n in [([[2,3]],5,1),([[2,3]],5,2),([[2,3]],5,4),([[2,3],[3,4]],5,4),([[1,10],[2,2],[3,4]],6,5),([[1,2]],1,6),([[5,2],[2,5]],4,3),([[3,3],[4,2]],2,5),([[2,2],[2,3]],10,6),([[7,2]],3,5),([[1,5],[4,2]],8,7),([[6,2],[3,3],[2,4]],5,4),([[2,10],[9,2]],1,3),([[4,2],[5,2]],20,6)]],RACE,[RACE.replace('dp[0]=-change_time','dp[0]=0'),RACE.replace('if lap>first+change_time:break','if lap>first:break')],['Charges an unnecessary tire-change cost before the first stint.','Stops precomputing a stint as soon as lap time grows at all, missing useful consecutive laps.'],race_oracle,random_race,['Long consecutive tire runs become worse than changing once their next lap exceeds a fresh first lap plus change cost.','Precompute the best same-tire time for each useful stint length, then partition the race into stints.','Set dp[0]=-change_time; append a stint with one change plus its precomputed time; minimize over stint lengths.','Every race strategy is a partition into consecutive same-tire stints, and each stint uses its best tire; the negative initial change cancels the charge before the first stint.'],'O(tires*useful_laps+num_laps^2)','O(num_laps)',8),
    2189: entry('count_card_houses',[('n','int')],'int',['math','dynamic programming','partitions'],['A row with k adjacent triangles uses 3*k-1 cards.','Higher rows must contain fewer triangles, so each allowable row size 2,5,8,... may be used at most once.','Count distinct sets of row card counts totaling exactly n.'],[([16],'The distinct row-card sets {2,14} and {5,11} both total sixteen, giving two houses.'),([2],'One two-card triangle forms the only possible house.')],[[x] for x in [1,2,3,4,5,7,8,10,11,13,14,16,20,25,30]],CARDS,[CARDS.replace('range(n,row_cards-1,-1)','range(row_cards,n+1)'),CARDS.replace('ways[0]=1','ways[0]=0')],['Updates totals upward and reuses the same row size multiple times.','Removes the empty construction base case, so no house can be formed.'],cards_oracle,random_cards,['Each possible row consumes a distinct card count congruent to two modulo three.','This is a subset-sum count using each row size at most once.','Initialize ways[0]=1; for row_cards=2,5,8,... update totals downward; return ways[n].','Downward updates prevent reusing a row size, and every selected subset corresponds uniquely to strictly decreasing triangle counts across house rows.'],'O(n^2)','O(n)',6),
    2190: entry('most_frequent_value_after_key',[('nums','list[int]'),('key','int')],'int',['arrays','counting','hash maps'],['Inspect indices i only through len(nums)-2 where nums[i] equals key.','Count the immediately following value nums[i+1].','The input guarantees one target has a unique highest count; return that target.'],[([[1,100,200,1,100],1],'Value 100 follows key 1 twice and is the unique most frequent target.'),([[2,2,2,2,3],2],'Two follows the key three times while three follows it once, so return two.')],[[a,k] for a,k in [([1,2],1),([1,2,1,2],1),([1,100,200,1,100],1),([2,2,2,2,3],2),([3,1,3,2,3,1],3),([5,6,7,5,6],5),([9,8,9,7,9,8,9,8],9),([1,1],1),([4,3,4,3,4,2],4),([0,1,0,1,0,2],0),([7,7,8,7,7],7),([2,3,4,2,3,2,3],2),([10,20,10,30,10,20],10),([6,5,6,5,6,4],6)]],FOLLOWER,[FOLLOWER.replace('nums[index+1] for index','key for index'),FOLLOWER.replace('if nums[index]==key','if nums[index+1]==key')],['Counts the key itself for each occurrence instead of counting the immediately following value.','Selects positions whose following value is key, reversing the relationship.'],follower_oracle,random_follower,['Only adjacent pairs beginning with key contribute.','Scan every index that has a successor and count that successor when the current value is key.','Build a Counter from nums[i+1] for matching i, then return the key with maximum count.','The comprehension represents exactly every required occurrence, and the guaranteed unique maximum removes tie ambiguity.'],'O(n)','O(distinct followers)',3),
}
