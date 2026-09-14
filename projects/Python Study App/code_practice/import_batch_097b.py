"""Second half of batch 97: compression DP, greedy simulation, and parity masks."""
from collections import Counter,deque
from functools import lru_cache
from itertools import combinations,product
from .import_batch_055 import entry
MOD=1_000_000_007
def encoded(s):
 out=0;i=0
 while i<len(s):
  j=i+1
  while j<len(s) and s[j]==s[i]:j+=1
  count=j-i;out+=1+(len(str(count)) if count>1 else 0);i=j
 return out
def compress_o(a):
 s,k=a;return min(encoded(''.join(c for i,c in enumerate(s) if i not in removed)) for removed in combinations(range(len(s)),k))
def triplets_o(a):
 arr,x,y,z=a;return sum(abs(arr[i]-arr[j])<=x and abs(arr[j]-arr[k])<=y and abs(arr[i]-arr[k])<=z for i in range(len(arr)) for j in range(i+1,len(arr)) for k in range(j+1,len(arr)))
def winner_o(a):
 arr,k=a;queue=deque(arr);wins=0;champion=queue.popleft()
 while wins<k:
  rival=queue.popleft()
  if champion>rival:wins+=1;queue.append(rival)
  else:queue.append(champion);champion=rival;wins=1
 return champion
def grid_o(a):
 grid=a[0];n=len(grid);start=tuple(tuple(row) for row in grid);queue=deque([(start,0)]);seen={start}
 def valid(g):return all(g[row][col]==0 for row in range(n) for col in range(row+1,n))
 while queue:
  state,moves=queue.popleft()
  if valid(state):return moves
  for row in range(n-1):
   nxt=list(state);nxt[row],nxt[row+1]=nxt[row+1],nxt[row];nxt=tuple(nxt)
   if nxt not in seen:seen.add(nxt);queue.append((nxt,moves+1))
 return -1
def score_o(a):
 x,y=a;common=sorted(set(x)&set(y));last=-10**30;segments=[]
 for value in common+[10**30]:segments.append((sum(v for v in x if last<v<value),sum(v for v in y if last<v<value),None if value==10**30 else value));last=value
 best=0
 for choices in product((0,1),repeat=len(segments)):
  total=sum(segment[choice]+(segment[2] or 0) for segment,choice in zip(segments,choices));best=max(best,total)
 return best%MOD
def missing_o(a):
 arr,k=a;present=set(arr);value=0
 while k:
  value+=1
  if value not in present:k-=1
 return value
def convert_o(a):
 s,t,k=a
 if len(s)!=len(t):return False
 used=Counter()
 for left,right in zip(s,t):
  shift=(ord(right)-ord(left))%26
  if shift:
   if shift+26*used[shift]>k:return False
   used[shift]+=1
 return True
def balance_o(a):
 s=a[0];index=opens=insertions=0
 while index<len(s):
  if s[index]=='(':opens+=1;index+=1;continue
  if index+1<len(s) and s[index+1]==')':index+=2
  else:insertions+=1;index+=1
  if opens:opens-=1
  else:insertions+=1
 return insertions+2*opens
def awesome_o(a):
 s=a[0];best=0
 for left in range(len(s)):
  counts=Counter()
  for right in range(left,len(s)):
   counts[s[right]]+=1
   if sum(v%2 for v in counts.values())<=1:best=max(best,right-left+1)
 return best
def great_o(a):
 value=a[0]
 while True:
  for i in range(len(value)-1):
   if value[i]!=value[i+1] and value[i].lower()==value[i+1].lower():value=value[:i]+value[i+2:];break
  else:return value
def rcompress(r):
 s=''.join(r.choice('abcd') for _ in range(r.randint(1,10)));return [s,r.randint(0,len(s))]
def rtriplets(r):return [[r.randint(-10,10) for _ in range(r.randint(3,10))],r.randint(0,10),r.randint(0,10),r.randint(0,10)]
def rwinner(r):
 n=r.randint(2,12);return [r.sample(range(1,100),n),r.randint(1,20)]
def rgrid(r):
 n=r.randint(1,5);return [[[r.randint(0,1) for _ in range(n)] for _ in range(n)]]
def rscore(r):
 x=sorted(r.sample(range(1,50),r.randint(1,8)));y=sorted(r.sample(range(1,50),r.randint(1,8)));return [x,y]
def rmissing(r):
 arr=sorted(r.sample(range(1,50),r.randint(1,15)));return [arr,r.randint(1,30)]
def rconvert(r):
 n=r.randint(1,20);return [''.join(r.choice('abcdxyz') for _ in range(n)),''.join(r.choice('abcdxyz') for _ in range(n)),r.randint(0,100)]
