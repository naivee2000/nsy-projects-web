"""Ordered sets, interval DP, monotonic ranges, trees, and functional graphs."""
from bisect import bisect_left, insort
from functools import lru_cache
from itertools import combinations
from math import isqrt
from .import_batch_055 import entry

def difference_oracle(args):
    nums,x=args
    return min(abs(nums[i]-nums[j]) for i in range(len(nums)) for j in range(i+1,len(nums)) if j-i>=x)
def random_difference(rng):
    nums=[rng.randint(-50,50) for _ in range(rng.randint(2,25))];return [nums,rng.randint(1,len(nums)-1)]

def groups_oracle(args):
    nums=args[0];best=len(nums)
    for one in range(len(nums)+1):
        for two in range(one,len(nums)+1):
            target=[1]*one+[2]*(two-one)+[3]*(len(nums)-two)
            best=min(best,sum(a!=b for a,b in zip(nums,target)))
    return best
def random_three_groups(rng):return [[rng.randint(1,3) for _ in range(rng.randint(1,25))]]

def offers_oracle(args):
    _,offers=args;best=0
    for mask in range(1<<len(offers)):
        chosen=[offers[i] for i in range(len(offers)) if mask>>i&1]
        if all(a[1]<b[0] or b[1]<a[0] for a,b in combinations(chosen,2)):
            best=max(best,sum(offer[2] for offer in chosen))
    return best
def random_offers(rng):
    n=rng.randint(1,10);offers=[]
    for _ in range(rng.randint(1,10)):
        left=rng.randrange(n);right=rng.randint(left,n-1);offers.append([left,right,rng.randint(1,20)])
    return [n,offers]

def ranges_oracle(args):
    nums=args[0];answer=[]
    for index,value in enumerate(nums):
        left=index
        while left and nums[left-1]<value:left-=1
        right=index
        while right+1<len(nums) and nums[right+1]<value:right+=1
        answer.append(right-left+1)
    return answer
def random_ranges(rng):
    n=rng.randint(1,30);return [rng.sample(range(-100,101),n)]

def ball_oracle(args):
    receiver,k=args;best=0
    for start in range(len(receiver)):
        node=start;score=start
        for _ in range(k):node=receiver[node];score+=node
        best=max(best,score)
    return best
def random_ball(rng):
    n=rng.randint(1,15);return [[rng.randrange(n) for _ in range(n)],rng.randint(1,30)]

def heroes_oracle(args):
    heroes,monsters,coins=args
    return [sum(coin for monster,coin in zip(monsters,coins) if monster<=hero) for hero in heroes]
def random_heroes(rng):
    monsters=[rng.randint(1,30) for _ in range(rng.randint(1,25))]
    return [[rng.randint(1,30) for _ in range(rng.randint(1,20))],monsters,[rng.randint(1,50) for _ in monsters]]

def square(value):return isqrt(value)**2==value
def complete_oracle(args):
    nums=args[0];best=0;n=len(nums)
    for mask in range(1,1<<n):
        indices=[i+1 for i in range(n) if mask>>i&1]
        if all(square(a*b) for a,b in combinations(indices,2)):
            best=max(best,sum(nums[i-1] for i in indices))
    return best
def random_complete(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,10))]]

def components_oracle(args):
    n,edges,values,k=args;best=0
    for cut in range(1<<len(edges)):
        parent=list(range(n))
        def find(x):
            while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
            return x
        for i,(a,b) in enumerate(edges):
            if not cut>>i&1:
                a,b=find(a),find(b);parent[a]=b
        sums={}
        for node,value in enumerate(values):root=find(node);sums[root]=sums.get(root,0)+value
        if all(total%k==0 for total in sums.values()):best=max(best,len(sums))
    return best
def random_components(rng):
    n=rng.randint(1,9);edges=[[i,rng.randrange(i)] for i in range(1,n)];k=rng.randint(1,8)
    values=[rng.randint(1,20) for _ in range(n-1)];values.append((-sum(values))%k or k)
    return [n,edges,values,k]

