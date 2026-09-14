"""Vowel ordering, parity scores, power sums, separator parsing, and merges batch 184."""
from functools import lru_cache
from .import_batch_055 import entry
VOWELS=set('AEIOUaeiou')
def vowels_oracle(a):
 s=a[0];pool=iter(sorted(c for c in s if c in VOWELS));return ''.join(next(pool) if c in VOWELS else c for c in s)
def random_vowels(r):return [''.join(r.choice('abcdeiouAEIOUxyz') for _ in range(r.randint(1,40)))]
def score_oracle(a):
 nums,x=a;best=-10**9
 for mask in range(1<<(len(nums)-1)):
  chosen=[nums[0]]+[nums[i] for i in range(1,len(nums)) if mask>>(i-1)&1]
  best=max(best,sum(chosen)-x*sum(p%2!=q%2 for p,q in zip(chosen,chosen[1:])))
 return best
def random_score(r):return [[r.randint(1,20) for _ in range(r.randint(1,11))],r.randint(0,15)]
def ways_oracle(a):
 n,x=a;values=[i**x for i in range(1,n+1) if i**x<=n]
 @lru_cache(None)
 def visit(i,left):
  if left==0:return 1
  if i==len(values) or left<0:return 0
  return visit(i+1,left)+visit(i+1,left-values[i])
 return visit(0,n)%1_000_000_007
def random_ways(r):return [r.randint(1,120),r.randint(1,5)]
def split_oracle(a):
 words,separator=a;answer=[]
 for word in words:
  answer.extend(piece for piece in word.split(separator) if piece)
 return answer
def random_split(r):
 sep=r.choice('.|,$#');return [[''.join(r.choice('abc'+sep) for _ in range(r.randint(1,15))) for _ in range(r.randint(1,8))],sep]
def merge_oracle(a):
 start=tuple(a[0]);seen={start};stack=[start];best=max(start)
 while stack:
  values=stack.pop();best=max(best,max(values))
  for i in range(len(values)-1):
   if values[i]<=values[i+1]:
    nxt=values[:i]+(values[i]+values[i+1],)+values[i+2:]
    if nxt not in seen:seen.add(nxt);stack.append(nxt)
 return best
