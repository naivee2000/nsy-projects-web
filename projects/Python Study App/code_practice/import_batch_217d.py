"""Constrained inversions, bounding rectangles, alternating partitions, and parity subsequences."""
from itertools import permutations

from .import_batch_055 import entry


def inversions(values):return sum(values[i]>values[j] for i in range(len(values)) for j in range(i+1,len(values)))


def inversion_oracle(args):
    n,requirements=args;wanted=dict(requirements);answer=0
    for perm in permutations(range(n)):
        if all(inversions(perm[:end+1])==count for end,count in requirements):answer+=1
    return answer%1_000_000_007


def random_inversion(rng):
    n=rng.randint(1,8);perm=list(range(n));rng.shuffle(perm);ends=rng.sample(range(n),rng.randint(1,n))
    return [n,[[end,inversions(perm[:end+1])] for end in sorted(ends)]]


def area(points):
    return 0 if not points else (max(r for r,c in points)-min(r for r,c in points)+1)*(max(c for r,c in points)-min(c for r,c in points)+1)


def one_area_oracle(args):
    grid=args[0];return area([(r,c) for r,row in enumerate(grid) for c,value in enumerate(row) if value])


def random_one_area(rng):
    rows=rng.randint(1,6);cols=rng.randint(1,6);grid=[[rng.randint(0,1) for _ in range(cols)] for _ in range(rows)]
    if not any(map(any,grid)):grid[rng.randrange(rows)][rng.randrange(cols)]=1
    return [grid]


def alternating_oracle(args):
    nums=args[0];best=-10**30
    for mask in range(1<<(len(nums)-1)):
        total=0;sign=1
        for index,value in enumerate(nums):
            total+=sign*value
            if index==len(nums)-1 or mask>>index&1:sign=1
            else:sign=-sign
        best=max(best,total)
    return best


def random_alternating(rng):return [[rng.randint(-15,15) for _ in range(rng.randint(1,12))]]


def three_area_oracle(args):
    grid=args[0];rows=len(grid);cols=len(grid[0]);ones={(r,c) for r in range(rows) for c in range(cols) if grid[r][c]};rectangles=[]
    for top in range(rows):
        for bottom in range(top,rows):
            for left in range(cols):
                for right in range(left,cols):
                    covered={(r,c) for r,c in ones if top<=r<=bottom and left<=c<=right}
                    if covered:rectangles.append((top,bottom,left,right,covered,(bottom-top+1)*(right-left+1)))
    best=10**30
    for i in range(len(rectangles)):
        a=rectangles[i]
        for j in range(i+1,len(rectangles)):
            b=rectangles[j]
            if not (a[1]<b[0] or b[1]<a[0] or a[3]<b[2] or b[3]<a[2]):continue
            for k in range(j+1,len(rectangles)):
                c=rectangles[k]
                if not (a[1]<c[0] or c[1]<a[0] or a[3]<c[2] or c[3]<a[2]):continue
                if not (b[1]<c[0] or c[1]<b[0] or b[3]<c[2] or c[3]<b[2]):continue
                if a[4]|b[4]|c[4]==ones:best=min(best,a[5]+b[5]+c[5])
    return best


def random_three_area(rng):
    rows=rng.randint(2,3);cols=rng.randint(2,3);cells=rng.sample([(r,c) for r in range(rows) for c in range(cols)],rng.randint(3,rows*cols));grid=[[0]*cols for _ in range(rows)]
    for r,c in cells:grid[r][c]=1
    return [grid]


def parity_oracle(args):
    nums=args[0];best=1
    for mask in range(1,1<<len(nums)):
        seq=[nums[i] for i in range(len(nums)) if mask>>i&1]
        if len(seq)<2 or len({(seq[i]+seq[i+1])%2 for i in range(len(seq)-1)})==1:best=max(best,len(seq))
    return best


def random_parity(rng):return [[rng.randint(0,20) for _ in range(rng.randint(1,12))]]


