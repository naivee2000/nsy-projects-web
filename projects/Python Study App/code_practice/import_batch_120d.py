"""Final reviewed group of workbook batch 120."""
from collections import Counter
from functools import lru_cache
from .import_batch_055 import entry

def lonely_o(a):
 counts=Counter(a[0]);return sorted(x for x,v in counts.items() if v==1 and x-1 not in counts and x+1 not in counts)
def good_o(a):
 statements=a[0];n=len(statements);best=0
 for mask in range(1<<n):
  if all(not (mask>>i&1) or all(x==2 or (mask>>j&1)==x for j,x in enumerate(row)) for i,row in enumerate(statements)):best=max(best,mask.bit_count())
 return best
def lines_o(a):
 points=a[0];n=len(points);line_masks={1<<i for i in range(n)}
 for i in range(n):
  for j in range(i+1,n):
   x1,y1=points[i];x2,y2=points[j];mask=0
   for k,(x,y) in enumerate(points):
    if (x2-x1)*(y-y1)==(y2-y1)*(x-x1):mask|=1<<k
   line_masks.add(mask)
 @lru_cache(None)
 def solve(mask):
  if mask==(1<<n)-1:return 0
  first=next(i for i in range(n) if not mask>>i&1)
  return 1+min(solve(mask|line) for line in line_masks if line>>first&1)
 return solve(0)
def multiply_o(a):
 nums,value=a
 while value in nums:value*=2
 return value
def scores_o(a):
 nums=a[0];scores=[nums[:i].count(0)+nums[i:].count(1) for i in range(len(nums)+1)];best=max(scores);return [i for i,x in enumerate(scores) if x==best]
def rlonely(r):return [[r.randint(-10,10) for _ in range(r.randint(1,25))]]
def rgood(r):
 n=r.randint(1,8);return [[[2 if i==j else r.randint(0,2) for j in range(n)] for i in range(n)]]
def rlines(r):
 all_points=[[x,y] for x in range(-3,4) for y in range(-3,4)];r.shuffle(all_points);return [all_points[:r.randint(1,8)]]
def rmultiply(r):return [[r.randint(1,50) for _ in range(r.randint(1,20))],r.randint(1,20)]
def rscores(r):return [[r.randint(0,1) for _ in range(r.randint(1,25))]]