def random_merge(r):return [[r.randint(1,20) for _ in range(r.randint(1,9))]]
VOWEL='''\
def sort_vowels_in_string(s):
    vowels=set('AEIOUaeiou');ordered=iter(sorted(char for char in s if char in vowels))
    return ''.join(next(ordered) if char in vowels else char for char in s)
'''
SCORE='''\
def maximum_parity_subsequence_score(nums,x):
    best=[float('-inf')]*2;best[nums[0]%2]=nums[0]
    for value in nums[1:]:
        parity=value%2;best[parity]=max(best[parity]+value,best[1-parity]+value-x)
    return max(best)
'''
WAYS='''\
def count_distinct_power_sums(n,x):
    MOD=1_000_000_007;dp=[0]*(n+1);dp[0]=1;base=1
    while base**x<=n:
        value=base**x
        for total in range(n,value-1,-1):dp[total]=(dp[total]+dp[total-value])%MOD
        base+=1
    return dp[n]
'''
SPLIT='''\
def split_words_by_separator(words,separator):
    return [piece for word in words for piece in word.split(separator) if piece]
'''
MERGE='''\
def maximum_value_after_merges(nums):
    current=answer=nums[-1]
    for value in reversed(nums[:-1]):
        current=current+value if value<=current else value
        answer=max(answer,current)
    return answer
'''
BATCH={
2785:entry('sort_vowels_in_string',[('s','str')],'str',['strings','sorting'],['Keep every consonant at its original index.','Sort all English vowels by character code and place them back into vowel positions.','Return the resulting string.'],[(['lEetcOde'],'The vowel codes sort as E,O,e,e, producing lEOtcede.'),(['rhythm'],'There are no vowels, so the string is unchanged.')],[[s] for s in ['a','U','rhythm','lEetcOde','AEIOU','uoiea','Hello','aA','bcdEfgI','leetcode','AaEeIi','xyzou','Programming','TheQuickBrownFox']],VOWEL,[VOWEL.replace('sorted(','sorted(',1).replace('ordered=iter(sorted','ordered=iter(sorted',1).replace('))\n',',reverse=True))\n',1),VOWEL.replace("'AEIOUaeiou'","'aeiou'")],['Sorts vowel character codes in descending order.','Recognizes lowercase vowels only.'],vowels_oracle,random_vowels,['Collect vowels without moving consonants.','Sort vowel characters by their ordinary character-code order.','Iterate through s, replacing only vowel positions from the sorted iterator.','The fixed consonant positions and sorted sequence uniquely determine the required result.'],'O(n log n)','O(n)',3),
2786:entry('maximum_parity_subsequence_score',[('nums','list[int]'),('x','int')],'int',['arrays','dynamic programming'],['Choose a subsequence that must include nums[0].','Its score is the sum of chosen values minus x whenever consecutive chosen values have different parity.','Return the maximum score.'],[([[2,3,6,1,9,2],5],'An optimal parity-aware subsequence has score thirteen.'),([[2,4,6],3],'Taking every even value pays no switching penalty and scores twelve.')],[[a,x] for a,x in [([1],5),([2,3,6,1,9,2],5),([2,4,6],3),([1,2],0),([1,2],10),([2,1,2],1),([5,1,9],4),([4,3,2,1],2),([1,3,5,2],3),([10,1,10],5),([2,7,8,3],4),([6,5,4,3,2],1),([1,100,2],50),([8,1,3,10,2],6)]],SCORE,[SCORE.replace('value-x','value+x'),SCORE.replace('best[nums[0]%2]=nums[0]','best[0]=best[1]=nums[0]')],['Adds the parity-change penalty instead of subtracting it.','Pretends the required first value can end with either parity.'],score_oracle,random_score,['Keep the best score ending in an even and odd chosen value.','For each value, either extend the same parity freely or switch from the other parity and pay x.','Initialize only the parity of nums[0], then update the current value’s parity state.','These two states retain exactly the only history—last parity—that affects every future choice.'],'O(n)','O(1)',5),
2787:entry('count_distinct_power_sums',[('n','int'),('x','int')],'int',['math','dynamic programming','backtracking'],['Represent n as a sum of distinct positive integers each raised to power x.','Different selected base sets count as different representations.','Return the number of representations modulo 1,000,000,007.'],[([10,2],'Only 1²+3² equals ten, so there is one representation.'),([4,1],'The distinct sums are 4 and 1+3, giving two representations.')],[[n,x] for n,x in [(1,1),(4,1),(10,2),(100,2),(10,1),(5,2),(25,2),(9,2),(50,3),(8,3),(20,2),(15,1),(30,2),(120,3)]],WAYS,[WAYS.replace('range(n,value-1,-1)','range(value,n+1)'),WAYS.replace('base+=1','base+=2')],['Updates totals forward and therefore reuses the same base multiple times.','Considers only odd bases.'],ways_oracle,random_ways,['List every base whose x-th power is at most n.','Use a zero-one sum DP initialized with one way to make zero.','Process totals backward for each power so that base is selected at most once.','Backward knapsack transitions correspond bijectively to distinct subsets of bases.'],'O(n*n^(1/x))','O(n)',8),
2788:entry('split_words_by_separator',[('words','list[str]'),('separator','str')],'list[str]',['strings','parsing'],['Split each word wherever the one-character separator occurs.','Discard empty pieces caused by leading, trailing, or consecutive separators.','Preserve word order and piece order.'],[([['one.two.three','four.five','six'],'.'],'The pieces are one, two, three, four, five, and six in order.'),([['$easy$','$problem$'],'$'],'Empty edge pieces are discarded, leaving easy and problem.')],[[w,s] for w,s in [(['a'],'.'),(['a.b'],'.'),(['one.two.three','four.five','six'],'.'),(['$easy$','$problem$'],'$'),(['a||b'],'|'),(['...'],'.'),(['a','b'],','),(['a,b,',',c'],','),(['#a##b#'],'#'),(['x y'],' '),(['ababa'],'b'),(['1-2-3'],'-'),(['::a', 'b::'],':'),(['abc'],'c')]],SPLIT,[SPLIT.replace('if piece',''),SPLIT.replace('word.split(separator)','separator.split(word)')],['Keeps empty pieces.','Splits the separator by each word rather than each word by the separator.'],split_oracle,random_split,['Process input words from left to right.','Split each with the given literal character and filter empty strings.','Flatten the remaining pieces in comprehension order.','The language split operation identifies every separator boundary, while filtering implements the explicit empty-piece rule.'],'O(total characters)','O(output)',3),
2789:entry('maximum_value_after_merges',[('nums','list[int]')],'int',['arrays','greedy'],['Repeatedly choose adjacent values with left less than or equal to right and replace them by their sum.','Choose any valid operation order.','Return the largest array value achievable.'],[([[2,3,7,9,3]],'Right-to-left merges combine two, three, seven, and nine into twenty-one.'),([[5,3,3]],'The final pair merges to six, which then absorbs five for eleven.')],[[x] for x in [[1],[1,2],[2,1],[2,3,7,9,3],[5,3,3],[1,1,1],[10,1,2],[4,5,1],[3,2,6],[9,8,7],[1,5,2,10],[6,3,4,2],[2,8,1,9],[10,5,5,20]]],MERGE,[MERGE.replace('value<=current','value<current'),MERGE.replace('reversed(nums[:-1])','nums[:-1]')],['Disallows merging equal adjacent values.','Scans left to right even though merge feasibility depends on accumulated right suffixes.'],merge_oracle,random_merge,['Scan from right because a merged suffix is the potential absorber for its left neighbor.','If the next left value is at most the suffix sum, merge it; otherwise begin a new suffix.','Track the maximum suffix sum seen.','A value that cannot enter its immediate optimized right suffix cannot cross it, while every permitted merge grows that suffix and preserves feasibility.'],'O(n)','O(1)',5),
}

VOWEL_DESC=VOWEL.replace(
    "sorted(char for char in s if char in vowels)",
    "sorted((char for char in s if char in vowels),reverse=True)",
)
BATCH[2785]['wrong'][0]=VOWEL_DESC
