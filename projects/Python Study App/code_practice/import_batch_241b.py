"""Triangle geometry, balanced swaps, dynamic GCD queries, zigzag trees, and stable indices."""
from itertools import combinations
from math import acos,degrees,gcd
from .import_batch_055 import entry


def triangle_oracle(args):
    a,b,c=sorted(args[0])
    if a+b<=c:return []
    result=[]
    for opposite,left,right in ((a,b,c),(b,a,c),(c,a,b)):
        result.append(degrees(acos((left*left+right*right-opposite*opposite)/(2*left*right))))
    return sorted(result)
def random_triangle(rng):return [[rng.randint(1,100) for _ in range(3)]]

def balanced_oracle(args):
    text=args[0];best=0
    variants={text}
    for i in range(len(text)):
        for j in range(i+1,len(text)):
            values=list(text);values[i],values[j]=values[j],values[i];variants.add(''.join(values))
    for value in variants:
        for left in range(len(value)):
            zeros=ones=0
            for right in range(left,len(value)):
                zeros+=value[right]=='0';ones+=value[right]=='1'
                if zeros==ones:best=max(best,right-left+1)
    return best
def random_balanced(rng):return [''.join(rng.choice('01') for _ in range(rng.randint(1,14)))]

def queries_oracle(args):
    nums,p,queries=args;values=nums[:];answer=0
    for index,value in queries:
        values[index]=value;good=False
        for mask in range(1,1<<len(values)):
            if mask==(1<<len(values))-1:continue
            current=0
            for i,item in enumerate(values):
                if mask>>i&1:current=gcd(current,item)
            if current==p:good=True;break
        answer+=good
    return answer
def random_queries(rng):
    n=rng.randint(1,8);return [[rng.randint(1,30) for _ in range(n)],rng.randint(1,8),[[rng.randrange(n),rng.randint(1,30)] for _ in range(rng.randint(1,8))]]

def tree_levels(values):
    if not values or values[0] is None:return []
    levels=[];queue=[values[0]];cursor=1
    while queue:
        levels.append(queue);next_level=[]
        for _ in queue:
            for _ in range(2):
                if cursor<len(values):
                    value=values[cursor];cursor+=1
                    if value is not None:next_level.append(value)
        queue=next_level
    return levels
def zigzag_oracle(args):
    values=args[0]
    if not values:return []
    # Build indexed nodes so missing-child stop conditions remain visible.
    nodes=[];queue=[];cursor=0
    if values[0] is None:return []
    nodes.append([values[0],None,None]);queue=[0];cursor=1
    while queue and cursor<len(values):
        parent=queue.pop(0)
        for side in (1,2):
            if cursor>=len(values):break
            value=values[cursor];cursor+=1
            if value is not None:
                child=len(nodes);nodes.append([value,None,None]);nodes[parent][side]=child;queue.append(child)
    answer=[];level=[0];left=True
    while level:
        total=0
        for node_index in (level if left else reversed(level)):
            child=nodes[node_index][1 if left else 2]
            if child is None:break
            total+=nodes[node_index][0]
        answer.append(total);level=[child for i in level for child in nodes[i][1:] if child is not None];left=not left
    return answer
def random_zigzag(rng):return [[rng.randint(-10,20) for _ in range(rng.randint(1,15))]]

def stable_oracle(args):
    nums,k=args
    for i in range(len(nums)):
        if max(nums[:i+1])-min(nums[i:])<=k:return i
    return -1
def random_stable(rng):return [[rng.randint(-30,30) for _ in range(rng.randint(1,40))],rng.randint(-10,50)]

TRIANGLE='''def triangle_angles(sides):
    from math import acos,degrees
    a,b,c=sorted(sides)
    if a+b<=c:return []
    first=degrees(acos((b*b+c*c-a*a)/(2*b*c)))
    second=degrees(acos((a*a+c*c-b*b)/(2*a*c)))
    return [first,second,180-first-second]
'''

BALANCED='''def longest_balanced_after_swap(s):
    zeros=s.count('0');ones=len(s)-zeros;positions={0:[-1]};prefix=0;answer=0
    for i,character in enumerate(s):
        prefix+=1 if character=='1' else -1
        positions.setdefault(prefix,[]).append(i);answer=max(answer,i-positions[prefix][0])
        for difference,available in ((-2,zeros),(2,ones)):
            prior=positions.get(prefix+difference)
            if prior:
                if (i-prior[0]-2)//2<available:answer=max(answer,i-prior[0])
                elif len(prior)>1:answer=max(answer,i-prior[1])
    return answer
'''

