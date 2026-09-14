"""Partition gaps, divisible permutations, wall painting, unique substrings, and reverse pairs batch 178."""
from itertools import permutations,combinations
from .import_batch_055 import entry

def partition_oracle(a):
 nums=a[0];n=len(nums);answer=10**18
 for mask in range(1,(1<<n)-1):
  left=[nums[i] for i in range(n) if mask>>i&1];right=[nums[i] for i in range(n) if not mask>>i&1]
  answer=min(answer,abs(max(left)-min(right)))
 return answer
def random_partition(r):return [[r.randint(-50,50) for _ in range(r.randint(2,10))]]
def special_oracle(a):
 return sum(all(x%y==0 or y%x==0 for x,y in zip(p,p[1:])) for p in permutations(a[0]))%1_000_000_007
def random_special(r):return [r.sample(range(1,31),r.randint(1,8))]
def paint_oracle(a):
 cost,time=a;n=len(cost);return min(sum(cost[i] for i in range(n) if mask>>i&1) for mask in range(1<<n) if sum(1+time[i] for i in range(n) if mask>>i&1)>=n)
def random_paint(r):
 n=r.randint(1,10);return [[r.randint(1,30) for _ in range(n)],[r.randint(0,6) for _ in range(n)]]
def unique_oracle(a):
 s=a[0];return sum(len(set(s[i:j]))==j-i for i in range(len(s)) for j in range(i+1,len(s)+1))
def random_unique(r):return [''.join(r.choice('abcde') for _ in range(r.randint(1,35)))]
def pairs_oracle(a):
 words=a[0];used=set();answer=0
 for i in range(len(words)):
  if i in used:continue
  for j in range(i+1,len(words)):
   if j not in used and words[i]==words[j][::-1]:used|={i,j};answer+=1;break
 return answer
def random_pairs(r):return [[''.join(r.choice('abcd') for _ in range(2)) for _ in range(r.randint(1,30))]]

PART='''\
def minimum_partition_value(nums):
    nums=sorted(nums)
    return min(right-left for left,right in zip(nums,nums[1:]))
'''
SPECIAL='''\
def count_special_permutations(nums):
    MOD=1_000_000_007;n=len(nums);dp={(1<<i,i):1 for i in range(n)}
    for mask in range(1,1<<n):
        for last in range(n):
            ways=dp.get((mask,last),0)
            if not ways:continue
            for following in range(n):
                if not mask>>following&1 and (nums[last]%nums[following]==0 or nums[following]%nums[last]==0):
                    key=(mask|1<<following,following);dp[key]=(dp.get(key,0)+ways)%MOD
    return sum(dp.get(((1<<n)-1,last),0) for last in range(n))%MOD
'''
PAINT='''\
def minimum_wall_painting_cost(cost,time):
    n=len(cost);dp=[0]+[float('inf')]*n
    for price,saved in zip(cost,time):
        for painted in range(n,-1,-1):
            following=min(n,painted+saved+1);dp[following]=min(dp[following],dp[painted]+price)
    return dp[n]
'''
UNIQUE='''\
def count_unique_character_substrings(s):
    last={};left=0;answer=0
    for right,char in enumerate(s):
        left=max(left,last.get(char,-1)+1);last[char]=right;answer+=right-left+1
    return answer
'''
PAIRS='''\
def maximum_reversed_word_pairs(words):
    waiting={};answer=0
    for word in words:
        reverse=word[::-1]
        if waiting.get(reverse,0):waiting[reverse]-=1;answer+=1
        else:waiting[word]=waiting.get(word,0)+1
    return answer
'''

