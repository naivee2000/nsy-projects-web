"""Product matrices, mountain triplets, knapsack lengths, equal sums, and graph champions."""
from .import_batch_055 import entry


def product_matrix_oracle(args):
    grid=args[0];flat=[value for row in grid for value in row];answer=[];index=0
    for row in grid:
        current=[]
        for _ in row:
            product=1
            for other,value in enumerate(flat):
                if other!=index:product=product*value%12345
            current.append(product);index+=1
        answer.append(current)
    return answer


def random_product_matrix(rng):
    rows,cols=rng.randint(1,4),rng.randint(1,4)
    if rows*cols==1:cols=2
    return [[[rng.randint(1,20000) for _ in range(cols)] for _ in range(rows)]]


def mountain_triplet_oracle(args):
    nums=args[0];values=[nums[i]+nums[j]+nums[k] for i in range(len(nums)) for j in range(i+1,len(nums)) for k in range(j+1,len(nums)) if nums[i]<nums[j] and nums[k]<nums[j]]
    return min(values,default=-1)


def random_mountain_triplet(rng):return [[rng.randint(1,30) for _ in range(rng.randint(3,16))]]


def subsequence_length_oracle(args):
    nums,target=args;best=-1
    for mask in range(1<<len(nums)):
        if sum(nums[index] for index in range(len(nums)) if mask>>index&1)==target:best=max(best,mask.bit_count())
    return best


def random_subsequence_length(rng):return [[rng.randint(1,12) for _ in range(rng.randint(1,12))],rng.randint(1,45)]


def equal_sum_oracle(args):
    first,second=args
    minimum1=sum(value or 1 for value in first);minimum2=sum(value or 1 for value in second)
    flexible1=0 in first;flexible2=0 in second
    for total in range(max(minimum1,minimum2),max(minimum1,minimum2)+200):
        if (total==minimum1 or flexible1) and (total==minimum2 or flexible2):return total
    return -1


def random_equal_sum(rng):
    return [[rng.randint(0,8) for _ in range(rng.randint(1,8))],[rng.randint(0,8) for _ in range(rng.randint(1,8))]]


def champion_oracle(args):
    size,edges=args;incoming={target for _,target in edges};candidates=[team for team in range(size) if team not in incoming]
    return candidates[0] if len(candidates)==1 else -1


def random_champion(rng):
    size=rng.randint(1,10);order=list(range(size));rng.shuffle(order);edges=[]
    for i in range(size):
        for j in range(i+1,size):
            if rng.random()<.25:edges.append([order[i],order[j]])
    return [size,edges]


PRODUCT_MATRIX='''def construct_product_matrix(grid):
    rows=len(grid);cols=len(grid[0]);answer=[[1]*cols for _ in range(rows)];suffix=1
    for index in range(rows*cols-1,-1,-1):
        row,col=divmod(index,cols);answer[row][col]=suffix;suffix=suffix*grid[row][col]%12345
    prefix=1
    for index in range(rows*cols):
        row,col=divmod(index,cols);answer[row][col]=answer[row][col]*prefix%12345;prefix=prefix*grid[row][col]%12345
    return answer
'''


MOUNTAIN='''def minimum_mountain_triplet_sum(nums):
    size=len(nums);right=[float('inf')]*(size+1)
    for index in range(size-1,-1,-1):right[index]=min(right[index+1],nums[index])
    left=float('inf');answer=float('inf')
    for index,value in enumerate(nums):
        if left<value and right[index+1]<value:answer=min(answer,left+value+right[index+1])
        left=min(left,value)
    return -1 if answer==float('inf') else answer
'''


SUBSEQUENCE_LENGTH='''def longest_subsequence_sum_length(nums,target):
    best=[-1]*(target+1);best[0]=0
    for value in nums:
        for total in range(target,value-1,-1):
            if best[total-value]>=0:best[total]=max(best[total],best[total-value]+1)
    return best[target]
'''


EQUAL_SUM='''def minimum_equal_replacement_sum(nums1,nums2):
    minimum1=sum(value if value else 1 for value in nums1);minimum2=sum(value if value else 1 for value in nums2)
    if minimum1<minimum2 and 0 not in nums1:return -1
    if minimum2<minimum1 and 0 not in nums2:return -1
    return max(minimum1,minimum2)
'''


