"""Interior value, substring decrement, chocolate rotations, dominance queries, and marked paths batch 177."""

from itertools import product

from .import_batch_055 import entry


def interior_oracle(args):
    nums=args[0];low=min(nums);high=max(nums)
    return next((value for value in nums if low<value<high),-1)


def random_interior(rng):return [[rng.randint(-20,20) for _ in range(rng.randint(2,30))]]


def smallest_oracle(args):
    s=args[0];answers=[]
    for left in range(len(s)):
        for right in range(left,len(s)):
            chars=list(s)
            for index in range(left,right+1):chars[index]='z' if chars[index]=='a' else chr(ord(chars[index])-1)
            answers.append(''.join(chars))
    return min(answers)


def random_smallest(rng):return [''.join(rng.choice('abcxyz') for _ in range(rng.randint(1,10)))]


def chocolates_oracle(args):
    nums,x=args;n=len(nums);answer=10**30
    for operations in range(n):
        total=operations*x
        for index in range(n):total+=min(nums[(index-shift)%n] for shift in range(operations+1))
        answer=min(answer,total)
    return answer


def random_chocolates(rng):return [[rng.randint(1,40) for _ in range(rng.randint(1,9))],rng.randint(0,30)]


def queries_oracle(args):
    nums1,nums2,queries=args
    return [max((first+second for first,second in zip(nums1,nums2) if first>=x and second>=y),default=-1) for x,y in queries]


def random_queries(rng):
    size=rng.randint(1,30);nums1=[rng.randint(1,60) for _ in range(size)];nums2=[rng.randint(1,60) for _ in range(size)]
    return [nums1,nums2,[[rng.randint(1,65),rng.randint(1,65)] for _ in range(rng.randint(1,25))]]


def marked_oracle(args):
    n,edges,s,marked=args;distances=[10**18]*n;distances[s]=0
    for _ in range(n-1):
        changed=False
        for left,right,weight in edges:
            if distances[left]+weight<distances[right]:distances[right]=distances[left]+weight;changed=True
        if not changed:break
    answer=min((distances[node] for node in marked),default=10**18)
    return -1 if answer==10**18 else answer


def random_marked(rng):
    n=rng.randint(1,9);edges=[]
    for left in range(n):
        for right in range(n):
            if left!=right and rng.random()<.22:edges.append([left,right,rng.randint(1,20)])
    nodes=list(range(n));rng.shuffle(nodes);return [n,edges,rng.randrange(n),nodes[:rng.randint(1,n)]]


def fuel_oracle(args):
    main,additional=args;distance=0;used=0
    while main:
        main-=1;used+=1;distance+=10
        if used==5 and additional:
            main+=1;additional-=1;used=0
    return distance


def random_fuel(rng):return [rng.randint(1,100),rng.randint(0,100)]


INTERIOR="""\
def neither_minimum_nor_maximum(nums):
    low=min(nums);high=max(nums)
    return next((value for value in nums if value!=low and value!=high),-1)
"""

SMALLEST="""\
def smallest_after_one_decrement(s):
    chars=list(s);start=0
    while start<len(chars) and chars[start]=='a':start+=1
    if start==len(chars):chars[-1]='z';return ''.join(chars)
    end=start
    while end<len(chars) and chars[end]!='a':chars[end]=chr(ord(chars[end])-1);end+=1
    return ''.join(chars)
"""

CHOCOLATES="""\
def minimum_chocolate_collection_cost(nums,x):
    n=len(nums);best=nums[:];answer=sum(best)
    for operations in range(1,n):
        for index in range(n):best[index]=min(best[index],nums[(index-operations)%n])
        answer=min(answer,sum(best)+operations*x)
    return answer
"""

