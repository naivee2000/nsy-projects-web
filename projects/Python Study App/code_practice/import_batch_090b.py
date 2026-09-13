"""Second half of batch 90: greedy groups, windows, traversal, and bit logic."""
from collections import Counter, deque
from .import_batch_055 import entry

def groups_o(a):
 nums,k=a;counts=Counter(nums)
 def solve(left):
  if not left:return True
  first=min(left)
  for x in range(first,first+k):
   if not left.get(x):return False
   left[x]-=1
   if not left[x]:del left[x]
  return solve(left)
 return len(nums)%k==0 and solve(counts)
def freq_o(a):
 s,mn,lo,hi=a;seen=Counter()
 for size in range(lo,hi+1):
  for i in range(len(s)-size+1):
   part=s[i:i+size]
   if len(set(part))<=mn:seen[part]+=1
 return max(seen.values(),default=0)
def replace_o(a):return [max(a[0][i+1:],default=-1) for i in range(len(a[0]))]
def mutate_o(a):
 arr,target=a;return min(range(max(arr)+1),key=lambda cap:(abs(sum(min(x,cap) for x in arr)-target),cap))
def jump_o(a):
 arr,start=a;q=[start];seen={start}
 for i in q:
  if arr[i]==0:return True
  for j in (i-arr[i],i+arr[i]):
   if 0<=j<len(arr) and j not in seen:seen.add(j);q.append(j)
 return False
def decrypt_o(a):
 s=a[0];i=0;out=''
 while i<len(s):
  if i+2<len(s) and s[i+2]=='#':value=int(s[i:i+2]);i+=3
  else:value=int(s[i]);i+=1
  out+=chr(96+value)
 return out
def xor_o(a):
 arr,queries=a;return [__import__('functools').reduce(int.__xor__,arr[l:r+1],0) for l,r in queries]
def decompress_o(a):
 nums=a[0];return [value for count,value in zip(nums[::2],nums[1::2]) for _ in range(count)]
def block_o(a):
 mat,k=a;h=len(mat);w=len(mat[0]);return [[sum(mat[x][y] for x in range(max(0,i-k),min(h,i+k+1)) for y in range(max(0,j-k),min(w,j+k+1))) for j in range(w)] for i in range(h)]
def flips_o(a):
 x,y,z=a;answer=0
 while x or y or z:
  p,q,r=x&1,y&1,z&1;answer+=(p+q if r==0 else int(not(p or q)));x>>=1;y>>=1;z>>=1
 return answer

def rg(r):return [[r.randint(1,12) for _ in range(r.randint(1,16))],r.randint(1,5)]
def rf(r):
 n=r.randint(1,18);s=''.join(r.choice('abcd') for _ in range(n));lo=r.randint(1,n);return [s,r.randint(1,4),lo,r.randint(lo,n)]
def rr(r):return [[r.randint(1,100) for _ in range(r.randint(1,20))]]
def rm(r):
 arr=[r.randint(1,50) for _ in range(r.randint(1,15))];return [arr,r.randint(1,sum(arr)+20)]
def rj(r):
 arr=[r.randint(0,8) for _ in range(r.randint(1,20))];return [arr,r.randrange(len(arr))]
def rd(r):
 values=[r.randint(1,26) for _ in range(r.randint(1,20))];return [''.join(str(x)+'#' if x>=10 else str(x) for x in values)]
def rx(r):
 arr=[r.randint(0,100) for _ in range(r.randint(1,20))];return [arr,[sorted(r.sample(range(len(arr)),2)) if len(arr)>1 else [0,0] for _ in range(r.randint(1,10))]]
def rde(r):return [[v for _ in range(r.randint(1,8)) for v in (r.randint(1,5),r.randint(-5,5))]]
def rb(r):
 h,w=r.randint(1,5),r.randint(1,5);return [[[r.randint(-5,9) for _ in range(w)] for _ in range(h)],r.randint(0,5)]
def rfl(r):return [r.randint(0,10000),r.randint(0,10000),r.randint(0,10000)]

