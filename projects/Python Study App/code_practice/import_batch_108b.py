"""Second reviewed group of workbook batch 108."""
from itertools import permutations
from .import_batch_055 import entry
def replace_o(a):
 s=a[0];out=list(s)
 for index in range(1,len(out),2):out[index]=chr(ord(out[index-1])+int(out[index]))
 return ''.join(out)
def rearrange_o(a):
 best=0
 for order in set(permutations(a[0])):
  previous=0;valid=True
  for value in order:
   current=min(value,previous+1)
   if current<1:valid=False;break
   previous=current
  if valid:best=max(best,previous)
 return best
def distance_o(a):
 nums,target,start=a;return min(abs(index-start) for index,value in enumerate(nums) if value==target)
def split_o(a):
 s=a[0]
 def visit(index,previous,parts):
  if index==len(s):return parts>=2
  value=0
  for end in range(index,len(s)):
   value=value*10+int(s[end])
   if (previous is None or previous-value==1) and visit(end+1,value,parts+1):return True
  return False
 return visit(0,None,0)
def swaps_o(a):
 num,k=a;greater=sorted({''.join(value) for value in permutations(num) if ''.join(value)>num});target=greater[k-1];current=list(num);moves=0
 for index,wanted in enumerate(target):
  found=index
  while current[found]!=wanted:found+=1
  while found>index:current[found],current[found-1]=current[found-1],current[found];found-=1;moves+=1
 return moves
def rreplace(r):
 chars=[];count=r.randint(1,6)
 for index in range(count):
  letter=r.choice('abcdefghijklmnop');chars.append(letter)
  if index<count-1 or r.random()<.5:chars.append(str(r.randint(0,min(9,ord('z')-ord(letter)))))
 return [''.join(chars)]
def rrearrange(r):return [[r.randint(1,10) for _ in range(r.randint(1,7))]]
def rdistance(r):
 nums=[r.randint(0,7) for _ in range(r.randint(1,15))];target=r.choice(nums);return [nums,target,r.randrange(len(nums))]
def rsplit(r):return [''.join(r.choice('0123456789') for _ in range(r.randint(2,10)))]
def rswaps(r):
 while True:
  num=''.join(r.choice('01234') for _ in range(r.randint(2,7)));greater=sorted({''.join(value) for value in permutations(num) if ''.join(value)>num})
  if greater:return [num,r.randint(1,min(8,len(greater)))]
