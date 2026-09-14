"""Batch 103: prefix sums, sequence mapping, arithmetic, and XOR."""
from bisect import bisect_left,bisect_right
from .import_batch_055 import entry
MOD=1_000_000_007

def split_o(a):
 nums=a[0];answer=0
 for i in range(1,len(nums)-1):
  for j in range(i+1,len(nums)):
   left=sum(nums[:i]);middle=sum(nums[i:j]);right=sum(nums[j:])
   answer+=left<=middle<=right
 return answer%MOD
def ops_o(a):
 target,arr=a;positions={value:i for i,value in enumerate(target)};mapped=[positions[x] for x in arr if x in positions]
 best=[]
 for value in mapped:
  at=bisect_left(best,value)
  if at==len(best):best.append(value)
  else:best[at]=value
 return len(target)-len(best)
def money_o(a):
 n=a[0];return sum(1+day//7+day%7 for day in range(n))
def xor_o(a):
 encoded,first=a;answer=[first]
 for value in encoded:answer.append(answer[-1]^value)
 return answer
def squares_o(a):
 rectangles=a[0];sizes=[min(x) for x in rectangles];return sizes.count(max(sizes))

def rsplit(r):return [[r.randint(0,12) for _ in range(r.randint(3,14))]]
def rops(r):
 target=r.sample(range(30),r.randint(1,12));return [target,[r.randrange(30) for _ in range(r.randint(1,25))]]
def rmoney(r):return [r.randint(1,1000)]
def rxor(r):
 nums=[r.randint(0,255) for _ in range(r.randint(1,20))];return [[nums[i]^nums[i+1] for i in range(len(nums)-1)],nums[0]]
def rsquares(r):return [[[r.randint(1,30),r.randint(1,30)] for _ in range(r.randint(1,20))]]

SPLIT='''def good_three_way_split_count(nums):
 from bisect import bisect_left,bisect_right
 prefix=[];total=0
 for value in nums:total+=value;prefix.append(total)
 answer=0
 for left_end in range(len(nums)-2):
  first=bisect_left(prefix,2*prefix[left_end],left_end+1,len(nums)-1)
  last=bisect_right(prefix,(total+prefix[left_end])//2,first,len(nums)-1)
  answer+=last-first
 return answer%1000000007
'''
OPS='''def minimum_subsequence_insertions(target, arr):
 from bisect import bisect_left
 positions={value:index for index,value in enumerate(target)};tails=[]
 for value in arr:
  if value not in positions:continue
  index=positions[value];at=bisect_left(tails,index)
  if at==len(tails):tails.append(index)
  else:tails[at]=index
 return len(target)-len(tails)
'''
MONEY='''def total_bank_savings(n):
 weeks,remainder=divmod(n,7)
 return 28*weeks+7*weeks*(weeks-1)//2+remainder*(weeks+1)+remainder*(remainder-1)//2
'''
XOR='''def decode_xored_array(encoded, first):
 answer=[first]
 for value in encoded:answer.append(answer[-1]^value)
 return answer
'''
SQUARES='''def count_largest_square_rectangles(rectangles):
 largest=max(min(length,width) for length,width in rectangles)
 return sum(min(length,width)==largest for length,width in rectangles)
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1712:E('good_three_way_split_count',[('nums','list[int]')],'int',['arrays','prefix-sums','binary-search'],['nums has 3–100,000 nonnegative integers.','Split it into three nonempty contiguous parts and count splits with left sum <= middle sum <= right sum, modulo 1,000,000,007.'],[([[1,1,1]],'Only [1], [1], [1] satisfies both inequalities.'),([[1,2,2,2,5,0]],'The three valid boundary pairs produce the required count three.')],[[x] for x in [[1,1,1],[1,2,2,2,5,0],[3,2,1],[0,0,0],[0,0,0,0],[1,0,1],[1,1,2,2],[5,0,0],[1,3,1,5],[2,2,2,2,2],[0,1,0,1,0],[4,1,3,2,8],[1,1,1,1,1,1],[10,0,10,0,20]]],SPLIT,[SPLIT.replace('2*prefix[left_end]','2*prefix[left_end]+1'),SPLIT.replace('(total+prefix[left_end])//2','(total-prefix[left_end])//2')],['Requires the middle sum to be strictly greater than the left sum.','Uses the remaining total rather than the prefix-coordinate upper boundary.'],split_o,rsplit,L('Nonnegative values make prefix sums sorted, so valid middle endpoints form one interval.','For every left endpoint, binary-search the first middle sum at least left and the last at most right.','Search prefix >= 2*left and prefix <= floor((total+left)/2), excluding the final index.','These two bounds are algebraically equivalent to left<=middle and middle<=right; every boundary pair is counted once.'),'O(n log n)','O(n)',5),
1713:E('minimum_subsequence_insertions',[('target','list[int]'),('arr','list[int]')],'int',['arrays','binary-search','longest-increasing-subsequence'],['target contains distinct integers; arr may contain duplicates.','Insert the fewest values anywhere in arr so target becomes a subsequence.'],[([[5,1,3],[9,4,2,3,4]],'Only target value three is already in order, so two insertions are needed.'),([[6,4,8,1,3,2],[4,7,6,2,3,8,6,1]],'A longest target-ordered subsequence has length three, requiring three insertions.')],[[*x] for x in [([5,1,3],[9,4,2,3,4]),([6,4,8,1,3,2],[4,7,6,2,3,8,6,1]),([1],[1]),([1],[2]),([1,2,3],[1,2,3]),([1,2,3],[3,2,1]),([3,1,2],[3,3,1,2]),([1,3,5],[1,2,3,4,5]),([9,8,7],[9,7]),([2,4,6,8],[8,2,4,6]),([5,4,3,2,1],[1,2,3,4,5]),([10,20,30],[20,10,30]),([0,-1,2],[-1,0,2]),([7,3,9,1],[7,9,3,1])]],OPS,[OPS.replace('bisect_left(tails,index)','bisect_right(tails,index)'),OPS.replace('return len(target)-len(tails)','return len(arr)-len(tails)')],['Allows duplicate mapped positions to extend the subsequence.','Subtracts from arr length instead of the required target length.'],ops_o,rops,L('Distinct target values map the problem to keeping an increasing sequence of target indices.','Map arr values that occur in target, then find the LIS length.','Maintain minimal tail indices with lower-bound replacement; answer target length minus tails length.','Increasing mapped indices are exactly a target subsequence, and every missing target member needs one insertion.'),'O((n+m) log n)','O(n)',8),
1716:E('total_bank_savings',[('n','int')],'int',['math','simulation'],['Save for n consecutive days, starting with $1 on Monday.','Each next weekday adds $1, while each new Monday starts $1 above the previous Monday.'],[([4],'The first four deposits are 1, 2, 3, and 4, totaling 10.'),([10],'A full first week contributes 28 and the next Monday through Wednesday contribute 2+3+4, totaling 37.')],[[n] for n in [1,2,4,7,8,10,14,15,20,21,28,35,70,1000]],MONEY,[MONEY.replace('7*weeks*(weeks-1)//2','7*weeks*(weeks+1)//2'),MONEY.replace('remainder*(weeks+1)','remainder*weeks')],['Raises every completed week by one extra dollar per day.','Starts the partial week one dollar too low.'],money_o,rmoney,L('Whole weeks are arithmetic sequences, as are the remaining weekday deposits.','Split n into complete weeks and a remainder.','Sum 28 per base week plus the increasing Monday offsets, then add the partial week starting at weeks+1.','The formula partitions every deposit by week and weekday exactly once.'),'O(1)','O(1)',3),
1720:E('decode_xored_array',[('encoded','list[int]'),('first','int')],'list[int]',['arrays','bit-manipulation'],['encoded[i] equals original[i] XOR original[i+1].','Given the first original value, reconstruct the full array.'],[([[1,2,3],1],'Successive XORs reconstruct [1,0,2,1].'),([[6,2,7,3],4],'Starting at four and undoing each adjacent XOR yields [4,2,0,7,4].')],[[*x] for x in [([],0),([],9),([1],0),([1],1),([1,2,3],1),([6,2,7,3],4),([0,0],5),([255],128),([3,3,3],3),([10,20],7),([0],0),([7,0,7],12),([1,1,0,1],1),([31,16,8],4)]],XOR,[XOR.replace('answer[-1]^value','first^value'),XOR.replace('answer=[first]','answer=[0]')],['Decodes every position from the first value rather than the previous decoded value.','Assumes the first decoded value is zero instead of using the supplied first value.'],xor_o,rxor,L('XOR is its own inverse: if a XOR b=e, then b=a XOR e.','Start with first and process encoded from left to right.','Append answer[-1] XOR encoded[i] for every encoded value.','Induction shows each append reconstructs the unique next original value.'),'O(n)','O(n)',3),
1725:E('count_largest_square_rectangles',[('rectangles','list[list[int]]')],'int',['arrays','counting'],['Each rectangle is [length,width] with positive sides.','Its largest inscribed square has side min(length,width); count rectangles attaining the maximum such side.'],[([[[5,8],[3,9],[5,12],[16,5]]],'Three rectangles support side five, the largest available.'),([[[2,3],[3,7],[4,3],[3,7]]],'Three rectangles support the maximum side three.')],[[r] for r in [[[5,8],[3,9],[5,12],[16,5]],[[2,3],[3,7],[4,3],[3,7]],[[1,1]],[[1,2],[2,1]],[[4,4],[3,10]],[[6,5],[5,6]],[[2,8],[3,3],[9,2]],[[10,1],[1,10]],[[7,7],[7,8],[8,7]],[[3,4],[4,5],[5,6]],[[9,2],[8,3],[7,4]],[[2,2],[2,2],[2,2]],[[1,9],[5,5],[6,4]],[[30,20],[20,30],[25,25]]]],SQUARES,[SQUARES.replace('min(length,width)','max(length,width)'),SQUARES.replace('==largest','<largest')],['Uses the longer rectangle side, which cannot fit inside the shorter side.','Counts rectangles below the maximum instead of tied at it.'],squares_o,rsquares,L('A square is limited by the shorter side of its rectangle.','Compute every shorter side, find their maximum, and count its occurrences.','Let largest=max(min(length,width)); return the number of rectangles with that minimum.','This directly evaluates each rectangle’s maximum square and counts precisely the global maximizers.'),'O(n)','O(1)',3),
}
