"""Concatenation, robot collisions, alternating parity, prime pairs, and bounded windows batch 180."""
from collections import deque
from .import_batch_055 import entry

def concat_oracle(a):
 states={a[0][0]}
 for word in a[0][1:]:
  following=set()
  for text in states:
   following.add(text+word[1:] if text[-1]==word[0] else text+word)
   following.add(word[:-1]+text if word[-1]==text[0] else word+text)
  states=following
 return min(map(len,states))
def random_concat(r):return [[''.join(r.choice('abc') for _ in range(r.randint(1,4))) for _ in range(r.randint(1,8))]]
def collisions_oracle(a):
 positions,healths,directions=a;alive=sorted([[p,h,d,i] for i,(p,h,d) in enumerate(zip(positions,healths,directions))])
 while True:
  hit=next((i for i in range(len(alive)-1) if alive[i][2]=='R' and alive[i+1][2]=='L'),None)
  if hit is None:break
  left,right=alive[hit],alive[hit+1]
  if left[1]==right[1]:alive[hit:hit+2]=[]
  elif left[1]>right[1]:left[1]-=1;alive.pop(hit+1)
  else:right[1]-=1;alive.pop(hit)
 return [h for _,h,_,i in sorted(alive,key=lambda item:item[3])]
def random_collisions(r):
 n=r.randint(1,10);return [r.sample(range(1,40),n),[r.randint(1,15) for _ in range(n)],''.join(r.choice('LR') for _ in range(n))]
def alternating_oracle(a):
 nums,threshold=a;return max((j-i for i in range(len(nums)) for j in range(i+1,len(nums)+1) if nums[i]%2==0 and max(nums[i:j])<=threshold and all(nums[k]%2!=nums[k-1]%2 for k in range(i+1,j))),default=0)
