"""Balanced substrings, square-product ancestors, divisibility increments, and parity balance."""
from collections import Counter
from math import isqrt
from .import_batch_055 import entry


def balanced_string_oracle(args):
    s=args[0];answer=0
    for left in range(len(s)):
        for right in range(left,len(s)):
            values=list(Counter(s[left:right+1]).values())
            if len(set(values))==1:answer=max(answer,right-left+1)
    return answer

def random_balanced_one(rng):return [''.join(rng.choice('abcdef') for _ in range(rng.randint(1,14)))]
def random_balanced_two(rng):return [''.join(rng.choice('abc') for _ in range(rng.randint(1,14)))]

def ancestor_oracle(args):
    n,edges,nums=args;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    parent=[-1]*n;stack=[0];order=[0]
    while stack:
        node=stack.pop()
        for nxt in graph[node]:
            if nxt==parent[node]:continue
            parent[nxt]=node;stack.append(nxt);order.append(nxt)
    answer=0
    for node in order[1:]:
        current=parent[node]
        while current!=-1:
            product=nums[node]*nums[current];answer+=isqrt(product)**2==product;current=parent[current]
    return answer

def random_ancestor(rng):
    n=rng.randint(1,12);edges=[[node,rng.randrange(node)] for node in range(1,n)]
    return [n,edges,[rng.randint(1,40) for _ in range(n)]]

