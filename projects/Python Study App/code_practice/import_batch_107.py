"""First reviewed group of workbook batch 107."""
from itertools import permutations
from math import gcd
from .import_batch_055 import entry
def difference_o(a):
 first,second=a;best=sum(abs(x-y) for x,y in zip(first,second))
 for index in range(len(first)):
  for replacement in first:best=min(best,sum(abs((replacement if i==index else first[i])-second[i]) for i in range(len(first))))
 return best%(10**9+7)
def gcds_o(a):
 nums=a[0];values=set()
 for mask in range(1,1<<len(nums)):
  value=0
  for index,item in enumerate(nums):
   if mask>>index&1:value=gcd(value,item)
  values.add(value)
 return len(values)
def invitations_o(a):
 grid=a[0];best=0
 for size in range(1,min(len(grid),len(grid[0]))+1):
  for girls in permutations(range(len(grid[0])),size):
   if any(all(grid[boys[i]][girls[i]] for i in range(size)) for boys in permutations(range(len(grid)),size)):best=size
 return best
def sign_o(a):
 product=1
 for value in a[0]:product*=value
 return (product>0)-(product<0)
def winner_o(a):
 n,k=a;friends=list(range(1,n+1));index=0
 while len(friends)>1:index=(index+k-1)%len(friends);friends.pop(index)
 return friends[0]
def rdifference(r):
 n=r.randint(1,8);return [[r.randint(1,30) for _ in range(n)],[r.randint(1,30) for _ in range(n)]]
def rgcds(r):return [[r.randint(1,30) for _ in range(r.randint(1,9))]]
def rinvitations(r):
 rows,columns=r.randint(1,5),r.randint(1,5)
 return [[[r.randint(0,1) for _ in range(columns)] for _ in range(rows)]]
