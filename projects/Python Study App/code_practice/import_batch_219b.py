"""Incremental roads, equal child subtrees, consecutive windows, drink DP, and hashes."""
from collections import deque
from functools import lru_cache
from .import_batch_055 import entry

def roads_oracle(args):
    n,queries=args;graph=[[] for _ in range(n)];answer=[]
    for i in range(n-1):graph[i].append(i+1)
    for u,v in queries:
        graph[u].append(v);distance=[-1]*n;distance[0]=0;queue=deque([0])
        while queue:
            node=queue.popleft()
            for nxt in graph[node]:
                if distance[nxt]<0:distance[nxt]=distance[node]+1;queue.append(nxt)
        answer.append(distance[-1])
    return answer
def random_roads(rng):
    n=rng.randint(3,14);choices=[(u,v) for u in range(n) for v in range(u+2,n)];rng.shuffle(choices)
    return [n,[list(x) for x in choices[:rng.randint(1,min(18,len(choices)))] ]]

def good_oracle(args):
    edges=args[0];n=len(edges)+1;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    answer=0
    def visit(node,parent):
        nonlocal answer
        sizes=[visit(child,node) for child in graph[node] if child!=parent]
        answer+=len(set(sizes))<=1
        return 1+sum(sizes)
    visit(0,-1);return answer
def random_tree(rng):
    n=rng.randint(2,20);edges=[[node,rng.randrange(node)] for node in range(1,n)];rng.shuffle(edges);return [edges]

def power_oracle(args):
    nums,k=args;answer=[]
    for left in range(len(nums)-k+1):
        window=nums[left:left+k];answer.append(window[-1] if all(b==a+1 for a,b in zip(window,window[1:])) else -1)
    return answer
def random_power(rng):
    nums=[rng.randint(1,20) for _ in range(rng.randint(1,25))];return [nums,rng.randint(1,len(nums))]

def energy_oracle(args):
    a,b=args;n=len(a)
    @lru_cache(None)
    def visit(hour,last):
        if hour==n:return 0
        best=visit(hour+1,2)
        if last in (0,2):best=max(best,a[hour]+visit(hour+1,0))
        if last in (1,2):best=max(best,b[hour]+visit(hour+1,1))
        return best
    return visit(0,2)
def random_energy(rng):
    n=rng.randint(3,12);return [[rng.randint(1,30) for _ in range(n)],[rng.randint(1,30) for _ in range(n)]]

def hash_oracle(args):
    s,k=args;alphabet='abcdefghijklmnopqrstuvwxyz'
    return ''.join(alphabet[sum(alphabet.index(char) for char in s[i:i+k])%26] for i in range(0,len(s),k))
def random_hash(rng):
    k=rng.randint(1,8);groups=rng.randint(1,8);return [''.join(chr(97+rng.randrange(26)) for _ in range(k*groups)),k]

ROADS='''def shortest_paths_after_roads(n,queries):
    graph=[[] for _ in range(n)]
    for city in range(n-1):graph[city].append(city+1)
    answer=[]
    for start,end in queries:
        graph[start].append(end);distance=list(range(n))
        for city in range(n):
            for destination in graph[city]:distance[destination]=min(distance[destination],distance[city]+1)
        answer.append(distance[-1])
    return answer
'''
GOOD='''def count_equal_child_subtree_nodes(edges):
    n=len(edges)+1;graph=[[] for _ in range(n)]
    for a,b in edges:graph[a].append(b);graph[b].append(a)
    parent=[-1]*n;order=[0]
    for node in order:
        for child in graph[node]:
            if child!=parent[node]:parent[child]=node;order.append(child)
    size=[1]*n;answer=0
    for node in reversed(order):
        children=[child for child in graph[node] if parent[child]==node]
        answer+=len({size[child] for child in children})<=1
        if parent[node]>=0:size[parent[node]]+=size[node]
    return answer
'''
POWER='''def k_window_consecutive_power(nums,k):
    run=1;answer=[]
    for index,number in enumerate(nums):
        if index and number==nums[index-1]+1:run+=1
        else:run=1
        if index>=k-1:answer.append(number if run>=k else -1)
    return answer
'''
ENERGY='''def maximum_two_drink_energy(energy_drink_a,energy_drink_b):
    n=len(energy_drink_a);drink_a=[0]*n;drink_b=[0]*n
    for hour in range(n):
        drink_a[hour]=energy_drink_a[hour]+max(drink_a[hour-1] if hour else 0,drink_b[hour-2] if hour>=2 else 0)
        drink_b[hour]=energy_drink_b[hour]+max(drink_b[hour-1] if hour else 0,drink_a[hour-2] if hour>=2 else 0)
    return max(drink_a[-1],drink_b[-1])
'''
HASH='''def hash_string_chunks(s,k):
    result=[]
    for start in range(0,len(s),k):
        total=0
        for char in s[start:start+k]:total+=ord(char)-ord('a')
        result.append(chr(ord('a')+total%26))
    return ''.join(result)
'''
def lesson(a,b,c,d):return [a,b,c,d]

