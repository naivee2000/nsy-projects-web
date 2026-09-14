"""Segmentation DP, subset products, factor traversal, trimming, and diagonals batch 174."""

from collections import deque
from functools import lru_cache
from itertools import combinations
from math import gcd

from .import_batch_055 import entry


def extras_oracle(args):
    s,words=args
    @lru_cache(None)
    def visit(index):
        if index==len(s):return 0
        best=1+visit(index+1)
        for word in words:
            if s.startswith(word,index):best=min(best,visit(index+len(word)))
        return best
    return visit(0)


def random_extras(rng):
    s=''.join(rng.choice('abc') for _ in range(rng.randint(1,18)))
    words={''.join(rng.choice('abc') for _ in range(rng.randint(1,5))) for _ in range(rng.randint(1,10))}
    return [s,sorted(words)]


def strength_oracle(args):
    nums=args[0]
    return max(product for size in range(1,len(nums)+1) for chosen in combinations(nums,size)
               for product in [__import__('math').prod(chosen)])


def random_strength(rng):return [[rng.randint(-8,8) for _ in range(rng.randint(1,13))]]


def traversal_oracle(args):
    nums=args[0];graph=[[] for _ in nums]
    for left,right in combinations(range(len(nums)),2):
        if gcd(nums[left],nums[right])>1:graph[left].append(right);graph[right].append(left)
    seen={0};queue=deque([0])
    while queue:
        for neighbor in graph[queue.popleft()]:
            if neighbor not in seen:seen.add(neighbor);queue.append(neighbor)
    return len(seen)==len(nums)


def random_traversal(rng):return [[rng.randint(1,40) for _ in range(rng.randint(1,12))]]


def zeros_oracle(args):
    value=args[0];end=len(value)
    while end>0 and value[end-1]=='0':end-=1
    return value[:end]


def random_zeros(rng):return [''.join(rng.choice('0123456789') for _ in range(rng.randint(1,40))).lstrip('0') or '1']


def diagonals_oracle(args):
    grid=args[0];rows=len(grid);columns=len(grid[0]);answer=[]
    for row in range(rows):
        output=[]
        for column in range(columns):
            upper={grid[row-step][column-step] for step in range(1,min(row,column)+1)}
            lower={grid[row+step][column+step] for step in range(1,min(rows-row,columns-column))}
            output.append(abs(len(upper)-len(lower)))
        answer.append(output)
    return answer


def random_diagonals(rng):
    rows,columns=rng.randint(1,7),rng.randint(1,7)
    return [[[rng.randint(1,8) for _ in range(columns)] for _ in range(rows)]]


EXTRAS="""\
def minimum_extra_string_characters(s,dictionary):
    words=set(dictionary);dp=[0]*(len(s)+1)
    for end in range(1,len(s)+1):
        dp[end]=dp[end-1]+1
        for start in range(end):
            if s[start:end] in words:dp[end]=min(dp[end],dp[start])
    return dp[-1]
"""

STRENGTH="""\
def maximum_nonempty_subset_product(nums):
    positives=[value for value in nums if value>0];negatives=sorted(value for value in nums if value<0)
    if len(negatives)%2:negatives.pop()
    chosen=positives+negatives
    if chosen:
        product=1
        for value in chosen:product*=value
        return product
    return 0 if 0 in nums else max(nums)
"""

TRAVERSAL="""\
def gcd_connected_traversal(nums):
    if len(nums)==1:return True
    if 1 in nums:return False
    parent=list(range(len(nums)));size=[1]*len(nums)
    def find(node):
        while parent[node]!=node:parent[node]=parent[parent[node]];node=parent[node]
        return node
    def union(first,second):
        first,second=find(first),find(second)
        if first==second:return
        if size[first]<size[second]:first,second=second,first
        parent[second]=first;size[first]+=size[second]
    owner={}
    for index,value in enumerate(nums):
        factor=2
        while factor*factor<=value:
            if value%factor==0:
                union(index,owner.setdefault(factor,index))
                while value%factor==0:value//=factor
            factor+=1
        if value>1:union(index,owner.setdefault(value,index))
    root=find(0)
    return all(find(index)==root for index in range(len(nums)))
"""

ZEROS="""\
def remove_decimal_trailing_zeros(num):
    return num.rstrip('0')
"""