BATCH={
2740:entry('minimum_partition_value',[('nums','list[int]')],'int',['arrays','sorting'],['Split nums into two nonempty groups.','A split value is the absolute difference between the groups’ maximum and minimum values.','Return the minimum split value.'],[([[1,3,2,4]],'Separating values at an adjacent sorted gap of one attains the minimum.'),([[10,1]],'The only split separates ten and one, giving nine.')],[[x] for x in [[1,2],[10,1],[1,3,2,4],[1,100,50],[5,5],[3,8,12],[0,-3,9],[-5,-2,-9],[2,4,8,16],[7,1,7,3],[100,99,1],[4,10,6,3],[20,5,15,10],[1,9,2,8,3]]],PART,[PART.replace('right-left','right+left'),PART.replace('sorted(nums)','nums')],['Adds adjacent values instead of taking their gap.','Checks adjacency in input order rather than value order.'],partition_oracle,random_partition,['Sort values so every group boundary is visible.','The optimum separates the sorted sequence between two adjacent values.','Return the smallest adjacent sorted difference.','Any two-group separation has a crossing adjacent sorted pair no wider than its extreme gap, and cutting there attains it.'],'O(n log n)','O(n)',5),
2741:entry('count_special_permutations',[('nums','list[int]')],'int',['arrays','dynamic programming','bitmask'],['A permutation is special when every adjacent pair has one value divisible by the other.','Use every distinct nums value exactly once.','Return the number of special permutations modulo 1,000,000,007.'],[([[2,3,6]],'The valid orders are 2,6,3 and 3,6,2.'),([[1,2,4]],'Every pair involving one divides, while two divides four, so all six orders work.')],[[x] for x in [[1],[1,2],[2,3],[2,3,6],[1,2,4],[2,4,8],[3,6,12],[2,5,10],[4,6,12],[2,6,3,9],[5,10,20,4],[2,4,3,12],[7,14,2,28],[2,3,5,30]]],SPECIAL,[SPECIAL.replace(' or nums[following]%nums[last]==0',''),SPECIAL.replace('sum(dp.get','max(dp.get')],['Checks divisibility in only one direction.','Returns only the largest count ending at one final value instead of summing all endpoints.'],special_oracle,random_special,['Use a bitmask for chosen indices and remember the last index.','Append an unused value only when it is divisibility-compatible with the last value.','Accumulate counts for every (mask,last), then sum all full-mask endpoints.','Every permutation has one unique sequence of prefix states, so the transitions count each valid order exactly once.'],'O(n²2^n)','O(n2^n)',8),
2742:entry('minimum_wall_painting_cost',[('cost','list[int]'),('time','list[int]')],'int',['arrays','dynamic programming','knapsack'],['Paying painter i costs cost[i] and paints one wall while a free painter can paint time[i] additional walls.','The free painter works only while a paid painter is active.','Return the minimum cost to finish all n walls.'],[([[1,2,3,2],[1,2,3,2]],'Hiring painter zero alone covers two walls; hiring painter three covers three, totaling cost three for all four.'),([[2,3,4,2],[1,1,1,1]],'Two cost-two painters cover all four walls for total four.')],[[c,t] for c,t in [([1],[0]),([5],[10]),([1,2,3,2],[1,2,3,2]),([2,3,4,2],[1,1,1,1]),([10,1],[0,0]),([5,6,1],[0,0,2]),([8,2,7],[3,0,0]),([1,100,100],[0,5,5]),([4,3,2,1],[0,1,2,3]),([9,8,7,6],[1,1,1,1]),([2,20,3],[0,10,0]),([5,5,5,5,5],[0,0,0,0,0]),([10,2,8,3],[4,0,1,0]),([7,1,9,2,8],[0,2,0,1,4])]],PAINT,[PAINT.replace('painted+saved+1','painted+max(1,saved)'),PAINT.replace('range(n,-1,-1)','range(n+1)')],['Counts only the free-painter time when it exceeds one, omitting the paid painter’s own wall.','Updates knapsack forward, illegally hiring the same painter multiple times.'],paint_oracle,random_paint,['Hiring painter i provides capacity for 1+time[i] completed walls.','Use 0/1 knapsack where dp[j] is minimum cost to cover j walls.','Update covered counts backward and cap them at n.','Every hired subset has additive cost and coverage; backward transitions enumerate each subset once and retain its cheapest capped coverage.'],'O(n²)','O(n)',8),
2743:entry('count_unique_character_substrings',[('s','str')],'int',['strings','sliding window'],['Count nonempty substrings whose characters are all distinct.','Equal text at different positions counts as different substrings.','Return the total count.'],[(['abcd'],'All ten substrings have distinct characters.'),(['aaa'],'Only the three one-character substrings qualify.')],[[s] for s in ['a','aa','ab','aaa','abcd','abba','abcabc','dvdf','pwwkew','abab','aabcc','abcdefa','zzxy','abcaefbg']],UNIQUE,[UNIQUE.replace('max(left,','min(left,'),UNIQUE.replace('last.get(char,-1)+1','last.get(char,-1)')],['Moves the left boundary backward when an old duplicate lies outside the window.','Moves to the duplicate itself rather than the following character.'],unique_oracle,random_unique,['Maintain the longest distinct-character window ending at each position.','Store each character’s latest index and move left past a duplicate without moving backward.','Add the current window length for every right endpoint.','Every valid substring ending at right starts at or after left, giving exactly right-left+1 new substrings.'],'O(n)','O(alphabet)',5),
2744:entry('maximum_reversed_word_pairs',[('words','list[str]')],'int',['strings','hash maps','greedy'],['Every word contains exactly two lowercase letters.','Pair two unused indices when one word equals the reverse of the other.','Return the maximum number of disjoint pairs.'],[([['cd','ac','dc','ca','zz']],'cd pairs with dc and ac pairs with ca; zz has no second copy, giving two.'),([['ab','ab']],'Two identical non-palindromic words are not reverses, so no pair is possible.')],[[w] for w in [['ab'],['ab','ba'],['ab','ab'],['aa','aa'],['aa'],['cd','ac','dc','ca','zz'],['ab','ba','ab','ba'],['xy','yx','zz','zz'],['aa','aa','aa'],['ab','bc','ca'],['az','za','az'],['pq','qp','rs','sr'],['aa','bb','aa','bb'],['ab','ba','ba']]],PAIRS,[PAIRS.replace('reverse=word[::-1]','reverse=word'),PAIRS.replace('waiting[reverse]-=1','waiting[reverse]-=0')],['Pairs identical words instead of reversed words.','Leaves a matched reverse word available for reuse.'],pairs_oracle,random_pairs,['Keep counts of unmatched words.','For each new word, consume one unmatched reverse when available; otherwise store the new word.','Increment the answer on every successful consumption.','Matching immediately cannot hurt because all copies of a two-letter word have the same only compatible reverse type.'],'O(n)','O(n)',3),
}
