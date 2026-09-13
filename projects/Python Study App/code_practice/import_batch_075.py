"""Reviewed matrix, number theory, binary search, greedy, and graph imports."""
from collections import Counter, deque
from functools import lru_cache
from math import isqrt

from .import_batch_055 import entry

def matrix_oracle(a):
 g=a[0];best=0
 for rows in range(1<<len(g)):
  for cols in range(1<<len(g[0])):
   best=max(best,sum(((g[r][c]^(rows>>r&1)^(cols>>c&1))<<(len(g[0])-1-c)) for r in range(len(g)) for c in range(len(g[0]))))
 return best
def prime_pal_oracle(a):
 def prime(n):return n>=2 and all(n%d for d in range(2,isqrt(n)+1))
 n=a[0]
 while not (str(n)==str(n)[::-1] and prime(n)):n+=1
 return n
def transpose_oracle(a):return [list(row) for row in zip(*a[0])]
def gap_oracle(a):
 positions=[i for i,c in enumerate(bin(a[0])[:1:-1]) if c=='1'];return max((b-a for a,b in zip(positions,positions[1:])),default=0)
def power_oracle(a):return tuple(sorted(str(a[0]))) in {tuple(sorted(str(1<<i))) for i in range(31)}
def fiblen_oracle(a):
 arr=a[0];values=set(arr);best=0
 for i in range(len(arr)):
  for j in range(i+1,len(arr)):
   x,y=arr[i],arr[j];length=2
   while x+y in values:x,y=y,x+y;length+=1
   if length>=3:best=max(best,length)
 return best
def robot_oracle(a):
 commands,obstacles=a;blocked={tuple(x) for x in obstacles};x=y=0;direction=0;dirs=((0,1),(1,0),(0,-1),(-1,0));best=0
 for command in commands:
  if command==-2:direction=(direction-1)%4
  elif command==-1:direction=(direction+1)%4
  else:
   for _ in range(command):
    nx,ny=x+dirs[direction][0],y+dirs[direction][1]
    if (nx,ny) in blocked:break
    x,y=nx,ny;best=max(best,x*x+y*y)
 return best
