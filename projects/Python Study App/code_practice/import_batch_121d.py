"""Fourth slice of workbook batch 121."""

from collections import deque

from .import_batch_055 import entry


def grid_mask(grid):
    columns = len(grid[0])
    return sum(value << (row * columns + column) for row, line in enumerate(grid) for column, value in enumerate(line))


def remove_oracle(args):
    grid = args[0]
    rows, columns = len(grid), len(grid[0])
    start = grid_mask(grid)
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        mask, distance = queue.popleft()
        if mask == 0:
            return distance
        for row in range(rows):
            for column in range(columns):
                bit = row * columns + column
                if not (mask >> bit) & 1:
                    continue
                cleared = mask
                for other in range(columns):
                    cleared &= ~(1 << (row * columns + other))
                for other in range(rows):
                    cleared &= ~(1 << (other * columns + column))
                if cleared not in seen:
                    seen.add(cleared)
                    queue.append((cleared, distance + 1))


def random_remove(rng):
    rows, columns = rng.randint(1, 4), rng.randint(1, 4)
    return [[[rng.randrange(2) for _ in range(columns)] for _ in range(rows)]]


def divisible_oracle(args):
    nums, k = args
    return sum(nums[i] == nums[j] and i * j % k == 0 for i in range(len(nums)) for j in range(i + 1, len(nums)))


def random_divisible(rng):
    return [[rng.randint(1, 8) for _ in range(rng.randint(1, 30))], rng.randint(1, 12)]


def three_oracle(args):
    num = args[0]
    if num % 3:
        return []
    middle = num // 3
    return [middle - 1, middle, middle + 1]


def random_three(rng):
    return [rng.randint(-100_000, 100_000)]


def triplets_oracle(args):
    first, second = args
    position = {value: index for index, value in enumerate(second)}
    return sum(
        position[first[i]] < position[first[j]] < position[first[k]]
        for i in range(len(first))
        for j in range(i + 1, len(first))
        for k in range(j + 1, len(first))
    )


def random_triplets(rng):
    n = rng.randint(3, 9)
    first = list(range(n))
    second = list(range(n))
    rng.shuffle(first)
    rng.shuffle(second)
    return [first, second]


def even_oracle(args):
    return sum(sum(map(int, str(value))) % 2 == 0 for value in range(1, args[0] + 1))


def random_even(rng):
    return [rng.randint(1, 1000)]


REMOVE = '''\
def minimum_row_column_clear_operations(grid):
    from functools import lru_cache
    rows,columns=len(grid),len(grid[0])
    start=sum(value<<(row*columns+column) for row,line in enumerate(grid) for column,value in enumerate(line))
    @lru_cache(None)
    def search(mask):
        if mask==0:return 0
        answer=rows*columns
        for row in range(rows):
            for column in range(columns):
                bit=row*columns+column
                if not (mask>>bit)&1:continue
                cleared=mask
                for other in range(columns):cleared&=~(1<<(row*columns+other))
                for other in range(rows):cleared&=~(1<<(other*columns+column))
                answer=min(answer,1+search(cleared))
        return answer
    return search(start)
'''

DIVISIBLE = '''\
def count_equal_index_product_pairs(nums,k):
    answer=0
    for right in range(len(nums)):
        for left in range(right):
            if nums[left]==nums[right] and left*right%k==0:answer+=1
    return answer
'''

THREE = '''\
def three_consecutive_sum(num):
    if num%3:return []
    middle=num//3
    return [middle-1,middle,middle+1]
'''

TRIPLETS = '''\
def count_ordered_permutation_triplets(nums1,nums2):
    position={value:index for index,value in enumerate(nums2)}
    order=[position[value] for value in nums1]
    n=len(order)
    tree=[0]*(n+1)
    def add(index):
        index+=1
        while index<=n:tree[index]+=1;index+=index&-index
    def query(index):
        total=0
        while index:total+=tree[index];index-=index&-index
        return total
    left=[]
    for value in order:left.append(query(value));add(value)
    tree=[0]*(n+1);answer=0
    for index in range(n-1,-1,-1):
        greater=(n-1-index)-query(order[index]+1)
        answer+=left[index]*greater;add(order[index])
    return answer
'''