def random_alternating(r):return [[r.randint(1,20) for _ in range(r.randint(1,30))],r.randint(1,20)]
def prime_oracle(a):
 n=a[0]
 def prime(x):return x>=2 and all(x%d for d in range(2,int(x**.5)+1))
 return [[x,n-x] for x in range(2,n//2+1) if prime(x) and prime(n-x)]
def random_prime(r):return [r.randint(2,500)]
def continuous_oracle(a):
 nums=a[0];return sum(max(nums[i:j])-min(nums[i:j])<=2 for i in range(len(nums)) for j in range(i+1,len(nums)+1))
def random_continuous(r):return [[r.randint(-20,20) for _ in range(r.randint(1,40))]]

CONCAT='''\
def minimum_decremental_concatenation(words):
    states={(words[0][0],words[0][-1]):len(words[0])}
    for word in words[1:]:
        following={}
        for (first,last),length in states.items():
            right=(first,word[-1]);following[right]=min(following.get(right,10**9),length+len(word)-(last==word[0]))
            left=(word[0],last);following[left]=min(following.get(left,10**9),length+len(word)-(word[-1]==first))
        states=following
    return min(states.values())
'''
COLLISIONS='''\
def surviving_robot_healths(positions,healths,directions):
    order=sorted(range(len(positions)),key=positions.__getitem__);stack=[];alive=[True]*len(positions)
    for index in order:
        if directions[index]=='R':stack.append(index);continue
        while stack and alive[index]:
            other=stack[-1]
            if healths[other]==healths[index]:alive[other]=alive[index]=False;stack.pop()
            elif healths[other]>healths[index]:healths[other]-=1;alive[index]=False
            else:healths[index]-=1;alive[other]=False;stack.pop()
    return [healths[i] for i in range(len(positions)) if alive[i]]
'''
ALTERNATING='''\
def longest_even_odd_threshold_subarray(nums,threshold):
    answer=length=0
    for index,value in enumerate(nums):
        if value>threshold:length=0
        elif length and nums[index-1]%2!=value%2:length+=1
        elif value%2==0:length=1
        else:length=0
        answer=max(answer,length)
    return answer
'''
PRIMES='''\
def prime_pairs_with_sum(n):
    prime=[True]*(n+1);prime[:2]=[False,False]
    for value in range(2,int(n**0.5)+1):
        if prime[value]:prime[value*value:n+1:value]=[False]*(((n-value*value)//value)+1)
    return [[value,n-value] for value in range(2,n//2+1) if prime[value] and prime[n-value]]
'''
CONTINUOUS='''\
def count_continuous_subarrays(nums):
    minimum=deque();maximum=deque();left=0;answer=0
    for right,value in enumerate(nums):
        while minimum and nums[minimum[-1]]>=value:minimum.pop()
        while maximum and nums[maximum[-1]]<=value:maximum.pop()
        minimum.append(right);maximum.append(right)
        while nums[maximum[0]]-nums[minimum[0]]>2:
            if minimum[0]==left:minimum.popleft()
            if maximum[0]==left:maximum.popleft()
            left+=1
        answer+=right-left+1
    return answer
'''
BATCH={
2746:entry('minimum_decremental_concatenation',[('words','list[str]')],'int',['strings','dynamic programming'],['Process words in order, placing each new word at either end of the current string.','When touching endpoint characters match, overlap that one character.','Return the minimum possible final length.'],[([['aa','ab','bc']],'Append ab with one overlap, then append bc with one overlap, producing aabc of length four.'),([['ab','b']],'Appending b overlaps the existing final b, so length remains two.')],[[w] for w in [['a'],['a','a'],['ab','b'],['aa','ab','bc'],['ab','cd'],['ab','ba'],['abc','ca','ab'],['a','b','c'],['aa','aa','aa'],['ab','bc','ca'],['abc','cba'],['az','za','aa'],['ba','ac','cb','bb'],['abc','b','ca','a']]],CONCAT,[CONCAT.replace('(last==word[0])','False'),CONCAT.replace('(word[-1]==first)','False').replace('(last==word[0])','False')],['Never overlaps when appending on the right.','Concatenates full words and misses overlaps at both endpoints.'],concat_oracle,random_concat,['Only the current first and last characters affect future overlap choices.','Map each endpoint pair to its minimum achievable length.','For every word, transition by prepending and appending with a one-character discount when endpoints match.','States with identical endpoints have identical futures, so retaining only their shortest length loses no optimum.'],'O(n*alphabet²)','O(alphabet²)',8),
2751:entry('surviving_robot_healths',[('positions','list[int]'),('healths','list[int]'),('directions','str')],'list[int]',['arrays','sorting','stacks','simulation'],['Robots move at equal speed left or right; only opposing robots collide.','The lower-health robot disappears and the survivor loses one health; equal-health robots both disappear.','Return surviving healths in original input order.'],[([ [5,4,3,2,1],[2,17,9,15,10],'RRRRR'],'No robots move toward one another, so every health remains in input order.'),([[3,5,2,6],[10,10,15,12],'RLRL'],'The opposing pairs resolve according to health until only surviving robots remain.')],[[p,h,d] for p,h,d in [([1],[5],'R'),([1,2],[3,3],'RL'),([1,2],[4,3],'RL'),([1,2],[3,4],'RL'),([5,4,3,2,1],[2,17,9,15,10],'RRRRR'),([1,2,3],[5,3,2],'RRL'),([1,2,3],[2,3,5],'RLL'),([3,5,2,6],[10,10,15,12],'RLRL'),([10,1],[2,2],'LR'),([1,3,5,7],[5,4,3,2],'RRLL'),([1,4,8],[1,2,3],'LRL'),([9,2,6],[4,7,5],'LRR'),([2,5,8,11],[3,3,3,3],'RLRL'),([20,10,30],[8,2,5],'LRL')]],COLLISIONS,[COLLISIONS.replace('healths[other]-=1','healths[index]-=1',1),COLLISIONS.replace('alive[other]=alive[index]=False','alive[index]=False')],['Decreases the destroyed left-moving robot instead of the surviving right-moving robot.','Lets the right-moving robot survive an equal-health collision.'],collisions_oracle,random_collisions,['Sort robots by position and stack unmatched right movers.','A left mover can collide only with the nearest surviving right mover on its left.','Resolve and pop until the left mover dies or no opponent remains.','The stack preserves spatial collision order; each resolution exactly applies the health rule, and final filtering restores input order.'],'O(n log n)','O(n)',8),
2760:entry('longest_even_odd_threshold_subarray',[('nums','list[int]'),('threshold','int')],'int',['arrays','sliding window'],['Choose a contiguous subarray beginning with an even number.','Every value must be at most threshold and adjacent parities must alternate.','Return the maximum length.'],[([[3,2,5,4],5],'The subarray 2,5,4 begins even, alternates, and has length three.'),([[1,2],1],'The only even value exceeds the threshold, so the answer is zero.')],[[a,t] for a,t in [([2],2),([1],5),([3,2,5,4],5),([1,2],1),([2,3,4,5],10),([2,2,3],5),([4,3,2,1],3),([8,1,6,3],7),([1,4,3,2],4),([6,5,4,3,2],6),([2,9,4],8),([10,1,2],10),([3,5,7],9),([0,1,0,1],1)]],ALTERNATING,[ALTERNATING.replace('value>threshold','value>=threshold'),ALTERNATING.replace('value%2==0','value%2==1')],['Rejects values equal to the threshold.','Starts candidate subarrays at odd values.'],alternating_oracle,random_alternating,['Track the valid alternating suffix ending at each index.','Reset above threshold; extend on parity change; otherwise restart at one only for an even value.','Keep the maximum suffix length.','Every valid subarray ending at an index is a suffix, and the recurrence retains the longest such suffix with the required even start.'],'O(n)','O(1)',3),
2761:entry('prime_pairs_with_sum',[('n','int')],'list[list[int]]',['math','sieve'],['Find prime numbers x and y with x+y=n and x<=y.','List each unordered pair once in increasing x order.','Return an empty list when no pair exists.'],[([10],'The prime decompositions are 3+7 and 5+5.'),([3],'Only 1+2 is possible, but one is not prime, so no pair exists.')],[[n] for n in [2,3,4,5,6,7,8,9,10,12,20,27,50,100]],PRIMES,[PRIMES.replace('range(2,n//2+1)','range(2,n//2)'),PRIMES.replace('if prime[value]:','if False:')],['Omits the equal pair n/2+n/2.','Never crosses out composite numbers in the sieve.'],prime_oracle,random_prime,['Build a primality sieve through n.','Check x only through n/2 so each unordered pair appears once.','Emit [x,n-x] when both entries are prime.','The bounded scan covers exactly one orientation of every possible sum pair, while the sieve gives correct primality.'],'O(n log log n)','O(n)',5),
2762:entry('count_continuous_subarrays',[('nums','list[int]')],'int',['arrays','sliding window','monotonic queues'],['A subarray is continuous when its maximum and minimum differ by at most two.','Count all nonempty contiguous continuous subarrays.','Return the total count.'],[([[5,4,2,4]],'The valid subarrays total eight; windows containing both five and two are invalid.'),([[1,1,1]],'All six nonempty subarrays have range zero.')],[[a] for a in [[1],[1,1],[1,4],[5,4,2,4],[1,1,1],[1,2,3],[1,2,4],[3,1,2],[10,8,9,7],[0,-1,-2],[-3,0,-1],[5,3,5,3],[1,4,2,3],[9,6,7,8,5]]],CONTINUOUS,[CONTINUOUS.replace('>2','>=2'),CONTINUOUS.replace('right-left+1','right-left')],['Requires range strictly below two rather than at most two.','Omits the one-character substring beginning at left for every endpoint.'],continuous_oracle,random_continuous,['Maintain increasing and decreasing deques of indices for the window minimum and maximum.','Shrink from the left while their difference exceeds two.','Add right-left+1 valid suffixes for each right endpoint.','After shrinking, every suffix beginning at or after left is valid and every earlier start contains the same invalid extremes.'],'O(n)','O(n)',5),
}
