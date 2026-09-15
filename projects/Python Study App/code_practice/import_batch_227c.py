"""Array compression, product residues, dynamic product queries, implicit-treap XOR, and survey counts."""
from functools import lru_cache

from .import_batch_055 import entry


def nondesc_oracle(args):
    nums=args[0];n=len(nums);best=0
    for cuts in range(1<<(n-1)):
        values=[];start=0
        for i in range(n-1):
            if cuts>>i&1:values.append(max(nums[start:i+1]));start=i+1
        values.append(max(nums[start:]))
        if all(values[i]<=values[i+1] for i in range(len(values)-1)):best=max(best,len(values))
    return best


def random_nondesc(rng):return [[rng.randint(1,15) for _ in range(rng.randint(1,11))]]


def x_values_oracle(args):
    nums,k=args;answer=[0]*k
    for left in range(len(nums)):
        product=1
        for right in range(left,len(nums)):
            product=product*nums[right]%k;answer[product]+=1
    return answer


def random_x_values(rng):return [[rng.randint(1,20) for _ in range(rng.randint(1,12))],rng.randint(1,5)]


def dynamic_x_oracle(args):
    nums,k,queries=args;nums=list(nums);answer=[]
    for index,value,start,target in queries:
        nums[index]=value;product=1;count=0
        for end in range(start,len(nums)):
            product=product*nums[end]%k;count+=product==target
        answer.append(count)
    return answer


def random_dynamic_x(rng):
    n=rng.randint(1,10);nums=[rng.randint(1,15) for _ in range(n)];k=rng.randint(1,5);queries=[]
    for _ in range(rng.randint(1,15)):queries.append([rng.randrange(n),rng.randint(1,15),rng.randrange(n),rng.randrange(k)])
    return [nums,k,queries]


def xor_query_oracle(args):
    nums,queries=args;nums=list(nums);answer=[]
    for kind,left,right in queries:
        if kind==1:nums[left]=right
        elif kind==2:
            value=0
            for item in nums[left:right+1]:value^=item
            answer.append(value)
        else:nums[left:right+1]=nums[left:right+1][::-1]
    return answer


def random_xor_queries(rng):
    n=rng.randint(1,12);nums=[rng.randint(0,31) for _ in range(n)];queries=[]
    for _ in range(rng.randint(1,18)):
        kind=rng.randint(1,3)
        if kind==1:queries.append([1,rng.randrange(n),rng.randint(0,31)])
        else:
            left=rng.randrange(n);queries.append([kind,left,rng.randint(left,n-1)])
    return [nums,queries]


def response_oracle(args):
    responses=args[0];words=sorted({word for day in responses for word in day})
    return min(words,key=lambda word:(-sum(word in day for day in map(set,responses)),word))


def random_response(rng):
    words=['a','b','c','yes','no','maybe'];return [[rng.choice(words) for _ in range(rng.randint(1,7))] for _ in range(rng.randint(1,7))]


NONDESC='''def maximum_nondecreasing_size(nums):
    answer=0;maximum=0
    for value in nums:
        if value>=maximum:answer+=1;maximum=value
    return answer
'''


X_VALUES='''def count_subarray_product_remainders(nums,k):
    answer=[0]*k;ending=[0]*k
    for value in nums:
        current=[0]*k;current[value%k]+=1
        for remainder,count in enumerate(ending):current[remainder*value%k]+=count
        for remainder,count in enumerate(current):answer[remainder]+=count
        ending=current
    return answer
'''


DYNAMIC_X='''def dynamic_suffix_product_counts(nums,k,queries):
    n=len(nums);size=1
    while size<n:size*=2
    tree=[(1%k,[0]*k) for _ in range(2*size)]
    def leaf(value):
        counts=[0]*k;counts[value%k]=1;return value%k,counts
    def merge(first,second):
        product=first[0]*second[0]%k;counts=first[1][:]
        for remainder,count in enumerate(second[1]):counts[first[0]*remainder%k]+=count
        return product,counts
    for index,value in enumerate(nums):tree[size+index]=leaf(value)
    for index in range(size-1,0,-1):tree[index]=merge(tree[index*2],tree[index*2+1])
    answer=[]
    for position,value,start,target in queries:
        index=size+position;tree[index]=leaf(value);index//=2
        while index:tree[index]=merge(tree[index*2],tree[index*2+1]);index//=2
        left=size+start;right=size+n;before=(1%k,[0]*k);after=(1%k,[0]*k)
        while left<right:
            if left&1:before=merge(before,tree[left]);left+=1
            if right&1:right-=1;after=merge(tree[right],after)
            left//=2;right//=2
        answer.append(merge(before,after)[1][target])
    return answer
'''


