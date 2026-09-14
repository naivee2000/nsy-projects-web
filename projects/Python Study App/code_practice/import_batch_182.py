"""Subarray imbalance, achievable number, bounded jumps, dual arrays, and zero windows batch 182."""
from collections import deque
from functools import lru_cache
from .import_batch_055 import entry

def imbalance_oracle(a):
 nums=a[0];answer=0
 for i in range(len(nums)):
  for j in range(i+1,len(nums)+1):
   values=sorted(set(nums[i:j]));answer+=sum(y-x>1 for x,y in zip(values,values[1:]))
 return answer
def random_imbalance(r):return [[r.randint(1,12) for _ in range(r.randint(1,20))]]
def achievable_oracle(a):return max(a[0]+left-right for left in range(2*a[1]+1) for right in range(2*a[1]+1) if left+right==2*a[1])
def random_achievable(r):return [r.randint(-100,100),r.randint(0,50)]
def jumps_oracle(a):
 nums,target=a
 @lru_cache(None)
 def visit(i):
  if i==len(nums)-1:return 0
  values=[visit(j) for j in range(i+1,len(nums)) if abs(nums[j]-nums[i])<=target]
  return -10**6 if not values else 1+max(values)
 answer=visit(0);return -1 if answer<0 else answer
def random_jumps(r):return [[r.randint(-15,15) for _ in range(r.randint(2,14))],r.randint(0,12)]
def nondecreasing_oracle(a):
 first,second=a;n=len(first);answer=1
 for mask in range(1<<n):
  values=[second[i] if mask>>i&1 else first[i] for i in range(n)]
  for i in range(n):
   for j in range(i+1,n+1):
    if all(values[k]<=values[k+1] for k in range(i,j-1)):answer=max(answer,j-i)
 return answer
def random_nondecreasing(r):
 n=r.randint(1,10);return [[r.randint(0,15) for _ in range(n)],[r.randint(0,15) for _ in range(n)]]
def zero_oracle(a):
 nums,k=a;start=tuple(nums);queue=deque([start]);seen={start}
 while queue:
  values=queue.popleft()
  if not any(values):return True
  for i in range(len(values)-k+1):
   if all(values[j]>0 for j in range(i,i+k)):
    following=tuple(v-1 if i<=j<i+k else v for j,v in enumerate(values))
    if following not in seen:seen.add(following);queue.append(following)
 return False
def random_zero(r):
 n=r.randint(1,8);return [[r.randint(0,3) for _ in range(n)],r.randint(1,n)]

