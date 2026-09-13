"""Reviewed DP, BFS, heap, MST, and search imports (batch 84b)."""
from collections import Counter, deque
from functools import lru_cache
from itertools import combinations, product

from .import_batch_055 import entry
from .import_batch_082 import make_tree

MOD=1_000_000_007

def dice_oracle(a):
 n,k,target=a
 return sum(sum(roll)==target for roll in product(range(1,k+1),repeat=n))%MOD
def repeat_oracle(a):
 text=a[0];best=0
 for i in range(len(text)):
  for j in range(i,len(text)):
   chars=list(text);chars[i],chars[j]=chars[j],chars[i];run=1
   for k in range(1,len(chars)):run=run+1 if chars[k]==chars[k-1] else 1;best=max(best,run)
 return max(best,1)
def level_oracle(a):
 root=make_tree(a[0]);level=[root];depth=1;best_depth=1;best=root[0]
 while level:
  total=sum(n[0] for n in level)
  if total>best:best=total;best_depth=depth
  level=[child for node in level for child in node[1:] if child];depth+=1
 return best_depth
def distance_oracle(a):
 g=a[0];land=[(r,c) for r,row in enumerate(g) for c,v in enumerate(row) if v];water=[(r,c) for r,row in enumerate(g) for c,v in enumerate(row) if not v]
 if not land or not water:return -1
 return max(min(abs(r-x)+abs(c-y) for x,y in land) for r,c in water)
def last_oracle(a):return max(a[0][i:] for i in range(len(a[0])))
def keyboard_oracle(a):
 keyboard,word=a;where={c:i for i,c in enumerate(keyboard)};at=total=0
 for c in word:total+=abs(where[c]-at);at=where[c]
 return total
def sticks_oracle(a):
 values=tuple(sorted(a[0]))
 @lru_cache(None)
 def solve(state):
  if len(state)<2:return 0
  return min(state[i]+state[j]+solve(tuple(sorted([state[k] for k in range(len(state)) if k not in (i,j)]+[state[i]+state[j]]))) for i in range(len(state)) for j in range(i+1,len(state)))
 return solve(values)
def water_oracle(a):
 n,wells,pipes=a;edges=[[0,i+1,c] for i,c in enumerate(wells)]+pipes;best=None
 for chosen in combinations(edges,n):
  parent=list(range(n+1))
  def find(x):
   while parent[x]!=x:x=parent[x]
   return x
  for x,y,_ in chosen:parent[find(x)]=find(y)
  if len({find(i) for i in range(n+1)})==1:
   cost=sum(e[2] for e in chosen);best=cost if best is None else min(best,cost)
 return best
def invalid_oracle(a):
 tx=a[0];parts=[x.split(',') for x in tx];bad=[]
 for i,(name,time,amount,city) in enumerate(parts):
  if int(amount)>1000 or any(i!=j and name==n and city!=c and abs(int(time)-int(t))<=60 for j,(n,t,_,c) in enumerate(parts)):bad.append(tx[i])
 return bad
def frequency_oracle(a):
 queries,words=a
 def f(s):return s.count(min(s))
 return [sum(f(q)<f(w) for w in words) for q in queries]

def random_dice(r):
 n,k=r.randint(1,5),r.randint(1,6);return [n,k,r.randint(1,n*k+2)]
def random_repeat(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,9)))]
def random_tree(r):return [[r.randint(-20,20) for _ in range(r.randint(1,15))]]
def random_square(r):
 n=r.randint(1,6);return [[[r.randint(0,1) for _ in range(n)] for _ in range(n)]]
def random_string(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,20)))]
def random_keyboard(r):
 keys=list('abcdefghijklmnopqrstuvwxyz');r.shuffle(keys);return [''.join(keys),''.join(r.choice(keys) for _ in range(r.randint(1,20)))]
def random_sticks(r):return [[r.randint(1,20) for _ in range(r.randint(1,5))]]
def random_water(r):
 n=r.randint(1,5);pipes=[[i,j,r.randint(1,15)] for i in range(1,n+1) for j in range(i+1,n+1) if r.random()<.5];return [n,[r.randint(1,15) for _ in range(n)],pipes]
def random_transactions(r):
 out=[]
 for _ in range(r.randint(1,10)):out.append(f"{r.choice(['alice','bob','lee'])},{r.randint(0,120)},{r.randint(1,1500)},{r.choice(['mtv','beijing','la'])}")
 return [out]
def random_frequency(r):
 word=lambda:''.join(r.choice('abcd') for _ in range(r.randint(1,8)))
 return [[word() for _ in range(r.randint(1,7))],[word() for _ in range(r.randint(1,7))]]

