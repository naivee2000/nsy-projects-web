"""Centered sums, Caesar pairs, incremented AND, repair thresholds, and towers."""
from collections import Counter,deque
from itertools import combinations,product
from .import_batch_055 import entry


def centered_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        total=0;values=set()
        for right in range(left,len(nums)):
            total+=nums[right];values.add(nums[right]);answer+=total in values
    return answer
def random_centered(rng):return [[rng.randint(-10,10) for _ in range(rng.randint(1,18))]]

def caesar_key(word):return tuple((ord(char)-ord(word[0]))%26 for char in word)
def caesar_oracle(args):
    keys=[caesar_key(word) for word in args[0]]
    return sum(keys[i]==keys[j] for i in range(len(keys)) for j in range(i+1,len(keys)))
def random_caesar(rng):
    length=rng.randint(1,7);return [[''.join(rng.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length)) for _ in range(rng.randint(1,15))]]

def and_oracle(args):
    nums,k,m=args;answer=0
    for indices in combinations(range(len(nums)),m):
        for increases in product(range(k+1),repeat=m):
            if sum(increases)<=k:
                value=nums[indices[0]]+increases[0]
                for position in range(1,m):value&=nums[indices[position]]+increases[position]
                answer=max(answer,value)
    return answer
def random_and(rng):
    n=rng.randint(1,6);return [[rng.randint(1,20) for _ in range(n)],rng.randint(1,7),rng.randint(1,n)]

def repair_oracle(args):
    n,edges,k=args
    for money in sorted({edge[2] for edge in edges}):
        graph=[[] for _ in range(n)]
        for a,b,cost in edges:
            if cost<=money:graph[a].append(b);graph[b].append(a)
        distance=[-1]*n;distance[0]=0;queue=deque([0])
        while queue:
            node=queue.popleft()
            for nxt in graph[node]:
                if distance[nxt]<0:distance[nxt]=distance[node]+1;queue.append(nxt)
        if 0<=distance[-1]<=k:return money
    return -1
def random_repair(rng):
    n=rng.randint(2,8);pairs=list(combinations(range(n),2));rng.shuffle(pairs);count=rng.randint(1,min(len(pairs),12))
    return [n,[[a,b,rng.randint(1,30)] for a,b in pairs[:count]],rng.randint(1,n)]

def tower_oracle(args):
    towers,center,radius=args;reachable=[item for item in towers if abs(item[0]-center[0])+abs(item[1]-center[1])<=radius]
    return [-1,-1] if not reachable else min(reachable,key=lambda item:(-item[2],item[0],item[1]))[:2]
def random_tower(rng):
    return [[[rng.randint(0,20),rng.randint(0,20),rng.randint(0,20)] for _ in range(rng.randint(1,15))],[rng.randint(0,20),rng.randint(0,20)],rng.randint(0,20)]


CENTERED='''def count_centered_subarrays(nums):
    answer=0
    for left in range(len(nums)):
        total=0;values=set()
        for right in range(left,len(nums)):
            total+=nums[right];values.add(nums[right])
            if total in values:answer+=1
    return answer
'''

CAESAR='''def count_caesar_cipher_pairs(words):
    counts={};answer=0
    for word in words:
        key=tuple((ord(char)-ord(word[0]))%26 for char in word)
        answer+=counts.get(key,0);counts[key]=counts.get(key,0)+1
    return answer
'''

AND='''def maximum_and_after_increments(nums,k,m):
    answer=0;limit=(max(nums)+k).bit_length()
    for bit in range(limit-1,-1,-1):
        target=answer|(1<<bit);costs=[]
        for value in nums:
            missing=(target&~value).bit_length();mask=(1<<missing)-1
            costs.append((target&mask)-(value&mask))
        costs.sort()
        if sum(costs[:m])<=k:answer=target
    return answer
'''

AND_WRONG='''def maximum_and_after_increments(nums,k,m):
    values=sorted(nums,reverse=True)[:m]
    answer=values[0]
    for value in values[1:]:answer&=value
    return answer+k
'''

