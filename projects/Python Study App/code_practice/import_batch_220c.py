"""Binary concatenation, suspicious methods, GCD ranks, tree endpoints, and bitwise predecessors."""
from itertools import permutations
from math import gcd
from collections import deque
from .import_batch_055 import entry

def binary_oracle(args):return max(int(''.join(bin(x)[2:] for x in order),2) for order in permutations(args[0]))
def random_binary(rng):return [[rng.randint(1,127) for _ in range(3)]]

def methods_oracle(args):
    n,k,edges=args;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b)
    suspicious={k};stack=[k]
    while stack:
        for nxt in graph[stack.pop()]:
            if nxt not in suspicious:suspicious.add(nxt);stack.append(nxt)
    if any(a not in suspicious and b in suspicious for a,b in edges):return list(range(n))
    return [i for i in range(n) if i not in suspicious]
def random_methods(rng):
    n=rng.randint(1,12);pairs=[(a,b) for a in range(n) for b in range(n) if a!=b];rng.shuffle(pairs)
    return [n,rng.randrange(n),[list(x) for x in pairs[:rng.randint(0,min(25,len(pairs)))]]]

def gcd_oracle(args):
    nums,queries=args;values=sorted(gcd(nums[i],nums[j]) for i in range(len(nums)) for j in range(i+1,len(nums)))
    return [values[q] for q in queries]
def random_gcd(rng):
    n=rng.randint(2,16);nums=[rng.randint(1,40) for _ in range(n)];pairs=n*(n-1)//2
    return [nums,[rng.randrange(pairs) for _ in range(rng.randint(1,15))]]

def distances(graph,start):
    result=[-1]*len(graph);result[start]=0;queue=deque([start])
    while queue:
        node=queue.popleft()
        for nxt in graph[node]:
            if result[nxt]<0:result[nxt]=result[node]+1;queue.append(nxt)
    return result
def last_oracle(args):
    edges=args[0];n=len(edges)+1;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    first=distances(graph,0);a=max(range(n),key=lambda i:first[i]);da=distances(graph,a)
    b=max(range(n),key=lambda i:da[i]);db=distances(graph,b)
    return [a if x>y else b for x,y in zip(da,db)]
def random_tree(rng):
    n=rng.randint(2,20);edges=[[i,rng.randrange(i)] for i in range(1,n)];rng.shuffle(edges);return [edges]

def bit_oracle(args):
    answer=[]
    for value in args[0]:answer.append(next((x for x in range(value+1) if x|(x+1)==value),-1))
    return answer
PRIMES=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
def random_bit(rng):return [[rng.choice(PRIMES) for _ in range(rng.randint(1,18))]]

BINARY='''def maximum_binary_concatenation(nums):
    from itertools import permutations
    answer=0
    for order in permutations(nums):
        value=0
        for number in order:value=(value<<number.bit_length())|number
        answer=max(answer,value)
    return answer
'''
METHODS='''def remaining_project_methods(n,k,invocations):
    graph=[[] for _ in range(n)]
    for caller,called in invocations:graph[caller].append(called)
    suspicious={k};stack=[k]
    while stack:
        method=stack.pop()
        for called in graph[method]:
            if called not in suspicious:suspicious.add(called);stack.append(called)
    for caller,called in invocations:
        if caller not in suspicious and called in suspicious:return list(range(n))
    return [method for method in range(n) if method not in suspicious]
'''
GCD_VALUES='''def sorted_gcd_pair_queries(nums,queries):
    import bisect
    maximum=max(nums);frequency=[0]*(maximum+1)
    for value in nums:frequency[value]+=1
    exact=[0]*(maximum+1)
    for divisor in range(maximum,0,-1):
        count=sum(frequency[multiple] for multiple in range(divisor,maximum+1,divisor))
        exact[divisor]=count*(count-1)//2-sum(exact[multiple] for multiple in range(2*divisor,maximum+1,divisor))
    cumulative=[];total=0
    for value in exact:total+=value;cumulative.append(total)
    return [bisect.bisect_right(cumulative,query) for query in queries]
'''
LAST='''def last_marked_tree_nodes(edges):
    from collections import deque
    n=len(edges)+1;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    def distances(start):
        result=[-1]*n;result[start]=0;queue=deque([start])
        while queue:
            node=queue.popleft()
            for nxt in graph[node]:
                if result[nxt]<0:result[nxt]=result[node]+1;queue.append(nxt)
        return result
    first=distances(0);a=max(range(n),key=lambda i:first[i]);from_a=distances(a)
    b=max(range(n),key=lambda i:from_a[i]);from_b=distances(b)
    return [a if da>db else b for da,db in zip(from_a,from_b)]
'''
BITS='''def minimum_bitwise_predecessors(nums):
    answer=[]
    for value in nums:
        if value==2:answer.append(-1);continue
        bit=1
        while value&bit:bit<<=1
        answer.append(value^(bit>>1))
    return answer
'''
def lesson(a,b,c,d):return [a,b,c,d]

