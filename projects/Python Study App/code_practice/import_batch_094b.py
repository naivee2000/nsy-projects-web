"""Second half of batch 94: recursion, string ordering, and counting tasks."""
from collections import Counter
from functools import lru_cache
from itertools import groupby
from math import gcd
from .import_batch_055 import entry

def tree(raw):
 if not raw:return None
 nodes=[None if x is None else [x,None,None] for x in raw];children=iter(nodes[1:])
 for node in nodes:
  if node is not None:node[1]=next(children,None);node[2]=next(children,None)
 return nodes[0]
def power_o(a):return max(len(list(g)) for _,g in groupby(a[0]))
def fractions_o(a):return [f'{x}/{y}' for y in range(2,a[0]+1) for x in range(1,y) if gcd(x,y)==1]
def good_o(a):
 root=tree(a[0]);answer=0
 def walk(node,largest):
  nonlocal answer
  if not node:return
  if node[0]>=largest:answer+=1
  walk(node[1],max(largest,node[0]));walk(node[2],max(largest,node[0]))
 walk(root,float('-inf'));return answer
def largest_o(a):
 cost,target=a
 @lru_cache(None)
 def search(digit,remaining):
  if digit==0:return '' if remaining==0 else None
  best=None;c=cost[digit-1]
  for count in range(remaining//c+1):
   tail=search(digit-1,remaining-count*c)
   if tail is not None:
    candidate=str(digit)*count+tail
    if best is None or (len(candidate),candidate)>(len(best),best):best=candidate
  return best
 answer=search(9,target);return answer if answer else '0'
def students_o(a):return sum(start<=a[2]<=end for start,end in zip(a[0],a[1]))
def arrange_o(a):
 words=a[0].lower().split();answer=' '.join(sorted(words,key=len));return answer[0].upper()+answer[1:]
def companies_o(a):
 groups=list(map(set,a[0]));return [i for i,g in enumerate(groups) if not any(i!=j and g<=other for j,other in enumerate(groups))]
def prefix_o(a):
 sentence,word=a
 for i,x in enumerate(sentence.split(),1):
  if x.startswith(word):return i
 return -1
def vowels_o(a):
 s,k=a;return max(sum(c in 'aeiou' for c in s[i:i+k]) for i in range(len(s)-k+1))
def paths_o(a):
 root=tree(a[0]);answer=0
 def walk(node,counts):
  nonlocal answer
  if not node:return
  counts[node[0]]+=1
  if not node[1] and not node[2]:answer+=sum(v%2 for v in counts.values())<=1
  else:walk(node[1],counts);walk(node[2],counts)
  counts[node[0]]-=1
 walk(root,Counter());return answer

def rpower(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,50)))]
def rfrac(r):return [r.randint(2,20)]
def rtree(r):return [[r.randint(-20,20) for _ in range(r.randint(1,25))]]
def rlargest(r):return [[r.randint(1,9) for _ in range(9)],r.randint(1,25)]
def rstudent(r):
 n=r.randint(1,30);starts=[r.randint(1,30) for _ in range(n)];ends=[x+r.randint(0,20) for x in starts];return [starts,ends,r.randint(1,50)]
def rarrange(r):
 words=[''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,10))) for _ in range(r.randint(1,15))];text=' '.join(words);return [text[0].upper()+text[1:]]
def rcompany(r):
 names=[f'c{i}' for i in range(10)];return [[sorted(r.sample(names,r.randint(1,6))) for _ in range(r.randint(2,8))]]
def rprefix(r):
 words=[''.join(r.choice('abcde') for _ in range(r.randint(1,8))) for _ in range(r.randint(1,15))];return [' '.join(words),''.join(r.choice('abcde') for _ in range(r.randint(1,5)))]
def rvowels(r):
 s=''.join(r.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(r.randint(1,40)));return [s,r.randint(1,len(s))]
def rpaths(r):return [[r.randint(1,9) for _ in range(r.randint(1,25))]]