INV='''def count_permutations_with_prefix_inversions(n,requirements):
    modulo=1000000007;required={end+1:count for end,count in requirements};maximum=n*(n-1)//2;dp=[1]+[0]*maximum
    if required.get(1,0)!=0:return 0
    for length in range(2,n+1):
        nxt=[0]*(maximum+1);window=0
        for count in range(maximum+1):
            window=(window+dp[count]-(dp[count-length] if count>=length else 0))%modulo;nxt[count]=window
        if length in required:
            wanted=required[length];nxt=[value if index==wanted else 0 for index,value in enumerate(nxt)]
        dp=nxt
    return sum(dp)%modulo
'''


ONE='''def minimum_one_cover_area(grid):
    rows=[];columns=[]
    for row,line in enumerate(grid):
        for column,value in enumerate(line):
            if value:rows.append(row);columns.append(column)
    return (max(rows)-min(rows)+1)*(max(columns)-min(columns)+1)
'''


ALT='''def maximum_alternating_partition_cost(nums):
    positive=nums[0];negative=-10**30
    for value in nums[1:]:positive,negative=max(positive,negative)+value,positive-value
    return max(positive,negative)
'''


THREE='''def minimum_three_rectangle_area(grid):
    rows=len(grid);cols=len(grid[0]);infinity=10**30
    def box(top,bottom,left,right):
        points=[(r,c) for r in range(top,bottom) for c in range(left,right) if grid[r][c]]
        return infinity if not points else (max(r for r,c in points)-min(r for r,c in points)+1)*(max(c for r,c in points)-min(c for r,c in points)+1)
    answer=infinity
    for first in range(1,rows):
        for second in range(first+1,rows):answer=min(answer,box(0,first,0,cols)+box(first,second,0,cols)+box(second,rows,0,cols))
    for first in range(1,cols):
        for second in range(first+1,cols):answer=min(answer,box(0,rows,0,first)+box(0,rows,first,second)+box(0,rows,second,cols))
    for horizontal in range(1,rows):
        for vertical in range(1,cols):
            answer=min(answer,box(0,horizontal,0,cols)+box(horizontal,rows,0,vertical)+box(horizontal,rows,vertical,cols))
            answer=min(answer,box(horizontal,rows,0,cols)+box(0,horizontal,0,vertical)+box(0,horizontal,vertical,cols))
            answer=min(answer,box(0,rows,0,vertical)+box(0,horizontal,vertical,cols)+box(horizontal,rows,vertical,cols))
            answer=min(answer,box(0,rows,vertical,cols)+box(0,horizontal,0,vertical)+box(horizontal,rows,0,vertical))
    return answer
'''


