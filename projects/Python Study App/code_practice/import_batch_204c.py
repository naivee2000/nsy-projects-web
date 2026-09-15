"""Coin probability, fair partitioning, balanced windows, unique subsets, and tree diameter."""
from collections import Counter
from itertools import combinations,product
from .import_batch_055 import entry

def coins_o(a):
    probabilities,target=a;answer=0.0
    for outcomes in product((0,1),repeat=len(probabilities)):
        if sum(outcomes)!=target:continue
        chance=1.0
        for outcome,p in zip(outcomes,probabilities):chance*=p if outcome else 1-p
        answer+=chance
    return answer
def rcoins(r):
    n=r.randint(1,9);return [[r.randint(0,10)/10 for _ in range(n)],r.randint(0,n)]

def chocolate_o(a):
    values,k=a;n=len(values);best=0
    for cuts in combinations(range(1,n),k):
        ends=(0,)+cuts+(n,);best=max(best,min(sum(values[ends[i]:ends[i+1]]) for i in range(k+1)))
    return best
def rchocolate(r):
    n=r.randint(2,10);return [[r.randint(1,15) for _ in range(n)],r.randint(0,n-1)]

def balanced_o(a):
    text=a[0];need=len(text)//4;best=len(text)
    for left in range(len(text)+1):
        for right in range(left,len(text)+1):
            outside=Counter(text[:left]+text[right:])
            if all(outside[c]<=need for c in 'QWER'):best=min(best,right-left)
    return best
def rbalanced(r):
    n=4*r.randint(1,8);return [''.join(r.choice('QWER') for _ in range(n))]

def unique_o(a):
    words=a[0];best=0
    for mask in range(1<<len(words)):
        text=''.join(words[i] for i in range(len(words)) if mask>>i&1)
        if len(set(text))==len(text):best=max(best,len(text))
    return best
def runique(r):return [[''.join(r.choice('abcdef') for _ in range(r.randint(1,5))) for _ in range(r.randint(1,10))]]

def diameter_o(a):
    edges=a[0];n=len(edges)+1;distance=[[n+1]*n for _ in range(n)]
    for i in range(n):distance[i][i]=0
    for x,y in edges:distance[x][y]=distance[y][x]=1
    for k in range(n):
        for i in range(n):
            for j in range(n):distance[i][j]=min(distance[i][j],distance[i][k]+distance[k][j])
    return max(max(row) for row in distance)
def rdiameter(r):
    n=r.randint(1,15);return [[[i,r.randrange(i)] for i in range(1,n)]]

COINS='''def exact_head_probability(prob,target):
    dp=[0.0]*(target+1);dp[0]=1.0
    for chance in prob:
        for heads in range(target,-1,-1):dp[heads]=dp[heads]*(1-chance)+(dp[heads-1]*chance if heads else 0)
    return dp[target]
'''
CHOCOLATE='''def maximize_minimum_sweetness(sweetness,k):
    pieces=k+1;left,right=1,sum(sweetness)//pieces
    while left<=right:
        middle=(left+right)//2;count=total=0
        for value in sweetness:
            total+=value
            if total>=middle:count+=1;total=0
        if count>=pieces:left=middle+1
        else:right=middle-1
    return right
'''
BALANCED='''def minimum_balanced_replacement(s):
    target=len(s)//4;outside=Counter(s);answer=len(s);left=0
    if all(outside[c]<=target for c in 'QWER'):return 0
    for right,char in enumerate(s):
        outside[char]-=1
        while left<=right and all(outside[c]<=target for c in 'QWER'):
            answer=min(answer,right-left+1);outside[s[left]]+=1;left+=1
    return answer
'''
UNIQUE='''def maximum_unique_concatenation(arr):
    masks=[]
    for word in arr:
        if len(set(word))<len(word):continue
        mask=0
        for char in word:mask|=1<<(ord(char)-97)
        masks.append(mask)
    possible={0};best=0
    for mask in masks:
        for used in list(possible):
            if not used&mask:possible.add(used|mask);best=max(best,(used|mask).bit_count())
    return best
'''
DIAMETER='''def tree_diameter(edges):
    if not edges:return 0
    graph={}
    for a,b in edges:graph.setdefault(a,[]).append(b);graph.setdefault(b,[]).append(a)
    def farthest(start):
        stack=[(start,-1,0)];best=(0,start)
        while stack:
            node,parent,distance=stack.pop();best=max(best,(distance,node))
            for nxt in graph[node]:
                if nxt!=parent:stack.append((nxt,node,distance+1))
        return best
    return farthest(farthest(edges[0][0])[1])[0]
'''

