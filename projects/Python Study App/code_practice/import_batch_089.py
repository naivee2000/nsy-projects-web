"""First half of batch 89: deterministic array, string, and sequence tasks."""
from collections import Counter
from math import gcd
from .import_batch_055 import entry


def minimum_pairs_oracle(a):
 arr=a[0];best=min(abs(arr[i]-arr[j]) for i in range(len(arr)) for j in range(i));return sorted([sorted([arr[i],arr[j]]) for i in range(len(arr)) for j in range(i) if abs(arr[i]-arr[j])==best])
def occurrences_oracle(a):
 values=list(Counter(a[0]).values());return len(values)==len(set(values))
def budget_oracle(a):
 s,t,b=a;return max([0]+[j-i for i in range(len(s)) for j in range(i+1,len(s)+1) if sum(abs(ord(s[k])-ord(t[k])) for k in range(i,j))<=b])
def remove_oracle(a):
 text,k=a
 while True:
  changed=False;out='';i=0
  while i<len(text):
   j=i+1
   while j<len(text) and text[j]==text[i]:j+=1
   if j-i>=k:out+=text[i]*((j-i)%k);changed=True
   else:out+=text[i:j]
   i=j
  if not changed:return out
  text=out
def intersection_oracle(a):return sorted(set(a[0])&set(a[1])&set(a[2]))
def chips_oracle(a):return min(sum((value-target)%2 for value in a[0]) for target in range(min(a[0]),max(a[0])+1))
def subsequence_oracle(a):
 arr,d=a;best=[1]*len(arr)
 for i in range(len(arr)):
  for j in range(i):
   if arr[i]-arr[j]==d:best[i]=max(best[i],best[j]+1)
 return max(best)
def balanced_oracle(a):
 balance=answer=0
 for char in a[0]:
  balance+=1 if char=='R' else -1
  if balance==0:answer+=1
 return answer
def progression_oracle(a):
 arr=a[0];step=(arr[-1]-arr[0])//len(arr)
 if step==0:return arr[0]
 expected=arr[0]
 for value in arr:
  if value!=expected:return expected
  expected+=step
 return expected
def line_oracle(a):
 points=a[0];dx=points[1][0]-points[0][0];dy=points[1][1]-points[0][1]
 return all((x-points[0][0])*dy==(y-points[0][1])*dx for x,y in points[2:])


def random_pairs(r):return [r.sample(range(-100,101),r.randint(2,20))]
def random_occurrences(r):return [[r.randint(-6,6) for _ in range(r.randint(1,40))]]
def random_budget(r):
 n=r.randint(1,18);return [''.join(r.choice('abcdef') for _ in range(n)),''.join(r.choice('abcdef') for _ in range(n)),r.randint(0,30)]
def random_remove(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,40))),r.randint(2,6)]
def random_intersection(r):return [sorted(r.sample(range(1,50),r.randint(1,15))) for _ in range(3)]
def random_chips(r):return [[r.randint(1,50) for _ in range(r.randint(1,30))]]
def random_subsequence(r):return [[r.randint(-15,15) for _ in range(r.randint(1,25))],r.randint(-6,6)]
def random_balanced(r):
 n=r.randint(1,20);chars=list('R'*n+'L'*n);r.shuffle(chars);return [''.join(chars)]
def random_progression(r):
 n=r.randint(3,15);start=r.randint(-30,30);step=r.choice([i for i in range(-8,9) if i]);full=[start+i*step for i in range(n+1)];full.pop(r.randint(1,n-1));return [full]
def random_line(r):
 x,y=r.randint(-10,10),r.randint(-10,10);dx,dy=r.randint(-4,4),r.randint(-4,4)
 if dx==dy==0:dx=1
 points=[[x+i*dx,y+i*dy] for i in range(r.randint(2,10))]
 if len(points)>2 and r.random()<.5:points[-1][r.randrange(2)]+=1
 r.shuffle(points);return [points]