QUERIES="""\
def maximum_sum_queries(nums1,nums2,queries):
    values=sorted(set(nums2+[y for _,y in queries]));size=len(values);tree=[-1]*(size+1)
    def update(index,value):
        index=size-index
        while index<=size:tree[index]=max(tree[index],value);index+=index&-index
    def lookup(index):
        index=size-index;answer=-1
        while index>0:answer=max(answer,tree[index]);index-=index&-index
        return answer
    from bisect import bisect_left
    points=sorted(zip(nums1,nums2),reverse=True);ordered=sorted(enumerate(queries),key=lambda item:item[1][0],reverse=True)
    answer=[-1]*len(queries);point=0
    for query_index,(x,y) in ordered:
        while point<len(points) and points[point][0]>=x:
            first,second=points[point];update(bisect_left(values,second),first+second);point+=1
        answer[query_index]=lookup(bisect_left(values,y))
    return answer
"""

MARKED="""\
def closest_marked_node(n,edges,s,marked):
    import heapq
    graph=[[] for _ in range(n)]
    for left,right,weight in edges:graph[left].append((right,weight))
    targets=set(marked);distances=[float('inf')]*n;distances[s]=0;heap=[(0,s)]
    while heap:
        distance,node=heapq.heappop(heap)
        if distance!=distances[node]:continue
        if node in targets:return distance
        for neighbor,weight in graph[node]:
            following=distance+weight
            if following<distances[neighbor]:distances[neighbor]=following;heapq.heappush(heap,(following,neighbor))
    return -1
"""

FUEL="""\
def total_truck_distance(mainTank,additionalTank):
    transfers=min((mainTank-1)//4,additionalTank)
    return (mainTank+transfers)*10
"""


