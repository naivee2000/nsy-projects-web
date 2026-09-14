"""Final group of batch 103: sets, combinatorics, strings, and prefix XOR."""
from collections import Counter
from itertools import product
from math import comb
from .import_batch_055 import entry
MOD=1_000_000_007
def teaching_o(a):
 n,languages,friendships=a;bad=[(x-1,y-1) for x,y in friendships if not set(languages[x-1])&set(languages[y-1])]
 if not bad:return 0
 people=set(sum(([x,y] for x,y in bad),[]));return min(sum(lang not in languages[p] for p in people) for lang in range(1,n+1))
def products_o(a):
 def ways(n,k):
  @__import__('functools').lru_cache(None)
  def build(left,remaining):
   if left==1:return 1
   return sum(build(left-1,remaining//d) for d in range(1,remaining+1) if remaining%d==0)
  return build(n,k)
 return [ways(n,k)%MOD for n,k in a[0]]
def time_o(a):
 pattern=a[0];answer=''
 for h in range(24):
  for m in range(60):
   candidate=f'{h:02d}:{m:02d}'
   if all(x=='?' or x==y for x,y in zip(pattern,candidate)):answer=max(answer,candidate)
 return answer
def changes_o(a):
 first,second=a;best=len(first)+len(second)
 for boundary in range(25):
  best=min(best,sum(ord(c)-97>boundary for c in first)+sum(ord(c)-97<=boundary for c in second))
  best=min(best,sum(ord(c)-97>boundary for c in second)+sum(ord(c)-97<=boundary for c in first))
 for letter in range(26):best=min(best,sum(ord(c)-97!=letter for c in first+second))
 return best
def xorvalue_o(a):
 matrix,k=a;rows=len(matrix);cols=len(matrix[0]);values=[]
 for r in range(rows):
  for c in range(cols):
   value=0
   for i in range(r+1):
    for j in range(c+1):value^=matrix[i][j]
   values.append(value)
 return sorted(values,reverse=True)[k-1]
def rteach(r):
 people=r.randint(2,8);n=r.randint(1,6);languages=[r.sample(range(1,n+1),r.randint(1,n)) for _ in range(people)];friends=[[i,j] for i in range(1,people+1) for j in range(i+1,people+1) if r.random()<.3];return [n,languages,friends]
def rproducts(r):return [[[r.randint(1,5),r.randint(1,30)] for _ in range(r.randint(1,6))]]
def rtime(r):
 valid=f'{r.randrange(24):02d}:{r.randrange(60):02d}';return [''.join(c if c==':' else '?' if r.random()<.55 else c for c in valid)]
def rchanges(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,10))),''.join(r.choice('abcde') for _ in range(r.randint(1,10)))]
def rxorvalue(r):
 rows,cols=r.randint(1,5),r.randint(1,5);matrix=[[r.randint(0,31) for _ in range(cols)] for _ in range(rows)];return [matrix,r.randint(1,rows*cols)]
