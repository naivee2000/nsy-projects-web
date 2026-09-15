"""Grid counting, Fenwick distribution, triplets, greedy choice, and substrings."""
from itertools import permutations

from .import_batch_055 import entry


def y_oracle(args):
    grid = args[0]; size = len(grid); middle = size // 2
    inside, outside = [], []
    for row in range(size):
        for column in range(size):
            on_y = ((row <= middle and (column == row or column == size - 1 - row)) or
                    (row >= middle and column == middle))
            (inside if on_y else outside).append(grid[row][column])
    return min(sum(value != a for value in inside) + sum(value != b for value in outside)
               for a in range(3) for b in range(3) if a != b)


def random_y(rng):
    size = rng.choice((3, 5, 7))
    return [[[rng.randrange(3) for _ in range(size)] for _ in range(size)]]


def distribution_oracle(args):
    nums = args[0]; first, second = [nums[0]], [nums[1]]
    for value in nums[2:]:
        above_first = sum(item > value for item in first)
        above_second = sum(item > value for item in second)
        if above_first > above_second or (above_first == above_second and len(first) <= len(second)):
            first.append(value)
        else:
            second.append(value)
    return first + second


def random_distribution(rng):
    return [[rng.randint(1, 20) for _ in range(rng.randint(2, 14))]]


def triplet_oracle(args):
    nums = args[0]; answer = 0
    for left in range(len(nums)):
        for middle in range(left + 1, len(nums)):
            for right in range(middle + 1, len(nums)):
                if nums[left] < nums[middle] < nums[right]:
                    answer = max(answer, nums[left] - nums[middle] + nums[right])
    return answer


def random_triplet(rng):
    return [[rng.randint(1, 40) for _ in range(rng.randint(3, 12))]]


def happiness_oracle(args):
    values, count = args
    best = 0
    for order in permutations(range(len(values)), count):
        total = sum(max(values[index] - turn, 0) for turn, index in enumerate(order))
        best = max(best, total)
    return best


def random_happiness(rng):
    size = rng.randint(1, 8)
    return [[rng.randint(1, 20) for _ in range(size)], rng.randint(1, size)]


def uncommon_oracle(args):
    words = args[0]
    owners = {}
    for index, word in enumerate(words):
        for left in range(len(word)):
            for right in range(left + 1, len(word) + 1):
                owners.setdefault(word[left:right], set()).add(index)
    answer = []
    for index, word in enumerate(words):
        choices = {word[left:right] for left in range(len(word))
                   for right in range(left + 1, len(word) + 1)
                   if owners[word[left:right]] == {index}}
        answer.append(min(choices, key=lambda text: (len(text), text)) if choices else '')
    return answer


def random_uncommon(rng):
    return [["".join(rng.choice("abcd") for _ in range(rng.randint(1, 7)))
             for _ in range(rng.randint(1, 7))]]


Y_SHAPE = '''def minimum_y_grid_changes(grid):
    from collections import Counter
    size=len(grid);middle=size//2;inside=Counter();outside=Counter()
    for row in range(size):
        for column in range(size):
            on_y=(row<=middle and (column==row or column==size-1-row)) or (row>=middle and column==middle)
            (inside if on_y else outside)[grid[row][column]]+=1
    y_cells=sum(inside.values());other_cells=sum(outside.values())
    return min(y_cells-inside[a]+other_cells-outside[b] for a in range(3) for b in range(3) if a!=b)
'''


DISTRIBUTE = '''def distribute_by_greater_counts(nums):
    values=sorted(set(nums));size=len(values);first=[nums[0]];second=[nums[1]]
    tree1=[0]*(size+1);tree2=[0]*(size+1)
    from bisect import bisect_left
    def add(tree,index):
        while index<=size:tree[index]+=1;index+=index&-index
    def prefix(tree,index):
        total=0
        while index:total+=tree[index];index-=index&-index
        return total
    add(tree1,bisect_left(values,nums[0])+1);add(tree2,bisect_left(values,nums[1])+1)
    for value in nums[2:]:
        rank=bisect_left(values,value)+1
        above1=len(first)-prefix(tree1,rank);above2=len(second)-prefix(tree2,rank)
        if above1>above2 or (above1==above2 and len(first)<=len(second)):
            first.append(value);add(tree1,rank)
        else:second.append(value);add(tree2,rank)
    return first+second
'''


