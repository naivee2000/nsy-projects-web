"""First half of batch 93: bounded strings, games, counting, and tables."""
from collections import Counter
from functools import lru_cache
from itertools import product
import re
from .import_batch_055 import entry

MOD=1_000_000_007
def good_o(a):
 n,lo,hi,bad=a
 alphabet='abcdefghijklmnopqrstuvwxyz'
 if n<=2:
  return sum(lo<=word<=hi and bad not in word
             for letters in product(alphabet,repeat=n)
             for word in (''.join(letters),))%MOD
 transitions={}
 for matched in range(len(bad)):
  for character in alphabet:
   suffix=bad[:matched]+character
   transitions[matched,character]=max(
    length for length in range(len(bad)+1) if suffix.endswith(bad[:length]))
 def at_most(bound):
  states={(0,True):1}
  for upper in bound:
   following={}
   for (matched,tight),count in states.items():
    for character in alphabet:
     if tight and character>upper:break
     next_matched=transitions[matched,character]
     if next_matched==len(bad):continue
     key=(next_matched,tight and character==upper)
     following[key]=(following.get(key,0)+count)%MOD
   states=following
  return sum(states.values())%MOD
 return (at_most(hi)-at_most(lo)+int(bad not in lo))%MOD
def stones_o(a):
 v=a[0]
 @lru_cache(None)
 def play(i):return max((sum(v[i:j])-play(j) for j in range(i+1,min(len(v),i+3)+1)),default=0)
 score=play(0);return 'Alice' if score>0 else 'Bob' if score<0 else 'Tie'
def queries_o(a):
 q,m=a;p=list(range(1,m+1));out=[]
 for x in q:i=p.index(x);out.append(i);p.pop(i);p.insert(0,x)
 return out
ENT={'quot':'"','apos':"'",'amp':'&','gt':'>','lt':'<','frasl':'/'}
def entity_o(a):return re.sub(r'&(quot|apos|amp|gt|lt|frasl);',lambda m:ENT[m.group(1)],a[0])
def paint_o(a):
 n=a[0];rows=[x for x in product(range(3),repeat=3) if x[0]!=x[1] and x[1]!=x[2]];counts={row:1 for row in rows}
 for _ in range(1,n):counts={row:sum(count for old,count in counts.items() if all(x!=y for x,y in zip(row,old)))%MOD for row in rows}
 return sum(counts.values())%MOD
def start_o(a):
 for start in range(1,1000):
  total=start
  if all((total:=total+x)>=1 for x in a[0]):return start
def fib_o(a):
 k=a[0];coins=[1,2]
 while coins[-1]<k:coins.append(coins[-1]+coins[-2])
 dp=[0]+[k+1]*k
 for value in range(1,k+1):dp[value]=1+min(dp[value-c] for c in coins if c<=value)
 return dp[k]
def happy_o(a):
 n,k=a;words=[''.join(w) for w in product('abc',repeat=n) if all(w[i]!=w[i-1] for i in range(1,n))];return words[k-1] if k<=len(words) else ''
def restore_o(a):
 s,k=a
 @lru_cache(None)
 def ways(i):
  if i==len(s):return 1
  if s[i]=='0':return 0
  total=0
  for j in range(i+1,len(s)+1):
   if int(s[i:j])>k:break
   total+=ways(j)
  return total%MOD
 return ways(0)
def table_o(a):
 orders=a[0];foods=sorted({x[2] for x in orders});counts=Counter((x[1],x[2]) for x in orders)
 return [['Table',*foods]]+[[table,*[str(counts[table,food]) for food in foods]] for table in sorted({x[1] for x in orders},key=int)]

def rgood(r):
 n=r.randint(1,2);a=''.join(r.choice('abc') for _ in range(n));b=''.join(r.choice('abc') for _ in range(n));lo,hi=sorted((a,b));return [n,lo,hi,''.join(r.choice('abc') for _ in range(r.randint(1,n)))]
def rstone(r):return [[r.randint(-20,20) for _ in range(r.randint(1,12))]]
def rquery(r):
 m=r.randint(1,15);return [[r.randint(1,m) for _ in range(r.randint(1,20))],m]
def rent(r):
 tokens=list(ENT)+['bad','x'];return [''.join(r.choice(['text',' ','&'+r.choice(tokens)+';']) for _ in range(r.randint(1,15)))]
