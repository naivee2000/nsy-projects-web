"""Second slice of workbook batch 129."""

from .import_batch_055 import entry


def merge_oracle(args):
    totals = {}
    for value, weight in args[0] + args[1]: totals[value] = totals.get(value, 0) + weight
    return [[value, totals[value]] for value in sorted(totals)]


def random_merge(rng):
    values = list(range(1, 16)); rng.shuffle(values); cut = rng.randint(1, 8)
    first_values = values[:cut]; rng.shuffle(values); second_values = values[:rng.randint(1, 8)]
    return [[[v, rng.randint(1, 20)] for v in first_values], [[v, rng.randint(1, 20)] for v in second_values]]


def bad_oracle(args):
    nums = args[0]
    return sum(j - i != nums[j] - nums[i] for i in range(len(nums)) for j in range(i + 1, len(nums)))


def random_bad(rng):
    return [[rng.randint(0, 20) for _ in range(rng.randint(1, 20))]]


def triplet_oracle(args):
    nums, difference = args
    return sum(nums[j] - nums[i] == difference and nums[k] - nums[j] == difference
               for i in range(len(nums)) for j in range(i + 1, len(nums)) for k in range(j + 1, len(nums)))


def random_triplet(rng):
    nums = sorted(rng.sample(range(0, 40), rng.randint(3, 12)))
    return [nums, rng.randint(1, 10)]


def local_oracle(args):
    grid = args[0]; n = len(grid)
    return [[max(grid[r][c] for r in range(row, row + 3) for c in range(column, column + 3))
             for column in range(n - 2)] for row in range(n - 2)]


def random_local(rng):
    n = rng.randint(3, 7)
    return [[[rng.randint(1, 99) for _ in range(n)] for _ in range(n)]]


def recolor_oracle(args):
    blocks, width = args
    return min(blocks[start:start + width].count('W') for start in range(len(blocks) - width + 1))


def random_recolor(rng):
    n = rng.randint(1, 25)
    return [''.join(rng.choice('BW') for _ in range(n)), rng.randint(1, n)]


MERGE='''\
def merge_similar_items(items1,items2):
    totals={}
    for value,weight in items1+items2:totals[value]=totals.get(value,0)+weight
    return [[value,totals[value]] for value in sorted(totals)]
'''

BAD='''\
def count_bad_index_pairs(nums):
    seen={};good=0
    for index,value in enumerate(nums):
        key=value-index;good+=seen.get(key,0);seen[key]=seen.get(key,0)+1
    return len(nums)*(len(nums)-1)//2-good
'''

TRIPLETS='''\
def count_arithmetic_triplets(nums,diff):
    values=set(nums)
    return sum(value+diff in values and value+2*diff in values for value in nums)
'''

LOCAL='''\
def largest_local_matrix_values(grid):
    n=len(grid)
    return [[max(grid[r][c] for r in range(row,row+3) for c in range(column,column+3)) for column in range(n-2)] for row in range(n-2)]
'''

RECOLOR='''\
def minimum_recolors_for_black_run(blocks,k):
    white=blocks[:k].count('W');answer=white
    for right in range(k,len(blocks)):
        white+=(blocks[right]=='W')-(blocks[right-k]=='W');answer=min(answer,white)
    return answer
'''


