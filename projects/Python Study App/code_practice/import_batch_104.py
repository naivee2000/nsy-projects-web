"""Batch 104: trees, counting, prefix extrema, and two pointers."""
from collections import Counter,deque
from .import_batch_055 import entry
def distance_o(a):
 values,p,q=a;graph={};queue=deque();cursor=1
 if values and values[0] is not None:queue.append(0);graph[values[0]]=[]
 while queue and cursor<len(values):
  parent=queue.popleft()
  for _ in range(2):
   if cursor>=len(values):break
   if values[cursor] is not None:
    graph.setdefault(values[parent],[]).append(values[cursor]);graph.setdefault(values[cursor],[]).append(values[parent]);queue.append(cursor)
   cursor+=1
 todo=deque([(p,0)]);seen={p}
 while todo:
  node,d=todo.popleft()
  if node==q:return d
  for nxt in graph[node]:
   if nxt not in seen:seen.add(nxt);todo.append((nxt,d+1))
def balls_o(a):
 low,high=a;counts=Counter(sum(map(int,str(value))) for value in range(low,high+1));return max(counts.values())
def unique_o(a):return sum(value for value,count in Counter(a[0]).items() if count==1)
def absolute_o(a):
 nums=a[0];best=0
 for i in range(len(nums)):
  total=0
  for j in range(i,len(nums)):total+=nums[j];best=max(best,abs(total))
 return best
def trim_o(a):
 s=a[0];left=0;right=len(s)-1
 while left<right and s[left]==s[right]:
  char=s[left]
  while left<=right and s[left]==char:left+=1
  while left<=right and s[right]==char:right-=1
 return max(0,right-left+1)
def rdistance(r):
 n=r.randint(1,30);values=r.sample(range(-100,101),n);p,q=r.sample(values,2) if n>1 else (values[0],values[0]);return [values,p,q]
def rballs(r):
 low=r.randint(1,500);return [low,r.randint(low,min(1000,low+200))]
