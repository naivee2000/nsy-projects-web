"""Alternating subsequences, zigzags, directed index costs, fixed points, and coherent strings."""
from itertools import combinations,product
from .import_batch_055 import entry

MOD=1_000_000_007

def alternating(values):
    differences=[values[i+1]-values[i] for i in range(len(values)-1)]
    return all(value for value in differences) and all(differences[i]*differences[i+1]<0 for i in range(len(differences)-1))
def alternating_oracle(args):
    nums,k=args;best=max(nums)
    for size in range(2,len(nums)+1):
        for indices in combinations(range(len(nums)),size):
            if all(indices[i+1]-indices[i]>=k for i in range(size-1)) and alternating([nums[i] for i in indices]):best=max(best,sum(nums[i] for i in indices))
    return best
def random_alternating(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,13))],rng.randint(1,5)]

def zigzag_oracle(args):
    n,left,right=args;answer=0
    for values in product(range(left,right+1),repeat=n):
        if all(values[i]!=values[i+1] for i in range(n-1)) and all((values[i]-values[i-1])*(values[i+1]-values[i])<0 for i in range(1,n-1)):answer+=1
    return answer%MOD
def random_zigzag(rng):return [rng.randint(1,7),0,rng.randint(1,5)]

def move_oracle(args):
    nums,queries=args;answer=[]
    def step(index,direction):
        destination=index+direction;gap=abs(nums[destination]-nums[index]);other=index-direction
        closest=not(0<=other<len(nums)) or gap<abs(nums[other]-nums[index]) or gap==abs(nums[other]-nums[index]) and destination<index
        return 1 if closest else gap
    for left,right in queries:
        total=0;direction=1 if left<right else -1
        while left!=right:total+=step(left,direction);left+=direction
        answer.append(total)
    return answer
def random_move(rng):
    n=rng.randint(2,25);nums=sorted(rng.sample(range(-100,101),n));return [nums,[[rng.randrange(n),rng.randrange(n)] for _ in range(rng.randint(1,20))]]

def fixed_oracle(args):
    nums=args[0];best=0
    for mask in range(1<<len(nums)):
        values=[nums[i] for i in range(len(nums)) if mask>>i&1]
        best=max(best,sum(value==index for index,value in enumerate(values)))
    return best
def random_fixed(rng):return [[rng.randint(0,12) for _ in range(rng.randint(1,12))]]

def coherent(value):return '011' not in ''.join(value[i] for i in range(len(value))) and False
def flips_oracle(args):
    source=args[0];best=len(source)
    for target in product('01',repeat=len(source)):
        text=''.join(target)
        bad011=any(text[i]=='0' and text[j]=='1' and text[k]=='1' for i in range(len(text)) for j in range(i+1,len(text)) for k in range(j+1,len(text)))
        bad110=any(text[i]=='1' and text[j]=='1' and text[k]=='0' for i in range(len(text)) for j in range(i+1,len(text)) for k in range(j+1,len(text)))
        if not bad011 and not bad110:best=min(best,sum(a!=b for a,b in zip(source,text)))
    return best
def random_flips(rng):return [''.join(rng.choice('01') for _ in range(rng.randint(1,11)))]

ALTERNATING='''def maximum_spaced_alternating_sum(nums,k):
    values=sorted(set(nums));rank={value:i+1 for i,value in enumerate(values)};size=len(values);negative=-10**30
    trees=[[negative]*(size+1) for _ in range(2)]
    def update(tree,index,value):
        while index<=size:tree[index]=max(tree[index],value);index+=index&-index
    def query(tree,index):
        answer=negative
        while index:answer=max(answer,tree[index]);index-=index&-index
        return answer
    states=[[value,value] for value in nums];answer=max(nums)
    for i,value in enumerate(nums):
        if i>=k:
            index=rank[value];lower=query(trees[0],index-1);greater=query(trees[1],size-index)
            states[i][1]=max(states[i][1],lower+value);states[i][0]=max(states[i][0],greater+value)
        eligible=i-k+1
        if eligible>=0:
            index=rank[nums[eligible]];update(trees[0],index,states[eligible][0]);update(trees[1],size-index+1,states[eligible][1])
        answer=max(answer,*states[i])
    return answer
'''

ZIGZAG='''def count_zigzag_arrays(n,l,r):
    modulus=1_000_000_007;width=r-l+1
    if n==1:return width
    up=[value for value in range(width)];down=[width-1-value for value in range(width)]
    for _ in range(2,n):
        prefix=[];running=0
        for value in down:running=(running+value)%modulus;prefix.append(running)
        suffix=[0]*width;running=0
        for i in range(width-1,-1,-1):running=(running+up[i])%modulus;suffix[i]=running
        up=[prefix[i-1] if i else 0 for i in range(width)]
        down=[suffix[i+1] if i+1<width else 0 for i in range(width)]
    return (sum(up)+sum(down))%modulus
'''

