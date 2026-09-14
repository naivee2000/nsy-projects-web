"""Completion of batch 93: sequence DP, windows, diagonals, and simulations."""
from collections import Counter, deque
from itertools import product
from .import_batch_055 import entry

MOD=1_000_000_007
def frogs_o(a):
 s=a[0];stage={c:[] for c in 'croak'};active=best=0;counts=[0]*5
 for ch in s:
  i='croak'.find(ch)
  if i<0 or (i and counts[i-1]==0):return -1
  if i:counts[i-1]-=1
  counts[i]+=1
  if i==0:active+=1;best=max(best,active)
  if i==4:counts[i]-=1;active-=1
 return best if active==0 else -1
def arrays_o(a):
 n,m,k=a;return sum(sum(max(w[:i+1])>max(w[:i]) for i in range(1,n)) + 1==k for w in product(range(1,m+1),repeat=n))%MOD
def split_o(a):
 s=a[0];return max(s[:i].count('0')+s[i:].count('1') for i in range(1,len(s)))
def cards_o(a):
 cards,k=a;n=len(cards);return max(sum(cards[:left])+sum(cards[n-(k-left):] if k-left else []) for left in range(k+1))
def diagonal_o(a):
 nums=a[0];items=[(i+j,-i,x) for i,row in enumerate(nums) for j,x in enumerate(row)];return [x for _,_,x in sorted(items)]
def constrained_o(a):
 nums,k=a;dp=[]
 for i,x in enumerate(nums):dp.append(x+max(0,max(dp[max(0,i-k):i],default=0)))
 return max(dp)
def elements_o(a):
 arr=a[0];values=set(arr);return sum(x+1 in values for x in arr)
def shifts_o(a):
 s,ops=a;amount=sum(x if direction else -x for direction,x in ops)%len(s);return s[-amount:]+s[:-amount] if amount else s
def candies_o(a):
 values,extra=a;largest=max(values);return [x+extra>=largest for x in values]
def difference_o(a):
 text=str(a[0]);values=[]
 for old in '0123456789':
  for new in '0123456789':
   changed=text.replace(old,new)
   if changed[0]!='0':values.append(int(changed))
 return max(values)-min(values)
def break_o(a):
 x,y=map(sorted,a);return all(i>=j for i,j in zip(x,y)) or all(i<=j for i,j in zip(x,y))

def rfrog(r):return [''.join(r.choice('croak') for _ in range(r.randint(1,30)))]
def rarray(r):return [r.randint(1,5),r.randint(1,5),r.randint(1,5)]
def rsplit(r):return [''.join(r.choice('01') for _ in range(r.randint(2,40)))]
def rcard(r):
 v=[r.randint(1,50) for _ in range(r.randint(1,20))];return [v,r.randint(1,len(v))]
def rdiag(r):return [[[r.randint(-20,20) for _ in range(r.randint(1,8))] for _ in range(r.randint(1,8))]]
def rcon(r):
 v=[r.randint(-30,30) for _ in range(r.randint(1,30))];return [v,r.randint(1,len(v))]
def relem(r):return [[r.randint(0,20) for _ in range(r.randint(1,40))]]
def rshift(r):
 s=''.join(r.choice('abcde') for _ in range(r.randint(1,20)));return [s,[[r.randint(0,1),r.randint(0,50)] for _ in range(r.randint(1,20))]]
def rcandy(r):return [[r.randint(0,30) for _ in range(r.randint(1,20))],r.randint(0,30)]
def rdiff(r):return [r.randint(1,999_999_999)]
def rbreak(r):
 n=r.randint(1,20);return [''.join(r.choice('abcde') for _ in range(n)),''.join(r.choice('abcde') for _ in range(n))]