def runique(r):return [[r.randint(-10,10) for _ in range(r.randint(1,30))]]
def rabsolute(r):return [[r.randint(-20,20) for _ in range(r.randint(1,25))]]
def rtrim(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,30)))]
DISTANCE='''def binary_tree_value_distance(root, p, q):
 def path(node,target,route):
  if not node:return False
  route.append(node.val)
  if node.val==target:return True
  if path(node.left,target,route) or path(node.right,target,route):return True
  route.pop();return False
 first=[];second=[];path(root,p,first);path(root,q,second);common=0
 while common<min(len(first),len(second)) and first[common]==second[common]:common+=1
 return len(first)+len(second)-2*common
'''
BALLS='''def maximum_balls_in_box(low_limit, high_limit):
 counts={}
 for value in range(low_limit,high_limit+1):
  box=sum(int(digit) for digit in str(value));counts[box]=counts.get(box,0)+1
 return max(counts.values())
'''
UNIQUE='''def sum_unique_values(nums):
 counts=Counter(nums)
 return sum(value for value,count in counts.items() if count==1)
'''
ABSOLUTE='''def maximum_absolute_subarray_sum(nums):
 prefix=0;smallest=largest=0;answer=0
 for value in nums:
  prefix+=value;answer=max(answer,abs(prefix-smallest),abs(prefix-largest));smallest=min(smallest,prefix);largest=max(largest,prefix)
 return answer
'''
TRIM='''def minimum_length_after_matching_end_deletions(s):
 left,right=0,len(s)-1
 while left<right and s[left]==s[right]:
  char=s[left]
  while left<=right and s[left]==char:left+=1
  while left<=right and s[right]==char:right-=1
 return max(0,right-left+1)
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1740:E('binary_tree_value_distance',[('root','TreeNode | None'),('p','int'),('q','int')],'int',['trees','depth-first-search','lowest-common-ancestor'],['Tree node values are unique, and p and q are values present in the tree.','Return the number of edges on the shortest path between those two nodes.'],[([[3,5,1,6,2,0,8,None,None,7,4],5,0],'The path 5-3-1-0 contains three edges.'),([[3,5,1,6,2,0,8,None,None,7,4],5,7],'Five is the ancestor of seven through node two, so the distance is two.')],[[*x] for x in [([1],1,1),([1,2],1,2),([1,2,3],2,3),([1,2,3,4,5],4,3),([1,2,3,4,5,6,7],4,5),([1,2,3,4,5,6,7],4,7),([10,5,15,2,7,12,20],2,20),([0,-1,1,-2,None,None,2],-2,2),([3,5,1,6,2,0,8,None,None,7,4],5,0),([3,5,1,6,2,0,8,None,None,7,4],5,7),([8,4,12,2,6,10,14],6,10),([9,3,15,None,6,12,18],6,18),([5,4,None,3,None,2],5,2),([1,2,3,None,4,None,5],4,5)]],DISTANCE,[DISTANCE.replace('2*common','common'),DISTANCE.replace('route.pop();return False','return False')],['Subtracts only one copy of the common path and overcounts distance.','Does not backtrack failed path nodes, corrupting later root-to-node routes.'],distance_o,rdistance,L('Two root-to-node paths share exactly the route through their lowest common ancestor.','Find both value paths and count their common prefix.','Return len(path_p)+len(path_q)-2*common_prefix_length.','Removing the shared root-to-LCA edges from both paths leaves exactly the unique edge path between p and q.'),'O(n)','O(height)',5),
1742:E('maximum_balls_in_box',[('low_limit','int'),('high_limit','int')],'int',['math','counting'],['Put every integer in the inclusive range into the box numbered by its decimal digit sum.','Return the largest number of balls in any box.'],[([1,10],'Box one receives balls 1 and 10, so the maximum is two.'),([5,15],'Digit-sum boxes five and six each receive two balls, and no box receives more.')],[[*x] for x in [(1,10),(5,15),(1,1),(9,9),(9,10),(10,20),(19,28),(1,99),(90,100),(100,110),(500,550),(999,1000),(123,321),(1,1000)]],BALLS,[BALLS.replace('high_limit+1','high_limit'),BALLS.replace('sum(int(digit) for digit in str(value))','value%10')],['Treats high_limit as exclusive.','Uses only the final digit instead of the full digit sum.'],balls_o,rballs,L('Only a number’s digit sum determines its box.','Scan the inclusive interval and count each digit sum.','Compute the decimal digit sum, increment its frequency, then return the maximum frequency.','Every ball is assigned exactly once and the largest frequency is precisely the fullest box.'),'O(range*digits)','O(digits)',3),
1748:E('sum_unique_values',[('nums','list[int]')],'int',['arrays','hash-maps','counting'],['An element is unique only when it occurs exactly once in nums.','Return the sum of all unique element values.'],[([[1,2,3,2]],'Values one and three occur once, so their sum is four.'),([[1,1,1,1,1]],'No value is unique, so the sum is zero.')],[[x] for x in [[1,2,3,2],[1,1,1,1,1],[1],[1,2],[2,2],[-1,0,1],[0,0,1],[5,4,3,2,1],[3,3,2,2,1],[10,-10,10],[7,8,7,9],[1,2,2,3,3,4],[0],[4,4,5,6,6]]],UNIQUE,[UNIQUE.replace('count==1','count>=1'),UNIQUE.replace('value for value','count for value')],['Sums every distinct value even when it repeats.','Sums frequencies rather than the unique values themselves.'],unique_o,runique,L('Uniqueness depends on global frequency, not first appearance.','Count every value, then select entries with frequency one.','Return the sum of keys whose stored count equals one.','The frequency table exactly characterizes the requested values and each selected key contributes once.'),'O(n)','O(n)',3),
1749:E('maximum_absolute_subarray_sum',[('nums','list[int]')],'int',['arrays','prefix-sums','dynamic-programming'],['Choose any contiguous subarray; the empty subarray with sum zero is allowed.','Return the maximum absolute subarray sum.'],[([[1,-3,2,3,-4]],'Subarray [2,3] sums to five, the largest absolute value.'),([[2,-5,1,-4,3,-2]],'Subarray [-5,1,-4] sums to negative eight, giving absolute value eight.')],[[x] for x in [[1,-3,2,3,-4],[2,-5,1,-4,3,-2],[1],[-1],[0],[1,2,3],[-1,-2,-3],[5,-5],[3,-1,-2,4],[-10,1,1],[2,-1,2,-1,2],[0,0,0],[-2,5,-7,4],[10,-20,30,-40]]],ABSOLUTE,[ABSOLUTE.replace('abs(prefix-smallest),abs(prefix-largest)','abs(prefix-smallest)'),ABSOLUTE.replace('smallest=largest=0','smallest=largest=nums[0]')],['Tracks only the largest positive subarray sum and misses a larger negative magnitude.','Initializes prefix extrema from a value rather than the empty prefix zero.'],absolute_o,rabsolute,L('Any subarray sum is the difference between two prefix sums.','At each prefix, compare it with both the smallest and largest earlier prefix.','Update the answer with both absolute differences, then extend the prefix extrema.','The farthest earlier prefix produces the maximum absolute difference ending here; scanning all endpoints covers every subarray.'),'O(n)','O(1)',5),
1750:E('minimum_length_after_matching_end_deletions',[('s','str')],'int',['strings','two-pointers'],['In one operation, if both ends share a character, delete any positive prefix and suffix made only of that character without overlap.','Return the minimum remaining length after repeated operations.'],[(['ca'],'The end characters differ, so no deletion is possible and length two remains.'),(['cabaabac'],'Delete the outer c runs, then a runs, then b runs; nothing remains.')],[[s] for s in ['ca','cabaabac','a','aa','aba','abba','bbbb','aabccbaa','abcba','cabbaac','abca','ccabcc','aaccaa','abcddcba']],TRIM,[TRIM.replace('while left<right','if left<right',1),TRIM.replace('s[left]==s[right]','s[left]!=s[right]')],['Performs at most one outer-character deletion round.','Deletes when the endpoint characters differ instead of when they match.'],trim_o,rtrim,L('Whenever endpoints match, deleting their complete same-character runs can never reduce future options.','Use two pointers and repeatedly skip the shared character from both ends.','While left<right and endpoints match, remember the character and advance each pointer across its run.','Any legal operation removes subsets of those same outer runs; removing them fully reaches the same interior with no extra cost.'),'O(n)','O(1)',5),
}
BATCH[1740]['params'][0]=('root','TreeNode | None','treenode')
