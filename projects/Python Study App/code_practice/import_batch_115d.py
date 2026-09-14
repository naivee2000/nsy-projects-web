"""Final reviewed group of workbook batch 115."""
from bisect import bisect_left
from itertools import combinations
from .import_batch_055 import entry
MOD=1_000_000_007

def subarrays_o(a):
 nums=a[0];return sum(sum(1 if x else -1 for x in nums[i:j])>0 for i in range(len(nums)) for j in range(i+1,len(nums)+1))%MOD
def two_o(a):
 sets=list(map(set,a));return sorted((sets[0]&sets[1])|(sets[0]&sets[2])|(sets[1]&sets[2]))
def grid_o(a):
 grid,x=a;values=[v for row in grid for v in row]
 if any((v-values[0])%x for v in values):return -1
 return min(sum(abs(v-target)//x for v in values) for target in values)
def partition_o(a):
 nums=a[0];half=len(nums)//2;total=sum(nums)
 return min(abs(total-2*sum(nums[i] for i in ids)) for ids in combinations(range(len(nums)),half))
def seats_o(a):
 seats,students=a
 return min(sum(abs(seats[i]-students[j]) for i,j in enumerate(order)) for order in __import__('itertools').permutations(range(len(students))))
def rsub(r):return [[r.randint(0,1) for _ in range(r.randint(1,40))]]
def rtwo(r):return [[r.randint(1,20) for _ in range(r.randint(1,15))],[r.randint(1,20) for _ in range(r.randint(1,15))],[r.randint(1,20) for _ in range(r.randint(1,15))]]
def rgrid(r):
 rows,cols=r.randint(1,5),r.randint(1,5);return [[[r.randint(1,30) for _ in range(cols)] for _ in range(rows)],r.randint(1,8)]
def rpartition(r):
 half=r.randint(1,8);return [[r.randint(-30,30) for _ in range(2*half)]]
def rseats(r):
 n=r.randint(1,7);return [r.sample(range(1,30),n),r.sample(range(1,30),n)]

SUBARRAYS='''\
def count_more_ones_subarrays(nums):
    mod=1_000_000_007;n=len(nums);tree=[0]*(2*n+3);offset=n+1
    def add(index):
        index+=offset
        while index<len(tree):tree[index]+=1;index+=index&-index
    def query(index):
        index+=offset;total=0
        while index>0:total+=tree[index];index-=index&-index
        return total
    prefix=answer=0;add(0)
    for value in nums:
        prefix+=1 if value else -1
        answer=(answer+query(prefix-1))%mod;add(prefix)
    return answer
'''
TWO='''\
def values_in_at_least_two(nums1,nums2,nums3):
    first,second,third=set(nums1),set(nums2),set(nums3)
    return list((first&second)|(first&third)|(second&third))
'''
GRID='''\
def minimum_univalue_grid_operations(grid,x):
    values=sorted(value for row in grid for value in row)
    if any((value-values[0])%x for value in values):return -1
    median=values[len(values)//2]
    return sum(abs(value-median)//x for value in values)
'''
PARTITION='''\
def minimum_equal_size_partition_difference(nums):
    from bisect import bisect_left
    n=len(nums)//2;left=nums[:n];right=nums[n:];total=sum(nums)
    left_sums=[[] for _ in range(n+1)];right_sums=[[] for _ in range(n+1)]
    for mask in range(1<<n):
        count=mask.bit_count()
        left_sums[count].append(sum(left[i] for i in range(n) if mask>>i&1))
        right_sums[count].append(sum(right[i] for i in range(n) if mask>>i&1))
    answer=float('inf')
    for count in range(n+1):
        candidates=sorted(right_sums[n-count])
        for value in left_sums[count]:
            target=total/2-value;at=bisect_left(candidates,target)
            for index in (at-1,at):
                if 0<=index<len(candidates):answer=min(answer,abs(total-2*(value+candidates[index])))
    return answer
'''
SEATS='''\
def minimum_seating_moves(seats,students):
    seats=sorted(seats);students=sorted(students)
    return sum(abs(seat-student) for seat,student in zip(seats,students))
'''
def L(*x):return list(x)
BATCH={
2031:entry('count_more_ones_subarrays',[('nums','list[int]')],'int',['prefix sums','Fenwick tree','counting'],['nums has 1 through 100000 binary values.','Count contiguous subarrays containing strictly more ones than zeros.','Return the count modulo 1000000007.'],[([[0,1,1,0,1]],'Nine contiguous subarrays have a positive ones-minus-zeros balance.'),([[0]],'The only subarray has more zeros, so the count is zero.')],[[x] for x in [[1],[0],[0,1],[1,0],[1,1],[0,0],[0,1,1,0,1],[1,0,1],[0,1,0],[1,1,0,0],[1,1,1],[0,0,1,1,1],[1,0,0,1,1],[0,1,1,1,0]]],SUBARRAYS,[SUBARRAYS.replace('query(prefix-1)','query(prefix)'),SUBARRAYS.replace('1 if value else -1','1 if value else 0')],['Counts equal-balance subarrays even though ones must be strictly more numerous.','Treats zero as neutral instead of contributing negative one.'],subarrays_o,rsub,L('Map one to +1 and zero to -1; a subarray qualifies when its ending prefix is greater than its starting prefix.','Maintain frequencies of earlier prefix sums in a Fenwick tree and query how many are strictly smaller.','Seed prefix zero; for each new prefix add query(prefix-1), then insert it.','Every subarray corresponds to one ordered prefix pair, and strict prefix inequality is exactly positive balance.'),'O(n log n)','O(n)',6),
2032:entry('values_in_at_least_two',[('nums1','list[int]'),('nums2','list[int]'),('nums3','list[int]')],'list[int]',['sets','arrays'],['Each input has 1 through 100 integers.','Return each distinct value occurring in at least two of the three arrays.','Output order does not matter.'],[([[1,1,3,2],[2,3],[3]],'Values two and three each occur in at least two arrays.'),([[3,1],[2,3],[1,2]],'All three values occur in exactly two arrays.')],[[a,b,c] for a,b,c in [([1],[1],[2]),([1],[2],[3]),([1],[1],[1]),([1,1],[1],[2]),([1,2],[2,3],[3,4]),([3,1],[2,3],[1,2]),([1,2,3],[4,5],[6,7]),([5],[5,6],[6]),([1,1,1],[2,2],[1,2]),([10,20],[20,30],[30,10]),([0],[0],[0]),([-1,2],[2,3],[-1,4]),([7,8,9],[8],[9]),([1,4],[2,4],[3,4])]],TWO,[TWO.replace('|(second&third)',''),TWO.replace('set(nums3)','set()')],['Omits values appearing only in the second and third arrays.','Ignores the third array entirely.'],two_o,rtwo,L('Duplicates inside one array must not count as multiple-array appearances.','Convert each array to a set and union the three pairwise intersections.','Return (A&B)|(A&C)|(B&C).','A value belongs to the union exactly when at least one pair of input sets contains it, which is equivalent to appearing in at least two arrays.'),'O(total input)','O(unique values)',3),
2033:entry('minimum_univalue_grid_operations',[('grid','list[list[int]]'),('x','int')],'int',['matrices','sorting','median'],['grid is nonempty with at most 100000 cells and x is positive.','One operation adds or subtracts x from one cell.','Return the minimum operations to make every cell equal, or -1 if impossible.'],[([[[2,4],[6,8]],2],'Choosing four or six as the target costs four total two-unit moves.'),([[[1,2],[3,4]],2],'The values have different remainders modulo two, so equality is impossible.')],[[g,x] for g,x in [([[1]],1),([[2,4],[6,8]],2),([[1,2],[3,4]],2),([[1,1],[1,1]],3),([[1,3,5]],2),([[2,2,8]],3),([[0,10]],5),([[1,4,7],[10,13,16]],3),([[5,9],[13,17]],4),([[2,5],[8,11]],3),([[1,7]],4),([[10,4,7]],3),([[6,6,12,18]],6),([[3,8,13],[18,23,28]],5)]],GRID,[GRID.replace('values[len(values)//2]','values[0]'),GRID.replace('%x','%(x+1)')],['Targets the smallest value rather than a median and can use extra moves.','Tests congruence modulo x+1 instead of the permitted step x.'],grid_o,rgrid,L('Adding or subtracting x preserves each value’s remainder modulo x, so differing remainders make the task impossible.','After scaling congruent values by x, minimizing absolute distance is a median problem.','Sort values, choose the median, and sum abs(value-median)//x.','The median minimizes total L1 distance, and congruence guarantees every quotient represents an attainable integer number of operations.'),'O(cells log cells)','O(cells)',5),
2035:entry('minimum_equal_size_partition_difference',[('nums','list[int]')],'int',['meet-in-the-middle','binary search','bitmasks'],['nums has 2n elements with n at most 15; values may be negative.','Split all elements into two groups of exactly n elements.','Return the minimum absolute difference between group sums.'],[([[3,9,7,3]],'Splitting [3,9] and [7,3] gives sums twelve and ten, difference two.'),([[-36,36]],'Each group receives one value, producing absolute difference seventy-two.')],[[x] for x in [[1,1],[1,2],[3,9,7,3],[-36,36],[2,-1,0,4,-2,-9],[1,2,3,4],[1,-1,1,-1],[10,20,-10,-20],[5,5,5,5,5,5],[-3,-2,-1,1,2,3],[100,-100,50,-50],[7,3,2,5,8,1],[0,0,0,0],[9,-4,6,-8,3,-2]]],PARTITION,[PARTITION.replace('right_sums[n-count]','right_sums[count]'),PARTITION.replace('target=total/2-value','target=total-value')],['Chooses the same subset size from each half instead of complementary sizes totaling n.','Searches near the full remaining total instead of half the total needed to balance groups.'],partition_o,rpartition,L('Enumerating all 2^(2n) subsets is too large, but each half has at most fifteen elements.','Group subset sums of each half by chosen count; pair complementary counts and binary-search near half the total.','For each left sum using c items, search sorted right sums using n-c items near total/2-left.','Every legal n-item group splits into one complementary-count pair, and the closest combined sum to half the total minimizes |total-2*chosen|.'),'O(n*2^n log 2^n)','O(2^n)',8),
2037:entry('minimum_seating_moves',[('seats','list[int]'),('students','list[int]')],'int',['sorting','greedy'],['seats and students have equal length up to 100 with integer positions.','Moving one student one position costs one move; every seat receives exactly one student.','Return the minimum total moves.'],[([[3,1,5],[2,7,4]],'After sorting, the paired distances are one, one, and two, totaling four.'),([[4,1,5,9],[1,3,2,6]],'Sorted order matching gives total moves seven.')],[[s,t] for s,t in [([1],[1]),([1],[5]),([3,1,5],[2,7,4]),([4,1,5,9],[1,3,2,6]),([1,2],[2,1]),([1,10],[4,7]),([5,5],[1,9]),([1,3,5],[2,4,6]),([10,20,30],[30,20,10]),([2,2,8],[1,5,9]),([0,100],[50,51]),([7,3,9,1],[2,4,6,8]),([1,1,1],[2,2,2]),([5,10,15],[1,11,20])]],SEATS,[SEATS.replace('students=sorted(students)','students=sorted(students,reverse=True)'),SEATS.replace('abs(seat-student)','seat-student')],['Pairs seats with students in opposite orders, creating avoidable crossing assignments.','Omits absolute value and lets movements in opposite directions cancel.'],seats_o,rseats,L('On a line, crossing two assignments can be uncrossed without increasing total distance.','Sort both position lists and pair them by rank.','Return sum(abs(sorted_seats[i]-sorted_students[i])).','The exchange inequality |a-d|+|b-c| >= |a-c|+|b-d| for a<=b and c<=d removes crossings until the sorted matching remains.'),'O(n log n)','O(n)',3)
}
BATCH[2032]['comparator']='unordered'
BATCH[2035]['wrong'][1]=PARTITION.replace('target=total/2-value','target=total/2+value')
BATCH[2035]['wrong_reasons'][1]='Adds the left-half sum when locating its complement instead of subtracting it.'
