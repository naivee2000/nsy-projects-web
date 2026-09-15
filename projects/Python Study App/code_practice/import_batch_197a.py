"""Array validity, nondecreasing increments, parity suffixes, scoring, and reversal."""
from .import_batch_055 import entry


def valid_oracle(a):
    nums=a[0];out=[]
    for i,x in enumerate(nums):
        if i==0 or i==len(nums)-1 or x>max(nums[:i]) or x>max(nums[i+1:]):out.append(x)
    return out
def random_valid(r):return [[r.randint(1,30) for _ in range(r.randint(1,40))]]
def increments_oracle(a):return sum(max(a[0][i]-a[0][i+1],0) for i in range(len(a[0])-1))
def random_increments(r):return [[r.randint(1,100) for _ in range(r.randint(1,50))]]
def parity_oracle(a):return [sum((x-y)%2!=0 for y in a[0][i+1:]) for i,x in enumerate(a[0])]
def random_parity(r):return [[r.randint(-50,50) for _ in range(r.randint(1,50))]]
def score_oracle(a):
    score=wickets=0
    for event in a[0]:
        if event.isdigit():score+=int(event)
        elif event=='W':
            wickets+=1
            if wickets==10:break
        else:score+=1
    return [score,wickets]
def random_score(r):return [[r.choice(['0','1','2','3','4','6','W','WD','NB']) for _ in range(r.randint(1,30))]]
def concat_oracle(a):return a[0]+a[0][::-1]
def random_concat(r):return [[r.randint(-50,50) for _ in range(r.randint(1,40))]]

VALID='''def find_valid_elements(nums):
    right=[0]*len(nums);best=float('-inf')
    for i in range(len(nums)-1,-1,-1):
        right[i]=best;best=max(best,nums[i])
    out=[];left=float('-inf')
    for i,x in enumerate(nums):
        if i==0 or i==len(nums)-1 or x>left or x>right[i]:out.append(x)
        left=max(left,x)
    return out
'''
INCREMENTS='''def minimum_nondecreasing_increment_cost(nums):
    return sum(max(nums[i]-nums[i+1],0) for i in range(len(nums)-1))
'''
PARITY='''def count_opposite_parity_to_right(nums):
    remaining=[sum(x%2==0 for x in nums),sum(x%2!=0 for x in nums)];out=[]
    for x in nums:
        remaining[x&1]-=1;out.append(remaining[(x&1)^1])
    return out
'''
SCORE='''def validate_event_score(events):
    score=wickets=0
    for event in events:
        if event.isdigit():score+=int(event)
        elif event=='W':
            wickets+=1
            if wickets==10:break
        else:score+=1
    return [score,wickets]
'''
CONCAT='''def concatenate_with_reverse(nums):
    return nums+nums[::-1]
'''

