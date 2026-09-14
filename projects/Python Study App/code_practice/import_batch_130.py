"""First slice of workbook batch 130."""

from bisect import bisect_right

from .import_batch_055 import entry


def training_oracle(args):
    initial_energy, initial_experience, energy, experience = args
    extra = max(0, sum(energy) + 1 - initial_energy); current = initial_experience
    for rival in experience:
        if current <= rival:
            needed = rival + 1 - current; extra += needed; current += needed
        current += rival
    return extra


def random_training(rng):
    n = rng.randint(1, 12)
    return [rng.randint(1, 20), rng.randint(1, 20), [rng.randint(1, 12) for _ in range(n)], [rng.randint(1, 20) for _ in range(n)]]


def limited_oracle(args):
    nums, queries = args; ordered = sorted(nums); result = []
    for limit in queries:
        total = count = 0
        for value in ordered:
            if total + value > limit: break
            total += value; count += 1
        result.append(count)
    return result


def random_limited(rng):
    return [[rng.randint(1, 30) for _ in range(rng.randint(1, 15))], [rng.randint(0, 150) for _ in range(rng.randint(1, 12))]]


def stars_oracle(args):
    text = list(args[0])
    while '*' in text:
        index = text.index('*'); del text[index]; del text[index - 1]
    return ''.join(text)


def random_stars(rng):
    output = []
    for _ in range(rng.randint(1, 25)):
        if output and rng.random() < .35: output.append('*')
        else: output.append(rng.choice('abcxyz'))
    # Repair prefix balance so each star always has a removable character.
    balance = 0; fixed = []
    for char in output:
        if char == '*' and balance == 0: char = 'a'
        fixed.append(char); balance += -1 if char == '*' else 1
    return [''.join(fixed)]


def increasing_oracle(args):
    nums = args[0]
    return sum(all(nums[index] < nums[index + 1] for index in range(left, right))
               for left in range(len(nums)) for right in range(left, len(nums)))


def random_increasing(rng):
    return [[rng.randint(-10, 10) for _ in range(rng.randint(1, 20))]]


def equal_sum_oracle(args):
    nums = args[0]
    sums = [nums[index] + nums[index + 1] for index in range(len(nums) - 1)]
    return len(sums) != len(set(sums))


def random_equal_sum(rng):
    return [[rng.randint(-10, 10) for _ in range(rng.randint(2, 20))]]


TRAIN='''\
def minimum_training_hours(initialEnergy,initialExperience,energy,experience):
    training=max(0,sum(energy)+1-initialEnergy);current=initialExperience
    for rival in experience:
        if current<=rival:training+=rival+1-current;current=rival+1
        current+=rival
    return training
'''

LIMIT='''\
def longest_subsequence_under_queries(nums,queries):
    ordered=sorted(nums);prefix=[];total=0
    for value in ordered:total+=value;prefix.append(total)
    return [__import__('bisect').bisect_right(prefix,limit) for limit in queries]
'''

STARS='''\
def remove_stars_from_string(s):
    kept=[]
    for char in s:
        if char=='*':kept.pop()
        else:kept.append(char)
    return ''.join(kept)
'''

INCREASING='''\
def count_strictly_increasing_subarrays(nums):
    run=answer=0;previous=None
    for value in nums:
        run=run+1 if previous is None or previous<value else 1
        answer+=run;previous=value
    return answer
'''

EQUALSUM='''\
def has_equal_adjacent_pair_sums(nums):
    seen=set()
    for index in range(len(nums)-1):
        total=nums[index]+nums[index+1]
        if total in seen:return True
        seen.add(total)
    return False
'''


