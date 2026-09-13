"""Reviewed tree, graph, greedy, union-find, prefix, and dynamic-programming imports."""
from collections import Counter, deque
from functools import lru_cache
from itertools import combinations

from .import_batch_055 import entry
from .import_batch_082 import make_tree, serial_tree

def forest_oracle(a):
 root=make_tree(a[0]);deleted=set(a[1]);forest=[]
 def visit(node,is_root):
  if not node:return None
  gone=node[0] in deleted
  if is_root and not gone:forest.append(node)
  node[1]=visit(node[1],gone);node[2]=visit(node[2],gone)
  return None if gone else node
 visit(root,True);return [serial_tree(x) for x in forest]
def split_oracle(a):
 depth=0;answer=[]
 for ch in a[0]:
  if ch=='(':answer.append(depth%2);depth+=1
  else:depth-=1;answer.append(depth%2)
 return answer
def days_oracle(a):
 year,month=a
 if month==2:return 29 if year%400==0 or year%4==0 and year%100 else 28
 return 30 if month in (4,6,9,11) else 31
def vowels_oracle(a):return ''.join(ch for ch in a[0] if ch not in 'aeiou')
def average_oracle(a):
 root=make_tree(a[0]);best=0
 def walk(node):
  nonlocal best
  if not node:return 0,0
  ls,lc=walk(node[1]);rs,rc=walk(node[2]);total=ls+rs+node[0];count=lc+rc+1;best=max(best,total/count);return total,count
 walk(root);return best
def divide_oracle(a):
 nums,k=a;n=len(nums);groups=n//k
 if groups==0:return False
 return max(Counter(nums).values())<=groups
def relative_oracle(a):
 x,order=a;rank={v:i for i,v in enumerate(order)};return sorted(x,key=lambda v:(0,rank[v]) if v in rank else (1,v))
def deepest_oracle(a):
 root=make_tree(a[0])
 def walk(node):
  if not node:return 0,None
  ld,ln=walk(node[1]);rd,rn=walk(node[2])
  return (ld+1,ln) if ld>rd else (rd+1,rn) if rd>ld else (ld+1,node)
 return serial_tree(walk(root)[1])
def interval_oracle(a):
 hours=a[0];best=0
 for i in range(len(hours)):
  score=0
  for j in range(i,len(hours)):
   score+=1 if hours[j]>8 else -1
   if score>0:best=max(best,j-i+1)
 return best
def team_oracle(a):
 skills,people=a;need=set(skills)
 for size in range(len(people)+1):
  for chosen in combinations(range(len(people)),size):
   if set().union(*(set(people[i]) for i in chosen),set())>=need:return list(chosen)
def dominoes_oracle(a):
 count=Counter(tuple(sorted(x)) for x in a[0]);return sum(v*(v-1)//2 for v in count.values())
def alternating_oracle(a):
 n,red,blue=a;adj=[[[],[]] for _ in range(n)]
 for x,y in red:adj[x][0].append(y)
 for x,y in blue:adj[x][1].append(y)
 dist=[[-1,-1] for _ in range(n)];q=deque([(0,0),(0,1)]);dist[0]=[0,0]
 while q:
  node,last=q.popleft();color=1-last
  for other in adj[node][color]:
   if dist[other][color]<0:dist[other][color]=dist[node][last]+1;q.append((other,color))
 return [min((x for x in row if x>=0),default=-1) for row in dist]
def leaf_tree_oracle(a):
 values=a[0]
 @lru_cache(None)
 def solve(i,j):
  if j-i<=1:return 0
  return min(solve(i,k)+solve(k,j)+max(values[i:k])*max(values[k:j]) for k in range(i+1,j))
 return solve(0,len(values))
def absolute_oracle(a):
 x,y=a;return max(abs(x[i]-x[j])+abs(y[i]-y[j])+abs(i-j) for i in range(len(x)) for j in range(len(x)))
def unique_oracle(a):
 c=Counter(a[0]);return max((x for x,n in c.items() if n==1),default=-1)
def armstrong_oracle(a):
 s=str(a[0]);return sum(int(ch)**len(s) for ch in s)==a[0]
def mst_oracle(a):
 n,edges=a;best=None
 for chosen in combinations(edges,n-1):
  parent=list(range(n+1))
  def find(x):
   while parent[x]!=x:x=parent[x]
   return x
  for x,y,_ in chosen:parent[find(x)]=find(y)
  if len({find(i) for i in range(1,n+1)})==1:
   total=sum(e[2] for e in chosen);best=total if best is None else min(best,total)
 return -1 if best is None else best
def courses_oracle(a):
 n,relations=a;done=set();terms=0
 while len(done)<n:
  ready=[course for course in range(1,n+1) if course not in done and all(y!=course or x in done for x,y in relations)]
  if not ready:return -1
  done.update(ready);terms+=1
 return terms
def trib_oracle(a):
 values=[0,1,1]
 for _ in range(3,a[0]+1):values.append(sum(values[-3:]))
 return values[a[0]]
def board_oracle(a):
 board=['abcde','fghij','klmno','pqrst','uvwxy','z'];positions={ch:(r,c) for r,row in enumerate(board) for c,ch in enumerate(row)};current=(0,0);out=''
 for ch in a[0]:
  target=positions[ch]
  while current[0]>target[0]:out+='U';current=(current[0]-1,current[1])
  while current[1]>target[1]:out+='L';current=(current[0],current[1]-1)
  while current[0]<target[0]:out+='D';current=(current[0]+1,current[1])
  while current[1]<target[1]:out+='R';current=(current[0],current[1]+1)
  out+='!'
 return out

def random_tree(r):return [[r.randint(0,50) for _ in range(r.randint(1,15))]]
def random_forest(r):
 tree=list(range(1,r.randint(1,15)+1));return [tree,r.sample(tree,r.randint(0,len(tree)))]
def random_parens(r):
 def make(d=0):return '()' if d>3 or r.random()<.4 else '('+make(d+1)+')'+(make(d) if r.random()<.4 else '')
 return [make()]
def random_date(r):return [r.randint(1600,2400),r.randint(1,12)]
def random_word(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,30)))]
def random_divide(r):return [[r.randint(1,6) for _ in range(r.randint(1,15))],r.randint(1,7)]
def random_relative(r):
 vals=[r.randint(0,15) for _ in range(r.randint(1,15))];return [vals,r.sample(sorted(set(vals)),r.randint(0,len(set(vals))))]
