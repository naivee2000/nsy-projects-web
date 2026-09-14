"""Third group of batch 105: greedy gains, geometry, base three, and frequencies."""
from collections import Counter
from itertools import combinations
from .import_batch_055 import entry
def equal_o(a):
 first,second=a
 if 6*len(first)<len(second) or 6*len(second)<len(first):return -1
 difference=abs(sum(first)-sum(second))
 if difference==0:return 0
 low,high=(first,second) if sum(first)<sum(second) else (second,first);gains=[6-x for x in low]+[x-1 for x in high]
 for size in range(1,len(gains)+1):
  if any(sum(chosen)>=difference for chosen in combinations(gains,size)):return size
def point_o(a):
 x,y,points=a;valid=[(abs(px-x)+abs(py-y),index) for index,(px,py) in enumerate(points) if px==x or py==y];return min(valid)[1] if valid else -1
def powers_o(a):
 n=a[0]
 while n:
  if n%3==2:return False
  n//=3
 return True
def beauty_o(a):
 s=a[0];answer=0
 for left in range(len(s)):
  for right in range(left+1,len(s)+1):
   counts=Counter(s[left:right]).values();answer+=max(counts)-min(counts)
 return answer
def segment_o(a):return '01' not in a[0]
def requal(r):return [[r.randint(1,6) for _ in range(r.randint(1,5))],[r.randint(1,6) for _ in range(r.randint(1,5))]]
def rpoint(r):return [r.randint(-5,5),r.randint(-5,5),[[r.randint(-5,5),r.randint(-5,5)] for _ in range(r.randint(1,15))]]
def rpowers(r):return [r.randint(1,10000)]
def rbeauty(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,14)))]
def rsegment(r):return [''.join(r.choice('01') for _ in range(r.randint(1,30)))]
EQUAL='''def minimum_equal_sum_operations(nums1, nums2):
 if 6*len(nums1)<len(nums2) or 6*len(nums2)<len(nums1):return -1
 if sum(nums1)>sum(nums2):nums1,nums2=nums2,nums1
 difference=sum(nums2)-sum(nums1);gains=sorted([6-value for value in nums1]+[value-1 for value in nums2],reverse=True);operations=0
 for gain in gains:
  if difference<=0:break
  difference-=gain;operations+=1
 return operations
'''
POINT='''def nearest_axis_aligned_point(x, y, points):
 best_distance=10**18;answer=-1
 for index,(px,py) in enumerate(points):
  if px==x or py==y:
   distance=abs(px-x)+abs(py-y)
   if distance<best_distance:best_distance=distance;answer=index
 return answer
'''
POWERS='''def is_sum_of_distinct_powers_of_three(n):
 while n:
  if n%3==2:return False
  n//=3
 return True
'''
BEAUTY='''def substring_beauty_sum(s):
 answer=0
 for left in range(len(s)):
  counts={}
  for right in range(left,len(s)):
   counts[s[right]]=counts.get(s[right],0)+1;values=counts.values();answer+=max(values)-min(values)
 return answer
'''
SEGMENT='''def has_at_most_one_one_segment(s):
 return '01' not in s
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1775:E('minimum_equal_sum_operations',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','greedy','sorting'],['Every value is from one through six; one operation changes one value to any other value in that range.','Return the fewest operations needed to make the array sums equal, or -1 if impossible.'],[([[1,2,3,4,5,6],[1,1,2,2,2,2]],'Using the largest available sum changes first closes the difference in three operations.'),([[1,1,1,1,1,1,1],[6]],'Even maximizing the one-element array cannot reach the minimum seven-element sum, so return -1.')],[[*x] for x in [([1,2,3,4,5,6],[1,1,2,2,2,2]),([1,1,1,1,1,1,1],[6]),([1],[1]),([1],[6]),([6],[1]),([1,1],[6]),([1,2],[3]),([6,6],[1,1]),([2,2,2],[3,3]),([1,6],[2,5]),([1,1,1],[6,6]),([3,4,5],[1,2,6]),([1,2,3],[4,5]),([6,5,4,3],[1,2,3,4])]],EQUAL,[EQUAL.replace('reverse=True','reverse=False'),EQUAL.replace('difference-=gain','difference-=gain+1')],['Uses the smallest possible improvements first instead of the largest.','Credits every operation with one more sum change than the selected element permits.'],equal_o,requal,L('Each element has a maximum useful gain toward closing the sum difference.','Orient arrays so nums1 has the smaller sum, sort all increase/decrease gains descending, and consume them.','Stop after the first prefix whose total gain reaches the difference; reject impossible length ranges first.','Any k operations can close at most the sum of the k largest gains, so the first sufficient prefix is optimal.'),'O((n+m) log(n+m))','O(n+m)',5),
1779:E('nearest_axis_aligned_point',[('x','int'),('y','int'),('points','list[list[int]]')],'int',['arrays','geometry'],['A point is valid when its x-coordinate equals x or its y-coordinate equals y.','Return the valid point with minimum Manhattan distance, breaking ties by smaller input index; return -1 if none.'],[([3,4,[[1,2],[3,1],[2,4],[2,3],[4,4]]],'Valid indices one, two, and four have distances three, one, and one, so smaller tied index two wins.'),([3,4,[[2,3]]],'The only point shares neither coordinate, so return -1.')],[[*x] for x in [(3,4,[[1,2],[3,1],[2,4],[2,3],[4,4]]),(3,4,[[2,3]]),(0,0,[[0,0]]),(0,0,[[0,2],[2,0]]),(1,1,[[1,3],[1,-1]]),(2,5,[[2,9],[3,5]]),(-1,-2,[[-1,4],[5,-2]]),(5,5,[[1,1],[2,2]]),(3,0,[[3,10],[3,1],[0,0]]),(0,4,[[0,8],[2,4],[-1,4]]),(7,7,[[7,8],[8,7],[7,6]]),(1,2,[[1,9],[1,3],[0,2]]),(0,0,[[1,0],[0,1],[-1,0]]),(4,-3,[[4,-1],[2,-3],[4,-5]])]],POINT,[POINT.replace('px==x or py==y','px==x and py==y'),POINT.replace('distance<best_distance','distance<=best_distance')],['Requires both coordinates to match instead of either one.','Replaces earlier tied points and returns the larger index.'],point_o,rpoint,L('Only axis-aligned candidates need distance comparison.','Scan points in input order and update only on a strictly smaller valid distance.','Track the best Manhattan distance and its index, leaving ties unchanged.','Filtering enforces validity, strict improvement preserves the first tied index, and scanning covers every candidate.'),'O(points)','O(1)',3),
1780:E('is_sum_of_distinct_powers_of_three',[('n','int')],'bool',['math','number-theory'],['Use each nonnegative power of three at most once.','Return whether their sum can equal n.'],[([12],'Twelve equals 9+3, using distinct powers of three.'),([21],'Base-three 210 contains digit two, so no distinct-power sum equals twenty-one.')],[[n] for n in [1,2,3,4,5,9,10,12,21,27,28,40,91,10000]],POWERS,[POWERS.replace('n%3==2','n%3==1'),POWERS.replace('n//=3','n//=2')],['Rejects required base-three digit one instead of forbidden digit two.','Examines binary digits rather than base-three digits.'],powers_o,rpowers,L('A sum of distinct powers of three has a base-three representation containing only digits zero and one.','Repeatedly inspect n modulo three and divide by three.','Return false on remainder two; otherwise continue until n is zero.','Base representation is unique, so digit two is exactly the need to reuse a power and digits zero/one construct the desired sum.'),'O(log n)','O(1)',5),
1781:E('substring_beauty_sum',[('s','str')],'int',['strings','hash-maps','counting'],['The beauty of a substring is its highest positive character frequency minus its lowest positive character frequency.','Return the sum of beauty over every substring.'],[(['aabcb'],'The nonzero beauties across all substrings sum to five.'),(['aabcbaa'],'Accumulating max-minus-min frequencies for every start and end gives seventeen.')],[[s] for s in ['aabcb','aabcbaa','a','aa','ab','aba','abc','aaaa','abb','abca','abcabc','zzxyzz','aabbcc','abacaba']],BEAUTY,[BEAUTY.replace('max(values)-min(values)','max(values)'),BEAUTY.replace('counts.get(s[right],0)+1','1')],['Omits the minimum positive frequency from each beauty calculation.','Stores character presence rather than growing substring frequencies.'],beauty_o,rbeauty,L('Fixing a left endpoint lets one frequency table serve every expanding right endpoint.','For each left index, extend right while updating one character count and adding current max minus min.','Take min only across present dictionary values, not absent alphabet letters.','Every substring appears once for its endpoint pair, and its maintained counts exactly define its beauty.'),'O(n^2*alphabet)','O(alphabet)',5),
1784:E('has_at_most_one_one_segment',[('s','str')],'bool',['strings'],['A segment of ones is a maximal contiguous run of 1 characters.','Return whether the binary string contains at most one such segment.'],[(['1001'],'The zero-to-one transition starts a second one segment, so return false.'),(['110'],'All ones form one initial segment, so return true.')],[[s] for s in ['1001','110','0','1','00','11','01','10','101','111000','000111','010','00100','1110111']],SEGMENT,[SEGMENT.replace("'01'","'10'"),SEGMENT.replace('not in s','in s')],['Rejects a one-to-zero transition even though ending the only segment is allowed.','Returns true when a second one segment is explicitly detected.'],segment_o,rsegment,L('After a one segment ends, any later one creates a second segment.','Detect whether the string contains a zero-to-one transition.','Return true exactly when substring 01 is absent.','Any 01 transition starts a one segment after zeros; without one, all ones belong to at most the initial single run.'),'O(n)','O(1)',3),
}