def koko_oracle(a):
 piles,h=a
 for speed in range(1,max(piles)+1):
  if sum((p+speed-1)//speed for p in piles)<=h:return speed
def stone_oracle(a):
 piles=a[0]
 @lru_cache(None)
 def score(l,r):return piles[l] if l==r else max(piles[l]-score(l+1,r),piles[r]-score(l,r-1))
 return score(0,len(piles)-1)>0
def decoded_oracle(a):
 s,k=a;text=''
 for char in s:
  if char.isdigit():text*=int(char)
  else:text+=char
  if len(text)>=k:return text[k-1]
def boats_oracle(a):
 people,limit=a
 @lru_cache(None)
 def solve(state):
  if not state:return 0
  values=list(state);first=values.pop();best=1+solve(tuple(values))
  for i,v in enumerate(values):
   if first+v<=limit:best=min(best,1+solve(tuple(values[:i]+values[i+1:])))
  return best
 return solve(tuple(sorted(people)))
def projection_oracle(a):
 g=a[0];return sum(v>0 for row in g for v in row)+sum(max(row) for row in g)+sum(max(g[r][c] for r in range(len(g))) for c in range(len(g[0])))
def uncommon_oracle(a):return [w for w,c in Counter((a[0]+' '+a[1]).split()).items() if c==1]
def spiral_oracle(a):
 rows,cols,r,c=a;answer=[];steps=1;direction=0;dirs=((0,1),(1,0),(0,-1),(-1,0))
 if 0<=r<rows and 0<=c<cols:answer.append([r,c])
 while len(answer)<rows*cols:
  for _ in range(2):
   dr,dc=dirs[direction%4]
   for _ in range(steps):
    r+=dr;c+=dc
    if 0<=r<rows and 0<=c<cols:answer.append([r,c])
   direction+=1
  steps+=1
 return answer
def bipartition_oracle(a):
 n,edges=a;g=[[] for _ in range(n)]
 for x,y in edges:g[x-1].append(y-1);g[y-1].append(x-1)
 color=[-1]*n
 for start in range(n):
  if color[start]>=0:continue
  color[start]=0;q=[start]
  while q:
   node=q.pop()
   for nxt in g[node]:
    if color[nxt]<0:color[nxt]=color[node]^1;q.append(nxt)
    elif color[nxt]==color[node]:return False
 return True
def candy_oracle(a):
 alice,bob=a;difference=(sum(alice)-sum(bob))//2
 return min(([x,x-difference] for x in alice if x-difference in set(bob)),default=[])
def pattern_oracle(a):
 def canon(s):
  ids={};return [ids.setdefault(c,len(ids)) for c in s]
 return [w for w in a[0] if canon(w)==canon(a[1])]
def surface_oracle(a):
 g=a[0];rows=len(g);cols=len(g[0]);area=0
 for r in range(rows):
  for c in range(cols):
   h=g[r][c]
   if h:area+=2
   for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
    nr,nc=r+dr,c+dc;area+=max(0,h-(g[nr][nc] if 0<=nr<rows and 0<=nc<cols else 0))
 return area
def special_oracle(a):
 def key(w):return (tuple(sorted(w[::2])),tuple(sorted(w[1::2])))
 return len({key(w) for w in a[0]})
def monotonic_oracle(a):
 x=a[0];return all(p<=q for p,q in zip(x,x[1:])) or all(p>=q for p,q in zip(x,x[1:]))

def random_matrix(r):
 rows,cols=r.randint(1,4),r.randint(1,5);return [[[r.randrange(2) for _ in range(cols)] for _ in range(rows)]]
def random_prime(r):return [r.randint(1,20000)]
def random_transpose(r):
 rows,cols=r.randint(1,6),r.randint(1,6);return [[[r.randint(-9,9) for _ in range(cols)] for _ in range(rows)]]
def random_gap(r):return [r.randint(1,10**6)]
def random_power(r):return [r.randint(1,10**9)]
def random_fiblen(r):return [sorted(r.sample(range(1,100),r.randint(3,10)))]
def random_robot(r):return [[r.choice([-2,-1]+list(range(1,10))) for _ in range(r.randint(1,15))],[[r.randint(-8,8),r.randint(-8,8)] for _ in range(r.randint(0,10))]]
def random_koko(r):
 piles=[r.randint(1,50) for _ in range(r.randint(1,9))];return [piles,r.randint(len(piles),len(piles)+30)]
def random_stone(r):
 size=2*r.randint(1,6);p=[r.randint(1,20) for _ in range(size)];p[0]+=sum(p)%2==0;return [p]
def random_decoded(r):
 s='a';length=1
 for _ in range(r.randint(1,8)):
  if r.random()<.45:s+=str(r.randint(2,4));length*=int(s[-1])
  else:s+=r.choice('abc');length+=1
 return [s,r.randint(1,min(length,500))]
def random_boats(r):
 limit=r.randint(2,12);return [[r.randint(1,limit) for _ in range(r.randint(1,9))],limit]
def random_projection(r):
 rows,cols=r.randint(1,5),r.randint(1,5);return [[[r.randint(0,8) for _ in range(cols)] for _ in range(rows)]]
def random_uncommon(r):return [' '.join(r.choice('abcde') for _ in range(r.randint(1,8))),' '.join(r.choice('abcde') for _ in range(r.randint(1,8)))]
def random_spiral(r):
 rows,cols=r.randint(1,8),r.randint(1,8);return [rows,cols,r.randrange(rows),r.randrange(cols)]
def random_bipartition(r):
 n=r.randint(1,9);return [n,[[i,j] for i in range(1,n+1) for j in range(i+1,n+1) if r.random()<.2]]
def random_candy(r):
 a=[r.randint(1,10) for _ in range(r.randint(1,7))];b=[r.randint(1,10) for _ in range(r.randint(1,7))];delta=sum(a)-sum(b)
 if delta%2 or not any(x-delta//2 in b for x in a):a=[1,1];b=[2,2]
 return [a,b]
def random_pattern(r):
 p=''.join(r.choice('abc') for _ in range(r.randint(1,6)));return [[''.join(r.choice('abc') for _ in p) for _ in range(r.randint(1,10))],p]
def random_surface(r):
 rows,cols=r.randint(1,5),r.randint(1,5);return [[[r.randint(0,6) for _ in range(cols)] for _ in range(rows)]]
def random_special(r):return [[''.join(r.choice('abcd') for _ in range(r.randint(1,8))) for _ in range(r.randint(1,10))]]
def random_monotonic(r):return [[r.randint(-10,10) for _ in range(r.randint(1,15))]]

MATRIX='''\
def maximum_binary_matrix_score(grid):
 rows,cols=len(grid),len(grid[0]);answer=rows*(1<<(cols-1))
 for c in range(1,cols):
  ones=sum(grid[r][c]==grid[r][0] for r in range(rows));answer+=max(ones,rows-ones)*(1<<(cols-1-c))
 return answer
'''
PRIME='''\
def next_prime_palindrome(n):
 def prime(x):
  if x<2:return False
  d=2
  while d*d<=x:
   if x%d==0:return False
   d+=1
  return True
 if 8<=n<=11:return 11
 length=len(str(n))
 while True:
  half=(length+1)//2
  for prefix in range(10**(half-1),10**half):
   text=str(prefix);candidate=int(text+text[-(2 if length%2 else 1)::-1])
   if candidate>=n and prime(candidate):return candidate
  length+=1
'''
TRANSPOSE='''\
def transpose_matrix(matrix):
 return [[matrix[r][c] for r in range(len(matrix))] for c in range(len(matrix[0]))]
'''
GAP='''\
def maximum_binary_gap(n):
 last=None;best=0;index=0
 while n:
  if n&1:
   if last is not None:best=max(best,index-last)
   last=index
  n>>=1;index+=1
 return best
'''
POWER='''\
def reordered_power_of_two(n):
 signature=sorted(str(n))
 return any(sorted(str(1<<power))==signature for power in range(31))
'''
FIBLEN='''\
def longest_fibonacci_subsequence(arr):
 index={value:i for i,value in enumerate(arr)};dp={};best=0
 for j in range(len(arr)):
  for k in range(j+1,len(arr)):
   i=index.get(arr[k]-arr[j],-1)
   if i<j:
    dp[j,k]=dp.get((i,j),2)+1;best=max(best,dp[j,k])
 return best
'''
ROBOT='''\
def maximum_robot_distance(commands, obstacles):
 blocked={tuple(x) for x in obstacles};x=y=direction=best=0;steps=((0,1),(1,0),(0,-1),(-1,0))
 for command in commands:
  if command==-2:direction=(direction-1)%4
  elif command==-1:direction=(direction+1)%4
  else:
   for _ in range(command):
    nx,ny=x+steps[direction][0],y+steps[direction][1]
    if (nx,ny) in blocked:break
    x,y=nx,ny;best=max(best,x*x+y*y)
 return best
'''
KOKO='''\
def minimum_eating_speed(piles, h):
 left,right=1,max(piles)
 while left<right:
  speed=(left+right)//2
  if sum((pile+speed-1)//speed for pile in piles)<=h:right=speed
  else:left=speed+1
 return left
'''
STONE='''\
def first_player_wins_stone_game(piles):
 dp=piles[:]
 for length in range(2,len(piles)+1):
  for left in range(len(piles)-length+1):
   right=left+length-1;dp[left]=max(piles[left]-dp[left+1],piles[right]-dp[left])
 return dp[0]>0
'''
DECODED='''\
def decoded_character_at(s, k):
 size=0
 for char in s:size=size*int(char) if char.isdigit() else size+1
 for char in reversed(s):
  k%=size
  if k==0 and char.isalpha():return char
  size=size//int(char) if char.isdigit() else size-1
'''
BOATS='''\
def minimum_rescue_boats(people, limit):
 people=sorted(people);left=0;right=len(people)-1;boats=0
 while left<=right:
  if people[left]+people[right]<=limit:left+=1
  right-=1;boats+=1
 return boats
'''
PROJECTION='''\
def projection_area(grid):
 return sum(value>0 for row in grid for value in row)+sum(max(row) for row in grid)+sum(max(row[c] for row in grid) for c in range(len(grid[0])))
'''
UNCOMMON='''\
def uncommon_sentence_words(s1, s2):
 from collections import Counter
 counts=Counter((s1+' '+s2).split());return [word for word,count in counts.items() if count==1]
'''
SPIRAL='''\
def spiral_matrix_coordinates(rows, cols, r_start, c_start):
 answer=[];r,c=r_start,c_start;step=1;direction=0;dirs=((0,1),(1,0),(0,-1),(-1,0))
 if 0<=r<rows and 0<=c<cols:answer.append([r,c])
 while len(answer)<rows*cols:
  for _ in range(2):
   dr,dc=dirs[direction%4]
   for _ in range(step):
    r+=dr;c+=dc
    if 0<=r<rows and 0<=c<cols:answer.append([r,c])
   direction+=1
  step+=1
 return answer
'''
BIPART='''\
def can_bipartition(n, dislikes):
 graph=[[] for _ in range(n)]
 for a,b in dislikes:graph[a-1].append(b-1);graph[b-1].append(a-1)
 color=[-1]*n
 for start in range(n):
  if color[start]>=0:continue
  color[start]=0;queue=[start]
  while queue:
   node=queue.pop()
   for other in graph[node]:
    if color[other]<0:color[other]=color[node]^1;queue.append(other)
    elif color[other]==color[node]:return False
 return True
'''
CANDY='''\
def fair_candy_swap(alice_sizes, bob_sizes):
 difference=(sum(alice_sizes)-sum(bob_sizes))//2;bob=set(bob_sizes)
 return min(([value,value-difference] for value in alice_sizes if value-difference in bob),default=[])
'''
PATTERN='''\
def pattern_matching_words(words, pattern):
 def form(text):
  mapping={};return [mapping.setdefault(char,len(mapping)) for char in text]
 target=form(pattern);return [word for word in words if form(word)==target]
'''
SURFACE='''\
def stacked_cube_surface_area(grid):
 rows,cols=len(grid),len(grid[0]);area=0
 for r in range(rows):
  for c in range(cols):
   height=grid[r][c]
   if height:area+=2+4*height
   if r:area-=2*min(height,grid[r-1][c])
   if c:area-=2*min(height,grid[r][c-1])
 return area
'''
SPECIAL='''\
def special_equivalent_group_count(words):
 return len({(''.join(sorted(word[::2])),''.join(sorted(word[1::2]))) for word in words})
'''
MONOTONIC='''\
def is_monotonic_array(nums):
 increasing=decreasing=True
 for a,b in zip(nums,nums[1:]):
  increasing&=a<=b;decreasing&=a>=b
 return increasing or decreasing
'''

def lesson(a,b,c,d):return [a,b,c,d],d
BATCH={
861:entry('maximum_binary_matrix_score',[('grid','list[list[int]]')],'int',['matrices','greedy'],['Flip any rows or columns of a binary matrix.','Interpret each row as binary and maximize their sum.'],[([[[0,0,1,1],[1,0,1,0],[1,1,0,0]]],'Making every leading bit one and choosing each later majority gives total 39.'),([[[0]]],'Flipping the only bit gives score one.')],[[g] for g in ([[1]],[[0,1]],[[1,0]],[[0],[1]],[[0,0],[0,0]],[[1,1],[1,1]],[[0,1],[1,0]],[[0,0,1],[1,1,0]],[[1,0,1],[0,1,0]],[[0,1,1],[0,1,1]],[[1,0,0,1],[0,1,1,0]],[[0,0,0],[1,0,1],[0,1,0]])],MATRIX,[MATRIX.replace('max(ones,rows-ones)','ones'),MATRIX.replace('grid[r][c]==grid[r][0]','grid[r][c]!=grid[r][0]')],['Never flips a column whose zeros are the majority.','Counts bits that disagree with the normalized leading bit.'],matrix_oracle,random_matrix,*lesson('The most significant bit dominates every lower bit, so every row should first be made to lead with one.','Treat row flips implicitly, then choose the majority normalized bit per later column.','Score leading column as all ones; for c count grid[r][c]==grid[r][0] and take max(count,rows-count).','Column choices are independent after optimal row normalization, and binary weights convert counts directly to score.'),'O(rows*columns)','O(1)',5),
866:entry('next_prime_palindrome',[('n','int')],'int',['math','strings'],['1 <= n <= 100,000,000.','Return the smallest prime palindrome at least n.'],[([6],'Seven is the first prime palindrome no smaller than six.'),([13],'The next prime palindrome is 101.')],[[n] for n in (1,2,7,8,10,11,12,100,101,102,998,1000,10000)],PRIME,[PRIME.replace('candidate>=n','candidate>n'),PRIME.replace('if 8<=n<=11:return 11','if 8<=n<=11:return 101')],['Skips n itself when it already qualifies.','Skips the special even-length prime palindrome eleven.'],prime_pal_oracle,random_prime,*lesson('Except eleven, every even-length palindrome is divisible by eleven, so generate odd-length palindromes.','Mirror numeric prefixes and primality-test candidates in increasing length/order.','Handle 8..11, mirror prefix without its last digit, and return first candidate>=n that is prime.','Prefix order equals palindrome order, while the divisibility fact safely removes all other even lengths.'),'O(sqrt(answer)*palindrome candidates)','O(1)',5),
867:entry('transpose_matrix',[('matrix','list[list[int]]')],'list[list[int]]',['matrices'],['Matrix is nonempty and rectangular.','Return its transpose, swapping rows with columns.'],[([[[1,2,3],[4,5,6],[7,8,9]]],'Rows become the three output columns.'),([[[1,2,3],[4,5,6]]],'A 2-by-3 matrix becomes 3-by-2.')],[[m] for m in ([[1]],[[1,2]],[[1],[2]],[[1,2],[3,4]],[[1,2,3]],[[1],[2],[3]],[[0,-1],[2,3]],[[1,2],[3,4],[5,6]],[[1,2,3],[4,5,6],[7,8,9],[10,11,12]],[[0,0],[0,0]],[[1,-2,3],[4,-5,6]],[[9,8,7,6],[5,4,3,2]])],TRANSPOSE,[TRANSPOSE.replace('matrix[r][c]','matrix[c][r]'),TRANSPOSE.replace('range(len(matrix[0]))','range(len(matrix))')],['Indexes the source coordinates backward.','Keeps the original row count for rectangular output.'],transpose_oracle,random_transpose,*lesson('Transposition maps output[c][r] to input[r][c].','Build one output row for each input column.','For c over columns, collect matrix[r][c] over rows.','Every input cell appears once at its coordinate-swapped position.'),'O(rows*columns)','O(rows*columns)',3),
868:entry('maximum_binary_gap',[('n','int')],'int',['bit-manipulation'],['1 <= n <= 10^9.','Return the largest distance between consecutive one bits, or zero if fewer than two.'],[([22],'Binary 10110 has consecutive-one distances two and one, so the maximum is two.'),([8],'Binary 1000 has one set bit, so the answer is zero.')],[[n] for n in (1,2,3,4,5,6,9,10,17,21,42,85,1024,1025)],GAP,[GAP.replace('index-last','index-last-1'),GAP.replace('last=index','last=0')],['Counts zeros between ones rather than positional distance.','Resets the previous position to zero after every one bit.'],gap_oracle,random_gap,*lesson('Only positions of consecutive set bits matter.','Scan bits while storing the previous one-bit index.','On each one update max(index-last), then set last=index.','Each adjacent pair of set-bit positions is considered exactly once.'),'O(log n)','O(1)',3),
869:entry('reordered_power_of_two',[('n','int')],'bool',['counting','math'],['1 <= n <= 10^9; reordered decimal digits cannot start with zero.','Return whether some permutation forms a power of two.'],[([1],'One is 2^0.'),([10],'Neither 10 nor 01 is a power of two.')],[[n] for n in (2,3,4,16,24,46,61,128,218,256,625,1024,1204,1000000000)],POWER,[POWER.replace('range(31)','range(30)'),POWER.replace('sorted(str(n))','set(str(n))')],['Omits the largest relevant exponent.','Compares digit sets and ignores multiplicity.'],power_oracle,random_power,*lesson('Digit permutations share exactly the same sorted digit signature.','Compare n’s signature with every power of two in range.','Return any(sorted(str(2^p))==sorted(str(n))) for p=0..30.','Equal multisets are precisely the condition for a no-leading-zero permutation; powers never begin with zero.'),'O(log n^2)','O(log n)',5),
873:entry('longest_fibonacci_subsequence',[('arr','list[int]')],'int',['dynamic-programming','hash-maps'],['arr is strictly increasing with at most 1,000 elements.','Return longest Fibonacci-like subsequence length, or zero if none has length three.'],[([[1,2,3,4,5,6,7,8]],'One longest subsequence is 1,2,3,5,8 of length five.'),([[1,3,7,11,12,14,18]],'Sequences 1,11,12 and 3,11,14 have length three.')],[[x] for x in ([1,2,3],[1,2,4],[1,3,4,7],[2,4,6,10,16],[1,2,3,5,8,13],[1,4,5,9,14],[3,6,9,15,24],[1,5,6,11,17,28],[2,3,5,8,12],[1,10,11,21,32],[1,2,4,7,11,18],[5,10,15,25,40])],FIBLEN,[FIBLEN.replace('dp.get((i,j),2)+1','3'),FIBLEN.replace('if i<j','if i<=j')],['Never extends an existing Fibonacci pair beyond length three.','Allows an invalid predecessor at the same index.'],fiblen_oracle,random_fiblen,*lesson('A Fibonacci-like subsequence is determined by its last two values.','Use pair DP and a value-to-index lookup for the required predecessor.','For pair j,k find i with arr[i]=arr[k]-arr[j]; dp[j,k]=dp[i,j]+1.','Strict increase makes the predecessor unique and i<j enforces subsequence order.'),'O(n^2)','O(n^2)',5),
874:entry('maximum_robot_distance',[('commands','list[int]'),('obstacles','list[list[int]]')],'int',['simulation','hash-maps'],['Robot begins at origin facing north; -2 turns left, -1 right, and positive commands move forward.','Stop before obstacles and return maximum squared distance reached.'],[([[4,-1,3],[]],'The robot reaches (3,4), whose squared distance is 25.'),([[4,-1,4,-2,4],[[2,4]]],'The obstacle stops the eastward segment and the maximum squared distance is 65.')],[[c,o] for c,o in (([1],[]),([-1,1],[]),([-2,1],[]),([5],[[0,3]]),([2,-1,2],[]),([2,-1,2],[[1,2]]),([1,-1,1,-1,1,-1,1],[]),([9,9],[]),([-1,-1,3],[]),([4,-2,4],[[0,2]]),([3,-1,3,-1,3],[[1,3]]),([2,2,-1,2],[[0,1]]))],ROBOT,[ROBOT.replace("if (nx,ny) in blocked:break",''),ROBOT.replace('direction=(direction-1)%4','direction=(direction+1)%4')],['Walks through obstacles.','Turns left in the same direction as a right turn.'],robot_oracle,random_robot,*lesson('Movement must be simulated one unit at a time because an obstacle can stop a longer command early.','Track orientation and a hash set of blocked coordinates.','Rotate direction on negatives; for each forward unit test next coordinate before moving and update squared distance.','Every reachable intermediate position is considered, including the maximum before a later return toward the origin.'),'O(total commanded steps)','O(obstacles)',5),
875:entry('minimum_eating_speed',[('piles','list[int]'),('h','int')],'int',['binary-search','greedy'],['h is at least the number of piles.','At integer speed k, one pile consumes ceil(pile/k) hours; return minimum feasible k.'],[([[3,6,7,11],8],'Speed four needs 1+2+2+3=8 hours and speed three is too slow.'),([[30,11,23,4,20],5],'With one hour per pile, speed must equal the largest pile, 30.')],[[p,h] for p,h in (([1],1),([10],10),([10],1),([1,1],2),([2,2],3),([3,6,7,11],10),([5,5,5],6),([1,100],3),([9,10,11],9),([30,11,23,4,20],6),([100,100],100),([2,3,5,7,11],8))],KOKO,[KOKO.replace('(pile+speed-1)//speed','pile//speed'),KOKO.replace('right=speed','right=speed-1')],['Uses floor hours and underestimates partial-pile time.','Uses an incompatible boundary update and can skip the minimum feasible speed.'],koko_oracle,random_koko,*lesson('Required hours decrease monotonically as speed increases.','Binary-search the first speed whose ceiling-hour sum is at most h.','If feasible move right=mid; otherwise left=mid+1.','Monotonic feasibility preserves the first valid speed inside the search interval.'),'O(piles log maxPile)','O(1)',5),
877:entry('first_player_wins_stone_game',[('piles','list[int]')],'bool',['dynamic-programming','game-theory'],['piles has even length and odd total; players optimally take one end each turn.','Return whether the first player wins.'],[([[5,3,4,5]],'Optimal play lets the first player secure more stones.'),([[3,7,2,3]],'The first player can choose a parity strategy and win.')],[[x] for x in ([1,2],[2,1],[1,2,3,5],[3,9,1,2],[8,1,2,4],[1,100,3,4],[5,4,3,1],[2,7,9,4],[10,1,1,1],[1,1,1,2],[20,3,4,5,6,7],[2,3,10,1,4,7])],STONE,[STONE.replace('max(piles[left]-dp[left+1],piles[right]-dp[left])','min(piles[left]-dp[left+1],piles[right]-dp[left])'),STONE.replace('return dp[0]>0','return False')],['Lets the opponent choose the minimizing outcome for the current player.','Assumes the first player always loses.'],stone_oracle,random_stone,*lesson('For an interval, track current player’s maximum score advantage over the opponent.','Choose left or right and subtract the opponent’s optimal remaining advantage.','dp[l,r]=max(piles[l]-dp[l+1,r],piles[r]-dp[l,r-1]).','Zero-sum optimal play makes positive final advantage exactly equivalent to a first-player win.'),'O(n^2)','O(n)',5),
880:entry('decoded_character_at',[('s','str'),('k','int')],'str',['strings','math'],['Letters append normally; digit d repeats the entire current tape d times.','Return the one-indexed kth decoded character without constructing the huge tape.'],[(['leet2code3',10],'The decoded prefix is leetleetcode, whose tenth character is o.'),(['ha22',5],'The repeated tape hahahaha has h at position five.')],[[s,k] for s,k in (('a',1),('a2',2),('ab2',3),('ab2',4),('abc3',7),('x2y3',5),('ha22',8),('a2345678999999999999999',1),('leet2code3',20),('abc2d2',10),('z9',9),('ab3c2',13))],DECODED,[DECODED.replace('k%=size','k=size%k'),DECODED.replace('k==0','k==1')],['Applies modulo in the wrong direction.','Uses one instead of zero after modulo normalization.'],decoded_oracle,random_decoded,*lesson('Reverse traversal can undo repetition lengths without materializing repeated text.','Compute total decoded length, then walk backward reducing k modulo the current length.','At digit divide size; at letter return when k%size==0, else decrement size.','Repeated copies map a position to the same position in one copy, which modulo performs exactly.'),'O(len(s))','O(1)',5),
881:entry('minimum_rescue_boats',[('people','list[int]'),('limit','int')],'int',['greedy','two-pointers'],['Each boat carries at most two people with combined weight at most limit.','Return the minimum boats.'],[([[1,2],3],'Both people share one boat.'),([[3,2,2,1],3],'The optimal pairing uses three boats.')],[[p,l] for p,l in (([1],1),([1,1],2),([1,2],2),([1,2,2],3),([3,5,3,4],5),([2,2,2,2],4),([1,2,3,4],5),([5,1,1,1],5),([3,3,1,1],4),([2,4,2,1],5),([10,10],10),([1,1,1,1,9,9],10))],BOATS,[BOATS.replace('people[left]+people[right]<=limit','people[left]+people[right]<limit'),BOATS.replace('right-=1','right-=2')],['Rejects pairs that exactly fill the boat.','Removes two people even when the heaviest rides alone.'],boats_oracle,random_boats,*lesson('The heaviest remaining person must take a boat; pairing them with the lightest is optimal whenever feasible.','Sort and use two pointers.','Always remove right; also remove left if their sum fits; increment boats.','If the lightest cannot pair with the heaviest nobody can; if they can, using the lightest preserves heavier partners for later.'),'O(n log n)','O(n)',5),
883:entry('projection_area',[('grid','list[list[int]]')],'int',['matrices','geometry'],['Each cell height is a vertical stack of unit cubes.','Sum top, front, and side projection areas.'],[([[[1,2],[3,4]]],'Top contributes four, row maxima six, and column maxima seven, totaling 17.'),([[[2]]],'One stack of height two projects areas one, two, and two for total five.')],[[g] for g in ([[0]],[[1]],[[1,0]],[[1],[2]],[[0,0],[0,0]],[[1,1],[1,1]],[[1,2,3]],[[1],[2],[3]],[[0,2],[3,0]],[[5,1],[2,4]],[[1,0,2],[0,3,0]],[[2,2,2],[2,2,2]])],PROJECTION,[PROJECTION.replace('value>0','value'),PROJECTION.replace('max(row[c] for row in grid)','sum(row[c] for row in grid)')],['Adds stack heights to the top projection instead of occupied cells.','Sums column heights instead of taking the silhouette maximum.'],projection_oracle,random_projection,*lesson('Top projection counts occupied cells; the two side projections take maxima along rows and columns.','Compute those three independent silhouettes.','Sum(value>0)+sum(row maxima)+sum(column maxima).','Each viewing direction hides all cubes except the footprint or tallest stack on each sight line.'),'O(rows*columns)','O(1)',3),
884:entry('uncommon_sentence_words',[('s1','str'),('s2','str')],'list[str]',['hash-maps','strings'],['Words are space-separated lowercase tokens.','Return words appearing exactly once across both sentences; order is irrelevant.'],[(['this apple is sweet','this apple is sour'],'Sweet and sour each appear once overall.'),(['apple apple','banana'],'Only banana is uncommon.')],[[a,b] for a,b in (('a','b'),('a','a'),('a b','c d'),('one two one','three'),('x y','y z'),('same same','same'),('red blue','green red'),('a b c','a b c'),('hello','world world'),('foo bar foo','baz qux'),('cat dog','bird fish'),('single','other single'))],UNCOMMON,[UNCOMMON.replace('count==1','count<=2'),UNCOMMON.replace("(s1+' '+s2).split()","s1.split()")],['Includes words appearing twice.','Counts only the first sentence.'],uncommon_oracle,random_uncommon,*lesson('Uncommon means global frequency exactly one, not one occurrence per sentence.','Count the concatenated token streams once.','Return keys whose Counter value equals one.','Global counting naturally excludes repeated words within or across sentences.'),'O(total words)','O(distinct words)',3),
885:entry('spiral_matrix_coordinates',[('rows','int'),('cols','int'),('r_start','int'),('c_start','int')],'list[list[int]]',['matrices','simulation'],['Start inside the grid facing east and walk an expanding clockwise spiral, continuing outside boundaries.','Return in-grid coordinates in visit order until all cells are listed.'],[([1,4,0,0],'The first eastward steps visit the only row from column zero through three.'),([5,6,1,4],'The expanding spiral eventually records all thirty grid cells in order.')],[[r,c,x,y] for r,c,x,y in ((1,1,0,0),(2,2,0,0),(2,3,1,1),(3,2,1,0),(3,3,1,1),(1,5,0,2),(5,1,2,0),(4,4,0,3),(4,5,3,0),(2,5,0,4),(5,2,4,1),(6,6,3,2))],SPIRAL,[SPIRAL.replace('for _ in range(2)','for _ in range(1)'),SPIRAL.replace('direction%4','(direction+1)%4')],['Increases step length after every direction instead of every two directions.','Starts by moving south rather than east.'],spiral_oracle,random_spiral,*lesson('A square spiral travels lengths 1,1,2,2,3,3 in east,south,west,north order.','Simulate that infinite path and record only coordinates inside the grid.','For each step length walk two directions, then increment length, stopping after rows*cols records.','The spiral eventually encloses every finite grid cell even while intermediate positions lie outside.'),'O(max(rows,cols)^2)','O(rows*cols)',5),
886:entry('can_bipartition',[('n','int'),('dislikes','list[list[int]]')],'bool',['graphs','breadth-first-search'],['People are labeled 1..n and dislike edges are undirected.','Return whether people can be split so every dislike edge crosses groups.'],[([4,[[1,2],[1,3],[2,4]]],'A valid split is {1,4} and {2,3}.'),([3,[[1,2],[1,3],[2,3]]],'The triangle cannot be colored with two groups.')],[[n,e] for n,e in ((1,[]),(2,[]),(2,[[1,2]]),(3,[[1,2],[2,3]]),(4,[[1,2],[3,4]]),(4,[[1,2],[2,3],[3,4],[4,1]]),(5,[[1,2],[2,3],[3,1]]),(5,[[1,2],[1,3],[4,5]]),(6,[[1,4],[2,5],[3,6]]),(4,[[1,2],[1,3],[1,4]]),(6,[[1,2],[2,3],[4,5],[5,6]]),(7,[[1,2],[2,3],[3,4],[4,5],[5,1]]))],BIPART,[BIPART.replace('color[other]=color[node]^1','color[other]=color[node]'),BIPART.replace('for start in range(n)','for start in range(1)')],['Assigns neighbors the same color.','Checks only the component containing person one.'],bipartition_oracle,random_bipartition,*lesson('The requested split is exactly a two-coloring of the dislike graph.','Color every connected component by BFS or DFS.','Assign each unseen neighbor the opposite color; reject an equal-colored edge.','A proper two-coloring gives the two groups, and any odd-cycle conflict proves no split exists.'),'O(n+edges)','O(n+edges)',5),
888:entry('fair_candy_swap',[('alice_sizes','list[int]'),('bob_sizes','list[int]')],'list[int]',['hash-maps','math'],['A solution exists; for deterministic feedback return the lexicographically smallest valid [Alice gives, Bob gives] pair.','After swapping one box each, total candy amounts must be equal.'],[([[1,1],[2,2]],'Alice gives one and Bob gives two, leaving both totals three.'),([[1,2],[2,3]],'Swapping one for two balances the totals.')],[[a,b] for a,b in (([1],[1]),([1],[2]),([2],[1]),([1,2,5],[2,4]),([1,1,1],[1,1,1]),([2,3],[1,4]),([5,7],[3,9]),([1,4,6],[2,3,8]),([10,10],[5,15]),([1,2,3],[2,2,4]),([8,1],[4,5]),([3,3,6],[2,5,5]))],CANDY,[CANDY.replace('//2','//1'),CANDY.replace('value-difference','value+difference')],['Uses the full total difference rather than half.','Moves totals farther apart by using the wrong sign.'],candy_oracle,random_candy,*lesson('If Alice gives x and Bob gives y, equality requires x-y=(sumA-sumB)/2.','Hash Bob’s sizes and test Alice’s sizes in sorted pair order.','For x, seek y=x-difference; return the lexicographically smallest match.','The algebraic condition is necessary and sufficient, and set lookup avoids testing all box pairs.'),'O(a+b)','O(b)',3),
890:entry('pattern_matching_words',[('words','list[str]'),('pattern','str')],'list[str]',['hash-maps','strings'],['A word matches when a bijection replaces pattern letters to form it.','Return matching words in input order.'],[([['abc','deq','mee','aqq','dkd','ccc'],'abb'],'Mee and aqq share the pattern of one letter followed by a repeated second letter.'),([['a','b','c'],'a'],'Every one-letter word matches.')],[[w,p] for w,p in ((['abc'],'abc'),(['foo','bar'],'abb'),(['aa','ab'],'aa'),(['xyz','xyy','yxx'],'abb'),(['ab','cd'],'ab'),(['aaa','bbb','aba'],'aaa'),(['paper','title'],'abcde'),(['mee','aqq'],'abb'),(['dkd'],'aba'),(['abc','def','ghi'],'xyz'),(['xxy','xyy'],'aab'),(['noon','deed','moon'],'abba'))],PATTERN,[PATTERN.replace('mapping.setdefault(char,len(mapping))','ord(char)'),PATTERN.replace('form(word)==target','set(word)==set(pattern)')],['Compares literal character codes instead of structural first-occurrence IDs.','Compares character sets and ignores position/repetition structure.'],pattern_oracle,random_pattern,*lesson('Bijective renaming preserves the sequence of first-occurrence IDs.','Canonicalize both word and pattern by assigning each new character its next ID.','Keep words whose canonical ID list equals the pattern’s list.','Equal canonical forms establish a one-to-one correspondence in both directions.'),'O(total word characters)','O(alphabet)',5),
892:entry('stacked_cube_surface_area',[('grid','list[list[int]]')],'int',['matrices','geometry'],['Each grid value is the height of a unit-cube stack.','Return total exposed top, bottom, and side area.'],[([[[1,2],[3,4]]],'Adding exposed faces and subtracting shared faces gives total 34.'),([[[2]]],'A two-cube vertical stack exposes ten faces.')],[[g] for g in ([[0]],[[1]],[[3]],[[1,1]],[[1],[1]],[[1,1],[1,1]],[[1,2]],[[1],[2]],[[0,2],[3,0]],[[2,2],[2,2]],[[1,3,1],[2,0,2]],[[5,1],[1,5]])],SURFACE,[SURFACE.replace('area-=2*min','area-=min'),SURFACE.replace('if height:area+=2+4*height','area+=2+4*height')],['Subtracts only one face for each shared cube contact.','Adds top and bottom faces for empty cells.'],surface_oracle,random_surface,*lesson('Each nonempty stack contributes top/bottom plus four vertical sides, reduced by shared faces with neighbors.','Add isolated-stack area and subtract twice each shared boundary with top/left neighbors.','For height h add 2+4h; subtract 2*min(h,neighbor) for each processed adjacency.','Every cube face is initially counted, and each internal touching pair removes its two hidden faces exactly once.'),'O(rows*columns)','O(1)',3),
893:entry('special_equivalent_group_count',[('words','list[str]')],'int',['hash-maps','strings'],['Swaps may occur between indices with the same parity.','Count equivalence groups under arbitrary even-even and odd-odd swaps.'],[([['abcd','cdab','cbad','xyzz','zzxy','zzyx']],'The words form three parity-multiset groups.'),([['abc','acb','bac','bca','cab','cba']],'The six permutations form three special-equivalence groups.')],[[w] for w in ((['a']),(['a','a']),(['ab','ba']),(['abc','cba']),(['abcd','cdab']),(['abcd','badc']),(['aaab','abaa']),(['xyz','zyx']),(['abc','abc','cba']),(['even','neve','veen']),(['aa','bb','ab']),(['abcd','adcb','cbad']))],SPECIAL,[SPECIAL.replace("word[::2]","word"),SPECIAL.replace("word[1::2]","''")],['Sorts all letters together and permits cross-parity swaps.','Ignores the odd-index multiset.'],special_oracle,random_special,*lesson('Same-parity swaps can arbitrarily permute even positions and odd positions independently.','Use sorted even-index and sorted odd-index characters as a canonical key.','key=(sorted(word[::2]),sorted(word[1::2])); count distinct keys.','The key is invariant under allowed swaps and equal keys can be transformed by parity-wise permutations.'),'O(total letters log length)','O(total letters)',5),
896:entry('is_monotonic_array',[('nums','list[int]')],'bool',['arrays'],['An array is monotonic when entirely nondecreasing or entirely nonincreasing.','Equal adjacent values are allowed.'],[([[1,2,2,3]],'Every adjacent step is nondecreasing.'),([[1,3,2]],'The direction changes from increasing to decreasing.')],[[x] for x in ([1],[1,1],[1,2],[2,1],[1,2,3],[3,2,1],[1,1,2,1],[3,3,2,2],[1,3,2,4],[0,-1,-1,-2],[1,2,2,1],[5,4,4,4,1])],MONOTONIC,[MONOTONIC.replace('a<=b','a<b'),MONOTONIC.replace('or decreasing','and decreasing')],['Requires strict monotonicity and rejects equal neighbors.','Requires the array to be both increasing and decreasing.'],monotonic_oracle,random_monotonic,*lesson('Only a sign reversal among adjacent differences breaks monotonicity.','Track whether all steps remain nondecreasing and whether all remain nonincreasing.','For each pair update increasing with a<=b and decreasing with a>=b; return either flag.','One flag survives exactly when every adjacent constraint for that direction holds.'),'O(n)','O(1)',3),
}
BATCH[884]['comparator']='unordered'

BATCH[861]['wrong'][1]='''\
def maximum_binary_matrix_score(grid):
    rows,cols=len(grid),len(grid[0]);answer=rows*(1<<(cols-1))
    for column in range(1,cols):
        ones=sum(grid[row][column] for row in range(rows))
        answer+=max(ones,rows-ones)*(1<<(cols-1-column))
    return answer
'''
BATCH[867]['wrong'][0]='''\
def transpose_matrix(matrix):
    return [row[:] for row in matrix]
'''
BATCH[867]['wrong'][1]='''\
def transpose_matrix(matrix):
    return [list(reversed(row)) for row in matrix]
'''
BATCH[869]['wrong'][0]='''\
def reordered_power_of_two(n):
    return n>0 and n&(n-1)==0
'''
BATCH[873]['reference']=FIBLEN.replace('if i<j','if 0<=i<j')
BATCH[885]['wrong'][0]='''\
def spiral_matrix_coordinates(rows, cols, r_start, c_start):
    return [[r_start,c_start]]
'''
BATCH[886]['boundaries'].append([4,[[2,3],[3,4],[4,2]]])
BATCH[893]['wrong'][0]='''\
def special_equivalent_group_count(words):
    return len({''.join(sorted(word)) for word in words})
'''
