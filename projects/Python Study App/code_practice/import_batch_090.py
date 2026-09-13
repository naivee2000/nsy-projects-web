"""First half of batch 90: intervals, matrices, search, and counting."""
from collections import Counter
from math import ceil
from .import_batch_055 import entry

def remove_o(a):
 intervals,cut=a;out=[]
 for l,r in intervals:
  if l<cut[0]:out.append([l,min(r,cut[0])])
  if r>cut[1]:out.append([max(l,cut[1]),r])
 return [x for x in out if x[0]<x[1]]
def game_o(a):
 board=[[None]*3 for _ in range(3)]
 for i,(r,c) in enumerate(a[0]):
  player='A' if i%2==0 else 'B';board[r][c]=player
  lines=[board[r], [board[x][c] for x in range(3)]]
  if r==c:lines.append([board[x][x] for x in range(3)])
  if r+c==2:lines.append([board[x][2-x] for x in range(3)])
  if [player]*3 in lines:return player
 return 'Draw' if len(a[0])==9 else 'Pending'
def burgers_o(a):
 t,c=a
 for jumbo in range(c+1):
  if 4*jumbo+2*(c-jumbo)==t:return [jumbo,c-jumbo]
 return []
def squares_o(a):
 g=a[0];h=len(g);w=len(g[0]);ans=0
 for i in range(h):
  for j in range(w):
   for size in range(1,min(h-i,w-j)+1):ans+=all(g[x][y] for x in range(i,i+size) for y in range(j,j+size))
 return ans
def digits_o(a):
 ds=list(map(int,str(a[0])));p=1
 for d in ds:p*=d
 return p-sum(ds)
