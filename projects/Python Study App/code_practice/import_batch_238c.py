"""Digit indices, increasing suffixes, selective rotation, tree distances, and bit ranks."""
from collections import deque
from math import comb
from .import_batch_055 import entry


def good_oracle(args):
    s=args[0];answer=[]
    for index in range(len(s)):
        text=str(index);start=index-len(text)+1
        if start>=0 and ''.join(s[pos] for pos in range(start,index+1))==text:answer.append(index)
    return answer
def random_good(rng):return [''.join(rng.choice('0123456789') for _ in range(rng.randint(1,150)))]

def prefix_oracle(args):
    nums=args[0]
    for removed in range(len(nums)+1):
        rest=nums[removed:]
        if all(rest[i]<rest[i+1] for i in range(len(rest)-1)):return removed
def random_prefix(rng):return [[rng.randint(-30,30) for _ in range(rng.randint(1,40))]]

def rotate_oracle(args):
    nums,k=args;positions=[i for i,value in enumerate(nums) if value>=0]
    if not positions:return nums[:]
    answer=nums[:];values=[nums[i] for i in positions];shift=k%len(values)
    values=values[shift:]+values[:shift]
    for index,value in zip(positions,values):answer[index]=value
    return answer
def random_rotate(rng):return [[rng.randint(-9,9) for _ in range(rng.randint(1,30))],rng.randint(0,100)]

def pythagorean_oracle(args):
    n,edges,x,y,z=args;distance=[[n+1]*n for _ in range(n)]
    for i in range(n):distance[i][i]=0
    for a,b in edges:distance[a][b]=distance[b][a]=1
    for mid in range(n):
        for left in range(n):
            for right in range(n):distance[left][right]=min(distance[left][right],distance[left][mid]+distance[mid][right])
    answer=0
    for node in range(n):
        a,b,c=sorted((distance[node][x],distance[node][y],distance[node][z]));answer+=a*a+b*b==c*c
    return answer
def random_pythagorean(rng):
    n=rng.randint(4,10);targets=rng.sample(range(n),3)
    return [n,[[i,rng.randrange(i)] for i in range(1,n)],*targets]

def count_with_bits(limit,bits):
    if limit<0:return 0
    answer=0;remaining=bits
    for position in range(49,-1,-1):
        if limit>>position&1:
            if 0<=remaining<=position:answer+=comb(position,remaining)
            remaining-=1
            if remaining<0:break
    return answer+(remaining==0)
def nth_bits_oracle(args):
    rank,bits=args;left=1;right=(1<<50)-1
    while left<right:
        middle=(left+right)//2
        if count_with_bits(middle,bits)>=rank:right=middle
        else:left=middle+1
    return left
def random_bits(rng):
    bits=rng.randint(1,8);maximum=comb(30,bits);return [rng.randint(1,min(maximum,10000)),bits]


GOOD='''def good_digit_string_indices(s):
    answer=[]
    for index in range(len(s)):
        text=str(index);start=index-len(text)+1
        if start>=0 and s[start:index+1]==text:answer.append(index)
    return answer
'''

PREFIX='''def minimum_increasing_prefix_removal(nums):
    for index in range(len(nums)-1,0,-1):
        if nums[index-1]>=nums[index]:return index
    return 0
'''

ROTATE='''def rotate_nonnegative_elements(nums,k):
    values=[value for value in nums if value>=0]
    if not values:return nums[:]
    shift=k%len(values);rotated=values[shift:]+values[:shift];answer=nums[:];position=0
    for index,value in enumerate(nums):
        if value>=0:answer[index]=rotated[position];position+=1
    return answer
'''

PYTHAGOREAN='''def count_pythagorean_distance_nodes(n,edges,x,y,z):
    from collections import deque
    graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    def distances(start):
        result=[-1]*n;result[start]=0;queue=deque([start])
        while queue:
            node=queue.popleft()
            for nxt in graph[node]:
                if result[nxt]<0:result[nxt]=result[node]+1;queue.append(nxt)
        return result
    first,second,third=distances(x),distances(y),distances(z);answer=0
    for values in zip(first,second,third):
        a,b,c=sorted(values);answer+=a*a+b*b==c*c
    return answer
'''

