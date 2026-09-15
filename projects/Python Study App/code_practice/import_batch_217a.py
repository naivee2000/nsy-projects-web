"""Free workdays, starred strings, closest OR, queue champions, and good subsequences."""
from itertools import combinations

from .import_batch_055 import entry


def days_oracle(args):
    days, meetings = args
    occupied = {day for left, right in meetings for day in range(left, right + 1)}
    return days - len(occupied)


def random_days(rng):
    days = rng.randint(1, 40); meetings = []
    for _ in range(rng.randint(0, 12)):
        left = rng.randint(1, days); meetings.append([left, rng.randint(left, days)])
    return [days, meetings]


def stars_oracle(args):
    text = args[0]; kept = []
    for char in text:
        if char != '*':kept.append(char);continue
        smallest = min(kept); index = max(i for i, value in enumerate(kept) if value == smallest);kept.pop(index)
    return ''.join(kept)


def random_stars(rng):
    parts = []; available = 0
    for _ in range(rng.randint(1, 30)):
        if available and rng.random() < .3:parts.append('*');available -= 1
        else:parts.append(rng.choice('abcde'));available += 1
    return [''.join(parts)]


def or_oracle(args):
    nums, target = args; best = 10**30
    for left in range(len(nums)):
        value = 0
        for right in range(left, len(nums)):value |= nums[right];best = min(best, abs(value-target))
    return best


def random_or(rng):
    return [[rng.randint(0, 127) for _ in range(rng.randint(1, 14))],rng.randint(0, 150)]


def winner_oracle(args):
    skills, needed = args; queue = list(range(len(skills))); champion = None; streak = 0
    while True:
        first, second = queue[0], queue[1]
        if skills[first] > skills[second]:winner, loser = first, second
        else:winner, loser = second, first
        queue = [winner] + queue[2:] + [loser]
        if winner == champion:streak += 1
        else:champion, streak = winner, 1
        if streak == needed:return winner


def random_winner(rng):
    skills = list(range(1, rng.randint(2, 10) + 1));rng.shuffle(skills)
    return [skills,rng.randint(1,15)]


def good_oracle(args):
    nums, limit = args; best = 0
    for size in range(1, len(nums)+1):
        for indices in combinations(range(len(nums)),size):
            changes = sum(nums[indices[i]] != nums[indices[i-1]] for i in range(1,size))
            if changes <= limit:best = size
    return best


def random_good(rng):
    return [[rng.randint(1,5) for _ in range(rng.randint(1,10))],rng.randint(0,4)]


DAYS = '''def count_days_without_meetings(days,meetings):
    if not meetings:return days
    meetings=sorted(meetings);covered=0;left,right=meetings[0]
    for start,end in meetings[1:]:
        if start>right+1:covered+=right-left+1;left,right=start,end
        else:right=max(right,end)
    return days-covered-(right-left+1)
'''


STARS = '''def lexicographically_minimum_after_stars(s):
    positions=[[] for _ in range(26)];removed=[False]*len(s)
    for index,char in enumerate(s):
        if char!='*':positions[ord(char)-97].append(index);continue
        removed[index]=True
        for stack in positions:
            if stack:removed[stack.pop()]=True;break
    return ''.join(char for index,char in enumerate(s) if not removed[index])
'''


OR_CLOSEST = '''def closest_subarray_or_difference(nums,k):
    previous=set();answer=10**30
    for number in nums:
        current={number}|{value|number for value in previous}
        answer=min(answer,min(abs(value-k) for value in current));previous=current
    return answer
'''


WINNER = '''def first_consecutive_game_winner(skills,k):
    champion=0;streak=0
    for challenger in range(1,len(skills)):
        if skills[champion]>skills[challenger]:streak+=1
        else:champion=challenger;streak=1
        if streak>=k:return champion
    return champion
'''


