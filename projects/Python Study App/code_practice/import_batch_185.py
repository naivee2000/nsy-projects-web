"""Increasing groups, palindromic tree paths, targets, complete windows, and superstrings batch 185."""
from collections import Counter
from functools import lru_cache
from itertools import combinations,permutations
from .import_batch_055 import entry

def groups_oracle(a):
 limits=tuple(a[0]);n=len(limits)
 def possible(g):
  @lru_cache(None)
  def place(size,remaining):
   if size==0:return True
   for chosen in combinations([i for i,v in enumerate(remaining) if v],size):
    nxt=list(remaining)
    for i in chosen:nxt[i]-=1
    if place(size-1,tuple(nxt)):return True
   return False
  return g<=n and place(g,limits)
 return max(g for g in range(1,n+1) if possible(g))
def random_groups(r):return [[r.randint(1,5) for _ in range(r.randint(1,7))]]
def paths_oracle(a):
 parent,s=a;masks=[0]*len(parent)
 for node in range(1,len(parent)):masks[node]=masks[parent[node]]^(1<<(ord(s[node])-97))
 return sum((masks[i]^masks[j]).bit_count()<=1 for i in range(len(parent)) for j in range(i+1,len(parent)))
def random_paths(r):
 n=r.randint(1,30);return [[-1]+[r.randrange(i) for i in range(1,n)],''.join(r.choice('abcde') for _ in range(n))]
def target_oracle(a):return sum(value>=a[1] for value in a[0])
def random_target(r):return [[r.randint(0,20) for _ in range(r.randint(1,40))],r.randint(0,20)]
def complete_oracle(a):
 nums=a[0];needed=len(set(nums));return sum(len(set(nums[i:j]))==needed for i in range(len(nums)) for j in range(i+1,len(nums)+1))
def random_complete(r):return [[r.randint(1,8) for _ in range(r.randint(1,35))]]
def combine(left,right):
 if right in left:return left
 for size in range(min(len(left),len(right)),0,-1):
  if left.endswith(right[:size]):return left+right[size:]
 return left+right
def shortest_oracle(a):return min((combine(combine(x,y),z) for x,y,z in permutations(a)),key=lambda s:(len(s),s))
def random_shortest(r):return [''.join(r.choice('abc') for _ in range(r.randint(1,5))) for _ in range(3)]

