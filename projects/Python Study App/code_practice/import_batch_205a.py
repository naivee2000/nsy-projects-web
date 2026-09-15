"""Divisible subsets, prefix suggestions, bounded walks, zero subtrees, and palindrome partitions."""
from itertools import combinations,product
from .import_batch_055 import entry

def divisible_o(a):
    nums=a[0];best=0
    for mask in range(1<<len(nums)):
        total=sum(nums[i] for i in range(len(nums)) if mask>>i&1)
        if total%3==0:best=max(best,total)
    return best
def rdivisible(r):return [[r.randint(1,20) for _ in range(r.randint(1,11))]]

def suggest_o(a):
    products,word=a;ordered=sorted(products);return [[item for item in ordered if item.startswith(word[:length])][:3] for length in range(1,len(word)+1)]
def rsuggest(r):
    products=set()
    while len(products)<r.randint(1,15):products.add(''.join(r.choice('abcde') for _ in range(r.randint(1,7))))
    return [list(products),''.join(r.choice('abcde') for _ in range(r.randint(1,6)))]

def stay_o(a):
    steps,length=a
    if steps<=9:return sum(sum(moves)==0 and all(0<=sum(moves[:i])<length for i in range(1,steps+1)) for moves in product((-1,0,1),repeat=steps))%(10**9+7)
    states={0:1}
    for _ in range(steps):
        nxt={}
        for place,count in states.items():
            for target in (place-1,place,place+1):
                if 0<=target<length:nxt[target]=nxt.get(target,0)+count
        states=nxt
    return states.get(0,0)%(10**9+7)
def rstay(r):return [r.randint(1,8),r.randint(1,7)]

def delete_o(a):
    nodes,parent,value=a;children=[[] for _ in range(nodes)]
    for i in range(1,nodes):children[parent[i]].append(i)
    def visit(node):
        total=value[node];count=1
        for child in children[node]:
            sub,c=visit(child);total+=sub;count+=c
        return (0,0) if total==0 else (total,count)
    return visit(0)[1]
def rdelete(r):
    n=r.randint(1,14);parent=[-1]+[r.randrange(i) for i in range(1,n)];return [n,parent,[r.randint(-5,5) for _ in range(n)]]