def visited_oracle(args):
    edges=args[0];answer=[]
    for start in range(len(edges)):
        seen=set();node=start
        while node not in seen:seen.add(node);node=edges[node]
        answer.append(len(seen))
    return answer
def random_visited(rng):
    n=rng.randint(1,35);return [[rng.randrange(n) for _ in range(n)]]

def operations_oracle(args):
    first,second,x=args;n=len(first);start=sum((a!=b)<<i for i,(a,b) in enumerate(zip(first,second)))
    if start.bit_count()%2:return -1
    distance={start:0};pending=[(0,start)]
    import heapq
    while pending:
        cost,mask=heapq.heappop(pending)
        if cost!=distance[mask]:continue
        if mask==0:return cost
        for i in range(n-1):
            nxt=mask^(1<<i)^(1<<(i+1));new=cost+1
            if new<distance.get(nxt,10**9):distance[nxt]=new;heapq.heappush(pending,(new,nxt))
        for i in range(n):
            for j in range(i+1,n):
                nxt=mask^(1<<i)^(1<<j);new=cost+x
                if new<distance.get(nxt,10**9):distance[nxt]=new;heapq.heappush(pending,(new,nxt))
def random_operations(rng):
    n=rng.randint(2,8);return [''.join(rng.choice('01') for _ in range(n)),''.join(rng.choice('01') for _ in range(n)),rng.randint(1,8)]

DIFF='''def constrained_minimum_difference(nums,x):
    ordered=[];answer=float('inf')
    for index in range(x,len(nums)):
        insort(ordered,nums[index-x]);place=bisect_left(ordered,nums[index])
        if place<len(ordered):answer=min(answer,ordered[place]-nums[index])
        if place:answer=min(answer,nums[index]-ordered[place-1])
    return answer
'''
GROUPS='''def minimum_three_group_changes(nums):
    costs=[0,0,0]
    for value in nums:
        costs=[costs[0]+(value!=1),min(costs[:2])+(value!=2),min(costs)+(value!=3)]
    return min(costs)
'''
OFFERS='''def maximum_house_offer_profit(n,offers):
    ending=[[] for _ in range(n)]
    for start,end,gold in offers:ending[end].append((start,gold))
    best=[0]*(n+1)
    for house in range(n):
        best[house+1]=best[house]
        for start,gold in ending[house]:best[house+1]=max(best[house+1],best[start]+gold)
    return best[n]
'''
RANGES='''def maximum_element_ranges(nums):
    n=len(nums);left=[-1]*n;right=[n]*n;stack=[]
    for i,value in enumerate(nums):
        while stack and nums[stack[-1]]<value:stack.pop()
        if stack:left[i]=stack[-1]
        stack.append(i)
    stack=[]
    for i in range(n-1,-1,-1):
        while stack and nums[stack[-1]]<nums[i]:stack.pop()
        if stack:right[i]=stack[-1]
        stack.append(i)
    return [b-a-1 for a,b in zip(left,right)]
'''
BALL='''def maximum_ball_passing_value(receiver,k):
    levels=k.bit_length();n=len(receiver);jump=[receiver[:]];score=[[i for i in range(n)]]
    for _ in range(1,levels):
        previous=jump[-1];jump.append([previous[previous[i]] for i in range(n)])
        old=score[-1];score.append([old[i]+old[previous[i]] for i in range(n)])
    answer=0
    for start in range(n):
        node=start;total=0
        for bit in range(levels):
            if k>>bit&1:total+=score[bit][node];node=jump[bit][node]
        answer=max(answer,total+node)
    return answer
'''
HEROES='''def maximum_hero_coins(heroes,monsters,coins):
    from bisect import bisect_right
    pairs=sorted(zip(monsters,coins));powers=[];prefix=[0]
    for power,coin in pairs:powers.append(power);prefix.append(prefix[-1]+coin)
    return [prefix[bisect_right(powers,hero)] for hero in heroes]
'''
COMPLETE='''def maximum_complete_index_sum(nums):
    groups={}
    for index,value in enumerate(nums,1):
        key=index;factor=2
        while factor*factor<=key:
            while key%(factor*factor)==0:key//=factor*factor
            factor+=1
        groups[key]=groups.get(key,0)+value
    return max(groups.values())
'''
COMPONENTS='''def maximum_divisible_tree_components(n,edges,values,k):
    graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    answer=0
    def visit(node,parent):
        nonlocal answer
        total=values[node]
        for child in graph[node]:
            if child!=parent:total+=visit(child,node)
        if total%k==0:answer+=1
        return total
    visit(0,-1);return answer
'''
VISITED='''def count_functional_graph_visits(edges):
    n=len(edges);answer=[0]*n;state=[0]*n
    for start in range(n):
        if answer[start]:continue
        path=[];position={};node=start
        while not answer[node] and node not in position:position[node]=len(path);path.append(node);node=edges[node]
        if answer[node]:base=answer[node]
        else:
            cycle_start=position[node];cycle=len(path)-cycle_start
            for item in path[cycle_start:]:answer[item]=cycle
            path=path[:cycle_start];base=cycle
        for item in reversed(path):base+=1;answer[item]=base
    return answer
'''
OPERATIONS='''def minimum_binary_transform_cost(s1,s2,x):
    positions=[i for i,(a,b) in enumerate(zip(s1,s2)) if a!=b]
    if len(positions)%2:return -1
    @lru_cache(None)
    def solve(left,right):
        if left>right:return 0
        return min(x+solve(left+1,right-1),positions[left+1]-positions[left]+solve(left+2,right),positions[right]-positions[right-1]+solve(left,right-2))
    return solve(0,len(positions)-1)
'''

