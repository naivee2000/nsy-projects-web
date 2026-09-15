"""Maximum windows, divisible triples, canonical groups, polygons, and field squares."""
from itertools import combinations

from .import_batch_055 import entry


def maximum_subarrays_oracle(args):
    nums, k = args; maximum = max(nums); answer = 0
    for left in range(len(nums)):
        for right in range(left, len(nums)):
            answer += nums[left:right + 1].count(maximum) >= k
    return answer


def random_maximum_subarrays(rng):
    nums = [rng.randint(1, 8) for _ in range(rng.randint(1, 20))]
    return [nums, rng.randint(1, len(nums) + 2)]


def triplets_oracle(args):
    nums, divisor = args
    return sum((nums[i] + nums[j] + nums[k]) % divisor == 0
               for i, j, k in combinations(range(len(nums)), 3))


def random_triplets(rng):
    return [[rng.randint(1, 50) for _ in range(rng.randint(1, 16))], rng.randint(1, 15)]


def groups_oracle(args):
    nums, limit = args; nums = sorted(nums); result = []
    for index in range(0, len(nums), 3):
        group = nums[index:index + 3]
        if group[-1] - group[0] > limit:
            return []
        result.append(group)
    return result


def random_groups(rng):
    size = 3 * rng.randint(1, 6)
    return [[rng.randint(1, 30) for _ in range(size)], rng.randint(1, 12)]


def polygon_oracle(args):
    nums = args[0]; answer = -1
    for size in range(3, len(nums) + 1):
        for chosen in combinations(nums, size):
            if 2 * max(chosen) < sum(chosen):
                answer = max(answer, sum(chosen))
    return answer


def random_polygon(rng):
    return [[rng.randint(1, 25) for _ in range(rng.randint(3, 11))]]


def field_oracle(args):
    rows, columns, horizontal, vertical = args
    hs = {b - a for a, b in combinations(sorted([1, rows] + horizontal), 2)}
    vs = {b - a for a, b in combinations(sorted([1, columns] + vertical), 2)}
    side = max(hs & vs, default=0)
    return side * side % 1_000_000_007 if side else -1


def random_field(rng):
    rows, columns = rng.randint(3, 16), rng.randint(3, 16)
    horizontal = rng.sample(range(2, rows), rng.randint(1, rows - 2))
    vertical = rng.sample(range(2, columns), rng.randint(1, columns - 2))
    return [rows, columns, horizontal, vertical]


MAXIMUM_SUBARRAYS = '''def count_subarrays_with_frequent_maximum(nums,k):
    maximum=max(nums);left=occurrences=answer=0
    for value in nums:
        occurrences+=value==maximum
        while occurrences>=k:
            occurrences-=nums[left]==maximum;left+=1
        answer+=left
    return answer
'''


TRIPLETS = '''def count_divisible_triplets(nums,d):
    counts={};answer=0
    for middle in range(len(nums)):
        for right in range(middle+1,len(nums)):
            needed=(-nums[middle]-nums[right])%d
            answer+=counts.get(needed,0)
        remainder=nums[middle]%d;counts[remainder]=counts.get(remainder,0)+1
    return answer
'''


GROUPS = '''def divide_into_bounded_triples(nums,k):
    nums=sorted(nums);answer=[]
    for index in range(0,len(nums),3):
        group=nums[index:index+3]
        if group[-1]-group[0]>k:return []
        answer.append(group)
    return answer
'''


POLYGON = '''def largest_polygon_perimeter(nums):
    nums=sorted(nums);prefix=0;answer=-1
    for value in nums:
        if prefix>value:answer=prefix+value
        prefix+=value
    return answer
'''


