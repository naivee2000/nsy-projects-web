"""Stack simulation, monotone windows, ordered-pair DP, counting, and strings."""
from itertools import combinations
from string import ascii_lowercase
from .import_batch_055 import entry


def merge_oracle(args):
    values=list(args[0]);index=0
    while index+1<len(values):
        if values[index]==values[index+1]:
            values[index:index+2]=[values[index]*2];index=max(0,index-1)
        else:index+=1
    return values
def random_merge(rng):return [[rng.randint(1,8) for _ in range(rng.randint(1,25))]]

def cost_oracle(args):
    nums,k=args;answer=0
    for left in range(len(nums)):
        low=high=nums[left]
        for right in range(left,len(nums)):
            low=min(low,nums[right]);high=max(high,nums[right])
            answer+=(high-low)*(right-left+1)<=k
    return answer
def random_cost(rng):return [[rng.randint(-20,20) for _ in range(rng.randint(1,18))],rng.randint(0,200)]

def pairs_oracle(args):
    a,b,k=args
    return max(sum(a[i]*b[j] for i,j in zip(left,right)) for left in combinations(range(len(a)),k) for right in combinations(range(len(b)),k))
def random_pairs(rng):
    n=rng.randint(1,7);m=rng.randint(1,7);k=rng.randint(1,min(n,m))
    return [[rng.randint(-9,9) for _ in range(n)],[rng.randint(-9,9) for _ in range(m)],k]

def delayed_oracle(args):
    nums,k=args
    return [sum(nums[j]==value for j in range(i+k+1,len(nums))) for i,value in enumerate(nums)]
def random_delayed(rng):
    n=rng.randint(1,25);return [[rng.randint(-5,5) for _ in range(n)],rng.randint(0,n+3)]

def words_oracle(args):
    words,weights=args
    output=''
    for word in words:
        total=0
        for character in word:total+=weights[ascii_lowercase.index(character)]
        output+=ascii_lowercase[25-total%26]
    return output
def random_words(rng):
    words=[''.join(rng.choice(ascii_lowercase) for _ in range(rng.randint(1,12))) for _ in range(rng.randint(1,12))]
    return [words,[rng.randint(0,30) for _ in range(26)]]


MERGE='''def merge_adjacent(nums):
    stack=[]
    for value in nums:
        stack.append(value)
        while len(stack)>1 and stack[-1]==stack[-2]:
            value=stack.pop();stack[-1]+=value
    return stack
'''

COST='''def count_bounded_cost_subarrays(nums,k):
    from collections import deque
    maximum=deque();minimum=deque();left=0;answer=0
    for right,value in enumerate(nums):
        while maximum and nums[maximum[-1]]<=value:maximum.pop()
        while minimum and nums[minimum[-1]]>=value:minimum.pop()
        maximum.append(right);minimum.append(right)
        while (nums[maximum[0]]-nums[minimum[0]])*(right-left+1)>k:
            if maximum[0]==left:maximum.popleft()
            if minimum[0]==left:minimum.popleft()
            left+=1
        answer+=right-left+1
    return answer
'''

PAIRS='''def maximum_ordered_pair_score(nums1,nums2,k):
    negative=-10**30;m=len(nums2)
    previous=[[negative]*(k+1) for _ in range(m+1)]
    for j in range(m+1):previous[j][0]=0
    for first in nums1:
        current=[row[:] for row in previous]
        for j,second in enumerate(nums2,1):
            for used in range(1,k+1):
                current[j][used]=max(current[j][used],current[j-1][used],previous[j-1][used-1]+first*second)
        previous=current
    return previous[m][k]
'''

DELAYED='''def delayed_equal_counts(nums,k):
    from collections import Counter
    counts=Counter();answer=[0]*len(nums)
    for i in range(len(nums)-k-2,-1,-1):
        counts[nums[i+k+1]]+=1
        answer[i]=counts[nums[i]]
    return answer
'''

WORDS='''def map_weighted_words(words,weights):
    answer=[]
    for word in words:
        total=sum(weights[ord(character)-97] for character in word)
        answer.append(chr(122-total%26))
    return ''.join(answer)
'''

def lesson(a,b,c,d):return [a,b,c,d]

