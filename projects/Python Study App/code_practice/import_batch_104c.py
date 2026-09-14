"""Third group of batch 104: dynamic programming and meet-in-the-middle."""
from bisect import bisect_left,bisect_right
from itertools import combinations
from functools import lru_cache
from .import_batch_055 import entry
def square_o(a):
 nums=a[0];best=-10**18
 for changed in range(len(nums)):
  values=nums[:];values[changed]**=2
  for left in range(len(nums)):
   total=0
   for right in range(left,len(nums)):total+=values[right];best=max(best,total)
 return best
def events_o(a):
 events,k=a;best=0
 for size in range(min(k,len(events))+1):
  for chosen in combinations(events,size):
   ordered=sorted(chosen);valid=all(ordered[i][1]<ordered[i+1][0] for i in range(len(ordered)-1))
   if valid:best=max(best,sum(event[2] for event in ordered))
 return best
def merge_o(a):
 first,second=a
 @lru_cache(None)
 def build(i,j):
  if i==len(first):return second[j:]
  if j==len(second):return first[i:]
  return max(first[i]+build(i+1,j),second[j]+build(i,j+1))
 return build(0,0)
def closest_o(a):
 nums,goal=a;best=abs(goal)
 for mask in range(1<<len(nums)):
  total=sum(nums[i] for i in range(len(nums)) if mask>>i&1);best=min(best,abs(total-goal))
 return best
def alternating_o(a):
 s=a[0];return min(sum(char!=str(i%2) for i,char in enumerate(s)),sum(char!=str(1-i%2) for i,char in enumerate(s)))
def rsquare(r):return [[r.randint(-15,15) for _ in range(r.randint(1,15))]]
def revents(r):
 events=[]
 for _ in range(r.randint(1,9)):
  start=r.randint(1,15);events.append([start,start+r.randint(0,5),r.randint(1,20)])
 return [events,r.randint(1,len(events))]