XOR_QUERIES='''def range_xor_with_reversals(nums,queries):
    seed=2463534242
    class Node:
        __slots__=('value','priority','left','right','size','xor','reverse')
        def __init__(self,value,priority):self.value=value;self.priority=priority;self.left=None;self.right=None;self.size=1;self.xor=value;self.reverse=False
    def node_size(node):return node.size if node else 0
    def node_xor(node):return node.xor if node else 0
    def apply(node):
        if node:node.reverse^=True;node.left,node.right=node.right,node.left
    def push(node):
        if node and node.reverse:apply(node.left);apply(node.right);node.reverse=False
    def pull(node):node.size=1+node_size(node.left)+node_size(node.right);node.xor=node_xor(node.left)^node.value^node_xor(node.right)
    def split(node,count):
        if not node:return None,None
        push(node)
        if node_size(node.left)>=count:
            first,node.left=split(node.left,count);pull(node);return first,node
        node.right,second=split(node.right,count-node_size(node.left)-1);pull(node);return node,second
    def merge(first,second):
        if not first or not second:return first or second
        if first.priority<second.priority:push(first);first.right=merge(first.right,second);pull(first);return first
        push(second);second.left=merge(first,second.left);pull(second);return second
    root=None
    for value in nums:
        seed=(seed*1664525+1013904223)&0xffffffff;root=merge(root,Node(value,seed))
    answer=[]
    for kind,left,right in queries:
        if kind==1:
            first,tail=split(root,left);middle,last=split(tail,1);middle.value=right;pull(middle);root=merge(first,merge(middle,last))
        else:
            first,tail=split(root,left);middle,last=split(tail,right-left+1)
            if kind==2:answer.append(node_xor(middle))
            else:apply(middle)
            root=merge(first,merge(middle,last))
    return answer
'''


RESPONSES='''def most_common_daily_response(responses):
    from collections import Counter
    counts=Counter()
    for day in responses:counts.update(set(day))
    return min(counts,key=lambda word:(-counts[word],word))
'''


def lesson(a,b,c,d):return [a,b,c,d]


NONDESC_CASES=[[[*values]] for values in [[4,2,5,3,5],[1,2,3],[3,2,1],[1],[2,2,2],[5,1,5],[1,3,2,4],[9,1,2,3],[2,1,2,1,2],[1,5,4,3,6],[7,3,8,2,9,1],[4,4,3,5,5],[10,2,8,6,12],[3,1,4,1,5,9]]]
X_CASES=[[nums,k] for nums,k in [([1,2,3,4,5],3),([1,2,4,8,16,32],4),([1,1,2,1,1],2),([5],1),([5],3),([2,2],4),([3,6,9],3),([1,2,3],5),([7,7,7,7],5),([2,3,5,7],2),([10,20,30],4),([1,1,1,1],3),([4,5,6,7,8],5),([9,2,6,5,3,5],4)]]
DYNAMIC_CASES=[list(case) for case in [
([1,2,3,4,5],3,[[2,2,0,2],[3,3,3,0],[0,1,0,1]]),([1,2,4,8,16,32],4,[[0,2,0,2],[0,2,0,1]]),
([1,1,2,1,1],2,[[2,1,0,1]]),([5],3,[[0,4,0,1],[0,6,0,0]]),([2,3],5,[[1,4,0,3],[0,5,1,4]]),
([1,2,3],1,[[1,9,0,0]]),([4,4,4],5,[[0,1,0,1],[2,2,1,3]]),([2,5,7,3],3,[[1,2,2,2],[3,6,0,0]]),
([9,8,7,6,5],4,[[4,1,4,1],[0,2,1,0]]),([1,1,1,1],2,[[2,2,0,0],[2,1,1,1]]),
([6,10,15],5,[[1,1,0,1]]),([3,2,1,2,3],4,[[2,7,2,3],[4,8,0,0]]),([11,12],3,[[0,3,0,0],[1,5,0,0]]),
([2,4,8,16],5,[[3,3,1,4],[1,6,0,2]])]]
XOR_CASES=[[nums,queries] for nums,queries in [
([1,2,3,4,5],[[2,1,3],[1,2,10],[3,0,4],[2,0,4]]),([7,8,9],[[1,0,3],[2,0,2],[3,1,2]]),
([1],[[2,0,0],[3,0,0],[1,0,7],[2,0,0]]),([1,2],[[3,0,1],[2,0,0],[2,1,1]]),([0,0,0],[[2,0,2]]),
([5,6,7,8],[[3,1,3],[2,0,2]]),([1,1,2,2],[[2,0,3],[3,0,3],[2,1,2]]),([9,3,12],[[1,1,5],[2,0,2]]),
([4,8,15,16,23,42],[[3,1,4],[1,3,7],[2,2,5]]),([31,0,31],[[2,0,2],[3,0,1],[2,0,1]]),
([2,4,6,8,10],[[3,0,4],[3,1,3],[2,0,4]]),([7,7,7,7],[[1,2,0],[2,1,3]]),
([1,2,4,8],[[2,0,1],[3,0,2],[2,0,1]]),([10,20,30,40,50],[[3,2,4],[1,0,99],[2,0,3]])]]
RESPONSE_CASES=[[days] for days in [
[['good','ok','good','ok'],['ok','bad','good','ok','ok'],['good'],['bad']],
[['good','ok','good'],['ok','bad'],['bad','notsure'],['great','good']],[['a']],[['b','a']],[['x','x','x'],['y']],
[['yes','no'],['yes','maybe'],['no','maybe']],[['z'],['a']],[['cat','dog','cat'],['dog'],['cat']],
[['aa','ab'],['ab','aa']],[['one','two','three'],['two','two'],['three']],
[['same','same'],['same']],[['red','blue'],['green','blue'],['green']],
[['k','j','k'],['j','k'],['j']],[['long','short'],['short'],['long'],['short']]]]


