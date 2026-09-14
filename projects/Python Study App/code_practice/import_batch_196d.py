"""Mirror matches, signal states, graph degrees, stable splits, and digit placement."""
from .import_batch_055 import entry, EXTRA_BOUNDARIES

EXTRA_BOUNDARIES['adjacency_matrix_vertex_degrees']=[
    [[[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]]],
    [[[0,1,0,0,0],[1,0,1,0,0],[0,1,0,1,0],[0,0,1,0,1],[0,0,0,1,0]]],
    [[[0,1,1,1,1],[1,0,1,1,1],[1,1,0,1,1],[1,1,1,0,1],[1,1,1,1,0]]],
]

def mirror_oracle(a):
    s=a[0];return next((i for i in range(len(s)) if s[i]==s[-1-i]),-1)
def random_mirror(r):return [''.join(r.choice('abcdef') for _ in range(r.randint(1,50)))]
def signal_oracle(a):
    t=a[0];return 'Green' if t==0 else 'Orange' if t==30 else 'Red' if 31<=t<=90 else 'Invalid'
def random_signal(r):return [r.randint(-20,120)]
def degree_oracle(a):return [sum(row) for row in a[0]]
def random_degree(r):
    n=r.randint(1,10);g=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            if r.random()<.4:g[i][j]=g[j][i]=1
    return [g]
def stable_oracle(a):
    nums,k=a
    return next((i for i in range(len(nums)) if max(nums[:i+1])-min(nums[i:])<=k),-1)
def random_stable(r):return [[r.randint(-30,50) for _ in range(r.randint(1,30))],r.randint(0,50)]
def digit_oracle(a):
    n,x=a;s=str(n);return str(x) in s and s[0]!=str(x)
def random_digit(r):return [r.randint(0,10**10),r.randint(0,9)]

MIRROR='''def first_matching_mirrored_index(s):
    for i,char in enumerate(s):
        if char==s[len(s)-1-i]:return i
    return -1
'''
SIGNAL='''def traffic_signal_color(timer):
    if timer==0:return 'Green'
    if timer==30:return 'Orange'
    if 31<=timer<=90:return 'Red'
    return 'Invalid'
'''
DEGREE='''def adjacency_matrix_vertex_degrees(matrix):
    return [sum(row) for row in matrix]
'''
STABLE='''def smallest_stable_split_index(nums,k):
    suffix=[];best=float('inf')
    for value in reversed(nums):best=min(best,value);suffix.append(best)
    suffix.reverse();prefix=float('-inf')
    for i,value in enumerate(nums):
        prefix=max(prefix,value)
        if prefix-suffix[i]<=k:return i
    return -1
'''
DIGIT='''def is_valid_contained_nonleading_digit(n,x):
    text=str(n);digit=str(x)
    return digit in text and text[0]!=digit
'''

