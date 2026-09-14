"""Hard-focused third group of workbook batch 114."""
from collections import Counter
from functools import lru_cache
from itertools import product
from math import gcd
from .import_batch_055 import entry
MOD=1_000_000_007

def good_o(a):
 nums=a[0];ans=0
 for mask in range(1,1<<len(nums)):
  value=1
  for i,x in enumerate(nums):
   if mask>>i&1:value*=x
  if value>1:
   p=2;ok=True
   while p*p<=value:
    if value%(p*p)==0:ok=False;break
    p+=1
   ans+=ok
 return ans%MOD
def gcdsort_o(a):
 nums=a[0];n=len(nums);parent=list(range(n))
 def f(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for i in range(n):
  for j in range(i):
   if gcd(nums[i],nums[j])>1:parent[f(i)]=f(j)
 target=sorted(nums);groups={}
 for i in range(n):groups.setdefault(f(i),[]).append(i)
 return all(sorted(nums[i] for i in ids)==sorted(target[i] for i in ids) for ids in groups.values())
def pal_o(a):
 s=a[0];best=0
 for assign in product(range(3),repeat=len(s)):
  x=''.join(c for c,k in zip(s,assign) if k==1);y=''.join(c for c,k in zip(s,assign) if k==2)
  if x==x[::-1] and y==y[::-1]:best=max(best,len(x)*len(y))
 return best
def gene_o(a):
 parents,nums=a;n=len(nums);children=[[] for _ in range(n)]
 for i in range(1,n):children[parents[i]].append(i)
 ans=[]
 for root in range(n):
  stack=[root];seen=set()
  while stack:
   node=stack.pop();seen.add(nums[node]);stack.extend(children[node])
  missing=1
  while missing in seen:missing+=1
  ans.append(missing)
 return ans
def game_o(a):
 n=a[0];component=[0,1]
 for order in range(2,n+1):component.append((component[order-2]^component[order-1])+1)
 return n>1 and (component[n-2]^component[n-1])!=0

def rgood(r):return [[r.randint(1,30) for _ in range(r.randint(1,11))]]
def rgcdsort(r):return [[r.randint(2,30) for _ in range(r.randint(1,10))]]
def rpal(r):return [''.join(r.choice('abcd') for _ in range(r.randint(2,9)))]
def rgene(r):
 n=r.randint(2,30);parents=[-1]+[r.randrange(i) for i in range(1,n)];return [parents,r.sample(range(1,100),n)]
def rgame(r):return [r.randint(1,20)]

GOOD='''\
def number_of_good_subsets(nums):
    from collections import Counter
    primes=[2,3,5,7,11,13,17,19,23,29]
    count=Counter(nums);dp=[0]*1024;dp[0]=pow(2,count[1],1_000_000_007)
    for value in range(2,31):
        if not count[value]:continue
        mask=0;valid=True
        for bit,prime in enumerate(primes):
            if value%(prime*prime)==0:valid=False;break
            if value%prime==0:mask|=1<<bit
        if not valid:continue
        for state in range(1023,-1,-1):
            if state&mask==0:
                dp[state|mask]=(dp[state|mask]+dp[state]*count[value])%1_000_000_007
    return sum(dp[1:])%1_000_000_007
'''
GCDSORT='''\
def can_gcd_sort(nums):
    parent={value:value for value in nums}
    def find(value):
        parent.setdefault(value,value)
        while parent[value]!=value:
            parent[value]=parent[parent[value]];value=parent[value]
        return value
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[a]=b
    for value in nums:
        remaining=value;factor=2
        while factor*factor<=remaining:
            if remaining%factor==0:
                union(value,factor)
                while remaining%factor==0:remaining//=factor
            factor+=1
        if remaining>1:union(value,remaining)
    return all(a==b or find(a)==find(b) for a,b in zip(nums,sorted(nums)))
'''
PAL='''\
def maximum_palindromic_subsequence_product(s):
    size=len(s);palindrome=[False]*(1<<size);length=[0]*(1<<size)
    for mask in range(1,1<<size):
        text=''.join(s[i] for i in range(size) if mask>>i&1)
        palindrome[mask]=text==text[::-1];length[mask]=len(text)
    answer=0;full=(1<<size)-1
    for first in range(1,1<<size):
        if not palindrome[first]:continue
        second=full^first
        subset=second
        while subset:
            if palindrome[subset]:answer=max(answer,length[first]*length[subset])
            subset=(subset-1)&second
    return answer
'''
GENE='''\
def smallest_missing_genetic_values(parents,nums):
    n=len(nums);answer=[1]*n
    if 1 not in nums:return answer
    children=[[] for _ in range(n)]
    for node in range(1,n):children[parents[node]].append(node)
    visited=[False]*n;present=set();missing=1
    def add(root):
        stack=[root]
        while stack:
            node=stack.pop()
            if visited[node]:continue
            visited[node]=True;present.add(nums[node]);stack.extend(children[node])
    node=nums.index(1)
    while node!=-1:
        add(node)
        while missing in present:missing+=1
        answer[node]=missing;node=parents[node]
    return answer
'''
GAME='''\
def alice_wins_fibonacci_tree(n):
    return n % 6 != 1
'''
def L(*x):return list(x)

BATCH={
1994:entry('number_of_good_subsets',[('nums','list[int]')],'int',['dynamic programming','bitmasks','number theory'],['nums has 1 through 100000 values from 1 through 30.','A good subset’s product contains one or more distinct primes, with no squared prime factor.','Index choices distinguish subsets; return the count modulo 1000000007.'],[([[1,2,3,4]],'The six valid index subsets use two or three, optionally with the one; four is invalid because it repeats prime two.'),([[4,2,3,15]],'The five good subsets combine the square-free values without repeating a prime factor.')],[[x] for x in [[1],[2],[4],[1,1,2],[2,3],[2,2],[6,10],[4,2,3,15],[1,2,3,4],[5,7,11],[6,15],[2,3,5,7],[8,9,25],[1,1,1,30]]],GOOD,[GOOD.replace('pow(2,count[1],1_000_000_007)','count[1] + 1'),GOOD.replace('state&mask==0','state&mask!=0')],['Counts choices of value one linearly instead of multiplying every good subset by 2^count(1).','Combines numbers only when they repeat a prime instead of when their prime masks are disjoint.'],good_o,rgood,L('Represent the prime factors of every square-free value 2..30 as a ten-bit mask.','Use subset DP over used-prime masks; skip values containing a squared prime and multiply transitions by their occurrence count.','Seed dp[0]=2^count(1); for each value, add dp[state]*count[value] to disjoint state|mask.','A good subset maps uniquely to disjoint selected prime masks and index choices; descending mask transitions use each numeric value group once.'),'O(30*2^10*10)','O(2^10)',8),
1998:entry('can_gcd_sort',[('nums','list[int]')],'bool',['union-find','prime factorization','sorting'],['nums has 1 through 30000 integers from 2 through 100000.','You may swap two positions whenever their current values have gcd greater than one.','Return whether some sequence of allowed swaps can sort nums nondecreasingly.'],[([[7,21,3]],'Twenty-one links factors seven and three, allowing the values to reach sorted order.'),([[5,2,6,2]],'Five shares no factor with another value and cannot move to its sorted position.')],[[x] for x in [[2],[7,21,3],[5,2,6,2],[10,5,9,3,15],[2,3],[4,2],[6,10,15],[7,5,3],[8,4,2],[9,3,6],[11,22,2],[12,7,6],[15,10,6,3],[25,10,14,7]]],GCDSORT,[GCDSORT.replace('if remaining>1:union(value,remaining)',''),GCDSORT.replace('factor+=1','factor+=2')],['Drops a remaining large prime factor after trial division.','Tests only even candidate factors after two and misses odd prime connections.'],gcdsort_o,rgcdsort,L('Values connected through shared prime factors can be permuted within one component.','Union every value with each distinct prime factor, then compare original and sorted values position by position.','Factor values; union(value,factor); require find(nums[i])==find(sorted_nums[i]) whenever values differ.','Allowed swaps generate exactly the factor-connectivity components, and arbitrary permutations are possible inside a connected swap graph.'),'O(n*sqrt(V)+n log n)','O(n+V)',8),
2002:entry('maximum_palindromic_subsequence_product',[('s','str')],'int',['bitmasks','backtracking','palindromes'],['s has 2 through 12 lowercase letters.','Choose two nonempty subsequences using disjoint character indices, and require both to be palindromes.','Return the maximum product of their lengths.'],[(['leetcodecom'],'The disjoint palindromes ete and cdc have lengths three and three, giving product nine.'),(['bb'],'Choose one b for each subsequence, producing product one.')],[[s] for s in ['aa','ab','bb','aba','abc','aaaa','leetcodecom','accbcaxxcxx','abcba','abacdc','abcdef','aabb','racecarx','zzxyyx']],PAL,[PAL.replace('second=full^first','second=full'),PAL.replace('text==text[::-1]','text==s[::-1]')],['Allows the second mask to reuse indices from the first subsequence.','Compares each subsequence with the reverse of the whole source string.'],pal_o,rpal,L('With at most twelve positions, bitmasks can enumerate every subsequence exactly.','Precompute which masks form palindromes, then enumerate palindrome masks inside each complement.','For palindrome first, iterate all subsets of full^first and maximize popcount products for palindrome second.','Complement restriction is exactly disjointness, and exhaustive mask enumeration includes every legal pair.'),'O(3^n+n*2^n)','O(2^n)',7),
2003:entry('smallest_missing_genetic_values',[('parents','list[int]'),('nums','list[int]')],'list[int]',['trees','depth-first-search','sets'],['parents and nums have equal length 2 through 100000; parents describes a tree rooted at zero.','Genetic values are distinct integers from 1 through 100000.','For every node, return the smallest positive value absent from its subtree.'],[([[-1,0,0,2],[1,2,3,4]],'The root contains one through four and misses five; every other subtree misses one.'),([[-1,0,1,0,3,3],[5,4,6,2,1,3]],'Only ancestors of the node holding one can have an answer greater than one, yielding [7,1,1,4,2,1].')],[[p,n] for p,n in [([-1,0],[1,2]),([-1,0],[2,1]),([-1,0,0],[1,2,3]),([-1,0,0],[3,2,1]),([-1,0,1],[2,3,4]),([-1,0,0,2],[1,2,3,4]),([-1,0,1,0,3,3],[5,4,6,2,1,3]),([-1,0,1,2],[1,4,2,3]),([-1,0,0,1,1],[5,1,2,3,4]),([-1,0,0,0],[2,4,6,8]),([-1,0,1,1],[4,3,2,1]),([-1,0,0,2,2],[10,1,3,2,4]),([-1,0,1,2,3],[5,4,3,2,1]),([-1,0,0,1,2,2],[7,6,5,4,3,1])]],GENE,[GENE.replace('node=nums.index(1)','node=0'),GENE.replace('while missing in present','while missing+1 in present')],['Updates only ancestors of the root instead of ancestors of the unique node containing value one.','Advances based on the next integer and can report a value already present.'],gene_o,rgene,L('Any subtree without value one immediately has answer one, so only one ancestor chain needs work.','Start at the node containing one and walk to the root, incrementally adding each newly included subtree to one shared set.','DFS each unvisited ancestor subtree; advance missing while present; record it; move to parent.','Off-chain subtrees lack one. Along the chain, visited nodes only grow and each tree node is added once, so every recorded set is exactly that ancestor’s subtree.'),'O(n+max answer)','O(n)',8),
2005:entry('alice_wins_fibonacci_tree',[('n','int')],'bool',['trees','game theory','dynamic programming'],['1 <= n <= 100; order zero is empty and order one is a single node.','Order n has children of orders n-2 and n-1; a move removes a chosen node and its subtree.','The player forced to delete the root loses; return whether Alice wins with optimal play.'],[([3],'The protected-root position has nonzero nim value, so Alice can leave Bob the losing state.'),([1],'There is no legal non-root removal, so Alice must delete the root and loses.')],[[n] for n in [2,4,5,6,7,8,9,10,13,15,19,20,25,31]],GAME,[GAME.replace('!= 1','== 1'),GAME.replace('% 6','% 3')],['Reverses winning and losing positions.','Uses a period of three instead of the six-order Grundy cycle.'],game_o,rgame,L('Treat deleting the protected root as the losing forced action, so legal play ends when no child component remains.','A removable rooted component has value one plus the xor of its child components; the protected root exposes only the xor.','Let c0=0,c1=1 and c[n]=(c[n-2] xor c[n-1])+1; its zero protected values occur exactly when n mod 6 is one.','The component recurrence follows the green-tree pruning mex rule. Its six-step invariant proves precisely those orders are losing.'),'O(1)','O(1)',8)
}
