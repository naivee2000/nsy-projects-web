"""Second group of batch 104: constructive math, intervals, palindromes, and greedy."""
from .import_batch_055 import entry
def boxes_o(a):
 n=a[0];height=0
 while (height+1)*(height+2)*(height+3)//6<=n:height+=1
 used=height*(height+1)*(height+2)//6;base=height*(height+1)//2;extra=0
 while used<n:extra+=1;used+=extra
 return base+extra
def candy_o(a):
 counts,queries=a;prefix=[];total=0
 for value in counts:total+=value;prefix.append(total)
 answer=[]
 for kind,day,cap in queries:
  first=1 if kind==0 else prefix[kind-1]+1;last=prefix[kind];answer.append(day+1<=last and (day+1)*cap>=first)
 return answer
def partition_o(a):
 s=a[0]
 def pal(x):return x==x[::-1]
 return any(pal(s[:i]) and pal(s[i:j]) and pal(s[j:]) for i in range(1,len(s)-1) for j in range(i+1,len(s)))
def rotated_o(a):
 nums=a[0];return sum(nums[i]>nums[(i+1)%len(nums)] for i in range(len(nums)))<=1
def stones_o(a):
 piles=a;total=sum(piles);return min(total//2,total-max(piles))
def rboxes(r):return [r.randint(1,10000)]
def rcandy(r):
 counts=[r.randint(1,20) for _ in range(r.randint(1,8))];queries=[[r.randrange(len(counts)),r.randint(0,100),r.randint(1,30)] for _ in range(r.randint(1,12))];return [counts,queries]
def rpartition(r):return [''.join(r.choice('abc') for _ in range(r.randint(3,12)))]
def rrotated(r):return [[r.randint(-5,5) for _ in range(r.randint(1,20))]]
def rstones(r):return [r.randint(1,50),r.randint(1,50),r.randint(1,50)]
BOXES='''def minimum_floor_boxes(n):
 used=floor=layer=0
 while used+layer*(layer+1)//2<=n:
  used+=layer*(layer+1)//2;floor+=layer;layer+=1
 extra=0
 while used<n:extra+=1;used+=extra
 return floor+extra
'''
CANDY='''def favorite_candy_possible(candies_count, queries):
 prefix=[];total=0
 for count in candies_count:total+=count;prefix.append(total)
 answer=[]
 for kind,day,cap in queries:
  before=0 if kind==0 else prefix[kind-1]
  answer.append(day+1<=prefix[kind] and (day+1)*cap>before)
 return answer
'''
PARTITION='''def can_split_into_three_palindromes(s):
 n=len(s);pal=[[False]*n for _ in range(n)]
 for left in range(n-1,-1,-1):
  for right in range(left,n):pal[left][right]=s[left]==s[right] and (right-left<2 or pal[left+1][right-1])
 return any(pal[0][first] and pal[first+1][second] and pal[second+1][n-1] for first in range(n-2) for second in range(first+1,n-1))
'''
ROTATED='''def is_sorted_and_rotated(nums):
 drops=sum(nums[index]>nums[(index+1)%len(nums)] for index in range(len(nums)))
 return drops<=1
'''
STONES='''def maximum_stone_removal_score(a, b, c):
 total=a+b+c
 return min(total//2,total-max(a,b,c))
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1739:E('minimum_floor_boxes',[('n','int')],'int',['math','greedy','binary-search'],['Stack n unit boxes in a cubic corner; every box not on the floor must have all four lower corners supported by boxes beneath it.','Return the minimum number of boxes touching the floor.'],[([3],'All three boxes must touch the floor, so the answer is three.'),([10],'A complete three-layer corner pyramid uses ten boxes and six floor positions.')],[[n] for n in [1,2,4,5,6,7,8,9,11,15,20,35,100,10000]],BOXES,[BOXES.replace('used+layer*(layer+1)//2<=n','used+layer*(layer+1)//2<n'),BOXES.replace('used+=extra','used+=extra+1')],['Stops before an exactly complete layer and adds an unnecessary floor box.','Credits each partial floor extension with one too many supported boxes.'],boxes_o,rboxes,L('Complete corner layers contribute triangular numbers of boxes and use one new floor row.','Build the largest complete tetrahedral stack, then extend the next floor row until the remainder is supported.','Accumulate layer*(layer+1)/2 while it fits; afterward add floor boxes whose cumulative support is 1+2+....','Complete layers are maximally support-efficient, and each extra floor box in the boundary row increases capacity by the next integer.'),'O(cube_root(n)+sqrt(n))','O(1)',8),
1744:E('favorite_candy_possible',[('candies_count','list[int]'),('queries','list[list[int]]')],'list[bool]',['arrays','prefix-sums','intervals'],['Eat at least one candy daily, never exceed the query cap, and finish each candy type before starting the next.','For [type,day,cap], report whether a candy of that type can be eaten on that zero-based day.'],[([[7,4,5,3,8],[[0,2,2],[4,2,4],[2,13,1000000000]]],'The possible-consumption interval overlaps type zero and type two for the first and third queries, but cannot reach type four by day two.'),([[5],[[0,0,1],[0,4,1],[0,5,10]]],'The only type can be eaten on days zero through four, but is exhausted before day five.')],[[*x] for x in [([7,4,5,3,8],[[0,2,2],[4,2,4],[2,13,1000000000]]),([5],[[0,0,1],[0,4,1],[0,5,10]]),([1],[[0,0,1]]),([1],[[0,1,1]]),([2,2],[[1,0,1]]),([2,2],[[1,1,1]]),([2,2],[[1,3,1]]),([10,1],[[1,0,20]]),([3,4,5],[[2,2,2]]),([3,4,5],[[1,10,1]]),([1,1,1],[[2,0,3]]),([100,1],[[1,1,100]]),([4,6],[[0,9,1],[1,4,2]]),([5,5,5],[[2,4,3],[2,3,3]])]],CANDY,[CANDY.replace('(day+1)*cap>before','(day+1)*cap>=before'),CANDY.replace('day+1<=prefix[kind]','day<prefix[kind]')],['Allows the maximum eaten count to stop before the first candy of the requested type.','Uses the zero-based day directly for the minimum eaten count.'],candy_o,rcandy,L('By a given day, total candies eaten can be any integer from day+1 through (day+1)*cap.','Compare that attainable interval with the one-based index interval occupied by the requested type.','Let before be prior-type count and through include this type; require day+1<=through and (day+1)*cap>before.','Two integer intervals overlap exactly under those inequalities, which is equivalent to eating the requested type that day.'),'O(types+queries)','O(types)',5),
1745:E('can_split_into_three_palindromes',[('s','str')],'bool',['strings','dynamic-programming'],['Split s into exactly three nonempty contiguous substrings.','Return whether all three substrings can be palindromes.'],[(['abcbdd'],'The split a | bcb | dd consists entirely of palindromes.'),(['bcbddxy'],'No two cut positions produce three palindromic pieces.')],[[s] for s in ['abcbdd','bcbddxy','aaa','abc','aba','aaaa','aabbaa','racecarxxyy','abacdcaba','aabaa','abcdcbaaa','xyzyxzz','abbacddc','abcdefedcba']],PARTITION,[PARTITION.replace('right-left<2','right-left<1'),PARTITION.replace('range(n-2)','range(1,n-2)')],['Fails to initialize adjacent equal characters as palindromes.','Never allows the first piece to have length one.'],partition_o,rpartition,L('Only palindrome status for substrings and two cut positions matter.','Precompute palindrome intervals, then enumerate the two cuts.','Fill pal[left][right] from matching endpoints and the inner interval; test pal[0][i], pal[i+1][j], and pal[j+1][n-1].','Every three-part split has exactly one cut pair, so the enumeration accepts exactly when one pair has three palindrome intervals.'),'O(n^2)','O(n^2)',8),
1752:E('is_sorted_and_rotated',[('nums','list[int]')],'bool',['arrays'],['nums may contain duplicates.','Return whether it is a nondecreasing array rotated any number of positions, including zero.'],[([[3,4,5,1,2]],'Only the circular edge from five to one decreases, so this is a rotation of sorted order.'),([[2,1,3,4]],'There are two circular decreases, so no rotation can make the order nondecreasing.')],[[x] for x in [[3,4,5,1,2],[2,1,3,4],[1],[1,2,3],[3,2,1],[2,2,2],[2,3,1],[1,1,2,1],[5,1,2,3,4],[1,3,2],[2,1],[1,2],[3,3,1,2,3],[0,-1,-1,0]]],ROTATED,[ROTATED.replace('drops<=1','drops==1'),ROTATED.replace('>nums','>=nums')],['Rejects already sorted arrays with zero rotations.','Treats equal adjacent values as decreases.'],rotated_o,rrotated,L('A sorted circular order has at most one strict decrease, at the rotation boundary.','Count strict decreases across every adjacent pair, including last-to-first.','Return whether that circular drop count is at most one.','With zero drops the array is sorted; with one, cutting after it yields sorted order; two drops cannot be repaired by one rotation cut.'),'O(n)','O(1)',3),
1753:E('maximum_stone_removal_score',[('a','int'),('b','int'),('c','int')],'int',['math','greedy'],['Each move removes one stone from each of two different nonempty piles and earns one point.','Return the maximum possible score.'],[([2,4,6],'The two smaller piles contain six stones total, allowing six moves against the largest pile.'),([4,4,6],'Seven pairs can be removed before fewer than two piles remain nonempty.')],[[*x] for x in [(2,4,6),(4,4,6),(1,1,1),(1,1,10),(1,2,3),(5,5,5),(2,2,100),(10,1,1),(3,7,8),(9,9,1),(20,30,40),(6,2,4),(100,100,1),(7,8,9)]],STONES,[STONES.replace('total-max(a,b,c)','max(a,b,c)'),STONES.replace('total//2','(total-1)//2')],['Uses the largest pile size rather than the total stones outside it as the imbalance bound.','Rounds down after subtracting one and loses a move when the total is even.'],stones_o,rstones,L('The score cannot exceed half the total stones or the number outside the largest pile.','These two upper bounds are both achievable by repeatedly pairing the largest available piles.','Return min(total//2, total-largest).','If one pile dominates, every move consumes one outside stone; otherwise stones can be paired until fewer than two remain.'),'O(1)','O(1)',5),
}
BATCH[1739]['wrong'][0]=BOXES.replace('floor+=layer','floor+=layer+1')
BATCH[1739]['wrong_reasons'][0]='Adds one nonexistent floor position for every completed corner layer.'
BATCH[1744]['wrong'][1]=CANDY.replace('day+1<=prefix[kind]','day+2<=prefix[kind]')
BATCH[1744]['wrong_reasons'][1]='Treats the requested type as exhausted one day before its last possible candy.'
