"""Batch 105: ordered matching, multi-source BFS, prefixes, and interval DP."""
from collections import deque
from functools import lru_cache
from .import_batch_055 import entry
def groups_o(a):
 groups,nums=a
 def find(group,index):return next((start+len(group) for start in range(index,len(nums)-len(group)+1) if nums[start:start+len(group)]==group),None)
 index=0
 for group in groups:
  index=find(group,index)
  if index is None:return False
 return True
def peak_o(a):
 water=a[0];sources=[(r,c) for r,row in enumerate(water) for c,value in enumerate(row) if value];return [[min(abs(r-x)+abs(c-y) for x,y in sources) for c in range(len(water[0]))] for r in range(len(water))]
def merge_o(a):
 first,second=a;answer=[]
 for i in range(max(len(first),len(second))):
  if i<len(first):answer.append(first[i])
  if i<len(second):answer.append(second[i])
 return ''.join(answer)
def moves_o(a):
 boxes=a[0];return [sum(abs(i-j) for j,char in enumerate(boxes) if char=='1') for i in range(len(boxes))]
def score_o(a):
 nums,multipliers=a
 @lru_cache(None)
 def play(step,left):
  if step==len(multipliers):return 0
  right=len(nums)-1-(step-left);factor=multipliers[step]
  return max(factor*nums[left]+play(step+1,left+1),factor*nums[right]+play(step+1,left))
 return play(0,0)
def rgroups(r):
 nums=[r.randint(-2,3) for _ in range(r.randint(1,18))];groups=[[r.randint(-2,3) for _ in range(r.randint(1,4))] for _ in range(r.randint(1,5))];return [groups,nums]