GROUPS='''\
def maximum_increasing_groups(usageLimits):
    total=groups=0
    for limit in sorted(usageLimits):
        total+=limit
        if total>=(groups+1)*(groups+2)//2:groups+=1
    return groups
'''
PATHS='''\
def count_palindromic_tree_paths(parent,s):
    counts={0:1};masks=[0]*len(parent);answer=0
    for node in range(1,len(parent)):
        mask=masks[parent[node]]^(1<<(ord(s[node])-97));masks[node]=mask
        answer+=counts.get(mask,0)
        for bit in range(26):answer+=counts.get(mask^(1<<bit),0)
        counts[mask]=counts.get(mask,0)+1
    return answer
'''
TARGET='''\
def employees_meeting_target(hours,target):
    return sum(value>=target for value in hours)
'''
COMPLETE='''\
def count_complete_subarrays(nums):
    required=len(set(nums));counts={};left=0;answer=0
    for right,value in enumerate(nums):
        counts[value]=counts.get(value,0)+1
        while len(counts)==required:
            old=nums[left];counts[old]-=1
            if counts[old]==0:del counts[old]
            left+=1
        answer+=left
    return answer
'''
SHORTEST='''\
def shortest_three_string_superstring(a,b,c):
    from itertools import permutations
    def merge(left,right):
        if right in left:return left
        for size in range(min(len(left),len(right)),0,-1):
            if left.endswith(right[:size]):return left+right[size:]
        return left+right
    candidates=[merge(merge(first,second),third) for first,second,third in permutations((a,b,c))]
    return min(candidates,key=lambda value:(len(value),value))
'''
BATCH={
2790:entry('maximum_increasing_groups',[('usageLimits','list[int]')],'int',['arrays','sorting','greedy'],['Create groups whose sizes are strictly increasing.','Each group uses distinct number types, and type i may be used at most usageLimits[i] times across groups.','Return the maximum number of groups.'],[([[1,2,5]],'The limits support groups of sizes one, two, and three, so the answer is three.'),([[2,1,2]],'Only two increasing groups can be supplied.')],[[x] for x in [[1],[1,1],[1,2,5],[2,1,2],[1,1,1],[3,3,3],[1,2,3,4],[5,1],[2,2,2,2],[10,1,1],[1,5,5],[4,2,1,3],[6,6,1],[2,3,5,7]]],GROUPS,[GROUPS.replace('>=','>',1),GROUPS.replace('sorted(usageLimits)','usageLimits')],['Requires surplus capacity beyond the exact triangular demand.','Processes types in input order instead of increasing capacity order.'],groups_oracle,random_groups,['Sort usage limits and accumulate available uses.','After g groups, total demand is g(g+1)/2.','Whenever accumulated capacity reaches demand for g+1 groups, increment g.','Sorting exposes scarce types first; surplus capacity carries forward and the triangular threshold is both necessary and sufficient.'],'O(n log n)','O(n)',8),
2791:entry('count_palindromic_tree_paths',[('parent','list[int]'),('s','str')],'int',['trees','bit manipulation','prefix masks'],['parent defines a rooted tree at node zero; character s[i] labels the edge from parent[i] to i for i>0.','Count unordered pairs of distinct nodes whose path characters can be rearranged into a palindrome.','A multiset forms a palindrome when at most one character count is odd.'],[([[-1,0,0,1,1,2],'acaabc'],'The path parity masks produce eight node pairs with at most one odd character.'),([[-1,0],'aa'],'The sole path has one character and is palindromic.')],[[p,s] for p,s in [([-1],'a'),([-1,0],'aa'),([-1,0,0],'abc'),([-1,0,0,1,1,2],'acaabc'),([-1,0,1],'aaa'),([-1,0,1],'abc'),([-1,0,0,0],'aaaa'),([-1,0,1,2],'abca'),([-1,0,0,1],'abbb'),([-1,0,1,1,2],'aacba'),([-1,0,0,2,2],'abcaa'),([-1,0,1,2,3],'aaaaa'),([-1,0,0,1,2,2],'abccba'),([-1,0,1,1,3,3],'aabcde')]],PATHS,[PATHS.replace('<=1','==0'),PATHS.replace('range(26)','range(25)')],['Counts only paths with every character even.','Never permits z as the one odd character.'],paths_oracle,random_paths,['Represent odd character counts along each root path by a 26-bit XOR mask.','The mask on a path between two nodes is the XOR of their root masks.','For each node, count earlier masks equal to its mask or differing in one bit.','Those and only those XOR results have zero or one set bit, exactly the palindrome-rearrangement condition.'],'O(26n)','O(n)',8),
2798:entry('employees_meeting_target',[('hours','list[int]'),('target','int')],'int',['arrays','counting'],['hours[i] is the study time completed by employee i.','Count employees whose hours are at least target.','Return that count.'],[([[0,1,2,3,4],2],'Employees with two, three, and four hours meet the target, giving three.'),([[5,5],5],'Both values equal the inclusive target, so both count.')],[[h,t] for h,t in [([0],0),([0],1),([0,1,2,3,4],2),([5,5],5),([1,2,3],4),([10,1,10],10),([2,2,2],2),([1,5,9],5),([0,10],5),([3,7,2,8],6),([100],99),([4,3,2,1],3),([6,6,5,7],6),([0,0,1],0)]],TARGET,[TARGET.replace('>=','>'),TARGET.replace('sum(','len([').replace(' for value in hours)', ' for value in hours])')],['Treats equality with target as insufficient.','Returns the number of booleans generated rather than the number that are true.'],target_oracle,random_target,['Each employee can be classified independently.','Compare every hours value with the inclusive threshold.','Sum the resulting booleans.','In Python true contributes one and false zero, so the sum is exactly the qualifying count.'],'O(n)','O(1)',3),
2799:entry('count_complete_subarrays',[('nums','list[int]')],'int',['arrays','sliding window','hash maps'],['A subarray is complete when it contains every distinct value appearing anywhere in nums.','Count all nonempty contiguous complete subarrays.','Return the total count.'],[([[1,3,1,2,2]],'Exactly four subarrays contain all three distinct values one, two, and three.'),([[5,5]],'The two singleton subarrays and the full array all contain the sole distinct value.')],[[x] for x in [[1],[5,5],[1,2],[1,3,1,2,2],[1,2,3],[1,1,2],[1,2,1,2],[3,2,1,3],[7,7,7],[1,2,3,4,1],[2,1,2,3,2],[4,5,4,6],[1,1,2,2,3,3],[9,8,9,7,8]]],COMPLETE,[COMPLETE.replace('answer+=left','answer+=left+1'),COMPLETE.replace('while len(counts)==required','if len(counts)==required')],['Adds one extra candidate start for every right endpoint.','Shrinks the window only once and leaves additional removable starts uncounted.'],complete_oracle,random_complete,['Track a frequency map in a right-expanding window.','While the window contains every global distinct value, remove from its left.','After shrinking, left equals the number of valid starts for this right endpoint; add it.','Every earlier start still contains all required values and every later start does not, so exactly left subarrays are counted.'],'O(n)','O(distinct)',5),
2800:entry('shortest_three_string_superstring',[('a','str'),('b','str'),('c','str')],'str',['strings','greedy','enumeration'],['Return a string containing a, b, and c as substrings.','First minimize result length; among tied shortest results choose the lexicographically smallest.','Input strings may already contain one another.'],[(['abc','bca','aaa'],'Merging aaa before bca gives aaabca, the shortest lexicographically smallest result.'),(['ab','ba','ab'],'Only ab and ba need joining; aba is the shortest result.')],[[a,b,c] for a,b,c in [('a','b','c'),('abc','bca','aaa'),('ab','ba','ab'),('a','a','a'),('abc','bc','c'),('cat','at','t'),('ab','bc','ca'),('aa','ab','ba'),('x','xy','xyz'),('cab','abc','bca'),('zz','za','az'),('aba','bab','ab'),('hello','ell','lo'),('ac','ca','aa')]],SHORTEST,[SHORTEST.replace('if right in left:return left',''),SHORTEST.replace('key=lambda value:(len(value),value)','key=len')],['Fails to remove a string already contained inside another.','Ignores lexicographic tie-breaking among equal shortest results.'],shortest_oracle,random_shortest,['Try all six input orders because only three strings exist.','Merge an ordered pair using the largest suffix-prefix overlap, first discarding a contained string.','Build each ordered candidate and minimize by (length,text).','Any shortest superstring induces an occurrence order; maximal overlaps minimize that order, and enumerating all orders plus lexicographic comparison finds the required optimum.'],'O(total length)','O(total length)',5),
}

BATCH[2791]['wrong'][0]=PATHS.replace(
    "        for bit in range(26):answer+=counts.get(mask^(1<<bit),0)\n",
    "",
)
BATCH[2791]['boundaries'].append([[-1,0],'az'])