TRIPLET = '''def maximum_increasing_triplet_value(nums):
    from bisect import bisect_left
    values=sorted(set(nums));size=len(values);tree=[-1]*(size+1)
    suffix=[0]*len(nums);suffix[-1]=nums[-1]
    for index in range(len(nums)-2,-1,-1):suffix[index]=max(nums[index],suffix[index+1])
    def update(index,value):
        while index<=size:tree[index]=max(tree[index],value);index+=index&-index
    def query(index):
        answer=-1
        while index:answer=max(answer,tree[index]);index-=index&-index
        return answer
    update(bisect_left(values,nums[0])+1,nums[0]);answer=0
    for middle in range(1,len(nums)-1):
        rank=bisect_left(values,nums[middle])+1;left=query(rank-1)
        if left>=0 and suffix[middle+1]>nums[middle]:answer=max(answer,left-nums[middle]+suffix[middle+1])
        update(rank,nums[middle])
    return answer
'''


HAPPINESS = '''def maximum_happiness_sum(happiness,k):
    answer=0
    for turn,value in enumerate(sorted(happiness,reverse=True)[:k]):
        answer+=max(value-turn,0)
    return answer
'''


UNCOMMON = '''def shortest_uncommon_substrings(arr):
    answer=[]
    for index,word in enumerate(arr):
        found=''
        for length in range(1,len(word)+1):
            choices=[]
            for start in range(len(word)-length+1):
                candidate=word[start:start+length]
                if all(other==index or candidate not in text for other,text in enumerate(arr)):
                    choices.append(candidate)
            if choices:found=min(choices);break
        answer.append(found)
    return answer
'''


def lesson(concept, strategy, pseudocode, proof):
    return [concept, strategy, pseudocode, proof]