def rpeak(r):
 rows,cols=r.randint(1,6),r.randint(1,6);grid=[[0]*cols for _ in range(rows)]
 for position in r.sample(range(rows*cols),r.randint(1,rows*cols)):grid[position//cols][position%cols]=1
 return [grid]
def rmerge(r):return [''.join(r.choice('abc') for _ in range(r.randint(0,12))),''.join(r.choice('xyz') for _ in range(r.randint(0,12)))]
def rmoves(r):return [''.join(r.choice('01') for _ in range(r.randint(1,30)))]
def rscore(r):
 nums=[r.randint(-10,10) for _ in range(r.randint(1,10))];m=r.randint(1,len(nums));return [nums,[r.randint(-10,10) for _ in range(m)]]
GROUPS='''def can_form_from_ordered_groups(groups, nums):
 position=0
 for group in groups:
  while position+len(group)<=len(nums) and nums[position:position+len(group)]!=group:position+=1
  if position+len(group)>len(nums):return False
  position+=len(group)
 return True
'''
PEAK='''def highest_peak_map(is_water):
 from collections import deque
 rows,cols=len(is_water),len(is_water[0]);height=[[-1]*cols for _ in range(rows)];queue=deque()
 for r in range(rows):
  for c in range(cols):
   if is_water[r][c]:height[r][c]=0;queue.append((r,c))
 while queue:
  r,c=queue.popleft()
  for nr,nc in ((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
   if 0<=nr<rows and 0<=nc<cols and height[nr][nc]<0:height[nr][nc]=height[r][c]+1;queue.append((nr,nc))
 return height
'''
MERGE='''def merge_strings_alternately(word1, word2):
 answer=[]
 for index in range(max(len(word1),len(word2))):
  if index<len(word1):answer.append(word1[index])
  if index<len(word2):answer.append(word2[index])
 return ''.join(answer)
'''
MOVES='''def ball_moves_for_each_box(boxes):
 answer=[0]*len(boxes);balls=moves=0
 for index,char in enumerate(boxes):answer[index]+=moves;balls+=char=='1';moves+=balls
 balls=moves=0
 for index in range(len(boxes)-1,-1,-1):answer[index]+=moves;balls+=boxes[index]=='1';moves+=balls
 return answer
'''
SCORE='''def maximum_multiplier_score(nums, multipliers):
 from functools import lru_cache
 @lru_cache(None)
 def play(step,left):
  if step==len(multipliers):return 0
  right=len(nums)-1-(step-left);factor=multipliers[step]
  return max(factor*nums[left]+play(step+1,left+1),factor*nums[right]+play(step+1,left))
 return play(0,0)
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1764:E('can_form_from_ordered_groups',[('groups','list[list[int]]'),('nums','list[int]')],'bool',['arrays','greedy','pattern-matching'],['Match every group as an exact contiguous subarray of nums in the given order.','Matched groups may not overlap; unused nums elements may appear before, between, or after groups.'],[([[[1,-1,-1],[3,-2,0]],[1,-1,0,1,-1,-1,3,-2,0]],'The first match begins at index three and the second immediately follows it.'),([[[10,-2],[1,2,3,4]],[1,2,3,4,10,-2]],'The second requested group occurs only before the first match would finish, so order cannot be satisfied.')],[[*x] for x in [([[1,-1,-1],[3,-2,0]],[1,-1,0,1,-1,-1,3,-2,0]),([[10,-2],[1,2,3,4]],[1,2,3,4,10,-2]),([[1]],[1]),([[1]],[2]),([[1],[2]],[1,2]),([[1],[1]],[1]),([[1,2]],[0,1,2,3]),([[1,2],[2,3]],[1,2,3]),([[-1,-1],[0]],[5,-1,-1,4,0]),([[1,1],[1]],[1,1,1]),([[1,2],[3,4]],[1,2,0,3,4]),([[2,2]],[2,2]),([[2,2]],[2]),([[1],[2],[3]],[1,0,2,0,3])]],GROUPS,[GROUPS.replace('position+=len(group)','position+=1'),GROUPS.replace('!=group','==group')],['Advances only one position after a match, allowing later groups to overlap it.','Skips positions that match and stops at a nonmatching slice.'],groups_o,rgroups,L('For each group, the earliest nonoverlapping match leaves the most suffix space for later groups.','Scan nums from the current position until the group matches, then jump past it.','Return false if a group cannot fit or match; otherwise continue until every group is consumed.','Replacing any later chosen match by the earliest available one cannot hurt subsequent ordered matches, proving the greedy scan.'),'O(total scan*group length)','O(1)',5),
1765:E('highest_peak_map',[('is_water','list[list[int]]')],'list[list[int]]',['matrices','breadth-first-search'],['Water cells contain one and must receive height zero; land cells contain zero.','Assign nonnegative heights with adjacent differences at most one, maximizing the highest height; return the height matrix.'],[([[[0,1],[0,0]]],'Distances to the water cell give [[1,0],[2,1]].'),([[[0,0,1],[1,0,0],[0,0,0]]],'Multi-source distances create heights [[1,1,0],[0,1,1],[1,2,2]].')],[[g] for g in [[[1]],[[0,1]],[[1,0]],[[0],[1]],[[0,1],[0,0]],[[1,0],[0,0]],[[1,1],[1,1]],[[0,0,1],[1,0,0],[0,0,0]],[[1,0,0],[0,0,0],[0,0,1]],[[0,1,0],[0,0,0]],[[1,0,1],[0,0,0]],[[0,0],[0,1],[0,0]],[[1,0,0,0]],[[0,0,0],[0,1,0],[0,0,0]]]],PEAK,[PEAK.replace('height[nr][nc]=height[r][c]+1','height[nr][nc]=height[r][c]+2'),PEAK.replace('queue.popleft()','queue.pop()')],['Raises each BFS layer by two and violates the adjacent-difference bound.','Uses depth-first processing, assigning nonminimal distance from whichever water source reaches a cell first.'],peak_o,rpeak,L('The greatest valid height at a cell is its shortest Manhattan path distance to water.','Run breadth-first search simultaneously from every water cell at height zero.','Assign each unseen neighbor current+1 and enqueue it.','Distance-to-nearest-water satisfies every edge bound, and no valid assignment can exceed path length along a route to water.'),'O(rows*columns)','O(rows*columns)',5),
1768:E('merge_strings_alternately',[('word1','str'),('word2','str')],'str',['strings','two-pointers'],['Take one character from word1, then one from word2, repeating while possible.','When one word ends, append the remainder of the other word.'],[(['abc','pqr'],'Alternating characters produces apbqcr.'),(['ab','pqrs'],'After apbq, word2 contributes its remaining rs.')],[[*x] for x in [('abc','pqr'),('ab','pqrs'),('abcd','pq'),('','abc'),('abc',''),('a','b'),('a','xyz'),('xyz','a'),('same','size'),('12','abcd'),('hello','world'),('x',''),('','y'),('longer','up')]],MERGE,[MERGE.replace('answer.append(word1[index])','answer.append(word2[index])',1),MERGE.replace("return ''.join(answer)","return ''.join(answer[::-1])")],['Takes the corresponding word2 character in place of each word1 character.','Reverses the completed alternating result.'],merge_o,rmerge,L('Only the same index from each word is consumed in each round.','Iterate through the longer length and append each available word1 then word2 character.','Bounds-check both words at every index and join the collected characters.','This exactly follows the required alternating order, and the checks append the unmatched suffix unchanged.'),'O(n+m)','O(n+m)',3),
1769:E('ball_moves_for_each_box',[('boxes','str')],'list[int]',['strings','prefix-sums'],['boxes[i] is one when box i contains one ball and zero otherwise.','For every destination box, return the total adjacent moves needed to bring all balls there.'],[(['110'],'Destinations zero, one, and two require totals one, one, and three.'),(['001011'],'Summing each ball’s distance gives [11,8,5,4,3,4].')],[[s] for s in ['110','001011','0','1','10','01','11','0000','1111','10001','01010','10101','0001','1000']],MOVES,[MOVES.replace('moves+=balls','moves+=1'),MOVES.replace("balls+=boxes[index]=='1'","balls+=boxes[index]=='0'")],['Increases movement by one per step instead of by the number of balls already crossed.','Counts empty boxes as balls during the right-to-left pass.'],moves_o,rmoves,L('Moving the destination one step changes cost by the number of balls on each side.','Accumulate contributions in separate left-to-right and right-to-left passes.','Track balls crossed and cumulative moves; add moves to answer before consuming the current box in each direction.','Each ball contributes one move for every edge between its source and destination, counted exactly in the corresponding directional pass.'),'O(n)','O(n)',5),
1770:E('maximum_multiplier_score',[('nums','list[int]'),('multipliers','list[int]')],'int',['dynamic-programming','recursion'],['For each multiplier in order, remove either the current leftmost or rightmost nums value and add their product.','Use exactly len(multipliers) operations and return the maximum score.'],[([[1,2,3],[3,2,1]],'Choosing right three, right two, then left one scores 9+4+1=14.'),([[-5,-3,-3,-2,7,1],[-10,-5,3,4,6]],'Dynamic programming over remaining endpoints yields 102.')],[[*x] for x in [([1,2,3],[3,2,1]),([-5,-3,-3,-2,7,1],[-10,-5,3,4,6]),([5],[2]),([1,2],[1]),([1,2],[1,1]),([-1,-2],[3]),([-1,5],[-2]),([1,2,3],[1,1]),([3,2,1],[-1,-2]),([10,-10,5],[2,-3]),([0,1,0],[5,5]),([4,-2,7,1],[3,-1,2]),([-5,6,-7,8],[2,2,2]),([1,9,2,8,3],[4,-3,2])]],SCORE,[SCORE.replace('step-left','step+left'),SCORE.replace('play(step+1,left+1)','play(step+1,left)')],['Computes the right endpoint from the wrong number of prior right removals.','Fails to advance the left pointer after choosing the left value, allowing reuse.'],score_o,rscore,L('After step operations, the state is determined by how many selections came from the left; right removals follow from step-left.','Memoize the best score for (step,left) and try both endpoints.','Use right=n-1-(step-left), multiply each endpoint by the current factor, and recurse.','The two transitions exhaust the required choice at each step, and memoization merges all histories with identical remaining intervals.'),'O(m^2)','O(m^2)',8),
}
BATCH[1768]['wrong'][0]=MERGE.replace('if index<len(word1):answer.append(word1[index])','if index<len(word1):pass')
BATCH[1768]['wrong_reasons'][0]='Consumes the alternating positions for word1 without appending their characters.'
BATCH[1770]['wrong'][0]=SCORE.replace("return max(factor*nums[left]+play(step+1,left+1),factor*nums[right]+play(step+1,left))","return factor*nums[right]+play(step+1,left)")
BATCH[1770]['wrong_reasons'][0]='Always selects the right endpoint and never considers a better left choice.'