def lesson(a,b,c,d):return [a,b,c,d]
CASES={
2817:[[a,x] for a,x in [([4,3,2,4],2),([5,3,2,10,15],1),([1,2],1),([1,1],1),([1,9,2],2),([-5,0,5],1),([8,3,8,1],3),([10,20,30,40],2),([7,2,9,4,7],4),([0,-10,10,0],2),([6,5,4,3,2,1],3),([100,-100,50],2),([2,8,3,9,4],2),([1,100,2,99],3)]],
2826:[[x] for x in ([2,1,3,2,1],[1,3,2,1,3,3],[1],[2],[3],[1,2,3],[3,2,1],[1,1,2,2,3,3],[2,2,1,3],[3,3,2,2,1],[1,3,1,3],[2,1,2,3,1],[1,2,1,2,3],[3,1,2,3,2])],
2830:[[n,o] for n,o in [(5,[[0,0,1],[0,2,2],[1,3,2]]),(5,[[0,0,1],[0,2,10],[1,3,2]]),(1,[[0,0,5]]),(3,[[0,1,4],[2,2,3]]),(4,[[0,3,10],[0,0,3],[1,2,5]]),(5,[[0,1,2],[2,4,4],[1,3,10]]),(2,[[0,0,1],[1,1,1]]),(4,[[1,1,7],[1,2,8]]),(6,[[0,2,5],[3,5,6],[1,4,20]]),(3,[[0,0,5],[0,0,7]]),(5,[[4,4,9],[0,3,8]]),(7,[[0,1,3],[2,3,4],[4,6,5]]),(4,[[0,2,6],[3,3,6],[1,1,5]]),(5,[[0,4,1],[1,1,10],[2,2,10]])]],
2832:[[x] for x in ([1,5,4,3,6],[1,2,3,4,5],[5,4,3,2,1],[1],[2,1],[1,2],[3,1,2],[2,3,1],[4,1,3,2],[10,5,8,1,7],[0,-1,-2,3],[8,2,6,4,10],[3,7,1,5,2],[9,1,8,2,7])],
2836:[[r,k] for r,k in [([2,0,1],4),([1,1,1,2,3],3),([0],1),([0],10),([1,0],1),([1,0],2),([0,0,1],5),([2,2,2],4),([1,2,3,0],7),([4,0,1,2,3],6),([1,2,0],20),([3,3,3,3],2),([2,3,1,0],9),([5,0,1,2,3,4],12)]],
2838:[[h,m,c] for h,m,c in [([1,4,2],[1,1,5,2,3],[2,3,4,5,6]),([5],[1,2,3],[10,20,30]),([1],[2],[5]),([3,1],[1,3],[4,7]),([10,0],[5,10],[2,8]),([2,2],[2,2],[3,4]),([4,8],[1,5,7],[2,4,6]),([6],[6,7,1],[10,20,30]),([1,2,3],[3,2,1],[1,10,100]),([100],[20,30],[7,9]),([5,3,9],[4,8,2],[5,6,7]),([2],[1,1,1],[2,2,2]),([7,1],[7,1],[9,8]),([3,6,9],[2,5,8],[10,20,30])]],
2862:[[x] for x in ([8,7,3,5,7,2,4,9],[5,10,3,10,1,13,7,9,4],[1],[1,2],[1,2,3,4],[4,3,2,1],[10,1,1,10],[2,4,6,8,10],[9,8,7,6,5,4,3,2,1],[1,10,1,10,1],[5,5,5,5,5,5],[3,1,4,1,5,9,2],[20,1,20,1,20,1,20,1],[7,6,5,4,3,2,1,9,8])],
2872:[[n,e,v,k] for n,e,v,k in [(5,[[0,2],[1,2],[1,3],[2,4]],[1,8,1,4,4],6),(7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[3,0,6,1,5,2,1],3),(1,[],[6],3),(2,[[0,1]],[2,4],3),(3,[[0,1],[1,2]],[1,2,3],3),(3,[[0,1],[0,2]],[2,2,2],2),(4,[[0,1],[1,2],[2,3]],[1,1,1,1],4),(4,[[0,1],[0,2],[0,3]],[3,3,3,3],3),(5,[[0,1],[1,2],[2,3],[3,4]],[2,4,6,8,10],5),(5,[[0,1],[0,2],[2,3],[2,4]],[5,1,2,3,4],5),(6,[[0,1],[0,2],[1,3],[1,4],[4,5]],[1,2,3,4,5,3],3),(3,[[0,1],[0,2]],[7,7,7],7),(2,[[0,1]],[5,5],5),(5,[[0,1],[1,2],[1,3],[3,4]],[6,1,2,3,6],3)]],
2876:[[x] for x in ([1,2,0,0],[1,2,3,4,0],[0],[0,0],[1,0],[1,1],[2,2,2],[1,2,3,3],[2,0,1,2],[4,0,1,2,3],[1,2,0,4,3],[3,3,3,3],[1,0,3,2],[2,3,4,0,1])],
2896:[[a,b,x] for a,b,x in [('1100011000','0101001010',2),('10110','00011',4),('00','00',3),('01','10',5),('0','1',2),('0000','1111',3),('0101','1010',1),('1001','0110',10),('111000','000111',2),('101','001',7),('1100','1001',3),('000000','101101',4),('01010101','10101010',2),('1111','0000',10)]],
}

