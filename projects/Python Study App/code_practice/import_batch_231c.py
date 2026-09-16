"""Trapezoids, dynamic popcount queries, subsequences, and prime teleports."""
from collections import Counter, defaultdict, deque
from itertools import combinations
from math import gcd
from .import_batch_055 import entry

def horizontal_oracle(args):
    points=args[0];answer=0
    for chosen in combinations(points,4):
        counts=Counter(y for x,y in chosen)
        answer+=sorted(counts.values())==[2,2]
    return answer%(10**9+7)

def random_horizontal(rng):
    points=set()
    while len(points)<rng.randint(4,9):points.add((rng.randint(-4,4),rng.randint(-3,3)))
    return [[list(point) for point in points]]

def popdepth(x):
    result=0
    while x!=1:x=x.bit_count();result+=1
    return result

def query_oracle(args):
    nums,queries=args;nums=nums[:];answer=[]
    for query in queries:
        if query[0]==1:answer.append(sum(popdepth(nums[i])==query[3] for i in range(query[1],query[2]+1)))
        else:nums[query[1]]=query[2]
    return answer

def random_queries(rng):
    n=rng.randint(1,12);nums=[rng.randint(1,1000) for _ in range(n)];queries=[]
    for _ in range(rng.randint(1,18)):
        if rng.randrange(3):
            left=rng.randrange(n);right=rng.randrange(left,n);queries.append([1,left,right,rng.randint(0,5)])
        else:queries.append([2,rng.randrange(n),rng.randint(1,1000)])
    return [nums,queries]

def hull(points):
    points=sorted(points)
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[]
    for p in points:
        while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0:lower.pop()
        lower.append(p)
    upper=[]
    for p in reversed(points):
        while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0:upper.pop()
        upper.append(p)
    return lower[:-1]+upper[:-1]

def trapezoid_oracle(args):
    answer=0
    for chosen in combinations(args[0],4):
        polygon=hull(chosen)
        if len(polygon)!=4:continue
        directions=[(polygon[(i+1)%4][0]-polygon[i][0],polygon[(i+1)%4][1]-polygon[i][1]) for i in range(4)]
        parallel=lambda a,b:a[0]*b[1]==a[1]*b[0]
        answer+=parallel(directions[0],directions[2]) or parallel(directions[1],directions[3])
    return answer

def random_trapezoid(rng):
    points=set()
    while len(points)<rng.randint(4,8):points.add((rng.randint(-5,5),rng.randint(-5,5)))
    return [[list(point) for point in points]]

def count_lct(s):
    l=lc=answer=0
    for char in s:
        if char=='L':l+=1
        elif char=='C':lc+=l
        elif char=='T':answer+=lc
    return answer

def subsequence_oracle(args):
    s=args[0];return max([count_lct(s)]+[count_lct(s[:i]+char+s[i:]) for i in range(len(s)+1) for char in 'LCT'])

def random_subsequence(rng):return [''.join(rng.choice('LCTX') for _ in range(rng.randint(1,14)))]

def prime(value):return value>=2 and all(value%d for d in range(2,int(value**0.5)+1))

def jumps_oracle(args):
    nums=args[0];n=len(nums);distance=[-1]*n;distance[0]=0;queue=deque([0])
    while queue:
        i=queue.popleft()
        if i==n-1:return distance[i]
        targets=[j for j in (i-1,i+1) if 0<=j<n]
        if prime(nums[i]):targets.extend(j for j,value in enumerate(nums) if value%nums[i]==0)
        for j in targets:
            if distance[j]<0:distance[j]=distance[i]+1;queue.append(j)

def random_jumps(rng):return [[rng.randint(1,50) for _ in range(rng.randint(1,20))]]

HORIZONTAL='''def count_horizontal_trapezoids(points):
    from collections import Counter
    mod=10**9+7;total_pairs=0;answer=0
    for count in Counter(y for x,y in points).values():
        pairs=count*(count-1)//2
        answer=(answer+total_pairs*pairs)%mod;total_pairs+=pairs
    return answer
'''

