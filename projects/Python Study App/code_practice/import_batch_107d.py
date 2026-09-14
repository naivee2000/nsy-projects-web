"""Final reviewed group of workbook batch 107."""
from collections import Counter
from .import_batch_055 import entry
def duplicate_o(a):
 values=a[0];counts=Counter(values);return [value for value in values if counts[value]==1]
def base_o(a):
 n,k=a;digits=[]
 while n:digits.append(n%k);n//=k
 return sum(digits)
def frequency_o(a):
 nums,k=a;best=1
 for target in range(min(nums),max(nums)+k+1):
  costs=sorted(target-value for value in nums if value<=target);spent=0
  for count,cost in enumerate(costs,1):
   spent+=cost
   if spent<=k:best=max(best,count)
 return best
def vowels_o(a):
 word=a[0];best=0
 for left in range(len(word)):
  for right in range(left,len(word)):
   part=word[left:right+1]
   if set(part)==set('aeiou') and all(part[i]<=part[i+1] for i in range(len(part)-1)):best=max(best,len(part))
 return best
def building_o(a):
 n,restrictions=a;limits={1:0,**{index:height for index,height in restrictions}}
 return max(min(height+abs(position-index) for index,height in limits.items()) for position in range(1,n+1))
def rduplicate(r):return [[r.randint(-5,5) for _ in range(r.randint(0,15))]]
def rbase(r):return [r.randint(1,10000),r.randint(2,10)]
def rfrequency(r):return [[r.randint(1,20) for _ in range(r.randint(1,10))],r.randint(0,30)]
def rvowels(r):return [''.join(r.choice('aeiou') for _ in range(r.randint(1,15)))]
def rbuilding(r):
 n=r.randint(2,12);positions=r.sample(range(2,n+1),r.randint(0,n-1));return [n,[[position,r.randint(0,n+5)] for position in positions]]