REPAIR='''def minimum_graph_repair_money(n,edges,k):
    from collections import deque
    costs=sorted({cost for _,_,cost in edges})
    def possible(money):
        graph=[[] for _ in range(n)]
        for a,b,cost in edges:
            if cost<=money:graph[a].append(b);graph[b].append(a)
        distance=[-1]*n;distance[0]=0;queue=deque([0])
        while queue:
            node=queue.popleft()
            if distance[node]==k:continue
            for nxt in graph[node]:
                if distance[nxt]<0:distance[nxt]=distance[node]+1;queue.append(nxt)
        return 0<=distance[-1]<=k
    left=0;right=len(costs)
    while left<right:
        middle=(left+right)//2
        if possible(costs[middle]):right=middle
        else:left=middle+1
    return -1 if left==len(costs) else costs[left]
'''

REPAIR_WRONG='''def minimum_graph_repair_money(n,edges,k):
    from heapq import heappop,heappush
    graph=[[] for _ in range(n)]
    for a,b,cost in edges:graph[a].append((b,cost));graph[b].append((a,cost))
    distance=[10**30]*n;distance[0]=0;queue=[(0,0)]
    while queue:
        cost,node=heappop(queue)
        if cost!=distance[node]:continue
        for nxt,weight in graph[node]:
            if cost+weight<distance[nxt]:distance[nxt]=cost+weight;heappush(queue,(cost+weight,nxt))
    return -1 if distance[-1]==10**30 else distance[-1]
'''

TOWER='''def best_reachable_tower(towers,center,radius):
    best=None
    for x,y,quality in towers:
        if abs(x-center[0])+abs(y-center[1])<=radius:
            candidate=(quality,-x,-y)
            if best is None or candidate>best[0]:best=(candidate,[x,y])
    return [-1,-1] if best is None else best[1]
'''

def lesson(a,b,c,d):return [a,b,c,d]

C_CASES=[[[*v]] for v in ([-1,1,0],[2,-3],[5],[0,0],[-2,2],[1,2,-3],[3,-1,-2,0],[1,1,1],[-1,-1,2],[4,-2,1,-3],[0,1,0,-1],[5,-5,5,-5],[2,3,-1,-4,0],[-3,1,2,-2,2])]
S_CASES=[[[*w]] for w in (['fusion','layout'],['ab','aa','za','aa'],['a'],['a','z'],['abc','bcd','xyz'],['az','ba','yx'],['aaa','bbb','ccc'],['abc','abd'],['zab','abc','bcd'],['hello','ifmmp','uryyb'],['aa','aa','bb','bc'],['mnop','zabc','bcde'],['abcd','bcde','cdef','abce'],['xyz','yza','zab','xya'])]
A_CASES=[[a,k,m] for a,k,m in (([3,1,2],8,2),([1,2,8,4],7,3),([1,1],3,2),([5],1,1),([7,7],1,2),([1,2,3],1,2),([2,4,6],5,2),([8,1,8],4,3),([3,5,9,12],6,2),([1,1,1],7,3),([10,11,12],3,2),([15,2,7,8],5,3),([4,4,4,4],2,3),([1,6,10,14,18],7,4))]
R_CASES=[[n,e,k] for n,e,k in ((2,[[0,1,5]],1),(3,[[0,1,10],[1,2,10],[0,2,100]],1),(3,[[0,1,1]],1),(3,[[0,1,1],[1,2,2]],2),(4,[[0,1,3],[1,3,8],[0,2,5],[2,3,5]],2),(4,[[0,1,1],[1,2,1],[2,3,1]],2),(5,[[0,1,4],[1,4,9],[0,2,6],[2,3,6],[3,4,6]],3),(5,[[0,4,20],[0,1,2],[1,2,3],[2,3,4],[3,4,5]],1),(6,[[0,1,10],[1,5,12],[0,2,5],[2,3,6],[3,4,7],[4,5,5]],2),(3,[[0,1,7],[1,2,2],[0,2,9]],2),(4,[[0,1,100],[1,3,1],[0,2,2],[2,3,2]],2),(5,[[0,1,3],[1,2,3],[2,4,3],[0,3,10],[3,4,10]],2),(6,[[0,1,1],[1,2,2],[2,5,8],[0,3,4],[3,4,4],[4,5,4]],3),(7,[[0,1,5],[1,6,5],[0,2,2],[2,3,2],[3,4,2],[4,5,2],[5,6,2]],2))]
T_CASES=[[a,b,r] for a,b,r in (([[1,2,5],[2,1,7],[3,1,9]],[1,1],2),([[1,3,4],[2,2,4],[4,4,7]],[0,0],5),([[5,6,8],[0,3,5]],[1,2],1),([[0,0,1]],[0,0],0),([[1,1,5],[0,2,5]],[0,0],2),([[3,4,10],[1,1,1]],[0,0],5),([[3,4,10],[4,3,10]],[0,0],7),([[10,10,100],[1,1,2]],[0,0],3),([[0,5,3],[5,0,4]],[0,0],5),([[2,2,0],[3,3,1]],[2,2],0),([[1,2,8],[2,1,8],[0,3,8]],[0,0],3),([[20,20,5],[21,20,6]],[20,20],1),([[4,4,7],[2,6,7],[3,5,7]],[0,0],8),([[0,0,9],[100,100,10]],[50,50],100),([[7,1,3],[1,7,4],[4,4,5]],[4,4],6))]

