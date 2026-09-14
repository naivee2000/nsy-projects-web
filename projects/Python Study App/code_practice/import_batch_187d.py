"""Easy subsequence, constrained-index, mountain, subarray, and bit-threshold problems for batch 187."""
from .import_batch_055 import entry as _entry

def entry(*args,**kwargs):
    """Accept source examples carrying a documented expected value; the builder recomputes it."""
    values=list(args)
    values[5]=[(item[0],item[-1]) for item in values[5]]
    return _entry(*values,**kwargs)

def groups_oracle(a):
    words,groups=a;best=[]
    for mask in range(1<<len(words)):
        chosen=[i for i in range(len(words)) if mask>>i&1]
        if all(groups[x]!=groups[y] for x,y in zip(chosen,chosen[1:])) and len(chosen)>len(best):best=chosen
    return [words[i] for i in best]
def random_groups(r):
    n=r.randint(1,10);return [[f'w{i}' for i in range(n)],[r.randint(0,1) for _ in range(n)]]
def indices_oracle(a):
    nums,index_difference,value_difference=a
    for i in range(len(nums)):
        for j in range(len(nums)):
            if abs(i-j)>=index_difference and abs(nums[i]-nums[j])>=value_difference:return [i,j]
    return [-1,-1]
def random_indices(r):
    n=r.randint(1,25);return [[r.randint(-30,30) for _ in range(n)],r.randint(0,n),r.randint(0,60)]
def mountain_oracle(a):
    nums=a[0];answers=[nums[i]+nums[j]+nums[k] for i in range(len(nums)) for j in range(i+1,len(nums)) for k in range(j+1,len(nums)) if nums[i]<nums[j] and nums[k]<nums[j]]
    return min(answers,default=-1)
def random_mountain(r):return [[r.randint(1,100) for _ in range(r.randint(3,20))]]
def distinct_square_oracle(a):
    nums=a[0];answer=0
    for left in range(len(nums)):
        seen=set()
        for right in range(left,len(nums)):
            seen.add(nums[right]);answer+=len(seen)**2
    return answer
def random_distinct_square(r):return [[r.randint(1,8) for _ in range(r.randint(1,20))]]
def kor_oracle(a):
    nums,k=a;answer=0
    for bit in range(31):
        if sum(value>>bit&1 for value in nums)>=k:answer|=1<<bit
    return answer
def random_kor(r):
    nums=[r.randint(0,2**20-1) for _ in range(r.randint(1,50))];return [nums,r.randint(1,len(nums))]

GROUPS='''\
def longest_alternating_group_words(words,groups):
    answer=[words[0]];last=groups[0]
    for word,group in zip(words[1:],groups[1:]):
        if group!=last:answer.append(word);last=group
    return answer
'''
INDICES='''\
def find_far_different_indices(nums,indexDifference,valueDifference):
    for i in range(len(nums)):
        for j in range(len(nums)):
            if abs(i-j)>=indexDifference and abs(nums[i]-nums[j])>=valueDifference:return [i,j]
    return [-1,-1]
'''
MOUNTAIN='''\
def minimum_mountain_triplet_sum(nums):
    n=len(nums);left=[float('inf')]*n;small=float('inf')
    for i,value in enumerate(nums):left[i]=small;small=min(small,value)
    right=float('inf');answer=float('inf')
    for j in range(n-1,-1,-1):
        if left[j]<nums[j] and right<nums[j]:answer=min(answer,left[j]+nums[j]+right)
        right=min(right,nums[j])
    return -1 if answer==float('inf') else answer
'''
DISTINCT_SQUARE='''\
def sum_squared_distinct_subarrays(nums):
    answer=0
    for left in range(len(nums)):
        seen=set()
        for right in range(left,len(nums)):
            seen.add(nums[right]);answer+=len(seen)*len(seen)
    return answer
'''
KOR='''\
def array_k_or(nums,k):
    answer=0
    for bit in range(31):
        if sum((value>>bit)&1 for value in nums)>=k:answer|=1<<bit
    return answer
'''