def random_hours(r):return [[r.randint(0,16) for _ in range(r.randint(1,16))]]
def random_team(r):
 skills=[chr(97+i) for i in range(r.randint(1,6))];people=[]
 for _ in range(r.randint(1,9)):people.append([s for s in skills if r.random()<.4])
 if set().union(*map(set,people),set())!=set(skills):people.append(skills)
 return [skills,people]
def random_dominoes(r):return [[[r.randint(1,9),r.randint(1,9)] for _ in range(r.randint(1,15))]]
def random_alt(r):
 n=r.randint(1,9);return [n,[[i,j] for i in range(n) for j in range(n) if i!=j and r.random()<.12],[[i,j] for i in range(n) for j in range(n) if i!=j and r.random()<.12]]
def random_leaves(r):return [[r.randint(1,15) for _ in range(r.randint(2,8))]]
def random_abs(r):
 n=r.randint(1,12);return [[r.randint(-20,20) for _ in range(n)],[r.randint(-20,20) for _ in range(n)]]
def random_unique(r):return [[r.randint(0,15) for _ in range(r.randint(1,18))]]
def random_armstrong(r):return [r.randint(0,100000)]
def random_mst(r):
 n=r.randint(1,6);return [n,[[i,j,r.randint(1,20)] for i in range(1,n+1) for j in range(i+1,n+1) if r.random()<.45]]
def random_courses(r):
 n=r.randint(1,8);order=list(range(1,n+1));r.shuffle(order);return [n,[[order[i],order[j]] for i in range(n) for j in range(i+1,n) if r.random()<.2]]
def random_trib(r):return [r.randint(0,30)]
def random_target(r):return [''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,18)))]