BITS='''def nth_integer_with_k_one_bits(n,k):
    from math import comb
    answer=0
    for position in range(49,-1,-1):
        without=comb(position,k) if 0<=k<=position else 0
        if n>without:
            n-=without;answer|=1<<position;k-=1
            if k==0:break
    return answer
'''

def lesson(a,b,c,d):return [a,b,c,d]

G_CASES=[[s] for s in ('0','1','01234','12345','0234567890112','0000000000','0123456789','99999999999','000000000011','101112131415','314159265358979','000102030405060','987654321012345','0012345678910111213')]
P_CASES=[[[*v]] for v in ([1],[1,2,3,4],[4,3,-2,-5],[1,-1,2,3,3,4,5],[2,2],[3,2,1],[-3,-2,-1],[1,3,2,4],[5,1,2,3],[0,-1,0,1],[10,9,8,20],[1,2,2,3,4],[4,1,5,6,7],[-1,-1,-1,-1])]
R_CASES=[[a,k] for a,k in (([1,-2,3,-4],3),([-3,-2,7],1),([5,4,-9,6],2),([-1,-2],5),([0],100),([1,2,3],0),([1,2,3],4),([-1,0,-2,1],1),([4,-1,5,-2,6],2),([0,0,-1,1],3),([9,-8,7,-6,5],10),([-1,2,3,4,-5],1),([1,-1,2,-2,3,-3,4],7),([-9,-8,0,-7],2))]
T_CASES=[[n,e,x,y,z] for n,e,x,y,z in ((4,[[0,1],[0,2],[0,3]],1,2,3),(4,[[0,1],[1,2],[2,3]],0,1,3),(4,[[0,1],[1,2],[1,3]],1,3,0),(5,[[0,1],[0,2],[2,3],[2,4]],0,3,4),(5,[[0,1],[1,2],[2,3],[3,4]],0,2,4),(6,[[0,1],[1,2],[1,3],[3,4],[3,5]],0,2,5),(6,[[0,1],[0,2],[2,3],[3,4],[4,5]],1,3,5),(7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],3,5,6),(7,[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]],0,3,6),(8,[[0,1],[0,2],[0,3],[1,4],[2,5],[3,6],[6,7]],4,5,7),(8,[[0,1],[1,2],[1,3],[3,4],[3,5],[5,6],[5,7]],0,2,7),(9,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6],[6,7],[6,8]],3,7,8),(10,[[0,1],[1,2],[2,3],[1,4],[4,5],[5,6],[4,7],[7,8],[7,9]],0,6,9),(10,[[0,1],[0,2],[2,3],[2,4],[4,5],[4,6],[6,7],[6,8],[8,9]],1,5,9))]
B_CASES=[[n,k] for n,k in ((1,1),(3,1),(4,2),(1,2),(2,2),(10,2),(20,3),(100,3),(5,4),(30,4),(1000,5),(50,6),(1,10),(2,10))]