QUERIES='''def count_good_subsequence_queries(nums,p,queries):
    from math import gcd
    n=len(nums);size=1
    while size<n:size*=2
    tree=[0]*(2*size)
    divisible=0
    def update(index,value):
        index+=size;tree[index]=value;index//=2
        while index:tree[index]=gcd(tree[2*index],tree[2*index+1]);index//=2
    for i,value in enumerate(nums):
        if value%p==0:update(i,value);divisible+=1
    answer=0
    for index,value in queries:
        if nums[index]%p==0:divisible-=1;update(index,0)
        if value%p==0:divisible+=1;update(index,value)
        nums[index]=value
        if tree[1]!=p:continue
        if divisible<n or n>6:answer+=1;continue
        prefix=[0]*(n+1);suffix=[0]*(n+1)
        for i in range(n):prefix[i+1]=gcd(prefix[i],nums[i])
        for i in range(n-1,-1,-1):suffix[i]=gcd(suffix[i+1],nums[i])
        if any(gcd(prefix[i],suffix[i+1])==p for i in range(n)):answer+=1
    return answer
'''

ZIGZAG='''def zigzag_level_sums(root):
    if root is None:return []
    level=[root];left=True;answer=[]
    while level:
        total=0
        for node in (level if left else reversed(level)):
            child=node.left if left else node.right
            if child is None:break
            total+=node.val
        answer.append(total);level=[child for node in level for child in (node.left,node.right) if child is not None];left=not left
    return answer
'''

STABLE='''def smallest_stable_index(nums,k):
    suffix=[0]*len(nums);suffix[-1]=nums[-1]
    for i in range(len(nums)-2,-1,-1):suffix[i]=min(nums[i],suffix[i+1])
    maximum=-10**30
    for i,value in enumerate(nums):
        maximum=max(maximum,value)
        if maximum-suffix[i]<=k:return i
    return -1
'''

def lesson(a,b,c,d):return [a,b,c,d]
T_CASES=[[[*v]] for v in ([3,4,5],[1,1,1],[1,1,2],[2,3,4],[5,5,8],[6,8,10],[7,10,5],[10,10,12],[2,2,3],[4,7,9],[8,15,17],[9,9,9],[3,5,7],[20,21,29],[100,100,199])]
B_CASES=[[s] for s in ('100001','0','1','01','00','0011','0101','111000','000111','101010','11000','00001','11110','10010','00101101')]
Q_CASES=[[a,p,q] for a,p,q in (([4,8,12,16],2,[[0,3],[2,6]]),([2],2,[[0,2]]),([2,4],2,[[0,3]]),([6,10,15],5,[[0,5]]),([3,6,9],3,[[1,12]]),([4,6,8],2,[[1,5],[1,10]]),([7,14,21],7,[[0,8]]),([2,3,5],1,[[0,4]]),([8,12,20,28],4,[[2,16]]),([5,10],5,[[1,15]]),([9,15,21],3,[[2,22],[2,18]]),([6,35,10],5,[[0,15]]),([2,4,6,8,10,12,14],2,[[0,16]]),([11,22,33],11,[[1,44]]),([4,9,25],1,[[1,10],[2,14]]))]
Z_CASES=[[v] for v in ([5,2,8,1,None,9,6],[1],[1,2],[1,None,2],[1,2,3],[1,2,3,4,5,6,7],[4,2,6,None,3,5],[0,-1,2,-3,None,1,4],[8,4,12,2,6,10,14],[5,1,9,None,2,7,None],[3,2,4,1,None,None,5],[10,5,15,2,7,12,20],[1,None,2,None,3],[7,3,9,1,5,None,10],[6,2,8,None,4,7,9])]
S_CASES=[[a,k] for a,k in (([5,0,1,4],3),([1],0),([-5],0),([1,2],0),([2,1],1),([-5,-3],0),([3,1,2],2),([10,0,5],5),([1,1,1],0),([5,4,3,2],1),([-10,-20,-5],15),([0,10,0],9),([7,2,8,1],6),([3,9,4,6],5),([100,1,50],49))]