GROUPS='''def can_divide_consecutive_groups(nums, k):
 from collections import Counter
 if len(nums)%k:return False
 counts=Counter(nums)
 for first in sorted(counts):
  copies=counts[first]
  if copies:
   for value in range(first,first+k):
    if counts[value]<copies:return False
    counts[value]-=copies
 return True
'''
FREQ='''def maximum_limited_letter_substring_frequency(s, max_letters, min_size, max_size):
 from collections import Counter
 counts=Counter(s[i:i+min_size] for i in range(len(s)-min_size+1) if len(set(s[i:i+min_size]))<=max_letters)
 return max(counts.values(),default=0)
'''
REPLACE='''def replace_with_greatest_right(arr):
 answer=arr[:];greatest=-1
 for i in range(len(arr)-1,-1,-1):answer[i],greatest=greatest,max(greatest,arr[i])
 return answer
'''
MUTATE='''def closest_capped_array_value(arr, target):
 left,right=0,max(arr)
 while left<right:
  middle=(left+right)//2
  if sum(min(x,middle) for x in arr)<target:left=middle+1
  else:right=middle
 return min((left,left-1),key=lambda cap:(abs(sum(min(x,cap) for x in arr)-target),cap))
'''
JUMP='''def can_reach_zero(arr, start):
 stack=[start];seen=set()
 while stack:
  index=stack.pop()
  if index in seen:continue
  if arr[index]==0:return True
  seen.add(index)
  for nxt in (index-arr[index],index+arr[index]):
   if 0<=nxt<len(arr):stack.append(nxt)
 return False
'''
DECRYPT='''def decrypt_alphabet_string(s):
 answer='';i=len(s)-1
 while i>=0:
  if s[i]=='#':value=int(s[i-2:i]);i-=3
  else:value=int(s[i]);i-=1
  answer=chr(96+value)+answer
 return answer
'''
XOR='''def xor_subarray_queries(arr, queries):
 prefix=[0]
 for value in arr:prefix.append(prefix[-1]^value)
 return [prefix[right+1]^prefix[left] for left,right in queries]
'''
DECOMPRESS='''def decompress_run_length_list(nums):
 answer=[]
 for count,value in zip(nums[::2],nums[1::2]):answer.extend([value]*count)
 return answer
'''
BLOCK='''def matrix_block_sum(mat, k):
 h,w=len(mat),len(mat[0]);prefix=[[0]*(w+1) for _ in range(h+1)]
 for i in range(h):
  for j in range(w):prefix[i+1][j+1]=mat[i][j]+prefix[i][j+1]+prefix[i+1][j]-prefix[i][j]
 return [[prefix[min(h,i+k+1)][min(w,j+k+1)]-prefix[max(0,i-k)][min(w,j+k+1)]-prefix[min(h,i+k+1)][max(0,j-k)]+prefix[max(0,i-k)][max(0,j-k)] for j in range(w)] for i in range(h)]
'''
FLIPS='''def minimum_or_target_flips(a, b, c):
 answer=0
 while a or b or c:
  x,y,z=a&1,b&1,c&1;answer+=x+y if z==0 else int(not(x or y));a>>=1;b>>=1;c>>=1
 return answer
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1296:S('can_divide_consecutive_groups',[('nums','list[int]'),('k','int')],'bool',['greedy','hash-maps'],['Every group must contain k consecutive distinct values.','Every input occurrence must belong to exactly one group.'],[([[1,2,3,3,4,4,5,6],4],'The groups 1,2,3,4 and 3,4,5,6 use every value.'),([[3,3,2,2,1,1],3],'Two copies of 1,2,3 form two valid groups.')],[[a,k] for a,k in [([1],1),([1,2],1),([1,2],2),([1,3],2),([1,2,3],3),([1,2,3,4],3),([1,1,2,2],2),([1,2,2,3],2),([1,2,3,4,5,6],3),([1,2,4,5],2),([5,6,7,7,8,9],3),([1,2,3,3,4,5],3),([10,11,12,10,11,12],3),([1,2,3,4],4)]],GROUPS,[GROUPS.replace('range(first,first+k)','range(first,first+k-1)'),GROUPS.replace('sorted(counts)','counts')],['Builds groups with only k-1 values.','Processes arbitrary insertion order instead of starting at the smallest remaining value.'],groups_o,rg,['The smallest remaining value must start a group.','Count values, then consume its multiplicity from every value in the next k positions.','Reject a shortage; continue through keys in sorted order.','No earlier value can precede the smallest remaining one, so the greedy start is forced.'],'O(n log n)','O(n)',5),
1297:S('maximum_limited_letter_substring_frequency',[('s','str'),('max_letters','int'),('min_size','int'),('max_size','int')],'int',['sliding-window','hash-maps'],['Count substrings having at most max_letters distinct characters.','Return the greatest occurrence count among lengths min_size through max_size.'],[(['aababcaab',2,3,4],'Substring aab occurs twice and has two distinct letters.'),(['aaaa',1,2,3],'Substring aa occurs three times, the maximum frequency.')],[[s,m,a,b] for s,m,a,b in [('a',1,1,1),('aaaa',1,1,1),('abc',3,1,3),('abc',1,1,3),('abab',2,2,4),('aabb',1,2,3),('abcabc',3,3,5),('zzzyzz',1,2,4),('abcd',2,2,2),('aaaaa',1,3,5),('abacaba',2,3,4),('xyzxyzx',3,2,6),('aabcaab',2,3,5),('mississippi',3,2,5)]],FREQ,['''def maximum_limited_letter_substring_frequency(s, max_letters, min_size, max_size):
 from collections import Counter
 counts=Counter(s[i:i+max_size] for i in range(len(s)-max_size+1) if len(set(s[i:i+max_size]))<=max_letters)
 return max(counts.values(),default=0)
