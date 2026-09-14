"""Final reviewed group of workbook batch 114."""
from collections import Counter
from itertools import combinations
from .import_batch_055 import entry

def diff_o(a):
 nums,k=a;return sum(abs(nums[i]-nums[j])==k for i in range(len(nums)) for j in range(i+1,len(nums)))
def doubled_o(a):
 changed=a[0]
 if len(changed)%2:return []
 for choice in combinations(range(len(changed)),len(changed)//2):
  original=sorted(changed[i] for i in choice);left=Counter(changed)
  for x in original:left[x]-=1;left[2*x]-=1
  if all(v==0 for v in left.values()):return original
 return []
def taxi_o(a):
 n,rides=a;best=0
 for mask in range(1<<len(rides)):
  chosen=[rides[i] for i in range(len(rides)) if mask>>i&1];chosen.sort();end=earn=0;ok=True
  for s,e,t in chosen:
   if s<end:ok=False;break
   end=e;earn+=e-s+t
  if ok:best=max(best,earn)
 return best
def continuous_o(a):
 nums=a[0];n=len(nums);unique=set(nums);return min(n-sum(start<=x<start+n for x in unique) for start in unique)
def variable_o(a):return sum(1 if '+' in op else -1 for op in a[0])
def rdiff(r):return [[r.randint(-10,10) for _ in range(r.randint(1,30))],r.randint(0,10)]
def rdoubled(r):
 original=[r.randint(0,20) for _ in range(r.randint(1,7))];changed=original+[2*x for x in original];r.shuffle(changed);return [changed]
def rtaxi(r):
 n=r.randint(2,12);rides=[]
 for _ in range(r.randint(1,9)):
  s=r.randint(1,n-1);e=r.randint(s+1,n);rides.append([s,e,r.randint(0,10)])
 return [n,rides]
def rcontinuous(r):return [[r.randint(1,30) for _ in range(r.randint(1,10))]]
def rvariable(r):return [[r.choice(['++X','X++','--X','X--']) for _ in range(r.randint(1,100))]]

DIFF='''\
def count_pairs_with_difference(nums,k):
    counts={};answer=0
    for value in nums:
        answer+=counts.get(value-k,0)
        if k:answer+=counts.get(value+k,0)
        counts[value]=counts.get(value,0)+1
    return answer
'''
DOUBLED='''\
def original_from_doubled(changed):
    if len(changed)%2:return []
    counts=Counter(changed);answer=[]
    for value in sorted(counts,key=abs):
        if value==0:
            if counts[value]%2:return []
            answer.extend([0]*(counts[value]//2));counts[value]=0
            continue
        if counts[value]>counts[2*value]:return []
        amount=counts[value]
        answer.extend([value]*amount);counts[2*value]-=amount
    return answer if len(answer)*2==len(changed) else []
'''
TAXI='''\
def maximum_taxi_earnings(n,rides):
    rides.sort(key=lambda ride:ride[1]);ends=[];best=[0]
    from bisect import bisect_right
    for start,end,tip in rides:
        prior=bisect_right(ends,start)
        best.append(max(best[-1],best[prior]+end-start+tip));ends.append(end)
    return best[-1]
'''
CONT='''\
def minimum_operations_for_continuous_array(nums):
    n=len(nums);values=sorted(set(nums));left=answer=0
    best=0
    for right,value in enumerate(values):
        while value-values[left]>=n:left+=1
        best=max(best,right-left+1)
    return n-best
'''
VARIABLE='''\
def final_variable_value(operations):
    value=0
    for operation in operations:value+=1 if '+' in operation else -1
    return value
'''
def L(*x):return list(x)
BATCH={
2006:entry('count_pairs_with_difference',[('nums','list[int]'),('k','int')],'int',['arrays','hash maps','counting'],['nums has 1 through 200 integers and k is nonnegative.','Count index pairs i<j with absolute difference exactly k.','Duplicate values at different indices form distinct pairs.'],[([[1,2,2,1],1],'Each one pairs with each two, producing four index pairs.'),([[1,3],3],'Their difference is two, so no pair qualifies.')],[[x,k] for x,k in [([1],0),([1,1],0),([1,2],1),([1,2,2,1],1),([1,3],3),([3,2,1,5,4],2),([1,1,1],0),([0,0,1],1),([-1,1],2),([5,5,5,5],0),([1,4,7,10],3),([2,4,6,8],4),([10,1,9,2],8),([1,2,3,4,5],1)]],DIFF,[DIFF.replace("if k:answer+=counts.get(value+k,0)","answer+=counts.get(value+k,0)"),DIFF.replace('value-k','value-k-1')],['Double-counts equal-value pairs when k is zero.','Looks for a difference one larger than k on one side.'],diff_o,rdiff,L('When the later value arrives, count all earlier values exactly k away.','Maintain frequencies and query value-k and value+k, taking care not to query zero distance twice.','Add count[x-k], plus count[x+k] when k>0; then record x.','Every i<j pair is considered once at j, and the two queried values are exactly the solutions to |nums[i]-nums[j]|=k.'),'O(n)','O(n)',3),
2007:entry('original_from_doubled',[('changed','list[int]')],'list[int]',['arrays','sorting','hash maps'],['changed has even length up to 100000 and contains nonnegative integers.','It should be a shuffled original array together with twice every original value.','Return a valid original array, or [] when none exists.'],[([[1,3,4,2,6,8]],'Pair one with two, three with six, and four with eight, yielding [1,3,4].'),([[6,3,0,1]],'One has no matching two, so no original array exists.')],[[x] for x in [[],[0,0],[1,2],[1,3],[1,3,4,2,6,8],[6,3,0,1],[1,2,2,4],[0,0,0,0],[2,4,4,8],[4,2,8,1],[1,1,2,2],[3,6,9,18],[1,2,4,8],[5,10,5,10]]],DOUBLED,[DOUBLED.replace('key=abs','reverse=True'),DOUBLED.replace('counts[2*value]-=amount','counts[2*value]-=1')],['Processes large doubles before their smaller originals.','Consumes only one doubled copy even when several originals share a value.'],doubled_o,rdoubled,L('Smaller magnitudes must claim their doubles before those doubles can be treated as originals.','Count values and process in increasing absolute value, consuming the same number of doubled values.','For x in abs-sorted keys, require count[x]<=count[2x], append count[x] copies, subtract them from count[2x].','Every original occurrence needs one distinct double; magnitude order makes each forced pairing before a value can serve in the next scale.'),'O(n log n)','O(n)',5),
2008:entry('maximum_taxi_earnings',[('n','int'),('rides','list[list[int]]')],'int',['dynamic programming','binary search','intervals'],['Stops are numbered 1 through n; each ride [start,end,tip] has start<end.','The taxi moves only forward and can carry at most one passenger at a time.','A completed ride earns end-start+tip; maximize total earnings.'],[([5,[[2,5,4],[1,5,1]]],'Taking the ride from two to five earns seven, more than the other ride.'),([20,[[1,6,1],[3,10,2],[10,12,3],[11,12,2],[12,15,2],[13,18,1]]],'Compatible rides can be chained for maximum total earnings twenty.')],[[n,r] for n,r in [(2,[[1,2,0]]),(5,[[2,5,4],[1,5,1]]),(4,[[1,2,1],[2,4,1]]),(4,[[1,3,5],[2,4,5]]),(6,[[1,2,1],[2,3,1],[3,6,1]]),(10,[[1,10,0],[1,5,10],[5,10,10]]),(5,[[1,2,0],[1,3,0],[3,5,0]]),(7,[[2,3,5],[3,6,1],[1,7,0]]),(8,[[1,4,2],[4,8,2],[2,7,10]]),(6,[[1,3,1],[3,5,1],[5,6,1]]),(9,[[1,2,8],[2,9,0],[1,9,1]]),(5,[[4,5,100]]),(10,[[1,4,2],[4,6,3],[6,10,4]]),(6,[[1,6,5],[2,3,20]])]],TAXI,[TAXI.replace('bisect_right(ends,start)','bisect_right(ends,start-1)'),TAXI.replace('+tip','-tip')],['Rejects a ride ending exactly when the next ride begins.','Subtracts tips instead of adding them to fare earnings.'],taxi_o,rtaxi,L('This is weighted interval scheduling with compatibility at equal endpoints.','Sort by end; for each ride, binary-search how many earlier rides end by its start.','dp[i]=max(dp[i-1],dp[prior]+end-start+tip).','Every optimum either skips the current ride or takes it after an optimum compatible prefix, so the recurrence covers both exhaustive cases.'),'O(r log r)','O(r)',6),
2009:entry('minimum_operations_for_continuous_array',[('nums','list[int]')],'int',['sorting','sliding windows','sets'],['nums has 1 through 100000 positive integers.','One operation replaces any element; the final list must contain n distinct consecutive integers.','Return the minimum replacements required.'],[([[4,2,5,3]],'The values already form the consecutive set two through five, so zero operations are needed.'),([[1,2,3,5,6]],'Replacing one endpoint with four creates five consecutive distinct values, so one operation suffices.')],[[x] for x in [[1],[1,2],[1,1],[4,2,5,3],[1,2,3,5,6],[1,10,100,1000],[1,1,1,1],[8,5,9,9,8,4],[3,4,5,6],[10,12,11,14],[1,2,2,3],[100,101,103],[5,7,9,11],[2,3,4,10,11]]],CONT,[CONT.replace('sorted(set(nums))','sorted(nums)'),CONT.replace('>=n','>n')],['Keeps duplicates in the window even though final values must be distinct.','Allows a span of n, which needs n+1 distinct integer positions rather than n.'],continuous_o,rcontinuous,L('Keep the largest set of existing distinct values that fits inside some interval of n consecutive integers.','Sort unique values and use two pointers for windows with max-min<n.','best=max(right-left+1) while values[right]-values[left]<n; answer=n-best.','All kept values in such a window can remain while missing positions receive replacements, and no wider-span set can belong to one length-n consecutive target.'),'O(n log n)','O(n)',8),
2011:entry('final_variable_value',[('operations','list[str]')],'int',['arrays','simulation'],['operations has 1 through 100 strings, each one of ++X, X++, --X, or X--.','X starts at zero; increment operations add one and decrement operations subtract one.','Return X after applying operations in order.'],[([['--X','X++','X++']],'The changes are minus one, plus one, plus one, ending at one.'),([['++X','++X','X++']],'Three increments leave X equal to three.')],[[x] for x in [['++X'],['--X'],['X++'],['X--'],['--X','X++','X++'],['++X','++X','X++'],['++X','--X'],['X++','X--'],['--X','--X'],['++X','X++','--X'],['X--','X--','++X'],['++X']*10,['--X']*10,['++X','X--','X++','--X']]],VARIABLE,[VARIABLE.replace("'+' in operation","operation=='++X'"),VARIABLE.replace('value=0','value=1')],['Recognizes prefix increment but misses the postfix X++ form.','Starts X at one instead of zero.'],variable_o,rvariable,L('All four strings encode only the sign of a one-unit change.','Test whether the operation contains plus; otherwise it is a decrement.','Initialize zero and add +1 for plus operations or -1 for minus operations.','Applying the encoded change once per operation exactly simulates the variable, regardless of prefix or postfix notation.'),'O(n)','O(1)',3)
}