DICE='''def dice_roll_ways(n, k, target):
 mod=1000000007;dp=[0]*(target+1);dp[0]=1
 for _ in range(n):
  following=[0]*(target+1)
  for total,count in enumerate(dp):
   for face in range(1,min(k,target-total)+1):following[total+face]=(following[total+face]+count)%mod
  dp=following
 return dp[target]
'''
REPEAT='''def longest_repeated_after_swap(text):
 from collections import Counter
 counts=Counter(text);answer=0
 for char,total in counts.items():
  left=other=0
  for right,value in enumerate(text):
   other+=value!=char
   while other>1:other-=text[left]!=char;left+=1
   answer=max(answer,min(right-left+1,total))
 return answer
'''
LEVEL='''def maximum_level_sum_depth(root):
 level=[root];depth=1;best_depth=1;best=float('-inf')
 while level:
  total=sum(node.val for node in level)
  if total>best:best=total;best_depth=depth
  level=[child for node in level for child in (node.left,node.right) if child];depth+=1
 return best_depth
'''
DIST='''def farthest_water_distance(grid):
 from collections import deque
 n=len(grid);q=deque((r,c) for r in range(n) for c in range(n) if grid[r][c])
 if not q or len(q)==n*n:return -1
 distance=-1
 while q:
  distance+=1
  for _ in range(len(q)):
   r,c=q.popleft()
   for x,y in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
    if 0<=x<n and 0<=y<n and grid[x][y]==0:grid[x][y]=2;q.append((x,y))
 return distance
'''
LAST='''def lexicographically_last_substring(s):
 i,j,k=0,1,0;n=len(s)
 while j+k<n:
  if s[i+k]==s[j+k]:k+=1;continue
  if s[i+k]<s[j+k]:i=max(i+k+1,j);j=i+1
  else:j=j+k+1
  k=0
 return s[i:]
'''
KEY='''def single_row_keyboard_time(keyboard, word):
 positions={char:i for i,char in enumerate(keyboard)};at=total=0
 for char in word:total+=abs(positions[char]-at);at=positions[char]
 return total
'''
STICKS='''def minimum_stick_connection_cost(sticks):
 import heapq
 heap=list(sticks);heapq.heapify(heap);total=0
 while len(heap)>1:
  joined=heapq.heappop(heap)+heapq.heappop(heap);total+=joined;heapq.heappush(heap,joined)
 return total
'''
WATER='''def minimum_water_supply_cost(n, wells, pipes):
 parent=list(range(n+1))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 total=0
 for cost,x,y in sorted([(cost,0,i+1) for i,cost in enumerate(wells)]+[(cost,x,y) for x,y,cost in pipes]):
  a,b=find(x),find(y)
  if a!=b:parent[a]=b;total+=cost
 return total
'''
INVALID='''def invalid_transactions(transactions):
 parsed=[item.split(',') for item in transactions];bad=[]
 for i,(name,time,amount,city) in enumerate(parsed):
  invalid=int(amount)>1000 or any(i!=j and name==other_name and city!=other_city and abs(int(time)-int(other_time))<=60 for j,(other_name,other_time,_,other_city) in enumerate(parsed))
  if invalid:bad.append(transactions[i])
 return bad
'''
FREQ='''def smallest_character_frequency_counts(queries, words):
 from bisect import bisect_right
 def frequency(text):return text.count(min(text))
 values=sorted(frequency(word) for word in words)
 return [len(values)-bisect_right(values,frequency(query)) for query in queries]
'''

