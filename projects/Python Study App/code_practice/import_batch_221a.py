"""Frequency windows, division greediness, and postorder tree intervals."""
from itertools import product
from .import_batch_055 import entry


def frequency_oracle(args):
    s,k=args;answer=0
    for left in range(len(s)):
        counts={};valid=False
        for right in range(left,len(s)):
            counts[s[right]]=counts.get(s[right],0)+1
            if counts[s[right]]>=k:valid=True
            answer+=valid
    return answer


def random_frequency(rng):
    n=rng.randint(1,18)
    return [''.join(rng.choice('abcd') for _ in range(n)),rng.randint(1,n)]


def smallest_factor(value):
    divisor=2
    while divisor*divisor<=value:
        if value%divisor==0:return divisor
        divisor+=1
    return value


def division_oracle(args):
    nums=args[0]
    choices=[]
    for value in nums:
        factor=smallest_factor(value)
        choices.append([(value,0)] if factor==value else [(value,0),(factor,1)])
    answer=None
    for selected in product(*choices):
        values=[item[0] for item in selected]
        if all(values[i]<=values[i+1] for i in range(len(values)-1)):
            cost=sum(item[1] for item in selected)
            answer=cost if answer is None else min(answer,cost)
    return -1 if answer is None else answer


def random_division(rng):
    return [[rng.randint(1,100) for _ in range(rng.randint(1,8))]]


def dfs_words(parent,s):
    children=[[] for _ in parent]
    for node in range(1,len(parent)):children[parent[node]].append(node)
    words=[]
    for root in range(len(parent)):
        output=[];stack=[(root,False)]
        while stack:
            node,exit=stack.pop()
            if exit:output.append(s[node]);continue
            stack.append((node,True))
            for child in reversed(children[node]):stack.append((child,False))
        words.append(''.join(output))
    return words


def palindrome_oracle(args):
    return [word==word[::-1] for word in dfs_words(*args)]


def random_palindrome(rng):
    n=rng.randint(1,16);parent=[-1]+[rng.randrange(i) for i in range(1,n)]
    return [parent,''.join(rng.choice('abc') for _ in range(n))]


def subtree_oracle(args):
    parent,s=args;n=len(parent);final=[-1]*n
    for node in range(1,n):
        ancestor=parent[node]
        while ancestor!=-1 and s[ancestor]!=s[node]:ancestor=parent[ancestor]
        final[node]=parent[node] if ancestor==-1 else ancestor
    children=[[] for _ in parent]
    for node in range(1,n):children[final[node]].append(node)
    sizes=[1]*n
    stack=[(0,False)]
    while stack:
        node,exit=stack.pop()
        if exit:
            sizes[node]=1+sum(sizes[child] for child in children[node])
        else:
            stack.append((node,True))
            for child in children[node]:stack.append((child,False))
    return sizes


def random_subtree(rng):
    n=rng.randint(1,20);parent=[-1]+[rng.randrange(i) for i in range(1,n)]
    return [parent,''.join(rng.choice('abcd') for _ in range(n))]


FREQUENCY='''def count_k_frequency_substrings(s,k):
    counts={};left=0;answer=0
    for char in s:
        counts[char]=counts.get(char,0)+1
        while counts[char]>=k:
            counts[s[left]]-=1;left+=1
        answer+=left
    return answer
'''

DIVISION='''def minimum_division_operations(nums):
    values=list(nums);operations=0
    limit=max(values);factor=list(range(limit+1))
    for prime in range(2,int(limit**0.5)+1):
        if factor[prime]==prime:
            for multiple in range(prime*prime,limit+1,prime):
                if factor[multiple]==multiple:factor[multiple]=prime
    for index in range(len(values)-2,-1,-1):
        if values[index]>values[index+1]:
            values[index]=factor[values[index]];operations+=1
            if values[index]>values[index+1]:return -1
    return operations
'''

PALINDROME='''def dfs_subtree_palindromes(parent,s):
    n=len(parent);children=[[] for _ in range(n)]
    for node in range(1,n):children[parent[node]].append(node)
    sequence=[];size=[0]*n;end=[0]*n;stack=[(0,False)]
    while stack:
        node,exit=stack.pop()
        if exit:
            size[node]=1+sum(size[child] for child in children[node])
            sequence.append(s[node]);end[node]=len(sequence)-1
        else:
            stack.append((node,True))
            for child in reversed(children[node]):stack.append((child,False))
    odd=[0]*n;left=0;right=-1
    for center in range(n):
        radius=1 if center>right else min(odd[left+right-center],right-center+1)
        while center-radius>=0 and center+radius<n and sequence[center-radius]==sequence[center+radius]:radius+=1
        odd[center]=radius
        if center+radius-1>right:left,right=center-radius+1,center+radius-1
    even=[0]*n;left=0;right=-1
    for center in range(n):
        radius=0 if center>right else min(even[left+right-center+1],right-center+1)
        while center-radius-1>=0 and center+radius<n and sequence[center-radius-1]==sequence[center+radius]:radius+=1
        even[center]=radius
        if center+radius-1>right:left,right=center-radius,center+radius-1
    answer=[]
    for node in range(n):
        start=end[node]-size[node]+1;length=size[node]
        if length%2:center=(start+end[node])//2;answer.append(odd[center]>=length//2+1)
        else:center=(start+end[node]+1)//2;answer.append(even[center]>=length//2)
    return answer
'''

