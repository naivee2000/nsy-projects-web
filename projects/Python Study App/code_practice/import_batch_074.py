"""Reviewed string simulation, grid, greedy, graph, and probability imports."""
from collections import Counter, deque
from functools import lru_cache
from math import gcd

from . import import_batch_055 as batch_base
from .import_batch_055 import entry

batch_base.EXTRA_BOUNDARIES.update({
    'mountain_peak_index': [[[2,5,9,4,1]]],
    'parentheses_score': [['(()()())']],
})

def replace_oracle(a):
 s,idx,src,dst=a;edits={i:(x,y) for i,x,y in zip(idx,src,dst)};out='';i=0
 while i<len(s):
  if i in edits and s.startswith(edits[i][0],i):out+=edits[i][1];i+=len(edits[i][0])
  else:out+=s[i];i+=1
 return out
def overlap_oracle(a):
 x,y=a; n=len(x);return max(sum(x[r][c] and 0<=r+dr<n and 0<=c+dc<n and y[r+dr][c+dc] for r in range(n) for c in range(n)) for dr in range(-n+1,n) for dc in range(-n+1,n))
def rectangle_oracle(a):
 x,y=a;return max(x[0],y[0])<min(x[2],y[2]) and max(x[1],y[1])<min(x[3],y[3])
def game_oracle(a):
 n,k,m=a
 @lru_cache(None)
 def win(total):return float(total<=n) if total>=k else sum(win(total+d) for d in range(1,m+1))/m
 return win(0)
def domino_oracle(a):
 s=a[0];n=len(s);answer=[]
 for i,char in enumerate(s):
  if char!='.':answer.append(char);continue
  left=next((i-j for j in range(i-1,-1,-1) if s[j]!='.'),10**9);right=next((j-i for j in range(i+1,n) if s[j]!='.'),10**9)
  lchar=s[i-left] if left<10**9 else None;rchar=s[i+right] if right<10**9 else None
  answer.append('R' if lchar=='R' and (rchar!='L' or left<right) else 'L' if rchar=='L' and (lchar!='R' or right<left) else '.')
 return ''.join(answer)
def magic_oracle(a):
 g=a[0];return sum(sorted(g[r+i][c+j] for i in range(3) for j in range(3))==list(range(1,10)) and len({sum(g[r+i][c+j] for j in range(3)) for i in range(3)}|{sum(g[r+i][c+j] for i in range(3)) for j in range(3)}|{sum(g[r+i][c+i] for i in range(3)),sum(g[r+i][c+2-i] for i in range(3))})==1 for r in range(len(g)-2) for c in range(len(g[0])-2))
def rooms_oracle(a):
 rooms=a[0];seen={0};changed=True
 while changed:
  old=len(seen);seen|={key for room in list(seen) for key in rooms[room]};changed=len(seen)>old
 return len(seen)==len(rooms)
def fib_oracle(a):
 text=a[0]
 for i in range(1,min(11,len(text))):
  if text[0]=='0' and i>1:break
  for j in range(i+1,min(i+11,len(text))):
   if text[i]=='0' and j>i+1:break
   values=[int(text[:i]),int(text[i:j])];pos=j
   while pos<len(text):
    value=values[-1]+values[-2]
    if value>2**31-1 or not text.startswith(str(value),pos):break
    values.append(value);pos+=len(str(value))
   if pos==len(text) and len(values)>=3:return values
 return []
def backspace_oracle(a):
 def clean(s):
  out=[]
  for c in s:out.pop() if c=='#' and out else out.append(c) if c!='#' else None
  return ''.join(out)
 return clean(a[0])==clean(a[1])
def mountain_oracle(a):
 x=a[0];best=0
 for i in range(len(x)):
  for j in range(i+3,len(x)+1):
   best=max(best,j-i) if any(all(x[k]<x[k+1] for k in range(i,p)) and all(x[k]>x[k+1] for k in range(p,j-1)) for p in range(i+1,j-1)) else best
 return best
def straights_oracle(a):
 hand,size=a
 if len(hand)%size:return False
 counts=Counter(hand)
 def solve():
  if not counts:return True
  start=min(counts)
  for v in range(start,start+size):
   if not counts.get(v):return False
   counts[v]-=1
   if counts[v]==0:del counts[v]
  return solve()
 return solve()
def shifts_oracle(a):
 s,shifts=a;return ''.join(chr((ord(c)-97+sum(shifts[i:]))%26+97) for i,c in enumerate(s))
def seats_oracle(a):
 seats=a[0];occupied=[i for i,x in enumerate(seats) if x];return max(min(abs(i-j) for j in occupied) for i,x in enumerate(seats) if not x)
def rich_oracle(a):
 richer,quiet=a;answer=[]
 for person in range(len(quiet)):
  available={person};changed=True
  while changed:
   old=len(available);available|={x for x,y in richer if y in available};changed=len(available)>old
  answer.append(min(available,key=quiet.__getitem__))
 return answer
def peak_oracle(a):return max(range(len(a[0])),key=a[0].__getitem__)
def fleet_oracle(a):
 target,pos,speed=a;times=sorted(((p,(target-p)/v) for p,v in zip(pos,speed)),reverse=True);fleets=[]
 for _,time in times:
  if not fleets or time>fleets[-1]:fleets.append(time)
 return len(fleets)
def score_oracle(a):
 s=a[0];stack=[0]
 for c in s:
  if c=='(':stack.append(0)
  else:v=stack.pop();stack[-1]+=max(1,2*v)
 return stack[0]
def mirror_oracle(a):
 p,q=a
 if q==0:return 0
 l=p*q//gcd(p,q);horizontal=l//p;vertical=l//q
 return 2 if vertical%2==0 else 1 if horizontal%2 else 0
def buddy_oracle(a):
 s,g=a
 if len(s)!=len(g):return False
 return len(set(s))<len(s) if s==g else any(s[:i]+s[j]+s[i+1:j]+s[i]+s[j+1:]==g for i in range(len(s)) for j in range(i+1,len(s)))