BATCH={
3523:entry('maximum_nondecreasing_size',[('nums','list[int]')],'int',['arrays','greedy','monotonic stacks'],['nums has up to 200,000 positive integers.','An operation replaces any nonempty contiguous subarray by its maximum value.','After any operations, maximize the length of a non-decreasing resulting array.'],[([[4,2,5,3,5]],'Keeping four and compressing through each later five yields a non-decreasing array of length three.'),([[1,2,3]],'The array is already non-decreasing, so all three positions remain.')],NONDESC_CASES,NONDESC,[NONDESC.replace('value>=maximum','value>maximum'),NONDESC.replace('maximum=value','maximum=max(maximum,value+1)')],['Rejects equal values even though non-decreasing arrays allow them.','Raises the retained maximum beyond each value and incorrectly blocks valid future blocks.'],nondesc_oracle,random_nondesc,lesson('A retained block contributes its maximum, and the next block must end at a value at least that maximum.','Scan left to right, retaining exactly the values that meet the largest maximum forced so far.','Increment the answer when value >= current maximum, then set the current maximum to that value.','Any skipped values can be absorbed into the next retained block; taking the earliest feasible endpoint leaves maximal room for later blocks.'),'O(n)','O(1)',5),
3524:entry('count_subarray_product_remainders',[('nums','list[int]'),('k','int')],'list[int]',['arrays','dynamic programming','modular arithmetic'],['nums has up to 100,000 positive integers and 1 <= k <= 5.','Removing a prefix and suffix while leaving a nonempty array is equivalent to choosing a nonempty contiguous subarray.','For every remainder 0 through k-1, return how many subarray products have that remainder modulo k.'],[([[1,2,3,4,5],3],'All fifteen subarrays contribute; nine products are remainder zero, two remainder one, and four remainder two.'),([[1,2,4,8,16,32],4],'Eighteen of the twenty-one subarrays have product divisible by four.')],X_CASES,X_VALUES,[X_VALUES.replace('current[value%k]+=1','current[1%k]+=1'),X_VALUES.replace('remainder*value%k','(remainder+value)%k')],['Starts every one-element subarray with remainder one instead of its value.','Tracks subarray sums modulo k rather than products.'],x_values_oracle,random_x_values,lesson('Every retained array is a contiguous subarray, so count product remainders for all subarrays.','Maintain counts by remainder for subarrays ending at the previous position, then extend them by the new value.','Start the one-value subarray, multiply every prior ending remainder, add current counts to the global result, and advance.','Each subarray is created exactly once at its right endpoint, and modular multiplication preserves precisely the needed state.'),'O(nk)','O(k)',6),
3525:entry('dynamic_suffix_product_counts',[('nums','list[int]'),('k','int'),('queries','list[list[int]]')],'list[int]',['arrays','segment trees','modular arithmetic'],['nums has up to 100,000 positive integers, k <= 5, and updates persist across up to 20,000 queries.','Each [index,value,start,x] first updates nums[index], then fixes removal of indices before start.','Count nonempty prefixes of nums[start:] whose product is congruent to x; return one count per query.'],[([[1,2,3,4,5],3,[[2,2,0,2],[3,3,3,0],[0,1,0,1]]],'After each persistent update, the requested suffix start has exactly two qualifying prefix products.'),([[1,2,4,8,16,32],4,[[0,2,0,2],[0,2,0,1]]],'After changing the first value to two, one prefix has remainder two and none has remainder one.')],DYNAMIC_CASES,DYNAMIC_X,[DYNAMIC_X.replace('counts[first[0]*remainder%k]+=count','counts[remainder]+=count'),DYNAMIC_X.replace('left=size+start','left=size')],['Merges right-prefix counts without multiplying by the full left segment product.','Ignores the required start index and always queries from the beginning.'],dynamic_x_oracle,random_dynamic_x,lesson('A segment is summarized by its total product and counts of each nonempty prefix-product remainder.','Use an order-preserving segment tree; merging appends right prefixes after the entire left segment.','Point-update the changed value, query the ordered range [start,n), and return its prefix-count entry for x.','The merge summary is associative and contains exactly the data required for any larger segment, so updates and suffix queries stay logarithmic.'),'O((n+q) k log n)','O(nk)',8),
3526:entry('range_xor_with_reversals',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['arrays','implicit treaps','lazy propagation'],['nums and queries each have up to 100,000 entries.','[1,index,value] updates one position; [2,left,right] reports inclusive range XOR; [3,left,right] reverses that range.','Updates and reversals persist, and XOR answers must follow query order.'],[([[1,2,3,4,5],[[2,1,3],[1,2,10],[3,0,4],[2,0,4]]],'The first range XOR is five; after the update and reversal, the whole-array XOR is eight.'),([[7,8,9],[[1,0,3],[2,0,2],[3,1,2]]],'Updating the first value makes the full XOR two; the later reversal produces no additional answer.')],XOR_CASES,XOR_QUERIES,[XOR_QUERIES.replace("if kind==2:answer.append(node_xor(middle))","if kind==2:answer.append(node_xor(root))"),XOR_QUERIES.replace('else:apply(middle)','else:pass')],['Returns the whole-array XOR instead of the selected interval.','Ignores reversal operations, so later positional updates and queries use the wrong order.'],xor_query_oracle,random_xor_queries,lesson('Range reversal changes order but not subtree membership or XOR, making an implicit balanced tree with a lazy reverse flag natural.','Store sequence position by subtree size, range XOR as an aggregate, and reversal as a child-swap flag.','Split around each range, read or toggle its middle tree, then merge the three pieces; isolate one node for updates.','Split/merge preserve sequence order, aggregates are refreshed locally, and lazy swaps exactly represent every pending reversal.'),'O((n+q) log n) expected','O(n)',8),
3527:entry('most_common_daily_response',[('responses','list[list[str]]')],'str',['arrays','hash maps','counting'],['responses contains at least one nonempty daily list of lowercase words.','A word counts at most once per day even if repeated within that day.','Return the word occurring on the most days, breaking ties lexicographically smallest.'],[([[['good','ok','good','ok'],['ok','bad','good','ok','ok'],['good'],['bad']]],'After per-day deduplication, good appears on three days and wins.'),([[['good','ok','good'],['ok','bad'],['bad','notsure'],['great','good']]],'Bad, good, and ok each occur on two days, so bad wins the lexical tie.')],RESPONSE_CASES,RESPONSES,[RESPONSES.replace('counts.update(set(day))','counts.update(day)'),RESPONSES.replace('(-counts[word],word)','(-counts[word],word[::-1])')],['Counts repeated answers multiple times within one day.','Breaks frequency ties using reversed spellings rather than normal lexicographic order.'],response_oracle,random_response,lesson('The frequency unit is days, not raw response occurrences, so each daily list must be deduplicated first.','Update a global counter from the set of responses for each day.','Count every word once per daily set, then minimize the key (-frequency, word).','The negative count chooses maximum frequency and the word component implements the required smallest lexical tie-break.'),'O(total responses)','O(distinct responses)',5),
}
