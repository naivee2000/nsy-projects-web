"""Adjacent-array counts, maximal suffixes, decreasing differences, and subarrays."""
from itertools import combinations, product
from math import gcd, lcm

from .import_batch_055 import entry

MOD=1_000_000_007


def arrays_oracle(args):
    n,m,k=args
    return sum(sum(values[i]==values[i-1] for i in range(1,n))==k for values in product(range(1,m+1),repeat=n))%MOD


def random_arrays(rng):
    n=rng.randint(1,7)
    return [n,rng.randint(1,4),rng.randint(0,n-1)]


def box_oracle(args):
    word,friends=args
    if friends==1:return word
    pieces=[]
    for cuts in combinations(range(1,len(word)),friends-1):
        points=(0,)+cuts+(len(word),)
        pieces.extend(word[points[i]:points[i+1]] for i in range(friends))
    return max(pieces)


def random_box(rng):
    n=rng.randint(1,9)
    return [''.join(rng.choice('abcd') for _ in range(n)),rng.randint(1,n)]


def decreasing_oracle(args):
    nums=args[0];answer=1
    for mask in range(1,1<<len(nums)):
        values=[nums[i] for i in range(len(nums)) if mask>>i&1]
        differences=[abs(values[i]-values[i-1]) for i in range(1,len(values))]
        if all(differences[i]<=differences[i-1] for i in range(1,len(differences))):answer=max(answer,len(values))
    return answer


def random_decreasing(rng):
    return [[rng.randint(1,12) for _ in range(rng.randint(2,11))]]


def kadane(values):
    best=current=values[0]
    for value in values[1:]:current=max(value,current+value);best=max(best,current)
    return best


def removal_oracle(args):
    nums=args[0];answer=kadane(nums)
    for value in set(nums):
        remaining=[number for number in nums if number!=value]
        if remaining:answer=max(answer,kadane(remaining))
    return answer


def random_removal(rng):
    return [[rng.randint(-8,8) for _ in range(rng.randint(1,11))]]


def equal_products_oracle(args):
    nums=args[0];answer=0
    for left in range(len(nums)):
        for right in range(left,len(nums)):
            values=nums[left:right+1];p=1;g=0;l=1
            for value in values:p*=value;g=gcd(g,value);l=lcm(l,value)
            if p==g*l:answer=max(answer,len(values))
    return answer


def random_equal_products(rng):
    return [[rng.randint(1,10) for _ in range(rng.randint(2,12))]]


ARRAYS='''def count_arrays_with_k_equal_neighbors(n,m,k):
    modulo=1000000007
    def choose(total,take):
        if take<0 or take>total:return 0
        numerator=denominator=1
        for value in range(1,take+1):numerator=numerator*(total-take+value)%modulo;denominator=denominator*value%modulo
        return numerator*pow(denominator,modulo-2,modulo)%modulo
    return choose(n-1,k)*m*pow(m-1,n-k-1,modulo)%modulo
'''

BOX='''def largest_string_from_box_large(word,num_friends):
    if num_friends==1:return word
    first=0;second=1;matched=0;n=len(word)
    while second+matched<n:
        if word[first+matched]==word[second+matched]:matched+=1
        elif word[first+matched]<word[second+matched]:
            first=max(first+matched+1,second);second=first+1;matched=0
        else:second+=matched+1;matched=0
    return word[first:first+n-num_friends+1]
'''

DECREASING='''def longest_decreasing_difference_subsequence(nums):
    maximum=300;exact=[[0]*maximum for _ in range(maximum+1)];best=[[0]*(maximum+1) for _ in range(maximum+1)];seen=[False]*(maximum+1);answer=1
    for value in nums:
        updates={}
        for previous in range(1,maximum+1):
            if seen[previous]:
                difference=abs(value-previous);updates[difference]=max(updates.get(difference,0),best[previous][difference]+1)
        seen[value]=True
        for difference,length in updates.items():exact[value][difference]=max(exact[value][difference],length);answer=max(answer,length)
        running=1
        for difference in range(maximum-1,-1,-1):
            running=max(running,exact[value][difference]);best[value][difference]=running
    return answer
'''