FROGS='''def minimum_croaking_frogs(croak_of_frogs):
 word='croak';counts=[0]*5;active=answer=0
 for char in croak_of_frogs:
  stage=word.find(char)
  if stage<0 or (stage and counts[stage-1]==0):return -1
  if stage:counts[stage-1]-=1
  counts[stage]+=1
  if stage==0:active+=1;answer=max(answer,active)
  elif stage==4:counts[stage]-=1;active-=1
 return answer if active==0 else -1
'''
ARRAYS='''def count_arrays_with_search_cost(n, m, k):
 mod=1000000007;dp={(0,0):1}
 for _ in range(n):
  new={}
  for (maximum,cost),count in dp.items():
   for value in range(1,m+1):
    state=(max(maximum,value),cost+(value>maximum));new[state]=(new.get(state,0)+count)%mod
  dp=new
 return sum(count for (maximum,cost),count in dp.items() if cost==k)%mod
'''
SPLIT='''def maximum_binary_split_score(s):
 right_ones=s.count('1');left_zeros=answer=0
 for char in s[:-1]:
  if char=='0':left_zeros+=1
  else:right_ones-=1
  answer=max(answer,left_zeros+right_ones)
 return answer
'''
CARDS='''def maximum_card_points(card_points, k):
 current=sum(card_points[:k]);answer=current
 for right in range(1,k+1):current+=card_points[-right]-card_points[k-right];answer=max(answer,current)
 return answer
'''
DIAGONAL='''def diagonal_traverse_jagged(nums):
 diagonals={}
 for row,values in enumerate(nums):
  for column,value in enumerate(values):diagonals.setdefault(row+column,[]).append(value)
 answer=[]
 for key in sorted(diagonals):answer.extend(reversed(diagonals[key]))
 return answer
'''
CONSTRAINED='''def constrained_subsequence_sum(nums, k):
 queue=deque();best=[];answer=-10**18
 for i,value in enumerate(nums):
  while queue and queue[0]<i-k:queue.popleft()
  score=value+max(0,best[queue[0]] if queue else 0);best.append(score);answer=max(answer,score)
  while queue and best[queue[-1]]<=score:queue.pop()
  queue.append(i)
 return answer
'''
ELEMENTS='''def count_elements_with_successor(arr):
 values=set(arr)
 return sum(value+1 in values for value in arr)
'''
SHIFTS='''def apply_string_shifts(s, shift):
 amount=sum(value if direction==1 else -value for direction,value in shift)%len(s)
 return s[-amount:]+s[:-amount] if amount else s
'''
CANDIES='''def kids_with_extra_candies(candies, extra_candies):
 greatest=max(candies)
 return [value+extra_candies>=greatest for value in candies]
'''
DIFFERENCE='''def maximum_remap_difference(num):
 text=str(num);high_digit=next((char for char in text if char!='9'),None);high=text.replace(high_digit,'9') if high_digit else text
 if text[0]!='1':low=text.replace(text[0],'1')
 else:
  low_digit=next((char for char in text[1:] if char not in '01'),None);low=text.replace(low_digit,'0') if low_digit else text
 return int(high)-int(low)
'''
BREAK='''def can_one_string_break(s1, s2):
 first=sorted(s1);second=sorted(s2)
 return all(a>=b for a,b in zip(first,second)) or all(a<=b for a,b in zip(first,second))
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1419:S('minimum_croaking_frogs',[('croak_of_frogs','str')],'int',['strings','simulation'],['The input interleaves zero or more simultaneous copies of the exact word croak.','Return the minimum concurrent frogs, or -1 if the sequence is invalid.'],[(['croakcroak'],'One frog can finish the first croak before starting the second.'),(['crcoakroak'],'Two croaks overlap, so at least two frogs are active.')],[[s] for s in ['croak','croakcroak','crcoakroak','croakcrook','croakcroa','c','croakcroakcroak','ccrrooaakk','croacroakkk','kcroa','croakk','croakcroakx','croakcroakcroa','ccrrooaakkcroak']],FROGS,[FROGS.replace('active+=1','active+=0'),FROGS.replace("return answer if active==0 else -1","return answer")],['Never counts newly active frogs.','Accepts unfinished croaks at the end.'],frogs_o,rfrog,['Track how many frogs currently wait at each stage of c-r-o-a-k.','A non-c letter must consume a frog from the immediately previous stage.','Increment concurrency at c and decrement it at k.','The maximum active count is necessary and sufficient; leftover stages make the input invalid.'],'O(n)','O(1)',5),
1420:S('count_arrays_with_search_cost',[('n','int'),('m','int'),('k','int')],'int',['dynamic-programming','counting'],['Count length-n arrays with values 1..m whose running maximum increases exactly k times.','Return the result modulo 1,000,000,007.'],[([2,3,1],'The six non-increasing-with-respect-to-the-first-maximum arrays have cost one.'),([5,2,3],'Exactly five length-five binary arrays introduce a new maximum three times.')],[[*x] for x in [(1,1,1),(1,3,1),(1,3,2),(2,2,1),(2,2,2),(2,3,1),(2,3,2),(3,2,1),(3,2,2),(3,2,3),(4,3,2),(5,2,3),(5,4,1),(5,5,5)]],ARRAYS,[ARRAYS.replace('cost+(value>maximum)','cost+(value>=maximum)'),ARRAYS.replace('if cost==k','if cost<=k')],['Counts ties with the current maximum as new records.','Includes arrays with fewer than k comparisons.'],arrays_o,rarray,['DP state needs processed length, current maximum, and record-increase count.','Append every value 1..m; only values above the current maximum increase cost.','Merge identical resulting states modulo the modulus.','Every array has a unique prior prefix and final value, so transitions count it exactly once.'],'O(n*m²*k)','O(m*k)',8),
1422:S('maximum_binary_split_score',[('s','str')],'int',['strings','prefix-sums'],['Split the binary string into two non-empty parts.','Score is zeroes on the left plus ones on the right; return the maximum.'],[(['011101'],'Splitting after the first character gives one left zero plus four right ones.'),(['1111'],'Any valid split has no left zeroes; the earliest leaves three right ones.')],[[s] for s in ['01','10','00','11','011101','00111','1111','0000','0101','1010','00100','11011','01010101','1000001']],SPLIT,[SPLIT.replace("s[:-1]","s"),'''def maximum_binary_split_score(s):
 right_ones=s.count('1');left_zeros=answer=0
 for char in s[:-1]:
  if char=='0':left_zeros+=1
  answer=max(answer,left_zeros+right_ones)
 return answer
