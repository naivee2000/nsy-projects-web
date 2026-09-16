"""Reviewed array, string, counting, dynamic-programming, and greedy imports."""
from collections import Counter
from functools import lru_cache
from itertools import product
from math import gcd

from .import_batch_055 import entry

MOD = 1_000_000_007

def or_count_oracle(a):
 arr=a[0];return len({v for i in range(len(arr)) for j in range(i,len(arr)) for v in [__import__('functools').reduce(int.__or__,arr[i:j+1])]})
def orderly_oracle(a):
 s,k=a
 if k>1:return ''.join(sorted(s))
 return min(s[i:]+s[:i] for i in range(len(s)))
def digit_set_oracle(a):
 digits,n=a;allowed=set(digits)
 if n<=1000:return sum(set(str(x))<=allowed for x in range(1,n+1))
 from functools import lru_cache
 bound=str(n)
 @lru_cache(None)
 def count(position,tight,started):
  if position==len(bound):return int(started)
  limit=int(bound[position]) if tight else 9
  total=count(position+1,tight and limit==0,False) if not started else 0
  for character in digits:
   value=int(character)
   if value<=limit:
    total+=count(position+1,tight and value==limit,True)
  return total
 return count(0,True,False)
def fruit_oracle(a):
 f=a[0];best=0
 for i in range(len(f)):
  for j in range(i,len(f)):
   if len(set(f[i:j+1]))<=2:best=max(best,j-i+1)
 return best
def minimums_oracle(a):
 arr=a[0];return sum(min(arr[i:j+1]) for i in range(len(arr)) for j in range(i,len(arr)))%MOD
def range_one_oracle(a):
 nums,k=a
 # Reachable intervals for the original extremes close by 2k; interior values
 # can always be placed inside the remaining span.
 return max(max(nums)-k-(min(nums)+k),0)
def range_two_oracle(a):
 nums,k=a
 return min(max(v+d for v,d in zip(nums,ds))-min(v+d for v,d in zip(nums,ds)) for ds in product((-k,k),repeat=len(nums)))
def sort_oracle(a):return sorted(a[0])
def groups_oracle(a):
 counts=Counter(a[0]);return any(all(v%d==0 for v in counts.values()) for d in range(2,min(counts.values())+1))
def partition_oracle(a):
 x=a[0]
 return next(i for i in range(1,len(x)) if max(x[:i])<=min(x[i:]))
def subsets_oracle(a):
 words,requirements=a;need=Counter()
 for word in requirements:
  for c,n in Counter(word).items():need[c]=max(need[c],n)
 return [word for word in words if not (need-Counter(word))]
def reverse_letters_oracle(a):
 s=a[0];letters=iter(reversed([c for c in s if c.isalpha()]));return ''.join(next(letters) if c.isalpha() else c for c in s)
def additions_oracle(a):
 balance=missing=0
 for c in a[0]:
  if c=='(':balance+=1
  elif balance:balance-=1
  else:missing+=1
 return missing+balance
def three_sum_oracle(a):
 arr,target=a;return sum(arr[i]+arr[j]+arr[k]==target for i in range(len(arr)) for j in range(i+1,len(arr)) for k in range(j+1,len(arr)))%MOD
def long_press_oracle(a):
 name,typed=a
 def runs(text):
  out=[]
  for c in text:
   if out and out[-1][0]==c:out[-1][1]+=1
   else:out.append([c,1])
  return out
 expected,actual=runs(name),runs(typed)
 return len(expected)==len(actual) and all(c==d and have>=need for (c,need),(d,have) in zip(expected,actual))
def flips_oracle(a):
 s=a[0];return min(sum(c!='0' for c in s[:i])+sum(c!='1' for c in s[i:]) for i in range(len(s)+1))
def email_oracle(a):
 seen=set()
 for email in a[0]:
  local,domain=email.split('@');seen.add((local.split('+')[0].replace('.',''),domain))
 return len(seen)
def binary_sum_oracle(a):
 nums,goal=a;return sum(sum(nums[i:j])==goal for i in range(len(nums)) for j in range(i+1,len(nums)+1))
def falling_oracle(a):
 matrix=a[0];rows=len(matrix);cols=len(matrix[0])
 @lru_cache(None)
 def walk(r,c):return matrix[r][c] if r==rows-1 else matrix[r][c]+min(walk(r+1,nc) for nc in (c-1,c,c+1) if 0<=nc<cols)
 return min(walk(0,c) for c in range(cols))
def knight_oracle(a):
 n=a[0];moves=((4,6),(6,8),(7,9),(4,8),(0,3,9),(),(0,1,7),(2,6),(1,3),(2,4))
 @lru_cache(None)
 def ways(d,left):return 1 if left==1 else sum(ways(x,left-1) for x in moves[d])
 return sum(ways(d,n) for d in range(10))%MOD
def logs_oracle(a):
 logs=a[0];letters=[x for x in logs if not x.split(' ',1)[1][0].isdigit()];digits=[x for x in logs if x.split(' ',1)[1][0].isdigit()]
 return sorted(letters,key=lambda x:(x.split(' ',1)[1],x.split(' ',1)[0]))+digits
def range_bst_oracle(a):
 root,low,high=a;return sum(x for x in root if x is not None and low<=x<=high)

def random_arr(r):return [[r.randrange(16) for _ in range(r.randint(1,9))]]
def random_orderly(r):
 s=''.join(r.choice('abcde') for _ in range(r.randint(1,8)));return [s,r.randint(1,len(s))]