BATCH={
2733:entry('neither_minimum_nor_maximum',[('nums','list[int]')],'int',['arrays','sorting'],
 ['Choose any array value that is neither the minimum nor the maximum value.','Duplicate copies of an extreme value are still extremes.','Return one qualifying value, or -1 when none exists.'],
 [([[3,2,1,4]],'Two is strictly between the minimum one and maximum four, so it is valid.'),([[1,2]],'Both values are extremes, so no qualifying value exists.')],
 [[a] for a in [[1,2],[2,1],[1,2,3],[3,2,1],[3,2,1,4],[1,1,2],[1,2,2],[2,2,2],[5,1,5,3],[0,-1,1],[-5,-2,-3],[10,20,10,15],[4,9,7,4,9],[8,6,7,5,3,0,9]]],
 INTERIOR,[INTERIOR.replace('value!=low and value!=high','value!=low or value!=high'),INTERIOR.replace("),-1)","),low)")],
 ['Uses OR, so every value qualifies because it differs from at least one extreme.','Returns the minimum instead of -1 when no interior value exists.'],interior_oracle,random_interior,
 ['Find the minimum and maximum values.','Scan for a value unequal to both extremes.','Return the first such value; if the scan ends, return -1.','A value is neither extreme exactly when both inequality tests hold, so the scan accepts only and all permitted answers.'],'O(n)','O(1)',3),
2734:entry('smallest_after_one_decrement',[('s','str')],'str',['strings','greedy'],
 ['Choose exactly one nonempty substring.','Replace each chosen character by its alphabet predecessor, with a wrapping to z.','Return the lexicographically smallest string obtainable.'],
 [(['cbabc'],'Decrement the initial cb to ba; stopping before a avoids wrapping it to z, producing baabc.'),(['aaaa'],'Every choice wraps selected a characters to z, so changing only the last gives aaaz.')],
 [[s] for s in ['a','b','z','aa','ab','ba','zz','aaaa','cbabc','leetcode','azaza','bbba','aabcc','xyzabc']],
 SMALLEST,[SMALLEST.replace("while start<len(chars) and chars[start]=='a'","while start<len(chars) and chars[start]!='a'"),SMALLEST.replace("if start==len(chars):chars[-1]='z'","if start==len(chars):chars[0]='z'")],
 ['Skips the first non-a block and begins at an a, causing a harmful wrap.','For an all-a string, changes the first character rather than the lexicographically least-significant last character.'],smallest_oracle,random_smallest,
 ['Avoid decrementing a because it wraps to z, except when every character is a.','Start at the first non-a character and decrement its maximal consecutive non-a block.','If no such character exists, replace only the final a with z.','The earliest improvable position dominates lexicographic order; extending through non-a characters improves the string until the first harmful wrap.'],'O(n)','O(n)',5),
2735:entry('minimum_chocolate_collection_cost',[('nums','list[int]'),('x','int')],'int',['arrays','dynamic programming','enumeration'],
 ['Chocolate type i initially costs nums[i].','Pay x for one global cyclic operation; after k operations, type i may be bought using any of the k+1 cyclically preceding prices.','Choose the operation count and one purchase price per type to minimize total cost.'],
 [([[20,1,15],5],'After two rotations every type can use price one, so purchases cost three and rotations cost ten, totaling thirteen.'),([[1,2,3],10],'Rotations cannot save their cost, so buying immediately costs six.')],
 [[a,x] for a,x in [([5],10),([20,1,15],5),([1,2,3],10),([10,10],0),([9,1],3),([8,7,6,5],1),([5,100,5],20),([100,1,100,1],15),([4,3,2,1],0),([7,2,9,4,1],6),([1,100,100,100],20),([30,20,10],7),([6,5,4,3,2,1],3),([12,1,8,20],100)]],
 CHOCOLATES,[CHOCOLATES.replace('range(1,n)','range(1,n-1)'),CHOCOLATES.replace("best[index]=min(best[index],nums[(index-operations)%n])","best[index]=nums[(index-operations)%n]")],
 ['Never considers using n-1 rotations, which can be the unique optimum.','Keeps only the newest rotated price instead of the cheapest price seen across all rotations.'],chocolates_oracle,random_chocolates,
 ['There are only n distinct useful rotation counts.','Maintain each type’s cheapest reachable price as one more cyclic source becomes available.','For every k from zero through n-1, minimize sum(best prices)+k*x.','For a fixed k, choosing each type’s cheapest reachable price is independent; enumerating every useful k therefore includes the global optimum.'],'O(n²)','O(n)',5),
2736:entry('maximum_sum_queries',[('nums1','list[int]'),('nums2','list[int]'),('queries','list[list[int]]')],'list[int]',['arrays','offline queries','sorting','fenwick tree'],
 ['Point i has coordinates nums1[i] and nums2[i] and value nums1[i]+nums2[i].','For query [x,y], consider points whose first coordinate is at least x and second is at least y.','Return the maximum point value for every query, or -1 when no point qualifies.'],
 [([[4,3,1,2],[2,4,9,5],[[4,1],[1,3],[2,5]]],'The best qualifying sums for the three thresholds are six, ten, and seven.'),([[2,1],[2,3],[[3,3]]],'No first coordinate reaches three, so the answer is -1.')],
 [[a,b,q] for a,b,q in [([1],[1],[[1,1]]),([1],[1],[[2,1]]),([4,3,1,2],[2,4,9,5],[[4,1],[1,3],[2,5]]),([2,1],[2,3],[[3,3]]),([5,5],[1,9],[[5,1],[5,9]]),([1,2,3],[3,2,1],[[1,1],[2,2],[3,3]]),([10,1],[1,10],[[5,5]]),([3,7,4],[8,2,6],[[4,5]]),([2,2,2],[1,2,3],[[2,2]]),([9,8,7],[1,2,3],[[8,1],[7,3]]),([1,100],[100,1],[[1,1]]),([6,4,2],[5,7,9],[[3,6],[6,5]]),([5,3,8,2],[4,9,1,7],[[2,4],[7,1]]),([20,10,30],[3,40,2],[[10,3],[21,1]] )]],
 QUERIES,[QUERIES.replace('points[point][0]>=x','points[point][0]>x'),QUERIES.replace('bisect_left(values,y)','bisect_left(values,y)+1')],
 ['Treats the first-coordinate threshold as strict.','Queries values strictly above y and loses points exactly on the second-coordinate threshold.'],queries_oracle,random_queries,
 ['Sort points and queries by descending first-coordinate threshold.','As x decreases, insert every newly eligible point into a suffix-maximum structure keyed by its second coordinate.','Coordinate-compress second coordinates and use a reversed Fenwick maximum query for y and above.','At each query, the structure contains exactly points meeting x; its suffix maximum enforces y and returns the best eligible sum.'],'O((n+q) log(n+q))','O(n+q)',8),
2737:entry('closest_marked_node',[('n','int'),('edges','list[list[int]]'),('s','int'),('marked','list[int]')],'int',['graphs','shortest path','heaps'],
 ['Each edge [u,v,w] is directed from u to v with positive weight w.','Starting at node s, find the shortest distance to any node listed in marked.','Return -1 when no marked node is reachable.'],
 [([4,[[0,1,1],[1,2,3],[2,3,2],[0,3,4]],0,[2,3]],'Node three is directly reachable at distance four, less than the distance to node two.'),([3,[[0,1,2]],2,[0,1]],'No directed edge leaves node two, so neither marked node is reachable.')],
 [[n,e,s,m] for n,e,s,m in [(1,[],0,[0]),(2,[[0,1,5]],0,[1]),(2,[[0,1,5]],1,[0]),(3,[[0,1,2]],2,[0,1]),(4,[[0,1,1],[1,2,3],[2,3,2],[0,3,4]],0,[2,3]),(3,[[0,1,10],[0,2,3],[2,1,2]],0,[1]),(4,[[0,1,1],[1,2,1]],0,[3]),(4,[[0,1,5],[1,3,5],[0,2,2],[2,3,2]],0,[3]),(5,[[0,1,3],[1,2,4],[2,4,5]],0,[2,4]),(3,[[0,1,4],[1,0,1]],0,[0]),(4,[[0,1,8],[0,2,2],[2,1,2]],0,[1,3]),(5,[[4,3,1],[3,2,1],[2,1,1]],4,[1]),(3,[[0,1,5],[0,1,2],[1,2,1]],0,[2]),(6,[[0,1,1],[1,2,1],[3,4,1]],0,[4,5])]],
 MARKED,[MARKED.replace('graph[left].append((right,weight))','graph[right].append((left,weight))'),MARKED.replace('if node in targets:return distance','if node in targets and node!=s:return distance')],
 ['Reverses every directed edge.','Refuses to return zero when the starting node itself is marked.'],marked_oracle,random_marked,
 ['This is a multi-target shortest-path problem with nonnegative edges.','Run Dijkstra from s and keep marked nodes in a set.','Return as soon as a marked node is removed from the priority queue at its finalized distance.','Dijkstra pops nodes in nondecreasing shortest distance, so the first finalized marked node is the closest one.'],'O((n+e) log n)','O(n+e)',5),
2739:entry('total_truck_distance',[('mainTank','int'),('additionalTank','int')],'int',['math','simulation'],
 ['The truck travels ten kilometers per liter consumed from its main tank.','After each five liters consumed from the main tank, transfer one liter from the additional tank when available.','Return the greatest total distance before the main tank becomes empty.'],
 [([5,10],'Five original liters trigger one transfer, so six liters are consumed for sixty kilometers.'),([1,2],'The main tank empties before five liters are consumed, so no transfer occurs and distance is ten.')],
 [[m,a] for m,a in [(1,0),(1,2),(4,10),(5,0),(5,1),(5,10),(8,3),(9,3),(10,1),(10,10),(20,0),(20,2),(25,10),(100,100)]],
 FUEL,[FUEL.replace('(mainTank-1)//4','mainTank//5'),FUEL.replace('transfers=min((mainTank-1)//4,additionalTank)','transfers=(mainTank-1)//4')],
 ['Counts transfers from each original block of five and misses that transferred fuel can trigger later transfers.','Ignores the limited number of liters in the additional tank.'],fuel_oracle,random_fuel,
 ['A transfer adds one consumable liter after every five consumed liters.','With m original liters, the self-sustaining transfer opportunities are floor((m-1)/4), capped by additionalTank.','Add that transfer count to the original main-tank liters and multiply by ten.','Each transfer requires four more original-or-transferred liters beyond the previous trigger; the final empty state cannot trigger fuel that would be consumed afterward.'],'O(1)','O(1)',3),
}