BATCH={
3912:entry('find_valid_elements',[('nums','list[int]')],'list[int]',['arrays','prefix maxima','suffix maxima'],['The first and last values are always valid.','An interior value is valid when it is strictly greater than every value on at least one side.','Return valid values in their original order.'],[([[1,2,4,2,3,2]],'The endpoints qualify, and 2, 4, and 3 each dominate at least one complete side.'),([[5,4,3]],'Every value dominates all values to its right, so all three qualify.')],[[x] for x in [[1],[1,2],[2,1],[1,2,4,2,3,2],[5,4,3],[1,1,1],[3,1,2],[2,5,1,4],[9,1,8,2,7],[1,3,2,4],[4,2,4],[2,1,3,1,2],[10,9,8,7],[1,5,5,1]]],VALID,[VALID.replace('x>left or x>right[i]','x>left and x>right[i]'),VALID.replace('x>left or x>right[i]','x<left or x<right[i]')],['Requires domination of both sides instead of either side.','Reverses both strict dominance comparisons.'],valid_oracle,random_valid,['Precompute the maximum strictly to each index’s right.','Maintain the maximum strictly to the left during a forward scan.','Accept endpoints or a strict comparison against either side maximum.','The two running summaries represent every value on each complete side.'],'O(n)','O(n)',5),
3914:entry('minimum_nondecreasing_increment_cost',[('nums','list[int]')],'int',['arrays','greedy'],['An operation adds any positive integer x to every value in one nonempty subarray.','Minimize the sum of all chosen x values needed to make nums nondecreasing.','Return that minimum cost.'],[([[3,3,2,1]],'The drops 3-to-2 and 2-to-1 each require one unit, for total cost two.'),([[5,1,2,3]],'Raising the suffix beginning at one by four makes the array nondecreasing.')],[[x] for x in [[1],[1,2],[2,1],[3,3,2,1],[5,1,2,3],[1,1,1],[5,4,3,2,1],[1,3,2,4],[10,1,10],[2,5,1],[9,8],[1,10,2,3],[7,3,5,1],[100,1]]],INCREMENTS,[INCREMENTS.replace('nums[i]-nums[i+1]','nums[i+1]-nums[i]'),INCREMENTS.replace(',0)',',1)')],['Counts upward steps instead of downward deficits.','Charges one even when adjacent values already satisfy the order.'],increments_oracle,random_increments,['Each downward adjacent gap must be repaired.','One suffix increment can repair exactly the gap at its left boundary.','Sum max(nums[i]-nums[i+1], 0) over adjacent pairs.','Every drop supplies a lower bound, and applying those increments to matching suffixes attains it.'],'O(n)','O(1)',5),
3917:entry('count_opposite_parity_to_right',[('nums','list[int]')],'list[int]',['arrays','counting'],['For every index i, inspect indices strictly to its right.','Count values whose parity differs from nums[i].','Return all per-index counts.'],[([[1,2,3,4]],'One has two even values to its right; two has one odd; three has one even; four has none.'),([[2,4,6]],'No value has an opposite-parity value to its right.')],[[x] for x in [[1],[1,2],[2,1],[1,2,3,4],[2,4,6],[1,3,5],[-1,0,1],[0,0,1,1],[9,8,7,6,5],[2,3,2,3],[10,11],[1,1,2],[4,1,6,3],[0,1,0,1,0]]],PARITY,[PARITY.replace('remaining[x&1]-=1;',''),PARITY.replace('remaining[(x&1)^1]','remaining[x&1]')],['Includes the current element in future inventory.','Counts same-parity rather than opposite-parity values.'],parity_oracle,random_parity,['Count all even and odd values first.','Before answering an index, remove its value from the remaining inventory.','Read the bucket for the opposite parity.','Removing values left to right leaves exactly the strict suffix.'],'O(n)','O(1)',3),
3921:entry('validate_event_score',[('events','list[str]')],'list[int]',['arrays','simulation'],['Digit events add their numeric value; WD and NB add one.','W increments the wicket counter but adds no score.','Stop immediately after the tenth W and return [score,wickets].'],[([['1','4','W','6','WD']],'The numeric events add eleven, WD adds one, and one W is recorded.'),([['W']*10+['6']],'Processing stops at the tenth W, so the trailing six is ignored.')],[[x] for x in [['0'],['6'],['WD'],['NB'],['W'],['1','4','W','6','WD'],['W']*10+['6'],['W']*9+['NB'],['1','2','3'],['WD','NB','W'],['0','W','0'],['6','6','W','NB'],['W']*11,['4','WD','2','NB']]],SCORE,[SCORE.replace("else:score+=1","else:score+=0"),SCORE.replace('if wickets==10:break','if wickets==11:break')],['Fails to score WD and NB events.','Processes one event beyond the tenth wicket.'],score_oracle,random_score,['Maintain score and wicket counters.','Classify digits, W, and the two one-point tokens.','Break as soon as the W count reaches ten.','The loop order ensures no event after the stop condition is scored.'],'O(n)','O(1)',3),
3925:entry('concatenate_with_reverse',[('nums','list[int]')],'list[int]',['arrays','simulation'],['Create a new array twice as long as nums.','Place nums first and its reverse second.','Return the new array without changing nums.'],[([[1,2,3]],'The original sequence is followed by 3, 2, 1.'),([[1]],'A one-value array followed by its reverse contains the value twice.')],[[x] for x in [[1],[1,2],[2,1],[1,2,3],[0],[-1,0,1],[5,5],[9,8,7,6],[-3,-2],list(range(5)),[10,-10],[4,1,4],[2,3,5,7],[100]]],CONCAT,[CONCAT.replace('nums[::-1]','nums'),CONCAT.replace('nums+nums[::-1]','nums[::-1]+nums')],['Repeats nums without reversing the second half.','Puts the reversed half before the original half.'],concat_oracle,random_concat,['Copy nums for the first half.','A reverse slice supplies the second half.','Concatenate the two sequences.','Each original value appears once in forward order and once in reverse order.'],'O(n)','O(n)',3),
}
