"""Opening of batch 101: combinatorics, heaps, simulation, and greedy counts."""
from itertools import combinations
from math import comb
from .import_batch_055 import entry

def vowel_oracle(args):return comb(args[0]+4,4)
def building_oracle(args):
 heights,bricks,ladders=args
 climbs=[]
 for index,(left,right) in enumerate(zip(heights,heights[1:])):
  if right>left:climbs.append(right-left)
  possible=any(sum(climb for i,climb in enumerate(climbs) if i not in chosen)<=bricks for chosen in combinations(range(len(climbs)),min(ladders,len(climbs))))
  if not possible:return index
 return len(heights)-1
def path_oracle(args):
 destination,k=args;vertical,horizontal=destination;paths=[]
 for positions in combinations(range(vertical+horizontal),vertical):
  chosen=set(positions);paths.append(''.join('V' if index in chosen else 'H' for index in range(vertical+horizontal)))
 return sorted(paths)[k-1]
def generated_oracle(args):
 n=args[0]
 if n<2:return n
 values=[0]*(n+1);values[1]=1
 for index in range(1,(n+1)//2+1):
  if 2*index<=n:values[2*index]=values[index]
  if 2*index+1<=n:values[2*index+1]=values[index]+values[index+1]
 return max(values)
def deletion_oracle(args):
 counts=list(__import__('collections').Counter(args[0]).values());best=0
 def search(index,used,kept):
  nonlocal best
  if index==len(counts):best=max(best,kept);return
  for amount in range(counts[index]+1):
   if amount==0 or amount not in used:
    if amount:used.add(amount)
    search(index+1,used,kept+amount)
    if amount:used.remove(amount)
 search(0,set(),0);return len(args[0])-best

def rvowel(r):return [r.randint(1,50)]
def rbuilding(r):return [[r.randint(1,30) for _ in range(r.randint(1,9))],r.randint(0,20),r.randint(0,4)]
def rpath(r):
 v,h=r.randint(1,5),r.randint(1,5);return [[v,h],r.randint(1,comb(v+h,v))]
def rgenerated(r):return [r.randint(0,100)]
def rdeletion(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,12)))]