BATCH={
2817:entry('constrained_minimum_difference',[('nums','list[int]'),('x','int')],'int',['arrays','ordered sets','binary search'],['Choose two indices whose distance is at least x.','Return the minimum absolute difference between their values.'],[([CASES[2817][0][0],CASES[2817][0][1]],'Indices zero and three both contain four and are at least two apart, so the answer is zero.'),([CASES[2817][1][0],CASES[2817][1][1]],'The closest values at distinct eligible indices differ by one.')],CASES[2817][2:],DIFF,[DIFF.replace('nums[index-x]','nums[index-x+1]'),DIFF.replace('if place:','if place>1:')],['Adds candidates one position too late and misses pairs exactly x apart.','Skips the immediate predecessor when it is the closest eligible value.'],difference_oracle,random_difference,lesson('When processing index i, only values at indices through i-x are eligible.','Maintain those values in sorted order and inspect the insertion neighbors of nums[i].','Insert nums[i-x], binary-search nums[i], and update from successor and predecessor.','In a sorted set the closest value must be adjacent to the insertion point, so two checks suffice.'),'O(n²) with a list; O(n log n) with a balanced ordered set','O(n)',5),
2826:entry('minimum_three_group_changes',[('nums','list[int]')],'int',['arrays','dynamic programming'],['Change any element to 1, 2, or 3.','Return the minimum changes needed to make nums nondecreasing.'],[([[2,1,3,2,1]],'Changing three positions can produce a nondecreasing grouping of ones, twos, then threes.'),([[1,3,2,1,3,3]],'Two middle changes suffice to restore nondecreasing order.')],CASES[2826][2:],GROUPS,[GROUPS.replace('min(costs[:2])','costs[1]'),GROUPS.replace('min(costs)','costs[2]')],['Forces state two to follow only state two and cannot transition from ones.','Forces state three to follow only threes and misses cheaper earlier groups.'],groups_oracle,random_three_groups,lesson('A nondecreasing prefix ending in value v may follow only states at most v.','Track minimum changes for prefixes ending in one, two, or three.','For each value, take the allowed prefix minimum plus whether changing the current element is necessary.','The three states exhaust the possible final group of every nondecreasing transformed prefix.'),'O(n)','O(1)',5),
2830:entry('maximum_house_offer_profit',[('n','int'),('offers','list[list[int]]')],'int',['arrays','dynamic programming','intervals'],['An accepted offer [start,end,gold] sells every inclusive house in that interval.','Choose nonoverlapping offers to maximize total gold.'],[([5,[[0,0,1],[0,2,2],[1,3,2]]],'Accepting the first and third offers sells disjoint houses for total three.'),([5,[[0,0,1],[0,2,10],[1,3,2]]],'The offer paying ten is better than either overlapping alternative.')],CASES[2830][2:],OFFERS,[OFFERS.replace('best[start]+gold','best[start+1]+gold'),OFFERS.replace('best[house]','0',1)],['Combines an offer with schedules that may already sell its starting house.','Drops the best profit carried from the preceding house.'],offers_oracle,random_offers,lesson('A schedule ending by house i either ignores i or accepts an offer ending there.','Group offers by end and store best profit for each house prefix.','Carry best[i], and for [start,i,gold] combine gold with best[start].','The prefix before start is exactly the largest nonoverlapping subproblem for that offer.'),'O(n+offers)','O(n+offers)',5),
2832:entry('maximum_element_ranges',[('nums','list[int]')],'list[int]',['arrays','monotonic stack'],['nums contains distinct integers.','For every index, return the longest contiguous range containing it in which its value is the maximum.'],[([[1,5,4,3,6]],'Value five controls indices zero through three while six controls the whole array, giving 1,4,2,1,5.'),([[1,2,3,4,5]],'Each value extends through every smaller value to its left.')],CASES[2832][2:],RANGES,[RANGES.replace('<value','>value',1),RANGES.replace('b-a-1','b-a')],['Pops smaller-boundary logic in the wrong direction on the left scan.','Has an off-by-one range length.'],ranges_oracle,random_ranges,lesson('A value can extend until the first greater value on either side.','Use decreasing stacks to find those two blocking indices.','Compute right blocker minus left blocker minus one.','Every interior value is smaller and each boundary is the nearest violation, making the range maximal.'),'O(n)','O(n)',5),
2836:entry('maximum_ball_passing_value',[('receiver','list[int]'),('k','int')],'int',['graphs','binary lifting','dynamic programming'],['Starting at node i, add i and the receiver reached after each of exactly k passes.','Return the maximum function value over all starting nodes.'],[([[2,0,1],4],'Starting at zero follows 0,2,1,0,2 for a total of six.'),([[1,1,1,2,3],3],'Trying every start through binary lifting gives the maximum total ten.')],CASES[2836][2:],BALL,[BALL.replace('total+node','total'),BALL.replace('score=[[i for i in range(n)]]','score=[[receiver[i] for i in range(n)]]')],['Omits the final reached node from each function value.','Stores receiver values instead of the starting nodes for jump-block sums.'],ball_oracle,random_ball,lesson('Powers of two let long pass counts be composed from logarithmically many jumps.','For every node and bit, store the destination and sum of starting nodes over that jump block.','Apply the set bits of k, accumulating block sums, then add the final node.','Binary decomposition covers exactly k edges without overlap, so each visited node is counted once.'),'O(n log k)','O(n log k)',8),
2838:entry('maximum_hero_coins',[('heroes','list[int]'),('monsters','list[int]'),('coins','list[int]')],'list[int]',['sorting','prefix sums','binary search'],['A hero defeats every monster whose power is at most the hero value and collects its coins.','Return total collectible coins independently for each hero in input order.'],[([[1,4,2],[1,1,5,2,3],[2,3,4,5,6]],'Heroes with powers one, four, and two collect totals five, sixteen, and ten.'),([[5],[1,2,3],[10,20,30]],'Power five defeats all three monsters and collects sixty coins.')],CASES[2838][2:],HEROES,[HEROES.replace('bisect_right','bisect_left'),HEROES.replace('prefix[-1]+coin','coin')],['Excludes monsters whose power exactly equals the hero power.','Stores individual coins rather than cumulative prefix totals.'],heroes_oracle,random_heroes,lesson('Sorting monsters converts each hero’s defeatable set into a prefix.','Sort power/coin pairs and build cumulative coin sums.','Use upper-bound search for each hero and read that prefix total.','Every monster before the boundary is defeatable and every later monster is too strong.'),'O((m+h) log m)','O(m)',5),
2862:entry('maximum_complete_index_sum',[('nums','list[int]')],'int',['arrays','number theory','hash maps'],['A nonempty subset of one-indexed positions is complete when every pairwise index product is a perfect square.','Return the maximum sum of nums values over complete subsets.'],[([[8,7,3,5,7,2,4,9]],'Indices sharing the same square-free kernel form candidate groups; the best group sums to sixteen.'),([[5,10,3,10,1,13,7,9,4]],'Grouping positions by square-free kernel gives the maximum valid element sum.')],CASES[2862][2:],COMPLETE,[COMPLETE.replace('factor*factor','factor',1),COMPLETE.replace('groups.get(key,0)+value','value')],['Removes single prime factors instead of square factors and merges incompatible indices.','Overwrites earlier values instead of summing each complete group.'],complete_oracle,random_complete,lesson('Two indices have square product exactly when their square-free kernels match.','Reduce every one-based index by removing all square factors and group nums by the remainder.','Accumulate each group and return its largest sum.','Equal kernels cancel every odd prime exponent in the product; unequal kernels leave at least one odd exponent.'),'O(n sqrt n)','O(n)',8),
2872:entry('maximum_divisible_tree_components',[('n','int'),('edges','list[list[int]]'),('values','list[int]'),('k','int')],'int',['trees','depth-first search','modular arithmetic'],['edges forms a tree and the total value sum is divisible by k.','Remove edges so every resulting component sum is divisible by k; maximize component count.'],[([5,[[0,2],[1,2],[1,3],[2,4]],[1,8,1,4,4],6],'Cutting one suitable edge produces two components whose sums are both divisible by six.'),([7,[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]],[3,0,6,1,5,2,1],3],'Postorder subtree sums identify the maximum divisible component cuts.')],CASES[2872][2:],COMPONENTS,[COMPONENTS.replace('total%k==0','total%k!=0'),COMPONENTS.replace('return total','return values[node]')],['Counts nondivisible subtrees instead of cuttable divisible ones.','Returns only each root value and discards child subtree sums.'],components_oracle,random_components,lesson('A subtree whose total is divisible by k can be detached without harming the remainder.','Compute subtree sums bottom-up and count every divisible sum.','DFS children, add their returned totals, count total modulo k equal to zero.','Because the whole sum is divisible, greedily cutting every divisible subtree yields valid remaining components and cannot reduce the optimum.'),'O(n)','O(n)',8),
2876:entry('count_functional_graph_visits',[('edges','list[int]')],'list[int]',['graphs','cycles','dynamic programming'],['Every node has exactly one outgoing edge edges[i].','For every start, return the number of distinct nodes visited before the first repeat.'],[([[1,2,0,0]],'Nodes zero through two lie on a three-cycle; node three reaches it after one extra visit.'),([[1,2,3,4,0]],'All five nodes form one cycle, so every answer is five.')],CASES[2876][2:],VISITED,[VISITED.replace('cycle=len(path)-cycle_start','cycle=len(path)-cycle_start-1'),VISITED.replace('base+=1','base+=2')],['Undercounts every newly discovered cycle by one.','Adds two rather than one for each tail node leading into a known path.'],visited_oracle,random_visited,lesson('Each walk consists of a tail followed by either a new cycle or a previously solved path.','Record positions in the current path to detect the cycle boundary.','Assign cycle length to cycle nodes, then walk the tail backward adding one; reuse known answers when encountered.','Functional edges give one deterministic continuation, so every node belongs to exactly one such decomposition.'),'O(n)','O(n)',8),
2896:entry('minimum_binary_transform_cost',[('s1','str'),('s2','str'),('x','int')],'int',['strings','dynamic programming'],['One operation flips any two positions for cost x or two adjacent positions for cost one.','Return the minimum cost to transform s1 into s2, or -1 when impossible.'],[(['1100011000','0101001010',2],'Pairing mismatch positions by cheap adjacent moves or cost-two arbitrary flips gives minimum four.'),(['10110','00011',4],'The mismatch pairing dynamic program gives the minimum valid transformation cost.')],CASES[2896][2:],OPERATIONS,[OPERATIONS.replace('if len(positions)%2:return -1','if len(positions)%2:return 0'),OPERATIONS.replace('positions[left+1]-positions[left]','positions[left+1]-positions[left]+1')],['Treats an odd mismatch count as already solved instead of impossible.','Adds one extra cost to every adjacent-pair repair.'],operations_oracle,random_operations,lesson('Only mismatch positions matter, and they must be paired.','In sorted mismatch order, an optimal plan pairs the two ends arbitrarily or adjacent positions locally.','Memoize an interval and try outer arbitrary flip, left adjacent pair, or right adjacent pair.','Uncrossing shows a cheapest pairing has one of these forms, so the interval recurrence covers an optimum.'),'O(m²)','O(m²)',5),
}

