"""Circular peaks, interval teams, digit counts, alternating primality, and binary segments."""
from itertools import permutations
from math import isqrt
from .import_batch_055 import entry

MOD=1_000_000_007

def peak_oracle(args):
    nums,k=args;n=len(nums);best=None
    for mask in range(1<<n):
        chosen=[i for i in range(n) if mask>>i&1]
        if len(chosen)<k:continue
        if n==1 and chosen:continue
        if any((i+1)%n in chosen for i in chosen):continue
        cost=sum(max(0,max(nums[(i-1)%n],nums[(i+1)%n])+1-nums[i]) for i in chosen)
        best=cost if best is None else min(best,cost)
    return -1 if best is None else best
def random_peak(rng):
    n=rng.randint(1,14);return [[rng.randint(-15,15) for _ in range(n)],rng.randint(0,n)]

def team_oracle(args):
    starts,ends=args;best=0
    for anchor in range(len(starts)):
        best=max(best,sum(not(ends[i]<starts[anchor] or starts[i]>ends[anchor]) for i in range(len(starts))))
    return best
def random_team(rng):
    n=rng.randint(1,30);starts=[];ends=[]
    for _ in range(n):
        left=rng.randint(-20,20);starts.append(left);ends.append(left+rng.randint(0,15))
    return [starts,ends]

def digit_oracle(args):return sum(str(value).count(str(args[1])) for value in args[0])
def random_digit(rng):return [[rng.randint(0,1_000_000) for _ in range(rng.randint(1,40))],rng.randint(0,9)]

def is_prime_oracle(value):return value>=2 and all(value%factor for factor in range(2,isqrt(value)+1))
def alternating_oracle(args):
    answer=0
    for index,value in enumerate(args[0]):
        want=index%2==0
        while is_prime_oracle(value)!=want:value+=1;answer+=1
    return answer
def random_alternating(rng):return [[rng.randint(0,500) for _ in range(rng.randint(1,30))]]

def segments_oracle(args):
    ones,zeros=args;best=''
    for order in permutations(range(len(ones))):
        value=''.join('1'*ones[i]+'0'*zeros[i] for i in order)
        if value>best:best=value
    result=0
    for bit in best:result=(result*2+int(bit))%MOD
    return result
def random_segments(rng):
    n=rng.randint(1,7);return [[rng.randint(0,4) for _ in range(n)],[rng.randint(0,4) for _ in range(n)]]

PEAK='''def minimum_circular_peak_operations(nums,k):
    n=len(nums)
    if k==0:return 0
    if n==1 or k>n//2:return -1
    costs=[max(0,max(nums[(i-1)%n],nums[(i+1)%n])+1-nums[i]) for i in range(n)]
    infinity=10**30
    def line(left,right,need):
        skip=[0]+[infinity]*need;take=[infinity]*(need+1)
        for i in range(left,right):
            next_skip=[min(skip[j],take[j]) for j in range(need+1)];next_take=[infinity]*(need+1)
            for j in range(1,need+1):next_take[j]=skip[j-1]+costs[i]
            skip,take=next_skip,next_take
        return min(skip[need],take[need])
    without_zero=line(1,n,k)
    with_zero=costs[0]+line(2,n-1,k-1) if k>=1 else infinity
    return min(without_zero,with_zero)
'''

TEAM='''def maximum_interval_team(start_time,end_time):
    from bisect import bisect_left,bisect_right
    intervals=list(zip(start_time,end_time));starts=sorted(start_time);ends=sorted(end_time);answer=0
    for left,right in intervals:
        ending_before=bisect_left(ends,left);starting_by=bisect_right(starts,right)
        answer=max(answer,starting_by-ending_before)
    return answer
'''

DIGIT='''def count_digit_appearances(nums,digit):
    target=str(digit);answer=0
    for value in nums:answer+=str(value).count(target)
    return answer
'''

PRIME='''def minimum_alternating_prime_increments(nums):
    from math import isqrt
    def prime(value):
        if value<2:return False
        for factor in range(2,isqrt(value)+1):
            if value%factor==0:return False
        return True
    answer=0
    for index,start in enumerate(nums):
        value=start;wanted=index%2==0
        while prime(value)!=wanted:value+=1
        answer+=value-start
    return answer
'''