REMOVAL='''def maximum_subarray_after_value_removal(nums):
    size=1
    while size<len(nums):size*=2
    tree=[None]*(2*size)
    def combine(left,right):
        if left is None:return right
        if right is None:return left
        return (left[0]+right[0],max(left[1],left[0]+right[1]),max(right[2],right[0]+left[2]),max(left[3],right[3],left[2]+right[1]))
    def update(index,value):
        position=size+index;tree[position]=(value,value,value,value);position//=2
        while position:tree[position]=combine(tree[2*position],tree[2*position+1]);position//=2
    positions={}
    for index,value in enumerate(nums):update(index,value);positions.setdefault(value,[]).append(index)
    answer=tree[1][3]
    for value in positions:
        if value>=0 or len(positions[value])==len(nums):continue
        for index in positions[value]:update(index,0)
        if tree[1][3]>0:answer=max(answer,tree[1][3])
        for index in positions[value]:update(index,value)
    return answer
'''

EQUAL_PRODUCTS='''def maximum_equal_product_subarray(nums):
    from math import gcd,lcm
    answer=0
    for left in range(len(nums)):
        product=1;common=0;multiple=1
        for right in range(left,len(nums)):
            value=nums[right];product*=value;common=gcd(common,value);multiple=lcm(multiple,value)
            if product==common*multiple:answer=max(answer,right-left+1)
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


ARRAY_CASES=[[n,m,k] for n,m,k in [(3,2,1),(1,1,0),(1,5,0),(2,2,0),(2,2,1),(3,1,2),(4,3,0),(4,3,1),(4,3,3),(5,2,2),(6,4,3),(7,2,0),(7,3,6),(10,5,4)]]
BOX_CASES=[[word,friends] for word,friends in [('dbca',2),('a',1),('abc',1),('abc',2),('abc',3),('aaaa',2),('zabc',2),('azby',3),('leetcode',4),('banana',2),('cabaa',4),('xyzxyz',3),('baca',2),('zzza',3)]]
DECREASING_CASES=[[[v for v in values]] for values in [[16,6,3],[1,2],[1,2,3],[1,3,2],[5,5,5],[1,5,2,4,3],[10,1,9,2,8],[3,1,4,1,5,9],[8,4,2,1],[1,10,2,9,3,8],[7,2,6,3,5,4],[1,4,7,10],[10,7,5,4,4],[2,9,1,8,3,7,4]]]
REMOVAL_CASES=[[[v for v in values]] for values in [[-3,2,-2,-1,3,-2,3],[1],[-1],[1,2,3],[-1,-2,-3],[1,-1,1],[2,-2,2,-2,2],[5,-10,5,-10,5],[0,0],[-5,4,-5,4,-5],[3,-1,-1,3],[1,-2,3,-2,4],[10,-3,-3,-3,10],[-1,5,-2,5,-1]]]
PRODUCT_CASES=[[[v for v in values]] for values in [[1,2,1,2,1,1,1],[1,1],[2,2],[2,3],[1,2,3],[2,3,6],[1,1,1,1],[2,4,8],[3,5,7],[1,2,4,2,1],[6,10,15],[2,3,2,3],[10,1,10,1],[4,6,2,3,1]]]


BATCH={
3405:entry('count_arrays_with_k_equal_neighbors',[('n','int'),('m','int'),('k','int')],'int',['combinatorics','math','modular arithmetic'],['1 <= n,m <= 100,000 and 0 <= k < n.','Array values lie in 1..m.','Count arrays having exactly k indices i where values[i] equals values[i+1], modulo 1,000,000,007.'],[([3,2,1],'Choose which one of two boundaries matches and choose the starting value, producing four arrays.'),([2,2,0],'The arrays [1,2] and [2,1] have no equal adjacent pair, so the answer is two.')],ARRAY_CASES,ARRAYS,[ARRAYS.replace('choose(n-1,k)','choose(n,k)'),ARRAYS.replace('n-k-1','n-k')],['Chooses matching positions from n slots instead of n-1 boundaries.','Requires one extra color-changing boundary.'],arrays_oracle,random_arrays,lesson('Choose the k matching boundaries; every other boundary must change value.','After choosing the first of m values, each nonmatching boundary has m-1 choices.','Multiply C(n-1,k), m, and (m-1)^(n-k-1) modulo the prime.','Boundary selections and value choices uniquely construct every valid array and never alter the exact match count.'),'O(min(k,n-k))','O(1)',8),
3406:entry('largest_string_from_box_large',[('word','str'),('num_friends','int')],'str',['strings','two pointers','greedy'],['word has 1–200,000 lowercase letters and 1 <= num_friends <= len(word).','Consider every split into num_friends nonempty consecutive parts.','Return the lexicographically largest part appearing across all splits.'],[(['dbca',2],'The part dbc can appear while leaving a for the other friend, and it is lexicographically largest.'),(['abc',1],'With one friend, the full word is the only part.')],BOX_CASES,BOX,[BOX.replace('return word[first:first+n-num_friends+1]','return word[first:]'),BOX.replace('+1]',' ]')],['Returns the greatest suffix without reserving characters for other friends.','Truncates the best suffix one character too early.'],box_oracle,random_box,lesson('The answer starts at the lexicographically greatest suffix but cannot exceed n-numFriends+1 characters.','Find the greatest suffix in linear time by eliminating losing starts with two pointers.','Compare candidate suffixes at their first mismatch, skip the losing matched block, then truncate the winner.','Every skipped start shares the compared prefix and loses at the mismatch, so it cannot be the maximal suffix.'),'O(n)','O(1)',8),
3409:entry('longest_decreasing_difference_subsequence',[('nums','list[int]')],'int',['arrays','dynamic programming','subsequences'],['nums has 2–10,000 values in 1..300.','Choose a subsequence whose absolute adjacent differences are non-increasing.','Return its maximum length.'],[([[16,6,3]],'The differences ten then three decrease, so all three values form a valid subsequence.'),([[1,2,4,8]],'Every attempted third selection increases the adjacent difference, so the maximum length is two.')],DECREASING_CASES,DECREASING,[DECREASING.replace('best[previous][difference]+1','best[previous][min(299,difference+1)]+1'),DECREASING.replace('for difference in range(maximum-1,-1,-1)','for difference in range(maximum)')],['Requires the next difference to be strictly smaller and loses equal-difference extensions.','Builds prefix rather than suffix maxima over allowed prior differences.'],decreasing_oracle,random_decreasing,lesson('A state needs the ending value and its most recent difference.','Because values are bounded by 300, query every prior value and a suffix maximum over allowable prior differences.','For each new value, batch pair extensions before updating its exact-difference row, then rebuild that row’s suffix maxima.','The suffix query enforces prior difference >= new difference, and batching preserves increasing index order.'),'O(n*300)','O(300²)',6),
3410:entry('maximum_subarray_after_value_removal',[('nums','list[int]')],'int',['arrays','segment trees','maximum subarray'],['nums has 1–100,000 integers with absolute value at most one million.','At most once, choose one value and remove every occurrence of that value; choosing no value is allowed.','Return the maximum nonempty subarray sum after the optional removal.'],[([[-3,2,-2,-1,3,-2,3]],'Removing every -2 joins the useful regions and produces maximum sum seven.'),([[1,-1,1]],'Removing -1 joins the two positive values for sum two.')],REMOVAL_CASES,REMOVAL,[REMOVAL.replace('for index in positions[value]:update(index,0)','for index in positions[value][:1]:update(index,0)',1).replace('for index in positions[value]:update(index,value)','for index in positions[value][:1]:update(index,value)'),REMOVAL.replace('        for index in positions[value]:update(index,value)\n','')],['Removes only the first occurrence of the chosen value.','Fails to restore trial deletions and illegally combines removals of several values.'],removal_oracle,random_removal,lesson('Only removing a negative value can increase a subarray sum, and deletion acts like a zero that connects its neighbors.','Maintain total, prefix, suffix, and best subarray values in a segment tree; temporarily zero all positions of each negative value.','Build once, update one value group to zero, read the root answer, then restore that group.','All updates across groups total O(n), while the segment tree exactly recomputes the best connected interval after each trial.'),'O(n log n)','O(n)',8),
3411:entry('maximum_equal_product_subarray',[('nums','list[int]')],'int',['arrays','math','enumeration'],['nums has 2–100 positive values in 1..10.','For a contiguous subarray, compare its product with its GCD multiplied by its LCM.','Return the longest length for which those quantities are equal.'],[([[1,2,1,2,1,1,1]],'A length-five subarray attains product equal to GCD times LCM.'),([[2,3]],'Product six equals gcd one times lcm six, so both elements qualify.')],PRODUCT_CASES,EQUAL_PRODUCTS,[EQUAL_PRODUCTS.replace('product==common*multiple','product==multiple'),EQUAL_PRODUCTS.replace('common=gcd(common,value)','common=value')],['Omits the GCD factor from the equality.','Uses only the latest value instead of the subarray GCD.'],equal_products_oracle,random_equal_products,lesson('The required quantities can be updated incrementally as a right endpoint grows.','Enumerate each left endpoint while maintaining product, GCD, and LCM.','Multiply the next value, update gcd/lcm, and record the length whenever product equals their product.','Every subarray appears once under its left and right endpoints, and the maintained aggregates are exact.'),'O(n²)','O(1)',3),
}
