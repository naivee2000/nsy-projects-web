"""Zero-array subsets, beautiful digit DP, property graphs, potion timing, and divide-by-four ranges."""
from itertools import combinations

from .import_batch_055 import entry


def zero_oracle(args):
    nums,queries=args
    for prefix in range(len(queries)+1):
        possible=True
        for index,target in enumerate(nums):
            values=[value for left,right,value in queries[:prefix] if left<=index<=right]
            if not any(sum(values[position] for position in chosen)==target for size in range(len(values)+1) for chosen in combinations(range(len(values)),size)):
                possible=False;break
        if possible:return prefix
    return -1


def random_zero(rng):
    n=rng.randint(1,6);q=rng.randint(1,8)
    queries=[]
    for _ in range(q):
        left=rng.randrange(n);queries.append([left,rng.randint(left,n-1),rng.randint(1,8)])
    return [[rng.randint(0,15) for _ in range(n)],queries]


def beautiful_number(value):
    digits=[int(char) for char in str(value)];total=sum(digits);product=1
    for digit in digits:product*=digit
    return product%total==0


def beautiful_oracle(args):
    left,right=args;return sum(beautiful_number(value) for value in range(left,right+1))


def random_beautiful(rng):
    left=rng.randint(1,500);return [left,rng.randint(left,min(700,left+150))]


def components_oracle(args):
    properties,k=args;n=len(properties);sets=list(map(set,properties));seen=set();answer=0
    for start in range(n):
        if start in seen:continue
        answer+=1;seen.add(start);stack=[start]
        while stack:
            node=stack.pop()
            for other in range(n):
                if other not in seen and len(sets[node]&sets[other])>=k:seen.add(other);stack.append(other)
    return answer


def random_components(rng):
    return [[[rng.randint(1,8) for _ in range(rng.randint(1,6))] for _ in range(rng.randint(1,9))],rng.randint(1,4)]


def potion_oracle(args):
    skill,mana=args;previous=[0]*len(skill);prefix=[0]
    for value in skill:prefix.append(prefix[-1]+value)
    for power in mana:
        start=max(previous[index]-prefix[index]*power for index in range(len(skill)))
        previous=[start+prefix[index+1]*power for index in range(len(skill))]
    return previous[-1]


def random_potion(rng):
    return [[rng.randint(1,8) for _ in range(rng.randint(1,6))],[rng.randint(1,8) for _ in range(rng.randint(1,6))]]


def steps(value):
    answer=0
    while value:value//=4;answer+=1
    return answer


