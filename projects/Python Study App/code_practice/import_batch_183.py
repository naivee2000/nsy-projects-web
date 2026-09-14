"""Divisor positions, beauty windows, dominant splits, forbidden substrings, and good arrays batch 183."""
from collections import Counter
from .import_batch_055 import entry

def squares_oracle(a):
 nums=a[0];n=len(nums);return sum(v*v for i,v in enumerate(nums,1) if n%i==0)
def random_squares(r):return [[r.randint(-30,30) for _ in range(r.randint(1,40))]]
def beauty_oracle(a):
 nums,k=a;return max(sum(abs(x-center)<=k for x in nums) for center in range(min(nums)-k,max(nums)+k+1))
def random_beauty(r):return [[r.randint(0,50) for _ in range(r.randint(1,30))],r.randint(0,15)]
def split_oracle(a):
 nums=a[0]
 for i in range(len(nums)-1):
  left=Counter(nums[:i+1]);right=Counter(nums[i+1:])
  if any(c*2>i+1 and right[v]*2>len(nums)-i-1 for v,c in left.items()):return i
 return -1
def random_dominant(r):return [[r.randint(1,6) for _ in range(r.randint(2,30))]]
def forbidden_oracle(a):
 word,forbidden=a;bad=set(forbidden);return max((j-i for i in range(len(word)) for j in range(i+1,len(word)+1) if all(word[x:y] not in bad for x in range(i,j) for y in range(x+1,j+1))),default=0)
def random_forbidden(r):
 word=''.join(r.choice('abcd') for _ in range(r.randint(1,18)));bad={''.join(r.choice('abcd') for _ in range(r.randint(1,4))) for _ in range(r.randint(1,8))};return [word,sorted(bad)]
def good_oracle(a):
 nums=a[0];n=len(nums)-1;return Counter(nums)==Counter(list(range(1,n+1))+[n])
def random_good(r):return [[r.randint(1,10) for _ in range(r.randint(2,15))]]