FOREST='''def delete_nodes_forest(root, to_delete):
 deleted=set(to_delete);forest=[]
 def serialize(node):
  if node is None:return []
  from collections import deque
  out=[];q=deque([node])
  while q:
   item=q.popleft()
   if item is None:out.append(None)
   else:out.append(item.val);q.extend((item.left,item.right))
  while out and out[-1] is None:out.pop()
  return out
 def visit(node,is_root):
  if node is None:return None
  gone=node.val in deleted
  if is_root and not gone:forest.append(node)
  node.left=visit(node.left,gone);node.right=visit(node.right,gone)
  return None if gone else node
 visit(root,True);return [serialize(node) for node in forest]
'''
SPLIT='''def split_parentheses_depth(seq):
 depth=0;answer=[]
 for char in seq:
  if char=='(':answer.append(depth%2);depth+=1
  else:depth-=1;answer.append(depth%2)
 return answer
'''
DAYS='''def days_in_month(year, month):
 if month==2:return 29 if year%400==0 or year%4==0 and year%100!=0 else 28
 return 30 if month in (4,6,9,11) else 31
'''
VOWELS='''def remove_lowercase_vowels(text):
 return ''.join(char for char in text if char not in 'aeiou')
'''
AVERAGE='''def maximum_subtree_average(root):
 best=0
 def visit(node):
  nonlocal best
  if node is None:return 0,0
  a,b=visit(node.left);c,d=visit(node.right);total=a+c+node.val;count=b+d+1;best=max(best,total/count);return total,count
 visit(root);return best
'''
DIVIDE='''def can_divide_increasing_sequences(nums, k):
 from collections import Counter
 return len(nums)//k>=max(Counter(nums).values())
'''
RELATIVE='''def relative_sort_values(arr1, arr2):
 rank={value:i for i,value in enumerate(arr2)}
 return sorted(arr1,key=lambda value:(0,rank[value]) if value in rank else (1,value))
'''
DEEPEST='''def deepest_leaves_lca(root):
 def visit(node):
  if node is None:return 0,None
  ld,left=visit(node.left);rd,right=visit(node.right)
  return (ld+1,left) if ld>rd else (rd+1,right) if rd>ld else (ld+1,node)
 return visit(root)[1]
'''
INTERVAL='''def longest_well_performing_interval(hours):
 score=0;first={0:-1};answer=0
 for i,value in enumerate(hours):
  score+=1 if value>8 else -1
  if score>0:answer=i+1
  elif score-1 in first:answer=max(answer,i-first[score-1])
  first.setdefault(score,i)
 return answer
'''
TEAM='''def smallest_sufficient_team(req_skills, people):
 bits={skill:1<<i for i,skill in enumerate(req_skills)};dp={0:()}
 for i,skills in enumerate(people):
  mask=0
  for skill in skills:mask|=bits.get(skill,0)
  for have,team in list(dp.items()):
   combined=have|mask;candidate=team+(i,)
   if combined not in dp or (len(candidate),candidate)<(len(dp[combined]),dp[combined]):dp[combined]=candidate
 return list(dp[(1<<len(req_skills))-1])
'''
TEAM_GREEDY='''def smallest_sufficient_team(req_skills, people):
 bits={skill:1<<i for i,skill in enumerate(req_skills)};masks=[]
 for skills in people:
  mask=0
  for skill in skills:mask|=bits.get(skill,0)
  masks.append(mask)
 have=0;team=[];target=(1<<len(req_skills))-1
 while have!=target:
  person=max((i for i in range(len(people)) if i not in team),key=lambda i:((masks[i]&~have).bit_count(),-i))
  team.append(person);have|=masks[person]
 return team
'''
DOMINO='''def equivalent_domino_pair_count(dominoes):
 from collections import Counter
 counts=Counter(tuple(sorted(pair)) for pair in dominoes)
 return sum(count*(count-1)//2 for count in counts.values())
'''
ALT='''def shortest_alternating_paths(n, red_edges, blue_edges):
 adjacent=[[[],[]] for _ in range(n)]
 for x,y in red_edges:adjacent[x][0].append(y)
 for x,y in blue_edges:adjacent[x][1].append(y)
 from collections import deque
 distance=[[-1,-1] for _ in range(n)];distance[0]=[0,0];q=deque([(0,0),(0,1)])
 while q:
  node,last=q.popleft();color=1-last
  for other in adjacent[node][color]:
   if distance[other][color]<0:distance[other][color]=distance[node][last]+1;q.append((other,color))
 return [min((x for x in row if x>=0),default=-1) for row in distance]
'''
LEAFTREE='''def minimum_leaf_value_tree_cost(arr):
 stack=[float('inf')];answer=0
 for value in arr:
  while stack[-1]<=value:middle=stack.pop();answer+=middle*min(stack[-1],value)
  stack.append(value)
 while len(stack)>2:answer+=stack.pop()*stack[-1]
 return answer
'''
ABSOLUTE='''def maximum_absolute_expression(arr1, arr2):
 answer=0
 for a,b,c in ((1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1)):
  values=[a*x+b*y+c*i for i,(x,y) in enumerate(zip(arr1,arr2))];answer=max(answer,max(values)-min(values))
 return answer
'''
UNIQUE='''def largest_unique_value(nums):
 from collections import Counter
 counts=Counter(nums);return max((value for value,count in counts.items() if count==1),default=-1)
'''
ARMSTRONG='''def is_armstrong_number(n):
 digits=str(n);return sum(int(char)**len(digits) for char in digits)==n
'''
MST='''def minimum_city_connection_cost(n, connections):
 parent=list(range(n+1))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 total=edges=0
 for x,y,cost in sorted(connections,key=lambda edge:edge[2]):
  x,y=find(x),find(y)
  if x!=y:parent[x]=y;total+=cost;edges+=1
 return total if edges==n-1 else -1
'''
COURSES='''def minimum_course_terms(n, relations):
 adjacent=[[] for _ in range(n)];degree=[0]*n
 for x,y in relations:adjacent[x-1].append(y-1);degree[y-1]+=1
 current=[i for i,d in enumerate(degree) if d==0];terms=completed=0
 while current:
  terms+=1;following=[]
  for course in current:
   completed+=1
   for other in adjacent[course]:degree[other]-=1;following.append(other) if degree[other]==0 else None
  current=following
 return terms if completed==n else -1
'''
TRIB='''def tribonacci_number(n):
 if n<2:return n
 a,b,c=0,1,1
 for _ in range(3,n+1):a,b,c=b,c,a+b+c
 return c
'''
BOARD='''def alphabet_board_path(target):
 row=column=0;answer=[]
 for char in target:
  index=ord(char)-97;r,c=divmod(index,5)
  answer.append('U'*max(0,row-r));answer.append('L'*max(0,column-c));answer.append('D'*max(0,r-row));answer.append('R'*max(0,c-column));answer.append('!');row,column=r,c
 return ''.join(answer)
'''

