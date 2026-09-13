"""Second half of batch 89: paths, simulation, counting, and number theory."""
from collections import Counter
from math import gcd
from .import_batch_055 import entry

def folders_o(a):
 out=[]
 for p in sorted(a[0]):
  if not out or not p.startswith(out[-1]+'/'):out.append(p)
 return out
def transform_o(a):
 x=a[0][:]
 while True:
  y=x[:]
  for i in range(1,len(x)-1):y[i]=x[i]+(x[i]<x[i-1] and x[i]<x[i+1])-(x[i]>x[i-1] and x[i]>x[i+1])
  if y==x:return y
  x=y
def swaps_o(a):
 x=sum(c!=d for c,d in zip(*a) if c=='x');y=sum(c!=d for c,d in zip(*a) if c=='y')
 return -1 if (x+y)%2 else x//2+y//2+2*(x%2)
def nice_o(a):
 nums,k=a;return sum(sum(v%2 for v in nums[i:j])==k for i in range(len(nums)) for j in range(i+1,len(nums)+1))
def valid_o(a):
 s=a[0];bad=set();stack=[]
 for i,c in enumerate(s):
  if c=='(':stack.append(i)
  elif c==')':
   if stack:stack.pop()
   else:bad.add(i)
 bad.update(stack);return ''.join(c for i,c in enumerate(s) if i not in bad)
def good_o(a):
 g=0
 for x in a[0]:g=gcd(g,x)
 return g==1
def odd_o(a):
 m,n,idx=a;grid=[[0]*n for _ in range(m)]
 for r,c in idx:
  for j in range(n):grid[r][j]+=1
  for i in range(m):grid[i][c]+=1
 return sum(v%2 for row in grid for v in row)
def shift_o(a):
 g,k=a;flat=sum(g,[]);k%=len(flat);flat=flat[-k:]+flat[:-k] if k else flat;w=len(g[0]);return [flat[i:i+w] for i in range(0,len(flat),w)]
def time_o(a):return sum(max(abs(x-u),abs(y-v)) for (x,y),(u,v) in zip(a[0],a[0][1:]))
def servers_o(a):
 g=a[0];rs=[sum(r) for r in g];cs=[sum(g[i][j] for i in range(len(g))) for j in range(len(g[0]))];return sum(g[i][j] and (rs[i]>1 or cs[j]>1) for i in range(len(g)) for j in range(len(g[0])))

def rf(r):
 roots=[f'/{c}' for c in r.sample(list('abcdef'),r.randint(1,5))];items=roots+[p+'/x'+str(i) for i,p in enumerate(roots) if r.random()<.7];r.shuffle(items);return [items]