def lemonade_oracle(a):
 cash=[]
 for bill in a[0]:
  need=bill-5
  for coin in sorted(cash,reverse=True):
   if coin<=need:cash.remove(coin);need-=coin
  if need:return False
  cash.append(bill)
 return True

def rr(r,n=8):return [r.randint(0,9) for _ in range(n)]
def random_replace(r):
 s=''.join(r.choice('abcd') for _ in range(r.randint(1,12)));idx=sorted(r.sample(range(len(s)),r.randint(0,min(3,len(s)))));src=[s[i:i+1] for i in idx];return [s,idx,src,['x'+x for x in src]]
def random_overlap(r):
 n=r.randint(1,5);return [[[r.randrange(2) for _ in range(n)] for _ in range(n)],[[r.randrange(2) for _ in range(n)] for _ in range(n)]]
def random_rectangle(r):
 x1,y1=r.randint(-5,3),r.randint(-5,3);x2,y2=x1+r.randint(1,6),y1+r.randint(1,6);a1,b1=r.randint(-5,3),r.randint(-5,3);return [[x1,y1,x2,y2],[a1,b1,a1+r.randint(1,6),b1+r.randint(1,6)]]
def random_game(r):return [r.randint(0,30),r.randint(0,12),r.randint(1,10)]
def random_domino(r):return [''.join(r.choice('.LR') for _ in range(r.randint(1,20)))]
def random_magic(r):
 rows,cols=r.randint(1,5),r.randint(1,5);return [[[r.randint(0,12) for _ in range(cols)] for _ in range(rows)]]
def random_rooms(r):
 n=r.randint(1,8);return [[[j for j in range(n) if j!=i and r.random()<.2] for i in range(n)]]
def random_fib(r):return [''.join(str(r.randrange(10)) for _ in range(r.randint(3,14)))]
def random_backspace(r):return [''.join(r.choice('abc#') for _ in range(r.randint(1,15))),''.join(r.choice('abc#') for _ in range(r.randint(1,15)))]
def random_mountain(r):return [[r.randint(0,12) for _ in range(r.randint(3,12))]]
def random_straights(r):return [[r.randint(1,10) for _ in range(r.randint(1,12))],r.randint(1,5)]
def random_shifts(r):
 s=''.join(r.choice('abcxyz') for _ in range(r.randint(1,15)));return [s,[r.randint(0,50) for _ in s]]
def random_seats(r):
 x=[r.randrange(2) for _ in range(r.randint(2,15))];x[r.randrange(len(x))]=1
 if all(x):x[0]=0
 return [x]
def random_rich(r):
 n=r.randint(1,8);order=list(range(n));r.shuffle(order);edges=[[order[j],order[i]] for i in range(n) for j in range(i+1,n) if r.random()<.2];quiet=list(range(n));r.shuffle(quiet);return [edges,quiet]
def random_peak(r):
 peak=r.randint(1,8);return [list(range(peak))+list(range(peak,-1,-1))]
def random_fleet(r):
 target=r.randint(5,30);pos=r.sample(range(target),r.randint(1,min(8,target)));return [target,pos,[r.randint(1,8) for _ in pos]]
def random_score(r):
 s='';open_count=0
 for _ in range(r.randint(1,10)):
  if open_count==0 or r.random()<.6:s+='(';open_count+=1
  else:s+=')';open_count-=1
 return [s+')'*open_count]
def random_mirror(r):
 p=r.randint(1,100);return [p,r.randint(0,p)]
def random_buddy(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,8))),''.join(r.choice('abc') for _ in range(r.randint(1,8)))]
def random_lemonade(r):return [[r.choice((5,10,20)) for _ in range(r.randint(1,20))]]

