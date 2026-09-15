"""Pair distances, interval coverage, plus signs, couples, and sorted chunks."""
from itertools import combinations
from .import_batch_055 import entry

def distance_oracle(a):
    nums,k=a;return sorted(abs(x-y) for i,x in enumerate(nums) for y in nums[i+1:])[k-1]
def random_distance(r):
    n=r.randint(2,30);return [[r.randint(0,100) for _ in range(n)],r.randint(1,n*(n-1)//2)]
def intersection_oracle(a):
    intervals=a[0];points=range(min(x[0] for x in intervals),max(x[1] for x in intervals)+1)
    for size in range(len(points)+1):
        if any(all(sum(left<=x<=right for x in chosen)>=2 for left,right in intervals) for chosen in combinations(points,size)):return size
def random_intersection(r):
    intervals=[]
    for _ in range(r.randint(1,5)):
        left=r.randint(0,7);intervals.append([left,r.randint(left+1,9)])
    return [intervals]
def plus_oracle(a):
    n,mines=a;blocked={tuple(x) for x in mines};best=0
    for i in range(n):
        for j in range(n):
            order=0
            while all((i+di*order,j+dj*order) not in blocked and 0<=i+di*order<n and 0<=j+dj*order<n for di,dj in ((1,0),(-1,0),(0,1),(0,-1))):order+=1
            best=max(best,order)
    return best
def random_plus(r):
    n=r.randint(1,8);cells=[[i,j] for i in range(n) for j in range(n)];return [n,r.sample(cells,r.randint(0,len(cells)))]
def couples_oracle(a):
    row=a[0];n=len(row)//2;graph=[set() for _ in range(n)]
    for i in range(0,len(row),2):
        x,y=row[i]//2,row[i+1]//2;graph[x].add(y);graph[y].add(x)
    seen=set();components=0
    for start in range(n):
        if start not in seen:
            components+=1;todo=[start];seen.add(start)
            while todo:
                for nxt in graph[todo.pop()]:
                    if nxt not in seen:seen.add(nxt);todo.append(nxt)
    return n-components
def random_couples(r):
    row=list(range(2*r.randint(1,10)));r.shuffle(row);return [row]
def chunks_oracle(a):
    arr=a[0];n=len(arr);best=1
    for mask in range(1<<(n-1)):
        result=[];start=0;parts=0
        for i in range(n):
            if i==n-1 or mask>>i&1:result.extend(sorted(arr[start:i+1]));start=i+1;parts+=1
        if result==sorted(arr):best=max(best,parts)
    return best
def random_chunks(r):
    arr=list(range(r.randint(1,9)));r.shuffle(arr);return [arr]

DISTANCE='''def kth_smallest_pair_distance(nums,k):
    nums=sorted(nums)
    def count(limit):
        total=left=0
        for right,value in enumerate(nums):
            while value-nums[left]>limit:left+=1
            total+=right-left
        return total
    low,high=0,nums[-1]-nums[0]
    while low<high:
        middle=(low+high)//2
        if count(middle)>=k:high=middle
        else:low=middle+1
    return low
'''
INTERSECTION='''def minimum_two_point_interval_set(intervals):
    intervals=sorted(intervals,key=lambda x:(x[1],-x[0]));older=newer=-1;answer=0
    for left,right in intervals:
        if left<=older:continue
        if left>newer:answer+=2;older,newer=right-1,right
        else:answer+=1;older,newer=newer,right
    return answer
'''
PLUS='''def largest_plus_sign_order(n,mines):
    blocked={tuple(cell) for cell in mines};grid=[[0]*n for _ in range(n)]
    for i in range(n):
        run=0
        for j in range(n):run=0 if (i,j) in blocked else run+1;grid[i][j]=run
        run=0
        for j in range(n-1,-1,-1):run=0 if (i,j) in blocked else run+1;grid[i][j]=min(grid[i][j],run)
    answer=0
    for j in range(n):
        run=0
        for i in range(n):run=0 if (i,j) in blocked else run+1;grid[i][j]=min(grid[i][j],run)
        run=0
        for i in range(n-1,-1,-1):run=0 if (i,j) in blocked else run+1;answer=max(answer,min(grid[i][j],run))
    return answer
'''
COUPLES='''def minimum_couple_swaps(row):
    couples=len(row)//2;parent=list(range(couples))
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for i in range(0,len(row),2):
        x,y=find(row[i]//2),find(row[i+1]//2)
        if x!=y:parent[x]=y
    return couples-sum(find(i)==i for i in range(couples))
'''
CHUNKS='''def maximum_sorted_chunks(arr):
    answer=maximum=0
    for i,value in enumerate(arr):
        maximum=max(maximum,value)
        if maximum==i:answer+=1
    return answer
'''

BATCH={
719:entry('kth_smallest_pair_distance',[('nums','list[int]'),('k','int')],'int',['arrays','binary search','two pointers'],['nums has at least two integers and k indexes the sorted multiset of all unordered-pair distances from one.','Repeated values and repeated distances count separately.','Return the kth smallest absolute distance.'],[([[1,3,1],1],'The equal pair has distance zero, which is smallest.'),([[1,6,1],3],'Distances are zero, five, and five, so the third is five.')],[[n,k] for n,k in [([1,1],1),([1,3,1],1),([1,6,1],3),([1,2],1),([0,10],1),([1,2,3],2),([4,4,4],3),([9,1,5],1),([9,1,5],3),([0,2,7,10],4),([1,100,50],2),([3,8,3,8],5),([5,4,3,2,1],7),([0,0,1,1],4)]],DISTANCE,[DISTANCE.replace('>=k','>k'),DISTANCE.replace('total+=right-left','total+=right-left+1')],['Uses a strict count threshold and skips exact kth boundaries.','Counts each element paired with itself.'],distance_oracle,random_distance,['For a proposed distance d, count pairs no farther than d with a sliding left pointer.','That count is monotone in d.','Binary-search the first d whose count reaches k.','The lower-bound distance is exactly the kth value in the sorted distance multiset.'],'O(n log range)','O(n)',8),
757:entry('minimum_two_point_interval_set',[('intervals','list[list[int]]')],'int',['intervals','greedy'],['Every inclusive interval has at least two integer points.','Choose the smallest set of integers such that each interval contains at least two chosen values.','Return the set size.'],[([[[1,3],[3,7],[8,9]]],'Two points cover each disconnected side and one overlap is shared, requiring five total.'),([[[1,3],[1,4],[2,5]]],'Choosing two and three satisfies all three intervals.')],[[x] for x in [[[1,2]],[[1,3],[3,7],[8,9]],[[1,3],[1,4],[2,5]],[[0,1],[1,2]],[[1,5],[2,4]],[[1,2],[2,3],[3,4]],[[0,9],[1,8],[2,7]],[[1,2],[4,5]],[[2,6],[4,8],[6,9]],[[0,2],[0,3]],[[5,7],[1,6]],[[1,10],[9,10]],[[0,4],[2,3],[3,5]],[[1,3],[2,4],[4,6]]]],INTERSECTION,[INTERSECTION.replace('right-1,right','left,left+1'),INTERSECTION.replace('if left<=older','if left<older')],['Chooses earliest points, reducing reuse by later intervals.','Mishandles an interval whose start equals the older selected point.'],intersection_oracle,random_intersection,['Sort by increasing right endpoint, with larger starts first on ties.','Track the two greatest chosen points; add two if neither is inside, one if only the newer is inside.','Place new points as far right as possible.','Rightmost feasible points maximize their chance of covering every later-ending interval without harming the current one.'],'O(n log n)','O(n)',8),
764:entry('largest_plus_sign_order',[('n','int'),('mines','list[list[int]]')],'int',['matrices','dynamic programming'],['Begin with an n by n grid of ones and set listed mine coordinates to zero.','A plus order is one plus its equal arm length in four cardinal directions.','Return the greatest order, or zero if every cell is mined.'],[([5,[[4,2]]],'The largest surviving axis-aligned plus has order two.'),([1,[[0,0]]],'The only cell is mined, so no plus exists.')],[[n,m] for n,m in [(1,[]),(1,[[0,0]]),(2,[]),(2,[[0,0]]),(3,[]),(3,[[1,1]]),(5,[[4,2]]),(4,[[0,0],[3,3]]),(5,[[2,0],[2,4]]),(6,[[3,3]]),(3,[[0,1],[1,0],[1,2],[2,1]]),(4,[[1,1],[2,2]]),(7,[[0,0],[6,6],[3,3]]),(2,[[0,0],[0,1],[1,0],[1,1]])]],PLUS,[PLUS.replace('range(n-1,-1,-1)','range(n)',1),PLUS.replace('answer=max(answer,min(grid[i][j],run))','answer=max(answer,grid[i][j])')],['Scans the right arm in the wrong direction.','Ignores the final downward/upward arm constraint.'],plus_oracle,random_plus,['At each cell the order is the minimum consecutive-one length in four directions.','Compute left/right/up/down run lengths through directional sweeps.','Store running minima and take the maximum after all four directions.','A plus of order k exists exactly when all four directional lengths are at least k.'],'O(n^2)','O(n^2)',5),
765:entry('minimum_couple_swaps',[('row','list[int]')],'int',['graphs','union-find'],['row is a permutation of 0..2n-1; partners are 2c and 2c+1.','One swap exchanges any two seated people.','Return the fewest swaps so every adjacent seat pair is a couple.'],[([[0,2,1,3]],'One swap seats couples zero-one and two-three together.'),([[3,2,0,1]],'Both couples are already adjacent, so return zero.')],[[x] for x in [[0,1],[1,0],[0,2,1,3],[3,2,0,1],[0,3,2,1],[0,4,2,3,1,5],[5,4,3,2,1,0],[0,2,4,1,3,5],[2,0,1,3],[1,2,0,3],[6,2,1,7,4,5,0,3],[0,5,2,7,4,1,6,3],[3,1,4,0,2,5],[7,0,3,4,1,6,2,5]]],COUPLES,[COUPLES.replace('couples-sum','couples-1-sum'),COUPLES.replace('row[i+1]//2','row[i+1]%2')],['Subtracts an extra component from the swap count.','Maps the second person by parity instead of couple number.'],couples_oracle,random_couples,['Each adjacent seat pair connects the two couple IDs currently occupying it.','Within a connected component of c couples, c-1 swaps suffice and are necessary.','Union each seated pair and return couples minus component count.','Summing c-1 over all components yields n-components.'],'O(n alpha(n))','O(n)',8),
769:entry('maximum_sorted_chunks',[('arr','list[int]')],'int',['arrays','greedy'],['arr is a permutation of 0..n-1.','Partition into contiguous chunks, sort each independently, and concatenate.','Return the maximum chunks that produce globally sorted order.'],[([[4,3,2,1,0]],'No proper prefix contains exactly its target values, so only one chunk works.'),([[1,0,2,3,4]],'The first two values form one chunk and each later value can stand alone, totaling four.')],[[x] for x in [[0],[1,0],[0,1],[4,3,2,1,0],[1,0,2,3,4],[2,0,1],[0,2,1],[1,2,0],[2,1,0,3],[3,2,1,0],[0,1,2,3],[2,3,0,1],[1,3,2,0],[0,3,1,2]]],CHUNKS,[CHUNKS.replace('maximum==i','maximum<=i'),CHUNKS.replace('maximum=max(maximum,value)','maximum=value')],['Uses a non-strict boundary test that is unsafe outside the permutation invariant.','Forgets earlier large values when testing prefix closure.'],chunks_oracle,random_chunks,['A chunk may end at i exactly when the prefix contains values 0..i.','For a permutation, that holds when the prefix maximum equals i.','Scan with a running maximum and count equality positions.','Every valid boundary is independent, so cutting at all of them maximizes the number of chunks.'],'O(n)','O(1)',5),
}
BATCH[769]['wrong'][0]=CHUNKS.replace('maximum==i','maximum==i+1')
BATCH[769]['wrong_reasons'][0]='Tests an off-by-one prefix maximum and misses valid chunk boundaries.'
