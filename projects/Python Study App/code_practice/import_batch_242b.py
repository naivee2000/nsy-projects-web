"""Order statistics, matrix maxima, unique subarrays, and circular residue costs."""
from bisect import bisect_left, bisect_right
from collections import Counter
from .import_batch_055 import entry

MOD = 1_000_000_007


def power_oracle(args):
    nums, power, queries = args
    values = list(nums)
    answer = []
    for value, k in queries:
        values.append(value)
        chosen = sorted(values, reverse=True)[k - 1]
        power = pow(power, chosen, MOD)
        answer.append(power)
    return answer


def random_power(rng):
    nums = [rng.randint(1, 30) for _ in range(rng.randint(1, 10))]
    queries = []
    for _ in range(rng.randint(1, 10)):
        queries.append([rng.randint(1, 30), rng.randint(1, len(nums) + len(queries) + 1)])
    return [nums, rng.randint(1, 30), queries]


def local_oracle(args):
    matrix = args[0]
    rows, cols = len(matrix), len(matrix[0])
    answer = 0
    for row in range(rows):
        for col in range(cols):
            radius = matrix[row][col]
            if radius == 0:
                continue
            largest = True
            for other_row in range(max(0, row - radius), min(rows, row + radius + 1)):
                for other_col in range(max(0, col - radius), min(cols, col + radius + 1)):
                    if abs(other_row - row) == radius and abs(other_col - col) == radius:
                        continue
                    if matrix[other_row][other_col] > radius:
                        largest = False
            answer += largest
    return answer


def random_local(rng):
    rows, cols = rng.randint(1, 7), rng.randint(1, 7)
    return [[[rng.randint(0, 6) for _ in range(cols)] for _ in range(rows)]]


def unique_oracle(args):
    nums = args[0]
    for length in range(1, len(nums) + 1):
        counts = Counter(tuple(nums[start:start + length]) for start in range(len(nums) - length + 1))
        if 1 in counts.values():
            return length


def random_unique(rng):
    return [[rng.randint(1, 6) for _ in range(rng.randint(1, 18))]]


def modulo_oracle(args):
    nums, modulus = args
    even = nums[::2]
    odd = nums[1::2]
    def cost(values, target):
        return sum(min(abs(value % modulus - target), modulus - abs(value % modulus - target)) for value in values)
    return min(cost(even, left) + cost(odd, right)
               for left in range(modulus) for right in range(modulus) if left != right)


def random_modulo(rng):
    return [[rng.randint(1, 80) for _ in range(rng.randint(1, 16))], rng.randint(2, 10)]


POWER_FENWICK = '''def power_update_fenwick(nums,p,queries):
    modulus=1_000_000_007;coordinates=sorted(set(nums+[value for value,_ in queries]));index={value:i+1 for i,value in enumerate(coordinates)};tree=[0]*(len(coordinates)+1)
    def add(position):
        while position<len(tree):tree[position]+=1;position+=position&-position
    def select(order):
        position=0;step=1<<(len(coordinates).bit_length()-1)
        while step:
            nxt=position+step
            if nxt<len(tree) and tree[nxt]<order:position=nxt;order-=tree[nxt]
            step//=2
        return coordinates[position]
    for value in nums:add(index[value])
    answer=[];size=len(nums)
    for value,k in queries:
        add(index[value]);size+=1;chosen=select(size-k+1);p=pow(p,chosen,modulus);answer.append(p)
    return answer
'''

POWER_HEAPS = '''def power_update_heaps(nums,p,queries):
    import heapq
    modulus=1_000_000_007;lower=[-value for value in nums];heapq.heapify(lower);upper=[];answer=[]
    for value,k in queries:
        if upper and value>=upper[0]:heapq.heappush(upper,value)
        else:heapq.heappush(lower,-value)
        while len(upper)>k:heapq.heappush(lower,-heapq.heappop(upper))
        while len(upper)<k:heapq.heappush(upper,-heapq.heappop(lower))
        chosen=upper[0];p=pow(p,chosen,modulus);answer.append(p)
    return answer
'''