def divisor_o(a):
 nums,t=a
 for d in range(1,max(nums)+1):
  if sum((x+d-1)//d for x in nums)<=t:return d
def quarter_o(a):
 n=len(a[0]);return next(x for x,c in Counter(a[0]).items() if c*4>n)
def covered_o(a):
 iv=a[0];return sum(not any(i!=j and a<=l and r<=b for j,(a,b) in enumerate(iv)) for i,(l,r) in enumerate(iv))
def sequential_o(a):
 low,high=a;values=[]
 for first in range(1,9):
  value=first
  for digit in range(first+1,10):value=value*10+digit;values.append(value)
 return sorted(value for value in values if low<=value<=high)
def even_o(a):return sum(len(str(abs(x)))%2==0 for x in a[0])

def rr(r):
 pts=sorted(r.sample(range(-20,21),2*r.randint(1,6)));iv=[[pts[i],pts[i+1]] for i in range(0,len(pts),2)];x,y=sorted(r.sample(range(-20,21),2));return [iv,[x,y]]
def rgame(r):
 cells=[[i//3,i%3] for i in range(9)];r.shuffle(cells);moves=[]
 for cell in cells[:r.randint(1,9)]:
  moves.append(cell)
  if game_o([moves]) in {'A','B'}:break
 return [moves]
def rb(r):return [2*r.randint(0,20)+2*r.randint(0,20),r.randint(0,20)]
def rsq(r):
 h,w=r.randint(1,5),r.randint(1,5);return [[[r.randint(0,1) for _ in range(w)] for _ in range(h)]]
def rd(r):return [r.randint(1,10**9)]
def rdiv(r):
 nums=[r.randint(1,100) for _ in range(r.randint(1,12))];return [nums,r.randint(len(nums),sum(nums))]
def rq(r):
 n=r.randint(5,30);winner=r.randint(-20,20);count=n//4+1
 others=[value for value in range(-50,51) if value!=winner][:n-count]
 return [sorted([winner]*count+others)]
def rcov(r):
 out=[]
 while len(out)<r.randint(1,10):
  x,y=sorted(r.sample(range(0,30),2));p=[x,y]
  if p not in out:out.append(p)
 return [out]
def rseq(r):
 low=r.randint(10,10**8);return [low,min(10**9-1,low+r.randint(0,200000))]
def reven(r):return [[r.randint(1,10**9) for _ in range(r.randint(1,30))]]

REMOVE='''def remove_interval(intervals, to_be_removed):
 answer=[];a,b=to_be_removed
 for left,right in intervals:
  if right<=a or left>=b:answer.append([left,right])
  else:
   if left<a:answer.append([left,a])
   if right>b:answer.append([b,right])
 return answer
'''
GAME='''def tic_tac_toe_result(moves):
 rows=[0]*3;cols=[0]*3;diag=anti=0
 for i,(r,c) in enumerate(moves):
  value=1 if i%2==0 else -1;rows[r]+=value;cols[c]+=value
  if r==c:diag+=value
  if r+c==2:anti+=value
  if 3 in (abs(rows[r]),abs(cols[c]),abs(diag),abs(anti)):return 'A' if value==1 else 'B'
 return 'Draw' if len(moves)==9 else 'Pending'
'''
BURGERS='''def burger_counts(tomato_slices, cheese_slices):
 jumbo=(tomato_slices-2*cheese_slices)//2;small=cheese_slices-jumbo
 return [jumbo,small] if jumbo>=0 and small>=0 and 4*jumbo+2*small==tomato_slices else []
'''
SQUARES='''def count_all_one_squares(matrix):
 dp=[0]*(len(matrix[0])+1);answer=0
 for row in matrix:
  previous=0
  for j,value in enumerate(row,1):
   old=dp[j];dp[j]=1+min(dp[j],dp[j-1],previous) if value else 0;answer+=dp[j];previous=old
 return answer
'''
DIGITS='''def digit_product_minus_sum(n):
 product=1;total=0
 while n:digit=n%10;product*=digit;total+=digit;n//=10
 return product-total
'''
DIVISOR='''def smallest_threshold_divisor(nums, threshold):
 left,right=1,max(nums)
 while left<right:
  middle=(left+right)//2
  if sum((x+middle-1)//middle for x in nums)<=threshold:right=middle
  else:left=middle+1
 return left
'''
QUARTER='''def more_than_quarter_value(arr):
 n=len(arr)
 for i in range(n-n//4):
  if arr[i]==arr[i+n//4]:return arr[i]
'''
COVERED='''def remaining_uncovered_intervals(intervals):
 intervals=sorted(intervals,key=lambda x:(x[0],-x[1]));right=-float('inf');answer=0
 for left,end in intervals:
  if end>right:answer+=1;right=end
 return answer
'''
SEQUENTIAL='''def sequential_digits_in_range(low, high):
 digits='123456789';answer=[]
 for length in range(2,10):
  for start in range(10-length):
   value=int(digits[start:start+length])
   if low<=value<=high:answer.append(value)
 return sorted(answer)
'''
EVEN='''def count_even_digit_numbers(nums):
 return sum(len(str(value))%2==0 for value in nums)
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(1)',d=3):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1272:S('remove_interval',[('intervals','list[list[int]]'),('to_be_removed','list[int]')],'list[list[int]]',['intervals','arrays'],['Input intervals are sorted and pairwise disjoint.','Remove the half-open interval and retain nonempty fragments.'],[([[[0,2],[3,4],[5,7]],[1,6]],'The removal leaves fragments [0,1] and [6,7].'),([[[0,5]],[2,3]],'A middle removal splits one interval into two fragments.')],[[x,c] for x,c in [([[0,1]],[2,3]),([[0,4]],[0,4]),([[0,4]],[1,3]),([[0,2],[4,6]],[2,4]),([[-5,-1],[1,5]],[-2,3]),([[1,2],[3,5]],[0,10]),([[1,10]],[5,20]),([[1,10]],[-5,5]),([[0,1],[2,3],[4,5]],[2,3]),([[0,10]],[3,7]),([[0,2],[3,8]],[1,4]),([[-10,0]],[0,1]),([[5,9]],[1,5]),([[1,3],[5,7]],[3,5])]],REMOVE,['''def remove_interval(intervals, to_be_removed):
 a,b=to_be_removed
 return [[left,right] for left,right in intervals if right<=a or left>=b]
''',REMOVE.replace('if right>b','if right>=b')],['Drops an entire overlapping interval instead of preserving its outside fragments.','Emits a zero-length right fragment when endpoints coincide.'],remove_o,rr,['Process each disjoint interval independently.','Keep disjoint intervals; for overlap, retain the portions strictly left of a and right of b.','Append only nonempty fragments in traversal order.','Set subtraction from one interval can create at most those two fragments.'],'O(n)','O(n)',5),
1275:S('tic_tac_toe_result',[('moves','list[list[int]]')],'str',['simulation','matrices'],['Moves alternate A then B and target empty cells.','Return A, B, Draw, or Pending.'],[([[[0,0],[2,0],[1,1],[2,1],[2,2]]],'A completes the main diagonal.'),([[[0,0],[1,1]]],'No winner exists and empty cells remain, so the game is pending.')],[[m] for m in [[[0,0]],[[0,0],[1,1],[0,1],[2,2],[0,2]],[[0,0],[1,0],[0,1],[1,1],[2,2],[1,2]],[[0,0],[0,1],[1,0],[1,1],[2,2],[2,1],[0,2]],[[1,1],[0,0],[0,1],[2,0],[2,1],[1,0],[1,2],[2,2],[0,2]],[[2,0],[0,0],[2,1],[1,1],[2,2]],[[0,2],[0,0],[1,1],[1,0],[2,0]],[[0,0],[0,1],[2,2],[1,1],[1,2],[2,1],[2,0],[0,2],[1,0]],[[1,0],[0,0],[1,1],[0,1],[2,2]],[[0,1],[0,0],[1,1],[1,0],[2,1]],[[2,2],[1,1],[2,1],[0,0],[2,0]],[[1,1],[0,1],[1,0],[0,0],[1,2]],[[0,0],[2,2],[2,0],[1,1],[1,0]],[[2,0],[1,0],[2,1],[1,1],[0,0],[1,2]]]],GAME,[GAME.replace("value=1 if i%2==0 else -1","value=-1 if i%2==0 else 1"),GAME.replace("'Draw' if len(moves)==9 else 'Pending'","'Pending'")],['Assigns the first move to B.','Never reports a full-board draw.'],game_o,rgame,['Encode A moves as +1 and B moves as -1.','Update the chosen row, column, and applicable diagonals.','An absolute total of three declares the current player; otherwise full board means Draw.','Three equal marks are exactly a signed sum of ±3.'],'O(moves)','O(1)',3),
1276:S('burger_counts',[('tomato_slices','int'),('cheese_slices','int')],'list[int]',['math','algebra'],['Jumbo burgers use four tomato slices; small burgers use two; both use one cheese slice.','Return [jumbo,small] or an empty list.'],[([16,7],'Solving the two equations gives one jumbo and six small burgers.'),([17,4],'An odd tomato count cannot be consumed exactly.')],[[t,c] for t,c in [(0,0),(2,1),(4,1),(4,2),(6,2),(8,3),(10,3),(12,4),(1,1),(20,2),(100,25),(100,50),(6,4),(40,15)]],BURGERS,[BURGERS.replace('//2','//4'),BURGERS.replace('jumbo>=0 and small>=0','jumbo>0 and small>0')],['Solves the tomato difference with the wrong divisor.','Rejects valid solutions containing zero of one burger type.'],burgers_o,rb,['Use j+s=cheese and 4j+2s=tomato.','Subtract twice the cheese equation to get 2j=tomato-2*cheese.','Compute both counts and validate nonnegativity and exact consumption.','The linear system has at most one integer solution.'],'O(1)','O(1)',3),
1277:S('count_all_one_squares',[('matrix','list[list[int]]')],'int',['matrices','dynamic-programming'],['matrix is nonempty and binary.','Count square submatrices of every size.'],[([[[0,1,1,1],[1,1,1,1],[0,1,1,1]]],'There are ten 1x1, four 2x2, and one 3x3 square.'),([[[1,0],[0,1]]],'Only the two individual one cells form squares.')],[[g] for g in [[[0]],[[1]],[[1,1]],[[1],[1]],[[1,1],[1,1]],[[1,0],[1,1]],[[1,1,1],[1,1,1]],[[0,0],[0,0]],[[1,1,0],[1,1,0],[0,0,1]],[[1]*4 for _ in range(4)],[[0,1,0],[1,1,1],[0,1,0]],[[1,0,1],[1,1,1]],[[1],[0],[1]],[[1,1,1],[0,1,1],[1,1,1]]]],SQUARES,[SQUARES.replace('min(dp[j],dp[j-1],previous)','max(dp[j],dp[j-1],previous)'),SQUARES.replace('answer+=dp[j]','answer+=value')],['Uses the largest neighboring square and invents unsupported cells.','Counts only 1x1 squares.'],squares_o,rsq,['Let dp[j] be the largest all-one square ending at the current cell.','For a one, use one plus the minimum of upper, left, and upper-left sizes.','Add every ending size to the answer because it represents that many nested squares.','A larger square exists exactly when all three smaller neighboring squares exist.'],'O(rows*cols)','O(cols)',5),
1281:S('digit_product_minus_sum',[('n','int')],'int',['math','digits'],['1 <= n <= 100000.','Return product of decimal digits minus their sum.'],[([234],'The product 24 minus sum 9 equals 15.'),([101],'A zero digit makes the product zero, so the result is -2.')],[[n] for n in [1,9,10,11,22,99,100,123,405,999,1000,2024,55555,100000]],DIGITS,[DIGITS.replace('product=1','product=0'),DIGITS.replace('return product-total','return total-product')],['Initializes the multiplicative identity incorrectly.','Subtracts the product from the sum.'],digits_o,rd,['Extract digits with remainder modulo ten.','Accumulate their product and sum while integer-dividing n by ten.','Return product minus sum.','Each decimal digit is processed exactly once.'],'O(log n)','O(1)',3),
1283:S('smallest_threshold_divisor',[('nums','list[int]'),('threshold','int')],'int',['binary-search','arrays'],['nums is positive and threshold >= len(nums).','Find the smallest positive divisor whose rounded-up quotient sum is at most threshold.'],[([[1,2,5,9],6],'Divisor five yields 1+1+1+2=5, while four exceeds the threshold.'),([[44,22,33,11,1],5],'Only divisor 44 makes every quotient one.')],[[a,t] for a,t in [([1],1),([2],2),([2],1),([1,2],3),([1,2],2),([2,3,5],6),([2,3,5],3),([10,10],4),([10,10],2),([1,100],51),([5,9,13],7),([7,7,7],4),([1,1,1],3),([100,200,300],10)]],DIVISOR,[DIVISOR.replace('(x+middle-1)//middle','x//middle'),DIVISOR.replace('right=middle','left=middle+1')],['Uses floor rather than ceiling division.','Moves the lower bound upward when a divisor is feasible.'],divisor_o,rdiv,['The quotient sum never increases as the divisor grows.','Binary-search divisors from one through max(nums).','Use integer ceiling (x+d-1)//d and keep feasible midpoints on the right.','Monotonic feasibility makes the first feasible divisor well-defined.'],'O(n log M)','O(1)',5),
1287:S('more_than_quarter_value',[('arr','list[int]')],'int',['arrays','two-pointers'],['arr is sorted and one value appears more than 25%.','Return that value.'],[([[1,2,2,6,6,6,6,7,10]],'Six occupies four of nine positions, exceeding one quarter.'),([[1,1,2,3]],'One occupies two of four positions.')],[[x] for x in [[1],[1,1],[1,1,2],[1,2,2],[1,1,2,3],[1,2,3,3],[1,1,1,2,3],[0,0,0,1,2,3,4,5],[-2,-2,-2,-1,0],[1,2,3,4,4,4],[5,5,6,7,8],[1,1,2,2,2,3],[9,9,9,9,10,11,12],[1,2,2,2,2,3,4,5]]],QUARTER,[QUARTER.replace('i+n//4','i+n//4+1'),'''def more_than_quarter_value(arr):
 return arr[len(arr)//4]
'''],['Checks a span longer than one quarter and can miss the answer.','Assumes the answer always covers the first quarter position.'],quarter_o,rq,['In sorted order, a value over one quarter spans positions distance floor(n/4).','Scan i and compare arr[i] with arr[i+n//4].','The first equality identifies a qualifying repeated block.','Every block longer than n/4 contains such an indexed pair.'],'O(n)','O(1)',3),
1288:S('remaining_uncovered_intervals',[('intervals','list[list[int]]')],'int',['sorting','intervals'],['Intervals are distinct.','An interval is removed when another interval covers both its endpoints.'],[([[[1,4],[3,6],[2,8]]],'Only [1,4] is covered by [2,8]? It is not; [3,6] is covered, leaving two intervals.'),([[[1,4],[1,5]]],'The longer interval covers the shorter one.')],[[x] for x in [[[1,2]],[[1,2],[3,4]],[[1,4],[2,3]],[[1,4],[1,3]],[[1,3],[1,4]],[[1,10],[2,9],[3,8]],[[0,5],[5,10]],[[1,2],[1,3],[1,4]],[[1,5],[2,6]],[[0,10],[0,9],[1,10]],[[2,3],[1,4],[0,5]],[[1,6],[2,4],[3,7]],[[0,1],[0,2],[2,3]],[[5,9],[1,8],[2,7]]]],COVERED,[COVERED.replace("key=lambda x:(x[0],-x[1])","key=lambda x:(x[0],x[1])"),COVERED.replace('end>right','end>=right')],['Sorts equal starts shortest-first and wrongly counts a covered short interval.','Counts equal right endpoints as new uncovered intervals.'],covered_o,rcov,['Sort by start ascending and end descending.','Track the farthest right endpoint seen.','Count an interval only when its end extends beyond that frontier.','Earlier starts plus a no-smaller end exactly characterize coverage.'],'O(n log n)','O(n)',5),
1291:S('sequential_digits_in_range',[('low','int'),('high','int')],'list[int]',['strings','enumeration'],['10 <= low <= high < 10^9.','Every digit must be exactly one greater than its predecessor.'],[([100,300],'The qualifying numbers are 123 and 234.'),([1000,13000],'The qualifying values are 1234 and 2345 through 6789 and 12345.')],[[l,h] for l,h in [(10,12),(12,12),(12,23),(100,123),(124,234),(100,1000),(1000,10000),(10,100000000),(123456789,123456789),(200,800),(5000,7000),(10,99),(100000,900000),(99999999,999999999)]],SEQUENTIAL,[SEQUENTIAL.replace("digits='123456789'","digits='0123456789'"),SEQUENTIAL.replace('range(2,10)','range(3,10)')],['Generates values beginning with zero.','Omits every two-digit sequential number.'],sequential_o,rseq,['All answers are contiguous slices of 123456789.','Enumerate slice lengths two through nine and every valid start.','Convert each slice and keep it when it lies in the inclusive range.','There are only 36 candidate slices, so exhaustive enumeration is constant-sized.'],'O(1)','O(1)',5),
1295:S('count_even_digit_numbers',[('nums','list[int]')],'int',['arrays','digits'],['nums contains positive integers.','Count values whose decimal representation has an even number of digits.'],[([[12,345,2,6,7896]],'Twelve and 7896 have even digit counts, giving two.'),([[555,901,482,1771]],'Only 1771 has an even number of digits.')],[[x] for x in [[1],[10],[99],[100],[999],[1000],[1,22,333,4444],[10,100,1000,10000],[2,4,6],[12,34,56],[99999,100000],[7,88,999,1000],[123456],[1000000000]]],EVEN,[EVEN.replace('%2==0','%2==1'),EVEN.replace('str(value)','str(value+1)')],['Counts odd digit lengths instead.','Counts digits after incrementing the value, failing at powers of ten minus one.'],even_o,reven,['Convert each positive integer to decimal text.','Its digit count is the text length.','Increment the answer when that length is even.','Each number contributes independently and is examined once.'],'O(n log M)','O(1)',3),
}
BATCH[1276]['sample_contract_adapter']={'source_sample':'Input tomatoSlices = 16, cheeseSlices = 7 → Output [1,6] Explantion: To make one jumbo burger and 6 small burgers we need 4*1 + 2*6 = 16 tomato and 1 + 6 = 7 cheese. There will be no remaining ingredients.','arguments':[16,7],'expected':[1,6],'reason':'The workbook appended prose and a misspelled Explanation label to the output literal; the reviewed adapter preserves its two inputs and stated [1,6] result.'}