EVEN = '''\
def count_even_digit_sums(num):
    digit_sum=sum(map(int,str(num)))
    return num//2 if digit_sum%2==0 else (num-1)//2
'''


BATCH = {
    2174: entry('minimum_row_column_clear_operations',[('grid','list[list[int]]')],'int',['matrices','bit masks','breadth first search'],['In one operation choose a cell currently equal to one.','Set every cell in that chosen cell’s row and column to zero.','Return the minimum operations needed to remove every one.'],[([[[1,1,1],[1,1,1],[0,1,0]]],'Choosing two well-placed one cells clears all rows and columns containing ones, so the minimum is 2.'),([[[0,0],[0,0]]],'No operation is needed when the grid already contains only zeros.')],[[g] for g in [[[0]],[[1]],[[1,1]],[[1],[1]],[[1,0],[0,1]],[[1,1],[1,1]],[[1,0],[1,0]],[[0,1],[1,1]],[[1,1,1],[1,1,1],[0,1,0]],[[1,0,1],[0,1,0],[1,0,1]],[[0,0],[0,0]],[[1,0,0],[0,1,0],[0,0,1]],[[1,1,0],[0,1,1]],[[0,1,0],[1,1,1],[0,1,0]]]],REMOVE,[REMOVE.replace('for row in range(rows):','for row in range(rows-1):',1),REMOVE.replace('for other in range(rows):cleared','for other in []:cleared')],['Never considers choosing a one from the final row.','Clears the selected row but never clears its selected column.'],remove_oracle,random_remove,['The grid is small enough to represent every remaining one as a bit mask.','An operation deterministically clears one full row and one full column; memoize the best result for each mask.','For every current one, clear its row and column in a copied mask and recurse with cost one.','Every legal first operation is tried, and the remaining problem depends only on the resulting mask, so the recurrence contains every possible operation sequence.'],'O(2^(m*n)*m*n*(m+n))','O(2^(m*n))',7),
    2176: entry('count_equal_index_product_pairs',[('nums','list[int]'),('k','int')],'int',['arrays','enumeration'],['Count index pairs with 0 <= i < j < len(nums).','The values nums[i] and nums[j] must be equal.','The index product i*j, not the value product, must be divisible by k.'],[([[3,1,2,2,2,1,3],2],'Four equal-value pairs also have an index product divisible by two.'),([[1,2,3,4],1],'Every index product is divisible by one, but no values match, so return zero.')],[[a,k] for a,k in [([1],1),([1,1],1),([1,1],2),([1,2,1],2),([3,1,2,2,2,1,3],2),([1,2,3,4],1),([5,5,5],3),([2,2,2,2],4),([1,2,1,2,1],3),([0,0,0],2),([7,8,7,8,7,8],5),([1,1,2,2,1,2],6),([9,9,9,9,9],7),([3,4,3,4,3],2)]],DIVISIBLE,[DIVISIBLE.replace('left*right%k==0','(left+right)%k==0'),DIVISIBLE.replace('nums[left]==nums[right]','nums[left]!=nums[right]')],['Checks the sum of indices instead of their product.','Counts unequal values instead of equal values.'],divisible_oracle,random_divisible,['The constraints allow checking every index pair directly.','Use nested indices and test both required predicates.','For each right index, scan all earlier left indices and increment when values match and left*right is divisible by k.','Every valid ordered index pair i<j appears exactly once in the nested loops.'],'O(n^2)','O(1)',3),
    2177: entry('three_consecutive_sum',[('num','int')],'list[int]',['math','simulation'],['Return three integers x-1, x, x+1 in increasing order whose sum is num.','Negative integers and zero are allowed.','Return an empty list when no such integer middle value exists.'],[([33],'The middle value is 11, giving consecutive integers [10,11,12].'),([4],'Four is not divisible by three, so no integer middle value exists.')],[[x] for x in [-100,-99,-3,-2,-1,0,1,2,3,4,6,33,999,1000,-999]],THREE,[THREE.replace('num%3','num%2'),THREE.replace('middle-1,middle,middle+1','middle,middle+1,middle+2')],['Tests divisibility by two rather than three.','Returns three consecutive values whose middle is shifted upward.'],three_oracle,random_three,['Three consecutive integers centered at x always sum to 3*x.','A solution exists exactly when num is divisible by three.','If num%3 is nonzero return []; otherwise return [num//3-1, num//3, num//3+1].','The outer terms cancel around the middle, so the sum is three times the middle and the condition is both necessary and sufficient.'],'O(1)','O(1)',5),
    2179: entry('count_ordered_permutation_triplets',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','fenwick trees','order statistics'],['Both arrays are permutations of 0 through n-1.','A value triplet must appear in increasing index order in both permutations.','Return the number of such triplets; the result may exceed 32-bit range.'],[([[2,0,1,3],[0,1,2,3]],'Only values 0,1,3 preserve increasing order in both arrays, so return 1.'),([[4,0,1,3,2],[4,1,0,2,3]],'Exactly four value triplets have increasing positions in both permutations.')],[[a,b] for a,b in [([0,1,2],[0,1,2]),([0,1,2],[2,1,0]),([2,0,1,3],[0,1,2,3]),([0,1,2,3],[0,1,2,3]),([3,2,1,0],[0,1,2,3]),([4,0,1,3,2],[4,1,0,2,3]),([1,0,2,3],[0,1,2,3]),([0,2,1,3],[0,1,2,3]),([1,2,3,0],[0,1,2,3]),([0,1,2,3,4],[4,3,2,1,0]),([5,0,2,4,1,3],[0,1,2,3,4,5]),([2,5,1,4,0,3],[3,0,4,1,5,2]),([6,5,4,3,2,1,0],[6,5,4,3,2,1,0]),([3,0,4,1,5,2],[0,1,2,3,4,5])]],TRIPLETS,[TRIPLETS.replace('query(value)','query(max(0,value-1))',1),TRIPLETS.replace('(n-1-index)-query(order[index]+1)','(n-index)-query(order[index]+1)')],['Omits the immediately smaller rank from the left-side Fenwick prefix.','Overcounts the number of elements to the right by one.'],triplets_oracle,random_triplets,['Map nums1 into the position order imposed by nums2; the task becomes counting increasing subsequences of length three.','For each middle element, count smaller values to its left and greater values to its right with Fenwick trees.','Scan left-to-right for smaller counts, then right-to-left for greater counts; sum their products.','Every increasing triplet has a unique middle. The product chooses its valid left and right endpoints independently, counting each triplet once.'],'O(n log n)','O(n)',8),
    2180: entry('count_even_digit_sums',[('num','int')],'int',['math','digit sums'],['Count positive integers x with 1 <= x <= num.','A number qualifies when the sum of its decimal digits is even.','num is at least one and at most one thousand.'],[([4],'Among 1 through 4, only 2 and 4 have even digit sums, so return 2.'),([30],'Fourteen positive integers through 30 have an even digit sum.')],[[x] for x in [1,2,3,4,9,10,11,19,20,29,30,99,100,999,1000]],EVEN,[EVEN.replace('digit_sum%2==0','digit_sum%2!=0'),EVEN.replace('num//2','(num+1)//2')],['Uses the odd digit-sum branch for the endpoint adjustment.','Rounds the even half upward regardless of the endpoint digit sum.'],even_oracle,random_even,['Digit-sum parity alternates between neighboring numbers except across carries, but paired counts remain balanced.','Exactly half of 1..num qualify, with the final unpaired endpoint included only when its digit sum is even.','Compute the digit sum of num; return num//2 for even parity and (num-1)//2 otherwise.','Pairing consecutive endpoints yields one even digit-sum member per pair; the parity of num resolves the lone endpoint when needed.'],'O(log num)','O(log num)',3),
}
