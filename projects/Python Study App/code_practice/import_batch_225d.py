"""Digit binomials, square-boundary spacing, two-lane coins, copy shifts, and removal DP."""
from functools import lru_cache
from itertools import combinations, product

from .import_batch_055 import entry


def digits_oracle(args):
    values=[int(char) for char in args[0]]
    while len(values)>2:values=[(values[i]+values[i+1])%10 for i in range(len(values)-1)]
    return values[0]==values[1]


def random_digits(rng):return [''.join(str(rng.randrange(10)) for _ in range(rng.randint(2,20)))]


def boundary_points(side):
    return list(dict.fromkeys([(0,y) for y in range(side+1)]+[(x,side) for x in range(side+1)]+[(side,y) for y in range(side+1)]+[(x,0) for x in range(side+1)]))


def distance_oracle(args):
    _,points,k=args;answer=0
    for chosen in combinations(points,k):answer=max(answer,min(abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in combinations(chosen,2)))
    return answer


def random_distance(rng):
    side=rng.randint(1,7);available=boundary_points(side);points=rng.sample(available,rng.randint(4,min(10,len(available))))
    return [side,[list(point) for point in points],rng.randint(4,len(points))]


def coins_oracle(args):
    lane1,lane2=args;n=len(lane1);answer=-10**30
    for left in range(n):
        for right in range(left,n):
            for lanes in product(range(2),repeat=right-left+1):
                switches=(lanes[0]==1)+sum(lanes[i]!=lanes[i-1] for i in range(1,len(lanes)))
                if switches<=2:answer=max(answer,sum((lane1,lane2)[lane][left+i] for i,lane in enumerate(lanes)))
    return answer


def random_coins(rng):
    n=rng.randint(1,8);return [[rng.randint(-10,10) for _ in range(n)],[rng.randint(-10,10) for _ in range(n)]]


def copies_oracle(args):
    original,bounds=args;low=min(left-value for value,(left,_) in zip(original,bounds))-1;high=max(right-value for value,(_,right) in zip(original,bounds))+1
    return sum(all(left<=value+shift<=right for value,(left,right) in zip(original,bounds)) for shift in range(low,high+1))


def random_copies(rng):
    n=rng.randint(1,12);original=[rng.randint(-10,10) for _ in range(n)];bounds=[]
    for _ in range(n):
        left=rng.randint(-15,10);bounds.append([left,rng.randint(left,15)])
    return [original,bounds]


def removal_oracle(args):
    @lru_cache(None)
    def solve(values):
        if len(values)<3:return max(values,default=0)
        return min(max(values[i],values[j])+solve(tuple(value for index,value in enumerate(values) if index not in (i,j))) for i,j in combinations(range(3),2))
    return solve(tuple(args[0]))


def random_removal(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,10))]]


