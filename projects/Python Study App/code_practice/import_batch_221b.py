"""Tourist DP, run-length counting, factor scores, transformations, and GCD pairs."""
from itertools import product
from math import gcd,lcm
from .import_batch_055 import entry


MOD=1_000_000_007


def tourist_oracle(args):
    n,k,stay,travel=args;answer=0
    for route in product(range(n),repeat=k+1):
        score=sum(stay[day][route[day]] if route[day]==route[day+1] else travel[route[day]][route[day+1]] for day in range(k))
        answer=max(answer,score)
    return answer


def random_tourist(rng):
    n=rng.randint(1,4);k=rng.randint(1,4)
    stay=[[rng.randint(1,12) for _ in range(n)] for _ in range(k)]
    travel=[[0 if a==b else rng.randint(0,12) for b in range(n)] for a in range(n)]
    return [n,k,stay,travel]


def run_lengths(word):
    lengths=[]
    for char in word:
        if lengths and char==lengths[-1][0]:lengths[-1][1]+=1
        else:lengths.append([char,1])
    return [item[1] for item in lengths]


def typed_oracle(args):
    word,k=args;answer=0
    for lengths in product(*(range(1,size+1) for size in run_lengths(word))):
        answer+=sum(lengths)>=k
    return answer%MOD


def random_typed(rng):
    groups=rng.randint(1,7);parts=[];last=''
    for _ in range(groups):
        char=rng.choice([c for c in 'abcd' if c!=last]);last=char
        parts.append(char*rng.randint(1,4))
    word=''.join(parts)
    return [word,rng.randint(1,len(word))]


def factor_oracle(args):
    nums=args[0];answer=0
    for removed in range(-1,len(nums)):
        kept=[value for index,value in enumerate(nums) if index!=removed]
        if not kept:score=0
        else:
            common=0;multiple=1
            for value in kept:common=gcd(common,value);multiple=lcm(multiple,value)
            score=common*multiple
        answer=max(answer,score)
    return answer


def random_factor(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,9))]]


def transform_oracle(args):
    text,t=args
    for _ in range(t):text=''.join('ab' if char=='z' else chr(ord(char)+1) for char in text)
    return len(text)%MOD


def random_transform(rng):return [''.join(rng.choice('awxyz') for _ in range(rng.randint(1,12))),rng.randint(1,8)]


def gcd_pair_oracle(args):
    nums=args[0];answer=0
    for choices in product(range(3),repeat=len(nums)):
        first=second=0
        for value,choice in zip(nums,choices):
            if choice==1:first=gcd(first,value)
            elif choice==2:second=gcd(second,value)
        answer+=first!=0 and first==second
    return answer%MOD


def random_gcd_pair(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,8))]]


TOURIST='''def maximum_tourist_points(n,k,stay_score,travel_score):
    previous=[0]*n
    for day in range(k):
        current=[0]*n
        for destination in range(n):
            current[destination]=max(previous[origin]+(stay_score[day][destination] if origin==destination else travel_score[origin][destination]) for origin in range(n))
        previous=current
    return max(previous)
'''

TYPED='''def count_possible_original_strings(word,k):
    modulo=1000000007;runs=[]
    for char in word:
        if runs and char==runs[-1][0]:runs[-1][1]+=1
        else:runs.append([char,1])
    total=1
    for _,length in runs:total=total*length%modulo
    if len(runs)>=k:return total
    ways=[0]*k;ways[0]=1
    for _,length in runs:
        prefix=[0]*(k+1)
        for size in range(k):prefix[size+1]=(prefix[size]+ways[size])%modulo
        next_ways=[0]*k
        for size in range(1,k):next_ways[size]=(prefix[size]-prefix[max(0,size-length)])%modulo
        ways=next_ways
    return (total-sum(ways))%modulo
'''

FACTOR='''def maximum_factor_score(nums):
    from math import gcd,lcm
    n=len(nums);suffix_gcd=[0]*(n+1);suffix_lcm=[1]*(n+1)
    for index in range(n-1,-1,-1):
        suffix_gcd[index]=gcd(suffix_gcd[index+1],nums[index]);suffix_lcm[index]=lcm(suffix_lcm[index+1],nums[index])
    answer=suffix_gcd[0]*suffix_lcm[0];prefix_gcd=0;prefix_lcm=1
    for index,value in enumerate(nums):
        answer=max(answer,gcd(prefix_gcd,suffix_gcd[index+1])*lcm(prefix_lcm,suffix_lcm[index+1]))
        prefix_gcd=gcd(prefix_gcd,value);prefix_lcm=lcm(prefix_lcm,value)
    return answer
'''

TRANSFORM='''def transformed_string_length(s,t):
    modulo=1000000007;counts=[0]*26
    for char in s:counts[ord(char)-97]+=1
    for _ in range(t):
        z=counts[25];counts=[z,(counts[0]+z)%modulo]+counts[1:25]
    return sum(counts)%modulo
'''