for source in (BATCH[2817]['reference'],*BATCH[2817]['wrong']):
    replacement=source.replace('    ordered=[]', '    from bisect import bisect_left, insort\n    ordered=[]')
    if source==BATCH[2817]['reference']:BATCH[2817]['reference']=replacement
    else:BATCH[2817]['wrong'][BATCH[2817]['wrong'].index(source)]=replacement
BATCH[2817]['wrong'][1]='''def constrained_minimum_difference(nums,x):
    return min(abs(nums[index]-nums[index-x]) for index in range(x,len(nums)))
'''
BATCH[2817]['wrong_reasons'][1]='Checks only pairs exactly x positions apart and misses better pairs at greater distances.'
for source in (BATCH[2896]['reference'],*BATCH[2896]['wrong']):
    replacement=source.replace('    positions=', '    from functools import lru_cache\n    positions=')
    if source==BATCH[2896]['reference']:BATCH[2896]['reference']=replacement
    else:BATCH[2896]['wrong'][BATCH[2896]['wrong'].index(source)]=replacement
BATCH[2862]['wrong'][0]='''def maximum_complete_index_sum(nums):
    groups={0:0,1:0}
    for index,value in enumerate(nums,1):groups[index%2]+=value
    return max(groups.values())
'''
BATCH[2862]['wrong_reasons'][0]='Groups positions only by parity, which does not characterize square index products.'