QUERIES='''def popcount_depth_queries(nums,queries):
    def depth(value):
        result=0
        while value!=1:value=value.bit_count();result+=1
        return result
    n=len(nums);trees=[[0]*(n+1) for _ in range(6)]
    def add(level,index,delta):
        index+=1
        while index<=n:trees[level][index]+=delta;index+=index&-index
    def prefix(level,index):
        total=0
        while index>0:total+=trees[level][index];index-=index&-index
        return total
    levels=[depth(value) for value in nums]
    for index,level in enumerate(levels):add(level,index,1)
    answer=[]
    for query in queries:
        if query[0]==1:
            _,left,right,level=query;answer.append(prefix(level,right+1)-prefix(level,left))
        else:
            _,index,value=query;add(levels[index],index,-1);levels[index]=depth(value);add(levels[index],index,1)
    return answer
'''

TRAPEZOIDS='''def count_all_trapezoids(points):
    from collections import defaultdict
    from math import gcd
    by_slope=defaultdict(lambda:defaultdict(int));by_midpoint=defaultdict(lambda:defaultdict(int))
    for i in range(len(points)):
        x1,y1=points[i]
        for j in range(i):
            x2,y2=points[j];dx=x2-x1;dy=y2-y1;factor=gcd(abs(dx),abs(dy));dx//=factor;dy//=factor
            if dx<0 or (dx==0 and dy<0):dx=-dx;dy=-dy
            slope=(dx,dy);line=dy*x1-dx*y1
            by_slope[slope][line]+=1;by_midpoint[(x1+x2,y1+y2)][slope]+=1
    answer=0
    for lines in by_slope.values():
        prior=0
        for count in lines.values():answer+=prior*count;prior+=count
    for slopes in by_midpoint.values():
        prior=0
        for count in slopes.values():answer-=prior*count;prior+=count
    return answer
'''

SUBSEQUENCES='''def maximum_lct_subsequences(s):
    left=0;right=s.count('T');existing=0;insert_c=0
    for char in s:
        if char=='T':right-=1
        if char=='C':existing+=left*right
        if char=='L':left+=1
        insert_c=max(insert_c,left*right)
    pairs_lc=l=0;pairs_ct=t=0
    for char in s:
        if char=='L':l+=1
        elif char=='C':pairs_lc+=l
    for char in reversed(s):
        if char=='T':t+=1
        elif char=='C':pairs_ct+=t
    return existing+max(pairs_lc,pairs_ct,insert_c)
'''

JUMPS='''def minimum_prime_teleport_jumps(nums):
    from collections import defaultdict,deque
    n=len(nums);maximum=max(nums);smallest=list(range(maximum+1))
    for p in range(2,int(maximum**0.5)+1):
        if smallest[p]==p:
            for value in range(p*p,maximum+1,p):
                if smallest[value]==value:smallest[value]=p
    prime_values={value for value in nums if value>=2 and smallest[value]==value};buckets=defaultdict(list)
    for index,value in enumerate(nums):
        remaining=value
        while remaining>1:
            factor=smallest[remaining]
            if factor in prime_values:buckets[factor].append(index)
            while remaining%factor==0:remaining//=factor
    distance=[-1]*n;distance[0]=0;queue=deque([0])
    while queue:
        index=queue.popleft()
        if index==n-1:return distance[index]
        targets=[]
        if index:targets.append(index-1)
        if index+1<n:targets.append(index+1)
        if nums[index] in prime_values:targets+=buckets.pop(nums[index],[])
        for nxt in targets:
            if distance[nxt]<0:distance[nxt]=distance[index]+1;queue.append(nxt)
'''

def lesson(a,b,c,d):return [a,b,c,d]