LOCAL = '''def count_local_maximums(matrix):
    rows=len(matrix);cols=len(matrix[0]);positions={}
    for row in range(rows):
        for col in range(cols):
            if matrix[row][col]:positions.setdefault(matrix[row][col],[]).append((row,col))
    answer=0
    for value,cells in positions.items():
        prefix=[[0]*(cols+1) for _ in range(rows+1)]
        for row in range(rows):
            running=0
            for col in range(cols):
                running+=matrix[row][col]>value;prefix[row+1][col+1]=prefix[row][col+1]+running
        for row,col in cells:
            top=max(0,row-value);bottom=min(rows-1,row+value);left=max(0,col-value);right=min(cols-1,col+value)
            greater=prefix[bottom+1][right+1]-prefix[top][right+1]-prefix[bottom+1][left]+prefix[top][left]
            for other_row in (row-value,row+value):
                for other_col in (col-value,col+value):
                    if 0<=other_row<rows and 0<=other_col<cols and matrix[other_row][other_col]>value:greater-=1
            answer+=greater==0
    return answer
'''

UNIQUE = '''def smallest_unique_subarray(nums):
    n=len(nums);suffixes=list(range(n));rank=list(nums);step=1
    while step<n:
        suffixes.sort(key=lambda start:(rank[start],rank[start+step] if start+step<n else -1))
        next_rank=[0]*n
        for order in range(1,n):
            previous=suffixes[order-1];current=suffixes[order]
            next_rank[current]=next_rank[previous]+((rank[previous],rank[previous+step] if previous+step<n else -1)!=(rank[current],rank[current+step] if current+step<n else -1))
        rank=next_rank
        if rank[suffixes[-1]]==n-1:break
        step*=2
    order=[0]*n
    for position,start in enumerate(suffixes):order[start]=position
    lcp=[0]*max(0,n-1);length=0
    for start in range(n):
        position=order[start]
        if position==n-1:length=0;continue
        other=suffixes[position+1]
        while start+length<n and other+length<n and nums[start+length]==nums[other+length]:length+=1
        lcp[position]=length
        if length:length-=1
    answer=n
    for start in range(n):
        position=order[start];left=lcp[position-1] if position else 0;right=lcp[position] if position<n-1 else 0;shared=max(left,right)
        if shared<n-start:answer=min(answer,shared+1)
    return answer
'''

MODULO = '''def minimum_modulo_alternating_operations(nums,k):
    from bisect import bisect_left,bisect_right
    def costs(values):
        residues=sorted(value%k for value in values);extended=sorted([value-k for value in residues]+residues+[value+k for value in residues]);prefix=[0]
        for value in extended:prefix.append(prefix[-1]+value)
        answer=[];left_radius=(k-1)//2;right_radius=k//2
        for target in range(k):
            left=bisect_left(extended,target-left_radius);right=bisect_right(extended,target+right_radius);middle=bisect_right(extended,target,left,right)
            answer.append(target*(middle-left)-(prefix[middle]-prefix[left])+(prefix[right]-prefix[middle])-target*(right-middle))
        return answer
    even=costs(nums[::2]);odd=costs(nums[1::2]);order=sorted(range(k),key=lambda residue:odd[residue]);first,second=order[:2]
    return min(even[residue]+odd[first if first!=residue else second] for residue in range(k))
'''

LINEAR_MODULO = '''def minimum_modulo_alternating_operations(nums,k):
    even=nums[::2];odd=nums[1::2]
    return min(sum(abs(value%k-left) for value in even)+sum(abs(value%k-right) for value in odd) for left in range(k) for right in range(k) if left!=right)
'''


def lesson(a, b, c, d):
    return [a, b, c, d]


