"""XOR bases, common indices, capped subset sums, stable parity, and block moves."""
from collections import deque
from itertools import combinations
from .import_batch_055 import entry


def xor_oracle(args):
    nums=args[0];values={0}
    for value in nums:values|={current^value for current in list(values)}
    return max(values)

def random_xor(rng):return [[rng.randint(0,255) for _ in range(rng.randint(2,15))]]

def index_oracle(args):
    first,second=args;answer=None
    for i,a in enumerate(first):
        for j,b in enumerate(second):
            if a==b:answer=i+j if answer is None else min(answer,i+j)
    return -1 if answer is None else answer

def random_index(rng):
    n=rng.randint(1,15);return [[rng.randint(-8,8) for _ in range(n)],[rng.randint(-8,8) for _ in range(n)]]

def capped_oracle(args):
    nums,k=args;answer=[]
    for cap in range(1,len(nums)+1):
        possible={0}
        for value in nums:possible|={total+min(value,cap) for total in list(possible) if total+min(value,cap)<=k}
        answer.append(k in possible)
    return answer

def random_capped(rng):
    n=rng.randint(1,11);return [[rng.randint(1,n) for _ in range(n)],rng.randint(1,25)]

def stable_oracle(args):
    nums=args[0];answer=0
    for mask in range(1,1<<len(nums)):
        parity=[nums[i]&1 for i in range(len(nums)) if mask>>i&1]
        if all(not (a==b==c) for a,b,c in zip(parity,parity[1:],parity[2:])):answer+=1
    return answer%(10**9+7)

def random_stable(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,12))]]

def neighbors(values):
    n=len(values);result=set()
    for left in range(n):
        for right in range(left,n):
            block=values[left:right+1];remaining=values[:left]+values[right+1:]
            for position in range(len(remaining)+1):result.add(remaining[:position]+block+remaining[position:])
    result.discard(values);return result

def merge_oracle(args):
    start,target=map(tuple,args)
    if start==target:return 0
    front={start};back={target};seen_front={start};seen_back={target};steps=0
    while front:
        if len(front)>len(back):front,back=back,front;seen_front,seen_back=seen_back,seen_front
        steps+=1;new=set()
        for state in front:
            for nxt in neighbors(state):
                if nxt in seen_back:return steps
                if nxt not in seen_front:seen_front.add(nxt);new.add(nxt)
        front=new

def random_merge(rng):
    n=rng.randint(2,6);first=[rng.randint(-3,3) for _ in range(n)];second=first[:];rng.shuffle(second);return [first,second]


XOR_BASIS='''def maximum_subsequence_xor(nums):
    basis=[0]*31
    for value in nums:
        while value:
            bit=value.bit_length()-1
            if basis[bit]:value^=basis[bit]
            else:basis[bit]=value;break
    answer=0
    for bit in range(30,-1,-1):answer=max(answer,answer^basis[bit])
    return answer
'''

INDEX_SUM='''def minimum_common_index_sum(nums1,nums2):
    earliest={}
    for index,value in enumerate(nums2):
        if value not in earliest:earliest[value]=index
    answer=None
    for index,value in enumerate(nums1):
        if value in earliest:
            candidate=index+earliest[value];answer=candidate if answer is None else min(answer,candidate)
    return -1 if answer is None else answer
'''

CAPPED='''def capped_subsequence_sum_possible(nums,k):
    n=len(nums);counts=[0]*(n+1)
    for value in nums:counts[value]+=1
    reachable=1;remaining=n;answer=[];mask=(1<<(k+1))-1
    for cap in range(1,n+1):
        possible=False
        for capped_count in range(min(remaining,k//cap)+1):
            target=k-capped_count*cap
            if reachable>>target&1:possible=True;break
        answer.append(possible)
        for _ in range(counts[cap]):reachable=(reachable|(reachable<<cap))&mask
        remaining-=counts[cap]
    return answer
'''

STABLE='''def count_stable_subsequences(nums):
    mod=10**9+7;states=[[0,0],[0,0]]
    for value in nums:
        parity=value&1;other=parity^1
        one=(1+states[other][0]+states[other][1])%mod;two=states[parity][0]
        states[parity][0]=(states[parity][0]+one)%mod;states[parity][1]=(states[parity][1]+two)%mod
    return sum(map(sum,states))%mod
'''

