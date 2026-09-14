"""Second group of batch 105: tree ancestry, palindrome DP, and counting."""
from collections import deque
from itertools import product
from math import gcd
from .import_batch_055 import entry
def coprime_o(a):
 nums,edges=a;n=len(nums);graph=[[] for _ in range(n)]
 for x,y in edges:graph[x].append(y);graph[y].append(x)
 parent=[-1]*n;depth=[0]*n;queue=deque([0]);order=[0]
 while queue:
  node=queue.popleft()
  for nxt in graph[node]:
   if nxt!=parent[node]:parent[nxt]=node;depth[nxt]=depth[node]+1;queue.append(nxt);order.append(nxt)
 answer=[]
 for node in range(n):
  ancestor=parent[node]
  while ancestor!=-1 and gcd(nums[node],nums[ancestor])!=1:ancestor=parent[ancestor]
  answer.append(ancestor)
 return answer
def palindrome_o(a):
 first,second=a;combined=first+second;split=len(first);best=0
 for mask in range(1,1<<len(combined)):
  if not any(mask>>i&1 for i in range(split)) or not any(mask>>i&1 for i in range(split,len(combined))):continue
  text=''.join(combined[i] for i in range(len(combined)) if mask>>i&1)
  if text==text[::-1]:best=max(best,len(text))
 return best
def features_o(a):
 features,responses=a;counts={f:0 for f in features}
 for response in responses:
  words=set(response.split())
  for feature in features:counts[feature]+=feature in words
 order={feature:i for i,feature in enumerate(features)};return sorted(features,key=lambda f:(-counts[f],order[f]))
def items_o(a):
 items,key,value=a;index={'type':0,'color':1,'name':2}[key];return sum(item[index]==value for item in items)
def dessert_o(a):
 bases,toppings,target=a;best=None
 for base in bases:
  for choices in product((0,1,2),repeat=len(toppings)):
   cost=base+sum(count*value for count,value in zip(choices,toppings))
   if best is None or (abs(cost-target),cost)<(abs(best-target),best):best=cost
 return best
def rcoprime(r):
 n=r.randint(1,20);nums=[r.randint(1,20) for _ in range(n)];edges=[[node,r.randrange(node)] for node in range(1,n)];return [nums,edges]
def rpalindrome(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,5))),''.join(r.choice('abc') for _ in range(r.randint(1,5)))]
def rfeatures(r):
 features=[f'f{i}' for i in range(r.randint(1,7))];responses=[' '.join(r.choices(features+['other'],k=r.randint(1,10))) for _ in range(r.randint(1,10))];return [features,responses]
def ritems(r):
 pool=['a','b','c'];items=[[r.choice(pool),r.choice(pool),r.choice(pool)] for _ in range(r.randint(1,20))];return [items,r.choice(('type','color','name')),r.choice(pool)]