DUPLICATE='''def remove_all_duplicate_values(head):
 from collections import Counter
 counts=Counter();node=head
 while node:counts[node.val]+=1;node=node.next
 dummy=ListNode(0,head);previous=dummy;node=head
 while node:
  if counts[node.val]>1:previous.next=node.next
  else:previous=node
  node=node.next
 return dummy.next
'''
BASE='''def digit_sum_in_base(n, k):
 answer=0
 while n:answer+=n%k;n//=k
 return answer
'''
FREQUENCY='''def maximum_frequency_after_increments(nums, k):
 nums=sorted(nums);left=0;total=0;answer=1
 for right,value in enumerate(nums):
  total+=value
  while value*(right-left+1)-total>k:total-=nums[left];left+=1
  answer=max(answer,right-left+1)
 return answer
'''
VOWELS='''def longest_ordered_vowel_substring(word):
 answer=0;start=0;groups=1
 for index in range(1,len(word)):
  if word[index]<word[index-1]:start=index;groups=1
  elif word[index]>word[index-1]:groups+=1
  if groups==5:answer=max(answer,index-start+1)
 return answer
'''
BUILDING='''def maximum_building_height(n, restrictions):
 limits=[item[:] for item in restrictions]+[[1,0]];limits.sort()
 if limits[-1][0]!=n:limits.append([n,n-1])
 for index in range(1,len(limits)):limits[index][1]=min(limits[index][1],limits[index-1][1]+limits[index][0]-limits[index-1][0])
 for index in range(len(limits)-2,-1,-1):limits[index][1]=min(limits[index][1],limits[index+1][1]+limits[index+1][0]-limits[index][0])
 return max((left_height+right_height+right-left)//2 for (left,left_height),(right,right_height) in zip(limits,limits[1:]))
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1836:E('remove_all_duplicate_values',[('head','ListNode | None')],'ListNode | None',['linked-lists','hash-maps'],['Remove every node whose value occurs more than once anywhere in the unsorted list.','Preserve the original relative order of values occurring exactly once.'],[([[1,2,3,2]],'Value two occurs twice, so both two-nodes are removed and [1,3] remains.'),([[1,1,1,2,3]],'All one-nodes are removed, leaving [2,3].')],[[x] for x in [[],[1],[1,1],[1,2],[1,2,3,2],[1,1,1,2,3],[1,2,1,2],[3,2,1],[0,0,1],[1,2,3,3,2,1],[5,4,5,3],[2,2,3,4,4],[1,-1,1],[7,8,9,8]]],DUPLICATE,[DUPLICATE.replace('counts[node.val]>1','counts[node.val]>2'),DUPLICATE.replace('previous.next=node.next','previous=node')],['Keeps values that occur exactly twice.', 'Advances over duplicates without unlinking them.'],duplicate_o,rduplicate,H('First learn global value frequencies; a one-pass local check cannot know future duplicates.','Count values, then traverse again behind a dummy node.','Unlink a node when its count exceeds one; otherwise advance the retained-tail pointer.','Every node is removed exactly when its globally counted value is duplicated, and the pointer rewiring preserves all unique nodes in order.'),'O(n)','O(distinct values)',5),
1837:E('digit_sum_in_base',[('n','int'),('k','int')],'int',['math'],['n is positive and k is between two and ten.','Convert n to base k conceptually and return the sum of its digits as a decimal integer.'],[([34,6],'Thirty-four is 54 in base six, whose digits sum to nine.'),([10,10],'Ten is 10 in base ten, whose digits sum to one.')],[[*x] for x in [(1,2),(2,2),(34,6),(10,10),(10,2),(255,8),(100,3),(9,3),(8,2),(31,5),(999,10),(64,8),(1234,7),(5,6)]],BASE,[BASE.replace('answer+=n%k','answer+=n//k'),BASE.replace('n//=k','n//=10')],['Adds the quotient rather than the next base-k digit.', 'Peels decimal digits instead of base-k digits.'],base_o,rbase,H('Repeated division by k exposes one base-k digit at a time.','The remainder n%k is the current least-significant digit.','Add the remainder, replace n by n//k, and stop at zero.','Euclidean division uniquely decomposes n into base-k digits, so the loop visits and sums each digit exactly once.'),'O(log_k n)','O(1)',3),
1838:E('maximum_frequency_after_increments',[('nums','list[int]'),('k','int')],'int',['arrays','sorting','sliding-window','greedy'],['At most k operations may each increment one element by one; decrements are forbidden.','Return the largest achievable frequency of a single value.'],[([[1,2,4],5],'Raise one and two to four using five increments, making frequency three.'),([[1,4,8,13],5],'At most two values can be made equal within five increments.')],[[*x] for x in [([1],0),([1,2,4],5),([1,4,8,13],5),([3,9,6],2),([1,1,1],0),([1,1,2],1),([5,4,3,2,1],10),([10,10,1],9),([2,2,4,4],4),([1,5,5],4),([1,2,2,3],2),([7,1,7],6),([1,10],8),([4,6,8,10],6)]],FREQUENCY,[FREQUENCY.replace('>k','>=k'),FREQUENCY.replace('total-=nums[left]','total+=nums[left]')],['Shrinks a window whose cost exactly equals the allowed budget.', 'Increases rather than decreases the window sum when removing its left value.'],frequency_o,rfrequency,H('After sorting, an optimal group is a contiguous window raised to its rightmost value.','Maintain the window sum so its raising cost is target*length-sum.','Move left while cost exceeds k and track the largest valid window.','Any skipped value between chosen sorted values costs no more than a chosen smaller value, so an optimal selection is contiguous and the sliding window considers it.'),'O(n log n)','O(n)',7),
1839:E('longest_ordered_vowel_substring',[('word','str')],'int',['strings','sliding-window'],['word contains only vowels; a beautiful substring has one or more of each a,e,i,o,u in nondecreasing order.','Return the greatest beautiful-substring length, or zero if none exists.'],[(['aeiaaioaaaaeiiiiouuuooaauuaeiu'],'The longest ordered run containing all five vowel groups has length thirteen.'),(['aeeeiiiioooauuuaeiou'],'The final aeiou is the longest complete ordered run, length five.')],[[s] for s in ['a','aeiou','uuuuu','aeiaaioaaaaeiiiiouuuooaauuaeiu','aeeeiiiioooauuuaeiou','aaaaeeeeiiiioooouuuu','aeio','aaeiiouu','uoiea','aeiouaeiou','aaaeeeiioou','eeeiioouu','aeeeiou','aaeeiioouu']],VOWELS,[VOWELS.replace('groups==5','groups>=4'),VOWELS.replace('word[index]<word[index-1]','word[index]<=word[index-1]')],['Accepts substrings missing one vowel group.', 'Restarts on repeated vowels and loses valid runs.'],vowels_o,rvowels,H('Within a candidate run, vowel characters may stay equal or increase but never decrease.','Track the run start and the number of strict vowel transitions.', 'Reset on a decrease; a run becomes beautiful after reaching five distinct vowel groups.','Because the alphabet is restricted to vowels, a nondecreasing run with five groups contains all five in order; every decrease is a necessary boundary.'),'O(n)','O(1)',5),
1840:E('maximum_building_height',[('n','int'),('restrictions','list[list[int]]')],'int',['arrays','sorting','math','greedy'],['Building one has height zero; adjacent nonnegative heights differ by at most one.','Each [index,max_height] is an upper bound; return the greatest achievable height anywhere.'],[([5,[[2,1],[4,1]]],'The restrictions allow a peak of two at building five.'),([6,[]],'Without additional restrictions, heights can rise from zero to five.')],[[*x] for x in [(2,[]),(5,[[2,1],[4,1]]),(6,[]),(10,[[5,3],[2,5],[7,4],[10,3]]),(3,[[2,0]]),(4,[[4,0]]),(8,[[3,1],[6,1]]),(5,[[5,10]]),(7,[[2,0],[7,0]]),(9,[[5,2]]),(6,[[3,3]]),(10,[[2,1],[9,2]]),(4,[[2,1],[3,1]]),(12,[[4,2],[8,3],[11,1]])]],BUILDING,[BUILDING.replace('min(limits[index][1]','max(limits[index][1]',1),BUILDING.replace('//2','//3')],['Loosens a restriction during the forward feasibility pass.', 'Divides the feasible peak formula by three instead of two.'],building_o,rbuilding,H('Restrictions constrain each other through the adjacent slope limit.', 'Add [1,0], sort, then tighten heights left-to-right and right-to-left.', 'Between consecutive feasible endpoints, the highest peak is floor((left_height+right_height+distance)/2).','The two passes compute tight endpoint caps; rising from both ends at slope one meets at that formula, giving both an upper bound and a constructible peak.'),'O(r log r)','O(r)',8),
}
BATCH[1836]['params'][0]=('head','ListNode | None','listnode')
BATCH[1836]['adapter']='listnode'
