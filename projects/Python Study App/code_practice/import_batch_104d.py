"""Final group of batch 104: runs, parametric search, graph trios, and strings."""
from itertools import combinations
from .import_batch_055 import entry
MOD=1_000_000_007
def homogeneous_o(a):
 s=a[0];return sum(len(set(s[i:j]))==1 for i in range(len(s)) for j in range(i+1,len(s)+1))%MOD
def bags_o(a):
 nums,operations=a
 for limit in range(1,max(nums)+1):
  if sum((value-1)//limit for value in nums)<=operations:return limit
def trio_o(a):
 n,edges=a;links={tuple(sorted(edge)) for edge in edges};degrees=[0]*(n+1)
 for x,y in links:degrees[x]+=1;degrees[y]+=1
 answer=10**9
 for x,y,z in combinations(range(1,n+1),3):
  if (x,y) in links and (x,z) in links and (y,z) in links:answer=min(answer,degrees[x]+degrees[y]+degrees[z]-6)
 return -1 if answer==10**9 else answer
def ocean_o(a):
 heights=a[0];return [i for i in range(len(heights)) if all(heights[i]>heights[j] for j in range(i+1,len(heights)))]
def nice_o(a):
 s=a[0];best=''
 for i in range(len(s)):
  for j in range(i+1,len(s)+1):
   part=s[i:j]
   if len(part)>len(best) and all(c.swapcase() in part for c in set(part)):best=part
 return best
def rhomogeneous(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,40)))]
def rbags(r):return [[r.randint(1,60) for _ in range(r.randint(1,12))],r.randint(0,30)]
def rtrio(r):
 n=r.randint(3,9);edges=[[i,j] for i in range(1,n+1) for j in range(i+1,n+1) if r.random()<.3];return [n,edges]