MERGE='''def minimum_split_merge_operations(nums1,nums2):
    from collections import deque
    start=tuple(nums1);target=tuple(nums2);queue=deque([(start,0)]);seen={start};n=len(start)
    while queue:
        current,distance=queue.popleft()
        if current==target:return distance
        for left in range(n):
            for right in range(left,n):
                block=current[left:right+1];remaining=current[:left]+current[right+1:]
                for position in range(len(remaining)+1):
                    nxt=remaining[:position]+block+remaining[position:]
                    if nxt not in seen:seen.add(nxt);queue.append((nxt,distance+1))
'''

def lesson(a,b,c,d):return [a,b,c,d]

X_CASES=[[x] for x in ([0,0],[1,1],[1,2],[5,3],[7,7,7],[1,2,4,8],[3,5,6],[8,10,12],[0,1,3,7],[536870912,1],[5,9,12,6],[1023,512,255])]
I_CASES=[[a,b] for a,b in (([1],[1]),([1],[2]),([1,2],[2,1]),([1,1],[1,2]),([3,2,1],[1,2,3]),([-1,0],[2,-1]),([5,4,3],[3,4,5]),([1,2,1],[3,1,3]),([0,0,1],[1,0,0]),([9,8,7,6],[5,6,7,8]),([-3,-2,-1],[-1,-2,-3]),([4,5,6,4],[7,4,5,6]))]
C_CASES=[[a,k] for a,k in (([1],1),([1],2),([2,2],3),([1,2,3],4),([3,3,3],5),([1,1,1,1],3),([2,3,3],6),([4,1,4,1],7),([1,2,3,4,5],10),([5,5,2,2,1],8),([3,1,4,1,5],9),([2,5,2,5,2,5],12))]
S_CASES=[[x] for x in ([1],[2,4],[1,3],[1,3,5,7],[2,4,6],[1,2,3],[2,3,4,4],[1,2,1,2,1],[2,2,1,1,2],[5,7,2,4,9],[1,1,2,2,3,3],[6,3,8,5,10,7])]
M_CASES=[[a,b] for a,b in (([1,2],[1,2]),([1,2],[2,1]),([1,2,3],[2,3,1]),([1,2,3],[3,2,1]),([1,1,2],[2,1,1]),([0,-1,2],[-1,2,0]),([1,2,3,4],[3,4,1,2]),([1,2,1,3],[1,3,1,2]),([5,4,3,2,1],[1,2,3,4,5]),([1,1,2,2],[2,2,1,1]),([3,1,4,1,5],[1,5,3,1,4]),([2,7,1,8,2,8],[8,2,8,1,7,2]))]