def operations_oracle(args):
    answer=0
    for left,right in args[0]:
        needed=[steps(value) for value in range(left,right+1)];answer+=max((sum(needed)+1)//2,max(needed))
    return answer


def random_operations(rng):
    queries=[]
    for _ in range(rng.randint(1,6)):
        left=rng.randint(1,30);queries.append([left,rng.randint(left,min(45,left+12))])
    return [queries]


ZERO='''def minimum_zero_array_query_prefix(nums,queries):
    reachable=[1]*len(nums);masks=[(1<<(target+1))-1 for target in nums]
    if all(target==0 for target in nums):return 0
    for count,(left,right,value) in enumerate(queries,1):
        for index in range(left,right+1):reachable[index]|=(reachable[index]<<value)&masks[index]
        if all((reachable[index]>>target)&1 for index,target in enumerate(nums)):return count
    return -1
'''

BEAUTIFUL='''def count_beautiful_numbers(left,right):
    from functools import lru_cache
    def through(limit):
        if limit<=0:return 0
        digits=list(map(int,str(limit)));answer=0
        for target in range(1,9*len(digits)+1):
            @lru_cache(None)
            def count(position,total,remainder,started,tight):
                if total>target:return 0
                if position==len(digits):return int(started and total==target and remainder==0)
                result=0;maximum=digits[position] if tight else 9
                for digit in range(maximum+1):
                    next_tight=tight and digit==maximum
                    if not started and digit==0:result+=count(position+1,total,1%target,False,next_tight)
                    else:result+=count(position+1,total+digit,(remainder*digit)%target,True,next_tight)
                return result
            answer+=count(0,0,1%target,False,True)
        return answer
    return through(right)-through(left-1)
'''

COMPONENTS='''def count_property_graph_components(properties,k):
    sets=list(map(set,properties));n=len(sets);parent=list(range(n))
    def find(node):
        while parent[node]!=node:parent[node]=parent[parent[node]];node=parent[node]
        return node
    for left in range(n):
        for right in range(left):
            if len(sets[left]&sets[right])>=k:
                a,b=find(left),find(right)
                if a!=b:parent[a]=b
    return len({find(node) for node in range(n)})
'''

POTION='''def minimum_synchronized_potion_time(skill,mana):
    finish=[0]*len(skill)
    for power in mana:
        current=0
        for index,value in enumerate(skill):current=max(current,finish[index])+value*power
        finish[-1]=current
        for index in range(len(skill)-2,-1,-1):finish[index]=finish[index+1]-skill[index+1]*power
    return finish[-1]
'''

OPERATIONS='''def sum_minimum_divide_by_four_operations(queries):
    def prefix(limit):
        answer=0;start=level=1
        while start<=limit:
            answer+=(min(start*4-1,limit)-start+1)*level;start*=4;level+=1
        return answer
    total=0
    for left,right in queries:
        work=prefix(right)-prefix(left-1);largest=prefix(right)-prefix(right-1);total+=max((work+1)//2,largest)
    return total
'''


def lesson(concept,strategy,pseudocode,editorial):return [concept,strategy,pseudocode,editorial]


ZERO_CASES=[[nums,queries] for nums,queries in [([2,0,2],[[0,2,1],[0,2,1],[1,1,3]]),([0],[[0,0,1]]),([1],[[0,0,1]]),([2],[[0,0,1]]),([3],[[0,0,1],[0,0,2]]),([3],[[0,0,2],[0,0,2]]),([1,2],[[0,1,1],[1,1,1]]),([2,3],[[0,0,2],[1,1,1],[1,1,2]]),([4,4],[[0,1,2],[0,1,2]]),([5,1,5],[[0,2,1],[0,0,4],[2,2,4]]),([7,3],[[0,1,3],[0,0,4]]),([6,6],[[0,0,2],[1,1,3],[0,1,4]]),([0,5],[[1,1,2],[1,1,3]]),([8,9,10],[[0,2,2],[0,1,3],[1,2,5],[2,2,3]])]]
BEAUTIFUL_CASES=[[left,right] for left,right in [(10,20),(1,9),(1,1),(11,11),(12,12),(20,30),(95,105),(100,120),(1,100),(200,250),(999,1010),(123,321),(500,650),(1000,1100)]]
COMPONENT_CASES=[[values,k] for values,k in [([[1,2],[1,1],[3,4],[4,5],[5,6],[7,7]],1),([[1]],1),([[1],[1]],1),([[1],[2]],1),([[1,1],[1,2]],2),([[1,2],[2,3],[3,4]],1),([[1,2,3],[2,3,4],[4,5]],2),([[1,1,1],[1]],1),([[1,2],[1,2],[1,2]],2),([[1,2],[2,3],[1,3]],1),([[1,2,3],[3,4,5],[5,6,1]],1),([[7,8],[8,9],[10,11]],1),([[1,2,3,4],[2,3,4,5],[3,4,5,6]],3),([[1],[1],[2],[2]],1)]]
POTION_CASES=[[skill,mana] for skill,mana in [([1,5,2,4],[5,1,4,2]),([1],[1]),([3],[2,4]),([1,1],[1,1]),([2,3],[4]),([2,3],[4,1]),([5,1],[1,5]),([1,2,3],[3,2,1]),([4,2,1],[2,5,3]),([3,3,3],[3,3]),([1,10,1],[1,2,3]),([8,1,4,2],[2,2,5]),([2,7],[6,1,4,2]),([5,4,3,2,1],[1,3,2])]]
OPERATION_CASES=[[[pair[:] for pair in queries]] for queries in [[[1,2],[2,4]],[[1,1]],[[4,4]],[[1,4]],[[5,8]],[[15,16]],[[16,16]],[[1,10]],[[2,3],[8,9]],[[10,20]],[[1,1],[2,2],[3,3]],[[31,33]],[[4,15],[16,20]],[[7,19],[20,30],[1,5]]]]


BATCH={
3489:entry('minimum_zero_array_query_prefix',[('nums','list[int]'),('queries','list[list[int]]')],'int',['arrays','dynamic programming','subset sums'],['Each query [left,right,value] may decrement any chosen subset of covered indices by exactly value.','Process queries in order and never make an element negative.','Return the smallest prefix length that can make every nums element zero, zero if already zero, or -1 if impossible.'],[([[2,0,2],[[0,2,1],[0,2,1],[1,1,3]]],'Selecting both outer indices in the first two queries reaches zero after two queries.'),([[3],[[0,0,2],[0,0,2]]],'No subset of the available decrements sums to three, so return -1.')],ZERO_CASES,ZERO,[ZERO.replace('range(left,right+1)','range(len(nums))'),ZERO.replace('reachable[index]|=(reachable[index]<<value)&masks[index]','reachable[index]=reachable[index]<<value')],['Applies each query to every index instead of only its covered range.','Requires using every covering query and discards earlier subset sums.'],zero_oracle,random_zero,lesson('Each index has an independent 0/1 subset-sum problem over values from queries that cover it.','Maintain one bitset of reachable decrement totals per index and update covered bitsets once per query.','Shift by the query value, OR with prior sums, cap at nums[i], and after each query test every target bit.','Subset choices are independent across indices, so all targets being reachable is necessary and sufficient for that prefix.'),'O(sum(query lengths)*max(nums)/word_size)','O(n*max(nums)/word_size)',6),
3490:entry('count_beautiful_numbers',[('l','int'),('r','int')],'int',['digit dynamic programming','math'],['1 <= l <= r.','A positive integer is beautiful when its digit product is divisible by its digit sum.','Count beautiful integers in the inclusive range.'],[([10,20],'Only two integers in this range satisfy product divisible by sum.'),([1,9],'Every one-digit positive number has equal digit product and sum, so all nine qualify.')],BEAUTIFUL_CASES,BEAUTIFUL,[BEAUTIFUL.replace('(remainder*digit)%target','(remainder+digit)%target'),BEAUTIFUL.replace('remainder==0','remainder==1%target')],['Tracks digit sum modulo the target instead of digit product modulo the target.','Accepts product remainder one instead of divisibility remainder zero.'],beautiful_oracle,random_beautiful,lesson('The digit sum is at most nine times the digit count, so enumerate its final target value.','For each target sum, run a bounded digit DP tracking current sum, product remainder, whether a number started, and tightness.','Append each possible digit, multiplying the remainder after the first nonzero digit; accept exact target sum with remainder zero.','Every positive number belongs to exactly one target-sum DP, so summing targets counts each beautiful number once.'),'O(d*max_sum^3)','O(d*max_sum^2)',8),
3493:entry('count_property_graph_components',[('properties','list[list[int]]'),('k','int')],'int',['graphs','union find','sets'],['properties is a nonempty list of integer lists and k is positive.','Two nodes are adjacent when their property lists share at least k distinct values.','Return the number of connected components in the resulting undirected graph.'],[([[[1,2],[1,1],[3,4],[4,5],[5,6],[7,7]],1],'The shared-value edges form three connected components.'),([[[1,1],[1,2]],2],'Duplicates do not count twice, so the two nodes share only one distinct value and remain separate.')],COMPONENT_CASES,COMPONENTS,[COMPONENTS.replace('sets=list(map(set,properties))',"sets=[__import__('collections').Counter(row) for row in properties]").replace('len(sets[left]&sets[right])','sum(sets[left][value]*sets[right][value] for value in sets[left].keys() & sets[right].keys())'),COMPONENTS.replace('>=k','>k')],['Counts duplicate pairings rather than distinct shared values.','Requires more than k shared values instead of at least k.'],components_oracle,random_components,lesson('Only distinct property values matter, and connected components can be merged as qualifying pairs are found.','Convert every row to a set, compare all node pairs, and union roots when intersection size reaches k.','Use path compression in find; after all pair checks, count distinct roots.','Union operations create exactly the transitive closure of qualifying graph edges, so remaining roots equal graph components.'),'O(n^2*m)','O(n*m)',6),
3494:entry('minimum_synchronized_potion_time',[('skill','list[int]'),('mana','list[int]')],'int',['arrays','simulation','prefix timing'],['skill and mana are nonempty positive-integer arrays.','Every potion visits all wizards in order; wizard i takes skill[i]*mana[j] time.','A potion must pass immediately between wizards, and no wizard may process two potions simultaneously; minimize the final completion time.'],[([[1,5,2,4],[5,1,4,2]],'The earliest synchronized no-wait schedule finishes after 110 time units.'),([[1],[1]],'One wizard brewing one potion needs one time unit.')],POTION_CASES,POTION,[POTION.replace('current=max(current,finish[index])','current=current'),POTION.replace('finish[index]=finish[index+1]-skill[index+1]*power','finish[index]=finish[index+1]')],['Ignores conflicts with the preceding potion and overlaps work on the same wizard.','Back-propagates equal finish times instead of subtracting each downstream processing duration.'],potion_oracle,random_potion,lesson('Once a potion starts, its no-wait finish times are fixed offsets; its start must satisfy every wizard’s previous finish.','Simulate the earliest feasible schedule and back-propagate each new potion’s synchronized timeline.','Sweep wizards using max(current arrival, prior finish), set the last finish, then subtract processing times backward to recover earlier finishes.','The forward maximum finds the smallest start respecting all resource conflicts, and delaying it could only delay the final answer.'),'O(len(skill)*len(mana))','O(len(skill))',6),
3495:entry('sum_minimum_divide_by_four_operations',[('queries','list[list[int]]')],'int',['math','range counting','greedy'],['Each query represents the array of every integer from left through right, inclusive.','One operation chooses two current elements and replaces each by floor(value/4).','Return the sum, over all queries, of the minimum operations needed to make every element zero.'],[([[[1,2],[2,4]]],'The two query arrays require one and two operations, totaling three.'),([[[16,16]]],'The sole value needs three divisions and can be selected only once per operation, so the answer is three.')],OPERATION_CASES,OPERATIONS,[OPERATIONS.replace('max((work+1)//2,largest)','(work+1)//2'),OPERATIONS.replace('start*=4','start*=2')],['Uses only half the total work and ignores the lower bound from the slowest single element.','Groups values by powers of two instead of powers of four and assigns incorrect division counts.'],operations_oracle,random_operations,lesson('Each value contributes its number of repeated divide-by-four steps; an operation performs at most two steps on distinct elements.','Count total steps over a range by power-of-four bands and also obtain the largest individual step count.','Use a cumulative band function for [1,x]; for [l,r], take max(ceil(total/2),steps(r)) and sum queries.','Pairing available steps achieves the total-work bound until only the longest element remains, making the maximum of the two bounds exact.'),'O(q log_4 r)','O(1)',8),
}
