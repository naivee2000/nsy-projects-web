"""Second half of batch 92: strings, counting, geometry, and greedy tasks."""
from collections import Counter
from itertools import combinations, permutations
from .import_batch_055 import entry

def prefix_o(a):
 s=a[0];return max((s[:n] for n in range(1,len(s)) if s[:n]==s[-n:]),key=len,default='')
def lucky_o(a):
 c=Counter(a[0]);return max((x for x,n in c.items() if x==n),default=-1)
def teams_o(a):
 r=a[0];return sum((r[i]<r[j]<r[k]) or (r[i]>r[j]>r[k]) for i in range(len(r)) for j in range(i+1,len(r)) for k in range(j+1,len(r)))
def groups_o(a):
 c=Counter(sum(map(int,str(x))) for x in range(1,a[0]+1));m=max(c.values());return sum(n==m for n in c.values())
def pal_o(a):
 s,k=a;return sum(n%2 for n in Counter(s).values())<=k<=len(s)
def overlap_o(a):
 r,x,y,x1,y1,x2,y2=a;dx=0 if x1<=x<=x2 else min(abs(x-x1),abs(x-x2));dy=0 if y1<=y<=y2 else min(abs(y-y1),abs(y-y2));return dx*dx+dy*dy<=r*r
def dishes_o(a):
 v=a[0];best=0
 for n in range(1,len(v)+1):
  for chosen in combinations(v,n):
   for order in permutations(chosen):best=max(best,sum((i+1)*x for i,x in enumerate(order)))
 return best
def subseq_o(a):
 nums=a[0];total=sum(nums)
 for n in range(1,len(nums)+1):
  valid=[[nums[i] for i in indexes] for indexes in combinations(range(len(nums)),n) if sum(nums[i] for i in indexes)*2>total]
  if valid:return sorted(max(valid,key=sum),reverse=True)
 return []
def binary_o(a):
 n=int(a[0],2);steps=0
 while n!=1:n=n//2 if n%2==0 else n+1;steps+=1
 return steps
def matching_o(a):
 w=a[0];return [x for i,x in enumerate(w) if any(i!=j and x in y for j,y in enumerate(w))]

def rp(r):return [''.join(r.choice('abcd') for _ in range(r.randint(1,30)))]
def rl(r):return [[r.randint(1,12) for _ in range(r.randint(1,30))]]
def rt(r):
 n=r.randint(3,10);return [r.sample(range(1,100),n)]
def rg(r):return [r.randint(1,500)]
def rpal(r):
 s=''.join(r.choice('abcde') for _ in range(r.randint(1,25)));return [s,r.randint(1,len(s)+2)]
def ro(r):
 x1,x2=sorted(r.sample(range(-12,13),2));y1,y2=sorted(r.sample(range(-12,13),2));return [r.randint(1,10),r.randint(-15,15),r.randint(-15,15),x1,y1,x2,y2]
def rd(r):return [[r.randint(-10,10) for _ in range(r.randint(1,6))]]
def rs(r):return [[r.randint(1,20) for _ in range(r.randint(1,9))]]
def rb(r):return ['1'+''.join(r.choice('01') for _ in range(r.randint(0,30)))]
def rm(r):
 target=r.randint(2,9);words=set()
 while len(words)<target:words.add(''.join(r.choice('abcd') for _ in range(r.randint(1,8))))
 return [list(words)]

