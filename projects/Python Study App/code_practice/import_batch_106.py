"""First reviewed group of workbook batch 106."""
from itertools import product
from .import_batch_055 import entry


def center_o(a):
 edges=a[0];counts={}
 for u,v in edges:counts[u]=counts.get(u,0)+1;counts[v]=counts.get(v,0)+1
 return max(counts,key=counts.get)
def ratio_o(a):
 classes,extra=a;best=0.0
 for assignment in product(range(len(classes)),repeat=extra):
  added=[0]*len(classes)
  for index in assignment:added[index]+=1
  best=max(best,sum((passed+added[i])/(total+added[i]) for i,(passed,total) in enumerate(classes))/len(classes))
 return best
def score_o(a):
 nums,k=a;return max(min(nums[left:right+1])*(right-left+1) for left in range(k+1) for right in range(k,len(nums)))
def quadruples_o(a):
 first,second=a;matches=[]
 for i in range(len(first)):
  for j in range(i,len(first)):
   for start in range(len(second)):
    end=start+j-i
    if end<len(second) and first[i:j+1]==second[start:end+1]:matches.append((j-start,i,j,start,end))
 if not matches:return 0
 smallest=min(item[0] for item in matches);return sum(item[0]==smallest for item in matches)
def digit_o(a):
 values=sorted({int(char) for char in a[0] if char.isdigit()},reverse=True);return values[1] if len(values)>1 else -1
def rcenter(r):
 n=r.randint(3,15);center=r.randint(1,n);edges=[[center,node] if r.random()<.5 else [node,center] for node in range(1,n+1) if node!=center];r.shuffle(edges);return [edges]
def rratio(r):
 classes=[]
 for _ in range(r.randint(1,4)):
  total=r.randint(1,8);classes.append([r.randint(1,total),total])
 return [classes,r.randint(1,5)]
def rscore(r):
 nums=[r.randint(1,20) for _ in range(r.randint(1,12))];return [nums,r.randrange(len(nums))]
def rquad(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,7))),''.join(r.choice('abcd') for _ in range(r.randint(1,7)))]
def rdigit(r):return [''.join(r.choice('abcxyz0123456789') for _ in range(r.randint(1,30)))]