P_CASES = [
    [[2],4,[[3,1],[1,2]]], [[7,5],6,[[4,3],[7,2]]], [[1],2,[[2,1]]],
    [[5,5],3,[[5,2]]], [[1,2,3],7,[[4,4]]], [[9],1,[[1,2],[8,1]]],
    [[2,8],5,[[4,2],[10,1],[1,4]]], [[3],6,[[3,1],[3,2],[3,4]]],
    [[1,10,4],2,[[7,3]]], [[6,2],9,[[5,1],[4,4]]], [[11],12,[[1,1]]],
    [[4,1],13,[[9,2],[2,3]]], [[8,7,6],3,[[5,4]]], [[2],10,[[1,2]]],
    [[30,1],4,[[20,2],[10,3],[5,5]]],
]
L_CASES = [
    [[[0,0,0],[0,2,0],[0,0,0]]], [[[1,2],[3,4]]], [[[1,0,1],[0,1,0],[1,0,1]]],
    [[[1,1],[1,1]]], [[[0]]], [[[5]]], [[[1,0],[0,2]]], [[[2,0,3],[0,1,0]]],
    [[[1,9],[0,1]]], [[[2,0,0],[0,0,0],[0,0,3]]], [[[0,4,0]]],
    [[[1],[2],[1]]], [[[3,0,0,4]]], [[[2,7,2],[0,2,0]]], [[[6,0],[0,1]]],
]
U_CASES = [
    [[3,3,3]], [[2,1,2,3,3]], [[1,1,2,2,1]], [[1]], [[1,2]], [[5,5]],
    [[1,2,1]], [[1,2,1,2]], [[1,1,1,2]], [[4,3,4,3,2]], [[1,2,3,1,2,4]],
    [[2,2,3,2,2]], [[1,2,1,3,1,2]], [[9,8,7,9,8,6]], [[1,1,2,1,1,3]],
]
M_CASES = [
    [[1,2,3,4],3], [[1,1,1],2], [[5],4], [[2,2],3], [[1,4,7],5],
    [[6,1,8,3],4], [[10,20,30],7], [[9,9,1,1],10], [[2,5,8,11],3],
    [[100],2], [[1,2],2], [[3,6,9,12,15],4], [[7,14,2],6], [[8,1,8,1],9],
    [[13,27,42,55,61],8],
]


