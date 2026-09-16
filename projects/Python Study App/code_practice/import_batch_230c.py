"""Unique segments, removal LCPs, XOR partitions, stable trees, and waiting grids."""
from itertools import combinations
from .import_batch_055 import entry

def partition_oracle(args):
    s=args[0];seen=set();out=[];start=0
    while start<len(s):
        end=start+1
        while end<=len(s) and s[start:end] in seen:end+=1
        if end>len(s):break
        part=s[start:end];out.append(part);seen.add(part);start=end
    return out

def random_partition(rng):return [''.join(rng.choice('abcd') for _ in range(rng.randint(1,30)))]

def lcp(a,b):
    i=0
    while i<min(len(a),len(b)) and a[i]==b[i]:i+=1
    return i

def removal_oracle(args):
    words=args[0];out=[]
    for removed in range(len(words)):
        rest=words[:removed]+words[removed+1:]
        out.append(max((lcp(rest[i],rest[i+1]) for i in range(len(rest)-1)),default=0))
    return out

def random_removal(rng):return [[''.join(rng.choice('abcd') for _ in range(rng.randint(1,8))) for _ in range(rng.randint(1,9))]]

def xor_oracle(args):
    nums,k=args;n=len(nums);answer=float('inf')
    for cuts in combinations(range(1,n),k-1):
        start=0;worst=0
        for end in (*cuts,n):
            value=0
            for number in nums[start:end]:value^=number
            worst=max(worst,value);start=end
        answer=min(answer,worst)
    return answer

def random_xor(rng):
    n=rng.randint(1,9)
    return [[rng.randint(1,63) for _ in range(n)],rng.randint(1,n)]

def stability_oracle(args):
    n,edges,k=args;must={i for i,e in enumerate(edges) if e[3]};answer=-1
    for chosen_tuple in combinations(range(len(edges)),n-1):
        chosen=set(chosen_tuple)
        if not must<=chosen:continue
        parent=list(range(n))
        def find(x):
            while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
            return x
        valid=True
        for index in chosen:
            a,b=map(find,edges[index][:2])
            if a==b:valid=False;break
            parent[a]=b
        if not valid or len({find(i) for i in range(n)})>1:continue
        optional=[i for i in chosen if not edges[i][3]]
        for count in range(min(k,len(optional))+1):
            for upgraded_tuple in combinations(optional,count):
                upgraded=set(upgraded_tuple)
                answer=max(answer,min(edges[i][2]*(2 if i in upgraded else 1) for i in chosen))
    return answer

def random_stability(rng):
    n=rng.randint(2,5);pairs=list(combinations(range(n),2));rng.shuffle(pairs)
    edges=[[u,v,rng.randint(1,12),int(rng.randrange(6)==0)] for u,v in pairs[:rng.randint(1,min(8,len(pairs)))]]
    return [n,edges,rng.randint(0,n)]

def waiting_oracle(args):
    m,n,wait=args;answer=10**30
    def visit(row,column,total):
        nonlocal answer
        if total>=answer:return
        if (row,column)==(m-1,n-1):answer=total;return
        if (row,column)!=(0,0):total+=wait[row][column]
        if row+1<m:visit(row+1,column,total+(row+2)*(column+1))
        if column+1<n:visit(row,column+1,total+(row+1)*(column+2))
    visit(0,0,1);return answer

def random_waiting(rng):
    m=rng.randint(1,5);n=rng.randint(1,5)
    if m*n==1:n=2
    return [m,n,[[rng.randint(0,12) for _ in range(n)] for _ in range(m)]]

PARTITION='''def partition_unique_segments(s):
    seen=set();segments=[];current=''
    for char in s:
        current+=char
        if current not in seen:
            seen.add(current);segments.append(current);current=''
    return segments
'''

REMOVAL='''def longest_adjacent_prefix_after_removals(words):
    def common(a,b):
        length=0
        while length<min(len(a),len(b)) and a[length]==b[length]:length+=1
        return length
    n=len(words)
    if n<=2:return [0]*n
    adjacent=[common(words[i],words[i+1]) for i in range(n-1)]
    prefix=[0]*n;suffix=[0]*n
    for i in range(n-1):prefix[i+1]=max(prefix[i],adjacent[i])
    for i in range(n-2,-1,-1):suffix[i]=max(suffix[i+1],adjacent[i])
    answer=[]
    for i in range(n):
        best=max(prefix[max(0,i-1)],suffix[min(n-1,i+1)])
        if 0<i<n-1:best=max(best,common(words[i-1],words[i+1]))
        answer.append(best)
    return answer
'''

XOR='''def minimize_maximum_partition_xor(nums,k):
    n=len(nums);prefix=[0]*(n+1)
    for i,value in enumerate(nums,1):prefix[i]=prefix[i-1]^value
    previous=[float('inf')]*(n+1);previous[0]=0
    for group in range(1,k+1):
        current=[float('inf')]*(n+1)
        for end in range(group,n+1):
            for cut in range(group-1,end):current[end]=min(current[end],max(previous[cut],prefix[end]^prefix[cut]))
        previous=current
    return previous[n]
'''

