"""Dominant tree nodes, future-valued series, even-product compositions, ratios, and discounts."""
from itertools import product,permutations
from .import_batch_055 import entry

def tree_oracle(a):
    values=a[0]
    def walk(i):
        if i>=len(values) or values[i] is None:return (float('-inf'),0)
        lm,lc=walk(2*i+1);rm,rc=walk(2*i+2);v=values[i];return max(v,lm,rm),lc+rc+(v>=lm and v>=rm)
    return walk(0)[1]
def random_tree(r):
    return [[r.randint(-20,20) for _ in range(r.randint(1,31))]]
def series_oracle(a):
    one,two=a;times=sorted({x for x,_ in one}|{x for x,_ in two});out=[]
    for t in times:
        first=next((v for x,v in one if x>=t),0);second=next((v for x,v in two if x>=t),0);out.append([t,first+second])
    return out
def random_series(r):
    times=sorted(r.sample(range(1,30),r.randint(1,8)));other=sorted(r.sample(range(1,30),r.randint(1,8)))
    return [[[t,r.randint(-10,20)] for t in times],[[t,r.randint(-10,20)] for t in other]]
def compositions(total,count,prefix=()):
    if count==1:return [prefix+(total,)]
    return sum((compositions(total-x,count-1,prefix+(x,)) for x in range(1,total-count+2)),[])
def sequences_oracle(a):
    n,k=a;return sum(any(x%2==0 for x in seq) for seq in compositions(n,k))%(10**9+7)
def random_sequences(r):
    n=r.randint(1,14);return [n,r.randint(1,n)]
def ratio_oracle(a):
    nums,p,q=a;answer=0
    for i in range(len(nums)):
        even=odd=0
        for x in nums[i:]:
            if x%2:odd+=1
            else:even+=1
            answer+=odd>0 and even*q<=odd*p
    return answer
def random_ratio(r):return [[r.randint(1,20) for _ in range(r.randint(1,15))],r.randint(1,8),r.randint(1,8)]
def discounts_oracle(a):
    prices,discounts=a;best=float('inf')
    padded=discounts+[0]*max(0,len(prices)-len(discounts))
    for order in set(permutations(padded,min(len(prices),len(padded)))):
        best=min(best,sum(price*(100-order[i])/100 for i,price in enumerate(prices)))
    return best
def random_discounts(r):return [[r.randint(1,100) for _ in range(r.randint(1,6))],[r.randint(1,90) for _ in range(r.randint(1,5))]]

DOMINANT='''def count_dominant_tree_nodes(root):
    answer=0
    def visit(node):
        nonlocal answer
        if node is None:return float('-inf')
        left=visit(node.left);right=visit(node.right)
        if node.val>=left and node.val>=right:answer+=1
        return max(node.val,left,right)
    visit(root);return answer
'''
SERIES='''def aggregate_future_time_series(series1,series2):
    i=j=0;answer=[]
    while i<len(series1) and j<len(series2):
        t1,v1=series1[i];t2,v2=series2[j]
        if t1==t2:answer.append([t1,v1+v2]);i+=1;j+=1
        elif t1<t2:answer.append([t1,v1+v2]);i+=1
        else:answer.append([t2,v1+v2]);j+=1
    answer.extend(series1[i:]);answer.extend(series2[j:]);return answer
'''
SEQUENCES='''def count_even_product_compositions(n,k):
    MOD=10**9+7
    def choose(total,take):
        if take<0 or take>total:return 0
        answer=1
        for i in range(1,take+1):answer=answer*(total-take+i)%MOD*pow(i,MOD-2,MOD)%MOD
        return answer
    all_sequences=choose(n-1,k-1)
    all_odd=choose((n+k)//2-1,k-1) if (n-k)%2==0 else 0
    return (all_sequences-all_odd)%MOD
'''
RATIO='''def count_bounded_even_odd_ratio_subarrays(nums,a,b):
    answer=0
    for left in range(len(nums)):
        even=odd=0
        for value in nums[left:]:
            if value%2:odd+=1
            else:even+=1
            if odd and even*b<=odd*a:answer+=1
    return answer
'''
DISCOUNTS='''def minimum_discounted_total(prices,discounts):
    prices=sorted(prices,reverse=True);discounts=sorted(discounts,reverse=True)
    return sum(price*(100-(discounts[i] if i<len(discounts) else 0))/100 for i,price in enumerate(prices))
'''