MERGE_CASES=[[[*v]] for v in ([3,1,1,2],[1],[2,2],[1,1,2],[2,1,1],[4,4,8,8],[1,1,1],[1,1,2,2],[3,3,6,12],[1,2,2,1],[5,5,10,10,20],[2,2,4,1,1,2],[8,4,4,8],[1,1,2,4,4],[7,7,7,7])]
COST_CASES=[[a,k] for a,k in (([1,3,2],4),([5],0),([1,1],0),([1,2],1),([1,2],2),([3,1,4],6),([-2,2],8),([4,1,7,2],20),([2,5,2,5],9),([10,0,10],19),([1,2,3,4],12),([-3,-1,-2],4),([8,6,7,5,3],25),([0,100,0],200),([9,1,8,2],24))]
PAIR_CASES=[[a,b,k] for a,b,k in (([1,3,2],[4,5,1],2),([2],[3],1),([-2],[3],1),([-2],[-3],1),([1,2],[3,4],2),([5,1],[2,9],1),([3,-1,4],[2,5],2),([-3,-2],[-4,-1],2),([0,2,0],[7,1,8],2),([9,1,2],[1,8,3],2),([1,2,3],[4,5],1),([4,1],[2,3,5],2),([-5,6,-2],[3,-4,7],2),([2,2,2],[3,3,3],3),([7,-8,9],[-2,5,-6],1))]
DELAYED_CASES=[[a,k] for a,k in (([1,2,1,1],1),([1],0),([1,1],0),([1,1],1),([1,2,1],0),([1,2,1],1),([3,3,3,3],2),([1,2,3,1,2,3],2),([0,-1,0,-1],0),([5,4,5,4,5],3),([2,1,2,1,2],1),([9,8,7],5),([1,2,3,4],0),([4,4,3,4,3,4],2),([6,7,6,8,6,7],4))]
W=[i for i in range(1,27)];Z=[0]*26;R=list(reversed(W));SAMPLE_W=[5,3,12,14,1,2,3,2,10,6,6,9,7,8,7,10,8,9,6,9,9,8,3,7,7,2]
WORD_CASES=[[words,weights] for words,weights in ((['a'],W),(['z'],W),(['abc'],W),(['a','b'],Z),(['leetcode','code'],W),(['xyz'],R),(['aa','zz'],W),(['az','za'],R),(['m','no','pqr'],W),(['hello'],[1]*26),(['abc','def','ghi'],[2]*26),(['qwerty','asdf'],R),(['zoo','yak'],[3]*26),(['binary','tree'],W),(['stack','queue','heap'],R))]