def rocean(r):return [r.sample(range(1,100),r.randint(1,20))]
def rnice(r):return [''.join(r.choice('abABcdCD') for _ in range(r.randint(1,14)))]
HOMOGENEOUS='''def homogeneous_substring_count(s):
 answer=run=0;previous=''
 for char in s:
  run=run+1 if char==previous else 1;answer+=run;previous=char
 return answer%1000000007
'''
BAGS='''def minimum_bag_penalty(nums, max_operations):
 low,high=1,max(nums)
 while low<high:
  middle=(low+high)//2
  if sum((value-1)//middle for value in nums)<=max_operations:high=middle
  else:low=middle+1
 return low
'''
TRIO='''def minimum_connected_trio_degree(n, edges):
 neighbors=[set() for _ in range(n+1)]
 for left,right in edges:neighbors[left].add(right);neighbors[right].add(left)
 answer=10**9
 for first in range(1,n+1):
  for second in neighbors[first]:
   if second<=first:continue
   for third in neighbors[first]&neighbors[second]:
    if third>second:answer=min(answer,len(neighbors[first])+len(neighbors[second])+len(neighbors[third])-6)
 return -1 if answer==10**9 else answer
'''
OCEAN='''def ocean_view_buildings(heights):
 answer=[];tallest=-1
 for index in range(len(heights)-1,-1,-1):
  if heights[index]>tallest:answer.append(index);tallest=heights[index]
 return answer[::-1]
'''
NICE='''def longest_nice_substring(s):
 if len(s)<2:return ''
 letters=set(s)
 for index,char in enumerate(s):
  if char.swapcase() not in letters:
   left=longest_nice_substring(s[:index]);right=longest_nice_substring(s[index+1:])
   return left if len(left)>=len(right) else right
 return s
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1759:E('homogeneous_substring_count',[('s','str')],'int',['strings','counting'],['A substring is homogeneous when every character in it is the same.','Count all nonempty homogeneous substrings by position, modulo 1,000,000,007.'],[(['abbcccaa'],'Run lengths one, two, three, and two contribute 1+3+6+3=13.'),(['xy'],'Each one-character substring is homogeneous, giving two.')],[[s] for s in ['abbcccaa','xy','a','aa','aaa','ab','aba','aabbaa','ccccd','abcde','zzzzzz','aabbaaa','ababab','aaabccccbb']],HOMOGENEOUS,[HOMOGENEOUS.replace('answer+=run','answer+=1'),HOMOGENEOUS.replace('char==previous','char!=previous')],['Counts only one substring per ending position and misses longer homogeneous suffixes.','Extends runs when the character changes instead of when it matches.'],homogeneous_o,rhomogeneous,L('A run of length r contributes r substrings ending at its newest character.','Track the current equal-character suffix length and add it at every position.','Reset run to one on a character change; otherwise increment it; reduce the total modulo M.','Every homogeneous substring is uniquely identified by its ending position and one of the current run-length starting points.'),'O(n)','O(1)',5),
1760:E('minimum_bag_penalty',[('nums','list[int]'),('max_operations','int')],'int',['binary-search','greedy'],['One operation splits a bag into two positive-sized bags.','Minimize the maximum balls in any bag using at most max_operations splits.'],[([[9],2],'Splitting nine into three bags of three uses two operations, so the minimum penalty is three.'),([[2,4,8,2],4],'Penalty two is achievable in four splits and penalty one is not.')],[[*x] for x in [([9],2),([2,4,8,2],4),([1],0),([10],0),([10],1),([10],9),([1,1,1],5),([3,6],2),([7,17],2),([100,1],3),([5,5,5],3),([2,3,5,7],4),([20,30],10),([8,8,8,8],7)]],BAGS,[BAGS.replace('(value-1)//middle','value//middle'),BAGS.replace('low=middle+1','low=middle')],['Overcounts splits when a bag size is exactly divisible by the proposed limit.','Fails to advance the lower bound after an infeasible midpoint and can loop forever.'],bags_o,rbags,L('For a proposed limit p, a bag of size x needs floor((x-1)/p) splits.','Feasibility is monotone, so binary-search the smallest feasible penalty.','Sum required splits at each midpoint; move high down when within budget, otherwise low to midpoint+1.','Larger limits never require more splits, and the formula is the minimum pieces needed to keep every part at most p.'),'O(n log max(nums))','O(1)',5),
1761:E('minimum_connected_trio_degree',[('n','int'),('edges','list[list[int]]')],'int',['graphs','sets'],['The undirected simple graph uses one-indexed nodes.','For every fully connected three-node trio, its degree is the number of edges from trio nodes to outside nodes; return the minimum or -1.'],[([6,[[1,2],[1,3],[3,2],[4,1],[5,2],[3,6]]],'Trio 1,2,3 has three external incident edges, so its degree is three.'),([7,[[1,3],[4,1],[4,3],[2,5],[5,6],[6,7],[7,5],[2,6]]],'The only connected trio 5,6,7 has two outside edges.')],[[*x] for x in [(3,[]),(3,[[1,2],[2,3],[1,3]]),(4,[[1,2],[2,3],[1,3],[1,4]]),(4,[[1,2],[2,3]]),(5,[[1,2],[2,3],[1,3],[3,4],[4,5]]),(6,[[1,2],[1,3],[3,2],[4,1],[5,2],[3,6]]),(7,[[1,3],[4,1],[4,3],[2,5],[5,6],[6,7],[7,5],[2,6]]),(4,[[1,2],[1,3],[2,3],[1,4],[2,4],[3,4]]),(5,[[1,2],[1,3],[2,3],[4,5]]),(6,[[1,2],[2,3],[1,3],[4,5],[5,6],[4,6]]),(5,[[1,2],[2,3],[1,3],[3,4],[3,5]]),(8,[[1,2],[2,3],[1,3],[3,8]]),(3,[[1,2]]),(5,[[1,2],[1,3],[2,3],[2,4],[2,5]])]],TRIO,[TRIO.replace('-6','-3'),TRIO.replace('third>second','third>=second')],['Subtracts only three internal edge incidences instead of six endpoint incidences.','Uses a non-strict ordering guard that can admit repeated enumeration logic incorrectly.'],trio_o,rtrio,L('A trio exists when two adjacent nodes share a third neighbor.','Store neighbor sets, intersect them for each ordered edge, and evaluate each trio once.','Its external degree is deg(a)+deg(b)+deg(c)-6 because three internal edges contribute two endpoints each.','Set intersection proves all three edges exist, and the ordering guards cover each unordered trio exactly once.'),'O(sum over edges of intersection cost)','O(n+edges)',8),
1762:E('ocean_view_buildings',[('heights','list[int]')],'list[int]',['arrays','monotonic-scan'],['Building heights are distinct; the ocean is to the right.','A building has a view only if every building to its right is shorter; return qualifying indices in increasing order.'],[([[4,2,3,1]],'Indices zero, two, and three are taller than everything to their right.'),([[4,3,2,1]],'Every building has an unobstructed ocean view.')],[[x] for x in [[4,2,3,1],[4,3,2,1],[1],[1,2],[2,1],[1,2,3,4],[5,1,4,2,3],[3,1,2],[10,9,1,8],[2,5,1,4,3],[7,2,6,1,5],[9,1,8,2,7,3],[1,3,2,5,4],[100,1,2,3]]],OCEAN,[OCEAN.replace('>tallest','<tallest'),OCEAN.replace('answer[::-1]','answer')],['Selects buildings shorter than the current right-side maximum.','Returns qualifying indices in decreasing scan order.'],ocean_o,rocean,L('Scanning from the ocean side maintains the tallest blocker seen so far.','A building qualifies exactly when its height exceeds that right-side maximum.','Scan right to left, append qualifying indices, update the maximum, then reverse the result.','The maintained maximum summarizes every building to the right, making the comparison both necessary and sufficient.'),'O(n)','O(n)',5),
1763:E('longest_nice_substring',[('s','str')],'str',['strings','divide-and-conquer','recursion'],['A substring is nice when every letter it contains appears in both lowercase and uppercase.','Return the longest nice substring; when lengths tie, return the earliest one.'],[(['YazaAay'],'aAa is the longest substring containing both cases of each included letter.'),(['Bb'],'The entire string is nice because both cases of b appear.')],[[s] for s in ['YazaAay','Bb','c','dDzeE','aA','abAB','abcABC','aAb','xXy','xYyX','AaBbC','zZaAqQ','abc','aAAa']],NICE,[NICE.replace("if len(s)<2:return ''","if len(s)<3:return ''"),NICE.replace('len(left)>=len(right)','len(left)>len(right)')],['Rejects valid two-character pairs such as Bb.','Chooses the later substring when equal-length nice candidates tie.'],nice_o,rnice,L('If a character lacks its opposite case in the current string, no nice substring can cross that character.','Split at the first offending character and solve both sides recursively.','Return the longer result, choosing the left result on equal lengths; if no character offends, return the whole string.','Every feasible substring lies wholly on one side of each offending character, so divide-and-conquer loses no candidate.'),'O(n^2)','O(n) recursion',3),
}
BATCH[1760]['wrong'][1]=BAGS.replace('return low','return low+1')
BATCH[1760]['wrong_reasons'][1]='Returns the value above the smallest feasible penalty through an off-by-one mistake.'
BATCH[1761]['wrong'][1]=TRIO.replace('if third>second:','if third>second and third<n:')
BATCH[1761]['wrong_reasons'][1]='Ignores every trio containing the highest-numbered graph node.'