REPLACE='''\
def simultaneous_find_replace(s, indices, sources, targets):
 edits={i:(a,b) for i,a,b in zip(indices,sources,targets)};out=[];i=0
 while i<len(s):
  if i in edits and s.startswith(edits[i][0],i):out.append(edits[i][1]);i+=len(edits[i][0])
  else:out.append(s[i]);i+=1
 return ''.join(out)
'''
OVERLAP='''\
def maximum_image_overlap(img1, img2):
 from collections import Counter
 left=[(r,c) for r,row in enumerate(img1) for c,x in enumerate(row) if x];right=[(r,c) for r,row in enumerate(img2) for c,x in enumerate(row) if x]
 return max(Counter((a-c,b-d) for a,b in left for c,d in right).values(),default=0)
'''
RECT='''\
def rectangles_overlap(rec1, rec2):
 return max(rec1[0],rec2[0])<min(rec1[2],rec2[2]) and max(rec1[1],rec2[1])<min(rec1[3],rec2[3])
'''
GAME='''\
def new_twenty_one_probability(n, k, max_pts):
 if k==0 or n>=k+max_pts-1:return 1.0
 dp=[0.0]*(n+1);dp[0]=1.0;window=1.0;answer=0.0
 for total in range(1,n+1):
  dp[total]=window/max_pts
  if total<k:window+=dp[total]
  else:answer+=dp[total]
  if total-max_pts>=0 and total-max_pts<k:window-=dp[total-max_pts]
 return answer
'''
DOMINO='''\
def pushed_dominoes(dominoes):
 s='L'+dominoes+'R';answer=[]
 for i in range(1,len(s)):
  if s[i]=='.':continue
  middle=i-1
  while middle>=0 and s[middle]=='.':middle-=1
  gap=i-middle-1;answer.append(s[middle])
  if s[middle]==s[i]:answer.extend(s[i]*gap)
  elif s[middle]=='L' and s[i]=='R':answer.extend('.'*gap)
  else:answer.extend('R'*(gap//2)+('.' if gap%2 else '')+'L'*(gap//2))
 return ''.join(answer)
'''
MAGIC='''\
def magic_square_count(grid):
 answer=0
 for r in range(len(grid)-2):
  for c in range(len(grid[0])-2):
   values=[grid[r+i][c+j] for i in range(3) for j in range(3)]
   sums=[sum(grid[r+i][c+j] for j in range(3)) for i in range(3)]+[sum(grid[r+i][c+j] for i in range(3)) for j in range(3)]+[sum(grid[r+i][c+i] for i in range(3)),sum(grid[r+i][c+2-i] for i in range(3))]
   answer+=sorted(values)==list(range(1,10)) and len(set(sums))==1
 return answer
'''
ROOMS='''\
def can_visit_all_rooms(rooms):
 seen={0};stack=[0]
 while stack:
  for key in rooms[stack.pop()]:
   if key not in seen:seen.add(key);stack.append(key)
 return len(seen)==len(rooms)
'''
FIB='''\
def split_fibonacci_sequence(num):
 values=[]
 def search(index):
  if index==len(num):return len(values)>=3
  value=0
  for end in range(index,min(len(num),index+10)):
   if end>index and num[index]=='0':break
   value=value*10+int(num[end])
   if value>2**31-1:break
   if len(values)>=2 and value<values[-1]+values[-2]:continue
   if len(values)>=2 and value>values[-1]+values[-2]:break
   values.append(value)
   if search(end+1):return True
   values.pop()
  return False
 return values if search(0) else []
'''
BACK='''\
def backspace_strings_equal(s, t):
 def clean(text):
  stack=[]
  for char in text:
   if char=='#':
    if stack:stack.pop()
   else:stack.append(char)
  return stack
 return clean(s)==clean(t)
'''
MOUNTAIN='''\
def longest_mountain_length(arr):
 best=up=down=0
 for i in range(1,len(arr)):
  if down and arr[i-1]<arr[i]:up=down=0
  if arr[i-1]<arr[i]:up+=1
  elif arr[i-1]>arr[i]:down+=1
  else:up=down=0
  if up and down:best=max(best,up+down+1)
 return best
'''
STRAIGHTS='''\
def can_form_straight_hands(hand, group_size):
 from collections import Counter
 if len(hand)%group_size:return False
 counts=Counter(hand)
 for start in sorted(counts):
  copies=counts[start]
  if copies:
   for value in range(start,start+group_size):
    if counts[value]<copies:return False
    counts[value]-=copies
 return True
'''
SHIFTS='''\
def shifted_letters(s, shifts):
 total=0;answer=[]
 for char,shift in zip(reversed(s),reversed(shifts)):
  total=(total+shift)%26;answer.append(chr((ord(char)-97+total)%26+97))
 return ''.join(reversed(answer))
'''
SEATS='''\
def maximum_seat_distance(seats):
 best=0;last=None
 for i,taken in enumerate(seats):
  if taken:
   best=max(best,i if last is None else (i-last)//2);last=i
 return max(best,len(seats)-1-last)
'''
RICH='''\
def quietest_richer_people(richer, quiet):
 graph=[[] for _ in quiet]
 for rich,poor in richer:graph[poor].append(rich)
 from functools import lru_cache
 @lru_cache(None)
 def solve(person):return min([person]+[solve(other) for other in graph[person]],key=quiet.__getitem__)
 return [solve(person) for person in range(len(quiet))]
'''
PEAK='''\
def mountain_peak_index(arr):
 left,right=0,len(arr)-1
 while left<right:
  middle=(left+right)//2
  if arr[middle]<arr[middle+1]:left=middle+1
  else:right=middle
 return left
'''
FLEET='''\
def car_fleet_count(target, position, speed):
 fleets=[]
 for p,v in sorted(zip(position,speed),reverse=True):
  time=(target-p)/v
  if not fleets or time>fleets[-1]:fleets.append(time)
 return len(fleets)
'''
SCORE='''\
def parentheses_score(s):
 score=depth=0
 for i,char in enumerate(s):
  if char=='(':depth+=1
  else:
   depth-=1
   if s[i-1]=='(':score+=1<<depth
 return score
'''
MIRROR='''\
def mirror_receptor(p, q):
 from math import gcd
 common=gcd(p,q);p//=common;q//=common
 if p%2==0:return 2
 return 1 if q%2 else 0
'''
BUDDY='''\
def are_buddy_strings(s, goal):
 if len(s)!=len(goal):return False
 different=[i for i in range(len(s)) if s[i]!=goal[i]]
 return len(set(s))<len(s) if not different else len(different)==2 and s[different[0]]==goal[different[1]] and s[different[1]]==goal[different[0]]
'''
LEMON='''\
def can_make_lemonade_change(bills):
 five=ten=0
 for bill in bills:
  if bill==5:five+=1
  elif bill==10:
   if not five:return False
   five-=1;ten+=1
  else:
   if ten and five:ten-=1;five-=1
   elif five>=3:five-=3
   else:return False
 return True
'''