GOOD = '''def longest_good_subsequence(nums,k):
    n=len(nums);dp=[[1]*(k+1) for _ in range(n)];answer=1
    for index in range(n):
        for prior in range(index):
            change=nums[prior]!=nums[index]
            for used in range(change,k+1):dp[index][used]=max(dp[index][used],dp[prior][used-change]+1)
        answer=max(answer,max(dp[index]))
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH = {
3169:entry('count_days_without_meetings',[('days','int'),('meetings','list[list[int]]')],'int',['intervals','sorting'],['Days are numbered inclusively from one through days; meetings may be empty.','Each meeting [start,end] occupies every day in that inclusive interval, and meetings may overlap.','Return the number of days not covered by any meeting.'],[([10,[[5,7],[1,3],[9,10]]],'The meetings cover days 1–3, 5–7, and 9–10, leaving days 4 and 8.'),([5,[[1,5],[2,3]]],'The first meeting already covers every workday, so none are free.')],[[d,m] for d,m in [(1,[]),(1,[[1,1]]),(10,[[5,7],[1,3],[9,10]]),(5,[[1,5],[2,3]]),(7,[[2,2]]),(10,[[1,2],[3,4]]),(10,[[1,3],[3,5]]),(20,[[2,8],[6,12],[15,18]]),(6,[[1,1],[6,6]]),(8,[[2,4],[2,4]]),(100,[[20,30],[1,10],[40,100]]),(4,[]),(9,[[3,7],[1,2]]),(12,[[5,5],[7,9],[6,6]])]],DAYS,[DAYS.replace('start>right+1','start>=right'),DAYS.replace('right-left+1','right-left')],['Treats intervals sharing an endpoint as disjoint and counts that shared day twice.','Counts inclusive meeting intervals as half-open and undercounts occupied endpoints.'],days_oracle,random_days,lesson('Only the union of meeting intervals matters; overlapping days must be counted once.','Sort intervals and merge each overlap or adjacency into the current covered block.','Accumulate inclusive lengths of finished merged blocks; subtract total covered from days.','The sorted scan partitions the union into disjoint maximal intervals whose lengths sum to exactly the occupied-day count.'),'O(m log m)','O(m)',5),
3170:entry('lexicographically_minimum_after_stars',[('s','str')],'str',['greedy','stacks','strings'],['s contains lowercase letters and stars, and every star has at least one surviving letter to its left.','Process stars from left to right; each removes itself and one smallest surviving letter to its left.','When that smallest letter occurs multiple times, remove its rightmost occurrence to obtain the lexicographically smallest final string.'],[(['aaba*'],'The smallest eligible letter is a; deleting its rightmost occurrence leaves aab.'),(['abc*de*'],'The first star removes a, then the second removes b, leaving cde.')],[[s] for s in ['a*','aaba*','abc*de*','ba*','cb*a*','abc***','aaaa**','dcba*','azby*x*','baca**','leetcode****','z*y*x*','abcc*b*','qwerty***']],STARS,[STARS.replace('stack.pop()','stack.pop(0)'),STARS.replace('for stack in positions','for stack in reversed(positions)')],['Removes the leftmost copy of the smallest letter, leaving a lexicographically larger prefix.','Removes the largest available letter rather than the smallest.'],stars_oracle,random_stars,lesson('The letter value must be smallest; among equal candidates, preserving the earlier copy makes the remaining string lexicographically smaller.','Keep one stack of indices per letter and mark the rightmost index from the first nonempty letter stack.','Scan s; push letter indices; at star scan a..z, pop one index, and mark both positions removed.','The exchange rule chooses the optimal deletion at every forced star without affecting which letter values remain eligible later.'),'O(26n)','O(n)',5),
3171:entry('closest_subarray_or_difference',[('nums','list[int]'),('k','int')],'int',['bit manipulation','dynamic programming','subarrays'],['nums is a nonempty array of nonnegative integers and k is nonnegative.','Choose one nonempty contiguous subarray and compute the bitwise OR of all its values.','Return the minimum absolute difference between such an OR and k.'],[([[1,2,4,5],3],'The subarray [1,2] has bitwise OR three, so the minimum difference is zero.'),([[8,1,2],6],'Possible useful OR values include 8, 1, 2, and 3; value eight is closest with difference two.')],[[n,k] for n,k in [([1],0),([1],1),([1,2,4,5],3),([8,1,2],6),([0],5),([0,0],0),([7,7],4),([1,1,1],2),([2,4,8],7),([15,1],8),([3,5,6],4),([16,8,4,2,1],31),([5,10,5],12),([64,1,32,2],35)]],OR_CLOSEST,[OR_CLOSEST.replace('previous=current','previous={number}'),OR_CLOSEST.replace('value|number','value&number')],['Forgets subarrays longer than one after every step.','Computes bitwise AND values rather than bitwise OR values.'],or_oracle,random_or,lesson('For a fixed right endpoint, extending every prior subarray produces all ending OR values, and equal results may be deduplicated.','Carry the distinct OR set from the previous endpoint and OR every value with the new number.','current={number} union {old|number}; minimize abs(current-k); replace previous.','The recurrence represents every nonempty subarray by its unique left endpoint, while deduplication is safe because future OR extensions depend only on the current value.'),'O(n*word_bits)','O(word_bits)',8),
3175:entry('first_consecutive_game_winner',[('skills','list[int]'),('k','int')],'int',['arrays','simulation'],['skills contains at least two distinct skill values and k is positive.','The first two queued players compete; the stronger remains first and the loser moves to the back.','Return the original zero-based index of the first player to win k consecutive games.'],[([[4,2,6,3,9],2],'Player zero wins once, then original player two defeats players zero and three consecutively and wins.'),([[2,5,1],10],'The maximum-skill player at index one eventually stays in front forever and reaches any large streak.')],[[s,k] for s,k in [([4,2,6,3,9],2),([2,5,1],10),([2,1],1),([1,2],1),([3,1,2],2),([1,3,2],2),([5,4,3,2,1],4),([1,2,3,4,5],3),([10,1,9,2],2),([7,3,8,6],1),([4,9,1,2,3],5),([6,5,7],2),([2,8,4,10,6],3),([100,10,20],20)]],WINNER,[WINNER.replace('streak=1','streak=0'),WINNER.replace('return champion\n','return 0\n')],['Resets a new champion’s first victory to zero instead of one.','After the initial scan always returns player zero, even though the maximum champion remains in front.'],winner_oracle,random_winner,lesson('Once a player loses, they cannot matter before the current champion faces every later player; the global maximum never loses.','Scan challengers in original order while tracking the front champion and its current consecutive wins.','Champion win increments streak; challenger win replaces champion with streak one; return on k or final champion.','This scan matches the actual sequence until the maximum reaches the front, after which it wins forever, so no explicit queue rotation is needed.'),'O(n)','O(1)',5),
3176:entry('longest_good_subsequence',[('nums','list[int]'),('k','int')],'int',['dynamic programming','subsequences'],['nums is nonempty and k is nonnegative.','Choose a subsequence in original index order; count adjacent chosen pairs whose values differ.','Return the maximum subsequence length whose differing-adjacency count is at most k.'],[([[1,2,1,1,3],2],'One length-four choice is 1,2,1,1, using two value changes.'),([[1,1,1],0],'All three equal values form a valid subsequence with zero changes.')],[[n,k] for n,k in [([1],0),([1,2,1,1,3],2),([1,1,1],0),([1,2,3],0),([1,2,3],2),([1,2,1,2],1),([3,3,2,2,1],1),([1,2,1,3,1],0),([5,4,3,2,1],3),([1,1,2,2,3,3],2),([2,1,2,1,2],2),([7,7,8,7,8,8],1),([1,2,3,1,2,3],2),([4,1,4,2,4,3],1)]],GOOD,[GOOD.replace('change=nums[prior]!=nums[index]','change=1'),GOOD.replace('range(change,k+1)','range(change,k)')],['Charges a change even when consecutive chosen values are equal.','Never fills DP states using exactly k changes.'],good_oracle,random_good,lesson('A subsequence ending at index i is determined for extension by its last value and number of changes used.','Use DP over ending index and change budget, extending every earlier endpoint.','dp[i][c]=max(dp[j][c-different]+1); initialize singleton states to one.','Every subsequence has a penultimate chosen index j, so the recurrence enumerates all and records the best length for each exact-or-at-most budget.'),'O(n²k)','O(nk)',5),
}
