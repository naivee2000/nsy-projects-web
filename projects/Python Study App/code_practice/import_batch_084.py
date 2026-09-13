"""Reviewed matrix, game-DP, tree, search, and string imports (batch 84a)."""
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations

from .import_batch_055 import entry
from .import_batch_082 import make_tree


def border_oracle(a):
 g=a[0];rows=len(g);cols=len(g[0]);best=0
 for r in range(rows):
  for c in range(cols):
   for side in range(1,min(rows-r,cols-c)+1):
    if all(g[r][j] and g[r+side-1][j] for j in range(c,c+side)) and all(g[i][c] and g[i][c+side-1] for i in range(r,r+side)):best=max(best,side*side)
 return best
def stones_oracle(a):
 piles=a[0];suffix=[0]*(len(piles)+1)
 for i in range(len(piles)-1,-1,-1):suffix[i]=suffix[i+1]+piles[i]
 @lru_cache(None)
 def play(i,m):return suffix[i] if i+2*m>=len(piles) else suffix[i]-min(play(i+x,max(m,x)) for x in range(1,2*m+1))
 return play(0,1)
def zigzag_oracle(a):
 nums=a[0]
 def cost(parity):return sum(max(0,nums[i]-min(nums[i-1] if i else 10**10,nums[i+1] if i+1<len(nums) else 10**10)+1) for i in range(parity,len(nums),2))
 return min(cost(0),cost(1))
def coloring_oracle(a):
 root=make_tree(a[0]);n,x=a[1:];parts=[]
 def size(node):
  if not node:return 0
  left=size(node[1]);right=size(node[2])
  if node[0]==x:parts.extend((left,right))
  return left+right+1
 size(root);parts.append(n-1-sum(parts));return max(parts)>n//2
def chunks_oracle(a):
 text=a[0]
 @lru_cache(None)
 def solve(left,right):
  if left>=right:return 0
  best=1
  for width in range(1,(right-left)//2+1):
   if text[left:left+width]==text[right-width:right]:best=max(best,2+solve(left+width,right-width))
  return best
 return solve(0,len(text))
def majority_oracle(a):return a[0].count(a[1])>len(a[0])//2
def swaps_oracle(a):
 data=a[0];ones=sum(data)
 return 0 if ones<2 else ones-max(sum(data[i:i+ones]) for i in range(len(data)-ones+1))
def pattern_oracle(a):
 users,times,sites=a;visits=defaultdict(list)
 for time,user,site in sorted(zip(times,users,sites)):visits[user].append(site)
 scores=Counter()
 for seq in visits.values():scores.update(set(combinations(seq,3)))
 return list(min(scores,key=lambda p:(-scores[p],p)))
def transform_oracle(a):
 first,second=a
 if first==second:return True
 mapping={}
 for x,y in zip(first,second):
  if x in mapping and mapping[x]!=y:return False
  mapping[x]=y
 return len(set(second))<26
def day_oracle(a):
 year,month,day=map(int,a[0].split('-'));days=[31,28+(year%400==0 or year%4==0 and year%100!=0),31,30,31,30,31,31,30,31,30,31]
 return sum(days[:month-1])+day

def random_grid(r):
 rows,cols=r.randint(1,6),r.randint(1,6);return [[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)]]
def random_piles(r):return [[r.randint(1,20) for _ in range(r.randint(1,9))]]
def random_nums(r):return [[r.randint(1,20) for _ in range(r.randint(1,14))]]
def random_color(r):
 n=r.randint(1,15);return [list(range(1,n+1)),n,r.randint(1,n)]
def random_text(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,14)))]
def random_majority(r):
 nums=sorted(r.randint(0,6) for _ in range(r.randint(1,20)));return [nums,r.randint(0,6)]
def random_bits(r):return [[r.randint(0,1) for _ in range(r.randint(1,20))]]
def random_pattern(r):
 users=[];times=[];sites=[];t=0
 for u in range(r.randint(1,4)):
  for _ in range(r.randint(3,6)):t+=1;users.append(chr(97+u));times.append(t);sites.append(r.choice(['a','b','c','d']))
 return [users,times,sites]
def random_transform(r):
 n=r.randint(1,20);return [''.join(r.choice('abcde') for _ in range(n)),''.join(r.choice('abcde') for _ in range(n))]