def rdessert(r):return [[r.randint(1,20) for _ in range(r.randint(1,5))],[r.randint(1,10) for _ in range(r.randint(1,5))],r.randint(1,50)]
COPRIME='''def nearest_coprime_ancestors(nums, edges):
 from math import gcd
 graph=[[] for _ in nums]
 for left,right in edges:graph[left].append(right);graph[right].append(left)
 latest=[[] for _ in range(51)];answer=[-1]*len(nums)
 def visit(node,parent,depth):
  best_depth=-1
  for value in range(1,51):
   if latest[value] and gcd(value,nums[node])==1 and latest[value][-1][0]>best_depth:best_depth,answer[node]=latest[value][-1]
  latest[nums[node]].append((depth,node))
  for child in graph[node]:
   if child!=parent:visit(child,node,depth+1)
  latest[nums[node]].pop()
 visit(0,-1,0);return answer
'''
PALINDROME='''def longest_cross_word_palindrome(word1, word2):
 text=word1+word2;n=len(text);split=len(word1);dp=[[0]*n for _ in range(n)];answer=0
 for left in range(n-1,-1,-1):
  dp[left][left]=1
  for right in range(left+1,n):
   if text[left]==text[right]:dp[left][right]=2+(dp[left+1][right-1] if right-left>1 else 0)
   else:dp[left][right]=max(dp[left+1][right],dp[left][right-1])
   if left<split<=right and text[left]==text[right]:answer=max(answer,dp[left][right])
 return answer
'''
FEATURES='''def sort_features_by_popularity(features, responses):
 counts={feature:0 for feature in features}
 for response in responses:
  mentioned=set(response.split())
  for feature in features:
   if feature in mentioned:counts[feature]+=1
 position={feature:index for index,feature in enumerate(features)}
 return sorted(features,key=lambda feature:(-counts[feature],position[feature]))
'''
ITEMS='''def matching_item_count(items, rule_key, rule_value):
 index={'type':0,'color':1,'name':2}[rule_key]
 return sum(item[index]==rule_value for item in items)
'''
DESSERT='''def closest_dessert_cost(base_costs, topping_costs, target):
 possible=set(base_costs)
 for topping in topping_costs:possible|={cost+topping for cost in list(possible)}|{cost+2*topping for cost in list(possible)}
 return min(possible,key=lambda cost:(abs(cost-target),cost))
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1766:E('nearest_coprime_ancestors',[('nums','list[int]'),('edges','list[list[int]]')],'list[int]',['trees','depth-first-search','number-theory'],['Nodes form a tree rooted at zero and nums[i] is between 1 and 50.','For each node, return its nearest strict ancestor whose value is coprime with the node value, or -1.'],[([[2,3,3,2],[[0,1],[1,2],[1,3]]],'Node one uses ancestor zero; node two also uses zero; node three uses nearest ancestor one, giving [-1,0,0,1].'),([[5,6,10,2,3,6,15],[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]]],'Walking each root path and choosing the deepest coprime value gives [-1,0,-1,0,0,-1,-1].')],[[*x] for x in [([2],[]),([2,3],[[0,1]]),([2,4],[[0,1]]),([2,3,5],[[0,1],[1,2]]),([6,10,7],[[0,1],[1,2]]),([2,3,3,2],[[0,1],[1,2],[1,3]]),([5,6,10,2,3,6,15],[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]]),([1,2,3],[[0,1],[0,2]]),([6,35,10,9],[[0,1],[1,2],[2,3]]),([4,9,8,3],[[0,1],[0,2],[2,3]]),([2,2,3,3,5],[[0,1],[1,2],[2,3],[3,4]]),([30,6,7,11],[[0,1],[1,2],[1,3]]),([8,15,21,25],[[0,1],[1,2],[2,3]]),([10,9,8,7,6],[[0,1],[0,2],[1,3],[1,4]])]],COPRIME,[COPRIME.replace('latest[value][-1][0]>best_depth','latest[value][0][0]>best_depth'),COPRIME.replace('latest[nums[node]].pop()','latest[nums[node]].clear()')],['Compares the oldest matching occurrence but returns the newest node, corrupting depth selection.','Clears all same-valued ancestors when backtracking instead of removing only the current node.'],coprime_o,rcoprime,L('Only the latest active ancestor for each value 1..50 can be nearest.','DFS the rooted tree while maintaining a stack of (depth,node) for each value.','Before pushing the current node, scan coprime value stacks and choose the deepest top; pop after visiting children.','The active stacks exactly represent the root-to-parent path, and their tops dominate older equal-valued ancestors.'),'O(n*50)','O(n+50)',8),
1771:E('longest_cross_word_palindrome',[('word1','str'),('word2','str')],'int',['strings','dynamic-programming'],['Choose a nonempty subsequence from each word and concatenate them in word order.','Return the maximum possible palindrome length, or zero if none can use characters from both words.'],[(['cacb','cbba'],'Choosing ac from word1 and bca from word2 forms acbca of length five.'),(['ab','ab'],'Choosing a from each word gives palindrome aa of length two.')],[[*x] for x in [('cacb','cbba'),('ab','ab'),('a','a'),('a','b'),('aa','bb'),('abc','cba'),('abc','def'),('aaa','a'),('abca','xyax'),('zz','zz'),('abcd','dcba'),('cab','bac'),('xxy','yxx'),('ace','eca')]],PALINDROME,[PALINDROME.replace('left<split<=right','left<=split<=right'),PALINDROME.replace('answer=max(answer,dp[left][right])','answer=max(answer,2)')],['Allows the left palindrome endpoint to come from word2, accepting a one-word palindrome.','Records only the matching endpoint pair and ignores a longer palindromic interior.'],palindrome_o,rpalindrome,L('A valid answer must contain a matching outer pair with its left character in word1 and right character in word2.','Compute longest-palindromic-subsequence DP on the concatenated text.','Whenever a matching transition crosses the word boundary, use its DP length to update the answer.','Every valid cross-word palindrome has such an outer cross-boundary matching pair, and the interval DP optimizes its interior.'),'O((n+m)^2)','O((n+m)^2)',8),
1772:E('sort_features_by_popularity',[('features','list[str]'),('responses','list[str]')],'list[str]',['strings','hash-maps','sorting'],['Popularity is the number of responses containing the feature as a complete whitespace-separated word; repeated mentions in one response count once.','Sort descending by popularity, preserving original feature order on ties.'],[([['cooler','lock','touch'],['i like cooler cooler','lock touch cool','locker like touch']],'Touch appears in two responses; cooler and lock appear once and retain their original tie order.'),([['a','b','c'],['b a','c b','a c']],'All features appear twice, so the original order remains unchanged.')],[[*x] for x in [(['cooler','lock','touch'],['i like cooler cooler','lock touch cool','locker like touch']),(['a','b','c'],['b a','c b','a c']),(['x'],['x']),(['x'],['other']),(['a','b'],[]),(['a','b'],['a']),(['a','b'],['b']),(['one','two'],['one one one']),(['cat','car'],['catalog car']),(['f0','f1','f2'],['f2 f1','f2']),(['red','blue','green'],['red blue','green','blue']),(['aa','a'],['aa a']),(['p','q','r'],['q r','p q','r']),(['first','second'],['second first','second'])]],FEATURES,[FEATURES.replace('mentioned=set(response.split())','mentioned=response.split()'),FEATURES.replace('position[feature]','-position[feature]')],['Counts repeated mentions within one response multiple times.','Reverses the original order when popularity ties.'],features_o,rfeatures,L('Each response contributes at most one vote per feature.','Convert each response to a word set, tally feature membership, and sort with original index as tie-breaker.','Use key (-count,original_position).','Set membership enforces one vote per response, and the compound key exactly implements the required stable popularity order.'),'O(responses*features+features log features)','O(features)',5),
1773:E('matching_item_count',[('items','list[list[str]]'),('rule_key','str'),('rule_value','str')],'int',['arrays','hash-maps'],['Every item stores [type,color,name].','Count items whose field selected by rule_key equals rule_value exactly.'],[([[['phone','blue','pixel'],['computer','silver','lenovo'],['phone','gold','iphone']],'color','silver'],'Only the computer has silver in the color field.'),([[['phone','blue','pixel'],['computer','silver','phone'],['phone','gold','iphone']],'type','phone'],'The first and third items have type phone, so the count is two.')],[[*x] for x in [([['phone','blue','pixel'],['computer','silver','lenovo'],['phone','gold','iphone']],'color','silver'),([['phone','blue','pixel'],['computer','silver','phone'],['phone','gold','iphone']],'type','phone'),([['a','b','c']],'name','c'),([['a','b','c']],'name','a'),([['x','x','x']],'color','x'),([['a','b','c'],['a','c','b']],'type','a'),([['a','b','c'],['a','c','b']],'color','b'),([['a','b','c'],['a','c','b']],'name','b'),([['1','2','3']],'type','1'),([['red','red','red'],['blue','red','x']],'color','red'),([['t','c','n'],['u','d','m']],'name','z'),([['a','b','c'],['d','e','f'],['g','h','i']],'color','e'),([['same','x','y'],['other','same','z']],'type','same'),([['x','y','z'],['z','y','x']],'name','x')]],ITEMS,[ITEMS.replace("'color':1","'color':2"),ITEMS.replace('==rule_value','!=rule_value')],['Reads item name when the rule requests color.','Counts nonmatching items instead of matching items.'],items_o,ritems,L('The rule key selects one fixed position in every three-field item.','Map type, color, and name to indices zero, one, and two.','Count rows whose selected field equals the rule value.','The mapping is the item schema, so the equality test is exactly the rule definition for every row.'),'O(items)','O(1)',3),
1774:E('closest_dessert_cost',[('base_costs','list[int]'),('topping_costs','list[int]'),('target','int')],'int',['backtracking','sets'],['Choose exactly one base and zero, one, or two of each topping.','Minimize absolute difference from target; if two totals tie, return the smaller total.'],[([[1,7],[3,4],10],'Base seven plus topping three reaches target exactly.'),([[2,3],[4,5,100],18],'The closest attainable total is seventeen, using base three and two each of toppings four and five.')],[[*x] for x in [([1,7],[3,4],10),([2,3],[4,5,100],18),([5],[1],5),([5],[1],6),([5],[1],7),([1],[10],6),([1,2],[3],4),([10],[2,3],1),([2],[2],5),([3,8],[1,2],7),([1],[1,1],4),([4,6],[5],10),([7],[3,4],20),([2,9],[2,5],12)]],DESSERT,[DESSERT.replace('(0,1,2)','(0,1)'),DESSERT.replace('(abs(cost-target),cost)','(abs(cost-target),-cost)')],['Allows each topping at most once instead of twice.','Breaks equal-distance ties toward the larger total.'],dessert_o,rdessert,L('Each topping independently has multiplicity zero, one, or two.','Grow the set of attainable totals from all bases by adding one and two copies of each topping.','Choose the cost with key (absolute difference,cost).','The set expansion enumerates every legal combination exactly as a sequence of multiplicity choices, and the key enforces both optimization rules.'),'O(bases*3^toppings)','O(bases*3^toppings)',5),
}
BATCH[1766]['wrong'][0]=COPRIME.replace("latest[value][-1][0]>best_depth","answer[node]==-1")
BATCH[1766]['wrong_reasons'][0]='Chooses the first coprime value numerically instead of the deepest coprime ancestor.'
BATCH[1772]['wrong'][0]=FEATURES.replace('mentioned=set(response.split())','mentioned=response.split()').replace('if feature in mentioned:counts[feature]+=1','counts[feature]+=mentioned.count(feature)')
BATCH[1772]['wrong_reasons'][0]='Counts every repeated mention in a response instead of at most one vote per response.'
BATCH[1774]['wrong'][0]=DESSERT.replace('|{cost+2*topping for cost in list(possible)}','')
BATCH[1774]['wrong_reasons'][0]='Generates zero or one copy of each topping but omits the allowed second copy.'