BATCH = {
3071: entry('minimum_y_grid_changes',[('grid','list[list[int]]')],'int',['matrices','counting','enumeration'],['grid is an odd-size square matrix of values zero, one, and two.','The Y consists of both upper diagonals through the center and the center column from the center downward.','All Y cells need one value and all other cells a different value; return the minimum cell changes.'],[([[[1,2,2],[1,1,0],[0,1,0]]],'Choosing one for the Y and zero outside requires three changes.'),([[[0,0,1],[0,2,0],[2,1,2]]],'Choosing one for the Y and zero outside changes the center and two stem cells, for three operations.')],[[g] for g in [[[0,0,0],[0,0,0],[0,0,0]],[[0,1,0],[2,1,2],[0,1,0]],[[1,0,1],[0,1,0],[2,1,2]],[[2,1,2],[0,2,0],[1,2,1]],[[0,1,2],[2,1,0],[1,0,2]],[[1,1,1],[1,1,1],[1,1,1]],[[0,2,0],[1,2,1],[0,2,0]],[[2,0,2],[0,2,0],[1,2,1]],[[0]*5 for _ in range(5)],[[0,1,2,1,0],[2,0,1,0,2],[1,2,1,2,1],[0,1,2,1,0],[2,0,1,0,2]],[[2 if r==c or r+c==4 or (r>=2 and c==2) else 1 for c in range(5)] for r in range(5)],[[((r+c)%3) for c in range(5)] for r in range(5)],[[1 if c==2 else 0 for c in range(5)] for r in range(5)],[[2 if r<=2 and (c==r or c==4-r) else 0 for c in range(5)] for r in range(5)]]],Y_SHAPE,[Y_SHAPE.replace('row<=middle','row<middle').replace('row>=middle','row>middle'),Y_SHAPE.replace('column==size-1-row','column==size-row')],['Omits the center cell from both the arms and stem of the Y.','Shifts the upper-right diagonal one column and misclassifies its cells.'],y_oracle,random_y,lesson('Only the frequency of each value inside and outside the fixed Y shape matters.','Classify every cell, count its value in one of two groups, and try the six distinct value assignments.','For Y value a and outside value b≠a, changes=Ysize-countY[a]+outsideSize-countOutside[b].','For a fixed assignment, every disagreeing cell must change and every agreeing cell can remain; checking all assignments finds the global minimum.'),'O(n^2)','O(1)',5),
3072: entry('distribute_by_greater_counts',[('nums','list[int]')],'list[int]',['Fenwick trees','coordinate compression','simulation'],['nums contains at least two positive integers.','Start arrays with nums[0] and nums[1]; each later value goes where strictly more existing elements are greater.','Equal greater-counts choose the shorter array, with a remaining size tie choosing the first; return first followed by second.'],[([[2,1,3,3]],'The first three goes to the first array by the size tie; the second three goes to the second, producing [2,3,1,3].'),([[5,14,3,1,2]],'Three and one go to the first array by greater counts; two then goes to the second, producing [5,3,1,14,2].')],[[n] for n in [[1,2],[2,1,3],[2,1,3,3],[1,1,1],[3,3,2,2],[5,1,4,2,3],[1,5,2,4,3],[10,9,8,7,6],[1,2,3,4,5],[4,1,4,1,4,1],[2,8,6,4,10,3],[7,7,6,8,6,8],[9,2,5,1,8,3,7],[3,1,2,2,4,1,5]]],DISTRIBUTE,[DISTRIBUTE.replace('prefix(tree1,rank)','prefix(tree1,rank-1)').replace('prefix(tree2,rank)','prefix(tree2,rank-1)'),DISTRIBUTE.replace('len(first)<=len(second)','len(first)<len(second)')],['Counts values equal to the current value as greater by querying only ranks below it.','Sends a full tie to the second array instead of the required first array.'],distribution_oracle,random_distribution,lesson('Greater-than counts equal array length minus the number of values at or below the current value.','Coordinate-compress values and maintain one Fenwick frequency tree per result array.','Query each tree through current rank; compare length-prefixCount, then apply size and first-array ties; append and update.','Fenwick prefix frequencies give exact greater counts, and the conditional sequence directly implements every distribution rule in priority order.'),'O(n log n)','O(n)',8),
3073: entry('maximum_increasing_triplet_value',[('nums','list[int]')],'int',['Fenwick trees','arrays','suffix maxima'],['nums contains at least three positive integers.','Choose indices i<j<k with strictly increasing values nums[i]<nums[j]<nums[k].','Maximize nums[i]-nums[j]+nums[k], returning zero when no valid triplet exists.'],[([[5,6,9]],'The only triplet is increasing and has value five minus six plus nine, which is eight.'),([[1,10,3,4,19]],'Indices zero, two, and four form 1<3<19 with value seventeen, the maximum.')],[[n] for n in [[1,2,3],[3,2,1],[1,1,1],[1,3,2],[2,1,3],[5,6,6],[5,6,9],[1,10,3,4,19],[8,1,2,9],[2,5,3,10],[4,4,5,6],[9,2,8,3,10],[1,5,2,6,3,7],[10,1,9,2,8,20],[3,7,4,9,5,11]]],TRIPLET,[TRIPLET.replace('query(rank-1)','query(rank)'),TRIPLET.replace('if left>=0 and suffix[middle+1]>nums[middle]:','if left>=0:')],['Allows an equal-valued left endpoint despite strict increase.','Uses the largest later value without checking that it is greater than the middle value.'],triplet_oracle,random_triplet,lesson('For each middle index, the best endpoints are the largest earlier value below it and the largest later value above it.','Precompute suffix maxima and use a compressed Fenwick maximum tree to query earlier values by rank.','At j, query ranks below nums[j]; if suffix[j+1]>nums[j], maximize left-nums[j]+suffix[j+1]; then insert nums[j].','The strict rank query and suffix condition enumerate exactly valid middles, while choosing the largest endpoints maximizes the expression for that middle.'),'O(n log n)','O(n)',5),
3075: entry('maximum_happiness_sum',[('happiness','list[int]'),('k','int')],'int',['greedy','sorting','arrays'],['happiness contains positive integers and 1≤k≤its length.','On turn t starting at zero, the selected child contributes max(original happiness-t,0).','Choose exactly k distinct children and maximize the total contribution.'],[([[1,2,3],2],'Select happiness three first for three, then two contributes one, totaling four.'),([[12,1,42],3],'Selecting 42, then 12, then 1 contributes 42+11+0=53.')],[[a,k] for a,k in [([1],1),([1,1],2),([2,1],1),([2,1],2),([5,4,3],2),([1,2,3],3),([10,1,1,1],2),([3,3,3,3],3),([100,2,1],2),([7,6,1,1],4),([4,9,2,8],3),([1,20,3,19,5],4),([6,5,4,3,2,1],5),([2,2,10,10,1],3)]],HAPPINESS,[HAPPINESS.replace('value-turn','value'),HAPPINESS.replace('max(value-turn,0)','value-turn')],['Never applies the per-turn decrease to unselected children.','Allows negative contributions instead of flooring decreased happiness at zero.'],happiness_oracle,random_happiness,lesson('At any turn, selecting a larger original value never gives less contribution than selecting a smaller one.','Sort descending and take the first k values, subtracting the zero-based turn and flooring at zero.','Sum max(sorted_descending[t]-t,0) for t from zero through k-1.','An exchange that moves a larger unselected value earlier cannot decrease either affected contribution, so descending order is optimal.'),'O(n log n)','O(n)',5),
3076: entry('shortest_uncommon_substrings',[('arr','list[str]')],'list[str]',['strings','enumeration','hash maps'],['arr contains nonempty lowercase strings.','For each string, find a substring absent from every other array element.','Choose minimum length first and lexicographically smallest second; use an empty string when no candidate exists.'],[([['cab','ad','bad','c']],'For cab the shortest unique choice is ab; bad chooses ba; the other two have no unique substring.'),([['abc','bcd','abcd']],'The unique one-letter substrings are a for abc and d for bcd; every substring of abcd appears in another word, so its result is empty.')],[[a] for a in [['a'],['a','b'],['a','a'],['ab','ba'],['abc','bcd','abcd'],['cab','ad','bad','c'],['hello','world'],['aaa','aa','a'],['abc','def','ghi'],['abab','baba'],['x','xy','xyz'],['cat','car','dog'],['abcd','bc','cd'],['zzab','zzac','zzad']]],UNCOMMON,["""def shortest_uncommon_substrings(arr):
    return [next((word[:length] for length in range(1,len(word)+1) if all(i==j or word[:length] not in other for j,other in enumerate(arr))), '') for i,word in enumerate(arr)]
""",UNCOMMON.replace('found=min(choices)','found=max(choices)')],['Examines prefixes only and misses unique substrings beginning later in a word.','Breaks equal-length ties toward the lexicographically largest candidate.'],uncommon_oracle,random_uncommon,lesson('A candidate belongs to one string only when no other full string contains it anywhere.','Enumerate candidate lengths from shortest to longest; collect unique substrings at that length and choose the lexicographic minimum.','For each word and length, test every slice against all other words; stop after the first nonempty candidate set.','Length order proves minimality, the minimum of the first qualifying set enforces the tie rule, and exhaustive slices ensure no candidate is missed.'),'O(n^2*L^3)','O(L)',5),
}