def rbalance(r):return [''.join(r.choice('()') for _ in range(r.randint(1,18)))]
def rawesome(r):return [''.join(r.choice('012345') for _ in range(r.randint(1,15)))]
def rgreat(r):return [''.join(r.choice('abcABC') for _ in range(r.randint(1,30)))]

COMPRESS='''def minimum_compressed_length(s, k):
 from functools import lru_cache
 @lru_cache(None)
 def solve(index,deletions):
  if len(s)-index<=deletions:return 0
  best=10**9;same=removed=0
  for end in range(index,len(s)):
   if s[end]==s[index]:same+=1
   else:removed+=1
   if removed>deletions:break
   length=1+(1 if same>=2 else 0)+(1 if same>=10 else 0)+(1 if same>=100 else 0)
   best=min(best,length+solve(end+1,deletions-removed))
  return min(best,solve(index+1,deletions-1) if deletions else best)
 return solve(0,k)
'''
TRIPLETS='''def count_threshold_triplets(arr, a, b, c):
 answer=0
 for i in range(len(arr)):
  for j in range(i+1,len(arr)):
   for k in range(j+1,len(arr)):
    answer+=abs(arr[i]-arr[j])<=a and abs(arr[j]-arr[k])<=b and abs(arr[i]-arr[k])<=c
 return answer
'''
WINNER='''def array_game_winner(arr, k):
 champion=arr[0];wins=0
 for rival in arr[1:]:
  if champion>rival:wins+=1
  else:champion=rival;wins=1
  if wins==k:return champion
 return champion
'''
GRID='''def minimum_binary_grid_swaps(grid):
 n=len(grid);zeros=[]
 for row in grid:
  count=0
  for value in reversed(row):
   if value:break
   count+=1
  zeros.append(count)
 answer=0
 for row in range(n):
  need=n-row-1;candidate=row
  while candidate<n and zeros[candidate]<need:candidate+=1
  if candidate==n:return -1
  answer+=candidate-row
  zeros[row:candidate+1]=[zeros[candidate]]+zeros[row:candidate]
 return answer
'''
SCORE='''def maximum_two_array_path_score(nums1, nums2):
 i=j=0;left=right=0
 while i<len(nums1) and j<len(nums2):
  if nums1[i]<nums2[j]:left+=nums1[i];i+=1
  elif nums2[j]<nums1[i]:right+=nums2[j];j+=1
  else:left=right=max(left,right)+nums1[i];i+=1;j+=1
 left+=sum(nums1[i:]);right+=sum(nums2[j:])
 return max(left,right)%1000000007
'''
MISSING='''def kth_missing_positive(arr, k):
 previous=0
 for value in arr:
  gap=value-previous-1
  if k<=gap:return previous+k
  k-=gap;previous=value
 return previous+k
'''
CONVERT='''def can_convert_with_scheduled_shifts(s, t, k):
 if len(s)!=len(t):return False
 used=[0]*26
 for left,right in zip(s,t):
  shift=(ord(right)-ord(left))%26
  if shift:
   required=shift+26*used[shift]
   if required>k:return False
   used[shift]+=1
 return True
'''
BALANCE='''def minimum_double_close_insertions(s):
 insertions=need=0
 for char in s:
  if char=='(':
   if need%2:insertions+=1;need-=1
   need+=2
  else:
   need-=1
   if need<0:insertions+=1;need=1
 return insertions+need
'''
AWESOME='''def longest_awesome_digit_substring(s):
 earliest={0:-1};mask=answer=0
 for index,char in enumerate(s):
  mask^=1<<int(char)
  if mask in earliest:answer=max(answer,index-earliest[mask])
  else:earliest[mask]=index
  for digit in range(10):
   candidate=mask^(1<<digit)
   if candidate in earliest:answer=max(answer,index-earliest[candidate])
 return answer
'''
GREAT='''def make_case_string_good(s):
 stack=[]
 for char in s:
  if stack and stack[-1]!=char and stack[-1].lower()==char.lower():stack.pop()
  else:stack.append(char)
 return ''.join(stack)
'''
E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1531:S('minimum_compressed_length',[('s','str'),('k','int')],'int',['dynamic-programming','strings'],['Delete at most k characters, then encode each equal-character run as the character plus its count when greater than one.','Return the minimum possible encoded length.'],[(['aaabcccd',2],'Deleting b and d produces aaaccc, encoded as a3c3 with length four.'),(['aabbaa',2],'Deleting both b characters joins four a characters into a4, of length two.')],[[s,k] for s,k in [('a',0),('a',1),('aaabcccd',2),('aabbaa',2),('aaaaaaaaaaa',0),('aaaaaaaaaaa',1),('abc',1),('abc',3),('aaabbaaa',1),('aaabbaaa',3),('abababab',4),('aabcddd',2),('aaaaaaaaaab',1),('abcddeee',2)]],COMPRESS,[COMPRESS.replace('return solve(0,k)','return solve(0,0)'),COMPRESS.replace('1 if same>=2 else 0','1')],['Ignores the deletion budget and compresses the original string only.','Adds a count digit even for singleton runs.'],compress_o,rcompress,['Memoize the best result from a string index with a remaining deletion budget.','Choose the current character as the next run and scan forward, spending deletions on different characters.','Charge one character plus digits when the kept run reaches 2, 10, or 100; also consider deleting the current character.','Every optimal compressed string has a first kept run represented by one such scan.'],'O(n²*k)','O(n*k)',8),
1534:S('count_threshold_triplets',[('arr','list[int]'),('a','int'),('b','int'),('c','int')],'int',['arrays','enumeration'],['Choose indices i<j<k.','Require |arr[i]-arr[j]|<=a, |arr[j]-arr[k]|<=b, and |arr[i]-arr[k]|<=c.'],[([[3,0,1,1,9,7],7,2,3],'Exactly four ordered-index triplets satisfy all three distance limits.'),([[1,1,2,2,3],0,0,1],'No three positions satisfy both zero-distance adjacent-pair requirements.')],[[*x] for x in [([1,2,3],1,1,2),([3,0,1,1,9,7],7,2,3),([1,1,2,2,3],0,0,1),([0,0,0],0,0,0),([1,5,9],10,10,10),([1,5,9],3,10,10),([-1,0,1],1,1,2),([1,2,3,4],2,2,3),([5,1,5,1],0,4,4),([10,0,5,6],5,2,6),([2,2,2,3],0,1,1),([9,7,5,3],2,2,4),([1,10,2,9],9,8,1),([0,3,6,9,12],6,6,12)]],TRIPLETS,[TRIPLETS.replace('and abs(arr[i]-arr[k])<=c',''),TRIPLETS.replace('range(j+1,len(arr))','range(j,len(arr))')],['Ignores the first-to-third distance constraint.','Allows j and k to be the same index.'],triplets_o,rtriplets,['Enumerate every index triple in increasing order.','Evaluate the three absolute-difference bounds.','Increment only when all are satisfied.','The nested index ranges generate each legal i<j<k triple exactly once.'],'O(n³)','O(1)',3),
1535:S('array_game_winner',[('arr','list[int]'),('k','int')],'int',['arrays','simulation'],['arr contains distinct integers; the larger of the first two wins a round and stays in front while the loser moves to the end.','Return the first value to win k consecutive rounds.'],[([[2,1,3,5,4,6,7],2],'Five beats three and four consecutively before any larger value reaches the front.'),([[3,2,1],10],'The maximum three eventually wins every remaining round and reaches any large streak.')],[[a,k] for a,k in [([2,1],1),([2,1],5),([2,1,3,5,4,6,7],2),([3,2,1],10),([1,2,3],1),([1,2,3],2),([5,1,2,3,4],3),([4,3,2,1],2),([1,5,2,4,3],2),([10,1,9,2],3),([7,6,5,4,3,2,1],6),([1,3,2],2),([9,1,8,2,7],1),([2,4,1,3],4)]],WINNER,[WINNER.replace('wins=1','wins=0'),WINNER.replace('if wins==k:return champion','if wins>k:return champion')],['Resets a new champion’s first win to zero.','Requires one more consecutive win than k.'],winner_o,rwinner,['Keep the current front champion and its consecutive wins.','Compare it with each new challenger in original order; the larger becomes champion.','A new champion has already won once, while a surviving champion increments its streak.','Once the global maximum arrives it never loses, so a single pass suffices even when k is large.'],'O(n)','O(1)',5),
1536:S('minimum_binary_grid_swaps',[('grid','list[list[int]]')],'int',['matrices','greedy'],['grid is square and only adjacent row swaps are allowed.','After rearrangement, row i needs at least n-i-1 trailing zeros so every cell above the main diagonal is zero.'],[([[[0,0,1],[1,1,0],[1,0,0]]],'Rows with one and two trailing zeros must bubble upward, requiring three adjacent swaps.'),([[[0,1,1,0],[0,1,1,0],[0,1,1,0],[0,1,1,0]]],'No row has the three trailing zeros required at the top, so arrangement is impossible.')],[[g] for g in [[[0]],[[0,0],[1,0]],[[1,0],[0,0]],[[0,0,1],[1,1,0],[1,0,0]],[[0,1,1,0],[0,1,1,0],[0,1,1,0],[0,1,1,0]],[[1,0,0],[1,1,0],[1,1,1]],[[0,0,0],[0,0,0],[0,0,0]],[[1,1],[1,1]],[[0,1,0],[0,0,1],[1,0,0]],[[1,0,0],[0,1,0],[0,0,1]],[[0,0],[0,1]],[[1,0,0,0],[1,1,0,0],[1,1,1,0],[1,1,1,1]],[[0,0,1],[0,1,0],[1,0,0]],[[1,0,1],[0,0,0],[1,1,0]]]],GRID,[GRID.replace('need=n-row-1','need=n-row'),GRID.replace('answer+=candidate-row','answer+=1')],['Requires one extra trailing zero in every row.','Counts one per selected row instead of the adjacent swaps needed to bubble it upward.'],grid_o,rgrid,['Count trailing zeros in every row.','For each target row from top down, find the nearest later row meeting its required zero count.','Bubble that row upward and add the traveled distance.','Choosing the nearest feasible row is exchange-optimal because every farther choice costs at least as many swaps and leaves the same multiset below.'],'O(n²)','O(n)',5),
1537:S('maximum_two_array_path_score',[('nums1','list[int]'),('nums2','list[int]')],'int',['two-pointers','greedy'],['Both arrays are strictly increasing and positive; traverse either array from left to right and may switch at shared values.','Count a shared value once and return the maximum path sum modulo 1,000,000,007.'],[([[2,4,5,8,10],[4,6,8,9]],'Choosing the better segment at shared values four and eight produces score thirty.'),([[1,3,5,7,9],[3,5,100]],'Switching to the second array after shared value five reaches one hundred for score one hundred nine.')],[[a,b] for a,b in [([1],[2]),([1],[1]),([2,4,5,8,10],[4,6,8,9]),([1,3,5,7,9],[3,5,100]),([1,2,3],[4,5,6]),([1,2,3],[1,2,3]),([1,4,7],[2,4,8]),([5,10],[5,6,10]),([1,10,20],[2,10,30]),([1,2,100],[1,50,100]),([3,6,9],[3,5,6,8,9]),([1,5,9],[2,6,10]),([7],[7]),([1,2,4,8,16],[2,3,4,7,16])]],SCORE,[SCORE.replace('max(left,right)','min(left,right)'),SCORE.replace('+nums1[i]','+nums1[i]*2')],['Chooses the smaller accumulated segment at each crossing.','Double-counts every shared switching value.'],score_o,rscore,['Accumulate segment sums independently while advancing two pointers.','At a shared value, both paths can arrive there, so set both totals to the larger prior total plus that value once.','After the final crossing, append each remaining tail and take the larger total.','Any switch is possible only at a shared value, making each between-crossing segment an independent maximum choice.'],'O(n+m)','O(1)',8),
1539:S('kth_missing_positive',[('arr','list[int]'),('k','int')],'int',['arrays','binary-search'],['arr is strictly increasing and contains positive integers.','Return the kth positive integer absent from arr.'],[([[2,3,4,7,11],5],'Missing values are one, five, six, eight, and nine, so the fifth is nine.'),([[1,2,3,4],2],'The missing sequence begins five, six, making six the second.')],[[a,k] for a,k in [([1],1),([2],1),([2,3,4,7,11],5),([1,2,3,4],2),([5,6,7],1),([5,6,7],4),([1,3],1),([1,3],2),([2,4,6],3),([10],9),([1,10],5),([3,4,5],2),([1,2,100],3),([4,7,9,10],6)]],MISSING,[MISSING.replace('gap=value-previous-1','gap=value-previous'),MISSING.replace('return previous+k','return previous+k+1')],['Counts the present endpoint itself as missing inside every gap.','Adds one after the final array value.'],missing_o,rmissing,['Track the previous present value, beginning at zero.','The gap before value contains value-previous-1 missing positives.','If k falls in that gap, offset from previous; otherwise subtract the gap and continue.','After the array, every subsequent integer is missing, so add the remaining rank.'],'O(n)','O(1)',3),
1540:S('can_convert_with_scheduled_shifts',[('s','str'),('t','str'),('k','int')],'bool',['strings','counting'],['Move i can shift one not-yet-chosen index forward by i letters modulo 26; each index is used at most once.','Return whether all required shifts can be assigned distinct move numbers no greater than k.'],[(['input','ouput',9],'The nonzero shifts can be scheduled within nine moves without reusing a move number.'),(['aab','bbb',27],'Two positions need shift one, schedulable at moves one and twenty-seven.')],[[s,t,k] for s,t,k in [('a','a',0),('a','b',1),('a','z',24),('input','ouput',9),('aab','bbb',27),('aa','bb',26),('aa','bb',27),('abc','bcd',53),('abc','abc',0),('az','za',25),('az','za',1),('abcd','bcda',80),('xxx','aaa',9),('xxx','aaa',61)]],CONVERT,[CONVERT.replace('shift+26*used[shift]','shift'),CONVERT.replace('26*used[shift]','25*used[shift]')],['Reuses the same move number for multiple indices needing an equal shift.','Schedules repeated equal shifts only twenty-five moves apart, causing move collisions modulo 26.'],convert_o,rconvert,['Compute each position’s forward shift modulo 26; zero needs no move.','The first occurrence of shift d uses move d, the next d+26, then d+52, and so on.','Track how many times each shift has appeared and reject if its required move exceeds k.','These are the earliest distinct moves producing that residue, so any later schedule cannot improve feasibility.'],'O(n)','O(alphabet)',5),
1541:S('minimum_double_close_insertions',[('s','str')],'int',['strings','greedy'],['Every opening parenthesis must be matched by two consecutive closing parentheses.','Insert the fewest parentheses anywhere to make s balanced.'],[(['(()))'],'The first opening is closed by the final pair, while one closing parenthesis must be inserted for the other opening.'),(['())'],'One opening followed by two closings is already balanced, so no insertion is needed.')],[[s] for s in ['(',')','()','())','(()))','))())(','(((',')))','()()','(()','())(()','())())','((((()))','())(()))']],BALANCE,[BALANCE.replace('if need%2:','if not need%2:'),BALANCE.replace('need=1','need=2')],['Closes an even pending requirement before accepting a new opening.','After an unmatched closing, leaves two rather than one required closing parenthesis.'],balance_o,rbalance,['Track how many closing parentheses are currently required.','Before a new opening, if the requirement is odd, insert one closing parenthesis so previous pairs stay consecutive.','A closing consumes one requirement; if it makes need negative, insert an opening and leave one closing still required.','Each repair is forced at the position where the grammar would otherwise become impossible, so the greedy count is minimal.'],'O(n)','O(1)',5),
1542:S('longest_awesome_digit_substring',[('s','str')],'int',['bit-manipulation','prefix-parity'],['s contains decimal digits.','Return the longest substring whose characters can be rearranged into a palindrome, meaning at most one digit has odd frequency.'],[(['3242415'],'Substring 24241 has only digit four with odd frequency, so the maximum length is five.'),(['12345678'],'No length-two-or-more substring can form a palindrome, so the answer is one.')],[[s] for s in ['0','00','01','3242415','12345678','213123','999','0123456789','010','112233','98766789','0011223','1233214','555012555','102030201']],AWESOME,[AWESOME.replace('for digit in range(10):','for digit in range(9):'),AWESOME.replace('earliest={0:-1}','earliest={0:0}')],['Never checks the parity exception for digit nine.','Records the empty prefix at index zero instead of before the string.'],awesome_o,rawesome,['Represent prefix digit-count parity as a ten-bit mask.','Equal masks delimit a substring with all even counts.','Masks differing by one bit delimit a substring with exactly one odd count.','Store only the earliest index for each mask to maximize every candidate length.'],'O(10*n)','O(2^10)',8),
1544:S('make_case_string_good',[('s','str')],'str',['strings','stacks'],['Adjacent characters form a bad pair when they are the same letter in opposite cases.','Repeatedly remove bad pairs and return the unique remaining string.'],[(['leEeetcode'],'Removing E and e exposes no further bad pair, yielding leetcode.'),(['abBAcC'],'Removing bB then aA then cC leaves the empty string.')],[[s] for s in ['a','A','aA','Aa','leEeetcode','abBAcC','s','mC','Pp','abcCBA','aabAAB','xYyX','Code','cCcodeE']],GREAT,[GREAT.replace("stack[-1]!=char and ",''),GREAT.replace('stack.pop()','stack=[]')],['Removes identical same-case adjacent letters too.','Clears the entire stack whenever one bad pair appears.'],great_o,rgreat,['Maintain the already-good prefix in a stack.','If the next character forms an opposite-case pair with the stack top, pop it; otherwise push.','A removal can expose only the new top to the next character, which the stack handles immediately.','This simulates all forced adjacent cancellations and yields the unique stable result.'],'O(n)','O(n)',3),
}