def partition_o(a):
    text,k=a;best=len(text)
    for cuts in combinations(range(1,len(text)),k-1):
        ends=(0,)+cuts+(len(text),);cost=0
        for i in range(k):
            piece=text[ends[i]:ends[i+1]];cost+=sum(piece[j]!=piece[-1-j] for j in range(len(piece)//2))
        best=min(best,cost)
    return best
def rpartition(r):
    text=''.join(r.choice('abcd') for _ in range(r.randint(1,10)));return [text,r.randint(1,len(text))]

DIVISIBLE='''def maximum_sum_divisible_by_three(nums):
    best=[0,float('-inf'),float('-inf')]
    for value in nums:
        previous=best[:]
        for remainder,total in enumerate(previous):best[(remainder+value)%3]=max(best[(remainder+value)%3],total+value)
    return best[0]
'''
SUGGEST='''def search_suggestions(products,searchWord):
    products=sorted(products);answer=[];left,right=0,len(products)
    for index,char in enumerate(searchWord):
        prefix=searchWord[:index+1]
        while left<right and not products[left].startswith(prefix):left+=1
        while right>left and not products[right-1].startswith(prefix):right-=1
        answer.append(products[left:min(left+3,right)])
    return answer
'''
STAY='''def ways_to_stay_at_zero(steps,arrLen):
    mod=10**9+7;width=min(arrLen,steps//2+1);dp=[0]*width;dp[0]=1
    for _ in range(steps):
        nxt=[0]*width
        for i,count in enumerate(dp):
            for j in (i-1,i,i+1):
                if 0<=j<width:nxt[j]=(nxt[j]+count)%mod
        dp=nxt
    return dp[0]
'''
DELETE='''def remaining_tree_nodes(nodes,parent,value):
    children=[[] for _ in range(nodes)]
    for node in range(1,nodes):children[parent[node]].append(node)
    def visit(node):
        total=value[node];count=1
        for child in children[node]:
            child_sum,child_count=visit(child);total+=child_sum;count+=child_count
        return (0,0) if total==0 else (total,count)
    return visit(0)[1]
'''
PARTITION='''def palindrome_partition_changes(s,k):
    n=len(s);cost=[[0]*n for _ in range(n)]
    for length in range(2,n+1):
        for left in range(n-length+1):
            right=left+length-1;cost[left][right]=(cost[left+1][right-1] if length>2 else 0)+(s[left]!=s[right])
    dp=[[n+1]*(k+1) for _ in range(n+1)];dp[0][0]=0
    for end in range(1,n+1):
        for pieces in range(1,min(k,end)+1):
            dp[end][pieces]=min(dp[start][pieces-1]+cost[start][end-1] for start in range(pieces-1,end))
    return dp[n][k]
'''

BATCH={
1262:entry('maximum_sum_divisible_by_three',[('nums','list[int]')],'int',['dynamic programming','arrays'],['Choose any subset of positive integers.','Return the greatest possible subset sum divisible by three.','The empty subset is allowed and has sum zero.'],[([[3,6,5,1,8]],'Choosing three, six, five, one, and eight except five gives eighteen.'),([[4]],'Four is not divisible by three, so the empty subset gives zero.')],[[x] for x in [[3],[4],[3,6,5,1,8],[8,1],[1,2,3,4,4],[2,2,2],[1,1],[5,5,5],[7,8,9],[1,4,7],[2,5,8],[10,20,30],[6,1,1],[9,2,2,2]]],DIVISIBLE,[DIVISIBLE.replace('previous=best[:]','previous=best'),DIVISIBLE.replace('return best[0]','return max(best)')],['Updates from the current row and can reuse one value multiple times.','Returns the greatest sum regardless of its remainder.'],divisible_o,rdivisible,['Track the best sum for each remainder modulo three.','For every value, transition from a snapshot of the three previous states.','Update the remainder of total plus value and return remainder zero.','Every subset either excludes or includes the current value exactly once, and only its remainder matters for future choices.'],'O(n)','O(1)',5),
1268:entry('search_suggestions',[('products','list[str]'),('searchWord','str')],'list[list[str]]',['strings','sorting','binary search'],['Products are distinct lowercase strings.','After each typed prefix, return at most three lexicographically smallest products beginning with it.','Return one suggestion list per character of searchWord.'],[([['mobile','mouse','moneypot','monitor','mousepad'],'mouse'],'Sorting and narrowing prefixes yields the requested lists for m, mo, mou, mous, and mouse.'),([['havana'],'havana'],'The sole product remains suggested for every prefix.')],[[p,w] for p,w in [(['a'],'a'),(['a'],'b'),(['mobile','mouse','moneypot','monitor','mousepad'],'mouse'),(['havana'],'havana'),(['bags','baggage','banner','box','cloths'],'bags'),(['abc','abd','abe','abf'],'ab'),(['z','za','zb'],'z'),(['car','cat','dog'],'ca'),(['apple','app'],'apple'),(['aa','ab','ac','ad'],'a'),(['test','team','tear'],'te'),(['x','xy','xyz'],'xy'),(['code','coder','coding'],'cod'),(['b','ba','baa','bab'],'baa')]],SUGGEST,[SUGGEST.replace('min(left+3,right)','min(left+2,right)'),SUGGEST.replace('products=sorted(products)','products=sorted(products,reverse=True)')],['Returns at most two suggestions rather than three.','Sorts products in reverse lexicographic order.'],suggest_o,rsuggest,['Sort the products once.','For each longer prefix, move the active left and right boundaries past products that no longer match.','Return the first three items in the remaining sorted range.','Matching products form a contiguous sorted interval, and prefixes only shrink that interval.'],'O(p log p+total characters)','O(p)',5),
1269:entry('ways_to_stay_at_zero',[('steps','int'),('arrLen','int')],'int',['dynamic programming'],['Start at index zero in an array of length arrLen.','Each step moves left, moves right, or stays, without leaving the array.','Return ways to be at index zero after exactly steps moves, modulo 1000000007.'],[([3,2],'There are four valid three-step sequences returning to zero.'),([2,4],'Stay-stay and right-left are the two returning sequences.')],[[*x] for x in [(1,1),(1,2),(2,1),(2,4),(3,2),(4,2),(5,3),(6,4),(7,2),(8,5),(10,1),(12,3),(15,8),(20,4)]],STAY,[STAY.replace('steps//2+1','steps//2'),STAY.replace('return dp[0]','return sum(dp)')],['Allocates too few reachable positions for short walks.','Counts paths ending anywhere instead of only at zero.'],stay_o,rstay,['Only positions through steps/2 can participate in a path returning to zero.','Track counts at reachable positions and transition left, stay, and right each step.','Apply array bounds and the modulus.','The position after the final step partitions all paths; returning paths are exactly state zero.'],'O(steps*min(arrLen,steps))','O(min(arrLen,steps))',8),
1273:entry('remaining_tree_nodes',[('nodes','int'),('parent','list[int]'),('value','list[int]')],'int',['trees','recursion'],['parent describes a rooted tree with root zero and parent[0] equal to -1.','Delete every subtree whose node-value sum is zero, including all its descendants.','Return the number of nodes remaining.'],[([7,[-1,0,0,1,2,2,2],[1,-2,4,0,-2,-1,-1]],'The zero-sum subtree rooted at node two removes four nodes, leaving three.'),([7,[-1,0,0,1,2,2,2],[1,-2,4,0,-2,-1,-2]],'No complete subtree sums to zero, so all seven remain.')],[[n,p,v] for n,p,v in [(1,[-1],[0]),(1,[-1],[5]),(2,[-1,0],[1,-1]),(2,[-1,0],[1,1]),(7,[-1,0,0,1,2,2,2],[1,-2,4,0,-2,-1,-1]),(7,[-1,0,0,1,2,2,2],[1,-2,4,0,-2,-1,-2]),(3,[-1,0,0],[0,1,-1]),(4,[-1,0,1,1],[1,-1,2,-2]),(5,[-1,0,0,2,2],[2,1,-2,1,1]),(3,[-1,0,1],[1,2,-2]),(6,[-1,0,0,1,1,2],[3,-3,1,1,1,-1]),(4,[-1,0,0,0],[1,0,0,0]),(5,[-1,0,1,2,3],[1,-1,1,-1,0]),(6,[-1,0,0,2,2,4],[2,-1,-1,1,-1,0])]],DELETE,[DELETE.replace('(0,0) if total==0','(total,count) if total==0'),DELETE.replace('count+=child_count','count+=1')],['Keeps zero-sum subtrees instead of deleting them.','Counts one per child subtree instead of all surviving descendants.'],delete_o,rdelete,['Build child lists from the parent array.','Postorder returns each subtree’s sum and surviving node count.','If the completed sum is zero, return zero surviving nodes to the parent.','Every descendant is included before the deletion decision, so a deleted root removes its entire subtree.'],'O(nodes)','O(nodes)',5),
1278:entry('palindrome_partition_changes',[('s','str'),('k','int')],'int',['strings','dynamic programming'],['Split s into exactly k nonempty contiguous substrings.','You may change individual characters; minimize changes needed to make every piece a palindrome.','One changed position costs one.'],[(['abc',2],'Split a and bc, then change one character in bc.'),(['aabbc',3],'Split aa, bb, and c; no changes are needed.')],[[*x] for x in [('a',1),('abc',2),('aabbc',3),('leetcode',8),('abc',1),('abcd',2),('aaaa',2),('abca',1),('abcba',2),('abcdef',3),('aab',2),('banana',2),('racecar',3),('coding',4)]],PARTITION,[PARTITION.replace('(s[left]!=s[right])','0'),PARTITION.replace('range(pieces-1,end)','range(pieces,end)')],['Treats mismatched mirrored characters as free.','Forbids the earliest legal start position for every final piece.'],partition_o,rpartition,['Precompute the mismatch cost to turn every substring into a palindrome.','Then partition prefixes: choose the start of the final piece and add its precomputed cost.','Fill by increasing prefix length and piece count.','Every exact-k partition has one final cut, so minimizing over all such cuts is exhaustive.'],'O(n^2*k)','O(n*k+n^2)',8),
}

# Keep known-wrong fixtures executable so validation proves a logical mismatch,
# rather than accepting an incidental exception as evidence of rejection.
BATCH[1269]['wrong'][0] = STAY.replace('dp[0]=1', 'dp[0]=0')
BATCH[1269]['wrong_reasons'][0] = 'Initializes the starting position with zero paths.'
BATCH[1278]['wrong'][1] = PARTITION.replace('return dp[n][k]', 'return dp[n][k]+1')
BATCH[1278]['wrong_reasons'][1] = 'Adds one to every computed optimum.'