MOVE='''def minimum_index_move_cost(nums,queries):
    n=len(nums);forward=[0]*n;backward=[0]*n
    for i in range(1,n):
        gap=nums[i]-nums[i-1]
        forward[i]=forward[i-1]+(gap if i>1 and nums[i-1]-nums[i-2]<=gap else 1)
        backward[i]=backward[i-1]+(gap if i<n-1 and gap>nums[i+1]-nums[i] else 1)
    return [forward[right]-forward[left] if left<right else backward[left]-backward[right] for left,right in queries]
'''

FIXED='''def maximum_fixed_points_after_deletions(nums):
    candidates=[(index,value) for index,value in enumerate(nums) if 0<=value<=index];best=[1]*len(candidates);answer=0
    for j,(index,value) in enumerate(candidates):
        for i in range(j):
            prior_index,prior_value=candidates[i]
            if prior_value<value and prior_index-prior_value<=index-value:best[j]=max(best[j],best[i]+1)
        answer=max(answer,best[j])
    return answer
'''

FLIPS='''def minimum_coherent_flips(s):
    infinity=10**9;states={(0,0):0}
    for original in s:
        updated={}
        for (progress_011,progress_110),cost in states.items():
            for bit in '01':
                if bit=='0':
                    next_011=max(progress_011,1);next_110=progress_110
                    if progress_110==2:continue
                else:
                    next_011=progress_011;next_110=min(2,progress_110+1)
                    if progress_011==2:continue
                    if progress_011==1:next_011=2
                state=(next_011,next_110);updated[state]=min(updated.get(state,infinity),cost+(bit!=original))
        states=updated
    return min(states.values())
'''

def lesson(a,b,c,d):return [a,b,c,d]
A_CASES=[[a,k] for a,k in (([5,4,2],2),([1],1),([1,2],1),([2,1],1),([1,3,2],1),([5,1,4,2],1),([5,1,4,2],2),([1,5,2,6,3],1),([10,1,9,2,8],2),([3,3,3],1),([2,8,1,7,3],2),([9,2,8,1,7,3],3),([1,10,2,9,3,8],2),([4,1,5,2,6],1),([7,2,9,1,8],4))]
Z_CASES=[[n,l,r] for n,l,r in ((3,4,5),(1,0,0),(1,1,3),(2,1,2),(3,1,2),(4,1,2),(3,0,2),(4,0,2),(5,1,3),(2,5,8),(6,0,1),(3,2,5),(5,0,3),(7,1,2),(4,3,6))]
M_CASES=[[a,q] for a,q in (([-5,-2,3],[[0,2],[2,0],[1,2]]),([1,3],[[0,1],[1,0]]),([1,2,10],[[0,2]]),([0,5,6],[[2,0]]),([-10,-5,0,20],[[0,3],[3,0]]),([1,4,9,10],[[1,3]]),([2,8,9,15],[[3,1]]),([0,1,3,10],[[0,0]]),([5,6,20],[[0,2],[2,1]]),([-8,-3,4,5],[[1,3]]),([1,10,11,30],[[3,0]]),([0,2,5,9,10],[[0,4]]),([3,7,8,20,21],[[4,0]]),([-20,-10,-9,0],[[0,3]]),([1,100,101],[[2,0]]))]
F_CASES=[[[*v]] for v in ([0,2,1],[0],[1],[1,0],[2,0],[0,1,2],[2,1,0],[3,0,2,1],[0,5,1,3,4],[4,0,1,2,3],[1,2,3,4],[0,0,2,3],[5,1,2,0,4],[2,4,1,3,0],[0,3,2,5,4,1])]
C_CASES=[[s] for s in ('1010','0','1','011','110','0101','0011','1110','0001','101010','0110','1101','001011','111000','01010101')]