BATCH={
2363:entry('merge_similar_items',[('items1','list[list[int]]'),('items2','list[list[int]]')],'list[list[int]]',['arrays','hash maps','sorting'],['Each item is [value,weight], and values are unique within each input list.','Combine weights for equal values across the two lists.','Return [value,total_weight] pairs in increasing value order.'],[([[[1,1],[4,5],[3,8]],[[3,1],[1,5]]],'Values one and three combine across lists, and the sorted result is [[1,6],[3,9],[4,5]].'),([[[1,1],[3,2],[2,3]],[[2,1],[3,2],[1,3]]],'Every value occurs in both lists, producing totals four, four, and four.')],[[a,b] for a,b in [([[1,2]],[[2,3]]),([[1,2]],[[1,3]]),([[3,1],[1,2]],[[2,4]]),([[5,5]],[[5,5]]),([[1,1],[2,2]],[[2,3],[3,4]]),([[10,1]],[[1,10]]),([[2,8],[7,1]],[[2,2],[9,4]]),([[1,9],[8,2]],[[4,3],[8,7]]),([[6,6]],[[7,7]]),([[1,1],[5,5],[9,9]],[[2,2],[5,1]]),([[4,10],[2,1]],[[3,2],[4,5]]),([[100,1]],[[100,99]]),([[3,3],[6,6]],[[1,1],[9,9]]),([[8,4],[1,7]],[[1,2],[8,3]])]],MERGE,[MERGE.replace('items1+items2','items1'),MERGE.replace('sorted(totals)','totals')],['Ignores every item from the second input.','Returns insertion order instead of the required increasing value order.'],merge_oracle,random_merge,['Use a dictionary from item value to accumulated weight.','Add every pair from both lists into the same dictionary.','Iterate sorted dictionary keys to build the result.','Each input weight contributes once to its value, and sorted keys enforce the output contract.'],'O((n+m) log(n+m))','O(n+m)',3),
2364:entry('count_bad_index_pairs',[('nums','list[int]')],'int',['arrays','hash maps','counting'],['For indexes i<j, a pair is good when j-i equals nums[j]-nums[i].','A bad pair is any index pair that is not good.','Return the number of bad unordered index pairs.'],[([[4,1,3,3]],'There is one good pair and five of the six total pairs are bad.'),([[1,2,3,4,5]],'Every pair is good because value-index is constant, so the result is zero.')],[[a] for a in [[1],[1,1],[1,2],[2,1],[0,1,2],[3,3,3],[5,4,3,2],[1,3,5,7],[10,11,12,5],[0,0,1,1],[2,4,6,8],[9,1,9,1],[1,5,2,6,3],[100,101,50]]],BAD,[BAD.replace('key=value-index','key=value+index'),BAD.replace('-good','+good')],['Groups by value+index instead of the invariant value-index.','Adds good pairs to total pairs instead of subtracting them.'],bad_oracle,random_bad,['Rearrange the good condition to nums[i]-i == nums[j]-j.','Count earlier occurrences of each value-index key while scanning.','Subtract the accumulated good-pair count from n(n-1)/2 total pairs.','Equal keys characterize exactly the good pairs, and every earlier equal key forms one such pair with the current index.'],'O(n)','O(n)',5),
2367:entry('count_arithmetic_triplets',[('nums','list[int]'),('diff','int')],'int',['arrays','hash sets'],['nums is strictly increasing and diff is positive.','Count index triples i<j<k with consecutive value differences both equal to diff.','Each starting value identifies at most one valid triple.'],[([[0,1,4,6,7,10],3],'The triples with values 1,4,7 and 4,7,10 are valid.'),([[4,5,6,7,8,9],2],'Starting at four and five yields the two valid triples.')],[[a,d] for a,d in [([0,1,2],1),([0,2,4],2),([1,2,4],1),([1,3,5,7],2),([1,4,7,10],3),([0,5,10],5),([1,2,3,4,5],1),([2,6,10,14],4),([1,10,20],9),([0,3,4,6,8],2),([5,7,9,12],2),([1,6,11,16,21],5),([0,2,3,4,6],2),([10,20,30,40],10)]],TRIPLETS,[TRIPLETS.replace('value+2*diff','value+3*diff'),TRIPLETS.replace('and','or')],['Looks for a third value three differences away instead of two.','Accepts a start when only one of the two required later values exists.'],triplet_oracle,random_triplet,['Put all values in a set for constant-time membership checks.','Treat each array value as a possible first member.','Count it when value+diff and value+2*diff are both present.','Strict ordering makes those later values occur at later indexes and makes each valid triple’s start unique.'],'O(n)','O(n)',3),
2373:entry('largest_local_matrix_values',[('grid','list[list[int]]')],'list[list[int]]',['matrices','sliding windows'],['The input is an n by n matrix with n at least three.','For every contiguous three-by-three region, output its maximum.','The result has dimensions (n-2) by (n-2).'],[([[[9,9,8,1],[5,6,2,6],[8,2,6,4],[6,2,2,2]]],'The four overlapping three-by-three windows have maxima nine, nine, eight, and six.'),([[[1,1,1],[1,2,1],[1,1,1]]],'The only three-by-three window has maximum two.')],[[g] for g in [[[1,2,3],[4,5,6],[7,8,9]],[[9,8,7],[6,5,4],[3,2,1]],[[5,5,5],[5,5,5],[5,5,5]],[[1,2,1,2],[2,9,2,1],[1,2,8,2],[2,1,2,7]],[[1,0,0],[0,1,0],[0,0,1]],[[3,1,4],[1,5,9],[2,6,5]],[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]],[[16,15,14,13],[12,11,10,9],[8,7,6,5],[4,3,2,1]],[[1,9,1],[9,1,9],[1,9,1]],[[2,3,2,3],[3,2,3,2],[2,3,2,3],[3,2,3,2]],[[99,1,1],[1,1,1],[1,1,98]],[[1,2,3,4,5],[5,4,3,2,1],[1,6,1,6,1],[7,1,7,1,7],[1,8,1,8,1]],[[4,0,4],[0,0,0],[4,0,4]],[[1,3,2],[4,2,6],[5,0,7]]]],LOCAL,[LOCAL.replace('range(row,row+3)','range(row,row+2)'),LOCAL.replace('range(n-2)','range(n-3)')],['Examines only two rows within each required three-row window.','Creates too few output windows in each dimension.'],local_oracle,random_local,['The output cell (r,c) corresponds to rows r..r+2 and columns c..c+2.','There are n-2 valid starting rows and n-2 valid starting columns.','For each start, take the maximum across its nine cells.','Enumerating exactly those starts and cells directly matches the definition of every output entry.'],'O(n^2)','O(n^2)',3),
2379:entry('minimum_recolors_for_black_run',[('blocks','str'),('k','int')],'int',['strings','sliding windows'],['Each character is B for black or W for white.','Recoloring one white block black costs one operation.','Return the minimum recolors needed to create some contiguous run of k black blocks.'],[(['WBBWWBBWBW',7],'The best length-seven window contains three white blocks, so three recolors suffice.'),(['WBWBBBW',2],'A pair of adjacent black blocks already exists, so zero recolors are needed.')],[[s,k] for s,k in [('B',1),('W',1),('BBBB',4),('WWWW',4),('BWBW',2),('WBWB',3),('BBWWBB',2),('BBWWBB',4),('WBBBBW',5),('BWWWB',3),('WBW',1),('BWBWBWB',3),('WWBBBW',4),('BWBBBBWB',6)]],RECOLOR,[RECOLOR.replace('answer=min(answer,white)','answer=max(answer,white)'),RECOLOR.replace("-(blocks[right-k]=='W')",'')],['Maximizes the number of white blocks instead of minimizing recolors.','Never removes the block leaving the window, so counts accumulate across windows.'],recolor_oracle,random_recolor,['For a fixed length-k window, its number of white blocks is exactly its recolor cost.','Count white blocks in the first window.','Slide one position at a time, adding the entering white indicator and subtracting the leaving one; keep the minimum.','Every possible target run is one length-k window, so the minimum window cost is optimal.'],'O(n)','O(1)',3),
}