def random_digits(r):
 ds=sorted(r.sample(list('123456789'),r.randint(1,5)));return [ds,r.randint(1,300)]
def random_fruit(r):return [[r.randrange(5) for _ in range(r.randint(1,15))]]
def random_positive(r):return [[r.randint(1,20) for _ in range(r.randint(1,10))]]
def random_range(r):return [[r.randint(0,20) for _ in range(r.randint(1,7))],r.randint(0,8)]
def random_sort(r):return [[r.randint(-30,30) for _ in range(r.randint(1,15))]]
def random_deck(r):return [[r.randrange(6) for _ in range(r.randint(1,18))]]
def random_partition(r):
 left=sorted(r.sample(range(0,20),r.randint(1,5)));right=sorted(r.sample(range(21,50),r.randint(1,5)));x=left+right
 if r.random()<.5:r.shuffle(left);r.shuffle(right);x=left+right
 return [x]
def random_subsets(r):
 words=[''.join(r.choice('abcde') for _ in range(r.randint(1,7))) for _ in range(r.randint(1,8))];req=[''.join(r.choice('abcde') for _ in range(r.randint(1,3))) for _ in range(r.randint(1,4))];return [words,req]
def random_punct(r):return [''.join(r.choice('abcXYZ-_=!23') for _ in range(r.randint(1,20)))]
def random_parens(r):return [''.join(r.choice('()') for _ in range(r.randint(1,18)))]
def random_three(r):return [[r.randrange(8) for _ in range(r.randint(3,12))],r.randrange(20)]
def random_press(r):
 name=''.join(r.choice('abc') for _ in range(r.randint(1,8)));typed=''.join(c*r.randint(1,3) for c in name)
 if r.random()<.25:typed+=r.choice('xyz')
 return [name,typed]
def random_binary(r):return [''.join(r.choice('01') for _ in range(r.randint(1,20)))]
def random_emails(r):
 return [[f"{r.choice(['a.b','ab','a+b','x.y'])}{r.randint(0,2)}@{r.choice(['x.com','y.org'])}" for _ in range(r.randint(1,12))]]
def random_binary_sum(r):
 nums=[r.randrange(2) for _ in range(r.randint(1,18))];return [nums,r.randint(0,len(nums))]
def random_matrix(r):
 n=r.randint(1,6);return [[[r.randint(-9,15) for _ in range(n)] for _ in range(n)]]
def random_n(r):return [r.randint(1,20)]
def random_logs(r):
 out=[]
 for i in range(r.randint(1,10)):
  ident=f'id{i}'
  body=' '.join(str(r.randrange(10)) for _ in range(r.randint(1,4))) if r.random()<.4 else ' '.join(r.choice(('art','can','dog','own','kit','zero')) for _ in range(r.randint(1,4)))
  out.append(ident+' '+body)
 return [out]
def random_bst(r):
 values=sorted(r.sample(range(-30,31),r.randint(1,15)))
 def build(items,index=0):
  if not items:return None
  mid=len(items)//2;return (items[mid],build(items[:mid]),build(items[mid+1:]))
 tree=build(values);out=[];queue=[tree]
 while queue:
  node=queue.pop(0)
  if node is None:out.append(None)
  else:out.append(node[0]);queue.extend((node[1],node[2]))
 while out and out[-1] is None:out.pop()
 low,high=sorted((r.randint(-35,35),r.randint(-35,35)));return [out,low,high]

