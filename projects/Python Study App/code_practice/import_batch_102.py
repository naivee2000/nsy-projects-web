"""Opening of batch 102: counting, bit concatenation, sets, and prefix sums."""
from collections import Counter
from .import_batch_055 import entry
MOD=1_000_000_007
def pairs_o(a):
 nums,target=a;counts=Counter(nums);answer=0
 for value in list(counts):
  other=target-value
  if value==other:answer+=counts[value]//2;counts[value]=0
  elif counts[value] and counts[other]:take=min(counts[value],counts[other]);answer+=take;counts[value]-=take;counts[other]-=take
 return answer
def binary_o(a):return int(''.join(bin(i)[2:] for i in range(1,a[0]+1)),2)%MOD
def consistent_o(a):
 allowed,words=a;return sum(not(set(word)-set(allowed)) for word in words)
def differences_o(a):return [sum(abs(value-other) for other in a[0]) for value in a[0]]
def matches_o(a):
 teams=a[0];answer=0
 while teams>1:played=teams//2;answer+=played;teams=played+teams%2
 return answer
def rpairs(r):return [[r.randint(-10,20) for _ in range(r.randint(1,30))],r.randint(-10,30)]
def rbinary(r):return [r.randint(1,40)]
def rconsistent(r):
 letters=list('abcdef');r.shuffle(letters);allowed=''.join(letters[:r.randint(1,6)]);return [allowed,[''.join(r.choice('abcdef') for _ in range(r.randint(1,8))) for _ in range(r.randint(1,20))]]