''',FREQ.replace('<=max_letters','<max_letters')],['Counts only maximum-size substrings, missing more frequent shorter ones.','Rejects windows using exactly max_letters distinct characters.'],freq_o,rf,['Only min_size needs counting: every occurrence of a longer valid substring contains a valid min_size prefix.','Count each min_size window whose distinct-character count is within the limit.','Return the maximum counter value.','A longer substring cannot occur more often than its fixed prefix, so it cannot improve the optimum.'],'O(n*min_size)','O(n)',5),
1299:S('replace_with_greatest_right',[('arr','list[int]')],'list[int]',['arrays','suffixes'],['Replace every value by the greatest value strictly to its right.','Replace the final position by -1.'],[([[17,18,5,4,6,1]],'Suffix maxima produce 18,6,6,6,1,-1.'),([[400]],'No value lies to the right, so return -1.')],[[x] for x in [[1],[1,2],[2,1],[1,2,3],[3,2,1],[1,1,1],[5,1,5],[10,9,8],[3,1,2],[10,5,8,2],[1,9,2,8,3],[100,1,50],[2,7,4,3,5],[9,1,8,2,7],[4,10,4,10]]],REPLACE,[REPLACE.replace('greatest=-1','greatest=0'),REPLACE.replace('max(greatest,arr[i])','min(greatest,arr[i])')],['Uses zero instead of the required -1 suffix sentinel.','Tracks suffix minima rather than maxima.'],replace_o,rr,['Scan from right to left while storing the greatest value already seen.','Write the stored greatest before incorporating the current original value.','Initialize the stored value to -1 for the last position.','At each index the stored value is exactly the maximum of the strict suffix.'],'O(n)','O(n)',3),
1300:S('closest_capped_array_value',[('arr','list[int]'),('target','int')],'int',['binary-search','arrays'],['Replace values greater than the chosen nonnegative cap by the cap.','Minimize distance from target; ties choose the smaller cap.'],[([[4,9,3],10],'Cap three gives sum nine, closer than cap four giving eleven.'),([[2,3,5],10],'No cap below the maximum improves the unchanged sum, so return five.')],[[a,t] for a,t in [([1],1),([10],5),([1,2],3),([1,2],1),([2,3,5],10),([2,3,5],5),([4,9,3],10),([60864,25176,27249,21296,20204],56803),([1,1,1],10),([100,100],1),([5,10,15],20),([2,8,9],16),([7,7,7],14),([1,1000,1000],1001)]],MUTATE,[MUTATE.replace('(left,left-1)','(left,)'),MUTATE.replace("<target",">target")],['Checks only the first cap whose sum reaches target and misses a closer lower tie candidate.','Moves binary search in the wrong direction.'],mutate_o,rm,['The capped sum is nondecreasing in the cap.','Binary-search the first cap whose sum reaches or exceeds target.','Compare that cap with the preceding cap using distance then cap value.','Only the two caps around the crossing can minimize absolute distance.'],'O(n log M)','O(1)',5),
1306:S('can_reach_zero',[('arr','list[int]'),('start','int')],'bool',['graphs','depth-first-search'],['From index i jump exactly arr[i] positions left or right.','Return whether any reachable index contains zero.'],[([[4,2,3,0,3,1,2],5],'Jumps 5→4→1→3 reach the zero.'),([[3,0,2,1,2],2],'Every route cycles without reaching index one.')],[[a,s] for a,s in [([0],0),([1,0],0),([1,0],1),([1,1],0),([2,0,1],2),([2,1,0],0),([3,0,2,1,2],2),([4,2,3,0,3,1,2],0),([1,2,3,0],0),([2,2,2,0],0),([1,1,1,1,0],0),([5,4,3,2,1,0],0),([1,0,1],2),([2,4,1,0,3],1)]],JUMP,[JUMP.replace('index-arr[index]','index-1'),JUMP.replace("for nxt in (index-arr[index],index+arr[index]):","for nxt in (index+arr[index],):")],['Moves one step left instead of exactly arr[index].','Explores only rightward jumps and misses reachable zeros to the left.'],jump_o,rj,['Treat indices as graph nodes with up to two outgoing jumps.','DFS or BFS from start and mark each visited index.','Return true on a zero; enqueue only in-range unseen destinations.','Graph search visits exactly the reachable indices and terminates despite cycles.'],'O(n)','O(n)',5),
1309:S('decrypt_alphabet_string',[('s','str')],'str',['strings','parsing'],['1..9 map to a..i and 10#..26# map to j..z.','The encoded string is valid.'],[(['10#11#12'],'Tokens 10#,11#,1,2 decode to jkab.'),(['1326#'],'Tokens 1,3,26# decode to acz.')],[[s] for s in ['1','9','10#','26#','123','10#1','25#1','11#','20#20#','123456789','10#20#','26#10#','23#4','12#34#']],DECRYPT,['''def decrypt_alphabet_string(s):
 return ''.join(chr(96+int(char)) for char in s if char!='#')
