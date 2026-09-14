"""Button timing, triple condition, prefix deletion, column increments, and wildcard matching."""
from .import_batch_055 import entry

def button_oracle(a):
    best=(-1,None);previous=0
    for button,time in a[0]:
        duration=time-previous;previous=time
        if duration>best[0] or duration==best[0] and button<best[1]:best=(duration,button)
    return best[1]
def random_button(r):
    ids=r.sample(range(1,101),r.randint(1,20));time=0;events=[]
    for button in ids:time+=r.randint(1,20);events.append([button,time])
    return [events]
def triple_oracle(a):return sum(2*(a[0][i]+a[0][i+2])==a[0][i+1] for i in range(len(a[0])-2))
def random_triple(r):return [[r.randint(-30,30) for _ in range(r.randint(3,50))]]
def distinct_oracle(a):
    nums=a[0]
    for operations in range((len(nums)+2)//3+1):
        rest=nums[3*operations:]
        if len(rest)==len(set(rest)):return operations
def random_distinct(r):return [[r.randint(1,12) for _ in range(r.randint(1,40))]]
def columns_oracle(a):
    grid=a[0];answer=0
    for col in range(len(grid[0])):
        previous=grid[0][col]
        for row in range(1,len(grid)):
            current=max(grid[row][col],previous+1);answer+=current-grid[row][col];previous=current
    return answer
def random_columns(r):
    rows,columns=r.randint(1,8),r.randint(1,8)
    return [[[r.randint(0,20) for _ in range(columns)] for _ in range(rows)]]
def wildcard_oracle(a):
    s,p=a;left,right=p.split('*')
    for start in range(len(s)+1):
        if s.startswith(left,start):
            after=start+len(left)
            if s.find(right,after)>=0:return True
    return False
def random_wildcard(r):
    s=''.join(r.choice('abcd') for _ in range(r.randint(1,40)));i=r.randint(0,len(s));j=r.randint(i,len(s))
    left=s[i:r.randint(i,j)] if r.random()<.7 else ''.join(r.choice('abcd') for _ in range(r.randint(0,5)))
    right=s[r.randint(i,j):j] if r.random()<.7 else ''.join(r.choice('abcd') for _ in range(r.randint(0,5)))
    return [s,left+'*'+right]
def zigzag_oracle(a):
    grid=a[0];ordered=[]
    for row in range(len(grid)):
        columns=range(len(grid[0])) if row%2==0 else range(len(grid[0])-1,-1,-1)
        for column in columns:ordered.append(grid[row][column])
    return ordered[::2]
def random_zigzag(r):
    rows,columns=r.randint(2,10),r.randint(2,10)
    return [[[r.randint(1,100) for _ in range(columns)] for _ in range(rows)]]

BUTTON='''def longest_button_push(events):
    previous=0
    best_duration=-1
    answer=None
    for button,time in events:
        duration=time-previous
        previous=time
        if duration>best_duration or duration==best_duration and button<answer:
            best_duration=duration
            answer=button
    return answer
'''
TRIPLE='''def count_special_length_three_subarrays(nums):
    return sum(nums[i+1]==2*(nums[i]+nums[i+2]) for i in range(len(nums)-2))
'''
DISTINCT='''def minimum_prefix_triple_removals_for_distinct(nums):
    operations=0
    while len(nums)-3*operations>0:
        remaining=nums[3*operations:]
        if len(remaining)==len(set(remaining)):break
        operations+=1
    return operations
'''
COLUMNS='''def minimum_column_increment_operations(grid):
    operations=0
    for column in range(len(grid[0])):
        previous=grid[0][column]
        for row in range(1,len(grid)):
            needed=max(grid[row][column],previous+1)
            operations+=needed-grid[row][column]
            previous=needed
    return operations
'''
WILDCARD='''def has_single_wildcard_substring(s,p):
    prefix,suffix=p.split('*')
    start=s.find(prefix)
    while start!=-1:
        if s.find(suffix,start+len(prefix))!=-1:return True
        start=s.find(prefix,start+1)
    return False
'''
ZIGZAG='''def zigzag_grid_traversal_with_skip(grid):
    answer=[]
    take=True
    for row_index,row in enumerate(grid):
        values=row if row_index%2==0 else reversed(row)
        for value in values:
            if take:answer.append(value)
            take=not take
    return answer
'''

BATCH={
3386:entry('longest_button_push',[('events','list[list[int]]')],'int',['arrays','simulation'],['Each event contains a button index and the cumulative time when its press ends.','A press duration is its end time minus the preceding event’s end time, or zero for the first start.','Return the button with the longest duration, breaking ties by smaller button index.'],[([[[1,2],[2,5],[3,9],[1,15]]],'The durations are 2, 3, 4, and 6, so button one has the longest press.'),([[[10,5],[1,10]]],'Both durations are five; the smaller button index one wins the tie.')],[[e] for e in [[[1,1]],[[2,5]],[[1,2],[2,3]],[[2,2],[1,4]],[[5,3],[4,8]],[[10,5],[1,10]],[[3,1],[2,4],[1,9]],[[1,10],[2,11]],[[9,2],[8,4],[7,6]],[[4,4],[3,5],[2,6]],[[1,2],[2,5],[3,9],[1,15]],[[6,7],[2,8]],[[100,1],[1,2]],[[3,3],[1,7],[2,8]]]],BUTTON,[BUTTON.replace('time-previous','time'),BUTTON.replace('button<answer','button>answer')],['Uses cumulative timestamps as durations.','Breaks equal-duration ties toward the larger button index.'],button_oracle,random_button,['Track the previous cumulative end time.','Subtract it from each current end time to obtain that press duration.','Replace the best on a longer duration or an equal duration with a smaller index.','This evaluates every press exactly once with the specified tie rule.'],'O(n)','O(1)',3),
3392:entry('count_special_length_three_subarrays',[('nums','list[int]')],'int',['arrays','subarrays'],['Inspect every contiguous subarray of exactly three values.','It qualifies when the middle value equals twice the sum of the first and third values.','Return the number of qualifying subarrays.'],[([[1,2,1,4,1]],'Only [1,4,1] qualifies because four is twice the endpoint sum two.'),([[0,0,0]],'The all-zero triple satisfies the equality.')],[[x] for x in [[1,1,1],[0,0,0],[1,4,1],[1,2,1,4,1],[2,8,2],[-1,-4,-1],[1,6,2],[3,12,3,12,3],[1,0,-1],[5,20,5,0],[2,7,2],[-2,0,2],[4,16,4],[1,4,1,4,1]]],TRIPLE,[TRIPLE.replace('2*(nums[i]+nums[i+2])','nums[i]+nums[i+2]'),TRIPLE.replace('==','!=')],['Forgets to double the endpoint sum.','Counts nonqualifying triples.'],triple_oracle,random_triple,['Slide a length-three window over nums.','For each start, compute the two endpoint sum.','Compare the middle value with twice that sum.','Summing the Boolean results counts each qualifying window once.'],'O(n)','O(1)',3),
3396:entry('minimum_prefix_triple_removals_for_distinct',[('nums','list[int]')],'int',['arrays','sets','simulation'],['One operation removes the first three remaining elements; if fewer than three remain, it removes all of them.','Stop when the remaining array has pairwise distinct values.','Return the minimum number of operations.'],[([[1,2,3,4,2,3,3,5,7]],'After two operations the suffix [3,5,7] is distinct; after one it is not.'),([[4,5,6]],'The original array is already distinct, so no operation is needed.')],[[x] for x in [[1],[1,1],[1,2],[1,2,3],[1,1,1],[1,2,1,2],[1,2,3,1],[1,2,3,4,2,3,3,5,7],[4,5,6],[1,1,2,2,3,3],[1,2,3,4,1],[5,5,5,5,5],[1,2,1,3,4,5],[9,8,7,9]]],DISTINCT,[DISTINCT.replace('3*operations','2*operations'),DISTINCT.replace('operations+=1','operations+=2')],['Removes only two elements per operation.','Counts each required operation twice.'],distinct_oracle,random_distinct,['Check whether the current suffix has duplicates using a set.','If it does, advance the suffix start by three and count one operation.','The first distinct suffix encountered is optimal because operations have only one possible effect.','An empty suffix is distinct, covering removal of a final short remainder.'],'O(n^2)','O(n)',3),
3402:entry('minimum_column_increment_operations',[('grid','list[list[int]]')],'int',['matrices','greedy'],['You may increment any grid cell by one per operation.','Make every column strictly increasing from top to bottom.','Return the minimum total number of increments.'],[([[[3,2],[1,3],[3,4],[0,1]]],'Raising each cell only to one above its adjusted predecessor requires fifteen increments total.'),([[[1,2],[2,3],[3,4]]],'Both columns are already strictly increasing, so zero operations are needed.')],[[g] for g in [[[0]],[[1],[1]],[[1],[2]],[[2],[1]],[[1,2],[2,3],[3,4]],[[3,2],[1,3],[3,4],[0,1]],[[0,0],[0,0]],[[5,1],[4,2],[3,3]],[[1,5],[1,1]],[[9,9],[0,0],[0,0]],[[1,2,3]],[[2,0],[2,0],[2,0]],[[0,5],[5,0]],[[3,3],[2,2],[1,1]]]],COLUMNS,[COLUMNS.replace('previous+1','previous'),COLUMNS.replace('grid[row][column]','grid[row][0]')],['Makes columns merely nondecreasing instead of strictly increasing.','Reads column zero while adjusting every column.'],columns_oracle,random_columns,['Treat each column independently.','Scan downward while tracking the already adjusted previous value.','Raise the current cell only to max(original, previous+1).','Any smaller value violates strict increase and any larger value wastes operations, proving the greedy choice optimal.'],'O(rows*columns)','O(1)',3),
3407:entry('has_single_wildcard_substring',[('s','str'),('p','str')],'bool',['strings','pattern matching'],['Pattern p contains exactly one asterisk, which may match any sequence including empty.','Return whether some contiguous substring of s matches the complete pattern.','Characters before and after the asterisk must appear in order without gaps inside their own parts.'],[(['leetcode','ee*e'],'Replacing the asterisk with tcod makes the matching substring eetcode.'),(['car','c*v'],'No substring begins with c and later ends with v.')],[[s,p] for s,p in [('a','*'),('a','a*'),('a','*a'),('a','a*a'),('abc','a*c'),('abc','ab*bc'),('leetcode','ee*code'),('car','c*v'),('hello','he*lo'),('hello','x*'),('mississippi','iss*ppi'),('abcd','bc*'),('abcd','*bc'),('aaaa','aa*aa')]],WILDCARD,[WILDCARD.replace('start+len(prefix)','start'),WILDCARD.replace("s.find(prefix)","s.find(suffix)",1)],['Allows the suffix to overlap the required prefix.','Searches for the suffix where the prefix must begin.'],wildcard_oracle,random_wildcard,['Split p at its one asterisk into a fixed prefix and suffix.','Find an occurrence of the prefix in s.','Search for the suffix at or after the end of that prefix; the intervening text is consumed by the asterisk.','Try later prefix occurrences if necessary; success of either ordered fixed part proves a matching substring.'],'O(n^2)','O(1)',3),
3417:entry('zigzag_grid_traversal_with_skip',[('grid','list[list[int]]')],'list[int]',['arrays','matrices','simulation'],['Traverse row zero left to right, row one right to left, and continue alternating directions.','Across that single traversal, visit the first cell and skip every alternate cell.','Return visited values in traversal order without modifying grid.'],[([[[1,2],[3,4]]],'The zigzag order is 1,2,4,3; taking alternate cells gives [1,4].'),([[[1,2,3],[4,5,6],[7,8,9]]],'The zigzag order yields alternate visited values [1,3,5,7,9].')],[[g] for g in [[[1,2],[3,4],[5,6]],[[2,1],[2,1],[2,1]],[[1,2,3],[4,5,6]],[[1,2],[3,4],[5,6],[7,8]],[[1,2,3,4],[5,6,7,8]],[[9,8],[7,6]],[[1,1,1],[2,2,2]],[[1,2,3,4,5],[6,7,8,9,10]],[[10,20],[30,40],[50,60]],[[1,2,3],[4,5,6],[7,8,9],[10,11,12]],[[5,4,3,2],[1,2,3,4]],[[1,9],[2,8],[3,7]],[[4,3,2],[5,6,7]],[[1,2,3,4],[8,7,6,5],[9,10,11,12]]]],ZIGZAG,[ZIGZAG.replace('else reversed(row)','else row'),ZIGZAG.replace('take=True','take=False')],['Traverses every row left to right rather than zigzagging.','Skips the first cell instead of visiting it.'],zigzag_oracle,random_zigzag,['Form the row traversal in alternating directions.','Maintain one take/skip flag across row boundaries.','Append a value only when the flag says take, then flip it after every cell.','A persistent flag implements alternate-cell skipping over the complete zigzag sequence.'],'O(rows*columns)','O(output)',3),
}
