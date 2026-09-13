"""Reviewed tree, parser, in-place, statistics, graph, and dynamic-programming imports."""
from collections import Counter, deque
from functools import lru_cache
from itertools import combinations, product

from .import_batch_055 import entry

def make_tree(serial):
 if not serial:return None
 root=[serial[0],None,None];q=deque([root]);i=1
 while q and i<len(serial):
  node=q.popleft()
  for side in (1,2):
   if i<len(serial) and serial[i] is not None:node[side]=[serial[i],None,None];q.append(node[side])
   i+=1
 return root
def serial_tree(root):
 if not root:return []
 out=[];q=deque([root])
 while q:
  node=q.popleft()
  if node is None:out.append(None)
  else:out.append(node[0]);q.extend(node[1:])
 while out and out[-1] is None:out.pop()
 return out
def sufficient_oracle(a):
 root=make_tree(a[0]);limit=a[1]
 def prune(node,total):
  if not node:return None
  total+=node[0]
  if node[1] is None and node[2] is None:return node if total>=limit else None
  node[1]=prune(node[1],total);node[2]=prune(node[2],total)
  return node if node[1] or node[2] else None
 return serial_tree(prune(root,0))
def minimum_digits_oracle(a):return sum(map(int,str(min(a[0]))))%2==0
def high_five_oracle(a):
 groups={}
 for student,score in a[0]:groups.setdefault(student,[]).append(score)
 return [[student,sum(sorted(scores,reverse=True)[:5])//5] for student,scores in sorted(groups.items())]
def brace_one_oracle(a):
 pieces=[]
 for part in a[0].replace('}','{').split('{'):
  if part:pieces.append(sorted(part.split(',')))
 return [''.join(x) for x in product(*pieces)]
def rotated_number(n):
 m={'0':'0','1':'1','6':'9','8':'8','9':'6'};s=str(n)
 return int(''.join(m[c] for c in reversed(s))) if all(c in m for c in s) else n
def confusing_two_oracle(a):return sum(rotated_number(x)!=x for x in range(1,a[0]+1))
def zeros_oracle(a):
 arr=a[0];expanded=[]
 for x in arr:expanded.extend([0,0] if x==0 else [x])
 return expanded[:len(arr)]
def labels_oracle(a):
 values,labels,want,limit=a;best=0
 for size in range(want+1):
  for chosen in combinations(range(len(values)),size):
   counts=Counter(labels[i] for i in chosen)
   if max(counts.values(),default=0)<=limit:best=max(best,sum(values[i] for i in chosen))
 return best
def scs_oracle(a):
 x,y=a
 @lru_cache(None)
 def solve(i,j):
  if i==len(x):return y[j:]
  if j==len(y):return x[i:]
  if x[i]==y[j]:return x[i]+solve(i+1,j+1)
  left=x[i]+solve(i+1,j);right=y[j]+solve(i,j+1)
  return min((left,right),key=lambda s:(len(s),s))
 return solve(0,0)
def stats_oracle(a):
 count=a[0];values=[i for i,c in enumerate(count) for _ in range(c)];n=len(values)
 return [values[0],values[-1],sum(values)/n,(values[(n-1)//2]+values[n//2])/2,max(range(256),key=lambda i:count[i])]
def car_oracle(a):
 trips,capacity=a
 for point in range(max((b for _,_,b in trips),default=0)+1):
  if sum(p for p,start,end in trips if start<=point<end)>capacity:return False
 return True
def brace_two_oracle(a):
 expression=a[0];i=0
 def parse(stop=False):
  nonlocal i
  union=set();current={''}
  while i<len(expression) and expression[i]!='}':
   if expression[i]==',':union|=current;current={''};i+=1
   else:
    if expression[i]=='{':i+=1;part=parse(True);i+=1
    else:part={expression[i]};i+=1
    current={x+y for x in current for y in part}
  return union|current
 return sorted(parse())
def less_k_oracle(a):
 nums,k=a;return max((x+y for i,x in enumerate(nums) for y in nums[i+1:] if x+y<k),default=-1)
def unique_k_oracle(a):
 s,k=a;return sum(len(set(s[i:i+k]))==k for i in range(len(s)-k+1))
def friends_oracle(a):
 logs,n=a;groups=[{i} for i in range(n)]
 for time,x,y in sorted(logs):
  merged=groups[x]|groups[y]
  for z in merged:groups[z]=merged
  if len(merged)==n:return time
 return -1
def maxmin_oracle(a):
 grid=a[0];rows=len(grid);cols=len(grid[0]);best=-1
 def walk(r,c,seen,score):
  nonlocal best
  if (r,c)==(rows-1,cols-1):best=max(best,score);return
  for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
   nr,nc=r+dr,c+dc
   if 0<=nr<rows and 0<=nc<cols and (nr,nc) not in seen:walk(nr,nc,seen|{(nr,nc)},min(score,grid[nr][nc]))
 walk(0,0,{(0,0)},grid[0][0]);return best
def candies_oracle(a):
 candies,n=a;out=[0]*n;give=1;i=0
 while candies:
  amount=min(give,candies);out[i%n]+=amount;candies-=amount;give+=1;i+=1
 return out
def zigzag_oracle(a):
 label=a[0];path=[]
 while label:
  path.append(label);level=label.bit_length();label=((1<<(level-1))+(1<<level)-1-label)//2
 return path[::-1]
def shelves_oracle(a):
 books,width=a
 @lru_cache(None)
 def solve(i):
  if i==len(books):return 0
  used=height=10**9;answer=10**9;used=height=0
  for j in range(i,len(books)):
   used+=books[j][0]
   if used>width:break
   height=max(height,books[j][1]);answer=min(answer,height+solve(j+1))
  return answer
 return solve(0)
def bool_oracle(a):
 s=a[0];i=0
 def parse():
  nonlocal i
  ch=s[i];i+=1
  if ch in 'tf':return ch=='t'
  op=ch;i+=1;values=[]
  while s[i]!=')':
   values.append(parse())
   if s[i]==',':i+=1
  i+=1
  return (not values[0]) if op=='!' else all(values) if op=='&' else any(values)
 return parse()
def defang_oracle(a):return a[0].replace('.','[.]')

def random_tree_limit(r):return [[r.randint(-8,12) for _ in range(r.randint(1,15))],r.randint(-15,30)]
def random_minimum(r):return [[r.randint(1,9999) for _ in range(r.randint(1,15))]]
def random_scores(r):
 ids=r.randint(1,4);return [[[student,r.randint(0,100)] for student in range(1,ids+1) for _ in range(r.randint(5,8))]]
def random_brace_one(r):return [''.join('{'+','.join(sorted(set(r.choice('abcde') for _ in range(r.randint(1,3)))))+'}' if r.random()<.6 else r.choice('abcde') for _ in range(r.randint(1,5)))]
def random_confusing_two(r):return [r.randint(1,5000)]
def random_zeros(r):return [[r.randint(0,5) for _ in range(r.randint(1,18))]]
def random_labels(r):
 n=r.randint(1,9);return [[r.randint(1,30) for _ in range(n)],[r.randint(1,4) for _ in range(n)],r.randint(1,n),r.randint(1,3)]
def random_scs(r):return [''.join(r.choice('abc') for _ in range(r.randint(0,7))),''.join(r.choice('abc') for _ in range(r.randint(0,7)))]
def random_stats(r):
 c=[0]*256
 for _ in range(r.randint(1,30)):c[r.randrange(20)]+=1
 return [c]
def random_trips(r):return [[[r.randint(1,6),start:=r.randint(0,8),r.randint(start+1,12)] for _ in range(r.randint(0,8))],r.randint(1,15)]
def random_brace_two(r):
 atoms=[r.choice('abcd') for _ in range(r.randint(1,4))];return ['{'+','.join(atoms)+'}' if len(atoms)>1 else atoms[0]]
def random_less(r):return [[r.randint(1,50) for _ in range(r.randint(1,12))],r.randint(2,80)]
def random_unique(r):
 s=''.join(r.choice('abcdef') for _ in range(r.randint(1,20)));return [s,r.randint(1,8)]
def random_friends(r):
 n=r.randint(2,8);pairs=list(combinations(range(n),2));r.shuffle(pairs);return [[[i+1,x,y] for i,(x,y) in enumerate(pairs[:r.randint(0,len(pairs))])],n]
def random_grid(r):
 rows,cols=r.randint(1,4),r.randint(1,4);return [[[r.randint(0,20) for _ in range(cols)] for _ in range(rows)]]
def random_candies(r):return [r.randint(1,200),r.randint(1,12)]
def random_zigzag(r):return [r.randint(1,10000)]
def random_books(r):
 width=r.randint(2,10);return [[[r.randint(1,width),r.randint(1,12)] for _ in range(r.randint(1,9))],width]
def random_bool(r):
 def make(depth=0):
  if depth>2 or r.random()<.4:return r.choice('tf')
  op=r.choice('!&|');count=1 if op=='!' else r.randint(1,4);return op+'('+','.join(make(depth+1) for _ in range(count))+')'
 return [make()]
def random_ip(r):return ['.'.join(str(r.randrange(256)) for _ in range(4))]

SUFFICIENT='''def prune_insufficient_nodes(root, limit):
 def prune(node,total):
  if node is None:return None
  total+=node.val
  if node.left is None and node.right is None:return node if total>=limit else None
  node.left=prune(node.left,total);node.right=prune(node.right,total)
  return node if node.left or node.right else None
 return prune(root,0)
'''
MINDIG='''def minimum_digit_sum_is_even(nums):
 return sum(map(int,str(min(nums))))%2==0
'''
HIGH='''def student_top_five(items):
 groups={}
 for student,score in items:groups.setdefault(student,[]).append(score)
 return [[student,sum(sorted(scores,reverse=True)[:5])//5] for student,scores in sorted(groups.items())]
'''
BRACE1='''def expand_simple_braces(expression):
 options=[];i=0
 while i<len(expression):
  if expression[i]=='{':j=expression.index('}',i);options.append(sorted(expression[i+1:j].split(',')));i=j+1
  else:options.append([expression[i]]);i+=1
 answer=['']
 for group in options:answer=[prefix+letter for prefix in answer for letter in group]
 return answer
'''
CONFUSE2='''def count_confusing_numbers(n):
 mapping={0:0,1:1,6:9,8:8,9:6};answer=0
 def build(value,rotated,place):
  nonlocal answer
  if value>n:return
  if value and value!=rotated:answer+=1
  for digit,turned in mapping.items():
   if value==0 and digit==0:continue
   build(value*10+digit,turned*place+rotated,place*10)
 build(0,0,1);return answer
'''
ZEROS='''def duplicate_zeros_fixed(arr):
 zeros=arr.count(0);i=len(arr)-1;j=i+zeros
 while i<j:
  if j<len(arr):arr[j]=arr[i]
  if arr[i]==0:
   j-=1
   if j<len(arr):arr[j]=0
  i-=1;j-=1
'''
LABELS='''def largest_labeled_sum(values, labels, num_wanted, use_limit):
 used={};answer=0
 for value,label in sorted(zip(values,labels),reverse=True):
  if num_wanted and used.get(label,0)<use_limit:answer+=value;used[label]=used.get(label,0)+1;num_wanted-=1
 return answer
'''
SCS='''def shortest_common_supersequence(str1, str2):
 from functools import lru_cache
 @lru_cache(None)
 def solve(i,j):
  if i==len(str1):return str2[j:]
  if j==len(str2):return str1[i:]
  if str1[i]==str2[j]:return str1[i]+solve(i+1,j+1)
  a=str1[i]+solve(i+1,j);b=str2[j]+solve(i,j+1);return min((a,b),key=lambda s:(len(s),s))
 return solve(0,0)
'''
STATS='''def sample_statistics(count):
 total=sum(count);minimum=next(i for i,c in enumerate(count) if c);maximum=next(i for i in range(255,-1,-1) if count[i]);mean=sum(i*c for i,c in enumerate(count))/total;mode=max(range(256),key=lambda i:count[i]);middle=[];seen=0
 for i,c in enumerate(count):
  for target in ((total-1)//2,total//2):
   if seen<=target<seen+c:middle.append(i)
  seen+=c
 return [minimum,maximum,mean,sum(middle)/2,mode]
'''
CAR='''def can_carpool(trips, capacity):
 changes={}
 for passengers,start,end in trips:changes[start]=changes.get(start,0)+passengers;changes[end]=changes.get(end,0)-passengers
 current=0
 for point in sorted(changes):
  current+=changes[point]
  if current>capacity:return False
 return True
'''
BRACE2='''def expand_nested_braces(expression):
 i=0
 def parse():
  nonlocal i
  union=set();current={''}
  while i<len(expression) and expression[i]!='}':
   if expression[i]==',':union|=current;current={''};i+=1;continue
   if expression[i]=='{':i+=1;part=parse();i+=1
   else:part={expression[i]};i+=1
   current={a+b for a in current for b in part}
  return union|current
 return sorted(parse())
'''
LESS='''def maximum_pair_below_k(nums, k):
 nums.sort();left=0;right=len(nums)-1;answer=-1
 while left<right:
  total=nums[left]+nums[right]
  if total<k:answer=max(answer,total);left+=1
  else:right-=1
 return answer
'''
UNIQUE='''def unique_k_substring_count(s, k):
 counts={};left=answer=0
 for right,char in enumerate(s):
  counts[char]=counts.get(char,0)+1
  if right-left+1>k:
   old=s[left];counts[old]-=1;left+=1
   if counts[old]==0:del counts[old]
  if right-left+1==k and len(counts)==k:answer+=1
 return answer
'''
FRIENDS='''def earliest_full_friendship(logs, n):
 parent=list(range(n));groups=n
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for time,x,y in sorted(logs):
  x,y=find(x),find(y)
  if x!=y:parent[x]=y;groups-=1
  if groups==1:return time
 return -1
'''
MAXMIN='''def maximum_minimum_path(grid):
 import heapq
 rows,cols=len(grid),len(grid[0]);heap=[(-grid[0][0],0,0)];seen={(0,0)}
 while heap:
  negative,r,c=heapq.heappop(heap);score=-negative
  if (r,c)==(rows-1,cols-1):return score
  for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
   nr,nc=r+dr,c+dc
   if 0<=nr<rows and 0<=nc<cols and (nr,nc) not in seen:seen.add((nr,nc));heapq.heappush(heap,(-min(score,grid[nr][nc]),nr,nc))
'''
CANDIES='''def distribute_candies(candies, num_people):
 answer=[0]*num_people;give=1;person=0
 while candies:
  amount=min(give,candies);answer[person%num_people]+=amount;candies-=amount;give+=1;person+=1
 return answer
'''
ZIGZAG='''def zigzag_tree_path(label):
 answer=[]
 while label:
  answer.append(label);level=label.bit_length();label=((1<<(level-1))+(1<<level)-1-label)//2
 return answer[::-1]
'''
SHELVES='''def minimum_shelf_height(books, shelf_width):
 dp=[0]+[10**9]*len(books)
 for end in range(1,len(books)+1):
  width=height=0
  for start in range(end-1,-1,-1):
   width+=books[start][0]
   if width>shelf_width:break
   height=max(height,books[start][1]);dp[end]=min(dp[end],dp[start]+height)
 return dp[-1]
'''
BOOL='''def evaluate_boolean_expression(expression):
 stack=[]
 for char in expression:
  if char in 'tf!&|':stack.append(char)
  elif char==')':
   values=[]
   while stack[-1] not in '!&|':values.append(stack.pop()=='t')
   op=stack.pop();value=(not values[0]) if op=='!' else all(values) if op=='&' else any(values);stack.append('t' if value else 'f')
 return stack[-1]=='t'
'''
DEFANG='''def defang_ip_address(address):
 return address.replace('.','[.]')
'''

def E(*args):
 if len(args)==15 and args[0]=='can_carpool':args=args[:3]+(['prefix-sums','sorting'],)+args[3:]
 return entry(*args)
def tests(rows):return rows
BATCH={
1080:E('prune_insufficient_nodes',[('root','TreeNode'),('limit','int')],'TreeNode | None',['trees','recursion'],['Delete every node not lying on any root-to-leaf path with sum at least limit.','Return the remaining root or None.'],[([[1,2,-3,-5,None,4,None],-1],'Only nodes belonging to a sufficiently large surviving path remain.'),([[1,2,3],10],'Neither root-to-leaf sum reaches ten, so return an empty tree.')],[[t,k] for t,k in [([1],1),([1],2),([1,2],3),([1,2],4),([1,2,3],3),([1,2,3],5),([5,-2,-3],3),([1,2,3,4,5],7),([1,-1,-1,2],2),([10,5,15],20),([-1,-2,-3],-3),([0,0,0],0),([1,2,None,3],6),([8,3,10,1,6],12)]],SUFFICIENT,[SUFFICIENT.replace('total>=limit','total>limit'),SUFFICIENT.replace('node.left or node.right','node.left and node.right')],['Rejects leaf paths exactly equal to the limit.','Keeps internal nodes only when both child branches survive.'],sufficient_oracle,random_tree_limit,['A node survives exactly when at least one descendant leaf completes a sufficient path.','Use postorder recursion carrying the root-to-node sum.','Prune children first; keep a leaf only when its sum reaches limit and an internal node when either child remains.','Postorder converts the global path condition into this exact subtree survival rule.'],'O(n)','O(height)',5),
1085:E('minimum_digit_sum_is_even',[('nums','list[int]')],'bool',['math','arrays'],['nums contains positive integers.','Return whether the digit sum of its minimum value is even.'],[([[34,23,1,24,75,33,54,8]],'The minimum is one, whose digit sum is odd.'),([[99,77,33,66,55]],'The minimum is 33 and its digit sum six is even.')],[[x] for x in [[1],[2],[10],[11],[12],[99,100],[34,23,1],[55,44,33],[999,123,456],[20,3,40],[101,11],[8,80,800],[19,28,37],[1000,999]]],MINDIG,[MINDIG.replace('min(nums)','max(nums)'),MINDIG.replace('%2==0','%2==1')],['Uses the maximum rather than minimum array value.','Returns true for odd digit sums.'],minimum_digits_oracle,random_minimum,['Only the smallest array element matters after selection.','Convert that number to decimal digits and sum them.','Return whether the sum modulo two is zero.','This directly implements the two independent selection and parity requirements.'],'O(n+digits)','O(digits)',3),
1086:E('student_top_five',[('items','list[list[int]]')],'list[list[int]]',['sorting','hash-maps'],['Each student has at least five scores.','Return IDs increasing with the floor average of each student’s top five.'],[([[[1,91],[1,92],[2,93],[2,97],[1,60],[2,77],[1,65],[1,87],[1,100],[2,100],[2,76]]],'Student one averages 87 and student two 88 across their best five.'),([[[1,100],[1,90],[1,80],[1,70],[1,60]]],'The sole top-five average is eighty.')],[[x] for x in [[[1,1],[1,2],[1,3],[1,4],[1,5]],[[2,100],[2,90],[2,80],[2,70],[2,60]],[[1,10],[1,20],[1,30],[1,40],[1,50],[2,50],[2,40],[2,30],[2,20],[2,10]],[[3,99],[3,98],[3,97],[3,96],[3,95],[3,1]],[[1,5],[1,5],[1,5],[1,5],[1,5]],[[5,0],[5,1],[5,2],[5,3],[5,4],[5,100]],[[1,90],[2,80],[1,70],[2,60],[1,50],[2,40],[1,30],[2,20],[1,10],[2,0]],[[9,10],[9,20],[9,30],[9,40],[9,50],[9,60]],[[2,1],[2,2],[2,3],[2,4],[2,5],[1,5],[1,4],[1,3],[1,2],[1,1]],[[4,100],[4,100],[4,100],[4,100],[4,99]],[[1,6],[1,7],[1,8],[1,9],[1,10],[1,100]],[[7,13],[7,27],[7,42],[7,58],[7,99]],[[3,1],[3,100],[3,2],[3,99],[3,3],[3,98]],[[8,80],[8,70],[8,60],[8,50],[8,40],[8,30]]]],HIGH,[HIGH.replace('reverse=True','reverse=False'),HIGH.replace('//5','//len(scores)')],['Averages the bottom five scores.','Divides the top-five sum by all submitted scores.'],high_five_oracle,random_scores,['Group scores by student ID.','Sort each student’s scores descending and select five.','Floor-divide their sum by five and emit IDs in sorted order.','Grouping isolates students and sorting identifies exactly their five greatest scores.'],'O(n log n)','O(n)',3),
1087:E('expand_simple_braces',[('expression','str')],'list[str]',['strings','backtracking'],['Brace groups contain comma-separated distinct letters and are not nested.','Return all choices in lexicographic order.'],[(['{a,b}c{d,e}f'],'Cartesian choices produce acdf,acef,bcdf,bcef.'),(['abcd'],'With no braces, the only expansion is abcd.')],[[s] for s in ['a','{a,b}','a{b,c}','{a,b}{c,d}','x{a,b}y','{a,b,c}d','a{b,c}d{e,f}','{z}','{a,c}b{d,e}','p{q,r,s}','{a,b}cde','ab{c,d,e}','{b,c}a{d,f}','{a,d}x{b,c}']],BRACE1,[BRACE1.replace('sorted(expression[i+1:j].split(\',\'))','expression[i+1:j].split(\',\')'),BRACE1.replace('for letter in group','for letter in group[:1]')],['Preserves unsorted group order instead of lexicographic output.','Uses only the first alternative from every group.'],brace_one_oracle,random_brace_one,['Parse literals as singleton choices and each brace group as sorted alternatives.','Build a list of option groups from left to right.','Take their Cartesian product by extending every current prefix with every next option.','Each output selects exactly one alternative per position and sorted groups preserve lexicographic order.'],'O(output length)','O(output length)',5),
1088:E('count_confusing_numbers',[('n','int')],'int',['backtracking','math'],['Count positive confusing numbers at most n.','Only digits 0,1,6,8,9 remain valid after rotation.'],[([20],'The confusing numbers through twenty are 6,9,10,16,18,19.'),([100],'Nineteen valid numbers rotate to a different value.')],[[n] for n in [1,5,6,9,10,11,18,19,20,50,99,101,500,1000]],CONFUSE2,[CONFUSE2.replace('value!=rotated','value==rotated'),CONFUSE2.replace('turned*place+rotated','rotated*10+turned')],['Counts rotationally unchanged numbers instead.','Builds the rotated digits in the wrong positional direction.'],confusing_two_oracle,random_confusing_two,['Generate only numbers composed of rotatable digits.','Carry both the forward number and its rotated value while appending digits.','Count a nonzero value when it is within n and differs from its rotation.','The DFS enumerates each valid-digit integer once and prunes every prefix exceeding n.'],'O(5^digits)','O(digits)',8),
1089:E('duplicate_zeros_fixed',[('arr','list[int]')],'None',['arrays','two-pointers'],['Duplicate every zero in place while keeping the original fixed length.','Elements shifted beyond the end are discarded.'],[([[1,0,2,3,0,4,5,0]],'The fixed array becomes 1,0,0,2,3,0,0,4.'),([[1,2,3]],'With no zeros the array is unchanged.')],[[x] for x in [[0],[1],[0,0],[1,0],[0,1],[1,0,2],[0,1,0],[1,2,0],[0,0,1,2],[1,0,0,2],[1,2,3,0],[0,1,2,3],[1,0,2,0,3],[9,0,8,7,0,6]]],ZEROS,[ZEROS.replace('zeros=arr.count(0)','zeros=0'),ZEROS.replace('if j<len(arr):arr[j]=0','if j<len(arr):arr[j]=arr[i]')],['Allocates no virtual extra positions for duplicated zeros.','Copies the original zero branch incorrectly instead of writing the duplicate.'],zeros_oracle,random_zeros,['Work backward so writes never destroy unread values.','Count zeros to locate each value’s virtual expanded index.','Copy values from the end; for zero, step back once more and write its duplicate when in bounds.','Backward virtual indexing is exactly expansion followed by truncation to fixed length.'],'O(n)','O(1)',5),
1090:E('largest_labeled_sum',[('values','list[int]'),('labels','list[int]'),('numWanted','int'),('useLimit','int')],'int',['greedy','sorting'],['Choose at most numWanted items and at most useLimit per label.','Maximize total value.'],[([[5,4,3,2,1],[1,1,2,2,3],3,1],'Choose values five,three,one from three labels for total nine.'),([[5,4,3,2,1],[1,3,3,3,2],3,2],'Choose five,four,three for total twelve.')],[[v,l,n,u] for v,l,n,u in [([1],[1],1,1),([5,4],[1,1],2,1),([5,4],[1,2],1,1),([5,4,3],[1,1,2],2,1),([10,9,8,7],[1,1,1,2],3,2),([1,2,3],[1,2,3],5,1),([9,8,7],[1,1,1],2,3),([5,4,3,2,1],[1,1,2,2,3],2,2),([6,5,4,3],[1,2,1,2],3,1),([100,1,99],[1,1,2],2,1),([4,4,4],[1,2,3],2,1),([8,7,6,5],[1,1,2,2],4,1),([3,2,1],[1,1,1],0,1),([20,10,5,4],[2,2,3,3],3,2)]],LABELS,[LABELS.replace('reverse=True','reverse=False'),LABELS.replace('<use_limit','<=use_limit')],['Chooses lowest values first.','Allows one item beyond each label limit.'],labels_oracle,random_labels,['Considering items by descending value makes every accepted choice locally best.','Track how many selections each label has used.','Accept an item while capacity remains and its label count is below useLimit.','Skipping a permitted higher value for a lower one cannot improve feasibility or total.'],'O(n log n)','O(labels)',5),
1092:E('shortest_common_supersequence',[('str1','str'),('str2','str')],'str',['dynamic-programming','strings'],['Both inputs must be subsequences of the result.','Return the lexicographically smallest among shortest valid supersequences.'],[(['abac','cab'],'Cabac contains both inputs and has minimum length five.'),(['aaaaaaaa','aaaaaaaa'],'Identical strings are already their own shortest supersequence.')],[[a,b] for a,b in [('','a'),('a',''),('a','a'),('a','b'),('ab','ba'),('abc','abc'),('abc','def'),('abac','cab'),('geek','eke'),('aaa','aa'),('abc','ac'),('xy','yz'),('banana','ana'),('cab','abc')]],SCS,[SCS.replace('key=lambda s:(len(s),s)','key=lambda s:(-len(s),s)'),SCS.replace('str1[i]==str2[j]','str1[i]!=str2[j]')],['Chooses the longer rather than shorter merge branch.','Merges unequal characters as though they matched.'],scs_oracle,random_scs,['Memoize the shortest answer for suffix index pairs.','Equal leading characters are shared; otherwise prepend either leading character and choose by length then lexicographic order.','Base cases append the untouched other suffix.','Every common supersequence begins with one permitted leading choice, so the recurrence is exhaustive and optimal.'],'O(n*m*(n+m))','O(n*m*(n+m))',8),
1093:E('sample_statistics',[('count','list[int]')],'list[float]',['arrays','statistics'],['count has 256 frequencies and at least one sample.','Return minimum,maximum,mean,median,mode; ties for mode use the smaller value.'],[([[0,1,3]+[0]*253],'Samples 1,2,2,2 give minimum 1, maximum 2, mean 1.75, median 2, mode 2.'),([[1]+[0]*255],'A sole zero makes every statistic zero.')],[[c] for c in [[1]+[0]*255,[0,1]+[0]*254,[1,1]+[0]*254,[0,2,1]+[0]*253,[0,1,1]+[0]*253,[0,0,5]+[0]*253,[1,0,1]+[0]*253,[0,3,0,2]+[0]*252,[2,2]+[0]*254,[0]*10+[1]+[0]*245,[0,1,2,3]+[0]*252,[5,4,3]+[0]*253,[0]*100+[2,1]+[0]*154,[0,0,1,0,1]+[0]*251]],STATS,[STATS.replace('sum(middle)/2','middle[0]'),STATS.replace('max(range(256),key=lambda i:count[i])','max(i for i,c in enumerate(count) if c)')],['Uses the lower middle sample instead of averaging two central samples.','Returns the maximum observed value as the mode.'],stats_oracle,random_stats,['Frequencies allow all statistics without expanding the sample.','Scan for endpoints, weighted sum, largest frequency, and the two central ranks.','Average the central values and weighted total appropriately.','Each statistic follows directly from the ordered frequency representation.'],'O(256)','O(1)',5),
1094:E('can_carpool',[('trips','list[list[int]]'),('capacity','int')],'bool',['Passengers board at start and leave before boarding at the same end position.','Return whether capacity is never exceeded.'],[([[[2,1,5],[3,3,7]],4],'At positions three and four, five passengers exceed capacity four.'),([[[2,1,5],[3,5,7]],3],'The first group exits at five before the next boards, so capacity three works.')],[[t,c] for t,c in [([],1),([[1,0,1]],1),([[2,0,2]],1),([[2,1,5],[3,3,7]],5),([[2,1,5],[3,5,7]],2),([[3,0,5],[2,2,4]],5),([[3,0,5],[2,2,4]],4),([[1,0,10],[1,2,3],[1,3,4]],2),([[5,5,10]],5),([[2,0,5],[2,0,5]],4),([[2,0,5],[2,0,5]],3),([[1,1,2],[1,2,3],[1,3,4]],1),([[4,2,8],[3,4,6]],6),([[2,0,3],[3,3,6],[4,6,9]],4)]],CAR,[CAR.replace('changes[end]=changes.get(end,0)-passengers','changes[end]=changes.get(end,0)+passengers'),CAR.replace('current>capacity','current>=capacity')],['Adds passengers again at their drop-off point.','Rejects occupancy exactly equal to capacity.'],car_oracle,random_trips,['Represent each trip as a pickup delta and drop-off delta.','Aggregate changes by position, with negative departures applied at the same coordinate.','Scan positions in order and reject when the running occupancy exceeds capacity.','The running sum equals passengers aboard on every interval between events.'],'O(n log n)','O(n)',5),
1096:E('expand_nested_braces',[('expression','str')],'list[str]',['recursion','parsing'],['Expressions use union commas, implicit concatenation, braces, and lowercase letters.','Return distinct expansions sorted lexicographically.'],[(['{a,b}{c,{d,e}}'],'Concatenation with nested union yields ac,ad,ae,bc,bd,be.'),(['{{a,z},a{b,c},{ab,z}}'],'Union removes duplicates and sorts to a,ab,ac,z.')],[[s] for s in ['a','{a,b}','a{b,c}','{a,b}{c,d}','{{a,b},c}','{a,{b,c}}','a,b','{a,b},c','a{b,{c,d}}','{{a,b},{b,c}}','{a,b}c{d,e}','{{a,z},a{b,c},{ab,z}}','{a,{b,c{d,e}}}','{{a,b}c,d}']],BRACE2,[BRACE2.replace('union|current','union&current'),BRACE2.replace('current={a+b','current={b+a')],['Intersects union branches instead of combining them.','Reverses concatenation operand order.'],brace_two_oracle,random_brace_two,['Recursive descent separates union at the current brace level from concatenation between adjacent factors.','Maintain a current product set and a union accumulator.','On comma merge current into union; on a factor take the Cartesian concatenation; on closing brace return their union.','These operations mirror the grammar precedence and sets remove duplicates.'],'O(output size)','O(output size)',8),
1099:E('maximum_pair_below_k',[('nums','list[int]'),('k','int')],'int',['sorting','two-pointers'],['Choose two distinct indices whose sum is strictly less than k.','Return the maximum sum or -1.'],[([[34,23,1,24,75,33,54,8],60],'Values 34 and 24 sum to the optimal 58.'),([[10,20,30],15],'No pair has sum below fifteen.')],[[x,k] for x,k in [([1],5),([1,2],4),([1,2],3),([5,5],11),([5,5],10),([1,3,5,7],9),([10,20,30],31),([2,2,2],5),([8,1,9,2],10),([50,10,20],100),([3,6,9,12],16),([1,100,2,99],102),([20,30,40],60),([7,14,21,28],36)]],LESS,[LESS.replace('total<k','total<=k'),LESS.replace('answer=max(answer,total)','answer=min(answer,total)')],['Allows a sum equal to k.','Keeps the minimum qualifying sum.'],less_k_oracle,random_less,['After sorting, pair sums move monotonically with either pointer.','If a pair is too large, decrease right; otherwise record it and increase left.','Continue until pointers meet.','For each left endpoint, the accepted right is its largest feasible partner, so no better pair is skipped.'],'O(n log n)','O(n)',3),
1100:E('unique_k_substring_count',[('s','str'),('k','int')],'int',['sliding-window','hash-maps'],['Count length-k substrings whose characters are all distinct.','Return zero when k exceeds the string length.'],[(['havefunonleetcode',5],'Six length-five windows contain five distinct characters.'),(['home',5],'No length-five substring exists.')],[[s,k] for s,k in [('a',1),('a',2),('aa',1),('aa',2),('ab',2),('abc',2),('abc',3),('abca',3),('aaaaa',2),('abcdef',4),('abacdef',4),('havefunonleetcode',4),('xyzxyz',3),('aabbccdde',2)]],UNIQUE,[UNIQUE.replace('len(counts)==k','len(counts)<=k'),UNIQUE.replace('right-left+1>k','right-left+1>=k')],['Accepts every full window even with repeated characters.','Evicts a character before the window actually exceeds k.'],unique_k_oracle,random_unique,['A fixed-length sliding window needs character frequencies to test uniqueness.','Add the entering character and remove the leaving one when length exceeds k.','Count a full window exactly when its map has k keys.','A length-k window has k distinct characters precisely under that condition.'],'O(n)','O(k)',5),
1101:E('earliest_full_friendship',[('logs','list[list[int]]'),('n','int')],'int',['union-find','sorting'],['Each log is [timestamp,a,b].','Return the earliest timestamp when all n people are connected, or -1.'],[([[[20190101,0,1],[20190104,3,4],[20190107,2,3],[20190211,1,5],[20190224,2,4],[20190301,0,3],[20190312,1,2],[20190322,4,5]],6],'The final component merges at timestamp 20190301.'),([[[0,2,0],[1,0,1],[3,0,3],[4,1,2],[7,3,1]],4],'All four become connected at timestamp three.')],[[l,n] for l,n in [([],2),([[1,0,1]],2),([[2,0,1],[1,1,2]],3),([[1,0,1]],3),([[1,0,1],[2,1,2]],3),([[5,0,1],[3,1,2]],3),([[1,0,1],[2,2,3],[3,1,2]],4),([[1,0,1],[2,0,1],[3,1,2]],3),([[10,0,4],[2,0,1],[4,1,2],[6,2,3],[8,3,4]],5),([[1,0,2],[2,1,3],[3,2,3]],4),([[4,0,1],[1,2,3],[2,1,2]],4),([[1,0,1],[2,2,3]],4),([[7,3,1],[3,0,3],[1,0,1],[4,1,2]],4),([[100,0,1],[200,1,2],[300,2,3]],4)]],FRIENDS,[FRIENDS.replace('sorted(logs)','logs'),FRIENDS.replace('groups-=1','groups+=1')],['Processes logs in input rather than chronological order.','Increases the component count after a successful union.'],friends_oracle,random_friends,['Sort events because connectivity only grows over time.','Union the endpoints and track the number of components.','Return the timestamp when a successful union reduces components to one.','That first chronological moment is exactly when everyone shares one connected component.'],'O(logs log logs)','O(n)',5),
1102:E('maximum_minimum_path',[('grid','list[list[int]]')],'int',['graphs','priority-queues'],['Move four-directionally from top-left to bottom-right.','Maximize the minimum cell value encountered along the path.'],[([[[5,4,5],[1,2,6],[7,4,6]]],'A path whose minimum is four is optimal.'),([[[2,2,1,2,2,2],[1,2,2,2,1,2]]],'The best path must touch value two until the destination, scoring two.')],[[g] for g in [[[1]],[[1,2]],[[2,1]],[[1],[2]],[[5,4],[3,2]],[[1,100],[1,1]],[[5,4,5],[1,2,6],[7,4,6]],[[3,3],[3,3]],[[9,1,9],[9,1,9],[9,9,9]],[[0,1],[2,3]],[[8,7,6],[5,4,3]],[[2,2,1],[1,2,2]],[[10,0,10],[10,10,10]],[[4,3,2],[5,1,6],[7,8,9]]]],MAXMIN,[MAXMIN.replace('min(score,grid[nr][nc])','max(score,grid[nr][nc])'),MAXMIN.replace('heapq.heappop(heap)','heapq.heappop(heap); heap=[]')],['Tracks the maximum cell rather than the path minimum.','Discards all alternative frontier paths after each pop.'],maxmin_oracle,random_grid,['This is a widest-path problem: a partial path is ranked by its minimum value.','Use a max-heap and finalize cells in descending path score.','A neighbor score is min(current score,neighbor value); return when the destination is popped.','The heap ensures no later path can improve a popped cell’s bottleneck score.'],'O(rows*cols log(rows*cols))','O(rows*cols)',5),
1103:E('distribute_candies',[('candies','int'),('numPeople','int')],'list[int]',['simulation','math'],['Give 1,2,3,... candies cyclically until none remain.','A final partial gift goes to the current person.'],[([7,4],'Gifts 1,2,3, then the remaining one produce 1,2,3,1.'),([10,3],'Gifts yield totals 5,2,3.')],[[c,n] for c,n in [(1,1),(2,1),(3,2),(4,2),(5,2),(6,3),(7,4),(8,4),(10,3),(20,4),(50,5),(100,10),(3,5),(25,2)]],CANDIES,[CANDIES.replace('min(give,candies)','give'),CANDIES.replace('person%num_people','person')],['Gives the full scheduled amount even when fewer candies remain.','Does not cycle the recipient index.'],candies_oracle,random_candies,['Direct simulation is bounded by roughly the square root of the candy count.','Track the next gift size and cycle person modulo numPeople.','Give min(scheduled,remaining), update totals, and stop at zero.','Each iteration reproduces exactly one gift specified by the process.'],'O(sqrt(candies))','O(numPeople)',3),
1104:E('zigzag_tree_path',[('label','int')],'list[int]',['trees','math'],['Rows alternate left-to-right and right-to-left labels in a perfect binary tree.','Return labels from root to the given node.'],[([14],'Mirroring parents yields path 1,3,4,14.'),([26],'The root path is 1,2,6,10,26.')],[[n] for n in [1,2,3,4,5,6,7,8,10,14,15,16,26,100]],ZIGZAG,[ZIGZAG.replace('//2','//1'),ZIGZAG.replace('answer[::-1]','answer')],['Fails to move up one binary-tree level.','Returns the leaf-to-root order.'],zigzag_oracle,random_zigzag,['At each level, mirror a zigzag label to its normal complete-tree position.','The mirrored parent equals (level minimum + level maximum - label)//2.','Append labels while climbing and reverse at the end.','The mirror formula accounts for row direction before taking the ordinary parent.'],'O(log label)','O(log label)',5),
1105:E('minimum_shelf_height',[('books','list[list[int]]'),('shelfWidth','int')],'int',['dynamic-programming','arrays'],['Books remain in order and each shelf width cannot exceed shelfWidth.','Minimize total shelf heights.'],[([[[1,1],[2,3],[2,3],[1,1],[1,1],[1,1],[1,2]],4],'Optimal shelf breaks give total height six.'),([[[1,3],[2,4],[3,2]],6],'All books fit one shelf of height four.')],[[b,w] for b,w in [([[1,1]],1),([[1,2],[1,3]],1),([[1,2],[1,3]],2),([[2,3],[2,4]],3),([[2,3],[2,4]],4),([[1,5],[3,2]],4),([[1,1],[1,2],[1,3]],2),([[3,4],[1,1],[1,1]],3),([[2,2],[2,2],[2,2]],4),([[1,10],[1,1],[1,1]],3),([[4,5],[2,6],[1,2]],6),([[1,3],[2,4],[3,2]],5),([[2,7],[1,2],[2,5],[1,3]],4),([[1,1],[2,3],[2,3],[1,1]],4)]],SHELVES,[SHELVES.replace('height=max(height','height=min(height'),SHELVES.replace('dp[start]+height','dp[start]+books[start][1]')],['Uses the shortest rather than tallest book as shelf height.','Charges only the first book height instead of the shelf maximum.'],shelves_oracle,random_books,['Let dp[end] be minimum height for the first end books.','Try every suffix that fits as the final shelf while maintaining its maximum height.','Transition from dp[start]+shelf height.','Every valid arrangement has one such final shelf, making the recurrence exhaustive.'],'O(n^2)','O(n)',5),
1106:E('evaluate_boolean_expression',[('expression','str')],'bool',['stacks','parsing','recursion'],['Expressions contain t,f, unary !, and n-ary & and |.','Evaluate the complete valid expression.'],[(['!(f)'],'Not false is true.'),(['|(&(t,f,t),!(t))'],'Both operands of the outer OR are false.')],[[s] for s in ['t','f','!(t)','!(f)','&(t,t)','&(t,f)','|(f,f)','|(f,t)','!(&(t,f))','&(!(f),t)','|(&(t,f),!(f))','!(!(t))','&(t,|(f,t))','|(&(t,t),&(f,t))']],BOOL,[BOOL.replace('all(values)','any(values)'),BOOL.replace('not values[0]','values[0]')],['Evaluates AND using any instead of all.','Ignores logical negation.'],bool_oracle,random_bool,['Operators remain on a stack until their closing parenthesis.','Push literals and operators, ignoring commas and opening parentheses.','At a close, pop operand literals through the operator, evaluate it, and push one literal result.','Nested subexpressions reduce before their enclosing operator, matching the grammar.'],'O(n)','O(n)',8),
1108:E('defang_ip_address',[('address','str')],'str',['strings'],['address is a valid IPv4 dotted-decimal string.','Replace each period with [.] exactly.'],[(['1.1.1.1'],'The defanged form is 1[.]1[.]1[.]1.'),(['255.100.50.0'],'Every one of the three dots is bracketed.')],[[s] for s in ['0.0.0.0','127.0.0.1','192.168.1.1','8.8.8.8','10.0.0.1','172.16.0.1','1.2.3.4','255.255.255.255','100.64.0.1','169.254.1.2','224.0.0.1','198.51.100.42','203.0.113.7','99.9.99.9']],DEFANG,[DEFANG.replace("'[.]'","'[]'"),DEFANG.replace("replace('.','[.]')","replace('1','[.]')")],['Removes the dot rather than retaining it inside brackets.','Replaces digit one instead of period separators.'],defang_oracle,random_ip,['Defanging is a literal separator substitution.','Use the string replace operation on periods only.','Replace each dot with the three-character token [.].','IPv4 has exactly three period separators, and no other characters are changed.'],'O(n)','O(n)',3),
}
for pid in (1080,):BATCH[pid]['params'][0]=('root','TreeNode | None','treenode');BATCH[pid]['adapter']='treenode'
BATCH[1089].update(result_mode='mutated_argument',mutated_parameter=0)
BATCH[1093]['comparator']='float_list'
BATCH[1080]['examples'].append(([[1,2,3,4,-99,-99,7,8,9,-99,-99,12,13,-99,14],1],'Pruning insufficient negative branches leaves the workbook tree 1,2,3,4,null,null,7,8,9,null,14.'))
BATCH[1087]['sample_contract_adapter']={'source_sample':'Input s = "{a,b}c{d,e}f" → Output ["acdf","acef","bcdf","bcef"].','arguments':['{a,b}c{d,e}f'],'expected':['acdf','acef','bcdf','bcef'],'reason':'The workbook calls the single expression parameter s; this reviewed function uses the clearer name expression.'}
BATCH[1089]['wrong'][1]='''def duplicate_zeros_fixed(arr):
 for i in range(len(arr)-1):
  if arr[i]==0:arr[i+1]=0
'''
BATCH[1089]['wrong_reasons'][1]='Overwrites the next unread value while scanning forward instead of shifting safely from the end.'
BATCH[1102]['wrong'][1]='''def maximum_minimum_path(grid):
 return min(grid[0][0],grid[-1][-1])
'''
BATCH[1102]['wrong_reasons'][1]='Assumes only the two endpoints determine the path bottleneck and ignores interior cells.'
BATCH[1103]['wrong'][0]=CANDIES.replace('amount=min(give,candies)','amount=candies')
BATCH[1103]['wrong_reasons'][0]='Gives all remaining candies to the current person instead of the scheduled amount.'
BATCH[1103]['wrong'][1]=CANDIES.replace('person%num_people','(person+1)%num_people')
BATCH[1103]['wrong_reasons'][1]='Starts the distribution at the second person instead of the first.'
BATCH[1104]['wrong'][0]='''def zigzag_tree_path(label):
 answer=[]
 while label:answer.append(label);label//=2
 return answer[::-1]
'''
BATCH[1104]['wrong_reasons'][0]='Uses ordinary heap-label parents and ignores the mirrored numbering on alternating rows.'
BATCH[1106]['examples'].append((['&(|(f))'],'The nested OR is false, so the enclosing AND is also false.'))