BATCH={
3681:entry('maximum_subsequence_xor',[('nums','list[int]')],'int',['arrays','bit manipulation','linear basis'],['Two to 100,000 nonnegative integers up to one billion.','The two chosen subsequences may overlap or be empty.','Maximize XOR(first) XOR XOR(second).'],[([[1,2,3]],'The achievable maximum is three.'),([[5,2]],'Choosing five and two separately produces seven.')],X_CASES,XOR_BASIS,[XOR_BASIS.replace('range(30,-1,-1)','range(28,-1,-1)'),XOR_BASIS.replace('answer=max(answer,answer^basis[bit])','answer^=basis[bit]')],['Never considers bit twenty-nine in the final maximization.','Blindly XORs every basis vector instead of greedily improving the result.'],xor_oracle,random_xor,lesson('An element included in both subsequences cancels, so only elements included in exactly one matter.','The problem is therefore maximum subset XOR, solved by a binary linear basis.','Insert each value by eliminating its highest bit, then greedily improve the answer from high bits down.','Every XOR of the two subsequences is a subset XOR and every subset XOR is attainable by placing that subset in only one subsequence.'),'O(n log V)','O(log V)',8),
3682:entry('minimum_common_index_sum',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','hash maps'],['Equal-length arrays contain up to 100,000 signed integers.','A good pair holds equal values across the arrays.','Return the minimum i+j, or negative one if none exists.'],[([[3,2,1],[1,3,1]],'Value three at indices zero and one gives the minimum sum one.'),([[5,1,2],[2,1,3]],'Values one and two both achieve index sum two.')],I_CASES,INDEX_SUM,[INDEX_SUM.replace('if value not in earliest:earliest[value]=index','earliest[value]=index'),INDEX_SUM.replace('min(answer,candidate)','max(answer,candidate)')],['Stores the last second-array index instead of the earliest.','Chooses the maximum matching index sum after the first match.'],index_oracle,random_index,lesson('For a fixed value, only its earliest position in the second array can minimize a sum.','Build an earliest-index map, then scan the first array and minimize i+map[value].','Preserve the first occurrence in nums2 and return negative one when no mapped value appears.','Replacing either index by a later occurrence cannot improve the sum, so the map loses no optimum.'),'O(n)','O(n)',5),
3685:entry('capped_subsequence_sum_possible',[('nums','list[int]'),('k','int')],'list[bool]',['arrays','dynamic programming','bitsets'],['One to 4,000 values, each between one and n; k is at most 4,000.','For every cap x from one through n, replace each value by min(value,x).','Return whether a nonempty subsequence can sum exactly to k.'],[([[4,3,2,4],5],'Caps one and two cannot form five; caps three and four can.'),([[1,2,3,4,5],3],'Every cap permits a subsequence summing to three.')],C_CASES,CAPPED,[CAPPED.replace('min(remaining,k//cap)+1','min(remaining,k//cap)'),CAPPED.replace('remaining-=counts[cap]','remaining-=counts[cap]+1')],['Omits the largest feasible number of capped elements.','Removes an extra capped item from later-cap availability.'],capped_oracle,random_capped,lesson('At cap x, values below x keep their value and every remaining value contributes exactly x.','Maintain subset sums of values already below the cap and try t capped elements for k-t*x.','Use a bitset for processed values; answer the cap, then insert values equal to x and reduce the remaining count.','Every capped subsequence uniquely splits into processed original values and t still-capped values, so the test is exact.'),'O(n*k/word + k log n)','O(k+n)',6),
3686:entry('count_stable_subsequences',[('nums','list[int]')],'int',['arrays','dynamic programming'],['Up to 100,000 positive integers.','A selected subsequence may not contain three consecutive selected values of one parity.','Count nonempty stable subsequences modulo 1,000,000,007.'],[([[1,3,5]],'All nonempty subsequences except the full three-odd sequence are stable, giving six.'),([[2,3,4,2]],'Only the selected even triple [2,4,2] is unstable, leaving fourteen.')],S_CASES,STABLE,[STABLE.replace('two=states[parity][0]','two=states[parity][0]+states[parity][1]'),STABLE.replace("parity=value&1","parity=0")],['Allows extending an already length-two same-parity run.','Treats every value as even and loses parity transitions.'],stable_oracle,random_stable,lesson('Only the last parity and whether its current run has length one or two affect future validity.','Maintain four counts: parity zero/one crossed with run length one/two.','A new value starts alone or follows either opposite-parity state into run one; it extends same-parity run one into run two.','These transitions enumerate every stable subsequence exactly when its final element is processed and exclude precisely the forbidden third equal-parity choice.'),'O(n)','O(1)',8),
3690:entry('minimum_split_merge_operations',[('nums1','list[int]'),('nums2','list[int]')],'int',['arrays','breadth first search'],['Both arrays have equal length between two and six.','nums2 is a permutation of nums1, including duplicate multiplicities.','One move removes any contiguous block and reinserts it unchanged anywhere.'],[([[3,1,2],[1,2,3]],'Move the leading three to the end in one operation.'),([[1,1,2,3,4,5],[5,4,3,2,1,1]],'Three block moves are necessary and sufficient.')],M_CASES,MERGE,[MERGE.replace('for right in range(left,n)','for right in range(left,left+1)'),MERGE.replace('if current==target:return distance','if current==target:return max(0,distance-1)')],['Allows moving only single elements and misses optimal multi-element blocks.','Undercounts by omitting the final move into the target state.'],merge_oracle,random_merge,lesson('The length-six limit makes the finite permutation state graph small enough for BFS.','Treat each distinct array arrangement as a node and every block removal/reinsertion as one edge.','Generate all left/right blocks and insertion positions, deduplicate states, and stop when the target is dequeued.','All legal operations are unit-weight edges, so BFS depth is the minimum number of split-and-merge moves.'),'O(n! * n^3)','O(n!)',6),
}