'''],['Also considers an invalid empty right part.','Never removes ones that move from right to left.'],split_o,rsplit,['Start with all ones counted on the right and no left zeroes.','Move the split across every position except the final character.','Update the appropriate count for the crossed character.','Every legal split is examined once with its exact score.'],'O(n)','O(1)',3),
1423:S('maximum_card_points',[('card_points','list[int]'),('k','int')],'int',['sliding-window','arrays'],['Take exactly k cards, one at a time, only from either end.','Return the maximum obtainable sum.'],[([[1,2,3,4,5,6,1],3],'Taking six and the two rightmost cards yields twelve.'),([[2,2,2],2],'Any two end cards total four.')],[[c,k] for c,k in [([1],1),([1,2],1),([1,2],2),([1,2,3,4,5,6,1],3),([2,2,2],2),([9,7,7,9,7,7,9],7),([1,1000,1],1),([1,1000,1],2),([5,1,2,10],2),([10,1,2,5],3),([3,3,3,9],2),([8,1,1,1,8],2),([4,2,7,1,9],3),([6,5,4,3,2,1],4)]],CARDS,[CARDS.replace('range(1,k+1)','range(1,k)'),CARDS.replace('answer=max(answer,current)','answer=min(answer,current)')],['Never considers taking all k cards from the right.','Minimizes rather than maximizes across valid end splits.'],cards_o,rcard,['Any valid outcome takes some prefix and the remaining cards from the suffix.','Begin with all k from the left.','Move one choice at a time from the left boundary to the right boundary.','The k+1 prefix/suffix splits cover every possible end-taking result.'],'O(k)','O(1)',5),
1424:S('diagonal_traverse_jagged',[('nums','list[list[int]]')],'list[int]',['arrays','sorting'],['Rows may have different lengths.','Visit diagonals by increasing row+column, and within a diagonal from lower row to upper row.'],[([[[1,2,3],[4,5,6],[7,8,9]]],'The diagonal groups are 1; 4,2; 7,5,3; 8,6; 9.'),([[[1,2,3,4,5],[6,7],[8],[9,10,11],[12,13,14,15,16]]],'Jagged rows contribute only their existing coordinates.')],[[x] for x in [[[1]],[[1,2]],[[1],[2]],[[1,2],[3,4]],[[1,2,3],[4],[5,6]],[[1],[2,3,4],[5,6]],[[1,2,3],[4,5,6],[7,8,9]],[[1,2,3,4,5],[6,7],[8],[9,10,11],[12,13,14,15,16]],[[1],[2],[3],[4]],[[1,2,3,4]],[[1,2],[3],[4,5,6]],[[9,8,7],[6,5],[4]],[[1],[2,3],[4,5,6],[7]],[[10,20],[30,40,50],[60]]]],DIAGONAL,[DIAGONAL.replace('reversed(diagonals[key])','diagonals[key]'),DIAGONAL.replace('row+column','row-column')],['Traverses each diagonal from upper row to lower row.','Groups anti-diagonals by row-column instead of row+column.'],diagonal_o,rdiag,['Cells on one required diagonal share row+column.','Collect values by that sum while scanning rows top-down.','Reverse each bucket to visit larger row indices first.','Concatenating buckets by increasing sum implements both ordering rules.'],'O(cells log cells)','O(cells)',5),
1425:S('constrained_subsequence_sum',[('nums','list[int]'),('k','int')],'int',['dynamic-programming','monotonic-queue'],['Choose a non-empty subsequence whose consecutive chosen indices differ by at most k.','Return its maximum sum; values may be negative.'],[([[10,2,-10,5,20],2],'The constrained subsequence 10, 2, 5, 20 totals 37.'),([[-1,-2,-3],1],'The best non-empty choice is -1.')],[[v,k] for v,k in [([1],1),([-1],1),([10,2,-10,5,20],2),([-1,-2,-3],1),([10,-2,-10,-5,20],2),([1,-1,1,-1,1],1),([5,-100,6],2),([5,-100,6],1),([0,0,0],2),([-5,10,-5,10],2),([3,-2,4,-1,5],3),([8,-9,7,-6,5],1),([1,2,3,4],4),([-10,1,2,-10,3],2)]],CONSTRAINED,[CONSTRAINED.replace('queue[0]<i-k','queue[0]<=i-k'),CONSTRAINED.replace('max(0,best[queue[0]] if queue else 0)','best[queue[0]] if queue else 0')],['Expires an index exactly k away even though it remains valid.','Forces extension of a negative prior sum instead of starting anew.'],constrained_o,rcon,['Let best[i] be the best valid subsequence ending at i.','Add nums[i] to the positive maximum best value among the previous k indices, or start at nums[i].','Maintain candidate best values in decreasing order in a deque and expire old indices.','The deque front is exactly the window maximum needed by the recurrence.'],'O(n)','O(n)',8),
1426:S('count_elements_with_successor',[('arr','list[int]')],'int',['arrays','hash-maps'],['Count each array occurrence x when x+1 appears anywhere in the array.','Duplicate qualifying occurrences count separately.'],[([[1,2,3]],'One and two qualify because their successors appear; three does not.'),([[1,1,3,3,5,5,7,7]],'None has its immediate successor present, so the count is zero.')],[[x] for x in [[1],[1,2],[2,1],[1,2,3],[1,1,2],[1,1,2,2],[0,1,1,2],[-1,0],[-2,0], [1,1,3,3,5,5,7,7],[5,4,3,2,1],[10,11,10],[0,2,1,3],[7,8,8,9]]],ELEMENTS,[ELEMENTS.replace('value+1','value-1'),ELEMENTS.replace('for value in arr','for value in values')],['Looks for a predecessor instead of a successor.','Counts distinct values rather than array occurrences.'],elements_o,relem,['Put all values in a set for membership tests.','For every original occurrence, test whether value+1 is present.','Sum the true tests without deduplicating the iteration.','Set membership answers existence while scanning arr preserves duplicate contribution.'],'O(n)','O(n)',3),
1427:S('apply_string_shifts',[('s','str'),('shift','list[list[int]]')],'str',['strings','math'],['Each [0,amount] shifts left and [1,amount] shifts right.','Apply all operations and return the final string.'],[(['abc',[[0,1],[1,2]]],'The net movement is one position right, producing cab.'),(['abcdefg',[[1,1],[1,1],[0,2],[1,3]]],'The operations combine to a net right rotation of three.')],[[s,o] for s,o in [('a',[[0,1]]),('ab',[[0,1]]),('ab',[[1,1]]),('abc',[[0,1],[1,2]]),('abcdefg',[[1,1],[1,1],[0,2],[1,3]]),('hello',[[0,5]]),('hello',[[1,12]]),('xyz',[[0,100]]),('abcd',[[0,1],[0,1]]),('abcd',[[1,1],[1,1]]),('rotation',[[0,3],[1,1]]),('aaab',[[1,1]]),('python',[[0,2],[1,8]]),('z',[[0,0],[1,99]])]],SHIFTS,[SHIFTS.replace('if direction==1 else -value','if direction==0 else -value'),SHIFTS.replace('%len(s)','')],['Reverses the meanings of left and right.','Fails to reduce large net shifts modulo string length.'],shifts_o,rshift,['All rotations compose, so sum signed amounts first.','Treat right as positive and left as negative.','Reduce the net shift modulo the string length.','One final slice rotation has the same effect as the full operation sequence.'],'O(operations+n)','O(n)',3),
1431:S('kids_with_extra_candies',[('candies','list[int]'),('extra_candies','int')],'list[bool]',['arrays','comparison'],['Give the same extra-candy amount hypothetically to each child in turn.','Return whether that child could then have at least as many as the current maximum.'],[([[2,3,5,1,3],3],'After receiving three, every child except the one starting at one reaches at least five.'),([[4,2,1,1,2],1],'Only the child already holding four can reach the maximum four.')],[[c,e] for c,e in [([1],0),([1],5),([2,3,5,1,3],3),([4,2,1,1,2],1),([12,1,12],10),([0,0],0),([0,1],1),([5,5,5],0),([1,2,3],0),([10,1],8),([10,1],9),([3,6,2,6],3),([100,50,1],49),([7,8,9,10],2)]],CANDIES,[CANDIES.replace('>=greatest','>greatest'),CANDIES.replace('greatest=max(candies)','greatest=min(candies)')],['Requires strictly more than the current maximum instead of allowing a tie.','Compares against the current minimum.'],candies_o,rcandy,['Find the largest current candy count once.','For each child, add the hypothetical extra amount.','A child qualifies when that sum is at least the maximum.','The children are independent because the extra candies are hypothetical, not consumed.'],'O(n)','O(n)',3),
1432:S('maximum_remap_difference',[('num','int')],'int',['greedy','strings'],['For each of two values, replace every occurrence of one chosen digit with another digit.','Neither result may have a leading zero; return the largest possible difference.'],[([555],'Changing 5 to 9 gives 999 and changing 5 to 1 gives 111, for difference 888.'),([9],'The maximum remains 9 and the minimum is 1, giving eight.')],[[n] for n in [1,9,10,11,99,100,555,123456,909,1101057,999999,10000,9288,123123]],DIFFERENCE,[DIFFERENCE.replace("char!='9'","char=='9'"),DIFFERENCE.replace("if text[0]!='1'","if text[0]=='1'")],['Chooses a nine rather than the first non-nine digit for maximizing.','Uses the wrong branch for minimizing the leading digit.'],difference_o,rdiff,['To maximize, replace the first digit not already nine and all its repeats with nine.','To minimize, change a non-one leading digit to one.','If the leading digit is one, change the first later digit outside zero/one to zero.','The earliest differing decimal position dominates every later choice, proving each greedy remap.'],'O(digits)','O(digits)',5),
1433:S('can_one_string_break',[('s1','str'),('s2','str')],'bool',['strings','sorting'],['The strings have equal length and lowercase letters.','One string can break the other when its characters can be permuted so every position is >= the other string.'],[(['abc','xya'],'After sorting, abc is componentwise no greater than axy, so xya can break abc.'),(['abe','acd'],'The sorted comparisons cross directions, so neither string can break the other.')],[[a,b] for a,b in [('a','a'),('a','b'),('abc','xya'),('abe','acd'),('leetcodee','interview'),('aaa','bbb'),('cba','abc'),('az','by'),('zz','aa'),('ab','ba'),('abcd','bcda'),('ace','bdf'),('aabb','ccdd'),('xyz','xzz')]],BREAK,[BREAK.replace(' or all(a<=b',' and all(a<=b'),'''def can_one_string_break(s1, s2):
 return all(a>=b for a,b in zip(s1,s2)) or all(a<=b for a,b in zip(s1,s2))
'''],['Requires both opposite componentwise directions simultaneously.','Compares original positions without allowing permutations.'],break_o,rbreak,['Sort both multisets so comparable ranks align.','Check whether every character of the first is >= its counterpart.','Also check the reverse direction with <=.','Sorted rankwise dominance is necessary and sufficient for a matching permutation by the standard exchange argument.'],'O(n log n)','O(n)',5),
}