CENTER='''def find_star_center(edges):
 first,second=edges[0],edges[1]
 return first[0] if first[0] in second else first[1]
'''
RATIO='''def maximum_average_pass_ratio(classes, extra_students):
 import heapq
 heap=[]
 for passed,total in classes:heapq.heappush(heap,(-((passed+1)/(total+1)-passed/total),passed,total))
 for _ in range(extra_students):
  _,passed,total=heapq.heappop(heap);passed+=1;total+=1;heapq.heappush(heap,(-((passed+1)/(total+1)-passed/total),passed,total))
 return sum(passed/total for _,passed,total in heap)/len(classes)
'''
SCORE='''def maximum_good_subarray_score(nums, k):
 left=right=k;minimum=nums[k];answer=minimum
 while left>0 or right+1<len(nums):
  if left==0:right+=1
  elif right+1==len(nums):left-=1
  elif nums[left-1]>nums[right+1]:left-=1
  else:right+=1
  minimum=min(minimum,nums[left],nums[right]);answer=max(answer,minimum*(right-left+1))
 return answer
'''
QUADRUPLES='''def count_minimum_difference_equal_substrings(first_string, second_string):
 latest={char:index for index,char in enumerate(second_string)};best=float('inf');answer=0
 for index,char in enumerate(first_string):
  if char in latest:
   difference=index-latest[char]
   if difference<best:best=difference;answer=1
   elif difference==best:answer+=1
 return answer
'''
DIGIT='''def second_largest_digit(s):
 largest=second=-1
 for char in s:
  if char.isdigit():
   value=int(char)
   if value>largest:largest,second=value,largest
   elif largest>value>second:second=value
 return second
'''
def H(*a):return list(a)
def E(*a):return entry(*a)
BATCH={
1791:E('find_star_center',[('edges','list[list[int]]')],'int',['graphs'],['The input is a valid undirected star with at least three nodes.','Return the one node incident to every edge.'],[([[[1,2],[2,3],[4,2]]],'Node two occurs in all three edges.'),([[[1,2],[5,1],[1,3],[1,4]]],'Node one is the shared endpoint of every edge.')],[[x] for x in [[[1,3],[2,3]],[[5,2],[2,1],[3,2],[2,4]],[[7,1],[2,7],[7,3],[4,7],[7,5],[6,7]],[[1,4],[2,4],[3,4]],[[9,2],[1,9],[9,3],[4,9],[5,9],[9,6],[7,9],[8,9]],[[2,1],[2,3]],[[3,1],[1,2]],[[10,1],[2,10],[3,10],[10,4],[5,10],[6,10],[10,7],[8,10],[9,10]],[[6,4],[1,6],[6,2],[3,6],[5,6]],[[1,8],[8,2],[3,8],[8,4],[5,8],[8,6],[7,8]],[[4,1],[2,4],[4,3]],[[3,5],[1,3],[3,2],[4,3]]]],CENTER,[CENTER.replace('first[0] in second','first[0] not in second'),CENTER.replace('first[1]','second[0]')],['Selects the non-shared endpoint.','Returns an arbitrary endpoint from the second edge.'],center_o,rcenter,H('The center must occur in each edge.','Only the first two edges are needed because their common endpoint is the center.','Check which endpoint of the first edge appears in the second.','In a valid star, two distinct edges share only the center, so this intersection identifies it uniquely.'),'O(1)','O(1)',3),
1792:E('maximum_average_pass_ratio',[('classes','list[list[int]]'),('extra_students','int')],'float',['arrays','greedy','heaps'],['Each class is [passed,total] with at least one passing student.','Assign every guaranteed-pass extra student to maximize the final average; answers use floating tolerance.'],[([[[1,2],[3,5],[2,2]],2],'Both students go to the first class, producing average (3/4+3/5+1)/3.'),([[[2,4],[3,9],[4,5],[2,10]],4],'Repeatedly choosing the largest marginal ratio increase gives approximately 0.53485.')],[[c,e] for c,e in [([[1,1]],1),([[1,2]],1),([[1,2]],3),([[1,3],[1,3]],2),([[2,2],[1,2]],1),([[1,4],[2,3]],2),([[3,5],[4,8]],3),([[1,10],[9,10]],4),([[2,4],[3,9],[4,5],[2,10]],4),([[5,5],[5,6]],2),([[1,2],[1,2],[1,2]],3),([[2,7],[3,4],[1,5]],2),([[8,10],[1,2]],5),([[1,8],[2,8],[3,8]],4)]],RATIO,[RATIO.replace('heapq.heappop(heap)','heap.pop()'),RATIO.replace('-((passed+1)/(total+1)-passed/total)','-passed/total')],['Does not reliably choose the maximum-gain class from the heap.','Prioritizes current pass ratio instead of marginal improvement.'],ratio_o,rratio,H('Measure how much one extra passing student improves each class ratio.','Always give the next student to the class with the largest current marginal gain.','Store negative gains in a min-heap and recompute a class gain after assignment.','Marginal gains diminish for each class, so the exchange argument makes the largest available gain optimal at every step.'),'O((classes+extra) log classes)','O(classes)',5),
1793:E('maximum_good_subarray_score',[('nums','list[int]'),('k','int')],'int',['arrays','two-pointers','greedy','monotonic-stacks'],['A good contiguous subarray must include index k.','Its score is its minimum value times its length; return the maximum score.'],[([[1,4,3,7,4,5],3],'Subarray indices one through five have minimum three and length five, scoring fifteen.'),([[5,5,4,5,4,1,1,1],0],'The first five values have minimum four and score twenty.')],[[a,k] for a,k in [([1],0),([2,1],0),([2,1],1),([1,2,3],1),([3,2,1],1),([5,5,5],1),([1,4,3,7,4,5],3),([5,5,4,5,4,1,1,1],0),([2,4,6,8],2),([8,6,4,2],2),([3,1,3],1),([1,10,1],1),([6,2,5,4,5,1,6],3),([9,8,7,6,5],4)]],SCORE,[SCORE.replace('nums[left-1]>nums[right+1]','nums[left-1]<nums[right+1]'),SCORE.replace('minimum*(right-left+1)','minimum*(right-left)')],['Expands toward the smaller boundary and lowers the running minimum prematurely.','Omits one element from every subarray length.'],score_o,rscore,H('Grow an interval outward from k while tracking its minimum.','When both sides are available, expand toward the larger adjacent value.','Update the running minimum and score after every expansion until the whole array is covered.','For every possible minimum threshold, choosing the larger boundary delays lowering that minimum and visits the widest qualifying interval, so no optimal score is skipped.'),'O(n)','O(1)',8),
1794:E('count_minimum_difference_equal_substrings',[('first_string','str'),('second_string','str')],'int',['strings','hash-maps','greedy'],['Count equal nonempty substring pairs whose value j-a is globally minimum.','Indices i,j belong to the first string and a,b to the second.'],[(['abcd','bccda'],'The single-character match a at first index zero and second index four uniquely minimizes j-a.'),(['ab','cd'],'The strings share no character, so no equal substring pair exists.')],[[a,b] for a,b in [('a','a'),('a','b'),('ab','ba'),('aa','aa'),('abc','abc'),('zzaz','azzz'),('abcd','bccda'),('ab','cd'),('banana','ananas'),('abcabc','cbacba'),('xxy','yxx'),('aaaa','baaa'),('cab','abc'),('leetcode','codeleet')]],QUADRUPLES,[QUADRUPLES.replace('latest={char:index','latest={char:0'),QUADRUPLES.replace('difference<best','difference>best')],['Stores the first position as zero for every character instead of its latest occurrence.','Maximizes the index difference rather than minimizing it.'],quadruples_o,rquad,H('Any longer equal substring contains a one-character equal pair with no larger j-a.', 'For each character, only its latest position in the second string can minimize the difference.', 'Scan first-string positions, compare index minus the stored latest matching index, and count ties.', 'Reducing every candidate to its ending character preserves or improves j-a; the latest second occurrence is optimal for that character, so the scan counts exactly all global minima.'),'O(n+m)','O(alphabet)',5),
1796:E('second_largest_digit',[('s','str')],'int',['strings','counting'],['The input contains lowercase letters and decimal digits.','Return the second-largest distinct digit, or -1 when fewer than two distinct digits occur.'],[(['dfa12321afd'],'Distinct digits are one, two, and three, so the second largest is two.'),(['abc1111'],'Only digit one occurs, so there is no second-largest distinct digit.')],[[s] for s in ['0','9','19','91','a1b2c3','abc','0001','9876543210','a9z9b8','112233','5a4b5','x0y1z0','123456789','a2b2c1']],DIGIT,[DIGIT.replace('largest>value>second','largest>=value>second'),DIGIT.replace('return second','return largest')],['Treats a duplicate maximum digit as the second distinct value.','Returns the largest digit rather than the second largest.'],digit_o,rdigit,H('Track the largest and second-largest distinct digit seen so far.','Ignore letters; when a new maximum arrives, demote the old maximum to second.', 'Otherwise update second only for a value strictly between it and the maximum.', 'The two variables maintain the top two distinct digits after every character, so the final second value is correct or remains -1.'),'O(n)','O(1)',3),
}
BATCH[1792]['comparator']='float'
BATCH[1792]['sample_correction']={
 'original_expected':0.78333,
 'corrected_expected':47/60,
 'reason':'The workbook rounds the repeating decimal to five places; the exact ratio is 47/60.'}