SQUARES='''\
def sum_special_index_squares(nums):
    n=len(nums)
    return sum(value*value for index,value in enumerate(nums,1) if n%index==0)
'''
BEAUTY='''\
def maximum_array_beauty(nums,k):
    nums=sorted(nums);left=0;answer=0
    for right,value in enumerate(nums):
        while value-nums[left]>2*k:left+=1
        answer=max(answer,right-left+1)
    return answer
'''
SPLIT='''\
def minimum_dominant_split_index(nums):
    from collections import Counter
    dominant,total=Counter(nums).most_common(1)[0];left=0
    for index,value in enumerate(nums[:-1]):
        left+=value==dominant
        if left*2>index+1 and (total-left)*2>len(nums)-index-1:return index
    return -1
'''
FORBIDDEN='''\
def longest_substring_without_forbidden(word,forbidden):
    bad=set(forbidden);left=0;answer=0
    for right in range(len(word)):
        for start in range(right,max(left-1,right-10),-1):
            if word[start:right+1] in bad:left=start+1;break
        answer=max(answer,right-left+1)
    return answer
'''
GOOD='''\
def is_good_array(nums):
    n=len(nums)-1
    return sorted(nums)==list(range(1,n+1))+[n]
'''
BATCH={
2778:entry('sum_special_index_squares',[('nums','list[int]')],'int',['arrays','math'],['Use one-based positions in nums.','A position i is special when the array length is divisible by i.','Return the sum of squares of values at special positions.'],[([[1,2,3,4]],'Positions one, two, and four divide length four, contributing 1+4+16=21.'),([[2,7,1]],'Positions one and three divide length three, contributing four and one.')],[[x] for x in [[1],[1,2],[1,2,3,4],[2,7,1],[0,5,0,5],[3,3,3,3,3,3],[-2,4,-6,8],[10,1,1,1,1],[1,2,3,4,5,6],[9,8,7,6,5,4,3,2],[5,0,2],[4,3,2,1,0],[-1,-2,-3],list(range(1,13))]],SQUARES,[SQUARES.replace('n%index==0','n%index!=0'),SQUARES.replace('value*value','value')],['Uses positions that do not divide the length.','Adds raw values instead of their squares.'],squares_oracle,random_squares,['Enumerate with one-based indices.','Test n modulo each index.','Square and add exactly when the remainder is zero.','The divisibility condition independently classifies every position, so direct filtering is complete.'],'O(n)','O(1)',3),
2779:entry('maximum_array_beauty',[('nums','list[int]'),('k','int')],'int',['arrays','sorting','sliding window'],['Each value may independently be replaced by any integer within k of itself.','Beauty is the greatest achievable frequency of one common resulting value.','Return the maximum beauty.'],[([[4,6,1,2],2],'Values one, two, and four can all become a common value, giving beauty three.'),([[1,1,1],0],'All three values already match.')],[[a,k] for a,k in [([1],0),([1,1,1],0),([4,6,1,2],2),([1,10],4),([1,10],5),([3,5,7],1),([0,0,5],3),([1,2,3,4],0),([10,8,6,4],2),([5,1,5,1],2),([2,9,3,8],3),([100,1,50],25),([7,7,8,8],0),([1,4,7,10,13],3)]],BEAUTY,[BEAUTY.replace('2*k','k'),BEAUTY.replace('>2*k','>=2*k')],['Allows a total original-value span of only k instead of 2k.','Treats intervals touching at one endpoint as disjoint.'],beauty_oracle,random_beauty,['Two values can reach a common target exactly when their k-radius intervals overlap.','After sorting, a feasible group has maximum minus minimum at most 2k.','Use a sliding window and shrink while its span exceeds 2k.','For one-dimensional equal-radius intervals, the extremes overlap iff every interval shares a common point.'],'O(n log n)','O(n)',5),
2780:entry('minimum_dominant_split_index',[('nums','list[int]')],'int',['arrays','hash maps','prefix counts'],['A value is dominant in an array when it appears in more than half its positions.','Split after index i so the same value is dominant in both nonempty parts.','Return the smallest valid i, or -1.'],[([[1,2,2,2]],'Splitting after index two leaves 2 dominant in [1,2,2] and [2].'),([[3,3,3,3,7,2,2]],'No split makes one value dominant in both halves.')],[[x] for x in [[1,1],[1,2],[1,2,2,2],[3,3,3,3,7,2,2],[2,2,1],[1,1,2,1],[5,5,5,1,2],[1,2,1,2],[4,4,3,4,3,4],[9,1,9,9,2,9],[1,1,1,2,2],[2,1,2,1,2],[7,7,8,8,7,7],[3,4,3,4,3,3,3]]],SPLIT,[SPLIT.replace('>index+1','>=index+1'),SPLIT.replace('return -1','return len(nums)-1')],['Accepts exactly-half frequency as dominant on the left.','Returns the final index instead of -1 when no nonempty split works.'],split_oracle,random_dominant,['Any valid common dominant must be the full array’s dominant value.','Count that candidate globally, then scan its prefix count.','At each nonfinal index test strict majority in both prefix and suffix; return the first success.','If one value dominates both disjoint parts, their counts add to a strict majority overall, proving no other candidate is needed.'],'O(n)','O(n)',5),
2781:entry('longest_substring_without_forbidden',[('word','str'),('forbidden','list[str]')],'int',['strings','sliding window','hash maps'],['A substring is valid when it contains no member of forbidden as a contiguous substring.','Every forbidden word has length at most ten.','Return the maximum valid substring length.'],[(['cbaaaabc',['aaa','cb']],'The longest valid substring has length four after excluding occurrences of cb and aaa.'),(['abc',['d']],'No forbidden text occurs, so the entire length three is valid.')],[[w,b] for w,b in [('a',['a']),('a',['b']),('abc',['d']),('cbaaaabc',['aaa','cb']),('aaaa',['aa']),('abcdef',['bc']),('ababab',['aba']),('xyz',['x','z']),('mississippi',['issi']),('leetcode',['code']),('abcabc',['abc','cab']),('zzzz',['z']),('abacada',['aca','da']),('thequick',['he','quick'])]],FORBIDDEN,[FORBIDDEN.replace('right-10','right-9'),FORBIDDEN.replace('left=start+1','left=start')],['Checks only suffixes of length at most nine and misses a ten-character forbidden word.','Keeps the forbidden occurrence’s first character inside the window.'],forbidden_oracle,random_forbidden,['Track the earliest allowed start for a window ending at each right index.','Only inspect suffixes ending at right of length at most ten.','When a forbidden suffix is found, move left just after its start; record the window length.','Every newly created forbidden occurrence must end at the newly added character, so these bounded suffix checks are sufficient.'],'O(10n)','O(forbidden)',8),
2784:entry('is_good_array',[('nums','list[int]')],'bool',['arrays','sorting','counting'],['Let n be one less than nums length.','The array is good when it contains each value 1 through n-1 once and value n exactly twice.','Return whether nums has precisely that multiset.'],[([[2,1,3]],'Here n=2, but the required multiset is [1,2,2], so the array is not good.'),([[1,3,3,2]],'Here n=3 and the sorted values are exactly 1,2,3,3.')],[[x] for x in [[1,1],[1,2],[2,1,3],[1,3,3,2],[1,2,2],[1,2,3,3],[1,1,2],[2,2],[1,2,3,4,4],[1,2,3,4,5],[3,1,2,3],[1,4,2,4,3],[5,4,3,2,1,5],[1,2,2,3]]],GOOD,[GOOD.replace('+[n]',''),GOOD.replace('n=len(nums)-1','n=len(nums)')],['Requires only one copy of the maximum n.','Uses the array length itself as n.'],good_oracle,random_good,['The required multiset is uniquely determined by the array length.','Set n=len(nums)-1 and construct 1 through n followed by one extra n.','Compare that target with sorted nums.','Sorted equality is equivalent to exact equality of every required value count.'],'O(n log n)','O(n)',3),
}

# Explicitly exercises the declared maximum forbidden-word length.
BATCH[2781]['boundaries'].append(['abcdefghijx',['abcdefghij']])