''',DECRYPT.replace('i-=3','i-=2')],['Drops # markers and decodes both digits of every two-digit token separately.','Consumes only two characters for a # token and reparses its first digit.'],decrypt_o,rd,['Parse from right to left because # unambiguously marks a two-digit token.','On # read the preceding two digits; otherwise read one digit.','Convert 1..26 to letters and prepend or reverse the result.','Every suffix has exactly one valid next token under this grammar.'],'O(n)','O(n)',3),
1310:S('xor_subarray_queries',[('arr','list[int]'),('queries','list[list[int]]')],'list[int]',['prefix-sums','bit-manipulation'],['Queries use inclusive zero-based endpoints.','Return one XOR result per query in input order.'],[([[1,3,4,8],[[0,1],[1,2],[0,3],[3,3]]],'Prefix XOR cancellation yields 2,7,14,8.'),([[4,8,2,10],[[2,3],[1,3],[0,0],[0,3]]],'The four requested subarray XOR values are returned in order.')],[[a,q] for a,q in [([1],[[0,0]]),([1,2],[[0,1]]),([1,2],[[1,1]]),([0,0,0],[[0,2]]),([1,1,1],[[0,1],[1,2]]),([5,3,7],[[0,2],[1,1]]),([4,8,2,10],[[2,3]]),([9,0,9],[[0,2]]),([1,2,4,8],[[1,3]]),([7,7],[[0,0],[0,1]]),([10,20,30],[[0,1],[1,2]]),([3,5,6,7],[[0,3]]),([2,4,6,8],[[2,2]]),([1,3,4,8],[[0,1],[1,2]])]],XOR,[XOR.replace('prefix[right+1]^prefix[left]','prefix[right]^prefix[left]'),XOR.replace('prefix[-1]^value','prefix[-1]+value')],['Treats the right endpoint as exclusive.','Builds arithmetic prefix sums instead of XOR prefixes.'],xor_o,rx,['Prefix XOR through index i cancels shared prefixes just like prefix sums.','Build prefix[0]=0 and append prefix[-1] XOR value.','Query [l,r] is prefix[r+1] XOR prefix[l].','Every element before l appears twice and cancels; each queried element appears once.'],'O(n+q)','O(n)',5),
1313:S('decompress_run_length_list',[('nums','list[int]')],'list[int]',['arrays','simulation'],['nums has even length and stores [frequency,value] pairs.','Concatenate each value frequency times.'],[([[1,2,3,4]],'One two followed by three fours gives 2,4,4,4.'),([[1,1,2,3]],'One one followed by two threes gives 1,3,3.')],[[x] for x in [[1,5],[2,5],[1,1,1,2],[3,0],[2,-1,1,4],[1,2,2,3,3,4],[5,1],[1,9,4,8],[2,2,2,2],[3,7,1,7],[1,0,2,0],[4,-2,2,3],[2,5,3,6,1,7],[1,1,1,1,1,1]]],DECOMPRESS,[DECOMPRESS.replace('[value]*count','[count]*value'),DECOMPRESS.replace('nums[1::2]','nums[::2]')],['Swaps frequency and value roles.','Uses frequencies as both counts and emitted values.'],decompress_o,rde,['Read the input two entries at a time as count then value.','Append count copies of value for each pair.','Concatenate all expanded runs in their original order.','Each pair independently specifies exactly one output run.'],'O(output)','O(output)',3),
1314:S('matrix_block_sum',[('mat','list[list[int]]'),('k','int')],'list[list[int]]',['matrices','prefix-sums'],['For each cell sum rows i-k..i+k and columns j-k..j+k clipped to the matrix.','mat is nonempty and rectangular.'],[([[[1,2,3],[4,5,6],[7,8,9]],1],'Each output is the sum of its clipped 3-by-3 neighborhood.'),([[[1,2],[3,4]],0],'A zero-radius block returns the original matrix.')],[[m,k] for m,k in [([[1]],0),([[1]],5),([[1,2]],1),([[1],[2]],1),([[1,2],[3,4]],1),([[1,2],[3,4]],2),([[1,2,3],[4,5,6]],1),([[0,0],[0,0]],1),([[-1,2],[-3,4]],1),([[1,2,3],[4,5,6],[7,8,9]],2),([[5,1,5]],0),([[1],[2],[3]],2),([[2,4],[6,8],[10,12]],1),([[1,0,1],[0,1,0]],3)]],BLOCK,[BLOCK.replace('max(0,i-k)','max(0,i-k+1)'),BLOCK.replace('prefix[i][j]','prefix[i+1][j+1]')],['Drops the outermost row above each block.','Uses the current prefix cell for inclusion-exclusion and double-counts values.'],block_o,rb,['A 2D prefix table answers any clipped rectangle sum in constant time.','Build prefix with one zero border row and column.','For each center, clip its four bounds and apply inclusion-exclusion.','The prefix rectangle formula counts every cell in the block exactly once.'],'O(rows*cols)','O(rows*cols)',5),
1318:S('minimum_or_target_flips',[('a','int'),('b','int'),('c','int')],'int',['bit-manipulation','greedy'],['Flip individual bits in a or b until a OR b equals c.','Return the minimum number of flips.'],[([2,6,5],'Bitwise comparison requires three flips.'),([4,2,7],'Only the low bit must be set, so one flip is enough.')],[[a,b,c] for a,b,c in [(0,0,0),(0,0,1),(1,0,0),(1,1,0),(1,1,1),(2,6,5),(4,2,7),(8,3,5),(10,10,10),(15,0,0),(0,15,15),(7,7,0),(16,1,17),(100,200,300)]],FLIPS,[FLIPS.replace('answer+=x+y if z==0','answer+=int(x or y) if z==0'),FLIPS.replace('int(not(x or y))','int(not(x and y))')],['Charges one flip when both input bits are one but target bit is zero.','Requires both input bits to be one when target needs only one.'],flips_o,rfl,['Bits are independent, so minimize each position separately.','For target zero, flip every one among a and b; for target one, flip once only when both are zero.','Shift all three integers until no bits remain.','Summing independent per-bit minima gives the global minimum.'],'O(log M)','O(1)',5),
}