def lesson(a,b,c,d):return [a,b,c,d],d
BATCH={
833:entry('simultaneous_find_replace',[('s','str'),('indices','list[int]'),('sources','list[str]'),('targets','list[str]')],'str',['strings','simulation'],['Replacement checks use the original string and operations do not overlap.','Apply only sources that match at their given indices.'],[(['abcd',[0,2],['a','cd'],['eee','ffff']],'Both sources match, producing eeebffff.'),(['abcd',[0,2],['ab','ec'],['eee','ffff']],'Only ab matches, producing eeecd.')],[[s,i,a,b] for s,i,a,b in (('a',[],[],[]),('a',[0],['a'],['x']),('a',[0],['b'],['x']),('abc',[1],['b'],['zz']),('abc',[0],['ab'],['x']),('aaaa',[0,2],['aa','aa'],['b','c']),('abcde',[0,3],['a','de'],['x','y']),('abc',[2],['c'],['q']),('abc',[0],['abcd'],['x']),('hello',[0,2],['he','ll'],['x','y']),('xyz',[0,1,2],['x','y','z'],['a','b','c']),('mississippi',[0,4],['miss','iss'],['x','y']))],REPLACE,[REPLACE.replace("s.startswith(edits[i][0],i)",'True'),REPLACE.replace("i+=len(edits[i][0])",'i+=1')],['Replaces a nonmatching source.','Advances by one and leaves source suffix characters behind.'],replace_oracle,random_replace,*lesson('Simultaneous means every match is tested against the unchanged source string.','Index operations and scan the source left to right.','At an operation index, append target and skip source length only if source matches; otherwise copy one character.','Nonoverlap makes the scan unambiguous and preserves every unreplaced character exactly once.'),'O(n+replacement output)','O(operations)',5),
835:entry('maximum_image_overlap',[('img1','list[list[int]]'),('img2','list[list[int]]')],'int',['matrices','hash-maps'],['Images are equal-size square binary matrices.','Translate one image without rotation and maximize positions where both contain one.'],[([[[1,1,0],[0,1,0],[0,1,0]],[[0,0,0],[0,1,1],[0,0,1]]],'A suitable translation aligns three one-cells.'),([[[1]],[[1]]],'The single one overlaps for score one.')],[[a,b] for a,b in (([[0]],[[0]]),([[1]],[[0]]),([[0]],[[1]]),([[1,0],[0,0]],[[0,1],[0,0]]),([[1,1],[0,0]],[[1,1],[0,0]]),([[1,0],[0,1]],[[0,1],[1,0]]),([[1,1],[1,1]],[[1,1],[1,1]]),([[0,0],[0,0]],[[1,1],[1,1]]),([[1,0,0],[0,1,0],[0,0,1]],[[0,1,0],[0,0,1],[0,0,0]]),([[1,1,0],[0,0,0],[0,0,0]],[[0,0,0],[0,1,1],[0,0,0]]),([[1,0],[1,0]],[[0,1],[0,1]]),([[1,0,1],[0,1,0],[1,0,1]],[[1,0,1],[0,1,0],[1,0,1]]))],OVERLAP,[OVERLAP.replace('(a-c,b-d)','(a+c,b+d)'),OVERLAP.replace('for c,d in right','for c,d in left')],['Adds coordinates instead of measuring translation vectors.','Compares the first image with itself.'],overlap_oracle,random_overlap,*lesson('Every aligned pair of one-cells votes for the translation vector between them.','Count differences between coordinates of ones in the two images.','For each one pair increment count[(r1-r2,c1-c2)]; take maximum.','Pairs sharing a translation align simultaneously, so its vote count equals overlap under that shift.'),'O(ones1*ones2)','O(n^2)',5),
836:entry('rectangles_overlap',[('rec1','list[int]'),('rec2','list[int]')],'bool',['geometry'],['Rectangles are [x1,y1,x2,y2] with positive area and axis-aligned.','Touching edges or corners do not count as positive-area overlap.'],[([[0,0,2,2],[1,1,3,3]],'Both axis projections overlap with positive length.'),([[0,0,1,1],[1,0,2,1]],'The rectangles only share an edge, so they do not overlap.')],[[a,b] for a,b in (([0,0,1,1],[2,2,3,3]),([0,0,2,2],[0,0,2,2]),([0,0,3,1],[1,-1,2,2]),([-2,-2,0,0],[-1,-1,1,1]),([0,0,1,2],[0,1,1,3]),([0,0,1,1],[0,1,1,2]),([1,1,4,4],[2,2,3,3]),([0,0,10,1],[5,0,6,1]),([0,0,1,10],[0,5,1,6]),([-3,0,-1,2],[-2,1,0,3]),([0,0,2,2],[2,2,4,4]),([0,0,5,5],[-1,-1,6,6]))],RECT,[RECT.replace('<min','<=min'),RECT.replace('and max','or max')],['Treats boundary contact as positive overlap.','Requires overlap on only one axis.'],rectangle_oracle,random_rectangle,*lesson('Positive rectangle intersection requires positive overlap on both coordinate axes.','Compare the larger lower bound with the smaller upper bound for x and y.','Return max(x1)<min(x2) and max(y1)<min(y2).','Strict inequalities exclude zero-width contact while conjunction enforces two-dimensional area.'),'O(1)','O(1)',3),
837:entry('new_twenty_one_probability',[('n','int'),('k','int'),('max_pts','int')],'float',['dynamic-programming','sliding-windows'],['Draw uniform 1..max_pts while score is below k, then stop.','Return probability final score is at most n within 1e-5.'],[([10,1,10],'One draw always lands from one through ten, so probability is one.'),([6,1,10],'Only six of ten possible first draws are at most six.')],[[n,k,m] for n,k,m in ((0,0,1),(1,0,10),(0,1,1),(1,1,1),(5,1,10),(10,10,1),(10,5,10),(15,10,10),(20,10,10),(21,17,10),(30,20,5),(100,50,20))],GAME,[GAME.replace('window/max_pts','window/(max_pts+1)'),GAME.replace('if total<k','if total<=k')],['Uses the wrong uniform draw denominator.','Continues drawing at score k.'],game_oracle,random_game,*lesson('The probability of reaching a score is the average of the previous maxPts active probabilities.','Maintain that average numerator as a sliding window.','dp[x]=window/maxPts; add dp[x] to window only if x<k, otherwise to answer; remove x-maxPts.','Only active pre-k states can generate future scores, and the window holds exactly those one-draw predecessors.'),'O(n)','O(n)',5),
838:entry('pushed_dominoes',[('dominoes','str')],'str',['two-pointers','simulation'],['L and R exert one unit of force per time step; equal opposing forces leave a domino upright.','Return the final state.'],[(['RR.L'],'The existing dot is balanced against no new force, so RR.L remains unchanged.'),(['.L.R...LR..L..'],'Resolving each interval between forces yields LL.RR.LLRRLL..')],[[s] for s in ('.','L','R','..','L.','R.','.L','.R','R.L','R..L','R...L','L...R','R...R','L...L','...L','R...')],DOMINO,[DOMINO.replace("s='L'+dominoes+'R'","s='R'+dominoes+'L'"),DOMINO.replace("'.' if gap%2 else ''","''")],['Uses reversed sentinel forces at the boundaries.','Drops the balanced center domino between equal-distance opposing forces.'],domino_oracle,random_domino,*lesson('Only the nearest non-dot forces bounding a dot interval determine its outcome.','Add neutral sentinels and resolve each interval by endpoint directions.','Equal forces fill the gap; L...R stays upright; R...L fills inward with optional center dot.','More distant forces are blocked by the interval endpoints, so intervals can be solved independently.'),'O(n)','O(n)',5),
840:entry('magic_square_count',[('grid','list[list[int]]')],'int',['matrices','simulation'],['Count 3-by-3 subgrids containing 1..9 exactly once with equal row, column, and diagonal sums.','Grid values may lie outside 1..9.'],[([[[4,3,8,4],[9,5,1,9],[2,7,6,2]]],'The left 3-by-3 window is magic; the right one is not.'),([[[1,1,1],[1,1,1],[1,1,1]]],'Equal sums alone are insufficient because values are not 1 through 9.')],[[g] for g in (([[4,3,8],[9,5,1],[2,7,6]]),([[8,1,6],[3,5,7],[4,9,2]]),([[1,2,3],[4,5,6],[7,8,9]]),([[4,3,8],[9,5,1],[2,6,7]]),([[0,0],[0,0]]),([[5]]),([[4,3,8,4],[9,5,1,9],[2,7,6,2],[4,3,8,4]]),([[10,3,8],[9,5,1],[2,7,6]]),([[2,7,6],[9,5,1],[4,3,8]]),([[6,7,2],[1,5,9],[8,3,4]]),([[4,9,2],[3,5,7],[8,1,6]]),([[4,3,8,0],[9,5,1,0],[2,7,6,0]]))],MAGIC,[MAGIC.replace("sorted(values)==list(range(1,10)) and ",''),MAGIC.replace('len(set(sums))==1','len(set(sums[:6]))==1')],['Checks sums but not the required digits.','Ignores diagonal sums.'],magic_oracle,random_magic,*lesson('A valid window needs both the exact digit multiset and eight equal line sums.','Enumerate 3-by-3 origins, collect nine values and all row/column/diagonal sums.','Accept sorted values 1..9 and one distinct sum.','Those checks are precisely the definition; each origin identifies one candidate window.'),'O(rows*columns)','O(1)',5),
841:entry('can_visit_all_rooms',[('rooms','list[list[int]]')],'bool',['graphs','depth-first-search'],['Room zero starts unlocked; keys found in visited rooms unlock named rooms.','Return whether all rooms become reachable.'],[([[[1],[2],[3],[]]],'The keys form a chain reaching every room.'),([[[1,3],[3,0,1],[2],[0]]],'Room two is never reached from room zero.')],[[x] for x in (([[]]),([[1],[]]),([[],[]]),([[1,2],[],[]]),([[1],[0]]),([[1],[2],[0]]),([[2],[2],[]]),([[1,2],[2],[1]]),([[3],[2],[3],[]]),([[1,1],[]]),([[1],[2],[3],[4],[]]),([[1,2],[3],[3],[],[]]))],ROOMS,[ROOMS.replace('seen={0}','seen=set()'),ROOMS.replace('if key not in seen','if key in seen')],['Does not initially mark room zero visited.','Follows only already-seen keys.'],rooms_oracle,random_rooms,*lesson('Rooms and keys form a directed reachability graph.','Run DFS or BFS from room zero and mark every newly unlocked room.','Pop a room, add unseen keys to seen and stack; compare seen count with room count.','Graph traversal reaches exactly the rooms unlockable by a chain of keys.'),'O(rooms+keys)','O(rooms)',5),
842:entry('split_fibonacci_sequence',[('num','str')],'list[int]',['backtracking','strings'],['Use every digit in order; numbers fit signed 32-bit and have no leading zeros except zero.','Return one Fibonacci-like sequence of length at least three or [].'],[(['1101111'],'Choosing 11,0 gives 11,11 and consumes all digits.'),(['0123'],'A leading-zero first number blocks every full Fibonacci split.')],[[s] for s in ('0000','1011','11235813','123456579','1234','011235','2147483647','11011','111','101','112358130','999999')],FIB,[FIB.replace("if end>index and num[index]=='0':break",''),FIB.replace('value>2**31-1','value>=2**31-1')],['Allows multi-digit values with leading zero.','Incorrectly rejects the maximum valid 32-bit value.'],fib_oracle,random_fib,*lesson('After choosing two numbers, every later number is forced.','Backtrack only over early cuts, pruning by the required sum and overflow.','Reject leading zeros; once two values exist compare candidate to their sum, continuing or breaking accordingly.','Monotone digit extension makes an oversized candidate impossible to repair, while exact matches uniquely advance the sequence.'),'O(n^2)','O(n)',5),
844:entry('backspace_strings_equal',[('s','str'),('t','str')],'bool',['stacks','strings'],['# deletes the preceding typed character when one exists.','Return whether both strings produce equal final text.'],[(['ab#c','ad#c'],'Both strings reduce to ac.'),(['a#c','b'],'The first reduces to c, which differs from b.')],[[a,b] for a,b in (('',''),('#',''),('##',''),('a#',''),('ab#','a'),('ab##',''),('abc###',''),('a##c','#a#c'),('bxj##tw','bxo#j##tw'),('nzp#o#g','b#nzp#o#g'),('abc','abc'),('####a','a'))],BACK,[BACK.replace('if stack:stack.pop()','stack.pop()'),BACK.replace("else:stack.append(char)","else:stack.insert(0,char)")],['Raises or mishandles backspaces on an empty buffer.','Builds surviving characters in reverse order.'],backspace_oracle,random_backspace,*lesson('Typing semantics are naturally represented by a stack of surviving characters.','Normalize each input independently.','Push letters; on # pop only when nonempty; compare final stacks.','The stack always equals the editor contents after the processed prefix.'),'O(n+m)','O(n+m)',3),
845:entry('longest_mountain_length',[('arr','list[int]')],'int',['two-pointers','arrays'],['A mountain has length at least three, strictly rises, then strictly falls.','Return the maximum contiguous mountain length or zero.'],[([[2,1,4,7,3,2,5]],'The subarray [1,4,7,3,2] has length five.'),([[2,2,2]],'No strict rise and fall exists.')],[[x] for x in ([1,2,1],[1,2,3,2,1],[1,2,3],[3,2,1],[1,1,2,1],[1,2,2,1],[0,1,0,1,0],[5,4,3,2,1],[1,3,2,4,6,5],[2,1,2,3,4,3,2],[1,2,1,1,2,1],[0,2,4,3,2,1,3])],MOUNTAIN,[MOUNTAIN.replace('if up and down','if up or down'),MOUNTAIN.replace('if down and arr[i-1]<arr[i]','if False')],['Counts pure rises or falls as mountains.','Fails to reset after a descent followed by a new rise.'],mountain_oracle,random_mountain,*lesson('A mountain is characterized by consecutive up-step and down-step counts.','Scan slopes, resetting on plateaus and when a new rise follows descent.','Increment up/down by comparison; when both positive update up+down+1.','The counters describe the unique maximal slope run ending at each index.'),'O(n)','O(1)',5),
846:entry('can_form_straight_hands',[('hand','list[int]'),('group_size','int')],'bool',['greedy','hash-maps'],['Every card must belong to a group of group_size consecutive values.','Duplicate values represent distinct cards.'],[([[1,2,3,6,2,3,4,7,8],3],'Groups [1,2,3], [2,3,4], and [6,7,8] use all cards.'),([[1,2,3,4,5],4],'Five cards cannot be divided into groups of four.')],[[h,g] for h,g in (([1],1),([1,2],2),([1,3],2),([1,2,2,3],2),([1,2,2,3],4),([1,2,3,4],2),([1,2,3,4],4),([1,1,2,2,3,3],3),([2,3,4,5,6,7],3),([1,2,4,5],2),([10,11,12],3),([1,2,3,3,4,4,5,6],4))],STRAIGHTS,[STRAIGHTS.replace('counts[value]<copies','counts[value]==0'),STRAIGHTS.replace('for start in sorted(counts)','for start in counts')],['Removes one copy rather than all groups starting at the smallest value.','Processes hash insertion order instead of numeric order.'],straights_oracle,random_straights,*lesson('The smallest remaining card must start a group because no smaller predecessor can consume it.','Process values ascending and remove all copies of each start from its consecutive range.','For copies=count[start], subtract copies from start..start+size-1, rejecting shortages.','The forced smallest choice is safe; batching equal starts handles duplicates without changing the greedy proof.'),'O(n log n)','O(n)',5),
848:entry('shifted_letters',[('s','str'),('shifts','list[int]')],'str',['prefix-sums','strings'],['shifts[i] rotates letters 0 through i forward with wraparound.','Return the final lowercase string.'],[(['abc',[3,5,9]],'Suffix shift totals are 17,14,9, producing rpl.'),(['aaa',[1,2,3]],'The letters receive totals six, five, and three, producing gfd.')],[[s,x] for s,x in (('a',[0]),('a',[1]),('z',[1]),('ab',[1,1]),('abc',[0,0,0]),('xyz',[1,1,1]),('az',[26,52]),('hello',[1,2,3,4,5]),('a',[100]),('abcd',[3,0,2,1]),('zzzz',[25,25,25,25]),('python',[10,20,30,40,50,60]))],SHIFTS,[SHIFTS.replace('reversed(shifts)','shifts'),SHIFTS.replace('%26','%25')],['Pairs reversed characters with forward-order shifts.','Wraps letters modulo 25 instead of 26.'],shifts_oracle,random_shifts,*lesson('Position i receives every operation whose prefix reaches i, which is the suffix sum from i onward.','Scan both arrays right-to-left with a running shift modulo 26.','total=(total+shifts[i])%26; rotate s[i] by total.','The running total contains exactly the operations affecting the current and earlier positions.'),'O(n)','O(n)',5),
849:entry('maximum_seat_distance',[('seats','list[int]')],'int',['arrays','greedy'],['At least one seat is occupied and one is empty.','Choose an empty seat maximizing distance to the closest occupied seat.'],[([[1,0,0,0,1,0,1]],'The center of the three-seat gap is distance two from either occupied end.'),([[1,0,0,0]],'The trailing empty seat is distance three from the occupied seat.')],[[x] for x in ([0,1],[1,0],[1,0,1],[1,0,0,1],[0,0,1],[1,0,0,0,1],[0,1,0,0,1],[1,0,1,0,1],[0,0,0,1,0],[1,0,0,1,0,0],[0,1,0],[0,0,1,0,0])],SEATS,[SEATS.replace('(i-last)//2','i-last'),SEATS.replace('i if last is None','i//2 if last is None')],['Uses the full interior gap rather than half.','Halves the leading edge gap as though it had two occupied endpoints.'],seats_oracle,random_seats,*lesson('Edge gaps use their full length; interior gaps contribute half rounded down.','Track the previous occupied index while scanning occupied seats.','Update leading i, interior (i-last)//2, and trailing n-1-last.','The nearest occupied seat in each independent gap determines its optimal position and distance.'),'O(n)','O(1)',5),
851:entry('quietest_richer_people',[('richer','list[list[int]]'),('quiet','list[int]')],'list[int]',['graphs','depth-first-search'],['richer pairs [a,b] mean a is richer than b; relations are consistent.','For each person return the quietest person known to be at least as rich.'],[([[[1,0],[2,1],[3,1],[3,7],[4,3],[5,3],[6,3]],[3,2,5,4,6,1,7,0]],'Ancestor searches select [5,5,2,5,4,5,6,7].'),([[],[0]],'With no richer relation, the only person selects themself.')],[[r,q] for r,q in (([],[1,0]),([[1,0]],[1,0]),([[1,0]],[0,1]),([[2,1],[1,0]],[3,2,1]),([[1,0],[2,0]],[2,1,0]),([[2,0],[2,1]],[1,2,0]),([[1,0],[2,1],[3,2]],[3,2,1,0]),([[3,1],[3,2]],[3,2,1,0]),([[1,0],[2,0],[3,1],[3,2]],[4,3,2,1]),([],list(range(10))),([[4,3],[3,2],[2,1],[1,0]],[0,1,2,3,4]),([[2,0],[3,0],[4,2],[4,3]],[5,4,3,2,1]))],RICH,[RICH.replace('graph[poor].append(rich)','graph[rich].append(poor)'),RICH.replace('key=quiet.__getitem__','key=lambda x:x')],['Traverses poorer descendants instead of richer ancestors.','Chooses the smallest index rather than the quietest score.'],rich_oracle,random_rich,*lesson('Each answer depends on the answers of directly richer neighbors, forming memoizable graph ancestry.','Build edges from poorer to richer and DFS for the quietest reachable candidate.','solve(p)=argmin quiet among p and solve(richer neighbors).','Consistency makes the relation acyclic, and recursion considers every richer ancestor exactly through its incoming chain.'),'O(people+relations)','O(people+relations)',5),
852:entry('mountain_peak_index',[('arr','list[int]')],'int',['binary-search','arrays'],['arr strictly rises to one peak then strictly falls.','Return the peak index in logarithmic time.'],[([[0,1,0]],'The maximum one is at index one.'),([[0,2,1,0]],'The sequence changes from rising to falling at index one.')],[[x] for x in ([0,1,0],[0,1,2,1],[0,3,2,1],[1,5,2],[0,1,2,3,2,1],[0,10,5,2],[1,2,3,4,0],[0,2,4,6,5],[3,5,9,7,1],[0,100,99],[1,3,8,12,4,2],[0,1,5,10,9,8,2])],PEAK,[PEAK.replace('arr[middle]<arr[middle+1]','arr[middle]<=arr[middle+1]'),PEAK.replace('right=middle','right=middle-1')],['Uses a non-strict comparison inconsistent with the contract.','Can skip the peak when moving the right boundary.'],peak_oracle,random_peak,*lesson('The slope at middle reveals which side contains the unique peak.','Binary-search with a closed candidate interval.','If arr[mid]<arr[mid+1], peak is right; otherwise peak is at mid or left.','Strict mountain shape guarantees the slope changes exactly once, so each comparison discards only nonpeak indices.'),'O(log n)','O(1)',5),
853:entry('car_fleet_count',[('target','int'),('position','list[int]'),('speed','list[int]')],'int',['sorting','stacks'],['Cars drive toward target without passing; catching a fleet joins it at the slower speed.','Return the number of fleets arriving at target.'],[([12,[10,8,0,5,3],[2,4,1,1,3]],'Processing from nearest to target groups the cars into three fleets.'),([10,[3],[3]],'One car forms one fleet.')],[[t,p,s] for t,p,s in ((10,[0],[1]),(10,[0,5],[1,1]),(10,[0,5],[2,1]),(10,[0,5],[1,2]),(12,[10,8],[2,4]),(20,[0,10,15],[4,2,1]),(10,[6,8],[2,1]),(100,[0,25,50,75],[4,3,2,1]),(10,[1,2,3],[3,2,1]),(15,[0,5,10],[1,1,1]),(8,[0,4],[4,2]),(30,[5,10,20,25],[5,4,2,1]))],FLEET,[FLEET.replace('time>fleets[-1]','time>=fleets[-1]'),FLEET.replace('reverse=True','reverse=False')],['Counts equal-arrival cars as separate fleets.','Processes cars farthest-first and forms fleets prematurely.'],fleet_oracle,random_fleet,*lesson('Scanning from nearest to target, a car joins the fleet ahead exactly when its arrival time is no later.','Sort positions descending and keep increasing fleet arrival times.','Compute time=(target-position)/speed; append only if time exceeds last fleet time.','A later arrival cannot catch the fleet ahead and starts a new fleet; an earlier/equal arrival merges.'),'O(n log n)','O(n)',5),
856:entry('parentheses_score',[('s','str')],'int',['stacks','strings'],['s is balanced parentheses.','() scores 1, concatenation adds, and wrapping doubles.'],[(['()'],'One primitive pair scores one.'),(['(()(()))'],'The inner concatenation scores three and the outer wrapping doubles it to six.')],[[s] for s in ('(())','()()','((()))','(()())','()(())','((())())','()()()','(((())))','(())()','(()(()))','((()()))','()((()))')],SCORE,[SCORE.replace('1<<depth','1<<(depth+1)'),SCORE.replace("if s[i-1]=='('",'if True')],['Doubles every primitive contribution once too many.','Adds a contribution at every closing parenthesis, including nonprimitive closures.'],score_oracle,random_score,*lesson('Each primitive () contributes 2^depth where depth is measured after its closing parenthesis.','Track nesting depth and add only when a closing parenthesis immediately follows an opening one.','On close decrement depth; if previous was ( add 1<<depth.','Wrapping doubles primitive contributions per containing level, and concatenated primitives add independently.'),'O(n)','O(1)',5),
858:entry('mirror_receptor',[('p','int'),('q','int')],'int',['math','geometry'],['A laser starts at the southwest corner of a p-square room and rises q while crossing width p.','Return receptor 0 northwest, 1 northeast, or 2 southeast.'],[([2,1],'After unfolding, the first corner reached corresponds to southeast receptor two.'),([3,1],'The first common corner corresponds to northeast receptor one.')],[[p,q] for p,q in ((1,0),(1,1),(2,0),(2,2),(3,2),(4,1),(4,2),(4,3),(5,1),(5,2),(6,4),(100,75))],MIRROR,[MIRROR.replace('if p%2==0:return 2','if q%2==0:return 2'),MIRROR.replace('return 1 if q%2 else 0','return 0 if q%2 else 1')],['Uses vertical parity to choose the southeast receptor.','Swaps the northwest and northeast parity cases.'],mirror_oracle,random_mirror,*lesson('Unfolding reflections turns the ray into a straight line; the first corner is governed by reduced p and q parity.','Divide p and q by their gcd and inspect odd/even parity.','Even reduced p gives receptor 2; otherwise odd q gives 1 and even q gives 0.','The least common horizontal/vertical travel counts determine which room boundaries are reached at the first corner.'),'O(log p)','O(1)',5),
859:entry('are_buddy_strings',[('s','str'),('goal','str')],'bool',['strings','hash-maps'],['Swap exactly two distinct positions in s.','Return whether one swap can make s equal goal.'],[(['ab','ba'],'Swapping the two positions produces ba.'),(['ab','ab'],'Equal strings with distinct letters cannot remain equal after one required swap.')],[[a,b] for a,b in (('aa','aa'),('a','a'),('abc','acb'),('abc','abc'),('aaaa','aaaa'),('ab','ca'),('abcd','abdc'),('abcd','badc'),('abca','abca'),('abc','bac'),('xxy','xyx'),('aaaaab','baaaaa'))],BUDDY,[BUDDY.replace('len(set(s))<len(s)','True'),BUDDY.replace('len(different)==2','len(different)<=2')],['Allows equal strings without a duplicate character to swap.','Accepts a single mismatch even though one swap cannot fix it.'],buddy_oracle,random_buddy,*lesson('A successful swap yields either exactly two cross-matching mismatches, or zero mismatches with a duplicate available.','Collect mismatch indices after checking equal lengths.','Zero mismatches requires duplicate; two requires crossed characters; every other count rejects.','A swap changes at most two positions, and these cases precisely characterize whether it can preserve or repair equality.'),'O(n)','O(alphabet)',3),
860:entry('can_make_lemonade_change',[('bills','list[int]')],'bool',['greedy','simulation'],['Each lemonade costs five and customers pay 5, 10, or 20 in order.','Start with no change and return whether exact change can be given to everyone.'],[([[5,5,5,10,20]],'Three fives cover the ten-dollar and then the twenty-dollar change.'),([[5,5,10,10,20]],'After two ten-dollar customers, no five remains for the final twenty.')],[[x] for x in ([5],[10],[20],[5,10],[5,20],[5,5,20],[5,5,5,20],[5,10,5,20],[5,5,10,20],[5,10,10],[5,5,5,10,10,20],[5,5,5,5,10,20,20])],LEMON,[LEMON.replace('if ten and five','if five>=3'),LEMON.replace('elif five>=3','elif ten and five')],['Spends three fives before a ten and a five, reducing future flexibility.','The alternate branch order mishandles available denominations.'],lemonade_oracle,random_lemonade,*lesson('For a twenty, spending one ten preserves more five-dollar bills than spending three fives.','Track counts of fives and tens, greedily prefer 10+5 for fifteen change.','On 10 spend one five; on 20 spend 10+5 else three fives; reject shortages.','Tens have no use except twenty-dollar change, while fives are required for both, so preserving fives is optimal.'),'O(n)','O(1)',3),
}
for i in (837,):BATCH[i]['comparator']='float'