SUBTREE='''def changed_parent_subtree_sizes(parent,s):
    n=len(parent);children=[[] for _ in range(n)]
    for node in range(1,n):children[parent[node]].append(node)
    nearest={};new_parent=[-1]*n;order=[];stack=[(0,False)]
    while stack:
        node,exit=stack.pop();char=s[node]
        if exit:
            nearest[char].pop()
            continue
        if node:new_parent[node]=nearest.get(char,[-1])[-1] if nearest.get(char) else parent[node]
        nearest.setdefault(char,[]).append(node);order.append(node);stack.append((node,True))
        for child in reversed(children[node]):stack.append((child,False))
    sizes=[1]*n
    for node in reversed(order[1:]):sizes[new_parent[node]]+=sizes[node]
    return sizes
'''


def lesson(a,b,c,d):return [a,b,c,d]


FREQUENCY_CASES=[[s,k] for s,k in [('a',1),('a',2),('aa',1),('aa',2),('ab',2),('aaa',2),('abab',2),('aabb',2),('abcabc',2),('zzzzz',3),('abca',2),('mississippi',3),('leetcode',2),('abcd',4)]]
PALINDROME_CASES=[[p,s] for p,s in [([-1],'a'),([-1,0],'aa'),([-1,0],'ab'),([-1,0,0],'aba'),([-1,0,0],'abc'),([-1,0,1,1],'abba'),([-1,0,1,2],'aaaa'),([-1,0,0,1,1],'abcba'),([-1,0,0,2,2],'aabaa'),([-1,0,1,1,2,2],'abccba'),([-1,0,0,0],'abca'),([-1,0,1,1,3],'abcab'),([-1,0,0,1,2,3,3],'abacaba'),([-1,0,1,0,2,2,4,4],'aabbccaa')]]
SUBTREE_CASES=[[p,s] for p,s in [([-1],'a'),([-1,0],'aa'),([-1,0],'ab'),([-1,0,0],'aaa'),([-1,0,1,2],'aaaa'),([-1,0,1,2],'abca'),([-1,0,0,1,1],'ababa'),([-1,0,0,2,2],'abcac'),([-1,0,1,1,2,2],'abccba'),([-1,0,0,0],'abca'),([-1,0,1,1,3],'abcab'),([-1,0,0,1,2,3,3],'abacaba'),([-1,0,1,0,2,2,4,4],'aabbccaa'),([-1,0,0,1,1,2,2,3],'abcdabcd')]]