POWER='''def longest_character_power(s):
 answer=current=1
 for i in range(1,len(s)):
  current=current+1 if s[i]==s[i-1] else 1;answer=max(answer,current)
 return answer
'''
FRACTIONS='''def simplified_fractions(n):
 from math import gcd
 return [f'{numerator}/{denominator}' for denominator in range(2,n+1) for numerator in range(1,denominator) if gcd(numerator,denominator)==1]
'''
GOOD='''def count_good_tree_nodes(root):
 def visit(node,largest):
  if not node:return 0
  good=int(node.val>=largest);largest=max(largest,node.val)
  return good+visit(node.left,largest)+visit(node.right,largest)
 return visit(root,float('-inf'))
'''
LARGEST='''def largest_number_for_digit_cost(cost, target):
 best=[None]*(target+1);best[0]=''
 for total in range(1,target+1):
  for digit,value in enumerate(cost,1):
   if value<=total and best[total-value] is not None:
    candidate=''.join(sorted(best[total-value]+str(digit),reverse=True))
    if best[total] is None or (len(candidate),candidate)>(len(best[total]),best[total]):best[total]=candidate
 return best[target] if best[target] else '0'
'''
STUDENTS='''def active_students_at_time(start_time, end_time, query_time):
 return sum(start<=query_time<=end for start,end in zip(start_time,end_time))
'''
ARRANGE='''def rearrange_sentence_by_length(text):
 words=text.lower().split();ordered=sorted(words,key=len);answer=' '.join(ordered)
 return answer[0].upper()+answer[1:]
'''
COMPANIES='''def non_subset_company_people(favorite_companies):
 groups=[set(group) for group in favorite_companies]
 return [i for i,group in enumerate(groups) if not any(i!=j and group<=other for j,other in enumerate(groups))]
'''
PREFIX='''def first_prefix_word(sentence, search_word):
 for index,word in enumerate(sentence.split(),1):
  if word.startswith(search_word):return index
 return -1
'''
VOWELS='''def maximum_vowels_in_window(s, k):
 vowels=set('aeiou');current=sum(char in vowels for char in s[:k]);answer=current
 for right in range(k,len(s)):
  current+=(s[right] in vowels)-(s[right-k] in vowels);answer=max(answer,current)
 return answer
'''
PATHS='''def count_pseudo_palindromic_paths(root):
 def visit(node,mask):
  if not node:return 0
  mask^=1<<node.val
  if not node.left and not node.right:return int(mask&(mask-1)==0)
  return visit(node.left,mask)+visit(node.right,mask)
 return visit(root,0)
'''
ZERO_FRACTIONS='''def simplified_fractions(n):
 from math import gcd
 return [f'{numerator}/{denominator}' for denominator in range(2,n+1) for numerator in range(0,denominator) if numerator==0 or gcd(numerator,denominator)==1]
'''
START_ONLY_STUDENTS='''def active_students_at_time(start_time, end_time, query_time):
 return sum(start<=query_time for start in start_time)
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1446:S('longest_character_power',[('s','str')],'int',['strings','counting'],['Power is the maximum length of a non-empty substring containing one repeated character.','s is non-empty.'],[(['leetcode'],'The longest runs are ee and consecutive c characters, each length two.'),(['abbcccddddeeeeedcba'],'The five consecutive e characters give power five.')],[[s] for s in ['a','aa','ab','aba','leetcode','abbcccddddeeeeedcba','aaaaa','abcde','aabbaa','xxxyzzzz','mississippi','111122','abababab','zzyyyzz']],POWER,[POWER.replace('s[i]==s[i-1]','s[i]!=s[i-1]'),POWER.replace('answer=max(answer,current)','answer=min(answer,current)')],['Extends runs when adjacent characters differ.','Retains the shortest rather than longest run.'],power_o,rpower,['Track the length of the current equal-character run.','Extend it when the character matches the previous one; otherwise reset to one.','Update the maximum after each character.','Every constant substring lies inside exactly one maximal run, so the longest run is the answer.'],'O(n)','O(1)',3),
1447:S('simplified_fractions',[('n','int')],'list[str]',['math','number-theory'],['Return every reduced fraction between zero and one whose denominator is at most n.','Order by increasing denominator, then numerator.'],[([2],'The only eligible reduced fraction is 1/2.'),([4],'Denominators two through four yield 1/2, 1/3, 2/3, 1/4, and 3/4.')],[[n] for n in [2,3,4,5,6,7,8,9,10,12,15,20,30,50]],FRACTIONS,[FRACTIONS.replace('gcd(numerator,denominator)==1','True'),ZERO_FRACTIONS],['Includes unreduced duplicate-valued fractions.','Includes a zero fraction for every denominator.'],fractions_o,rfrac,['Enumerate each denominator from two through n.','For each smaller positive numerator, keep it only when gcd is one.','Format each retained pair as numerator/denominator.','Coprime numerator and denominator is exactly the reduced-form condition, and loop order gives the requested order.'],'O(n² log n)','O(output)',5),
1448:S('count_good_tree_nodes',[('root','TreeNode | None')],'int',['trees','depth-first-search'],['A node is good when no earlier node on its root-to-node path has a greater value.','The tree is non-empty and values may repeat.'],[([[3,1,4,3,None,1,5]],'The root, left leaf three, right four, and right leaf five are good.'),([[3,3,None,4,2]],'Equal-to-maximum values count, while two below path maximum does not.')],[[t] for t in [[1],[1,2],[2,1],[3,1,4,3,None,1,5],[3,3,None,4,2],[1,1,1],[0,-1,1],[-5,-4,-6],[5,4,3,6,7],[2,2,1,2,3],[10,5,15,3,7,12,20],[1,None,2,None,3],[4,3,None,2,None,1],[2,1,3,4,0]]],GOOD,[GOOD.replace('node.val>=largest','node.val>largest'),GOOD.replace('largest=max(largest,node.val)','largest=node.val')],['Rejects nodes equal to the prior path maximum.','Forgets larger ancestors and compares only with the parent.'],good_o,rtree,['Carry the greatest value seen on the root-to-current path.','Count the node when node.val is at least that value.','Pass max(previous,node.val) to both children.','The carried maximum summarizes exactly all ancestors relevant to the definition.'],'O(n)','O(height)',5),
1449:S('largest_number_for_digit_cost',[('cost','list[int]'),('target','int')],'str',['dynamic-programming','strings'],['cost[d-1] is the cost of appending digit d; use total cost exactly target.','Return the numerically largest positive integer, or "0" if impossible.'],[([[4,3,2,5,6,7,2,5,5],9],'Four digits are possible, and descending 7772 is the largest.'),([[7,6,5,5,5,6,8,7,8],12],'Two nines cost sixteen, so the optimal exact-cost result is 85.')],[[c,t] for c,t in [([1]*9,1),([1]*9,3),([2]*9,1),([2]*9,4),([4,3,2,5,6,7,2,5,5],9),([7,6,5,5,5,6,8,7,8],12),([2,4,6,2,4,6,4,4,4],5),([6,10,15,40,40,40,40,40,40],47),([5,4,3,2,1,2,3,4,5],5),([9,8,7,6,5,4,3,2,1],10),([3,3,3,3,3,3,3,3,3],6),([2,3,5,7,11,13,17,19,23],20),([8,1,8,8,8,8,8,8,8],4),([5,5,5,5,5,5,5,5,5],7)]],LARGEST,[LARGEST.replace('(len(candidate),candidate)>(len(best[total]),best[total])','candidate>best[total]'),LARGEST.replace('reverse=True','reverse=False')],['Compares lexicographically without first maximizing digit count.','Sorts chosen digits ascending, producing a smaller number.'],largest_o,rlargest,['DP over each achievable total cost, storing its best digit string.','Extend a prior exact-cost state with every digit whose cost fits.','Compare candidates first by length, then lexicographically, and keep digits descending.','Longer positive integers are always larger; for equal lengths lexicographic order is numeric order.'],'O(target²*9)','O(target²)',8),
1450:S('active_students_at_time',[('start_time','list[int]'),('end_time','list[int]'),('query_time','int')],'int',['arrays','intervals'],['Student i works throughout the inclusive interval start_time[i] through end_time[i].','Count students active at query_time.'],[([[1,2,3],[3,2,7],4],'Only the third student’s interval includes time four.'),([[4],[4],4],'Both endpoints are inclusive, so the student is active.')],[[s,e,q] for s,e,q in [([1],[1],1),([1],[2],2),([1],[2],3),([1,2,3],[3,2,7],4),([4],[4],4),([1,1],[1,1],1),([1,5],[3,7],4),([1,5],[3,7],5),([2,4,6],[8,8,8],8),([10,20],[20,30],20),([1,2,3],[1,2,3],2),([0,5,10],[4,9,14],7),([3,3,3],[5,5,5],4),([1,100],[99,100],100)]],STUDENTS,[STUDENTS.replace('start<=query_time<=end','start<query_time<end'),START_ONLY_STUDENTS],['Treats both interval endpoints as exclusive.','Ignores end times and counts every student who has started.'],students_o,rstudent,['Pair corresponding start and end values.','Test the inclusive condition start <= query <= end.','Count each true condition.','Intervals are independent, so the sum of membership indicators is exactly the number active.'],'O(n)','O(1)',3),
1451:S('rearrange_sentence_by_length',[('text','str')],'str',['strings','stable-sorting'],['Words are separated by single spaces; only the sentence’s first letter is uppercase.','Sort words by nondecreasing length, preserving original order for ties, then capitalize only the output’s first letter.'],[(['Leetcode is cool'],'Lengths place is first, then cool, then leetcode.'),(['Keep calm and code on'],'Stable sorting keeps calm before code among four-letter words.')],[[s] for s in ['A','Leetcode is cool','Keep calm and code on','To be or not to be','Python makes study fun','I love coding','Same size word test','One three five seven','Z aa bbb cccc','This is a sentence','Code practice lab','We go now','Stable ties stay ordered','Hello world']],ARRANGE,[ARRANGE.replace('sorted(words,key=len)','sorted(words,key=len,reverse=True)'),ARRANGE.replace('text.lower()','text')],['Sorts longest words first.','Leaves the original initial uppercase letter attached to its moved word.'],arrange_o,rarrange,['Lowercase the source before moving words.','Use a stable sort keyed only by word length.','Join with single spaces and uppercase the first output character.','Python’s stable sort preserves original order among equal-length words exactly as required.'],'O(n log n)','O(n)',5),
1452:S('non_subset_company_people',[('favorite_companies','list[list[str]]')],'list[int]',['sets','arrays'],['Each person lists distinct company names.','Return ascending indices whose list is not a subset of any other person’s list.'],[([[['leetcode','google','facebook'],['google','microsoft'],['google','facebook'],['google'],['amazon']]],'Indices zero, one, and four are not contained in another list.'),([[['a'],['a','b'],['c']]],'The first list is excluded as a subset; indices one and two remain.')],[[x] for x in [[['a'],['b']],[['a'],['a','b']],[['a','b'],['a']],[['a'],['a','b'],['c']],[['leetcode','google','facebook'],['google','microsoft'],['google','facebook'],['google'],['amazon']],[['a','b'],['b','c'],['a','c']],[['x'],['x'],['y']],[['a','b','c'],['a','b'],['a']],[['one'],['two','three'],['three']],[['a','d'],['a','b','c'],['d','e']],[['m','n'],['m','n','o'],['p','q']],[['z'],['a','z'],['a','b','z']],[['a','b'],['a','b','c'],['b','c','d'],['e']],[['solo'],['pair','two']]]],COMPANIES,[COMPANIES.replace('group<=other','group<other'),COMPANIES.replace('i!=j and ','')],['Uses strict subset and keeps duplicate-equal lists.','Allows each set to match itself, removing every person.'],companies_o,rcompany,['Convert each favorite list to a set.','For each person, test containment in every different person’s set.','Keep the index only when no such superset exists.','Set <= handles both proper and equal subsets, while the distinct-index check avoids self-containment.'],'O(p²*c)','O(p*c)',5),
1455:S('first_prefix_word',[('sentence','str'),('search_word','str')],'int',['strings','search'],['Return the one-based index of the first sentence word beginning with search_word.','Return -1 when no word has that prefix.'],[(['i love eating burger','burg'],'burger is the fourth word and begins with burg.'),(['this problem is an easy problem','pro'],'problem is the second word, the earliest matching prefix.')],[[s,w] for s,w in [('a','a'),('a','b'),('i love eating burger','burg'),('this problem is an easy problem','pro'),('i am tired','you'),('hello world','hell'),('hello world','world'),('one two three','t'),('prefix prelude','pre'),('same same','same'),('abc ab','abcd'),('look for word','w'),('x y z','z'),('alpha beta gamma','a')]],PREFIX,[PREFIX.replace('enumerate(sentence.split(),1)','enumerate(sentence.split())'),PREFIX.replace('word.startswith(search_word)','search_word.startswith(word)')],['Returns zero-based word indices.','Reverses the prefix relationship.'],prefix_o,rprefix,['Split the sentence into words in order.','Enumerate starting at one.','Return immediately for the first word whose startswith test succeeds.','If the scan ends, no qualifying word exists and -1 is required.'],'O(sentence length)','O(sentence length)',3),
1456:S('maximum_vowels_in_window',[('s','str'),('k','int')],'int',['sliding-window','strings'],['Count lowercase vowels a,e,i,o,u in every length-k substring.','Return the maximum count.'],[(['abciiidef',3],'The substring iii contains three vowels.'),(['aeiou',2],'Every adjacent pair contains two vowels.')],[[s,k] for s,k in [('a',1),('b',1),('abciiidef',3),('aeiou',2),('leetcode',3),('rhythms',4),('aaaaa',5),('abcde',5),('weallloveyou',7),('tryhard',2),('uoiea',3),('abababab',4),('xyzabc',3),('education',4)]],VOWELS,[VOWELS.replace("set('aeiou')","set('aeio')"),VOWELS.replace('s[right-k]','s[right-k+1]')],['Omits u from the vowel set.','Removes the wrong outgoing character while sliding.'],vowels_o,rvowels,['Count vowels in the initial length-k window.','Slide one character at a time, adding the entrant and subtracting the character k positions behind.','Track the largest current count.','Every length-k substring appears once as the maintained window.'],'O(n)','O(1)',5),
1457:S('count_pseudo_palindromic_paths',[('root','TreeNode | None')],'int',['trees','recursion','bit-manipulation'],['Node values are digits one through nine.','Count root-to-leaf paths whose values can be permuted into a palindrome.'],[([[2,3,1,3,1,None,1]],'Two leaf paths have at most one digit with odd frequency.'),([[2,1,1,1,3,None,None,None,None,None,1]],'Exactly one root-to-leaf multiset is pseudo-palindromic.')],[[t] for t in [[1],[1,1],[1,2],[2,3,1,3,1,None,1],[2,1,1,1,3,None,None,None,None,None,1],[1,2,3],[1,2,2],[2,2,2,2,2],[9,8,9,None,8],[1,2,None,2],[3,3,1,1,1],[4,5,4,5,None,None,4],[7,7,8,8,7],[1,2,3,2,3,2,3]]],PATHS,[PATHS.replace('mask&(mask-1)==0','mask==0'),PATHS.replace('mask^=1<<node.val','mask|=1<<node.val')],['Accepts only paths with zero odd counts, rejecting valid odd-length palindromes.','Records presence rather than parity, so repeated digits never cancel.'],paths_o,rpaths,['Toggle one bit for each node digit while descending.','At a leaf, a palindrome permutation is possible when at most one count is odd.','A bit mask has at most one set bit exactly when mask & (mask-1) equals zero.','Backtracking by value-passed masks keeps each root-to-leaf parity state independent.'],'O(n)','O(height)',5),
}
for pid in (1448,1457):BATCH[pid]['params'][0]=('root','TreeNode | None','treenode')