GCD_PAIRS='''def equal_gcd_subsequence_pairs(nums):
    from math import gcd
    modulo=1000000007;states={(0,0):1}
    for value in nums:
        updated=dict(states)
        for (first,second),count in states.items():
            a=(gcd(first,value),second);b=(first,gcd(second,value))
            updated[a]=(updated.get(a,0)+count)%modulo
            updated[b]=(updated.get(b,0)+count)%modulo
        states=updated
    return sum(count for (first,second),count in states.items() if first and first==second)%modulo
'''


def lesson(a,b,c,d):return [a,b,c,d]


TOURIST_CASES=[[n,k,s,t] for n,k,s,t in [(1,1,[[5]],[[0]]),(1,3,[[1],[2],[3]],[[0]]),(2,1,[[1,1]],[[0,5],[4,0]]),(2,2,[[5,1],[1,5]],[[0,2],[3,0]]),(2,3,[[1,4],[5,1],[2,2]],[[0,6],[3,0]]),(3,1,[[2,8,3]],[[0,1,9],[4,0,2],[3,7,0]]),(3,2,[[1,2,3],[3,2,1]],[[0,4,1],[2,0,5],[6,1,0]]),(3,3,[[4,1,2],[1,7,1],[3,1,8]],[[0,3,2],[5,0,4],[1,6,0]]),(2,2,[[100,1],[1,100]],[[0,0],[0,0]]),(2,2,[[1,1],[1,1]],[[0,100],[100,0]]),(3,2,[[9,1,1],[1,9,1]],[[0,8,2],[3,0,7],[6,4,0]]),(4,1,[[1,2,3,4]],[[0,1,2,3],[4,0,5,6],[7,8,0,9],[1,2,3,0]]),(2,4,[[2,3],[4,1],[1,5],[6,2]],[[0,3],[7,0]]),(3,2,[[5,5,5],[5,5,5]],[[0,5,5],[5,0,5],[5,5,0]])]]
TYPED_CASES=[[w,k] for w,k in [('a',1),('aaaa',1),('aaaa',4),('aaaa',3),('ab',1),('ab',2),('aaabbb',3),('aaabbb',5),('aabbcc',4),('aabbcc',6),('abcabc',4),('zzzy',2),('aabbaa',5),('abbcccdddd',7)]]
FACTOR_CASES=[[[x for x in values]] for values in [[1],[3],[1,1],[2,3],[2,4],[2,4,8],[6,10,15],[1,2,3,5],[5,5,5],[2,3,5,7],[4,8,16,32],[6,12,18,24],[7,14,21],[30,1,1,1]]]
TRANSFORM_CASES=[[s,t] for s,t in [('a',1),('z',1),('z',2),('y',2),('az',1),('zz',1),('xyz',3),('abc',26),('leetcode',5),('yyyy',2),('wxyz',4),('a',30),('zzzzz',8),('algorithm',10)]]
GCD_CASES=[[[x for x in values]] for values in [[1],[2],[1,1],[2,2],[1,2],[2,4],[2,4,6],[3,6,9],[6,10,15],[1,1,1],[2,3,5],[4,8,16,32],[6,6,3,3],[1,2,1,2]]]