H_CASES=[[p] for p in ([[0,0],[1,0],[0,1],[3,1]],[[0,0],[1,1],[2,2],[3,3]],[[0,0],[1,0],[2,0],[0,2],[1,2],[2,2]],[[0,0],[2,0],[1,1],[3,1]],[[0,0],[1,0],[2,0],[3,1]],[[1,1],[2,1],[3,2],[4,2],[5,2]],[[0,-1],[1,-1],[0,3],[1,3]],[[0,0],[1,0],[2,1],[3,1],[4,2],[5,2]],[[1,0],[2,0],[3,0],[4,1],[5,1],[6,2]],[[0,0],[1,0],[2,0],[3,0]],[[0,0],[1,1],[2,0],[3,1]],[[0,0],[1,0],[2,0],[0,1],[1,1],[0,2],[1,2]])]
Q_CASES=[[a,q] for a,q in (([1],[[1,0,0,0]]),([2],[[1,0,0,1]]),([7],[[1,0,0,3]]),([2,4],[[2,1,1],[1,0,1,0]]),([3,5,6],[[1,0,2,2],[2,1,4],[1,1,2,1]]),([1,2],[[2,0,3],[1,0,0,2]]),([15,16,31],[[1,0,2,2]]),([8,7,6,5],[[1,1,3,2],[2,2,1],[1,0,3,0]]),([2,3,4,5],[[1,0,3,1]]),([63,64],[[1,0,1,3]]),([1,1,1],[[1,0,2,0],[2,1,2],[1,0,2,1]]),([10,11,12],[[2,0,1],[1,0,2,0]]))]
T_CASES=[[p] for p in ([[0,0],[1,0],[0,1],[3,1]],[[0,0],[1,0],[1,1],[0,1]],[[0,0],[2,0],[3,1],[1,1]],[[0,0],[1,1],[2,0],[1,-1]],[[0,0],[1,0],[2,1],[3,1]],[[0,0],[2,0],[1,2],[3,2],[2,4]],[[0,0],[1,2],[3,3],[2,1]],[[0,0],[0,2],[2,0],[2,2],[1,3]],[[0,0],[2,1],[4,2],[1,3]],[[0,0],[1,0],[2,0],[3,0]],[[0,0],[1,1],[2,2],[0,2],[2,0]],[[0,0],[3,0],[1,1],[4,1],[2,2]])]
S_CASES=[[s] for s in ('L','C','T','LCT','LCCCT','LLTT','CLT','TCL','LCLC','CTCT','XYZ','LLCCTT')]
J_CASES=[[a] for a in ([1],[1,1],[2,4],[4,6,5,9],[2,3,4,7,15],[3,6,9],[5,10,15,20],[7,1,14],[6,2,12,18],[11,22,33,44],[4,9,25,49],[2,1,1,1,6])]