E=entry
BATCH={
1155:E('dice_roll_ways',[('n','int'),('k','int'),('target','int')],'int',['dynamic-programming'],['Each die has faces 1 through k.','Return the count modulo 1,000,000,007.'],[([1,6,3],'One die has exactly one way to total three.'),([2,6,7],'Six ordered pairs total seven.')],[[n,k,t] for n,k,t in [(1,1,1),(1,2,3),(2,2,2),(2,2,3),(2,2,4),(3,2,3),(3,2,4),(3,3,5),(4,2,5),(2,6,12),(3,6,18),(3,6,2),(4,3,8),(5,2,7)]],DICE,[DICE.replace('dp[0]=1','dp[1]=1'),DICE.replace('range(1,min(k,target-total)+1)','range(1,min(k,target-total))')],['Initializes one way to total one instead of zero.','Excludes the largest legal face from each transition.'],dice_oracle,random_dice,['Let dp[sum] count ways after the dice processed so far.','Begin with one way to make zero using no dice.','For each die, add every face value into a fresh table, reducing modulo the required constant.','Each ordered roll sequence follows exactly one transition path, so the final target cell is exact.'],'O(n*k*target)','O(target)',5),
1156:E('longest_repeated_after_swap',[('text','str')],'int',['sliding-window','hash-maps'],['At most one swap may be performed.','Return the longest all-equal substring length.'],[(['ababa'],'Swapping one b with an a creates a run of three a characters.'),(['aaabaaa'],'The separated a groups can form a run of six because only six a characters exist.')],[[s] for s in ['a','aa','ab','aba','abba','aaaa','abcdef','aaabbaaa','bbababaaaa','aabaa','abcabc','zzzyzzz','abbba','baaab']],REPEAT,[REPEAT.replace('other>1','other>0'),REPEAT.replace('min(right-left+1,total)','right-left+1')],['Allows no interrupting character in the window.','Can report a run longer than the total available copies of the character.'],repeat_oracle,random_repeat,['Count total occurrences of each candidate character.','For one character, slide a window containing at most one different character.','Its achievable run is min(window length,total copies); maximize across windows and characters.','The one mismatch can be swapped with an outside copy, while the total count caps the result.'],'O(alphabet*n)','O(alphabet)',5),
1161:E('maximum_level_sum_depth',[('root','TreeNode')],'int',['trees','breadth-first-search'],['The tree is nonempty.','Return the smallest one-based level with maximum sum.'],[([[1,7,0,7,-8,None,None]],'Level two sums to seven, exceeding levels one and three.'),([[1]],'The only level is level one.')],[[t] for t in [[0],[-1],[-1,-2,-3],[1,2,3],[1,7,0,7,-8],[5,1,1,10,0,0,0],[1,-1,-1,5,5],[10,-5,-5,-5,-5],[1,2,3,4,5,6,7],[3,3,0,0,0,3,3],[-10,1,2,3,4],[2,None,3,None,4],[8,4,12,2,6,10,14],[1,1,0]]],LEVEL,[LEVEL.replace('total>best','total>=best'),LEVEL.replace('best_depth=depth','best_depth=depth+1')],['Chooses the later level when sums tie.','Reports levels using an off-by-one depth.'],level_oracle,random_tree,['Breadth-first traversal naturally groups nodes by level.','Sum every current level before constructing the next one.','Update only on a strictly larger sum to preserve the smallest depth on ties.','Each node contributes once to exactly its own level total.'],'O(n)','O(width)',5),
1162:E('farthest_water_distance',[('grid','list[list[int]]')],'int',['matrix','breadth-first-search'],['grid is square and binary.','Return -1 for all-land or all-water grids.'],[([[[1,0,1],[0,0,0],[1,0,1]]],'The center water cell is distance two from land.'),([[[1,0,0],[0,0,0],[0,0,0]]],'The opposite corner is four steps from the sole land cell.')],[[g] for g in [[[0]],[[1]],[[1,0],[0,0]],[[0,1],[0,0]],[[1,1],[1,0]],[[0,0],[0,0]],[[1,1],[1,1]],[[1,0,1],[0,0,0],[1,0,1]],[[1,0,0],[0,0,0],[0,0,1]],[[0,0,1],[0,0,0],[1,0,0]],[[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],[[1,1,0],[1,0,0],[0,0,0]],[[0,1,0],[0,0,0],[0,0,0]],[[1,0,1,0],[0,0,0,0],[0,1,0,0],[0,0,0,1]]]],DIST,[DIST.replace('len(q)==n*n','len(q)==0'),DIST.replace('return distance','return distance-1')],['Treats any grid containing land as an invalid all-water case.','Subtracts an extra BFS layer from the distance.'],distance_oracle,random_square,['Start a multi-source BFS from every land cell simultaneously.','Reject the two grids lacking either terrain type.','Expand layer by layer into unvisited water, marking it when queued.','The final BFS layer is the maximum of every water cell’s nearest-land distance.'],'O(n^2)','O(n^2)',5),
1163:E('lexicographically_last_substring',[('s','str')],'str',['two-pointers','strings'],['s is nonempty.','Return the lexicographically greatest suffix.'],[(['abab'],'The suffix bab is lexicographically greatest.'),(['leetcode'],'The suffix tcode begins with the greatest available leading character.')],[[s] for s in ['a','aa','ab','ba','abc','cba','banana','abab','aaaaab','zzza','mississippi','cabca','leetcode','azbycx']],LAST,[LAST.replace('s[i+k]<s[j+k]','s[i+k]>s[j+k]'),LAST.replace('return s[i:]','return s[j:]')],['Advances the candidate with the larger mismatch character.','Returns the challenger pointer rather than the surviving best pointer.'],last_oracle,random_string,['Compare two candidate suffix starts while tracking their common prefix length.','At the first mismatch, discard the start whose character is smaller along with starts proven no better inside the matched block.','Reset the matched length after advancing a candidate.','Every discarded start loses a direct lexicographic comparison, leaving the unique best suffix start.'],'O(n)','O(1)',8),
1165:E('single_row_keyboard_time',[('keyboard','str'),('word','str')],'int',['hash-maps','strings'],['keyboard is a permutation of lowercase letters.','The finger starts at keyboard index zero.'],[(['abcdefghijklmnopqrstuvwxyz','cba'],'Moves 0→2→1→0 take four time units.'),(['pqrstuvwxyzabcdefghijklmno','leetcode'],'Position lookup determines each travel distance in the rearranged keyboard.')],[[k,w] for k,w in [('abcdefghijklmnopqrstuvwxyz','a'),('abcdefghijklmnopqrstuvwxyz','z'),('abcdefghijklmnopqrstuvwxyz','az'),('abcdefghijklmnopqrstuvwxyz','za'),('abcdefghijklmnopqrstuvwxyz','hello'),('zyxwvutsrqponmlkjihgfedcba','abc'),('zyxwvutsrqponmlkjihgfedcba','zzz'),('bcdefghijklmnopqrstuvwxyza','abc'),('qwertyuiopasdfghjklzxcvbnm','type'),('abcdefghijklmnopqrstuvwxyz','code'),('mnbvcxzlkjhgfdsaqwertyuiop','map'),('abcdefghijklmnopqrstuvwxyz','aaaa'),('zyxwvutsrqponmlkjihgfedcba','az'),('phqgiumeaylnofdxjkrcvstzwb','leetcode')]],KEY,[KEY.replace('at=total=0','at=total=1'),KEY.replace('abs(positions[char]-at)','positions[char]-at')],['Starts the finger at index one.','Uses signed movement and lets leftward travel reduce time.'],keyboard_oracle,random_keyboard,['Map each character to its keyboard index.','Track the current finger index, initially zero.','Add the absolute index difference for each typed character, then move the finger there.','The sum includes every required adjacent-key step exactly once.'],'O(26+word)','O(26)',3),
1167:E('minimum_stick_connection_cost',[('sticks','list[int]')],'int',['heaps','greedy'],['Every merge costs the sum of its two sticks.','Continue until one stick remains.'],[([[2,4,3]],'Merge two and three for five, then five and four for nine: total fourteen.'),([[1,8,3,5]],'Repeatedly merging the two shortest gives total thirty.')],[[s] for s in [[1],[1,1],[1,2],[2,4,3],[1,8,3,5],[5,5,5],[1,2,3,4],[10,1,1],[7,6,5,4],[2,2,2,2],[100,1,2],[3,9,1,2],[8,4],[1,1,1,1,1]]],STICKS,[STICKS.replace('heapq.heappop(heap)+heapq.heappop(heap)','heapq.heappop(heap)+heapq.heappop(heap) if len(heap)>2 else 0'),STICKS.replace('heapq.heapify(heap)','heap.sort(reverse=True)')],['Makes the final merge free.','Sorts descending but still pops from the end using heap operations on an invalid heap.'],sticks_oracle,random_sticks,['A min-heap exposes the two shortest current sticks.','Merge those two, add their length to cost, and push the combined stick back.','Repeat until one stick remains.','The exchange argument for optimal merge patterns shows the two least weights can be siblings in an optimal tree.'],'O(n log n)','O(n)',5),
1168:E('minimum_water_supply_cost',[('n','int'),('wells','list[int]'),('pipes','list[list[int]]')],'int',['minimum-spanning-tree','union-find'],['House labels are 1 through n.','Each house may connect directly to a virtual source at its well cost.'],[([3,[1,2,2],[[1,2,1],[2,3,1]]],'A well at house one plus two unit-cost pipes totals three.'),([2,[5,5],[[1,2,1]]],'One well and the pipe cost six.')],[[n,w,p] for n,w,p in [(1,[3],[]),(2,[1,2],[]),(2,[5,5],[[1,2,1]]),(3,[1,2,2],[[1,2,1],[2,3,1]]),(3,[5,1,5],[[1,2,2],[2,3,2]]),(3,[1,1,1],[[1,2,10],[2,3,10]]),(4,[4,4,4,4],[[1,2,1],[2,3,1],[3,4,1]]),(3,[10,10,1],[[1,2,2],[2,3,2]]),(2,[1,100],[[1,2,50]]),(4,[1,9,9,9],[[1,2,2],[1,3,3],[1,4,4]]),(3,[4,4,4],[]),(5,[5,4,3,2,1],[[1,2,1],[2,3,1],[3,4,1],[4,5,1]]),(3,[3,3,3],[[1,2,3],[2,3,3],[1,3,3]]),(4,[10,1,10,1],[[1,2,2],[2,3,2],[3,4,2]])]],WATER,[WATER.replace('[(cost,0,i+1)','[(cost,1,i+1)'),WATER.replace('if a!=b','if a==b')],['Connects wells to house one instead of the virtual source.','Adds only cycle edges rather than component-joining edges.'],water_oracle,random_water,['Model building a well as an edge from virtual node zero to that house.','Combine virtual well edges with pipe edges.','Run Kruskal’s algorithm with union-find over nodes zero through n.','Every valid supply plan is a spanning tree of this augmented graph, so its MST is the minimum cost.'],'O((n+pipes) log(n+pipes))','O(n)',8),
1169:E('invalid_transactions',[('transactions','list[str]')],'list[str]',['sorting','hash-maps'],['A transaction is invalid above 1000 or near a same-name different-city transaction.','Return invalid original strings in any order.'],[([['alice,20,800,mtv','alice,50,100,beijing']],'Both Alice transactions conflict within thirty minutes across cities.'),([['alice,20,1200,mtv','bob,50,100,beijing']],'Only the amount-1200 transaction is invalid.')],[[t] for t in [["a,0,1,x"],["a,0,1001,x"],["a,0,1000,x"],["a,0,1,x","a,60,1,y"],["a,0,1,x","a,61,1,y"],["a,0,1,x","b,10,1,y"],["a,0,1,x","a,10,1,x"],["a,10,500,x","a,50,500,y","a,100,500,z"],["bob,20,1200,a","bob,90,2,b"],["a,100,1,x","a,40,1,y"],["a,0,1001,x","a,100,1001,x"],["a,0,1,x","a,60,1,y","b,30,2000,z"],["lee,55,900,la","lee,5,900,mtv"],["x,0,1,a","x,30,1,b","x,90,1,c"]]],INVALID,[INVALID.replace('<=60','<60'),INVALID.replace('city!=other_city','city==other_city')],['Treats exactly sixty minutes apart as valid.','Flags same-city pairs instead of different-city pairs.'],invalid_oracle,random_transactions,['Parse each transaction into name, time, amount, and city while retaining its original string.','An amount above 1000 immediately marks it invalid.','Otherwise compare it with other entries for equal name, different city, and time difference at most sixty.','The pairwise predicate exactly covers both invalidity rules and preserves duplicates by index.'],'O(n^2)','O(n)',5),
1170:E('smallest_character_frequency_counts',[('queries','list[str]'),('words','list[str]')],'list[int]',['binary-search','sorting'],['All strings are nonempty.','For each query count words with strictly greater smallest-character frequency.'],[([['cbd'],['zaaaz']],'The smallest character occurs once in cbd and three times in zaaaz.'),([['bbb','cc'],['a','aa','aaa','aaaa']],'Frequencies three and two produce answer one and two respectively.')],[[q,w] for q,w in [(['a'],['b']),(['aa'],['b']),(['b'],['aa']),(['abc'],['ddd']),(['zz'],['a','bb','ccc']),(['a','bb'],['ccc']),(['abcd'],['a','aa','aaa']),(['aaaa'],['b','cc']),(['cbd'],['zaaaz']),(['x','yy','zzz'],['a','bb','ccc','dddd']),(['aba'],['aa','bbb']),(['mno'],['ppp','qq']),(['z'],['z']),(['aaa','b'],['cc','ddd','eeee'])]],FREQ,[FREQ.replace('bisect_right','bisect_left'),FREQ.replace('len(values)-','len(values)+')],['Counts words with equal frequency as if strictly greater.','Adds the insertion index instead of subtracting it from the word count.'],frequency_oracle,random_frequency,['Compute each string’s smallest character and count its occurrences.','Sort all word frequencies once.','For a query, binary-search the first word frequency strictly greater than its frequency.','Every suffix value after bisect_right is strictly larger, so its length is the requested count.'],'O(total characters + words log words + queries log words)','O(words)',5),
}
BATCH[1161]['params'][0]=('root','TreeNode | None','treenode')
BATCH[1169]['comparator']='unordered'