def rmerge(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,7))),''.join(r.choice('abc') for _ in range(r.randint(1,7)))]
def rclosest(r):return [[r.randint(-20,20) for _ in range(r.randint(1,12))],r.randint(-50,50)]
def ralternating(r):return [''.join(r.choice('01') for _ in range(r.randint(1,40)))]
SQUARE='''def maximum_subarray_after_one_square(nums):
 plain=used=answer=-10**18
 for value in nums:
  previous_plain=plain;plain=max(value,plain+value);used=max(value*value,previous_plain+value*value,used+value);answer=max(answer,used)
 return answer
'''
EVENTS='''def maximum_event_value(events, k):
 from bisect import bisect_right
 from functools import lru_cache
 events=sorted(events);starts=[event[0] for event in events]
 @lru_cache(None)
 def best(index,left):
  if index==len(events) or left==0:return 0
  following=bisect_right(starts,events[index][1]);return max(best(index+1,left),events[index][2]+best(following,left-1))
 return best(0,k)
'''
MERGE='''def lexicographically_largest_merge(word1, word2):
 first=second=0;answer=[]
 while first<len(word1) and second<len(word2):
  if word1[first:]>word2[second:]:answer.append(word1[first]);first+=1
  else:answer.append(word2[second]);second+=1
 return ''.join(answer)+word1[first:]+word2[second:]
'''
CLOSEST='''def closest_subsequence_sum_difference(nums, goal):
 from bisect import bisect_left
 middle=len(nums)//2
 def sums(values):
  result=[0]
  for value in values:result += [total+value for total in result]
  return result
 left=sums(nums[:middle]);right=sorted(sums(nums[middle:]));answer=abs(goal)
 for value in left:
  index=bisect_left(right,goal-value)
  for at in (index-1,index):
   if 0<=at<len(right):answer=min(answer,abs(value+right[at]-goal))
 return answer
'''
ALTERNATING='''def minimum_alternating_changes(s):
 mismatch=sum(char!=str(index%2) for index,char in enumerate(s))
 return min(mismatch,len(s)-mismatch)
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1746:E('maximum_subarray_after_one_square',[('nums','list[int]')],'int',['arrays','dynamic-programming'],['Choose exactly one array element and replace it by its square, then choose a nonempty contiguous subarray.','Return the maximum possible subarray sum.'],[([[2,-1,-4,-3]],'Squaring negative four and taking [2,-1,16] produces seventeen.'),([[1,-1,1,1,-1,-1,1]],'Squaring either one changes nothing; the best contiguous sum is three.')],[[x] for x in [[2,-1,-4,-3],[1,-1,1,1,-1,-1,1],[1],[-1],[0],[2,3],[-2,-3],[1,-5,2],[5,-1,5],[-10,1,1],[3,-4,3],[-2,5,-2],[-1,-1,-1],[4,-10,-3,2]]],SQUARE,[SQUARE.replace('value*value','value',1),SQUARE.replace('used+value','plain+value')],['Never squares the current element when starting the transformed state.','Forgets the already-used state and permits postponing the square beyond the chosen subarray.'],square_o,rsquare,L('A best subarray ending here either has not used the square or has used it exactly once.','Track the best ordinary ending sum and transformed ending sum.','Update transformed from square alone, previous plain plus square, or previous transformed plus value.','These are the exhaustive positions of the one squared element relative to the subarray ending here.'),'O(n)','O(1)',8),
1751:E('maximum_event_value',[('events','list[list[int]]'),('k','int')],'int',['dynamic-programming','binary-search'],['Each event is [start,end,value], occupies both endpoint days, and may be attended whole.','Attend at most k nonoverlapping events to maximize total value.'],[([[[1,2,4],[3,4,3],[2,3,1]],2],'Events [1,2] and [3,4] do not overlap and total seven.'),([[[1,2,4],[3,4,3],[2,3,10]],2],'The value-ten event overlaps both others, so attending it alone is optimal.')],[[*x] for x in [([[1,2,4],[3,4,3],[2,3,1]],2),([[1,2,4],[3,4,3],[2,3,10]],2),([[1,1,5]],1),([[1,2,5],[2,3,6]],2),([[1,2,5],[3,3,6]],2),([[1,5,10],[2,3,20]],1),([[1,1,2],[2,2,3],[3,3,4]],2),([[5,6,7],[1,2,8]],2),([[1,10,5],[11,12,6]],2),([[1,3,4],[4,6,5],[7,8,6]],3),([[1,2,10],[3,4,1],[5,6,10]],2),([[2,2,5],[2,2,7]],1),([[1,100,50],[2,3,20],[4,5,20]],2),([[1,1,1],[2,2,2],[3,3,3],[4,4,4]],3)]],EVENTS,[EVENTS.replace('bisect_right(starts,events[index][1])','bisect_left(starts,events[index][1])'),EVENTS.replace('left-1','left')],['Allows an event starting on the same day the current event ends.','Never consumes an attendance slot when selecting an event.'],events_o,revents,L('After sorting by start, selecting an event jumps to the first start strictly after its end.','Memoize the best value by event index and remaining slots.','Compare skipping with value+best(next_nonoverlap,left-1), locating next by upper-bound search.','Every feasible schedule either skips the current event or selects it and then lies wholly in the computed suffix.'),'O(n log n+n*k)','O(n*k)',8),
1754:E('lexicographically_largest_merge',[('word1','str'),('word2','str')],'str',['strings','greedy'],['Repeatedly take the first remaining character from either word, preserving internal order in both.','Return the lexicographically largest possible complete merge.'],[(['cabaa','bcaaa'],'Comparing remaining suffixes at ties yields cbcabaaaaa.'),(['abcabc','abdcaba'],'The larger second suffix is chosen through the initial tie, producing abdcabcabcaba.')],[[*x] for x in [('cabaa','bcaaa'),('abcabc','abdcaba'),('a','b'),('b','a'),('a','a'),('aa','ab'),('ab','aa'),('zzz','zza'),('abc','xyz'),('same','same'),('gugu','gg'),('abab','abaa'),('x','xxxx'),('banana','band')]],MERGE,[MERGE.replace('word1[first:]>word2[second:]','word1[first]>word2[second]'),MERGE.replace('else:answer.append(word2[second]);second+=1','else:answer.append(word1[first]);first+=1')],['Compares only tied current characters instead of the remaining suffixes.','Takes from word one whenever it is not larger, reversing the greedy choice.'],merge_o,rmerge,L('When current characters tie, the larger remaining suffix determines which choice can produce the larger merge.','At each step compare word1[i:] and word2[j:] lexicographically.','Take the first character of the larger suffix, then append whichever suffix remains at exhaustion.','The choice maximizes the first position where the two possible continuations can differ, so it is greedily safe.'),'O((n+m)^2)','O(n+m)',5),
1755:E('closest_subsequence_sum_difference',[('nums','list[int]'),('goal','int')],'int',['meet-in-the-middle','binary-search'],['Choose any subsequence, including empty, and sum its elements.','Return the minimum absolute difference between such a sum and goal.'],[([[5,-7,3,5],6],'Subsequence [5,-7,3,5] sums to six, so the difference is zero.'),([[7,-9,15,-2],-5],'The closest subsequence sum differs from negative five by one.')],[[*x] for x in [([5,-7,3,5],6),([7,-9,15,-2],-5),([1],0),([1],2),([-1],-1),([1,2,3],7),([1,2,3],4),([-5,-2,7],1),([10,-10],3),([2,4,8],6),([-3,6,9],5),([0,0,1],0),([20,-7,-8,3],9),([1,-2,4,-8,16],11)]],CLOSEST,[CLOSEST.replace('for at in (index-1,index)','for at in (index,)'),CLOSEST.replace('result=[0]','result=[]')],['Checks only the insertion-side sum and misses the closest value immediately below it.','Omits the empty subset, preventing subset construction entirely.'],closest_o,rclosest,L('Splitting the array turns exponential search into two lists of about square-root size.','Enumerate subset sums of each half; for every left sum, binary-search the right sum nearest goal-left.','Check both lower-bound neighbors and retain the smallest absolute difference.','Every subsequence uniquely combines one subset from each half, and one of the two binary-search neighbors is its closest partner.'),'O(2^(n/2) log 2^(n/2))','O(2^(n/2))',8),
1758:E('minimum_alternating_changes',[('s','str')],'int',['strings','counting'],['s is a nonempty binary string.','Return the fewest character replacements needed to make adjacent characters alternate.'],[(['0100'],'Only the final zero must change to one, so one operation is enough.'),(['1111'],'Either alternating target differs in two positions.')],[[s] for s in ['0100','1111','0','1','01','10','00','11','010101','101010','000','111','001011','110100']],ALTERNATING,[ALTERNATING.replace('len(s)-mismatch','len(s)-mismatch+1'),ALTERNATING.replace('index%2','(index+1)%2')],['Adds one to the mismatch count for the opposite alternating pattern.','Computes the opposite pattern twice and never evaluates a zero-start pattern.'],alternating_o,ralternating,L('There are only two alternating strings of a fixed length, and their mismatch positions are complementary.','Count mismatches against 0101...; the other target has n-mismatch mismatches.','Return min(mismatch,n-mismatch).','Every valid alternating result is one of those two targets, so the smaller Hamming distance is optimal.'),'O(n)','O(1)',3),
}
BATCH[1758]['wrong'][1]=ALTERNATING.replace('return min(mismatch,len(s)-mismatch)','return mismatch')
BATCH[1758]['wrong_reasons'][1]='Checks only the zero-start alternating target and ignores the one-start target.'