BATCH={
3884:entry('first_matching_mirrored_index',[('s','str')],'int',['strings','two pointers'],['Compare each character with the character equally far from the other end.','Return the smallest index whose characters match.','Return -1 when no mirrored positions match.'],[(['abcacbd'],'Index one contains b and mirrors the b at index five, so it is the first match.'),(['ab'],'Neither mirrored comparison matches.')],[[s] for s in ['a','ab','aa','abcacbd','abc','abba','abcd','racecar','xyzx','aabb','abcdefa','zzxy','mnopon','cabac']],MIRROR,[MIRROR.replace('==','!='),MIRROR.replace('return i','return len(s)-1-i')],['Returns the first mirrored mismatch.','Returns the opposite index instead of the smallest matching index.'],mirror_oracle,random_mirror,['Scan indices from zero upward.','Map i to n-1-i at the opposite end.','Return immediately when the two characters agree.','Early return supplies the smallest matching index.'],'O(n)','O(1)',3),
3894:entry('traffic_signal_color',[('timer','int')],'str',['conditionals','simulation'],['Return Green exactly at timer zero and Orange exactly at timer thirty.','Return Red for timers from 31 through 90 inclusive.','Return Invalid for every other value.'],[([60],'Sixty lies in the inclusive red interval.'),([30],'Thirty is the exact orange state.')],[[t] for t in [-1,0,1,29,30,31,60,89,90,91,100,15,45,120]],SIGNAL,[SIGNAL.replace('timer==30','timer<=30'),SIGNAL.replace('31<=timer<=90','31<timer<90')],['Labels other low timer values Orange.','Excludes both endpoints of the Red interval.'],signal_oracle,random_signal,['Check the two exact-value states first.','Then test the closed interval 31 through 90.','Return Invalid after all recognized cases fail.','The branches are disjoint and cover every integer timer.'],'O(1)','O(1)',3),
3898:entry('adjacency_matrix_vertex_degrees',[('matrix','list[list[int]]')],'list[int]',['graphs','matrices'],['matrix is the symmetric zero-one adjacency matrix of an undirected graph.','The degree of a vertex is the number of incident edges.','Return degrees in vertex-index order.'],[([[[0,1,1],[1,0,1],[1,1,0]]],'Every vertex connects to the other two, so all degrees are two.'),([[[0,0],[0,0]]],'The graph has no edges, so both degrees are zero.')],[[g] for g in [[[0]],[[0,1],[1,0]],[[0,0],[0,0]],[[0,1,1],[1,0,1],[1,1,0]],[[0,1,0],[1,0,0],[0,0,0]],[[0,1,0,1],[1,0,1,0],[0,1,0,1],[1,0,1,0]],[[0,0,1],[0,0,1],[1,1,0]],[[0,1,1,1],[1,0,0,0],[1,0,0,0],[1,0,0,0]],[[0,1],[1,0]],[[0,0,0],[0,0,0],[0,0,0]],[[0,1,0],[1,0,1],[0,1,0]],[[0,1,1],[1,0,0],[1,0,0]],[[0,1,0,0],[1,0,1,1],[0,1,0,0],[0,1,0,0]],[[0,0],[0,0]]]],DEGREE,[DEGREE.replace('sum(row)','sum(row)//2'),DEGREE.replace('sum(row)','sum(row[1:])')],['Halves each vertex degree.','Ignores every edge represented in the first matrix column.'],degree_oracle,random_degree,['Each matrix row describes all neighbors of one vertex.','A one contributes one incident edge to that row’s vertex.','Sum each row independently.','Preserving row order preserves vertex-index order.'],'O(n^2)','O(n)',3),
3903:entry('smallest_stable_split_index',[('nums','list[int]'),('k','int')],'int',['arrays','prefix maxima','suffix minima'],['At index i, compare the maximum over nums[0..i] with the minimum over nums[i..n-1].','The index is stable when their difference is at most k.','Return the smallest stable index, or -1.'],[([[5,0,1,4],3],'Only index three has prefix maximum five and suffix minimum four within distance three.'),([[1,2,3],0],'Index zero has prefix maximum and suffix minimum both one, so return zero.')],[[n,k] for n,k in [([1],0),([5,0,1,4],3),([1,2,3],0),([3,2,1],0),([1,5,2],2),([10,1],5),([0,0],0),([-1,0,1],0),([4,3,5,2],3),([9,8,7],2),([1,10,1],9),([5,4,3,2,1],4),([2,7,3,8],5),([100,0,99],1)]],STABLE,[STABLE.replace('prefix-suffix[i]<=k','prefix-suffix[i]<k'),STABLE.replace('suffix[i]','suffix[0]')],['Uses a strict bound instead of allowing equality.','Uses the whole-array suffix minimum at every index.'],stable_oracle,random_stable,['Precompute the minimum of every suffix.','Scan left to right while maintaining the prefix maximum.','Test their difference against k at each index.','Return the first passing index to enforce smallest order.'],'O(n)','O(n)',3),
3908:entry('is_valid_contained_nonleading_digit',[('n','int'),('x','int')],'bool',['math','digits','strings'],['Determine whether decimal n contains digit x at least once.','The leading digit of n must not equal x.','Return true only when both conditions hold.'],[([101,0],'Zero occurs inside 101 and is not its leading digit.'),([515,5],'Five occurs, but it is the leading digit, so return false.')],[[n,x] for n,x in [(101,0),(515,5),(123,2),(123,1),(9,9),(10,0),(10,1),(222,2),(9876,5),(1000,0),(456,6),(707,7),(808,0),(42,4)]],DIGIT,[DIGIT.replace("text[0]!=digit","text[0]==digit"),DIGIT.replace('digit in text and ','')],['Requires x to be the leading digit.','Checks only that the leading digit differs and ignores whether x occurs.'],digit_oracle,random_digit,['Convert n and x to decimal strings.','Use membership to establish at least one occurrence.','Compare x with the first character to reject a leading occurrence.','Logical AND enforces both requirements.'],'O(digits)','O(digits)',3),
}
