"""Second half of batch 91: windows, bits, dates, and graph validation."""
from collections import Counter, deque
from datetime import date
from .import_batch_055 import entry

def averages_o(a):
 nums,k,t=a;return sum(sum(nums[i:i+k])>=k*t for i in range(len(nums)-k+1))
def angle_o(a):
 h,m=a;gap=abs((h%12)*30+m/2-m*6);return min(gap,360-gap)
def double_o(a):
 arr=a[0];return any(i!=j and x==2*y for i,x in enumerate(arr) for j,y in enumerate(arr))
def anagram_o(a):
 left=list(a[0]);right=list(a[1]);matches=0
 for c in left:
  if c in right:right.remove(c);matches+=1
 return len(left)-matches
def negatives_o(a):return sum(value<0 for row in a[0] for value in row)
def bits_o(a):return sorted(a[0],key=lambda x:(bin(x).count('1'),x))
def abc_o(a):
 s=a[0];return sum(set('abc')<=set(s[i:j]) for i in range(len(s)) for j in range(i+1,len(s)+1))
def orders_o(a):
 from math import factorial
 n=a[0];return (factorial(2*n)//(2**n))%1000000007
def dates_o(a):
 y1,m1,d1=map(int,a[0].split('-'));y2,m2,d2=map(int,a[1].split('-'));return abs((date(y1,m1,d1)-date(y2,m2,d2)).days)
def tree_o(a):
 n,left,right=a;parents=[0]*n
 for child in left+right:
  if child!=-1:
   parents[child]+=1
   if parents[child]>1:return False
 roots=[i for i,v in enumerate(parents) if v==0]
 if len(roots)!=1:return False
 seen=set();stack=roots[:]
 while stack:
  node=stack.pop()
  if node in seen:return False
  seen.add(node);stack.extend(x for x in (left[node],right[node]) if x!=-1)
 return len(seen)==n

def ravg(r):
 a=[r.randint(0,20) for _ in range(r.randint(1,20))];return [a,r.randint(1,len(a)),r.randint(0,20)]
def rangle(r):return [r.randint(1,12),r.randint(0,59)]
def rdouble(r):return [[r.randint(-20,20) for _ in range(r.randint(2,20))]]
def ranag(r):
 n=r.randint(1,30);return [''.join(r.choice('abcde') for _ in range(n)),''.join(r.choice('abcde') for _ in range(n))]
def rneg(r):
 h,w=r.randint(1,7),r.randint(1,7);values=sorted([r.randint(-9,9) for _ in range(h*w)],reverse=True)
 return [[values[i*w:(i+1)*w] for i in range(h)]]
def rbits(r):return [r.sample(range(0,1000),r.randint(1,30))]
def rabc(r):return [''.join(r.choice('abc') for _ in range(r.randint(3,35)))]
def rorders(r):return [r.randint(1,10)]
def rdates(r):
 first=date.fromordinal(r.randint(date(1971,1,1).toordinal(),date(2100,12,31).toordinal()));second=date.fromordinal(r.randint(date(1971,1,1).toordinal(),date(2100,12,31).toordinal()));return [first.isoformat(),second.isoformat()]
def rtree(r):
 n=r.randint(1,12);left=[-1]*n;right=[-1]*n
 for child in range(1,n):
  if r.random()<.8:
   options=[i for i in range(child) if left[i]==-1 or right[i]==-1]
   if options:
    p=r.choice(options)
    if left[p]==-1 and (right[p]!=-1 or r.random()<.5):left[p]=child
    else:right[p]=child
 if n>1 and r.random()<.3:left[r.randrange(n)]=r.randrange(n)
 return [n,left,right]

AVERAGES='''def qualifying_fixed_average_count(arr, k, threshold):
 total=sum(arr[:k]);answer=int(total>=k*threshold)
 for i in range(k,len(arr)):total+=arr[i]-arr[i-k];answer+=total>=k*threshold
 return answer
'''
ANGLE='''def smaller_clock_angle(hour, minutes):
 difference=abs((hour%12)*30+minutes*.5-minutes*6);return min(difference,360-difference)
'''
DOUBLE='''def contains_double_pair(arr):
 seen=set()
 for value in arr:
  if value*2 in seen or (value%2==0 and value//2 in seen):return True
  seen.add(value)
 return False
'''
ANAGRAM='''def minimum_anagram_replacements(s, t):
 from collections import Counter
 left,right=Counter(s),Counter(t);return sum(max(0,left[c]-right[c]) for c in left)
'''
NEGATIVES='''def count_sorted_matrix_negatives(grid):
 row=len(grid)-1;column=0;answer=0
 while row>=0 and column<len(grid[0]):
  if grid[row][column]<0:answer+=len(grid[0])-column;row-=1
  else:column+=1
 return answer
'''
BITS='''def sort_by_one_bit_count(arr):
 return sorted(arr,key=lambda value:(value.bit_count(),value))
'''
ABC='''def substrings_containing_abc(s):
 last={'a':-1,'b':-1,'c':-1};answer=0
 for i,char in enumerate(s):last[char]=i;answer+=min(last.values())+1
 return answer
'''
ORDERS='''def valid_pickup_delivery_orders(n):
 answer=1
 for pairs in range(1,n+1):answer=answer*pairs*(2*pairs-1)%1000000007
 return answer
'''
DATES='''def days_between_dates(date1, date2):
 def serial(text):
  year,month,day=map(int,text.split('-'))
  def leap(y):return y%400==0 or (y%4==0 and y%100!=0)
  days=365*(year-1971)+sum(leap(y) for y in range(1971,year));lengths=[31,28+leap(year),31,30,31,30,31,31,30,31,30,31]
  return days+sum(lengths[:month-1])+day
 return abs(serial(date1)-serial(date2))
'''
TREE='''def validates_binary_tree_nodes(n, left_child, right_child):
 indegree=[0]*n
 for child in left_child+right_child:
  if child!=-1:
   indegree[child]+=1
   if indegree[child]>1:return False
 roots=[i for i,v in enumerate(indegree) if v==0]
 if len(roots)!=1:return False
 seen=set();stack=roots
 while stack:
  node=stack.pop()
  if node in seen:return False
  seen.add(node)
  for child in (left_child[node],right_child[node]):
   if child!=-1:stack.append(child)
 return len(seen)==n
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(1)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1343:S('qualifying_fixed_average_count',[('arr','list[int]'),('k','int'),('threshold','int')],'int',['sliding-window','arrays'],['Count length-k subarrays whose average is at least threshold.','Inputs are nonnegative and 1 <= k <= len(arr).'],[([[2,2,2,2,5,5,5,8],3,4],'Three length-three windows have sum at least twelve.'),([[1,1,1,1,1],1,1],'Every single-element window qualifies.')],[[a,k,t] for a,k,t in [([1],1,0),([1],1,2),([1,2],2,1),([1,2],2,2),([5,5,5],2,5),([0,0,0],1,0),([1,2,3,4],2,2),([1,2,3,4],3,3),([10,1,10],1,10),([10,1,10],2,5),([2,2,2,2],4,2),([1,5,1,5,1],2,3),([9,8,7],2,8),([3,6,9,12],3,6)]],AVERAGES,[AVERAGES.replace('>=k*threshold','>k*threshold'),AVERAGES.replace('arr[i-k]','arr[i-k+1]')],['Rejects windows whose average equals the threshold.','Removes the wrong departing element when sliding.'],averages_o,ravg,['Compare integer window sum with k*threshold to avoid division.','Initialize the first length-k sum, then slide by adding the entrant and removing the departure.','Count every sum at least the target product.','Each length-k window is visited once with its exact sum.'],'O(n)','O(1)',5),
1344:S('smaller_clock_angle',[('hour','int'),('minutes','int')],'float',['math','geometry'],['hour is 1..12 and minutes is 0..59.','Return the smaller angle in degrees.'],[([12,30],'The minute hand is at 180° and hour hand at 15°, giving 165°.'),([3,30],'The hour hand has advanced to 105°, so the smaller gap is 75°.')],[[h,m] for h,m in [(12,0),(1,0),(6,0),(9,0),(12,15),(12,45),(1,30),(2,20),(3,15),(4,50),(6,30),(9,45),(11,59),(7,5)]],ANGLE,[ANGLE.replace('min(difference,360-difference)','difference'),ANGLE.replace('+minutes*.5','')],['Returns the reflex angle when the direct difference exceeds 180°.','Treats the hour hand as fixed at the hour mark between hours.'],angle_o,rangle,['Convert minute position to 6m degrees and hour position to 30h+0.5m degrees.','Take their absolute difference.','Return min(difference,360-difference).','The two circular arcs sum to 360°, so the smaller formula is exact.'],'O(1)','O(1)',5),
1346:S('contains_double_pair',[('arr','list[int]')],'bool',['hash-maps','arrays'],['Use two distinct indices.','Values may be negative or zero.'],[([[10,2,5,3]],'Ten is twice five at a different index.'),([[3,1,7,11]],'No pair has one value twice the other.')],[[x] for x in [[0,0],[0,1],[1,2],[2,1],[-1,-2],[-2,-1],[1,3,6],[2,4,8],[5,10,3],[1,1,2],[7,14,14],[-3,6],[-3,-6],[100,50]]],DOUBLE,['''def contains_double_pair(arr):
 values=set(arr);return any(2*x in values for x in values)
''',DOUBLE.replace('value%2==0 and value//2 in seen','value//2 in seen')],['Uses one zero occurrence as both indices.','Uses truncated halves for odd values.'],double_o,rdouble,['Check each new value against previously seen values only.','A valid earlier partner is either twice the current value or half of it when current is even.','Return on a match, then add current to seen.','Restricting matches to seen automatically enforces distinct indices.'],'O(n)','O(n)',3),
1347:S('minimum_anagram_replacements',[('s','str'),('t','str')],'int',['hash-maps','strings'],['Strings have equal length and lowercase letters.','Replace characters in t so it becomes an anagram of s.'],[(['bab','aba'],'t lacks one b and has one extra a, so one replacement suffices.'),(['leetcode','practice'],'The frequency deficits determine the minimum replacements.')],[[a,b] for a,b in [('a','a'),('a','b'),('ab','ba'),('aa','bb'),('abc','abd'),('aabb','abbb'),('xyz','xxx'),('hello','bello'),('anagram','mangaar'),('aaaa','abaa'),('abcd','zzzz'),('miss','sips'),('paper','title'),('silent','listen')]],ANAGRAM,[ANAGRAM.replace('max(0,left[c]-right[c])','abs(left[c]-right[c])'),'''def minimum_anagram_replacements(s, t):
 return len(set(s)-set(t))
'''],['Double-counts symmetric frequency differences instead of counting only deficits in t.','Compares only distinct letter presence and ignores multiplicity.'],anagram_o,ranag,['Count both strings.','Each missing occurrence required by s must replace one surplus occurrence in t.','Sum max(0,count_s-count_t) across characters.','Equal total lengths guarantee deficits and surpluses have the same total.'],'O(n)','O(alphabet)',5),
1351:S('count_sorted_matrix_negatives',[('grid','list[list[int]]')],'int',['matrices','two-pointers'],['Rows and columns are sorted nonincreasing.','Count entries strictly below zero.'],[([[[4,3,2,-1],[3,2,1,-1],[1,1,-1,-2],[-1,-1,-2,-3]]],'There are eight negative entries.'),([[[3,2],[1,0]]],'Zero is not negative, so the answer is zero.')],[[g] for g in [[[0]],[[-1]],[[1]],[[1,-1]],[[1],[-1]],[[2,1],[0,-1]],[[0,0],[-1,-1]],[[5,4,3],[2,1,0]],[[3,0,-1],[2,-1,-2]],[[1,-1],[-1,-2]],[[10,0],[-5,-6]],[[4,3,2],[3,2,1]],[[0,-1,-2],[-1,-2,-3]],[[9,5,0,-1]]]],NEGATIVES,[NEGATIVES.replace('<0','<=0'),NEGATIVES.replace('row-=1','column+=1')],['Counts zeros as negative.','Moves right after finding a negative suffix and counts it repeatedly.'],negatives_o,rneg,['Start at bottom-left.','A negative value means every cell to its right in that row is negative; count them and move up.','A nonnegative value means every cell above it in that column is nonnegative; move right.','Each move discards a fully classified row suffix or column prefix.'],'O(rows+cols)','O(1)',3),
1356:S('sort_by_one_bit_count',[('arr','list[int]')],'list[int]',['sorting','bit-manipulation'],['Values are nonnegative and distinct.','Sort by set-bit count, then numerical value ascending.'],[([[0,1,2,3,4,5,6,7,8]],'Bit counts group 0, then 1/2/4/8, then 3/5/6, then 7.'),([[1024,512,256,128,64,32,16,8,4,2,1]],'Equal one-bit values are sorted numerically.')],[[x] for x in [[0],[1,2],[3,1],[7,8],[0,3,5],[10,100,1000],[2,4,8,16],[15,7,3,1],[5,6,7,8],[9,10,12],[31,32,33],[1,3,7,15],[100,50,25],[0,1,3,7,15,31]]],BITS,[BITS.replace('value.bit_count()','-value.bit_count()'),BITS.replace('(value.bit_count(),value)','(value.bit_count(),-value)')],['Sorts larger bit counts first.','Breaks equal-bit-count ties by larger numerical value.'],bits_o,rbits,['Python integers expose their population count directly; it can also be computed by clearing low set bits.','Use a compound sort key (bit_count,value).','Return the sorted values.','Tuple comparison applies exactly the required primary and secondary order.'],'O(n log n)','O(n)',3),
1358:S('substrings_containing_abc',[('s','str')],'int',['sliding-window','strings'],['s contains only a, b, and c.','Count contiguous substrings containing at least one of each.'],[(['abcabc'],'Ten substrings contain all three letters.'),(['aaacb'],'Only substrings ending after both c and b and starting early enough qualify.')],[[s] for s in ['abc','acb','aaa','aabbcc','abca','cab','abcabc','aaabbbccc','abababc','ccccba','bacbac','aabcbc','ccabca','abcaaaa']],ABC,[ABC.replace('min(last.values())','max(last.values())'),ABC.replace("last={'a':-1,'b':-1,'c':-1}","last={'a':0,'b':0,'c':0}")],['Uses the latest rather than earliest last occurrence and overcounts starts.','Pretends every character appeared at index zero before it was seen.'],abc_o,rabc,['Track the most recent index of a, b, and c.','At each right endpoint, valid starts run from zero through the minimum last index.','Add min(last)+1, which is zero until all letters have appeared.','A start no later than every last occurrence includes all three; later starts miss the earliest one.'],'O(n)','O(1)',5),
1359:S('valid_pickup_delivery_orders',[('n','int')],'int',['combinatorics','dynamic-programming'],['There are n labeled pickup-delivery pairs and each delivery must follow its pickup.','Return the count modulo 1,000,000,007.'],[([1],'Only pickup then delivery is valid.'),([2],'The two pairs have six valid interleavings.')],[[n] for n in [3,4,5,6,7,8,9,10,11,12,20,50,100,500]],ORDERS,[ORDERS.replace('(2*pairs-1)','(2*pairs-2)'),ORDERS.replace('pairs*(2*pairs-1)','pairs+pairs-1')],['Uses one too few insertion slots for the new delivery.','Adds pickup and delivery choices instead of multiplying independent placements.'],orders_o,rorders,['Insert pair i into an existing valid sequence of i-1 pairs.','There are i choices for the pickup-relative placement and 2i-1 later slots for its delivery.','Multiply by i(2i-1) for each pair and reduce modulo the constant.','Removing the highest-labeled pair reverses this construction uniquely.'],'O(n)','O(1)',8),
1360:S('days_between_dates',[('date1','str'),('date2','str')],'int',['math','dates'],['Dates are valid ISO YYYY-MM-DD from 1971 through 2100.','Return the nonnegative absolute day difference.'],[(['2019-06-29','2019-06-30'],'The dates are one day apart.'),(['2020-01-15','2019-12-31'],'Crossing the year boundary gives fifteen days.')],[[a,b] for a,b in [('1971-01-01','1971-01-01'),('1971-01-01','1971-01-02'),('1971-01-31','1971-02-01'),('2019-02-28','2019-03-01'),('2020-02-28','2020-03-01'),('2000-02-28','2000-03-01'),('2100-02-28','2100-03-01'),('1999-12-31','2000-01-01'),('2000-01-01','1999-01-01'),('1980-06-15','1981-06-15'),('1971-01-01','2100-12-31'),('2024-02-29','2024-03-01'),('2010-05-20','2010-04-20'),('2099-12-31','2100-01-01')]],DATES,[DATES.replace('28+leap(year)','28'),'''def days_between_dates(date1, date2):
 from datetime import date
 a=date.fromisoformat(date1);b=date.fromisoformat(date2);return (a-b).days
'''],['Treats every February as 28 days and fails leap-year crossings.','Returns a negative value when date1 precedes date2.'],dates_o,rdates,['Convert each date to a serial day count from a fixed epoch.','Add complete years with leap days, complete months using the current year’s February length, and the day.','Return the absolute difference of the two serial values.','Equal epoch offsets cancel, leaving exactly the number of crossed midnights.'],'O(year range)','O(1)',5),
1361:S('validates_binary_tree_nodes',[('n','int'),('left_child','list[int]'),('right_child','list[int]')],'bool',['graphs','trees'],['Each child entry is -1 or a node index.','All n nodes must form exactly one rooted binary tree.'],[([4,[1,-1,3,-1],[2,-1,-1,-1]],'Node zero is the unique root and reaches every node exactly once.'),([4,[1,-1,3,-1],[2,3,-1,-1]],'Node three has two parents, so the structure is invalid.')],[[n,l,r] for n,l,r in [(1,[-1],[-1]),(2,[1,-1],[-1,-1]),(2,[-1,-1],[1,-1]),(2,[1,0],[-1,-1]),(3,[1,-1,-1],[2,-1,-1]),(3,[1,-1,-1],[1,-1,-1]),(3,[-1,-1,-1],[-1,-1,-1]),(3,[1,2,-1],[-1,-1,-1]),(4,[1,-1,3,-1],[2,-1,-1,-1]),(4,[1,-1,-1,-1],[2,-1,-1,-1]),(4,[1,2,3,-1],[-1,-1,-1,-1]),(4,[1,-1,-1,-1],[2,3,-1,-1]),(5,[1,3,-1,-1,-1],[2,4,-1,-1,-1]),(3,[1,-1,0],[-1,2,-1]),(4,[1,-1,3,2],[-1,-1,-1,-1])]],TREE,[TREE.replace('return len(seen)==n','return True'),'''def validates_binary_tree_nodes(n, left_child, right_child):
 return sum(child!=-1 for child in left_child+right_child)==n-1
'''],['Accepts disconnected nodes after validating only the reachable component.','Checks only edge count and misses cycles or multiple parents.'],tree_o,rtree,['A tree has one root of indegree zero and every other node indegree one.','Reject multiple parents, then identify the unique root.','Traverse from the root, rejecting revisits, and require exactly n visited nodes.','These checks enforce unique parenthood, acyclicity, and connectedness—the defining tree properties.'],'O(n)','O(n)',5),
}
BATCH[1344]['comparator']='float'
BATCH[1356]['sample_contract_adapter']={'source_sample':'Input arr = [0,1,2,3,4,5,6,7,8] → Output [0,1,2,4,8,3,5,6,7] Explantion: The integers 0 through 8 are ordered by set-bit count, with numerical order breaking ties.','arguments':[[0,1,2,3,4,5,6,7,8]],'expected':[0,1,2,4,8,3,5,6,7],'reason':'The workbook appends a misspelled Explanation section to the output; the adapter preserves the stated input and result while normalizing that prose.'}