def random_date2(r):
 y=r.randint(1900,2200);m=r.randint(1,12);days=[31,28+(y%400==0 or y%4==0 and y%100!=0),31,30,31,30,31,31,30,31,30,31];d=r.randint(1,days[m-1]);return [f'{y:04d}-{m:02d}-{d:02d}']

BORDER='''def largest_one_bordered_square(grid):
 rows=len(grid);cols=len(grid[0]);left=[[0]*cols for _ in grid];up=[[0]*cols for _ in grid];best=0
 for r in range(rows):
  for c in range(cols):
   if grid[r][c]:
    left[r][c]=1+(left[r][c-1] if c else 0);up[r][c]=1+(up[r-1][c] if r else 0);side=min(left[r][c],up[r][c])
    while side*side>best:
     if up[r][c-side+1]>=side and left[r-side+1][c]>=side:best=side*side;break
     side-=1
 return best
'''
STONES='''def stone_game_two(piles):
 from functools import lru_cache
 suffix=[0]*(len(piles)+1)
 for i in range(len(piles)-1,-1,-1):suffix[i]=suffix[i+1]+piles[i]
 @lru_cache(None)
 def play(i,m):
  if i+2*m>=len(piles):return suffix[i]
  return suffix[i]-min(play(i+x,max(m,x)) for x in range(1,2*m+1))
 return play(0,1)
'''
ZIG='''def minimum_zigzag_decrements(nums):
 def cost(start):
  total=0
  for i in range(start,len(nums),2):total+=max(0,nums[i]-min(nums[i-1] if i else float('inf'),nums[i+1] if i+1<len(nums) else float('inf'))+1)
  return total
 return min(cost(0),cost(1))
'''
COLOR='''def can_second_player_win(root, n, x):
 parts=[]
 def size(node):
  if node is None:return 0
  left=size(node.left);right=size(node.right)
  if node.val==x:parts.extend((left,right))
  return left+right+1
 size(root);parts.append(n-1-sum(parts));return max(parts)>n//2
'''
CHUNKS='''def longest_chunked_decomposition(text):
 def split(value):
  if not value:return 0
  for width in range(1,len(value)//2+1):
   if value[:width]==value[-width:]:return 2+split(value[width:-width])
  return 1
 return split(text)
'''
MAJ='''def is_sorted_majority(nums, target):
 from bisect import bisect_left,bisect_right
 return bisect_right(nums,target)-bisect_left(nums,target)>len(nums)//2
'''
SWAPS='''def minimum_swaps_group_ones(data):
 width=sum(data)
 if width<2:return 0
 inside=sum(data[:width]);best=inside
 for i in range(width,len(data)):inside+=data[i]-data[i-width];best=max(best,inside)
 return width-best
'''
PATTERN='''def most_visited_three_pattern(username, timestamp, website):
 from collections import defaultdict,Counter
 from itertools import combinations
 visits=defaultdict(list)
 for time,user,site in sorted(zip(timestamp,username,website)):visits[user].append(site)
 scores=Counter()
 for sequence in visits.values():scores.update(set(combinations(sequence,3)))
 return list(min(scores,key=lambda pattern:(-scores[pattern],pattern)))
'''
TRANSFORM='''def can_transform_string(str1, str2):
 if str1==str2:return True
 mapping={}
 for source,target in zip(str1,str2):
  if source in mapping and mapping[source]!=target:return False
  mapping[source]=target
 return len(set(str2))<26
'''
DAY='''def ordinal_day(date):
 year,month,day=map(int,date.split('-'));days=[31,28+(year%400==0 or year%4==0 and year%100!=0),31,30,31,30,31,31,30,31,30,31]
 return sum(days[:month-1])+day
'''

G=[[[1]],[[0]],[[1,1]],[[1],[1]],[[1,1],[1,1]],[[1,0],[1,1]],[[0,0],[0,0]],[[1,1,1],[1,0,1],[1,1,1]],[[1,1,0],[1,1,0],[0,0,0]],[[1,1,1,1],[1,0,0,1],[1,0,0,1],[1,1,1,1]],[[0,1,0],[1,1,1],[0,1,0]],[[1,0,1],[0,1,0],[1,0,1]],[[1,1,1],[1,1,1]],[[0,1],[1,0]]]
P=[[1],[1,2],[2,7,9,4,4],[1,1,1,1],[10,1,1],[1,2,3,4,5],[5,4,3,2,1],[3,9,1,2],[8,8,8],[1,10,3,2],[2,2,2,9,1],[20,1,2,3,4,5],[4,7,2,9,5,2],[6,1,8,3,2]]
N=[[1],[1,2],[2,1],[1,2,3],[9,6,1,6,2],[2,2,2],[3,1,3],[1,3,2,4],[10,1,10,1],[5,4,3,2,1],[1,5,1,5,1],[8,2,6,4],[4,9,7,3,8],[2,7,1,8,2]]