PAIRS='''def minimum_absolute_pairs(arr):
 arr=sorted(arr);gap=min(b-a for a,b in zip(arr,arr[1:]));return [[a,b] for a,b in zip(arr,arr[1:]) if b-a==gap]
'''
OCCURRENCES='''def has_unique_occurrence_counts(arr):
 from collections import Counter
 counts=Counter(arr).values();return len(counts)==len(set(counts))
'''
BUDGET='''def longest_equal_substring_budget(s, t, max_cost):
 left=cost=best=0
 for right in range(len(s)):
  cost+=abs(ord(s[right])-ord(t[right]))
  while cost>max_cost:cost-=abs(ord(s[left])-ord(t[left]));left+=1
  best=max(best,right-left+1)
 return best
'''
REMOVE='''def remove_k_adjacent_duplicates(s, k):
 stack=[]
 for char in s:
  if stack and stack[-1][0]==char:stack[-1][1]+=1
  else:stack.append([char,1])
  if stack[-1][1]==k:stack.pop()
 return ''.join(char*count for char,count in stack)
'''
INTERSECTION='''def intersection_three_sorted(arr1, arr2, arr3):
 i=j=k=0;answer=[]
 while i<len(arr1) and j<len(arr2) and k<len(arr3):
  if arr1[i]==arr2[j]==arr3[k]:answer.append(arr1[i]);i+=1;j+=1;k+=1
  else:
   smallest=min(arr1[i],arr2[j],arr3[k]);i+=arr1[i]==smallest;j+=arr2[j]==smallest;k+=arr3[k]==smallest
 return answer
'''
CHIPS='''def minimum_chip_move_cost(position):
 even=sum(value%2==0 for value in position);return min(even,len(position)-even)
'''
SUBSEQUENCE='''def longest_fixed_difference_subsequence(arr, difference):
 best={};answer=0
 for value in arr:best[value]=best.get(value-difference,0)+1;answer=max(answer,best[value])
 return answer
'''
BALANCED='''def maximum_balanced_string_splits(s):
 balance=answer=0
 for char in s:
  balance+=1 if char=='R' else -1
  if balance==0:answer+=1
 return answer
'''
PROGRESSION='''def missing_arithmetic_value(arr):
 step=(arr[-1]-arr[0])//len(arr)
 if step==0:return arr[0]
 for left,right in zip(arr,arr[1:]):
  if right-left!=step:return left+step
 return arr[-1]+step
'''
LINE='''def points_form_straight_line(coordinates):
 x0,y0=coordinates[0];dx=coordinates[1][0]-x0;dy=coordinates[1][1]-y0
 return all((x-x0)*dy==(y-y0)*dx for x,y in coordinates[2:])
'''