VOWEL='''def count_sorted_vowel_strings(n):
 counts=[1]*5
 for _ in range(n-1):
  for index in range(3,-1,-1):counts[index]+=counts[index+1]
 return sum(counts)
'''
BUILDING='''def furthest_reachable_building(heights, bricks, ladders):
 climbs=[]
 for index in range(len(heights)-1):
  climb=heights[index+1]-heights[index]
  if climb>0:
   heappush(climbs,climb)
   if len(climbs)>ladders:
    bricks-=heappop(climbs)
    if bricks<0:return index
 return len(heights)-1
'''
PATH='''def kth_smallest_path(destination, k):
 from math import comb
 vertical,horizontal=destination;answer=[]
 while vertical+horizontal:
  horizontal_first=comb(vertical+horizontal-1,vertical) if horizontal else 0
  if horizontal and k<=horizontal_first:answer.append('H');horizontal-=1
  else:answer.append('V');vertical-=1;k-=horizontal_first
 return ''.join(answer)
'''
GENERATED='''def maximum_generated_array_value(n):
 if n<2:return n
 values=[0]*(n+1);values[1]=1
 for index in range(2,n+1):
  values[index]=values[index//2] if index%2==0 else values[index//2]+values[index//2+1]
 return max(values)
'''
DELETIONS='''def minimum_unique_frequency_deletions(s):
 counts=sorted(Counter(s).values(),reverse=True);used=set();answer=0
 for count in counts:
  while count>0 and count in used:count-=1;answer+=1
  if count:used.add(count)
 return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]
def E(*args):return entry(*args)
BATCH={
1641:E('count_sorted_vowel_strings',[('n','int')],'int',['combinatorics','dynamic-programming'],['1 <= n <= 50.','Count length-n strings over a,e,i,o,u whose characters never decrease alphabetically.'],[([1],'Each individual vowel is valid, giving five strings.'),([2],'The fifteen nondecreasing vowel pairs are counted.')],[[n] for n in [1,2,3,4,5,6,7,8,10,15,20,30,40,50]],VOWEL,[VOWEL.replace('range(n-1)','range(n)'),VOWEL.replace('return sum(counts)','return sum(counts)-1')],['Performs one extra length-extension step.','Drops one valid string from every result.'],vowel_oracle,rvowel,lesson('A state can record the smallest vowel still allowed.','Accumulate suffix counts once for each additional character position.','Start with one string per final vowel, repeatedly add counts from larger vowels, then sum all starts.','Every sorted string has a unique first vowel followed by a sorted suffix using that vowel or a larger one.'),'O(n)','O(1)',5),
1642:E('furthest_reachable_building',[('heights','list[int]'),('bricks','int'),('ladders','int')],'int',['greedy','heaps'],['1–100,000 buildings; bricks and ladders are nonnegative.','Descending moves are free. Spend ladders on the largest positive climbs encountered and bricks on the others.'],[([[4,2,7,6,9,14,12],5,1],'Using bricks for climbs five and three leaves no resources for the next climb five, so index four is furthest.'),([[4,12,2,7,3,18,20,3,19],10,2],'Optimal resource assignment reaches index seven.')],[[*x] for x in [([4,2,7,6,9,14,12],5,1),([4,12,2,7,3,18,20,3,19],10,2),([1],0,0),([1,2],1,0),([1,2],0,1),([5,4,3],0,0),([1,5,10],4,1),([1,5,10],3,1),([1,2,3,4],2,1),([10,1,20],9,0),([1,100,101],1,1),([3,3,3],0,0),([1,6,2,8],5,1),([1,4,8,12],7,1)]],BUILDING,[BUILDING.replace('heappop(climbs)','max(climbs)'),BUILDING.replace('if bricks<0','if bricks<=0')],['Spends bricks on the largest climb instead of the smallest ladder candidate.','Stops when bricks reach exactly zero even though that climb is affordable.'],building_oracle,rbuilding,lesson('Among climbs seen so far, ladders should cover the largest ones.','Put every positive climb in a min-heap; when there are too many for the ladders, pay bricks for the smallest.','Process edges in order and stop before the first payment that makes bricks negative.','Exchanging a ladder from a smaller climb to a larger one never uses more bricks, proving the heap allocation is optimal.'),'O(n log ladders)','O(ladders)',5),
1643:E('kth_smallest_path',[('destination','list[int]'),('k','int')],'str',['combinatorics','greedy'],['Destination gives 1–15 vertical and horizontal moves; k is within the number of paths.','H is lexicographically before V. Return the one-indexed kth path string.'],[([[2,3],1],'The first path places all three H moves before both V moves: HHHVV.'),([[2,3],3],'Skipping the first two H-leading combinations at the deciding prefix produces HHVVH.')],[[*x] for x in [([2,3],1),([2,3],3),([1,1],1),([1,1],2),([1,2],1),([1,2],3),([2,1],2),([3,3],10),([3,2],5),([4,1],3),([1,4],4),([4,4],1),([4,4],70),([5,3],20)]],PATH,[PATH.replace('k<=horizontal_first','k<horizontal_first'),PATH.replace("answer.append('H')","answer.append('V')",1)],['Uses a zero-indexed boundary when deciding whether the kth path begins with H.','Emits V while consuming a horizontal move.'],path_oracle,rpath,lesson('At any prefix, count paths beginning with H before choosing the next character.','The H block contains C(remaining-1,vertical) paths.','If k is inside that block, append H; otherwise append V and subtract the whole H block.','All H-prefixed paths precede every V-prefixed path, so repeated block selection identifies the kth string.'),'O(rows+columns)','O(rows+columns)',8),
1646:E('maximum_generated_array_value',[('n','int')],'int',['arrays','simulation'],['0 <= n <= 100.','Construct indices 0 through n by the stated even and odd recurrences and return their maximum.'],[([7],'The generated values 0,1,1,2,1,3,2,3 have maximum three.'),([0],'Only nums[0]=0 exists, so the maximum is zero.')],[[n] for n in [0,1,2,3,4,5,6,7,8,9,10,15,20,31]],GENERATED,[GENERATED.replace('index//2+1','index//2-1'),GENERATED.replace('if n<2:return n','if n<2:return 1')],['Uses the previous rather than next parent value for odd indices.','Returns one for the n=0 base case.'],generated_oracle,rgenerated,lesson('Each new value depends only on already generated smaller indices.','Allocate n+1 values and fill them in increasing index order.','Copy nums[i//2] at even i; add nums[i//2] and nums[i//2+1] at odd i; track the maximum.','Both parent indices are smaller than i, so forward construction satisfies every recurrence exactly once.'),'O(n)','O(n)',3),
1647:E('minimum_unique_frequency_deletions',[('s','str')],'int',['strings','greedy'],['1–100,000 lowercase letters.','Delete the fewest characters so all remaining positive character frequencies are distinct; characters may be deleted entirely.'],[(['aab'],'Frequencies two and one are already distinct, so no deletion is needed.'),(['aaabbbcc'],'Reduce one frequency three to two and the original frequency two to one, using two deletions.')],[[s] for s in ['aab','aaabbbcc','ceabaacb','a','ab','aa','aabb','aaaabbbb','abcabc','aaaaabbbbcc','zzzyyyxxw','abcdefghijkl','aabbccdde','aaaaabbbbcccdde']],DELETIONS,[DELETIONS.replace('while count>0 and count in used','if count>0 and count in used'),DELETIONS.replace('while count>0 and count in used','while count>1 and count in used')],['Deletes at most once from a colliding frequency even when the reduced value still collides.','Refuses to delete a colliding frequency of one down to zero.'],deletion_oracle,rdeletion,lesson('For each frequency, the best available replacement is the largest unused value no greater than it.','Process counts high to low and decrement collisions until reaching an unused positive count or zero.','Record positive kept counts and accumulate every decrement.','Choosing a smaller available count would only add deletions and cannot create more room for later, no-larger frequencies.'),'O(n+alphabet²)','O(alphabet)',5),
}