BATCH={
2900:entry('longest_alternating_group_words',[('words','list[str]'),('groups','list[int]')],'list[str]',['arrays','greedy','subsequences'],['words and groups have the same length, and each group is zero or one.','Choose a longest subsequence whose adjacent chosen entries have different groups.','Return the chosen words in original order; any longest answer is allowed, and this function returns the earliest greedy answer.'],[([['e','a','b'],[0,0,1]],['e','b'],'Taking e then b changes group from zero to one.'),([['a','b','c','d'],[1,0,1,1]],['a','b','c'],'The first three words alternate groups; the final group repeats one.')],[[w,g] for w,g in [(['a'],[0]),(['a','b'],[0,0]),(['a','b'],[0,1]),(['a','b','c'],[0,1,0]),(['a','b','c'],[1,1,1]),(['a','b','c'],[1,0,0]),(['a','b','c','d'],[0,0,1,1]),(['a','b','c','d'],[0,1,1,0]),(['w0','w1','w2','w3','w4'],[1,0,1,0,1]),(['x','y','z'],[0,0,1]),(['one','two','three','four'],[1,1,0,1]),(['p','q','r','s'],[0,1,0,0]),(['aa','bb','cc'],[1,0,1]),(['u','v','w','x','y'],[0,0,0,1,0])]],GROUPS,[GROUPS.replace('group!=last','group==last'),GROUPS.replace('last=group','last=groups[0]')],['Selects repeated groups instead of transitions.','Never updates the last chosen group, missing later valid transitions.'],groups_oracle,random_groups,['Within a run of equal group values, at most one word can be chosen.','Choose the first word of every maximal equal-group run.','Append exactly when the group differs from the last chosen group.','This takes one word per run, which is feasible and also matches the upper bound, so it is longest.'],'O(n)','O(n)',3),
2903:entry('find_far_different_indices',[('nums','list[int]'),('indexDifference','int'),('valueDifference','int')],'list[int]',['arrays','enumeration'],['Find indices i and j whose absolute index difference is at least indexDifference.','Their values must differ by at least valueDifference in absolute value.','Return the first pair in row-major i,j order, or [-1,-1] when no pair exists.'],[([[5,1,4,1],2,4],[0,3],'Indices zero and three are far enough and their values differ by four.'),([[1,2,3],2,4],[-1,-1],'The only sufficiently separated endpoints differ by only two.')],[[nums,d,v] for nums,d,v in [([1],0,0),([1],1,0),([1,2],1,1),([1,2],1,2),([5,1,4,1],2,4),([1,2,3],2,2),([1,2,3],2,3),([10,1,10],1,9),([0,0,0],0,0),([3,-3],1,6),([3,-3],0,7),([1,10,2,9],3,8),([8,1,7,2],2,6),([4,4,9,4],2,5)]],INDICES,[INDICES.replace('>=indexDifference','>indexDifference'),INDICES.replace('>=valueDifference','>valueDifference')],['Requires the index distance to be strictly greater instead of at least.','Requires the value difference to be strictly greater instead of at least.'],indices_oracle,random_indices,['The constraints are independent inequalities on a pair of indices.','Enumerate candidate i and j in the documented return order.','Return immediately when both absolute differences meet their inclusive thresholds.','Exhaustive enumeration guarantees the first qualifying pair is returned and proves impossibility if none qualifies.'],'O(n^2)','O(1)',3),
2908:entry('minimum_mountain_triplet_sum',[('nums','list[int]')],'int',['arrays','prefix minima','suffix minima'],['Choose indices i<j<k such that nums[i] and nums[k] are both strictly smaller than nums[j].','Minimize nums[i]+nums[j]+nums[k].','Return -1 when no mountain triplet exists.'],[([[8,6,1,5,3]],9,'Indices two, three, and four form 1<5>3 with sum nine.'),([[5,4,8,7,10,2]],13,'Values 4,7,2 form the minimum valid mountain sum thirteen.')],[[x] for x in [[1,2,3],[3,2,1],[1,3,2],[2,3,1],[1,1,1],[1,2,1],[8,6,1,5,3],[5,4,8,7,10,2],[10,1,10],[4,2,5,1],[2,9,3,8,1],[7,6,5,8,4],[1,5,4,3,2],[9,1,2,3,0]]],MOUNTAIN,[MOUNTAIN.replace('left[j]<nums[j]','left[j]<=nums[j]'),MOUNTAIN.replace('right<nums[j]','right>nums[j]')],['Allows an equal left endpoint despite the strict mountain inequality.','Requires the right endpoint to be larger than the peak.'],mountain_oracle,random_mountain,['For each possible middle index, only the smallest value on each side can minimize its triplet.','Build the exclusive prefix minimum for every position.','Scan from right to left while maintaining the exclusive suffix minimum, testing both strict inequalities.','Any valid triplet using a middle j is no better than the two side minima, so minimizing these candidates is globally optimal.'],'O(n)','O(n)',3),
2913:entry('sum_squared_distinct_subarrays',[('nums','list[int]')],'int',['arrays','sets','enumeration'],['For every nonempty contiguous subarray, count its distinct values.','Square that distinct count and add it to the answer.','Return the total over all subarrays.'],[([[1,2,1]],15,'The six subarrays have distinct counts 1,2,2,1,2,1; their squares sum to fifteen.'),([[1,1]],3,'The two length-one subarrays and the full subarray each contribute one.')],[[x] for x in [[1],[1,1],[1,2],[1,2,1],[1,2,3],[3,2,1],[1,1,1],[1,2,2],[2,1,2,1],[1,2,3,4],[4,4,3,3],[1,3,1,3,2],[5,4,3,2,1],[1,2,1,2,1,2]]],DISTINCT_SQUARE,[DISTINCT_SQUARE.replace('len(seen)*len(seen)','len(seen)'),DISTINCT_SQUARE.replace('seen.add(nums[right])','seen={nums[right]}')],['Adds distinct counts without squaring them.','Forgets values seen earlier in the current subarray.'],distinct_square_oracle,random_distinct_square,['Fix each possible left endpoint.','Extend the right endpoint one position at a time while maintaining a set of encountered values.','After each extension, add the square of the set size.','Every nonempty subarray has one unique left/right pair and is therefore evaluated exactly once with its exact distinct set.'],'O(n^2)','O(n)',3),
2917:entry('array_k_or',[('nums','list[int]'),('k','int')],'int',['arrays','bit manipulation','counting'],['For each nonnegative bit position, count how many array values contain that bit.','Set the bit in the answer when its count is at least k.','Return the integer represented by all qualifying bits.'],[([[7,12,9,8,9,15],4],9,'Bits zero and three appear in at least four values, producing binary 1001.'),([[2,12,1,11,4,5],6],0,'No bit occurs in all six values.')],[[nums,k] for nums,k in [([0],1),([1],1),([1,2],1),([1,2],2),([3,3],2),([7,12,9,8,9,15],4),([2,12,1,11,4,5],6),([0,0,0],1),([5,5,1],2),([8,4,2,1],1),([8,4,2,1],2),([15,0,15],2),([1023,512,256],2),([1,3,7,15],3)]],KOR,[KOR.replace('>=k','>k'),KOR.replace('answer|=1<<bit','answer+=bit')],['Requires more than k occurrences instead of at least k.','Adds the bit index rather than setting its positional value.'],kor_oracle,random_kor,['Bits contribute independently to the result.','Count the one bits at each position across all values.','Set position b by OR-ing 1<<b exactly when its count reaches k.','The definition makes no cross-bit interaction, so evaluating every supported position separately constructs precisely the k-or.'],'O(31n)','O(1)',3),
}
BATCH[2900]['wrong'][1]='''def longest_alternating_group_words(words,groups):
    answer=[words[0]];last=groups[0]
    for word,group in zip(words[1:],groups[1:]):
        if group!=last:answer.append(word)
    return answer
'''
BATCH[2908]['boundaries'].append([[1,1,0]])
