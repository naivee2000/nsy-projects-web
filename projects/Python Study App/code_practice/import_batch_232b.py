"""Activation groups, special palindromes, two bags, grid sensors, and perfect pairs."""
from bisect import bisect_right
from functools import lru_cache
from itertools import permutations, product
from .import_batch_055 import entry


def activation_oracle(args):
    values,limits=args;n=len(values)
    @lru_cache(None)
    def solve(alive,active):
        best=0;active_count=active.bit_count()
        for index in range(n):
            bit=1<<index
            if alive&bit and not active&bit and active_count<limits[index]:
                new_active=active|bit;count=new_active.bit_count();removed=0
                for j,limit in enumerate(limits):
                    if limit<=count:removed|=1<<j
                new_alive=alive&~removed;new_active&=new_alive
                best=max(best,values[index]+solve(new_alive,new_active))
        return best
    return solve((1<<n)-1,0)

def random_activation(rng):
    n=rng.randint(1,8);return [[rng.randint(1,30) for _ in range(n)],[rng.randint(1,n) for _ in range(n)]]

@lru_cache(None)
def oracle_specials():
    answer=set()
    for mask in range(1,1<<9):
        digits=[digit for digit in range(1,10) if mask>>(digit-1)&1]
        if sum(digits)>17 or sum(digit%2 for digit in digits)>1:continue
        half=[];center=''
        for digit in digits:
            half.extend(str(digit) for _ in range(digit//2))
            if digit%2:center=str(digit)
        for arranged in set(permutations(half)):
            left=''.join(arranged);answer.add(int(left+center+left[::-1]))
    return tuple(sorted(answer))

def special_oracle(args):return oracle_specials()[bisect_right(oracle_specials(),args[0])]
def random_special(rng):return [rng.randint(0,10**15)]

def bags_oracle(args):
    weights,w1,w2=args;answer=0
    for choices in product(range(3),repeat=len(weights)):
        first=sum(value for value,choice in zip(weights,choices) if choice==1)
        second=sum(value for value,choice in zip(weights,choices) if choice==2)
        if first<=w1 and second<=w2:answer=max(answer,first+second)
    return answer

def random_bags(rng):
    return [[rng.randint(1,12) for _ in range(rng.randint(1,8))],rng.randint(1,20),rng.randint(1,20)]

def sensors_oracle(args):
    rows,cols,k=args
    if k==0:return rows*cols
    def line_cover(length):
        full=(1<<length)-1;intervals=[]
        for center in range(length):
            mask=0
            for cell in range(length):
                if abs(center-cell)<=k:mask|=1<<cell
            intervals.append(mask)
        @lru_cache(None)
        def cover(mask):
            if mask==full:return 0
            cell=((~mask)&full&-((~mask)&full)).bit_length()-1
            return 1+min(cover(mask|interval) for interval in intervals if interval>>cell&1)
        return cover(0)
    if rows*cols>16:return line_cover(rows)*line_cover(cols)
    full=(1<<(rows*cols))-1;covers=[]
    for r in range(rows):
        for c in range(cols):
            mask=0
            for x in range(rows):
                for y in range(cols):
                    if max(abs(r-x),abs(c-y))<=k:mask|=1<<(x*cols+y)
            covers.append(mask)
    containing=[[] for _ in range(rows*cols)]
    for index,mask in enumerate(covers):
        for cell in range(rows*cols):
            if mask>>cell&1:containing[cell].append(index)
    @lru_cache(None)
    def solve(mask):
        if mask==full:return 0
        cell=((~mask)&full&-((~mask)&full)).bit_length()-1
        return 1+min(solve(mask|covers[index]) for index in containing[cell])
    return solve(0)

def random_sensors(rng):return [rng.randint(1,4),rng.randint(1,4),rng.randint(0,4)]

def pairs_oracle(args):
    nums=args[0];answer=0
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            a,b=nums[i],nums[j];low=min(abs(a-b),abs(a+b));high=max(abs(a-b),abs(a+b))
            answer+=low<=min(abs(a),abs(b)) and high>=max(abs(a),abs(b))
    return answer

def random_pairs(rng):return [[rng.randint(-30,30) for _ in range(rng.randint(2,20))]]


ACTIVATION='''def maximum_activation_total(value,limit):
    groups={}
    for score,bound in zip(value,limit):groups.setdefault(bound,[]).append(score)
    answer=0
    for bound,scores in groups.items():
        scores.sort(reverse=True);answer+=sum(scores[:bound])
    return answer
'''

SPECIAL='''_special_palindromes=None
def next_special_palindrome(n):
    global _special_palindromes
    if _special_palindromes is None:
        values=set()
        def arrange(counts,length,prefix,center):
            if len(prefix)==length:
                left=''.join(prefix);values.add(int(left+center+left[::-1]));return
            for digit in range(1,10):
                if counts[digit]:
                    counts[digit]-=1;prefix.append(str(digit));arrange(counts,length,prefix,center);prefix.pop();counts[digit]+=1
        for mask in range(1,1<<9):
            digits=[digit for digit in range(1,10) if mask>>(digit-1)&1];length=sum(digits);odd=sum(digit%2 for digit in digits)
            if length>17 or odd>1:continue
            counts=[0]*10;center=''
            for digit in digits:
                counts[digit]=digit//2
                if digit%2:center=str(digit)
            arrange(counts,sum(counts),[],center)
        _special_palindromes=sorted(values)
    import bisect
    return _special_palindromes[bisect.bisect_right(_special_palindromes,n)]
'''

BAGS='''def maximum_weight_two_bags(weights,w1,w2):
    dp=[[0]*(w2+1) for _ in range(w1+1)]
    for weight in weights:
        for first in range(w1,-1,-1):
            for second in range(w2,-1,-1):
                if weight<=first:dp[first][second]=max(dp[first][second],dp[first-weight][second]+weight)
                if weight<=second:dp[first][second]=max(dp[first][second],dp[first][second-weight]+weight)
    return dp[w1][w2]
'''

SENSORS='''def minimum_grid_sensors(n,m,k):
    width=2*k+1
    return ((n+width-1)//width)*((m+width-1)//width)
'''

PAIRS='''def count_perfect_pairs(nums):
    values=sorted(abs(value) for value in nums);zeros=0
    while zeros<len(values) and values[zeros]==0:zeros+=1
    answer=zeros*(zeros-1)//2;left=zeros
    for right in range(zeros,len(values)):
        while left<right and values[right]>2*values[left]:left+=1
        answer+=right-left
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

A_CASES=[[v,l] for v,l in (([5],[1]),([5,9],[1,1]),([1,2,3],[3,3,3]),([8,1,7,2],[2,2,2,2]),([10,20,30],[1,2,3]),([4,1,5,2],[3,3,2,3]),([6,5,4,3,2],[1,2,3,4,5]),([9,8,7,6],[2,1,2,1]),([1,100,2,99],[4,2,4,2]),([3,3,3,3],[1,2,3,4]),([12,7,15,1,20],[3,3,1,5,2]),([2,4,6,8,10,12],[2,2,4,4,6,6]))]
SP_CASES=[[0],[1],[21],[22],[211],[212],[332],[333],[1000],[9999],[123456],[10**15]]
B_CASES=[[w,a,b] for w,a,b in (([1],1,1),([2],1,2),([1,2,3],3,3),([5,8],2,3),([2,2,2],2,2),([4,5,6],10,1),([3,6,4,8],9,7),([1,1,1,1],2,2),([9,8,7,6],15,10),([2,5,3,7,4],8,9),([10,20,30],25,35),([6,6,5,5,4],11,10))]
S_CASES=[[a,b,k] for a,b,k in ((1,1,0),(1,7,0),(3,4,0),(1,10,2),(3,3,1),(4,7,1),(6,6,2),(10,3,3),(9,14,2),(1000,1000,1000),(8,9,0),(17,23,4))]
P_CASES=[[x] for x in ([0,0],[0,1],[1,2],[1,3],[-1,2],[2,4],[2,5],[-3,2,-1,5],[1,10,100,1000],[0,0,0,2],[5,-5,10,-10],[3,6,7,14,15])]

BATCH={
3645:entry('maximum_activation_total',[('value','list[int]'),('limit','list[int]')],'int',['arrays','greedy','sorting'],['The arrays have equal length up to 100,000.','Activation adds a value once; limits at or below the active count then become permanently inactive.','Choose any activation order to maximize the accumulated value.'],[([[3,5,8],[2,1,3]],'Activating values five, three, then eight collects all sixteen.'),([[4,2,6],[1,1,1]],'Only one limit-one item can activate, so choose value six.')],A_CASES,ACTIVATION,[ACTIVATION.replace('scores[:bound]','scores[:max(0,bound-1)]'),ACTIVATION.replace('scores[:bound]','scores[:1]')],['Keeps only bound minus one values from each limit group.','Keeps only one value even when a larger limit permits several activations.'],activation_oracle,random_activation,lesson('Items sharing a limit compete only for that group’s available activation slots.','For every limit L, retain the L largest values in that group.','Group by limit, sort values descending, and add each group’s top min(L,size) entries.','At most L members of a limit-L group can activate before that group is eliminated, and ordering groups by their eliminations realizes all selected entries.'),'O(n log n)','O(n)',5),
3646:entry('next_special_palindrome',[('n','int')],'int',['backtracking','palindromes','combinatorics'],['Zero <= n <= 10^15.','A present digit d must occur exactly d times.','Return the smallest qualifying palindrome strictly greater than n.'],[([2],'Twenty-two is the first larger palindrome with digit two appearing twice.'),([33],'Two hundred twelve is next; digit one occurs once and digit two occurs twice.')],SP_CASES,SPECIAL,[SPECIAL.replace('bisect.bisect_right','bisect.bisect_left'),SPECIAL.replace('if length>17 or odd>1:continue','if length>17 or odd>1 or mask&1:continue')],['Uses a non-strict search and may return n itself.','Incorrectly forbids all valid palindromes containing digit one.'],special_oracle,random_special,lesson('A palindrome’s digit counts allow at most one included odd digit, which must occupy the center.','Enumerate valid digit subsets, permute only their half-counts, and mirror each half.','Generate every valid special palindrome through length seventeen, sort them, then binary-search strictly after n.','Every valid palindrome has exactly one generated half multiset and center; mirroring enumerates all arrangements, and upper-bound search chooses the least greater value.'),'O(S log S)','O(S)',8),
3647:entry('maximum_weight_two_bags',[('weights','list[int]'),('w1','int'),('w2','int')],'int',['dynamic programming','knapsack'],['At most 100 positive item weights.','Each capacity is between one and 300.','Each item may be used in at most one bag.'],[([[1,4,3,2],5,4],'Pack three plus two in the first bag and four in the second for nine.'),([[5,7],2,3],'Neither item fits either capacity, so the result is zero.')],B_CASES,BAGS,[BAGS.replace('range(w1,-1,-1)','range(w1+1)').replace('range(w2,-1,-1)','range(w2+1)'),BAGS.replace('if weight<=second:dp[first][second]=max(dp[first][second],dp[first][second-weight]+weight)','if False:pass')],['Iterates capacities upward and can reuse the same item repeatedly.','Never considers placing an item into the second bag.'],bags_oracle,random_bags,lesson('The state is the best packed weight for a pair of remaining capacity bounds.','Use two-dimensional 0/1 knapsack and iterate both capacities downward per item.','For each item, keep the state or place it in exactly one bag when it fits.','Descending updates ensure every transition reads the prior-item layer, so no item is reused and all legal assignments are represented.'),'O(n*w1*w2)','O(w1*w2)',6),
3648:entry('minimum_grid_sensors',[('n','int'),('m','int'),('k','int')],'int',['math','greedy coverage'],['The grid dimensions are between one and 1,000.','A sensor covers a square of side at most 2k+1 under Chebyshev distance.','Return the minimum count covering every cell.'],[([5,5,1],'Each sensor spans at most three rows and columns, so a two-by-two placement uses four.'),([2,2,2],'One radius-two sensor covers the entire grid.')],S_CASES,SENSORS,[SENSORS.replace('width=2*k+1','width=k+1'),SENSORS.replace('(n+width-1)//width','n//width').replace('(m+width-1)//width','m//width')],['Uses k+1 rather than the full 2k+1 coverage width.','Rounds both one-dimensional sensor counts down instead of up.'],sensors_oracle,random_sensors,lesson('Chebyshev coverage is an axis-aligned square spanning at most 2k+1 rows and columns.','Cover each dimension with the minimum number of intervals of that width, then take their Cartesian product.','Compute ceil(n/(2k+1))*ceil(m/(2k+1)).','Each sensor covers at most one width-sized block per dimension, giving the lower bound, and evenly spaced row/column centers attain its product.'),'O(1)','O(1)',5),
3649:entry('count_perfect_pairs',[('nums','list[int]')],'int',['arrays','sorting','two pointers'],['The array has between two and 100,000 signed integers.','For each i<j, test both |a-b| and |a+b| against the smaller and larger magnitudes.','Return the number of qualifying index pairs.'],[([[0,1,2,3]],'Only magnitude pairs one-two and two-three satisfy the inequalities.'),([[-3,2,-1,4]],'Four index pairs have larger magnitude at most twice the smaller magnitude.')],P_CASES,PAIRS,[PAIRS.replace('answer=zeros*(zeros-1)//2','answer=0'),PAIRS.replace('values[right]>2*values[left]','values[right]>=2*values[left]')],['Forgets that two zeros form a valid pair.','Rejects pairs whose larger magnitude is exactly twice the smaller.'],pairs_oracle,random_pairs,lesson('For magnitudes x<=y, the two expressions are y-x and y+x regardless of signs.','The second inequality is automatic; the first becomes y<=2x, with zero pairing only with zero.','Sort absolute values, count zero-zero pairs, and use a moving left boundary for each positive right endpoint.','All indices from the first magnitude at least half of y through right-1 qualify, and monotonic sorting makes the boundary move only forward.'),'O(n log n)','O(n)',5),
}
