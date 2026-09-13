"""Second half of batch 88: deterministic geometry, graph, and counting tasks."""
from collections import Counter, deque
from .import_batch_055 import entry


def rectangle_oracle(args):
    rectangles=args[0]
    left=min(r[0] for r in rectangles);bottom=min(r[1] for r in rectangles)
    right=max(r[2] for r in rectangles);top=max(r[3] for r in rectangles)
    cells=set()
    for x1,y1,x2,y2 in rectangles:
        for x in range(x1,x2):
            for y in range(y1,y2):
                if (x,y) in cells:return False
                cells.add((x,y))
    return cells=={(x,y) for x in range(left,right) for y in range(bottom,top)}


def division_oracle(args):
    equations,values,queries=args;known={name for edge in equations for name in edge};ratio={}
    for name in known:ratio[name,name]=1.0
    for (left,right),value in zip(equations,values):ratio[left,right]=value;ratio[right,left]=1.0/value
    for middle in known:
        for left in known:
            for right in known:
                if (left,middle) in ratio and (middle,right) in ratio:
                    ratio[left,right]=ratio[left,middle]*ratio[middle,right]
    return [ratio.get((left,right),-1.0) for left,right in queries]


def hex_oracle(args):return format(args[0]&0xffffffff,'x')


def fizz_oracle(args):
    return ['FizzBuzz' if value%15==0 else 'Fizz' if value%3==0 else 'Buzz' if value%5==0 else str(value)
            for value in range(1,args[0]+1)]


def segments_oracle(args):
    text=args[0];count=0;inside=False
    for char in text:
        if char!=' ' and not inside:count+=1
        inside=char!=' '
    return count


def coins_oracle(args):
    coins=args[0];row=0
    while coins>=row+1:row+=1;coins-=row
    return row


def duplicates_oracle(args):
    counts=Counter(args[0]);return sorted(value for value,count in counts.items() if count==2)


def pigs_oracle(args):
    buckets,die,test=args;rounds=test//die;pigs=0;states=1
    while states<buckets:pigs+=1;states*=rounds+1
    return pigs


def balancing_oracle(args):
    balances=Counter()
    for source,target,amount in args[0]:balances[source]-=amount;balances[target]+=amount
    values=[value for value in balances.values() if value]
    size=1<<len(values);total=[0]*size;groups=[-10**9]*size;groups[0]=0
    for mask in range(1,size):
        bit=mask&-mask;index=bit.bit_length()-1;total[mask]=total[mask^bit]+values[index]
        sub=mask
        while sub:
            if total[sub]==0:groups[mask]=max(groups[mask],groups[mask^sub]+1)
            sub=(sub-1)&mask
    return len(values)-groups[-1]


def split_oracle(args):
    nums=args[0];prefix=[0]
    for value in nums:prefix.append(prefix[-1]+value)
    for i in range(1,len(nums)-5):
        for j in range(i+2,len(nums)-3):
            for k in range(j+2,len(nums)-1):
                if prefix[i]==prefix[j]-prefix[i+1]==prefix[k]-prefix[j+1]==prefix[-1]-prefix[k+1]:return True
    return False


def random_rectangle(rng):
    width,height=rng.randint(1,4),rng.randint(1,4)
    cells=[[x,y,x+1,y+1] for x in range(width) for y in range(height)]
    if rng.random()<.5 or len(cells)==1:return [cells]
    cells.append(list(rng.choice(cells)))
    rng.shuffle(cells);return [cells]


def random_division(rng):
    names=list('abcdef')[:rng.randint(2,6)];weights={name:rng.randint(1,9) for name in names}
    equations=[]
    for index in range(1,len(names)):
        parent=rng.randrange(index);equations.append([names[parent],names[index]])
    values=[weights[a]/weights[b] for a,b in equations]
    pool=names+['x'];queries=[[rng.choice(pool),rng.choice(pool)] for _ in range(rng.randint(1,10))]
    return [equations,values,queries]


def random_hex(rng):return [rng.randint(-(2**31),2**31-1)]
def random_fizz(rng):return [rng.randint(1,300)]
def random_segments(rng):return [''.join(rng.choice(' abcXYZ,!') for _ in range(rng.randint(0,80)))]
def random_coins(rng):return [rng.randint(0,2**31-1)]