E=entry
BATCH={
1139:E('largest_one_bordered_square',[('grid','list[list[int]]')],'int',['matrix','dynamic-programming'],['grid is nonempty and binary.','Return the area, not side length.'],[([[[1,1,1],[1,0,1],[1,1,1]]],'The outer border is all ones, so the area is nine.'),([[[1,1],[1,1]]],'All four cells form a bordered square of area four.')],[[g] for g in G if g not in G[4:5]+G[7:8]]+[[[[1,1],[0,1]]]],BORDER,[BORDER.replace('return best','return int(best**.5)',1),BORDER.replace('up[r][c-side+1]>=side','up[r][c]>=side')],['Returns side length instead of area.','Checks the right border twice and can ignore a missing left border.'],border_oracle,random_grid,['Precompute consecutive ones ending at every cell from the left and above.','Treat each one as a possible bottom-right corner.','Try side lengths bounded by its left/up runs and verify the opposite top and left borders.','Every candidate border is checked in constant time after the DP preprocessing.'],'O(rows*cols*min(rows,cols))','O(rows*cols)',5),
1140:E('stone_game_two',[('piles','list[int]')],'int',['dynamic-programming','game-theory'],['Both players play optimally.','M begins at one and becomes max(M,X).'],[([[2,7,9,4,4]],'Optimal counterplay limits Alice to ten stones.'),([[1]],'Alice takes the only pile.')],[[p] for p in P if p not in P[:1]+P[2:3]],STONES,[STONES.replace('max(m,x)','m'),STONES.replace('min(play','max(play')],['Never expands M after taking more piles.','Subtracts the opponent’s largest rather than smallest achievable result.'],stones_oracle,random_piles,['Use the suffix sum as all stones still available.','A state is the starting index and current M.','Alice’s best total is remaining stones minus the minimum total the next player can force over each legal X.','Memoization evaluates every reachable game state under optimal play.'],'O(n^3)','O(n^2)',8),
1144:E('minimum_zigzag_decrements',[('nums','list[int]')],'int',['greedy','arrays'],['Only decrements are allowed.','Either all even or all odd indices must be strict valleys.'],[([[1,2,3]],'Lowering the middle below both neighbors costs two moves.'),([[9,6,1,6,2]],'Making even indices valleys costs four moves, the minimum orientation.')],[[n] for n in N if n not in N[3:5]],ZIG,[ZIG.replace('return min(cost(0),cost(1))','return cost(0)'),ZIG.replace('+1)',')')],['Checks only the even-valley orientation.','Allows equality with a neighbor instead of strict inequality.'],zigzag_oracle,random_nums,['Evaluate the two possible valley parities independently.','A valley only needs to be lowered below its smaller neighbor.','Its required decrement is max(0,value-min(neighbors)+1).','Valleys of one parity are never adjacent, so their optimal decrements add independently.'],'O(n)','O(1)',5),
1145:E('can_second_player_win',[('root','TreeNode'),('n','int'),('x','int')],'bool',['trees','recursion'],['Tree values are unique and x is the first player’s node.','The second player chooses one node before expansion begins.'],[([[1,2,3,4,5,6,7,8,9,10,11],11,3],'The component above node three has more than half the nodes.'),([[1],1,1],'No uncolored node remains for the second player.')],[[list(range(1,n+1)),n,x] for n,x in [(2,1),(3,1),(3,2),(4,1),(5,2),(6,3),(7,1),(7,2),(8,4),(9,3),(10,5),(11,1),(12,6),(15,7)]],COLOR,[COLOR.replace('max(parts)>n//2','max(parts)>=n//2'),COLOR.replace('parts.append(n-1-sum(parts))','parts.append(n-sum(parts))')],['Treats a tied half as a winning majority.','Counts the red node inside the parent-side component.'],coloring_oracle,random_color,['Removing the red node separates the tree into left, right, and parent-side regions.','The second player can lock one entire region by choosing its adjacent node.','Compute the two child subtree sizes; the third size is n-1-left-right.','A forced win exists exactly when one region contains more than half of all nodes.'],'O(n)','O(height)',5),
1147:E('longest_chunked_decomposition',[('text','str')],'int',['strings','greedy'],['Every chunk is nonempty.','Mirrored chunks must be equal; maximize their count.'],[(['ghiabcdefhelloadamhelloabcdefghi'],'The symmetric pieces split into seven chunks.'),(['merchant'],'No matching outer pieces exist, so the whole text is one chunk.')],[[s] for s in ['a','aa','aaa','aaaa','abc','volvo','antaprezatepzapreanta','merchant','ghiabcdefhelloadamhelloabcdefghi','abab','abcabc','elvtoelvto','aaaabaaaa','leetcode']],CHUNKS,[CHUNKS.replace('return 2+split(value[width:-width])','return 1+split(value[width:-width])'),CHUNKS.replace('range(1,len(value)//2+1)','range(1,2)')],['Counts each matching outer pair as only one chunk.','Checks only single-character outer matches and misses longer equal chunks.'],chunks_oracle,random_text,['Grow equal-length pieces inward from both ends.','Whenever the accumulated prefix and suffix match, commit them immediately.','Count two chunks unless both pieces are the same central character, then reset accumulators.','Choosing the earliest outer match cannot reduce future chunks and maximizes the remaining interior.'],'O(n^2)','O(n)',8),
1150:E('is_sorted_majority',[('nums','list[int]'),('target','int')],'bool',['binary-search','arrays'],['nums is sorted.','A majority occurs strictly more than n/2 times.'],[([[2,4,5,5,5,5,5,6,6],5],'Five occupies five of nine positions, so it is a majority.'),([[10,100,101,101],101],'Two of four is not strictly more than half.')],[[n,t] for n,t in [([1],1),([1],2),([1,1],1),([1,2],1),([1,2,2],2),([2,2,3,3],2),([0,0,0,1],0),([1,2,3,4],3),([5,5,5,5],5),([1,1,2,2,2],2),([2,4,5,5,5,5,5,6,6],4),([1,2,2,2,3,4],2),([7,8,9],6),([3,3,3,4,4],4)]],MAJ,[MAJ.replace('>len(nums)//2','>=len(nums)//2'),MAJ.replace('bisect_right','bisect_left')],['Accepts exactly half as a majority.','Uses the left boundary for both ends, always counting zero.'],majority_oracle,random_majority,['Sorted duplicates occupy one contiguous interval.','Binary search for the first and first-after-target positions.','Their difference is the frequency; compare it strictly with n//2.','The two boundaries count exactly every target occurrence in logarithmic time.'],'O(log n)','O(1)',3),
1151:E('minimum_swaps_group_ones',[('data','list[int]')],'int',['sliding-window','arrays'],['data is binary.','Any two positions may be swapped.'],[([[1,0,1,0,1]],'A length-three window contains two ones, requiring one swap.'),([[0,0,0,1,0]],'A single one is already grouped.')],[[x] for x in [[0],[1],[1,1],[1,0],[0,1,0],[1,0,1],[0,1,1,0],[1,1,0,0,1],[0,0,0],[1,0,0,1,0,1],[1,1,1,0],[0,1,0,1,0,1,0],[1,0,1,1,0,0],[0,0,1,1,0]]],SWAPS,[SWAPS.replace('best=max(best,inside)','best=min(best,inside)'),SWAPS.replace('return width-best','return best')],['Tracks the sparsest rather than densest window.','Returns ones already inside instead of zeros needing swaps.'],swaps_oracle,random_bits,['The final block width must equal the total number of ones.','A window needs one swap for each zero inside it.','Find the maximum ones in any window of that fixed width.','Choosing the densest window minimizes width-inside swaps, and each outside one fills one inside zero.'],'O(n)','O(1)',5),
1152:E('most_visited_three_pattern',[('username','list[str]'),('timestamp','list[int]'),('website','list[str]')],'list[str]',['sorting','hash-maps'],['Each user contributes at most once to a pattern score.','Break score ties lexicographically.'],[([['joe','joe','joe','james','james','james','james','mary','mary','mary'],[1,2,3,4,5,6,7,8,9,10],['home','about','career','home','cart','maps','home','home','about','career']],'Home,about,career is used by two users and has the highest score.'),([['u','u','u'],[3,1,2],['c','a','b']],'Time sorting yields the sole pattern a,b,c.')],[[u,t,s] for u,t,s in [(['a','a','a'],[1,2,3],['x','y','z']),(['a','a','a','a'],[1,2,3,4],['a','b','c','d']),(['a','a','a','b','b','b'],[1,2,3,4,5,6],['x','y','z','x','y','z']),(['a','a','a','b','b','b'],[1,2,3,4,5,6],['a','b','d','a','b','c']),(['a','a','a'],[3,2,1],['c','b','a']),(['a','a','a','a'],[1,2,3,4],['x','x','x','x']),(['a','a','a','b','b','b'],[1,3,5,2,4,6],['x','z','y','x','z','y']),(['u','u','u','u'],[4,3,2,1],['d','c','b','a']),(['a','a','a','b','b','b','c','c','c'],list(range(9)),['x','y','z']*3),(['a','a','a','a'],[1,2,3,4],['b','a','b','a']),(['a','a','a','b','b','b'],[1,2,3,1,2,3],['m','n','o','m','n','p']),(['x','x','x'],[10,20,30],['one','two','three'])]],PATTERN,[PATTERN.replace('sorted(zip(timestamp,username,website))','zip(timestamp,username,website)'),PATTERN.replace('(-scores[pattern],pattern)','(-scores[pattern],tuple(reversed(pattern)))')],['Uses input order instead of chronological visit order.','Breaks score ties using reversed lexical order.'],pattern_oracle,random_pattern,['Sort all visits by timestamp and group website histories by user.','Generate each user’s ordered three-website subsequences as a set.','Count users per pattern, then minimize (-score,pattern).','Per-user deduplication implements the score definition and tuple ordering resolves ties.'],'O(visits log visits + users*visits^3)','O(patterns)',5),
1153:E('can_transform_string',[('str1','str'),('str2','str')],'bool',['graphs','hash-maps'],['Strings have equal length and lowercase letters.','One operation replaces every occurrence of one character.'],[(['aabcc','ccdee'],'Mappings a→c,b→d,c→e are consistent and a spare letter breaks cycles.'),(['leetcode','codeleet'],'One source character would need conflicting destinations.')],[[a,b] for a,b in [('a','a'),('a','b'),('aa','ab'),('ab','ba'),('abc','bcd'),('abc','abc'),('abab','bcbc'),('abc','ddd'),('aaa','bbb'),('abcdefghijklmnopqrstuvwxyz','bcdefghijklmnopqrstuvwxyza'),('abcdefghijklmnopqrstuvwxyz','abcdefghijklmnopqrstuvwxyz'),('abca','zbcz'),('paper','title'),('foo','bar')]],TRANSFORM,[TRANSFORM.replace("if str1==str2:return True","if str1==str2:return False"),TRANSFORM.replace("return len(set(str2))<26","return True")],['Rejects already-equal strings.','Ignores the lack of a spare character needed to break a full-alphabet cycle.'],transform_oracle,random_transform,['Each source character must always map to the same destination character.','If strings already match, no operation is needed.','Otherwise a consistent mapping is possible only when the target leaves at least one of 26 letters unused.','A spare letter breaks mapping cycles; inconsistency or a full target alphabet is the only obstruction.'],'O(n)','O(1)',8),
1154:E('ordinal_day',[('date','str')],'int',['math','strings'],['date is valid YYYY-MM-DD.','Use Gregorian leap-year rules.'],[(['2019-01-09'],'January ninth is day nine.'),(['2019-02-10'],'Thirty-one January days plus ten gives day forty-one.')],[[d] for d in ['2000-03-01','1900-03-01','2020-02-29','2019-12-31','2020-12-31','2021-01-01','2021-04-30','2021-05-01','2004-02-28','2004-03-01','2100-03-01','2400-12-31','1999-07-15','2022-11-30']],DAY,[DAY.replace('year%100!=0','year%100==0'),DAY.replace('sum(days[:month-1])','sum(days[:month])')],['Treats every century divisible by four as leap.','Includes the entire current month before adding the day.'],day_oracle,random_date2,['Parse year, month, and day from the fixed format.','Build month lengths with February adjusted by Gregorian divisibility.','Sum completed months and add the current day.','Each prior calendar day is counted once, including February 29 only in a valid leap year.'],'O(1)','O(1)',3),
}
BATCH[1145]['params'][0]=('root','TreeNode | None','treenode')