LONELY='''\
def lonely_numbers(nums):
    from collections import Counter
    counts=Counter(nums)
    return sorted(value for value,count in counts.items() if count==1 and value-1 not in counts and value+1 not in counts)
'''
GOOD='''\
def maximum_consistent_good_people(statements):
    n=len(statements);answer=0
    for mask in range(1<<n):
        valid=True
        for person,row in enumerate(statements):
            if not (mask>>person&1):continue
            for other,claim in enumerate(row):
                if claim!=2 and (mask>>other&1)!=claim:valid=False;break
            if not valid:break
        if valid:answer=max(answer,mask.bit_count())
    return answer
'''
LINES='''\
def minimum_covering_lines(points):
    from functools import lru_cache
    n=len(points);complete=(1<<n)-1
    line=[[0]*n for _ in range(n)]
    for i in range(n):
        line[i][i]=1<<i
        for j in range(i+1,n):
            x1,y1=points[i];x2,y2=points[j];mask=0
            for k,(x,y) in enumerate(points):
                if (x2-x1)*(y-y1)==(y2-y1)*(x-x1):mask|=1<<k
            line[i][j]=line[j][i]=mask
    @lru_cache(None)
    def search(mask):
        if mask==complete:return 0
        first=next(i for i in range(n) if not mask>>i&1);answer=1+search(mask|1<<first)
        for other in range(first+1,n):
            if not mask>>other&1:answer=min(answer,1+search(mask|line[first][other]))
        return answer
    return search(0)
'''
MULTIPLY='''\
def final_doubled_value(nums,original):
    values=set(nums)
    while original in values:original*=2
    return original
'''
SCORES='''\
def highest_split_scores(nums):
    zeros=0;ones=sum(nums);best=ones;answer=[0]
    for index,value in enumerate(nums,1):
        zeros+=value==0;ones-=value==1;score=zeros+ones
        if score>best:best=score;answer=[index]
        elif score==best:answer.append(index)
    return answer
'''
def L(*x):return list(x)
BATCH={
2150:entry('lonely_numbers',[('nums','list[int]')],'list[int]',['arrays','hash maps','counting'],['A lonely value occurs exactly once and neither adjacent integer value occurs anywhere.','Return every lonely value in increasing order.','Duplicate occurrences make that value non-lonely.'],[([[10,6,5,8]],'Ten and eight occur once and have no neighboring integer in the array.'),([[1,3,5,3]],'Only one and five are unique and isolated from adjacent values.')],[[x] for x in [[1],[1,1],[1,2],[1,3],[1,2,3],[0,2,4],[5,4,6],[10,6,5,8],[-1,1],[-2,-1,1],[2,2,4],[7,9,8],[1,4,7,10],[3,5,5,8]]],LONELY,[LONELY.replace('count==1','count>=1'),LONELY.replace('value-1 not in counts','value-2 not in counts')],['Allows duplicated values to qualify as lonely.','Checks distance two on the lower side instead of the adjacent value.'],lonely_o,rlonely,L('A frequency map answers uniqueness and neighbor presence in constant time per distinct value.','Count values, then require count one and absence of both value-1 and value+1.','Return the qualifying keys sorted.','The three map conditions exactly encode the definition, and sorting provides deterministic output without changing membership.'),'O(n log n)','O(n)',5),
2151:entry('maximum_consistent_good_people',[('statements','list[list[int]]')],'int',['bit masks','enumeration','logic'],['Statements use zero for bad, one for good, and two for unknown; diagonal entries may be ignored.','Every person assumed good must have all definite statements agree with the assignment; bad people impose no constraint.','Return the greatest possible number of good people.'],[([[[2,1,2],[1,2,2],[2,0,2]]],'People zero and one can both be good consistently, giving maximum two.'),([[[2,0],[0,2]]],'Either person may be good alone, but both good contradict their statements, so the maximum is one.')],[[s] for s in [[[2]],[[2,1],[1,2]],[[2,0],[0,2]],[[2,1],[0,2]],[[2,2],[2,2]],[[2,1,0],[1,2,0],[0,0,2]],[[2,1,2],[1,2,2],[2,0,2]],[[2,0,1],[2,2,2],[1,2,2]],[[2,1,1],[1,2,1],[1,1,2]],[[2,0,0],[0,2,0],[0,0,2]],[[2,2,0],[2,2,1],[1,1,2]],[[2,1,2,0],[1,2,1,2],[2,1,2,1],[0,2,1,2]],[[2,0,2],[1,2,1],[2,1,2]],[[2,2,2],[2,2,2],[2,2,2]]]],GOOD,[GOOD.replace('if not (mask>>person&1):continue','if mask>>person&1:continue'),GOOD.replace('claim!=2','claim==2')],['Checks statements made by bad people and ignores the required truthful people.','Treats unknown statements as definite constraints while ignoring zero and one claims.'],good_o,rgood,L('The small n permits checking every proposed set of good people.','Encode an assignment as a bit mask; inspect only rows whose person bit is one.','Reject when any claim below two differs from the corresponding assignment bit; maximize valid bit counts.','Good rows are enforced exactly, bad rows remain unrestricted, and exhaustive masks include every possible classification.'),'O(2^n*n^2)','O(1)',8),
2152:entry('minimum_covering_lines',[('points','list[list[int]]')],'int',['geometry','bitmask dynamic programming'],['Points are distinct integer coordinates.','A line may cover any number of collinear points; every point must be covered.','Return the minimum number of infinite straight lines.'],[([[[0,1],[2,3],[4,5],[4,3]]],'The first three collinear points share one line and the remaining point needs a second.'),([[[0,0],[1,1],[2,2]]],'All points lie on one line, so one line suffices.')],[[p] for p in [[[0,0]],[[0,0],[1,1]],[[0,0],[1,1],[2,2]],[[0,0],[1,0],[0,1]],[[0,0],[0,1],[0,2],[1,0]],[[0,0],[1,1],[2,2],[3,3]],[[0,0],[1,2],[2,4],[1,0]],[[0,0],[1,0],[2,0],[0,1],[0,2]],[[1,1],[2,3],[3,5],[4,7],[0,0]],[[0,0],[1,1],[1,-1],[-1,1]],[[0,1],[2,3],[4,5],[4,3]],[[0,0],[2,0],[1,0],[1,2]],[[1,0],[1,1],[1,2],[2,2]],[[0,0],[1,2],[2,1],[3,3]]]],LINES,[LINES.replace('first+1,n','first+2,n'),LINES.replace('return search(0)','return search(0)+1')],['Skips pairing the first uncovered point with its immediate next point.','Adds an unnecessary extra line to every result.'],lines_o,rlines,L('A DP state is the set of already covered points; an optimal next line may be chosen through the first uncovered point.','Precompute the collinear mask for every point pair, then recurse on covered masks.','Try a singleton line and every pair line through first; memoize the minimum one plus the remaining state.','Any optimal cover has a line through the first uncovered point, represented by one of these choices, so the recurrence is exhaustive.'),'O(3^n)','O(2^n+n^3)',7),
2154:entry('final_doubled_value',[('nums','list[int]'),('original','int')],'int',['arrays','hash sets','simulation'],['nums contains positive integers and original is positive.','While the current value appears anywhere in nums, double it; array elements are not consumed.','Return the first resulting value absent from nums.'],[([[5,3,6,1,12],3],'Three, six, and twelve appear successively, so doubling stops at twenty-four.'),([[2,7,9],4],'Four is absent initially, so it is returned unchanged.')],[[n,o] for n,o in [([1],1),([1],2),([2,4,8],2),([2,4,8],1),([1,2,4,8],1),([3,6,12],3),([3,6,12],6),([5,3,6,1,12],1),([10,20,40],10),([2,2,4],2),([100],50),([7,14,28,56],7),([1,3,9],3),([16,8,4,2],2)]],MULTIPLY,[MULTIPLY.replace('original*=2','original+=2'),MULTIPLY.replace('values=set(nums)','values=[]')],['Adds two instead of doubling the found value.','Uses a list initialized empty and never detects any present value.'],multiply_o,rmultiply,L('Membership does not consume occurrences, so a set is the exact needed structure.','Repeatedly test current value and multiply by two while found.','Build values=set(nums); while original in values: original*=2; return original.','The loop follows the mandated deterministic sequence and stops precisely at its first absent value.'),'O(n+number of doublings)','O(n)',3),
2155:entry('highest_split_scores',[('nums','list[int]')],'list[int]',['arrays','prefix counts'],['For split i from zero through n, the left side is nums[:i] and right side nums[i:].','Score equals left zeros plus right ones.','Return every maximum-score split index in any order.'],[([[0,0,1,0]],'Splits two and four both score three, the maximum.'),([[0,0,0]],'Only split three places all zeros on the left, so it is uniquely best.')],[[x] for x in [[0],[1],[0,1],[1,0],[0,0],[1,1],[0,0,1,0],[1,1,0,1],[0,1,0,1],[1,0,1,0],[0,0,0],[1,1,1],[0,1,1,0,0],[1,0,0,1,1]]],SCORES,[SCORES.replace('enumerate(nums,1)','enumerate(nums[:-1],1)'),SCORES.replace('zeros+=value==0','zeros+=value==1')],['Never evaluates the final split after every element has moved left.','Counts left-side ones instead of zeros.'],scores_o,rscores,L('Update the split score incrementally as one element crosses from right to left.','Start with all right-side ones; moving zero adds one, moving one subtracts one.','Track the best score and replace or append its split index after each move.','Each update exactly reflects the score definition for the next split, including empty-side splits zero and n.'),'O(n)','O(output)',5)
}
BATCH[2150]['comparator']='unordered'
BATCH[2155]['comparator']='unordered'