def random_duplicates(rng):
    n=rng.randint(1,25);distinct=rng.randint((n+1)//2,n);values=rng.sample(range(1,n+1),distinct)
    nums=values+rng.sample(values,n-distinct);rng.shuffle(nums);return [nums]


def random_pigs(rng):
    die=rng.randint(1,30);rounds=rng.randint(1,8);return [rng.randint(1,1000),die,die*rounds]


def random_balancing(rng):
    people=rng.randint(2,7);transactions=[]
    for _ in range(rng.randint(1,9)):
        source,target=rng.sample(range(people),2);transactions.append([source,target,rng.randint(1,20)])
    return [transactions]


def random_split(rng):return [[rng.randint(-8,8) for _ in range(rng.randint(7,14))]]


RECTANGLE='''def is_perfect_rectangle(rectangles):
 area=0;corners=set();left=bottom=float('inf');right=top=float('-inf')
 for x1,y1,x2,y2 in rectangles:
  left=min(left,x1);bottom=min(bottom,y1);right=max(right,x2);top=max(top,y2);area+=(x2-x1)*(y2-y1)
  for corner in ((x1,y1),(x1,y2),(x2,y1),(x2,y2)):
   if corner in corners:corners.remove(corner)
   else:corners.add(corner)
 return area==(right-left)*(top-bottom) and corners=={(left,bottom),(left,top),(right,bottom),(right,top)}
'''

DIVISION='''def evaluate_division(equations, values, queries):
 graph={}
 for (left,right),value in zip(equations,values):
  graph.setdefault(left,[]).append((right,value));graph.setdefault(right,[]).append((left,1.0/value))
 answer=[]
 for start,end in queries:
  if start not in graph or end not in graph:answer.append(-1.0);continue
  queue=__import__('collections').deque([(start,1.0)]);seen={start};result=-1.0
  while queue:
   node,value=queue.popleft()
   if node==end:result=value;break
   for other,factor in graph[node]:
    if other not in seen:seen.add(other);queue.append((other,value*factor))
  answer.append(result)
 return answer
'''

HEX='''def integer_to_hex(num):
 if num==0:return '0'
 num&=0xffffffff;digits='0123456789abcdef';answer=''
 while num:answer=digits[num&15]+answer;num>>=4
 return answer
'''

FIZZ='''def fizz_buzz(n):
 answer=[]
 for value in range(1,n+1):
  text=('Fizz' if value%3==0 else '')+('Buzz' if value%5==0 else '')
  answer.append(text or str(value))
 return answer
'''

SEGMENTS='''def count_text_segments(s):
 return sum(char!=' ' and (index==0 or s[index-1]==' ') for index,char in enumerate(s))
'''

COINS='''def complete_coin_rows(n):
 left,right=0,n
 while left<=right:
  middle=(left+right)//2
  if middle*(middle+1)//2<=n:left=middle+1
  else:right=middle-1
 return right
'''

DUPLICATES='''def duplicated_values(nums):
 answer=[]
 for value in nums:
  index=abs(value)-1
  if nums[index]<0:answer.append(abs(value))
  else:nums[index]=-nums[index]
 return answer
'''

PIGS='''def minimum_test_pigs(buckets, minutes_to_die, minutes_to_test):
 rounds=minutes_to_test//minutes_to_die;states=rounds+1;pigs=0;capacity=1
 while capacity<buckets:pigs+=1;capacity*=states
 return pigs
'''

BALANCE='''def minimum_balance_transactions(transactions):
 balance={}
 for source,target,amount in transactions:balance[source]=balance.get(source,0)-amount;balance[target]=balance.get(target,0)+amount
 debts=[value for value in balance.values() if value]
 def settle(start):
  while start<len(debts) and debts[start]==0:start+=1
  if start==len(debts):return 0
  best=len(debts);used=set()
  for other in range(start+1,len(debts)):
   if debts[start]*debts[other]<0 and debts[other] not in used:
    used.add(debts[other]);debts[other]+=debts[start];best=min(best,1+settle(start+1));debts[other]-=debts[start]
  return best
 return settle(0)
'''

SPLIT='''def can_split_four_equal_sums(nums):
 prefix=[0]
 for value in nums:prefix.append(prefix[-1]+value)
 for middle in range(3,len(nums)-3):
  left_sums=set()
  for first in range(1,middle-1):
   if prefix[first]==prefix[middle]-prefix[first+1]:left_sums.add(prefix[first])
  for third in range(middle+2,len(nums)-1):
   if prefix[third]-prefix[middle+1]==prefix[-1]-prefix[third+1] and prefix[third]-prefix[middle+1] in left_sums:return True
 return False
'''


E=entry
BATCH={
391:E('is_perfect_rectangle',[('rectangles','list[list[int]]')],'bool',['geometry','hash-maps'],['Each rectangle has positive integer width and height.','Return true only for exact coverage with neither gaps nor overlaps.'],[([[[1,1,3,3],[3,1,4,2],[3,2,4,4],[1,3,2,4],[2,3,3,4]]],'The five pieces cover every point of the 3-by-3 bounding rectangle exactly once.'),([[[1,1,2,3],[1,3,2,4],[3,1,4,2],[3,2,4,4]]],'A vertical gap separates the left and right pieces.')],[[r] for r in [[[0,0,1,1]],[[0,0,1,1],[1,0,2,1]],[[0,0,2,1],[0,1,2,2]],[[0,0,2,2],[1,1,3,3]],[[0,0,1,2],[1,0,2,1],[1,1,2,2]],[[0,0,1,1],[0,1,1,2],[1,0,2,2]],[[0,0,2,2],[0,0,1,1],[1,1,2,2]],[[1,1,4,4]],[[0,0,3,1],[0,1,1,3],[1,1,3,3]],[[0,0,1,3],[1,0,3,1],[1,1,3,3]],[[0,0,1,1],[2,0,3,1]],[[0,0,2,1],[0,1,1,2]],[[0,0,1,1],[1,0,2,1],[0,1,1,2],[1,1,2,2]],[[0,0,3,3],[1,1,2,2]],[[0,0,2,1],[0,1,1,2],[0,1,1,2]]]],RECTANGLE,['''def is_perfect_rectangle(rectangles):
 area=sum((x2-x1)*(y2-y1) for x1,y1,x2,y2 in rectangles);left=min(r[0] for r in rectangles);bottom=min(r[1] for r in rectangles);right=max(r[2] for r in rectangles);top=max(r[3] for r in rectangles)
 return area==(right-left)*(top-bottom)
''','''def is_perfect_rectangle(rectangles):
 left=min(r[0] for r in rectangles);bottom=min(r[1] for r in rectangles);right=max(r[2] for r in rectangles);top=max(r[3] for r in rectangles)
 corners={(x,y) for r in rectangles for x,y in ((r[0],r[1]),(r[0],r[3]),(r[2],r[1]),(r[2],r[3]))}
 return {(left,bottom),(left,top),(right,bottom),(right,top)}<=corners
'''],['Area alone lets an overlap cancel a gap of equal area.','Merely seeing the four outer corners does not rule out gaps or overlaps inside.'],rectangle_oracle,random_rectangle,['A perfect cover has the bounding area and exactly four unmatched corners.','Toggle each small-rectangle corner in a set while accumulating area and bounds.','Require total area equal to bounding area and the toggle set equal to the four bounding corners.','Interior corners occur an even number of times; area equality then rules out both missing and multiply covered regions.'],'O(n)','O(n)',8),
399:E('evaluate_division',[('equations','list[list[str]]'),('values','list[float]'),('queries','list[list[str]]')],'list[float]',['graphs','breadth-first-search'],['Equation values are positive and mutually consistent.','Unknown variables produce -1.0, including unknown divided by itself.'],[([[['a','b'],['b','c']],[2.0,3.0],[['a','c'],['b','a'],['a','e'],['a','a'],['x','x']]],'Path products give 6, 0.5, -1, 1, and -1 respectively.'),([[['x','y']],[4.0],[['y','x'],['x','x']]],'The reverse edge has weight one quarter, and a known variable divided by itself is one.')],[[e,v,q] for e,v,q in [([['a','b']],[2.0],[['a','b']]),([['a','b']],[2.0],[['b','a']]),([['a','b']],[2.0],[['a','a']]),([['a','b']],[2.0],[['z','z']]),([['a','b'],['b','c']],[2.0,5.0],[['a','c']]),([['a','b'],['c','d']],[2.0,3.0],[['a','d']]),([['a','b'],['b','c'],['c','d']],[2.0,3.0,4.0],[['d','a']]),([['m','n']],[0.5],[['m','n'],['n','m']]),([['a','b'],['a','c']],[2.0,4.0],[['b','c']]),([['p','q'],['q','r']],[1.0,1.0],[['p','r']]),([['a','b']],[3.0],[['b','x']]),([['u','v'],['v','w']],[10.0,0.1],[['u','w']]),([['a','b'],['b','c']],[1.5,2.0],[['c','a']]),([['a','b'],['c','d']],[2.0,4.0],[['c','d'],['b','a']])]],DIVISION,['''def evaluate_division(equations, values, queries):
 direct={(a,b):v for (a,b),v in zip(equations,values)}
 return [direct.get((a,b),1.0 if a==b else -1.0) for a,b in queries]
''',DIVISION.replace("graph.setdefault(right,[]).append((left,1.0/value))",'pass')],['Uses only direct equations and treats unknown self-queries as defined.','Builds no reciprocal edges, so reverse-direction paths are unreachable.'],division_oracle,random_division,['Treat each equation a/b=v as weighted edges a→b with v and b→a with 1/v.','For each query, search from numerator to denominator while multiplying edge weights.','Reject immediately when either endpoint is unknown; otherwise BFS with a visited set.','A path product cancels intermediate variables and equals the requested quotient.'],'O(queries*(variables+equations))','O(variables+equations)',5),
405:E('integer_to_hex',[('num','int')],'str',['bit-manipulation','math'],['num is a signed 32-bit integer.','Use lowercase hexadecimal without leading zeros; negatives use 32-bit two’s complement.'],[([26],'Twenty-six is one group of 1 and one group of 10, written 1a.'),([-1],'All 32 bits are one, producing ffffffff.')],[[n] for n in [0,1,15,16,17,255,256,4095,4096,-2,-16,-26,-2147483648,2147483647]],HEX,['''def integer_to_hex(num):
 return format(abs(num),'x')
''',HEX.replace("digits='0123456789abcdef'","digits='0123456789ABCDEF'")],['Uses magnitude for negative inputs instead of their 32-bit two’s-complement value.','Emits uppercase digits although the contract requires lowercase.'],hex_oracle,random_hex,['Mask the integer to its low 32 bits.','Repeatedly take the low four bits, map them to one hex digit, and shift right.','Handle zero separately; reverse or prepend the collected digits.','Each hexadecimal digit represents exactly four bits, so eight groups cover every 32-bit value.'],'O(1)','O(1)',3),
412:E('fizz_buzz',[('n','int')],'list[str]',['simulation','math'],['1 <= n <= 10000.','Return one entry for every integer from 1 through n.'],[([3],'The entries are 1, 2, and Fizz.'),([15],'The fifteenth entry is FizzBuzz because fifteen is divisible by both three and five.')],[[n] for n in [1,2,4,5,6,10,14,16,20,30,31,45,100,999]],FIZZ,['''def fizz_buzz(n):
 return ['Fizz' if value%3==0 else 'Buzz' if value%5==0 else 'FizzBuzz' if value%15==0 else str(value) for value in range(1,n+1)]
''','''def fizz_buzz(n):
 return [str(value) for value in range(n)]
'''],['Checks divisibility by three before the combined case, so multiples of fifteen become only Fizz.','Uses zero-based values and never performs the substitutions.'],fizz_oracle,random_fizz,['A multiple of fifteen needs both words.','Build each entry from an optional Fizz part and optional Buzz part.','Append the combined text when nonempty; otherwise append the decimal number.','Independent divisibility checks naturally concatenate both labels for common multiples.'],'O(n)','O(n)',3),
434:E('count_text_segments',[('s','str')],'int',['strings','state-machines'],['0 <= len(s) <= 300.','Only the ordinary space character separates segments.'],[(['Hello, my name is John'],'Five runs of non-space characters form five segments.'),(['   '],'Spaces alone contain no segment.')],[[s] for s in ['', 'a',' a','a ',' a ','a b','a  b','hello,world','hello, world','! !','one\ttwo','  many   gaps  ','x,y,z',' end']],SEGMENTS,['''def count_text_segments(s):
 return len(s.split(' '))
''','''def count_text_segments(s):
 return len(s.split(','))
'''],['Counts empty pieces created by leading, trailing, or repeated spaces.','Treats commas as separators even though only spaces delimit segments.'],segments_oracle,random_segments,['A segment begins at a non-space character whose predecessor is absent or a space.','Scan once and count exactly those transitions.','For each index, add one when s[i] is non-space and i is zero or s[i-1] is space.','Every maximal non-space run has exactly one starting transition.'],'O(n)','O(1)',3),
441:E('complete_coin_rows',[('n','int')],'int',['binary-search','math'],['0 <= n <= 2^31-1.','Row k needs k coins; return the number of fully completed rows.'],[([5],'Rows of one and two consume three coins; only two of the next three are available.'),([8],'Rows one through three require six coins, leaving two.')],[[n] for n in [0,1,2,3,4,6,7,9,10,15,16,100,1000,2147483647]],COINS,['''def complete_coin_rows(n):
 return int((2*n)**0.5)
''','''def complete_coin_rows(n):
 return n//2
'''],['Rounds the square-root estimate without enforcing k(k+1)/2 <= n.','Assumes every full row costs two coins.'],coins_oracle,random_coins,['Completing k rows costs the triangular number k(k+1)/2.','Binary-search the greatest k whose triangular cost is at most n.','Move right after feasible midpoints and left after infeasible ones; return the last feasible bound.','The triangular cost is strictly increasing, so feasibility is a monotone predicate.'],'O(log n)','O(1)',3),
442:E('duplicated_values',[('nums','list[int]')],'list[int]',['arrays','in-place'],['len(nums)=n; every value is in 1..n and appears once or twice.','Return all twice-occurring values in O(n) time and O(1) auxiliary space.'],[([[4,3,2,7,8,2,3,1]],'Values two and three are each encountered twice.'),([[1,1,2]],'Only one occurs twice.')],[[x] for x in [[1],[1,1],[1,2],[2,2],[1,2,3],[3,3,1],[2,1,2],[5,4,3,2,1],[1,2,3,4,4],[2,2,3,3],[6,1,2,3,4,6],[1,1,2,2,3,3],[4,1,4,2,3],[7,6,5,4,3,2,1,7]]],DUPLICATES,['''def duplicated_values(nums):
 return list(set(nums))
''','''def duplicated_values(nums):
 return [value for index,value in enumerate(nums) if value in nums[:index]]+[nums[0]]
'''],['Returns every distinct value rather than only values occurring twice.','Adds an extra first value even when it is not duplicated.'],duplicates_oracle,random_duplicates,['A value v can use array index v-1 as one bit of visitation state.','Negate nums[abs(v)-1] on first sight; if it is already negative, v is duplicated.','Use abs while reading because earlier visits may have changed the sign.','The value bounds provide one unique marker position per possible value without extra storage.'],'O(n)','O(1)',5),
458:E('minimum_test_pigs',[('buckets','int'),('minutes_to_die','int'),('minutes_to_test','int')],'int',['math','combinatorics'],['1 <= buckets <= 1000; time values are positive and minutes_to_test >= minutes_to_die.','All pigs may participate in every testing round until they die.'],[([4,15,15],'One round gives each pig two outcomes; two pigs distinguish four buckets.'),([1000,15,60],'Four rounds give five states per pig, so five pigs distinguish at least 1000 buckets.')],[[b,d,t] for b,d,t in [(1,1,1),(2,1,1),(3,1,1),(8,1,1),(9,1,1),(5,10,20),(9,10,20),(10,10,20),(25,5,10),(26,5,10),(100,15,30),(125,15,30),(126,15,30),(500,10,60)]],PIGS,['''def minimum_test_pigs(buckets, minutes_to_die, minutes_to_test):
 states=minutes_to_test//minutes_to_die+1;pigs=0
 while states**pigs<=buckets:pigs+=1
 return pigs
''','''def minimum_test_pigs(buckets, minutes_to_die, minutes_to_test):
 states=minutes_to_test//minutes_to_die
 if states<=1:return buckets-1
 pigs=0;capacity=1
 while capacity<buckets:pigs+=1;capacity*=states
 return pigs
'''],['Uses a strict capacity comparison and adds a pig when capacity equals the bucket count.','Counts only death rounds and omits the final survives-all-rounds state.'],pigs_oracle,random_pigs,['After r rounds, one pig has r+1 distinguishable outcomes: death in each round or survival.','With p pigs, outcome vectors distinguish (r+1)^p buckets.','Increase p until that capacity reaches buckets.','Assigning each bucket a base-(r+1) outcome vector attains the bound, so the first sufficient p is minimal.'],'O(log buckets)','O(1)',5),
465:E('minimum_balance_transactions',[('transactions','list[list[int]]')],'int',['backtracking','hash-maps'],['Each transaction is [payer,receiver,positive amount].','Only final net balances matter; return the fewest settlement transfers.'],[([[[0,1,10],[2,0,5]]],'Net balances are -5,+10,-5 and need two settlement transfers.'),([[[0,1,10],[1,0,10]]],'The two transactions cancel, so no settlement is needed.')],[[t] for t in [[[0,1,5]],[[0,1,5],[1,2,5]],[[0,1,5],[2,3,7]],[[0,1,10],[2,0,5]],[[0,1,10],[1,0,10]],[[0,1,5],[0,2,5],[1,2,5]],[[0,1,4],[2,3,4],[1,2,4]],[[0,1,8],[0,2,4],[3,0,6]],[[0,1,3],[1,2,2],[2,0,1]],[[0,1,10],[2,3,10],[1,2,10]],[[0,1,5],[2,0,5],[3,4,7]],[[0,1,5],[0,2,5],[3,0,10]],[[0,1,2],[0,2,2],[0,3,2]],[[0,1,6],[2,0,4],[1,2,2]]]],BALANCE,['''def minimum_balance_transactions(transactions):
 balance={}
 for a,b,v in transactions:balance[a]=balance.get(a,0)-v;balance[b]=balance.get(b,0)+v
 return max(0,len([v for v in balance.values() if v])-1)
''','''def minimum_balance_transactions(transactions):
 balance={}
 for a,b,v in transactions:balance[a]=balance.get(a,0)-v;balance[b]=balance.get(b,0)+v
 return sum(v<0 for v in balance.values())
'''],['Assumes all nonzero balances must form one settlement group, missing independent zero-sum groups.','Assumes one transfer per debtor even when a debtor must pay multiple creditors.'],balancing_oracle,random_balancing,['Collapse the history into one net balance per person.','Choose the first unsettled balance and pair it with each opposite-signed later balance.','Apply the transfer in place, recurse, undo it, and keep the minimum; skip duplicate partner balances.','Every solution must settle the first nonzero person with someone of the opposite sign, so the branches are exhaustive.'],'O(m!)','O(m)',8),
548:E('can_split_four_equal_sums',[('nums','list[int]')],'bool',['prefix-sums','hash-maps'],['7 <= len(nums) <= 2000; values may be negative.','Remove indices i,j,k with at least one element in each of the four remaining sections.'],[([[1,2,1,2,1,2,1]],'Removing indices 1,3,5 leaves four sections each summing to one.'),([[1,2,3,4,5,6,7]],'No three separators produce four equal section sums.')],[[x] for x in [[0]*7,[1]*7,[1,2,1,2,1,2,1],[1,2,3,4,5,6,7],[2,0,2,0,2,0,2],[-1,0,-1,0,-1,0,-1],[3,1,3,1,3,1,3],[1,1,1,1,1,1,1,1],[1,-1,1,-1,1,-1,1],[5,0,0,5,0,0,5,0,0,5],[0,1,0,1,0,1,0,1,0],[2,3,2,3,2,3,2],[4,-2,4,-2,4,-2,4],[1,0,1,0,1,0,2]]],SPLIT,['''def can_split_four_equal_sums(nums):
 total=sum(nums)
 return total%4==0
''','''def can_split_four_equal_sums(nums):
 prefix=[0]
 for value in nums:prefix.append(prefix[-1]+value)
 for middle in range(3,len(nums)-3):
  left=set()
  for first in range(1,middle-1):
   if prefix[first]==prefix[middle]-prefix[first+1]:left.add(prefix[first])
  for third in range(middle+2,len(nums)-1):
   if prefix[third]-prefix[middle+1] in left:return True
 return False
'''],['Checks only divisibility of the total and ignores the removed separator values.','Matches the first three sections but never checks the final suffix sum.'],split_oracle,random_split,['Fix the middle removed index j and match feasible sums from its left and right sides.','For each j, collect sums where the first two sections match.','Search k on the right; accept when its two sections match and their sum occurs in the left set.','Every valid triple has one middle j and is tested, while prefix sums make each section comparison constant time.'],'O(n²)','O(n)',8),
}

BATCH[399]['comparator']='float_list'
BATCH[442]['comparator']='unordered'