BATCH={
3997:entry('count_dominant_tree_nodes',[('root','TreeNode | None')],'int',['trees','recursion','postorder traversal'],['A node is dominant when its value equals the maximum value in its entire rooted subtree.','The binary tree is complete but values may repeat.','Return the number of dominant nodes.'],[([[5,3,8,2,4,7,1]],'Leaves qualify, node eight dominates its children, and root five does not dominate eight, producing five.'),([[1]],'A leaf is the maximum of its one-node subtree.')],[[t] for t in [[1],[5,3,8,2,4,7,1],[1,2,3],[3,2,1],[5,5,5],[0,-1,-2],[10,5,15,1,7,12,20],[2,3,1,4,0],[7,3,9,1,5,8,10],[1,1,2,1,1,1,1],[9,8,7,6,5,4,3],[0,0,0],[-1,-2,-3],[4,2,6,1,3,5,7]]],DOMINANT,[DOMINANT.replace('node.val>=left and node.val>=right','node.val>left and node.val>right'),DOMINANT.replace('return max(node.val,left,right)','return node.val')],['Requires strict dominance and rejects nodes tied with a descendant maximum.','Returns only the child root value rather than the subtree maximum.'],tree_oracle,random_tree,['Postorder returns the maximum value in each child subtree.','Compare the current value with both returned maxima.','Count the node when it is at least both, then return the maximum of all three values.','Every subtree maximum is computed once and includes all descendants by induction.'],'O(n)','O(tree height)',5),
4001:entry('aggregate_future_time_series',[('series1','list[list[int]]'),('series2','list[list[int]]')],'list[list[int]]',['arrays','two pointers'],['Each series contains increasing [timestamp,value] pairs.','At a timestamp missing from one series, use that series’s next available value, or zero if none remains.','Return every timestamp from either series with the two applicable values summed.'],[([[[1,3],[4,1]],[[2,2],[5,2]]],'At times one, two, four, and five the future/current pairs sum to 5, 3, 3, and 2.'),([[[1,5]],[[1,7]]],'Matching timestamps combine directly to twelve.')],[[a,b] for a,b in [([[1,5]],[[1,7]]),([[1,3],[4,1]],[[2,2],[5,2]]),([[1,1]],[[2,2]]),([[2,2]],[[1,1]]),([[1,2],[3,4]],[[1,5],[3,6]]),([[1,1],[5,5]],[[2,2],[3,3]]),([[10,1]],[[1,2]]),([[1,-1]],[[1,1]]),([[1,3],[2,4]],[[3,5]]),([[3,5]],[[1,3],[2,4]]),([[1,1],[2,2],[3,3]],[[2,10]]),([[5,9]],[[5,1],[6,2]]),([[1,4],[9,8]],[[2,7],[8,3]]),([[1,0]],[[2,0]])]],SERIES,[SERIES.replace('v1+v2','v1',1),SERIES.replace('else:answer.append([t2,v1+v2])','else:answer.append([t2,v2])')],['Fails to add the second series at the first unmatched timestamp.','Fails to add the next first-series value when the second timestamp is smaller.'],series_oracle,random_series,['Keep pointers at the next unused value in each series.','At the smaller timestamp, pair its value with the other pointer’s next value.','Advance whichever timestamp was emitted; advance both on equality.','Once one series ends, the other values pair with zero and can be appended.'],'O(n+m)','O(n+m)',5),
4002:entry('count_even_product_compositions',[('n','int'),('k','int')],'int',['math','combinatorics'],['Count ordered sequences of k positive integers summing to n.','The product must be even, meaning at least one element is even.','Return the count modulo 1,000,000,007.'],[([5,3],'There are six positive compositions; three contain an even value.'),([4,2],'The sequences (1,3), (2,2), and (3,1) include only one even-product case: (2,2).')],[[n,k] for n,k in [(1,1),(2,1),(2,2),(3,1),(3,2),(4,2),(5,3),(6,2),(6,3),(7,4),(8,1),(8,4),(10,5),(20,6)]],SEQUENCES,[SEQUENCES.replace('all_sequences-all_odd','all_sequences+all_odd'),SEQUENCES.replace('(n-k)%2==0','(n-k)%2!=0')],['Adds all-odd compositions instead of subtracting them.','Uses the wrong parity condition for whether all-odd compositions exist.'],sequences_oracle,random_sequences,['Stars and bars counts all positive compositions as C(n-1,k-1).','An odd product occurs exactly when every term is odd.','Transform each odd term 2y+1 to count those compositions, then subtract.','The two classes partition all compositions, and modular combinations handle the large domain.'],'O(k log MOD)','O(1)',8),
4011:entry('count_bounded_even_odd_ratio_subarrays',[('nums','list[int]'),('a','int'),('b','int')],'int',['arrays','enumeration'],['For each nonempty subarray, count its even and odd elements.','It qualifies only with at least one odd and even/odd <= a/b.','Return the number of qualifying subarrays.'],[([[1,2,1,2],3,2],'Seven subarrays contain an odd and meet the ratio bound.'),([[2,4],1,1],'No subarray contains an odd value.')],[[n,a,b] for n,a,b in [([1],1,1),([2],1,1),([1,2,1,2],3,2),([2,4],1,1),([1,3],1,2),([2,1],1,1),([2,2,1],2,1),([1,2,2],1,2),([1,1,2,2],1,1),([3,4,5],2,3),([2,3,4,5],3,2),([1,2,3],1,3),([6,8,9],5,1),([1,1,1],1,1)]],RATIO,[RATIO.replace('even*b<=odd*a','even*b<odd*a'),RATIO.replace('if odd and even*b<=odd*a','if even*b<=max(1,odd)*a')],['Uses a strict ratio and rejects equality.','Treats a zero odd count as one and admits all-even subarrays.'],ratio_oracle,random_ratio,['Fix a left boundary and extend right while maintaining parity counts.','Avoid floating point by cross-multiplying even*b <= odd*a.','Require odd to be positive before counting.','Every subarray is evaluated once with exact integer arithmetic.'],'O(n^2)','O(1)',5),
4014:entry('minimum_discounted_total',[('prices','list[int]'),('discounts','list[int]')],'float',['greedy','sorting'],['Apply each percentage discount to at most one item and at most one discount per item.','Unused discounts and undiscounted items are allowed.','Return the minimum unrounded total price.'],[([[10,30,21],[50,60]],'Pair sixty percent with thirty and fifty percent with twenty-one, leaving ten, for total 32.5.'),([[10],[20,50]],'Use the larger fifty-percent discount on the only item, paying five.')],[[p,d] for p,d in [([10],[50]),([10],[20,50]),([10,30,21],[50,60]),([1,2],[10]),([100,50],[0]),([5,5],[50,50]),([10,20,30],[]),([9,1],[90]),([3,7],[25,75]),([100],[100]),([20,40,60],[10,20]),([1,100],[1,99]),([8,16,32],[50]),([11,22],[33,66,99])]],DISCOUNTS,[DISCOUNTS.replace('sorted(prices,reverse=True)','sorted(prices)'),DISCOUNTS.replace('sorted(discounts,reverse=True)','sorted(discounts)')],['Pairs the largest discount with the smallest price.','Uses the smallest discounts first.'],discounts_oracle,random_discounts,['A discount saves price*percentage/100.','Maximize savings by sorting both prices and discounts descending and pairing corresponding positions.','Leave excess prices undiscounted and excess discounts unused.','The rearrangement inequality proves like-ranked pairing maximizes total savings.'],'O(n log n+m log m)','O(n+m)',5),
}
BATCH[3997]['params'][0]=('root','TreeNode | None','treenode')