def beautiful_oracle(args):
    nums=args[0];states={nums[0]:0}
    for value in nums[1:]:
        updated={}
        for previous,cost in states.items():
            for current in range(((value+previous-1)//previous)*previous,101,previous):
                updated[current]=min(updated.get(current,10**9),cost+current-value)
        states=updated
    return min(states.values())

def random_beautiful(rng):return [[rng.randint(1,12) for _ in range(rng.randint(1,7))]]

def balanced_array_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            values=set(nums[left:right+1]);even=sum(value%2==0 for value in values)
            if even==len(values)-even:answer=max(answer,right-left+1)
    return answer

def random_balanced_array(rng):return [[rng.randint(1,15) for _ in range(rng.randint(1,14))]]


BALANCED_ONE='''def longest_balanced_substring(s):
    answer=0
    for left in range(len(s)):
        counts={};maximum=0
        for right in range(left,len(s)):
            character=s[right];counts[character]=counts.get(character,0)+1;maximum=max(maximum,counts[character])
            if maximum*len(counts)==right-left+1:answer=max(answer,right-left+1)
    return answer
'''

BALANCED_TWO='''def longest_abc_balanced_substring(s):
    def one_character():
        answer=start=0
        for index in range(1,len(s)+1):
            if index==len(s) or s[index]!=s[start]:answer=max(answer,index-start);start=index
        return answer
    def two_characters(first,second):
        answer=0;index=0
        while index<len(s):
            while index<len(s) and s[index] not in (first,second):index+=1
            earliest={0:index-1};difference=0
            while index<len(s) and s[index] in (first,second):
                difference+=1 if s[index]==first else -1
                if difference in earliest:answer=max(answer,index-earliest[difference])
                else:earliest[difference]=index
                index+=1
        return answer
    earliest={(0,0):-1};counts={'a':0,'b':0,'c':0};three=0
    for index,character in enumerate(s):
        counts[character]+=1;key=(counts['a']-counts['b'],counts['b']-counts['c'])
        if key in earliest:three=max(three,index-earliest[key])
        else:earliest[key]=index
    return max(one_character(),two_characters('a','b'),two_characters('a','c'),two_characters('b','c'),three)
'''

ANCESTORS='''def sum_square_product_ancestors(n,edges,nums):
    limit=max(nums);smallest=list(range(limit+1))
    for prime in range(2,int(limit**0.5)+1):
        if smallest[prime]==prime:
            for value in range(prime*prime,limit+1,prime):
                if smallest[value]==value:smallest[value]=prime
    def kernel(value):
        result=1
        while value>1:
            prime=smallest[value];odd=0
            while value%prime==0:value//=prime;odd^=1
            if odd:result*=prime
        return result
    keys=[kernel(value) for value in nums];graph=[[] for _ in range(n)]
    for first,second in edges:graph[first].append(second);graph[second].append(first)
    counts={};answer=0;stack=[(0,-1,False)]
    while stack:
        node,parent,leaving=stack.pop();key=keys[node]
        if leaving:
            counts[key]-=1;continue
        answer+=counts.get(key,0);counts[key]=counts.get(key,0)+1;stack.append((node,parent,True))
        for nxt in reversed(graph[node]):
            if nxt!=parent:stack.append((nxt,node,False))
    return answer
'''

BEAUTIFUL='''def minimum_beautiful_array_operations(nums):
    states={nums[0]:0}
    for value in nums[1:]:
        updated={}
        for previous,cost in states.items():
            current=(value+previous-1)//previous*previous
            while current<=100:
                updated[current]=min(updated.get(current,10**9),cost+current-value);current+=previous
        states=updated
    return min(states.values())
'''

BALANCED_ARRAY='''def longest_distinct_parity_balanced_subarray(nums):
    answer=0
    for left in range(len(nums)):
        seen=set();even=odd=0
        for right in range(left,len(nums)):
            value=nums[right]
            if value not in seen:
                seen.add(value)
                if value%2:odd+=1
                else:even+=1
            if even==odd:answer=max(answer,right-left+1)
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

S1_CASES=[[s] for s in ('a','aa','ab','aba','abc','aabb','abca','zzabccz','abcabc','aabbbbcc','mississippi','abcdefedcba')]
S2_CASES=[[s] for s in ('a','aa','ab','aba','abc','bbcc','abca','aabca','abcabc','aabbbbcc','ccbaaacb','abccbaabc')]
A_CASES=[[n,e,v] for n,e,v in ((1,[],[1]),(2,[[0,1]],[2,8]),(3,[[0,1],[1,2]],[1,4,9]),(3,[[0,1],[0,2]],[2,3,8]),(4,[[0,1],[0,2],[1,3]],[1,2,9,5]),(4,[[0,1],[1,2],[2,3]],[2,8,18,50]),(5,[[0,1],[0,2],[1,3],[1,4]],[6,24,10,54,96]),(5,[[0,1],[0,2],[2,3],[2,4]],[1,1,1,1,1]),(6,[[0,1],[0,2],[1,3],[1,4],[2,5]],[2,3,5,8,12,20]),(6,[[0,1],[1,2],[2,3],[3,4],[4,5]],[7,28,63,112,175,252]),(7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[4,9,16,25,36,49,64]),(8,[[0,1],[0,2],[1,3],[1,4],[2,5],[5,6],[5,7]],[2,18,8,50,72,32,98,128]))]
B_CASES=[[[*values]] for values in ([4],[1,1,2],[2,3],[1,3,4],[5,6,7],[4,9,10],[10,1,1],[49,50,49],[2,5,11,23],[6,7,13,25],[3,8,17,34,50],[12,23,47,49])]
R_CASES=[[[*values]] for values in ([1],[2],[1,2],[2,4],[1,3],[2,2,3],[1,2,3,2],[2,5,4,5],[3,2,2,5,6],[2,2,4,4,1,3],[1,1,2,2,3,4],[6,7,6,9,8,11,10])]

BATCH={
3713:entry('longest_balanced_substring',[('s','str')],'int',['strings','hash maps','counting'],['s contains one to 1,000 lowercase English letters.','A substring is balanced when all characters present in it have equal frequency.','Return the maximum balanced substring length.'],[(['abbac'],'The substring abba has two copies each of a and b, so its length is four.'),(['zzabccy'],'The substring zabc contains four distinct letters once each.')],S1_CASES,BALANCED_ONE,[BALANCED_ONE.replace('maximum*len(counts)==right-left+1','maximum==right-left+1'),BALANCED_ONE.replace('maximum=max(maximum,counts[character])','maximum=counts[character]')],['Recognizes only single-character balanced windows.','Forgets the true maximum when a lower-frequency character is updated.'],balanced_string_oracle,random_balanced_one,lesson('If every present character has one common frequency f, then window length equals f times its distinct-character count.','For each left endpoint, extend right while maintaining frequencies, their maximum, and the distinct count.','A window is balanced exactly when maximum×distinct equals its length.','All counts are positive and at most the maximum, so equality of their sum with maximum×count forces every count to equal the maximum.'),'O(n²)','O(alphabet)',5),
3714:entry('longest_abc_balanced_substring',[('s','str')],'int',['strings','prefix sums','hash maps'],['s contains up to 100,000 characters, each a, b, or c.','A substring is balanced when all characters present in it have equal frequency.','Return the maximum balanced substring length.'],[(['abbac'],'The substring abba has two copies each of a and b, so its length is four.'),(['aabcc'],'The substring abc has one copy of each character, giving length three.')],S2_CASES,BALANCED_TWO,[BALANCED_TWO.replace("two_characters('b','c')","0"),BALANCED_TWO.replace("key=(counts['a']-counts['b'],counts['b']-counts['c'])","key=(counts['a']-counts['b'],counts['a']-counts['c']+1)")],['Never considers balanced substrings containing only b and c.','Offsets one prefix-difference coordinate and misses three-character matches.'],balanced_string_oracle,random_balanced_two,lesson('A balanced substring contains exactly one, two, or all three possible characters.','Handle runs for one character, prefix differences inside two-character segments, and a pair of global prefix differences for all three.','Equal prefix-difference states mark a substring with equal relevant counts; excluded third characters split the two-character cases.','The three cases exhaust every possible distinct-character set and each prefix identity is equivalent to equal frequencies.'),'O(n)','O(n)',6),
3715:entry('sum_square_product_ancestors',[('n','int'),('edges','list[list[int]]'),('nums','list[int]')],'int',['trees','depth first search','number theory'],['The rooted tree has up to 100,000 nodes, root zero, and n-1 undirected edges.','Each node value is between one and 100,000.','Count ancestor–descendant pairs whose value product is a perfect square.'],[([3,[[0,1],[1,2]],[2,8,2]],'All three ancestor pairs have products 16 or 4, so the sum is three.'),([4,[[0,1],[0,2],[1,3]],[1,2,9,4]],'Nodes two and three each match root zero, giving two pairs.')],A_CASES,ANCESTORS,[ANCESTORS.replace('keys=[kernel(value) for value in nums]','keys=nums[:]'),ANCESTORS.replace('if leaving:\n            counts[key]-=1;continue','if leaving:\n            continue')],['Compares raw values instead of their square-free kernels.','Never removes a completed branch from the active ancestor counts.'],ancestor_oracle,random_ancestor,lesson('A product is a square exactly when both values have the same square-free kernel.','Factor every value by prime-exponent parity, then count equal kernels along the current root-to-node path.','An iterative DFS adds the current kernel on entry and removes it on exit; the prior count is this node’s matching ancestors.','The active counter contains exactly and only ancestors, while kernel equality is equivalent to every product prime exponent being even.'),'O(V log log V + n log V)','O(V+n)',8),
3717:entry('minimum_beautiful_array_operations',[('nums','list[int]')],'int',['arrays','dynamic programming'],['nums contains one to 100 values, each between one and 50.','Only positions after index zero may be incremented.','Minimize increments so every value is divisible by its predecessor.'],[([[3,7,9]],'Raising seven to nine costs two and yields [3,9,9].'),([[1,1,1]],'Every adjacent divisibility condition already holds, so the cost is zero.')],B_CASES,BEAUTIFUL,[BEAUTIFUL.replace('while current<=100:','if current<=100:'),BEAUTIFUL.replace('(value+previous-1)//previous','max(1,value//previous)')],['Keeps only the smallest immediate multiple and misses globally better larger choices.','Rounds down to a positive multiple and can incorrectly count a decrement as an operation.'],beautiful_oracle,random_beautiful,lesson('The optimal choice at one position depends only on its adjusted predecessor.','Keep the minimum cost for every feasible adjusted value through 100 and transition to each multiple of the predecessor not below the original value.','Add exactly current-original to the prior cost and merge equal current values by minimum.','The DP enumerates every legal nondecreasing-by-increments chain; dominated costs with the same final value can never help later.'),'O(n·100²)','O(100)',6),
3719:entry('longest_distinct_parity_balanced_subarray',[('nums','list[int]')],'int',['arrays','hash maps','enumeration'],['nums contains one to 1,500 positive integers.','Balance compares counts of distinct even and distinct odd values, not occurrence counts.','Return the longest contiguous balanced subarray length.'],[([[2,5,4,3]],'Two distinct even and two distinct odd values make the full length four balanced.'),([[3,2,2,5,4]],'The full array has two distinct values of each parity, so its length is five.')],R_CASES,BALANCED_ARRAY,[BALANCED_ARRAY.replace('if value not in seen:','if True:'),BALANCED_ARRAY.replace('if even==odd:','if abs(even-odd)<=1:')],['Counts repeated values again instead of distinct values only.','Accepts parity counts that differ by one.'],balanced_array_oracle,random_balanced_array,lesson('Only the first occurrence of each value inside a candidate window changes its parity counts.','Fix each left endpoint, extend right, and maintain a set plus distinct even/odd counters.','Update a counter only for a newly seen value and record the length whenever the counters match.','Every subarray is visited once by its endpoints and the maintained counters exactly describe its two distinct-value sets.'),'O(n²)','O(n)',5),
}