def rpaint(r):return [r.randint(1,5)]
def rstart(r):return [[r.randint(-20,20) for _ in range(r.randint(1,30))]]
def rfib(r):return [r.randint(1,200)]
def rhappy(r):
 n=r.randint(1,8);return [n,r.randint(1,3*(2**(n-1))+5)]
def rrestore(r):return [''.join(r.choice('0123456789') for _ in range(r.randint(1,12))),r.randint(1,10000)]
def rtable(r):
 foods=['Rice','Soup','Tea','Cake','Fish'];return [[[f'C{i}',str(r.randint(1,12)),r.choice(foods)] for i in range(r.randint(1,25))]]

GOOD='''def count_good_strings_between(n, s1, s2, evil):
 from functools import lru_cache
 mod=1000000007;lps=[0]*len(evil)
 for i in range(1,len(evil)):
  j=lps[i-1]
  while j and evil[i]!=evil[j]:j=lps[j-1]
  if evil[i]==evil[j]:j+=1
  lps[i]=j
 @lru_cache(None)
 def solve(pos,matched,low,high):
  if matched==len(evil):return 0
  if pos==n:return 1
  answer=0;first=s1[pos] if low else 'a';last=s2[pos] if high else 'z'
  for code in range(ord(first),ord(last)+1):
   char=chr(code);state=matched
   while state and evil[state]!=char:state=lps[state-1]
   if evil[state]==char:state+=1
   answer+=solve(pos+1,state,low and char==first,high and char==last)
  return answer%mod
 return solve(0,0,True,True)
'''
STONES='''def stone_game_three(stone_value):
 n=len(stone_value);best=[0]*(n+1)
 for i in range(n-1,-1,-1):
  taken=0;best[i]=-10**18
  for j in range(i,min(n,i+3)):
   taken+=stone_value[j];best[i]=max(best[i],taken-best[j+1])
 return 'Alice' if best[0]>0 else 'Bob' if best[0]<0 else 'Tie'
'''
QUERIES='''def process_permutation_queries(queries, m):
 permutation=list(range(1,m+1));answer=[]
 for value in queries:
  index=permutation.index(value);answer.append(index);permutation.pop(index);permutation.insert(0,value)
 return answer
'''
ENTITY='''def parse_html_entities(text):
 entities={'&quot;':'"','&apos;':"'",'&amp;':'&','&gt;':'>','&lt;':'<','&frasl;':'/'};answer=[];i=0
 while i<len(text):
  match=next((key for key in entities if text.startswith(key,i)),None)
  if match:answer.append(entities[match]);i+=len(match)
  else:answer.append(text[i]);i+=1
 return ''.join(answer)
'''
PAINT='''def paint_n_by_three_grid(n):
 mod=1000000007;same=different=6
 for _ in range(1,n):same,different=(3*same+2*different)%mod,(2*same+2*different)%mod
 return (same+different)%mod
'''
START='''def minimum_positive_start(nums):
 prefix=lowest=0
 for value in nums:prefix+=value;lowest=min(lowest,prefix)
 return 1-lowest
'''
FIB='''def minimum_fibonacci_count(k):
 numbers=[1,2]
 while numbers[-1]<k:numbers.append(numbers[-1]+numbers[-2])
 answer=0
 for value in reversed(numbers):
  if value<=k:k-=value;answer+=1
 return answer
'''
HAPPY='''def kth_happy_string(n, k):
 answer=[]
 def build(path):
  if len(path)==n:answer.append(path);return
  for char in 'abc':
   if not path or path[-1]!=char:build(path+char)
 build('')
 return answer[k-1] if k<=len(answer) else ''
'''
RESTORE='''def count_array_restorations(s, k):
 mod=1000000007;n=len(s);ways=[0]*(n+1);ways[n]=1
 for i in range(n-1,-1,-1):
  if s[i]=='0':continue
  value=0
  for j in range(i,n):
   value=value*10+int(s[j])
   if value>k:break
   ways[i]=(ways[i]+ways[j+1])%mod
 return ways[0]
'''
TABLE='''def display_food_orders(orders):
 from collections import Counter
 foods=sorted({food for _,_,food in orders});counts=Counter((table,food) for _,table,food in orders)
 return [['Table']+foods]+[[table]+[str(counts[table,food]) for food in foods] for table in sorted({table for _,table,_ in orders},key=int)]
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1397:S('count_good_strings_between',[('n','int'),('s1','str'),('s2','str'),('evil','str')],'int',['dynamic-programming','strings','kmp'],['s1 and s2 are lowercase strings of length n with s1 <= s2.','Count strings in that inclusive range that do not contain evil; return modulo 1,000,000,007.'],[([2,'aa','da','b'],'Among the 79 strings from aa through da, exactly 28 contain b, leaving 51.'),([2,'gx','gz','x'],'gx is excluded, while gy and gz are valid, giving two.')],[[*x] for x in [(1,'a','z','a'),(1,'a','z','z'),(2,'aa','aa','b'),(2,'aa','ab','b'),(2,'aa','da','b'),(2,'gx','gz','x'),(3,'aaa','azz','aa'),(3,'abc','acd','bc'),(3,'aaa','zzz','zz'),(4,'aaaa','aaaz','aaa'),(4,'abab','acac','ba'),(5,'aaaaa','aazzz','abc'),(6,'aaaaaa','aaaazz','z'),(10,'aaaaaaaaaa','zzzzzzzzzz','evil')]],GOOD,[GOOD.replace("return solve(0,0,True,True)","return solve(0,0,False,False)"),GOOD.replace('if matched==len(evil):return 0','if matched==len(evil):return 1')],['Ignores both lexical boundaries and counts the entire length-n domain.','Counts strings after the forbidden substring has already appeared.'],good_o,rgood,['Track position, matched evil-prefix length, and whether each lexical bound is still tight.','Use the KMP failure table to update the forbidden-prefix state for each next character.','Return zero immediately when all of evil has matched.','These states contain exactly the history needed for range membership and forbidden-substring detection.'],'O(n*len(evil)*26)','O(n*len(evil))',9),
1406:S('stone_game_three',[('stone_value','list[int]')],'str',['dynamic-programming','games'],['Alice and Bob alternately take one, two, or three leading remaining stones.','Each maximizes their final score difference; return Alice, Bob, or Tie.'],[([[1,2,3,7]],'Alice cannot avoid Bob finishing with the larger total.'),([[1,2,3,-9]],'Alice takes the first three stones and wins.')],[[x] for x in [[1],[0],[-1],[1,2],[1,-2],[1,2,3],[1,2,3,7],[1,2,3,-9],[1,2,3,6],[-1,-2,-3],[-1,-2,5],[5,-10,4,3],[0,0,0,0],[2,7,9,4,4]]],STONES,[STONES.replace('min(n,i+3)','min(n,i+1)'),STONES.replace('taken-best[j+1]','taken+best[j+1]')],['Always takes exactly one stone.','Adds the opponent’s advantage instead of subtracting it.'],stones_o,rstone,['Let best[i] be the maximum score difference from suffix i.','Try taking the next one, two, or three values.','A choice yields the taken sum minus best at the remaining suffix.','Optimal play on both sides is captured because subtracting the opponent optimum converts it to the current difference.'],'O(n)','O(n)',8),
1409:S('process_permutation_queries',[('queries','list[int]'),('m','int')],'list[int]',['arrays','simulation'],['Begin with permutation 1 through m.','For each query, record its zero-based position and move that value to the front.'],[([[3,1,2,1],5],'The successive positions are 2, 1, 2, and 1 as queried values move forward.'),([[4,1,2,2],4],'Moving prior queries changes the later position of the repeated two.')],[[q,m] for q,m in [([1],1),([1],5),([5],5),([1,1],2),([2,1],2),([3,1,2,1],5),([4,1,2,2],4),([7,5,5,8,3],8),([1,2,3,4,5],5),([5,4,3,2,1],5),([2,2,2],3),([3,2,1,3],3),([10,1,10],10),([2,4,2,1],4)]],QUERIES,[QUERIES.replace('permutation.insert(0,value)','permutation.append(value)'),QUERIES.replace('answer.append(index)','answer.append(index+1)')],['Moves queried values to the back rather than the front.','Returns one-based rather than zero-based positions.'],queries_o,rquery,['Maintain the current permutation explicitly.','Find the queried value’s current zero-based index.','Remove it and insert it at position zero.','Performing these operations in order exactly mirrors the evolving permutation.'],'O(q*m)','O(m)',5),
1410:S('parse_html_entities',[('text','str')],'str',['strings','parsing'],['Recognize only &quot;, &apos;, &amp;, &gt;, &lt;, and &frasl;.','Unknown or incomplete entity-like text remains unchanged; replacements are not parsed a second time.'],[(['& is an HTML entity but &ambassador; is not.'],'Neither ampersand begins one of the six complete recognized entities.'),(['x &gt; y &amp;&amp; y &lt; z'],'The three recognized tokens become x > y && y < z.')],[[s] for s in ['plain','&amp;','&quot;&apos;','&gt;&lt;','&frasl;','&unknown;','&amp;gt;','&&amp;;','a &amp; b','& is an HTML entity but &ambassador; is not.','Stay &quot;home&quot;.','1 &lt; 2 &amp;&amp; 3 &gt; 2','trailing &amp','&apos;x&apos;']],ENTITY,[ENTITY.replace("'&amp;':'&'","'&amp;':''"),'''def parse_html_entities(text):
 return text.replace('&amp;','&').replace('&gt;','>').replace('&lt;','<').replace('&quot;','"').replace('&apos;',"'").replace('&frasl;','/')