FIELD = '''def maximum_square_field_area(m,n,h_fences,v_fences):
    from itertools import combinations
    horizontal={b-a for a,b in combinations(sorted([1,m]+h_fences),2)}
    vertical={b-a for a,b in combinations(sorted([1,n]+v_fences),2)}
    side=max(horizontal&vertical,default=0)
    return side*side%1000000007 if side else -1
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
2962: entry('count_subarrays_with_frequent_maximum',[('nums','list[int]'),('k','int')],'int',['sliding window','arrays','counting'],['nums is nonempty and k is positive.','Use the maximum value of the entire array, not each subarray local maximum.','Count contiguous subarrays containing that value at least k times.'],[([[1,3,2,3,3],2],'Exactly six subarrays include at least two occurrences of the global maximum three.'),([[1,4,2,1],3],'The global maximum four occurs only once, so no subarray reaches three occurrences.')],[[n,k] for n,k in [([1],1),([1],2),([1,1],1),([1,1],2),([1,2,3],1),([1,2,3],2),([3,1,3],2),([2,2,1,2],2),([5,1,5,1,5],3),([1,4,4,2,4],2),([9,8,7,9,6],1),([3,3,3,3],3),([1,2,1,2,1],2),([10,1,10,10,2,10],3)]],MAXIMUM_SUBARRAYS,[MAXIMUM_SUBARRAYS.replace('while occurrences>=k','while occurrences>k'),MAXIMUM_SUBARRAYS.replace('answer+=left','answer+=left+1')],['Shrinks only after more than k maxima, counting windows with too few occurrences.','Adds an extra start position for every right endpoint, overcounting invalid windows.'],maximum_subarrays_oracle,random_maximum_subarrays,lesson('After shrinking past the earliest necessary maximum, every start before left forms a valid subarray ending here.','Track maximum occurrences and advance left while the window has at least k, then add left.','For each right value update count; while count>=k remove nums[left] and advance; accumulate left.','The loop leaves exactly the first invalid start at left, so starts zero through left-1—and only those—retain at least k maxima.'),'O(n)','O(1)',5),
2964: entry('count_divisible_triplets',[('nums','list[int]'),('d','int')],'int',['hash maps','arrays','modular arithmetic'],['nums contains positive integers and d is positive.','Count index triples i<j<k whose three values sum to a multiple of d.','Different index choices count separately even when values repeat.'],[([[3,3,4,7,8],5],'Index triples (0,1,2), (0,2,4), and (1,2,4) have sums divisible by five.'),([[3,3,3,3],3],'Every choice of three among four indices sums to nine, producing four triplets.')],[[n,d] for n,d in [([1],1),([1,2],3),([1,2,3],3),([1,2,3],7),([3,3,3,3],6),([1,1,1],1),([1,1,1,1],3),([2,4,6,8],2),([1,2,4,8],5),([5,10,15,20],10),([7,7,14,21,28],7),([9,1,5,3,7],4),([100,200,300,400],6),([2,3,5,7,11,13],5)]],TRIPLETS,[TRIPLETS.replace('(-nums[middle]-nums[right])%d','(nums[middle]+nums[right])%d'),TRIPLETS.replace('range(middle+1,len(nums))','range(middle,len(nums))')],['Looks up the pair remainder rather than its additive inverse.','Allows the middle and right indices to be equal, counting non-triplets.'],triplets_oracle,random_triplets,lesson('For fixed middle and right indices, an earlier value must have one specific remainder.','Count remainders of indices before middle and query the needed complement for every later right index.','Add counts[(-nums[j]-nums[k]) mod d], then insert nums[j] only after processing its right partners.','Delayed insertion enforces i<j, the inner scan enforces j<k, and the remainder complement is equivalent to divisibility.'),'O(n^2)','O(min(n,d))',5),
2966: entry('divide_into_bounded_triples',[('nums','list[int]'),('k','int')],'list[list[int]]',['greedy','sorting','arrays'],['nums has positive length divisible by three and k is positive.','Return the canonical grouping made by sorting nums and taking consecutive triples.','Return an empty list if any triple maximum minus minimum exceeds k.'],[([[1,3,4,8,7,9,3,5,1],2],'Sorting and taking consecutive triples gives [[1,1,3],[3,4,5],[7,8,9]], each with spread at most two.'),([[2,4,2,2,5,2],2],'Any split leaves a triple containing values two and five, so no valid grouping exists.')],[[n,k] for n,k in [([1,1,1],1),([1,2,3],2),([1,2,4],2),([3,2,1],5),([1,1,2,2,3,3],1),([1,2,3,4,5,6],2),([1,2,3,4,5,6],5),([5,5,5,5,5,5],1),([1,10,11,20,21,22],2),([2,3,4,8,9,10],2),([1,1,5,5,9,9],4),([7,3,5,1,9,11,13,15,17],4),([100,101,102],1),([4,8,6,2,10,12],4)]],GROUPS,[GROUPS.replace('>k','>=k'),GROUPS.replace('nums=sorted(nums)','nums=list(nums)')],['Rejects triples whose spread equals the allowed limit.','Groups input order without sorting, missing feasible canonical partitions.'],groups_oracle,random_groups,lesson('In sorted order, the smallest remaining value must be grouped within the next two positions in any feasible partition.','Sort and partition consecutive blocks of three, rejecting any block whose endpoints differ by more than k.','For i=0,3,... take sorted_nums[i:i+3], test last-first, and append.','If a consecutive block fails, its smallest value cannot pair with two later values more closely; if all pass, the blocks directly witness feasibility.'),'O(n log n)','O(n)',5),
2971: entry('largest_polygon_perimeter',[('nums','list[int]')],'int',['greedy','sorting','prefix sums'],['nums contains at least three positive side lengths.','A chosen set forms a polygon exactly when its longest side is strictly less than the sum of the others.','Return the largest obtainable perimeter, or -1 if no subset forms a polygon.'],[([[5,5,5]],'All three sides form a triangle with perimeter fifteen.'),([[1,12,1,2,5,50,3]],'Sides 1,1,2,3,5 form the largest valid polygon, with perimeter twelve.')],[[n] for n in [[1,1,2],[1,1,3],[2,3,4],[5,5,50],[1,2,3,4],[1,2,3,10],[3,3,3,3],[1,1,1,10,10],[2,4,5,9],[6,1,2,3,4],[100,1,1,1,1,1],[7,8,9,20,21],[5,10,12,13,15],[1,2,4,8,16]]],POLYGON,[POLYGON.replace('prefix>value','prefix>=value'),POLYGON.replace('answer=prefix+value','answer=value')],['Allows a degenerate polygon where the longest side equals the other-side sum.','Returns only the longest side instead of the full perimeter.'],polygon_oracle,random_polygon,lesson('After sorting, the prefix before a side is the greatest possible sum of smaller available sides.','Scan in ascending order with a prefix sum; whenever prefix exceeds the current side, record their total.','Maintain prefix; if prefix>value set answer=prefix+value, then include value in prefix.','Adding positive sorted sides only increases perimeter, so the latest valid prefix is optimal; a failed side cannot help without later accumulated sides.'),'O(n log n)','O(n)',5),
2975: entry('maximum_square_field_area',[('m','int'),('n','int'),('h_fences','list[int]'),('v_fences','list[int]')],'int',['hash sets','enumeration','geometry'],['m and n are at least three; interior fence positions are unique and strictly inside their dimension.','Boundary fences at positions one and m or n cannot be removed.','Choose equal horizontal and vertical coordinate gaps; return the largest square area modulo 1,000,000,007, or -1.'],[([4,3,[2,3],[2]],'Both dimensions can expose a gap of two, producing square area four.'),([6,7,[2],[4]],'The available horizontal and vertical coordinate gaps have no common value, so no square is possible.')],[[m,n,h,v] for m,n,h,v in [(3,3,[2],[2]),(3,4,[2],[2]),(4,4,[2],[2]),(5,5,[2,4],[2,4]),(5,6,[2,3],[3,5]),(6,5,[3,5],[2,4]),(7,7,[2,4,6],[3,5]),(8,6,[2,5,7],[2,4]),(10,9,[3,6,8],[2,5,7]),(12,15,[2,4,9],[3,8,12]),(100,100,[25,50,75],[20,40,60,80]),(9,13,[2,4,8],[3,7,10]),(20,17,[5,10,15],[4,8,12,16]),(1000000000,1000000000,[2],[2])]],FIELD,[FIELD.replace('horizontal&vertical','horizontal|vertical'),FIELD.replace('side*side%1000000007','side*side')],['Uses a gap present in either direction instead of requiring the same side length in both.','Forgets to reduce a potentially huge square area modulo 1,000,000,007.'],field_oracle,random_field,lesson('Removing intermediate fences exposes every distance between two retained coordinate lines.','Enumerate all pairwise horizontal and vertical gaps, intersect the sets, and select the largest common gap.','Add immutable boundaries, build distance sets from every pair, take max intersection, square modulo M.','Any square is bounded by two lines in each direction with one common gap, and every shared gap can be realized by removing intervening fences.'),'O(h^2+v^2)','O(h^2+v^2)',5),
}
