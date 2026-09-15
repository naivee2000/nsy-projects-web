"""Modular subsequences, merged-tree diameters, hopping, enemies, and circular alternation."""
from itertools import combinations

from .import_batch_055 import entry


def modular_oracle(args):
    nums,k=args;best=1
    for size in range(2,len(nums)+1):
        for chosen in combinations(range(len(nums)),size):
            if len({(nums[chosen[i-1]]+nums[chosen[i]])%k for i in range(1,size)})==1:best=size
    return best


def random_modular(rng):return [[rng.randint(0,30) for _ in range(rng.randint(1,11))],rng.randint(1,7)]


def graph_diameter(edges):
    size=len(edges)+1;graph=[[] for _ in range(size)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    return max(sum(1 for _ in []) if False else _dist(graph,start) for start in range(size))


def _dist(graph,start):
    distances=[-1]*len(graph);distances[start]=0;queue=[start]
    for node in queue:
        for neighbor in graph[node]:
            if distances[neighbor]<0:distances[neighbor]=distances[node]+1;queue.append(neighbor)
    return max(distances)


def diameter_oracle(args):
    first,second=args;d1=graph_diameter(first);d2=graph_diameter(second)
    return max(d1,d2,(d1+1)//2+(d2+1)//2+1)


def random_tree_edges(rng):
    def tree(size):return [[node,rng.randrange(node)] for node in range(1,size)]
    return [tree(rng.randint(1,10)),tree(rng.randint(1,10))]


def hopping_oracle(args):
    nums=args[0];dp=[-10**30]*len(nums);dp[0]=0
    for right in range(1,len(nums)):
        dp[right]=max(dp[left]+(right-left)*nums[right] for left in range(right))
    return dp[-1]


def random_hopping(rng):return [[rng.randint(1,30) for _ in range(rng.randint(2,15))]]


def enemies_oracle(args):
    energies,current=args;minimum=min(energies)
    return 0 if current<minimum else (current+sum(energies)-minimum)//minimum


def random_enemies(rng):return [[rng.randint(1,30) for _ in range(rng.randint(1,12))],rng.randint(0,50)]


def alternating_oracle(args):
    colors,k=args;n=len(colors);return sum(all(colors[(start+i)%n]!=colors[(start+i-1)%n] for i in range(1,k)) for start in range(n))


def random_alternating(rng):
    size=rng.randint(2,15);return [[rng.randint(0,1) for _ in range(size)],rng.randint(2,size)]


MODULAR='''def longest_constant_modular_pair_subsequence(nums,k):
    dp=[[0]*k for _ in range(k)]
    for number in nums:
        remainder=number%k
        for target in range(k):
            needed=(target-remainder)%k
            dp[remainder][target]=max(dp[remainder][target],dp[needed][target]+1)
    return max(max(row) for row in dp)
'''


DIAMETER='''def minimum_merged_tree_diameter(edges1,edges2):
    def diameter(edges):
        graph=[[] for _ in range(len(edges)+1)]
        for first,second in edges:graph[first].append(second);graph[second].append(first)
        def farthest(start):
            distance=[-1]*len(graph);distance[start]=0;queue=[start]
            for node in queue:
                for neighbor in graph[node]:
                    if distance[neighbor]<0:distance[neighbor]=distance[node]+1;queue.append(neighbor)
            endpoint=max(range(len(graph)),key=distance.__getitem__);return endpoint,distance[endpoint]
        endpoint,_=farthest(0);return farthest(endpoint)[1]
    first=diameter(edges1);second=diameter(edges2)
    return max(first,second,(first+1)//2+(second+1)//2+1)
'''


HOPPING='''def maximum_array_hopping_score(nums):
    best=0;answer=0
    for index in range(len(nums)-1,0,-1):best=max(best,nums[index]);answer+=best
    return answer
'''


ENEMIES='''def maximum_enemy_battle_points(enemyEnergies,currentEnergy):
    minimum=min(enemyEnergies)
    return 0 if currentEnergy<minimum else (currentEnergy+sum(enemyEnergies)-minimum)//minimum
'''


ALTERNATING='''def circular_alternating_groups(colors,k):
    n=len(colors);run=1;answer=0
    for index in range(1,n+k-1):
        if colors[index%n]!=colors[(index-1)%n]:run+=1
        else:run=1
        if index>=k-1 and run>=k:answer+=1
    return answer
'''


def lesson(a,b,c,d):return [a,b,c,d]


BATCH={
3202:entry('longest_constant_modular_pair_subsequence',[('nums','list[int]'),('k','int')],'int',['dynamic programming','modular arithmetic'],['nums is nonempty and k is positive.','Choose a subsequence in input order such that every adjacent chosen pair has the same sum remainder modulo k.','Return the maximum possible subsequence length.'],[([[1,2,3,4,5],2],'Every adjacent sum in the full sequence is odd, so all five values are valid.'),([[1,4,2,3,1,4],3],'Dynamic programming selects the longest chain having one fixed adjacent-sum remainder.')],[[n,k] for n,k in [([1],1),([1,2,3,4,5],2),([1,4,2,3,1,4],3),([1,1,1],5),([1,2,3],1),([0,1,2,3],4),([2,4,6],3),([5,1,5,1],2),([1,3,2,4],5),([7,8,9,10],3),([0,0,1,1],2),([6,2,5,4,3],4),([10,20,30],7),([1,2,1,3,2,4],3)]],MODULAR,[MODULAR.replace('(target-remainder)%k','(target+remainder)%k'),MODULAR.replace('dp[needed][target]+1','dp[remainder][target]+1')],['Solves the wrong modular equation for the required preceding remainder.','Extends only subsequences already ending in the current remainder and misses mixed remainders.'],modular_oracle,random_modular,lesson('Fix the common pair-sum remainder t; if the new value has remainder r, its predecessor must have remainder t-r.','Maintain the best length by ending remainder and chosen target remainder.','For each r and t, dp[r][t]=max(dp[r][t],dp[(t-r)%k][t]+1).','The recurrence appends the current index to every and only compatible prior state; taking all targets covers every valid subsequence.'),'O(nk)','O(k²)',5),
3203:entry('minimum_merged_tree_diameter',[('edges1','list[list[int]]'),('edges2','list[list[int]]')],'int',['trees','graphs','breadth-first search'],['Each edge list describes a possibly single-node undirected tree numbered consecutively from zero.','Add exactly one edge joining any node of the first tree to any node of the second.','Return the minimum possible diameter of the combined tree, measured in edges.'],[([[[0,1],[0,2],[0,3]],[[0,1]]],'Connecting centers produces diameter three; no connection can make either original diameter smaller.'),([[],[]],'Joining the two single nodes creates one edge, so the diameter is one.')],[[a,b] for a,b in [([[0,1],[0,2],[0,3]],[[0,1]]),([],[]),([[0,1]],[]),([[0,1]],[[0,1]]),([[0,1],[1,2]],[[0,1],[1,2]]),([[0,1],[1,2],[2,3]],[[0,1]]),([[0,1],[0,2]],[[0,1],[0,2]]),([[0,1],[1,2],[1,3]],[[0,1],[1,2]]),([[0,1],[1,2],[2,3],[3,4]],[]),([[0,1],[0,2],[0,3],[0,4]],[[0,1],[1,2],[2,3]]),([[0,1],[1,2],[2,3]],[[0,1],[0,2],[0,3]]),([[0,1],[1,2],[1,3],[3,4]],[[0,1]]),([[0,1],[0,2],[2,3],[2,4]],[[0,1],[1,2]]),([[0,1],[1,2],[2,3],[3,4]],[[0,1],[1,2],[2,3],[3,4]])]],DIAMETER,[DIAMETER.replace('(first+1)//2+(second+1)//2+1','first//2+second//2+1'),DIAMETER.replace('return max(first,second,(first+1)//2+(second+1)//2+1)','return (first+1)//2+(second+1)//2+1')],['Uses floor radii and underestimates trees with odd diameters.','Returns only the cross-tree path and ignores an unchanged larger original diameter.'],diameter_oracle,random_tree_edges,lesson('Connecting a center of each tree minimizes the longest path that crosses the new edge.','Find each diameter with two BFS sweeps; its minimum eccentricity is ceil(diameter/2).','Return max(d1,d2,ceil(d1/2)+ceil(d2/2)+1).','Original diameters remain lower bounds, and every cross path through connected centers is bounded by the sum of the two radii plus one.'),'O(nodes+edges)','O(nodes)',8),
3205:entry('maximum_array_hopping_score',[('nums','list[int]')],'int',['greedy','dynamic programming'],['nums contains at least two positive integers.','Start at index zero and make strictly rightward hops until reaching the final index.','A hop i to j scores (j-i)*nums[j]; maximize the total score.'],[([[1,5,8]],'Jumping directly from zero to two scores 2*8=16.'),([[4,10,2,8]],'Each unit gap should be assigned to the greatest reachable destination value, giving 10+8+8=26.')],[[n] for n in [[1,5,8],[4,10,2,8],[1,1],[5,2],[1,2,3],[3,2,1],[2,9,1],[8,1,8],[1,10,1,10],[5,4,20,1],[2,3,2,3,2],[10,1,1,1,9],[7,6,5,100],[1,4,2,8,3]]],HOPPING,[HOPPING.replace('best=max(best,nums[index])','best=nums[index]'),HOPPING.replace("range(len(nums)-1,0,-1)","range(len(nums)-2,0,-1)")],['Uses each immediate destination rather than the best destination reachable across that gap.','Omits the final unit gap and therefore never credits the mandatory arrival at the last index.'],hopping_oracle,random_hopping,lesson('Expand every hop score into one copy of its destination value for each crossed unit gap.','For each gap, choose the greatest array value to its right; suffix maxima make these choices compatible as hop endpoints.','Scan destinations right to left, add the running maximum for every gap.','Suffix-maximum changes identify an increasing sequence of hop destinations that realizes all independently optimal gap contributions.'),'O(n)','O(1)',5),
3207:entry('maximum_enemy_battle_points',[('enemyEnergies','list[int]'),('currentEnergy','int')],'int',['greedy','math'],['enemyEnergies is nonempty and positive; currentEnergy is nonnegative.','An affordable unmarked enemy can be fought repeatedly for one point while spending its energy; alternatively, with a point, mark an enemy to gain its energy.','Return the maximum attainable points.'],[([[3,2,2],2],'Keep one minimum-energy enemy available, mark the others for energy, and fight the minimum repeatedly for three points.'),([[5,6],4],'No enemy is initially affordable, so no first point can be earned and the answer is zero.')],[[e,c] for e,c in [([3,2,2],2),([5,6],4),([1],0),([1],1),([5],20),([2,3],2),([10,1,10],1),([4,4,4],4),([2,100],3),([7,3,5],10),([1,2,3],1),([9,2,8,4],2),([6,6],5),([3,10,20],15)]],ENEMIES,[ENEMIES.replace('-minimum',''),ENEMIES.replace('currentEnergy<minimum','currentEnergy<=minimum')],['Adds the kept minimum enemy’s energy as if it could be marked while still remaining available to fight.','Incorrectly rejects the valid case where initial energy exactly equals the cheapest enemy.'],enemies_oracle,random_enemies,lesson('If the cheapest enemy is initially affordable, keep it unmarked as a repeatable point source and convert every other enemy into energy.','The total spendable energy is initial plus all enemy energy except one minimum copy; divide by the minimum cost.','If initial<minimum return zero; otherwise floor((initial+sum-minimum)/minimum).','No point can be earned below the minimum; once affordable, every other energy can be harvested while one cheapest target remains, reaching the upper bound.'),'O(n)','O(1)',5),
3208:entry('circular_alternating_groups',[('colors','list[int]'),('k','int')],'int',['sliding windows','circular arrays'],['colors is a circular binary array and 2≤k≤len(colors).','A length-k group begins at any tile and follows clockwise with wraparound.','Count starts for which every adjacent pair within the group has different colors.'],[([[0,1,0,1,0],3],'Starts zero, one, and two produce alternating triples; the two groups crossing the equal circular boundary do not.'),([[0,1,0,1],4],'The full four-tile circle alternates along the three edges inside each linearized group, so all four starts count.')],[[c,k] for c,k in [([0,1,0,1,0],3),([0,1,0,1],4),([0,0],2),([0,1],2),([1,1,1],2),([0,1,0],2),([0,1,1,0],3),([1,0,1,0,1,0],5),([0,0,1,0,1],3),([1,0,0,1,0],4),([0,1,0,0,1,0],3),([1,1,0,1,1],2),([0,1,0,1,0,1,0],6),([1,0,1,1,0,1],4)]],ALTERNATING,[ALTERNATING.replace('n+k-1','n'),ALTERNATING.replace('run>=k','run==k')],['Stops before examining wraparound starts.','Counts a window only when the run length equals k and misses later windows within a longer alternating run.'],alternating_oracle,random_alternating,lesson('Linearize enough circular positions to include every n possible length-k start.','Track the current alternating run length across n+k-1 visited positions.','Increment answer whenever index≥k-1 and run≥k.','A length-k window alternates exactly when the alternating suffix ending there has length at least k; the scanned endpoints correspond one-to-one with circular starts.'),'O(n+k)','O(1)',5),
}