SEGMENTS='''def maximum_binary_segment_value(nums1,nums0):
    modulus=1_000_000_007
    segments=list(zip(nums1,nums0))
    def key(segment):
        ones,zeros=segment
        if zeros==0:return (0,-ones,0)
        if ones:return (1,-ones,zeros)
        return (2,zeros,0)
    segments.sort(key=key);answer=0
    for ones,zeros in segments:
        for _ in range(ones):answer=(answer*2+1)%modulus
        answer=answer*pow(2,zeros,modulus)%modulus
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]
P_CASES=[[a,k] for a,k in (([2,1,2],1),([1],0),([1],1),([1,2],1),([1,2],2),([1,2,1],1),([1,1,1,1],2),([1,3,1,3],2),([5,1,5,1,5],2),([0,0,0,0,0],2),([1,2,3,4,5,6],3),([6,5,4,3,2,1],2),([10,1,10,1,10,1],3),([-1,-2,-1,-2],2),([3,1,4,1,5,9,2],3))]
T_CASES=[[a,b] for a,b in (([1,2,3],[4,5,6]),([1],[1]),([1,3],[2,4]),([1,5],[2,6]),([1,10],[10,20]),([1,2,8],[3,4,9]),([0,5,10],[6,7,12]),([3,3,3],[3,3,3]),([-5,0,5],[-1,4,9]),([1,4,7,10],[2,8,9,11]),([2,6,8],[5,7,10]),([1,100,50],[60,110,55]),([0,2,4,6],[1,3,5,7]),([10,20,30],[15,25,35]),([1,2,100,101],[3,4,102,103]))]
D_CASES=[[a,d] for a,d in (([12,54,32,22],2),([0],0),([0],1),([1],1),([10],0),([100,200],0),([111,11],1),([987654321],9),([22,222],2),([5,55,555],5),([1010,2020],0),([123,456,789],7),([999,909],9),([42,24],4),([1000000],0))]
A_CASES=[[[*v]] for v in ([1,2,3,4],[2],[1],[4,4],[2,2],[8,9,10],[0,1,2,3],[11,11,11],[14,17,20,23],[25,2,27,4],[100,101,102],[3,5,7,9],[6,8,10,12],[49,50,51],[97,2,99,4])]
S_CASES=[[a,b] for a,b in (([1,2],[1,0]),([1],[0]),([0],[1]),([1],[1]),([2,1],[0,2]),([0,1],[2,0]),([1,1],[1,1]),([3,2,1],[0,1,2]),([0,0,1],[1,2,1]),([2,0,2],[2,3,0]),([1,3,2],[2,1,2]),([4,1],[1,4]),([0,2,3],[3,0,1]),([2,2,2],[1,2,3]),([1,0,4],[3,2,0]))]

BATCH={
3892:entry('minimum_circular_peak_operations',[('nums','list[int]'),('k','int')],'int',['arrays','dynamic programming','cycles'],['nums is a nonempty circular array and k is nonnegative.','A peak is strictly greater than both circular neighbors; one operation increments one element.','Return the minimum operations producing at least k peaks, or -1 when impossible.'],[([[2,1,2],1],'Raising either value two once creates a circular peak, so one operation is enough.'),([[1],1],'The only element is also both of its own neighbors and cannot be strictly greater, so return -1.')],P_CASES,PEAK,[PEAK.replace('with_zero=costs[0]+line(2,n-1,k-1)','with_zero=infinity'),PEAK.replace('k>n//2','k>=n//2')],['Never considers solutions that select circular index zero.','Rejects feasible requests at exactly the maximum peak count.'],peak_oracle,random_peak,lesson('Chosen peaks form an independent set on the cycle, with a fixed cost to raise each above its unchanged neighbors.','Split into cases excluding index zero or including it; inclusion excludes indices one and n-1.','Solve each remaining line with take/skip DP for exactly k selected indices.','Extra peaks are never cheaper than a k-subset, so exactly k suffices; the two cases cover every circular independent set.'),'O(nk)','O(k)',8),
3893:entry('maximum_interval_team',[('startTime','list[int]'),('endTime','list[int]')],'int',['arrays','sorting','binary search'],['startTime and endTime have equal positive length and startTime[i]≤endTime[i].','A team is valid when one member’s interval overlaps every other member’s interval.','Return the maximum valid team size.'],[([[1,2,3],[4,5,6]],'The first employee overlaps both others, so all three form a valid team.'),([[1,5],[2,6]],'The intervals are disjoint, so the maximum team contains one employee.')],T_CASES,TEAM,[TEAM.replace('bisect_left(ends,left)','bisect_right(ends,left)'),TEAM.replace('bisect_right(starts,right)','bisect_left(starts,right)')],['Treats an interval ending exactly at the anchor start as disjoint.','Treats an interval starting exactly at the anchor end as disjoint.'],team_oracle,random_team,lesson('Fix the member who overlaps everyone else.','For anchor [l,r], exclude intervals ending before l and starting after r.','Sorted endpoint arrays and binary search count the remaining intervals in logarithmic time.','An interval survives exactly when it intersects the anchor, so the largest anchor count is precisely the largest valid team.'),'O(n log n)','O(n)',5),
3895:entry('count_digit_appearances',[('nums','list[int]'),('digit','int')],'int',['arrays','math','strings'],['nums contains nonnegative integers and digit is between zero and nine.','Use each integer’s ordinary decimal representation, including one zero for the number 0.','Return the total occurrences of digit across all representations.'],[([[12,54,32,22],2],'The values contain one, zero, one, and two copies of digit two, totaling four.'),([[0],0],'The decimal representation of zero contains one zero.')],D_CASES,DIGIT,[DIGIT.replace('str(value).count(target)','int(target in str(value))'),DIGIT.replace('target=str(digit)','target=str(9-digit)')],['Counts only whether the digit occurs, not all repeated appearances.','Counts the mirror digit 9-digit instead of the requested digit.'],digit_oracle,random_digit,lesson('Decimal text already represents exactly the digits that must be counted, including zero itself.','Convert the target digit once, then count it in each number’s decimal string.','Sum those per-number counts.','String conversion preserves every decimal occurrence and avoids the common loop bug that drops the number zero.'),'O(total digits)','O(1)',3),
3896:entry('minimum_alternating_prime_increments',[('nums','list[int]')],'int',['arrays','number theory'],['nums contains nonnegative integers.','After increments, even indices must be prime and odd indices must be non-prime.','Return the minimum total one-unit increments.'],[([[1,2,3,4]],'Raise one to two, two to four, and three to five; index three already has non-prime four, totaling three.'),([[2]],'Two is already prime at even index, so zero operations are needed.')],A_CASES,PRIME,[PRIME.replace('wanted=index%2==0','wanted=index%2==1'),PRIME.replace('value=start','value=start+1')],['Reverses the required prime/non-prime index pattern.','Forces at least one increment even when the starting value already qualifies.'],alternating_oracle,random_alternating,lesson('Indices are independent because incrementing one value does not affect another.','Test primality by trial division through the square root.','At each index, advance until primality matches the required parity pattern and add the distance.','The first qualifying value is the cheapest reachable value for that index, so summing independent minima is globally optimal.'),'O(total search·√M)','O(1)',5),
3897:entry('maximum_binary_segment_value',[('nums1','list[int]'),('nums0','list[int]')],'int',['arrays','greedy','sorting'],['nums1 and nums0 have equal positive length and nonnegative counts; each segment is 1 repeated nums1[i] then 0 repeated nums0[i].','Rearrange whole segments to maximize the concatenated binary integer.','Return that maximum value modulo 1,000,000,007.'],[([[1,2],[1,0]],'Ordering segment 11 before 10 produces binary 1110, decimal fourteen.'),([[1],[1]],'The only segment is binary 10, giving decimal two.')],S_CASES,SEGMENTS,[SEGMENTS.replace('segments.sort(key=key)','segments.sort(key=key,reverse=True)'),SEGMENTS.replace('answer*2+1','answer*2')],['Sorts segments in the minimizing order.','Appends zero for every claimed one bit.'],segments_oracle,random_segments,lesson('For two segments A and B, place A first exactly when concatenation AB is lexicographically at least BA.','For runs 1^a0^b this comparison reduces to: all-one segments first, mixed segments by more ones then fewer zeros, and all-zero segments last.','Stream the ordered bits modulo the prime, using a power of two to append zero runs efficiently.','The pairwise exchange rule is transitive under this key, so removing every inverted adjacent pair reaches a globally maximal concatenation.'),'O(n log n+total ones)','O(n)',8),
}
