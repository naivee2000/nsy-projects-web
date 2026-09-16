"""Prime sums, special string operations, component cost, and palindromic graph paths."""
from collections import deque
from itertools import combinations
from .import_batch_055 import entry

def primes(count):
    limit=10
    while True:
        sieve=[True]*(limit+1);sieve[:2]=[False,False]
        for value in range(2,int(limit**0.5)+1):
            if sieve[value]:sieve[value*value:limit+1:value]=[False]*(((limit-value*value)//value)+1)
        result=[i for i,flag in enumerate(sieve) if flag]
        if len(result)>=count:return result[:count]
        limit*=2

def prime_oracle(args):
    n,m=args;allowed=[p for p in primes(m) if p<=n];distance=[-1]*(n+1);distance[0]=0;queue=deque([0])
    while queue:
        total=queue.popleft()
        for p in allowed:
            nxt=total+p
            if nxt<=n and distance[nxt]<0:distance[nxt]=distance[total]+1;queue.append(nxt)
    return distance[n]

def random_prime(rng):return [rng.randint(1,100),rng.randint(1,30)]

def string_oracle(args):
    result=''
    for char in args[0]:
        if char.isalpha():result+=char
        elif char=='*':result=result[:-1]
        elif char=='#':result=result+result
        else:result=result[::-1]
    return result

def random_string(rng):return [''.join(rng.choice('abc*#%') for _ in range(rng.randint(1,16)))]

def component_oracle(args):
    n,edges,k=args;answer=10**30
    for mask in range(1<<len(edges)):
        parent=list(range(n));cost=0
        def find(x):
            while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
            return x
        for i,(u,v,w) in enumerate(edges):
            if mask>>i&1:
                a,b=find(u),find(v);parent[a]=b;cost=max(cost,w)
        if len({find(i) for i in range(n)})<=k:answer=min(answer,cost)
    return answer

def random_component(rng):
    n=rng.randint(1,7);pairs=list(combinations(range(n),2));rng.shuffle(pairs)
    chosen=set(pairs[:max(0,n-1)])
    for i in range(1,n):chosen.add((rng.randrange(i),i))
    remaining=[p for p in pairs if p not in chosen];rng.shuffle(remaining);chosen|=set(remaining[:rng.randint(0,min(3,len(remaining)))])
    return [n,[[u,v,rng.randint(1,15)] for u,v in chosen],rng.randint(1,n)]

def kth_oracle(args):
    result=string_oracle([args[0]]);k=args[1]
    return result[k] if k<len(result) else '.'

def random_kth(rng):
    while True:
        s=''.join(rng.choice('abc*#%') for _ in range(rng.randint(1,15)));result=string_oracle([s])
        if len(result)<=100000:return [s,rng.randint(0,max(3,len(result)+2))]

def palindrome_oracle(args):
    n,edges,label=args;graph=[[] for _ in range(n)]
    for u,v in edges:graph[u].append(v);graph[v].append(u)
    answer=1
    def visit(node,mask,text):
        nonlocal answer
        if text==text[::-1]:answer=max(answer,len(text))
        for nxt in graph[node]:
            if not mask>>nxt&1:visit(nxt,mask|1<<nxt,text+label[nxt])
    for start in range(n):visit(start,1<<start,label[start])
    return answer

def random_palindrome(rng):
    n=rng.randint(1,7);pairs=list(combinations(range(n),2));rng.shuffle(pairs);count=rng.randint(max(0,n-1),min(len(pairs),n+3))
    return [n,[list(edge) for edge in pairs[:count]],''.join(rng.choice('abc') for _ in range(n))]

PRIME='''def minimum_prime_sum_count(n,m):
    primes=[];candidate=2
    while len(primes)<m:
        if all(candidate%p for p in primes if p*p<=candidate):primes.append(candidate)
        candidate+=1
    best=[0]+[float('inf')]*n
    for prime in primes:
        for total in range(prime,n+1):best[total]=min(best[total],best[total-prime]+1)
    return best[n] if best[n]<float('inf') else -1
'''

PROCESS='''def process_special_string(s):
    result=[]
    for char in s:
        if char.isalpha():result.append(char)
        elif char=='*' and result:result.pop()
        elif char=='#':result.extend(result)
        elif char=='%':result.reverse()
    return ''.join(result)
'''

COMPONENT='''def minimize_maximum_component_cost(n,edges,k):
    if k>=n:return 0
    parent=list(range(n));components=n
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for u,v,weight in sorted(edges,key=lambda edge:edge[2]):
        u=find(u);v=find(v)
        if u!=v:
            parent[u]=v;components-=1
            if components<=k:return weight
    return 0
'''

KTH='''def kth_processed_string_character(s,k):
    length=0
    for char in s:
        if char=='*':length=max(0,length-1)
        elif char=='#':length*=2
        elif char!='%':length+=1
    if k>=length:return '.'
    for char in reversed(s):
        if char=='*':length+=1
        elif char=='#':
            length//=2
            if k>=length:k-=length
        elif char=='%':k=length-1-k
        else:
            length-=1
            if k==length:return char
    return '.'
'''

PALINDROME='''def longest_palindromic_graph_path(n,edges,label):
    graph=[[] for _ in range(n)]
    for u,v in edges:graph[u].append(v);graph[v].append(u)
    queue=[];seen=set();answer=1
    for node in range(n):queue.append((1<<node,node,node));seen.add((1<<node,node,node))
    for u,v in edges:
        if label[u]==label[v]:
            state=((1<<u)|(1<<v),u,v);queue.append(state);seen.add(state);answer=2
    for mask,left,right in queue:
        answer=max(answer,mask.bit_count())
        for outer_left in graph[left]:
            if mask>>outer_left&1:continue
            for outer_right in graph[right]:
                if outer_left==outer_right or mask>>outer_right&1 or label[outer_left]!=label[outer_right]:continue
                state=(mask|(1<<outer_left)|(1<<outer_right),outer_left,outer_right)
                if state not in seen:seen.add(state);queue.append(state)
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

P_CASES=[[n,m] for n,m in ((1,1),(2,1),(3,1),(4,1),(5,1),(7,6),(17,4),(20,3),(25,2),(31,1),(100,10),(999,1000))]
S_CASES=[[s] for s in ('a','*','ab*','ab#','abc%','z*%','a##','ab%#','abc**','a#%','ab#*%','abc#%**')]
C_CASES=[[n,e,k] for n,e,k in ((1,[],1),(2,[[0,1,7]],2),(2,[[0,1,7]],1),(3,[[0,1,1],[1,2,9],[0,2,5]],2),(3,[[0,1,1],[1,2,9],[0,2,5]],1),(4,[[0,1,5],[1,2,5],[2,3,5]],4),(5,[[0,1,9],[1,2,1],[2,3,8],[3,4,2]],3),(4,[[0,1,3],[0,2,4],[0,3,10]],2),(5,[[0,1,2],[1,2,4],[2,3,6],[3,4,8],[0,4,10]],2),(3,[[0,1,100],[1,2,1]],2),(6,[[0,1,1],[1,2,2],[2,3,3],[3,4,4],[4,5,5]],3),(4,[[0,1,8],[1,2,2],[2,3,7],[0,3,3]],1))]
K_CASES=[[s,k] for s,k in (('a',0),('a',1),('*',0),('z*#',0),('ab#',2),('ab%',0),('ab%',1),('a##',3),('abc**',0),('dc%#*#',3),('ab#%*',2),('a##########',100))]
L_CASES=[[n,e,s] for n,e,s in ((1,[],'a'),(2,[[0,1]],'aa'),(2,[[0,1]],'ab'),(3,[[0,1],[0,2]],'aac'),(4,[[0,2],[0,3],[3,1]],'abac'),(4,[[0,1],[1,2],[2,3]],'abba'),(4,[[0,1],[1,2],[2,3]],'abca'),(5,[[0,1],[1,2],[2,3],[3,4]],'abcba'),(5,[[0,1],[0,2],[0,3],[0,4]],'aaaaa'),(4,[[0,1],[1,2],[2,0],[2,3]],'abac'),(6,[[0,1],[1,2],[2,3],[3,4],[4,5]],'aabbaa'),(5,[[0,1],[1,2],[2,3],[3,4],[4,0]],'abcab'))]

BATCH={
3610:entry('minimum_prime_sum_count',[('n','int'),('m','int')],'int',['dynamic programming','number theory','coin change'],['Target n is one to 1000 and m is one to 1000.','Use any of the first m primes any number of times.','Return the minimum count summing exactly to n, or -1.'],[([10,2],'Using primes two and three, 2+2+3+3 needs four terms.'),([15,5],'Three copies of five reach fifteen.')],P_CASES,PRIME,[PRIME.replace('range(prime,n+1)','range(n,prime-1,-1)'),PRIME.replace('best[total-prime]+1','best[total-prime]+2')],['Treats each prime as usable only once.','Charges two terms for each chosen prime.'],prime_oracle,random_prime,lesson('The first m primes act like reusable coin denominations.','Generate the primes, then run unbounded minimum-coin DP.','Scan totals upward for each prime and relax count from total-prime.','Upward scans permit reuse, and every multiset has a final selected prime represented by a relaxation.'),'O(m sqrt(p_m)+m*n)','O(n+m)',6),
3612:entry('process_special_string',[('s','str')],'str',['strings','simulation'],['One to 20 lowercase letters or *, #, %.','Letters append, * removes the last character when present, # duplicates, and % reverses.','Process strictly left to right.'],[(['a#b%*'],'The states a, aa, aab, baa, ba produce ba.'),(['z*#'],'Removing z leaves an empty string that remains empty when duplicated.')],S_CASES,PROCESS,[PROCESS.replace('result.pop()','result.clear()'),PROCESS.replace('result.extend(result)','result.extend(result[:1])')],['Clears the whole result instead of removing one character.','Duplicates only the first character instead of the entire result.'],string_oracle,random_string,lesson('Each token transforms only the current result.','Simulate with a mutable character list.','Append, pop conditionally, extend by itself, or reverse according to the token.','Applying the four exact transformations in input order reproduces the specified state after every prefix.'),'O(output length across operations)','O(final output length)',5),
3613:entry('minimize_maximum_component_cost',[('n','int'),('edges','list[list[int]]'),('k','int')],'int',['graphs','union find','minimum spanning trees'],['The input graph is connected with up to 50,000 nodes and 100,000 weighted edges.','Remove edges so at most k components remain.','Minimize the largest retained edge weight; isolated components cost zero.'],[([5,[[0,1,4],[1,2,3],[1,3,2],[3,4,6]],2],'Edges through weight four connect all but one allowed component.'),([4,[[0,1,5],[1,2,5],[2,3,5]],1],'One connected component requires retaining edges of weight five.')],C_CASES,COMPONENT,[COMPONENT.replace('components<=k','components<k'),COMPONENT.replace("sorted(edges,key=lambda edge:edge[2])","sorted(edges,key=lambda edge:edge[2],reverse=True)")],['Builds one component too many before stopping.','Processes expensive edges before cheap ones.'],component_oracle,random_component,lesson('For threshold w, edges no heavier than w determine the fewest components achievable at that cost.','Run Kruskal until the component count reaches k.','Union edges by increasing weight and return the weight of the union that makes components no more than k.','Kruskal maximizes connectivity under each threshold, so the first qualifying threshold is optimal.'),'O(E log E)','O(n)',6),
3614:entry('kth_processed_string_character',[('s','str'),('k','int')],'str',['strings','reverse simulation','math'],['The instruction string has up to 100,000 tokens.','The conceptual result length is at most 10^15 and k is zero-based.','Return a dot when k lies outside the final result.'],[(['a#b%*',1],'The final string is ba, whose index one is a.'),(['cd%#*#',3],'The final string dcddcd has d at index three.')],K_CASES,KTH,[KTH.replace('if k>=length:k-=length','if k>length:k-=length'),KTH.replace('k=length-1-k','k=length-k')],['Maps the first position of the duplicated second half incorrectly.','Uses an off-by-one index when reversing.'],kth_oracle,random_kth,lesson('Only the result length is needed forward; the requested index can be mapped backward through operations.','Compute final length, reject an out-of-range k, then invert each token in reverse.','Undo doubling by folding k into the first half, undo reversal by mirroring, and identify the appended letter when its position is reached.','Each inverse mapping preserves the character occupying k without constructing the exponentially large result.'),'O(len(s))','O(1)',8),
3615:entry('longest_palindromic_graph_path',[('n','int'),('edges','list[list[int]]'),('label','str')],'int',['graphs','bitmasking','dynamic programming'],['The undirected graph has at most 14 nodes.','A path may start anywhere but may visit each node at most once.','Maximize path length whose node labels form a palindrome.'],[([3,[[0,1],[1,2]],'aba'],'The full path spells aba.'),([3,[[0,1],[0,2]],'abc'],'No two-node or longer path is palindromic, so the answer is one.')],L_CASES,PALINDROME,[PALINDROME.replace("for u,v in edges:\n        if label[u]==label[v]:","for u,v in []:\n        if label[u]==label[v]:"),PALINDROME.replace('label[outer_left]!=label[outer_right]','label[outer_left]==label[outer_right]')],['Omits even-length palindromes centered on an edge.','Extends endpoints with different labels instead of equal labels.'],palindrome_oracle,random_palindrome,lesson('A palindrome can be grown symmetrically from one center node or one equal-label center edge.','Track used-node masks and the two current endpoints.','Extend both endpoints to distinct unused neighbors having equal labels.','Every simple palindromic path reduces to a valid shorter center state after removing its matching endpoint pair.'),'O(2^n*n^4)','O(2^n*n^2)',8),
}