BATCH={
3623:entry('count_horizontal_trapezoids',[('points','list[list[int]]')],'int',['geometry','combinatorics','hash maps'],['Four to 100,000 distinct points.','Choose two horizontal point-pairs on different y-levels.','Return the number modulo 1,000,000,007.'],[([[[1,0],[2,0],[3,0],[2,2],[3,2]]],'Three lower pairs combine with the one upper pair.'),([[[0,0],[1,0],[0,1],[2,1]]],'One pair exists on each of two levels, giving one trapezoid.')],H_CASES,HORIZONTAL,[HORIZONTAL.replace('total_pairs*pairs','total_pairs+pairs'),HORIZONTAL.replace('Counter(y for x,y in points)','Counter(x for x,y in points)')],['Adds pair counts instead of multiplying choices across levels.','Groups vertical lines by x-coordinate rather than horizontal lines by y-coordinate.'],horizontal_oracle,random_horizontal,lesson('Any two distinct horizontal segments on different y-levels form one convex horizontal trapezoid.','Count point pairs per y-level, then combine each level with all prior levels.','For level size c use C(c,2), add prior_pairs*this_pairs, and update prior_pairs.','Every trapezoid has a unique pair of horizontal supporting levels and one segment choice on each.'),'O(n)','O(distinct y)',5),
3624:entry('popcount_depth_queries',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['fenwick trees','bit manipulation','range queries'],['Up to 100,000 positive values and queries.','Type one counts a requested depth in an inclusive index range; type two updates one value.','Depth is between zero and five.'],[([[2,4],[[1,0,1,1],[2,1,1],[1,0,1,0]]],'The two initial powers of two have depth one; after updating, one value has depth zero.'),([[3,5,6],[[1,0,2,2],[2,1,4],[1,1,2,1],[1,0,1,0]]],'The query answers are three, one, and zero.')],Q_CASES,QUERIES,[QUERIES.replace('prefix(level,right+1)-prefix(level,left)','prefix(level,right)-prefix(level,left)'),QUERIES.replace('levels[index]=depth(value);add(levels[index],index,1)','levels[index]=depth(value)')],['Treats the inclusive right endpoint as exclusive.','Removes the old category during an update but never inserts the new category.'],query_oracle,random_queries,lesson('Only six depth categories exist, so maintain one frequency structure per category.','Use six Fenwick trees for range counts and point updates.','Remove the old depth, compute and add the new depth, and answer with prefix differences.','Each tree exactly tracks indices in one category, so their range sums remain correct after every update.'),'O((n+q) log n)','O(6n)',8),
3625:entry('count_all_trapezoids',[('points','list[list[int]]')],'int',['geometry','hash maps','combinatorics'],['Four to 500 distinct integer points.','A valid convex quadrilateral has at least one pair of parallel opposite sides.','Count each set of four points once.'],[([[[-3,2],[3,0],[2,3],[3,2],[2,-3]]],'Exactly two four-point subsets form trapezoids.'),([[[0,0],[1,0],[0,1],[2,1]]],'The two horizontal sides form one trapezoid.')],T_CASES,TRAPEZOIDS,[TRAPEZOIDS.replace('answer-=prior*count','answer+=prior*count'),TRAPEZOIDS.replace('line=dy*x1-dx*y1','line=dy*x1+dx*y1')],['Adds parallelograms again instead of removing their double count.','Uses an invalid line invariant and merges or separates parallel supporting lines incorrectly.'],trapezoid_oracle,random_trapezoid,lesson('Pairs of segments on distinct parallel lines define trapezoids, but parallelograms appear once for each parallel-side direction.','Group point pairs by exact normalized slope and supporting line; then subtract nondegenerate equal-midpoint diagonal pairs.','Combine segment counts across lines per slope, and subtract midpoint groups whose diagonal slopes differ.','Every trapezoid contributes one parallel-side pairing; parallelograms contribute two and the exact midpoint correction removes the extra one.'),'O(n^2)','O(n^2)',8),
3628:entry('maximum_lct_subsequences',[('s','str')],'int',['strings','subsequences','dynamic programming'],['One to 100,000 uppercase letters.','Insert at most one uppercase letter anywhere.','Maximize the number of LCT subsequences.'],[(['LMCT'],'Inserting L at the beginning doubles the single existing subsequence.'),(['LCCT'],'Inserting L at the beginning produces four subsequences.')],S_CASES,SUBSEQUENCES,[SUBSEQUENCES.replace('max(pairs_lc,pairs_ct,insert_c)','max(pairs_lc,pairs_ct)'),SUBSEQUENCES.replace('existing+=left*right','existing+=0')],['Never considers inserting C between existing L and T characters.','Counts only subsequences using the inserted letter and forgets all preexisting LCT subsequences.'],subsequence_oracle,random_subsequence,lesson('Only inserting L, C, or T can help; each contributes an existing CT pair, an L-before/T-after product, or an LC pair.','Count existing LCT subsequences and the best marginal contribution of one insertion.','Track L left and T right for C insertion, plus total LC and CT pairs for endpoint insertions.','Every new LCT uses the inserted character in exactly one of these three roles, so the best marginal count is complete.'),'O(n)','O(1)',6),
3629:entry('minimum_prime_teleport_jumps',[('nums','list[int]')],'int',['graphs','breadth first search','number theory'],['One to 100,000 values between one and one million.','Adjacent indices are always reachable in one jump.','From a prime value p, teleport to any other index whose value is divisible by p.'],[([[1,2,4,6]],'Step to prime two, then teleport to the final multiple of two.'),([[2,3,4,7,9]],'Step to prime three, then teleport to value nine.')],J_CASES,JUMPS,[JUMPS.replace('if nums[index] in prime_values','if smallest[nums[index]] in prime_values').replace('buckets.pop(nums[index],[])','buckets.pop(smallest[nums[index]],[])'),JUMPS.replace('targets+=buckets.pop(nums[index],[])','targets+=[]')],['Allows composite values to teleport using a prime factor.','Disables prime teleportation and permits only adjacent steps.'],jumps_oracle,random_jumps,lesson('Array indices form a graph with adjacent edges plus one shared teleport bucket for each prime value present.','Factor values to build divisibility buckets, then run BFS and consume each prime bucket once.','Visit adjacent indices; when the current value is prime, enqueue its bucket and delete that bucket.','BFS gives minimum jumps, and clearing is safe because the first visit already uses that bucket at the smallest possible distance.'),'O(max(nums) log log max + total factors + n)','O(max(nums)+n)',6),
}