BATCH={
3332:entry('maximum_tourist_points',[('n','int'),('k','int'),('stay_score','list[list[int]]'),('travel_score','list[list[int]]')],'int',['dynamic programming','matrices'],['There are 1–200 cities and exactly 1–200 days; the tourist may start in any city.','Staying on day d in city c earns stay_score[d][c]; moving from origin to a different destination earns travel_score[origin][destination].','Return the maximum total over all valid city routes.'],[([2,1,[[2,3]],[[0,2],[1,0]]],'Starting in city 1 and staying earns three, better than either move.'),([3,2,[[3,4,2],[2,1,2]],[[0,2,1],[2,0,4],[3,2,0]]],'Stay in city 1 for four points, then move to city 2 for four more.')],TOURIST_CASES,TOURIST,[TOURIST.replace('previous=[0]*n','previous=[0]+[-10**9]*(n-1)'),TOURIST.replace('travel_score[origin][destination]','travel_score[destination][origin]')],['Forces the tourist to start in city zero.','Reads travel points in the reverse direction.'],tourist_oracle,random_tourist,lesson('The only history needed after a day is the best score ending in each city.','For every destination, try staying from itself or traveling from every other origin.','Initialize every possible start at zero; repeat k destination transitions; return the best endpoint.','Each route has one previous endpoint, so the transition considers every route exactly through its best prefix.'),'O(kn²)','O(n)',6),
3333:entry('count_possible_original_strings',[('word','str'),('k','int')],'int',['strings','dynamic programming','prefix sums'],['word has 1–500,000 lowercase letters and 1 <= k <= 2,000.','Each maximal equal-character run of length r could originate from choosing 1 through r copies of that character.','Count possible original strings whose total length is at least k, modulo 1,000,000,007.'],[(['aabbccdd',7],'Four binary run-length choices yield five originals of length at least seven.'),(['aabbccdd',8],'Only choosing both characters from all four runs reaches length eight.')],TYPED_CASES,TYPED,[TYPED.replace('if len(runs)>=k:return total','if len(runs)+1>=k:return total'),TYPED.replace('total-sum(ways)','total+sum(ways)')],['Returns all run-length choices when the minimum possible original length is still one below k.','Adds invalid short originals instead of subtracting them.'],typed_oracle,random_typed,lesson('A displayed run of length r represents exactly r possible intended run lengths.','Count all products, then subtract choices whose total intended length is below k.','Use a length DP truncated at k and prefix sums for each run’s 1..r transition.','Run choices are independent, and the DP partitions all combinations by total length before the final complement.'),'O(rk)','O(k)',8),
3334:entry('maximum_factor_score',[('nums','list[int]')],'int',['arrays','number theory','prefix and suffix'],['nums has 1–100 values in 1..30.','A nonempty array scores gcd(all values) multiplied by lcm(all values); the empty array scores zero.','Remove at most one element and return the largest score.'],[([[2,4,8,16]],'Removing two leaves GCD 4 and LCM 16, for a score of 64.'),([[1,2,3,4,5]],'Keeping every value gives GCD 1 and LCM 60, which is optimal.')],FACTOR_CASES,FACTOR,[FACTOR.replace('answer=suffix_gcd[0]*suffix_lcm[0]','answer=0'),FACTOR.replace('suffix_lcm=[1]*(n+1)','suffix_lcm=[0]*(n+1)')],['Requires removing one element and ignores the legal keep-all score.','Uses zero as the empty LCM identity, making all suffix LCM values zero.'],factor_oracle,random_factor,lesson('Removing one position combines the aggregates strictly before and after it.','Precompute suffix GCD/LCM, then sweep a prefix pair of aggregates.','Start with the keep-all score; for each removal combine prefix and suffix using identities GCD 0 and LCM 1.','Associativity of GCD and LCM makes the two sides exactly equal to aggregating every retained element.'),'O(n log V)','O(n)',5),
3335:entry('transformed_string_length',[('s','str'),('t','int')],'int',['strings','dynamic programming','counting'],['s has 1–100,000 lowercase letters and 1 <= t <= 100,000.','Each simultaneous step changes z to ab and every other letter to its alphabet successor.','Return the final length modulo 1,000,000,007 without constructing the expanded string.'],[(['abcyy',2],'The transformations are bcdzz and then cdeabab, whose length is seven.'),(['azbk',1],'The z produces two characters while the other three each produce one, for length five.')],TRANSFORM_CASES,TRANSFORM,[TRANSFORM.replace("z=counts[25]","z=0"),TRANSFORM.replace("counts=[z,(counts[0]+z)%modulo]+counts[1:25]","counts=[z,counts[0]]+counts[1:25]")],['Drops every z instead of expanding it to a and b.','Creates only a from each z and omits its additional b.'],transform_oracle,random_transform,lesson('Only the count of each letter matters because every occurrence transforms independently.','Shift the 26 frequency buckets; split the old z bucket into new a and b contributions.','Repeat t times with modular counts, then sum all letter frequencies.','The bucket transition is exactly the simultaneous character rule and preserves the full multiset size information.'),'O(len(s)+26t)','O(26)',6),
3336:entry('equal_gcd_subsequence_pairs',[('nums','list[int]')],'int',['dynamic programming','number theory','subsequences'],['nums has 1–200 values in 1..200.','Assign indices to two ordered, nonempty, disjoint subsequences or to neither; subsequence order follows nums.','Count assignments whose two subsequence GCDs are equal, modulo 1,000,000,007.'],[([[1,2,3,4]],'Ten ordered disjoint subsequence pairs have equal GCD one.'),([[10,20,30]],'The two valid ordered pairs swap [10] and [20,30], both with GCD ten.')],GCD_CASES,GCD_PAIRS,[GCD_PAIRS.replace('if first and first==second','if first==second'),GCD_PAIRS.replace('b=(first,gcd(second,value))','b=(first,value)')],['Counts the state where both subsequences are empty.','Tracks only the last value placed in the second subsequence instead of its GCD.'],gcd_pair_oracle,random_gcd_pair,lesson('Each index has three disjoint choices: unused, first subsequence, or second subsequence.','Aggregate prefixes by the pair of GCDs produced so far, using zero as the empty identity.','Copy states for unused; add transitions gcd(first,x) and gcd(second,x); sum equal nonzero pairs.','The three transitions are exhaustive and mutually exclusive, while the state retains exactly what future GCD updates need.'),'O(nV²)','O(V²)',8),
}