PARITY='''def longest_constant_pair_parity_subsequence(nums):
    even=sum(value%2==0 for value in nums);odd=len(nums)-even;alternating=1
    for index in range(1,len(nums)):
        if nums[index]%2!=nums[index-1]%2:alternating+=1
    return max(even,odd,alternating)
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
3193:entry('count_permutations_with_prefix_inversions',[('n','int'),('requirements','list[list[int]]')],'int',['dynamic programming','combinatorics'],['n is positive; each requirement [end,count] fixes inversions in permutation positions 0 through end.','Requirement end indices are distinct, and a missing prefix has no inversion restriction.','Count permutations of 0 through n-1 satisfying every requirement, modulo 1,000,000,007.'],[([3,[[2,2],[0,0]]],'The permutations [1,2,0] and [2,0,1] each have two total inversions and satisfy the length-one prefix.'),([3,[[1,0],[2,0]]],'Only the fully increasing permutation has zero inversions in both constrained prefixes.')],[[n,r] for n,r in [(1,[[0,0]]),(2,[]),(2,[[1,1]]),(3,[[2,2],[0,0]]),(3,[[1,0],[2,0]]),(3,[[1,1]]),(4,[[3,6]]),(4,[[1,1],[3,3]]),(4,[[0,0],[2,2]]),(5,[[4,0]]),(5,[[2,1],[4,5]]),(6,[[1,0],[3,2],[5,4]]),(7,[[6,10]]),(8,[[2,3],[7,12]])]],INV,[INV.replace('count>=length','count>length'),INV.replace('required={end+1:count','required={end:count')],['Uses an oversized sliding window and permits one too many new inversions at each insertion.','Treats zero-based end indices as prefix lengths without adding one.'],inversion_oracle,random_inversion,lesson('Inserting the new largest value into a length-L permutation adds any inversion count from zero through L-1.','Use inversion-count DP with a sliding window, and zero all states except a required count whenever a constrained prefix is reached.','next[c]=sum(dp[c-x],x=0..L-1); filter at required[L].','Every length-L permutation uniquely removes its largest value to one prior permutation plus its insertion contribution, so the recurrence counts each once.'),'O(n*maximum required inversions)','O(maximum inversions)',8),
3195:entry('minimum_one_cover_area',[('grid','list[list[int]]')],'int',['matrices','geometry'],['grid is a nonempty rectangular binary matrix containing at least one one.','Choose one axis-aligned rectangle whose cells include every one; zero cells may also lie inside.','Return the smallest possible rectangle area.'],[([[[0,1,0],[1,0,1]]],'The ones span both rows and all three columns, so the bounding rectangle area is six.'),([[[0,0],[0,1]]],'A one-cell rectangle around the only one has area one.')],[[g] for g in [[[1]],[[0,0],[0,1]],[[0,1,0],[1,0,1]],[[1,1],[1,1]],[[1,0,0]],[[0],[1],[0]],[[1,0,1],[0,0,0],[1,0,1]],[[0,0,1],[0,1,0]],[[0,1,0],[0,1,0],[0,1,0]],[[1,0],[0,0],[0,1]],[[0,0,0],[1,1,0]],[[1,0,0,0],[0,0,0,1]],[[0,1],[1,0],[0,1]],[[0,0,1,0],[0,1,0,0],[1,0,0,0]]]],ONE,[ONE.replace('+1)*(max(columns)',' )*(max(columns)'),ONE.replace('(max(rows)-min(rows)+1)*(max(columns)-min(columns)+1)','(max(rows)-min(rows)+1)+(max(columns)-min(columns)+1)')],['Omits one inclusive row from the bounding height.','Adds the bounding height and width instead of multiplying them to obtain area.'],one_area_oracle,random_one_area,lesson('Any covering rectangle must include the extreme row and column containing a one.','Scan all ones and track minimum and maximum row and column.','Return (maxRow-minRow+1)*(maxColumn-minColumn+1).','The extremes force these four boundaries, and their bounding rectangle covers every intervening one, so it is minimal.'),'O(rows*columns)','O(number of ones) in this implementation',5),
3196:entry('maximum_alternating_partition_cost',[('nums','list[int]')],'int',['dynamic programming','arrays'],['nums is a nonempty integer array.','Split it into nonempty contiguous parts; a part costs first-second+third-fourth and so on.','Maximize the sum of all part costs while using every element exactly once.'],[([[1,-2,3,4]],'Keeping 1,-2,3 together costs six and starting a new part at four gives total ten.'),([[-5]],'The only part contains -5, so the maximum total is -5.')],[[n] for n in [[1],[-5],[1,-2,3,4],[1,2],[1,-2],[-1,-2,-3],[5,4,3],[3,-10,4],[1,2,3,4,5],[10,-1,-1,10],[-5,10,-5],[0,0,0],[4,-3,2,-1],[8,1,-9,2,7]]],ALT,[ALT.replace('positive-value','negative-value'),ALT.replace('return max(positive,negative)','return positive')],['Extends a negative-signed state from itself instead of a preceding positive-signed state.','Forces the final element to carry a positive sign and misses optimal parts ending on a subtraction.'],alternating_oracle,random_alternating,lesson('At each position retain the best total when the current element receives a plus or minus sign within its part.','A plus may begin a new part after either state; a minus can only continue after a plus.','newPlus=max(plus,minus)+x; newMinus=plus-x.','These are the only legal roles for the next element, so induction preserves the best cost for both possible ending signs.'),'O(n)','O(1)',5),
3197:entry('minimum_three_rectangle_area',[('grid','list[list[int]]')],'int',['matrices','enumeration','geometry'],['grid is a binary rectangular matrix containing at least three ones.','Use exactly three positive-area axis-aligned rectangles with disjoint interiors; each rectangle must contain at least one one.','Cover every one and minimize the sum of rectangle areas; rectangles may touch along boundaries.'],[([[[1,0,1],[1,1,1]]],'A two-cell vertical rectangle at the left and two horizontal rectangles covering the remaining top and bottom ones total area five.'),([[[1,0,0],[0,1,0],[0,0,1]]],'Three one-cell rectangles cover the diagonal ones with total area three.')],[[g] for g in [[[1,0,1],[1,1,1]],[[1,0,0],[0,1,0],[0,0,1]],[[1,1,1]],[[1],[1],[1]],[[1,1],[1,1]],[[1,0,1],[0,1,0]],[[1,0,0],[1,0,0],[1,1,1]],[[1,1,0],[0,1,1]],[[1,0,1,0],[0,1,0,1]],[[1,1,1],[1,0,1],[1,1,1]],[[0,1,0],[1,1,1],[0,1,0]],[[1,0],[1,0],[0,1],[0,1]],[[1,1,0,0],[0,0,1,1]],[[1,0,0,1],[0,1,1,0],[1,0,0,1]]]],THREE,[THREE.replace('answer=min(answer,box(0,horizontal,0,cols)+','answer=min(answer,box(0,horizontal,0,cols)*0+'),THREE.replace('max(c for r,c in points)-min(c for r,c in points)+1','right-left')],['Allows one region’s bounding rectangle to contribute zero area.','Uses the whole partition-region width instead of the tight bounding width around its ones.'],three_area_oracle,random_three_area,lesson('Three disjoint axis-aligned rectangles can be separated by two parallel cuts or by one full cut and one perpendicular cut on either side.','Enumerate the six layout families and use a tight one-bounding box inside each of the three regions.','Try all horizontal triples, vertical triples, and four T-shaped orientations; reject empty regions.','Any three pairwise disjoint rectangles admit one of these separating layouts; tightening each within its assigned region never hurts coverage or overlap.'),'O(rows²*cols²*(rows+cols)) with direct box scans','O(rows*cols) temporary',8),
3201:entry('longest_constant_pair_parity_subsequence',[('nums','list[int]')],'int',['dynamic programming','parity'],['nums is a nonempty integer array.','Choose a subsequence such that every adjacent chosen pair has the same sum parity.','Return the maximum length; valid sequences therefore either use one value parity throughout or alternate parities throughout.'],[([[1,2,3,4]],'All adjacent sums in the full alternating-parity sequence are odd, so its length is four.'),([[1,3,5,2]],'The three odd values form a length-three subsequence whose adjacent sums are even.')],[[n] for n in [[1],[1,2,3,4],[1,3,5,2],[2,4,6],[1,2,2,1],[1,1,2,2],[0,1,0,1,0],[5,4,3,2,1],[2,1,4,3,6],[7,7,8,8,7],[1,2],[1,1],[9,2,7,4,5,6],[0,2,1,3,4]]],PARITY,[PARITY.replace("max(even,odd,alternating)","max(even,odd)"),PARITY.replace('nums[index]%2!=nums[index-1]%2','nums[index]%2==nums[index-1]%2')],['Considers only even-sum pairs and misses longer alternating-parity subsequences.','Counts equal-parity transitions as part of the alternating candidate.'],parity_oracle,random_parity,lesson('Constant adjacent-sum parity has only two cases: every chosen value has one parity, or chosen parities alternate.','Count all evens and odds, and greedily count the longest alternating-parity subsequence.','Return max(evenCount,oddCount,alternatingCount).','Same-parity pairs have even sums; different-parity pairs have odd sums, and greedily taking each next opposite parity maximizes an alternating subsequence.'),'O(n)','O(1)',5),
}
