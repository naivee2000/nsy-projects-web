"""Equalization, Hamming space, tagged squares, balanced partitions, and big products."""
from collections import Counter

from .import_batch_055 import entry


def equalize_oracle(args):
    nums, single, pair = args; maximum = max(nums); upper = 2 * maximum - min(nums) + 6; best = 10**30
    for target in range(maximum, upper + 1):
        deficits = [target - value for value in nums]; total = sum(deficits)
        paired = (min(total // 2, total - max(deficits))
                  if len(nums) > 1 and pair < 2 * single else 0)
        best = min(best, paired * pair + (total - 2 * paired) * single)
    return best % 1_000_000_007


def random_equalize(rng):
    return [[rng.randint(0, 15) for _ in range(rng.randint(1, 8))], rng.randint(1, 12), rng.randint(1, 20)]


def hamming_oracle(args):
    nums, _ = args
    return [max((value ^ other).bit_count() for other in nums) for value in nums]


def random_hamming(rng):
    bits = rng.randint(1, 7)
    return [[rng.randrange(1 << bits) for _ in range(rng.randint(1, 12))], bits]


def square_oracle(args):
    points, tags = args; answer = 0
    for distance in sorted({max(abs(x), abs(y)) for x, y in points}):
        selected = [tags[index] for index, (x, y) in enumerate(points) if max(abs(x), abs(y)) <= distance]
        if len(selected) == len(set(selected)):answer = max(answer, len(selected))
    return answer


def random_square(rng):
    size = rng.randint(1, 12)
    return [[[rng.randint(-10, 10), rng.randint(-10, 10)] for _ in range(size)],
            ''.join(rng.choice('abcdef') for _ in range(size))]


def partition_oracle(args):
    text = args[0]; best = len(text)
    def search(index, groups):
        nonlocal best
        if index == len(text):best = min(best, groups); return
        counts = Counter()
        for end in range(index, len(text)):
            counts[text[end]] += 1
            if len(set(counts.values())) == 1:search(end + 1, groups + 1)
    search(0, 0); return best


def random_partition(rng):
    return [''.join(rng.choice('abcde') for _ in range(rng.randint(1, 14)))]


def products_oracle(args):
    queries = args[0]; needed = max(right for _, right, _ in queries) + 1; exponents = []; value = 1
    while len(exponents) < needed:
        for bit in range(value.bit_length()):
            if value >> bit & 1:exponents.append(bit)
        value += 1
    return [pow(2, sum(exponents[left:right+1]), mod) for left, right, mod in queries]


def random_products(rng):
    queries = []
    for _ in range(rng.randint(1, 6)):
        left = rng.randint(0, 80); right = rng.randint(left, 120); queries.append([left, right, rng.randint(2, 100)])
    return [queries]


EQUALIZE = '''def minimum_array_equalization_cost(nums,cost1,cost2):
    modulo=1000000007;size=len(nums);maximum=max(nums);total=sum(nums);minimum=min(nums)
    if size<=2 or cost2>=2*cost1:return sum(maximum-value for value in nums)*cost1%modulo
    boundary=max(maximum,(total-2*minimum+size-3)//(size-2))
    candidates={maximum}
    for target in range(max(maximum,boundary-2),boundary+3):candidates.add(target)
    answer=10**40
    for target in candidates:
        deficit=size*target-total;largest=target-minimum
        pairs=min(deficit//2,deficit-largest)
        answer=min(answer,pairs*cost2+(deficit-2*pairs)*cost1)
    return answer%modulo
'''


HAMMING = '''def maximum_hamming_distances(nums,m):
    from collections import deque
    size=1<<m;distance=[-1]*size;queue=deque()
    for value in set(nums):distance[value]=0;queue.append(value)
    while queue:
        value=queue.popleft()
        for bit in range(m):
            neighbor=value^(1<<bit)
            if distance[neighbor]<0:distance[neighbor]=distance[value]+1;queue.append(neighbor)
    mask=size-1
    return [m-distance[value^mask] for value in nums]
'''


SQUARE = '''def maximum_uniquely_tagged_square_points(points,s):
    groups={}
    for index,(x,y) in enumerate(points):groups.setdefault(max(abs(x),abs(y)),[]).append(index)
    seen=set();answer=0
    for distance in sorted(groups):
        tags=[s[index] for index in groups[distance]]
        if len(tags)!=len(set(tags)) or any(tag in seen for tag in tags):break
        seen.update(tags);answer+=len(tags)
    return answer
'''


PARTITION = '''def minimum_balanced_substring_partition(s):
    from functools import lru_cache
    @lru_cache(None)
    def search(index):
        if index==len(s):return 0
        counts={};answer=len(s)-index
        for end in range(index,len(s)):
            counts[s[end]]=counts.get(s[end],0)+1
            if len(set(counts.values()))==1:answer=min(answer,1+search(end+1))
        return answer
    return search(0)
'''


PRODUCTS = '''def big_array_range_products(queries):
    width=60;counts=[0]*(width+1);sums=[0]*(width+1);power=1
    for bit in range(1,width+1):
        counts[bit]=counts[bit-1]*2+power
        sums[bit]=sums[bit-1]*2+power*(bit-1)
        power*=2
    def through_number(value):
        count=total=0
        while value:
            bit=value.bit_length()-1
            count+=counts[bit];total+=sums[bit];value-=1<<bit
            total+=(value+1)*bit;count+=value+1
        return count,total
    def prefix(length):
        low,high=0,1<<width
        while low<high:
            middle=(low+high+1)//2
            if through_number(middle)[0]<length:low=middle
            else:high=middle-1
        count,total=through_number(low);remaining=length-count;value=low+1
        for _ in range(remaining):
            bit=value&-value;total+=bit.bit_length()-1;value-=bit
        return total
    return [pow(2,prefix(right+1)-prefix(left),mod) for left,right,mod in queries]
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3139: entry('minimum_array_equalization_cost',[('nums','list[int]'),('cost1','int'),('cost2','int')],'int',['greedy','math','arrays'],['nums is nonempty and contains nonnegative integers; both operation costs are positive.','A single operation increments one element; a pair operation increments two different elements.','Make every value equal at minimum cost and return that cost modulo 1,000,000,007.'],[([[4,1],5,2],'With two elements every increment pair preserves their difference, so raise one by three single increments for cost fifteen.'),([[1,2,3],4,3],'Raise one and two together once, then raise the former one once more, reaching three for cost seven.')],[[a,c1,c2] for a,c1,c2 in [([1],5,2),([4,1],5,2),([1,2,3],4,3),([1,1,1],2,1),([0,10,10],10,1),([1,5,5],2,3),([1,2,10],7,4),([3,3,9,9],5,6),([0,0,5],3,2),([2,8,9,10],4,5),([1,1,10,10,10],9,2),([5,2,7,1],1,10),([100,1,1],8,3),([4,6,8,10,12],5,7)]],EQUALIZE,["""def minimum_array_equalization_cost(nums,cost1,cost2):
    target=max(nums);return sum(target-value for value in nums)*cost1%1000000007
""",EQUALIZE.replace('pairs=min(deficit//2,deficit-largest)','pairs=deficit//2')],['Never considers pair increments or a target above the current maximum.','Pairs increments from the same dominant-deficit element, violating the distinct-index rule.'],equalize_oracle,random_equalize,lesson('For a fixed target, the maximum legal pair count is limited by half the total deficit and by deficit outside the largest-deficit index.','Evaluate the current maximum and targets near the point where the largest deficit stops dominating; use singles when pairing is not cheaper.','pairs=min(totalDeficit//2,totalDeficit-largestDeficit); cost pairs and remaining singles; test the balance boundary and adjacent parities.','Fixed-target pairing is maximal when cheaper; cost is linear before balance and increasing after balance apart from parity, so the boundary neighborhood contains an optimum.'),'O(n)','O(1)',8),
3141: entry('maximum_hamming_distances',[('nums','list[int]'),('m','int')],'list[int]',['bit manipulation','breadth-first search','hypercubes'],['m is positive and every nums value lies from zero through 2^m-1.','For each occurrence, find the maximum Hamming distance to any value occurring in nums; comparing with itself is allowed.','Return the distances in original input order.'],[([[9,12,9,11],4],'The farthest listed values differ from 9 in two bits and from 12 or 11 in three bits, giving [2,3,2,3].'),([[0,7],3],'Zero and seven differ in all three bits, so both answers are three.')],[[a,m] for a,m in [([0],1),([0,1],1),([0,7],3),([1,2],2),([9,12,9,11],4),([0,15],4),([3,3,3],3),([1,3,7],3),([2,5,6],3),([0,1,2,4],3),([7,8,9],4),([5,10,15,0],4),([1,2,4,8],4),([31,16,7],5)]],HAMMING,[HAMMING.replace('value^mask','value'),HAMMING.replace('m-distance[value^mask]','distance[value^mask]')],['Measures distance to the input set from the value itself, yielding zero instead of using its complement.','Returns the complement’s minimum distance directly instead of converting it to maximum Hamming distance.'],hamming_oracle,random_hamming,lesson('Distance(x,y)=m-distance(complement(x),y), so maximizing distance to the input set equals m minus the complement’s nearest-set distance.','Multi-source BFS from every input value across the m-bit hypercube computes all nearest distances.','Seed distinct nums at distance zero; flip each bit in BFS; answer m-dist[x xor allOnes].','Hypercube path length is Hamming distance, and complementing x converts agreement with x into disagreement bit by bit.'),'O(m*2^m)','O(2^m)',8),
3143: entry('maximum_uniquely_tagged_square_points',[('points','list[list[int]]'),('s','str')],'int',['geometry','sorting','hash sets'],['points and s have equal nonzero length, with one tag character per point.','A centered axis-aligned square of radius d contains exactly points with max(abs(x),abs(y))≤d.','Maximize contained points subject to all contained tags being distinct.'],[([[[2,2],[-1,-2],[-4,4],[-3,1],[3,-3]],'abdca'],'Radius two contains the first two points with distinct tags; the next distance introduces a repeated a, so the maximum is two.'),([[[1,0],[0,1],[2,2]],'abc'],'All three tags are distinct, so a radius-two square contains all points.')],[[p,s] for p,s in [([[0,0]],'a'),([[1,0],[0,1]],'ab'),([[1,0],[0,1]],'aa'),([[2,2],[-1,-2],[-4,4],[-3,1],[3,-3]],'abdca'),([[1,0],[0,1],[2,2]],'abc'),([[1,1],[2,2],[3,3]],'aba'),([[1,2],[-2,1],[3,0]],'xyz'),([[0,0],[0,0]],'ab'),([[0,0],[1,1]],'aa'),([[5,0],[0,5],[4,4]],'abc'),([[1,1],[1,-1],[-1,1],[-1,-1]],'abcd'),([[2,0],[3,0],[4,0]],'abb'),([[10,10],[1,9],[9,1]],'qrs'),([[1,0],[2,0],[3,0],[4,0]],'abca')]],SQUARE,[SQUARE.replace('if len(tags)!=len(set(tags)) or any(tag in seen for tag in tags):break','if any(tag in seen for tag in tags):break'),SQUARE.replace('seen.update(tags)','seen=set(tags)')],['Misses duplicate tags introduced together at the same square boundary.','Forgets tags from smaller included distances when processing the next boundary.'],square_oracle,random_square,lesson('All points at the same Chebyshev distance enter a centered square simultaneously.','Group by max absolute coordinate, process distances together, and stop before the first group that duplicates a tag internally or previously seen.','At each sorted distance collect tags; if group has duplicates or intersects seen, return prior count; otherwise add all.','Every possible contained set changes only at a group boundary, and the first duplicate can never be removed by enlarging the square.'),'O(n log n)','O(n)',5),
3144: entry('minimum_balanced_substring_partition',[('s','str')],'int',['dynamic programming','strings','counting'],['s is a nonempty lowercase string.','A substring is balanced when every distinct character appearing in it has the same positive frequency.','Partition all characters into the fewest nonempty balanced contiguous substrings.'],[(['fabccddg'],'One optimal partition is fab, ccdd, g, so the minimum is three.'),(['ababcc'],'All three present characters occur twice, so the whole string is one balanced part.')],[[s] for s in ['a','ab','aa','aba','abab','ababcc','fabccddg','abcabc','aabbb','aaaaab','abacbc','zzxyxy','abcddcba','aabbcccddd']],PARTITION,[PARTITION.replace('len(set(counts.values()))==1','len(set(counts.values()))<=2'),PARTITION.replace('answer=min(answer,1+search(end+1))','answer=1+search(end+1)')],['Accepts substrings having two different positive frequencies.','Overwrites the best partition with the last balanced prefix instead of minimizing all choices.'],partition_oracle,random_partition,lesson('A partition decision depends only on its next start index; every balanced prefix is a valid next edge.','Use suffix DP and enumerate end positions while maintaining character counts.','At start i, extend j; when all positive counts are equal, minimize 1+dp[j+1].','Every valid partition begins with one enumerated balanced prefix, and optimal suffix reuse gives the minimum number of parts.'),'O(n^2*alphabet)','O(n+alphabet)',5),
3145: entry('big_array_range_products',[('queries','list[list[int]]')],'list[int]',['bit manipulation','binary search','prefix sums'],['Each query is [left,right,mod] with 0≤left≤right and mod≥2.','The infinite big array concatenates, for integers 1,2,..., the ascending powers of two corresponding to their set bits.','Return each inclusive range product modulo mod.'],[([[[1,3,7]]],'The indexed elements are 2,1,2, whose product four modulo seven is four.'),([[[0,0,5],[0,4,100]]],'The first element is one; the first five elements 1,2,1,2,4 multiply to sixteen.')],[[q] for q in [[[0,0,2]],[[0,0,5]],[[1,3,7]],[[0,4,100]],[[2,6,11]],[[5,10,97]],[[10,20,1000]],[[0,20,13]],[[30,50,17]],[[7,7,9]],[[1,3,7],[0,4,100]],[[50,100,101]],[[99,120,64]],[[3,15,37]]]],PRODUCTS,[PRODUCTS.replace('prefix(right+1)-prefix(left)','prefix(right)-prefix(left)'),PRODUCTS.replace('pow(2,','pow(4,')],['Treats the inclusive right endpoint as exclusive.','Raises four instead of two to the accumulated set-bit exponent.'],products_oracle,random_products,lesson('Every big-array element is a power of two, so a range product is two raised to the sum of its bit positions.','Compute prefix exponent sums by binary-searching how many set bits occur through an integer and taking a partial next integer.','Precompute counts/sums for complete bit-length blocks; prefix(right+1)-prefix(left) gives the range exponent; modular-power two.','Concatenation order and the partial set-bit scan account for exactly the requested prefix, while exponent addition converts multiplication to subtraction of prefix sums.'),'O(60^2+queries*60^2)','O(60)',8),
}