E=entry
BATCH={
1200:E('minimum_absolute_pairs',[('arr','list[int]')],'list[list[int]]',['sorting','arrays'],['2 <= len(arr) <= 100000; values are distinct integers.','Return ascending pairs in ascending order.'],[([[4,2,1,3]],'After sorting, every adjacent gap is one, so all three neighboring pairs qualify.'),([[1,3,6,10,15]],'The unique minimum gap is two between one and three.')],[[x] for x in [[1,2],[-1,1],[1,10,20],[3,8,4,9],[0,-10,10],[-5,-4,-1,2],[100,50,51],[7,3,11,15],[1,5,9,13],[2,4,7,9],[10,1,6,11],[-20,-10,-9,0],[8,6,4,2],[42,0,-42]]],PAIRS,[PAIRS.replace('min(b-a','max(b-a'),PAIRS.replace('zip(arr,arr[1:])','zip(arr,arr[2:])')],['Selects the largest adjacent difference.','Compares values two positions apart and skips true neighbors.'],minimum_pairs_oracle,random_pairs,['Only adjacent values in sorted order can attain the global minimum difference.','Sort, compute the smallest neighboring gap, then collect every neighbor pair with that gap.','Emit pairs during a second neighboring scan.','Any nonadjacent sorted pair spans at least one neighboring gap and cannot be smaller than all of them.'],'O(n log n)','O(n)',3),
1207:E('has_unique_occurrence_counts',[('arr','list[int]')],'bool',['hash-maps','arrays'],['1 <= len(arr) <= 1000.','Return whether no two distinct values have the same frequency.'],[([[1,2,2,1,1,3]],'Frequencies three, two, and one are all distinct.'),([[1,2]],'Both values occur once, so the counts are not unique.')],[[x] for x in [[1],[1,1],[1,1,2],[1,2,2],[1,1,2,2],[3,3,3,2,2,1],[-1,-1,0],[0,0,0,1,1],[1,2,3],[5,5,4,4,4],[1,1,1,2,2,3,3,3,3],[-2,-2,-2,-1],[9,8,8,7,7,7],[4,4,4,4,3,3,2]]],OCCURRENCES,[OCCURRENCES.replace('len(counts)==len(set(counts))','len(counts)!=len(set(counts))'),'''def has_unique_occurrence_counts(arr):
 return len(arr)==len(set(arr))
'''],['Returns the opposite of the required uniqueness test.','Checks whether values are unique rather than whether their occurrence counts are unique.'],occurrences_oracle,random_occurrences,['Count each distinct value, then inspect the resulting frequencies.','Frequency values must themselves contain no duplicate.','Compare the number of frequencies with the size of their set.','Equal sizes mean every distinct input value has a different occurrence count.'],'O(n)','O(n)',3),
1208:E('longest_equal_substring_budget',[('s','str'),('t','str'),('max_cost','int')],'int',['sliding-window','strings'],['s and t have equal positive length; max_cost is nonnegative.','Changing position i costs abs(ord(s[i])-ord(t[i])).'],[(['abcd','bcdf',3],'Costs 1,1,1,2 allow the first three positions within budget three.'),(['abcd','cdef',3],'Every change costs two, so the longest affordable substring has length one.')],[[s,t,b] for s,t,b in [('a','a',0),('a','z',0),('a','z',25),('abc','abc',0),('abc','bcd',2),('abc','bcd',3),('abcd','bcdf',5),('krrgw','zjxss',19),('aaaa','zzzz',50),('xyz','abc',100),('azaz','zaza',25),('hello','ifmmp',4),('same','same',1),('budget','cvehfu',6)]],BUDGET,['''def longest_equal_substring_budget(s, t, max_cost):
 total=sum(abs(ord(a)-ord(b)) for a,b in zip(s,t))
 return len(s) if total<=max_cost else 0
''',BUDGET.replace('best=max(best','best=min(best')],['Tests only the whole strings and misses affordable proper substrings.','Keeps the shortest rather than longest affordable window.'],budget_oracle,random_budget,['Convert each aligned character pair into a nonnegative change cost.','A sliding window is valid while its cost sum is at most max_cost.','Add the right cost; repeatedly remove left costs while over budget; retain the maximum length.','Because costs are nonnegative, advancing left is the only way to restore an over-budget window.'],'O(n)','O(1)',5),
1209:E('remove_k_adjacent_duplicates',[('s','str'),('k','int')],'str',['stacks','strings'],['1 <= len(s) <= 100000; 2 <= k <= 10000.','Repeated removals may expose new adjacent groups.'],[(['abcd',2],'No adjacent character appears twice, so the string is unchanged.'),(['deeedbbcccbdaa',3],'Removing eee, ccc, bbb, and then ddd leaves aa.')],[[s,k] for s,k in [('a',2),('aa',2),('aaa',2),('aaaa',2),('abbaca',2),('pbbcggttciiippooaais',2),('yfttttfbbbbnnnnffbgffffgbbbbgssssgthyyyy',4),('aaaaa',3),('baaaab',4),('aabbbacd',3),('abcddcba',2),('xxxyyyxxx',3),('ababab',2),('cccbcccb',3)]],REMOVE,['''def remove_k_adjacent_duplicates(s, k):
 out=''
 for char in s:
  if out.endswith(char*k):out=out[:-k]
  out+=char
 return out
''',REMOVE.replace('if stack[-1][1]==k','if stack[-1][1]>k')],['Checks for a removable group before appending its final character.','Waits for k+1 copies, so exact groups of k remain.'],remove_oracle,random_remove,['A stack run stores one character and its current adjacent count.','Increment the top run for a match, otherwise push a new run.','Pop immediately when a run reaches k; later characters can then merge with the newly exposed top.','The stack always represents the fully reduced processed prefix.'],'O(n)','O(n)',5),
1213:E('intersection_three_sorted',[('arr1','list[int]'),('arr2','list[int]'),('arr3','list[int]')],'list[int]',['two-pointers','arrays'],['All three arrays are strictly increasing.','Return their common values in increasing order.'],[([[1,2,3,4,5],[1,2,5,7,9],[1,3,4,5,8]],'One and five appear in all three arrays.'),([[1,2],[3,4],[5,6]],'No value is shared by every array.')],[[a,b,c] for a,b,c in [([1],[1],[1]),([1],[1],[2]),([1,2],[2],[2,3]),([1,3,5],[1,3,5],[1,3,5]),([1,2,3],[2,3,4],[3,4,5]),([-3,-1,2],[-3,0,2],[-3,2]),([1,10],[1,5,10],[0,1,10]),([2,4,6],[1,2,3],[0,2,8]),([1,4,7],[2,5,8],[3,6,9]),([5],[1,5],[5,9]),([1,2,8],[2,4,8],[2,6,8]),([-2,-1],[-2,-1],[-1]),([3,6,9],[0,3,9],[3,9]),([1,100],[50,100],[99,100])]],INTERSECTION,[INTERSECTION.replace('smallest=min','smallest=max'),'''def intersection_three_sorted(arr1, arr2, arr3):
 return sorted(set(arr1)&set(arr2))
'''],['Advances the arrays holding the largest values instead of the smallest.','Intersects only the first two arrays and ignores the third.'],intersection_oracle,random_intersection,['Compare one current value from each sorted array.','On equality emit it and advance all three; otherwise advance every pointer at the minimum current value.','Stop when any array is exhausted.','A minimum value cannot match later values in the other arrays, so discarding it is safe.'],'O(n1+n2+n3)','O(1)',3),
1217:E('minimum_chip_move_cost',[('position','list[int]')],'int',['greedy','math'],['Positions are positive integers.','Moving by two costs zero and moving by one costs one.'],[([[1,2,3]],'Move chips at one and three together for free, then move the chip at two once.'),([[2,2,2,3,3]],'Moving the two odd-position chips to an even position costs two.')],[[x] for x in [[1],[2],[1,1],[1,2],[1,3],[2,4,6],[1,3,5],[1,2,4],[1,2,3,4],[10,20,30,41],[5,5,6,6,6],[100,1],[7,8,9,10,11],[2,2,3,3,4,4]]],CHIPS,[CHIPS.replace('min(even','max(even'),'''def minimum_chip_move_cost(position):
 return max(position)-min(position)
'''],['Moves the larger parity group instead of the smaller one.','Treats coordinate distance as cost even though two-step moves are free.'],chips_oracle,random_chips,['Free two-step moves collapse all even positions together and all odd positions together.','Only crossing from one parity to the other costs one per chip.','Count even and odd positions and move the smaller group.','Any common destination has one parity, so exactly the opposite-parity chips must pay once.'],'O(n)','O(1)',3),
1218:E('longest_fixed_difference_subsequence',[('arr','list[int]'),('difference','int')],'int',['dynamic-programming','hash-maps'],['1 <= len(arr) <= 100000.','The subsequence must preserve input order and every adjacent difference must equal difference.'],[([[1,2,3,4],1],'The full array is an arithmetic subsequence of length four.'),([[1,5,7,8,5,3,4,2,1],-2],'The subsequence 7,5,3,1 has length four.')],[[a,d] for a,d in [([1],0),([1,1],0),([1,2],0),([1,3,5],2),([5,3,1],-2),([1,2,4,6],2),([3,3,3],0),([1,4,7,2,5,8],3),([10,5,0,-5],-5),([1,2,3],-1),([2,4,2,4,6],2),([0,-1,-2,-3],-1),([5,1,5,1,5],0),([1,10,2,9,3,8],1)]],SUBSEQUENCE,[SUBSEQUENCE.replace('value-difference','value+difference'),SUBSEQUENCE.replace('+1','+0')],['Looks for a successor value rather than the required predecessor.','Fails to count the current element when extending a subsequence.'],subsequence_oracle,random_subsequence,['A subsequence ending at value x can extend the best earlier subsequence ending at x-difference.','Map each ending value to its best length so far.','Set best[x]=best.get(x-difference,0)+1 while scanning left to right.','The scan order enforces subsequence order and the map retains the strongest predecessor.'],'O(n)','O(n)',5),
1221:E('maximum_balanced_string_splits',[('s','str')],'int',['greedy','strings'],['s has equal total counts of L and R.','Split into the maximum number of nonempty balanced substrings.'],[(['RLRRLLRLRL'],'The running balance returns to zero four times.'),(['RLLLLRRRLR'],'The earliest zero balances create three substrings.')],[[s] for s in ['LR','RL','LLRR','RRLL','LRLR','RLRL','LLRRLR','RRLLRL','LLLRRR','RLRRLL','LRRLLR','RRRLLLRL','LRLRLRLR','LLLLRRRR']],BALANCED,[BALANCED.replace("if balance==0:answer+=1","if balance==1:answer+=1"),'''def maximum_balanced_string_splits(s):
 return 1
'''],['Cuts when the balance is one rather than when it returns to zero.','Assumes every balanced input is indivisible.'],balanced_oracle,random_balanced,['Represent R as +1 and L as -1.','A prefix is balanced exactly when the running sum returns to zero.','Cut greedily at every zero and count those returns.','Any balanced piece must end at a zero; taking the earliest such end cannot reduce later opportunities.'],'O(n)','O(1)',3),
1228:E('missing_arithmetic_value',[('arr','list[int]')],'int',['arrays','math'],['3 <= len(arr) <= 1000; arr is an arithmetic progression with one interior value removed.','The progression may increase, decrease, or be constant.'],[([[5,7,11,13]],'The common difference is two, so nine is missing between seven and eleven.'),([[15,13,12]],'The descending progression has step -1 and is missing fourteen.')],[[x] for x in [[1,3,7,9],[9,7,3,1],[0,0,0],[1,2,4],[4,2,1],[-5,-1,1],[-1,-3,-7],[10,20,40,50],[3,6,9,15],[100,90,80,60],[2,2,2,2],[1,6,11,21],[20,15,5,0],[-10,-5,5,10]]],PROGRESSION,[PROGRESSION.replace('//len(arr)','//(len(arr)-1)'),PROGRESSION.replace('return left+step','return right+step')],['Computes the observed-gap average instead of the original progression step.','Returns a value after the gap rather than the missing value inside it.'],progression_oracle,random_progression,['The original progression has len(arr)+1 terms, so its step is (last-first)/len(arr).','Scan adjacent values for the one gap that differs from the step.','Return left+step at that gap; constant progressions return their repeated value.','All intact gaps equal the true step, while the removed interior term doubles exactly one gap.'],'O(n)','O(1)',3),
1232:E('points_form_straight_line',[('coordinates','list[list[int]]')],'bool',['geometry','math'],['2 <= len(coordinates) <= 1000; points are distinct.','Avoid floating-point slopes and support vertical lines.'],[([[[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]]],'Every displacement is a multiple of direction (1,1).'),([[[1,1],[2,2],[3,4]]],'The final point has a different slope from the first two.')],[[p] for p in [[[0,0],[1,0]],[[0,0],[0,1],[0,2]],[[0,0],[1,1],[2,2]],[[0,0],[1,2],[2,4]],[[0,0],[1,2],[2,5]],[[1,1],[-1,-1],[2,2]],[[1,2],[3,2],[5,2]],[[2,3],[2,-1],[2,10]],[[1,1],[2,3],[3,5],[4,7]],[[1,1],[2,3],[4,6]],[[0,1],[2,3],[4,5]],[[5,5],[4,3],[3,1]],[[0,0],[-2,4],[-4,8]],[[1,0],[2,1],[3,3]]]],LINE,['''def points_form_straight_line(coordinates):
 return all(coordinates[i][1]-coordinates[i-1][1]==coordinates[1][1]-coordinates[0][1] for i in range(2,len(coordinates)))
''','''def points_form_straight_line(coordinates):
 if len(coordinates)<=3:return True
 x0,y0=coordinates[0];dx=coordinates[1][0]-x0;dy=coordinates[1][1]-y0
 return all((x-x0)*dy==(y-y0)*dx for x,y in coordinates[2:])
'''],['Compares only y increments and ignores x displacement.','Assumes every set of three points is collinear.'],line_oracle,random_line,['Two points define a direction vector (dx,dy).','A later displacement (x-x0,y-y0) is parallel exactly when its cross product with the direction is zero.','Check (x-x0)*dy == (y-y0)*dx for every point.','Integer cross multiplication handles vertical lines and avoids slope rounding.'],'O(n)','O(1)',3),
}