def palindrome_oracle(args):
    text,k=args;answer=0
    for mask in range(1<<len(text)):
        chosen=[text[index] for index in range(len(text)) if mask>>index&1];cost=0
        for index in range(len(chosen)//2):
            distance=abs(ord(chosen[index])-ord(chosen[-1-index]));cost+=min(distance,26-distance)
        if cost<=k:answer=max(answer,len(chosen))
    return answer


def random_palindrome(rng):return [''.join(rng.choice('abcdefxyz') for _ in range(rng.randint(1,10))),rng.randint(1,12)]


DIGITS='''def final_reduced_digits_equal(s):
    row=len(s)-2
    def choose_mod_five(n,k):
        answer=1
        while n or k:
            a=n%5;b=k%5
            if b>a:return 0
            table=((1,0,0,0,0),(1,1,0,0,0),(1,2,1,0,0),(1,3,3,1,0),(1,4,1,4,1));answer=answer*table[a][b]%5;n//=5;k//=5
        return answer
    left=right=0
    for index in range(row+1):
        mod_two=1 if index&~row==0 else 0;mod_five=choose_mod_five(row,index);coefficient=next(value for value in range(mod_five,10,5) if value%2==mod_two)
        left=(left+coefficient*int(s[index]))%10;right=(right+coefficient*int(s[index+1]))%10
    return left==right
'''

DISTANCE='''def maximize_square_boundary_distance(side,points,k):
    from bisect import bisect_left
    perimeter=4*side;positions=[]
    for x,y in points:
        if x==0:positions.append(y)
        elif y==side:positions.append(side+x)
        elif x==side:positions.append(3*side-y)
        else:positions.append(4*side-x)
    positions.sort()
    def possible(gap):
        for start in positions:
            current=start;end=start+perimeter-gap
            for _ in range(k-1):
                index=bisect_left(positions,current+gap)
                if index==len(positions) or positions[index]>end:break
                current=positions[index]
            else:return True
        return False
    low=0;high=side+1
    while low+1<high:
        middle=(low+high)//2
        if possible(middle):low=middle
        else:high=middle
    return low
'''

COINS='''def maximum_two_lane_coins(lane1,lane2):
    negative=-10**30;previous=[[negative,negative] for _ in range(3)];answer=negative
    for first,second in zip(lane1,lane2):
        current=[[negative,negative] for _ in range(3)]
        for switches in range(3):
            current[switches][0]=first+max(previous[switches][0],0 if switches==0 else negative)
            current[switches][1]=second+max(previous[switches][1],0 if switches==1 else negative)
            if switches:current[switches][0]=max(current[switches][0],first+previous[switches-1][1]);current[switches][1]=max(current[switches][1],second+previous[switches-1][0])
        previous=current;answer=max(answer,max(max(row) for row in current))
    return answer
'''

COPIES='''def count_difference_preserving_copies(original,bounds):
    low=-10**30;high=10**30
    for value,(left,right) in zip(original,bounds):low=max(low,left-value);high=min(high,right-value)
    return max(0,high-low+1)
'''

REMOVAL='''def minimum_front_three_removal_cost(nums):
    from functools import lru_cache
    @lru_cache(None)
    def solve(index,carry):
        if index>=len(nums):return carry
        if index==len(nums)-1:return max(carry,nums[index])
        first,second=nums[index],nums[index+1]
        return min(max(first,second)+solve(index+2,carry),max(carry,second)+solve(index+2,first),max(carry,first)+solve(index+2,second))
    return solve(1,nums[0])
'''

PALINDROME='''def longest_budget_palindromic_subsequence(s,k):
    from functools import lru_cache
    @lru_cache(None)
    def solve(left,right,budget):
        if left>right:return 0
        if left==right:return 1
        answer=max(solve(left+1,right,budget),solve(left,right-1,budget));distance=abs(ord(s[left])-ord(s[right]));cost=min(distance,26-distance)
        if cost<=budget:answer=max(answer,2+solve(left+1,right-1,budget-cost))
        return answer
    return solve(0,len(s)-1,k)
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


DIGIT_CASES=[[text] for text in ['3902','34789','11','10','00','99','123','909','1234','55555','314159','987654321','10101010','0123456789']]
DISTANCE_CASES=[[side,[list(point) for point in boundary_points(side)[:min(8,4*side)]],min(4+side%4,8,4*side)] for side in range(1,15)]
COIN_CASES=[[a,b] for a,b in [([1,-2,-10,3],[-5,10,0,1]),([5],[-1]),([-5],[7]),([1,2],[3,4]),([-1,-2],[-3,-4]),([10,-20,10],[0,15,0]),([1,1,1],[2,2,2]),([5,-100,5],[1,1,1]),([-5,10,-5,10],[10,-5,10,-5]),([3,-2,4,-1,5],[-1,6,-3,7,-2]),([0,0,0],[0,0,0]),([9,-9,9,-9,9],[1,1,1,1,1]),([2,8,-20,8,2],[7,-1,7,-1,7]),([-10,5,6,-10],[4,-2,-2,4])]]
COPY_CASES=[[original,bounds] for original,bounds in [([1,2,3,4],[[1,2],[2,3],[3,4],[4,5]]),([1,2,3],[[1,1],[2,2],[3,3]]),([1],[[0,5]]),([5],[[5,5]]),([1,3],[[0,2],[4,5]]),([1,3],[[0,0],[0,0]]),([-1,2],[[0,3],[3,6]]),([10,5,0],[[8,12],[3,7],[-2,2]]),([0,0,0],[[-1,1],[-2,2],[0,3]]),([3,1,4],[[1,9],[-1,5],[2,8]]),([100,200],[[0,100],[100,200]]),([2,4,6,8],[[1,3],[3,5],[5,7],[7,9]]),([-5,-3],[[0,2],[2,4]]),([7,7,7],[[1,10],[5,8],[6,9]])]]
REMOVAL_CASES=[[[value for value in nums]] for nums in [[6,2,8,4],[1],[1,2],[1,2,3],[3,2,1],[5,5,5],[10,1,1,10],[1,9,2,8,3],[4,7,2,9,1,6],[100,1,50],[2,8,4,6,10,12],[9,3,7,1,5,2,8],[1,100,1,100,1],[5,4,3,2,1,6,7,8]]]
PALINDROME_CASES=[[text,k] for text,k in [('abced',2),('aaazzz',4),('a',1),('ab',1),('az',1),('abc',1),('abc',2),('racecar',1),('xyzzy',2),('leetcode',5),('aaaa',3),('zbyaz',2),('abcdef',10),('azbycxdw',6)]]


BATCH={
3463:entry('final_reduced_digits_equal',[('s','str')],'bool',['strings','combinatorics','number theory'],['s has 2–100,000 decimal digits.','Replace every adjacent pair by its sum modulo ten, shortening the string by one, until two digits remain.','Return whether those final two digits are equal.'],[(['3902'],'Repeated adjacent sums reduce the string to two equal digits.'),(['10'],'The input already has two unequal digits, so return false.')],DIGIT_CASES,DIGITS,[DIGITS.replace('row=len(s)-2','row=max(0,len(s)-3)'),DIGITS.replace('coefficient=next(value for value in range(mod_five,10,5) if value%2==mod_two)','coefficient=mod_two')],['Uses the preceding Pascal row and applies the wrong binomial coefficients.','Uses coefficients modulo two only instead of reconstructing them modulo ten.'],digits_oracle,random_digits,lesson('After all reductions, each final digit is a binomially weighted sum of an adjacent length-(n-1) slice.','Compute row n-2 binomial coefficients modulo two and five with Lucas’s theorem, then combine residues modulo ten.','For every coefficient, evaluate its base-two inclusion test and base-five digit product; use CRT and accumulate the two shifted sums.','Pascal’s identity exactly mirrors one reduction round, while CRT is valid because ten factors into coprime two and five.'),'O(n log_5 n)','O(1)',8),
3464:entry('maximize_square_boundary_distance',[('side','int'),('points','list[list[int]]'),('k','int')],'int',['geometry','binary search','greedy'],['At least four distinct integer points lie on the boundary of a square with positive side length.','Choose k points, where 4 <= k <= min(25,len(points)).','Maximize the minimum Manhattan distance between every selected pair.'],[([2,[[0,2],[2,0],[2,2],[0,0]],4],'Selecting all four corners gives pairwise Manhattan distance at least two.'),([2,[[0,0],[1,2],[2,0],[2,2],[2,1]],4],'The best four-point selection has minimum Manhattan distance one.')],DISTANCE_CASES,DISTANCE,[DISTANCE.replace('return low','return max(0,low-1)'),DISTANCE.replace('for start in positions:','for start in positions[:1]:')],['Returns one below the final feasible binary-search boundary.','Treats the first sorted point as the only possible circular cut and misses solutions that wrap elsewhere.'],distance_oracle,random_distance,lesson('For candidate distances up to the side length, Manhattan separation of boundary points is equivalent to circular perimeter separation.','Map points clockwise to one coordinate, greedily select the next point at least the candidate gap away, and try every first point.','Reserve a final gap before the perimeter wraps to the start; binary-search the largest feasible gap.','Earliest-next greedy leaves maximum room for remaining selections, and trying every cyclic cut covers every optimal chosen set.'),'O(p*k*log p*log side)','O(p)',8),
3466:entry('maximum_two_lane_coins',[('lane1','list[int]'),('lane2','list[int]')],'int',['arrays','dynamic programming'],['lane arrays have equal nonzero length and may contain gains or losses.','Enter at any mile on lane one, travel forward at least one mile, and switch lanes at most twice; an immediate switch allows beginning collection on lane two.','Choose the entry, exit, and switches to maximize collected coins.'],[([[1,-2,-10,3],[-5,10,0,1]],'Enter lane one, use beneficial switches, and exit with a maximum collection of fourteen.'),([[-5],[7]],'Enter lane one and immediately switch before collecting to take seven from lane two.')],COIN_CASES,COINS,[COINS.replace('0 if switches==1 else negative','0 if switches==0 else negative'),COINS.replace('range(3)','range(2)')],['Starts directly on lane two without charging the required initial switch.','Allows only one switch instead of two.'],coins_oracle,random_coins,lesson('The best route ending at a mile depends only on its lane and switches used.','Maintain six maximum-subarray states, permitting a fresh lane-one start or a lane-two start that consumes one switch.','At each mile extend the same lane, transition from the other lane with one more switch, or initialize a legal route; update the global best.','Every route has one final-mile state and one of these predecessors, so the recurrence covers all entry, exit, and switch choices.'),'O(n)','O(1)',6),
3468:entry('count_difference_preserving_copies',[('original','list[int]'),('bounds','list[list[int]]')],'int',['arrays','interval intersection'],['original and bounds have equal nonzero length; each bound is an inclusive [low,high] interval.','Every adjacent difference in copy must equal the corresponding difference in original.','Count integer copy arrays satisfying every positional bound.'],[([[1,2,3,4],[[1,2],[2,3],[3,4],[4,5]]],'The valid common shifts are zero and one, producing two arrays.'),([[1,3],[[0,0],[0,0]]],'No common shift can place both values at zero while preserving their difference, so return zero.')],COPY_CASES,COPIES,[COPIES.replace('high-low+1','high-low'),COPIES.replace('left-value','left').replace('right-value','right')],['Treats inclusive shift endpoints as exclusive and undercounts by one.','Intersects raw bounds without translating them by original values.'],copies_oracle,random_copies,lesson('Equal adjacent differences force every copy value to equal original[i] plus one shared integer shift.','Translate each positional bound into an allowed shift interval and intersect them all.','Update the maximum lower shift and minimum upper shift; return the inclusive intersection size or zero.','A chosen first value fixes the shared shift and therefore the entire copy, giving a one-to-one correspondence with feasible shifts.'),'O(n)','O(1)',5),
3469:entry('minimum_front_three_removal_cost',[('nums','list[int]')],'int',['arrays','dynamic programming','recursion'],['nums is a nonempty positive-integer array.','While at least three remain, remove any two of the first three and pay their maximum.','When fewer than three remain, remove all and pay their maximum; minimize total cost.'],[([[6,2,8,4]],'Choosing which value survives the first operation yields a minimum total cost of twelve.'),([[1,2]],'Fewer than three values remain, so remove both once at cost two.')],REMOVAL_CASES,REMOVAL,[REMOVAL.replace('return min(max(first,second)+solve(index+2,carry),max(carry,second)+solve(index+2,first),max(carry,first)+solve(index+2,second))','return max(carry,first)+solve(index+2,second)'),REMOVAL.replace('return max(carry,nums[index])','return carry+nums[index]')],['Always removes the first two available values and never compares the other survivor choices.','Charges the sum of the final two elements instead of their maximum.'],removal_oracle,random_removal,lesson('After each operation, exactly one of the first three survives to join the next two untouched values.','Memoize by the next untouched index and the surviving value.','Try keeping each of the three candidates, add the maximum of the removed pair, and recurse two positions forward; handle one or two leftovers directly.','The state contains the full remaining prefix information, and the three transitions exhaust every legal removal choice.'),'O(n^2)','O(n^2)',6),
3472:entry('longest_budget_palindromic_subsequence',[('s','str'),('k','int')],'int',['strings','dynamic programming','recursion'],['s has 1–200 lowercase letters and 1 <= k <= 200.','One operation moves one chosen character one alphabet step forward or backward, wrapping between a and z.','Return the longest palindromic subsequence obtainable with at most k operations.'],[(['abced',2],'Two character changes allow a palindromic subsequence of length three.'),(['aaazzz',4],'Using wraparound changes makes the entire six-character string palindromic within the budget.')],PALINDROME_CASES,PALINDROME,[PALINDROME.replace('cost=min(distance,26-distance)','cost=distance'),PALINDROME.replace('if cost<=budget:','if cost==0:')],['Uses linear alphabet distance and ignores the cheaper wraparound path.','Pairs only already-equal characters and never spends the available operation budget.'],palindrome_oracle,random_palindrome,lesson('Matching two endpoint letters costs their shortest circular alphabet distance.','Memoize the best subsequence length for an interval and remaining budget.','Either skip the left endpoint, skip the right endpoint, or pay their match cost and take both when affordable.','Every palindromic subsequence makes one of these endpoint choices; memoization selects the longest feasible result over all choices.'),'O(n^2*k)','O(n^2*k)',6),
}
