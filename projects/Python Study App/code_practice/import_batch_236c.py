"""Binary palindromes, task techniques, window inversions, prime sums, and dungeon scores."""
from itertools import product
from math import isqrt
from .import_batch_055 import entry


def binary_oracle(args):
    answer=[]
    for value in args[0]:
        distance=0
        while True:
            candidates=(value-distance,value+distance)
            if any(item>=0 and bin(item)[2:]==bin(item)[2:][::-1] for item in candidates):answer.append(distance);break
            distance+=1
    return answer

def random_binary(rng):return [[rng.randint(1,5000) for _ in range(rng.randint(1,15))]]

def points_oracle(args):
    first,second,k=args;answer=0
    for choices in product((0,1),repeat=len(first)):
        if sum(choice==0 for choice in choices)>=k:
            answer=max(answer,sum((first if choice==0 else second)[index] for index,choice in enumerate(choices)))
    return answer

def random_points(rng):
    n=rng.randint(1,10);return [[rng.randint(1,30) for _ in range(n)],[rng.randint(1,30) for _ in range(n)],rng.randint(0,n)]

def inversion_oracle(args):
    nums,k=args;answer=None
    for start in range(len(nums)-k+1):
        window=nums[start:start+k];value=sum(window[i]>window[j] for i in range(k) for j in range(i+1,k))
        answer=value if answer is None else min(answer,value)
    return answer

def random_inversion(rng):
    n=rng.randint(1,18);return [[rng.randint(1,12) for _ in range(n)],rng.randint(1,n)]

def prime(value):return value>=2 and all(value%factor for factor in range(2,isqrt(value)+1))
def prime_sum_oracle(args):
    n=args[0];total=answer=0
    for value in range(2,n+1):
        if prime(value):
            total+=value
            if total>n:break
            if prime(total):answer=total
    return answer

def random_prime_sum(rng):return [rng.randint(1,5000)]

def dungeon_oracle(args):
    hp,damage,requirement=args;answer=0
    for start in range(len(damage)):
        health=hp
        for room in range(start,len(damage)):
            health-=damage[room];answer+=health>=requirement[room]
    return answer

def random_dungeon(rng):
    n=rng.randint(1,14);return [rng.randint(1,50),[rng.randint(1,20) for _ in range(n)],[rng.randint(1,20) for _ in range(n)]]


BINARY='''def minimum_binary_palindrome_operations(nums):
    from bisect import bisect_left
    palindromes=[value for value in range(8192) if (bits:=bin(value)[2:])==bits[::-1]];answer=[]
    for value in nums:
        index=bisect_left(palindromes,value);best=10**9
        if index<len(palindromes):best=min(best,palindromes[index]-value)
        if index:best=min(best,value-palindromes[index-1])
        answer.append(best)
    return answer
'''

POINTS='''def maximum_task_points(technique1,technique2,k):
    order=sorted(range(len(technique1)),key=lambda index:technique1[index]-technique2[index],reverse=True);answer=sum(technique2)
    for position,index in enumerate(order):
        if position<k or technique1[index]>=technique2[index]:answer+=technique1[index]-technique2[index]
    return answer
'''

INVERSIONS='''def minimum_window_inversions(nums,k):
    ordered=sorted(set(nums));rank={value:index+1 for index,value in enumerate(ordered)};tree=[0]*(len(ordered)+1)
    def add(index,delta):
        while index<len(tree):tree[index]+=delta;index+=index&-index
    def count(index):
        answer=0
        while index:answer+=tree[index];index-=index&-index
        return answer
    inversions=0
    for seen,value in enumerate(nums[:k]):
        r=rank[value];inversions+=seen-count(r);add(r,1)
    answer=inversions
    for right in range(k,len(nums)):
        outgoing=rank[nums[right-k]];add(outgoing,-1);inversions-=count(outgoing-1)
        incoming=rank[nums[right]];inversions+=(k-1)-count(incoming);add(incoming,1);answer=min(answer,inversions)
    return answer
'''

PRIME_SUM='''def largest_consecutive_prime_sum(n):
    from math import isqrt
    if n<2:return 0
    sieve=[True]*(n+1);sieve[0]=sieve[1]=False
    for value in range(2,isqrt(n)+1):
        if sieve[value]:
            for multiple in range(value*value,n+1,value):sieve[multiple]=False
    total=answer=0
    for value in range(2,n+1):
        if sieve[value]:
            total+=value
            if total>n:break
            if sieve[total]:answer=total
    return answer
'''