def rdifferences(r):return [sorted(r.randint(-20,20) for _ in range(r.randint(1,30)))]
def rmatches(r):return [r.randint(1,1000)]
PAIRS='''def maximum_k_sum_pairs(nums, k):
 counts=Counter(nums);answer=0
 for value in list(counts):
  other=k-value
  if value>other:continue
  take=counts[value]//2 if value==other else min(counts[value],counts[other]);answer+=take
 return answer
'''
BINARY='''def concatenated_binary_value(n):
 answer=0;bits=0
 for value in range(1,n+1):
  if value&(value-1)==0:bits+=1
  answer=((answer<<bits)|value)%1000000007
 return answer
'''
CONSISTENT='''def count_consistent_strings(allowed, words):
 permitted=set(allowed)
 return sum(all(char in permitted for char in word) for word in words)
'''
DIFFERENCES='''def sorted_absolute_difference_sums(nums):
 total=sum(nums);left_sum=0;n=len(nums);answer=[]
 for index,value in enumerate(nums):
  left=value*index-left_sum;right=(total-left_sum-value)-value*(n-index-1);answer.append(left+right);left_sum+=value
 return answer
'''
MATCHES='''def tournament_match_count(n):
 return n-1
'''
def L(a,b,c,d):return [a,b,c,d]
def E(*a):return entry(*a)
BATCH={
1679:E('maximum_k_sum_pairs',[('nums','list[int]'),('k','int')],'int',['hash-maps','greedy'],['Each array entry may be used in at most one pair.','Return the maximum number of disjoint pairs whose values sum to k.'],[([[1,2,3,4],5],'Pair one with four and two with three for two operations.'),([[3,1,3,4,3],6],'Only two of the three values equal to three can form one pair.')],[[*x] for x in [([1,2,3,4],5),([3,1,3,4,3],6),([],5),([1],2),([1,1],2),([1,1,1],2),([1,2],3),([1,2,2,3],4),([0,0,0,0],0),([-1,1,-2,2],0),([5,5,5,5],10),([1,4,2,3,2,3],5),([10,0,5,5],10),([2,2,8,8,5],10)]],PAIRS,[PAIRS.replace('counts[value]//2','counts[value]'),PAIRS.replace('if value>other:continue','if value>=other:continue')],['Uses every equal value instead of requiring two copies per self-complement pair.','Skips the self-complement case entirely.'],pairs_o,rpairs,L('A value can pair only with its complement k-value.','Count values and process each unordered complement pair once.','For distinct values add the smaller count; for value=k/2 add count//2.','These choices consume every possible complement match and pairs from different value groups cannot compete.'),'O(n)','O(n)',5),
1680:E('concatenated_binary_value',[('n','int')],'int',['bit-manipulation','math'],['1 <= n <= 100,000.','Concatenate the ordinary binary forms of 1 through n and return the resulting integer modulo 1,000,000,007.'],[([1],'The concatenation is binary 1, whose value is one.'),([3],'Binary forms 1,10,11 concatenate to 11011, decimal twenty-seven.')],[[n] for n in [1,2,3,4,5,6,7,8,9,10,16,31,32,100]],BINARY,[BINARY.replace('if value&(value-1)==0','if value&(value-1)!=0'),BINARY.replace('|value','|(value-1)')],['Increases the bit width at non-powers of two instead of powers of two.','Appends each value minus one.'],binary_o,rbinary,L('Appending value’s binary digits shifts the current result left by that value’s bit length.','Track bit length, increasing it exactly at powers of two.','For value 1..n, update bits on powers of two and set answer=((answer<<bits)|value) mod M.','The shift opens exactly the required digit positions and OR copies value into them, matching string concatenation.'),'O(n)','O(1)',5),
1684:E('count_consistent_strings',[('allowed','str'),('words','list[str]')],'int',['sets','strings'],['allowed contains unique lowercase letters; words are nonempty lowercase strings.','A word is consistent only when every one of its characters belongs to allowed.'],[(['ab',['ad','bd','aaab','baa','badab']],'Only aaab and baa use no characters outside a or b.'),(['abc',['a','b','c','ab','ac','bc','abc']],'Every listed word uses only allowed letters, giving seven.')],[[*x] for x in [('ab',['ad','bd','aaab','baa','badab']),('abc',['a','b','c','ab','ac','bc','abc']),('a',['a']),('a',['b']),('abc',['d']),('z',['zz','zzz']),('ab',['','a']),('xyz',['xy','yz','xz']),('abc',['abcd','abc']),('abcdef',['fed','cab']),('q',['qqq','pq']),('ab',['ba','abba']),('abcd',['dcba','ace']),('mno',['moon','no'])]],CONSISTENT,[CONSISTENT.replace('all(char in permitted','any(char in permitted'),CONSISTENT.replace('for word in words','for word in set(words)')],['Accepts a word when any one character is allowed.','Deduplicates repeated words even though each array entry must be counted.'],consistent_o,rconsistent,L('Consistency is set containment of each word’s characters.','Build the allowed set once and test every character of every word.','Count words for which all character membership checks pass.','All checks are necessary and together sufficient; processing entries individually preserves duplicates.'),'O(total characters)','O(alphabet)',3),
1685:E('sorted_absolute_difference_sums',[('nums','list[int]')],'list[int]',['prefix-sums','arrays'],['nums is sorted nondecreasing and nonempty.','At each index return the sum of absolute differences from that value to every array entry.'],[([[2,3,5]],'For values two, three, and five the sums are four, three, and five.'),([[1,4,6,8,10]],'Prefix and suffix contributions produce 24,15,13,15,21.')],[[x] for x in [[2,3,5],[1,4,6,8,10],[1],[1,1],[1,2],[-2,0,2],[0,0,0],[1,2,3,4],[-5,-3,-3,10],[2,2,3,5],[0,10,20],[1,1,1,2],[3,7,11,15],[1,100]]],DIFFERENCES,[DIFFERENCES.replace('value*index-left_sum','left_sum-value*index'),DIFFERENCES.replace('n-index-1','n-index')],['Reverses the sign of every left-side contribution.','Counts the current value as part of the right-side width.'],differences_o,rdifferences,L('Sorted order removes absolute-value ambiguity on each side of an index.','Use prefix sum for smaller values and total-minus-prefix for larger values.','Left contribution is value*i-left_sum; right is right_sum-value*(n-i-1).','Every earlier value contributes value-other and every later value contributes other-value, so the two formulas partition the full sum.'),'O(n)','O(n)',5),
1688:E('tournament_match_count',[('n','int')],'int',['math','simulation'],['1–200 teams; each match eliminates exactly one team.','Rounds continue until one champion remains. Return total matches.'],[([7],'Eliminating six teams to leave one champion requires six matches.'),([14],'Thirteen eliminations occur across all rounds.')],[[n] for n in [1,2,3,4,5,6,7,8,9,10,14,31,100,200]],MATCHES,[MATCHES.replace('n-1','n'),MATCHES.replace('return n-1','return n//2')],['Counts one match too many.','Counts only the first round.'],matches_o,rmatches,L('Every match removes exactly one team from championship contention.','Count eliminations instead of simulating odd and even rounds.','To reduce n teams to one survivor, return n-1.','There are n-1 eliminated teams and each match eliminates exactly one, so the match count is fixed regardless of byes.'),'O(1)','O(1)',3),
}

BATCH[1684]['boundaries']=[arguments for arguments in BATCH[1684]['boundaries'] if all(arguments[1])]
BATCH[1684]['boundaries'].append(['a',['a','a']])