IMBALANCE='''\
def sum_subarray_imbalances(nums):
    answer=0
    for left in range(len(nums)):
        seen=set();components=0
        for right in range(left,len(nums)):
            value=nums[right]
            if value not in seen:
                components+=1-(value-1 in seen)-(value+1 in seen);seen.add(value)
            answer+=components-1
    return answer
'''
ACHIEVE='''\
def maximum_achievable_number(num,t):
    return num+2*t
'''
JUMPS='''\
def maximum_bounded_jumps(nums,target):
    dp=[-10**9]*len(nums);dp[0]=0
    for end in range(1,len(nums)):
        for start in range(end):
            if abs(nums[end]-nums[start])<=target:dp[end]=max(dp[end],dp[start]+1)
    return -1 if dp[-1]<0 else dp[-1]
'''
NONDEC='''\
def longest_dual_nondecreasing_subarray(nums1,nums2):
    first=second=answer=1
    for index in range(1,len(nums1)):
        old_first,old_second=first,second;first=second=1
        if nums1[index]>=nums1[index-1]:first=max(first,old_first+1)
        if nums1[index]>=nums2[index-1]:first=max(first,old_second+1)
        if nums2[index]>=nums1[index-1]:second=max(second,old_first+1)
        if nums2[index]>=nums2[index-1]:second=max(second,old_second+1)
        answer=max(answer,first,second)
    return answer
'''
ZERO='''\
def can_zero_with_length_k(nums,k):
    difference=[0]*(len(nums)+1);active=0
    for index,value in enumerate(nums):
        active+=difference[index];needed=value+active
        if needed<0:return False
        if needed:
            if index+k>len(nums):return False
            active-=needed;difference[index+k]+=needed
    return True
'''
BATCH={
2763:entry('sum_subarray_imbalances',[('nums','list[int]')],'int',['arrays','hash maps','enumeration'],['For each nonempty subarray, sort its distinct values.','Its imbalance is the number of adjacent sorted pairs whose difference exceeds one.','Return the sum of imbalance values over all subarrays.'],[([[2,3,1,4]],'Only selected subarrays contain a gap larger than one; their imbalance values sum to three.'),([[1,1]],'Every subarray has one distinct value, so the total is zero.')],[[x] for x in [[1],[1,1],[1,3],[2,3,1,4],[1,2,3],[3,1,2],[1,4,2],[5,1,5],[2,4,6],[1,3,3],[4,2,1,5],[7,7,1],[1,5,2,6],[3,8,4,1,7]]],IMBALANCE,[IMBALANCE.replace('components-1','components'),IMBALANCE.replace('value not in seen','value in seen')],['Counts connected value components instead of gaps between them.','Updates components only for duplicate values rather than new values.'],imbalance_oracle,random_imbalance,['For a fixed left endpoint, extend the right endpoint while tracking distinct values.','Distinct integers form consecutive components; imbalance equals components minus one.','A new value creates one component and merges with each present neighbor value-1 and value+1.','The component update exactly tracks gaps in sorted distinct values, so adding components-1 for every endpoint yields the required sum.'],'O(n²)','O(n)',8),
2769:entry('maximum_achievable_number',[('num','int'),('t','int')],'int',['math'],['In one operation, increase one of num and x by one while decreasing the other by one.','A number x is achievable if it can equal num after exactly t operations.','Return the maximum achievable x.'],[([4,1],'Start x at six; decreasing x and increasing num once makes both five.'),([3,2],'Starting x at seven allows the two values to meet after two operations.')],[[a,b] for a,b in [(0,0),(4,1),(3,2),(1,1),(-5,3),(10,0),(100,50),(7,7),(2,10),(-10,1),(999,2),(5,20),(42,4),(1,100)]],ACHIEVE,[ACHIEVE.replace('2*t','t'),ACHIEVE.replace('+2*t','-2*t')],['Accounts for only one side of each operation’s two-unit closing change.','Returns the minimum symmetric achievable value instead of the maximum.'],achievable_oracle,random_achievable,['To maximize x, begin above num.','Each operation can decrease x by one and increase num by one, closing a gap of two.','Therefore the largest initial x is num+2*t.','A larger gap cannot close in t steps, and this construction closes exactly the stated gap.'],'O(1)','O(1)',3),
2770:entry('maximum_bounded_jumps',[('nums','list[int]'),('target','int')],'int',['arrays','dynamic programming'],['Start at index zero and jump only to a larger index.','A jump i to j is allowed when abs(nums[j]-nums[i]) is at most target.','Return the maximum jumps reaching the final index, or -1 when unreachable.'],[([[1,3,6,4,1,2],2],'A longest valid route reaches the last index in three jumps.'),([[1,3,6,4,1,2],0],'No equal-value route reaches the final value two, so return -1.')],[[a,t] for a,t in [([1,2],1),([1,3],1),([1,3,6,4,1,2],2),([1,3,6,4,1,2],0),([1,1,1],0),([1,4,2,3],2),([5,1,5],0),([0,10,20],10),([3,2,1],1),([1,100,2],5),([-3,-1,-2],2),([7,7,8,7],0),([1,5,9,3],4),([2,8,4,10,6],3)]],JUMPS,[JUMPS.replace('<=target','<target'),JUMPS.replace('max(dp[end],dp[start]+1)','min(dp[end],dp[start]+1)')],['Treats the allowed difference equal to target as invalid.','Minimizes transitions from an unreachable sentinel rather than maximizing jumps.'],jumps_oracle,random_jumps,['Let dp[j] be the maximum jumps reaching j.','For every earlier reachable i satisfying the value bound, relax dp[j] with dp[i]+1.','Return the final state or -1 if it remains negative.','Every path to j has a unique preceding index i, so considering all earlier i exhausts and maximizes valid paths.'],'O(n²)','O(n)',5),
2771:entry('longest_dual_nondecreasing_subarray',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','dynamic programming'],['At each index choose either nums1[i] or nums2[i].','Find the longest contiguous index interval whose chosen values are nondecreasing.','Return that maximum length.'],[([[2,3,1],[1,2,1]],'Choosing 1,2 over the first two indices gives a nondecreasing interval of length two.'),([[1,3,2,1],[2,2,3,4]],'Choosing 1,2,2,4 across all indices gives length four.')],[[a,b] for a,b in [([1],[2]),([2,3,1],[1,2,1]),([1,3,2,1],[2,2,3,4]),([3,2],[1,4]),([5,4,3],[5,4,3]),([1,2,3],[3,2,1]),([2,2],[2,2]),([10,1,10],[1,10,1]),([1,5,2,6],[2,3,4,5]),([7,6,5,4],[1,2,3,4]),([0,0,1],[-1,1,1]),([4,1,3],[2,5,2]),([1,9,2,8],[3,4,5,6]),([8,2,7,3,6],[1,4,5,5,7])]],NONDEC,[NONDEC.replace('nums1[index]>=nums2[index-1]','nums1[index]>nums2[index-1]'),NONDEC.replace('old_first,old_second=first,second','old_first,old_second=first,first')],['Treats equality on a cross-array transition as decreasing.','Forgets the previous state ending with nums2.'],nondecreasing_oracle,random_nondecreasing,['Track two suffix lengths, ending with the choice from nums1 or nums2 at the current index.','Each new ending can extend either previous ending when its value is at least the chosen predecessor.','Compute four comparisons using saved prior states and keep the global maximum.','The ending choice and preceding ending choice are the only information needed to characterize every nondecreasing suffix.'],'O(n)','O(1)',5),
2772:entry('can_zero_with_length_k',[('nums','list[int]'),('k','int')],'bool',['arrays','greedy','difference arrays'],['An operation chooses k consecutive elements and decreases each by one.','Operations may be repeated but array values may never become negative.','Return whether all elements can become zero.'],[([[2,2,3,1,1,0],3],'Applying the forced operations from left to right reduces every entry exactly to zero.'),([[1,3,1,1],2],'The middle demand cannot be satisfied without making a neighboring value negative.')],[[a,k] for a,k in [([0],1),([3],1),([1,1],2),([1,0],2),([2,2,3,1,1,0],3),([1,3,1,1],2),([1,1,1],2),([2,2,2],3),([0,1,1],2),([1,1,0],2),([3,3,0],2),([1,2,2,1],2),([0,0,0],3),([2,3,3,2],2)]],ZERO,[ZERO.replace('needed<0','needed<=0'),ZERO.replace('index+k>len(nums)','index+k>=len(nums)')],['Rejects a position that already reaches exactly zero.','Rejects a valid final window ending exactly at the array boundary.'],zero_oracle,random_zero,['Scan left to right while tracking the active decrement contributed by earlier windows.','At each index, the remaining value forces exactly that many operations to begin there.','Schedule their expiration k positions later with a difference array; fail if negative or a needed window exceeds the boundary.','No later window can change an earlier index, so the forced greedy choice is necessary and, when all choices fit, sufficient.'],'O(n)','O(n)',5),
}