BATCH={
3899:entry('triangle_angles',[('sides','list[int]')],'list[float]',['arrays','geometry','math'],['sides contains exactly three positive integers.','Return an empty list when the triangle inequality fails.','Otherwise return the three interior angles in nondecreasing degree order.'],[([[3,4,5]],'The 3-4-5 right triangle has angles about 36.86990, 53.13010, and 90 degrees.'),([[1,1,2]],'The two shorter sides equal the longest, giving zero area, so return an empty list.')],T_CASES,TRIANGLE,[TRIANGLE.replace('a+b<=c','a+b<c'),TRIANGLE.replace('180-first-second','180-first+second')],['Accepts a degenerate zero-area triangle.','Uses the wrong sign when deriving the third angle from the 180-degree sum.'],triangle_oracle,random_triangle,lesson('Sort the sides so both validity and angle order align.','Reject when the two smaller sides do not exceed the largest.','Apply the law of cosines to the first two angles and derive the third from their 180-degree sum.','Larger sides face larger angles, so sorted sides yield sorted results; the cosine law uniquely determines the valid triangle.'),'O(1)','O(1)',5),
3900:entry('longest_balanced_after_swap',[('s','str')],'int',['strings','prefix sums','hash maps'],['s is a nonempty binary string.','You may swap any two positions at most once, including positions outside the chosen substring.','Return the greatest substring length containing equal numbers of zeroes and ones after the swap.'],[(['100001'],'Swap one endpoint one with an interior zero to obtain a balanced substring of length four.'),(['01'],'The whole string is already balanced, so the answer is two.')],B_CASES,BALANCED,[BALANCED.replace('difference,available in ((-2,zeros),(2,ones))','difference,available in ((-2,zeros),)'),BALANCED.replace('answer=max(answer,i-positions[prefix][0])','answer=max(answer,0)')],['Repairs only substrings with one excess direction and misses the symmetric case.','Ignores already-balanced substrings that need no swap.'],balanced_oracle,random_balanced,lesson('Encode one as +1 and zero as -1; balanced substrings have prefix difference zero.','One cross-boundary swap can repair a substring whose difference is ±2, provided the needed opposite bit exists outside it.','Store occurrence indices for each prefix value, using the earliest feasible boundary and a second boundary when the earliest consumes all available bits.','The three checked differences 0 and ±2 are exactly the changes achievable by at most one swap.'),'O(n)','O(n)',6),
3901:entry('count_good_subsequence_queries',[('nums','list[int]'),('p','int'),('queries','list[list[int]]')],'int',['arrays','segment trees','number theory'],['nums is nonempty, p is positive, and each query [index,value] updates nums permanently.','A good subsequence is nonempty, proper, and has gcd exactly p.','Return how many post-update arrays contain at least one good subsequence.'],[([[4,8,12,16],2,[[0,3],[2,6]]],'After the first update no divisible subset has gcd two; after the second, [6,16] does, so one query qualifies.'),([[2],2,[[0,2]]],'The only nonempty subsequence is the full length-one array and is not proper, so the count is zero.')],Q_CASES,QUERIES,[QUERIES.replace('divisible<n or n>6','divisible<=n or n>6'),QUERIES.replace('tree[1]!=p','tree[1]==p')],['Treats the full array as automatically proper by using a non-strict count condition.','Skips precisely the updates whose divisible-element gcd equals p.'],queries_oracle,random_queries,lesson('Only values divisible by p can participate; their total gcd must be p for any qualifying subset.','Maintain their gcd under updates with a segment tree and track how many are divisible.','If some array element is excluded already, the full divisible set is proper. If all qualify, test deleting one element; for n>6 the gcd witness always has a proper subset.','Adding divisible values cannot change gcd p away from p, so any smaller witness extends to one of these maximal proper subsets.'),'O((n+q)log n)','O(n)',8),
3902:entry('zigzag_level_sums',[('root','TreeNode | None')],'list[int]',['trees','breadth-first search'],['Traverse tree levels starting with left-to-right at the root, then alternate direction.','Within a level, stop before the first visited node missing its direction-side child: left child for left-to-right, right child for right-to-left.','Append the sum processed before that stop for every nonempty level.'],[([[5,2,8,1,None,9,6]],'Root contributes five; next level visits eight first and stops after adding it because two lacks a right child; the final level stops immediately, giving [5,8,0].'),([[1]],'The root lacks its required left child, so its level sum is zero.')],Z_CASES,ZIGZAG,[ZIGZAG.replace('if child is None:break','if child is None:continue'),ZIGZAG.replace('left=not left','left=True')],['Skips a missing-child node but continues instead of stopping the level.','Never alternates traversal direction between levels.'],zigzag_oracle,random_zigzag,lesson('Breadth-first search supplies one complete level at a time in natural left-to-right order.','Iterate that list forward or backward according to direction, checking the required child before adding each node.','Build the next level from actual left and right children, then flip direction.','The break implements the first-missing-child rule exactly, while BFS preserves the requested level boundaries.'),'O(n)','O(w)',6),
3904:entry('smallest_stable_index',[('nums','list[int]'),('k','int')],'int',['arrays','prefix maxima','suffix minima'],['nums is nonempty and may contain negative integers; k is any integer.','At i compare max(nums[0:i+1]) with min(nums[i:n]).','Return the smallest i whose difference is at most k, or -1.'],[([[5,0,1,4],3],'Only index three has prefix maximum five and suffix minimum four within difference three; return three.'),([[-5,-3],0],'At index zero, prefix maximum and suffix minimum are both -5, so return zero.')],S_CASES,STABLE,[STABLE.replace('maximum=-10**30','maximum=0'),STABLE.replace('suffix[i]<=k','suffix[i]<k')],['Initializes the prefix maximum to zero, corrupting all-negative inputs.','Requires a strict difference less than k instead of allowing equality.'],stable_oracle,random_stable,lesson('Precompute the minimum of every suffix.','Scan left to right while maintaining the maximum of the current prefix.','The first index satisfying prefix_max-suffix_min≤k is the required answer.','Both summaries exactly cover the ranges in the definition, and scan order guarantees the smallest qualifying index.'),'O(n)','O(n)',5),
}
BATCH[3899]['comparator']='float_list'
BATCH[3902]['params'][0]=('root','TreeNode | None','treenode')