BATCH={
3325:entry('count_k_frequency_substrings',[('s','str'),('k','int')],'int',['strings','sliding window','hash maps'],['s has 1–3,000 lowercase letters and 1 <= k <= len(s).','Count every nonempty substring in which at least one character occurs at least k times.','Different start/end positions count separately even when their text is equal.'],[(['abacb',2],'The valid intervals spell aba, abac, abacb, and bacb, for four total.'),(['abcde',1],'Every one of the 15 nonempty substrings contains a character once.')],FREQUENCY_CASES,FREQUENCY,[FREQUENCY.replace('answer+=left','answer+=left+1'),FREQUENCY.replace('while counts[char]>=k','while counts[char]>k')],['Adds one invalid start position for every ending index.','Shrinks only after the triggering frequency exceeds k, so it misses boundary-valid substrings.'],frequency_oracle,random_frequency,lesson('For each right endpoint, valid starts form a prefix once some frequency reaches k.','Move left until the newest character occurs fewer than k times; the number removed equals the valid-start count.','Increment the new character, shrink while its count is at least k, then add left to the answer.','Before adding, starts below left are exactly those whose window contained k copies; starts at or above left do not.'),'O(n)','O(alphabet)',5),
3326:entry('minimum_division_operations',[('nums','list[int]')],'int',['arrays','greedy','number theory'],['nums has 1–100,000 values in 1..1,000,000.','One operation divides a value by its greatest proper divisor, changing a composite value to its smallest prime factor.','Return the fewest operations making nums nondecreasing, or -1 when impossible.'],[([[25,7]],'Twenty-five becomes 5 after division by its greatest proper divisor 5, producing [5,7].'),([[7,7,6]],'A prime seven cannot be reduced by the operation, so the final inversion cannot be repaired.')],[[a] for a in [[1],[2,1],[4,2],[6,3],[6,2],[8,4],[9,3],[25,7],[10,5,2],[16,8,4,2],[12,6,3],[15,10,5],[100,10,2],[2,3,5,7]]],DIVISION,[DIVISION.replace('range(len(values)-2,-1,-1)','range(len(values)-1)'),DIVISION.replace('return -1','return operations',1)],['Repairs left to right even though lowering a later value can invalidate an earlier comparison.','Returns the operations used so far when the array is still impossible.'],division_oracle,random_division,lesson('A useful operation maps a composite number directly to its smallest prime factor; repeating cannot reduce that prime.','Precompute smallest prime factors, then scan right to left so the fixed suffix supplies the allowed upper bound.','When values[i] exceeds its neighbor, replace it once; fail if it remains too large.','Each inversion forces that element’s only useful reduction, and the sieve supplies it in constant time during the scan.'),'O(M log log M+n)','O(M+n)',5),
3327:entry('dfs_subtree_palindromes',[('parent','list[int]'),('s','str')],'list[bool]',['trees','depth first search','manacher algorithm'],['parent and s describe a rooted tree of up to 100,000 nodes; parent[0] is -1.','A node’s DFS word visits children in increasing node order and appends the node character after all children.','Return whether every node’s complete subtree DFS word is a palindrome.'],[([[-1,0,0,1,1,2],'aababa'],'The root word is abaaba and node 2 gives ab, so the answers distinguish their palindrome status.'),([[-1,0,0,0,0],'aabcb'],'The root word abcba is a palindrome and every child contributes a one-letter palindrome.')],PALINDROME_CASES,PALINDROME,[PALINDROME.replace('children[parent[node]].append(node)','children[parent[node]].insert(0,node)'),PALINDROME.replace('answer.append(even[center]>=length//2)','answer.append(False)')],['Visits siblings in decreasing rather than increasing node order.','Declares every even-length subtree word non-palindromic.'],palindrome_oracle,random_palindrome,lesson('Every subtree occupies one contiguous interval in the global postorder character sequence.','Build that sequence and each interval, then preprocess all odd/even palindrome radii with Manacher’s algorithm.','Iterative postorder records subtree size and end; query the appropriate center radius for each interval.','Postorder contiguity converts every subtree question to an exact substring query, and Manacher answers all such queries in linear total time.'),'O(n)','O(n)',8),
3329:entry('count_large_k_frequency_substrings',[('s','str'),('k','int')],'int',['strings','sliding window','hash maps'],['s has 1–300,000 lowercase letters and 1 <= k <= len(s).','Count every nonempty substring in which at least one character occurs at least k times.','The required algorithm must handle the larger constraint without enumerating substrings.'],[(['abacb',2],'The four qualifying intervals are aba, abac, abacb, and bacb.'),(['abcde',1],'All 15 nonempty substrings qualify because each contains some character once.')],FREQUENCY_CASES,FREQUENCY.replace('count_k_frequency_substrings','count_large_k_frequency_substrings'),[FREQUENCY.replace('count_k_frequency_substrings','count_large_k_frequency_substrings').replace('answer+=left','answer+=len(s)-left'),FREQUENCY.replace('count_k_frequency_substrings','count_large_k_frequency_substrings').replace('counts[s[left]]-=1','counts[char]-=1')],['Counts suffix length rather than the number of valid starting positions.','Decrements the triggering character rather than the character that leaves the window.'],frequency_oracle,random_frequency,lesson('For a fixed right endpoint, every start before a boundary is valid and every later start is invalid.','Maintain the smallest window whose frequencies are all below k after removing the valid-start prefix.','Add the new character, shrink while it alone reaches k, and accumulate the boundary index.','Only the newly added character can newly reach k, so the single shrink condition preserves the invariant in O(n).'),'O(n)','O(alphabet)',7),
3331:entry('changed_parent_subtree_sizes',[('parent','list[int]'),('s','str')],'list[int]',['trees','depth first search','hash maps'],['parent and s describe a rooted tree of up to 100,000 nodes; parent[0] is -1.','Every nonroot node simultaneously moves to its closest original ancestor with the same character, if one exists.','Return all subtree sizes in the final tree.'],[([[-1,0,0,1,1,1],'abaabc'],'Node 3 moves from parent 1 to same-character ancestor 0; final sizes are 6,3,1,1,1,1.'),([[-1,0,4,0,1],'abbba'],'Nodes 4 and 2 choose closest matching ancestors in the original tree, producing sizes 5,2,1,1,1.')],SUBTREE_CASES,SUBTREE,[SUBTREE.replace("nearest.get(char,[-1])[-1]","nearest.get(char,[-1])[0]"),SUBTREE.replace('else parent[node]','else 0')],['Chooses the highest matching ancestor rather than the closest one.','Moves nodes with no matching ancestor to the root instead of leaving their parent unchanged.'],subtree_oracle,random_subtree,lesson('Simultaneous changes must consult ancestors in the original tree, not parents already changed.','During original-tree DFS, keep a stack of active ancestors for each character.','Assign the closest matching stack top, then aggregate final sizes from descendants toward ancestors.','The active stack exactly represents original ancestors; every new parent remains an ancestor, so reverse DFS order safely accumulates each subtree once.'),'O(n)','O(n)',6),
}