BATCH = {
    3930: entry('power_update_fenwick',[('nums','list[int]'),('p','int'),('queries','list[list[int]]')],'list[int]',['arrays','fenwick tree','order statistics'],['nums and queries are nonempty; all values and p are positive and at most 10^9.','Each query [value,k] inserts value before selecting the kth largest current element.','Apply every modular exponentiation to the p produced by the preceding query.'],[(([[2],4,[[3,1],[1,2]]]),'After inserting three, the largest exponent is three; after inserting one, the second largest is two.'),(([[7,5],6,[[4,3],[7,2]]]),'The selected exponents are four and seven, producing 1296 and then 220296870.')],P_CASES,POWER_FENWICK,[POWER_FENWICK.replace('size-k+1','k'),POWER_FENWICK.replace('size+=1;chosen','chosen')],['Selects the kth smallest rank instead of the kth largest.','Does not increase the multiset size after an insertion.'],power_oracle,random_power,lesson('All inserted values are known before processing begins, so coordinate compression preserves their order.','A Fenwick tree stores the frequency of every compressed value.','After insertion, the kth largest is the element of ascending order size-k+1.','Fenwick binary lifting finds that order statistic in logarithmic time; modular exponentiation then updates the running value.'),'O((n+q)log(n+q))','O(n+q)',8),
    3933: entry('count_local_maximums',[('matrix','list[list[int]]')],'int',['arrays','matrix','prefix sums'],['matrix is nonempty, rectangular, and contains values from 0 through 200.','For a cell of value x, inspect the clipped square within x rows and columns, except positions whose row and column distances both equal x.','Only nonzero cells can be local maximums; equal values do not disqualify a cell.'],[(([[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,2,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]]),'The only nonzero cell has value two and no greater considered neighbor, so it is the sole local maximum.'),(([[[1,2],[3,4]]]),'Every smaller value considers a greater cell; only four remains a local maximum.')],L_CASES,LOCAL,[LOCAL.replace('matrix[row][col]>value','matrix[row][col]>=value'),LOCAL.replace(' and matrix[other_row][other_col]>value:greater-=1',':greater-=1')],['Counts equal-valued cells as disqualifying, including the candidate itself.','Subtracts excluded corner positions even when they do not contain a greater value.'],local_oracle,random_local,lesson('A candidate only needs to know whether its considered region contains a value greater than x.','Group candidates by value and build one two-dimensional prefix count of cells greater than that value.','Query the clipped square, then subtract the at most four excluded exact-distance corners when they are greater.','The remaining count is zero exactly for a local maximum; processing each distinct value bounds work by 200 matrix scans.'),'O(Vmn)','O(mn)',6),
    3934: entry('smallest_unique_subarray',[('nums','list[int]')],'int',['arrays','suffix array','longest common prefix'],['nums is nonempty and may contain up to 100,000 positive integers.','Equal subarrays must have the same length and values at every position.','Return the minimum length of any subarray that occurs exactly once.'],[(([[3,3,3]]),'Lengths one and two repeat, while the full length-three subarray occurs once.'),(([[2,1,2,3,3]]),'The one-element subarray [1] occurs once, so the answer is one.')],U_CASES,UNIQUE,[UNIQUE.replace('shared=max(left,right)','shared=min(left,right)'),UNIQUE.replace('answer=min(answer,shared+1)','answer=max(answer,shared+1)')],['Uses the smaller adjacent LCP and can mistake a repeated prefix for a unique one.','Maximizes candidate length instead of minimizing it.'],unique_oracle,random_unique,lesson('Every subarray is a prefix of the suffix beginning at the same position.','In suffix-array order, the longest prefix shared with any other suffix is the larger LCP with the two adjacent suffixes.','That suffix needs exactly one more value than its largest adjacent LCP to become unique.','Evaluate this required prefix at every start and take the smallest valid length; a suffix array and Kasai scan avoid enumerating subarrays.'),'O(n log² n)','O(n)',8),
    3935: entry('power_update_heaps',[('nums','list[int]'),('p','int'),('queries','list[list[int]]')],'list[int]',['arrays','heaps','order statistics'],['nums and queries are nonempty; values and p are positive.','Each query inserts its value, then selects the kth largest current element; consecutive k values differ by less than ten.','Return p after every sequential update modulo 1,000,000,007.'],[(([[2],4,[[3,1],[1,2]]]),'The selected exponents are three and two, so the running powers are 64 and 4096.'),(([[7,5],6,[[4,3],[7,2]]]),'Rebalancing around k selects four for the first query and seven for the second.')],P_CASES,POWER_HEAPS,[POWER_HEAPS.replace('value>=upper[0]','value<=upper[0]'),POWER_HEAPS.replace('chosen=upper[0]','chosen=max(upper)')],['Places new values on the wrong side of the kth-largest boundary.','Uses the largest retained value rather than the kth largest.'],power_oracle,random_power,lesson('Keep exactly k largest values in one heap after each query.','Use a min-heap for those k values and a max-heap for everything smaller.','Insert relative to the current boundary, then move heap roots until the upper heap has the new requested size k.','The upper minimum is the kth largest; the small change in consecutive k values keeps rebalancing limited.'),'O((n+q+d)log(n+q))','O(n+q)',6),
    3944: entry('minimum_modulo_alternating_operations',[('nums','list[int]'),('k','int')],'int',['arrays','sorting','modular arithmetic'],['nums is nonempty and k is at least two.','One operation adds or subtracts one from one element; residues wrap modulo k.','Choose distinct target residues for even and odd indices and minimize all operations.'],[(([[1,4,2,8],3]),'Moving the odd-index value four to residue two and the even-index value two to residue one costs two operations total.'),(([[1,1,1],2]),'One parity can stay at residue one while the other moves to residue zero, costing one operation.')],M_CASES,MODULO,[MODULO.replace('first if first!=residue else second','first'),LINEAR_MODULO],['Allows even and odd positions to choose the same target residue.','Uses straight residue distance and misses cheaper wraparound moves.'],modulo_oracle,random_modulo,lesson('Changing an integer residue has circular distance min(|a-b|,k-|a-b|).','For one parity, represent every residue by its unique shifted copy inside a length-k window around each target.','Sorted shifted residues and prefix sums compute every target cost in O(k log n).','Combine each even target with the cheapest odd target having a different residue; only the two cheapest odd choices are needed.'),'O(n log n+k log n)','O(n+k)',8),
}

BATCH[3933]['sample_contract_adapter'] = {
    'source_sample': 'Input matrix = [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,2,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]] → Output 1 ' + '\u200b' * 21 + '.',
    'arguments': [[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,2,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]],
    'expected': 1,
    'reason': 'The workbook output contains zero-width formatting characters after the integer; the adapter preserves the stated matrix and result while removing that invisible markup.',
}