PREFIX='''def longest_happy_prefix(s):
 failure=[0]*len(s)
 for i in range(1,len(s)):
  length=failure[i-1]
  while length and s[i]!=s[length]:length=failure[length-1]
  if s[i]==s[length]:length+=1
  failure[i]=length
 return s[:failure[-1]]
'''
LUCKY='''def largest_lucky_integer(arr):
 from collections import Counter
 counts=Counter(arr)
 return max((value for value,count in counts.items() if value==count),default=-1)
'''
TEAMS='''def count_monotonic_teams(rating):
 answer=0
 for j,middle in enumerate(rating):
  lower_left=sum(value<middle for value in rating[:j]);higher_left=j-lower_left
  lower_right=sum(value<middle for value in rating[j+1:]);higher_right=len(rating)-j-1-lower_right
  answer+=lower_left*higher_right+higher_left*lower_right
 return answer
'''
GROUPS='''def count_largest_digit_sum_groups(n):
 counts={}
 for value in range(1,n+1):
  key=sum(int(digit) for digit in str(value));counts[key]=counts.get(key,0)+1
 largest=max(counts.values())
 return sum(size==largest for size in counts.values())
'''
PAL='''def can_construct_k_palindromes(s, k):
 from collections import Counter
 odd=sum(count%2 for count in Counter(s).values())
 return odd<=k<=len(s)
'''
OVERLAP='''def circle_overlaps_rectangle(radius, x_center, y_center, x1, y1, x2, y2):
 closest_x=max(x1,min(x_center,x2));closest_y=max(y1,min(y_center,y2))
 return (x_center-closest_x)**2+(y_center-closest_y)**2<=radius**2
'''
DISHES='''def maximum_like_time(satisfaction):
 running=answer=0
 for value in sorted(satisfaction,reverse=True):
  if running+value<=0:break
  running+=value;answer+=running
 return answer
'''
SUBSEQ='''def minimum_dominating_subsequence(nums):
 remaining=sum(nums);chosen=[];selected=0
 for value in sorted(nums,reverse=True):
  chosen.append(value);selected+=value;remaining-=value
  if selected>remaining:return chosen
 return chosen
'''
BINARY='''def binary_steps_to_one(s):
 steps=carry=0
 for i in range(len(s)-1,0,-1):
  bit=int(s[i])+carry
  if bit==1:steps+=2;carry=1
  else:steps+=1
 return steps+carry
'''
MATCH='''def substring_words(words):
 return [word for i,word in enumerate(words) if any(i!=j and word in other for j,other in enumerate(words))]
'''