BATCH[838]['reference']='''\
def pushed_dominoes(dominoes):
    size=len(dominoes);forces=[0]*size;force=0
    for index,char in enumerate(dominoes):
        if char=='R':force=size
        elif char=='L':force=0
        else:force=max(0,force-1)
        forces[index]+=force
    force=0
    for index in range(size-1,-1,-1):
        char=dominoes[index]
        if char=='L':force=size
        elif char=='R':force=0
        else:force=max(0,force-1)
        forces[index]-=force
    return ''.join('R' if force>0 else 'L' if force<0 else '.' for force in forces)
'''
BATCH[842]['boundaries'].append(['021474836472147483647'])
BATCH[844]['wrong'][0]='''\
def backspace_strings_equal(s, t):
    def clean(text):
        stack=[]
        for char in text:
            if char=='#' and stack:stack.pop()
            else:stack.append(char)
        return stack
    return clean(s)==clean(t)
'''
BATCH[846]['wrong'][0]='''\
def can_form_straight_hands(hand, group_size):
    from collections import Counter
    if len(hand)%group_size:return False
    counts=Counter(hand)
    for start in sorted(counts):
        if counts[start]:
            for value in range(start,start+group_size):
                if not counts[value]:return False
                counts[value]-=1
    return True
'''
BATCH[846]['boundaries'].append([[2,3,1,2],2])
BATCH[852]['wrong'][0]='''\
def mountain_peak_index(arr):
    for index in range(len(arr)-1):
        if arr[index]>arr[index+1]:return index+1
'''
BATCH[859]['boundaries'].append(['a','b'])
BATCH[859]['wrong'][1]='''\
def are_buddy_strings(s, goal):
    if len(s)!=len(goal):return False
    different=[i for i in range(len(s)) if s[i]!=goal[i]]
    if len(different)<=1:return True
    return len(different)==2 and s[different[0]]==goal[different[1]] and s[different[1]]==goal[different[0]]
'''