BATCH={
3243:entry('shortest_paths_after_roads',[('n','int'),('queries','list[list[int]]')],'list[int]',['graphs','dynamic programming','shortest paths'],['3≤n≤500; initially every city i has a directed road to i+1.','Each distinct query [u,v] has u+1<v and permanently adds a forward road.','After each addition return the shortest edge count from 0 to n-1.'],[([5,[[2,4],[0,2],[0,4]]],'The new best routes have lengths three, two, then one.'),([4,[[0,3],[0,2]]],'The direct road fixes the distance at one, so the second road cannot improve it.')],[[n,q] for n,q in [(3,[[0,2]]),(4,[[0,2]]),(4,[[1,3]]),(5,[[1,4]]),(5,[[0,3],[1,4]]),(6,[[0,2],[2,5]]),(6,[[1,4],[0,3]]),(7,[[0,6]]),(7,[[2,5],[1,4]]),(8,[[0,2],[2,4],[4,7]]),(8,[[3,7],[0,4]]),(9,[[1,8],[0,2]]),(10,[[0,5],[5,9],[1,8]]),(6,[[0,4],[1,5],[0,3]])]],ROADS,[ROADS.replace('graph[start].append(end)','graph[end].append(start)'),ROADS.replace('distance[destination],distance[city]+1','distance[destination],distance[city]')],['Adds each queried road backward.','Treats new roads as having zero cost.'],roads_oracle,random_roads,lesson('All roads point forward, so city order is already a topological order.','After each addition, recompute shortest distances by relaxing outgoing roads from left to right.','Start with chain distances 0..n-1; relax every stored edge once and record the last distance.','Topological relaxation considers every possible last edge after its source distance is final, proving the shortest result.'),'O(q(n+q))','O(n+q)',5),
3249:entry('count_equal_child_subtree_nodes',[('edges','list[list[int]]')],'int',['trees','depth first search'],['edges describes an undirected tree rooted at node 0 with 2≤n≤100,000.','A node is good when all subtrees rooted at its direct children have equal size.','Leaves and nodes with one child are good; return the total good-node count.'],[([[[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]]],'Every internal node has equal child-subtree sizes and all leaves are good, totaling seven.'),([[[0,1],[1,2],[2,3],[3,4],[0,5],[1,6],[2,7],[3,8]]],'Six nodes meet the equal-child-size condition.')],[[e] for e in [[[0,1]],[[0,1],[0,2]],[[0,1],[1,2]],[[0,1],[0,2],[0,3]],[[0,1],[1,2],[1,3]],[[0,1],[1,2],[2,3]],[[0,1],[0,2],[1,3]],[[0,1],[0,2],[1,3],[2,4]],[[0,1],[0,2],[0,3],[1,4]],[[0,1],[1,2],[1,3],[3,4]],[[0,1],[0,2],[1,3],[1,4],[2,5]],[[0,1],[1,2],[2,3],[0,4]],[[0,1],[0,2],[2,3],[2,4],[4,5]],[[0,1],[1,2],[1,3],[0,4],[4,5],[5,6]]]],GOOD,[GOOD.replace('len({size[child] for child in children})<=1','len(children)<=1'),GOOD.replace('size[parent[node]]+=size[node]','size[parent[node]]+=1')],['Counts only leaves and single-child nodes as good.','Adds only child counts rather than full subtree sizes.'],good_oracle,random_tree,lesson('Whether a node is good depends on child subtree sizes, which are known after its descendants.','Root the tree iteratively, then process the discovery order backward.','Store parent and subtree size; compare the set of direct-child sizes and accumulate each size into its parent.','Reverse order is postorder, so every compared child size is complete; the set condition exactly states equality.'),'O(n)','O(n)',5),
3254:entry('k_window_consecutive_power',[('nums','list[int]'),('k','int')],'list[int]',['arrays','sliding windows'],['nums is a nonempty positive-integer array and 1≤k≤len(nums).','A size-k window has power equal to its maximum only when values rise by exactly one at every step; otherwise power is -1.','Return the power for every size-k window in left-to-right order.'],[([[1,2,3,4,3,2,5],3],'The first two windows are consecutive and end at 3 and 4; the remaining three fail.'),([[2,2,2,2,2],4],'Neither length-four window rises by one, so both powers are -1.')],[[a,k] for a,k in [([1],1),([5,6],1),([5,6],2),([2,2],2),([3,2,3,2,3,2],2),([1,2,3],3),([1,3,4],2),([4,5,6,7],3),([4,5,3,4],2),([9,10,11,8],3),([1,2,4,5,6],3),([7,8,9,10,11],4),([3,4,5,2,3,4],3),([10,9,8,7],2)]],POWER,[POWER.replace('number==nums[index-1]+1','number>=nums[index-1]+1'),POWER.replace('run>=k','run>k')],['Accepts gaps larger than one as consecutive.','Rejects a run whose length is exactly k.'],power_oracle,random_power,lesson('A valid window is exactly a suffix of a run whose adjacent values rise by one.','Track the current consecutive-run length while scanning once.','Reset the run on any broken step; for each completed window output its last value iff run≥k.','The run length is the longest valid suffix, so it covers the current size-k window exactly when it reaches k.'),'O(n)','O(1)',5),
3259:entry('maximum_two_drink_energy',[('energy_drink_a','list[int]'),('energy_drink_b','list[int]')],'int',['dynamic programming','arrays'],['energy_drink_a and energy_drink_b have equal length n≥3 and contain positive boosts.','You may drink A or B in an hour; switching types requires one intervening hour with no drink.','You may begin with either type; return the maximum total boost.'],[([[1,3,1],[3,1,1]],'Staying with either drink for all three hours yields five.'),([[4,1,1],[1,1,3]],'Drink A for four, cleanse for one hour, then drink B for three, totaling seven.')],[[a,b] for a,b in [([1,1,1],[1,1,1]),([9,1,1],[1,1,9]),([1,9,1],[9,1,9]),([5,4,3],[1,9,1]),([1,2,3,4],[4,3,2,1]),([10,1,1,10],[1,10,10,1]),([2,2,8,2],[7,1,1,7]),([6,1,6,1,6],[1,6,1,6,1]),([3,8,2,9],[7,1,10,1]),([1,1,20,1,1],[8,8,1,8,8]),([4,7,2],[6,1,8]),([9,2,2,2],[1,8,8,8]),([2,10,2,10],[9,1,9,1]),([5,1,5,1,5],[1,9,1,9,1])]],ENERGY,[ENERGY.replace('hour-2','hour-1'),ENERGY.replace('max(drink_a[-1],drink_b[-1])','drink_a[-1]')],['Switches immediately without paying the cleanse hour.','Forces the schedule to finish with drink A.'],energy_oracle,random_energy,lesson('A schedule ending with A either also used A last hour or last used B at least two hours ago.','Keep best totals ending with each drink at every hour.','For A at hour i add its boost to max(A at i-1, B at i-2); use the symmetric recurrence for B.','Those two predecessor cases exhaust legal endings and preserve the best prefix, giving optimal substructure.'),'O(n)','O(n)',6),
3271:entry('hash_string_chunks',[('s','str'),('k','int')],'str',['strings','simulation'],['s contains lowercase English letters, 1≤k≤100, and len(s) is divisible by k.','For each consecutive size-k chunk, sum alphabet indices a=0 through z=25.','Reduce each sum modulo 26, convert it back to a letter, and concatenate the letters.'],[(['abcd',2],'ab hashes to 1→b and cd hashes to 5→f, producing bf.'),(['mxz',3],'The only chunk sums to 60; 60 modulo 26 is 8, which maps to i.')],[[s,k] for s,k in [('a',1),('z',1),('az',2),('zz',2),('abc',1),('aaa',3),('xyz',3),('abcdef',3),('leetcode',4),('abababab',2),('mnopqrst',4),('zzzzzz',3),('helloworld',5),('abcdefghijkl',6)]],HASH,[HASH.replace("ord(char)-ord('a')","ord(char)-ord('a')+1"),HASH.replace('total%26','total')],['Uses one-based rather than zero-based character hashes.','Fails to reduce each chunk sum modulo 26.'],hash_oracle,random_hash,lesson('Each output character depends on one fixed-size chunk only.','Scan chunks in order and accumulate zero-based alphabet values.','Take the sum modulo 26 and convert the resulting index back to a lowercase letter.','The chunks partition s, so processing each once produces exactly one output character in the required order.'),'O(n)','O(k)',3),
}