REPLACE='''def replace_digits_with_shifted_characters(s):
 chars=list(s)
 for index in range(1,len(chars),2):chars[index]=chr(ord(chars[index-1])+int(chars[index]))
 return ''.join(chars)
'''
REARRANGE='''def maximum_element_after_rearranging(arr):
 values=sorted(arr);current=0
 for value in values:current=min(value,current+1)
 return current
'''
DISTANCE='''def minimum_target_distance(nums, target, start):
 return min(abs(index-start) for index,value in enumerate(nums) if value==target)
'''
SPLIT='''def can_split_descending_consecutive(s):
 def search(index,previous,parts):
  if index==len(s):return parts>=2
  value=0
  for end in range(index,len(s)):
   value=value*10+int(s[end])
   if previous is None or value==previous-1:
    if search(end+1,value,parts+1):return True
   if previous is not None and value>=previous:break
  return False
 return search(0,None,0)
'''
SWAPS='''def minimum_swaps_to_kth_permutation(num, k):
 def advance(chars):
  pivot=len(chars)-2
  while chars[pivot]>=chars[pivot+1]:pivot-=1
  successor=len(chars)-1
  while chars[successor]<=chars[pivot]:successor-=1
  chars[pivot],chars[successor]=chars[successor],chars[pivot];chars[pivot+1:]=reversed(chars[pivot+1:])
 target=list(num)
 for _ in range(k):advance(target)
 current=list(num);moves=0
 for index,wanted in enumerate(target):
  found=index
  while current[found]!=wanted:found+=1
  while found>index:current[found],current[found-1]=current[found-1],current[found];found-=1;moves+=1
 return moves
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1844:E('replace_digits_with_shifted_characters',[('s','str')],'str',['strings'],['Even indices contain lowercase letters and odd indices contain digits.','Replace every digit by shifting its preceding letter forward that many alphabet positions; all shifts remain at most z.'],[(['a1c1e1'],'The digits shift a,c,e once to b,d,f, producing abcdef.'),(['a1b2c3d4e'],'The replacements are b,d,f,h, producing abbdcf d h e without spaces: abbfdh e.'.replace(' ',''))],[[s] for s in ['a','a0','a1','a1c1e1','x2','a9','m0n1','b2d3','p1q2r3','z0','c4e2','a1b2c3d4e','h5j1','q3s1']],REPLACE,[REPLACE.replace('ord(chars[index-1])','ord(chars[index-1])+1'),REPLACE.replace('int(chars[index])','0')],['Shifts every replacement one extra position.', 'Ignores the digit and leaves each replacement equal to its preceding letter.'],replace_o,rreplace,H('Each odd position depends only on the letter immediately before it.','Convert the string to a mutable list and visit odd indices.','Replace digit d with chr(ord(previous_letter)+int(d)).','The contract guarantees no shift exceeds z, and every digit is processed exactly once while letters remain unchanged.'),'O(n)','O(n)',3),
1846:E('maximum_element_after_rearranging',[('arr','list[int]')],'int',['arrays','sorting','greedy'],['You may reorder freely and decrease values while keeping them positive.','Afterward the first value must be one and adjacent differences at most one; maximize the largest value.'],[([[2,2,1,2,1]],'After sorting, the feasible sequence reaches maximum two.'),([[100,1,1000]],'Reorder and decrease to [1,2,3], reaching maximum three.')],[[x] for x in [[1],[2],[2,2,1,2,1],[100,1,1000],[1,2,3],[5,5,5],[3,1,3],[1,10],[2,3,4,5],[1,1,1],[4,2,7,1],[9,8,2],[2,2,2,2],[6,1,2,9]]],REARRANGE,[REARRANGE.replace('sorted(arr)','arr'),REARRANGE.replace('min(value,current+1)','max(value,current+1)')],['Uses the input order even though the optimal rearrangement requires sorting.', 'Increases values instead of respecting that values may only decrease.'],rearrange_o,rrearrange,H('Small values are the bottleneck for building a gradual sequence.', 'Sort ascending and maintain the greatest feasible current endpoint.', 'For each value, set current=min(value,current+1), starting from zero.', 'The next endpoint cannot exceed either its original value or one above the prior endpoint; sorting ensures this locally maximal choice cannot reduce future options.'),'O(n log n)','O(n)',5),
1848:E('minimum_target_distance',[('nums','list[int]'),('target','int'),('start','int')],'int',['arrays'],['target occurs at least once and start is a valid index.','Return the minimum absolute index distance from start to an occurrence of target.'],[([[1,2,3,4,5],5,3],'Target five is at index four, one step from start index three.'),([[1,1,1,1,1],1,0],'The start position already equals target, so distance is zero.')],[[*x] for x in [([1],1,0),([1,2,3,4,5],5,3),([1,1,1,1,1],1,0),([1,2,3],1,2),([1,2,3],3,0),([5,2,5],5,1),([0,1,0,1],1,2),([7,8,9,7],7,3),([2,4,6,8],4,3),([3,3,2],3,2),([9,1,9,1,9],9,2),([4,5,6],5,1),([1,0,2,0],0,0),([8,7,6,5],8,3)]],DISTANCE,[DISTANCE.replace('min(abs','max(abs'),DISTANCE.replace('==target','!=target')],['Returns the farthest occurrence instead of the nearest.', 'Measures positions whose value is not the target.'],distance_o,rdistance,H('Every occurrence is an independent candidate.', 'Scan indices whose value equals target and measure abs(index-start).','Return the minimum measured distance.', 'Absolute difference is exactly the number of index steps, and taking the minimum over every occurrence cannot miss the nearest one.'),'O(n)','O(1)',3),
1849:E('can_split_descending_consecutive',[('s','str')],'bool',['strings','backtracking','recursion'],['Split the entire digit string into at least two nonempty substrings; leading zeros are allowed.','Successive integer values must decrease by exactly one.'],[(['1234'],'No complete split forms values decreasing by exactly one.'),(['050043'],'The split 05,004,3 represents 5,4,3 and is valid.')],[[s] for s in ['10','21','1234','050043','9080701','10009998','0090089','54321','1110','9897','000','1098','10099','3210']],SPLIT,[SPLIT.replace('value==previous-1','value==previous+1'),SPLIT.replace('parts>=2','parts>=1')],['Searches for increasing rather than descending consecutive values.', 'Accepts the entire string as a one-part split.'],split_o,rsplit,H('Choose the first number length, then every later value is forced.', 'Use recursive backtracking that grows the next substring digit by digit.', 'Recurse only when the parsed value equals previous-1; require at least two parts at the end.', 'The recursion enumerates every possible boundary sequence, and the equality filter retains exactly descending consecutive numeric values, including leading-zero spellings.'),'O(2^n)','O(n) recursion',7),
1850:E('minimum_swaps_to_kth_permutation',[('num','str'),('k','int')],'int',['strings','two-pointers','greedy','permutations'],['The kth distinct lexicographically greater digit permutation is guaranteed to exist.','Return the minimum adjacent swaps needed to transform num into that target.'],[(['5489355142',4],'Advancing four permutations gives a target reachable in two adjacent swaps.'),(['11112',4],'The fourth greater permutation requires four adjacent swaps.')],[[*x] for x in [('12',1),('123',1),('123',2),('5489355142',4),('11112',4),('00123',1),('1123',2),('1234',5),('1023',2),('1223',3),('01234',4),('33421',1),('1243',2),('2314',3)]],SWAPS,[SWAPS.replace('for _ in range(k)','for _ in range(k-1)'),SWAPS.replace('moves+=1','moves+=2')],['Builds the previous greater permutation instead of the kth one.', 'Charges two swaps for each adjacent exchange.'],swaps_o,rswaps,H('First construct the kth next lexicographic permutation.', 'Then align target left-to-right; for each target digit, find its next matching occurrence in the current suffix.', 'Bubble that occurrence left with adjacent swaps and count each exchange.', 'Next-permutation produces the required target, while choosing the nearest matching occurrence preserves duplicate order and minimizes crossings, whose inversion count equals the minimum adjacent swaps.'),'O(k*n+n²)','O(n)',7),
}