TEACH='''def minimum_language_teachings(n, languages, friendships):
 known=[set(items) for items in languages];people=set()
 for left,right in friendships:
  left-=1;right-=1
  if not known[left]&known[right]:people.add(left);people.add(right)
 if not people:return 0
 return min(sum(language not in known[person] for person in people) for language in range(1,n+1))
'''
PRODUCTS='''def product_array_counts(queries):
 from math import comb
 answer=[]
 for length,value in queries:
  ways=1;divisor=2
  while divisor*divisor<=value:
   exponent=0
   while value%divisor==0:value//=divisor;exponent+=1
   if exponent:ways=ways*comb(exponent+length-1,exponent)%1000000007
   divisor+=1
  if value>1:ways=ways*length%1000000007
  answer.append(ways)
 return answer
'''
TIME='''def latest_valid_time(pattern):
 chars=list(pattern)
 if chars[0]=='?':chars[0]='2' if chars[1] in '?0123' else '1'
 if chars[1]=='?':chars[1]='3' if chars[0]=='2' else '9'
 if chars[3]=='?':chars[3]='5'
 if chars[4]=='?':chars[4]='9'
 return ''.join(chars)
'''
CHANGES='''def minimum_alphabet_condition_changes(a, b):
 count_a=Counter(a);count_b=Counter(b);answer=len(a)+len(b)
 for boundary in range(25):
  answer=min(answer,sum(count_a[chr(97+i)] for i in range(boundary+1,26))+sum(count_b[chr(97+i)] for i in range(boundary+1)))
  answer=min(answer,sum(count_b[chr(97+i)] for i in range(boundary+1,26))+sum(count_a[chr(97+i)] for i in range(boundary+1)))
 for letter in range(26):answer=min(answer,len(a)+len(b)-count_a[chr(97+letter)]-count_b[chr(97+letter)])
 return answer
'''
XORVALUE='''def kth_largest_coordinate_xor(matrix, k):
 rows,cols=len(matrix),len(matrix[0]);prefix=[[0]*(cols+1) for _ in range(rows+1)];values=[]
 for r in range(1,rows+1):
  for c in range(1,cols+1):
   prefix[r][c]=matrix[r-1][c-1]^prefix[r-1][c]^prefix[r][c-1]^prefix[r-1][c-1];values.append(prefix[r][c])
 return sorted(values,reverse=True)[k-1]
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1733:E('minimum_language_teachings',[('n','int'),('languages','list[list[int]]'),('friendships','list[list[int]]')],'int',['sets','greedy'],['People are one-indexed; languages[i] lists the languages person i+1 knows.','Choose one language and teach it to the fewest people so every friendship has a shared language.'],[([2,[[1],[2],[1,2]],[[1,2],[1,3],[2,3]]],'Only people one and two in the failing friendship need consideration; teaching either one person suffices.'),([3,[[2],[1,3],[1,2],[3]],[[1,4],[1,2],[3,4],[2,3]]],'Teaching language three to people one and three repairs all failing friendships, requiring two people.')],[[*x] for x in [(1,[[1],[1]],[[1,2]]),(2,[[1],[2]],[[1,2]]),(2,[[1,2],[2]],[[1,2]]),(3,[[1],[2],[3]],[[1,2],[2,3]]),(3,[[1,2],[2,3],[1,3]],[[1,2],[2,3],[1,3]]),(2,[[1],[1],[2]],[[1,2],[2,3]]),(4,[[1],[2],[3],[4]],[[1,2],[3,4]]),(3,[[1,3],[2],[2,3]],[[1,2],[2,3]]),(2,[[1],[2],[1,2]],[[1,2],[1,3],[2,3]]),(3,[[2],[1,3],[1,2],[3]],[[1,4],[1,2],[3,4],[2,3]]),(2,[[1],[2]],[]),(3,[[1,2],[2],[3]],[[1,2],[2,3]]),(3,[[1],[1],[1]],[[1,2],[2,3]]),(3,[[1],[2],[3],[1,2,3]],[[1,2],[2,3],[3,4]])]],TEACH,[TEACH.replace('if not known[left]&known[right]','if known[left]&known[right]'),TEACH.replace('people.add(left);people.add(right)','people.add(left)')],['Selects already-working friendships instead of the friendships that lack a common language.','Considers only one endpoint of each failing friendship.'],teaching_o,rteach,L('People outside failing friendships never need teaching.','Collect both endpoints of every friendship with disjoint language sets, then try each language.','For a candidate language, count collected people who do not know it; return the minimum.','Teaching that set repairs every failing edge, and any valid single-language plan must teach each collected non-speaker.'),'O(friendships*languages+n*people)','O(people*languages)',5),
1735:E('product_array_counts',[('queries','list[list[int]]')],'list[int]',['math','combinatorics'],['For each [n,k], count positive integer arrays of length n whose product is k.','Return each count modulo 1,000,000,007.'],[([[[2,6],[5,1],[73,660]]],'The first query has four ordered factor pairs; product one has one array, and the large query is reduced by prime exponents.'),([[[1,1],[1,7],[3,4]]],'Length-one queries have one choice; distributing two factors of two across three positions gives six arrays.')],[[q] for q in [[[2,6]],[[5,1]],[[1,1],[1,7],[3,4]],[[2,4]],[[3,8]],[[4,16]],[[2,12]],[[3,12]],[[5,6]],[[2,25]],[[4,9]],[[3,30]],[[1,30]],[[2,2],[3,3],[4,5]]]],PRODUCTS,[PRODUCTS.replace('exponent+length-1','exponent+length-2'),PRODUCTS.replace('if value>1:ways=ways*length','if value>1:ways=ways*(length+1)')],['Uses one too few allocation slots for each prime exponent.','Counts an extra position when a prime factor remains after trial division.'],products_o,rproducts,L('Prime factors can be distributed independently among array positions.','Factor k; for exponent e, stars-and-bars gives C(e+n-1,e) distributions.','Multiply those combinations for every prime exponent and reduce modulo M.','Unique prime factorization makes every exponent allocation correspond to exactly one array and prevents double counting.'),'O(queries*sqrt(k))','O(1)',8),
1736:E('latest_valid_time',[('pattern','str')],'str',['strings','greedy'],['pattern has HH:MM form with digits or question marks and admits at least one 24-hour time.','Replace every question mark to produce the latest valid time.'],[(['2?:?0'],'Hour ones can be three and minute tens five, giving 23:50.'),(['0?:3?'],'The latest matching time is 09:39.')],[[s] for s in ['??:??','2?:?0','0?:3?','?4:??','1?:??','?3:?9','23:59','00:00','??:00','??:59','2?:59','?9:??','1?:4?','0?:??']],TIME,[TIME.replace("chars[3]='5'","chars[3]='6'"),TIME.replace("chars[1]='3' if chars[0]=='2' else '9'","chars[1]='9'")],['Produces an invalid minute-tens digit six.','Allows hour 29 when the first digit is two.'],time_o,rtime,L('Earlier positions dominate lexicographic and chronological order.','Choose the largest digit that keeps each partially fixed field valid.','Resolve hour tens using hour ones, then hour ones using hour tens; set minute digits to five and nine.','Every choice is the largest feasible at the first still-unknown position, so no later valid time can exceed it.'),'O(1)','O(1)',3),
1737:E('minimum_alphabet_condition_changes',[('a','str'),('b','str')],'int',['strings','prefix-counts'],['Strings contain lowercase English letters.','Minimize replacements so every a character is less than every b character, every b character is less than every a character, or both strings contain only one shared letter.'],[(['aba','caa'],'Changing two letters can make every character in a smaller than every character in b.'),(['dabadd','cda'],'The minimum across the two ordering directions and one-letter condition is three.')],[[*x] for x in [('aba','caa'),('dabadd','cda'),('a','b'),('b','a'),('a','a'),('abc','abc'),('zzz','aaa'),('aaa','zzz'),('ab','cd'),('xy','yz'),('aaaa','bbbb'),('abcd','zzzz'),('mnop','lmno'),('leetcode','practice')]],CHANGES,[CHANGES.replace('range(25)','range(24)'),CHANGES.replace('for letter in range(26)','for letter in range(25)')],['Never considers the boundary between y and z.','Never considers changing both strings entirely to z.'],changes_o,rchanges,L('The first two conditions are determined by one alphabet boundary; the third by one chosen letter.','Count letters, try all 25 boundaries in both directions, then all 26 shared letters.','For boundary c, replace a letters above c and b letters at or below c; reverse for condition two.','Every valid ordered pair has a boundary, and every one-letter result has a chosen letter, so the exhaustive 51 candidates include the optimum.'),'O(len(a)+len(b)+alphabet^2)','O(alphabet)',5),
1738:E('kth_largest_coordinate_xor',[('matrix','list[list[int]]'),('k','int')],'int',['matrices','prefix-xor','sorting'],['For coordinate (r,c), XOR every matrix value in rows 0..r and columns 0..c.','Return the kth largest coordinate value, counting duplicate coordinates separately.'],[([[[5,2],[1,6]],1],'Coordinate XOR values are 5,7,4,0, so the largest is seven.'),([[[5,2],[1,6]],4],'The fourth largest coordinate XOR value is zero.')],[[*x] for x in [([[5,2],[1,6]],1),([[5,2],[1,6]],4),([[1]],1),([[0]],1),([[1,2]],1),([[1,2]],2),([[1],[2]],2),([[1,1],[1,1]],3),([[0,1],[2,3]],2),([[7,4,2],[1,3,5]],4),([[2,2,2],[2,2,2]],6),([[31,0],[0,31]],2),([[1,2,3],[4,5,6],[7,8,9]],5),([[9,8,7],[6,5,4]],3)]],XORVALUE,[XORVALUE.replace('prefix[r-1][c-1]','0'),XORVALUE.replace('[k-1]','[k]')],['Omits the overlapping prefix term required by XOR inclusion-exclusion.','Uses k as a zero-based index and returns the next smaller value.'],xorvalue_o,rxorvalue,L('A two-dimensional XOR prefix has the same overlap cancellation pattern as a sum prefix.','Build prefix[r][c] from the cell, upper prefix, left prefix, and diagonal prefix.','Collect every coordinate prefix, sort descending, and return index k-1.','Each prior cell appears exactly once after XOR cancellation, and sorting gives the requested coordinate rank.'),'O(rows*columns log(rows*columns))','O(rows*columns)',5),
}
BATCH[1736]['params']=[('time','str','raw')]
BATCH[1737]['wrong'][0]=CHANGES.replace('for boundary in range(25):','for boundary in range(1,25):')
BATCH[1737]['wrong_reasons'][0]='Skips the a/b alphabet boundary, missing already ordered strings such as a and b.'
BATCH[1737]['wrong'][1]=CHANGES.replace('return answer','return max(0,answer-1)')
BATCH[1737]['wrong_reasons'][1]='Subtracts one from the computed replacement count through an off-by-one mistake.'