def rsign(r):return [[r.randint(-8,8) for _ in range(r.randint(1,20))]]
def rwinner(r):return [r.randint(1,40),r.randint(1,30)]
DIFFERENCE='''def minimum_absolute_sum_difference(nums1, nums2):
 from bisect import bisect_left
 ordered=sorted(nums1);total=sum(abs(a-b) for a,b in zip(nums1,nums2));saving=0
 for original,target in zip(nums1,nums2):
  index=bisect_left(ordered,target);replacement=abs(original-target)
  if index<len(ordered):replacement=min(replacement,abs(ordered[index]-target))
  if index:replacement=min(replacement,abs(ordered[index-1]-target))
  saving=max(saving,abs(original-target)-replacement)
 return (total-saving)%(10**9+7)
'''
GCDS='''def count_subsequence_gcds(nums):
 from math import gcd
 present=set(nums);answer=0
 for candidate in range(1,max(nums)+1):
  common=0
  for multiple in range(candidate,max(nums)+1,candidate):
   if multiple in present:
    common=gcd(common,multiple)
    if common==candidate:answer+=1;break
 return answer
'''
INVITATIONS='''def maximum_accepted_invitations(grid):
 matched=[-1]*len(grid[0])
 def augment(boy,seen):
  for girl,allowed in enumerate(grid[boy]):
   if allowed and girl not in seen:
    seen.add(girl)
    if matched[girl]==-1 or augment(matched[girl],seen):matched[girl]=boy;return True
  return False
 return sum(augment(boy,set()) for boy in range(len(grid)))
'''
SIGN='''def product_sign(nums):
 sign=1
 for value in nums:
  if value==0:return 0
  if value<0:sign=-sign
 return sign
'''
WINNER='''def circular_game_winner(n, k):
 def solve(size):
  if size==1:return 0
  return (solve(size-1)+k)%size
 return solve(n)+1
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1818:E('minimum_absolute_sum_difference',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','binary-search','sorting'],['Arrays have equal positive length; one nums1 element may be replaced by any value already present in nums1.','Minimize the total absolute pairwise difference and return it modulo 1,000,000,007.'],[([[1,7,5],[2,3,5]],'Replacing seven by one or five reduces the sum to three.'),([[2,4,6,8,10],[2,4,6,8,10]],'The arrays already match, so no replacement is needed.')],[[*x] for x in [([1],[2]),([1],[1]),([1,7,5],[2,3,5]),([2,4,6,8,10],[2,4,6,8,10]),([1,10,4,4,2,7],[9,3,5,1,7,4]),([5,1],[1,5]),([1,100],[50,50]),([3,3,3],[1,2,4]),([1,2,3],[3,2,1]),([10,20,30],[12,18,40]),([4,8,12,16],[1,9,11,20]),([7,2,9],[5,5,5]),([1,5,9,13],[2,6,10,14]),([100,1,50],[2,99,49])]],DIFFERENCE,[DIFFERENCE.replace('saving=max(saving','saving=min(saving'),DIFFERENCE.replace('ordered=sorted(nums1)','ordered=sorted(nums2)')],['Tracks the smallest saving rather than the largest.', 'Chooses replacement values from nums2, which the operation forbids.'],difference_o,rdifference,H('For each target nums2 value, find the closest value available in nums1.','Sort a copy of nums1 and use binary search around every nums2 value.','Compute the largest reduction from replacing one original pair, then subtract it from the initial sum.','Only one index changes, so gains are independent; predecessor and successor around the insertion point are the closest legal replacements.'),'O(n log n)','O(n)',7),
1819:E('count_subsequence_gcds',[('nums','list[int]')],'int',['arrays','math','number-theory'],['Consider every nonempty subsequence and count distinct resulting greatest common divisors.','Values are positive integers.'],[([[6,10,3]],'The achievable GCD values are 1,2,3,6,10, giving five.'),([[5,15,40,5,6]],'The distinct subsequence GCDs total seven.')],[[x] for x in [[1],[2],[2,4],[6,10,3],[5,15,40,5,6],[3,6,9],[4,8,16],[2,3,5],[6,12,18,24],[7,14,21],[2,6,10,14],[9,15,25],[1,2,4],[12,18,30]]],GCDS,[GCDS.replace('common==candidate','common!=candidate'),GCDS.replace('range(1,max(nums)+1)','range(2,max(nums)+1)',1)],['Counts a candidate before its multiples have GCD equal to it.', 'Never considers GCD one.'],gcds_o,rgcds,H('A candidate g is achievable exactly when the GCD of all present multiples of g equals g.','Store input values in a set and scan multiples for each candidate.', 'Accumulate their GCD and stop as soon as it reaches the candidate.', 'Every subsequence producing g contains only multiples of g; conversely, the collected multiples themselves form a subsequence with GCD g when their common GCD reaches g.'),'O(max(nums)*log(max(nums)))','O(distinct nums)',8),
1820:E('maximum_accepted_invitations',[('grid','list[list[int]]')],'int',['graphs','matrix','bipartite-matching','recursion'],['grid[boy][girl] is one exactly when that invitation is possible.','Each boy and girl may participate in at most one accepted invitation; maximize the count.'],[([[[1,1,1],[1,0,1],[0,0,1]]],'A reassigned augmenting path matches all three boys.'),([[[1,0,1,0],[1,0,0,0],[0,0,1,0],[1,1,1,0]]],'At most three girls are reachable and all three can be matched.')],[[g] for g in [[[1]],[[0]],[[1,1]],[[1],[1]],[[1,0],[0,1]],[[0,1],[1,0]],[[1,1],[1,1]],[[1,1,1],[1,0,1],[0,0,1]],[[1,0,1,0],[1,0,0,0],[0,0,1,0],[1,1,1,0]],[[0,0],[0,0]],[[1,0,0],[1,1,0],[0,1,1]],[[1,1,0],[0,1,1]],[[1],[0],[1]],[[1,0,1],[0,1,0],[1,0,0]]]],INVITATIONS,[INVITATIONS.replace('matched[girl]==-1 or augment','matched[girl]==-1 and augment'),INVITATIONS.replace('return sum(augment','return max(augment')],['Refuses to reassign an already matched girl through an augmenting path.', 'Returns whether any one boy can match rather than the total matches.'],invitations_o,rinvitations,H('This is maximum bipartite matching between boys and girls.','For each boy, recursively search for an augmenting path, allowing a currently matched boy to move.','Use a fresh visited-girl set for each augmentation attempt.','Every successful augmentation increases matching size by one; when no path exists, the standard augmenting-path theorem proves the matching maximum.'),'O(boys²*girls)','O(boys+girls)',7),
1822:E('product_sign',[('nums','list[int]')],'int',['arrays','math'],['Return zero if any element is zero.','Otherwise return one for an even number of negative elements and negative one for an odd number.'],[([[-1,-2,-3,-4,3,2,1]],'Four negatives give a positive product sign.'),([[1,5,0,2,-3]],'The zero factor makes the product sign zero.')],[[x] for x in [[1],[-1],[0],[1,5,0,2,-3],[-1,-2,-3,-4,3,2,1],[-1,-2],[-1,-2,-3],[2,3,4],[-5,0],[0,0],[10,-2,3],[-1,1,-1,1],[7,-8,-9],[2,-3,4,-5,6]]],SIGN,[SIGN.replace('return 0','return 1'),SIGN.replace('sign=-sign','sign=sign')],['Treats a zero product as positive.', 'Ignores negative factors.'],sign_o,rsign,H('The magnitude of the product is irrelevant.', 'A zero fixes the answer at zero; every negative factor flips the sign.', 'Start at positive one and negate the state for each negative value.', 'Multiplication signs compose exactly by these flips, avoiding overflow from forming the full product.'),'O(n)','O(1)',3),
1823:E('circular_game_winner',[('n','int'),('k','int')],'int',['recursion','queues','math','simulation'],['Friends are labeled one through n and counting starts at friend one.','Remove every kth remaining friend clockwise until one winner remains.'],[([5,2],'Eliminating 2,4,1,5 leaves friend three.'),([6,5],'Following the circular eliminations leaves friend one.')],[[*x] for x in [(1,1),(2,1),(2,2),(3,2),(4,2),(5,2),(6,5),(5,1),(7,3),(10,2),(8,7),(12,4),(20,6),(40,17)]],WINNER,[WINNER.replace('+k)%size','+k-1)%size'),WINNER.replace('solve(n)+1','solve(n)')],['Uses the wrong rotation offset in the recurrence.', 'Returns the internal zero-based label.'],winner_o,rwinner,H('After one removal, the remaining game is the same problem with one fewer friend but rotated labels.','Let solve(size) return a zero-based winner; unwind with (previous+k) modulo size.','Use base case solve(1)=0, then convert the final result to one-based.', 'The recurrence exactly reverses the relabeling performed after each kth removal, so induction over circle size identifies the survivor.'),'O(n)','O(n) recursion',5),
}
