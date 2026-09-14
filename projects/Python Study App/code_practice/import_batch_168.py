"""ABC insertion, tree pricing, modular time, multiples, and sliding beauty batch 168."""

from collections import deque

from .import_batch_055 import entry


def additions_oracle(args):
    word=args[0]
    for repeats in range(1,len(word)+2):
        target='abc'*repeats;index=0
        for char in target:
            if index<len(word) and word[index]==char:index+=1
        if index==len(word):return len(target)-len(word)


def random_additions(rng):return [''.join(rng.choice('abc') for _ in range(rng.randint(1,30)))]


def price_oracle(args):
    n,edges,price,trips=args;graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    used=[0]*n
    for start,end in trips:
        parent={start:-1};queue=deque([start])
        while queue:
            node=queue.popleft()
            if node==end:break
            for neighbor in graph[node]:
                if neighbor not in parent:parent[neighbor]=node;queue.append(neighbor)
        node=end
        while node!=-1:used[node]+=1;node=parent[node]
    best=10**30
    for mask in range(1<<n):
        if any(mask>>a&1 and mask>>b&1 for a,b in edges):continue
        best=min(best,sum(used[i]*(price[i]//2 if mask>>i&1 else price[i]) for i in range(n)))
    return best


def random_price(rng):
    n=rng.randint(1,9);edges=[[node,rng.randrange(node)] for node in range(1,n)]
    trips=[[rng.randrange(n),rng.randrange(n)] for _ in range(rng.randint(1,8))]
    return [n,edges,[2*rng.randint(1,15) for _ in range(n)],trips]


def arrival_oracle(args):
    arrival,delay=args
    for _ in range(delay):arrival=0 if arrival==23 else arrival+1
    return arrival


def random_arrival(rng):return [rng.randint(0,23),rng.randint(1,24)]


def multiples_oracle(args):return sum(value for value in range(1,args[0]+1) if any(value%factor==0 for factor in (3,5,7)))
def random_multiples(rng):return [rng.randint(1,1000)]


def beauty_oracle(args):
    nums,k,x=args;answer=[]
    for start in range(len(nums)-k+1):
        negative=sorted(value for value in nums[start:start+k] if value<0)
        answer.append(negative[x-1] if len(negative)>=x else 0)
    return answer


def random_beauty(rng):
    n=rng.randint(1,30);k=rng.randint(1,n)
    return [[rng.randint(-50,50) for _ in range(n)],k,rng.randint(1,k)]


ADDITIONS="""\
def minimum_abc_insertions(word):
    additions=0;expected=0
    for char in word:
        position=ord(char)-ord('a')
        additions+=(position-expected)%3;expected=(position+1)%3
    return additions+(3-expected)%3
"""

PRICE="""\
def minimum_tree_trip_price(n,edges,price,trips):
    graph=[[] for _ in range(n)]
    for left,right in edges:graph[left].append(right);graph[right].append(left)
    visits=[0]*n
    def mark(node,parent,target):
        if node==target:visits[node]+=1;return True
        for neighbor in graph[node]:
            if neighbor!=parent and mark(neighbor,node,target):visits[node]+=1;return True
        return False
    for start,end in trips:mark(start,-1,end)
    def solve(node,parent):
        full=visits[node]*price[node];half=visits[node]*(price[node]//2)
        for neighbor in graph[node]:
            if neighbor==parent:continue
            child_full,child_half=solve(neighbor,node)
            full+=min(child_full,child_half);half+=child_full
        return full,half
    return min(solve(0,-1))
"""

ARRIVAL="""\
def delayed_arrival_hour(arrivalTime,delayedTime):
    return (arrivalTime+delayedTime)%24
"""

MULTIPLES="""\
def sum_three_five_seven_multiples(n):
    def total(factor):
        count=n//factor
        return factor*count*(count+1)//2
    return total(3)+total(5)+total(7)-total(15)-total(21)-total(35)+total(105)
"""

BEAUTY="""\
def sliding_negative_beauty(nums,k,x):
    counts=[0]*101
    for value in nums[:k]:counts[value+50]+=1
    def current():
        seen=0
        for value in range(-50,0):
            seen+=counts[value+50]
            if seen>=x:return value
        return 0
    answer=[current()]
    for index in range(k,len(nums)):
        counts[nums[index-k]+50]-=1;counts[nums[index]+50]+=1;answer.append(current())
    return answer
"""


BATCH={
2645:entry('minimum_abc_insertions',[('word','str')],'int',['strings','greedy'],
 ['A valid final string is one or more consecutive copies of abc.','You may insert only a, b, or c without deleting or reordering word.','Return the minimum number of inserted characters.'],
 [(['b'],'Insert a before b and c after it to obtain abc, requiring two insertions.'),(['aaa'],'Each original a must begin a separate abc block, requiring six insertions.')],
 [[s] for s in ['a','c','abc','ab','bc','ac','aaa','bbb','ccc','aab','abb','abca','cab','cba','abcabc']],
 ADDITIONS,[ADDITIONS.replace('(position-expected)%3','abs(position-expected)'),ADDITIONS.replace('(3-expected)%3','3-expected')],
 ['Uses absolute alphabet distance and mishandles wraparound between abc blocks.','Adds three trailing characters even when a complete block already ends at c.'],additions_oracle,random_additions,
 ['Track which character position is expected next in the repeating abc pattern.','Before each original character, insert the cyclic gap from expected to that character.','Advance expected to the character after the one retained, then fill the final partial block.','The order is fixed, so every skipped pattern position requires one insertion and greedily matching each original character as early as possible cannot hurt later matches.'],'O(n)','O(1)',5),
2646:entry('minimum_tree_trip_price',[('n','int'),('edges','list[list[int]]'),('price','list[int]'),('trips','list[list[int]]')],'int',['trees','graphs','dynamic programming','recursion'],
 ['edges describes a tree with even positive price per node.','Before all trips, you may halve prices at any set of pairwise nonadjacent nodes.','Each trip pays every node on its unique endpoint-inclusive path; return the minimum total across all trips.'],
 [([4,[[0,1],[1,2],[1,3]],[2,2,10,6],[[0,3],[2,1],[2,3]]],'Counting path visits and optimally halving nonadjacent nodes gives total price twenty-three.'),([2,[[0,1]],[2,2],[[0,0]]],'Only node zero is visited; halving its price yields cost one.')],
 [[n,e,p,t] for n,e,p,t in [
  (1,[],[2],[[0,0]]),(2,[[0,1]],[2,4],[[0,1]]),(3,[[0,1],[1,2]],[2,4,6],[[0,2]]),
  (3,[[0,1],[0,2]],[10,2,2],[[1,2]]),(4,[[0,1],[1,2],[2,3]],[2,2,2,2],[[0,3]]),
  (4,[[0,1],[0,2],[0,3]],[8,6,4,2],[[1,2],[2,3]]),(5,[[0,1],[1,2],[1,3],[3,4]],[2,4,6,8,10],[[0,4],[2,4]]),
  (5,[[0,1],[0,2],[2,3],[2,4]],[10,8,6,4,2],[[1,3],[4,1],[0,0]]),
  (6,[[0,1],[1,2],[2,3],[3,4],[4,5]],[2,4,6,8,10,12],[[0,5],[1,4]]),
  (6,[[0,1],[0,2],[1,3],[1,4],[2,5]],[12,10,8,6,4,2],[[3,5],[4,5],[0,2]]),
  (3,[[0,1],[1,2]],[100,2,100],[[0,2],[0,2]]),(4,[[0,1],[1,2],[1,3]],[4,8,12,16],[[2,2],[3,3]]),
  (7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[2,4,6,8,10,12,14],[[3,6],[4,5],[0,6]]),
  (5,[[0,1],[1,2],[2,3],[3,4]],[20,18,16,14,12],[[0,4],[0,4],[2,2]])]],
 PRICE,[PRICE.replace('half+=child_full','half+=min(child_full,child_half)'),PRICE.replace('price[node]//2','price[node]')],
 ['Allows adjacent parent and child nodes to both use halved prices.','Never actually halves a selected node price.'],price_oracle,random_price,
 ['First count how often each node appears across the unique trip paths.','Tree DP returns two costs per subtree: current node full-price or halved.','A full-price node allows either child state; a halved node forces every child to full price.','The two states enumerate every independent set of halved nodes, and visit counts make each state cost equal to all trip payments.'],'O(trips*n+n)','O(n)',8),
2651:entry('delayed_arrival_hour',[('arrivalTime','int'),('delayedTime','int')],'int',['math'],
 ['arrivalTime is an hour from 0 through 23.','Add the positive delay measured in whole hours.','Return the resulting hour in 24-hour clock format.'],
 [([15,5],'Five hours after 15:00 is 20:00.'),([23,2],'Two hours after 23:00 wraps past midnight to 01:00.')],
 [[a,d] for a,d in [(0,1),(0,24),(23,1),(23,24),(12,12),(5,20),(8,7),(18,10),(1,23),(22,3),(6,6),(15,9),(10,1),(3,24)]],
 ARRIVAL,[ARRIVAL.replace('%24','%23'),ARRIVAL.replace('arrivalTime+delayedTime','arrivalTime-delayedTime')],
 ['Wraps on a 23-hour cycle.','Subtracts the delay instead of adding it.'],arrival_oracle,random_arrival,
 ['Add the two hour counts.','Clock hours repeat every twenty-four.','Take the sum modulo 24.','Modulo returns the unique equivalent hour in the required zero-through-23 range, including every midnight wrap.'],'O(1)','O(1)',3),
2652:entry('sum_three_five_seven_multiples',[('n','int')],'int',['math','inclusion-exclusion'],
 ['Consider every positive integer from one through n inclusive.','Select values divisible by 3, 5, or 7.','Return their sum, counting a value only once even if several divisors divide it.'],
 [([7],'The selected values are three, five, six, and seven, whose sum is twenty-one.'),([10],'Adding three, five, six, seven, nine, and ten gives forty.')],
 [[n] for n in [1,2,3,4,5,6,8,14,15,20,21,35,100,1000]],
 MULTIPLES,[MULTIPLES.replace('-total(15)-total(21)-total(35)','-total(15)-total(21)'),MULTIPLES.replace('+total(105)','-total(105)')],
 ['Fails to subtract values divisible by both five and seven.','Subtracts the triple intersection instead of restoring it.'],multiples_oracle,random_multiples,
 ['The sum of positive multiples of d through n is d times the triangular number through floor(n/d).','Add the sums for divisors three, five, and seven.','Subtract pairwise least-common-multiple sums and restore the triple intersection at 105.','Inclusion-exclusion gives every selected integer coefficient one regardless of how many base divisors divide it.'],'O(1)','O(1)',3),
2653:entry('sliding_negative_beauty',[('nums','list[int]'),('k','int'),('x','int')],'list[int]',['arrays','sliding windows','counting'],
 ['For each contiguous window of length k, sort only its negative values conceptually.','Its beauty is the xth smallest negative value, or zero when fewer than x negatives exist.','Return the beauty of every window from left to right.'],
 [([[1,-1,-3,-2,3],3,2],'The successive second-smallest negative values are -1, -2, and -2.'),([[-1,-2,-3,-4,-5],2,2],'Each two-value window contains two negatives, so its larger negative is returned.')],
 [[a,k,x] for a,k,x in [([1],1,1),([-1],1,1),([0],1,1),([1,2,3],2,1),([-1,2,-3],2,1),([-1,2,-3],3,2),([-5,-4,-3],3,3),([1,-1,1,-1],2,1),([-50,50,-49,49],2,1),([0,-1,-2,0],3,2),([5,4,3,2,1],5,1),([-1,-1,-1],2,2),([1,-2,-2,3,-1],3,2),([-5,0,-4,0,-3],3,1)]],
 BEAUTY,[BEAUTY.replace('range(-50,0)','range(-49,0)'),BEAUTY.replace('nums[index-k]','nums[index-k+1]')],
 ['Never considers negative fifty as a candidate beauty.','Removes the wrong outgoing position and corrupts later windows.'],beauty_oracle,random_beauty,
 ['Values lie in the small fixed range -50 through 50, so maintain a frequency array.','Initialize counts for the first length-k window.','Scan negative values in ascending order until cumulative frequency reaches x; slide by removing the outgoing value and adding the incoming value.','The frequency scan exactly simulates sorted negative order, and each update preserves counts for the current window.'],'O(n*50)','O(101)',5),
}