BATCH={
1230:entry('exact_head_probability',[('prob','list[float]'),('target','int')],'float',['dynamic programming','probability'],['Coins are independent and coin i lands heads with probability prob[i].','Return the probability that exactly target coins land heads.','An answer within 0.00001 is accepted.'],[([[0.4],1],'The single coin must land heads, so the probability is 0.4.'),([[0.5,0.5,0.5,0.5,0.5],0],'All five coins must be tails, giving one thirty-second.')],[[p,t] for p,t in [([0.4],1),([0.4],0),([0.5,0.5],1),([0.5]*5,0),([1.0],1),([0.0],0),([0.2,0.3],2),([0.2,0.3],1),([0.1,0.2,0.3],0),([0.1,0.2,0.3],3),([0.25,0.5,0.75],1),([0.9,0.1,0.8],2),([0.3,0.3,0.3,0.3],2),([0.0,1.0,0.5],2)]],COINS,[COINS.replace('(1-chance)','chance'),COINS.replace('dp[heads-1]*chance','dp[heads-1]*(1-chance)')],['Uses the head probability when the current coin must be tails.','Uses the tail probability when the current coin supplies the new head.'],coins_o,rcoins,['Track probabilities by exact head count after each processed coin.','A state keeps its head count on tails or gains one on heads.','Update counts downward so the previous row is not overwritten.','The last coin is uniquely heads or tails, making the two probability contributions disjoint and exhaustive.'],'O(coins*target)','O(target)',5),
1231:entry('maximize_minimum_sweetness',[('sweetness','list[int]'),('k','int')],'int',['binary search','greedy'],['Cut the positive array into k+1 nonempty contiguous pieces.','You keep the piece with the smallest total sweetness.','Maximize the sweetness you can guarantee for that smallest piece.'],[([[1,2,3,4,5,6,7,8,9],5],'Six pieces can each reach at least six, but not seven.'),([[5,6,7,8,9,1,2,3,4],8],'Nine pieces means every element stands alone, so the minimum is one.')],[[a,k] for a,k in [([1,2],0),([1,2],1),([1,2,3,4,5,6,7,8,9],5),([5,6,7,8,9,1,2,3,4],8),([1,1,1],1),([10,1,1,1],1),([2,3,5,7],2),([9,8,7],0),([4,4,4,4],3),([1,2,1,2,1],2),([100,1,1,1,1],1),([3,6,2,8,4],2),([5,5,1,5,5],1),([2,2,9,2,2],2)]],CHOCOLATE,[CHOCOLATE.replace('count>=pieces','count>pieces'),CHOCOLATE.replace('return right','return left')],['Requires one extra feasible piece during binary search.','Returns the first infeasible value instead of the greatest feasible value.'],chocolate_o,rchocolate,['Binary-search a candidate guaranteed sweetness.','Greedily cut a piece whenever its running sum first reaches the candidate.','The candidate is feasible when this creates at least k+1 pieces.','Positive values make earliest cuts maximize the remaining material, and feasibility is monotone.'],'O(n log(sum/n))','O(1)',8),
1234:entry('minimum_balanced_replacement',[('s','str')],'int',['strings','sliding window'],['s contains only Q, W, E, and R and its length is divisible by four.','Replace one contiguous substring with any same-length string.','Return the minimum replacement length that can make all four character counts equal.'],[(['QWER'],'The string is already balanced, so no replacement is needed.'),(['QQWE'],'Replacing one Q with R balances all four counts.')],[[s] for s in ['QWER','QQWE','QQQW','QQQQ','WQWRQQQW','QWQW','EEEE','RREQ','QWERQWER','QQWWEERR','QRQR','WWEEQQRR','QQQQWWWW','QEWQRRRR']],BALANCED,[BALANCED.replace('outside[char]-=1','outside[char]+=1'),BALANCED.replace('<=target','<target')],['Adds the window character to the outside counts instead of removing it.','Requires every outside count to be strictly below its allowed quota.'],balanced_o,rbalanced,['The replacement window must contain every occurrence exceeding the target count.','Maintain counts outside a sliding window.','Shrink while all four outside counts are at most length/4, recording the minimum window.','Any characters missing outside can be supplied inside, so the quota condition is necessary and sufficient.'],'O(n)','O(1)',5),
1239:entry('maximum_unique_concatenation',[('arr','list[str]')],'int',['backtracking','bitmasks'],['Choose a subsequence of strings and concatenate it in original order.','Every character in the result must be unique.','Return the maximum possible result length.'],[([['un','iq','ue']],'Choosing iq and ue gives four distinct characters.'),([['cha','r','act','ers']],'Concatenating cha, r, and ers gives six distinct characters.')],[[x] for x in [['a'],['aa'],['un','iq','ue'],['cha','r','act','ers'],['abcdefghijklmnopqrstuvwxyz'],['ab','cd','ef'],['ab','bc'],['aa','bb','cc'],['a','b','c','d'],['abc','def','gha'],['xy','z','xyz'],['a','abc','d','de','def'],['hello','world'],['qwert','asdf','zxcv']]],UNIQUE,[UNIQUE.replace('if len(set(word))<len(word):continue','if False:continue'),UNIQUE.replace('if not used&mask','if used&mask')],['Allows words that already repeat a character internally.','Combines only masks that conflict instead of disjoint masks.'],unique_o,runique,['Represent each internally unique word by a 26-bit mask.','Maintain masks reachable from processed words.','Combine a word only with masks sharing no set bit and maximize the bit count.','Disjoint masks correspond exactly to concatenations with globally unique characters.'],'O(2^words*words)','O(2^words)',5),
1245:entry('tree_diameter',[('edges','list[list[int]]')],'int',['trees','graphs'],['edges form an undirected tree labeled zero through n-1.','The diameter is the greatest number of edges on a simple path.','Return zero for the one-vertex tree represented by no edges.'],[([[[0,1],[0,2]]],'The path one-zero-two has two edges.'),([[[0,1],[1,2],[2,3],[1,4],[4,5]]],'A longest path from three through one and four to five has four edges.')],[[e] for e in [[],[[0,1]],[[0,1],[0,2]],[[0,1],[1,2]],[[0,1],[1,2],[2,3]],[[0,1],[0,2],[0,3]],[[0,1],[1,2],[2,3],[1,4],[4,5]],[[1,0],[2,0],[3,2]],[[0,1],[1,2],[1,3],[3,4]],[[0,1],[0,2],[2,3],[2,4]],[[0,1],[1,2],[2,3],[3,4],[4,5]],[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[[0,1],[1,2],[2,3],[3,4],[2,5]],[[0,1],[1,2],[1,3],[3,4],[4,5],[4,6]]]],DIAMETER,[DIAMETER.replace('return farthest(farthest(edges[0][0])[1])[0]','return farthest(edges[0][0])[0]'),DIAMETER.replace('distance+1','distance+2')],['Returns eccentricity from an arbitrary vertex after only one traversal.','Counts every tree edge as length two.'],diameter_o,rdiameter,['A farthest vertex from any start is an endpoint of some diameter.','Traverse once to find that endpoint, then again to find its farthest distance.','Return the second traversal’s distance.','In a tree, unique paths ensure the two-sweep endpoint property and exact edge distances.'],'O(n)','O(n)',5),
}
BATCH[1230]['comparator']='float'