DIAGONALS="""\
def diagonal_distinct_differences(grid):
    rows=len(grid);columns=len(grid[0]);answer=[[0]*columns for _ in range(rows)]
    for row in range(rows):
        for column in range(columns):
            upper=set();r,c=row-1,column-1
            while r>=0 and c>=0:upper.add(grid[r][c]);r-=1;c-=1
            lower=set();r,c=row+1,column+1
            while r<rows and c<columns:lower.add(grid[r][c]);r+=1;c+=1
            answer[row][column]=abs(len(upper)-len(lower))
    return answer
"""


BATCH={
2707:entry('minimum_extra_string_characters',[('s','str'),('dictionary','list[str]')],'int',['strings','dynamic programming','hash maps'],
 ['Split any collection of nonoverlapping substrings from s whose exact values appear in dictionary.','Characters not covered by chosen dictionary words are extra.','Return the minimum possible number of extra characters.'],
 [(['leetscode',['leet','code','leetcode']],'Choose leet and code, leaving only s as one extra character.'),(['sayhelloworld',['hello','world']],'Using hello and world leaves the three-character prefix say extra.')],
 [[s,w] for s,w in [('a',['a']),('a',['b']),('abc',['a','bc']),('abc',['ab']),('aaaa',['a','aa']),('catsanddog',['cat','cats','and','sand','dog']),('applepenapple',['apple','pen']),('leetcode',['leet','code']),('ababa',['aba','ba']),('xyz',[]),('aaaaab',['aa','ab']),('mississippi',['miss','sip','pi']),('abcabc',['abc','bca']),('thequick',['the','quick','he'])]],
 EXTRAS,[EXTRAS.replace('dp[end-1]+1','dp[end-1]'),EXTRAS.replace('range(end)','range(end-1)')],
 ['Treats every unmatched character as free.','Never considers a dictionary word equal to the full current prefix.'],extras_oracle,random_extras,
 ['Let dp[i] be the minimum extras in the first i characters.','Default to treating s[i-1] as one extra character.','For every earlier boundary j whose substring s[j:i] is a dictionary word, minimize with dp[j].','Every optimal segmentation ends either in one extra character or one complete dictionary word, so the recurrence exhausts its final choice.'],'O(n²)','O(n+dictionary)',5),
2708:entry('maximum_nonempty_subset_product',[('nums','list[int]')],'int',['arrays','greedy','sorting'],
 ['Choose any nonempty index subset of nums.','Its strength is the product of its selected values.','Return the maximum possible strength, preserving duplicate indices as separate choices.'],
 [([[3,-1,-5,2,5,-9]],'Using all six values produces the positive maximum product 1350.'),([[-4,-5,-4]],'Choosing the two values -5 and -4 gives the maximum product twenty.')],
 [[a] for a in [[1],[0],[-1],[1,2],[-1,-2],[-1,0],[0,0],[1,-1],[2,-3,-4],[-4,-5,-4],[3,-1,-5,2,5,-9],[1,2,0,-1],[5,0,0],[-5,-4,-3,-2,-1]]],
 STRENGTH,[STRENGTH.replace('negatives.pop()','negatives.pop(0)'),STRENGTH.replace("return 0 if 0 in nums else max(nums)","return -1 if 0 in nums else max(nums)")],
 ['Drops the most negative value when an odd count should drop the one closest to zero.','Incorrectly treats a negative singleton as better than an available zero.'],strength_oracle,random_strength,
 ['Every positive value greater than zero can only improve a positive product.','Use all negatives when their count is even; when odd, discard the negative closest to zero.','If no nonzero product remains, choose zero when available, otherwise the largest negative singleton.','Two negatives multiply positively, and exchanging a retained negative for one with larger magnitude cannot decrease the resulting positive product.'],'O(n log n)','O(n)',5),
2709:entry('gcd_connected_traversal',[('nums','list[int]')],'bool',['arrays','union find','number theory','prime factorization'],
 ['Indices i and j have a direct traversal edge when gcd(nums[i],nums[j]) is greater than one.','Determine whether every index belongs to one connected component through any number of traversal edges.','Return True for a one-element array and False when a larger array contains one.'],
 [([[2,3,6]],'Value six connects the indices containing two and three, so all indices are reachable.'),([[3,9,5]],'The value five shares no prime factor with the other values, so traversal is disconnected.')],
 [[a] for a in [[1],[2],[1,2],[2,3],[2,4],[2,3,6],[3,9,5],[6,10,15],[4,8,16],[7,11,13],[2,5,10,15],[12,18,25,30],[6,35,10,21],[2,2,3,6]]],
 TRAVERSAL,[TRAVERSAL.replace('if 1 in nums:return False','if 1 in nums:return True'),TRAVERSAL.replace("        if value>1:union(index,owner.setdefault(value,index))\n",'')],
 ['Treats one as connected to every other value.','Forgets the remaining prime factor after trial division finishes.'],traversal_oracle,random_traversal,
 ['Factor every value into distinct prime factors.','Use a disjoint-set structure to join indices sharing an already-seen prime owner.','After processing all factors, verify every index has the same representative.','Two values have gcd greater than one exactly when they share a prime, and union transitivity exactly matches paths of allowed traversals.'],'O(n*sqrt(M))','O(n+primes)',8),
2710:entry('remove_decimal_trailing_zeros',[('num','str')],'str',['strings'],
 ['num is the ordinary decimal representation of a positive integer.','Remove every zero at the end of the string and no other character.','Return the remaining nonempty decimal string.'],
 [(['51230100'],'Removing the final two zeros leaves 512301.'),(['123'],'There is no trailing zero, so the string is unchanged.')],
 [[s] for s in ['1','10','100','101','1001','1000','51230100','123','9090900','1000000000','50005000','7','1203040500','9990']],
 ZEROS,[ZEROS.replace("rstrip('0')","replace('0','')"),ZEROS.replace("rstrip('0')","rstrip()")],
 ['Removes zero digits from the middle of the number as well as its suffix.','Strips whitespace rather than zero characters.'],zeros_oracle,random_zeros,
 ['Trailing zeros form one suffix.','Use a right-side strip restricted to the character zero.','Return the stripped string directly.','The positive-integer representation contains a nonzero digit, so only the maximal zero suffix is removed and the result remains nonempty.'],'O(n)','O(n)',3),
2711:entry('diagonal_distinct_differences',[('grid','list[list[int]]')],'list[list[int]]',['matrices','hash maps'],
 ['For each cell, inspect its top-left diagonal before the cell and its bottom-right diagonal after the cell.','Count distinct values on each side, excluding the cell itself.','Return their absolute count difference at every matrix position.'],
 [([[[1,2,3],[3,1,5],[3,2,1]]],'The distinct diagonal counts yield rows [1,1,0], [1,0,1], and [0,1,1].'),([[[1,2],[3,4]]],'Opposite corner cells see one diagonal value while the other two see none, producing [[1,0],[0,1]].')],
 [[g] for g in [[[1]],[[1,2]],[[1],[2]],[[1,2],[3,4]],[[1,1],[1,1]],[[1,2,3],[4,5,6],[7,8,9]],[[1,2,3],[3,1,5],[3,2,1]],[[1,2,1],[2,1,2]],[[5,4,3,2]],[[5],[4],[3],[2]],[[1,2,3,4],[5,1,7,8],[9,10,1,12]],[[3,3,3],[3,3,3]],[[1,2],[1,2],[1,2]],[[9,1,9],[1,2,1],[9,1,9]]]],
 DIAGONALS,[DIAGONALS.replace('abs(len(upper)-len(lower))','len(upper)+len(lower)'),DIAGONALS.replace('r,c=row-1,column-1','r,c=row,column')],
 ['Adds the two distinct counts instead of taking their absolute difference.','Includes the current cell in the top-left set.'],diagonals_oracle,random_diagonals,
 ['For each output cell, use two sets.','Walk repeatedly up-left from the preceding diagonal cell, and down-right from the following diagonal cell.','Store the absolute difference of the two set sizes.','The walks enumerate exactly the two open diagonal rays, while sets collapse repeats as required by distinct counting.'],'O(rows*columns*min(rows,columns))','O(min(rows,columns))',5),
}

BATCH[2711]['sample_contract_adapter']={
 'source_sample':'Input grid = [[1,2,3],[3,1,5],[3,2,1]] → Output Output: [[1,1,0],[1,0,1],[0,1,1]].',
 'arguments':[[[1,2,3],[3,1,5],[3,2,1]]],'expected':[[1,1,0],[1,0,1],[0,1,1]],
 'reason':'The workbook duplicates the Output label before the literal; this adapter preserves the matrix input and stated result while removing that label typo.'}