E=entry
def S(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time='O(n)',space='O(n)',d=5):return E(name,p,r,t,c,e,h,ref,w,why,o,g,hints,time,space,d)
BATCH={
1392:S('longest_happy_prefix',[('s','str')],'str',['strings','kmp'],['A happy prefix is non-empty, proper, and also a suffix.','Return the longest one, or the empty string when none exists.'],[(['level'],'The prefix and suffix l match; no longer proper prefix does.'),(['ababab'],'The longest matching proper prefix and suffix is abab.')],[[s] for s in ['a','aa','ab','aba','abab','aaaa','abcab','leetcodeleet','ababab','abcdabc','abcabcabc','aabaaab','xyzxyz','mississippi']],PREFIX,[PREFIX.replace('return s[:failure[-1]]','return s[:failure[-1]-1]'),'''def longest_happy_prefix(s):
 for size in range(1,len(s)):
  if s[:size]==s[-size:]:return s[:size]
 return ''
'''],['Drops one character from every discovered prefix.','Returns the first matching prefix instead of the longest.'],prefix_o,rp,['Build the KMP failure array over the entire string.','On mismatch, follow failure links to the next possible border.','The final failure value is the longest proper prefix also ending at the final character.','Failure links test every viable border in linear time.'],'O(n)','O(n)',8),
1394:S('largest_lucky_integer',[('arr','list[int]')],'int',['arrays','counting'],['An integer is lucky when its value equals its frequency in arr.','Return the largest lucky integer, or -1 when none exists.'],[([[2,2,3,4]],'Two occurs exactly twice and is the largest lucky value.'),([[1,2,2,3,3,3]],'One, two, and three are lucky; three is largest.')],[[x] for x in [[1],[2],[1,1],[2,2],[2,2,2],[1,2,2,3,3,3],[5,5,5,5,5],[4,4,4,4,3,3,3],[7,7],[1,1,2,2],[3,3,3,2,2,1],[10]*10,[6]*5,[2,2,3,4]]],LUCKY,[LUCKY.replace('max((value','min((value'),LUCKY.replace('value==count','value<=count')],['Returns the smallest lucky value.','Accepts values occurring more often than their value.'],lucky_o,rl,['Count each distinct value.','Keep values whose count equals the value itself.','Return their maximum, using -1 as the empty default.','The equality is precisely the lucky definition.'],'O(n)','O(n)',3),
1395:S('count_monotonic_teams',[('rating','list[int]')],'int',['arrays','counting'],['Choose indices i<j<k with strictly increasing or strictly decreasing ratings.','All ratings are distinct.'],[([[2,5,3,4,1]],'The three valid teams are (2,3,4), (5,3,1), and (5,4,1).'),([[1,2,3,4]],'Every choice of three indices is increasing, giving four teams.')],[[x] for x in [[1,2,3],[3,2,1],[1,3,2],[1,2,3,4],[4,3,2,1],[2,5,3,4,1],[1,3,2,4],[4,1,3,2],[5,1,4,2,3],[2,1,4,3,6,5],[10,20,30,5],[9,7,5,3,1],[1,5,2,4,3],[6,1,5,2,4,3]]],TEAMS,[TEAMS.replace('+higher_left*lower_right',''),TEAMS.replace('answer+=lower_left*higher_right+higher_left*lower_right','answer+=lower_left*lower_right+higher_left*higher_right')],['Counts only increasing teams.','Combines same-side directions rather than opposite sides.'],teams_o,rt,['Treat each rating as the middle member.','Count lower and higher values on both sides.','Multiply lower-left by higher-right, and higher-left by lower-right.','Every valid triple has exactly one middle index, so each is counted once.'],'O(n²)','O(1)',5),
1399:S('count_largest_digit_sum_groups',[('n','int')],'int',['counting','math'],['Group every integer from 1 through n by the sum of its decimal digits.','Return how many groups share the largest size.'],[([13],'Digit-sum groups one through four each have size two, so four groups tie.'),([2],'The sums one and two each occur once, producing two largest groups.')],[[n] for n in [1,2,5,9,10,11,13,19,20,50,99,100,321,500]],GROUPS,[GROUPS.replace('range(1,n+1)','range(n)'),GROUPS.replace('size==largest','size>=largest-1')],['Includes zero and omits n.','Also counts groups one below the maximum size.'],groups_o,rg,['Compute every decimal digit sum from 1 through n.','Count the size of each digit-sum bucket.','Find the maximum bucket size and count buckets equal to it.','This directly realizes the grouping and tie count.'],'O(n log n)','O(log n)',3),
1400:S('can_construct_k_palindromes',[('s','str'),('k','int')],'bool',['strings','counting'],['Use every character exactly once across exactly k non-empty palindrome strings.','Characters may be rearranged freely.'],[(['annabelle',2],'Two odd counts can supply the required palindrome centers.'),(['leetcode',3],'Five odd counts require at least five centers, so three is impossible.')],[[s,k] for s,k in [('a',1),('a',2),('aa',1),('aa',2),('abc',1),('abc',3),('annabelle',2),('leetcode',3),('true',4),('yzyzyzyzyzyzyzy',2),('aaaaabbbb',1),('aaaaabbbb',3),('abcabc',2),('abcdef',6)]],PAL,[PAL.replace('odd<=k','odd==k'),PAL.replace('k<=len(s)','k<len(s)')],['Requires exactly k odd counts although pairs can create extra palindromes.','Rejects one-character-per-palindrome constructions.'],pal_o,rpal,['Each odd-frequency character needs a palindrome center.','The odd-count total therefore cannot exceed k.','Also k cannot exceed the number of characters because palindromes are non-empty.','When both bounds hold, pairs can be split to reach exactly k.'],'O(n)','O(alphabet)',5),
1401:S('circle_overlaps_rectangle',[('radius','int'),('x_center','int'),('y_center','int'),('x1','int'),('y1','int'),('x2','int'),('y2','int')],'bool',['geometry','math'],['The rectangle is axis-aligned with the two given opposite corners.','Touching at an edge or corner counts as overlap.'],[([1,0,0,1,-1,3,1],'The circle touches the rectangle along x=1, so they overlap.'),([1,0,0,2,2,4,4],'The nearest corner is farther than the radius.')],[[*x] for x in [(1,0,0,1,-1,3,1),(1,0,0,2,2,4,4),(2,0,0,-1,-1,1,1),(1,2,2,0,0,4,4),(2,0,0,2,0,5,3),(3,0,0,2,2,5,5),(2,-2,0,0,-1,3,1),(5,10,10,0,0,5,5),(1,0,3,-2,0,2,2),(4,0,0,-5,-1,-4,1),(2,1,1,3,3,5,5),(10,0,0,6,8,9,12),(3,-5,-5,-2,-2,1,1),(1,5,0,0,-1,4,1)]],OVERLAP,[OVERLAP.replace('<=radius**2','<radius**2'),'''def circle_overlaps_rectangle(radius,x_center,y_center,x1,y1,x2,y2):
 return x1<=x_center<=x2 and y1<=y_center<=y2
'''],['Treats boundary contact as non-overlap.','Checks only whether the center lies inside the rectangle.'],overlap_o,ro,['Clamp the center to each rectangle coordinate range.','The clamped coordinates form the closest rectangle point.','Compare squared distance with squared radius, including equality.','Intersection exists exactly when this minimum distance is within the radius.'],'O(1)','O(1)',5),
1402:S('maximum_like_time',[('satisfaction','list[int]')],'int',['greedy','sorting'],['Choose and arrange any dishes; a dish at one-based time t contributes t*satisfaction.','Return the maximum total, allowing zero by cooking no dishes.'],[([[-1,-8,0,5,-9]],'Cooking -1, 0, and 5 in order yields the maximum 14.'),([[4,3,2]],'All positive dishes are used in ascending order for total 20.')],[[x] for x in [[-1],[-1,-2],[0],[1],[1,2],[-1,0,1],[-1,-8,0,5,-9],[4,3,2],[-2,5,-1,0,3],[-10,10],[-3,-2,5,6],[-5,1,2,3],[2,-2,2,-2],[5,4,-20,3]]],DISHES,[DISHES.replace('sorted(satisfaction,reverse=True)','sorted(satisfaction)'),DISHES.replace('if running+value<=0:break','if value<=0:break')],['Considers dishes from least satisfying to greatest.','Rejects negative dishes that profitably increase later multipliers.'],dishes_o,rd,['An optimal chosen order is ascending satisfaction.','Build that order backward from the largest value.','Prepending changes the total by the sum of all included values plus the new value.','Continue exactly while this gain is positive; smaller later candidates cannot recover after it fails.'],'O(n log n)','O(n)',8),
1403:S('minimum_dominating_subsequence',[('nums','list[int]')],'list[int]',['greedy','sorting'],['Return non-increasing values whose sum is strictly greater than the remaining sum.','Use the fewest elements; among ties maximize their sum.'],[([[4,3,10,9,8]],'Ten and nine are the fewest values whose sum exceeds the remainder.'),([[4,4,7,6,7]],'Selecting 7, 7, and 6 gives minimum length and maximum sum.')],[[x] for x in [[1],[1,1],[2,1],[1,2,3],[4,3,10,9,8],[4,4,7,6,7],[5,5,5],[10,1,1,1],[2,2,3,3],[1,2,2,2,6],[9,8,1,1,1],[3,1,4,1,5],[20,1,2,3,4],[6,6,6,5,5]]],SUBSEQ,[SUBSEQ.replace('reverse=True','reverse=False'),SUBSEQ.replace('selected>remaining','selected>=remaining')],['Selects smallest values first.','Accepts equal sums despite the strict requirement.'],subseq_o,rs,['Take values from largest downward to minimize count and maximize sum.','Move each chosen value from the remaining sum to selected sum.','Stop at the first strict selected-greater-than-remaining point.','No equally short selection can exceed the sum of the largest values.'],'O(n log n)','O(n)',3),
1404:S('binary_steps_to_one',[('s','str')],'int',['strings','bit-manipulation'],['s is a positive binary integer with no leading zeroes.','When even divide by two; when odd add one, repeating until one.'],[(['1101'],'Thirteen follows 13, 14, 7, 8, 4, 2, 1 for six operations.'),(['10'],'Two divides once to reach one.')],[[s] for s in ['1','10','11','100','101','110','111','1000','1001','1010','1101','1111','10000','101101']],BINARY,[BINARY.replace('steps+=2;carry=1','steps+=1;carry=1'),BINARY.replace('return steps+carry','return steps')],['Counts an odd add-and-divide pair as one operation.','Omits the final carry created through the leading bit.'],binary_o,rb,['Process bits right-to-left without materializing the integer.','An effective zero needs one division; an effective one needs add-one then division.','Carry remains set after adding through a one bit.','A remaining carry after non-leading bits accounts for the last operation.'],'O(n)','O(1)',5),
1408:S('substring_words',[('words','list[str]')],'list[str]',['strings','search'],['Return words occurring as a substring of another word in the same array.','Words are distinct; preserve input order.'],[([['mass','as','hero','superhero']],'as occurs in mass and hero occurs in superhero.'),([['leetcode','et','code']],'Both et and code occur inside leetcode.')],[[x] for x in [['a','b'],['a','aa'],['ab','abc','bc'],['mass','as','hero','superhero'],['leetcode','et','code'],['blue','green','bu'],['cat','cater','at'],['x','xy','xyz'],['abcd','bc','cd','d'],['same','name','me'],['foo','bar','foobar'],['one','tone','stone'],['hi','there'],['aaa','aa','a']]],MATCH,[MATCH.replace('word in other','other in word'),MATCH.replace('i!=j and ','')],['Reverses the substring relationship.','Allows each word to match itself.'],matching_o,rm,['Compare each word with every other word.','It qualifies if contained in at least one different element.','Keep the outer scan in original order.','The existential pair test exactly matches the required relation.'],'O(n²L)','O(n)',3),
}