STABILITY='''def maximum_spanning_tree_stability(n,edges,k):
    class DSU:
        def __init__(self):self.parent=list(range(n));self.components=n
        def find(self,x):
            while self.parent[x]!=x:self.parent[x]=self.parent[self.parent[x]];x=self.parent[x]
            return x
        def union(self,a,b):
            a=self.find(a);b=self.find(b)
            if a==b:return False
            self.parent[a]=b;self.components-=1;return True
    required=DSU()
    for u,v,strength,must in edges:
        if must and not required.union(u,v):return -1
    connected=DSU()
    for u,v,strength,must in edges:connected.union(u,v)
    if connected.components>1:return -1
    def feasible(limit):
        dsu=DSU()
        for u,v,strength,must in edges:
            if must:
                if strength<limit:return False
                dsu.union(u,v)
        for u,v,strength,must in edges:
            if not must and strength>=limit:dsu.union(u,v)
        upgrades=0
        for u,v,strength,must in edges:
            if not must and strength<limit<=2*strength and dsu.union(u,v):upgrades+=1
        return dsu.components==1 and upgrades<=k
    low,high=1,max(2*strength if not must else strength for u,v,strength,must in edges)
    while low<high:
        middle=(low+high+1)//2
        if feasible(middle):low=middle
        else:high=middle-1
    return low
'''

WAITING='''def minimum_waiting_grid_cost(m,n,waitCost):
    infinity=10**30;cost=[[infinity]*n for _ in range(m)];cost[0][0]=1
    for row in range(m):
        for column in range(n):
            if row==0 and column==0:continue
            entry=(row+1)*(column+1);best=infinity
            if row:
                extra=0 if (row-1,column)==(0,0) else waitCost[row-1][column]
                best=min(best,cost[row-1][column]+extra+entry)
            if column:
                extra=0 if (row,column-1)==(0,0) else waitCost[row][column-1]
                best=min(best,cost[row][column-1]+extra+entry)
            cost[row][column]=best
    return cost[-1][-1]
'''

def lesson(a,b,c,d):return [a,b,c,d]

P_CASES=[[s] for s in ('a','aa','ab','aaa','abcd','abab','abcabc','zzzzzz','aabaaa','banana','mississippi','abcddcba')]
L_CASES=[[x] for x in (['a'],['a','a'],['a','b'],['ab','ac','ad'],['aa','ab','zz','za'],['same']*3,['prefix','presto','prevent','x'],['x','abc','abd','abe','y'],['a','aa','aaa','aaaa'],['cat','car','cart','dog'],['zoo','zoom','z','zone'],['ab','cd','ab','ac'])]
X_CASES=[[a,k] for a,k in (([1],1),([1,2],1),([1,2],2),([7,7,7],2),([4,1,6,2],2),([8,1,2,12],3),([5]*4,2),([3,10,5,25,2],3),([1,2,4,8,16],4),([9,8,7,6,5],1),([6,1,6,1,6,1],3),([31,1,15,2],2))]
S_CASES=[[n,e,k] for n,e,k in ((2,[[0,1,5,0]],0),(2,[[0,1,5,0]],1),(3,[[0,1,1,1],[1,2,1,1],[2,0,1,1]],0),(4,[[0,1,4,1],[1,2,3,0],[2,3,2,0],[0,3,1,0]],2),(4,[[0,1,2,0],[2,3,2,0]],2),(4,[[0,1,5,1],[2,3,6,1],[1,2,2,0]],1),(5,[[0,1,8,0],[1,2,4,0],[2,3,3,0],[3,4,2,0]],2),(3,[[0,1,10,1],[1,2,1,0],[0,2,4,0]],1),(4,[[0,1,7,0],[1,2,6,0],[2,3,5,0],[0,3,4,0],[0,2,3,0]],0),(4,[[0,1,1,1],[1,2,2,1],[2,3,3,1]],3),(3,[[0,1,2,0],[1,2,2,0],[0,2,2,0]],1),(5,[[0,1,3,1],[1,2,5,0],[1,3,2,0],[3,4,6,0],[2,4,1,0]],2))]
W_CASES=[[m,n,w] for m,n,w in ((2,1,[[3],[4]]),(2,3,[[6,1,4],[3,2,5]]),(3,2,[[1,9],[2,3],[4,5]]),(1,5,[[9,1,7,2,8]]),(5,1,[[9],[1],[7],[2],[8]]),(3,3,[[0]*3 for _ in range(3)]),(3,3,[[5,1,9],[2,8,3],[4,7,6]]),(2,4,[[1,10,1,10],[10,1,10,1]]),(4,2,[[2,8],[1,7],[3,6],[4,5]]),(4,4,[[1,2,3,4],[4,3,2,1],[5,6,7,8],[8,7,6,5]]),(1,10,[list(range(10))]),(5,3,[[r+c for c in range(3)] for r in range(5)]))]

