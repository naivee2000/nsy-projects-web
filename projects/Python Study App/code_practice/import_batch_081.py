"""Reviewed assignment, graph, digit, string, stack, and matrix imports."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from math import gcd

from .import_batch_055 import entry

def previous_oracle(a):
 arr=a[0];candidates=[]
 for i in range(len(arr)):
  for j in range(i+1,len(arr)):
   copy=arr[:];copy[i],copy[j]=copy[j],copy[i]
   if copy<arr:candidates.append(copy)
 return max(candidates,default=arr)
def barcode_oracle(a):
 values=a[0];ordered=sorted(Counter(values).items(),key=lambda x:(-x[1],-x[0]));flat=[v for v,c in ordered for _ in range(c)];out=[0]*len(values);slots=list(range(0,len(values),2))+list(range(1,len(values),2))
 for slot,value in zip(slots,flat):out[slot]=value
 return out
def shortest_oracle(a):
 source,target=a
 if any(ch not in source for ch in target):return -1
 rounds=0;at=0
 while at<len(target):
  rounds+=1;before=at
  for ch in source:
   if at<len(target) and target[at]==ch:at+=1
  if at==before:return -1
 return rounds
def confusing_oracle(a):
 n=a[0];mapping={'0':'0','1':'1','6':'9','8':'8','9':'6'};text=str(n)
 return all(ch in mapping for ch in text) and ''.join(mapping[ch] for ch in reversed(text))!=text
def bikes_oracle(a):
 workers,bikes=a;pairs=sorted((abs(x-a)+abs(y-b),i,j) for i,(x,y) in enumerate(workers) for j,(a,b) in enumerate(bikes));answer=[-1]*len(workers);used=set()
 for _,i,j in pairs:
  if answer[i]<0 and j not in used:answer[i]=j;used.add(j)
 return answer
def rounding_oracle(a):
 prices,target=a;scaled=[int(x.replace('.','')) for x in prices];best=None
 for choices in product((0,1),repeat=sum(x%1000!=0 for x in scaled)):
  at=0;total=error=0
  for value in scaled:
   floor=value//1000
   if value%1000:
    up=choices[at];at+=1;total+=floor+up;error+=1000-value%1000 if up else value%1000
   else:total+=floor
  if total==target:best=error if best is None else min(best,error)
 return '-1' if best is None else f'{best/1000:.3f}'
def leads_oracle(a):
 n,edges,source,destination=a;adj=[[] for _ in range(n)]
 for x,y in edges:adj[x].append(y)
 def paths(node,seen):
  if node in seen:return False
  if not adj[node]:return node==destination
  return all(paths(other,seen|{node}) for other in adj[node])
 return paths(source,set())
def missing_oracle(a):
 nums,k=a;present=set(nums);value=nums[0]
 while k:
  value+=1
  if value not in present:k-=1
 return value
def equivalent_oracle(a):
 s1,s2,base=a;groups=[{chr(97+i)} for i in range(26)]
 for x,y in zip(s1,s2):
  merged=groups[ord(x)-97]|groups[ord(y)-97]
  for ch in merged:groups[ord(ch)-97]=merged
 return ''.join(min(groups[ord(ch)-97]) for ch in base)
def repeat_length_oracle(a):
 s=a[0]
 return max((size for size in range(1,len(s)) if any(s[i:i+size]==s[j:j+size] for i in range(len(s)-size+1) for j in range(i+1,len(s)-size+1))),default=0)
def valid_subarray_oracle(a):
 nums=a[0];return sum(all(nums[i]<=nums[k] for k in range(i,j+1)) for i in range(len(nums)) for j in range(i,len(nums)))
def fixed_oracle(a):return next((i for i,x in enumerate(a[0]) if i==x),-1)
def index_pairs_oracle(a):
 text,words=a;return [[i,j] for i in range(len(text)) for j in range(i,len(text)) if text[i:j+1] in words]
def bikes_two_oracle(a):
 workers,bikes=a
 return min(sum(abs(workers[i][0]-bikes[p[i]][0])+abs(workers[i][1]-bikes[p[i]][1]) for i in range(len(workers))) for p in permutations(range(len(bikes)),len(workers)))
def digit_range_oracle(a):
 d,low,high=a;return sum(str(value).count(str(d)) for value in range(low,high+1))
def gcd_string_oracle(a):
 x,y=a
 return x[:gcd(len(x),len(y))] if x+y==y+x else ''
def equal_rows_oracle(a):
 matrix=a[0];return max(sum(all((row[j]^mask[j])==(row[0]^mask[0]) for j in range(len(row))) for row in matrix) for mask in product((0,1),repeat=len(matrix[0])))
def neg_value(bits):return sum(bit*((-2)**i) for i,bit in enumerate(reversed(bits)))
def neg_bits(value):
 if value==0:return [0]
 out=[]
 while value:
  value,bit=divmod(value,-2)
  if bit<0:value+=1;bit+=2
  out.append(bit)
 return out[::-1]
def neg_add_oracle(a):return neg_bits(neg_value(a[0])+neg_value(a[1]))
def submatrix_oracle(a):
 matrix,target=a;rows=len(matrix);cols=len(matrix[0]);answer=0
 for r1 in range(rows):
  for r2 in range(r1,rows):
   for c1 in range(cols):
    for c2 in range(c1,cols):answer+=sum(matrix[r][c] for r in range(r1,r2+1) for c in range(c1,c2+1))==target
 return answer
def bigram_oracle(a):
 text,first,second=a;words=text.split();return [words[i+2] for i in range(len(words)-2) if words[i]==first and words[i+1]==second]

def random_previous(r):return [r.sample(range(1,30),r.randint(1,8))]
def random_barcodes(r):
 n=r.randint(1,12);k=r.randint(1 if n==1 else 2,min(5,n));vals=[i+1 for i in range(k)];out=[]
 while len(out)<n:
  choices=[v for v in vals if out.count(v)<(n+1)//2]
  out.append(r.choice(choices))
 r.shuffle(out);return [out]
def random_shortest(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,7))),''.join(r.choice('abcde') for _ in range(r.randint(1,15)))]
def random_confusing(r):return [r.randint(1,100000)]
def random_bikes(r):
 w=[r.sample(range(0,20),2) for _ in range(r.randint(1,5))];b=[r.sample(range(0,20),2) for _ in range(r.randint(len(w),7))];return [w,b]
def random_rounding(r):
 n=r.randint(1,8);p=[f'{r.randint(0,9)}.{r.randint(0,999):03d}' for _ in range(n)];return [p,r.randint(sum(int(x.split('.')[0]) for x in p),sum((int(x.replace('.',''))+999)//1000 for x in p))]
def random_graph(r):
 n=r.randint(1,8);edges=[[i,j] for i in range(n) for j in range(n) if i!=j and r.random()<.15];return [n,edges,r.randrange(n),r.randrange(n)]
def random_missing(r):
 vals=sorted(r.sample(range(0,40),r.randint(1,10)));return [vals,r.randint(1,12)]
def random_equivalent(r):
 n=r.randint(1,12);return [''.join(r.choice('abcdef') for _ in range(n)),''.join(r.choice('abcdef') for _ in range(n)),''.join(r.choice('abcdef') for _ in range(r.randint(1,15)))]
def random_repeat(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,16)))]
def random_valid_sub(r):return [[r.randint(0,20) for _ in range(r.randint(1,14))]]
def random_fixed(r):
 return [sorted(r.sample(range(-15,25),r.randint(1,15)))]
def random_index_pairs(r):
 text=''.join(r.choice('abcd') for _ in range(r.randint(1,18)));words=list({text[i:j] for i in range(len(text)) for j in range(i+1,min(len(text),i+5)+1) if r.random()<.12}|{'zz'});return [text,words]
def random_bikes_two(r):
 n=r.randint(1,5);m=r.randint(n,7);return [[[r.randint(0,10),r.randint(0,10)] for _ in range(n)],[[r.randint(0,10),r.randint(0,10)] for _ in range(m)]]
def random_digit(r):
 low=r.randint(1,700);return [r.randrange(10),low,r.randint(low,1000)]
def random_gcd_string(r):
 base=''.join(r.choice('ABC') for _ in range(r.randint(1,4)));x=base*r.randint(1,5);y=base*r.randint(1,5)
 if r.random()<.3:y+='Z'
 return [x,y]
def random_rows(r):return [[[r.randrange(2) for _ in range(r.randint(1,7))] for _ in range(r.randint(1,8))]]
def random_neg_add(r):return [neg_bits(r.randint(0,100)),neg_bits(r.randint(0,100))]
def random_submatrix(r):
 rows,cols=r.randint(1,4),r.randint(1,4);return [[[r.randint(-3,3) for _ in range(cols)] for _ in range(rows)],r.randint(-5,5)]
def random_bigram(r):
 words=[r.choice('abcde') for _ in range(r.randint(1,18))];return [' '.join(words),r.choice('abcde'),r.choice('abcde')]

PREVIOUS='''def previous_one_swap(arr):
 answer=arr[:]
 for i in range(len(answer)-2,-1,-1):
  if answer[i]>answer[i+1]:
   j=len(answer)-1
   while answer[j]>=answer[i] or (j>i+1 and answer[j]==answer[j-1]):j-=1
   answer[i],answer[j]=answer[j],answer[i];break
 return answer
'''
BARCODES='''def rearrange_barcodes(barcodes):
 from collections import Counter
 ordered=sorted(Counter(barcodes).items(),key=lambda x:(-x[1],-x[0]));values=[v for v,count in ordered for _ in range(count)];answer=[0]*len(barcodes);slots=list(range(0,len(barcodes),2))+list(range(1,len(barcodes),2))
 for slot,value in zip(slots,values):answer[slot]=value
 return answer
'''
SHORTEST='''def shortest_source_subsequences(source, target):
 if not target:return 0
 positions={char:[] for char in source}
 for i,char in enumerate(source):positions[char].append(i)
 import bisect
 rounds=1;at=-1
 for char in target:
  if char not in positions:return -1
  j=bisect.bisect_right(positions[char],at)
  if j==len(positions[char]):rounds+=1;at=positions[char][0]
  else:at=positions[char][j]
 return rounds
'''
CONFUSING='''def is_confusing_number(n):
 mapping={0:0,1:1,6:9,8:8,9:6};original=n;rotated=0
 while n:
  digit=n%10
  if digit not in mapping:return False
  rotated=rotated*10+mapping[digit];n//=10
 return rotated!=original
'''
BIKES='''def assign_campus_bikes(workers, bikes):
 pairs=sorted((abs(x-a)+abs(y-b),i,j) for i,(x,y) in enumerate(workers) for j,(a,b) in enumerate(bikes));answer=[-1]*len(workers);used=set()
 for distance,i,j in pairs:
  if answer[i]<0 and j not in used:answer[i]=j;used.add(j)
 return answer
'''
ROUNDING='''def minimum_rounding_error(prices, target):
 values=[int(x.replace('.','')) for x in prices];floor=sum(x//1000 for x in values);need=target-floor;fractions=sorted((x%1000 for x in values if x%1000),reverse=True)
 if need<0 or need>len(fractions):return '-1'
 error=sum(1000-x for x in fractions[:need])+sum(fractions[need:]);return f'{error/1000:.3f}'
'''
LEADS='''def all_paths_lead_to_destination(n, edges, source, destination):
 adjacent=[[] for _ in range(n)]
 for x,y in edges:adjacent[x].append(y)
 state=[0]*n
 def visit(node):
  if not adjacent[node]:return node==destination
  if state[node]:return state[node]==2
  state[node]=1
  if not all(visit(other) for other in adjacent[node]):return False
  state[node]=2;return True
 return visit(source)
'''
MISSING='''def kth_missing_sorted(nums, k):
 missing=lambda i:nums[i]-nums[0]-i;low,high=0,len(nums)
 while low<high:
  middle=(low+high)//2
  if missing(middle)<k:low=middle+1
  else:high=middle
 return nums[0]+k+low-1
'''
EQUIVALENT='''def smallest_equivalent_string(s1, s2, base_str):
 parent=list(range(26))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for a,b in zip(s1,s2):
  x,y=find(ord(a)-97),find(ord(b)-97)
  if x!=y:parent[max(x,y)]=min(x,y)
 return ''.join(chr(find(ord(ch)-97)+97) for ch in base_str)
'''
REPEAT='''def longest_repeating_substring_length(s):
 low,high=0,len(s)-1
 while low<high:
  middle=(low+high+1)//2;seen=set();found=False
  for i in range(len(s)-middle+1):
   part=s[i:i+middle]
   if part in seen:found=True;break
   seen.add(part)
  if found:low=middle
  else:high=middle-1
 return low
'''
VALID='''def count_valid_subarrays(nums):
 answer=0;stack=[]
 for value in nums:
  while stack and stack[-1]>value:stack.pop()
  stack.append(value);answer+=len(stack)
 return answer
'''
FIXED='''def smallest_fixed_point(arr):
 low,high=0,len(arr)-1;answer=-1
 while low<=high:
  middle=(low+high)//2
  if arr[middle]>=middle:
   if arr[middle]==middle:answer=middle
   high=middle-1
  else:low=middle+1
 return answer
'''
PAIRS='''def word_index_pairs(text, words):
 answer=[]
 for i in range(len(text)):
  for word in words:
   if text.startswith(word,i):answer.append([i,i+len(word)-1])
 return sorted(answer)
'''
BIKES2='''def minimum_bike_assignment_distance(workers, bikes):
 from functools import lru_cache
 @lru_cache(None)
 def solve(i,used):
  if i==len(workers):return 0
  return min(abs(workers[i][0]-bike[0])+abs(workers[i][1]-bike[1])+solve(i+1,used|1<<j) for j,bike in enumerate(bikes) if not used>>j&1)
 return solve(0,0)
'''
DIGITS='''def digit_occurrences_in_range(d, low, high):
 def count(n):
  if n<=0:return 0
  total=0;factor=1
  while factor<=n:
   lower=n%factor;current=n//factor%10;higher=n//(factor*10)
   if d:total+=higher*factor+(factor if current>d else lower+1 if current==d else 0)
   elif higher:total+=(higher-1)*factor+(factor if current>0 else lower+1)
   factor*=10
  return total
 return count(high)-count(low-1)
'''
GCDSTR='''def greatest_common_divisor_string(str1, str2):
 from math import gcd
 return str1[:gcd(len(str1),len(str2))] if str1+str2==str2+str1 else ''
'''
ROWS='''def maximum_equal_rows_after_flips(matrix):
 counts={}
 for row in matrix:
  key=tuple(value^row[0] for value in row);counts[key]=counts.get(key,0)+1
 return max(counts.values())
'''
NEGADD='''def add_negative_binary(arr1, arr2):
 i=len(arr1)-1;j=len(arr2)-1;carry=0;answer=[]
 while i>=0 or j>=0 or carry:
  total=carry+(arr1[i] if i>=0 else 0)+(arr2[j] if j>=0 else 0);answer.append(total&1);carry=-(total>>1);i-=1;j-=1
 while len(answer)>1 and answer[-1]==0:answer.pop()
 return answer[::-1]
'''
SUBMATRIX='''def count_target_submatrices(matrix, target):
 rows,cols=len(matrix),len(matrix[0]);answer=0
 for top in range(rows):
  sums=[0]*cols
  for bottom in range(top,rows):
   for c in range(cols):sums[c]+=matrix[bottom][c]
   seen={0:1};prefix=0
   for value in sums:prefix+=value;answer+=seen.get(prefix-target,0);seen[prefix]=seen.get(prefix,0)+1
 return answer
'''
BIGRAM='''def words_after_bigram(text, first, second):
 words=text.split();return [words[i+2] for i in range(len(words)-2) if words[i]==first and words[i+1]==second]
'''

def E(*args):
 if len(args)==15 and args[0]=='all_paths_lead_to_destination':args=args[:3]+(['graphs','depth-first-search'],)+args[3:]
 return entry(*args)
BATCH={
1053:E('previous_one_swap',[('arr','list[int]')],'list[int]',['arrays','greedy'],['Return the lexicographically largest array smaller than arr obtainable with at most one swap.','If impossible, return an unchanged copy.'],[([[3,2,1]],'Swap two and one to obtain the closest smaller arrangement 3,1,2.'),([[1,1,5]],'No swap can make this nondecreasing array smaller.')],[[x] for x in [[1],[2,1],[1,2],[3,1,2],[1,9,4,6,7],[3,1,1,3],[5,3,3,2],[2,2,1],[4,7,6,5,3,1],[9,8,7],[1,3,2,3],[6,1,5,4,3,2],[2,1,1],[8,4,6,2,5]]],PREVIOUS,[PREVIOUS.replace('range(len(answer)-2,-1,-1)','range(len(answer)-1)'),PREVIOUS.replace('answer[j]==answer[j-1]','answer[j]!=answer[j-1]')],['Chooses the first descent rather than the rightmost improvable position.','Skips distinct swap values instead of duplicate ones.'],previous_oracle,random_previous,['The changed prefix should be as late as possible, so find the rightmost descent.','Swap that value with the largest smaller suffix value, choosing the leftmost copy among duplicates.','Scan from right for the descent and from the end for the candidate while skipping duplicate copies.','These choices minimize the lexicographic decrease at the first changed position.'],'O(n)','O(n)',5),
1054:E('rearrange_barcodes',[('barcodes','list[int]')],'list[int]',['greedy','sorting'],['A valid no-equal-adjacent arrangement is guaranteed.','For deterministic grading, order value groups by decreasing frequency then decreasing value and fill even slots before odd slots.'],[([[1,1,1,2,2,2]],'Equal-frequency groups put value two in even slots and one in odd slots.'),([[1,1,1,1,2,2,3,3]],'The most frequent value occupies separated even positions first.')],[[x] for x in [[1],[1,2],[1,1,2],[1,1,2,2],[1,1,1,2,2],[3,3,3,2,2,1],[1,1,1,1,2,2,2],[5,5,4,4,3,3],[9,9,9,8,8,7,7],[1,2,3,4],[2,2,2,1,1,3],[6,6,6,6,5,5,5],[1,1,2,2,3,3,3],[4,4,4,2,2,1,1]]],BARCODES,[BARCODES.replace('range(0,len(barcodes),2)','range(1,len(barcodes),2)'),BARCODES.replace('(-x[1],-x[0])','(x[1],x[0])')],['Starts filling odd slots and produces an incomplete or adjacent arrangement.','Orders least frequent groups first.'],barcode_oracle,random_barcodes,['Place the largest frequency group into alternating positions so its copies cannot touch.','Sort groups by frequency and value, flatten them, and assign even then odd indices.','The guaranteed frequency bound fits the largest group in even slots.','All remaining copies fill the gaps, and the documented ordering makes tied outputs deterministic.'],'O(n log n)','O(n)',5),
1055:E('shortest_source_subsequences',[('source','str'),('target','str')],'int',['greedy','binary-search'],['Form target by concatenating subsequences of source.','Return the minimum number or -1 when a target character is absent.'],[(['abc','abcbc'],'Use abc followed by bc, so two subsequences suffice.'),(['abc','acdbc'],'Character d is absent from source, making construction impossible.')],[[s,t] for s,t in [('a','a'),('a','aa'),('abc','abc'),('abc','cba'),('xyz','xzyxz'),('aaaa','aaaaa'),('ab','baba'),('abc',''),('abc','dddd'),('cab','abcab'),('leetcode','codeleet'),('abca','caaac'),('xyz','zzzz'),('abcde','edcba')]],SHORTEST,[SHORTEST.replace('bisect_right','bisect_left'),SHORTEST.replace('rounds+=1','rounds-=1')],['Reuses the same source position for repeated characters.','Decrements rather than increments when a new subsequence is required.'],shortest_oracle,random_shortest,['Greedily consume the earliest source position after the current one.','Store sorted occurrence indices and binary-search the next index for each target character.','When none remains, start a new source subsequence at that character’s first occurrence.','Choosing an earlier available occurrence never reduces future choices, so greedy minimizes restarts.'],'O((source+target) log source)','O(source)',5),
1056:E('is_confusing_number',[('n','int')],'bool',['math','simulation'],['Valid rotated digits are 0,1,6,8,9.','Rotate 180 degrees, reversing digit order, and require a different valid number.'],[([6],'Six rotates to nine, so it is confusing.'),([11],'Eleven remains eleven after rotation, so it is not confusing.')],[[n] for n in [1,8,9,10,16,18,25,60,66,69,88,89,96,100]],CONFUSING,[CONFUSING.replace('rotated!=original','rotated==original'),CONFUSING.replace('mapping[digit]','digit')],['Accepts unchanged rotations instead of changed ones.','Fails to map six and nine while rotating.'],confusing_oracle,random_confusing,['Read digits from right to left, which is exactly the order of the rotated number.','Reject a digit outside the rotation map.','Accumulate rotated=10*rotated+mapped[digit], then compare with original.','The map handles glyph rotation and digit extraction supplies the required reversal.'],'O(digits)','O(1)',3),
1057:E('assign_campus_bikes',[('workers','list[list[int]]'),('bikes','list[list[int]]')],'list[int]',['sorting','greedy'],['Assign one distinct bike per worker.','Process pairs by distance, then worker index, then bike index.'],[([[[0,0],[2,1]],[[1,2],[3,3]]],'The globally ordered pairs assign bike one to worker zero and bike zero to worker one.'),([[[0,0],[1,1],[2,0]],[[1,0],[2,2],[2,1]]],'Tie-breaking by worker and bike indices determines the assignment.')],[[w,b] for w,b in [([[0,0]],[[1,1]]),([[0,0]],[[1,0],[0,1]]),([[0,0],[2,0]],[[1,0],[3,0]]),([[0,0],[10,10]],[[9,9],[1,1]]),([[0,0],[1,0]],[[0,1],[1,1]]),([[1,1],[2,2]],[[1,2],[2,1]]),([[0,0],[3,3]],[[1,1],[2,2],[4,4]]),([[5,5],[0,0]],[[1,0],[6,5]]),([[0,1],[1,0],[2,2]],[[0,0],[1,1],[3,3]]),([[2,3],[4,5]],[[3,4],[5,6]]),([[0,0],[2,1]],[[1,2],[3,3]]),([[1,2],[3,4],[5,6]],[[2,2],[4,4],[6,6]]),([[9,0],[0,9]],[[8,1],[1,8],[5,5]]),([[0,0],[1,2],[3,1]],[[2,0],[0,2],[3,3]])]],BIKES,[BIKES.replace('sorted((abs','sorted((-abs'),BIKES.replace('j not in used','j in used')],['Prioritizes farthest rather than nearest pairs.','Assigns only bikes already used by another worker.'],bikes_oracle,random_bikes,['The problem defines one global ordering over every worker-bike pair.','Sort tuples (distance,worker,bike).','Accept a tuple only when both its worker and bike remain unassigned.','Scanning the exact priority order makes each accepted assignment the mandated next choice.'],'O(workers*bikes log(workers*bikes))','O(workers*bikes)',5),
1058:E('minimum_rounding_error',[('prices','list[str]'),('target','int')],'str',['greedy','sorting'],['Prices have exactly three decimal digits and are nonnegative.','Round each up or down to reach target and return minimum error with three decimals, or -1.'],[([['0.700','2.800','4.900'],8],'Round to 1,2,5 for total eight and error one.'),([['1.500','2.500','3.000'],10],'Even rounding every fractional price up cannot reach ten, so return -1.')],[[p,t] for p,t in [(['1.000'],1),(['1.001'],1),(['1.001'],2),(['0.500','0.500'],1),(['1.200','2.300'],3),(['1.200','2.300'],4),(['9.999','0.001'],10),(['2.500','2.500','2.500'],8),(['0.100','0.200','0.300'],1),(['5.000','6.000'],11),(['1.999','2.001'],4),(['3.333','3.333','3.334'],10),(['0.700','2.800','4.900'],7),(['4.250','4.750'],9)]],ROUNDING,[ROUNDING.replace('reverse=True','reverse=False'),ROUNDING.replace('need>len(fractions)','need>=len(fractions)')],['Rounds up the smallest fractions instead of the largest.','Rejects the valid case requiring every fractional value to round up.'],rounding_oracle,random_rounding,['Flooring everything establishes the baseline; target determines exactly how many values must round up.','Rounding fraction f up costs 1-f instead of f, so larger fractions give greater savings.','Sort fractions descending and round up the required count.','The number of upward choices is fixed, and selecting greatest savings minimizes total absolute error.'],'O(n log n)','O(n)',5),
1059:E('all_paths_lead_to_destination',[('n','int'),('edges','list[list[int]]'),('source','int'),('destination','int')],'bool',['The directed graph may contain cycles.','Every maximal path from source must terminate at destination.'],[([3,[[0,1],[0,2]],0,2],'Path 0 to 1 terminates at the wrong sink, so false.'),([4,[[0,1],[0,2],[1,3],[2,3]],0,3],'Both branches terminate at destination three.')],[[n,e,s,d] for n,e,s,d in [(1,[],0,0),(2,[[0,1]],0,1),(2,[[0,1]],1,0),(2,[[0,1],[1,0]],0,1),(3,[[0,1],[1,2]],0,2),(3,[[0,1],[0,2]],0,1),(3,[[0,1],[1,1]],0,1),(4,[[0,1],[1,2],[2,3]],0,3),(4,[[0,1],[0,2],[1,3],[2,3]],0,3),(4,[[0,1],[0,2],[2,2]],0,1),(5,[[0,1],[1,2],[3,4]],0,2),(5,[[0,1],[1,2],[2,4],[1,3],[3,4]],0,4),(3,[],0,2),(4,[[0,3],[1,2]],0,3)]],LEADS,[LEADS.replace('node==destination','node!=destination'),LEADS.replace('state[node]=1','state[node]=2',1)],['Accepts terminal nodes other than the destination.','Marks an active node complete before exploring, allowing reachable cycles.'],leads_oracle,random_graph,['A valid path cannot reach a wrong sink or a cycle.','Use three-state DFS: unseen, visiting, and proven safe.','A leaf is valid only at destination; revisiting a visiting node is a cycle; mark safe after all children pass.','Every maximal continuation is checked, while memoized safe nodes avoid repeated work.'],'O(n+edges)','O(n)',5),
1060:E('kth_missing_sorted',[('nums','list[int]'),('k','int')],'int',['binary-search','arrays'],['nums is strictly increasing and k is positive.','Count missing integers starting after nums[0].'],[([[4,7,9,10],1],'Five is the first missing value after four.'),([[4,7,9,10],3],'The first three missing values are five,six,eight; return eight.')],[[n,k] for n,k in [([1],1),([1],5),([1,2],1),([1,3],1),([1,3],2),([4,7,9,10],2),([4,7,9,10],5),([0,2,5],3),([10,20],9),([2,3,4,7,11],5),([5,6,10],2),([1,10,20],15),([-5,-2,0],4),([100,101,105],10)]],MISSING,[MISSING.replace('nums[i]-nums[0]-i','nums[i]-nums[0]+i'),MISSING.replace('low-1','low')],['Adds the index instead of discounting present values.','Returns one beyond the kth missing value.'],missing_oracle,random_missing,['At index i, nums[i]-nums[0]-i values are missing before or at that position.','Binary-search the first index whose missing count reaches k.','Insert the count of present positions before that boundary into nums[0]+k.','The monotone missing-count function locates whether the answer lies inside or beyond the array.'],'O(log n)','O(1)',5),
1061:E('smallest_equivalent_string',[('s1','str'),('s2','str'),('baseStr','str')],'str',['union-find','strings'],['Paired characters define transitive equivalence.','Replace each base character with the smallest letter in its component.'],[(['parker','morris','parser'],'Equivalence groups map parser to makkek.'),(['hello','world','hold'],'The smallest representatives transform hold to hdld.')],[[a,b,c] for a,b,c in [('a','b','ab'),('abc','bcd','abcd'),('a','a','a'),('az','za','zoo'),('abc','cde','edcba'),('leetcode','programs','sourcecode'),('hello','world','hold'),('aaaa','bbbb','abba'),('xy','yz','xyz'),('mnop','nopq','qponm'),('ab','cd','abcd'),('z','a','zzz'),('abc','def','fed'),('pqr','qrs','spr')]],EQUIVALENT,[EQUIVALENT.replace('parent[max(x,y)]=min(x,y)','parent[min(x,y)]=max(x,y)'),EQUIVALENT.replace('chr(find','chr(max(find')],['Keeps the largest rather than smallest component representative.','Uses an unrelated maximum expression instead of the component minimum.'],equivalent_oracle,random_equivalent,['Union equivalent letters while retaining the smallest root.','Find representatives with path compression.','For each pair attach the larger root to the smaller; translate base characters through find.','Transitive closure is captured by components and the root invariant gives the lexicographically smallest replacement.'],'O(total alpha(26))','O(26)',5),
1062:E('longest_repeating_substring_length',[('s','str')],'int',['strings','binary-search'],['Occurrences may overlap.','Return the maximum repeated substring length, or zero.'],[(['abcd'],'Every nonempty substring is unique, so return zero.'),(['abbaba'],'Substring ab appears more than once and no longer substring repeats, so return two.')],[[s] for s in ['a','aa','aaa','abab','abcabc','banana','mississippi','abcdefa','aaaaa','ababa','xyzxyzx','abcdabc','zzxyzzxy','thethree']],REPEAT,[REPEAT.replace('seen.add(part)','seen=set()'),REPEAT.replace('low=middle','high=middle-1')],['Clears observed substrings each iteration and cannot detect repeats.','Shrinks rather than grows after finding a feasible length.'],repeat_length_oracle,random_repeat,['If a length repeats, every shorter prefix length also repeats.','Binary-search substring length and test duplicates with a set.','Grow the lower bound on success and shrink the upper bound on failure.','Monotonicity guarantees the final lower bound is the greatest feasible length.'],'O(n^2 log n)','O(n^2)',5),
1063:E('count_valid_subarrays',[('nums','list[int]')],'int',['monotonic-stack','arrays'],['A subarray is valid when its leftmost element is no greater than every later element.','Count all nonempty valid subarrays.'],[([[1,4,2,5,3]],'Eleven subarrays keep their first value as a minimum.'),([[3,2,1]],'Only the three singleton subarrays are valid.')],[[x] for x in [[1],[1,2],[2,1],[1,1],[1,2,3],[3,2,1],[2,1,2],[1,4,2,5,3],[5,5,5],[3,1,2,4],[1,3,2,2],[4,1,5,2,6],[0,2,0,2],[9,1,8,2,7]]],VALID,[VALID.replace('stack[-1]>value','stack[-1]>=value'),VALID.replace('answer+=len(stack)','answer+=1')],['Pops equal minima even though equality is valid.','Counts only singleton subarrays.'],valid_subarray_oracle,random_valid_sub,['A previous start remains valid until a smaller value appears.','Keep a nondecreasing stack of active starting values.','Pop values greater than the new endpoint; after pushing it, stack size is the number of valid subarrays ending here.','Each surviving stack entry represents one start whose first value is still minimal through this endpoint.'],'O(n)','O(n)',8),
1064:E('smallest_fixed_point',[('arr','list[int]')],'int',['binary-search','arrays'],['arr is strictly increasing.','Return the smallest index i with arr[i]==i, or -1.'],[([[-10,-5,0,3,7]],'Index three stores value three and is the first fixed point.'),([[0,2,5,8,17]],'Index zero is immediately a fixed point.')],[[x] for x in [[-1],[0],[1],[-1,1],[-2,0,2],[-5,-1,2,3],[-10,-5,0,3,7],[0,1,2],[1,2,3],[-3,-2,-1,3],[0,2,5,8,17],[-10,0,2,4,8],[2,3,4,5],[-4,-1,1,5,9]]],FIXED,[FIXED.replace('high=middle-1','low=middle+1'),FIXED.replace('answer=middle','return middle')],['Searches right after finding or passing a possible smaller fixed point.','Returns immediately and can miss a smaller fixed point.'],fixed_oracle,random_fixed,['For a strictly increasing array, arr[i]-i is nondecreasing.','Binary-search the first position where arr[i]>=i while recording equality.','Move left on equality to find the smallest fixed point.','Monotonicity rules out the discarded half at every comparison.'],'O(log n)','O(1)',3),
1065:E('word_index_pairs',[('text','str'),('words','list[str]')],'list[list[int]]',['strings','sorting'],['Return inclusive [start,end] pairs for every dictionary occurrence, including overlaps.','Sort pairs by start then end.'],[(['thestoryofleetcodeandme',['story','fleet','leetcode']],'Story occupies 3..7; fleet 9..13; leetcode 10..17.'),(['ababa',['aba','ab']],'Overlapping matches yield 0..1,0..2,2..3,2..4.')],[[t,w] for t,w in [('a',['a']),('a',['b']),('aaa',['a']),('aaa',['aa']),('abc',['a','bc']),('abcabc',['abc']),('mississippi',['is','sip']),('abab',['ab','ba']),('hello',['ll','lo']),('aaaa',['aa','aaa']),('xyz',['x','y','z']),('banana',['ana','na']),('leetcode',['leet','code','e']),('abcab',['ab','cab'])]],PAIRS,[PAIRS.replace('i+len(word)-1','i+len(word)'),PAIRS.replace('text.startswith(word,i)','word.startswith(text[i:])')],['Reports exclusive rather than inclusive end indices.','Tests whether the dictionary word starts with the remaining text.'],index_pairs_oracle,random_index_pairs,['Each answer begins at some text index and equals one dictionary word.','Test every word with startswith at every possible start.','Append the inclusive end and sort all pairs.','This enumerates every occurrence independently, including overlapping and nested words.'],'O(text*words*word length)','O(output)',3),
1066:E('minimum_bike_assignment_distance',[('workers','list[list[int]]'),('bikes','list[list[int]]')],'int',['bitmask-dp','dynamic-programming'],['There are at least as many bikes as workers.','Assign distinct bikes to minimize total Manhattan distance.'],[([[[0,0],[2,1]],[[1,2],[3,3]]],'Assign bikes zero and one respectively for distances three and three, total six.'),([[[0,0],[1,1],[2,0]],[[1,0],[2,2],[2,1]]],'The optimal one-to-one assignment totals four.')],[[w,b] for w,b in [([[0,0]],[[1,1]]),([[0,0]],[[1,0],[5,5]]),([[0,0],[2,0]],[[1,0],[3,0]]),([[0,0],[10,10]],[[9,9],[1,1]]),([[1,1],[2,2]],[[1,2],[2,1]]),([[0,0],[3,3]],[[1,1],[2,2],[4,4]]),([[5,5],[0,0]],[[1,0],[6,5]]),([[0,1],[1,0],[2,2]],[[0,0],[1,1],[3,3]]),([[2,3],[4,5]],[[3,4],[5,6]]),([[1,2],[3,4],[5,6]],[[2,2],[4,4],[6,6]]),([[9,0],[0,9]],[[8,1],[1,8],[5,5]]),([[0,0],[1,2],[3,1]],[[2,0],[0,2],[3,3]]),([[1,1],[8,8]],[[0,0],[9,9],[4,4]]),([[0,5],[5,0],[5,5]],[[1,5],[5,1],[4,4],[9,9]])]],BIKES2,[BIKES2.replace('if not used>>j&1','if used>>j&1'),BIKES2.replace('used|1<<j','used')],['Offers only already-used bikes.','Never marks the selected bike used, allowing reuse.'],bikes_two_oracle,random_bikes_two,['The worker index equals the number of selected bits, so state needs only the bike mask.','Try every unused bike for the next worker and memoize the minimum.','Add Manhattan distance plus the recursive cost with that bit set.','Every injective assignment corresponds to exactly one path through these states.'],'O(workers*2^bikes)','O(2^bikes)',5),
1067:E('digit_occurrences_in_range',[('d','int'),('low','int'),('high','int')],'int',['math','digit-dp'],['0<=d<=9 and 1<=low<=high.','Count digit occurrences in ordinary decimal representations without leading zeros.'],[([1,1,13],'One appears in 1,10,11,12,13 a total of six times.'),([0,1,20],'Zero appears in 10 and 20, twice.')],[[d,l,h] for d,l,h in [(1,1,1),(0,1,9),(0,1,10),(1,1,10),(2,1,22),(9,9,99),(0,10,100),(5,50,55),(3,1,333),(7,70,77),(1,98,102),(0,99,101),(4,400,450),(2,123,234)]],DIGITS,[DIGITS.replace('(higher-1)*factor','higher*factor'),DIGITS.replace('count(high)-count(low-1)','count(high)-count(low)')],['Counts leading zeros in each digit position.','Subtracts through low rather than through low-1.'],digit_range_oracle,random_digit,['Count occurrences from one through n independently at each decimal place.','Split n into higher, current, and lower digits around factor; handle zero by removing leading-zero blocks.','Answer range low..high as count(high)-count(low-1).','At each place, complete higher cycles contribute fixed blocks and the partial cycle depends only on current/lower.'],'O(log high)','O(1)',8),
1071:E('greatest_common_divisor_string',[('str1','str'),('str2','str')],'str',['strings','math'],['A divisor string repeated whole times must form both inputs.','Return the longest such string or empty.'],[(['ABCABC','ABC'],'ABC repeated twice forms the first string and once forms the second.'),(['LEET','CODE'],'The strings have no shared repeating base.')],[[a,b] for a,b in [('A','A'),('A','AA'),('AB','AB'),('ABAB','AB'),('ABCABC','ABC'),('AAAA','AA'),('ABAB','ABABAB'),('ABC','AB'),('LEET','CODE'),('XYZXYZ','XYZ'),('TAUTAU','TAU'),('ABCDABCD','ABCD'),('abab','ab'),('ABCABCABC','ABCABC')]],GCDSTR,[GCDSTR.replace('str1+str2==str2+str1','str1.startswith(str2)'),GCDSTR.replace('gcd(len(str1),len(str2))','min(len(str1),len(str2))')],['Uses one-way prefix compatibility rather than common repetition.','Returns the entire shorter string instead of the gcd-length base.'],gcd_string_oracle,random_gcd_string,['Compatible repeating strings commute under concatenation.','When str1+str2 equals str2+str1, their common base length is gcd of lengths.','Return that prefix, otherwise empty.','Commutation proves a shared primitive pattern, and the greatest common length gives its longest whole repetition.'],'O(n+m)','O(n+m)',3),
1072:E('maximum_equal_rows_after_flips',[('matrix','list[list[int]]')],'int',['hash-maps','matrices'],['One operation flips every value in a chosen column.','Return the maximum number of rows that can become internally constant after the same flips.'],[([[[0,1],[1,1]]],'No flip choice makes both rows constant, so the maximum is one.'),([[[0,1],[1,0]]],'The rows are complements and one column flip makes both constant.')],[[m] for m in [[[0]],[[0],[1]],[[0,0],[1,1]],[[0,1],[1,0]],[[0,1],[1,1]],[[1,0,1],[0,1,0]],[[1,1,0],[0,0,1],[1,1,0]],[[0,0,1],[0,1,1]],[[1,0],[1,0],[0,1]],[[0,1,0],[0,1,0]],[[1,1],[0,0],[1,1]],[[0,1,1,0],[1,0,0,1]],[[0,0,0],[1,1,1]],[[1,0,0],[0,1,1],[1,0,0]]]],ROWS,[ROWS.replace('value^row[0]','value'),ROWS.replace('max(counts.values())','min(counts.values())')],['Groups only identical rows and misses complementary patterns.','Returns the least frequent normalized row pattern.'],equal_rows_oracle,random_rows,['A row becomes constant under a flip mask determined up to complement by its first bit.','Normalize each row by XOR with its first value.','Rows with the same normalized tuple can all become constant together; return the largest frequency.','Equal normalized patterns mean rows are identical or complements in exactly the required columnwise way.'],'O(rows*cols)','O(rows*cols)',5),
1073:E('add_negative_binary',[('arr1','list[int]'),('arr2','list[int]')],'list[int]',['math','arrays'],['Inputs are canonical base -2 digit arrays.','Return their sum without leading zeros except [0].'],[([[1,1,1,1,1],[1,0,1]],'The values eleven and five sum to sixteen, represented as 10000.'),([[0],[0]],'Zero plus zero remains canonical zero.')],[[x,y] for x,y in [([0],[1]),([1],[1]),([1,0],[1]),([1,1],[1]),([1,0,0],[1,0]),([1,1,0],[1,1]),([1,0,1],[1,0,1]),([1,1,1],[1]),([1,0,0,0],[1]),([1,1,1,1],[1,0]),([1,0,1,0],[1,1]),([1,1,0,1],[1,0,0]),([1,0,0,1],[1,1,1]),([1,1,1,1,1],[1,0,1])]],NEGADD,[NEGADD.replace('carry=-(total>>1)','carry=total>>1'),NEGADD.replace('total&1','total%3')],['Uses positive-base carry propagation.','Emits ternary remainders rather than binary digits.'],neg_add_oracle,random_neg_add,['At each position choose a binary output digit with the same parity as the total.','The remaining value divided by -2 becomes carry=-(total>>1).','Process both arrays from right to left, trim high zeros, and reverse.','The invariant exactly preserves the unprocessed base -2 value plus carry.'],'O(max lengths)','O(max lengths)',5),
1074:E('count_target_submatrices',[('matrix','list[list[int]]'),('target','int')],'int',['prefix-sums','matrices','hash-maps'],['Matrix values and target may be negative.','Count all nonempty rectangular submatrices summing to target.'],[([[[0,1,0],[1,1,1],[0,1,0]],0],'The four corner singleton zeros are the only zero-sum rectangles.'),([[[1,-1],[-1,1]],0],'Five rectangles have sum zero.')],[[m,t] for m,t in [([[0]],0),([[1]],0),([[1]],1),([[1,-1]],0),([[1],[-1]],0),([[1,2],[3,4]],3),([[1,-1],[-1,1]],1),([[0,0],[0,0]],0),([[1,2,3]],3),([[1],[2],[3]],3),([[2,-2,2],[-2,2,-2]],0),([[1,0,1],[0,-1,0]],1),([[3,-1],[-2,0]],0),([[1,2],[-3,4]],4)]],SUBMATRIX,[SUBMATRIX.replace('prefix-target','prefix+target'),SUBMATRIX.replace('seen={0:1}','seen={}')],['Looks for prefixes differing by negative target.','Omits the empty prefix and misses rectangles starting at the first column.'],submatrix_oracle,random_submatrix,['Fix top and bottom rows to collapse the rectangle problem into one-dimensional column sums.','For each collapsed array, count target-sum subarrays with prefix frequencies.','Repeat for every row pair, seeding prefix zero once.','Every rectangle has one unique top-bottom pair and one contiguous column interval counted exactly once.'],'O(rows^2*cols)','O(cols)',8),
1078:E('words_after_bigram',[('text','str'),('first','str'),('second','str')],'list[str]',['strings','arrays'],['Words are separated by single spaces.','Return every word immediately following the consecutive pair first,second in order.'],[(['alice is a good girl she is a good student','a','good'],'The pair a good is followed by girl and later student.'),(['we will we will rock you','we','will'],'The two occurrences are followed by we and rock.')],[[t,a,b] for t,a,b in [('a b c','a','b'),('a b','a','b'),('a a a','a','a'),('one two three four','two','three'),('x y z x y q','x','y'),('hello world again','hello','world'),('a b c a b d','a','b'),('we will we will rock you','we','will'),('no match here','x','y'),('first second third','first','second'),('a good day a good night','a','good'),('red blue red blue green','red','blue'),('one one two one one three','one','one'),('the quick brown fox','quick','brown')]],BIGRAM,[BIGRAM.replace('words[i+2]','words[i+1]'),BIGRAM.replace('words[i+1]==second','words[i+2]==second')],['Returns the second bigram word instead of the following word.','Searches for first,anything,second rather than adjacent first,second.'],bigram_oracle,random_bigram,['Split text once into words.','Inspect each triple of consecutive words.','When its first two equal first and second, append the third.','Every qualifying occurrence has exactly one such triple and scanning preserves order.'],'O(words)','O(words)',3),
}

BATCH[1061]['wrong'][1]=EQUIVALENT.replace("return ''.join(chr(find(ord(ch)-97)+97) for ch in base_str)","return ''.join(ch for ch in base_str)")
BATCH[1061]['wrong_reasons'][1]='Builds equivalence classes but returns the unchanged base string.'
BATCH[1066]['wrong'][0]='''def minimum_bike_assignment_distance(workers, bikes):
 return sum(abs(worker[0]-bikes[0][0])+abs(worker[1]-bikes[0][1]) for worker in workers)
'''
BATCH[1066]['wrong_reasons'][0]='Assigns bike zero to every worker instead of enforcing distinct bikes.'