CHAMPION='''def find_unique_champion(n,edges):
    indegree=[0]*n
    for _,weaker in edges:indegree[weaker]+=1
    candidates=[team for team,value in enumerate(indegree) if value==0]
    return candidates[0] if len(candidates)==1 else -1
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
2906:entry('construct_product_matrix',[('grid','list[list[int]]')],'list[list[int]]',['prefix products','matrices','modular arithmetic'],['grid is a nonempty rectangular positive-integer matrix with at least two cells.','Each output cell is the product of every input cell except the corresponding one, modulo 12345.','Do not use modular division because excluded values may not be invertible.'],[([[[1,2],[3,4]]],'Excluding each value from total product twenty-four gives [[24,12],[8,6]].'),([[[12345],[2],[1]]],'Excluding 12345 gives two; every other product contains a zero-modulo factor.')],[[g] for g in [[[1,1]],[[2,3]],[[2],[3]],[[5,5],[5,5]],[[1,2,3]],[[1],[2],[3]],[[12345,1]],[[12345,12345]],[[2,3],[5,7]],[[10,20,30],[40,50,60]],[[99999,2],[3,4]],[[1,12345,2],[3,4,5]],[[7,11],[13,17],[19,23]],[[1000000000,1],[1,1]]]],PRODUCT_MATRIX,[PRODUCT_MATRIX.replace('answer[row][col]=suffix','answer[row][col]=suffix*grid[row][col]%12345'),PRODUCT_MATRIX.replace('%12345','%12346')],['Includes the current cell in the suffix contribution instead of excluding it.','Uses modulus 12346 rather than the required 12345.'],product_matrix_oracle,random_product_matrix,lesson('Division is unsafe under a composite modulus, but products before and after a cell are independent.','Flatten traversal conceptually and combine a suffix-exclusive pass with a prefix-exclusive pass.','Store the product after each cell, multiply by the product before it, and reduce modulo 12345 throughout.','Every other cell lies exactly in the prefix or suffix relative to the excluded position, so their product is included once without division.'),'O(rows*cols)','O(rows*cols) output',5),
2909:entry('minimum_mountain_triplet_sum',[('nums','list[int]')],'int',['prefix minima','arrays'],['nums contains at least three positive integers.','Choose i<j<k with both nums[i] and nums[k] strictly smaller than the middle value nums[j].','Return the minimum three-value sum, or -1 when no mountain triplet exists.'],[([[8,6,1,5,3]],'Values one, five, and three form the minimum mountain sum nine.'),([[5,4,8,7,10,2]],'Values four, seven, and two form the minimum sum thirteen.')],[[n] for n in [[1,2,3],[3,2,1],[1,3,2],[2,3,1],[3,1,2],[2,2,1],[1,2,1],[5,4,3,4,5],[6,5,4,3,4,5],[10,1,9,2,8],[1,10,2,9,3],[4,8,2,7,1],[9,3,6,2,5,1],[7,1,8,2,9,3]]],MOUNTAIN,[MOUNTAIN.replace('right[index+1]<value','right[index+1]>value'),MOUNTAIN.replace('left<value','left<=value').replace('right[index+1]<value','right[index+1]<=value')],['Requires the right endpoint to be greater than the middle instead of smaller.','Allows equal endpoint and middle values despite strict mountain inequalities.'],mountain_triplet_oracle,random_mountain_triplet,lesson('For each middle index, only the smallest value on each side can minimize a valid sum.','Precompute suffix minima and maintain a running prefix minimum.','When both side minima are strictly below the middle, update their three-value sum.','Any valid middle is improved or matched by replacing its endpoints with the side minima, so testing every middle is exhaustive and optimal.'),'O(n)','O(n)',5),
2915:entry('longest_subsequence_sum_length',[('nums','list[int]'),('target','int')],'int',['dynamic programming','knapsack','subsequences'],['nums contains positive integers and target is positive.','Choose indices in original order whose values sum exactly to target.','Return the maximum chosen length, or -1 when no subsequence reaches target.'],[([[1,2,3,4,5],9],'Both [1,3,5] and [2,3,4] reach nine with maximum length three.'),([[4,1,3,2,1,5],7],'The subsequence [1,3,2,1] reaches seven with length four.')],[[n,t] for n,t in [([1],1),([1],2),([1,1],2),([2,2],2),([1,2,3],3),([1,2,3],4),([5,4,3,2,1],6),([2,2,2,2],6),([1,1,5,4,5],3),([3,1,3,1,3],5),([10,1,1,1],3),([2,5,1,2,1],6),([7,3,4,2,6],9),([1,2,1,2,1,2],5)]],SUBSEQUENCE_LENGTH,[SUBSEQUENCE_LENGTH.replace('range(target,value-1,-1)','range(value,target+1)'),SUBSEQUENCE_LENGTH.replace('max(best[total],best[total-value]+1)','best[total-value]+1')],['Updates sums upward and may reuse the same input element multiple times.','Overwrites a longer solution with the latest shorter solution.'],subsequence_length_oracle,random_subsequence_length,lesson('For each sum, retain the longest subsequence length achievable from processed items.','Use descending 0-1 knapsack updates so each positive value is considered at most once.','If total-value is reachable, maximize best[total] with best[total-value]+1.','Descending updates preserve the previous-item state, and maximizing length for every exact sum is sufficient for all future extensions.'),'O(n*target)','O(target)',5),
2918:entry('minimum_equal_replacement_sum',[('nums1','list[int]'),('nums2','list[int]')],'int',['greedy','arrays'],['Both arrays are nonempty and contain nonnegative integers.','Replace every zero with a strictly positive integer so the final sums are equal.','Return the smallest possible common sum, or -1 if equality is impossible.'],[([[3,2,0,1,0],[6,5,0]],'Replacing zeros by positive values can make both sums twelve, the larger minimum.'),([[2,0,2,0],[1,4]],'The first array’s minimum is six, but the fixed second sum is five, so equality is impossible.')],[[a,b] for a,b in [([1],[1]),([0],[0]),([0],[1]),([0],[2]),([1],[2]),([1,0],[2]),([1],[2,0]),([0,0],[1]),([5,0],[2,2]),([3,3],[1,0,0]),([1,2,0],[4,0]),([10],[0,0,0]),([2,0,3],[1,1,1]),([0,5,0],[3,3])]],EQUAL_SUM,[EQUAL_SUM.replace('value if value else 1','value'),EQUAL_SUM.replace('max(minimum1,minimum2)','min(minimum1,minimum2)')],['Treats replacement zeros as contributing zero instead of at least one.','Returns the smaller minimum sum even though the other array cannot decrease.'],equal_sum_oracle,random_equal_sum,lesson('Replacing each zero by one gives an array’s minimum attainable final sum.','The common sum must be the larger minimum; the lower side can reach it only if that side contains a zero.','Compute both minima, reject when the smaller fixed array cannot grow, otherwise return their maximum.','Any array with a zero can add arbitrary extra positive amount to one replacement, while an array without zeros has a fixed sum, proving both feasibility and minimality.'),'O(n+m)','O(1)',5),
2924:entry('find_unique_champion',[('n','int'),('edges','list[list[int]]')],'int',['graphs','indegree'],['Teams are numbered zero through n-1 and edges form a directed acyclic graph from stronger to weaker teams.','A champion has no incoming edge from any stronger team.','Return the unique champion, or -1 when more than one team has indegree zero.'],[([3,[[0,1],[1,2]]],'Only team zero has no incoming edge, so it is the champion.'),([4,[[0,2],[1,3],[1,2]]],'Teams zero and one both have no incoming edge, so no unique champion exists.')],[[n,e] for n,e in [(1,[]),(2,[]),(2,[[0,1]]),(2,[[1,0]]),(3,[[0,1],[0,2]]),(3,[[1,0],[1,2]]),(3,[[0,2],[1,2]]),(4,[[0,1],[1,2],[2,3]]),(4,[[3,2],[2,1],[1,0]]),(4,[[0,2],[0,3],[1,3]]),(5,[[2,0],[2,1],[2,3],[2,4]]),(5,[[0,1],[2,3]]),(6,[[0,1],[0,2],[2,3],[3,4],[4,5]]),(6,[[1,0],[1,2],[3,4],[3,5]])]],CHAMPION,[CHAMPION.replace('indegree[weaker]+=1','indegree[_]+=1'),CHAMPION.replace('if len(candidates)==1 else -1','if candidates else -1')],['Counts outgoing edges instead of incoming edges.', 'Returns the first undefeated team even when the champion is not unique.'],champion_oracle,random_champion,lesson('Every edge proves its destination has a stronger team.','Count incoming edges and collect teams with indegree zero.','Return the sole zero-indegree team; otherwise return -1.','In a DAG every champion candidate is exactly a source, and uniqueness is the only remaining requirement.'),'O(n+edges)','O(n)',5),
}