BATCH={
3915:entry('maximum_spaced_alternating_sum',[('nums','list[int]'),('k','int')],'int',['arrays','fenwick trees','dynamic programming'],['nums contains positive integers and k is positive.','Choose indices at least k apart whose adjacent selected values strictly alternate up and down.','A singleton is valid; maximize the sum.'],[([[5,4,2],2],'Indices zero and two are two apart and decrease strictly, giving sum seven.'),([[1,3,2],1],'The whole sequence alternates up then down and sums six.')],A_CASES,ALTERNATING,[ALTERNATING.replace('index-1','index'),ALTERNATING.replace('eligible=i-k+1','eligible=i-k')],['Allows equal consecutive selected values in the lower-value transition.','Delays eligibility by one extra index and misses valid pairs exactly k apart.'],alternating_oracle,random_alternating,lesson('Track best sums ending after an upward or downward comparison.','Fenwick prefix maxima over value ranks find the best smaller predecessor; a reversed-rank tree finds larger predecessors.','Delay insertion until an index is at least k behind the current position.','Strict rank ranges enforce alternating inequalities, and delayed updates enforce distance while every valid predecessor remains queryable.'),'O(n log n)','O(n)',8),
3916:entry('count_zigzag_arrays',[('n','int'),('l','int'),('r','int')],'int',['arrays','dynamic programming','prefix sums'],['n is positive and l≤r.','Every value lies in [l,r], adjacent values differ, and three consecutive values may not be strictly monotone.','Return the count modulo 1,000,000,007.'],[([3,4,5],'The only length-three arrays are [4,5,4] and [5,4,5], giving two.'),([1,1,3],'Any one of the three values forms a valid length-one array.')],Z_CASES,ZIGZAG,[ZIGZAG.replace('prefix[i-1] if i else 0','prefix[i]'),ZIGZAG.replace('suffix[i+1] if i+1<width else 0','suffix[i]')],['Allows an equal predecessor in upward transitions.','Allows an equal predecessor in downward transitions.'],zigzag_oracle,random_zigzag,lesson('After two elements, validity depends only on the last value and whether the last comparison went up or down.','An up step must follow a down step from a smaller value; a down step symmetrically follows an up step from a larger value.','Prefix and suffix sums evaluate all strict predecessor ranges in linear time per position.','Alternating comparison directions are exactly the condition excluding equal neighbors and monotone triples.'),'O(n(r-l+1))','O(r-l+1)',8),
3919:entry('minimum_index_move_cost',[('nums','list[int]'),('queries','list[list[int]]')],'list[int]',['arrays','prefix sums','queries'],['nums is strictly increasing with at least two elements.','Move only between adjacent indices; the move costs one when the destination is a closest neighbor of the source, otherwise the value gap.','Return the minimum monotone-path cost for every [left,right] query.'],[([[-5,-2,3],[[0,2],[2,0],[1,2]]],'Forward costs are one then five, backward costs one per closest step, giving [6,2,5].'),([[1,3],[[0,1],[1,0]]],'Each endpoint has only one neighbor, so both directions cost one.')],M_CASES,MOVE,[MOVE.replace('<=gap','<gap'),MOVE.replace('gap>nums[i+1]-nums[i]','gap>=nums[i+1]-nums[i]')],['Breaks closest-neighbor ties in the wrong direction for forward moves.','Breaks ties in the wrong direction for backward moves.'],move_oracle,random_move,lesson('On a line, any detour adds positive cost, so the optimal route follows adjacent indices monotonically.','Precompute the directed cost of every forward and backward edge using the closer-neighbor rule.','Prefix sums turn each monotone query into one subtraction.','The edge rule is local to its source; summing exactly those directed edges yields the unique no-detour path cost.'),'O(n+q)','O(n)',5),
3920:entry('maximum_fixed_points_after_deletions',[('nums','list[int]')],'int',['arrays','dynamic programming'],['nums is a nonempty nonnegative integer array.','Delete any elements; retained elements are renumbered from zero.','Maximize retained positions whose value equals their new index.'],[([[0,2,1]],'Keep values zero and one, which become indices zero and one, producing two fixed points.'),([[1]],'Keeping or deleting the value yields no fixed point, so return zero.')],F_CASES,FIXED,[FIXED.replace('answer=max(answer,best[j])','answer+=1'),FIXED.replace('prior_index-prior_value<=index-value','prior_index-prior_value<index-value')],['Counts every individually eligible candidate even when they cannot coexist in one retained subsequence.','Rejects feasible chains whose filler capacity is exactly tight.'],fixed_oracle,random_fixed,lesson('A fixed point at original index i with value v needs exactly v retained elements before it, so v≤i.','For consecutive fixed points (i,v) and (j,w), require v<w and enough intervening positions: w-v≤j-i.','Run longest-chain DP over eligible (index,value) pairs using the equivalent slack condition i-v≤j-w.','Fill unused retained ranks with arbitrary intervening elements, making the chain conditions both necessary and sufficient.'),'O(n²)','O(n)',8),
3922:entry('minimum_coherent_flips',[('s','str')],'int',['strings','dynamic programming','automata'],['s is a nonempty binary string.','Flip individual bits so the result contains neither 011 nor 110 as a subsequence.','Return the minimum flips.'],[(['1010'],'Flipping one middle bit can avoid both forbidden subsequences, so the minimum is one.'),(['011'],'One flip is necessary and sufficient to destroy subsequence 011.')],C_CASES,FLIPS,[FLIPS.replace("if progress_110==2:continue","if False:continue"),FLIPS.replace("cost+(bit!=original)","cost+1")],['Allows appending zero after two earlier ones, completing forbidden subsequence 110.','Charges a flip even when keeping the original bit.'],flips_oracle,random_flips,lesson('A subsequence constraint can be recognized by two three-stage prefix automata.','Track the longest matched prefix of 011 and of 110.','For each source character, try output zero and one, add flip cost, and discard transitions completing either pattern.','The pair of prefix states retains exactly the history relevant to either forbidden subsequence, so dynamic programming finds the cheapest accepted output.'),'O(n)','O(1)',6),
}