BATCH={
3817:entry('good_digit_string_indices',[('s','str')],'list[int]',['strings','simulation'],['s contains up to 100,000 decimal digits.','Index i is good when the decimal text of i appears as the suffix ending exactly at s[i].','Return good indices in increasing order.'],[(['0234567890112'],'The suffixes ending at indices zero, eleven, and twelve equal 0, 11, and 12.'),(['01234'],'Each one-digit index matches the digit at its own position.')],G_CASES,GOOD,[GOOD.replace('s[start:index+1]==text','s[index:index+len(text)]==text'),GOOD.replace('start=index-len(text)+1','start=index-len(text)')],['Matches text starting at i rather than ending at i.','Starts the suffix one position too early and compares an extra digit.'],good_oracle,random_good,lesson('The candidate text at index i is fixed: str(i).','Its only possible matching substring ending at i begins at i-len(str(i))+1.','Check that this start is nonnegative and compare exactly that slice.','Every good index must use this unique suffix, so the direct scan is exhaustive and ordered.'),'O(n log n)','O(log n)',5),
3818:entry('minimum_increasing_prefix_removal',[('nums','list[int]')],'int',['arrays','greedy'],['nums has up to 100,000 signed integers.','Remove one prefix, which may be empty or leave a singleton.','Minimize the removed length so the remainder is strictly increasing.'],[([[1,-1,2,3,3,4,5]],'The longest increasing suffix is [3,4,5], beginning at index four.'),([[1,2,3,4]],'The full array is already strictly increasing, so remove zero values.')],P_CASES,PREFIX,[PREFIX.replace('>=','>'),PREFIX.replace('return index','return index+1')],['Treats equal adjacent values as strictly increasing.','Removes one extra value beyond the last bad adjacency.'],prefix_oracle,random_prefix,lesson('Only the longest strictly increasing suffix can remain after removing a prefix.','Scan adjacent pairs from right to left until finding the rightmost non-increasing pair.','Remove through its left endpoint, which means returning the right index of that pair.','Everything to its right is increasing by the scan, while keeping any earlier start would retain this violating pair.'),'O(n)','O(1)',5),
3819:entry('rotate_nonnegative_elements',[('nums','list[int]'),('k','int')],'list[int]',['arrays','simulation'],['nums has up to 100,000 signed integers and k is nonnegative.','Negative values and their positions never change.','Cyclically rotate only the nonnegative subsequence left by k positions.'],[([[1,-2,3,-4],3],'The nonnegative sequence [1,3] rotates left by one to [3,1].'),([[5,4,-9,6],2],'Rotating [5,4,6] left by two gives [6,5,4] in the same nonnegative slots.')],R_CASES,ROTATE,[ROTATE.replace('values[shift:]+values[:shift]','values[-shift:]+values[:-shift]'),ROTATE.replace('if value>=0','if value>0')],['Rotates the selected values to the right instead of left.','Treats zero as negative and leaves it fixed.'],rotate_oracle,random_rotate,lesson('Negative positions form fixed holes; only the ordered nonnegative subsequence changes.','Extract that subsequence, reduce k modulo its length, and concatenate suffix then prefix for a left rotation.','Write the rotated values back into exactly the original nonnegative positions.','Extraction and reinsertion preserve every negative slot, while cyclic indexing produces precisely k left moves.'),'O(n)','O(n)',5),
3820:entry('count_pythagorean_distance_nodes',[('n','int'),('edges','list[list[int]]'),('x','int'),('y','int'),('z','int')],'int',['trees','breadth-first search'],['4≤n≤100,000; edges forms a tree and x,y,z are distinct nodes.','For every node, take its three unweighted distances to x,y,z.','Count nodes whose sorted distances a≤b≤c satisfy a²+b²=c².'],[([4,[[0,1],[0,2],[0,3]],1,2,3],'Each leaf has distances 0,2,2 and the center has 1,1,1; three nodes satisfy after sorting according to the source result.'),([4,[[0,1],[1,2],[1,3]],1,3,0],'Node one has distances 0,1,1, satisfying 0²+1²=1².')],T_CASES,PYTHAGOREAN,[PYTHAGOREAN.replace('a,b,c=sorted(values)','a,b,c=values'),PYTHAGOREAN.replace('a*a+b*b==c*c','a+b==c')],['Assumes x,y,z distances already arrive in nondecreasing order.','Checks ordinary addition instead of the Pythagorean squared relation.'],pythagorean_oracle,random_pythagorean,lesson('Tree distances from one fixed source to every node come from one breadth-first search.','Run BFS independently from x, y, and z.','At each node, sort the three distances and test a²+b²=c².','The three BFS arrays give exact unique-path lengths, and sorting assigns the hypotenuse role to the largest distance.'),'O(n)','O(n)',6),
3821:entry('nth_integer_with_k_one_bits',[('n','int'),('k','int')],'int',['bit manipulation','combinatorics','math'],['n and k are positive and the guaranteed answer is below 2^50.','Order positive integers numerically.','Return the nth integer whose binary representation contains exactly k one bits.'],[([4,2],'The sequence begins 3,5,6,9, so the fourth value is nine.'),([3,1],'The one-bit values are 1,2,4,…, making the third value four.')],B_CASES,BITS,[BITS.replace('if n>without','if n>=without'),BITS.replace('k-=1','k-=2')],['Uses a zero-based comparison and chooses a high bit one rank too early.','Removes two required one bits after choosing a position.'],nth_bits_oracle,random_bits,lesson('Among values using positions 0..p, exactly C(p,k) have bit p equal to zero and k ones below it.','Construct the answer from bit 49 downward, comparing n with the size of the zero-bit group.','If n exceeds that group, subtract it, set the bit, and reduce the remaining one count.','This is lexicographic unranking of fixed-size bit-position subsets, which matches numeric order from the highest bit downward.'),'O(50)','O(1)',8),
}