BATCH={
3309:entry('maximum_binary_concatenation',[('nums','list[int]')],'int',['bit manipulation','enumeration','sorting'],['nums contains exactly three integers in 1..127.','Concatenate the ordinary binary representations without leading zeros in any order.','Return the largest resulting base-ten integer.'],[([[1,2,3]],'Ordering 3,1,2 forms binary 11110, which is decimal 30.'),([[2,8,16]],'Ordering 2,8,16 forms binary 10100010000, which is 1296.')],[[a] for a in [[1,1,1],[1,1,2],[3,2,1],[7,1,4],[127,1,2],[5,10,20],[2,3,4],[8,4,2],[15,16,1],[6,6,3],[9,12,7],[32,1,31],[100,50,25],[127,126,125]]],BINARY,[BINARY.replace('permutations(nums)','[nums]'),BINARY.replace('number.bit_length()','7')],['Uses only the input order.','Pads every number to seven bits and introduces forbidden leading zeros.'],binary_oracle,random_binary,lesson('Only six orders exist, and bit shifts concatenate binary values without creating strings.','Try each permutation while shifting by the next number’s actual bit length.','Update value=(value<<bits)|number for all three numbers and retain the maximum.','The recurrence is exact binary concatenation and enumeration covers every allowed order.'),'O(1)','O(1)',5),
3310:entry('remaining_project_methods',[('n','int'),('k','int'),('invocations','list[list[int]]')],'list[int]',['graphs','depth first search'],['Methods are 0..n-1 and each distinct directed edge [a,b] means a invokes b.','The suspicious set contains k and every method reachable from k.','Remove that entire set only if no outside method invokes into it; otherwise return every method.'],[([4,1,[[1,2],[0,1],[3,2]]],'Outside calls from 0 and 3 enter the suspicious set, so no method is removed.'),([5,0,[[1,2],[0,2],[0,1],[3,4]]],'Methods 0,1,2 can be removed, leaving 3 and 4.')],[[n,k,e] for n,k,e in [(1,0,[]),(2,0,[[0,1]]),(2,1,[[0,1]]),(3,0,[[0,1],[1,2]]),(3,1,[[0,1],[1,2]]),(3,2,[[1,2],[0,1],[2,0]]),(4,0,[[0,1],[2,3]]),(4,1,[[1,2],[2,1]]),(5,2,[[2,3],[3,4],[0,1]]),(5,2,[[2,3],[1,3]]),(6,0,[[0,1],[1,2],[3,4],[4,5]]),(6,3,[[0,1],[3,4],[4,5]]),(4,2,[[2,3],[0,3]]),(5,4,[])]],METHODS,[METHODS.replace('caller not in suspicious','caller in suspicious'),METHODS.replace('graph[method]','graph[k]')],['Rejects removal for calls made inside the suspicious set.','Explores only direct calls from k and misses deeper suspicious methods.'],methods_oracle,random_methods,lesson('First compute exactly what k can reach; then one edge scan decides whether that whole set is removable.','Use iterative DFS from k, then look for an invocation whose caller is outside and callee inside.','Return all methods on a blocking edge; otherwise filter out the suspicious set.','Reachability defines every required removal, and the edge condition is precisely the stated all-or-nothing external dependency rule.'),'O(n+e)','O(n+e)',5),
3312:entry('sorted_gcd_pair_queries',[('nums','list[int]'),('queries','list[int]')],'list[int]',['number theory','sieve','binary search'],['nums has 2–100,000 values in 1..50,000 and every query indexes its n(n-1)/2 unordered pairs.','Sort all pairwise greatest common divisors conceptually in ascending order.','Return the GCD at every zero-based queried rank without materializing the pairs.'],[([[2,3,4],[0,2,2]],'The sorted GCDs are 1,1,2, so the requested values are 1,2,2.'),([[4,4,2,1],[5,3,1,0]],'The sorted GCDs 1,1,1,2,2,4 answer the ranks as 4,2,1,1.')],[[a,q] for a,q in [([2,2],[0]),([1,1,1],[0,2]),([2,4],[0]),([6,10,15],[0,1,2]),([4,4,2,1],[0,5]),([3,6,9,12],[1,3,5]),([5,10,20],[0,2]),([7,11,13],[0,1,2]),([8,12,16],[0,2]),([2,3,4,5],[0,5]),([6,6,6,3],[2,4]),([9,15,21,27],[1,5]),([10,20,30,40,50],[0,4,9]),([2,2,3,3],[0,3,5])]],GCD_VALUES,[GCD_VALUES.replace('range(maximum,0,-1)','range(1,maximum+1)'),GCD_VALUES.replace('bisect.bisect_right','bisect.bisect_left')],['Computes exact-divisor counts before subtracting larger multiples.','Uses lower-bound ranks and returns the previous divisor at cumulative boundaries.'],gcd_oracle,random_gcd,lesson('Count pairs divisible by each d, then subtract pairs whose exact GCD is a larger multiple of d.','Sweep divisors downward using the value-frequency sieve.','Prefix-sum exact GCD frequencies and use upper_bound(query) to recover each zero-based rank.','Möbius-style downward subtraction assigns every pair to its unique exact GCD; cumulative counts are the conceptual sorted array.'),'O(M log M+q log M)','O(M)',8),
3313:entry('last_marked_tree_nodes',[('edges','list[list[int]]')],'list[int]',['trees','breadth first search','diameter'],['edges describes an undirected tree of 2–100,000 nodes.','For each starting node, return a farthest node, which is marked last by breadthwise spreading.','For deterministic ties, use the second diameter endpoint produced by smallest-index double sweeps.'],[([[[0,1],[0,2]]],'Diameter endpoints are 1 and 2; the deterministic answers are 2,2,1.'),([[[0,1]]],'Each node’s only farthest node is the other endpoint.')],[[e] for e in [[[0,1],[1,2]],[[0,1],[0,2],[2,3],[2,4]],[[0,1],[0,2],[0,3]],[[0,1],[1,2],[2,3]],[[0,2],[2,1]],[[0,1],[1,2],[1,3]],[[0,1],[0,2],[1,3]],[[0,1],[0,2],[1,3],[2,4]],[[0,1],[1,2],[2,3],[3,4]],[[0,1],[0,2],[0,3],[3,4]],[[0,2],[2,4],[0,1],[2,3]],[[0,1],[1,2],[1,3],[3,4],[3,5]],[[0,5],[5,4],[4,3],[3,2],[2,1]],[[0,1],[0,2],[1,3],[2,4],[2,5]]]],LAST,[LAST.replace('da>db','da>=db'),LAST.replace('distances(b)','distances(0)')],['Chooses the first rather than second diameter endpoint on distance ties.','Compares distances from node zero instead of the second diameter endpoint.'],last_oracle,random_tree,lesson('A farthest node from any tree vertex is represented by at least one endpoint of a fixed diameter.','Find diameter endpoints with two BFS sweeps, then compute distances from both.','For each node return the endpoint with greater distance, choosing the second endpoint on ties.','The diameter-endpoint eccentricity theorem proves max(dist to a, dist to b) is the true farthest distance.'),'O(n)','O(n)',8),
3315:entry('minimum_bitwise_predecessors',[('nums','list[int]')],'list[int]',['bit manipulation','arrays'],['nums contains 1–100 prime values between 2 and 1,000,000,000.','For each prime p, find the smallest nonnegative x with x OR (x+1)=p.','Return -1 when impossible.'],[([[2,3,5,7]],'Two is impossible; the minimum predecessors for 3,5,7 are 1,4,3.'),([[11,13,31]],'Clearing the highest bit in each trailing-one run gives 9,12,15.')],[[a] for a in [[2],[3],[5],[7],[11],[13],[17],[19],[23],[29],[31],[37],[41],[2,2,3],[3,5,7,11],[43,47,53]]],BITS,[BITS.replace('bit>>1','bit'),BITS.replace('if value==2','if value%2==0')],['Clears the first zero bit instead of the highest bit in the trailing-one run.','Treats every even input as impossible instead of the sole prime two; this mutant also violates the declared prime-domain reasoning.'],bit_oracle,random_bit,lesson('x OR (x+1) is always odd and changes the trailing-one structure around x’s lowest zero bit.','For odd p, locate its first zero bit and clear the preceding one bit.','Return -1 for p=2; otherwise scan powers of two while p contains them and XOR the previous bit.','Clearing the highest trailing one makes increment restore the entire run, and clearing any lower bit would produce a larger x.'),'O(n log max(nums))','O(1)',5),
}

BATCH[3315]['wrong'][1]=BITS.replace('if value==2','if value<=3')
BATCH[3315]['wrong_reasons'][1]='Incorrectly treats prime three as impossible along with two.'