def rt(r):return [[r.randint(1,20) for _ in range(r.randint(3,12))]]
def rs(r):
 n=r.randint(1,20);a=''.join(r.choice('xy') for _ in range(n));b=list(a);indices=r.sample(range(n),2*(r.randint(0,n//2)))
 for i in indices:b[i]='y' if b[i]=='x' else 'x'
 return [a,''.join(b)]
def rn(r):return [[r.randint(0,20) for _ in range(r.randint(1,20))],r.randint(1,6)]
def rv(r):return [''.join(r.choice('()abc') for _ in range(r.randint(1,40)))]
def rg(r):return [[r.randint(1,100) for _ in range(r.randint(1,15))]]
def ro(r):
 m,n=r.randint(1,8),r.randint(1,8)
 return [m,n,[[r.randrange(m),r.randrange(n)] for _ in range(r.randint(0,12))]]
def rshift(r):
 h,w=r.randint(1,5),r.randint(1,5);return [[[r.randint(-9,9) for _ in range(w)] for _ in range(h)],r.randint(0,50)]
def rp(r):return [[[r.randint(-20,20),r.randint(-20,20)] for _ in range(r.randint(1,15))]]
def rserver(r):
 h,w=r.randint(1,6),r.randint(1,6);return [[[r.randint(0,1) for _ in range(w)] for _ in range(h)]]

F='''def remove_subfolders(folder):
 out=[]
 for path in sorted(folder):
  if not out or not path.startswith(out[-1]+'/'):out.append(path)
 return out
'''
T='''def transform_array_until_stable(arr):
 current=arr[:]
 while True:
  following=current[:]
  for i in range(1,len(current)-1):
   if current[i]<current[i-1] and current[i]<current[i+1]:following[i]+=1
   elif current[i]>current[i-1] and current[i]>current[i+1]:following[i]-=1
  if following==current:return following
  current=following
'''
S='''def minimum_xy_swaps(s1, s2):
 x=sum(a!=b and a=='x' for a,b in zip(s1,s2));y=sum(a!=b and a=='y' for a,b in zip(s1,s2))
 return -1 if (x+y)%2 else x//2+y//2+2*(x%2)
'''
N='''def count_nice_subarrays(nums, k):
 counts={0:1};odd=answer=0
 for value in nums:odd+=value%2;answer+=counts.get(odd-k,0);counts[odd]=counts.get(odd,0)+1
 return answer
'''
V='''def minimum_remove_valid_parentheses(s):
 chars=list(s);stack=[]
 for i,c in enumerate(chars):
  if c=='(':stack.append(i)
  elif c==')':
   if stack:stack.pop()
   else:chars[i]=''
 for i in stack:chars[i]=''
 return ''.join(chars)
'''
G='''def is_good_array(nums):
 from math import gcd
 value=0
 for number in nums:value=gcd(value,number)
 return value==1
'''
O='''def odd_matrix_cells(m, n, indices):
 rows=[0]*m;cols=[0]*n
 for r,c in indices:rows[r]^=1;cols[c]^=1
 return sum(rows[i]^cols[j] for i in range(m) for j in range(n))
'''
SHIFT='''def shift_grid(grid, k):
 flat=sum(grid,[]);k%=len(flat)
 if k:flat=flat[-k:]+flat[:-k]
 width=len(grid[0]);return [flat[i:i+width] for i in range(0,len(flat),width)]
'''
P='''def minimum_point_visit_time(points):
 return sum(max(abs(x-u),abs(y-v)) for (x,y),(u,v) in zip(points,points[1:]))
'''
SERVER='''def communicating_server_count(grid):
 rows=[sum(row) for row in grid];cols=[sum(row[j] for row in grid) for j in range(len(grid[0]))]
 return sum(grid[i][j] and (rows[i]>1 or cols[j]>1) for i in range(len(grid)) for j in range(len(grid[0])))
'''

E=entry
def spec(pid,name,params,ret,topics,constraints,examples,hidden,ref,wrong,reasons,oracle,gen,hints,time='O(n)',space='O(n)',difficulty=5):return E(name,params,ret,topics,constraints,examples,hidden,ref,wrong,reasons,oracle,gen,hints,time,space,difficulty)
BATCH={
1233:spec(1233,'remove_subfolders',[('folder','list[str]')],'list[str]',['sorting','strings'],['Paths are distinct absolute folder paths.','Remove every path having another input path as a slash-delimited parent.'],[([['/a','/a/b','/c/d','/c/d/e','/c/f']],'The parent /a removes /a/b and /c/d removes /c/d/e.'),([['/a','/ab','/a/b']],'The prefix /a is not a parent of /ab because no slash follows it.')],[[x] for x in [['/a'],['/a','/a/b'],['/a/b','/a'],['/a','/ab'],['/a/b','/a/c'],['/x','/x/y','/x/y/z'],['/a/b/c','/a/b/d'],['/z','/a','/a/q'],['/aa','/aa/b','/a'],['/one/two','/one'],['/p/q','/p2'],['/a/b','/a/bc'],['/root/a','/root/b'],['/m','/m/n','/z/z']]],F,[F.replace("out[-1]+'/'","out[-1]"),F.replace('sorted(folder)','folder')],['Confuses ordinary string prefixes with folder ancestry.','Relies on input order and may accept a child before its parent.'],folders_o,rf,['Lexicographic sorting places each parent immediately before all descendants.','Keep a path unless it starts with the last kept path plus slash.','Append only top-level surviving paths.','A previous surviving parent suppresses its entire contiguous descendant range.']),
1243:spec(1243,'transform_array_until_stable',[('arr','list[int]')],'list[int]',['simulation','arrays'],['Endpoints never change.','Each day updates all interior values simultaneously until stable.'],[([[6,2,3,4]],'Two rises to three on the first day, after which the array is stable.'),([[1,6,3,4,3,5]],'Repeated simultaneous peak and valley changes eventually stabilize the interior.')],[[x] for x in [[1,2,3],[3,2,1],[1,3,1],[3,1,3],[1,1,1],[1,5,2,4,1],[6,2,3,4],[1,6,3,4,3,5],[9,1,9,1,9],[2,8,4,6,2],[1,2,2,1],[5,4,3,2,1],[1,2,3,4,5],[10,1,5,1,10]]],T,['''def transform_array_until_stable(arr):
 following=arr[:]
 for i in range(1,len(arr)-1):
  if arr[i]<arr[i-1] and arr[i]<arr[i+1]:following[i]+=1
  elif arr[i]>arr[i-1] and arr[i]>arr[i+1]:following[i]-=1
 return following
''',T.replace("following[i]+=1","following[i]-=1")],['Performs only one day and returns before later changes reach stability.','Moves valleys downward rather than upward.'],transform_o,rt,['Copy the current day before changing any interior position.','Raise strict valleys by one and lower strict peaks by one.','Repeat until a full day makes no change.','Copying enforces simultaneous updates; bounded neighbor gaps guarantee convergence.'],'O(n*range)','O(n)'),
1247:spec(1247,'minimum_xy_swaps',[('s1','str'),('s2','str')],'int',['greedy','strings'],['Strings have equal length and contain only x and y.','One swap exchanges characters at different positions across the two strings.'],[(['xx','yy'],'Two xy mismatches are fixed by one cross-string swap.'),(['xy','yx'],'Opposite mismatch types require two swaps.')],[[a,b] for a,b in [('x','x'),('x','y'),('xx','xx'),('yy','yy'),('xx','yy'),('xy','yx'),('xxx','yyy'),('xxyy','yyxx'),('xyxy','yxyx'),('xxxx','yyyy'),('xy','xy'),('xxy','yxx'),('yyxx','xxyy'),('xyxxy','yxyxx')]],S,[S.replace('2*(x%2)','x%2'),S.replace("return -1 if (x+y)%2 else","return")],['Charges one rather than two swaps for the remaining opposite-type pair.','Never rejects an odd number of mismatches.'],swaps_o,rs,['Count xy and yx mismatch orientations.','Two equal orientations cost one swap; one leftover of each costs two.','An odd total mismatch count is impossible.','Pairing identical orientations is optimal, leaving at most one mixed pair.'],'O(n)','O(1)'),
1248:spec(1248,'count_nice_subarrays',[('nums','list[int]'),('k','int')],'int',['prefix-sums','hash-maps'],['Return the number of contiguous subarrays containing exactly k odd values.','k is positive.'],[([[1,1,2,1,1],3],'Two subarrays contain exactly three odd values.'),([[2,4,6],1],'No subarray contains an odd value.')],[[a,k] for a,k in [([1],1),([2],1),([1,1],1),([1,1],2),([2,1,2],1),([1,2,1],1),([1,2,1],2),([2,2,1,2,2],1),([1,1,1],2),([2,4,1,3],2),([1,2,2,2],1),([3,5,2,7],2),([0,1,0,1,0],1),([2,2,2,1],2)]],N,[N.replace('odd-k','odd+k'),N.replace('counts={0:1}','counts={}')],['Looks for a future larger prefix count.','Omits the empty prefix, losing subarrays starting at index zero.'],nice_o,rn,['Map each prefix odd-count to how often it occurred.','At current count c, earlier prefixes c-k begin valid subarrays.','Add their frequency, then record c.','Subtracting equal prefix counts leaves exactly k odds.'],'O(n)','O(n)'),
1249:spec(1249,'minimum_remove_valid_parentheses',[('s','str')],'str',['stacks','strings'],['Remove the fewest parentheses to make the string valid.','Letters remain in their original order.'],[(['lee(t(c)o)de)'],'Removing the unmatched final close parenthesis yields lee(t(c)o)de.'),(['a)b(c)d'],'Removing the early unmatched close yields ab(c)d.')],[[s] for s in ['a','()','(',')','(a)','a(b)c','))((','((a)','a))','(a))(','(()','())','x(y(z)','x)y(z)','((x))y)']],V,[V.replace("else:chars[i]=''","else:pass"),V.replace("for i in stack:chars[i]=''","pass")],['Keeps unmatched closing parentheses.','Keeps unmatched opening parentheses.'],valid_o,rv,['Track indices of unmatched opening parentheses.','Match each close to the latest open; mark unmatched closes immediately.','After scanning, remove opens left on the stack and every marked close.','Every removed parenthesis is unmatched, and retaining all matched pairs minimizes removals.'],'O(n)','O(n)'),
1250:spec(1250,'is_good_array',[('nums','list[int]')],'bool',['number-theory','math'],['All values are positive.','Return whether an integer linear combination of the values can equal one.'],[([[12,5,7,23]],'The overall greatest common divisor is one, so Bézout coefficients exist.'),([[3,6]],'Every integer combination is divisible by three.')],[[x] for x in [[1],[2],[2,3],[4,6],[6,10,15],[7,14,21],[8,12,18],[17,19],[100,25],[9,28,35],[2,4,8,16],[11,22,33,5],[30,42,70],[999,1000]]],G,[G.replace('value==1','value!=1'),'''def is_good_array(nums):
 return 1 in nums
'''],['Reverses the gcd criterion.','Requires a literal one and ignores combinations of coprime larger values.'],good_o,rg,['Bézout’s identity connects integer combinations to the overall gcd.','Fold gcd across all values.','Return true exactly when the final gcd is one.','All combinations are multiples of the gcd, and the gcd itself is an integer combination.'],'O(n log M)','O(1)',8),
1252:spec(1252,'odd_matrix_cells',[('m','int'),('n','int'),('indices','list[list[int]]')],'int',['matrices','parity'],['Each operation increments one whole row and one whole column.','Return the number of cells with odd final values.'],[([2,3,[[0,1],[1,1]]],'Both rows are toggled once while column one is toggled twice, so all six cells are odd.'),([2,2,[[1,1],[0,0]]],'Each row and column is toggled once, so every cell receives an even total and the answer is zero.')],[[m,n,x] for m,n,x in [(1,1,[]),(1,1,[[0,0]]),(1,3,[[0,1]]),(2,2,[]),(2,2,[[0,0]]),(2,3,[[0,1],[1,1]]),(3,3,[[0,0],[0,0]]),(3,4,[[1,2]]),(4,2,[[0,0],[3,1]]),(2,5,[[1,4],[1,4],[0,0]]),(5,5,[[2,2]]),(3,2,[[0,1],[1,1],[2,1]]),(4,4,[[0,0],[1,1],[2,2]]),(2,2,[[0,1],[0,1],[1,0]])]],O,[O.replace('rows[r]^=1','rows[r]=1'),O.replace('rows[i]^cols[j]','rows[i] and cols[j]')],['Does not cancel repeated operations on the same row.','Counts only cells whose row and column are both odd rather than their parity XOR.'],odd_o,ro,['Only row and column increment parity matters.','Toggle a bit for each referenced row and column.','A cell is odd exactly when its row and column bits differ.','Its value is row increments plus column increments, whose parity is XOR.'],'O(m*n+q)','O(m+n)',3),
1260:spec(1260,'shift_grid',[('grid','list[list[int]]'),('k','int')],'list[list[int]]',['matrices','arrays'],['grid is nonempty and rectangular.','Shift every cell right k times with row wrapping.'],[([[[1,2,3],[4,5,6],[7,8,9]],1],'Nine wraps to the first cell and every other value moves right once.'),([[[1,2],[3,4]],4],'A shift by the cell count restores the grid.')],[[g,k] for g,k in [([[1]],0),([[1]],5),([[1,2]],1),([[1,2]],2),([[1],[2],[3]],1),([[1,2],[3,4]],1),([[1,2],[3,4]],2),([[1,2,3]],5),([[1,2,3],[4,5,6]],3),([[1,2,3],[4,5,6]],7),([[0,0],[0,1]],1),([[-1,2],[-3,4]],3),([[1,2],[3,4],[5,6]],5),([[9,8,7]],100)]],SHIFT,[SHIFT.replace('flat[-k:]+flat[:-k]','flat[k:]+flat[:k]'),SHIFT.replace('k%=len(flat)','k%=len(grid)')],['Shifts left rather than right.','Reduces k by row count instead of total cell count.'],shift_o,rshift,['Flatten row-major order so one right shift is a cyclic shift by one.','Reduce k modulo total cells and rotate the flat list.','Slice the rotated values back into rows of the original width.','Row-major flattening preserves exactly the required wrap order.'],'O(m*n)','O(m*n)',3),
1266:spec(1266,'minimum_point_visit_time',[('points','list[list[int]]')],'int',['geometry','greedy'],['Move horizontally, vertically, or diagonally by one per second.','Visit points in the given order.'],[([[[1,1],[3,4],[-1,0]]],'Chebyshev distances three and four sum to seven.'),([[[3,2],[-2,2]]],'Five horizontal moves are necessary and sufficient.')],[[p] for p in [[[0,0]],[[0,0],[1,1]],[[0,0],[3,1]],[[1,1],[1,5]],[[1,1],[-1,-1]],[[0,0],[2,3],[5,3]],[[5,5],[0,0],[5,0]],[[1,2],[3,4],[5,6]],[[0,0],[-3,4]],[[10,10],[9,8]],[[1,1],[3,4],[-1,0]],[[0,0],[0,0]],[[2,-2],[-2,2]],[[1,5],[4,1],[4,8]]]],P,[P.replace('max(abs(x-u),abs(y-v))','abs(x-u)+abs(y-v)'),P.replace('sum(','max(')],['Uses Manhattan distance and ignores diagonal movement.','Returns only the slowest leg rather than total travel time.'],time_o,rp,['For one leg, diagonal moves reduce both coordinate differences simultaneously.','Use min(dx,dy) diagonals then the remaining straight moves.','That total equals max(dx,dy); sum it over consecutive point pairs.','No move can reduce either coordinate gap by more than one, so the maximum gap is also a lower bound.'],'O(n)','O(1)',3),
1267:spec(1267,'communicating_server_count',[('grid','list[list[int]]')],'int',['matrices','counting'],['A server communicates when another server shares its row or column.','Count communicating servers, not communicating pairs.'],[([[[1,0],[0,1]]],'Neither diagonal server shares a row or column, so the count is zero.'),([[[1,0],[1,1]]],'All three servers share a row or column with another server.')],[[g] for g in [[[0]],[[1]],[[1,1]],[[1],[1]],[[1,0],[0,1]],[[1,0],[1,0]],[[0,1],[1,1]],[[1,1],[1,1]],[[1,0,0],[0,1,0],[0,0,1]],[[1,1,0],[0,0,1]],[[0,1,0],[1,1,1]],[[1,0,1],[0,1,0]],[[1,0],[0,0],[1,0]],[[0,0,0],[0,0,0]]]],SERVER,[SERVER.replace('rows[i]>1 or cols[j]>1','rows[i]>1 and cols[j]>1'),SERVER.replace('rows[i]>1','rows[i]>=1')],['Requires companions in both the row and column.','Counts isolated servers because their own row count is one.'],servers_o,rserver,['Count servers in each row and each column.','A server qualifies when its row count or column count exceeds one.','Scan the grid a second time and count qualifying occupied cells.','The row/column counts exactly encode existence of another aligned server.'],'O(m*n)','O(m+n)',5),
}