BATCH={
3597:entry('partition_unique_segments',[('s','str')],'list[str]',['strings','hash sets','simulation'],['One to 100,000 lowercase letters.','Extend each segment until its value has not appeared as a completed segment.','Return completed segments in order.'],[(['abbccccd'],'Repeated candidates are extended until each completed segment is new.'),(['aaaa'],'The segments are a and aa.')],P_CASES,PARTITION,[PARTITION.replace('current not in seen','current in seen'),PARTITION.replace('seen.add(current);','')],['Ends segments when already seen.','Never remembers completed segments.'],partition_oracle,random_partition,lesson('Track completed segment values.','Extend a buffer until it is absent from a set.','Record an unseen buffer and reset it.','This makes every segment end at the earliest required position.'),'O(n^2) worst case','O(n)',5),
3598:entry('longest_adjacent_prefix_after_removals',[('words','list[str]')],'list[int]',['arrays','strings','prefix maxima'],['At most 100,000 total characters.','For each removed index, inspect adjacent pairs in the remaining order.','Return zero when no positive adjacent prefix exists.'],[([['jump','run','run','jump','run']],'Removing the first word preserves a run/run prefix of length three.'),([['dog','racer','car']],'No removal creates a positive adjacent prefix.')],L_CASES,REMOVAL,[REMOVAL.replace('suffix[min(n-1,i+1)]','suffix[min(n-1,i)]'),REMOVAL.replace("if 0<i<n-1:best=max(best,common(words[i-1],words[i+1]))",'')],['Retains a pair touching the removed word.','Omits the new bridge pair.'],removal_oracle,random_removal,lesson('Only two old pairs disappear and one bridge may appear.','Precompute adjacent LCPs and range maxima.','Combine unaffected prefix, suffix, and bridge candidates.','These are exactly all adjacent pairs after removal.'),'O(total characters)','O(n)',5),
3599:entry('minimize_maximum_partition_xor',[('nums','list[int]'),('k','int')],'int',['dynamic programming','bit manipulation','prefix xor'],['One to 250 positive integers.','Split into exactly k nonempty contiguous subarrays.','Minimize the largest segment XOR.'],[([[1,2,3],2],'The split [1] and [2,3] has maximum XOR one.'),([[2,3,3,2],3],'The split [2], [3,3], [2] has maximum XOR two.')],X_CASES,XOR,[XOR.replace('max(previous[cut],prefix[end]^prefix[cut])','min(previous[cut],prefix[end]^prefix[cut])'),XOR.replace('prefix[end]^prefix[cut]','prefix[end]|prefix[cut]')],['Tracks the smaller value instead of the partition maximum.','Uses OR instead of XOR.'],xor_oracle,random_xor,lesson('Prefix XOR evaluates a segment in constant time.','Use DP by prefix length and group count.','Try every final cut and minimize the resulting maximum.','Every partition has exactly one final cut considered by the recurrence.'),'O(k*n^2)','O(n)',6),
3600:entry('maximum_spanning_tree_stability',[('n','int'),('edges','list[list[int]]'),('k','int')],'int',['graphs','union find','binary search'],['Up to 100,000 nodes and edges.','Mandatory edges must appear and cannot be upgraded.','Optional edges may be doubled once using at most k upgrades.'],[([3,[[0,1,2,1],[1,2,3,0]],1],'The mandatory strength-two edge caps stability at two.'),([3,[[0,1,4,0],[1,2,3,0],[0,2,1,0]],2],'Upgrading strengths four and three yields stability six.')],S_CASES,STABILITY,[STABILITY.replace('if must and not required.union(u,v):return -1','if must:required.union(u,v)'),STABILITY.replace('if strength<limit:return False','if False:return False')],['Accepts mandatory cycles.','Ignores that an unupgradable mandatory edge caps the stability.'],stability_oracle,random_stability,lesson('Threshold feasibility separates required, free, and upgraded edges.','Binary search stability with union-find.','Add mandatory edges, then strong free edges, then qualifying upgraded edges.','The predicate is monotone and free-first minimizes upgrades.'),'O(E log S)','O(n)',8),
3603:entry('minimum_waiting_grid_cost',[('m','int'),('n','int'),('waitCost','list[list[int]]')],'int',['dynamic programming','matrices'],['Two to 100,000 grid cells.','Move only right or down.','Before each move except the first, pay one wait at the current cell.'],[([1,2,[[1,2]]],'The first move costs two, producing total three.'),([2,2,[[3,5],[2,4]]],'Down, wait, right costs 1+2+2+4=9.')],W_CASES,WAITING,[WAITING.replace("extra=0 if (row-1,column)==(0,0) else waitCost[row-1][column]","extra=waitCost[row-1][column]").replace("extra=0 if (row,column-1)==(0,0) else waitCost[row][column-1]","extra=waitCost[row][column-1]"),WAITING.replace("else waitCost[row-1][column]","else 0").replace("else waitCost[row][column-1]","else 0")],['Charges a wait before the first move.','Never charges intermediate waits.'],waiting_oracle,random_waiting,lesson('Every move after the first has one predecessor wait.','Use right/down grid DP.','Add predecessor wait plus destination entry cost.','Every monotone route is represented by its final predecessor.'),'O(m*n)','O(m*n)',5),
}