OR_REF='''def distinct_subarray_or_count(arr):
 current=set();answer=set()
 for value in arr:
  current={value|prior for prior in current}|{value};answer|=current
 return len(answer)
'''
ORDER_REF='''def smallest_orderly_queue(s, k):
 if k>1:return ''.join(sorted(s))
 return min(s[i:]+s[:i] for i in range(len(s)))
'''
DIGIT_REF='''def count_numbers_from_digits(digits, n):
 text=str(n);m=len(text);answer=sum(len(digits)**length for length in range(1,m))
 for i,c in enumerate(text):
  answer+=sum(d<c for d in digits)*len(digits)**(m-i-1)
  if c not in digits:return answer
 return answer+1
'''
FRUIT_REF='''def longest_two_fruit_window(fruits):
 counts={};left=best=0
 for right,value in enumerate(fruits):
  counts[value]=counts.get(value,0)+1
  while len(counts)>2:
   old=fruits[left];counts[old]-=1;left+=1
   if counts[old]==0:del counts[old]
  best=max(best,right-left+1)
 return best
'''
MINS_REF='''def sum_subarray_minimums(arr):
 arr=[-1]+arr+[-1];stack=[];answer=0
 for i,value in enumerate(arr):
  while stack and arr[stack[-1]]>value:
   j=stack.pop();answer+=arr[j]*(j-stack[-1])*(i-j)
  stack.append(i)
 return answer%1000000007
'''
RANGE1_REF='''def smallest_range_after_bounded_changes(nums, k):
 return max(0,max(nums)-min(nums)-2*k)
'''
RANGE2_REF='''def smallest_range_after_fixed_changes(nums, k):
 nums=sorted(nums);answer=nums[-1]-nums[0]
 for i in range(len(nums)-1):
  high=max(nums[-1]-k,nums[i]+k);low=min(nums[0]+k,nums[i+1]-k);answer=min(answer,high-low)
 return answer
'''
SORT_REF='''def merge_sort_numbers(nums):
 def sort(a):
  if len(a)<2:return a
  mid=len(a)//2;left=sort(a[:mid]);right=sort(a[mid:]);out=[];i=j=0
  while i<len(left) and j<len(right):
   if left[i]<=right[j]:out.append(left[i]);i+=1
   else:out.append(right[j]);j+=1
  return out+left[i:]+right[j:]
 return sort(nums)
'''
GROUP_REF='''def has_equal_card_groups(deck):
 from math import gcd
 from collections import Counter
 size=0
 for count in Counter(deck).values():size=gcd(size,count)
 return size>=2
'''
PART_REF='''def disjoint_partition_length(nums):
 left_max=global_max=nums[0];answer=1
 for i,value in enumerate(nums[1:],1):
  global_max=max(global_max,value)
  if value<left_max:answer=i+1;left_max=global_max
 return answer
'''
SUBSETS_REF='''def universal_words(words, requirements):
 from collections import Counter
 need=Counter()
 for req in requirements:
  for c,n in Counter(req).items():need[c]=max(need[c],n)
 return [word for word in words if not (need-Counter(word))]
'''
REVERSE_REF='''def reverse_only_letters(s):
 chars=list(s);left=0;right=len(chars)-1
 while left<right:
  if not chars[left].isalpha():left+=1
  elif not chars[right].isalpha():right-=1
  else:chars[left],chars[right]=chars[right],chars[left];left+=1;right-=1
 return ''.join(chars)
'''
ADD_REF='''def minimum_parentheses_additions(s):
 open_count=missing=0
 for c in s:
  if c=='(':open_count+=1
  elif open_count:open_count-=1
  else:missing+=1
 return missing+open_count
'''
THREE_REF='''def three_sum_multiplicity(arr, target):
 from collections import Counter
 count=Counter(arr);values=sorted(count);answer=0
 for i,x in enumerate(values):
  for y in values[i:]:
   z=target-x-y
   if z<y or z not in count:continue
   if x==y==z:answer+=count[x]*(count[x]-1)*(count[x]-2)//6
   elif x==y:answer+=count[x]*(count[x]-1)//2*count[z]
   elif y==z:answer+=count[x]*count[y]*(count[y]-1)//2
   else:answer+=count[x]*count[y]*count[z]
 return answer%1000000007
'''
PRESS_REF='''def is_long_pressed_name(name, typed):
 i=0
 for j,c in enumerate(typed):
  if i<len(name) and c==name[i]:i+=1
  elif j==0 or c!=typed[j-1]:return False
 return i==len(name)
'''
FLIP_REF='''def minimum_monotone_flips(s):
 ones=flips=0
 for c in s:
  if c=='1':ones+=1
  else:flips=min(flips+1,ones)
 return flips
'''
EMAIL_REF='''def unique_normalized_emails(emails):
 seen=set()
 for email in emails:
  local,domain=email.split('@');local=local.split('+')[0].replace('.','');seen.add(local+'@'+domain)
 return len(seen)
'''
BINARY_REF='''def binary_subarrays_with_sum(nums, goal):
 counts={0:1};prefix=answer=0
 for value in nums:
  prefix+=value;answer+=counts.get(prefix-goal,0);counts[prefix]=counts.get(prefix,0)+1
 return answer
'''
FALL_REF='''def minimum_falling_path_sum(matrix):
 dp=matrix[0][:]
 for row in matrix[1:]:dp=[value+min(dp[max(0,c-1):min(len(dp),c+2)]) for c,value in enumerate(row)]
 return min(dp)
'''
KNIGHT_REF='''def knight_dialer_count(n):
 moves=((4,6),(6,8),(7,9),(4,8),(0,3,9),(),(0,1,7),(2,6),(1,3),(2,4));dp=[1]*10
 for _ in range(n-1):dp=[sum(dp[x] for x in moves[d])%1000000007 for d in range(10)]
 return sum(dp)%1000000007
'''
LOGS_REF='''def reorder_log_files(logs):
 letters=[];digits=[]
 for log in logs:
  ident,body=log.split(' ',1)
  if body[0].isdigit():digits.append(log)
  else:letters.append((body,ident,log))
 letters.sort()
 return [log for _,_,log in letters]+digits
'''
BST_RANGE_REF='''def range_sum_bst(root, low, high):
 if root is None:return 0
 if root.val<low:return range_sum_bst(root.right,low,high)
 if root.val>high:return range_sum_bst(root.left,low,high)
 return root.val+range_sum_bst(root.left,low,high)+range_sum_bst(root.right,low,high)
'''

def lesson(a,b,c,d):return [a,b,c,d],d
def E(name,params,ret,topics,constraints,examples,bounds,ref,wrongs,reasons,oracle,gen,hints,time,space,diff):
 return entry(name,params,ret,topics,constraints,examples,bounds,ref,wrongs,reasons,oracle,gen,*lesson(*hints),time,space,diff)