BATCH={
3804:entry('count_centered_subarrays',[('nums','list[int]')],'int',['arrays','hash maps','enumeration'],['nums has length up to 500 and signed values.','A centered subarray has a sum equal to at least one value inside that same subarray.','Count all contiguous subarrays satisfying the equality.'],[([[-1,1,0]],'Three singletons, [1,0], and the whole array are centered, totaling five.'),([[2,-3]],'Only the two singleton subarrays have sums present within themselves.')],C_CASES,CENTERED,[CENTERED.replace('if total in values:answer+=1','if any(total>=value for value in values):answer+=1'),CENTERED.replace('if total in values:answer+=1','if total in set(nums):answer+=1')],['Uses an at-least comparison instead of requiring equality.','Accepts a sum found elsewhere in nums rather than inside the current subarray.'],centered_oracle,random_centered,lesson('Extend every possible left endpoint while maintaining both the running sum and values seen in the current interval.','After adding nums[right], test whether the running sum belongs to that interval’s set.','Increment the count exactly on membership, then continue extending right.','Every contiguous subarray has one unique pair of endpoints and is tested once against precisely its own values.'),'O(n²)','O(n)',5),
3805:entry('count_caesar_cipher_pairs',[('words','list[str]')],'int',['strings','hash maps','modular arithmetic'],['All words have the same length and total input size is at most 100,000.','One operation shifts every character of one chosen word forward cyclically by one.','Count index pairs whose words differ by one uniform cyclic shift.'],[([['fusion','layout']],'Shifting every character of fusion forward six times produces layout.'),([['ab','aa','za','aa']],'The pairs (ab,za) and the two identical aa words are similar.')],S_CASES,CAESAR,[CAESAR.replace('%26',''),CAESAR.replace("key=tuple((ord(char)-ord(word[0]))%26 for char in word)","key=word")],['Fails to wrap negative character differences modulo 26.','Counts only identical strings instead of uniform Caesar shifts.'],caesar_oracle,random_caesar,lesson('Uniform shifts preserve every character’s modular difference from the first character.','Normalize a word to the tuple (char-first) mod 26, whose first component is zero.','Count earlier identical keys while scanning words.','Two words have the same normalized differences exactly when one uniform cyclic shift transforms one into the other.'),'O(total characters)','O(total characters)',5),
3806:entry('maximum_and_after_increments',[('nums','list[int]'),('k','int'),('m','int')],'int',['arrays','bit manipulation','greedy'],['nums has up to 50,000 positive integers; choose exactly m positions.','At most k total operations may increment chosen or unchosen elements by one.','Maximize the bitwise AND of the m chosen final values.'],[([[3,1,2],8,2],'Raising three and two to six costs seven and yields AND six.'),([[1,2,8,4],7,3],'Raising one and two to four lets three chosen values share bit four.')],A_CASES,AND,[AND_WRONG,AND.replace('if sum(costs[:m])<=k','if max(costs[:m])<=k')],['Adds k to the original AND instead of allocating increments to satisfy target bits.','Treats k as a separate per-element budget rather than one shared operation budget.'],and_oracle,random_and,lesson('Build the answer from high bits to low bits, keeping a bit only when some m values can be raised to contain all chosen bits.','For a target mask and value x, only bits through the highest target bit missing from x need change before the next feasible number is reached.','Compute that increment cost per value, select the m smallest, and compare their sum with k.','High-to-low greedy is valid because feasibility is monotone under removing target bits, and accepted higher bits dominate every combination of lower bits.'),'O(Bn log n)','O(n)',8),
3807:entry('minimum_graph_repair_money',[('n','int'),('edges','list[list[int]]'),('k','int')],'int',['graphs','breadth-first search','binary search'],['n≤50,000, there are up to 100,000 weighted undirected edges, and k≥1.','Choosing money repairs every edge with cost at most that threshold.','Find the minimum threshold enabling a 0-to-(n-1) path of at most k edges, or -1.'],[([3,[[0,1,10],[1,2,10],[0,2,100]],1],'A one-edge route requires repairing the direct cost-100 edge.'),([3,[[0,1,1]],1],'Node two remains unreachable at every repair threshold.')],R_CASES,REPAIR,[REPAIR_WRONG,REPAIR.replace('if distance[node]==k:continue','').replace('return 0<=distance[-1]<=k','return distance[-1]>=0')],['Minimizes the sum of repair costs instead of the single global repair threshold.','Ignores the maximum number of path edges.'],repair_oracle,random_repair,lesson('For a fixed money threshold, usable edges form an unweighted graph.','Breadth-first search determines whether the destination is reachable within k edges.','This predicate is monotone as money increases, so binary-search the sorted distinct repair costs.','The first feasible threshold repairs exactly the edges needed by some allowed-length path; every smaller threshold was proved infeasible.'),'O((n+m) log m)','O(n+m)',5),
3809:entry('best_reachable_tower',[('towers','list[list[int]]'),('center','list[int]'),('radius','int')],'list[int]',['arrays','geometry'],['Each tower is [x,y,quality], with up to 100,000 towers.','Reachability uses Manhattan distance from center and an inclusive radius.','Choose maximum quality, breaking ties by lexicographically smallest [x,y], or return [-1,-1].'],[([[[1,2,5],[2,1,7],[3,1,9]],[1,1],2],'All are reachable; quality nine at [3,1] is largest.'),([[[1,3,4],[2,2,4],[4,4,7]],[0,0],5],'The first two tie on quality, so lexicographically smaller [1,3] wins.')],T_CASES,TOWER,[TOWER.replace('abs(x-center[0])+abs(y-center[1])<=radius','(x-center[0])**2+(y-center[1])**2<=radius**2'),TOWER.replace('candidate=(quality,-x,-y)','candidate=(quality,x,y)')],['Uses Euclidean rather than Manhattan reachability.','Breaks quality ties toward lexicographically largest coordinates.'],tower_oracle,random_tower,lesson('Filter towers by Manhattan distance |x-cx|+|y-cy|≤radius.','Rank each reachable tower by higher quality, then smaller x, then smaller y.','A tuple (quality,-x,-y) converts that ordering into one maximum comparison.','Every tower is inspected once, and the maintained best tuple exactly represents the stated priority order.'),'O(n)','O(1)',5),
}
