"""Second half of batch 96: matrices, parsing, games, graphs, and rooted trees."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from .import_batch_055 import entry

MOD=1_000_000_007

def submat_o(a):
 mat=a[0];rows,cols=len(mat),len(mat[0]);answer=0
 for top in range(rows):
  for bottom in range(top,rows):
   run=0
   for col in range(cols):
    if all(mat[row][col] for row in range(top,bottom+1)):run+=1;answer+=run
    else:run=0
 return answer
def date_o(a):
 day,month,year=a[0].split();months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
 return f'{year}-{months.index(month)+1:02d}-{int(day[:-2]):02d}'
def ranges_o(a):
 nums,n,left,right=a;sums=sorted(sum(nums[i:j]) for i in range(n) for j in range(i+1,n+1))
 return sum(sums[left-1:right])%MOD
def moves_o(a):
 nums=a[0]
 if len(nums)<=4:return 0
 best=max(nums)-min(nums)
 for removed in combinations(range(len(nums)),3):
  keep=[v for i,v in enumerate(nums) if i not in removed];best=min(best,max(keep)-min(keep))
 return best
def stone_o(a):
 @lru_cache(None)
 def win(n):return any(not win(n-square*square) for square in range(1,int(n**.5)+1))
 return win(a[0])
def good_o(a):
 nums=a[0];return sum(nums[i]==nums[j] for i in range(len(nums)) for j in range(i+1,len(nums)))
def ones_o(a):
 s=a[0];return sum(all(char=='1' for char in s[i:j]) for i in range(len(s)) for j in range(i+1,len(s)+1))%MOD
def probability_o(a):
 n,edges,prob,start,end=a;best=[0.0]*n;best[start]=1.0
 for _ in range(n-1):
  changed=False
  for (x,y),p in zip(edges,prob):
   if best[y]*p>best[x]:best[x]=best[y]*p;changed=True
   if best[x]*p>best[y]:best[y]=best[x]*p;changed=True
  if not changed:break
 return best[end]
def bottles_o(a):
 full,rate=a;drunk=empty=0
 while full:
  drunk+=full;empty+=full;full,empty=divmod(empty,rate)
 return drunk
def labels_o(a):
 n,edges,labels=a;graph=[[] for _ in range(n)]
 for x,y in edges:graph[x].append(y);graph[y].append(x)
 parent=[-2]*n;parent[0]=-1;order=[0]
 for node in order:
  for child in graph[node]:
   if parent[child]==-2:parent[child]=node;order.append(child)
 return [sum(labels[node]==labels[target] and _descendant(target,node,parent) for target in range(n)) for node in range(n)]
def _descendant(node,root,parent):
 while node!=-1 and node!=root:node=parent[node]
 return node==root

def rsubmat(r):
 rows,cols=r.randint(1,5),r.randint(1,5);return [[[r.randint(0,1) for _ in range(cols)] for _ in range(rows)]]
def rdate(r):
 month=r.choice(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);day=r.randint(1,28);suffix='th' if 10<day%100<14 else {1:'st',2:'nd',3:'rd'}.get(day%10,'th')
 return [f'{day}{suffix} {month} {r.randint(1900,2100)}']
def rranges(r):
 n=r.randint(1,12);nums=[r.randint(1,30) for _ in range(n)];total=n*(n+1)//2;left=r.randint(1,total);return [nums,n,left,r.randint(left,total)]
def rmoves(r):return [[r.randint(-30,30) for _ in range(r.randint(1,9))]]
def rstone(r):return [r.randint(0,100)]
def rgood(r):return [[r.randint(0,8) for _ in range(r.randint(1,40))]]
def rones(r):return [''.join(r.choice('01') for _ in range(r.randint(1,50)))]
def rprob(r):
 n=r.randint(2,9);edges=[]
 for node in range(1,n):edges.append([r.randrange(node),node])
 for x in range(n):
  for y in range(x+1,n):
   if [x,y] not in edges and r.random()<.12:edges.append([x,y])
 return [n,edges,[r.random() for _ in edges],r.randrange(n),r.randrange(n)]
def rbottles(r):return [r.randint(1,1000),r.randint(2,20)]
def rlabels(r):
 n=r.randint(1,20);edges=[[r.randrange(node),node] for node in range(1,n)]
 return [n,edges,''.join(r.choice('abcde') for _ in range(n))]

SUBMAT='''def count_all_one_submatrices(mat):
 rows,cols=len(mat),len(mat[0]);heights=[0]*cols;answer=0
 for row in mat:
  for col,value in enumerate(row):heights[col]=heights[col]+1 if value else 0
  for right in range(cols):
   minimum=heights[right]
   for left in range(right,-1,-1):minimum=min(minimum,heights[left]);answer+=minimum
 return answer
'''
DATE='''def reformat_ordinal_date(date):
 day,month,year=date.split();months={name:index for index,name in enumerate(('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'),1)}
 return f"{year}-{months[month]:02d}-{int(day[:-2]):02d}"
'''
RANGES='''def sorted_subarray_range_sum(nums, n, left, right):
 values=[]
 for start in range(n):
  total=0
  for end in range(start,n):total+=nums[end];values.append(total)
 values.sort()
 return sum(values[left-1:right])%1000000007
'''
MOVES='''def minimum_range_after_three_moves(nums):
 if len(nums)<=4:return 0
 nums=sorted(nums)
 return min(nums[-4]-nums[0],nums[-3]-nums[1],nums[-2]-nums[2],nums[-1]-nums[3])
'''
STONE='''def wins_square_stone_game(n):
 winning=[False]*(n+1)
 for stones in range(1,n+1):
  winning[stones]=any(not winning[stones-square*square] for square in range(1,int(stones**0.5)+1))
 return winning[n]
'''
GOOD='''def count_good_pairs(nums):
 from collections import Counter
 return sum(count*(count-1)//2 for count in Counter(nums).values())
'''
ONES='''def count_one_only_substrings(s):
 answer=run=0
 for char in s:
  run=run+1 if char=='1' else 0;answer=(answer+run)%1000000007
 return answer
'''
PROB='''def maximum_path_probability(n, edges, succ_prob, start, end):
 import heapq
 graph=[[] for _ in range(n)]
 for (x,y),probability in zip(edges,succ_prob):graph[x].append((y,probability));graph[y].append((x,probability))
 best=[0.0]*n;best[start]=1.0;heap=[(-1.0,start)]
 while heap:
  probability,node=heapq.heappop(heap);probability=-probability
  if node==end:return probability
  if probability<best[node]:continue
  for neighbor,edge_probability in graph[node]:
   candidate=probability*edge_probability
   if candidate>best[neighbor]:best[neighbor]=candidate;heapq.heappush(heap,(-candidate,neighbor))
 return 0.0
'''
BOTTLES='''def maximum_drank_bottles(num_bottles, num_exchange):
 answer=empty=0
 while num_bottles:
  answer+=num_bottles;empty+=num_bottles
  num_bottles,empty=divmod(empty,num_exchange)
 return answer
'''
LABELS='''def subtree_label_counts(n, edges, labels):
 graph=[[] for _ in range(n)]
 for x,y in edges:graph[x].append(y);graph[y].append(x)
 answer=[0]*n
 def visit(node,parent):
  counts=[0]*26
  for child in graph[node]:
   if child!=parent:
    child_counts=visit(child,node)
    for index in range(26):counts[index]+=child_counts[index]
  label=ord(labels[node])-97;counts[label]+=1;answer[node]=counts[label]
  return counts
 visit(0,-1)
 return answer
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1504:S('count_all_one_submatrices',[('mat','list[list[int]]')],'int',['matrices','dynamic-programming'],['mat is a non-empty binary matrix.','Count every rectangular submatrix containing only ones.'],[([[[1,0,1],[1,1,0],[1,1,0]]],'There are six single cells, five vertical or horizontal rectangles, and two larger rectangles, for thirteen.'),([[[1,1],[1,1]]],'Four cells, two rows, two columns, and the whole matrix give nine rectangles.')],[[m] for m in [[[1]],[[0]],[[1,1],[1,1]],[[1,0,1],[1,1,0],[1,1,0]],[[1,0],[0,1]],[[1,1,1]],[[1],[1],[1]],[[0,0],[0,0]],[[1,1,0],[1,1,1]],[[1,0,1],[1,0,1]],[[1,1,1],[0,1,0]],[[1,1,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]],[[1,0,0],[1,1,0],[1,1,1]]]],SUBMAT,[SUBMAT.replace('answer+=minimum','answer+=minimum>0'),SUBMAT.replace('minimum=min(minimum,heights[left])','minimum=heights[left]')],['Counts only one rectangle per positive-width ending instead of every possible height.','Forgets the minimum height across the full column interval.'],submat_o,rsubmat,['Convert each row into histogram heights of consecutive ones.','For every right boundary, extend left while tracking the minimum height.','That minimum is the number of all-one rectangles with this bottom and horizontal span.','Every rectangle has one bottom row and pair of horizontal boundaries, so it is counted exactly once.'],'O(rows*cols²)','O(cols)',8),
1507:S('reformat_ordinal_date',[('date','str')],'str',['strings','parsing'],['Input is day-with-suffix, three-letter month, and four-digit year.','Return the zero-padded ISO form YYYY-MM-DD.'],[(['20th Oct 2052'],'October is month ten and the ordinal suffix is removed, producing 2052-10-20.'),(['6th Jun 1933'],'Both month and day are padded to two digits, producing 1933-06-06.')],[[s] for s in ['1st Jan 1900','2nd Feb 2000','3rd Mar 2020','4th Apr 2021','20th Oct 2052','6th Jun 1933','11th Nov 2011','12th Dec 2012','21st May 1999','22nd Aug 1988','23rd Sep 1977','31st Jul 2100','10th Jan 2001','28th Feb 2024']],DATE,[DATE.replace('{months[month]:02d}-{int(day[:-2]):02d}','{int(day[:-2]):02d}-{months[month]:02d}'),DATE.replace('enumerate((\'Jan\'','enumerate((\'Feb\',\'Jan\'')],['Swaps the month and day fields in the output.','Assigns January the wrong month number.'],date_o,rdate,['Split the three space-separated fields.','Remove the final two ordinal-suffix characters from the day.','Map the month abbreviation to a number from one through twelve.','Format year, month, and day with two-digit padding.'],'O(1)','O(1)',3),
1508:S('sorted_subarray_range_sum',[('nums','list[int]'),('n','int'),('left','int'),('right','int')],'int',['arrays','sorting'],['nums contains positive integers and n equals its length.','Sort all contiguous non-empty subarray sums and add ranks left through right, using one-based ranks.'],[([[1,2,3,4],4,1,5],'The five smallest sorted sums are 1,2,3,3,4 and total thirteen.'),([[1,2,3,4],4,3,4],'The third and fourth sums are both three, totaling six.')],[[a,n,l,r] for a,n,l,r in [([1],1,1,1),([1,2],2,1,3),([1,2,3,4],4,1,5),([1,2,3,4],4,3,4),([5,5],2,2,3),([3,1,2],3,1,6),([10,1],2,1,2),([2,2,2],3,2,5),([1,1,1,1],4,4,8),([4,3,2,1],4,6,10),([7],1,1,1),([1,3,1],3,2,4),([6,2,5],3,4,6),([9,8,7,6],4,1,10)]],RANGES,[RANGES.replace('for end in range(start,n):','for end in range(start+1,n):'),RANGES.replace('left-1:right','left:right+1')],['Omits every length-one subarray except the final index.','Treats one-based ranks as zero-based slice indices.'],ranges_o,rranges,['Generate each contiguous subarray sum using a running total per start index.','Sort the resulting n(n+1)/2 values.','Slice from left-1 through right and sum modulo the modulus.','Generation covers every contiguous interval once, and the adjusted slice matches the one-based inclusive ranks.'],'O(n² log n)','O(n²)',5),
1509:S('minimum_range_after_three_moves',[('nums','list[int]')],'int',['sorting','greedy'],['In one move, replace any one value with any other value; make at most three moves.','Minimize the difference between the final maximum and minimum.'],[([[5,3,2,4]],'All but one value can be changed to match, so four or fewer values always yield zero.'),([[1,5,0,10,14]],'Changing one, zero, and fourteen leaves values five and ten, whose range is five.')],[[x] for x in [[1],[1,2],[5,3,2,4],[1,5,0,10,14],[6,6,0,1,1,4,6],[1,2,3,4,5],[10,10,10,10,20],[-10,-5,0,5,10],[1,100,101,102,103],[1,2,100,101,102,103],[0,0,0,5,5,5],[9,1,8,2,7,3],[1,50,51,52,100],[4,8,15,16,23,42]]],MOVES,[MOVES.replace('if len(nums)<=4:return 0','if len(nums)<=5:return 0'),MOVES.replace('nums[-4]-nums[0],','')],['Incorrectly assumes three moves can always collapse a five-value range to zero.','Omits the case that changes the three largest values.'],moves_o,rmoves,['Only values at the sorted extremes ever need replacement.','Distribute three changes between the low and high ends in four possible ways.','Compute the remaining range for 3/0, 2/1, 1/2, and 0/3 removals.','Replacing removed extremes inside the surviving range realizes each case; changing an interior value cannot improve either boundary.'],'O(n log n)','O(n)',5),
1510:S('wins_square_stone_game',[('n','int')],'bool',['dynamic-programming','game-theory'],['Players alternate removing a positive square number of stones.','Return whether the first player has a winning strategy under optimal play.'],[([1],'Remove one square stone and win immediately.'),([2],'Any move leaves one stone, which the opponent removes to win.')],[[n] for n in [0,1,2,3,4,5,7,10,12,15,16,17,18,23]],STONE,[STONE.replace('not winning[stones-square*square]','winning[stones-square*square]'),STONE.replace('winning=[False]*(n+1)','winning=[True]*(n+1)')],['Moves only to positions already known to be winning for the opponent.','Incorrectly marks the zero-stone base state as winning.'],stone_o,rstone,['A position is winning if any legal move leaves a losing position.','Build results from zero stones upward.','Try every square not exceeding the current pile.','All moves lead to smaller already-computed states, so the recurrence exactly represents optimal play.'],'O(n*sqrt(n))','O(n)',5),
1512:S('count_good_pairs',[('nums','list[int]')],'int',['arrays','counting'],['A good pair has indices i<j and equal values.','Return the total number of good pairs.'],[([[1,2,3,1,1,3]],'Value one contributes three pairs and value three contributes one, totaling four.'),([[1,1,1,1]],'Four equal occurrences choose two indices in six ways.')],[[x] for x in [[1],[1,2],[1,1],[1,2,3,1,1,3],[1,1,1,1],[1,2,3],[0,0,1,1],[-1,-1,-1],[5,5,6,5],[1,2,1,2,1,2],[9,8,7,9],[0,0,0,0,0],[2,3,2,4,3,2],[10,10,20,20,20]]],GOOD,[GOOD.replace('count*(count-1)//2','count-1'),GOOD.replace('//2','')],['Counts only one fewer than each frequency, missing combinations among larger groups.','Counts ordered equal pairs twice.'],good_o,rgood,['Count how often each value occurs.','A value appearing c times contributes c choose 2 pairs.','Sum c(c-1)/2 across values.','Each good pair belongs to exactly one value bucket and every two indices in that bucket form one pair.'],'O(n)','O(n)',3),
1513:S('count_one_only_substrings',[('s','str')],'int',['strings','dynamic-programming'],['s is a non-empty binary string.','Count substrings containing only ones and return modulo 1,000,000,007.'],[(['0110111'],'Runs of lengths two and three contribute three plus six, for nine.'),(['101'],'Each isolated one contributes one, for two total.')],[[s] for s in ['0','1','00','11','0110111','101','1111','1000','0001','110011','010101','111011','0011100','10111101']],ONES,[ONES.replace('answer+run','answer+1'),ONES.replace("else 0","else run")],['Adds only one per one character instead of the number of substrings ending there.','Fails to reset the run at a zero.'],ones_o,rones,['Track the current consecutive run of ones.','At each one, its run length equals the number of all-one substrings ending there.','Reset the run at zero and add each run value to the answer.','Every all-one substring is counted exactly at its final character.'],'O(n)','O(1)',3),
1514:S('maximum_path_probability',[('n','int'),('edges','list[list[int]]'),('succ_prob','list[float]'),('start','int'),('end','int')],'float',['graphs','shortest-path'],['Each undirected edge has an independent traversal success probability.','Return the maximum product probability from start to end, or zero if unreachable.'],[([3,[[0,1],[1,2],[0,2]],[0.5,0.5,0.2],0,2],'The path through node one has probability 0.25, exceeding the direct edge probability 0.2.'),([3,[[0,1]],[0.5],0,2],'Node two is unreachable, so the probability is zero.')],[[*x] for x in [(2,[[0,1]],[1.0],0,1),(3,[[0,1],[1,2],[0,2]],[0.5,0.5,0.2],0,2),(3,[[0,1]],[0.5],0,2),(1,[],[],0,0),(3,[[0,1],[1,2]],[0.0,0.9],0,2),(4,[[0,1],[1,3],[0,2],[2,3]],[0.5,0.5,0.8,0.2],0,3),(4,[[0,1],[1,2],[2,3]],[0.9,0.9,0.9],3,0),(3,[[0,1],[0,2]],[0.3,0.7],1,2),(5,[[0,1],[1,4],[0,2],[2,3],[3,4]],[0.9,0.1,0.5,0.9,0.9],0,4),(2,[],[],0,1),(3,[[0,1],[1,2]],[1.0,1.0],0,2),(4,[[0,1],[1,2],[2,0],[2,3]],[0.5,0.6,0.7,0.8],0,3),(3,[[0,1],[1,2],[0,2]],[0.1,0.1,0.02],0,2),(5,[[0,1],[1,2],[3,4]],[0.4,0.4,0.9],0,4)]],PROB,[PROB.replace('candidate=probability*edge_probability','candidate=probability*(1-edge_probability)'),PROB.replace('if node==end:return probability','if node==end:return probability/2')],['Uses failure probability rather than success probability on each edge.','Halves the probability when the destination is reached.'],probability_o,rprob,['Use a max-priority queue keyed by best probability reached so far.','Relax an edge by multiplying the current path probability by its edge probability.','Keep a neighbor only when the product improves its best known value.','Because multiplying by values at most one never increases a path probability, the first queue removal of a node is optimal, as in Dijkstra’s proof.'],'O((n+edges) log n)','O(n+edges)',8),
1518:S('maximum_drank_bottles',[('num_bottles','int'),('num_exchange','int')],'int',['simulation','math'],['Drink every full bottle; num_exchange empty bottles can be exchanged for one full bottle.','Return the maximum number of bottles that can be drunk.'],[([9,3],'Nine bottles produce nine empties, then three bottles, then one, for thirteen total.'),([15,4],'Exchanges produce three bottles, then one more using accumulated empties, for nineteen total.')],[[b,e] for b,e in [(1,2),(2,2),(9,3),(15,4),(5,5),(4,5),(10,2),(100,10),(20,3),(3,2),(8,4),(25,6),(50,7),(99,9)]],BOTTLES,[BOTTLES.replace('divmod(empty,num_exchange)','(empty//num_exchange,0)'),BOTTLES.replace('while num_bottles:','while num_bottles>=num_exchange:')],['Discards leftover empty bottles after each exchange.','Stops before drinking the final batch smaller than the exchange rate.'],bottles_o,rbottles,['Drink all currently full bottles and add them to the empty count.','Exchange as many empties as possible, retaining the remainder.','Repeat until no full bottles remain.','Each iteration performs every available exchange without losing empties, so no additional bottle can be obtained afterward.'],'O(log bottles)','O(1)',3),
1519:S('subtree_label_counts',[('n','int'),('edges','list[list[int]]'),('labels','str')],'list[int]',['trees','depth-first-search'],['The undirected edges form a tree rooted at node zero.','For each node, count nodes in its rooted subtree carrying the same label.'],[([7,[[0,1],[0,2],[1,4],[1,5],[2,3],[2,6]],'abaedcd'],'Node zero and descendant two share a; every other node has one matching label in its subtree.'),([4,[[0,1],[1,2],[0,3]],'bbbb'],'The subtree sizes are four, two, one, and one because every label is b.')],[[*x] for x in [(1,[],'a'),(2,[[0,1]],'aa'),(2,[[0,1]],'ab'),(7,[[0,1],[0,2],[1,4],[1,5],[2,3],[2,6]],'abaedcd'),(4,[[0,1],[1,2],[0,3]],'bbbb'),(4,[[0,1],[0,2],[0,3]],'abac'),(5,[[0,1],[1,2],[2,3],[3,4]],'abcaa'),(6,[[0,1],[0,2],[1,3],[1,4],[2,5]],'ababab'),(3,[[0,1],[1,2]],'aaa'),(5,[[0,1],[0,2],[2,3],[2,4]],'abcba'),(7,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]],'abacaba'),(6,[[0,1],[0,2],[0,3],[3,4],[3,5]],'cacaca'),(4,[[0,1],[1,2],[2,3]],'abca'),(8,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6],[6,7]],'aabbccaa')]],LABELS,[LABELS.replace('counts[label]+=1;answer[node]=counts[label]','counts[label]+=1;answer[node]=1'),LABELS.replace('if child!=parent:','if child==parent:')],['Returns one for every node instead of accumulated same-label descendants.','Recurses toward the parent rather than unvisited children.'],labels_o,rlabels,['Root the tree at zero with a DFS.','Return a 26-slot label-frequency array from each subtree.','Merge child arrays, add the current label, and record its resulting frequency.','Postorder aggregation includes every descendant exactly once and excludes everything outside the rooted subtree.'],'O(n*alphabet)','O(n*alphabet)',5),
}
BATCH[1514]['comparator']='float'