BATCH={
898:E('distinct_subarray_or_count',[('arr','list[int]')],'int',['bit-manipulation','dynamic-programming'],['1 <= len(arr) <= 50,000; values are nonnegative.','Count distinct bitwise-OR results over all nonempty contiguous subarrays.'],[([[0]],'The only subarray has OR zero.'),([[1,1,2]],'The distinct results are 1, 2, and 3.')],[[x] for x in ([1],[2],[1,2],[3,1],[1,2,4],[0,0],[0,1,0],[7,7],[1,3,7],[8,4,2,1],[5,2,8],[15,0,1],[1,1,1,1],[2,5,6,1])],OR_REF,[OR_REF.replace('answer|=current','answer=current'),OR_REF.replace('{value|prior for prior in current}|{value}','{value}')],['Forgets results from earlier ending positions.','Counts only length-one subarrays.'],or_count_oracle,random_arr,['Many previous ORs collapse to the same value.','Keep the set of ORs ending at the previous index.','Form {value} union {old|value}, and add it to a global set.','Each subarray is represented when its right endpoint is processed.'],'O(n log value)','O(log value)',5),
899:E('smallest_orderly_queue',[('s','str'),('k','int')],'str',['strings','greedy'],['Move one of the first k characters to the end repeatedly.','Return the lexicographically smallest reachable string.'],[(['cba',1],'Only rotations are reachable; acb is smallest.'),(['baaca',3],'With k greater than one, any permutation is reachable, so aaabc is smallest.')],[[s,k] for s,k in [('a',1),('ba',1),('ba',2),('abc',1),('bca',1),('dcab',2),('aaaa',3),('zxy',1),('zxy',2),('cabca',1),('cabca',4),('leetcode',1),('leetcode',2),('bbaca',1)]],ORDER_REF,[ORDER_REF.replace("if k>1","if k>2"),ORDER_REF.replace("min(s[i:]+s[:i] for i in range(len(s)))","s")],['Fails to unlock permutations when k equals two.','Never considers rotations for k equals one.'],orderly_oracle,random_orderly,['The reachable set changes completely at k=2.','For k=1 test every rotation; for k>1 sort.','Return min rotation when k==1, otherwise sorted characters.','A second selectable position permits adjacent-order rearrangement and hence every permutation.'],'O(n^2)','O(n)',8),
902:E('count_numbers_from_digits',[('digits','list[str]'),('n','int')],'int',['dynamic-programming','math'],['digits are distinct and exclude zero; 1 <= n <= 10^9.','Count positive integers at most n using only the supplied digits.'],[([['1','3','5','7'],100],'There are four one-digit and sixteen two-digit valid numbers.'),([['1','4','9'],1_000_000_000],'Every length one through nine is allowed, totaling 29,523.')],[[d,n] for d,n in [(['1'],1),(['1'],10),(['2'],1),(['1','2'],2),(['1','2'],9),(['1','2'],10),(['1','2'],11),(['1','2'],12),(['3','5'],40),(['1','5','9'],200),(['7'],777),(['2','4','8'],999),(['1','3','5','7'],99),(['1','9'],1000)]],DIGIT_REF,[DIGIT_REF.replace('return answer+1','return answer'),DIGIT_REF.replace('d<c','d<=c')],['Excludes n when all its digits are allowed.','Double-counts an equal prefix digit as smaller.'],digit_set_oracle,random_digits,['Count shorter lengths before matching n digit by digit.','At each position count allowed digits smaller than n’s digit.','Add smaller-prefix completions; stop if the current digit is unavailable.','Every valid number is classified by length and then its first differing digit.'],'O(digits*log n)','O(1)',8),
904:E('longest_two_fruit_window',[('fruits','list[int]')],'int',['sliding-window','hash-maps'],['Choose a contiguous segment containing at most two fruit types.','Return its maximum length.'],[([[1,2,1]],'The whole length-three segment uses two types.'),([[0,1,2,2]],'The best segment is 1,2,2 of length three.')],[[x] for x in ([1],[1,1],[1,2],[1,2,3],[1,2,1,3],[0,1,2,2],[3,3,3],[1,2,3,2,2],[1,2,1,2,3],[0,1,0,2,0,2],[1,2,3,4],[4,3,4,3,2],[1,1,2,2,3,3],[0,0,1,2,2,2])],FRUIT_REF,[FRUIT_REF.replace('len(counts)>2','len(counts)>1'),FRUIT_REF.replace('left+=1','left+=2')],['Allows only one fruit type.','Moves the left edge by two and skips necessary removals.'],fruit_oracle,random_fruit,['This is a longest window with at most two distinct values.','Expand right and shrink left while three types are present.','Maintain frequency counts and delete zero-count types.','After shrinking, the current window is valid and is the longest valid one ending at right.'],'O(n)','O(1)',5),
907:E('sum_subarray_minimums',[('arr','list[int]')],'int',['monotonic-stack'],['1 <= len(arr) <= 30,000; values are positive.','Sum the minimum of every nonempty contiguous subarray modulo 1,000,000,007.'],[([[3,1,2,4]],'The ten subarray minima sum to 17.'),([[11,81,94,43,3]],'All subarray minimum contributions total 444.')],[[x] for x in ([1],[1,1],[1,2],[2,1],[3,1,2],[2,2,2],[5,4,3,2,1],[1,2,3,4,5],[2,1,2,1],[4,2,3,1],[10,1,10],[3,3,1,3],[6,2,5,4],[9,8,1,7,6])],MINS_REF,[MINS_REF.replace('return answer%1000000007','return min(arr)'),MINS_REF.replace('(j-stack[-1])*(i-j)','(i-j)')],['Returns only the smallest sentinel-augmented value.','Omits choices for the left boundary.'],minimums_oracle,random_positive,['Count how many subarrays choose each element as their representative minimum.','Use a monotonic stack to find its previous and next stopping boundaries.','On pop add value*leftChoices*rightChoices.','Tie direction assigns duplicate minima once, and every subarray has one assigned minimum.'],'O(n)','O(n)',5),
908:E('smallest_range_after_bounded_changes',[('nums','list[int]'),('k','int')],'int',['greedy','math'],['Each value may independently change by any amount from -k through k.','Return the smallest possible maximum-minus-minimum.'],[([[1],0],'A singleton always has range zero.'),([[0,10],2],'Moving inward by two at each end reduces the range to six.')],[[x,k] for x,k in [([1],5),([1,3],1),([1,3],2),([0,10],0),([0,10],5),([2,7,9],2),([5,5],3),([1,2,3],1),([10,20,30],4),([0,1],9),([4,8,15],3),([100,1,50],10),([3,9,12],4),([0,0,10],1)]],RANGE1_REF,[RANGE1_REF.replace('-2*k','-k'),RANGE1_REF.replace('max(0,','max(1,')],['Moves only one endpoint inward.','Never permits a zero range.'],range_one_oracle,random_range,['Only the original minimum and maximum constrain the final span.','Move both extremes toward one another by k.','Return max(0, originalRange-2k).','Every point’s reachable interval intersects any span between the adjusted extremes.'],'O(n)','O(1)',3),
910:E('smallest_range_after_fixed_changes',[('nums','list[int]'),('k','int')],'int',['sorting','greedy'],['Add exactly either k or -k to every value.','Return the minimum achievable range.'],[([[1],0],'A singleton has range zero.'),([[1,3,6],3],'Choose +3,-3,-3 to obtain 4,0,3 and range four.')],[[x,k] for x,k in [([1],5),([1,2],1),([1,5],2),([1,5],3),([1,3,6],0),([1,3,6],2),([0,10],5),([2,7,9],2),([5,5,5],3),([1,2,3,4],2),([10,20,30],7),([0,1,10],4),([4,8,15],5),([3,9,12,20],6)]],RANGE2_REF,[RANGE2_REF.replace('nums[i+1]-k','nums[i+1]+k'),RANGE2_REF.replace('answer=min(answer,high-low)','answer=max(answer,high-low)')],['Raises both sides of the split.','Maximizes candidate ranges instead of minimizing.'],range_two_oracle,random_range,['After sorting, an optimal assignment has one split: smaller values rise and larger values fall.','Enumerate every split and compute its new extremes.','high=max(last-k,nums[i]+k), low=min(first+k,nums[i+1]-k).','Any crossed choices can be swapped without increasing the range, yielding a single split.'],'O(n log n)','O(n)',5),
912:E('merge_sort_numbers',[('nums','list[int]')],'list[int]',['sorting','recursion'],['Return all integers in nondecreasing order.','Do not rely on bounded value ranges.'],[([[5,2,3,1]],'Sorting yields 1,2,3,5.'),([[5,1,1,2,0,0]],'Duplicates are retained in nondecreasing order.')],[[x] for x in ([1],[2,1],[1,2],[-1,0,1],[3,3,2],[5,4,3,2,1],[0,0,0],[10,-10,5,-5],[2,1,2,1],[9,1,8,2,7,3],[100,-100],[4,6,5,1,3,2],[1,-1,1,-1],[7,0,7,0,3])],SORT_REF,[SORT_REF.replace('left[i]<=right[j]','left[i]>=right[j]'),SORT_REF.replace('return sort(nums)','return nums')],['Merges in descending order.','Returns the input unchanged.'],sort_oracle,random_sort,['Divide until lists have at most one element.','Recursively sort both halves, then merge their smallest fronts.','Append the smaller head until one half is exhausted, then append the remainder.','Induction proves each returned half and their merge are sorted and complete.'],'O(n log n)','O(n)',5),
914:E('has_equal_card_groups',[('deck','list[int]')],'bool',['hash-maps','math'],['Partition the entire deck into groups of equal size at least two.','Every group must contain one repeated card value.'],[([[1,2,3,4,4,3,2,1]],'Each value can form a pair.'),([[1,1,1,2,2,2,3,3]],'Counts 3,3,2 have greatest common divisor one.')],[[x] for x in ([1],[1,1],[1,2],[1,1,1],[1,1,2,2],[1,1,1,2,2,2],[1,1,1,1,2,2],[0,0,0,0],[1,2,3,4],[1,1,2,2,3,3],[5,5,5,5,5,5],[1,1,1,1,2,2,2,2],[1,1,1,2,2,2,3,3,3],[0,0,1,1,1,1])],GROUP_REF,[GROUP_REF.replace('return size>=2','return min(Counter(deck).values())>=2'),GROUP_REF.replace('size=gcd(size,count)','size=count')],['Checks only that every value appears twice, ignoring a common group size.','Keeps only the last count.'],groups_oracle,random_deck,['A valid group size must divide every value frequency.','Compute the greatest common divisor of all counts.','Return whether that gcd is at least two.','Every common divisor creates equal pure groups, and any valid size is such a divisor.'],'O(n)','O(distinct values)',3),
915:E('disjoint_partition_length',[('nums','list[int]')],'int',['arrays','greedy'],['A valid split exists with nonempty left and right parts.','Return the smallest left length where every left value is at most every right value.'],[([[5,0,3,8,6]],'The first three values have maximum five, no greater than the remaining minimum six.'),([[1,1,1,0,6,12]],'The smallest valid left part ends after the zero, at length four.')],[[x] for x in ([1,2],[2,1,3],[1,2,3],[3,1,2,4],[5,0,3,8,6],[1,1,0,2],[0,0,1],[10,1,2,20],[2,2,2,3],[4,3,2,1,5],[1,5,2,6],[7,3,5,8,9],[0,5,4,6],[9,0,10,11])],PART_REF,[PART_REF.replace('value<left_max','value<=left_max'),PART_REF.replace('return answer','return 1')],['Extends the left side unnecessarily on equality.','Always splits after the first value.'],partition_oracle,random_partition,['Track the maximum committed to the left and the maximum seen overall.','When a new value is below left_max, the split must move past it.','Set answer=i+1 and promote left_max to global_max.','Each violation forces inclusion; otherwise all later values seen remain at least the committed maximum.'],'O(n)','O(1)',5),
916:E('universal_words',[('words1','list[str]'),('words2','list[str]')],'list[str]',['hash-maps','strings'],['A word is universal when it contains every requirement with multiplicity.','Return universal words in input order.'],[([['amazon','apple','facebook','google','leetcode'],['e','o']],'Facebook, google, and leetcode contain both required letters.'),([['amazon','apple','facebook','google','leetcode'],['e','oo']],'Google is the only word containing e and two o characters.')],[[w,b] for w,b in [(['a'],['a']),(['a'],['b']),(['ab','ba'],['a']),(['abc','abb'],['ab']),(['abc','abb'],['bb']),(['aaaa','aa'],['aa']),(['cat','taco'],['ca']),(['google','leetcode'],['eo']),(['foo','food'],['oo']),(['xyz','xxyyzz'],['xyz']),(['hello','world'],['ll']),(['abcde','edcba'],['a','e']),(['mississippi'],['issi']),(['aaa','bbb','abab'],['ab'])]],SUBSETS_REF,[SUBSETS_REF.replace('max(need[c],n)','need[c]+n'),SUBSETS_REF.replace('not (need-Counter(word))','set(need)<=set(word)')],['Adds requirements instead of taking their maximum multiplicity.','Ignores repeated required letters.'],subsets_oracle,random_subsets,['Combine all requirement words into one maximum-frequency demand.','A candidate passes when its count for every character meets that demand.','Build need[c]=max frequency across requirements, then filter candidates.','Meeting the coordinate-wise maximum is equivalent to meeting every individual requirement.'],'O(total characters)','O(alphabet)',5),
917:E('reverse_only_letters',[('s','str')],'str',['strings','two-pointers'],['Reverse only alphabetic characters.','Every nonletter must remain at its original index.'],[(['ab-cd'],'Letters reverse to dcba while the hyphen stays fixed: dc-ba.'),(['a-bC-dEf-ghIj'],'Reversing just letters produces j-Ih-gfE-dCba.')],[[s] for s in ['a','-','ab','a-b','1a2b3','Test1ng-Leet=code-Q!','---abc','abc---','A1b2C','a_b_c','123','Z-y-X','ab!!cd','x=Y-z']],REVERSE_REF,[REVERSE_REF.replace('isalpha()','isalnum()'),REVERSE_REF.replace('chars[left],chars[right]=chars[right],chars[left]','chars[left]=chars[right]')],['Treats digits as letters and moves them.','Overwrites one side instead of swapping.'],reverse_letters_oracle,random_punct,['Nonletters are fixed barriers only in the output positions, not in letter order.','Use pointers to find the next letter from each side.','Skip nonletters; swap two letters; move both pointers.','Each swap places the next required reversed letters without touching fixed characters.'],'O(n)','O(n)',3),
921:E('minimum_parentheses_additions',[('s','str')],'int',['strings','stacks'],['Insert the fewest parentheses so the result is valid.','Return only the number of insertions.'],[(['())'],'One opening parenthesis remains unmatched, so one closing insertion is needed.'),(['((('],'Three closing parentheses are needed.')],[[s] for s in ['(',')','()','(())','())','(()',')))','(((','())(','()()','))((','(()))(','(()())','())(()','((((()))','())())']],ADD_REF,[ADD_REF.replace('missing+open_count','missing'),ADD_REF.replace("elif open_count:open_count-=1","elif open_count:open_count+=1")],['Counts missing openings but forgets unmatched openings.','Increases rather than closes an available opening.'],additions_oracle,random_parens,['A closing parenthesis either consumes an open one or requires an inserted opening.','Track unmatched openings and missing openings.','Increment on (, decrement when possible on ), otherwise increment missing; return both counts.','The two unmatched categories require independent insertions and every insertion fixes one.'],'O(n)','O(1)',3),
923:E('three_sum_multiplicity',[('arr','list[int]'),('target','int')],'int',['counting','combinatorics'],['Count index triples i<j<k whose values sum to target.','Return the count modulo 1,000,000,007.'],[([[1,1,2,2,3,3,4,4,5,5],8],'Accounting for repeated value choices gives twenty index triples.'),([[1,1,2,2,2,2],5],'Choose two ones and one of four twos, giving twelve triples.')],[[x,t] for x,t in [([0,0,0],0),([1,2,3],6),([1,2,3],7),([1,1,1,1],3),([1,1,2,2],4),([0,1,2,3],3),([2,2,2,3,3],7),([1,2,2,2,3],6),([0,0,1,1,2],2),([5,5,5],15),([1,3,3,3,5],7),([0,2,4,6,8],12),([1,1,2,3,4],6),([7,0,7,0,7],14)]],THREE_REF,[THREE_REF.replace('//6','//3'),THREE_REF.replace('for y in values[i:]','for y in values')],['Uses the wrong combination divisor for three equal values.','Counts value orders more than once.'],three_sum_oracle,random_three,['Group triples by their ordered values x<=y<=z.','Use frequencies and the appropriate combination formula for equality cases.','Enumerate x,y and derive z; add C(cx,3), C(cx,2)cz, cxC(cy,2), or cxc ycz.','Each index triple has exactly one sorted value pattern and multiplicities count its index choices.'],'O(v^2)','O(v)',5),
925:E('is_long_pressed_name',[('name','str'),('typed','str')],'bool',['strings','two-pointers'],['Typed may repeat a key character beyond its occurrences in name.','Return whether typed can result from long-pressing name.'],[(['alex','aaleex'],'Extra a and e characters are valid long presses.'),(['saeed','ssaaedd'],'The e run is too short, so the typed text is invalid.')],[[a,b] for a,b in [('a','a'),('a','aa'),('aa','a'),('ab','aab'),('ab','abb'),('ab','ac'),('alex','alex'),('leelee','lleeelee'),('vtkgn','vttkgnn'),('pyplrz','ppyypllr'),('abc','aaabbbccc'),('abc','abccx'),('aaa','aaaa'),('aab','aaab')]],PRESS_REF,[PRESS_REF.replace("elif j==0 or c!=typed[j-1]:return False","else:return False"),PRESS_REF.replace('return i==len(name)','return True')],['Rejects all legitimate repeated typed characters.','Accepts typed strings that never finish the name.'],long_press_oracle,random_press,['Each typed character must match the next name character or repeat the prior typed character.','Advance the name pointer on direct matches; otherwise require a long press.','Reject an unmatched new character and finally require every name character consumed.','The scan assigns each typed character to its only possible original or repeated role.'],'O(len(name)+len(typed))','O(1)',3),
926:E('minimum_monotone_flips',[('s','str')],'int',['dynamic-programming','strings'],['Flip individual bits so the result is nondecreasing: some zeros followed by some ones.','Return the minimum flips.'],[(['00110'],'Flipping the final zero gives 00111 with one change.'),(['010110'],'Two flips are sufficient, for example producing 011111.')],[[s] for s in ['0','1','01','10','00','11','001','110','101','010','000111','111000','00110','010110','00011000','101010']],FLIP_REF,[FLIP_REF.replace('min(flips+1,ones)','flips+1'),FLIP_REF.replace("if c=='1':ones+=1","if c=='0':ones+=1")],['Always flips zeros after any one and misses cheaper earlier-one flips.','Counts zeros as the prefix ones that could be flipped.'],flips_oracle,random_binary,['At each position track ones seen and best flips for a monotone prefix.','A zero is either flipped, or all previous ones are flipped.','For zero set flips=min(flips+1,ones); for one increment ones.','These are the only ways a monotone prefix can end after a zero.'],'O(n)','O(1)',5),
929:E('unique_normalized_emails',[('emails','list[str]')],'int',['hash-maps','strings'],['In the local part, dots are ignored and text after the first plus is ignored.','The domain is unchanged; count distinct delivered addresses.'],[([['test.email+alex@leetcode.com','test.e.mail+bob.cathy@leetcode.com','testemail+david@lee.tcode.com']],'The first two normalize together; the third has a different domain, giving two.'),([['a@leetcode.com','b@leetcode.com','c@leetcode.com']],'The three distinct local parts remain distinct.')],[[x] for x in [['a@x.com'],['a.b@x.com','ab@x.com'],['a+b@x.com','a@x.com'],['a@x.com','a@y.com'],['a.b+c@x.com','ab+d@x.com'],['x+y+z@d.com'],['a.@x.com','.a@x.com'],['abc@x.com','abd@x.com'],['a+b@x.com','a+b@y.com'],['first.last@x.com','firstlast@x.com'],['x@a.com','x@b.com'],['a+z@x.com','a.q@x.com'],['m.n+tag@site.org','mn@site.org'],['a@x.com','a@x.com']]],EMAIL_REF,[EMAIL_REF.replace(".replace('.','')",''),EMAIL_REF.replace("local.split('+')[0]","local")],['Keeps dots in the local part.','Keeps ignored plus suffixes.'],email_oracle,random_emails,['Normalize only the local portion; domain rules are different.','Split at @, truncate local at +, remove local dots, then reattach domain.','Insert each normalized address into a set.','Exactly addresses with the same normalized local and identical domain share delivery.'],'O(total characters)','O(total characters)',3),
930:E('binary_subarrays_with_sum',[('nums','list[int]'),('goal','int')],'int',['prefix-sums','hash-maps'],['nums contains only zero and one.','Count nonempty contiguous subarrays whose sum equals goal.'],[([[1,0,1,0,1],2],'Four contiguous subarrays contain exactly two ones.'),([[0,0,0,0,0],0],'All fifteen nonempty subarrays sum to zero.')],[[x,g] for x,g in [([0],0),([1],0),([1],1),([0,0],0),([1,1],1),([1,1],2),([1,0,1],1),([0,1,0],1),([1,0,0,1],1),([1,0,1,0,1],3),([0,0,1,0],0),([1,1,0,1],2),([0,1,1,0,1],2),([1,0,0,0,1],0)]],BINARY_REF,[BINARY_REF.replace('{0:1}','{}'),BINARY_REF.replace('prefix-goal','goal-prefix')],['Omits the empty prefix and loses subarrays starting at zero.','Looks up the prefix difference with the wrong sign.'],binary_sum_oracle,random_binary_sum,['A subarray sum is the difference of two prefix sums.','Count how often each earlier prefix has occurred.','At current prefix p add count[p-goal], then record p; seed count[0]=1.','Every matching earlier prefix identifies one unique ending-at-current subarray.'],'O(n)','O(n)',5),
931:E('minimum_falling_path_sum',[('matrix','list[list[int]]')],'int',['dynamic-programming','matrices'],['From each row move down-left, down, or down-right.','Return the minimum sum from the first row through the last.'],[([[[2,1,3],[6,5,4],[7,8,9]]],'The path 1,5,7 has sum thirteen.'),([[[-19,57],[-40,-5]]],'The path -19,-40 has sum -59.')],[[m] for m in [[[1]],[[1,2],[3,4]],[[2,1],[3,4]],[[-1,-2],[-3,-4]],[[1,9,1],[9,1,9],[1,9,1]],[[5,5],[5,5]],[[1,2,3],[4,5,6],[7,8,9]],[[9,8,7],[6,5,4],[3,2,1]],[[0,0],[0,0]],[[10,-10],[20,-20]],[[3,1,2],[4,8,1],[9,2,7]],[[1,100,1],[1,100,1],[1,1,1]],[[7,3,8],[2,9,1],[6,4,5]],[[2,-3,4],[5,-6,7],[8,9,-10]]]],FALL_REF,[FALL_REF.replace('c-1','c'),FALL_REF.replace('return min(dp)','return dp[0]')],['Forbids down-left moves.','Requires the final path to end in the first column.'],falling_oracle,random_matrix,['Only the best cost reaching each position in the previous row matters.','Roll one DP row downward.','new[c]=matrix[r][c]+min(dp[c-1:c+2] within bounds).','Every valid path to a cell ends at one of those three predecessors, so taking their minimum is exhaustive.'],'O(rows*columns)','O(columns)',5),
935:E('knight_dialer_count',[('n','int')],'int',['dynamic-programming','graphs'],['Start on any digit and make n-1 chess-knight moves on a phone keypad.','Return the number of length-n dial strings modulo 1,000,000,007.'],[([1],'Every digit is a valid one-digit number, giving ten.'),([2],'There are twenty legal directed knight moves between keypad digits.')],[[n] for n in range(3,17)],KNIGHT_REF,[KNIGHT_REF.replace('dp=[1]*10','dp=[1]*9+[0]'),KNIGHT_REF.replace('range(n-1)','range(n)')],['Forgets that a sequence may start at digit nine.','Makes n moves instead of n-1.'],knight_oracle,random_n,['Treat keypad digits as graph vertices joined by knight moves.','Track how many sequences of the current length end at each digit.','For each additional digit, sum counts from its knight neighbors.','Every longer sequence has exactly one previous endpoint and one legal final edge.'],'O(n)','O(1)',5),
937:E('reorder_log_files',[('logs','list[str]')],'list[str]',['sorting','strings'],['Letter-logs sort by content then identifier; digit-logs retain input order after all letter-logs.','Return the reordered complete log strings.'],[([['dig1 8 1 5 1','let1 art can','dig2 3 6','let2 own kit dig','let3 art zero']],'Letter logs sort by body, then the two digit logs keep their original order.'),([['a1 9 2 3 1','g1 act car','zo4 4 7','ab1 off key dog','a8 act zoo']],'The act and off letter bodies sort before the stable digit logs.')],[[x] for x in [['d1 1'],['l1 art'],['d1 1','d2 2'],['l2 zoo','l1 art'],['b same','a same'],['d1 9','l1 x','d2 8'],['l1 a b','l2 a a'],['x 1 2','a alpha','y 3'],['z dog cat','a dog car'],['a x','b x','c x'],['d 0','l zero','e 1'],['id9 own kit','id1 own kit'],['a art can','b art zero','c art can'],['x 9','y eight']]],LOGS_REF,[LOGS_REF.replace('letters.sort()','letters.sort(reverse=True)'),LOGS_REF.replace('+digits','+list(reversed(digits))')],['Sorts letter logs in descending order.','Reverses digit logs instead of preserving them.'],logs_oracle,random_logs,['Digit-log order is stable; only letter logs receive sort keys.','Separate the two kinds while scanning.','Sort letter triples by (body,identifier), then append untouched digit logs.','The tuple key exactly implements both letter tie rules and separation preserves digit order.'],'O(n log n)','O(n)',5),
938:E('range_sum_bst',[('root','TreeNode'),('low','int'),('high','int')],'int',['trees','binary-search-trees','recursion'],['The input is a binary search tree with distinct values.','Return the sum of values in the inclusive interval [low,high].'],[([[10,5,15,3,7,None,18],7,15],'Values 7,10,15 lie in range and sum to 32.'),([[10,5,15,3,7,13,18,1,None,6],6,10],'Values 6,7,10 sum to 23.')],[[t,l,h] for t,l,h in [([1],1,1),([2,1,3],1,3),([2,1,3],2,2),([2,1,3],0,0),([5,3,8,2,4,7,9],4,8),([0,-2,3,-4,-1,2,5],-2,2),([10,5,15],11,20),([10,5,15],0,9),([4,2,6,1,3,5,7],3,5),([8,4,12,2,6,10,14],6,13),([1,None,2,None,3],1,3),([3,2,None,1],1,2),([20,10,30,5,15,25,35],15,25),([7,3,9,1,5,8,10],6,8)]],BST_RANGE_REF,[BST_RANGE_REF.replace('root.val<low','root.val<=low'),BST_RANGE_REF.replace('return root.val+','return 0*root.val+')],['Prunes a boundary value that must be included.','Traverses but never contributes the current node value.'],range_bst_oracle,random_bst,['BST ordering lets an out-of-range node eliminate one entire subtree.','Recurse right when value<low, left when value>high, and both when inside.','Return zero for None; otherwise prune or add node plus both child sums.','All discarded subtree values lie beyond the same interval boundary by the BST invariant.'],'O(nodes visited)','O(tree height)',3),
}
BATCH[938]['params'][0]=('root','TreeNode | None','treenode')