DUNGEON='''def total_dungeon_run_score(hp,damage,requirement):
    from bisect import bisect_left
    prefix=[0]
    for value in damage:prefix.append(prefix[-1]+value)
    answer=0
    for room in range(1,len(prefix)):
        threshold=prefix[room]+requirement[room-1]-hp
        answer+=room-bisect_left(prefix,threshold,0,room)
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

B_CASES=[[[*values]] for values in ([1],[2],[4],[6,7,13],[3,5,9],[10,11,12],[15,16,17],[31,32,33],[100,255,256],[4998,4999,5000],[21,22,23,24],[1,8,63,64,127,128])]
P_CASES=[[a,b,k] for a,b,k in (([1],[2],0),([1],[2],1),([5,2,10],[10,3,8],1),([10,20,31],[5,15,25],2),([1,2,3],[4,5,6],0),([3,9],[8,4],1),([7,1,5],[2,9,4],2),([10,1,1,10],[1,10,10,1],2),([4,8,2,6],[7,3,9,1],3),([5,5,5],[5,5,5],2),([20,3,15,7,9],[1,18,4,12,11],2),([2,30,4,28,6,26],[29,1,27,3,25,5],4))]
I_CASES=[[a,k] for a,k in (([1],1),([2,1],1),([2,1],2),([3,1,2,5,4],2),([5,3,2,0],4),([1,1,1],2),([2,1,1],2),([1,3,2,4,0],3),([4,1,3,2,5],4),([2,2,1,1],3),([9,8,7,1,2,3],3),([5,1,4,2,3,0,6],5))]
R_CASES=[[n] for n in (1,6,3,4,5,10,17,19,21,41,100,500)]
D_CASES=[[h,d,r] for h,d,r in ((1,[1],[1]),(3,[10000,1],[1,1]),(11,[3,6,8],[4,2,5]),(10,[2,3],[5,4]),(5,[1,1,1],[1,2,3]),(20,[5,5,5],[10,5,1]),(3,[4,1,2],[1,1,1]),(50,[10,20,5,8],[5,10,20,1]),(15,[3,3,3,3],[12,9,6,3]),(100,[25,25,25],[50,25,1]),(8,[2,7,1,5],[6,1,4,2]),(30,[9,1,8,2,7],[15,20,5,10,1]))]

BATCH={
3766:entry('minimum_binary_palindrome_operations',[('nums','list[int]')],'list[int]',['arrays','binary search','bit manipulation'],['nums contains up to 5,000 values between one and 5,000.','One operation increments or decrements one value by one.','For every input value, return its minimum distance to a nonnegative integer with palindromic binary representation.'],[([[1,2,4]],'Binary one is already palindromic, while two and four are each one step from binary 11.'),([[6,7,12]],'Nearest distances to binary palindromes are one, zero, and three.')],B_CASES,BINARY,[BINARY.replace('answer.append(best)','answer.append(best+1)'),BINARY.replace('if index:best=min(best,value-palindromes[index-1])','if False:best=min(best,value-palindromes[index-1])')],['Adds one unnecessary operation to every nearest-palindrome distance.','Never considers the nearest lower binary palindrome.'],binary_oracle,random_binary,lesson('Changing by ±1 makes the cost exactly numeric distance to the target set.','Precompute all binary palindromes through the next all-ones bound above 5,000 and sort them.','Binary-search each value and compare the neighboring palindrome on each side.','In a sorted target set the nearest member must be the insertion successor or predecessor.'),'O(P+n log P)','O(P)',5),
3767:entry('maximum_task_points',[('technique1','list[int]'),('technique2','list[int]'),('k','int')],'int',['arrays','sorting','greedy'],['Both technique arrays contain the same up to 100,000 positive scores.','Choose exactly one technique per task, using technique one for at least k tasks.','Maximize the total score.'],[([[5,2,10],[10,3,8],2],'Use technique one on scores two and ten and technique two on ten, totaling twenty-two.'),([[10,20,30],[5,15,25],2],'Technique one is better on every task, so choosing it throughout gives sixty.')],P_CASES,POINTS,[POINTS.replace('reverse=True','reverse=False'),POINTS.replace('position<k or technique1[index]>=technique2[index]','position<k')],['Forces technique one on the k worst score differences.','After satisfying k, ignores additional tasks where technique one scores higher.'],points_oracle,random_points,lesson('Start with technique two everywhere; switching task i changes the total by technique1[i]-technique2[i].','Sort these gains descending, take the first k even if negative, then take every remaining nonnegative gain.','Add all selected gains to the technique-two baseline.','Any feasible choice omitting a larger forced gain for a smaller one improves by exchange, and optional positive gains always help.'),'O(n log n)','O(n)',6),
3768:entry('minimum_window_inversions',[('nums','list[int]'),('k','int')],'int',['arrays','fenwick trees','sliding windows'],['nums contains up to 100,000 positive integers and 1≤k≤n.','An inversion in a window is a pair i<j with nums[i]>nums[j].','Return the minimum inversion count among all contiguous length-k windows.'],[([[3,1,2,5,4],3],'The middle window [1,2,5] has zero inversions.'),([[5,3,2,1],4],'The only window is fully decreasing and has six inversions.')],I_CASES,INVERSIONS,[INVERSIONS.replace('inversions-=count(outgoing-1)','inversions-=count(outgoing)'),INVERSIONS.replace('(k-1)-count(incoming)','(k-1)-count(incoming-1)')],['Subtracts equal outgoing values as though they were smaller.','Counts values equal to the incoming value as greater inversions.'],inversion_oracle,random_inversion,lesson('Maintain the current window’s value frequencies in a Fenwick tree.','When removing its leftmost value, subtract remaining values smaller than it; when appending on the right, add existing values greater than it.','Coordinate-compress values, update both changes in logarithmic time, and track the minimum.','These are exactly the inversion pairs incident to the departing and arriving endpoints; all other pairs persist.'),'O(n log n)','O(n)',8),
3770:entry('largest_consecutive_prime_sum',[('n','int')],'int',['math','number theory','sieves'],['n is between one and 500,000.','Candidates are prefix sums 2, 2+3, 2+3+5, and so on.','Return the largest candidate no greater than n that is prime, or zero when none exists.'],[([20],'Prime prefix sums two, five, and seventeen are at most twenty, so return seventeen.'),([2],'The first prime prefix sum is two itself.')],R_CASES,PRIME_SUM,[PRIME_SUM.replace('if sieve[total]:answer=total','answer=total'),PRIME_SUM.replace('for value in range(2,n+1)','for value in range(3,n+1)')],['Returns the largest prime prefix sum even when that sum is composite.','Skips prime two when building consecutive sums.'],prime_sum_oracle,random_prime_sum,lesson('Only prefix sums of the prime sequence beginning at two are eligible.','Use a sieve through n, scan primes in order, accumulate their sum, and record sums that are themselves prime.','Stop when the running sum exceeds n and return the last recorded value.','The scan generates every allowed consecutive-prime prefix exactly once and the sieve tests primality exactly.'),'O(n log log n)','O(n)',5),
3771:entry('total_dungeon_run_score',[('hp','int'),('damage','list[int]'),('requirement','list[int]')],'int',['arrays','prefix sums','binary search'],['damage and requirement have equal length up to 100,000 and all values are positive.','For every starting room j, enter all rooms j..n; room i scores when health after its damage is at least requirement[i].','Return the sum of scores over every starting room.'],[([11,[3,6,7],[4,2,5]],'Across all starts, rooms earn a total of three points.'),([2,[10000,1],[1,1]],'Only starting at the second room earns a point, so the total is one.')],D_CASES,DUNGEON,[DUNGEON.replace('prefix[room]+requirement[room-1]-hp','prefix[room]-requirement[room-1]-hp'),DUNGEON.replace('answer+=room-bisect_left(prefix,threshold,0,room)','answer+=max(0,room-1-bisect_left(prefix,threshold,0,room))')],['Subtracts the health requirement instead of adding it to the damage threshold.','Undercounts one qualifying starting boundary for every scored room.'],dungeon_oracle,random_dungeon,lesson('For a fixed room i and start j, remaining health is hp-(prefix[i]-prefix[j-1]).','Rearrange the scoring condition to prefix[j-1]≥prefix[i]+requirement[i]-hp.','Damage prefixes are strictly increasing, so binary-search the first qualifying start boundary among prefixes before i and count the suffix.','Summing these counts by scored room is equivalent to summing scores by starting room.'),'O(n log n)','O(n)',6),
}