E=entry
BATCH={
1110:E('delete_nodes_forest',[('root','TreeNode'),('toDelete','list[int]')],'list[list[int]]',['trees','recursion'],['Return surviving trees as level-order lists in root-discovery order.','Delete listed values and promote surviving children to forest roots.'],[([[1,2,3,4,5,6,7],[3,5]],'Deleting three and five yields forests rooted at one,six,seven.'),([[1,2,4,None,3],[3]],'Deleting leaf three leaves the remaining tree rooted at one.')],[[t,d] for t,d in [([1],[]),([1],[1]),([1,2],[1]),([1,2],[2]),([1,2,3],[1]),([1,2,3],[2]),([1,2,3],[2,3]),([1,2,3,4,5],[2]),([1,2,3,4,5],[4]),([1,2,None,3],[2]),([1,None,2,None,3],[2]),([1,2,3,4,5,6,7],[1,4]),([10,5,15,3,7],[5]),([1,2,3,4,None,None,5],[3])]],FOREST,[FOREST.replace('return None if gone else node','return node'),FOREST.replace('if is_root and not gone','if is_root or not gone')],['Never removes deleted nodes from their parents.','Adds every surviving node as a separate forest root.'],forest_oracle,random_forest,['Postorder must prune children before deciding the parent’s returned link.','Carry whether a node occupies a forest-root position.','When a node is deleted, recurse on children as roots and return None; otherwise preserve it.','Every surviving component is discovered exactly where its parent is absent.'],'O(n)','O(height)',5),
1111:E('split_parentheses_depth',[('seq','str')],'list[int]',['stacks','greedy'],['seq is a valid parentheses string.','Assign each character to group 0 or 1 using nesting-depth parity.'],[(['(()())'],'Depth parity splits nested pairs between the groups.'),(['()(())()'],'Independent primitives restart at depth zero.')],[[s] for s in ['()','(())','()()','((()))','(()())','()(())','((())())','(()(()))','()()()','(((())))','(())(())','()((()))','(()())()','((()))()']],SPLIT,[SPLIT.replace('depth%2','0'),SPLIT.replace("else:depth-=1;answer.append(depth%2)","else:answer.append(depth%2);depth-=1")],['Places every parenthesis in one group.','Assigns a closing parenthesis before decreasing its depth.'],split_oracle,random_parens,['Alternating nesting levels balances maximum depth between two groups.','For opening use current depth parity before incrementing; for closing decrement before using parity.','Emit one group bit per input character.','Matching parentheses receive the same parity and each group gets alternating original depth layers.'],'O(n)','O(n)',5),
1118:E('days_in_month',[('year','int'),('month','int')],'int',['math','dates'],['Use Gregorian leap-year rules.','Return the number of days in the requested month.'],[([1992,7],'July always has 31 days.'),([2000,2],'Year 2000 is divisible by 400, so February has 29 days.')],[[y,m] for y,m in [(2019,2),(2020,2),(1900,2),(2004,2),(2100,2),(2021,4),(2021,6),(2021,9),(2021,11),(2021,1),(2021,3),(2021,12),(1600,2),(2400,2)]],DAYS,[DAYS.replace('year%100!=0','year%100==0'),DAYS.replace('(4,6,9,11)','(4,6,9)')],['Treats century years as leap years when divisible by four.','Gives November 31 days.'],days_oracle,random_date,['February depends on leap-year divisibility; four months always have thirty days.','A leap year is divisible by 400 or divisible by 4 but not 100.','Handle February, then 30-day months, otherwise 31.','These disjoint calendar cases cover all twelve months.'],'O(1)','O(1)',3),
1119:E('remove_lowercase_vowels',[('s','str')],'str',['strings'],['Input contains lowercase English letters.','Remove a,e,i,o,u and preserve all other order.'],[(['leetcodeisacommunityforcoders'],'Removing vowels yields ltcdscmmntyfrcdrs.'),(['aeiou'],'Removing every character yields empty text.')],[[s] for s in ['a','b','ab','xyz','hello','rhythm','education','queue','algorithm','mississippi','uoiea','banana','strengths','onomatopoeia']],VOWELS,[VOWELS.replace("'aeiou'","'aeio'"),VOWELS.replace('not in','in')],['Fails to remove the vowel u.','Keeps only vowels instead of consonants.'],vowels_oracle,random_word,['A stable filter directly expresses the operation.','Test each character for membership in the five-vowel set.','Join only characters not in aeiou.','Filtering visits and preserves every surviving consonant exactly once.'],'O(n)','O(n)',3),
1120:E('maximum_subtree_average',[('root','TreeNode')],'float',['trees','recursion'],['Tree values are nonnegative.','Return the maximum node-average among all nonempty subtrees.'],[([[5,6,1]],'Leaf six has the greatest subtree average six.'),([[0,None,1]],'Leaf one produces maximum average one.')],[[t] for t in [[1],[0],[1,2],[2,1],[1,2,3],[5,6,1],[10,1,1,1,1],[0,0,0],[3,9,1,2,4],[8,4,12,2,6,10,14],[1,None,5,None,9],[7,7,7],[20,5,30,1,10],[2,8,3,9,None,1]]],AVERAGE,[AVERAGE.replace('total/count','total//count'),AVERAGE.replace('best=max(best','best=min(best')],['Uses integer division and loses fractional averages.','Keeps the minimum rather than maximum subtree average.'],average_oracle,random_tree,['Each subtree needs its total sum and node count.','Postorder combines child sums/counts with the current value.','Update a global maximum with total/count at every node.','Every possible rooted subtree is evaluated once with exact aggregate data.'],'O(n)','O(height)',5),
1121:E('can_divide_increasing_sequences',[('nums','list[int]'),('k','int')],'bool',['greedy','hash-maps'],['nums is sorted nondecreasing.','Partition all values into increasing subsequences each of length at least k.'],[([[1,2,2,3,3,4,4],3],'At most two copies occur and seven values allow two groups of length at least three.'),([[5,6,6,7,8],3],'Two copies of six require two sequences, but five values cannot give both length three.')],[[n,k] for n,k in [([1],1),([1],2),([1,2],2),([1,1],1),([1,1],2),([1,2,3],3),([1,1,2,2,3,3],3),([1,1,1,2,2,3],2),([1,2,2,3,3,4,4],4),([1,2,3,4,5],2),([1,1,2,3,4,5],3),([2,2,2,3,3,4,4,5,5],3),([1,2,2,2,3,4],2),([1,1,2,2,3,4,5,6],4)]],DIVIDE,[DIVIDE.replace('len(nums)//k','len(nums)%k'),DIVIDE.replace('>=','>')],['Uses the remainder rather than maximum possible group count.','Rejects exact feasibility when group count equals maximum frequency.'],divide_oracle,random_divide,['Equal values must occupy different strictly increasing sequences.','Maximum frequency is therefore the minimum number of required sequences.','The array can supply at most len(nums)//k sequences of length at least k; compare these counts.','Sorted order lets values be distributed across that many sequences whenever the frequency bound holds.'],'O(n)','O(distinct)',8),
1122:E('relative_sort_values',[('arr1','list[int]'),('arr2','list[int]')],'list[int]',['sorting','hash-maps'],['arr2 contains distinct values present in arr1.','Place arr2 values in its order, then remaining values ascending.'],[([[2,3,1,3,2,4,6,7,9,2,19],[2,1,4,3,9,6]],'Values named by arr2 come first by its ranking, followed by 7 and 19.'),([[28,6,22,8,44,17],[22,28,8,6]],'Ranked values precede remaining 17 and 44.')],[[a,b] for a,b in [([1],[]),([1],[1]),([2,1],[1]),([1,2,1],[2]),([3,1,2],[]),([1,2,3],[3,2,1]),([2,3,2,1],[2,1]),([5,3,5,2,1],[5,2]),([0,1,0,2],[0]),([9,8,7,9],[9,7]),([4,4,3,2,1],[4,1]),([10,5,10,1],[5]),([2,1,4,3,2],[3,2]),([7,6,5,4,3],[5,7])]],RELATIVE,[RELATIVE.replace('(1,value)','(1,-value)'),RELATIVE.replace('rank[value]','value')],['Sorts unranked values descending.','Ignores arr2 order and ranks by numeric value.'],relative_oracle,random_relative,['A composite sort key can encode both ordering rules.','Map arr2 values to their indices.','Ranked values use (0,index); others use (1,value).','Tuple sorting places the entire ranked block first and applies the correct order within each block.'],'O(n log n)','O(arr2)',3),
1123:E('deepest_leaves_lca',[('root','TreeNode')],'TreeNode | None',['trees','recursion'],['Return the lowest common ancestor subtree of every deepest leaf.','Tree values are unique.'],[([[3,5,1,6,2,0,8,None,None,7,4]],'Leaves seven and four are deepest; their LCA subtree is [2,7,4].'),([[1]],'The sole node is itself the deepest leaf and its LCA.')],[[t] for t in [[1],[1,2],[1,None,2],[1,2,3],[1,2,3,4],[1,2,3,4,5],[1,2,3,4,None,None,5],[1,2,None,3,None,4],[10,5,15,3,7,13,18],[1,2,3,4,5,6,7],[1,2,3,None,4,None,5],[8,4,12,2,6],[1,None,2,3,4],[5,3,8,1,4,7,9,None,2]]],DEEPEST,[DEEPEST.replace('ld>rd','ld<rd'),DEEPEST.replace('else (ld+1,node)','else (ld+1,left)')],['Chooses the shallower subtree when depths differ.','Returns a child result rather than the current node when depths tie.'],deepest_oracle,random_tree,['Return both deepest depth and its LCA from each subtree.','Choose the deeper child result; when depths tie, current node joins deepest leaves from both sides.','Add one to depth while unwinding.','The first lowest node where maximum-depth branches tie is exactly their LCA.'],'O(n)','O(height)',5),
1124:E('longest_well_performing_interval',[('hours','list[int]')],'int',['prefix-sums','hash-maps'],['A day is tiring when hours>8.','Return longest interval with more tiring than non-tiring days.'],[([[9,9,6,0,6,6,9]],'The first three days score +1 overall, giving length three.'),([[6,6,6]],'No interval has positive score.')],[[x] for x in [[9],[8],[9,8],[8,9],[9,9],[8,8],[9,8,9],[8,9,8],[9,9,6,0,6,6,9],[10,7,10,7,10],[6,9,9,6],[9,6,6,9,9],[12,8,7,10,11],[8,8,9,9,8,9]]],INTERVAL,[INTERVAL.replace('score-1','score+1'),INTERVAL.replace('first.setdefault(score,i)','first[score]=i')],['Looks for the wrong prior prefix score.','Overwrites earliest prefix positions and shortens intervals.'],interval_oracle,random_hours,['Map tiring days to +1 and others to -1; a valid interval has positive sum.','Store the first index of each prefix score.','Positive total from start gives i+1; otherwise score-1 locates an earlier prefix producing +1 or more.','Earliest occurrences maximize length, and integer steps guarantee crossing score-1.'],'O(n)','O(n)',5),
1125:E('smallest_sufficient_team',[('reqSkills','list[str]'),('people','list[list[str]]')],'list[int]',['bitmask-dp','dynamic-programming'],['All required skills can be covered.','Return the lexicographically smallest index list among minimum-size teams.'],[([['java','nodejs','reactjs'],[['java'],['nodejs'],['nodejs','reactjs']]],'People zero and two form the unique smallest team.'),([['algorithms','math','java','reactjs','csharp','aws'],[['algorithms','math','java'],['algorithms','math','reactjs'],['java','csharp','aws'],['reactjs','csharp'],['csharp','math'],['aws','java']]],'People one and two cover all six skills with minimum size two.')],[[s,p] for s,p in [(['a'],[['a']]),(['a','b'],[['a'],['b']]),(['a','b'],[['a','b'],['a'],['b']]),(['a','b','c'],[['a'],['b'],['c']]),(['a','b','c'],[['a','b'],['b','c']]),(['a','b'],[[],['a'],['b']]),(['a','b','c'],[['a','c'],['b'],['a','b']]),(['a'],[[],['a']]),(['a','b','c','d'],[['a','b'],['c','d'],['a','c'],['b','d']]),(['x','y'],[['x'],['x','y']]),(['a','b','c'],[['a'],['a','b'],['c']]),(['a','b','c'],[['a','b','c'],['a','b']]),(['a','b','c','d'],[['a'],['b'],['c'],['d']]),(['a','b','c'],[['a','b'],['a','c'],['b','c']])]],TEAM,[TEAM_GREEDY,TEAM.replace('(len(candidate),candidate)<','(len(candidate),tuple(-x for x in candidate))<')],['Greedily chooses the person with the most uncovered skills, which need not minimize team size.','Uses reversed index preference instead of lexicographically smallest ties.'],team_oracle,random_team,['Encode required skills as bits and map each person to a mask.','For every current covered mask, consider adding the next person.','Keep the candidate with smallest (team length,index tuple) for each combined mask.','Dominated larger teams can never improve a future union, while tie ordering makes output deterministic.'],'O(people*2^skills)','O(2^skills)',8),
1128:E('equivalent_domino_pair_count',[('dominoes','list[list[int]]')],'int',['hash-maps','counting'],['Domino [a,b] is equivalent to [b,a].','Count index pairs of equivalent dominoes.'],[([[[1,2],[2,1],[3,4],[5,6]]],'The first two dominoes form the only equivalent pair.'),([[[1,2],[1,2],[1,1],[1,2],[2,2]]],'Three copies of 1,2 create three pairs.')],[[d] for d in [[[1,1]],[[1,2],[2,1]],[[1,2],[1,2]],[[1,2],[2,3]],[[1,1],[1,1],[1,1]],[[1,2],[2,1],[1,2]],[[3,4],[4,3],[3,4],[4,3]],[[1,9],[9,1],[2,8]],[[5,5],[5,5]],[[1,2],[2,1],[3,3]],[[7,8],[8,7],[7,8]],[[2,2],[2,3],[3,2]],[[1,3],[3,1],[1,3],[2,4]],[[9,9],[9,9],[9,9],[9,9]]]],DOMINO,[DOMINO.replace('tuple(sorted(pair))','tuple(pair)'),DOMINO.replace('//2','//1')],['Treats reversed dominoes as different keys.','Counts ordered rather than unordered index pairs.'],dominoes_oracle,random_dominoes,['Normalize each domino to its sorted endpoint pair.','Count frequencies of normalized pairs.','A group of count c contributes c(c-1)/2 index pairs.','Normalization captures reversal equivalence and the combination formula counts every unordered pair once.'],'O(n)','O(distinct)',3),
1129:E('shortest_alternating_paths',[('n','int'),('redEdges','list[list[int]]'),('blueEdges','list[list[int]]')],'list[int]',['graphs','breadth-first-search'],['Paths start at node zero and consecutive edge colors must alternate.','Return shortest distance to every node or -1.'],[([3,[[0,1],[1,2]],[]],'Node one is one red edge away, but node two cannot use two red edges consecutively.'),([3,[[0,1]],[[1,2]]],'Alternating red then blue reaches distances zero,one,two.')],[[n,r,b] for n,r,b in [(1,[],[]),(2,[[0,1]],[]),(2,[],[[0,1]]),(3,[[0,1],[1,2]],[]),(3,[[0,1]],[[1,2]]),(3,[[0,1]],[[0,2]]),(3,[[0,1],[1,0]],[[1,2]]),(4,[[0,1],[2,3]],[[1,2]]),(4,[[0,1],[1,2]],[[2,3]]),(3,[[0,1]],[[1,0],[1,2]]),(5,[[0,1],[2,3]],[[1,2],[3,4]]),(3,[[1,2]],[[0,1]]),(4,[],[]),(4,[[0,1],[0,2]],[[1,3],[2,3]])]],ALT,[ALT.replace('color=1-last','color=last'),ALT.replace('distance[0]=[0,0]','distance[0]=[-1,0]')],['Continues with the same color instead of alternating.','Seeds only one prior-color state at the source.'],alternating_oracle,random_alt,['BFS state must include both node and color of the last edge.','Seed node zero with both imaginary prior colors.','From each state traverse only the opposite-color adjacency list and visit each (node,color) once.','BFS levels give shortest alternating distances while the color state enforces legality.'],'O(n+edges)','O(n+edges)',5),
1130:E('minimum_leaf_value_tree_cost',[('arr','list[int]')],'int',['monotonic-stack','greedy'],['Leaf inorder values equal arr and internal value is product of subtree maxima.','Return minimum sum of internal values.'],[([[6,2,4]],'Combining two with its smaller neighbor four first yields total 32.'),([[4,11]],'The sole internal node costs 44.')],[[x] for x in [[1,1],[1,2],[2,1],[1,2,3],[3,2,1],[6,2,4],[4,11],[5,5,5],[1,10,1],[7,3,8,2],[2,9,4,6],[15,1,15],[3,1,2,4],[9,8,7,6]]],LEAFTREE,[LEAFTREE.replace('min(stack[-1],value)','value'),LEAFTREE.replace('while len(stack)>2','while False and len(stack)>2')],['Always pairs a removed local minimum with the incoming value, even when its left neighbor is smaller.','Forgets to combine values left in the decreasing stack.'],leaf_tree_oracle,random_leaves,['The smallest remaining leaf maximum should be paired with its smaller neighbor.','A decreasing stack identifies when a value has found both neighboring greater values.','Pop while top<=current and add top*min(new top,current); finish remaining stack pairs.','Exchange arguments show delaying a local minimum to a larger neighbor cannot lower cost.'],'O(n)','O(n)',5),
1131:E('maximum_absolute_expression',[('arr1','list[int]'),('arr2','list[int]')],'int',['math','arrays'],['Arrays have equal nonzero length.','Maximize |a[i]-a[j]|+|b[i]-b[j]|+|i-j|.'],[([[1,2,3,4],[-1,4,5,6]],'The maximum expression value is thirteen.'),([[1,-2,-5,0,10],[0,-2,-1,-7,-4]],'The maximum is twenty.')],[[x,y] for x,y in [([1],[1]),([1,2],[1,2]),([1,2],[2,1]),([0,0],[0,0]),([-1,1],[-1,1]),([1,2,3],[3,2,1]),([1,2,3,4],[-1,4,5,6]),([10,-10],[5,-5]),([1,1,1],[1,1,1]),([0,5,0],[5,0,5]),(([-3,2,7],[4,-1,0])),([9,1,8],[2,7,3]),([1,-2,-5,0,10],[0,-2,-1,-7,-4]),([4,3,2,1],[1,3,5,7])]],ABSOLUTE,[ABSOLUTE.replace('((1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1))','((1,1,1),)'),ABSOLUTE.replace('max(values)-min(values)','max(values)+min(values)')],['Checks only one sign combination.','Adds extrema rather than taking their range.'],absolute_oracle,random_abs,['Each absolute value can be represented by choosing a sign; paired global negations give four distinct cases.','For each signs on arr1,arr2,index, compute transformed values.','The best pair for that sign case is maximum minus minimum.','One sign case matches the orientations of every optimal i,j pair, so their maximum is exact.'],'O(n)','O(n)',5),
1133:E('largest_unique_value',[('nums','list[int]')],'int',['hash-maps','counting'],['Return the largest value occurring exactly once.','Return -1 when every value repeats.'],[([[5,7,3,9,4,9,8,3,1]],'Eight is the greatest value with frequency one.'),([[9,9,8,8]],'No value occurs once, so return -1.')],[[x] for x in [[1],[1,1],[1,2],[2,1,2],[3,3,2],[5,7,3,9,4,9,8,3,1],[0,0,1],[10,9,10],[4,4,5,6,6],[1,2,3,3,2],[9,8,7,9,8],[5,5,5],[2,3,4,2,3],[100,1,100,2]]],UNIQUE,[UNIQUE.replace('count==1','count>=1'),UNIQUE.replace('max(','min(')],['Allows repeated values to compete.','Returns the smallest unique value.'],unique_oracle,random_unique,['Frequency one is the complete eligibility condition.','Count values with a hash map.','Take the maximum key whose count equals one, defaulting to -1.','Every candidate is checked exactly once against both required properties.'],'O(n)','O(distinct)',3),
1134:E('is_armstrong_number',[('n','int')],'bool',['math'],['Raise each decimal digit to the total digit count.','Return whether their sum equals n.'],[([153],'1^3+5^3+3^3 equals 153.'),([123],'The cube sum 36 does not equal 123.')],[[n] for n in [0,1,9,10,100,370,371,407,9474,9475,1634,8208,24678050,99]],ARMSTRONG,[ARMSTRONG.replace('len(digits)','2'),ARMSTRONG.replace('==n','!=n')],['Always squares digits regardless of digit count.','Returns true when the Armstrong sum differs.'],armstrong_oracle,random_armstrong,['The exponent is fixed by the number’s decimal width.','Convert to text to obtain all digits and their count.','Sum int(digit)**width and compare with n.','This is the Armstrong definition applied directly to every decimal digit.'],'O(digits)','O(digits)',3),
1135:E('minimum_city_connection_cost',[('n','int'),('connections','list[list[int]]')],'int',['union-find','minimum-spanning-tree'],['Cities are labeled 1..n and connections are undirected weighted edges.','Return MST cost or -1 if not all cities connect.'],[([3,[[1,2,5],[1,3,6],[2,3,1]]],'Edges cost one and five connect all cities for total six.'),([4,[[1,2,3],[3,4,4]]],'Two disconnected components make full connection impossible.')],[[n,e] for n,e in [(1,[]),(2,[[1,2,5]]),(2,[]),(3,[[1,2,1],[2,3,2]]),(3,[[1,2,5],[1,3,6],[2,3,1]]),(3,[[1,2,1]]),(4,[[1,2,1],[2,3,1],[3,4,1]]),(4,[[1,2,10],[1,3,2],[3,4,3],[2,4,1]]),(4,[[1,2,3],[3,4,4]]),(5,[[1,2,1],[2,3,2],[3,4,3],[4,5,4],[1,5,20]]),(3,[[1,2,1],[1,2,2],[2,3,3]]),(4,[[1,4,5],[2,4,1],[2,3,2],[1,3,10]]),(5,[]),(2,[[1,2,100]])]],MST,[MST.replace('key=lambda edge:edge[2]','key=lambda edge:-edge[2]'),MST.replace('edges==n-1','edges<=n-1')],['Runs maximum rather than minimum spanning-tree order.','Accepts disconnected forests as complete.'],mst_oracle,random_mst,['Kruskal chooses the cheapest edge that joins two current components.','Sort connections by cost and use union-find.','Accumulate successful unions; require exactly n-1.','The cut property proves every selected cheapest cross-component edge is safe for an MST.'],'O(edges log edges)','O(n)',5),
1136:E('minimum_course_terms',[('n','int'),('relations','list[list[int]]')],'int',['graphs','topological-sort'],['Each relation [a,b] requires a before b.','Take unlimited ready courses per term; return minimum terms or -1 on a cycle.'],[([3,[[1,3],[2,3]]],'Courses one and two share term one, then course three takes term two.'),([3,[[1,2],[2,3],[3,1]]],'The prerequisite cycle makes completion impossible.')],[[n,e] for n,e in [(1,[]),(2,[]),(2,[[1,2]]),(2,[[1,2],[2,1]]),(3,[[1,3],[2,3]]),(3,[[1,2],[2,3]]),(3,[[1,2],[1,3]]),(4,[[1,2],[2,3],[3,4]]),(4,[[1,3],[2,3],[3,4]]),(4,[[1,2],[3,4]]),(5,[[1,2],[1,3],[2,4],[3,4],[4,5]]),(3,[[1,2],[1,2]]),(5,[]),(4,[[1,2],[2,1],[3,4]])]],COURSES,[COURSES.replace('terms+=1','terms+=len(current)'),COURSES.replace('degree[y-1]+=1','degree[x-1]+=1')],['Counts each ready course as a separate term.','Increments indegree of prerequisites instead of dependent courses.'],courses_oracle,random_courses,['Each topological BFS layer is one semester of simultaneously ready courses.','Track indegrees and begin with all zero-indegree nodes.','Remove one layer, unlock its successors, and count layers; detect a cycle by incomplete count.','Dependencies force successive layers, while every course within a layer can run together.'],'O(n+relations)','O(n+relations)',5),
1137:E('tribonacci_number',[('n','int')],'int',['dynamic-programming','math'],['T0=0,T1=T2=1 and each later term sums the previous three.','Return Tn.'],[([4],'Values 0,1,1,2,4 give T4=4.'),([25],'Iterating the recurrence gives 1389537.')],[[n] for n in [0,1,2,3,5,6,7,10,15,20,25,30,35,37]],TRIB,[TRIB.replace('a+b+c','b+c'),TRIB.replace('if n<2','if n<3')],['Drops the oldest of the three recurrence terms.','Uses the same base return for n=2 and returns two instead of one.'],trib_oracle,random_trib,['Only the previous three terms are needed.','Handle n zero and one directly; initialize 0,1,1.','Rotate the triple while appending their sum through index n.','The variables maintain exactly T(i-2),T(i-1),T(i) after each iteration.'],'O(n)','O(1)',3),
1138:E('alphabet_board_path',[('target','str')],'str',['strings','simulation'],['The board rows are abcde through uvwxy with z alone below u.','For deterministic grading move Up, then Left, then Down, then Right before selecting with !.'],[(['leet'],'Moves select l,e,e,t while staying on valid cells.'),(['code'],'Moves select c,o,d,e.')],[[s] for s in ['a','z','az','za','abc','xyz','leetcode','code','zz','bz','zb','u','v','alphabet','maze']],BOARD,[BOARD.replace("answer.append('U'","answer.append('D'"),BOARD.replace("answer.append('!'","answer.append(''" )],['Moves downward when an upward move is required, potentially entering invalid cells.','Never emits the selection marker.'],board_oracle,random_target,['Map each letter index to row,column with divmod by five.','Move up and left before down and right so leaving or entering z never crosses missing cells.','Append one ! after reaching each target character.','The coordinate differences give a shortest route and the move order makes it valid and deterministic.'],'O(target)','O(target)',5),
}
for pid in (1110,1120,1123):BATCH[pid]['params'][0]=('root','TreeNode | None','treenode')
BATCH[1123]['adapter']='treenode'
BATCH[1120]['comparator']='float'