'''],['Deletes recognized ampersand entities.','Repeated replacement wrongly decodes entity text produced by an earlier replacement.'],entity_o,rent,['Scan left to right and test the six complete entity spellings at an ampersand.','Append the mapped character and skip the full token on a match.','Otherwise copy one source character unchanged.','Because consumed source is never rescanned, nested-looking text is decoded only once.'],'O(n)','O(n)',5),
1411:S('paint_n_by_three_grid',[('n','int')],'int',['dynamic-programming','counting'],['Paint an n-by-3 grid with three colors so horizontally and vertically adjacent cells differ.','Return the count modulo 1,000,000,007.'],[([1],'A single row has twelve valid colorings.'),([2],'Combining compatible row patterns gives 54 colorings.')],[[n] for n in [1,2,3,4,5,6,7,8,10,20,50,100,1000,5000]],PAINT,[PAINT.replace('same=different=6','same=different=3'),PAINT.replace('3*same+2*different','2*same+2*different')],['Starts with half of the valid one-row patterns.','Uses the wrong transition count for two-color ABA row patterns.'],paint_o,rpaint,['Classify a valid row as ABA using two colors or ABC using three.','There are six initial patterns of each type.','The next counts are 3*ABA+2*ABC and 2*ABA+2*ABC.','These compatibility counts cover every valid next row and depend only on the prior row type.'],'O(n)','O(1)',8),
1413:S('minimum_positive_start',[('nums','list[int]')],'int',['arrays','prefix-sums'],['Choose the smallest positive start value so every running total stays at least one.','nums may contain positive and negative integers.'],[([[-3,2,-3,4,2]],'The lowest zero-based prefix is -4, so start value five is necessary.'),([[1,2]],'All prefixes are already positive when starting at one.')],[[x] for x in [[1],[-1],[0],[1,2],[-3,2,-3,4,2],[1,-2,-3],[5,-10,6],[-5,-5],[2,-1,2,-1],[-1,1,-1,1],[100,-99],[-100,50,49],[3,-4,2,-3,5],[0,0,0]]],START,[START.replace('return 1-lowest','return -lowest'),START.replace('lowest=min(lowest,prefix)','lowest=max(lowest,prefix)')],['Allows a running total to reach zero.','Tracks the largest rather than smallest prefix sum.'],start_o,rstart,['Compute prefix sums assuming a zero start.','Record the minimum prefix, including the empty prefix zero.','The chosen start must be at least one minus that minimum.','This value makes the lowest adjusted prefix exactly one and any smaller value fail there.'],'O(n)','O(1)',3),
1414:S('minimum_fibonacci_count',[('k','int')],'int',['greedy','math'],['Use Fibonacci numbers starting 1, 2, 3, 5, and so on; values may be reused.','Return the minimum number whose sum is exactly k.'],[([7],'Five plus two reaches seven using two Fibonacci numbers.'),([19],'Thirteen plus five plus one reaches nineteen using three.')],[[k] for k in [1,2,3,4,7,10,19,20,50,99,100,250,500,1000]],FIB,[FIB.replace('reversed(numbers)','numbers'),FIB.replace('answer+=1','answer+=2')],['Greedily tries smallest Fibonacci numbers first.','Counts every selected Fibonacci number twice.'],fib_o,rfib,['Generate Fibonacci values through k.','Repeatedly take the largest value not exceeding the remainder.','Move downward until the remainder is zero.','The Fibonacci recurrence ensures replacing the largest choice cannot use fewer smaller terms.'],'O(log k)','O(log k)',5),
1415:S('kth_happy_string',[('n','int'),('k','int')],'str',['backtracking','strings'],['A happy string uses only a, b, c and has no equal adjacent characters.','Return the one-based kth string in lexicographic order, or empty when k is too large.'],[([1,3],'The length-one order is a, b, c, so the third is c.'),([3,9],'There are twelve length-three happy strings; the ninth is cab.')],[[n,k] for n,k in [(1,1),(1,3),(1,4),(2,1),(2,6),(2,7),(3,1),(3,9),(3,12),(3,13),(4,5),(5,20),(8,100),(10,1536)]],HAPPY,[HAPPY.replace("for char in 'abc'","for char in 'cba'"),HAPPY.replace('path[-1]!=char','path[-1]==char')],['Generates valid strings in reverse lexicographic order.','Allows only repeated adjacent characters instead of forbidding them.'],happy_o,rhappy,['Build candidates left-to-right in a, b, c order.','Skip a character equal to the current last character.','Each completed length-n path arrives in lexicographic order.','Select index k-1 when present; otherwise the requested rank does not exist.'],'O(3*2^n)','O(2^n)',5),
1416:S('count_array_restorations',[('s','str'),('k','int')],'int',['dynamic-programming','strings'],['Split the digit string into integers from 1 through k with no leading zeroes.','Return the number of splits modulo 1,000,000,007.'],[(['1000',10000],'The whole string as integer 1000 is the only valid restoration.'),(['1000',10],'Every possible piece after the initial one begins with zero, so no restoration exists.')],[[s,k] for s,k in [('1',1),('0',10),('10',10),('10',9),('1000',10000),('1000',10),('1317',2000),('2020',30),('1111',11),('123',100),('999',9),('10101',101),('123456',1000),('1111111111',1000000000)]],RESTORE,[RESTORE.replace("if s[i]=='0':continue",''),RESTORE.replace('if value>k:break','if value>=k:break')],['Allows pieces with leading zeroes.','Rejects pieces exactly equal to k.'],restore_o,rrestore,['Let ways[i] count valid splits of the suffix beginning at i.','A suffix beginning with zero contributes none.','Extend a numeric piece until it exceeds k, adding ways after each valid endpoint.','Every restoration has a unique first piece, so this partitions the solution set without overlap.'],'O(n log k)','O(n)',8),
1418:S('display_food_orders',[('orders','list[list[str]]')],'list[list[str]]',['counting','sorting'],['Each order is [customer, table-number string, food].','Return a header with foods alphabetically, then numeric table rows with decimal count strings.'],[([[['David','3','Ceviche'],['Corina','10','Beef Burrito'],['David','3','Fried Chicken']]],'The header sorts the three foods; table 3 precedes table 10 and missing counts are zero.'),([[['A','2','Tea'],['B','2','Tea'],['C','1','Cake']]],'Table one precedes table two, with Cake before Tea in the header.')],[[o] for o in [[['A','1','Tea']],[['A','2','Tea'],['B','2','Tea']],[['A','10','Rice'],['B','2','Soup']],[['A','1','Z'],['B','1','A']],[['A','3','Cake'],['B','3','Tea'],['C','3','Cake']],[['David','3','Ceviche'],['Corina','10','Beef Burrito'],['David','3','Fried Chicken']],[['A','2','Tea'],['B','2','Tea'],['C','1','Cake']],[['A','12','Fish'],['B','3','Fish'],['C','3','Rice']],[['X','5','Soup'],['Y','5','Soup'],['Z','5','Soup']],[['A','9','B'],['B','10','A'],['C','9','A']],[['A','1','Tea'],['A','1','Tea'],['A','1','Cake']],[['N','100','Rice'],['M','1','Rice']],[['A','4','X'],['B','2','Y'],['C','3','Z']],[['A','7','Soup'],['B','7','Cake'],['C','8','Soup']]]],TABLE,[TABLE.replace('key=int',''),TABLE.replace("foods=sorted({food for _,_,food in orders})","foods=list({food for _,_,food in orders})")],['Sorts table-number strings lexicographically instead of numerically.','Leaves food columns in arbitrary encounter/set order.'],table_o,rtable,['Collect and alphabetically sort every distinct food name.','Count orders by the pair (table, food).','Sort distinct table strings using their integer values.','Emit zero for absent pairs so every row aligns with the shared header.'],'O(n log n)','O(n)',5),
}