BATCH={
2383:entry('minimum_training_hours',[('initialEnergy','int'),('initialExperience','int'),('energy','list[int]'),('experience','list[int]')],'int',['arrays','greedy','simulation'],['Opponents are fought in the given order.','Before each fight, current energy and experience must both be strictly greater than that opponent’s values.','Winning subtracts the opponent energy and adds the opponent experience; training raises either initial stat by one per hour.'],[([5,3,[1,4,3,2],[2,6,3,1]],'Six energy hours and two strategically required experience hours total eight.'),([2,4,[1],[3]],'Both initial stats already strictly exceed the only opponent, so no training is needed.')],[[a,b,e,x] for a,b,e,x in [(1,1,[1],[1]),(2,1,[1],[1]),(10,1,[1,2],[1,2]),(1,10,[3,4],[1,1]),(5,5,[2,2],[5,5]),(3,2,[1,1,1],[3,3,3]),(20,2,[5,5,5],[1,10,20]),(1,1,[10],[10]),(7,7,[2,3],[4,8]),(100,1,[1,1],[50,1]),(4,3,[4,1],[2,10]),(9,9,[3,3,3],[8,8,8]),(2,20,[1,1,1],[5,10,15]),(6,2,[2,2],[2,5])]],TRAIN,[TRAIN.replace('sum(energy)+1','sum(energy)'),TRAIN.replace('current<=rival','current<rival')],['Allows energy to equal the total cost even though energy must stay strictly positive before the final fight.','Allows equal experience despite the strict greater-than requirement.'],training_oracle,random_training,['Energy training can be computed once from the total energy cost.','Experience must be handled in fight order because each win increases it.','Raise current experience to rival+1 only when needed, record the increase, then add the rival’s experience.','The energy lower bound is necessary and sufficient; each experience adjustment is the minimum that permits the next fight, so delaying or adding more cannot improve the total.'],'O(n)','O(1)',3),
2389:entry('longest_subsequence_under_queries',[('nums','list[int]'),('queries','list[int]')],'list[int]',['arrays','sorting','binary search'],['For each query, choose any subsequence whose sum is at most that query.','Return the maximum possible subsequence length for every query in original query order.','All nums values are positive.'],[([[4,5,2,1],[3,10,21]],'Sorted prefix sums are one, three, seven, and twelve, giving lengths two, three, and four.'),([[2,3,4,5],[1]],'Even the smallest value exceeds one, so the answer is zero.')],[[a,q] for a,q in [([1],[0]),([1],[1]),([5],[10]),([1,2,3],[3]),([3,1,2],[4]),([10,20,30],[25]),([2,2,2],[4]),([5,1,5,1],[6]),([9,8,7],[100]),([1,10,2,9],[11]),([4,4,4,4],[15]),([2,7,1,8,2],[0,3,10]),([100,1],[1,99,101]),([6,5,4,3,2,1],[6,12])]],LIMIT,[LIMIT.replace('ordered=sorted(nums)','ordered=nums'),LIMIT.replace('bisect_right','bisect_left')],['Builds prefix sums in input order instead of selecting the cheapest values.','Uses a left insertion point and rejects a prefix whose sum equals the query.'],limited_oracle,random_limited,['To maximize count under a sum limit, choose the smallest values first.','Sort nums and build cumulative prefix sums.','For each query, binary-search the number of prefix sums no greater than it.','Any same-length selection costs at least the sorted prefix of that length, so the largest affordable prefix length is optimal.'],'O(n log n+q log n)','O(n)',3),
2390:entry('remove_stars_from_string',[('s','str')],'str',['strings','stacks'],['Every star removes itself and the closest non-star character to its left.','The input guarantees a removable character exists for every star.','Return the final string after all removals.'],[(['leet**cod*e'],'The stars remove the preceding t, e, and d, leaving lecoe.'),(['erase*****'],'Five stars remove all five letters, leaving an empty string.')],[[s] for s in ['a','a*','ab*','ab**','abc*','abc**','abc***','a*b','ab*c','abcd**','x*y*z','hello*','code***','aa**bb*']],STARS,[STARS.replace('kept.pop()','kept.pop(0)'),STARS.replace("if char=='*'","if char!='*'")],['Removes the earliest retained character instead of the closest one.','Treats normal letters as removal markers and stars as retained characters.'],stars_oracle,random_stars,['The closest surviving character to the left is the most recently retained one.','Use a list as a stack of retained characters.','Push letters; on a star, pop the stack top; finally join the stack.','Stack order exactly represents the surviving prefix after each processed character, so each pop performs the required removal.'],'O(n)','O(n)',5),
2393:entry('count_strictly_increasing_subarrays',[('nums','list[int]')],'int',['arrays','dynamic programming'],['Count nonempty contiguous subarrays whose adjacent values are strictly increasing.','Equal adjacent values break an increasing run.','Return the total across all endpoints.'],[([[1,3,5,4,4,6]],'The increasing run lengths ending at each position are one, two, three, one, one, and two, totaling ten.'),([[1,2,3,4]],'All ten nonempty subarrays are strictly increasing.')],[[a] for a in [[1],[1,1],[1,2],[2,1],[1,2,1],[3,2,1],[1,2,3],[0,-1,0],[1,1,2,2],[5,6,7,1,2],[2,4,6,8,10],[10,8,6,4],[1,3,2,4,3,5],[0,0,0,1]]],INCREASING,[INCREASING.replace('previous<value','previous<=value'),INCREASING.replace('answer+=run','answer+=1')],['Treats equal adjacent values as strictly increasing.','Counts only singleton endings and omits longer increasing subarrays.'],increasing_oracle,random_increasing,['Track the length of the strictly increasing run ending at each element.','Extend the run only when previous < current; otherwise reset it to one.','Add the current run length to the answer.','Exactly one increasing subarray ends at the current position for every possible start within its maximal increasing suffix.'],'O(n)','O(1)',5),
2395:entry('has_equal_adjacent_pair_sums',[('nums','list[int]')],'bool',['arrays','hash sets'],['Consider every contiguous subarray of length two.','Return true when two different adjacent pairs have equal sums.','The pairs may overlap.'],[([[4,2,4]],'The pairs [4,2] and [2,4] both sum to six.'),([[1,2,3,4,5]],'The adjacent sums three, five, seven, and nine are all distinct.')],[[a] for a in [[1,1],[1,1,1],[1,2,1],[1,2,3],[0,0,0],[2,3,4,1],[5,1,5],[1,-1,1,-1],[10,20,10],[3,3,4,2],[7,0,7],[1,4,2,3],[9,8,7,6],[2,5,1,6,2]]],EQUALSUM,[EQUALSUM.replace('nums[index]+nums[index+1]','nums[index]-nums[index+1]'),EQUALSUM.replace('range(len(nums)-1)','range(len(nums)-2)')],['Compares adjacent differences instead of adjacent sums.','Skips the final adjacent pair, which may create the first duplicate sum.'],equal_sum_oracle,random_equal_sum,['Compute each adjacent pair sum from left to right.','Store previously seen sums in a set.','Return true on the first repeated sum; otherwise add it and continue.','A set membership hit is equivalent to an earlier distinct adjacent pair having the same sum.'],'O(n)','O(n)',3),
}

BATCH[2390]['wrong'][1] = '''\
def remove_stars_from_string(s):
    return ''.join(char for char in s if char!='*')
'''
BATCH[2390]['wrong_reasons'][1] = 'Deletes each star but leaves the character that the star must also remove.'