BATCH={
3834:entry('merge_adjacent',[('nums','list[int]')],'list[int]',['arrays','stacks','simulation'],['nums contains between 1 and 100,000 positive integers.','Scan from left to right; merging a pair can immediately create another equal pair with its new left neighbor.','Return the stable sequence after all such cascading merges.'],[([[3,1,1,2]],'The two ones form two; that two merges with the following two, leaving [3,4].'),([[1,1,2]],'The ones become two, then the two twos become four, so the answer is [4].')],MERGE_CASES,MERGE,[MERGE.replace('while len(stack)>1','if len(stack)>1'),MERGE.replace('stack[-1]+=value','stack.append(value*2)')],['Performs at most one merge for each input value and misses cascades.','Appends a merged value without removing the surviving left member.'],merge_oracle,random_merge,lesson('The unresolved suffix is the only place where a new equality can appear.','Use a stack and repeatedly combine its last two values while they match.','Push each input value, then cascade merges before reading the next value.','Everything below the stack top was already stable; each merge reduces length, so the final stack is exactly the prescribed left-to-right process.'),'O(n)','O(n)',5),
3835:entry('count_bounded_cost_subarrays',[('nums','list[int]'),('k','int')],'int',['arrays','sliding window','monotonic queues'],['nums has up to 100,000 integers and k is nonnegative.','A subarray of length L costs (maximum-minimum)×L.','Count all nonempty contiguous subarrays whose cost is at most k.'],[([[1,3,2],4],'All subarrays except [1,3,2] qualify, so the count is five.'),([[1,1],0],'Both singletons and the equal pair have zero cost, giving three.')],COST_CASES,COST,[COST.replace('*(right-left+1)>k','*(right-left)>k'),COST.replace('answer+=right-left+1','answer+=1')],['Uses one less than the true subarray length in the cost.','Counts only one qualifying window per right endpoint instead of all qualifying suffixes.'],cost_oracle,random_cost,lesson('For a fixed right endpoint, removing values from the left cannot increase range or length.','Maintain window maximum and minimum with decreasing and increasing index deques.','Shrink until the cost qualifies, then add every suffix starting from left through right.','Monotonicity makes exactly right-left+1 suffixes valid, and each index enters and leaves each deque once.'),'O(n)','O(n)',6),
3836:entry('maximum_ordered_pair_score',[('nums1','list[int]'),('nums2','list[int]'),('k','int')],'int',['arrays','dynamic programming'],['Both arrays are nonempty, contain signed integers, and k does not exceed either length.','Choose increasing indices i1<…<ik and j1<…<jk.','Maximize the sum of nums1[it]×nums2[jt] over the k position-preserving pairs.'],[([[1,3,2],[4,5,1],2],'Choosing values [3,2] and [4,5] scores 3×4+2×5=22.'),([[-2],[3],1],'The only required pair scores -6; choosing no pair is not allowed.')],PAIR_CASES,PAIRS,[PAIRS.replace('negative=-10**30','negative=0'),PAIRS.replace('previous[j-1][used-1]+first*second','previous[j][used-1]+first*second')],['Initializes impossible states to zero, incorrectly allowing fewer than k pairs when scores are negative.','Reuses the current second-array prefix when pairing, which can reuse an index or violate order.'],pairs_oracle,random_pairs,lesson('The final choice either skips an element or pairs the current elements after an optimal smaller-prefix solution.','Track the best score by second-array prefix and number of completed pairs while sweeping the first array.','Copy skip states, propagate skips in nums2, and extend only the previous first-array row at j-1.','Those three transitions cover every ordered matching, while using the previous row prevents reusing a nums1 element.'),'O(nmk)','O(mk)',8),
3837:entry('delayed_equal_counts',[('nums','list[int]'),('k','int')],'list[int]',['arrays','hash maps','counting'],['nums has up to 100,000 integers and k is nonnegative.','For every i, count equal values at indices j satisfying j>i+k.','Return one count for every input index.'],[([[1,2,1,1],1],'Index zero matches the ones at indices two and three; no later index has an eligible equal value.'),([[1,2,1],0],'Index zero sees the equal one at index two, producing [1,0,0].')],DELAYED_CASES,DELAYED,[DELAYED.replace('i+k+1','i+k'),DELAYED.replace('range(len(nums)-k-2,-1,-1)','range(len(nums)-k-3,-1,-1)')],['Includes distance exactly k instead of requiring the later index to be more than k away.','Starts one position too early and leaves a valid leading answer uncomputed.'],delayed_oracle,random_delayed,lesson('Scanning right to left lets a frequency map represent exactly the eligible suffix.','Before answering i, insert the value at i+k+1 when that index exists.','Read the frequency of nums[i], then move one position left.','The map invariant contains precisely indices greater than i+k, so each reported frequency is exact.'),'O(n)','O(n)',5),
3838:entry('map_weighted_words',[('words','list[str]'),('weights','list[int]')],'str',['arrays','strings','simulation'],['words contains nonempty lowercase English strings and weights has exactly 26 integers.','Sum the supplied weight of every character in each word.','Map remainder r to the reverse-alphabet letter at index 25-r and concatenate the results.'],[([['abcd','def','xyz'],SAMPLE_W],'The totals 34, 17, and 16 map from reverse-alphabet remainders to r, i, and j.'),([['a'],W],'Weight one has remainder one, which maps to reverse index one: y.'),([['a','b'],Z],'Both totals are zero, and reverse index zero is z, so the result is zz.')],WORD_CASES,WORDS,[WORDS.replace('122-total%26','97+total%26'),WORDS.replace('for word in words:','for word in words[:-1]:')],['Maps remainders in normal alphabetical order instead of reverse order.','Silently omits the final word.'],words_oracle,random_words,lesson('Each word is independent: only its total weight modulo 26 matters.','Use character codes to index the 26 weights, then reflect the remainder across the alphabet.','Accumulate one mapped character per word in the original order.','The sum matches the definition, modulo preserves the requested class, and code point 122-r is exactly the reverse-alphabet mapping.'),'O(total characters)','O(number of words)',3),
}
